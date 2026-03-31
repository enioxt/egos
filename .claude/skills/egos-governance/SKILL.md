---
name: egos-governance
description: EGOS governance validation and sync. Use when checking drift, syncing repos, or validating SSOT compliance.
allowed-tools: Bash(bun *), Read, Grep, Glob
---

# EGOS Governance Skill

Validate and maintain EGOS governance across the ecosystem.

## Commands

### Check governance drift
```bash
bun run governance:check
```

### Sync governance (execute fixes)
```bash
bun run governance:sync:exec
```

### Validate doctor checks
```bash
bun run doctor --json
```

### Check SSOT compliance
```bash
grep -r "SSOT-VISIT" docs/
```

## Validation checklist

Before marking any governance task complete:

1. Run `bun run governance:check` (exit code 0 = no drift)
2. Run `bun run doctor` (exit code 0 = all healthy)
3. Verify SSOT files are fresh (<7 days old)
4. Check `.guarani/` symlinks are valid
5. Validate agents.json matches schema v2.0

## Quick health check

```bash
bun run doctor && bun run governance:check
```

If both pass (exit 0), governance is clean.
