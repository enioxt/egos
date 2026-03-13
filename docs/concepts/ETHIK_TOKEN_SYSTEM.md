# ETHIK Token Distribution System — Reference

> **Origin:** EGOSv2 (Oct 2025) | **Status:** Concept / Future Implementation
> **Full spec:** `/home/enio/egos-archive/v2/EGOSv2/ETHIK_DISTRIBUTION_SYSTEM.md`

## Core Algorithm

Proportional token distribution based on **growth delta** during Fibonacci periods.

```
user_tokens = (user_delta / total_delta) × token_pool
```

## Key Properties

- **Initial Score:** F₁₂ = 144 points (everyone starts equal)
- **Period:** F₇ = 13 days (Fibonacci)
- **Point Scale:** Simple=1, Moderate=1.5, Advanced=2 (max)
- **Anti-inflation:** Max F₂₁ = 21 points per period
- **Dual Tracking:** Permanent score + periodic delta counter
- **100% Distribution:** Entire pool distributed proportionally

## Database Schema (Reference)

- `ethik_scores` — permanent user scores
- `ethik_periods` — tracking periods
- `ethik_period_deltas` — per-period growth
- `ethik_actions` — audit trail with GitHub PR links

## Integration Points

- ATRiAN ethical validation for point awards
- Reviewer approval for high-value actions (2 pts)
- GitHub PR/Issue linking for audit trail
- Fibonacci-based tier system (F₃, F₅, F₈, F₁₃, F₂₁)

## When to Implement

After EGOS reaches community traction (10+ external contributors).
Requires: Supabase tables, distribution engine, admin dashboard.
