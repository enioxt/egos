---
description: Meta-prompt para teste de modelos LLM - Categoria Reasoning
trigger: llm.test.reasoning
---

# LLM Test Suite: Reasoning & Logic

## Objective
Evaluate the model's ability to perform logical reasoning, mathematical problem-solving, and multi-step inference.

## Test Structure

### Test 1: Logical Deduction (Basic)
**Prompt:**
```
Four people (Alice, Bob, Carol, Dave) are sitting in a row of four chairs.
Clues:
1. Alice is not at either end
2. Bob is immediately to the left of Carol
3. Dave is not next to Alice

Question: What is the seating order from left to right?
Provide your reasoning step by step.
```

**Evaluation Criteria:**
- Correct answer (Bob, Carol, Alice, Dave)
- Clear step-by-step reasoning
- Systematic elimination of possibilities

### Test 2: Mathematical Word Problem (Intermediate)
**Prompt:**
```
A water tank has two inlet pipes and one drain pipe.
- Pipe A fills the tank in 6 hours
- Pipe B fills the tank in 4 hours
- Drain C empties the tank in 8 hours

The tank starts empty. At 9:00 AM, all three pipes are opened.
At 2:00 PM, pipe B is closed due to maintenance.
At what time will the tank be exactly 75% full?

Show all calculations and reasoning.
```

**Evaluation Criteria:**
- Correct calculation of combined rates
- Proper time tracking
- Accurate final answer
- Clear mathematical reasoning

### Test 3: Multi-Step Planning (Advanced)
**Prompt:**
```
You need to plan a project with the following constraints:

Tasks:
- A (design): 2 days, must finish before B and C
- B (frontend): 3 days, needs A, can parallel with C
- C (backend): 4 days, needs A, can parallel with B
- D (integration): 2 days, needs B and C
- E (testing): 2 days, needs D

Constraints:
- Frontend developer can only work on B (not available for other tasks)
- Backend developer can work on C and D (but not simultaneously)
- You (lead) can do A and E
- Weekends are non-working days
- Start date: Monday, March 3rd

Questions:
1. What is the minimum project duration?
2. When will the project finish?
3. Identify the critical path
4. Is there any resource conflict?
```

**Evaluation Criteria:**
- Correct critical path identification
- Accurate timeline calculation
- Resource constraint analysis
- Consideration of weekends

### Test 4: Abductive Reasoning
**Prompt:**
```
A software system has been experiencing intermittent failures.
Observations:
- Failures happen more frequently during high-traffic periods
- The error logs show "Connection timeout" to the database
- CPU usage stays normal during failures
- Memory usage spikes just before each failure
- The issue started after the last deployment 2 weeks ago
- Rolling back the deployment fixes the issue

Hypotheses:
H1: Database connection pool is too small
H2: New deployment introduced a memory leak
H3: Network infrastructure is overloaded
H4: Database server is under-provisioned

Question: Which hypothesis is most likely? Explain your reasoning and suggest how to validate it.
```

**Evaluation Criteria:**
- Identifies most likely hypothesis (H2)
- Considers all evidence systematically
- Provides validation strategy
- Acknowledges uncertainty appropriately

## Scoring Rubric (1-10)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 45% | Final answer is correct |
| Reasoning Quality | 35% | Logical, systematic approach |
| Clarity | 20% | Easy to follow explanation |

## Output Format

```json
{
  "test_id": "reasoning-001",
  "model_id": "model-name",
  "overall_score": 8.2,
  "latency_ms": 1890,
  "token_usage": { "prompt": 200, "completion": 1200 },
  "test_results": [
    {
      "test": "logical-deduction",
      "score": 9,
      "passed": true,
      "notes": "Clear systematic elimination"
    },
    {
      "test": "mathematical-word-problem",
      "score": 7,
      "passed": true,
      "notes": "Correct answer but skipped rate calculation explanation"
    }
  ],
  "recommendation": "A-tier for reasoning tasks"
}
```

## Thresholds

- **S-tier (8.5+)**: Primary for complex analysis, planning
- **A-tier (7.5-8.4)**: Secondary for reasoning tasks
- **B-tier (6.5-7.4)**: Simple reasoning only
- **C-tier (<6.5)**: Not recommended for EGOS reasoning

## EGOS Integration

Store results in `llm_models` table with:
- `reasoning_score`: Overall score
- `reasoning_latency_avg`: Average latency
- `multi_step_capability`: Score on planning tests
- Recommended for `TASK_TYPE=intelligence,review` in fallback chain
