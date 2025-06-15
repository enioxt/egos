---
title: case_sensitivity_standards
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: case_sensitivity_standards
tags: [documentation]
---
---
title: case_sensitivity_standards
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
title: case_sensitivity_standards
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

# EGOS Case Sensitivity Standards

## Overview

This document defines the EGOS system-wide standards for handling case sensitivity to ensure cross-platform compatibility, particularly between Windows (case-insensitive filesystem) and Unix-based systems (case-sensitive filesystem).

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - governance/dynamic_import_resilience.md





  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Related Documentation:
  - [cross_platform_compatibility.md](../../../..\..\subsystems\HARMONY\docs\cross_platform_compatibility.md) - HARMONY implementation
  - [case_sensitivity_rule.md](../../../..\..\subsystems\TRUST_WEAVER\docs\rules\case_sensitivity_rule.md) - TRUST_WEAVER rule
  - [dynamic_import_resilience](../../governance/dynamic_import_resilience.md) - Import resilience pattern
  - docs/standards/case_sensitivity_standards.md

## Core Principles

1. **Universal Accessibility**: Code must work consistently across all platforms
2. **Conscious Modularity**: Cross-platform concerns should be centralized in HARMONY
3. **Systemic Cartography**: Clear documentation of cross-platform patterns

## Naming Standards

### Filesystem & Module Names

1. **Use snake_case for all Python module names**:
   - Correct: `user_authentication.py`, `data_processor.py`
   - Incorrect: `UserAuthentication.py`, `dataProcessor.py`

2. **Use consistent casing for directory names**:
   - Preferred: `subsystems/harmony/src` (all lowercase)
   - Alternative: `subsystems/HARMONY/src` (consistent uppercase for subsystem names)
   - Incorrect: `subsystems/Harmony/src` (mixed case)

3. **Respect platform-specific filenames**:
   - Always maintain the exact case when referencing existing files
   - Do not rely on case-insensitive behavior, even on Windows

## Import Patterns

### EGOS Import Resilience Pattern

All Python modules should use the EGOS Import Resilience pattern to ensure cross-platform compatibility:

```python
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])  # Adjust the number based on file location
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

### Absolute vs. Relative Imports

1. **Prefer absolute imports** for cross-platform compatibility:
   ```python
   # Instead of this (can be problematic)
   from ..module import Symbol
   
   # Use this
   from subsystems.my_subsystem.module import Symbol
   ```

2. **When using relative imports**, ensure they work when the module is run directly:
   ```python
   # Add this if the module might be run directly
   if __name__ == "__main__":
       import sys
       from pathlib import Path
       sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
   ```

### Import Guarding

Use import guarding to handle potential import issues gracefully:

```python
try:
    from subsystems.harmony.module import Symbol
except ImportError:
    # Fallback or graceful degradation
    Symbol = None  # Or a mock implementation
```

## Path Handling

1. **Use pathlib.Path for all filesystem operations**:
   ```python
   # Instead of this
   import os
   path = os.path.join('dir', 'file.txt')
   
   # Use this
   from pathlib import Path
   path = Path('dir') / 'file.txt'
   ```

2. **Normalize case for path comparisons**:
   ```python
   # For case-insensitive comparisons (needed for cross-platform)
   if path1.name.lower() == path2.name.lower():
       # ...
   ```

3. **Use exists() checks before accessing paths**:
   ```python
   path = Path('some/path')
   if path.exists():
       # Safe to use
   ```

## Circular Import Resolution

1. **Extract shared types to dedicated modules**:
   ```python
   # In base_types.py
   class BaseClass:
       # Common functionality
       
   # In module_a.py and module_b.py
   from base_types import BaseClass
   ```

2. **Use local imports** for circular dependencies that can't be avoided:
   ```python
   def function():
       # Import inside function to avoid circular import
       from . import other_module
       other_module.something()
   ```

## Testing Standards

1. **Test on multiple platforms** whenever possible
2. **Use automated CI tests** on both Windows and Unix-based systems
3. **Include explicit case sensitivity tests** in cross-platform code

## Enforcement

These standards are enforced through:

1. **HARMONY Case Sensitivity Framework**: System-wide detection and resolution
2. **TRUST_WEAVER Rule TW-PLAT-001**: IDE integration and linting
3. **Pre-commit hooks**: Prevent introduction of case sensitivity issues
4. **Code review guidelines**: Manual review for standards compliance

## Common Issues and Solutions

### Mixed Import Styles

**Problem**:
```python
# Inconsistent import styles in the same module
from .module_a import SymbolA
from subsystems.my_subsystem.module_b import SymbolB
```

**Solution**:
```python
# Choose one style and be consistent
from subsystems.my_subsystem.module_a import SymbolA
from subsystems.my_subsystem.module_b import SymbolB
```

### Case Conflicts

**Problem**:
```
my_module.py
MyModule.py  # Same name, different case - works on Windows, breaks on Unix
```

**Solution**:
Choose a single, consistent naming convention and rename conflicting files.

### Cross-Platform Testing

**Problem**: Code works on development machine but fails on other platforms.

**Solution**: Set up GitHub Actions or other CI tools to test on multiple platforms:
```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
```

## Transition Plan

For existing code that doesn't meet these standards:

1. **Identify**: Use the HARMONY scanner to find issues
2. **Prioritize**: Focus on modules with cross-platform usage first
3. **Refactor**: Apply the patterns described in this document
4. **Verify**: Test on multiple platforms after refactoring