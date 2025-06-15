@references:
  - docs/TaskMaster.md

# TaskMaster AI Integration for EGOS

## Overview

TaskMaster AI is integrated into the EGOS ecosystem as a task management and planning system that aligns with the Master Quantum Prompt principles. It provides structured task creation, management, and ethical evaluation through ATRiAN integration.

## Core Functionality

- **AI-Driven Task Management**: Generate, track, and manage tasks with AI assistance
- **Ethical Alignment**: Integration with ATRiAN for ethical evaluation of tasks
- **Structured Development**: Break down complex projects into manageable tasks
- **Progress Tracking**: Monitor task status, dependencies, and completion

## Directory Structure

```
C:\EGOS\.taskmaster\         # Main TaskMaster configuration directory
├── config.json              # TaskMaster AI model configuration
├── tasks\                   # Task storage directory
│   └── tasks.json           # Central task database
├── docs\                    # TaskMaster documentation
├── reports\                 # Analysis reports
└── templates\               # Task templates
```

## Configuration

TaskMaster is configured to use OpenRouter for AI models, with the following configuration:

- **Main Model**: OpenRouter (gpt-3.5-turbo)
- **Research Model**: OpenRouter (meta-llama/llama-3-8b-instruct)
- **Fallback Model**: OpenRouter (google/gemma-7b-it)

Environment variables are managed through:
- `.env` file for CLI usage
- MCP configuration for Windsurf integration

## Command Reference (`egos-tasks.ps1`)

The primary way to interact with TaskMaster within EGOS is through the `egos-tasks.ps1` wrapper script. This script provides a set of commands that often map to underlying `task-master` functionalities, along with EGOS-specific enhancements. 

*Note: Commands marked with (P) are placeholders and their full functionality is under development.*

| Command (`.\egos-tasks.ps1 ...`) | Description | Example |
|---------------------------------|-------------|---------|
| `init`                          | Initialize task-master in the EGOS project | `.\egos-tasks.ps1 init` |
| `add "Task Title" [--desc "..."]` | Add a new task | `.\egos-tasks.ps1 add "Implement Feature X" --desc "Details..."` |
| `list`                          | List all tasks | `.\egos-tasks.ps1 list` |
| `next`                          | Show next recommended task | `.\egos-tasks.ps1 next` |
| `done <taskId>`                 | Mark task as completed | `.\egos-tasks.ps1 done 123` |
| `prd <filePath>`                | Process Product Requirements Document | `.\egos-tasks.ps1 prd C:\EGOS\docs\PRD_FeatureY.md` |
| `plan`                          | Generate project plan based on tasks | `.\egos-tasks.ps1 plan` |
| `scan-docs`                     | Scan key EGOS documents for context | `.\egos-tasks.ps1 scan-docs` |
| `status <taskId> <status>`      | Update task status (e.g., open, in-progress) | `.\egos-tasks.ps1 status 123 in-progress` |
| `generate`                      | Generate task files from tasks.json (if applicable) | `.\egos-tasks.ps1 generate` |
| `template list`                 | (P) List available prompt templates | `.\egos-tasks.ps1 template list` |
| `template use <tpl> --target <details>` | (P) Use a prompt template | `.\egos-tasks.ps1 template use MyTemplate --target "New task details"` |
| `expand --id <taskId> [--cot] [--steps N]` | (P) Expand task, optionally with Chain of Thought | `.\egos-tasks.ps1 expand --id 123 --cot --steps 3` |
| `enrich-task --id <id> --context "C" --refs "R"` | (P) Add metadata to a task | `.\egos-tasks.ps1 enrich-task --id 123 --context "Relates to UI" --refs "ui_spec.md"` |
| `visualize-dependencies --format <fmt> [--out <file>]` | (P) Visualize task dependencies | `.\egos-tasks.ps1 visualize-dependencies --format mermaid` |
| `analyze-codebase --metrics "m1,m2"` | (P) Analyze codebase | `.\egos-tasks.ps1 analyze-codebase --metrics "complexity,coverage"` |
| `create-refactoring-plan --based-on <file>` | (P) Create refactoring plan | `.\egos-tasks.ps1 create-refactoring-plan --based-on analysis.json` |
| `validate-task --id <id> [--with-tests <tests>]` | (P) Validate a task | `.\egos-tasks.ps1 validate-task --id 123 --with-tests pester_tests.ps1` |
| `evaluate --id <id> [--impact "..."] [--princ "..."]` | (P) Evaluate task ethics (ATRiAN integration pending) | `.\egos-tasks.ps1 evaluate --id 123 --impact "High"` |

## EGOS Integration Points

### ATRiAN Integration

TaskMaster integrates with ATRiAN to ensure tasks are ethically evaluated and aligned with the Master Quantum Prompt principles. This integration:

1. Evaluates task descriptions for ethical considerations
2. Provides guidance on task implementation aligned with Sacred Privacy
3. Ensures task outcomes respect Integrated Ethics principles

### MQP Alignment

All tasks created through TaskMaster are aligned with the Master Quantum Prompt principles:

- **Conscious Modularity**: Tasks are broken down into manageable components
- **Sacred Privacy**: Tasks involving sensitive data are properly flagged
- **Integrated Ethics**: Ethical considerations are embedded in task descriptions
- **Systemic Cartography**: Task dependencies are clearly mapped

### Workflow Integration

TaskMaster is integrated into the EGOS workflow through:

1. **Task Creation**: `task-master parse-prd` to generate tasks from EGOS documents
2. **Daily Planning**: `task-master list` and `task-master next` for work prioritization
3. **Status Updates**: `task-master set-status` to track progress
4. **Complexity Analysis**: `task-master analyze-complexity` to identify challenging tasks

## Usage Guidelines

1. Begin each development session by checking current tasks with `task-master list`
2. Select tasks based on dependencies, priority, and alignment with current goals
3. Update task status as you progress
4. Document implementation details in task files
5. Use `egos-tasks.ps1` for EGOS-specific task management commands

## References

- [TaskMaster GitHub Repository](https://github.com/eyaltoledano/claude-task-master)
- [EGOS Master Quantum Prompt](file:///C:/EGOS/MQP.md)
- [ATRiAN Integration Documentation](file:///C:/EGOS/ATRiAN/ATRiAN.md)