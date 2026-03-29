# Dissemination Protocol

> **SSOT Owner:** `egos/docs/governance/DISSEMINATION_PROTOCOL.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-097 | **Workflows:** `.agents/workflows/disseminate.md`, `.windsurf/workflows/disseminate.md`

---

## Purpose

Defines the canonical contract for propagating new strategic rules, governance changes, and knowledge to all mapped repos. Prevents drift between the kernel and leaf repos after every significant session.

---

## When to Disseminate

Trigger dissemination after any session that produces:

| Trigger | Examples |
|---------|---------|
| New governance contract | New file in `docs/governance/` |
| SSOT change | `CAPABILITY_REGISTRY.md`, `SSOT_REGISTRY.md`, `SYSTEM_MAP.md` updated |
| New package capability | New export in `packages/shared/src/` |
| Security fix | CVE remediation, dependency override, hardening rule |
| Strategic decision | Ecosystem classification change, product verdict |
| Agent registry change | New agent, contract field update |

Do NOT disseminate for: work-in-progress branches, draft docs not merged to main, or changes that haven't passed QA loop.

---

## Protocol Steps

### Step 1 — Identify scope

```bash
git diff main..HEAD --name-only | sort
```

Classify each changed file:
- `docs/governance/` → governance rule → propagate
- `packages/shared/src/` → capability → update CAPABILITY_REGISTRY
- `docs/strategy/` → strategic → update FLAGSHIP_BRIEF if applicable
- `agents/registry/agents.json` → agent change → update CAPABILITY_REGISTRY

### Step 2 — Update CAPABILITY_REGISTRY

If a new capability was created:
```bash
# Add row to docs/CAPABILITY_REGISTRY.md
# Fields: Capability | SSOT | Quality | Adopted By | Should Adopt | Tags
```

### Step 3 — Run governance sync

```bash
bun run governance:sync:exec
# Propagates .guarani/, workflows, docs to ~/.egos/
# Run: bun run governance:check to verify
```

### Step 4 — Update leaf repo TASKS.md (if applicable)

If the change requires action in a leaf repo:
1. Open that repo's TASKS.md
2. Add a new task referencing the kernel change
3. Mark as P1 if it's a breaking change, P2 otherwise

### Step 5 — Record in handoff

Create or update `docs/_current_handoffs/<date>.md`:
```markdown
## Session: <date>
### What changed
- <list of significant changes>
### What needs doing next
- <next actions>
### Leaf repos to update
- <repo>: <what to add>
```

### Step 6 — Commit dissemination changes

```bash
git add docs/ && git commit -m "chore(disseminate): <session-summary>"
```

---

## Propagation Map

| Kernel surface | Propagates to | Mechanism |
|---------------|---------------|-----------|
| `.guarani/` | `~/.egos/guarani/` | `governance-sync.sh` |
| `.windsurf/workflows/` | `~/.egos/workflows/` | `governance-sync.sh` |
| `docs/CAPABILITY_REGISTRY.md` | `~/.egos/docs/` | `governance-sync.sh` |
| `docs/SSOT_REGISTRY.md` | `~/.egos/docs/` | `governance-sync.sh` |
| `docs/modules/CHATBOT_SSOT.md` | `~/.egos/docs/modules/` | `governance-sync.sh` |
| `packages/shared/` | leaf repos via npm or workspace | npm publish / workspace link |
| `docs/governance/` contracts | Leaf repos via TASKS.md entries | Manual (add task per repo) |

---

## Drift Prevention

A dissemination is **incomplete** if:
- `bun run governance:check` reports drift
- CAPABILITY_REGISTRY has no entry for a new capability added this session
- TASKS.md has no completion entry for the work done
- No handoff doc exists for the session

---

*Maintained by: EGOS Kernel*
*Related: EGOS-097, scripts/governance-sync.sh, .agents/workflows/disseminate.md*
