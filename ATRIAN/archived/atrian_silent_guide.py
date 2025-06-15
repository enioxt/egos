# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md)
# - [WeaverOfTrust Enhancement](./docs/WeaverOfTrust_Enhancement.md)
# - [EGOS Global Rules](../.windsurfrules) (Section 3.6 - ATRiAN)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import logging
import yaml
import os
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from datetime import datetime

from atrian_ethical_compass import EthicalCompass
from atrian_trust_weaver import WeaverOfTrust, TrustDimension
from atrian_ethics_trust_integration import EthicsTrustIntegration, EthicsTrustEvent

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Constants
DEFAULT_GUIDE_CONFIG_PATH = "./silent_guide_config.yaml"
MAX_GUIDANCE_HISTORY = 100
PRIVACY_KEYWORDS = ["personal", "private", "sensitive", "confidential", "user data", "password"]
SECURITY_KEYWORDS = ["authentication", "authorization", "access control", "encryption", "credential"]

class GuidanceType(Enum):
    """Types of guidance that can be provided by the Silent Guide."""
    SUGGESTION = "suggestion"
    WARNING = "warning"
    ALERT = "alert"
    INSIGHT = "insight"
    RECOMMENDATION = "recommendation"
    EDUCATIONAL = "educational"
    ETHICAL_CONSIDERATION = "ethical_consideration"

class GuidanceContext(Enum):
    """Context types in which guidance can be provided."""
    CODE_EDITING = "code_editing"
    DATA_HANDLING = "data_handling"
    SYSTEM_OPERATION = "system_operation"
    USER_INTERACTION = "user_interaction"
    SECURITY_OPERATION = "security_operation"
    DEPLOYMENT = "deployment"
    GENERAL = "general"

class SilentGuide:
    """
    Provides contextual guidance based on ethics and trust assessments.
    
    The Silent Guide embodies the "guiding hand" of ATRiAN, offering subtle
    and contextually appropriate guidance that respects user autonomy while
    promoting system integrity and ethical behavior.
    """
    
    def __init__(self, 
                 ethics_trust_integration: Optional[EthicsTrustIntegration] = None,
                 config_filepath: str = DEFAULT_GUIDE_CONFIG_PATH):
        """
        Initialize the Silent Guide component.
        
        Args:
            ethics_trust_integration: An initialized EthicsTrustIntegration instance
            config_filepath: Path to the Silent Guide configuration file
        """
        # Initialize components
        if ethics_trust_integration:
            self.ethics_trust_integration = ethics_trust_integration
        else:
            ethical_compass = EthicalCompass()
            trust_weaver = WeaverOfTrust()
            self.ethics_trust_integration = EthicsTrustIntegration(ethical_compass, trust_weaver)
        
        self.config_filepath = config_filepath
        self.config = {}
        self.guidance_history = []
        self.guidance_templates = {}
        self.guidance_rules = []
        self.active_contexts = {}
        
        # Load configuration
        self._load_config()
        
        logger.info("SilentGuide initialized with EthicsTrustIntegration")
    
    def _load_config(self) -> None:
        """Load the Silent Guide configuration from YAML."""
        if os.path.exists(self.config_filepath):
            try:
                with open(self.config_filepath, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        self.config = config
                        self.guidance_templates = config.get('guidance_templates', {})
                        self.guidance_rules = config.get('guidance_rules', [])
                        logger.info(f"Loaded SilentGuide configuration from '{self.config_filepath}'")
                    else:
                        logger.warning(f"Guide config file '{self.config_filepath}' is empty or malformed")
            except Exception as e:
                logger.error(f"Error loading guide config file '{self.config_filepath}': {e}")
        else:
            logger.info(f"No guide config file found at '{self.config_filepath}', using defaults")
            self._initialize_default_config()
    
    def _initialize_default_config(self) -> None:
        """Initialize default configuration when no config file is found."""
        self.guidance_templates = {
            "privacy_warning": "Consider privacy implications when {action}. {principle_reference}",
            "security_recommendation": "Enhanced security practices recommended for {context}.",
            "ethical_consideration": "This action has ethical implications related to {principles}.",
            "trust_based_insight": "Based on trust assessment, consider {recommendation}.",
            "educational_note": "Did you know? {fact} This relates to {principle}.",
            "code_suggestion": "Consider {suggestion} when implementing {feature}.",
            "data_handling": "When processing {data_type}, ensure {requirement}."
        }
        
        self.guidance_rules = [
            {
                "context": "code_editing",
                "keywords": ["user data", "personal information"],
                "guidance_type": "privacy_warning",
                "trust_threshold": 0.0,  # Applies to all trust levels
                "template_vars": {
                    "action": "processing user data",
                    "principle_reference": "This aligns with Sacred Privacy (SP)."
                }
            },
            {
                "context": "data_handling",
                "keywords": ["storage", "database", "save"],
                "guidance_type": "data_handling",
                "trust_threshold": 0.0,
                "template_vars": {
                    "data_type": "sensitive information",
                    "requirement": "proper encryption and access controls"
                }
            },
            {
                "context": "security_operation",
                "keywords": ["authentication", "login", "credential"],
                "guidance_type": "security_recommendation",
                "trust_threshold": 0.0,
                "template_vars": {
                    "context": "authentication systems"
                }
            }
        ]
    
    def provide_guidance(self, 
                         context: Dict[str, Any], 
                         user_id: str = "User", 
                         context_type: Union[str, GuidanceContext] = GuidanceContext.GENERAL) -> Dict[str, Any]:
        """
        Provide contextual guidance based on context and user.
        
        Args:
            context: Contextual information relevant to the guidance
            user_id: Identifier for the user or agent requesting guidance
            context_type: The type of context in which guidance is requested
            
        Returns:
            A dictionary containing the guidance details
        """
        # Convert string context_type to enum if needed
        if isinstance(context_type, str):
            try:
                context_type = GuidanceContext(context_type)
            except ValueError:
                context_type = GuidanceContext.GENERAL
                logger.warning(f"Unrecognized context_type '{context_type}', defaulting to GENERAL")
        
        # Update active contexts for this user
        self._update_active_context(user_id, context_type, context)
        
        # Get trust assessment
        trust_score = self.ethics_trust_integration.trust_weaver.get_trust_score(user_id)
        dimensional_trust = self.ethics_trust_integration.trust_weaver.get_dimensional_trust_scores(user_id)
        
        # Generate action description for ethical evaluation
        action_description = self._generate_action_description(context, context_type)
        
        # Get ethics assessment
        ethics_eval = self.ethics_trust_integration.ethical_compass.evaluate_action(
            action_description, {"context": context, "user_id": user_id}
        )
        
        # Determine what guidance to provide based on context, trust, and ethics
        guidance_content, guidance_type = self._determine_guidance(
            context, context_type, trust_score, dimensional_trust, ethics_eval
        )
        
        # Create guidance object
        guidance = {
            "id": f"guidance_{len(self.guidance_history) + 1}",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "context_type": context_type.value,
            "guidance_type": guidance_type.value if isinstance(guidance_type, GuidanceType) else str(guidance_type),
            "content": guidance_content,
            "trust_assessment": {
                "overall_score": trust_score,
                "key_dimensions": {
                    "integrity": dimensional_trust.get(TrustDimension.INTEGRITY, 0.5),
                    "transparency": dimensional_trust.get(TrustDimension.TRANSPARENCY, 0.5),
                    "security": dimensional_trust.get(TrustDimension.SECURITY, 0.5)
                }
            },
            "ethical_assessment": {
                "allowed": ethics_eval.get("allowed", True),
                "relevant_rules": ethics_eval.get("relevant_rules", []),
                "warnings": ethics_eval.get("warnings", [])
            }
        }
        
        # Record guidance in history
        self._add_to_guidance_history(guidance)
        
        # Log the guidance provision
        logger.info(f"Provided {guidance_type} guidance to {user_id} in {context_type.value} context")
        
        return guidance
    
    def _generate_action_description(self, context: Dict[str, Any], context_type: GuidanceContext) -> str:
        """Generate an action description based on context for ethical evaluation."""
        if context_type == GuidanceContext.CODE_EDITING:
            file_path = context.get("file_path", "unknown file")
            language = context.get("language", "code")
            return f"Editing {language} in {file_path}"
        
        elif context_type == GuidanceContext.DATA_HANDLING:
            data_type = context.get("data_type", "data")
            operation = context.get("operation", "processing")
            return f"{operation} {data_type}"
        
        elif context_type == GuidanceContext.SYSTEM_OPERATION:
            operation = context.get("operation", "system task")
            return f"Performing system operation: {operation}"
        
        elif context_type == GuidanceContext.USER_INTERACTION:
            interaction = context.get("interaction_type", "interaction")
            return f"User interaction: {interaction}"
        
        elif context_type == GuidanceContext.SECURITY_OPERATION:
            operation = context.get("operation", "security task")
            return f"Security operation: {operation}"
        
        elif context_type == GuidanceContext.DEPLOYMENT:
            component = context.get("component", "system")
            environment = context.get("environment", "production")
            return f"Deploying {component} to {environment}"
            
        else:  # GENERAL or unrecognized
            return f"General operation in context: {json.dumps(context)[:100]}"
    
    def _determine_guidance(self, 
                           context: Dict[str, Any],
                           context_type: GuidanceContext,
                           trust_score: float,
                           dimensional_trust: Dict[TrustDimension, float],
                           ethics_eval: Dict[str, Any]) -> Tuple[str, GuidanceType]:
        """
        Determine what guidance to provide based on context, trust, and ethics.
        
        Returns:
            Tuple of (guidance_content, guidance_type)
        """
        # Check for matching guidance rules
        for rule in self.guidance_rules:
            # Skip if context doesn't match
            if rule.get("context") != context_type.value:
                continue
                
            # Skip if trust threshold isn't met
            if trust_score < rule.get("trust_threshold", 0.0):
                continue
                
            # Check for keyword matches
            keywords = rule.get("keywords", [])
            context_str = json.dumps(context).lower()
            
            if any(keyword.lower() in context_str for keyword in keywords):
                # Found a matching rule
                template_name = rule.get("guidance_type")
                template = self.guidance_templates.get(template_name, "Guidance: {context}")
                template_vars = rule.get("template_vars", {})
                template_vars["context"] = context_type.value
                
                # Format the template with variables
                try:
                    guidance_content = template.format(**template_vars)
                    return guidance_content, GuidanceType(rule.get("guidance_type_enum", "suggestion"))
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error formatting guidance template: {e}")
        
        # If no rule matched, provide default guidance based on context
        if context_type == GuidanceContext.CODE_EDITING:
            # Look for privacy concerns in code
            code = context.get("current_code", "")
            if any(keyword in code.lower() for keyword in PRIVACY_KEYWORDS):
                return "Consider privacy implications in this code. Ensure proper data handling and consent.", GuidanceType.ETHICAL_CONSIDERATION
            
            # Look for security concerns
            if any(keyword in code.lower() for keyword in SECURITY_KEYWORDS):
                return "Security-sensitive code detected. Consider additional validation and protection measures.", GuidanceType.RECOMMENDATION
            
            # Default code guidance
            return "Continue developing with EGOS principles in mind.", GuidanceType.SUGGESTION
        
        elif context_type == GuidanceContext.DATA_HANDLING:
            sensitivity = context.get("sensitivity", "unknown")
            if sensitivity == "high":
                return "This involves highly sensitive data. Ensure strict privacy controls and minimal access.", GuidanceType.WARNING
            return "Follow data minimization principles and ensure proper consent for data processing.", GuidanceType.RECOMMENDATION
        
        elif context_type == GuidanceContext.SECURITY_OPERATION:
            return "Verify all security operations adhere to best practices and EGOS security standards.", GuidanceType.ALERT
        
        # Default general guidance
        if trust_score < 0.3:
            return "Proceed with caution. Additional verification recommended.", GuidanceType.WARNING
        elif trust_score > 0.8:
            return "Trusted context. Standard protocols sufficient.", GuidanceType.INSIGHT
        else:
            return "Follow standard EGOS protocols for this operation.", GuidanceType.SUGGESTION
    
    def _update_active_context(self, user_id: str, context_type: GuidanceContext, context: Dict[str, Any]) -> None:
        """Update the active context for a user."""
        if user_id not in self.active_contexts:
            self.active_contexts[user_id] = {}
        
        self.active_contexts[user_id][context_type.value] = {
            "context": context,
            "last_updated": datetime.now().isoformat()
        }
    
    def _add_to_guidance_history(self, guidance: Dict[str, Any]) -> None:
        """Add guidance to history and maintain size limit."""
        self.guidance_history.append(guidance)
        
        # Trim history if it exceeds maximum size
        if len(self.guidance_history) > MAX_GUIDANCE_HISTORY:
            self.guidance_history = self.guidance_history[-MAX_GUIDANCE_HISTORY:]
    
    def get_guidance_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent guidance from history.
        
        Args:
            limit: Maximum number of guidance entries to return
            
        Returns:
            A list of guidance entries
        """
        return self.guidance_history[-limit:]
    
    def get_user_guidance_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get guidance history for a specific user.
        
        Args:
            user_id: The user ID to get history for
            limit: Maximum number of guidance entries to return
            
        Returns:
            A list of guidance entries for the specified user
        """
        user_guidance = [g for g in self.guidance_history if g["user_id"] == user_id]
        return user_guidance[-limit:]
    
    def get_active_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get the active contexts for a user.
        
        Args:
            user_id: The user ID to get active contexts for
            
        Returns:
            A dictionary of active contexts for the user
        """
        return self.active_contexts.get(user_id, {})
    
    def register_guidance_template(self, template_name: str, template: str) -> None:
        """
        Register a new guidance template.
        
        Args:
            template_name: Name for the template
            template: The template string with format placeholders
        """
        self.guidance_templates[template_name] = template
        logger.info(f"Registered new guidance template: {template_name}")
    
    def add_guidance_rule(self, rule: Dict[str, Any]) -> None:
        """
        Add a new guidance rule.
        
        Args:
            rule: The rule definition as a dictionary
        """
        if "context" in rule and "keywords" in rule and "guidance_type" in rule:
            self.guidance_rules.append(rule)
            logger.info(f"Added new guidance rule for context: {rule['context']}")
        else:
            logger.error("Cannot add guidance rule: missing required fields (context, keywords, guidance_type)")
    
    def generate_adaptive_interface(self, user_id: str) -> Dict[str, Any]:
        """
        Generate adaptive interface recommendations based on trust level.
        
        This method suggests UI adaptations based on the user's trust level.
        Higher trust might mean simplified interfaces, while lower trust
        could suggest more validation steps and detailed explanations.
        
        Args:
            user_id: The user ID to generate interface recommendations for
            
        Returns:
            A dictionary of interface recommendations
        """
        # Get trust score and key dimensions
        trust_score = self.ethics_trust_integration.trust_weaver.get_trust_score(user_id)
        dimensional_trust = self.ethics_trust_integration.trust_weaver.get_dimensional_trust_scores(user_id)
        
        # Base recommendations on trust level
        if trust_score < 0.3:
            # Low trust recommendations
            return {
                "trust_level": "low",
                "validation_level": "high",
                "explanation_detail": "detailed",
                "interface_elements": {
                    "show_explanation_panels": True,
                    "require_confirmations": True,
                    "show_trust_indicators": True,
                    "simplify_options": False
                },
                "messaging_tone": "formal",
                "recommendation": "Provide detailed explanations and multiple confirmation steps for this user."
            }
        elif trust_score < 0.7:
            # Medium trust recommendations
            return {
                "trust_level": "medium",
                "validation_level": "standard",
                "explanation_detail": "moderate",
                "interface_elements": {
                    "show_explanation_panels": True,
                    "require_confirmations": False,
                    "show_trust_indicators": True,
                    "simplify_options": False
                },
                "messaging_tone": "balanced",
                "recommendation": "Provide standard validation and moderate explanations for this user."
            }
        else:
            # High trust recommendations
            return {
                "trust_level": "high",
                "validation_level": "minimal",
                "explanation_detail": "concise",
                "interface_elements": {
                    "show_explanation_panels": False,
                    "require_confirmations": False,
                    "show_trust_indicators": False,
                    "simplify_options": True
                },
                "messaging_tone": "friendly",
                "recommendation": "Provide streamlined experience with minimal friction for this trusted user."
            }


# Example usage
if __name__ == "__main__":
    print("=== ATRiAN Silent Guide Example ===")
    
    # Initialize components
    ethical_compass = EthicalCompass()
    trust_weaver = WeaverOfTrust()
    ethics_trust = EthicsTrustIntegration(ethical_compass, trust_weaver)
    silent_guide = SilentGuide(ethics_trust)
    
    # Example 1: Code editing guidance
    code_context = {
        "file_path": "/example/user_data.py",
        "current_code": "def save_user_data(user_id, personal_info):\n    database.store(user_id, personal_info)",
        "language": "python",
        "user_intent": "storing user data"
    }
    
    guidance = silent_guide.provide_guidance(code_context, "ExampleUser", GuidanceContext.CODE_EDITING)
    print(f"\nGuidance for Code Editing:")
    print(f"Type: {guidance['guidance_type']}")
    print(f"Content: {guidance['content']}")
    
    # Example 2: Adaptive interface
    interface_rec = silent_guide.generate_adaptive_interface("ExampleUser")
    print(f"\nAdaptive Interface Recommendations:")
    print(f"Trust Level: {interface_rec['trust_level']}")
    print(f"Recommendation: {interface_rec['recommendation']}")
    
    print("\n=== Silent Guide Demo Complete ===")