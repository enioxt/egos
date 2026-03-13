# EGOS Development Tree Diagnostic — 2026-03-13

## Scope

This document reconstructs the current development tree of EGOS from repo evidence, git history, registry data, governance files, and migration work completed on 2026-03-13.

## Verified Sources

- `egos-lab/agents/registry/agents.json`
- `egos-lab/TASKS.md`
- `egos-lab/docs/KNOWLEDGE_ATLAS.md`
- `egos-lab/docs/EGOS_ECOSYSTEM_MAP.md`
- `egos-lab/docs/research/GROK_CONVERSATION_ANALYSIS_2026-03-09.md`
- `egos/docs/MIGRATION_PLAN.md`
- `git log --diff-filter=A --follow` on agents and core files

## Timeline — Core Formation

| Date | Layer | Evidence |
|------|-------|----------|
| 2026-02-13 | Repo governance base | `AGENTS.md`, `TASKS.md`, `.windsurfrules`, `.guarani/IDENTITY.md`, `.guarani/PREFERENCES.md` |
| 2026-02-16 | Script-born utility phase | `security_scan.ts`, `scan_ideas.ts`, `rho.ts`, `review.ts`, `disseminate.ts` |
| 2026-02-17 | Agent kernel crystallizes | `agents/runtime/runner.ts`, `agents/registry/agents.json`, `ssot_auditor`, `auth_roles_checker`, `dep_auditor`, `dead_code_detector`, `orchestrator` |
| 2026-02-18 | QA/design expansion | `ui_designer`, `contract_tester`, `integration_tester`, `regression_watcher`, `ai_verifier` |
| 2026-02-20 | Reflexive architecture phase | `event-bus.ts`, `ambient_disseminator`, `domain_explorer`, `living_laboratory` |
| 2026-02-22 to 2026-02-24 | Operational hardening | `start.sh`, `social_media_agent`, `setup.sh`, `security_scanner_v2`, `showcase_writer`, `open_source_readiness` |
| 2026-02-25 | Orchestration formalization | `.guarani/orchestration/PIPELINE.md`, `GATES.md` |
| 2026-02-26 to 2026-03-09 | Productized research phase | `carteira_x_engine`, `gem_hunter`, `report_generator`, `autoresearch` |
| 2026-03-13 | Kernel extraction | `egos/` canonical repo, governance sync, CI, first migrated agent |

## Agent Growth Curve

- `11` agents — documented in `handoff_session_ui_designer_skills_perf.md` on 2026-02-18
- `14` agents — documented in `handoff_session_testing_architecture_14_agents.md` on 2026-02-18
- `15` agents — documented in `handoff_session_15_agents_regression_watcher.md` on 2026-02-18
- `27` agents — documented in `TASKS.md` session sync for 2026-03-07
- `28` agents — documented in `TASKS.md` session sync for 2026-03-08 (`report_generator` added)
- `29` agents — documented in `TASKS.md` session sync for 2026-03-09 (`autoresearch` registered)

This shows an expansion pattern from a compact QA/governance nucleus into a broader agentic operating system with research, reporting, orchestration, and self-improvement layers.

## Agent Lineage Waves

- **Wave 0 — script utilities**
  - `security_scanner`, `idea_scanner`, `rho_calculator`, `code_reviewer`, `disseminator`
- **Wave 1 — governance and QA nucleus**
  - `ssot_auditor`, `auth_roles_checker`, `dep_auditor`, `dead_code_detector`, `ui_designer`, `contract_tester`, `integration_tester`, `regression_watcher`, `ai_verifier`, `orchestrator`
- **Wave 2 — self-observation and architecture**
  - `ambient_disseminator`, `domain_explorer`, `living_laboratory`
- **Wave 3 — publication and readiness**
  - `social_media_agent`, `security_scanner_v2`, `showcase_writer`, `open_source_readiness`
- **Wave 4 — flagship research and ecosystem coupling**
  - `carteira_x_engine`, `gem_hunter`, `report_generator`, `autoresearch`

## Order vs Entropy

### Order

- `egos/` now exists as the canonical kernel.
- `governance-sync.sh` enforces `egos/.guarani/ -> ~/.egos/guarani/`.
- `~/.egos/sync.sh` already symlinks `.egos`, workflows, and skills into leaf repos.
- `27/29` shared governance files are exact duplicates across `egos`, `egos-lab`, and `~/.egos`.
- Agent creation shows a coherent progression from scripts to governed agents to research products.

### Entropy

- `IDENTITY.md` and `PREFERENCES.md` drift between `egos` and `egos-lab`.
- Shared workflows are aligned, but local overrides still drift in `egos-lab/.agent/workflows/*` and in part of `br-acc` / `forja`.
- `ghost_hunter` is a deliberate dormant discovery placeholder whose entrypoint is a protocol doc, not an implemented TS agent.
- Historical docs still contain changing counts (`27`, `28`, `29`) and mixed snapshots from different phases.

## Transition Directives

- Keep `IDENTITY.md` and `PREFERENCES.md` local until repo-role drift is explicitly resolved.
- Review the remaining workflow overrides in `egos-lab/.agent`, `br-acc/.windsurf`, and `forja/.windsurf`.
- Continue replacing only exact matches with symlinks.
- Treat `egos-lab` as incubator/operations; stop letting it be the place where governance truth evolves first.

## Individual Growth Signal

The development path is clear: simple scripts -> governed repo rules -> agent runtime -> registry platform -> self-observing system -> research flagship -> canonical kernel extraction.

This supports a future narrative centered on personal evolution from tactical coding to ecosystem design, governance engineering, and agentic architecture.
