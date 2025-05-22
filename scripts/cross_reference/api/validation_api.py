"""Cross-Reference Validation API Server

This module provides a FastAPI server that exposes endpoints for running
the unified cross-reference validator and retrieving validation results.

@file validation_api.py
@module scripts/cross_reference/api/validation_api
@version 0.1.0
@date 2025-05-21
@license MIT

@references
- mdc:scripts/cross_reference/validator/unified_validator.py (UnifiedValidator)
- mdc:scripts/cross_reference/validator/validation_models.py (ValidationModels)
- mdc:website/src/lib/api/dashboardClient.ts (API Client)
- mdc:website/src/app/api/validation/unified-report/route.ts (Next.js API Route)
- mdc:ROADMAP.md#cref-backend-realtime-01 (Real-time Validation API)

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import os
import sys
import asyncio
import logging
import datetime
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from pydantic import BaseModel, Field

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
            Path(__file__).parent / "validation_api.log",
            mode="a"
        )
    ]
)
logger = logging.getLogger("validation-api")

# Create FastAPI app
app = FastAPI(
    title="EGOS Cross-Reference Validation API",
    description="API for running and retrieving cross-reference validation results",
    version="0.1.0"
)

# Add CORS middleware to allow cross-origin requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for validation results
validation_cache = {
    "latest_report": None,
    "latest_timestamp": None,
    "running": False,
    "scheduled_runs": [],
}

# Models for API requests and responses
class ValidationRequest(BaseModel):
    """Request model for running validation"""
    orphaned_files: bool = Field(True, description="Whether to check for orphaned files")
    reference_check: bool = Field(True, description="Whether to check for broken references")
    max_files: Optional[int] = Field(None, description="Maximum number of files to check")
    include_patterns: Optional[List[str]] = Field(None, description="Patterns to include in validation")
    exclude_patterns: Optional[List[str]] = Field(None, description="Patterns to exclude from validation")
    report_path: Optional[str] = Field(None, description="Path to save the report")

class ValidationStatus(BaseModel):
    """Response model for validation status"""
    running: bool = Field(..., description="Whether validation is currently running")
    latest_timestamp: Optional[str] = Field(None, description="Timestamp of the latest validation run")
    scheduled_runs: List[str] = Field([], description="Timestamps of scheduled validation runs")

class ScheduleRequest(BaseModel):
    """Request model for scheduling validation runs"""
    schedule_time: str = Field(..., description="When to run the validation (ISO format)")
    config: ValidationRequest = Field(..., description="Validation configuration")

# Background task for running validation
async def run_validation_task(config: ValidationRequest):
    """Run validation in the background"""
    logger.info(f"Starting validation run with config: {config}")
    validation_cache["running"] = True
    
    try:
        # Create validation configuration
        validator_config = ValidationConfig(
            orphaned_files=config.orphaned_files,
            reference_check=config.reference_check,
            max_files=config.max_files,
            include_patterns=config.include_patterns or [],
            exclude_patterns=config.exclude_patterns or [],
        )
        
        # Create validator
        validator = UnifiedValidator(config=validator_config)
        
        # Run validation
        report = await asyncio.to_thread(validator.validate_all)
        
        # Update cache
        validation_cache["latest_report"] = report.dict()
        validation_cache["latest_timestamp"] = datetime.datetime.now().isoformat()
        
        # Save report if path provided
        if config.report_path:
            report_path = Path(config.report_path)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            save_json(report.dict(), report_path)
            logger.info(f"Saved report to {report_path}")
        
        logger.info("Validation run completed successfully")
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}", exc_info=True)
        raise
    finally:
        validation_cache["running"] = False

# Endpoint for running validation
@app.post("/api/run-validation", response_model=dict)
async def run_validation(
    config: ValidationRequest,
    background_tasks: BackgroundTasks
):
    """Run cross-reference validation asynchronously"""
    if validation_cache["running"]:
        raise HTTPException(409, "Validation is already running")
    
    background_tasks.add_task(run_validation_task, config)
    
    return {
        "status": "started",
        "message": "Validation started in the background",
        "timestamp": datetime.datetime.now().isoformat()
    }

# Endpoint for getting validation status
@app.get("/api/validation-status", response_model=ValidationStatus)
async def get_validation_status():
    """Get the current validation status"""
    return ValidationStatus(
        running=validation_cache["running"],
        latest_timestamp=validation_cache["latest_timestamp"],
        scheduled_runs=validation_cache["scheduled_runs"]
    )

# Endpoint for getting the latest validation report
@app.get("/api/validation-report", response_model=dict)
async def get_validation_report():
    """Get the latest validation report"""
    if not validation_cache["latest_report"]:
        raise HTTPException(404, "No validation report available")
    
    return validation_cache["latest_report"]

# Endpoint for scheduling a validation run
@app.post("/api/schedule-validation", response_model=dict)
async def schedule_validation(request: ScheduleRequest):
    """Schedule a validation run for a future time"""
    try:
        schedule_time = datetime.datetime.fromisoformat(request.schedule_time)
    except ValueError:
        raise HTTPException(400, "Invalid schedule time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    if schedule_time < datetime.datetime.now():
        raise HTTPException(400, "Schedule time must be in the future")
    
    # Add to scheduled runs
    validation_cache["scheduled_runs"].append(request.schedule_time)
    
    # Calculate delay in seconds
    delay = (schedule_time - datetime.datetime.now()).total_seconds()
    
    # Schedule the validation run
    async def delayed_run():
        await asyncio.sleep(delay)
        if request.schedule_time in validation_cache["scheduled_runs"]:
            validation_cache["scheduled_runs"].remove(request.schedule_time)
            await run_validation_task(request.config)
    
    # Start the delayed task
    asyncio.create_task(delayed_run())
    
    return {
        "status": "scheduled",
        "schedule_time": request.schedule_time,
        "message": f"Validation scheduled for {request.schedule_time}"
    }

# Endpoint for canceling a scheduled validation run
@app.delete("/api/cancel-scheduled-validation/{schedule_time}", response_model=dict)
async def cancel_scheduled_validation(schedule_time: str):
    """Cancel a scheduled validation run"""
    if schedule_time not in validation_cache["scheduled_runs"]:
        raise HTTPException(404, f"No scheduled validation found for time: {schedule_time}")
    
    validation_cache["scheduled_runs"].remove(schedule_time)
    
    return {
        "status": "canceled",
        "schedule_time": schedule_time,
        "message": f"Scheduled validation for {schedule_time} has been canceled"
    }

# Healthcheck endpoint
@app.get("/healthcheck")
async def healthcheck():
    """Simple healthcheck endpoint"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

if __name__ == "__main__":
    # Run the server when the script is executed directly
    uvicorn.run(
        "validation_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
