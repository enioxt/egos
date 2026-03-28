# SSOT `/start` System Architecture — v5.5

## Overview

The `/start` workflow is the **unified kernel activation system** for EGOS. It provides:
- Ordered initialization (SSOT loading → governance check → tooling verification)
- Capability registry inspection
- IDE integration metadata
- Agent signature contract activation
- Unified orchestration across all leaf repositories

---

## Source of Truth (SSOT)

### Canonical Location
**`~/.egos/workflows/start.md`** (74 lines, v5.5)

- Owned and maintained in the shared config directory
- Contains complete 10-section initialization workflow
- Version footer: `*v5.5 — Added Capability Registry + SecOps CISA KEV Dependency scanning.*`

### Propagation via Symlinks

| Repository | Location | Status |
|------------|----------|--------|
| **egos-lab** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **egos-lab** | `.agents/workflows/start.md` | ✅ Symlink |
| **egos** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **852** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **852** | `.agents/workflows/start.md` | ✅ Symlink |
| **br-acc** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **carteira-libre** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **forja** | `.windsurf/workflows/start.md` | ✅ Symlink |
| **egos-self** | `.windsurf/workflows/start.md` | ✅ Symlink |

### Customizations (Intentional Deviations)

| Repository | Type | Purpose | Notes |
|-----------|------|---------|-------|
| **INPI** | `.windsurf/workflows/start.md` | 🎯 Custom (10 lines, PT) | Minimal session initialization |
| **policia** | `.windsurf/workflows/start.md` | 🎯 Custom (101 lines) | Sensitive data handling + egos governance mapping |

These are **intentional customizations** — do NOT replace with symlinks.

---

## Workflow Structure (10 Sections)

### 1. SSOT Loading Rules
- **Purpose**: Define precedence order for workflow discovery
- **Rules**:
  1. Check local override: `.windsurf/workflows/start-local.md`
  2. Load `.windsurf/workflows/start.md`
  3. Fallback: `.egos/workflows/start.md`

### 2. Unified Orchestration
- **Purpose**: Activate the orchestration system
- **Actions**:
  - Load kernel agents registry
  - Initialize event bus
  - Activate mycelium connectivity

### 3. Boot Sequence
- **Purpose**: Load core SSOT files
- **Files Checked**:
  - `AGENTS.md` — Agent registry and roles
  - `TASKS.md` — Priority task list (P0/P1/P2)
  - `.guarani/PREFERENCES.md` — Coding standards
  - `.windsurfrules` — Project-specific rules
  - `docs/SYSTEM_MAP.md` — Architecture overview

### 4. IDE Integration
- **Purpose**: Configure editor metadata
- **Loads**:
  - Meta-prompts registry (`triggers.json`)
  - Classifier configuration
  - Windsurf-specific settings

### 5. Capability Registry
- **Purpose**: Verify `docs/CAPABILITY_REGISTRY.md` exists
- **Action**: Load shared capabilities checklist
- **Impact**: Ensures leaf repos align with kernel standards

### 6. Governance Sync Status
- **Purpose**: Check drift between narrative (docs) and live system
- **Verification**:
  - Agent count matches registry
  - Task priorities are current
  - Rule files are not stale

### 7. Orchestration Check
- **Purpose**: Verify agent runtime is healthy
- **Checks**:
  - Event bus connectivity
  - Runner availability
  - Pipeline gates functional

### 8. Tooling Session Check
- **Purpose**: Verify external integrations
- **Verifies**:
  - Alibaba API key (LLM provider)
  - OpenRouter fallback
  - GitHub token
  - Supabase credentials
  - Telegram bot (if configured)
  - Codex CLI availability

### 9. Output Briefing
- **Purpose**: Present initialization summary to user
- **Output Format**:
  - ✅ Passed checks summary
  - ⚠️ Warning alerts
  - ❌ Blockers (if any)
  - 💡 Next actions

### 10. Agent Signature Activation
- **Purpose**: Load and enforce message signature contract
- **Activation Steps**:
  1. Load `.guarani/standards/AGENT_MESSAGE_SIGNATURE_CONTRACT.md`
  2. Enforce signature footer on all operational replies
  3. Run `bun run governance:sync:exec` if changes made
  4. Verify with `bun run governance:check`

---

## Loading Precedence

When `/start` is invoked:

```
1. Windsurf checks for .windsurf/workflows/start-local.md
   ↓ (if not found)
2. Load .windsurf/workflows/start.md
   ↓ (if not found, fallback)
3. Load ~/.egos/workflows/start.md
   ↓
4. Execute workflow (all 10 sections in order)
```

**Result**: Unified initialization across all 9 active repositories

---

## Customization Guidelines

### When to Customize
1. **Repository-specific requirements** (e.g., Polícia sensitive data rules)
2. **Language requirements** (e.g., INPI in Portuguese)
3. **Domain-specific governance** (e.g., compliance, security)

### How to Customize
1. Create **local override**: `.windsurf/workflows/start-local.md`
   - OR create **custom version**: `.windsurf/workflows/start-custom.md`
   - Do NOT edit the symlinked version

2. Document in repo's `CLAUDE.md`:
   ```markdown
   ## Custom /start Workflow
   This repo uses custom initialization at: `.windsurf/workflows/start-custom.md`
   Reason: [explain customization]
   Synced with kernel: [date]
   ```

3. Keep in sync with kernel updates (v5.5+) for critical sections

---

## Governance Propagation

### Via `/disseminate`
When kernel `/start` is updated:

```bash
cd /home/enio/egos
bun run governance:sync:exec
# Propagates updated symlinks to all leaf repos
```

### Verification
```bash
# Verify all symlinks point to canonical SSOT
find /home/enio -name "start.md" -path "*/.windsurf/workflows/*" -exec ls -l {} \;

# Check symlink targets
find /home/enio -type l -name "start.md" -exec readlink {} \;
```

---

## Current State (2026-03-28)

| Status | Count | Details |
|--------|-------|---------|
| ✅ Active Symlinks | 9 | All pointing to `~/.egos/workflows/start.md` |
| ✅ Custom Versions | 2 | INPI, policia (intentional) |
| ✅ Kernel Sync | YES | Last synced: 2026-03-28 |
| ✅ Version | 5.5 | Latest with Agent Signature + Capability Registry |

---

## Migration History

| Date | Action | Result |
|------|--------|--------|
| 2026-03-27 | Initial symlink creation | 6 repos linked |
| 2026-03-28 | Unified egos copy | Converted to symlink |
| 2026-03-28 | Added egos-lab/.agents symlink | All agent workflows unified |
| 2026-03-28 | Documentation created | SSOT architecture formalized |

---

## Troubleshooting

### Symlink Broken
```bash
# Check target
readlink ~/.egos/workflows/start.md
# Should exist and be readable

# Repair if needed
rm /repo/.windsurf/workflows/start.md
ln -s /home/enio/.egos/workflows/start.md /repo/.windsurf/workflows/start.md
```

### Workflow Not Loading
```bash
# Verify SSOT file exists
ls -la ~/.egos/workflows/start.md

# Check if local override exists (takes precedence)
ls -la .windsurf/workflows/start-local.md

# Test with explicit path
cat ~/.egos/workflows/start.md | head -20
```

### Version Mismatch
```bash
# Verify all symlinks point to v5.5
for f in $(find /home/enio -type l -name "start.md"); do
  version=$(grep "^\\*v" $(readlink $f) | tail -1)
  echo "$f: $version"
done
```

---

**Status**: ✅ COMPLETE — Unified SSOT system operational across 9 active repos + 2 custom implementations.
