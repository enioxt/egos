@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_priority_list.md
  - docs/governance/development_standards.md
  - docs/project_documentation/subsystems/KOIOS/KOS_roadmap.md
  - docs/project_documentation/subsystems/KOIOS/KOS_standards.md
  - docs/templates/file_creation_checklist.md






  - docs/governance/file_lifecycle_management.md

# File Lifecycle Management

## Overview

This document provides comprehensive guidelines for managing the lifecycle of files within the EGOS ecosystem, from creation to maintenance to retirement. It implements the File Management Golden Rule established in the [Development Standards](./development_standards.md).

## File Lifecycle Stages

### 1. Planning

Before creating a new file, consider:

- **Purpose**: What specific need will this file address?
- **Existing Solutions**: Has this functionality already been implemented elsewhere?
- **Location**: Where should the file be placed for optimal discoverability?
- **Dependencies**: What other components will this file interact with?
- **Naming**: What naming convention will make this file easily discoverable?

### 2. Creation

When creating a new file:

- **Use Templates**: Utilize appropriate templates from `docs/templates/` when available
- **Include Headers**: All files should begin with appropriate headers and metadata
- **Document Purpose**: Clearly state the file's purpose and functionality
- **Add Cross-References**: Include references to related files and components
- **Set Standards**: Establish quality standards specific to the file's purpose

### 3. Development

During active development:

- **Commit Incrementally**: Make regular, focused commits with clear messages
- **Document as You Go**: Update documentation alongside code changes
- **Test Thoroughly**: Implement tests for all functionality
- **Maintain Cross-References**: Update references as relationships evolve
- **Seek Review**: Obtain feedback from other developers when appropriate

### 4. Maintenance

For ongoing maintenance:

- **Regular Review**: Periodically review files for relevance and quality
- **Update References**: Ensure cross-references remain accurate and current
- **Refactor When Needed**: Improve structure and organization as the system evolves
- **Address Technical Debt**: Regularly clean up and improve existing code
- **Document Changes**: Maintain a clear history of significant changes

### 5. Retirement

When a file is no longer needed:

- **Document Decision**: Record the rationale for retirement
- **Update References**: Remove or update references from other files
- **Archive if Valuable**: Consider archiving historically significant files
- **Clean Dependencies**: Remove dependencies and update affected components
- **Complete Removal**: Ensure all traces are removed from the active codebase

## Implementing the Golden Rule

### Avoiding Duplicate Functionality

Before creating a new file:

1. **Search the Codebase**: Use tools like `grep_search` or `codebase_search` to find similar functionality
2. **Review Documentation**: Check existing documentation for related components
3. **Consult Team Members**: Ask colleagues about existing solutions
4. **Consider Extending**: Determine if extending an existing file is better than creating a new one

### Cleaning Up Incomplete Work

For incomplete or untested files:

1. **Regular Audits**: Periodically review work-in-progress files
2. **Decision Points**: Establish clear criteria for continuing development or removing the file
3. **Documentation**: If removing, document the reason and any lessons learned
4. **Knowledge Preservation**: Extract and preserve valuable insights before deletion
5. **Clean References**: Remove any references to the deleted file

### Ensuring File Completeness

A file is considered complete when it has:

1. **Comprehensive Documentation**: Clear purpose, usage instructions, and API documentation
2. **Sufficient Test Coverage**: Tests for all critical functionality
3. **Proper Cross-References**: Links to related files and components
4. **Quality Assurance**: Passes all linting and quality checks
5. **Peer Review**: Has been reviewed by at least one other developer

## File Management Tools

EGOS provides several tools to assist with file lifecycle management:

- **Cross-Reference Manager**: Maintains and verifies documentation references
- **Recent Files Verifier**: Checks recently modified files for proper references
- **Code Quality Tools**: Enforces coding standards and best practices
- **Documentation Generators**: Creates standardized documentation from code

## Checklist for New Files

Before considering a new file complete, ensure:

- [ ] File follows naming conventions and is in the appropriate location
- [ ] Purpose and functionality are clearly documented
- [ ] All functions and classes have proper docstrings
- [ ] Cross-references to related files are included
- [ ] Tests are implemented with adequate coverage
- [ ] Code passes all linting and quality checks
- [ ] No duplicate functionality exists elsewhere in the codebase
- [ ] File has been reviewed by at least one other developer

## Related Documents

- [MQP.md](../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](../ROADMAP.md) - Project roadmap and planning
- [Development Standards](./development_standards.md) - Core development standards including Golden Rule
- [Cross-Reference Priority List](./cross_reference_priority_list.md) - Files needing cross-reference attention
- [File Creation Checklist](../templates/file_creation_checklist.md) - Template for new file creation
- [KOIOS Documentation Standards](../project_documentation/subsystems/KOIOS/KOS_standards.md) - Documentation standards
- [Cross-Reference Enhancement Plan](../project_documentation/subsystems/KOIOS/KOS_roadmap.md) - Roadmap for cross-reference improvements