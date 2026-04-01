# Neural Mesh — Investigation Report: Build vs Buy vs Compose

> **VERSION:** 1.0.0 | **DATE:** 2026-03-31
> **STATUS:** INVESTIGATION COMPLETE — Decision required
> **METHOD:** Exa web search (50+ results), deep crawl (15 tools), cross-reference with EGOS existing systems

<!-- llmrefs:start -->
## LLM Reference Signature
- **Role:** research report evaluating whether to build Neural Mesh from scratch, adopt existing tools, or compose a hybrid
- **Summary:** Investigated 20+ tools across 4 tiers. Verdict: COMPOSE — adopt codebase-memory-mcp (MCP knowledge graph) + @aiready/pattern-detect (duplicate detection) + keep CRCDM (change tracking). Don't build llmrefs tooling — the market has solved this better.
- **Read next:**
  - `docs/concepts/NEURAL_MESH_ARCHITECTURE.md` — **design** — original architecture spec (to be revised)
  - `TASKS.md` — **implementation** — EGOS-167..176 (to be revised based on this report)
  - `.guarani/orchestration/DOMAIN_RULES.md` — **governance** — domain checklists
<!-- llmrefs:end -->

---

## 1. WHAT WE WANTED

The Neural Mesh vision had **four pillars:**

| Pillar | Description |
|--------|------------|
| **P1: AI Navigation** | AI agents follow typed cross-references between files instead of brute-force grep |
| **P2: Knowledge Reuse** | Pre-commit warns before duplicating existing modules/features |
| **P3: Self-Healing SSOTs** | Broken links auto-detected, stale references auto-flagged, renames auto-propagated |
| **P4: Brain Visualization** | Obsidian-like graph view of the entire ecosystem |

---

## 2. WHAT THE MARKET OFFERS (2026-03-31)

### Tier 1: Knowledge Graph Engines (solve P1 + P4)

| Tool | Stars | Language | License | What it does |
|------|-------|----------|---------|-------------|
| **codebase-memory-mcp** | 1,100 | C | MIT | Single binary, 66 languages, 14 MCP tools, indexes Linux kernel in 3 min, 120x fewer tokens, 3D graph UI, auto-sync via git polling. **Best-in-class.** |
| **CodeGraphContext** | 2,663 | Python | MIT | Graph DB + MCP + CLI. 100k+ downloads. Strong community. |
| **GitNexus** | 14,000 | TypeScript | PolyForm NC | Most popular but **non-commercial license** — unusable for EGOS |
| **Axon** | 603 | Python | — | Web dashboard, force-directed graph |

**Verdict on codebase-memory-mcp:** This tool does 80% of what our `extract-mesh-graph.ts` + `validate-llmrefs.ts` were supposed to do — but better. It:
- Indexes all 12 EGOS repos in seconds
- Provides call chains, dependency graphs, blast radius analysis
- Has built-in 3D graph visualization (replaces our Obsidian export need)
- Auto-detects Claude Code and configures MCP + skills + hooks
- Single static binary, zero dependencies, MIT license

**What it DOESN'T do:** Cross-repo knowledge linking (it indexes one repo at a time), SSOT governance, documentation cross-references, feature/module registry.

### Tier 2: Semantic Code Navigation (solve P1)

| Tool | Stars | What it does |
|------|-------|-------------|
| **cx** | 202 | Rust CLI — file overviews, symbol search, definitions, references. 66% fewer file reads, 37% fewer re-reads. Injects into CLAUDE.md. |
| **Octocode MCP** | 751 | 13 MCP tools, LSP navigation, PR archaeology |
| **mcp-codebase-index** | 44 | 17 MCP query tools, incremental re-indexing via git diff, persistent disk cache |

**cx is elegant** — it teaches agents an "escalation hierarchy" (overview → symbols → definition → references → read). Proven: 66% reduction in read chains across 105 Claude Code sessions. But it's Rust (we don't have Rust in our stack) and only solves P1.

### Tier 3: Semantic Duplicate Detection (solves P2)

| Tool | Approach | What it does |
|------|----------|-------------|
| **@aiready/pattern-detect** | Jaccard similarity on AST tokens | Finds semantic duplicates (same logic, different syntax). Pre-commit hook + CI integration. 85% context token reduction in real projects. |
| **polydup-core** | Tree-sitter + Rabin-Karp | Cross-language duplicate detection library |
| **CodeClone** | Python AST | Structural duplication + maintainability metrics |

**@aiready/pattern-detect is exactly what EGOS-174 (feature registry pre-commit) was supposed to be.** It already has:
- Pre-commit hook integration
- CI/CD GitHub Actions
- Configurable thresholds per category (validators, formatters, API handlers, utilities)
- JSON output for downstream tooling

### Tier 4: Persistent AI Memory (cross-session context)

| Tool | Stars | What it does |
|------|-------|-------------|
| **Mem0** | — | Extraction-based memory with graph. 91% response time reduction. arXiv paper. |
| **Stompy / Truth Mesh** | — | Federated AI memory with confidence decay, conflict detection, delta evaluation. NATO-origin. |
| **claude-mem / agentmemory** | 65 | Persistent memory for AI coding agents via MCP |
| **SharedContext** | 46 | Cross-client memory, SQLite + AES-256, Arweave sync |
| **omega-memory** | 56 | Persistent memory via PostgreSQL |

**Truth Mesh (Stompy) is philosophically identical to our Mycelium vision** — federated nodes, confidence decay, conflict detection at scope boundaries, delta evaluation. But it's a SaaS product, not an open-source framework we can embed.

**What EGOS already has that covers this tier:**
- CLAUDE.md auto-memory (`~/.claude/projects/*/memory/`)
- CRCDM for cross-repo change tracking
- /start + /end + /disseminate for session lifecycle
- Mycelium reference-graph.ts for topology

### Tier 5: Context Packing & Documentation

| Tool | Stars | What it does |
|------|-------|-------------|
| **Repomix** | 22,444 | Packs entire repo into XML for LLM consumption. Tree-sitter compression ~70%. |
| **SpecWeave** | — | Living documentation sync: parses, classifies, distributes specs into cross-linked docs |
| **Documentation.AI** | — | GitHub-connected AI doc agent. Auto-aligns docs with code. |
| **Context+** | — | MCP server with RAG + Tree-sitter AST + Spectral Clustering + Obsidian-style linking |

**Context+ (ForLoopCodes/contextplus)** combines several things we wanted: RAG, AST analysis, spectral clustering, AND Obsidian-style linking. Worth evaluating as an alternative to building our own.

---

## 3. CROSS-REFERENCE WITH EGOS EXISTING SYSTEMS

| EGOS System | Status | What market tool replaces/complements it |
|-------------|--------|----------------------------------------|
| **CRCDM** (~/.egos/crcdm/) | Active, 1211 lines bash | **KEEP.** No tool does cross-repo change detection with DAG + Merkle trees + governance hooks. Unique to EGOS. |
| **Mycelium reference-graph.ts** | Phase 1, 300 lines TS | **REPLACE with codebase-memory-mcp.** The MCP tool builds a richer graph automatically from code (not manual seed data). |
| **Mycelium redis-bridge.ts** | Scaffold only | **DEFER.** Not needed if using codebase-memory-mcp for structural queries. |
| **llmrefs** (5 files have them) | Embryonic | **KEEP but simplify.** llmrefs serve a different purpose than code graphs — they guide AI through *documentation*, not code. Keep for key docs (~15 files), don't build tooling for them. |
| **/start, /end, /disseminate** | Active | **KEEP.** Session lifecycle is orthogonal to code intelligence. Nothing in the market replaces this. |
| **CLAUDE.md auto-memory** | Active | **KEEP.** This is our persistent cross-session memory. It works. |
| **governance-sync.sh** | Active | **KEEP.** Cross-repo governance propagation. Unique to EGOS. |

---

## 4. THE VERDICT: COMPOSE, DON'T BUILD

### What to ADOPT (install today, zero code):

| Tool | Solves | Effort | Priority |
|------|--------|--------|----------|
| **codebase-memory-mcp** | P1 (AI navigation) + P4 (graph visualization) | 5 min install, auto-configures Claude Code | **P0 — do first** |
| **@aiready/pattern-detect** | P2 (knowledge reuse / duplicate detection) | npm install + pre-commit hook | **P1** |
| **cx** (optional) | P1 (lighter alternative to codebase-memory-mcp) | cargo install or brew | P2 |

### What to KEEP (already built, unique to EGOS):

| System | Why keep it |
|--------|-----------|
| **CRCDM** | Cross-repo DAG — nothing in the market does this. Enhance with llmrefs staleness check. |
| **llmrefs blocks** | For documentation navigation (15 key .md files). Not for code. Manual authoring is fine. |
| **/start + /end + /disseminate** | Session lifecycle. Market tools don't cover this. |
| **governance-sync.sh** | EGOS governance propagation. Unique. |
| **CLAUDE.md + auto-memory** | Cross-session context. Works well enough. |

### What to KILL (don't build):

| Planned | Why kill it |
|---------|-----------|
| `scripts/validate-llmrefs.ts` (EGOS-169) | codebase-memory-mcp validates code structure better than our custom validator ever would. For docs, manual llmrefs in 15 files don't need a validator. |
| `scripts/extract-mesh-graph.ts` (EGOS-170) | codebase-memory-mcp exports richer graphs. 3D visualization included. |
| `scripts/inject-llmrefs.ts` (EGOS-171) | Injecting headers into every file is maintenance overhead with diminishing returns. The MCP knowledge graph makes file headers unnecessary for code navigation. |
| EGOS-172 (Level 2 JSDoc llmrefs) | MCP knowledge graph already indexes TypeScript with tree-sitter AST. No need for manual JSDoc annotations. |
| EGOS-176 (Obsidian export) | codebase-memory-mcp has built-in 3D graph UI at localhost:9749. |
| Mycelium Phase 2 (Redis bridge) | Premature. The event bus is fine for local communication. Distributed events not needed yet. |

### What to BUILD (small, EGOS-specific):

| Item | What | Effort |
|------|------|--------|
| **CRCDM enhancement** | Add llmrefs staleness check + new-file warning to pre-commit. Wire `codebase-memory-mcp` graph data into CRCDM impact analysis. | 2-3h |
| **llmrefs for 10 more key docs** | Manually add llmrefs to Level 0 + Level 1 governance files (15 total). No automation needed. | 1h |
| **Multi-repo MCP config** | Configure codebase-memory-mcp to index all 9 EGOS repos. Create a script that runs `index_repository` for each. | 30min |
| **@aiready pre-commit hook** | Wire `@aiready/pattern-detect` into CRCDM pre-commit for semantic duplicate detection. | 1h |

---

## 5. REVISED TASK LIST

Original EGOS-167..176 (14 hours estimated) → Revised plan (5 hours total):

| Task | What | Priority | Effort |
|------|------|----------|--------|
| **EGOS-167 (revised)** | Install codebase-memory-mcp, configure for all 9 repos, verify graph UI | P0 | 30min |
| **EGOS-168 (revised)** | Manually add llmrefs to 10 more governance docs (total 15 with llmrefs) | P1 | 1h |
| **EGOS-169 (revised)** | Install @aiready/pattern-detect, wire into CRCDM pre-commit | P1 | 1h |
| **EGOS-170 (revised)** | Enhance CRCDM: llmrefs staleness warning + codebase-memory-mcp integration | P2 | 2h |
| ~~EGOS-171~~ | KILLED — inject-llmrefs.ts not needed | — | — |
| ~~EGOS-172~~ | KILLED — JSDoc llmrefs not needed | — | — |
| **EGOS-173 (keep)** | CRCDM hook: auto-heal llmrefs on file rename | P2 | 30min |
| **EGOS-174 (revised)** | REPLACED by @aiready/pattern-detect | — | — |
| ~~EGOS-175~~ | SIMPLIFIED — just add kernel llmrefs pointers to leaf repo AGENTS.md files (manual) | P2 | 30min |
| ~~EGOS-176~~ | KILLED — codebase-memory-mcp has built-in 3D graph UI | — | — |

**Total: ~5.5 hours vs original 14 hours. Better result with less custom code.**

---

## 6. WHY THIS IS BETTER THAN BUILDING

### The original Neural Mesh architecture proposed:
- 3 custom scripts (~400 lines TypeScript)
- Custom graph extraction format
- Custom validation logic
- Custom Obsidian export
- Custom pre-commit duplicate detection
- Maintenance burden: indefinite

### The composed solution uses:
- **codebase-memory-mcp**: 1,100 stars, 20 contributors, C (blazing fast), MIT, 30 releases, active development
- **@aiready/pattern-detect**: Proven on real projects, 85% token reduction, CI/CD ready
- **CRCDM**: Already built, already working, just needs minor enhancement
- **llmrefs**: 15 manually-maintained blocks in governance docs (5 minutes each to update)

**The key insight:** The market has solved code-level intelligence (knowledge graphs, call chains, impact analysis) far better than we could build. What the market HASN'T solved is:
1. Cross-repo governance (CRCDM — we have this)
2. AI session lifecycle (/start, /end — we have this)
3. Documentation-level navigation (llmrefs — lightweight, manual is fine)
4. Framework governance propagation (governance-sync.sh — we have this)

**Our competitive advantage is governance, not code intelligence.** Build on that. Use the market for everything else.

---

## 7. THE TRUTH MESH CONNECTION

Markus Sandelin's "Truth Mesh" concept (federated AI memory with confidence decay, conflict detection, delta evaluation) is philosophically aligned with our Mycelium vision. Key takeaways:

- **Confidence decay** — SSOTs should lose trust over time unless revalidated. Our `/start` already does a version of this (checks freshness). Could formalize.
- **Delta evaluation** — When syncing across repos, only propagate what's new/changed/conflicting. CRCDM already does this with its DAG.
- **Conflict detection at scope boundaries** — When a kernel truth changes, leaf repos should be notified. governance-sync.sh does this partially.

**We don't need to build Truth Mesh.** We already have the primitives (CRCDM + governance-sync + /start freshness checks). What we can do is:
1. Add confidence decay to SSOT freshness checks in `/start`
2. Add conflict detection to governance-sync.sh (when a leaf repo's AGENTS.md diverges from kernel)
3. This is a 2-3 hour enhancement, not a new system.

---

## 8. RECOMMENDATION SUMMARY

```
┌─────────────────────────────────────────────┐
│  ADOPT: codebase-memory-mcp (MCP graph)     │  ← Replaces Mycelium + Obsidian export
│  ADOPT: @aiready/pattern-detect             │  ← Replaces feature registry pre-commit
│  KEEP:  CRCDM (enhance, don't replace)      │  ← Cross-repo DAG, unique to EGOS
│  KEEP:  llmrefs (15 files, manual)          │  ← Documentation navigation
│  KEEP:  /start + /end + /disseminate        │  ← Session lifecycle
│  KILL:  3 custom scripts (validate/extract/ │
│         inject-llmrefs)                      │  ← Market solved this better
│  KILL:  Mycelium Phase 2 (Redis bridge)     │  ← Not needed
│  KILL:  Obsidian export script              │  ← 3D graph UI built into MCP tool
└─────────────────────────────────────────────┘
```

**Net result:** 4 tools working together (codebase-memory-mcp + pattern-detect + CRCDM + llmrefs) delivering all 4 pillars of the Neural Mesh vision, with ~5 hours of integration work instead of ~14 hours of custom development.

---

## 9. SOURCES

### Tools Evaluated (20+)
- **codebase-memory-mcp** — github.com/DeusData/codebase-memory-mcp (1,100 stars, MIT)
- **CodeGraphContext** — github.com/CodeGraphContext/CodeGraphContext (2,663 stars, MIT)
- **GitNexus** — github.com/abhigyanpatwari/GitNexus (14,000 stars, PolyForm NC)
- **Axon** — github.com/harshkedia177/axon (603 stars)
- **cx** — github.com/ind-igo/cx (202 stars, MIT)
- **mcp-codebase-index** — github.com/MikeRecognex/mcp-codebase-index (44 stars, AGPL)
- **@aiready/pattern-detect** — github.com/caopengau/aiready-cli
- **Repomix** — github.com/yamadashy/repomix (22,444 stars)
- **Context+** — github.com/ForLoopCodes/contextplus
- **code-graph-rag** — github.com/vitali87/code-graph-rag (2,273 stars)
- **Code-Atlas** — github.com/SerPeter/code-atlas
- **CodexA** — github.com/M9nx/CodexA
- **SourceBridge** — github.com/jstuart0/sourcebridge
- **SharedContext** — github.com/Eversmile12/sharedcontext (46 stars)
- **omega-memory** — github.com/omega-memory/omega-memory (56 stars)
- **agentmemory** — github.com/rohitg00/agentmemory (65 stars)

### Research & Analysis
- Ry Walker — "Code Intelligence Tools for AI Agents Compared" (rywalker.com/research/code-intelligence-tools)
- Markus Sandelin — "The Truth Mesh: Federated AI Memory" (Medium, Feb 2026)
- Sourabh Sharma — "Persistent Memory for AI Coding Agents" (Medium, Feb 2026)
- Peng Cao — "Semantic Duplicate Detection with AST Analysis" (Medium, Feb 2026)
- Masaki Hirokawa — "Navigating Large Codebases with Claude Code" (claudelab.net, Mar 2026)
- SpecWeave — "Intelligent Living Docs Sync" (spec-weave.com)
- Documentation.AI — "AI Documentation Agent" (documentation.ai)

---

*This report is the SSOT for the Neural Mesh build-vs-buy decision. Implementation tasks to be revised in TASKS.md.*
