#!/usr/bin/env python3
"""
Direct Test Script for ATRiAN Ethics as a Service (EaaS) API
-----------------------------------------------------------

This script directly tests the ATRiAN EaaS API by importing the API components
and calling them directly without HTTP requests. This allows us to validate
the integration of EthicalCompass with the API endpoints.

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
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import API components
from eaas_api import (
    evaluate_ethics,
    explain_ethics,
    suggest_alternatives,
    list_ethical_frameworks,
    get_ethical_framework
)

# Import models
from eaas_models import (
    EthicsEvaluationRequestContext,
    EthicsEvaluationOptions,
    EthicsEvaluationRequest,
    EthicsExplanationRequest,
    EthicsSuggestionRequest
)

# Configure simple output
def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_result(title, result):
    print(f"\n--- {title} ---")
    if hasattr(result, "dict"):
        result_dict = result.dict()
        for key, value in result_dict.items():
            if isinstance(value, list) and value and hasattr(value[0], "dict"):
                print(f"{key}:")
                for item in value[:2]:  # Print first 2 items
                    item_dict = item.dict() if hasattr(item, "dict") else item
                    print(f"  - {item_dict}")
                if len(value) > 2:
                    print(f"  ... and {len(value)-2} more items")
            else:
                print(f"{key}: {value}")
    else:
        print(result)

async def test_evaluate_endpoint():
    print_header("Testing /ethics/evaluate Endpoint")
    
    # Create test request
    context = EthicsEvaluationRequestContext(
        domain="healthcare",
        data_sources=["patient_records", "medical_research"],
        purpose="Develop a diagnostic tool for early disease detection",
        stakeholders=["patients", "doctors", "hospital administrators"]
    )
    
    options = EthicsEvaluationOptions(
        detail_level="comprehensive",
        include_alternatives=True
    )
    
    # Test Case 1: Generally ethical action
    request1 = EthicsEvaluationRequest(
        action="Analyze anonymized patient data to improve diagnostic accuracy",
        context=context,
        options=options
    )
    
    print("\nTest Case 1: Generally ethical action")
    result1 = await evaluate_ethics(request1)
    print_result("Result", result1)
    
    # Test Case 2: Potentially concerning action
    request2 = EthicsEvaluationRequest(
        action="Collect identifiable patient data without explicit consent for research purposes",
        context=context,
        options=options
    )
    
    print("\nTest Case 2: Potentially concerning action")
    result2 = await evaluate_ethics(request2)
    print_result("Result", result2)

async def test_explain_endpoint():
    print_header("Testing /ethics/explain Endpoint")
    
    # Create a mock evaluation ID
    eval_id = f"eval_{uuid.uuid4()}"
    
    request = EthicsExplanationRequest(
        evaluation_id=eval_id,
        explanation_token=f"expl_token_{uuid.uuid4()}"
    )
    
    result = await explain_ethics(request)
    print_result("Explanation Result", result)

async def test_suggest_endpoint():
    print_header("Testing /ethics/suggest Endpoint")
    
    request = EthicsSuggestionRequest(
        action_description="Implement an AI diagnostic system that makes automated treatment decisions",
        ethical_concerns=["privacy", "autonomy"],
        suggestion_count=2
    )
    
    result = await suggest_alternatives(request)
    print_result("Suggestion Result", result)

async def test_framework_endpoints():
    print_header("Testing Framework Endpoints")
    
    # List all frameworks
    print("\nListing all ethical frameworks:")
    frameworks = await list_ethical_frameworks()
    for i, framework in enumerate(frameworks):
        print(f"\n{i+1}. {framework.name} (ID: {framework.id})")
        print(f"   Version: {framework.version}")
        print(f"   Active: {framework.active}")
        print(f"   Principles: {', '.join(framework.principles[:3])}...")
    
    # Get specific framework
    if frameworks:
        framework_id = frameworks[0].id
        print(f"\nGetting details for framework: {framework_id}")
        framework = await get_ethical_framework(framework_id)
        print_result(f"Framework: {framework.name}", framework)

async def run_all_tests():
    """Run all test cases."""
    print_header("STARTING DIRECT EAAS API TESTS")
    
    try:
        # Test each endpoint
        await test_evaluate_endpoint()
        await test_explain_endpoint()
        await test_suggest_endpoint()
        await test_framework_endpoints()
        
        print_header("ALL TESTS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print_header("END OF TESTS")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_all_tests())