#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Logging Script

This script tests the logging functionality for the Directory Unification Tool.
It creates a logger with both console and file handlers and verifies that
logging works correctly.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\scripts\maintenance\directory_unification\utils.py
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
import logging
import datetime
from pathlib import Path

# Local imports
from utils import setup_logger

# Constants
CONFIG = {
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_LEVEL": logging.INFO,
    "LOG_FILENAME": "test_logging.log"
}

def main():
    """Test logging functionality."""
    print("===== LOGGING TEST SCRIPT =====", file=sys.stderr, flush=True)
    
    # Print directly to stderr for debugging
    print("DEBUG: Starting logging test", file=sys.stderr, flush=True)
    
    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output", f"logging_test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write a marker file to confirm the output directory
    marker_file = os.path.join(output_dir, "marker.txt")
    with open(marker_file, "w") as f:
        f.write(f"Test marker file created at {datetime.datetime.now()}")
    
    print(f"DEBUG: Created output directory: {output_dir}", file=sys.stderr, flush=True)
    print(f"DEBUG: Created marker file: {marker_file}", file=sys.stderr, flush=True)
    
    # Set up logger with DEBUG level for verbose output
    logger = setup_logger(
        name="test_logger",
        log_format=CONFIG["LOG_FORMAT"],
        log_level=logging.DEBUG,  # Force DEBUG level
        log_dir=output_dir,
        log_filename=CONFIG["LOG_FILENAME"]
    )
    
    # Log messages at different levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    # Log the expected log file path
    log_file_path = os.path.join(output_dir, CONFIG["LOG_FILENAME"])
    logger.info(f"Log file should be at: {log_file_path}")
    
    # Check if log file exists
    if os.path.exists(log_file_path):
        print(f"DEBUG: Log file created successfully: {log_file_path}", file=sys.stderr, flush=True)
        logger.info("Log file exists!")
        
        # Read and print the first few lines of the log file
        try:
            with open(log_file_path, "r") as f:
                first_lines = "".join(f.readlines()[:5])
                logger.info(f"First few lines of log file:\n{first_lines}")
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
    else:
        print(f"DEBUG: Log file NOT found: {log_file_path}", file=sys.stderr, flush=True)
        logger.error("Log file does not exist!")
    
    print("DEBUG: Logging test completed", file=sys.stderr, flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())