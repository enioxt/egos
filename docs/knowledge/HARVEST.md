# HARVEST.md — EGOS Core Knowledge

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-13
> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo

## Activation Hardening

- Core workflows must be **repo-role-aware**. The kernel cannot assume `egos-lab`-only surfaces like `session:guard`, Gem Hunter, or report-generation directories.
- `docs/SYSTEM_MAP.md` is the repo-local activation surface for the kernel. Cross-repo topology still starts at `~/.egos/SYSTEM_MAP.md`.
- `bun run governance:check` and `bun run ssot:link` are canonical local readiness checks for the kernel repo.

## Chatbot SSOT

- The core repo is the SSOT holder for shared chatbot primitives and compliance rules, not the production chatbot surface itself.
- `docs/CAPABILITY_REGISTRY.md` and `docs/modules/CHATBOT_SSOT.md` must stay aligned with real adoption evidence.

## Cross-Repo Chatbot Hardening (2026-03-13)

- **Python adapter pattern:** Port `atrian.ts`, `pii-scanner.ts`, `conversation-memory.ts` semantics into a single `chatbot_ssot.py` in the target repo's `services/` folder. Functions must match names the compliance-checker agent looks for (`scanForPII`, `sanitizeText`, `buildConversationMemoryBlock`, `validateResponse`). No external deps; stdlib only.
- **In-memory rate limiter (TypeScript):** When a leaf repo can't use `@egos-lab/shared`, implement `RateLimiter` class with `Map`-based buckets (`windowMs`, `max`). Single-file, zero deps, drop into `src/lib/chat/rate-limiter.ts`.
- **Chat guard helper:** Wrap memory-context, PII sanitization, and ATRiAN validation into a single `_chat-guard.ts` (for serverless) or `chatbot_ssot.py` (for Python) so the route/endpoint stays thin.
- **Validation sequence in chat endpoints:** `buildMemoryContext → call LLM → scanForPII(response) → sanitizeText → validateResponse(ATRiAN) → return`. Never skip ATRiAN step even when PII is clean.
- **Compliance evidence:** `chatbot_compliance_checker --dry --target=/path` gives 100/100 when all 7 SSOT signals are present. Use this as gate before marking EGOS-0XX complete.

## Context Tracker

- **CTX score formula:** uncommitted × 4 + session_commits × 2 + changed_code_files × 1 + handoff_KB × 0.5 + agent_runs × 8. Max 280.
- **Zones:** 0–100 safe, 101–180 warn, 181–250 high, 251+ critical (auto /end).
- **Run before long multi-step tasks:** `bun agent:run context_tracker --dry` gives instant CTX estimate.
- **Auto-trigger:** If agent detects CTX ≥ 250 it MUST emit `/end` autonomously — user should then open a new chat continuing from the generated handoff.

## Governance Propagation Automation

- Remove interactive `read -p "y/n"` prompts from `governance-sync.sh`. Replace with `--auto` flag or `EGOS_AUTO_PROPAGATE=1` env var.
- Pre-commit hook should block commits that change canonical governance files without a subsequent `governance:sync:exec` pass.
- `.windsurfrules` MANDAMENTO 15: governance changes are not complete until `bun run governance:sync:exec` + `bun run governance:check` return 0 drift.

## Workflow Inheritance

- Shared workflows such as `/start`, `/end`, and `/disseminate` should live in the kernel and propagate through `~/.egos/workflows`.
- Leaf repos should either use a symlink/exact inherited copy or a thin local wrapper only when repo-specific precedence is truly required.
- Exact-match local copies are drift magnets and should be re-linked to the shared source instead of being maintained by hand.
- Repo-local overrides are legitimate only when they protect local truth or sensitivity constraints, such as mapped-only or sigiloso workspaces.

## Cheap-First Orchestration

- The winning pattern is not multi-model fanout. Use one coordinator and route sequentially by cost and confidence.
- Default order: local tools and code search first, cheap triage model second, premium reasoning model only on blockers, reviewer model last for proof-of-work.
- Keep user-scope secrets and MCP auth outside repo-tracked files; keep repo instructions local; keep shared governance in `~/.egos`.

## External-Input Hardening

- Treat issue titles, PR text, web pages, and imported documents as untrusted input until sanitized.
- Agents that read untrusted input must not also hold publish, cache-mutation, or broad shell privileges.
- High-impact actions must stay behind an explicit human gate, even when the analysis path is automated.

## Mycelium

- Mycelium references in the kernel must distinguish **present**, **partial**, and **planned** layers instead of implying all historical surfaces exist locally.
