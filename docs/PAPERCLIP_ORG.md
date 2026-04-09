# EGOS Org Chart — Paperclip Mapping (DASH-005)

> Maps EGOS agents to Paperclip's CEO→Director→IC hierarchy.
> Source of truth for DASH-004 registration script.
> Updated: 2026-04-09

## Hierarchy

```
EGOS Kernel (CEO)
  └── runner.ts + agents.json registry
  └── reports to: Enio Rocha (human)

Guard Brasil Domain (Director)
  └── guard-brasil-api container
  └── capabilities: PII detection, LGPD, ATRiAN validation
  └── reports to: EGOS Kernel

Gem Hunter Domain (Director)
  └── gem-hunter adaptive CCR
  └── capabilities: research, scoring, Telegram alerts
  └── reports to: EGOS Kernel

ARCH Domain (Director)
  └── codebase-miner, doc-drift-sentinel
  └── capabilities: archaeology, drift detection
  └── reports to: EGOS Kernel

FORJA Domain (Director)  [planned]
  └── forja-chatbot
  └── capabilities: metalurgia tools, WhatsApp/Email pipeline
  └── reports to: EGOS Kernel

Task Runners (IC level)
  └── disseminate-propagator — kernel propagation
  └── disseminate-verifier — verification
  └── auto-disseminate.sh — post-commit SSOT sync
  └── portfolio-sync.ts — living portfolio updater
  └── scoring-feedback-reader.ts — gem feedback loop [planned]
  └── reports to: respective Domain Director
```

## Paperclip Employee Spec

| Agent ID | Title | Role | Adapter | Reports To |
|----------|-------|------|---------|-----------|
| `egos-kernel` | EGOS Kernel | CEO | custom/egos | human |
| `guard-brasil` | Guard Brasil API | Director | custom/egos | egos-kernel |
| `gem-hunter` | Gem Hunter | Director | custom/egos | egos-kernel |
| `codebase-miner` | Codebase Archaeologist | IC | custom/egos | egos-kernel |
| `doc-drift-sentinel` | Doc Drift Sentinel | IC | custom/egos | egos-kernel |
| `disseminate-propagator` | Disseminate Propagator | IC | custom/egos | egos-kernel |

## Integration Status

| Component | Status | Blocked by |
|-----------|--------|-----------|
| Paperclip Docker deploy (DASH-002) | ✅ compose ready | — |
| EGOS agents registration (DASH-004) | 🔴 waiting | feat/external-adapter-phase1 merge |
| Guard Brasil compliance plugin (DASH-006) | 🔴 waiting | adapter API + DASH-004 |
| Heartbeat→Paperclip mapping (DASH-007) | 🟡 partial | PAP-001 ✅, needs Paperclip running |
| Per-agent budget (DASH-008) | 🔴 waiting | PAP-002 + adapter API |

## Adapter API (when feat/external-adapter-phase1 merges)

```typescript
// server/src/adapters/registry.ts
import { registerServerAdapter } from 'paperclip/server/adapters'

registerServerAdapter({
  type: 'custom/egos',
  name: 'EGOS Agent',
  // ... adapter config
})
```

## Caddy Route (add to VPS /opt/bracc/infra/Caddyfile)

```
paperclip.egos.ia.br {
    reverse_proxy localhost:3100
}
```
