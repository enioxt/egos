---
description: "Prompt creation: Architect → Evaluator → Optimizer"
---

# /prompt — Prompt Engineering Flow (Agnostic v2.0)

> **Works in:** ANY repo | **When:** Creating system prompts, agent instructions, or AI workflows

---

## Phase 1: Architect

```
⚠️  AI AGENT: Design the prompt:

1. ROLE: Who is the AI? What's its expertise?
2. CONTEXT: What information does it need?
3. TASK: What exactly should it do?
4. FORMAT: How should the output be structured?
5. CONSTRAINTS: What should it NOT do?
6. EXAMPLES: Provide 1-2 input/output examples

Output a complete draft prompt.
```

## Phase 2: Evaluate

```
⚠️  AI AGENT: Score the draft on:

| Criterion | Score (1-10) | Notes |
|-----------|-------------|-------|
| Clarity | | Is the instruction unambiguous? |
| Completeness | | Does it cover all cases? |
| Efficiency | | Is it concise (no unnecessary tokens)? |
| Safety | | Does it prevent harmful outputs? |
| Robustness | | Will it handle edge cases? |

Identify weaknesses and improvement opportunities.
```

## Phase 3: Optimize

```
⚠️  AI AGENT: Apply optimizations:

1. Remove redundant instructions
2. Add missing edge case handling
3. Improve output format specification
4. Add chain-of-thought if complex reasoning needed
5. Test with adversarial inputs mentally
6. Final version with estimated token count
```
