"""TODO: Module docstring for test_sparc_tasks.py"""
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)


"""
Tests for MYCELIUM/src/schemas/sparc_tasks.py
Covers all Pydantic models and enums for schema validation, instantiation, enums, and edge cases.
"""
import uuid
import pytest
from datetime import datetime
from pydantic import ValidationError
from subsystems.MYCELIUM.src.schemas.sparc_tasks import (
    SparcStage, TaskStatus, BaseSparcMessage, SparcTaskRequest, SparcTaskResult, SparcStageUpdate
)

def test_sparc_stage_enum():
    """Test all SparcStage enum values are accessible and string values are correct."""
    assert SparcStage.SETUP == "SETUP"
    assert SparcStage.PERCEIVE == "PERCEIVE"
    assert SparcStage.ACTION == "ACTION"
    assert SparcStage.REFLECT == "REFLECT"
    assert SparcStage.CONSOLIDATE == "CONSOLIDATE"

def test_task_status_enum():
    """Test all TaskStatus enum values are accessible and string values are correct."""
    assert TaskStatus.PENDING == "PENDING"
    assert TaskStatus.IN_PROGRESS == "IN_PROGRESS"
    assert TaskStatus.COMPLETED == "COMPLETED"
    assert TaskStatus.FAILED == "FAILED"
    assert TaskStatus.CANCELLED == "CANCELLED"

def test_base_sparc_message_instantiation():
    """Test instantiation of BaseSparcMessage with required fields."""
    msg = BaseSparcMessage(
        task_id=uuid.uuid4(),
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS"
    )
    assert isinstance(msg.message_id, uuid.UUID)
    assert isinstance(msg.timestamp, datetime)
    assert msg.source_subsystem == "CORUJA"
    assert msg.destination_subsystem == "ATLAS"

def test_sparc_task_request_valid():
    """Test valid instantiation of SparcTaskRequest."""
    req = SparcTaskRequest(
        task_id=uuid.uuid4(),
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        task_type="refactor_code",
        parameters={"filename": "main.py", "lines": [1, 2, 3]}
    )
    assert req.task_type == "refactor_code"
    assert isinstance(req.parameters, dict)

def test_sparc_task_request_missing_fields():
    """Test SparcTaskRequest raises error when required fields are missing."""
    with pytest.raises(ValidationError):
        SparcTaskRequest(
            task_id=uuid.uuid4(),
            source_subsystem="CORUJA",
            destination_subsystem="ATLAS"
            # Missing task_type and parameters
        )

def test_sparc_task_result_success():
    """Test SparcTaskResult with a successful result."""
    result = SparcTaskResult(
        message_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        status=TaskStatus.COMPLETED,
        result_data={"output": "success!"}
    )
    assert result.status == TaskStatus.COMPLETED
    assert result.result_data["output"] == "success!"
    assert result.error_message is None

def test_sparc_task_result_failure():
    """Test SparcTaskResult with a failure and error message."""
    result = SparcTaskResult(
        message_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        status=TaskStatus.FAILED,
        error_message="Something went wrong."
    )
    assert result.status == TaskStatus.FAILED
    assert result.result_data is None
    assert result.error_message == "Something went wrong."

def test_sparc_stage_update_valid():
    """Test valid instantiation of SparcStageUpdate."""
    upd = SparcStageUpdate(
        message_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        stage=SparcStage.ACTION,
        status=TaskStatus.IN_PROGRESS,
        stage_data={"progress": 42},
        details="Processing code refactor."
    )
    assert upd.stage == SparcStage.ACTION
    assert upd.status == TaskStatus.IN_PROGRESS
    assert upd.stage_data["progress"] == 42
    assert upd.details == "Processing code refactor."

def test_sparc_stage_update_missing_required():
    """Test SparcStageUpdate raises error when required fields are missing."""
    with pytest.raises(ValidationError):
        SparcStageUpdate(
            message_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            timestamp=datetime.utcnow(),
            source_subsystem="CORUJA",
            destination_subsystem="ATLAS"
            # Missing stage and status
        )
