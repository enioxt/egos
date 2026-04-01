# NEURAL MESH — EGOS Cross-Reference Architecture

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-31
> **STATUS:** SPEC — Implementation tasks at bottom
> **AUTHOR:** Architecture session (Claude Opus + Enio)

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** master architecture for the EGOS cross-reference and knowledge interconnection system
- **Summary:** Unifies three existing systems (CRCDM, Mycelium, llmrefs) into a fractal, self-healing mesh that makes all EGOS files AI-navigable — from kernel core outward to leaf repos. Every file becomes a neuron; every cross-reference a synapse.
- **Read next:**
  - `docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md` — existing graph topology
  - `docs/concepts/mycelium/MYCELIUM_OVERVIEW.md` — layer separation
  - `docs/SSOT_REGISTRY.md` — canonical ownership registry
  - `docs/SYSTEM_MAP.md` — current activation map
  - `.guarani/RULES_INDEX.md` — governance lookup table

<!-- llmrefs:end -->

---

## 1. THE PROBLEM

AI agents reading EGOS repos today face a cold-start problem:
- They land on a file and don't know what else matters
- They can grep/glob, but that's brute-force — no intelligence about relationships
- Critical context lives in files they'll never discover without luck
- When an AI modifies code, it doesn't know what downstream files might be affected
- SSOTs drift because nothing enforces the links between them

**Three systems were built to solve this. None completed the job:**

| System | What it does | What it doesn't do |
|--------|-------------|-------------------|
| **CRCDM** (`~/.egos/crcdm/`) | Tracks changes across 9 repos via DAG + Merkle trees | Doesn't help AI navigate files. Tracks *changes*, not *knowledge*. |
| **Mycelium** (`packages/shared/src/mycelium/`) | TypeScript reference graph (27 nodes, 32 edges) | Runtime-only. Not embedded in files. AI must load the graph first. |
| **llmrefs** (`<!-- llmrefs:start -->` blocks) | File-embedded navigation for AI agents | Only 5 files have them. No validation. No tooling. |

**The insight:** What we need is **llmrefs everywhere** — backed by Mycelium's graph for validation and CRCDM's hooks for enforcement.

---

## 2. THE VISION

> *"Quando jogar isso no Obsidian, a visão seria um cérebro em conexão, sinergias, várias áreas se comunicando. Como a sinestesia que os fungos proporcionam — ver o cheiro, enxergar a música."*

A fractal system where:
- **Level 0 (Nucleus):** 5 kernel files, fully cross-referenced — the "brain stem"
- **Level 1 (Cortex):** `.guarani/`, `docs/`, `agents/` — governance and runtime
- **Level 2 (Limbic):** `packages/shared/` — reusable capabilities
- **Level 3 (Peripheral):** Leaf repos (852, forja, carteira-livre, etc.)

Every file has a **signature** (llmrefs block) that tells AI agents:
1. What this file IS (role)
2. What it's ABOUT (summary)
3. Where to go NEXT (read next — the synapses)

As the AI follows these paths, it loads exactly the context it needs — no more, no less.

---

## 3. ARCHITECTURE

### 3.1 The llmrefs Standard (Expanded)

Every file that matters gets this header:

```markdown
<!-- llmrefs:start -->
## LLM Reference Signature
- **Role:** <what this file does in the system>
- **Summary:** <one-sentence essence>
- **Level:** <0|1|2|3> — position in the fractal hierarchy
- **Read next:**
  - `relative/path.md` — **<category>** — why this matters
  - `another/file.ts` — **<category>** — why this matters
- **Read if:**
  - `path/to/file.md` — **<condition>** — only if working on X
<!-- llmrefs:end -->
```

**Categories** (typed edges): `governance`, `implementation`, `topology`, `data`, `test`, `deploy`, `security`, `design`

**"Read if" (conditional edges):** Only follow when the AI's current task matches the condition. This prevents context bloat.

### 3.2 The Four Layers

```
┌─────────────────────────────────────────┐
│  LAYER 4: VALIDATION & ENFORCEMENT      │
│  scripts/validate-llmrefs.ts            │
│  CRCDM hooks → auto-update on commit    │
│  pre-commit: warn on missing llmrefs    │
├─────────────────────────────────────────┤
│  LAYER 3: GRAPH EXTRACTION              │
│  scripts/extract-mesh-graph.ts          │
│  Reads all llmrefs → builds JSON graph  │
│  Exports to Obsidian / Mycelium / API   │
├─────────────────────────────────────────┤
│  LAYER 2: PROPAGATION                   │
│  governance-sync.sh enhanced            │
│  Kernel llmrefs → leaf repo templates   │
│  CRCDM detects → notifies dependents    │
├─────────────────────────────────────────┤
│  LAYER 1: FILE-LEVEL SIGNATURES         │
│  <!-- llmrefs:start/end --> blocks      │
│  Human + AI authored, machine-readable  │
│  THE foundation. Everything builds here │
└─────────────────────────────────────────┘
```

### 3.3 Level 0 — The Nucleus (5 files)

These 5 files form the "brain stem." Every AI session touches at least one:

```
AGENTS.md ←→ TASKS.md ←→ .windsurfrules
     ↕              ↕              ↕
docs/SYSTEM_MAP.md ←→ .guarani/IDENTITY.md
```

**Every nucleus file references all other nucleus files.** This is the fully-connected core. An AI landing on ANY of these reaches all 5 within one hop.

### 3.4 Level 1 — The Cortex (governance + docs)

```
.guarani/PREFERENCES.md          → Level 0: .windsurfrules, AGENTS.md
.guarani/orchestration/PIPELINE.md → Level 0: TASKS.md, AGENTS.md
.guarani/RULES_INDEX.md          → Level 0: all 5 nucleus files
docs/SSOT_REGISTRY.md            → Level 0: AGENTS.md, SYSTEM_MAP.md
docs/CAPABILITY_REGISTRY.md      → Level 0: AGENTS.md, TASKS.md
agents/registry/agents.json      → Level 0: AGENTS.md (comment header)
```

Level 1 files reference Level 0 (always) + sibling Level 1 files (when relevant). An AI at Level 1 is always one hop from the nucleus.

### 3.5 Level 2 — The Limbic System (packages/shared)

```
packages/shared/src/index.ts     → Level 1: docs/CAPABILITY_REGISTRY.md
packages/shared/src/pii-scanner.ts → Level 1: docs/CAPABILITY_REGISTRY.md
packages/shared/src/model-router.ts → Level 1: .guarani/orchestration/DOMAIN_RULES.md
```

TypeScript files use a JSDoc comment variant:

```typescript
/**
 * @llmref
 * Role: Brazilian PII detection engine (CPF, RG, CNPJ + 12 more patterns)
 * Level: 2
 * ReadNext: docs/CAPABILITY_REGISTRY.md (adoption tracking)
 * ReadIf: .guarani/orchestration/DOMAIN_RULES.md (when adding patterns)
 */
```

### 3.6 Level 3 — Peripheral (Leaf Repos)

Each leaf repo's `AGENTS.md` references the kernel:

```markdown
- **Read next:**
  - `/home/enio/egos/AGENTS.md` — **governance** — kernel identity and rules
  - `/home/enio/egos/docs/SSOT_REGISTRY.md` — **topology** — where SSOTs live
```

Leaf repos maintain their own internal mesh, but always have at least one upward reference to the kernel.

---

## 4. TOOLING

### 4.1 `scripts/validate-llmrefs.ts`

**Purpose:** Validate all llmrefs blocks across the repo (and optionally across all leaf repos).

**What it checks:**
1. Every file in a configurable "must-have" list has an llmrefs block
2. Every `Read next` path actually exists (no broken links)
3. Every Level 0 file references all other Level 0 files
4. Level 1 files have at least one upward reference to Level 0
5. No circular-only references (must always reach Level 0 in ≤3 hops)
6. Categories are from the allowed set

**Output:** JSON report + CLI summary

### 4.2 `scripts/extract-mesh-graph.ts`

**Purpose:** Parse all llmrefs blocks and produce a graph.

**Outputs:**
1. `mesh-graph.json` — nodes + edges (compatible with Mycelium reference-graph.ts)
2. `mesh-graph.obsidian.md` — Obsidian-compatible wiki-links for Canvas visualization
3. `mesh-graph.mermaid` — Mermaid diagram for docs
4. Optionally updates `packages/shared/src/mycelium/reference-graph.ts` seed data

### 4.3 `scripts/inject-llmrefs.ts`

**Purpose:** Scaffold llmrefs blocks into files that don't have them.

**Behavior:**
1. Reads file content
2. Infers Role from filename + first 10 lines
3. Infers Level from file path (root=0, .guarani=1, packages=2, etc.)
4. Suggests Read next from SSOT_REGISTRY + existing graph
5. Writes the block (with `<!-- TODO: verify -->` markers)

**NOT an auto-generator.** It scaffolds; humans/AI verify.

### 4.4 Pre-commit hook enhancement

Add to CRCDM's pre-commit:

```bash
# Neural Mesh: warn if modifying a file with llmrefs but not updating them
if file_has_llmrefs "$file" && llmrefs_stale "$file"; then
  warn "⚠️  $file has llmrefs — consider updating Read next references"
fi

# Neural Mesh: warn if creating a new file without llmrefs in must-have zones
if is_new_file "$file" && in_must_have_zone "$file" && ! file_has_llmrefs "$file"; then
  warn "⚠️  New file in must-have zone without llmrefs: $file"
fi
```

### 4.5 Feature/Module Registry (Knowledge Base)

**Purpose:** Before committing new code, check if similar functionality exists.

**Implementation:** A lightweight index generated from:
1. `docs/CAPABILITY_REGISTRY.md` — existing capabilities
2. `packages/shared/src/index.ts` — exported modules
3. `agents/registry/agents.json` — registered agents
4. llmrefs `Role` fields across all files

**Pre-commit check:**
```bash
# Extract keywords from changed files
# Compare against registry
# If >70% keyword overlap with existing capability → warn
echo "⚠️  Similar capability exists: pii-scanner.ts (85% keyword match)"
echo "    Consider reusing instead of duplicating."
```

---

## 5. SELF-HEALING MECHANISMS

### 5.1 Stale Reference Detection

When `validate-llmrefs.ts` runs (in pre-commit or CI):
- If a `Read next` target was deleted → **ERROR** (block commit)
- If a `Read next` target was moved → **WARN** + suggest new path
- If the llmrefs block hasn't been updated in 30+ days → **INFO** (review prompt)

### 5.2 Auto-Heal on Rename/Move

When CRCDM detects a file rename (via git diff):
1. Find all llmrefs blocks that reference the old path
2. Update references to new path
3. Stage the changes
4. Log the auto-heal event

### 5.3 Orphan Detection

Files that have no incoming references AND no outgoing references are "orphans." Monthly scan:
- Report orphaned files
- Suggest connections based on content similarity
- Flag for human review: keep, connect, or archive

### 5.4 Drift Reconciliation

Weekly (or on `/start`):
- Extract mesh graph from llmrefs
- Compare with Mycelium reference-graph.ts seed data
- Report discrepancies
- Optionally auto-update Mycelium seed to match llmrefs (llmrefs is SSOT)

---

## 6. OBSIDIAN VISUALIZATION

The extracted graph maps directly to Obsidian:
- Each file with llmrefs = a note
- Each `Read next` = a wiki-link
- Each Level = a folder/tag
- Categories = link types (color-coded)

**Expected result:** A brain-like graph view where:
- Nucleus (Level 0) is the dense center
- Cortex (Level 1) radiates outward
- Limbic (Level 2) forms clusters
- Peripheral (Level 3) are satellite nodes connected by thin bridges

---

## 7. IS THIS WORTH IT?

### What we gain:
1. **AI context quality:** Agents load exactly what they need, following typed edges
2. **Knowledge reuse:** Pre-commit warns before duplicating existing modules
3. **SSOT integrity:** Broken links caught at commit time, auto-healed on rename
4. **Onboarding:** New AI sessions (or humans) navigate the codebase via guided paths
5. **Obsidian brain:** Visual graph of the entire ecosystem for strategic thinking

### What it costs:
1. **Initial injection:** ~40 files need llmrefs blocks (2-3 hours with tooling)
2. **Three scripts:** validate, extract, inject (~400 lines total)
3. **Hook enhancement:** ~50 lines added to CRCDM pre-commit
4. **Maintenance:** Near-zero if self-healing works; ~10 min/week if manual

### Compared to alternatives:
- **/start + /end + /disseminate** solve session continuity but NOT inter-file navigation
- **CRCDM** tracks changes but doesn't guide AI through knowledge
- **Mycelium reference-graph.ts** is a runtime graph but not embedded in files
- **CLAUDE.md** gives rules but not file-to-file navigation

**Verdict:** Worth it. The three scripts + 40 llmrefs blocks deliver 80% of the vision. The self-healing hooks deliver the remaining 20% over time.

---

## 8. RELATIONSHIP TO EXISTING SYSTEMS

```
Neural Mesh = llmrefs (file signatures) + validation + extraction

Built ON TOP of:
├── CRCDM (change detection hooks → enforcement layer)
├── Mycelium reference-graph.ts (graph format → export target)
├── governance-sync.sh (propagation → leaf repo distribution)
└── .guarani/ (governance rules → where to enforce)

Does NOT replace:
├── /start, /end, /disseminate (session lifecycle — orthogonal)
├── CRCDM (still tracks changes independently)
├── Mycelium event bus (runtime events — different concern)
└── SSOT_REGISTRY (ownership tracking — feeds into llmrefs)
```

---

## 9. IMPLEMENTATION PRIORITY

| Phase | What | Effort | Depends on |
|-------|------|--------|------------|
| **Phase 1** | Inject llmrefs into Level 0 (5 nucleus files) | 30 min | Nothing |
| **Phase 2** | Inject llmrefs into Level 1 (10 governance files) | 1 hour | Phase 1 |
| **Phase 3** | Build `validate-llmrefs.ts` | 2 hours | Phase 1 |
| **Phase 4** | Build `extract-mesh-graph.ts` | 2 hours | Phase 3 |
| **Phase 5** | Build `inject-llmrefs.ts` (scaffolder) | 1.5 hours | Phase 3 |
| **Phase 6** | Inject llmrefs into Level 2 (packages/shared) | 1 hour | Phase 5 |
| **Phase 7** | CRCDM hook enhancement (self-healing) | 1 hour | Phase 3 |
| **Phase 8** | Feature/module registry + pre-commit check | 2 hours | Phase 4 |
| **Phase 9** | Leaf repo propagation (Level 3) | 2 hours | Phase 7 |
| **Phase 10** | Obsidian export + Mycelium seed sync | 1 hour | Phase 4 |

**Total: ~14 hours across 10 phases.**

---

*This document is the SSOT for Neural Mesh architecture. Implementation tasks tracked in TASKS.md.*
