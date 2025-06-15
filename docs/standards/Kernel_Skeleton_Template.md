@references:
  - docs/standards/Kernel_Skeleton_Template.md

# EGOS Prompt Kernel Skeleton Template v1.0

**Last Updated:** {{ CURRENT_DATE_ISO }}
**Status:** Active

## 1. Introduction & Purpose

This document provides a standardized skeleton template for creating new prompt kernels within the EGOS (Ethical Governance Operating System) framework. Its purpose is to ensure consistency, clarity, comprehensiveness, and effectiveness across all EGOS prompt kernels, facilitating their development, understanding, validation, and use.

This template is derived from the analysis of advanced kernels like the Multiverse Strategic Analysis Kernel (MSAK v4.2) and is designed to be scalable, adaptable for both simple and complex prompts. Adherence to this template promotes modularity and aligns with KOIOS PDD (Prompt Design Document) standards.

## 2. When to Use This Template

Use this template when designing a new, reusable prompt kernel intended for integration into the EGOS system, particularly if it:

*   Involves multiple analytical steps or sections.
*   Requires the LLM to adopt a specific persona or set of personas.
*   Has a clearly defined input and a structured output format.
*   Is intended to be documented with a KOIOS PDD.
*   Aims for high reliability and reusability.

For very simple, single-instruction prompts, a less formal structure might suffice, but creating a PDD is still highly recommended.

## 3. Kernel Skeleton Structure

A prompt kernel based on this template should ideally include the following sections. Sections marked with `(Optional)` can be omitted if not relevant to the specific kernel's complexity or purpose.

```markdown
# [KERNEL NAME] v[Version] – [Descriptive Title]

## I. META-PURPOSE & CORE DIRECTIVE

**Objective:** [Clearly state the primary goal of the kernel. What problem does it solve or what output does it aim to produce? Be specific and concise.]

**Core Directive:** [Instruct the LLM on its fundamental mission for this task. This is a high-level instruction setting the overall tone and expectation. If the kernel uses a primary overarching persona, define it here.]

## II. PERSONA(S) (Optional but Recommended for Complex Kernels)

[This section defines the role(s) the LLM (or parts of the LLM's process) will embody. If using multiple personas, list them and their specific responsibilities or areas of focus within the kernel's execution.]

**Example for a single overarching persona (if not fully defined in Core Directive):
**Persona:** You are [Persona Name], a [Role Description] specializing in [Area of Expertise]. Your mandate is to [Specific Mandate related to the kernel's objective].

**Example for multiple personas (like MSAK):
**This kernel is executed by the [Collective Persona Name], composed of:
1.  **[Persona 1 Name] ([Abbreviation1]):** [Brief description of expertise and focus. Indicate which analytical sections they primarily contribute to.]
2.  **[Persona 2 Name] ([Abbreviation2]):** [Brief description of expertise and focus. Indicate which analytical sections they primarily contribute to.]
3.  ...and so on.

## III. CORE EXECUTION INSTRUCTIONS & METHODOLOGY

[This section provides overarching rules, methodologies, constraints, and quality standards that apply throughout the kernel's execution.]

*   **Primary Input:** [Describe the main input the user will provide to the kernel. E.g., "User-defined strategic challenge," "A block of text for summarization," "A description of an AI system for ethical review."]
*   **Key Methodologies/Approaches:** [List any specific analytical methods, frameworks, or thinking processes the LLM should employ. E.g., "Systems Thinking," "Root Cause Analysis," "Red Teaming," "ETHIK Framework principles."]
*   **Ethical Guardrails:** [Specify any ethical principles or considerations the LLM must adhere to. E.g., "Ensure objectivity and impartiality," "Avoid generating harmful or biased content," "Prioritize user privacy and data protection according to EGOS policies."]
*   **Output Format & Structure:** [Define the expected structure and format of the final output. E.g., "Markdown format," "A JSON object with specific keys," "A report with a clear Table of Contents, Executive Summary, and detailed sections as outlined below."]
*   **Tone & Style:** [Specify the desired tone and style of the output. E.g., "Formal and analytical," "Clear and concise for a general audience," "Action-oriented and prescriptive."]
*   **Constraints & Limitations:** [Mention any known limitations or things the LLM should avoid. E.g., "Do not provide financial advice," "Base analysis only on provided information unless external research is explicitly permitted."]
*   **Self-Correction/Critique:** [Encourage the LLM to review and critique its own work before finalizing the output. E.g., "Critically evaluate your findings for completeness, coherence, and relevance to the core objective."]

## IV. INPUT PARAMETERS / USER-PROVIDED CONTEXT (If applicable)

[If the kernel requires specific parameters or structured context from the user beyond the 'Primary Input', define them here. This helps the user prepare the necessary information.]

*   **[Parameter 1 Name]:** [Description of the parameter and its purpose. Specify format if necessary.]
*   **[Parameter 2 Name]:** [Description of the parameter and its purpose. Specify format if necessary.]
*   **Example User Input Block:**
    ```
    Strategic Challenge: [User's detailed challenge description]
    Time Horizon: [e.g., 5 years]
    Key Stakeholders: [e.g., Customers, Employees, Investors]
    ```

## V. ANALYTICAL SECTIONS / PROCESSING STEPS

[This is the core of the kernel, breaking down the task into manageable, sequential, or parallel analytical sections or processing steps. Each section should have a clear objective. For complex kernels with multiple personas, assign lead personas to each section.]

### SECTION 1: [Name of Section 1]
*   **Objective:** [Specific goal for this section.]
*   **Lead Persona(s) (If applicable):** [Persona(s) primarily responsible for this section.]
*   **Key Questions to Address / Tasks to Perform:**
    1.  [Question/Task 1]
    2.  [Question/Task 2]
    3.  ...
*   **Expected Deliverables for this Section:** [Specific outputs or findings for this section.]

### SECTION 2: [Name of Section 2]
*   **Objective:** [...]
*   **Lead Persona(s) (If applicable):** [...]
*   **Key Questions to Address / Tasks to Perform:**
    1.  [...]
*   **Expected Deliverables for this Section:** [...]

(...Continue for all analytical sections...)

## VI. COMPREHENSIVE SYNTHESIS & FINAL OUTPUT GENERATION

[This section instructs the LLM on how to bring together the findings from all previous analytical sections into a coherent and unified final output, as defined in 'Output Format & Structure'.]

*   **Synthesis Objective:** To integrate all preceding analyses into a holistic, actionable, and insightful final response that directly addresses the kernel's Meta-Purpose.
*   **Key Synthesis Steps:**
    1.  Review findings from all analytical sections.
    2.  Identify key themes, interconnections, contradictions, and emergent insights.
    3.  Structure the final output according to the specified format (e.g., generate Executive Summary, Table of Contents, then detailed sections).
    4.  Ensure clarity, coherence, and consistency throughout the final output.
*   **Final Review Directive:** Before concluding, perform a final self-critique to ensure all aspects of the Core Directive and Meta-Purpose have been met.

## VII. (Optional) GLOSSARY / KEY DEFINITIONS

[If the kernel uses specialized terminology or acronyms, define them here for clarity.]

*   **[Term 1]:** [Definition]
*   **[Acronym 1]:** [Full Form]

## VIII. (Optional) REFERENCES / CITATIONS

[If the kernel is expected to cite sources or refer to specific documents (beyond user-provided input), list them here or instruct on how citations should be handled.]

---

## 4. Adapting the Template

*   **For Simpler Kernels:** Many sections can be significantly condensed or merged. For instance, a simple summarization kernel might only have a Meta-Purpose, Core Execution Instructions (focusing on input/output), and a single 'Processing Step' for summarization.
*   **Persona Usage:** Personas are most useful for complex tasks requiring diverse perspectives or specialized knowledge. For simpler tasks, a single, well-defined instruction to the LLM may suffice.
*   **Section Granularity:** The number and detail of 'Analytical Sections' should match the complexity of the task. Too many trivial sections can be counterproductive.

## 5. Relationship to KOIOS PDD

This Kernel Skeleton Template is designed to work in conjunction with the [KOIOS Prompt Design Document (PDD) Standard](file:///C:/EGOS/docs/standards/KOIOS_PDD_Standard.md). The PDD provides the metadata, context, and formal description of the kernel, while the kernel file itself (created using this template) contains the actual prompt text given to the LLM.

Key fields in the PDD (like `prompt_components`, `role_definition`, `input_parameters`, `output_structure`) will directly map to or be derived from the content structured by this template.

## 6. Versioning

Kernels created using this template should be versioned (e.g., `my_kernel_v1.0.md`, `my_kernel_v1.1.md`). Significant changes to structure or core logic warrant a new version.

```