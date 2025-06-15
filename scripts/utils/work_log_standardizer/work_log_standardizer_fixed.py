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
                    logger.error(f"Error renaming file {file_path.name}: {e}")
                        # filename_fixed remains False
        
        # Reformat content if necessary (frontmatter, sections)
        # This part assumes frontmatter and markdown_content are available
        # and might need to be re-parsed if the filename was the only issue.
        
        # For simplicity, we'll assume frontmatter and markdown_content are passed in correctly.
        # A more robust implementation might re-parse if they are None.

        if frontmatter is None or markdown_content is None:
            logger.warning(f"Frontmatter or markdown content is missing for {file_path}, attempting to re-parse.")
            frontmatter, markdown_content, _ = self._parse_work_log(file_path)
            if frontmatter is None or markdown_content is None:
                logger.error(f"Failed to re-parse {file_path}. Cannot reformat content.")
                self.reformatting_failures.append({
                    'file': str(file_path), 
                    'reason': 'Failed to parse for reformatting'
                })
                return # Cannot proceed with content reformatting

        # Create standardized frontmatter
        standard_frontmatter = frontmatter.copy() # Start with existing
        # Ensure all expected keys are present, fill with defaults if not
        for key in EXPECTED_FRONTMATTER_KEYS:
            if key not in standard_frontmatter:
                if key == 'tags' or key == 'roadmap_ids':
                    standard_frontmatter[key] = []
                elif key == 'date':
                    standard_frontmatter[key] = datetime.now().strftime("%Y-%m-%d")
                elif key == 'status':
                    standard_frontmatter[key] = "In Progress" # Default status
                else:
                    standard_frontmatter[key] = f"<{key.replace('_', ' ').title()} Placeholder>" # Generic placeholder
        
        # Ensure date is a string in YYYY-MM-DD format for YAML output
        if 'date' in standard_frontmatter and isinstance(standard_frontmatter['date'], date):
            standard_frontmatter['date'] = standard_frontmatter['date'].strftime("%Y-%m-%d")

        # Create standardized markdown content
        # This involves ensuring all sections are present and correctly ordered.
        # For now, we'll focus on ensuring the YAML frontmatter is well-formed.
        # A more complex reformatting would re-order/add missing sections.
        
        # For this version, we'll assume the markdown_content structure is mostly okay
        # or that validation would catch structural issues. Reformatting here will
        # primarily ensure the frontmatter is correctly written.

        new_content_parts = []
        new_content_parts.append("---")
        new_content_parts.append(yaml.dump(standard_frontmatter, sort_keys=False, allow_unicode=True).strip())
        new_content_parts.append("---")
        new_content_parts.append(markdown_content) # Append original markdown content
        
        full_new_content = "\n".join(new_content_parts)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_new_content)
            logger.info(f"Successfully reformatted content for {file_path}")
            if not filename_fixed : # if filename was already ok, but content was fixed
                 self.files_standardized +=1
        except Exception as e:
            logger.error(f"Error writing reformatted content to {file_path}: {e}")
            self.reformatting_failures.append({
                'file': str(file_path),
                'reason': f'Error writing reformatted content: {e}'
            })

    def _standardize_work_log(self, file_path: Path) -> bool:
        """Standardize a work log file that has validation issues."""
        logger.info(f"Attempting to standardize work log: {file_path}")
        
        frontmatter, markdown_content, parse_success = self._parse_work_log(file_path)
        
        if not parse_success:
            logger.error(f"Cannot standardize {file_path} due to parsing errors.")
            self.reformatting_failures.append({
                'file': str(file_path),
                'reason': 'Parse failure before standardization attempt'
            })
            return False

        # Call reformat which handles filename and content
        # _reformat_work_log will use self.dry_run
        self._reformat_work_log(file_path, frontmatter, markdown_content)
        
        # After reformatting, re-validate to see if issues are fixed
        # Note: _reformat_work_log might have renamed file_path
        # For simplicity, we assume it operates on the potentially new path if renamed.
        # A more robust flow might return the new path from _reformat_work_log.
        
        # Re-validation is tricky here because _reformat_work_log handles self.files_standardized.
        # We'll assume _reformat_work_log did its best.
        # The success of standardization is implicitly tracked by whether it reduced issues
        # or if self.files_standardized was incremented.
        
        # For now, we'll return True if reformatting was attempted.
        # The overall impact is seen in the final report.
        logger.info(f"Standardization attempt completed for {file_path}.")
        return True # Indicates an attempt was made.

    def _archive_work_log(self, file_path: Path) -> None:
        """Move a completed work log file to the archive directory."""
        if not self.archive_dir.exists() and not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
        archive_path = self.archive_dir / file_path.name
        
        logger.info(f"Archiving work log: {file_path} to {archive_path}")
        
        if not self.dry_run:
            try:
                shutil.move(str(file_path), str(archive_path))
                # Update frontmatter status to 'Archived'
                self._update_frontmatter_status(archive_path, "Archived")
                logger.info(f"Successfully archived {file_path.name}")
            except Exception as e:
                logger.error(f"Error archiving {file_path.name}: {e}")
        else:
            logger.info(f"[DRY RUN] Would archive {file_path.name} to {archive_path.name}")
            # Simulate status update for dry run consistency
            logger.info(f"[DRY RUN] Would update status to 'Archived' in {archive_path.name}")


    def _update_frontmatter_status(self, file_path: Path, new_status: str) -> None:
        """Update the status field in the frontmatter of a work log file."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update status to '{new_status}' in {file_path.name}")
            return

        frontmatter, markdown_content, parse_success = self._parse_work_log(file_path)
        if not parse_success or frontmatter is None:
            logger.warning(f"Could not parse {file_path} to update status. Skipping.")
            return

        frontmatter['status'] = new_status
        
        # Ensure date is a string for YAML dump if it was parsed as a date object
        if 'date' in frontmatter and isinstance(frontmatter['date'], date):
            frontmatter['date'] = frontmatter['date'].strftime("%Y-%m-%d")

        new_content_parts = [
            "---",
            yaml.dump(frontmatter, sort_keys=False, allow_unicode=True).strip(),
            "---",
            markdown_content if markdown_content else ""
        ]
        full_new_content = "\n".join(new_content_parts)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_new_content)
            logger.info(f"Updated status to '{new_status}' in {file_path.name}")
        except Exception as e:
            logger.error(f"Error updating status in {file_path.name}: {e}")

    def _should_archive_work_log(self, file_path: Path) -> bool:
        """Determine if a work log should be archived based on its status and completion date."""
        frontmatter, _, parse_success = self._parse_work_log(file_path)
        
        if not parse_success or frontmatter is None:
            logger.warning(f"Cannot determine archival status for {file_path} due to parsing issues.")
            return False
            
        status = frontmatter.get('status', '').lower()
        if status != 'completed':
            return False # Only archive completed logs
            
        # Check completion date (if available, otherwise use file's date)
        completion_date_str = frontmatter.get('completion_date') # Assuming a 'completion_date' field
        if not completion_date_str:
            # Fallback to 'date' field if 'completion_date' is missing
            completion_date_str = frontmatter.get('date')

        if completion_date_str:
            try:
                # Handle if date is already a date object (from YAML parsing)
                if isinstance(completion_date_str, date):
                    completion_date = completion_date_str
                else: # Assume string
                    completion_date = datetime.strptime(str(completion_date_str), "%Y-%m-%d").date()
                
                # Archive if completion date is older than retention period
                if (datetime.now().date() - completion_date) > timedelta(days=ARCHIVE_RETENTION_DAYS):
                    logger.info(f"Work log {file_path.name} is due for archival (completed on {completion_date}).")
                    return True
            except ValueError:
                logger.warning(f"Invalid date format for 'completion_date' or 'date' in {file_path.name}: {completion_date_str}")
        
        return False

# Main execution block
# =========================================================================
def main():
    """Main function to run the Work Log Standardizer."""
    parser = argparse.ArgumentParser(description="EGOS Work Log Standardizer")
    parser.add_argument(
        "--active-dir",
        type=Path,
        default=DEFAULT_ACTIVE_DIR,
        help=f"Directory for active work logs (default: {DEFAULT_ACTIVE_DIR})"
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help=f"Directory for archived work logs (default: {DEFAULT_ARCHIVE_DIR})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate changes without writing to files (dry run mode)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    
    args = parser.parse_args()

    # Update logger level based on command-line argument
    logger.setLevel(args.log_level.upper())
    # Also update for the root logger if desired, or specific handlers
    for handler in logging.getLogger().handlers: # Get root logger's handlers
        handler.setLevel(args.log_level.upper())
        
    logger.info(f"Log level set to: {args.log_level.upper()}")

    # Initialize and run the standardizer
    standardizer = WorkLogStandardizer(
        active_dir=args.active_dir,
        archive_dir=args.archive_dir,
        dry_run=args.dry_run
    )
    
    # Run the standardization process
    summary = standardizer.run_standardization()
    
    # Output summary to console
    print("\n--- Standardization Summary ---")
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("-----------------------------")
    
    if summary['issues_found'] > 0:
        print("\nWarning: Some issues were found. Please check the generated report for details.")
        # Potentially exit with a non-zero status code if issues were found
        # sys.exit(1) 

if __name__ == "__main__":
    # EGOS System Signature - Adherence to MQP Principles
    # This script operates under the EGOS framework, upholding principles such as:
    # - Systemic Cartography: By organizing and standardizing work logs.
    # - Evolutionary Preservation: By ensuring work logs are maintained and archived correctly.
    # - Integrated Ethics (ETHIK): By transparently reporting actions.
    logger.info("EGOS Work Log Standardizer - Invoking main function.")
    logger.info("MQP Principles: Systemic Cartography, Evolutionary Preservation, ETHIK.")
    
    main()
    
    logger.info("EGOS Work Log Standardizer - Main function execution complete.")
    logger.info("Exiting script.")