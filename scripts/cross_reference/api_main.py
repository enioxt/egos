"""@file api_main.py
@description FastAPI server for the EGOS Cross-Reference System API.
@module scripts/cross_reference/api_main
@version 0.1.0
@date 2025-05-21

@references
- mdc:scripts/cross_reference/validator/unified_validator.py (UnifiedValidator)
- mdc:scripts/cross_reference/utils/serialization.py (EGOSJSONEncoder)
- mdc:website/src/lib/api/dashboardClient.ts (API Client)

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

from validator.unified_validator import UnifiedValidator
from validator.validation_models import UnifiedValidationReport, OrphanedFileReport, ReferenceCheckReport
from utils.serialization import EGOSJSONEncoder, save_json_file, serialize_to_json

@dataclass
class ValidationConfig:
    """Configuration for the unified validator."""
    workspace_root: str
    docs_dirs: List[str] = field(default_factory=list)
    code_dirs: List[str] = field(default_factory=list) 
    output_dir: Optional[str] = None
    file_extensions: List[str] = field(default_factory=list)
    ignore_patterns: List[str] = field(default_factory=list)
    reference_patterns: Dict[str, str] = field(default_factory=dict)
    orphaned_file_config: Dict[str, Any] = field(default_factory=dict)
    file_reference_checker_config: Dict[str, Any] = field(default_factory=dict)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EGOS Cross-Reference System API",
    description="API for managing and retrieving cross-reference validation data.",
    version="0.1.0"
)

# Configure CORS
# TODO: Restrict origins for production environments
origins = [
    "http://localhost:3000", # For Next.js frontend dev server
    "http://localhost:8000", # For FastAPI dev server (if accessed directly)
    # Add other origins as needed (e.g., deployed frontend URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration --- #
# Define a default configuration path or load dynamically
# For now, let's assume a default config or a simple one for testing
# This should be made more robust, e.g., loading from a YAML file or environment variables
DEFAULT_WORKSPACE_ROOT = Path(__file__).resolve().parents[2] # Assumes EGOS root
DEFAULT_CONFIG = ValidationConfig(
    workspace_root=str(DEFAULT_WORKSPACE_ROOT),
    docs_dirs=["docs", "docs_egos"],
    code_dirs=["scripts", "website/src"],
    output_dir=str(DEFAULT_WORKSPACE_ROOT / "reports" / "cross_reference"),
    file_extensions=[".md", ".py", ".ts", ".tsx", ".json", ".yaml", ".yml"],
    ignore_patterns=["**/node_modules/**", "**/.git/**", "**/dist/**", "**/build/**", "**/.next/**"],
    reference_patterns={ # Basic patterns, expand as needed
        "mdc": r"mdc:([\w\/-]+(?:\.[a-zA-Z0-9]+)?)",
        "http": r"https?:\/\/[^\s\)\]]+"
    },
    orphaned_file_config={
        "report_format": "json",
        "priority_keywords": {
            "high": ["critical", "urgent", "blocker"],
            "medium": ["important", "moderate"],
            "low": ["trivial", "enhancement"]
        }
    },
    file_reference_checker_config={
        "report_format": "json",
        "check_url_references": True,
        "url_timeout": 5
    }
)

# --- API Endpoints --- #

@app.get("/api/health", tags=["General"])
async def health_check():
    """Perform a health check."""
    logger.info("Health check endpoint called.")
    return {"status": "healthy", "message": "EGOS Cross-Reference API is running."}

@app.get("/api/validation/unified-report", response_model=UnifiedValidationReport, tags=["Validation"])
async def get_unified_report(config_path: str = None):
    """
    Run the unified validation process and return the report.
    Optionally, a path to a custom JSON configuration file can be provided.
    """
    logger.info(f"Unified validation report requested. Config path: {config_path}")
    try:
        # TODO: Implement loading config from config_path if provided
        # For now, uses the DEFAULT_CONFIG
        current_config = DEFAULT_CONFIG
        if config_path:
            logger.warning(f"Custom config_path ('{config_path}') provided but not yet implemented. Using default config.")
            # Example: current_config = ValidationConfig.load_from_json(config_path)

        validator = UnifiedValidator(config=current_config)
        report = validator.validate_all()
        
        # Optionally save the report to a file (can be configured)
        # report_path = Path(current_config.output_dir) / f"unified_report_{report.timestamp.replace(':', '-')}.json"
        # save_json_report(report.model_dump(), report_path, cls=EGOSJSONEncoder)
        # logger.info(f"Unified report saved to {report_path}")

        return report # FastAPI will use Pydantic's .model_dump_json() or similar
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise HTTPException(status_code=404, detail=f"Configuration file not found: {e.filename}")
    except Exception as e:
        logger.error(f"Error generating unified validation report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# --- Main Execution --- #
if __name__ == "__main__":
    logger.info("Starting EGOS Cross-Reference API server...")
    # FastAPI handles Pydantic model serialization to JSON automatically using the response_model.
    # If Path objects or other custom types within UnifiedValidationReport need special handling
    # for JSON serialization, it's best to configure this within the Pydantic models themselves
    # (e.g., using field_serializer or model_serializer in Pydantic v2, or custom json_encoders in Pydantic v1).
    # For now, we rely on Pydantic's default behavior which should convert Path to string.

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

