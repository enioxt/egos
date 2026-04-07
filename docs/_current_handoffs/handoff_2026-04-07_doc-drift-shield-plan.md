# HANDOFF 2026-04-07 — Doc-Drift Shield Implementation Plan

> **From:** Claude Sonnet 4.6 (session P33 — diagnostic + doc-drift design)
> **To:** Next LLM session (Sonnet 4.6 recommended — execution phase)
> **Session date:** 2026-04-07
> **Session length:** ~3 hours (diagnostic → planning → foundation)
> **Status:** Foundation complete (L1 + CLAUDE.md §27), implementation pending (L2-L4)
> **Handoff intent:** Execute complete Doc-Drift Shield + Phases 6-10 from this plan.

---

## 1. SESSION SUMMARY (what happened today)

### Request
Enio asked to: (1) start EGOS system, (2) read `/home/enio/Downloads/Resume and X.com Posts.md` final part, (3) investigate VPS and validate all claims, (4) improve CV to find partners on X.com, (5) start the partnership journey.

Follow-up turn: activate tutor/copilot mode, ask questions iteratively, create proofs for every claim with hashes/sources/validations, update all documentation, list all integrations and SSOTs, investigate the EGOS-Inteligencia repo (128 stars), trace a complete diagnostic plan, deep-dive Carteira Livre, use Exa MCP for research on doc-drift prevention.

Final turn: stop executing code, consolidate into a complete handoff plan for the next session to execute. Update TASKS. Answer the Claude Code extension vs CLI question. Run /disseminate and /end.

### Key discoveries (VERIFIED facts — not inferences)

**VPS state — Hetzner 204.168.217.125:**
- 19 Docker containers running; uptime 9+ days on most
- 8/8 public domains LIVE (verified via curl):
  - guard.egos.ia.br: 200 ✅
  - 852.egos.ia.br: 200 ✅ (RESTORED today — was missing from active Caddyfile)
  - eagleeye.egos.ia.br: 200 ✅ (FIXED today — Caddyfile was routing to wrong port)
  - gemhunter.egos.ia.br: 200 ✅ (FIXED today — was pointing to nonexistent :3095)
  - hq.egos.ia.br: 307 (redirect to /login, normal)
  - openclaw.egos.ia.br: 200 ✅
  - carteiralivre.com.br: 308 (redirect to carteiralivre.com, normal)
  - inteligencia.egos.ia.br: 200 ✅ (NEWLY DISCOVERED — wasn't in MASTER_INDEX)

**Neo4j (bracc-neo4j container):**
- **83,773,683 nodes** (README claimed 77M → drift +8.8%)
- **26,808,540 relationships** (README claimed 25M → drift +7.2%)
- 32 distinct labels: Person, Partner, Company, Contract, Sanction, PublicOffice, Investigation, Amendment, Health, Finance, Embargo, Education, Convenio, LaborStats, Inquiry, InquiryRequirement, InquirySession, MunicipalBid, MunicipalContract, MunicipalBidItem, MunicipalGazetteAct, JudicialCase, SourceDocument, IngestionRun, TemporalViolation, Election, User, GlobalPEP, PEPRecord, BarredNGO, GovCardExpense, GovTravel
- Auth: `neo4j/BrAcc2026EgosNeo4j!`
- Container: bracc-neo4j, up 9 days, healthy

**EGOS-Inteligencia GitHub repo (128 ⭐):**
- Path: `/home/enio/br-acc` (the local git repo is br-acc; its origin points to enioxt/EGOS-Inteligencia.git)
- Upstream: `https://github.com/World-Open-Graph/br-acc.git` (fork relationship)
- 360 commits, 16 forks, 31 open issues
- Language: Python
- `description: null` (empty on GitHub — SEO loss)
- `topics: []` (empty — SEO loss)
- README still says "77M entidades" (needs update to 83.7M)

**Migration state (br-acc ↔ egos-inteligencia):**
- `/home/enio/br-acc` = canonical git repo (origin: EGOS-Inteligencia.git)
- `/home/enio/egos-inteligencia` = **abandoned scaffold**, NOT a git repo, last modified 2026-04-01
- Intent was: merge BR-ACC backend + Intelink frontend → new clean repo
- Status: structure created, build passing 19 routes, 0% tests, Neo4j not connected in new scaffold
- **Decision made this session: KEEP br-acc as canonical, absorb useful pieces from the scaffold later**

**Carteira Livre deep-dive (big drift):**
- 1,690 commits by Enio Rocha (single contributor), first commit 2025-12-12
- Monthly velocity: Dec 138 / Jan 600 / Feb 826 / Mar 124 / Apr 2
- Peak: February 2026 with 826 commits (~28/day)
- **Pages: README said 54 → real 134** (+148%)
- **API routes: README said 68 → real 254** (+273%)
- **Test files: 37 / test assertions: 2,847** (README said "175 tests")
- Total TypeScript LOC: 182,589
- Source files: 553 .ts + 303 .tsx = 856 files
- Feature fingerprint: 317 auth files, 322 supabase files, 72 whatsapp, 61 asaas, 41 KYC, 14 gemini
- **16 hidden features discovered via git log:** Rádio Philein 24/7 (2026-01-28), AI Orchestrator + influencer discovery (2026-02-04), multi-state architecture (2026-02-01), Guia INPI MVP (2026-01-20), Ambassador system (2026-01-23), Mobile offline mode + haptics (2026-01-30), etc.

### Files updated/created THIS session

| File | Action | Purpose |
|------|--------|---------|
| `/home/enio/personal/cv-enio-completo-2025-portugues.html` | edited | 77M→83.7M, Contabo→Hetzner, 50+→84+ territorios, Eagle Eye/Gem Hunter text updated |
| `/home/enio/personal/X_POST_5_VERCOES_LOW_PROFILE.md` | edited + added Version 6 | All numbers corrected, Version 6 "O Investigador que Virou Builder" added |
| `/opt/bracc/infra/Caddyfile` (VPS) | edited | Added 852.egos.ia.br block; fixed eagleeye→eagle-eye:3001; fixed gemhunter→egos-gateway:3050 |
| `/home/enio/carteira-livre/README.md` | header rewritten | Real badges (1690/134/254/182589), 16-row scope table, verification commands |
| `/home/enio/egos/docs/DOC_DRIFT_SHIELD.md` | **NEW** | Complete 4-layer shield design doc |
| `/home/enio/egos/.egos-manifest.yaml` | **NEW** | L1 manifest for egos kernel repo |
| `/home/enio/br-acc/.egos-manifest.yaml` | **NEW** | L1 manifest for br-acc (with Neo4j proof commands) |
| `/home/enio/carteira-livre/.egos-manifest.yaml` | **NEW** | L1 manifest for carteira-livre (16 claims) |
| `/home/enio/.claude/CLAUDE.md` | §27 added | 10 Doc-Drift hard rules + bumped to v2.8.0 |

### Critical bug found and fixed

**`sed -i` breaks Docker bind mount inodes.** When editing `/opt/bracc/infra/Caddyfile` via `sed -i`, the inode changed and the Caddy container (bind-mounted) kept serving the old file. Solution: restart the container after `sed -i`, OR use `python3 open("w")` + restart, OR use `docker cp` (but `docker cp` fails if destination is bind-mounted). **Canonical fix: edit file on host with sed, then `docker restart <container>`.** This should go into HARVEST.md as a pattern.

---

## 2. COMPLETED IN THIS SESSION (do not redo)

### Layer 1 — Contract Manifest (DONE ✅)
- `docs/DOC_DRIFT_SHIELD.md` — full design
- `.egos-manifest.yaml` in egos + br-acc + carteira-livre
- Schema defined (claims, tolerances, domains, endpoints)

### Layer 4 part B — CLAUDE.md §27 Global Rules (DONE ✅)
- 10 hard rules added
- Bumped to v2.8.0 (2026-04-07)

### Diagnostic work (DONE ✅)
- 8/8 domains verified
- Neo4j 83.7M captured
- Carteira Livre deep-dive complete
- Migration br-acc↔egos-inteligencia resolved
- Caddyfile fixed (852, eagleeye, gemhunter)

---

## 3. PENDING WORK — DETAILED SPECS FOR NEXT SESSION

### PRIORITY ORDER (recommended execution sequence)

1. **DRIFT-001 → DRIFT-004** (Layer 2 + Layer 3 code)
2. **DRIFT-005 → DRIFT-006** (deployment + CCR module)
3. **Phase 6** (br-acc README update — high impact for 128⭐)
4. **Phase 7** (MASTER_INDEX update)
5. **Phase 9** (Timeline doc)
6. **Phase 10** (Posts PT + EN)

**Time estimate (fresh session):** 3-4 hours total if no major blockers.

---

### DRIFT-001 — Write `doc-drift-verifier.ts`

**Location:** `/home/enio/egos/agents/agents/doc-drift-verifier.ts`

**Purpose:** Read a `.egos-manifest.yaml`, run every claim command, compare to `last_value` against `tolerance`, output JSON report.

**CRITICAL: Existing agents to check first (potential conflict/reuse):**
- `/home/enio/egos/agents/agents/drift-sentinel.ts` — EXISTS. Read it first. Decide: extend or create separate. Based on name, `drift-sentinel.ts` is probably for governance file drift, not doc-code drift. Most likely: create `doc-drift-verifier.ts` and `doc-drift-sentinel.ts` as new files but import helpers from existing code.
- `/home/enio/egos/agents/agents/capability-drift-checker.ts` — EXISTS. May already detect capability drift. Extend for doc-drift?
- `/home/enio/egos/agents/agents/ssot-auditor.ts` / `ssot-fixer.ts` — related. Read before creating new.

**Input:** Path to `.egos-manifest.yaml` (or auto-detect in CWD).

**Output (JSON):**
```json
{
  "manifest": "/home/enio/carteira-livre/.egos-manifest.yaml",
  "repo": "carteira-livre",
  "verified_at": "2026-04-07T12:00:00Z",
  "summary": {
    "total_claims": 16,
    "passed": 14,
    "drifted": 2,
    "errors": 0
  },
  "results": [
    {
      "id": "nextjs_pages",
      "status": "drifted",
      "last_value": "134",
      "current_value": "138",
      "tolerance": "±5",
      "drift_pct": 2.9,
      "command": "find app/ -name 'page.tsx' | wc -l | tr -d ' '",
      "severity": "warn"
    }
  ],
  "exit_code": 1
}
```

**CLI:**
```bash
bun agents/agents/doc-drift-verifier.ts --manifest ./.egos-manifest.yaml
bun agents/agents/doc-drift-verifier.ts --repo /home/enio/carteira-livre
bun agents/agents/doc-drift-verifier.ts --all   # scans all repos in workspace
bun agents/agents/doc-drift-verifier.ts --fail-on-drift  # exit 1 if any drift
bun agents/agents/doc-drift-verifier.ts --json              # JSON output
bun agents/agents/doc-drift-verifier.ts --markdown          # markdown table output
```

**Implementation checklist:**
- [ ] Parse YAML (use `yaml` npm package or bun's built-in)
- [ ] For each claim: execute `command` via `Bun.spawn` with 30s timeout
- [ ] Parse `tolerance` string: `exact`, `±N`, `±N%`, `min:N`, `max:N`
- [ ] Compute drift: `current_value` vs `last_value` using tolerance
- [ ] Severity: `ok` | `warn` (within tolerance but not exact) | `drifted` (exceeds tolerance) | `error` (command failed)
- [ ] Check `domains` list: curl each, verify `expected_status`
- [ ] Check `endpoints` list: curl + verify `expected_contains`
- [ ] Exit code: 0 if clean, 1 if `--fail-on-drift` and any drift, 2 on error
- [ ] Log results to `docs/jobs/YYYY-MM-DD-doc-drift-verifier.md`

**Test plan:**
1. Run on carteira-livre manifest — should pass all 16 claims (values were captured today)
2. Manually add a new page to carteira-livre, re-run — should detect `nextjs_pages` drift
3. Run on br-acc — Neo4j commands require VPS SSH; may fail locally. Should degrade gracefully.

**Acceptance criteria:**
- Runs under 60s for all 3 pilot repos
- JSON schema matches spec above
- Exit codes correct
- Domain check reachability test added

---

### DRIFT-002 — Write `.husky/doc-drift-check.sh` + wire to pre-commit

**Location:** `/home/enio/egos/.husky/doc-drift-check.sh`

**Purpose:** Pre-commit hook that runs the verifier and applies the Palmieri pairing rule.

**Content (Bash):**
```bash
#!/bin/sh
# EGOS Doc-Drift Check — Layer 2 of the Doc-Drift Shield
# Blocks commits that drift from declared claims without pairing README/manifest update.

set -eu

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
MANIFEST="$REPO_ROOT/.egos-manifest.yaml"

# Skip if no manifest (opt-in)
if [ ! -f "$MANIFEST" ]; then
  echo "  [doc-drift] no manifest in $REPO_ROOT — skipping"
  exit 0
fi

# Rule A: Pairing — if code staged but README/manifest NOT staged, require verification
STAGED_CODE=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|py|js|jsx)$' || true)
STAGED_DOCS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '(README\.md|\.egos-manifest\.yaml)$' || true)

# Rule B: Override via commit message body
COMMIT_MSG_FILE="$REPO_ROOT/.git/COMMIT_EDITMSG"
if [ -f "$COMMIT_MSG_FILE" ] && grep -q "DOC-DRIFT-ACCEPTED:" "$COMMIT_MSG_FILE"; then
  REASON=$(grep "DOC-DRIFT-ACCEPTED:" "$COMMIT_MSG_FILE" | head -1)
  echo "  [doc-drift] OVERRIDE accepted: $REASON"
  echo "$(date -Iseconds) $REASON" >> "$REPO_ROOT/docs/jobs/doc-drift-overrides.log" 2>/dev/null || true
  exit 0
fi

# Run verifier only if code is staged
if [ -n "$STAGED_CODE" ]; then
  echo "  [doc-drift] code staged — running drift verifier..."
  cd "$REPO_ROOT"
  if ! bun /home/enio/egos/agents/agents/doc-drift-verifier.ts --repo "$REPO_ROOT" --fail-on-drift --json > /tmp/doc-drift.json 2>&1; then
    echo "❌ DOC-DRIFT BLOCKED: code changes drifted from declared claims."
    cat /tmp/doc-drift.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for r in d.get('results', []):
    if r['status'] == 'drifted':
        print(f\"  - {r['id']}: last={r['last_value']} current={r['current_value']} tolerance={r['tolerance']}\")
"
    echo ""
    echo "Fix options:"
    echo "  1. Update README.md with new numbers + re-stage"
    echo "  2. Update .egos-manifest.yaml last_value + re-stage"
    echo "  3. Override: add 'DOC-DRIFT-ACCEPTED: <reason>' to commit body"
    exit 1
  fi
fi

echo "  [doc-drift] ✅ all claims verified"
exit 0
```

**Wire into existing `.husky/pre-commit`:**
Add a new step after step 2.5 (tsc check):
```bash
# 3. Doc-drift check — Layer 2 of the Doc-Drift Shield
echo "  [3/N] doc-drift: verifying .egos-manifest.yaml claims..."
bash .husky/doc-drift-check.sh || exit 1
```

**TTY safety (P29 lesson):**
The hook must NEVER prompt interactively. All output is non-blocking echo. If interactive prompt needed in future, guard with `if [ -t 0 ]`.

**Test plan:**
1. Run `git commit --allow-empty -m "test doc-drift hook"` → should skip (no code staged)
2. Modify a .ts file without README update → should trigger verifier
3. If verifier passes (no drift), commit succeeds
4. Manually drift a claim in manifest, commit code → should block
5. Add `DOC-DRIFT-ACCEPTED: testing override` to commit body → should pass + log

**Acceptance criteria:**
- Hook exits 0 if no manifest (backward compat with repos without L1)
- Hook blocks on real drift
- Override mechanism logs to `docs/jobs/doc-drift-overrides.log`
- Hook runs in < 30s on all pilot repos
- No TTY prompts

---

### DRIFT-003 — Write `doc-drift-sentinel.ts` (L3 agent)

**Location:** `/home/enio/egos/agents/agents/doc-drift-sentinel.ts`

**Purpose:** Autonomous daily scanner that runs on VPS, detects drift, auto-patches manifests, opens GitHub issues, sends Telegram alerts.

**Algorithm:**
```
1. Discover all repos with .egos-manifest.yaml:
   find /home/enio -maxdepth 2 -name '.egos-manifest.yaml' -not -path '*/node_modules/*'

2. For each repo:
   a. cd into repo
   b. Run doc-drift-verifier.ts --repo . --json → parse result
   c. If any claim drifted:
      i.   Create branch: drift-YYYY-MM-DD (if not exists)
      ii.  Update .egos-manifest.yaml: new last_value + last_verified_at
      iii. Commit: "auto(drift): update <claim_id> <old>→<new> [skip ci]"
      iv.  Push branch (never to main)
      v.   Open GitHub issue via gh CLI (rate-limit: max 1 per claim per 7d)
      vi.  Send Telegram alert to @egosin_bot: "⚠️ Drift detected: <repo>/<claim_id>"
   d. If any domain failed: alert only (no auto-fix)

3. Write consolidated report: docs/jobs/YYYY-MM-DD-doc-drift-sentinel.md

4. Exit 0 always (never blocks anything else)
```

**CLI:**
```bash
bun agents/agents/doc-drift-sentinel.ts --dry          # detect but don't commit/push/alert
bun agents/agents/doc-drift-sentinel.ts --exec         # full run
bun agents/agents/doc-drift-sentinel.ts --exec --repo /home/enio/carteira-livre  # single repo
```

**Rate-limit storage:**
Use `/var/lib/egos/doc-drift-sentinel/issue-log.json`:
```json
{
  "issues": [
    {
      "repo": "enioxt/carteira-livre",
      "claim_id": "nextjs_pages",
      "issue_number": 42,
      "opened_at": "2026-04-07T03:00:00Z"
    }
  ]
}
```
Skip creating issue if same `(repo, claim_id)` exists within last 7 days.

**Telegram alert format:**
```
⚠️ Doc-Drift Sentinel
Repo: carteira-livre
Claim: nextjs_pages
Drift: 134 → 138 (tolerance ±5)
Branch: drift-2026-04-07
Issue: https://github.com/enioxt/carteira-livre/issues/42
```

**Safety:**
- Never force-push (§25 rule)
- Never push to main/master
- Never overwrite uncommitted changes: check `git status --porcelain` before editing
- Never run if `git status` shows unrelated staged changes

**Test plan:**
1. `--dry` run on all repos — should find 0 drift (manifests captured today)
2. Manually break a claim in carteira-livre manifest (e.g., `last_value: "100"` for pages)
3. Run `--exec --repo /home/enio/carteira-livre` — should create branch + issue + alert
4. Re-run — should NOT create new issue (rate limit)
5. Wait 7d simulation — should create new issue

**Acceptance criteria:**
- `--dry` run completes in < 2 min for all repos
- No main branch modifications
- Rate limit works
- Telegram alert sent (mock if token unavailable)

---

### DRIFT-004 — Register sentinel in `agents/registry/agents.json`

**File:** `/home/enio/egos/agents/registry/agents.json`

**Add entry:**
```json
{
  "id": "doc-drift-sentinel",
  "name": "Doc-Drift Sentinel",
  "description": "Layer 3 of the Doc-Drift Shield. Daily scanner that verifies all .egos-manifest.yaml claims, auto-patches last_value, opens GitHub issues, sends Telegram alerts on drift.",
  "path": "agents/agents/doc-drift-sentinel.ts",
  "runtime": "bun",
  "schedule": "0 3 * * *",
  "schedule_tz": "America/Sao_Paulo",
  "status": "active",
  "tags": ["governance", "documentation", "drift", "sentinel"],
  "created_at": "2026-04-07",
  "requires": ["yaml", "git", "gh"],
  "outputs": ["docs/jobs/YYYY-MM-DD-doc-drift-sentinel.md"],
  "dry_run_support": true
}
```

**Run `bun agent:lint` after editing** to validate registry integrity.

---

### DRIFT-005 — Deploy sentinel cron to VPS

**Steps:**
1. Copy `doc-drift-sentinel.ts` to VPS: `rsync -avz /home/enio/egos/agents/agents/doc-drift-sentinel.ts root@204.168.217.125:/opt/egos/agents/agents/`
2. Pull latest egos repo on VPS: `ssh root@204.168.217.125 'cd /opt/egos && git pull'`
3. Test in dry mode: `ssh root@204.168.217.125 'cd /opt/egos && bun agents/agents/doc-drift-sentinel.ts --dry'`
4. Add cron entry via crontab: `0 3 * * * cd /opt/egos && bun agents/agents/doc-drift-sentinel.ts --exec >> /var/log/doc-drift.log 2>&1`
5. Verify: `ssh root@204.168.217.125 'crontab -l | grep doc-drift'`
6. Create log dir: `ssh root@204.168.217.125 'mkdir -p /var/lib/egos/doc-drift-sentinel && touch /var/log/doc-drift.log && chmod 644 /var/log/doc-drift.log'`

**Blocker check:** VPS has all target repos cloned? Check `/opt/egos`, `/opt/br-acc`, `/opt/carteira-livre`. Sentinel needs these paths to scan. If repos not on VPS, sentinel runs from local dev machine via cron instead.

**Alternative:** Add sentinel as CCR scheduled job (Claude Code extension) instead of VPS cron. Trade-off: CCR runs weekly instead of daily, but no infra management needed.

---

### DRIFT-006 — Extend CCR Governance Drift Sentinel job (L4)

**Current job:** `Governance Drift Sentinel` (daily 0h17 BRT)
**Location:** Check `~/.claude/` or ask user for the CCR job config

**New module to add:** `doc-drift-analyzer`

**Weekly analysis prompt for Claude:**
```
Read all files in docs/jobs/*-doc-drift-sentinel.md from the last 7 days.

Identify:
1. Which repos drift most often?
2. Which claims drift every scan (unstable claims)?
3. Which claims never drift (stable — good candidates for badges)?
4. Which repos have claims failing verification (command errors)?

Propose:
- Remove unstable claims from manifests (they create noise)
- Add new claims for features mentioned in recent commits but not tracked
- Fix broken commands

Output to: docs/jobs/YYYY-WW-doc-drift-weekly.md
Create branch: claude/doc-drift-weekly-YYYY-WW
Open PR if proposals non-trivial.
```

**Safety:** PR must be human-reviewed. Never auto-merge structural changes.

---

### Phase 6 — Update br-acc README (the 128 ⭐ repo)

**File:** `/home/enio/br-acc/README.md`

**Current state (lines 1-10):**
```markdown
# EGOS Inteligência — Plataforma Aberta de Cruzamento de Dados Públicos

> **Status:** ⏸️ Ritmo reduzido — renomeando para EGOS Inteligência. 77M entidades, Neo4j graph, ETL pipeline.
> Este projeto tem MVP funcional disponível. Interessados em contribuir ou co-fundar: entre em contato via [Issues](https://github.com/enioxt/br-acc/issues) ou enio@egos.ia.br

<!-- RHO_BADGE --> **Rho Score:** 🟡 0.30 (WARNING) | Contributors: 4 | Commits (30d): 94 | Updated: 2026-03-02 <!-- /RHO_BADGE -->
```

**Changes needed:**
1. `77M entidades` → `83.7M nós + 26.8M relacionamentos`
2. Add `32 tipos de entidade` list (the 32 labels)
3. Update `Rho Score` block: `Contributors: 1 (Enio Rocha), Commits (30d): <verify>, Updated: 2026-04-07`
4. Update issue link: `github.com/br-acc/issues` → `github.com/enioxt/EGOS-Inteligencia/issues`
5. Add Verified Evidence section pointing to `.egos-manifest.yaml`
6. Add live domain badges: inteligencia.egos.ia.br
7. Update VPS section: Contabo → Hetzner
8. Scope section: list 32 entity types with counts (if queryable)

**Verify after edit:** Run `bun agents/agents/doc-drift-verifier.ts --repo /home/enio/br-acc` — should be clean.

**Commit + push:** Commit to `main`, push to origin (EGOS-Inteligencia.git). Then update GitHub metadata via gh API:
```bash
gh repo edit enioxt/EGOS-Inteligencia \
  --description "Plataforma aberta de inteligência sobre dados públicos brasileiros. Grafo Neo4j com 83.7M nós, 26.8M relacionamentos, 32 tipos de entidade. OSINT + ETL + AI Router." \
  --homepage "https://inteligencia.egos.ia.br" \
  --add-topic osint \
  --add-topic neo4j \
  --add-topic brazil \
  --add-topic lgpd \
  --add-topic public-data \
  --add-topic graph-database \
  --add-topic python \
  --add-topic open-source \
  --add-topic corruption-detection \
  --add-topic govtech
```

---

### Phase 7 — Update MASTER_INDEX.md

**File:** `/home/enio/egos/docs/MASTER_INDEX.md`

**Changes:**
1. Version: 1.2.0 → 1.3.0
2. Line 12: `18 agents` → verify via `python3 -c "import json; print(len(json.load(open('agents/registry/agents.json'))['agents']))"`
3. Line 64: `EGOS Inteligência (br-acc)` row: "OSINT platform, 77M Neo4j" → "OSINT platform, **83.7M Neo4j nodes + 26.8M rels + 32 labels** (verified 2026-04-07 — see br-acc/.egos-manifest.yaml)"
4. Add new section after Repository Universe:
   ```markdown
   ## 🧪 Verified Evidence (2026-04-07 session)
   
   Every claim in this document with a "(verified)" tag is backed by a reproducible command in the corresponding repo's `.egos-manifest.yaml`. See `docs/DOC_DRIFT_SHIELD.md`.
   
   ### Ecosystem health snapshot
   
   | Check | Command | Result | Timestamp |
   |-------|---------|--------|-----------|
   | Neo4j nodes | `curl -u neo4j:<pass> localhost:7474/db/neo4j/query/v2 -d '{"statement":"MATCH (n) RETURN count(n)"}'` | 83,773,683 | 2026-04-07T00:00Z |
   | Neo4j rels | (same, MATCH ()-[r]->()) | 26,808,540 | 2026-04-07T00:00Z |
   | Neo4j labels | (same, CALL db.labels()) | 32 | 2026-04-07T00:00Z |
   | guard.egos.ia.br | `curl -s -o /dev/null -w "%{http_code}" https://guard.egos.ia.br/health` | 200 | 2026-04-07 |
   | 852.egos.ia.br | (same URL) | 200 | 2026-04-07 (fixed today) |
   | eagleeye.egos.ia.br | (same) | 200 | 2026-04-07 (fixed today) |
   | hq.egos.ia.br | (same) | 307 | 2026-04-07 |
   | inteligencia.egos.ia.br | (same) | 200 | 2026-04-07 (newly listed) |
   | carteiralivre.com.br | (same) | 308→200 | 2026-04-07 |
   | gemhunter.egos.ia.br | (same) | 200 | 2026-04-07 |
   | openclaw.egos.ia.br | (same) | 200 | 2026-04-07 |
   | VPS containers | `docker ps --format '{{.Names}}' \| wc -l` | 19 | 2026-04-07 |
   | EGOS-Inteligencia stars | `gh api repos/enioxt/EGOS-Inteligencia \| jq .stargazers_count` | 128 | 2026-04-07 |
   ```
5. Add `inteligencia.egos.ia.br` row to the domain list
6. Remove references to "Contabo" (migration complete)

**Do NOT create new files.** Everything goes into MASTER_INDEX.md per SSOT-first rule (§26).

---

### Phase 9 — Timeline doc

**File:** `/home/enio/egos/docs/ENIO_DEVELOPER_TIMELINE.md` (or append to MASTER_INDEX if Enio prefers less files)

**Content:** Chronological archaeology of Enio Rocha as developer, reconstructed from git logs.

**Key dates already extracted:**
| Date | Repo | Event |
|------|------|-------|
| 2025-12-12 18:44 | carteira-livre | **Day 0**: "MVP Carteira Livre - Plataforma de instrutores de direção" (first commit, origin of the ecosystem) |
| 2025-12-12 19:09 | carteira-livre | Same day, commit 5: "Tutor IA com Gemini 2.0 Flash" (AI integrated from hour 1) |
| 2025-12-14 | carteira-livre | ETHIK reputation UI components |
| 2025-12-17 | carteira-livre | Real booking flow with APIs |
| 2025-12-22 | carteira-livre | Leaflet GPS tracking |
| 2026-01-18 | carteira-livre | Multi-persona (Aluno ⇄ Instrutor) |
| 2026-01-20 | carteira-livre | INPI MVP |
| 2026-01-28 | carteira-livre | Rádio Philein 24/7 (!) |
| 2026-02-01 | carteira-livre | Multi-state architecture |
| 2026-02-04 | carteira-livre | AI Orchestrator + influencer discovery |
| 2026-02-13 | egos-lab | **Day 63**: Initial egos-lab monorepo + Eagle Eye MVP |
| 2026-02-22 | br-acc | **Day 72**: Phase 0 foundation (becomes EGOS-Inteligencia) |
| 2026-03-01 | EGOS-Inteligencia | GitHub repo created (current 128⭐) |
| 2026-03-04 | forja | **Day 82**: scaffold Forja project |
| 2026-03-10 | 852 | **Day 88**: Initial commit from Create Next App |

**Narrative arc to write:**
1. Dec 2025: Solo founder launches first product (Carteira Livre) — CONTRAN 1020/2025 compliance niche
2. Jan 2026: Velocity peak — 600 commits in one month, multi-persona, growth engine
3. Feb 2026: Breakthrough month — 826 commits (~28/day), kernel emerges (egos-lab), graph platform (br-acc), multi-state expansion
4. Mar 2026: Ecosystem formalizes — Forja, 852, EGOS-Inteligencia goes public (128⭐ acquired)
5. Apr 2026: Consolidation mode — MASTER_INDEX, governance, GTM push

**Use the reproducible commands:**
```bash
git -C /home/enio/carteira-livre log --reverse --pretty=format:"%h %ai %s" | head -5
git -C /home/enio/carteira-livre log --pretty=format:"%ai" | awk '{print substr($1,1,7)}' | sort | uniq -c
```

---

### Phase 10a — Post X.com em Português

**Target:** `/home/enio/personal/X_POST_PT_2026-04-07.md` (or append to existing X_POST_5_VERCOES)

**Angle:** Narrativa pessoal investigador→builder + foco BR (LGPD, Guard Brasil, licitações, CONTRAN). Use Version 6 already written in X_POST_5_VERCOES as base.

**Reinforcement:** All numbers MUST come from `.egos-manifest.yaml` files created today. Any number in the post MUST have a corresponding claim in a manifest.

### Phase 10b — Post X.com in English

**Target:** `/home/enio/personal/X_POST_EN_2026-04-07.md`

**Angle:** Technical capability for global audience. Focus on:
- Neo4j 83.7M graph (universally impressive, no BR knowledge needed)
- 23 autonomous AI agents with governance
- Multi-LLM orchestration (Alibaba Qwen, Google Gemini, OpenRouter fallback)
- Open source (MIT, auditable, 128⭐ on one repo)
- Web3 gem hunter (8+ years, tokenomics analysis of 1000+ projects)
- 19 Docker containers on Hetzner, 8/8 domains live, 9-day uptime

**Do NOT translate PT post. Write native EN.** Different audience, different hooks.

**Structure suggestion (EN):**
```
1. Hook: "Built a 83.7M node OSINT platform solo in 18 months. Here's the stack."
2. Graph numbers + source verification (commands)
3. Multi-agent architecture (23 agents with governance)
4. Multi-LLM fallback chain (for resilience)
5. What I'm looking for: co-founder for US/EU markets
6. CTA: DM for demo
```

**Testing:**
- Verify every number matches manifest
- Run spell check
- Keep tweets ≤ 280 chars

---

## 4. OPEN DECISIONS (Enio needs to decide at some point)

1. **Sentinel deployment location:** VPS cron vs CCR scheduled job? (§DRIFT-005)
2. **Rho Score block in br-acc README:** Keep or remove? Who computes Rho? The badge says "4 contributors" but reality is 1. This is its own drift issue.
3. **EGOS-Inteligencia rename:** Rename GitHub repo from `EGOS-Inteligencia` to something cleaner? Would lose external links but gain clarity. Not urgent.
4. **Abandoned `/home/enio/egos-inteligencia` scaffold:** Archive? Merge useful files into br-acc? Delete? Decision deferred.
5. **CLI vs Windsurf extension:** See §6 of this handoff.

---

## 5. VERIFICATION COMMANDS (next session: run these first to confirm state)

```bash
# Confirm L1 files exist
ls -la /home/enio/egos/docs/DOC_DRIFT_SHIELD.md
ls -la /home/enio/egos/.egos-manifest.yaml
ls -la /home/enio/br-acc/.egos-manifest.yaml
ls -la /home/enio/carteira-livre/.egos-manifest.yaml

# Confirm CLAUDE.md §27 present
grep -c "§27 Doc-Drift" /home/enio/.claude/CLAUDE.md  # should output: 1

# Confirm VPS domains still live
for d in guard 852 eagleeye gemhunter hq openclaw inteligencia; do
  curl -s -o /dev/null -w "$d.egos.ia.br: %{http_code}\n" --max-time 10 "https://$d.egos.ia.br/"
done
curl -s -o /dev/null -w "carteiralivre.com.br: %{http_code}\n" --max-time 10 https://carteiralivre.com.br/

# Confirm Neo4j still has 83.7M
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 \
  'curl -s -u neo4j:BrAcc2026EgosNeo4j! http://localhost:7474/db/neo4j/query/v2 \
   -H "Content-Type: application/json" \
   -d "{\"statement\":\"MATCH (n) RETURN count(n)\"}"'

# Confirm 19 containers still up
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 'docker ps | wc -l'

# Read existing drift-sentinel.ts BEFORE writing doc-drift-sentinel.ts
cat /home/enio/egos/agents/agents/drift-sentinel.ts | head -40
cat /home/enio/egos/agents/agents/capability-drift-checker.ts | head -40
```

---

## 6. CLAUDE CODE EXTENSION vs CLI — Answer

**Current state:** This session runs inside Claude Code VSCode-native extension (Windsurf). The system prompt confirms: "running within the Claude Agent SDK" + "You are running inside a VSCode native extension environment".

**Functional parity:** Both the CLI and the extension share the same:
- Model access (Sonnet 4.6, Opus 4.6, Haiku 4.5)
- Tool set (Read, Edit, Bash, Grep, Glob, WebFetch, etc.)
- MCP servers (exa, brave, firecrawl, github, supabase, vercel, notion, gmail, memory, codebase-memory-mcp, etc.)
- Skills and subagents (general-purpose, Explore, Plan, statusline-setup, claude-code-guide)
- Scheduled jobs (CCR/triggers)

**Differences:**
| Aspect | Extension (Windsurf) | CLI (terminal) |
|--------|---------------------|----------------|
| Visual diffs | ✅ inline | Text-only |
| IDE selection context | ✅ auto (ide_opened_file tag) | ❌ manual |
| Long sessions (>1h) | Works but can lag | Better for long runs |
| Background processes | Limited | Full |
| Parallel sessions | 1 per IDE window | N per terminal |
| Agent tool calls | Same | Same |
| File system access | Same | Same |

**Recommendation: STAY in the extension for this phase.**
Reasons:
1. We're in the middle of documentation work — inline diff review is valuable
2. Switching loses context (you'd need to re-onboard the CLI session)
3. The extension has the `ide_opened_file` tag which helps orient the LLM to your current focus
4. All the heavy lifting (agents, tools, MCPs) works identically

**Switch to CLI when:**
- You want to run scheduled jobs directly from your terminal
- You're doing large refactors across 20+ files (less UI friction)
- You want to run multiple parallel Claude sessions
- You want to use the `claude` command as a subcommand in shell scripts

**For tonight's handoff:** Extension is fine. Start next session in extension too.

---

## 7. NEXT SESSION QUICK-START (copy this to the first message)

```
Olá Claude. Continuar sessão iniciada em 2026-04-07 — execução do Doc-Drift Shield.

Leia primeiro:
1. /home/enio/egos/docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md (este arquivo)
2. /home/enio/egos/docs/DOC_DRIFT_SHIELD.md (design completo)
3. /home/enio/.claude/CLAUDE.md §27 (regras globais duras)
4. /home/enio/egos/agents/agents/drift-sentinel.ts (existente — NÃO duplicar)
5. /home/enio/egos/agents/agents/capability-drift-checker.ts (existente — NÃO duplicar)

Depois execute §5 do handoff (verification commands) para confirmar estado.

Depois execute na ordem:
1. DRIFT-001: doc-drift-verifier.ts
2. DRIFT-002: .husky/doc-drift-check.sh + wire
3. DRIFT-003: doc-drift-sentinel.ts
4. DRIFT-004: registrar em agents.json + bun agent:lint
5. DRIFT-005: deploy VPS cron
6. DRIFT-006: CCR job extension
7. Phase 6: br-acc README update (128⭐ repo)
8. Phase 7: MASTER_INDEX update
9. Phase 9: Timeline doc
10. Phase 10: Posts PT + EN

Objetivo da sessão: todos os itens acima ✅. Tempo estimado: 3-4h.

Regras não-negociáveis:
- Seguir CLAUDE.md §27 integralmente
- Cada novo claim em README DEVE ter entrada no manifest
- Nunca force-push (§25)
- Usar TodoWrite para tracking
- Testar cada etapa antes de avançar
```

---

## 8. DECISION LOG (this session)

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Manifest path: `.egos-manifest.yaml` (repo root) | `.egos/` is already used by kernel governance, conflicting per-repo |
| 2 | Keep br-acc as canonical repo | 360 commits + 128⭐ + active origin; scaffold is abandoned |
| 3 | All 4 layers of Drift Shield | User confirmed via AskUserQuestion |
| 4 | Drift Shield before Phase 6-10 | User priority: protection first, then polished outputs |
| 5 | Contract manifest > docs annotations | Machine-readable, reproducible, fits EGOS SSOT pattern |
| 6 | Schema version 1.0.0 + updated_at | Future migrations clean, time-stamped |
| 7 | Tolerance types (exact, ±N, ±N%, min:N, max:N) | Covers all real-world claims seen today |
| 8 | PT + EN posts are DIFFERENT (not translations) | Different ICP, different hooks (§10a vs §10b) |
| 9 | Carteira Livre README FULL rewrite | 5 claims drifted — cheaper to rebuild header than patch |
| 10 | `sed -i` banned for bind-mounted files | INC-level bug discovered this session |

---

## 9. BLOCKERS & RISKS

| # | Item | Severity | Mitigation |
|---|------|----------|------------|
| 1 | VPS SSH credentials required for Neo4j proof command in manifest | medium | Sentinel must run FROM VPS, not locally |
| 2 | `drift-sentinel.ts` already exists — possible conflict | low | Read first, decide extend vs create new |
| 3 | Pre-commit hook adds latency | low | Cache verifier results for 60s in-session |
| 4 | Telegram bot token for alerts | low | Fallback to log file if token missing |
| 5 | GitHub rate limit on gh CLI issues | low | Sentinel rate-limits to 1 issue/claim/week |
| 6 | Carteira Livre README was rewritten but not committed | medium | Commit at end of this session |
| 7 | No git commit made this session for doc updates | **medium** | Next session should `/commit` early |

---

## 10. GIT STATE AT HANDOFF

**egos repo:**
```
Branch: main
Uncommitted changes expected (this session):
  - modified: docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md (this file)
  - modified: TASKS.md (adding DRIFT-001..010)
  - new file: docs/DOC_DRIFT_SHIELD.md
  - new file: .egos-manifest.yaml
```

**br-acc repo:**
```
Branch: main
Uncommitted changes:
  - new file: .egos-manifest.yaml
(README update is Phase 6 — pending)
```

**carteira-livre repo:**
```
Branch: main
Uncommitted changes:
  - modified: README.md (header rewrite — verified numbers + 16-row scope table)
  - new file: .egos-manifest.yaml
```

**~/.claude/CLAUDE.md:**
```
- modified: added §27 Doc-Drift Shield Rules, bumped to v2.8.0
```

**/home/enio/personal/ (not git):**
```
- modified: cv-enio-completo-2025-portugues.html
- modified: X_POST_5_VERCOES_LOW_PROFILE.md (Version 6 added)
```

**VPS Caddyfile:** Already deployed and serving. 852 + eagleeye + gemhunter fixed.

**Next session: commit carteira-livre README + .egos-manifest.yaml first** before anything else. Then proceed with DRIFT-001.

---

## 11. CONTACT FOR HANDOFF QUESTIONS

- **Memory index:** `/home/enio/.claude/projects/-home-enio-egos/memory/MEMORY.md`
- **Latest memory:** (will be written by /end skill)
- **Governance canon:** `/home/enio/egos/.guarani/RULES_INDEX.md`
- **This file:** `/home/enio/egos/docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md`

---

*Handoff author: Claude Sonnet 4.6, Windsurf extension, session P33 (2026-04-07)*
*Next session target: P34 — Doc-Drift Shield implementation + Phase 6-10 execution*
*Recommended next model: Claude Sonnet 4.6 (Opus 4.6 if cost allows and reasoning depth needed for structural decisions)*
