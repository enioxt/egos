#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validation Models for the EGOS Cross-Reference System

This module defines Pydantic models for cross-reference validation reports
to ensure consistent serialization and deserialization of validation data.

@references:
- 🔗 Reference: [orphaned_file_detector.py](./orphaned_file_detector.py)
- 🔗 Reference: [file_reference_checker_ultra.py](../file_reference_checker_ultra.py)
- 🔗 Reference: [serialization.py](../utils/serialization.py)
- 🔗 Reference: [dashboardClient.ts](../../../website/src/lib/api/dashboardClient.ts)
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md

Created: 2025-05-21
Author: EGOS Team
Version: 1.0.0"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, model_validator, field_serializer


class OrphanedFile(BaseModel):
    """Model representing a file with no incoming references."""
    file_path: str
    file_type: str
    last_modified: float
    size: int
    outgoing_references: int = 0
    priority: str = "low"  # low, medium, high


class OrphanedFileReport(BaseModel):
    """Report containing orphaned files and analysis."""
    orphaned_files: List[OrphanedFile] = Field(default_factory=list)
    total_files_scanned: int = 0
    total_orphaned_files: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    execution_time: float = 0.0


class ReferenceIssue(BaseModel):
    """Model representing an issue with a file reference."""
    source_file: str
    target_file: str
    line_number: int
    context: str = ""
    issue_type: str  # "broken", "dangling", "circular", etc.
    severity: str = "medium"  # "high", "medium", "low"
    message: str


class ReferenceCheckReport(BaseModel):
    """Report containing file reference checking results."""
    total_files_checked: int = 0
    total_references_found: int = 0
    valid_references: int = 0
    invalid_references: int = 0
    issues_found: int = 0
    issues: List[ReferenceIssue] = Field(default_factory=list)
    execution_time: float = 0.0


class UnifiedValidationReport(BaseModel):
    """
    Combined report from all validation components.
    
    This model unifies the results from both the orphaned file detector
    and the file reference checker into a single comprehensive report.
    """
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    execution_time: float = 0.0
    
    orphaned_files: Optional[OrphanedFileReport] = None
    references: Optional[ReferenceCheckReport] = None
    
    # Serialize Path objects to strings
    @field_serializer('*')
    def serialize_path(self, v: Any, _info):
        if isinstance(v, Path):
            return str(v)
        return v
    
    @model_validator(mode='after')
    def calculate_total_execution_time(self):
        """Calculate the total execution time from component reports."""
        total_time = 0.0
        
        if self.orphaned_files:
            total_time += self.orphaned_files.execution_time
            
        if self.references:
            total_time += self.references.execution_time
            
        self.execution_time = total_time
        return self
