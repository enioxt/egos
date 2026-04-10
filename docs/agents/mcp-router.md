# MCP Router
> **ID:** `mcp-router` | **Status:** active | **Area:** infrastructure | **Risk:** T0  
> **Entrypoint:** `agents/agents/mcp-router.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Routes incoming MCP server discovery requests to the correct handler based on capability matching and server health status

## Proof of Life
```bash
bun agents/agents/mcp-router.ts --dry-run
```

## Triggers
manual

## Side Effects
none

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
