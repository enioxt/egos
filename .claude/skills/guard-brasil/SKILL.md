---
name: guard-brasil
description: Guard Brasil development, testing, and deployment. Use when working with PII detection, LGPD compliance, or Brazilian data patterns.
allowed-tools: Bash(bun *), Bash(npm *), Bash(curl *), Read, Edit
---

# Guard Brasil Development Skill

Work with Guard Brasil package, API, and deployment.

## Package structure
- `packages/guard-brasil/` - Core package (@egosbr/guard-brasil)
- `apps/api/` - REST API (Hetzner deployed)
- `apps/guard-brasil-web/` - Landing page + dashboard

## Common tasks

### Run tests
```bash
cd packages/guard-brasil
bun test
```

### Build package
```bash
cd packages/guard-brasil
bun run build
```

### Test API locally
```bash
cd apps/api
bun dev
```

### Test PII detection
```bash
curl -X POST http://localhost:3099/v1/inspect \
  -H "Content-Type: application/json" \
  -d '{"text": "Meu CPF é 123.456.789-00"}'
```

## PII Patterns (12 Brazilian types)
Located in `packages/guard-brasil/src/pii-patterns.ts`:
- CPF, RG, CNH, MASP, REDS, REG
- Processo, Placa, Título de Eleitor
- CNS, CEP, Telefone

## Deployment

**API Status:** Live at guard.egos.ia.br (port 3099, Caddy reverse proxy)
**Container:** `guard-brasil-api`
**Health check:** `curl https://guard.egos.ia.br/health`

## GTM Chain (P0)
1. npm publish (@egosbr/guard-brasil) - MANUAL M-001
2. DNS validation (guard.egos.ia.br) - MANUAL M-002
3. Cold outreach (20 CTOs) - MANUAL M-007
