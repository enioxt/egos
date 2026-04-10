# Gem Hunter API
> **ID:** `gem-hunter-api` | **Status:** active | **Area:** intelligence | **Risk:** T1  
> **Entrypoint:** `agents/api/gem-hunter-server.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Standalone REST API for gem-hunter (Phase 1 product). Endpoints: GET /v1/findings, /v1/papers, /v1/signals, /v1/kols; POST /v1/hunt. Port 3097.

## Proof of Life
```bash
bun agents/api/gem-hunter-server.ts
```

## Triggers
manual, on_deploy

## Side Effects
http_server, spawn_agent

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
