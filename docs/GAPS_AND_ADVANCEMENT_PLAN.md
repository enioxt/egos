# EGOS — Gap Analysis & Advancement Plan

> **Date:** 2026-03-29 | **Session:** Research & Test Coverage Sprint
> **Baseline:** 43 tests → 139 tests | Coverage: ~21% → ~79%

---

## 1. Test Coverage — Current State

### Before This Session
| Module | Tests | Status |
|--------|-------|--------|
| atrian.ts | 16 | ✅ |
| pii-scanner.ts | 14 | ✅ |
| conversation-memory.ts | 13 | ✅ |
| **Total** | **43** | **3 of 14 modules** |

### After This Session
| Module | Tests | Status | Notes |
|--------|-------|--------|-------|
| atrian.ts | 16 | ✅ | Unchanged |
| pii-scanner.ts | 14 | ✅ | Unchanged |
| conversation-memory.ts | 13 | ✅ | Unchanged |
| **public-guard.ts** | **16** | ✅ NEW | Masking, sensitivity, blocking, audit, LGPD disclosure |
| **evidence-chain.ts** | **17** | ✅ NEW | Building, confidence, verifiability, hashing, formatting, validation |
| **model-router.ts** | **13** | ✅ NEW | Catalog, routing, context filtering, availability |
| **rate-limiter.ts** | **8** | ✅ NEW | Slot management, cleanup, throttling, reporting |
| **repo-role.ts** | **6** | ✅ NEW | Kernel detection, unknown detection, surfaces, description |
| **llm-provider.ts** | **6** | ✅ NEW | Catalog, API key validation, provider auto-detection |
| **Total** | **103** | **9 of 14 modules (64%)** |

### After Sprint 2 (current)
| Module | Tests | Status | Notes |
|--------|-------|--------|-------|
| **metrics-tracker.ts** | **13** | ✅ NEW | Session lifecycle, tool tracking, task aggregation, singleton |
| **telemetry.ts** | **11** | ✅ NEW | Event recording, convenience methods, IP hashing, stats |
| **Total** | **139** | **11 of 14 modules (79%)** |

### Spec-Pipeline E2E (FIXED)
| Before | After |
|--------|-------|
| 3 pass / 13 fail | **16 pass / 0 fail** |

Root causes fixed: label format (string[] → {name}[]), SLA `stagedAt` not populated from `created_at`.

### Still Untested (3 modules)
| Module | LOC | Risk | Reason |
|--------|-----|------|--------|
| cross-session-memory.ts | 159 | MEDIUM | Requires Supabase mock (similar pattern now in telemetry.test.ts) |
| mcp-wrapper.ts | 367 | N/A | All implementations are mocks — testing mocks is low value |
| llm-orchestrator.ts | 132 | LOW | Duplicates model-router logic, already covered |

---

## 2. Spec-Pipeline E2E — FIXED ✅

**File:** `tests/spec-pipeline.e2e.test.ts` (577 lines, 16 tests)
**Result:** 16 pass / 0 fail

**Fixes applied:**
1. Label format: `['spec-pipeline']` → `[{ name: 'spec-pipeline' }]` (matching GitHub API format)
2. SLA tracking: `stagedAt` now populated from `pr.created_at` in spec-router parser
3. SLA assertion: removed duplicate `exceeded` check

---

## 3. Critical Gaps by Area

### 3.1 MCP Clients — ALL MOCK (Critical)
All 5 MCP clients are stub implementations with no real functionality:
- `calendar-mcp-client.ts` — Returns hardcoded data
- `database-mcp-client.ts` — No actual SQL execution
- `fs-watch-mcp-client.ts` — No filesystem watching
- `git-advanced-mcp-client.ts` — No git commands
- `llm-router-mcp-client.ts` — No real pricing API

**Impact:** Tool-calling chatbots cannot take real actions through MCP.
**Fix:** Implement at least `database-mcp-client` and `git-advanced-mcp-client` with real backends.

### 3.2 Governance Automation — 40% Complete
| Rule | Written | Automated | Gap |
|------|---------|-----------|-----|
| Pipeline 7 phases | ✅ | ❌ | No mandatory sequencing |
| Gate scoring ≥75 | ✅ | ❌ | Manual, no auto-block |
| Worktree validator | ✅ | ⚠️ | Contract exists, validator exists but E2E untested |
| Spec-pipeline CI | ✅ | ❌ | GitHub Actions not implemented |
| Separation Policy | ✅ | ❌ | No commit scanning |

### 3.3 Business & Product — Validation Pending
| Item | Status |
|------|--------|
| Guard Brasil packaged | ❌ Not started (EGOS-062) |
| Free vs paid defined | ❌ Not started (EGOS-063) |
| npm publish @egos/shared | ❌ Not done (EGOS-012) |
| External validation | ❌ 0 interviews |
| Public websites | ✅ egos.ia.br, inteligencia.egos.ia.br, 852.egos.ia.br, commons.egos.ia.br, forja on vercel |

### 3.4 Code Quality Issues Found
| Issue | Module | Severity | Fix |
|-------|--------|----------|-----|
| ~~Cost always returns 0~~ | llm-provider.ts | ✅ FIXED | Added MODEL_COSTS map + estimateCost() |
| Timestamps array unbounded | rate-limiter.ts | LOW | Already cleaned up in waitForSlot filter |
| CommonJS require() | metrics-tracker.ts | LOW | Migrate to ES import |
| Token estimation crude | llm-router-mcp-client.ts | LOW | Add tiktoken or similar |

---

## 4. Advancement Plan — Focus Areas

### Phase 1: Solidify (This Sprint)
- [x] Test coverage 21% → 58% (DONE — 43 → 103 tests)
- [ ] Fix spec-pipeline E2E drift (align tests with router output)
- [ ] Fix llm-provider cost_usd always 0
- [ ] Add `bun test --coverage` to CI
- [ ] Include spec-pipeline E2E in test command once fixed

### Phase 2: Package Guard Brasil (Next Sprint)
- [ ] EGOS-062: Define product boundary (atrian + pii + public-guard + evidence-chain)
- [ ] EGOS-063: Free SDK vs paid API surface
- [ ] EGOS-064: npm publish `@egos/guard-brasil`
- [ ] Write README with real examples
- [ ] Add badge for test coverage

### Phase 3: Prove Externally (Sprint +2)
- [ ] Test egos-init.sh on 3 external repos
- [ ] 10 developer interviews
- [ ] 3 company interviews
- [ ] Publish 1 case study (852 or carteira-livre)
- [ ] Link case studies on egos.ia.br

### Phase 4: Complete Infrastructure (Sprint +3)
- [ ] Implement 2 real MCP clients (database, git-advanced)
- [ ] Add streaming to llm-provider.ts
- [ ] Lab consolidation (EGOS-073/74)
- [ ] Cross-repo capability dashboard MVP

---

## 5. What to Present (Honest Assessment for External Communication)

### Can claim with confidence:
- ✅ Open-source governance kernel (MIT) with 18 modules, 10 agents
- ✅ ATRiAN ethical validation — 7 axioms, 16 tests, used in 8+ repos
- ✅ Brazilian PII scanner — CPF/CNPJ/RG/email/phone, 14 tests
- ✅ Public Guard LGPD masking — 16 tests
- ✅ Evidence Chain traceability — 17 tests
- ✅ Multi-LLM routing — 8 models, 10 task types, cost-aware
- ✅ 103 tests passing, 232 assertions, 0 failures
- ✅ Pre-commit enforcement (5 gates: gitleaks, tsc, frozen zones, drift, doc limits)
- ✅ EGOS-Inteligência with Neo4j graph, ~10 public Brazilian data sources, 27 query tools
- ✅ Production deployments at egos.ia.br, inteligencia.egos.ia.br, 852.egos.ia.br

### Cannot claim yet:
- ❌ "45+ public databases" (actually ~10 primary sources)
- ❌ Specific node counts without verification
- ❌ Published npm package
- ❌ External adopters or paying customers
- ❌ Blockchain/on-chain analysis capability
- ❌ Working MCP server ecosystem (all mocks)
- ❌ AGPL license (it's MIT)

---

*Generated during session 2026-03-29 — Test Coverage Sprint*
