#!/usr/bin/env python3
"""EGOS Documentation Migration Verification Tool

This script verifies the results of the documentation structure migration,
checking for remaining cross-reference issues, identifying files that should
have been migrated but weren't, and generating a comprehensive migration report.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-003
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
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import yaml
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migration_verification.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("docs_migration_verification")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")

# Old directories that should be empty or removed
OLD_DIRECTORIES = [
    os.path.join(DOCS_DIR, "reference"),
    os.path.join(DOCS_DIR, "subsystems"),
    os.path.join(DOCS_DIR, "governance"),
    os.path.join(DOCS_DIR, "guides"),
    os.path.join(DOCS_DIR, "templates"),
    os.path.join(DOCS_DIR, "development"),
]


class DocsMigrationVerifier:
    """
    Verifies the results of the documentation structure migration.
    """

    def __init__(self, root_dir: str = ROOT_DIR, fix_issues: bool = False):
        """
        Initialize the verifier.
        
        Args:
            root_dir: Root directory of the EGOS project
            fix_issues: If True, attempt to fix identified issues
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.project_documentation_dir = self.docs_dir / "project_documentation"
        self.fix_issues = fix_issues
        
        # Statistics
        self.stats = {
            "broken_references": 0,
            "fixed_references": 0,
            "unmigrated_files": 0,
            "non_empty_old_dirs": 0,
        }
        
        # Lists for reporting
        self.broken_references = []
        self.unmigrated_files = []
        self.non_empty_old_dirs = []
        
    def verify_migration(self):
        """
        Verify the migration results.
        """
        logger.info("Starting migration verification...")
        
        # Check for broken cross-references
        self._check_cross_references()
        
        # Check for unmigrated files
        self._check_unmigrated_files()
        
        # Check if old directories are empty
        self._check_old_directories()
        
        # Generate verification report
        self._generate_report()
        
    def _check_cross_references(self):
        """
        Check for broken cross-references in markdown files.
        """
        logger.info("Checking for broken cross-references...")
        
        # Regular expression to find markdown links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        # Process all markdown files in the project_documentation directory
        for md_file in Path(self.project_documentation_dir).glob("**/*.md"):
            if not md_file.is_file():
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find all links in the content
                links = link_pattern.findall(content)
                modified = False
                
                for link_text, link_path in links:
                    # Skip external links and anchors
                    if link_path.startswith(('http://', 'https://', '#')):
                        continue
                        
                    # Check if the link points to a file that exists
                    target_path = (md_file.parent / link_path).resolve()
                    
                    if not target_path.exists() and not target_path.is_absolute():
                        # This is a broken reference
                        self.stats["broken_references"] += 1
                        self.broken_references.append({
                            "file": str(md_file),
                            "link_text": link_text,
                            "link_path": link_path,
                        })
                        
                        if self.fix_issues:
                            # Try to fix the reference
                            fixed = self._try_fix_reference(md_file, link_text, link_path, content)
                            if fixed:
                                self.stats["fixed_references"] += 1
                                modified = True
                                content = fixed
                
                # Write the updated content back to the file if modified
                if modified and self.fix_issues:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            except Exception as e:
                logger.error(f"Error checking references in {md_file}: {e}")
    
    def _try_fix_reference(self, md_file: Path, link_text: str, link_path: str, content: str) -> Optional[str]:
        """
        Try to fix a broken reference.
        
        Args:
            md_file: The markdown file containing the broken reference
            link_text: The text of the link
            link_path: The path of the link
            content: The content of the file
            
        Returns:
            The updated content if the reference was fixed, None otherwise
        """
        # Extract the filename from the link path
        filename = os.path.basename(link_path)
        
        # Search for the file in the project_documentation directory
        found_files = list(Path(self.project_documentation_dir).glob(f"**/{filename}"))
        
        if len(found_files) == 1:
            # Found exactly one matching file, update the reference
            new_rel_path = os.path.relpath(found_files[0], md_file.parent)
            new_rel_path = new_rel_path.replace('\\', '/')
            
            # Replace the link in the content
            old_link = f'[{link_text}]({link_path})'
            new_link = f'[{link_text}]({new_rel_path})'
            updated_content = content.replace(old_link, new_link)
            
            logger.info(f"Fixed reference in {md_file}: {link_path} -> {new_rel_path}")
            
            return updated_content
        elif len(found_files) > 1:
            # Found multiple matching files, can't automatically determine which one to use
            logger.warning(f"Multiple matches found for {filename}, can't automatically fix reference in {md_file}")
            return None
        else:
            # No matching file found
            logger.warning(f"No match found for {filename}, can't fix reference in {md_file}")
            return None
    
    def _check_unmigrated_files(self):
        """
        Check for files that should have been migrated but weren't.
        """
        logger.info("Checking for unmigrated files...")
        
        # Check each old directory for markdown files
        for old_dir in OLD_DIRECTORIES:
            old_dir_path = Path(old_dir)
            
            if not old_dir_path.exists():
                continue
                
            # Find all markdown files in the old directory
            for md_file in old_dir_path.glob("**/*.md"):
                self.stats["unmigrated_files"] += 1
                self.unmigrated_files.append(str(md_file))
    
    def _check_old_directories(self):
        """
        Check if old directories are empty.
        """
        logger.info("Checking if old directories are empty...")
        
        for old_dir in OLD_DIRECTORIES:
            old_dir_path = Path(old_dir)
            
            if not old_dir_path.exists():
                continue
                
            # Check if directory is empty
            if any(old_dir_path.iterdir()):
                self.stats["non_empty_old_dirs"] += 1
                
                # Get list of files in the directory
                files = list(old_dir_path.glob("**/*"))
                
                self.non_empty_old_dirs.append({
                    "directory": str(old_dir_path),
                    "file_count": len(files),
                    "files": [str(f) for f in files[:10]],  # List up to 10 files
                })
    
    def _generate_report(self):
        """
        Generate a verification report.
        """
        report_path = os.path.join(SCRIPT_DIR, "migration_verification_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Documentation Migration Verification Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Broken Cross-References:** {self.stats['broken_references']}\n")
            f.write(f"- **Fixed Cross-References:** {self.stats['fixed_references']}\n")
            f.write(f"- **Unmigrated Files:** {self.stats['unmigrated_files']}\n")
            f.write(f"- **Non-Empty Old Directories:** {self.stats['non_empty_old_dirs']}\n\n")
            
            if self.broken_references:
                f.write("## Broken Cross-References\n\n")
                for ref in self.broken_references:
                    f.write(f"- **File:** {ref['file']}\n")
                    f.write(f"  - **Link Text:** {ref['link_text']}\n")
                    f.write(f"  - **Link Path:** {ref['link_path']}\n\n")
            
            if self.unmigrated_files:
                f.write("## Unmigrated Files\n\n")
                for file in self.unmigrated_files:
                    f.write(f"- {file}\n")
                f.write("\n")
            
            if self.non_empty_old_dirs:
                f.write("## Non-Empty Old Directories\n\n")
                for dir_info in self.non_empty_old_dirs:
                    f.write(f"- **Directory:** {dir_info['directory']}\n")
                    f.write(f"  - **File Count:** {dir_info['file_count']}\n")
                    f.write(f"  - **Sample Files:**\n")
                    for file in dir_info['files']:
                        f.write(f"    - {file}\n")
                    f.write("\n")
            
            f.write("## Recommendations\n\n")
            
            if self.stats['broken_references'] > 0:
                f.write("- **Fix Broken Cross-References:** Run this script with the `--fix-issues` flag to attempt automatic fixes.\n")
            
            if self.stats['unmigrated_files'] > 0:
                f.write("- **Migrate Remaining Files:** Review and manually migrate the unmigrated files listed above.\n")
            
            if self.stats['non_empty_old_dirs'] > 0:
                f.write("- **Clean Up Old Directories:** Review the contents of non-empty old directories and determine if they should be moved or deleted.\n")
        
        logger.info(f"Verification report generated: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS DOCUMENTATION MIGRATION VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"- Broken Cross-References: {self.stats['broken_references']}")
        print(f"- Fixed Cross-References: {self.stats['fixed_references']}")
        print(f"- Unmigrated Files: {self.stats['unmigrated_files']}")
        print(f"- Non-Empty Old Directories: {self.stats['non_empty_old_dirs']}")
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print("=" * 80 + "\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Documentation Migration Verification Tool")
    parser.add_argument(
        "--fix-issues", 
        action="store_true", 
        help="Attempt to fix identified issues"
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
    
    logger.info(f"Starting documentation migration verification{' (with fixes)' if args.fix_issues else ''}")
    logger.info(f"Root directory: {args.root_dir}")
    
    verifier = DocsMigrationVerifier(root_dir=args.root_dir, fix_issues=args.fix_issues)
    
    try:
        # Verify migration
        verifier.verify_migration()
        
        logger.info("Verification completed successfully")
        logger.info(f"Stats: {verifier.stats}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during verification: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())