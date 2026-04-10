# CLARITY_REVIEW.md — EGOS-121

> **Version:** 1.0.0
> **Created:** 2026-03-30
> **Owner:** EGOS kernel governance
> **Trigger:** First Monday of each month | or `/clarity-review` manual trigger
> **Cron reminder:** See Section 5

A monthly ritual to prune complexity, kill zombie tasks, and keep the kernel coherent. The goal is NOT to do more — it is to ensure that what EGOS says it is matches what it actually does.

---

## 1. When

**Scheduled:** First Monday of each month, during the first session of the day.

**Manual trigger:** Run `/clarity-review` at any time when TASKS.md exceeds 500 lines, after a major feature push, or when the kernel feels drifted.

**Time budget:** 30–45 minutes maximum. If it takes longer, the system has too much complexity to review in a session — that is itself a finding.

---

## 2. Inputs

Read these files before answering the 5 clarity questions:

| Input | File | What to look for |
|-------|------|-----------------|
| Active tasks | `TASKS.md` | Open items, age, stale markers |
| System architecture | `docs/SYSTEM_MAP.md` | What surfaces are listed as active |
| Ecosystem classification | `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` | What is kernel/lab/standalone/archive |
| Agent registry | `AGENTS.md` | What agents are listed, which have evidence |
| Capability registry | `docs/CAPABILITY_REGISTRY.md` | What capabilities are claimed vs proven |

Do NOT read more than these 5 files before answering. The questions must be answerable from a cold start. If they aren't, that is a drift signal.

---

## 3. The 5 Clarity Questions

Answer each in 2 sentences or fewer. If you cannot, the kernel has drifted and the review must go longer.

### Q1: "What is EGOS in one sentence?"

Write one sentence. If it requires a second sentence to be accurate, the kernel has accumulated scope creep. The answer from the previous clarity review is the baseline — if it changed, explain why in one sentence.

*Baseline (2026-03-30):* "EGOS is a multi-agent governance kernel that orchestrates AI tools, enforces ethical policies, and manages knowledge across a constellation of product repos."

### Q2: "What are the 3 things EGOS does that nothing else does?"

List exactly 3. No more. These should be verifiable in code, not in docs.

If you list something and cannot point to a file that proves it, remove it from the list.

*Baseline (2026-03-30):*
1. ATRiAN ethical gate — axiom-based policy enforcer that runs before any LLM output ships (`packages/shared/src/atrian.ts`)
2. Cross-repo governance sync — single `.guarani/` propagates to all leaf repos via `scripts/governance-sync.sh`
3. Evidence-first reference graph — canonical topology map distinguishing code/runtime/plan evidence (`packages/shared/src/mycelium/reference-graph.ts`)

### Q3: "What should we delete this month?"

Find all TASKS.md entries where:
- The entry is older than 90 days (check dates in surrounding context or creation date)
- Status is still `[ ]` (not started)
- No sub-item has a `[/]` marker (no partial progress)

List each candidate with its EGOS-NNN. Then decide: archive, reassign to P3, or delete.

Rule: Any item that has been open for 90+ days with zero progress is **zombie work**. It should be archived or explicitly accepted as P3/someday.

### Q4: "What is generating revenue or real usage?"

List only surfaces with at least one of:
- A paying customer or active user session in the last 30 days
- A live API endpoint with confirmed external calls
- A running service with external traffic

Do not list planned revenue or potential usage. Be honest.

*Format:* `<surface>: <evidence>`

### Q5: "What is the next 30-day focus?"

Name ONE primary objective. Not three. Not a list. One. The rest goes to P2/P3.

This one objective must be:
- Specific (not "improve the system")
- Measurable (you will know when it is done)
- Connected to Q4 (it either protects existing revenue or creates the next revenue event)

---

## 4. Outputs

After answering the 5 questions:

### 4.1 Archive Stale Tasks

For each item identified in Q3:
- Move the entry from its current section to a new `## Archived (YYYY-MM)` section at the bottom of TASKS.md
- Add a comment: `<!-- archived: YYYY-MM-DD reason: 90d no progress -->`
- Do NOT delete — kept for audit trail

### 4.2 Update TASKS.md Version Line

Bump the version at the top of TASKS.md:
```
> **Version:** X.Y.Z | **Updated:** YYYY-MM-DD | **Clarity Review:** YYYY-MM-DD
```

### 4.3 Run `/disseminate`

After any decision made during the review (new P0, archived tasks, changed focus), run `/disseminate` to propagate decisions to `~/.egos/` and relevant handoff files.

### 4.4 Gate Check

TASKS.md MUST be under 500 lines after the review. If it exceeds 500 lines:
1. Archive all P3 items immediately
2. Archive all items older than 60 days with no progress
3. If still over 500 lines, flag it as a SYSTEM_MAP drift signal and add to Q3 for next review

---

## 5. Gate

**TASKS.md must be < 500 lines after every clarity review.**

This is a hard gate. If the review completes and TASKS.md is still >= 500 lines, the review is not done. Continue archiving until the gate passes.

```bash
# Check line count
wc -l /home/enio/egos/TASKS.md
```

---

## 6. Cron Reminder

Add this to your calendar or shell startup as a reminder. The cron itself does not run the review — it is a human-triggered ritual.

```bash
# Add to crontab: 0 9 1-7 * 1 = 9am on first Monday of each month
# This sends a reminder, not an automated execution
# 0 9 1-7 * 1 echo "EGOS Clarity Review due today. Run /clarity-review in Claude Code." | mail -s "EGOS Monthly Clarity Review" root@localhost
```

**Note:** The `/clarity-review` skill trigger is registered in `/home/enio/.egos/guarani/prompts/triggers.json` (see below). When you type "clarity review" or "/clarity-review" in any EGOS-aware session, this contract is the activated guide.

---

- [x] **EGOS-121** — Monthly clarity review gate defined (2026-03-30)
