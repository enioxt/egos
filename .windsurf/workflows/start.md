---
description: start workflow
---

## 1. Mandatory activation sequence

Run, in order:

1. `bun run activation:check`
2. `bun run governance:check`
3. If the current repo exposes `session:guard`, run `bun run session:guard --json`
4. If the current repo exposes `start:audit`, run `bun run start:audit`
5. Else, if `/home/enio/egos-lab` exists, run `bun run start:audit` in `/home/enio/egos-lab` as the mesh-wide audit lane
6. For MODERATE+ tasks, run `codex --version` and `codex cloud list || true`
7. If the active repo is dirty, run `codex review --uncommitted || true`
8. Only with explicit approval for live/network verification, run `bun run session:guard --live` and `bun run start:audit:live`

## 2. Truth layers

`/start` must separate and compare four truths:

1. **Local truth** — current files and git state
2. **Documentation truth** — `AGENTS.md`, `TASKS.md`, `.windsurfrules`, `docs/SYSTEM_MAP.md`
3. **GitHub truth** — ahead/behind drift versus tracked remote
4. **Runtime truth** — public health or VPS-facing checks when live mode is approved

## 3. Required output briefing

The activation briefing must present:

- Security/runtime status
- Dirty repos, ahead/behind repos, and missing SSOT files
- Latest handoff and recent commit posture
- Codex availability + chosen lane
- Alibaba availability + chosen model/provider
- AI reconciliation summary when live mode runs
- Recommended next actions in priority order

## 4. Rules

- Codex runs in a parallel lane and never owns SSOT
- Alibaba is the preferred reconciliation model when configured
- If Alibaba is unavailable, the briefing must say `unavailable`
- If a repo is dirty or ahead of remote, `/start` must flag it explicitly
- If a required SSOT file is missing, `/start` must report drift explicitly

## 5. Canonical commands

- Fast mesh audit: `bun run start:audit` (or run it from `/home/enio/egos-lab` if absent locally)
- Live + AI audit: `bun run start:audit:live`
- Security gate: `bun run session:guard --live`

---

*v6.0 — Added mesh-wide truth audit, fallback to egos-lab startup audit, and explicit local/docs/github/runtime reconciliation contract.*
