#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Docstring Validator

This script validates that all scripts in the system_health directory have proper
docstrings and references according to EGOS standards. It follows RULE-SCRIPT-STD-03
for script structure and ensures all scripts maintain proper cross-references.

@author: EGOS Development Team
@date: 2025-05-27
@version: 0.1.0

@references:
- C:\EGOS\MQP.md (Conscious Modularity, Systemic Cartography)
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\.windsurfrules (RULE-SCRIPT-STD-03)
- C:\EGOS\docs\index\documentation_index.md
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
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("docstring_validator")

# Constants
SCRIPT_EXTENSIONS = ['.py']
DEFAULT_EXCLUSIONS = [
    '.git', 'venv', '.venv', 'env', 'node_modules', '__pycache__', 
    '.vscode', '.idea', 'build', 'dist', '.pytest_cache'
]

class DocstringValidator:
    """Validator for script docstrings and references."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validator with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        # Default configuration
        self.default_config = {
            "exclusions": DEFAULT_EXCLUSIONS,
            "script_extensions": SCRIPT_EXTENSIONS,
            "required_docstring_elements": [
                "@author", "@date", "@version", "@references"
            ],
            "min_docstring_lines": 3
        }
        
        # Merge with provided config
        self.config = self.default_config.copy()
        if config:
            self._merge_config(self.config, config)
        
        # Initialize data structures
        self.scripts = {}  # path -> metadata
        self.issues = []  # list of issues
    
    def _merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to override base
            
        Returns:
            Merged configuration
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
        return base_config
    
    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on exclusion rules.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        # Check directory exclusions
        for part in path.parts:
            if part in self.config["exclusions"]:
                return True
        
        return False
    
    def is_script(self, path: Path) -> bool:
        """Check if a path is a script file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a script file, False otherwise
        """
        return path.suffix.lower() in self.config["script_extensions"]
    
    def scan_directory(self, directory: Union[str, Path]) -> None:
        """Scan a directory for scripts.
        
        Args:
            directory: Directory to scan
        """
        directory = Path(directory)
        logger.info(f"Scanning directory: {directory}")
        
        # Walk the directory tree
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
            
            root_path = Path(root)
            
            # Process files
            for file_name in files:
                file_path = root_path / file_name
                
                # Skip excluded files
                if self.should_exclude(file_path):
                    continue
                
                # Process scripts
                if self.is_script(file_path):
                    self.scripts[str(file_path)] = {
                        "path": str(file_path),
                        "name": file_name,
                        "directory": str(root_path),
                        "has_docstring": False,
                        "docstring_lines": 0,
                        "has_required_elements": {},
                        "missing_elements": [],
                        "references": []
                    }
    
    def validate_docstrings(self) -> None:
        """Validate docstrings in all scripts."""
        logger.info(f"Validating docstrings in {len(self.scripts)} scripts")
        
        for path, metadata in self.scripts.items():
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for docstring
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    docstring = docstring_match.group(1).strip()
                    docstring_lines = docstring.count('\n') + 1
                    
                    metadata["has_docstring"] = True
                    metadata["docstring_lines"] = docstring_lines
                    
                    # Check for required elements
                    for element in self.config["required_docstring_elements"]:
                        has_element = element.lower() in docstring.lower()
                        metadata["has_required_elements"][element] = has_element
                        
                        if not has_element:
                            metadata["missing_elements"].append(element)
                    
                    # Extract references
                    references_match = re.search(r'@references:(.*?)(?=\n\w|\Z)', docstring, re.DOTALL)
                    if references_match:
                        references = references_match.group(1).strip().split('\n')
                        metadata["references"] = [ref.strip() for ref in references if ref.strip()]
                
                # Check if docstring is too short
                if metadata["docstring_lines"] < self.config["min_docstring_lines"]:
                    self.issues.append({
                        "path": path,
                        "issue": "Docstring too short",
                        "details": f"Docstring has {metadata['docstring_lines']} lines, minimum is {self.config['min_docstring_lines']}"
                    })
                
                # Check for missing elements
                if metadata["missing_elements"]:
                    self.issues.append({
                        "path": path,
                        "issue": "Missing docstring elements",
                        "details": f"Missing elements: {', '.join(metadata['missing_elements'])}"
                    })
                
                # Check if no docstring
                if not metadata["has_docstring"]:
                    self.issues.append({
                        "path": path,
                        "issue": "No docstring",
                        "details": "Script has no docstring"
                    })
            
            except Exception as e:
                logger.warning(f"Error validating docstring in {path}: {e}")
                self.issues.append({
                    "path": path,
                    "issue": "Error validating docstring",
                    "details": str(e)
                })
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate a report of the validation results.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Markdown report content
        """
        logger.info("Generating report")
        
        # Build report sections
        sections = []
        
        # Header
        sections.append("# EGOS Docstring Validation Report")
        sections.append(f"Generated: {os.path.basename(__file__)}")
        sections.append("")
        
        # Summary
        sections.append("## Summary")
        sections.append(f"- Total scripts analyzed: {len(self.scripts)}")
        sections.append(f"- Scripts with issues: {len(self.issues)}")
        sections.append(f"- Scripts with proper docstrings: {len(self.scripts) - len(self.issues)}")
        sections.append(f"- Compliance rate: {(len(self.scripts) - len(self.issues)) / len(self.scripts) * 100:.2f}%")
        sections.append("")
        
        # Issues
        if self.issues:
            sections.append("## Issues")
            sections.append("| Script | Issue | Details |")
            sections.append("|--------|-------|---------|")
            
            for issue in self.issues:
                sections.append(f"| {issue['path']} | {issue['issue']} | {issue['details']} |")
            
            sections.append("")
        
        # Recommendations
        sections.append("## Recommendations")
        sections.append("To fix the identified issues:")
        sections.append("")
        sections.append("1. **Add proper docstrings** to all scripts without docstrings.")
        sections.append("2. **Expand short docstrings** to include more detailed information.")
        sections.append("3. **Add missing elements** to docstrings, especially `@author`, `@date`, `@version`, and `@references`.")
        sections.append("4. **Update references** to include all relevant documents.")
        sections.append("")
        
        # Join sections
        report = "\n".join(sections)
        
        # Save report if output path provided
        if output_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write report
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                logger.info(f"Report saved to {output_path}")
            
            except Exception as e:
                logger.error(f"Error saving report: {e}")
        
        return report
    
    def validate(self, target_path: Union[str, Path]) -> Dict[str, Any]:
        """Run the complete validation process.
        
        Args:
            target_path: Path to validate
            
        Returns:
            Validation results
        """
        # Scan directory
        self.scan_directory(target_path)
        
        # Validate docstrings
        self.validate_docstrings()
        
        # Return results
        return {
            "scripts": self.scripts,
            "issues": self.issues
        }

def print_banner():
    """Print a banner for the docstring validator."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║             EGOS Docstring Validator                          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main function for running the docstring validator from the command line."""
    parser = argparse.ArgumentParser(description="EGOS Docstring Validator")
    parser.add_argument("target_path", nargs="?", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help="Path to validate (default: parent directory)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Path to save the report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print_banner()
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Create validator
    validator = DocstringValidator(config)
    
    # Run validation
    logger.info(f"Validating {args.target_path}")
    validator.validate(args.target_path)
    
    # Generate report
    output_path = args.output
    if not output_path:
        # Generate default output path
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "docstring_validation_report.md")
    
    report = validator.generate_report(output_path)
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total scripts analyzed: {len(validator.scripts)}")
    print(f"Scripts with issues: {len(validator.issues)}")
    print(f"Scripts with proper docstrings: {len(validator.scripts) - len(validator.issues)}")
    print(f"Compliance rate: {(len(validator.scripts) - len(validator.issues)) / len(validator.scripts) * 100:.2f}%")
    print(f"\nReport saved to {output_path}")
    
    # Return exit code based on issues found
    return 1 if validator.issues else 0

if __name__ == "__main__":
    sys.exit(main())