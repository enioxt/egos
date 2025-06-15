@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - subsystems/CoreDocs/framework_mcp/04_Getting_Started.md





  - EGOS_Framework/docs/03_MCP_Subsystem.md

# 03. Model-Context-Prompt (MCP) Subsystem

Version: 1.0 (as per agent_egos_blueprint.md synthesis)

The Model-Context-Prompt (MCP) Subsystem is a cornerstone of the EGOS Framework. It provides a standardized, flexible, and powerful paradigm for interacting with a diverse range of Artificial Intelligence (AI) models, external services, and internal EGOS capabilities. This subsystem embodies the principles of **Conscious Modularity (CM)** and **Integrated Ethics (IE)** by design.

## Purpose and Goals

The primary goals of the MCP Subsystem are to:

1.  **Abstract Complexity:** Hide the specific details and idiosyncrasies of various AI model APIs (e.g., different LLM providers, specialized ML models).
2.  **Standardize Interaction:** Provide a consistent pattern for how agents and other EGOS components request and receive services from AI models or tools.
3.  **Manage Context Effectively:** Facilitate the gathering, structuring, and provision of relevant context to AI models to improve the quality and relevance of their outputs.
4.  **Enable Sophisticated Prompt Engineering:** Support dynamic and programmatic construction of prompts tailored to specific tasks and models.
5.  **Integrate Ethical Oversight:** Allow the `ETHIK-MCP` to validate and potentially modify requests and responses, ensuring alignment with EGOS principles.
6.  **Promote Reusability and Extensibility:** Enable the creation of a library of MCPs that can be easily reused across different applications and extended with new capabilities.

## Core Concepts

-   **MCP Server:** A dedicated service (often a FastAPI application, as seen in `agent_egos_blueprint.md` examples) that exposes one or more related AI capabilities or tool functions through a standardized interface.
-   **Model:** The underlying AI model, service, or function that the MCP server provides access to (e.g., a specific LLM, a translation API, a knowledge graph query engine).
-   **Context:** The information provided to the MCP server along with the prompt. This can include user data, conversation history, system state, relevant documents, or any other information needed by the model to perform its task effectively.
-   **Prompt:** The specific instruction or query given to the model, often constructed dynamically by the calling agent or service based on the task and context.
-   **Response:** The output from the model, processed and structured by the MCP server before being returned to the caller.

## Standard MCP Structure (Conceptual)

While implementations can vary, a typical MCP server might expose endpoints like:

-   `POST /invoke` or `POST /execute`: The primary endpoint for sending a prompt and context to the model.
-   `GET /capabilities` or `GET /.well-known/mcp.json`: An endpoint describing the MCP's functions, expected inputs, outputs, and any specific parameters (as per `EGOS_MCP_Standardization_Guidelines.md`).
-   `GET /status`: To check the health and operational status of the MCP server.

## Key Defined MCPs (from AgentEGOS.md)

The `AgentEGOS.md` document outlines several foundational MCPs. The EGOS Framework will provide guidelines and potentially reference implementations or templates for these. Each MCP serves a distinct purpose:

1.  **Oracle-MCP (Universal LLM Gateway):**
    *   **Function:** Provides a unified interface to various Large Language Models (LLMs). Manages API keys, model selection, and basic prompt formatting.
    *   **Use Cases:** Text generation, summarization, question answering, translation.

2.  **ScribeAssist-MCP (Documentation & Code Generation):**
    *   **Function:** Specializes in generating code, documentation, and other structured text formats from specifications (e.g., Markdown prompts).
    *   **Use Cases:** Scaffolding new code modules, generating API documentation, creating reports from data.

3.  **Strategos-MCP (Project Planning & Task Management):**
    *   **Function:** Assists in breaking down complex goals into actionable plans, tracking tasks, and managing project workflows.
    *   **Use Cases:** AI-assisted project planning, dynamic task adaptation, agent goal decomposition.

4.  **Hermes-MCP (Web Research & Data Collection):**
    *   **Function:** Enables agents to perform web searches, retrieve content from URLs, and extract information from web pages.
    *   **Use Cases:** Information gathering, market research, content aggregation for agents.

5.  **ETHIK-MCP (Ethical Validation & Governance):**
    *   **Function:** Provides services for validating prompts, agent actions, and model outputs against EGOS ethical guidelines (MQP). A critical component for ensuring responsible AI behavior.
    *   **Use Cases:** Pre-flight checks for agent actions, content moderation, bias detection (aspirational).

6.  **NEXUS-MCP (Knowledge Graph Integration):**
    *   **Function:** Facilitates interaction with knowledge graphs (e.g., Neo4j), allowing agents to query, update, and reason over structured knowledge.
    *   **Use Cases:** Enhancing agent understanding, providing long-term memory, complex relationship analysis.

7.  **MYCELIUM-MCP (Inter-Agent Communication System):**
    *   **Function:** Provides a robust message bus for communication between agents, MCPs, and other EGOS components. Supports publish-subscribe and request-response patterns.
    *   **Use Cases:** Agent collaboration, distributed task execution, system-wide eventing.

## MCP Development and Standardization

-   All MCPs developed for or within the EGOS Framework **MUST** adhere to the [EGOS MCP Standardization Guidelines (`../standards/EGOS_MCP_Standardization_Guidelines.md`)](file:///C:/EGOS/EGOS_Framework/docs/standards/EGOS_MCP_Standardization_Guidelines.md).
-   MCP Product Briefs, detailing the design and purpose of each MCP, **MUST** be located in `../mcp_product_briefs/` (i.e., `C:\EGOS\EGOS_Framework\docs\mcp_product_briefs\`).
-   The framework will encourage the use of common technologies (like FastAPI for Python-based MCPs) for consistency but will remain open to other implementations where justified, provided they meet the standardization guidelines.

## Interaction Flow Example

1.  An **Agent** needs to summarize a document.
2.  The Agent forms a **Context** (the document content, desired summary length) and a **Prompt** ("Summarize this document concisely.").
3.  The Agent sends this to the **Oracle-MCP**'s `/invoke` endpoint.
4.  The **Oracle-MCP** might first send the request to the **ETHIK-MCP** for a pre-validation check (e.g., ensuring the document content is appropriate).
5.  Assuming ETHIK validation passes, the **Oracle-MCP** selects an appropriate LLM, formats the full prompt, and sends it to the LLM API.
6.  The LLM returns a summary.
7.  The **Oracle-MCP** receives the summary. It might again consult the **ETHIK-MCP** for post-validation of the generated summary.
8.  The **Oracle-MCP** formats the final, validated summary and returns it as a **Response** to the Agent.

This MCP subsystem is fundamental to achieving the desired modularity, intelligence, and ethical integrity of the EGOS Framework.

Next, learn how to get started with the framework in [Getting Started (`04_Getting_Started.md`)](04_Getting_Started.md).

---
✧༺❀༻∞ EGOS Framework ∞༺❀༻✧