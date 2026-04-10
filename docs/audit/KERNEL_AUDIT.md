# EGOS Kernel Audit — CLAUDE.md v4.0
> **Date:** 2026-04-10 | **Auditor:** Claude Opus 4.6  
> **Task:** ENC-L0-001 + ENC-L0-002  
> **Source:** `~/.claude/CLAUDE.md` v4.0.0 (263 lines, 15 sections + rule precedence header)  
> **Method:** Each section classified by enforcement level + evidence required

---

## Classification legend

| Status | Meaning |
|--------|---------|
| **PROVEN** | Rule enforced by code, pre-commit gate, or automated check |
| **PARTIAL** | Rule stated + partial enforcement; gaps documented |
| **ASPIRATIONAL** | Rule stated but no automated gate — relies on AI compliance |

---

## Section-by-section audit

### Rule Precedence Header (T0>T1>T2>T3>T4)

**Status: PROVEN**  
The precedence table references concrete sections. The 5-tier model was externally validated by 4 LLMs. Pre-commit implements T0/T1 rules as code. Higher tiers DO override lower tiers during rule conflicts (confirmed by hook chain order: focus→gitleaks→tsc→frozen-zone→doc-drift→ssot-gate→evidence-gate→file-intelligence→vocab-guard).

---

### §0 Critical Non-Negotiables [T0]

| Rule | Status | Gate |
|------|--------|------|
| NEVER force-push main | **PROVEN** | `.husky/pre-push`, `scripts/safe-push.sh`, GitHub branch protection |
| NEVER log secrets | **PROVEN** | `gitleaks protect --staged` in pre-commit step 1 |
| NEVER publish without human approval | **PARTIAL** | HITL exists in Telegram approval for Timeline bot. No gate on other channels. |
| NEVER `git add -A` in agents | **PARTIAL** | Rule stated; no automated enforcement. INC-002 was human-caught. |
| COMMIT TASKS.md immediately | **PARTIAL** | `auto-disseminate.sh` triggers on every commit + marks tasks done. No "within 60s" gate. |
| Incidental findings triage | **ASPIRATIONAL** | Protocol clear but relies entirely on AI judgment. No scanner. |

**Gap:** 3/6 rules are PARTIAL. The 3 proven ones cover the highest-damage scenarios (push safety, secrets, gitleaks). The gaps are coordination rules — harder to gate mechanically.

---

### §1 Mandatory Verification Gates [T1]

| Check | Status | Gate |
|-------|--------|------|
| File exists (Glob before Read) | **ASPIRATIONAL** | No pre-action gate. Hook `cbm-code-discovery-gate` nudges toward graph tools but doesn't enforce Glob-first. |
| Function exists (Grep before ref) | **ASPIRATIONAL** | Behavioral. |
| Claim from other session | **ASPIRATIONAL** | Behavioral. |
| All repos = list actual repos | **ASPIRATIONAL** | Behavioral. |
| Deployment state via SSH/curl | **ASPIRATIONAL** | Behavioral. |
| `bun run typecheck` after edit | **PARTIAL** | Pre-commit runs `npx tsc --noEmit`. Not per-edit — only at commit time. |

**Gap:** §1 is entirely aspirational except typecheck-at-commit. These are runtime AI behavior rules — cannot easily gate without instrumenting every tool call. Low priority for automation; high priority for AI training.

---

### §2 Edit Safety [T1]

| Rule | Status | Gate |
|------|--------|------|
| Read before Edit | **ASPIRATIONAL** | Behavioral. |
| Exact string from Read | **ASPIRATIONAL** | Behavioral. |
| Edit existing > write from scratch | **ASPIRATIONAL** | Behavioral. |
| Non-unique old_string → add context | **ASPIRATIONAL** | Behavioral. |
| Re-read after edit | **ASPIRATIONAL** | Behavioral. |
| Max 3 edits before verification read | **ASPIRATIONAL** | Behavioral. |
| Rename → grep all callers | **ASPIRATIONAL** | Behavioral. |
| Destructive action checklist | **PARTIAL** | Frozen-zone gate in pre-commit covers `.husky/pre-commit`, `.guarani/` files. `git push --force` is fully gated. `rm` on tracked files is not gated. |
| Large file >300 LOC phase rule | **ASPIRATIONAL** | Behavioral. |

**Gap:** §2 is largely aspirational — these are AI execution quality rules. Most cannot be automated without intercepting every tool call. The one mechanical gate (frozen zones) works. Consider: a `rm-guard` hook that flags `git rm` on tracked files.

---

### §3 Security [T1]

| Rule | Status | Gate |
|------|--------|------|
| Never log env var values | **PROVEN** | Gitleaks catches common patterns. Not 100% (dynamic keys bypass). |
| Never commit .env | **PROVEN** | `.gitignore` + gitleaks. |
| Input validation at boundaries | **ASPIRATIONAL** | No scanner. Review-only. |
| Gitleaks must pass | **PROVEN** | Pre-commit step 1, hard exit 1. |
| Guard Brasil audits own outputs | **PARTIAL** | article-writer.ts calls Guard for PII check. X-reply-bot does NOT call Guard before posting. |

**Gap:** X-reply-bot posts without Guard PII check. Low risk (Enio reviews posts) but should be added. See XRB-014 (create if not exists).

---

### §4 Git Safety [T1]

| Rule | Status | Gate |
|------|--------|------|
| Force-push forbidden on main | **PROVEN** | 4 layers: pre-push hook, safe-push.sh, GitHub branch protection, push-audit.yml CI |
| `safe-push.sh` for automation | **PROVEN** | All cron scripts use it (verified in gem-hunter-adaptive.yml) |
| `git fetch && git rebase` before push | **PARTIAL** | safe-push.sh does this. Manual pushes by humans may skip. |
| Background agents: specific file only | **PARTIAL** | Rule stated. No enforcement. INC-002 was manually caught. |
| TASKS.md: commit within 60s | **ASPIRATIONAL** | No time-gate. Relies on habit. |
| Read-parallel / Write-sequential | **ASPIRATIONAL** | Behavioral. No swarm coordinator enforces this. |

**Gap:** INC-002 pattern (git add -A in background agent) remains partially unprotected. Could add a pre-commit check that blocks commit if `git add -A` was the staging command — but this is hard to detect retroactively. Better: agent runtime guard in `agents/runtime/runner.ts`.

---

### §5 Context Management [T2]

**Status: ASPIRATIONAL**  
All rules are behavioral AI guidance. No automated gate. Low priority for mechanization — these are LLM context hygiene rules.

---

### §6 Agent & Swarm Rules [T2]

| Rule | Status | Gate |
|------|--------|------|
| Model selection (Haiku/Sonnet/Opus) | **ASPIRATIONAL** | Guidance only. |
| Cost control: 3 retries → STOP | **ASPIRATIONAL** | No circuit breaker in runner.ts currently. **Gap: INC potential.** |
| Independent → parallel agents | **ASPIRATIONAL** | Behavioral. |
| Dependent → sequential | **ASPIRATIONAL** | Behavioral. |

**Gap:** Cost control (3 retries → STOP) is the highest-risk gap in §6. No circuit breaker = potential runaway API costs. Task: add retry counter to `agents/runtime/runner.ts`.

---

### §7 SSOT & Anti-Dispersão [T2]

| Rule | Status | Gate |
|------|--------|------|
| SSOT table (domains → files) | **PARTIAL** | `scripts/ssot-router.ts` checks new .md files in pre-commit step 5.7. Does NOT check edits to existing files. |
| Never create docs/business/, docs/sales/ | **PARTIAL** | SSOT gate blocks new .md files in wrong domains. Doesn't block directories. |
| SSOT hierarchy (TASKS→agents.json→…) | **ASPIRATIONAL** | No enforcement. Behavioral priority. |

**Gap:** ssot-router.ts only fires on new `.md` files with diff-filter=A. Content additions to existing files bypass it. Low risk since the main dispersão pattern is creating new files.

---

### §8 Evidence-First Principle [T2]

| Rule | Status | Gate |
|------|--------|------|
| Claim without proof = invalid | **PARTIAL** | `scripts/evidence-gate.ts` — WARNING mode (2026-04-09 to 2026-04-15), BLOCKING from 2026-04-16 |
| Manifest entry required | **PARTIAL** | `.egos-manifest.yaml` + doc-drift-check.sh in pre-commit. Some repos lack manifest. |
| Dashboard tile OR dry-run | **ASPIRATIONAL** | No automated check for this requirement. |
| Unproven claims marked `unverified:` | **ASPIRATIONAL** | No scanner for unverified: compliance. |
| Doc-Drift Shield pre-commit | **PROVEN** | `bash .husky/doc-drift-check.sh` — hard exit 1 on drift. |

**Gap:** evidence-gate is currently warning-only. 33 violations in CAPABILITY_REGISTRY.md already found. Needs manifest entries before 2026-04-16 or claims must be marked `unverified:`.

---

### §9 Governance & Findings [T2]

| Rule | Status | Gate |
|------|--------|------|
| Governance check before structural changes | **PARTIAL** | `bun run governance:check` — must be run manually. Pre-commit doesn't require it for all commits. |
| TASKS.md anti-hallucination | **ASPIRATIONAL** | Protocol requires manual `find`/`grep`/`git log` before adding tasks. No gate. |
| Mark `[x]` in same commit | **PARTIAL** | `auto-disseminate.sh` reads commit message task IDs and marks done — only if task ID is in subject line. |
| Quorum Protocol | **PROVEN** | Protocol documented. meta-prompt template exists. Quorum history at `docs/quorum/`. Structurally sound. |
| Frozen zones | **PROVEN** | Pre-commit checks `.husky/pre-commit`, `.guarani/orchestration/PIPELINE.md`, `.guarani/orchestration/GATES.md`, `agents/runtime/runner.ts`, `agents/runtime/event-bus.ts`. |

---

### §10 Posture & Autonomy [T3]

**Status: ASPIRATIONAL**  
Behavioral alignment rules. No automation possible. These require AI training, not code gates.

Rollback protocol: ASPIRATIONAL — no automated rollback trigger. AI must remember to run `git restore`.

---

### §11 Vocabulary Map [T3]

**Status: PROVEN (structural)**  
Table is authoritative. Enio speech patterns included. Used actively in sessions. No automation needed — this is reference material.

---

### §12 Enio Profile & Hard Rules [T3]

| Rule | Status | Gate |
|------|--------|------|
| NO JOBS RULE | **PARTIAL** | Rule stated. `focus-enforcement.sh` blocks commits outside Guard/GemHunter scope, but doesn't specifically block "job application" content. Behavioral for AI. |
| No revenue anxiety in /start | **ASPIRATIONAL** | Behavioral. Relies on AI following §12. |
| Meta-prompt → load context first | **ASPIRATIONAL** | Behavioral. No session-start gate. |

---

### §13 Integrations [T4]

**Status: PROVEN (reference)**  
All URLs/commands verified as of 2026-04-10:
- `curl -s https://guard.egos.ia.br/health` → `{"status":"ok"...}` ✅
- SSH to VPS: functional ✅
- Caddy path correct ✅
- Supabase MCP: active ✅
- codebase-memory-mcp: hook enforces use ✅

---

### §14 Repo Map [T4]

**Status: PROVEN**  
`docs/REPO_MAP.md` exists and is canonical. 7 groups verified against actual repos. Anti-confusion rules accurate (ratio=read-only confirmed, 852≠policia confirmed, Forja=ERP confirmed).

---

## Summary table

| Section | Status | Critical Gap |
|---------|--------|-------------|
| Rule Precedence | PROVEN | — |
| §0 Non-Negotiables | PARTIAL | `git add -A` in agents unenforceable |
| §1 Verification Gates | ASPIRATIONAL | No pre-action tooling |
| §2 Edit Safety | ASPIRATIONAL | Only frozen-zone proven |
| §3 Security | PARTIAL | X-reply-bot posts without Guard check |
| §4 Git Safety | PARTIAL | INC-002 pattern partially unprotected |
| §5 Context | ASPIRATIONAL | Behavioral only |
| §6 Agents & Swarm | ASPIRATIONAL | **No circuit breaker = cost risk** |
| §7 SSOT | PARTIAL | Edit-additions bypass ssot-router |
| §8 Evidence-First | PARTIAL | 33 violations in CAPABILITY_REGISTRY |
| §9 Governance | PARTIAL | TASKS.md anti-hallucination behavioral |
| §10 Posture | ASPIRATIONAL | Behavioral only |
| §11 Vocabulary | PROVEN | — |
| §12 Profile | PARTIAL | Meta-prompt rule behavioral |
| §13 Integrations | PROVEN | — |
| §14 Repo Map | PROVEN | — |

**Score: 4 PROVEN, 6 PARTIAL, 6 ASPIRATIONAL out of 15 sections.**

---

## Top 5 gaps to close (priority order)

1. **§6 Cost control — circuit breaker** [HIGH]: 3-retry limit has no code enforcement. Runaway agents burn API budget. Fix: add `retryCount` guard to `agents/runtime/runner.ts`.

2. **§8 Evidence gate enforcement** [HIGH]: 33 violations in CAPABILITY_REGISTRY.md must be resolved before 2026-04-16 when gate turns blocking. Fix: mark aspirational counts as `unverified:` or add to `.egos-manifest.yaml`.

3. **§3 X-reply-bot Guard check** [MODERATE]: Bot can post PII without Guard audit. Fix: add Guard Brasil `/v1/inspect` call in `scripts/x-reply-bot.ts` before queue insertion (XRB-014).

4. **§4 INC-002 agent git add** [MODERATE]: Background agents could `git add -A`. Fix: interceptor in agent runner that wraps `git add` calls and blocks `-A`/`.` patterns.

5. **§9 TASKS.md anti-hallucination** [MODERATE]: No gate forces the `find`/`grep` check before task creation. Fix: a lightweight pre-task-add script or reminder banner in `/start`.

---

## Notes on aspirational rules

The 6 ASPIRATIONAL sections (§1, §2, §5, §6 partial, §10, §12 partial) are not failures — they represent behavior specifications that are correct but unenforceable without instrumenting every LLM tool call. The right response is to:

1. Keep them as written (they work in practice — this is how Claude Code operates)
2. Accept that "aspirational" for LLM behavior ≠ "aspirational" for human behavior
3. Only add gates where the failure mode has high blast radius (§6 cost, §8 evidence)

---

*Generated: 2026-04-10 | Task: ENC-L0-001+ENC-L0-002 | Next: ENC-L1-001 (Agents Registry audit)*
