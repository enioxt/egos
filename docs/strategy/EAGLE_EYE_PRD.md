# Eagle Eye — Product Requirements Document

> **Version:** 1.0.0 | **Updated:** 2026-03-30
> **Task:** EGOS-123
> **Status:** PRD DRAFT — pending user proposal integration
> **Owner:** egos-lab (leaf product) | Kernel interface: `packages/shared/src/osint/`

---

## 1. One-Sentence Value Proposition

**Eagle Eye** is Brazil's first AI-powered market intelligence scanner that turns public gazette data, OSINT signals, and local event patterns into actionable business opportunities — with governance, evidence chains, and LGPD compliance built in.

---

## 2. Problem Statement

Brazilian entrepreneurs and AI developers lack a tool to:
1. Monitor public gazettes (Diários Oficiais) for contract opportunities automatically
2. Identify local market signals (events, tourism spikes, regulatory changes) before competitors
3. Correlate multi-source data (gazettes + social + geographic) into scored opportunities
4. Do all of the above with LGPD-safe PII handling and audit trails

Existing tools are either English-first, paid-only, or lack Brazilian government data integrations.

---

## 3. Target Personas

| Persona | Pain | Eagle Eye Gain |
|---------|------|----------------|
| **Brazilian freelancer / micro-empresa** | Misses public tenders, discovers too late | Daily opportunity digest with viability score |
| **Municipal tourism agency** | No data on actual tourist flows | Citizen-logger + gamification + influencer radar |
| **EGOS operator / developer** | Needs cross-repo market intelligence | OSINT primitives in `@egos/shared` for custom agents |
| **Investigative journalist / researcher** | Manual gazette research is slow | Batch scan + event-pattern-matcher at scale |

---

## 4. Current State Inventory (egos-lab/apps/eagle-eye/)

### 4.1 Core Analysis Engine
| File | Function |
|------|----------|
| `src/analyze_viability.ts` | Scores opportunities 0–100 on feasibility, market size, competition |
| `src/analyze_gazette.ts` | Parses gazette text → structured opportunity records |
| `src/enrich_opportunity.ts` | Enriches raw opportunity with context (sector, location, budget) |
| `src/process_enrichment.ts` | Batch enrichment pipeline with retry/rate-limit |
| `src/fetch_gazettes.ts` | Fetches Diário Oficial content from public APIs |
| `src/idea_patterns.ts` | Detects recurring idea patterns across scans |
| `src/index.ts` | Entry point / orchestrator |
| `src/test-intelligence.ts` | Integration test harness |

### 4.2 Batch & Research
| File | Function |
|------|----------|
| `src/batch_scan.ts` | High-volume parallel scan with concurrency control |
| `src/research/timeline_tracer.ts` | Traces opportunity timelines across gazette history |
| `src/scripts/scan_brazil.ts` | Full Brazil territory scan script |
| `src/scripts/local-expansion/city_opportunity_scanner.ts` | Per-city opportunity scanner |
| `src/scripts/check_coverage.ts` | Reports gazette coverage by state/city |

### 4.3 Tourism Module (full sub-system)
| File | Function |
|------|----------|
| `src/modules/tourism/types.ts` | Tourism entity types |
| `src/modules/tourism/system-prompt.ts` | LLM prompt template for tourism analysis |
| `src/modules/tourism/campaign.ts` | Tourism campaign generator |
| `src/modules/tourism/checklist.ts` | Pre-launch checklist validation |
| `src/modules/tourism/gamification.ts` | Citizen contribution scoring system |
| `src/modules/tourism/citizen-logger.ts` | Records citizen tourism data with LGPD consent |
| `src/modules/tourism/influencer-radar.ts` | Detects local influencers in tourism sector |
| `src/modules/tourism/maps-instructor.ts` | Google Maps integration layer |
| `src/modules/tourism/social-listener.ts` | Social signal monitor for tourism spikes |
| `src/modules/tourism/truth-consensus.ts` | Multi-source consensus for contested data |
| `src/modules/tourism/web-scraper.ts` | Generic scraper with anti-bot handling |
| `src/modules/tourism/scraper-patoshoje.ts` | PatosHoje-specific scraper |
| `src/modules/tourism/scraper-patosja.ts` | PatosJá-specific scraper |
| `src/modules/tourism/seo-factory.ts` | SEO content generation for opportunities |
| `src/modules/tourism/index.ts` | Tourism module entry point |

### 4.4 Events & Influencers
| File | Function |
|------|----------|
| `src/modules/events/event-pattern-matcher.ts` | Detects recurring event patterns (festivals, fairs, tenders) |
| `src/modules/influencers/influencer-detector.ts` | Cross-platform influencer identification |

### 4.5 UI Surfaces
| Surface | Tech | Status |
|---------|------|--------|
| `src/ui/dashboard.html` | Vanilla HTML + JS | MVP (Wave 0) |
| `src/ui/analytics.html` | Vanilla HTML + JS | MVP (Wave 0) |
| `src/ui/map.html` | Vanilla HTML + Leaflet | MVP (Wave 0) |
| `src/ui/detail.html` | Vanilla HTML | MVP (Wave 0) |
| `src/app/dashboard/page.tsx` | Next.js 14 | Wave 3 redesign |
| `src/app/login/page.tsx` | Next.js 14 | Wave 3 redesign |
| `src/components/auth/AuthLayout.tsx` | React | Wave 3 redesign |
| `apps/egos-web/src/pages/EagleEye.tsx` | React (egos-web) | Embedded in public site |

### 4.6 Data
| File | Function |
|------|----------|
| `src/data/territories.ts` | Brazil territory data — states, cities, IBGE codes |

### 4.7 Strategy Docs (apps/eagle-eye/docs/)
| Doc | Contents |
|-----|----------|
| `API_STRATEGY.md` | Public API design — rate limits, auth, endpoints |
| `COMMUNITY_STRATEGY.md` | OSS community growth plan |
| `GAMIFICATION_REPORT.md` | Citizen engagement and point system design |
| `PHASE_20_PLAN.md` | Wave 20+ roadmap (advanced ML / agent integration) |
| `STITCH_PROMPTS.md` | Google Stitch UI generation prompts |
| `SCRAPER_REPORT.md` | Scraping coverage and reliability report |
| `SEO_STRATEGY.md` | SEO + content marketing strategy |
| `TOURISM_MODULE.md` | Tourism module architecture spec |
| `handoffs/handoff_tourism_v1-3.md` | Cross-session handoff notes |

### 4.8 Infra
| File | Function |
|-----|----------|
| `Dockerfile` | Containerized deployment |
| `.env.example` | Required environment vars |
| `package.json` | App dependencies |
| `README.md` | Setup guide |

---

## 5. Standalone vs Stay-in-egos-lab: Verdict

**Decision: KEEP IN EGOS-LAB for now.**

| Factor | Assessment |
|--------|------------|
| External users | 0 — no npm package, no public API yet |
| Team size | 1 (Enio) |
| Repo split benefit | None — adds sync overhead before first user |
| Kernel dependency | Uses `packages/shared` (shared in egos-lab) |
| Classification | `leaf_consumer` + `incubator` in ecosystem registry |
| When to reconsider | After first paying customer OR ≥100 active free users |

**Kernel responsibilities:**
- `packages/shared/src/osint/` — gazette fetch primitives + opportunity types (cross-repo reuse)
- `agents/agents/eagle-eye-auditor.ts` — kernel agent that runs against any Eagle Eye deployment

**Eagle Eye responsibilities (stays in egos-lab):**
- All app code, UI, scrapers, tourism module, deploy config
- LGPD consent flows, citizen data, database schemas

---

## 6. Architecture (Target State)

```
egos (kernel)
└── packages/shared/src/osint/
    ├── gazette-types.ts       ← gazette record shapes, opportunity schema
    ├── territory-types.ts     ← Brazil states/cities/IBGE type definitions
    └── viability-types.ts     ← opportunity viability score schema

egos-lab
└── apps/eagle-eye/
    ├── src/
    │   ├── fetch_gazettes.ts      (imports @egos/shared/osint)
    │   ├── analyze_viability.ts   (imports @egos/shared/osint)
    │   ├── modules/
    │   │   ├── tourism/           (standalone, 15 files)
    │   │   ├── events/
    │   │   └── influencers/
    │   └── ui/                    (Next.js dashboard)
    └── docs/
        ├── API_STRATEGY.md
        ├── TOURISM_MODULE.md
        └── PHASE_20_PLAN.md
```

---

## 7. Roadmap

### Wave A — Kernel Foundation (NOW, in egos kernel)
- [ ] EGOS-123: Eagle Eye PRD (this document)
- [ ] EGOS-124: Create `packages/shared/src/osint/` — gazette + opportunity types
- [ ] EGOS-125: Create `eagle_eye_auditor` kernel agent — scans Eagle Eye deployments for LGPD compliance + module health

### Wave B — Core Hardening (in egos-lab, needs access)
- [ ] EGOS-126: Migrate Eagle Eye to consume `@egos/shared` for ATRiAN + PII masking
- [ ] EGOS-127: Add evidence chain to all opportunity records (audit hash, source, timestamp)
- [ ] EGOS-128: Wire Guard Brasil into citizen-logger.ts for LGPD-compliant data collection
- [ ] EGOS-129: Add typecheck + test suite to eagle-eye (bun test for core modules)

### Wave C — API Surface (gate: Guard Brasil npm-published first)
- [ ] EGOS-130: Build Eagle Eye REST API (`/api/scan`, `/api/opportunities`, `/api/report`)
- [ ] EGOS-131: Add rate limiting + API key auth using `@egos/shared` rate-limiter
- [ ] EGOS-132: Deploy Eagle Eye API on Hetzner VPS as Docker container

### Wave D — Advanced Intelligence (gate: ≥100 users)
- [ ] EGOS-133: Integrate Eagle Eye event-pattern-matcher with Mycelium event bus
- [ ] EGOS-134: Cross-app event routing: Eagle Eye ↔ Intelink ↔ EGOS (Mycelium Phase 4)
- [ ] EGOS-135: ML opportunity scoring upgrade (fine-tuned on Brazilian public tender data)

---

## 8. Integration Points with EGOS Kernel

| Kernel Surface | Eagle Eye Integration |
|----------------|----------------------|
| `@egos/guard-brasil` | PII masking on citizen data, ATRiAN scoring on AI responses |
| `packages/shared/model-router` | Route gazette analysis to cheap-first models |
| `packages/shared/mycelium/reference-graph` | Eagle Eye as node in EGOS graph |
| `agents/registry/agents.json` | Register `eagle_eye_auditor` as kernel agent |
| `docs/governance/DISSEMINATION_PROTOCOL.md` | Eagle Eye receives kernel governance updates |

---

## 9. Success Metrics

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Opportunities scanned / day | ≥100 | 10–99 | <10 |
| Gazette coverage (states) | 27/27 | 15–26 | <15 |
| Viability score accuracy (manual audit) | ≥80% correct | 60–79% | <60% |
| ATRiAN score on AI responses | ≥85 | 70–84 | <70 |
| LGPD compliance checks passing | 100% | — | <100% |
| API uptime (Wave C+) | ≥99.5% | 98–99.4% | <98% |

---

## 10. Open Questions (for Enio)

1. What are the specific proposals for Eagle Eye improvements?
2. Should the Next.js dashboard replace the vanilla HTML UI entirely or coexist?
3. Is the tourism module (Patos de Minas focus) the primary vertical or one of many?
4. Target launch date for the API surface?
5. Any new data sources to integrate beyond Diário Oficial?
