# @references:
#   - ATRIAN/atrian_ethical_compass.py
# 
# EGOS System - ATRiAN Module: Ethical Compass
# Version: 0.2 (EaaS Integration)
# Last Modified: {{ CURRENT_DATE_TIME_ISO }} # This will be set by the system or manually updated
#
# Purpose:
# This module provides the EthicalCompass class, responsible for providing ethical
# guidance based on predefined ethics_rules.yaml, MQP principles, and EaaS concepts.
# It is a core component of the ATRiAN subsystem, detailed in
# ATRiAN_Implementation_Plan.md Section 4.1. Now adapted for EaaS API integration.
#
# Key Functionalities (Planned & Implemented):
# - Load and interpret rules from ethics_rules.yaml (existing).
# - Evaluate actions using EaaS Pydantic models (EthicsEvaluationRequestContext, EthicsEvaluationOptions).
# - Return structured ethical evaluations (EthicsEvaluationResult).
# - Provide actionable ethical advice or warnings through EthicalConcern and EthicalRecommendation models.
# - Integrate with EaaS frameworks and principles.
#
# MQP Alignment:
# - Integrated Ethics (IE/ETHIK): Central to its function.
# - Universal Redemption (UR), Compassionate Temporality (CT), Sacred Privacy (SP),
#   Unconditional Love (UL), Reciprocal Trust (RT): These principles inform the
#   ethical rules and guidance provided.
#
# Cross-references:
# - [ATRiAN Ethics Rules Configuration](./ethics_rules.yaml)
# - [ATRiAN EaaS Models](./eaas_models.py)
# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md) (Sections 3.2.2, 4.1)
# - [ATRiAN README](./README.md)
# - [EGOS Global Rules](../.windsurfrules) (Section 3.6 - ATRiAN)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import logging
import yaml # For loading ethics_rules.yaml
from typing import Dict, List, Any, Optional

from eaas_models import (
    EthicsEvaluationRequestContext,
    EthicsEvaluationOptions,
    EthicalConcern,
    EthicalRecommendation,
    EthicsEvaluationResult
)

# Configure basic logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class EthicalCompass:
    """
    Provides ethical guidance based on a defined set of rules and principles.

    The Ethical Compass is responsible for interpreting ethical rules (typically from
    ethics_rules.yaml) and MQP principles to offer guidance on actions, decisions,
    or information handling within the EGOS system. It embodies the concept of
    'Ethics as a Service' (EaaS) by providing structured ethical evaluations.
    """
    def __init__(self, rules_filepath: Optional[str] = "C:/EGOS/ATRiAN/ethics_rules.yaml"):
        """
        Initializes the EthicalCompass.

        Args:
            rules_filepath (Optional[str]): Path to the YAML file containing ethical rules.
                                            Defaults to 'C:/EGOS/ATRiAN/ethics_rules.yaml'.
        """
        self.rules: List[Dict[str, Any]] = []
        self.rules_filepath: Optional[str] = rules_filepath
        self.mqp_principles: Dict[str, str] = {
            "UR": "Universal Redemption",
            "CT": "Compassionate Temporality",
            "SP": "Sacred Privacy",
            "UA": "Universal Accessibility",
            "UL": "Unconditional Love",
            "RT": "Reciprocal Trust",
            "IE": "Integrated Ethics (ETHIK)",
            "CM": "Conscious Modularity",
            "SC": "Systemic Cartography",
            "EP": "Evolutionary Preservation"
        }
        if rules_filepath:
            self.load_rules(rules_filepath)
        else:
            logger.warning("No rules file path provided. EthicalCompass initialized with no rules.")

    def load_rules(self, filepath: str) -> None:
        """
        Loads ethical rules from a YAML file.

        Args:
            filepath (str): The path to the YAML file.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.rules = data.get('ethics', [])
            logger.info(f"Successfully loaded {len(self.rules)} rules from {filepath}")
            # Store the filepath for reference
            self.rules_filepath = filepath
        except FileNotFoundError:
            logger.error(f"Ethical rules file not found: {filepath}. Proceeding with no rules loaded.")
            self.rules = []
        except yaml.YAMLError as e:
            logger.error(f"Error parsing ethical rules file {filepath}: {e}. Proceeding with no rules loaded.")
            self.rules = []
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading rules from {filepath}: {e}. Proceeding with no rules loaded.")
            self.rules = []

    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific rule by its ID.

        Args:
            rule_id (str): The ID of the rule to find.

        Returns:
            Optional[Dict[str, Any]]: The rule if found, otherwise None.
        """
        for rule in self.rules:
            if rule.get('id') == rule_id:
                return rule
        return None

    def evaluate_action(
        self,
        action_description: str,
        context: EthicsEvaluationRequestContext,
        options: Optional[EthicsEvaluationOptions] = None
    ) -> EthicsEvaluationResult:
        """
        Evaluates a given action against the loaded ethical rules and MQP principles.
        This version is adapted for EaaS and returns an EthicsEvaluationResult.

        Args:
            action_description (str): A description of the action to be evaluated.
            context (EthicsEvaluationRequestContext): Contextual information surrounding the action.
            options (Optional[EthicsEvaluationOptions]): Options for the evaluation process.

        Returns:
            EthicsEvaluationResult: The result of the ethical evaluation.
        """
        logger.info(f"Evaluating EaaS action: '{action_description}' with context: {context}, options: {options}")
        
        concerns: List[EthicalConcern] = []
        recommendations: List[EthicalRecommendation] = []
        compliant = True
        ethical_score = 0.9  # Default high score, can be adjusted by rules/logic

        # Mock logic adapted from original eaas_api.py stub for consistency
        if context.data_sources and any("sensitive_data" in (ds.lower() if ds else '') for ds in context.data_sources):
            concerns.append(
                EthicalConcern(
                    principle="data_privacy_SP", # Align with MQP
                    severity="high",
                    description="Action involves sensitive data. Ensure robust anonymization, consent mechanisms, and alignment with Sacred Privacy (SP)."
                )
            )
            recommendations.append(
                EthicalRecommendation(
                    action="Review and enhance data handling protocols for sensitive data, prioritizing Sacred Privacy (SP).",
                    priority="high",
                    rationale="Mitigate risks associated with sensitive data exposure and uphold SP."
                )
            )
            compliant = False
            ethical_score = 0.6

        if context.domain and context.domain.lower() == "surveillance":
            concerns.append(
                EthicalConcern(
                    principle="autonomy_and_oversight_IE_UR", # Align with MQP
                    severity="critical",
                    description="Surveillance applications require stringent human oversight, justification, and pathways for Universal Redemption (UR)."
                )
            )
            recommendations.append(
                EthicalRecommendation(
                    action="Implement a multi-level human review process for all surveillance outputs. Ensure transparency and clear justification.",
                    priority="critical",
                    rationale="Uphold individual autonomy, prevent misuse, and align with Integrated Ethics (IE) and Universal Redemption (UR)."
                )
            )
            compliant = False
            ethical_score = 0.4
        
        # Rule-based evaluation (integrates with loaded self.rules from YAML)
        action_lower = action_description.lower()
        for rule in self.rules:
            rule_text_lower = rule.get('rule', '').lower()
            keywords = rule.get('keywords', [])
            triggered_by_keyword = any(keyword.lower() in action_lower for keyword in keywords)
            triggered_by_rule_text = rule_text_lower and rule_text_lower in action_lower
            
            triggered_by_scope = False
            if context and rule.get('scope'):
                rule_scope_lower = rule.get('scope').lower()
                if context.domain and rule_scope_lower in context.domain.lower():
                    triggered_by_scope = True
                elif context.purpose and rule_scope_lower in context.purpose.lower():
                     triggered_by_scope = True

            if triggered_by_keyword or triggered_by_rule_text or triggered_by_scope:
                concerns.append(
                    EthicalConcern(
                        principle=rule.get('principle', 'Undefined Principle'),
                        severity=rule.get('severity', 'medium'), 
                        description=f"Action potentially conflicts with rule '{rule.get('id', 'N/A')}': {rule.get('rule')}"
                    )
                )
                if rule.get('disallow_if_triggered', False):
                    compliant = False
                    ethical_score = min(ethical_score, 0.3) 
                
                recommendations.append(
                    EthicalRecommendation(
                        action=f"Review adherence to rule '{rule.get('id', 'N/A')}' ({rule.get('principle', 'N/A')}). Specific guidance: {rule.get('guidance', 'Consult rule documentation.')}",
                        priority=rule.get('severity', 'medium'),
                        rationale=f"Ensure compliance with defined ethical standard: {rule.get('rule')}"
                    )
                )

        if compliant and not concerns:
            recommendations.append(
                EthicalRecommendation(
                    action="Proceed with continuous ethical monitoring and adherence to MQP.",
                    priority="low",
                    rationale="Maintain ethical standards throughout the lifecycle, guided by MQP principles."
                )
            )
        elif not compliant and not recommendations and not concerns: # Only add this if no other rec/concerns exist for non-compliance
             recommendations.append(
                EthicalRecommendation(
                    action="Action deemed non-compliant. Cease and re-evaluate based on concerns.",
                    priority="critical",
                    rationale="Immediate re-evaluation required to address ethical violations."
                )
            )

        return EthicsEvaluationResult(
            ethical_score=round(ethical_score, 2),
            compliant=compliant,
            concerns=concerns,
            recommendations=recommendations
        )

# Example Usage (for testing or direct script execution)
if __name__ == "__main__":
    print("--- EthicalCompass Example Usage (EaaS Integrated) --- ")
    
    # Define the path to the dummy rules file within the ATRiAN directory
    # This ensures it's co-located with the script for easier testing
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dummy_rules_file = os.path.join(current_dir, "ethics_rules_dummy.yaml")

    try:
        with open(dummy_rules_file, 'w', encoding='utf-8') as f:
            yaml.dump({
                'ethics': [
                    {'id': 'ER-SP-001', 'principle': 'Sacred Privacy (SP)', 'rule': 'Protect PII rigorously. Minimize collection, ensure consent, and provide transparency.', 'scope': 'data_handling', 'keywords': ['pii', 'personal data', 'user data'], 'severity': 'high', 'disallow_if_triggered': True, 'guidance': 'Implement strong encryption, access controls, and data retention policies.'},
                    {'id': 'ER-IE-001', 'principle': 'Integrated Ethics (IE)', 'rule': 'Ensure all actions are demonstrably ethically sound and align with MQP.', 'scope': 'general_operation', 'severity': 'medium', 'guidance': 'Conduct ethical impact assessments for new features.'},
                    {'id': 'ER-DM-001', 'principle': 'Data Minimization (IE)', 'rule': 'Only collect, process, and retain data absolutely essential for the specified purpose.', 'scope': 'data_handling', 'keywords': ['collect data', 'store data', 'retain data'], 'severity': 'medium', 'guidance': 'Regularly audit data holdings and purge unnecessary data.'},
                    {'id': 'ER-AI-BIAS-001', 'principle': 'Fairness & Non-Discrimination (UA, UR)', 'rule': 'Actively identify and mitigate biases in AI models and data.', 'scope': 'ai_development', 'keywords': ['ai model', 'algorithm', 'bias'], 'severity': 'high', 'guidance': 'Use diverse datasets, fairness metrics, and bias detection tools.'}
                ]
            }, f)
        compass = EthicalCompass(rules_filepath=dummy_rules_file)
    except Exception as e:
        print(f"Could not create or load dummy rules for testing: {e}")
        # Fallback to initializing without a rules file if dummy creation fails
        compass = EthicalCompass(rules_filepath=None) 

    print(f"Loaded {len(compass.rules)} rules.")
    if compass.rules:
        print(f"First rule: {compass.rules[0]['id']}: {compass.rules[0]['rule']}")

    # Test evaluation using EaaS models
    test_request_context_finance = EthicsEvaluationRequestContext(
        domain="finance",
        data_sources=["user_pii_data", "transaction_history", "sensitive_data_user_credit_score"],
        purpose="To assess creditworthiness for a loan application using an AI model.",
        stakeholders=["applicant", "lender", "regulatory_body"]
    )
    test_options = EthicsEvaluationOptions(detail_level="comprehensive", include_alternatives=True)

    evaluation1 = compass.evaluate_action(
        action_description="Collect PII and credit score for AI-driven loan application processing.",
        context=test_request_context_finance,
        options=test_options
    )
    print(f"\nEvaluation for 'AI Loan Application Processing':")
    print(f"  Compliant: {evaluation1.compliant}")
    print(f"  Ethical Score: {evaluation1.ethical_score}")
    print(f"  Concerns ({len(evaluation1.concerns)}):")
    for concern in evaluation1.concerns:
        print(f"    - [{concern.severity.upper()}] {concern.principle}: {concern.description}")
    print(f"  Recommendations ({len(evaluation1.recommendations)}):")
    for rec in evaluation1.recommendations:
        print(f"    - [{rec.priority.upper()}] {rec.action} (Rationale: {rec.rationale})")

    test_request_context_surveillance = EthicsEvaluationRequestContext(
        domain="public_safety_surveillance", 
        data_sources=["public_camera_feeds", "facial_recognition_database"],
        purpose="To monitor public spaces for security threats using AI-powered facial recognition."
    )
    evaluation2 = compass.evaluate_action(
        action_description="Deploy AI facial recognition for public surveillance.",
        context=test_request_context_surveillance
        # options not provided, will use default
    )
    print(f"\nEvaluation for 'AI Public Surveillance':")
    print(f"  Compliant: {evaluation2.compliant}")
    print(f"  Ethical Score: {evaluation2.ethical_score}")
    print(f"  Concerns ({len(evaluation2.concerns)}):")
    for concern in evaluation2.concerns:
        print(f"    - [{concern.severity.upper()}] {concern.principle}: {concern.description}")
    print(f"  Recommendations ({len(evaluation2.recommendations)}):")
    for rec in evaluation2.recommendations:
        print(f"    - [{rec.priority.upper()}] {rec.action} (Rationale: {rec.rationale})")

    # Test with no rules loaded explicitly
    print("\n--- Testing with no rules file ---")
    compass_no_rules = EthicalCompass(rules_filepath=None)
    evaluation_no_rules = compass_no_rules.evaluate_action(
        action_description="Generic action with no specific rule triggers.",
        context=EthicsEvaluationRequestContext(domain="general", purpose="testing")
    )
    print(f"Evaluation for 'Generic action':")
    print(f"  Compliant: {evaluation_no_rules.compliant}")
    print(f"  Ethical Score: {evaluation_no_rules.ethical_score}")
    print(f"  Concerns: {len(evaluation_no_rules.concerns)}")
    print(f"  Recommendations: {len(evaluation_no_rules.recommendations)}")

    print("--- EthicalCompass Example Usage Complete ---")