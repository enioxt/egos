#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal Logging Test Script

This script tests basic Python logging functionality without any dependencies.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
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
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler

def setup_basic_logger(log_dir, log_filename):
    """Set up a basic logger with console and file handlers."""
    # Create logger
    logger = logging.getLogger("minimal_test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create output directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create file handler
    log_file_path = os.path.join(log_dir, log_filename)
    try:
        file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        print(f"Added file handler for: {log_file_path}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Error creating file handler: {e}", file=sys.stderr, flush=True)
    
    return logger

def main():
    """Run minimal logging test."""
    print("===== MINIMAL LOGGING TEST =====", file=sys.stderr, flush=True)
    
    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output", f"minimal_logging_{timestamp}")
    
    # Create marker file
    os.makedirs(output_dir, exist_ok=True)
    marker_path = os.path.join(output_dir, "marker.txt")
    with open(marker_path, "w") as f:
        f.write(f"Marker file created at {datetime.datetime.now()}")
    
    print(f"Created output directory: {output_dir}", file=sys.stderr, flush=True)
    print(f"Created marker file: {marker_path}", file=sys.stderr, flush=True)
    
    # Set up logger
    logger = setup_basic_logger(output_dir, "minimal_test.log")
    
    # Log test messages
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    # Check if log file exists
    log_file_path = os.path.join(output_dir, "minimal_test.log")
    if os.path.exists(log_file_path):
        print(f"Log file created successfully: {log_file_path}", file=sys.stderr, flush=True)
        
        # Read and print the first few lines
        try:
            with open(log_file_path, "r") as f:
                first_lines = "".join(f.readlines()[:5])
                print(f"First few lines of log file:\n{first_lines}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"Error reading log file: {e}", file=sys.stderr, flush=True)
    else:
        print(f"Log file NOT found: {log_file_path}", file=sys.stderr, flush=True)
    
    print("Minimal logging test completed", file=sys.stderr, flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())