# Documentation SSOT Audit & Cleanup Plan

> **DATE:** 2026-03-29
> **PURPOSE:** Apply SSOT Merge Rule (#23) to eliminate doc duplication.
> **FINDING:** 89 docs, 17,900 lines. Only 22 have VERSION tags (canonical). 67 are one-off/stale.

## SSOT Duplications Found

### Guard Brasil (3 docs about same thing)
| File | Lines | Action |
|------|-------|--------|
| `docs/products/GUARD_BRASIL.md` | 172 | KEEP — product definition SSOT |
| `docs/products/GUARD_BRASIL_FREE_PAID.md` | 105 | MERGE into GUARD_BRASIL_PRODUCT_BOUNDARY |
| `docs/strategy/GUARD_BRASIL_PRODUCT_BOUNDARY.md` | 99 | KEEP — strategy SSOT |

**Action:** Merge FREE_PAID into PRODUCT_BOUNDARY (they cover same topic).

### MCP Strategy (4 docs about same thing)
| File | Lines | Action |
|------|-------|--------|
| `docs/MCP_IMPLEMENTATION_SUMMARY.md` | 354 | ARCHIVE — superseded by Matrix |
| `docs/MCP_INTEGRATION_GUIDE.md` | 760 | ARCHIVE — 760 lines, stale |
| `docs/MCP_INTEGRATION_MAP.md` | 206 | KEEP — has VERSION tag |
| `docs/MCP_ORCHESTRATION_STRATEGY.md` | 303 | KEEP — has VERSION tag |

**Action:** Archive IMPLEMENTATION_SUMMARY and INTEGRATION_GUIDE to `_archived_handoffs/`.

### Model/LLM Routing (3 docs about same thing)
| File | Lines | Action |
|------|-------|--------|
| `docs/MODEL_SPECIALIZATIONS.md` | 305 | ARCHIVE — superseded by LLM_ORCHESTRATION_MATRIX |
| `docs/ROUTING_DECISION_TREE.txt` | ? | ARCHIVE — aspirational, not code-backed |
| `docs/contracts/LLM_ORCHESTRATION_MATRIX.md` | 64 | KEEP — canonical SSOT |

### EGOS-116 Presentation (6 docs)
All 5 PRESENTATION_*.md + INDEX are canonical. But EGOS-116_COMPLETION_STATUS.md is a one-off status doc.
**Action:** Archive EGOS-116_COMPLETION_STATUS.md.

### FORJA (2 docs, not kernel concern)
| File | Lines | Action |
|------|-------|--------|
| `docs/FORJA_INVENTORY_WEDNESDAY_MEETING.md` | 526 | ARCHIVE — meeting notes, not SSOT |
| `docs/FORJA_P0_P1_FOCUS.md` | 432 | ARCHIVE — should live in FORJA repo |

### One-Off Docs (should archive)
| File | Lines | Reason |
|------|-------|--------|
| `docs/ACTIVATION_GUIDE.md` | 316 | OpenCode-specific, stale |
| `docs/BLUEPRINT_TASKS_MATRIX.md` | 223 | BLUEPRINT absorption done |
| `docs/KERNEL_MISSION_CONTROL.md` | 435 | Frontend design, stale |
| `docs/MARKET_READY_FEATURES.md` | 123 | Superseded by FLAGSHIP_BRIEF |
| `docs/METRICS_DASHBOARD.md` | 331 | Concept only, not built |
| `docs/MISSION_CONTROL_FRONTEND_DESIGN.md` | 1257 | Frontend design, 1257 lines! |
| `docs/OPENCODE_CUSTOM_FORK_STRATEGY.md` | 434 | OpenCode-specific |
| `docs/OPENCODE_FREE_MODELS_SETUP.md` | 403 | OpenCode-specific |
| `docs/SYSTEM_CHECKLIST_20260325.md` | 268 | Timestamped! Violates anti-proliferation |
| `docs/TASKS_HUMAN_VALIDATION_REQUIRED.md` | 152 | One-off validation list |
| `docs/conversaGROK.md` | 2729 | External conversation dump |

### Handoffs >30 days old
All handoffs in `docs/_current_handoffs/` from before 2026-03-01 should move to `docs/_archived_handoffs/`.

## Summary of Actions

| Action | Files | Lines Freed |
|--------|-------|-------------|
| Archive MCP docs (2) | 2 | ~1,114 |
| Archive model docs (2) | 2 | ~305+ |
| Archive FORJA docs (2) | 2 | ~958 |
| Archive one-off docs (11) | 11 | ~6,671 |
| Archive EGOS-116 status | 1 | ~388 |
| Merge Guard Brasil FREE_PAID | 1 | ~105 |
| **Total** | **19 files** | **~9,541 lines** |

Post-cleanup: ~70 docs → ~51 docs, ~17,900 lines → ~8,400 lines.

## Canonical SSOT Docs (Keep — The Real SSOT)

| Doc | Purpose | Version |
|-----|---------|---------|
| AGENTS.md | System identity | v2.0.0 |
| TASKS.md | Roadmap | v2.9.0 |
| .windsurfrules | Rules | 23 rules |
| docs/SSOT_REGISTRY.md | Cross-repo SSOT map | v2.0.0 |
| docs/SYSTEM_MAP.md | Activation map | v3.0.0 |
| docs/CAPABILITY_REGISTRY.md | Capability index | v1.4.0 |
| docs/modules/CHATBOT_SSOT.md | Chatbot standard | v1.2.0 |
| docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md | Product/module classification | v1.1.0 |
| docs/knowledge/HARVEST.md | Knowledge accumulation | v2.1.0 |
| docs/contracts/AGENT_CLAIM_CONTRACT.md | Agent maturity taxonomy | v1.0.0 |
| docs/contracts/LLM_ORCHESTRATION_MATRIX.md | LLM lane routing | v1.0.0 |
| docs/contracts/NEW_PROJECT_GATE.md | Project gate | v1.0.0 |
| docs/strategy/FLAGSHIP_BRIEF.md | Guard Brasil brief | v1.0.0 |
| docs/strategy/OPERATOR_NARRATIVE_KIT.md | 1-page pitch | v1.0.0 |
| docs/strategy/REVENUE_MODEL_RECONCILIATION.md | Revenue unification | v1.0.0 |
| docs/strategy/GO_TO_MARKET_RESEARCH.md | GTM research | v2.0.0 |
| docs/strategy/EGOS_LAB_ARCHIVAL_PLAN.md | Lab consumer plan | v2.0.0 |
| docs/products/GUARD_BRASIL.md | Product definition | v1.0.0 |
| business/inventory.md | Product inventory | v2.0.0 |
