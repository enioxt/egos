#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Work Log Standardizer Integrator

This script integrates the Work Log Standardizer with other EGOS subsystems,
particularly the Script Ecosystem Analyzer and file monitoring systems.
It establishes cross-references, sets up automatic hooks for work log
creation/modification, and ensures proper system-wide monitoring.

@author: EGOS Development Team
@date: 2025-05-27
@version: 1.0.0

@references:
- C:\EGOS\MQP.md (Systemic Cartography, Evolutionary Preservation)
- C:\EGOS\docs\work_logs\WORK_2025-05-23_Work_Log_Standardization.md
- C:\EGOS\scripts\utils\work_log_standardizer\work_log_standardizer.py
- C:\EGOS\scripts\system_health\analyzers\script_ecosystem_analyzer.py
- C:\EGOS\scripts\system_health\integrations\ecosystem_analyzer_integrator.py
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
import re
import logging
import json
import datetime
import argparse
import shutil
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("work_log_standardizer_integrator")

# Constants
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work_log_standardizer.py")
ECOSYSTEM_ANALYZER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "system_health", "analyzers", "script_ecosystem_analyzer.py")
ECOSYSTEM_INTEGRATOR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "system_health", "integrations", "ecosystem_analyzer_integrator.py")
WORK_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                            "docs", "work_logs")
ACTIVE_LOGS_DIR = os.path.join(WORK_LOGS_DIR, "active")
ARCHIVE_LOGS_DIR = os.path.join(WORK_LOGS_DIR, "archive")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                          "docs", "reports", "work_logs")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work_log_standardizer_config.json")

# Default configuration
DEFAULT_CONFIG = {
    "auto_standardize": True,
    "watch_directories": [ACTIVE_LOGS_DIR],
    "standardize_on_change": True,
    "standardize_interval_minutes": 60,
    "ecosystem_analyzer_integration": True,
    "notification_enabled": True
}

def print_banner():
    """Print a banner for the work log standardizer integrator."""
    banner = """
+--------------------------------------------------+
|        EGOS Work Log Standardizer Integrator     |
|  Connecting work logs to the EGOS ecosystem      |
+--------------------------------------------------+
"""
    print(banner)

def ensure_directory_exists(directory: str):
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default if not exists.
    
    Returns:
        Configuration dictionary
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_PATH}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            return DEFAULT_CONFIG
    else:
        logger.info(f"Configuration file not found at {CONFIG_PATH}")
        logger.info("Creating default configuration")
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
                logger.info(f"Created default configuration at {CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error creating configuration file: {e}")
        return DEFAULT_CONFIG

def run_standardizer(target_dir: str = ACTIVE_LOGS_DIR, dry_run: bool = False) -> Optional[str]:
    """Run the work log standardizer.
    
    Args:
        target_dir: Directory to standardize
        dry_run: Whether to run in dry run mode
        
    Returns:
        Path to the generated report, if any
    """
    logger.info(f"Running Work Log Standardizer on {target_dir}")
    try:
        cmd = [sys.executable, SCRIPT_PATH, "--active-dir", target_dir]
        if dry_run:
            cmd.append("--dry-run")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Work Log Standardizer completed successfully")
            # Extract report path from output
            report_path = None
            for line in result.stdout.split('\n'):
                if "detailed report has been generated at:" in line:
                    report_path = line.split("at:")[-1].strip()
                    break
            return report_path
        else:
            logger.error(f"Work Log Standardizer failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error running Work Log Standardizer: {e}")
        return None

def integrate_with_ecosystem_analyzer(report_path: Optional[str] = None):
    """Integrate with the Script Ecosystem Analyzer.
    
    Args:
        report_path: Optional path to an existing standardization report
    """
    logger.info("Integrating with Script Ecosystem Analyzer")
    
    # First, ensure the work log standardizer is included in the ecosystem analysis
    try:
        # Run the ecosystem analyzer with focus on the work log standardizer directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cmd = [sys.executable, ECOSYSTEM_ANALYZER_PATH, "--target", script_dir]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Script Ecosystem Analyzer completed successfully")
            # Now run the integrator to ensure proper cross-references
            cmd = [sys.executable, ECOSYSTEM_INTEGRATOR_PATH]
            if report_path:
                cmd.extend(["--report", report_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Ecosystem Analyzer Integrator completed successfully")
            else:
                logger.error(f"Ecosystem Analyzer Integrator failed with code {result.returncode}")
                logger.error(f"Error: {result.stderr}")
        else:
            logger.error(f"Script Ecosystem Analyzer failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
    except Exception as e:
        logger.error(f"Error integrating with Script Ecosystem Analyzer: {e}")

class WorkLogChangeHandler(FileSystemEventHandler):
    """Handler for work log file system events."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the handler with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.last_run_time = 0
        self.min_interval = config.get("standardize_interval_minutes", 60) * 60  # Convert to seconds
    
    def on_modified(self, event):
        """Handle file modification events.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
            
        # Check if it's a work log file
        if not event.src_path.endswith(".md") or not os.path.basename(event.src_path).startswith("WORK_"):
            return
            
        # Check if we should standardize on change
        if not self.config.get("standardize_on_change", True):
            logger.debug(f"File changed but standardize_on_change is disabled: {event.src_path}")
            return
            
        # Check if enough time has passed since last run
        current_time = time.time()
        if current_time - self.last_run_time < self.min_interval:
            logger.debug(f"File changed but minimum interval not reached: {event.src_path}")
            return
            
        logger.info(f"Work log file changed: {event.src_path}")
        self.last_run_time = current_time
        
        # Get the directory of the changed file
        file_dir = os.path.dirname(event.src_path)
        
        # Run standardizer
        report_path = run_standardizer(file_dir, dry_run=False)
        
        # Integrate with ecosystem analyzer if enabled
        if self.config.get("ecosystem_analyzer_integration", True) and report_path:
            integrate_with_ecosystem_analyzer(report_path)

def setup_file_watchers(config: Dict[str, Any]) -> Optional[Observer]:
    """Set up file system watchers for work log directories.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Observer object if watchers were set up, None otherwise
    """
    if not config.get("auto_standardize", True):
        logger.info("Auto-standardization is disabled")
        return None
        
    watch_dirs = config.get("watch_directories", [ACTIVE_LOGS_DIR])
    if not watch_dirs:
        logger.warning("No directories to watch")
        return None
        
    # Create event handler and observer
    event_handler = WorkLogChangeHandler(config)
    observer = Observer()
    
    # Set up watchers for each directory
    for directory in watch_dirs:
        if os.path.exists(directory):
            observer.schedule(event_handler, directory, recursive=True)
            logger.info(f"Watching directory: {directory}")
        else:
            logger.warning(f"Directory does not exist, cannot watch: {directory}")
    
    return observer

def main():
    """Main function for the work log standardizer integrator."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="EGOS Work Log Standardizer Integrator")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run standardization once and exit"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry run mode (no changes made)"
    )
    parser.add_argument(
        "--integrate-only",
        action="store_true",
        help="Only integrate with ecosystem analyzer, don't run standardizer"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set log level
    logger.setLevel(args.log_level)
    
    # Ensure directories exist
    ensure_directory_exists(ACTIVE_LOGS_DIR)
    ensure_directory_exists(ARCHIVE_LOGS_DIR)
    ensure_directory_exists(REPORTS_DIR)
    
    # Load configuration
    config = load_config()
    
    # If integrate-only, just run integration
    if args.integrate_only:
        integrate_with_ecosystem_analyzer()
        return 0
    
    # If run-once, run standardizer and exit
    if args.run_once:
        report_path = run_standardizer(ACTIVE_LOGS_DIR, args.dry_run)
        if report_path and config.get("ecosystem_analyzer_integration", True):
            integrate_with_ecosystem_analyzer(report_path)
        return 0
    
    # Otherwise, set up file watchers and run continuously
    observer = setup_file_watchers(config)
    if not observer:
        logger.error("Failed to set up file watchers")
        return 1
    
    try:
        logger.info("Starting file watchers")
        observer.start()
        
        # Run initial standardization
        report_path = run_standardizer(ACTIVE_LOGS_DIR, args.dry_run)
        if report_path and config.get("ecosystem_analyzer_integration", True):
            integrate_with_ecosystem_analyzer(report_path)
        
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file watchers")
        observer.stop()
    finally:
        observer.join()
    
    return 0

if __name__ == "__main__":
    # EGOS System Signature - Adherence to MQP Principles
    # This script operates under the EGOS framework, upholding principles such as:
    # - Systemic Cartography: By connecting work logs to the broader ecosystem.
    # - Evolutionary Preservation: By ensuring work logs are properly maintained.
    # - Integrated Ethics (ETHIK): By transparently reporting actions.
    logger.info("EGOS Work Log Standardizer Integrator - Invoking main function.")
    logger.info("MQP Principles: Systemic Cartography, Evolutionary Preservation, ETHIK.")
    
    sys.exit(main())
    
    logger.info("EGOS Work Log Standardizer Integrator - Main function execution complete.")
    logger.info("Exiting script.")