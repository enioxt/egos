# /start — Session Initialization (EGOS v5.6)

> **Works in:** ANY EGOS repo

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
- **Repo role:** from `egos.config.json` or heuristic

---
*v5.6 — Added Phase 6 (scheduled job results intake), codebase-memory-mcp in tooling check*
