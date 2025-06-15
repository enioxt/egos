# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# C:/EGOS/ATRiAN/eaas_models.py
"""
Shared Pydantic models for the ATRiAN EaaS API and core logic.

This module defines all the Pydantic models used by the ATRiAN Ethics as a Service (EaaS) API
and the EthicalCompass core logic. It provides a unified data contract for ethical evaluations,
explanations, suggestions, framework management, and audit logging.

Version: 0.2.0
Last Modified: 2025-06-01
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EthicsEvaluationOptions(BaseModel):
    detail_level: Optional[str] = Field("comprehensive", description="Level of detail in the response.")
    include_alternatives: Optional[bool] = Field(True, description="Whether to include ethical alternatives.")

class EthicsEvaluationRequestContext(BaseModel):
    domain: Optional[str] = Field(None, description="The domain of the action (e.g., healthcare, finance).")
    data_sources: Optional[List[str]] = Field(None, description="Data sources used or considered.")
    purpose: Optional[str] = Field(None, description="The purpose of the action or system.")
    stakeholders: Optional[List[str]] = Field(None, description="Key stakeholders involved or affected.")
    # Add other relevant contextual fields as needed

class EthicalConcern(BaseModel):
    principle: str = Field(..., description="The ethical principle or area of concern.")
    severity: str = Field(..., description="Severity of the concern (e.g., low, medium, high).")
    description: str = Field(..., description="Description of the ethical concern.")

class EthicalRecommendation(BaseModel):
    action: str = Field(..., description="Recommended action to address the concern or improve ethical posture.")
    priority: str = Field(..., description="Priority of the recommendation (e.g., low, medium, high).")
    rationale: str = Field(..., description="Rationale behind the recommendation.")

class EthicsEvaluationRequest(BaseModel):
    action: str = Field(..., description="The action, decision, or system component to be evaluated.")
    context: EthicsEvaluationRequestContext = Field(..., description="Contextual information surrounding the action.")
    options: Optional[EthicsEvaluationOptions] = Field(None, description="Options for the evaluation process.")

class EthicsEvaluationResult(BaseModel):
    evaluation_id: Optional[str] = Field(None, description="Unique ID for this evaluation.")
    ethical_score: Optional[float] = Field(None, description="An overall ethical score, if applicable.")
    compliant: bool = Field(..., description="Whether the action is deemed compliant with the ethical framework.")
    concerns: List[EthicalConcern] = Field(..., description="List of identified ethical concerns.")
    recommendations: List[EthicalRecommendation] = Field(..., description="List of recommendations.")
    explanation_token: Optional[str] = Field(None, description="Token to retrieve detailed explanation.")
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the evaluation was performed.")
    overall_rating: Optional[str] = Field(None, description="Qualitative rating of the ethical assessment.")

# Explanation Models
class EthicsExplanationRequest(BaseModel):
    evaluation_id: str = Field(..., description="ID of the evaluation to explain.")
    explanation_token: str = Field(..., description="Security token provided with the evaluation result.")
    detail_level: Optional[str] = Field("comprehensive", description="Level of detail for the explanation.")

class EthicsExplanation(BaseModel):
    evaluation_id: str = Field(..., description="ID of the evaluation being explained.")
    explanation: str = Field(..., description="Detailed explanation of the ethical assessment.")
    principles_applied: List[str] = Field(..., description="List of ethical principles applied in the assessment.")
    rule_references: Optional[List[str]] = Field(None, description="References to specific ethical rules applied.")
    timestamp: datetime = Field(..., description="Timestamp when the explanation was generated.")

# Suggestion Models
class EthicalAlternative(BaseModel):
    title: str = Field(..., description="Short title for the alternative.")
    description: str = Field(..., description="Detailed description of the alternative approach.")
    benefits: List[str] = Field(..., description="Ethical benefits of this alternative.")
    considerations: Optional[List[str]] = Field(None, description="Potential considerations or trade-offs.")
    principles_addressed: List[str] = Field(..., description="Ethical principles addressed by this alternative.")

class EthicsSuggestionRequest(BaseModel):
    evaluation_id: Optional[str] = Field(None, description="Optional ID of a previous evaluation.")
    action_description: Optional[str] = Field(None, description="Description of the action if no evaluation_id is provided.")
    context: Optional[EthicsEvaluationRequestContext] = Field(None, description="Context if no evaluation_id is provided.")
    ethical_concerns: Optional[List[str]] = Field(None, description="Specific concerns to address.")
    suggestion_count: Optional[int] = Field(3, description="Number of alternatives to suggest.")

class EthicsSuggestionResponse(BaseModel):
    request_id: str = Field(..., description="Unique ID for this suggestion request.")
    alternatives: List[EthicalAlternative] = Field(..., description="List of suggested ethical alternatives.")
    original_evaluation_id: Optional[str] = Field(None, description="ID of the original evaluation if applicable.")
    timestamp: datetime = Field(..., description="Timestamp when the suggestions were generated.")

# Framework Management Models
class EthicsFramework(BaseModel):
    id: str = Field(..., description="Unique identifier for the framework.")
    name: str = Field(..., description="Human-readable name of the framework.")
    description: str = Field(..., description="Description of the ethical framework.")
    version: str = Field(..., description="Version of the framework.")
    principles: List[str] = Field(..., description="Core principles of the framework.")
    last_updated: datetime = Field(..., description="When the framework was last updated.")
    active: bool = Field(True, description="Whether the framework is currently active.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the framework.")

class EthicsFrameworkCreateRequest(BaseModel):
    name: str = Field(..., description="Human-readable name of the framework.")
    description: str = Field(..., description="Description of the ethical framework.")
    version: str = Field("1.0", description="Version of the framework.")
    principles: List[str] = Field(..., description="Core principles of the framework.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the framework.")

class EthicsFrameworkUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Updated name for the framework.")
    description: Optional[str] = Field(None, description="Updated description.")
    principles: Optional[List[str]] = Field(None, description="Updated principles.")
    active: Optional[bool] = Field(None, description="Updated active status.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata.")

# Audit Models
class AuditLogEntry(BaseModel):
    log_id: str = Field(..., description="Unique identifier for this audit log entry.")
    timestamp: datetime = Field(..., description="When this action occurred.")
    action_type: str = Field(..., description="Type of action (e.g., 'evaluation', 'explanation', 'framework_update').")
    user_id: Optional[str] = Field(None, description="ID of the user who performed the action, if available.")
    resource_id: Optional[str] = Field(None, description="ID of the resource acted upon (e.g., evaluation_id).")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Summary of the request data.")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Summary of the response data.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about this audit entry.")
    # Additional fields used throughout the API that weren't originally defined
    endpoint_called: Optional[str] = Field(None, description="The API endpoint that was called.")
    request_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of the request for easier auditing.")
    response_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of the response for easier auditing.")

class EthicsAuditResponse(BaseModel):
    logs: List[AuditLogEntry] = Field(..., description="List of audit log entries.")
    total_count: int = Field(..., description="Total number of logs matching the filter criteria.")
    page: int = Field(..., description="Current page number.")
    page_size: int = Field(..., description="Number of logs per page.")
    has_more: bool = Field(..., description="Whether there are more logs available.")

# General API Response Models
class StatusResponse(BaseModel):
    status: str = Field(..., description="Status of the operation (e.g., 'success', 'error').")
    message: str = Field(..., description="Descriptive message about the operation result.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details or context, if applicable.")