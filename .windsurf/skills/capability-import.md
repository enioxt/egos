# Skill: Capability Import

> **Version:** 1.0.0
> **Trigger:** When importing features from one repo to another

## Purpose

Standardized process for importing capabilities between EGOS repos.

## Import Process

### 1. Source Analysis

Identify the source capability:

```bash
# Find the module in source repo
grep -r "export function" src/lib/ --include="*.ts"
```

Document:
- Module path
- Dependencies
- External APIs used
- Configuration required

### 2. Target Assessment

Check target repo readiness:

- [ ] `@egos/shared` dependency installed
- [ ] Required env vars documented in `.env.example`
- [ ] SYSTEM_MAP.md exists

### 3. Import Decision Matrix

| Scope | Action | Example |
|-------|--------|---------|
| Framework-level | Add to `@egos/shared` | ATRiAN, PII Scanner |
| Domain-specific | Copy to target repo | Gamification |
| Config-only | Update env vars | API keys |

### 4. Implementation Steps

**For @egos/shared modules:**

1. Create module in `/home/enio/egos/packages/shared/src/`
2. Export from `index.ts`
3. Run `bun typecheck` in egos kernel
4. Update target repo's SYSTEM_MAP.md

**For local modules:**

1. Copy module to target repo's `src/lib/`
2. Adapt imports and dependencies
3. Update SYSTEM_MAP.md with new capability
4. Add to AGENTS.md capabilities table

### 5. Validation Checklist

- [ ] Module compiles without errors
- [ ] Dependencies resolved
- [ ] Env vars documented
- [ ] SYSTEM_MAP.md updated
- [ ] AGENTS.md updated
- [ ] Handoff created

## Common Import Sources

| Source | Capabilities |
|--------|-------------|
| 852 | ATRiAN, PII, Memory, Telemetry, Export |
| carteira-livre | WhatsApp, Payments, Multi-tenant |
| egos-lab | Agent Runtime, Gem Hunter |
| egos | Model Router, Rate Limiter |

## Anti-Patterns

- ❌ Copy without updating docs
- ❌ Import without checking dependencies
- ❌ Skip SYSTEM_MAP.md update
- ❌ Hardcode source-specific values
