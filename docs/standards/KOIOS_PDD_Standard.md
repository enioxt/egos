---
title: KOIOS Prompt Design Document (PDD) Standard
version: 1.1.0
status: Active
date_created: 2025-05-10
date_modified: 2025-06-10
authors: [EGOS Team, Cascade AI]
description: "Defines the standard structure, content requirements, validation procedures, and best practices for creating Prompt Design Documents (PDDs) within the EGOS project. This standard supports a hierarchical schema system for PDDs, validated by `validate_pdd.py`, ensuring clarity, consistency, and effectiveness in prompt engineering under KOIOS governance."
file_type: standard
scope: project-wide
primary_entity_type: prompt_design_standard
primary_entity_name: KOIOS Prompt Design Document Standard
tags: [koios, pdd, prompt_design, standard, ai_interaction, coruja, documentation_standard, schema, validation, pydantic, hierarchical_schema]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/KOIOS_PDD_Standard.md

# KOIOS Standard: Prompt Design Document (PDD)

**Status:** Active
**Version:** 1.1.0
**Owner:** KOIOS Team
**Last Updated:** 2025-06-10

## 1. Introduction

This document defines the standard format and best practices for creating Prompt Design Documents (PDDs) within the EGOS system. PDDs are essential artifacts for managing, versioning, and standardizing the prompts used by the CORUJA subsystem and other AI interaction points.

Adherence to this standard ensures consistency, facilitates validation, enables better prompt management, and supports ethical review processes.

## 2. PDD Purpose

PDDs serve several key purposes:
*   **Standardization:** Define a consistent structure for all prompts, supporting a hierarchical schema system (e.g., base and specialized PDD types).
*   **Clarity:** Clearly document the prompt's intent, parameters, expected behavior, and its specific schema type (`pdd_type`).
*   **Validation:** Enable robust, automated validation of PDD YAML files against their declared Pydantic schemas using the `validate_pdd.py` script (located in `c:\EGOS\subsystems\KOIOS\schemas\`). This ensures structural integrity and adherence to defined constraints (e.g., no extra fields).
*   **Versioning:** Track changes to prompts over time using the `version` field within the PDD.
*   **Discoverability:** Facilitate finding and reusing prompts through standardized metadata and location.
*   **Ethical Governance:** Provide a designated place (`ethik_guidelines`) to specify ETHIK guidelines relevant to the prompt.
*   **Collaboration:** Offer a shared, validated format for teams designing, reviewing, and utilizing prompts.
*   **Automation:** Serve as a machine-readable definition for tools that consume or manage prompts.

## 3. PDD File Format and Location

*   **Format:** YAML (`.yaml` extension).
*   **Encoding:** UTF-8.
*   **Location:** Stored within the `c:\EGOS\docs\prompts\pdds\` directory.
*   **Naming Convention:** Filenames MUST use `snake_case` and correspond directly to the `id` field within the PDD (e.g., `generate_python_docstring.yaml` must contain `id: generate_python_docstring`).
*   **Schema Type Declaration:** Each PDD YAML file MUST include a `pdd_type` field (e.g., `pdd_type: base` or `pdd_type: specialized_handler`). This field determines which Pydantic schema will be used by `validate_pdd.py` for validation.

## 4. PDD Schema Definition

The authoritative definition of PDD structures is provided by Pydantic models located in `c:\EGOS\subsystems\KOIOS\schemas\pdd_schema.py`. This file defines a hierarchical schema system, allowing for a base PDD type and specialized PDD types.

All PDD schemas enforce strict validation by setting `model_config = {"extra": "forbid"}` in their Pydantic class definition. This means that PDD YAML files cannot contain any fields not explicitly defined in their corresponding schema, preventing unexpected or erroneous data.

### 4.1. Schema Selection via `pdd_type`

Each PDD YAML file **MUST** include a `pdd_type` field. The value of this field (e.g., `base`, `specialized_handler`) is used by the `validate_pdd.py` script to determine which Pydantic schema to use for validating that specific PDD file.

Example:
```yaml
# In your PDD YAML file:
pdd_type: base 
# ... other PDD fields
```
or
```yaml
# In your PDD YAML file:
pdd_type: specialized_handler
# ... other PDD fields
```

### 4.2. Base PDD Schema (`PddSchema`)

The `PddSchema` is the foundational schema from which all specialized PDD schemas should inherit (or which can be used directly for generic PDDs by specifying `pdd_type: base`).

#### 4.2.1. Required Fields for `PddSchema`:

*   **`id`** (string): A unique, `snake_case` identifier for the PDD. This MUST match the filename (without extension).
    *   Example: `generate_python_docstring`
*   **`name`** (string): A human-readable name for the prompt.
    *   Example: "Python Docstring Generator"
*   **`description`** (string): A concise explanation of the prompt's purpose and functionality.
    *   Example: "Generates a Python docstring for a given function signature and code context."
*   **`version`** (string): Semantic versioning for the PDD (e.g., "1.0.0", "0.2.1-alpha").
    *   Example: "1.0.0"
*   **`parameters`** (list[string]): A list of placeholder names (variables) used within the `template`. These are the inputs the prompt expects.
    *   Example: `["function_signature", "code_context"]`
*   **`template`** (string): The core prompt text, using curly braces `{}` to denote placeholders defined in `parameters`.
    *   Example: "Given the function signature `{function_signature}` and the code context:\n```python\n{code_context}\n```\nPlease generate a comprehensive Python docstring."

#### 4.2.2. Optional Fields for `PddSchema`:

*   **`metadata`** (object: `PddMetadata`): Contains metadata about the PDD.
    *   `author` (string, optional): The author or team responsible for the PDD. Example: "Coruja Team"
    *   `created_date` (string, optional): Date of creation (YYYY-MM-DD). Example: "2025-06-10"
    *   `last_updated` (string, optional): Date of last update (YYYY-MM-DD). Example: "2025-06-10"
    *   `tags` (list[string], optional): Keywords for categorization and search. Example: `["python", "code_generation", "documentation"]`
    *   `related_pdds` (list[string], optional): IDs of other related PDDs. Example: `["refactor_python_code"]`
*   **`ethik_guidelines`** (object: `PddEthikGuidelines`): Specifies ethical considerations for the prompt.
    *   `pii_handling` (string, optional): Instructions on handling Personally Identifiable Information. Example: "Ensure all PII is anonymized before processing."
    *   `bias_mitigation_ref` (string, optional): Reference to bias mitigation strategies or documents. Example: "Refer to EGOS Bias Mitigation Guide v1.2"
    *   `forbidden_topics` (list[string], optional): List of topics the prompt should not engage with. Example: `["hate_speech", "illegal_activities"]`
    *   `output_tone` (string, optional): Desired tone for the AI's output. Example: "Formal and objective"

### 4.3. Specialized PDD Schemas (Example: `SpecializedHandlerPddSchema`)

Specialized PDDs cater to specific use cases that require additional fields beyond the base schema. They inherit from `PddSchema` and add their own unique fields. To use a specialized schema, set the `pdd_type` field in the YAML file to the name registered for that schema in `validate_pdd.py` (e.g., `pdd_type: specialized_handler`).

#### 4.3.1. Example: `SpecializedHandlerPddSchema`

This schema might be used for prompts that interact with specific backend handlers or require a particular response structure.

**Additional Required Fields (example for `SpecializedHandlerPddSchema`):**

*   **`handler_type`** (string): Specifies the type of handler this prompt is designed for.
    *   Example: "ZendeskTicketProcessor"
*   **`response_format`** (string): Defines the expected format of the response (e.g., "json", "xml", "text_summary").
    *   Example: "json"

**Additional Optional Fields (example for `SpecializedHandlerPddSchema`):**
*   **(Specific fields relevant to the specialized handler type)**

### 4.4. Example PDD YAML Structures

#### 4.4.1. Example: Base PDD (`pdd_type: base`)

```yaml
# c:\EGOS\docs\prompts\pdds\generate_python_docstring.yaml
pdd_type: base
id: generate_python_docstring
name: Python Docstring Generator
description: Generates a Python docstring for a given function signature and code context.
version: "1.0.0"
parameters:
  - function_signature
  - code_context
template: |
  Given the function signature `{function_signature}` and the code context:
  ```python
  {code_context}
  ```
  Please generate a comprehensive Python docstring.
metadata:
  author: EGOS Core Team
  created_date: "2025-06-01"
  last_updated: "2025-06-10"
  tags:
    - python
    - code_generation
    - documentation
ethik_guidelines:
  output_tone: Formal and objective
```

#### 4.4.2. Example: Specialized PDD (`pdd_type: specialized_handler`)

```yaml
# c:\EGOS\docs\prompts\pdds\coruja_zendesk_ticket_analysis_v1.yaml
pdd_type: specialized_handler # Specifies usage of SpecializedHandlerPddSchema
id: coruja_zendesk_ticket_analysis_v1
name: Coruja Zendesk Ticket Analysis v1
description: Analyzes Zendesk ticket content for categorization and sentiment.
version: "1.0.0"
parameters:
  - ticket_subject
  - ticket_body
template: |
  Analyze the following Zendesk ticket:
  Subject: {ticket_subject}
  Body: {ticket_body}
  Provide a JSON response with 'category' and 'sentiment' fields.
# Fields from base PddSchema
metadata:
  author: Coruja Subsystem Team
  created_date: "2025-05-15"
  last_updated: "2025-06-10"
  tags:
    - zendesk
    - ticket_analysis
    - nlp
    - coruja
# Additional fields for SpecializedHandlerPddSchema
handler_type: ZendeskTicketProcessor 
response_format: json
ethik_guidelines:
  pii_handling: All user identifiable information must be redacted from logs.
  bias_mitigation_ref: Adhere to Coruja Bias Mitigation v1.0.
```

## 5. Best Practices for PDD Creation

*   **Clarity and Conciseness:** Write clear and unambiguous descriptions, names, and template text.
*   **Unique IDs:** Ensure `id` is unique across all PDDs and matches the filename. Use `snake_case`.
*   **Semantic Versioning:** Use `version` (e.g., "1.0.0", "1.0.1", "2.0.0-beta") to track significant changes.
*   **Effective Parameters:** Define parameters clearly. Use descriptive names.
*   **Informative Metadata:** Populate `metadata` fields thoroughly to aid discoverability and context. Use relevant `tags`.
*   **Comprehensive ETHIK Guidelines:** Clearly specify ethical considerations in `ethik_guidelines`.
*   **Choose Correct `pdd_type`:** Always specify the `pdd_type` field. Ensure it matches one of the types recognized by `validate_pdd.py` (e.g., `base`, `specialized_handler`). If creating a new specialized PDD type, ensure its schema is defined in `pdd_schema.py` and registered in `validate_pdd.py`.
*   **Adhere to Schema:** Strictly follow the field definitions for the chosen `pdd_type`. Do not add extra fields not defined in the schema, as `validate_pdd.py` enforces `extra = "forbid"`.
*   **Iterative Refinement:** Test prompts derived from PDDs thoroughly and iterate on the PDD content for optimal performance and safety.
*   **Regular Validation:** Validate PDDs using `validate_pdd.py` after any modification and before committing changes.

## 6. Template

A template file is available at `docs/templates/PDD_Template.yaml`.

## 7. Validation

PDD YAML files are validated using the `validate_pdd.py` script located in `c:\EGOS\subsystems\KOIOS\schemas\`. This script leverages Pydantic models defined in `pdd_schema.py` to perform the validation.

**How to Validate:**

1.  Ensure you have Python installed with `Pydantic` and `PyYAML` libraries.
    (These are typically managed by the project's dependency management, e.g., `requirements.txt`).
2.  Open a terminal or command prompt in the EGOS project root directory (`c:\EGOS\`).
3.  Run the validation script, providing the path to the PDD file you want to validate:
    ```bash
    python subsystems\KOIOS\schemas\validate_pdd.py docs\prompts\pdds\your_pdd_filename.yaml
    ```
    Replace `your_pdd_filename.yaml` with the actual name of your PDD file.

**Validation Output:**

*   **Success:** If the PDD is valid according to its declared `pdd_type` and corresponding schema, the script will print a success message, e.g.:
    `SUCCESS: docs\prompts\pdds\your_pdd_filename.yaml is valid against schema for pdd_type: <type>.`
*   **Failure:** If the PDD is invalid, the script will print an error message detailing the validation errors (e.g., missing fields, incorrect data types, extra fields not allowed). Example:
    `ERROR: docs\prompts\pdds\your_pdd_filename.yaml FAILED validation for pdd_type: <type>.`
    `Error details: <Pydantic validation error messages>`

The script dynamically loads the correct Pydantic schema based on the `pdd_type` field specified within the PDD YAML file. All schemas enforce `model_config = {"extra": "forbid"}`, meaning no undefined fields are permitted in the PDD.

## 8. Version History

*   **v1.1.0 (2025-06-10):**
    *   Updated to reflect hierarchical PDD schema system (`pdd_schema.py`) and `pdd_type` field.
    *   Detailed base schema (`PddSchema`) and specialized schema concepts (e.g., `SpecializedHandlerPddSchema`).
    *   Updated validation process to use `validate_pdd.py` script.
    *   Added examples for base and specialized PDD YAML.
    *   Emphasized strict validation (`extra = "forbid"`).
    *   Expanded best practices and validation instructions.
*   **v1.0.1 (2025-05-17):**
    *   Minor updates to descriptions and tags. (Assumed from previous frontmatter)
*   **v0.1 (YYYY-MM-DD):** Initial draft.