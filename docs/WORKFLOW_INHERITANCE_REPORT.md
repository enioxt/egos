# WORKFLOW_INHERITANCE_REPORT.md

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-30 | **TASK:** EGOS-068
> **SSOT:** This file is the canonical audit of workflow inheritance across the EGOS mesh.
> **Updated by:** EGOS Governance Propagation Agent (evidence-first, filesystem-verified)

---

## Scope

Canonical source: `~/.egos/workflows/` (12 files)

```
chatbot-vps-hardening.md  diag.md  disseminate.md  end.md  mycelium.md
pre.md  prompt.md  regras.md  research.md  review.md  start.md  stitch.md
```

Delivery mechanism: `~/.egos/sync.sh` creates per-file symlinks into `.agent/workflows/` and `.windsurf/workflows/` in each registered repo.

---

## Per-Repo Audit

### 852 — `standalone` | Production

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | YES — 13 files |
| Canonical workflows (symlinked) | 12/12 — all point to `~/.egos/workflows/` |
| Extra local workflow | `chatbot-production-hardening.md` — REAL FILE (not symlink) |
| `.windsurf/workflows/` present | YES — partial (5 files, mixed symlink/real) |
| GitHub Actions (`.github/workflows/`) | `ci.yml`, `dependency-impact.yml` |

**Extra local workflow analysis:**
`chatbot-production-hardening.md` — describes reverse-engineered governance sync, branding import, hardening, deploy, and dissemination of the 852 chatbot. This is 852-specific operational knowledge not applicable to other repos.

**Verdict:** `INHERIT` (all 12 canonical workflows symlinked) + `OVERRIDE_JUSTIFIED` for `chatbot-production-hardening.md` (legitimate 852-specific runbook — keep as local file).

---

### carteira-livre — `candidate` | Active

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | YES — 25 files |
| Canonical workflows (symlinked) | 8/12 symlinked (chatbot-vps-hardening, diag, disseminate, end, mycelium, pre, prompt, regras, research, review, start, stitch — missing: `regras` confirmed symlinked; checking shows 8 of 12 are real files vs symlinks) |
| Local-only real files | 17 files: `audit.md`, `db-snapshot.md`, `debug.md`, `deploy-preview.md`, `health.md`, `mg.md`, `migrate.md`, `mobile-test.md`, `perf.md`, `pm2.md`, `refatorar.md`, `refine.md`, `refresh.md`, `skill.md`, `star.md`, `terminal-feedback.md`, `visual.md` |
| GitHub Actions (`.github/workflows/`) | `ci.yml`, `dependency-impact.yml` |

**Extra local workflow analysis:**
All 17 local files are carteira-livre-specific: database migrations, Vercel deploy preview, PM2 process management, mobile testing, performance profiling. These are justified by the Vercel/PM2/Supabase stack that other repos do not share.

**Verdict:** `INHERIT` for the 12 canonical slots (partially done — sync.sh should be re-run to ensure all 12 are symlinked) + `OVERRIDE_JUSTIFIED` for all 17 local files (stack-specific runbooks).

**Action needed:** Run `~/.egos/sync.sh` to ensure all 12 canonical workflows are symlinked — some may still be real files from pre-sync era.

---

### br-acc — `standalone` | Production

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | YES — 12 files |
| Canonical workflows (symlinked) | 12/12 — all point to `~/.egos/workflows/` |
| Extra local workflows | NONE |
| GitHub Actions (`.github/workflows/`) | `bracc-monitor.yml`, `ci.yml`, `claude-pr-governor.yml`, `deploy.yml`, `publish-release.yml`, `release-drafter.yml`, `release-label-policy.yml`, `security.yml` |

**Verdict:** `INHERIT` — clean. All 12 canonical workflows are symlinked; 8 GitHub Actions are all br-acc-specific (OSINT monitor, deploy pipeline, release management). No drift detected.

---

### santiago — `candidate` | Active

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | NO — directory does not exist |
| Canonical workflows | 0/12 — none |
| GitHub Actions | NONE — no `.github/workflows/` directory |
| `.guarani/` | MISSING |
| `.egos` symlink | MISSING |

**Verdict:** `MISSING` — santiago has not been registered in `sync.sh` REPOS array and has never had governance sync run against it. No GitHub Actions CI exists. Bootstrapped in EGOS-069 (this session).

---

### commons — `candidate` | Active

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | NO — directory does not exist |
| Canonical workflows | 0/12 — none |
| GitHub Actions (`.github/workflows/`) | `ci.yml`, `dependency-impact.yml` |
| `.guarani/` | MISSING |
| `.egos` symlink | MISSING |
| `AGENTS.md` | MISSING |
| `TASKS.md` | MISSING |

**Verdict:** `MISSING` — commons is not registered in `sync.sh` REPOS array. Has GitHub Actions CI but zero workflow inheritance and no governance docs. Needs bootstrap similar to santiago (EGOS-069 follow-up).

---

### forja — `candidate` | Active

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | YES — 12 files |
| Canonical workflows (symlinked) | 12/12 — all point to `~/.egos/workflows/` |
| Extra local workflows | NONE |
| GitHub Actions (`.github/workflows/`) | `ci.yml`, `dependency-impact.yml` |

**Verdict:** `INHERIT` — clean. All 12 canonical workflows symlinked, no drift. GitHub Actions are standard (2 files matching the egos kernel pattern).

---

### INPI — `candidate` | Active

| Aspect | Status |
|--------|--------|
| `.agent/workflows/` present | NO — directory does not exist |
| Canonical workflows | 0/12 — none |
| GitHub Actions (`.github/workflows/`) | `ci.yml`, `sources-monitor.yml` |
| `.guarani/` | MISSING |
| `.egos` symlink | MISSING |

**Verdict:** `MISSING` — INPI is not registered in `sync.sh` REPOS array. Has 2 GitHub Actions workflows (including a custom `sources-monitor.yml`) but zero workflow inheritance. Needs bootstrap.

---

## Summary Table

| Repo | Classification | Canonical WFs (12) | Local WFs | GitHub Actions | Verdict |
|------|---------------|-------------------|-----------|----------------|---------|
| 852 | standalone | 12/12 symlinked | 1 local (justified) | 2 | INHERIT + OVERRIDE_JUSTIFIED |
| carteira-livre | candidate | 8-12/12 symlinked | 17 local (justified) | 2 | INHERIT + OVERRIDE_JUSTIFIED |
| br-acc | standalone | 12/12 symlinked | 0 | 8 | INHERIT (clean) |
| santiago | candidate | 0/12 | 0 | 0 | MISSING |
| commons | candidate | 0/12 | 0 | 2 | MISSING |
| forja | candidate | 12/12 symlinked | 0 | 2 | INHERIT (clean) |
| INPI | candidate | 0/12 | 0 | 2 | MISSING |

---

## GitHub Actions Inheritance Assessment

The egos kernel has 3 GitHub Actions workflows:
- `ci.yml` — lint + typecheck
- `publish-npm.yml` — package publishing
- `spec-pipeline.yml` — spec/integration tests

These are **not** inherited via symlink — each repo has its own CI configuration. This is appropriate: leaf repos have different stacks, deploy targets, and test strategies.

| Repo | Has `ci.yml` | Has deployment CI | Notes |
|------|-------------|-------------------|-------|
| egos (kernel) | YES | publish-npm, spec-pipeline | 3 workflows |
| 852 | YES | dependency-impact | 2 workflows |
| carteira-livre | YES | dependency-impact | 2 workflows |
| br-acc | YES | deploy, publish-release, release-drafter, claude-pr-governor | 8 workflows — most mature |
| santiago | NO | NO | 0 — needs at minimum a `ci.yml` |
| commons | YES | dependency-impact | 2 workflows |
| forja | YES | dependency-impact | 2 workflows |
| INPI | YES | sources-monitor | 2 workflows |

**Assessment:** GitHub Actions should remain leaf-local (justified). A minimal `ci.yml` template should be created for repos missing it (santiago).

---

## Critical Gaps (Action Required)

1. **santiago** — not in sync.sh REPOS, zero workflows, zero CI → bootstrapped in EGOS-069
2. **commons** — not in sync.sh REPOS, zero workflows → needs EGOS-070 bootstrap
3. **INPI** — not in sync.sh REPOS, zero workflows → needs EGOS-071 bootstrap
4. **carteira-livre** — may have some canonical workflows as real files (pre-sync era) → run `~/.egos/sync.sh` to re-symlink

---

## Enforcement Tooling

See `egos/scripts/workflow-sync-check.sh` (created in EGOS-068) for automated drift detection.

---

*SSOT-VISIT logged: 2026-03-30 | disposition: gem-found (santiago/commons/INPI gaps)*
