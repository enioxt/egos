#!/usr/bin/env python3
"""Reference Migration Script for EGOS

This script migrates existing cross-references to the canonical EGOS cross-reference standards.

@references: <!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->, Cross-reference migration implementation
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

import re
import os
import logging
import yaml
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("reference_migration")

class ReferenceMigrator:
    """Migrates existing cross-references to the canonical EGOS cross-reference standards."""
    
    # Old reference patterns
    OLD_PATTERNS = [
        # @references: format
        re.compile(r'@references:\s*(.*?)(?=\n|$)'),
        # **@references: format
        re.compile(r'\*\*@references:\s*(.*?)\*\*'),
        # Primary References: format
        re.compile(r'\*\*Primary References:\*\*\s*(.*?)(?=\n\n|\n\*\*|\Z)', re.DOTALL),
        # References: format
        re.compile(r'\*\*References:\*\*\s*(.*?)(?=\n\n|\n\*\*|\Z)', re.DOTALL)
    ]
    
    # Reference ID pattern
    REFERENCE_ID_PATTERN = re.compile(r'EGOS-([A-Z]+)-([A-Z]+)-(\d+)')
    
    # YAML frontmatter pattern
    FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
    
    def __init__(
        self, 
        mapping_file: Optional[str] = None,
        dry_run: bool = False,
        backup: bool = True
    ):
        """
        Initialize the Reference Migrator.
        
        Args:
            mapping_file: Path to reference mapping file
            dry_run: Whether to perform a dry run (no changes)
            backup: Whether to create backups of modified files
        """
        self.mapping_file = mapping_file
        self.dry_run = dry_run
        self.backup = backup
        self.mapping = self._load_mapping() if mapping_file else {}
        self.migration_stats = {
            "files_processed": 0,
            "files_modified": 0,
            "references_found": 0,
            "references_migrated": 0,
            "references_mapped": 0,
            "references_generated": 0,
            "errors": 0
        }
        
        logger.info(f"Reference Migrator initialized with dry_run={dry_run}, backup={backup}")
    
    def _load_mapping(self) -> Dict[str, str]:
        """
        Load reference mapping from file.
        
        Returns:
            Dictionary mapping old references to new reference IDs
        """
        if not self.mapping_file or not os.path.exists(self.mapping_file):
            logger.warning(f"Mapping file not found: {self.mapping_file}")
            return {}
        
        try:
            with open(self.mapping_file, 'r') as f:
                mapping = json.load(f)
            
            logger.info(f"Loaded reference mapping with {len(mapping)} entries")
            return mapping
        except Exception as e:
            logger.error(f"Error loading mapping: {str(e)}")
            return {}
    
    def migrate_file(self, file_path: str) -> bool:
        """
        Migrate references in a file.
        
        Args:
            file_path: Path to the file to migrate
            
        Returns:
            True if file was modified, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # Migrate based on file type
            if file_ext == '.py':
                return self._migrate_python_file(file_path)
            elif file_ext == '.md':
                return self._migrate_markdown_file(file_path)
            elif file_ext in ['.yaml', '.yml']:
                return self._migrate_yaml_file(file_path)
            else:
                return self._migrate_generic_file(file_path)
                
        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {str(e)}")
            self.migration_stats["errors"] += 1
            return False
    
    def _migrate_python_file(self, file_path: str) -> bool:
        """
        Migrate references in a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.migration_stats["files_processed"] += 1
            
            # Extract docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if not docstring_match:
                logger.warning(f"No module docstring found in {file_path}")
                return False
            
            docstring = docstring_match.group(0)  # Include the triple quotes
            original_docstring = docstring
            
            # Find references in docstring
            for pattern in self.OLD_PATTERNS:
                for match in pattern.finditer(docstring):
                    self.migration_stats["references_found"] += 1
                    old_reference = match.group(0)
                    new_reference = self._migrate_reference(old_reference)
                    docstring = docstring.replace(old_reference, new_reference)
                    self.migration_stats["references_migrated"] += 1
            
            # If docstring was modified, update file
            if docstring != original_docstring:
                if not self.dry_run:
                    # Create backup if needed
                    if self.backup:
                        backup_path = f"{file_path}.bak"
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"Created backup: {backup_path}")
                    
                    # Update file
                    new_content = content.replace(original_docstring, docstring)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    logger.info(f"Updated references in {file_path}")
                    self.migration_stats["files_modified"] += 1
                else:
                    logger.info(f"Would update references in {file_path} (dry run)")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error migrating Python file {file_path}: {str(e)}")
            self.migration_stats["errors"] += 1
            return False
    
    def _migrate_markdown_file(self, file_path: str) -> bool:
        """
        Migrate references in a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.migration_stats["files_processed"] += 1
            modified = False
            
            # Check for frontmatter
            frontmatter_match = self.FRONTMATTER_PATTERN.match(content)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                
                # Parse frontmatter
                try:
                    frontmatter_data = yaml.safe_load(frontmatter)
                    
                    # Check for references in frontmatter
                    if 'references' not in frontmatter_data:
                        # Extract references from content
                        references = []
                        for pattern in self.OLD_PATTERNS:
                            for match in pattern.finditer(content):
                                old_reference = match.group(1)
                                ref_ids = self._extract_reference_ids(old_reference)
                                references.extend(ref_ids)
                        
                        if references:
                            frontmatter_data['references'] = references
                            new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False)
                            content = content.replace(frontmatter, new_frontmatter)
                            modified = True
                            self.migration_stats["references_migrated"] += len(references)
                    
                except Exception as e:
                    logger.warning(f"Error parsing frontmatter in {file_path}: {str(e)}")
            
            # Migrate inline references
            for pattern in self.OLD_PATTERNS:
                for match in pattern.finditer(content):
                    self.migration_stats["references_found"] += 1
                    old_reference = match.group(0)
                    new_reference = self._migrate_reference(old_reference)
                    if new_reference != old_reference:
                        content = content.replace(old_reference, new_reference)
                        modified = True
                        self.migration_stats["references_migrated"] += 1
            
            # Update file if modified
            if modified and not self.dry_run:
                # Create backup if needed
                if self.backup:
                    backup_path = f"{file_path}.bak"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Created backup: {backup_path}")
                
                # Update file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Updated references in {file_path}")
                self.migration_stats["files_modified"] += 1
            elif modified:
                logger.info(f"Would update references in {file_path} (dry run)")
            
            return modified
            
        except Exception as e:
            logger.error(f"Error migrating Markdown file {file_path}: {str(e)}")
            self.migration_stats["errors"] += 1
            return False
    
    def _migrate_yaml_file(self, file_path: str) -> bool:
        """
        Migrate references in a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.migration_stats["files_processed"] += 1
            modified = False
            
            # Find reference comments
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    for pattern in self.OLD_PATTERNS:
                        match = pattern.search(line)
                        if match:
                            self.migration_stats["references_found"] += 1
                            old_reference = match.group(0)
                            new_reference = self._migrate_reference(old_reference)
                            if new_reference != old_reference:
                                lines[i] = line.replace(old_reference, new_reference)
                                modified = True
                                self.migration_stats["references_migrated"] += 1
            
            # Update file if modified
            if modified and not self.dry_run:
                # Create backup if needed
                if self.backup:
                    backup_path = f"{file_path}.bak"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Created backup: {backup_path}")
                
                # Update file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                logger.info(f"Updated references in {file_path}")
                self.migration_stats["files_modified"] += 1
            elif modified:
                logger.info(f"Would update references in {file_path} (dry run)")
            
            return modified
            
        except Exception as e:
            logger.error(f"Error migrating YAML file {file_path}: {str(e)}")
            self.migration_stats["errors"] += 1
            return False
    
    def _migrate_generic_file(self, file_path: str) -> bool:
        """
        Migrate references in a generic file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.migration_stats["files_processed"] += 1
            modified = False
            
            # Find and migrate references
            for pattern in self.OLD_PATTERNS:
                for match in pattern.finditer(content):
                    self.migration_stats["references_found"] += 1
                    old_reference = match.group(0)
                    new_reference = self._migrate_reference(old_reference)
                    if new_reference != old_reference:
                        content = content.replace(old_reference, new_reference)
                        modified = True
                        self.migration_stats["references_migrated"] += 1
            
            # Update file if modified
            if modified and not self.dry_run:
                # Create backup if needed
                if self.backup:
                    backup_path = f"{file_path}.bak"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Created backup: {backup_path}")
                
                # Update file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Updated references in {file_path}")
                self.migration_stats["files_modified"] += 1
            elif modified:
                logger.info(f"Would update references in {file_path} (dry run)")
            
            return modified
            
        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {str(e)}")
            self.migration_stats["errors"] += 1
            return False
    
    def _migrate_reference(self, reference: str) -> str:
        """
        Migrate a reference to the canonical format.
        
        Args:
            reference: Reference to migrate
            
        Returns:
            Migrated reference
        """
        # Check if reference is already in canonical format
        if self.REFERENCE_ID_PATTERN.search(reference):
            return reference
        
        # Check if reference is in mapping
        if reference in self.mapping:
            mapped_reference = self.mapping[reference]
            self.migration_stats["references_mapped"] += 1
            return mapped_reference
        
        # Generate a new reference ID
        reference_ids = self._extract_reference_ids(reference)
        if reference_ids:
            # Format as canonical reference
            if reference.startswith('@references:'):
                return f"@references: {', '.join(reference_ids)}"
            elif reference.startswith('**@references:'):
                return f"**@references: {', '.join(reference_ids)}**"
            else:
                return f"@references: {', '.join(reference_ids)}"
        
        # If no reference IDs found, return original
        return reference
    
    def _extract_reference_ids(self, reference: str) -> List[str]:
        """
        Extract reference IDs from a reference string.
        
        Args:
            reference: Reference string
            
        Returns:
            List of reference IDs
        """
        # Check for existing reference IDs
        existing_ids = self.REFERENCE_ID_PATTERN.findall(reference)
        if existing_ids:
            return [f"EGOS-{ref_type}-{subsystem}-{number}" for ref_type, subsystem, number in existing_ids]
        
        # Generate a new reference ID
        if 'ETHIK' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        elif 'KOIOS' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        elif 'NEXUS' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        elif 'MYCELIUM' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        elif 'ROADMAP' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        elif 'MQP' in reference:
            ref_id = "<!-- TO_BE_REPLACED -->"
        else:
            ref_id = "<!-- TO_BE_REPLACED -->"
        
        self.migration_stats["references_generated"] += 1
        return [ref_id]
    
    def migrate_directory(
        self, 
        directory_path: str, 
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Migrate all files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to recursively migrate subdirectories
            file_extensions: List of file extensions to migrate (e.g., ['.py', '.md'])
            
        Returns:
            Migration statistics
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return self.migration_stats
        
        # Default to common file types if not specified
        if file_extensions is None:
            file_extensions = ['.py', '.md', '.yaml', '.yml', '.txt']
        
        # Find files to migrate
        files_to_migrate = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        files_to_migrate.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                if os.path.isfile(os.path.join(directory_path, file)) and \
                   any(file.endswith(ext) for ext in file_extensions):
                    files_to_migrate.append(os.path.join(directory_path, file))
        
        # Migrate each file
        for file_path in files_to_migrate:
            self.migrate_file(file_path)
        
        return self.migration_stats
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a migration report.
        
        Args:
            output_path: Path to save the report (optional)
            
        Returns:
            Report dictionary
        """
        # Compile report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "backup": self.backup,
            "stats": self.migration_stats
        }
        
        # Save report if output path provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Migration report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving migration report: {str(e)}")
        
        return report


if __name__ == "__main__":
    # Configure argument parser
    parser = argparse.ArgumentParser(description="Migrate cross-references to EGOS standards")
    parser.add_argument("--path", type=str, required=True, help="File or directory to migrate")
    parser.add_argument("--mapping", type=str, help="Path to reference mapping file")
    parser.add_argument("--output", type=str, help="Path to save migration report")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run (no changes)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backups of modified files")
    parser.add_argument("--recursive", action="store_true", help="Recursively migrate directories")
    parser.add_argument("--extensions", type=str, help="Comma-separated list of file extensions to migrate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = ReferenceMigrator(
        mapping_file=args.mapping,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    # Migrate path
    if os.path.isfile(args.path):
        migrator.migrate_file(args.path)
    elif os.path.isdir(args.path):
        extensions = args.extensions.split(',') if args.extensions else None
        migrator.migrate_directory(
            args.path,
            recursive=args.recursive,
            file_extensions=extensions
        )
    else:
        logger.error(f"Path not found: {args.path}")
        exit(1)
    
    # Generate report
    report = migrator.generate_report(args.output)
    
    # Print summary
    print(f"Migration Summary:")
    print(f"  Dry Run: {report['dry_run']}")
    print(f"  Backup: {report['backup']}")
    print(f"  Files Processed: {report['stats']['files_processed']}")
    print(f"  Files Modified: {report['stats']['files_modified']}")
    print(f"  References Found: {report['stats']['references_found']}")
    print(f"  References Migrated: {report['stats']['references_migrated']}")
    print(f"  References Mapped: {report['stats']['references_mapped']}")
    print(f"  References Generated: {report['stats']['references_generated']}")
    print(f"  Errors: {report['stats']['errors']}")
    
    if args.output:
        print(f"Full report saved to: {args.output}")
