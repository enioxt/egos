#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Reference Fixer

This script fixes invalid references in EGOS documents by updating them to use
the standardized format with EGOS IDs. It prioritizes files with the most invalid
references and can be run in dry-run mode to preview changes.

Part of the EGOS Cross-Reference Standardization Initiative.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - subsystems/AutoCrossRef/CROSSREF_STANDARD.md

# Standard library imports
import os
import re
import sys
import json
import time
import logging
import argparse
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Pattern, Union
from collections import defaultdict

# Third-party imports
from tqdm import tqdm
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    if not 'Fore' in globals():
        Fore = DummyColorama()
    if not 'Style' in globals():
        Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
TERMINAL_WIDTH = 120
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_WORKERS = 4
DEFAULT_TIMEOUT = 30  # seconds

# Configuration
CONFIG = {
    # Performance settings
    "batch_size": DEFAULT_BATCH_SIZE,
    "max_workers": DEFAULT_MAX_WORKERS,
    "timeout": DEFAULT_TIMEOUT,
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'reference_fixer.log'),
    "log_level": "INFO",
    
    # Reference settings
    "reference_block_start": "<!-- crossref_block:start -->",
    "reference_block_end": "<!-- crossref_block:end -->",
    "reference_line_prefix": "- 🔗 Reference: ",
    "egos_id_prefix": "EGOS-REF-",
    
    # File extensions to process
    "file_extensions": ['.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'],
    
    # Directories to exclude
    "exclude_dirs": {'.git', 'venv', 'node_modules', '__pycache__', 'dist', 'build', 'target', 'bin', 'obj'},
    
    # Backup settings
    "create_backups": True,
    "backup_dir": os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'reports', 'backups'),
}

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("reference_fixer")

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# Helper functions
def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (width - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (width - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (width-2)}╝{Style.RESET_ALL}")
    print()

def format_time(seconds: float) -> str:
    """Format time in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def generate_egos_id() -> str:
    """Generate a unique EGOS reference ID."""
    # Use a UUID to ensure uniqueness
    unique_id = str(uuid.uuid4()).split('-')[0]
    return f"{CONFIG['egos_id_prefix']}{unique_id.upper()}"

def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of a file before modifying it.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file, or None if backup failed
    """
    if not CONFIG["create_backups"]:
        return None
    
    try:
        # Create backup directory if it doesn't exist
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(CONFIG["backup_dir"]) / timestamp
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create relative path structure in backup directory
        rel_path = file_path.relative_to(Path.cwd())
        backup_file = backup_dir / rel_path
        os.makedirs(backup_file.parent, exist_ok=True)
        
        # Copy file to backup location
        with open(file_path, 'rb') as src, open(backup_file, 'wb') as dst:
            dst.write(src.read())
        
        logger.debug(f"Created backup of {file_path} at {backup_file}")
        return backup_file
    
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {str(e)}")
        return None

class ReferenceFixer:
    """Reference fixer for EGOS documents."""
    
    def __init__(self, base_path: str, priority_files: List[str] = None, dry_run: bool = False):
        """Initialize the reference fixer.
        
        Args:
            base_path: Base path to process
            priority_files: List of files to prioritize for fixing
            dry_run: If True, don't actually modify files
        """
        self.base_path = Path(base_path)
        self.priority_files = priority_files or []
        self.dry_run = dry_run
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "references_found": 0,
            "references_fixed": 0,
            "errors": 0,
            "processing_time": 0,
        }
        
        # Cache of all files
        self.all_files = set()
        
        # Cache of file paths
        self.file_path_cache = {}
    
    def find_files(self) -> List[Path]:
        """Find all files to process.
        
        Returns:
            List of file paths
        """
        logger.info(f"Finding files to process in {self.base_path}")
        
        files = []
        priority_files_set = set(self.priority_files)
        
        for root, dirs, filenames in os.walk(self.base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in CONFIG["exclude_dirs"]]
            
            for filename in filenames:
                file_path = Path(os.path.join(root, filename))
                
                # Check if extension is in the list to process
                if file_path.suffix.lower() in CONFIG["file_extensions"]:
                    files.append(file_path)
                    self.all_files.add(file_path.resolve())
        
        # Sort files by priority
        if priority_files_set:
            # Put priority files first
            files.sort(key=lambda f: str(f) not in priority_files_set)
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def extract_references(self, content: str) -> List[Tuple[str, str, int, int]]:
        """Extract references from content.
        
        Args:
            content: Content to extract references from
            
        Returns:
            List of tuples (reference_text, reference_target, start_index, end_index)
        """
        references = []
        
        # Find standard markdown links
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            text = match.group(1)
            target = match.group(2)
            
            # Skip external links
            if not target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                references.append((text, target, match.start(), match.end()))
        
        return references
    
    def validate_reference(self, reference: Tuple[str, str], source_file: Path) -> bool:
        """Validate a reference.
        
        Args:
            reference: Tuple (reference_text, reference_target)
            source_file: Path to the source file
            
        Returns:
            True if the reference is valid, False otherwise
        """
        text, target = reference
        
        try:
            # Handle relative paths
            if not os.path.isabs(target):
                target_path = source_file.parent / target
            else:
                target_path = Path(target)
            
            # Normalize path
            target_path = target_path.resolve()
            
            # Check if target exists
            return target_path in self.all_files
        
        except Exception as e:
            logger.error(f"Error validating reference {text} -> {target} in {source_file}: {str(e)}")
            return False
    
    def fix_reference(self, content: str, reference: Tuple[str, str, int, int], source_file: Path) -> Tuple[str, bool]:
        """Fix a reference by updating it to use the standardized format.
        
        Args:
            content: Content to fix
            reference: Tuple (reference_text, reference_target, start_index, end_index)
            source_file: Path to the source file
            
        Returns:
            Tuple (updated_content, was_fixed)
        """
        text, target, start_idx, end_idx = reference
        
        # Check if reference is valid
        is_valid = self.validate_reference((text, target), source_file)
        
        if is_valid:
            # Reference is valid, no need to fix
            return content, False
        
        # Try to find a valid target
        fixed_target = self.find_valid_target(target, source_file)
        
        if fixed_target:
            # Replace the reference with the fixed target
            old_ref = content[start_idx:end_idx]
            new_ref = f"[{text}]({fixed_target})"
            
            # Generate a unique EGOS ID for the reference
            egos_id = generate_egos_id()
            
            # Add EGOS ID to the reference
            new_ref_with_id = f"{new_ref} <!-- {egos_id} -->"
            
            # Replace the reference
            updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
            
            logger.info(f"Fixed reference in {source_file}: {old_ref} -> {new_ref_with_id}")
            return updated_content, True
        
        # Couldn't fix the reference
        return content, False
    
    def find_valid_target(self, target: str, source_file: Path) -> Optional[str]:
        """Find a valid target for a reference.
        
        Args:
            target: Reference target
            source_file: Path to the source file
            
        Returns:
            Valid target path, or None if no valid target could be found
        """
        # Try different extensions
        for ext in CONFIG["file_extensions"]:
            # Try with the extension
            test_target = f"{target}{ext}"
            if self.validate_reference(("", test_target), source_file):
                return test_target
            
            # Try without the current extension and with the new extension
            if "." in target:
                base_target = target.rsplit(".", 1)[0]
                test_target = f"{base_target}{ext}"
                if self.validate_reference(("", test_target), source_file):
                    return test_target
        
        # Try to find a file with a similar name
        try:
            target_filename = os.path.basename(target)
            target_dir = os.path.dirname(target)
            
            # If target_dir is empty, use the source file's directory
            if not target_dir:
                target_dir = str(source_file.parent)
            
            # Resolve the target directory
            if not os.path.isabs(target_dir):
                target_dir = str((source_file.parent / target_dir).resolve())
            
            # Check if we've already cached this directory
            if target_dir not in self.file_path_cache:
                # Cache all files in this directory
                self.file_path_cache[target_dir] = []
                
                if os.path.exists(target_dir) and os.path.isdir(target_dir):
                    for root, _, filenames in os.walk(target_dir):
                        for filename in filenames:
                            if any(filename.endswith(ext) for ext in CONFIG["file_extensions"]):
                                self.file_path_cache[target_dir].append(os.path.join(root, filename))
            
            # Look for similar filenames
            target_base = os.path.splitext(target_filename)[0].lower()
            for file_path in self.file_path_cache[target_dir]:
                file_base = os.path.splitext(os.path.basename(file_path))[0].lower()
                
                # Check if the filename is similar
                if file_base == target_base or target_base in file_base or file_base in target_base:
                    # Convert to relative path from source file
                    rel_path = os.path.relpath(file_path, os.path.dirname(str(source_file)))
                    
                    # Normalize path separators
                    rel_path = rel_path.replace("\\", "/")
                    
                    return rel_path
        
        except Exception as e:
            logger.error(f"Error finding valid target for {target} in {source_file}: {str(e)}")
        
        return None
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results
        """
        result = {
            "file": str(file_path),
            "references_found": 0,
            "references_fixed": 0,
            "was_modified": False,
            "error": None
        }
        
        try:
            # Check if file exists and is readable
            if not file_path.exists() or not os.access(file_path, os.R_OK):
                result["error"] = f"File does not exist or is not readable"
                return result
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract references
            references = self.extract_references(content)
            result["references_found"] = len(references)
            
            # Fix references
            modified_content = content
            for reference in references:
                modified_content, was_fixed = self.fix_reference(modified_content, reference, file_path)
                if was_fixed:
                    result["references_fixed"] += 1
                    result["was_modified"] = True
            
            # Write modified content back to file if needed
            if result["was_modified"] and not self.dry_run:
                # Create backup
                create_backup(file_path)
                
                # Write modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            return result
        
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def process_files(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files.
        
        Args:
            files: List of files to process
            
        Returns:
            List of processing results
        """
        results = []
        total_files = len(files)
        
        # Process files in batches
        batch_size = CONFIG["batch_size"]
        num_batches = (total_files + batch_size - 1) // batch_size
        
        # Create progress bar
        progress = tqdm(
            total=total_files,
            desc=f"{Fore.CYAN}Fixing references{Style.RESET_ALL}",
            unit="files",
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_files = files[start_idx:end_idx]
            
            # Process batch
            for file_path in batch_files:
                result = self.process_file(file_path)
                results.append(result)
                
                # Update statistics
                self.stats["files_processed"] += 1
                
                if result["was_modified"]:
                    self.stats["files_modified"] += 1
                
                self.stats["references_found"] += result["references_found"]
                self.stats["references_fixed"] += result["references_fixed"]
                
                if result["error"]:
                    self.stats["errors"] += 1
                
                # Update progress
                progress.update()
        
        progress.close()
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Path:
        """Generate a report of the fixing results.
        
        Args:
            results: List of processing results
            
        Returns:
            Path to the generated report
        """
        # Create report directory if it doesn't exist
        report_dir = self.base_path / "docs" / "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate report filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"reference_fixer_{timestamp}.md"
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            # Title and metadata
            f.write(f"# EGOS Reference Fixer Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Mode:** {'Dry Run (no files modified)' if self.dry_run else 'Live Run (files modified)'}\n\n")
            
            # Executive summary
            f.write(f"## 📊 Executive Summary\n\n")
            f.write(f"This report presents the results of fixing invalid references across the EGOS ecosystem.\n\n")
            f.write(f"- **Files Processed:** {self.stats['files_processed']:,}\n")
            f.write(f"- **Files Modified:** {self.stats['files_modified']:,} ({self.stats['files_modified'] / self.stats['files_processed'] * 100:.1f}% of files)\n")
            f.write(f"- **References Found:** {self.stats['references_found']:,}\n")
            f.write(f"- **References Fixed:** {self.stats['references_fixed']:,} ({self.stats['references_fixed'] / self.stats['references_found'] * 100:.1f}% of references)\n")
            f.write(f"- **Errors:** {self.stats['errors']:,}\n")
            f.write(f"- **Processing Time:** {format_time(self.stats['processing_time'])}\n\n")
            
            # Modified files
            modified_results = [r for r in results if r["was_modified"]]
            
            if modified_results:
                f.write(f"## 📝 Modified Files\n\n")
                f.write(f"The following files were modified to fix invalid references:\n\n")
                f.write(f"| File | References Fixed | Total References |\n")
                f.write(f"|------|-----------------|------------------|\n")
                
                for result in sorted(modified_results, key=lambda x: x["references_fixed"], reverse=True):
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    f.write(f"| {rel_path} | {result['references_fixed']} | {result['references_found']} |\n")
            else:
                f.write(f"## 📝 No Files Modified\n\n")
                f.write(f"No files were modified during this run.\n\n")
            
            # Errors
            error_results = [r for r in results if r["error"]]
            
            if error_results:
                f.write(f"\n## ⚠️ Errors\n\n")
                f.write(f"The following errors occurred during processing:\n\n")
                f.write(f"| File | Error |\n")
                f.write(f"|------|-------|\n")
                
                for result in error_results:
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    f.write(f"| {rel_path} | {result['error']} |\n")
            
            # Next steps
            f.write(f"\n## 🚀 Next Steps\n\n")
            
            if self.dry_run:
                f.write(f"1. Review this report to ensure the proposed changes are correct\n")
                f.write(f"2. Run the reference fixer in live mode to apply the changes\n")
                f.write(f"3. Run the cross-reference validator to confirm all references are valid\n")
            else:
                f.write(f"1. Run the cross-reference validator to confirm all references are valid\n")
                f.write(f"2. Fix any remaining invalid references manually\n")
                f.write(f"3. Add cross-reference validation to the CI/CD pipeline\n")
            
            # Add EGOS signature
            f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def run(self) -> Path:
        """Run the reference fixer.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Find files to process
        files = self.find_files()
        
        # Process files
        results = self.process_files(files)
        
        # Generate report
        report_path = self.generate_report(results)
        
        # Update statistics
        self.stats["processing_time"] = time.time() - start_time
        
        return report_path

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fix invalid references in EGOS documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Fix references in the current directory (dry run)
  python reference_fixer.py --dry-run
  
  # Fix references in a specific directory
  python reference_fixer.py --base-path /path/to/directory
  
  # Fix references in specific files
  python reference_fixer.py --priority-files file1.md file2.md

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(), help="Base path to process")
    parser.add_argument("--priority-files", type=str, nargs="+", help="List of files to prioritize for fixing")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually modify files")
    parser.add_argument("--batch-size", type=int, default=CONFIG["batch_size"], help="Number of files to process in each batch")
    parser.add_argument("--no-backups", action="store_true", help="Don't create backups before modifying files")
    
    args = parser.parse_args()
    
    # Update configuration from command line arguments
    CONFIG["batch_size"] = args.batch_size
    CONFIG["create_backups"] = not args.no_backups
    
    # Print banner
    print_banner(
        "EGOS Reference Fixer",
        f"{'Dry Run (no files modified)' if args.dry_run else 'Live Run (files will be modified)'}"
    )
    
    # Create and run the reference fixer
    fixer = ReferenceFixer(
        base_path=args.base_path,
        priority_files=args.priority_files,
        dry_run=args.dry_run
    )
    
    try:
        report_path = fixer.run()
        
        # Display summary statistics
        logger.info(f"\n{Fore.GREEN}Reference fixing completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files processed:{Style.RESET_ALL} {fixer.stats['files_processed']:,}")
        logger.info(f"  • {Fore.CYAN}Files modified:{Style.RESET_ALL} {fixer.stats['files_modified']:,} ({fixer.stats['files_modified'] / fixer.stats['files_processed'] * 100:.1f}% of files)")
        logger.info(f"  • {Fore.CYAN}References found:{Style.RESET_ALL} {fixer.stats['references_found']:,}")
        logger.info(f"  • {Fore.CYAN}References fixed:{Style.RESET_ALL} {fixer.stats['references_fixed']:,} ({fixer.stats['references_fixed'] / fixer.stats['references_found'] * 100:.1f}% of references)")
        logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {fixer.stats['errors']:,}")
        logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(fixer.stats['processing_time'])}")
        logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
        
        # Suggest next steps
        print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
        
        if args.dry_run:
            print(f"1. Review the report at {report_path}")
            print(f"2. Run the reference fixer in live mode to apply the changes")
            print(f"3. Run the cross-reference validator to confirm all references are valid")
        else:
            print(f"1. Run the cross-reference validator to confirm all references are valid")
            print(f"2. Fix any remaining invalid references manually")
            print(f"3. Add cross-reference validation to the CI/CD pipeline")
        
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running reference fixer: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()