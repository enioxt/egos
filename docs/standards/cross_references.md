---
title: EGOS Cross-Reference Standards
description: Canonical standards for cross-references across the EGOS ecosystem
created: 2025-05-21
updated: 2025-05-21
author: EGOS Team
version: 1.0.0
status: Active
tags: [standards, cross-reference, documentation, KOIOS]
references: [<!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/cross_references.md

# EGOS Cross-Reference Standards

**@references: <!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->**

## Overview

This document defines the canonical standards for cross-references across the EGOS ecosystem. These standards ensure that all references are consistent, machine-readable, and optimized for automated integration and maintenance. Following these standards is critical for system integrity, documentation quality, and effective cross-subsystem integration.

## Principles

The EGOS cross-reference standards adhere to the following principles:

1. **Consistency**: All references follow the same format throughout the codebase
2. **Machine-Readability**: References can be automatically parsed and validated
3. **Human-Readability**: References remain clear and understandable to humans
4. **Traceability**: References can be traced back to their source
5. **Maintainability**: References can be easily updated and maintained
6. **Integration**: References support cross-subsystem integration

## Canonical Reference Formats

### 1. Inline References

For all inline references in code, markdown, and docstrings:

```
@references: [REFERENCE-ID-1], [REFERENCE-ID-2], [DESCRIPTION]
```

Where:
- `REFERENCE-ID` follows the pattern `EGOS-[TYPE]-[SUBSYSTEM]-[NUMBER]` (e.g., `<!-- TO_BE_REPLACED -->`)
- `DESCRIPTION` is a brief, human-readable description of the reference (optional)

Examples:
```markdown
**@references: <!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->**
```

```python
"""
Module description

@references: <!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->, Dependency mapping implementation
"""
```

### 2. Document Metadata Format

For document frontmatter in markdown files:

```yaml
---
title: [Document Title]
description: [Brief Description]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
author: [Author Name/Team]
version: [X.Y.Z]
status: [Active|Draft|Deprecated|Archived]
tags: [tag1, tag2, ...]
references: [REFERENCE-ID-1, REFERENCE-ID-2, ...]
---
```

Example:
```yaml
---
title: EGOS Cross-Reference Standards
description: Canonical standards for cross-references across the EGOS ecosystem
created: 2025-05-21
updated: 2025-05-21
author: EGOS Team
version: 1.0.0
status: Active
tags: [standards, cross-reference, documentation, KOIOS]
references: [<!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->]
---
```

### 3. Reference ID Format

All reference IDs follow this pattern:

```
EGOS-[TYPE]-[SUBSYSTEM]-[NUMBER]
```

Where:
- `EGOS` is the project prefix
- `TYPE` is the reference type (see below)
- `SUBSYSTEM` is the subsystem name (e.g., ETHIK, KOIOS, NEXUS)
- `NUMBER` is a sequential number (starting from 01)

#### Reference Types

| Type | Description | Example |
|------|-------------|---------|
| `EPIC` | High-level feature or initiative | `<!-- TO_BE_REPLACED -->` |
| `FEAT` | Specific feature | `<!-- TO_BE_REPLACED -->` |
| `TASK` | Individual task | `<!-- TO_BE_REPLACED -->` |
| `DOC` | Documentation | `<!-- TO_BE_REPLACED -->` |
| `STD` | Standard | `<!-- TO_BE_REPLACED -->` |
| `MOD` | Module | `<!-- TO_BE_REPLACED -->` |
| `BUG` | Bug fix | `<!-- TO_BE_REPLACED -->` |
| `TEST` | Test | `<!-- TO_BE_REPLACED -->` |

## File-Specific Standards

### Python Files

References should be placed in the module docstring:

```python
"""
Module name and description

@references: EGOS-MOD-SUBSYSTEM-XX, EGOS-FEAT-SUBSYSTEM-YY, Brief description
"""
```

### Markdown Files

References should be placed in both the frontmatter and as an inline reference after the title:

```markdown
---
title: Document Title
description: Document description
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: Author Name
version: X.Y.Z
status: Active
tags: [tag1, tag2]
references: [EGOS-DOC-SUBSYSTEM-XX, EGOS-FEAT-SUBSYSTEM-YY]
---

# Document Title

**@references: EGOS-DOC-SUBSYSTEM-XX, EGOS-FEAT-SUBSYSTEM-YY**

Document content...
```

### YAML Configuration Files

References should be placed in a comment at the top of the file:

```yaml
# EGOS Configuration File
# @references: EGOS-CONFIG-SUBSYSTEM-XX, EGOS-FEAT-SUBSYSTEM-YY

config:
  key: value
```

## Validation Rules

1. All references must follow the canonical format
2. Reference IDs must exist in the reference registry
3. References must be placed in the correct location for each file type
4. References must be machine-readable and parsable
5. References must be human-readable and understandable

## Migration Guidelines

When migrating existing references to the new standard:

1. Preserve the original reference content when possible
2. Map existing references to the new format
3. Update all references in a single batch to maintain consistency
4. Validate all references after migration
5. Document any exceptions or special cases

## Implementation Tools

The following tools are available for working with cross-references:

1. **File Reference Checker Ultra**: Validates references against the standard
2. **Reference Migration Script**: Migrates existing references to the new standard
3. **Reference Registry**: Central registry of all reference IDs
4. **Reference Validator**: Validates references against the registry

## Conclusion

Following these cross-reference standards ensures consistency, traceability, and maintainability across the EGOS ecosystem. All contributors should adhere to these standards when creating or updating references.

For questions or suggestions regarding these standards, please contact the KOIOS team.

✧༺❀༻∞ EGOS ∞༺❀༻✧