---
description: Meta-prompt para teste de modelos LLM - Categoria Contexto Longo
trigger: llm.test.context
---

# LLM Test Suite: Long Context & Retrieval

## Objective
Evaluate the model's ability to handle long contexts (128K+ tokens) and accurately retrieve information from specific locations in the text.

## Test Structure

### Test 1: Needle in Haystack (Basic)
**Setup:**
Generate a context of exactly 50,000 tokens containing:
- Technical documentation about a fictional API
- Multiple code examples in different languages
- Scattered "needles" (specific facts) at various depths

**Needle Example:**
```
The secret API key for testing is: "sk-test-needle-789xyz"
This key should only be used in sandbox environments.
```

**Prompt Template:**
```
[FULL_CONTEXT_50K_TOKENS]

Question: What is the test API key mentioned in the documentation, and where should it be used?
```

**Evaluation Criteria:**
- Correctly retrieves exact key
- Understands usage constraints
- Identifies approximate location (beginning/middle/end)

### Test 2: Multi-Needle Retrieval (Intermediate)
**Setup:**
Generate a 100,000 token technical specification document with:
- 10 specific facts scattered at different positions
- Red herrings (similar but incorrect information)
- References to earlier sections

**Prompt Template:**
```
[FULL_CONTEXT_100K_TOKENS]

Questions:
1. What is the maximum file upload size allowed?
2. Which authentication method is deprecated as of v2.3?
3. What is the recommended cache TTL for user profiles?
4. List all rate limit headers returned by the API.
```

**Evaluation Criteria:**
- Accuracy of each retrieval (10 items)
- No confusion with red herrings
- Ability to connect related information across sections

### Test 3: Long-Context Summarization (Advanced)
**Setup:**
Provide 150,000 tokens of meeting transcripts from 10 weekly engineering meetings spanning 3 months.

**Prompt Template:**
```
[MEETING_TRANSCRIPTS_150K_TOKENS]

Task: Create a comprehensive summary covering:
1. Key decisions made across all meetings
2. Action items that were completed vs. still pending
3. Blockers mentioned and their resolution status
4. Technical directions that evolved over time

Format: Executive summary (1 page) + detailed breakdown by topic
```

**Evaluation Criteria:**
- Captures information from early AND late meetings
- Identifies trends over time
- Accurate tracking of action item status
- No hallucination of decisions not mentioned

### Test 4: Context-Aware Code Generation
**Setup:**
Provide 80,000 tokens of a large codebase (multiple files) with:
- Existing patterns and conventions
- Specific utility functions available
- Business logic scattered across files

**Prompt Template:**
```
[CODEBASE_80K_TOKENS]

Task: Add a new feature endpoint `/api/v1/users/bulk-export` that:
1. Accepts a list of user IDs (max 1000)
2. Returns CSV export asynchronously
3. Uses existing queue system (see queue.ts)
4. Follows the error handling pattern in errors.ts
5. Reuses the user serialization from user-serializer.ts
6. Respects the rate limiting middleware

Provide the complete implementation following existing patterns.
```

**Evaluation Criteria:**
- Uses patterns from the provided codebase
- Correctly references utility functions
- Follows existing error handling conventions
- Respects architectural constraints mentioned

## Scoring Rubric (1-10)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 50% | Correct retrieval from context |
| Completeness | 25% | Finds all relevant information |
| No Hallucination | 25% | Doesn't invent information |

## Context Length Tiers

| Tier | Tokens | Test Context | Target Models |
|------|--------|--------------|---------------|
| L1 | 32K | 25K context | Standard models |
| L2 | 128K | 100K context | Good long-context |
| L3 | 256K | 200K context | Excellent (Nemotron, Qwen3.6) |
| L4 | 1M | 800K context | Premium (Lyria, Gemini) |

## Output Format

```json
{
  "test_id": "context-001",
  "model_id": "model-name",
  "overall_score": 9.1,
  "context_tier_tested": "L3",
  "latency_ms": 3200,
  "token_usage": { "prompt": 50000, "completion": 500 },
  "test_results": [
    {
      "test": "needle-in-haystack",
      "score": 10,
      "passed": true,
      "depth_tokens": [1000, 25000, 49000],
      "retrieval_rate": "100%"
    },
    {
      "test": "multi-needle-retrieval",
      "score": 8,
      "passed": true,
      "needles_found": "9/10",
      "false_positives": 1
    }
  ],
  "context_window": 262144,
  "effective_context": 250000,
  "recommendation": "S-tier for long-context tasks"
}
```

## Thresholds

- **S-tier (9.0+)**: Primary for RAG, document analysis, large codebase understanding
- **A-tier (8.0-8.9)**: Secondary for long-context tasks
- **B-tier (7.0-7.9)**: Moderate context tasks (32K-64K)
- **C-tier (<7.0)**: Short context only (<32K)

## EGOS Integration

Store results in `llm_models` table with:
- `context_score`: Overall score
- `max_effective_context`: Last tier where accuracy > 90%
- `needle_retrieval_rate`: % of needles correctly found
- `context_latency_ms`: Latency at max context
- Recommended for `TASK_TYPE=summary,intelligence` when context >32K
