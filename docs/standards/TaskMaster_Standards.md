@references:
  - docs/standards/TaskMaster_Standards.md

# TaskMaster AI Standards for EGOS

## 1. Purpose and Scope

This document establishes standards for integrating and using TaskMaster AI within the EGOS ecosystem, ensuring alignment with the Master Quantum Prompt principles and EGOS global rules.

## 2. TaskMaster Directory Structure Standards

- **RULE-TM-DIR-01 (TaskMaster Directory):** TaskMaster files must be organized within the `.taskmaster` directory at the EGOS root.
- **RULE-TM-DIR-02 (Task Storage):** All tasks must be stored in `.taskmaster/tasks/tasks.json` with individual task files generated in the `tasks/` directory.
- **RULE-TM-DIR-03 (Configuration):** TaskMaster configuration must be maintained in `.taskmaster/config.json` following the established schema.

## 3. Task Creation and Management Standards

- **RULE-TM-TASK-01 (Task Structure):** All tasks must follow the standard TaskMaster JSON structure with required fields: id, title, description, status, dependencies, priority, details, testStrategy, and subtasks.
- **RULE-TM-TASK-02 (Task Language):** All task content must be in English, following `RULE-AI-LANG-01`.
- **RULE-TM-TASK-03 (MQP Alignment):** Tasks must align with Master Quantum Prompt principles, particularly Conscious Modularity, Sacred Privacy, and Integrated Ethics.
- **RULE-TM-TASK-04 (Task Dependencies):** Task dependencies must be explicitly defined and validated using `task-master validate-dependencies`.

## 4. TaskMaster Command Standards (via `egos-tasks.ps1`)

*Note: Standards for commands marked (P) are preliminary and will evolve as functionality is implemented.*

- **RULE-TM-CMD-01 (Primary Interface):** All TaskMaster operations within EGOS **must** be performed through the `.\egos-tasks.ps1 <command> [arguments]` wrapper script to ensure adherence to EGOS-specific workflows, logging (ADRS), and future integrations (e.g., ATRiAN).
- **RULE-TM-CMD-02 (Task Creation):** Create tasks using `.\egos-tasks.ps1 add "<task_title>" --desc "<description>"` or by processing documentation with `.\egos-tasks.ps1 prd <doc_path>`.
    - Tasks must align with `RULE-TM-TASK-03` (MQP Alignment).
- **RULE-TM-CMD-03 (Task Status Updates):** Update task status using `.\egos-tasks.ps1 status <id> <status>` or `.\egos-tasks.ps1 done <id>`.
    - Valid statuses include: `open`, `in-progress`, `blocked`, `review`, `done`, `deferred`, `cancelled`.
- **RULE-TM-CMD-04 (Task Generation):** If manual edits to `tasks.json` are necessary (discouraged), regenerate individual task files using `.\egos-tasks.ps1 generate`.

### 4.1 Advanced Task Operations (Placeholders - `egos-tasks.ps1`)

- **RULE-TM-CMD-05 (Template Usage - P):** 
    - `.\egos-tasks.ps1 template list`: Review available prompt engineering templates.
    - `.\egos-tasks.ps1 template use <templateName> --target <details>`: Apply templates for consistent task formulation. Templates themselves should be stored in `C:\EGOS\.taskmaster\templates` and align with MQP principles.
- **RULE-TM-CMD-06 (Task Expansion - P):** 
    - `.\egos-tasks.ps1 expand --id <taskId> [--cot] [--steps N]`: Break down complex tasks. If using `--cot`, ensure reasoning steps are logical and auditable.
- **RULE-TM-CMD-07 (Metadata Enrichment - P):** 
    - `.\egos-tasks.ps1 enrich-task --id <id> --context "<ctx>" --references "<refs>"`: Add relevant context or file references to tasks to aid understanding and execution. References should be valid paths or URLs.
- **RULE-TM-CMD-08 (Dependency Visualization - P):** 
    - `.\egos-tasks.ps1 visualize-dependencies --format <mermaid|text> [--output <file>]`: Generate visualizations to understand task relationships. If outputting to a file, use the `C:\EGOS\.taskmaster\reports` directory.
- **RULE-TM-CMD-09 (Code Analysis - P):** 
    - `.\egos-tasks.ps1 analyze-codebase --metrics "<metrics>"`: Perform codebase analysis. Generated reports should be stored in `C:\EGOS\.taskmaster\analysis`.
- **RULE-TM-CMD-10 (Refactoring Planning - P):** 
    - `.\egos-tasks.ps1 create-refactoring-plan --based-on <analysisFile>`: Develop refactoring plans based on analysis results. Plans should be stored in `C:\EGOS\.taskmaster\analysis`.
- **RULE-TM-CMD-11 (Task Validation - P):** 
    - `.\egos-tasks.ps1 validate-task --id <id> [--with-tests <details>]`: Verify task completion against defined criteria or tests. Test files, if referenced, should be accessible and executable.
- **RULE-TM-CMD-12 (Ethical Evaluation - P):** 
    - `.\egos-tasks.ps1 evaluate --id <id> [--impact "..."] [--principles "..."]`: Conduct ethical evaluations, especially for tasks with significant impact or AI involvement. Reference specific EGOS ethical principles or ATRiAN guidelines. This is a critical step before finalizing high-impact tasks.

## 5. TaskMaster AI Model Configuration Standards

- **RULE-TM-MODEL-01 (Provider Selection):** Configure TaskMaster to use OpenRouter as the primary provider for main, research, and fallback models.
- **RULE-TM-MODEL-02 (Model Selection):** Use free models where possible: gpt-3.5-turbo for main tasks, llama-3-8b-instruct for research, and gemma-7b-it as fallback.
- **RULE-TM-MODEL-03 (Environment Variables):** Maintain consistent environment variables across `.env` file and MCP configuration.

## 6. TaskMaster Integration Standards

- **RULE-TM-INT-01 (ATRiAN Integration):** Integrate TaskMaster with ATRiAN for ethical evaluation of tasks, particularly those involving user data or AI decision-making.
- **RULE-TM-INT-02 (Workflow Integration):** Use the established TaskMaster workflow (`/taskmaster_task_management`) for standardized task management.
- **RULE-TM-INT-03 (EGOS Wrapper Script):** The `egos-tasks.ps1` script is the **mandatory** interface for all TaskMaster operations and EGOS-specific integrations, including the advanced placeholder commands. It standardizes logging, argument parsing, and interaction with the underlying `task-master-ai` tool.

## 7. TaskMaster Documentation Standards

- **RULE-TM-DOC-01 (Task Documentation):** Document implementation details and decisions in individual task files.
- **RULE-TM-DOC-02 (Reference Documentation):** Maintain up-to-date TaskMaster documentation in `docs/TaskMaster.md`.
- **RULE-TM-DOC-03 (Standards Compliance):** Ensure all TaskMaster documentation follows KOIOS documentation standards.

## 8. TaskMaster Reporting Standards

- **RULE-TM-REP-01 (Task Status Reporting):** Begin development sessions by checking task status with `task-master list`.
- **RULE-TM-REP-02 (Complexity Analysis):** Use `task-master analyze-complexity` to identify and report on complex tasks.
- **RULE-TM-REP-03 (Progress Tracking):** Track and report task progress in alignment with `RULE-OPS-ROADMAP-TASKING-01`.

## 9. References

- [TaskMaster Documentation](file:///C:/EGOS/docs/TaskMaster.md)
- [TaskMaster Task Management Workflow](file:///C:/EGOS/.windsurf/workflows/taskmaster_task_management.md)
- [EGOS Global Rules](.windsurfrules)
- [Master Quantum Prompt](file:///C:/EGOS/MQP.md)