@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - subsystems/CoreDocs/framework_mcp/02_Architecture_Overview.md
  - subsystems/CoreDocs/framework_mcp/03_MCP_Subsystem.md
  - subsystems/CoreDocs/framework_mcp/04_Getting_Started.md
  - subsystems/CoreDocs/framework_mcp/07_Contribution_Guidelines.md





  - EGOS_Framework/docs/06_Development_Guide.md

# 06. EGOS Framework Development Guide

This guide provides developers with best practices, patterns, and conventions for building modules, agents, and tools within the EGOS Framework. It assumes familiarity with the [Architecture Overview (`02_Architecture_Overview.md`)](02_Architecture_Overview.md) and the [MCP Subsystem (`03_MCP_Subsystem.md`)](03_MCP_Subsystem.md).

## General Principles

1.  **Adhere to MQP:** All development must align with the Master Quantum Prompt principles. Regularly ask how your design choices reflect UR, CT, SP, UA, UL, RT, IE, CM, SC, and EP.
2.  **Follow Standardization Guidelines:**
    *   **MCPs:** Strictly follow the `EGOS_MCP_Standardization_Guidelines.md` for any MCP development. Create Product Briefs in `C:\EGOS\docs\mcp_product_briefs\`.
    *   **Scripts:** Adhere to rules from `script_standardization` (e.g., use `script_template_generator.py`, register in `tool_registry.json`).
    *   **Documentation (KOIOS):** All code, MCPs, agents, and modules must have comprehensive documentation following KOIOS standards. Maintain cross-references (`RULE-XREF-01`, `RULE-XREF-02`).
3.  **Security First:** Implement security best practices. Sanitize inputs, validate data, handle secrets appropriately, and consider potential vulnerabilities.
4.  **Write Testable Code:** Design components for testability. Write unit tests, integration tests, and consider end-to-end tests where applicable.
5.  **Embrace Asynchronicity:** For I/O-bound operations (network requests, file access, messaging), use asynchronous programming (e.g., `async/await` in Python) to maintain responsiveness.
6.  **Log Meaningfully:** Implement structured logging. Logs should provide clear, actionable information for debugging and monitoring.
7.  **Configuration Management:** Externalize configurations. Do not hardcode URLs, API keys, or environment-specific parameters.

## Developing Model-Context-Prompt (MCP) Servers

MCPs are the primary way to expose AI capabilities or discrete services within EGOS.

1.  **Technology Choice:** FastAPI (Python) is the recommended starting point due to its performance, Pydantic integration for data validation, and automatic OpenAPI documentation.
2.  **Standard Endpoints:**
    *   Implement `/.well-known/mcp.json` as per standardization guidelines.
    *   Implement primary action endpoint(s) (e.g., `/invoke`, `/query`, `/generate`).
    *   Consider `/status` or health check endpoints.
3.  **Data Models (Pydantic):** Define clear Pydantic models for request and response bodies. This ensures data validation and clear API contracts.
4.  **Error Handling:** Implement robust error handling. Return appropriate HTTP status codes and informative error messages.
5.  **ETHIK Integration:** For MCPs handling sensitive data or performing actions with ethical implications, consult/integrate with `ETHIK-MCP` for validation before and/or after processing.
6.  **Concurrency:** Design MCPs to handle concurrent requests efficiently, leveraging asynchronous capabilities.
7.  **Dependency Management:** Use a `requirements.txt` or `pyproject.toml` for Python dependencies.

**Example MCP Structure (FastAPI):**
Refer to the `EchoMCP` example in [Getting Started (`04_Getting_Started.md`)](04_Getting_Started.md) and the more detailed MCP examples in `AgentEGOS.md`.

## Developing EGOS Agents (Conceptual)

Agents are autonomous or semi-autonomous entities that perform tasks, interact with users, and collaborate with other agents.

1.  **Agent Archetype:** (To be defined by the framework) Expect a base class or interface that provides:
    *   Lifecycle methods (`on_start`, `on_stop`, `run_cycle`).
    *   Access to communication (MYCELIUM), memory, and tool subsystems.
2.  **Perception Loop:** How the agent gathers information from its environment (e.g., messages from MYCELIUM, sensor data, API responses).
3.  **Reasoning/Decision Engine:** The core logic of the agent. This could range from simple rule-based systems to complex LLM-driven planning.
4.  **Action Execution:** How the agent interacts with the world (e.g., calling MCPs, sending messages, manipulating data).
5.  **State Management:** How the agent maintains its internal state. This might involve in-memory state, or persistence via the Data & Knowledge Persistence Layer.
6.  **Tool Use:** Agents should leverage MCPs as tools. The framework will provide mechanisms for tool discovery and invocation.
7.  **Communication:** Agents will primarily use `MYCELIUM-MCP` to communicate with other agents and services.

## Creating Utility Modules and Services

These are non-MCP, non-Agent components that provide shared functionality.

1.  **Clear Purpose:** Define a clear, single responsibility for the module/service.
2.  **Well-Defined API:** If it's a service, expose a clear API (e.g., a Python class interface, or a simple internal HTTP API if necessary).
3.  **Reusability:** Design for use by multiple other components.
4.  **Statelessness (Preferred for Services):** Aim for stateless services where possible to simplify scaling and management.

## Working with Data and Knowledge

1.  **NEXUS-MCP:** For interactions with graph-based knowledge, use `NEXUS-MCP`.
2.  **Data Models:** Use Pydantic or similar data validation libraries for structured data.
3.  **Privacy (SP):** Always handle data in accordance with Sacred Privacy principles. Anonymize or pseudonymize when appropriate. Obtain consent.

## Version Control and Collaboration (Git)

1.  **Branching Strategy:** Follow a consistent branching strategy (e.g., GitFlow, GitHub Flow).
2.  **Commit Messages:** Write clear, concise, and standardized commit messages (refer to EGOS standards if defined, otherwise adopt a common convention like Conventional Commits).
3.  **Pull Requests/Merge Requests:** Use PRs/MRs for code review. Ensure changes are reviewed before merging.
4.  **Issue Tracking:** Use an issue tracker (e.g., GitHub Issues, Jira) to manage tasks, bugs, and features.

## Testing Strategies

-   **Unit Tests:** Test individual functions and classes in isolation.
-   **Integration Tests:** Test the interaction between components (e.g., an agent calling an MCP).
-   **MCP Contract Tests:** Verify that MCPs adhere to their defined request/response schemas and behaviors.
-   **Ethical Tests (Future):** Develop scenarios to test adherence to ETHIK principles.

This guide provides a starting point. As the EGOS Framework matures, more specific patterns, libraries, and SDKs will be developed to further streamline the development process.

Next, refer to the [Contribution Guidelines (`07_Contribution_Guidelines.md`)](07_Contribution_Guidelines.md) if you plan to contribute to the framework itself.

---
✧༺❀༻∞ EGOS Framework ∞༺❀༻✧