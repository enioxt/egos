"""
ATRiAN Ethical Constitution Validator - Usage Examples

This file demonstrates how to use the ATRiAN Ethical Constitution Validator
in various scenarios, particularly with PromptVault integration.

Version: 0.1.0
Last Modified: 2025-06-12
"""
# 
# @references:
#   - ATRIAN/templates/examples/validator_usage_example.py
# 
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from templates.constitution_validator import (
    EthicalConstitutionValidator,
    validate_prompt_with_constitutions
)

def example_1_basic_validation():
    """
    Basic example of validating a prompt against a single ethical constitution.
    """
    print("\n=== Example 1: Basic Validation ===")
    
    # Sample prompt to validate
    prompt = """
    Design a facial recognition system that automatically collects and stores facial data
    from public areas to identify individuals. The system should operate continuously
    and build profiles of regular visitors without notifications.
    """
    
    # Initialize the validator
    validator = EthicalConstitutionValidator()
    
    # Load constitutions
    validator.load_all_constitutions()
    print(f"Loaded {len(validator.constitutions)} constitutions.")
    
    # Validate against GDPR constitution
    result = validator.validate_prompt(prompt, "egos-gdpr-ethical-constitution-v1")
    
    # Print results
    print(f"\nValidation Result for GDPR Constitution:")
    print(f"Passed: {result.passed}")
    print(f"Score: {result.overall_score:.2f}")
    print(f"\nWarnings: {len(result.warnings)}")
    for warning in result.warnings:
        print(f"- {warning}")
    
    print(f"\nRecommendations:")
    for recommendation in result.recommendations:
        print(f"- {recommendation}")
    
    if result.critical_failures:
        print(f"\nCritical Failures: {result.critical_failures}")


def example_2_multiple_constitutions():
    """
    Example of validating a prompt against multiple ethical constitutions
    and combining the results.
    """
    print("\n=== Example 2: Multiple Constitution Validation ===")
    
    # Sample healthcare prompt
    healthcare_prompt = """
    Create an AI system to analyze patient data and recommend treatments
    without human oversight. The system should access full medical records
    and be able to prescribe medications directly.
    """
    
    # Validate against multiple constitutions
    validation_result = validate_prompt_with_constitutions(
        healthcare_prompt, 
        ["egos-healthcare-ethical-constitution-v1", "egos-eu-ai-act-ethical-constitution-v1"]
    )
    
    # Print summary results
    print(f"Overall validation passed: {validation_result['passed']}")
    print(f"Overall score: {validation_result['overall_score']:.2f}")
    print(f"Validated against {len(validation_result['constitution_results'])} constitutions")
    
    # Print results for each constitution
    for const_result in validation_result['constitution_results']:
        print(f"\n{const_result['constitution_name']} validation:")
        print(f"Passed: {const_result['passed']}")
        print(f"Score: {const_result['overall_score']:.2f}")
    
    # Print combined recommendations
    print(f"\nCombined Recommendations:")
    for recommendation in validation_result['combined_recommendations']:
        print(f"- {recommendation}")


def example_3_promptvault_integration():
    """
    Example showing integration with PromptVault
    (mocked for demonstration purposes)
    """
    print("\n=== Example 3: PromptVault Integration ===")
    
    # This is a mock of what the PromptVault integration would look like
    class MockPromptVault:
        def store_prompt(self, prompt, metadata=None):
            print(f"Storing prompt in PromptVault: {prompt[:30]}...")
            return {"prompt_id": "pv-123456"}
            
        def validate_prompt(self, prompt, validation_config):
            print(f"Validating prompt with PromptVault...")
            
            # Use ATRiAN validator in the background
            constitutions = validation_config.get("ethical_constitutions", [])
            result = validate_prompt_with_constitutions(prompt, constitutions)
            
            # Add validation results to prompt metadata
            validation_status = "VALID" if result["passed"] else "INVALID"
            print(f"Validation status: {validation_status}")
            print(f"Validation score: {result['overall_score']:.2f}")
            
            # This would be stored with the prompt in a real implementation
            return {
                "validation_status": validation_status,
                "validation_score": result["overall_score"],
                "validation_details": result,
                "validator": "ATRiAN Ethical Constitution Validator v0.1.0"
            }
    
    # Create mock PromptVault
    pv = MockPromptVault()
    
    # Example prompt to validate and store
    test_prompt = """
    Design a system to analyze student behavior in classrooms using cameras
    and microphones. The system should track attention levels and create
    individual profiles for each student.
    """
    
    # Validate the prompt before storing
    validation_result = pv.validate_prompt(
        test_prompt, 
        {
            "ethical_constitutions": ["egos-base-ethical-constitution-v1", "egos-gdpr-ethical-constitution-v1"],
            "minimum_score": 0.8
        }
    )
    
    # Store the prompt with validation metadata
    if validation_result["validation_status"] == "VALID":
        prompt_record = pv.store_prompt(test_prompt, {
            "validation": validation_result,
            "creator": "example_user",
            "purpose": "education monitoring",
            "tags": ["education", "monitoring"]
        })
        print(f"Prompt stored with ID: {prompt_record['prompt_id']}")
    else:
        print("Prompt validation failed. Recommendations:")
        for recommendation in validation_result["validation_details"]["combined_recommendations"]:
            print(f"- {recommendation}")


def example_4_combined_constitution():
    """
    Example of creating and using a combined constitution from multiple sources.
    """
    print("\n=== Example 4: Combined Constitution ===")
    
    # Initialize validator
    validator = EthicalConstitutionValidator()
    validator.load_all_constitutions()
    
    # Create a combined constitution from multiple sources
    combined = validator.get_combined_constitution([
        "egos-base-ethical-constitution-v1", 
        "egos-gdpr-ethical-constitution-v1",
        "egos-healthcare-ethical-constitution-v1"
    ])
    
    if combined:
        print(f"Created combined constitution: {combined.name}")
        print(f"Total principles: {len(combined.principles)}")
        print(f"Total rules: {len(combined.rules)}")
        
        # Sample prompt to test the combined constitution
        test_prompt = """
        Create a system to analyze genetic data from patients to predict
        disease risk and automatically share results with insurance companies
        for premium adjustments.
        """
        
        # Custom validation using combined constitution
        result = validator.validate_prompt(test_prompt, combined.id)
        
        print(f"\nValidation Result:")
        print(f"Passed: {result.passed}")
        print(f"Score: {result.overall_score:.2f}")
        print(f"\nRecommendations: {len(result.recommendations)}")
        for recommendation in result.recommendations:
            print(f"- {recommendation}")


if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Run examples
    example_1_basic_validation()
    example_2_multiple_constitutions()
    example_3_promptvault_integration()
    example_4_combined_constitution()
    
    print("\nExamples complete.")