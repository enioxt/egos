---
title: code_health_tools_guide
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: code_health_tools_guide
tags: [documentation]
---
---
title: code_health_tools_guide
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
title: code_health_tools_guide
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
title: EGOS Code Health Tools Guide
version: 1.0.0
status: Active
date: 2025-04-25
tags: [code-quality, development, maintenance, koios]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/guides/standards/docstring_standards.md
  - docs/guides/standards/file_size_modularity_standard.md





  - [MQP](../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Standards:
  - [docstring_standards](../guides/standards/docstring_standards.md)
  - [file_size_modularity_standard](../guides/standards/file_size_modularity_standard.md)
---
  - docs/guides/code_health_tools_guide.md

# EGOS Code Health Tools Guide

**Document ID:** KOIOS-GUIDE-002  
**Version:** 1.0  
**Last Updated:** 2025-04-25  
**Status:** ⚡ Active  

## 1. Introduction

This guide provides detailed instructions for using the EGOS code health tools to maintain high code quality across the project. These tools help identify and fix common issues related to syntax, indentation, docstrings, and other code quality concerns.

## 2. Comprehensive Code Health Tool

The `comprehensive_code_health.py` tool is the primary utility for checking and fixing code health issues. It combines multiple specialized checks into a single, unified interface.

### 2.1 Features

- **AST-based syntax checking**: Robust detection of Python syntax errors
- **HTML comment detection**: Identifies invalid HTML-style comments in Python files
- **Unbalanced triple quotes**: Detects and fixes unbalanced triple-quoted strings
- **Indentation checking**: Ensures consistent indentation in Python files
- **Docstring validation**: Verifies docstring presence and formatting

### 2.2 Usage

```bash
# Basic usage - check current directory
python scripts/maintenance/code_health/comprehensive_code_health.py

# Check a specific file or directory
python scripts/maintenance/code_health/comprehensive_code_health.py path/to/check

# Check recursively
python scripts/maintenance/code_health/comprehensive_code_health.py --recursive path/to/check

# Show issues without fixing (dry run)
python scripts/maintenance/code_health/comprehensive_code_health.py --dry-run path/to/check

# Fix issues automatically
python scripts/maintenance/code_health/comprehensive_code_health.py --fix path/to/check

# Generate a JSON report
python scripts/maintenance/code_health/comprehensive_code_health.py --report report.json path/to/check

# Focus on specific issue types
python scripts/maintenance/code_health/comprehensive_code_health.py --html-comments path/to/check
python scripts/maintenance/code_health/comprehensive_code_health.py --triple-quotes path/to/check
```

### 2.3 Common Issues and Fixes

#### HTML-style Comments

**Problem**: HTML-style comments (`<!-- ... -->`) are not valid Python syntax and break AST parsing.

**Detection**:
```python
# This will be detected as an issue
<!-- This is an HTML comment -->
def some_function():
    pass
```

**Fix**: The tool converts HTML comments to Python comments:
```python
# This is an HTML comment
def some_function():
    pass
```

#### Unbalanced Triple Quotes

**Problem**: Unbalanced triple quotes (`"""` or `'''`) break Python's syntax parsing.

**Detection**:
```python
def broken_function():
    """This docstring is not closed properly
    return None
```

**Fix**: The tool either adds closing quotes or converts to comments:
```python
def fixed_function():
    """This docstring is now closed properly"""
    return None
```

## 3. Specialized Tools

While the comprehensive tool is recommended for most use cases, specialized tools are available for specific needs:

### 3.1 Docstring Tools

- `fix_docstring_issues.py`: Focused tool for fixing docstring formatting issues
- `batch_fix_docstrings.py`: Runs docstring fixes across multiple directories

### 3.2 Indentation Checker

- `check_indentation.py`: Specialized tool for identifying indentation inconsistencies

## 4. Integration with Development Workflow

### 4.1 Pre-commit Hooks

The code health tools are integrated with pre-commit hooks to catch issues before they're committed:

```yaml
# In .pre-commit-config.yaml
- id: comprehensive-code-health
  name: Comprehensive Code Health
  description: "Check for syntax, indentation, and docstring issues"
  entry: python scripts/maintenance/code_health/comprehensive_code_health.py
  language: system
  types: [python]
  args: [--dry-run]
  pass_filenames: true
```

### 4.2 VS Code / Windsurf Extensions

The following extensions can help maintain code health in your editor:

| Extension | Purpose | Install Command |
|-----------|---------|----------------|
| Python (Microsoft) | Linting, formatting, IntelliSense | `ext install ms-python.python` |
| Remove Comments | Deletes comment blocks | `ext install rioj7.vscode-remove-comments` |
| DeepSource Autofix™ AI | AI-based code health & auto-fix | `ext install DeepSourceCorp.deepsource-vscode` |
| autoDocstring | Generate and fix docstrings | Search "autoDocstring" in Extensions |

### 4.3 Editor Configuration

Add the following to your `settings.json` to enable lint-on-save:

```json
{
  "editor.formatOnSave": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

## 5. Best Practices

1. **Run checks regularly**: Incorporate code health checks into your development routine
2. **Fix issues promptly**: Address code health issues as soon as they're identified
3. **Use pre-commit hooks**: Let automated tools catch issues before they're committed
4. **Review automated fixes**: Always review changes made by automated tools
5. **Maintain documentation**: Keep docstrings and comments up-to-date

## 6. Troubleshooting

### 6.1 False Positives

If you encounter false positives, consider:

1. Updating the tool with more robust patterns
2. Adding specific exclusions for edge cases
3. Using more specialized tools for specific contexts

### 6.2 Common Errors

| Error | Possible Cause | Solution |
|-------|---------------|----------|
| "Syntax error" | Invalid Python syntax | Fix the syntax error according to the error message |
| "HTML-style comment found" | Using `<!-- ... -->` in Python | Convert to Python comments (`#`) |
| "Unbalanced triple-quoted string" | Missing closing `"""` or `'''` | Add closing quotes or convert to comments |

## 7. Contributing

To improve the code health tools:

1. Submit bug reports with specific examples
2. Propose new patterns for detection
3. Contribute fixes via pull requests
4. Help expand the test suite

---

For questions or feedback about this guide, please contact the KOIOS documentation team.

✧༺❀༻∞ EGOS ∞༺❀༻✧