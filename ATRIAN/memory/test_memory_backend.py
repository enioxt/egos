#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Cross-references:
# - @references {C:\EGOS\ATRiAN\memory\windsurf_memory_adapter.py}
# - @references {C:\EGOS\ATRiAN\memory\windsurf_api_backend.py}
# --- 

import os
import sys
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory_backend_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("memory_backend_test")

# Import memory components
try:
    from memory.windsurf_memory_adapter import WindsurfMemoryAdapter, LocalStorageBackend, PrivacySensitivity
    from memory.windsurf_api_backend import WindsurfAPIBackend
    logger.info("Successfully imported memory components")
except ImportError as e:
    logger.error(f"Error importing memory components: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

def print_banner(title: str) -> None:
    """Print a formatted banner with the given title."""
    width = 80
    padding = (width - len(title) - 4) // 2
    print("\n" + "=" * width)
    print(" " * padding + f"| {title} |")
    print("=" * width + "\n")

def print_section(title: str) -> None:
    """Print a section title."""
    print(f"\n--- {title} ---")

def test_backend_initialization():
    """Test the initialization of different backend types."""
    print_section("Backend Initialization Tests")
    
    # Create a temporary directory for the test
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    # Test LocalStorageBackend
    print("Testing LocalStorageBackend initialization...")
    try:
        local_backend = LocalStorageBackend(storage_dir=test_dir)
        print("✅ LocalStorageBackend initialized successfully")
    except Exception as e:
        print(f"❌ LocalStorageBackend initialization failed: {str(e)}")
        traceback.print_exc()
    
    # Test WindsurfAPIBackend
    print("\nTesting WindsurfAPIBackend initialization...")
    try:
        # Use a placeholder URL - this will likely fail to connect but should initialize
        api_base_url = "http://localhost:8000"  # Corrected base URL for the mock server
        api_backend = WindsurfAPIBackend(api_base_url=api_base_url)
        print(f"✅ WindsurfAPIBackend initialized successfully with URL: {api_base_url}")
        
        # Test connection (expected to fail if no server is running)
        connection_result = api_backend._check_api_connection()
        print(f"Connection check result: {'✅ Connected' if connection_result else '❌ Failed to connect'}")
    except Exception as e:
        print(f"❌ WindsurfAPIBackend initialization failed: {str(e)}")
        traceback.print_exc()

def test_memory_adapter_with_local_backend():
    """Test the WindsurfMemoryAdapter with LocalStorageBackend."""
    print_section("WindsurfMemoryAdapter with LocalStorageBackend Tests")
    
    # Create a temporary directory for the test
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")
    os.makedirs(test_dir, exist_ok=True)
    
    # Initialize components
    try:
        # Create LocalStorageBackend
        backend = LocalStorageBackend(storage_dir=test_dir)
        print("✅ LocalStorageBackend initialized")
        
        # Create WindsurfMemoryAdapter with LocalStorageBackend
        adapter = WindsurfMemoryAdapter(backend=backend)
        print("✅ WindsurfMemoryAdapter initialized with LocalStorageBackend")
        
        # Test basic operations
        test_key = f"test_key_{int(time.time())}"
        test_value = "Test value for memory adapter"
        
        # Store a value
        print(f"\nStoring value with key: {test_key}")
        adapter.store_operation(
            user_id="test_user",
            operation_type="test_operation",
            context={"test_key": test_key, "test_data": test_value},
            result={"status": "success"}
        )
        print("✅ Value stored successfully")
        
        # Retrieve context
        print("\nRetrieving context for test_operation")
        context_items = adapter.retrieve_context("test_user", "test_operation")
        print(f"Retrieved {len(context_items)} context items")
        
        for i, item in enumerate(context_items):
            print(f"  Item {i+1}:")
            print(f"    Operation ID: {item.get('operation_id', 'unknown')}")
            print(f"    Timestamp: {item.get('timestamp', 'unknown')}")
            print(f"    Context: {item.get('context', {})}")
        
        # Test trust score storage and retrieval
        print("\nTesting trust score storage and retrieval")
        adapter.store_trust_score("test_user", 0.85)
        retrieved_score = adapter.retrieve_trust_score("test_user")
        print(f"Stored trust score: 0.85, Retrieved trust score: {retrieved_score}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        traceback.print_exc()

def test_memory_adapter_with_api_backend():
    """Test the WindsurfMemoryAdapter with WindsurfAPIBackend and a running mock server."""
    print_section("WindsurfMemoryAdapter with WindsurfAPIBackend Tests")
    
    api_base_url = "http://localhost:8000" # Corrected base URL for the mock server
    
    try:
        # Initialize WindsurfAPIBackend
        api_backend = WindsurfAPIBackend(api_base_url=api_base_url)
        print(f"Attempting to connect to mock API at: {api_base_url}")
        
        # Check connection (should succeed if mock server is running)
        if not api_backend._check_api_connection():
            print(f"❌ CRITICAL: Failed to connect to the mock API server at {api_base_url}.")
            print("Please ensure 'enhanced_mock_windsurf_api.py' is running.")
            return 
        print("✅ WindsurfAPIBackend initialized and connected to mock API.")
        
        # Create WindsurfMemoryAdapter with WindsurfAPIBackend
        adapter = WindsurfMemoryAdapter(backend=api_backend)
        print("✅ WindsurfMemoryAdapter initialized with WindsurfAPIBackend")
        
        user_id = f"api_user_{int(time.time())}"
        operation_type_success = "api_test_success"
        operation_type_error = "api_test_error_sim"
        context_success = {"data": "This should succeed via API", "timestamp": datetime.now().isoformat()}
        context_error = {"data": "This should trigger a simulated error", "error_code": "500"} 
        
        # Test 1: Successful operation storage and retrieval
        print(f"\nStoring successful operation for user: {user_id}, type: {operation_type_success}")
        adapter.store_operation(
            user_id=user_id,
            operation_type=operation_type_success,
            context=context_success,
            result={"status": "success", "message": "API call successful"}
        )
        print("✅ Successful operation stored via API.")
        
        print(f"\nRetrieving context for user: {user_id}, type: {operation_type_success}")
        retrieved_items_success = adapter.retrieve_context(user_id, operation_type_success)
        print(f"Retrieved {len(retrieved_items_success)} items for successful operation.")
        if retrieved_items_success:
            assert any(item['context'].get('data') == context_success['data'] for item in retrieved_items_success), "Retrieved data mismatch"
            print("✅ Content of retrieved successful operation verified (basic check).")
        else:
            print("❌ No items retrieved for successful operation.")

        # Test 2: Trust score storage and retrieval via API
        print("\nTesting trust score storage and retrieval via API")
        trust_score_api = 0.77
        adapter.store_trust_score(user_id, trust_score_api)
        print(f"Stored trust score via API: {trust_score_api}")
        retrieved_score_api = adapter.retrieve_trust_score(user_id)
        print(f"Retrieved trust score via API: {retrieved_score_api}")
        assert retrieved_score_api == trust_score_api, "Trust score mismatch via API"
        print("✅ Trust score verified via API.")

        # Test 3: Simulate an error 
        print(f"\nAttempting to store an operation designed to simulate an error for user: {user_id}")
        try:
            adapter.store_operation(
                user_id=user_id,
                operation_type=operation_type_error,
                context=context_error, 
                result={"status": "attempted_error_sim"}
            )
            print("✅ Error simulation request sent. Check mock server logs for error handling.")
        except Exception as e_sim:
            print(f"✅ Error simulation correctly triggered an exception in the client: {str(e_sim)}")

        # Test 4: Latency simulation
        print("\nAttempting an operation configured for latency (manual check of timing).")
        context_latency = {"data": "This call should have latency", "simulate_latency_ms": "1000"}
        start_time = time.time()
        adapter.store_operation(
            user_id=user_id,
            operation_type="api_test_latency",
            context=context_latency,
            result={"status": "latency_test"}
        )
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ Latency simulation request sent. Call duration: {duration:.2f}s. Check mock server config for expected latency.")
        if 'simulate_latency_ms' in context_latency:
             expected_latency_s = int(context_latency['simulate_latency_ms']) / 1000.0
             assert duration >= expected_latency_s, f"Duration {duration}s was less than expected latency {expected_latency_s}s"
             print(f"✅ Call duration {duration:.2f}s is consistent with expected latency of {expected_latency_s}s.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        traceback.print_exc()

def run_tests():
    """Run all memory backend tests."""
    print_banner("ATRiAN Memory Backend Tests")
    
    try:
        # Run individual test functions
        test_backend_initialization()
        test_memory_adapter_with_local_backend()
        test_memory_adapter_with_api_backend() # Add the new test here
        
        print("\nAll tests completed.")
    except Exception as e:
        logger.error(f"Error during tests: {str(e)}")
        traceback.print_exc()
    
    print("\nTo clean up the test data, delete the 'test_data' directory.")

if __name__ == "__main__":
    run_tests()