# BLUEPRINT Tasks Quick Reference Matrix
## EGOS-110 to EGOS-123 Execution Map

**Version:** 2.0.0
**Date:** 2026-03-26
**Purpose:** One-page reference for task scheduling and dependency tracking

---

## Status at a Glance

```
COMPLETED (4)      ✅ EGOS-107, 109, 113, 115
PARTIAL (1)        🟡 EGOS-112 (60%)
PENDING (10)       ⏳ EGOS-110, 111, 114, 116-121
RESERVED (2)       📅 EGOS-122, 123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL EFFORT       185+ story points
CRITICAL PATH      8-9 weeks
BOTTLENECK         EGOS-116 ⭐ (unblocks 5 tasks)
```

---

## Task Matrix: Quick Reference

| Task | Title | Status | Complexity | Effort | Days | Dependencies | Owner | Blocker? |
|------|-------|--------|-----------|--------|------|-------------|-------|----------|
| 110 | Worktree Contract | ⏳ | Moderate | 25 | 3-4 | EGOS-099, 102 | Arch | **YES** ⚠️ |
| 111 | Spec-Pipeline Contract | ⏳ | Moderate | 28 | 4-5 | EGOS-110 | Gov | Weak |
| 112 | Doctor Command | 🟡 | Simple | 12 | 2 | None | DevOps | No |
| 113 | Benchmarker | ✅ | Complex | 45 | — | None | Research | No |
| 114 | MASA Pilot | ⏳ | Complex | 40 | 21 | EGOS-113 | Arch | Weak |
| 115 | Gem Hunter | ✅ | Complex | 50 | — | None | Agents | No |
| 116 | Presentation SSOT | ⏳ | Complex | 35 | 5-7 | EGOS-115 | PM | **YES** ⭐⭐ |
| 117 | Operator Kit | ⏳ | Moderate | 25 | 4-5 | EGOS-116 | PM | Strong |
| 118 | Demo Lane | ⏳ | Moderate | 20 | 3-4 | EGOS-116 | DevOps | Strong |
| 119 | Scorecard Cmd | ⏳ | Simple | 15 | 2-3 | EGOS-113 | DevOps | Weak |
| 120 | Visual Identity | ⏳ | Simple | 10 | 2-3 | EGOS-116 | Design | Weak |
| 121 | Clarity Review | ⏳ | Simple | 8 | 1-2 | EGOS-116 | Gov | Weak |
| 122 | [Reserved] | 📅 | — | — | — | — | — | — |
| 123 | [Reserved] | 📅 | — | — | — | — | — | — |

---

## Execution Roadmap (Gantt View)

```
WEEK 1     │████│   Phase 1: Foundations
├─ EGOS-112: Doctor [██──]
├─ EGOS-110: Worktree [██████──] (if EGOS-099,102 done)
└─ EGOS-114: MASA setup [█]

WEEK 2     │████│   Phase 2: Critical Path
├─ EGOS-116: Presentation [██████████────] (5-7 days, spans to W3)
├─ EGOS-111: Spec-Pipeline [████████──]
└─ EGOS-114: Measurement [ongoing]

WEEK 3     │████│   Phase 3: Narrative Execution (All Parallel)
├─ EGOS-117: Operator Kit [████████──]
├─ EGOS-118: Demo Lane [██████──]
├─ EGOS-119: Scorecard [██████]
├─ EGOS-120: Visual Identity [██████]
└─ EGOS-121: Clarity Review [████]

WEEK 4-7   │████│   Phase 4: Validation
├─ EGOS-114: Measurement (ongoing, 4 weeks)
└─ Integration & Hardening
```

---

## Dependency Flow (Text Graph)

```
CRITICAL BLOCKERS (Must Resolve)
┌────────────────────────────────────────────┐
│ EGOS-099 & EGOS-102 ?                      │
│ (Worktree + Operator Map prerequisites)    │
│ STATUS: ⚠️ UNKNOWN - CHECK IMMEDIATELY     │
└────────────────────────────────────────────┘
         ↓ Must both be DONE before:
    EGOS-110 (Worktree Contract)
         ↓
    EGOS-111 (Spec-Pipeline)

CRITICAL PATH BLOCKER (Unblocks 5 tasks)
┌────────────────────────────────────────────┐
│ EGOS-115 ✅ (Complete)                     │
│         ↓                                   │
│ EGOS-116 ⭐⭐ (Presentation SSOT)           │
│ STATUS: ⏳ PENDING - 5-7 DAYS DURATION    │
│         ↓                                   │
│    ┌────┴────┬─────────┬──────────┬────┐  │
│    ↓         ↓         ↓          ↓    ↓   │
│  EGOS-117  EGOS-118  EGOS-120  EGOS-121   │
│  (Kit)     (Demo)    (Visual)   (Gate)    │
│                                           │
│ ⭐⭐ = Start immediately after verification │
└────────────────────────────────────────────┘

INDEPENDENT CHAINS (Run Parallel)
┌────────────────────────────────────────────┐
│ EGOS-113 ✅ → EGOS-119 (Scorecard)         │
│           → EGOS-114 (MASA Pilot)          │
│ (No blocking; run anytime)                 │
└────────────────────────────────────────────┘
```

---

## Weekly Execution Checklist

### Week 1 Checklist
- [ ] **DAY 1:** Verify EGOS-099 + EGOS-102 completion
- [ ] **DAY 1:** Schedule PM for EGOS-116 review (Week 2)
- [ ] **DAY 1-2:** Start EGOS-112 completion (40% remaining)
- [ ] **DAY 2:** Start EGOS-110 IF prerequisites complete
- [ ] **DAY 2:** Setup EGOS-114 measurement framework
- [ ] **DAY 5:** Weekly sync — review blockers & parallel progress

### Week 2 Checklist
- [ ] **DAY 1:** Confirm EGOS-110 progress (50%+ done)
- [ ] **DAY 1:** START EGOS-116 (Presentation SSOT) — CRITICAL
- [ ] **DAY 2-3:** Continue EGOS-111 progress (if EGOS-110 on track)
- [ ] **DAY 3:** EGOS-114 baseline data collection
- [ ] **DAY 5:** Weekly sync — PM checkpoint on EGOS-116

### Week 3 Checklist (Post-EGOS-116 Completion)
- [ ] **DAY 1:** Review & approve EGOS-116 output
- [ ] **DAY 1:** UNBLOCK EGOS-117, 118, 120, 121 (start all)
- [ ] **DAY 2-3:** All 4 tasks running in parallel
- [ ] **DAY 3:** Start EGOS-119 (independent of phase)
- [ ] **DAY 5:** Weekly sync — narrative kit review

### Week 4+ Checklist
- [ ] **DAY 1:** Integration sweep (sync contracts to repos)
- [ ] **DAY 2:** EGOS-114 measurement phase (ongoing)
- [ ] **DAY 3:** VPS hardening for Mission Control deployment
- [ ] **DAY 5:** Monthly sync — EGOS-114 first data point

---

## Critical Path Decision Tree

```
START
  │
  ├─→ [Are EGOS-099 & EGOS-102 complete?]
  │   │
  │   ├─ YES ✅
  │   │   └─→ Start EGOS-110 immediately (Week 1, Day 2)
  │   │
  │   └─ NO ❌
  │       └─→ ADD THEM TO P0 BLOCKERS
  │           └─→ Adjust EGOS-110 timeline
  │
  ├─→ [Is PM scheduled for EGOS-116 review?]
  │   │
  │   ├─ YES ✅
  │   │   └─→ Start EGOS-116 Week 2, Day 1 (locked calendar)
  │   │
  │   └─ NO ❌
  │       └─→ SCHEDULE NOW (can't delay)
  │
  └─→ [Has EGOS-112 remaining 40% started?]
      │
      ├─ YES ✅
      │   └─→ Should complete by Week 1, Day 2
      │
      └─ NO ❌
          └─→ START IMMEDIATELY (fastest win)

THEN: Run all 3 parallel tracks (Infrastructure, Narrative, Research)
```

---

## Blocker Status Tracker

| Blocker | Status | Impact | Action Required | Deadline |
|---------|--------|--------|-----------------|----------|
| EGOS-099 (prerequisite) | ⚠️ UNKNOWN | Blocks EGOS-110 | **Verify today** | 2026-03-26 |
| EGOS-102 (prerequisite) | ⚠️ UNKNOWN | Blocks EGOS-110 | **Verify today** | 2026-03-26 |
| PM availability | ⚠️ UNSCHEDULED | Delays EGOS-116 | **Schedule today** | 2026-03-26 |
| EGOS-116 coherence | 🟡 PENDING | Cascades to 5 tasks | Monitor during execution | 2026-04-02 |

---

## Key Metrics to Track

### Daily Standup Metrics
- EGOS-110 progress % (if started)
- EGOS-116 status (when active)
- Any blockers emerged?
- Parallel track velocity

### Weekly Review Metrics
- % tasks on schedule
- Blocker resolution time (avg hours)
- Context loss % (token usage vs plan)
- PM review feedback on EGOS-116 (when active)

### Phase Gate Metrics
- Phase 1→2: EGOS-112 (100%), EGOS-110 (documented), EGOS-113/115 (proven)
- Phase 2→3: EGOS-116 (complete + reviewed), Stakeholder feedback (>80% positive)
- Phase 3→4: EGOS-117/118/120 (complete), Demo success (5/5 runs), Visual consistency (100%)

---

## Quick Links to Full Documentation

- **Full Plan:** `/home/user/egos/BLUEPRINT_EXECUTION_PLAN.md`
- **Analysis:** `/home/user/egos/BLUEPRINT_EXECUTION_ANALYSIS.md`
- **Task List:** `/home/user/egos/TASKS.md` (EGOS-110..123 section)
- **Strategy:** `/home/user/egos/docs/strategy/`
- **Governance:** `/home/user/egos/.guarani/orchestration/`

---

**Last Updated:** 2026-03-26
**Next Review:** 2026-04-02 (6 days)
**Version:** 2.0.0
