# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md)
# - [Windsurf Integration Plan](./docs/ATRiAN_Windsurf_Integration_Plan.md)
# - [EGOS Global Rules](../.windsurfrules) (Section 20 - ATRiAN Integration)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import logging
import os
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime

# Import ATRiAN components
from atrian_ethical_compass import EthicalCompass
from atrian_trust_weaver import WeaverOfTrust, TrustDimension
from atrian_ethics_trust_integration import EthicsTrustIntegration, EthicsTrustEvent
from atrian_silent_guide import SilentGuide, GuidanceContext, GuidanceType

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Constants
DEFAULT_ADAPTER_CONFIG_PATH = "./atrian_windsurf_config.yaml"
MEMORY_KEY_PREFIX = "atrian_windsurf_"
SENSITIVE_OPERATIONS = [
    "file_creation", "code_generation", "system_config", 
    "authentication", "data_access", "external_api_call"
]
PRIVACY_KEYWORDS = [
    "personal", "private", "sensitive", "confidential", 
    "user data", "password", "credential", "token", "api key"
]

class WindsurfOperationType(Enum):
    """Types of operations performed in the Windsurf IDE."""
    FILE_CREATION = "file_creation"
    FILE_MODIFICATION = "file_modification"
    CODE_GENERATION = "code_generation"
    CODE_EDITING = "code_editing"
    SYSTEM_CONFIG = "system_config"
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    EXTERNAL_API_CALL = "external_api_call"
    USER_INTERACTION = "user_interaction"
    GENERAL = "general"

class ATRiANWindsurfAdapter:
    """Adapter that connects ATRiAN components to Windsurf IDE."""
    
    def __init__(self, config_filepath: str = DEFAULT_ADAPTER_CONFIG_PATH):
        """
        Initialize the adapter with ATRiAN components.
        
        Args:
            config_filepath: Path to adapter configuration file
        """
        self.config_filepath = config_filepath
        self.config = {}
        self._load_config()
        
        # Initialize ATRiAN components
        self.ethical_compass = EthicalCompass()
        self.trust_weaver = WeaverOfTrust()
        self.ethics_trust = EthicsTrustIntegration(self.ethical_compass, self.trust_weaver)
        self.silent_guide = SilentGuide(self.ethics_trust)
        
        # Track active operations and their states
        self.active_operations = {}
        
        logger.info("ATRiANWindsurfAdapter initialized with ATRiAN components")
    
    def _load_config(self) -> None:
        """Load the adapter configuration from YAML."""
        if os.path.exists(self.config_filepath):
            try:
                with open(self.config_filepath, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        self.config = config
                        logger.info(f"Loaded ATRiANWindsurfAdapter configuration from '{self.config_filepath}'")
                    else:
                        logger.warning(f"Adapter config file '{self.config_filepath}' is empty or malformed")
            except Exception as e:
                logger.error(f"Error loading adapter config file '{self.config_filepath}': {e}")
        else:
            logger.info(f"No adapter config file found at '{self.config_filepath}', using defaults")
            self._initialize_default_config()
    
    def _initialize_default_config(self) -> None:
        """Initialize default configuration when no config file is found."""
        self.config = {
            "enable_auto_guidance": True,
            "enable_trust_tracking": True,
            "notification_threshold": 0.6,  # Higher values = fewer notifications
            "privacy_sensitivity": 0.8,     # Higher values = more privacy protections
            "operation_mapping": {
                "file_creation": "DATA_HANDLING",
                "file_modification": "DATA_HANDLING",
                "code_generation": "CODE_EDITING",
                "code_editing": "CODE_EDITING",
                "system_config": "SYSTEM_OPERATION",
                "authentication": "SECURITY_OPERATION",
                "data_access": "DATA_HANDLING",
                "external_api_call": "SECURITY_OPERATION",
                "user_interaction": "USER_INTERACTION",
                "general": "GENERAL"
            }
        }
    
    def evaluate_operation(self, 
                           operation_type: Union[str, WindsurfOperationType], 
                           context: Dict[str, Any], 
                           user_id: str = "User") -> Dict[str, Any]:
        """
        Evaluate an operation using ATRiAN components.
        
        Args:
            operation_type: The type of operation being performed
            context: Contextual information about the operation
            user_id: Identifier for the user performing the operation
            
        Returns:
            A dictionary containing the evaluation results
        """
        # Normalize operation type
        if isinstance(operation_type, str):
            try:
                operation_type = WindsurfOperationType(operation_type)
            except ValueError:
                operation_type = WindsurfOperationType.GENERAL
                logger.warning(f"Unrecognized operation_type '{operation_type}', defaulting to GENERAL")
        
        # Map operation type to guidance context
        context_mapping = self.config.get("operation_mapping", {})
        guidance_context_str = context_mapping.get(
            operation_type.value, 
            "GENERAL"
        )
        
        try:
            guidance_context = GuidanceContext[guidance_context_str]
        except (KeyError, ValueError):
            guidance_context = GuidanceContext.GENERAL
            logger.warning(f"Could not map operation {operation_type.value} to guidance context {guidance_context_str}, using GENERAL")
        
        # Generate operation ID for tracking
        operation_id = f"{operation_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(context))}"
        self.active_operations[operation_id] = {
            "type": operation_type.value,
            "context": context,
            "user_id": user_id,
            "start_time": datetime.now().isoformat()
        }
        
        # Enhance context with privacy keywords detection
        context_str = json.dumps(context).lower()
        privacy_matches = [kw for kw in PRIVACY_KEYWORDS if kw.lower() in context_str]
        contains_sensitive_data = len(privacy_matches) > 0
        
        enhanced_context = context.copy()
        enhanced_context["__atrian_metadata"] = {
            "operation_id": operation_id,
            "contains_sensitive_data": contains_sensitive_data,
            "detected_privacy_keywords": privacy_matches,
            "is_sensitive_operation": operation_type.value in SENSITIVE_OPERATIONS
        }
        
        # Get guidance from Silent Guide
        guidance = self.silent_guide.provide_guidance(enhanced_context, user_id, guidance_context)
        
        # Process ethics trust event if appropriate
        if contains_sensitive_data:
            if guidance["ethical_assessment"]["allowed"]:
                self.ethics_trust.process_ethics_trust_event(
                    user_id,
                    EthicsTrustEvent.PRIVACY_RESPECT,
                    f"Proper handling of sensitive data in {operation_type.value} operation",
                    0.05
                )
            else:
                self.ethics_trust.process_ethics_trust_event(
                    user_id,
                    EthicsTrustEvent.PRIVACY_VIOLATION,
                    f"Potential privacy concern in {operation_type.value} operation",
                    0.1
                )
        
        # Determine notification level based on trust and ethics assessment
        should_notify = (
            not guidance["ethical_assessment"]["allowed"] or
            guidance["trust_assessment"]["overall_score"] < self.config.get("notification_threshold", 0.6) or
            (contains_sensitive_data and self.config.get("privacy_sensitivity", 0.8) > 0.5)
        )
        
        # Complete the operation record
        self.active_operations[operation_id].update({
            "guidance": guidance["content"],
            "guidance_type": guidance["guidance_type"],
            "ethical_assessment": guidance["ethical_assessment"],
            "trust_assessment": guidance["trust_assessment"],
            "should_notify": should_notify,
            "end_time": datetime.now().isoformat()
        })
        
        # Prepare the evaluation result
        evaluation_result = {
            "operation_id": operation_id,
            "allowed": guidance["ethical_assessment"]["allowed"],
            "guidance": guidance["content"],
            "guidance_type": guidance["guidance_type"],
            "trust_level": guidance["trust_assessment"]["overall_score"],
            "should_notify": should_notify,
            "notification_priority": "high" if not guidance["ethical_assessment"]["allowed"] else (
                "medium" if contains_sensitive_data else "low"
            ),
            "ethical_warnings": guidance["ethical_assessment"]["warnings"],
            "contains_sensitive_data": contains_sensitive_data,
            "detected_keywords": privacy_matches
        }
        
        # Log the evaluation
        logger.info(f"Evaluated {operation_type.value} operation (ID: {operation_id}). Allowed: {evaluation_result['allowed']}, Should notify: {should_notify}")
        
        return evaluation_result
    
    def generate_notification(self, operation_id: str) -> Dict[str, Any]:
        """
        Generate a notification for the Windsurf IDE based on a previous operation evaluation.
        
        Args:
            operation_id: ID of the operation to generate notification for
            
        Returns:
            A dictionary containing notification details
        """
        if operation_id not in self.active_operations:
            logger.warning(f"Cannot generate notification for unknown operation ID: {operation_id}")
            return {"error": "Unknown operation ID"}
        
        operation = self.active_operations[operation_id]
        
        if not operation.get("should_notify", False):
            logger.info(f"Operation {operation_id} does not require notification")
            return {"notification_required": False}
        
        notification_type = "warning" if not operation["ethical_assessment"]["allowed"] else "info"
        
        notification = {
            "notification_required": True,
            "type": notification_type,
            "title": f"ATRiAN {notification_type.capitalize()}: {operation['type']}",
            "message": operation["guidance"],
            "priority": operation.get("notification_priority", "medium"),
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # Add suggested actions based on the evaluation
        if notification_type == "warning":
            notification["actions"].append({
                "label": "Review Ethics Guidelines",
                "action": "show_ethics_guidelines"
            })
            
        if operation.get("contains_sensitive_data", False):
            notification["actions"].append({
                "label": "Review Privacy Best Practices",
                "action": "show_privacy_guidelines"
            })
        
        logger.info(f"Generated {notification_type} notification for operation {operation_id}")
        return notification
    
    def generate_adaptive_interface(self, user_id: str) -> Dict[str, Any]:
        """
        Generate adaptive interface recommendations for Windsurf IDE.
        
        Args:
            user_id: The user ID to generate interface recommendations for
            
        Returns:
            A dictionary containing interface recommendations
        """
        return self.silent_guide.generate_adaptive_interface(user_id)
    
    def persist_state_to_memory(self, memory_system) -> None:
        """
        Persist ATRiAN state to Windsurf memory system.
        
        Args:
            memory_system: Windsurf memory system interface
        """
        # Trust scores
        try:
            memory_system.create_memory(
                action="create" if not memory_system.get_memory_by_title("ATRiAN Trust Scores") else "update",
                title="ATRiAN Trust Scores",
                content=json.dumps(self.trust_weaver.dynamic_trust_scores),
                tags=["atrian", "trust_scores", "windsurf_integration"],
                corpus_names=["c:/EGOS"]
            )
            logger.info("Successfully persisted trust scores to Windsurf memory")
        except Exception as e:
            logger.error(f"Error persisting trust scores: {e}")
        
        # Recent guidance
        try:
            recent_guidance = self.silent_guide.get_guidance_history(limit=20)
            memory_system.create_memory(
                action="create" if not memory_system.get_memory_by_title("ATRiAN Recent Guidance") else "update",
                title="ATRiAN Recent Guidance",
                content=json.dumps(recent_guidance),
                tags=["atrian", "guidance_history", "windsurf_integration"],
                corpus_names=["c:/EGOS"]
            )
            logger.info("Successfully persisted recent guidance to Windsurf memory")
        except Exception as e:
            logger.error(f"Error persisting recent guidance: {e}")
    
    def load_state_from_memory(self, memory_system) -> None:
        """
        Load ATRiAN state from Windsurf memory system.
        
        Args:
            memory_system: Windsurf memory system interface
        """
        # Trust scores
        try:
            trust_scores_memory = memory_system.get_memory_by_title("ATRiAN Trust Scores")
            if trust_scores_memory:
                trust_scores = json.loads(trust_scores_memory.content)
                self.trust_weaver.dynamic_trust_scores.update(trust_scores)
                logger.info("Successfully loaded trust scores from Windsurf memory")
        except Exception as e:
            logger.error(f"Error loading trust scores: {e}")
    
    def get_operation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent operation history.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            A list of recent operations
        """
        operations = list(self.active_operations.values())
        return operations[-limit:]


# Example usage (won't execute when imported)
if __name__ == "__main__":
    print("=== ATRiAN Windsurf Adapter Example ===")
    
    # Initialize adapter
    adapter = ATRiANWindsurfAdapter()
    
    # Example operation evaluation
    file_creation_context = {
        "file_path": "/example/user_data.py",
        "file_content": "def save_user_data(user_id, personal_info):\n    database.store(user_id, personal_info)",
        "file_type": "python",
        "user_intent": "creating data storage module"
    }
    
    result = adapter.evaluate_operation(
        WindsurfOperationType.FILE_CREATION,
        file_creation_context,
        "ExampleUser"
    )
    
    print(f"\nOperation Evaluation:")
    print(f"Allowed: {result['allowed']}")
    print(f"Guidance: {result['guidance']}")
    print(f"Should Notify: {result['should_notify']}")
    
    # Generate notification if needed
    if result['should_notify']:
        notification = adapter.generate_notification(result['operation_id'])
        print(f"\nNotification:")
        print(f"Type: {notification['type']}")
        print(f"Message: {notification['message']}")
        print(f"Actions: {notification['actions']}")
    
    print("\n=== Adapter Demo Complete ===")