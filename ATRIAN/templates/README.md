@references:
  - ATRIAN/templates/README.md

# ATRiAN Ethical Constitution Templates

**Version:** 0.1.0  
**Last Modified:** 2025-06-12  
**Status:** Active Development (MVP)

## Overview

This directory contains the ethical constitution templates for the ATRiAN system. These templates form a core component of the EGOS MVP, providing "ethical governance at the prompt level" - a key differentiator in the AI governance market.

Ethical constitutions are structured frameworks that define ethical principles and rules for validating AI prompts against regulatory requirements and best practices. This implementation aligns with the EU AI Act and GDPR principles while supporting customization for different sectors and regulatory environments.

## Directory Structure

```
templates/
├── base/                   # Base ethical constitutions and schemas
│   ├── base_constitution.yaml        # Core ethical principles and rules
│   └── ethical_constitution_schema.py # Pydantic schemas for validation
├── regulatory/             # Regulation-specific constitutions
│   ├── eu_ai_act_constitution.yaml   # EU AI Act specific requirements
│   └── gdpr_constitution.yaml        # GDPR data protection requirements
├── sectorial/              # Industry-specific constitutions
│   └── healthcare_constitution.yaml  # Healthcare-specific ethics
├── integrations/           # Integration adapters
│   └── promptvault_adapter.py        # PromptVault integration
├── examples/               # Usage examples
│   └── validator_usage_example.py    # Example code
├── constitution_validator.py  # Core validation engine
└── README.md               # This file
```

## Key Components

### 1. Base Schema and Constitution

The foundation of the system is defined in `base/ethical_constitution_schema.py`, which provides Pydantic models for representing and validating ethical constitutions. The `base_constitution.yaml` implements the core EGOS principles derived from the Master Quantum Prompt.

### 2. Regulatory Frameworks

Specialized constitutions for regulatory compliance:
- `eu_ai_act_constitution.yaml`: Implements EU AI Act principles and risk-based approach
- `gdpr_constitution.yaml`: Implements GDPR data protection requirements

### 3. Sectorial Templates

Industry-specific ethical constitutions that extend the base and regulatory templates:
- `healthcare_constitution.yaml`: Healthcare-specific ethical considerations

### 4. Validation Engine

The `constitution_validator.py` module provides the core functionality for:
- Loading constitution templates
- Validating prompts against ethical principles and rules
- Providing detailed validation results with recommendations
- Supporting constitution inheritance and composition

### 5. Integration with PromptVault

The `integrations/promptvault_adapter.py` module provides adapters for integrating ATRiAN's ethical constitution templates with PromptVault, including:
- Prompt validation before storage
- Retrieving prompts with validation metadata
- Managing ethical constitution lifecycle

## Usage

### Basic Prompt Validation

```python
from templates.constitution_validator import EthicalConstitutionValidator

# Initialize validator
validator = EthicalConstitutionValidator()
validator.load_all_constitutions()

# Validate prompt against EU AI Act requirements
prompt = "Design a facial recognition system that automatically collects data..."
result = validator.validate_prompt(prompt, "egos-eu-ai-act-ethical-constitution-v1")

# Check if validation passed
if result.passed:
    print("Prompt is ethically valid!")
else:
    print("Ethical concerns detected:")
    for recommendation in result.recommendations:
        print(f"- {recommendation}")
```

### Integration with PromptVault

```python
from templates.integrations.promptvault_adapter import PromptVaultAdapter

# Initialize adapter
adapter = PromptVaultAdapter()

# Validate and store prompt
result = adapter.store_prompt_with_validation(
    prompt="Create a system to analyze user data...",
    constitution_ids=["egos-base-ethical-constitution-v1", "egos-gdpr-ethical-constitution-v1"],
    metadata={
        "creator": "user123",
        "purpose": "data analysis",
        "tags": ["analytics", "user_data"]
    }
)

# Check result
if result["status"] == "success":
    print(f"Prompt stored with ID: {result['prompt_id']}")
else:
    print("Validation failed. Recommendations:")
    for rec in result["validation"]["validation_details"]["combined_recommendations"]:
        print(f"- {rec}")
```

## Constitution Structure

Ethical constitutions follow a hierarchical structure:

1. **Principles**: High-level ethical values and guidelines (e.g., "Sacred Privacy")
2. **Rules**: Specific ethical requirements that implement principles
3. **Validation Logic**: Patterns and heuristics for detecting rule violations
4. **Recommendations**: Guidance for addressing ethical issues

The system supports inheritance and composition of constitutions, allowing for:
- Extension of base constitutions with specialized rules
- Combination of multiple regulatory frameworks
- Customization for specific domains and use cases

## Extending and Customizing

To create a new ethical constitution template:

1. Create a new YAML file in the appropriate directory (`regulatory/` or `sectorial/`)
2. Reference parent constitutions using the `parent_constitutions` list
3. Define specialized principles and rules
4. Configure validation behavior

See examples in `regulatory/` and `sectorial/` directories for the structure and patterns to follow.

## Integration with KOIOS PDD Validation

The ethical constitution validation system is designed to integrate with KOIOS Prompt Design Document (PDD) validation. This integration will be implemented in a future phase of the project.

## Development Roadmap

See the main [WORK_2025-06-12_Ethical_Constitution_Templates_MVP.md](../WORK_2025-06-12_Ethical_Constitution_Templates_MVP.md) file for the detailed development plan and current status.

✧༺❀༻∞ EGOS ∞༺❀༻✧

@references(level=1):
  - ATRIAN/WORK_2025-06-12_Ethical_Constitution_Templates_MVP.md