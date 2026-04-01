# Gem Hunter — Single Source of Truth

> **Version:** 1.0.0 | **Updated:** 2026-04-01
> **Owner:** EGOS Kernel | **Domain:** Discovery Intelligence

---

## What is Gem Hunter?

Automated discovery pipeline that finds, scores, and extracts transplantable patterns from open-source repositories for the EGOS ecosystem.

## SSOT Locations

### Code (canonical)

| Component | Path | LOC | Status |
|-----------|------|-----|--------|
| **Core Engine v5.0** | `egos-lab/agents/agents/gem-hunter.ts` | 1528 | ACTIVE — runs via CCR scheduled job |
| **SecOps Scanner** | `egos/scripts/gem-hunter-secops.ts` | 58 | ACTIVE — security-focused variant |
| **Freshness Checker** | `egos-lab/scripts/gem-hunter-freshness.ts` | 60 | ACTIVE — validates repo freshness |
| **Gratitude Tracker** | `~/.egos/bin/gem-hunter-gratitude.ts` | 93 | ACTIVE — tracks open-source attribution |
| **ARCH Model Config** | `arch/src/lib/model-gem-hunter.ts` | 291 | ACTIVE — ARCH-specific, stays in arch |

### Reports (canonical)

| Type | Path |
|------|------|
| **Discovery reports** | `egos-lab/docs/gem-hunter/gems-YYYY-MM-DD.md` |
| **Latest run state** | `egos-lab/docs/gem-hunter/latest-run.json` |
| **Assets (SSOT blocks)** | `egos-lab/docs/gem-hunter/assets/` |

### Configuration (canonical — NEW)

| Type | Path |
|------|------|
| **Registry (all repos)** | `egos/docs/gem-hunter/registry.yaml` |
| **Scoring weights** | `egos/docs/gem-hunter/weights.yaml` |
| **Pair analysis reports** | `egos/docs/gem-hunter/pairs/egos__<repo>/` |
| **Session records** | `egos/docs/gem-hunter/sessions/` |

### Skills

| Skill | Path |
|-------|------|
| `/study` | `~/.egos/.claude/commands/study.md` |
| `/study-end` | `~/.egos/.claude/commands/study-end.md` |

### Scheduled Execution

| Job | Schedule | Platform |
|-----|----------|----------|
| Gem Hunter Adaptive Intelligence | Seg+Qui 2h37 BRT | Claude Code CCR (trig_01Sn7Y...) |

### Deprecated / Removed

| What | Was at | Reason |
|------|--------|--------|
| ~~aiox-gem-hunter.ts~~ | `egos/agents/agents/` | Dead code, never called |
| ~~mastra-gem-hunter.ts~~ | `egos/agents/agents/` | Dead code, never called |
| ~~gem_hunter.py~~ | `br-acc/agents/gem_hunter/` | Replaced by TS engine |
| ~~gem-hunter-secops.ts~~ | `852/scripts/` | Duplicate of egos/ version |
| ~~gem-hunter-daily.yml~~ | `egos-lab/.github/workflows/` | Replaced by CCR job |

---

## Architecture

```
6-Layer Pipeline:
  L1 Discovery → L2 Triage → L3 Pair Diagnosis → L4 Decision Intelligence → L5 SSOT → L6 Continuous Operation

10 Analytical Categories:
  coding_surface | agent_runtime | memory_context | model_gateway | observability_evals
  retrieval_context | durable_workflow | protocol_tooling | product_surface | governance_safety

9-Factor Scoring (see weights.yaml):
  egos_relevance(0.24) + transplantability(0.18) + complementarity(0.14) + novelty(0.12)
  + maintenance(0.10) + doc_quality(0.08) + license(0.06) + op_fit(0.04) + obs_maturity(0.04)
```

## Rules

1. **One SSOT**: This file is the canonical reference. All other mentions should point here.
2. **Clean-room only**: Never copy code from external repos. Extract patterns, not implementations.
3. **Read-only reference repos**: External repos cloned to `/tmp/gem-hunter-study/` are never modified.
4. **License check**: Before any transplant proposal, verify license compatibility.
5. **Mandatory closure**: Every `/study` session must end with `/study-end` (9 sections).
6. **Evidence-based**: Every conclusion must cite source files/modules.
