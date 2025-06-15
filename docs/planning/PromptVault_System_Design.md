@references:
  - docs/planning/PromptVault_System_Design.md

# EGOS PromptVault System Design

**Version:** 0.1.0
**Date:** {{ CURRENT_DATE_ISO }}

## 1. Introduction

The PromptVault system is designed to capture, store, organize, and reuse high-quality, distilled prompts generated from interactions with Large Language Models (LLMs) within the EGOS ecosystem. This practice, often referred to as "prompt distillation," is a key component of EGOS's "Reverse Prompt Engineering" strategy. It aims to create a library of efficient, reliable, and reusable "master prompts" (or "super prompts") that can produce desired outputs consistently, reducing conversational overhead and forming a core part of our evolving AI interaction knowledge base.

This document outlines the vision, goals, architecture, and phased implementation plan for the PromptVault system.

## 2. System Goals

*   **Capture:** Systematically capture effective prompts derived from successful LLM interactions.
*   **Distill:** Refine these captures into concise, optimized "super prompts."
*   **Store:** Persist these super prompts along with relevant metadata in a structured format.
*   **Organize:** Classify prompts using tags, types, and context for easy discoverability.
*   **Reuse:** Enable users and AI agents to easily find and reuse vaulted prompts.
*   **Evolve:** Create a living library that grows and improves over time.
*   **Facilitate Reverse Prompt Engineering:** Serve as a primary resource and dataset for understanding and mastering prompt construction, enabling the creation of highly effective "master prompts."

## 3. Phased Implementation Plan

### Phase 1: Manual Trigger & Basic Storage (MVP)

*   **Workflow (`/distill_and_vault_prompt`):** A manually triggered Windsurf workflow guides the user through:
    *   Requesting the super prompt from the LLM.
    *   Validating the super prompt in a fresh LLM session.
    *   Manually gathering metadata.
    *   Manually creating a JSON file in the PromptVault directory.
*   **PromptVault Directory:** `c:\EGOS\PromptVault\` established as the central repository.
*   **Documentation:** This design document and the workflow file.
*   **Status & Validation (as of 2025-06-09):** Phase 1 successfully tested. The manual workflow (`/distill_and_vault_prompt`) was validated, the `PromptVault` directory was created, and the first prompt was successfully vaulted. The workflow document was also enhanced with an inline example.

### Phase 2: Semi-Automated Capture & Scripting

*   **Helper Script (`prompt_distiller.py` or `.ps1`):**
    *   Automates the creation of the JSON file, including UUID generation, timestamping, and prompting for metadata.
    *   Integrated into the `/distill_and_vault_prompt` workflow.
*   **`.windsurfrules` Integration (Basic):**
    *   Simple rules to suggest using the workflow/script when keywords like "checkpoint prompt" are detected.

### Phase 3: Advanced Automation, Querying & UI (Future)

*   **Automated Detection:** Explore advanced `.windsurfrules` or agent logic to infer "good outputs" and proactively suggest/initiate distillation.
*   **Query Script/Tool (`promptvault_query.py` or `.ps1`):**
    *   Enables searching the PromptVault by tags, type, keywords, etc.
*   **Database Integration (Optional):** Consider SQLite or a vector database for more sophisticated querying and semantic search.
*   **Dedicated UI (Optional):** A web interface within EGOS for browsing, searching, and managing the PromptVault.
*   **Feedback Loop:** Mechanisms for rating and prioritizing prompts based on usage and effectiveness.

## 4. PromptVault Architecture

### 4.0. Leveraging Agentic AI Patterns for Optimal Prompt Design

Crafting effective and reusable "super prompts" for the PromptVault goes beyond just capturing a good interaction. It involves structuring the prompt in a way that guides the AI's behavior predictably and reliably. Incorporating established "Agentic AI Patterns" can significantly enhance prompt quality. These patterns, observed in effective AI agent interactions, help ensure clarity, robustness, and better alignment with user intent.

Consider these patterns when designing or refining prompts for the Vault:

1.  **Context Reassertion:**
    *   **Description:** The AI explicitly restates or confirms critical pieces of context it has received or inferred before proceeding.
    *   **PromptVault Application:** Design prompts to instruct the AI to summarize its understanding of the provided input or the current state before generating a detailed response. This helps catch misunderstandings early.
    *   *Example Prompt Snippet:* `"Before you generate the code, briefly state the primary goal and the key constraints you are working with."`

2.  **Intent Echoing:**
    *   **Description:** The AI confirms its understanding of the user's core goal or question.
    *   **PromptVault Application:** Prompts should guide the AI to paraphrase the user's intent.
    *   *Example Prompt Snippet:* `"My understanding is you want to [paraphrased user goal]. Is this correct?"` (More suitable for interactive scenarios, but the principle can be adapted for direct output prompts by having the AI state its interpreted goal).

3.  **Semantic Anchoring:**
    *   **Description:** The AI ties its responses or actions to specific, unambiguous references in the input or context (e.g., line numbers, specific file names, defined terms).
    *   **PromptVault Application:** Encourage prompts that require the AI to reference specific parts of the input data or previous statements.
    *   *Example Prompt Snippet:* `"When suggesting changes, refer to the exact line numbers of the code snippet provided."`

4.  **Answer-Only Output Constraint:**
    *   **Description:** The AI provides only the direct answer or requested output without conversational filler, especially when the output is meant for programmatic use.
    *   **PromptVault Application:** For prompts designed to generate structured data or code, explicitly instruct the AI to avoid extraneous explanations unless specifically requested.
    *   *Example Prompt Snippet:* `"Provide only the Python code block. Do not include any explanatory text before or after the code."`

5.  **Adaptive Framing:**
    *   **Description:** The AI adjusts its response style, confidence level, or requests for clarification based on the perceived ambiguity or complexity of the query.
    *   **PromptVault Application:** Prompts can include instructions on how to behave when faced with uncertainty.
    *   *Example Prompt Snippet:* `"If the request is ambiguous, list the possible interpretations and ask for clarification before proceeding. If confident, proceed directly."`

6.  **Declarative Intent Pattern:**
    *   **Description:** The AI's role, capabilities, and limitations are clearly stated at the beginning of an interaction or within its core instructions.
    *   **PromptVault Application:** Master prompts should clearly define the AI's persona, task, and any boundaries.
    *   *Example Prompt Snippet:* `"You are an expert Python code reviewer. Your task is to identify potential bugs and suggest improvements based on PEP 8 guidelines. You will not generate new features."`

7.  **Instructional Framing Voice:**
    *   **Description:** The AI uses metacognitive guidance or gives instructions to the user on how to best interact with it or interpret its responses.
    *   **PromptVault Application:** While less common for vaulted "super prompts" (which are often instructions *to* the AI), this pattern can be relevant if the prompt's output is intended to guide a user through a complex process. More often, the prompt itself will use an instructional voice *towards* the AI.
    *   *Example Prompt Snippet (AI guiding user):* `"To get the best results, please provide the following three pieces of information...\"`
    *   *Example Prompt Snippet (User guiding AI, more typical for PromptVault):* `"Follow these steps carefully: First, analyze X. Second, synthesize Y. Finally, output Z in JSON format."`

8.  **Constraint Signaling Pattern:**
    *   **Description:** The AI clearly communicates any constraints it's operating under or that apply to its output (e.g., length limits, format requirements).
    *   **PromptVault Application:** Prompts should explicitly state output format requirements, length constraints, or other rules the AI must follow.
    *   *Example Prompt Snippet:* `"The summary must be no more than 200 words and must be in bullet-point format."`

**Relation to MASS (Multi-Agent System Search):**

While PromptVault primarily focuses on individual "super prompts" (akin to **Localized Prompt Optimization** in the MASS framework), the principles of effective agentic communication are foundational. As EGOS evolves, these well-crafted prompts can become building blocks in more complex AI-driven workflows (topologies). Ensuring each prompt is robust and clear through these patterns contributes to the overall effectiveness of any larger system they might become part of, aligning with the spirit of **Global Prompt Optimization** by fostering consistency and reliability.

By consciously applying these patterns, prompts stored in PromptVault will be more robust, easier to understand (for both humans and AI), and more likely to produce the desired outcomes consistently.

### 4.1. Directory Structure

*   **Root:** `c:\EGOS\PromptVault\`
*   **Subdirectories (Optional for future organization, e.g., by `asset_type` or `year/month`):
    *   `c:\EGOS\PromptVault\code_generation\`
    *   `c:\EGOS\PromptVault\documentation_text\`
    *   `c:\EGOS\PromptVault\2025\06\`

### 4.2. File Naming Convention

*   `YYYY-MM-DD_HHMMSS_<primary_keyword_or_title_slugified>.json`
*   Example: `2025-06-09_103000_python_yaml_scan.json`

### 4.3. Prompt File Format (JSON)

Each distilled prompt will be stored as a JSON file with the following structure:

```json
{
  "id": "uuid_v4_string", // Auto-generated in Phase 2+
  "timestamp_created": "YYYY-MM-DDTHH:MM:SSZ", // Auto-generated
  "timestamp_updated": "YYYY-MM-DDTHH:MM:SSZ", // Auto-generated
  "title": "Concise, descriptive title for the prompt",
  "distilled_prompt": "The validated super prompt text itself.",
  "original_interaction_log": "Text blob or reference to the original interaction log. Highly recommended for reverse engineering.",
  "user_goal_summary": "Concise summary of what the user was trying to achieve in the original interaction.",
  "key_information_provided_by_user": "Critical pieces of information, context, or constraints the user provided that were essential for the LLM's success (array of strings or text blob).",
  "llm_source_original_output": "Identifier for the LLM that produced the original good output (e.g., Cascade, ChatGPT-4, Claude-3-Sonnet)",
  "llm_source_distillation": "Identifier for the LLM/process that helped distill the prompt (e.g., Cascade, ChatGPT-4, human_refined, ai_assisted_analysis)",
  "llm_persona_elicited": "If the LLM adopted a specific persona or role successfully (string, optional).",
  "llm_parameters_inferred": { // Optional object for speculative parameters
    "temperature_approx": "e.g., 0.5",
    "style_observed": "e.g., formal, creative"
  },
  "asset_type": "Predefined category (see vocabulary below)",
  "tags": ["keyword1", "keyword2", "relevant_technology"],
  "related_files_or_artifacts": [
    "c:/EGOS/path/to/relevant_script.py",
    "EGOS_Roadmap.md#feature-xyz"
  ],
  "usage_instructions_or_notes": "Any specific instructions for using this prompt, or observations.",
  "refinement_iterations": 0, // Number of significant back-and-forths to get the desired output before distillation.
  "distillation_method": "llm_self_reflection | human_refined | ai_assisted_analysis", // How the super prompt was derived.
  "validation_results": {
    "success": true, // boolean
    "tested_on_llm": "Identifier for the LLM used for validation (e.g., Cascade, ChatGPT-4)",
    "validation_notes": "Any specific observations during validation (string, optional).",
    "user_effectiveness_rating": 0 // Integer 1-5, optional
  },
  "version": "1.0"
}
```

### 4.4. Asset Type Vocabulary (Initial List - Expandable)

*   `code_generation`
*   `code_refactoring`
*   `code_explanation`
*   `documentation_text_creation`
*   `documentation_text_update`
*   `planning_strategy_development`
*   `rule_definition` (for `.windsurfrules`)
*   `workflow_step_generation`
*   `workflow_creation`
*   `data_analysis_query`
*   `image_generation_prompt`
*   `general_qa_optimized`
*   `translation_request`
*   `summarization_request`
*   `prompt_distillation_itself` (meta-prompts for this process)
*   `other`

## 5. Integration with `.windsurfrules` (Conceptual for Phase 2+)

Future `.windsurfrules` could include:

```yaml
# RULE-PROMPTVAULT-S01: Suggest Prompt Distillation on User Cue
# Purpose: Remind the user to consider distilling and vaulting a high-quality LLM interaction.
# Trigger: When the user explicitly indicates satisfaction or a desire to checkpoint.
# --- 
# onUserInteraction:
#   ifUserSaysPattern: [ "perfect!", "great result", "exactly what I wanted", "checkpoint this prompt", "save this interaction", "good prompt" ]
#   # andConfidenceScore: high # (Hypothetical capability)
#   then:
#     suggestWorkflow: "/distill_and_vault_prompt"
#     withMessage: "This seems like a valuable interaction! Would you like to distill this into a 'super prompt' and save it to the PromptVault using the '/distill_and_vault_prompt' workflow?"

# RULE-PROMPTVAULT-A01: (More Advanced) Auto-trigger Distillation Script (Phase 2/3)
# Purpose: Semi-automatically initiate the prompt distillation script.
# --- 
# onUserCommand: "vault_this_prompt"
# then:
#  runScript: "c:\EGOS\scripts\prompt_distiller.py --mode=interactive --last_llm_output_ref=CASCADE_LAST_RESPONSE_ID"
#  # Requires Windsurf to pass context like last response ID to the script
```
(Note: The exact syntax and capabilities depend on the Windsurf rule engine.)

## 6. Workflow Integration

The primary interaction in Phase 1 will be through the `/distill_and_vault_prompt` workflow, detailed in `c:\EGOS\.windsurf\workflows\distill_and_vault_prompt.md`.

## 7. Future Considerations

*   **Versioning of Prompts:** How to handle updates to existing super prompts.
*   **Prompt Chaining:** Storing sequences of prompts that work together.
*   **Performance Metrics:** Tracking which prompts are most effective or most used.
*   **Access Control:** If needed, managing permissions for contributing to or using the PromptVault.