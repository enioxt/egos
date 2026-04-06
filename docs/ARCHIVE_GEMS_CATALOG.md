# ARCHIVE GEMS CATALOG — Valuable Concepts for Modern Kernel

> **Date:** 2026-04-06  
> **Analyst:** Cascade  
> **Scope:** Deep Investigation of /home/enio/egos-archive (v2-v5)  
> **Status:** INVESTIGATION COMPLETE — Partial decisions recorded, remaining gems still under evaluation
> **Type:** FIXO — Catálogo permanente do archive

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Catalog of valuable legacy code/concepts from egos-archive v2-v5
- **Summary:** 20 gems cataloged; Self-Discovery and Booking Agent already decided, remaining items still await PORT/STUDY/ARCHIVE decisions
- **Type:** FIXO — Permanent reference catalog
- **Read next:**
  - `MASTER_INDEX.md` — scope everything
  - `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — current decisions status
  - `docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md` — integration recommendations
- **Archive when:** NEVER — Keep as historical catalog

<!-- llmrefs:end -->

---

## ⚠️ IMPORTANT NOTICE

This document catalogs **ALL** discovered items from egos-archive **before** any archive decisions.  
**Confirmed decisions are now recorded inline where they already exist.**  
Remaining items stay presented with enough context for future PORT/STUDY/ARCHIVE decisions.

---

## 🏆 DISCOVERED GEMS (Require User Decision)

### 1. SACRED MATHEMATICS SYSTEM (v2/core/sacred_math.py)

**What it is:**
- Golden Ratio (φ=1.618033988749895) calculations
- PHI_INVERSE (0.618) for optimization
- Quantum compression (37% target)
- Proportion calculation (major/minor splits)

**Lines of code:** 304  
**Language:** Python  
**Current status:** Legacy but functional  

**Potential value:**
- ✅ Optimization algorithms (port to TypeScript)
- ✅ Aesthetic proportion calculations
- ✅ Data compression heuristics
- ⚠️ "Sacred" terminology needs sanitization

**User decision needed:** PORT or ARCHIVE?

---

### 2. EVENT BUS SYSTEM (v2/core/intelligence/event_bus.py)

**What it is:**
- Event-driven architecture (neurotransmitter analogy)
- 8 event types (F₈ sacred math)
- Async/await implementation
- Subscriber/publisher pattern

**Lines of code:** 505  
**Language:** Python  
**Dependencies:** asyncio, dataclasses

**Potential value:**
- ✅ Pattern for Mycelium event system
- ✅ Event taxonomy (KNOWLEDGE_ABSORBED, SYNAPSE_FIRED, etc.)
- ✅ Priority levels (F₅ = 5 levels)
- ⚠️ Biological metaphors need sanitization

**User decision needed:** PORT CONCEPTS or ARCHIVE?

---

### 3. KNOWLEDGE GRAPH (v2/core/intelligence/knowledge_graph.py)

**What it is:**
- Graph database for concept relationships
- 8 relation types (F₈ = 8)
- Node/edge structure
- Path traversal algorithms

**Lines of code:** 538  
**Language:** Python  

**Potential value:**
- ✅ Relationship taxonomy for BRACC Neo4j
- ✅ Graph traversal patterns
- ✅ Relation types: DEPENDS_ON, ENHANCES, VALIDATES, DISSEMINATES, etc.
- ⚠️ Biological metaphors need sanitization

**User decision needed:** PORT TO BRACC or ARCHIVE?

---

### 4. LINT INTELLIGENCE (v2/core/lint/)

**What it is:**
- `egos_lint_validator.py` (15,603 bytes)
- `ethik_lint_adapter.py` (7,249 bytes)
- `egos_lint.toml` configuration
- ATRiAN integration for code ethics

**Potential value:**
- ✅ Code quality + ethical validation combined
- ✅ Integration with Ruff + ESLint
- ✅ Pre-commit hooks with ethics
- ⚠️ Needs modernization for TypeScript era

**User decision needed:** STUDY PATTERNS or ARCHIVE?

---

### 5. TALMUDIC VALIDATION (v2/core/validators/talmudic_validation.py)

**What it is:**
- Counter-argument evaluation system
- Stress test framework
- Cross-domain analogies
- Decision brief generator

**Lines of code:** 180  

**Potential value:**
- ✅ Decision-making framework
- ✅ Risk assessment methodology
- ✅ Go/pivot/stop decision rules
- ⚠️ "Talmudic" terminology needs discussion

**User decision needed:** PORT or ARCHIVE?

---

### 6. AGENT ACTIVATION PROTOCOL (v2/core/agents/activation_protocol.py)

**What it is:**
- 5-step activation flow
- Identity verification
- Memory hash check
- Git delta loading
- Framework docs loading

**Lines of code:** 130  

**Potential value:**
- ✅ Agent context loading pattern
- ✅ Cache invalidation strategy
- ✅ Framework state hydration
- ✅ Similar to modern /start workflow

**User decision needed:** COMPARE TO v6 or ARCHIVE?

---

### 7. QUANTUM BACKUP SYSTEM (v2/scripts/quantum-aggregate-backup.sh)

**What it is:**
- Golden Ratio-based data selection
- 37% compression target
- SQLite deduplication index
- Tiered backup (Critical/Important/Useful)

**Lines of code:** 654  

**Potential value:**
- ✅ Backup strategy with sacred_math
- ✅ Deduplication methodology
- ✅ Tiered backup concept
- ⚠️ "Quantum" is metaphor, not quantum computing

**User decision needed:** PORT CONCEPTS or ARCHIVE?

---

### 8. FASTCHECK SYSTEM (v2/scripts/fastcheck.js)

**What it is:**
- Aggregates type-check, lint, AutoHeal
- JSON report generation
- Incremental TypeScript cache
- Golden Ratio optimization (φ=1.618)

**Lines of code:** 629  
**Language:** Node.js

**Potential value:**
- ✅ Pre-commit quality gate
- ✅ Incremental caching strategy
- ✅ CI/CD integration pattern
- ✅ TypeScript compilation optimization

**User decision needed:** PORT TO v6 or ARCHIVE?

---

### 9. PM2 MANAGER (v2/scripts/pm2-manager.js)

**What it is:**
- PM2 process manager wrapper
- Circuit breaker pattern
- Telegram notifications
- Service health tracking

**Lines of code:** 400  
**Language:** Node.js

**Potential value:**
- ✅ Process management patterns
- ✅ Circuit breaker implementation
- ✅ Notification system design
- ⚠️ PM2 replaced by Docker in modern EGOS

**User decision needed:** STUDY PATTERNS or ARCHIVE?

---

### 10. HEALTH MONITOR (v2/scripts/health-monitor.js)

**What it is:**
- Service monitoring with circuit breaker
- Memory/CPU thresholds
- Restart tracking
- Telegram alerts

**Lines of code:** 349  
**Language:** Node.js

**Potential value:**
- ✅ Similar to modern watchdog.sh
- ✅ Health check methodology
- ✅ Circuit breaker pattern
- ✅ Threshold-based alerting

**User decision needed:** COMPARE TO v6 watchdog or ARCHIVE?

---

### 11. TELEGRAM NOTIFIER (v2/scripts/telegram-notifier.js)

**What it is:**
- Telegram Bot API wrapper
- .env.local configuration
- Markdown support
- Async message sending

**Lines of code:** 155  
**Language:** Node.js

**Potential value:**
- ✅ Notification system pattern
- ✅ Bot API integration
- ✅ Async error handling
- ⚠️ Similar to modern Telegram notifications

**User decision needed:** COMPARE TO v6 or ARCHIVE?

---

### 12. MYCELIUM GENERATOR (v2/scripts/mycelium/generate_integration.py)

**What it is:**
- Auto-generates integration code from YAML
- Jinja2 templating
- Module configuration validation
- Code generation pipeline

**Lines of code:** 352  
**Language:** Python

**Potential value:**
- ✅ Code generation pattern
- ✅ YAML-driven development
- ✅ Template-based scaffolding
- ⚠️ Related to modern Mycelium concepts

**User decision needed:** STUDY or ARCHIVE?

---

### 13. MCP HUB (v2/apps/mcp-hub/)

**What it is:**
- Unified MCP Server (port 8112)
- Code intelligence tools
- Image generation tools
- EGOS APIs integration
- Context playbook tools

**Files:**
- `server.py` (24,231 bytes)
- `code_intel_tools.py` (7,850 bytes)
- `image_generation_tools.py` (8,741 bytes)
- `egos_apis_mcp.py` (8,528 bytes)

**Potential value:**
- ✅ MCP tool patterns
- ✅ Code intelligence implementation
- ✅ Multi-tool aggregation
- ⚠️ Superseded by modern MCP architecture

**User decision needed:** STUDY PATTERNS or ARCHIVE?

---

### 14. BOOKING AGENT (v2/apps/booking-agent/)

**What it is:**
- Complete booking automation system
- Multi-tenant architecture
- React frontend
- Supabase backend
- Documentation-heavy (15+ docs)

**Size:** 208,705 bytes (compressed)  
**Language:** TypeScript/React/Python

**Potential value:**
- ✅ Productized agent example
- ✅ Multi-tenant patterns
- ✅ Frontend/backend integration
- ⚠️ Specific to booking use case
- ⚠️ May be product, not framework

**Status:** ✅ **DECIDIDO — ARQUIVAR (2026-04-06)**
- **Rationale:** Mercado saturado (Calendly, Square), diferença competitiva não clara
- **Action:** Manter em archive v2. Pattern detection pode ser extraído para Forja CRM futuro.
- **Container:** NÃO criar. Foco no Guard Brasil e Self-Discovery.

---

### 15. ETHIK DISTRIBUTION SYSTEM (v2/ETHIK_DISTRIBUTION_SYSTEM.md)

**What it is:**
- Token distribution algorithm
- Proportional to point growth
- Fibonacci periods (F₇=13, F₈=21 days)
- Anti-inflation mechanisms

**Lines:** 629  

**Potential value:**
- ✅ Gamification patterns
- ✅ Point systems
- ✅ Distribution algorithms
- ⚠️ Blockchain/token focus abandoned
- ⚠️ Philosophical/financial complexity

**User decision needed:** ARCHIVE or EXTRACT PATTERNS?

---

### 16. CODE ARCHAEOLOGY CATALOG (v2/CODE_ARCHAEOLOGY_CATALOG.json)

**What it is:**
- Complete module analysis
- Git history per module
- Function/class extraction
- External reference tracking (68 refs to lint)

**Lines:** 1,348  
**Format:** JSON

**Potential value:**
- ✅ Migration methodology
- ✅ Code analysis patterns
- ✅ Historical documentation
- ✅ Reference tracking

**User decision needed:** KEEP AS TEMPLATE or ARCHIVE?

---

### 17. SELF-DISCOVERY SYSTEM (v2/docs/SELF_DISCOVERY_TEST.md)

**What it is:**
- Pattern detection for psychology
- Maieutic (Socratic) questioning
- Interface for self-reflection
- API endpoints for pattern detection

**Potential value:**
- ✅ Therapeutic AI application
- ✅ Pattern detection methodology
- ✅ Question generation algorithms
- ⚠️ Specific use case (therapy)

**Status:** ✅ **DECIDIDO — PRODUTIZAR (2026-04-06)**
- **Porta:** 3098 (nova porta VPS)
- **Nome:** egos-self-discovery ou therapeutic-assistant
- **ICP:** B2C wellness/self-improvement (não medical device)
- **Diferencial:** "IA que pergunta, não responde" (método maiêutico)
- **Nicho inicial:** Padrões de procrastinação (evitar claims médicos)
- **Stack:** Manter Python v2 inicialmente, portar para TS gradualmente
- **Integração:** Via Gateway (futuro), não acoplamento direto
- **Container:** Criar Docker container no VPS (task VPS-002)

---

### 18. TALMUDIC VALIDATION (v2/core/validators/talmudic_validation.py)

**What it is:**
- Counter-argument evaluation
- Stress test framework  
- Cross-domain analogies
- Decision brief generator

**Lines:** 180  

**Potential value:**
- ✅ Decision-making methodology
- ✅ Risk assessment patterns
- ✅ Multi-perspective analysis
- ⚠️ "Talmudic" terminology needs discussion

**User decision needed:** PORT or ARCHIVE?

---

### 19. SYSTEMD SERVICES (v2/ops/deploy/systemd/)

**What it is:**
- 15+ production-ready systemd units
- Security hardening (NoNewPrivileges, ProtectSystem)
- Environment file patterns
- Restart policies

**Files:**
- `egos-agent.service`
- `mcp_hub.service`
- `mcp_bridge.service`
- `egos-website.service`
- `windsurf-monitor.service`
- `oracle-arm-monitor.service`
- etc.

**Potential value:**
- ✅ Production deployment patterns
- ✅ Security hardening templates
- ✅ Systemd best practices
- ⚠️ Replaced by Docker Compose in modern EGOS

**User decision needed:** REFERENCE or ARCHIVE?

---

### 20. STRATEGY DOCUMENT (v2/STRATEGY.md)

**What it is:**
- Product strategy for EGOS v.3
- Market comparison (ChatGPT, Claude, Perplexity)
- Freemium pricing model
- Maiêutic method explanation

**Lines:** 675  

**Potential value:**
- ✅ Historical strategy context
- ✅ Market positioning
- ✅ Pricing research
- ✅ Differentiation analysis

**User decision needed:** KEEP or ARCHIVE?

---

## 📊 CATEGORIZATION SUMMARY

| Category | Count | Total Size | Status |
|----------|-------|------------|--------|
| **Core Algorithms** | 5 | ~2,000 lines | AWAITING DECISION |
| **System/Infra** | 6 | ~2,500 lines | AWAITING DECISION |
| **Booking Agent** | 1 | ~100KB | ✅ **ARQUIVADO (2026-04-06)** |
| **Self-Discovery** | 1 | ~50KB | ✅ **PRODUTIZAR (2026-04-06)** |
| **Documentation** | 5 | ~5,000 lines | AWAITING DECISION |
| **TOTAL** | **20 gems** | **~200KB+** | **PARTIAL DECISIONS RECORDED** |

---

## ✅ DECISÕES CONFIRMADAS (2026-04-06)

### RESUMO EXECUTIVO

| Gem | Decisão | Detalhes | Status |
|-----|---------|----------|--------|
| **Self-Discovery** | **PRODUTIZAR** | Container porta 3098, B2C wellness, método maiêutico | ✅ Decidido |
| **Booking Agent** | **ARQUIVAR** | Manter em v2, pattern detection pode ir para Forja | ✅ Decidido |

### PRÓXIMAS DECISÕES PENDENTES

| Gem | Status | Prioridade |
|-----|--------|------------|
| Sacred Math | PORT vs ARCHIVE? | P2 |
| Event Bus | PORT CONCEPTS vs ARCHIVE? | P2 |
| Knowledge Graph | PORT vs ARCHIVE? (BRACC separado) | P1 |
| Lint Intelligence | STUDY vs ARCHIVE? | P2 |
| MCP Hub v2 | STUDY PATTERNS vs ARCHIVE? | P2 |

### DECISÕES DE TERMINOLOGIA

| Termo | Status | Ação |
|-------|--------|------|
| "Sacred Math" | Sanitizar | Substituir por "optimization algorithms" |
| "Talmudic" | Revisar | Substituir por "multi-perspective validation" |
| "Quantum" (backup) | Sanitizar | Substituir por "intelligent" |

---

### Remaining Decisions Needed:

1. **Sacred Math** — Port Golden Ratio algorithms to TypeScript?
2. **Event Bus** — Use patterns for modern Mycelium?
3. **Knowledge Graph** — Port to BRACC Neo4j schema?
4. **MCP Hub** — Study patterns or fully superseded?
5. **ETHIK System** — Extract gamification or fully archive?

### Terminology Discussion:

8. "Sacred" / "Sacred Math" — Keep concept, change name?
9. "Talmudic" — Appropriate terminology?
10. "Quantum" (for backup) — Misleading? Change to "Intelligent"?

### Strategy Questions:

11. Should v2 apps be productized separately from kernel?
12. Which patterns are worth documenting vs porting?
13. Archive timeline — how long to keep before purging?

---

## 🗂️ ARCHIVE ORGANIZATION RECOMMENDATION

### Proposed Structure:

```
egos-archive/
├── _DECISIONS_PENDING/     # All items awaiting your decision
│   ├── sacred_math/
│   ├── event_bus/
│   ├── knowledge_graph/
│   ├── lint_system/
│   ├── talmudic_validator/
│   ├── activation_protocol/
│   ├── quantum_backup/
│   ├── fastcheck/
│   ├── pm2_manager/
│   ├── health_monitor/
│   ├── telegram_notifier/
│   ├── mycelium_generator/
│   ├── mcp_hub/
│   ├── booking_agent/
│   ├── ethik_distribution/
│   ├── code_archaeology/
│   ├── self_discovery/
│   ├── systemd_services/
│   └── strategy_docs/
│
├── _ALREADY_DECIDED/       # Items you've ruled on
│   ├── PORT_TO_KERNEL/     # Successfully ported
│   ├── STUDY_ONLY/         # Studied, patterns extracted
│   └── ARCHIVE/            # Archived (decided not to use)
│
├── v2-EGOSv2/              # Original structure preserved
├── v3-EGOSv3/              # Original structure preserved
├── v4-egosv4/              # Original structure preserved
├── v4-EGOSv4/              # Original structure preserved
├── v5-EGOSv5/              # Original structure preserved
└── README.md               # This catalog
```

---

## ⏳ NEXT STEPS

### Awaiting Your Input:

1. Review each gem above
2. Decide: PORT / STUDY / ARCHIVE for each
3. Discuss terminology concerns
4. Confirm product vs framework separation
5. Set archive retention policy

### Once Decided:

- I'll organize files per your decisions
- Create porting plans for selected items
- Document patterns from study-only items
- Archive rejected items with clear rationale

---

**Prepared by:** Cascade  
**Date:** 2026-04-06  
**Status:** PARTIAL DECISIONS RECORDED — remaining archive gems still await review  
**No additional items should be ported or archived without explicit approval**
