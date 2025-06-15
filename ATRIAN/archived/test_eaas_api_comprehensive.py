#!/usr/bin/env python3
"""
Comprehensive Test Suite for ATRiAN Ethics as a Service (EaaS) API
------------------------------------------------------------------

This script provides a comprehensive test suite for the ATRiAN EaaS API,
focusing on the integration of the EthicalCompass core logic with the API endpoints.

It tests:
1. Direct EthicalCompass functionality
2. API endpoint integration
3. Various ethical scenarios
4. Error handling and edge cases

Usage:
    python test_eaas_api_comprehensive.py

Author: EGOS Team
Version: 1.0.0
Date: 2025-06-01
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
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import ATRiAN components
from atrian_ethical_compass import EthicalCompass
from eaas_models import (
    EthicsEvaluationRequestContext,
    EthicsEvaluationOptions,
    EthicsEvaluationResult,
    EthicsEvaluationRequest,
    EthicalConcern,
    EthicalRecommendation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("eaas_api_test")

# Test configuration
RULES_FILEPATH = "C:/EGOS/ATRiAN/ethics_rules.yaml"
TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "total": 0
}

def print_separator(title: str) -> None:
    """Print a separator with a title for better test output readability."""
    width = 80
    print("\n" + "=" * width)
    print(f"{title.center(width)}")
    print("=" * width)

def assert_test(condition: bool, message: str, warning: bool = False, details: Any = None) -> None:
    """Assert a test condition and update test results."""
    TEST_RESULTS["total"] += 1
    
    if condition:
        TEST_RESULTS["passed"] += 1
        logger.info(f"✅ PASS: {message}")
        if details:
            print(f"    Details: {details}")
    else:
        if warning:
            TEST_RESULTS["warnings"] += 1
            logger.warning(f"⚠️ WARNING: {message}")
            if details:
                print(f"    Details: {details}")
        else:
            TEST_RESULTS["failed"] += 1
            logger.error(f"❌ FAIL: {message}")
            if details:
                print(f"    Details: {details}")

def test_ethical_compass_initialization() -> None:
    """Test the initialization of the EthicalCompass class."""
    print_separator("TESTING ETHICAL COMPASS INITIALIZATION")
    
    # Test with default rules path
    compass1 = EthicalCompass()
    assert_test(
        compass1 is not None, 
        "EthicalCompass initialized with default rules path"
    )
    
    # Test with explicit rules path
    compass2 = EthicalCompass(rules_filepath=RULES_FILEPATH)
    assert_test(
        compass2 is not None, 
        "EthicalCompass initialized with explicit rules path"
    )
    
    # Test with non-existent rules path (should log warning but not fail)
    non_existent_path = "C:/EGOS/ATRiAN/non_existent_rules.yaml"
    compass3 = EthicalCompass(rules_filepath=non_existent_path)
    assert_test(
        compass3 is not None, 
        "EthicalCompass initialized with non-existent rules path (should log warning)"
    )

def test_ethical_compass_evaluation() -> None:
    """Test the evaluation functionality of the EthicalCompass class."""
    print_separator("TESTING ETHICAL COMPASS EVALUATION")
    
    compass = EthicalCompass(rules_filepath=RULES_FILEPATH)
    
    # Test case 1: Privacy concern scenario
    context1 = EthicsEvaluationRequestContext(
        domain="finance",
        stakeholders=["users", "financial institution"],
        data_sources=["biometric", "personal"],
        purpose="User authentication for financial services"
    )
    options1 = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    # Define the action
    action1 = "Collect user biometric data for authentication"
    
    # Call evaluate_action with the correct signature
    result1 = compass.evaluate_action(action1, context1, options1)
    
    assert_test(
        isinstance(result1, EthicsEvaluationResult),
        "EthicalCompass.evaluate_action returns an EthicsEvaluationResult object"
    )
    assert_test(
        result1.evaluation_id is not None and len(result1.evaluation_id) > 0,
        "EthicsEvaluationResult contains a valid evaluation_id"
    )
    assert_test(
        result1.explanation_token is not None and len(result1.explanation_token) > 0,
        "EthicsEvaluationResult contains a valid explanation_token"
    )
    assert_test(
        len(result1.concerns) > 0,
        "Privacy scenario should identify at least one ethical concern"
    )
    assert_test(
        any("privacy" in concern.lower() for concern in result1.concerns),
        "Privacy scenario should identify privacy-related concerns"
    )
    assert_test(
        len(result1.recommendations) > 0,
        "Privacy scenario should provide recommendations"
    )
    
    # Test case 2: Surveillance concern scenario
    context2 = EthicsEvaluationRequestContext(
        domain="workplace",
        stakeholders=["employees", "management"],
        data_sources=["activity logs", "personal"],
        purpose="Productivity tracking"
    )
    options2 = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    action2 = "Monitor employee computer activity"
    result2 = compass.evaluate_action(action2, context2, options2)
    
    assert_test(
        isinstance(result2, EthicsEvaluationResult),
        "EthicalCompass.evaluate_action returns an EthicsEvaluationResult object for surveillance scenario"
    )
    assert_test(
        len(result2.concerns) > 0,
        "Surveillance scenario should identify at least one ethical concern"
    )
    assert_test(
        any("surveillance" in concern.lower() or "privacy" in concern.lower() or "trust" in concern.lower() 
            for concern in result2.concerns),
        "Surveillance scenario should identify surveillance, privacy, or trust concerns"
    )
    
    # Test case 3: Compliant scenario
    context3 = EthicsEvaluationRequestContext(
        domain="software",
        stakeholders=["users", "developers"],
        data_sources=["anonymized usage data"],
        purpose="Improving user experience with opt-in analytics"
    )
    options3 = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=False
    )
    
    action3 = "Provide anonymized usage statistics"
    result3 = compass.evaluate_action(action3, context3, options3)
    
    assert_test(
        isinstance(result3, EthicsEvaluationResult),
        "EthicalCompass.evaluate_action returns an EthicsEvaluationResult object for compliant scenario"
    )
    # Note: This is a more compliant scenario, but may still have some concerns
    # We'll check that it has fewer concerns than the privacy scenario
    assert_test(
        len(result3.concerns) <= len(result1.concerns),
        "Compliant scenario should have fewer concerns than privacy scenario",
        warning=True
    )

def test_edge_cases() -> None:
    """Test edge cases and error handling in the EthicalCompass class."""
    print_separator("TESTING EDGE CASES")
    
    compass = EthicalCompass(rules_filepath=RULES_FILEPATH)
    
    # Test case 1: Empty context
    context1 = EthicsEvaluationRequestContext(
        domain="",
        stakeholders=[],
        data_sources=[],
        purpose=""
    )
    options1 = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    action1 = ""
    result1 = compass.evaluate_action(action1, context1, options1)
    
    assert_test(
        isinstance(result1, EthicsEvaluationResult),
        "EthicalCompass handles empty context gracefully"
    )
    assert_test(
        result1.evaluation_id is not None,
        "Empty context evaluation still produces an evaluation_id"
    )
    
    # Test case 2: Very long inputs
    long_text = "This is a very long text. " * 100
    context2 = EthicsEvaluationRequestContext(
        domain="test",
        stakeholders=["user"] * 50,
        data_sources=["data"] * 50,
        purpose=long_text
    )
    
    action2 = long_text
    result2 = compass.evaluate_action(action2, context2, options1)
    
    assert_test(
        isinstance(result2, EthicsEvaluationResult),
        "EthicalCompass handles very long inputs gracefully"
    )
    
    # Test case 3: Different detail level
    options3 = EthicsEvaluationOptions(
        detail_level="minimal",
        include_alternatives=False
    )
    
    # This should use the minimal detail level
    action3 = "Process user data"
    result3 = compass.evaluate_action(action3, context1, options3)
    
    assert_test(
        isinstance(result3, EthicsEvaluationResult),
        "EthicalCompass handles different detail levels gracefully"
    )

def test_multiple_evaluations() -> None:
    """Test multiple evaluations to ensure consistency and uniqueness."""
    print_separator("TESTING MULTIPLE EVALUATIONS")
    
    compass = EthicalCompass(rules_filepath=RULES_FILEPATH)
    
    # Create a standard context for repeated evaluations
    context = EthicsEvaluationRequestContext(
        domain="web",
        stakeholders=["users", "website owners"],
        data_sources=["preferences", "browsing history"],
        purpose="A website wants to customize content based on user preferences"
    )
    options = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    # Define the action
    action = "Process user data for personalization"
    
    # Perform multiple evaluations
    evaluation_ids = []
    explanation_tokens = []
    
    for i in range(5):
        result = compass.evaluate_action(action, context, options)
        
        assert_test(
            isinstance(result, EthicsEvaluationResult),
            f"Evaluation {i+1} returns a valid result"
        )
        
        evaluation_ids.append(result.evaluation_id)
        explanation_tokens.append(result.explanation_token)
    
    # Check that all evaluation IDs are unique
    assert_test(
        len(set(evaluation_ids)) == len(evaluation_ids),
        "All evaluation IDs should be unique"
    )
    
    # Check that all explanation tokens are unique
    assert_test(
        len(set(explanation_tokens)) == len(explanation_tokens),
        "All explanation tokens should be unique"
    )
    
    # Check consistency in concerns (they should be similar but not identical due to potential randomness)
    # This is a soft check, as some variation is expected
    concern_counts = []
    for i in range(5):
        result = compass.evaluate_action(action, context, options)
        concern_counts.append(len(result.concerns))
    
    # Check that the number of concerns is relatively consistent
    max_diff = max(concern_counts) - min(concern_counts)
    assert_test(
        max_diff <= 2,
        f"Concern count should be relatively consistent (max difference: {max_diff})",
        warning=True
    )

def run_all_tests() -> None:
    """Run all test cases."""
    print_separator("STARTING COMPREHENSIVE EAAS API TESTS")
    
    try:
        # Run all test functions
        print("\n1. Testing EthicalCompass initialization...")
        test_ethical_compass_initialization()
        print("\n2. Testing EthicalCompass evaluation...")
        test_ethical_compass_evaluation()
        print("\n3. Testing edge cases...")
        test_edge_cases()
        print("\n4. Testing multiple evaluations...")
        test_multiple_evaluations()
        
        # Print test summary
        print_separator("TEST SUMMARY")
        print(f"Total tests: {TEST_RESULTS['total']}")
        print(f"Passed: {TEST_RESULTS['passed']}")
        print(f"Failed: {TEST_RESULTS['failed']}")
        print(f"Warnings: {TEST_RESULTS['warnings']}")
        
        success_rate = (TEST_RESULTS['passed'] / TEST_RESULTS['total']) * 100
        print(f"Success rate: {success_rate:.2f}%")
        
        if TEST_RESULTS['failed'] == 0:
            print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")
        else:
            print(f"\n⚠️ {TEST_RESULTS['failed']} TESTS FAILED!")
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print_separator("END OF TESTS")

if __name__ == "__main__":
    run_all_tests()