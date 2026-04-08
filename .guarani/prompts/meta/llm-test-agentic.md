---
description: Meta-prompt para teste de modelos LLM - Categoria Agentic/Tool Calling
trigger: llm.test.agentic
---

# LLM Test Suite: Agentic Behavior & Tool Calling

## Objective
Evaluate the model's ability to use tools effectively, maintain state across turns, and execute multi-step agentic workflows.

## Test Structure

### Test 1: Tool Selection (Basic)
**Available Tools:**
```json
{
  "tools": [
    {
      "name": "search_code",
      "description": "Search codebase for patterns",
      "parameters": { "query": "string", "language": "string?" }
    },
    {
      "name": "read_file",
      "description": "Read file contents",
      "parameters": { "path": "string", "offset": "number?", "limit": "number?" }
    },
    {
      "name": "write_file",
      "description": "Write or edit file",
      "parameters": { "path": "string", "content": "string" }
    },
    {
      "name": "run_command",
      "description": "Execute shell command",
      "parameters": { "command": "string", "cwd": "string?" }
    }
  ]
}
```

**Prompt:**
```
Task: Find all usages of the deprecated function `legacyAuth()` and replace them with `newAuth()`.

Plan your approach and call the necessary tools. Show your reasoning before each tool call.
```

**Expected Tool Sequence:**
1. `search_code` for "legacyAuth"
2. Multiple `read_file` to understand contexts
3. Multiple `write_file` to perform replacements
4. `run_command` to verify (e.g., grep to confirm)

**Evaluation Criteria:**
- Correct tool selection for each step
- Proper parameter formatting
- Logical sequence of operations
- Verification step included

### Test 2: State Management (Intermediate)
**Scenario:**
Multi-turn conversation where the agent must:
- Remember user preferences across turns
- Handle corrections gracefully
- Maintain context of ongoing task

**Turn 1:**
```
User: "I need to refactor the authentication module. Please use TypeScript and follow the repository pattern. I prefer async/await over promises."
```

**Turn 2:**
```
User: "Actually, I changed my mind - use the service pattern instead of repository. Keep the async/await preference though."
```

**Turn 3:**
```
User: "Start with the login function. It should validate the email format and check against the database."
```

**Turn 4:**
```
User: "Wait, what pattern did I ask for again? And which syntax preference?"
```

**Evaluation Criteria:**
- Correctly remembers: service pattern, async/await, TypeScript
- Implements with correct pattern
- Accurately recalls preferences when asked

### Test 3: Error Recovery (Advanced)
**Setup:**
Agent is given a task with tools that will fail intermittently.

**Scenario:**
```
Task: Deploy a new feature branch to staging.

Available tools: git_clone, git_checkout, run_tests, deploy_staging, notify_slack

Simulated failures:
- git_checkout will fail first time (network error), succeed second time
- run_tests will fail with flaky test (agent should retry once)
- deploy_staging will timeout (agent should handle gracefully)
```

**Evaluation Criteria:**
- Retries on transient failures
- Doesn't give up too early
- Reports meaningful error when unrecoverable
- Maintains task context through retries

### Test 4: Multi-Tool Coordination
**Task:**
```
Create a new API endpoint with full implementation:

1. Add the route handler in routes.ts
2. Create the controller in controllers/
3. Add validation schema in schemas/
4. Write unit tests in __tests/
5. Update the API documentation
6. Run tests to verify

Use the existing patterns from the codebase.
```

**Evaluation Criteria:**
- Discovers existing patterns first (read_file)
- Creates all required files (write_file)
- Follows consistent style
- Runs verification (run_command/run_tests)
- Handles errors appropriately

## Scoring Rubric (1-10)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Tool Accuracy | 35% | Correct tool for the job |
| Error Handling | 25% | Graceful failures and recovery |
| State Management | 25% | Remembers context across turns |
| Efficiency | 15% | Minimal unnecessary tool calls |

## Agentic Capabilities Matrix

| Capability | Description | Test Coverage |
|------------|-------------|---------------|
| Tool Calling | Structured JSON tool calls | Test 1, 4 |
| State Tracking | Memory across conversation | Test 2 |
| Error Recovery | Retry and fallback logic | Test 3 |
| Planning | Multi-step task breakdown | Test 4 |
| Verification | Self-checking results | Test 1, 4 |

## Output Format

```json
{
  "test_id": "agentic-001",
  "model_id": "model-name",
  "overall_score": 8.7,
  "latency_ms": 5600,
  "token_usage": { "prompt": 800, "completion": 1200 },
  "turns_required": 8,
  "tool_calls": {
    "total": 12,
    "correct": 11,
    "redundant": 1
  },
  "test_results": [
    {
      "test": "tool-selection",
      "score": 9,
      "passed": true,
      "tools_used": ["search_code", "read_file", "write_file", "run_command"],
      "sequence_correct": true
    },
    {
      "test": "state-management",
      "score": 8,
      "passed": true,
      "recall_accuracy": "100%"
    }
  ],
  "recommendation": "S-tier for agentic tasks"
}
```

## Thresholds

- **S-tier (8.5+)**: Primary for agent workflows, tool use
- **A-tier (7.5-8.4)**: Secondary for agent tasks
- **B-tier (6.5-7.4)**: Simple tool calling only
- **C-tier (<6.5)**: Not recommended for agentic use

## EGOS Integration

Store results in `llm_models` table with:
- `agentic_score`: Overall score
- `tool_accuracy`: % of correct tool selections
- `error_recovery_rate`: % of recoverable errors handled
- `avg_turns_to_complete`: Efficiency metric
- Recommended for `TASK_TYPE=agent-workflow,mcp-routing` in fallback chain
