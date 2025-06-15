#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc_organizer.py

Recursively scans a target directory and deletes any empty subdirectories found.
Provides detailed logging of operations and supports a dry-run mode to preview changes.
This script is part of the EGOS project's efforts to maintain a clean and organized
documentation structure.

Author: EGOS Development Team
Created: 2025-05-23
Version: 1.0.0

@references:
- C:\EGOS\MQP.md (Master Quantum Prompt)
- C:\EGOS\docs\standards\scripting\script_management_best_practices.md
- C:\EGOS\docs\work_logs\WORK_2025-05-23_Docs_Reorg_Initial_Cleanup_Log.md (Context for creation)
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
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Union, Callable
import textwrap
import stat
from collections import defaultdict, Counter

# Third-party imports
from tqdm import tqdm
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

# Configuration
script_filename = os.path.basename(__file__)
script_name = Path(script_filename).stem
CONFIG = {
    # Add your configuration settings here
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', f'{script_filename.replace(".py", ".log")}'),
    "log_level": "INFO",
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

logger = logging.getLogger(script_name) # Use stem for logger name

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

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

class ProgressTracker:
    """Enhanced progress tracking with ETA and visual feedback."""
    
    def __init__(self, total: int, description: str = "Processing", unit: str = "items"):
        """Initialize the progress tracker.
        
        Args:
            total: Total number of items to process
            description: Description of the progress bar
            unit: Unit of measurement for the progress bar
        """
        self.total = total
        self.description = description
        self.unit = unit
        self.processed = 0
        self.start_time = time.time()
        
        # Create progress bar
        self.pbar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}{description}{Style.RESET_ALL}",
            unit=unit,
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
    
    def update(self, n: int = 1) -> None:
        """Update progress by n units.
        
        Args:
            n: Number of units to update by
        """
        self.processed += n
        self.pbar.update(n)
    
    def close(self) -> None:
        """Close the progress bar."""
        self.pbar.close()



# Helper functions to extract metadata from the docstring
def get_script_metadata(script_docstring: Optional[str]) -> Dict[str, str]:
    """Extracts metadata like Author, Version, Created from the script's docstring."""
    metadata = {}
    if script_docstring:
        for line in script_docstring.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in ["Author", "Version", "Created"]:
                    metadata[key] = value
    return metadata

def get_script_description(script_docstring: Optional[str] = __doc__) -> str:
    """Extracts the main description from the script's docstring."""
    if script_docstring:
        lines = [line for line in script_docstring.strip().split('\n') if ':' not in line or not any(m in line for m in ["Author:", "Version:", "Created:", "@references:"])]
        description = "\n".join(lines).strip()
        first_line = description.split('\n')[0].strip()
        # script_filename and script_name are assumed to be globally available in the script
        if script_filename.lower() in first_line.lower() or script_name.lower() in first_line.lower():
            description = "\n".join(description.split('\n')[1:]).strip()
        return description
    return "No description available."

_script_metadata_cache = None # Global cache for metadata

def get_script_author(script_docstring: Optional[str] = __doc__) -> str:
    """Extracts the Author from the script's docstring."""
    global _script_metadata_cache
    if _script_metadata_cache is None:
        _script_metadata_cache = get_script_metadata(script_docstring)
    return _script_metadata_cache.get("Author", "Unknown Author")

def get_script_version(script_docstring: Optional[str] = __doc__) -> str:
    """Extracts the Version from the script's docstring."""
    global _script_metadata_cache
    if _script_metadata_cache is None:
        _script_metadata_cache = get_script_metadata(script_docstring)
    return _script_metadata_cache.get("Version", "0.0.0")

def get_creation_date(script_docstring: Optional[str] = __doc__) -> str:
    """Extracts the Creation Date from the script's docstring."""
    global _script_metadata_cache
    if _script_metadata_cache is None:
        _script_metadata_cache = get_script_metadata(script_docstring)
    return _script_metadata_cache.get("Created", "Unknown Date")


class BaseProcessor:
    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "errors": 0,
            "processing_time": 0,
        }

class DocOrganizer(BaseProcessor):
    """Handles the logic for scanning and deleting empty directories."""
    
    def __init__(self, base_path: str, dry_run: bool = False, log_level: str = "INFO", interactive: bool = False):
        """Initialize the DocOrganizer.

        Args:
            base_path (str): The root directory to scan.
            dry_run (bool): If True, no directories will be deleted (simulation mode).
            log_level (str): The logging level (e.g., INFO, DEBUG).
            interactive (bool): If True, enables interactive mode for user input.
            
        Raises:
            ValueError: If log_level is not a valid logging level.
            IOError: If log file cannot be created or written to.
        """
        super().__init__()
        
        # Validate and normalize inputs with error handling
        try:
            # Validate base_path
            if not base_path or not isinstance(base_path, (str, Path)):
                raise ValueError(f"Invalid base_path: {base_path}. Must be a non-empty string or Path object.")
                
            self.base_path = Path(base_path)
            
            # Validate log_level
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            self.log_level = log_level.upper()
            if self.log_level not in valid_log_levels:
                raise ValueError(f"Invalid log_level: {log_level}. Must be one of {valid_log_levels}")
                
            # Set dry_run flag
            self.dry_run = bool(dry_run)  # Ensure it's a boolean
            
            # Set interactive mode flag
            self.interactive = bool(interactive)  # Ensure it's a boolean
            
            # Setup logger level with error handling
            logger.setLevel(self.log_level)
            
            # Add file handler if configured and not already added by basicConfig
            if CONFIG.get("log_file"):
                log_file_path = CONFIG["log_file"]
                log_dir = os.path.dirname(log_file_path)
                
                try:
                    # Create log directory if it doesn't exist
                    os.makedirs(log_dir, exist_ok=True)
                    
                    # Check if log file is writable or can be created
                    if os.path.exists(log_file_path) and not os.access(log_file_path, os.W_OK):
                        raise IOError(f"Log file exists but is not writable: {log_file_path}")
                    elif not os.path.exists(log_file_path) and not os.access(log_dir, os.W_OK):
                        raise IOError(f"Cannot create log file in directory: {log_dir}. Check permissions.")
                    
                    # Only add file handler if not already present
                    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
                        file_handler = logging.FileHandler(log_file_path)
                        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                        logger.addHandler(file_handler)
                        logger.debug(f"Added file handler for log file: {log_file_path}")
                except (IOError, OSError) as e:
                    # Log the error but continue without file logging
                    logger.error(f"Failed to set up log file {log_file_path}: {str(e)}")
                    logger.error("Continuing with console logging only.")
            
            # Initialize statistics dictionary with detailed tracking
            self.stats.update({
                "empty_directories_list": [],  # List to store paths of empty directories
                "directories_scanned": 0,
                "empty_directories_found": 0,
                "directories_deleted": 0,
                "errors": 0,
                "error_details": [],  # List to store detailed error information
                "inaccessible_directories": 0,
                "processing_time": 0.0,
                "start_time": time.time(),
                "end_time": None
            })
            
            # Log initialization information
            logger.info(f"Initializing {script_name} v{get_script_version()} with base path: {self.base_path}")
            logger.info(f"Log level set to: {self.log_level}")
            if self.dry_run:
                logger.warning("Dry run mode enabled. No changes will be made.")
                
        except Exception as e:
            # Catch any initialization errors and log them
            error_msg = f"Error initializing DocOrganizer: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            
            # Re-raise with more context to ensure proper handling upstream
            raise RuntimeError(f"Failed to initialize DocOrganizer: {str(e)}") from e

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file with timeout protection and enhanced error handling.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results including detailed error information if applicable
            
        Note:
            This method is designed to be robust against various file-related errors and will
            never raise exceptions to the caller. All errors are captured in the returned dictionary.
        """
        # Initialize result dictionary with detailed tracking
        result = {
            "file": str(file_path),
            "modified": False,
            "error": None,
            "error_type": None,
            "error_details": {},
            "processing_time": 0,
            "recoverable": True,  # Assume errors are recoverable by default
            "operation": "file_processing"
        }
        
        start_time = time.time()
        
        # Validate input
        if not file_path or not isinstance(file_path, Path):
            result["error"] = f"Invalid file path: {file_path}"
            result["error_type"] = "ValueError"
            result["recoverable"] = False
            return result
        
        try:
            # Enhanced file existence and permission checking with specific error types
            if not file_path.exists():
                result["error"] = f"File does not exist: {file_path}"
                result["error_type"] = "FileNotFoundError"
                result["error_details"] = {
                    "path": str(file_path),
                    "suggestion": "Verify the file path or check if it was deleted during processing."
                }
                return result
            
            if not os.path.isfile(file_path):
                result["error"] = f"Path exists but is not a file: {file_path}"
                result["error_type"] = "IsADirectoryError"
                result["error_details"] = {
                    "path": str(file_path),
                    "is_dir": os.path.isdir(file_path),
                    "suggestion": "Ensure the path points to a file, not a directory or other special file."
                }
                return result
                
            if not os.access(file_path, os.R_OK):
                result["error"] = f"File exists but is not readable (permission denied): {file_path}"
                result["error_type"] = "PermissionError"
                result["error_details"] = {
                    "path": str(file_path),
                    "suggestion": "Check file permissions or run the script with elevated privileges."
                }
                return result
            
            # TODO: Implement file processing logic
            # This is a placeholder for actual file processing that would be implemented
            # based on the specific requirements of the script.
            
            # Example implementation with proper error handling:
            try:
                # Simulate file reading with timeout protection
                # with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                #     content = f.read()
                
                # Process content (placeholder)
                # modified_content = content
                
                # Write changes if not in dry-run mode and content was modified
                # if not self.dry_run and modified_content != content:
                #     # Check write permissions before attempting to write
                #     if not os.access(file_path, os.W_OK):
                #         raise PermissionError(f"File is not writable: {file_path}")
                #         
                #     # Create backup before writing (optional safety measure)
                #     # backup_path = f"{file_path}.bak"
                #     # shutil.copy2(file_path, backup_path)
                #     
                #     # Write with error handling
                #     with open(file_path, 'w', encoding='utf-8') as f:
                #         f.write(modified_content)
                #     
                #     result["modified"] = True
                #     result["backup_created"] = True  # If backup was created
                #     logger.info(f"Successfully modified file: {file_path}")
                pass  # Remove this when implementing actual logic
                
            except UnicodeDecodeError as e:
                result["error"] = f"Unicode decode error while reading file: {str(e)}"
                result["error_type"] = "UnicodeDecodeError"
                result["error_details"] = {
                    "path": str(file_path),
                    "encoding_attempted": "utf-8",
                    "suggestion": "File may be binary or use a different encoding."
                }
                result["recoverable"] = False
                logger.error(f"Unicode decode error processing {file_path}: {str(e)}")
                
            except PermissionError as e:
                result["error"] = f"Permission denied while writing to file: {str(e)}"
                result["error_type"] = "PermissionError"
                result["error_details"] = {
                    "path": str(file_path),
                    "operation": "write",
                    "suggestion": "Check file permissions or if file is locked by another process."
                }
                result["recoverable"] = False
                logger.error(f"Permission error processing {file_path}: {str(e)}")
                
            except IOError as e:
                result["error"] = f"IO error while processing file: {str(e)}"
                result["error_type"] = "IOError"
                result["error_details"] = {
                    "path": str(file_path),
                    "errno": getattr(e, 'errno', None),
                    "suggestion": "Check disk space, file locks, or network issues if on a network drive."
                }
                result["recoverable"] = False
                logger.error(f"IO error processing {file_path}: {str(e)}")
                
        except FileNotFoundError as e:
            # This could happen if the file was deleted between the existence check and processing
            result["error"] = f"File disappeared during processing: {str(e)}"
            result["error_type"] = "FileNotFoundError"
            result["error_details"] = {
                "path": str(file_path),
                "suggestion": "File may have been deleted by another process during scanning."
            }
            logger.warning(f"File disappeared during processing: {file_path}")
            
        except PermissionError as e:
            result["error"] = f"Permission denied: {str(e)}"
            result["error_type"] = "PermissionError"
            result["error_details"] = {
                "path": str(file_path),
                "suggestion": "Check file permissions or run with elevated privileges."
            }
            result["recoverable"] = False
            logger.error(f"Permission error accessing {file_path}: {str(e)}")
            
        except OSError as e:
            result["error"] = f"OS error: {str(e)}"
            result["error_type"] = "OSError"
            result["error_details"] = {
                "path": str(file_path),
                "errno": getattr(e, 'errno', None),
                "suggestion": "Check system resources, disk space, or file system integrity."
            }
            result["recoverable"] = False
            logger.error(f"OS error processing {file_path}: {str(e)}")
            
        except Exception as e:
            # Catch-all for unexpected errors
            result["error"] = f"Unexpected error: {str(e)}"
            result["error_type"] = type(e).__name__
            result["error_details"] = {
                "path": str(file_path),
                "exception_type": type(e).__name__,
                "suggestion": "This is an unexpected error. Please report it with the full stack trace."
            }
            result["recoverable"] = False
            logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            logger.exception("Exception details:")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        result["processing_time"] = processing_time
        
        # Log processing outcome
        if result["error"]:
            # Add to global error stats if there was an error
            self.stats["errors"] += 1
            self.stats["error_details"] = self.stats.get("error_details", []) + [{
                "type": result["error_type"],
                "path": str(file_path),
                "message": result["error"],
                "operation": "process_file",
                "recoverable": result["recoverable"],
                "details": result["error_details"]
            }]
        elif result["modified"]:
            logger.info(f"Successfully processed and modified {file_path} in {format_time(processing_time)}")
        else:
            logger.debug(f"Processed {file_path} (no changes needed) in {format_time(processing_time)}")
        
        return result
    
    def run(self) -> None:
        """Run the main processing logic to find and delete empty directories."""
        start_time = time.time()
        logger.info(f"Starting scan in {self.base_path}...")

        # Enhanced base path validation with specific error types
        try:
            if not self.base_path.exists():
                error_msg = f"Base path {self.base_path} does not exist."
                logger.error(error_msg)
                self.stats["errors"] += 1
                self.stats["error_details"] = self.stats.get("error_details", []) + [{
                    "type": "FileNotFoundError",
                    "path": str(self.base_path),
                    "message": error_msg,
                    "recoverable": False
                }]
                self.stats["processing_time"] = time.time() - start_time
                return
            
            if not self.base_path.is_dir():
                error_msg = f"Base path {self.base_path} exists but is not a directory."
                logger.error(error_msg)
                self.stats["errors"] += 1
                self.stats["error_details"] = self.stats.get("error_details", []) + [{
                    "type": "NotADirectoryError",
                    "path": str(self.base_path),
                    "message": error_msg,
                    "recoverable": False
                }]
                self.stats["processing_time"] = time.time() - start_time
                return
            
            # Check for read permissions on base path
            if not os.access(self.base_path, os.R_OK):
                error_msg = f"Base path {self.base_path} exists but is not readable. Check permissions."
                logger.error(error_msg)
                self.stats["errors"] += 1
                self.stats["error_details"] = self.stats.get("error_details", []) + [{
                    "type": "PermissionError",
                    "path": str(self.base_path),
                    "message": error_msg,
                    "recoverable": False
                }]
                self.stats["processing_time"] = time.time() - start_time
                return
        except Exception as e:
            # Catch any unexpected errors during validation
            error_msg = f"Unexpected error validating base path {self.base_path}: {str(e)}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            self.stats["errors"] += 1
            self.stats["error_details"] = self.stats.get("error_details", []) + [{
                "type": type(e).__name__,
                "path": str(self.base_path),
                "message": error_msg,
                "recoverable": False
            }]
            self.stats["processing_time"] = time.time() - start_time
            return

        # Initialize error tracking for specific directories
        self.stats["inaccessible_directories"] = 0
        self.stats["error_details"] = self.stats.get("error_details", [])

        try:
            # We walk bottom-up to ensure child directories are processed before parents
            for dirpath, dirnames, filenames in os.walk(self.base_path, topdown=False):
                current_dir = Path(dirpath)
                self.stats["directories_scanned"] += 1
                
                # Log initial state from os.walk
                logger.debug(f"Scanning directory: {current_dir}. os.walk - dirnames: {dirnames}, filenames: {filenames}")

                try:
                    # Get actual current contents using os.listdir()
                    current_actual_contents = os.listdir(current_dir)
                    is_truly_empty = not current_actual_contents # Empty if os.listdir returns an empty list

                    # Specific debugging for parent_dir_2 related paths
                    if 'parent_dir_2' in str(current_dir):
                        logger.info(f"{Fore.MAGENTA}[DEBUG PARENT_DIR_2]{Style.RESET_ALL} Path: {current_dir}, "
                                    f"os.walk dirnames: {dirnames}, os.walk filenames: {filenames}, "
                                    f"os.listdir() actual_contents: {current_actual_contents}, is_truly_empty: {is_truly_empty}")

                    if is_truly_empty:
                        self.stats["empty_directories_found"] += 1
                        # Store the path of the empty directory for later use
                        self.stats["empty_directories_list"].append(str(current_dir))
                        logger.info(f"{Fore.YELLOW}[EMPTY]{Style.RESET_ALL} Directory confirmed empty by os.listdir: {current_dir}")
                        
                        if not self.dry_run:
                            # Enhanced error handling for directory deletion
                            max_retries = 3
                            retry_count = 0
                            deletion_success = False
                            last_error = None
                            
                            while retry_count < max_retries and not deletion_success:
                                try:
                                    os.rmdir(current_dir)
                                    logger.warning(f"{Fore.GREEN}Deleted empty directory: {current_dir}{Style.RESET_ALL}")
                                    self.stats["directories_deleted"] += 1
                                    deletion_success = True
                                except PermissionError as e:
                                    last_error = e
                                    error_msg = f"Permission denied when deleting directory {current_dir}: {e}"
                                    logger.error(error_msg)
                                    # Only increment retry for permission errors, they might be temporary
                                    retry_count += 1
                                    if retry_count < max_retries:
                                        logger.info(f"Retrying deletion of {current_dir} (attempt {retry_count+1}/{max_retries})...")
                                        time.sleep(0.5)  # Brief pause before retry
                                except FileNotFoundError as e:
                                    # This could happen if another process deleted the directory
                                    logger.warning(f"Directory {current_dir} no longer exists, possibly deleted by another process: {e}")
                                    # Count as success since the directory is gone
                                    self.stats["directories_deleted"] += 1
                                    deletion_success = True
                                except OSError as e:
                                    last_error = e
                                    error_msg = f"OS error when deleting directory {current_dir}: {e}"
                                    logger.error(error_msg)
                                    # Break immediately for other OS errors as they're likely not transient
                                    break
                                except Exception as e:
                                    last_error = e
                                    error_msg = f"Unexpected error when deleting directory {current_dir}: {e}"
                                    logger.error(error_msg)
                                    logger.exception("Exception details:")
                                    # Break immediately for unexpected errors
                                    break
                            
                            # If deletion failed after retries, record the error
                            if not deletion_success:
                                self.stats["errors"] += 1
                                self.stats["error_details"].append({
                                    "type": type(last_error).__name__ if last_error else "UnknownError",
                                    "path": str(current_dir),
                                    "message": str(last_error) if last_error else "Unknown error during directory deletion",
                                    "operation": "delete_directory",
                                    "recoverable": False
                                })
                        else:
                            logger.info(f"[DRY RUN] Would delete empty directory: {current_dir}")
                    else:
                        # This 'else' is for when os.listdir() shows it's not empty
                        logger.debug(f"Directory not empty (checked by os.listdir): {current_dir}, Actual Contents: {current_actual_contents}")
                        if 'parent_dir_2' in str(current_dir) and not self.dry_run: # More debug for non-dry-run
                             logger.info(f"{Fore.CYAN}[NOT TRULY EMPTY DEBUG]{Style.RESET_ALL} Directory {current_dir} not deleted. "
                                         f"os.listdir() actual_contents: {current_actual_contents}. "
                                         f"Original os.walk dirnames: {dirnames}, filenames: {filenames}")

                except PermissionError as e_perm:
                    error_msg = f"Permission denied when accessing directory {current_dir}: {e_perm}"
                    logger.error(error_msg)
                    self.stats["errors"] += 1
                    self.stats["inaccessible_directories"] += 1
                    self.stats["error_details"].append({
                        "type": "PermissionError",
                        "path": str(current_dir),
                        "message": error_msg,
                        "operation": "list_directory",
                        "recoverable": False
                    })
                except FileNotFoundError as e_not_found:
                    error_msg = f"Directory {current_dir} not found (possibly deleted during scan): {e_not_found}"
                    logger.warning(error_msg)  # Warning, not error, as this might be expected in some cases
                    # Don't increment error count for this case
                    self.stats["error_details"].append({
                        "type": "FileNotFoundError",
                        "path": str(current_dir),
                        "message": error_msg,
                        "operation": "list_directory",
                        "recoverable": True  # This is recoverable as we can just skip this directory
                    })
                except OSError as e_os:
                    error_msg = f"OS error listing directory {current_dir}: {e_os}"
                    logger.error(error_msg)
                    self.stats["errors"] += 1
                    self.stats["error_details"].append({
                        "type": "OSError",
                        "path": str(current_dir),
                        "message": error_msg,
                        "operation": "list_directory",
                        "recoverable": False
                    })
                    # Specific debugging for parent_dir_2 related paths even on listdir error
                    if 'parent_dir_2' in str(current_dir):
                        logger.info(f"{Fore.RED}[DEBUG PARENT_DIR_2 - LISTDIR ERROR]{Style.RESET_ALL} Path: {current_dir}, "
                                    f"os.walk dirnames: {dirnames}, os.walk filenames: {filenames}. Error: {e_os}")
                except Exception as e_unexpected:
                    error_msg = f"Unexpected error processing directory {current_dir}: {e_unexpected}"
                    logger.error(error_msg)
                    logger.exception("Exception details:")
                    self.stats["errors"] += 1
                    self.stats["error_details"].append({
                        "type": type(e_unexpected).__name__,
                        "path": str(current_dir),
                        "message": error_msg,
                        "operation": "list_directory",
                        "recoverable": False
                    })
        except Exception as e_walk:
            # Handle errors in the os.walk itself
            error_msg = f"Error during directory traversal: {e_walk}"
            logger.error(error_msg)
            logger.exception("Exception details:")
            self.stats["errors"] += 1
            self.stats["error_details"].append({
                "type": type(e_walk).__name__,
                "path": str(self.base_path),
                "message": error_msg,
                "operation": "walk_directory_tree",
                "recoverable": False
            })

        # Calculate final processing time
        self.stats["processing_time"] = time.time() - start_time
        
        # Generate summary of errors if any occurred
        if self.stats["errors"] > 0:
            logger.warning(f"Completed with {self.stats['errors']} errors. See log for details.")
            if self.stats.get("inaccessible_directories", 0) > 0:
                logger.warning(f"Could not access {self.stats['inaccessible_directories']} directories due to permission issues.")
        else:
            logger.info("Scan completed successfully with no errors.")
            
        # Log summary statistics
        logger.info(f"Scan summary: {self.stats['directories_scanned']} directories scanned, "
                   f"{self.stats['empty_directories_found']} empty directories found, "
                   f"{self.stats['directories_deleted']} directories deleted.")
        logger.info(f"Total processing time: {format_time(self.stats['processing_time'])}")
        
        # Return detailed error report if requested and errors occurred
        if self.log_level == "DEBUG" and self.stats["errors"] > 0:
            logger.debug("Detailed error report:")
            for i, error in enumerate(self.stats.get("error_details", [])):
                logger.debug(f"Error {i+1}: {error['type']} - {error['message']} (Path: {error['path']})")
                
        logger.info("Scan complete.")
        
        # Return success status
        return self.stats["errors"] == 0

def delete_empty_directories(organizer: DocOrganizer) -> bool:
    """Delete all empty directories found during the scan.
    
    Args:
        organizer: DocOrganizer instance with scan results
        
    Returns:
        bool: True if all deletions were successful, False otherwise
    """
    if not organizer.stats.get("empty_directories_list"):
        print(f"\n{Fore.YELLOW}No empty directories to delete.{Style.RESET_ALL}")
        return True
    
    print(f"\n{Fore.CYAN}Deleting {len(organizer.stats['empty_directories_list'])} empty directories...{Style.RESET_ALL}")
    
    success = True
    deleted_count = 0
    errors = 0
    
    # Create a progress tracker
    progress = ProgressTracker(len(organizer.stats['empty_directories_list']), "Deleting directories", "dirs")
    
    for dir_path in organizer.stats['empty_directories_list']:
        try:
            # Check if directory still exists and is still empty
            dir_path_obj = Path(dir_path)
            if dir_path_obj.exists() and dir_path_obj.is_dir():
                if not os.listdir(dir_path):
                    # Directory is still empty, delete it
                    os.rmdir(dir_path)
                    deleted_count += 1
                    logger.info(f"Deleted empty directory: {dir_path}")
                else:
                    logger.warning(f"Directory no longer empty, skipping: {dir_path}")
            else:
                logger.info(f"Directory no longer exists, skipping: {dir_path}")
        except Exception as e:
            errors += 1
            success = False
            logger.error(f"Error deleting directory {dir_path}: {str(e)}")
        
        progress.update()
    
    progress.close()
    
    # Update stats
    organizer.stats["directories_deleted"] = deleted_count
    organizer.stats["errors"] += errors
    
    print(f"\n{Fore.GREEN}Successfully deleted {deleted_count} directories.{Style.RESET_ALL}")
    if errors > 0:
        print(f"{Fore.RED}Encountered {errors} errors during deletion. See log for details.{Style.RESET_ALL}")
    
    return success


def display_empty_directories(organizer: DocOrganizer) -> None:
    """Display a list of empty directories found during the scan.
    
    Args:
        organizer: DocOrganizer instance with scan results
    """
    empty_dirs = organizer.stats.get("empty_directories_list", [])
    
    if not empty_dirs:
        print(f"\n{Fore.YELLOW}No empty directories found.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Empty Directories Found ({len(empty_dirs)}):{Style.RESET_ALL}")
    
    # Group directories by parent for better organization
    by_parent = defaultdict(list)
    for dir_path in empty_dirs:
        parent = os.path.dirname(dir_path)
        by_parent[parent].append(os.path.basename(dir_path))
    
    # Display grouped directories
    for i, (parent, children) in enumerate(by_parent.items(), 1):
        print(f"\n{i}. {Fore.BLUE}{parent}{Style.RESET_ALL}")
        for j, child in enumerate(children, 1):
            print(f"   {j}. {child}")
    
    print(f"\n{Fore.YELLOW}Total: {len(empty_dirs)} empty directories{Style.RESET_ALL}")


def interactive_menu(organizer: DocOrganizer) -> int:
    """Display an interactive menu for the user to choose actions.
    
    Args:
        organizer: DocOrganizer instance with scan results
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    exit_code = 0
    
    while True:
        print(f"\n{Fore.CYAN}=== Doc Organizer Interactive Menu ==={Style.RESET_ALL}")
        print(f"1. {Fore.GREEN}View empty directories{Style.RESET_ALL}")
        print(f"2. {Fore.YELLOW}Delete all empty directories{Style.RESET_ALL}")
        print(f"3. {Fore.BLUE}Scan again{Style.RESET_ALL}")
        print(f"4. {Fore.MAGENTA}Generate report{Style.RESET_ALL}")
        print(f"5. {Fore.RED}Exit{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}Enter your choice (1-5):{Style.RESET_ALL} ")
        
        if choice == "1":
            display_empty_directories(organizer)
        elif choice == "2":
            if organizer.dry_run:
                print(f"\n{Fore.YELLOW}Dry run mode enabled. No changes will be made.{Style.RESET_ALL}")
                print(f"Would delete {len(organizer.stats.get('empty_directories_list', []))} empty directories.")
            else:
                confirm = input(f"\n{Fore.YELLOW}Are you sure you want to delete all empty directories? (y/n):{Style.RESET_ALL} ").lower()
                if confirm == "y":
                    success = delete_empty_directories(organizer)
                    if not success:
                        exit_code = 3
        elif choice == "3":
            print(f"\n{Fore.BLUE}Scanning again...{Style.RESET_ALL}")
            try:
                organizer.run()
            except Exception as e:
                logger.error(f"Error during scan: {str(e)}")
                print(f"\n{Fore.RED}Error during scan: {str(e)}{Style.RESET_ALL}")
                exit_code = 3
        elif choice == "4":
            report_path = input(f"\n{Fore.CYAN}Enter report file path (or press Enter for default):{Style.RESET_ALL} ")
            if not report_path:
                report_path = os.path.join(os.getcwd(), f"doc_organizer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            
            try:
                generate_report(organizer.stats, report_path, "markdown")
                print(f"\n{Fore.GREEN}Report saved to: {report_path}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                print(f"\n{Fore.RED}Error generating report: {str(e)}{Style.RESET_ALL}")
        elif choice == "5":
            print(f"\n{Fore.CYAN}Exiting...{Style.RESET_ALL}")
            break
        else:
            print(f"\n{Fore.RED}Invalid choice. Please enter a number between 1 and 5.{Style.RESET_ALL}")
    
    return exit_code


def main() -> int:
    """Main entry point for the script.
    
    Returns:
        int: Exit code. 0 for success, non-zero for errors.
            1: Command-line argument error
            2: Initialization error
            3: Runtime error during processing
    """
    exit_code = 0
    start_time = time.time()
    
    try:
        # Parse command line arguments with error handling
        try:
            # Define script description for ArgumentParser using the helper function
            defined_script_description = get_script_description()

            parser = argparse.ArgumentParser(
                prog=script_filename,
                description=f"{defined_script_description}",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog="""Examples:
      # Basic usage
      python {script_filename}
      
      # Specify base path
      python {script_filename} --base-path /path/to/process
      
      # Run in dry-run mode (no changes made)
      python {script_filename} --dry-run

    ✧༺❀༻∞ EGOS ∞༺❀༻✧"""
            )
            
            parser.add_argument("--base-path", type=str, default=os.getcwd(), 
                                help="Target root directory to scan for empty subdirectories.")
            parser.add_argument("--log-level", type=str, default="INFO", 
                                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                                help="Set the logging level.")
            parser.add_argument("--dry-run", action="store_true", 
                                help="Run in dry-run mode (no changes made)")
            parser.add_argument("--report-format", type=str, default="markdown", 
                                choices=["markdown", "text"], 
                                help="Format for the output report (complies with RULE-REPORT-STD-01)")
            parser.add_argument("--report-file", type=str, 
                                help="Path to save the report file. If not specified, report is only displayed on console.")
            parser.add_argument("--interactive", action="store_true",
                                help="Run in interactive mode with menu options after scan")
            
            args = parser.parse_args()
            
        except argparse.ArgumentError as e:
            logger.error(f"Invalid command-line argument: {str(e)}")
            return 1
        except Exception as e:
            logger.error(f"Error parsing command-line arguments: {str(e)}")
            logger.exception("Exception details:")
            return 1
        
        # Print banner
        print_banner(
            f"{script_name}",
            f"v{get_script_version()} | {get_script_author()} | {get_creation_date()}"
        )
        
        # Create and run the DocOrganizer with error handling
        try:
            organizer = DocOrganizer(
                base_path=args.base_path,
                dry_run=args.dry_run,
                log_level=args.log_level,
                interactive=args.interactive
            )
        except ValueError as e:
            logger.error(f"Invalid configuration: {str(e)}")
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} {str(e)}")
            return 2
        except (IOError, OSError) as e:
            logger.error(f"File system error during initialization: {str(e)}")
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} File system error: {str(e)}")
            return 2
        except RuntimeError as e:
            logger.error(f"Runtime error during initialization: {str(e)}")
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} Initialization failed: {str(e)}")
            return 2
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {str(e)}")
            logger.exception("Exception details:")
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} Unexpected initialization error: {str(e)}")
            return 2
        
        # Run the organizer with error handling
        try:
            success = organizer.run()
            if not success and organizer.stats["errors"] > 0:
                exit_code = 3  # Set exit code for runtime errors
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
            logger.warning("Process interrupted by user.")
            exit_code = 130  # Standard exit code for SIGINT
            # Still continue to print summary with partial results
        except Exception as e:
            logger.error(f"Unexpected error during execution: {str(e)}")
            logger.exception("Exception details:")
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} Unexpected execution error: {str(e)}")
            exit_code = 3
            # Still continue to print summary with partial results
        
        # Print summary
        print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"  Directories scanned: {organizer.stats.get('directories_scanned', 0)}")
        print(f"  Empty directories found: {organizer.stats.get('empty_directories_found', 0)}")
        
        if not args.dry_run:
            print(f"  Directories deleted: {organizer.stats.get('directories_deleted', 0)}")
        else:
            print(f"  Directories that would be deleted: {organizer.stats.get('empty_directories_found', 0)}")
            
        # Display a sample of empty directories found
        empty_dirs = organizer.stats.get("empty_directories_list", [])
        if empty_dirs:
            print(f"\n{Fore.YELLOW}Sample of empty directories found:{Style.RESET_ALL}")
            for i, dir_path in enumerate(empty_dirs[:5], 1):  # Show first 5
                print(f"  {i}. {dir_path}")
            if len(empty_dirs) > 5:
                print(f"  ... and {len(empty_dirs) - 5} more. Use interactive mode to view all.")
            
        # Enhanced error reporting
        error_count = organizer.stats.get('errors', 0)
        if error_count > 0:
            print(f"  {Fore.RED}Errors encountered: {error_count}{Style.RESET_ALL}")
            
            # Show detailed error information if available and in verbose mode
            if args.log_level.upper() in ["DEBUG", "INFO"] and 'error_details' in organizer.stats:
                print(f"\n{Fore.YELLOW}Error Details:{Style.RESET_ALL}")
                for i, error in enumerate(organizer.stats['error_details'][:5]):  # Show first 5 errors
                    print(f"  {i+1}. {error['type']}: {error['message']}")
                    print(f"     Path: {error['path']}")
                    
                if len(organizer.stats['error_details']) > 5:
                    print(f"  ... and {len(organizer.stats['error_details']) - 5} more errors. See log for details.")
        else:
            print(f"  {Fore.GREEN}Errors encountered: 0{Style.RESET_ALL}")
            
        # Print processing time
        total_time = time.time() - start_time
        print(f"  Processing time: {format_time(organizer.stats.get('processing_time', total_time))}")
        
        # Generate report file if requested
        if args.report_file:
            try:
                generate_report(organizer.stats, args.report_file, args.report_format)
                print(f"\n{Fore.GREEN}Report saved to: {args.report_file}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                print(f"\n{Fore.RED}Error generating report: {str(e)}{Style.RESET_ALL}")
                # Don't change exit code for report generation failure
                
        # If interactive mode is enabled, show the interactive menu
        if args.interactive:
            print(f"\n{Fore.CYAN}Entering interactive mode...{Style.RESET_ALL}")
            interactive_exit_code = interactive_menu(organizer)
            if interactive_exit_code != 0:
                exit_code = interactive_exit_code
        # If not in interactive mode but empty directories were found, suggest options
        elif organizer.stats.get('empty_directories_found', 0) > 0:
            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"  - Run with {Fore.YELLOW}--interactive{Style.RESET_ALL} flag to view and manage empty directories")
            print(f"  - Run without {Fore.YELLOW}--dry-run{Style.RESET_ALL} flag to delete empty directories")
            print(f"  - Run with {Fore.YELLOW}--report-file{Style.RESET_ALL} to generate a detailed report")
        
    except Exception as e:
        # Catch-all for any unexpected errors in the main function
        logger.critical(f"Critical error in main function: {str(e)}")
        logger.exception("Exception details:")
        print(f"\n{Fore.RED}Critical Error:{Style.RESET_ALL} {str(e)}")
        return 3
    finally:
        # Print EGOS signature regardless of success/failure
        print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    return exit_code


def generate_report(stats: Dict[str, Any], report_file: str, format_type: str = "markdown") -> None:
    """Generate a report file in the specified format.
    
    Args:
        stats: Statistics dictionary from DocOrganizer
        report_file: Path to save the report
        format_type: Format of the report ('markdown' or 'text')
        
    Raises:
        IOError: If the report file cannot be written
        ValueError: If the format type is invalid
    """
    # Create directory for report if it doesn't exist
    report_dir = os.path.dirname(report_file)
    if report_dir and not os.path.exists(report_dir):
        os.makedirs(report_dir, exist_ok=True)
    
    # Get current timestamp for the report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if format_type.lower() == "markdown":
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Doc Organizer Report\n\n")
            f.write(f"**Generated:** {timestamp}\n\n")
            f.write(f"**Version:** {get_script_version()}\n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Directories Scanned:** {stats.get('directories_scanned', 0)}\n")
            f.write(f"- **Empty Directories Found:** {stats.get('empty_directories_found', 0)}\n")
            f.write(f"- **Directories Deleted:** {stats.get('directories_deleted', 0)}\n")
            f.write(f"- **Errors Encountered:** {stats.get('errors', 0)}\n")
            f.write(f"- **Processing Time:** {format_time(stats.get('processing_time', 0))}\n\n")
            
            # Add list of empty directories to the report
            empty_dirs = stats.get("empty_directories_list", [])
            if empty_dirs:
                f.write(f"## Empty Directories Found ({len(empty_dirs)})\n\n")
                
                # Group directories by parent for better organization
                by_parent = defaultdict(list)
                for dir_path in empty_dirs:
                    parent = os.path.dirname(dir_path)
                    by_parent[parent].append(os.path.basename(dir_path))
                
                # Write grouped directories
                for parent, children in by_parent.items():
                    f.write(f"### {parent}\n\n")
                    for child in children:
                        f.write(f"- `{child}`\n")
                    f.write("\n")
            
            if stats.get('errors', 0) > 0 and 'error_details' in stats:
                f.write(f"## Error Details\n\n")
                f.write(f"| # | Type | Path | Message | Recoverable |\n")
                f.write(f"|---|------|------|---------|------------|\n")
                
                for i, error in enumerate(stats['error_details']):
                    f.write(f"| {i+1} | {error.get('type', 'Unknown')} | {error.get('path', 'N/A')} | "
                            f"{error.get('message', 'No message')} | {error.get('recoverable', False)} |\n")
            
            f.write(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
    
    elif format_type.lower() == "text":
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"DOC ORGANIZER REPORT\n")
            f.write(f"===================\n\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Version: {get_script_version()}\n\n")
            
            f.write(f"SUMMARY:\n")
            f.write(f"  Directories Scanned: {stats.get('directories_scanned', 0)}\n")
            f.write(f"  Empty Directories Found: {stats.get('empty_directories_found', 0)}\n")
            f.write(f"  Directories Deleted: {stats.get('directories_deleted', 0)}\n")
            f.write(f"  Errors Encountered: {stats.get('errors', 0)}\n")
            f.write(f"  Processing Time: {format_time(stats.get('processing_time', 0))}\n\n")
            
            # Add list of empty directories to the report
            empty_dirs = stats.get("empty_directories_list", [])
            if empty_dirs:
                f.write(f"EMPTY DIRECTORIES FOUND ({len(empty_dirs)}):\n\n")
                
                # Group directories by parent for better organization
                by_parent = defaultdict(list)
                for dir_path in empty_dirs:
                    parent = os.path.dirname(dir_path)
                    by_parent[parent].append(os.path.basename(dir_path))
                
                # Write grouped directories
                for parent, children in by_parent.items():
                    f.write(f"  {parent}:\n")
                    for child in children:
                        f.write(f"    - {child}\n")
                    f.write("\n")
            
            if stats.get('errors', 0) > 0 and 'error_details' in stats:
                f.write(f"ERROR DETAILS:\n")
                for i, error in enumerate(stats['error_details']):
                    f.write(f"  {i+1}. {error.get('type', 'Unknown')}: {error.get('message', 'No message')}\n")
                    f.write(f"     Path: {error.get('path', 'N/A')}\n")
                    f.write(f"     Recoverable: {error.get('recoverable', False)}\n")
            
            f.write(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
    else:
        raise ValueError(f"Invalid report format: {format_type}. Must be 'markdown' or 'text'.")

if __name__ == "__main__":
    sys.exit(main())