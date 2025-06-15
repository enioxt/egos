@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - ATRIAN/docs/case_studies/top_incidents.md
  - CONTRIBUTING.md
  - LICENSE
  - docs/API_REFERENCE.md
  - docs/BEGINNERS_GUIDE.md
  - docs/CORE_CONCEPTS.md
  - docs/examples





# ðŸŒŒ EGOS - Ethical Governance Operating System

> "Building the infrastructure for transparent, ethical AI governance with blockchain-backed validation"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/enioxt/EGOS)
[![Ethical Framework: ETHIK](https://img.shields.io/badge/Ethical_Framework-ETHIK-purple.svg)](docs/ETHIK_FRAMEWORK.md)
[![GitHub Stars](https://img.shields.io/github/stars/enioxt/EGOS?style=social)](https://github.com/enioxt/EGOS)

## ðŸ” What is EGOS?

**EGOS** is an integrated ecosystem for ethical AI governance that combines:

- **ðŸ§  Ethics as a Service (EaaS)**: API-driven ethical evaluations through ATRiAN
- **â›“ï¸ Decentralized Validation**: Blockchain-backed ethical verification via DEV
- **ðŸ› ï¸ Modular Components**: Purpose-built subsystems working in concert
- **ðŸ“Š Transparency Tools**: Visual dashboards for oversight and accountability

EGOS stands apart from other AI ethics platforms by implementing a practical, actionable governance system rather than just theoretical guidelines.

## ðŸ’Ž Core Features

| Feature | Description |
|---------|-------------|
| **ATRiAN Module** | The system's ethical core, providing intuitive guidance and context management |
| **ETHIK Framework** | Comprehensive methodology for evaluating AI systems against ethical principles |
| **TaskMaster AI** | Structured task management system aligned with MQP principles |
| **Distributed Ethical Validator (DEV)** | Decentralized consensus mechanism for ethical validation |
| **Blockchain Integration** | $ETHIK token across multiple chains enables transparent governance |
| **ATRiAN: Proactive Ethical Incident Avoidance** | ATRiAN doesn't just react to ethical breaches; it proactively identifies potential incidents and provides mechanisms for their avoidance. This unique capability is crucial for building trustworthy AI systems. [Learn more about our methodology and proof of concept](file:///C:/EGOS/ATRIAN/docs/INCIDENT_AVOIDANCE_PROOF.md). |
| **Dashboard System** | Visual monitoring of ethical metrics and system performance |
| **Relation Extraction Service** | FastAPI + spaCy microservice that surfaces entity relationships for dashboard graph view (v0.2) |
| **Standardized Workflows** | Pre-built processes for research, code refinement, and documentation |
| **PromptVault** | System for capturing, distilling, validating, and reusing high-quality prompts. |
| **AutoCrossRef System** | Automatically creates and maintains a knowledge graph of your codebase and documentation by injecting reference links. See the [full documentation](subsystems/AutoCrossRef/README.md) for details.
| **Dataset Inventory** | Comprehensive catalogue of all ATRiAN datasets and snapshots. See [`ATRIAN/docs/DATA_INVENTORY.md`](file:///c:/EGOS/ATRIAN/docs/DATA_INVENTORY.md) | |
| **MSAK v4.2** | Multiverse Strategic Analysis Kernel; a comprehensive prompt framework for advanced AI-augmented transdisciplinary strategic analysis. See PDD: [`pdd_egos_ultra_v4.2_msak.yaml`](file:///c:/EGOS/docs/prompts/pdds/pdd_egos_ultra_v4.2_msak.yaml) |
| **KOIOS PDD System** | Standardized Prompt Design Document (PDD) creation, validation, and management |
| **Financial ROI Analytics** | Quantifies risk-mitigation savings with real incident cost data and ATRiAN score-driven ROI calculations |

## 🔗 Cross-Reference Architecture

EGOS employs **AutoCrossRef** to maintain a living knowledge graph of the entire repository.

* **Level-0 (Universal)** – A mandatory 6-item block injected at the very top of *every* file:

  ```text
  @references:
  - .windsurfrules
  - CODE_OF_CONDUCT.md
  - MQP.md
  - ROADMAP.md
  - CROSSREF_STANDARD.md
  ```

  This guarantees that all files share a common root set of essential project artefacts.

* **Level-1 (Contextual)** – Auto-generated references to "immediate neighbours" (markdown links, imports, same-feature docs).  Built by `scripts/build_level1_xrefs.py`, enforced via a git *pre-commit* hook and the `/cross_reference_maintenance` Windsurf workflow (nightly CI).

* **Future Levels** – Planned expansion to parse code imports (Python, JS/TS) and semantic similarity to surface latent links.

This multi-level approach ensures discoverability, prevents documentation drift, and feeds richer context to AI assistants like Cascade.

---

## 🚀 Key Capabilities & Advanced Kernels

EGOS leverages sophisticated prompt architectures and kernels to drive advanced analytical and operational capabilities. These are designed to be used with capable Large Language Models.

*   **Multiverse Strategic Analysis Kernel (MSAK v4.2):**
    *   **Description:** A comprehensive 12-section prompt framework for advanced AI-augmented transdisciplinary strategic analysis. Guides an LLM, acting as a virtual strategic committee, through a deep-dive analysis of complex challenges.
    *   **Kernel:** [`egos_ultra_v4.2_msak.md`](file:///c:/EGOS/docs/prompt_kernels/egos_ultra_v4.2_msak.md)
    *   **PDD:** [`pdd_egos_ultra_v4.2_msak.yaml`](file:///c:/EGOS/docs/prompts/pdds/pdd_egos_ultra_v4.2_msak.yaml)
    *   **Usage Workflow:** [`/initiate_msak_analysis`](file:///c:/EGOS/.windsurf/workflows/initiate_msak_analysis.md)

*(This section will be expanded as more advanced kernels are developed.)*

## ðŸ”® Why Choose EGOS?

Unlike theoretical ethics frameworks or general-purpose AI platforms, EGOS provides:

- **Practical Implementation**: Ready-to-use tools and APIs for embedding ethics in AI systems
- **Decentralized Trust**: Not reliant on a single authority for ethical validation
- **Blockchain Transparency**: Every ethical evaluation is transparent and immutable
- **Modular Integration**: Components can be adopted individually based on your needs
- **Living Documentation**: Continuously evolving best practices and standards

## ðŸš€ Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Quick Installation
```bash
# Clone the repository
git clone https://github.com/enioxt/EGOS

# Navigate to project directory
cd EGOS

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run dashboard/streamlit_app.py
```

## ðŸ’° Blockchain Integration

EGOS integrates with multiple blockchains through the $ETHIK token:

* **HyperLiquid**: <a href="https://app.hyperliquid.xyz/explorer/address/0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4" target="_blank">`0xEFC3c015E0CD02246e6b6CD5faA89e96a71Ec1E4`</a>
* **Solana**: <a href="https://gmgn.ai/sol/token/DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump" target="_blank">`DsLmsjwXschqEe5EnHFvv1oi5BNGoQin6VDN81Ufpump`</a>
* **Base**: <a href="https://gmgn.ai/base/token/0x633b346b85c4877ace4d47f7aa72c2a092136cb5" target="_blank">`0x633b346b85c4877ace4d47f7aa72c2a092136cb5`</a>

## ðŸ”„ Core Workflows

EGOS leverages a growing suite of standardized operational procedures defined in the .windsurf/workflows/ directory. These workflows streamline common tasks, ensure consistency, and promote best practices across the ecosystem. Key workflows include:

*   **/project_handover_procedure**: Ensures smooth transitions of projects, tasks, or roles between human and AI agents, maintaining context and continuity. ([View Workflow](file:///C:/EGOS/.windsurf/workflows/project_handover_procedure.md))
*   **/distill_and_vault_prompt**: Captures, refines, and archives high-quality LLM prompts in the EGOS PromptVault, building a reusable knowledge base for effective AI interaction. ([View Workflow](file:///C:/EGOS/.windsurf/workflows/distill_and_vault_prompt.md))
*   **/ai_assisted_research_and_synthesis**: Systematically gathers, processes, and synthesizes information for research tasks, enhancing efficiency and depth of insights.
*   **/iterative_code_refinement_cycle**: Progressively improves code quality, functionality, and performance using AI-assisted feedback loops and automated checks.
*   **/dynamic_documentation_update_from_code_changes**: Automates the synchronization of documentation with code modifications, ensuring accuracy and currency.

These, along with other specialized workflows, are integral to EGOS's operational efficiency and commitment to methodical precision.

    A key component of this operational framework is the **EGOS PromptVault** and its associated workflow, `/distill_and_vault_prompt`. This system is crucial for:
    *   **Capturing Excellence:** Identifying and saving highly effective LLM interactions.
    *   **Reverse Prompt Engineering:** Distilling these interactions into reusable "master prompts" that ensure consistent, high-quality outputs.
    *   **Knowledge Management:** Building a searchable, versioned library of best-practice prompts, reducing redundant effort and accelerating learning across the EGOS ecosystem.
    *   **AI-Assisted Distillation:** Leveraging AI (including Cascade itself) to analyze interactions and suggest or refine master prompts, as demonstrated by the vaulting of the "Master Prompt for Prompt Distillation."
    This structured approach to prompt management is vital for maximizing the efficiency and effectiveness of all AI-assisted tasks within EGOS.

## ðŸ“œ KOIOS: Prompt Design & Validation Subsystem

The **KOIOS subsystem** is central to EGOS's commitment to high-quality, consistent, and reusable AI prompts. It provides a comprehensive framework for Prompt Design Documents (PDDs), ensuring that all prompts used within the EGOS ecosystem are well-defined, validated, and managed.

**Key Capabilities of KOIOS:**

*   **Hierarchical PDD Schema (`pdd_schema.py`):**
    *   A robust Pydantic-based schema defines the structure for PDDs, ensuring all necessary metadata and prompt components are present.
    *   Supports a base schema for common fields and specialized schemas (e.g., `SpecializedHandlerPddSchema`) for advanced prompt types, selected via a `pdd_type` field in the PDD YAML.
    *   Enforces strict validation (`extra = 'forbid'`) to maintain schema integrity.
*   **Automated Validation (`validate_pdd.py`):**
    *   A dedicated script validates PDD YAML files against the defined schemas, providing clear success/failure feedback and detailed error reporting. This ensures PDDs are syntactically correct and complete before use.
*   **Standardized Prompt Engineering:**
    *   Promotes a consistent approach to designing and documenting prompts, enhancing clarity, reusability, and maintainability.
    *   Facilitates the creation of complex prompts by providing a structured template.
*   **Foundation for Advanced AI Operations:**
    *   Validated PDDs serve as reliable inputs for automated prompt execution frameworks, AI model interactions, and integration with other EGOS subsystems like ATRiAN (for ethical reviews) and Mycelium (for knowledge graphing).
*   **Workflow Integration:**
    *   PDD validation is integrated into core EGOS workflows, such as the `/distill_and_vault_prompt` process, ensuring prompts are associated with valid PDDs before being stored in the PromptVault.

The KOIOS subsystem, through its PDD standard and validation tools, underpins the quality and reliability of all prompt-driven operations within EGOS, aligning with the MQP principles of clarity, context, and precision in AI interactions. Refer to the **[KOIOS Prompt Design Document (PDD) Standard](file:///C:/EGOS/docs/standards/KOIOS_PDD_Standard.md)** for detailed specifications.

## 📚 PromptVault: Master Prompt Library

The **PromptVault** (`/PromptVault`) is EGOS's curated repository of high-quality, production-ready prompts.

* **Distillation & Vaulting:** Prompts are distilled from effective LLM interactions via the [`/distill_and_vault_prompt`](file:///c:/EGOS/.windsurf/workflows/distill_and_vault_prompt.md) workflow and automatically stored in JSON format.
* **Versioning & Searchability:** Each entry is timestamped, schema-validated, and searchable—building a living library of best-practice prompts.
* **Reverse Prompt Engineering:** Facilitates analysis and refinement of master prompts to continuously improve AI output quality.

Current vaulted prompts include:

* `2025-06-09_103100_explicacao_python_iniciante.json`
* `ultimate_multidisciplinary_strategic_analysis_v3.json`

Refer to PromptVault when designing new kernels or tasks to avoid duplicating work and ensure consistency across the ecosystem.

## 🔗 AutoCrossRef: Your Project's Living Knowledge Graph

The **AutoCrossRef** system is a powerful internal tool that acts as the connective tissue for the entire EGOS project. It automatically scans every file, understands its location, and injects a self-referencing link. This simple action is the foundation for a powerful, interconnected knowledge management system.

### How It Works & Technologies Used

-   **Core Technology**: A robust Python script (`subsystems/AutoCrossRef/src/ref_injector.py`) handles all the logic. It's built to be lightweight and has no external dependencies beyond standard Python libraries.
-   **Process**:
    1.  A master script (`scripts/regen_references.py`) is run.
    2.  It traverses all specified project directories (like `docs/` and `subsystems/`).
    3.  For each file, it creates a secure, timestamped backup.
    4.  It intelligently finds the correct insertion point (e.g., after shebangs/encoding lines in Python files).
    5.  It injects a commented-out `@references` block containing the file's own path.
-   **CI/CD Integration**: The system is backed by a GitHub Actions workflow (`.github/workflows/autocrossref_ci.yml`) that runs comprehensive unit and integration tests on every change, guaranteeing its stability.

### Practical Benefits & Real-World Utility

-   **Instant Context & Impact Analysis**: By creating a machine-readable map of the project, we can instantly answer questions like, "If I change this file, what other parts of the system might be affected?" This dramatically reduces development risks.
-   **Accelerated Onboarding**: New developers can understand the relationships between different parts of the code and documentation much faster, navigating the project as if it were a wiki.
-   **Living Documentation**: It prevents documentation from becoming stale and isolated. Every document is an active node in the project's knowledge graph.
-   **Foundation for Advanced Tooling**: This reference system is the prerequisite for future tools, such as automated diagram generation, dependency analysis dashboards, and advanced semantic code search.

The AutoCrossRef system transforms a static collection of files into a dynamic, interconnected, and intelligent knowledge base, embodying the EGOS principle of systemic coherence. The newly implemented hierarchical reference standard enforcement ensures consistent cross-referencing across all project files, with support for different operational modes (diagnose, fix-core, full) and detailed compliance reporting.

## ðŸ“š Documentation

| Resource | Description |
|----------|-------------|
| [**ðŸ“˜ Core Concepts**](docs/CORE_CONCEPTS.md) | Foundational principles and architecture |
| [**ðŸš¶ Beginner's Guide**](docs/BEGINNERS_GUIDE.md) | Step-by-step introduction for new users |
| [**ðŸ’» API Reference**](docs/API_REFERENCE.md) | Complete technical documentation |
| [**ðŸ§© Integration Examples**](docs/examples/) | Code samples for common use cases |
| [**ðŸ”­ Roadmap**](ROADMAP.md) | Future development plans and priorities |
| [**🛠️ Top Incidents Case Studies**](ATRIAN/docs/case_studies/top_incidents.md) | Diagnostics of five high-severity AI incidents & ATRiAN mitigation patterns |

## ðŸŒŸ Use Cases

- **Healthcare AI**: Ensure patient data ethics and unbiased diagnostic algorithms
- **Financial Services**: Implement fair lending practices and transparent credit scoring
- **Content Moderation**: Balance freedom of expression with harm prevention
- **Public Sector AI**: Accountable decision-making in government applications
- **Research Oversight**: Ethical guardrails for advanced AI research

## ðŸ‘¥ Community & Contribution

We welcome contributors of all skill levels! Check out our [**CONTRIBUTING.md**](CONTRIBUTING.md) guide to get started.

- **Good First Issues**: Look for issues tagged with `good-first-issue` for newcomers
- **Feature Requests**: Share ideas in [GitHub Discussions](https://github.com/enioxt/EGOS/discussions)
- **Bug Reports**: Submit via [GitHub Issues](https://github.com/enioxt/EGOS/issues)
- **Documentation**: Help improve our guides and references

## ðŸ“ž Contact

- **Creator**: Enio Rocha
- **Email**: <eniodind@protonmail.com>
- **Telegram**: <https://t.me/ethikin>

## ðŸ“„ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">âœ§à¼ºâ€à¼»âˆž EGOS âˆžà¼ºâ€à¼»âœ§</p>