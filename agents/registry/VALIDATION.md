# Agent Registry Validation — Lightweight Provenance

> **Version:** 1.0.0 | **Purpose:** Cache de validação de agentes com hash de integridade
> **Updated:** On demand (not every run) — when agents.json changes or explicit validation triggered

## Por que existe

O `agents.json` é o SSOT de agentes, mas NÃO inclui validação de existência em runtime. O `drift-sentinel` detecta drift, mas tem falsos positivos em paths não-padrão (`scripts/`, `agents/api/`).

Este arquivo (`validation.json`) é o **SSOT de validação** — prova que cada agente foi verificado e onde.

## Estrutura

```json
{
  "lastValidated": "2026-04-03T12:30:00Z",
  "validator": "cascade-agent",
  "validationSource": "/home/enio/egos/agents/registry/agents.json",
  "validationMethod": "4-point-check",
  "agents": [
    {
      "id": "kol-discovery",
      "entrypoint": "scripts/kol-discovery.ts",
      "status": "active",
      "exists": true,
      "verifiedAt": "2026-04-03T12:30:00Z",
      "validationHash": "sha256:9c5d1e..."
    }
  ],
  "stats": { "total": 13, "verified": 13, "ghosts": 0, "dead": 2, "orphanFiles": 0 }
}
```

## Quando atualizar

**NÃO atualizar automaticamente a cada run** — isso deixaria o sistema lento.

Atualizar apenas quando:
1. `agents.json` foi modificado (detectado via hash)
2. Validação explícita solicitada (`bun agent:run agent-validator --exec`)
3. Passou 24h desde última validação E há suspeita de drift

## Validação 4-Point Check

Cada entrada neste arquivo foi verificada via:

| Check | Ferramenta | Evidence |
|-------|-----------|----------|
| 1. Entrypoint lido | `read_file` em `agents.json` | Path string |
| 2. File existe | `existsSync` no path completo | Boolean |
| 3. Status verificado | `agents.json` campo `status` | "active"/"dead" |
| 4. Contexto validado | `kind`, `run_modes` | Tipo correto |

## Uso

```bash
# Verificar se validação está fresh
bun agents/registry/validator.ts --check

# Forçar re-validação
bun agents/registry/validator.ts --exec

# Apenas reportar (não atualizar arquivo)
bun agents/registry/validator.ts --dry
```

## Ground Truth Hierarchy

1. **agents.json** — SSOT de definição (o que DEVE existir)
2. **validation.json** — SSOT de verificação (o que FOI confirmado existir)
3. **drift-sentinel** — Detector de drift (pode ter falsos positivos)

**Regra:** Sempre confiar em `validation.json` > `drift-sentinel` para "agente existe/não existe".
