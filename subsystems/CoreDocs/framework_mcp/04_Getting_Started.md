@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - subsystems/CoreDocs/framework_mcp/01_Philosophy_and_Principles.md
  - subsystems/CoreDocs/framework_mcp/03_MCP_Subsystem.md
  - subsystems/CoreDocs/framework_mcp/05_Core_Components.md
  - subsystems/CoreDocs/framework_mcp/06_Development_Guide.md





  - EGOS_Framework/docs/04_Getting_Started.md

# 04. Getting Started with the EGOS Framework

This guide provides the initial steps and conceptual understanding needed to start working with the EGOS Framework. As the framework evolves, this document will be updated with more concrete setup instructions and code examples.

## Prerequisites

While the EGOS Framework aims for technology agnosticism in the long term, initial development and examples will likely leverage the following (based on existing EGOS work and common AI development practices):

-   **Programming Language:** Python (v3.9+) is the primary language for initial reference implementations.
-   **Web Framework (for MCPs):** FastAPI is recommended for building MCP servers due to its performance, ease of use, and automatic data validation/documentation features.
-   **Messaging System (for MYCELIUM-MCP):** NATS.io is a strong candidate for a lightweight, high-performance messaging backbone.
-   **Containerization (Optional but Recommended):** Docker and Docker Compose for managing services and ensuring consistent environments.
-   **Version Control:** Git (repository hosting on a platform like GitHub, GitLab, or a self-hosted solution).
-   **Development Environment:** An IDE or code editor of your choice (e.g., VS Code, PyCharm).

Familiarity with these technologies will be beneficial.

## Conceptual Setup: Understanding the EGOS Way

Before diving into code, it's crucial to internalize the EGOS philosophy:

1.  **Review the MQP:** Understand the [Philosophy and Principles (`01_Philosophy_and_Principles.md`)](01_Philosophy_and_Principles.md). Every component you build should reflect these values.
2.  **Think in MCPs:** For any AI interaction or discrete service, consider if it should be exposed as a Model-Context-Prompt service. Refer to the [MCP Subsystem (`03_MCP_Subsystem.md`)](03_MCP_Subsystem.md) and the `EGOS_MCP_Standardization_Guidelines.md`.
3.  **Embrace Conscious Modularity:** Design components to be as self-contained and reusable as possible, with clear interfaces and responsibilities.
4.  **Prioritize Ethical Considerations:** Constantly ask how your work aligns with the ETHIK principles. Consult the `ETHIK-MCP` concepts for guidance on embedding ethical validation.
5.  **Document Thoroughly:** Follow KOIOS documentation standards. Good documentation is key to Systemic Cartography and collaboration.

## Initial Environment Setup (Conceptual)

As the framework is in its genesis, a central installable package is not yet available. Early adopters and contributors will typically work by:

1.  **Cloning the EGOS Workspace:** Ensuring you have the `C:\EGOS\` directory structure and its contents, including the `EGOS_Framework` directory.
2.  **Setting up a Python Virtual Environment:**
    ```bash
    python -m venv .venv
    # Activate the virtual environment
    # Windows:
    .venv\Scripts\activate
    # macOS/Linux:
    # source .venv/bin/activate
    ```
3.  **Installing Core Dependencies (Anticipated):**
    A `requirements.txt` or `pyproject.toml` will be provided in the future. Anticipated core dependencies for developing MCPs and agents might include:
    -   `fastapi`
    -   `uvicorn`
    -   `pydantic`
    -   `aiohttp` (for async HTTP requests)
    -   `nats-py` (for NATS messaging)
    -   Libraries for interacting with specific AI models (e.g., `openai`, `huggingface_hub`).

## Your First Steps: Building a Simple MCP (Conceptual Example)

Let's imagine creating a very simple "EchoMCP" that just returns what it receives. This illustrates the basic pattern.

1.  **Define the MCP Product Brief:** Following `EGOS_MCP_Standardization_Guidelines.md`, create a brief for `EchoMCP` in `C:\EGOS\docs\mcp_product_briefs\`.
2.  **Create the MCP Server Directory:** e.g., `C:\EGOS\mcp\echo_mcp\`
3.  **Implement the Server (`server.py`):**

    ```python
    # C:\EGOS\mcp\echo_mcp\server.py
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import logging

    logger = logging.getLogger("EchoMCP")
    app = FastAPI(title="EGOS Echo-MCP", version="1.0.0")

    class EchoRequest(BaseModel):
        message: str
        context: dict = {}

    class EchoResponse(BaseModel):
        echoed_message: str
        status: str

    @app.post("/invoke", response_model=EchoResponse)
    async def invoke_echo(request: EchoRequest):
        logger.info(f"Received message: {request.message} with context: {request.context}")
        # ETHIK-MCP validation would go here in a real scenario
        return EchoResponse(echoed_message=request.message, status="success")

    @app.get("/.well-known/mcp.json")
    async def get_manifest():
        return {
            "name": "EGOS Echo-MCP",
            "version": "1.0.0",
            "description": "A simple MCP that echoes the input message.",
            "capabilities": {
                "tools": True, # Indicates it provides callable functions
                "resources": False,
                "prompts": False
            },
            "endpoints": {
                "invoke": {
                    "path": "/invoke",
                    "method": "POST",
                    "request_schema": EchoRequest.schema(),
                    "response_schema": EchoResponse.schema()
                }
            }
        }

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001) # Choose an appropriate port
    ```

4.  **Register with Tool Registry:** Add `EchoMCP` to `C:\EGOS\config\tool_registry.json` so it can be discovered and potentially called by other EGOS tools or agents.

## Next Steps

-   Explore the [Core Components (`05_Core_Components.md`)](05_Core_Components.md) document to understand other key parts of the framework.
-   Review the [Development Guide (`06_Development_Guide.md`)](06_Development_Guide.md) for more in-depth information on building within EGOS.
-   Start thinking about how your own projects or ideas could be structured as MCPs or Agents within this framework.

This Getting Started guide is intentionally high-level as the framework is in its early stages. Refer to the `ROADMAP.md` for planned features and more concrete implementation details as they become available.

---
✧༺❀༻∞ EGOS Framework ∞༺❀༻✧