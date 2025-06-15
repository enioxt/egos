---
title: LLM Suggestion Engine for Invalid Constitutions
status: Draft
owner: R&D
---

@references:
  - docs/validator/LLM_SUGGESTION_ENGINE.md

## Prompt Template
```
You are an AI compliance assistant. Given the following constitution YAML and validation error message, propose a corrected constitution snippet.

Error: {{ error_message }}
Constitution:
{{ constitution_yaml }}
```

## Safety & Cost Controls
* `max_tokens` 400
* temperature 0.3
* model: `gpt-4o` or local `Mistral-7B` fallback

## Flow
1. Validator fails → captures `error_message` and raw YAML.
2. Sends prompt to LLM via `/suggest` internal endpoint.
3. Returns `suggested_fix` block.

## Future
* Fine-tune a smaller model for on-prem deployments.