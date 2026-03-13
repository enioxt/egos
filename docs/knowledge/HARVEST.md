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

## Mycelium

- Mycelium references in the kernel must distinguish **present**, **partial**, and **planned** layers instead of implying all historical surfaces exist locally.
