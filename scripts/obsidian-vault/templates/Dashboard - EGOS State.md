# Dashboard - EGOS State

> Auto-generated from `/start` diagnostics  
> Updated: {{date}}

---

## 🔌 Integrations Health

| Service | Status | Version | Last Check |
|---------|--------|---------|------------|
| Guard Brasil API | 🟢 | v0.2.0 | {{date}} |
| ARCH API | 🟢 | — | {{date}} |
| Eagle Eye | 🟢 | — | {{date}} |
| VPS Hetzner | 🟢 | 19 containers | {{date}} |
| MCP Servers | 🟢 | 6 active | {{date}} |

## 📈 Active Tasks (P0)

```dataview
task
from "01 - Raw Sources"
where !completed
where text contains "P0"
sort file.name asc
```

## 🗓️ Recent Sessions

```dataview
table date, summary, integrationsrom "03 - Sessions"
sort date desc
limit 10
```

## 🧠 Knowledge Graph Stats

- **Nodes:** 51,000 (codebase-memory-mcp)
- **Edges:** 75,000
- **Repos indexed:** 7
- **Atoms:** {{atom_count}}

## 🚨 Alerts

- [ ] {{#if drift}}Governance drift detected{{/if}}
- [ ] {{#if stale_tasks}}Stale P0 tasks{{/if}}
- [ ] {{#if unassigned}}Unassigned blockers{{/if}}

---

*[[Open Dashboard Query|🔍 Query Details]]*
