# EGOS Investigation Protocol

> **Version:** 1.0.0 | **Updated:** 2026-04-03
> **Source:** CLAUDE.md v2.4.0, sections §20-§21
> **Scope:** All AI sessions performing discovery or architecture decisions
> **Propagated via:** governance-sync.sh

---

## §20. INVESTIGATION PROTOCOL (P20 — All Requests)

Every request involving discovery or architecture decisions MUST produce a structured investigation report.

### Report Template

```markdown
## Investigation: [TITLE]

### Sources Consulted
- [ ] Codebase (files, grep, graph)
- [ ] Supabase (tables, functions, logs)
- [ ] VPS (services, configs, health)
- [ ] External (APIs, docs, references)
- [ ] Memory (knowledge graph, previous sessions)

### Findings

**FACT** (verified, evidence-linked):
- ...

**INFERENCE** (logical deduction, not directly observed):
- ...

**PROPOSAL** (recommended action):
- ...

### Decision
- **Chosen path:** ...
- **Alternatives considered:** ...
- **Risks:** ...

### Dissemination
- [ ] TASKS.md updated
- [ ] HARVEST.md updated
- [ ] Memory/knowledge graph updated
- [ ] Supabase logged (if applicable)
- [ ] WhatsApp/Telegram notified (if applicable)
```

### When to Use

This protocol applies when:
- Exploring unfamiliar parts of the codebase
- Making architecture decisions (new packages, integrations, patterns)
- Debugging production issues
- Evaluating third-party tools or services
- Answering strategic questions from Enio

### Severity Levels

| Level | Trigger | Required sections |
|-------|---------|-------------------|
| **Light** | Simple code question | Sources + Findings |
| **Standard** | Architecture decision | All sections |
| **Deep** | Production incident, strategic pivot | All sections + post-mortem |

---

## §21. ENIO'S VOCABULARY MAP (P20 — Translation Table)

Enio uses conceptual names. Always translate to technical equivalents:

| Enio says | Technical meaning |
|-----------|-------------------|
| **Mycelium** | Event Bus (Supabase Realtime + agent_events table) |
| **ARR** | Atomic Representation Retrieval (sentence-level search, packages/search-engine) |
| **Quantum Search** | ARR / vector similarity search (pgvector in Supabase) |
| **Tutor Melkin** | Personal AI assistant (agent-runner + messaging + knowledge base) |
| **Hermes** | Hermes-3 8B LLM model (for autonomous execution, not a service) |
| **Guard** | Guard Brasil API (PII detection + LGPD compliance) |
| **Eagle Eye** | OSINT Licitacoes platform (Eagle Eye on egos-lab) |
| **Consciousness Loop** | Master API Option C (cognitive architecture pattern) |
| **Dream Cycle** | Overnight batch processing (memory consolidation + maintenance) |
| **Disseminate** | Propagate knowledge/rules across entire ecosystem |

### Usage Rules

- Always use the **technical name** in code, configs, and file paths
- Use **Enio's name** in conversation and user-facing messages
- When both names appear in a prompt, prioritize the technical interpretation
- If a new term appears that isn't mapped, ask Enio to clarify and add it here

---

## Enforcement

- AI sessions MUST label findings as FACT / INFERENCE / PROPOSAL
- Unlabeled claims in investigation contexts are governance violations
- The vocabulary map is authoritative — do not invent new mappings without adding them here

## Cross-References

- Autonomy Rules: `.guarani/orchestration/AUTONOMY_RULES.md`
- Rules Index: `.guarani/RULES_INDEX.md`
- SSOT Registry: `docs/SSOT_REGISTRY.md`
