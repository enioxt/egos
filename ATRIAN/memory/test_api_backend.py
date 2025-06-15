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

# - @references {C:\EGOS\ATRiAN\memory\windsurf_api_backend.py}
# - @references {C:\EGOS\ATRiAN\memory\mock_windsurf_api.py}
# - @references {C:\EGOS\ATRiAN\memory\windsurf_memory_adapter.py}
# --- 

import os
import sys
import json
import time
import logging
import traceback
import subprocess
import threading
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_backend_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_backend_test")

# Import ATRiAN components
try:
    from memory.windsurf_memory_adapter import WindsurfMemoryAdapter
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

def start_mock_server(port=8000):
    """Start the mock API server as a subprocess."""
    try:
        print_section("Starting Mock Windsurf API Server")
        process = subprocess.Popen(
            [sys.executable, "mock_windsurf_api.py", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if server is running
        try:
            response = requests.get(f"http://localhost:{port}/api/v1/atrian/health")
            if response.status_code == 200:
                print(f"✅ Mock API server running on port {port}")
                return process
            else:
                print(f"❌ Server started but health check failed: {response.status_code}")
                process.kill()
                return None
        except requests.RequestException:
            print("❌ Failed to connect to mock API server")
            process.kill()
            return None
    except Exception as e:
        print(f"❌ Failed to start mock API server: {str(e)}")
        traceback.print_exc()
        return None

def test_api_backend(port=8000):
    """Test the WindsurfAPIBackend with the mock API."""
    print_section("Testing WindsurfAPIBackend")
    
    api_url = f"http://localhost:{port}/api/v1/atrian"
    print(f"API URL: {api_url}")
    
    try:
        # Initialize WindsurfAPIBackend
        backend = WindsurfAPIBackend(api_base_url=api_url)
        print("✅ WindsurfAPIBackend initialized")
        
        # Check API connection
        if backend._check_api_connection():
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return False
        
        # Test storing data
        test_key = f"test_key_{int(time.time())}"
        test_value = "Test value from API backend test"
        test_metadata = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "api_backend_test"
        }
        
        print(f"\nStoring data with key: {test_key}")
        store_result = backend.store(test_key, test_value, test_metadata)
        if store_result:
            print("✅ Data stored successfully")
        else:
            print("❌ Failed to store data")
            return False
        
        # Test retrieving data
        print(f"\nRetrieving data with key: {test_key}")
        retrieved_value, retrieved_metadata = backend.retrieve(test_key)
        
        if retrieved_value == test_value:
            print("✅ Retrieved value matches stored value")
        else:
            print(f"❌ Value mismatch. Expected: {test_value}, Got: {retrieved_value}")
            return False
        
        # Verify metadata
        if retrieved_metadata.get("test_type") == "api_backend_test":
            print("✅ Retrieved metadata matches stored metadata")
        else:
            print("❌ Metadata mismatch")
            return False
        
        # Test listing keys
        print("\nListing keys")
        keys = backend.list(prefix="test_key_")
        if test_key in keys:
            print(f"✅ Listed {len(keys)} keys, including our test key")
        else:
            print("❌ Test key not found in listing")
            return False
        
        # Test deleting data
        print(f"\nDeleting data with key: {test_key}")
        delete_result = backend.delete(test_key)
        if delete_result:
            print("✅ Data deleted successfully")
        else:
            print("❌ Failed to delete data")
            return False
        
        # Verify deletion
        try:
            retrieved_value, _ = backend.retrieve(test_key)
            print("❌ Data still exists after deletion")
            return False
        except Exception:
            print("✅ Data properly deleted (retrieval failed as expected)")
        
        # Test storing multiple items and clearing
        print("\nStoring multiple items")
        prefix = f"test_batch_{int(time.time())}_"
        for i in range(5):
            backend.store(f"{prefix}{i}", f"Batch test value {i}", {"batch": True})
        
        keys = backend.list(prefix=prefix)
        if len(keys) == 5:
            print(f"✅ Stored 5 batch items")
        else:
            print(f"❌ Expected 5 batch items, found {len(keys)}")
            return False
        
        # Test clearing data
        print(f"\nClearing data with prefix: {prefix}")
        cleared_count = backend.clear(prefix=prefix)
        if cleared_count == 5:
            print("✅ Cleared 5 items as expected")
        else:
            print(f"❌ Expected to clear 5 items, cleared {cleared_count}")
            return False
        
        print("\n✅ All WindsurfAPIBackend tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during backend testing: {str(e)}")
        traceback.print_exc()
        return False

def test_memory_adapter_with_api_backend(port=8000):
    """Test the WindsurfMemoryAdapter with the WindsurfAPIBackend."""
    print_section("Testing WindsurfMemoryAdapter with WindsurfAPIBackend")
    
    api_url = f"http://localhost:{port}/api/v1/atrian"
    
    try:
        # Initialize components
        backend = WindsurfAPIBackend(api_base_url=api_url)
        adapter = WindsurfMemoryAdapter(backend=backend)
        print("✅ WindsurfMemoryAdapter initialized with WindsurfAPIBackend")
        
        # Test trust score storage and retrieval
        print("\nStoring trust score")
        user_id = "test_api_user"
        trust_score = 0.75
        
        adapter.store_trust_score(user_id, trust_score)
        print(f"✅ Trust score stored: {trust_score}")
        
        retrieved_score = adapter.retrieve_trust_score(user_id)
        print(f"✅ Trust score retrieved: {retrieved_score}")
        
        if abs(retrieved_score - trust_score) < 0.001:
            print("✅ Trust score matches")
        else:
            print(f"❌ Trust score mismatch: Expected {trust_score}, Got {retrieved_score}")
            return False
        
        # Test operation storage and retrieval
        print("\nStoring operation")
        operation_type = "test_operation"
        context = {
            "action": "api_backend_test",
            "timestamp": datetime.now().isoformat(),
            "data": "Test data for API backend integration"
        }
        result = {"status": "success", "message": "Operation completed"}
        
        operation_id = adapter.store_operation(
            user_id=user_id,
            operation_type=operation_type,
            context=context,
            result=result
        )
        print(f"✅ Operation stored with ID: {operation_id}")
        
        # Retrieve context
        contexts = adapter.retrieve_context(user_id, operation_type)
        if contexts and len(contexts) > 0:
            print(f"✅ Retrieved {len(contexts)} contexts")
            
            # Verify context content
            found = False
            for ctx in contexts:
                if (ctx.get("context", {}).get("action") == "api_backend_test" and 
                    ctx.get("operation_id") == operation_id):
                    found = True
                    break
            
            if found:
                print("✅ Context content matches")
            else:
                print("❌ Context content mismatch")
                return False
        else:
            print("❌ No contexts retrieved")
            return False
        
        # Test privacy filtering in context
        print("\nTesting privacy filtering")
        sensitive_context = {
            "email": "test@example.com",
            "credit_card": "1234-5678-9012-3456",
            "password": "secret123"
        }
        
        sensitive_op_id = adapter.store_operation(
            user_id=user_id,
            operation_type="privacy_test",
            context=sensitive_context,
            result={"status": "filtered"}
        )
        print(f"✅ Sensitive operation stored with ID: {sensitive_op_id}")
        
        # Retrieve sensitive context (should be filtered)
        sensitive_contexts = adapter.retrieve_context(user_id, "privacy_test")
        if sensitive_contexts and len(sensitive_contexts) > 0:
            context_data = sensitive_contexts[0].get("context", {})
            
            # Check if sensitive data was anonymized
            if ("[EMAIL]" in str(context_data) or 
                "[CREDIT_CARD]" in str(context_data) or 
                "secret123" not in str(context_data)):
                print("✅ Privacy filtering working correctly")
            else:
                print("❌ Privacy filtering not working")
                return False
        else:
            print("❌ No sensitive contexts retrieved")
            return False
        
        print("\n✅ All WindsurfMemoryAdapter with API backend tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during adapter testing: {str(e)}")
        traceback.print_exc()
        return False

def run_tests(port=8000):
    """Run all API backend tests."""
    print_banner("ATRiAN WindsurfAPIBackend Integration Tests")
    
    # Start mock server
    server_process = start_mock_server(port)
    if not server_process:
        print("❌ Cannot continue tests without mock server")
        return
    
    try:
        # Run tests
        backend_result = test_api_backend(port)
        adapter_result = test_memory_adapter_with_api_backend(port)
        
        # Final summary
        print_section("Test Results Summary")
        print(f"WindsurfAPIBackend direct tests: {'✅ PASSED' if backend_result else '❌ FAILED'}")
        print(f"WindsurfMemoryAdapter with API backend tests: {'✅ PASSED' if adapter_result else '❌ FAILED'}")
        
        if backend_result and adapter_result:
            print("\n✅ All tests PASSED! The WindsurfAPIBackend is functioning correctly.")
        else:
            print("\n❌ Some tests FAILED. Please review the logs for details.")
    
    finally:
        # Stop the mock server
        print_section("Stopping Mock Server")
        if server_process:
            server_process.terminate()
            time.sleep(1)
            if server_process.poll() is None:  # Still running
                server_process.kill()
            print("✅ Mock server stopped")

if __name__ == "__main__":
    run_tests()