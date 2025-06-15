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

# - @references {C:\\EGOS\\ATRiAN\\atrian_windsurf_adapter.py}
# - @references {C:\\EGOS\\ATRiAN\\atrian_trust_weaver.py}
# - @references {C:\\EGOS\\ATRiAN\\atrian_ethical_compass.py}
# --- 

import os
import sys
import json
import logging
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ATRiAN components
try:
    from memory.windsurf_memory_adapter import (
        WindsurfMemoryAdapter, 
        LocalStorageBackend,
        PrivacySensitivity
    )
    from atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType
    from atrian_trust_weaver import WeaverOfTrust
    from atrian_ethical_compass import EthicalCompass
    from atrian_ethics_trust_integration import EthicsTrustIntegration
except ImportError as e:
    # Define mock classes for testing
    print(f"Error importing ATRiAN components: {str(e)}")
    print("Using mock classes for testing...")
    
    class WindsurfOperationType(Enum):
        FILE_CREATION = "file_creation"
        CODE_GENERATION = "code_generation"
        AUTHENTICATION = "authentication"
        SYSTEM_CONFIG = "system_config"
    
    class ATRiANWindsurfAdapter:
        def __init__(self, memory_adapter=None, config_path=None):
            self.memory_adapter = memory_adapter
            self.trust_weaver = WeaverOfTrust()
            self.ethical_compass = EthicalCompass()
            self.ethics_trust_integration = EthicsTrustIntegration(
                self.ethical_compass, self.trust_weaver
            )
        
        def evaluate_operation(self, operation_type, context, user_id):
            operation_id = f"{operation_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Get trust score from memory or use default
            trust_score = 0.7
            if self.memory_adapter:
                stored_score = self.memory_adapter.retrieve_trust_score(user_id)
                if stored_score is not None:
                    trust_score = stored_score
            
            # Get past context from memory
            past_context = []
            if self.memory_adapter:
                past_context = self.memory_adapter.retrieve_context(
                    user_id, operation_type.value
                )
            
            # Evaluate operation
            result = {
                "operation_id": operation_id,
                "user_id": user_id,
                "operation_type": operation_type.value,
                "timestamp": datetime.now().isoformat(),
                "allowed": True,
                "trust_score": trust_score,
                "past_context": past_context
            }
            
            # Store operation in memory
            if self.memory_adapter:
                self.memory_adapter.store_operation(
                    user_id, operation_type.value, context, result
                )
            
            return result
    
    class WeaverOfTrust:
        def __init__(self):
            self.trust_scores = {}
        
        def get_trust_score(self, agent_id):
            return self.trust_scores.get(agent_id, 0.7)
        
        def update_trust_score(self, agent_id, event_type, outcome, magnitude=0.1):
            current_score = self.get_trust_score(agent_id)
            
            if outcome == "positive":
                new_score = min(1.0, current_score + magnitude)
            else:
                new_score = max(0.0, current_score - magnitude)
            
            self.trust_scores[agent_id] = new_score
            return new_score
    
    class EthicalCompass:
        def __init__(self, rules_filepath=None):
            pass
        
        def evaluate_action(self, action_context):
            return {"allowed": True, "reasoning": "Mock evaluation"}
    
    class EthicsTrustIntegration:
        def __init__(self, ethical_compass, trust_weaver):
            self.ethical_compass = ethical_compass
            self.trust_weaver = trust_weaver
        
        def evaluate_with_trust(self, action_context, agent_id):
            trust_score = self.trust_weaver.get_trust_score(agent_id)
            evaluation = self.ethical_compass.evaluate_action(action_context)
            
            return {
                "allowed": evaluation["allowed"],
                "reasoning": evaluation["reasoning"],
                "trust_score": trust_score
            }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_memory_adapter_integration")

class MemoryAdapterIntegrationTest(unittest.TestCase):
    """Test suite for validating memory adapter integration with ATRiAN components."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a backend with the temporary directory
        self.backend = LocalStorageBackend(storage_dir=self.test_dir)
        
        # Create a memory adapter with the test backend
        self.memory_adapter = WindsurfMemoryAdapter(backend=self.backend)
        
        # Create an ATRiAN adapter with the memory adapter
        self.atrian_adapter = ATRiANWindsurfAdapter(memory_adapter=self.memory_adapter)
        
        # Test user ID
        self.test_user = "test_user"
        
        logger.info(f"Test environment set up with temporary directory: {self.test_dir}")
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        logger.info("Test environment cleaned up")
    
    def test_trust_score_persistence(self):
        """Test that trust scores are persisted through the memory adapter."""
        # Set initial trust score
        initial_score = 0.8
        self.memory_adapter.store_trust_score(self.test_user, initial_score)
        
        # Verify trust score is stored
        stored_score = self.memory_adapter.retrieve_trust_score(self.test_user)
        self.assertEqual(stored_score, initial_score, "Trust score should be stored correctly")
        
        # Perform an operation that affects trust
        context = {"file_path": "/path/to/file.txt", "content": "print('Hello, World!')"}
        result = self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, context, self.test_user
        )
        
        # Verify trust score is used in operation evaluation
        self.assertEqual(result["trust_score"], initial_score, 
                        "Operation evaluation should use stored trust score")
        
        # Update trust score through adapter
        new_score = 0.9
        self.memory_adapter.store_trust_score(self.test_user, new_score)
        
        # Perform another operation
        context = {"prompt": "Generate a function to calculate factorial", "language": "python"}
        result = self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.CODE_GENERATION, context, self.test_user
        )
        
        # Verify updated trust score is used
        self.assertEqual(result["trust_score"], new_score, 
                        "Operation evaluation should use updated trust score")
    
    def test_operation_history_persistence(self):
        """Test that operation history is persisted through the memory adapter."""
        # Perform a series of operations
        operations = [
            {
                "type": WindsurfOperationType.FILE_CREATION,
                "context": {"file_path": "/path/to/file1.txt", "content": "File 1 content"}
            },
            {
                "type": WindsurfOperationType.FILE_CREATION,
                "context": {"file_path": "/path/to/file2.txt", "content": "File 2 content"}
            },
            {
                "type": WindsurfOperationType.CODE_GENERATION,
                "context": {"prompt": "Generate a function", "language": "python"}
            }
        ]
        
        for op in operations:
            self.atrian_adapter.evaluate_operation(op["type"], op["context"], self.test_user)
        
        # Retrieve context for file creation operations
        context_items = self.memory_adapter.retrieve_context(
            self.test_user, WindsurfOperationType.FILE_CREATION.value
        )
        
        # Verify context items
        self.assertEqual(len(context_items), 2, "Should retrieve 2 file creation operations")
        
        # Verify context content
        file_paths = [item["context"]["file_path"] for item in context_items]
        self.assertIn("/path/to/file1.txt", file_paths, "Should contain file1.txt operation")
        self.assertIn("/path/to/file2.txt", file_paths, "Should contain file2.txt operation")
        
        # Retrieve context for code generation operations
        context_items = self.memory_adapter.retrieve_context(
            self.test_user, WindsurfOperationType.CODE_GENERATION.value
        )
        
        # Verify context items
        self.assertEqual(len(context_items), 1, "Should retrieve 1 code generation operation")
        self.assertEqual(context_items[0]["context"]["language"], "python", 
                        "Should contain correct operation context")
    
    def test_context_retrieval_for_evaluation(self):
        """Test that past context is retrieved for operation evaluation."""
        # Perform initial operation
        initial_context = {"file_path": "/path/to/file.txt", "content": "Initial content"}
        self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, initial_context, self.test_user
        )
        
        # Perform second operation of same type
        second_context = {"file_path": "/path/to/file.txt", "content": "Updated content"}
        result = self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, second_context, self.test_user
        )
        
        # Verify past context is included
        self.assertIsNotNone(result.get("past_context"), "Past context should be included in result")
        self.assertGreater(len(result["past_context"]), 0, "Past context should not be empty")
        
        # Verify past context content
        past_context = result["past_context"][0]
        self.assertEqual(past_context["context"]["file_path"], initial_context["file_path"],
                        "Past context should contain correct file path")
        self.assertEqual(past_context["context"]["content"], initial_context["content"],
                        "Past context should contain correct content")
    
    def test_privacy_filtering_in_integration(self):
        """Test that privacy filtering works in the integration flow."""
        # Perform operation with sensitive data
        sensitive_context = {
            "username": "testuser",
            "password": "password123",
            "remember_me": True
        }
        
        result = self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.AUTHENTICATION, sensitive_context, self.test_user
        )
        
        # Retrieve operation from memory
        context_items = self.memory_adapter.retrieve_context(
            self.test_user, WindsurfOperationType.AUTHENTICATION.value
        )
        
        # Verify privacy filtering
        self.assertGreater(len(context_items), 0, "Should retrieve authentication operation")
        stored_context = context_items[0]["context"]
        
        # Password should be anonymized
        self.assertNotEqual(stored_context.get("password"), sensitive_context["password"],
                          "Password should be anonymized in stored context")
        
        # Non-sensitive data should be preserved
        self.assertEqual(stored_context.get("username"), sensitive_context["username"],
                        "Username should be preserved in stored context")
        self.assertEqual(stored_context.get("remember_me"), sensitive_context["remember_me"],
                        "remember_me flag should be preserved in stored context")
    
    def test_multiple_users_isolation(self):
        """Test that data from different users is properly isolated."""
        # Create two test users
        user1 = "test_user_1"
        user2 = "test_user_2"
        
        # Set different trust scores
        self.memory_adapter.store_trust_score(user1, 0.8)
        self.memory_adapter.store_trust_score(user2, 0.6)
        
        # Perform operations for each user
        context1 = {"file_path": "/path/to/user1_file.txt", "content": "User 1 content"}
        context2 = {"file_path": "/path/to/user2_file.txt", "content": "User 2 content"}
        
        self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, context1, user1
        )
        
        self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, context2, user2
        )
        
        # Verify trust scores are isolated
        self.assertEqual(self.memory_adapter.retrieve_trust_score(user1), 0.8,
                        "User 1 trust score should be preserved")
        self.assertEqual(self.memory_adapter.retrieve_trust_score(user2), 0.6,
                        "User 2 trust score should be preserved")
        
        # Verify operation history is isolated
        context_items1 = self.memory_adapter.retrieve_context(
            user1, WindsurfOperationType.FILE_CREATION.value
        )
        
        context_items2 = self.memory_adapter.retrieve_context(
            user2, WindsurfOperationType.FILE_CREATION.value
        )
        
        # Check user 1 context
        self.assertEqual(len(context_items1), 1, "User 1 should have 1 operation")
        self.assertEqual(context_items1[0]["context"]["file_path"], context1["file_path"],
                        "User 1 context should contain correct file path")
        
        # Check user 2 context
        self.assertEqual(len(context_items2), 1, "User 2 should have 1 operation")
        self.assertEqual(context_items2[0]["context"]["file_path"], context2["file_path"],
                        "User 2 context should contain correct file path")
    
    def test_context_relevance_scoring(self):
        """Test that context relevance scoring works correctly."""
        # Enable context relevance scoring
        self.memory_adapter.config["enable_context_relevance"] = True
        self.memory_adapter.config["context_relevance_threshold"] = 0.3
        
        # Perform a series of operations with different timestamps
        operations = [
            # Recent operation (high relevance)
            {
                "type": WindsurfOperationType.FILE_CREATION,
                "context": {"file_path": "/path/to/recent.txt", "content": "Recent content"}
            },
            # Older operation (medium relevance)
            {
                "type": WindsurfOperationType.FILE_CREATION,
                "context": {"file_path": "/path/to/older.txt", "content": "Older content"}
            },
            # Very old operation (low relevance)
            {
                "type": WindsurfOperationType.FILE_CREATION,
                "context": {"file_path": "/path/to/oldest.txt", "content": "Oldest content"}
            }
        ]
        
        # Store operations with different timestamps
        for i, op in enumerate(operations):
            op_id = self.memory_adapter.store_operation(
                user_id=self.test_user,
                operation_type=op["type"].value,
                context=op["context"],
                result={"status": "success"}
            )
            
            # Manipulate timestamp for testing
            if i > 0:
                key = self.memory_adapter._get_key("operation", self.test_user, op_id)
                operation, metadata = self.backend.retrieve(key)
                
                # Set timestamp to the past
                days_ago = i * 10  # 0, 10, 20 days ago
                past_time = datetime.now() - timedelta(days=days_ago)
                metadata["timestamp"] = past_time.isoformat()
                self.backend.store(key, operation, metadata)
        
        # Retrieve context with relevance scoring
        context_items = self.memory_adapter.retrieve_context(
            self.test_user, WindsurfOperationType.FILE_CREATION.value
        )
        
        # Verify context items are ordered by relevance
        self.assertGreaterEqual(len(context_items), 2, "Should retrieve at least 2 operations")
        
        # First item should be the most recent (highest relevance)
        self.assertEqual(context_items[0]["context"]["file_path"], "/path/to/recent.txt",
                        "Most recent operation should have highest relevance")
        
        # If we have 3 items, the last should be the oldest
        if len(context_items) >= 3:
            self.assertNotEqual(context_items[-1]["context"]["file_path"], "/path/to/recent.txt",
                              "Oldest operation should have lowest relevance")
    
    def test_trust_decay_integration(self):
        """Test that trust decay works in the integration flow."""
        # Enable trust decay
        self.memory_adapter.config["enable_trust_decay"] = True
        self.memory_adapter.config["trust_decay_rate"] = 0.1  # 10% decay per day
        
        # Set initial trust score
        initial_score = 0.9
        self.memory_adapter.store_trust_score(self.test_user, initial_score)
        
        # Manipulate timestamp to simulate passage of time
        key = self.memory_adapter._get_key("trust", self.test_user)
        _, metadata = self.backend.retrieve(key)
        if metadata:
            # Set timestamp to 5 days ago
            past_date = datetime.now() - timedelta(days=5)
            metadata["timestamp"] = past_date.isoformat()
            self.backend.store(key, initial_score, metadata)
        
        # Perform an operation to trigger trust score retrieval with decay
        context = {"file_path": "/path/to/file.txt", "content": "File content"}
        result = self.atrian_adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, context, self.test_user
        )
        
        # Calculate expected decay
        # Formula: score * (1 - decay_rate)^days
        expected_decay = initial_score * ((1 - 0.1) ** 5)
        expected_score = max(0.3, expected_decay)  # Minimum threshold is 0.3
        
        # Verify trust score is decayed
        self.assertLess(result["trust_score"], initial_score, 
                       "Trust score should be decayed after 5 days")
        self.assertAlmostEqual(result["trust_score"], expected_score, places=2,
                              "Trust score should be decayed by the correct amount")
        
        # Verify trust score is updated in memory
        updated_score = self.memory_adapter.retrieve_trust_score(self.test_user)
        self.assertAlmostEqual(updated_score, expected_score, places=2,
                              "Updated trust score should be stored in memory")

def run_tests():
    """Run the memory adapter integration tests and generate a report."""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(MemoryAdapterIntegrationTest)
    
    # Run tests
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Print summary
    print("\n=== Memory Adapter Integration Test Summary ===")
    print(f"Tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    print(f"Skipped: {len(test_result.skipped)}")
    
    # Return success status
    return len(test_result.failures) == 0 and len(test_result.errors) == 0

if __name__ == "__main__":
    run_tests()