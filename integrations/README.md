# EGOS Integrations

Standardized contracts, manifests, and compact distribution bundles for EGOS integrations.

## Surfaces

- `_contracts/` — interface-first contracts and stubs
- `manifests/` — release manifests used by the integration gate
- `distribution/` — compact artifacts ready to copy/share

## Release Contract

No integration can be called **validated** or **shareable** unless it has:

1. Contract/stub or implementation surface
2. Canonical SSOT reference
3. Setup + operations runbook refs
4. Runtime proof
5. Compact distribution artifact
6. Executable smoke check

Run:

```bash
bun run integration:check
bun run governance:check
```

## Current Kernel State

- `slack`, `discord`, `telegram`, `webhook`, `github` → `contract_only`
- `whatsapp-runtime` → `validated` pattern with manifest + distribution bundle

## Creating a New Integration

1. Add or update `integrations/_contracts/<channel>.ts`
2. Create `integrations/manifests/<id>.json`
3. Point manifest docs to canonical SSOT/setup/runbook refs
4. Add runtime proof (`log`, `endpoint`, `runbook`, or equivalent evidence)
5. Create `integrations/distribution/<id>/` with artifact + `.env.example` when applicable
6. Add a real `validation.smokeCommand`
7. Pass `bun run integration:check`

## Security

All integrations must:
- Read credentials from environment variables, never hardcode
- Provide `.env.example` when secrets/config are required
- Log access via EGOS audit system
- Handle rate limits with retry/backoff
- Declare runtime proof before being marked validated
