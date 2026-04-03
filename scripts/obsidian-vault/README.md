# EGOS Knowledge Base

> **Vault:** EGOS  
> **Model:** Karpathy Knowledge Base Pattern  
> **Created:** 2026-04-03  
> **Auto-compiled:** Yes (via `scripts/export-to-obsidian.ts`)

---

## 🎯 Purpose

This vault implements Andrej Karpathy's LLM Knowledge Base pattern for the EGOS ecosystem:

- **Raw/**: Source documents from all EGOS repositories
- **Wiki/**: LLM-compiled knowledge (summaries, articles, backlinks)
- **Sessions/**: Per-session handoffs and insights
- **Outputs/**: Dashboards, reports, visualizations
- **Inbox/**: Temporary captures before processing

## 🔄 Workflow

```
EGOS Session → /start → export-to-obsidian.ts → Wiki update → Obsidian view
```

## 📊 Quick Navigation

- [[Dashboard - EGOS State]] — Real-time ecosystem health
- [[Tasks - Active P0]] — Critical priorities
- [[Sessions Index]] — All session handoffs
- [[Capabilities Registry]] — 160 capabilities, 13 domains

## 🛠️ Maintenance

- **Auto-updated:** After each `/start` or `/end`
- **Manual sync:** `bun run obsidian:sync`
- **Health check:** `bun run obsidian:lint`

---

*Last compiled: {{date}}*
