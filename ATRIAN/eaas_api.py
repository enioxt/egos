# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# C:/EGOS/ATRiAN/eaas_api.py
"""
ATRiAN Ethics as a Service (EaaS) API

This module implements the FastAPI application for ATRiAN EaaS, providing
endpoints for ethical evaluation, explanation, suggestions, framework management,
and auditing, as defined in the EaaS Integration Plan.

Version: 0.2.0 (Integrated with EthicalCompass core logic)
Last Modified: 2025-06-01

@references
  - file:///C:/EGOS/ATRiAN/EaaS_Integration_Plan.md
  - file:///C:/EGOS/ROADMAP.md (MON-EAAS-001-P1-02)
  - file:///C:/EGOS/ATRiAN/eaas_models.py
  - file:///C:/EGOS/ATRiAN/atrian_ethical_compass.py
"""

from fastapi import FastAPI, HTTPException, Path, Query, Depends
from typing import List, Dict, Any, Optional
import uuid
import os
import logging
import json
from datetime import datetime, timedelta # Added timedelta for audit log generation
from functools import lru_cache
import hashlib

# Import the persistence manager
from eaas_persistence import EaasPersistenceManager

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Import models from the new eaas_models.py
from eaas_models import (
    EthicsEvaluationOptions, EthicsEvaluationRequestContext, EthicsEvaluationRequest,
    EthicalConcern, EthicalRecommendation, EthicsEvaluationResult,
    EthicsExplanationRequest, EthicsExplanation,
    EthicsSuggestionRequest, EthicalAlternative, EthicsSuggestionResponse,
    EthicsFramework, EthicsFrameworkCreateRequest, EthicsFrameworkUpdateRequest,
    AuditLogEntry, EthicsAuditResponse, StatusResponse
)

# Import the EthicalCompass
from atrian_ethical_compass import EthicalCompass

# Initialize FastAPI app
app = FastAPI(
    title="ATRiAN Ethics as a Service (EaaS) API",
    version="0.3.1",  # Updated version to reflect code refinements
    description="API for ATRiAN's ethical guidance capabilities, with integrated core evaluation logic and persistent storage."
)

# Health check endpoint
@app.get("/health", response_model=StatusResponse, tags=["System"])
async def health_check():
    """Liveness probe for monitoring and CI tests."""
    return StatusResponse(status="success", message="EaaS API is running")

# Define the data directory for persistence
DATA_DIR = os.environ.get("ATRIAN_DATA_DIR", "C:/EGOS/ATRiAN/data")

# Service Dependencies container for better testing and dependency injection
class ServiceDependencies:
    """Container for service dependencies to facilitate testing."""
    def __init__(self, 
                persistence_manager: EaasPersistenceManager = None,
                ethical_compass_instance: EthicalCompass = None):
        self.persistence_manager = persistence_manager or EaasPersistenceManager(data_dir=DATA_DIR)
        self.ethical_compass = ethical_compass_instance or EthicalCompass(rules_filepath="C:/EGOS/ATRiAN/ethics_rules.yaml")

# Instantiate the EthicalCompass
# It will load rules from C:/EGOS/ATRiAN/ethics_rules.yaml by default (if present)
ethical_compass = EthicalCompass(rules_filepath="C:/EGOS/ATRiAN/ethics_rules.yaml")

# Create a persistence manager instance
persistence = EaasPersistenceManager(data_dir=DATA_DIR)

# Default production dependencies
default_dependencies = ServiceDependencies(
    persistence_manager=persistence,
    ethical_compass_instance=ethical_compass
)

# Utility functions

def create_audit_entry(action_type: str, endpoint_called: str, 
                     user_id: str = "anonymous", request_summary: dict = None,
                     resource_id: str = None, metadata: dict = None) -> AuditLogEntry:
    """
    Create a standardized audit log entry with common defaults.
    
    Args:
        action_type: Type of action being performed (e.g., "evaluate_ethics")
        endpoint_called: The API endpoint being called
        user_id: ID of the user making the request (default "anonymous")
        request_summary: Dictionary summarizing the request contents
        resource_id: ID of the resource being accessed or created
        metadata: Additional metadata about the request
        
    Returns:
        AuditLogEntry: A properly initialized audit log entry
    """
    return AuditLogEntry(
        log_id=f"log_{uuid.uuid4()}",
        timestamp=datetime.utcnow(),
        action_type=action_type,
        endpoint_called=endpoint_called,
        user_id=user_id,
        request_summary=request_summary or {},
        resource_id=resource_id,
        metadata=metadata or {}
    )
    
def handle_not_found(resource_type: str, resource_id: str, 
                     audit_entry: AuditLogEntry = None,
                     persistence_mgr: EaasPersistenceManager = None) -> None:
    """
    Standardized handling of not found resources with audit logging.
    
    Args:
        resource_type: Type of resource not found (e.g., "ethical framework", "evaluation")
        resource_id: ID of the resource that wasn't found
        audit_entry: Optional audit entry to update with error information
        persistence_mgr: Optional persistence manager to log the updated audit entry
        
    Raises:
        HTTPException: Always raises a 404 error with standardized detail message
    """
    if audit_entry and persistence_mgr:
        audit_entry.response_summary = {
            "error": "not_found", 
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        persistence_mgr.log_audit_entry(audit_entry)
        
    raise HTTPException(
        status_code=404, 
        detail=f"{resource_type.capitalize()} with ID '{resource_id}' not found."
    )

# Dependency to get the persistence manager
def get_persistence():
    return persistence
    
# Dependency injection function for service dependencies
def get_dependencies() -> ServiceDependencies:
    """Provides service dependencies, can be overridden in tests."""
    return default_dependencies

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)

# Log startup information
logger.info(f"ATRiAN EaaS API initialized with data directory: {DATA_DIR}")
# Use getattr with a default value to avoid AttributeError
rules_filepath = getattr(ethical_compass, 'rules_filepath', 'unknown_location')
logger.info(f"EthicalCompass initialized with rules from: {rules_filepath}")

# --- Utility Functions ---

# Cache helper functions
def get_cache_key(evaluation_request: dict) -> str:
    """Generate a unique cache key for an evaluation request."""
    request_str = f"{evaluation_request.get('action')}-{json.dumps(evaluation_request.get('context', {}))}"
    return hashlib.md5(request_str.encode()).hexdigest()

@lru_cache(maxsize=100)  # Cache the last 100 evaluation results
def cached_ethical_evaluation(action: str, context_json: str, options_json: str):
    """Cache evaluation results based on input parameters."""
    context = json.loads(context_json) if context_json else {}
    options = json.loads(options_json) if options_json else {}
    return ethical_compass.evaluate_action(action, context, options)
    
# Validation functions
def validate_evaluation_request(request: EthicsEvaluationRequest) -> None:
    """Validate ethics evaluation request fields."""
    if not request.action or len(request.action.strip()) == 0:
        raise HTTPException(status_code=422, detail="Action description cannot be empty")
    
    if len(request.action) > 5000:  # Reasonable limit
        raise HTTPException(status_code=422, detail="Action description exceeds maximum length (max: 5000 characters)")
    
    # Additional validation as needed for context fields
    if request.context and request.context.data_sources:
        for source in request.context.data_sources:
            if len(source) > 1000:  # Reasonable limit for data source descriptions
                raise HTTPException(status_code=422, detail="Data source description too long (max: 1000 characters)")

# --- API Endpoints ---

@app.post("/ethics/evaluate", response_model=EthicsEvaluationResult, tags=["Ethics Evaluation"])
async def evaluate_ethics(request: EthicsEvaluationRequest, 
                           dependencies: ServiceDependencies = Depends(get_dependencies)):
    """
    Evaluates the ethical implications of a given action, decision, or system component
    using the integrated ATRiAN EthicalCompass.

    - **action**: Description of what needs to be evaluated.
    - **context**: Detailed context (domain, data sources, purpose, stakeholders).
    - **options**: Evaluation options (detail level, include alternatives).
    """
    evaluation_id = f"eval_{uuid.uuid4()}"
    # The explanation_token might be generated by the compass or handled differently later.
    # For now, we'll keep a placeholder generation here if not returned by compass.
    explanation_token = f"expl_token_{uuid.uuid4()}" 

    # Validate the request
    validate_evaluation_request(request)
    
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the evaluation request for auditing using the utility function
    audit_entry = create_audit_entry(
        action_type="evaluate_ethics",
        endpoint_called="/ethics/evaluate",
        request_summary={
            "action": request.action[:100] + "..." if len(request.action) > 100 else request.action,
            "domain": request.context.domain if request.context.domain else "general"
        },
        metadata={
            "data_sources_count": len(request.context.data_sources) if request.context.data_sources else 0
        }
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Check if we have a cached result
    context_json = json.dumps(request.context.dict()) if request.context else "{}"
    options_json = json.dumps(request.options.dict()) if request.options else "{}"
    cache_key = get_cache_key({"action": request.action, "context": context_json, "options": options_json})
    
    try:
        # Try to get cached result (optimization)
        core_evaluation_result = cached_ethical_evaluation(
            request.action,
            context_json,
            options_json
        )
        logger.info(f"Using cached evaluation result for key {cache_key[:8]}...")
    except Exception as e:
        # If cache fails or not available, use direct evaluation
        logger.warning(f"Cache error or miss: {str(e)[:100]}")
        core_evaluation_result = dependencies.ethical_compass.evaluate_action(
            action_description=request.action,
            context=request.context,
            options=request.options
        )

    # Create a dictionary from the core result and add the API-specific fields
    result_dict = core_evaluation_result.dict()
    result_dict.update({
        'evaluation_id': evaluation_id,
        'explanation_token': explanation_token,
        'timestamp': datetime.utcnow()
    })
    
    # Create a new EthicsEvaluationResult instance for the API response
    api_response = EthicsEvaluationResult(**result_dict)
    
    # Save the evaluation result to persistent storage
    if not persistence_mgr.save_evaluation(api_response):
        logger.warning(f"Failed to save evaluation result {evaluation_id} to persistent storage")
    else:
        logger.info(f"Saved evaluation result {evaluation_id} to persistent storage")
    
    # Update the audit log with the evaluation result
    audit_entry.response_summary = {
        "evaluation_id": evaluation_id,
        "compliant": api_response.compliant,
        "ethical_score": api_response.ethical_score,
        "concerns_count": len(api_response.concerns) if api_response.concerns else 0
    }
    audit_entry.resource_id = evaluation_id
    persistence_mgr.log_audit_entry(audit_entry)
    
    return api_response

@app.post("/ethics/explain", response_model=EthicsExplanation, tags=["Ethics Explanation"])
async def explain_ethics(request: EthicsExplanationRequest, 
                          dependencies: ServiceDependencies = Depends(get_dependencies)):
    """
    Provides a detailed explanation for a previous ethical evaluation.
    Now integrated with persistence to retrieve actual evaluation results.

    - **evaluation_id**: The ID of the evaluation to explain.
    - **explanation_token**: Security token (if required by future implementation).
    """
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Validate the request
    if not request.evaluation_id or not request.evaluation_id.strip():
        raise HTTPException(status_code=422, detail="Evaluation ID cannot be empty")
    
    # Audit the request using the utility function
    user_id = request.user_id if hasattr(request, "user_id") and request.user_id else "anonymous"
    audit_entry = create_audit_entry(
        action_type="explain_ethics",
        endpoint_called="/ethics/explain",
        user_id=user_id,
        request_summary={
            "evaluation_id": request.evaluation_id,
        },
        resource_id=request.evaluation_id
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Try to retrieve the actual evaluation from persistent storage
    stored_evaluation = persistence_mgr.get_evaluation(request.evaluation_id)
    
    # Check if we have a stored explanation already
    stored_explanation = persistence_mgr.get_explanation(request.evaluation_id)
    if stored_explanation:
        logger.info(f"Retrieved existing explanation for evaluation {request.evaluation_id}")
        
        # Update audit log
        audit_entry.response_summary = {"found": True, "source": "cache"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        return stored_explanation
    
    # If we have the related evaluation, generate explanation based on actual data
    if stored_evaluation:
        # Generate a more specific explanation based on the actual evaluation
        principles = []
        rule_references = []
        explanation_details = []
        
        # Extract principles and references from concerns
        if stored_evaluation.concerns:
            for concern in stored_evaluation.concerns:
                if concern.principle and concern.principle not in principles:
                    principles.append(concern.principle)
                explanation_details.append(f"Concern: {concern.description}")
                
        # If we have recommendations, include them in the explanation
        if stored_evaluation.recommendations:
            for rec in stored_evaluation.recommendations:
                explanation_details.append(f"Recommendation: {rec.action}. Rationale: {rec.rationale}")
        
        # Add default principles if none found
        if not principles:
            principles = ["Sacred Privacy", "Universal Accessibility", "Integrated Ethics"]
            
        # Create references based on actual principles
        for principle in principles:
            if "privacy" in principle.lower():
                rule_references.append("MQP Section on Sacred Privacy")
            elif "ethics" in principle.lower():
                rule_references.append("Integrated Ethics Framework")
            
        # Always include the rules source
        rule_references.append("ATRiAN/ethics_rules.yaml")
        
        # Create the explanation text
        if explanation_details:
            explanation_text = "Detailed explanation based on evaluation results:\n\n" + "\n\n".join(explanation_details)
        else:
            explanation_text = ("Detailed explanation: The evaluation assessed the ethical implications of the action "
                               f"with an ethical score of {stored_evaluation.ethical_score} "
                               f"and found it to be {'' if stored_evaluation.compliant else 'non-'}compliant with the ethical framework.")
        
        explanation = EthicsExplanation(
            evaluation_id=request.evaluation_id,
            explanation=explanation_text,
            principles_applied=principles,
            rule_references=rule_references,
            timestamp=datetime.utcnow()
        )
        
        # Save the explanation to persistent storage
        if persistence_mgr.save_explanation(explanation):
            logger.info(f"Saved explanation for evaluation {request.evaluation_id} to persistent storage")
            
        # Update audit log
        audit_entry.response_summary = {
            "found": True, 
            "source": "generated", 
            "principles_count": len(principles)
        }
        persistence_mgr.log_audit_entry(audit_entry)
        
        return explanation
        
    # Fall back to generic explanation if we don't have the evaluation stored
    if request.evaluation_id.startswith("eval_"):
        logger.warning(f"Evaluation {request.evaluation_id} not found in storage, generating generic explanation")
        
        related_concern_desc = "General ethical considerations apply. Specific details depend on the evaluation context."
        if "sensitive_data" in request.evaluation_id.lower(): # very naive check for demo
            related_concern_desc = "The evaluation likely highlighted concerns regarding data privacy due to the use of sensitive data. Recommendations would focus on enhancing data protection measures."

        explanation = EthicsExplanation(
            evaluation_id=request.evaluation_id,
            explanation="Detailed explanation: " + related_concern_desc + " (Note: This is a generic explanation as the original evaluation was not found in storage)",
            principles_applied=["Sacred Privacy", "Universal Accessibility", "Integrated Ethics"],
            rule_references=["MQP Section on Sacred Privacy", "ATRiAN/ethics_rules.yaml", "EaaS API Documentation"],
            timestamp=datetime.utcnow()
        )
        
        # Save even the generic explanation to avoid regenerating it
        if persistence_mgr.save_explanation(explanation):
            logger.info(f"Saved generic explanation for evaluation {request.evaluation_id} to persistent storage")
            
        # Update audit log
        audit_entry.response_summary = {"found": False, "source": "generic"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        return explanation
    else:
        # Update audit log before raising exception
        audit_entry.response_summary = {"found": False, "error": "invalid_id_format"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=404, detail=f"Evaluation ID '{request.evaluation_id}' not found or explanation token invalid.")

@app.post("/ethics/suggest", response_model=EthicsSuggestionResponse, tags=["Ethics Suggestions"])
async def suggest_alternatives(request: EthicsSuggestionRequest, 
                               dependencies: ServiceDependencies = Depends(get_dependencies)):
    """
    Suggests ethical alternatives for an action or to address concerns from a previous evaluation.
    Now integrated with persistence to store suggestions and retrieve relevant evaluations.

    - **evaluation_id**: (Optional) ID of a previous evaluation.
    - **action_description**: (Optional) Original action if no evaluation_id.
    - **context**: (Optional) Original context if no evaluation_id.
    - **ethical_concerns**: Specific concerns to address.
    - **suggestion_count**: Desired number of alternatives.
    """
    # Generate a unique request ID
    request_id = f"req_{uuid.uuid4()}"
    
    # Log the request for auditing
    audit_entry = AuditLogEntry(
        log_id=f"log_{uuid.uuid4()}",
        timestamp=datetime.utcnow(),
        action_type="suggest_alternatives",
        endpoint_called="/ethics/suggest",
        user_id=request.context.user_id if hasattr(request, "context") and hasattr(request.context, "user_id") and request.context.user_id else "anonymous",
        request_summary={
            "evaluation_id": request.evaluation_id,
            "action_description": request.action_description[:100] + "..." if request.action_description and len(request.action_description) > 100 else request.action_description,
            "concerns_count": len(request.ethical_concerns) if request.ethical_concerns else 0
        },
        resource_id=request_id
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # If we have an evaluation_id, try to retrieve it from persistent storage
    original_evaluation = None
    if request.evaluation_id:
        original_evaluation = persistence_mgr.get_evaluation(request.evaluation_id)
        if original_evaluation:
            logger.info(f"Retrieved evaluation {request.evaluation_id} for generating suggestions")
    
    # Generate suggestions based on the evaluation or request
    alternatives = []
    
    # If we have the original evaluation, use its concerns to generate better suggestions
    if original_evaluation and original_evaluation.concerns:
        for i in range(request.suggestion_count or 2):  # Default to 2 suggestions if we have evaluation data
            # Select a concern to address - cycle through if we have multiple
            concern_index = i % len(original_evaluation.concerns)
            concern = original_evaluation.concerns[concern_index]
            
            # Generate a suggestion that specifically addresses this concern
            alternatives.append(
                EthicalAlternative(
                    title=f"Alternative to address {concern.principle}" if concern.principle else f"Alternative {i+1}",
                    description=f"To address the concern: '{concern.description}', consider implementing more robust controls that align with {concern.principle if concern.principle else 'ethical principles'}.",
                    benefits=["Enhanced alignment with ethical principles", "Reduced ethical risk", "Improved stakeholder trust"],
                    considerations=["Implementation effort", "Potential trade-offs with efficiency"] if i % 2 == 0 else ["Training requirements", "Monitoring needs"],
                    principles_addressed=[concern.principle] if concern.principle else ["Sacred Privacy", "Reciprocal Trust"]
                )
            )
    # Otherwise, generate more generic suggestions based on the request
    else:
        concern_summary = request.ethical_concerns[0] if request.ethical_concerns else 'general_ethical_guidelines'
        principles = []
        
        # Try to extract principles from concerns
        if request.ethical_concerns:
            for concern in request.ethical_concerns:
                if "privacy" in concern.lower():
                    principles.append("Sacred Privacy")
                elif "trust" in concern.lower():
                    principles.append("Reciprocal Trust")
                elif "access" in concern.lower():
                    principles.append("Universal Accessibility")
        
        # Default principles if none extracted
        if not principles:
            principles = ["Sacred Privacy", "Reciprocal Trust"]
        
        for i in range(request.suggestion_count or 1):
            alternatives.append(
                EthicalAlternative(
                    title=f"Alternative {i+1}",
                    description=f"For '{request.action_description or 'the specified action'}', consider applying data minimization or exploring privacy-enhancing technologies (PETs).",
                    benefits=["Enhanced privacy", "Reduced data exposure", "Better user control"],
                    considerations=["Implementation complexity", "Resource requirements"] if i % 2 == 0 else None,
                    principles_addressed=principles
                )
            )
    
    # Create the response
    suggestion_response = EthicsSuggestionResponse(
        request_id=request_id,
        alternatives=alternatives,
        original_evaluation_id=request.evaluation_id,
        timestamp=datetime.utcnow()
    )
    
    # Save the suggestion to persistent storage
    if persistence_mgr.save_suggestion(suggestion_response):
        logger.info(f"Saved suggestion response {request_id} to persistent storage")
    else:
        logger.warning(f"Failed to save suggestion response {request_id} to persistent storage")
    
    # Update the audit log
    audit_entry.response_summary = {
        "request_id": request_id,
        "alternatives_count": len(alternatives),
        "based_on_evaluation": True if original_evaluation else False
    }
    persistence_mgr.log_audit_entry(audit_entry)
    
    return suggestion_response


# Initialize the frameworks on startup
@app.on_event("startup")
async def initialize_frameworks():
    """Initialize the ethical frameworks data on API startup."""
    # Check if we already have frameworks in the persistence store
    frameworks = persistence.get_frameworks()
    
    if not frameworks:
        logger.info("No frameworks found in persistence store. Initializing default frameworks.")
        
        # Create the MQP v9 framework
        mqp_framework = EthicsFramework(
            id="mqp_v9_full_moon",
            name="Master Quantum Prompt v9.0 'Full Moon Blueprint' Core Tenets",
            version="9.0",
            description="Core ethical and operational principles of the EGOS system, derived from MQP.md. These form a foundational ethical framework.",
            principles=["Universal Redemption", "Compassionate Temporality", "Sacred Privacy", "Universal Accessibility", 
                      "Unconditional Love", "Reciprocal Trust", "Integrated Ethics", "Conscious Modularity", 
                      "Systemic Cartography", "Evolutionary Preservation"],
            last_updated=datetime.utcnow(),
            active=True,
            metadata={
                "UR": {"title": "Universal Redemption", "summary": "Systems should be designed to allow for recovery, correction, and forgiveness, promoting learning and growth from errors rather than punitive outcomes."},
                "CT": {"title": "Compassionate Temporality", "summary": "Recognize and respect the evolving nature of understanding, context, and societal norms over time. Design for adaptability and future ethical shifts."},
                "SP": {"title": "Sacred Privacy", "summary": "Data concerning individuals is sacrosanct and must be protected with utmost rigor, ensuring confidentiality, integrity, and user control."},
                "UA": {"title": "Universal Accessibility", "summary": "Strive to make systems usable, beneficial, and equitable for all, irrespective of ability, background, or circumstance."},
                "UL": {"title": "Unconditional Love", "summary": "Design with empathy, aiming for positive impact, well-being, and fostering a supportive and constructive environment for users and society."},
                "RT": {"title": "Reciprocal Trust", "summary": "Systems should be transparent, reliable, and accountable, fostering a relationship of mutual trust with users and stakeholders."},
                "IE": {"title": "Integrated Ethics (ETHIK)", "summary": "Ethical considerations are woven into the fabric of the system's design, development, and operation, not merely as an afterthought."},
                "CM": {"title": "Conscious Modularity", "summary": "Components are designed with awareness of their interdependencies, potential impacts, and their role within the broader systemic and ethical context."},
                "SC": {"title": "Systemic Cartography", "summary": "Maintain a clear, dynamic, and understandable map of the system's components, data flows, decision points, and ethical touchpoints to ensure transparency and accountability."},
                "EP": {"title": "Evolutionary Preservation", "summary": "Ensure that the system can adapt and evolve in response to new knowledge and changing contexts while preserving its core ethical integrity and foundational principles."}
            }
        )
        
        # Create the ATRiAN rules framework
        atrian_rules_framework = EthicsFramework(
            id="atrian_rules_v1",
            name="ATRiAN Core Ethical Rules Set",
            version="1.0",
            description="The set of configurable ethical rules loaded by EthicalCompass from ethics_rules.yaml. This entry represents the live, operational ruleset.",
            principles=["Universal Redemption", "Sacred Privacy", "Integrated Ethics"],
            last_updated=datetime.utcnow(),
            active=True,
            metadata={"placeholder": "Content dynamically managed by EthicalCompass based on ethics_rules.yaml.", "rules_source": "C:/EGOS/ATRiAN/ethics_rules.yaml"}
        )
        
        # Save the frameworks to the persistence store
        if persistence.save_framework(mqp_framework):
            logger.info(f"Saved framework {mqp_framework.id} to persistence store")
        else:
            logger.error(f"Failed to save framework {mqp_framework.id} to persistence store")
            
        if persistence.save_framework(atrian_rules_framework):
            logger.info(f"Saved framework {atrian_rules_framework.id} to persistence store")
        else:
            logger.error(f"Failed to save framework {atrian_rules_framework.id} to persistence store")
    else:
        logger.info(f"Found {len(frameworks)} existing frameworks in persistence store")
        
        # Update the ATRiAN rules framework metadata based on current rules
        atrian_rules = next((f for f in frameworks if f.id == "atrian_rules_v1"), None)
        if atrian_rules and ethical_compass.rules:
            atrian_rules.metadata = {
                "rules_count": len(ethical_compass.rules),
                "rules_source": ethical_compass.rules_filepath,
                "last_loaded": datetime.utcnow().isoformat()
            }
            atrian_rules.last_updated = datetime.utcnow() # Or file mod time
            
            # Save the updated framework
            if persistence.save_framework(atrian_rules):
                logger.info(f"Updated framework {atrian_rules.id} with current rules metadata")
            else:
                logger.error(f"Failed to update framework {atrian_rules.id} metadata")
    
    # Log an audit entry for the initialization
    audit_entry = AuditLogEntry(
        log_id=f"log_{uuid.uuid4()}",
        timestamp=datetime.utcnow(),
        action_type="system",
        endpoint_called="startup",
        user_id="system",
        request_summary={"action": "initialize_frameworks"},
        response_summary={"frameworks_count": len(persistence.get_frameworks())}
    )
    persistence.log_audit_entry(audit_entry)

@app.get("/ethics/frameworks", response_model=List[EthicsFramework], tags=["Ethical Frameworks"])
async def list_ethical_frameworks(dependencies: ServiceDependencies = Depends(get_dependencies)):
    """Lists all available ethical frameworks known to the EaaS API."""
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the request for auditing
    audit_entry = create_audit_entry(
        action_type="list_frameworks",
        endpoint_called="/ethics/framework",
        user_id="anonymous",  # In a real implementation, this would come from authentication
        request_summary={"action": "list_all_frameworks"}
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Get all frameworks from persistent storage
    frameworks = persistence_mgr.get_all_frameworks()
    
    # Update the audit log
    audit_entry.response_summary = {"frameworks_count": len(frameworks)}
    persistence_mgr.log_audit_entry(audit_entry)
    
    return frameworks

@app.get("/ethics/framework/{framework_id}", response_model=EthicsFramework, tags=["Ethical Frameworks"])
async def get_ethical_framework(
    framework_id: str = Path(..., description="The ID of the ethical framework to retrieve."),
    dependencies: ServiceDependencies = Depends(get_dependencies)
):
    """
    Retrieves a specific ethical framework by its ID.
    """
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the request for auditing using the utility function
    audit_entry = create_audit_entry(
        action_type="get_framework",
        endpoint_called=f"/ethics/framework/{framework_id}",
        request_summary={"framework_id": framework_id},
        resource_id=framework_id
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Get the framework from persistent storage
    framework = persistence_mgr.get_framework(framework_id)
    if not framework:
        # Use the standardized error handling utility
        handle_not_found("ethical framework", framework_id, audit_entry, persistence_mgr)
    
    # Potentially refresh 'atrian_rules_v1' content if it's meant to be dynamic
    if framework_id == "atrian_rules_v1" and ethical_compass.rules:
        # This is a conceptual update; actual representation might differ
        framework.metadata = {
            "rules_count": len(ethical_compass.rules),
            "rules_source": ethical_compass.rules_filepath,
            "last_loaded": datetime.utcnow().isoformat()
        }
        framework.last_updated = datetime.utcnow() # Or file mod time
        
        # Save the updated framework
        if persistence_mgr.save_framework(framework):
            logger.info(f"Updated framework {framework_id} with current rules metadata")
        else:
            logger.error(f"Failed to update framework {framework_id} metadata")
    
    # Update the audit log
    audit_entry.response_summary = {"found": True, "version": framework.version}
    persistence_mgr.log_audit_entry(audit_entry)
    
    return framework

@app.put("/ethics/framework/{framework_id}", response_model=EthicsFramework, tags=["Ethical Frameworks"])
async def update_ethical_framework(
    framework_id: str = Path(..., description="The ID of the ethical framework to update."),
    update_request: EthicsFrameworkUpdateRequest = ...,
    dependencies: ServiceDependencies = Depends(get_dependencies)
):
    """
    Updates an existing ethical framework.
    Now integrated with the persistence layer for permanent storage.

    - **framework_id**: The ID of the framework to update.
    - **update_request**: The update details (name, description, principles, active status).
    """
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the request for auditing
    audit_entry = create_audit_entry(
        action_type="update_framework",
        endpoint_called=f"/ethics/framework/{framework_id}",
        user_id="anonymous",  # In a real implementation, this would come from authentication
        request_summary={
            "framework_id": framework_id,
            "update_fields": [
                field for field in ["name", "description", "principles", "active", "metadata"]
                if getattr(update_request, field) is not None
            ]
        },
        resource_id=framework_id
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Get the framework from persistent storage
    framework = persistence_mgr.get_framework(framework_id)
    if not framework:
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "not_found"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=404, detail=f"Ethical framework with ID '{framework_id}' not found.")
    
    # Update fields if provided in the request
    if update_request.name is not None:
        framework.name = update_request.name
    if update_request.description is not None:
        framework.description = update_request.description
    if update_request.principles is not None:
        framework.principles = update_request.principles
    if update_request.active is not None:
        framework.active = update_request.active
    if update_request.metadata is not None:
        # Merge with existing metadata instead of replacing
        if not framework.metadata:
            framework.metadata = {}
        framework.metadata.update(update_request.metadata)
    
    framework.last_updated = datetime.utcnow()
    
    # Save the updated framework
    if not persistence_mgr.save_framework(framework):
        logger.error(f"Failed to save updated framework {framework_id}")
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "persistence_failure"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=500, detail=f"Failed to save updated framework {framework_id}")
    
    # If this is the ATRiAN rules framework and we're changing active status,
    # we may need to reload rules in the EthicalCompass
    if framework_id == "atrian_rules_v1" and update_request.active is not None:
        # This is a placeholder for potential rule reloading logic
        if update_request.active:
            logger.info("Framework activation may require reloading rules in EthicalCompass")
        else:
            logger.info("Framework deactivation may require disabling rules in EthicalCompass")
    
    # Update the audit log
    audit_entry.response_summary = {"updated": True, "version": framework.version}
    persistence_mgr.log_audit_entry(audit_entry)
    
    return framework

@app.post("/ethics/framework", response_model=EthicsFramework, tags=["Ethical Frameworks"])
async def create_ethical_framework(
    framework_request: EthicsFrameworkCreateRequest,
    dependencies: ServiceDependencies = Depends(get_dependencies)
):
    """
    Creates a new ethical framework.
    Now integrated with the persistence layer for permanent storage.

    - **framework_request**: The framework details (name, description, principles, etc.).
    """
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the request using utility function
    audit_entry = create_audit_entry(
        action_type="create_framework",
        endpoint_called="/ethics/framework",
        user_id="anonymous",  # In a real implementation, this would come from authentication
        request_summary={
            "name": framework_request.name,
            "principles_count": len(framework_request.principles) if framework_request.principles else 0
        }
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Generate a unique ID for the new framework
    framework_id = f"framework_{uuid.uuid4().hex[:8]}"
    
    # Create the new framework object
    new_framework = EthicsFramework(
        id=framework_id,
        name=framework_request.name,
        version="1.0",  # Initial version
        description=framework_request.description,
        principles=framework_request.principles or [],
        last_updated=datetime.utcnow(),
        active=True,  # New frameworks are active by default
        metadata=framework_request.metadata or {}
    )
    
    # Save to the persistence store
    if not persistence_mgr.save_framework(new_framework):
        logger.error(f"Failed to save new framework {framework_id}")
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "persistence_failure"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=500, detail="Failed to save new ethical framework")
    
    # Update the audit log with success information
    audit_entry.response_summary = {"created": True, "id": framework_id}
    audit_entry.resource_id = framework_id  # Add the created resource ID to the audit
    persistence_mgr.log_audit_entry(audit_entry)
    
    return new_framework

@app.delete("/ethics/framework/{framework_id}", response_model=StatusResponse, tags=["Ethical Frameworks"])
async def delete_ethical_framework(
    framework_id: str = Path(..., description="The ID of the ethical framework to delete."),
    dependencies: ServiceDependencies = Depends(get_dependencies)
):
    """
    Deletes an ethical framework by ID.
    Now integrated with the persistence layer for permanent storage.

    - **framework_id**: The ID of the framework to delete.
    """
    # Extract persistence manager from dependencies
    persistence_mgr = dependencies.persistence_manager
    
    # Log the request using utility function
    audit_entry = create_audit_entry(
        action_type="delete_framework",
        endpoint_called=f"/ethics/framework/{framework_id}",
        user_id="anonymous",  # In a real implementation, this would come from authentication
        request_summary={"framework_id": framework_id},
        resource_id=framework_id
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Check if the framework exists
    framework = persistence_mgr.get_framework(framework_id)
    if not framework:
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "not_found"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=404, detail=f"Ethical framework with ID '{framework_id}' not found.")
    
    # Prevent deletion of core frameworks
    if framework_id in ["mqp_v9_full_moon", "atrian_rules_v1"]:
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "protected_framework"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=403, detail=f"Core framework '{framework_id}' cannot be deleted.")
    
    # Delete from the persistence store
    if not persistence_mgr.delete_framework(framework_id):
        logger.error(f"Failed to delete framework {framework_id}")
        # Update the audit log with the error
        audit_entry.response_summary = {"error": "persistence_failure"}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=500, detail=f"Failed to delete framework {framework_id}")
    
    # Update the audit log with success information
    audit_entry.response_summary = {"deleted": True}
    persistence_mgr.log_audit_entry(audit_entry)
    
    return StatusResponse(status="success", message=f"Ethical framework '{framework_id}' deleted successfully.")

@app.get("/ethics/audit", response_model=EthicsAuditResponse, tags=["Audit & Monitoring"])
async def get_audit_logs(
    start_date: Optional[datetime] = Query(None, description="Filter logs from this date/time"),
    end_date: Optional[datetime] = Query(None, description="Filter logs until this date/time"),
    action_type: Optional[str] = Query(None, description="Filter by action type (e.g., evaluate, explain, suggest)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    offset: int = Query(0, description="Number of logs to skip"),
    dependencies: ServiceDependencies = Depends(get_dependencies)
):
    """
    Retrieves audit logs of API usage with optional filtering.
    
    - **start_date**: Optional filter for logs after this date/time
    - **end_date**: Optional filter for logs before this date/time
    - **action_type**: Optional filter by action type
    - **user_id**: Optional filter by user ID
    - **limit**: Maximum number of logs to return (default: 100)
    - **offset**: Number of logs to skip for pagination (default: 0)
    """
    # Create audit log entry for this audit request itself
    audit_entry = AuditLogEntry(
        log_id=f"log_{uuid.uuid4()}",
        timestamp=datetime.utcnow(),
        action_type="retrieve_audit_logs",
        endpoint_called="/ethics/audit",
        user_id="anonymous",  # In a real implementation, this would come from authentication
        request_summary={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "action_type": action_type,
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }
    )
    persistence_mgr.log_audit_entry(audit_entry)
    
    # Get audit logs from persistence manager
    try:
        logs = persistence_mgr.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            action_type=action_type,
            limit=limit,
            offset=offset
        )
        
        # Update the audit log entry with success information
        audit_entry.response_summary = {"logs_count": len(logs)}
        persistence_mgr.log_audit_entry(audit_entry)
        
        return EthicsAuditResponse(
            logs=logs,
            total_count=len(logs),
            page=(offset // limit) + 1 if limit > 0 else 1,
            page_size=limit,
            has_more=len(logs) >= limit
        )
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        
        # Update the audit log entry with error information
        audit_entry.response_summary = {"error": str(e)}
        persistence_mgr.log_audit_entry(audit_entry)
        
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")

# To run this API (for development):
# Ensure you are in the C:/EGOS/ATRiAN/ directory in your terminal.
# Create a virtual environment if you haven't already:
#   python -m venv .venv
#   source .venv/bin/activate  (Linux/macOS)
#   .venv\Scripts\activate    (Windows)
# Install dependencies: pip install -r requirements.txt
# Then run from terminal: uvicorn eaas_api:app --reload
# Access interactive API docs (Swagger UI) at http://127.0.0.1:8000/docs
# Access ReDoc at http://127.0.0.1:8000/redoc

if __name__ == "__main__":
    import uvicorn
    # This is for development purposes only. 
    # For production, use a proper ASGI server like Gunicorn with Uvicorn workers.
    uvicorn.run("eaas_api:app", host="0.0.0.0", port=8000, reload=True)