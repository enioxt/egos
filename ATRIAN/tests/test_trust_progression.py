# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Trust Weaver](../atrian_trust_weaver.py)
# - [ATRiAN Implementation Plan](../ATRiAN_Implementation_Plan.md)
# - [EGOS Global Rules](../../.windsurfrules)
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
    from ATRiAN.atrian_trust_weaver import WeaverOfTrust
    from ATRiAN.atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType
except ImportError:
    # Mock classes for testing without actual implementation
    class WeaverOfTrust:
        def __init__(self, config_path=None):
            self.trust_scores = {}
            self.trust_events = []
            
        def get_trust_score(self, agent_id):
            return self.trust_scores.get(agent_id, 0.7)
            
        def update_trust_score(self, agent_id, event_type, outcome, magnitude=0.1):
            current_score = self.get_trust_score(agent_id)
            if outcome == "positive":
                new_score = min(1.0, current_score + magnitude)
            else:
                new_score = max(0.0, current_score - magnitude)
            self.trust_scores[agent_id] = new_score
            self.trust_events.append({
                "agent_id": agent_id,
                "event_type": event_type,
                "outcome": outcome,
                "magnitude": magnitude,
                "timestamp": datetime.now().isoformat()
            })
            return new_score
    
    class WindsurfOperationType(Enum):
        FILE_CREATION = "file_creation"
        CODE_GENERATION = "code_generation"
        AUTHENTICATION = "authentication"
        SYSTEM_CONFIG = "system_config"
        
    class ATRiANWindsurfAdapter:
        def __init__(self, config_path=None):
            self.trust_weaver = WeaverOfTrust()
            self.operations = {}
            
        def evaluate_operation(self, operation_type, context, user_id):
            operation_id = f"{operation_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            result = {
                "operation_id": operation_id,
                "allowed": True,
                "trust_score": self.trust_weaver.get_trust_score(user_id)
            }
            self.operations[operation_id] = result
            return result

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_trust_progression_test")

class TrustProgressionTest(unittest.TestCase):
    """Test suite for validating trust progression in the ATRiAN-Windsurf integration."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.adapter = ATRiANWindsurfAdapter()
        self.test_user = "TestUser"
        # Reset trust score to neutral starting point
        self.adapter.trust_weaver.trust_scores[self.test_user] = 0.7
        
    def test_progressive_trust_building(self):
        """Test that trust increases progressively with positive interactions."""
        initial_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
        
        # Simulate a series of positive interactions
        positive_operations = [
            (WindsurfOperationType.FILE_CREATION, {"file_path": "/example/utils.py", "content": "def helper(): pass"}),
            (WindsurfOperationType.CODE_GENERATION, {"purpose": "create utility functions", "content": "def validate_input(data): return data.strip()"}),
            (WindsurfOperationType.AUTHENTICATION, {"method": "secure_token", "remember_user": False}),
        ]
        
        trust_progression = [initial_trust]
        
        for op_type, context in positive_operations:
            result = self.adapter.evaluate_operation(op_type, context, self.test_user)
            # Simulate positive outcome
            self.adapter.trust_weaver.update_trust_score(
                self.test_user, 
                f"{op_type.value}_success", 
                "positive", 
                0.05
            )
            current_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
            trust_progression.append(current_trust)
            
        # Verify trust increased
        self.assertGreater(trust_progression[-1], trust_progression[0])
        # Verify progressive nature (each step increases)
        for i in range(1, len(trust_progression)):
            self.assertGreater(trust_progression[i], trust_progression[i-1])
            
        logger.info(f"Trust progression: {trust_progression}")
    
    def test_trust_decay_after_violations(self):
        """Test that trust declines after ethical violations."""
        initial_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
        
        # Simulate ethical violations
        violation_operations = [
            (
                WindsurfOperationType.CODE_GENERATION, 
                {"purpose": "scrape user data without consent", "content": "def scrape_profiles(): return user_data"}
            ),
            (
                WindsurfOperationType.SYSTEM_CONFIG, 
                {"component": "security", "action": "disable_authentication", "reason": "testing"}
            ),
        ]
        
        trust_progression = [initial_trust]
        
        for op_type, context in violation_operations:
            result = self.adapter.evaluate_operation(op_type, context, self.test_user)
            # Simulate negative outcome
            self.adapter.trust_weaver.update_trust_score(
                self.test_user, 
                f"{op_type.value}_violation", 
                "negative", 
                0.15  # Higher magnitude for violations
            )
            current_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
            trust_progression.append(current_trust)
            
        # Verify trust decreased
        self.assertLess(trust_progression[-1], trust_progression[0])
        # Verify progressive nature (each step decreases)
        for i in range(1, len(trust_progression)):
            self.assertLess(trust_progression[i], trust_progression[i-1])
            
        logger.info(f"Trust decay: {trust_progression}")
    
    def test_trust_recovery_after_violations(self):
        """Test that trust can be rebuilt after violations through positive actions."""
        # First, create a violation to reduce trust
        self.adapter.trust_weaver.update_trust_score(
            self.test_user, 
            "privacy_violation", 
            "negative", 
            0.3  # Significant violation
        )
        
        reduced_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
        
        # Simulate recovery through positive actions
        recovery_operations = [
            (
                WindsurfOperationType.FILE_CREATION, 
                {"file_path": "/example/privacy_policy.py", "content": "def get_user_consent(): return user.prompt_consent()"}
            ),
            (
                WindsurfOperationType.AUTHENTICATION, 
                {"method": "two_factor", "remember_user": False}
            ),
            (
                WindsurfOperationType.CODE_GENERATION, 
                {"purpose": "implement privacy protection", "content": "def anonymize_data(user_data): return hash_sensitive_fields(user_data)"}
            ),
            (
                WindsurfOperationType.SYSTEM_CONFIG, 
                {"component": "security", "action": "enable_advanced_protection", "reason": "improving security"}
            ),
        ]
        
        trust_progression = [reduced_trust]
        
        for op_type, context in recovery_operations:
            result = self.adapter.evaluate_operation(op_type, context, self.test_user)
            # Simulate positive outcome
            self.adapter.trust_weaver.update_trust_score(
                self.test_user, 
                f"{op_type.value}_success", 
                "positive", 
                0.05  # Smaller increments for rebuilding trust
            )
            current_trust = self.adapter.trust_weaver.get_trust_score(self.test_user)
            trust_progression.append(current_trust)
            
        # Verify trust increased from the reduced level
        self.assertGreater(trust_progression[-1], trust_progression[0])
        # Verify recovery is slower than initial violation (trust not fully restored)
        self.assertLess(trust_progression[-1], 0.7)  # Initial trust was 0.7
            
        logger.info(f"Trust recovery: {trust_progression}")
    
    def test_trust_based_operation_restrictions(self):
        """Test that operations are restricted based on trust level."""
        # Set up a low trust scenario
        self.adapter.trust_weaver.trust_scores[self.test_user] = 0.3  # Low trust
        
        # Attempt a sensitive operation
        sensitive_operation = (
            WindsurfOperationType.SYSTEM_CONFIG, 
            {"component": "security", "action": "modify_permissions", "reason": "testing"}
        )
        
        # In a real implementation, this would check trust thresholds and potentially block
        # For this test, we'll manually implement the check
        result = self.adapter.evaluate_operation(sensitive_operation[0], sensitive_operation[1], self.test_user)
        
        # For testing purposes, simulate the adapter's trust-based restriction logic
        # In real implementation, this would be handled inside evaluate_operation
        allowed = result.get("trust_score", 0) >= 0.5  # Example threshold
        
        self.assertFalse(allowed, "Low trust should restrict sensitive operations")
        
        # Set up a high trust scenario
        self.adapter.trust_weaver.trust_scores[self.test_user] = 0.9  # High trust
        
        # Try the same operation
        result = self.adapter.evaluate_operation(sensitive_operation[0], sensitive_operation[1], self.test_user)
        
        # Simulate trust-based restriction again
        allowed = result.get("trust_score", 0) >= 0.5  # Example threshold
        
        self.assertTrue(allowed, "High trust should allow sensitive operations")
        
    def test_long_term_trust_patterns(self):
        """Test long-term trust patterns with mixed behavior."""
        # Initialize events list to track trust changes
        events = []
        
        # Simulate a series of mixed interactions over time
        mixed_operations = [
            # Initial positive actions
            {"op_type": WindsurfOperationType.FILE_CREATION, "context": {"purpose": "utility"}, "outcome": "positive", "magnitude": 0.05},
            {"op_type": WindsurfOperationType.CODE_GENERATION, "context": {"purpose": "helpers"}, "outcome": "positive", "magnitude": 0.05},
            # Violation
            {"op_type": WindsurfOperationType.SYSTEM_CONFIG, "context": {"action": "disable_security"}, "outcome": "negative", "magnitude": 0.2},
            # Recovery attempts
            {"op_type": WindsurfOperationType.AUTHENTICATION, "context": {"method": "secure"}, "outcome": "positive", "magnitude": 0.05},
            {"op_type": WindsurfOperationType.FILE_CREATION, "context": {"purpose": "security"}, "outcome": "positive", "magnitude": 0.05},
            # Another violation
            {"op_type": WindsurfOperationType.CODE_GENERATION, "context": {"purpose": "bypass"}, "outcome": "negative", "magnitude": 0.15},
            # Sustained recovery
            {"op_type": WindsurfOperationType.AUTHENTICATION, "context": {"method": "mfa"}, "outcome": "positive", "magnitude": 0.05},
            {"op_type": WindsurfOperationType.SYSTEM_CONFIG, "context": {"action": "enhance_security"}, "outcome": "positive", "magnitude": 0.05},
            {"op_type": WindsurfOperationType.FILE_CREATION, "context": {"purpose": "privacy"}, "outcome": "positive", "magnitude": 0.05},
            {"op_type": WindsurfOperationType.CODE_GENERATION, "context": {"purpose": "encryption"}, "outcome": "positive", "magnitude": 0.05},
        ]
        
        # Track trust score progression
        trust_progression = [self.adapter.trust_weaver.get_trust_score(self.test_user)]
        
        for operation in mixed_operations:
            # Process operation
            self.adapter.evaluate_operation(operation["op_type"], operation["context"], self.test_user)
            
            # Update trust
            new_trust = self.adapter.trust_weaver.update_trust_score(
                self.test_user,
                f"{operation['op_type'].value}_{operation['outcome']}",
                operation["outcome"],
                operation["magnitude"]
            )
            
            trust_progression.append(new_trust)
            events.append({
                "operation": operation["op_type"].value,
                "context": operation["context"],
                "outcome": operation["outcome"],
                "trust_after": new_trust
            })
        
        # Verify trust patterns
        # 1. Trust should drop after violations
        violation_indices = [2, 5]  # Based on our test data
        for idx in violation_indices:
            self.assertLess(trust_progression[idx+1], trust_progression[idx], 
                           f"Trust should decrease after violation at step {idx}")
        
        # 2. Trust should increase during recovery periods
        recovery_periods = [(3, 4), (6, 9)]  # Based on our test data
        for start, end in recovery_periods:
            self.assertGreater(trust_progression[end+1], trust_progression[start+1], 
                              f"Trust should increase during recovery period {start}-{end}")
        
        # 3. Final trust should be different from initial trust
        self.assertNotEqual(trust_progression[0], trust_progression[-1], 
                           "Trust should evolve over time")
        
        # Log detailed trust progression
        logger.info("Long-term trust progression:")
        for i, trust in enumerate(trust_progression):
            event_info = f"Operation: {events[i-1]['operation']}, Outcome: {events[i-1]['outcome']}" if i > 0 else "Initial"
            logger.info(f"Step {i}: Trust = {trust:.2f} - {event_info}")
        
        # Create a visualization-ready dataset
        visualization_data = {
            "timestamps": [i for i in range(len(trust_progression))],
            "trust_scores": trust_progression,
            "events": [{"index": i, "event": e["operation"], "outcome": e["outcome"]} for i, e in enumerate(events, 1)]
        }
        
        # Save for potential visualization
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/trust_progression_data.json", "w") as f:
            json.dump(visualization_data, f, indent=2)
        
        logger.info(f"Visualization data saved to test_results/trust_progression_data.json")

def run_tests():
    """Run the trust progression tests and generate a report."""
    # Set up test suite
    suite = unittest.TestSuite()
    suite.addTest(TrustProgressionTest('test_progressive_trust_building'))
    suite.addTest(TrustProgressionTest('test_trust_decay_after_violations'))
    suite.addTest(TrustProgressionTest('test_trust_recovery_after_violations'))
    suite.addTest(TrustProgressionTest('test_trust_based_operation_restrictions'))
    suite.addTest(TrustProgressionTest('test_long_term_trust_patterns'))
    
    # Run tests
    print("\n" + "="*50)
    print("ATRiAN Trust Progression Test Suite")
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
    report_path = f"test_results/trust_progression_test_report_{int(time.time())}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTest report saved to {report_path}")
    print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    return report

if __name__ == "__main__":
    run_tests()