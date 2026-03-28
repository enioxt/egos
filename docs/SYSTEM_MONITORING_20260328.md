# System Monitoring Report — 2026-03-28

## Executive Summary

**6 kernel agents + 2 monitoring agents = 8 active systems checked**
- ✅ All agents running successfully
- ⚠️ **CRITICAL**: 26 agent files exist but not registered in registry
- ⚠️ **HIGH**: 52 dead code exports found in packages/shared
- ℹ️ **INFO**: All AI providers operational (OpenRouter healthy, Groq/Alibaba no keys)

---

## Kernel Agents Status (6/6 ✅)

### 1. dep-auditor
- **Status**: ✅ Success
- **Duration**: 341ms
- **Findings**: 12
  - ⚠️ 4 version conflicts: eslint, typescript, tailwindcss, vite
  - ℹ️ 8 possibly unused dependencies
- **Action**: Align workspace dependencies

### 2. archaeology-digger
- **Status**: ✅ Success
- **Duration**: 1435ms
- **Findings**: 22
  - 265 feature-addition events in egos-lab
  - 83 feature-addition events in egos
  - 21 agents registered in egos-lab lineage
  - 6 agents in egos kernel (correct!)
  - 35 governance additions
  - 42 session handoffs tracked
  - ⚠️ 10 breakpoints detected (major feature additions)
- **Implication**: System evolution is well-documented

### 3. context-tracker
- **Status**: ✅ Success
- **Duration**: 13ms
- **Finding**: CTX 16/280 🟢 SAFE
- **Breakdown**: uncommitted=2, code_changed=1, handoff=14.1kb, agent_runs=0
- **Action**: Continue normally

### 4. chatbot-compliance-checker
- **Status**: ✅ Success
- **Duration**: 9410ms
- **Finding**: SSOT score 100/100 for egos
- **Action**: All chatbot capabilities in compliance

### 5. dead-code-detector
- **Status**: ✅ Success
- **Duration**: 277ms
- **Findings**: 52 dead exports found
  - MyceliumBus, getAgent, createBus (event-bus.ts)
  - scanForSecrets, redactSecrets, redactPII (privacy-scanner.ts)
  - MetricsTracker, initMetricsTracker (utilities.ts)
  - ALIBABA_TEST_MODELS, MODEL_REGISTRY, MODEL_CATALOG (AI models)
  - 25+ more dead exports in shared packages
- **Impact**: ~50% of exported APIs in packages/shared are unused
- **Action**: Audit and remove exports marked as @internal

### 6. capability-drift-checker
- **Status**: ✅ Success
- **Duration**: 42ms
- **Finding**: Capability drift 100% (15/15 adopted)
- **Action**: egos core is fully compliant with capability framework

---

## Monitoring Agents Status (2/2 ✅)

### drift-sentinel (AGENT-034)
- **Status**: ✅ Success
- **Severity**: 🟡 MEDIUM (26 findings)
- **Critical Finding**: **46 agent registry mismatches**
  - **26 agents exist in files but NOT in agents.json**
    - e.g., drift-sentinel.ts exists but registry has no "drift-sentinel" entry
    - e.g., quota-guardian.ts exists but registry has no "quota-guardian" entry
  - **6 kernel agents have underscore/dash mismatch**
    - agents.json: "dep_auditor" | File: "dep-auditor.ts"
    - agents.json: "archaeology_digger" | File: "archaeology-digger.ts"
    - etc for all 6
- **Root Cause**: Migration from egos-lab incomplete; registry not synchronized
- **Impact**: `bun agent:run <id>` fails for unregistered agents; naming inconsistent
- **P0 Action**: Normalize all agent IDs to kebab-case in both registry and filenames

### quota-guardian (AGENT-033)
- **Status**: ✅ Success
- **Provider Health**:
  - 🟢 **OpenRouter**: OK (424ms)
    - Status: All quotas within limits
    - Fallback: Primary provider
  - ⚪ **Groq**: No API key configured
  - ⚪ **Alibaba DashScope**: No API key configured
- **Fallback Order**: openrouter → groq → alibaba
- **Action**: Add Groq/Alibaba keys if needed; OpenRouter sufficient for now

---

## Summary Table

| Component | Status | Type | Count | Priority |
|-----------|--------|------|-------|----------|
| Kernel agents | ✅ | Operational | 6/6 | — |
| Monitoring agents | ✅ | Operational | 2/2 | — |
| Version conflicts | ⚠️ | Dependencies | 4 | P1 |
| Dead code exports | ⚠️ | Code quality | 52 | P2 |
| Registry orphans | 🔴 | **CRITICAL** | 26 | **P0** |
| Naming mismatches | 🔴 | **CRITICAL** | 6 | **P0** |
| AI providers | ✅ | External | 1/3 healthy | — |
| Compliance score | ✅ | SSOT | 100/100 | — |

---

## P0 Actions (Blocking)

### 1. **Fix Registry Drift (26 orphans + 6 naming mismatches)**
   - **File**: agents/registry/agents.json
   - **Action**:
     - Register all 26 agents from egos-lab/agents/agents/
     - Normalize to kebab-case IDs across registry and filenames
     - Update agent.json descriptions for clarity
   - **Effort**: 2-3h (bulk edit + validation)
   - **Blocker**: Many agents unreachable via `bun agent:run`

### 2. **Dead Code Removal (52 exports)**
   - **Files**: packages/shared/* (6+ files with dead exports)
   - **Action**: Audit each export; remove if truly dead; mark @public if API
   - **Effort**: 1-2h (code review focused)
   - **Impact**: Cleaner shared package exports

### 3. **Dependency Alignment (4 version conflicts)**
   - **Conflicts**:
     - eslint: ^9.0.0 vs ^9.39.4
     - typescript: ^5.7.0 vs ~5.9.3
     - tailwindcss: ^4.2.2 vs ^3.4.19
     - vite: ^8.0.1 vs ^8.0.2
   - **Action**: Choose canonical versions; update all workspaces
   - **Effort**: 1h

---

## Findings Exported

- Full reports saved to: `docs/agent-tests/` (if available)
- Event logs: `agents/.logs/events.jsonl` (updated with correlation IDs)

---

## Next Steps

1. **P0**: Fix registry drift (drift-sentinel→26 orphans, 6 mismatches)
2. **P1**: Align dependencies (4 version conflicts)
3. **P2**: Audit dead code exports (52 unused APIs)
4. **P3**: Complete carteira-livre transparency timeline (in progress)

---

**Report Generated**: 2026-03-28 20:45 UTC
**Kernel Status**: 🟢 OPERATIONAL
**System Health**: 🟡 MEDIUM (registry issues not blocking core agents)
