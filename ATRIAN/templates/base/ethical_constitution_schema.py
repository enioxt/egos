"""
ATRiAN Ethical Constitution Schema

This module defines the base Pydantic models for ATRiAN ethical constitution templates.
These schemas are used for creating, validating, and managing ethical constitutions
that can be applied to prompt validation workflows.

Version: 0.1.0
Last Modified: 2025-06-12
"""
# 
# @references:
#   - ATRIAN/templates/base/ethical_constitution_schema.py
# 
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    """Severity levels for ethical concerns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EthicalPrinciple(BaseModel):
    """Defines a core ethical principle in a constitution"""
    id: str = Field(..., description="Unique identifier for the principle")
    name: str = Field(..., description="Name of the principle")
    description: str = Field(..., description="Detailed description of the principle")
    severity: SeverityLevel = Field(..., description="Severity level if principle is violated")
    references: Optional[List[str]] = Field(default_factory=list, description="External references or sources")
    model_config = ConfigDict(extra="forbid")


class EthicalRule(BaseModel):
    """Defines a specific ethical rule tied to principles"""
    id: str = Field(..., description="Unique identifier for the rule")
    principle_ids: List[str] = Field(..., description="IDs of principles this rule implements")
    description: str = Field(..., description="Human-readable description of the rule")
    trigger_keywords: List[str] = Field(default_factory=list, description="Keywords that may trigger this rule")
    validation_patterns: Optional[List[str]] = Field(
        default_factory=list, 
        description="Regex patterns or heuristics for automated validation"
    )
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Recommendations if this rule is violated"
    )
    severity_override: Optional[SeverityLevel] = Field(
        None, 
        description="Override severity from the principle if needed"
    )
    model_config = ConfigDict(extra="forbid")


class ConstitutionMetadata(BaseModel):
    """Metadata for the ethical constitution"""
    version: str = Field(..., description="Version of the constitution")
    created_date: datetime = Field(..., description="Creation date")
    modified_date: Optional[datetime] = Field(None, description="Last modification date")
    author: str = Field(..., description="Author of the constitution")
    purpose: str = Field(..., description="Purpose of this ethical constitution")
    applicable_domains: List[str] = Field(
        default_factory=list, 
        description="Domains where this constitution applies"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for classification")
    parent_constitutions: List[str] = Field(
        default_factory=list, 
        description="IDs of parent constitutions this inherits from"
    )
    regulatory_alignment: List[str] = Field(
        default_factory=list, 
        description="Regulations this constitution aligns with"
    )
    model_config = ConfigDict(extra="forbid")


class EthicalConstitution(BaseModel):
    """
    Complete ethical constitution template that can be applied to validate prompts
    against ethical guidelines and regulatory requirements.
    """
    id: str = Field(..., description="Unique identifier for the constitution")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Detailed description")
    metadata: ConstitutionMetadata = Field(..., description="Constitution metadata")
    principles: List[EthicalPrinciple] = Field(..., description="Ethical principles")
    rules: List[EthicalRule] = Field(..., description="Ethical rules")
    validation_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Configuration for validation behavior"
    )
    model_config = ConfigDict(extra="forbid")
    
    @model_validator(mode='after')
    def validate_rule_principles(self) -> 'EthicalConstitution':
        """Ensure all rule principle_ids reference existing principles"""
        principle_ids = {p.id for p in self.principles}
        for rule in self.rules:
            for principle_id in rule.principle_ids:
                if principle_id not in principle_ids:
                    raise ValueError(
                        f"Rule {rule.id} references non-existent principle {principle_id}"
                    )
        return self