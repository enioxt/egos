---
title: KOIOS Interaction Standards
version: 1.0.1
status: Active
date_created: 2025-05-10
date_modified: 2025-05-17
authors: [EGOS Team, Cascade AI]
description: "Defines the standards and protocols for interactions with and within the KOIOS subsystem, including data exchange formats, API usage guidelines, and communication patterns. It covers the Smart Tips Protocol and Git Workflow Standards."
file_type: standard
scope: subsystem-specific:KOIOS
primary_entity_type: interaction_standard
primary_entity_name: KOIOS System Interaction Standards
tags: [koios, interaction, standard, api_guidelines, data_exchange, subsystem_KOIOS, protocols, smart_tips, git_workflow]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/KOIOS_Interaction_Standards.md

# KOIOS Interaction Standards

**Version:** 1.0
**Last Updated:** April 7, 2025
**Status:** Active

## Overview

This document outlines key interaction standards implemented in the EGOS system, focusing on:

1. **Smart Tips Protocol:** Guidelines for contextual, helpful suggestions during user interactions
2. **Git Workflow Standards:** Structured procedures for version control operations, especially in challenging scenarios

These standards have been implemented as rules in the `.cursor/rules/` directory and are integrated into the EGOS AI assistant's behavior.

## Smart Tips Protocol

### Purpose

The Smart Tips protocol enriches user experience by providing optional, contextual suggestions that foster continuous learning and system improvement. Tips are offered after task completion to suggest potential improvements or alternatives.

### Key Principles

- **Contextual Relevance:** Tips are related to current tasks or workflows
- **Optional Nature:** Tips are suggestions, not requirements
- **Progressive Learning:** Focus on immediate next-level knowledge
- **Categorization:** Tips are classified by type (Development, Documentation, Security, etc.)
- **Subsystem Specificity:** Tips are tailored to relevant subsystems
- **Ethical Context Awareness**: Tips should, where appropriate, highlight or reinforce ETHIK principles and EGOS ethical guidelines relevant to the suggested action or artifact.

### Tip Categories

The protocol defines several categories of tips:

1. **Development Tips:** Code improvements, testing approaches, design patterns
2. **Documentation Tips:** Docstring improvements, README updates, cross-referencing
3. **KOIOS Standards Tips:** Naming conventions, directory structure, logging practices
4. **Security Tips:** Data validation, PII handling, input sanitization
5. **Performance Tips:** Optimizations, memory management, caching
6. **User Experience Tips:** Error messaging, interface enhancements, help text

### Subsystem-Specific Tips

The protocol includes common tips specifically tailored for each EGOS subsystem:

- **CRONOS:** State capture, backup verification, path formatting, data retention
- **ETHIK:** PII detection, content filtering, moderation balance, decision explanations
- **KOIOS:** Documentation synchronization, error codes, search capabilities, formatting
- **CORUJA:** AI interaction logging, temperature controls, prompt templates, output parsing
- **NEXUS:** Module relationships, interface patterns, lazy loading, boundary documentation
- **ATLAS:** Visualization conventions, drill-down capabilities, timeline views, color coding
- **MYCELIUM:** Message serialization, delivery mechanisms, topic naming, monitoring

### Implementation

This protocol is implemented in the `.cursor/rules/smart-tips.mdc` file and integrated into the EGOS AI assistant's behavior. The assistant automatically identifies opportunities to provide tips based on user interactions and task completions.

## Git Workflow Standards

### Purpose

The Git Workflow Standards provide structured procedures for version control operations, focusing on challenging scenarios such as merge conflicts, pre-commit hook failures, and repository transitions.

### Core Principles

- **Targeted Fixing:** Address specific issues directly
- **Progressive Resolution:** Solve problems incrementally
- **Prioritization:** Focus on critical files first
- **Separation of Concerns:** Divide large merges into smaller commits
- **Documentation:** Use meaningful commit messages

### Standard Procedures

The standards define three key procedures documented in `git_workflow_standards.mdc`:

1. **Standard Local Commit (EGOS-GIT-COMMIT-01):**
   - Selective staging of completed files
   - Local commit with conventional message
   - Push to remote repository

2. **Merge Conflict Resolution (EGOS-GIT-MERGE-01):**
   - Identify conflicting files
   - Examine each conflict
   - Resolve strategically based on context
   - Mark files as resolved
   - Complete the merge (potentially using `--no-verify` if hooks conflict)

3. **Pre-commit Hook Failure Handling (EGOS-GIT-PRECOMMIT-01):**
   - Analyze hook failures
   - Address common failures (formatting, large files, imports)
   - Use strategic bypassing when appropriate
   - Implement post-bypass cleanup

4. **Repository Management (EGOS-GIT-REPO-01):**
   - Configure credentials
   - Manage repository migrations
   - Push to new repositories
   - Validate migrations

### EGOS-Specific Considerations

The standards include several considerations specific to EGOS:

- **Local-First Development:** Always create and modify files locally first, then push to GitHub
- **Windows Path Handling:** Use Windows-compatible formats with proper quoting
- **KOIOS Compliance:** Follow commit message standards and project structure
- **ETHIK Considerations:** Never commit sensitive data or PII

### Implementation

These standards are implemented in the `.cursor/rules/git_workflow_standards.mdc` file. They provide explicit guidance for common Git operations and challenging scenarios, with concrete examples and code snippets.

## 4. Documentation and Versioning of KOIOS-Interfaced Artifacts

While this document focuses on specific KOIOS interaction protocols, it's crucial that any EGOS modules, services, or artifacts that KOIOS indexes, interacts with, or provides context for, adhere to broader EGOS documentation and versioning standards. This includes:

*   **Comprehensive Module Documentation:** Following the pattern of detailed `README.md` files (see `ATRiAN/README.md` for an example) that cover purpose, architecture, APIs, setup, and usage.
*   **Detailed Planning Documents:** For significant features or integrations, detailed planning documents should be created (e.g., `ATRiAN/EaaS_Integration_Plan.md`).
*   **Semantic Versioning:** APIs, and key documents or schemas managed or referenced by KOIOS, should follow semantic versioning (SemVer) to ensure clarity and manage dependencies effectively.
*   **Adherence to EGOS Global Rules:** All documentation and versioning practices must align with the overarching [EGOS Global Rules (.windsurfrules)](file:///C:/EGOS/.windsurfrules) and any specific EGOS Framework guidelines (e.g., [EGOS_MCP_Standardization_Guidelines.md](file:///C:/EGOS/EGOS_Framework/docs/standards/EGOS_MCP_Standardization_Guidelines.md)).

KOIOS plays a role in making these standards discoverable and in validating compliance where possible.

## Related Resources

- **Smart Tips Protocol:** `.cursor/rules/smart-tips.mdc`
- **Git Workflow Standards:** `.cursor/rules/git_workflow_standards.mdc`
- **Commit Message Standards:** `.cursor/rules/commit_messages.mdc`

## Changelog

- **1.0 (April 7, 2025):** Initial documentation of Smart Tips Protocol and Git Workflow Standards

---

✧༺❀༻∞ EGOS ∞༺❀༻✧