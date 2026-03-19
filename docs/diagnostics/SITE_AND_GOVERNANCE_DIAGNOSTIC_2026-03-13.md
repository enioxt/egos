# EGOS Site & Governance Diagnostic

> **Date:** 2026-03-13
> **Scope:** egos.ia.br frontend audit, cross-repo governance dispersal, ATRiAN archaeology, target audience, SSOT→frontend roadmap

---

## 1. ATRiAN — Archaeological Finding

**ATRiAN** (Ethical Guardrail) is a **Python module** from EGOSv2/v3 that validates tool calls before execution.

| Item | Value |
|------|-------|
| **Origin** | `EGOSv2/core/atrian/atrian_validator.py` |
| **Also found** | `EGOSv3/core/atrian/validator.py`, `egos-archive/v3/`, `egos-archive/v5/` |
| **What it does** | Score-based ethical guardrail (0.0–1.0). Checks tool names and args against blocked/caution keyword lists. Returns `SAFE`, `CAUTION`, or `BLOCKED`. |
| **Integration** | Was integrated with GEPA (evolutionary prompt optimizer). Achieved 0.925/1.0 avg score. |
| **Migrated?** | **NO.** Not migrated to egos/ or egos-lab. |
| **Current equivalent** | Partially replaced by `.windsurfrules` Frozen Zones + pre-commit hooks + `egos-gov check`. But ATRiAN operated at **runtime execution level** (before each tool call), not at the governance/file level. |
| **Verdict** | ATRiAN should be resurrected as a TypeScript agent in `egos/`. Natural fit for Event Bus — intercept `tool.call.*` events and validate before execution. First **real-time ethical guardrail** in current system. |

---

## 2. Hardcoded Stats in egos.ia.br (Frontend Audit)

### Wrong / Stale Values

| File | Line | Current Value | Correct Value | Fix |
|------|------|---------------|---------------|-----|
| `pages/AuditHub.tsx` | 331 | `18 agents` | `29 agents` | Replace with `ECOSYSTEM_STATS.agents.total` |
| `components/AuditHub.tsx` | 43 | `useState(23)` | Should be 29 | Import and use `ECOSYSTEM_STATS.agents.total` |
| `components/EcosystemGrid.tsx` | 68 | `'29 agentes autônomos...'` | Hardcoded string | Template literal |
| `components/EcosystemGrid.tsx` | 69 | `'29 agentes registrados (24 ativos)...'` | Hardcoded | Template literal |
| `pages/Blog.tsx` | 69 | `'29 agentes autônomos'` | Hardcoded in markdown | Template literal |
| `pages/Blog.tsx` | 287 | `'29 Agentes, Zero Microgerenciamento'` | Hardcoded title | Template literal |

### Already Dynamic (Good)

| Component | Source |
|-----------|--------|
| `HeroSection.tsx` | `ECOSYSTEM_STATS.agents.total` ✅ |
| `Layout.tsx` | `AGENTS.length` from registry ✅ |
| `EcosystemPulse.tsx` | `ECOSYSTEM_STATS` + API fallback ✅ |

---

## 3. Governance Dispersal — CRITICAL FINDING

### Reality: ALL governance files are LOCAL COPIES, not symlinks

| Repo | `.guarani/` | `.windsurfrules` | Notes |
|------|-------------|------------------|-------|
| **egos** | LOCAL (canonical) | LOCAL (canonical) | This IS the source |
| **egos-lab** | LOCAL COPY (4 files symlinked) | LOCAL COPY | Partial symlinks only |
| **carteira-livre** | LOCAL COPY | LOCAL COPY | Zero symlinks |
| **br-acc** | LOCAL COPY | LOCAL COPY | Zero symlinks |
| **forja** | LOCAL COPY | LOCAL COPY | Zero symlinks |
| **policia** | LOCAL COPY | LOCAL COPY | Zero symlinks |
| **egos-self** | LOCAL COPY | LOCAL COPY | Zero symlinks |

**Risk:** If someone updates `.guarani/PREFERENCES.md` in `carteira-livre`, it will NOT propagate. Governance DNA can silently drift.

**Note:** `AGENTS.md`, `TASKS.md`, and `.windsurfrules` are repo-specific. Shared governance DNA like `.guarani/orchestration/`, `.guarani/philosophy/`, and `.guarani/prompts/` can be symlinked from the kernel when the local copy is an exact match.

---

## 4. Target Audience & Positioning

### Who is EGOS for RIGHT NOW?

| Persona | Why they'd use EGOS | What they'd replace |
|---------|---------------------|---------------------|
| **Solo dev with multiple repos** | SSOT enforcement, AI governance, frozen zones | Manual `.eslintrc` + scattered docs |
| **AI-first startup (2-5 devs)** | Agent registry, event bus, zero-dep runtime | LangChain/CrewAI (heavy Python) |
| **Open-source maintainer** | Audit Hub (paste URL → report), Gem Hunter | Manual code review + CodeClimate |
| **Researcher / Academic** | Lineage tracking, Tree of Life, governance-as-code | No equivalent exists |

### The Honest Value Proposition

> **EGOS is for developers who use AI coding assistants (Cursor, Windsurf, Claude Code, Codex) and want to prevent those assistants from destroying their codebase.**

---

## 5. Can Existing Tools Benefit Retroactively?

| Tool/App | Benefit | Effort |
|----------|---------|--------|
| **carteira-livre** | HIGH — 31 scripts → governed agents | Medium |
| **br-acc** | MEDIUM — governance only (Python/Neo4j) | Low |
| **egos-lab apps** | HIGH — fix frontend to reflect reality | Low |
| **policia / forja** | LOW — governance only | Minimal |

**New projects benefit MORE** (start with kernel from day zero). Existing projects benefit from governance but migrating scripts→agents requires deliberate work.

---

## 6. SSOT → Frontend Connection Roadmap

### Phase 1: Fix Hardcoded Values (TODAY)
- Replace all hardcoded agent counts with `ECOSYSTEM_STATS`
- Update `landingConstants.ts` to reflect current reality

### Phase 2: API Endpoint for Live Stats
- `GET /api/ecosystem-stats` reads from agents.json, git log, Supabase

### Phase 3: Embed Evolution Tree
- Share data source between `evolution-tree.html` and `MILESTONES_DATA`
- Add `/evolution` route to egos-web

### Phase 4: Surface Parity Agent
- Auto-sync backend truth → frontend constants on pre-commit

---

## 7. Progress

| Area | % |
|------|---|
| Agent Runtime | 95% |
| Governance DNA | 80% (exists but not symlinked) |
| Archaeological Lineage | 100% |
| Frontend reflects reality | 60% (hardcoded values) |
| VPS Synchronization | 15% (strategy only) |
| Cross-repo symlink enforcement | 20% |
| ATRiAN migration | 0% |
| Surface Parity Agent | 0% |
| **Overall Consolidation** | **~55%** |
