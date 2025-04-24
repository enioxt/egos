"""TODO: Module docstring for message.py"""
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Mycelium Network - Core Message Module
------------------------------------------
Defines the foundational message structure for the Mycelium Network,
the central communication infrastructure for EGOS subsystems.

This module implements the base message schema and validation logic,
ensuring all inter-subsystem communications follow a consistent structure
with proper trace ID propagation.

EGOS Principles Applied:
- Conscious Modularity: Clear separation of message components
- Reciprocal Trust: Transparent message structure for reliable communication
- Systemic Cartography: Trace ID for mapping message flows through the system
"""

from __future__ import annotations

import uuid
import json
import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator, root_validator


class MyceliumMessage(BaseModel):
    """
    Base message structure for all Mycelium Network communications.
    
    Every message in the Mycelium Network follows this structure to ensure
    consistent handling, routing, and traceability across subsystems.
    
    Attributes:
        message_id: Unique identifier for this specific message
        trace_id: Identifier that follows the message through its entire lifecycle
        source: Originating subsystem of the message
        destination: Target subsystem (optional for broadcast/pub-sub)
        topic: Topic for publish/subscribe messaging (optional for direct)
        timestamp: Time when the message was created
        payload: Actual content/data of the message
        metadata: Additional contextual information about the message
            Methods:
            None
"""
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    trace_id: uuid.UUID
    source: str
    destination: Optional[str] = None
    topic: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
                    Attributes:
                None
"""Pydantic configuration for the MyceliumMessage model."""
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            datetime.datetime: lambda v: v.isoformat()
        }
        
        # Ensure frozen=False to allow creation of trace_id if not provided
        frozen = False
    
    @validator('source')
    def validate_source(cls, v: str) -> str:
        """
        Validate the source subsystem name.
        
        Args:
            v: The source subsystem name to validate
            
        Returns:
            The validated source name
            
        Raises:
            ValueError: If the source name is invalid
        """
        if not v or not isinstance(v, str):
            raise ValueError("Source must be a non-empty string")
        
        if len(v) > 50:
            raise ValueError("Source name must be 50 characters or less")
        
        # Validate against known subsystems or pattern
        valid_subsystems = [
            "CORUJA", "KOIOS", "CRONOS", "ETHIK", 
            "HARMONY", "NEXUS", "MYCELIUM"
        ]
        
        # Allow testing/development subsystems with prefix
        if not (v in valid_subsystems or v.startswith("TEST_") or v.startswith("DEV_")):
            raise ValueError(f"Source must be one of {valid_subsystems} or start with 'TEST_' or 'DEV_'")
        
        return v
    
    @validator('destination')
    def validate_destination(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """
        Validate the destination subsystem name.
        
        Either destination or topic must be provided.
        
        Args:
            v: The destination subsystem name to validate
            values: The other field values
            
        Returns:
            The validated destination name or None
            
        Raises:
            ValueError: If the destination name is invalid
        """
        if v is None:
            # Destination can be None if topic is provided
            if 'topic' not in values or values['topic'] is None:
                raise ValueError("Either destination or topic must be provided")
            return None
        
        if not isinstance(v, str):
            raise ValueError("Destination must be a string")
        
        if len(v) > 50:
            raise ValueError("Destination name must be 50 characters or less")
        
        # Validate against known subsystems or pattern
        valid_subsystems = [
            "CORUJA", "KOIOS", "CRONOS", "ETHIK", 
            "HARMONY", "NEXUS", "MYCELIUM", 
            "BROADCAST"  # Special value for broadcasting to all subsystems
        ]
        
        # Allow testing/development subsystems with prefix
        if not (v in valid_subsystems or v.startswith("TEST_") or v.startswith("DEV_")):
            raise ValueError(f"Destination must be one of {valid_subsystems} or start with 'TEST_' or 'DEV_'")
        
        return v
    
    @validator('topic')
    def validate_topic(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """
        Validate the message topic.
        
        Either destination or topic must be provided.
        Topics follow a hierarchical structure with dot notation.
        
        Args:
            v: The topic to validate
            values: The other field values
            
        Returns:
            The validated topic or None
            
        Raises:
            ValueError: If the topic is invalid
        """
        if v is None:
            # Topic can be None if destination is provided
            if 'destination' not in values or values['destination'] is None:
                raise ValueError("Either destination or topic must be provided")
            return None
        
        if not isinstance(v, str):
            raise ValueError("Topic must be a string")
        
        if len(v) > 255:
            raise ValueError("Topic must be 255 characters or less")
        
        # Validate topic format (hierarchical with dots)
        if not all(part.isalnum() or part == '*' for part in v.split('.')):
            raise ValueError("Topic parts must be alphanumeric or '*' separated by dots")
        
        return v
    
    @validator('trace_id', pre=True, always=True)
    def set_trace_id_if_missing(cls, v: Optional[uuid.UUID]) -> uuid.UUID:
        """
        Ensure trace_id exists, generating a new one if not provided.
        
        Args:
            v: The trace_id value or None
            
        Returns:
            The existing or newly generated trace_id
        """
        if v is None:
            return uuid.uuid4()
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the metadata structure.
        
        Args:
            v: The metadata dictionary
            
        Returns:
            The validated metadata
            
        Raises:
            ValueError: If the metadata is invalid
        """
        if not isinstance(v, dict):
            raise ValueError("Metadata must be a dictionary")
        
        # Add standard metadata fields if not present
        if 'version' not in v:
            v['version'] = '1.0'
            
        if 'hops' not in v:
            v['hops'] = 0
            
        return v
    
    def increment_hops(self) -> None:
        """
        Increment the hop count in metadata.
        
        This tracks how many nodes/services the message has passed through.
        """
        if 'hops' in self.metadata:
            self.metadata['hops'] += 1
        else:
            self.metadata['hops'] = 1
    
    def add_routing_info(self, node_id: str, timestamp: Optional[datetime.datetime] = None) -> None:
        """
        Add routing information to the message metadata.
        
        Args:
            node_id: Identifier of the node handling the message
            timestamp: Time when the message was handled (defaults to now)
        """
        if 'routing_path' not in self.metadata:
            self.metadata['routing_path'] = []
        
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        self.metadata['routing_path'].append({
            'node_id': node_id,
            'timestamp': timestamp.isoformat() if isinstance(timestamp, datetime.datetime) else timestamp
        })
    
    def to_json(self) -> str:
        """
        Convert the message to a JSON string.
        
        Returns:
            JSON representation of the message
        """
        return self.json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MyceliumMessage':
        """
        Create a message instance from a JSON string.
        
        Args:
            json_str: JSON representation of a message
            
        Returns:
            MyceliumMessage instance
        """
        return cls.parse_raw(json_str)
    
    def create_response(self, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> 'MyceliumMessage':
        """
        Create a response message to this message.
        
        Args:
            payload: Content for the response message
            metadata: Optional additional metadata
            
        Returns:
            New MyceliumMessage instance configured as a response
        """
        response_metadata = dict(self.metadata)
        if metadata:
            response_metadata.update(metadata)
        
        # Add response correlation
        response_metadata['in_response_to'] = str(self.message_id)
        
        return MyceliumMessage(
            trace_id=self.trace_id,
            source=self.destination or 'UNKNOWN',  # Response from the original destination
            destination=self.source,               # Back to the original source
            topic=self.topic,                      # Same topic if any
            payload=payload,
            metadata=response_metadata
        )


class MyceliumRequestMessage(MyceliumMessage):
    """
    A message representing a request requiring a response.
    
    This specialization adds metadata to track timeouts and
    identify the message as requiring a response.
    
    Attributes:
        timeout_seconds: How long to wait for a response
    """
    
    @root_validator(pre=True)
    def ensure_request_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure metadata contains request-specific information.
        
        Args:
            values: The field values
            
        Returns:
            Updated field values
        """
        # Initialize metadata if not present
        if 'metadata' not in values:
            values['metadata'] = {}
        
        # Add request type metadata
        values['metadata']['message_type'] = 'request'
        
        # Extract timeout from values or use default
        timeout = values.pop('timeout_seconds', 30.0)
        values['metadata']['timeout_seconds'] = timeout
        
        return values


# Factory functions for message creation
def create_direct_message(
    source: str,
    destination: str,
    payload: Dict[str, Any],
    trace_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MyceliumMessage:
    """
    Create a direct point-to-point message.
    
    Args:
        source: Originating subsystem
        destination: Target subsystem
        payload: Message content
        trace_id: Optional trace ID (generated if not provided)
        metadata: Optional additional metadata
        
    Returns:
        Configured MyceliumMessage instance
    """
    return MyceliumMessage(
        trace_id=trace_id or uuid.uuid4(),
        source=source,
        destination=destination,
        payload=payload,
        metadata=metadata or {}
    )


def create_topic_message(
    source: str,
    topic: str,
    payload: Dict[str, Any],
    trace_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MyceliumMessage:
    """
    Create a topic-based publish/subscribe message.
    
    Args:
        source: Originating subsystem
        topic: Message topic (hierarchical with dots)
        payload: Message content
        trace_id: Optional trace ID (generated if not provided)
        metadata: Optional additional metadata
        
    Returns:
        Configured MyceliumMessage instance
    """
    return MyceliumMessage(
        trace_id=trace_id or uuid.uuid4(),
        source=source,
        topic=topic,
        payload=payload,
        metadata=metadata or {}
    )


def create_request_message(
    source: str,
    destination: str,
    payload: Dict[str, Any],
    timeout_seconds: float = 30.0,
    trace_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MyceliumRequestMessage:
    """
    Create a request message expecting a response.
    
    Args:
        source: Originating subsystem
        destination: Target subsystem
        payload: Message content
        timeout_seconds: How long to wait for response
        trace_id: Optional trace ID (generated if not provided)
        metadata: Optional additional metadata
        
    Returns:
        Configured MyceliumRequestMessage instance
    """
    if metadata is None:
        metadata = {}
    
    metadata['message_type'] = 'request'
    metadata['timeout_seconds'] = timeout_seconds
    
    return MyceliumRequestMessage(
        trace_id=trace_id or uuid.uuid4(),
        source=source,
        destination=destination,
        payload=payload,
        metadata=metadata
    )


def create_broadcast_message(
    source: str,
    payload: Dict[str, Any],
    trace_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> MyceliumMessage:
    """
    Create a broadcast message to all subsystems.
    
    Args:
        source: Originating subsystem
        payload: Message content
        trace_id: Optional trace ID (generated if not provided)
        metadata: Optional additional metadata
        
    Returns:
        Configured MyceliumMessage instance
    """
    if metadata is None:
        metadata = {}
    
    metadata['message_type'] = 'broadcast'
    
    return MyceliumMessage(
        trace_id=trace_id or uuid.uuid4(),
        source=source,
        destination="BROADCAST",
        payload=payload,
        metadata=metadata
    )