# SSOT_REGISTRY.md — EGOS Cross-Repo Registry

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-20
> **PURPOSE:** canonical registry for the SSOT surfaces that govern the EGOS workspace.

## Registry Contract

- `kernel_canonical` means the source lives in `egos` and must propagate outward.
- `leaf_local` means the source lives in the repo and must not be overwritten by the kernel.
- `shared_home` means the synced copy in `~/.egos/` used by mapped repos.
- Every SSOT must declare owner, enforcement point, and freshness rule.

## Canonical Global SSOTs

| Surface | Class | Canonical Source | Shared Copy | Enforcement |
|---|---|---|---|---|
| Governance DNA | `kernel_canonical` | `egos/.guarani/` | `~/.egos/guarani/` | `governance:sync`, pre-commit |
| Shared Workflows | `kernel_canonical` | `egos/.windsurf/workflows/` | `~/.egos/workflows/` | `governance:sync`, pre-commit |
| Capability Registry | `kernel_canonical` | `egos/docs/CAPABILITY_REGISTRY.md` | `~/.egos/docs/CAPABILITY_REGISTRY.md` | `governance:check` |
| Chatbot SSOT | `kernel_canonical` | `egos/docs/modules/CHATBOT_SSOT.md` | `~/.egos/docs/modules/CHATBOT_SSOT.md` | compliance checks |
| SSOT Registry | `kernel_canonical` | `egos/docs/SSOT_REGISTRY.md` | `~/.egos/docs/SSOT_REGISTRY.md` | `governance:check` |

## Required Local SSOTs per Repo

| Surface | Class | Required In | Notes |
|---|---|---|---|
| `AGENTS.md` | `leaf_local` | every repo | identity, runtime, commands |
| `TASKS.md` | `leaf_local` | every repo | execution SSOT |
| `.windsurfrules` | `leaf_local` | every repo | repo-local governance |
| `docs/SYSTEM_MAP.md` or local equivalent | `leaf_local` | every repo | human + machine map |
| `docs/knowledge/HARVEST.md` | `leaf_local` | when repo keeps knowledge docs | local learnings |

## Freshness Rules

1. New global governance surface: update this file, `docs/CAPABILITY_REGISTRY.md`, and `docs/SYSTEM_MAP.md` in `egos`.
2. New repo-local capability: update local `AGENTS.md`, local `TASKS.md`, and local system map.
3. Any staged change to a canonical global SSOT must pass `bun run governance:check`.
4. Any staged change to a repo-local SSOT must pass local doc freshness checks.

## Workspace Adoption Targets

- `egos-lab`: consume the registry as non-canonical lab surface.
- `carteira-livre`: map leaf-local SSOTs to the registry and extract shared candidates.
- `forja`: adopt the same leaf-local contract and shared pointers.
- `852`, `policia`, `br-acc`: add explicit local pointers to this registry in tasks/maps.

## Update Flow

1. Edit kernel canonical SSOT in `egos`.
2. Run `bun run governance:sync:exec`.
3. Run `bun run governance:check`.
4. Update affected leaf `TASKS.md` and system maps.
5. Record learnings in `docs/knowledge/HARVEST.md` and `/disseminate`.
