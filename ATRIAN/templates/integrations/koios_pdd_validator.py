"""
ATRiAN Ethical Constitution - KOIOS PDD Integration

This module provides integration between ATRiAN's ethical constitution validation
system and KOIOS Prompt Design Document (PDD) validation framework. It allows
ethical validation to be performed as part of the PDD validation process.

Version: 0.1.0
Last Modified: 2025-06-12
"""
# 
# @references:
#   - ATRIAN/templates/integrations/koios_pdd_validator.py
# 
from typing import Dict, List, Any, Optional, Union, Tuple
import os
import sys
from pathlib import Path
import logging
import json

# Import from ATRiAN ethical constitution validator
sys.path.append(str(Path(__file__).parent.parent.parent))
from templates.constitution_validator import (
    validate_prompt_with_constitutions,
    EthicalConstitutionValidator,
    ValidationResult
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_koios_integration")

class KoiosPddEthicalValidator:
    """
    Validator for KOIOS Prompt Design Documents that checks for compliance
    with ATRiAN ethical constitutions.
    """
    
    def __init__(self, constitution_dir: Optional[str] = None):
        """
        Initialize the validator.
        
        Args:
            constitution_dir: Directory containing ethical constitution templates
        """
        self.constitution_dir = constitution_dir or os.path.join(
            Path(__file__).parent.parent.parent,
            "templates"
        )
        
        # Initialize the validator
        self.validator = EthicalConstitutionValidator(self.constitution_dir)
        
        # Load all available constitutions
        self.available_constitutions = self.validator.load_all_constitutions()
        logger.info(f"Loaded {len(self.available_constitutions)} ethical constitutions")
    
    def get_available_constitutions(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns metadata for all available ethical constitutions.
        
        Returns:
            Dictionary mapping constitution IDs to basic metadata
        """
        result = {}
        for const_id, constitution in self.available_constitutions.items():
            result[const_id] = {
                "name": constitution.name,
                "description": constitution.description,
                "version": constitution.metadata.version,
                "applicable_domains": constitution.metadata.applicable_domains,
                "tags": constitution.metadata.tags,
                "regulatory_alignment": constitution.metadata.regulatory_alignment
            }
        return result
    
    def validate_pdd(self, pdd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a KOIOS Prompt Design Document against applicable ethical constitutions.
        
        Args:
            pdd_data: The PDD data to validate
            
        Returns:
            Validation result
        """
        # Determine which constitutions to use based on PDD metadata
        constitution_ids = self._determine_constitutions_for_pdd(pdd_data)
        
        # If no constitutions are specified or determined, use the base ethical constitution
        if not constitution_ids:
            constitution_ids = ["egos-base-ethical-constitution-v1"]
            
        # Extract prompt content from the PDD
        prompt_content = self._extract_prompts_from_pdd(pdd_data)
        
        # Validate each prompt against the constitutions
        validation_results = {}
        combined_passed = True
        combined_score = 0.0
        combined_recommendations = set()
        num_prompts = len(prompt_content)
        
        for prompt_key, prompt_text in prompt_content.items():
            # Validate this prompt
            result = validate_prompt_with_constitutions(prompt_text, constitution_ids)
            validation_results[prompt_key] = result
            
            # Update combined results
            combined_passed = combined_passed and result["passed"]
            combined_score += result["overall_score"] / num_prompts
            combined_recommendations.update(result["combined_recommendations"])
        
        # Create the final validation report
        validation_report = {
            "ethical_validation_passed": combined_passed,
            "ethical_validation_score": round(combined_score, 2),
            "ethical_validation_summary": (
                "All prompts comply with ethical standards" if combined_passed
                else "Some prompts raise ethical concerns"
            ),
            "applied_constitutions": constitution_ids,
            "prompt_validations": validation_results,
            "combined_recommendations": list(combined_recommendations),
            "validator_version": "ATRiAN Ethical Constitution Validator v0.1.0"
        }
        
        logger.info(f"Validated PDD: {validation_report['ethical_validation_summary']}, " +
                   f"Score: {validation_report['ethical_validation_score']:.2f}")
        
        return validation_report
    
    def _determine_constitutions_for_pdd(self, pdd_data: Dict[str, Any]) -> List[str]:
        """
        Determine which ethical constitutions should be applied to a PDD.
        
        Args:
            pdd_data: The PDD data
            
        Returns:
            List of constitution IDs to apply
        """
        constitutions = []
        
        # Always include the base constitution
        constitutions.append("egos-base-ethical-constitution-v1")
        
        # Check if the PDD metadata contains regulatory requirements
        if "metadata" in pdd_data:
            # Add EU AI Act constitution if relevant
            if "regulatory_compliance" in pdd_data["metadata"]:
                compliance = pdd_data["metadata"]["regulatory_compliance"]
                if isinstance(compliance, list):
                    if "EU_AI_ACT" in compliance:
                        constitutions.append("egos-eu-ai-act-ethical-constitution-v1")
                    if "GDPR" in compliance:
                        constitutions.append("egos-gdpr-ethical-constitution-v1")
                    
            # Add sector-specific constitutions if relevant
            if "domain" in pdd_data["metadata"]:
                domain = pdd_data["metadata"]["domain"]
                if domain == "HEALTHCARE":
                    constitutions.append("egos-healthcare-ethical-constitution-v1")
                # Add more sector-specific constitutions as they're developed
        
        # If specific constitutions are explicitly specified, use those instead
        if "ethical_constitutions" in pdd_data.get("metadata", {}):
            explicit_constitutions = pdd_data["metadata"]["ethical_constitutions"]
            if isinstance(explicit_constitutions, list) and explicit_constitutions:
                return explicit_constitutions
                
        return constitutions
    
    def _extract_prompts_from_pdd(self, pdd_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract all prompts from a PDD for validation.
        
        Args:
            pdd_data: The PDD data
            
        Returns:
            Dictionary mapping prompt IDs to prompt text
        """
        results = {}
        
        # Extract system prompt if present
        if "system_prompt" in pdd_data:
            results["system_prompt"] = pdd_data["system_prompt"]
        
        # Extract user prompt if present
        if "user_prompt" in pdd_data:
            results["user_prompt"] = pdd_data["user_prompt"]
        
        # Extract example prompts if present
        if "examples" in pdd_data and isinstance(pdd_data["examples"], list):
            for i, example in enumerate(pdd_data["examples"]):
                if "prompt" in example:
                    results[f"example_{i+1}"] = example["prompt"]
        
        # Extract any additional prompt variations
        if "prompt_variations" in pdd_data and isinstance(pdd_data["prompt_variations"], list):
            for i, variation in enumerate(pdd_data["prompt_variations"]):
                if isinstance(variation, str):
                    results[f"variation_{i+1}"] = variation
                elif isinstance(variation, dict) and "text" in variation:
                    results[f"variation_{i+1}"] = variation["text"]
        
        return results
    
    def koios_validator_plugin(self, pdd_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Plugin function that can be called from KOIOS PDD validation framework.
        
        Args:
            pdd_data: The PDD data to validate
            
        Returns:
            Tuple of (validation_passed, validation_details)
        """
        validation_results = self.validate_pdd(pdd_data)
        passed = validation_results["ethical_validation_passed"]
        
        # Format results for KOIOS validator
        report = {
            "ethical_validation": {
                "passed": passed,
                "score": validation_results["ethical_validation_score"],
                "message": validation_results["ethical_validation_summary"],
                "recommendations": validation_results["combined_recommendations"],
                "validator": "ATRiAN Ethical Constitution Validator",
                "details": validation_results
            }
        }
        
        return passed, report


# Example usage
if __name__ == "__main__":
    # Create validator
    validator = KoiosPddEthicalValidator()
    
    # List available constitutions
    print("Available ethical constitutions:")
    for const_id, meta in validator.get_available_constitutions().items():
        print(f"- {const_id}: {meta['name']}")
    
    # Example PDD
    example_pdd = {
        "metadata": {
            "name": "Example Prompt Design Document",
            "version": "1.0.0",
            "author": "EGOS Team",
            "domain": "HEALTHCARE",
            "regulatory_compliance": ["EU_AI_ACT", "GDPR"]
        },
        "system_prompt": "You are a helpful healthcare assistant. Always maintain privacy and confidentiality.",
        "user_prompt": "Analyze the following patient data and suggest treatment options.",
        "examples": [
            {"prompt": "The patient is a 45-year-old male with diabetes type 2."},
            {"prompt": "Please create a demographic profile of patients based on medical records."}
        ]
    }
    
    # Validate PDD
    validation_result = validator.validate_pdd(example_pdd)
    
    # Print results
    print("\nValidation Result:")
    print(f"Passed: {validation_result['ethical_validation_passed']}")
    print(f"Score: {validation_result['ethical_validation_score']}")
    
    if validation_result['combined_recommendations']:
        print("\nRecommendations:")
        for rec in validation_result['combined_recommendations']:
            print(f"- {rec}")
    
    # Print individual prompt validations
    print("\nIndividual Prompt Validations:")
    for prompt_id, result in validation_result['prompt_validations'].items():
        print(f"  {prompt_id}: {'✓' if result['passed'] else '✗'} ({result['overall_score']:.2f})")