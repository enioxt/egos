#!/usr/bin/env python3
"""EGOS Unique Files Processor

This script processes unique files in old documentation directories based on the
recommendations from the unique_files_analyzer.py script. It can migrate, archive,
or delete files according to the recommendations.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-006
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
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "process_unique_files.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("process_unique_files")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")
ARCHIVE_DIR = os.path.join(DOCS_DIR, "archived")


class UniqueFilesProcessor:
    """
    Processes unique files based on recommendations.
    """

    def __init__(self, root_dir: str = ROOT_DIR, analysis_file: str = None, dry_run: bool = False):
        """
        Initialize the processor.
        
        Args:
            root_dir: Root directory of the EGOS project
            analysis_file: Path to the analysis file (JSON format)
            dry_run: If True, don't actually move or delete files
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.project_documentation_dir = self.docs_dir / "project_documentation"
        self.archive_dir = self.docs_dir / "archived"
        self.analysis_file = analysis_file or os.path.join(SCRIPT_DIR, "unique_files_analysis_report.json")
        self.dry_run = dry_run
        
        # Statistics
        self.stats = {
            "files_migrated": 0,
            "files_archived": 0,
            "files_deleted": 0,
            "errors": 0
        }
        
        # File analysis data
        self.file_analysis = []
        
        # Ensure archive directory exists
        if not self.archive_dir.exists() and not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created archive directory: {self.archive_dir}")
    
    def process_files(self, action: str = "all"):
        """
        Process files based on recommendations.
        
        Args:
            action: Action to perform (migrate, archive, delete, all)
        """
        logger.info(f"Starting to process unique files ({action})...")
        
        # Load analysis data
        self._load_analysis_data()
        
        # Process files based on action
        if action in ["migrate", "all"]:
            self._process_migrate_files()
        
        if action in ["archive", "all"]:
            self._process_archive_files()
        
        if action in ["delete", "all"]:
            self._process_delete_files()
        
        # Generate report
        self._generate_report()
        
        logger.info(f"Processing completed with stats: {self.stats}")
    
    def _load_analysis_data(self):
        """
        Load analysis data from JSON file.
        """
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.file_analysis = data.get("files", [])
            
            logger.info(f"Loaded analysis data with {len(self.file_analysis)} files")
        except Exception as e:
            logger.error(f"Error loading analysis data: {e}")
            sys.exit(1)
    
    def _process_migrate_files(self):
        """
        Process files recommended for migration.
        """
        logger.info("Processing files recommended for migration...")
        
        migrate_files = [f for f in self.file_analysis if f.get("recommendation") == "migrate"]
        logger.info(f"Found {len(migrate_files)} files to migrate")
        
        for file_info in migrate_files:
            try:
                source_path = Path(file_info["path"])
                
                # Determine target path based on category
                target_path = self._determine_target_path(source_path, file_info["category"])
                
                if not target_path:
                    logger.warning(f"Could not determine target path for {source_path}")
                    continue
                
                # Create parent directories if they don't exist
                if not self.dry_run:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                logger.info(f"{'[DRY RUN] Would migrate' if self.dry_run else 'Migrating'} {source_path} -> {target_path}")
                
                if not self.dry_run:
                    shutil.copy2(source_path, target_path)
                    self.stats["files_migrated"] += 1
            except Exception as e:
                logger.error(f"Error migrating {file_info['path']}: {e}")
                self.stats["errors"] += 1
    
    def _process_archive_files(self):
        """
        Process files recommended for archiving.
        """
        logger.info("Processing files recommended for archiving...")
        
        archive_files = [f for f in self.file_analysis if f.get("recommendation") == "archive"]
        logger.info(f"Found {len(archive_files)} files to archive")
        
        for file_info in archive_files:
            try:
                source_path = Path(file_info["path"])
                
                # Determine archive path
                rel_path = source_path.relative_to(self.docs_dir)
                archive_path = self.archive_dir / rel_path
                
                # Create parent directories if they don't exist
                if not self.dry_run:
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                logger.info(f"{'[DRY RUN] Would archive' if self.dry_run else 'Archiving'} {source_path} -> {archive_path}")
                
                if not self.dry_run:
                    shutil.copy2(source_path, archive_path)
                    self.stats["files_archived"] += 1
            except Exception as e:
                logger.error(f"Error archiving {file_info['path']}: {e}")
                self.stats["errors"] += 1
    
    def _process_delete_files(self):
        """
        Process files recommended for deletion.
        """
        logger.info("Processing files recommended for deletion...")
        
        delete_files = [f for f in self.file_analysis if f.get("recommendation") == "delete"]
        logger.info(f"Found {len(delete_files)} files to delete")
        
        for file_info in delete_files:
            try:
                source_path = Path(file_info["path"])
                
                # Delete the file
                logger.info(f"{'[DRY RUN] Would delete' if self.dry_run else 'Deleting'} {source_path}")
                
                if not self.dry_run:
                    source_path.unlink()
                    self.stats["files_deleted"] += 1
            except Exception as e:
                logger.error(f"Error deleting {file_info['path']}: {e}")
                self.stats["errors"] += 1
    
    def _determine_target_path(self, source_path: Path, category: str) -> Optional[Path]:
        """
        Determine the target path for a file based on its category and content.
        
        Args:
            source_path: Source path of the file
            category: File category
            
        Returns:
            Target path for the file, or None if it can't be determined
        """
        # Get relative path from docs directory
        try:
            rel_path = source_path.relative_to(self.docs_dir)
        except ValueError:
            logger.error(f"Source path {source_path} is not under docs directory")
            return None
        
        # Handle different categories
        if category == "documentation":
            # Documentation files go to appropriate subdirectory based on source
            if "reference" in str(rel_path):
                return self.project_documentation_dir / "reference" / rel_path.name
            elif "subsystems" in str(rel_path):
                # Preserve subsystem structure
                parts = rel_path.parts
                if len(parts) > 1:
                    return self.project_documentation_dir / "subsystems" / parts[1] / rel_path.name
                else:
                    return self.project_documentation_dir / "subsystems" / rel_path.name
            elif "governance" in str(rel_path):
                return self.project_documentation_dir / "governance" / rel_path.name
            elif "guides" in str(rel_path):
                return self.project_documentation_dir / "guides" / rel_path.name
            else:
                return self.project_documentation_dir / "reference" / rel_path.name
        
        elif category == "code":
            # Code files go to scripts directory
            return self.root_dir / "scripts" / "migrations" / "imported" / rel_path.name
        
        elif category == "data":
            # Data files go to resources directory
            return self.docs_dir / "resources" / "data" / rel_path.name
        
        elif category == "image":
            # Image files go to assets directory
            return self.docs_dir / "assets" / "images" / rel_path.name
        
        else:
            # Other files go to resources directory
            return self.docs_dir / "resources" / "other" / rel_path.name
    
    def _generate_report(self):
        """
        Generate processing report.
        """
        report_path = os.path.join(SCRIPT_DIR, "process_unique_files_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Unique Files Processing Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Files Migrated:** {self.stats['files_migrated']}\n")
            f.write(f"- **Files Archived:** {self.stats['files_archived']}\n")
            f.write(f"- **Files Deleted:** {self.stats['files_deleted']}\n")
            f.write(f"- **Errors:** {self.stats['errors']}\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the migrated files to ensure they are in the correct location.\n")
            f.write("2. Update any cross-references to the migrated files.\n")
            f.write("3. Review the archived files to ensure they are properly preserved.\n")
            f.write("4. Clean up any empty directories in the old structure.\n")
        
        logger.info(f"Report generated: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS UNIQUE FILES PROCESSING SUMMARY")
        print("=" * 80)
        print(f"- Files Migrated: {self.stats['files_migrated']}")
        print(f"- Files Archived: {self.stats['files_archived']}")
        print(f"- Files Deleted: {self.stats['files_deleted']}")
        print(f"- Errors: {self.stats['errors']}")
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print("=" * 80 + "\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Unique Files Processor")
    parser.add_argument(
        "--action", 
        choices=["migrate", "archive", "delete", "all"],
        default="all",
        help="Action to perform (default: all)"
    )
    parser.add_argument(
        "--analysis-file",
        help="Path to the analysis file (JSON format)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Don't actually move or delete files"
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
    
    logger.info(f"Starting to process unique files ({args.action})...")
    logger.info(f"Root directory: {args.root_dir}")
    logger.info(f"Dry run: {args.dry_run}")
    
    processor = UniqueFilesProcessor(
        root_dir=args.root_dir,
        analysis_file=args.analysis_file,
        dry_run=args.dry_run
    )
    
    try:
        # Process files
        processor.process_files(action=args.action)
        
        logger.info("Processing completed successfully")
        
        return 0
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())