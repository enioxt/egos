#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cross-Reference Purge Script
Part of the EGOS Cross-Reference Standardization Initiative.

This script identifies and purges outdated reference formats from the EGOS codebase,
preparing files for the injection of standardized references. It includes safety
features like backup functionality and dry-run mode.

Author: EGOS Development Team
Date: 2025-05-21
Version: 1.0.0

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

import os
import re
import shutil
import logging
import argparse
import json
import sys
import time
import asyncio
import math
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Pattern, Union, Callable
from collections import defaultdict, Counter
import concurrent.futures
from tqdm import tqdm

# Try to import colorama for cross-platform colored terminal output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Create dummy colorama classes
    class DummyColorama:
        def __getattr__(self, name):
            return ''
    Fore = Style = DummyColorama()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("cross_reference_purger")

# Constants for terminal output
TERMINAL_WIDTH = shutil.get_terminal_size().columns
BANNER_WIDTH = min(100, TERMINAL_WIDTH)

class ProgressTracker:
    """Enhanced progress tracking with ETA and visual feedback.
    
    Provides rich visual feedback during long-running operations,
    including progress bars, ETA calculations, and status updates.
    """
    
    def __init__(self, total: int, description: str = "Processing", unit: str = "files"):
        self.total = total
        self.description = description
        self.unit = unit
        self.processed = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 0.5  # seconds
        self.last_eta = "Calculating..."
        self.speed = 0.0
        
        # Create progress bar
        self.pbar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}{description}{Style.RESET_ALL}",
            unit=unit,
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
    
    def update(self, increment: int = 1, status: Optional[str] = None) -> None:
        """Update progress and display status."""
        self.processed += increment
        current_time = time.time()
        
        # Only update visual elements periodically to reduce overhead
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            
            # Calculate speed and ETA
            elapsed = current_time - self.start_time
            if elapsed > 0:
                self.speed = self.processed / elapsed
                remaining = (self.total - self.processed) / self.speed if self.speed > 0 else 0
                
                # Format ETA
                if remaining > 3600:
                    self.last_eta = f"{remaining/3600:.1f}h"
                elif remaining > 60:
                    self.last_eta = f"{remaining/60:.1f}m"
                else:
                    self.last_eta = f"{remaining:.0f}s"
            
            # Update progress bar
            self.pbar.update(increment)
            
            # Display status if provided
            if status:
                self.pbar.set_description_str(f"{Fore.CYAN}{self.description}{Style.RESET_ALL} - {status}")
    
    def close(self) -> None:
        """Close the progress tracker."""
        self.pbar.close()
    
    def display_summary(self) -> None:
        """Display a summary of the operation."""
        elapsed = time.time() - self.start_time
        speed = self.processed / elapsed if elapsed > 0 else 0
        
        logger.info(f"""\n{Fore.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}""")
        logger.info(f"{Fore.GREEN}Operation Summary:{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Total {self.unit}:{Style.RESET_ALL} {self.processed:,}")
        logger.info(f"  • {Fore.CYAN}Elapsed time:{Style.RESET_ALL} {format_time(elapsed)}")
        logger.info(f"  • {Fore.CYAN}Average speed:{Style.RESET_ALL} {speed:.2f} {self.unit}/second")
        logger.info(f"{Fore.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")

def format_time(seconds: float) -> str:
    """Format time in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours, {minutes} minutes"

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

# Constants
BACKUP_DIR = r"C:\EGOS\docs\reports\backups"
INVENTORY_DIR = r"C:\EGOS\docs\reports"
TEMP_DIR = r"C:\EGOS\docs\reports\temp_grep_results"

# Directories to exclude from processing
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'venv', 'node_modules', 'dist', 'build', '.idea', '.vscode',
    'backups', 'temp_grep_results'
}

# Patterns to purge based on inventory report
PURGE_PATTERNS = [
    # Relative paths (handle with care - only in specific contexts)
    {"name": "RelativePathSelf", "pattern": r"\./", "context_required": True},
    {"name": "RelativePathParent", "pattern": r"\.\./", "context_required": True},
    
    # EGOS ID references (only when not in canonical format)
    {"name": "EGOS_ID_Start", "pattern": r"EGOS-[A-Z]+-[A-Z]+-\d+", "context_required": False},
    
    # Memory references
    {"name": "MEMORY", "pattern": r"MEMORY\[[a-zA-Z0-9\-]+\]", "context_required": False},
    
    # Keyword-based references
    {"name": "Source", "pattern": r"Source:\s", "context_required": False},
    {"name": "Reference", "pattern": r"Reference:\s", "context_required": False},
    {"name": "Ref", "pattern": r"Ref:\s", "context_required": False},
    {"name": "Related", "pattern": r"Related:\s", "context_required": False},
    {"name": "Doc", "pattern": r"Doc:\s", "context_required": False},
    {"name": "LinkTo", "pattern": r"Link to:\s", "context_required": False},
    {"name": "SeeAlso", "pattern": r"See also:\s", "context_required": False},
    
    # Structural patterns
    {"name": "WikiLinkStart", "pattern": r"\[\[", "context_required": True},
    {"name": "xref", "pattern": r"<!-- TO_BE_REPLACED -->", "context_required": False},
    {"name": "REF_XYZ_Start", "pattern": r"\<!-- TO_BE_REPLACED -->", "context_required": False},
]

# Context patterns to determine if a reference should be purged
CONTEXT_PATTERNS = {
    # For relative paths, only purge when they appear to be references
    "RelativePathSelf": [
        r"\[.*?\]\(\.\/.*?\)",  # Markdown link with relative path
        r"href=\"\.\/.*?\"",     # HTML link with relative path
        r"from\s+\.\/",          # Python import with relative path
    ],
    "RelativePathParent": [
        r"\[.*?\]\(\.\.\/.*?\)",  # Markdown link with parent path
        r"href=\"\.\.\/.*?\"",     # HTML link with parent path
        r"from\s+\.\.\/",          # Python import with parent path
    ],
    # For wiki links, only purge complete wiki links
    "WikiLinkStart": [
        r"\[\[.*?\]\]",  # Complete wiki link
    ],
}

# File extensions to process
INCLUDE_EXTENSIONS = {
    '.md', '.py', '.yaml', '.yml', '.json', '.txt', '.sh', '.ps1', '.rst', '.tex', '.ini', '.cfg'
}

class ReferencePattern:
    """Class representing a reference pattern to purge."""
    
    def __init__(self, name: str, pattern: str, context_required: bool = False):
        self.name = name
        self.pattern = pattern
        self.context_required = context_required
        self.regex = re.compile(pattern)
        self.context_regexes = []
        
        # Compile context patterns if required
        if context_required and name in CONTEXT_PATTERNS:
            self.context_regexes = [re.compile(p) for p in CONTEXT_PATTERNS[name]]
    
    def matches(self, text: str) -> bool:
        """Check if the pattern matches the text."""
        if not self.context_required:
            return bool(self.regex.search(text))
        
        # For context-required patterns, check if any context pattern matches
        if not self.regex.search(text):
            return False
        
        return any(context.search(text) for context in self.context_regexes)

# Configuration section - can be moved to a separate YAML file in the future
CONFIG = {
    # Performance settings
    "batch_size": 100,  # Number of files to process in each batch
    "max_workers": 4,   # Maximum number of parallel workers
    "timeout": 30,      # Timeout for processing a single file (seconds)
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'purge_references.log'),
    "log_level": "INFO",
    
    # File processing settings
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "chunk_size": 8192,  # Read files in chunks of this size
    
    # Safety settings
    "max_replacements_per_file": 1000,  # Maximum number of replacements in a single file
}

# Add file handler to logger if configured
if CONFIG["log_file"]:
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    logger.info(f"Logging to file: {CONFIG['log_file']}")


"""
EGOS Script Standards Documentation

Based on analysis of file_reference_checker_ultra.py, the following standards
should be applied to all EGOS scripts:

1. Visual Elements
   - Use colorful banners for script headers and section divisions
   - Implement progress bars with ETA for long-running operations
   - Use Unicode box-drawing characters for structured output
   - Apply consistent color coding (e.g., cyan for descriptions, yellow for important info)

2. Performance Considerations
   - Process files in batches to prevent memory issues
   - Implement timeout mechanisms for operations that might hang
   - Use async/await for I/O-bound operations
   - Provide detailed progress tracking with accurate ETAs

3. Error Handling
   - Implement comprehensive try/except blocks with detailed error messages
   - Create backup mechanisms before destructive operations
   - Support dry-run modes for testing
   - Log all errors with contextual information

4. Code Structure
   - Use classes for encapsulation of related functionality
   - Implement comprehensive docstrings with parameter documentation
   - Organize imports logically (standard library first, then third-party)
   - Use type hints consistently

5. Configuration Management
   - Support YAML configuration files
   - Provide sensible defaults with clear documentation
   - Allow command-line overrides of configuration options
   - Validate configuration values before use

6. Logging
   - Configure both console and file logging
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
   - Include timestamps and context in log messages
   - Implement structured logging for machine-readable output

7. User Experience
   - Provide clear help messages and usage examples
   - Implement interactive confirmations for destructive operations
   - Display summary statistics at the end of operations
   - Support both interactive and non-interactive modes
"""

class ReferencePurger:
    """Enhanced class for purging old reference formats from files.
    
    Features:
    - Batch processing to prevent memory issues
    - Detailed progress tracking with ETA
    - Comprehensive error handling and reporting
    - Backup functionality for safe operations
    - Performance optimizations for large codebases
    """
    
    def __init__(self, base_path: str, dry_run: bool = True, backup: bool = True):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir = Path(BACKUP_DIR) / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.patterns = [ReferencePattern(**p) for p in PURGE_PATTERNS]
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "references_purged": 0,
            "patterns": {p.name: 0 for p in self.patterns},
            "errors": 0,
            "skipped_files": 0,
            "processing_time": 0,
        }
        
        # Create backup directory if needed
        if backup and not dry_run:
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.info(f"Created backup directory: {self.backup_dir}")

    
    def find_files(self) -> List[Path]:
        """Find all files to process with enhanced filtering."""
        logger.info(f"Finding files to process in {self.base_path}")

        
        # Create progress tracker for directory scanning
        scan_tracker = ProgressTracker(
            total=100,  # Placeholder, will be updated as we scan
            description="Scanning directories",
            unit="dirs"
        )
        
        files = []
        dirs_scanned = 0
        
        try:
            for root, dirs, filenames in os.walk(self.base_path):
                # Update progress
                dirs_scanned += 1
                if dirs_scanned % 10 == 0:  # Update every 10 directories
                    scan_tracker.update(10, f"Found {len(files)} files so far")
                
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    
                    # Apply filters
                    if file_path.suffix.lower() in INCLUDE_EXTENSIONS:
                        # Skip files that are too large
                        try:
                            if file_path.stat().st_size > CONFIG["max_file_size"]:
                                logger.warning(f"Skipping large file: {file_path} ({file_path.stat().st_size / 1024 / 1024:.2f} MB)")
                                self.stats["skipped_files"] += 1
                                continue
                        except Exception as e:
                            logger.warning(f"Error checking file size for {file_path}: {str(e)}")
                            continue
                        
                        files.append(file_path)
        finally:
            scan_tracker.close()
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def backup_file(self, file_path: Path) -> bool:
        """Create a backup of the file with enhanced error handling."""
        if not self.backup or self.dry_run:
            return True
        
        try:
            # Create relative path structure in backup directory
            rel_path = file_path.relative_to(self.base_path)
            backup_path = self.backup_dir / rel_path
            
            # Create parent directories if they don't exist
            os.makedirs(backup_path.parent, exist_ok=True)
            
            # Copy the file
            shutil.copy2(file_path, backup_path)
            return True
        
        except Exception as e:
            logger.error(f"Error backing up {file_path}: {str(e)}")
            return False
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file to purge old references with timeout protection."""
        result = {
            "file": str(file_path),
            "modified": False,
            "references_purged": 0,
            "patterns": {},
            "error": None,
            "processing_time": 0,
        }
        
        start_time = time.time()
        
        try:
            # Read file content with encoding error handling
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with error replacement
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    logger.warning(f"Encoding issues detected in {file_path}, using replacement mode")
            
            # Check if processing should time out
            if time.time() - start_time > CONFIG["timeout"]:
                raise TimeoutError(f"Processing timed out after {CONFIG['timeout']} seconds")
            
            # Check each pattern
            modified_content = content
            replacements_made = 0
            
            for pattern in self.patterns:
                # Skip further processing if we've hit the max replacements limit
                if replacements_made >= CONFIG["max_replacements_per_file"]:
                    logger.warning(f"Reached maximum replacements limit ({CONFIG['max_replacements_per_file']}) for {file_path}")
                    break
                
                # For context-required patterns, we need to check the whole content
                if pattern.context_required:
                    if pattern.matches(modified_content):
                        for context_regex in pattern.context_regexes:
                            matches = list(context_regex.finditer(modified_content))
                            if matches:
                                for match in reversed(matches):  # Process in reverse to maintain indices
                                    # Check timeout periodically
                                    if len(matches) > 100 and matches.index(match) % 100 == 0:
                                        if time.time() - start_time > CONFIG["timeout"]:
                                            raise TimeoutError(f"Processing timed out after {CONFIG['timeout']} seconds")
                                    
                                    # Only replace if it's not already in a crossref_block
                                    if "<!-- crossref_block:" not in modified_content[max(0, match.start()-50):match.start()]:
                                        modified_content = modified_content[:match.start()] + "<!-- TO_BE_REPLACED -->" + modified_content[match.end():]
                                        result["references_purged"] += 1
                                        replacements_made += 1
                                        result["patterns"][pattern.name] = result["patterns"].get(pattern.name, 0) + 1
                                        
                                        # Break if we've hit the limit
                                        if replacements_made >= CONFIG["max_replacements_per_file"]:
                                            break
                else:
                    # For non-context patterns, we can use simple replacement
                    matches = list(pattern.regex.finditer(modified_content))
                    if matches:
                        for match in reversed(matches):  # Process in reverse to maintain indices
                            # Check timeout periodically
                            if len(matches) > 100 and matches.index(match) % 100 == 0:
                                if time.time() - start_time > CONFIG["timeout"]:
                                    raise TimeoutError(f"Processing timed out after {CONFIG['timeout']} seconds")
                            
                            # Only replace if it's not already in a crossref_block
                            if "<!-- crossref_block:" not in modified_content[max(0, match.start()-50):match.start()]:
                                modified_content = modified_content[:match.start()] + "<!-- TO_BE_REPLACED -->" + modified_content[match.end():]
                                result["references_purged"] += 1
                                replacements_made += 1
                                result["patterns"][pattern.name] = result["patterns"].get(pattern.name, 0) + 1
                                
                                # Break if we've hit the limit
                                if replacements_made >= CONFIG["max_replacements_per_file"]:
                                    break
            
            # Check if content was modified
            if modified_content != content:
                result["modified"] = True
                
                # Backup and write changes if not in dry run mode
                if not self.dry_run:
                    if self.backup_file(file_path):
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
        
        except TimeoutError as e:
            result["error"] = str(e)
            logger.error(f"Timeout processing {file_path}: {str(e)}")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Record processing time
        result["processing_time"] = time.time() - start_time
        
        return result
    
    async def process_files_async(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files asynchronously in batches to prevent memory issues."""
        all_results = []
        total_files = len(files)
        
        # Create progress tracker
        progress = ProgressTracker(
            total=total_files,
            description="Purging references" if not self.dry_run else "Analyzing references (dry run)",
            unit="files"
        )
        
        # Process files in batches
        batch_size = CONFIG["batch_size"]
        num_batches = math.ceil(total_files / batch_size)
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_files = files[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_idx + 1}/{num_batches} ({len(batch_files)} files)")
            
            # Process batch with ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self.process_file, file_path): file_path
                    for file_path in batch_files
                }
                
                # Process results as they complete
                batch_results = []
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        batch_results.append(result)
                        
                        # Update progress with status
                        status = None
                        if result["modified"]:
                            status = f"Modified: {result['references_purged']} refs in {Path(result['file']).name}"

                        elif result["error"]:
                            status = f"Error: {Path(result['file']).name}"

                        
                        progress.update(1, status)
                        
                    except Exception as e:
                        logger.error(f"Exception processing {file_path}: {str(e)}")
                        progress.update(1, f"Exception: {file_path.name}")
                        batch_results.append({
                            "file": str(file_path),
                            "modified": False,
                            "references_purged": 0,
                            "patterns": {},
                            "error": str(e),
                            "processing_time": 0,
                        })
            
            # Add batch results to all results
            all_results.extend(batch_results)
            
            # Allow event loop to process other tasks
            await asyncio.sleep(0.1)
        
        # Close progress tracker
        progress.close()
        progress.display_summary()
        
        return all_results
    
    def process_files(self, files: List[Path]) -> None:
        """Process multiple files with enhanced error handling and reporting."""
        logger.info(f"Processing {len(files)} files with {CONFIG['max_workers']} workers")
        
        # Run the async processing
        start_time = time.time()
        results = asyncio.run(self.process_files_async(files))
        total_time = time.time() - start_time
        
        # Update stats
        self.stats["files_processed"] = len(files)
        self.stats["files_modified"] = sum(1 for r in results if r["modified"])
        self.stats["references_purged"] = sum(r["references_purged"] for r in results)
        self.stats["errors"] = sum(1 for r in results if r["error"])
        self.stats["processing_time"] = total_time
        
        # Update pattern stats
        for result in results:
            for pattern_name, count in result.get("patterns", {}).items():
                self.stats["patterns"][pattern_name] = self.stats["patterns"].get(pattern_name, 0) + count
        
        # Generate report
        self.generate_report(results)
    
    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """Generate a comprehensive report of the purge operation with rich formatting."""
        logger.info("Generating purge report")
        
        # Create report directory if it doesn't exist
        report_dir = Path(INVENTORY_DIR)
        os.makedirs(report_dir, exist_ok=True)
        
        # Report filename
        mode = "dry_run" if self.dry_run else "actual"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = report_dir / f"purge_report_{mode}_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Title and metadata with EGOS styling
            f.write(f"# EGOS Cross-Reference Purge Report ({mode.upper()})\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Part of:** Cross-Reference Standardization Initiative (Phase 2: Purge Outdated Formats)\n\n")
            
            # Executive summary with enhanced formatting
            f.write("## 📊 Executive Summary\n\n")
            f.write("This report presents the results of the purge operation for outdated reference formats.\n\n")
            f.write(f"- **Mode:** {'🔍 Dry Run (no changes made)' if self.dry_run else '✅ Actual (changes applied)'}\n")
            f.write(f"- **Files Processed:** {self.stats['files_processed']:,}\n")
            f.write(f"- **Files Modified:** {self.stats['files_modified']:,}\n")
            f.write(f"- **References Purged:** {self.stats['references_purged']:,}\n")
            f.write(f"- **Errors:** {self.stats['errors']:,}\n")
            f.write(f"- **Skipped Files:** {self.stats['skipped_files']:,}\n")
            f.write(f"- **Processing Time:** {format_time(self.stats['processing_time'])}\n")
            
            if not self.dry_run and self.backup:
                f.write(f"- **Backup Directory:** `{self.backup_dir}`\n")
            
            # Pattern statistics with visual enhancements
            f.write("\n## 📈 Pattern Statistics\n\n")
            f.write("| Pattern | Count | Percentage | Example |\n")
            f.write("|---------|-------|------------|--------|\n")
            
            # Get examples for each pattern
            pattern_examples = {}
            for result in results:
                if result["modified"]:
                    for pattern_name in result["patterns"]:
                        if pattern_name not in pattern_examples:
                            pattern_examples[pattern_name] = result["file"]
            
            for pattern_name, count in sorted(self.stats["patterns"].items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    percentage = (count / self.stats["references_purged"]) * 100 if self.stats["references_purged"] > 0 else 0
                    example = f"`{Path(pattern_examples.get(pattern_name, '')).name}`" if pattern_name in pattern_examples else "N/A"
                    f.write(f"| `{pattern_name}` | {count:,} | {percentage:.2f}% | {example} |\n")
            
            # Performance analysis
            f.write(f"\n## ⚡ Performance Analysis\n\n")
            
            # Calculate processing times
            processing_times = [r["processing_time"] for r in results if r["processing_time"] > 0]
            if processing_times:
                avg_time = sum(processing_times) / len(processing_times)
                max_time = max(processing_times)
                min_time = min(processing_times)
                
                # Find slowest files
                slowest_files = sorted(results, key=lambda x: x["processing_time"], reverse=True)[:5]
                
                f.write(f"- **Average Processing Time:** {avg_time:.2f} seconds per file\n")
                f.write(f"- **Maximum Processing Time:** {max_time:.2f} seconds\n")
                f.write(f"- **Minimum Processing Time:** {min_time:.2f} seconds\n")
                
                f.write(f"\n### Slowest Files\n\n")
                for result in slowest_files:
                    if result["processing_time"] > 0:
                        f.write(f"- **{Path(result['file']).name}** - {result['processing_time']:.2f} seconds\n")
            
            # Modified files with enhanced details
            f.write(f"\n## 🔄 Modified Files\n\n")
            
            modified_files = [r for r in results if r["modified"]]
            if modified_files:
                f.write(f"The following {len(modified_files):,} files were modified:\n\n")
                
                # Group by directory for better organization
                dir_groups = {}
                for result in modified_files:
                    file_path = Path(result["file"])
                    try:
                        # Check if base_path is part of the file path
                        if str(self.base_path) in str(file_path):
                            parent = str(file_path.parent.relative_to(self.base_path))
                        else:
                            parent = str(file_path.parent)
                        if parent not in dir_groups:
                            dir_groups[parent] = []
                        dir_groups[parent].append(result)
                    except Exception as e:
                        logger.warning(f"Error grouping file {file_path}: {str(e)}")
                        # Use a fallback group
                        if "Other" not in dir_groups:
                            dir_groups["Other"] = []
                        dir_groups["Other"].append(result)
                
                # Display top directories with most changes
                f.write(f"### Top Directories\n\n")
                for dir_path, files in sorted(dir_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                    f.write(f"- **{dir_path}** - {len(files):,} files modified\n")
                
                # Display top files with most references purged
                f.write(f"\n### Top Files by References Purged\n\n")
                for result in sorted(modified_files, key=lambda x: x["references_purged"], reverse=True)[:20]:
                    patterns = ", ".join([f"`{p}`" for p in result["patterns"].keys()])
                    f.write(f"- **{result['file']}** - {result['references_purged']:,} references purged ({patterns})\n")
                
                if len(modified_files) > 20:
                    f.write(f"\n... and {len(modified_files) - 20:,} more files.\n")
            else:
                f.write(f"No files were modified.\n")
            
            # Errors with categorization
            f.write(f"\n## ⚠️ Errors\n\n")
            
            error_files = [r for r in results if r["error"]]
            if error_files:
                # Categorize errors
                error_categories = {}
                for result in error_files:
                    error_msg = result["error"]
                    category = "Timeout" if "timeout" in error_msg.lower() else \
                              "Encoding" if "encoding" in error_msg.lower() or "codec" in error_msg.lower() else \
                              "Permission" if "permission" in error_msg.lower() else \
                              "Other"
                    
                    if category not in error_categories:
                        error_categories[category] = []
                    error_categories[category].append(result)
                
                f.write(f"Encountered {len(error_files):,} errors during processing:\n\n")
                
                # Display error summary by category
                f.write(f"### Error Summary\n\n")
                f.write(f"| Category | Count | Percentage |\n")
                f.write(f"|----------|-------|------------|\n")
                
                for category, errors in sorted(error_categories.items(), key=lambda x: len(x[1]), reverse=True):
                    percentage = (len(errors) / len(error_files)) * 100
                    f.write(f"| {category} | {len(errors):,} | {percentage:.2f}% |\n")
                
                # Display examples of each error category
                f.write(f"\n### Error Examples\n\n")
                for category, errors in sorted(error_categories.items(), key=lambda x: len(x[1]), reverse=True):
                    f.write(f"#### {category} Errors\n\n")
                    for result in errors[:5]:  # Show up to 5 examples per category
                        f.write(f"- **{result['file']}** - {result['error']}\n")
                    
                    if len(errors) > 5:
                        f.write(f"... and {len(errors) - 5:,} more {category.lower()} errors.\n\n")
            else:
                f.write(f"No errors were encountered during processing.\n")
            
            # Next steps with detailed recommendations
            f.write(f"\n## 🚀 Next Steps\n\n")
            
            if self.dry_run:
                f.write(f"1. **Review this report** to confirm the changes are as expected\n")
                f.write(f"2. **Run the purge script in actual mode** to apply the changes:\n\n")
                f.write(f"   ```bash\n   python scripts/cross_reference/purge_old_references.py\n   ```\n\n")
                f.write(f"3. **Proceed to Phase 3** (Hierarchical Injection of Standardized References)\n")
            else:
                f.write(f"1. **Verify the changes** made by the purge operation\n")
                f.write(f"2. **Restore from backup** if needed:\n\n")
                f.write(f"   ```bash\n   # Example restoration command\n   cp -r {self.backup_dir}/* {self.base_path}/\n   ```\n\n")
                f.write(f"3. **Proceed to Phase 3** (Hierarchical Injection of Standardized References)\n")
            
            # Add EGOS signature
            f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path

def main():
    """Main function to run the purge script with enhanced user experience."""
    parser = argparse.ArgumentParser(
        description="Purge outdated reference formats from the EGOS codebase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Run in dry-run mode (no changes made)
  python purge_old_references.py --dry-run
  
  # Run in actual mode with 8 worker threads
  python purge_old_references.py --workers 8
  
  # Run without creating backups (use with caution)
  python purge_old_references.py --no-backup

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    parser.add_argument("--base-path", default="C:\\EGOS", help="Base path to process")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backups")
    parser.add_argument("--workers", type=int, default=CONFIG["max_workers"], help="Number of worker threads")
    parser.add_argument("--batch-size", type=int, default=CONFIG["batch_size"], help="Number of files to process in each batch")
    parser.add_argument("--timeout", type=int, default=CONFIG["timeout"], help="Timeout for processing a single file (seconds)")
    parser.add_argument("--max-file-size", type=int, default=CONFIG["max_file_size"], help="Maximum file size to process in bytes")
    args = parser.parse_args()
    
    # Update configuration from command line arguments
    CONFIG["max_workers"] = args.workers
    CONFIG["batch_size"] = args.batch_size
    CONFIG["timeout"] = args.timeout
    CONFIG["max_file_size"] = args.max_file_size
    
    # Display banner
    print_banner(
        "EGOS Cross-Reference Purge Script",
        f"Version 1.0.0 - {datetime.now().strftime('%Y-%m-%d')}"
    )
    
    # Display mode
    mode_text = "DRY RUN MODE (no changes will be made)" if args.dry_run else "ACTUAL MODE (changes will be applied)"
    logger.info(f"{Fore.YELLOW}{mode_text}{Style.RESET_ALL}")
    
    # Confirm if not in dry run mode
    if not args.dry_run:
        print(f"\n{Fore.RED}WARNING: You are about to run in ACTUAL mode, which will modify files.{Style.RESET_ALL}")
        print(f"Backup {'will NOT' if args.no_backup else 'will'} be created.\n")
        
        try:
            confirm = input(f"Type 'yes' to continue or anything else to abort: ")
            if confirm.lower() != "yes":
                logger.info("Operation aborted by user.")
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info("Operation aborted by user.")
            sys.exit(0)
    
    try:
        # Create purger
        purger = ReferencePurger(
            base_path=args.base_path,
            dry_run=args.dry_run,
            backup=not args.no_backup
        )
        
        # Find files to process
        files = purger.find_files()
        
        # Process files
        purger.process_files(files)
        
        # Display summary
        logger.info(f"\n{Fore.GREEN}Reference purge completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files processed:{Style.RESET_ALL} {purger.stats['files_processed']:,}")
        logger.info(f"  • {Fore.CYAN}Files modified:{Style.RESET_ALL} {purger.stats['files_modified']:,}")
        logger.info(f"  • {Fore.CYAN}References purged:{Style.RESET_ALL} {purger.stats['references_purged']:,}")
        logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {purger.stats['errors']:,}")
        logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(purger.stats['processing_time'])}")
        
        if args.dry_run:
            logger.info(f"\n{Fore.YELLOW}This was a dry run. No changes were made.{Style.RESET_ALL}")
            logger.info(f"To apply changes, run without the --dry-run flag.")
        elif purger.backup:
            logger.info(f"\n{Fore.CYAN}Backup created at:{Style.RESET_ALL} {purger.backup_dir}")
    
    except KeyboardInterrupt:
        logger.info("\nOperation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n{Fore.RED}Error during execution:{Style.RESET_ALL} {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()