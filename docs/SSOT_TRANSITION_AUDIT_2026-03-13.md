# SSOT Transition Audit — 2026-03-13

## Verified State

- `27/29` `.guarani` files are exact duplicates across `egos`, `egos-lab`, and `~/.egos`
- `IDENTITY.md` and `PREFERENCES.md` are the only `.guarani` files with real drift
- All `7` core workflows in `~/.egos/workflows` are now aligned with the canonical `egos` versions
- Remaining drift is now limited to local overrides in leaf repos

## Safe To Link Now

- `DESIGN_IDENTITY.md`
- `ENGINEERING_STANDARDS_2026.md`
- `SEPARATION_POLICY.md`
- `orchestration/DOMAIN_RULES.md`
- `orchestration/GATES.md`
- `orchestration/PIPELINE.md`
- `orchestration/QUESTION_BANK.md`
- `philosophy/TSUN_CHA_PROTOCOL.md`
- `preprocessor.md`
- `prompts/PROMPT_SYSTEM.md`
- `prompts/meta/brainet-collective.md`
- `prompts/meta/mycelium-orchestrator.md`
- `prompts/meta/universal-strategist.md`
- `prompts/triggers.json`
- `refinery/README.md`
- `refinery/classifier.md`
- `refinery/compiler.md`
- `refinery/interrogators/bug.md`
- `refinery/interrogators/feature.md`
- `refinery/interrogators/knowledge.md`
- `refinery/interrogators/refactor.md`
- `refinery/vocabulary_learner.md`
- `security/SEC-001_PHONE_BRIDGE.md`
- `security/SEC-002_VPS_HARDENING.md`
- `standards/MCP_TOOL_QUALITY_FRAMEWORK.md`
- `tools/code-health-monitor.ts`
- `tools/privacy-scanner.ts`

## Keep Local For Now

- `IDENTITY.md`
- `PREFERENCES.md`
- `egos-lab/.agent/workflows/*`
- `br-acc/.windsurf/workflows/start.md`
- `br-acc/.windsurf/workflows/end.md`
- `br-acc/.windsurf/workflows/disseminate.md`
- `forja/.windsurf/workflows/start.md`
- `forja/.windsurf/workflows/end.md`
- `forja/.windsurf/workflows/disseminate.md`

## New Transition Tooling

- `scripts/governance-sync.sh`
  - Syncs `egos/.guarani/` into `~/.egos/guarani/`
- `scripts/link-ssot-files.sh`
  - Replaces only exact matches with symlinks
  - Skips any file with drift
- `package.json`
  - `bun ssot:link`
  - `bun ssot:link:exec`

## Current Rollout Status

1. Canonical governance synced from `egos` into `~/.egos`
2. Shared workflows aligned from `egos` into `~/.egos`
3. Exact-match linker executed in `egos-lab`, `852`, `br-acc`, `carteira-livre`, and `forja`
4. Remaining local overrides were intentionally skipped
