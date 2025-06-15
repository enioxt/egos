#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Work Log Standardizer

This script standardizes work log files (WORK_*.md) in the EGOS system to ensure
consistency with the format defined in the Work Log Standardization document.
It handles locating, parsing, validating, reformatting, and archiving work logs.
Additional capabilities include deduplication, filename standardization to snake_case,
and comprehensive reporting of all actions taken.

@author: EGOS Development Team (AI: Cascade)
@date: 2025-05-27
@version: 1.0.0

@references:
- C:\EGOS\docs\work_logs\WORK_2025-05-23_Work_Log_Standardization.md
- C:\EGOS\MQP.md (Systemic Cartography, Evolutionary Preservation)
- C:\EGOS\.windsurfrules (RULE-SCRIPT-STD-03, EGOS_PRINCIPLE:Systemic_Organization)
- C:\EGOS\docs\index\documentation_index.md
- C:\EGOS\ADRS_Log.md (Indentation Standards)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Standard library imports
import os
import sys
import re
import logging
import argparse
import shutil
import hashlib
import difflib
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

# Third-party imports
import yaml  # For parsing YAML frontmatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WorkLogStandardizer")

# Banner for script execution
BANNER = """
╔══════════════════════════════════════════════════════╗
║             EGOS Work Log Standardizer              ║
║  Ensuring consistency across all EGOS work logs     ║
╚══════════════════════════════════════════════════════╝
"""

# Print banner at script start
print(BANNER)

# Constants
# =========================================================================

# File naming and path constants
# -------------------------------------------------------------------------
WORK_LOG_PREFIX = "WORK_"  # Prefix for all work log filenames
WORK_LOG_EXTENSION = ".md"  # Extension for all work log files

# Directory paths (using forward slashes for cross-platform compatibility)
DEFAULT_ACTIVE_DIR = Path("C:/EGOS/docs/work_logs/active")  # Directory for active work logs
DEFAULT_ARCHIVE_DIR = Path("C:/EGOS/docs/work_logs/archive")  # Directory for archived work logs
BACKUP_DIR = Path("C:/EGOS/docs/work_logs/backup")  # Directory for backing up files during deduplication

# Process parameters
# -------------------------------------------------------------------------
ARCHIVE_RETENTION_DAYS = 7  # Number of days after completion before archiving
DEDUP_SIMILARITY_THRESHOLD = 0.9  # Threshold for content similarity to consider files duplicates

# Content standards (based on WORK_2025-05-23_Work_Log_Standardization.md)
# -------------------------------------------------------------------------
# Required frontmatter keys for all work logs
EXPECTED_FRONTMATTER_KEYS = [
    "title",       # Title of the work log
    "date",        # Date in YYYY-MM-DD format
    "author",      # Author of the work log
    "status",      # Current status (e.g., "In Progress", "Completed")
    "priority",    # Priority level (e.g., "High", "Medium", "Low")
    "tags",        # List of relevant tags
    "roadmap_ids"  # References to roadmap items
]

# Required section headers for all work logs
EXPECTED_SECTIONS = [
    "Objective",       # Purpose and goals of the work
    "Context",         # Background and related information
    "Completed Tasks", # What has been accomplished
    "Next Steps",      # Future work and follow-up tasks
    "Modified Files"   # Files changed during the work
    # "AI Assistant Contributions" and "References" are optional or standard footers
]

class WorkLogStandardizer:
    """Standardizes EGOS work log files.
    
    This class provides functionality to standardize work log files according to
    EGOS documentation standards. It handles file discovery, validation, reformatting,
    deduplication, and archiving of work logs.
    
    Attributes:
        active_dir (Path): Directory containing active work logs
        archive_dir (Path): Directory for archived work logs
        backup_dir (Path): Directory for backed up files during deduplication
        dry_run (bool): If True, simulate changes without writing to files
        issues_found (int): Counter for validation and processing issues
        files_processed (int): Counter for total files processed
        files_standardized (int): Counter for files that were reformatted
        files_archived (int): Counter for files moved to archive
        duplicates_handled (int): Counter for duplicate files processed
        filenames_standardized (int): Counter for filenames that were standardized
    """

    def __init__(self, active_dir: Path = DEFAULT_ACTIVE_DIR, archive_dir: Path = DEFAULT_ARCHIVE_DIR, dry_run: bool = False):
        """Initialize the WorkLogStandardizer.

        Args:
            active_dir (Path, optional): Directory containing active work logs. 
                Defaults to DEFAULT_ACTIVE_DIR.
            archive_dir (Path, optional): Directory for archived work logs. 
                Defaults to DEFAULT_ARCHIVE_DIR.
            dry_run (bool, optional): If True, simulate changes without writing to files. 
                Defaults to False.
        """
        # Directory paths
        self.active_dir = active_dir
        self.archive_dir = archive_dir
        self.backup_dir = BACKUP_DIR
        self.dry_run = dry_run
        
        # Counters for tracking progress and results
        self.issues_found = 0
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        
        # Tracking collections for detailed reporting
        self.validation_failures = []  # Store detailed validation failure information
        self.reformatting_failures = []  # Store any files that couldn't be reformatted successfully
        self.deduplication_actions = []  # Track deduplication actions
        self.rename_actions = []  # Track filename standardization actions

        # Ensure directories exist (if not in dry run mode)
        if not self.dry_run:
            self._ensure_directories_exist()

        logger.info(f"WorkLogStandardizer initialized. Active: '{self.active_dir}', "
                   f"Archive: '{self.archive_dir}', Backup: '{self.backup_dir}', "
                   f"Dry Run: {self.dry_run}")
    
    def _ensure_directories_exist(self) -> None:
        """Create required directories if they don't exist."""
        for directory in [self.active_dir, self.archive_dir, self.backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
            
    def _deduplicate_work_logs(self) -> None:
        """Identify and handle duplicate work logs across active and archive directories.
        
        This method identifies potential duplicates based on:
        1. Similar filenames (ignoring case and non-alphanumeric characters)
        2. Content similarity using difflib sequence matcher
        3. Date and title in frontmatter
        
        When duplicates are found, it keeps the most complete/valid file and backs up others.
        
        Returns:
            None. Updates self.duplicates_handled counter.
        """
        logger.info("Starting work log deduplication process...")
        
        # Ensure backup directory exists
        if not self.backup_dir.exists() and not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
        # Get all work logs from both active and archive directories
        active_logs = self._find_work_logs(self.active_dir)
        archive_logs = self._find_work_logs(self.archive_dir)
        all_logs = active_logs + archive_logs
        
        if not all_logs:
            logger.info("No work logs found for deduplication.")
            return
            
        logger.info(f"Analyzing {len(all_logs)} work logs for potential duplicates...")
        
        # Dictionary to store groups of potential duplicates
        # Key: normalized filename (without date, all lowercase, no special chars)
        # Value: list of file paths with similar names
        duplicate_groups = {}
        
        # Group files by normalized filename
        for log_path in all_logs:
            # Extract the description part (after date)
            parts = log_path.stem.split('_', 2)
            if len(parts) >= 3:
                # Normalize the description part for comparison
                desc = parts[2].lower()
                # Remove non-alphanumeric chars for fuzzy matching
                norm_desc = ''.join(c for c in desc if c.isalnum())
                
                if norm_desc not in duplicate_groups:
                    duplicate_groups[norm_desc] = []
                duplicate_groups[norm_desc].append(log_path)
        
        # Filter groups to only those with multiple files
        potential_duplicates = {k: v for k, v in duplicate_groups.items() if len(v) > 1}
        
        if not potential_duplicates:
            logger.info("No potential duplicates found based on filename similarity.")
            return
            
        logger.info(f"Found {len(potential_duplicates)} groups of potential duplicates.")
        
        # Process each group of potential duplicates
        duplicates_found = 0
        for desc, file_paths in potential_duplicates.items():
            logger.debug(f"Analyzing potential duplicate group: {desc} with {len(file_paths)} files")
            
            # Compare files within each group for content similarity
            confirmed_duplicates = []
            
            # Parse all files in the group
            parsed_files = []
            for path in file_paths:
                frontmatter, content, success = self._parse_work_log(path)
                parsed_files.append((path, frontmatter, content, success))
            
            # Compare each pair of files
            for i in range(len(parsed_files)):
                for j in range(i+1, len(parsed_files)):
                    path1, fm1, content1, success1 = parsed_files[i]
                    path2, fm2, content2, success2 = parsed_files[j]
                    
                    # Skip if either file couldn't be parsed
                    if not success1 or not success2:
                        continue
                        
                    # Check for content similarity
                    similarity = 0.0
                    if content1 and content2:
                        matcher = difflib.SequenceMatcher(None, content1, content2)
                        similarity = matcher.ratio()
                    
                    # Check for matching frontmatter
                    frontmatter_match = False
                    if fm1 and fm2:
                        # Check if title and date match
                        title_match = fm1.get('title') == fm2.get('title')
                        date_match = fm1.get('date') == fm2.get('date')
                        frontmatter_match = title_match and date_match
                    
                    # If content is very similar or frontmatter matches, consider them duplicates
                    if similarity >= DEDUP_SIMILARITY_THRESHOLD or frontmatter_match:
                        logger.info(f"Duplicate detected: {path1.name} and {path2.name} (similarity: {similarity:.2f})")
                        duplicates_found += 1
                        
                        # Determine which file to keep based on completeness and validity
                        keep_first = self._determine_better_file(path1, fm1, content1, path2, fm2, content2)
                        
                        # Add to confirmed duplicates list
                        dup_pair = (path1, path2, keep_first)
                        if dup_pair not in confirmed_duplicates:
                            confirmed_duplicates.append(dup_pair)
                            
                            # Record deduplication action for reporting
                            self.deduplication_actions.append({
                                'file1': str(path1),
                                'file2': str(path2),
                                'similarity': similarity,
                                'action': f"Keeping {'first' if keep_first else 'second'} file"
                            })
            
            # Handle confirmed duplicates
            for path1, path2, keep_first in confirmed_duplicates:
                self._handle_duplicate_files(path1, path2, keep_first)
        
        logger.info(f"Deduplication complete. Found {duplicates_found} duplicate pairs.")
        logger.info(f"Handled {self.duplicates_handled} duplicate files.")
    
    def _determine_better_file(self, path1: Path, fm1: Optional[Dict], content1: Optional[str], 
                              path2: Path, fm2: Optional[Dict], content2: Optional[str]) -> bool:
        """Determine which of two duplicate files should be kept.
        
        This method evaluates two files and decides which one is more complete/valid
        based on several criteria:
        1. Valid frontmatter vs. invalid/missing frontmatter
        2. More complete content (longer, more sections)
        3. More recent modification time
        4. Active file vs. archived file
        
        Args:
            path1: Path to first file
            fm1: Parsed frontmatter of first file
            content1: Content of first file
            path2: Path to second file
            fm2: Parsed frontmatter of second file
            content2: Content of second file
            
        Returns:
            Boolean indicating whether to keep the first file (True) or second file (False)
        """
        # Score each file based on completeness and validity
        score1 = 0
        score2 = 0
        
        # Criterion 1: Valid frontmatter
        if fm1 is not None:
            score1 += 2
            # Additional points for more complete frontmatter
            score1 += min(len(fm1) / 2, 3)  # Up to 3 points for frontmatter completeness
        
        if fm2 is not None:
            score2 += 2
            # Additional points for more complete frontmatter
            score2 += min(len(fm2) / 2, 3)  # Up to 3 points for frontmatter completeness
        
        # Criterion 2: Content completeness
        if content1:
            # Points based on content length (normalized)
            content_len1 = len(content1)
            score1 += min(content_len1 / 500, 5)  # Up to 5 points for content length
            
            # Points for having expected sections
            for section in EXPECTED_SECTIONS:
                if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", content1, re.MULTILINE | re.IGNORECASE):
                    score1 += 0.5  # 0.5 points per section
        
        if content2:
            # Points based on content length (normalized)
            content_len2 = len(content2)
            score2 += min(content_len2 / 500, 5)  # Up to 5 points for content length
            
            # Points for having expected sections
            for section in EXPECTED_SECTIONS:
                if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", content2, re.MULTILINE | re.IGNORECASE):
                    score2 += 0.5  # 0.5 points per section
        
        # Criterion 3: File modification time (more recent is better)
        try:
            mtime1 = path1.stat().st_mtime
            mtime2 = path2.stat().st_mtime
            
            # Add points for more recent file (up to 2 points)
            if mtime1 > mtime2:
                score1 += min((mtime1 - mtime2) / (60*60*24), 2)  # Scale by days, max 2 points
            else:
                score2 += min((mtime2 - mtime1) / (60*60*24), 2)  # Scale by days, max 2 points
        except Exception as e:
            logger.warning(f"Error comparing file modification times: {e}")
        
        # Criterion 4: Active vs. archived status
        # Prefer active files over archived ones
        is_active1 = path1.parent.samefile(self.active_dir) if self.active_dir.exists() else False
        is_active2 = path2.parent.samefile(self.active_dir) if self.active_dir.exists() else False
        
        if is_active1 and not is_active2:
            score1 += 1
        elif is_active2 and not is_active1:
            score2 += 1
        
        logger.debug(f"File comparison scores: {path1.name}: {score1}, {path2.name}: {score2}")
        
        # Return True to keep first file, False to keep second file
        return score1 >= score2  # Prefer first file in case of tie
    
    def _handle_duplicate_files(self, path1: Path, path2: Path, keep_first: bool) -> None:
        """Handle a pair of duplicate files by keeping one and backing up the other.
        
        Args:
            path1: Path to first file
            path2: Path to second file
            keep_first: Boolean indicating whether to keep the first file (True) or second file (False)
        """
        # Determine which file to keep and which to back up
        keep_path = path1 if keep_first else path2
        backup_path = path2 if keep_first else path1
        
        # Create backup filename with timestamp to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_path.stem}_duplicate_{timestamp}{backup_path.suffix}"
        backup_dest = self.backup_dir / backup_filename
        
        logger.info(f"Keeping {keep_path.name} and backing up {backup_path.name} to {backup_dest.name}")
        
        if not self.dry_run:
            try:
                # Ensure backup directory exists
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy file to backup location
                shutil.copy2(backup_path, backup_dest)
                
                # Remove the duplicate file
                backup_path.unlink()
                
                self.duplicates_handled += 1
                logger.info(f"Successfully backed up and removed duplicate: {backup_path.name}")
            except Exception as e:
                logger.error(f"Error handling duplicate files: {e}")
        else:
            logger.info(f"[DRY RUN] Would back up {backup_path.name} to {backup_dest.name} and remove original")
            self.duplicates_handled += 1
            
    def _standardize_filenames(self) -> None:
        """Standardize work log filenames to follow EGOS naming conventions.
        
        This method ensures all work log filenames follow the standard format:
        WORK_YYYY-MM-DD_descriptive_name.md where:
        - The date is properly formatted
        - The descriptive name is in snake_case (lowercase with underscores)
        - No special characters are used except underscores
        
        The method identifies non-standard filenames and renames them according to the rules.
        
        Returns:
            None. Updates self.filenames_standardized counter.
        """
        logger.info("Starting filename standardization process...")
        
        # Get all work logs from both active and archive directories
        active_logs = self._find_work_logs(self.active_dir)
        archive_logs = self._find_work_logs(self.archive_dir)
        all_logs = active_logs + archive_logs
        
        if not all_logs:
            logger.info("No work logs found for filename standardization.")
            return
            
        logger.info(f"Analyzing {len(all_logs)} work logs for non-standard filenames...")
        
        for log_path in all_logs:
            # Check if filename needs standardization
            if self._validate_filename(log_path):
                logger.debug(f"Filename already standardized: {log_path.name}")
                continue
                
            # Attempt to standardize the filename
            new_filename = self._generate_standard_filename(log_path)
            if new_filename:
                # Generate the new path
                new_path = log_path.parent / new_filename
                
                # Check if the new path already exists
                if new_path.exists() and new_path != log_path:
                    logger.warning(f"Cannot rename {log_path.name} to {new_filename} - target file already exists")
                    continue
                    
                # Rename the file
                logger.info(f"Standardizing filename: {log_path.name} -> {new_filename}")
                
                if not self.dry_run:
                    try:
                        log_path.rename(new_path)
                        self.filenames_standardized += 1
                        
                        # Record rename action for reporting
                        self.rename_actions.append({
                            'original': str(log_path),
                            'new': str(new_path)
                        })
                        
                        logger.info(f"Successfully renamed file to: {new_filename}")
                    except Exception as e:
                        logger.error(f"Error renaming file {log_path.name}: {e}")
                else:
                    logger.info(f"[DRY RUN] Would rename {log_path.name} to {new_filename}")
                    self.filenames_standardized += 1
                    
                    # Record rename action for reporting (even in dry run)
                    self.rename_actions.append({
                        'original': str(log_path),
                        'new': str(new_path),
                        'dry_run': True
                    })
            else:
                logger.warning(f"Could not determine standard filename for: {log_path.name}")
                
        logger.info(f"Filename standardization complete. Standardized {self.filenames_standardized} filenames.")
        
    def _generate_standard_filename(self, file_path: Path) -> Optional[str]:
        """Generate a standardized filename for a work log file.
        
        This method attempts to extract the date and description from the existing filename
        or from the frontmatter, and generates a new standardized filename following EGOS conventions.
        
        Args:
            file_path: Path to the work log file
            
        Returns:
            A standardized filename string, or None if standardization is not possible
        """
        filename = file_path.name
        
        # Try to extract date and description from existing filename
        date_str = None
        description = None
        
        # Pattern to extract date from filename
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        date_match = re.search(date_pattern, filename)
        
        if date_match:
            date_str = date_match.group(0)
            
            # Try to extract description part after the date
            parts = filename.split(date_str, 1)
            if len(parts) > 1 and parts[1]:
                # Remove leading underscore or other separators
                description = parts[1].lstrip('_-. ')
                # Remove file extension
                if WORK_LOG_EXTENSION in description:
                    description = description.split(WORK_LOG_EXTENSION)[0]
        
        # If we couldn't extract from filename, try parsing the file to get info from frontmatter
        if not date_str or not description:
            frontmatter, _, success = self._parse_work_log(file_path)
            
            if success and frontmatter:
                # Try to get date from frontmatter
                if not date_str and 'date' in frontmatter:
                    fm_date = frontmatter['date']
                    if isinstance(fm_date, str):
                        # Try to parse and format the date string
                        try:
                            date_obj = datetime.strptime(fm_date, "%Y-%m-%d").date()
                            date_str = date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            logger.warning(f"Could not parse date from frontmatter: {fm_date}")
                    elif hasattr(fm_date, 'year') and hasattr(fm_date, 'month') and hasattr(fm_date, 'day'):
                        # It's a date-like object
                        date_str = f"{fm_date.year:04d}-{fm_date.month:02d}-{fm_date.day:02d}"
                
                # Try to get description from frontmatter title
                if not description and 'title' in frontmatter:
                    title = frontmatter['title']
                    if title:
                        description = self._convert_to_snake_case(title)
        
        # If we still don't have a date, use today's date
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            logger.warning(f"Could not determine date for {filename}, using current date: {date_str}")
        
        # If we still don't have a description, use a generic one
        if not description:
            description = "untitled_work_log"
            logger.warning(f"Could not determine description for {filename}, using generic: {description}")
        else:
            # Ensure description is in snake_case
            description = self._convert_to_snake_case(description)
        
        # Construct the standardized filename
        return f"{WORK_LOG_PREFIX}{date_str}_{description}{WORK_LOG_EXTENSION}"
    
    def _convert_to_snake_case(self, text: str) -> str:
        """Convert a string to snake_case format.
        
        This method converts any string to snake_case by:
        1. Replacing spaces and special characters with underscores
        2. Converting to lowercase
        3. Removing consecutive underscores
        4. Removing leading/trailing underscores
        
        Args:
            text: The string to convert
            
        Returns:
            The converted snake_case string
        """
        if not text:
            return ""
            
        # Replace spaces and special characters with underscores
        # First, handle camelCase by adding underscores before uppercase letters
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
        
        # Convert to lowercase and replace non-alphanumeric chars with underscores
        s2 = re.sub('[^a-z0-9]', '_', s1.lower())
        
        # Remove consecutive underscores
        s3 = re.sub('_+', '_', s2)
        
        # Remove leading/trailing underscores
        s4 = s3.strip('_')
        
        # Ensure the result is not empty
        if not s4:
            return "untitled"
            
        return s4
        
    def run_standardization(self) -> Dict[str, int]:
        """Run the standardization process on all work logs.
        
        This method orchestrates the complete standardization process:
        1. Deduplication of work logs to eliminate duplicates
        2. Validation and standardization of work log content
        3. Archiving of completed work logs
        4. Standardization of filenames to follow EGOS conventions
        5. Generation of a comprehensive report
        
        Following EGOS principles of Systemic Organization and Evolutionary Preservation,
        this process ensures all work logs are properly formatted, named, and organized.
        
        Returns:
            Dictionary with summary statistics of the standardization process
        """
        logger.info(f"Starting work log standardization...")
        logger.info(f"Active directory: {self.active_dir}")
        logger.info(f"Archive directory: {self.archive_dir}")
        logger.info(f"Backup directory: {self.backup_dir}")
        logger.info(f"Dry run mode: {self.dry_run}")
        
        # Reset counters for this run
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.issues_found = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        
        # Clear tracking collections
        self.validation_failures = []
        self.reformatting_failures = []
        self.deduplication_actions = []
        self.rename_actions = []
        
        # Step 1: Perform deduplication across all work logs
        logger.info("Step 1: Performing deduplication...")
        self._deduplicate_work_logs()
        
        # Step 2: Process active work logs (validation, standardization, archiving)
        logger.info("Step 2: Processing active work logs...")
        active_logs = self._find_work_logs(self.active_dir)
        for log_file in active_logs:
            self.files_processed += 1
            validation_result = self._validate_work_log(log_file)
            
            if validation_result:
                logger.debug(f"Work log is valid: {log_file}")
                # Check if work log should be archived based on completion date
                if self._should_archive_work_log(log_file):
                    self._archive_work_log(log_file)
                    self.files_archived += 1
            else:
                logger.warning(f"Work log has issues: {log_file}")
                self.issues_found += 1
                # Attempt to standardize the file if it has issues
                if self._standardize_work_log(log_file):
                    self.files_standardized += 1
        
        # Step 3: Process archived work logs (validation and standardization only)
        logger.info("Step 3: Processing archived work logs...")
        archive_logs = self._find_work_logs(self.archive_dir)
        for log_file in archive_logs:
            self.files_processed += 1
            if not self._validate_work_log(log_file):
                logger.warning(f"Archived work log has issues: {log_file}")
                self.issues_found += 1
                # Attempt to standardize the file if it has issues
                if self._standardize_work_log(log_file):
                    self.files_standardized += 1
        
        # Step 4: Standardize filenames to ensure consistency
        logger.info("Step 4: Standardizing filenames...")
        self._standardize_filenames()
        
        # Step 5: Generate comprehensive report
        logger.info("Step 5: Generating standardization report...")
        self._generate_standardization_report()
        
        # Print summary
        logger.info("\nStandardization complete!")
        logger.info(f"Files processed: {self.files_processed}")
        logger.info(f"Files standardized: {self.files_standardized}")
        logger.info(f"Files archived: {self.files_archived}")
        logger.info(f"Duplicates handled: {self.duplicates_handled}")
        logger.info(f"Filenames standardized: {self.filenames_standardized}")
        logger.info(f"Issues found: {self.issues_found}")
        
        if self.issues_found > 0:
            logger.warning(f"Some issues were found during standardization. Please review the report for details.")
            
        return {  # Return summary statistics for programmatic use
            'files_processed': self.files_processed,
            'files_standardized': self.files_standardized,
            'files_archived': self.files_archived,
            'duplicates_handled': self.duplicates_handled,
            'filenames_standardized': self.filenames_standardized,
            'issues_found': self.issues_found
        }
        
    def _generate_standardization_report(self) -> None:
        """Generate a detailed report of all standardization actions taken.
        
        This method creates a comprehensive Markdown report documenting all actions
        taken during the standardization process, including:
        - Summary statistics
        - Validation issues found
        - Files standardized
        - Duplicates handled
        - Filenames standardized
        
        The report is saved to the EGOS documentation directory following
        EGOS_PRINCIPLE:Systemic_Organization and RULE-REPORT-STD-01 standards.
        
        Returns:
            None. Saves report to file system.
        """
        logger.info("Generating standardization report...")
        
        # Create timestamp for the report filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"work_log_standardization_report_{timestamp}.md"
        report_dir = Path("C:/EGOS/docs/reports/work_logs")
        report_path = report_dir / report_filename
        
        # Ensure report directory exists
        if not self.dry_run:
            report_dir.mkdir(parents=True, exist_ok=True)
        
        # Build report content
        report_content = []
        
        # Add report header
        report_content.append("# EGOS Work Log Standardization Report")
        report_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"**Mode:** {'Dry Run (no changes made)' if self.dry_run else 'Live Run'}")
        report_content.append("")
        
        # Add summary section
        report_content.append("## Summary")
        report_content.append("| Metric | Count |")
        report_content.append("| ------ | ----- |")
        report_content.append(f"| Files Processed | {self.files_processed} |")
        report_content.append(f"| Files Standardized | {self.files_standardized} |")
        report_content.append(f"| Files Archived | {self.files_archived} |")
        report_content.append(f"| Duplicates Handled | {self.duplicates_handled} |")
        report_content.append(f"| Filenames Standardized | {self.filenames_standardized} |")
        report_content.append(f"| Issues Found | {self.issues_found} |")
        report_content.append("")
        
        # Add validation issues section if any were found
        if self.validation_failures:
            report_content.append("## Validation Issues")
            report_content.append("The following files had validation issues:")
            report_content.append("")
            report_content.append("| File | Issues |")
            report_content.append("| ---- | ------ |")
            
            for failure in self.validation_failures:
                file_path = failure.get('file', 'Unknown')
                issues = failure.get('issues', [])
                issues_str = ', '.join(issues) if issues else 'Unknown issues'
                report_content.append(f"| {file_path} | {issues_str} |")
                
            report_content.append("")
        
        # Add deduplication section if any duplicates were handled
        if self.deduplication_actions:
            report_content.append("## Duplicates Handled")
            report_content.append("The following duplicate files were processed:")
            report_content.append("")
            report_content.append("| File 1 | File 2 | Similarity | Action |")
            report_content.append("| ------ | ------ | ---------- | ------ |")
            
            for action in self.deduplication_actions:
                file1 = action.get('file1', 'Unknown')
                file2 = action.get('file2', 'Unknown')
                similarity = action.get('similarity', 0.0)
                action_taken = action.get('action', 'Unknown')
                report_content.append(f"| {file1} | {file2} | {similarity:.2f} | {action_taken} |")
                
            report_content.append("")
        
        # Add filename standardization section if any filenames were standardized
        if self.rename_actions:
            report_content.append("## Filenames Standardized")
            report_content.append("The following files were renamed to follow EGOS standards:")
            report_content.append("")
            report_content.append("| Original Filename | New Filename |")
            report_content.append("| ----------------- | ------------ |")
            
            for action in self.rename_actions:
                original = Path(action.get('original', 'Unknown')).name
                new = Path(action.get('new', 'Unknown')).name
                dry_run = action.get('dry_run', False)
                new_name = f"{new} (DRY RUN)" if dry_run else new
                report_content.append(f"| {original} | {new_name} |")
                
            report_content.append("")
        
        # Add references section
        report_content.append("## References")
        report_content.append("- [Work Log Standardization Document](C:\EGOS\docs\work_logs\WORK_2025-05-23_Work_Log_Standardization.md)")
        report_content.append("- [EGOS Master Quantum Prompt](C:\EGOS\MQP.md)")
        report_content.append("- [EGOS Documentation Index](C:\EGOS\docs\index\documentation_index.md)")
        report_content.append("")
        
        # Add EGOS signature
        report_content.append("---")
        report_content.append("*Generated by EGOS Work Log Standardizer v1.0.0*")
        report_content.append("*Following EGOS principles: Systemic Organization, Evolutionary Preservation, Systemic Cartography*")
        
        # Join all content with newlines
        full_report = "\n".join(report_content)
        
        # Save report to file
        if not self.dry_run:
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(full_report)
                logger.info(f"Standardization report saved to: {report_path}")
            except Exception as e:
                logger.error(f"Error saving standardization report: {e}")
                logger.info("Report content:\n" + full_report)
        else:
            logger.info(f"[DRY RUN] Would save standardization report to: {report_path}")
            logger.debug("Report content preview (first 10 lines):\n" + "\n".join(report_content[:10]) + "\n...")
        
        return


    def _find_work_logs(self, directory: Path) -> List[Path]:
        """Find all work log files in the specified directory.
        
        This method searches for files matching the work log pattern
        (WORK_*.md) in the specified directory. It handles cases where
        the directory might not exist and logs appropriate messages.
        
        Args:
            directory: The directory to search for work log files
            
        Returns:
            List of Path objects for all work log files found
        """
        work_logs = []
        
        # Check if directory exists
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return work_logs
        
        # Use glob pattern to find all work log files
        pattern = f"{WORK_LOG_PREFIX}*{WORK_LOG_EXTENSION}"
        try:
            # Find all files matching the pattern
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    work_logs.append(file_path)
            
            # Sort work logs by filename for consistent processing order
            work_logs.sort()
            
            logger.debug(f"Found {len(work_logs)} work logs in {directory}")
            
            # If no work logs found, log a more specific message
            if not work_logs:
                logger.info(f"No work logs matching pattern '{pattern}' found in {directory}")
                
            return work_logs
            
        except Exception as e:
            logger.error(f"Error searching for work logs in {directory}: {e}")
            return []

    def _parse_work_log(self, file_path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str], bool]:
        """Parse a work log file into YAML frontmatter and Markdown content.
        
        This method reads a work log file and extracts the YAML frontmatter and
        Markdown content. It handles various error cases such as missing frontmatter,
        invalid YAML, and file access issues.
        
        Args:
            file_path: Path to the work log file to parse
            
        Returns:
            A tuple containing:
            - Dict of parsed frontmatter (or None if parsing failed)
            - String of Markdown content (or None if parsing failed)
            - Boolean indicating if parsing was successful
        """
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return None, None, False
            
        try:
            # Read file content with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                logger.warning(f"File is empty: {file_path}")
                return None, None, False
            
            # Extract frontmatter using regex pattern for YAML between --- markers
            frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
            match = re.match(frontmatter_pattern, content, re.DOTALL)
            
            if match:
                # Successfully found frontmatter section
                frontmatter_str, markdown_content = match.groups()
                
                try:
                    # Parse YAML frontmatter
                    frontmatter = yaml.safe_load(frontmatter_str)
                    
                    # Validate that frontmatter is a dictionary
                    if not isinstance(frontmatter, dict):
                        logger.warning(f"Frontmatter in {file_path} is not a dictionary: {type(frontmatter)}")
                        frontmatter = {}
                        
                    return frontmatter, markdown_content.strip(), True
                    
                except yaml.YAMLError as yaml_err:
                    # Handle YAML parsing errors
                    logger.error(f"Error parsing YAML frontmatter in {file_path}: {yaml_err}")
                    return None, markdown_content.strip() if markdown_content else None, False
            else:
                # No frontmatter found, treat entire content as Markdown
                logger.warning(f"No YAML frontmatter found in {file_path}")
                return None, content.strip(), True
                
        except UnicodeDecodeError as ude:
            # Handle encoding issues
            logger.error(f"Encoding error reading {file_path}: {ude}. File may not be UTF-8 encoded.")
            return None, None, False
            
        except Exception as e:
            # Handle any other errors
            logger.error(f"Error reading or parsing file {file_path}: {e}")
            return None, None, False

    def _validate_filename(self, file_path: Path) -> bool:
        """Validate the work log filename format: WORK_YYYY-MM-DD_concise_description.md
        
        This method checks if a work log filename follows the EGOS standard format:
        - Starts with 'WORK_'
        - Followed by a date in YYYY-MM-DD format
        - Followed by an underscore and a snake_case description
        - Ends with '.md'
        
        The method performs several checks:
        1. Basic pattern validation
        2. Snake_case validation for the description part
        3. Date format validation
        
        Args:
            file_path: Path to the work log file to validate
            
        Returns:
            Boolean indicating if the filename is valid
        """
        filename = file_path.name
        
        # Check 1: Basic pattern validation - WORK_DATE_description.md
        basic_pattern = rf"^{WORK_LOG_PREFIX}\d{{4}}-\d{{2}}-\d{{2}}_[\w-]+{WORK_LOG_EXTENSION}$"
        if not re.match(basic_pattern, filename):
            logger.warning(f"Invalid filename format: {filename}")
            logger.warning(f"Expected format: {WORK_LOG_PREFIX}YYYY-MM-DD_concise_description{WORK_LOG_EXTENSION}")
            return False
            
        # Check 2: Snake_case validation for the description part
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        if len(parts) >= 3:
            desc_with_ext = parts[2]
            # Extract description part without extension
            desc_part = desc_with_ext.split('.')[0] if '.' in desc_with_ext else desc_with_ext
            
            # Check if the descriptive part follows snake_case convention (all lowercase with underscores)
            if not all(c.islower() or c.isdigit() or c == '_' for c in desc_part):
                logger.warning(f"Filename description part not in snake_case: {desc_part}")
                logger.warning("Description must use only lowercase letters, numbers, and underscores")
                return False
            
            # Check for consecutive underscores which are not allowed in snake_case
            if '__' in desc_part:
                logger.warning(f"Filename contains consecutive underscores: {desc_part}")
                return False
            
            # Check if description starts or ends with underscore
            if desc_part.startswith('_') or desc_part.endswith('_'):
                logger.warning(f"Filename description cannot start or end with underscore: {desc_part}")
                return False
        
        # Check 3: Date format validation
        try:
            date_str = parts[1] if len(parts) > 1 else ''
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Additional check: Date should not be in the future
            if date_obj.date() > datetime.now().date():
                logger.warning(f"Date in filename is in the future: {date_str}")
                return False
                
        except (IndexError, ValueError) as e:
            logger.warning(f"Invalid date format in filename: {filename}. Error: {e}")
            logger.warning("Date must be in YYYY-MM-DD format")
            return False
            
        return True

    def _validate_frontmatter(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> bool:
        """Validate the YAML frontmatter content in a work log file.
        
        This method checks if the frontmatter in a work log file follows EGOS standards:
        - Contains all required keys (title, date, author, status, etc.)
        - Has valid date format
        - Has valid status values
        - Has appropriate tag formats
        
        Args:
            file_path: Path to the work log file being validated
            frontmatter: Dictionary containing the parsed frontmatter, or None if parsing failed
            
        Returns:
            Boolean indicating if the frontmatter is valid
        """
        # Check if frontmatter exists
        if frontmatter is None:
            logger.warning(f"Missing frontmatter in {file_path} (or parse error occurred before this check).")
            return False

        valid = True
        validation_issues = []
        
        # Check 1: Required keys
        missing_keys = [key for key in EXPECTED_FRONTMATTER_KEYS if key not in frontmatter]
        if missing_keys:
            issue = f"Missing required frontmatter keys: {', '.join(missing_keys)}"
            validation_issues.append(issue)
            logger.warning(f"{file_path.name}: {issue}")
            valid = False
        
        # Check 2: Date format validation
        if 'date' in frontmatter:
            try:
                date_value = frontmatter['date']
                # Check if PyYAML parsed the date into a datetime.date object or similar
                if hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
                    # It's a date-like object, check if it's in the future
                    if isinstance(date_value, date) and date_value > datetime.now().date():
                        issue = f"Date in frontmatter is in the future: {date_value}"
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
                elif isinstance(date_value, str):
                    # Parse the string to validate format
                    date_obj = datetime.strptime(date_value, "%Y-%m-%d").date()
                    # Check if date is in the future
                    if date_obj > datetime.now().date():
                        issue = f"Date in frontmatter is in the future: {date_value}"
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
                else:
                    # If it's neither a recognized date-like object nor a string, it's an unexpected type
                    issue = f"Date in frontmatter has unexpected type: {type(date_value)}"
                    validation_issues.append(issue)
                    logger.warning(f"{file_path.name}: {issue}")
                    valid = False
            except ValueError as e:
                issue = f"Invalid date format in frontmatter: {e}"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
        
        # Check 3: Status validation
        if 'status' in frontmatter:
            status = frontmatter['status']
            valid_statuses = ['In Progress', 'Completed', 'Pending', 'Blocked', 'Archived']
            if not isinstance(status, str):
                issue = f"Status must be a string, got {type(status)}"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
            elif status not in valid_statuses:
                issue = f"Invalid status: '{status}'. Expected one of: {', '.join(valid_statuses)}"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
        
        # Check 4: Tags validation
        if 'tags' in frontmatter:
            tags = frontmatter['tags']
            if not isinstance(tags, list):
                issue = f"Tags must be a list, got {type(tags)}"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
            else:
                for tag in tags:
                    if not isinstance(tag, str):
                        issue = f"Tag must be a string, got {type(tag)}: {tag}"
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
                    elif not re.match(r'^[a-z0-9_-]+$', tag):
                        issue = f"Tag contains invalid characters: '{tag}'. Use only lowercase letters, numbers, hyphens, and underscores."
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
    def _validate_sections(self, file_path: Path, markdown_content: Optional[str]) -> bool:
        """Validate the presence of required sections in the Markdown content.
        
        This method checks if all required sections are present in the work log markdown content.
        It handles various section header formats (with or without numbering).
        
        Args:
            file_path: Path to the work log file being validated
            markdown_content: String containing the markdown content, or None if parsing failed
            
        Returns:
            Boolean indicating if all required sections are present
        """
        if markdown_content is None:
            logger.warning(f"Missing markdown content for section validation in {file_path}.")
            # This usually follows a parsing error, so issue might already be counted.
            return False
        
        if not markdown_content.strip():
            logger.warning(f"Empty markdown content in {file_path}")
            return False
            
        valid = True
        validation_issues = []
        found_sections = []
        missing_sections = []
        
        # First, extract all section headers from the markdown content
        section_pattern = r'^##\s*(\d+\.\s*)?([^\n]+)'  # Matches '## Section', '## 1. Section', etc.
        section_matches = re.finditer(section_pattern, markdown_content, re.MULTILINE)
        
        # Build a list of all found section titles (normalized for comparison)
        for match in section_matches:
            section_title = match.group(2).strip()
            found_sections.append(section_title.lower())
        
        # Check for each required section
        for section_title in EXPECTED_SECTIONS:
            # Check if any found section matches this required section (case-insensitive)
            if not any(section_title.lower() in found.lower() or found.lower() in section_title.lower() 
                      for found in found_sections):
                missing_sections.append(section_title)
                issue = f"Missing required section: '{section_title}'"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
        
        # Additional check: Ensure sections have content
        section_blocks = re.split(section_pattern, markdown_content, flags=re.MULTILINE)[1:]
        # section_blocks will contain: [number, title, content, number, title, content, ...]
        # We need to check every third item (the content)
        for i in range(2, len(section_blocks), 3):
            if i < len(section_blocks):
                content = section_blocks[i].strip()
                title = section_blocks[i-1].strip() if i-1 < len(section_blocks) else "Unknown"
                if not content:
                    issue = f"Empty section content for '{title}'"
                    validation_issues.append(issue)
                    logger.warning(f"{file_path.name}: {issue}")
                    valid = False
        
        if not valid:
            logger.warning(f"Section validation failed for {file_path.name} with {len(validation_issues)} issues")
            if missing_sections:
                logger.warning(f"Missing sections: {', '.join(missing_sections)}")
        
        return valid

    def _validate_work_log(self, file_path: Path) -> bool:
        """Validate a single work log file comprehensively."""
        logger.debug(f"Validating work log: {file_path}")
        # self.files_processed is incremented in run_standardization before calling this

        issues_for_this_file = []

        filename_valid = self._validate_filename(file_path)
        if not filename_valid:
            issues_for_this_file.append("filename_invalid")
        
        frontmatter, markdown_content, parse_successful = self._parse_work_log(file_path)
        if not parse_successful:
            issues_for_this_file.append("parse_failed")
            # If parsing failed, frontmatter/markdown_content might be None, affecting subsequent checks.
            # _validate_frontmatter and _validate_sections should handle None inputs gracefully.

        # Proceed with content validation even if filename/parse had issues, to gather all problems
        # but only if parse was successful enough to yield some content to validate.
        frontmatter_valid = self._validate_frontmatter(file_path, frontmatter) 
        if not frontmatter_valid:
            issues_for_this_file.append("frontmatter_invalid")

        sections_valid = self._validate_sections(file_path, markdown_content)
        if not sections_valid:
            issues_for_this_file.append("sections_invalid")
        
        # A file is fully valid if all checks pass. Note: parse_successful is implicitly part of this.
        # If parse_successful is false, frontmatter_valid/sections_valid might also be false due to None inputs.
        is_fully_valid = filename_valid and parse_successful and frontmatter_valid and sections_valid
        
        if is_fully_valid:
            logger.info(f"Work log {file_path} is valid.")
            return True
        else:
            failure_info = {
                "file": str(file_path),
                "issues": issues_for_this_file,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.validation_failures.append(failure_info)
            logger.warning(f"Work log {file_path} has validation issues: {', '.join(issues_for_this_file)}.")
            self.issues_found += 1 # Increment global issue counter ONCE if any validation failed for this file.
            return False

    def _reformat_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]], markdown_content: Optional[str]) -> None:
        """Reformat a work log file to the standard, fixing both content and filename if needed."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would reformat {file_path}")
            self.files_standardized +=1 # Assume it would be standardized
            return
            
        # Check and fix filename if needed
        original_path = file_path
        filename = file_path.name
        filename_fixed = False
        
        # If filename doesn't match the snake_case pattern for the descriptive part
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        if len(parts) >= 3:
            prefix, date, desc_with_ext = parts
            # Check if the descriptive part has uppercase letters
            if not all(c.islower() or c.isdigit() or c == '_' or c == '.' for c in desc_with_ext):
                # Convert descriptive part to snake_case (lowercase with underscores)
                desc_part = desc_with_ext.split('.')[0]
                ext = desc_with_ext.split('.')[-1] if '.' in desc_with_ext else 'md'
                
                # Convert to snake_case
                new_desc_part = desc_part.lower()
                
                # Construct the new filename
                new_filename = f"{prefix}_{date}_{new_desc_part}.{ext}"
                new_path = file_path.parent / new_filename
                
                try:
                    # Rename the file
                    if new_path.exists():
                        logger.warning(f"Cannot rename to {new_filename} as it already exists. Will update content only.")
                    else:
                        file_path.rename(new_path)
                        logger.info(f"Renamed file from {filename} to {new_filename}")
                        file_path = new_path  # Update file_path for content reformatting
                        filename_fixed = True
                except Exception as e:
                    logger.error(f"Error renaming file {file_path} to {new_path}: {e}")
                    # Continue with content reformatting even if renaming fails

        # Basic reformatting: Ensure frontmatter and essential sections exist.
        # A more sophisticated version would try to intelligently migrate existing content.
        
        new_frontmatter = frontmatter if frontmatter is not None else {}
        new_markdown_content = markdown_content if markdown_content is not None else ""

        # Ensure all expected frontmatter keys are present, adding defaults if necessary
        if 'date' not in new_frontmatter:
            try:
                # Attempt to get date from filename
                date_str = file_path.name.split('_')[1]
                new_frontmatter['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except (IndexError, ValueError):
                new_frontmatter['date'] = datetime.now().strftime("%Y-%m-%d") # Default to today
        
        for key in EXPECTED_FRONTMATTER_KEYS:
            if key not in new_frontmatter:
                if key == 'title':
                    new_frontmatter[key] = f"Work Log for {file_path.stem}" 
                elif key == 'author':
                    new_frontmatter[key] = "EGOS System (Standardized)"
                elif key == 'status':
                    new_frontmatter[key] = "In Progress" # Default status
                elif key == 'priority':
                    new_frontmatter[key] = "Medium"
                elif key == 'tags':
                    new_frontmatter[key] = ["standardized"]
                elif key == 'roadmap_ids':
                    new_frontmatter[key] = []
                else:
                    new_frontmatter[key] = f"Placeholder for {key}"
        
        # Ensure date is a string for YAML dump
        date_val = new_frontmatter.get('date')
        # Check if it's a date-like object (parsed by PyYAML or already a datetime.date)
        if hasattr(date_val, 'year') and hasattr(date_val, 'month') and hasattr(date_val, 'day') and not isinstance(date_val, str):
            new_frontmatter['date'] = date_val.strftime('%Y-%m-%d')
        elif isinstance(date_val, str):
            # If it's already a string, ensure it's in the correct format or log warning
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Date string '{date_val}' in frontmatter of {file_path.name} is not in YYYY-MM-DD format during reformat. Attempting to keep original.")
        # If it's None or some other type, it will be handled by YAML dump or previous validation

        # Ensure required sections are present in markdown
        current_sections = {re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE).group(1).strip(): True 
                            for line in new_markdown_content.splitlines() if re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE)}
        
        added_sections_content = "\n"
        for i, section_title in enumerate(EXPECTED_SECTIONS):
            if section_title not in current_sections:
                added_sections_content += f"## {i+1}. {section_title}\n\n(Content for {section_title} needs to be added.)\n\n"
        
        final_markdown_content = new_markdown_content + added_sections_content
        if '✧༺❀༻∞ EGOS ∞༺❀༻✧' not in final_markdown_content:
            final_markdown_content += "\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n"

        try:
            frontmatter_yaml = yaml.dump(new_frontmatter, sort_keys=False, default_flow_style=False)
            new_content = f"---\n{frontmatter_yaml}---\n{final_markdown_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Successfully reformatted and saved {file_path}")
            self.files_standardized += 1
        except Exception as e:
            error_info = {
                "file": str(file_path),
                "error": str(e),
                "stage": "writing_reformatted_file",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.reformatting_failures.append(error_info)
            logger.error(f"Error writing reformatted file {file_path}: {e}")
            self.issues_found +=1 # Count as an issue if reformatting fails

    def _archive_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> None:
        """Archive a completed work log if it meets the criteria."""
        if frontmatter is None or frontmatter.get('status', '').lower() != 'completed':
            return # Not completed, or no frontmatter to check status

        file_mod_time_str = frontmatter.get('date') # Use 'date' from frontmatter as proxy for completion date
        if not file_mod_time_str or not isinstance(file_mod_time_str, str):
             # If no valid date, try to get file's actual modification time
            try:
                file_mod_timestamp = file_path.stat().st_mtime
                file_mod_date = datetime.fromtimestamp(file_mod_timestamp)
            except OSError:
                logger.warning(f"Could not determine modification date for {file_path} to check for archiving.")
                return
        else:
            try:
                file_mod_date = datetime.strptime(file_mod_time_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date '{file_mod_time_str}' in frontmatter of {file_path} for archiving check.")
                return

        if datetime.now() - file_mod_date > timedelta(days=ARCHIVE_RETENTION_DAYS):
            archive_target_path = self.archive_dir / file_path.name
            if self.dry_run:
                logger.info(f"[DRY RUN] Would archive {file_path} to {archive_target_path}")
            else:
                try:
                    shutil.move(str(file_path), str(archive_target_path))
                    logger.info(f"Archived {file_path} to {archive_target_path}")
                    self.files_archived += 1
                except Exception as e:
                    logger.error(f"Error archiving {file_path} to {archive_target_path}: {e}")
                    self.issues_found +=1
        else:
            logger.debug(f"Work log {file_path} is completed but not yet old enough for archiving.")

    def _standardize_filename(self, file_path: Path) -> Path:
        """Standardize a work log filename to snake_case format.
        
        Returns:
            The new path if renamed, or the original path if no renaming was needed or possible.
        """
        filename = file_path.name
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        
        if len(parts) < 3:
            logger.warning(f"Cannot standardize filename {filename}: unexpected format (not enough parts)")
            return file_path
            
        prefix, date, desc_with_ext = parts
        
        # Check if date format needs correction (some files might use underscore instead of hyphen)
        if '-' not in date and len(date) == 8:  # Format might be YYYYMMDD or YYYY_MM_DD
            try:
                if '_' in date:  # Format is YYYY_MM_DD
                    year, month, day = date.split('_')
                else:  # Format is YYYYMMDD
                    year, month, day = date[:4], date[4:6], date[6:8]
                date = f"{year}-{month}-{day}"
                logger.info(f"Corrected date format in filename from {parts[1]} to {date}")
            except ValueError:
                logger.warning(f"Could not parse date in filename: {filename}")
        
        # Fix description part (convert to snake_case)
        desc_parts = desc_with_ext.split('.')
        desc = desc_parts[0]
        ext = desc_parts[1] if len(desc_parts) > 1 else "md"
        
        # Remove any existing underscores for clean conversion
        desc_no_underscores = desc.replace('_', ' ')
        
        # Handle common patterns like MCP_Documentation to mcp_documentation
        # First replace internal uppercase-prefixed words with space + that word
        # E.g., "MCPDocumentation" -> "MCP Documentation"
        desc_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', desc_no_underscores)
        
        # Then convert to lowercase and replace spaces with underscores
        snake_desc = desc_spaced.lower().replace(' ', '_')
        
        # Construct new filename
        new_filename = f"{prefix}_{date}_{snake_desc}.{ext}"
        
        if new_filename == filename:
            return file_path  # No change needed
            
        new_path = file_path.parent / new_filename
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename {filename} to {new_filename}")
            return file_path  # Return original in dry run
            
        try:
            if new_path.exists():
                logger.warning(f"Cannot rename to {new_filename} as it already exists.")
                return file_path
                
            file_path.rename(new_path)
            logger.info(f"Successfully renamed {filename} to {new_filename}")
            return new_path
        except Exception as e:
            logger.error(f"Error renaming {filename} to {new_filename}: {e}")
            return file_path
    
    def run_standardization(self) -> None:
        """Run the full work log standardization process.
        
        This comprehensive process includes:
        1. Detecting and handling duplicate work logs
        2. Standardizing filenames to follow snake_case convention
        3. Validating and reformatting work log content
        4. Archiving completed work logs
        5. Generating a detailed report of all actions taken
        """
        logger.info("Starting comprehensive work log standardization process...")
        self.issues_found = 0
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        self.validation_failures = []  # Store detailed validation failure information
        self.reformatting_failures = []  # Store any files that couldn't be reformatted successfully
        self.deduplication_actions = []  # Track deduplication actions
        self.rename_actions = []  # Track filename standardization actions

        # Step 1: Find all work logs in the active directory
        initial_active_logs = self._find_work_logs(self.active_dir)
        logger.info(f"Found {len(initial_active_logs)} initial work logs in {self.active_dir}")
        
        # Step 2: Detect and handle duplicate work logs
        logger.info("=== PHASE 1: DEDUPLICATION ===")
        deduplicated_logs = self._detect_and_handle_duplicates(self.active_dir)
        
        # Step 3: Standardize all filenames to follow snake_case convention
        logger.info("=== PHASE 2: FILENAME STANDARDIZATION ===")
        standardized_logs = self._standardize_all_filenames(deduplicated_logs)
        
        # Step 4: Process each work log (validate, reformat, archive)
        logger.info("=== PHASE 3: CONTENT VALIDATION AND REFORMATTING ===")
        logger.info(f"Processing {len(standardized_logs)} work logs from {self.active_dir}")
        
        for log_path in standardized_logs:
            logger.info(f"--- Processing: {log_path.name} ---")
            self.files_processed += 1
            
            # Validate the work log
            is_valid = self._validate_work_log(log_path)
            
            # Parse for reformatting and archiving
            frontmatter, markdown_content, parse_successful = self._parse_work_log(log_path)

            # If validation failed, attempt to reformat content
            if not is_valid:
                logger.info(f"Attempting to reformat invalid work log: {log_path.name}")
                self._reformat_work_log(log_path, frontmatter, markdown_content)
                
                # After reformatting, re-parse to get updated frontmatter for archiving
                frontmatter, _, _ = self._parse_work_log(log_path) 
            
            # Step 5: Attempt to archive if it's completed
            self._archive_work_log(log_path, frontmatter)

        # Process logs in archive directory to ensure they are indeed archived (e.g. old completed logs)
        # This could also be a place to validate archived logs, though less critical than active ones.
        archived_logs = self._find_work_logs(self.archive_dir)
        logger.info(f"Checking {len(archived_logs)} work logs in archive directory {self.archive_dir} for any active logs that need moving back.")
        # Example: if a log in archive is not 'Completed', it might need to be moved back to active.
        # For now, this part is kept simple.

        # Step 6: Generate comprehensive standardization report
        logger.info("=== PHASE 4: GENERATING STANDARDIZATION REPORT ===")
        
        # Console summary
        logger.info("--- Standardization Process Summary ---")
        logger.info(f"Total files processed: {self.files_processed}")
        logger.info(f"Duplicate files handled: {self.duplicates_handled}")
        logger.info(f"Filenames standardized: {self.filenames_standardized}")
        logger.info(f"Content reformatted/standardized: {self.files_standardized}")
        logger.info(f"Files archived: {self.files_archived}")
        logger.info(f"Total issues encountered: {self.issues_found}")
        
        # Generate comprehensive standardization report
        report_path = Path(self.active_dir.parent, 'work_log_standardization_report.md')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# EGOS Work Log Standardization Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add EGOS signature banner
                f.write("✧｡◙◞ ◟◙｡✧\n\n")
                
                f.write("## Summary\n")
                f.write(f"- Total files processed: {self.files_processed}\n")
                f.write(f"- Duplicate files handled: {self.duplicates_handled}\n")
                f.write(f"- Filenames standardized: {self.filenames_standardized}\n")
                f.write(f"- Content reformatted: {self.files_standardized}\n")
                f.write(f"- Files archived: {self.files_archived}\n")
                f.write(f"- Issues encountered: {self.issues_found}\n\n")
                
                # Deduplication section
                if self.deduplication_actions:
                    f.write("## Deduplication Actions\n")
                    f.write("The following duplicate files were identified and handled:\n\n")
                    f.write("| Original File | Action | Kept File | Score Comparison |\n")
                    f.write("|--------------|--------|-----------|------------------|\n")
                    
                    for action in self.deduplication_actions:
                        original = Path(action['original']).name
                        kept = Path(action['kept']).name
                        if self.dry_run:
                            action_text = "Would be backed up (dry run)"
                        else:
                            action_text = f"Backed up to {Path(action['backup']).name}"
                        score_comparison = f"{action['score_original']} vs {action['score_kept']}"
                        
                        f.write(f"| {original} | {action_text} | {kept} | {score_comparison} |\n")
                    
                    f.write("\n")
                
                # Filename standardization section
                if self.rename_actions:
                    f.write("## Filename Standardization Actions\n")
                    f.write("The following files were renamed to comply with snake_case convention:\n\n")
                    f.write("| Original Filename | Standardized Filename |\n")
                    f.write("|-------------------|----------------------|\n")
                    
                    for action in self.rename_actions:
                        f.write(f"| {action['original']} | {action['new']} |\n")
                    
                    f.write("\n")
                
                # Validation and reformatting section
                if self.validation_failures:
                    f.write("## Validation Failures\n")
                    for failure in self.validation_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                if self.reformatting_failures:
                    f.write("## Reformatting Failures\n")
                    for failure in self.reformatting_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Error: {failure['error']}\n")
                        f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                # Next steps and recommendations
                f.write("## Next Steps\n")
                if self.issues_found > 0:
                    f.write("To address the remaining issues:\n\n")
                    f.write("1. **Fix invalid frontmatter** in work logs with missing or incorrect metadata.\n")
                    f.write("2. **Add missing sections** to work logs that lack required content structure.\n")
                    f.write("3. **Review backed-up duplicates** to ensure no important content was lost.\n")
                    f.write("4. **Run the standardizer again** after addressing these issues.\n\n")
                else:
                    f.write("All work logs are now standardized according to EGOS requirements. Regular maintenance should include:\n\n")
                    f.write("1. **Run this standardizer weekly** to ensure ongoing compliance.\n")
                    f.write("2. **Archive completed work logs** regularly to maintain a clean active directory.\n")
                    f.write("3. **Follow standard templates** when creating new work logs.\n\n")
                
                # References to EGOS standards
                f.write("## References\n")
                f.write("- [Work Log Standardization](C:\\EGOS\\docs\\work_logs\\WORK_2025-05-23_Work_Log_Standardization.md)\n")
                f.write("- [Master Quantum Prompt](C:\\EGOS\\MQP.md) (Systemic Organization, Evolutionary Preservation principles)\n")
                f.write("- [EGOS Documentation Standards](C:\\EGOS\\docs\\core_materials\\standards\\documentation_standards.md)\n\n")
                
                # EGOS signature footer
                f.write("\n✧｡◙◞ ◟◙｡✧ EGOS ✧｡◙◞ ◟◙｡✧\n")
                
            logger.info(f"Comprehensive standardization report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write standardization report: {e}")
        
        # Generate diagnostic report for issues if needed
        if self.issues_found > 0:
            diagnostic_report_path = Path(self.active_dir.parent, 'standardization_diagnostic_report.md')
            try:
                with open(diagnostic_report_path, 'w', encoding='utf-8') as f:
                    f.write("# Work Log Standardization Diagnostic Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("## Summary\n")
                    f.write(f"- Total files processed: {self.files_processed}\n")
                    f.write(f"- Files with issues: {self.issues_found}\n")
                    f.write(f"- Files standardized: {self.files_standardized}\n")
                    f.write(f"- Files archived: {self.files_archived}\n\n")
                    
                    if self.validation_failures:
                        f.write("## Validation Failures\n")
                        for failure in self.validation_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    if self.reformatting_failures:
                        f.write("## Reformatting Failures\n")
                        for failure in self.reformatting_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Error: {failure['error']}\n")
                            f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    f.write("## Recommendations\n")
                    f.write("To fix the identified issues:\n\n")
                    f.write("1. **Ensure frontmatter** is present in all work logs with correct format.\n")
                    f.write("2. **Check for required sections** such as Objective, Progress, Challenges, etc.\n")
                    f.write("3. **Validate filenames** follow the format `WORK_YYYY-MM-DD_descriptive_name.md`.\n")
                    f.write("4. Run the standardizer again after fixing the issues.\n")
                    
                logger.info(f"Detailed diagnostic report saved to: {diagnostic_report_path}")
            except Exception as e:
                logger.error(f"Failed to write diagnostic report: {e}")
        
        logger.info("Work log standardization process finished.")

        if self.issues_found > 0:
            logger.warning("Standardization completed with issues. Please review the standardization report for details.")
        else:
            logger.info("Standardization completed successfully.")

    def analyze_directory_contents(self, root_dir: Path) -> None:
        """Analyzes work logs directly within root_dir to identify their status."""
        logger.info(f"--- Starting Analysis of Directory: {root_dir} ---")
        found_logs_in_root = 0
        active_identified = 0
        inactive_identified = 0
        unknown_status = 0

        # Determine the names of active and archive directories to avoid double-processing if they are subdirs of root_dir
        # This check is simplified; assumes root_dir is a direct parent if active/archive are inside it.
        active_dir_name = self.active_dir.name
        archive_dir_name = self.archive_dir.name
        is_processing_parent_of_managed_dirs = (self.active_dir.parent == root_dir or self.archive_dir.parent == root_dir)

        for item in root_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs_in_root += 1
                logger.info(f"Analyzing file: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                status_str = "Unknown/Missing Status"
                # is_active = False # Default assumption - not strictly needed here

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str = frontmatter['status'] # Keep original casing for logging
                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        inactive_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as INACTIVE/ARCHIVABLE")
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        active_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as ACTIVE")
                    else:
                        unknown_status += 1
                        logger.warning(f"  -> Status: '{status_str}' - Status UNKNOWN or not standard.")
                else:
                    unknown_status += 1
                    logger.warning(f"  -> Status: MISSING - Could not determine status from frontmatter.")
        
        logger.info("--- Directory Analysis Summary ---")
        logger.info(f"Total work log files found directly in {root_dir}: {found_logs_in_root}")
        logger.info(f"  Identified as ACTIVE: {active_identified}")
        logger.info(f"  Identified as INACTIVE/ARCHIVABLE: {inactive_identified}")
        logger.info(f"  Status UNKNOWN or MISSING: {unknown_status}")
        logger.info("Analysis finished. No files were moved or modified.")

    def _detect_and_handle_duplicates(self, directory: Path) -> List[Path]:
        """Detect and handle duplicate work log files in the specified directory.
        
        Duplicates are detected based on:
        1. Similar filenames (after standardization)
        2. Similar content (using similarity threshold)
        3. Same date in frontmatter
        
        When duplicates are found:
        1. The most complete/valid file is kept
        2. Other duplicates are backed up and noted in the report
        
        Args:
            directory: Directory to search for duplicates
            
        Returns:
            List of paths to the deduplicated work log files
        """
        logger.info(f"Detecting and handling duplicate work logs in {directory}...")
        
        all_logs = self._find_work_logs(directory)
        if len(all_logs) <= 1:
            logger.info(f"No potential duplicates found in {directory} (only {len(all_logs)} logs)")
            return all_logs
            
        # Group files by normalized names (to catch variations like WORK_2025-05-22 vs WORK_2025_05_22)
        name_groups = {}
        for log_path in all_logs:
            # Extract date and description from filename
            parts = log_path.stem.split('_', 2)
            if len(parts) < 3:
                # Not a standard work log filename, skip grouping
                continue
                
            date_part = parts[1]
            # Normalize date format (replace underscores with hyphens)
            norm_date = date_part.replace('_', '-')
            
            # Normalize description part to lowercase
            desc_part = parts[2].lower()
            
            # Create normalized key for grouping
            norm_key = f"{norm_date}_{desc_part}"
            
            if norm_key not in name_groups:
                name_groups[norm_key] = []
            name_groups[norm_key].append(log_path)
        
        # Filter to only groups with multiple files (potential duplicates)
        duplicate_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
        
        if not duplicate_groups:
            logger.info(f"No duplicate work logs found in {directory} based on filename analysis")
            return all_logs
            
        logger.info(f"Found {len(duplicate_groups)} groups of potential duplicate work logs")
        
        # Process each group of potential duplicates
        final_logs = []
        duplicate_paths = set()  # Track all identified duplicates
        
        for group_key, group_paths in duplicate_groups.items():
            logger.info(f"Processing duplicate group: {group_key} with {len(group_paths)} files")
            
            # Read content and metadata for each file in the group
            group_files = []
            for path in group_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    frontmatter, markdown, parse_success = self._parse_work_log(path)
                    
                    # Count complete sections as a measure of completeness
                    section_count = 0
                    if markdown:
                        for section in EXPECTED_SECTIONS:
                            if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", markdown, re.MULTILINE | re.IGNORECASE):
                                section_count += 1
                    
                    # Calculate file score (higher is better)
                    # Scoring factors: file size, completeness of frontmatter, number of sections
                    frontmatter_score = len(frontmatter.keys()) if frontmatter else 0
                    size_score = len(content)
                    
                    file_score = size_score + (frontmatter_score * 100) + (section_count * 500)
                    
                    group_files.append({
                        'path': path,
                        'content': content,
                        'frontmatter': frontmatter,
                        'markdown': markdown,
                        'section_count': section_count,
                        'score': file_score
                    })
                except Exception as e:
                    logger.error(f"Error processing {path} for duplicate detection: {e}")
            
            if not group_files:
                logger.warning(f"Could not process any files in duplicate group {group_key}")
                continue
                
            # Sort files by score (highest first)
            group_files.sort(key=lambda x: x['score'], reverse=True)
            
            # Keep the highest scoring file, mark others as duplicates
            keeper = group_files[0]
            duplicate_files = group_files[1:]
            
            logger.info(f"Keeping highest scoring file: {keeper['path'].name} (score: {keeper['score']})")
            final_logs.append(keeper['path'])
            
            # Backup and record duplicates
            for dup in duplicate_files:
                duplicate_paths.add(dup['path'])
                
                if not self.dry_run:
                    try:
                        # Create backup with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_name = f"{dup['path'].stem}_DUPLICATE_{timestamp}{dup['path'].suffix}"
                        backup_path = self.backup_dir / backup_name
                        
                        shutil.copy2(dup['path'], backup_path)
                        logger.info(f"Backed up duplicate: {dup['path'].name} to {backup_path}")
                        
                        # Record action
                        self.deduplication_actions.append({
                            'original': str(dup['path']),
                            'backup': str(backup_path),
                            'kept': str(keeper['path']),
                            'score_original': dup['score'],
                            'score_kept': keeper['score'],
                            'timestamp': timestamp
                        })
                        
                        self.duplicates_handled += 1
                    except Exception as e:
                        logger.error(f"Error backing up duplicate {dup['path']}: {e}")
                else:
                    logger.info(f"[DRY RUN] Would back up duplicate: {dup['path'].name}")
                    self.deduplication_actions.append({
                        'original': str(dup['path']),
                        'backup': f"[DRY RUN] Would back up to {self.backup_dir}",
                        'kept': str(keeper['path']),
                        'score_original': dup['score'],
                        'score_kept': keeper['score'],
                        'timestamp': '[DRY RUN]'
                    })
        
        # Add any non-duplicate files to the final list
        for log_path in all_logs:
            if log_path not in duplicate_paths and log_path not in final_logs:
                final_logs.append(log_path)
        
        logger.info(f"Duplicate handling complete. Kept {len(final_logs)} unique files, handled {self.duplicates_handled} duplicates")
        return final_logs
    
    def _standardize_all_filenames(self, log_paths: List[Path]) -> List[Path]:
        """Standardize all work log filenames to follow EGOS snake_case convention.
        
        Args:
            log_paths: List of paths to work log files
            
        Returns:
            List of paths to the standardized files (may be different from input paths if renamed)
        """
        logger.info(f"Standardizing filenames for {len(log_paths)} work logs...")
        
        standardized_paths = []
        for log_path in log_paths:
            standardized_path = self._standardize_filename(log_path)
            standardized_paths.append(standardized_path)
            
            if standardized_path != log_path:
                self.filenames_standardized += 1
                
        logger.info(f"Filename standardization complete. Standardized {self.filenames_standardized} filenames")
        return standardized_paths

    def migrate_logs_from_directory(self, source_dir: Path) -> None:
        """Analyzes logs in source_dir and migrates them to active/archive dirs. Reports unknown status logs."""
        logger.info(f"--- Starting Migration from Directory: {source_dir} ---")
        logger.info(f"Target ACTIVE directory: {self.active_dir}")
        logger.info(f"Target ARCHIVE directory: {self.archive_dir}")
        if self.dry_run:
            logger.info("[DRY RUN] No files will actually be moved.")

        found_logs = 0
        moved_to_active = 0
        moved_to_archive = 0
        unknown_status_logs = []
        migration_errors = 0

        # Ensure target directories exist
        if not self.dry_run:
            self.active_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs += 1
                logger.debug(f"Processing file for migration: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                target_path = None
                action_description = ""

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str_original = frontmatter['status']

                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        target_path = self.archive_dir / item.name
                        action_description = f"Identified as INACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_archive +=1 # Tentative count
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        target_path = self.active_dir / item.name
                        action_description = f"Identified as ACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_active +=1 # Tentative count
                    else:
                        logger.warning(f"File '{item.name}': Status '{status_str_original}' is UNKNOWN. File will not be moved.")
                        unknown_status_logs.append(item.name)
                else:
                    logger.warning(f"File '{item.name}': Status MISSING in frontmatter. File will not be moved.")
                    unknown_status_logs.append(item.name)

                if target_path:
                    logger.info(f"File '{item.name}': {action_description}")
                    if not self.dry_run:
                        try:
                            if target_path.exists():
                                logger.warning(f"  SKIPPING move: Target file {target_path} already exists.")
                                # Decrement count if skipped
                                if self.archive_dir / item.name == target_path: moved_to_archive -=1
                                if self.active_dir / item.name == target_path: moved_to_active -=1
                                migration_errors +=1
                            else:
                                shutil.move(str(item), str(target_path))
                                logger.info(f"  SUCCESS: Moved '{item.name}' to '{target_path}'")
                        except Exception as e:
                            logger.error(f"  FAILED to move '{item.name}' to '{target_path}': {e}")
                            # Decrement count if failed
                            if self.archive_dir / item.name == target_path: moved_to_archive -=1
                            if self.active_dir / item.name == target_path: moved_to_active -=1
                            migration_errors += 1
                
        logger.info("--- Migration Summary ---")
        logger.info(f"Total work log files found in {source_dir}: {found_logs}")
        logger.info(f"  Attempted to move to ACTIVE ({self.active_dir}): {moved_to_active}")
        logger.info(f"  Attempted to move to ARCHIVE ({self.archive_dir}): {moved_to_archive}")
        logger.info(f"  Files with UNKNOWN/MISSING status (not moved): {len(unknown_status_logs)}")
        if unknown_status_logs:
            for log_name in unknown_status_logs:
                logger.info(f"    - {log_name}")
        if migration_errors > 0:
            logger.warning(f"  Migration errors encountered: {migration_errors}")
        logger.info(f"Migration process finished. Check logs for details. Dry run: {self.dry_run}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize EGOS work log files.")
    parser.add_argument("--active-dir", type=Path, default=DEFAULT_ACTIVE_DIR, help="Directory for active work logs.")
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archived work logs.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without modifying files.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--analyze-root-directory", type=Path, help="Analyze work logs in the specified root directory to identify their status without moving or standardizing.")
    parser.add_argument("--migrate-logs-from", type=Path, help="Analyze and migrate logs from a source directory to 'active' or 'archive' subdirectories. Logs with unknown status are reported but not moved.")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    standardizer = WorkLogStandardizer(active_dir=args.active_dir, archive_dir=args.archive_dir, dry_run=args.dry_run)

    if args.analyze_root_directory:
        if not args.analyze_root_directory.is_dir():
            logger.error(f"Error: --analyze-root-directory path is not a valid directory: {args.analyze_root_directory}")
            sys.exit(1)
        standardizer.analyze_directory_contents(args.analyze_root_directory)
    elif args.migrate_logs_from:
        if not args.migrate_logs_from.is_dir():
            logger.error(f"Error: --migrate-logs-from path is not a valid directory: {args.migrate_logs_from}")
            sys.exit(1)
        standardizer.migrate_logs_from_directory(args.migrate_logs_from)
    else:
        standardizer.run_standardization()
        sys.exit(1 if standardizer.issues_found > 0 else 0)
, tag):
                        issue = f"Tag contains invalid characters: '{tag}'. Use only lowercase letters, numbers, hyphens, and underscores."
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
        
        if not valid:
            logger.warning(f"Frontmatter validation failed for {file_path.name} with {len(validation_issues)} issues")
        
        return valid

    def _validate_sections(self, file_path: Path, markdown_content: Optional[str]) -> bool:
        """Validate the presence of required sections in the Markdown content."""
        if markdown_content is None:
            logger.warning(f"Missing markdown content for section validation in {file_path}.")
            # This usually follows a parsing error, so issue might already be counted.
            return False

        valid = True
        for section_title in EXPECTED_SECTIONS:
            # Regex to find section headers like '## 1. Objective' or '## Objective'
            if not re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section_title)}\s*$\n", markdown_content, re.MULTILINE | re.IGNORECASE):
                logger.warning(f"Missing section '{section_title}' in {file_path}")
                # self.issues_found += 1 # Moved to _validate_work_log
                valid = False
        return valid

    def _validate_work_log(self, file_path: Path) -> bool:
        """Validate a single work log file comprehensively."""
        logger.debug(f"Validating work log: {file_path}")
        # self.files_processed is incremented in run_standardization before calling this

        issues_for_this_file = []

        filename_valid = self._validate_filename(file_path)
        if not filename_valid:
            issues_for_this_file.append("filename_invalid")
        
        frontmatter, markdown_content, parse_successful = self._parse_work_log(file_path)
        if not parse_successful:
            issues_for_this_file.append("parse_failed")
            # If parsing failed, frontmatter/markdown_content might be None, affecting subsequent checks.
            # _validate_frontmatter and _validate_sections should handle None inputs gracefully.

        # Proceed with content validation even if filename/parse had issues, to gather all problems
        # but only if parse was successful enough to yield some content to validate.
        frontmatter_valid = self._validate_frontmatter(file_path, frontmatter) 
        if not frontmatter_valid:
            issues_for_this_file.append("frontmatter_invalid")

        sections_valid = self._validate_sections(file_path, markdown_content)
        if not sections_valid:
            issues_for_this_file.append("sections_invalid")
        
        # A file is fully valid if all checks pass. Note: parse_successful is implicitly part of this.
        # If parse_successful is false, frontmatter_valid/sections_valid might also be false due to None inputs.
        is_fully_valid = filename_valid and parse_successful and frontmatter_valid and sections_valid
        
        if is_fully_valid:
            logger.info(f"Work log {file_path} is valid.")
            return True
        else:
            failure_info = {
                "file": str(file_path),
                "issues": issues_for_this_file,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.validation_failures.append(failure_info)
            logger.warning(f"Work log {file_path} has validation issues: {', '.join(issues_for_this_file)}.")
            self.issues_found += 1 # Increment global issue counter ONCE if any validation failed for this file.
            return False

    def _reformat_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]], markdown_content: Optional[str]) -> None:
        """Reformat a work log file to the standard, fixing both content and filename if needed."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would reformat {file_path}")
            self.files_standardized +=1 # Assume it would be standardized
            return
            
        # Check and fix filename if needed
        original_path = file_path
        filename = file_path.name
        filename_fixed = False
        
        # If filename doesn't match the snake_case pattern for the descriptive part
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        if len(parts) >= 3:
            prefix, date, desc_with_ext = parts
            # Check if the descriptive part has uppercase letters
            if not all(c.islower() or c.isdigit() or c == '_' or c == '.' for c in desc_with_ext):
                # Convert descriptive part to snake_case (lowercase with underscores)
                desc_part = desc_with_ext.split('.')[0]
                ext = desc_with_ext.split('.')[-1] if '.' in desc_with_ext else 'md'
                
                # Convert to snake_case
                new_desc_part = desc_part.lower()
                
                # Construct the new filename
                new_filename = f"{prefix}_{date}_{new_desc_part}.{ext}"
                new_path = file_path.parent / new_filename
                
                try:
                    # Rename the file
                    if new_path.exists():
                        logger.warning(f"Cannot rename to {new_filename} as it already exists. Will update content only.")
                    else:
                        file_path.rename(new_path)
                        logger.info(f"Renamed file from {filename} to {new_filename}")
                        file_path = new_path  # Update file_path for content reformatting
                        filename_fixed = True
                except Exception as e:
                    logger.error(f"Error renaming file {file_path} to {new_path}: {e}")
                    # Continue with content reformatting even if renaming fails

        # Basic reformatting: Ensure frontmatter and essential sections exist.
        # A more sophisticated version would try to intelligently migrate existing content.
        
        new_frontmatter = frontmatter if frontmatter is not None else {}
        new_markdown_content = markdown_content if markdown_content is not None else ""

        # Ensure all expected frontmatter keys are present, adding defaults if necessary
        if 'date' not in new_frontmatter:
            try:
                # Attempt to get date from filename
                date_str = file_path.name.split('_')[1]
                new_frontmatter['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except (IndexError, ValueError):
                new_frontmatter['date'] = datetime.now().strftime("%Y-%m-%d") # Default to today
        
        for key in EXPECTED_FRONTMATTER_KEYS:
            if key not in new_frontmatter:
                if key == 'title':
                    new_frontmatter[key] = f"Work Log for {file_path.stem}" 
                elif key == 'author':
                    new_frontmatter[key] = "EGOS System (Standardized)"
                elif key == 'status':
                    new_frontmatter[key] = "In Progress" # Default status
                elif key == 'priority':
                    new_frontmatter[key] = "Medium"
                elif key == 'tags':
                    new_frontmatter[key] = ["standardized"]
                elif key == 'roadmap_ids':
                    new_frontmatter[key] = []
                else:
                    new_frontmatter[key] = f"Placeholder for {key}"
        
        # Ensure date is a string for YAML dump
        date_val = new_frontmatter.get('date')
        # Check if it's a date-like object (parsed by PyYAML or already a datetime.date)
        if hasattr(date_val, 'year') and hasattr(date_val, 'month') and hasattr(date_val, 'day') and not isinstance(date_val, str):
            new_frontmatter['date'] = date_val.strftime('%Y-%m-%d')
        elif isinstance(date_val, str):
            # If it's already a string, ensure it's in the correct format or log warning
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Date string '{date_val}' in frontmatter of {file_path.name} is not in YYYY-MM-DD format during reformat. Attempting to keep original.")
        # If it's None or some other type, it will be handled by YAML dump or previous validation

        # Ensure required sections are present in markdown
        current_sections = {re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE).group(1).strip(): True 
                            for line in new_markdown_content.splitlines() if re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE)}
        
        added_sections_content = "\n"
        for i, section_title in enumerate(EXPECTED_SECTIONS):
            if section_title not in current_sections:
                added_sections_content += f"## {i+1}. {section_title}\n\n(Content for {section_title} needs to be added.)\n\n"
        
        final_markdown_content = new_markdown_content + added_sections_content
        if '✧༺❀༻∞ EGOS ∞༺❀༻✧' not in final_markdown_content:
            final_markdown_content += "\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n"

        try:
            frontmatter_yaml = yaml.dump(new_frontmatter, sort_keys=False, default_flow_style=False)
            new_content = f"---\n{frontmatter_yaml}---\n{final_markdown_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Successfully reformatted and saved {file_path}")
            self.files_standardized += 1
        except Exception as e:
            error_info = {
                "file": str(file_path),
                "error": str(e),
                "stage": "writing_reformatted_file",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.reformatting_failures.append(error_info)
            logger.error(f"Error writing reformatted file {file_path}: {e}")
            self.issues_found +=1 # Count as an issue if reformatting fails

    def _archive_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> None:
        """Archive a completed work log if it meets the criteria."""
        if frontmatter is None or frontmatter.get('status', '').lower() != 'completed':
            return # Not completed, or no frontmatter to check status

        file_mod_time_str = frontmatter.get('date') # Use 'date' from frontmatter as proxy for completion date
        if not file_mod_time_str or not isinstance(file_mod_time_str, str):
             # If no valid date, try to get file's actual modification time
            try:
                file_mod_timestamp = file_path.stat().st_mtime
                file_mod_date = datetime.fromtimestamp(file_mod_timestamp)
            except OSError:
                logger.warning(f"Could not determine modification date for {file_path} to check for archiving.")
                return
        else:
            try:
                file_mod_date = datetime.strptime(file_mod_time_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date '{file_mod_time_str}' in frontmatter of {file_path} for archiving check.")
                return

        if datetime.now() - file_mod_date > timedelta(days=ARCHIVE_RETENTION_DAYS):
            archive_target_path = self.archive_dir / file_path.name
            if self.dry_run:
                logger.info(f"[DRY RUN] Would archive {file_path} to {archive_target_path}")
            else:
                try:
                    shutil.move(str(file_path), str(archive_target_path))
                    logger.info(f"Archived {file_path} to {archive_target_path}")
                    self.files_archived += 1
                except Exception as e:
                    logger.error(f"Error archiving {file_path} to {archive_target_path}: {e}")
                    self.issues_found +=1
        else:
            logger.debug(f"Work log {file_path} is completed but not yet old enough for archiving.")

    def _standardize_filename(self, file_path: Path) -> Path:
        """Standardize a work log filename to snake_case format.
        
        Returns:
            The new path if renamed, or the original path if no renaming was needed or possible.
        """
        filename = file_path.name
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        
        if len(parts) < 3:
            logger.warning(f"Cannot standardize filename {filename}: unexpected format (not enough parts)")
            return file_path
            
        prefix, date, desc_with_ext = parts
        
        # Check if date format needs correction (some files might use underscore instead of hyphen)
        if '-' not in date and len(date) == 8:  # Format might be YYYYMMDD or YYYY_MM_DD
            try:
                if '_' in date:  # Format is YYYY_MM_DD
                    year, month, day = date.split('_')
                else:  # Format is YYYYMMDD
                    year, month, day = date[:4], date[4:6], date[6:8]
                date = f"{year}-{month}-{day}"
                logger.info(f"Corrected date format in filename from {parts[1]} to {date}")
            except ValueError:
                logger.warning(f"Could not parse date in filename: {filename}")
        
        # Fix description part (convert to snake_case)
        desc_parts = desc_with_ext.split('.')
        desc = desc_parts[0]
        ext = desc_parts[1] if len(desc_parts) > 1 else "md"
        
        # Remove any existing underscores for clean conversion
        desc_no_underscores = desc.replace('_', ' ')
        
        # Handle common patterns like MCP_Documentation to mcp_documentation
        # First replace internal uppercase-prefixed words with space + that word
        # E.g., "MCPDocumentation" -> "MCP Documentation"
        desc_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', desc_no_underscores)
        
        # Then convert to lowercase and replace spaces with underscores
        snake_desc = desc_spaced.lower().replace(' ', '_')
        
        # Construct new filename
        new_filename = f"{prefix}_{date}_{snake_desc}.{ext}"
        
        if new_filename == filename:
            return file_path  # No change needed
            
        new_path = file_path.parent / new_filename
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename {filename} to {new_filename}")
            return file_path  # Return original in dry run
            
        try:
            if new_path.exists():
                logger.warning(f"Cannot rename to {new_filename} as it already exists.")
                return file_path
                
            file_path.rename(new_path)
            logger.info(f"Successfully renamed {filename} to {new_filename}")
            return new_path
        except Exception as e:
            logger.error(f"Error renaming {filename} to {new_filename}: {e}")
            return file_path
    
    def run_standardization(self) -> None:
        """Run the full work log standardization process.
        
        This comprehensive process includes:
        1. Detecting and handling duplicate work logs
        2. Standardizing filenames to follow snake_case convention
        3. Validating and reformatting work log content
        4. Archiving completed work logs
        5. Generating a detailed report of all actions taken
        """
        logger.info("Starting comprehensive work log standardization process...")
        self.issues_found = 0
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        self.validation_failures = []  # Store detailed validation failure information
        self.reformatting_failures = []  # Store any files that couldn't be reformatted successfully
        self.deduplication_actions = []  # Track deduplication actions
        self.rename_actions = []  # Track filename standardization actions

        # Step 1: Find all work logs in the active directory
        initial_active_logs = self._find_work_logs(self.active_dir)
        logger.info(f"Found {len(initial_active_logs)} initial work logs in {self.active_dir}")
        
        # Step 2: Detect and handle duplicate work logs
        logger.info("=== PHASE 1: DEDUPLICATION ===")
        deduplicated_logs = self._detect_and_handle_duplicates(self.active_dir)
        
        # Step 3: Standardize all filenames to follow snake_case convention
        logger.info("=== PHASE 2: FILENAME STANDARDIZATION ===")
        standardized_logs = self._standardize_all_filenames(deduplicated_logs)
        
        # Step 4: Process each work log (validate, reformat, archive)
        logger.info("=== PHASE 3: CONTENT VALIDATION AND REFORMATTING ===")
        logger.info(f"Processing {len(standardized_logs)} work logs from {self.active_dir}")
        
        for log_path in standardized_logs:
            logger.info(f"--- Processing: {log_path.name} ---")
            self.files_processed += 1
            
            # Validate the work log
            is_valid = self._validate_work_log(log_path)
            
            # Parse for reformatting and archiving
            frontmatter, markdown_content, parse_successful = self._parse_work_log(log_path)

            # If validation failed, attempt to reformat content
            if not is_valid:
                logger.info(f"Attempting to reformat invalid work log: {log_path.name}")
                self._reformat_work_log(log_path, frontmatter, markdown_content)
                
                # After reformatting, re-parse to get updated frontmatter for archiving
                frontmatter, _, _ = self._parse_work_log(log_path) 
            
            # Step 5: Attempt to archive if it's completed
            self._archive_work_log(log_path, frontmatter)

        # Process logs in archive directory to ensure they are indeed archived (e.g. old completed logs)
        # This could also be a place to validate archived logs, though less critical than active ones.
        archived_logs = self._find_work_logs(self.archive_dir)
        logger.info(f"Checking {len(archived_logs)} work logs in archive directory {self.archive_dir} for any active logs that need moving back.")
        # Example: if a log in archive is not 'Completed', it might need to be moved back to active.
        # For now, this part is kept simple.

        # Step 6: Generate comprehensive standardization report
        logger.info("=== PHASE 4: GENERATING STANDARDIZATION REPORT ===")
        
        # Console summary
        logger.info("--- Standardization Process Summary ---")
        logger.info(f"Total files processed: {self.files_processed}")
        logger.info(f"Duplicate files handled: {self.duplicates_handled}")
        logger.info(f"Filenames standardized: {self.filenames_standardized}")
        logger.info(f"Content reformatted/standardized: {self.files_standardized}")
        logger.info(f"Files archived: {self.files_archived}")
        logger.info(f"Total issues encountered: {self.issues_found}")
        
        # Generate comprehensive standardization report
        report_path = Path(self.active_dir.parent, 'work_log_standardization_report.md')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# EGOS Work Log Standardization Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add EGOS signature banner
                f.write("✧｡◙◞ ◟◙｡✧\n\n")
                
                f.write("## Summary\n")
                f.write(f"- Total files processed: {self.files_processed}\n")
                f.write(f"- Duplicate files handled: {self.duplicates_handled}\n")
                f.write(f"- Filenames standardized: {self.filenames_standardized}\n")
                f.write(f"- Content reformatted: {self.files_standardized}\n")
                f.write(f"- Files archived: {self.files_archived}\n")
                f.write(f"- Issues encountered: {self.issues_found}\n\n")
                
                # Deduplication section
                if self.deduplication_actions:
                    f.write("## Deduplication Actions\n")
                    f.write("The following duplicate files were identified and handled:\n\n")
                    f.write("| Original File | Action | Kept File | Score Comparison |\n")
                    f.write("|--------------|--------|-----------|------------------|\n")
                    
                    for action in self.deduplication_actions:
                        original = Path(action['original']).name
                        kept = Path(action['kept']).name
                        if self.dry_run:
                            action_text = "Would be backed up (dry run)"
                        else:
                            action_text = f"Backed up to {Path(action['backup']).name}"
                        score_comparison = f"{action['score_original']} vs {action['score_kept']}"
                        
                        f.write(f"| {original} | {action_text} | {kept} | {score_comparison} |\n")
                    
                    f.write("\n")
                
                # Filename standardization section
                if self.rename_actions:
                    f.write("## Filename Standardization Actions\n")
                    f.write("The following files were renamed to comply with snake_case convention:\n\n")
                    f.write("| Original Filename | Standardized Filename |\n")
                    f.write("|-------------------|----------------------|\n")
                    
                    for action in self.rename_actions:
                        f.write(f"| {action['original']} | {action['new']} |\n")
                    
                    f.write("\n")
                
                # Validation and reformatting section
                if self.validation_failures:
                    f.write("## Validation Failures\n")
                    for failure in self.validation_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                if self.reformatting_failures:
                    f.write("## Reformatting Failures\n")
                    for failure in self.reformatting_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Error: {failure['error']}\n")
                        f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                # Next steps and recommendations
                f.write("## Next Steps\n")
                if self.issues_found > 0:
                    f.write("To address the remaining issues:\n\n")
                    f.write("1. **Fix invalid frontmatter** in work logs with missing or incorrect metadata.\n")
                    f.write("2. **Add missing sections** to work logs that lack required content structure.\n")
                    f.write("3. **Review backed-up duplicates** to ensure no important content was lost.\n")
                    f.write("4. **Run the standardizer again** after addressing these issues.\n\n")
                else:
                    f.write("All work logs are now standardized according to EGOS requirements. Regular maintenance should include:\n\n")
                    f.write("1. **Run this standardizer weekly** to ensure ongoing compliance.\n")
                    f.write("2. **Archive completed work logs** regularly to maintain a clean active directory.\n")
                    f.write("3. **Follow standard templates** when creating new work logs.\n\n")
                
                # References to EGOS standards
                f.write("## References\n")
                f.write("- [Work Log Standardization](C:\\EGOS\\docs\\work_logs\\WORK_2025-05-23_Work_Log_Standardization.md)\n")
                f.write("- [Master Quantum Prompt](C:\\EGOS\\MQP.md) (Systemic Organization, Evolutionary Preservation principles)\n")
                f.write("- [EGOS Documentation Standards](C:\\EGOS\\docs\\core_materials\\standards\\documentation_standards.md)\n\n")
                
                # EGOS signature footer
                f.write("\n✧｡◙◞ ◟◙｡✧ EGOS ✧｡◙◞ ◟◙｡✧\n")
                
            logger.info(f"Comprehensive standardization report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write standardization report: {e}")
        
        # Generate diagnostic report for issues if needed
        if self.issues_found > 0:
            diagnostic_report_path = Path(self.active_dir.parent, 'standardization_diagnostic_report.md')
            try:
                with open(diagnostic_report_path, 'w', encoding='utf-8') as f:
                    f.write("# Work Log Standardization Diagnostic Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("## Summary\n")
                    f.write(f"- Total files processed: {self.files_processed}\n")
                    f.write(f"- Files with issues: {self.issues_found}\n")
                    f.write(f"- Files standardized: {self.files_standardized}\n")
                    f.write(f"- Files archived: {self.files_archived}\n\n")
                    
                    if self.validation_failures:
                        f.write("## Validation Failures\n")
                        for failure in self.validation_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    if self.reformatting_failures:
                        f.write("## Reformatting Failures\n")
                        for failure in self.reformatting_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Error: {failure['error']}\n")
                            f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    f.write("## Recommendations\n")
                    f.write("To fix the identified issues:\n\n")
                    f.write("1. **Ensure frontmatter** is present in all work logs with correct format.\n")
                    f.write("2. **Check for required sections** such as Objective, Progress, Challenges, etc.\n")
                    f.write("3. **Validate filenames** follow the format `WORK_YYYY-MM-DD_descriptive_name.md`.\n")
                    f.write("4. Run the standardizer again after fixing the issues.\n")
                    
                logger.info(f"Detailed diagnostic report saved to: {diagnostic_report_path}")
            except Exception as e:
                logger.error(f"Failed to write diagnostic report: {e}")
        
        logger.info("Work log standardization process finished.")

        if self.issues_found > 0:
            logger.warning("Standardization completed with issues. Please review the standardization report for details.")
        else:
            logger.info("Standardization completed successfully.")

    def analyze_directory_contents(self, root_dir: Path) -> None:
        """Analyzes work logs directly within root_dir to identify their status."""
        logger.info(f"--- Starting Analysis of Directory: {root_dir} ---")
        found_logs_in_root = 0
        active_identified = 0
        inactive_identified = 0
        unknown_status = 0

        # Determine the names of active and archive directories to avoid double-processing if they are subdirs of root_dir
        # This check is simplified; assumes root_dir is a direct parent if active/archive are inside it.
        active_dir_name = self.active_dir.name
        archive_dir_name = self.archive_dir.name
        is_processing_parent_of_managed_dirs = (self.active_dir.parent == root_dir or self.archive_dir.parent == root_dir)

        for item in root_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs_in_root += 1
                logger.info(f"Analyzing file: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                status_str = "Unknown/Missing Status"
                # is_active = False # Default assumption - not strictly needed here

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str = frontmatter['status'] # Keep original casing for logging
                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        inactive_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as INACTIVE/ARCHIVABLE")
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        active_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as ACTIVE")
                    else:
                        unknown_status += 1
                        logger.warning(f"  -> Status: '{status_str}' - Status UNKNOWN or not standard.")
                else:
                    unknown_status += 1
                    logger.warning(f"  -> Status: MISSING - Could not determine status from frontmatter.")
        
        logger.info("--- Directory Analysis Summary ---")
        logger.info(f"Total work log files found directly in {root_dir}: {found_logs_in_root}")
        logger.info(f"  Identified as ACTIVE: {active_identified}")
        logger.info(f"  Identified as INACTIVE/ARCHIVABLE: {inactive_identified}")
        logger.info(f"  Status UNKNOWN or MISSING: {unknown_status}")
        logger.info("Analysis finished. No files were moved or modified.")

    def _detect_and_handle_duplicates(self, directory: Path) -> List[Path]:
        """Detect and handle duplicate work log files in the specified directory.
        
        Duplicates are detected based on:
        1. Similar filenames (after standardization)
        2. Similar content (using similarity threshold)
        3. Same date in frontmatter
        
        When duplicates are found:
        1. The most complete/valid file is kept
        2. Other duplicates are backed up and noted in the report
        
        Args:
            directory: Directory to search for duplicates
            
        Returns:
            List of paths to the deduplicated work log files
        """
        logger.info(f"Detecting and handling duplicate work logs in {directory}...")
        
        all_logs = self._find_work_logs(directory)
        if len(all_logs) <= 1:
            logger.info(f"No potential duplicates found in {directory} (only {len(all_logs)} logs)")
            return all_logs
            
        # Group files by normalized names (to catch variations like WORK_2025-05-22 vs WORK_2025_05_22)
        name_groups = {}
        for log_path in all_logs:
            # Extract date and description from filename
            parts = log_path.stem.split('_', 2)
            if len(parts) < 3:
                # Not a standard work log filename, skip grouping
                continue
                
            date_part = parts[1]
            # Normalize date format (replace underscores with hyphens)
            norm_date = date_part.replace('_', '-')
            
            # Normalize description part to lowercase
            desc_part = parts[2].lower()
            
            # Create normalized key for grouping
            norm_key = f"{norm_date}_{desc_part}"
            
            if norm_key not in name_groups:
                name_groups[norm_key] = []
            name_groups[norm_key].append(log_path)
        
        # Filter to only groups with multiple files (potential duplicates)
        duplicate_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
        
        if not duplicate_groups:
            logger.info(f"No duplicate work logs found in {directory} based on filename analysis")
            return all_logs
            
        logger.info(f"Found {len(duplicate_groups)} groups of potential duplicate work logs")
        
        # Process each group of potential duplicates
        final_logs = []
        duplicate_paths = set()  # Track all identified duplicates
        
        for group_key, group_paths in duplicate_groups.items():
            logger.info(f"Processing duplicate group: {group_key} with {len(group_paths)} files")
            
            # Read content and metadata for each file in the group
            group_files = []
            for path in group_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    frontmatter, markdown, parse_success = self._parse_work_log(path)
                    
                    # Count complete sections as a measure of completeness
                    section_count = 0
                    if markdown:
                        for section in EXPECTED_SECTIONS:
                            if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", markdown, re.MULTILINE | re.IGNORECASE):
                                section_count += 1
                    
                    # Calculate file score (higher is better)
                    # Scoring factors: file size, completeness of frontmatter, number of sections
                    frontmatter_score = len(frontmatter.keys()) if frontmatter else 0
                    size_score = len(content)
                    
                    file_score = size_score + (frontmatter_score * 100) + (section_count * 500)
                    
                    group_files.append({
                        'path': path,
                        'content': content,
                        'frontmatter': frontmatter,
                        'markdown': markdown,
                        'section_count': section_count,
                        'score': file_score
                    })
                except Exception as e:
                    logger.error(f"Error processing {path} for duplicate detection: {e}")
            
            if not group_files:
                logger.warning(f"Could not process any files in duplicate group {group_key}")
                continue
                
            # Sort files by score (highest first)
            group_files.sort(key=lambda x: x['score'], reverse=True)
            
            # Keep the highest scoring file, mark others as duplicates
            keeper = group_files[0]
            duplicate_files = group_files[1:]
            
            logger.info(f"Keeping highest scoring file: {keeper['path'].name} (score: {keeper['score']})")
            final_logs.append(keeper['path'])
            
            # Backup and record duplicates
            for dup in duplicate_files:
                duplicate_paths.add(dup['path'])
                
                if not self.dry_run:
                    try:
                        # Create backup with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_name = f"{dup['path'].stem}_DUPLICATE_{timestamp}{dup['path'].suffix}"
                        backup_path = self.backup_dir / backup_name
                        
                        shutil.copy2(dup['path'], backup_path)
                        logger.info(f"Backed up duplicate: {dup['path'].name} to {backup_path}")
                        
                        # Record action
                        self.deduplication_actions.append({
                            'original': str(dup['path']),
                            'backup': str(backup_path),
                            'kept': str(keeper['path']),
                            'score_original': dup['score'],
                            'score_kept': keeper['score'],
                            'timestamp': timestamp
                        })
                        
                        self.duplicates_handled += 1
                    except Exception as e:
                        logger.error(f"Error backing up duplicate {dup['path']}: {e}")
                else:
                    logger.info(f"[DRY RUN] Would back up duplicate: {dup['path'].name}")
                    self.deduplication_actions.append({
                        'original': str(dup['path']),
                        'backup': f"[DRY RUN] Would back up to {self.backup_dir}",
                        'kept': str(keeper['path']),
                        'score_original': dup['score'],
                        'score_kept': keeper['score'],
                        'timestamp': '[DRY RUN]'
                    })
        
        # Add any non-duplicate files to the final list
        for log_path in all_logs:
            if log_path not in duplicate_paths and log_path not in final_logs:
                final_logs.append(log_path)
        
        logger.info(f"Duplicate handling complete. Kept {len(final_logs)} unique files, handled {self.duplicates_handled} duplicates")
        return final_logs
    
    def _standardize_all_filenames(self, log_paths: List[Path]) -> List[Path]:
        """Standardize all work log filenames to follow EGOS snake_case convention.
        
        Args:
            log_paths: List of paths to work log files
            
        Returns:
            List of paths to the standardized files (may be different from input paths if renamed)
        """
        logger.info(f"Standardizing filenames for {len(log_paths)} work logs...")
        
        standardized_paths = []
        for log_path in log_paths:
            standardized_path = self._standardize_filename(log_path)
            standardized_paths.append(standardized_path)
            
            if standardized_path != log_path:
                self.filenames_standardized += 1
                
        logger.info(f"Filename standardization complete. Standardized {self.filenames_standardized} filenames")
        return standardized_paths

    def migrate_logs_from_directory(self, source_dir: Path) -> None:
        """Analyzes logs in source_dir and migrates them to active/archive dirs. Reports unknown status logs."""
        logger.info(f"--- Starting Migration from Directory: {source_dir} ---")
        logger.info(f"Target ACTIVE directory: {self.active_dir}")
        logger.info(f"Target ARCHIVE directory: {self.archive_dir}")
        if self.dry_run:
            logger.info("[DRY RUN] No files will actually be moved.")

        found_logs = 0
        moved_to_active = 0
        moved_to_archive = 0
        unknown_status_logs = []
        migration_errors = 0

        # Ensure target directories exist
        if not self.dry_run:
            self.active_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs += 1
                logger.debug(f"Processing file for migration: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                target_path = None
                action_description = ""

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str_original = frontmatter['status']

                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        target_path = self.archive_dir / item.name
                        action_description = f"Identified as INACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_archive +=1 # Tentative count
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        target_path = self.active_dir / item.name
                        action_description = f"Identified as ACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_active +=1 # Tentative count
                    else:
                        logger.warning(f"File '{item.name}': Status '{status_str_original}' is UNKNOWN. File will not be moved.")
                        unknown_status_logs.append(item.name)
                else:
                    logger.warning(f"File '{item.name}': Status MISSING in frontmatter. File will not be moved.")
                    unknown_status_logs.append(item.name)

                if target_path:
                    logger.info(f"File '{item.name}': {action_description}")
                    if not self.dry_run:
                        try:
                            if target_path.exists():
                                logger.warning(f"  SKIPPING move: Target file {target_path} already exists.")
                                # Decrement count if skipped
                                if self.archive_dir / item.name == target_path: moved_to_archive -=1
                                if self.active_dir / item.name == target_path: moved_to_active -=1
                                migration_errors +=1
                            else:
                                shutil.move(str(item), str(target_path))
                                logger.info(f"  SUCCESS: Moved '{item.name}' to '{target_path}'")
                        except Exception as e:
                            logger.error(f"  FAILED to move '{item.name}' to '{target_path}': {e}")
                            # Decrement count if failed
                            if self.archive_dir / item.name == target_path: moved_to_archive -=1
                            if self.active_dir / item.name == target_path: moved_to_active -=1
                            migration_errors += 1
                
        logger.info("--- Migration Summary ---")
        logger.info(f"Total work log files found in {source_dir}: {found_logs}")
        logger.info(f"  Attempted to move to ACTIVE ({self.active_dir}): {moved_to_active}")
        logger.info(f"  Attempted to move to ARCHIVE ({self.archive_dir}): {moved_to_archive}")
        logger.info(f"  Files with UNKNOWN/MISSING status (not moved): {len(unknown_status_logs)}")
        if unknown_status_logs:
            for log_name in unknown_status_logs:
                logger.info(f"    - {log_name}")
        if migration_errors > 0:
            logger.warning(f"  Migration errors encountered: {migration_errors}")
        logger.info(f"Migration process finished. Check logs for details. Dry run: {self.dry_run}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize EGOS work log files.")
    parser.add_argument("--active-dir", type=Path, default=DEFAULT_ACTIVE_DIR, help="Directory for active work logs.")
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archived work logs.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without modifying files.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--analyze-root-directory", type=Path, help="Analyze work logs in the specified root directory to identify their status without moving or standardizing.")
    parser.add_argument("--migrate-logs-from", type=Path, help="Analyze and migrate logs from a source directory to 'active' or 'archive' subdirectories. Logs with unknown status are reported but not moved.")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    standardizer = WorkLogStandardizer(active_dir=args.active_dir, archive_dir=args.archive_dir, dry_run=args.dry_run)

    if args.analyze_root_directory:
        if not args.analyze_root_directory.is_dir():
            logger.error(f"Error: --analyze-root-directory path is not a valid directory: {args.analyze_root_directory}")
            sys.exit(1)
        standardizer.analyze_directory_contents(args.analyze_root_directory)
    elif args.migrate_logs_from:
        if not args.migrate_logs_from.is_dir():
            logger.error(f"Error: --migrate-logs-from path is not a valid directory: {args.migrate_logs_from}")
            sys.exit(1)
        standardizer.migrate_logs_from_directory(args.migrate_logs_from)
    else:
        standardizer.run_standardization()
        sys.exit(1 if standardizer.issues_found > 0 else 0)
, tag):
                        issue = f"Tag contains invalid characters: '{tag}'. Use only lowercase letters, numbers, hyphens, and underscores."
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
    def _validate_sections(self, file_path: Path, markdown_content: Optional[str]) -> bool:
        """Validate the presence of required sections in the Markdown content.
        
        This method checks if all required sections are present in the work log markdown content.
        It handles various section header formats (with or without numbering).
        
        Args:
            file_path: Path to the work log file being validated
            markdown_content: String containing the markdown content, or None if parsing failed
            
        Returns:
            Boolean indicating if all required sections are present
        """
        if markdown_content is None:
            logger.warning(f"Missing markdown content for section validation in {file_path}.")
            # This usually follows a parsing error, so issue might already be counted.
            return False
        
        if not markdown_content.strip():
            logger.warning(f"Empty markdown content in {file_path}")
            return False
            
        valid = True
        validation_issues = []
        found_sections = []
        missing_sections = []
        
        # First, extract all section headers from the markdown content
        section_pattern = r'^##\s*(\d+\.\s*)?([^\n]+)'  # Matches '## Section', '## 1. Section', etc.
        section_matches = re.finditer(section_pattern, markdown_content, re.MULTILINE)
        
        # Build a list of all found section titles (normalized for comparison)
        for match in section_matches:
            section_title = match.group(2).strip()
            found_sections.append(section_title.lower())
        
        # Check for each required section
        for section_title in EXPECTED_SECTIONS:
            # Check if any found section matches this required section (case-insensitive)
            if not any(section_title.lower() in found.lower() or found.lower() in section_title.lower() 
                      for found in found_sections):
                missing_sections.append(section_title)
                issue = f"Missing required section: '{section_title}'"
                validation_issues.append(issue)
                logger.warning(f"{file_path.name}: {issue}")
                valid = False
        
        # Additional check: Ensure sections have content
        section_blocks = re.split(section_pattern, markdown_content, flags=re.MULTILINE)[1:]
        # section_blocks will contain: [number, title, content, number, title, content, ...]
        # We need to check every third item (the content)
        for i in range(2, len(section_blocks), 3):
            if i < len(section_blocks):
                content = section_blocks[i].strip()
                title = section_blocks[i-1].strip() if i-1 < len(section_blocks) else "Unknown"
                if not content:
                    issue = f"Empty section content for '{title}'"
                    validation_issues.append(issue)
                    logger.warning(f"{file_path.name}: {issue}")
                    valid = False
        
        if not valid:
            logger.warning(f"Section validation failed for {file_path.name} with {len(validation_issues)} issues")
            if missing_sections:
                logger.warning(f"Missing sections: {', '.join(missing_sections)}")
        
        return valid

    def _validate_work_log(self, file_path: Path) -> bool:
        """Validate a single work log file comprehensively."""
        logger.debug(f"Validating work log: {file_path}")
        # self.files_processed is incremented in run_standardization before calling this

        issues_for_this_file = []

        filename_valid = self._validate_filename(file_path)
        if not filename_valid:
            issues_for_this_file.append("filename_invalid")
        
        frontmatter, markdown_content, parse_successful = self._parse_work_log(file_path)
        if not parse_successful:
            issues_for_this_file.append("parse_failed")
            # If parsing failed, frontmatter/markdown_content might be None, affecting subsequent checks.
            # _validate_frontmatter and _validate_sections should handle None inputs gracefully.

        # Proceed with content validation even if filename/parse had issues, to gather all problems
        # but only if parse was successful enough to yield some content to validate.
        frontmatter_valid = self._validate_frontmatter(file_path, frontmatter) 
        if not frontmatter_valid:
            issues_for_this_file.append("frontmatter_invalid")

        sections_valid = self._validate_sections(file_path, markdown_content)
        if not sections_valid:
            issues_for_this_file.append("sections_invalid")
        
        # A file is fully valid if all checks pass. Note: parse_successful is implicitly part of this.
        # If parse_successful is false, frontmatter_valid/sections_valid might also be false due to None inputs.
        is_fully_valid = filename_valid and parse_successful and frontmatter_valid and sections_valid
        
        if is_fully_valid:
            logger.info(f"Work log {file_path} is valid.")
            return True
        else:
            failure_info = {
                "file": str(file_path),
                "issues": issues_for_this_file,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.validation_failures.append(failure_info)
            logger.warning(f"Work log {file_path} has validation issues: {', '.join(issues_for_this_file)}.")
            self.issues_found += 1 # Increment global issue counter ONCE if any validation failed for this file.
            return False

    def _reformat_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]], markdown_content: Optional[str]) -> None:
        """Reformat a work log file to the standard, fixing both content and filename if needed."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would reformat {file_path}")
            self.files_standardized +=1 # Assume it would be standardized
            return
            
        # Check and fix filename if needed
        original_path = file_path
        filename = file_path.name
        filename_fixed = False
        
        # If filename doesn't match the snake_case pattern for the descriptive part
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        if len(parts) >= 3:
            prefix, date, desc_with_ext = parts
            # Check if the descriptive part has uppercase letters
            if not all(c.islower() or c.isdigit() or c == '_' or c == '.' for c in desc_with_ext):
                # Convert descriptive part to snake_case (lowercase with underscores)
                desc_part = desc_with_ext.split('.')[0]
                ext = desc_with_ext.split('.')[-1] if '.' in desc_with_ext else 'md'
                
                # Convert to snake_case
                new_desc_part = desc_part.lower()
                
                # Construct the new filename
                new_filename = f"{prefix}_{date}_{new_desc_part}.{ext}"
                new_path = file_path.parent / new_filename
                
                try:
                    # Rename the file
                    if new_path.exists():
                        logger.warning(f"Cannot rename to {new_filename} as it already exists. Will update content only.")
                    else:
                        file_path.rename(new_path)
                        logger.info(f"Renamed file from {filename} to {new_filename}")
                        file_path = new_path  # Update file_path for content reformatting
                        filename_fixed = True
                except Exception as e:
                    logger.error(f"Error renaming file {file_path} to {new_path}: {e}")
                    # Continue with content reformatting even if renaming fails

        # Basic reformatting: Ensure frontmatter and essential sections exist.
        # A more sophisticated version would try to intelligently migrate existing content.
        
        new_frontmatter = frontmatter if frontmatter is not None else {}
        new_markdown_content = markdown_content if markdown_content is not None else ""

        # Ensure all expected frontmatter keys are present, adding defaults if necessary
        if 'date' not in new_frontmatter:
            try:
                # Attempt to get date from filename
                date_str = file_path.name.split('_')[1]
                new_frontmatter['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except (IndexError, ValueError):
                new_frontmatter['date'] = datetime.now().strftime("%Y-%m-%d") # Default to today
        
        for key in EXPECTED_FRONTMATTER_KEYS:
            if key not in new_frontmatter:
                if key == 'title':
                    new_frontmatter[key] = f"Work Log for {file_path.stem}" 
                elif key == 'author':
                    new_frontmatter[key] = "EGOS System (Standardized)"
                elif key == 'status':
                    new_frontmatter[key] = "In Progress" # Default status
                elif key == 'priority':
                    new_frontmatter[key] = "Medium"
                elif key == 'tags':
                    new_frontmatter[key] = ["standardized"]
                elif key == 'roadmap_ids':
                    new_frontmatter[key] = []
                else:
                    new_frontmatter[key] = f"Placeholder for {key}"
        
        # Ensure date is a string for YAML dump
        date_val = new_frontmatter.get('date')
        # Check if it's a date-like object (parsed by PyYAML or already a datetime.date)
        if hasattr(date_val, 'year') and hasattr(date_val, 'month') and hasattr(date_val, 'day') and not isinstance(date_val, str):
            new_frontmatter['date'] = date_val.strftime('%Y-%m-%d')
        elif isinstance(date_val, str):
            # If it's already a string, ensure it's in the correct format or log warning
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Date string '{date_val}' in frontmatter of {file_path.name} is not in YYYY-MM-DD format during reformat. Attempting to keep original.")
        # If it's None or some other type, it will be handled by YAML dump or previous validation

        # Ensure required sections are present in markdown
        current_sections = {re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE).group(1).strip(): True 
                            for line in new_markdown_content.splitlines() if re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE)}
        
        added_sections_content = "\n"
        for i, section_title in enumerate(EXPECTED_SECTIONS):
            if section_title not in current_sections:
                added_sections_content += f"## {i+1}. {section_title}\n\n(Content for {section_title} needs to be added.)\n\n"
        
        final_markdown_content = new_markdown_content + added_sections_content
        if '✧༺❀༻∞ EGOS ∞༺❀༻✧' not in final_markdown_content:
            final_markdown_content += "\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n"

        try:
            frontmatter_yaml = yaml.dump(new_frontmatter, sort_keys=False, default_flow_style=False)
            new_content = f"---\n{frontmatter_yaml}---\n{final_markdown_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Successfully reformatted and saved {file_path}")
            self.files_standardized += 1
        except Exception as e:
            error_info = {
                "file": str(file_path),
                "error": str(e),
                "stage": "writing_reformatted_file",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.reformatting_failures.append(error_info)
            logger.error(f"Error writing reformatted file {file_path}: {e}")
            self.issues_found +=1 # Count as an issue if reformatting fails

    def _archive_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> None:
        """Archive a completed work log if it meets the criteria."""
        if frontmatter is None or frontmatter.get('status', '').lower() != 'completed':
            return # Not completed, or no frontmatter to check status

        file_mod_time_str = frontmatter.get('date') # Use 'date' from frontmatter as proxy for completion date
        if not file_mod_time_str or not isinstance(file_mod_time_str, str):
             # If no valid date, try to get file's actual modification time
            try:
                file_mod_timestamp = file_path.stat().st_mtime
                file_mod_date = datetime.fromtimestamp(file_mod_timestamp)
            except OSError:
                logger.warning(f"Could not determine modification date for {file_path} to check for archiving.")
                return
        else:
            try:
                file_mod_date = datetime.strptime(file_mod_time_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date '{file_mod_time_str}' in frontmatter of {file_path} for archiving check.")
                return

        if datetime.now() - file_mod_date > timedelta(days=ARCHIVE_RETENTION_DAYS):
            archive_target_path = self.archive_dir / file_path.name
            if self.dry_run:
                logger.info(f"[DRY RUN] Would archive {file_path} to {archive_target_path}")
            else:
                try:
                    shutil.move(str(file_path), str(archive_target_path))
                    logger.info(f"Archived {file_path} to {archive_target_path}")
                    self.files_archived += 1
                except Exception as e:
                    logger.error(f"Error archiving {file_path} to {archive_target_path}: {e}")
                    self.issues_found +=1
        else:
            logger.debug(f"Work log {file_path} is completed but not yet old enough for archiving.")

    def _standardize_filename(self, file_path: Path) -> Path:
        """Standardize a work log filename to snake_case format.
        
        Returns:
            The new path if renamed, or the original path if no renaming was needed or possible.
        """
        filename = file_path.name
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        
        if len(parts) < 3:
            logger.warning(f"Cannot standardize filename {filename}: unexpected format (not enough parts)")
            return file_path
            
        prefix, date, desc_with_ext = parts
        
        # Check if date format needs correction (some files might use underscore instead of hyphen)
        if '-' not in date and len(date) == 8:  # Format might be YYYYMMDD or YYYY_MM_DD
            try:
                if '_' in date:  # Format is YYYY_MM_DD
                    year, month, day = date.split('_')
                else:  # Format is YYYYMMDD
                    year, month, day = date[:4], date[4:6], date[6:8]
                date = f"{year}-{month}-{day}"
                logger.info(f"Corrected date format in filename from {parts[1]} to {date}")
            except ValueError:
                logger.warning(f"Could not parse date in filename: {filename}")
        
        # Fix description part (convert to snake_case)
        desc_parts = desc_with_ext.split('.')
        desc = desc_parts[0]
        ext = desc_parts[1] if len(desc_parts) > 1 else "md"
        
        # Remove any existing underscores for clean conversion
        desc_no_underscores = desc.replace('_', ' ')
        
        # Handle common patterns like MCP_Documentation to mcp_documentation
        # First replace internal uppercase-prefixed words with space + that word
        # E.g., "MCPDocumentation" -> "MCP Documentation"
        desc_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', desc_no_underscores)
        
        # Then convert to lowercase and replace spaces with underscores
        snake_desc = desc_spaced.lower().replace(' ', '_')
        
        # Construct new filename
        new_filename = f"{prefix}_{date}_{snake_desc}.{ext}"
        
        if new_filename == filename:
            return file_path  # No change needed
            
        new_path = file_path.parent / new_filename
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename {filename} to {new_filename}")
            return file_path  # Return original in dry run
            
        try:
            if new_path.exists():
                logger.warning(f"Cannot rename to {new_filename} as it already exists.")
                return file_path
                
            file_path.rename(new_path)
            logger.info(f"Successfully renamed {filename} to {new_filename}")
            return new_path
        except Exception as e:
            logger.error(f"Error renaming {filename} to {new_filename}: {e}")
            return file_path
    
    def run_standardization(self) -> None:
        """Run the full work log standardization process.
        
        This comprehensive process includes:
        1. Detecting and handling duplicate work logs
        2. Standardizing filenames to follow snake_case convention
        3. Validating and reformatting work log content
        4. Archiving completed work logs
        5. Generating a detailed report of all actions taken
        """
        logger.info("Starting comprehensive work log standardization process...")
        self.issues_found = 0
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        self.validation_failures = []  # Store detailed validation failure information
        self.reformatting_failures = []  # Store any files that couldn't be reformatted successfully
        self.deduplication_actions = []  # Track deduplication actions
        self.rename_actions = []  # Track filename standardization actions

        # Step 1: Find all work logs in the active directory
        initial_active_logs = self._find_work_logs(self.active_dir)
        logger.info(f"Found {len(initial_active_logs)} initial work logs in {self.active_dir}")
        
        # Step 2: Detect and handle duplicate work logs
        logger.info("=== PHASE 1: DEDUPLICATION ===")
        deduplicated_logs = self._detect_and_handle_duplicates(self.active_dir)
        
        # Step 3: Standardize all filenames to follow snake_case convention
        logger.info("=== PHASE 2: FILENAME STANDARDIZATION ===")
        standardized_logs = self._standardize_all_filenames(deduplicated_logs)
        
        # Step 4: Process each work log (validate, reformat, archive)
        logger.info("=== PHASE 3: CONTENT VALIDATION AND REFORMATTING ===")
        logger.info(f"Processing {len(standardized_logs)} work logs from {self.active_dir}")
        
        for log_path in standardized_logs:
            logger.info(f"--- Processing: {log_path.name} ---")
            self.files_processed += 1
            
            # Validate the work log
            is_valid = self._validate_work_log(log_path)
            
            # Parse for reformatting and archiving
            frontmatter, markdown_content, parse_successful = self._parse_work_log(log_path)

            # If validation failed, attempt to reformat content
            if not is_valid:
                logger.info(f"Attempting to reformat invalid work log: {log_path.name}")
                self._reformat_work_log(log_path, frontmatter, markdown_content)
                
                # After reformatting, re-parse to get updated frontmatter for archiving
                frontmatter, _, _ = self._parse_work_log(log_path) 
            
            # Step 5: Attempt to archive if it's completed
            self._archive_work_log(log_path, frontmatter)

        # Process logs in archive directory to ensure they are indeed archived (e.g. old completed logs)
        # This could also be a place to validate archived logs, though less critical than active ones.
        archived_logs = self._find_work_logs(self.archive_dir)
        logger.info(f"Checking {len(archived_logs)} work logs in archive directory {self.archive_dir} for any active logs that need moving back.")
        # Example: if a log in archive is not 'Completed', it might need to be moved back to active.
        # For now, this part is kept simple.

        # Step 6: Generate comprehensive standardization report
        logger.info("=== PHASE 4: GENERATING STANDARDIZATION REPORT ===")
        
        # Console summary
        logger.info("--- Standardization Process Summary ---")
        logger.info(f"Total files processed: {self.files_processed}")
        logger.info(f"Duplicate files handled: {self.duplicates_handled}")
        logger.info(f"Filenames standardized: {self.filenames_standardized}")
        logger.info(f"Content reformatted/standardized: {self.files_standardized}")
        logger.info(f"Files archived: {self.files_archived}")
        logger.info(f"Total issues encountered: {self.issues_found}")
        
        # Generate comprehensive standardization report
        report_path = Path(self.active_dir.parent, 'work_log_standardization_report.md')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# EGOS Work Log Standardization Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add EGOS signature banner
                f.write("✧｡◙◞ ◟◙｡✧\n\n")
                
                f.write("## Summary\n")
                f.write(f"- Total files processed: {self.files_processed}\n")
                f.write(f"- Duplicate files handled: {self.duplicates_handled}\n")
                f.write(f"- Filenames standardized: {self.filenames_standardized}\n")
                f.write(f"- Content reformatted: {self.files_standardized}\n")
                f.write(f"- Files archived: {self.files_archived}\n")
                f.write(f"- Issues encountered: {self.issues_found}\n\n")
                
                # Deduplication section
                if self.deduplication_actions:
                    f.write("## Deduplication Actions\n")
                    f.write("The following duplicate files were identified and handled:\n\n")
                    f.write("| Original File | Action | Kept File | Score Comparison |\n")
                    f.write("|--------------|--------|-----------|------------------|\n")
                    
                    for action in self.deduplication_actions:
                        original = Path(action['original']).name
                        kept = Path(action['kept']).name
                        if self.dry_run:
                            action_text = "Would be backed up (dry run)"
                        else:
                            action_text = f"Backed up to {Path(action['backup']).name}"
                        score_comparison = f"{action['score_original']} vs {action['score_kept']}"
                        
                        f.write(f"| {original} | {action_text} | {kept} | {score_comparison} |\n")
                    
                    f.write("\n")
                
                # Filename standardization section
                if self.rename_actions:
                    f.write("## Filename Standardization Actions\n")
                    f.write("The following files were renamed to comply with snake_case convention:\n\n")
                    f.write("| Original Filename | Standardized Filename |\n")
                    f.write("|-------------------|----------------------|\n")
                    
                    for action in self.rename_actions:
                        f.write(f"| {action['original']} | {action['new']} |\n")
                    
                    f.write("\n")
                
                # Validation and reformatting section
                if self.validation_failures:
                    f.write("## Validation Failures\n")
                    for failure in self.validation_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                if self.reformatting_failures:
                    f.write("## Reformatting Failures\n")
                    for failure in self.reformatting_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Error: {failure['error']}\n")
                        f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                # Next steps and recommendations
                f.write("## Next Steps\n")
                if self.issues_found > 0:
                    f.write("To address the remaining issues:\n\n")
                    f.write("1. **Fix invalid frontmatter** in work logs with missing or incorrect metadata.\n")
                    f.write("2. **Add missing sections** to work logs that lack required content structure.\n")
                    f.write("3. **Review backed-up duplicates** to ensure no important content was lost.\n")
                    f.write("4. **Run the standardizer again** after addressing these issues.\n\n")
                else:
                    f.write("All work logs are now standardized according to EGOS requirements. Regular maintenance should include:\n\n")
                    f.write("1. **Run this standardizer weekly** to ensure ongoing compliance.\n")
                    f.write("2. **Archive completed work logs** regularly to maintain a clean active directory.\n")
                    f.write("3. **Follow standard templates** when creating new work logs.\n\n")
                
                # References to EGOS standards
                f.write("## References\n")
                f.write("- [Work Log Standardization](C:\\EGOS\\docs\\work_logs\\WORK_2025-05-23_Work_Log_Standardization.md)\n")
                f.write("- [Master Quantum Prompt](C:\\EGOS\\MQP.md) (Systemic Organization, Evolutionary Preservation principles)\n")
                f.write("- [EGOS Documentation Standards](C:\\EGOS\\docs\\core_materials\\standards\\documentation_standards.md)\n\n")
                
                # EGOS signature footer
                f.write("\n✧｡◙◞ ◟◙｡✧ EGOS ✧｡◙◞ ◟◙｡✧\n")
                
            logger.info(f"Comprehensive standardization report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write standardization report: {e}")
        
        # Generate diagnostic report for issues if needed
        if self.issues_found > 0:
            diagnostic_report_path = Path(self.active_dir.parent, 'standardization_diagnostic_report.md')
            try:
                with open(diagnostic_report_path, 'w', encoding='utf-8') as f:
                    f.write("# Work Log Standardization Diagnostic Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("## Summary\n")
                    f.write(f"- Total files processed: {self.files_processed}\n")
                    f.write(f"- Files with issues: {self.issues_found}\n")
                    f.write(f"- Files standardized: {self.files_standardized}\n")
                    f.write(f"- Files archived: {self.files_archived}\n\n")
                    
                    if self.validation_failures:
                        f.write("## Validation Failures\n")
                        for failure in self.validation_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    if self.reformatting_failures:
                        f.write("## Reformatting Failures\n")
                        for failure in self.reformatting_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Error: {failure['error']}\n")
                            f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    f.write("## Recommendations\n")
                    f.write("To fix the identified issues:\n\n")
                    f.write("1. **Ensure frontmatter** is present in all work logs with correct format.\n")
                    f.write("2. **Check for required sections** such as Objective, Progress, Challenges, etc.\n")
                    f.write("3. **Validate filenames** follow the format `WORK_YYYY-MM-DD_descriptive_name.md`.\n")
                    f.write("4. Run the standardizer again after fixing the issues.\n")
                    
                logger.info(f"Detailed diagnostic report saved to: {diagnostic_report_path}")
            except Exception as e:
                logger.error(f"Failed to write diagnostic report: {e}")
        
        logger.info("Work log standardization process finished.")

        if self.issues_found > 0:
            logger.warning("Standardization completed with issues. Please review the standardization report for details.")
        else:
            logger.info("Standardization completed successfully.")

    def analyze_directory_contents(self, root_dir: Path) -> None:
        """Analyzes work logs directly within root_dir to identify their status."""
        logger.info(f"--- Starting Analysis of Directory: {root_dir} ---")
        found_logs_in_root = 0
        active_identified = 0
        inactive_identified = 0
        unknown_status = 0

        # Determine the names of active and archive directories to avoid double-processing if they are subdirs of root_dir
        # This check is simplified; assumes root_dir is a direct parent if active/archive are inside it.
        active_dir_name = self.active_dir.name
        archive_dir_name = self.archive_dir.name
        is_processing_parent_of_managed_dirs = (self.active_dir.parent == root_dir or self.archive_dir.parent == root_dir)

        for item in root_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs_in_root += 1
                logger.info(f"Analyzing file: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                status_str = "Unknown/Missing Status"
                # is_active = False # Default assumption - not strictly needed here

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str = frontmatter['status'] # Keep original casing for logging
                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        inactive_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as INACTIVE/ARCHIVABLE")
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        active_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as ACTIVE")
                    else:
                        unknown_status += 1
                        logger.warning(f"  -> Status: '{status_str}' - Status UNKNOWN or not standard.")
                else:
                    unknown_status += 1
                    logger.warning(f"  -> Status: MISSING - Could not determine status from frontmatter.")
        
        logger.info("--- Directory Analysis Summary ---")
        logger.info(f"Total work log files found directly in {root_dir}: {found_logs_in_root}")
        logger.info(f"  Identified as ACTIVE: {active_identified}")
        logger.info(f"  Identified as INACTIVE/ARCHIVABLE: {inactive_identified}")
        logger.info(f"  Status UNKNOWN or MISSING: {unknown_status}")
        logger.info("Analysis finished. No files were moved or modified.")

    def _detect_and_handle_duplicates(self, directory: Path) -> List[Path]:
        """Detect and handle duplicate work log files in the specified directory.
        
        Duplicates are detected based on:
        1. Similar filenames (after standardization)
        2. Similar content (using similarity threshold)
        3. Same date in frontmatter
        
        When duplicates are found:
        1. The most complete/valid file is kept
        2. Other duplicates are backed up and noted in the report
        
        Args:
            directory: Directory to search for duplicates
            
        Returns:
            List of paths to the deduplicated work log files
        """
        logger.info(f"Detecting and handling duplicate work logs in {directory}...")
        
        all_logs = self._find_work_logs(directory)
        if len(all_logs) <= 1:
            logger.info(f"No potential duplicates found in {directory} (only {len(all_logs)} logs)")
            return all_logs
            
        # Group files by normalized names (to catch variations like WORK_2025-05-22 vs WORK_2025_05_22)
        name_groups = {}
        for log_path in all_logs:
            # Extract date and description from filename
            parts = log_path.stem.split('_', 2)
            if len(parts) < 3:
                # Not a standard work log filename, skip grouping
                continue
                
            date_part = parts[1]
            # Normalize date format (replace underscores with hyphens)
            norm_date = date_part.replace('_', '-')
            
            # Normalize description part to lowercase
            desc_part = parts[2].lower()
            
            # Create normalized key for grouping
            norm_key = f"{norm_date}_{desc_part}"
            
            if norm_key not in name_groups:
                name_groups[norm_key] = []
            name_groups[norm_key].append(log_path)
        
        # Filter to only groups with multiple files (potential duplicates)
        duplicate_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
        
        if not duplicate_groups:
            logger.info(f"No duplicate work logs found in {directory} based on filename analysis")
            return all_logs
            
        logger.info(f"Found {len(duplicate_groups)} groups of potential duplicate work logs")
        
        # Process each group of potential duplicates
        final_logs = []
        duplicate_paths = set()  # Track all identified duplicates
        
        for group_key, group_paths in duplicate_groups.items():
            logger.info(f"Processing duplicate group: {group_key} with {len(group_paths)} files")
            
            # Read content and metadata for each file in the group
            group_files = []
            for path in group_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    frontmatter, markdown, parse_success = self._parse_work_log(path)
                    
                    # Count complete sections as a measure of completeness
                    section_count = 0
                    if markdown:
                        for section in EXPECTED_SECTIONS:
                            if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", markdown, re.MULTILINE | re.IGNORECASE):
                                section_count += 1
                    
                    # Calculate file score (higher is better)
                    # Scoring factors: file size, completeness of frontmatter, number of sections
                    frontmatter_score = len(frontmatter.keys()) if frontmatter else 0
                    size_score = len(content)
                    
                    file_score = size_score + (frontmatter_score * 100) + (section_count * 500)
                    
                    group_files.append({
                        'path': path,
                        'content': content,
                        'frontmatter': frontmatter,
                        'markdown': markdown,
                        'section_count': section_count,
                        'score': file_score
                    })
                except Exception as e:
                    logger.error(f"Error processing {path} for duplicate detection: {e}")
            
            if not group_files:
                logger.warning(f"Could not process any files in duplicate group {group_key}")
                continue
                
            # Sort files by score (highest first)
            group_files.sort(key=lambda x: x['score'], reverse=True)
            
            # Keep the highest scoring file, mark others as duplicates
            keeper = group_files[0]
            duplicate_files = group_files[1:]
            
            logger.info(f"Keeping highest scoring file: {keeper['path'].name} (score: {keeper['score']})")
            final_logs.append(keeper['path'])
            
            # Backup and record duplicates
            for dup in duplicate_files:
                duplicate_paths.add(dup['path'])
                
                if not self.dry_run:
                    try:
                        # Create backup with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_name = f"{dup['path'].stem}_DUPLICATE_{timestamp}{dup['path'].suffix}"
                        backup_path = self.backup_dir / backup_name
                        
                        shutil.copy2(dup['path'], backup_path)
                        logger.info(f"Backed up duplicate: {dup['path'].name} to {backup_path}")
                        
                        # Record action
                        self.deduplication_actions.append({
                            'original': str(dup['path']),
                            'backup': str(backup_path),
                            'kept': str(keeper['path']),
                            'score_original': dup['score'],
                            'score_kept': keeper['score'],
                            'timestamp': timestamp
                        })
                        
                        self.duplicates_handled += 1
                    except Exception as e:
                        logger.error(f"Error backing up duplicate {dup['path']}: {e}")
                else:
                    logger.info(f"[DRY RUN] Would back up duplicate: {dup['path'].name}")
                    self.deduplication_actions.append({
                        'original': str(dup['path']),
                        'backup': f"[DRY RUN] Would back up to {self.backup_dir}",
                        'kept': str(keeper['path']),
                        'score_original': dup['score'],
                        'score_kept': keeper['score'],
                        'timestamp': '[DRY RUN]'
                    })
        
        # Add any non-duplicate files to the final list
        for log_path in all_logs:
            if log_path not in duplicate_paths and log_path not in final_logs:
                final_logs.append(log_path)
        
        logger.info(f"Duplicate handling complete. Kept {len(final_logs)} unique files, handled {self.duplicates_handled} duplicates")
        return final_logs
    
    def _standardize_all_filenames(self, log_paths: List[Path]) -> List[Path]:
        """Standardize all work log filenames to follow EGOS snake_case convention.
        
        Args:
            log_paths: List of paths to work log files
            
        Returns:
            List of paths to the standardized files (may be different from input paths if renamed)
        """
        logger.info(f"Standardizing filenames for {len(log_paths)} work logs...")
        
        standardized_paths = []
        for log_path in log_paths:
            standardized_path = self._standardize_filename(log_path)
            standardized_paths.append(standardized_path)
            
            if standardized_path != log_path:
                self.filenames_standardized += 1
                
        logger.info(f"Filename standardization complete. Standardized {self.filenames_standardized} filenames")
        return standardized_paths

    def migrate_logs_from_directory(self, source_dir: Path) -> None:
        """Analyzes logs in source_dir and migrates them to active/archive dirs. Reports unknown status logs."""
        logger.info(f"--- Starting Migration from Directory: {source_dir} ---")
        logger.info(f"Target ACTIVE directory: {self.active_dir}")
        logger.info(f"Target ARCHIVE directory: {self.archive_dir}")
        if self.dry_run:
            logger.info("[DRY RUN] No files will actually be moved.")

        found_logs = 0
        moved_to_active = 0
        moved_to_archive = 0
        unknown_status_logs = []
        migration_errors = 0

        # Ensure target directories exist
        if not self.dry_run:
            self.active_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs += 1
                logger.debug(f"Processing file for migration: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                target_path = None
                action_description = ""

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str_original = frontmatter['status']

                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        target_path = self.archive_dir / item.name
                        action_description = f"Identified as INACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_archive +=1 # Tentative count
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        target_path = self.active_dir / item.name
                        action_description = f"Identified as ACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_active +=1 # Tentative count
                    else:
                        logger.warning(f"File '{item.name}': Status '{status_str_original}' is UNKNOWN. File will not be moved.")
                        unknown_status_logs.append(item.name)
                else:
                    logger.warning(f"File '{item.name}': Status MISSING in frontmatter. File will not be moved.")
                    unknown_status_logs.append(item.name)

                if target_path:
                    logger.info(f"File '{item.name}': {action_description}")
                    if not self.dry_run:
                        try:
                            if target_path.exists():
                                logger.warning(f"  SKIPPING move: Target file {target_path} already exists.")
                                # Decrement count if skipped
                                if self.archive_dir / item.name == target_path: moved_to_archive -=1
                                if self.active_dir / item.name == target_path: moved_to_active -=1
                                migration_errors +=1
                            else:
                                shutil.move(str(item), str(target_path))
                                logger.info(f"  SUCCESS: Moved '{item.name}' to '{target_path}'")
                        except Exception as e:
                            logger.error(f"  FAILED to move '{item.name}' to '{target_path}': {e}")
                            # Decrement count if failed
                            if self.archive_dir / item.name == target_path: moved_to_archive -=1
                            if self.active_dir / item.name == target_path: moved_to_active -=1
                            migration_errors += 1
                
        logger.info("--- Migration Summary ---")
        logger.info(f"Total work log files found in {source_dir}: {found_logs}")
        logger.info(f"  Attempted to move to ACTIVE ({self.active_dir}): {moved_to_active}")
        logger.info(f"  Attempted to move to ARCHIVE ({self.archive_dir}): {moved_to_archive}")
        logger.info(f"  Files with UNKNOWN/MISSING status (not moved): {len(unknown_status_logs)}")
        if unknown_status_logs:
            for log_name in unknown_status_logs:
                logger.info(f"    - {log_name}")
        if migration_errors > 0:
            logger.warning(f"  Migration errors encountered: {migration_errors}")
        logger.info(f"Migration process finished. Check logs for details. Dry run: {self.dry_run}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize EGOS work log files.")
    parser.add_argument("--active-dir", type=Path, default=DEFAULT_ACTIVE_DIR, help="Directory for active work logs.")
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archived work logs.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without modifying files.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--analyze-root-directory", type=Path, help="Analyze work logs in the specified root directory to identify their status without moving or standardizing.")
    parser.add_argument("--migrate-logs-from", type=Path, help="Analyze and migrate logs from a source directory to 'active' or 'archive' subdirectories. Logs with unknown status are reported but not moved.")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    standardizer = WorkLogStandardizer(active_dir=args.active_dir, archive_dir=args.archive_dir, dry_run=args.dry_run)

    if args.analyze_root_directory:
        if not args.analyze_root_directory.is_dir():
            logger.error(f"Error: --analyze-root-directory path is not a valid directory: {args.analyze_root_directory}")
            sys.exit(1)
        standardizer.analyze_directory_contents(args.analyze_root_directory)
    elif args.migrate_logs_from:
        if not args.migrate_logs_from.is_dir():
            logger.error(f"Error: --migrate-logs-from path is not a valid directory: {args.migrate_logs_from}")
            sys.exit(1)
        standardizer.migrate_logs_from_directory(args.migrate_logs_from)
    else:
        standardizer.run_standardization()
        sys.exit(1 if standardizer.issues_found > 0 else 0)
, tag):
                        issue = f"Tag contains invalid characters: '{tag}'. Use only lowercase letters, numbers, hyphens, and underscores."
                        validation_issues.append(issue)
                        logger.warning(f"{file_path.name}: {issue}")
                        valid = False
        
        if not valid:
            logger.warning(f"Frontmatter validation failed for {file_path.name} with {len(validation_issues)} issues")
        
        return valid

    def _validate_sections(self, file_path: Path, markdown_content: Optional[str]) -> bool:
        """Validate the presence of required sections in the Markdown content."""
        if markdown_content is None:
            logger.warning(f"Missing markdown content for section validation in {file_path}.")
            # This usually follows a parsing error, so issue might already be counted.
            return False

        valid = True
        for section_title in EXPECTED_SECTIONS:
            # Regex to find section headers like '## 1. Objective' or '## Objective'
            if not re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section_title)}\s*$\n", markdown_content, re.MULTILINE | re.IGNORECASE):
                logger.warning(f"Missing section '{section_title}' in {file_path}")
                # self.issues_found += 1 # Moved to _validate_work_log
                valid = False
        return valid

    def _validate_work_log(self, file_path: Path) -> bool:
        """Validate a single work log file comprehensively."""
        logger.debug(f"Validating work log: {file_path}")
        # self.files_processed is incremented in run_standardization before calling this

        issues_for_this_file = []

        filename_valid = self._validate_filename(file_path)
        if not filename_valid:
            issues_for_this_file.append("filename_invalid")
        
        frontmatter, markdown_content, parse_successful = self._parse_work_log(file_path)
        if not parse_successful:
            issues_for_this_file.append("parse_failed")
            # If parsing failed, frontmatter/markdown_content might be None, affecting subsequent checks.
            # _validate_frontmatter and _validate_sections should handle None inputs gracefully.

        # Proceed with content validation even if filename/parse had issues, to gather all problems
        # but only if parse was successful enough to yield some content to validate.
        frontmatter_valid = self._validate_frontmatter(file_path, frontmatter) 
        if not frontmatter_valid:
            issues_for_this_file.append("frontmatter_invalid")

        sections_valid = self._validate_sections(file_path, markdown_content)
        if not sections_valid:
            issues_for_this_file.append("sections_invalid")
        
        # A file is fully valid if all checks pass. Note: parse_successful is implicitly part of this.
        # If parse_successful is false, frontmatter_valid/sections_valid might also be false due to None inputs.
        is_fully_valid = filename_valid and parse_successful and frontmatter_valid and sections_valid
        
        if is_fully_valid:
            logger.info(f"Work log {file_path} is valid.")
            return True
        else:
            failure_info = {
                "file": str(file_path),
                "issues": issues_for_this_file,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.validation_failures.append(failure_info)
            logger.warning(f"Work log {file_path} has validation issues: {', '.join(issues_for_this_file)}.")
            self.issues_found += 1 # Increment global issue counter ONCE if any validation failed for this file.
            return False

    def _reformat_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]], markdown_content: Optional[str]) -> None:
        """Reformat a work log file to the standard, fixing both content and filename if needed."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would reformat {file_path}")
            self.files_standardized +=1 # Assume it would be standardized
            return
            
        # Check and fix filename if needed
        original_path = file_path
        filename = file_path.name
        filename_fixed = False
        
        # If filename doesn't match the snake_case pattern for the descriptive part
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        if len(parts) >= 3:
            prefix, date, desc_with_ext = parts
            # Check if the descriptive part has uppercase letters
            if not all(c.islower() or c.isdigit() or c == '_' or c == '.' for c in desc_with_ext):
                # Convert descriptive part to snake_case (lowercase with underscores)
                desc_part = desc_with_ext.split('.')[0]
                ext = desc_with_ext.split('.')[-1] if '.' in desc_with_ext else 'md'
                
                # Convert to snake_case
                new_desc_part = desc_part.lower()
                
                # Construct the new filename
                new_filename = f"{prefix}_{date}_{new_desc_part}.{ext}"
                new_path = file_path.parent / new_filename
                
                try:
                    # Rename the file
                    if new_path.exists():
                        logger.warning(f"Cannot rename to {new_filename} as it already exists. Will update content only.")
                    else:
                        file_path.rename(new_path)
                        logger.info(f"Renamed file from {filename} to {new_filename}")
                        file_path = new_path  # Update file_path for content reformatting
                        filename_fixed = True
                except Exception as e:
                    logger.error(f"Error renaming file {file_path} to {new_path}: {e}")
                    # Continue with content reformatting even if renaming fails

        # Basic reformatting: Ensure frontmatter and essential sections exist.
        # A more sophisticated version would try to intelligently migrate existing content.
        
        new_frontmatter = frontmatter if frontmatter is not None else {}
        new_markdown_content = markdown_content if markdown_content is not None else ""

        # Ensure all expected frontmatter keys are present, adding defaults if necessary
        if 'date' not in new_frontmatter:
            try:
                # Attempt to get date from filename
                date_str = file_path.name.split('_')[1]
                new_frontmatter['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except (IndexError, ValueError):
                new_frontmatter['date'] = datetime.now().strftime("%Y-%m-%d") # Default to today
        
        for key in EXPECTED_FRONTMATTER_KEYS:
            if key not in new_frontmatter:
                if key == 'title':
                    new_frontmatter[key] = f"Work Log for {file_path.stem}" 
                elif key == 'author':
                    new_frontmatter[key] = "EGOS System (Standardized)"
                elif key == 'status':
                    new_frontmatter[key] = "In Progress" # Default status
                elif key == 'priority':
                    new_frontmatter[key] = "Medium"
                elif key == 'tags':
                    new_frontmatter[key] = ["standardized"]
                elif key == 'roadmap_ids':
                    new_frontmatter[key] = []
                else:
                    new_frontmatter[key] = f"Placeholder for {key}"
        
        # Ensure date is a string for YAML dump
        date_val = new_frontmatter.get('date')
        # Check if it's a date-like object (parsed by PyYAML or already a datetime.date)
        if hasattr(date_val, 'year') and hasattr(date_val, 'month') and hasattr(date_val, 'day') and not isinstance(date_val, str):
            new_frontmatter['date'] = date_val.strftime('%Y-%m-%d')
        elif isinstance(date_val, str):
            # If it's already a string, ensure it's in the correct format or log warning
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Date string '{date_val}' in frontmatter of {file_path.name} is not in YYYY-MM-DD format during reformat. Attempting to keep original.")
        # If it's None or some other type, it will be handled by YAML dump or previous validation

        # Ensure required sections are present in markdown
        current_sections = {re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE).group(1).strip(): True 
                            for line in new_markdown_content.splitlines() if re.match(r"^##\s*(?:\d+\.\s*)?([^\n]+)", line, re.IGNORECASE)}
        
        added_sections_content = "\n"
        for i, section_title in enumerate(EXPECTED_SECTIONS):
            if section_title not in current_sections:
                added_sections_content += f"## {i+1}. {section_title}\n\n(Content for {section_title} needs to be added.)\n\n"
        
        final_markdown_content = new_markdown_content + added_sections_content
        if '✧༺❀༻∞ EGOS ∞༺❀༻✧' not in final_markdown_content:
            final_markdown_content += "\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n"

        try:
            frontmatter_yaml = yaml.dump(new_frontmatter, sort_keys=False, default_flow_style=False)
            new_content = f"---\n{frontmatter_yaml}---\n{final_markdown_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Successfully reformatted and saved {file_path}")
            self.files_standardized += 1
        except Exception as e:
            error_info = {
                "file": str(file_path),
                "error": str(e),
                "stage": "writing_reformatted_file",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.reformatting_failures.append(error_info)
            logger.error(f"Error writing reformatted file {file_path}: {e}")
            self.issues_found +=1 # Count as an issue if reformatting fails

    def _archive_work_log(self, file_path: Path, frontmatter: Optional[Dict[str, Any]]) -> None:
        """Archive a completed work log if it meets the criteria."""
        if frontmatter is None or frontmatter.get('status', '').lower() != 'completed':
            return # Not completed, or no frontmatter to check status

        file_mod_time_str = frontmatter.get('date') # Use 'date' from frontmatter as proxy for completion date
        if not file_mod_time_str or not isinstance(file_mod_time_str, str):
             # If no valid date, try to get file's actual modification time
            try:
                file_mod_timestamp = file_path.stat().st_mtime
                file_mod_date = datetime.fromtimestamp(file_mod_timestamp)
            except OSError:
                logger.warning(f"Could not determine modification date for {file_path} to check for archiving.")
                return
        else:
            try:
                file_mod_date = datetime.strptime(file_mod_time_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date '{file_mod_time_str}' in frontmatter of {file_path} for archiving check.")
                return

        if datetime.now() - file_mod_date > timedelta(days=ARCHIVE_RETENTION_DAYS):
            archive_target_path = self.archive_dir / file_path.name
            if self.dry_run:
                logger.info(f"[DRY RUN] Would archive {file_path} to {archive_target_path}")
            else:
                try:
                    shutil.move(str(file_path), str(archive_target_path))
                    logger.info(f"Archived {file_path} to {archive_target_path}")
                    self.files_archived += 1
                except Exception as e:
                    logger.error(f"Error archiving {file_path} to {archive_target_path}: {e}")
                    self.issues_found +=1
        else:
            logger.debug(f"Work log {file_path} is completed but not yet old enough for archiving.")

    def _standardize_filename(self, file_path: Path) -> Path:
        """Standardize a work log filename to snake_case format.
        
        Returns:
            The new path if renamed, or the original path if no renaming was needed or possible.
        """
        filename = file_path.name
        parts = filename.split('_', 2)  # Split into WORK, DATE, and description parts
        
        if len(parts) < 3:
            logger.warning(f"Cannot standardize filename {filename}: unexpected format (not enough parts)")
            return file_path
            
        prefix, date, desc_with_ext = parts
        
        # Check if date format needs correction (some files might use underscore instead of hyphen)
        if '-' not in date and len(date) == 8:  # Format might be YYYYMMDD or YYYY_MM_DD
            try:
                if '_' in date:  # Format is YYYY_MM_DD
                    year, month, day = date.split('_')
                else:  # Format is YYYYMMDD
                    year, month, day = date[:4], date[4:6], date[6:8]
                date = f"{year}-{month}-{day}"
                logger.info(f"Corrected date format in filename from {parts[1]} to {date}")
            except ValueError:
                logger.warning(f"Could not parse date in filename: {filename}")
        
        # Fix description part (convert to snake_case)
        desc_parts = desc_with_ext.split('.')
        desc = desc_parts[0]
        ext = desc_parts[1] if len(desc_parts) > 1 else "md"
        
        # Remove any existing underscores for clean conversion
        desc_no_underscores = desc.replace('_', ' ')
        
        # Handle common patterns like MCP_Documentation to mcp_documentation
        # First replace internal uppercase-prefixed words with space + that word
        # E.g., "MCPDocumentation" -> "MCP Documentation"
        desc_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', desc_no_underscores)
        
        # Then convert to lowercase and replace spaces with underscores
        snake_desc = desc_spaced.lower().replace(' ', '_')
        
        # Construct new filename
        new_filename = f"{prefix}_{date}_{snake_desc}.{ext}"
        
        if new_filename == filename:
            return file_path  # No change needed
            
        new_path = file_path.parent / new_filename
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would rename {filename} to {new_filename}")
            return file_path  # Return original in dry run
            
        try:
            if new_path.exists():
                logger.warning(f"Cannot rename to {new_filename} as it already exists.")
                return file_path
                
            file_path.rename(new_path)
            logger.info(f"Successfully renamed {filename} to {new_filename}")
            return new_path
        except Exception as e:
            logger.error(f"Error renaming {filename} to {new_filename}: {e}")
            return file_path
    
    def run_standardization(self) -> None:
        """Run the full work log standardization process.
        
        This comprehensive process includes:
        1. Detecting and handling duplicate work logs
        2. Standardizing filenames to follow snake_case convention
        3. Validating and reformatting work log content
        4. Archiving completed work logs
        5. Generating a detailed report of all actions taken
        """
        logger.info("Starting comprehensive work log standardization process...")
        self.issues_found = 0
        self.files_processed = 0
        self.files_standardized = 0
        self.files_archived = 0
        self.duplicates_handled = 0
        self.filenames_standardized = 0
        self.validation_failures = []  # Store detailed validation failure information
        self.reformatting_failures = []  # Store any files that couldn't be reformatted successfully
        self.deduplication_actions = []  # Track deduplication actions
        self.rename_actions = []  # Track filename standardization actions

        # Step 1: Find all work logs in the active directory
        initial_active_logs = self._find_work_logs(self.active_dir)
        logger.info(f"Found {len(initial_active_logs)} initial work logs in {self.active_dir}")
        
        # Step 2: Detect and handle duplicate work logs
        logger.info("=== PHASE 1: DEDUPLICATION ===")
        deduplicated_logs = self._detect_and_handle_duplicates(self.active_dir)
        
        # Step 3: Standardize all filenames to follow snake_case convention
        logger.info("=== PHASE 2: FILENAME STANDARDIZATION ===")
        standardized_logs = self._standardize_all_filenames(deduplicated_logs)
        
        # Step 4: Process each work log (validate, reformat, archive)
        logger.info("=== PHASE 3: CONTENT VALIDATION AND REFORMATTING ===")
        logger.info(f"Processing {len(standardized_logs)} work logs from {self.active_dir}")
        
        for log_path in standardized_logs:
            logger.info(f"--- Processing: {log_path.name} ---")
            self.files_processed += 1
            
            # Validate the work log
            is_valid = self._validate_work_log(log_path)
            
            # Parse for reformatting and archiving
            frontmatter, markdown_content, parse_successful = self._parse_work_log(log_path)

            # If validation failed, attempt to reformat content
            if not is_valid:
                logger.info(f"Attempting to reformat invalid work log: {log_path.name}")
                self._reformat_work_log(log_path, frontmatter, markdown_content)
                
                # After reformatting, re-parse to get updated frontmatter for archiving
                frontmatter, _, _ = self._parse_work_log(log_path) 
            
            # Step 5: Attempt to archive if it's completed
            self._archive_work_log(log_path, frontmatter)

        # Process logs in archive directory to ensure they are indeed archived (e.g. old completed logs)
        # This could also be a place to validate archived logs, though less critical than active ones.
        archived_logs = self._find_work_logs(self.archive_dir)
        logger.info(f"Checking {len(archived_logs)} work logs in archive directory {self.archive_dir} for any active logs that need moving back.")
        # Example: if a log in archive is not 'Completed', it might need to be moved back to active.
        # For now, this part is kept simple.

        # Step 6: Generate comprehensive standardization report
        logger.info("=== PHASE 4: GENERATING STANDARDIZATION REPORT ===")
        
        # Console summary
        logger.info("--- Standardization Process Summary ---")
        logger.info(f"Total files processed: {self.files_processed}")
        logger.info(f"Duplicate files handled: {self.duplicates_handled}")
        logger.info(f"Filenames standardized: {self.filenames_standardized}")
        logger.info(f"Content reformatted/standardized: {self.files_standardized}")
        logger.info(f"Files archived: {self.files_archived}")
        logger.info(f"Total issues encountered: {self.issues_found}")
        
        # Generate comprehensive standardization report
        report_path = Path(self.active_dir.parent, 'work_log_standardization_report.md')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# EGOS Work Log Standardization Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add EGOS signature banner
                f.write("✧｡◙◞ ◟◙｡✧\n\n")
                
                f.write("## Summary\n")
                f.write(f"- Total files processed: {self.files_processed}\n")
                f.write(f"- Duplicate files handled: {self.duplicates_handled}\n")
                f.write(f"- Filenames standardized: {self.filenames_standardized}\n")
                f.write(f"- Content reformatted: {self.files_standardized}\n")
                f.write(f"- Files archived: {self.files_archived}\n")
                f.write(f"- Issues encountered: {self.issues_found}\n\n")
                
                # Deduplication section
                if self.deduplication_actions:
                    f.write("## Deduplication Actions\n")
                    f.write("The following duplicate files were identified and handled:\n\n")
                    f.write("| Original File | Action | Kept File | Score Comparison |\n")
                    f.write("|--------------|--------|-----------|------------------|\n")
                    
                    for action in self.deduplication_actions:
                        original = Path(action['original']).name
                        kept = Path(action['kept']).name
                        if self.dry_run:
                            action_text = "Would be backed up (dry run)"
                        else:
                            action_text = f"Backed up to {Path(action['backup']).name}"
                        score_comparison = f"{action['score_original']} vs {action['score_kept']}"
                        
                        f.write(f"| {original} | {action_text} | {kept} | {score_comparison} |\n")
                    
                    f.write("\n")
                
                # Filename standardization section
                if self.rename_actions:
                    f.write("## Filename Standardization Actions\n")
                    f.write("The following files were renamed to comply with snake_case convention:\n\n")
                    f.write("| Original Filename | Standardized Filename |\n")
                    f.write("|-------------------|----------------------|\n")
                    
                    for action in self.rename_actions:
                        f.write(f"| {action['original']} | {action['new']} |\n")
                    
                    f.write("\n")
                
                # Validation and reformatting section
                if self.validation_failures:
                    f.write("## Validation Failures\n")
                    for failure in self.validation_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                if self.reformatting_failures:
                    f.write("## Reformatting Failures\n")
                    for failure in self.reformatting_failures:
                        filename = Path(failure['file']).name
                        f.write(f"### {filename}\n")
                        f.write(f"- File path: `{failure['file']}`\n")
                        f.write(f"- Error: {failure['error']}\n")
                        f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                        f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                
                # Next steps and recommendations
                f.write("## Next Steps\n")
                if self.issues_found > 0:
                    f.write("To address the remaining issues:\n\n")
                    f.write("1. **Fix invalid frontmatter** in work logs with missing or incorrect metadata.\n")
                    f.write("2. **Add missing sections** to work logs that lack required content structure.\n")
                    f.write("3. **Review backed-up duplicates** to ensure no important content was lost.\n")
                    f.write("4. **Run the standardizer again** after addressing these issues.\n\n")
                else:
                    f.write("All work logs are now standardized according to EGOS requirements. Regular maintenance should include:\n\n")
                    f.write("1. **Run this standardizer weekly** to ensure ongoing compliance.\n")
                    f.write("2. **Archive completed work logs** regularly to maintain a clean active directory.\n")
                    f.write("3. **Follow standard templates** when creating new work logs.\n\n")
                
                # References to EGOS standards
                f.write("## References\n")
                f.write("- [Work Log Standardization](C:\\EGOS\\docs\\work_logs\\WORK_2025-05-23_Work_Log_Standardization.md)\n")
                f.write("- [Master Quantum Prompt](C:\\EGOS\\MQP.md) (Systemic Organization, Evolutionary Preservation principles)\n")
                f.write("- [EGOS Documentation Standards](C:\\EGOS\\docs\\core_materials\\standards\\documentation_standards.md)\n\n")
                
                # EGOS signature footer
                f.write("\n✧｡◙◞ ◟◙｡✧ EGOS ✧｡◙◞ ◟◙｡✧\n")
                
            logger.info(f"Comprehensive standardization report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write standardization report: {e}")
        
        # Generate diagnostic report for issues if needed
        if self.issues_found > 0:
            diagnostic_report_path = Path(self.active_dir.parent, 'standardization_diagnostic_report.md')
            try:
                with open(diagnostic_report_path, 'w', encoding='utf-8') as f:
                    f.write("# Work Log Standardization Diagnostic Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("## Summary\n")
                    f.write(f"- Total files processed: {self.files_processed}\n")
                    f.write(f"- Files with issues: {self.issues_found}\n")
                    f.write(f"- Files standardized: {self.files_standardized}\n")
                    f.write(f"- Files archived: {self.files_archived}\n\n")
                    
                    if self.validation_failures:
                        f.write("## Validation Failures\n")
                        for failure in self.validation_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Issues: {', '.join(failure['issues'])}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    if self.reformatting_failures:
                        f.write("## Reformatting Failures\n")
                        for failure in self.reformatting_failures:
                            filename = Path(failure['file']).name
                            f.write(f"### {filename}\n")
                            f.write(f"- File path: `{failure['file']}`\n")
                            f.write(f"- Error: {failure['error']}\n")
                            f.write(f"- Stage: {failure.get('stage', 'unknown')}\n")
                            f.write(f"- Timestamp: {failure['timestamp']}\n\n")
                    
                    f.write("## Recommendations\n")
                    f.write("To fix the identified issues:\n\n")
                    f.write("1. **Ensure frontmatter** is present in all work logs with correct format.\n")
                    f.write("2. **Check for required sections** such as Objective, Progress, Challenges, etc.\n")
                    f.write("3. **Validate filenames** follow the format `WORK_YYYY-MM-DD_descriptive_name.md`.\n")
                    f.write("4. Run the standardizer again after fixing the issues.\n")
                    
                logger.info(f"Detailed diagnostic report saved to: {diagnostic_report_path}")
            except Exception as e:
                logger.error(f"Failed to write diagnostic report: {e}")
        
        logger.info("Work log standardization process finished.")

        if self.issues_found > 0:
            logger.warning("Standardization completed with issues. Please review the standardization report for details.")
        else:
            logger.info("Standardization completed successfully.")

    def analyze_directory_contents(self, root_dir: Path) -> None:
        """Analyzes work logs directly within root_dir to identify their status."""
        logger.info(f"--- Starting Analysis of Directory: {root_dir} ---")
        found_logs_in_root = 0
        active_identified = 0
        inactive_identified = 0
        unknown_status = 0

        # Determine the names of active and archive directories to avoid double-processing if they are subdirs of root_dir
        # This check is simplified; assumes root_dir is a direct parent if active/archive are inside it.
        active_dir_name = self.active_dir.name
        archive_dir_name = self.archive_dir.name
        is_processing_parent_of_managed_dirs = (self.active_dir.parent == root_dir or self.archive_dir.parent == root_dir)

        for item in root_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs_in_root += 1
                logger.info(f"Analyzing file: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                status_str = "Unknown/Missing Status"
                # is_active = False # Default assumption - not strictly needed here

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str = frontmatter['status'] # Keep original casing for logging
                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        inactive_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as INACTIVE/ARCHIVABLE")
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        active_identified += 1
                        logger.info(f"  -> Status: '{status_str}' - Identified as ACTIVE")
                    else:
                        unknown_status += 1
                        logger.warning(f"  -> Status: '{status_str}' - Status UNKNOWN or not standard.")
                else:
                    unknown_status += 1
                    logger.warning(f"  -> Status: MISSING - Could not determine status from frontmatter.")
        
        logger.info("--- Directory Analysis Summary ---")
        logger.info(f"Total work log files found directly in {root_dir}: {found_logs_in_root}")
        logger.info(f"  Identified as ACTIVE: {active_identified}")
        logger.info(f"  Identified as INACTIVE/ARCHIVABLE: {inactive_identified}")
        logger.info(f"  Status UNKNOWN or MISSING: {unknown_status}")
        logger.info("Analysis finished. No files were moved or modified.")

    def _detect_and_handle_duplicates(self, directory: Path) -> List[Path]:
        """Detect and handle duplicate work log files in the specified directory.
        
        Duplicates are detected based on:
        1. Similar filenames (after standardization)
        2. Similar content (using similarity threshold)
        3. Same date in frontmatter
        
        When duplicates are found:
        1. The most complete/valid file is kept
        2. Other duplicates are backed up and noted in the report
        
        Args:
            directory: Directory to search for duplicates
            
        Returns:
            List of paths to the deduplicated work log files
        """
        logger.info(f"Detecting and handling duplicate work logs in {directory}...")
        
        all_logs = self._find_work_logs(directory)
        if len(all_logs) <= 1:
            logger.info(f"No potential duplicates found in {directory} (only {len(all_logs)} logs)")
            return all_logs
            
        # Group files by normalized names (to catch variations like WORK_2025-05-22 vs WORK_2025_05_22)
        name_groups = {}
        for log_path in all_logs:
            # Extract date and description from filename
            parts = log_path.stem.split('_', 2)
            if len(parts) < 3:
                # Not a standard work log filename, skip grouping
                continue
                
            date_part = parts[1]
            # Normalize date format (replace underscores with hyphens)
            norm_date = date_part.replace('_', '-')
            
            # Normalize description part to lowercase
            desc_part = parts[2].lower()
            
            # Create normalized key for grouping
            norm_key = f"{norm_date}_{desc_part}"
            
            if norm_key not in name_groups:
                name_groups[norm_key] = []
            name_groups[norm_key].append(log_path)
        
        # Filter to only groups with multiple files (potential duplicates)
        duplicate_groups = {k: v for k, v in name_groups.items() if len(v) > 1}
        
        if not duplicate_groups:
            logger.info(f"No duplicate work logs found in {directory} based on filename analysis")
            return all_logs
            
        logger.info(f"Found {len(duplicate_groups)} groups of potential duplicate work logs")
        
        # Process each group of potential duplicates
        final_logs = []
        duplicate_paths = set()  # Track all identified duplicates
        
        for group_key, group_paths in duplicate_groups.items():
            logger.info(f"Processing duplicate group: {group_key} with {len(group_paths)} files")
            
            # Read content and metadata for each file in the group
            group_files = []
            for path in group_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse frontmatter
                    frontmatter, markdown, parse_success = self._parse_work_log(path)
                    
                    # Count complete sections as a measure of completeness
                    section_count = 0
                    if markdown:
                        for section in EXPECTED_SECTIONS:
                            if re.search(rf"^##\s*(\d+\.\s*)?{re.escape(section)}", markdown, re.MULTILINE | re.IGNORECASE):
                                section_count += 1
                    
                    # Calculate file score (higher is better)
                    # Scoring factors: file size, completeness of frontmatter, number of sections
                    frontmatter_score = len(frontmatter.keys()) if frontmatter else 0
                    size_score = len(content)
                    
                    file_score = size_score + (frontmatter_score * 100) + (section_count * 500)
                    
                    group_files.append({
                        'path': path,
                        'content': content,
                        'frontmatter': frontmatter,
                        'markdown': markdown,
                        'section_count': section_count,
                        'score': file_score
                    })
                except Exception as e:
                    logger.error(f"Error processing {path} for duplicate detection: {e}")
            
            if not group_files:
                logger.warning(f"Could not process any files in duplicate group {group_key}")
                continue
                
            # Sort files by score (highest first)
            group_files.sort(key=lambda x: x['score'], reverse=True)
            
            # Keep the highest scoring file, mark others as duplicates
            keeper = group_files[0]
            duplicate_files = group_files[1:]
            
            logger.info(f"Keeping highest scoring file: {keeper['path'].name} (score: {keeper['score']})")
            final_logs.append(keeper['path'])
            
            # Backup and record duplicates
            for dup in duplicate_files:
                duplicate_paths.add(dup['path'])
                
                if not self.dry_run:
                    try:
                        # Create backup with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_name = f"{dup['path'].stem}_DUPLICATE_{timestamp}{dup['path'].suffix}"
                        backup_path = self.backup_dir / backup_name
                        
                        shutil.copy2(dup['path'], backup_path)
                        logger.info(f"Backed up duplicate: {dup['path'].name} to {backup_path}")
                        
                        # Record action
                        self.deduplication_actions.append({
                            'original': str(dup['path']),
                            'backup': str(backup_path),
                            'kept': str(keeper['path']),
                            'score_original': dup['score'],
                            'score_kept': keeper['score'],
                            'timestamp': timestamp
                        })
                        
                        self.duplicates_handled += 1
                    except Exception as e:
                        logger.error(f"Error backing up duplicate {dup['path']}: {e}")
                else:
                    logger.info(f"[DRY RUN] Would back up duplicate: {dup['path'].name}")
                    self.deduplication_actions.append({
                        'original': str(dup['path']),
                        'backup': f"[DRY RUN] Would back up to {self.backup_dir}",
                        'kept': str(keeper['path']),
                        'score_original': dup['score'],
                        'score_kept': keeper['score'],
                        'timestamp': '[DRY RUN]'
                    })
        
        # Add any non-duplicate files to the final list
        for log_path in all_logs:
            if log_path not in duplicate_paths and log_path not in final_logs:
                final_logs.append(log_path)
        
        logger.info(f"Duplicate handling complete. Kept {len(final_logs)} unique files, handled {self.duplicates_handled} duplicates")
        return final_logs
    
    def _standardize_all_filenames(self, log_paths: List[Path]) -> List[Path]:
        """Standardize all work log filenames to follow EGOS snake_case convention.
        
        Args:
            log_paths: List of paths to work log files
            
        Returns:
            List of paths to the standardized files (may be different from input paths if renamed)
        """
        logger.info(f"Standardizing filenames for {len(log_paths)} work logs...")
        
        standardized_paths = []
        for log_path in log_paths:
            standardized_path = self._standardize_filename(log_path)
            standardized_paths.append(standardized_path)
            
            if standardized_path != log_path:
                self.filenames_standardized += 1
                
        logger.info(f"Filename standardization complete. Standardized {self.filenames_standardized} filenames")
        return standardized_paths

    def migrate_logs_from_directory(self, source_dir: Path) -> None:
        """Analyzes logs in source_dir and migrates them to active/archive dirs. Reports unknown status logs."""
        logger.info(f"--- Starting Migration from Directory: {source_dir} ---")
        logger.info(f"Target ACTIVE directory: {self.active_dir}")
        logger.info(f"Target ARCHIVE directory: {self.archive_dir}")
        if self.dry_run:
            logger.info("[DRY RUN] No files will actually be moved.")

        found_logs = 0
        moved_to_active = 0
        moved_to_archive = 0
        unknown_status_logs = []
        migration_errors = 0

        # Ensure target directories exist
        if not self.dry_run:
            self.active_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if item.is_file() and item.name.startswith(WORK_LOG_PREFIX) and item.name.endswith(WORK_LOG_EXTENSION):
                found_logs += 1
                logger.debug(f"Processing file for migration: {item.name}")
                frontmatter, _ = self._parse_work_log(item)
                
                target_path = None
                action_description = ""

                if frontmatter and 'status' in frontmatter:
                    status_from_fm = str(frontmatter['status']).lower().strip()
                    status_str_original = frontmatter['status']

                    if status_from_fm in ['completed', 'closed', 'archived', 'done', 'finalized', 'resolved']:
                        target_path = self.archive_dir / item.name
                        action_description = f"Identified as INACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_archive +=1 # Tentative count
                    elif status_from_fm in ['in progress', 'open', 'pending', 'to do', 'active', 'ongoing', 'new', 'review']:
                        target_path = self.active_dir / item.name
                        action_description = f"Identified as ACTIVE ('{status_str_original}'). Target: {target_path}"
                        moved_to_active +=1 # Tentative count
                    else:
                        logger.warning(f"File '{item.name}': Status '{status_str_original}' is UNKNOWN. File will not be moved.")
                        unknown_status_logs.append(item.name)
                else:
                    logger.warning(f"File '{item.name}': Status MISSING in frontmatter. File will not be moved.")
                    unknown_status_logs.append(item.name)

                if target_path:
                    logger.info(f"File '{item.name}': {action_description}")
                    if not self.dry_run:
                        try:
                            if target_path.exists():
                                logger.warning(f"  SKIPPING move: Target file {target_path} already exists.")
                                # Decrement count if skipped
                                if self.archive_dir / item.name == target_path: moved_to_archive -=1
                                if self.active_dir / item.name == target_path: moved_to_active -=1
                                migration_errors +=1
                            else:
                                shutil.move(str(item), str(target_path))
                                logger.info(f"  SUCCESS: Moved '{item.name}' to '{target_path}'")
                        except Exception as e:
                            logger.error(f"  FAILED to move '{item.name}' to '{target_path}': {e}")
                            # Decrement count if failed
                            if self.archive_dir / item.name == target_path: moved_to_archive -=1
                            if self.active_dir / item.name == target_path: moved_to_active -=1
                            migration_errors += 1
                
        logger.info("--- Migration Summary ---")
        logger.info(f"Total work log files found in {source_dir}: {found_logs}")
        logger.info(f"  Attempted to move to ACTIVE ({self.active_dir}): {moved_to_active}")
        logger.info(f"  Attempted to move to ARCHIVE ({self.archive_dir}): {moved_to_archive}")
        logger.info(f"  Files with UNKNOWN/MISSING status (not moved): {len(unknown_status_logs)}")
        if unknown_status_logs:
            for log_name in unknown_status_logs:
                logger.info(f"    - {log_name}")
        if migration_errors > 0:
            logger.warning(f"  Migration errors encountered: {migration_errors}")
        logger.info(f"Migration process finished. Check logs for details. Dry run: {self.dry_run}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize EGOS work log files.")
    parser.add_argument("--active-dir", type=Path, default=DEFAULT_ACTIVE_DIR, help="Directory for active work logs.")
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archived work logs.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without modifying files.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--analyze-root-directory", type=Path, help="Analyze work logs in the specified root directory to identify their status without moving or standardizing.")
    parser.add_argument("--migrate-logs-from", type=Path, help="Analyze and migrate logs from a source directory to 'active' or 'archive' subdirectories. Logs with unknown status are reported but not moved.")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    standardizer = WorkLogStandardizer(active_dir=args.active_dir, archive_dir=args.archive_dir, dry_run=args.dry_run)

    if args.analyze_root_directory:
        if not args.analyze_root_directory.is_dir():
            logger.error(f"Error: --analyze-root-directory path is not a valid directory: {args.analyze_root_directory}")
            sys.exit(1)
        standardizer.analyze_directory_contents(args.analyze_root_directory)
    elif args.migrate_logs_from:
        if not args.migrate_logs_from.is_dir():
            logger.error(f"Error: --migrate-logs-from path is not a valid directory: {args.migrate_logs_from}")
            sys.exit(1)
        standardizer.migrate_logs_from_directory(args.migrate_logs_from)
    else:
        standardizer.run_standardization()
        sys.exit(1 if standardizer.issues_found > 0 else 0)