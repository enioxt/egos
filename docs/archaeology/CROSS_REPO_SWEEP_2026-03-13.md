# Cross-Repo Archaeology Sweep

> **Generated:** 2026-03-13
> **Scope:** `egos`, `egos-lab`, `carteira-livre`, `br-acc`, `forja`, `policia`, `egos-self`

## Systemic Findings

1. **Governance Alignment (100% SSOT Match)**
   - EVERY checked repo has `.guarani/`, `.windsurfrules`, `AGENTS.md`, and `TASKS.md`.
   - The SSOT enforcement strategy (via `~/.egos/` symlinks) is completely effective across the ecosystem.
   - We have successfully broken the "silo" effect. Governance DNA is universal.

2. **Agent Distribution**
   - **`egos-lab`**: 29 agents (The experimental laboratory / orchestrator nexus)
   - **`egos`**: 2 agents (The core framework / runtime kernel)
   - **`carteira-livre`, `br-acc`, `forja`, `policia`, `egos-self`**: 0 registered agents
   - **Conclusion**: The split between *agent runtime* (egos) and *agent implementations* (egos-lab) is currently where all the action is. The leaf repos (carteira-livre, br-acc) are consuming the outputs of egos-lab but do not yet host their own registry-bound agents. They rely heavily on `scripts/` (carteira-livre has 31 scripts).

3. **Script vs Agent Evolution**
   - `carteira-livre` relies on 31 scripts.
   - `egos-lab` successfully transitioned from scripts to 29 registered agents.
   - **Next Evolutionary Step**: `carteira-livre` should migrate its internal maintenance scripts into leaf-level agents using the `egos` runtime framework.
