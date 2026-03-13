# VPS Synchronization Strategy

> **Date:** 2026-03-13
> **Status:** Proposed

## The Problem
We have successfully decoupled the core framework (`egos`) from the apps (`egos-lab`, `carteira-livre`). We have enforced SSOT across 7 local repos via `~/.egos` symlinks.
However, the **online VPS** (Contabo/Railway) environments are currently disconnected from this new governance reality.

## The Strategy: "Mycelial Push"

1. **The Kernel Push**
   - The VPS should NOT run `egos-lab` monolithic worker.
   - The VPS should clone the `egos` kernel and run it as a lightweight background daemon.

2. **The Worker Model (Railway)**
   - Railway currently runs `egos-lab-infrastructure` worker.
   - Update the Railway Dockerfile to pull `egos` (for runtime) and `egos-lab` (for agent definitions).
   - Use the `bun egos-init` script inside the Docker container to reconstruct the exact same symlink structure we use locally.

3. **The VPS Model (Contabo)**
   - Used for heavy tasks (Neo4j, DataJud bots).
   - We will deploy `egos-commander` (a lightweight agent router) that listens for Mycelium Bus events over Redis.

## Change Map Versioning (The "Ecosystem Genesis" Ledger)

To maintain sanity, we will use a **Decentralized Ledger of Changes** (JSONL) instead of a monolithic markdown file.

- **File:** `~/.egos/change-map.jsonl`
- **Format:** `{"date": "...", "version": "v1.2.0", "repo": "egos", "change": "Extracted orchestrator", "vps_synced": false}`
- **Sync Agent:** A new agent (`vps_sync_agent`) will read this file, SSH into the VPS, apply the changes, and mark `vps_synced: true`.
