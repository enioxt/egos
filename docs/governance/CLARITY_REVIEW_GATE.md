# Clarity Review Gate

> **SSOT Owner:** `egos/docs/governance/CLARITY_REVIEW_GATE.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-121 | **Cadence:** Monthly

---

## Purpose

A monthly forcing function to prune complexity before it compounds. The kernel must stay explainable in one sentence. If it can't, this gate finds what to cut.

---

## When to Run

- First session of each month
- After any sprint that added >5 new governance docs or >3 new agents
- Before a demo or investor meeting
- When `/start` takes more than 30 seconds to orient you

---

## The Gate (15 minutes max)

### Check 1 — Can you explain EGOS in one sentence?

Write it now without looking at any docs:

> "EGOS is ___________."

If you can't write it in ≤15 words, something is wrong. Check FLAGSHIP_BRIEF.md and update if needed.

---

### Check 2 — TASKS.md complexity audit

```bash
wc -l TASKS.md
grep -c "^- \[ \]" TASKS.md  # open tasks
grep -c "^- \[x\]" TASKS.md  # completed tasks
```

| Metric | Green | Yellow | Red — Act |
|--------|-------|--------|----------|
| Total lines | ≤400 | 400–480 | >480 — archive completed tasks |
| Open tasks | ≤40 | 40–60 | >60 — close or defer 10+ tasks |
| Completed tasks (uncleaned) | ≤30 | 30–50 | >50 — archive to `docs/archive/TASKS_ARCHIVE.md` |

---

### Check 3 — docs/governance/ audit

```bash
ls docs/governance/ | wc -l
```

Each doc in `docs/governance/` must be referenceable from at least one active task or workflow. If not:
- Move to `docs/archive/governance/`
- Remove from SYSTEM_MAP.md references

---

### Check 4 — Agent registry health

```bash
bun run agent:lint
bun run agent:list
```

For each agent: does it have a task it was built for? If the task is closed and the agent is `active`, mark it `archived` if it's no longer used.

---

### Check 5 — Dead package check

```bash
ls packages/ | while read pkg; do
  echo "=== $pkg ===" && grep -r "\"@egos/$pkg\"" packages/*/package.json 2>/dev/null | wc -l
done
```

A package with 0 consumers that has been in the repo for >30 days without a linked open task is a candidate for archival.

---

### Check 6 — OPERATOR_MAP.md freshness

Read `docs/OPERATOR_MAP.md`. Ask:
- Is the "What We Are Building" section still accurate?
- Are the "Live Surfaces" still live?
- Is the "What's Blocked" list still current?
- Is the decision log recent (last entry ≤30 days)?

Update immediately if any is stale.

---

## Output

After the gate, write one paragraph in `docs/_current_handoffs/<date>-clarity-review.md`:

```markdown
## Clarity Review — <date>
- EGOS in one sentence: <sentence>
- TASKS.md: <N> lines, <N> open, <N> archived this review
- Governance docs: <N> total, <N> archived
- Agents: <N> active, <N> archived
- Dead packages: none / <list>
- OPERATOR_MAP: updated / current
- Overall: CLEAN / PRUNED / NEEDS_ATTENTION
```

---

*Maintained by: EGOS Kernel*
*Related: EGOS-121, docs/OPERATOR_MAP.md, TASKS.md, docs/governance/*
