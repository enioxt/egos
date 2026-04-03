## SSOT Validation Hierarchy Pattern (2026-04-03)

### Problem
Agent registry validation has no lightweight provenance layer. Every check requires reading agents.json + verifying file existence, which is slow. False positives from drift-sentinel cause confusion because there's no cached ground truth.

### Solution
Three-layer hierarchy with dedicated validation cache:

| Layer | File | Purpose | Update Frequency |
|-------|------|---------|------------------|
| Definition | `agents.json` | SSOT of what SHOULD exist | On agent changes |
| Verification | `validation.json` | SSOT of what WAS CONFIRMED to exist | On demand (< 24h) |
| Detection | `drift-sentinel` | Drift alerts (may have false positives) | Daily |

### Implementation

**validation.json structure:**
```json
{
  "lastValidated": "2026-04-03T12:35:00Z",
  "validator": "agent-validator",
  "agents": [
    {
      "id": "kol-discovery",
      "entrypoint": "scripts/kol-discovery.ts",
      "status": "active",
      "exists": true,
      "verifiedAt": "2026-04-03T12:35:00Z",
      "validationHash": "sha256:9c5d1e..."
    }
  ],
  "stats": { "total": 16, "verified": 14, "ghosts": 0, "dead": 2 }
}
```

**agent-validator.ts modes:**
```bash
--check   # Verify cache is fresh (< 24h), exit 0/1
--exec    # Re-validate all agents, write cache
--dry     # Preview without writing
```

### When to Update
- NÃO atualizar automaticamente a cada run
- Apenas quando: agents.json modificado, validação explícita solicitada, ou 24h+ stale

### Applied To
- `agents/registry/validation.json` — cache SSOT
- `agents/agents/agent-validator.ts` — validation agent
- `agents/registry/VALIDATION.md` — documentation
- `.windsurf/workflows/start.md` — SSOT hierarchy in /start

---

