---
title: cross_reference_guidelines
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: cross_reference_guidelines
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/project/archived_project_principles/principles_archive/cross_reference_guidelines.md

---
title: EGOS Cross-Reference Guidelines
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

# EGOS Cross-Reference Guidelines

---
version: "1.0.0"
status: "Draft"
date: "2025-05-06"
authors:
  - "Cascade (Windsurf)"
  - "USER (Enio)"
description: "Defines the standard for metadata and cross-referencing within all EGOS project files to ensure clarity, discoverability, and effective navigation for both human developers and AI systems."
file_type: "Documentation"
scope: "Project"
primary_entity_type: "EGOS"
primary_entity_name: "EGOS Project Governance"
tags:
  - "documentation_standard"
  - "metadata"
  - "cross_reference"
  - "koios"
  - "governance"
egos_principles_applied:
  - "SystemicCartography"
  - "ConsciousModularity"
  - "IntegratedEthics"
koios_compliance_level: "Full"
ethik_validation_status: "NotAssessed"
cross_reference_verified: false
verification_date: ""
verified_by: ""
---

## 1. Introduction

These guidelines establish the standardized approach for embedding metadata and creating cross-references within all files in the EGOS project. Adherence to these standards is crucial for:

*   **Clarity**: Providing immediate context about a file's purpose, status, and relationships.
*   **Discoverability**: Enabling efficient searching and filtering of project assets.
*   **Navigability**: Allowing both human developers and AI systems (like Cascade) to understand dependencies and navigate the codebase effectively.
*   **Maintainability**: Facilitating easier updates and impact analysis when changes are made.

This document is a cornerstone of the **KOIOS Documentation System** and aligns with the **Systemic Cartography** and **Conscious Modularity** core principles of EGOS.

## 2. Metadata Standard

All critical files (documentation, scripts, core source code modules, configuration files) MUST include a metadata block at the beginning of the file.

*   **Markdown Files (.md)**: Use YAML frontmatter (between `---` delimiters).
*   **Python Files (.py)**: Use a multi-line string block (e.g., `"""METADATA"""`) immediately after the (optional) shebang and encoding lines, before any import statements. The content within the string should be YAML-formatted.
*   **Other Script/Configuration Files**: Adapt the Python approach (structured comment block with YAML content) as appropriate for the file type.

### 2.1. Metadata Fields

The following fields constitute the standard metadata block. Fields are categorized by their primary purpose.

#### 2.1.1. Identification & Status

| Field             | Obligation | Type          | Description                                                                                                |
|-------------------|------------|---------------|------------------------------------------------------------------------------------------------------------|
| `title`           | Mandatory  | String        | Descriptive title of the file's content.                                                                   |
| `id`              | Optional   | String (UUID) | A unique identifier for the file, if path-based identification is insufficient (e.g., for database linking). |
| `version`         | Mandatory  | String        | Semantic version (e.g., "1.0.2") of the file/document itself, not necessarily the project version.         |
| `status`          | Mandatory  | String        | Current lifecycle status. Enum: `Draft`, `InReview`, `Approved`, `Active`, `Deprecated`, `Archived`.         |
| `date_created`    | Recommended| String (Date) | YYYY-MM-DD format; the date the file was initially created.                                                |
| `date_modified`   | Mandatory  | String (Date) | YYYY-MM-DD format; the date of the last significant modification to the file's content or metadata.      |
| `authors`         | Mandatory  | List (String) | List of primary authors or responsible teams. Include AI assistants if co-authored (e.g., "Cascade (Windsurf)"). |
| `description`     | Mandatory  | String        | Concise summary (1-3 sentences) of the file's purpose, content, and relevance.                             |

#### 2.1.2. Classification & Scope

| Field                   | Obligation | Type   | Description                                                                                                                               |
|-------------------------|------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `file_type`             | Mandatory  | String | Type of the file. Enum: `Documentation`, `Script`, `SourceCodeModule`, `Configuration`, `Data`, `Test`, `InterfaceDefinition`, `Notebook`, `Other`. |
| `scope`                 | Mandatory  | String | The broad area of the project this file belongs to. Enum: `Project`, `Subsystem`, `App`, `Tool`, `Module`, `Interface`.                    |
| `primary_entity_type`   | Mandatory  | String | The type of the main EGOS entity this file describes or is part of. Enum: `EGOS`, `Subsystem`, `App`, `Tool`, `Module`, `Interface`, `Process`. |
| `primary_entity_name`   | Mandatory  | String | The specific name of the primary entity (e.g., "CORUJA", "UserAuthService", "CrossReferenceUpdater", "ReorganizationProcessMay2025").         |

#### 2.1.3. Discovery & Organization

| Field | Obligation | Type          | Description                                                        |
|-------|------------|---------------|--------------------------------------------------------------------|
| `tags`  | Recommended| List (String) | Keywords for searchability and categorization (use `snake_case`). |

#### 2.1.4. Relationships & Dependencies

Use relative paths as described in Section 3.

| Field        | Obligation | Type        | Description                                                                                                                                    |
|--------------|------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `depends_on` | Recommended| List(Object)| List of files/modules this file requires to function correctly or to be fully understood. Each object has `path` (String) and `description` (String). |
| `related_to` | Recommended| List(Object)| List of files/modules that are strongly related but not strict dependencies. Each object has `path` (String) and `description` (String).         |

_Example for `depends_on` or `related_to`:_
```yaml
depends_on:
  - path: "../../scripts/utils/data_parser.py"
    description: "Utilizes data parsing functions."
  - path: "../../config/coruja_config.yaml"
    description: "Reads configuration for CORUJA subsystem."
```

#### 2.1.5. Type-Specific Fields

##### For `file_type: Script`

| Field             | Obligation | Type   | Description                                                                                                   |
|-------------------|------------|--------|---------------------------------------------------------------------------------------------------------------|
| `entry_point`     | Optional   | String | Name of the main function or execution point if the script is directly runnable (e.g., "main", "run_analysis"). |
| `inputs`          | Recommended| String | Description of expected inputs, parameters, environment variables, or data sources.                           |
| `outputs`         | Recommended| String | Description of outputs, generated files, side effects, or return values.                                      |
| `usage_examples`  | Recommended| String | Multi-line string showing example command(s) or import statements and function calls. Use `mdc:` paths.       |

_Example `usage_examples`:_
```yaml
usage_examples: |
  """
  # To run from project root
  python scripts/tools/my_tool.py --input data/input.csv --output data/output.json

  # As a module
  from subsystems.my_module.utils import useful_function
  result = useful_function(data)
  """
```

##### For `file_type: SourceCodeModule` (in addition to comprehensive docstrings within the code)

| Field            | Obligation | Type          | Description                                         |
|------------------|------------|---------------|-----------------------------------------------------|
| `main_classes`   | Optional   | List (String) | Key classes defined or primarily managed by this module. |
| `main_functions` | Optional   | List (String) | Key functions/methods central to this module's API.    |

#### 2.1.6. EGOS Compliance & Principles

| Field                      | Obligation | Type          | Description                                                                                                          |
|----------------------------|------------|---------------|----------------------------------------------------------------------------------------------------------------------|
| `egos_principles_applied`  | Recommended| List (String) | List of EGOS Core Principles most relevant to or embodied by this file (e.g., "ConsciousModularity", "SystemicCartography"). |
| `koios_compliance_level`   | Recommended| String        | Level of adherence to KOIOS documentation standards. Enum: `Full`, `Partial`, `None`, `NotApplicable`.                |
| `ethik_validation_status`  | Recommended| String        | Level of ETHIK ethical review applied or needed. Enum: `High`, `Medium`, `Low`, `NotAssessed`, `NotApplicable`.       |

#### 2.1.7. Cross-Reference Verification

| Field                        | Obligation | Type          | Description                                                                                              |
|------------------------------|------------|---------------|----------------------------------------------------------------------------------------------------------|
| `cross_reference_verified` | Recommended| Boolean       | Status of whether the cross-references (`mdc:` links) within this file have been verified as valid.        |
| `verification_date`        | Recommended| String (Date) | YYYY-MM-DD format; the date of the last cross-reference verification for this file.                      |
| `verified_by`              | Recommended| String        | Name of the human or script that performed the last verification (e.g., "John Doe", "CrossRefValidatorScript"). |

### 2.2. Example Metadata Block (Markdown/YAML Frontmatter)

```yaml
---
title: "CORUJA Subsystem Overview"
id: "doc-coruja-overview-v1"
version: "1.1.0"
status: "Active"
date_created: "2024-11-10"
date_modified: "2025-05-01"
authors:
  - "AI Team"
  - "Cascade (Windsurf)"
description: "Provides a high-level overview of the CORUJA subsystem, its architecture, core components, and responsibilities within the EGOS project."
file_type: "Documentation"
scope: "Subsystem"
primary_entity_type: "Subsystem"
primary_entity_name: "CORUJA"
tags:
  - "coruja"
  - "subsystem_overview"
  - "architecture"
depends_on:
  - path: "../core/principles/EGOS_CORE_PRINCIPLES.md"
    description: "CORUJA adheres to these core principles."
related_to:
  - path: "../../../subsystems/CORUJA/src/main.py"
    description: "Main source code for CORUJA."
  - path: "../../../config/coruja_config.yaml"
    description: "Configuration file for CORUJA."
egos_principles_applied:
  - "ConsciousModularity"
  - "SystemicCartography"
  - "IntegratedEthics"
koios_compliance_level: "Full"
ethik_validation_status: "Medium"
cross_reference_verified: true
verification_date: "2025-05-05"
verified_by: "CrossRefValidatorScript"
---
```

## 3. Cross-Reference Path Convention

EGOS uses **simple relative paths** for cross-references within documentation. This approach ensures compatibility with standard Markdown renderers, GitHub, and other documentation platforms while maintaining clear relationships between files.

*   **Format**: `../path/to/file.extension` (relative to the current file location)
*   **Usage**: Should be used in all `depends_on`, `related_to` fields, and within documentation content when linking to other project files.
*   **Benefits**: Works natively with most Markdown renderers, requires no special processing, and is easy to validate with standard tools.

**Examples:**

*   From a file in `docs/subsystems/CORUJA/` linking to a file in `docs/core/principles/`:
    `../../core/principles/cross_reference_guidelines.md`
*   From a file in `docs/processes/` linking to a file in `scripts/tools/`:
    `../../scripts/tools/data_importer.py`
*   From a file in `docs/subsystems/MYCELIUM/` linking to a file in `apps/dashboard/`:
    `../../../apps/dashboard/static/css/main.css`

## 4. File and Directory Naming Conventions

To ensure consistency and predictability:

*   **Directories**: Use `snake_case` (e.g., `project_governance`, `core_services`). For entities that are proper nouns or acronyms, PascalCase or UPPERCASE can be used if it significantly improves readability (e.g., `CORUJA`, `OPENAI_MODELS`). Prefer consistency within a given level or type of directory.
*   **Markdown Files (.md)**: Use `UPPER_SNAKE_CASE.md` or `Title_Case_With_Underscores.md` for significant documents. For less formal or numerous files within a directory, `snake_case.md` is acceptable. (User to confirm final preference).
*   **Python Files (.py)**: Use `snake_case.py` for modules and scripts. Class names within Python files should follow `PascalCase` as per PEP 8.
*   **Other Script Files**: Generally `snake_case.extension` (e.g., `run_analysis.sh`, `config_loader.ps1`).
*   **Configuration Files**: `entity_config.yaml`, `settings.json`, etc.

Clarity and predictability are paramount. Avoid overly long names, but ensure names are descriptive.

## 5. Verification Process

The `cross_reference_verified`, `verification_date`, and `verified_by` fields are intended to support automated and manual checks of link integrity.

*   Scripts (e.g., `scripts/tools/validate_cross_reference.py`) will be developed to parse files, identify `mdc:` links, and verify that the target files exist.
*   Upon successful verification, these fields can be updated by the script or manually.
*   This helps maintain the semantic integrity of the project's Systemic Cartography.

## 6. Tooling Support

To facilitate adherence to these guidelines, the following tools are planned or will be developed under `C:\EGOS\scripts\tools\`:

*   `validate_cross_reference.py`: Validates metadata blocks and `mdc:` links.
*   `generate_metadata_template.py`: Inserts a boilerplate metadata template into new or existing files.
*   `generate_global_index.py`: Creates/updates the `docs/INDEX.md` file.

Further details on these tools will be available in their respective documentation within `docs/06_TOOLS_REFERENCE/`.