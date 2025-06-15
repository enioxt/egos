---
title: user_guide
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: user_guide
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/guides/user_guide.md

---
title: user_guide
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

---
schema_version: "1.0"
title: "Documentation System User Guide"
id: "DOC-SYS-002"
status: "active"
date_created: "2025-04-30"
date_updated: "2025-04-30"
subsystem: "KOIOS"
author: "EGOS Team"
document_type: "user_guide"
audience: "Developers, Technical Writers"
tags: ["documentation", "system", "user guide", "KOIOS"]
principles: ["Universal Accessibility", "Conscious Modularity"]
related_documents:
  - id: "DOC-SYS-001"
    title: "EGOS Documentation System Overview"
    relationship: "parent"
  - id: "DOC-SYS-003"
    title: "Documentation System Developer Guide"
    relationship: "related"
---

# Documentation System User Guide

This guide provides step-by-step instructions for using the EGOS Documentation System to create, validate, and maintain project documentation.

## Overview

The EGOS Documentation System is designed to make documentation creation and maintenance as straightforward as possible while ensuring consistency and quality. This guide will walk you through the most common tasks and workflows.

## Prerequisites

Before using the documentation system, ensure you have:

- Git installed and configured
- Python 3.9 or higher
- Access to the EGOS repository
- Basic understanding of Markdown

## Getting Started

### Installing Dependencies

```bash
# Clone the repository if you haven't already
git clone https://github.com/your-org/EGOS.git
cd EGOS

# Install required packages
pip install -r requirements.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

## Creating Documentation

### Choosing the Right Template

The system provides several specialized templates for different types of documentation:

1. **Generic Markdown Document** - For general purpose documentation
2. **API Documentation** - For documenting APIs and interfaces
3. **Architecture Documentation** - For system architecture documentation
4. **User Guide** - For end-user documentation
5. **Development Standard** - For development guidelines and standards

### Creating a New Document

To create a new document using a template:

```bash
python scripts/sync_docs.py --create-template <template_name> <output_path>
```

For example, to create a new user guide:

```bash
python scripts/sync_docs.py --create-template user_guide docs/my_feature/user_guide.md
```

### Required Frontmatter Fields

All documents must include these frontmatter fields:

| Field | Description | Example |
|-------|-------------|---------|
| schema_version | Document schema version | "1.0" |
| title | Document title | "Feature X User Guide" |
| id | Unique document ID | "DOC-FEAT-001" |
| status | Document status | "draft", "active", "deprecated" |
| date_created | Creation date | "2025-04-30" |
| date_updated | Last update date | "2025-04-30" |
| subsystem | Related subsystem | "KOIOS" |
| author | Document author | "EGOS Team" |
| document_type | Type of document | "user_guide", "api_documentation", etc. |

## Validating Documentation

### Local Validation

To validate your document before committing:

```bash
# Validate a specific document
python scripts/sync_docs.py --check --files docs/my_feature/document.md

# Validate all documentation
python scripts/sync_docs.py --check
```

### Fixing Common Issues

The system can automatically fix common formatting issues:

```bash
python scripts/fix_documentation_linting.py --specific-file docs/my_feature/document.md
```

## Working with Document Relationships

### Adding Related Documents

To create relationships between documents, add them to the frontmatter:

```yaml
related_documents:
  - id: "DOC-FEAT-002"
    title: "Feature X API Documentation"
    relationship: "related"
```

Relationship types include:
- `parent` - Parent document
- `child` - Child document
- `related` - Related document
- `references` - Document referenced by this document
- `implements` - Document implementing concepts from this document

### Visualizing Relationships

To visualize document relationships:

```bash
python scripts/metrics/documentation_metrics.py --network docs/network_visualization.html
```

## Migrating Legacy Documentation

To migrate existing documentation to the current format:

```bash
# Analyze a single document
python scripts/migrate_legacy_docs.py --files docs/legacy_document.md

# Migrate with auto-fix
python scripts/migrate_legacy_docs.py --files docs/legacy_document.md --force
```

## Documentation Quality Metrics

### Generating Quality Reports

```bash
# Generate documentation quality metrics
python scripts/test_legacy_docs.py --dir docs --output reports/quality_report.md
```

### Interpreting Quality Scores

The quality score is calculated based on:
- Presence of required metadata
- Proper document structure
- Compliance with linting rules
- Cross-references and relationships

Scores are categorized as:
- **High Compliance (90-100%)**: Follows all major standards
- **Medium Compliance (70-89%)**: Minor issues present
- **Low Compliance (<70%)**: Requires significant improvements

## Best Practices

### Document Structure

1. **Start with a clear introduction** - Explain the purpose of the document
2. **Use appropriate heading hierarchy** - Don't skip levels (e.g., h1 → h3)
3. **Include relevant code examples** - With proper syntax highlighting
4. **Add diagrams for complex concepts** - Using Mermaid syntax for diagrams
5. **Link to related documents** - Create a well-connected documentation network

### Frontmatter Management

1. **Keep the ID unique** - Follow the pattern `DOC-<SUBSYSTEM/AREA>-<NUMBER>`
2. **Update date_updated when changing content** - Maintains accurate timeline
3. **Use meaningful tags** - To improve searchability
4. **Link related documents** - To create a cohesive documentation network

### Common Pitfalls

- **Missing required fields** - Ensure all required frontmatter fields are present
- **Outdated relationships** - Ensure related document references are current
- **Inconsistent formatting** - Use the built-in linting tools
- **Duplicate content** - Reference existing documentation instead of duplicating

## Troubleshooting

### Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required field" | Frontmatter missing mandatory field | Add the required field to frontmatter |
| "Invalid schema version" | Incorrect schema_version value | Change to current version (1.0) |
| "Invalid related document" | Referenced document doesn't exist | Update reference or create the document |
| "Linting errors" | Markdown formatting issues | Run fix_documentation_linting.py |

### Common Tool Issues

**Error**: `ModuleNotFoundError`
**Solution**: Ensure all dependencies are installed (`pip install -r requirements.txt`)

**Error**: `FileNotFoundError`
**Solution**: Check file paths and ensure directories exist

**Error**: `ValidationError`
**Solution**: Check the error message for details on which validation rule failed

## Getting Help

For additional assistance:
- Check the Developer Guide for more technical details
- Consult the Troubleshooting Guide for common issues
- Submit issues through the project tracking system

## Conclusion

Following this guide will help you create and maintain high-quality documentation that adheres to the EGOS project standards. Consistent, well-structured documentation enhances project understanding, facilitates collaboration, and improves maintainability.