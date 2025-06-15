@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/core_materials/standards/manual_conversion_documentation_standard.md

# EGOS Manual Conversion Documentation Standard

**Date:** 2025-05-26
**Author:** Cascade (AI Assistant)
**Status:** Active
**MQP Principles:** Systemic Cartography (SC), Evolutionary Preservation (EP)

## 1. Purpose

This document defines the standard for documenting manual file and directory name conversions within the EGOS project, particularly for `snake_case` naming convention compliance. Proper documentation ensures traceability, facilitates cross-reference updates, and provides valuable data for improving automated conversion tools.

## 2. Documentation Format

### 2.1. Conversion Log Entry Format

Each manual conversion must be documented with the following information:

| Field | Description | Example |
|-------|-------------|---------|
| Original Path | Full path to the original file or directory | `C:\EGOS\scripts\subsystems\MASTER` |
| New Path | Full path to the renamed file or directory | `C:\EGOS\scripts\subsystems\master` |
| Date | Date of conversion (YYYY-MM-DD) | `2025-05-26` |
| Status | Status of the conversion (Completed, Skipped, Failed) | `Completed` |
| Pattern Type | Categorization of the naming pattern converted | `UPPERCASE_TO_LOWERCASE` |
| Conversion Rule | Specific rule applied for the conversion | `Convert all uppercase to lowercase` |
| Notes | Any additional relevant information | `Directory contained 5 files that reference this path` |

### 2.2. Pattern Type Categories

The following standardized pattern types must be used:

| Pattern Type | Description | Example Conversion |
|--------------|-------------|-------------------|
| `UPPERCASE_TO_LOWERCASE` | All uppercase letters converted to lowercase | `MASTER` → `master` |
| `CAMELCASE_TO_SNAKE_CASE` | camelCase converted to snake_case | `camelCase` → `camel_case` |
| `PASCALCASE_TO_SNAKE_CASE` | PascalCase converted to snake_case | `PascalCase` → `pascal_case` |
| `KEBABCASE_TO_SNAKE_CASE` | kebab-case converted to snake_case | `kebab-case` → `kebab_case` |
| `SPACE_TO_SNAKE_CASE` | Spaces converted to underscores | `space case` → `space_case` |
| `MIXED_PATTERN` | Multiple patterns in a single name | `MixedPattern-With Space` → `mixed_pattern_with_space` |

### 2.3. Conversion Rule Categories

The following standardized conversion rules must be used:

| Conversion Rule | Description | Example |
|-----------------|-------------|---------|
| `UPPERCASE_TO_LOWERCASE` | Convert all uppercase to lowercase | `MASTER` → `master` |
| `INSERT_UNDERSCORE_BEFORE_CAPITAL` | Insert underscore before capital letters | `camelCase` → `camel_Case` |
| `LOWERCASE_AFTER_UNDERSCORE` | Convert to lowercase after inserting underscores | `camel_Case` → `camel_case` |
| `REPLACE_HYPHEN_WITH_UNDERSCORE` | Replace hyphens with underscores | `kebab-case` → `kebab_case` |
| `REPLACE_SPACE_WITH_UNDERSCORE` | Replace spaces with underscores | `space case` → `space_case` |
| `REMOVE_DUPLICATE_UNDERSCORES` | Remove multiple consecutive underscores | `multiple__underscores` → `multiple_underscores` |
| `TRIM_UNDERSCORES` | Remove leading and trailing underscores | `_trimmed_` → `trimmed` |

## 3. Documentation Location

Manual conversion documentation must be stored in:

1. **Primary Location:** `C:\EGOS\logs\snake_case_conversion\manual_conversion_log.md`
2. **Reference in:** `C:\EGOS\reports\snake_case_conversion_execution_report.md`
3. **Summary in:** `C:\EGOS\WORK_2025-05-26_snake_case_Conversion_Implementation.md`

## 4. Cross-Reference Updates

For each manual conversion, any cross-references to the renamed file or directory must be updated and documented:

1. **Identify affected files** using grep or similar tools
2. **Document updates** in a separate section of the conversion log
3. **Verify functionality** after updates

## 5. Pattern Analysis

After each batch of manual conversions, an analysis must be performed to identify:

1. **Common patterns** that can be automated
2. **Edge cases** that require special handling
3. **Potential improvements** to the conversion script logic

This analysis should be documented in the work log and used to refine the automated conversion tools.

## 6. References

- [MQP.md](C:\EGOS\MQP.md) - Master Quantum Prompt defining EGOS principles
- [snake_case_naming_convention.md](C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md) - Naming convention standard
- [WORK_2025-05-26_snake_case_Conversion_Implementation.md](C:\EGOS\WORK_2025-05-26_snake_case_Conversion_Implementation.md) - Work log