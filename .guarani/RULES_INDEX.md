# EGOS Rules Index — Canonical Discovery Map

> **Version:** 1.2.0 | **Updated:** 2026-04-06
> **Purpose:** Single entry point for ALL EGOS rules, standards, and governance surfaces.
> Any AI session or human contributor starts here to find the relevant rule.

---

## Quick Lookup

| I need rules for... | File | Location |
|---------------------|------|----------|
| **Governance canon** | RULES_INDEX.md | `.guarani/RULES_INDEX.md` |
| **Multi-env sync** | governance-sync.sh | `scripts/governance-sync.sh` |
| **Shared home mirror** | EGOS sync | `.egos/sync.sh` |
| **Claude Code adapter** | CLAUDE.md | `CLAUDE.md` |
| **Windsurf adapter** | .windsurfrules | `.windsurfrules` |
| **Reports** | REPORT_SSOT.md | `docs/REPORT_SSOT.md` |
| **Code quality** | PREFERENCES.md | `.guarani/PREFERENCES.md` |
| **Rollout / launch planning** | PREFERENCES.md + DOMAIN_RULES.md | `.guarani/PREFERENCES.md`, `.guarani/orchestration/DOMAIN_RULES.md` |
| **Agent claims** | AGENT_CLAIM_CONTRACT.md | `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md` |
| **Worktree workflow** | WORKTREE_CONTRACT.md | `.guarani/orchestration/WORKTREE_CONTRACT.md` |
| **QA/Testing** | QA_LOOP_CONTRACT.md | `.guarani/orchestration/QA_LOOP_CONTRACT.md` |
| **Integration releases** | INTEGRATION_RELEASE_CONTRACT.md | `.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md` |
| **Spec pipeline** | SPEC_PIPELINE_CONTRACT.md | `.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md` |
| **Monthly review** | CLARITY_REVIEW.md | `.guarani/orchestration/CLARITY_REVIEW.md` |
| **Benchmarks** | BENCHMARK_ENFORCEMENT.md | `.guarani/orchestration/BENCHMARK_ENFORCEMENT.md` |
| **LLM routing** | LLM_ORCHESTRATION_MATRIX.md | `.guarani/orchestration/LLM_ORCHESTRATION_MATRIX.md` |
| **PII/LGPD** | Guard Brasil | `packages/guard-brasil/src/pii-patterns.ts` |
| **PII masking API** | Guard Brasil API | `apps/api/src/server.ts` (POST /v1/inspect) |
| **Meta-prompts** | Trigger system | `.guarani/prompts/triggers.json` |
| **Prompt anatomy** | PROMPT_SYSTEM.md | `.guarani/prompts/PROMPT_SYSTEM.md` |
| **SSOT registry** | SSOT_REGISTRY.md | `docs/SSOT_REGISTRY.md` |
| **Branding** | BRAND_CANONICAL.md | `docs/BRAND_CANONICAL.md` |
| **Engineering** | ENGINEERING_STANDARDS_2026.md | `.guarani/ENGINEERING_STANDARDS_2026.md` |
| **MCP quality** | MCP_TOOL_QUALITY_FRAMEWORK.md | `.guarani/standards/MCP_TOOL_QUALITY_FRAMEWORK.md` |
| **Domain rules** | DOMAIN_RULES.md | `.guarani/orchestration/DOMAIN_RULES.md` |
| **Pre-commit hooks** | pre-commit | `.husky/pre-commit` |
| **File classification** | file-intelligence.sh | `scripts/file-intelligence.sh` |
| **Doc proliferation** | check-doc-proliferation.sh | `scripts/check-doc-proliferation.sh` |
| **Agent identity** | IDENTITY.md | `.guarani/IDENTITY.md` |
| **Autonomy & challenge mode** | AUTONOMY_RULES.md | `.guarani/orchestration/AUTONOMY_RULES.md` |
| **Investigation protocol** | INVESTIGATION_PROTOCOL.md | `.guarani/orchestration/INVESTIGATION_PROTOCOL.md` |
| **Vocabulary map** | INVESTIGATION_PROTOCOL.md §21 | `.guarani/orchestration/INVESTIGATION_PROTOCOL.md` |
| **Snapshot versioning** | AUTONOMY_RULES.md §17 | `.guarani/orchestration/AUTONOMY_RULES.md` |
| **Disseminate everywhere** | AUTONOMY_RULES.md §18 | `.guarani/orchestration/AUTONOMY_RULES.md` |
| **Meta-prompt activation** | AUTONOMY_RULES.md §19 | `.guarani/orchestration/AUTONOMY_RULES.md` |
| **Chatbot everywhere** | AUTONOMY_RULES.md §22 | `.guarani/orchestration/AUTONOMY_RULES.md` |

## Enforcement Surfaces

| Surface | Enforcement | When |
|---------|-------------|------|
| Secrets | gitleaks | pre-commit (blocking) |
| Types | tsc --noEmit | pre-commit (blocking) |
| Frozen zones | git diff check | pre-commit (blocking) |
| Doc proliferation | check-doc-proliferation.sh | pre-commit (blocking) |
| Governance drift | governance-sync.sh --check | pre-commit (blocking) |
| SSOT file sizes | wc -l check | pre-commit (blocking) |
| File intelligence | file-intelligence.sh | pre-commit (warnings + blocking for PII/.env) |
| Report compliance | REPORT_SSOT rules | file-intelligence.sh (warnings) |
| Agent claims | agents.json lint | bun agent:lint |
| QA evidence | QA_LOOP_CONTRACT | PR review |
| **Task ID sync** | **auto-disseminate.sh** | **post-commit (non-blocking)** |
| **HARVEST.md injection** | **auto-disseminate.sh** | **post-commit (non-blocking)** |
| **Daily handoff** | **session-aggregator.sh** | **cron 02:30 UTC (non-blocking)** |
| **Knowledge compile** | **daily-knowledge-sync.sh** | **cron 13:00 UTC (non-blocking)** |

## For AI Sessions

When starting any work, check:
1. `.guarani/RULES_INDEX.md` (this file) — canonical rule discovery
2. `TASKS.md` — what is pending and in what order
3. `.guarani/PREFERENCES.md` — coding and rollout standards
4. `CLAUDE.md` / `.windsurfrules` — environment adapter surface only
5. `.guarani/orchestration/` — if touching governance or planning execution
6. `docs/REPORT_SSOT.md` — if generating reports

> **Rule:** Never generate a report without reading REPORT_SSOT.md first.
> **Rule:** Never claim an agent without reading AGENT_CLAIM_CONTRACT.md first.
> **Rule:** Never release an integration without reading INTEGRATION_RELEASE_CONTRACT.md first.
> **Rule:** Default to maximum autonomy — act first, report after (§15).
> **Rule:** Challenge stale P0s, scope creep, and false claims (§16).
> **Rule:** Every discovery/architecture decision must produce FACT/INFERENCE/PROPOSAL (§20).
> **Rule:** Use Enio's vocabulary map for term translation (§21).
> **Rule:** If any adapter surface (`CLAUDE.md`, `.windsurfrules`) conflicts with `.guarani`, `.guarani` wins.
> **Rule:** Include task IDs in commit subjects for auto-propagation to TASKS.md (§28).
> **Rule:** Add `LEARNING: <insight>` lines to commit bodies to auto-append to HARVEST.md (§28).
> **Rule:** On `/start`, read last 3 days of `docs/jobs/` — surface CRITICAL as [BLOCKER] (§29).
