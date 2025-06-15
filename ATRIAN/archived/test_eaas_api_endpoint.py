#!/usr/bin/env python3
"""
ATRiAN EaaS API Endpoint Test
-----------------------------

This script tests the ATRiAN Ethics as a Service (EaaS) API endpoints directly.

Usage:
    python test_eaas_api_endpoint.py

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

import requests
import json
import sys
from pprint import pprint

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def print_separator(title=None):
    """Print a separator line with optional title."""
    width = 80
    if title:
        print(f"\n{'-' * 10} {title} {'-' * (width - len(title) - 12)}")
    else:
        print(f"\n{'-' * width}")

def test_ethics_evaluate_endpoint():
    """Test the /ethics/evaluate endpoint with a sample request."""
    print_separator("TESTING /ethics/evaluate ENDPOINT")
    
    # Prepare the request data
    request_data = {
        "action": "Collect user browsing data for targeted advertising",
        "context": {
            "domain": "advertising",
            "stakeholders": ["users", "advertisers", "platform"],
            "data_sources": ["browsing history", "user preferences", "demographics"],
            "purpose": "Personalized advertising and revenue generation"
        },
        "options": {
            "detail_level": "comprehensive",
            "include_alternatives": True
        }
    }
    
    # Send the request
    try:
        print(f"Sending request to {API_BASE_URL}/ethics/evaluate")
        response = requests.post(
            f"{API_BASE_URL}/ethics/evaluate",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check the response
        if response.status_code == 200:
            print(f"✅ Request successful (Status: {response.status_code})")
            result = response.json()
            
            # Print the evaluation result
            print("\nEvaluation Result:")
            print(f"Evaluation ID: {result.get('evaluation_id', 'N/A')}")
            print(f"Explanation Token: {result.get('explanation_token', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            print(f"Overall Rating: {result.get('overall_rating', 'N/A')}")
            
            # Print ethical concerns
            print("\nEthical Concerns:")
            for i, concern in enumerate(result.get('concerns', []), 1):
                print(f"  {i}. {concern.get('principle', 'Unknown Principle')}: {concern.get('description', 'No description')}")
                print(f"     Severity: {concern.get('severity', 'Unknown')}")
            
            # Print recommendations
            print("\nRecommendations:")
            for i, rec in enumerate(result.get('recommendations', []), 1):
                print(f"  {i}. {rec.get('title', 'Untitled')}: {rec.get('description', 'No description')}")
                print(f"     Principle: {rec.get('principle', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Request failed (Status: {response.status_code})")
            print(f"Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

def main():
    """Run all API endpoint tests."""
    print("\nATRiAN EaaS API ENDPOINT TESTS")
    print("==============================")
    
    # Check if the API server is running
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding correctly")
            print(f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Please start it with 'python run_eaas_api_server.py'")
        return False
    
    # Run the tests
    success = test_ethics_evaluate_endpoint()
    
    # Print summary
    print_separator("TEST SUMMARY")
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed. Please check the logs above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)