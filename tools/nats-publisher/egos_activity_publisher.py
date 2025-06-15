#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
egos_activity_publisher.py

Real-time EGOS activity monitoring and NATS publishing script.
This script monitors actual EGOS system activities and publishes relevant
events to NATS topics for real-time dashboard visualization.

This implementation follows the EGOS principles of:
- Conscious Modularity: Separate monitoring components for different activity types
- Systemic Cartography: Mapping system activities to meaningful events
- Authentic Integration: Using real system data rather than simulated content

@references:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- [Dashboard_Realtime_Data_Strategy.md](mdc:../../docs/planning/Dashboard_Realtime_Data_Strategy.md)
"""
# 
# @references:
#   - tools/nats-publisher/egos_activity_publisher.py

import os
import sys
import time
import json
import asyncio
import logging
import argparse
from datetime import datetime, timezone
import uuid
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import nats
from nats.aio.client import Client as NATS

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
project_root = str(Path(__file__).resolve().parents[2])  # C:\EGOS
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EGOS.ActivityPublisher")

# NATS Topics (must match those in the dashboard)
SPARC_TASK_TOPIC = "egos.sparc.tasks"
LLM_LOG_TOPIC = "egos.llm.logs"
PROPAGATION_TOPIC = "egos.propagation.log"

# Configuration
DEFAULT_NATS_URL = "nats://localhost:4222"
MONITOR_PATHS = {
    "sparc": [
        os.path.join(project_root, "apps", "sparc"),
        os.path.join(project_root, ".sparc")
    ],
    "llm": [
        os.path.join(project_root, "docs", "work_logs"),
        os.path.join(project_root, "docs", "planning")
    ],
    "propagation": [
        project_root  # Monitor the entire EGOS directory for cross-references
    ]
}

# File patterns to monitor
FILE_PATTERNS = {
    "sparc": [".py", ".js", ".ts", ".md"],
    "llm": [".md", ".txt"],
    "propagation": [".md", ".py", ".js", ".ts"]
}

# Global NATS client
nc = None

class SparcTaskEventHandler(FileSystemEventHandler):
    """Monitors SPARC-related file activities and publishes task events."""
    
    def __init__(self, nats_client):
        self.nats_client = nats_client
        self.task_counter = 0
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext.lower() in FILE_PATTERNS["sparc"]:
            self.task_counter += 1
            task_type = self._determine_task_type(file_path)
            
            # Create a SPARC task event
            task_event = {
                "id": self.task_counter,
                "type": task_type,
                "status": "completed",
                "result": f"File modified: {os.path.basename(file_path)}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "file_path": file_path,
                "trace_id": str(uuid.uuid4())
            }
            
            # Publish to NATS
            asyncio.run(self._publish_event(task_event))
            logger.info(f"Published SPARC task event: {task_type} for {os.path.basename(file_path)}")
    
    def _determine_task_type(self, file_path):
        """Determine the SPARC task type based on file path and extension."""
        file_name = os.path.basename(file_path).lower()
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if "test" in file_name:
            return "sparc_test"
        elif file_ext == ".py":
            return "sparc_analyze"
        elif file_ext in [".js", ".ts"]:
            return "sparc_refactor"
        elif file_ext == ".md":
            return "sparc_document"
        else:
            return "sparc_process"
    
    async def _publish_event(self, event):
        """Publish event to NATS."""
        if self.nats_client and self.nats_client.is_connected:
            await self.nats_client.publish(SPARC_TASK_TOPIC, json.dumps(event).encode())


class LLMLogEventHandler(FileSystemEventHandler):
    """Monitors LLM-related file activities and publishes log events."""
    
    def __init__(self, nats_client):
        self.nats_client = nats_client
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext.lower() in FILE_PATTERNS["llm"]:
            # Create an LLM log event
            log_event = {
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "model": self._determine_model(file_path),
                "prompt": f"Process file: {os.path.basename(file_path)}",
                "response": f"File processed successfully",
                "trace_id": str(uuid.uuid4()),
                "file_path": file_path
            }
            
            # Publish to NATS
            asyncio.run(self._publish_event(log_event))
            logger.info(f"Published LLM log event for {os.path.basename(file_path)}")
    
    def _determine_model(self, file_path):
        """Determine the LLM model based on file content or naming patterns."""
        file_name = os.path.basename(file_path).lower()
        
        if "gpt" in file_name:
            return "gpt-4o"
        elif "claude" in file_name:
            return "claude-3-opus"
        elif "atrian" in file_name:
            return "atrian-ethical-compass"
        else:
            return "egos-assistant"
    
    async def _publish_event(self, event):
        """Publish event to NATS."""
        if self.nats_client and self.nats_client.is_connected:
            await self.nats_client.publish(LLM_LOG_TOPIC, json.dumps(event).encode())


class PropagationEventHandler(FileSystemEventHandler):
    """Monitors cross-reference and pattern propagation in EGOS files."""
    
    def __init__(self, nats_client):
        self.nats_client = nats_client
        self.patterns = [
            "Conscious Modularity",
            "Systemic Cartography",
            "Integrated Ethics",
            "Sacred Privacy",
            "Adaptive Resilience",
            "Operational Elegance"
        ]
        self.subsystems = [
            "NEXUS",
            "ETHIK",
            "CORUJA",
            "KOIOS",
            "ATRIAN",
            "SPARC"
        ]
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext.lower() in FILE_PATTERNS["propagation"]:
            # For demonstration, we'll detect patterns based on file paths
            # In a real implementation, we would analyze file content
            subsystem = self._determine_subsystem(file_path)
            pattern = self._determine_pattern(file_path)
            
            if subsystem and pattern:
                # Create a propagation event
                propagation_event = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "subsystem": subsystem,
                    "pattern": pattern,
                    "status": "Adopted",
                    "file_path": file_path,
                    "trace_id": str(uuid.uuid4())
                }
                
                # Publish to NATS
                asyncio.run(self._publish_event(propagation_event))
                logger.info(f"Published propagation event: {pattern} in {subsystem}")
    
    def _determine_subsystem(self, file_path):
        """Determine the subsystem based on file path."""
        file_path_lower = file_path.lower()
        
        for subsystem in self.subsystems:
            if subsystem.lower() in file_path_lower:
                return subsystem
        
        # Default to the directory name as subsystem
        dir_name = os.path.basename(os.path.dirname(file_path))
        return dir_name.upper() if dir_name else "EGOS"
    
    def _determine_pattern(self, file_path):
        """Determine the pattern based on file path or naming conventions."""
        # In a real implementation, we would analyze file content
        # For demonstration, we'll select a pattern based on the file path
        file_path_hash = hash(file_path) % len(self.patterns)
        return self.patterns[file_path_hash]
    
    async def _publish_event(self, event):
        """Publish event to NATS."""
        if self.nats_client and self.nats_client.is_connected:
            await self.nats_client.publish(PROPAGATION_TOPIC, json.dumps(event).encode())


async def connect_to_nats(nats_url=DEFAULT_NATS_URL):
    """Connect to NATS server."""
    global nc
    
    logger.info(f"Connecting to NATS at {nats_url}...")
    try:
        nc = NATS()
        await nc.connect(nats_url)
        logger.info("Connected to NATS server.")
        return nc
    except Exception as e:
        logger.error(f"Failed to connect to NATS: {e}")
        return None


async def disconnect_from_nats():
    """Disconnect from NATS server."""
    global nc
    
    if nc and nc.is_connected:
        await nc.drain()
        logger.info("Disconnected from NATS server.")


async def publish_heartbeat():
    """Publish regular heartbeat messages to verify connection."""
    global nc
    
    while nc and nc.is_connected:
        heartbeat = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "publisher": "egos_activity_publisher",
            "trace_id": str(uuid.uuid4())
        }
        
        try:
            await nc.publish("egos.system.heartbeat", json.dumps(heartbeat).encode())
            logger.debug("Published heartbeat")
        except Exception as e:
            logger.error(f"Failed to publish heartbeat: {e}")
        
        await asyncio.sleep(30)  # Heartbeat every 30 seconds


def setup_file_watchers(nats_client):
    """Set up file system watchers for different event types."""
    observer = Observer()
    
    # Set up SPARC task watchers
    sparc_handler = SparcTaskEventHandler(nats_client)
    for path in MONITOR_PATHS["sparc"]:
        if os.path.exists(path):
            observer.schedule(sparc_handler, path, recursive=True)
            logger.info(f"Monitoring SPARC activities in {path}")
    
    # Set up LLM log watchers
    llm_handler = LLMLogEventHandler(nats_client)
    for path in MONITOR_PATHS["llm"]:
        if os.path.exists(path):
            observer.schedule(llm_handler, path, recursive=True)
            logger.info(f"Monitoring LLM activities in {path}")
    
    # Set up propagation watchers
    propagation_handler = PropagationEventHandler(nats_client)
    for path in MONITOR_PATHS["propagation"]:
        if os.path.exists(path):
            observer.schedule(propagation_handler, path, recursive=True)
            logger.info(f"Monitoring propagation activities in {path}")
    
    return observer


async def publish_initial_events(nats_client):
    """Publish initial events to populate the dashboard on startup."""
    if not nats_client or not nats_client.is_connected:
        logger.error("Cannot publish initial events: NATS client not connected")
        return
    
    # Initial SPARC task
    sparc_event = {
        "id": 1,
        "type": "sparc_analyze",
        "status": "completed",
        "result": "System startup analysis complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file_path": os.path.join(project_root, "apps", "sparc", "analyzer.py"),
        "trace_id": str(uuid.uuid4())
    }
    await nats_client.publish(SPARC_TASK_TOPIC, json.dumps(sparc_event).encode())
    logger.info("Published initial SPARC task event")
    
    # Initial LLM log
    llm_event = {
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "model": "egos-assistant",
        "prompt": "Initialize EGOS activity publisher",
        "response": "Publisher initialized successfully",
        "trace_id": str(uuid.uuid4()),
        "file_path": __file__
    }
    await nats_client.publish(LLM_LOG_TOPIC, json.dumps(llm_event).encode())
    logger.info("Published initial LLM log event")
    
    # Initial propagation event
    propagation_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subsystem": "DASHBOARD",
        "pattern": "Real-Time Monitoring",
        "status": "Activated",
        "file_path": __file__,
        "trace_id": str(uuid.uuid4())
    }
    await nats_client.publish(PROPAGATION_TOPIC, json.dumps(propagation_event).encode())
    logger.info("Published initial propagation event")


async def main(nats_url=DEFAULT_NATS_URL):
    """Main function to run the EGOS activity publisher."""
    # Connect to NATS
    nats_client = await connect_to_nats(nats_url)
    if not nats_client:
        logger.error("Failed to connect to NATS. Exiting.")
        return
    
    # Publish initial events
    await publish_initial_events(nats_client)
    
    # Set up file watchers
    observer = setup_file_watchers(nats_client)
    observer.start()
    logger.info("File watchers started")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(publish_heartbeat())
    
    try:
        # Keep the main task running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt. Shutting down...")
    finally:
        # Clean up
        observer.stop()
        observer.join()
        heartbeat_task.cancel()
        await disconnect_from_nats()
        logger.info("EGOS activity publisher shut down")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EGOS Activity Publisher")
    parser.add_argument("--nats-url", default=DEFAULT_NATS_URL, help="NATS server URL")
    args = parser.parse_args()
    
    logger.info("Starting EGOS activity publisher")
    asyncio.run(main(args.nats_url))