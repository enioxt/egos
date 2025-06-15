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

# - @references {C:\EGOS\ATRiAN\ui\trust_visualization.js}
# - @references {C:\EGOS\run_tools.py}
# - @references {C:\EGOS\ATRiAN\tests\test_memory_integration.py}
# --- 

import os
import sys
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_memory_demo")

# Import ATRiAN components
try:
    from memory.windsurf_memory_adapter import WindsurfMemoryAdapter, LocalStorageBackend, PrivacySensitivity
    from memory.windsurf_api_backend import WindsurfAPIBackend  # Added import
    from atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType
except ImportError as e:
    logger.error(f"Error importing ATRiAN components: {str(e)}")
    # Define mock classes for demonstration if imports fail
    class WindsurfOperationType(Enum):
        FILE_CREATION = "file_creation"
        CODE_GENERATION = "code_generation"
        AUTHENTICATION = "authentication"
        SYSTEM_CONFIG = "system_config"
    
    class ATRiANWindsurfAdapter:
        def __init__(self, config_path=None):
            pass
    
    class WindsurfMemoryAdapter:
        def __init__(self, backend=None, config_path=None):
            pass
    
    class LocalStorageBackend:
        def __init__(self, storage_dir=None):
            pass
    
    class PrivacySensitivity(Enum):
        LOW = 1
        MEDIUM = 2
        HIGH = 3
        CRITICAL = 4

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

def simulate_operations(adapter: ATRiANWindsurfAdapter, memory_adapter: WindsurfMemoryAdapter, user_id: str) -> None:
    """Simulate a series of operations to demonstrate memory integration."""
    print_section("Simulating Operations")
    
    # Define sample operations
    operations = [
        {
            "type": WindsurfOperationType.FILE_CREATION,
            "context": {
                "file_path": "C:\\Users\\user\\project\\main.py",
                "file_content": "print('Hello, World!')",
                "project_id": "sample_project"
            }
        },
        {
            "type": WindsurfOperationType.CODE_GENERATION,
            "context": {
                "prompt": "Generate a function to calculate factorial",
                "language": "python",
                "project_id": "sample_project"
            }
        },
        {
            "type": WindsurfOperationType.AUTHENTICATION,
            "context": {
                "username": "user@example.com",
                "password": "password123",  # This should be detected as sensitive
                "remember_me": True
            }
        },
        {
            "type": WindsurfOperationType.SYSTEM_CONFIG,
            "context": {
                "setting": "theme",
                "value": "dark",
                "persist": True
            }
        }
    ]
    
    # Simulate operations
    operation_ids = []
    for op in operations:
        print(f"Performing {op['type'].value} operation...")
        
        # Evaluate operation through ATRiAN adapter
        result = adapter.evaluate_operation(op["type"], op["context"], user_id)
        
        # Store operation in memory
        operation_id = memory_adapter.store_operation(
            user_id=user_id,
            operation_type=op["type"].value,
            context=op["context"],
            result=result
        )
        
        operation_ids.append(operation_id)
        print(f"  Operation ID: {operation_id}")
        
        # Simulate time passing between operations
        time.sleep(1)
    
    return operation_ids

def demonstrate_trust_score_management(memory_adapter: WindsurfMemoryAdapter, user_id: str) -> None:
    """Demonstrate trust score storage, retrieval, and decay."""
    print_section("Trust Score Management")
    
    # Store initial trust score
    initial_score = 0.8
    print(f"Storing initial trust score: {initial_score}")
    memory_adapter.store_trust_score(user_id, initial_score)
    
    # Retrieve trust score
    retrieved_score = memory_adapter.retrieve_trust_score(user_id)
    print(f"Retrieved trust score: {retrieved_score}")
    
    # Simulate time passing (trust decay)
    print("Simulating time passing to demonstrate trust decay...")
    
    # Hack the timestamp in the backend to simulate passage of time
    # In a real implementation, we would wait for actual time to pass
    key = memory_adapter._get_key("trust", user_id)
    _, metadata = memory_adapter.backend.retrieve(key)
    if metadata:
        # Set timestamp to 10 days ago
        past_date = datetime.now() - timedelta(days=10)
        metadata["timestamp"] = past_date.isoformat()
        memory_adapter.backend.store(key, retrieved_score, metadata)
        print(f"  Set last update timestamp to 10 days ago: {past_date.isoformat()}")
    
    # Retrieve trust score again (should be decayed)
    decayed_score = memory_adapter.retrieve_trust_score(user_id)
    print(f"Decayed trust score after 10 days: {decayed_score}")
    print(f"Decay amount: {initial_score - decayed_score:.4f}")

def demonstrate_context_retrieval(memory_adapter: WindsurfMemoryAdapter, user_id: str) -> None:
    """Demonstrate context retrieval for operations."""
    print_section("Context Retrieval")
    
    # Retrieve context for each operation type
    for op_type in [op_type.value for op_type in WindsurfOperationType]:
        print(f"Retrieving context for {op_type} operations...")
        context_items = memory_adapter.retrieve_context(user_id, op_type)
        
        print(f"  Found {len(context_items)} context items:")
        for i, item in enumerate(context_items):
            print(f"  {i+1}. Operation ID: {item.get('operation_id', 'unknown')}")
            print(f"     Timestamp: {item.get('timestamp', 'unknown')}")
            
            # Show context (but anonymize sensitive data for display)
            context = item.get("context", {})
            if "password" in str(context):
                print("     Context: [CONTAINS SENSITIVE DATA - ANONYMIZED]")
            else:
                print(f"     Context: {json.dumps(context, indent=2)[:100]}...")
            
            print()

def demonstrate_privacy_filtering(memory_adapter: WindsurfMemoryAdapter, user_id: str) -> None:
    """Demonstrate privacy filtering for sensitive data."""
    print_section("Privacy Filtering")
    
    # Create operation with sensitive data
    sensitive_context = {
        "credit_card": "4111-1111-1111-1111",
        "ssn": "123-45-6789",
        "email": "user@example.com",
        "notes": "This is a test with sensitive information"
    }
    
    print("Storing operation with sensitive data...")
    operation_id = memory_adapter.store_operation(
        user_id=user_id,
        operation_type="sensitive_test",
        context=sensitive_context,
        result={"status": "completed"}
    )
    
    # Retrieve the operation
    print("Retrieving operation with sensitive data...")
    operation = memory_adapter.retrieve_operation(user_id, operation_id)
    
    if operation:
        print("Retrieved operation:")
        print(f"  Operation ID: {operation.get('operation_id', 'unknown')}")
        print(f"  Original context contained: credit card, SSN, and email")
        print(f"  Stored context (should be anonymized):")
        print(f"  {json.dumps(operation.get('context', {}), indent=2)}")
    
    # Demonstrate clearing sensitive data
    print("\nClearing sensitive data...")
    cleared_count = memory_adapter.clear_sensitive_data(user_id, "sensitive_test")
    print(f"Cleared {cleared_count} sensitive data items")

def demonstrate_memory_statistics(memory_adapter: WindsurfMemoryAdapter, user_id: str) -> None:
    """Demonstrate memory usage statistics."""
    print_section("Memory Statistics")
    
    # Get statistics
    stats = memory_adapter.get_stats(user_id)
    
    print("Memory usage statistics:")
    print(f"  Total items: {stats['total_items']}")
    print(f"  Operation count: {stats['operation_count']}")
    print(f"  Trust score count: {stats['trust_score_count']}")
    print(f"  History count: {stats['history_count']}")
    print("  Sensitivity breakdown:")
    for level, count in stats['by_sensitivity'].items():
        print(f"    {level}: {count}")

def run_demo():
    """Run the ATRiAN memory integration demonstration."""
    print_banner("ATRiAN Windsurf Memory Integration Demo")
    
    # Create a temporary directory for the demo
    demo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_data")
    os.makedirs(demo_dir, exist_ok=True)
    
    # Initialize components
    print("Initializing ATRiAN components...")
    
    # --- Backend Configuration ---
    API_BASE_URL = "http://localhost:8000/api/v1/atrian"  # Placeholder - CHANGE IF NEEDED
    API_KEY = None  # Placeholder - CHANGE IF NEEDED

    backend = None
    try:
        logger.info(f"Attempting to initialize WindsurfAPIBackend with base URL: {API_BASE_URL}")
        api_backend = WindsurfAPIBackend(api_base_url=API_BASE_URL, api_key=API_KEY)
        if api_backend._check_api_connection(): # Check connection status
            backend = api_backend
            logger.info("Successfully initialized and connected to WindsurfAPIBackend.")
        else:
            logger.warning("WindsurfAPIBackend initialized but failed health check. Falling back to LocalStorageBackend.")
            backend = None # Explicitly set to None to trigger fallback
    except Exception as e:
        logger.error(f"Failed to initialize WindsurfAPIBackend: {str(e)}. Falling back to LocalStorageBackend.")
        backend = None

    if backend is None:
        logger.info("Initializing LocalStorageBackend as fallback.")
        backend = LocalStorageBackend(storage_dir=demo_dir)
    # --- End Backend Configuration ---
    
    # Create memory adapter
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    memory_adapter = WindsurfMemoryAdapter(backend=backend, config_path=config_path)
    
    # Create ATRiAN adapter
    atrian_adapter = ATRiANWindsurfAdapter()
    
    # Set user ID for demo
    user_id = "demo_user"
    
    # Run demonstration scenarios
    try:
        # Simulate operations
        operation_ids = simulate_operations(atrian_adapter, memory_adapter, user_id)
        
        # Demonstrate trust score management
        demonstrate_trust_score_management(memory_adapter, user_id)
        
        # Demonstrate context retrieval
        demonstrate_context_retrieval(memory_adapter, user_id)
        
        # Demonstrate privacy filtering
        demonstrate_privacy_filtering(memory_adapter, user_id)
        
        # Demonstrate memory statistics
        demonstrate_memory_statistics(memory_adapter, user_id)
        
        print_banner("Demo Completed Successfully")
        print("The ATRiAN Windsurf Memory Adapter has been demonstrated successfully.")
        print("You can find the stored data in the 'demo_data' directory.")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"\nError during demonstration: {str(e)}")
    
    print("\nTo clean up the demo data, delete the 'demo_data' directory.")

if __name__ == "__main__":
    try:
        # Configure detailed logging for diagnostics
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("debug_memory_integration.log"),
                logging.StreamHandler()
            ]
        )
        logger.info("Starting ATRiAN memory integration demo with enhanced diagnostics")
        run_demo()
    except Exception as e:
        logger.error(f"Error in demo execution: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\nERROR: {str(e)}\n")
        print("Full traceback has been saved to debug_memory_integration.log")
        print("Please check this file for detailed error information.")