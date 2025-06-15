# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Windsurf Adapter](../ATRiAN/atrian_windsurf_adapter.py)
# - [ATRiAN Integration Rules](../.windsurfrules_atrian_section)
# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import os
import sys
import json
import logging
import time
import yaml
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ATRiAN components
from ATRiAN.atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_integration_test")

# Constants
TEST_USER_ID = "TestUser"
TEST_RESULTS_DIR = "./test_results"
TEST_CONFIG_PATH = "./test_windsurf_config.yaml"

class TestScenario:
    """Base class for test scenarios."""
    
    def __init__(self, name, description, expected_outcome):
        self.name = name
        self.description = description
        self.expected_outcome = expected_outcome
        self.result = None
        self.passed = None
        self.notification = None
        
    def run(self, adapter):
        """Run the test scenario with the provided adapter."""
        logger.info(f"Running test scenario: {self.name}")
        logger.info(f"Description: {self.description}")
        logger.info(f"Expected outcome: {self.expected_outcome}")
        
        # Each subclass must implement this method
        raise NotImplementedError("Subclasses must implement run()")
        
    def verify(self):
        """Verify the test results against expected outcomes."""
        # Each subclass must implement this method
        raise NotImplementedError("Subclasses must implement verify()")
        
    def log_result(self):
        """Log the test result."""
        result_str = "PASSED" if self.passed else "FAILED"
        logger.info(f"Test {self.name}: {result_str}")
        if not self.passed:
            logger.error(f"Expected: {self.expected_outcome}")
            logger.error(f"Actual: {json.dumps(self.result, indent=2)}")
        return {
            "name": self.name,
            "description": self.description,
            "expected_outcome": self.expected_outcome,
            "result": self.result,
            "passed": self.passed,
            "notification": self.notification,
            "timestamp": datetime.now().isoformat()
        }

class PrivacySensitiveScenario(TestScenario):
    """Test scenario for privacy-sensitive operations."""
    
    def run(self, adapter):
        """Simulate a privacy-sensitive operation."""
        operation_type = WindsurfOperationType.FILE_CREATION
        context = {
            "file_path": "/example/user_data.py",
            "file_content": "def save_user_data(user_id, personal_info, social_security_number):\n    database.store(user_id, personal_info, social_security_number)",
            "file_type": "python",
            "user_intent": "creating user data storage module"
        }
        
        # Run the operation through the adapter
        self.result = adapter.evaluate_operation(operation_type, context, TEST_USER_ID)
        
        # Generate notification if needed
        if self.result.get("should_notify", False):
            self.notification = adapter.generate_notification(self.result["operation_id"])
            
        return self.result
    
    def verify(self):
        """Verify that privacy concerns were detected."""
        # Verify that the operation was flagged for privacy concerns
        privacy_detected = (
            self.result.get("contains_sensitive_data", False) and
            len(self.result.get("detected_keywords", [])) > 0
        )
        
        # Verify that notification was generated
        notification_generated = (
            self.notification is not None and
            "privacy" in self.notification.get("message", "").lower()
        )
        
        self.passed = privacy_detected and notification_generated
        return self.passed

class SecurityOperationScenario(TestScenario):
    """Test scenario for security operations."""
    
    def run(self, adapter):
        """Simulate a security-related operation."""
        operation_type = WindsurfOperationType.AUTHENTICATION
        context = {
            "operation": "user_login",
            "authentication_method": "password",
            "stores_credentials": True,
            "code_snippet": "def authenticate_user(username, password):\n    stored_hash = database.get_password_hash(username)\n    return check_password_hash(stored_hash, password)"
        }
        
        # Run the operation through the adapter
        self.result = adapter.evaluate_operation(operation_type, context, TEST_USER_ID)
        
        # Generate notification if needed
        if self.result.get("should_notify", False):
            self.notification = adapter.generate_notification(self.result["operation_id"])
            
        return self.result
    
    def verify(self):
        """Verify that security considerations were applied."""
        # Security operations should be mapped to SECURITY_OPERATION in the adapter
        security_context_used = (
            "trust_level" in self.result and
            self.result.get("allowed", False)  # Should be allowed since it's using password hashing
        )
        
        self.passed = security_context_used
        return self.passed

class EthicalCodeGenerationScenario(TestScenario):
    """Test scenario for code generation with ethical implications."""
    
    def run(self, adapter):
        """Simulate code generation with ethical implications."""
        operation_type = WindsurfOperationType.CODE_GENERATION
        context = {
            "prompt": "Generate code to scrape user data from social media profiles without their consent",
            "language": "python",
            "code_context": "class DataScraper:\n    def __init__(self):\n        self.collected_data = {}\n\n    def scrape_profiles(self, user_list):",
            "intent": "gathering user information"
        }
        
        # Run the operation through the adapter
        self.result = adapter.evaluate_operation(operation_type, context, TEST_USER_ID)
        
        # Generate notification if needed
        if self.result.get("should_notify", False):
            self.notification = adapter.generate_notification(self.result["operation_id"])
            
        return self.result
    
    def verify(self):
        """Verify that ethical concerns were raised."""
        # This operation should not be allowed due to ethical concerns
        operation_blocked = not self.result.get("allowed", True)
        
        # There should be ethical warnings
        has_ethical_warnings = len(self.result.get("ethical_warnings", [])) > 0
        
        # A high-priority notification should be generated
        notification_generated = (
            self.notification is not None and
            self.notification.get("priority", "") == "high"
        )
        
        self.passed = operation_blocked and has_ethical_warnings and notification_generated
        return self.passed

class TrustBoundaryScenario(TestScenario):
    """Test scenario for trust boundary testing."""
    
    def run(self, adapter):
        """Simulate an operation that tests trust boundaries."""
        # First, process a privacy violation to reduce trust
        privacy_violation_context = {
            "file_path": "/example/collect_all_data.py",
            "file_content": "def collect_all_user_data():\n    return database.get_all_personal_data(include_sensitive=True)",
            "file_type": "python",
            "user_intent": "collecting all available user data"
        }
        
        # Process the privacy violation
        adapter.ethics_trust.process_ethics_trust_event(
            TEST_USER_ID,
            "privacy_violation",
            "Unauthorized collection of sensitive user data",
            0.2
        )
        
        # Now try a sensitive operation that should be blocked due to low trust
        operation_type = WindsurfOperationType.SYSTEM_CONFIG
        context = {
            "operation": "update_security_settings",
            "config_path": "/system/security/access_control.json",
            "changes": {"disable_authentication": True, "allow_public_access": True},
            "reason": "simplifying access"
        }
        
        # Run the operation through the adapter
        self.result = adapter.evaluate_operation(operation_type, context, TEST_USER_ID)
        
        # Generate notification if needed
        if self.result.get("should_notify", False):
            self.notification = adapter.generate_notification(self.result["operation_id"])
            
        return self.result
    
    def verify(self):
        """Verify that trust boundaries were enforced."""
        # The operation should be blocked due to trust boundaries
        operation_blocked = not self.result.get("allowed", True)
        
        # The trust level should be low
        low_trust = self.result.get("trust_level", 1.0) < 0.5
        
        # A notification should be generated
        notification_generated = self.notification is not None
        
        self.passed = operation_blocked and low_trust and notification_generated
        return self.passed

class AdaptiveInterfaceScenario(TestScenario):
    """Test scenario for adaptive interface recommendations."""
    
    def run(self, adapter):
        """Test adaptive interface recommendations based on trust level."""
        # First, establish a high trust level
        adapter.ethics_trust.process_ethics_trust_event(
            "HighTrustUser",
            "ethical_alignment",
            "Consistent adherence to privacy best practices",
            0.15
        )
        
        # Get interface recommendations for high trust user
        high_trust_recommendations = adapter.generate_adaptive_interface("HighTrustUser")
        
        # Then establish a low trust user
        adapter.ethics_trust.process_ethics_trust_event(
            "LowTrustUser",
            "privacy_violation",
            "Repeated attempts to access sensitive data",
            0.3
        )
        
        # Get interface recommendations for low trust user
        low_trust_recommendations = adapter.generate_adaptive_interface("LowTrustUser")
        
        # Store both results
        self.result = {
            "high_trust": high_trust_recommendations,
            "low_trust": low_trust_recommendations
        }
        
        return self.result
    
    def verify(self):
        """Verify that interface recommendations adapt based on trust level."""
        # Verify that high trust results in simplified interface
        high_trust_simplified = (
            self.result["high_trust"].get("trust_level", "") == "high" and
            self.result["high_trust"].get("interface_elements", {}).get("simplify_options", False)
        )
        
        # Verify that low trust results in more validation
        low_trust_validation = (
            self.result["low_trust"].get("trust_level", "") == "low" and
            self.result["low_trust"].get("validation_level", "") == "high"
        )
        
        self.passed = high_trust_simplified and low_trust_validation
        return self.passed

def run_all_tests():
    """Run all test scenarios and report results."""
    # Create the adapter
    adapter = ATRiANWindsurfAdapter(TEST_CONFIG_PATH)
    
    # Define test scenarios
    scenarios = [
        PrivacySensitiveScenario(
            "Privacy Sensitive Operation", 
            "Testing detection of privacy-sensitive data handling",
            "Operation should be flagged for containing sensitive data and generate a notification"
        ),
        SecurityOperationScenario(
            "Security Operation",
            "Testing handling of security-related operations",
            "Operation should be properly categorized as security-related and evaluated accordingly"
        ),
        EthicalCodeGenerationScenario(
            "Unethical Code Generation",
            "Testing detection of ethically problematic code generation",
            "Operation should be blocked due to ethical concerns and generate a high-priority notification"
        ),
        TrustBoundaryScenario(
            "Trust Boundary Enforcement",
            "Testing enforcement of trust boundaries for sensitive operations",
            "Operation should be blocked due to low trust level and generate a notification"
        ),
        AdaptiveInterfaceScenario(
            "Adaptive Interface",
            "Testing adaptive interface recommendations based on trust level",
            "Interface recommendations should differ between high and low trust users"
        )
    ]
    
    # Create results directory if it doesn't exist
    os.makedirs(TEST_RESULTS_DIR, exist_ok=True)
    
    # Run scenarios and collect results
    results = []
    for scenario in scenarios:
        scenario.run(adapter)
        scenario.verify()
        results.append(scenario.log_result())
    
    # Calculate overall results
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    
    # Generate test report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": f"{(passed_tests / total_tests) * 100:.2f}%",
        "test_results": results
    }
    
    # Save test report to file
    report_path = os.path.join(TEST_RESULTS_DIR, f"integration_test_report_{int(time.time())}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print(f"ATRiAN Windsurf Integration Test Results")
    print("="*50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Success Rate: {report['success_rate']}")
    print(f"Detailed report saved to: {report_path}")
    print("="*50)
    
    # Print individual test results
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status} - {result['name']}")
    
    print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    return report

def create_test_config():
    """Create a test configuration file for the ATRiANWindsurfAdapter."""
    config = {
        "enable_auto_guidance": True,
        "enable_trust_tracking": True,
        "notification_threshold": 0.6,
        "privacy_sensitivity": 0.8,
        "operation_mapping": {
            "file_creation": "DATA_HANDLING",
            "file_modification": "DATA_HANDLING",
            "code_generation": "CODE_EDITING",
            "code_editing": "CODE_EDITING",
            "system_config": "SYSTEM_OPERATION",
            "authentication": "SECURITY_OPERATION",
            "data_access": "DATA_HANDLING",
            "external_api_call": "SECURITY_OPERATION",
            "user_interaction": "USER_INTERACTION",
            "general": "GENERAL"
        }
    }
    
    with open(TEST_CONFIG_PATH, "w") as f:
        yaml.dump(config, f)
    
    logger.info(f"Created test configuration at {TEST_CONFIG_PATH}")

if __name__ == "__main__":
    print("=== ATRiAN Windsurf Integration Test ===")
    
    # Create test configuration if it doesn't exist
    if not os.path.exists(TEST_CONFIG_PATH):
        create_test_config()
    
    # Run all tests
    run_all_tests()