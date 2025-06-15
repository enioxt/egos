#!/usr/bin/env python3
"""EGOS Empty Directories Cleanup

This script identifies and removes empty directories in the specified path,
typically used after a migration process to clean up the file structure.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-007
**Status:** Active
**Version:** 1.0.0

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Set, Optional
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup_empty_directories.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cleanup_empty_directories")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))


class EmptyDirectoryCleaner:
    """
    Identifies and removes empty directories.
    """

    def __init__(self, target_dir: str, exclude_dirs: Optional[List[str]] = None, dry_run: bool = False):
        """
        Initialize the cleaner.
        
        Args:
            target_dir: Target directory to clean
            exclude_dirs: List of directories to exclude from cleaning
            dry_run: If True, don't actually remove directories
        """
        self.target_dir = Path(target_dir)
        self.exclude_dirs = [Path(d) for d in (exclude_dirs or [])]
        self.dry_run = dry_run
        
        # Statistics
        self.stats = {
            "dirs_scanned": 0,
            "empty_dirs_found": 0,
            "dirs_removed": 0,
            "errors": 0
        }
        
        # Ensure target directory exists
        if not self.target_dir.exists():
            logger.error(f"Target directory does not exist: {self.target_dir}")
            sys.exit(1)
    
    def cleanup(self):
        """
        Clean up empty directories.
        """
        logger.info(f"Starting to clean up empty directories in {self.target_dir}...")
        
        # Find empty directories
        empty_dirs = self._find_empty_dirs(self.target_dir)
        self.stats["empty_dirs_found"] = len(empty_dirs)
        
        # Sort directories by depth (deepest first)
        empty_dirs_sorted = sorted(empty_dirs, key=lambda p: len(p.parts), reverse=True)
        
        # Remove empty directories
        for dir_path in empty_dirs_sorted:
            try:
                logger.info(f"{'[DRY RUN] Would remove' if self.dry_run else 'Removing'} empty directory: {dir_path}")
                
                if not self.dry_run:
                    dir_path.rmdir()
                    self.stats["dirs_removed"] += 1
            except Exception as e:
                logger.error(f"Error removing directory {dir_path}: {e}")
                self.stats["errors"] += 1
        
        # Generate report
        self._generate_report()
        
        logger.info(f"Cleanup completed with stats: {self.stats}")
    
    def _find_empty_dirs(self, start_dir: Path) -> Set[Path]:
        """
        Find empty directories recursively.
        
        Args:
            start_dir: Starting directory
            
        Returns:
            Set of empty directory paths
        """
        empty_dirs = set()
        
        for root, dirs, files in os.walk(start_dir, topdown=False):
            root_path = Path(root)
            self.stats["dirs_scanned"] += 1
            
            # Skip excluded directories
            if any(self._is_same_or_parent(ex_dir, root_path) for ex_dir in self.exclude_dirs):
                logger.debug(f"Skipping excluded directory: {root_path}")
                continue
            
            # Check if directory is empty
            if not dirs and not files:
                logger.debug(f"Found empty directory: {root_path}")
                empty_dirs.add(root_path)
        
        return empty_dirs
    
    def _is_same_or_parent(self, parent: Path, child: Path) -> bool:
        """
        Check if a path is the same as or a parent of another path.
        
        Args:
            parent: Potential parent path
            child: Potential child path
            
        Returns:
            True if parent is the same as or a parent of child
        """
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False
    
    def _generate_report(self):
        """
        Generate cleanup report.
        """
        report_path = os.path.join(SCRIPT_DIR, "cleanup_empty_directories_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Empty Directories Cleanup Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Target Directory:** {self.target_dir}\n")
            f.write(f"- **Directories Scanned:** {self.stats['dirs_scanned']}\n")
            f.write(f"- **Empty Directories Found:** {self.stats['empty_dirs_found']}\n")
            f.write(f"- **Directories Removed:** {self.stats['dirs_removed']}\n")
            f.write(f"- **Errors:** {self.stats['errors']}\n\n")
            
            if self.exclude_dirs:
                f.write("## Excluded Directories\n\n")
                for dir_path in self.exclude_dirs:
                    f.write(f"- {dir_path}\n")
                f.write("\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Verify that no important directories were accidentally removed.\n")
            f.write("2. Update any references to the removed directories in documentation or code.\n")
        
        logger.info(f"Report generated: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS EMPTY DIRECTORIES CLEANUP SUMMARY")
        print("=" * 80)
        print(f"- Target Directory: {self.target_dir}")
        print(f"- Directories Scanned: {self.stats['dirs_scanned']}")
        print(f"- Empty Directories Found: {self.stats['empty_dirs_found']}")
        print(f"- Directories Removed: {self.stats['dirs_removed']}")
        print(f"- Errors: {self.stats['errors']}")
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print("=" * 80 + "\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Empty Directories Cleanup")
    parser.add_argument(
        "--target-dir",
        default=os.path.join(ROOT_DIR, "docs"),
        help=f"Target directory to clean (default: {os.path.join(ROOT_DIR, 'docs')})"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        help="Directories to exclude from cleaning"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Don't actually remove directories"
    )
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()
    
    logger.info(f"Starting to clean up empty directories...")
    logger.info(f"Target directory: {args.target_dir}")
    logger.info(f"Exclude directories: {args.exclude_dirs or []}")
    logger.info(f"Dry run: {args.dry_run}")
    
    cleaner = EmptyDirectoryCleaner(
        target_dir=args.target_dir,
        exclude_dirs=args.exclude_dirs,
        dry_run=args.dry_run
    )
    
    try:
        # Clean up empty directories
        cleaner.cleanup()
        
        logger.info("Cleanup completed successfully")
        
        return 0
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())