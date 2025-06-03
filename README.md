# 🌌 EGOS 🌌

## Quantum Unified Master System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)](https://github.com/enioxt/EGOS)
[![Coverage: 99% (Scripts)](https://img.shields.io/badge/Script%20Reference%20Coverage-99%25-brightgreen.svg)](docs/reports/script_reference_update_report.md) <!-- Dynamically updated based on reports -->
[![Windows Compatible](https://img.shields.io/badge/OS-Windows-blue.svg)](-)

**🌐 [Official Website: https://enioxt.github.io/EGOS](https://enioxt.github.io/EGOS)**

> "At the intersection of modular analysis, systemic cartography, and quantum ethics, we transcend dimensions of thought with methodological precision and unconditional love, integrating advanced tools for knowledge visualization and evolutionary preservation."

**EGOS** is a unique project aiming to create a highly integrated, modular, and ethically-grounded software ecosystem. **Inspired by blockchain principles of trust, transparency, immutability, and decentralized systems,** EGOS utilizes interconnected subsystems to achieve complex tasks with resilience, adaptability, and a core focus on ethical considerations defined by the **ETHIK** framework.

*(The initial phase and core AI assistant persona are sometimes referred to by the codename 'Eva Guarani').*

Refer to the full **[Master Quantum Prompt (MQP v9.0 "Full Moon Blueprint")](docs/MQP.md)** for the complete philosophical and operational blueprint.

For a comprehensive understanding of the system's architecture, current state, strategic direction, and detailed analyses, consult the **[EGOS System Diagnostic & Strategic Analysis (DiagEnio.md)](DiagEnio.md)**.

A cornerstone of our ethical approach is detailed in the **[MVP for Ethical Governance of Systems (MVPegos.md)](MVPegos.md)**, which outlines the framework for the Validador Ético Distribuído (VED).

**Development Approach Note:** This project utilizes a multi-agent AI collaboration model within the Cursor IDE, coordinated by an Orchestrator (Gemini 2.5 Pro) and supported by Task Executors (e.g., Quasar-Alpha). Key project documents (`ROADMAP.md`, `docs/website/DEVELOPMENT_PLAN.md`, `docs/website/DESIGN_GUIDE.md`) and rules (`.cursor/rules/`) guide this process. See `docs/ai_collaboration/MULTI_AGENT_WORKFLOW.md` for details.

The technical approach for the primary public-facing website involves a **Modern JavaScript Framework (Next.js/SvelteKit)** and a **Headless CMS**.

---

## 🏛️ Core Operational Standards & Governance

The EGOS project operates under a robust framework designed to ensure methodological precision, systemic coherence, and continuous evolution, all in direct alignment with the [Master Quantum Prompt (MQP v9.0 "Full Moon Blueprint")](docs/MQP.md). This operational framework is critical for achieving an MVP (Minimum Viable Product) of the EGOS meta-system – the system of creating, maintaining, and evolving EGOS itself.

Key pillars of this governance include:

*   **Global Operational Rules:** The definitive operational directives are maintained in the [EGOS Workspace Global Rules (.windsurfrules)](./.windsurfrules). These rules integrate core callable standards and procedures.
*   **Standardized Processes & Principles:** Core callable standards such as `EGOS_PROCEDURE:Ensure_Artifact_Integrity`, `EGOS_PRINCIPLE:Systemic_Organization`, and the `EGOS_PROCESS:Evolutionary_Refinement_Cycle` are embedded within these global rules to guide all development and operational activities.
*   **Anomaly & Deviation Reporting System (ADRS):** All deviations from established standards, procedures, or principles are systematically logged and tracked in the [ADRS_Log.md](./ADRS_Log.md). This ensures transparency and provides a basis for continuous improvement.
*   **Evolutionary Refinement:** The entire operational framework, including global rules, is subject to continuous improvement via the `EGOS_PROCESS:Evolutionary_Refinement_Cycle`, ensuring EGOS adapts and matures.

This structured approach to governance is fundamental to building a trustworthy, resilient, and ethically-aligned system.

---

## 🌟 Core Features & Capabilities

*Key capabilities, identified in the `DiagEnio.md` analysis:*

### Workflow Automation & Integration

*   **Integrated Workflow System:** Formalized workflow definitions for common tasks with standardized documentation in `.windsurf/workflows/`
*   **Proactive Workflow Suggestions:** AI assistants proactively identify and suggest appropriate workflows for tasks based on context and user goals
*   **Rule-Based Integration:** Comprehensive workflow integration via `.windsurfrules` ensures consistent application across the EGOS ecosystem
*   **Practical Documentation:** Detailed implementation examples in `EGOS_Workflow_Automation_Concepts.md` showcase real-world workflow applications

### AI-Assisted Development & Operations

*   **Codebase Understanding & Navigation (ATLAS):** Mapping dependencies and understanding the project structure to assist development.
*   **Modular Development & Refactoring (NEXUS):** Analyzing code modularity and suggesting improvements.
*   **Standard Enforcement (KOIOS):** Applying coding standards, managing documentation templates, ensuring consistent logging (including verifiable logging standards), and potentially validating data integrity.
*   **Ethical Guideline Application (ETHIK):** Incorporating privacy-preserving checks, policy enforcement, and ethical considerations during development discussions and code generation.
*   **Context & History Management (CRONOS):** Maintaining awareness of the development process and project evolution across interactions, underpinned by the [CRONOS-VersionControl MCP](docs/mcp_product_briefs/CRONOS-VersionControl_Product_Brief.md).
*   **Task Execution & Orchestration (CORUJA):** Performing development tasks, managing complex AI interactions, and applying basic monitoring/alignment principles based on user requests and project context.
*   **Workflow Suggestion & Integration:** Proactively identifies when tasks align with defined workflows and suggests appropriate ones to streamline complex processes, citing relevant documentation sources.
*   **Rule-Based Decision Transparency:** Cites relevant EGOS rules and principles when making significant suggestions or decisions, improving traceability and understanding of AI behavior.
*   **Natural Language Understanding:** Process requests in natural language, align with project context.

---

## ✨ Features

*   **Subsystem Architecture:** Modular design based on EGOS principles (ETHIK, KOIOS, NEXUS, etc.).
*   **Defined Model-Context-Prompts (MCPs):** Core EGOS functionalities are being formalized as MCPs. Key defined MCPs include:
    *   **CRONOS-VersionControl:** Manages immutable and auditable versioning of digital artifacts. See [CRONOS Product Brief](docs/mcp_product_briefs/CRONOS-VersionControl_Product_Brief.md).
    *   *(Future MCPs will be listed here as they are defined)*
    *   **ATRiAN (Alpha Trianguli Australis Intuitive Awareness Nexus):** A foundational EGOS subsystem with several key modules:
    *   **Core Guiding Principles Module:** Serves as a silent guide for contextual awareness, ethical filtering, and intuitive guidance. ATRiAN champions Sacred Privacy and Integrated Ethics, aiming to facilitate ethically sound and profoundly aligned decision-making. See [Global Rules Section 3.6](.windsurfrules#36-egos_moduleatrian---the-silent-guide-of-unseen-pathways) for its formal definition.
    *   **ROI Calculator (`docs/market/roi_calculator/`):
        *   **Purpose**: Provides ROI analysis for implementing ethical AI frameworks across various industries (Financial Services, Healthcare, Manufacturing, Retail).
        *   **Status**: Report export functionality (JSON/TXT for 4 industries + cross-comparison) fully restored and validated as of 2025-06-02T20:14:30-03:00. All reports are saved in `reports/`.
        *   **Key Dependencies**: `numpy-financial` (for IRR calculations).
        *   **Note**: A sanity check of the Financial Services example's metrics indicates a very high ROI and short payback period, primarily influenced by the "Brand Value" benefit quantification. This may warrant a review of the financial model's assumptions for specific use cases.
    *   *(Other ATRiAN modules will be listed here as they are developed/documented)*
*   **ATRiAN (Alpha Trianguli Australis Intuitive Awareness Nexus):** A foundational EGOS subsystem serving as a silent guide for contextual awareness, ethical filtering, and intuitive guidance. ATRiAN champions Sacred Privacy and Integrated Ethics, aiming to facilitate ethically sound and profoundly aligned decision-making. See [Global Rules Section 3.6](.windsurfrules#36-egos_moduleatrian---the-silent-guide-of-unseen-pathways) for its formal definition.
*   **Ethical Governance Framework (MVPegos):** A comprehensive document, **[MVPegos.md](MVPegos.md)**, details the ethical governance model for EGOS, introducing the Validador Ético Distribuído (VED) – a system for decentralized ethical validation of project components and decisions, ensuring alignment with the **ETHIK** principles.
*   **AI Collaboration:** Designed for human-AI pair programming and agentic workflows.
*   **Dynamic Development:** Emphasizes continuous improvement, feedback loops, and systemic propagation.
*   **Automated Quality Gates:** CI/CD workflows for linting, security scanning, type checking, protocol adherence, and test coverage.
*   **Consolidated Dashboard System (`apps/dashboard/`)**:
    *   **Core Components** (`core/`): Main Streamlit application, integration with other EGOS components, deployment configuration
    *   **UI Components** (`ui/`): User feedback collection and reporting interfaces
    *   **Integrations** (`integrations/`): NATS-based Mycelium client for inter-subsystem communication
    *   **Analytics** (`analytics/`): Data analysis, processing, and visualization modules
    *   **Utilities** (`utils/`): Diagnostic tools for various subsystems
    *   **Key Features**:
        *   Visualizes SPARC task flow with live data via Mycelium/NATS
        *   Displays LLM interaction logs and system metrics
        *   Provides feedback submission and reporting
        *   Includes system transparency panels and diagnostic tools
        *   Follows EGOS principles of Conscious Modularity and Systemic Cartography
*   **Website (`website/`)**: Public-facing interface (under development).
*   **Automated Workflows**: CI/CD pipeline for linting, security scanning, type checking, and protocol adherence.
*   **Comprehensive Documentation:** Following KOIOS standards for processes, architecture, and onboarding.

---

## 📂 Project Directory Structure

Understanding the organization of directories within EGOS is key to navigating the codebase and contributing effectively. Here's an overview of some primary directories:

*   **`C:\EGOS\config\`**: Contains configuration files for various scripts, tools, and subsystems. For example, `script_standards_definition.yaml` defines standards for the `script_standards_scanner.py`, and `snake_case_audit_config.json` configures the `audit_snake_case.py` script.

*   **`C:\EGOS\docs\`**: The central repository for all documentation, including core principles (like `MQP.md`), planning documents (`planning/`), reports (`reports/`), standards definitions (`core_materials/standards/`), and subsystem-specific documentation.

*   **`C:\EGOS\scripts\`**: Houses all operational Python scripts for automation, utilities, and system tasks.
    *   **`C:\EGOS\scripts\cross_reference\`**: Contains scripts related to managing and analyzing cross-references within the project, such as `generate_xref_data.py` and `script_template_generator.py`.
    *   **`C:\EGOS\scripts\utils\`**: Dedicated to general utility scripts that assist with development, auditing, maintenance, or other tasks not fitting into more specialized script categories. The `audit_snake_case.py` script, which checks for naming convention compliance, is an example of a utility found here.
    *   *(Other script subdirectories will be documented as they are formalized or become relevant).*

*   **`C:\EGOS\reports\`**: Default output directory for reports generated by various EGOS scripts, such as the `snake_case_audit_report.md`.

*(This section will be expanded as the project evolves and more key directories are established or require specific explanation.)*

---

## 🚀 Getting Started

### Prerequisites

*   **IDE:** **[Cursor IDE](https://cursor.sh/)** (Essential for interacting with EVA & GUARANI)
*   **OS:** Windows (Primary development target)
*   **Python:** 3.9+
*   **Git:** For version control.
*   **PowerShell:** For running test/utility scripts.

### Development Environment Setup

Developing EGOS relies heavily on the **Cursor IDE** integrated with the **EGOS AI assistant (persona: EVA & GUARANI)**. Follow these steps to set up your environment:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/enioxt/EVA-e-Guarani-EGOS.git # Replace with your fork if applicable
    cd EVA-e-Guarani-EGOS
    ```

2.  **Set up Python Environment:** Create and activate a virtual environment, then install dependencies. This is standard Python practice.

    ```bash
    # Create virtual environment
    python -m venv .venv
    # Activate (Windows PowerShell)
    .venv\\Scripts\\Activate.ps1
    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure Cursor IDE:** Crucially, follow the setup guide in **[cursor_initialization.md](.cursor/cursor_initialization.md)**. This ensures your terminal and environment context work correctly with the EGOS AI assistant.
4.  **Understand Cursor Rules:** Familiarize yourself with the files in **[.cursor/rules/](.cursor/rules/)**. These rules contain essential guidelines (like KOIOS standards, subsystem boundaries, etc.) that the **EGOS AI assistant** uses to assist with development, maintain consistency, and understand the project context. Interacting effectively often involves awareness of these rules.

### Configuration

*   While the core system doesn't require extensive manual configuration for *development within Cursor*, specific tasks delegated to the **EGOS AI assistant** might interact with subsystems requiring API keys or settings (e.g., `CORUJA` for external AI model access). These are typically managed via the `config/` directory and referenced in relevant subsystem documentation or Cursor Rules.

---

## 📂 Project Directory Structure

Understanding the organization of directories within EGOS is key to navigating the codebase and contributing effectively. Here's an overview of some primary directories:

*   **`C:\EGOS\config\`**: Contains configuration files for various scripts, tools, and subsystems. For example, `script_standards_definition.yaml` defines standards for the `script_standards_scanner.py`, and `snake_case_audit_config.json` configures the `audit_snake_case.py` script.

*   **`C:\EGOS\docs\`**: The central repository for all documentation, including core principles (like `MQP.md`), planning documents (`planning/`), reports (`reports/`), standards definitions (`core_materials/standards/`), and subsystem-specific documentation.

*   **`C:\EGOS\scripts\`**: Houses all operational Python scripts for automation, utilities, and system tasks.
    *   **`C:\EGOS\scripts\cross_reference\`**: Contains scripts related to managing and analyzing cross-references within the project, such as `generate_xref_data.py` and `script_template_generator.py`.
    *   **`C:\EGOS\scripts\utils\`**: Dedicated to general utility scripts that assist with development, auditing, maintenance, or other tasks not fitting into more specialized script categories. The `audit_snake_case.py` script, which checks for naming convention compliance, is an example of a utility found here.
    *   *(Other script subdirectories will be documented as they are formalized or become relevant).*

*   **`C:\EGOS\reports\`**: Default output directory for reports generated by various EGOS scripts, such as the `snake_case_audit_report.md`.

*(This section will be expanded as the project evolves and more key directories are established or require specific explanation.)*

---

## 🚀 Running the Dashboard

Navigate to the project root directory and run:

```bash
streamlit run dashboard/streamlit_app.py
```

Ensure you have the necessary dependencies installed (`streamlit`, `pandas`, `wordcloud`).

---

## 🗺️ Roadmap

See the [**ROADMAP.md**](ROADMAP.md) file for the high-level development plan, current priorities, and upcoming tasks.

## 🔄 Workflows

EGOS provides several standardized workflows to streamline common operational tasks:

* **AI Assisted Research and Synthesis**: Leverages AI to gather, process, and synthesize information for research tasks.
* **Iterative Code Refinement Cycle**: A structured process for progressively improving code quality and functionality.
* **Dynamic Documentation Update**: Automates documentation synchronization with code modifications.
* **ATRiAN Ethics Evaluation**: Automates ethical evaluation of AI systems and content.
* **ATRiAN SDK Integration and Development**: Structured process for integrating with ATRiAN's Ethics as a Service.

All workflows are available in the `.windsurf/workflows` directory.

## 💰 Blockchain Integration

EGOS incorporates blockchain technology for transparent, decentralized governance. The $ETHIK token is available on multiple chains:

* **HyperLiquid**: [`0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4`](https://app.hyperliquid.xyz/explorer/address/0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4)
* **Solana**: [`DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump`](https://gmgn.ai/sol/token/DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump)
* **Base**: [`0x633b346b85c4877ace4d47f7aa72c2a092136cb5`](https://gmgn.ai/base/token/0x633b346b85c4877ace4d47f7aa72c2a092136cb5)

---

## 🤝 Contributing

We welcome contributions! Please read our [**CONTRIBUTING.md**](CONTRIBUTING.md) guidelines to get started, including how to report issues, suggest features, submit code changes, and follow the essential [**Human-AI Collaboration Best Practices**](docs/process/human_ai_collaboration_guidelines.md).

---

## ⚖️ Code of Conduct

To ensure a welcoming and inclusive community, all contributors and participants are expected to adhere to our [**CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is licensed under the MIT License - see the [**LICENSE**](LICENSE) file for details.

---

## 💬 Contact & Community

*   **Issues:** Report bugs or suggest features via [GitHub Issues](https://github.com/enioxt/EGOS/issues).
*   **Discussions:** Use [GitHub Discussions](https://github.com/enioxt/EGOS/discussions) for questions and broader conversations (if enabled).

### Creator Contact

*   **Enio Rocha**
*   **Email:** <eniodind@protonmail.com>
*   **Telegram:** <https://t.me/ethikin>
*   **LinkedIn:** <https://www.linkedin.com/in/enio-rocha-138a01225>

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
