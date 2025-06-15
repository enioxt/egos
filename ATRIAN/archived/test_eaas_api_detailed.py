"""
ATRiAN EaaS API Detailed Test Script

This script performs detailed testing of the EthicalCompass core logic
with various scenarios to validate the integration with the EaaS API.
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import sys
import os
import uuid
from datetime import datetime

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the models and EthicalCompass
from eaas_models import (
    EthicsEvaluationOptions, 
    EthicsEvaluationRequestContext,
    EthicsEvaluationRequest,
    EthicsEvaluationResult
)
from atrian_ethical_compass import EthicalCompass

# Create a separator function for better output formatting
def print_separator(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def print_evaluation_result(result, scenario_name):
    """Print the evaluation result in a well-formatted way."""
    print(f"\nEvaluation Result for '{scenario_name}':")
    print(f"  Ethical Score: {result.ethical_score}")
    print(f"  Compliant: {result.compliant}")
    
    if result.concerns:
        print("\nConcerns:")
        for i, concern in enumerate(result.concerns, 1):
            print(f"  {i}. [{concern.severity.upper()}] {concern.principle}: {concern.description}")
    else:
        print("\nNo ethical concerns identified.")
    
    if result.recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. [{rec.priority.upper()}] {rec.action}")
            print(f"     Rationale: {rec.rationale}")
    else:
        print("\nNo recommendations provided.")

def test_scenarios():
    """Run a series of test scenarios to validate the EthicalCompass."""
    # Initialize the EthicalCompass
    print_separator("INITIALIZING ETHICAL COMPASS")
    rules_filepath = "C:/EGOS/ATRiAN/ethics_rules.yaml"
    ethical_compass = EthicalCompass(rules_filepath=rules_filepath)
    print(f"EthicalCompass initialized with rules from: {rules_filepath}")
    print("Rules loaded successfully")
    
    
    # Scenario 1: Finance/PII scenario (should trigger privacy concerns)
    print_separator("SCENARIO 1: FINANCE/PII DATA COLLECTION")
    action1 = "Collect PII and credit score for AI-driven loan application processing."
    context1 = EthicsEvaluationRequestContext(
        domain="finance",
        data_sources=["user_pii_data", "transaction_history", "sensitive_data_user_credit_score"],
        purpose="To assess creditworthiness for a loan application using an AI model.",
        stakeholders=["applicant", "lender", "regulatory_body"]
    )
    options1 = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    result1 = ethical_compass.evaluate_action(
        action_description=action1,
        context=context1,
        options=options1
    )
    
    print_evaluation_result(result1, "Finance/PII Data Collection")
    
    # Scenario 2: Surveillance scenario (should trigger privacy and autonomy concerns)
    print_separator("SCENARIO 2: PUBLIC SURVEILLANCE")
    action2 = "Deploy AI facial recognition for public surveillance."
    context2 = EthicsEvaluationRequestContext(
        domain="surveillance",
        data_sources=["public_camera_feeds", "facial_recognition_database"],
        purpose="To monitor public spaces for security threats using AI-powered facial recognition."
    )
    
    result2 = ethical_compass.evaluate_action(
        action_description=action2,
        context=context2
    )
    
    print_evaluation_result(result2, "Public Surveillance")
    
    # Scenario 3: Anonymized healthcare data (should be more compliant)
    print_separator("SCENARIO 3: ANONYMIZED HEALTHCARE DATA")
    action3 = "Analyze anonymized public health data to improve disease prevention strategies."
    context3 = EthicsEvaluationRequestContext(
        domain="healthcare",
        data_sources=["anonymized_public_health_records"],
        purpose="To identify patterns that can improve public health interventions.",
        stakeholders=["public_health_officials", "researchers", "general_public"]
    )
    
    result3 = ethical_compass.evaluate_action(
        action_description=action3,
        context=context3
    )
    
    print_evaluation_result(result3, "Anonymized Healthcare Data")
    
    # Scenario 4: AI decision-making with no human oversight (should trigger autonomy concerns)
    print_separator("SCENARIO 4: AUTONOMOUS AI DECISION-MAKING")
    action4 = "Implement fully automated AI decision-making system for resource allocation."
    context4 = EthicsEvaluationRequestContext(
        domain="resource_management",
        data_sources=["historical_allocation_data", "current_resource_levels"],
        purpose="To optimize resource allocation without human intervention.",
        stakeholders=["resource_recipients", "system_administrators"]
    )
    
    result4 = ethical_compass.evaluate_action(
        action_description=action4,
        context=context4
    )
    
    print_evaluation_result(result4, "Autonomous AI Decision-Making")
    
    # Scenario 5: Educational AI with transparency (should be more compliant)
    print_separator("SCENARIO 5: EDUCATIONAL AI WITH TRANSPARENCY")
    action5 = "Develop an AI tutor that explains its reasoning and allows student control."
    context5 = EthicsEvaluationRequestContext(
        domain="education",
        data_sources=["anonymized_learning_patterns", "educational_content"],
        purpose="To provide personalized learning assistance with full transparency.",
        stakeholders=["students", "educators", "parents"]
    )
    
    result5 = ethical_compass.evaluate_action(
        action_description=action5,
        context=context5
    )
    
    print_evaluation_result(result5, "Educational AI with Transparency")

    print_separator("TESTING COMPLETE")
    print("All test scenarios completed successfully!")

if __name__ == "__main__":
    test_scenarios()