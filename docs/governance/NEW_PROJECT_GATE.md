# New Project Gate

> **SSOT Owner:** `egos/docs/governance/NEW_PROJECT_GATE.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE — BLOCKING
> **Task:** EGOS-077

---

## Purpose

No new product, package, or repo may be created without passing this gate.

This gate exists to prevent:
- Scope expansion before the flagship has revenue
- Parallel product lines that drain focus
- Repos and packages created out of enthusiasm that become maintenance debt

---

## The Gate

Every new surface must answer all questions before work begins. Unanswered questions = **blocked**.

### 1. PRD (Product Requirements Document)

| Field | Required Answer |
|-------|----------------|
| **Name** | What is the canonical name? |
| **One-sentence VP** | What does it do and for whom? (≤15 words) |
| **Problem statement** | What specific, observable problem does it solve? |
| **What it is NOT** | Explicit anti-scope to prevent drift |
| **Definition of done** | How do we know it's complete? (must be measurable) |

### 2. ICP (Ideal Customer Profile)

| Field | Required Answer |
|-------|----------------|
| **Who pays** | Name a real role/person type who writes the check |
| **Who uses** | Name a real role/person type who uses it daily |
| **Where they are** | Industry, org size, geography |
| **Job to be done** | What are they hiring this for? (Clayton Christensen format) |
| **Current workaround** | How do they solve this today without us? |

### 3. Go-to-Market

| Field | Required Answer |
|-------|----------------|
| **Distribution channel** | How do customers find it? (npm / direct outreach / referral / etc.) |
| **Acquisition motion** | Self-serve, sales-led, or community-led? |
| **First customer path** | Name one specific person or org that could be the first customer |
| **Price hypothesis** | What would someone pay? (free / R$X/mo / custom — with rationale) |
| **Competitive landscape** | Name 2 alternatives and why ours is better for the ICP |

### 4. Objective and Success Metrics

| Field | Required Answer |
|-------|----------------|
| **Objective** | One sentence: what outcome are we optimizing for? |
| **Metric 1 (leading)** | What early signal tells us it's working? |
| **Metric 2 (lagging)** | What confirms it worked? (revenue / users / retention) |
| **90-day milestone** | What does "done enough to evaluate" look like in 90 days? |
| **Kill condition** | What would tell us to stop? |

### 5. Kernel Health Prerequisite

Before any new product surface can be approved, the current flagship must meet at least one:

- [ ] `@egos/guard-brasil` published to npm
- [ ] ≥1 external user of Guard Brasil (not internal)
- [ ] ≥1 paying customer at any tier

**Exception:** kernel-core infrastructure (types, contracts, audit, registry) is exempt from this prerequisite.

### 6. Multi-Model Review

The PRD must be reviewed by at least two perspectives:

| Reviewer | Mode | Question to answer |
|----------|------|-------------------|
| Adversarial | "Why will this fail?" | Name 3 ways this could be a waste of time |
| Strategic | "Does this strengthen the flagship?" | Does it accelerate Guard Brasil revenue or dilute it? |

Both reviews must be recorded (inline in PRD, in a task comment, or in a handoff doc).

---

## Gate Decision

After completing the above, record one of:

| Decision | Meaning | Next step |
|----------|---------|-----------|
| `APPROVED` | All fields answered, prerequisites met, both reviews done | Assign to sprint, create EGOS task |
| `BLOCKED — prerequisites` | Flagship health gate not met | Revisit after Guard Brasil milestone |
| `BLOCKED — incomplete PRD` | Missing answers above | Complete PRD first, then re-submit |
| `ADVISORY — proceed with caution` | Answers exist but weak ICP or no clear revenue path | Owner accepts risk in writing, narrow scope first |

---

## Gate Template (copy to use)

```markdown
## New Project Gate — [Project Name]

**Date:** YYYY-MM-DD
**Author:** [name]
**Decision:** [ ] APPROVED / [ ] BLOCKED / [ ] ADVISORY

### PRD
- Name:
- One-sentence VP:
- Problem:
- Not:
- Done when:

### ICP
- Who pays:
- Who uses:
- Where:
- Job to be done:
- Current workaround:

### GTM
- Channel:
- Motion:
- First customer:
- Price hypothesis:
- Competitors:

### Objective + Metrics
- Objective:
- Leading metric:
- Lagging metric:
- 90-day milestone:
- Kill condition:

### Kernel Health
- [ ] @egos/guard-brasil on npm
- [ ] ≥1 external user
- [ ] ≥1 paying customer
(or mark as kernel_core exception)

### Multi-Model Review
**Adversarial:** [3 ways it fails]
**Strategic:** [Does it accelerate Guard Brasil?]
```

---

## Completed Gates

| Project | Date | Decision | Task |
|---------|------|----------|------|
| EGOS Guard Brasil | 2026-03-23 | `APPROVED` (pre-gate, retrospectively validated) | EGOS-062..064 |

---

*Maintained by: EGOS Kernel*
*Related: EGOS-077, EGOS-076, docs/strategy/ECOSYSTEM_CLASSIFICATION_REGISTRY.md*
