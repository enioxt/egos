#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Optimized Reference Fixer

This script efficiently fixes invalid references in EGOS documents by updating them to use
the standardized format with EGOS IDs. It features parallel processing, test mode for quick validation,
and standardized report locations.

Part of the EGOS Cross-Reference Standardization Initiative.

References:
- [EGOS Cross-Reference Standardization](../../../docs_egos/05_development/standards/cross_reference_standard.md)
- [KOIOS Documentation Standards](../../../docs_egos/05_development/standards/documentation_standards.md)
- [Reference Validator](../cross_reference/reference_validator.py)
- [Docs Directory Fixer](../cross_reference/docs_directory_fixer.py)

Author: EGOS Development Team
Created: 2025-05-21
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
import re
import sys
import time
import json
import logging
import argparse
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import defaultdict, Counter

# Third-party imports
from tqdm import tqdm

# Configure tqdm for clean output
tqdm.monitor_interval = 0

# Disable tqdm when redirecting output
if not sys.stdout.isatty():
    def _tqdm_wrapper(*args, **kwargs):
        return args[0] if args else None
    tqdm = _tqdm_wrapper

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
TERMINAL_WIDTH = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 100
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)
DEFAULT_TIMEOUT = 30
DEFAULT_TEST_FILE_LIMIT = 50

# Standardized report locations
REPORTS_DIR = Path("C:/EGOS/docs_egos/10_system_health/reports")
CROSSREF_REPORTS_DIR = REPORTS_DIR / "cross_reference"
BACKUPS_DIR = REPORTS_DIR / "backups"

# Configuration
CONFIG = {
    # Performance settings
    "batch_size": DEFAULT_BATCH_SIZE,
    "max_workers": min(32, (os.cpu_count() or 4) * 2),
    "timeout": DEFAULT_TIMEOUT,
    "test_file_limit": DEFAULT_TEST_FILE_LIMIT,
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'reference_fixer.log'),
    "log_level": "INFO",
    
    # Reference settings
    "reference_block_start": "<!-- crossref_block:start -->",
    "reference_block_end": "<!-- crossref_block:end -->",
    "reference_line_prefix": "- 🔗 Reference: ",
    "egos_id_prefix": "EGOS-REF-",
    
    # File extensions to process
    "file_extensions": ['.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'],
    
    # Directories to exclude
    "exclude_dirs": {
        '.git', 'venv', 'node_modules', '__pycache__', 'dist', 'build', 
        'target', 'bin', 'obj', '.backup', '.temp', 'backup', 'temp',
        '.vscode', '.idea', '.vs', 'backups'
    },
    
    # Path patterns to exclude (regex)
    "exclude_patterns": [
        r'.*backup.*',
        r'.*\.backup.*',
        r'.*\\backup.*',
        r'.*\\backups.*',
        r'.*\/backup.*',
        r'.*\/backups.*',
    ],
    
    # Backup settings
    "create_backups": True,
}

# Ensure report directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CROSSREF_REPORTS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("reference_fixer")

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# Helper functions
def print_banner(title: str, subtitle: Optional[str] = None):
    """Print a visually appealing banner.
    
    Args:
        title: Title to display
        subtitle: Optional subtitle
    """
    # Ensure clean output by flushing stdout first
    sys.stdout.flush()
    
    print(f"╔{'═' * (BANNER_WIDTH - 2)}╗")
    print(f"║{title.center(BANNER_WIDTH - 2)}║")
    
    if subtitle:
        print(f"║{subtitle.center(BANNER_WIDTH - 2)}║")
    
    # Bottom border
    print(f"╚{'═' * (BANNER_WIDTH - 2)}╝")
    
    # Ensure banner is fully displayed
    sys.stdout.flush()
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

def generate_egos_id() -> str:
    """Generate a unique EGOS reference ID."""
    # Use a UUID to ensure uniqueness
    unique_id = str(uuid.uuid4()).split('-')[0]
    return f"{CONFIG['egos_id_prefix']}{unique_id.upper()}"

def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of a file before modifying it.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file, or None if backup failed
    """
    if not CONFIG["create_backups"]:
        return None
    
    try:
        # Create backup directory if it doesn't exist
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = BACKUPS_DIR / timestamp
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create relative path structure in backup directory
        rel_path = file_path.relative_to(Path.cwd())
        backup_file = backup_dir / rel_path
        os.makedirs(backup_file.parent, exist_ok=True)
        
        # Copy file to backup location
        with open(file_path, 'rb') as src, open(backup_file, 'wb') as dst:
            dst.write(src.read())
        
        logger.debug(f"Created backup of {file_path} at {backup_file}")
        return backup_file
    
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {str(e)}")
        return None


class ReferenceFixer:
    """Optimized reference fixer for EGOS documents."""
    
    def __init__(
        self, 
        base_path: str, 
        priority_files: List[str] = None, 
        dry_run: bool = False,
        test_mode: bool = False,
        fix_docs_directory: bool = False
    ):
        """Initialize the reference fixer.
        
        Args:
            base_path: Base path to process
            priority_files: List of files to prioritize for fixing
            dry_run: If True, don't actually modify files
            test_mode: If True, only process a limited number of files
            fix_docs_directory: If True, handle docs vs docs_egos directory issue
        """
        self.base_path = Path(base_path)
        self.priority_files = priority_files or []
        self.dry_run = dry_run
        self.test_mode = test_mode
        self.fix_docs_directory = fix_docs_directory
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "references_found": 0,
            "references_fixed": 0,
            "docs_references_updated": 0,
            "errors": 0,
            "processing_time": 0,
        }
        
        # Cache of all files
        self.all_files = set()
        
        # Cache of file paths
        self.file_path_cache = {}
        
        # Cache of reference patterns
        self.reference_patterns = {
            "standard": re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            "mdc": re.compile(r'\[([^\]]+)\]\(mdc:([^)]+)\)'),
            "html": re.compile(r'<a\s+href=["\']([^"\'\']+)["\'][^>]*>([^<]+)</a>'),
            "cci": re.compile(r'\[([^\]]+)\]\(cci:7://([^)]+)\)'),
        }
        
        # Special reference prefixes to skip validation
        self.special_prefixes = [
            'cci:7://', 
            'mdc:',
            'http://', 
            'https://', 
            'ftp://', 
            'mailto:'
        ]
        
        # Initialize file path cache
        self._init_file_cache()
    
    def _init_file_cache(self) -> None:
        """Initialize the file path cache for faster lookups."""
        logger.info("Initializing file cache for faster reference validation...")
        
        # Use a set for O(1) lookups
        self.all_files = set()
        
        # Use a dictionary to map directories to files
        self.file_path_cache = defaultdict(list)
        
        # Compile exclude patterns for faster matching
        exclude_patterns = [re.compile(pattern) for pattern in CONFIG["exclude_patterns"]]
        
        # Track progress with simpler format to avoid display issues
        progress = tqdm(
            desc="Building file cache",
            unit="dirs",
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{desc}: {percentage:3.0f}% |{bar}| {n_fmt} dirs [{elapsed}<{remaining}]',
            leave=True,
            position=0,
            file=sys.stdout
        )
        # Ensure clean output
        sys.stdout.flush()
        
        # Walk the directory tree
        for root, dirs, filenames in os.walk(self.base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in CONFIG["exclude_dirs"]]
            
            # Skip paths matching exclude patterns
            if any(pattern.match(root) for pattern in exclude_patterns):
                dirs[:] = []  # Skip all subdirectories
                continue
            
            # Add files to cache
            for filename in filenames:
                file_path = Path(os.path.join(root, filename))
                file_path_str = str(file_path)
                
                # Skip files in excluded patterns
                if any(pattern.match(file_path_str) for pattern in exclude_patterns):
                    continue
                
                # Check if extension is in the list to process
                if file_path.suffix.lower() in CONFIG["file_extensions"]:
                    resolved_path = file_path.resolve()
                    self.all_files.add(resolved_path)
                    self.file_path_cache[str(file_path.parent)].append(str(file_path))
            
            # Update progress
            progress.update()
        
        progress.close()
        logger.info(f"File cache initialized with {len(self.all_files):,} files")
    
    def find_files(self) -> List[Path]:
        """Find all files to process.
        
        Returns:
            List of file paths
        """
        logger.info(f"Finding files to process in {self.base_path}")
        
        files = []
        priority_files_set = set(self.priority_files)
        
        for file_path in self.all_files:
            # Skip files in docs directory if we're not fixing that issue
            if not self.fix_docs_directory and "docs" in str(file_path) and "docs_egos" not in str(file_path):
                continue
                
            files.append(file_path)
        
        # Sort files by priority
        if priority_files_set:
            # Put priority files first
            files.sort(key=lambda f: str(f) not in priority_files_set)
        
        # Limit files in test mode
        if self.test_mode:
            logger.info(f"Test mode: limiting to {CONFIG['test_file_limit']} files")
            files = files[:CONFIG['test_file_limit']]
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def extract_references(self, content: str) -> List[Tuple[str, str, int, int, str]]:
        """Extract references from content.
        
        Args:
            content: Content to extract references from
            
        Returns:
            List of tuples (reference_text, reference_target, start_index, end_index, reference_type)
        """
        references = []
        
        # Find standard markdown links
        for match in self.reference_patterns["standard"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            
            # Skip external links
            if not any(target.startswith(prefix) for prefix in self.special_prefixes):
                references.append((text, target, match.start(), match.end(), "standard"))
        
        # Find MDC links
        for match in self.reference_patterns["mdc"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            references.append((text, target, match.start(), match.end(), "mdc"))
        
        # Find CCI links
        for match in self.reference_patterns["cci"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            references.append((text, target, match.start(), match.end(), "cci"))
        
        # Find HTML links
        for match in self.reference_patterns["html"].finditer(content):
            target = match.group(1)
            text = match.group(2)
            
            # Skip external links
            if not any(target.startswith(prefix) for prefix in self.special_prefixes):
                references.append((text, target, match.start(), match.end(), "html"))
        
        return references
    
    def validate_reference(self, reference: Tuple[str, str, str], source_file: Path) -> bool:
        """Validate a reference.
        
        Args:
            reference: Tuple (reference_text, reference_target, reference_type)
            source_file: Path to the source file
            
        Returns:
            True if the reference is valid, False otherwise
        """
        text, target, ref_type = reference
        
        try:
            # Handle special reference types
            if ref_type in ["mdc", "cci"]:
                # Special references are considered valid for now
                return True
            
            # Skip references with special prefixes
            if any(target.startswith(prefix) for prefix in self.special_prefixes):
                return True
            
            # Handle relative paths
            if not os.path.isabs(target):
                target_path = source_file.parent / target
            else:
                target_path = Path(target)
            
            # Normalize path
            target_path = target_path.resolve()
            
            # Check if target exists
            return target_path in self.all_files
        
        except Exception as e:
            # Log at debug level to reduce noise
            logger.debug(f"Error validating reference {text} -> {target} in {source_file}: {str(e)}")
            return False
    
    def fix_reference(self, content: str, reference: Tuple[str, str, int, int, str], source_file: Path) -> Tuple[str, bool]:
        """Fix a reference by updating it to use the standardized format.
        
        Args:
            content: Content to fix
            reference: Tuple (reference_text, reference_target, start_index, end_index, reference_type)
            source_file: Path to the source file
            
        Returns:
            Tuple (updated_content, was_fixed)
        """
        text, target, start_idx, end_idx, ref_type = reference
        
        # Check if we need to fix docs vs docs_egos
        if self.fix_docs_directory and "/docs/" in target and "/docs_egos/" not in target:
            # Replace docs with docs_egos in the target
            fixed_target = target.replace("/docs/", "/docs_egos/")
            
            # Create the new reference
            if ref_type == "standard":
                old_ref = content[start_idx:end_idx]
                new_ref = f"[{text}]({fixed_target})"
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref} <!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed docs reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                self.stats["docs_references_updated"] += 1
                return updated_content, True
            
            elif ref_type == "mdc":
                old_ref = content[start_idx:end_idx]
                new_ref = f"[{text}](mdc:{fixed_target})"
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref} <!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed docs MDC reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                self.stats["docs_references_updated"] += 1
                return updated_content, True
            
            elif ref_type == "html":
                old_ref = content[start_idx:end_idx]
                new_ref = f'<a href="{fixed_target}">{text}</a>'
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref}<!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed docs HTML reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                self.stats["docs_references_updated"] += 1
                return updated_content, True
        
        # Check if reference is valid
        is_valid = self.validate_reference((text, target, ref_type), source_file)
        
        if is_valid:
            # Reference is valid, no need to fix
            return content, False
        
        # Try to find a valid target
        fixed_target = self.find_valid_target(target, ref_type, source_file)
        
        if fixed_target:
            # Replace the reference with the fixed target
            if ref_type == "standard":
                old_ref = content[start_idx:end_idx]
                new_ref = f"[{text}]({fixed_target})"
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref} <!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                return updated_content, True
            
            elif ref_type == "mdc":
                old_ref = content[start_idx:end_idx]
                new_ref = f"[{text}](mdc:{fixed_target})"
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref} <!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed MDC reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                return updated_content, True
            
            elif ref_type == "html":
                old_ref = content[start_idx:end_idx]
                new_ref = f'<a href="{fixed_target}">{text}</a>'
                
                # Generate a unique EGOS ID for the reference
                egos_id = generate_egos_id()
                
                # Add EGOS ID to the reference
                new_ref_with_id = f"{new_ref}<!-- {egos_id} -->"
                
                # Replace the reference
                updated_content = content[:start_idx] + new_ref_with_id + content[end_idx:]
                
                logger.info(f"Fixed HTML reference in {source_file}: {old_ref} -> {new_ref_with_id}")
                return updated_content, True
        
        # Couldn't fix the reference
        return content, False
    
    def find_valid_target(self, target: str, ref_type: str, source_file: Path) -> Optional[str]:
        """Find a valid target for a reference.
        
        Args:
            target: Reference target
            ref_type: Reference type
            source_file: Path to the source file
            
        Returns:
            Valid target path, or None if no valid target could be found
        """
        # Handle MDC references differently
        if ref_type == "mdc":
            # For MDC references, we don't try to find alternative targets
            return None
        
        # Try different extensions
        for ext in CONFIG["file_extensions"]:
            # Try with the extension
            test_target = f"{target}{ext}"
            if self.validate_reference(("", test_target, ref_type), source_file):
                return test_target
            
            # Try without the current extension and with the new extension
            if "." in target:
                base_target = target.rsplit(".", 1)[0]
                test_target = f"{base_target}{ext}"
                if self.validate_reference(("", test_target, ref_type), source_file):
                    return test_target
        
        # Try to find a file with a similar name
        try:
            target_filename = os.path.basename(target)
            target_dir = os.path.dirname(target)
            
            # If target_dir is empty, use the source file's directory
            if not target_dir:
                target_dir = str(source_file.parent)
            
            # Resolve the target directory
            if not os.path.isabs(target_dir):
                target_dir = str((source_file.parent / target_dir).resolve())
            
            # Check if we've already cached this directory
            if target_dir in self.file_path_cache:
                # Look for similar filenames
                target_base = os.path.splitext(target_filename)[0].lower()
                for file_path in self.file_path_cache[target_dir]:
                    file_base = os.path.splitext(os.path.basename(file_path))[0].lower()
                    
                    # Check if the filename is similar
                    if file_base == target_base or target_base in file_base or file_base in target_base:
                        # Convert to relative path from source file
                        rel_path = os.path.relpath(file_path, os.path.dirname(str(source_file)))
                        
                        # Normalize path separators
                        rel_path = rel_path.replace("\\", "/")
                        
                        return rel_path
        
        except Exception as e:
            logger.error(f"Error finding valid target for {target} in {source_file}: {str(e)}")
        
        return None
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results
        """
        result = {
            "file": str(file_path),
            "references_found": 0,
            "references_fixed": 0,
            "docs_references_updated": 0,
            "was_modified": False,
            "error": None
        }
        
        try:
            # Check if file exists and is readable
            if not file_path.exists() or not os.access(file_path, os.R_OK):
                result["error"] = f"File does not exist or is not readable"
                return result
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract references
            references = self.extract_references(content)
            result["references_found"] = len(references)
            
            # Fix references
            modified_content = content
            for reference in references:
                modified_content, was_fixed = self.fix_reference(modified_content, reference, file_path)
                if was_fixed:
                    if self.fix_docs_directory and "/docs/" in reference[1] and "/docs_egos/" not in reference[1]:
                        result["docs_references_updated"] += 1
                    else:
                        result["references_fixed"] += 1
                    result["was_modified"] = True
            
            # Write modified content back to file if needed
            if result["was_modified"] and not self.dry_run:
                # Create backup
                create_backup(file_path)
                
                # Write modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            return result
        
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def process_files_parallel(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files in parallel using a thread pool.
        
        Args:
            files: List of files to process
            
        Returns:
            List of processing results
        """
        results = []
        total_files = len(files)
        processed_files = 0
        modified_files = 0
        
        # Create progress bar with simpler format to avoid display issues
        progress = tqdm(
            total=total_files,
            desc="Fixing references",
            unit="files",
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{desc}: {percentage:3.0f}% |{bar}| {n_fmt}/{total_fmt} files [{elapsed}<{remaining}]',
            leave=True,
            position=0,
            file=sys.stdout
        )
        # Ensure clean output
        sys.stdout.flush()
        
        # Process files in batches for better memory management
        batch_size = CONFIG["batch_size"]
        for i in range(0, total_files, batch_size):
            batch_files = files[i:i+batch_size]
            
            # Process batch in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
                # Submit all tasks
                future_to_file = {executor.submit(self.process_file, file_path): file_path for file_path in batch_files}
                
                # Process results as they complete with timeout
                try:
                    for future in concurrent.futures.as_completed(future_to_file, timeout=CONFIG["timeout"]):
                        file_path = future_to_file[future]
                        
                        try:
                            # Add timeout for individual results to prevent hanging
                            result = future.result(timeout=5)
                            results.append(result)
                            
                            # Update statistics
                            self.stats["files_processed"] += 1
                            processed_files += 1
                            
                            if result["was_modified"]:
                                self.stats["files_modified"] += 1
                                modified_files += 1
                            
                            self.stats["references_found"] += result["references_found"]
                            self.stats["references_fixed"] += result["references_fixed"]
                            self.stats["docs_references_updated"] += result["docs_references_updated"]
                            
                            if result["error"]:
                                self.stats["errors"] += 1
                        except concurrent.futures.TimeoutError:
                            logger.error(f"Timeout processing {file_path}")
                            self.stats["errors"] += 1
                            # Add a placeholder result to maintain file count
                            results.append({
                                "file_path": str(file_path),
                                "was_modified": False,
                                "references_found": 0,
                                "references_fixed": 0,
                                "docs_references_updated": 0,
                                "error": True,
                                "error_message": "Processing timeout"
                            })
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {str(e)}")
                            self.stats["errors"] += 1
                            # Add a placeholder result to maintain file count
                            results.append({
                                "file_path": str(file_path),
                                "was_modified": False,
                                "references_found": 0,
                                "references_fixed": 0,
                                "docs_references_updated": 0,
                                "error": True,
                                "error_message": str(e)
                            })
                        
                        # Update progress
                        progress.set_postfix_str(f"Modified: {modified_files} | Errors: {self.stats['errors']}")
                        progress.update()
                except concurrent.futures.TimeoutError:
                    logger.error(f"Batch timeout after {CONFIG['timeout']} seconds with {len(future_to_file)} unfinished futures")
                    # Cancel all remaining futures
                    for future in future_to_file:
                        future.cancel()
                    # Process any remaining files sequentially
                    for file_path in batch_files:
                        if not any(r.get("file_path") == str(file_path) for r in results):
                            logger.warning(f"Processing {file_path} sequentially after batch timeout")
                            try:
                                result = self.process_file(file_path)
                                results.append(result)
                                self.stats["files_processed"] += 1
                                processed_files += 1
                                progress.update()
                            except Exception as e:
                                logger.error(f"Error in sequential processing of {file_path}: {str(e)}")
                                self.stats["errors"] += 1
            
            # Periodically log progress
            if processed_files % (batch_size * 5) == 0 or processed_files == total_files:
                logger.info(f"Progress: {processed_files}/{total_files} files processed, {modified_files} modified, {self.stats['errors']} errors")
        
        progress.close()
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Path:
        """Generate a report of the fixing results.
        
        Args:
            results: List of processing results
            
        Returns:
            Path to the generated report
        """
        # Generate report filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = CROSSREF_REPORTS_DIR / f"reference_fixer_{timestamp}.md"
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            # Title and metadata
            f.write(f"# EGOS Reference Fixer Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Mode:** {'Test Mode' if self.test_mode else 'Full Mode'} | {'Dry Run (no files modified)' if self.dry_run else 'Live Run (files modified)'}\n\n")
            f.write(f"**Fix docs directory references:** {'Yes' if self.fix_docs_directory else 'No'}\n\n")
            
            # Executive summary
            f.write(f"## 📊 Executive Summary\n\n")
            f.write(f"This report presents the results of fixing invalid references across the EGOS ecosystem.\n\n")
            f.write(f"- **Files Processed:** {self.stats['files_processed']:,}\n")
            f.write(f"- **Files Modified:** {self.stats['files_modified']:,} ({self.stats['files_modified'] / max(1, self.stats['files_processed']) * 100:.1f}% of files)\n")
            f.write(f"- **References Found:** {self.stats['references_found']:,}\n")
            f.write(f"- **References Fixed:** {self.stats['references_fixed']:,} ({self.stats['references_fixed'] / max(1, self.stats['references_found']) * 100:.1f}% of references)\n")
            
            if self.fix_docs_directory:
                f.write(f"- **Docs References Updated:** {self.stats['docs_references_updated']:,}\n")
                
            f.write(f"- **Errors:** {self.stats['errors']:,}\n")
            f.write(f"- **Processing Time:** {format_time(self.stats['processing_time'])}\n\n")
            
            # Modified files
            modified_results = [r for r in results if r["was_modified"]]
            
            if modified_results:
                f.write(f"## 📝 Modified Files\n\n")
                f.write(f"The following files were modified to fix invalid references:\n\n")
                
                if self.fix_docs_directory:
                    f.write(f"| File | References Fixed | Docs References Updated | Total References |\n")
                    f.write(f"|------|-----------------|------------------------|------------------|\n")
                    
                    for result in sorted(modified_results, key=lambda x: x["references_fixed"] + x["docs_references_updated"], reverse=True):
                        file_path = Path(result["file"])
                        try:
                            rel_path = file_path.relative_to(self.base_path)
                        except ValueError:
                            rel_path = file_path
                        
                        f.write(f"| {rel_path} | {result['references_fixed']} | {result['docs_references_updated']} | {result['references_found']} |\n")
                else:
                    f.write(f"| File | References Fixed | Total References |\n")
                    f.write(f"|------|-----------------|------------------|\n")
                    
                    for result in sorted(modified_results, key=lambda x: x["references_fixed"], reverse=True):
                        file_path = Path(result["file"])
                        try:
                            rel_path = file_path.relative_to(self.base_path)
                        except ValueError:
                            rel_path = file_path
                        
                        f.write(f"| {rel_path} | {result['references_fixed']} | {result['references_found']} |\n")
            else:
                f.write(f"## 📝 No Files Modified\n\n")
                f.write(f"No files were modified during this run.\n\n")
            
            # Errors
            error_results = [r for r in results if r["error"]]
            
            if error_results:
                f.write(f"\n## ⚠️ Errors\n\n")
                f.write(f"The following errors occurred during processing:\n\n")
                f.write(f"| File | Error |\n")
                f.write(f"|------|-------|\n")
                
                for result in error_results:
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    f.write(f"| {rel_path} | {result['error']} |\n")
            
            # Next steps
            f.write(f"\n## 🚀 Next Steps\n\n")
            
            if self.dry_run:
                f.write(f"1. Review this report to ensure the proposed changes are correct\n")
                f.write(f"2. Run the reference fixer in live mode to apply the changes\n")
                f.write(f"3. Run the cross-reference validator to confirm all references are valid\n")
            else:
                f.write(f"1. Run the cross-reference validator to confirm all references are valid\n")
                f.write(f"2. Fix any remaining invalid references manually\n")
                f.write(f"3. Add cross-reference validation to the CI/CD pipeline\n")
            
            # Add EGOS signature
            f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def run(self) -> Path:
        """Run the reference fixer.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Find files to process
        files = self.find_files()
        
        # Process files in parallel
        results = self.process_files_parallel(files)
        
        # Generate report
        report_path = self.generate_report(results)
        
        # Update statistics
        self.stats["processing_time"] = time.time() - start_time
        
        return report_path


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Optimized reference fixer for EGOS documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Fix references in the current directory (dry run)
  python optimized_reference_fixer.py --dry-run
  
  # Fix references in a specific directory
  python optimized_reference_fixer.py --base-path /path/to/directory
  
  # Fix references in test mode (limited number of files)
  python optimized_reference_fixer.py --test-mode
  
  # Fix references in specific files
  python optimized_reference_fixer.py --priority-files file1.md file2.md
  
  # Fix docs vs docs_egos directory issue
  python optimized_reference_fixer.py --fix-docs-directory
  
  # Skip backup directories and increase workers
  python optimized_reference_fixer.py --skip-backups --max-workers 8

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(), help="Base path to process")
    parser.add_argument("--priority-files", type=str, nargs="+", help="List of files to prioritize for fixing")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually modify files")
    parser.add_argument("--test-mode", action="store_true", help="Only process a limited number of files")
    parser.add_argument("--fix-docs-directory", action="store_true", help="Fix docs vs docs_egos directory references")
    parser.add_argument("--batch-size", type=int, default=CONFIG["batch_size"], help="Number of files to process in each batch")
    parser.add_argument("--max-workers", type=int, default=CONFIG["max_workers"], help="Maximum number of worker threads")
    parser.add_argument("--test-file-limit", type=int, default=CONFIG["test_file_limit"], help="Number of files to process in test mode")
    parser.add_argument("--no-backups", action="store_true", help="Don't create backups before modifying files")
    parser.add_argument("--skip-backups", action="store_true", help="Skip scanning backup directories")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)
    
    # Update configuration from command line arguments
    CONFIG["batch_size"] = args.batch_size
    CONFIG["max_workers"] = args.max_workers
    CONFIG["test_file_limit"] = args.test_file_limit
    CONFIG["create_backups"] = not args.no_backups
    
    # Add additional exclude patterns if requested
    if args.skip_backups:
        CONFIG["exclude_patterns"].extend([
            r'.*backup.*',
            r'.*\.backup.*',
            r'.*\\backup.*',
            r'.*\\backups.*',
            r'.*\/backup.*',
            r'.*\/backups.*',
        ])
        CONFIG["exclude_dirs"].update({'backup', 'backups'})
    
    # Print banner
    mode_str = "Test Mode" if args.test_mode else "Full Mode"
    run_str = "Dry Run (no files modified)" if args.dry_run else "Live Run (files will be modified)"
    docs_str = "Fixing docs directory references" if args.fix_docs_directory else ""
    backup_str = "Skipping Backups" if args.skip_backups else ""
    
    subtitle = f"{mode_str} | {run_str}"
    if docs_str:
        subtitle += f" | {docs_str}"
    if backup_str:
        subtitle += f" | {backup_str}"
    
    print_banner(
        "EGOS Optimized Reference Fixer",
        subtitle
    )
    
    # Create and run the reference fixer
    fixer = ReferenceFixer(
        base_path=args.base_path,
        priority_files=args.priority_files,
        dry_run=args.dry_run,
        test_mode=args.test_mode,
        fix_docs_directory=args.fix_docs_directory
    )
    
    try:
        report_path = fixer.run()
        
        # Display summary statistics
        logger.info(f"\n{Fore.GREEN}Reference fixing completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files processed:{Style.RESET_ALL} {fixer.stats['files_processed']:,}")
        logger.info(f"  • {Fore.CYAN}Files modified:{Style.RESET_ALL} {fixer.stats['files_modified']:,} ({fixer.stats['files_modified'] / max(1, fixer.stats['files_processed']) * 100:.1f}% of files)")
        logger.info(f"  • {Fore.CYAN}References found:{Style.RESET_ALL} {fixer.stats['references_found']:,}")
        logger.info(f"  • {Fore.CYAN}References fixed:{Style.RESET_ALL} {fixer.stats['references_fixed']:,} ({fixer.stats['references_fixed'] / max(1, fixer.stats['references_found']) * 100:.1f}% of references)")
        
        if args.fix_docs_directory:
            logger.info(f"  • {Fore.CYAN}Docs references updated:{Style.RESET_ALL} {fixer.stats['docs_references_updated']:,}")
            
        logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {fixer.stats['errors']:,}")
        logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(fixer.stats['processing_time'])}")
        logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
        
        # Suggest next steps
        print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
        
        if args.dry_run:
            print(f"1. Review the report at {report_path}")
            print(f"2. Run the reference fixer in live mode to apply the changes")
            print(f"3. Run the cross-reference validator to confirm all references are valid")
        else:
            print(f"1. Run the cross-reference validator to confirm all references are valid")
            print(f"2. Fix any remaining invalid references manually")
            print(f"3. Add cross-reference validation to the CI/CD pipeline")
        
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running reference fixer: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()