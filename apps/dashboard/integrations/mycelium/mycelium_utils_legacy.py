"""
mycelium_utils.py

Shared utilities for the Mycelium/NATS messaging system in EGOS.
Provides standardized functions for trace_id generation, context management,
and other common operations used across the Mycelium ecosystem.

This module serves as a central connection point between various components
of the EGOS messaging infrastructure, implementing the Conscious Modularity
and Systemic Cartography principles.

@references:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
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
import uuid
import logging
import json
from typing import Optional, Dict, Any, Union
from datetime import datetime
from contextvars import ContextVar
import sys
from pathlib import Path

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logger = logging.getLogger("dashboard.mycelium_utils")

# Context variable to hold trace_id for logging/propagation within a task
current_trace_id: ContextVar[str] = ContextVar('current_trace_id', default='N/A')


def generate_trace_id() -> str:
    """Generate a unique trace_id for tracking events through the system.
    
    Returns:
        str: A unique identifier (UUID) as a string.
    """
    return str(uuid.uuid4())


def get_current_trace_id() -> str:
    """Get the current trace_id from the context variable.
    
    Returns:
        str: The current trace_id or 'N/A' if not set.
    """
    return current_trace_id.get()


def set_trace_id(trace_id: Optional[str] = None) -> object:
    """Set the current trace_id in the context variable.
    
    Args:
        trace_id: The trace_id to set. If None, generates a new one.
        
    Returns:
        object: Token for resetting the context variable.
    """
    if trace_id is None:
        trace_id = generate_trace_id()
    return current_trace_id.set(trace_id)


def reset_trace_id(token: object) -> None:
    """Reset the trace_id context variable using the provided token.
    
    Args:
        token: Token returned by set_trace_id.
    """
    current_trace_id.reset(token)


def ensure_trace_id(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure that a data dictionary has a trace_id, generating one if missing.
    
    Args:
        data: Dictionary that may or may not contain a trace_id.
        
    Returns:
        Dict[str, Any]: The input dictionary with a guaranteed trace_id.
    """
    if 'trace_id' not in data or not data['trace_id']:
        data['trace_id'] = generate_trace_id()
    return data


def extract_trace_id(data: Union[Dict[str, Any], bytes, str]) -> str:
    """Extract trace_id from various data formats.
    
    Args:
        data: Data that may contain a trace_id (dict, JSON bytes, or JSON string).
        
    Returns:
        str: The extracted trace_id or 'N/A' if not found.
    """
    try:
        if isinstance(data, dict):
            return data.get('trace_id', 'N/A')
        elif isinstance(data, bytes):
            try:
                json_data = json.loads(data.decode())
                if isinstance(json_data, dict):
                    return json_data.get('trace_id', 'N/A')
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        elif isinstance(data, str):
            try:
                json_data = json.loads(data)
                if isinstance(json_data, dict):
                    return json_data.get('trace_id', 'N/A')
            except json.JSONDecodeError:
                pass
    except Exception as e:
        logger.error(f"Error extracting trace_id: {e}")
    
    return 'N/A'


def log_with_trace_id(logger, level: str, message: str, trace_id: Optional[str] = None, **kwargs):
    """Log a message with the trace_id included.
    
    Args:
        logger: Logger instance to use.
        level: Log level ('debug', 'info', 'warning', 'error', 'critical').
        message: Log message.
        trace_id: Optional trace_id to use. If None, uses the current context.
        **kwargs: Additional logging parameters.
    """
    if trace_id is None:
        trace_id = get_current_trace_id()
    
    log_message = f"[TraceID: {trace_id}] {message}"
    
    if level == 'debug':
        logger.debug(log_message, **kwargs)
    elif level == 'info':
        logger.info(log_message, **kwargs)
    elif level == 'warning':
        logger.warning(log_message, **kwargs)
    elif level == 'error':
        logger.error(log_message, **kwargs)
    elif level == 'critical':
        logger.critical(log_message, **kwargs)
    else:
        logger.info(log_message, **kwargs)


def create_timestamped_event(event_type: str, payload: Dict[str, Any], source_subsystem: str) -> Dict[str, Any]:
    """Create a standardized event with timestamp and trace_id.
    
    Args:
        event_type: Type of the event.
        payload: Event payload data.
        source_subsystem: Name of the subsystem generating the event.
        
    Returns:
        Dict[str, Any]: A standardized event dictionary.
    """
    return {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "trace_id": generate_trace_id(),
        "source_subsystem": source_subsystem,
        "payload": payload
    }