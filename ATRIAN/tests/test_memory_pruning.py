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

# - @references {C:\\EGOS\\ATRiAN\\memory\\windsurf_memory_adapter.py}
# - @references {C:\\EGOS\\ATRiAN\\tests\\test_memory_integration.py}
# - @references {C:\\EGOS\\ATRiAN\\memory\\demo_memory_integration.py}
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

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ATRiAN components
try:
    from memory.windsurf_memory_adapter import (
        WindsurfMemoryAdapter, 
        LocalStorageBackend,
        PrivacySensitivity,
        PrivacyFilter
    )
except ImportError as e:
    print(f"Error importing ATRiAN components: {str(e)}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_memory_pruning")

class MemoryPruningTest(unittest.TestCase):
    """Test suite for validating memory pruning functionality."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a backend with the temporary directory
        self.backend = LocalStorageBackend(storage_dir=self.test_dir)
        
        # Create a memory adapter with the test backend
        self.memory_adapter = WindsurfMemoryAdapter(backend=self.backend)
        
        # Test user ID
        self.test_user = "test_user"
        
        # Override retention policies for testing
        self.memory_adapter.privacy_filter.retention_policies = {
            PrivacySensitivity.LOW: timedelta(days=30),
            PrivacySensitivity.MEDIUM: timedelta(days=7),
            PrivacySensitivity.HIGH: timedelta(days=1),
            PrivacySensitivity.CRITICAL: timedelta(hours=1)
        }
        
        logger.info(f"Test environment set up with temporary directory: {self.test_dir}")
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        logger.info("Test environment cleaned up")
    
    def _create_test_operations(self, count=10, sensitivity_distribution=None):
        """Create test operations with different sensitivity levels.
        
        Args:
            count (int): Number of operations to create
            sensitivity_distribution (Dict[PrivacySensitivity, float], optional): 
                Distribution of sensitivity levels (e.g., {LOW: 0.5, MEDIUM: 0.3, HIGH: 0.15, CRITICAL: 0.05})
                
        Returns:
            List[str]: List of operation IDs
        """
        # Default distribution if not provided
        if sensitivity_distribution is None:
            sensitivity_distribution = {
                PrivacySensitivity.LOW: 0.5,
                PrivacySensitivity.MEDIUM: 0.3,
                PrivacySensitivity.HIGH: 0.15,
                PrivacySensitivity.CRITICAL: 0.05
            }
        
        # Sample data for different sensitivity levels
        sample_data = {
            PrivacySensitivity.LOW: {
                "operation_type": "view_file",
                "context": {"file_path": "/path/to/file.txt", "read_only": True}
            },
            PrivacySensitivity.MEDIUM: {
                "operation_type": "user_preference",
                "context": {"setting": "theme", "value": "dark", "personal": True}
            },
            PrivacySensitivity.HIGH: {
                "operation_type": "profile_update",
                "context": {"email": "user@example.com", "address": "123 Main St"}
            },
            PrivacySensitivity.CRITICAL: {
                "operation_type": "authentication",
                "context": {"username": "testuser", "password": "password123"}
            }
        }
        
        operation_ids = []
        
        # Create operations based on distribution
        for i in range(count):
            # Determine sensitivity level
            import random
            rand_val = random.random()
            cumulative = 0
            selected_sensitivity = PrivacySensitivity.LOW
            
            for sensitivity, probability in sensitivity_distribution.items():
                cumulative += probability
                if rand_val <= cumulative:
                    selected_sensitivity = sensitivity
                    break
            
            # Get sample data for selected sensitivity
            data = sample_data[selected_sensitivity]
            
            # Add some uniqueness
            data["context"]["timestamp"] = datetime.now().isoformat()
            data["context"]["operation_number"] = i
            
            # Store operation
            operation_id = self.memory_adapter.store_operation(
                user_id=self.test_user,
                operation_type=data["operation_type"],
                context=data["context"],
                result={"status": "success"}
            )
            
            operation_ids.append(operation_id)
            
            # For testing, directly manipulate metadata to set sensitivity
            key = self.memory_adapter._get_key("operation", self.test_user, operation_id)
            _, metadata = self.backend.retrieve(key)
            if metadata:
                metadata["sensitivity"] = selected_sensitivity.value
                self.backend.store(key, self.memory_adapter.retrieve_operation(self.test_user, operation_id), metadata)
        
        return operation_ids
    
    def _manipulate_timestamps(self, operation_ids, age_distribution):
        """Manipulate timestamps for testing pruning.
        
        Args:
            operation_ids (List[str]): List of operation IDs
            age_distribution (Dict[str, timedelta]): How to age different operations
        """
        for op_id, age in zip(operation_ids, age_distribution):
            key = self.memory_adapter._get_key("operation", self.test_user, op_id)
            operation, metadata = self.backend.retrieve(key)
            
            if metadata and "timestamp" in metadata:
                # Set timestamp to the past
                past_time = datetime.now() - age
                metadata["timestamp"] = past_time.isoformat()
                self.backend.store(key, operation, metadata)
    
    def test_prune_expired_data(self):
        """Test pruning of expired data based on retention policies."""
        # Create test operations
        operation_ids = self._create_test_operations(count=20)
        
        # Get initial count
        initial_stats = self.memory_adapter.get_stats(self.test_user)
        initial_count = initial_stats["operation_count"]
        
        # Manipulate timestamps to simulate aging
        age_distribution = [
            timedelta(days=0),      # Fresh
            timedelta(days=2),      # 2 days old
            timedelta(days=10),     # 10 days old
            timedelta(days=40),     # 40 days old
            timedelta(days=0),      # Fresh
            timedelta(hours=2),     # 2 hours old
            timedelta(days=5),      # 5 days old
            timedelta(days=15),     # 15 days old
            timedelta(minutes=30),  # 30 minutes old
            timedelta(days=3),      # 3 days old
            timedelta(days=0),      # Fresh
            timedelta(days=2),      # 2 days old
            timedelta(days=10),     # 10 days old
            timedelta(days=40),     # 40 days old
            timedelta(days=0),      # Fresh
            timedelta(hours=2),     # 2 hours old
            timedelta(days=5),      # 5 days old
            timedelta(days=15),     # 15 days old
            timedelta(minutes=30),  # 30 minutes old
            timedelta(days=3),      # 3 days old
        ]
        
        self._manipulate_timestamps(operation_ids, age_distribution)
        
        # Run pruning
        pruned_count = self.memory_adapter.prune_expired_data()
        
        # Get final count
        final_stats = self.memory_adapter.get_stats(self.test_user)
        final_count = final_stats["operation_count"]
        
        # Verify pruning
        self.assertGreater(pruned_count, 0, "Should have pruned some data")
        self.assertEqual(initial_count - pruned_count, final_count, 
                        "Final count should equal initial count minus pruned count")
        
        logger.info(f"Pruned {pruned_count} items out of {initial_count}")
    
    def test_retention_policies(self):
        """Test that different sensitivity levels have different retention periods."""
        # Create one operation of each sensitivity level
        operations = {}
        
        for sensitivity in PrivacySensitivity:
            # Create context based on sensitivity
            if sensitivity == PrivacySensitivity.LOW:
                context = {"type": "view", "file": "document.txt"}
            elif sensitivity == PrivacySensitivity.MEDIUM:
                context = {"type": "preference", "personal": True}
            elif sensitivity == PrivacySensitivity.HIGH:
                context = {"type": "profile", "email": "user@example.com"}
            else:  # CRITICAL
                context = {"type": "auth", "password": "secret123"}
            
            # Store operation
            op_id = self.memory_adapter.store_operation(
                user_id=self.test_user,
                operation_type=f"test_{sensitivity.name.lower()}",
                context=context,
                result={"status": "success"}
            )
            
            # Override sensitivity directly in metadata
            key = self.memory_adapter._get_key("operation", self.test_user, op_id)
            operation, metadata = self.backend.retrieve(key)
            metadata["sensitivity"] = sensitivity.value
            self.backend.store(key, operation, metadata)
            
            operations[sensitivity] = op_id
        
        # Set all operations to be just past their retention period
        for sensitivity, op_id in operations.items():
            key = self.memory_adapter._get_key("operation", self.test_user, op_id)
            operation, metadata = self.backend.retrieve(key)
            
            # Get retention period and add a small buffer
            retention_period = self.memory_adapter.privacy_filter.retention_policies[sensitivity]
            past_time = datetime.now() - (retention_period + timedelta(minutes=5))
            
            # Update timestamp
            metadata["timestamp"] = past_time.isoformat()
            self.backend.store(key, operation, metadata)
        
        # Run pruning
        pruned_count = self.memory_adapter.prune_expired_data()
        
        # All operations should be pruned
        self.assertEqual(pruned_count, len(operations), 
                        f"Should have pruned all {len(operations)} operations")
        
        # Verify each operation is gone
        for sensitivity, op_id in operations.items():
            operation = self.memory_adapter.retrieve_operation(self.test_user, op_id)
            self.assertIsNone(operation, f"Operation with {sensitivity} sensitivity should be pruned")
    
    def test_should_retain_function(self):
        """Test the should_retain function of the privacy filter."""
        privacy_filter = self.memory_adapter.privacy_filter
        
        # Test retention for different sensitivity levels and ages
        test_cases = [
            # (sensitivity, age_days, should_retain)
            (PrivacySensitivity.LOW, 15, True),      # 15 days old, LOW sensitivity (30 day retention)
            (PrivacySensitivity.LOW, 40, False),     # 40 days old, LOW sensitivity (30 day retention)
            (PrivacySensitivity.MEDIUM, 5, True),    # 5 days old, MEDIUM sensitivity (7 day retention)
            (PrivacySensitivity.MEDIUM, 10, False),  # 10 days old, MEDIUM sensitivity (7 day retention)
            (PrivacySensitivity.HIGH, 0.5, True),    # 12 hours old, HIGH sensitivity (1 day retention)
            (PrivacySensitivity.HIGH, 2, False),     # 2 days old, HIGH sensitivity (1 day retention)
            (PrivacySensitivity.CRITICAL, 0.02, True),  # 30 minutes old, CRITICAL sensitivity (1 hour retention)
            (PrivacySensitivity.CRITICAL, 0.05, False)  # 1.2 hours old, CRITICAL sensitivity (1 hour retention)
        ]
        
        for sensitivity, age_days, expected_result in test_cases:
            # Calculate timestamp
            timestamp = datetime.now() - timedelta(days=age_days)
            
            # Test retention
            result = privacy_filter.should_retain(sensitivity, timestamp)
            
            self.assertEqual(result, expected_result, 
                           f"should_retain({sensitivity}, {age_days} days ago) should be {expected_result}")
    
    def test_pruning_updates_history(self):
        """Test that pruning updates the operation history."""
        # Create test operations
        operation_ids = self._create_test_operations(count=5)
        
        # Get initial history
        history_key = self.memory_adapter._get_key("history", self.test_user)
        initial_history, _ = self.backend.retrieve(history_key)
        
        # Make all operations expired
        for op_id in operation_ids:
            key = self.memory_adapter._get_key("operation", self.test_user, op_id)
            operation, metadata = self.backend.retrieve(key)
            
            # Set timestamp to the distant past
            past_time = datetime.now() - timedelta(days=100)
            metadata["timestamp"] = past_time.isoformat()
            self.backend.store(key, operation, metadata)
        
        # Run pruning
        pruned_count = self.memory_adapter.prune_expired_data()
        
        # Get updated history
        updated_history, _ = self.backend.retrieve(history_key)
        
        # Verify history was updated
        self.assertEqual(pruned_count, len(operation_ids), 
                        f"Should have pruned all {len(operation_ids)} operations")
        
        if initial_history and "operations" in initial_history:
            initial_op_count = len(initial_history["operations"])
            updated_op_count = len(updated_history["operations"]) if updated_history and "operations" in updated_history else 0
            
            self.assertEqual(updated_op_count, initial_op_count - pruned_count,
                           "History should be updated to remove pruned operations")
            
            # Verify pruned operations are not in history
            if updated_history and "operations" in updated_history:
                for op_id in operation_ids:
                    for op in updated_history["operations"]:
                        self.assertNotEqual(op["id"], op_id, 
                                         f"Pruned operation {op_id} should not be in history")

def run_tests():
    """Run the memory pruning tests and generate a report."""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(MemoryPruningTest)
    
    # Run tests
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Print summary
    print("\n=== Memory Pruning Test Summary ===")
    print(f"Tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    print(f"Skipped: {len(test_result.skipped)}")
    
    # Return success status
    return len(test_result.failures) == 0 and len(test_result.errors) == 0

if __name__ == "__main__":
    run_tests()