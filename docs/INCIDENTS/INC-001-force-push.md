# INC-001 — Force-push to main by parallel agent

**Date:** 2026-04-06
**Severity:** P0 (data-loss class)
**Status:** Mitigated. Root-cause investigation pending.
**Reporter:** Enio (visual: "https://guard.egos.ia.br/landing aqui ainda nao vi mudancas")

## What happened

While Enio was running an interactive session that committed brand assets and reorganized GTM priorities, a parallel scheduled agent push rewrote `origin/main` and dropped 9 in-flight commits:

```
9ad26b0  chore(tasks): v2.37.0 — Dream Cycle DC-001..011, LLM-001..002
e5bdd00  feat(dream-cycle): Phase 1 — overnight log harvester + Supabase
ed19d81  feat(llm): Google AI Studio + Qwen 3.6 Plus free
74ea2c2  docs(handoff): P26 addendum
68754da  chore(tasks): v2.36.0 — P26 MCPs
5b5e3d1  docs(harvest): GTM patterns v3.5.0
1c23929  fix(hooks): pre-commit large-commit graceful TTY fallback
216676c  fix(focus): researcher-builder FORBIDDEN-list v2.0
d7221fb  docs(handoff): P26 addendum — MCPs/research/HARVEST dedup issue
```

The replacement tip was `5ed6706 chore(gem-hunter): adaptive run [2026-04-06]` (Gem Hunter Bot), with parent `00d7b8a feat(gem-hunter): pair study EGOS vs OpenHands — score 79/100` (author `Claude <noreply@anthropic.com>`).

The local `git fetch` reported `+ d7221fb...5ed6706 main -> origin/main (forced update)`, confirming non-fast-forward rewrite of the remote.

## Root cause (provisional)

The remote runner that produced `00d7b8a` and `5ed6706` had a stale checkout (no `git fetch` before push) and was therefore unaware of the 9 local-only commits. Its `git push` non-FF should have been rejected by GitHub, but no branch protection was configured, so the push was accepted, rewriting history.

The likely culprit is the **Code Intel + Security Audit** scheduled CCR job (Mon+Thu 1h42 BRT) — `00d7b8a` is timestamped `2026-04-06 05:44 UTC` (= 02:44 BRT), which falls in that window, and its author signature matches the CCR job convention (`Claude <noreply@anthropic.com>`). Confirmation requires checking the run history at https://claude.ai/code/scheduled.

The **Gem Hunter Adaptive** GitHub Action (`gem-hunter-adaptive.yml`) is a contributing factor: its `git push` step did not fetch+rebase before pushing, so once main moved underneath it, retries would either fail or (without protection) corrupt history.

## How recovery worked

1. `git fetch origin` (revealed the divergence)
2. `git merge origin/main --no-ff` (preserved both lineages)
3. Conflicts only in 4 auto-generated `docs/gem-hunter/` files → resolved with `--theirs`
4. Merge commit `1d1ef23` reunited the histories without losing any work
5. `git push origin main` succeeded as fast-forward

No data was lost. Local clone had all 9 dropped commits in its reflog (because they were committed locally before the remote rewrite).

## Mitigations applied (this session)

| # | Layer | What | Where |
|---|-------|------|-------|
| 1 | Local | `pre-push` hook blocks non-FF push to protected branches | `.husky/pre-push` |
| 2 | Server | GitHub branch protection: `allow_force_pushes=false`, `allow_deletions=false` | `gh api ... branches/main/protection` |
| 3 | CI | `gem-hunter-adaptive.yml` rewritten with fetch+rebase retry loop (3 attempts) | `.github/workflows/gem-hunter-adaptive.yml` |
| 4 | CI | `push-audit.yml` watches all pushes to protected branches, opens an issue + Telegram alert on `forced=true` | `.github/workflows/push-audit.yml` |
| 5 | Tooling | `scripts/safe-push.sh` — universal safe-push wrapper for all agents and scripts. Refuses `--force` without `EGOS_ALLOW_FORCE_PUSH=1`. | `scripts/safe-push.sh` |
| 6 | Doc | Hard rule added to `~/.claude/CLAUDE.md` §25 — "Never `git push --force` to main" | global |

## Mitigations pending (require human action)

- [ ] Confirm which CCR scheduled job did the push: visit https://claude.ai/code/scheduled, inspect runs around 2026-04-06 02:00–03:00 BRT, identify the one that touched git
- [ ] Edit that scheduled job's prompt to call `bash scripts/safe-push.sh main` instead of `git push`
- [ ] Edit the other 2 CCR jobs (Governance Drift Sentinel, Gem Hunter Adaptive) to use the same wrapper, even if they don't currently push
- [ ] Audit `.github/workflows/*.yml` for any other plain `git push` to main and route through `safe-push.sh`
- [ ] Add `EGOS_ALLOW_FORCE_PUSH` to repo secrets documentation, mark as "human-only, never automated"

## Lessons learned

1. **Server-side protection is the only enforcement that catches everything.** Local hooks don't run on remote runners. Branch protection rules (GitHub's `allow_force_pushes=false`) are the only universal block.
2. **Stale checkouts are a load-bearing risk.** Any agent that runs `git push` without `git fetch && git rebase` first can rewrite history blindly if protection is off.
3. **Multi-agent races are not theoretical.** During THIS recovery session, another scheduled job committed `7bdc35f` while we were merging — second concurrent process within a 30-minute window. The fact that it landed cleanly (fast-forward) was luck, not design.
4. **Reflog is the safety net.** Local commits survive remote rewrites because git keeps them in the reflog for ~30 days. Always recover from local before assuming data loss.

## Verification

After mitigations, run:

```bash
# Pre-push hook fires correctly
echo | bash .husky/pre-push origin git@github.com:enioxt/egos.git 2>&1 | head

# Branch protection still active
gh api repos/enioxt/egos/branches/main/protection \
  -q '.allow_force_pushes.enabled,.allow_deletions.enabled'
# expected: false, false

# Safe-push wrapper rejects --force without env var
bash scripts/safe-push.sh main --force 2>&1 | head
# expected: exit 3, "Refusing"
```
