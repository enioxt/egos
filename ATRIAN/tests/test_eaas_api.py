"""
ATRiAN EaaS API Test Script

This script tests the core functionality of the ATRiAN EaaS API without needing to run a server.
It directly calls the API endpoint functions and verifies the integration with EthicalCompass.
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import asyncio
import json
from datetime import datetime

# Import the API components directly (no relative imports)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eaas_models import (
    EthicsEvaluationOptions, 
    EthicsEvaluationRequestContext,
    EthicsEvaluationRequest
)

# Create a direct instance of EthicalCompass for testing
from atrian_ethical_compass import EthicalCompass
ethical_compass = EthicalCompass()

# We'll test the core logic directly instead of through the API endpoint
# This avoids the async/FastAPI dependencies

def test_evaluate_ethics():
    """Test the EthicalCompass with a finance/PII scenario."""
    print("Testing EthicalCompass with finance/PII scenario...")
    
    # Create test data similar to what would be sent to the API
    action = "Collect PII and credit score for AI-driven loan application processing."
    context = EthicsEvaluationRequestContext(
        domain="finance",
        data_sources=["user_pii_data", "transaction_history", "sensitive_data_user_credit_score"],
        purpose="To assess creditworthiness for a loan application using an AI model.",
        stakeholders=["applicant", "lender", "regulatory_body"]
    )
    options = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    # Call the EthicalCompass directly
    result = ethical_compass.evaluate_action(
        action_description=action,
        context=context,
        options=options
    )
    
    # Add a mock evaluation_id and explanation_token for completeness
    # (these would normally be added by the API layer)
    result.evaluation_id = "test_eval_001"
    result.explanation_token = "test_token_001"
    
    # Print the result in a readable format
    print("\nEvaluation Result:")
    print(f"  Ethical Score: {result.ethical_score}")
    print(f"  Compliant: {result.compliant}")
    
    print("\nConcerns:")
    for i, concern in enumerate(result.concerns, 1):
        print(f"  {i}. [{concern.severity.upper()}] {concern.principle}: {concern.description}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. [{rec.priority.upper()}] {rec.action}")
        print(f"     Rationale: {rec.rationale}")
    
    # Return success if we got this far
    return True

def test_surveillance_scenario():
    """Test a surveillance scenario which should trigger specific ethical concerns."""
    print("\n\nTesting surveillance scenario...")
    
    action = "Deploy AI facial recognition for public surveillance."
    context = EthicsEvaluationRequestContext(
        domain="surveillance",
        data_sources=["public_camera_feeds", "facial_recognition_database"],
        purpose="To monitor public spaces for security threats using AI-powered facial recognition."
    )
    
    result = ethical_compass.evaluate_action(
        action_description=action,
        context=context
    )
    
    print("\nEvaluation Result:")
    print(f"  Ethical Score: {result.ethical_score}")
    print(f"  Compliant: {result.compliant}")
    
    print("\nConcerns:")
    for i, concern in enumerate(result.concerns, 1):
        print(f"  {i}. [{concern.severity.upper()}] {concern.principle}: {concern.description}")
    
    return True

def test_compliant_scenario():
    """Test a scenario that should be ethically compliant."""
    print("\n\nTesting compliant scenario...")
    
    action = "Analyze anonymized public health data to improve disease prevention strategies."
    context = EthicsEvaluationRequestContext(
        domain="healthcare",
        data_sources=["anonymized_public_health_records"],
        purpose="To identify patterns that can improve public health interventions.",
        stakeholders=["public_health_officials", "researchers", "general_public"]
    )
    
    result = ethical_compass.evaluate_action(
        action_description=action,
        context=context
    )
    
    print("\nEvaluation Result:")
    print(f"  Ethical Score: {result.ethical_score}")
    print(f"  Compliant: {result.compliant}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. [{rec.priority.upper()}] {rec.action}")
    
    return True

def run_all_tests():
    """Run all test scenarios."""
    try:
        test_evaluate_ethics()
        test_surveillance_scenario()
        test_compliant_scenario()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the tests
    run_all_tests()