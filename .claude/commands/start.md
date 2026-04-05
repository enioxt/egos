# /start — Session Initialization (EGOS v5.7)

> **Works in:** ANY EGOS repo

## Phase 0: World Model Snapshot

```bash
bun /home/enio/egos/packages/shared/src/world-model.ts --save 2>/dev/null
```

Presents: health%, P0 blockers, top P1 sprint, critical signals.
Use this as the "current state of the system" before any other phase.
If world-model errors: skip and continue — non-blocking.

## Phase 1: Collect Session Data

```bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo $PWD)
echo "Repo: $(basename $ROOT) | Branch: $(git branch --show-current 2>/dev/null)"
echo "Last commit: $(git log --oneline -1 2>/dev/null)"
echo "Uncommitted: $(git status --short 2>/dev/null | wc -l) files"
git log --oneline -5 2>/dev/null
```

## Phase 2: Governance + Sync Check

```bash
bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --check 2>/dev/null | tail -10
```

## Phase 3: File Existence Check

Required (flag if missing):
`AGENTS.md`, `TASKS.md`, `docs/CAPABILITY_REGISTRY.md`, `.windsurfrules`, `.guarani/PREFERENCES.md`, `.guarani/IDENTITY.md`, `.guarani/prompts/triggers.json`, `docs/SYSTEM_MAP.md`

## Phase 4: Resource Check

```bash
df -h / 2>/dev/null | tail -1 && free -h 2>/dev/null | head -2
```

## Phase 5: Meta-Prompts

```bash
cat .guarani/prompts/triggers.json 2>/dev/null | jq '.triggers | length' || echo "N/A"
```

## Phase 6: Scheduled Job Results

Read the latest reports from automated jobs. Present actionable summary.

```bash
echo "=== Latest Job Reports ==="
ls -t docs/jobs/*.md 2>/dev/null | head -3 | while read f; do
  echo "--- $(basename $f) ---"
  head -5 "$f"
  grep -i 'status:' "$f" 2>/dev/null | head -1
  echo ""
done

echo "=== Latest Gem Hunter ==="
ls -t docs/gem-hunter/*.md 2>/dev/null | head -1 | xargs head -5 2>/dev/null
```

**Interpretation rules:**
- `Status: CRITICAL` → flag as **P0 blocker** in briefing, recommend immediate action
- `Status: WARNING` or `REVIEW_NEEDED` → mention in **P1** section with top recommended action
- `Status: CLEAN/HEALTHY/SECURE` → just note "Jobs healthy"
- No reports in last 7 days → warn "No recent job results — check https://claude.ai/code/scheduled"
- Gem Hunter: mention top 1-2 discoveries if relevant to current sprint

**Active scheduled jobs (3 slots max):**
1. Gem Hunter — Scraping Tools (seg 9h BRT, weekly)
2. Governance Drift Sentinel (diário 0h17 BRT)
3. Code Intel + Security Audit (seg+qui 1h42 BRT)

## Phase 7: Tooling Check

| Tool | Check | Required? |
|------|-------|-----------|
| Alibaba Qwen | `ALIBABA_DASHSCOPE_API_KEY` in `.env` | YES — preferred orchestrator |
| Supabase | `SUPABASE_URL` in `.env` | If DB-backed repo |
| Codex | `codex --version 2>/dev/null` | MODERATE+ tasks |
| codebase-memory-mcp | `which codebase-memory-mcp 2>/dev/null` | YES — knowledge graph |
| SecOps Gate | `ls docs/gem-hunter/secops-*.md 2>/dev/null` | BLOCKING if UNMITIGATED |

## Phase 7.5: Knowledge Base Health

```bash
echo "=== Knowledge Base ==="
bun /home/enio/egos/agents/agents/wiki-compiler.ts --index 2>/dev/null | tail -5
```

Include page count and avg quality in Phase 8 briefing. If 0 pages: note "KB empty — run `bun wiki:compile`".

## Phase 7.6: Task Reconciliation

```bash
bun /home/enio/egos/scripts/task-reconciliation.ts --summary 2>/dev/null
```

Include the one-liner output in the Phase 8 briefing under **Tasks**.
If drift > 0: recommend `bun scripts/task-reconciliation.ts --fix`

## Phase 8: Output Briefing

Present to user:

- **Security Status:** Critical CVEs or ✅ Clean
- **Job Reports:** Summary from Phase 6 (CRITICAL/WARNING/CLEAN)
- **Tasks:** P0 blockers → P1 sprint → P2 backlog (counts)
- **Handoff:** Last session (1-2 lines from `docs/_current_handoffs/`)
- **Recent commits:** Last 5
- **Meta-prompts:** Count active triggers
- **Orchestration:** Alibaba/Qwen availability + Pipeline status
- **Knowledge Graph:** codebase-memory-mcp indexed repos count
- **Knowledge Base:** page count, avg quality, stale pages (from Phase 7.5)
- **Repo role:** from `egos.config.json` or heuristic

---
*v5.8 — Added Phase 7.5 (Knowledge Base health from wiki-compiler --index)*
