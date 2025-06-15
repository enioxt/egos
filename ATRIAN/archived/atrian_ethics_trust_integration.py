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
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

from atrian_ethical_compass import EthicalCompass
from atrian_trust_weaver import WeaverOfTrust, TrustDimension

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Constants
DEFAULT_INTEGRATION_CONFIG_PATH = "./ethics_trust_integration.yaml"
DEFAULT_ETHICS_WEIGHT = 0.3  # Weight given to ethical considerations in trust adjustments
DEFAULT_TRUST_WEIGHT = 0.4   # Weight given to trust scores in ethical evaluations
ETHICS_VIOLATION_PENALTY = 0.15  # Trust penalty for ethical violations
ETHICS_ALIGNMENT_BONUS = 0.05    # Trust bonus for ethical alignment

class EthicsTrustEvent(Enum):
    """Types of events that can occur in the ethics-trust integration system."""
    ETHICAL_VIOLATION = "ethical_violation"
    ETHICAL_ALIGNMENT = "ethical_alignment"
    TRUST_BOUNDARY_CROSSED = "trust_boundary_crossed"
    PRIVACY_RESPECT = "privacy_respect"
    PRIVACY_VIOLATION = "privacy_violation"
    TRANSPARENCY_ALIGNMENT = "transparency_alignment"
    TRANSPARENCY_VIOLATION = "transparency_violation"
    INTEGRITY_ENHANCEMENT = "integrity_enhancement"
    INTEGRITY_COMPROMISE = "integrity_compromise"

class EthicsTrustIntegration:
    """
    Integrates the EthicalCompass and WeaverOfTrust components of ATRiAN.
    
    This class provides bidirectional communication between the ethics and trust
    systems, enabling ethics-informed trust adjustments and trust-aware ethical
    recommendations.
    """
    
    def __init__(self, 
                 ethical_compass: Optional[EthicalCompass] = None, 
                 trust_weaver: Optional[WeaverOfTrust] = None,
                 config_filepath: str = DEFAULT_INTEGRATION_CONFIG_PATH):
        """
        Initialize the EthicsTrustIntegration component.
        
        Args:
            ethical_compass: An initialized EthicalCompass instance
            trust_weaver: An initialized WeaverOfTrust instance
            config_filepath: Path to the integration configuration file
        """
        self.ethical_compass = ethical_compass or EthicalCompass()
        self.trust_weaver = trust_weaver or WeaverOfTrust()
        self.config_filepath = config_filepath
        self.integration_config = {}
        self.ethics_weight = DEFAULT_ETHICS_WEIGHT
        self.trust_weight = DEFAULT_TRUST_WEIGHT
        self.event_log = []
        
        # Load configuration if available
        self._load_config()
        
        logger.info("EthicsTrustIntegration initialized with EthicalCompass and WeaverOfTrust components")
    
    def _load_config(self) -> None:
        """Load the ethics-trust integration configuration from YAML."""
        if os.path.exists(self.config_filepath):
            try:
                with open(self.config_filepath, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and isinstance(config, dict):
                        self.integration_config = config
                        self.ethics_weight = config.get('ethics_weight', DEFAULT_ETHICS_WEIGHT)
                        self.trust_weight = config.get('trust_weight', DEFAULT_TRUST_WEIGHT)
                        logger.info(f"Loaded EthicsTrustIntegration configuration from '{self.config_filepath}'")
                    else:
                        logger.warning(f"Integration config file '{self.config_filepath}' is empty or malformed")
            except Exception as e:
                logger.error(f"Error loading integration config file '{self.config_filepath}': {e}")
        else:
            logger.info(f"No integration config file found at '{self.config_filepath}', using defaults")
    
    def evaluate_action_with_trust(self, 
                                   agent_id: str, 
                                   action_description: str, 
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate an action considering both ethical rules and trust scores.
        
        Args:
            agent_id: The ID of the agent performing the action
            action_description: Description of the action to evaluate
            context: Additional context for the evaluation
            
        Returns:
            A dictionary containing the composite evaluation results
        """
        context = context or {}
        
        # Get current trust score for the agent
        trust_score = self.trust_weaver.get_trust_score(agent_id)
        dimensional_trust = self.trust_weaver.get_dimensional_trust_scores(agent_id)
        
        # Add trust information to the context for ethical evaluation
        trust_context = context.copy()
        trust_context.update({
            "agent_id": agent_id,
            "trust_score": trust_score,
            "dimensional_trust": dimensional_trust,
            "trust_history": self.trust_weaver.get_trust_events(agent_id, limit=5)
        })
        
        # Get ethical evaluation
        ethical_eval = self.ethical_compass.evaluate_action(action_description, trust_context)
        
        # Create composite evaluation
        composite_eval = {
            "agent_id": agent_id,
            "action": action_description,
            "timestamp": datetime.now().isoformat(),
            "ethical_evaluation": ethical_eval,
            "trust_assessment": {
                "overall_score": trust_score,
                "dimensional_scores": dimensional_trust,
                "trust_level": self._determine_trust_level(trust_score)
            },
            "composite_recommendation": self._generate_composite_recommendation(
                ethical_eval, trust_score, dimensional_trust
            ),
            "action_allowed": self._determine_if_action_allowed(
                ethical_eval, trust_score, dimensional_trust
            )
        }
        
        # Log the evaluation event
        self._log_evaluation_event(agent_id, action_description, composite_eval)
        
        return composite_eval
    
    def process_ethics_trust_event(self, 
                                   agent_id: str, 
                                   event_type: EthicsTrustEvent,
                                   details: str,
                                   magnitude: float = 0.1) -> Dict[str, Any]:
        """
        Process an event that has both ethical and trust implications.
        
        Args:
            agent_id: The ID of the agent involved in the event
            event_type: The type of ethics-trust event
            details: Details about the event
            magnitude: The magnitude of the event's impact (0.0 to 1.0)
            
        Returns:
            A dictionary containing the event processing results
        """
        # Map event types to appropriate trust dimensions and outcomes
        event_mapping = {
            EthicsTrustEvent.ETHICAL_VIOLATION: {
                "trust_outcome": "negative",
                "trust_dimension": TrustDimension.INTEGRITY,
                "trust_adjustment": -magnitude,
                "reason": f"Ethical violation: {details}"
            },
            EthicsTrustEvent.ETHICAL_ALIGNMENT: {
                "trust_outcome": "positive",
                "trust_dimension": TrustDimension.INTEGRITY,
                "trust_adjustment": magnitude,
                "reason": f"Ethical alignment: {details}"
            },
            EthicsTrustEvent.PRIVACY_RESPECT: {
                "trust_outcome": "positive",
                "trust_dimension": TrustDimension.BENEVOLENCE,
                "trust_adjustment": magnitude,
                "reason": f"Privacy respected: {details}"
            },
            EthicsTrustEvent.PRIVACY_VIOLATION: {
                "trust_outcome": "negative",
                "trust_dimension": TrustDimension.BENEVOLENCE,
                "trust_adjustment": -magnitude * 1.5,  # Higher penalty for privacy violations
                "reason": f"Privacy violation: {details}"
            },
            EthicsTrustEvent.TRANSPARENCY_ALIGNMENT: {
                "trust_outcome": "positive",
                "trust_dimension": TrustDimension.TRANSPARENCY,
                "trust_adjustment": magnitude,
                "reason": f"Transparency demonstrated: {details}"
            },
            EthicsTrustEvent.TRANSPARENCY_VIOLATION: {
                "trust_outcome": "negative",
                "trust_dimension": TrustDimension.TRANSPARENCY,
                "trust_adjustment": -magnitude,
                "reason": f"Lack of transparency: {details}"
            },
            EthicsTrustEvent.INTEGRITY_ENHANCEMENT: {
                "trust_outcome": "positive",
                "trust_dimension": TrustDimension.INTEGRITY,
                "trust_adjustment": magnitude,
                "reason": f"Integrity enhanced: {details}"
            },
            EthicsTrustEvent.INTEGRITY_COMPROMISE: {
                "trust_outcome": "negative",
                "trust_dimension": TrustDimension.INTEGRITY,
                "trust_adjustment": -magnitude * 1.2,  # Higher penalty for integrity issues
                "reason": f"Integrity compromised: {details}"
            },
            EthicsTrustEvent.TRUST_BOUNDARY_CROSSED: {
                "trust_outcome": "negative",
                "trust_dimension": TrustDimension.SECURITY,
                "trust_adjustment": -magnitude * 1.3,  # Higher penalty for boundary violations
                "reason": f"Trust boundary violation: {details}"
            }
        }
        
        # Get the mapping for this event type
        event_info = event_mapping.get(event_type, {
            "trust_outcome": "neutral",
            "trust_dimension": TrustDimension.RELIABILITY,
            "trust_adjustment": 0,
            "reason": f"Unclassified event: {details}"
        })
        
        # Update trust score based on the event
        original_score = self.trust_weaver.get_trust_score(agent_id)
        
        # If the event has a trust impact, update the trust score
        if abs(event_info["trust_adjustment"]) > 0.01:
            self.trust_weaver.update_trust_score(
                agent_id,
                str(event_type.value),
                event_info["trust_outcome"],
                abs(event_info["trust_adjustment"]),
                event_info["reason"]
            )
            
            # For dimensional trust, directly update the specific dimension
            self.trust_weaver.update_dimensional_trust(
                agent_id,
                event_info["trust_dimension"],
                event_info["trust_adjustment"]
            )
        
        new_score = self.trust_weaver.get_trust_score(agent_id)
        
        # Prepare event result
        event_result = {
            "agent_id": agent_id,
            "event_type": event_type.value,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "trust_impact": {
                "original_score": original_score,
                "new_score": new_score,
                "adjustment": new_score - original_score,
                "affected_dimension": event_info["trust_dimension"].value
            },
            "ethical_implications": self._get_ethical_implications(event_type, details)
        }
        
        # Log the event
        self._log_ethics_trust_event(agent_id, event_type, event_result)
        
        return event_result
    
    def _determine_trust_level(self, trust_score: float) -> str:
        """Determine the trust level description based on the trust score."""
        if trust_score >= 0.9:
            return "Highly Trusted"
        elif trust_score >= 0.75:
            return "Trusted"
        elif trust_score >= 0.5:
            return "Moderately Trusted"
        elif trust_score >= 0.25:
            return "Limited Trust"
        else:
            return "Minimal Trust"
    
    def _generate_composite_recommendation(self, 
                                          ethical_eval: Dict[str, Any],
                                          trust_score: float,
                                          dimensional_trust: Dict[TrustDimension, float]) -> str:
        """
        Generate a recommendation that considers both ethical and trust assessments.
        
        Args:
            ethical_eval: The ethical evaluation results
            trust_score: The overall trust score
            dimensional_trust: The dimensional trust scores
            
        Returns:
            A composite recommendation string
        """
        # Extract key information
        ethical_guidance = ethical_eval.get("guidance", "")
        ethical_warnings = ethical_eval.get("warnings", [])
        
        # Consider dimensional trust scores for specific recommendations
        integrity_score = dimensional_trust.get(TrustDimension.INTEGRITY, 0.5)
        transparency_score = dimensional_trust.get(TrustDimension.TRANSPARENCY, 0.5)
        
        # Base recommendation on combined factors
        if trust_score < 0.3:
            base_rec = "Exercise extreme caution. Verify all information and actions."
        elif trust_score < 0.6:
            base_rec = "Proceed with caution and additional verification."
        else:
            base_rec = "Proceed with standard verification protocols."
            
        # Add integrity considerations
        if integrity_score < 0.4:
            integrity_rec = "Integrity concerns detected. Consider additional validation."
        elif integrity_score > 0.8:
            integrity_rec = "High integrity demonstrated. Reduced validation acceptable."
        else:
            integrity_rec = ""
            
        # Add transparency considerations
        if transparency_score < 0.4:
            transparency_rec = "Low transparency. Request additional information before proceeding."
        elif transparency_score > 0.8:
            transparency_rec = "High transparency demonstrated. Clear communication established."
        else:
            transparency_rec = ""
        
        # Combine all recommendations
        components = [base_rec]
        if integrity_rec:
            components.append(integrity_rec)
        if transparency_rec:
            components.append(transparency_rec)
        if ethical_guidance:
            components.append(f"Ethical guidance: {ethical_guidance}")
        if ethical_warnings:
            components.append(f"Ethical considerations: {', '.join(ethical_warnings)}")
            
        return " ".join(components)
    
    def _determine_if_action_allowed(self,
                                   ethical_eval: Dict[str, Any],
                                   trust_score: float,
                                   dimensional_trust: Dict[TrustDimension, float]) -> bool:
        """
        Determine if an action should be allowed based on ethics and trust.
        
        Args:
            ethical_eval: The ethical evaluation results
            trust_score: The overall trust score
            dimensional_trust: The dimensional trust scores
            
        Returns:
            Boolean indicating if the action is allowed
        """
        # Extract ethical allowance
        ethical_allowed = ethical_eval.get("allowed", "indeterminate")
        
        # If ethics explicitly disallows, block regardless of trust
        if ethical_allowed is False:
            return False
        
        # If ethics is indeterminate, use trust thresholds
        if ethical_allowed == "indeterminate":
            # Check overall trust threshold
            if trust_score < 0.2:
                return False
            
            # Check critical dimensions
            integrity = dimensional_trust.get(TrustDimension.INTEGRITY, 0.5)
            security = dimensional_trust.get(TrustDimension.SECURITY, 0.5)
            
            # Block if critical dimensions are too low
            if integrity < 0.3 or security < 0.3:
                return False
        
        # Default to allowing if no specific blocks triggered
        return True
    
    def _get_ethical_implications(self, event_type: EthicsTrustEvent, details: str) -> List[str]:
        """
        Get ethical implications for a given event type.
        
        Args:
            event_type: The type of ethics-trust event
            details: Details about the event
            
        Returns:
            A list of ethical implications
        """
        # Map event types to relevant ethical principles
        ethics_mapping = {
            EthicsTrustEvent.ETHICAL_VIOLATION: ["Integrated Ethics", "Reciprocal Trust"],
            EthicsTrustEvent.ETHICAL_ALIGNMENT: ["Integrated Ethics", "Reciprocal Trust"],
            EthicsTrustEvent.PRIVACY_RESPECT: ["Sacred Privacy", "Reciprocal Trust"],
            EthicsTrustEvent.PRIVACY_VIOLATION: ["Sacred Privacy"],
            EthicsTrustEvent.TRANSPARENCY_ALIGNMENT: ["Transparency", "Reciprocal Trust"],
            EthicsTrustEvent.TRANSPARENCY_VIOLATION: ["Transparency"],
            EthicsTrustEvent.INTEGRITY_ENHANCEMENT: ["Integrity", "Reciprocal Trust"],
            EthicsTrustEvent.INTEGRITY_COMPROMISE: ["Integrity"],
            EthicsTrustEvent.TRUST_BOUNDARY_CROSSED: ["Security", "Reciprocal Trust"]
        }
        
        principles = ethics_mapping.get(event_type, ["General Ethical Considerations"])
        implications = [f"Implicates {principle} principle" for principle in principles]
        
        # Add standard EaaS implications
        implications.append("Subject to Ethics as a Service (EaaS) evaluation")
        
        return implications
    
    def _log_evaluation_event(self, agent_id: str, action: str, evaluation: Dict[str, Any]) -> None:
        """Log an evaluation event for record-keeping and analysis."""
        log_entry = {
            "type": "evaluation",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "result": {
                "ethical_allowed": evaluation["ethical_evaluation"].get("allowed", "indeterminate"),
                "composite_allowed": evaluation["action_allowed"],
                "trust_score": evaluation["trust_assessment"]["overall_score"]
            }
        }
        self.event_log.append(log_entry)
        logger.info(f"Logged evaluation event for agent '{agent_id}': {action}")
    
    def _log_ethics_trust_event(self, agent_id: str, event_type: EthicsTrustEvent, result: Dict[str, Any]) -> None:
        """Log an ethics-trust event for record-keeping and analysis."""
        log_entry = {
            "type": "ethics_trust_event",
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "event_type": event_type.value,
            "trust_impact": result["trust_impact"]["adjustment"]
        }
        self.event_log.append(log_entry)
        logger.info(f"Logged ethics-trust event for agent '{agent_id}': {event_type.value}")
    
    def get_event_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the most recent events from the event log.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            A list of event log entries
        """
        return self.event_log[-limit:]


# Example usage
if __name__ == "__main__":
    print("=== ATRiAN Ethics-Trust Integration Example ===")
    
    # Initialize components
    ethical_compass = EthicalCompass()
    trust_weaver = WeaverOfTrust()
    integration = EthicsTrustIntegration(ethical_compass, trust_weaver)
    
    # Example 1: Evaluate an action with trust
    agent_id = "TestAgent"
    action = "access_user_data"
    context = {"purpose": "system_maintenance", "data_type": "user_preferences"}
    
    result = integration.evaluate_action_with_trust(agent_id, action, context)
    print(f"\nAction Evaluation for '{agent_id}':")
    print(f"Action: {action}")
    print(f"Allowed: {result['action_allowed']}")
    print(f"Recommendation: {result['composite_recommendation']}")
    
    # Example 2: Process an ethics-trust event
    event_result = integration.process_ethics_trust_event(
        agent_id,
        EthicsTrustEvent.PRIVACY_RESPECT,
        "Implemented proper data minimization during user data access",
        0.08
    )
    print(f"\nEthics-Trust Event Processing:")
    print(f"Event Type: {event_result['event_type']}")
    print(f"Trust Impact: {event_result['trust_impact']['adjustment']:.3f}")
    print(f"Ethical Implications: {event_result['ethical_implications']}")
    
    print("\n=== Integration Complete ===")