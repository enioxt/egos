---
# AutoCrossRef ‑ Cross-Reference Standard (Single Source of Truth)
# This YAML header is parsed by tooling.  Edit with care.
core_references:
  - README.md
  - ROADMAP.md
  - MQP.md
  - CODE_OF_CONDUCT.md
  - .windsurfrules
hierarchy:
  level0: core_references  # Top-priority references present in nearly every file.
---

# AutoCrossRef – Cross-Reference Standard

This document defines the canonical rules the **AutoCrossRef** subsystem uses when
injecting or validating `@references:` blocks.
It is the single source of truth consulted by both human contributors and
LLM-powered tooling.

## 1. Core (Level-0) References
The list under `core_refs` in the YAML header **must appear** in every important
project file unless explicitly excluded by future rules.

## 2. Hierarchical Levels
We anticipate future layers:
* **Level 0** – global project essentials (this file).
* **Level 1** – subsystem-wide key files (e.g. each subsystem’s own README).
* **Level 2** – package- or feature-specific documents.

Tooling should process levels in order, ensuring lower levels never override the
presence of higher-level refs.

## 3. Formatting Rules
* Header line exactly `@references:` (or comment-prefixed variant).
* Each reference as Markdown list item, either plain path or `[Title](path)`.
* No duplicate lines.
* Self-reference is **not** allowed.

## 4. Workflow
1. Remove self-references and unknown legacy refs.
2. Inject any missing Level-0 refs.
3. Perform strict validation when run in CI (`--mode full`).

Keep this file concise—tooling parses only the YAML header. Additional guidance
below is for humans and may be extended freely.

@references(level=1):
  - subsystems/AutoCrossRef/path