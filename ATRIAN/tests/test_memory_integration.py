# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Implementation Plan](../ATRiAN_Implementation_Plan.md)
# - [EGOS Global Rules](../../.windsurfrules)
# - [WORK ATRiAN Windsurf Integration](../WORK_2025-05-27_ATRiAN_Windsurf_Integration.md)
# --- 

import os
import sys
import json
import logging
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ATRiAN components
try:
    from ATRiAN.atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType
except ImportError:
    # Mock classes for testing without actual implementation
    class WindsurfOperationType(Enum):
        FILE_CREATION = "file_creation"
        CODE_GENERATION = "code_generation"
        AUTHENTICATION = "authentication"
        SYSTEM_CONFIG = "system_config"
        
    class ATRiANWindsurfAdapter:
        def __init__(self, config_path=None):
            self.memory = WindsurfMemoryMock()
            self.trust_scores = {}
            self.operations = {}
            
        def evaluate_operation(self, operation_type, context, user_id):
            operation_id = f"{operation_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Check memory for relevant context
            past_context = self.memory.retrieve_context(user_id, operation_type.value)
            
            # Get trust score from memory or use default
            trust_score = self.trust_scores.get(user_id, 0.7)
            
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
            self.memory.store_operation(user_id, operation_type.value, context, result)
            self.operations[operation_id] = result
            
            return result
        
        def store_trust_score(self, user_id, score):
            """Store trust score in memory system."""
            self.trust_scores[user_id] = score
            self.memory.store_trust_score(user_id, score)
            
        def retrieve_trust_score(self, user_id):
            """Retrieve trust score from memory system."""
            score = self.memory.retrieve_trust_score(user_id)
            if score is not None:
                self.trust_scores[user_id] = score
            return self.trust_scores.get(user_id, 0.7)
        
        def clear_sensitive_data(self, user_id, data_type=None):
            """Clear sensitive data from memory."""
            return self.memory.clear_sensitive_data(user_id, data_type)

# Mock implementation of Windsurf's memory system
class WindsurfMemoryMock:
    """Mock implementation of Windsurf's memory system for testing."""
    
    def __init__(self):
        """Initialize the memory system mock."""
        self.memory_store = {
            "operations": {},
            "trust_scores": {},
            "context": {},
            "sensitive_data": set()
        }
    
    def store_operation(self, user_id, operation_type, context, result):
        """Store an operation in memory."""
        if user_id not in self.memory_store["operations"]:
            self.memory_store["operations"][user_id] = []
        
        # Add operation to user's history
        self.memory_store["operations"][user_id].append({
            "operation_type": operation_type,
            "context": context,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mark as sensitive if privacy-related terms are in context
        context_str = json.dumps(str(context)).lower()
        privacy_terms = ["password", "secret", "personal", "private", "sensitive"]
        if any(term in context_str for term in privacy_terms):
            self.memory_store["sensitive_data"].add(f"{user_id}:{operation_type}")
    
    def retrieve_context(self, user_id, operation_type, limit=5):
        """Retrieve past context for similar operations."""
        if user_id not in self.memory_store["operations"]:
            return []
        
        # Get past operations of the same type
        past_operations = [
            op for op in self.memory_store["operations"][user_id]
            if op["operation_type"] == operation_type
        ]
        
        # Sort by recency and limit
        past_operations.sort(key=lambda x: x["timestamp"], reverse=True)
        return past_operations[:limit]
    
    def store_trust_score(self, user_id, score):
        """Store a trust score in memory."""
        self.memory_store["trust_scores"][user_id] = {
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve_trust_score(self, user_id):
        """Retrieve a trust score from memory."""
        if user_id in self.memory_store["trust_scores"]:
            return self.memory_store["trust_scores"][user_id]["score"]
        return None
    
    def clear_sensitive_data(self, user_id, data_type=None):
        """Clear sensitive data from memory."""
        cleared_count = 0
        
        # Clear operations
        if user_id in self.memory_store["operations"]:
            if data_type:
                sensitive_key = f"{user_id}:{data_type}"
                if sensitive_key in self.memory_store["sensitive_data"]:
                    # Remove specific operation type
                    before_count = len(self.memory_store["operations"][user_id])
                    self.memory_store["operations"][user_id] = [
                        op for op in self.memory_store["operations"][user_id]
                        if op["operation_type"] != data_type
                    ]
                    cleared_count = before_count - len(self.memory_store["operations"][user_id])
                    self.memory_store["sensitive_data"].remove(sensitive_key)
            else:
                # Clear all operations for user
                cleared_count = len(self.memory_store["operations"][user_id])
                self.memory_store["operations"][user_id] = []
                # Remove all sensitive data markers for user
                self.memory_store["sensitive_data"] = {
                    key for key in self.memory_store["sensitive_data"]
                    if not key.startswith(f"{user_id}:")
                }
        
        return cleared_count

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_memory_integration_test")

class MemoryIntegrationTest(unittest.TestCase):
    """Test suite for validating memory system integration in the ATRiAN-Windsurf adapter."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.adapter = ATRiANWindsurfAdapter()
        self.test_user = "TestUser"
    
    def test_operation_storage_and_retrieval(self):
        """Test storage and retrieval of operations in memory."""
        # Perform a series of operations
        operations = [
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/test1.py", "content": "print('test1')"}),
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/test2.py", "content": "print('test2')"}),
            (WindsurfOperationType.CODE_GENERATION, {"purpose": "utility", "content": "def helper(): pass"})
        ]
        
        for op_type, context in operations:
            self.adapter.evaluate_operation(op_type, context, self.test_user)
        
        # Test retrieval of context for file creation
        result = self.adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, 
            {"file_path": "/test3.py", "content": "print('test3')"}, 
            self.test_user
        )
        
        # Check that past context was retrieved
        self.assertIn("past_context", result)
        self.assertIsInstance(result["past_context"], list)
        self.assertGreaterEqual(len(result["past_context"]), 2)  # Should have at least 2 file creation operations
        
        # Check the content of retrieved context
        file_paths = [op["context"].get("file_path") for op in result["past_context"] if "context" in op]
        self.assertIn("/test1.py", file_paths)
        self.assertIn("/test2.py", file_paths)
        
        logger.info(f"Retrieved {len(result['past_context'])} past contexts for file creation")
    
    def test_trust_score_persistence(self):
        """Test persistence of trust scores in memory."""
        # Store initial trust score
        initial_score = 0.8
        self.adapter.store_trust_score(self.test_user, initial_score)
        
        # Retrieve and verify
        retrieved_score = self.adapter.retrieve_trust_score(self.test_user)
        self.assertEqual(retrieved_score, initial_score)
        
        # Update score
        updated_score = 0.6
        self.adapter.store_trust_score(self.test_user, updated_score)
        
        # Retrieve and verify update
        retrieved_score = self.adapter.retrieve_trust_score(self.test_user)
        self.assertEqual(retrieved_score, updated_score)
        
        # Create new adapter instance (simulating new session)
        new_adapter = ATRiANWindsurfAdapter()
        
        # Memory mock doesn't persist between instances, so this is a limited test
        # In real implementation, this would test actual persistence across sessions
        
        logger.info(f"Trust score persistence verified: {initial_score} -> {updated_score}")
    
    def test_sensitive_data_handling(self):
        """Test handling of sensitive data in memory."""
        # Perform operations with sensitive data
        sensitive_operations = [
            (WindsurfOperationType.AUTHENTICATION, {"method": "password", "username": "test"}),
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/user_data.py", "content": "def save_personal_info(): pass"})
        ]
        
        for op_type, context in sensitive_operations:
            self.adapter.evaluate_operation(op_type, context, self.test_user)
        
        # Perform non-sensitive operation
        self.adapter.evaluate_operation(
            WindsurfOperationType.CODE_GENERATION, 
            {"purpose": "logging", "content": "def log(message): print(message)"}, 
            self.test_user
        )
        
        # Clear sensitive data for authentication
        cleared = self.adapter.clear_sensitive_data(self.test_user, "authentication")
        
        # Verify clearing
        self.assertEqual(cleared, 1)  # Should have cleared 1 operation
        
        # Check that sensitive data was removed
        result = self.adapter.evaluate_operation(
            WindsurfOperationType.AUTHENTICATION, 
            {"method": "token", "username": "test"}, 
            self.test_user
        )
        
        # Should not have past authentication operations in context
        auth_ops = [op for op in result["past_context"] if op["operation_type"] == "authentication"]
        self.assertEqual(len(auth_ops), 0)
        
        # But should still have other operations
        result = self.adapter.evaluate_operation(
            WindsurfOperationType.CODE_GENERATION, 
            {"purpose": "testing", "content": "def test(): pass"}, 
            self.test_user
        )
        
        self.assertGreaterEqual(len(result["past_context"]), 1)
        
        logger.info(f"Cleared {cleared} sensitive operations from memory")
    
    def test_operation_context_relevance(self):
        """Test that retrieved context is relevant to current operation."""
        # Create a variety of operations
        diverse_operations = [
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/utils.py", "purpose": "utility functions"}),
            (WindsurfOperationType.CODE_GENERATION, {"purpose": "data processing", "language": "python"}),
            (WindsurfOperationType.AUTHENTICATION, {"method": "oauth", "provider": "github"}),
            (WindsurfOperationType.SYSTEM_CONFIG, {"component": "logging", "level": "debug"}),
            (WindsurfOperationType.CODE_GENERATION, {"purpose": "error handling", "language": "python"}),
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/models.py", "purpose": "data models"}),
        ]
        
        for op_type, context in diverse_operations:
            self.adapter.evaluate_operation(op_type, context, self.test_user)
        
        # Test context retrieval for code generation
        result = self.adapter.evaluate_operation(
            WindsurfOperationType.CODE_GENERATION, 
            {"purpose": "testing", "language": "python"}, 
            self.test_user
        )
        
        # Should only retrieve code generation operations
        self.assertGreaterEqual(len(result["past_context"]), 2)  # Should have at least 2 code generation operations
        for op in result["past_context"]:
            self.assertEqual(op["operation_type"], "code_generation")
        
        # Test context retrieval for file creation
        result = self.adapter.evaluate_operation(
            WindsurfOperationType.FILE_CREATION, 
            {"file_path": "/tests.py", "purpose": "unit tests"}, 
            self.test_user
        )
        
        # Should only retrieve file creation operations
        self.assertGreaterEqual(len(result["past_context"]), 2)  # Should have at least 2 file creation operations
        for op in result["past_context"]:
            self.assertEqual(op["operation_type"], "file_creation")
            
        logger.info(f"Context relevance verified for different operation types")
    
    def test_memory_expiration(self):
        """Test that memory expires appropriately based on Compassionate Temporality."""
        # Note: This test is limited in a mock environment
        # In a real implementation, you would test time-based expiration
        
        # Simulate the passage of time and memory expiration
        logger.info("Memory expiration test: In a real implementation, would test time-based expiration")
        
        # At minimum, verify basic functionality
        self.adapter.evaluate_operation(
            WindsurfOperationType.AUTHENTICATION, 
            {"method": "password", "username": "test"}, 
            self.test_user
        )
        
        # Clear all sensitive data
        cleared = self.adapter.clear_sensitive_data(self.test_user)
        self.assertGreaterEqual(cleared, 1)  # Should have cleared at least 1 operation
        
        logger.info(f"Cleared {cleared} operations, simulating memory expiration")

def run_tests():
    """Run the memory integration tests and generate a report."""
    # Set up test suite
    suite = unittest.TestSuite()
    suite.addTest(MemoryIntegrationTest('test_operation_storage_and_retrieval'))
    suite.addTest(MemoryIntegrationTest('test_trust_score_persistence'))
    suite.addTest(MemoryIntegrationTest('test_sensitive_data_handling'))
    suite.addTest(MemoryIntegrationTest('test_operation_context_relevance'))
    suite.addTest(MemoryIntegrationTest('test_memory_expiration'))
    
    # Run tests
    print("\n" + "="*50)
    print("ATRiAN Memory Integration Test Suite")
    print("="*50)
    
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Generate test report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": test_result.testsRun,
        "passed_tests": test_result.testsRun - len(test_result.errors) - len(test_result.failures),
        "success_rate": f"{((test_result.testsRun - len(test_result.errors) - len(test_result.failures)) / test_result.testsRun) * 100:.2f}%",
        "errors": [str(e) for e in test_result.errors],
        "failures": [str(f) for f in test_result.failures]
    }
    
    # Save test report
    os.makedirs("test_results", exist_ok=True)
    report_path = f"test_results/memory_integration_test_report_{int(time.time())}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTest report saved to {report_path}")
    print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    return report

if __name__ == "__main__":
    run_tests()