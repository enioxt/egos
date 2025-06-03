# EGOS Repository Organization Guide

## Repository Structure

This repository follows a consistent organization structure to maintain the EGOS project effectively.

### Key Directories

- **/.windsurf/**: Windsurf workflows and configuration
- **/ATRIAN/**: The ATRiAN module - Ethics as a Service
- **/EGOS_Framework/**: Core EGOS framework and MCP files
- **/apps/**: EGOS applications and services
- **/config/**: Configuration files (excluding secrets)
- **/docs/**: Documentation organized by topic
  - **/core/**: Core concepts and architecture
  - **/systems/**: All subsystems documentation
  - **/guides/**: Usage and development guides
  - **/processes/**: Process documentation
  - **/standards/**: Project standards
  - **/research/**: Research materials
- **/scripts/**: Utility scripts and tools
- **/website/**: EGOS website source code

### File Types and Locations

- **Markdown Documentation**: Use .md files for all documentation
- **Python Code**: Follow PEP 8 style guidelines
- **Configuration**: Use YAML for configuration files when possible
- **Scripts**: Include usage comments at the top of each script

### Excluded Items

The following should never be committed to the repository:

- Secrets, API keys, or credentials
- Node modules and other large dependency directories
- Temporary or backup files
- Large binary assets (use external storage instead)

## Organization Guidelines

1. **Keep Related Items Together**: Group related files in the same directory
2. **Use Clear Naming**: File names should indicate content and purpose
3. **Minimize Duplication**: Avoid duplicating content across multiple locations
4. **Reference Don't Copy**: Link to existing content rather than duplicating it
5. **Document Structure**: Keep documentation structure parallel to code structure

Last updated: 2025-06-03
