# Cherry-Pick Inventory — EGOS Framework Core

> **Created:** 2026-03-13 | **Source:** Deep scan of 15 directories

## Scan Coverage

| Directory | Status | Key Findings |
|-----------|--------|-------------|
| `~/.egos` | Scanned | Governance home, refinery source of truth |
| `egos-lab` | Deep scan | Primary source for .guarani/, tools, workflows |
| `egos-archive/v2` | Scanned | ETHIK token algo, STRATEGY (product vision) |
| `egos-archive/v4` | Scanned | Cortex architecture, code-health-monitor |
| `egos-archive/v5` | Scanned | Engineering Standards 2026, refinery origin |
| `852` | Scanned | Clean governance, chatbot-hardening workflow |
| `br-acc` | Scanned | Report standards, gov database map |
| `carteira-livre` | Scanned | Design standards, valuation, rich workflows |
| `forja` | Scanned | WhatsApp agent arch, email pipeline |
| `policia` | Scanned | Minimal governance bootstrap |
| `egos-self` | Scanned | Git Layer Architecture (decentralization) |
| `INPI` | Scanned | Governed leaf (EGOS v3 framework) |
| `BrandForge` | Scanned | Multi-agent orchestration, metaprompts |
| `INTELINK` | Scanned | Legacy investigation platform |
| `EGOSv2` | Scanned | Stub only (28K) |
| `clipmon` | Scanned | Small clipboard tool, no governance |
| `personal` | Scanned | CVs only, no code |

## Files Cherry-Picked to egos/ (this session)

### .guarani/ — Governance Layer
| File | Source | Lines | Why |
|------|--------|-------|-----|
| `refinery/classifier.md` | egos-lab | 268 | Intent classification (core) |
| `refinery/interrogators/bug.md` | egos-lab | 169 | Bug investigation protocol |
| `refinery/interrogators/feature.md` | egos-lab | 140 | Feature refinement protocol |
| `refinery/interrogators/refactor.md` | egos-lab | 158 | Refactor assessment protocol |
| `refinery/interrogators/knowledge.md` | egos-lab | 145 | Knowledge query protocol |
| `refinery/compiler.md` | egos-lab | 267 | Intent→action compiler |
| `refinery/vocabulary_learner.md` | egos-lab | 222 | User vocabulary learning |
| `refinery/README.md` | egos-lab | 120 | Refinery system overview |
| `preprocessor.md` | egos-lab | 222 | Vague→explicit transformer |
| `SEPARATION_POLICY.md` | egos-lab | 114 | Repo visibility + channel rules |
| `ENGINEERING_STANDARDS_2026.md` | egos-archive/v5 | 62 | Vibe coding + agentic standards |
| `security/SEC-001_PHONE_BRIDGE.md` | egos-lab | 49 | Phone-as-2FA policy |
| `security/SEC-002_VPS_HARDENING.md` | egos-lab | 43 | VPS hardening policy |
| `standards/MCP_TOOL_QUALITY_FRAMEWORK.md` | egos-lab | 280 | MCP quality audit |
| `tools/code-health-monitor.ts` | egos-lab | 260 | Codebase health scorer |
| `tools/privacy-scanner.ts` | egos-lab | 117 | PII/secret scanner |
| `prompts/meta/mycelium-orchestrator.md` | egos-lab | 80 | Cross-repo sync prompt |

### .windsurf/workflows/ — Core Workflow Set
| File | Source | Why |
|------|--------|-----|
| `start.md` | egos-lab | Session initialization |
| `end.md` | egos-lab | Session finalization |
| `pre.md` | egos-lab | Instruction preprocessor |
| `prompt.md` | egos-lab | Prompt engineering |
| `regras.md` | egos-lab | Governance rule collector |
| `research.md` | egos-lab | Research protocol |
| `disseminate.md` | egos-lab | Knowledge dissemination |

### docs/concepts/ — Reference Architecture
| File | Source | Why |
|------|--------|-----|
| `ETHIK_TOKEN_SYSTEM.md` | egos-archive/v2 | Proportional token distribution |
| `CORTEX_ARCHITECTURE.md` | egos-archive/v4 | Knowledge system design |
| `GIT_LAYER_ARCHITECTURE.md` | egos-self | Decentralized identity layer |
| `ESPIRAIS_VISION.md` | egos-archive/v2 | Product vision (Listening Spirals) |

## Deliberately Excluded

| File | Reason |
|------|--------|
| `nexus/debate_mode.md` | Domain-specific to egos-lab Nexus |
| `ACTIVATION_PAYLOAD.md` | egos-lab specific activation |
| `ARCHAEOLOGY_INVENTORY.md` | Historical, egos-lab specific |
| `CORE_WHITELIST.json` | egos-lab specific |
| `SYSTEM_INDEX.md` | egos-lab specific |
| `DESIGN_STANDARDS.md` | Intelink-specific palette |
| `MCP_ORCHESTRATION_GUIDE.md` | Too long (335 lines), IDE-specific |
| Domain-specific workflows | carteira-livre db-snapshot, etc. |
