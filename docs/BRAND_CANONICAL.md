# EGOS Brand — Canonical Guide

<!-- SSOT-VISITED: 2026-03-30, disposition: superseded (egos-lab/branding/BRAND_GUIDE.md) -->

> **Version:** 1.0.0 | **Created:** 2026-03-30 | **Closes:** EGOS-132
> **Status:** CANONICAL — this is the single source of truth for EGOS brand identity
> **Supersedes:** `/home/enio/egos-lab/branding/BRAND_GUIDE.md` (v1.0.0, 2026-02-22)
> **Source:** `docs/PRESENTATION_VISUAL_IDENTITY.md` (v1.0.0, 2026-03-26), extended here

---

## Decision Record — Tsun-Cha Protocol

Two brand guides existed with incompatible specifications. One had to win.

### Evidence Examined

| Criterion | egos-lab BRAND_GUIDE.md | egos PRESENTATION_VISUAL_IDENTITY.md | Winner |
|-----------|------------------------|--------------------------------------|--------|
| **Date** | 2026-02-22 | 2026-03-26 | PRESENTATION (+32 days newer) |
| **Colors in actual app code** | Not found in egos/apps/ source | Not found in egos/apps/ source | Tie — neither used yet |
| **Depth/completeness** | ~115 lines, basic palette + voice | ~580 lines, full system: palette, typography, layout, CSS vars, dark mode, data viz, accessibility, usage examples | PRESENTATION (5x more complete) |
| **Referenced in canonical docs** | Not in AGENTS.md, SYSTEM_MAP.md | Referenced via TASKS.md EGOS-132 conflict note | PRESENTATION |
| **Serves operator-grade aesthetic** | Cyan #13b6ec / Purple — "glassmorphism", "consciousness tools" — consumer/community tone | Navy #0A0E27 / Blue #2563EB — "Governance is Infrastructure", "dark enterprise / operator-style" | PRESENTATION (explicit match) |
| **Gabriel Cambraia alignment** | Not aligned — brighter, more playful | Aligned — handoff_2026-03-22.md explicitly states "dark enterprise / operator-style" chosen to attract Cambraia | PRESENTATION |
| **CSS variables defined** | No | Yes — full `:root` block, dark mode block | PRESENTATION |
| **Accessibility spec** | No | Yes — WCAG AA ratios, dyslexia-friendly rules | PRESENTATION |

### Dialectical Check (Tsun-Cha)

**Thesis:** egos-lab BRAND_GUIDE.md should win — it was the first brand codified, lives in egos-lab
(the "real" public-facing codebase), and has the "open-source community" energy.

**Antithesis:** PRESENTATION_VISUAL_IDENTITY.md should win — it is newer, more complete,
explicitly aligned with the operator-grade dark-enterprise positioning, and matches the
stated GTM strategy (B2B, government contracts, labor rights enforcement — not consumer social).

**Synthesis:** The antithesis wins on every material dimension. The egos-lab guide was written
in an earlier phase (2026-02-22) when the brand narrative was still "conscious technology ecosystem."
By 2026-03-26, the positioning had crystallized to "Governance is Infrastructure" — a deliberate pivot
toward enterprise credibility. The Navy/Blue/Inter system is more professional, more legible in
dashboards and government contexts, and was explicitly chosen to signal operator-grade seriousness
to potential design talent (Cambraia). Cyan glassmorphism reads as startup/web3; Navy enterprise blue
reads as Stripe, GitHub, Vercel — the peers we want to be compared to.

**Decision: `docs/PRESENTATION_VISUAL_IDENTITY.md` is canonical.**

---

## Canonical Brand Specification

The full specification is maintained at:

**`/home/enio/egos/docs/PRESENTATION_VISUAL_IDENTITY.md`**

This file (`BRAND_CANONICAL.md`) serves as the decision record and migration anchor.
Do not duplicate the full spec here — read it from PRESENTATION_VISUAL_IDENTITY.md directly.

### Quick Reference (load-bearing values)

| Token | Value | Usage |
|-------|-------|-------|
| `--egos-black` | `#0A0E27` | Primary text, dark mode background |
| `--egos-navy` | `#1A2F5A` | Secondary backgrounds, cards |
| `--egos-blue` | `#2563EB` | CTAs, links, active states, logo |
| `--egos-green` | `#10B981` | Success, compliance passing |
| `--egos-amber` | `#F59E0B` | Warnings, drift detection |
| `--egos-red` | `#EF4444` | Errors, governance blocks |
| **Primary Font** | Inter | Headers, UI, navigation |
| **Code Font** | JetBrains Mono | Code blocks, governance rules |
| **Tagline** | "Governance is Infrastructure" | All external surfaces |

### What the Losing Guide Gets Right (Preserve These)

The egos-lab guide had elements worth keeping even though it is superseded:

1. **Sacred Code:** `000.111.369.963.1618` — retain as internal identity marker (logo detail, not prominent external)
2. **Bilingual policy:** PT-BR default, English for international — carry forward
3. **Voice principles:** "Technical but accessible," "Concise — no fluff, numbers first" — compatible with PRESENTATION guide
4. **Social handles:** `egos.ia.br`, `@ethikin` on Telegram — factual, not brand decisions

These are absorbed into the canonical guide, not lost.

---

## Migration Note

The guide at `/home/enio/egos-lab/branding/BRAND_GUIDE.md` is **superseded**.

- It retains its file location for historical reference
- A `SUPERSEDED` header has been added to that file pointing here
- Archive on next cleanup pass: move to `egos-lab/archive/branding/BRAND_GUIDE.md`
- No code changes required yet (neither color system was implemented in app source)
- First implementation surface: `apps/guard-brasil-web/` — use `--egos-blue: #2563EB` as primary

---

## Gabriel Cambraia — Creative Director Brief

**Context:** Gabriel Cambraia was identified as a target for passive brand attraction via
the `presentation.html` surface (handoff_2026-03-22.md). The operator-grade dark-enterprise
aesthetic was chosen explicitly to signal "this project has a strong visual foundation that
needs a human art director, not a generalist."

**What is settled (do not re-open without strong reason):**

- Color system: Navy/Blue/Green (enterprise-grade, WCAG AA verified)
- Font system: Inter + JetBrains Mono (GitHub/Stripe/Vercel tier)
- Tagline: "Governance is Infrastructure"
- Visual language: evidence-first, no fluff, no glassmorphism, no gradients for data viz
- Logo concept: Fibonacci spiral in EGOS Blue

**What remains TBD for the creative director:**

| Item | Status | Notes |
|------|--------|-------|
| Logo artwork | TODO | Fibonacci spiral concept defined, no SVG yet |
| Logo variations | TODO | Full / mark / wordmark / horizontal / vertical |
| Favicon | TODO | 32px mark variant needed |
| Component library | TODO | Figma file — entire token set needs production-ready implementation |
| Illustration style | TODO | Geometric, Fibonacci-based, SVG only — concept defined, no assets |
| Social templates | TODO | Figma templates for X, LinkedIn, Telegram announcement |
| Email signature | TODO | HTML template per brand spec |
| Motion guidelines | TODO | Subtle animations (opacity + y translate) — principles noted, not specified |
| Brand book PDF | TODO | Formal document for partnership/investor contexts |

**Invitation surface:** `presentation.html` (in egos repo) — the passive invite used to
demonstrate brand seriousness before direct outreach. This should be updated to reflect
the canonical color system before any Cambraia interaction.

---

## SSOT Visit Log

```
- [x] SSOT-VISIT 2026-03-30: egos-lab/branding/BRAND_GUIDE.md → read full file → superseded (canonical: egos/docs/PRESENTATION_VISUAL_IDENTITY.md)
- [x] SSOT-VISIT 2026-03-30: egos/docs/PRESENTATION_VISUAL_IDENTITY.md → read full file → kept-as-ref (canonical brand guide)
- [x] SSOT-VISIT 2026-03-30: egos/docs/_current_handoffs/handoff_2026-03-22.md → read Cambraia context → kept-as-ref
```

---

*Brand clarity is a governance decision. One truth, one system, forward.*
