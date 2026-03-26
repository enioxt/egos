# egos-lab Consolidation Diagnostic

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-23 | **STATUS:** Active
> **TASK:** EGOS-073

---

## Purpose

Classify every active surface in `egos-lab` into one of these buckets:

| Classification | Meaning |
|---------------|---------|
| `migrate_to_egos` | Generic, kernel-level — migrate to `packages/shared` or `agents/` |
| `keep_in_lab` | App/infra specific — stays in egos-lab as production surface |
| `standalone_candidate` | Could be its own repo/package (npm, pip, standalone service) |
| `internal_infra` | Dev tooling / CI / scripts — stays internal |
| `archive` | No longer actively used, should be archived or deleted |
| `discard` | Confirmed dead code, delete |

---

## Surfaces Classified

### Apps (`apps/`)

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| `egos-web` | `keep_in_lab` | Main public website for egos.ia.br — production web app | Stay in egos-lab |
| `agent-028-template` | `keep_in_lab` | AIXBT dashboard — production surface, Vercel deploy | Stay in egos-lab → Phase 3 deploy |
| `commons` (within egos-web) | `keep_in_lab` | Marketplace — product-specific to egos-lab | Stay in egos-lab |

### Agents (`agents/`)

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| `report_generator` (#30) | `keep_in_lab` | Agent-028 specific — generates dashboard data | Stay in egos-lab |
| `gem-hunter` | `keep_in_lab` | Lab-specific code discovery agent | Stay in egos-lab |
| `dead_code_detector` | `migrate_to_egos` | Generic kernel utility — already migrated in egos | Migrated ✅ |

### Packages / Shared (`packages/`)

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| `@egos/shared` (lab copy) | `migrate_to_egos` | Kernel owns `@egos/shared` — lab should consume, not duplicate | Use kernel package |
| `llm-provider` (lab copy) | `migrate_to_egos` | Already in kernel — lab copy is stale | Remove, import from kernel |
| `atrian` (lab copy) | `migrate_to_egos` | Already in kernel — lab copy is stale | Remove, import from kernel |

### Documentation (`docs/`)

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| `SYSTEM_MAP.md` (lab) | `migrate_to_egos` | Kernel owns SSOT system map | Merge into kernel SYSTEM_MAP |
| `CAPABILITY_REGISTRY.md` (lab) | `migrate_to_egos` | Kernel owns capability registry | Merge into kernel CAPABILITY_REGISTRY |
| Lab-specific docs | `keep_in_lab` | App/infra specific docs | Stay in egos-lab |
| Stale experiment docs | `archive` | No longer relevant | Archive |

### Workers / Infra

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| Railway worker | `keep_in_lab` | Production infra — egos-lab specific | Stay |
| Redis queue config | `keep_in_lab` | Infrastructure config — egos-lab specific | Stay |
| Vercel configs | `keep_in_lab` | Deploy-specific | Stay |

### Scripts

| Surface | Classification | Rationale | Destination |
|---------|---------------|-----------|-------------|
| `governance-sync.sh` (lab copy) | `migrate_to_egos` | Kernel is SSOT for governance scripts | Remove, use kernel |
| Lab-specific build scripts | `keep_in_lab` | App build scripts, stay | Stay |
| `gem-hunter` scripts | `keep_in_lab` | Lab-specific | Stay |

---

## Priority Migration Actions

### P0 — Immediate (unblocks kernel consistency)

1. **Remove duplicate `@egos/shared` code from egos-lab**
   - Lab should declare `@egos/shared` as a dependency, not re-implement
   - Action: Update `package.json` in lab to import from kernel published package

2. **Merge lab SYSTEM_MAP into kernel SYSTEM_MAP**
   - Lab's system map is a superset of kernel — extract lab-specific parts
   - Action: Kernel owns meta sections; lab keeps app-specific sections local

3. **Remove stale governance-sync.sh from lab**
   - Kernel is SSOT — lab scripts should call kernel's version via symlink or npx

### P1 — Important (reduces entropy)

4. **Archive old experiment docs in lab**
   - Docs older than 60 days with no task reference → move to `docs/archive/`

5. **Declare lab → kernel dependency contract**
   - Lab's `package.json` should have `"@egos/shared": "workspace:../egos/packages/shared"`
   - Or publish kernel to npm as `@egos/shared` and declare version

### P2 — Long-term

6. **Evaluate agent-028-template as standalone package**
   - Current: App-specific dashboard in egos-lab
   - Future: Could be a standalone `@egos/agent-dashboard` template
   - Decision: Keep in lab for now, evaluate at 100+ users

---

## Kernel ↔ Lab Boundary Contract

After this diagnostic, the contract is:

```
egos (kernel)
├── packages/shared/          ← SSOT for shared TypeScript modules
│   ├── atrian.ts             ← Kernel owns
│   ├── pii-scanner.ts        ← Kernel owns
│   ├── public-guard.ts       ← Kernel owns (EGOS-062)
│   ├── evidence-chain.ts     ← Kernel owns (EGOS-062)
│   └── ...                   ← All shared utilities
├── agents/                   ← SSOT for agent registry + runtime
│   ├── runtime/              ← Kernel owns runner, event-bus
│   └── agents/               ← Generic agents (dead_code, capability_drift)
├── .guarani/                 ← SSOT for governance DNA
└── scripts/guard.ts          ← SSOT for Guard Brasil CLI

egos-lab (lab)
├── apps/                     ← Production web apps (consumes kernel packages)
├── agents/agents/            ← Lab-specific agents (gem-hunter, report_generator)
└── packages/                 ← MUST NOT duplicate kernel; imports @egos/shared
```

---

## Status

- [x] All active surfaces classified
- [ ] P0 migration actions executed
- [ ] Lab `package.json` updated to import from kernel
- [ ] Stale docs archived in lab
- [ ] Boundary contract documented in lab's AGENTS.md

---

*Maintained by: EGOS Kernel*
*Related: EGOS-073, EGOS-074, EGOS-075*
