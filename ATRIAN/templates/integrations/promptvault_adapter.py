"""
ATRiAN Ethical Constitution - PromptVault Integration Adapter

This module provides the integration layer between ATRiAN's ethical constitution
validation capabilities and the PromptVault system. It implements the necessary
adapters and connectors to validate prompts against ethical constitutions during
storage and retrieval operations.

Version: 0.1.0
Last Modified: 2025-06-12
"""
# 
# @references:
#   - ATRIAN/templates/integrations/promptvault_adapter.py
# 
from typing import Dict, List, Any, Optional
import os
import json
import logging
from pathlib import Path
import sys

# Import from ATRiAN ethical constitution validator
sys.path.append(str(Path(__file__).parent.parent.parent))
from templates.constitution_validator import (
    validate_prompt_with_constitutions,
    EthicalConstitutionValidator
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_promptvault_adapter")


class PromptVaultAdapter:
    """
    Adapter class that connects ATRiAN's ethical constitution validation
    capabilities with the PromptVault system.
    """
    
    def __init__(self, promptvault_api_url=None, constitution_dir=None):
        """
        Initialize the adapter with connection to PromptVault API
        and the ethical constitution validator.
        
        Args:
            promptvault_api_url: URL of the PromptVault API endpoint
            constitution_dir: Directory containing ethical constitution templates
        """
        self.promptvault_api_url = promptvault_api_url or os.environ.get(
            "PROMPTVAULT_API_URL", "http://localhost:8080/api/promptvault"
        )
        self.constitution_dir = constitution_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "templates"
        )
        
        # Initialize the ethical constitution validator
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
    
    def validate_prompt(
        self, 
        prompt: str, 
        constitution_ids: List[str] = None,
        validation_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate a prompt against ethical constitutions before storing in PromptVault.
        
        Args:
            prompt: The prompt text to validate
            constitution_ids: List of constitution IDs to validate against
            validation_config: Additional validation configuration
            
        Returns:
            Validation result
        """
        # Use default constitutions if none specified
        if not constitution_ids:
            constitution_ids = ["egos-base-ethical-constitution-v1"]
        
        # Apply any additional validation configuration
        config = validation_config or {}
        
        # Validate prompt against specified constitutions
        validation_result = validate_prompt_with_constitutions(prompt, constitution_ids)
        
        # Determine validation status based on results and configuration
        min_score = config.get("minimum_score", 0.75)
        validation_status = "VALID" if validation_result["passed"] and validation_result["overall_score"] >= min_score else "INVALID"
        
        # Create complete validation response
        response = {
            "validation_status": validation_status,
            "validation_score": validation_result["overall_score"],
            "validation_details": validation_result,
            "validator": "ATRiAN Ethical Constitution Validator v0.1.0"
        }
        
        logger.info(f"Validated prompt against {len(constitution_ids)} constitutions: " +
                   f"Status={validation_status}, Score={validation_result['overall_score']:.2f}")
        
        return response
    
    def store_prompt_with_validation(
        self, 
        prompt: str, 
        constitution_ids: List[str] = None, 
        metadata: Dict[str, Any] = None,
        auto_validate: bool = True
    ) -> Dict[str, Any]:
        """
        Store a prompt in PromptVault with ethical validation.
        
        Args:
            prompt: The prompt text to store
            constitution_ids: List of constitution IDs to validate against
            metadata: Additional metadata for the prompt
            auto_validate: Whether to automatically validate the prompt
            
        Returns:
            Result of the storage operation
        """
        # Prepare metadata
        meta = metadata or {}
        
        # Validate prompt if requested
        if auto_validate:
            validation_result = self.validate_prompt(
                prompt, 
                constitution_ids=constitution_ids,
                validation_config=meta.get("validation_config")
            )
            
            # Add validation results to metadata
            meta["validation"] = validation_result
            
            # Don't store invalid prompts if configured to block them
            if (validation_result["validation_status"] == "INVALID" and 
                meta.get("validation_config", {}).get("block_invalid", False)):
                logger.warning("Prompt storage blocked due to failed ethical validation")
                return {
                    "status": "rejected",
                    "reason": "Failed ethical validation",
                    "validation": validation_result
                }
        
        # TODO: Implement actual PromptVault API call when available
        # For now, just return a mock response
        logger.info(f"Would store prompt in PromptVault (mock): {prompt[:30]}...")
        
        return {
            "status": "success",
            "prompt_id": "pv-" + os.urandom(4).hex(),
            "validation": meta.get("validation"),
            "message": "Prompt stored successfully (mock implementation)"
        }
    
    def retrieve_prompt_with_validation(
        self, 
        prompt_id: str, 
        validate_again: bool = False,
        constitution_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a prompt from PromptVault with optional re-validation.
        
        Args:
            prompt_id: ID of the prompt to retrieve
            validate_again: Whether to re-validate the prompt on retrieval
            constitution_ids: List of constitution IDs to validate against
            
        Returns:
            Retrieved prompt with metadata
        """
        # TODO: Implement actual PromptVault API call when available
        # For now, just return a mock response
        mock_prompt = "This is a mock prompt retrieved from PromptVault."
        mock_metadata = {
            "creator": "example_user",
            "created_at": "2025-06-12T12:00:00Z",
            "tags": ["example", "mock"],
            "validation": {
                "validation_status": "VALID",
                "validation_score": 0.85
            }
        }
        
        logger.info(f"Retrieved mock prompt with ID: {prompt_id}")
        
        # Re-validate if requested
        if validate_again:
            validation_result = self.validate_prompt(
                mock_prompt, 
                constitution_ids=constitution_ids
            )
            mock_metadata["revalidation"] = validation_result
        
        return {
            "prompt_id": prompt_id,
            "prompt_text": mock_prompt,
            "metadata": mock_metadata
        }


# Example usage
if __name__ == "__main__":
    # Create adapter
    adapter = PromptVaultAdapter()
    
    # List available constitutions
    print("Available ethical constitutions:")
    for const_id, meta in adapter.get_available_constitutions().items():
        print(f"- {const_id}: {meta['name']}")
    
    # Example prompt
    test_prompt = """
    Create an AI system to monitor and analyze social media posts to identify 
    political leanings and create user profiles for targeted advertising.
    """
    
    # Validate and store prompt
    result = adapter.store_prompt_with_validation(
        test_prompt,
        constitution_ids=["egos-base-ethical-constitution-v1", "egos-gdpr-ethical-constitution-v1"],
        metadata={
            "creator": "test_user",
            "purpose": "social media analysis",
            "tags": ["social_media", "profiling"],
            "validation_config": {
                "minimum_score": 0.75,
                "block_invalid": True
            }
        }
    )
    
    # Print result
    print(f"\nStore result: {result['status']}")
    if "validation" in result:
        print(f"Validation status: {result['validation']['validation_status']}")
        print(f"Validation score: {result['validation']['validation_score']:.2f}")
        
        if result['validation']['validation_status'] == "INVALID":
            print("\nRecommendations:")
            for rec in result['validation']['validation_details']['combined_recommendations']:
                print(f"- {rec}")