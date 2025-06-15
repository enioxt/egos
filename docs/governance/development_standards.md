@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_priority_list.md
  - docs/governance/file_lifecycle_management.md
  - docs/guides/development/script_versioning_standards.md
  - docs/project_documentation/guides/standards/docstring_standards.md
  - docs/project_documentation/guides/standards/python_code_standards.md
  - docs/project_documentation/subsystems/KOIOS/KOS_standards.md






  - docs/governance/development_standards.md

# EGOS Development Standards

## Overview

This document outlines the core development standards for the EGOS project. These standards ensure consistency, maintainability, and alignment with EGOS principles across all development activities.

## Core Principles

All development within EGOS should adhere to the following core principles from the Master Quantum Prompt (MQP):

- **Universal Redemption**: Code should be adaptable and redeemable for new purposes
- **Compassionate Temporality**: Development should acknowledge the temporal nature of code
- **Sacred Privacy**: User data and system internals must be properly protected
- **Universal Accessibility**: Systems should be accessible to all users
- **Unconditional Love**: Code should be written with care and consideration for future developers
- **Reciprocal Trust**: Systems should establish and maintain trust with users
- **Integrated Ethics**: Ethical considerations should be built into all development
- **Conscious Modularity**: Systems should be modular and well-structured
- **Systemic Cartography**: Code organization should provide clear navigation
- **Evolutionary Preservation**: Only preserve what continues to serve a purpose

## File Management Golden Rule

**For every file created, we must ensure no duplicate functionality exists, and any incomplete or untested scripts should be deleted if no longer useful.**

This rule enforces several key principles:

1. **Avoid Redundancy**: Before creating a new file, verify that its functionality doesn't already exist elsewhere in the codebase.

2. **Clean as You Go**: Delete temporary, incomplete, or untested files that are no longer needed.

3. **Complete What You Start**: Ensure that new files are properly tested, documented, and integrated before considering them complete.

4. **Maintain Clear Ownership**: Each file should have a clear purpose and ownership within the system architecture.

5. **Document Relationships**: Files should clearly document their relationships with other components through proper cross-references.

Adhering to this rule helps maintain a clean, efficient, and navigable codebase that aligns with the Evolutionary Preservation and Conscious Modularity principles.

## Code Quality Standards

### Python Standards

- Follow PEP 8 guidelines for code formatting
- Use meaningful variable and function names
- Include type hints for all functions and methods
- Write comprehensive docstrings for all modules, classes, and functions
- Keep functions focused on a single responsibility
- Maintain file size below 500 lines where possible
- Use ruff for linting and formatting

### Documentation Standards

- All code must be properly documented with docstrings
- Follow the KOIOS documentation standards
- Include cross-references to related components
- Document technical decisions and their rationale
- Keep documentation up-to-date with code changes

### Testing Standards

- Write unit tests for all new functionality
- Maintain test coverage above 90% for critical components
- Include integration tests for component interactions
- Document test scenarios and edge cases
- Automate testing through CI/CD pipelines

## Version Control Standards

- Follow Conventional Commits specification for commit messages
- Keep commits focused on single concerns
- Include issue/ticket references in commit messages
- Maintain a clean and meaningful commit history
- Use feature branches for all development work

## Security Standards

- Never hardcode secrets; use environment variables or dedicated secrets managers
- Validate all inputs and sanitize all outputs
- Apply the principle of least privilege
- Review dependencies for known vulnerabilities
- Document security considerations for each component

## Cross-Reference Standards

- Ensure all documentation files have appropriate cross-references
- Maintain a minimum of 2 relevant references per documentation file
- Update cross-references when moving or renaming files
- Use the documentation_reference_manager to verify and maintain references
- Run cross-reference verification for all recently modified files

## Related Documents

- [MQP.md](../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](../ROADMAP.md) - Project roadmap and planning
- [File Lifecycle Management](./file_lifecycle_management.md) - Detailed guidelines for file management
- [Cross-Reference Priority List](./cross_reference_priority_list.md) - Files needing cross-reference attention
- [KOIOS Documentation Standards](../project_documentation/subsystems/KOIOS/KOS_standards.md) - Documentation standards
- [Python Code Standards](../project_documentation/guides/standards/python_code_standards.md) - Python coding standards
- [Docstring Standards](../project_documentation/guides/standards/docstring_standards.md) - Documentation string standards
- [Script Versioning Standards](../guides/development/script_versioning_standards.md) - Script versioning guidelines