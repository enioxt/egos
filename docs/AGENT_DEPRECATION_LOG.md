# AGENT DEPRECATION LOG

> **Last Updated:** 2026-03-27 | **Audit Period:** Cleanup Phase 1

---

## Summary

Governance audit identified fragile agent & MCP configuration with:
- 2 duplicate agents across kernel & lab registries
- 3 non-functional agents in "pending" status
- 6 custom MCP server implementations that were never created
- 4 agents blocked by missing MCPs

**Action Taken:** Cleanup Phase 1 executed on 2026-03-27

---

## Removed Agents (Duplicates)

### 1. `dep_auditor` (duplicate)
- **Location:** egos-lab/agents/registry/agents.json
- **Reason:** Already exists in egos kernel registry as SSOT
- **Status:** REMOVED from lab registry (2026-03-27)
- **Impact:** None — kernel version is authoritative
- **Commit:** chore(agents): remove duplicate dep_auditor from egos-lab

### 2. `dead_code_detector` (duplicate)
- **Location:** egos-lab/agents/registry/agents.json
- **Reason:** Already exists in egos kernel registry as SSOT
- **Status:** REMOVED from lab registry (2026-03-27)
- **Impact:** None — kernel version is authoritative
- **Commit:** chore(agents): remove duplicate dead_code_detector from egos-lab

---

## Dormant Agents (Status Changed to dormant)

### 1. `e2e_smoke` (E2E Smoke Validator)
- **Area:** QA | **Risk:** T1 | **Status:** pending → **dormant** (2026-03-27)
- **Reason:** Never tested, Playwright integration incomplete, no active trigger schedule
- **Used By:** None (no agent depends on this)
- **When to Re-enable:**
  - When e2e test infrastructure is established
  - When Playwright integration is validated
  - Estimated: 2026-Q2
- **Location:** egos-lab/agents/registry/agents.json
- **Commit:** chore(agents): mark e2e_smoke as dormant (tech debt)

### 2. `social_media_agent` (Social Media Automation)
- **Area:** Knowledge | **Risk:** T3 | **Status:** pending → **dormant** (2026-03-27)
- **Reason:** Requires active social media strategy + scheduling, not operational
- **Used By:** None (no agent depends on this)
- **When to Re-enable:**
  - When social media content calendar is defined
  - When Telegram/Instagram/Twitter/X integrations are finalized
  - Estimated: 2026-Q3
- **Location:** egos-lab/agents/registry/agents.json
- **Commit:** chore(agents): mark social_media_agent as dormant (not operational)

### 3. `ghost_hunter` (??? unnamed discovery agent)
- **Area:** Discovery | **Risk:** T0 | **Status:** dormant (already)
- **Reason:** Mystical placeholder agent, no implementation
- **Used By:** None (no agent depends on this)
- **Notes:**
  - Awaiting activation by "first three discoverers" (rho-calibration protocol)
  - This is intentional design pattern — skip
- **Location:** egos-lab/agents/registry/agents.json
- **Status:** NO CHANGE (already dormant)

---

## Broken MCPs (Configuration Only)

Custom MCP servers were configured but never implemented. Status changed to `enabled: false` with deprecation notes.

### 1. `sequential-thinking-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/sequential-thinking-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** context_tracker, security_scanner, atrian_agent
- **Replacement:** Use native Claude Code sequential thinking feature
- **Config:** ~/.claude/config/mcp-servers.json (disabled)

### 2. `memory-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/memory-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** living_laboratory, ambient_disseminator
- **Replacement:** Use native `mcp__memory__*` functions (create_entities, create_relations, etc)
- **Config:** ~/.claude/config/mcp-servers.json (disabled)

### 3. `filesystem-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/filesystem-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** all_agents (used by all)
- **Replacement:** Use native Claude Code tools: Read, Write, Edit, Glob, Grep
- **Config:** ~/.claude/config/mcp-servers.json (disabled)

### 4. `github-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/github-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** security_scanner, code_reviewer, pr_curator
- **Replacement:** Use native `mcp__*` functions via gh CLI
- **Config:** ~/.claude/config/mcp-servers.json (disabled)

### 5. `supabase-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/supabase-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** contract_tester, integration_tester, report_generator, etl_orchestrator
- **Replacement:** Implement custom Supabase integration or use psql CLI
- **Priority:** HIGH (blocks 4 agents)
- **Config:** ~/.claude/config/mcp-servers.json (disabled)
- **Estimated Effort:** 2-3 hours implementation

### 6. `morph-server.js` (File: ~MISSING~)
- **Expected Location:** ~/.claude/mcp/morph-server.js
- **Status:** DISABLED (2026-03-27)
- **Affected Agents:** code_reviewer, ssot_fixer
- **Replacement:** Use native Edit tool for code transformations
- **Priority:** MEDIUM (blocks 2 agents)
- **Config:** ~/.claude/config/mcp-servers.json (disabled)
- **Estimated Effort:** 1-2 hours implementation or replacement

### 7. `egos-agents-mcp` (Custom orchestrator)
- **Expected Location:** /home/enio/egos/mcp/server.ts
- **Status:** DISABLED (already, marked as TODO_PHASE_4)
- **Affected Agents:** orchestrator
- **Replacement:** Keep using direct agent:run commands via Bash
- **Priority:** LOW (Phase 4 deliverable)
- **Config:** ~/.claude/config/mcp-servers.json (disabled)

---

## Agent Dependency Map (Broken MCPs)

```
High Priority (blocks critical agents):
├─ supabase-server.js → contract_tester ❌
├─ supabase-server.js → integration_tester ❌
├─ supabase-server.js → report_generator ❌
├─ supabase-server.js → etl_orchestrator ❌
│
├─ morph-server.js → code_reviewer ❌
└─ morph-server.js → ssot_fixer ❌

Medium Priority:
├─ sequential-thinking → context_tracker ✓ (can use native)
├─ memory → living_laboratory ✓ (can use mcp__memory__)
└─ memory → ambient_disseminator ✓ (can use mcp__memory__)

Low Priority:
└─ github-server.js → pr_curator ✓ (can use mcp__)
```

---

## Registry Changes

### Before (2026-03-27 09:00 UTC)
- **Kernel agents:** 6
- **Lab agents:** 30 (including 2 duplicates)
- **Total:** 36 (34 unique)
- **MCPs enabled:** 7/7 (0 working)
- **Agents in pending/dormant:** 3

### After (2026-03-27 10:30 UTC)
- **Kernel agents:** 6 (unchanged)
- **Lab agents:** 28 (removed 2 duplicates)
- **Total:** 34 agents
- **MCPs enabled:** 1/7 (exa only)
- **MCPs disabled:** 6/7 (with deprecation notes)
- **Agents in dormant:** 3 (e2e_smoke, social_media_agent, ghost_hunter)

---

## Recommendations

### Phase 2: Consolidation (Optional)
- [ ] Move `orchestrator` to kernel (used in all sessions)
- [ ] Move `security_scanner_v2` to kernel (run on every activation)
- [ ] Move `report_generator` to kernel (status dashboard dependency)

### Phase 3: Re-enable MCPs (Priority Order)
1. **Supabase MCP** (HIGH) — Blocks 4 agents, 2-3 hours
2. **Morph MCP** (MEDIUM) — Blocks 2 agents, 1-2 hours
3. **Exa Native** (DONE) — Already functional
4. **GitHub CLI** (LOW) — Working via native mcp__
5. **Custom Orchestrator** (LOW) — Phase 4, non-critical

### Phase 4: Post-Audit
- [ ] Update AGENTS.md with new agent counts (34 vs old "30+")
- [ ] Update TASKS.md with broken MCP resolution tasks
- [ ] Document agent dependency graph in docs/
- [ ] Establish agent lifecycle policy (dormant → removal after 6 months)

---

## Audit Trail

| Date | Action | Files | Status |
|------|--------|-------|--------|
| 2026-03-27 | Remove duplicates (dep_auditor, dead_code_detector) | egos-lab/agents/registry/agents.json | ✅ Done |
| 2026-03-27 | Mark e2e_smoke as dormant | egos-lab/agents/registry/agents.json | ✅ Done |
| 2026-03-27 | Mark social_media_agent as dormant | egos-lab/agents/registry/agents.json | ✅ Done |
| 2026-03-27 | Disable 6 broken MCPs | ~/.claude/config/mcp-servers.json | ✅ Done |
| 2026-03-27 | Create deprecation log | docs/AGENT_DEPRECATION_LOG.md | ✅ Done |
| TBD | Update AGENTS.md documentation | /home/enio/egos/AGENTS.md | ⏳ Pending |
| TBD | Update TASKS.md with MCP fixes | /home/enio/egos/TASKS.md | ⏳ Pending |

---

**Signed:** Claude Code Governance Audit
**Kernel:** /home/enio/egos
**Version:** 1.2.0
