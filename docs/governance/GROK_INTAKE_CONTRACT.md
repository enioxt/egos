# GROK Task Intake Contract

> **SSOT Owner:** `egos/docs/governance/GROK_INTAKE_CONTRACT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Tasks:** EGOS-103, EGOS-104

---

## Purpose

Any task, idea, or architectural suggestion originating from an external AI session (Grok, AI Studio, ChatGPT, any AI without direct repo access) must pass through this intake contract before entering TASKS.md or being acted on. Prevents phantom tasks, conflicting decisions, and unreconciled drift.

---

## GROK_TASK_INTAKE Template

Copy this for every external-AI-sourced task:

```markdown
## GROK_INTAKE — <short title>

| Field | Value |
|-------|-------|
| **Source** | Grok / AI Studio / ChatGPT / other |
| **Session link** | <URL or "exported transcript at docs/intake/<file>"> |
| **Quote / snippet** | "<exact text from AI that motivates this task>" |
| **Intended repo** | egos / egos-lab / FORJA / EGOS-Inteligencia / undecided |
| **Impact** | high / medium / low |
| **Effort** | days / hours / minutes |
| **Confidence** | confirmed / plausible / speculative |
| **Owner** | <name> |
| **Conflicts with** | <EGOS-NNN if it contradicts an existing decision, else "none"> |
| **Reconciled** | [ ] checked against kernel SSOT (TASKS.md, SSOT_REGISTRY, FLAGSHIP_BRIEF) |

### Reconciliation notes
<What changed or what was confirmed after checking kernel SSOT>

### Kernel SSOT verdict
- [ ] APPROVED — safe to add to TASKS.md as EGOS-NNN
- [ ] MODIFIED — added with these changes: <changes>
- [ ] REJECTED — conflicts with: <reason>
```

---

## Cross-Repo Task Router Policy

When a task is approved, route it by these rules:

| Task type | Target repo | Rationale |
|-----------|------------|-----------|
| Kernel governance, packages, agents | `egos` | Always kernel-first |
| Guard Brasil product features | `egos` (packages/guard-brasil) | Flagship lives in kernel |
| Web app features (dashboard, landing) | `egos-lab` | App layer |
| WhatsApp / marketplace features | `carteira-livre` | Domain-specific |
| ERP / investigation features | `FORJA` or `EGOS-Inteligencia` | Domain-specific |
| Undecided at intake time | `egos` (Grok Intake Queue section) | Hold temporarily, migrate when clear |

Migration rule: Tasks in the `## Grok Intake Queue` section of `egos/TASKS.md` must be migrated to their target repo within 14 days of creation, or they get a `P3` demotion and a target_repo annotation.

---

## Intake Queue Hygiene

The `## Grok Intake Queue` section in TASKS.md must stay ≤10 items:
- Intake → Reconcile → Route within one session
- If queue grows >10: stop adding, migrate existing ones first

---

## Deduplication Rules

Before adding a Grok-sourced task, search:
```bash
grep -i "<keyword from task>" TASKS.md
```

If a similar task exists:
- Mark the Grok source as a "+1 signal" in a comment on the existing task
- Do not create a duplicate entry

---

*Maintained by: EGOS Kernel*
*Related: EGOS-103, EGOS-104, EGOS-105, EGOS-106, docs/governance/ANTI_INJECTION_HARDENING.md*
