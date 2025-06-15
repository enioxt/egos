"""
TODO: Module docstring for event_schemas.py.

@references:
- Core References:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

from datetime import datetime
from pathlib import Path
import sys
from typing import Any, Dict
import uuid

from pydantic import BaseModel, Field, validator

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

"""
event_schemas.py.

Standardized Pydantic schemas for EGOS event data structures.
These schemas enforce consistent event formats across the EGOS system,
facilitating reliable processing, storage, and analysis.
This module implements the EGOS principles of:
- Conscious Modularity: Each event type has its own schema
- Systemic Cartography: Clear mapping of event structure and relationships
- Sacred Privacy: Validation ensures data integrity
- Universal Accessibility: Standard formats ensure interoperability

Interconnected with:
- mycelium_client.py: Uses these schemas for event validation
- mycelium_utils.py: Shares trace_id management functionality
- nats_simulator.py: Generates events conforming to these schemas
- direct_event_injector.py: Creates events following these schemas
"""


class BaseEvent(BaseModel):
    """Base model for all EGOS events, ensuring trace_id and timestamp presence."""

    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for tracking this event through the system",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO-8601 formatted timestamp when the event was created",
    )
    source_subsystem: str = Field(
        ..., description="Name of the subsystem that generated this event"
    )
    event_type: str = Field(..., description="Type of event (e.g., task_completion, log_entry)")

    class Config:
        """Pydantic configuration for BaseEvent."""

        extra = "allow"  # Allow additional fields beyond the schema

    @validator("timestamp")
    def validate_timestamp(cls, v):
        """Validate that the timestamp is in ISO format."""
        try:
            if isinstance(v, str):
                datetime.fromisoformat(v)
            return v
        except ValueError as err:
            raise ValueError(
                "timestamp must be in ISO-8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm)"
            ) from err


class SPARCTaskEvent(BaseEvent):
    """Schema for SPARC task events."""

    id: str = Field(..., description="Task identifier")
    type: str = Field(..., description="Task type (e.g., sparc_analyze, sparc_ingest)")
    status: str = Field(..., description="Task status (queued, in_progress, completed, failed)")
    result: str = Field(default="", description="Task result or output")

    @validator("source_subsystem", pre=True, always=True)
    def default_source_subsystem(cls, v):
        """Set default source_subsystem if not provided."""
        return v or "SPARC"

    @validator("event_type", pre=True, always=True)
    def default_event_type(cls, v):
        """Set default event_type if not provided."""
        return v or "task_update"


class LLMLogEvent(BaseEvent):
    """Schema for LLM interaction log events."""

    user: str = Field(..., description="User who initiated the interaction")
    prompt: str = Field(..., description="User prompt or query")
    response: str = Field(..., description="LLM response")

    @validator("source_subsystem", pre=True, always=True)
    def default_source_subsystem(cls, v):
        """Set default source_subsystem if not provided."""
        return v or "LLM"

    @validator("event_type", pre=True, always=True)
    def default_event_type(cls, v):
        """Set default event_type if not provided."""
        return v or "llm_interaction"


class PropagationEvent(BaseEvent):
    """Schema for system pattern propagation events."""

    subsystem: str = Field(..., description="Target subsystem for pattern propagation")
    pattern: str = Field(..., description="Pattern being propagated")
    status: str = Field(..., description="Propagation status")

    @validator("source_subsystem", pre=True, always=True)
    def default_source_subsystem(cls, v):
        """Set default source_subsystem if not provided."""
        return v or "PROPAGATION"

    @validator("event_type", pre=True, always=True)
    def default_event_type(cls, v):
        """Set default event_type if not provided."""
        return v or "pattern_propagation"


class LegacyEvent(BaseEvent):
    """Schema for migrated legacy events."""

    original_source: str = Field(..., description="Original source of the legacy data")
    migration_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the legacy data was migrated",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="Original legacy data payload"
    )

    @validator("source_subsystem", pre=True, always=True)
    def default_source_subsystem(cls, v):
        """Set default source_subsystem if not provided."""
        return v or "LEGACY_MIGRATOR"

    @validator("event_type", pre=True, always=True)
    def default_event_type(cls, v):
        """Set default event_type if not provided."""
        return v or "legacy_import"


class GlobalConfig(BaseModel):
    """Global configuration settings potentially affecting event schemas."""

    max_payload_size_kb: int = Field(1024, description="Maximum allowed event payload size in KB")


# Topic to schema mapping for validation
TOPIC_SCHEMAS = {
    "egos.sparc.tasks": SPARCTaskEvent,
    "egos.llm.logs": LLMLogEvent,
    "egos.propagation.log": PropagationEvent,
    "egos.legacy.import": LegacyEvent,
}


def validate_event(topic: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate an event against its schema based on the topic.

    Args:
        topic: The NATS topic the event is published to.
        data: The event data to validate.

    Returns:
        Dict[str, Any]: The validated (and possibly enhanced) event data.

    Raises:
        ValueError: If validation fails.

    """
    # Get the appropriate schema for this topic
    schema_cls = TOPIC_SCHEMAS.get(topic)

    if schema_cls:
        # Validate using the schema
        validated = schema_cls(**data)
        return validated.dict()

    # If no schema is defined for this topic, ensure at least trace_id and timestamp
    if "trace_id" not in data:
        data["trace_id"] = str(uuid.uuid4())
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()

    return data