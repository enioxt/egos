"""Cross-Reference Scheduled Validation Service

This module provides a scheduled validation service that runs cross-reference
validation at specified intervals and stores the results for the dashboard.

@file scheduled_validation.py
@module scripts/cross_reference/api/scheduled_validation
@version 0.1.0
@date 2025-05-21
@license MIT

@references
- mdc:scripts/cross_reference/validator/unified_validator.py (UnifiedValidator)
- mdc:scripts/cross_reference/api/validation_api.py (Validation API)
- mdc:website/src/lib/api/validationRunner.ts (API Client)
- mdc:ROADMAP.md#cref-backend-schedule-01 (Scheduled Validation Runs)

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import os
import sys
import time
import json
import logging
import argparse
import datetime
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio
import schedule

# Add parent directory to sys.path to allow imports from parent modules
sys.path.append(str(Path(__file__).parent.parent))

from validator.unified_validator import UnifiedValidator
from validator.validation_models import (
    OrphanedFileReport,
    ReferenceCheckReport,
    UnifiedValidationReport,
    ValidationConfig
)
from utils.serialization import CustomJSONEncoder, save_json, load_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).parent / "scheduled_validation.log",
            mode="a"
        )
    ]
)
logger = logging.getLogger("scheduled-validation")

# Configuration
DEFAULT_CONFIG = {
    "daily_schedule": "00:00",  # Run daily at midnight
    "weekly_schedule": "monday 02:00",  # Run weekly on Monday at 2 AM
    "reports_dir": str(Path(__file__).parent / "reports"),
    "max_reports": 10,  # Maximum number of reports to keep
    "validation_config": {
        "orphaned_files": True,
        "reference_check": True,
        "max_files": None,
        "include_patterns": [],
        "exclude_patterns": ["**/node_modules/**", "**/venv/**", "**/.git/**"],
    }
}

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from a JSON file or use defaults"""
    if config_path and config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    logger.info("Using default configuration")
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], config_path: Path) -> None:
    """Save configuration to a JSON file"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")

def run_validation(config: Dict[str, Any], schedule_name: str) -> None:
    """Run validation with the specified configuration"""
    logger.info(f"Starting {schedule_name} validation run")
    
    try:
        # Create reports directory if it doesn't exist
        reports_dir = Path(config["reports_dir"])
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Create validation configuration
        validation_config = ValidationConfig(**config["validation_config"])
        
        # Create validator
        validator = UnifiedValidator(config=validation_config)
        
        # Run validation
        report = validator.validate_all()
        
        # Generate report filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"validation_report_{schedule_name}_{timestamp}.json"
        
        # Save report
        save_json(report.dict(), report_path)
        logger.info(f"Saved {schedule_name} validation report to {report_path}")
        
        # Save latest report reference
        latest_path = reports_dir / f"latest_{schedule_name}.json"
        with open(latest_path, "w") as f:
            json.dump({
                "timestamp": datetime.datetime.now().isoformat(),
                "report_path": str(report_path),
                "schedule_name": schedule_name
            }, f, indent=2)
        
        # Clean up old reports if needed
        cleanup_old_reports(reports_dir, config["max_reports"], schedule_name)
        
        logger.info(f"Completed {schedule_name} validation run")
    except Exception as e:
        logger.error(f"Error during {schedule_name} validation run: {str(e)}")
        logger.error(traceback.format_exc())

def cleanup_old_reports(reports_dir: Path, max_reports: int, schedule_name: str) -> None:
    """Clean up old reports, keeping only the specified number of most recent reports"""
    try:
        # Get all reports for this schedule
        reports = list(reports_dir.glob(f"validation_report_{schedule_name}_*.json"))
        
        # Sort by modification time (newest first)
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Delete older reports beyond the maximum
        if len(reports) > max_reports:
            for old_report in reports[max_reports:]:
                old_report.unlink()
                logger.info(f"Deleted old report: {old_report}")
    except Exception as e:
        logger.error(f"Error cleaning up old reports: {str(e)}")

def run_scheduled_job(job_name: str, config: Dict[str, Any]) -> None:
    """Wrapper for scheduled jobs to handle exceptions"""
    try:
        logger.info(f"Running scheduled job: {job_name}")
        run_validation(config, job_name)
    except Exception as e:
        logger.error(f"Error in scheduled job {job_name}: {str(e)}")
        logger.error(traceback.format_exc())

def setup_schedules(config: Dict[str, Any]) -> None:
    """Set up scheduled validation runs"""
    # Daily schedule
    if "daily_schedule" in config and config["daily_schedule"]:
        daily_time = config["daily_schedule"]
        logger.info(f"Setting up daily validation at {daily_time}")
        schedule.every().day.at(daily_time).do(
            run_scheduled_job, "daily", config
        )
    
    # Weekly schedule
    if "weekly_schedule" in config and config["weekly_schedule"]:
        weekly_schedule = config["weekly_schedule"].split()
        if len(weekly_schedule) == 2:
            day, time = weekly_schedule
            logger.info(f"Setting up weekly validation on {day} at {time}")
            getattr(schedule.every(), day.lower()).at(time).do(
                run_scheduled_job, "weekly", config
            )
        else:
            logger.error(f"Invalid weekly schedule format: {config['weekly_schedule']}")
    
    # Add other schedules as needed (monthly, hourly, etc.)

def run_service(config_path: Optional[Path] = None) -> None:
    """Run the scheduled validation service"""
    # Load configuration
    config = load_config(config_path)
    
    # Setup schedules
    setup_schedules(config)
    
    logger.info("Scheduled validation service started")
    
    # Run forever
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduled validation service stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduled validation service: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduled Cross-Reference Validation Service")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run validation immediately before starting scheduled service"
    )
    
    args = parser.parse_args()
    config_path = Path(args.config) if args.config else None
    config = load_config(config_path)
    
    if args.run_now:
        logger.info("Running immediate validation as requested")
        run_validation(config, "manual")
    
    run_service(config_path)
