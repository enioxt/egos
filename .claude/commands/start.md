# /start — Session Initialization (EGOS v5.5)

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

## Phase 6: Tooling Check

| Tool | Check | Required? |
|------|-------|-----------|
| Alibaba Qwen | `ALIBABA_DASHSCOPE_API_KEY` in `.env` | YES — preferred orchestrator |
| Supabase | `SUPABASE_URL` in `.env` | If DB-backed repo |
| Codex | `codex --version 2>/dev/null` | MODERATE+ tasks |
| SecOps Gate | `ls docs/gem-hunter/secops-*.md 2>/dev/null` | BLOCKING if UNMITIGATED |

## Phase 7: Output Briefing

Present to user:

- **Security Status:** Critical CVEs or ✅ Clean
- **Tasks:** P0 blockers → P1 sprint → P2 backlog (counts)
- **Handoff:** Last session (1-2 lines from `docs/_current_handoffs/`)
- **Recent commits:** Last 5
- **Meta-prompts:** Count active triggers
- **Orchestration:** Alibaba/Qwen availability + Pipeline status
- **Repo role:** from `egos.config.json` or heuristic

---
*v5.5 — Aligned with .windsurf/workflows/start.md*
