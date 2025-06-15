#!/usr/bin/env python3
"""
HTTP Client Test Script for ATRiAN Ethics as a Service (EaaS) API
----------------------------------------------------------------

This script tests the ATRiAN EaaS API by making HTTP requests to the API endpoints.
It assumes the API server is running at http://127.0.0.1:8000.

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
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

# API base URL
API_BASE_URL = "http://127.0.0.1:8000"

# Configure simple output
def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_result(title, result):
    print(f"\n--- {title} ---")
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                print(f"{key}:")
                for item in value[:2]:  # Print first 2 items
                    print(f"  - {item}")
                if len(value) > 2:
                    print(f"  ... and {len(value)-2} more items")
            else:
                print(f"{key}: {value}")
    else:
        print(result)

def test_evaluate_endpoint():
    print_header("Testing /ethics/evaluate Endpoint")
    
    # Create test request
    context = {
        "domain": "healthcare",
        "data_sources": ["patient_records", "medical_research"],
        "purpose": "Develop a diagnostic tool for early disease detection",
        "stakeholders": ["patients", "doctors", "hospital administrators"]
    }
    
    options = {
        "detail_level": "comprehensive",
        "include_alternatives": True
    }
    
    # Test Case 1: Generally ethical action
    request1 = {
        "action": "Analyze anonymized patient data to improve diagnostic accuracy",
        "context": context,
        "options": options
    }
    
    print("\nTest Case 1: Generally ethical action")
    response1 = requests.post(f"{API_BASE_URL}/ethics/evaluate", json=request1)
    if response1.status_code == 200:
        result1 = response1.json()
        print_result("Result", result1)
    else:
        print(f"Error: {response1.status_code} - {response1.text}")
    
    # Test Case 2: Potentially concerning action
    request2 = {
        "action": "Collect identifiable patient data without explicit consent for research purposes",
        "context": context,
        "options": options
    }
    
    print("\nTest Case 2: Potentially concerning action")
    response2 = requests.post(f"{API_BASE_URL}/ethics/evaluate", json=request2)
    if response2.status_code == 200:
        result2 = response2.json()
        print_result("Result", result2)
    else:
        print(f"Error: {response2.status_code} - {response2.text}")

def test_explain_endpoint():
    print_header("Testing /ethics/explain Endpoint")
    
    # Create a mock evaluation ID
    eval_id = f"eval_{uuid.uuid4()}"
    
    request = {
        "evaluation_id": eval_id,
        "explanation_token": f"expl_token_{uuid.uuid4()}"
    }
    
    response = requests.post(f"{API_BASE_URL}/ethics/explain", json=request)
    if response.status_code == 200:
        result = response.json()
        print_result("Explanation Result", result)
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_suggest_endpoint():
    print_header("Testing /ethics/suggest Endpoint")
    
    request = {
        "action_description": "Implement an AI diagnostic system that makes automated treatment decisions",
        "ethical_concerns": ["privacy", "autonomy"],
        "suggestion_count": 2
    }
    
    response = requests.post(f"{API_BASE_URL}/ethics/suggest", json=request)
    if response.status_code == 200:
        result = response.json()
        print_result("Suggestion Result", result)
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_framework_endpoints():
    print_header("Testing Framework Endpoints")
    
    # List all frameworks
    print("\nListing all ethical frameworks:")
    response = requests.get(f"{API_BASE_URL}/ethics/framework")
    if response.status_code == 200:
        frameworks = response.json()
        for i, framework in enumerate(frameworks):
            print(f"\n{i+1}. {framework['name']} (ID: {framework['id']})")
            print(f"   Version: {framework['version']}")
            print(f"   Active: {framework['active']}")
            print(f"   Principles: {', '.join(framework['principles'][:3])}...")
        
        # Get specific framework
        if frameworks:
            framework_id = frameworks[0]['id']
            print(f"\nGetting details for framework: {framework_id}")
            response = requests.get(f"{API_BASE_URL}/ethics/framework/{framework_id}")
            if response.status_code == 200:
                framework = response.json()
                print_result(f"Framework: {framework['name']}", framework)
            else:
                print(f"Error: {response.status_code} - {response.text}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def run_all_tests():
    """Run all test cases."""
    print_header("STARTING HTTP EAAS API TESTS")
    
    try:
        # First check if the API server is running
        try:
            response = requests.get(f"{API_BASE_URL}/docs")
            if response.status_code != 200:
                print(f"Warning: API server may not be running. Status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to API server at {API_BASE_URL}")
            print("Please make sure the API server is running before running this test script.")
            print("You can start the server with: uvicorn eaas_api:app --reload")
            return
        
        # Test each endpoint
        test_evaluate_endpoint()
        test_explain_endpoint()
        test_suggest_endpoint()
        test_framework_endpoints()
        
        print_header("ALL TESTS COMPLETED")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print_header("END OF TESTS")

if __name__ == "__main__":
    run_all_tests()