# 🛣️ EGOS - Project Roadmap

**Version:** 1.3
**Last Updated:** 2025-04-08
**🌐 Website:** [https://enioxt.github.io/egos](https://enioxt.github.io/egos)

**Primary References:**

* `docs/MQP.md` (Master Quantum Prompt v9.0 "Full Moon Blueprint")
* `research/EGOS_ GitHub Project Search_.txt` (Contextual Study)
* `.cursor/rules/sparc_orchestration.mdc` (SPARC Integration)

---

## Guiding Principles

* Adherence to MQP v9.0 "Full Moon Blueprint" (ETHIK, KOIOS, HARMONY, CRONOS)
* Modularity & Decoupling via Subsystems (MYCELIUM)
* Structured Problem Solving via SPARC Methodology
* Iterative Development (Phased Approach)
* Documentation First / Continuous Documentation
* Consistent Code Quality via Automated Checks (KOIOS/Ruff)
* Security by Design (ETHIK / KOIOS)

---

## Phases Overview

* **Phase 1: Foundation & Core AI Interaction (EGOS Alpha)** - *Mostly Complete*
* **Phase 2: EGOS Beta – Foundation, Standardization & Core Capabilities** - *In Progress*
  * **Phase 2a: Initial Framework & Standards** - *Mostly Complete*
  * **Phase 2b: SPARC Integration & Advanced Orchestration** - *In Progress*
* **Phase 3: EGOS Hive – Interconnection, MVP Launch & Expansion** - *Future*
* **Phase 4: Continuous Evolution & Optimization** - *Ongoing/Future*

---

## 📐 Structure & Best Practices

* **Clear Sections**: Group tasks by Phase or Category.
* **Priority Tags**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
* **Status Indicators**: `Planned`, `In Progress`, `Completed`, `Blocked`, `DONE`.
* **Responsibility**: Assign owner or team where applicable.
* **Linked Issues/PRs/Docs**: Reference relevant GitHub items or documentation.
* **Dates (Optional)**: Target quarters or specific deadlines.
* **References**: Use `(See analysis in research/)` to link tasks to the GitHub project study.

---

## 💰 Monetization & Product Strategy (STRAT Lead)

*   **[STRAT-GTM-DEFINE]** **Define Go-To-Market Strategy:** Define strategy including target audience, value proposition, potential open-core model, and initial pricing exploration for defined MVPs. Leverage `docs/STRATEGY.md`, `research/`, and market analysis results. (`HIGH`) `Status: Planned`
*   **[MVP-DEFINE-SPARC-SVC]** **Define MVP - SPARC Service:** Define MVP for a 'SPARC-based Project Analysis & Refactoring Service', outlining core features, target outcomes, required subsystems, and potential delivery model. (`HIGH`) `Status: Planned`, `linked_doc: docs/strategy/MVP_Definition.md`
*   **[MVP-DEFINE-QPG]** **Define MVP - Quantum Prompt Generator (QPG):** Define MVP for the QPG as a potential standalone tool or premium feature, including core functionality, target user, and integration points. (`HIGH`) `Status: Planned`, `linked_doc: docs/strategy/MVP_Definition.md`
*   **[MARKET-ANALYSIS-MVP1]** **Conduct Initial Market Analysis:** Conduct analysis for defined MVPs (SPARC Service, QPG), identifying competitors, pricing models, and target segments. (`MEDIUM`) `Status: Planned`, `depends_on: [MVP-DEFINE-SPARC-SVC], [MVP-DEFINE-QPG]`

---

## 🧭 Current Phase: Phase 2 - Foundation, Standardization & Initial Capabilities (Q2-Q3 2025)

### Core Standardization & Refactoring (KOIOS Lead)

feat/roadmap-updates
* [DONE] Standardize Project Structure & Basic READMEs (`CRITICAL`)
* [DONE] Implement Conventional Commit Standards (`HIGH`)
* [DONE] Define Core Python Coding Standards (PEP8, Typing) (`HIGH`)
* [DONE] Implement Logging Standards (`HIGH`)
* [DONE] Establish Basic Documentation Standards (Docstrings) (`HIGH`)
* [DONE] Set up Pre-Commit Hooks (ruff, black) (`HIGH`)
* [DONE] Define Metadata Schema for MDC Rules (`MEDIUM`)
* [DONE] **Activate Cursor Agent Mode:** Transitioned from Chat to Agent, enabling direct file/terminal interaction. (`HIGH` - See `docs/ai_integration/cursor_agent_mode.md`)
* [DONE] **Consolidate `.cursor/rules`:** Reviewed all `.cursor/rules/*.mdc` files, consolidating or linking them into `global_rules.mdc` as the central source of truth for project standards. (`HIGH`)
* [In Progress] Refactor Subsystems for Metadata Compliance (`MEDIUM`)
* [Planned] [KOIOS][DOC-RU-01] Document Rationale for File Handling Rules (`Existence Check`, `Comprehensive Search`) in KOIOS standards (`MEDIUM`)
* [Planned] [KOIOS][DOC-BP-FS-01] Add "Best Practices for File Search/Creation" section to relevant documentation (`LOW`)
* [Planned] [KOIOS/NEXUS][DOC-HTA-USAGE-01] Document `analyze_git_history.py` script usage and examples (`LOW`)
* [Planned] [KOIOS][DOC-README-HTA-01] Update main `README.md` to mention historical analysis capability and link report (`LOW`)
* [Planned] [KOIOS][DOC-CONTRIB-AI-01] Update `CONTRIBUTING.md` (or create if needed) with latest AI collaboration rules (`LOW`)
* [Planned] [KOIOS][KOIOS-DOC-AUDIT-01] Perform Periodic Review of `.mdc` rules and `docs/` for consistency and alignment (`MEDIUM` - Recurring)

### 📈 Analysis & Insights (NEXUS Lead)

* [DONE] [NEXUS/KOIOS][TASK-HTA-01] Implement Historical File Lifespan Analysis (Script, CSV, Report) (`HIGH`)
* [DONE] [SPARC/HARMONY/KOIOS][HTA-02] Automate Git History Analysis via CI/CD (GitHub Actions) (`MEDIUM`) (Ref: Evolutionary Preservation)
* [Planned] [CORUJA/KOIOS][HTA-DASH-01a] Select Visualization Tool for HTA Dashboard (`MEDIUM`)
* [Planned] [CORUJA/KOIOS][HTA-DASH-01b] Implement HTA Dashboard Integration (`MEDIUM`) `depends_on: [HTA-DASH-01a]`
* [Planned] [NEXUS/KOIOS][HTA-REFINE-01] Review and Refine HTA Script and Report (Performance, Clarity, Artistry) (`LOW`)

### 🛡️ Security & Compliance (ETHIK Lead)

* [Planned] [ETHIK/HARMONY][SEC-AUDIT-01] Perform Periodic Security & License Audit (incl. `pip-audit`, license checks, sensitive data review) (`HIGH` - Recurring)

### SPARC Methodology Integration (KOIOS/CORUJA Lead) - Phase 2b

* [DONE] Create SPARC Orchestration Rule (`.cursor/rules/sparc_orchestration.mdc`) (`HIGH`)
* [DONE] Implement Basic SPARC Task Registry in CORUJA (`HIGH`)
* [DONE] Define Mycelium Message Formats for SPARC Tasks (`HIGH`)
* [In Progress] Document SPARC-EGOS Subsystem Mapping (`MEDIUM`) - ID: `SPARC-MAPPING`
* [Planned] Implement Model Selection Based on Task Type (`MEDIUM`) - ID: `CORUJA-MODEL-SELECT`, `depends_on: [CORUJA-ARCH]`
* [Planned] Integrate SPARC with CrewManager (`MEDIUM`) - ID: `SPARC-CREW-INTEGRATE`, `depends_on: [CORUJA-ARCH]`
* [Planned] Create Boomerang Task Handlers (`HIGH`) - ID: `SPARC-BOOMERANG`, `depends_on: [CORUJA-ARCH]`
* [Planned] Define SPARC Task Schema Validation (`LOW`) - ID: `SPARC-SCHEMA-VALID`

### System Standardization (KOIOS Lead)

**Description**: Implement and enforce KOIOS standards across the codebase. Includes directory structure migration, naming conventions, metadata validation. **(Branding alignment complete).**
**Status**: In Progress
**Priority**: CRITICAL
**Owner**: KOIOS Team / All Contributors
**Related Docs**: `docs/STANDARDS_*.md`, `subsystems/KOIOS/README.md`
**ETA**: Ongoing Q2 2025

* **In Progress**
  * [In Progress] Refactor Subsystems for Metadata Compliance (`MEDIUM`)
* **Planned**
  * [Planned] [KOIOS][DOC-RU-01] Document Rationale for File Handling Rules (`Existence Check`, `Comprehensive Search`) in KOIOS standards (`MEDIUM`)
  * [Planned] [KOIOS][DOC-BP-FS-01] Add "Best Practices for File Search/Creation" section to relevant documentation (`LOW`)
  * [Planned] [KOIOS][KOIOS-LESSONS-01] Create/Maintain "Lessons Learned" log for AI Collaboration & Onboarding (`LOW`)
  * [Planned] [KOIOS/NEXUS][DOC-HTA-USAGE-01] Document `analyze_git_history.py` script usage and examples (`LOW`)
  * [Planned] [KOIOS][DOC-README-HTA-01] Update main `README.md` to mention historical analysis capability and link report (`LOW`)
  * [Planned] [KOIOS][DOC-CONTRIB-AI-01] Update `CONTRIBUTING.md` (or create if needed) with latest AI collaboration rules (`LOW`)
  * [Planned] [KOIOS][KOIOS-DOC-AUDIT-01] Perform Periodic Review of `.mdc` rules and `docs/` for consistency and alignment (`MEDIUM` - Recurring)
* **Completed**
  * ✅ [DONE] Standardize Project Structure & Basic READMEs (`CRITICAL`)
  * ✅ [DONE] Implement Conventional Commit Standards (`HIGH`)
  * ✅ [DONE] Define Core Python Coding Standards (PEP8, Typing) (`HIGH`)
  * ✅ [DONE] Implement Logging Standards (`HIGH`)
  * ✅ [DONE] Establish Basic Documentation Standards (Docstrings) (`HIGH`)
  * ✅ [DONE] Set up Pre-Commit Hooks (ruff, black) (`HIGH`)
  * ✅ [DONE] Define Metadata Schema for MDC Rules (`MEDIUM`)
  * ✅ [DONE] **Activate Cursor Agent Mode:** Transitioned from Chat to Agent, enabling direct file/terminal interaction. (`HIGH` - See `docs/ai_integration/cursor_agent_mode.md`)
  * ✅ [DONE] **Consolidate `.cursor/rules`:** Reviewed all `.cursor/rules/*.mdc` files, consolidating or linking them into `global_rules.mdc` as the central source of truth for project standards. (`HIGH`)
main

### Monitoring & Dashboard (ATLAS/KOIOS)

* **In Progress**
  * [In Progress] Integrate Dashboard via Iframe (Streamlit Cloud) (`LOW`) - ID: `DASHBOARD-IFRAME-INTEGRATE`
* **Planned**
  * [Planned] Integrate Real NATS Client (post-Mycelium stabilization) (`HIGH`) - ID: `DASHBOARD-NATS-CLIENT`, `depends_on: [MYCELIUM-RELIABLE]`
  * [Planned] Deploy Dashboard (e.g., Streamlit Cloud) (`MEDIUM`) - ID: `DASHBOARD-DEPLOY`, `depends_on: [DASHBOARD-NATS-CLIENT]`
  * [Planned] Add SPARC Task Visualization (`MEDIUM`) - ID: `DASHBOARD-SPARC-VIZ`, `depends_on: [DASHBOARD-NATS-CLIENT]`
  * [Planned] [ATLAS/CORUJA] Implement Dashboard Theme Alignment with Website (`LOW`) - ID: `DASHBOARD-THEME-ALIGN`
  * [Planned] [ATLAS/CORUJA/ETHIK] Plan Deep Dashboard-Website Integration (API/Bridge for Auth/Data) (`MEDIUM`) - ID: `DASHBOARD-DEEP-INTEGRATE`
  * [Planned] [KOIOS] Update README/Roadmap ref Dashboard Integration (`LOW`) - ID: `DOC-DASHBOARD-INTEGRATION`
  * [Planned] [KOIOS] Update CONTRIBUTING.md ref Website Roadmap Usage (`LOW`) - ID: `DOC-CONTRIB-WEBSITE-FLOW`
* **Completed**
  * ✅ [DONE] Basic Streamlit Dashboard Setup (`MEDIUM`)
  * ✅ [DONE] Implement Modular UI Components (`MEDIUM`)
  * ✅ [DONE] Add Dark/Light Theme Toggle (`LOW`)
  * ✅ [DONE] Integrate Mock NATS Client for Demo (`HIGH`)
  * ✅ [DONE] Implement `KoiosLogger` for Dashboard Interactions (`HIGH`)
  * ✅ [DONE] Improve Light Theme Contrast (`LOW`)
  * ✅ [DONE] Refine Website Task Modal UI/UX (`MEDIUM`) - ID: `WEBSITE-MODAL-UI-REFINE`

### Website & Frontend (CORUJA/KOIOS Lead)

* **Planned**
  * [Planned] [CORUJA/KOIOS] Implement Task Modal Close Functionality (ESC, Click Outside) (`HIGH`) - ID: `WEBSITE-MODAL-CLOSE`
  * [Planned] [KOIOS/HARMONY] Plan and Execute Website Deployment (Vercel/Netlify/VPS) (`MEDIUM`) - ID: `WEBSITE-DEPLOY`

### CORUJA Subsystem (Phase 2b)

**Description**: Advanced development of the AI Orchestration subsystem with SPARC methodology integration. Focus on specialized task handling, model selection, and Boomerang Tasks. **Must include SPARC task registry, standardized message formats, and cross-subsystem communication via Mycelium.** Support for MVP features using structured problem solving.
**Status**: In Progress
**Priority**: HIGH
**Owner**: CORUJA Team
**Related Docs**: `subsystems/CORUJA/README.md`, `.cursor/rules/sparc_orchestration.mdc`
**ETA**: Q2/Q3 2025

### Define Initial Target Offering / Use Case

**Description**: Define the scope, features, and target audience for the first Minimum Viable Product (MVP), likely the "Content Aggregator & Insight Engine". **Must strongly emphasize ETHIK-driven features as key differentiators.**
**Status**: Planned
**Priority**: HIGH
**Owner**: Strategy/Product Team
**Related Docs**: `docs/strategy/EGOS_Business_Plan_v1.0.md`, `docs/strategy/MVP_Definition.md` (To be created)
**ETA**: Mid-Q3 2025

### Mycelium Network (MYCELIUM Lead)

* **In Progress**
  * [In Progress] Finalize Core NATS Message Schemas (`CRITICAL`)
  * [In Progress] Define SPARC Task Message Formats (`HIGH`)
* **Planned**
  * [Planned] Implement Reliable Message Handling (ACKs, Retries) (`HIGH`) - ID: `MYCELIUM-RELIABLE`
  * [Planned] Develop Test Suite for Mycelium (`HIGH`) - ID: `MYCELIUM-TEST-SUITE`, `depends_on: [MYCELIUM-RELIABLE]`

### Ethical Framework (ETHIK Lead)

* **In Progress**
  * [In Progress] Implement Core Validation Rules (PII, Security Patterns) (`CRITICAL`)
* **Planned**
  * [Planned] Define ETHIK API/Message Interface (`HIGH`) - ID: `ETHIK-API`
  * [Planned] Integrate ETHIK Validation into Key Workflows (e.g., CORUJA output) (`HIGH`) - ID: `ETHIK-INTEGRATION`, `depends_on: [ETHIK-API, MYCELIUM-RELIABLE]`
  * [Planned] Refactor `validator.py` into smaller modules (Adhering to `file_modularity.mdc`) (`LOW`) - ID: `ETHIK-REFACTOR`
  * [Planned] Add SPARC Task Validation Rules (`LOW`) - ID: `ETHIK-SPARC-RULES`, `depends_on: [ETHIK-API]`
  * `[Planned] Refine ETHIK Authentication Design based on SaaS patterns (MEDIUM)` - ID: `ETHIK-AUTH-DESIGN` (See `research/SaaS_Framework_Analysis.md`)

### Core AI Orchestration (CORUJA Lead)

* **In Progress**
  * [In Progress] Design Core CORUJA Architecture (`CRITICAL`) - ID: `CORUJA-ARCH`
* **Planned**
  * [Planned] Implement Basic LLM Interaction Handler (`CRITICAL`) - ID: `CORUJA-LLM-HANDLER`, `depends_on: [CORUJA-ARCH]`
  * [Planned] Define Standard Prompt Templates (`HIGH`) - ID: `CORUJA-PROMPT-TEMPLATES`, `depends_on: [CORUJA-ARCH]`
  * [Planned] Integrate with Mycelium for Task Requests (`CRITICAL`) - ID: `CORUJA-MYCELIUM-INTEGRATION`, `depends_on: [CORUJA-ARCH, MYCELIUM-RELIABLE]`
  * [Planned] Implement Model Selection for SPARC Tasks (`MEDIUM`) - ID: `CORUJA-MODEL-SELECT`, `depends_on: [CORUJA-ARCH]` (Note: Duplicate ID used, consistent with SPARC section)

### Project Documentation & Open Source Readiness (KOIOS Lead)

**Goal:** Conduct a comprehensive review and update of all project documentation to ensure clarity, accuracy, and completeness, preparing EGOS for open-source release and external collaboration. **(Critical Prerequisite for effective LLM Integration, especially RAG).**
**Status:** Planned (Phase 1 Starting)
**Priority:** HIGH

* **Phase 1: Foundational Analysis & Audit (Immediate Priority - Q2 2025)**
  * **In Progress**
    * [In Progress] **Task 1.3: Documentation Audit:** Assess all existing documentation (`/docs`, `.cursor/rules/`, subsystem docs) for completeness, accuracy, structure, format, and searchability. Identify gaps and inconsistencies.
  * **Planned**
    * [Planned] **Task 1.1: Deep EGOS System Analysis:** Perform thorough review of EGOS architecture, core module code, data flows, existing APIs, and authentication mechanisms (Ref: LLM Integration Plan I.B).
    * [Planned] **Task 1.2: Stakeholder Input:** Gather insights from developers/architects on system nuances and potential LLM use cases.
    * [Planned] **Task 1.4: Initial EGOS Summary:** Create the concise, high-level EGOS summary document intended for initial LLM context priming (Ref: LLM Integration Plan I.C).
* **Phase 2: Content Standardization & Enrichment (Q2/Q3 2025)**
feat/roadmap-updates
  * [Planned] **Task 2.1: Define Standards:** Establish documentation templates, style guide, and definitive format (e.g., Markdown in repo, potentially feeding a tool like MkDocs).
  * [Planned] **Task 2.2: Prioritized Content Creation/Revision:** Focus on documenting critical subsystems/features relevant to initial LLM support. Develop clear natural language descriptions, practical examples, diagrams (update/create), and relevant code snippets (Ref: LLM Integration Plan IV.B).
  * [Planned] **Task 2.3: Structure & Searchability:** Organize documentation logically (e.g., by subsystem) and ensure the chosen format is machine-parsable and ideally searchable (prep for RAG).
  * [Planned] **Task 2.4: Refine Website Standards:** Review and potentially further refine the enhanced `website_standards.mdc` (v1.1.0) based on feedback from initial website implementation tasks (Phase W1/W2).
  * [Planned] **[KOIOS-DOC-QPG-01]** **Document Quantum Prompt Generator:** Create documentation covering the QPG component's architecture, frontend usage, backend API interaction (if applicable), configuration, and contribution guidelines. (`MEDIUM`, Phase 2) `Status: Planned` `Subsystems: [KOIOS, WEBSITE]` `Principles: Comprehensive Documentation` `depends_on: [WEBSITE-QPG-IMPL-01]`

  * **Planned**
    * [Planned] **Task 2.1: Define Standards:** Establish documentation templates, style guide, and definitive format (e.g., Markdown in repo, potentially feeding a tool like MkDocs).
    * [Planned] **Task 2.2: Prioritized Content Creation/Revision:** Focus on documenting critical subsystems/features relevant to initial LLM support. Develop clear natural language descriptions, practical examples, diagrams (update/create), and relevant code snippets (Ref: LLM Integration Plan IV.B).
    * [Planned] **Task 2.3: Structure & Searchability:** Organize documentation logically (e.g., by subsystem) and ensure the chosen format is machine-parsable and ideally searchable (prep for RAG).
    * [Planned] **Task 2.4: Refine Website Standards:** Review and potentially further refine the enhanced `website_standards.mdc` (v1.1.0) based on feedback from initial website implementation tasks (Phase W1/W2).
main
* **Phase 3: Alignment & Maintenance Process (Q3 2025)**
  * **Planned**
    * [Planned] **Task 3.1: Code/Doc Alignment:** Verify documentation accurately reflects current implementation logic, interfaces, and KOIOS standards. Update docstrings/comments (`python_documentation.mdc`).
    * [Planned] **Task 3.2: Establish Maintenance Workflow:** Integrate documentation updates into the standard development lifecycle. Assign ownership.
* **Phase 4: Open Source Preparation (Q3/Q4 2025)**
  * **Planned**
    * [Planned] **Task 4.1:** Create `CONTRIBUTING.md` guidelines.
    * [Planned] **Task 4.2:** Add appropriate `LICENSE` file.
    * [Planned] **Task 4.3:** Review repository structure and file organization for external clarity.

### Website Enhancement & LLM Integration (Phased Approach)

**Goal:** Enhance the EGOS project website (`docs/index.html` etc.) by integrating an LLM (initially `quasar-alpha` via OpenRouter, with planned fallbacks) for dynamic user assistance, grounded in project knowledge, while managing risks and costs.
**Status:** Planned (Phase 1 Starting after Doc Phase 1)
**Priority:** HIGH
**Overall Considerations:** Prioritize Server-Side Security, UI Simplicity, Active Cost Control. Acknowledge **significant risks** associated with `openrouter/quasar-alpha` (Alpha status, potential instability/discontinuation, explicit logging policy) requiring mandatory fallback planning.

* **Phase 1: Foundational MVP (Focus: Core Functionality, Security Basics - Q2/Q3 2025)**
  * **In Progress**
    * [In Progress] **Task W1.1: Basic Backend Service:** Implement secure backend endpoint (Python/Node.js aligned with EGOS stack) for chat interaction.
  * **Planned**
    * [Planned] **Task W1.2: Secure API Key Handling:** Implement API key storage using **Secrets Manager (preferred)** or Environment Variables. Ensure key is never exposed client-side (Ref: LLM Plan II.D, VI.A).
    * [Planned] **Task W1.3: Basic OpenRouter Integration:** Connect backend to `quasar-alpha`, using the initial EGOS Summary (from Doc Phase 1.4) as basic context in the system prompt (Ref: LLM Plan V.A, V.C Option A). Implement basic error handling for API calls.
    * [Planned] **Task W1.4: Simple Chat UI:** Develop and integrate the basic chat interface component into `docs/index.html` (Ref: LLM Plan III.B).
    * [Planned] **Task W1.5: Basic Rate Limiting:** Implement initial IP-based rate limiting on the backend endpoint (Ref: LLM Plan VI.C).
    * [Planned] **Task W1.6: Basic Analytics:** Configure GA4 with essential event tracking (`llm_message_sent`, `llm_response_received`) (Ref: LLM Plan VII.B).
* **Phase 2: Enhancement & Contextualization (Focus: Usefulness, Control, Fallback Prep - Q3/Q4 2025)**
  * **Planned**
    * [Planned] **Task W2.1: Documentation Integration (RAG - Keyword):** Implement server-side documentation retrieval using **keyword search** based on the improved documentation (from Doc Phase 2). Inject relevant snippets into LLM prompts (Ref: LLM Plan IV.C Option B - Keyword, V.C). Requires documentation to be indexed.
    * [Planned] **Task W2.2: System Prompt Refinement:** Iteratively refine the LLM system prompt based on observed behavior and feedback (Ref: LLM Plan V.A).
    * [Planned] **Task W2.3: Granular Rate Limiting:** Implement User ID-based rate limiting (requires integration with EGOS auth) and stricter usage limits. Use **Redis** or similar for distributed counter storage if backend scales (Ref: LLM Plan VI.C, VI.D, VI.E).
    * [Planned] **Task W2.4: Cost Monitoring & Web Search:** Implement active cost monitoring. Evaluate and *cautiously* enable web search (`:online`) if deemed necessary, factoring in associated costs and limiting its use (Ref: LLM Plan VI.D, V.B).
    * [Planned] **Task W2.5: Expanded Analytics:** Implement detailed GA4 event tracking (doc interactions, feedback, errors) and configure Custom Dimensions/Metrics. Optionally implement Hotjar (free tier) for qualitative insights (Ref: LLM Plan VII.B, VII.C).
    * [Planned] **Task W2.6: Formal Alternative LLM Evaluation:** Systematically evaluate 2-3 alternative models on OpenRouter based on defined criteria (cost, context, performance, reliability) using EGOS-specific tasks. Document findings (Ref: LLM Plan VIII).
* **Phase 3: Optimization & Resilience (Focus: UX, Cost-Efficiency, Future-Proofing - Q4 2025 / Q1 2026)**
  * **Planned**
    * [Planned] **Task W3.1: UI/UX Polishing:** Refine chat UI based on analytics/feedback. Fully implement response **streaming (SSE)** for better perceived responsiveness (Ref: LLM Plan V.D).
    * [Planned] **Task W3.2: RAG Optimization (Semantic Search - Optional):** If keyword search proves insufficient, investigate and potentially implement semantic search using embeddings and a vector database (Ref: LLM Plan IV.C Option B - Semantic). Assess complexity vs. benefit.
    * [Planned] **Task W3.3: LLM Parameter Tuning:** Optimize `temperature`, `max_tokens`, etc., for cost, performance, and quality (Ref: LLM Plan V.D).
    * [Planned] **Task W3.4: Implement Fallback Mechanism:** Build capability in the backend to switch to a pre-evaluated alternative LLM if `quasar-alpha` fails or is deprecated (Ref: LLM Plan VIII.D).
    * [Planned] **Task W3.5: Migration Strategy:** Develop plan for fully migrating off `quasar-alpha` if necessary.
    * [Planned] **Task W3.6: Advanced Features (Optional):** Explore features like tool calling if beneficial for EGOS interactions.
    * [Planned] **Task W3.7 (Parallel): Website Design & UX Improvements** (Refine CSS, add diagram placeholders, implement subtle animations, ensure intuitive navigation based on `research/WebSite Enio Grok e Gemini.txt`).
    * [Planned] **Task W3.8 (Parallel): User Behavior Analysis (Deferred/Basic)** (Implement basic analytics, defer advanced tools like Hotjar/OpenReplay unless explicitly prioritized later).

### Phase 2: MVP Development & Refinement (Focus: Core Functionality)

* **Subsystems Implementation (Core MVP Features):**
  * **CORUJA (Phase 2b - Multi-Agent with SPARC):** Implement `CrewManager`, `Agent`, `Task`, `SPARCTask`, `SPARCTaskRegistry`, `ToolRegistry`, enhanced `ModelInterface` with task-based selection, `PromptManager`. Focus on executing complex tasks using SPARC methodology. Include foundational hooks for ETHIK integration and basic monitoring.
  * **KOIOS (Phase 2b):** Implement `KoiosLogger` with SPARC support. Define SPARC task schema and validation. Basic search capabilities (e.g., file content search). SPARC task visualization.
  * **ETHIK (Phase 2b):** Implement basic ethical check functions (e.g., keyword flagging, PII detection stubs). Define initial policies for prompt/response checks. **Define initial policies regarding data sensitivity classification and required Privacy-Preserving Computation (PPC) techniques.**
  * MVP Backend: Develop core logic for the Content Aggregator MVP, integrating with CORUJA for AI tasks using SPARC methodology.
  * Basic UI/UX: Implement the essential user interface for the MVP with SPARC task monitoring.
* **Testing:** Develop unit and integration tests for MVP components (Target >80% coverage).
* **Documentation:** Refine subsystem READMEs, document MVP APIs and usage, create SPARC implementation guides.

### Phase 3: Expansion & Hardening

* **Subsystem Enhancements:**
  * CORUJA (Phase 3): Enhance SPARC orchestration with automated workflows, add more specialized task handlers, improve model selection.
  * KOIOS (Phase 3): Implement SPARC task search/analytics, enhance visualization dashboard.
  * ETHIK (Phase 3): Implement more sophisticated ethical checks for SPARC workflows, refine policies based on initial usage. **Verify implementation of PPC techniques according to defined policies.**
  * NEXUS/ATLAS (Phase 3): Begin integrating architectural analysis with SPARC specifications.
* **Security Hardening & Audits:** Perform security reviews, address vulnerabilities. Include AI Safety/Alignment considerations.
* **Performance Optimization:** Identify and address bottlenecks in SPARC workflows.
* **Advanced UI/UX:** Improve task visualization and monitoring based on feedback.

### Ongoing / Cross-Cutting Concerns

* **Research & Development:**
  * `[Planned] Research: Visualization Techniques`. Investigate libraries (D3.js, Three.js, Cytoscape.js) & methods for interactive ATLAS/MYCELIUM visualization. (`MEDIUM`, Phase 2b/3) - ID: `RESEARCH-VISUALIZATION`
  * `[Planned] Research: $ETHIK Integration Architecture`. Define secure technical approach (frontend/backend/API) for token display & reward logic. (`MEDIUM`, Phase 3) - ID: `RESEARCH-ETHIK-ARCH`
  * `[Planned] Research: WCAG for Complex Interactions`. Investigate accessibility standards for custom visualizations & Web3 elements. (`MEDIUM`, Phase 3) - ID: `RESEARCH-WCAG`
  * `[Planned] Research: Agent Frameworks`. Investigate Empyreal SDK and CrewAI for potential integration with EGOS subsystems (MYCELIUM, ETHIK). (`MEDIUM` - R&D) - ID: `RESEARCH-AGENTS-FRAMEWORKS`
  * `[Planned] Research: External Insights`. Analyze insights from Hesamation (X) and Kaggle (Prompt Eng.) for roadmap/workflow improvements. (`LOW` - R&D) - ID: `RESEARCH-EXTERNAL-INSIGHTS`
  * `[Planned] Research: Product Strategy & Market Fit`. Compare EGOS approach with platforms like GitLab/Vercel; analyze market for 'ethical AI tools'. (`MEDIUM` - R&D) - ID: `RESEARCH-PRODUCT-STRATEGY`
  * Mycelium Network Design & Prototyping.
  * **Advanced AI Orchestration Techniques:** Explore enhancements to SPARC methodology ... **(See background studies in `research/`)**
  * Advanced ETHIK Mechanisms (bias detection, explainability).
  * Explore alternative LLMs and specialized AI models for different SPARC phases (Leverage LiteLLM for broad support).
  * Advanced AI Monitoring & Alignment Mechanisms (Context: ASI Risk Scenarios).
  * **PPC Technology Evaluation:** Investigate feasibility ... for EGOS use cases ... **(See background studies in `research/`)**
  * **Verifiable Logging/Actions:** Research and prototype methods ... inspired by Proof-of-View concepts. **(See background studies in `research/`)**
  * **Secure External Access:** Investigate patterns ... for CORUJA agents/tools ... **(See background studies in `research/`)**
  * **Decentralized Automation:** Explore reliable ... mechanisms ... for CORUJA and other subsystems. **(See background studies in `research/`)**
  * **Agent Monitoring & Observability:** Research integration with platforms ... **(See background studies in `research/`)**
  * `[Planned] Research integrating Clanker API for simplified token creation on Base network (LOW)` (See `research/Clanker_Analysis.md`)
  * `[Planned] Research alternative contributor reward models inspired by Clanker's creator-centric approach (MEDIUM - R&D)` (See `research/Clanker_Analysis.md`)
  * `[Planned] Research: AI for Subsystem Configuration Generation (MEDIUM - R&D)` (See `research/SaaS_Framework_Analysis.md`)
  * `[Planned] Research: 3rd-Party API Integration Strategy (Stripe, S3, etc.) (MEDIUM - R&D)` (See `research/SaaS_Framework_Analysis.md`)
  * **[Planned] Task IDE-1: Develop EGOS AI-Integrated Web IDE:** Research and implement a web-based IDE (potentially leveraging VS Code web components or Codespaces APIs) with deep integration of CORUJA for context-aware chat, code generation, and editing, mirroring Cursor's capabilities within the EGOS framework. (`MEDIUM - R&D`, Phase 4/5)
  * **[Planned] Task IDE-2: Design Simplified Mobile UI for Web IDE:** Create a streamlined mobile-first interface for the EGOS Web IDE, focusing on core review, status checking, and quick interaction functionalities. (`LOW - R&D`, Phase 5)

* **Documentation Maintenance:** Continuously update all documentation (MQP, Roadmap, Strategy, Subsystem READMEs, Docstrings, Website Dev Plan, Design Guide).
* **KOIOS Standards Evolution:** Refine and expand KOIOS standards based on project needs and best practices.
* **Community Building & Licensing:** Define and implement strategy.
* **Deployment Automation (HARMONY Lead):**
  * `[Planned] Enhance Deployment Automation (Docker, Python scripts, CI/CD with GitHub Actions)`. (`MEDIUM`)
* **Marketing & Outreach (KOIOS/Strategy Lead):**
  * **[Planned] Task CONTENT-STRATEGY:** Develop and execute a detailed content marketing plan (blog posts, deep dives, essays) based on the ethical marketing strategy and WCS-1. (`HIGH`, Phase 2b/3, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task WEB-SEO-SCHEMA:** Implement Schema.org structured data (JSON-LD) for relevant types on `docs/index.html` and future content pages. (`MEDIUM`, Phase 3/4, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task WEB-SEO-TECH:** Conduct technical SEO audit and implement optimizations (page speed, minification, image optimization, sitemap). (`MEDIUM`, Phase 3/4, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task WEB-SEO-LINKING:** Develop and implement internal linking strategy for website/documentation. (`LOW`, Phase 3, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task COMMUNITY-ENGAGEMENT:** Develop specific plans for authentic engagement on target platforms (GitHub, Reddit, Mastodon, etc.). (`MEDIUM`, Phase 3, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task AMPLIFY-DIRECTORIES:** Systematically submit EGOS to relevant OSS/AI project directories (when ready for broader visibility). (`MEDIUM`, Phase 3/4, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task AMPLIFY-ACADEMIC:** Develop strategy for academic dissemination (arXiv, conferences) if applicable based on research outputs. (`LOW`, R&D, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task AMPLIFY-OUTREACH:** Develop strategy for identifying and engaging potential collaborators and guest blogging opportunities. (`MEDIUM`, Phase 3, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)
  * **[Planned] Task DESIGN-VISUAL-GUIDE:** Develop a visual style guide for EGOS (website, docs, presentations) reflecting the "Art" principle. (`MEDIUM`, Phase 3, Ref: `research/EGOS Ethical Marketing Strategy_.txt`)

* **Governance & Workflow (KOIOS Lead - NEW)**
  * `[Planned] docs(governance): Define AI Collaboration Pipeline`. Document Quasar -> Gemini -> Human Review workflow in `docs/GOVERNANCE.md`. (`HIGH`, Phase 2b) - ID: `GOVERNANCE-PIPELINE`
  * `[Planned] chore(workflow): Automate Handover Notifications`. Explore GitHub Actions to notify team members on handovers/reviews. (`LOW`, Phase 3) - ID: `WORKFLOW-NOTIFY`

**NEW SECTION: Website Design & Foundation (Q2/Q3 2025)**

**Goal:** Define the core visual identity and information architecture, stabilize the static website foundation, and prepare for advanced feature integration (QPG, LLM Chat).
**Status:** In Progress
**Priority:** HIGH

* **Phase WD: Website Design Definition (High Priority Prerequisite)**
  * **Goal:** Generate concrete, EGOS-aligned design directives before major styling implementation.
  * **Status:** DONE
  * **Tasks:**
    * `[DONE] feat(website/design): Generate Core Design Directives`. Based on EGOS principles, subsystems, target UX, Grok/GPT analysis, strategic goals, and internal analysis (`research/EGOS design GROK.txt`). Defines visual themes, metaphors, mood boards, palettes, typography, layout principles, and visual representations for abstract concepts. (`HIGH`, Q2 2025) - ID: `WEBSITE-DESIGN-DIRECTIVES`
    * `[DONE] docs(website/design)`: Document the chosen design directives (from `research/EGOS design GROK.txt`) into a formal design guide (`docs/website/DESIGN_GUIDE.md`). (`HIGH`, Q2 2025) - ID: `WEBSITE-DESIGN-DOC`, `depends_on: [WEBSITE-DESIGN-DIRECTIVES]`

* **Phase WIA: Website Information Architecture (High Priority - NEW)**
  * **Goal:** Define the website's structure, navigation, and basic user flow based on core content and the adopted design directives.
  * **Status:** In Progress
  * **Depends On:** `WEBSITE-DESIGN-DIRECTIVES`
  * **Tasks:**
    * `[In Progress] docs(website/ia): Define Sitemap`. List main pages/sections (Home, Philosophy, Principles, Subsystems, Community/$ETHIK, Roadmap, Genki Dama, Feedback, etc.). (`HIGH`, Q2 2025) - ID: `WEBSITE-SITEMAP`
    * `[Planned] docs(website/ia): Define Navigation Structure`. Plan top navigation, footer links, and key internal linking strategy. (`HIGH`, Q2 2025) - ID: `WEBSITE-NAVIGATION`, `depends_on: [WEBSITE-SITEMAP]`
    * `[Planned] docs(website/ia): Outline Key User Flows`. Map basic journeys for target personas (researcher, contributor, curious visitor). (`MEDIUM`, Q2 2025) - ID: `WEBSITE-USERFLOWS`, `depends_on: [WEBSITE-SITEMAP]`

* **Phase WUX: User Experience Research (Status: Planned - Parallel)**
  * **Goal:** Deepen understanding of target audience needs and refine UX strategy.
  * `[Planned]` **Task WUX-1:** Conduct User Research (Surveys/Interviews) with target personas (e.g., "Contribuidor Técnico", "Pesquisador Ética em IA"). (`MEDIUM`)
  * `[Planned]` **Task WUX-2:** Develop Detailed Personas based on research. (`MEDIUM`)
  * `[Planned]` **Task WUX-3:** Refine User Journeys based on personas and research. (`MEDIUM`)

* **Phase WCS: Content Strategy & Creation (Status: Planned - Parallel)**
  * **Goal:** Develop the narrative and content plan for the website.
  * `[Planned]` **Task WCS-1:** Develop Content Strategy (Storytelling, Educational Resources - UNESCO ref, Blog/News plan, Tone of Voice). (`MEDIUM`)
  * `[Planned]` **Task WCS-2:** Write/Adapt Final Website Copy (aligned with Tone, IA, Design, Content Strategy). (`HIGH`)
  * `[Planned]` **Task WCS-3:** Source/Create Final Imagery & Assets (Illustrations, Icons, Photos - align with Design Guide). (`MEDIUM`)

* **Phase W1: Website Foundation Stabilization & Enhancement (High Priority)**
  * **Goal:** Ensure the static website is stable, accessible, maintainable, **fully styled according to Design Directives and IA**, and prepared for future integrations.
  * **Depends On:** `WEBSITE-DESIGN-DIRECTIVES`, `WEBSITE-NAVIGATION`
  * **Status:** Partially Done
  * **Tasks:**
    * `[DONE] refactor(website/i18n)`: Implement JavaScript/JSON-based internationalization solution.
    * `[DONE] feat(website/js)`: Implement core JS functionality for i18n language switcher (including ARIA state management).
    * `[Planned] fix(website/html)`: Correct HTML semantics (logo `<h1>`, icon ARIA, `target="_blank"` rel attributes, language switcher links, non-semantic separators) based on IA.
    * `[Planned] fix(website/a11y)`: Implement missing ARIA attributes (`aria-expanded`, `aria-controls`, necessary `id`s) for interactive elements (subsystem toggles, language dropdown).
    * `[Planned] feat(website/js)`: Implement/Refine JS for hamburger menu, subsystem toggles based on final design and IA.
    * `[Planned] feat(website/a11y)`: Ensure full keyboard navigation and visible focus states for all interactive elements.
    * `[Planned] style(website/css)`: Implement and refine styling (including dark theme) across all modular CSS files based on the **finalized Design Directives and IA**. (`HIGH`) - ID: `WEBSITE-STYLING`, `depends_on: [WEBSITE-DESIGN-DIRECTIVES, WEBSITE-NAVIGATION]`
    * `[Planned] docs(website/content)`: Populate final content and translations using the i18n system, organized according to IA.
    * `[Planned] feat(website/assets)`: Integrate final visual assets (e.g., SVG logo, favicon) based on Design Directives.
    * `[Planned] test(website)`: Conduct thorough testing (responsive design, functionality, accessibility (WCAG AA), cross-browser).
    * `[Planned] style(website/css)`: Implement footer background color update (`bg-footer-background`) for improved visual comfort. (`LOW`) - ID: `WEBSITE-UI-01`

* **Phase QPG1: Quantum Prompt Generator (QPG) - Planning & MVP (Medium Priority - Parallel)**
  * **Goal:** Plan and develop a Minimum Viable Product (MVP) for the Quantum Prompt Generator SaaS tool, integrated into the website.
  * **Status:** Planned
  * **Tasks:**
    * `[Planned] docs(qpg/planning)`: Define detailed QPG UX/UI flow, select initial LLMs (free/paid tiers), design backend architecture, plan user/credit/payment system (if applicable for MVP).
    * `[Planned] docs(qpg/legal)`: Draft comprehensive Privacy Policy & Terms of Use addressing data usage/personalization, ensuring ETHIK compliance and user control mechanisms (opt-in/out). (**Requires ETHIK review**).
    * `[Planned] feat(qpg/backend)`: Develop MVP backend API for prompt processing and LLM integration.
    * `[In Progress] feat(qpg/frontend)`: Scaffold initial Quantum Prompt Generator React component (`QuantumPromptGenerator.tsx`) with basic structure (Input, Output, Settings placeholders). (`MEDIUM`) - ID: `QPG-FE-SCAFFOLD-01`
    * `[Planned] feat(qpg/frontend)`: Develop MVP frontend JS logic within the website's `#prompt-generator` section to interact with the backend API. `depends_on: [QPG-FE-SCAFFOLD-01]`
    * `[Planned] chore(qpg/deploy)`: Deploy QPG MVP alongside the website.
    * `[Planned] chore(qpg/iteration)`: Gather user feedback and plan next iteration based on MVP performance.

---

**(Note:** This roadmap is dynamic and will be updated based on progress and strategic shifts.)

## 📚 Linked Documentation & Research

* Master Quantum Prompt: `docs/MQP.md`
* EGOS Strategy: `docs/STRATEGY.md`
* KOIOS Standards: `subsystems/KOIOS/docs/STANDARDS.md` & `.cursor/rules/`
* SPARC Orchestration: `.cursor/rules/sparc_orchestration.mdc`
* GitHub Project Search & Analysis: `research/EGOS_ GitHub Project Search_.txt`
* Website Strategic Guide: `research/Criaçao de site com IA.txt`
* Consolidated Design Analysis: `research/EGOS design GROK.txt`
* Design Directives Summary: `research/Análise e Refinamento do Projeto EGOS_.txt`
* Website Design Guide: `docs/website/DESIGN_GUIDE.md`
* Website Development Plan: `docs/website/DEVELOPMENT_PLAN.md`
* (Future) MVP Definition: `docs/strategy/MVP_Definition.md`
* (Future) Mycelium Topics: `subsystems/MYCELIUM/docs/topics.md`
* (Future) SPARC Implementation Guide: `docs/methodology/SPARC_GUIDE.md`

---

### Dynamic Roadmap Sync & Mycelium Interconnection

* **Planned**
  * [Planned] [KOIOS/CORUJA] Implement GitHub ROADMAP.md Fetch & Parse API for Website (`HIGH`) - ID: `ROADMAP-GITHUB-SYNC`
  * [Planned] [KOIOS] Refactor Website Roadmap Component to Use Parsed JSON (`HIGH`) - ID: `ROADMAP-WEBSITE-JSON`
  * [Planned] [MYCELIUM] Emit & Subscribe to Roadmap Update Events (`MEDIUM`) - ID: `ROADMAP-MYCELIUM-EVENTS`
  * [Planned] [CORUJA/KOIOS] Implement Roadmap Change Proposal UI & PR Automation (`MEDIUM`) - ID: `ROADMAP-PR-AUTOMATION`
  * [Planned] [ETHIK/KOIOS] Audit and Log All Roadmap Syncs and Changes (`HIGH`) - ID: `ROADMAP-ETHIK-AUDIT`

### Technical Implementation Plan: Dynamic Roadmap Sync (Phase 1)

* **Overview:**
  - This plan details the first phase of integrating a live, always-synced roadmap between the EGOS website and the canonical `ROADMAP.md` on GitHub, leveraging Mycelium for event-driven updates and KOIOS for documentation/standardization. All actions are cross-referenced with relevant subsystems.

* **Subsystem Context:**
  - **KOIOS:** Documentation structure, roadmap parsing, standards enforcement.
  - **MYCELIUM:** Event bus for roadmap updates, inter-subsystem communication.
  - **CRONOS:** Logging and evolutionary preservation of roadmap sync events.
  - **NEXUS:** Dependency analysis for integration and refactoring.
  - **SYNC:** Ensures data integrity and consistency across subsystems.
  - **ETHIK:** Security, privacy, and ethical validation of all sync actions.
  - **ATLAS:** Visualization of roadmap and sync state.
  - **CORUJA:** Orchestration of sync, UI/UX for roadmap modal, PR automation.
  - **HARMONY:** Ensures cross-platform compatibility of sync logic (especially for Windows).
  - **TRANSLATOR:** (Future) Enables multilingual roadmap/task display if required.
  - **MASTER:** Supervises and validates the overall process.

* **Phase 1 Tasks:**
  - [Planned] [KOIOS/CORUJA] Draft and publish technical specification for GitHub ROADMAP.md API sync (`HIGH`) - ID: `ROADMAP-SPEC-DRAFT`, cross-ref: `ROADMAP-GITHUB-SYNC`
  - [Planned] [KOIOS] Implement parser to convert ROADMAP.md to structured JSON for website (`HIGH`) - ID: `ROADMAP-PARSER-JSON`, cross-ref: `ROADMAP-WEBSITE-JSON`
  - [Planned] [MYCELIUM/CRONOS] Set up event emission and logging for roadmap updates (`MEDIUM`) - ID: `ROADMAP-EVENT-LOG`, cross-ref: `ROADMAP-MYCELIUM-EVENTS`
  - [Planned] [SYNC] Validate sync integrity and handle error states (`HIGH`) - ID: `ROADMAP-SYNC-VALIDATION`, cross-ref: `ROADMAP-MYCELIUM-EVENTS`
  - [Planned] [ETHIK] Audit sync process for security/privacy (`HIGH`) - ID: `ROADMAP-ETHIK-VALIDATION`, cross-ref: `ROADMAP-ETHIK-AUDIT`
  - [Planned] [ATLAS] Visualize roadmap sync status and history (`MEDIUM`) - ID: `ROADMAP-ATLAS-VIZ`
  - [Planned] [CORUJA] UI/UX for displaying live roadmap and sync status (`HIGH`) - ID: `ROADMAP-CORUJA-UI`, cross-ref: `ROADMAP-WEBSITE-JSON`
  - [Planned] [HARMONY] Ensure Windows compatibility for all sync tools/scripts (`HIGH`) - ID: `ROADMAP-HARMONY-COMPAT`
  - [Planned] [MASTER] Review and approve technical plan and implementation (`HIGH`) - ID: `ROADMAP-MASTER-REVIEW`

* **Cross-References:**
  - All tasks reference and depend on the core items in the "Dynamic Roadmap Sync & Mycelium Interconnection" section above.
  - Each subsystem is responsible for its domain and must document actions in accordance with KOIOS and CRONOS standards.

* **Documentation:**
  - The full technical plan and progress are to be documented in both `ROADMAP.md` and the relevant subsystem READMEs (e.g., `subsystems/KOIOS/README.md`, `subsystems/MYCELIUM/README.md`, etc.).

* **Principles:**
  - All work must comply with EGOS Fundamental Principles, especially Universal Accessibility, Reciprocal Trust, Evolutionary Preservation, and Integrated Ethics.

---

### Pending Review & Backlog

* Review all recent chat actions, subsystem capabilities, and architectural decisions for alignment and documentation.
* Ensure all cross-references are maintained and that every subsystem's role in the sync/interconnection plan is clear in their respective README files.
* If any item is not yet resolved or documented, add it here for triage in the next roadmap review cycle.

---

**(Note:** This roadmap is dynamic and will be updated based on progress and strategic shifts.)

## 🚀 Future Phase: Phase 3 - EGOS Hive – Interconnection, MVP Launch & Expansion

*(Details to be elaborated)*

### LLM Integration (CORUJA/NEXUS/ETHIK Lead)

* **Planned**
  * [Planned] [CORUJA/NEXUS] Implement RAG using Vector DB for EGOS Documentation (`HIGH`) - ID: `LLM-RAG-DOCS`
  * [Planned] [CORUJA] Develop Context-Aware Chat Interface on Task Pages (`HIGH`) - ID: `LLM-CHAT-INTERFACE`, `depends_on: [LLM-RAG-DOCS]`
  * [Planned] [ETHIK] Integrate LLM Features with ETHIK Token/Rewards System (`MEDIUM`) - ID: `LLM-ETHIK-INTEGRATE`, `depends_on: [ETHIK-CLAIM-01, LLM-CHAT-INTERFACE]`

## 🏁 Completed Milestones

*   **Phase 1: Foundation & Core AI Interaction (EGOS Alpha)**

---

### Monitoring & Dashboard (ATLAS/KOIOS)

* **In Progress**
  * [In Progress] Integrate Dashboard via Iframe (Streamlit Cloud) (`LOW`) - ID: `DASHBOARD-IFRAME-INTEGRATE`
* **Planned**
  * [Planned] Integrate Real NATS Client (post-Mycelium stabilization) (`HIGH`) - ID: `DASHBOARD-NATS-CLIENT`, `depends_on: [MYCELIUM-RELIABLE]`
  * [Planned] Deploy Dashboard (e.g., Streamlit Cloud) (`MEDIUM`) - ID: `DASHBOARD-DEPLOY`, `depends_on: [DASHBOARD-NATS-CLIENT]`
  * [Planned] Add SPARC Task Visualization (`MEDIUM`) - ID: `DASHBOARD-SPARC-VIZ`, `depends_on: [DASHBOARD-NATS-CLIENT]`
  * [Planned] [ATLAS/CORUJA] Implement Dashboard Theme Alignment with Website (`LOW`) - ID: `DASHBOARD-THEME-ALIGN`
  * [Planned] [ATLAS/CORUJA/ETHIK] Plan Deep Dashboard-Website Integration (API/Bridge for Auth/Data) (`MEDIUM`) - ID: `DASHBOARD-DEEP-INTEGRATE`
  * [Planned] [KOIOS] Update README/Roadmap ref Dashboard Integration (`LOW`) - ID: `DOC-DASHBOARD-INTEGRATION`
  * [Planned] [KOIOS] Update CONTRIBUTING.md ref Website Roadmap Usage (`LOW`) - ID: `DOC-CONTRIB-WEBSITE-FLOW`
* **Completed**
  * ✅ [DONE] Basic Streamlit Dashboard Setup (`MEDIUM`)
  * ✅ [DONE] Implement Modular UI Components (`MEDIUM`)
  * ✅ [DONE] Add Dark/Light Theme Toggle (`LOW`)
  * ✅ [DONE] Integrate Mock NATS Client for Demo (`HIGH`)
  * ✅ [DONE] Implement `KoiosLogger` for Dashboard Interactions (`HIGH`)
  * ✅ [DONE] Improve Light Theme Contrast (`LOW`)
  * ✅ [DONE] Refine Website Task Modal UI/UX (`MEDIUM`) - ID: `WEBSITE-MODAL-UI-REFINE`

### ETHIK Points & Blockchain Claim System

- **Status:** Planned
- **Subsystem(s):** ETHIK, Website, Blockchain
- **Task ID:** ETHIK-CLAIM-01
- **Priority:** HIGH
- **Description:**
  - Implement a system where contributors earn ETHIK points for project contributions. When a user reaches a defined threshold, they can claim the equivalent amount of ETHIK tokens on-chain. The claim is user-initiated and the user pays the blockchain transaction fee at the time of claim. The website must display the current blockchain network fee (gas/tx fee) in real time and explain the process clearly in the contributor dashboard. This approach reduces transaction costs by batching and only sending tokens when users request it.
- **Dependencies:** ETHIK token smart contract deployed, wallet integration (e.g., MetaMask, Phantom), blockchain fee API
- **Principles:** Universal Accessibility, Sacred Privacy, Reciprocal Trust, Integrated Ethics
- **Acceptance Criteria:**
  - Contributors see their ETHIK points balance
  - Can claim tokens to their wallet when threshold is reached
  - Real-time network fee is shown before claim
  - User pays the transaction fee
  - System is clear, secure, and accessible

### 🗣️ User Interaction & Frontend (CORUJA Lead / Website)

* **Planned**
  * [Planned] Define Standard UI Components/Style Guide (`HIGH`)
  * [Planned] Implement User Feedback Mechanisms (`MEDIUM`)
  * [Planned] Explore Voice Input Capabilities (`LOW`)
  * [Planned] Implement Internationalization/Localization Support (`LOW`)
  * [Planned] **[WEBSITE-REVAMP-CORE]** **Website Design, UX, & Technical Overhaul:** Major refactor/rebuild focusing on: Aesthetics (beauty, golden ratio, spirals), Interactivity, Accessibility (WCAG AA+, colorblind friendly), Responsiveness (mobile-first), Performance (lightweight), and Modern Framework (confirm Next.js/SvelteKit/Astro). Ensure intuitive navigation based on `research/WebSite Enio Grok e Gemini.txt` and `docs/website/DESIGN_GUIDE.md`. (`CRITICAL`)
  * [Planned] **Task W3.8 (Parallel): User Behavior Analysis (Deferred/Basic)** (Implement basic analytics, defer advanced tools like Hotjar/OpenReplay unless explicitly prioritized later).
  * [Planned] **[WEB/KOIOS][WEBSITE-ACCESSIBILITY-AUDIT]** Perform accessibility audit and implement necessary fixes (WCAG AA minimum) (`CRITICAL`), `depends_on: [WEBSITE-REVAMP-CORE]`

### Website Maturity:

feat/roadmap-updates
* [Planned] **[WEBSITE-GENKI-DAMA]** **Genki Dama Page Implementation:** Design and implement the "Genki Dama" page featuring specific artwork, clear calls for collaboration/contribution, and donation addresses (e.g., Solana: `[Your Solana Address]`, BTC: `[Your BTC Address]`, EVM: `[Your EVM Address]`). Ensure minimal text and focus on artistic/mysterious appeal. (`HIGH`)
* [Planned] **[WEB/ETHIK][WEBSITE-DONATION-INTEGRATION]** Securely integrate and test donation mechanisms for Genki Dama page (`HIGH`), `depends_on: [WEBSITE-GENKI-DAMA]`

## 🚀 EGOS DevKit Extension (Developer Experience Enhancement)

**Goal:** Enhance the VS Code development experience specifically for the EGOS project by creating a custom extension (`egos-devkit`) that complements the existing Windsurf extension and provides shortcuts, automations, and contextual information tailored to EGOS workflows and standards.
**Status:** Planned
**Priority:** MEDIUM
**Owner:** Developer Experience Team / Initial: [Your Name/Handle]
**Related Docs:** Extension codebase (to be created)

*   **Phase 0: Research & Definition (Status: Completed - 2025-04-17)**
    *   `[DONE]` **Task EXT-DEF-01:** Define goal: Complement Windsurf, customize VS Code for EGOS.
    *   `[DONE]` **Task EXT-DEF-MVP-01:** Define MVP features: Terminal command execution, basic Webview placeholder.
    *   `[CRITICAL]` **Task EXT-CHECK-WINDSURF-API-01:** Re-confirm Windsurf API status for potential deeper integration (Ongoing Check).

*   **Phase 1: Skeleton & Core Setup (Status: Planned - Est: 1-2 days)**
    *   `[Planned]` **Task EXT-INIT-01:** Initialize VS Code Extension project (`egos-devkit`) using `yo code` (TypeScript).
    *   `[Planned]` **Task EXT-STRUCTURE-01:** Create basic file structure (`src/extension.ts`, `src/commands/`, `src/panels/`).
    *   `[Planned]` **Task EXT-PACKAGE-JSON-01:** Configure `package.json` (name, activation events, contribution points).
    *   `[Planned]` **Task EXT-LINT-FORMAT-01:** Setup ESLint/Prettier.

*   **Phase 2: MVP Feature Implementation (Status: Planned - Est: 2-4 days)**
    *   `[Planned]` **Task EXT-CMD-TERMINAL-01:** Implement reliable `executeTerminalCommand`.
    *   `[Planned]` **Task EXT-CMD-PALETTE-01:** Ensure command visibility in Command Palette.
    *   `[Planned]` **Task EXT-PANEL-WEBVIEW-01:** Implement basic Webview View placeholder panel.
    *   `[Planned]` **Task EXT-TEST-BASIC-01:** Manually test MVP features.

*   **Phase 3: Refinement & Integration (Status: Planned - Est: Ongoing)**
    *   `[Planned]` **Task EXT-ADD-SHORTCUT-01:** Add optional keyboard shortcut for terminal command.
    *   `[Planned]` **Task EXT-INTEGRATE-API-X:** Plan/implement integration with specific APIs (e.g., GitHub, EGOS backend, potentially Windsurf commands if feasible).
    *   `[Planned]` **Task EXT-ENHANCE-UX-01:** Improve UI/UX based on usage.

---

## 📐 Structure & Best Practices

* **Clear Sections**: Group tasks by Phase or Category.
* **Priority Tags**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
* **Status Indicators**: `Planned`, `In Progress`, `Completed`, `Blocked`, `DONE`.
* **Responsibility**: Assign owner or team where applicable.
* **Linked Issues/PRs/Docs**: Reference relevant GitHub items or documentation.
* **Dates (Optional)**: Target quarters or specific deadlines.
* **References**: Use `(See analysis in research/)` to link tasks to the GitHub project study.

---

### Monitoring & Dashboard (ATLAS/KOIOS)

* [DONE] Basic Streamlit Dashboard Setup (`MEDIUM`)
* [DONE] Implement Modular UI Components (`MEDIUM`)
* [DONE] Add Dark/Light Theme Toggle (`LOW`)
* [DONE] Integrate Mock NATS Client for Demo (`HIGH`)
* [DONE] Implement `KoiosLogger` for Dashboard Interactions (`HIGH`)
* [DONE] Link Dashboard to Main Website (`LOW`)
* [DONE] Improve Light Theme Contrast (`LOW`)
* [Planned] Refine Dashboard UI/UX based on feedback (`MEDIUM`) - ID: `DASHBOARD-UI-REFINE`
* [Planned] Integrate Real NATS Client (post-Mycelium stabilization) (`HIGH`) - ID: `DASHBOARD-NATS-CLIENT`, `depends_on: [MYCELIUM-RELIABLE]`
* [Planned] Deploy Dashboard (e.g., Streamlit Cloud) (`MEDIUM`) - ID: `DASHBOARD-DEPLOY`, `depends_on: [DASHBOARD-NATS-CLIENT]`
* [Planned] Add SPARC Task Visualization (`MEDIUM`) - ID: `DASHBOARD-SPARC-VIZ`, `depends_on: [DASHBOARD-NATS-CLIENT]`

### 🗣️ User Interaction & Frontend (CORUJA Lead / Website)

* [Planned] Define Standard UI Components/Style Guide (`HIGH`)
* [Planned] Implement User Feedback Mechanisms (`MEDIUM`)
* [Planned] Explore Voice Input Capabilities (`LOW`)
* [Planned] Implement Internationalization/Localization Support (`LOW`)
* [Planned] **[WEBSITE-REVAMP-CORE]** **Website Design, UX, & Technical Overhaul:** Major refactor/rebuild focusing on: Aesthetics (beauty, golden ratio, spirals), Interactivity, Accessibility (WCAG AA+, colorblind friendly), Responsiveness (mobile-first), Performance (lightweight), and Modern Framework (confirm Next.js/SvelteKit/Astro). Ensure intuitive navigation based on `research/WebSite Enio Grok e Gemini.txt` and `docs/website/DESIGN_GUIDE.md`. (`CRITICAL`)
* [Planned] **Task W3.8 (Parallel): User Behavior Analysis (Deferred/Basic)** (Implement basic analytics, defer advanced tools like Hotjar/OpenReplay unless explicitly prioritized later).
* [Planned] **[WEB/KOIOS][WEBSITE-ACCESSIBILITY-AUDIT]** Perform accessibility audit and implement necessary fixes (WCAG AA minimum) (`CRITICAL`), `depends_on: [WEBSITE-REVAMP-CORE]`

### Website Maturity:

* [Planned] **[WEBSITE-GENKI-DAMA]** **Genki Dama Page Implementation:** Design and implement the "Genki Dama" page featuring specific artwork, clear calls for collaboration/contribution, and donation addresses (e.g., Solana: `[Your Solana Address]`, BTC: `[Your BTC Address]`, EVM: `[Your EVM Address]`). Ensure minimal text and focus on artistic/mysterious appeal. (`HIGH`)
* [Planned] **[WEB/ETHIK][WEBSITE-DONATION-INTEGRATION]** Securely integrate and test donation mechanisms for Genki Dama page (`HIGH`), `depends_on: [WEBSITE-GENKI-DAMA]`

* **Planned**
  * [Planned] **[WEBSITE-GENKI-DAMA]** **Genki Dama Page Implementation:** Design and implement the "Genki Dama" page featuring specific artwork, clear calls for collaboration/contribution, and donation addresses (e.g., Solana: `[Your Solana Address]`, BTC: `[Your BTC Address]`, EVM: `[Your EVM Address]`). Ensure minimal text and focus on artistic/mysterious appeal. (`HIGH`)
  * [Planned] **[WEB/ETHIK][WEBSITE-DONATION-INTEGRATION]** Securely integrate and test donation mechanisms for Genki Dama page (`HIGH`), `depends_on: [WEBSITE-GENKI-DAMA]`

## 🚀 Future Phase: Phase 3 - EGOS Hive – Interconnection, MVP Launch & Expansion

*(Details to be elaborated)*

### LLM Integration (CORUJA/NEXUS/ETHIK Lead)

* **Planned**
  * [Planned] [CORUJA/NEXUS] Implement RAG using Vector DB for EGOS Documentation (`HIGH`) - ID: `LLM-RAG-DOCS`
  * [Planned] [CORUJA] Develop Context-Aware Chat Interface on Task Pages (`HIGH`) - ID: `LLM-CHAT-INTERFACE`, `depends_on: [LLM-RAG-DOCS]`
  * [Planned] [ETHIK] Integrate LLM Features with ETHIK Token/Rewards System (`MEDIUM`) - ID: `LLM-ETHIK-INTEGRATE`, `depends_on: [ETHIK-CLAIM-01, LLM-CHAT-INTERFACE]`

```
main
