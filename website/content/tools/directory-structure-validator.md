---
title: Directory Structure Validator
description: Validates the EGOS directory structure against the canonical configuration defined in config/directo...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Validation]
tags: [validation, directory, structure, standards, compliance]
toc: true
---

# Directory Structure Validator

**Status**: ACTIVE

**Path**: `scripts/validation/directory_structure_validator.py`

**Category**: Validation

**Maintainer**: EGOS Development Team

## Description

Validates the EGOS directory structure against the canonical configuration defined in config/directory_structure_config.json. Ensures all directories and files follow the standardized structure and naming conventions.

## Examples

### Example 1: Basic validation

```bash
python scripts/validation/directory_structure_validator.py
```

**Output**:

```
Directory structure validation passed!
```

### Example 2: Generate report without fixing issues

```bash
python scripts/validation/directory_structure_validator.py --base-path C:\EGOS
```

**Output**:

```
Directory structure validation complete. Report generated at reports/structure_validation/directory_structure_validation_YYYYMMDD_HHMMSS.md
```

### Example 3: CI mode (exits with non-zero code on critical/error issues)

```bash
python scripts/validation/directory_structure_validator.py --ci
```

**Output**:

```
Directory structure validation failed! Review the report for details on issues that need to be addressed.
```

## Documentation

- **readme**: [scripts/validation/README.md](scripts/validation/README.md)
- **guide**: [docs/guides/directory_structure_validation.md](docs/guides/directory_structure_validation.md)

## Tags

- #validation
- #directory
- #structure
- #standards
- #compliance

