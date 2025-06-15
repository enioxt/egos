#!/usr/bin/env python3
"""EGOS Documentation Structure Migration Tool

This script implements the documentation reorganization plan outlined in 
DOCS_DIRECTORY_DIAGNOSTIC_20250518.md. It handles the migration of documentation 
files to the new structure, updates cross-references, and removes old directories
once migration is complete.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-002
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
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import yaml
from datetime import datetime

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migration_plan.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("docs_structure_migrator")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")


class DocsStructureMigrator:
    """
    Handles the migration of documentation files to the new structure.
    """

    def __init__(self, root_dir: str = ROOT_DIR, dry_run: bool = False):
        """
        Initialize the migrator.
        
        Args:
            root_dir: Root directory of the EGOS project
            dry_run: If True, don't actually move files or update references
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.project_documentation_dir = self.docs_dir / "project_documentation"
        self.dry_run = dry_run
        
        # Statistics
        self.stats = {
            "files_moved": 0,
            "references_updated": 0,
            "directories_created": 0,
            "directories_removed": 0,
        }
        
        # Mapping of old paths to new paths
        self.path_mapping: Dict[str, str] = {}
        
        # Set of directories to remove after migration
        self.directories_to_remove: Set[str] = set()
        
        # Ensure project_documentation directory exists
        if not self.project_documentation_dir.exists() and not self.dry_run:
            self.project_documentation_dir.mkdir(parents=True, exist_ok=True)
            self.stats["directories_created"] += 1
            
    def build_migration_plan(self):
        """
        Build the migration plan based on the diagnostic document.
        """
        logger.info("Building migration plan...")
        
        # Core directories in project_documentation
        core_dirs = [
            "core",
            "architecture",
            "standards",
            "guides",
            "reference",
            "governance",
            "subsystems",
        ]
        
        # Create core directories if they don't exist
        for dir_name in core_dirs:
            dir_path = self.project_documentation_dir / dir_name
            if not dir_path.exists() and not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stats["directories_created"] += 1
                logger.info(f"Created directory: {dir_path}")
        
        # Build mapping for reference documents
        self._map_reference_docs()
        
        # Build mapping for governance documents
        self._map_governance_docs()
        
        # Build mapping for subsystem documents
        self._map_subsystem_docs()
        
        # Build mapping for guides
        self._map_guides()
        
        # Build mapping for templates
        self._map_templates()
        
        # Build mapping for development documents
        self._map_development_docs()
        
        logger.info(f"Migration plan built with {len(self.path_mapping)} file mappings")
        
    def _map_reference_docs(self):
        """Map reference documents to their new locations."""
        reference_dir = self.docs_dir / "reference"
        if not reference_dir.exists():
            return
            
        # Add reference directory to directories to remove
        self.directories_to_remove.add(str(reference_dir))
        
        # Core reference documents go to core directory
        core_docs = ["MQP.md", "ROADMAP.md", "PHILOSOPHY.md", "STRATEGY.md"]
        
        for doc in reference_dir.glob("*.md"):
            if doc.name in core_docs:
                new_path = self.project_documentation_dir / "core" / doc.name
            else:
                new_path = self.project_documentation_dir / "reference" / doc.name
                
            self.path_mapping[str(doc)] = str(new_path)
            
        # Handle subdirectories
        for subdir in reference_dir.glob("*/"):
            if subdir.is_dir() and not subdir.name.startswith("."):
                new_subdir = self.project_documentation_dir / "reference" / subdir.name
                
                for doc in subdir.glob("**/*.md"):
                    rel_path = doc.relative_to(subdir)
                    new_path = new_subdir / rel_path
                    self.path_mapping[str(doc)] = str(new_path)
    
    def _map_governance_docs(self):
        """Map governance documents to their new locations."""
        governance_dir = self.docs_dir / "governance"
        if not governance_dir.exists():
            return
            
        # Add governance directory to directories to remove
        self.directories_to_remove.add(str(governance_dir))
        
        # Map all governance documents
        for doc in governance_dir.glob("**/*.md"):
            rel_path = doc.relative_to(governance_dir)
            new_path = self.project_documentation_dir / "governance" / rel_path
            self.path_mapping[str(doc)] = str(new_path)
    
    def _map_subsystem_docs(self):
        """Map subsystem documents to their new locations."""
        subsystems_dir = self.docs_dir / "subsystems"
        if not subsystems_dir.exists():
            return
            
        # Add subsystems directory to directories to remove
        self.directories_to_remove.add(str(subsystems_dir))
        
        # Map all subsystem documents
        for doc in subsystems_dir.glob("**/*.md"):
            rel_path = doc.relative_to(subsystems_dir)
            new_path = self.project_documentation_dir / "subsystems" / rel_path
            self.path_mapping[str(doc)] = str(new_path)
    
    def _map_guides(self):
        """Map guides to their new locations."""
        guides_dir = self.docs_dir / "guides"
        if not guides_dir.exists():
            return
            
        # Add guides directory to directories to remove
        self.directories_to_remove.add(str(guides_dir))
        
        # Map all guides
        for doc in guides_dir.glob("**/*.md"):
            rel_path = doc.relative_to(guides_dir)
            new_path = self.project_documentation_dir / "guides" / rel_path
            self.path_mapping[str(doc)] = str(new_path)
    
    def _map_templates(self):
        """Map templates to their new locations."""
        templates_dir = self.docs_dir / "templates"
        if not templates_dir.exists():
            return
            
        # Add templates directory to directories to remove
        self.directories_to_remove.add(str(templates_dir))
        
        # Map all templates
        for doc in templates_dir.glob("**/*"):
            if doc.is_file():
                rel_path = doc.relative_to(templates_dir)
                new_path = self.project_documentation_dir / "reference" / "templates" / rel_path
                self.path_mapping[str(doc)] = str(new_path)
    
    def _map_development_docs(self):
        """Map development documents to their new locations."""
        development_dir = self.docs_dir / "development"
        if not development_dir.exists():
            return
            
        # Add development directory to directories to remove
        self.directories_to_remove.add(str(development_dir))
        
        # Map all development documents
        for doc in development_dir.glob("**/*.md"):
            rel_path = doc.relative_to(development_dir)
            new_path = self.project_documentation_dir / "guides" / "development" / rel_path
            self.path_mapping[str(doc)] = str(new_path)
    
    def output_migration_plan(self):
        """
        Output a detailed migration plan summary.
        """
        logger.info("\n" + "=" * 80)
        logger.info("DETAILED MIGRATION PLAN SUMMARY")
        logger.info("=" * 80)
        
        # Group files by source directory
        by_source_dir = {}
        for old_path, new_path in self.path_mapping.items():
            source_dir = os.path.dirname(old_path)
            if source_dir not in by_source_dir:
                by_source_dir[source_dir] = []
            by_source_dir[source_dir].append((old_path, new_path))
        
        # Output summary by source directory
        for source_dir, files in sorted(by_source_dir.items()):
            logger.info(f"\nSource Directory: {source_dir}")
            logger.info("-" * 40)
            for old_path, new_path in sorted(files):
                logger.info(f"  {os.path.basename(old_path)} -> {new_path}")
        
        # Output directories to be removed
        logger.info("\n" + "=" * 80)
        logger.info("DIRECTORIES TO BE REMOVED")
        logger.info("=" * 80)
        for dir_path in sorted(self.directories_to_remove):
            logger.info(f"  {dir_path}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"TOTAL FILES TO BE MOVED: {len(self.path_mapping)}")
        logger.info(f"TOTAL DIRECTORIES TO BE REMOVED: {len(self.directories_to_remove)}")
        logger.info("=" * 80 + "\n")
        
    def execute_migration(self):
        """
        Execute the migration plan.
        """
        # Output detailed migration plan
        self.output_migration_plan()
        
        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Executing migration plan...")
        
        # Move files according to the mapping
        for old_path, new_path in self.path_mapping.items():
            self._move_file(old_path, new_path)
        
        # Update cross-references in all markdown files
        self._update_cross_references()
        
        # Remove old directories if they're empty
        if not self.dry_run:
            self._remove_empty_directories()
        
        logger.info(f"Migration completed with stats: {self.stats}")
    
    def _move_file(self, old_path: str, new_path: str):
        """
        Move a file from old_path to new_path.
        
        Args:
            old_path: Path to the file to move
            new_path: Path to move the file to
        """
        old_path = Path(old_path)
        new_path = Path(new_path)
        
        if not old_path.exists():
            logger.warning(f"Source file does not exist: {old_path}")
            return
            
        # Create parent directories if they don't exist
        if not self.dry_run:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"{'[DRY RUN] Would move' if self.dry_run else 'Moving'} {old_path} -> {new_path}")
        
        if not self.dry_run:
            # Ensure parent directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file to the new location
            shutil.copy2(old_path, new_path)
            
            # Remove the old file
            old_path.unlink()
            
            self.stats["files_moved"] += 1
    
    def _update_cross_references(self):
        """
        Update cross-references in all markdown files.
        """
        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Updating cross-references...")
        
        # Build reverse mapping for path lookup
        old_paths = {os.path.normpath(p).lower(): p for p in self.path_mapping.keys()}
        new_paths = {os.path.normpath(p).lower(): p for p in self.path_mapping.values()}
        
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
                        
                    # Normalize path
                    norm_link_path = os.path.normpath(link_path).lower()
                    
                    # Check if this is a link to a file that was moved
                    for old_path, new_path in self.path_mapping.items():
                        old_rel_path = os.path.relpath(old_path, self.docs_dir).lower()
                        
                        if norm_link_path == old_rel_path or norm_link_path.endswith(old_rel_path):
                            # Calculate new relative path
                            new_rel_path = os.path.relpath(new_path, md_file.parent)
                            new_rel_path = new_rel_path.replace('\\', '/')
                            
                            # Replace the link in the content
                            old_link = f'[{link_text}]({link_path})'
                            new_link = f'[{link_text}]({new_rel_path})'
                            content = content.replace(old_link, new_link)
                            modified = True
                            self.stats["references_updated"] += 1
                            logger.debug(f"Updated reference in {md_file}: {link_path} -> {new_rel_path}")
                
                # Write the updated content back to the file
                if modified and not self.dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            except Exception as e:
                logger.error(f"Error updating references in {md_file}: {e}")
    
    def _remove_empty_directories(self):
        """
        Remove empty directories after migration.
        """
        logger.info("Removing empty directories...")
        
        for dir_path in sorted(self.directories_to_remove, key=len, reverse=True):
            dir_path = Path(dir_path)
            
            if not dir_path.exists():
                continue
                
            # Check if directory is empty
            if not any(dir_path.iterdir()):
                logger.info(f"Removing empty directory: {dir_path}")
                dir_path.rmdir()
                self.stats["directories_removed"] += 1
            else:
                logger.warning(f"Directory not empty, skipping removal: {dir_path}")
                
                # List remaining files
                remaining_files = list(dir_path.glob("**/*"))
                if len(remaining_files) <= 10:
                    for file in remaining_files:
                        logger.warning(f"  Remaining file: {file}")
                else:
                    logger.warning(f"  {len(remaining_files)} files remaining")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Documentation Structure Migration Tool")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show changes without applying them"
    )
    parser.add_argument(
        "--root-dir",
        default=ROOT_DIR,
        help=f"Root directory of the EGOS project (default: {ROOT_DIR})"
    )
    return parser.parse_args()


def output_summary_report(migrator):
    """Output a concise summary report to the console."""
    print("\n" + "=" * 80)
    print("EGOS DOCUMENTATION MIGRATION SUMMARY")
    print("=" * 80)
    
    # Count files by source directory
    by_source_dir = {}
    for old_path in migrator.path_mapping.keys():
        source_dir = os.path.dirname(old_path)
        if source_dir not in by_source_dir:
            by_source_dir[source_dir] = 0
        by_source_dir[source_dir] += 1
    
    # Output summary by source directory
    print("\nFiles to be moved by source directory:")
    print("-" * 40)
    for source_dir, count in sorted(by_source_dir.items()):
        print(f"  {source_dir}: {count} files")
    
    # Output directories to be removed
    print("\nDirectories to be removed:")
    print("-" * 40)
    for dir_path in sorted(migrator.directories_to_remove):
        print(f"  {dir_path}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL FILES TO BE MOVED: {len(migrator.path_mapping)}")
    print(f"TOTAL DIRECTORIES TO BE REMOVED: {len(migrator.directories_to_remove)}")
    print("=" * 80 + "\n")

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    logger.info(f"Starting documentation structure migration{' (DRY RUN)' if args.dry_run else ''}")
    logger.info(f"Root directory: {args.root_dir}")
    
    migrator = DocsStructureMigrator(root_dir=args.root_dir, dry_run=args.dry_run)
    
    try:
        # Build migration plan
        migrator.build_migration_plan()
        
        # Output summary report
        output_summary_report(migrator)
        
        if not args.dry_run:
            # Execute migration
            migrator.execute_migration()
            
            logger.info("Migration completed successfully")
            logger.info(f"Stats: {migrator.stats}")
        else:
            print("\nThis was a dry run. No files were actually moved.")
            print("Run without --dry-run to execute the migration.")
        
        return 0
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())