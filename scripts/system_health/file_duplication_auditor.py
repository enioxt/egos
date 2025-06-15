#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS File Duplication Auditor

This script identifies duplicate files across the EGOS system using a context-aware
approach to find duplicates based on file name, content hash, and semantic similarity.
It implements a robust caching mechanism for improved performance and generates
comprehensive reports in various formats.

The script provides multiple analysis modes:
1. Name-based identification (same filename in different locations)
2. Content-based identification (identical content in different files)
3. Similarity-based identification (similar content across files)
4. Context-aware identification (considers file purpose and location)

Author: EGOS System
Created: 2025-05-22
Version: 2.0.0
Updated: 2023-11-17

References:
    - C:\EGOS\docs\process\script_management_guidelines.md
    - C:\EGOS\docs\reference\python_coding_standards.mdc
    - C:\EGOS\docs\standards\file_organization.md
    - C:\EGOS\docs\standards\directory_structure.md
    - C:\EGOS\config\tool_registry.json
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
import re
import sys
import time
import json
import shutil
import hashlib
import logging
import argparse
import tempfile
import platform
import webbrowser
import fnmatch
import difflib
import math
import subprocess
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Iterator, Callable
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports
try:
    from tqdm import tqdm
except ImportError:
    # Simple tqdm alternative if tqdm is not installed
    def tqdm(iterable, *args, **kwargs):
        return iterable

# Configure colorama for cross-platform colored output
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
        
        def __getattr__(self, name):
            return ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    Fore = DummyColorama()
    Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
TERMINAL_WIDTH = 120
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_WORKERS = os.cpu_count() or 4
DEFAULT_TIMEOUT = 60  # seconds

# Define banner and signature constants
BANNER = """
╔═════════════════════════════════════════════════════════════════════════╗
║                  EGOS File Duplication Auditor                         ║
║                                                                       ║
║  Identifies duplicate files based on name, content, and context       ║
║  Generates comprehensive reports and helps maintain a clean codebase  ║
╚═════════════════════════════════════════════════════════════════════════╝
"""

EGOS_SIGNATURE = "✧༺❀༻∞ EGOS ∞༺❀༻✧"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('egos.file_auditor')

def print_styled_banner():
    """
    Print a stylized banner for the application.
    
    This function displays a visually formatted banner with the tool name and
    brief description, maintaining visual consistency with other EGOS tools.
    """
    print(f"{Fore.CYAN}{BANNER}{Style.RESET_ALL}")

def cleanup_temporary_scripts():
    """
    Clean up temporary scripts created during development.
    
    This function removes the temporary scripts created during the development
    process to avoid cluttering the scripts directory. It follows the EGOS
    Script Management Best Practices by maintaining a clean repository and
    ensuring there is a single source of truth for each functionality.
    
    References:
        - C:\EGOS\docs\process\script_management_guidelines.md
    """
    temp_scripts = [
        "simple_duplicate_detector.py",
        "detect_design_guide_duplicates.py"
    ]
    
    for script in temp_scripts:
        script_path = Path(__file__).parent / script
        if script_path.exists():
            try:
                logger.info(f"Removing temporary script: {script}")
                script_path.unlink()
                logger.info(f"Successfully removed temporary script: {script}")
            except PermissionError:
                logger.warning(f"Could not remove temporary script {script}: Permission denied")
            except FileNotFoundError:
                logger.warning(f"Could not find temporary script {script}")
            except Exception as e:
                logger.warning(f"Could not remove temporary script {script}: {e}")

# Configuration
CONFIG = {
    # Scanning settings
    "excluded_dirs": {
        ".git", "venv", "node_modules", "__pycache__", "dist", "build", 
        "target", "bin", "obj", ".vs", ".vscode", "reports", ".next", 
        "temp", "backup", "zz_archive", "archive"
    },
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "batch_size": DEFAULT_BATCH_SIZE,
    "max_workers": DEFAULT_MAX_WORKERS,
    "timeout": DEFAULT_TIMEOUT,
    "similarity_threshold": 0.8,  # 80% similarity for content comparison
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'file_duplication_auditor.log'),
    "log_level": "INFO",
    
    # Cache settings
    "cache_enabled": True,
    "cache_directory": "./cache",
    "cache_retention_days": 7,
    "system_cache_file": "file_system_cache.json",
    "hash_cache_file": "file_hash_cache.json",
    "context_aware_duplicates": True,  # Use context-aware duplicate detection
    "allow_multiple_copies": True,     # Allow files with identical content in different contexts
    
    # Reporting settings
    "generate_html": True,
    "generate_json": True,
    "generate_csv": True,
    "generate_markdown": True,
    "report_retention_days": 30,  # Number of days to keep reports
    
    # Integration settings
    "enable_cross_reference": True,  # Enable cross-reference integration
    "cross_reference_script": "scripts/cross_reference/optimized_reference_fixer.py",  # Path to cross-reference script
    "cross_reference_timeout": 120,  # Timeout for cross-reference operations in seconds
}

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CONFIG["log_file"])
    ]
)

logger = logging.getLogger("file_duplication_auditor")

def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner with title and optional subtitle."""
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


class FileInfo:
    """
    Class to store information about a file, including its content hash
    for quick comparison.
    """
    
    def __init__(self, path: Path, max_content_read_size: int = -1):
        """
        Initialize file information.
        
        Args:
            path: Path to the file
        """
        self.path = path
        self.size = path.stat().st_size
        self.name = path.name
        self.stem = path.stem
        self.suffix = path.suffix
        self.last_modified = datetime.fromtimestamp(path.stat().st_mtime)
        self.parent = path.parent
        self.relative_path = None  # To be set later
        self._content = None
        self._content_hash = None
        self.max_content_read_size = max_content_read_size  # Max size for loading full content
    
    @property
    def content(self) -> str:
        """
        Get the file content, loaded lazily.
        
        Returns:
            String content of the file
        """
        if self._content is None:
            if self.max_content_read_size != -1 and self.size > self.max_content_read_size:
                logger.warning(f"File {self.path} ({self.size} bytes) exceeds max_content_read_size ({self.max_content_read_size} bytes). Content not loaded for similarity.")
                self._content = "<CONTENT_TOO_LARGE_TO_LOAD>"
                return self._content
            try:
                with open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
                    self._content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {self.path}: {e}")
                self._content = "<CONTENT_READ_ERROR>"
        return self._content
    
    @property
    def content_hash(self) -> str:
        """
        Get a hash of the file content for quick comparison.
        
        Returns:
            MD5 hash of the file content or special marker for errors
        """
        if self._content_hash is None:
            # Handle zero-size files with a special hash
            if self.size == 0:
                logger.debug(f"Zero-size file detected: {self.path}")
                self._content_hash = "ZERO_SIZE_FILE_HASH"
                return self._content_hash
                
            try:
                hash_md5 = hashlib.md5()
                with open(self.path, 'rb') as f:
                    # Read in chunks to handle large files efficiently
                    for chunk in iter(lambda: f.read(4096), b''):
                        hash_md5.update(chunk)
                self._content_hash = hash_md5.hexdigest()
                logger.debug(f"Generated hash for {self.path}: {self._content_hash}")
            except PermissionError:
                logger.warning(f"Permission denied when hashing file {self.path}")
                self._content_hash = "<PERMISSION_ERROR>"
            except FileNotFoundError:
                logger.warning(f"File not found when hashing: {self.path}")
                self._content_hash = "<FILE_NOT_FOUND>"
            except Exception as e:
                logger.error(f"Error hashing file {self.path}: {e}")
                self._content_hash = "<HASH_ERROR>"
        return self._content_hash
    
    def similarity_ratio(self, other: 'FileInfo') -> float:
        """
        Calculate content similarity ratio between this file and another.
        
        Args:
            other: Another FileInfo object to compare with
            
        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        if not self.content or not other.content:
            return 0.0
        
        # Quick check if hashes match
        if self.content_hash == other.content_hash:
            return 1.0
        
        # Use difflib to compare content similarity
        return difflib.SequenceMatcher(None, self.content, other.content).ratio()
    
    def is_archive(self) -> bool:
        """
        Check if this file is in an archive directory.
        
        Returns:
            Boolean indicating if file is in an archive
        """
        path_str = str(self.path).lower()
        return any(segment in path_str for segment in ('archive', 'backup', '.git'))
    
    def is_documentation(self) -> bool:
        """
        Check if this file is likely documentation.
        
        Returns:
            Boolean indicating if file is likely documentation
        """
        if self.suffix.lower() in ('.md', '.txt', '.rst'):
            return True
        
        if 'doc' in self.path.parts or 'docs' in self.path.parts:
            return True
            
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with file information
        """
        return {
            'path': str(self.path),
            'relative_path': str(self.relative_path) if self.relative_path else None,
            'name': self.name,
            'size': self.size,
            'last_modified': self.last_modified.isoformat(),
            'is_archive': self.is_archive(),
            'is_documentation': self.is_documentation(),
            'content_hash': self.content_hash
        }
    
    def __str__(self) -> str:
        return f"{self.path} ({self.size} bytes, modified {self.last_modified})"


class DuplicateGroup:
    """
    Class to represent a group of duplicate files.
    """
    
    def __init__(self, name: str):
        """
        Initialize a duplicate group.
        
        Args:
            name: Name for this group of duplicates
        """
        self.name = name
        self.files: List[FileInfo] = []
        self.canonical_file: Optional[FileInfo] = None
        self.similarity_threshold: float = 0.9  # Default threshold
    
    def add_file(self, file: FileInfo) -> None:
        """
        Add a file to this group.
        
        Args:
            file: FileInfo object to add
        """
        self.files.append(file)
        
        # Refined canonical file selection logic
        if not self.canonical_file:
            self.canonical_file = file
        else:
            # Prefer non-archived files
            if file.is_archive() and not self.canonical_file.is_archive():
                pass # Current canonical is better (not archive)
            elif not file.is_archive() and self.canonical_file.is_archive():
                self.canonical_file = file # New file is better (not archive)
            else: # Both are archive or both are not archive
                # Prefer files in 'docs' or 'website' directories as a heuristic
                file_in_preferred_dir = any(part in str(file.path).lower() for part in ['docs', 'website'])
                canonical_in_preferred_dir = any(part in str(self.canonical_file.path).lower() for part in ['docs', 'website'])

                if file_in_preferred_dir and not canonical_in_preferred_dir:
                    self.canonical_file = file
                elif not file_in_preferred_dir and canonical_in_preferred_dir:
                    pass
                else: # Both in preferred or both not, or same preferred status
                    # Prefer shorter paths
                    if len(str(file.path)) < len(str(self.canonical_file.path)):
                        self.canonical_file = file
                    elif len(str(file.path)) == len(str(self.canonical_file.path)):
                        # Fallback to most recent if paths are equal length
                        if file.last_modified > self.canonical_file.last_modified:
                            self.canonical_file = file
    
    def get_total_size(self) -> int:
        """
        Get total size of all files in this group.
        
        Returns:
            Sum of file sizes in bytes
        """
        return sum(file.size for file in self.files)
    
    def get_wasted_space(self) -> int:
        """
        Calculate wasted space due to duplication.
        
        Returns:
            Sum of sizes of duplicate files (excluding canonical)
        """
        if not self.canonical_file or len(self.files) <= 1:
            return 0
        
        # More robust calculation that handles edge cases
        return sum(f.size for f in self.files if f != self.canonical_file and f.size == self.canonical_file.size)
    
    def calculate_similarities(self) -> List[Tuple[FileInfo, FileInfo, float]]:
        """
        Calculate similarity between all files in the group.
        
        Returns:
            List of tuples with (file1, file2, similarity_ratio)
        """
        similarities = []
        for i, file1 in enumerate(self.files):
            for file2 in self.files[i+1:]:
                similarity = file1.similarity_ratio(file2)
                similarities.append((file1, file2, similarity))
        return similarities
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with group information
        """
        return {
            'name': self.name,
            'file_count': len(self.files),
            'total_size': self.get_total_size(),
            'wasted_space': self.get_wasted_space(),
            'canonical_file': self.canonical_file.to_dict() if self.canonical_file else None,
            'files': [file.to_dict() for file in self.files]
        }
    
    def __str__(self) -> str:
        return f"Group '{self.name}' with {len(self.files)} files ({self.get_wasted_space()} bytes wasted)"


class FileAuditor:
    """
    Main class to audit files for duplication.
    
    This class provides functionality to scan directories for files, identify duplicates
    based on various criteria (name, content hash, content similarity), and generate
    comprehensive reports of the findings.
    
    Attributes:
        base_path: Base path for scanning
        excluded_dirs: Set of directory names to exclude from scanning
        max_depth: Maximum directory depth to scan
        pattern: Pattern to match filenames
        extensions: List of file extensions to focus on
        exclude_patterns: List of patterns to exclude from scanning
        min_size: Minimum file size to consider
        max_size: Maximum file size to consider
        similarity_threshold: Threshold for content similarity (0.0-1.0)
        max_file_size_for_content_read: Maximum file size to read for content comparison
        num_workers: Number of worker threads for parallel processing
        batch_size: Batch size for parallel processing
        timeout: Timeout in seconds for operations
        max_comparisons: Maximum number of file comparisons per extension
        verbose: Enable verbose output
    """
    
    def __init__(
        self,
        base_path: Path,
        excluded_dirs: Set[str] = None,
        max_depth: Optional[int] = None,
        pattern: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        min_size: int = 0,
        max_size: Optional[int] = None,
        similarity_threshold: float = 0.8,
        max_file_size_for_content_read: int = 10 * 1024 * 1024,  # 10MB
        num_workers: Optional[int] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        timeout: int = DEFAULT_TIMEOUT,
        max_comparisons: int = 10000,
        verbose: bool = False
    ):
        """
        Initialize the file auditor.
        
        Args:
            base_path: Base path for scanning
            excluded_dirs: Set of directory names to exclude from scanning
            max_depth: Maximum directory depth to scan
            pattern: Pattern to match filenames
            extensions: List of file extensions to focus on
            exclude_patterns: List of patterns to exclude from scanning
            min_size: Minimum file size to consider
            max_size: Maximum file size to consider
            similarity_threshold: Threshold for content similarity (0.0-1.0)
            max_file_size_for_content_read: Maximum file size to read for content comparison
            num_workers: Number of worker threads for parallel processing
            batch_size: Batch size for parallel processing
            timeout: Timeout in seconds for operations
            max_comparisons: Maximum number of file comparisons per extension
            verbose: Enable verbose output
        """
        self.base_path = base_path
        self.files: List[FileInfo] = []
        self.duplicate_groups: List[DuplicateGroup] = []
        
        # Configuration parameters
        self.excluded_dirs = excluded_dirs or {
            # Standard Python/Node/Git exclusions
            'venv', '.venv', 'env', '.env', '.git', '__pycache__',
            'node_modules', 'build', 'dist', 'site-packages',
            # IDE/Editor specific
            '.vs', '.vscode', '.idea',
            # EGOS specific / Common build/report/temp artifacts
            'reports', '.next', 'htmlcov', '.cursor', '.roo', '.obsidian',
            'temp', 'tmp', 'logs',
            # Backup/Archive patterns
            'backup', 'backups', 'archive', 'archived', 'old', 'legacy_root_backups',
            'zz_archive', 'temp_backups', '_temp_website_backup', '_website_backup',
            # Cache directories
            '.cache', 'cache'
        }
        
        # Path patterns to exclude (partial matching)
        self.excluded_path_patterns = exclude_patterns or [
            'legacy_root_backups',
            'temp_backups',
            '_website_backup',
            'zz_archive'
        ]
        
        # Processing parameters
        self.max_depth = max_depth
        self.pattern = pattern
        self.target_extensions = set(extensions) if extensions else set()
        self.min_size = min_size
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.max_file_size_for_content_read = max_file_size_for_content_read
        self.num_workers = num_workers if num_workers is not None else os.cpu_count() or 1
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_comparisons = max_comparisons
        self.verbose = verbose
    
    def scan_files(self, directory: Path, recursive: bool = True, use_cache: bool = True) -> None:
        """
        Scan a directory for files and add them to the files list.
        
        This method scans the specified directory for files, optionally using a cache
        to improve performance for subsequent scans. The cache stores file metadata
        including paths, sizes, and modification times.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            use_cache: Whether to use file system cache
        """
        logger.info(f"Scanning directory: {directory}")
        
        # Initialize cache if enabled
        cache_file = None
        cache_data = {}
        
        if use_cache and CONFIG.get("cache_enabled", False):
            cache_dir = Path(CONFIG.get("cache_directory", "./cache"))
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / CONFIG.get("system_cache_file", "file_system_cache.json")
            
            # Load existing cache if available
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    logger.info(f"Loaded file system cache from {cache_file}")
                except Exception as e:
                    logger.warning(f"Failed to load cache from {cache_file}: {e}")
        
        # Scan directory using cache where possible
        start_time = datetime.now()
        self._scan_directory(directory, recursive, cache_data)
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        # Update cache with newly scanned files
        if use_cache and CONFIG.get("cache_enabled", False) and cache_file:
            try:
                # Create new cache from current file list
                new_cache = {}
                for file_info in self.files:
                    new_cache[str(file_info.path)] = {
                        "size": file_info.size,
                        "mtime": file_info.last_modified.timestamp(),
                        "relative_path": str(file_info.relative_path) if file_info.relative_path else None
                    }
                
                # Write updated cache to file
                with open(cache_file, 'w') as f:
                    json.dump(new_cache, f)
                logger.info(f"Updated file system cache at {cache_file}")
            except Exception as e:
                logger.warning(f"Failed to update cache at {cache_file}: {e}")
        
        logger.info(f"Found {len(self.files)} files in {directory} (scan completed in {scan_duration:.2f} seconds)")
        
    def scan_system(self, root_dirs: List[Path] = None, exclude_patterns: List[str] = None) -> None:
        """
        Perform a comprehensive system-wide scan to identify all files.
        
        This method scans multiple root directories in a single operation,
        creating a complete file inventory for duplicate detection.
        
        Args:
            root_dirs: List of root directories to scan (defaults to C:\ if None)
            exclude_patterns: Additional patterns to exclude
        """
        logger.info("Starting system-wide file scan...")
        start_time = datetime.now()
        
        # Default to C:\ if no root directories specified
        if not root_dirs:
            # For safety, we'll use a more limited set of directories
            # Users can specify the full C:\ if needed
            root_dirs = [Path("C:\\EGOS")]
            logger.info(f"No root directories specified, defaulting to {root_dirs}")
        
        # Combine user exclude patterns with defaults
        all_exclude_patterns = self.excluded_path_patterns.copy()
        if exclude_patterns:
            all_exclude_patterns.extend(exclude_patterns)
        
        # Track total files found
        initial_file_count = len(self.files)
        
        # Scan each root directory
        for root_dir in root_dirs:
            try:
                logger.info(f"Scanning root directory: {root_dir}")
                self.scan_files(root_dir, recursive=True, use_cache=True)
            except Exception as e:
                logger.error(f"Error scanning {root_dir}: {e}")
        
        # Calculate statistics
        total_duration = (datetime.now() - start_time).total_seconds()
        new_files_found = len(self.files) - initial_file_count
        
        logger.info(f"System scan completed in {total_duration:.2f} seconds")
        logger.info(f"Found {new_files_found} files across {len(root_dirs)} root directories")
        logger.info(f"Total files in inventory: {len(self.files)}")
        
        # Print summary to console
        print(f"\nSystem scan completed in {total_duration:.2f} seconds")
        print(f"Found {new_files_found} files across {len(root_dirs)} root directories")
        print(f"Total files in inventory: {len(self.files)}")

    
    def _scan_directory(self, directory: Path, recursive: bool = True, cache_data: Dict = None) -> None:
        """
        Recursively scan a directory for files with optional cache support.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            cache_data: Optional cache data to speed up scanning
        """
        try:
            # Make sure we have an absolute path
            directory = directory.resolve()
            
            # Skip processing if directory doesn't exist or we can't access it
            if not directory.exists() or not os.access(directory, os.R_OK):
                logger.warning(f"Directory not accessible: {directory}")
                return
            
            for item in directory.iterdir():
                # Skip excluded directories
                if item.is_dir() and item.name in self.excluded_dirs:
                    continue
                    
                # Skip items matching excluded path patterns
                if any(pattern in str(item) for pattern in self.excluded_path_patterns):
                    continue
                    
                if item.is_dir() and recursive:
                    # Calculate current depth
                    if self.max_depth is not None:
                        current_depth = len(item.relative_to(directory).parts)
                        if current_depth >= self.max_depth:
                            continue
                    
                    # Recursive scan
                    self._scan_directory(item, recursive, cache_data)
                elif item.is_file():
                    # Skip files not matching pattern
                    if self.pattern and not fnmatch.fnmatch(item.name, self.pattern):
                        continue
                    
                    # Skip files not matching extensions
                    if self.target_extensions and item.suffix.lower().lstrip('.') not in self.target_extensions:
                        continue
                    
                    # Check file size
                    try:
                        file_stats = item.stat()
                        size = file_stats.st_size
                        if self.min_size is not None and size < self.min_size:
                            continue
                        if self.max_size is not None and size > self.max_size:
                            continue
                    except Exception as e:
                        logger.debug(f"Could not get stats for {item}: {e}")
                        continue
                    
                    # Check if we can use cached data
                    use_cached_info = False
                    if cache_data and str(item) in cache_data:
                        cached_entry = cache_data[str(item)]
                        # Only use cache if file hasn't changed since cache was created
                        if cached_entry.get('mtime') == file_stats.st_mtime and \
                           cached_entry.get('size') == size:
                            use_cached_info = True
                    
                    # Create file info object
                    file_info = FileInfo(item)
                    
                    # Set relative path
                    if hasattr(self, 'base_path') and self.base_path:
                        try:
                            file_info.relative_path = item.relative_to(self.base_path)
                        except ValueError:
                            # If we can't make a relative path, just use the full path
                            pass
                    elif directory:
                        try:
                            file_info.relative_path = item.relative_to(directory)
                        except ValueError:
                            pass
                    
                    # If we have cached info, set it
                    if use_cached_info and 'content_hash' in cached_entry:
                        file_info._content_hash = cached_entry['content_hash']
                    
                    # Add to our files list
                    self.files.append(file_info)
            
        except PermissionError:
            logger.warning(f"Permission denied accessing directory: {directory}")
        except FileNotFoundError:
            logger.warning(f"Directory not found: {directory}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            if self.verbose:
                import traceback
                logger.debug(traceback.format_exc())
    
    def find_duplicates_by_name(self) -> None:
        """
        Find duplicates based on filename.
        """
        logger.info("Finding duplicates by filename...")
        
        # Group files by name
        name_groups: Dict[str, List[FileInfo]] = {}
        for file in self.files:
            if file.name not in name_groups:
                name_groups[file.name] = []
            name_groups[file.name].append(file)
        
        # Create duplicate groups for files with the same name
        for name, files in tqdm(name_groups.items(), desc="Grouping by name", unit="group", leave=False):
            if len(files) > 1:
                group = DuplicateGroup(f"Name: {name}")
                for file in files:
                    group.add_file(file)
                self.duplicate_groups.append(group)
        
        logger.info(f"Found {len(self.duplicate_groups)} groups of files with duplicate names.")
    
    def find_duplicates_by_content(self, similarity_threshold: float = 0.9) -> None:
        """
        Find duplicates based on content similarity.
        
        This method implements a robust approach to identify duplicate files by
        content hash, regardless of filename or location. It uses efficient file
        reading with proper error handling to ensure accurate detection.
        
        Args:
            similarity_threshold: Threshold for considering files similar (0.0-1.0)
        """
        # Log start of operation
        logger.info(f"Finding duplicate files by content (threshold: {similarity_threshold})...")
        start_time = datetime.now()
        
        # Check if we can use a hash cache
        hash_cache_file = None
        hash_cache = {}
        
        if CONFIG.get("cache_enabled", False):
            cache_dir = Path(CONFIG.get("cache_directory", "./cache"))
            cache_dir.mkdir(parents=True, exist_ok=True)
            hash_cache_file = cache_dir / CONFIG.get("hash_cache_file", "file_hash_cache.json")
            
            # Load existing hash cache if available
            if hash_cache_file.exists():
                try:
                    with open(hash_cache_file, 'r') as f:
                        hash_cache = json.load(f)
                    logger.info(f"Loaded hash cache with {len(hash_cache)} entries from {hash_cache_file}")
                except Exception as e:
                    logger.warning(f"Failed to load hash cache from {hash_cache_file}: {e}")
        
        # Dictionary to map hash values to list of files
        file_hash_dict = {}
        
        # Track statistics
        processed_count = 0
        error_count = 0
        skipped_count = 0
        cache_hits = 0
        
        # Remember existing duplicate groups count
        initial_groups_count = len(self.duplicate_groups)
        
        # Process each file to compute hash
        for file_info in tqdm(self.files, desc="Computing content hashes", unit="file", 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'):
            # Skip zero-size files
            if file_info.size == 0:
                skipped_count += 1
                continue
                
            # Skip files we can't access
            if not os.path.exists(file_info.path) or not os.access(file_info.path, os.R_OK):
                logger.warning(f"Cannot access file: {file_info.path}")
                error_count += 1
                continue
            
            # Try to use cached hash if available and file hasn't changed
            file_path_str = str(file_info.path)
            use_cached_hash = False
            
            if file_path_str in hash_cache:
                cached_item = hash_cache[file_path_str]
                try:
                    stats = file_info.path.stat()
                    # Only use cache if file size and modification time match
                    if cached_item.get('size') == stats.st_size and \
                       cached_item.get('mtime') == stats.st_mtime:
                        hash_value = cached_item.get('hash')
                        use_cached_hash = True
                        cache_hits += 1
                except Exception:
                    pass
                
            # Compute hash if not cached or cache invalid
            if not use_cached_hash:
                try:
                    # Compute hash directly
                    md5_hash = hashlib.md5()
                    
                    with open(file_info.path, 'rb') as f:
                        # Use fixed chunk size for consistent performance
                        chunk_size = 8192  # 8KB chunks
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            md5_hash.update(chunk)
                    
                    # Get the final hash value
                    hash_value = md5_hash.hexdigest()
                    
                    # Update hash cache
                    if CONFIG.get("cache_enabled", False):
                        try:
                            stats = file_info.path.stat()
                            hash_cache[file_path_str] = {
                                'hash': hash_value,
                                'size': stats.st_size,
                                'mtime': stats.st_mtime
                            }
                        except Exception as e:
                            logger.debug(f"Could not cache hash for {file_path_str}: {e}")
                    
                except PermissionError:
                    logger.warning(f"Permission denied: {file_info.path}")
                    error_count += 1
                    continue
                except FileNotFoundError:
                    logger.warning(f"File not found: {file_info.path}")
                    error_count += 1
                    continue
                except Exception as e:
                    logger.error(f"Error processing file {file_info.path}: {e}")
                    error_count += 1
                    continue
            
            # Add to hash dictionary
            if hash_value not in file_hash_dict:
                file_hash_dict[hash_value] = []
            file_hash_dict[hash_value].append(file_info)
            
            # Cache the computed hash in the FileInfo object
            file_info._content_hash = hash_value
            processed_count += 1
        
        # Save updated hash cache
        if CONFIG.get("cache_enabled", False) and hash_cache_file:
            try:
                with open(hash_cache_file, 'w') as f:
                    json.dump(hash_cache, f)
                logger.info(f"Updated hash cache with {len(hash_cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to save hash cache to {hash_cache_file}: {e}")
        
        # Log hash computation statistics
        hash_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Hash computation completed in {hash_time:.1f} seconds")
        logger.info(f"Processed {processed_count} files, skipped {skipped_count}, errors {error_count}")
        logger.info(f"Cache hits: {cache_hits} ({cache_hits/max(1, processed_count+cache_hits)*100:.1f}%)")
        
        # Create duplicate groups from hash dictionary
        duplicate_group_count = 0
        
        # Process each hash group
        for hash_value, files in file_hash_dict.items():
            # Skip files with error hash codes
            if hash_value.startswith("<"):
                logger.debug(f"Skipping files with error hash: {hash_value}")
                continue
                
            if len(files) > 1:
                # Create a direct content-based group without context separation
                group_name = f"Content Group: {hash_value[:8]}"
                group = DuplicateGroup(group_name)
                
                for file_info in files:
                    group.add_file(file_info)
                
                # Select canonical file
                self._select_canonical_file(group)
                
                # Add to duplicate groups
                self.duplicate_groups.append(group)
                
                # For context awareness, we can add this as supplementary information
                if CONFIG.get("context_aware_duplicates", True):
                    # Create additional context-aware groups for reporting
                    context_groups = self._group_by_context(files)
                    for context_name, context_files in context_groups.items():
                        if len(context_files) > 1:
                            logger.debug(f"Context group: {context_name} has {len(context_files)} files")
                            # This information can be used for reporting but doesn't affect the primary duplication detection
                        
                        # Log summary of duplicate groups found
                        logger.info(f"Found {len(self.duplicate_groups)} duplicate groups with a total of {sum(len(g.files) for g in self.duplicate_groups)} files")
                        total_wasted = sum(g.get_wasted_space() for g in self.duplicate_groups)
                        logger.info(f"Total wasted space: {self._format_size(total_wasted)}")
                        
                        # Log detailed information for debugging
                        for i, group in enumerate(self.duplicate_groups, 1):
                            logger.debug(f"Group {i}: {group.name} - {len(group.files)} files")
                            for file_info in group.files:
                                status = "[CANONICAL]" if file_info == group.canonical_file else "[DUPLICATE]"
                                logger.debug(f"  {status} {file_info.path} ({self._format_size(file_info.size)})")
        
        # Calculate total statistics
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Count duplicate files (all files except one canonical per group)
        total_duplicates = sum(len(group.files) - 1 for group in self.duplicate_groups[initial_groups_count:])
        
        # Calculate wasted disk space
        wasted_space = 0
        for group in self.duplicate_groups[initial_groups_count:]:
            if group.canonical_file:
                # Each non-canonical file wastes space
                wasted_space += (len(group.files) - 1) * group.canonical_file.size
        
        # Log final results
        logger.info(f"Duplicate analysis completed in {total_time:.1f} seconds")
        logger.info(f"Found {duplicate_group_count} duplicate groups with identical content")
        logger.info(f"Total duplicate files: {total_duplicates}")
        logger.info(f"Wasted disk space: {self._format_size(wasted_space)}")
        
        # Also print summary to console
        print(f"\nFound {duplicate_group_count} duplicate groups with identical content")
        print(f"Total duplicate files: {total_duplicates}")
        print(f"Wasted disk space: {self._format_size(wasted_space)}")
        
    def _group_by_context(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Group files by context to determine logical duplicates.
        
        This method analyzes files with identical content hashes and determines
        whether they should be considered duplicates based on context such as:
        - File location (production vs. test vs. backup)
        - File purpose (code, documentation, data)
        - Logical organization (same subsystem or component)
        
        Args:
            files: List of files with identical content hashes
            
        Returns:
            Dictionary mapping context name to list of files in that context
        """
        context_groups = {}
        
        # Define context categories
        contexts = {
            "documentation": ["docs", "documentation", ".md", ".txt", "readme", "manual"],
            "source_code": [".py", ".js", ".java", ".c", ".cpp", ".h", ".cs", "src", "source"],
            "configuration": [".json", ".yaml", ".yml", ".ini", ".config", ".conf", "settings"],
            "data": ["data", ".csv", ".json", ".xml", ".db", ".sqlite"],
            "web": ["website", "web", ".html", ".css", ".js"],
            "tests": ["test", "tests", "spec", "specs"],
            "archive": ["archive", "backup", "old", "deprecated", "legacy"],
        }
        
        # First pass: Try to determine context by path and extension
        for file_info in files:
            path_str = str(file_info.path).lower()
            ext = file_info.suffix.lower()
            
            # Determine the context
            assigned_context = "other"  # Default
            
            # Check if in archive
            if any(term in path_str for term in contexts["archive"]):
                assigned_context = "archive"
            # Check various contexts
            elif any(term in path_str for term in contexts["documentation"]) or ext in [".md", ".txt", ".rst"]:
                assigned_context = "documentation"
            elif any(term in path_str for term in contexts["source_code"]) or ext in [".py", ".js", ".java", ".c", ".cpp"]:
                assigned_context = "source_code"
            elif any(term in path_str for term in contexts["configuration"]) or ext in [".json", ".yaml", ".yml", ".ini"]:
                assigned_context = "configuration"
            elif any(term in path_str for term in contexts["data"]) or ext in [".csv", ".json", ".xml"]:
                assigned_context = "data"
            elif any(term in path_str for term in contexts["web"]) or ext in [".html", ".css", ".js"]:
                assigned_context = "web"
            elif any(term in path_str for term in contexts["tests"]) or "test" in path_str:
                assigned_context = "tests"
            
            # Add to context group
            if assigned_context not in context_groups:
                context_groups[assigned_context] = []
            context_groups[assigned_context].append(file_info)
        
        # If we have a single context or very few files, just return as is
        if len(context_groups) <= 1 or len(files) <= 3:
            return {"general": files}
        
        # For cases with multiple contexts, refine based on additional factors
        final_groups = {}
        context_count = 1
        
        for context_name, context_files in context_groups.items():
            # If only one file in context, it's not a duplicate within this context
            if len(context_files) <= 1:
                continue
                
            # Consider file modification dates - group files modified within similar timeframes
            time_groups = self._group_by_modification_time(context_files)
            
            # Add each time group as a separate context
            for time_group_name, time_group_files in time_groups.items():
                if len(time_group_files) > 1:  # Only include groups with actual duplicates
                    group_name = f"{context_name}_{time_group_name}"
                    final_groups[group_name] = time_group_files
                    context_count += 1
        
        # If no groups were created after refinement, return the original files
        return final_groups if final_groups else {"general": files}
    
    def _group_by_modification_time(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Group files by modification time clusters.
        
        Args:
            files: List of files to group
            
        Returns:
            Dictionary mapping time group name to list of files
        """
        if len(files) <= 2:
            return {"same_time": files}
            
        # Extract modification times
        file_times = []
        for file_info in files:
            try:
                mtime = file_info.last_modified.timestamp()
                file_times.append((file_info, mtime))
            except Exception:
                # If we can't get mtime, use a default
                file_times.append((file_info, 0))
        
        # Sort by modification time
        file_times.sort(key=lambda x: x[1])
        
        # Group into clusters based on time gaps
        time_groups = {}
        current_group = "time_group_1"
        time_groups[current_group] = [file_times[0][0]]
        group_count = 1
        
        # Define what constitutes a significant time gap (1 day in seconds)
        time_threshold = 60 * 60 * 24
        
        for i in range(1, len(file_times)):
            current_file, current_time = file_times[i]
            previous_time = file_times[i-1][1]
            
            # If there's a significant time gap, start a new group
            if current_time - previous_time > time_threshold:
                group_count += 1
                current_group = f"time_group_{group_count}"
                time_groups[current_group] = []
                
            time_groups[current_group].append(current_file)
        
        return time_groups



    
    def _find_similar_content(self, threshold: float) -> None:
        """
        Find files with similar (but not identical) content.
        
        Args:
            threshold: Similarity threshold (0.0-1.0)
        """
        # This can be very computationally expensive for large numbers of files,
        # so we'll use several optimizations:
        # 1. Group by extension
        # 2. Filter by size similarity
        # 3. Use file name similarity as a heuristic
        # 4. Use parallel processing with batching
        
        # Group documentation files by extension
        doc_files_by_ext: Dict[str, List[FileInfo]] = {}
        for file in self.files:
            if file.is_documentation():
                if file.suffix not in doc_files_by_ext:
                    doc_files_by_ext[file.suffix] = []
                doc_files_by_ext[file.suffix].append(file)
        
        similar_group_count = len(self.duplicate_groups)
        
        # For each extension group, compare file contents
        for ext, files in tqdm(doc_files_by_ext.items(), desc="Analyzing similar content by extension", 
                               unit="ext", leave=False, 
                               bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'):
            if len(files) > 1:
                # Calculate similarities (this is the expensive part)
                similarities = []
                comparison_tasks = []
                
                # Sort files by size for more efficient comparisons
                files.sort(key=lambda f: f.size)
                
                # Create comparison tasks, using size as a filter
                # Files with very different sizes are unlikely to be similar
                for i, file1 in enumerate(files):
                    for j in range(i+1, len(files)):
                        file2 = files[j]
                        
                        # Skip if files are already in the same group
                        if any(file1 in group.files and file2 in group.files 
                               for group in self.duplicate_groups if group.name.startswith("Content Group")):
                            continue
                            
                        # Skip if size difference is too large (> 50%)
                        if file1.size > 0 and file2.size > 0:
                            size_ratio = min(file1.size, file2.size) / max(file1.size, file2.size)
                            if size_ratio < 0.5:  # Skip if sizes differ by more than 50%
                                continue
                        
                        # Use filename similarity as a heuristic
                        name_similarity = difflib.SequenceMatcher(None, file1.name, file2.name).ratio()
                        if name_similarity > 0.7:  # Prioritize files with similar names
                            comparison_tasks.insert(0, (file1, file2))  # Add to beginning of list
                        else:
                            comparison_tasks.append((file1, file2))

                # Limit the number of comparisons to avoid excessive processing
                max_comparisons = 10000  # Adjust based on performance needs
                if len(comparison_tasks) > max_comparisons:
                    logger.warning(f"Limiting comparisons for extension '{ext}' from {len(comparison_tasks)} to {max_comparisons}")
                    comparison_tasks = comparison_tasks[:max_comparisons]

                if comparison_tasks:
                    total_tasks = len(comparison_tasks)
                    logger.info(f"Comparing {total_tasks} pairs in extension '{ext}' using {self.num_workers} workers.")
                    
                    # Process in batches to show better progress and avoid memory issues
                    batch_size = min(1000, total_tasks)  # Adjust based on memory constraints
                    num_batches = (total_tasks + batch_size - 1) // batch_size
                    
                    with tqdm(total=total_tasks, desc=f"Comparing files in ext {ext}", 
                              unit="pair", leave=False,
                              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                        
                        for batch_idx in range(num_batches):
                            start_idx = batch_idx * batch_size
                            end_idx = min(start_idx + batch_size, total_tasks)
                            batch_tasks = comparison_tasks[start_idx:end_idx]
                            
                            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                                future_to_pair = {executor.submit(file1.similarity_ratio, file2): (file1, file2) 
                                                  for file1, file2 in batch_tasks}
                                
                                for future in as_completed(future_to_pair):
                                    try:
                                        similarity = future.result(timeout=self.timeout)
                                        pair = future_to_pair[future]
                                        
                                        if similarity >= threshold:
                                            # Create a new group or add to existing
                                            self._add_similar_files(pair[0], pair[1], similarity)
                                        
                                        pbar.update(1)
                                    except Exception as e:
                                        logger.error(f"Error comparing files: {e}")
                                        pbar.update(1)
                    

        return True
    
    def _add_similar_files(self, file1: FileInfo, file2: FileInfo, similarity: float) -> None:
        """
        Add two similar files to a duplicate group or create a new group.
        
        Args:
            file1: First file
            file2: Second file
            similarity: Similarity ratio between the files
        """
        # Check if either file is already in a group
        existing_group = None
        
        for group in self.duplicate_groups:
            if file1 in group.files or file2 in group.files:
                existing_group = group
                break
        
        if existing_group:
            # Add files to existing group if not already present
            if file1 not in existing_group.files:
                existing_group.add_file(file1)
            if file2 not in existing_group.files:
                existing_group.add_file(file2)
        else:
            # Create a new group
            group_name = f"Similar: {file1.name} and {file2.name}"
            new_group = DuplicateGroup(group_name)
            new_group.add_file(file1)
            new_group.add_file(file2)
            new_group.similarity_threshold = similarity
            self.duplicate_groups.append(new_group)
            
            # Select canonical file based on various criteria
            self._select_canonical_file(new_group)
    
    def _select_canonical_file(self, group: DuplicateGroup) -> None:
        """
        Select the canonical file for a duplicate group based on various criteria.
        
        This method implements a sophisticated selection algorithm that considers:
        1. Non-archived files are preferred over archived files
        2. Files in preferred directories are prioritized
        3. Files with shorter paths are preferred (typically closer to project root)
        4. More recently modified files are preferred
        5. Documentation files are preferred over non-documentation files
        
        Args:
            group: The duplicate group to select a canonical file for
        """
        if not group.files:
            return
        
        # If only one file, it's automatically canonical
        if len(group.files) == 1:
            group.canonical_file = group.files[0]
            return
        
        # Define preferred directories (order matters)
        preferred_dirs = [
            "docs",
            "docs/reference",
            "docs/standards",
            "docs/subsystems",
            "docs/process",
            "README"
        ]
        
        # Score each file based on multiple criteria
        file_scores = []
        
        for file in group.files:
            score = 0
            
            # Criterion 1: Non-archived files are preferred
            if not file.is_archive():
                score += 100
            
            # Criterion 2: Files in preferred directories
            path_str = str(file.path).lower()
            for i, preferred_dir in enumerate(preferred_dirs):
                if preferred_dir.lower() in path_str:
                    # Higher score for earlier entries in the preferred_dirs list
                    score += 50 * (len(preferred_dirs) - i)
                    break
            
            # Criterion 3: Shorter paths are preferred
            path_length = len(str(file.path))
            score -= path_length * 0.1  # Small penalty for longer paths
            
            # Criterion 4: More recent files are preferred
            # Convert to timestamp and normalize to a reasonable range
            timestamp = file.last_modified.timestamp()
            current_time = datetime.now().timestamp()
            time_diff = current_time - timestamp  # Seconds since last modification
            max_time_diff = 60 * 60 * 24 * 365 * 2  # 2 years in seconds
            normalized_time_score = max(0, 1 - (time_diff / max_time_diff))
            score += normalized_time_score * 20  # Up to 20 points for recency
            
            # Criterion 5: Documentation files are preferred
            if hasattr(file, 'is_documentation') and file.is_documentation():
                score += 30
            
            file_scores.append((file, score))
        
        # Sort by score (descending) and select the highest-scoring file
        file_scores.sort(key=lambda x: x[1], reverse=True)
        group.canonical_file = file_scores[0][0]
        
        logger.debug(f"Selected canonical file for group '{group.name}': {group.canonical_file.path} (score: {file_scores[0][1]})")
    
    def _generate_html_report_content(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML report content for duplicate files."""
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        script_version = "1.0.0"  # Default version
        try:
            if 'CONFIG' in globals() and isinstance(CONFIG, dict):
                script_version = CONFIG.get("version", script_version)
            elif hasattr(self, 'config') and isinstance(self.config, dict):
                script_version = self.config.get("version", script_version)
        except Exception as e:
            logger.warning(f"Could not determine script version from CONFIG or self.config: {e}. Using default: {script_version}")
        
        # Prepare data for HTML template
        wasted_space_bytes = analysis.get('wasted_space', 0)
        wasted_space_human = self._format_size(wasted_space_bytes)
        wasted_space_bytes_str = f"{wasted_space_bytes:,}"
        
        # Prepare groups HTML
        groups_html = ""
        actual_duplicate_groups = [g for g in analysis.get('groups', []) if len(g.get('files', [])) > 1]
        
        for i, group in enumerate(actual_duplicate_groups):
            canonical_path = "N/A"
            if group.get('canonical_file'):
                canonical_path = group['canonical_file'].get('path', 'N/A')
            
            files_html = "<table>\n"
            files_html += "<thead><tr><th>File Path</th><th>Size</th><th>Last Modified</th><th>Status</th></tr></thead>\n<tbody>\n"
            
            for file_info in group['files']:
                status = "Canonical" if file_info['path'] == canonical_path else "Duplicate"
                status_class = "canonical" if status == "Canonical" else "duplicate"
                
                files_html += f"<tr>\n"
                files_html += f"  <td class='file-path'>{file_info['path']}</td>\n"
                files_html += f"  <td>{self._format_size(file_info['size'])}</td>\n"
                files_html += f"  <td>{file_info['last_modified']}</td>\n"
                files_html += f"  <td class='{status_class}'>{status}</td>\n"
                files_html += f"</tr>\n"
            
            files_html += "</tbody></table>"
            
            group_html = f"""
                <div class="duplicate-group">
                    <div class="group-header">
                        <h3>Group {i+1}</h3>
                        <p><strong>Files:</strong> {len(group['files'])}</p>
                        <p><strong>Wasted Space:</strong> {self._format_size(group['wasted_space'])}</p>
                        <p><strong>Canonical File:</strong> <span class="canonical">{canonical_path}</span></p>
                    </div>
                    <div class="group-content">
                        {files_html}
                    </div>
                </div>
            """
            
            groups_html += group_html
        
        # Complete HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGOS File Duplication Report</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; background-color: #f4f4f4; }
        h1, h2, h3 { color: #2c3e50; }
        .container { max-width: 1200px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .summary { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ced4da; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .file-path { font-family: monospace; word-break: break-all; }
        .canonical { color: #28a745; font-weight: bold; }
        .duplicate { color: #dc3545; }
        .duplicate-group { border: 1px solid #ddd; margin-bottom: 20px; border-radius: 4px; overflow: hidden; }
        .group-header { background-color: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; }
        .group-content { padding: 15px; }
        .recommendations { background-color: #e9ecef; padding: 15px; border-radius: 4px; margin-top: 30px; }
        .egos-signature { text-align: center; margin-top: 30px; color: #6c757d; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>EGOS File Duplication Report</h1>
        <p>Generated on {timestamp} | Script Version: {script_version}</p>
        <p>Base Directory: {base_directory}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Files Scanned:</strong> {total_files}</p>
            <p><strong>Duplicate Groups Found:</strong> {duplicate_groups_count}</p>
            <p><strong>Total Duplicate Files:</strong> {total_duplicates}</p>
            <p><strong>Wasted Space:</strong> {wasted_space_human} ({wasted_space_bytes_str} bytes)</p>
        </div>
        
        <h2>Duplicate Groups</h2>
        {groups_html}
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            <ul>
                <li>Review and consolidate documentation files to their canonical locations</li>
                <li>Update cross-references to point to canonical file locations</li>
                <li>Consider archiving or removing duplicate files in non-standard locations</li>
                <li>Run the cross-reference validator after cleanup to ensure all references remain valid</li>
            </ul>
        </div>
        
        <div class="egos-signature">✧༺❀༻∞ EGOS ∞༺❀༻✧</div>
    </div>
</body>
</html>
"""
        
        html_content = html_template.format(
            timestamp=current_timestamp,
            base_directory=str(self.base_path) if hasattr(self, 'base_path') else 'N/A',
            total_files=f"{len(self.files) if hasattr(self, 'files') else 0:,}",
            duplicate_groups_count=f"{len(actual_duplicate_groups):,}",
            total_duplicates=f"{analysis.get('total_duplicates', 0):,}",
            wasted_space_bytes_str=wasted_space_bytes_str,
            wasted_space_human=wasted_space_human,
            groups_html=groups_html,
            script_version=script_version
        )
        
        return html_content
    
    def _manage_report_retention(self, report_dir: Path, retention_days: int = 30) -> None:
        """
        Clean up old reports to manage storage.
        
        This method deletes reports older than the specified number of days.
        It follows the EGOS standard for report management as specified in the
        project documentation.
        
        Args:
            report_dir: Directory containing reports
            retention_days: Number of days to keep reports (older reports will be deleted)
        """
        if not report_dir.exists() or not report_dir.is_dir():
            logger.warning(f"Report directory {report_dir} does not exist or is not a directory")
            return
        
        logger.info(f"Checking for reports older than {retention_days} days in {report_dir}")
        
        # Get current time
        current_time = datetime.now()
        
        # Define report file patterns
        report_patterns = [
            "duplication_report_*.html",
            "duplication_report_*.json",
            "duplication_report_*.csv",
            "duplication_report_*.md"
        ]
        
        # Track statistics
        deleted_count = 0
        total_size_freed = 0
        
        # Process each pattern
        for pattern in report_patterns:
            # Find all matching files
            for report_file in report_dir.glob(pattern):
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                    
                    # Calculate age in days
                    age_days = (current_time - mod_time).days
                    
                    # Delete if older than retention period
                    if age_days > retention_days:
                        # Get file size before deleting
                        file_size = report_file.stat().st_size
                        
                        # Delete file
                        report_file.unlink()
                        
                        # Update statistics
                        deleted_count += 1
                        total_size_freed += file_size
                        
                        logger.debug(f"Deleted old report: {report_file} (Age: {age_days} days)")
                except Exception as e:
                    logger.warning(f"Error processing report file {report_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old reports, freed {self._format_size(total_size_freed)} of space")
        else:
            logger.info(f"No reports older than {retention_days} days found")
    
    def update_cross_references(self, canonical_file: Path, duplicate_files: List[Path]) -> bool:
        """
        Update cross-references to point to the canonical file.
        
        This method integrates with the EGOS cross-reference system to update
        references to duplicate files to point to the canonical file instead.
        
        Args:
            canonical_file: The canonical file path
            duplicate_files: List of duplicate file paths to update references for
            
        Returns:
            True if cross-references were updated successfully, False otherwise
        """
        if not CONFIG.get("enable_cross_reference", False):
            logger.info("Cross-reference integration is disabled")
            return False
            
        cross_ref_script = CONFIG.get("cross_reference_script")
        if not cross_ref_script or not Path(cross_ref_script).exists():
            logger.warning(f"Cross-reference script not found: {cross_ref_script}")
            return False
            
        logger.info(f"Updating cross-references for {len(duplicate_files)} duplicate files")
        
        try:
            # Prepare arguments for cross-reference script
            args = [
                sys.executable,
                str(cross_ref_script),
                "--source-files", ",".join(str(f) for f in duplicate_files),
                "--target-file", str(canonical_file),
                "--update-references",
                "--verbose"
            ]
            
            # Run cross-reference script
            timeout = CONFIG.get("cross_reference_timeout", 120)
            logger.info(f"Running cross-reference script: {' '.join(args)}")
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Cross-references updated successfully:\n{result.stdout}")
                return True
            else:
                logger.error(f"Cross-reference update failed with code {result.returncode}:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Cross-reference update timed out after {timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Error updating cross-references: {e}")
            return False
    
    def _format_size_with_unit(self, size_in_bytes: int) -> Tuple[str, str]:
        """
        Format file size in human-readable format and return the value and unit separately.
        
{{ ... }}
        Args:
            size_in_bytes: Size in bytes
            
        Returns:
            Tuple of (formatted size value, unit)
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f}", unit
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f}", "PB"
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append("    <meta charset='UTF-8'>")
        html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_parts.append(f"    <title>File Duplication Report - {timestamp}</title>")
        html_parts.append("    <style>")
        html_parts.append("        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; background-color: #f4f4f4; }")
        html_parts.append("        .container { max-width: 1200px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }")
        html_parts.append("        h1, h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }")
        html_parts.append("        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }")
        html_parts.append("        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }")
        html_parts.append("        th { background-color: #f0f0f0; }")
        html_parts.append("        .summary-card { background-color: #e9f5ff; border-left: 4px solid #2196F3; padding: 15px; margin-bottom: 20px; }")
        html_parts.append("        .summary-card p { margin: 5px 0; }")
        html_parts.append("        .file-path { font-family: monospace; word-break: break-all; }")
        html_parts.append("        .canonical { font-weight: bold; color: #28a745; }")
        html_parts.append("        .duplicate { color: #dc3545; }")
        html_parts.append("        details { margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }")
        html_parts.append("        summary { padding: 10px; background-color: #f9f9f9; cursor: pointer; font-weight: bold; }")
        html_parts.append("        .group-content { padding: 10px; }")
        html_parts.append("    </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        html_parts.append("    <div class='container'>")
        html_parts.append(f"        <h1>File Duplication Audit Report</h1>")
        html_parts.append(f"        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Scan completed at: {timestamp})</p>")
        html_parts.append(f"        <p>Base Path Scanned: <code>{self.base_path}</code></p>")

        html_parts.append("        <div class='summary-card'>")
        html_parts.append("            <h2>Overall Summary</h2>")
        html_parts.append(f"            <p>Total Files Scanned: {len(self.files)}</p>")
        html_parts.append(f"            <p>Total Size Scanned: {self._format_size(analysis['total_size'])}</p>")
        html_parts.append(f"            <p>Duplicate Groups Found: {analysis['duplicate_groups']}</p>")
        html_parts.append(f"            <p>Total Duplicate Files: {analysis['duplicate_files']}</p>")
        html_parts.append(f"            <p>Total Wasted Space: <strong class='duplicate'>{self._format_size(analysis['wasted_space'])}</strong></p>")
        html_parts.append("        </div>")

        html_parts.append("        <h2>Duplicate Groups</h2>")
        if not analysis['duplicate_groups']:
            html_parts.append("        <p>No duplicate groups found.</p>")
        else:
            for i, group_data in enumerate(analysis['groups']):
                group_id = f"Group {i}"
                canonical_path = "N/A"
                if group_data.get('canonical_file'):
                    canonical_path = group_data['canonical_file'].get('path', 'N/A')
                
                html_parts.append(f"        <details>")
                html_parts.append(f"            <summary>{group_id} (Files: {len(group_data['files'])}, Wasted: {self._format_size(group_data['wasted_space'])})</summary>")
                html_parts.append("            <div class='group-content'>")
                html_parts.append(f"            <p><strong>Canonical File Proposal:</strong> <span class='file-path canonical'>{canonical_path}</span></p>")
                html_parts.append("            <table>")
                html_parts.append("                <thead><tr><th>File Path</th><th>Size</th><th>Last Modified</th><th>Hash</th><th>Status</th></tr></thead>")
                html_parts.append("                <tbody>")
                for file_info in group_data['files']:
                    status = "Canonical" if file_info['path'] == canonical_path else "Duplicate"
                    status_class = "canonical" if status == "Canonical" else "duplicate"
                    
                    html_parts.append("                    <tr>")
                    html_parts.append(f"                        <td><span class='file-path'>{file_info['path']}</span></td>")
                    html_parts.append(f"                        <td>{self._format_size(file_info['size'])}</td>")
                    html_parts.append(f"                        <td>{file_info['last_modified']}</td>")
                    
                    # Handle potentially missing content_hash
                    content_hash = file_info.get('content_hash', 'N/A')
                    if content_hash != 'N/A':
                        content_hash = content_hash[:12] + '...'
                    
                    html_parts.append(f"                        <td><code>{content_hash}</code></td>")
                    html_parts.append(f"                        <td><span class='{status_class}'>{status}</span></td>")
                    html_parts.append("                    </tr>")
                html_parts.append("                </tbody>")
                html_parts.append("            </table>")
                html_parts.append("            </div>")
                html_parts.append("        </details>")
        
        html_parts.append("    </div>")
        html_parts.append("</body>")
        html_parts.append("</html>")
        return "\n".join(html_parts)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if not isinstance(size_bytes, (int, float)) or size_bytes < 0:
            logger.warning(f"Invalid size_bytes for _format_size: {size_bytes}. Returning 'N/A'.")
            return "N/A"
        if size_bytes == 0:
            return "0 B"
        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        # Ensure math is imported if not already. It is typically imported at the top of EGOS scripts.
        i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
        if i >= len(size_names):
            i = len(size_names) - 1 # Cap at YB if it's extremely large
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    def generate_report(self, output_dir: Path, generate_json_report: bool = True, 
                       generate_csv_report: bool = True, generate_html_report: bool = True,
                       generate_markdown_report: bool = True, report_retention_days: int = 30) -> bool:
        """
        Generate comprehensive reports about duplicate files in various formats.
        
        This method orchestrates the generation of different report types (HTML, Markdown, JSON, CSV)
        by calling the appropriate helper methods.
        
        Args:
            output_dir: Directory to save reports
            generate_json_report: Whether to generate JSON report
            generate_csv_report: Whether to generate CSV report
            generate_html_report: Whether to generate HTML report
            generate_markdown_report: Whether to generate Markdown report
            report_retention_days: Number of days to keep reports (older reports will be deleted)
            
        Returns:
            True if all requested reports were generated successfully, False otherwise
        """
        logger.info(f"Generating reports in {output_dir}")
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean up old reports before generating new ones
        self._manage_report_retention(output_dir, report_retention_days)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare analysis data for reports
        analysis = self._prepare_analysis_data()
        
        success = True
        
        # Generate HTML report
        if generate_html_report:
            try:
                html_path = output_dir / f"duplication_report_{timestamp}.html"
                html_content = self._generate_html_report_content(analysis)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"HTML report saved to {html_path}")
            except Exception as e:
                logger.error(f"Failed to generate HTML report: {e}")
                success = False
        
        # Generate JSON report
        if generate_json_report:
            try:
                json_path = output_dir / f"duplication_report_{timestamp}.json"
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                logger.info(f"JSON report saved to {json_path}")
            except Exception as e:
                logger.error(f"Failed to generate JSON report: {e}")
                success = False
        
        # Generate CSV report
        if generate_csv_report:
            try:
                csv_path = output_dir / f"duplication_report_{timestamp}.csv"
                
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    import csv
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(["Group", "File Path", "Size", "Last Modified", "Content Hash", "Status"])
                    
                    # Write data
                    for i, group in enumerate(analysis['groups']):
                        canonical_path = "N/A"
                        if group.get('canonical_file'):
                            canonical_path = group['canonical_file'].get('path', 'N/A')
                        
                        for file_info in group['files']:
                            status = "Canonical" if file_info['path'] == canonical_path else "Duplicate"
                            writer.writerow([
                                f"Group {i}",
                                file_info['path'],
                                file_info['size'],
                                file_info['last_modified'],
                                file_info.get('content_hash', 'N/A'),
                                status
                            ])
                
                logger.info(f"CSV report saved to {csv_path}")
            except Exception as e:
                logger.error(f"Failed to generate CSV report: {e}")
                success = False
        
        # Generate Markdown report
        if generate_markdown_report:
            try:
                md_path = output_dir / f"duplication_report_{timestamp}.md"
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# EGOS File Duplication Report\n\n")
                    f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write(f"## Summary\n\n")
                    f.write(f"- Total Files Scanned: {analysis['total_files']}\n")
                    f.write(f"- Duplicate Groups: {analysis['duplicate_groups']}\n")
                    f.write(f"- Total Duplicate Files: {analysis['duplicate_files']}\n")
                    f.write(f"- Wasted Space: {self._format_size(analysis['wasted_space'])}\n\n")
                    
                    f.write(f"## Duplicate Groups\n\n")
                    
                    for i, group in enumerate(analysis['groups']):
                        f.write(f"### Group {i+1}\n\n")
                        f.write(f"- Files: {len(group['files'])}\n")
                        f.write(f"- Wasted Space: {self._format_size(group['wasted_space'])}\n\n")
                        
                        canonical_path = "N/A"
                        if group.get('canonical_file'):
                            canonical_path = group['canonical_file'].get('path', 'N/A')
                            f.write(f"- Canonical File: **{canonical_path}**\n\n")
                        
                        f.write(f"| File Path | Size | Last Modified | Status |\n")
                        f.write(f"|----------|------|--------------|--------|\n")
                        
                        for file_info in group['files']:
                            status = "Canonical" if file_info['path'] == canonical_path else "Duplicate"
                            f.write(f"| {file_info['path']} | {self._format_size(file_info['size'])} | {file_info['last_modified']} | {status} |\n")
                        
                        f.write("\n")
                
                logger.info(f"Markdown report saved to {md_path}")
            except Exception as e:
                logger.error(f"Failed to generate Markdown report: {e}")
                success = False
        
        return success
    
    def _prepare_analysis_data(self) -> Dict[str, Any]:
        """
        Prepare analysis data for reports.
        
        Returns:
            Dictionary containing analysis data
        """
        # Calculate total wasted space
        wasted_space = 0
        duplicate_files = 0
        groups_data = []
        
        for group in self.duplicate_groups:
            if len(group.files) <= 1:
                continue  # Skip groups with only one file
                
            group_wasted_space = group.get_wasted_space()
            wasted_space += group_wasted_space
            duplicate_files += len(group.files) - 1
            
            # Prepare files data
            files_data = []
            for file in group.files:
                files_data.append({
                    'path': str(file.path),
                    'size': file.size,
                    'last_modified': file.last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                    'content_hash': file.content_hash,
                    'is_documentation': file.is_documentation() if hasattr(file, 'is_documentation') else False
                })
            
            # Prepare canonical file data
            canonical_file_data = None
            if group.canonical_file:
                canonical_file_data = {
                    'path': str(group.canonical_file.path),
                    'size': group.canonical_file.size,
                    'last_modified': group.canonical_file.last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                    'content_hash': group.canonical_file.content_hash,
                    'is_documentation': group.canonical_file.is_documentation() if hasattr(group.canonical_file, 'is_documentation') else False
                }
            
            groups_data.append({
                'name': group.name,
                'files': files_data,
                'canonical_file': canonical_file_data,
                'wasted_space': group_wasted_space
            })
        
        # Prepare analysis data
        analysis = {
            'total_files': len(self.files),
            'total_size': sum(file.size for file in self.files),
            'duplicate_groups': len(groups_data),
            'duplicate_files': duplicate_files,
            'wasted_space': wasted_space,
            'groups': groups_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'base_path': str(self.base_path)
        }
        
        return analysis

    def _generate_html_report_content(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML report content for duplicate files."""
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        script_version = "1.0.0" # Default version
        try:
            if 'CONFIG' in globals() and isinstance(CONFIG, dict):
                script_version = CONFIG.get("version", script_version)
            elif hasattr(self, 'config') and isinstance(self.config, dict):
                 script_version = self.config.get("version", script_version)
        except Exception as e:
            logger.warning(f"Could not determine script version from CONFIG or self.config: {e}. Using default: {script_version}")

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGOS File Duplication Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; background-color: #f4f4f4; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .container {{ max-width: 1200px; margin: 20px auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .summary {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ced4da; }}
        .group {{ background-color: #fff; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 15px; padding: 0; overflow: hidden; }}
        .group-header {{ background-color: #f8f9fa; color: #495057; padding: 10px 15px; border-bottom: 1px solid #ddd; }}
        .group-header h3 {{ margin: 0; font-size: 1.2em; }}
        .group-content {{ padding: 15px; }}
        .canonical {{ background-color: #d1e7dd; color: #0f5132; padding: 3px 6px; border-radius: 3px; font-weight: bold; }}
        .duplicate {{ background-color: #f8d7da; color: #842029; padding: 3px 6px; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .file-path {{ font-family: Consolas, 'Courier New', monospace; word-break: break-all; font-size: 0.9em; }}
        .egos-signature {{ text-align: center; margin-top: 30px; font-style: italic; color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>EGOS File Duplication Report</h1>
        <p><strong>Generated on:</strong> {timestamp}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Base directory:</strong> <span class="file-path">{base_directory}</span></p>
            <p><strong>Total files scanned:</strong> {total_files}</p>
            <p><strong>Duplicate groups found:</strong> {duplicate_groups_count}</p>
            <p><strong>Total duplicate files:</strong> {total_duplicates}</p>
            <p><strong>Total wasted space:</strong> {wasted_space_bytes_str} ({wasted_space_human})</p>
        </div>
        
        <h2>Duplicate File Groups</h2>
        {groups_html}
        
        <div class="egos-signature">
            <p>✧༺❀༻∞ EGOS ∞༺❀༻✧</p>
            <p>File Duplication Auditor v{script_version}</p>
        </div>
    </div>
</body>
</html>
"""
        
        wasted_space_bytes = analysis.get('wasted_space', 0)
        wasted_space_human = self._format_size(wasted_space_bytes)
        wasted_space_bytes_str = f"{wasted_space_bytes:,}"
        
        groups_html = ""
        actual_duplicate_groups = []
        if hasattr(self, 'duplicate_groups') and self.duplicate_groups:
            actual_duplicate_groups = [g for g in self.duplicate_groups if hasattr(g, 'files') and len(g.files) > 1]

        if not actual_duplicate_groups:
            groups_html = "<p>No significant duplicate groups found (all groups have 1 or fewer files, or no groups identified).</p>"
        else:
            for i, group_obj in enumerate(actual_duplicate_groups):
                if not hasattr(group_obj, 'files') or not group_obj.files:
                    continue

                size_human = self._format_size(group_obj.files[0].size if hasattr(group_obj.files[0], 'size') else 0)
                group_wasted_space_human = self._format_size(group_obj.get_wasted_space() if hasattr(group_obj, 'get_wasted_space') else 0)

                files_html = "<table>\n"
                files_html += "<thead><tr><th>File Path</th><th>Size</th><th>Last Modified</th><th>Status</th></tr></thead>\n<tbody>\n"
                
                canonical_file_path_str = str(group_obj.canonical_file.path) if hasattr(group_obj, 'canonical_file') and group_obj.canonical_file and hasattr(group_obj.canonical_file, 'path') else None

                sorted_files = sorted(
                    group_obj.files,
                    key=lambda f: (
                        not (canonical_file_path_str and hasattr(f, 'path') and str(f.path) == canonical_file_path_str),
                        str(f.path) if hasattr(f, 'path') else ''
                    )
                )

                for file_info_obj in sorted_files:
                    is_canonical = canonical_file_path_str and hasattr(file_info_obj, 'path') and str(file_info_obj.path) == canonical_file_path_str
                    status_class = "canonical" if is_canonical else "duplicate"
                    status_text = "Canonical" if is_canonical else "Duplicate"
                    file_size_human = self._format_size(file_info_obj.size if hasattr(file_info_obj, 'size') else 0)
                    
                    files_html += f"<tr>\n"
                    files_html += f"<td class='file-path'>{str(file_info_obj.path) if hasattr(file_info_obj, 'path') else 'N/A'}</td>\n"
                    files_html += f"<td>{file_size_human}</td>\n"
                    last_modified_str = 'N/A'
                    if hasattr(file_info_obj, 'last_modified') and isinstance(file_info_obj.last_modified, datetime):
                        last_modified_str = file_info_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
                    files_html += f"<td>{last_modified_str}</td>\n"
                    files_html += f"<td><span class='{status_class}'>{status_text}</span></td>\n"
                    files_html += f"</tr>\n"
                
                files_html += "</tbody></table>"
                
                group_name_str = group_obj.name if hasattr(group_obj, 'name') else f"Unnamed Group {i+1}"
                groups_html += f"""
                <div class="group">
                    <div class="group-header">
                        <h3>{group_name_str} (Group {i+1})</h3>
                        <p>Common File Size: {size_human} | Files in Group: {len(group_obj.files)} | Wasted Space in Group: {group_wasted_space_human}</p>
                    </div>
                    <div class="group-content">
                        {files_html}
                    </div>
                </div>
"""

        html_content = html_template.format(
            timestamp=current_timestamp,
            base_directory=str(self.base_path) if hasattr(self, 'base_path') else 'N/A',
            total_files=f"{len(self.files) if hasattr(self, 'files') else 0:,}",
            duplicate_groups_count=f"{len(actual_duplicate_groups):,}",
            total_duplicates=f"{analysis.get('total_duplicates', 0):,}",
            wasted_space_bytes_str=wasted_space_bytes_str,
            wasted_space_human=wasted_space_human,
            groups_html=groups_html,
            script_version=script_version
        )
        
        return html_content

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


def main():
    """
    Main function to run the script.
    
    Parses command-line arguments, configures the file auditor, performs the scan,
    and generates reports based on the specified options. It implements the full 
    EGOS file duplication detection workflow according to script standards.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Record start time for total execution timing
    start_time = time.time()
    
    # Display banner with proper title
    print_banner("EGOS File Duplication Auditor", "Scan and manage duplicate files")
    
    # Clean up temporary scripts
    cleanup_temporary_scripts()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="EGOS File Duplication Auditor - Find and manage duplicate files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Scanning options
    scan_group = parser.add_argument_group('Scanning Options')
    scan_group.add_argument("--scan-all", action="store_true",
                          help="Scan the entire codebase")
    scan_group.add_argument("--scan-system", action="store_true",
                           help="Scan the entire system (use with caution)")
    scan_group.add_argument("--scan-root", type=str, action="append",
                           help="Root directory for system scan (can be specified multiple times)")
    scan_group.add_argument("--use-cache", action="store_true", default=True,
                           help="Use file system and hash caches to speed up scanning (default: True)")
    scan_group.add_argument("--rebuild-cache", action="store_true",
                           help="Force rebuild of cache even if it exists")
    scan_group.add_argument("--scan-dir", type=str, action="append",
                          help="Directory to scan (can be specified multiple times)")
    scan_group.add_argument("--skip-archives", action="store_true",
                          help="Skip archive directories (zz_archive, backups, etc.)")
    scan_group.add_argument("--max-depth", type=int, default=None,
                          help="Maximum directory depth to scan (default: unlimited)")
    scan_group.add_argument("--dry-run", action="store_true",
                          help="Perform a dry run without generating reports")
    
    # Filtering options
    filter_group = parser.add_argument_group('Filtering Options')
    filter_group.add_argument("--pattern", type=str,
                            help="Pattern to match filenames (e.g., 'design*.md')")
    filter_group.add_argument("--extension", type=str, action="append",
                            help="File extension to focus on (e.g., 'md' without dot)")
    filter_group.add_argument("--exclude-pattern", type=str, action="append",
                            help="Pattern to exclude from scanning (can be specified multiple times)")
    filter_group.add_argument("--min-size", type=int, default=0,
                            help="Minimum file size in bytes")
    filter_group.add_argument("--max-size", type=int, default=None,
                            help="Maximum file size in bytes")
    filter_group.add_argument("--max-comparisons", type=int, default=10000,
                            help="Maximum number of file comparisons per extension")
    
    # Comparison options
    compare_group = parser.add_argument_group('Comparison Options')
    compare_group.add_argument("--by-name", action="store_true", default=True,
                             help="Find duplicates by name (default: True)")
    compare_group.add_argument("--by-content", action="store_true",
                             help="Find duplicates by content hash")
    compare_group.add_argument("--by-similarity", action="store_true",
                             help="Find similar content (not exact duplicates)")
    compare_group.add_argument("--similarity-threshold", type=float, default=CONFIG["similarity_threshold"],
                             help="Threshold for content similarity (0.0-1.0)")
    compare_group.add_argument("--max-read-size", type=int, default=CONFIG["max_file_size"],
                             help="Maximum file size to read for content comparison")
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument("--output-dir", type=str, default="./reports/duplicates",
                            help="Directory to save reports")
    output_group.add_argument("--json", action="store_true", default=CONFIG["generate_json"],
                            help="Generate JSON report")
    output_group.add_argument("--csv", action="store_true", default=CONFIG["generate_csv"],
                            help="Generate CSV report")
    output_group.add_argument("--html", action="store_true", default=CONFIG["generate_html"],
                            help="Generate HTML report")
    output_group.add_argument("--markdown", action="store_true", default=CONFIG["generate_markdown"],
                            help="Generate Markdown report")
    output_group.add_argument("--verbose", action="store_true",
                            help="Enable verbose output")
    output_group.add_argument("--quiet", action="store_true",
                            help="Suppress non-essential output")
    output_group.add_argument("--report-retention-days", type=int, default=30,
                            help="Number of days to keep reports (older reports will be deleted")

    
    # Performance options
    perf_group = parser.add_argument_group('Performance Options')
    perf_group.add_argument("--num-workers", type=int, default=CONFIG["max_workers"],
                          help=f"Number of worker threads")
    perf_group.add_argument("--batch-size", type=int, default=CONFIG["batch_size"],
                          help="Batch size for parallel processing")
    perf_group.add_argument("--timeout", type=int, default=CONFIG["timeout"],
                          help="Timeout in seconds for operations")
    perf_group.add_argument("--context-aware", action="store_true", default=CONFIG["context_aware_duplicates"],
                          help="Use context-aware duplicate detection (consider file purpose and location)")
    perf_group.add_argument("--no-context-aware", action="store_false", dest="context_aware",
                          help="Disable context-aware duplicate detection")
    
    # Integration options
    integration_group = parser.add_argument_group('Integration Options')
    integration_group.add_argument("--update-references", action="store_true",
                                help="Update cross-references to point to canonical files")
    integration_group.add_argument("--generate-proposals", action="store_true",
                                help="Generate canonical file location proposals")
    integration_group.add_argument("--auto-cleanup", action="store_true",
                                help="Automatically move files to canonical locations (use with caution)")
    integration_group.add_argument("--register-with-website", action="store_true",
                                help="Register report with EGOS website")
    integration_group.add_argument("--update-cross-references", action="store_true",
                                help="Update cross-references to point to canonical files")
    integration_group.add_argument("--cross-reference-script", type=str,
                                default=CONFIG.get("cross_reference_script"),
                                help="Path to cross-reference script")
    integration_group.add_argument("--cross-reference-timeout", type=int,
                                default=CONFIG.get("cross_reference_timeout"),
                                help="Timeout for cross-reference operations in seconds")
    
    args = parser.parse_args()
    
    # Configure logging verbosity
    if args.quiet:
        logger.setLevel(logging.WARNING)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Validate arguments
        if not args.scan_all and not args.scan_dir and not args.pattern:
            parser.error("At least one of --scan-all, --scan-dir, or --pattern must be specified")
        
        # Set up output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up base path for scanning
        base_path = Path.cwd()
        if args.scan_all:
            base_path = Path.cwd().parent  # Assume we're in a subdirectory
        
        # Set up excluded directories
        excluded_dirs = set(CONFIG["excluded_dirs"])
        
        if args.skip_archives:
            excluded_dirs.update({"zz_archive", "archive", "archives", "backup", "backups"})
        
        # Create and configure the auditor
        auditor = FileAuditor(
            base_path=base_path,
            excluded_dirs=excluded_dirs,
            max_depth=args.max_depth,
            pattern=args.pattern,
            extensions=args.extension,
            exclude_patterns=args.exclude_pattern,
            min_size=args.min_size,
            max_size=args.max_size,
            similarity_threshold=args.similarity_threshold,
            max_file_size_for_content_read=args.max_read_size,
            num_workers=args.num_workers,
            batch_size=args.batch_size,
            timeout=args.timeout,
            max_comparisons=args.max_comparisons,
            verbose=args.verbose
        )
        
        # Perform scan
        if args.scan_system:
            # System-wide scan
            root_dirs = [Path(d) for d in args.scan_root] if args.scan_root else None
            logger.info(f"Performing system-wide scan")
            auditor.scan_system(root_dirs=root_dirs)
        elif args.scan_dir:
            # Scan specific directories
            for directory in args.scan_dir:
                logger.info(f"Scanning directory: {directory}")
                auditor.scan_files(Path(directory), use_cache=args.use_cache)
        elif args.scan_all:
            # Scan entire codebase
            logger.info(f"Scanning entire codebase from: {base_path}")
            auditor.scan_files(base_path, use_cache=args.use_cache)
        
        # Configure context-aware duplicate detection
        CONFIG["context_aware_duplicates"] = args.context_aware
        
        # Find duplicates based on specified methods
        if args.by_name:
            logger.info("Finding duplicates by name...")
            auditor.find_duplicates_by_name()
        
        if args.by_content:
            logger.info("Finding duplicates by content...")
            auditor.find_duplicates_by_content(similarity_threshold=args.similarity_threshold)
        
        if args.by_similarity:
            logger.info("Finding similar files...")
            auditor.find_duplicates_by_similarity()
        
        # Check if integration is requested
        if args.generate_proposals:
            logger.info("Generating canonical file proposals...")
            integration_results = auditor.integrate_with_cross_reference_system(output_dir)
            if integration_results["status"] == "success":
                logger.info(f"Generated {integration_results.get('proposals_generated', 0)} canonical proposals")
                logger.info(f"Proposals saved to {integration_results.get('proposals_path')}")
                print(f"\nGenerated {integration_results.get('proposals_generated', 0)} canonical proposals")
                print(f"Proposals saved to {integration_results.get('proposals_path')}")
            else:
                logger.error(f"Failed to generate proposals: {integration_results.get('message')}")
                print(f"\nFailed to generate proposals: {integration_results.get('message')}")
            
        # Check if reference update is requested
        if args.update_references:
            logger.info("Updating cross-references...")
            update_results = auditor.update_cross_references(output_dir)
            if update_results["status"] == "success":
                logger.info(f"Updated {update_results.get('updated_references', 0)} cross-references")
                logger.info(f"Failed updates: {update_results.get('failed_updates', 0)}")
                print(f"\nUpdated {update_results.get('updated_references', 0)} cross-references")
                print(f"Failed updates: {update_results.get('failed_updates', 0)}")
            else:
                logger.error(f"Failed to update references: {update_results.get('message')}")
                print(f"\nFailed to update references: {update_results.get('message')}")
            
        # Check if auto-cleanup is requested
        if args.auto_cleanup:
            logger.warning("Auto-cleanup requested - this feature is not yet implemented")
            print("\nAuto-cleanup requested - this feature is not yet implemented")
            # TODO: Implement auto-cleanup
            
        # Check if cross-reference update is requested
        if args.update_cross_references:
            logger.info("Cross-reference update requested")
            
            # Update CONFIG with command-line arguments
            CONFIG["enable_cross_reference"] = True
            if args.cross_reference_script:
                CONFIG["cross_reference_script"] = args.cross_reference_script
            if args.cross_reference_timeout:
                CONFIG["cross_reference_timeout"] = args.cross_reference_timeout
                
            # Update cross-references for each duplicate group
            updated_groups = 0
            for group in auditor.duplicate_groups:
                if group.canonical_file and len(group.files) > 1:
                    # Get duplicate files (excluding canonical)
                    duplicate_files = [f.path for f in group.files if f.path != group.canonical_file.path]
                    
                    # Update cross-references
                    if auditor.update_cross_references(group.canonical_file.path, duplicate_files):
                        updated_groups += 1
                        
            if updated_groups > 0:
                logger.info(f"Updated cross-references for {updated_groups} duplicate groups")
                print(f"\n{Fore.GREEN}✓ Updated cross-references for {updated_groups} duplicate groups{Style.RESET_ALL}")
            else:
                logger.info("No cross-references were updated")
                print("\nNo cross-references were updated")

            
        # Check if website registration is requested
        if args.register_with_website:
            logger.info("Website registration requested")
            print("\nWebsite registration requested - this feature is not yet implemented")
            # TODO: Implement website registration               # This would be implemented in a future version
        
        # Skip report generation for dry runs
        if not args.dry_run:
            # Record report generation start time
            report_start_time = datetime.now()
            
            # Generate report
            auditor.generate_report(
                output_dir=output_dir,
                generate_json_report=args.json,
                generate_csv_report=args.csv,
                generate_html_report=args.html,
                generate_markdown_report=args.markdown,
                report_retention_days=args.report_retention_days
            )
            
            # Record report generation end time
            report_end_time = datetime.now()
            report_duration = (report_end_time - report_start_time).total_seconds()
            logger.info(f"Report generation completed in {report_duration:.2f} seconds")
            
        # Print summary
        total_time = time.time() - start_time
        if not args.quiet:
            print(f"\n{Fore.GREEN}✓ Scan completed in {format_time(total_time)}{Style.RESET_ALL}")
            print(f"  Total files scanned: {len(auditor.files)}")
            print(f"  Duplicate groups found: {len(auditor.duplicate_groups)}")
            
            # Calculate total wasted space safely
            total_wasted = 0
            for group in auditor.duplicate_groups:
                try:
                    total_wasted += group.get_wasted_space()
                except Exception as e:
                    logger.warning(f"Error calculating wasted space for group: {e}")
            
            # Use the auditor's _format_size method
            print(f"  Total wasted space: {auditor._format_size(total_wasted)}")
            
            if not args.dry_run:
                print(f"\n{Fore.CYAN}Reports saved to: {output_dir}{Style.RESET_ALL}")
        
        # Calculate total duration
        end_time = datetime.now()
        total_duration = (end_time - datetime.fromtimestamp(start_time)).total_seconds()
        
        # Log total execution time
        logger.info(f"Total execution time: {total_duration:.2f} seconds")
        
        # Print summary statistics
        logger.info("\nSummary Statistics:")
        logger.info(f"  Files scanned: {len(auditor.files)}")
        logger.info(f"  Duplicate groups found: {len(auditor.duplicate_groups)}")
        
        # Calculate total duplicates safely
        total_duplicates = 0
        for group in auditor.duplicate_groups:
            try:
                # Count all files in the group except the canonical one
                total_duplicates += len(group.files) - 1
            except Exception as e:
                logger.warning(f"Error calculating duplicate count for group: {e}")
                
        logger.info(f"  Total duplicate files: {total_duplicates}")
        logger.info(f"  Total wasted space: {auditor._format_size(total_wasted)}")

        return 0
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        start_time = time.time()
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("File Duplication Auditor completed")
        print(f"\n{Fore.BLUE}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}\n")