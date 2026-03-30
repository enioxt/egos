# @egos/mcp-governance

EGOS-087 — Governance MCP server (stdio). Provides 4 tools for SSOT drift detection, task inspection, agent registry health, and repo scoring.

## Tools

| Tool | Description |
|------|-------------|
| `ssot_drift_check` | Compares `agents.json` vs `TASKS.md`, returns drift score and orphaned items |
| `list_tasks` | Lists tasks from `TASKS.md` filtered by `pending` / `done` / `all` |
| `agent_status` | Reads `agents/registry/agents.json`, returns agents grouped by kind/status/risk |
| `repo_health` | Checks line count, last commit age, uncommitted files, governance file presence |

## Connect to Claude Code

Add to `.claude/settings.json` (or `~/.claude.json` mcpServers block):

```json
{
  "mcpServers": {
    "egos-governance": {
      "command": "bun",
      "args": ["/home/enio/egos/packages/mcp-governance/src/index.ts"]
    }
  }
}
```

## Run standalone

```bash
bun run /home/enio/egos/packages/mcp-governance/src/index.ts
```

Uses stdio transport — pipe JSON-RPC 2.0 messages to stdin.
