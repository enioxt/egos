# Integration Release Contract — EGOS-131

**Version:** 1.0.0
**Date:** 2026-03-30
**Status:** ACTIVE

## Objective

No integration can be called **validated** or **shareable** in EGOS without complete documentation, runtime proof, a compact distribution artifact, and an executable release check.

## Required Artifacts

| Artifact | Required | Location |
|---|---|---|
| Manifest | yes | `integrations/manifests/<id>.json` |
| Canonical SSOT | yes | repo-local SSOT reference |
| Setup guide | yes | SSOT or setup doc reference |
| Ops runbook | yes | SSOT or runbook reference |
| Runtime proof | yes | file/log/endpoint reference |
| Distribution bundle | yes | `integrations/distribution/<id>/` |
| Smoke command | yes | manifest `validation.smokeCommand` |

## Release States

- `contract_only` — interface exists, not releaseable
- `draft` — artifacts incomplete
- `pilot` — runnable in one environment with proof
- `validated` — docs + proof + distribution + smoke check complete
- `deprecated` — frozen, replacement documented

## Mandatory Manifest Fields

- `id`, `channel`, `name`, `version`, `owner`, `status`, `authType`
- `events`, `actions`
- `documentation.ssot`, `documentation.setup`, `documentation.runbook`
- `runtimeProof[]`
- `distribution.kind`, `distribution.artifactRef`, `distribution.installCommand`
- `validation.smokeCommand`

## Claim Rules

- A contract stub in `integrations/_contracts/` is **not** enough to claim release readiness.
- A setup guide without a compact artifact is **not** shareable.
- A bundle without runtime proof is **not** validated.
- If secrets are required, use env vars only and provide `.env.example` in the bundle.

## Acceptance Gate

```bash
bun run integration:check
bun run governance:check
```

A validated integration must pass both commands before merge or dissemination.

## First Canonical Bundle

`whatsapp-runtime` is the first manifest-backed integration pattern in the kernel.

- Manifest: `integrations/manifests/whatsapp-runtime.json`
- Bundle: `integrations/distribution/whatsapp-runtime/`
- SSOT: `docs/knowledge/WHATSAPP_SSOT.md`

## Scope

This contract applies to kernel and leaf repos adopting EGOS integration patterns through synced governance.
