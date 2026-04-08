---
description: Meta-prompt para teste de modelos LLM - Categoria Coding
trigger: llm.test.coding
---

# LLM Test Suite: Coding Performance

## Objective
Evaluate the model's ability to generate, debug, and refactor code across multiple languages and complexity levels.

## Test Structure

### Test 1: Function Generation (Basic)
**Prompt:**
```
Write a TypeScript function that validates Brazilian CPF numbers following the official algorithm.
Requirements:
- Accept string input with or without formatting (000.000.000-00 or 00000000000)
- Return boolean indicating validity
- Handle edge cases (empty string, null, repeated digits)
- Include comments explaining the algorithm
```

**Evaluation Criteria:**
- Correctness (must pass all test cases)
- Code style (readable, well-commented)
- Edge case handling
- Type safety

### Test 2: Debug Challenge (Intermediate)
**Prompt:**
```
Debug this TypeScript function that's supposed to debounce API calls:

function debounce(fn, delay) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(args), delay);
  };
}

Issues reported:
1. Arguments not being passed correctly to the debounced function
2. Memory leak warning in React applications
3. No way to cancel pending calls

Provide the fixed implementation with explanations.
```

**Evaluation Criteria:**
- Identifies all bugs
- Provides correct fix
- Explains the issues clearly
- Considers React/closure best practices

### Test 3: Refactoring (Advanced)
**Prompt:**
```
Refactor this nested promise chain to use modern async/await with proper error handling:

fetchUser(userId)
  .then(user => fetchOrders(user.id))
  .then(orders => {
    if (orders.length === 0) {
      return Promise.reject(new Error('No orders found'));
    }
    return processOrders(orders);
  })
  .then(processed => {
    return { success: true, data: processed };
  })
  .catch(err => {
    console.error(err);
    return { success: false, error: err.message };
  });
```

**Evaluation Criteria:**
- Proper async/await conversion
- Clean error handling
- Type safety
- Readability improvements

### Test 4: Algorithm Design
**Prompt:**
```
Design a rate limiter that supports:
- Token bucket algorithm
- Configurable rate and burst
- Per-key limits (e.g., per user ID)
- In-memory storage with optional Redis backend
- TypeScript implementation

Include the core algorithm and a usage example.
```

**Evaluation Criteria:**
- Algorithm correctness
- Clean architecture
- Configurability
- Performance considerations

## Scoring Rubric (1-10)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 40% | Code works as specified |
| Code Quality | 25% | Clean, idiomatic, maintainable |
| Edge Cases | 20% | Handles unexpected inputs |
| Explanation | 15% | Clear reasoning and comments |

## Output Format

```json
{
  "test_id": "coding-001",
  "model_id": "model-name",
  "overall_score": 8.5,
  "latency_ms": 2450,
  "token_usage": { "prompt": 150, "completion": 890 },
  "test_results": [
    {
      "test": "function-generation",
      "score": 9,
      "passed": true,
      "notes": "Excellent edge case handling"
    },
    {
      "test": "debug-challenge",
      "score": 8,
      "passed": true,
      "notes": "Correct fix but could explain memory leak better"
    }
  ],
  "recommendation": "S-tier for coding tasks"
}
```

## Thresholds

- **S-tier (9.0+)**: Primary model for coding tasks
- **A-tier (8.0-8.9)**: Secondary fallback for coding
- **B-tier (7.0-7.9)**: General tasks only
- **C-tier (<7.0)**: Not recommended for EGOS

## EGOS Integration

Store results in `llm_models` table with:
- `coding_score`: Overall score
- `coding_latency_avg`: Average latency across tests
- `coding_reliability`: Pass rate percentage
- Recommended for `TASK_TYPE=coding` in fallback chain
