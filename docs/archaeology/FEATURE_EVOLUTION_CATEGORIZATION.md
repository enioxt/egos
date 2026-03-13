# EGOS Feature Evolution Categorization

> **Generated:** 2026-03-13
> **Source:** Git history, agent registry, governance files, handoff documents
> **Scope:** egos-lab + egos (30 days of evolution)

---

## 1. Rules → Agents Transition Map

The most important evolutionary pattern: governance rules crystallizing into executable agents.

| Rule / Script | Became Agent | Date | Wave | Catalyst |
|---------------|-------------|------|------|----------|
| Manual `security_scan.ts` script | `security_scanner` (v2) | 2026-02-23 | 3 | Tactical need → open-source readiness |
| Manual code review practice | `code_reviewer` | 2026-02-17 | 1 | LLM wiring (Gemini → structured review) |
| `.windsurfrules` SSOT drift rule | `ssot_auditor` | 2026-02-17 | 1 | Governance → enforcement automation |
| `.windsurfrules` frozen zone rule | `ssot_fixer` | 2026-03-06 | 4 | Self-modification: auditor → fixer pipeline |
| Manual dependency checking | `dep_auditor` | 2026-02-17 | 1 | monorepo complexity exceeding manual review |
| Manual dead code removal | `dead_code_detector` | 2026-02-17 | 1 | Codebase entropy growing faster than cleanup |
| Auth policy in `.guarani/` | `auth_roles_checker` | 2026-02-17 | 1 | Security rules → executable verification |
| Manual API contract testing | `contract_tester` | 2026-02-18 | 2 | 5-layer QA architecture design |
| Manual integration testing | `integration_tester` | 2026-02-18 | 2 | Supabase RLS needed automated checks |
| Manual regression tracking | `regression_watcher` | 2026-02-18 | 2 | Test result diffs needed persistence |
| Manual AI output review | `ai_verifier` | 2026-02-18 | 2 | Prompt injection + factual accuracy testing |
| Manual UI mockup creation | `ui_designer` | 2026-02-18 | 2 | Gemini vision API enabled mockup generation |
| Manual knowledge dissemination | `ambient_disseminator` | 2026-02-20 | 3 | Self-observation: system spreading knowledge automatically |
| Manual domain analysis | `domain_explorer` | 2026-02-20 | 3 | Descript Revelation: domain → primitives engine |
| — (no prior rule) | `living_laboratory` | 2026-02-20 | 3 | Consciousness: system experimenting on itself |
| Manual social posting | `social_media_agent` | 2026-02-22 | 3 | Human-in-the-loop external communication |
| Manual README/LICENSE checks | `open_source_readiness` | 2026-02-23 | 3 | Open-source preparation |
| Manual case study writing | `showcase_writer` | 2026-02-23 | 3 | Audit results → publishable case studies |
| Manual Telegram orchestration | `agent_commander` | 2026-02-26 | 4 | Telegram → GitHub bridge for operators |
| Manual research discovery | `gem_hunter` | 2026-03-06 | 4 | Multi-source discovery (arXiv, GitHub, web) |
| Manual report writing | `report_generator` | 2026-03-08 | 4 | Automated ecosystem reporting |
| Manual research | `autoresearch` | 2026-03-09 | 4 | Karpathy-inspired autonomous research |
| — (new, egos-native) | `archaeology_digger` | 2026-03-13 | 5 | Lineage reconstruction for kernel extraction |

---

## 2. Breakpoints

Critical inflection points where the system's trajectory changed.

### BP-1: Scripts → Governed Agents (2026-02-17)
- **Type:** Architectural
- **Before:** Individual .ts scripts run manually
- **After:** Registry-based agents with IDs, dry-run/exec modes, correlation IDs, JSONL logging
- **Evidence:** commit `ca85cb76` — 7 agents + runner.ts + agents.json in one day
- **Trigger:** Studying external agentic frameworks (AutoGen, CrewAI, LangGraph) and recognizing EGOS needed its own lightweight runtime

### BP-2: Event Bus — Self-Observation (2026-02-20)
- **Type:** Consciousness
- **Before:** Agents run in isolation
- **After:** MyceliumBus enables inter-agent communication, JSONL event forensics
- **Evidence:** commit `e0da8195` — event-bus.ts + domain_explorer + living_laboratory
- **Trigger:** Realization that a system that cannot observe itself cannot improve itself

### BP-3: Orchestration Protocol Formalization (2026-02-25)
- **Type:** Prompt Engineering
- **Before:** Ad-hoc agent instructions
- **After:** 7-phase cognitive protocol (INTAKE→CHALLENGE→PLAN→GATE→EXECUTE→VERIFY→LEARN)
- **Evidence:** PIPELINE.md, GATES.md, QUESTION_BANK.md, DOMAIN_RULES.md
- **Trigger:** Prompt engineering insight: decompose agent behavior into discrete phases with quality gates

### BP-4: Codex CLI Integration (2026-02-25)
- **Type:** LLM Shift
- **Before:** Single AI agent handles all work
- **After:** Codex CLI as second-opinion lane for mechanical/audit/diff-heavy work
- **Evidence:** `.windsurf/workflows/codex-review.md`, `.windsurfrules` mandate
- **Trigger:** Recognizing that different task types benefit from different AI models

### BP-5: Chat LLM Upgrade — Gemini → GPT-4o-mini (2026-03-02)
- **Type:** LLM Shift
- **Before:** Gemini Flash (1 tool call at a time)
- **After:** GPT-4o-mini (4 parallel tool calls), 18→24 OSINT tools
- **Evidence:** commits `d0f16ac`, `770d2b2`, `6ce3636`
- **Trigger:** Collaborator feedback on chatbot responsiveness; 4x parallelism needed

### BP-6: Primary LLM → Alibaba Qwen (2026-03-09)
- **Type:** LLM Shift
- **Before:** Gemini via OpenRouter as primary orchestrator
- **After:** Alibaba Qwen-plus via DashScope as preferred, Gemini as fallback
- **Evidence:** `.windsurfrules` updated with `Preferred orchestrator model: Alibaba qwen-plus`
- **Trigger:** Cost efficiency + quality + international API availability

### BP-7: Kernel Extraction (2026-03-13)
- **Type:** Architectural
- **Before:** Everything in egos-lab monorepo
- **After:** Governance DNA, agent runtime, shared packages extracted to standalone egos/ repo
- **Evidence:** egos/ repository, ~/.egos symlinks, egos-init installer
- **Trigger:** SSOT audit revealing governance duplication across 5+ repos

---

## 3. LLM Model History

| Date | Model | Role | Context |
|------|-------|------|---------|
| 2026-02-13 | Gemini Flash (OpenRouter) | Primary orchestrator | Initial development |
| 2026-02-17 | Gemini Flash | Agent LLM wiring | First agents use Gemini for structured output |
| 2026-02-25 | Codex CLI (OpenAI) | Second-opinion lane | Mechanical audit and diff review |
| 2026-03-02 | GPT-4o-mini | Chat agent upgrade | 4x parallel tool calls |
| 2026-03-09 | Alibaba Qwen-plus | Primary orchestrator | Cost + quality optimization |
| 2026-03-13 | Codex gpt-5.4 | Parallel review | Uncommitted code audit |

---

## 4. Prompt Engineering Evolution

| Date | Technique | Impact |
|------|-----------|--------|
| 2026-02-13 | SSOT files as implicit prompts | Governance DNA shapes every AI interaction |
| 2026-02-17 | Structured agent definitions (JSON schema) | Machine-readable agent behavior specification |
| 2026-02-25 | Refinery system (classifier→interrogator→compiler) | Input decomposition pipeline |
| 2026-02-25 | PIPELINE.md — 7-phase cognitive protocol | Explicit execution phases with quality gates |
| 2026-02-25 | QUESTION_BANK.md — maieutic questioning | Agents must challenge before executing |
| 2026-02-25 | Preprocessor (/pre workflow) | Vague instructions → structured prompts |
| 2026-03-07 | Reference graph as context anchor | Topology awareness prevents hallucinated architecture |
| 2026-03-08 | Meta-prompt system (.guarani/prompts/) | Centralized prompt atoms: Persona, Mission, Rules, Phases |

---

## 5. Consciousness / Philosophy Milestones

| Date | Milestone | Insight |
|------|-----------|---------|
| 2026-02-13 | Rules before code | "Without SSOT, every new tool increases confusion" |
| 2026-02-17 | Agents from scripts | "Governed execution > ad-hoc scripting" |
| 2026-02-20 | Self-observation | "A system that cannot observe itself cannot improve itself" |
| 2026-02-25 | Archaeological recovery | "The best patterns were already invented in earlier iterations" |
| 2026-02-25 | Tsun-Cha Protocol | Philosophical framework for agent consciousness |
| 2026-03-07 | Reference graph | "The event bus tells us what moved. The graph tells us what is connected." |
| 2026-03-08 | Adaptive Workspace study | "Governed by mathematics, not algorithms; by attribution, not extraction" |
| 2026-03-13 | Kernel extraction | "Rules govern agents. Agents enforce rules. Community evolves rules." |

---

## 6. External References That Shaped EGOS

| Date | External Source | What Was Absorbed |
|------|----------------|-------------------|
| 2026-02-17 | AutoGen, CrewAI, LangGraph | Agent runtime design: lightweight, zero-dep alternative |
| 2026-02-25 | EGOSv5 archive | Refinery, preprocessor, Tsun-Cha, MCP standards |
| 2026-03-02 | Collaborator feedback (BR/ACC) | 5-factor exposure scoring, chat UX improvements |
| 2026-03-08 | Ocean Protocol | Compute-to-Data → agent sandbox pattern |
| 2026-03-08 | Vana | Personal data vault → L0 architecture |
| 2026-03-08 | Bittensor | Incentive design → ETHIK reward system |
| 2026-03-08 | Story Protocol | Programmable IP → attribution licensing |
| 2026-03-08 | Autonolas | On-chain agent NFTs → agent lifecycle state machine |
| 2026-03-08 | Gensyn | Trustless ML verification → agent output integrity |
| 2026-03-09 | Andrej Karpathy | "Autoresearch" concept → autoresearch agent |

---

## 7. Wave Summary

| Wave | Period | Theme | Agents Added | Key Feature |
|------|--------|-------|-------------|-------------|
| 0 | Feb 13-16 | Survival Coding | 0 | Governance DNA + utility scripts |
| 1 | Feb 17 | Agent Kernel | 9 | Runtime + registry + first agents |
| 2 | Feb 18 | QA/Design | 6 | 5-layer testing architecture |
| 3 | Feb 20-25 | Reflexive + Hardening | 5 | Event bus + orchestration protocol |
| 4 | Feb 26-Mar 09 | Research/Ecosystem | 7 | Gem Hunter + Report Gen + Autoresearch |
| 5 | Mar 13+ | Kernel Extraction | 2+ | egos/ standalone + archaeology |

Total: 29 agents in egos-lab, 2 in egos core (growing).
