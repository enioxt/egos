# @egosbr/knowledge-mcp

MCP server for EGOS Knowledge Base — ingest PDFs/docs, semantic search, Q&A, lint, and export.

## Tools

| Tool | Description |
|------|-------------|
| `search_wiki` | Semantic search across KB pages |
| `get_page` | Get a specific page by slug |
| `get_stats` | KB statistics (total pages, avg quality, categories) |
| `record_learning` | Save a learning/insight to the KB |
| `list_learnings` | List recent learnings |
| `ingest_file` | Ingest a PDF, DOCX, or Markdown file (with Guard Brasil PII scan) |
| `kb_lint` | Audit KB quality — orphans, stale content, broken refs, duplicates |
| `kb_export` | Export pages to JSON or Markdown |

## Install

```bash
npm install -g @egosbr/knowledge-mcp
```

## Usage with Claude Code

Add to `~/.claude.json` or project `.claude/settings.json`:

```json
{
  "mcpServers": {
    "egos-knowledge": {
      "command": "knowledge-mcp",
      "env": {
        "EGOS_GATEWAY_URL": "https://gateway.egos.ia.br",
        "SUPABASE_URL": "your-supabase-url",
        "SUPABASE_SERVICE_ROLE_KEY": "your-key",
        "GUARD_BRASIL_API_KEY": "optional-for-pii-scan"
      }
    }
  }
}
```

## Example prompts

```
/ingest-file /path/to/manual-fundição.pdf --category metalurgia
/ask Qual é o processo padrão de controle de qualidade?
/kb-lint --tenant=forja
/kb-export --format=markdown --category=metalurgia
```

## License

MIT — Enio Rocha / EGOS (egos.ia.br)
