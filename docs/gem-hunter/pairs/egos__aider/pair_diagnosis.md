# Gem Hunter Pair Diagnosis: EGOS ↔ Aider

**Date:** 2026-04-01
**Reference:** [Aider-AI/aider](https://github.com/Aider-AI/aider)
**Stars:** 42,667 | **License:** Apache 2.0 | **Language:** Python
**Study ID:** GH-011

---

## Architecture Comparison

| Category | EGOS State | Aider State | Gap |
|----------|-----------|-------------|-----|
| **coding_surface** | /study, /edit skills, pre-commit hooks | Full edit loop (extract→dry-run→apply→commit), 9 coder classes, dirty-commit safeguard | EGOS missing dry-run validation layer and pre-edit dirty-commit |
| **agent_runtime** | 35+ agents, MCP orchestration, CCR jobs | Monolithic single-agent; no sub-agents | EGOS more advanced. Aider proves simpler model is sufficient for targeted tasks |
| **memory_context** | codebase-memory-mcp (51K nodes), file-based memory | Repomap: tree-sitter + PageRank + chat-context weighting, binary search token budget | Aider's repomap is more sophisticated for per-task context; EGOS has more durable memory |
| **model_gateway** | Claude-only (Sonnet/Haiku via CCR) | 20+ providers (litellm), aliases ("sonnet"→claude), weak/editor model separation | Aider multi-model pattern is mature — cost control via weak model is actionable |
| **observability_evals** | No benchmark suite yet; Atrian OTel spans just started | SWE-Bench + Exercism benchmarks; metrics/plots over time; Docker reproducibility | Major gap: EGOS has no formal edit benchmark |
| **retrieval_context** | codebase-memory-mcp graph queries | Repomap (not RAG; summarized repo context per task) | Different approaches; Aider's context compression is complementary |
| **durable_workflow** | CCR scheduled jobs, no workflow engine | None (single-turn sessions) | Neither has durable workflow; EGOS CCR is ahead |
| **protocol_tooling** | MCP server/client, hooks, skills | No MCP, no plugin API; `cmd_*` naming convention only | EGOS significantly ahead |
| **product_surface** | Eagle Eye, Commons marketplace | Streamlit GUI (`--gui`), web scraping, browser mode | Different surfaces; neither directly reusable |
| **governance_safety** | .guarani, LGPD guard, pre-commit vocab guard | No equivalent; relies on user judgement | EGOS significantly ahead |

---

## Top 5 Transplant Candidates

| Pattern | Level | Evidence | Complexity | Risk | EGOS Value |
|---------|-------|----------|-----------|------|-----------|
| **Dry-run edit validation** | adapt_lightly | `base_coder.py: apply_edits_dry_run()` | Low | Low | Prevents destructive edits in Claude Code hooks/skills |
| **Dirty-commit safeguard** | adapt_lightly | `repo.py: dirty_commit()` — commits pre-existing changes before AI edits | Low | Low | Protects user work when Claude Code makes unrelated edits |
| **Repomap: PageRank + chat-context weighting** | adapt_heavily | `repomap.py` — tree-sitter + NetworkX PageRank, recency boost | High | Med | Improve codebase-memory-mcp relevance scoring |
| **SWE-Bench eval harness** | reimplement_from_idea | `/benchmark/benchmark.py` — real-world issue resolution metrics | Med | Low | EGOS needs a formal benchmark to validate agent edit quality |
| **Weak/editor model separation** | adapt_lightly | `models.py: weak_model, editor_model` — delegate cheap tasks to cheaper models | Low | Low | Cost reduction: use Haiku for lint/format, Sonnet for planning |

---

## Top 3 Anti-Patterns

| Anti-Pattern | Evidence | Why EGOS should avoid |
|-------------|----------|----------------------|
| **Monolithic main.py (62KB)** | `main.py` handles CLI + LLM + git + UI + config — 44KB | EGOS's modular agent architecture is explicitly better for multi-domain orchestration |
| **No external tool API** | `cmd_*` convention closes the system — adding new tools requires patching source | EGOS MCP hook/skill system is the right abstraction |
| **Single-agent only** | No sub-agent support, no parallel execution | Acceptable for terminal pair-programming; insufficient for EGOS's multi-domain tasks |

---

## Scorecard

| Factor | Weight | Score (0-100) | Weighted |
|--------|--------|--------------|---------|
| egos_relevance | 0.24 | 78 | 18.7 |
| transplantability | 0.18 | 72 | 13.0 |
| architectural_complementarity | 0.14 | 65 | 9.1 |
| novelty | 0.12 | 60 | 7.2 |
| maintenance_signal | 0.10 | 95 | 9.5 |
| doc_quality | 0.08 | 88 | 7.0 |
| license_clarity | 0.06 | 100 | 6.0 |
| operational_fit | 0.04 | 35 | 1.4 |
| observability_maturity | 0.04 | 45 | 1.8 |
| **TOTAL** | **1.00** | | **73.7** |

**Score: 73.7/100** — Above transplant threshold (70). Deep study validated.

**Operational fit is low (35)** because Aider is Python and EGOS is TypeScript/Bun — direct code transplant impossible. Pattern transplants only.
