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
# - @references {C:\\EGOS\\ATRiAN\\tests\\test_memory_pruning.py}
# - @references {C:\\EGOS\\ATRiAN\\memory\\demo_memory_integration.py}
# --- 

import os
import sys
import json
import logging
import unittest
import tempfile
import shutil
import re
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
logger = logging.getLogger("test_privacy_filtering")

class PrivacyFilteringTest(unittest.TestCase):
    """Test suite for validating privacy filtering functionality."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a backend with the temporary directory
        self.backend = LocalStorageBackend(storage_dir=self.test_dir)
        
        # Create a memory adapter with the test backend
        self.memory_adapter = WindsurfMemoryAdapter(backend=self.backend)
        
        # Get direct reference to privacy filter
        self.privacy_filter = self.memory_adapter.privacy_filter
        
        # Test user ID
        self.test_user = "test_user"
        
        logger.info(f"Test environment set up with temporary directory: {self.test_dir}")
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        logger.info("Test environment cleaned up")
    
    def test_detect_sensitivity_low(self):
        """Test detection of low sensitivity data."""
        # Test data with no sensitive information
        test_data = {
            "operation_type": "view_file",
            "context": {
                "file_path": "/path/to/file.txt",
                "read_only": True,
                "timestamp": "2025-05-27T12:00:00"
            }
        }
        
        # Detect sensitivity
        sensitivity = self.privacy_filter.detect_sensitivity(test_data)
        
        # Verify sensitivity level
        self.assertEqual(sensitivity, PrivacySensitivity.LOW, 
                        "Data with no sensitive information should have LOW sensitivity")
    
    def test_detect_sensitivity_medium(self):
        """Test detection of medium sensitivity data."""
        # Test data with some sensitive terms
        test_data = {
            "operation_type": "user_preference",
            "context": {
                "setting": "theme",
                "value": "dark",
                "personal": True,
                "user_id": "user123"
            }
        }
        
        # Detect sensitivity
        sensitivity = self.privacy_filter.detect_sensitivity(test_data)
        
        # Verify sensitivity level
        self.assertEqual(sensitivity, PrivacySensitivity.MEDIUM, 
                        "Data with some sensitive terms should have MEDIUM sensitivity")
    
    def test_detect_sensitivity_high(self):
        """Test detection of high sensitivity data."""
        # Test data with multiple sensitive terms
        test_data = {
            "operation_type": "profile_update",
            "context": {
                "email": "user@example.com",
                "address": "123 Main St",
                "phone": "555-123-4567",
                "personal": True,
                "private": True
            }
        }
        
        # Detect sensitivity
        sensitivity = self.privacy_filter.detect_sensitivity(test_data)
        
        # Verify sensitivity level
        self.assertEqual(sensitivity, PrivacySensitivity.HIGH, 
                        "Data with multiple sensitive terms should have HIGH sensitivity")
    
    def test_detect_sensitivity_critical(self):
        """Test detection of critical sensitivity data."""
        # Test data with critical sensitive information
        test_data = {
            "operation_type": "authentication",
            "context": {
                "username": "testuser",
                "password": "password123",
                "remember_me": True
            }
        }
        
        # Detect sensitivity
        sensitivity = self.privacy_filter.detect_sensitivity(test_data)
        
        # Verify sensitivity level
        self.assertEqual(sensitivity, PrivacySensitivity.CRITICAL, 
                        "Data with password should have CRITICAL sensitivity")
        
        # Test with SSN
        test_data = {
            "operation_type": "profile_update",
            "context": {
                "name": "John Doe",
                "ssn": "123-45-6789",
                "dob": "1980-01-01"
            }
        }
        
        # Detect sensitivity
        sensitivity = self.privacy_filter.detect_sensitivity(test_data)
        
        # Verify sensitivity level
        self.assertEqual(sensitivity, PrivacySensitivity.CRITICAL, 
                        "Data with SSN should have CRITICAL sensitivity")
    
    def test_anonymize_data_string(self):
        """Test anonymization of sensitive data in strings."""
        # Test various sensitive data patterns
        test_cases = [
            # (input_string, expected_output)
            ("My credit card is 4111-1111-1111-1111", "My credit card is [CREDIT_CARD]"),
            ("Contact me at user@example.com", "Contact me at [EMAIL]"),
            ("Call me at (555) 123-4567", "Call me at [PHONE]"),
            ("My SSN is 123-45-6789", "My SSN is [SSN]"),
            ("Server IP is 192.168.1.1", "Server IP is [IP_ADDRESS]"),
            ("Visit https://example.com/page", "Visit [URL]"),
            ("API key is abcdef1234567890abcdef1234567890", "API key is [API_KEY]"),
            ("password=mysecretpassword", "password=[PASSWORD]"),
            ("token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "token=[TOKEN]")
        ]
        
        for input_string, expected_output in test_cases:
            # Anonymize data
            result = self.privacy_filter.anonymize_data(input_string)
            
            # Verify anonymization
            self.assertEqual(result, expected_output, 
                           f"Failed to properly anonymize: {input_string}")
    
    def test_anonymize_data_dict(self):
        """Test anonymization of sensitive data in dictionaries."""
        # Test dictionary with sensitive data
        test_data = {
            "user": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-123-4567",
                "credit_card": "4111-1111-1111-1111",
                "address": "123 Main St"
            },
            "transaction": {
                "amount": 100.00,
                "currency": "USD",
                "notes": "Payment for order #12345"
            },
            "auth": {
                "username": "johndoe",
                "password": "secret123",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            }
        }
        
        # Anonymize data
        result = self.privacy_filter.anonymize_data(test_data)
        
        # Verify anonymization
        self.assertEqual(result["user"]["name"], "John Doe", "Non-sensitive data should not be anonymized")
        self.assertEqual(result["user"]["email"], "[EMAIL]", "Email should be anonymized")
        self.assertEqual(result["user"]["phone"], "[PHONE]", "Phone should be anonymized")
        self.assertEqual(result["user"]["credit_card"], "[CREDIT_CARD]", "Credit card should be anonymized")
        self.assertEqual(result["transaction"]["amount"], 100.00, "Non-sensitive data should not be anonymized")
        self.assertEqual(result["auth"]["password"], "[PASSWORD]", "Password should be anonymized")
        self.assertEqual(result["auth"]["token"], "[TOKEN]", "Token should be anonymized")
    
    def test_anonymize_data_list(self):
        """Test anonymization of sensitive data in lists."""
        # Test list with sensitive data
        test_data = [
            "My name is John Doe",
            "My email is john@example.com",
            "My phone is 555-123-4567",
            "My credit card is 4111-1111-1111-1111",
            "My SSN is 123-45-6789"
        ]
        
        # Anonymize data
        result = self.privacy_filter.anonymize_data(test_data)
        
        # Verify anonymization
        self.assertEqual(result[0], "My name is John Doe", "Non-sensitive data should not be anonymized")
        self.assertEqual(result[1], "My email is [EMAIL]", "Email should be anonymized")
        self.assertEqual(result[2], "My phone is [PHONE]", "Phone should be anonymized")
        self.assertEqual(result[3], "My credit card is [CREDIT_CARD]", "Credit card should be anonymized")
        self.assertEqual(result[4], "My SSN is [SSN]", "SSN should be anonymized")
    
    def test_anonymize_data_nested(self):
        """Test anonymization of sensitive data in nested structures."""
        # Test nested structure with sensitive data
        test_data = {
            "user": {
                "name": "John Doe",
                "contact": {
                    "email": "john@example.com",
                    "phone": "555-123-4567"
                },
                "payment": [
                    {
                        "type": "credit_card",
                        "number": "4111-1111-1111-1111",
                        "expiry": "12/25"
                    },
                    {
                        "type": "bank_account",
                        "account": "12345678",
                        "routing": "87654321"
                    }
                ]
            },
            "notes": [
                "User provided SSN: 123-45-6789",
                "User lives at 123 Main St"
            ]
        }
        
        # Anonymize data
        result = self.privacy_filter.anonymize_data(test_data)
        
        # Verify anonymization
        self.assertEqual(result["user"]["name"], "John Doe", "Non-sensitive data should not be anonymized")
        self.assertEqual(result["user"]["contact"]["email"], "[EMAIL]", "Email should be anonymized")
        self.assertEqual(result["user"]["contact"]["phone"], "[PHONE]", "Phone should be anonymized")
        self.assertEqual(result["user"]["payment"][0]["number"], "[CREDIT_CARD]", "Credit card should be anonymized")
        self.assertEqual(result["notes"][0], "User provided SSN: [SSN]", "SSN should be anonymized")
    
    def test_store_operation_with_privacy_filtering(self):
        """Test that store_operation applies privacy filtering."""
        # Test operation with sensitive data
        operation_type = "profile_update"
        context = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "address": "123 Main St"
        }
        result = {
            "status": "success",
            "message": "Profile updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        # Store operation
        operation_id = self.memory_adapter.store_operation(
            user_id=self.test_user,
            operation_type=operation_type,
            context=context,
            result=result
        )
        
        # Retrieve operation
        stored_operation = self.memory_adapter.retrieve_operation(self.test_user, operation_id)
        
        # Verify privacy filtering
        self.assertIsNotNone(stored_operation, "Operation should be stored")
        self.assertEqual(stored_operation["operation_type"], operation_type, "Operation type should be preserved")
        
        # Check that sensitive data is anonymized
        stored_context = stored_operation["context"]
        self.assertEqual(stored_context["name"], "John Doe", "Non-sensitive data should not be anonymized")
        self.assertEqual(stored_context["email"], "[EMAIL]", "Email should be anonymized")
        self.assertEqual(stored_context["phone"], "[PHONE]", "Phone should be anonymized")
        self.assertEqual(stored_context["ssn"], "[SSN]", "SSN should be anonymized")
    
    def test_disable_privacy_filtering(self):
        """Test that privacy filtering can be disabled."""
        # Disable privacy filtering
        self.memory_adapter.config["enable_privacy_filter"] = False
        
        # Test operation with sensitive data
        operation_type = "profile_update"
        context = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789"
        }
        result = {
            "status": "success",
            "message": "Profile updated successfully"
        }
        
        # Store operation
        operation_id = self.memory_adapter.store_operation(
            user_id=self.test_user,
            operation_type=operation_type,
            context=context,
            result=result
        )
        
        # Retrieve operation
        stored_operation = self.memory_adapter.retrieve_operation(self.test_user, operation_id)
        
        # Verify no privacy filtering
        self.assertIsNotNone(stored_operation, "Operation should be stored")
        
        # Check that sensitive data is preserved
        stored_context = stored_operation["context"]
        self.assertEqual(stored_context["email"], "john@example.com", "Email should not be anonymized when filtering is disabled")
        self.assertEqual(stored_context["phone"], "555-123-4567", "Phone should not be anonymized when filtering is disabled")
        self.assertEqual(stored_context["ssn"], "123-45-6789", "SSN should not be anonymized when filtering is disabled")
        
        # Re-enable privacy filtering for other tests
        self.memory_adapter.config["enable_privacy_filter"] = True
    
    def test_clear_sensitive_data(self):
        """Test clearing of sensitive data."""
        # Create operations with different sensitivity levels
        operations = {}
        
        for sensitivity in PrivacySensitivity:
            # Create context based on sensitivity
            if sensitivity == PrivacySensitivity.LOW:
                context = {"type": "view", "file": "document.txt"}
                op_type = "view_file"
            elif sensitivity == PrivacySensitivity.MEDIUM:
                context = {"type": "preference", "personal": True}
                op_type = "user_preference"
            elif sensitivity == PrivacySensitivity.HIGH:
                context = {"type": "profile", "email": "user@example.com"}
                op_type = "profile_update"
            else:  # CRITICAL
                context = {"type": "auth", "password": "secret123"}
                op_type = "authentication"
            
            # Store operation
            op_id = self.memory_adapter.store_operation(
                user_id=self.test_user,
                operation_type=op_type,
                context=context,
                result={"status": "success"}
            )
            
            operations[sensitivity] = (op_id, op_type)
        
        # Clear sensitive data for authentication operations
        cleared_count = self.memory_adapter.clear_sensitive_data(
            user_id=self.test_user,
            data_type="authentication"
        )
        
        # Verify clearing
        self.assertEqual(cleared_count, 1, "Should have cleared 1 authentication operation")
        
        # Check that authentication operation is gone
        critical_op_id, _ = operations[PrivacySensitivity.CRITICAL]
        critical_op = self.memory_adapter.retrieve_operation(self.test_user, critical_op_id)
        self.assertIsNone(critical_op, "Critical operation should be cleared")
        
        # Check that other operations still exist
        for sensitivity, (op_id, _) in operations.items():
            if sensitivity != PrivacySensitivity.CRITICAL:
                op = self.memory_adapter.retrieve_operation(self.test_user, op_id)
                self.assertIsNotNone(op, f"Operation with {sensitivity} sensitivity should not be cleared")
        
        # Clear all sensitive data
        cleared_count = self.memory_adapter.clear_sensitive_data(user_id=self.test_user)
        
        # Verify all remaining operations are cleared
        self.assertEqual(cleared_count, 3, "Should have cleared 3 remaining operations")
        
        # Check that all operations are gone
        for sensitivity, (op_id, _) in operations.items():
            op = self.memory_adapter.retrieve_operation(self.test_user, op_id)
            self.assertIsNone(op, f"Operation with {sensitivity} sensitivity should be cleared")
    
    def test_privacy_terms_coverage(self):
        """Test that privacy terms cover common sensitive data types."""
        # Get privacy terms
        privacy_terms = self.privacy_filter.privacy_terms
        
        # Define categories of terms that should be covered
        categories = {
            "personal_identifiers": ["password", "secret", "token", "key", "credential"],
            "financial": ["credit", "debit", "card", "payment", "bank", "account"],
            "identity": ["ssn", "social security", "passport", "license", "identity"],
            "contact": ["address", "phone", "email", "contact", "location"],
            "health": ["health", "medical", "diagnosis", "treatment", "patient"]
        }
        
        # Check coverage for each category
        for category, terms in categories.items():
            for term in terms:
                self.assertIn(term, privacy_terms, 
                             f"Privacy terms should include '{term}' in category '{category}'")
    
    def test_anonymization_patterns_coverage(self):
        """Test that anonymization patterns cover common sensitive data formats."""
        # Get anonymization patterns
        patterns = self.privacy_filter.anonymization_patterns
        
        # Test data formats that should be detected
        test_formats = {
            "credit_card": [
                "4111111111111111",
                "4111-1111-1111-1111",
                "4111 1111 1111 1111"
            ],
            "email": [
                "user@example.com",
                "first.last@subdomain.example.co.uk"
            ],
            "phone": [
                "555-123-4567",
                "(555) 123-4567",
                "5551234567"
            ],
            "ssn": [
                "123-45-6789"
            ],
            "ip_address": [
                "192.168.1.1",
                "10.0.0.1",
                "172.16.0.1"
            ],
            "url": [
                "https://example.com",
                "http://subdomain.example.com/path?query=value"
            ],
            "api_key": [
                "abcdef1234567890abcdef1234567890",
                "api_key_12345678901234567890"
            ],
            "password": [
                "password=secret123",
                "password: mypassword",
                "password = p@ssw0rd"
            ],
            "token": [
                "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "token: bearer_token_12345",
                "token = oauth_token_abcdef"
            ]
        }
        
        # Test each format against patterns
        for data_type, examples in test_formats.items():
            for example in examples:
                # Find matching pattern
                matched = False
                for pattern, replacement in patterns.items():
                    if re.search(pattern, example):
                        matched = True
                        break
                
                self.assertTrue(matched, 
                              f"Anonymization patterns should detect {data_type} format: '{example}'")

def run_tests():
    """Run the privacy filtering tests and generate a report."""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(PrivacyFilteringTest)
    
    # Run tests
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Print summary
    print("\n=== Privacy Filtering Test Summary ===")
    print(f"Tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    print(f"Skipped: {len(test_result.skipped)}")
    
    # Return success status
    return len(test_result.failures) == 0 and len(test_result.errors) == 0

if __name__ == "__main__":
    run_tests()