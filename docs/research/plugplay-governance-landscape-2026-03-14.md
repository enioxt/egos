# Plug-and-Play Governance Landscape — EGOS Focus Report

> Date: 2026-03-14
> Scope: MCP servers, A2A agent cards, adapter layers, registries/tool routers, personas, real validation
> Primary evidence: `gem-hunter` focused run + GitHub/Exa research

## Verified

### What was researched

A focused `gem-hunter` track was added in `egos-lab` for:

- `mcp-governance-servers`
- `a2a-agent-cards`
- `agent-adapters`
- `agent-marketplaces`
- `strategic-signals`

The run completed successfully with:

- `85` unique gems
- `25` governance/MCP results
- `12` A2A card/interoperability results
- `17` adapter/interoperability results
- `22` marketplace/registry/tool-router results
- `9` strategic signal results

Report artifact:

- `/home/enio/egos-lab/docs/gem-hunter/gems-2026-03-14.md`

### Best source clusters found

#### MCP / governance servers

- `@modelcontextprotocol/sdk`
- `@playwright/mcp`
- `ressl/mcp-firewall`
- `williamzujkowski/mcp-standards-server`
- `@rigour-labs/mcp`
- `modelcontextprotocol/registry`
- `agentic-community/mcp-gateway-registry`
- Kong article on dynamic MCP registry discovery

#### A2A / agent card / interoperability

- `a2aproject/A2A`
- `a2aprotocol.ai/docs/guide/a2a-typescript-guide.html`
- Google A2A codelabs
- compliance extension discussion on `a2aproject/A2A`

#### Adapter layers / protocol bridges

- `@zed-industries/claude-agent-acp`
- `@zed-industries/codex-acp`
- `@anthropic-ai/claude-agent-sdk`
- `agi-inc/agent-protocol`
- `llm-use/Polymcp`
- Rasa docs for integrating external agents via A2A

#### Marketplaces / registries / routers

- `openclaw`
- `clawhub`
- `agentregistry`
- `@agents-registry/mcp-server`
- `@composio/core`
- `@composio/mcp`
- Composio Tool Router docs
- `VoltAgent/awesome-openclaw-skills`

### Strong signals about EGOS positioning

Across sources, the strongest recurring concepts were:

- `policy-as-code`
- `gateway`
- `registry`
- `agent2agent`
- `compliance`
- `interoperability`
- `tool router`
- `audit`

This matches the proposed EGOS moat much more than generic standalone agents.

---

## Inferred

### What the market is telling us

The market is splitting into layers:

1. `Brains / runtimes`
2. `Tool access / MCP`
3. `Agent-to-agent coordination / A2A`
4. `Discovery / registry / marketplace`
5. `Governance / safety / compliance`

Most projects are strong in layers `1–4`.
Very few are strong in layer `5` in a portable, repo-propagatable way.

### Where EGOS can win

EGOS should not try to win on:

- general-purpose coding agents
- generic orchestration frameworks
- generic web automation
- generic social agents

EGOS can realistically win on:

- governed MCP servers for sensitive workflows
- Brazilian compliance-aware tool surfaces
- cross-repo governance propagation
- an adapter layer that makes external agents comply with EGOS rules
- auditability and evidence capture before/after tool execution

### The most important architectural insight

EGOS should become a **governance layer for the agent economy**, not another agent framework.

That means:

- expose our unique capabilities as MCP tools
- advertise them via an A2A-compatible identity/card
- ingest external agents through adapters
- rely on OpenClaw / agentregistry / Composio for distribution and discovery

---

## Proposed

## Product decomposition

### 1) `atrian-mcp`

Purpose:

- validate generated text for ethical/compliance issues before release

Core tools:

- `validate_response`
- `validate_batch`
- `filter_chunk`
- `explain_violations`
- `score_response`

Why this matters:

- no strong Brazil-aware ethical validator surfaced in research
- directly usable by IDE agents, chatbots, review bots, comms pipelines

### 2) `pii-scanner-mcp`

Purpose:

- detect and sanitize Brazilian sensitive data before storage, display, export, or LLM handoff

Core tools:

- `scan_text`
- `sanitize_text`
- `scan_file`
- `summarize_findings`
- `scan_batch`

Why this matters:

- LGPD + CPF/RG/MASP/REDS specificity is a real differentiator
- broadly useful across public sector, legal, compliance, investigations

### 3) `governance-sync-mcp`

Purpose:

- expose EGOS governance status, drift, sync plans, and policy gates as tools

Core tools:

- `check_governance_drift`
- `preview_sync`
- `run_sync`
- `check_frozen_zones`
- `verify_repo_governance`

Why this matters:

- this is EGOS’s clearest portable moat
- turns governance from docs into operational tooling

### 4) `egos-governance-agent-card`

Purpose:

- publish an A2A-compatible identity that declares what EGOS governs and how external agents can interact

Card should describe:

- capabilities
- allowed tasks
- policy constraints
- evidence expectations
- input/output contracts
- safety gates
- supported transports
- human approval requirements

### 5) `agent-adapter-kit`

Purpose:

- wrap external agents and normalize them under EGOS policy

Adapters to prioritize:

- OpenClaw skill / gateway adapter
- Codex ACP/CLI adapter
- Claude Agent SDK adapter
- Composio tool-router adapter

Adapter responsibilities:

- normalize task envelopes
- inject EGOS policy preflight
- capture evidence
- enforce dry-run-first when available
- run post-execution validation
- emit audit trail

---

## Personas

### Persona A — Compliance lead in a Brazilian regulated org

- **Who**: compliance manager, DPO, legal ops, internal audit
- **When**: before publishing answers, reports, messages, internal copilots
- **Frequency**: daily, often embedded in pipelines
- **Why**: avoid LGPD leakage, fabricated claims, false commitments, audit failure
- **Current substitute**: ad-hoc prompt rules, manual review, DLP tools, fragmented policy docs
- **Why switch**: EGOS gives policy-aware AI tool enforcement plus evidence trail

### Persona B — Engineering manager running multiple AI agents/tools

- **Who**: lead engineer, platform team, AI infra owner
- **When**: before exposing tools to IDE agents, coding agents, internal copilots
- **Frequency**: weekly during rollout, then per change
- **Why**: prevent uncontrolled tool sprawl, unsafe MCP adoption, drift across repos
- **Current substitute**: shell scripts, wiki rules, CI checks, manual reviews
- **Why switch**: EGOS gives repo-propagatable governance + policy checks as tools

### Persona C — Public-sector innovation squad / civic-tech team

- **Who**: innovation lab, investigation tooling squad, govtech consultancy
- **When**: before analyzing citizen data, internal cases, procurement docs, police/legal material
- **Frequency**: daily to weekly
- **Why**: combine agent productivity with privacy protection and auditable operation
- **Current substitute**: spreadsheets, manual anonymization, generic DLP, internal SOP PDFs
- **Why switch**: Brazil-native sanitization + governed automation + reproducible evidence

### Persona D — Agent marketplace operator / integration engineer

- **Who**: devrel, ecosystem engineer, AI platform architect
- **When**: when deciding which registry/router to integrate and how to govern external skills
- **Frequency**: during platform setup and new integration onboarding
- **Why**: external ecosystems move faster than internal policy teams
- **Current substitute**: allowlists, API gateway rules, manual vetting
- **Why switch**: EGOS can become the policy/control layer on top of existing ecosystems

---

## Competitive substitution

### What users already use instead

- `OpenClaw` for personal/local agent execution
- `Composio` for integration/tool routing
- `CrewAI`, `LangGraph`, `AutoGen`, `Mastra`, `VoltAgent` for orchestration
- generic DLP/compliance tools for privacy
- CI/policy engines for infra governance

### Direct competitors to the EGOS focus

Not many direct full competitors were surfaced.
Closest adjacent competitors:

- `mcp-firewall`
- `mcp-governance-sdk`
- `mcp-standards-server`
- `agentic-community/mcp-gateway-registry`
- compliance/policy-as-code platforms like Pulumi CrossGuard variants

### Why EGOS can still matter

Those tools cover fragments:

- firewall
- standards lookup
- registry
- generic policy

EGOS can combine:

- Brazil-native compliance
- repo governance propagation
- pre/post-execution evidence
- adapters for external agents
- policy-as-code for agent use, not just infra use

---

## Real validation battery

### Core validation principle

No claim counts as validated unless it survives:

- real inputs
- real execution path
- adversarial cases
- human review of outputs

### Test battery for `atrian-mcp`

#### Real cases

- public-sector chatbot answer draft
- procurement response draft
- legal/compliance memo draft
- citizen-service reply draft

#### Adversarial cases

- absolute claims (`100%`, `sempre`, `nunca`)
- fabricated citations (`segundo dados da...`)
- false promises (`vamos resolver`, `providências serão tomadas`)
- blocked entities / sensitive references
- invented acronyms

#### Human validation task

- ask a compliance reviewer to label each output as `pass / fail / borderline`
- compare human labels vs ATRiAN output

### Test battery for `pii-scanner-mcp`

#### Real cases

- OCR text from public PDFs
- complaint forms
- chat transcripts
- spreadsheets exported to CSV
- police/legal/public administration snippets

#### Target PII

- CPF
- RG
- MASP
- REDS
- phone
- email
- number plate
- date of birth
- named officials where policy requires masking

#### Human validation task

- reviewer checks false positives / false negatives
- sample at least `100` mixed documents

### Test battery for `governance-sync-mcp`

#### Real cases

- repo with drift between kernel and local copy
- repo with frozen-zone touch attempt
- repo missing required workflow or SSOT file
- repo with intentionally outdated rule file

#### Human validation task

- engineer reviews whether tool output is actionable and correct
- verify no false clean results on deliberately broken repo states

### Test battery for `agent-adapter-kit`

#### Real cases

- wrap one OpenClaw skill
- wrap one Codex/ACP agent
- wrap one internal runner-based agent
- wrap one Composio tool-router flow

#### Success criteria

- dry-run available or simulated
- preflight policy check runs
- evidence log emitted
- post-exec validation runs
- failure modes are visible and auditable

---

## Execution roadmap

### Phase 0 — Research hardening

- finalize shortlist of reference implementations
- save exemplars for MCP server shape, A2A card shape, registry/router integration
- build comparison matrix

### Phase 1 — Publish real MCP servers

Build first:

- `atrian-mcp`
- `pii-scanner-mcp`
- `governance-sync-mcp`

Success criteria:

- stdio mode works
- test suite exists
- fixtures with real Brazilian data exist
- docs show Claude/Cursor/Windsurf/OpenClaw usage

### Phase 2 — A2A identity

- create EGOS governance agent card
- publish capability manifest
- define supported tasks and policy boundaries
- add compliance metadata extension draft

### Phase 3 — Adapter layer

- create normalized task envelope
- implement `OpenClawAdapter`
- implement `CodexAdapter`
- implement `ClaudeAgentAdapter`
- implement `ComposioToolRouterAdapter`

### Phase 4 — External distribution

- publish to npm
- register in MCP registries where appropriate
- document OpenClaw / agentregistry / Composio integration
- produce examples and demo recordings

### Phase 5 — Field validation

- run pilots with real personas
- capture evidence logs
- quantify false positives / false negatives
- refine policy packs

---

## Immediate next tasks for the user to validate

### Task 1 — Real PII corpus

You should gather `20–50` real-world style samples:

- complaint snippets
- procurement documents
- OCR text from scans
- internal emails with phone/email/CPF patterns
- public case text with names and identifiers

Goal:

- help validate `pii-scanner-mcp`

### Task 2 — Real compliance drafts

You should gather `20–30` response drafts that a public/legal/compliance team would actually send.
Include:

- safe drafts
- risky drafts
- manipulative drafts
- overconfident drafts

Goal:

- benchmark `atrian-mcp` vs human judgment

### Task 3 — Repo drift scenarios

Create `5–10` deliberately broken repo states:

- stale `.windsurfrules`
- missing synced workflow
- frozen-zone edits
- missing SSOT file
- fake clean state

Goal:

- validate `governance-sync-mcp`

### Task 4 — Target persona interviews

Interview or simulate at least one case for each:

- compliance lead
- engineering/platform owner
- civic-tech/public-sector operator

Questions to answer:

- what task do they do weekly?
- what tool do they use today?
- what is slow or risky now?
- what evidence would make them trust EGOS?
- what would make them reject it?

---

## Instigation prompts for real usage discovery

Use these with yourself or with target users:

- `Em que momento você hoje revisa manualmente um texto antes de enviar por medo de risco jurídico ou reputacional?`
- `Que tipo de dado sensível mais vaza no seu fluxo atual: CPF, telefone, email, nome, processo, placa?`
- `Qual ferramenta você deixaria de usar se EGOS entregasse validação + evidência + integração pronta?`
- `Você aceitaria trocar parte do seu processo manual por um gateway governado se ele mostrasse claramente o que bloqueou e por quê?`
- `Quanto custaria um falso negativo real para você? Dinheiro, reputação, prazo, auditoria?`
- `Você prefere prevenção antes da execução, revisão depois, ou ambos?`

---

## Recommendation

The best near-term scope is exactly this:

1. publish `atrian`, `pii-scanner`, `governance-sync` as MCP servers
2. create an A2A-compatible EGOS governance card
3. build a thin adapter layer for external agents
4. integrate with OpenClaw / agentregistry / Composio instead of trying to outbuild them

Do not expand beyond this until:

- MCP servers run locally and in hosted mode
- real datasets exist
- false positive / false negative rates are measured
- at least one external integration works end-to-end
- at least one human persona validates usefulness in a real workflow
