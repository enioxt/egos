---
title: KOIOS Strategic Analysis Process
version: 1.0.0
status: Active
date: 2025-04-24
subsystem: KOIOS
tags: [documentation, egos, koios, process, strategy, analysis, atlas, nexus]
@references:
- Core References:
  - [MQP.md](mdc:../../../docs/core_materials/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../../ROADMAP.md) - Project roadmap and planning
  - [STRATEGY.md](mdc:../../../docs/STRATEGY.md) - Core EGOS Strategy Document
  - [Process Index](../process_index.md) - Index of all KOIOS processes
- Specific Dependencies:
  - Meta Prompt Location: `../../../STRATEGIC_THINKING/meta_prompts/`
  - Analysis Output Location: `../../../STRATEGIC_THINKING/analyses/`
  - Research Input Location: `../../../docs/research/`, `../../../STRATEGIC_THINKING/research_links/`
  - [ATLAS Subsystem](../../ATLAS/README.md) - For goal setting
  - [NEXUS Subsystem](../../NEXUS/README.md) - For feasibility/dependency analysis
---

# KOIOS Strategic Analysis Process

## 1. Purpose

This standard defines the KOIOS-managed process for conducting in-depth strategic analysis within the EGOS project. It mandates the use of the standardized "Elite Multidisciplinary Strategic Committee" meta-prompt (found in `STRATEGIC_THINKING/meta_prompts/`) to ensure comprehensive, consistent, and well-documented strategic thinking, leveraging diverse perspectives and incorporating critical considerations like Human-AI collaboration and AI risks.

This process involves coordination between ATLAS (for goal setting) and NEXUS (for feasibility/dependency analysis) to ensure strategic decisions are data-driven, aligned with EGOS principles, and consider technical constraints and opportunities.

## 2. Trigger Conditions

The **Elite Multidisciplinary Strategic Committee meta-prompt** (located at `../../../STRATEGIC_THINKING/meta_prompts/strategic_analysis_prompt_vX.Y.md` - use latest version) **MUST** be used when:

*   Planning a new major development phase (e.g., quarterly planning, initiating Phase 3).
*   Evaluating a significant new product concept or feature (e.g., defining an MVP, considering a major pivot).
*   Analyzing substantial market research findings or competitive intelligence.
*   Making critical architectural decisions with broad strategic implications.
*   Reviewing and potentially revising the core EGOS Strategy ([`STRATEGY.md`](mdc:../../../docs/STRATEGY.md)) or Master Quantum Prompt ([`MQP.md`](mdc:../../../docs/core_materials/MQP.md)).
*   Requested explicitly by project leadership for a specific strategic question.

## 3. Workflow Steps

1.  **Context Preparation:**
    *   Clearly define the `[Specific Context/Focus]` for the analysis.
    *   Gather all relevant background information, existing documents, research findings (e.g., from [`../../../docs/research/`](../../../docs/research/) or [`../../../STRATEGIC_THINKING/research_links/`](../../../STRATEGIC_THINKING/research_links/)).
    *   Identify the current version of the `strategic_analysis_prompt_vX.Y.md` in `../../../STRATEGIC_THINKING/meta_prompts/` to be used.

2.  **Prompt Execution:**
    *   Provide the prepared context and background information to the AI assistant (acting as the Committee).
    *   Execute the chosen meta-prompt, ensuring the AI understands its role and the required analysis areas.
    *   If the AI asks clarifying questions (as instructed in the prompt), provide the necessary details.

3.  **Analysis Review & Iteration:**
    *   Critically review the generated analysis output from the AI Committee.
    *   Check for depth, clarity, logical consistency, and coverage of all mandatory areas.
    *   Assess the identification and mitigation strategies for risks, especially AI-related ones.
    *   If the analysis is insufficient, iterate by refining the context, asking follow-up questions, or prompting for deeper exploration of specific sections (leveraging techniques like Chain-of-Thought or requesting critiques of alternatives).

4.  **Output Storage & Interlinking:**
    *   Save the **final, reviewed** analysis report as a Markdown file in the `../../../STRATEGIC_THINKING/analyses/` directory.
    *   Use a descriptive filename, including the focus and date (e.g., `analysis_local_agent_mvp_concept_2025-04-24.md`).
    *   **Mandatory:** Within the analysis document, include explicit Markdown links:
        *   Back to the specific version of the meta-prompt used (e.g., `Prompt Used: [strategic_analysis_prompt_v2.1.md](mdc:../../../STRATEGIC_THINKING/meta_prompts/strategic_analysis_prompt_v2.1.md)`).
        *   To key background documents or research papers used as context (e.g., `Context Based On: [LLM/IDE Study](mdc:../../../docs/research/Integração_LLM_em_IDEs_.txt)`).
        *   To any **new or updated tasks** added to the project roadmap as a result of the analysis (e.g., `Recommendation leads to: [See ROADMAP Task: CORUJA-API-Design]` - referencing the task ID in [`ROADMAP.md`](mdc:../../../ROADMAP.md)).
        *   To relevant KOIOS standards or ETHIK principles discussed (e.g., `Mitigation aligns with: [security_practices.mdc](mdc:../../../.cursor/rules/security_practices.mdc)`).

5.  **Roadmap Integration:**
    *   Ensure that actionable recommendations from the analysis (especially those in the "Action Plan" section) are translated into specific, actionable tasks in the [`ROADMAP.md`](mdc:../../../ROADMAP.md) file, following its standard format.
    *   Reference the analysis document within the relevant roadmap tasks (e.g., `(Derived from analysis: ../../../STRATEGIC_THINKING/analyses/analysis_local_agent_mvp_concept_2025-04-24.md)`).

## 4. Prompt Evolution

The Multidisciplinary Strategic Committee meta-prompt itself is subject to evolution. Updates should be:

*   Version-controlled (incrementing the version number in the filename and content).
*   Based on lessons learned, new research, or evolving EGOS needs.
*   Documented with a rationale for changes.
*   Managed within the `../../../STRATEGIC_THINKING/meta_prompts/` directory.

## 5. Rationale for Standardization

This structured KOIOS workflow ensures that strategic analysis in EGOS is:

*   **Comprehensive:** Leveraging a multidisciplinary perspective defined in the standard prompt.
*   **Consistent:** Following a repeatable process and output structure.
*   **Actionable:** Directly feeding into roadmap planning.
*   **Traceable:** Creating clear links between strategy, research, prompts, analyses, and tasks.
*   **Context-Aware:** Explicitly integrating project context and relevant research.
*   **Risk-Aware:** Incorporating considerations for AI ethics, security, and collaboration risks.

Adhering to this standard promotes informed decision-making and aligns strategic thinking with EGOS's core principles and practical development needs.
