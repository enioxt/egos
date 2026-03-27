# AGENT_DEPRECATION_LOG.md — EGOS Agent Lifecycle Audit Trail

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-27 | **TYPE:** Historical audit log (SSOT)
> **PURPOSE:** Transparent record of all agent removals, deprecations, and transitions

---

## Removed Agents (Kernel)

> **Reason:** Never implemented. Registered in agents.json but no entrypoint file exists.
> **Impact:** Pre-commit hook now prevents this pattern (Rule 8 — Ghost Agent Detection)

| Agent ID | Name | Risk Level | Entrypoint | Removed Date | Reason | Notes |
|----------|------|------------|-----------|--------------|--------|-------|
| `orchestrator` | Agent Orchestrator | T3 | `agents/agents/orchestrator.ts` ❌ | 2026-03-27 | Ghost agent (file never created) | Core runner — should have been priority. Blocked on unknown reason. |
| `security_scanner_v2` | Security Scanner v2 | T1 | `agents/agents/security-scanner.ts` ❌ | 2026-03-27 | Ghost agent (file never created) | Gitleaks wrapper — security-critical. May have been attempted but reverted? |
| `report_generator` | Report Generator | T0 | `agents/agents/report_generator.ts` ❌ | 2026-03-27 | Ghost agent (file never created) | AIXBT dashboard reporter — observability gap. Alternative: use etl_orchestrator. |

---

## Removed Agents (Egos-Lab)

> **Reason:** Duplicates of kernel agents. Removed during Phase 1 consolidation audit (2026-03-26).

| Agent ID | Name | Removed Date | Reason | Notes |
|----------|------|--------------|--------|-------|
| `dep_auditor` | Dependency Auditor | 2026-03-26 | Duplicate of kernel agent | Consolidated to kernel (portable, zero deps). |
| `dead_code_detector` | Dead Code Detector | 2026-03-26 | Duplicate of kernel agent | Consolidated to kernel (portable, zero deps). |

---

## Dormant Agents (Active in Registry, Intentional Pause)

> **Status:** `dormant` — Agent is registered but not scheduled. Has TODO comment explaining blocker.

| Agent ID | Repository | Entrypoint | Blocker | Priority |
|----------|------------|-----------|---------|----------|
| `e2e_smoke` | egos-lab | `agents/agents/e2e-smoke.ts` | Playwright MCP not implemented | P2 |
| `social_media_agent` | egos-lab | `agents/agents/social-media.ts` | Content strategy undefined | P3 |
| `ghost_hunter` | egos-lab | `docs/protocols/rho-calibration.md` ❌ | Discovery protocol unfinished | P3 |

---

## Broken Agents (Has Broken Dependencies, Marked as Active)

> **Status:** `active` but cannot execute — waiting for MCP implementations.

| Agent ID | Repository | Dependency | Impact | Task |
|----------|-----------|-----------|--------|------|
| `contract_tester` | egos-lab | Supabase MCP | Cannot run contract tests vs DB | TASKS.md#MCP-001 |
| `integration_tester` | egos-lab | Supabase MCP | Cannot run integration tests | TASKS.md#MCP-001 |
| `code_reviewer` | egos-lab | Morph MCP | Cannot transform code AST | TASKS.md#MCP-002 |
| `ssot_fixer` | egos-lab | Morph MCP | Cannot auto-fix SSOT drift | TASKS.md#MCP-002 |
| `etl_orchestrator` | egos-lab | Supabase MCP | Cannot monitor br-acc 24/7 | TASKS.md#MCP-001 |

---

## Summary: Agent Health Status

| Metric | Kernel | Lab | Total | Status |
|--------|--------|-----|-------|--------|
| Registered (active) | 9 | 20 | 29 | 🟡 Some are ghost agents |
| Implemented | 6 | ? | ? | 🔴 3 kernel ghost agents need removal |
| Dormant | 0 | 3 | 3 | 🟡 Need minimal `.ts` + TODO |
| Broken (MCP deps) | 0 | 6+ | 6+ | 🟠 Blocking Phase 1 completion |

---

## Document History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-03-27 | activation.egos | Initial creation — Phase 1 audit trail |
