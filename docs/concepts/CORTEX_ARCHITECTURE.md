# Cortex Knowledge System — Reference

> **Origin:** EGOSv4 (Dec 2025) | **Status:** Prototype archived
> **Full spec:** `/home/enio/egos-archive/v4-lowercase/egosv4/docs/ARCHITECTURE.md`

## 4-Layer Architecture

```
┌─────────────────────────────────────────────┐
│  GUARANI LAYER (Identity & Rules)           │
├─────────────────────────────────────────────┤
│  WORKFLOW LAYER (Automation)                │
├─────────────────────────────────────────────┤
│  CORTEX LAYER (Knowledge System)            │
│  ├── Daemon (File watcher + processor)      │
│  ├── MCP Server (AI agent interface)        │
│  ├── REST API (HTTP interface)              │
│  └── CLI (Command line)                     │
├─────────────────────────────────────────────┤
│  TOOLS LAYER (Utilities)                    │
└─────────────────────────────────────────────┘
```

## Data Flow

Files → Watcher → Analyzer (+ LLM) → SQLite DB

## Key Design Decisions

- **SQLite:** Portable, single file, no server, ACID
- **Prisma:** Type-safe ORM with migrations
- **MCP-First:** Use tools before writing code
- **Local-first:** Data stays on your machine

## Recovered Components

- `privacy-scanner.ts` → now in `.guarani/tools/`
- `code-health-monitor.ts` → now in `.guarani/tools/`
- `llm-bridge.ts` → superseded by `packages/shared/src/llm-provider.ts`

## Relevance to Current EGOS

The Cortex concept of file-watching + LLM analysis informs:
- Agent self-diagnosis capabilities
- Knowledge graph building
- Automated codebase health monitoring
