---
title: EGOS Documentation Structure Standard
version: 1.0.0
status: Active
date_created: 2025-05-18
date_modified: 2025-05-18
authors: [EGOS Team, Cascade AI]
description: "Comprehensive standard defining the organization of all documentation within EGOS, ensuring consistency across subsystems and making the structure easily understandable for both humans and AI assistants."
file_type: standard
scope: project-wide
primary_entity_type: standard
primary_entity_name: Documentation Structure Standard
subsystem: KOIOS
tags: [documentation, structure, organization, standard, koios, egos]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/path/to/file.md
  - docs/governance/relative/path/to/file.md
  - docs/governance/reorganization/DOCS_MIGRATION_PLAN.md
  - docs/reference/documentation_structure.mdc
  - docs/subsystems/KOIOS/KOS_architecture.md
  - docs/subsystems/KOIOS/KOS_roadmap.md
  - docs/subsystems/KOIOS/KOS_standards.md






  - [MQP](../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../../ROADMAP.md) - Main Project roadmap and planning
- Subsystem:
  - [KOS_roadmap](../subsystems/KOIOS/KOS_roadmap.md) - KOIOS Roadmap
  - [KOS_standards](../subsystems/KOIOS/KOS_standards.md) - KOIOS Standards
- Related:
  - [DOCS_MIGRATION_PLAN](../governance/reorganization/DOCS_MIGRATION_PLAN.md) - Documentation Migration Plan
---
  - docs/governance/documentation_structure_standard.md

# EGOS Documentation Structure Standard

**Version:** 1.0.0  
**Status:** Active  
**Last Updated:** 2025-05-18  
**Owner:** KOIOS Subsystem

## Overview

This document defines the standard structure for organizing documentation within the EGOS project. It establishes clear conventions for directory organization, file naming, and cross-referencing to ensure consistency, discoverability, and maintainability of all project documentation.

The EGOS documentation structure follows a hierarchical organization that separates different types of documentation based on their purpose, scope, and audience. This structure is designed to be intuitive for both human developers and AI assistants, making it easier to locate, update, and maintain documentation.

## Core Principles

The EGOS documentation structure is guided by the following core principles:

1. **Clarity and Discoverability**: Documentation should be organized in a way that makes it easy to find relevant information.
2. **Separation of Concerns**: Different types of documentation should be organized into separate directories based on their purpose.
3. **Consistent Naming**: File and directory names should follow consistent conventions to make them predictable and searchable.
4. **Cross-Referencing**: All documentation should be interconnected through cross-references to facilitate navigation.
5. **Hierarchical Organization**: Documentation should be organized in a hierarchical structure that reflects the organization of the project.
6. **Extensibility**: The structure should be flexible enough to accommodate new types of documentation as the project evolves.

## Root Directory Structure

The EGOS documentation is organized under the `docs` directory at the project root. Within this directory, the following structure is established:

```
docs/
├── project_documentation/    # Primary location for all project documentation
├── apps/                    # Documentation for specific applications
├── assets/                  # Shared assets used in documentation (images, diagrams, etc.)
├── diagrams/                # Source files for diagrams
├── logs/                    # Log files and reports
├── resources/               # External resources and references
├── training/                # Training materials and tutorials
└── user_documents/          # End-user documentation
```

## Project Documentation Structure

The `project_documentation` directory contains the core documentation for the EGOS project. It is organized as follows:

```
project_documentation/
├── core/                    # Core project documents (MQP, PHILOSOPHY, STRATEGY)
├── architecture/            # Architecture documentation
├── standards/               # Coding and documentation standards
├── guides/                  # Developer guides and tutorials
├── reference/               # Reference materials
├── governance/              # Project governance documentation
└── subsystems/              # Subsystem-specific documentation
```

### Core Documentation

The `core` directory contains foundational documents that define the project's mission, principles, and high-level strategy:

```
core/
├── MQP.md                   # Master Quantum Prompt
├── PHILOSOPHY.md            # Project philosophy and guiding principles
└── STRATEGY.md              # High-level project strategy
```

### Architecture Documentation

The `architecture` directory contains documents that describe the overall architecture of the EGOS system:

```
architecture/
├── system_architecture.md   # Overall system architecture
├── component_diagrams/      # Component diagrams
├── sequence_diagrams/       # Sequence diagrams
└── data_flow_diagrams/      # Data flow diagrams
```

### Standards Documentation

The `standards` directory contains documents that define coding, documentation, and other standards for the project:

```
standards/
├── coding_standards.md      # Coding standards
├── documentation_standards.md # Documentation standards
├── naming_conventions.md    # Naming conventions
└── file_size_modularity_standard.md # File size and modularity standards
```

### Guides Documentation

The `guides` directory contains developer guides and tutorials:

```
guides/
├── development/            # Development guides
├── deployment/             # Deployment guides
├── testing/                # Testing guides
└── maintenance/            # Maintenance guides
```

### Reference Documentation

The `reference` directory contains reference materials:

```
reference/
├── api/                    # API reference documentation
├── templates/              # Document templates
├── glossary.md             # Project glossary
└── faq.md                  # Frequently asked questions
```

### Governance Documentation

The `governance` directory contains project governance documentation:

```
governance/
├── roadmaps/               # Project roadmaps
├── reports/                # Project reports
├── auditing/               # Audit documentation
├── business/               # Business documentation
└── reorganization/         # Reorganization plans and documentation
```

### Subsystems Documentation

The `subsystems` directory contains documentation specific to each subsystem:

```
subsystems/
├── AETHER/                 # AETHER subsystem documentation
├── ATLAS/                  # ATLAS subsystem documentation
├── KOIOS/                  # KOIOS subsystem documentation
└── ...                     # Other subsystems
```

Each subsystem directory follows a consistent structure:

```
SUBSYSTEM_NAME/
├── SUBSYSTEM_description.md       # Subsystem overview
├── SUBSYSTEM_architecture.md      # Subsystem architecture
├── SUBSYSTEM_api.md               # Subsystem API documentation
├── SUBSYSTEM_data_model.md        # Subsystem data model
├── SUBSYSTEM_deployment_guide.md  # Subsystem deployment guide
├── SUBSYSTEM_contributing_guide.md # Subsystem contributing guide
├── SUBSYSTEM_faq.md               # Subsystem FAQ
├── SUBSYSTEM_roadmap.md           # Subsystem roadmap
└── processes/                     # Subsystem-specific processes
```

## File Naming Conventions

All documentation files should follow these naming conventions:

1. **Markdown Files**: All documentation files should use the `.md` extension.
2. **Subsystem Prefixes**: Files specific to a subsystem should be prefixed with the subsystem abbreviation (e.g., `KOS_` for KOIOS).
3. **Snake Case**: File names should use snake_case (lowercase with underscores).
4. **Descriptive Names**: File names should be descriptive of their content.
5. **No Spaces**: File names should not contain spaces.

Examples:
- `MQP.md` - Master Quantum Prompt
- `KOS_architecture.md` - KOIOS architecture documentation
- `file_size_modularity_standard.md` - File size and modularity standards

## Cross-Referencing

Cross-references between documentation files should use relative paths with markdown link syntax:

```markdown
[Link Text](relative/path/to/file.md)
```

Examples:
- `[MQP](../../core/MQP.md)` - Reference to the Master Quantum Prompt from a subsystem document
- `[KOIOS Architecture](../subsystems/KOIOS/KOS_architecture.md)` - Reference to the KOIOS architecture from a guide

## Frontmatter

All documentation files should include YAML frontmatter at the beginning of the file with the following fields:

```yaml
---
title: Document Title
version: x.y.z
status: [Active, Draft, Deprecated, Archived]
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
authors: [Author1, Author2]
description: "Brief description of the document"
file_type: [documentation, standard, guide, reference, etc.]
scope: [project-wide, subsystem_specific, etc.]
primary_entity_type: [document_type]
primary_entity_name: [document_name]
subsystem: [Subsystem name if applicable]
tags: [tag1, tag2, tag3]
@references:
- Category1:
  - [LinkText](path/to/file.md) - Brief description
- Category2:
  - [LinkText](path/to/file.md) - Brief description
---
```

## Migration Process

When reorganizing documentation or moving files, follow these steps:

1. **Create a Migration Plan**: Document the planned changes in a migration plan.
2. **Analyze Cross-References**: Identify all cross-references that will be affected by the migration.
3. **Create Migration Scripts**: Develop scripts to automate the migration process.
4. **Execute Migration**: Run the migration scripts to move files and update cross-references.
5. **Verify Migration**: Verify that all files have been moved correctly and all cross-references are working.
6. **Clean Up Old Directories**: Remove old directories once migration is complete.

## Implementation and Enforcement

This documentation structure standard is enforced through:

1. **Automated Validation**: Scripts that validate the structure and cross-references of documentation files.
2. **CI/CD Integration**: Integration with the CI/CD pipeline to ensure compliance with the standard.
3. **Documentation Review Process**: A review process that ensures new documentation follows the standard.
4. **Documentation Templates**: Templates for different types of documentation that follow the standard.

## Visualization

A visual representation of the documentation structure is maintained in the `docs/diagrams/documentation_structure.svg` file. This diagram is updated whenever the structure changes.

## References

- [DOCS_MIGRATION_PLAN](../governance/reorganization/DOCS_MIGRATION_PLAN.md) - Documentation Migration Plan
- [KOS_standards](../subsystems/KOIOS/KOS_standards.md) - KOIOS Standards
- [documentation_structure.mdc](../reference/documentation_structure.mdc) - Legacy Documentation Structure Reference

## Changelog

- **1.0.0** (2025-05-18): Initial version of the Documentation Structure Standard.