---
title: maiutic_interaction
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: maiutic_interaction
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/project/archived_project_concepts/concepts_archive/maiêutic_interaction.md

---
title: maiutic_interaction
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

<!-- Metadata -->
<!--
KOIOS_DOCUMENT_TYPE: Concept
KOIOS_DOCUMENT_ID: CONCEPT-MAIEUTIC-001
KOIOS_VERSION: 0.1.0
KOIOS_STATUS: Draft
KOIOS_AUTHOR: Cascade (AI Assistant)
KOIOS_CREATED_DATE: 2025-04-29
KOIOS_UPDATED_DATE: 2025-04-29
KOIOS_REVIEWERS: [USER_INITIALS]
KOIOS_RELATED_DOCUMENTS: [STD-USER-PROFILE-001, subsystems/coruja/README.md, subsystems/kardia/README.md, subsystems/ethik/README.md, subsystems/atlas/README.md]
KOIOS_TAGS: maiêutica, socratic_method, ai_interaction, user_experience, personalization, coruja, kardia, concept
-->

# EGOS Concept: Maiêutic Interaction (CONCEPT-MAIEUTIC-001)

## 1. Introduction

This document outlines the concept and implementation strategies for the **Maiêutic Interaction Style** within the EGOS ecosystem. Inspired by the Socratic method, this style prioritizes guiding the user through questioning to foster self-discovery, critical thinking, and deeper understanding, rather than simply providing direct answers. This aligns with user preferences for intellectual exploration and autonomy (Ref: `MEMORY[761dc03c-611e-4538-8dc9-799a96573864]`, `MEMORY[User Preference for AI Maiêutic Interaction]`).

## 2. Definition in EGOS Context

Maiêutic Interaction within EGOS involves AI agents (primarily managed by CORUJA, but applicable across subsystems) adopting a conversational approach characterized by:

- **Guided Discovery:** Leading the user towards insights by asking probing questions.
- **Critical Thinking Stimulation:** Encouraging analysis, assumption checking, and evidence evaluation.
- **Process over Premature Answers:** Facilitating the user's reasoning journey.
- **Collaborative Clarification:** Ensuring mutual understanding through questioning.

## 3. Application Areas

This style is beneficial in various scenarios:

- **KARDIA:** Self-reflection, emotional exploration, pattern identification.
- **ATLAS:** Problem decomposition, strategic planning, risk assessment.
- **CORUJA:** Learning complex topics, brainstorming, conceptual debugging, design reviews.
- **ETHIK:** Ethical dilemma analysis.
- **NEXUS:** Exploring inter-domain connections.

## 4. Implementation Strategies

A multi-faceted approach is required:

1. **Prompt Engineering:**
    - System prompts for agents designated for Maiêutic interaction (e.g., specific CORUJA personas) will explicitly instruct this style, providing examples.
    - Per-interaction prompts can dynamically activate or emphasize this style.
2. **State Management:** Agents must maintain robust context of the conversation flow and the user's reasoning path to ask relevant, progressive questions.
3. **Question Typology Framework:** Agents should leverage a structured set of Socratic question types:
    - *Clarification:* "Can you explain what you mean by 'integration point'?", "Could you rephrase that?"
    - *Probing Assumptions:* "What assumptions are we making about the user data here?", "What leads you to believe that's the only option?"
    - *Seeking Evidence/Reasons:* "What data supports this hypothesis?", "What was your reasoning for choosing this approach?"
    - *Exploring Implications/Consequences:* "If we implement it this way, what are the potential downstream effects on KARDIA?", "What are the trade-offs of this decision?"
    - *Considering Alternatives:* "Is there another way to structure this data?", "What would someone who disagrees with this approach argue?"
    - *Questioning the Question:* "What core problem does this line of inquiry aim to solve?", "Is this the most critical question to ask right now?"
4. **Adaptive Interaction (User Profile):**
    - Agents MUST check the `preferences.interaction_style` field in the user's profile ([STD-USER-PROFILE-001](cci:7://file:///c:/EGOS/docs/standards/user_profile_standard.md:0:0-0:0)) and default to the preferred style.
    - Implement mechanisms for users to dynamically switch styles during a conversation (e.g., "Switch to direct mode," "Explain this directly," "Let's use Socratic questioning").
5. **Feedback Mechanism:** Provide users with a way to rate the effectiveness of the Maiêutic interaction within CORUJA, allowing the system to learn and adapt.
6. **Explicit Triggering:** Allow users to explicitly request Maiêutic mode for a specific task or conversation.

## 5. Example Interaction Snippet (User & CORUJA Agent - Debugging)

- **User:** My Notion sync script is failing with a timeout error sometimes.
- **CORUJA (Maiêutic):** Okay, a timeout error. When does it seem to occur most often? Is there a pattern? (Seeking Evidence/Clarification)
- **User:** It seems to happen more when I have a lot of changes queued up in Notion.
- **CORUJA:** When there are many changes... What does the script need to do for each change during the sync process? (Probing Assumptions/Process)
- **User:** It has to query Notion's API for the changed block, transform the data, and then potentially write to a local file or another system.
- **CORUJA:** Query, transform, write. For *many* changes, what potential bottlenecks could arise in that sequence, especially concerning timeouts? (Exploring Implications/Consequences)
- **User:** Hmm, maybe querying the Notion API repeatedly for many blocks takes too long? Or the transformation step is complex?
- **CORUJA:** Good possibilities. How could we test the hypothesis about the API query time being the bottleneck? (Seeking Evidence/Testing)
- ...

## 6. Integration with EGOS

- **CORUJA:** Manages agent personas and core interaction logic, selecting/applying Maiêutic style based on user profile and context.
- **User Profile:** Stores the user's preferred interaction style.
- **KARDIA/ATLAS/etc.:** Can request CORUJA to facilitate interactions using the Maiêutic style for specific tasks within their domain.

---
*This document outlines the initial concept and will be refined as implementation proceeds.*