#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Script Metadata API

This script provides a standardized API for accessing metadata about scripts 
in the EGOS ecosystem. It serves as a central interface for querying script
information, relationships, and health metrics.

Features:
- REST API endpoints for script metadata
- Script search and filtering capabilities
- Standardized JSON response format
- Integration with script validator and ecosystem visualizer

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md
- C:\EGOS\scripts\maintenance\code_health\script_validator.py
- C:\EGOS\scripts\maintenance\code_health\script_ecosystem_visualizer.py
- C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py

Author: EGOS Development Team
Created: 2025-05-22
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
import json
import logging
import argparse
import threading
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable

# Try to import web framework with graceful fallback
try:
    from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
    from pydantic import BaseModel, Field
    import uvicorn
    from starlette.staticfiles import StaticFiles
    from starlette.responses import JSONResponse, FileResponse, RedirectResponse
    HAVE_FASTAPI = True
except ImportError:
    HAVE_FASTAPI = False
    print("Warning: FastAPI not installed. API server will not be available.")
    print("To install: pip install fastapi uvicorn")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "script_metadata_api.log")
    ]
)
logger = logging.getLogger("script_metadata_api")

# Define constants
DEFAULT_CACHE_PATH = Path(__file__).parent / "cache"
DEFAULT_VISUALIZATIONS_PATH = Path("C:\\EGOS\\docs\\visualizations")
DEFAULT_REPORTS_PATH = Path("C:\\EGOS\\docs\\reports")
DEFAULT_SCRIPTS_PATH = Path("C:\\EGOS\\scripts")
CACHE_REFRESH_INTERVAL = 3600  # 1 hour


class ScriptMetadataService:
    """
    Service for accessing and managing script metadata.
    
    This class provides methods for loading, caching, and querying script metadata
    from the ecosystem visualization data.
    """
    
    def __init__(self, cache_dir: Path = DEFAULT_CACHE_PATH, 
                 visualizations_dir: Path = DEFAULT_VISUALIZATIONS_PATH,
                 reports_dir: Path = DEFAULT_REPORTS_PATH,
                 scripts_dir: Path = DEFAULT_SCRIPTS_PATH):
        """
        Initialize the metadata service.
        
        Args:
            cache_dir: Directory to store cache files
            visualizations_dir: Directory containing visualizations
            reports_dir: Directory containing reports
            scripts_dir: Root directory of scripts
        """
        self.cache_dir = cache_dir
        self.visualizations_dir = visualizations_dir
        self.reports_dir = reports_dir
        self.scripts_dir = scripts_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache for script metadata
        self.metadata_cache = {}
        self.last_cache_update = 0
        self.cache_lock = threading.Lock()
        
        # Load initial data
        self._load_metadata()
        
        # Start background update thread
        self._start_background_update()
        
        logger.info(f"Script Metadata Service initialized with cache in {cache_dir}")
    
    def _start_background_update(self):
        """Start a background thread for periodic cache updates."""
        def update_thread():
            while True:
                time.sleep(CACHE_REFRESH_INTERVAL)
                try:
                    self._load_metadata(force=True)
                except Exception as e:
                    logger.error(f"Error updating metadata cache: {str(e)}")
        
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
        logger.info(f"Started background cache update thread (interval: {CACHE_REFRESH_INTERVAL}s)")
    
    def _load_metadata(self, force: bool = False) -> bool:
        """
        Load script metadata from ecosystem JSON.
        
        Args:
            force: Force reload even if cache is fresh
            
        Returns:
            True if metadata was loaded, False otherwise
        """
        current_time = time.time()
        
        # Check if cache is still fresh
        if not force and (current_time - self.last_cache_update) < CACHE_REFRESH_INTERVAL:
            return True
        
        with self.cache_lock:
            try:
                # Look for ecosystem JSON in visualizations directory
                ecosystem_json = self.visualizations_dir / "script_ecosystem.json"
                
                if not ecosystem_json.exists():
                    logger.warning(f"Ecosystem JSON not found: {ecosystem_json}")
                    return False
                
                # Load ecosystem data
                with open(ecosystem_json, 'r', encoding='utf-8') as f:
                    ecosystem_data = json.load(f)
                
                # Update cache
                self.metadata_cache = ecosystem_data
                self.last_cache_update = current_time
                
                # Save to cache file
                cache_file = self.cache_dir / "metadata_cache.json"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(ecosystem_data, f, indent=2)
                
                logger.info(f"Loaded metadata for {len(ecosystem_data.get('scripts', []))} scripts")
                return True
            
            except Exception as e:
                logger.error(f"Error loading script metadata: {str(e)}")
                
                # Try to load from cache file as fallback
                try:
                    cache_file = self.cache_dir / "metadata_cache.json"
                    if cache_file.exists():
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            self.metadata_cache = json.load(f)
                            logger.info(f"Loaded metadata from cache file (fallback)")
                            return True
                except Exception as cache_error:
                    logger.error(f"Error loading from cache file: {str(cache_error)}")
                
                return False
    
    def get_all_scripts(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all scripts.
        
        Returns:
            List of script metadata objects
        """
        return self.metadata_cache.get('scripts', [])
    
    def get_script_by_id(self, script_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific script by ID.
        
        Args:
            script_id: Script ID (relative path)
            
        Returns:
            Script metadata or None if not found
        """
        scripts = self.metadata_cache.get('scripts', [])
        for script in scripts:
            if script.get('id') == script_id:
                return script
        return None
    
    def get_scripts_by_subsystem(self, subsystem: str) -> List[Dict[str, Any]]:
        """
        Get metadata for scripts in a specific subsystem.
        
        Args:
            subsystem: Subsystem name
            
        Returns:
            List of script metadata objects
        """
        scripts = self.metadata_cache.get('scripts', [])
        return [s for s in scripts if s.get('subsystem') == subsystem]
    
    def get_subsystems(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all subsystems.
        
        Returns:
            List of subsystem metadata objects
        """
        return self.metadata_cache.get('subsystems', [])
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """
        Get relationships between scripts.
        
        Returns:
            List of relationship objects
        """
        return self.metadata_cache.get('relationships', [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get script ecosystem statistics.
        
        Returns:
            Dictionary of statistics
        """
        return self.metadata_cache.get('statistics', {})
    
    def search_scripts(self, query: str, subsystem: Optional[str] = None, 
                      valid_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Search for scripts matching criteria.
        
        Args:
            query: Search query string
            subsystem: Filter by subsystem
            valid_only: Filter by validation status
            
        Returns:
            List of matching script metadata objects
        """
        scripts = self.metadata_cache.get('scripts', [])
        results = []
        
        query = query.lower()
        
        for script in scripts:
            # Apply subsystem filter if provided
            if subsystem and script.get('subsystem') != subsystem:
                continue
            
            # Apply validation status filter if provided
            if valid_only is not None and script.get('valid') != valid_only:
                continue
            
            # Check if query matches any script fields
            if (query in script.get('rel_path', '').lower() or
                query in script.get('subsystem', '').lower()):
                results.append(script)
        
        return results


# Only define API models and routes if FastAPI is available
if HAVE_FASTAPI:
    # Define Pydantic models for API requests and responses
    class ScriptSearchParams(BaseModel):
        query: str = Field("", description="Search query string")
        subsystem: Optional[str] = Field(None, description="Filter by subsystem")
        valid_only: Optional[bool] = Field(None, description="Filter by validation status")
    
    class ScriptMetadata(BaseModel):
        id: str
        path: str
        rel_path: str
        subsystem: str
        valid: bool
        has_docstring: bool
        has_type_hints: bool
        line_count: int
        issues: List[str]
    
    class SubsystemMetadata(BaseModel):
        id: str
        name: str
        total: int
        valid: int
        invalid: int
        valid_percentage: float
    
    class RelationshipMetadata(BaseModel):
        source: str
        target: str
        type: str
    
    class StatisticsMetadata(BaseModel):
        total_scripts: int
        total_valid: int
        total_invalid: int
        valid_percentage: float
    
    # Create FastAPI application
    app = FastAPI(
        title="EGOS Script Metadata API",
        description="API for accessing metadata about scripts in the EGOS ecosystem",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Create metadata service
    metadata_service = ScriptMetadataService()
    
    # Define API routes
    @app.get("/api/scripts", response_model=List[ScriptMetadata], tags=["scripts"])
    async def get_scripts(
        query: str = Query("", description="Search query string"),
        subsystem: Optional[str] = Query(None, description="Filter by subsystem"),
        valid_only: Optional[bool] = Query(None, description="Filter by validation status")
    ):
        """Get a list of scripts, optionally filtered by search criteria."""
        if query or subsystem is not None or valid_only is not None:
            scripts = metadata_service.search_scripts(query, subsystem, valid_only)
        else:
            scripts = metadata_service.get_all_scripts()
        return scripts
    
    @app.get("/api/scripts/{script_id}", response_model=ScriptMetadata, tags=["scripts"])
    async def get_script(script_id: str):
        """Get metadata for a specific script by ID."""
        script = metadata_service.get_script_by_id(script_id)
        if not script:
            raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
        return script
    
    @app.get("/api/subsystems", response_model=List[SubsystemMetadata], tags=["subsystems"])
    async def get_subsystems():
        """Get a list of all subsystems."""
        return metadata_service.get_subsystems()
    
    @app.get("/api/subsystems/{subsystem_id}/scripts", response_model=List[ScriptMetadata], tags=["subsystems"])
    async def get_subsystem_scripts(subsystem_id: str):
        """Get all scripts in a specific subsystem."""
        scripts = metadata_service.get_scripts_by_subsystem(subsystem_id)
        return scripts
    
    @app.get("/api/relationships", response_model=List[RelationshipMetadata], tags=["relationships"])
    async def get_relationships():
        """Get relationships between scripts."""
        return metadata_service.get_relationships()
    
    @app.get("/api/statistics", response_model=StatisticsMetadata, tags=["statistics"])
    async def get_statistics():
        """Get script ecosystem statistics."""
        return metadata_service.get_statistics()
    
    @app.get("/api/refresh", tags=["management"])
    async def refresh_metadata(background_tasks: BackgroundTasks):
        """Refresh the metadata cache."""
        # Run in background to avoid blocking the response
        background_tasks.add_task(metadata_service._load_metadata, force=True)
        return {"message": "Metadata refresh started"}
    
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        """Redirect root to API docs."""
        return RedirectResponse(url="/api/docs")
    
    # Mount visualizations directory
    app.mount("/visualizations", StaticFiles(directory=str(DEFAULT_VISUALIZATIONS_PATH)), name="visualizations")


def start_api_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Start the API server.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        reload: Enable auto-reload for development
    """
    if not HAVE_FASTAPI:
        logger.error("Cannot start API server: FastAPI not installed")
        return
    
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run("script_metadata_api:app", host=host, port=port, reload=reload)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EGOS Script Metadata API')
    parser.add_argument('--host', type=str, default="127.0.0.1",
                        help='Host to listen on')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to listen on')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload for development')
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    # Start API server
    start_api_server(args.host, args.port, args.reload)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())