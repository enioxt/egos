# Migration Plan — egos-lab → egos

> **Version:** 1.0.0 | **Created:** 2026-03-13
> **Status:** Active — Phase 1 complete, Phase 2 in progress

## Architecture Decision

```
egos/          → Canonical kernel (governance + runtime + shared)
egos-lab/      → Incubator (apps + agent implementations + experiments)
~/.egos/       → Shared governance home (syncs to all repos)
```

### What Lives WHERE

| Category | Lives in `egos/` | Lives in `egos-lab/` |
|----------|-----------------|---------------------|
| `.guarani/orchestration/` | ✅ SSOT | Symlink or copy |
| `.guarani/refinery/` | ✅ SSOT | Symlink or copy |
| `.guarani/prompts/` | ✅ SSOT | Symlink or copy |
| `.guarani/security/` | ✅ SSOT | Symlink or copy |
| `.guarani/tools/` | ✅ SSOT | Symlink or copy |
| `agents/runtime/` | ✅ SSOT (frozen) | Import via package |
| `agents/registry/schema.json` | ✅ SSOT | Copy |
| `packages/shared/` | ✅ SSOT | Import via workspace |
| `.windsurf/workflows/` (core) | ✅ SSOT | Symlink or copy |
| Agent implementations | ❌ | ✅ SSOT |
| Apps (egos-web, etc.) | ❌ | ✅ SSOT |
| Domain docs (nexus, etc.) | ❌ | ✅ SSOT |
| Experiment scripts | ❌ | ✅ SSOT |

## Sync Direction: ONE-WAY (egos → leaves)

```
egos/ (kernel)
  ↓ governance-sync (automated)
  ├── egos-lab/
  ├── 852/
  ├── br-acc/
  ├── carteira-livre/
  ├── forja/
  ├── policia/
  └── egos-self/
```

**Rule:** Governance improvements MUST be made in `egos/` first,
then synced downstream. NEVER the reverse.

## Anti-Drift Protocol

### Problem
If we keep working in egos-lab and governance files improve there,
egos/ becomes stale. This MUST NOT happen.

### Solution: 3-Layer Protection

1. **Pre-commit in egos-lab**: Warn if `.guarani/` files are modified
   → "Did you mean to edit egos/ instead?"

2. **governance-sync script**: Runs daily or on-demand
   → Copies egos/.guarani/ → all leaf repos
   → Reports any local modifications in leaves

3. **CI check in egos/**: GitHub Action validates
   → All .guarani/ files match ~/.egos/ canonical copies
   → No SSOT drift detected

## Migration Timeline

### Phase 1 ✅ DONE (2026-03-13)
- Created egos/ with core runtime, registry, shared packages
- Cherry-picked governance from egos-lab
- Pushed to github.com/enioxt/egos

### Phase 2 ✅ DONE (2026-03-13)
- Deep scan of 15 directories
- Cherry-picked refinery, preprocessor, security, tools, standards
- Added 7 core workflows
- Added 4 concept reference docs
- Result: 65 files, 6,729 lines

### Phase 3 — Sync System (NOW)
- [ ] Build governance-sync script
- [ ] Add .egos symlink to egos/
- [ ] Validate pre-commit hooks end-to-end
- [ ] First commit with full governance

### Phase 4 — CI + First Agent Migration
- [ ] GitHub Actions CI for egos/
- [ ] Migrate one agent from egos-lab as proof-of-concept
- [ ] Document the agent migration pattern

### Phase 5 — Publication Ready
- [ ] egos-init one-command installer
- [ ] Write first article for dev.to / x.com
- [ ] Create CONTRIBUTING.md with governance rules

## Repos to Reduce/Archive

| Repo | Decision | Reason |
|------|----------|--------|
| `EGOSv2` | Archive | Stub (28K), already in egos-archive |
| `egos-archive` | Keep read-only | 7.6GB historical reference |
| `INTELINK` | Archive | Legacy, not maintained |
| `clipmon` | Keep | Small independent tool |
| `BrandForge` | Archive | Concept absorbed, not active |
| `personal` | Keep | CVs, non-code |
| `INPI` | Keep active | Governed leaf project |

## Metrics (Before → After)

| Metric | egos-lab (before) | egos/ (after) |
|--------|------------------|---------------|
| Total files | 1000+ | 65 |
| .guarani/ files | 23 | 29 |
| Workflows | 21+ | 7 (core only) |
| Agent implementations | 20 | 0 (clean) |
| Apps | 7 | 0 (clean) |
| Pre-commit checks | 4 | 4 (max enforcement) |
| SSOT files in limits | Partial | 100% |
| tsc --noEmit | Pass | Pass |
