#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Script References Updater

This script updates all Python scripts in the EGOS ecosystem to ensure they properly
reference the Script Management Best Practices document. It identifies scripts without
the reference and adds it to their docstrings following EGOS standards.

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md
- C:\EGOS\scripts\maintenance\code_health\script_validator.py
- C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
- C:\EGOS\scripts\cross_reference\inject_standardized_references.py

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import sys
import re
import ast
import json
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "update_script_references.log")
    ]
)
logger = logging.getLogger("update_script_references")

# Define constants
SCRIPT_MGMT_REFERENCE = "C:\\EGOS\\docs_egos\\03_processes\\script_management\\script_management_best_practices.md"
REFERENCE_PATTERN = re.compile(r'script_management_best_practices\.md', re.IGNORECASE)


class ScriptReferenceUpdater:
    """Updates Python scripts to ensure they reference the Script Management Best Practices document."""
    
    def __init__(self, root_path: Path, reference_path: Path = None, exclude_dirs: List[str] = None, 
                 dry_run: bool = False, retry_errors: bool = False):
        """Initialize the reference updater.
        
        Args:
            root_path: Base directory to search for Python files
            reference_path: Path to the Script Management Best Practices document
            exclude_dirs: Directories to exclude from scanning
            dry_run: If True, only show what would be changed without making changes
            retry_errors: If True, retry scripts that previously had errors
        """
        self.root_path = root_path
        self.exclude_dirs = exclude_dirs or ["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"]
        self.dry_run = dry_run
        self.retry_errors = retry_errors
        
        # Set reference path
        if reference_path and reference_path.exists():
            self.reference_path = str(reference_path).replace('\\', '\\\\')
        else:
            default_path = "C:\\EGOS\\docs_egos\\03_processes\\script_management\\script_management_best_practices.md"
            self.reference_path = default_path
            logger.warning(f"Using default reference path: {default_path}")
            
        # Error tracking file
        self.error_log_path = Path(self.root_path.parent) / "docs" / "reports" / "script_reference_errors.json"
        self.previous_errors = self._load_previous_errors()
        
        # Statistics
        self.stats = {
            "total": 0,
            "with_reference": 0,
            "missing_reference": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "error_details": []
        }
        
        logger.info(f"Script Reference Updater initialized with root: {root_path}, dry_run: {dry_run}, retry_errors: {retry_errors}")
    
    def find_python_files(self) -> List[Path]:
        """
        Find all Python files in the specified directory.
        
        Returns:
            List of paths to Python files
        """
        python_files = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        logger.info(f"Found {len(python_files)} Python files to check")
        self.stats["total"] = len(python_files)
        return python_files
    
    def _load_previous_errors(self) -> Dict[str, str]:
        """Load previous error information from error log file.
        
        Returns:
            Dictionary mapping script paths to error messages
        """
        if not self.error_log_path.exists():
            return {}
        
        try:
            with open(self.error_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading previous error log: {str(e)}")
            return {}
    
    def _save_error_log(self):
        """Save error information to error log file."""
        try:
            # Create error log directory if it doesn't exist
            self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert error details to dictionary
            error_dict = {}
            for error in self.stats["error_details"]:
                error_dict[error["path"]] = error["error"]
            
            with open(self.error_log_path, 'w', encoding='utf-8') as f:
                json.dump(error_dict, f, indent=2)
                
            logger.info(f"Error log saved to {self.error_log_path}")
        except Exception as e:
            logger.warning(f"Error saving error log: {str(e)}")
    
    def update_script(self, script_path: Path) -> bool:
        """Update a script to include a reference to the best practices document.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            True if the script was updated, False otherwise
        """
        # Skip if script had a previous error and retry_errors is False
        script_path_str = str(script_path)
        if not self.retry_errors and script_path_str in self.previous_errors:
            logger.info(f"Skipping script with previous error: {script_path}")
            self.stats["skipped"] += 1
            return False
        
        try:
            # Check if file is too large (> 1MB)
            if script_path.stat().st_size > 1024 * 1024:
                logger.warning(f"Script is too large (> 1MB), skipping: {script_path}")
                self.stats["skipped"] += 1
                return False
                
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if the script already has a reference
            if self._has_reference(content):
                logger.info(f"Script already has reference: {script_path}")
                self.stats["with_reference"] += 1
                return False
            
            # Update the script with a reference
            updated_content = self._add_reference(content)
            
            if self.dry_run:
                logger.info(f"Would update {script_path}")
                self.stats["missing_reference"] += 1
                return True
            
            # Create backup of original file
            backup_path = script_path.with_suffix('.py.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated content
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"Updated {script_path}")
            self.stats["updated"] += 1
            self.stats["missing_reference"] += 1
            return True
        
        except UnicodeDecodeError:
            # Handle binary or non-UTF-8 files gracefully
            logger.warning(f"File is not a valid UTF-8 text file, skipping: {script_path}")
            self.stats["skipped"] += 1
            return False
        except Exception as e:
            logger.error(f"Error updating {script_path}: {str(e)}")
            self.stats["errors"] += 1
            self.stats["error_details"].append({
                "path": script_path_str,
                "error": str(e)
            })
            return False
    
    def _has_reference(self, content: str) -> bool:
        """Check if the script already has a reference to the best practices document.
        
        Args:
            content: Script content
        
        Returns:
            True if the script has a reference, False otherwise
        """
        return REFERENCE_PATTERN.search(content) is not None
    
    def _add_reference(self, content: str) -> str:
        """Add a reference to the best practices document to the script content.
        
        Args:
            content: Script content
        
        Returns:
            Updated script content with reference
        """
        # Parse the AST to find docstring
        try:
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            
            if docstring:
                # Check if docstring has a references section
                if "@references:" in docstring:
                    # Add reference to existing section
                    ref_section_pattern = re.compile(r'(@references:.*?)(\n\n|\Z)', re.DOTALL)
                    match = ref_section_pattern.search(docstring)
                    
                    if match:
                        ref_section = match.group(1)
                        
                        # Check if the reference is already in the section
                        if REFERENCE_PATTERN.search(ref_section):
                            return content
                        
                        # Add reference to section
                        new_ref_section = ref_section + f"\n- {self.reference_path}"
                        new_docstring = docstring.replace(ref_section, new_ref_section)
                        
                        # Replace docstring in content
                        docstring_pattern = re.compile(r'""".*?"""', re.DOTALL)
                        return docstring_pattern.sub(f'"""{new_docstring}"""', content, count=1)
                else:
                    # Add new references section to docstring
                    new_section = f"\n\n@references: \n- {self.reference_path}"
                    new_docstring = docstring + new_section
                    
                    # Replace docstring in content
                    docstring_pattern = re.compile(r'""".*?"""', re.DOTALL)
                    return docstring_pattern.sub(f'"""{new_docstring}"""', content, count=1)
            else:
                # No docstring found
                return content
        except SyntaxError:
            # Could not parse AST, try simple regex approach
            # Find triple-quoted strings
            docstring_pattern = re.compile(r'"""(.*?)"""', re.DOTALL)
            match = docstring_pattern.search(content)
            
            if match:
                docstring = match.group(1)
                
                # Check if docstring has a references section
                if "@references:" in docstring:
                    # Add reference to existing section
                    ref_section_pattern = re.compile(r'(@references:.*?)(\n\n|\Z)', re.DOTALL)
                    ref_match = ref_section_pattern.search(docstring)
                    
                    if ref_match:
                        ref_section = ref_match.group(1)
                        
                        # Check if the reference is already in the section
                        if REFERENCE_PATTERN.search(ref_section):
                            return content
                        
                        # Add reference to section
                        new_ref_section = ref_section + f"\n- {self.reference_path}"
                        new_docstring = docstring.replace(ref_section, new_ref_section)
                        
                        # Replace docstring in content
                        return content.replace(f'"""{docstring}"""', f'"""{new_docstring}"""', 1)
                else:
                    # Add new references section to docstring
                    new_section = f"\n\n@references: \n- {self.reference_path}"
                    new_docstring = docstring + new_section
                    
                    # Replace docstring in content
                    return content.replace(f'"""{docstring}"""', f'"""{new_docstring}"""', 1)
            else:
                # No docstring found
                return content
    
    def update_all_scripts(self) -> Dict[str, Any]:
        """Update all Python scripts in the specified directory.
        
        Returns:
            Dictionary with update statistics
        """
        # Find Python files
        python_files = self.find_python_files()
        
        # Process files in batches to avoid memory issues
        batch_size = 100
        num_batches = (len(python_files) + batch_size - 1) // batch_size
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(python_files))
            batch = python_files[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_idx + 1}/{num_batches} ({len(batch)} files)")
            
            for python_file in batch:
                logger.info(f"Checking {python_file}")
                self.update_script(python_file)
        
        # Save error log
        if self.stats["errors"] > 0:
            self._save_error_log()
        
        return self.stats
    
    def generate_report(self) -> str:
        """Generate a report of the update process.
        
        Returns:
            Report as a string
        """
        report = []
        report.append("# Script Reference Update Report")
        report.append(f"\nDry Run: {self.dry_run}")
        report.append(f"\nRoot Directory: {self.root_path}")
        report.append(f"\nReference Path: {self.reference_path}")
        report.append(f"\nRetry Errors: {self.retry_errors}")
        
        # Add statistics
        report.append("\n## Statistics")
        report.append(f"\n- Total Scripts: {self.stats['total']}")
        report.append(f"- Scripts with Reference: {self.stats['with_reference']}")
        report.append(f"- Scripts Missing Reference: {self.stats['missing_reference']}")
        report.append(f"- Scripts Updated: {self.stats['updated']}")
        report.append(f"- Scripts Skipped: {self.stats['skipped']}")
        report.append(f"- Scripts with Errors: {self.stats['errors']}")
        
        # Calculate coverage percentage
        if self.stats['total'] > 0:
            coverage = ((self.stats['with_reference'] + self.stats['updated']) / self.stats['total']) * 100
        else:
            coverage = 0
        report.append(f"\n\nReference Coverage: {coverage:.2f}%")
        
        # Add visualization of progress
        report.append("\n## Coverage Visualization")
        report.append("\n```")
        bar_length = 50
        if self.stats['total'] > 0:
            covered = int((self.stats['with_reference'] + self.stats['updated']) / self.stats['total'] * bar_length)
            missing = bar_length - covered
            progress_bar = "[" + "#" * covered + "-" * missing + "]" 
            report.append(progress_bar + f" {coverage:.2f}%")
        else:
            report.append("[--------------------------------------------------] 0.00%")
        report.append("```")
        
        # Add error details
        if self.stats['errors'] > 0:
            report.append("\n## Error Details")
            for error in self.stats['error_details'][:20]:  # Limit to 20 errors to avoid huge reports
                report.append(f"\n### {error['path']}")
                report.append(f"\n```")
                report.append(error['error'])
                report.append("```")
            
            if len(self.stats['error_details']) > 20:
                report.append(f"\n\n*Note: Showing 20 of {len(self.stats['error_details'])} errors. See error log for complete details.*")
        
        # Add timestamp
        report.append(f"\n\n*Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EGOS Script Reference Updater')
    parser.add_argument('--root', type=str, default='C:\\EGOS\\scripts',
                        help='Root directory to search for Python files')
    parser.add_argument('--output', type=str, default='C:\\EGOS\\docs\\reports',
                        help='Output directory for reports')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--exclude', type=str, nargs='+',
                        default=["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"],
                        help='Directories to exclude from scanning')
    parser.add_argument('--reference-path', type=str, 
                        default='C:\\EGOS\\docs_egos\\03_processes\\script_management\\script_management_best_practices.md',
                        help='Path to the Script Management Best Practices document')
    parser.add_argument('--retry-errors', action='store_true',
                        help='Retry scripts that previously had errors')
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    root_path = Path(args.root)
    output_path = Path(args.output)
    reference_path = Path(args.reference_path)
    
    if not root_path.exists():
        logger.error(f"Root directory {root_path} does not exist")
        return 1
    
    if not reference_path.exists():
        logger.warning(f"Reference document {reference_path} does not exist. Will use placeholder path.")
    
    # Create output directory if it doesn't exist
    if not output_path.exists():
        logger.info(f"Creating output directory {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Updating script references in {root_path}")
    
    # Update references
    updater = ScriptReferenceUpdater(
        root_path=root_path,
        reference_path=reference_path,
        exclude_dirs=args.exclude,
        dry_run=args.dry_run,
        retry_errors=args.retry_errors
    )
    
    stats = updater.update_all_scripts()
    
    # Generate and save report
    report = updater.generate_report()
    report_file = output_path / "script_reference_update_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Report saved to {report_file}")
    
    # Print summary
    print("\nScript Reference Update Summary")
    print(f"Total Scripts: {stats['total']}")
    print(f"Scripts with Reference: {stats['with_reference']}")
    print(f"Scripts Missing Reference: {stats['missing_reference']}")
    print(f"Scripts Updated: {stats['updated']}")
    print(f"Scripts Skipped: {stats['skipped']}")
    print(f"Scripts with Errors: {stats['errors']}")
    
    if stats['total'] > 0:
        coverage = ((stats['with_reference'] + stats['updated']) / stats['total']) * 100
    else:
        coverage = 0
    print(f"\nReference Coverage: {coverage:.2f}%")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())