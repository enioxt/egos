#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Docs Directory Fixer

This script addresses the issue of the old 'docs' directory reappearing after migration to 'docs_egos'.
It identifies references to the old directory, updates them to use the new directory structure,

Features:
- Identifies files to migrate, update, or delete
- Interactive conflict resolution with diff viewing
- Batch operations for handling multiple conflicts
- Reference path updating in migrated files
- Detailed logging and reporting
- Dry-run mode for safe testing

References:
- [EGOS Cross-Reference Standardization](../../docs_egos/05_development/standards/cross_reference_standard.md)
- [KOIOS Documentation Standards](../../docs_egos/02_koios_standards/documentation_standards.md)

Author: EGOS Development Team
Created: 2025-05-20
Version: 1.1.0

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

# Standard library imports
import os
import sys
import re
import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from datetime import datetime
import difflib
import time
import json

# Third-party imports
try:
    from tqdm import tqdm
except ImportError:
    # Fallback implementation for tqdm
    def tqdm(iterable, **kwargs):
        return iterable

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
DEFAULT_TIMEOUT = 30  # seconds

# Standardized report locations
REPORTS_DIR = Path("C:/EGOS/docs_egos/10_system_health/reports")
CROSSREF_REPORTS_DIR = REPORTS_DIR / "cross_reference"

# Configuration
CONFIG = {
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'docs_directory_fixer.log'),
    "log_level": "INFO",
    
    # Directory settings
    "old_docs_dir": "docs",
    "new_docs_dir": "docs_egos",
    
    # Git settings
    "git_hooks_dir": ".git/hooks",
    "pre_commit_hook": "pre-commit",
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

logger = logging.getLogger("docs_directory_fixer")

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

def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a command and return its output.
    
    Args:
        cmd: Command to run
        cwd: Working directory
        
    Returns:
        Tuple (return_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout, stderr = process.communicate(timeout=DEFAULT_TIMEOUT)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

class DirectoryMigrationTool:
    """Generic tool for comparing, migrating, and synchronizing directory structures.
    
    This class provides functionality to compare two directory structures, identify files
    that need to be migrated, updated, or deleted, and perform these operations with
    user-guided conflict resolution. It can also update references within files to reflect
    the new directory structure.
    
    Attributes:
        source_dir (Path): Path to the source directory
        target_dir (Path): Path to the target directory
        dry_run (bool): If True, don't actually make any changes
        report_dir (Path): Directory to store reports
        file_extensions (Set[str]): File extensions to process for reference updates
        exclude_dirs (Set[str]): Directories to exclude from processing
        exclude_patterns (List[str]): Regex patterns for paths to exclude
        stats (Dict[str, int]): Statistics about the migration process
        global_choice (Optional[str]): User's choice for handling all remaining conflicts
    """
    
    def __init__(self, 
                 source_dir: Union[str, Path], 
                 target_dir: Union[str, Path], 
                 dry_run: bool = True,
                 report_dir: Optional[Union[str, Path]] = None,
                 file_extensions: Optional[Set[str]] = None,
                 exclude_dirs: Optional[Set[str]] = None,
                 exclude_patterns: Optional[List[str]] = None,
                 reference_patterns: Optional[List[Tuple[str, str]]] = None):
        """Initialize the directory migration tool.
        
        Args:
            source_dir: Path to the source directory
            target_dir: Path to the target directory
            dry_run: If True, don't actually make any changes
            report_dir: Directory to store reports (defaults to target_dir/reports)
            file_extensions: File extensions to process for reference updates (defaults to common text files)
            exclude_dirs: Directories to exclude from processing (defaults to common exclusions)
            exclude_patterns: Regex patterns for paths to exclude
            reference_patterns: List of (pattern, replacement) tuples for updating references
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.dry_run = dry_run
        
        # Set default report directory if not provided
        if report_dir is None:
            self.report_dir = Path(target_dir) / "reports"
        else:
            self.report_dir = Path(report_dir)
        
        # Set default file extensions if not provided
        if file_extensions is None:
            self.file_extensions = {".md", ".txt", ".py", ".html", ".css", ".js", ".json", ".yaml", ".yml"}
        else:
            self.file_extensions = file_extensions
        
        # Set default exclude directories if not provided
        if exclude_dirs is None:
            self.exclude_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv"}
        else:
            self.exclude_dirs = exclude_dirs
        
        # Set default exclude patterns if not provided
        if exclude_patterns is None:
            self.exclude_patterns = [
                r".*\.git.*",
                r".*__pycache__.*",
                r".*\.pyc$",
                r".*\.DS_Store$"
            ]
        else:
            self.exclude_patterns = exclude_patterns
            
        # Set default reference patterns if not provided
        if reference_patterns is None:
            # Default pattern for updating references from source_dir to target_dir
            source_name = self.source_dir.name
            target_name = self.target_dir.name
            self.reference_patterns = [
                (f"{source_name}/", f"{target_name}/"),
                (f"/{source_name}/", f"/{target_name}/"),
                (f"../{source_name}/", f"../{target_name}/"),
            ]
        else:
            self.reference_patterns = reference_patterns
        
        # Statistics
        self.stats = {
            "files_migrated": 0,
            "files_updated": 0,
            "files_deleted": 0,
            "references_updated": 0,
            "errors": 0,
        }
        
        # Global choice for conflict resolution
        self.global_choice = None
        
        # Compile exclude patterns for faster matching
        self.exclude_pattern_regex = [re.compile(pattern) for pattern in self.exclude_patterns]

    def check_directories(self) -> bool:
        """Check if both directories exist.
        
        Returns:
            True if both directories exist, False otherwise
        """
        if not self.source_dir.exists():
            logger.error(f"Source directory {self.source_dir} does not exist.")
            return False
        
        if not self.target_dir.exists():
            logger.error(f"Target directory {self.target_dir} does not exist.")
            return False
        
        logger.info("Both directories exist. Will compare and migrate files.")
        return True
    
    def compare_directories(self) -> Dict[str, List[Path]]:
        """Compare source and target directories to identify files to migrate, update, or delete.
        
        Returns:
            Dictionary with lists of files to migrate, update, or delete
        """
        logger.info(f"Comparing directories: {self.source_dir} vs {self.target_dir}")
        
        # Files to process
        files_to_process = {
            "to_migrate": [],  # Files that exist in source but not in target
            "to_update": [],   # Files that exist in both but are different
            "to_delete": [],   # Files that exist in target but not in source (should be deleted)
        }
        
        # Walk through the source directory
        for root, dirs, files in os.walk(self.source_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            # Process files
            for file in files:
                source_file = Path(root) / file
                source_file_str = str(source_file)
                
                # Skip files matching exclude patterns
                if any(pattern.match(source_file_str) for pattern in self.exclude_pattern_regex):
                    continue
                
                rel_path = source_file.relative_to(self.source_dir)
                target_file = self.target_dir / rel_path
                
                # Check if the file exists in the target directory
                if target_file.exists():
                    # Check if the files are different
                    if not self._files_are_identical(source_file, target_file):
                        files_to_process["to_update"].append(source_file)
                else:
                    files_to_process["to_migrate"].append(source_file)
        
        # Walk through the target directory to find files to delete
        for root, dirs, files in os.walk(self.target_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            # Process files
            for file in files:
                target_file = Path(root) / file
                target_file_str = str(target_file)
                
                # Skip files matching exclude patterns
                if any(pattern.match(target_file_str) for pattern in self.exclude_pattern_regex):
                    continue
                
                rel_path = target_file.relative_to(self.target_dir)
                source_file = self.source_dir / rel_path
                
                # Check if the file exists in the source directory
                if not source_file.exists():
                    files_to_process["to_delete"].append(target_file)
        
        # Log results
        logger.info(f"Found {len(files_to_process['to_migrate'])} files to migrate")
        logger.info(f"Found {len(files_to_process['to_update'])} files to update")
        logger.info(f"Found {len(files_to_process['to_delete'])} files to delete")
        
        return files_to_process
    
    def _files_are_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are identical.
        
        Args:
            file1: Path to the first file
            file2: Path to the second file
            
        Returns:
            True if the files are identical, False otherwise
        """
        try:
            # Compare file sizes first (quick check)
            if file1.stat().st_size != file2.stat().st_size:
                return False
            
            # Compare file contents
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                # Read and compare in chunks to handle large files
                chunk_size = 8192  # 8KB chunks
                while True:
                    chunk1 = f1.read(chunk_size)
                    chunk2 = f2.read(chunk_size)
                    
                    if chunk1 != chunk2:
                        return False
                    
                    if not chunk1:  # End of file reached
                        break
            
            return True
        
        except Exception as e:
            logger.error(f"Error comparing files {file1} and {file2}: {str(e)}")
            return False
    
    def _get_file_stats(self, file_path: Path) -> Dict[str, str]:
        """Get file statistics for display.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file statistics
        """
        try:
            stats = os.stat(file_path)
            size = f"{stats.st_size:,} bytes"
            modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            return {
                'size': size,
                'modified': modified
            }
        except Exception as e:
            logger.error(f"Error getting stats for {file_path}: {str(e)}")
            return {
                'size': 'Unknown',
                'modified': 'Unknown'
            }
    
    def _show_diff(self, file1: Path, file2: Path) -> None:
        """Show diff between two files.
        
        Args:
            file1: First file
            file2: Second file
        """
        try:
            # Read file contents
            with open(file1, 'r', encoding='utf-8', errors='replace') as f1, \
                 open(file2, 'r', encoding='utf-8', errors='replace') as f2:
                content1 = f1.readlines()
                content2 = f2.readlines()
            
            # Generate diff
            diff = difflib.unified_diff(
                content1, content2,
                fromfile=str(file1),
                tofile=str(file2),
                lineterm=''
            )
            
            # Print diff with colors
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║ {Fore.YELLOW}File Difference{Fore.CYAN}                                          ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            for line in diff:
                if line.startswith('+'):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith('-'):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                elif line.startswith('^'):
                    print(f"{Fore.BLUE}{line}{Style.RESET_ALL}")
                elif line.startswith('@@'):
                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                else:
                    print(line)
            
            print("\nPress Enter to continue...")
            input()
            
        except Exception as e:
            logger.error(f"Error showing diff: {str(e)}")
            print(f"{Fore.RED}Error showing diff: {str(e)}{Style.RESET_ALL}")
            print("Press Enter to continue...")
            input()
    
    def _handle_file_conflict(self, file: Path, new_file: Path) -> None:
        """Handle conflict between two files.
        
        Args:
            file: Old file
            new_file: New file
        """
        # Prompt user for which version to keep
        if not self.dry_run:
            # Check if we have global choice settings
            if hasattr(self, 'global_choice') and self.global_choice:
                choice = self.global_choice
            else:
                # Prepare file comparison summary
                old_stats = self._get_file_stats(file)
                new_stats = self._get_file_stats(new_file)
                
                # Show file comparison with context
                print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.YELLOW}File Conflict Resolution{Fore.CYAN}                                  ║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Style.RESET_ALL}The following file exists in both directories with differences:{Fore.CYAN} ║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║{Style.RESET_ALL}                                                           {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.GREEN}Old:{Style.RESET_ALL} {file}{' ' * (54 - len(str(file)))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║      {Style.RESET_ALL}Last modified: {old_stats['modified']}{' ' * (40 - len(old_stats['modified']))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║      {Style.RESET_ALL}Size: {old_stats['size']}{' ' * (50 - len(old_stats['size']))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║{Style.RESET_ALL}                                                           {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.BLUE}New:{Style.RESET_ALL} {new_file}{' ' * (54 - len(str(new_file)))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║      {Style.RESET_ALL}Last modified: {new_stats['modified']}{' ' * (40 - len(new_stats['modified']))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║      {Style.RESET_ALL}Size: {new_stats['size']}{' ' * (50 - len(new_stats['size']))}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.YELLOW}Options:{Style.RESET_ALL}                                                  {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}o{Style.RESET_ALL} - Keep {Fore.GREEN}old{Style.RESET_ALL} version (overwrite new with old content)        {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}n{Style.RESET_ALL} - Keep {Fore.BLUE}new{Style.RESET_ALL} version (preserve new content)                {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}s{Style.RESET_ALL} - {Fore.YELLOW}Skip{Style.RESET_ALL} this file (leave both versions as they are)      {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}d{Style.RESET_ALL} - Show {Fore.MAGENTA}diff{Style.RESET_ALL} between versions                          {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}O{Style.RESET_ALL} - Keep {Fore.GREEN}old{Style.RESET_ALL} version for {Fore.RED}all{Style.RESET_ALL} remaining conflicts          {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}N{Style.RESET_ALL} - Keep {Fore.BLUE}new{Style.RESET_ALL} version for {Fore.RED}all{Style.RESET_ALL} remaining conflicts          {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║ {Fore.WHITE}S{Style.RESET_ALL} - {Fore.YELLOW}Skip{Style.RESET_ALL} {Fore.RED}all{Style.RESET_ALL} remaining conflicts                        {Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
                
                # Get user choice
                choice = input(f"{Fore.YELLOW}Enter your choice:{Style.RESET_ALL} ").strip()
                
                # Handle global choices and full word inputs
                if choice in ['O', 'N', 'S']:
                    logger.info(f"Setting global choice to {choice}")
                    self.global_choice = choice.lower()
                    choice = choice.lower()
                # Handle case where user types the full word
                elif choice.lower() == 'skip':
                    choice = 's'
                elif choice.lower() == 'skip all':
                    logger.info("Setting global choice to skip all")
                    self.global_choice = 's'
                    choice = 's'
                elif choice.lower() == 'keep new' or choice.lower() == 'new':
                    choice = 'n'
                elif choice.lower() == 'keep old' or choice.lower() == 'old':
                    choice = 'o'
                elif choice.lower() == 'keep new for all' or choice.lower() == 'new all':
                    logger.info("Setting global choice to keep new for all")
                    self.global_choice = 'n'
                    choice = 'n'
                elif choice.lower() == 'keep old for all' or choice.lower() == 'old all':
                    logger.info("Setting global choice to keep old for all")
                    self.global_choice = 'o'
                    choice = 'o'
                elif choice.lower() == 'diff':
                    choice = 'd'
                else:
                    choice = choice.lower()
            
            # Process the choice
            if choice == 'o':
                # Keep old version
                shutil.copy2(file, new_file)
                logger.info(f"Updated {new_file} with content from {file}")
                self.stats["files_migrated"] += 1
                return True
            elif choice == 'n':
                # Keep new version (do nothing)
                logger.info(f"Kept existing content in {new_file}")
                return True
            elif choice == 'd':
                # Show diff and prompt again
                self._show_diff(file, new_file)
                # Recursive call to handle this file again
                return self._handle_file_conflict(file, new_file)
            else:
                # Skip
                logger.info(f"Skipped {file}")
                return True
        else:
            logger.info(f"Would prompt for which version to keep: {file} vs {new_file}")
            return True
    
    def migrate_files(self, files_to_process: Dict[str, List[Path]]) -> None:
        """Migrate files from source directory to target directory.
        
        Args:
            files_to_process: Dictionary with lists of files to migrate, update, or delete
        """
        # Initialize global choice flag if not already set
        if not hasattr(self, 'global_choice') or self.global_choice is None:
            self.global_choice = None
        
        # Process files to migrate
        for file in tqdm(files_to_process["to_migrate"], desc="Migrating files", unit="files"):
            try:
                rel_path = file.relative_to(self.source_dir)
                target_file = self.target_dir / rel_path
                
                # Create parent directories if they don't exist
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                if not self.dry_run:
                    # Copy the file
                    shutil.copy2(file, target_file)
                    logger.info(f"Migrated {file} to {target_file}")
                    self.stats["files_migrated"] += 1
                else:
                    logger.info(f"Would migrate {file} to {target_file}")
            
            except Exception as e:
                logger.error(f"Error migrating {file}: {str(e)}")
                self.stats["errors"] += 1
        
        # Process files to update
        for file in tqdm(files_to_process["to_update"], desc="Updating files", unit="files"):
            try:
                rel_path = file.relative_to(self.source_dir)
                target_file = self.target_dir / rel_path
                
                # Handle file conflict
                self._handle_file_conflict(file, target_file)
            except Exception as e:
                logger.error(f"Error updating {file}: {str(e)}")
                self.stats["errors"] += 1
                
        # Process files to delete (if requested)
        if "to_delete" in files_to_process and files_to_process["to_delete"]:
            for file in tqdm(files_to_process["to_delete"], desc="Deleting files", unit="files"):
                try:
                    if not self.dry_run:
                        # Delete the file
                        file.unlink()
                        logger.info(f"Deleted {file}")
                        self.stats["files_deleted"] += 1
                    else:
                        logger.info(f"Would delete {file}")
                
                except Exception as e:
                    logger.error(f"Error deleting {file}: {str(e)}")
                    self.stats["errors"] += 1
    
    def update_references(self) -> int:
        """Update references in files to reflect the new directory structure.
        
        This method searches for references to the source directory in files and
        updates them to point to the target directory. It uses the reference patterns
        specified during initialization.
        
        Returns:
            Number of references updated
        """
        logger.info("Updating references...")
        references_updated = 0
        
        if self.dry_run:
            logger.info("Skipping reference updates in dry-run mode")
            return 0
        
        try:
            # Find all files that might contain references
            files_to_check = []
            for root, dirs, files in os.walk(self.target_dir):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Only process files with specified extensions
                    if file_path.suffix.lower() in self.file_extensions:
                        files_to_check.append(file_path)
            
            # Process files
            for file_path in tqdm(files_to_check, desc="Updating references", unit="files"):
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Apply reference patterns
                    updated_content = content
                    for pattern, replacement in self.reference_patterns:
                        updated_content = updated_content.replace(pattern, replacement)
                    
                    # If content changed, write it back
                    if updated_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        # Count updated references (approximate)
                        for pattern, _ in self.reference_patterns:
                            references_updated += content.count(pattern)
                        
                        logger.debug(f"Updated references in {file_path}")
                
                except Exception as e:
                    logger.error(f"Error updating references in {file_path}: {str(e)}")
                    self.stats["errors"] += 1
            
            # Update statistics
            self.stats["references_updated"] = references_updated
            logger.info(f"Updated {references_updated} references")
            
            return references_updated
        
        except Exception as e:
            logger.error(f"Error updating references: {str(e)}")
            return 0
    
    def setup_git_hook(self) -> bool:
        """Set up a Git pre-commit hook to prevent reintroduction of the old docs directory.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Setting up Git pre-commit hook...")
        
        # Check if .git directory exists
        git_dir = self.base_path / ".git"
        if not git_dir.exists() or not git_dir.is_dir():
            logger.error(f"Git directory {git_dir} does not exist. Cannot set up hook.")
            return False
        
        # Create hooks directory if it doesn't exist
        hooks_dir = self.base_path / CONFIG["git_hooks_dir"]
        os.makedirs(hooks_dir, exist_ok=True)
        
        # Path to pre-commit hook
        hook_path = hooks_dir / CONFIG["pre_commit_hook"]
        
        # Pre-commit hook content
        hook_content = """#!/bin/sh
#
# EGOS pre-commit hook to prevent reintroduction of the old docs directory
#

# Check if any added or modified files are in the old docs directory
if git diff --cached --name-only | grep -q "^docs/"; then
    echo "Error: Attempting to commit files in the old 'docs' directory."
    echo "Please use 'docs_egos' directory instead."
    echo "Run 'python scripts/cross_reference/docs_directory_fixer.py' for assistance."
    exit 1
fi

# Continue with the commit
exit 0
"""
        
        if not self.dry_run:
            try:
                # Write hook file
                with open(hook_path, 'w', newline='\n') as f:
                    f.write(hook_content)
                
                # Make hook executable
                os.chmod(hook_path, 0o755)
                
                logger.info(f"Git pre-commit hook set up at {hook_path}")
                return True
            
            except Exception as e:
                logger.error(f"Error setting up Git hook: {str(e)}")
                return False
        else:
            logger.info(f"Dry run: would set up Git pre-commit hook at {hook_path}")
            return True
    
    def update_gitignore(self) -> bool:
        """Update .gitignore to ignore the old docs directory.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Updating .gitignore...")
        
        # Path to .gitignore
        gitignore_path = self.base_path / ".gitignore"
        
        # Check if .gitignore exists
        if not gitignore_path.exists():
            if not self.dry_run:
                # Create .gitignore
                with open(gitignore_path, 'w', newline='\n') as f:
                    f.write(f"# Ignore old docs directory\n/docs/\n")
                
                logger.info(f"Created .gitignore with entry for /docs/")
                return True
            else:
                logger.info(f"Dry run: would create .gitignore with entry for /docs/")
                return True
        
        # Check if docs is already in .gitignore
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        if "/docs/" in content or "\ndocs/" in content or "docs\n" in content:
            logger.info("Old docs directory is already in .gitignore")
            return True
        
        if not self.dry_run:
            # Append to .gitignore
            with open(gitignore_path, 'a', newline='\n') as f:
                f.write(f"\n# Ignore old docs directory\n/docs/\n")
            
            logger.info(f"Updated .gitignore with entry for /docs/")
            return True
        else:
            logger.info(f"Dry run: would update .gitignore with entry for /docs/")
            return True
    
    def remove_old_directory(self) -> bool:
        """Remove the old docs directory.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.old_docs_dir.exists():
            logger.info(f"Old docs directory {self.old_docs_dir} does not exist. Nothing to remove.")
            return True
        
        if not self.dry_run:
            try:
                # Remove old docs directory
                shutil.rmtree(self.old_docs_dir)
                
                logger.info(f"Removed old docs directory {self.old_docs_dir}")
                return True
            
            except Exception as e:
                logger.error(f"Error removing old docs directory: {str(e)}")
                return False
    def generate_report(self) -> Path:
        """Generate a report of the migration.
        
        Returns:
            Path to the report file
        """
        # Create report directory if it doesn't exist
        if hasattr(self, 'report_dir') and self.report_dir:
            report_dir = self.report_dir
        else:
            report_dir = self.target_dir / "reports"
        
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create report file
        report_path = report_dir / f"directory_migration_{timestamp}.md"
        
        # Write report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Directory Migration Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Mode:** {'Dry Run (no files modified)' if self.dry_run else 'Live Run (files modified)'}\n\n")
            f.write(f"**Source Directory:** {self.source_dir}\n\n")
            f.write(f"**Target Directory:** {self.target_dir}\n\n")
            
            f.write(f"## Statistics\n\n")
            f.write(f"- **Files Migrated:** {self.stats['files_migrated']}\n")
            f.write(f"- **Files Updated:** {self.stats['files_updated']}\n")
            f.write(f"- **Files Deleted:** {self.stats['files_deleted']}\n")
            f.write(f"- **References Updated:** {self.stats['references_updated']}\n")
            f.write(f"- **Errors:** {self.stats['errors']}\n\n")
            
            f.write(f"## Next Steps\n\n")
            
            if self.dry_run:
                f.write(f"1. Review this report for any issues\n")
                f.write(f"2. Run the directory migration tool in live mode to apply the changes\n")
                f.write(f"3. Verify that all references have been updated correctly\n")
            else:
                f.write(f"1. Verify that all files have been migrated correctly\n")
                f.write(f"2. Verify that all references have been updated correctly\n")
                f.write(f"3. Remove the source directory if it is no longer needed\n")
        
        logger.info(f"Report generated at {report_path}")
        self.report_path = report_path
        
        return report_path

    def run(self) -> Path:
        """Run the directory migration tool.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Check if both directories exist
        if self.check_directories():
            # Compare directories
            files_to_process = self.compare_directories()
            
            # Migrate files
            self.migrate_files(files_to_process)
            
            # Update references
            self.update_references()
            
            # Set up Git hook
            self.setup_git_hook()
            
            # Update .gitignore
            self.update_gitignore()
            
            # Remove old directory
            self.remove_old_directory()
        
        # Generate report
        report_path = self.generate_report()
        
        # Update statistics
        self.stats["processing_time"] = time.time() - start_time
        
        return report_path

def main():
    # ... (rest of the code remains the same)
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Directory Comparison and Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Run in dry-run mode (no changes made)
  python docs_directory_fixer.py --source-dir docs --target-dir docs_egos --dry-run
  
  # Run in live mode (files will be modified)
  python docs_directory_fixer.py --source-dir docs --target-dir docs_egos
  
  # Run with custom report directory
  python docs_directory_fixer.py --source-dir docs --target-dir docs_egos --report-dir ./reports
  
  # Run with specific file extensions
  python docs_directory_fixer.py --source-dir docs --target-dir docs_egos --extensions .md .txt .py

This tool can be used for documentation migrations, codebase reorganizations, or any scenario
where files need to be compared and selectively migrated between directory structures.
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--source-dir", type=str, default="docs", help="Source directory path")
    parser.add_argument("--target-dir", type=str, default="docs_egos", help="Target directory path")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes made)")
    parser.add_argument("--report-dir", type=str, help="Directory to store reports")
    parser.add_argument("--extensions", type=str, nargs="*", help="File extensions to process for reference updates")
    parser.add_argument("--exclude-dirs", type=str, nargs="*", help="Directories to exclude from processing")
    parser.add_argument("--exclude-patterns", type=str, nargs="*", help="Regex patterns for paths to exclude")
    
    args = parser.parse_args()
    
    # Convert extensions to set if provided
    file_extensions = None
    if args.extensions:
        file_extensions = set(args.extensions)
    
    # Convert exclude_dirs to set if provided
    exclude_dirs = None
    if args.exclude_dirs:
        exclude_dirs = set(args.exclude_dirs)
    
    # Print banner
    mode_str = "Dry Run (no changes will be made)" if args.dry_run else "Live Run (files will be modified)"
    
    print_banner(
        "Directory Migration Tool",
        mode_str
    )
    
    try:
        # Create migration tool
        migration_tool = DirectoryMigrationTool(
            source_dir=args.source_dir,
            target_dir=args.target_dir,
            dry_run=args.dry_run,
            report_dir=args.report_dir,
            file_extensions=file_extensions,
            exclude_dirs=exclude_dirs,
            exclude_patterns=args.exclude_patterns
        )
        
        # Check if both directories exist
        if not migration_tool.check_directories():
            logger.error("One or both directories do not exist. Exiting.")
            return 1
        
        # Compare directories
        files_to_process = migration_tool.compare_directories()
        
        # Migrate files
        migration_tool.migrate_files(files_to_process)
        
        # Update references
        migration_tool.update_references()
        
        # Generate report
        report_path = migration_tool.generate_report()
        
        # Display summary statistics
        logger.info(f"\n{Fore.GREEN}Directory migration completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files migrated:{Style.RESET_ALL} {migration_tool.stats['files_migrated']:,}")
        logger.info(f"  • {Fore.CYAN}Files updated:{Style.RESET_ALL} {migration_tool.stats['files_updated']:,}")
        logger.info(f"  • {Fore.CYAN}Files deleted:{Style.RESET_ALL} {migration_tool.stats['files_deleted']:,}")
        logger.info(f"  • {Fore.CYAN}References updated:{Style.RESET_ALL} {migration_tool.stats['references_updated']:,}")
        logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {migration_tool.stats['errors']:,}")
        logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
        
        # Print next steps
        print("\nNext steps:")
        print(f"1. Review the report at {report_path}")
        if args.dry_run:
            print(f"2. Run the script without --dry-run to apply changes")
        print(f"3. Verify that all references have been updated correctly")
        
        return 0
    
    except KeyboardInterrupt:
        logger.error("\nOperation cancelled by user.")
        return 130
    
    except Exception as e:
        logger.error(f"\nError: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
        sys.exit(1)

# End of file
# ✧༺❀༻∞ EGOS ∞༺❀༻✧