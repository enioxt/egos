---
title: CONTRIBUTING
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: contributing
tags: [documentation]
---
---
title: CONTRIBUTING
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

---
title: CONTRIBUTING
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

# Contributing to EGOS

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/guides/code_review.md
  - docs/process/community_engagement.md
  - docs/process/development_workflow.md
  - governance/human_ai_collaboration_guidelines.md
  - reference/ai_handover_standard.mdc
  - reference/git_workflow_standards.mdc
  - reference/templates/PDD_Template.md





  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
  - [MQP](..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
- Other:
  - [MQP](..\reference\MQP.md)
  - docs/governance/CONTRIBUTING.md




- Core Documents:
  - [MQP](..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
  - [README](../../governance/business/github_updates/README.md) - Project overview and introduction
- Community Guidelines:
  - [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) - Code of conduct
  - [docs/process/community_engagement.md](../../docs\process\community_engagement.md) - Community engagement processes
- Development Workflow:
  - [docs/process/development_workflow.md](../../docs\process\development_workflow.md) - Development workflow
  - [docs/guides/code_review.md](../../docs\guides\code_review.md) - Code review guidelines

First off, thank you for considering contributing to **EGOS**! Your involvement helps us build a more robust, ethical, and unified system.

This document provides guidelines for contributing to the project. Please read it carefully to ensure a smooth collaboration process.

**🌐 Official Website: [https://enioxt.github.io/egos](https://enioxt.github.io/egos)**

## Code of Conduct

By participating in this project, you agree to abide by our [**Code of Conduct**](CODE_OF_CONDUCT.md). Please read it to understand the standards of behavior we expect within our community.

## How Can I Contribute?

There are many ways to contribute:

- Reporting Bugs: If you find a bug, please create a detailed issue in our GitHub repository.
- Suggesting Enhancements: Have an idea for a new feature or an improvement? Open an issue to discuss it.
- Writing Code: Help implement new features, fix bugs, or improve existing code.
- Improving Documentation: Enhance READMEs, add docstrings, write tutorials, or correct typos.
- Submitting Feedback: Share your experience using EGOS and suggest improvements.

feat/roadmap-updates

## Using the Website Roadmap

The primary way to discover, understand, and contribute to EGOS tasks is through the interactive roadmap on the [official website](https://enioxt.github.io/egos) (or your local deployment). On the roadmap page, you can:

- Browse all current, planned, and completed tasks.
- Click on any task to open a detailed modal with:
  - Contribution instructions
  - Acceptance criteria
  - Links to the relevant GitHub code, issues, or discussions
- Follow the instructions in each modal to start contributing.

This modular approach ensures clarity, accessibility, and alignment with EGOS standards. Always refer to the roadmap first before opening issues or submitting pull requests.

main

## Reporting Bugs

Before creating a bug report, please check existing issues to see if someone has already reported it. If not, create a new issue and include:

- A clear and descriptive title.
- A detailed description of the steps to reproduce the bug.
- What you expected to happen.
- What actually happened (include error messages and stack traces if applicable).
- Your environment details (OS, Python version, etc.).

## Suggesting Enhancements

Use GitHub Issues to suggest enhancements. Provide:

- A clear title summarizing the suggestion.
- A detailed description of the proposed feature or improvement.
- The motivation behind the suggestion (what problem does it solve?).
- Any potential implementation ideas (optional).

## Development Workflow

1. **Fork the Repository:** Create your own copy of the EGOS repository on GitHub.
2. **Clone Your Fork:**

    ```bash
    git clone <your-fork-url>
    cd Eva-Guarani-EGOS
    ```

feat/roadmap-updates
3.  **Set Up Environment:** Follow the [Installation steps in the main project README.md](../../README.md#installation). Ensure all dependencies are correctly installed.

3. **Set Up Environment:** Follow the [Installation steps in the README](README.md#installation).
main
4. **Create a Branch:** Create a new branch for your feature or bugfix:

    ```bash
    git checkout -b <branch-name>
    # Examples: feature/add-atlas-mermaid-export, fix/koios-logger-bug
    ```

5. **Make Changes:** Implement your code or documentation changes.
feat/roadmap-updates
6. **Follow Standards:** Adhere to the **KOIOS** standards for code style, naming, logging, error handling, and documentation. Refer to the primary [README](../../governance/business/github_updates/README.md) and specific rules in `.cursor/rules/` or `docs/core_materials/standards/`. **When creating or modifying core AI prompts, document them using the [PDD_Template](../../reference/templates/PDD_Template.md).**

6. **Follow Standards:** Adhere to the KOIOS standards for code style, naming, logging, and error handling. Refer to relevant `.mdc` rules or documentation in `docs/STANDARDS_*.md`. **When creating or modifying core AI prompts, document them using the [PDD_Template](../../reference/templates/PDD_Template.md).**
main
7. **Write/Update Tests:** Ensure your changes are covered by unit tests. Aim to maintain or increase test coverage. Run tests using the provided PowerShell scripts (e.g., `.\test_<subsystem>.ps1 -Coverage`).
8. **Commit Changes:** Use clear and descriptive commit messages following the Conventional Commits format (see `commit_messages.mdc` rule). Reference related issues (e.g., `feat: Add Mermaid export to ATLASCore (closes #42)`).

    ```bash
    git add .
    git commit -m "type(scope): description"
    ```

9. **Push to Your Fork:**

    ```bash
    git push origin <branch-name>
    ```

10. **Submit a Pull Request (PR):** Open a PR from your branch to the `main` branch of the upstream EGOS repository.
    - Provide a clear title and description for your PR.
    - Link any related issues.
    - Explain the changes and the reasoning behind them.
    - Ensure all automated checks (CI/CD, linters - if configured) pass.
11. **Code Review:** Project maintainers will review your PR. Be responsive to feedback and make necessary adjustments.

feat/roadmap-updates

## AI Collaboration Workflow

EGOS leverages AI coding assistants (like Cascade) to accelerate development. When collaborating with AI:

- **Follow Guidelines:** Adhere strictly to the [human_ai_collaboration_guidelines](../../governance/human_ai_collaboration_guidelines.md).
- **Human Review MANDATORY:** All AI-generated output (code, documentation, plans, tests) **MUST** be reviewed and verified by a human developer. The developer retains full responsibility for the final committed code.
- **Handover Standards:** Use the [ai_handover_standard](../../reference/ai_handover_standard.mdc) when transferring context between sessions or agents.
- **Clarity:** Provide clear, concise instructions and context to the AI.
- **Verification:** Treat AI suggestions as proposals; verify their correctness, security, and alignment with project standards before integration.

main

## Standard Commit & Push Workflow (Main Branch)

To ensure your local changes are correctly synchronized with the `main` branch on GitHub, follow these steps **in order**. For standard commits of completed work, refer specifically to procedure **EGOS-GIT-COMMIT-01** in the [git_workflow_standards](../../reference/git_workflow_standards.mdc).

1. **Check Status (Optional, but recommended):**
    - Confirm which branch you are on and check for unsaved changes.
    - Command: `git status`

2. **Synchronize with Remote (`git pull`):**
    - **Purpose:** Download the latest updates from the `main` branch on GitHub to your local repository. This prevents your push from being rejected because the remote repository is ahead of yours.
    - Command: `git pull origin main`
    - **Attention:** If merge conflicts occur after the pull, resolve them by editing the marked files, save them, use `git add <resolved_file>` for each, and finalize the merge with `git commit` before proceeding.
    - **Important:** For detailed procedures on handling merge conflicts and other Git challenges, refer to the [git_workflow_standards](../../reference/git_workflow_standards.mdc) (Procedures EGOS-GIT-MERGE-01 and EGOS-GIT-PRECOMMIT-01).

3. **Stage Changes (`git add`):**
    - **Purpose:** Tell Git which modified or created files you want to include in the *next* commit.
    - Command for specific files: `git add <filename_1> <filename_2>`
    - Command to add *all* changes in the current directory (use with caution): `git add .`

4. **Commit Locally (`git commit`):**
    - **Purpose:** Save the staged changes to the history of *your* local repository.
    - Command: `git commit -m "type(scope): Your descriptive message here"`
    - **Important:** Use clear commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) standard (e.g., `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`). Refer to the `commit_messages.mdc` rule and **EGOS-GIT-COMMIT-01**.

5. **Push to GitHub (`git push`):**
    - **Purpose:** Send your local commits (which now include the updates from step 2) to the remote repository on GitHub.
    - Command: `git push origin main`

Following this sequence ensures a smoother workflow and reduces common Git errors.

## Documentation Contributions

Improvements to documentation are always welcome! Follow the development workflow above, making changes to `.md` files or adding docstrings within the code. Ensure your writing is clear, concise, and follows existing style where applicable.

Thank you again for your interest in contributing!

---

✧༺❀༻∞ EGOS ∞༺❀༻✧