# Skill: System Map Management

> **Version:** 1.0.0
> **Trigger:** When creating, updating, or auditing SYSTEM_MAP.md

## Purpose

Standardized approach for maintaining capability registries across all EGOS repos.

## SYSTEM_MAP.md Structure

```markdown
# [Project] — System Map

> **Version:** X.X.X | **Date:** YYYY-MM-DD
> **Governance:** EGOS Kernel (`/home/enio/egos`)

## 1. Overview
Brief description of the project.

## 2. Capability Registry

### Status Legend
| Status | Meaning |
|--------|---------|
| ✅ Active | Implemented and working |
| 🔧 Partial | Partially implemented |
| 📋 Planned | Not yet implemented |
| 🔴 Missing | Critical gap |

### Capabilities Table
| # | Capability | Module | Status | Source |
|---|-----------|--------|--------|--------|
| 1 | Feature X | `path/to/module` | ✅ Active | Local/egos/852 |

## 3. Architecture
```text
project/
├── src/
│   └── ...
└── docs/
```

## 4. Tech Stack
| Layer | Technology | Status |
|-------|------------|--------|

## 5. Integrations
| Integration | Provider | Status |
|-------------|----------|--------|

## 6. Governance
When to update this file.

## 7. Roadmap
Sprint-based implementation plan.
```

## Update Triggers

Update SYSTEM_MAP.md when:
1. New API route added
2. New lib module created
3. Capability status changes
4. New integration added
5. Architecture changes

## Validation Checklist

- [ ] Version incremented
- [ ] Date updated
- [ ] All capabilities have status
- [ ] Source column filled
- [ ] Architecture matches reality
- [ ] Roadmap reflects current sprint

## Cross-Repo Consistency

All EGOS repos should follow this structure:
- `docs/SYSTEM_MAP.md` — Capability registry
- `AGENTS.md` — LLM-readable project config
- `TASKS.md` — SSOT for tasks

## Gap Analysis Template

When comparing repos:

| Priority | Capability | Source Repo | Target Repo | Effort |
|----------|-----------|-------------|-------------|--------|
| P0 | Feature X | 852 | forja | Low |
