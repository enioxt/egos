#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Scheduled Cleanup Script
-----------------------------
Performs automated cleanup of temporary files and enforces retention policies.
Part of the LEGACY-CLEANUP-01 process.

This script follows the EGOS principles of:
- Compassionate Temporality: Respecting natural rhythms of evolution
- Evolutionary Preservation: Maintaining essence while allowing transformation
- Conscious Modularity: Understanding the relationship between parts and whole
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
import argparse
import logging
import datetime
import shutil
import glob
import json
from typing import Dict, List, Optional, Set, Tuple, Any

# Setup logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger("egos_cleanup")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Define retention policies (in days)
DEFAULT_RETENTION_POLICIES = {
    "temp_files": 7,    # Temporary files
    "logs": 30,         # Log files
    "backups": 90,      # Backup files
    "htmlcov": 14,      # HTML coverage reports
    "cache": 7,         # Cache files
    "old_versions": 180 # Old versions of files
}

# Define patterns for cleanup
DEFAULT_CLEANUP_PATTERNS = {
    "temp_files": ["*.tmp", "*.temp", "*.bak", "*.old", "*.backup", "~*"],
    "logs": ["*.log", "log/*.txt", "logs/*.log", "*.log.*"],
    "htmlcov": ["htmlcov/*", "*/htmlcov/*"],
    "cache": ["__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".ruff_cache", ".mypy_cache"],
    "old_versions": ["*_v[0-9].*", "*_old.*", "*_backup.*", "*_bak.*"]
}

# Default directories to exclude from cleanup
DEFAULT_EXCLUDE_DIRS = [
    ".git", ".github", ".vscode", "venv", ".venv", "env", "node_modules"
]

class EgosCleanupManager:
    """Manager for EGOS system cleanup operations."""

    def __init__(
        self,
        root_dir: str,
        retention_policies: Optional[Dict[str, int]] = None,
        cleanup_patterns: Optional[Dict[str, List[str]]] = None,
        exclude_dirs: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
        log_file: Optional[str] = None
    ):
        """
        Initialize the cleanup manager.

        Args:
            root_dir: Root directory to clean
            retention_policies: Dictionary of retention policies (days)
            cleanup_patterns: Dictionary of file patterns to clean
            exclude_dirs: Directories to exclude from cleanup
            dry_run: If True, only show what would be done without actually deleting
            verbose: If True, show detailed logs
            log_file: Optional file to log operations
        """
        self.root_dir = os.path.abspath(root_dir)
        self.retention_policies = retention_policies or DEFAULT_RETENTION_POLICIES
        self.cleanup_patterns = cleanup_patterns or DEFAULT_CLEANUP_PATTERNS
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.dry_run = dry_run
        self.verbose = verbose

        # Setup file logging if requested
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_formatter)
            logger.addHandler(file_handler)

        # Set logging level
        if verbose:
            logger.setLevel(logging.DEBUG)

        # Statistics
        self.stats = {
            "total_files_scanned": 0,
            "files_deleted": 0,
            "bytes_freed": 0,
            "errors": 0,
            "by_category": {}
        }

        logger.info(f"Initializing EGOS Cleanup Manager for {self.root_dir}")
        logger.debug(f"Retention policies: {self.retention_policies}")
        logger.debug(f"Cleanup patterns: {self.cleanup_patterns}")
        logger.debug(f"Exclude directories: {self.exclude_dirs}")
        logger.info(f"Dry run: {self.dry_run}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _should_exclude_dir(self, dir_path: str) -> bool:
        """Check if a directory should be excluded from cleanup."""
        for exclude_dir in self.exclude_dirs:
            if f"/{exclude_dir}/" in dir_path.replace("\\", "/") or f"\\{exclude_dir}\\" in dir_path:
                return True
        return False

    def _is_file_expired(self, file_path: str, category: str) -> bool:
        """Check if a file is older than the retention policy."""
        if category not in self.retention_policies:
            return False

        try:
            max_age_days = self.retention_policies[category]
            file_time = os.path.getmtime(file_path)
            file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(file_time)
            return file_age.days > max_age_days
        except Exception as e:
            logger.warning(f"Error checking file age for {file_path}: {e}")
            return False

    def clean_by_pattern(self, category: str) -> None:
        """
        Clean files matching patterns in the specified category.

        Args:
            category: Category of files to clean (must be in cleanup_patterns)
        """
        if category not in self.cleanup_patterns:
            logger.warning(f"Unknown cleanup category: {category}")
            return

        patterns = self.cleanup_patterns[category]
        logger.info(f"Cleaning {category} files with patterns: {patterns}")

        # Initialize category stats if not exists
        if category not in self.stats["by_category"]:
            self.stats["by_category"][category] = {
                "files_deleted": 0,
                "bytes_freed": 0
            }

        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude_dir(os.path.join(root, d))]

            # Process each pattern
            for pattern in patterns:
                # Handle directory patterns (ending with /)
                if pattern.endswith('/') or pattern.endswith('\\'):
                    dir_pattern = pattern.rstrip('/\\')
                    for d in dirs:
                        if d == dir_pattern or glob.fnmatch.fnmatch(d, dir_pattern):
                            dir_path = os.path.join(root, d)
                            if self._is_file_expired(dir_path, category):
                                self._delete_directory(dir_path, category)

                # Handle file patterns
                else:
                    matches = glob.glob(os.path.join(root, pattern), recursive=False)
                    for match in matches:
                        if os.path.isfile(match) and self._is_file_expired(match, category):
                            self._delete_file(match, category)

            # Special handling for __pycache__ and other directory-based patterns
            if category == "cache":
                for d in dirs[:]:
                    if d == "__pycache__" or d.endswith("_cache"):
                        dir_path = os.path.join(root, d)
                        if self._is_file_expired(dir_path, category):
                            self._delete_directory(dir_path, category)
                            dirs.remove(d)  # Remove from dirs to avoid recursion

    def _delete_file(self, file_path: str, category: str) -> None:
        """Delete a file and update statistics."""
        try:
            self.stats["total_files_scanned"] += 1

            # Get file size before deletion
            file_size = os.path.getsize(file_path)

            # Log the deletion
            rel_path = os.path.relpath(file_path, self.root_dir)
            logger.info(f"Deleting file: {rel_path} ({self._format_size(file_size)})")

            # Delete the file (unless dry run)
            if not self.dry_run:
                os.remove(file_path)

                # Update statistics
                self.stats["files_deleted"] += 1
                self.stats["bytes_freed"] += file_size
                self.stats["by_category"][category]["files_deleted"] += 1
                self.stats["by_category"][category]["bytes_freed"] += file_size
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            self.stats["errors"] += 1

    def _delete_directory(self, dir_path: str, category: str) -> None:
        """Delete a directory and update statistics."""
        try:
            # Calculate directory size
            dir_size = 0
            file_count = 0
            for dirpath, _, filenames in os.walk(dir_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        dir_size += os.path.getsize(fp)
                        file_count += 1
                    except:
                        pass

            # Log the deletion
            rel_path = os.path.relpath(dir_path, self.root_dir)
            logger.info(f"Deleting directory: {rel_path} ({self._format_size(dir_size)}, {file_count} files)")

            # Delete the directory (unless dry run)
            if not self.dry_run:
                shutil.rmtree(dir_path, ignore_errors=True)

                # Update statistics
                self.stats["files_deleted"] += file_count
                self.stats["bytes_freed"] += dir_size
                self.stats["by_category"][category]["files_deleted"] += file_count
                self.stats["by_category"][category]["bytes_freed"] += dir_size
        except Exception as e:
            logger.error(f"Error deleting directory {dir_path}: {e}")
            self.stats["errors"] += 1

    def enforce_backup_retention(self) -> None:
        """Enforce backup retention policy by removing old backups."""
        logger.info("Enforcing backup retention policy")

        # Look for backup directories
        backup_dirs = []
        for root, dirs, _ in os.walk(self.root_dir):
            for d in dirs:
                if (d == "backups" or d.startswith("backup_") or 
                    d.endswith("_backup") or "backup" in d.lower()):
                    backup_dirs.append(os.path.join(root, d))

        # Process each backup directory
        for backup_dir in backup_dirs:
            self._process_backup_directory(backup_dir)

    def _process_backup_directory(self, backup_dir: str) -> None:
        """Process a backup directory to enforce retention policy."""
        logger.info(f"Processing backup directory: {backup_dir}")

        # Get all subdirectories (potential backup sets)
        try:
            backup_sets = []
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path):
                    # Try to extract date from directory name
                    try:
                        # Look for date patterns like YYYYMMDD or YYYY-MM-DD
                        date_str = None
                        for part in item.split('_'):
                            if len(part) == 8 and part.isdigit():  # YYYYMMDD
                                date_str = part
                                break
                            elif len(part) == 10 and part.count('-') == 2:  # YYYY-MM-DD
                                date_str = part
                                break

                        if date_str:
                            # Try to parse the date
                            if '-' in date_str:
                                backup_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                backup_date = datetime.datetime.strptime(date_str, '%Y%m%d')
                        else:
                            # Use modification time as fallback
                            backup_date = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))

                        backup_sets.append((item_path, backup_date))
                    except:
                        # If date extraction fails, use modification time
                        backup_date = datetime.datetime.fromtimestamp(os.path.getmtime(item_path))
                        backup_sets.append((item_path, backup_date))

            # Sort by date (oldest first)
            backup_sets.sort(key=lambda x: x[1])

            # Keep only the most recent backups according to retention policy
            max_age_days = self.retention_policies.get("backups", 90)
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)

            # Always keep at least 3 most recent backups regardless of age
            if len(backup_sets) > 3:
                for backup_path, backup_date in backup_sets[:-3]:
                    if backup_date < cutoff_date:
                        rel_path = os.path.relpath(backup_path, self.root_dir)
                        logger.info(f"Backup set {rel_path} from {backup_date.strftime('%Y-%m-%d')} is older than retention policy ({max_age_days} days)")
                        self._delete_directory(backup_path, "backups")
        except Exception as e:
            logger.error(f"Error processing backup directory {backup_dir}: {e}")
            self.stats["errors"] += 1

    def generate_report(self, output_file: Optional[str] = None) -> None:
        """Generate a report of cleanup operations."""
        logger.info("Generating cleanup report")

        # Create report content
        report = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "root_directory": self.root_dir,
            "dry_run": self.dry_run,
            "stats": self.stats,
            "retention_policies": self.retention_policies,
            "cleanup_patterns": self.cleanup_patterns
        }

        # Print summary to console
        logger.info(f"Cleanup Summary:")
        logger.info(f"  Total files scanned: {self.stats['total_files_scanned']}")
        logger.info(f"  Files deleted: {self.stats['files_deleted']}")
        logger.info(f"  Space freed: {self._format_size(self.stats['bytes_freed'])}")
        logger.info(f"  Errors: {self.stats['errors']}")

        # Print category details
        for category, stats in self.stats["by_category"].items():
            if stats["files_deleted"] > 0:
                logger.info(f"  {category}: {stats['files_deleted']} files, {self._format_size(stats['bytes_freed'])}")

        # Write report to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Report written to {output_file}")
            except Exception as e:
                logger.error(f"Error writing report to {output_file}: {e}")

    def run_cleanup(self, categories: Optional[List[str]] = None) -> None:
        """
        Run cleanup for specified categories or all categories.

        Args:
            categories: List of categories to clean, or None for all
        """
        logger.info(f"Starting cleanup process for {self.root_dir}")

        # Determine categories to clean
        if not categories:
            categories = list(self.cleanup_patterns.keys())

        # Clean each category
        for category in categories:
            if category in self.cleanup_patterns:
                self.clean_by_pattern(category)
            else:
                logger.warning(f"Unknown cleanup category: {category}")

        # Enforce backup retention
        if "backups" in categories or not categories:
            self.enforce_backup_retention()

        # Generate report
        report_file = os.path.join(self.root_dir, "cleanup_report.json")
        self.generate_report(report_file)

        logger.info("Cleanup process completed")


def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description="EGOS Scheduled Cleanup Script")
    parser.add_argument("--root", default=".", help="Root directory to clean")
    parser.add_argument("--log-file", help="File to log operations")
    parser.add_argument("--categories", nargs="+", help="Categories to clean (default: all)")
    parser.add_argument("--exclude-dirs", nargs="+", help="Additional directories to exclude")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually deleting")
    parser.add_argument("--verbose", action="store_true", help="Show detailed logs")
    parser.add_argument("--config", help="JSON configuration file")

    args = parser.parse_args()

    # Load configuration from file if specified
    retention_policies = DEFAULT_RETENTION_POLICIES.copy()
    cleanup_patterns = DEFAULT_CLEANUP_PATTERNS.copy()
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()

    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)

                if "retention_policies" in config:
                    retention_policies.update(config["retention_policies"])

                if "cleanup_patterns" in config:
                    cleanup_patterns.update(config["cleanup_patterns"])

                if "exclude_dirs" in config:
                    exclude_dirs.extend(config["exclude_dirs"])
        except Exception as e:
            logger.error(f"Error loading configuration from {args.config}: {e}")

    # Add any additional exclude directories
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)

    # Create cleanup manager
    cleanup_manager = EgosCleanupManager(
        root_dir=args.root,
        retention_policies=retention_policies,
        cleanup_patterns=cleanup_patterns,
        exclude_dirs=exclude_dirs,
        dry_run=args.dry_run,
        verbose=args.verbose,
        log_file=args.log_file
    )

    # Run cleanup
    cleanup_manager.run_cleanup(args.categories)


if __name__ == "__main__":
    main()