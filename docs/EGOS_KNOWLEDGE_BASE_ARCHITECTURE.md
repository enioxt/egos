# EGOS Knowledge Base Architecture

> **Pattern:** Karpathy LLM Knowledge Base  
> **Implementation:** EGOS-Obsidian Integration  
> **Version:** 1.0.0  
> **Date:** 2026-04-03

---

## Overview

This document describes the architecture for integrating EGOS with Obsidian following Andrej Karpathy's knowledge base pattern. The goal is to transform scattered documentation across 9 repositories into a unified, LLM-maintained knowledge system.

## Core Pattern (Karpathy)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   raw/      │ →  │  wiki/      │ →  │  outputs/   │
│  (sources)  │    │ (compiled)  │    │(dashboards) │
└─────────────┘    └─────────────┘    └─────────────┘
       ↑                                    │
       └────────────────────────────────────┘
              (feedback loop)
```

**Key insight:** The LLM maintains the wiki. You rarely touch it directly.

## EGOS Implementation

### 1. Vault Structure

```
~/Obsidian Vault/EGOS/
├── 00 - Inbox/           # Temporary captures
├── 01 - Raw Sources/     # Copied from all repos
│   ├── egos/            # AGENTS.md, TASKS.md, docs/
│   ├── egos-lab/        # Eagle Eye, archived apps
│   ├── 852/             # PII scanner
│   ├── forja/           # WhatsApp/cameras
│   ├── carteira-livre/  # Financial
│   └── ...
├── 02 - Wiki/           # LLM-compiled knowledge
│   ├── Index.md         # Master index
│   ├── Repositories/    # Per-repo articles
│   ├── Concepts/        # Cross-cutting topics
│   └── Patterns/        # Design patterns
├── 03 - Sessions/       # /start → /end handoffs
│   ├── Session 2026-04-03.md
│   └── Session 2026-04-02.md
├── 04 - Outputs/        # Dashboards, reports
│   ├── Dashboard - EGOS State.md
│   └── Reports/
├── 05 - Templates/      # Obsidian templates
└── 99 - Archive/        # Old versions, attachments
```

### 2. Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     EGOS Ecosystem                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  egos   │  │egos-lab │  │   852   │  │  forja  │  ...  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                      │                                      │
│           ┌────────▼────────┐                              │
│           │ obsidian-export.ts │                             │
│           │  (bun run obsidian:sync)                        │
│           └────────┬────────┘                              │
└────────────────────┼────────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  Obsidian Vault/EGOS/  │
         │                       │
         │  • Raw sources        │
         │  • Compiled wiki      │
         │  • Session logs       │
         │  • Dashboards         │
         └───────────────────────┘
                     │
         ┌───────────▼───────────┐
         │      Obsidian IDE     │
         │  (frontend/visual)    │
         └───────────────────────┘
```

### 3. Components

#### Raw Sources (`01 - Raw Sources/`)

**What:** Priority files copied from each repo

| Repo | Priority Files |
|------|---------------|
| egos | AGENTS.md, TASKS.md, README.md, HARVEST.md, docs/, .guarani/ |
| egos-lab | Eagle Eye docs, archived apps |
| 852 | PII scanner implementation |
| forja | Business docs, pricing |
| carteira-livre | Product docs |

**Sync frequency:** After each `/start` or on-demand via `bun run obsidian:sync`

#### Wiki (`02 - Wiki/`)

**What:** LLM-compiled knowledge

**Structure:**
- `Index.md` — Master navigation
- `Repositories/` — Per-repo deep dives
- `Concepts/` — Cross-cutting topics
  - Governance
  - Agents/Runtime
  - Integrations/MCP
  - PII Detection
  - Session Management
- `Patterns/` — Reusable patterns
  - Karpathy Knowledge Base
  - AAR (Adaptive Atomic Retrieval)
  - SSOT Governance

**Auto-generated:** Yes, via LLM compilation

#### Sessions (`03 - Sessions/`)

**What:** Per-session handoffs from `/start` → `/end`

**Format:**
```markdown
# Session YYYY-MM-DD

## Summary
## Integration Status (table)
## Completed
## In Progress  
## Blockers
## Insights
## Files Modified
## Related (backlinks)
```

#### Outputs (`04 - Outputs/`)

**What:** Visual dashboards and reports

**Types:**
- Dashboard — Real-time ecosystem health
- Weekly Report — Progress, velocity, blockers
- Capability Map — 160 capabilities, 13 domains
- Dependency Graph — Mermaid diagrams

### 4. Commands

```bash
# Initialize vault structure
bun run obsidian:init

# Sync all repos to Obsidian
bun run obsidian:sync

# Validate wiki health (TODO)
bun run obsidian:lint

# Part of /start workflow (future)
bun run start --export-obsidian
```

### 5. Obsidian Plugins Recommended

| Plugin | Purpose |
|--------|---------|
| **Dataview** | SQL-like queries on markdown |
| **Graph View** | Visual knowledge graph |
| **Calendar** | Session timeline |
| **Templater** | Dynamic templates |
| **Obsidian Git** | Version control |
| **Periodic Notes** | Daily/weekly templates |

### 6. Auto-Improvement Loop

```
┌──────────────────────────────────────────┐
│           Auto-Improvement Loop          │
├──────────────────────────────────────────┤
│                                          │
│  1. /start diagnostic                     │
│     ↓                                    │
│  2. Agent analyzes changes               │
│     ↓                                    │
│  3. Update session log                   │
│     ↓                                    │
│  4. LLM compiles insights to wiki       │
│     ↓                                    │
│  5. Generate dashboard update            │
│     ↓                                    │
│  6. /end with summary                    │
│     ↓                                    │
│  7. (Loop) Next session refines further │
│                                          │
└──────────────────────────────────────────┘
```

## Integration with Existing EGOS Systems

### Codebase Memory MCP

**Already have:** 51K nodes, 75K edges indexed

**Integration:** Codebase queries → Obsidian wiki articles

```typescript
// Example: Generate repo overview from codebase-memory
const nodes = await searchGraph({ repo: 'egos', type: 'function' });
const article = await compileToWiki(nodes, 'EGOS Functions Overview');
await writeToObsidian('02 - Wiki/EGOS Functions.md', article);
```

### Atomizer + Search Engine

**Already have:** `@egos/atomizer`, `@egos/search-engine`

**Integration:** Atomize new docs → index → search from Obsidian

### Session Initialization v6.0

**Integration point:** Auto-export after `/start`

```typescript
// In start-v6.ts
if (flags.exportObsidian) {
  await runObsidianExport();
}
```

## Benefits

| Problem | Solution |
|---------|----------|
| **Fragmentation** | 9 repos → 1 unified view |
| **Context loss** | Session logs persist in wiki |
| **No big picture** | Dashboard shows real-time state |
| **Knowledge silos** | Cross-repo concepts linked |
| **Manual updates** | Auto-sync via `obsidian-export.ts` |
| **No memory** | Historical sessions searchable |

## Future Enhancements

1. **Agent Wiki-Compiler** — Dedicated agent to maintain wiki
2. **Query Interface** — Natural language queries against wiki
3. **Weekly Reports** — Auto-generated progress reports
4. **Drift Alerts** — Wiki flags when sources diverge
5. **Knowledge Metrics** — Track coverage, freshness, gaps

## References

- Karpathy post: https://x.com/karpathy/status/...
- EGOS codebase-memory-mcp: 51K nodes
- Obsidian: https://obsidian.md
- Dataview plugin: https://github.com/blacksmithgu/obsidian-dataview

---

*Architecture version 1.0.0 | EGOS Kernel*
