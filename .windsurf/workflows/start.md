---
description: start workflow
---
----|---------|----------|
| Vercel usage | > 50% | > 75% (STOP) |
| Supabase DB | > 500 MB | > 2 GB (EMERGENCY) |

## 8. Tooling Session Check (MANDATORY)

The agent MUST verify these before implementation work:

| Tool | Check command | Required? | Default |
|------|--------------|-----------|--------|
| Gem Hunter SecOps | `ls -t docs/gem-hunter/secops-*.md 2>/dev/null \| xargs grep -l UNMITIGATED` | YES (BLOCKING) | Must mitigate CVEs first |
| Codex | `codex --version` | MODERATE+ tasks | `codex review --uncommitted` |
| Codex cloud | `codex cloud list` | If pending tasks exist | Inspect before new work |
| Alibaba | `.env` has `ALIBABA_DASHSCOPE_API_KEY` | Yes | `alibaba:qwen-plus` |
| Session guard | `bun run session:guard` | Only if this repo exposes it | Else use `bun run governance:check` + `bun run agent:lint` |
| Gem Hunter | `ls -t docs/gem-hunter/gems-*.md 2>/dev/null \| head -1` | Research sessions in repos that ship Gem Hunter | Suggest if > 7 days old |
| Report Generator | `ls -t docs/reports/report-*.html 2>/dev/null \| head -1` | Research sessions in repos that ship report generation | `bun agent:run report-generator --exec` |

Rules:

- **[NEW] SecOps Gate**: If a critical zero-day is found in `docs/gem-hunter/secops-*.md`, the agent MUST abort the start and instruct the user to mitigate the CVE immediately.
- Codex runs in a **parallel terminal**, NEVER in main chat
- Codex NEVER owns SSOT; it reviews under human/Cascade supervision
- Alibaba is the preferred orchestrator when configured
- If Alibaba is not configured, the agent MUST say `unavailable` and MUST NOT claim `alibaba:qwen-plus` is active
- Kernel repos may not expose `session:guard`, `docs/gem-hunter`, or `docs/reports`; treat them as optional surfaces, not activation blockers

## 9. Output Briefing

Present to user:

- **Security Status:** Critical active CVEs or Clean Network
- **Rules:** Version + mandamento count + orchestration status
- **Tasks:** P0 blockers → P1 sprint → P2 backlog (counts)
- **Handoff:** Last session summary (1-2 lines)
- **Recent commits:** Last 5 commits
- **Meta-prompts:** Count loaded + active triggers
- **Codex:** Availability + pending cloud tasks + chosen mode (cloud vs local read-only)
- **Codex Limitations:** explicitly disclose lane constraints (non-interactive defaults, browser-tool dependency, possible ephemeral `~/.egos` state)
- **Alibaba:** Availability + chosen orchestrator provider/model
- **Research:** Latest gem-hunter/report state or `N/A` for kernel repos without those surfaces
- **Orchestration:** "Pipeline active. Refinery ready. Gate threshold: 75."
- **Agent Signature:** confirm signature contract loaded and enforced on every operational message
- **Git Provenance:** confirm signature footer includes repo/branch/commit/push-remote fields for Codex, Antigravity, and Google AI Studio lanes

---

## File Existence Check

Required (flag if missing): `AGENTS.md`, `TASKS.md`, `docs/CAPABILITY_REGISTRY.md`, `.windsurfrules`, `.guarani/PREFERENCES.md`, `.guarani/IDENTITY.md`, `.guarani/orchestration/PIPELINE.md`, `.guarani/orchestration/GATES.md`, `.guarani/orchestration/QUESTION_BANK.md`, `.guarani/orchestration/DOMAIN_RULES.md`, `.guarani/refinery/classifier.md`, `.guarani/refinery/interrogators/*.md`, `.guarani/preprocessor.md`, `.guarani/prompts/PROMPT_SYSTEM.md`, `.guarani/prompts/triggers.json`, `docs/SYSTEM_MAP.md`.

For leaf repos, missing required files MUST produce both: (1) an explicit drift note in the `/start` briefing, and (2) a canonical fallback load when a verified upstream source exists.

Optional: `.guarani/philosophy/TSUN_CHA_PROTOCOL.md`, `.guarani/MCP_ORCHESTRATION_GUIDE.md`, `.guarani/DESIGN_STANDARDS.md`.

---

## 10. Agent Signature Activation (MANDATORY)

Load and enforce:
- `.guarani/standards/AGENT_MESSAGE_SIGNATURE_CONTRACT.md`

Propagation step (kernel governance change):
1. `bun run governance:sync:exec`
2. `bun run governance:check`

Delegation instruction to other agents/environments:
- "Activate `AGENT_MESSAGE_SIGNATURE_CONTRACT.md` locally and enforce signature footer on every operational reply."

---

*v5.5 — Added Capability Registry + SecOps CISA KEV Dependency scanning.*
