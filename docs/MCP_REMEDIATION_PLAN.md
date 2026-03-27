# MCP Remediation Plan

> **Status:** Phase 1 Complete | Phase 2 Blocked on implementation decisions
> **Last Updated:** 2026-03-27
> **Owner:** EGOS Kernel Governance

---

## Executive Summary

6 MCPs were configured in `~/.claude/config/mcp-servers.json` but never implemented:
- **Sequential Thinking** — Disabled (use native Claude feature)
- **Memory** — Disabled (use native mcp__memory__)
- **Filesystem** — Disabled (use native Read/Write/Edit tools)
- **GitHub** — Disabled (use native mcp__)
- **Supabase** — Disabled (needs implementation or workaround)
- **Morph** — Disabled (needs implementation or workaround)

**Blocking Agents:** 6 agents cannot function properly without MCPs
- **Supabase:** contract_tester, integration_tester, report_generator, etl_orchestrator
- **Morph:** code_reviewer, ssot_fixer

---

## Phase 1: Disabled Broken MCPs (✅ COMPLETE)

**Status:** `enabled: false` in ~/.claude/config/mcp-servers.json

### 1. Sequential Thinking
- **Issue:** File ~/.claude/mcp/sequential-thinking-server.js never created
- **Status:** DISABLED (2026-03-27)
- **Replacement:** Claude native sequential thinking works natively
- **Impact:** context_tracker, security_scanner, atrian_agent can still work
- **Action:** None needed — agents can use native reasoning

### 2. Memory
- **Issue:** File ~/.claude/mcp/memory-server.js never created
- **Status:** DISABLED (2026-03-27)
- **Replacement:** Use `mcp__memory__*` functions (create_entities, create_relations, etc)
- **Impact:** living_laboratory, ambient_disseminator need mcp__ wiring
- **Action:** Update agent code to use mcp__ instead of custom MCP

### 3. Filesystem
- **Issue:** File ~/.claude/mcp/filesystem-server.js never created
- **Status:** DISABLED (2026-03-27)
- **Replacement:** Use native Claude Code tools: Read, Write, Edit, Glob, Grep, Bash
- **Impact:** All agents — but native tools already available
- **Action:** None needed — agents can use native tools directly

### 4. GitHub
- **Issue:** File ~/.claude/mcp/github-server.js never created
- **Status:** DISABLED (2026-03-27)
- **Replacement:** Use native `mcp__*` functions via gh CLI
- **Impact:** security_scanner, code_reviewer, pr_curator need mcp__ wiring
- **Action:** Update agent code to use mcp__ instead of custom MCP

---

## Phase 2: Implement Blocking MCPs (⏳ PENDING)

### High Priority: Supabase MCP

**Problem:** 4 agents blocked (contract_tester, integration_tester, report_generator, etl_orchestrator)

**Options:**

#### Option A: Create Supabase MCP (Recommended)
```bash
~/.claude/mcp/supabase-server.js
```
- Wraps Supabase API + RLS validation
- Provides: execute_sql, apply_migrations, list_tables, read_table_data
- Effort: 2-3 hours
- Language: JavaScript/Node.js

**Implementation Steps:**
1. Create MCP wrapper for Supabase client
2. Implement tools: execute_sql, list_tables, read_table_data, apply_migrations
3. Handle RLS validation (critical for data integrity)
4. Add error handling + transaction support
5. Test with integration_tester agent

**Estimated Cost:**
- Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 0.5 hour
- **Total: ~4 hours**

#### Option B: Use CLI Wrapper
```bash
# Instead of custom MCP, wrap psql directly
psql $SUPABASE_URL -c "SELECT * FROM table"
```
- Faster: 30 minutes
- Pros: Simpler, no new dependencies
- Cons: Less ergonomic for agents, no transaction support
- Risk: Shell injection vulnerabilities

#### Option C: Skip for Now (Status Quo)
- Leave agents dormant
- Revisit in Phase 3 (Q2 2026)
- Impact: report_generator, etl_orchestrator can't run

**Recommendation:** Option A (create proper MCP)

---

### Medium Priority: Morph MCP

**Problem:** 2 agents blocked (code_reviewer, ssot_fixer)

**Options:**

#### Option A: Create Morph MCP
```bash
~/.claude/mcp/morph-server.js
```
- Wraps Morph API for code transformation
- Provides: apply_edits, suggest_changes, validate_syntax
- Effort: 1-2 hours
- Language: JavaScript/Node.js

**Implementation Steps:**
1. Create MCP wrapper for Morph client
2. Implement tools: apply_edits, suggest_changes, validate_syntax
3. Add error handling + dry-run support
4. Test with ssot_fixer agent

#### Option B: Replace with Native Edit Tool
```bash
# Instead of Morph MCP, use native Edit tool
Edit(file_path, old_string, new_string)
```
- Faster: Already available
- Pros: Simple, no external dependency
- Cons: Limited to string replacement (less powerful than Morph)
- Risk: Edge cases in large files

#### Option C: Skip for Now
- Leave agents dormant
- Revisit in Phase 3

**Recommendation:** Option B (replace with native Edit tool)
- Simpler implementation
- Covers 80% of use cases
- Fallback: Option A if native Edit proves insufficient

---

## Phase 2 Task List (Prioritized)

1. **MCP-001: Implement Supabase MCP** (HIGH)
   - Effort: 4 hours
   - Unlocks: contract_tester, integration_tester, report_generator, etl_orchestrator
   - Files: ~/.claude/mcp/supabase-server.js
   - Tests: evals/supabase_mcp.json
   - Acceptance: All 4 agents pass dry-run test

2. **MCP-002: Update Memory/GitHub agents** (MEDIUM)
   - Effort: 2 hours
   - Updates: living_laboratory, ambient_disseminator (memory)
   -          security_scanner, code_reviewer, pr_curator (github)
   - Changes: Agent code to use mcp__ instead of custom MCP
   - Tests: Each agent passes integration test

3. **MCP-003: Replace Morph with Edit** (MEDIUM)
   - Effort: 1 hour
   - Updates: code_reviewer, ssot_fixer
   - Changes: Agent code to use native Edit tool
   - Tests: SSOT violation detection + fix workflow

4. **MCP-004: Documentation** (LOW)
   - Effort: 1 hour
   - Updates: AGENTS.md, MCP_REMEDIATION_PLAN.md
   - Changes: Mark MCPs as "working" vs "todo"
   - Tests: None

---

## Current MCP Status Matrix

| MCP | Config | File | Status | Replacement | Effort |
|-----|--------|------|--------|-------------|--------|
| exa | ✓ | npx | ✅ WORKS | Native | — |
| sequential-thinking | ✗ | missing | 🔴 BROKEN | Native Claude | 0h |
| memory | ✗ | missing | 🔴 BROKEN | mcp__ | 1h |
| filesystem | ✗ | missing | 🔴 BROKEN | Native tools | 0h |
| github | ✗ | missing | 🔴 BROKEN | mcp__ | 1h |
| supabase | ✗ | missing | 🔴 BROKEN | Create MCP | 4h |
| morph | ✗ | missing | 🔴 BROKEN | Edit tool | 1h |
| egos-agents-mcp | ✗ | missing | ⏸️ DISABLED | Keep disabled | 0h |

---

## Timeline

| Phase | Tasks | Duration | Status |
|-------|-------|----------|--------|
| Phase 1 | Disable broken MCPs, document | ✅ 2h | COMPLETE |
| Phase 2 | Implement Supabase, update agents | ⏳ 8h | PENDING |
| Phase 3 | Consolidate kernel agents | — | Q2 2026 |

---

## Risk Assessment

### High Risk (if not addressed)
- **Supabase agents blocked** — report_generator, etl_orchestrator can't provide infrastructure insights
- **Test pyramid incomplete** — contract_tester, integration_tester not available

### Medium Risk
- **Code review incomplete** — code_reviewer, ssot_fixer need workarounds
- **Knowledge persistence** — living_laboratory, ambient_disseminator need mcp__ wiring

### Low Risk
- **Sequential thinking** — Works natively
- **Filesystem** — Native tools already available

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-27 | Disable all 6 broken MCPs | Never implemented, causing false "enabled" status |
| 2026-03-27 | Keep Exa MCP (npx version) | Official package available, already working |
| 2026-03-27 | Recommend Supabase MCP implementation | 4 agents blocked, critical for infrastructure orchestration |
| 2026-03-27 | Recommend Edit tool for Morph replacement | Simpler, covers 80% of use cases |

---

## Next Steps (Phase 2)

1. **Decide on implementation approach** (Supabase: MCP vs CLI)
2. **Assign ownership** (ideally someone familiar with Supabase + MCP protocols)
3. **Create backlog items** (with tests + acceptance criteria)
4. **Execute in order:** Supabase → Memory/GitHub → Morph → Docs

---

**Status:** Ready for Phase 2 execution
**Blocker:** Decision on Supabase implementation approach (MCP vs CLI)
**Maintainer:** EGOS Kernel Governance
