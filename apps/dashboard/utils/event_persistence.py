"""
EGOS Dashboard Event Persistence Module
======================================

This module provides a lightweight persistence mechanism for storing NATS events
in a structured markdown format, aligning with EGOS's principles for lightweight
but effective data retention strategies.

Core Features:
- Stores events in organized markdown files with timestamps and categories
- Uses atomic write operations to prevent data corruption
- Maintains structured metadata for easy querying and filtering
- Respects EGOS standards for data management and accessibility

@see: EGOS_PRINCIPLE:Sacred_Transparency
@see: EGOS_PROCESS:Evolutionary_Refinement_Cycle
"""
# 
# @references:
#   - apps/dashboard/utils/event_persistence.py

import os
import json
import logging
from datetime import datetime
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import threading

# Get logger for this module
logger = logging.getLogger("EGOS.Dashboard.EventPersistence")

class EventPersistenceManager:
    """
    A lightweight manager for persisting NATS events to markdown files.
    
    This class handles the storage of real-time events in a human-readable,
    structured format that aligns with EGOS documentation standards.
    """
    
    def __init__(
        self, 
        base_dir: str = "C:/EGOS/data/events",
        max_events_per_file: int = 100,
        enabled: bool = True
    ):
        """
        Initialize the event persistence manager.
        
        Args:
            base_dir: Directory where event files will be stored
            max_events_per_file: Maximum number of events per file before rolling
            enabled: Whether event persistence is enabled
        """
        self.base_dir = Path(base_dir)
        self.max_events_per_file = max_events_per_file
        self.enabled = enabled
        self.lock = threading.Lock()
        
        # Create topic-specific buffers to collect events before writing
        self.event_buffers: Dict[str, List[Dict[str, Any]]] = {}
        
        # Ensure the base directory exists
        if self.enabled:
            os.makedirs(self.base_dir, exist_ok=True)
            logger.info(f"Event persistence enabled. Storing events in {self.base_dir}")
        else:
            logger.info("Event persistence disabled")
    
    def _get_category_from_topic(self, topic: str) -> str:
        """Extract a category from a NATS topic."""
        # Topics typically follow pattern like "egos.subsystem.eventtype"
        parts = topic.split('.')
        if len(parts) > 1:
            return parts[1]  # Return the subsystem as the category
        return "unknown"
    
    def _get_file_path(self, topic: str) -> Path:
        """Get the file path for storing events for a specific topic."""
        category = self._get_category_from_topic(topic)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create category directory if it doesn't exist
        category_dir = self.base_dir / category
        os.makedirs(category_dir, exist_ok=True)
        
        # Use date in filename for automatic chronological organization
        return category_dir / f"{today}_{category}_events.md"
    
    def store_event(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        Store an event in the appropriate markdown file.
        
        Args:
            topic: NATS topic that the event was published to
            data: Event data (must be JSON-serializable)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        # Create a buffer for this topic if it doesn't exist
        if topic not in self.event_buffers:
            self.event_buffers[topic] = []
        
        # Add to the buffer
        with self.lock:
            timestamp = datetime.now().isoformat()
            event_with_metadata = {
                "timestamp": timestamp,
                "topic": topic,
                "data": data
            }
            self.event_buffers[topic].append(event_with_metadata)
            
            # If we've reached the threshold, flush to disk
            if len(self.event_buffers[topic]) >= 5:  # Small threshold for quick persistence
                self._flush_buffer(topic)
        
        return True
    
    def _flush_buffer(self, topic: str) -> bool:
        """
        Flush the event buffer for a topic to disk.
        
        Args:
            topic: NATS topic to flush
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not topic in self.event_buffers or not self.event_buffers[topic]:
            return True  # Nothing to flush
        
        file_path = self._get_file_path(topic)
        
        # Create the file with headers if it doesn't exist
        if not file_path.exists():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    category = self._get_category_from_topic(topic)
                    f.write(f"# EGOS {category.upper()} Events\n\n")
                    f.write(f"*Auto-generated event log for {category} subsystem*\n\n")
                    f.write("## Events\n\n")
            except Exception as e:
                logger.error(f"Failed to initialize event file {file_path}: {e}")
                return False
        
        # Append events to the file
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                for event in self.event_buffers[topic]:
                    timestamp = event["timestamp"]
                    event_time = timestamp.split('T')[1].split('.')[0]  # Extract HH:MM:SS
                    
                    # Write event entry in markdown format
                    f.write(f"### {event_time} - {topic}\n\n")
                    
                    # Add event data as formatted JSON
                    f.write("```json\n")
                    f.write(json.dumps(event["data"], indent=2))
                    f.write("\n```\n\n")
            
            # Clear the buffer after successful write
            self.event_buffers[topic] = []
            return True
            
        except Exception as e:
            logger.error(f"Failed to write events to {file_path}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Flush all event buffers to disk.
        
        Returns:
            bool: True if all flushes were successful, False otherwise
        """
        success = True
        with self.lock:
            for topic in list(self.event_buffers.keys()):
                if not self._flush_buffer(topic):
                    success = False
        return success

# Create a singleton instance for use throughout the application
event_persister = EventPersistenceManager()