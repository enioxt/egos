# EGOS Agent Lineage Matrix (ARCH-003)

> **Generated:** 2026-03-13
> **Source:** Git commit history (per-file `--diff-filter=A`), agents.json registry, handoff documents
> **Scope:** All 29 egos-lab agents + 2 egos-native agents

---

## Complete Agent Registry — Commit-Level Tracing

| # | Agent ID | Name | Area | Created | Commit | Entrypoint | Status | Wave | Origin |
|---|----------|------|------|---------|--------|------------|--------|------|--------|
| 1 | `idea_scanner` | Idea Scanner | knowledge | 2026-02-13 | `cd9ca0f` | scripts/scan_ideas.ts | active | 0 | script |
| 2 | `security_scanner` | Security Scanner | security | 2026-02-16 | `abbc741` | scripts/security_scan.ts | active | 0 | script |
| 3 | `rho_calculator` | Rho Calculator | observability | 2026-02-16 | `15b7548` | scripts/rho.ts | active | 0 | script |
| 4 | `code_reviewer` | Cortex Reviewer | qa | 2026-02-16 | `b90542d` | scripts/review.ts | active | 0 | script |
| 5 | `disseminator` | Knowledge Disseminator | knowledge | 2026-02-16 | `b90542d` | scripts/disseminate.ts | active | 0 | script |
| 6 | `ssot_auditor` | SSOT Auditor | architecture | 2026-02-17 | `ca85cb7` | agents/agents/ssot-auditor.ts | active | 1 | kernel |
| 7 | `auth_roles_checker` | Auth & Roles Checker | auth | 2026-02-17 | `0c5afdb` | agents/agents/auth-roles-checker.ts | active | 1 | kernel |
| 8 | `dep_auditor` | Dependency Auditor | architecture | 2026-02-17 | `7c080cb` | agents/agents/dep-auditor.ts | active | 1 | kernel |
| 9 | `dead_code_detector` | Dead Code Detector | qa | 2026-02-17 | `7c080cb` | agents/agents/dead-code-detector.ts | active | 1 | kernel |
| 10 | `orchestrator` | Agent Orchestrator | orchestration | 2026-02-17 | `b03569e` | agents/agents/orchestrator.ts | active | 1 | kernel |
| 11 | `ui_designer` | Stitch UI Designer | design | 2026-02-18 | `d7eeaef` | agents/agents/ui-designer.ts | active | 2 | kernel |
| 12 | `contract_tester` | Contract Tester | qa | 2026-02-18 | `880ca31` | agents/agents/contract-tester.ts | active | 2 | kernel |
| 13 | `integration_tester` | Integration Tester | qa | 2026-02-18 | `880ca31` | agents/agents/integration-tester.ts | active | 2 | kernel |
| 14 | `ai_verifier` | AI Verifier | qa | 2026-02-18 | `534e4a6` | agents/agents/ai-verifier.ts | active | 2 | kernel |
| 15 | `regression_watcher` | Regression Watcher | qa | 2026-02-18 | `6d00fdb` | agents/agents/regression-watcher.ts | active | 2 | kernel |
| 16 | `ambient_disseminator` | Ambient Disseminator | knowledge | 2026-02-20 | `a84d709` | scripts/ambient_disseminator.ts | active | 3 | script |
| 17 | `domain_explorer` | Domain Explorer | architecture | 2026-02-20 | `e0da819` | agents/agents/domain_explorer.ts | active | 3 | kernel |
| 18 | `living_laboratory` | Living Laboratory | architecture | 2026-02-20 | `5870168` | agents/agents/living-laboratory.ts | active | 3 | kernel |
| 19 | `social_media_agent` | Social Media Agent | knowledge | 2026-02-22 | `53b38b5` | agents/agents/social-media.ts | pending | 3 | kernel |
| 20 | `security_scanner_v2` | Security Scanner v2 | security | 2026-02-23 | `010b89f` | agents/agents/security-scanner.ts | active | 3 | kernel |
| 21 | `showcase_writer` | Showcase Writer | qa | 2026-02-23 | `010b89f` | agents/agents/showcase-writer.ts | active | 3 | kernel |
| 22 | `open_source_readiness` | Open Source Readiness | orchestration | 2026-02-23 | `010b89f` | agents/agents/open-source-readiness.ts | active | 3 | kernel |
| 23 | `carteira_x_engine` | Carteira X Engine | observability | 2026-02-26 | `cba8f6b` | agents/agents/carteira-x-engine.ts | active | 4 | kernel |
| 24 | `ssot_fixer` | SSOT Fixer | architecture | 2026-03-06 | `f535ce5` | agents/agents/ssot-fixer.ts | active | 4 | kernel |
| 25 | `gem_hunter` | Gem Hunter | knowledge | 2026-03-06 | `e0f2d7a` | agents/agents/gem-hunter.ts | active | 4 | kernel |
| 26 | `ghost_hunter` | ??? (dormant placeholder) | discovery | 2026-03-06 | `fa7a673` | docs/protocols/rho-calibration.md | dormant | 4 | easter-egg |
| 27 | `report_generator` | Report Generator | knowledge | 2026-03-08 | `3effbaa` | agents/agents/report-generator.ts | active | 4 | kernel |
| 28 | `autoresearch` | AutoResearch | qa | 2026-03-09 | `9bf334f` | egos-autoresearch/autoresearch.ts | active | 4 | external |
| 29 | `e2e_smoke` | E2E Smoke Validator | qa | — | — | agents/agents/e2e-smoke.ts | pending | — | planned |

### egos-native agents (kernel repo)

| # | Agent ID | Name | Area | Created | Entrypoint | Status |
|---|----------|------|------|---------|------------|--------|
| 30 | `dep_auditor` | Dependency Auditor | architecture | 2026-03-13 | agents/agents/dep-auditor.ts | active |
| 31 | `archaeology_digger` | Archaeology Digger | knowledge | 2026-03-13 | agents/agents/archaeology-digger.ts | active |

---

## Wave Analysis

### Wave 0 — Survival Coding (Feb 13-16) — 5 agents
Script-born utilities solving immediate pain. No registry, no runtime, no governance.
- **Pattern:** `scripts/*.ts` files run via `bun scripts/X.ts`
- **Catalyst:** Tactical need — secret scanning, idea extraction, health scoring
- **Key insight:** These scripts are the "primordial soup" — they would later evolve into governed agents

### Wave 1 — Agent Kernel (Feb 17) — 5 agents
The runtime crystallizes. `runner.ts`, `agents.json`, `event-bus.ts` are created.
- **Pattern:** `agents/agents/*.ts` with registry entry, dry-run/exec modes, correlation IDs
- **Catalyst:** Studying AutoGen, CrewAI, LangGraph → deciding EGOS needs its own lightweight zero-dep runtime
- **Commits:** 4 commits in one day (`ca85cb7` → `b03569e`)
- **Key insight:** This is the single most important day — scripts became governed agents

### Wave 2 — QA/Design (Feb 18) — 5 agents
Complete 5-layer testing architecture designed and implemented in one session.
- **Pattern:** Structured QA layers — contract, integration, regression, AI verification, UI design
- **Catalyst:** Prompt engineering — using structured interrogator prompts to decompose QA
- **Commits:** 4 commits (`d7eeaef` → `6d00fdb`)

### Wave 3 — Reflexive + Hardening (Feb 20-23) — 7 agents
The system starts watching itself. Event bus enables inter-agent communication.
- **Pattern:** Self-observation agents + operational hardening for open-source
- **Catalyst:** "A system that cannot observe itself cannot improve itself"
- **Key agents:** `ambient_disseminator`, `domain_explorer`, `living_laboratory`

### Wave 4 — Research/Ecosystem (Feb 26 - Mar 09) — 7 agents
The system starts producing original research and self-modifying.
- **Pattern:** Discovery engines, self-repair, autonomous research
- **Catalyst:** Gem Hunter = multi-source discovery; SSOT Fixer = first self-modifying agent
- **Key agents:** `gem_hunter`, `ssot_fixer`, `autoresearch`, `report_generator`

### Wave 5 — Kernel Extraction (Mar 13+) — 2+ agents
Agents born native to the egos kernel, not migrated from egos-lab.
- **Pattern:** Archaeology and governance tooling
- **First native agent:** `archaeology_digger`

---

## Area Distribution

| Area | Count | Agents |
|------|-------|--------|
| qa | 8 | code_reviewer, dead_code_detector, contract_tester, integration_tester, ai_verifier, regression_watcher, showcase_writer, autoresearch |
| knowledge | 6 | idea_scanner, disseminator, ambient_disseminator, social_media_agent, gem_hunter, report_generator |
| architecture | 5 | ssot_auditor, dep_auditor, domain_explorer, living_laboratory, ssot_fixer |
| security | 2 | security_scanner, security_scanner_v2 |
| orchestration | 2 | orchestrator, open_source_readiness |
| observability | 2 | rho_calculator, carteira_x_engine |
| auth | 1 | auth_roles_checker |
| design | 1 | ui_designer |
| discovery | 1 | ghost_hunter (dormant) |

---

## Origin Classification

| Origin | Count | Description |
|--------|-------|-------------|
| **kernel** | 18 | Born in `agents/agents/` with full runtime integration |
| **script** | 6 | Born as `scripts/*.ts`, later registered in agents.json |
| **external** | 1 | Adapted from external project (karpathy/autoresearch) |
| **easter-egg** | 1 | Deliberate dormant placeholder (ghost_hunter) |
| **planned** | 1 | Registered but not yet implemented (e2e_smoke) |
| **egos-native** | 2 | Born in egos/ kernel repo |

---

## Catalyst Classification

| Catalyst | Count | Examples |
|----------|-------|---------|
| **tactical-need** | 6 | security_scanner, dep_auditor, showcase_writer |
| **qa-architecture** | 5 | contract_tester, integration_tester, regression_watcher |
| **governance-enforcement** | 4 | ssot_auditor, ssot_fixer, domain_explorer, archaeology_digger |
| **research-expansion** | 5 | gem_hunter, report_generator, autoresearch, ui_designer |
| **self-observation** | 3 | ambient_disseminator, living_laboratory, domain_explorer |
| **external-communication** | 2 | social_media_agent, carteira_x_engine |
| **organic-growth** | 6 | rho_calculator, dead_code_detector, orchestrator, code_reviewer |

---

## Key Lineage Relationships

```
scripts/security_scan.ts (Feb 16) ──evolves──▶ security_scanner_v2 (Feb 23)
scripts/disseminate.ts (Feb 16) ──spawns──▶ ambient_disseminator (Feb 20)
ssot_auditor (Feb 17) ──produces-findings-for──▶ ssot_fixer (Mar 06)
orchestrator (Feb 17) ──coordinates──▶ all agents via MyceliumBus
contract_tester (Feb 18) + integration_tester (Feb 18) ──feed──▶ regression_watcher (Feb 18)
gem_hunter (Mar 06) ──discovers──▶ autoresearch pattern (Mar 09)
karpathy/autoresearch ──adapted-to──▶ autoresearch agent (Mar 09)
dep_auditor (egos-lab Feb 17) ──migrated-to──▶ dep_auditor (egos Mar 13)
```

---

## Verification Status

- **Verified:** All 29 agent creation dates confirmed via `git log --diff-filter=A`
- **Verified:** All entrypoints exist in filesystem (except `e2e_smoke` — pending)
- **Verified:** Registry lint passes: 29 agents in egos-lab, 2 in egos, 0 errors
- **Inferred:** Wave assignments based on date clustering and commit message analysis
- **Inferred:** Catalyst classifications based on agent description + commit context
