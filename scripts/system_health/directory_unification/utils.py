#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities Module for Directory Unification Tool

This module provides utility functions used across the Directory Unification Tool.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
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
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set, Tuple, Optional, Union

# Third-party imports
try:
    from colorama import Fore, Style, init
    init()  # Initialize colorama
except ImportError:
    # Define dummy colorama classes if not available
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()


from logging.handlers import RotatingFileHandler # Ensure this import is present
import os # Ensure this import is present
from typing import Optional # Ensure this import is present

def setup_logger(name: str, 
                 log_format: str, 
                 log_level: int = logging.INFO, 
                 log_dir: Optional[str] = None, 
                 log_filename: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with the specified name and format.
    
    Args:
        name: Logger name
        log_format: Log format string
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)

    # Clear existing handlers to avoid duplication if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler
    # if not logger.handlers: # This condition is no longer needed due to clear() above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    # Create file handler if log_dir is provided
    if log_dir:
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating log directory {log_dir}: {e}", file=sys.stderr)
                return logger # Fall back to console-only

        _log_filename = log_filename if log_filename else f"{name}.log"
        log_file_path = os.path.join(log_dir, _log_filename)
        
        try:
            file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
            # For file logging, let's set it to DEBUG to capture more details, console can be INFO
            file_handler.setLevel(logging.DEBUG if log_level == logging.INFO else log_level) 
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Use the already configured console handler of the logger to report this
            logger.error(f"Failed to create file handler for {log_file_path}: {e}. File logging will be disabled.")

    return logger


def print_banner(title: str) -> None:
    """
    Print a banner with the specified title.
    
    Args:
        title: Banner title
    """
    banner = f"""
    {Fore.CYAN}╔══════════════════════════════════════════════════════════╗
    ║ {Fore.YELLOW}{title.center(52)}{Fore.CYAN} ║
    ║ {Fore.WHITE}EGOS Directory Unification Tool{Fore.CYAN}                       ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


def format_path(path: str) -> str:
    """
    Format a path for display with proper color coding.
    
    Args:
        path: Path to format
        
    Returns:
        Formatted path
    """
    path_parts = path.split(os.sep)
    formatted_parts = []
    
    for i, part in enumerate(path_parts):
        if i == len(path_parts) - 1:
            # Last part (filename or directory name)
            formatted_parts.append(f"{Fore.GREEN}{part}{Style.RESET_ALL}")
        else:
            # Directory parts
            formatted_parts.append(f"{Fore.BLUE}{part}{Style.RESET_ALL}")
    
    return os.sep.join(formatted_parts)


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is binary, False otherwise
    """
    # Check file extension first
    if file_path.suffix.lower() in {".pyc", ".exe", ".dll", ".pyd", ".so", ".zip", ".tar", ".gz", ".7z", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".pdf"}:
        return True
    
    # Read first chunk of the file to detect binary content
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return is_binary_string(chunk)
    except Exception:
        # If we can't read the file, assume it's binary to be safe
        return True


def is_binary_string(data: bytes) -> bool:
    """
    Check if a byte string contains binary data.
    
    Args:
        data: Byte string to check
        
    Returns:
        True if the string contains binary data, False otherwise
    """
    # Check for null bytes and high ASCII characters
    null_count = data.count(b'\x00')
    high_ascii_count = sum(1 for b in data if b > 127)
    
    # If more than 10% of the bytes are null or high ASCII, consider it binary
    return (null_count + high_ascii_count) > len(data) / 10


class Timer:
    """
    Timer class for measuring execution time.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize the Timer.
        
        Args:
            name: Timer name
        """
        self.name = name
        self.start_time = None
        self.elapsed = 0
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """
        Stop the timer and return the elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0
        
        self.elapsed = time.time() - self.start_time
        self.start_time = None
        return self.elapsed
    
    def __enter__(self):
        """Start the timer when entering a context."""
        self.start()
        return self
    
    def __exit__(self, *args):
        """Stop the timer when exiting a context."""
        self.stop()
        if self.name:
            print(f"{self.name}: {self.elapsed:.2f} seconds")


def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to a human-readable size.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """
    Return the singular or plural form based on the count.
    
    Args:
        count: Count
        singular: Singular form
        plural: Plural form (default: singular + 's')
        
    Returns:
        Appropriate form based on the count
    """
    if count == 1:
        return singular
    else:
        return plural if plural else singular + 's'


def progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', decimals: int = 1, length: int = 50, fill: str = '█', print_end: str = '\r') -> None:
    """
    Display a progress bar in the console.
    
    Args:
        iteration: Current iteration
        total: Total iterations
        prefix: Prefix string
        suffix: Suffix string
        decimals: Decimal places for percentage
        length: Character length of bar
        fill: Bar fill character
        print_end: End character (e.g. '\r', '\n')
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    
    # Print new line on completion
    if iteration == total:
        print()


def get_timestamp() -> str:
    """
    Get a formatted timestamp for filenames.
    
    Returns:
        Formatted timestamp
    """
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)} minutes, {int(seconds)} seconds"
    
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{int(hours)} hours, {int(minutes)} minutes"
    
    days, hours = divmod(hours, 24)
    return f"{int(days)} days, {int(hours)} hours"


class EGOSJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for EGOS objects.
    
    This encoder handles Python objects that are not natively JSON serializable,
    such as sets, Path objects, and datetime objects.
    
    References:
        - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def json_serialize(obj: Any) -> Dict[str, Any]:
    """
    Convert an object to a JSON-serializable dictionary.
    
    This function handles Python objects that are not natively JSON serializable,
    such as sets, Path objects, and datetime objects.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable dictionary
    
    References:
        - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
    """
    if isinstance(obj, dict):
        return {k: json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serialize(item) for item in obj]
    elif isinstance(obj, set):
        return [json_serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return [json_serialize(item) for item in obj]
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return json_serialize(obj.__dict__)
    else:
        return obj