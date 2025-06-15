#!/usr/bin/env python3
"""EGOS Documentation Duplicate File Finder

This script identifies duplicate files between old and new documentation directories,
helping to clean up after a migration by identifying which files in the old structure
have already been migrated to the new structure.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-004
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
import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "duplicate_finder.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("docs_duplicate_finder")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")

# Old directories to check for duplicates
OLD_DIRECTORIES = [
    os.path.join(DOCS_DIR, "reference"),
    os.path.join(DOCS_DIR, "subsystems"),
    os.path.join(DOCS_DIR, "governance"),
    os.path.join(DOCS_DIR, "guides"),
    os.path.join(DOCS_DIR, "templates"),
    os.path.join(DOCS_DIR, "development"),
]


class DocsDuplicateFinder:
    """
    Identifies duplicate files between old and new documentation directories.
    """

    def __init__(self, root_dir: str = ROOT_DIR, remove_duplicates: bool = False):
        """
        Initialize the duplicate finder.
        
        Args:
            root_dir: Root directory of the EGOS project
            remove_duplicates: If True, remove duplicate files from old directories
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.project_documentation_dir = self.docs_dir / "project_documentation"
        self.remove_duplicates = remove_duplicates
        
        # Statistics
        self.stats = {
            "files_scanned_old": 0,
            "files_scanned_new": 0,
            "duplicates_found": 0,
            "duplicates_removed": 0,
            "unique_old_files": 0,
        }
        
        # File hashes
        self.new_file_hashes = {}  # hash -> path
        self.old_file_hashes = {}  # hash -> path
        
        # Results
        self.duplicates = []  # [(old_path, new_path), ...]
        self.unique_old_files = []  # [old_path, ...]
        
    def find_duplicates(self):
        """
        Find duplicate files between old and new directories.
        """
        logger.info("Starting duplicate file search...")
        
        # First, hash all files in the new structure
        self._hash_new_files()
        
        # Then, hash all files in the old structure and check for duplicates
        self._hash_old_files()
        
        # Generate report
        self._generate_report()
        
        # Remove duplicates if requested
        if self.remove_duplicates:
            self._remove_duplicates()
        
    def _hash_new_files(self):
        """
        Hash all files in the new documentation structure.
        """
        logger.info("Hashing files in new structure...")
        
        for file_path in Path(self.project_documentation_dir).glob("**/*"):
            if file_path.is_file():
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    self.new_file_hashes[file_hash] = str(file_path)
                    self.stats["files_scanned_new"] += 1
                except Exception as e:
                    logger.error(f"Error hashing {file_path}: {e}")
        
        logger.info(f"Hashed {self.stats['files_scanned_new']} files in new structure")
    
    def _hash_old_files(self):
        """
        Hash all files in the old documentation structure and check for duplicates.
        """
        logger.info("Hashing files in old structure and checking for duplicates...")
        
        for old_dir in OLD_DIRECTORIES:
            old_dir_path = Path(old_dir)
            
            if not old_dir_path.exists():
                continue
                
            for file_path in old_dir_path.glob("**/*"):
                if file_path.is_file():
                    try:
                        file_hash = self._calculate_file_hash(file_path)
                        self.old_file_hashes[file_hash] = str(file_path)
                        self.stats["files_scanned_old"] += 1
                        
                        # Check if this file is a duplicate
                        if file_hash in self.new_file_hashes:
                            self.duplicates.append((str(file_path), self.new_file_hashes[file_hash]))
                            self.stats["duplicates_found"] += 1
                        else:
                            self.unique_old_files.append(str(file_path))
                            self.stats["unique_old_files"] += 1
                    except Exception as e:
                        logger.error(f"Error hashing {file_path}: {e}")
        
        logger.info(f"Hashed {self.stats['files_scanned_old']} files in old structure")
        logger.info(f"Found {self.stats['duplicates_found']} duplicates")
        logger.info(f"Found {self.stats['unique_old_files']} unique files in old structure")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate the MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash of the file
        """
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                
        return hash_md5.hexdigest()
    
    def _generate_report(self):
        """
        Generate a report of duplicate files.
        """
        report_path = os.path.join(SCRIPT_DIR, "duplicate_files_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Documentation Duplicate Files Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Files Scanned in New Structure:** {self.stats['files_scanned_new']}\n")
            f.write(f"- **Files Scanned in Old Structure:** {self.stats['files_scanned_old']}\n")
            f.write(f"- **Duplicates Found:** {self.stats['duplicates_found']}\n")
            f.write(f"- **Unique Files in Old Structure:** {self.stats['unique_old_files']}\n\n")
            
            if self.duplicates:
                f.write("## Duplicate Files\n\n")
                f.write("| Old File | New File |\n")
                f.write("|---------|----------|\n")
                
                # Group duplicates by old directory for better readability
                by_old_dir = {}
                for old_path, new_path in self.duplicates:
                    old_dir = os.path.dirname(old_path)
                    if old_dir not in by_old_dir:
                        by_old_dir[old_dir] = []
                    by_old_dir[old_dir].append((old_path, new_path))
                
                for old_dir, dupes in sorted(by_old_dir.items()):
                    for old_path, new_path in sorted(dupes):
                        f.write(f"| {old_path} | {new_path} |\n")
                
                f.write("\n")
            
            if self.unique_old_files:
                f.write("## Unique Files in Old Structure\n\n")
                
                # Group unique files by directory for better readability
                by_dir = {}
                for file_path in self.unique_old_files:
                    dir_path = os.path.dirname(file_path)
                    if dir_path not in by_dir:
                        by_dir[dir_path] = []
                    by_dir[dir_path].append(file_path)
                
                for dir_path, files in sorted(by_dir.items()):
                    f.write(f"### {dir_path}\n\n")
                    for file_path in sorted(files):
                        f.write(f"- {os.path.basename(file_path)}\n")
                    f.write("\n")
            
            f.write("## Recommendations\n\n")
            
            if self.stats['duplicates_found'] > 0:
                f.write("- **Remove Duplicate Files:** Run this script with the `--remove-duplicates` flag to remove duplicate files from old directories.\n")
            
            if self.stats['unique_old_files'] > 0:
                f.write("- **Review Unique Files:** Review the unique files in old directories and determine if they should be migrated to the new structure.\n")
        
        logger.info(f"Report generated: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS DOCUMENTATION DUPLICATE FILES SUMMARY")
        print("=" * 80)
        print(f"- Files Scanned in New Structure: {self.stats['files_scanned_new']}")
        print(f"- Files Scanned in Old Structure: {self.stats['files_scanned_old']}")
        print(f"- Duplicates Found: {self.stats['duplicates_found']}")
        print(f"- Unique Files in Old Structure: {self.stats['unique_old_files']}")
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print("=" * 80 + "\n")
    
    def _remove_duplicates(self):
        """
        Remove duplicate files from old directories.
        """
        if not self.duplicates:
            logger.info("No duplicates to remove")
            return
            
        logger.info(f"Removing {len(self.duplicates)} duplicate files...")
        
        for old_path, _ in self.duplicates:
            try:
                os.remove(old_path)
                self.stats["duplicates_removed"] += 1
                logger.info(f"Removed duplicate file: {old_path}")
            except Exception as e:
                logger.error(f"Error removing {old_path}: {e}")
        
        logger.info(f"Removed {self.stats['duplicates_removed']} duplicate files")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Documentation Duplicate File Finder")
    parser.add_argument(
        "--remove-duplicates", 
        action="store_true", 
        help="Remove duplicate files from old directories"
    )
    parser.add_argument(
        "--root-dir",
        default=ROOT_DIR,
        help=f"Root directory of the EGOS project (default: {ROOT_DIR})"
    )
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()
    
    logger.info(f"Starting duplicate file search{' (with removal)' if args.remove_duplicates else ''}")
    logger.info(f"Root directory: {args.root_dir}")
    
    finder = DocsDuplicateFinder(root_dir=args.root_dir, remove_duplicates=args.remove_duplicates)
    
    try:
        # Find duplicates
        finder.find_duplicates()
        
        logger.info("Duplicate file search completed successfully")
        logger.info(f"Stats: {finder.stats}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during duplicate file search: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())