---
title: docstring_standards
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: docstring_standards
tags: [documentation]
---
---
title: docstring_standards
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
title: docstring_standards
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
title: EGOS Docstring Standards
version: 1.0.0
status: Active
date: 2025-04-25
tags: [documentation, code-quality, standards, koios]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Standards:
  - [KOIOS Documentation Standards](../../../..\..\docs\standards\documentation_standards.md)
---
  - docs/standards/docstring_standards.md

# EGOS Docstring Standards

**Document ID:** KOIOS-STD-003  
**Version:** 1.0  
**Last Updated:** 2025-04-25  
**Status:** ⚡ Active  

## 1. Introduction

This document defines the standards for Python docstrings within the EGOS project. Proper docstring formatting is essential for code clarity, maintainability, and automated documentation generation. These standards align with Python's PEP 257 while incorporating EGOS-specific requirements.

## 2. General Principles

### 2.1 Purpose of Docstrings

Docstrings serve multiple critical functions:
- Document the purpose and behavior of code elements
- Enable automated documentation generation
- Provide context for developers
- Support IDE tooltips and code navigation
- Facilitate code maintenance and knowledge transfer

### 2.2 Core Requirements

All docstrings in EGOS must:
- Be enclosed in triple quotes (`"""` or `'''`)
- Be properly indented according to their context
- Be descriptive and concise
- Follow consistent formatting within their type
- Include all required sections for their context

## 3. Docstring Types and Formats

### 3.1 Module Docstrings

Module docstrings appear at the top of a file, before any imports or code.

```python
"""
Module name or short description.

Detailed description of the module's purpose and functionality.

@references:
- Core References:
  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Subsystems:
  - [README](../../governance/business/github_updates/README.md)
"""

# Imports and code follow...
```

### 3.2 Class Docstrings

Class docstrings appear immediately after the class declaration.

```python
class ExampleClass:
    """
    Brief description of the class.

    Detailed description of the class's purpose, behavior, and usage.
    Include any important notes about implementation details.

    Attributes:
        attribute_name: Description of the attribute.
        another_attribute: Description of another attribute.
    """
```

### 3.3 Method and Function Docstrings

Method and function docstrings appear immediately after the function declaration.

```python
def example_function(param1, param2, optional_param=None):
    """
    Brief description of the function.

    Detailed description of what the function does, any algorithms used,
    side effects, etc.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.
        optional_param: Description of the optional parameter.

    Returns:
        Description of the return value.

    Raises:
        ExceptionType: When and why this exception might be raised.
    """
```

### 3.4 Property Docstrings

Property docstrings should describe what the property represents.

```python
@property
def example_property(self):
    """Brief description of what this property represents."""
    return self._example
```

## 4. Indentation Rules

Proper indentation is critical for docstrings to be correctly interpreted by Python and documentation tools:

### 4.1 Module Docstrings
- Start at column 0 (no indentation)
- Must appear before any imports or code

### 4.2 Class Docstrings
- Indented at the same level as the class body
- Typically 4 spaces

### 4.3 Method and Function Docstrings
- Indented at the same level as the function body
- Typically 4 or 8 spaces (depending on nesting)

### 4.4 Common Errors to Avoid
- ❌ Docstrings with inconsistent indentation
- ❌ Docstrings after code has already appeared in the scope
- ❌ Docstrings with mixed tab and space indentation

## 5. Content Guidelines

### 5.1 Required Content

#### For Modules:
- Brief description
- Detailed explanation of purpose
- Cross-references to related documents (using EGOS MDC format)

#### For Classes:
- Brief description
- Explanation of the class's role
- Attributes (if applicable)
- Usage examples (for complex classes)

#### For Methods and Functions:
- Brief description
- Detailed explanation (for complex functions)
- Parameters (Args)
- Return values
- Exceptions raised

### 5.2 Cross-References

EGOS uses a specific format for cross-references in docstrings:

```python
"""
Example docstring with cross-references.

@references:
- Core References:
  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
- Related Components:
  - [related_module.py](code:../path/to/related_module.py)
"""
```

## 6. Automated Validation and Correction

EGOS provides tools to validate and correct docstring formatting:

### 6.1 Validation Tools
- `scripts/maintenance/code_health/comprehensive_code_health.py --dry-run`: Checks for docstring issues, indentation problems, and other syntax errors without modifying files
- `scripts/maintenance/code_health/fix_docstring_issues.py --dry-run`: Focused tool for checking docstring issues only
- Pre-commit hooks for docstring validation

### 6.2 Correction Tools
- `scripts/maintenance/code_health/comprehensive_code_health.py --fix`: Fixes common code health issues including docstrings, indentation, and syntax
- `scripts/maintenance/code_health/fix_docstring_issues.py`: Focused tool for fixing docstring issues only
- `scripts/maintenance/code_health/batch_fix_docstrings.py`: Runs docstring fixes across multiple directories

## 7. Common Issues and Solutions

### 7.1 Missing Triple Quotes
- **Issue**: Docstrings without triple quotes are interpreted as code
- **Solution**: Always enclose docstrings in triple quotes (`"""` or `'''`)

### 7.2 Incorrect Indentation
- **Issue**: Improper indentation causes syntax errors
- **Solution**: Ensure docstrings are indented at the same level as the code block they document

### 7.3 F-strings in Docstrings
- **Issue**: F-strings in docstrings cause syntax errors
- **Solution**: Use regular string formatting in docstrings, not f-strings

### 7.4 Docstring Placement
- **Issue**: Module docstrings after imports
- **Solution**: Always place module docstrings before any imports or code

## 8. Integration with Development Workflow

### 8.1 Pre-commit Hooks
Configure pre-commit hooks to validate docstrings before commits:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: docstring-check
      name: Check docstring formatting
      entry: python scripts/maintenance/code_health/fix_docstring_issues.py --dry-run
      language: system
      types: [python]
```

### 8.2 CI/CD Integration
Add docstring validation to CI/CD pipelines:

```yaml
# Example GitHub Actions workflow step
- name: Check docstring formatting
  run: python scripts/maintenance/code_health/fix_docstring_issues.py --dry-run
```

## 9. References

- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [KOIOS Documentation Standards](../../../..\..\docs\standards\documentation_standards.md)
- [EGOS Master Quantum Prompt](../../../..\..\MQP.md)