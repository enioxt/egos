# Pair Analysis: EGOS ↔ Continue

> **Session:** 2026-04-01 | **Status:** COMPLETED
> **Reference:** https://github.com/continuedev/continue (32k stars, Apache-2.0)

## Executive Summary

Continue is a **PR-scoped AI checking system** (source control → CI status checks) built on Markdown-based agent configuration (`.continue/checks/`). EGOS is a **governance-first production AI runtime** (multi-agent orchestration, event-driven, TypeScript/Bun native). These are **orthogonal architectures** with high complementarity: Continue lacks governance at runtime, EGOS lacks the PR-native checking workflow.

---

## Architecture Comparison

| Category | EGOS | Continue |
|----------|------|----------|
| **coding_surface** | Skills (.claude/commands/), hooks | `.continue/checks/` markdown checks, IDE extensions |
| **agent_runtime** | TypeScript registry JSON SSOT | Markdown files, CLI invocation |
| **memory_context** | codebase-memory-mcp (51K nodes, 7 repos) | Stateless — MCP docs, no persistence |
| **model_gateway** | LLM routing matrix (Alibaba→OpenRouter→Gemini) | Model-agnostic (bring your own) |
| **observability_evals** | Guard Brasil PII masking, ATRiAN cost tracking | GitHub Actions status checks, no internal telemetry |
| **protocol_tooling** | MCP stdio-primary | MCP HTTP/SSE transport (remote-capable) |
| **durable_workflow** | Scheduled CCR jobs, event bus (Supabase) | Single PR lifecycle, no persistence |
| **product_surface** | Internal CLI, no PR integration | Direct GitHub integration, visual status checks |
| **governance_safety** | Deep (.guarani/ rules, drift detection, pre-commit) | Minimal (no registry, no drift detection) |
| **retrieval_context** | codebase-memory-mcp semantic search | Agent consumes docs via MCP |

---

## Top 5 Transplantable Patterns

| # | Pattern | Source | Level | Complexity | Risk | Why EGOS needs it |
|---|---------|--------|-------|-----------|------|-------------------|
| 1 | **Markdown-as-config for checks** | `.continue/checks/` | Adapt Light | M | L | Non-technical operators can author `.guarani/checks/` rules as prose + YAML frontmatter |
| 2 | **PR-native agent invocation** | GitHub Actions integration | Adapt Heavy | H | M | Pre-merge gate that runs ssot-auditor + code-intel on branch diffs |
| 3 | **MCP HTTP/SSE transport** | mcpServers config | Adopt | M | L | Enables SaaS deployments and multi-tenant MCP beyond stdio |
| 4 | **Hub-based secret injection** | `${{ secrets.X }}` pattern | Adapt Light | L | L | Move Guard Brasil tokens to central vault, env var interpolation |
| 5 | **Transport-agnostic tool definitions** | CLI entrypoint separation | Adopt | L | L | Decouple agent entrypoints (dry-run/execute) from tool registration |

---

## Top 3 Anti-Patterns (Avoid)

1. **Stateless evaluation** — Continue discards context between PR checks. EGOS must preserve correlation IDs and evidence chain (ATRiAN) across runs. Never adopt "check → discard" model.

2. **Flat config hierarchy** — Continue's root-level YAML doesn't scale to 50+ agents. Don't replicate — keep EGOS hierarchical governance (identity → orchestration → rules → prompts → MCP).

3. **No drift detection** — Continue doesn't validate `.continue/checks/` against actual agent implementations. EGOS MUST maintain agents.json SSOT with pre-commit schema validation.

---

## Category Gaps Revealed in EGOS

| Gap | EGOS Weakness | Hybrid Solution |
|-----|---------------|-----------------|
| **product_surface** | No PR-native integration | `/pr` workflow + GitHub App for EGOS agents |
| **protocol_tooling** | MCP stdio-primary only | Upgrade codebase-memory-mcp to HTTP transport |
| **coding_surface** | Skills not versioned as MCP resources | Formalize EGOS skills as versioned MCP resources |

---

## Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| egos_relevance | 72 | Complementary problem, not core EGOS use case |
| transplantability | 68 | 3 patterns highly adoptable, 2 need adaption |
| architectural_complementarity | 81 | High — minimal collision, fills PR-gate gap |
| novelty | 52 | Markdown-as-config mature; MCP HTTP recent |
| maintenance_signal | 78 | 32k stars, active, Apache-2.0 |
| doc_quality | 75 | Good README, CONTRIBUTING, docs/ |
| license_clarity | 100 | Apache-2.0, fully compatible |
| operational_fit | 65 | TS but different stack (VS Code extension vs CLI) |
| observability_maturity | 40 | Minimal internal observability |

**Weighted Total: ~71/100** — RECOMMEND STUDY (above 60 threshold)

---

## Next Repo Recommendation

Based on this session's blind spots:
1. **Aider** (`Aider-AI/aider`) — git-native safe editing loop, fills coding_surface gap
2. **LangGraph** (`langchain-ai/langgraph`) — durable workflow, state persistence
3. **OpenHands** (`OpenHands/OpenHands`) — full agent stack for comparison vs EGOS kernel
