@references:
  - subsystems/KOIOS/schemas/README.md

# KOIOS PDD Schema and Validation Utilities

This directory contains the core components for defining and validating Prompt Design Documents (PDDs) within the EGOS ecosystem, under the governance of the KOIOS subsystem.

## Overview

The KOIOS PDD system utilizes Pydantic for defining robust, hierarchical schemas for PDDs and a Python script for validating PDD YAML files against these schemas. This ensures that all PDDs are well-structured, conform to predefined standards, and are machine-readable, facilitating automation and integration across EGOS tools.

Key principles:
- **Schema-Driven:** PDD structures are explicitly defined using Pydantic models.
- **Hierarchical:** Supports a base PDD schema and specialized PDD schemas for different prompt types.
- **Strict Validation:** No undefined fields are allowed in PDDs, ensuring precision.
- **Dynamic Loading:** The validation script selects the appropriate schema based on a `pdd_type` field in the PDD YAML.

## Files

### 1. `pdd_schema.py`

This Python script defines the Pydantic models that constitute the PDD schemas.

- **`PddSchema` (Base Schema):** The foundational PDD schema containing common fields required for all PDDs (e.g., `id`, `name`, `description`, `version`, `parameters`, `template`, `metadata`, `ethik_guidelines`).
- **Specialized Schemas (e.g., `SpecializedHandlerPddSchema`):** These schemas inherit from `PddSchema` and add fields specific to particular types of prompts or handlers. They allow for extending the PDD structure in a controlled manner.
- **Strict Validation (`model_config = {"extra": "forbid"}`):** All PDD schemas are configured to disallow any fields not explicitly defined in the model. This ensures that PDD YAML files strictly adhere to their intended structure.

### 2. `validate_pdd.py`

This Python script is the command-line tool used to validate PDD YAML files.

- **Purpose:** To check if a given PDD YAML file conforms to its declared PDD schema (as defined in `pdd_schema.py`).
- **Usage:**
  ```bash
  python c:\EGOS\subsystems\KOIOS\schemas\validate_pdd.py <path_to_pdd_file.yaml>
  ```
  Example:
  ```bash
  python c:\EGOS\subsystems\KOIOS\schemas\validate_pdd.py c:\EGOS\docs\prompts\pdds\generate_python_docstring.yaml
  ```
- **Dynamic Schema Loading:** The script reads the `pdd_type` field from the PDD YAML file (e.g., `pdd_type: base` or `pdd_type: specialized_handler`). It then uses this value to select and instantiate the corresponding Pydantic schema from `pdd_schema.py` for validation.
- **Output:**
    - **Success:** Prints a success message indicating the PDD is valid and specifies the schema used.
      `SUCCESS: <path_to_pdd_file.yaml> is valid against schema for pdd_type: <type>.`
    - **Failure:** Prints an error message detailing the validation errors (e.g., missing required fields, incorrect data types, extra fields not allowed).
      `ERROR: <path_to_pdd_file.yaml> FAILED validation for pdd_type: <type>.`
      `Error details: <Pydantic validation error messages>`

## Dependencies

To use these utilities, ensure you have the following Python libraries installed:
- `Pydantic` (for schema definition and validation)
- `PyYAML` (for loading YAML files)

These are typically listed in the project's `requirements.txt` file.

## Extending the PDD Schema System

To add a new type of specialized PDD:
1.  **Define the Schema:** In `pdd_schema.py`, create a new Pydantic class that inherits from `PddSchema` (or another relevant specialized schema). Add any new required or optional fields specific to this new PDD type.
2.  **Register the Schema:** In `validate_pdd.py`, update the `SCHEMA_REGISTRY` dictionary to include a mapping from a new `pdd_type` string (e.g., `"new_special_type"`) to your newly created Pydantic schema class.
3.  **Create PDDs:** Authors can now create PDD YAML files specifying `pdd_type: new_special_type` and include the fields defined in your new schema. These can then be validated using `validate_pdd.py`.

Refer to the [KOIOS PDD Standard](file:///C:/EGOS/docs/standards/KOIOS_PDD_Standard.md) for comprehensive details on PDD fields, best practices, and examples.