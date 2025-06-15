---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~7 k)
# Version 2.0 – “Prompt Alchemist” – 2025-06-13

description: Guides the distillation of a high-quality LLM interaction into a structured PDD (YAML), then validates and vaults it as JSON in the EGOS KOIOS PromptVault.
---

# DISTILL & VAULT PROMPT WORKFLOW (EGOS × WINDSURF)

> “Turn raw chat into structured, validated, and vaulted prompt assets.”

Invoke with `/distill_and_vault_prompt`.

---
## TABLE OF CONTENTS
1. Prerequisites & Environment  
2. Phase 1 – Capture Interaction  
3. Phase 2 – Distillation & Metadata  
4. Phase 3 – Quality Review  
5. Phase 4 – PDD Validation & Vaulting  
6. Annex – PDD YAML Structure Example  

---
## 1. PREREQUISITES & ENVIRONMENT // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | PromptVault repo cloned | `git remote -v` |
|   | EVA LLM evaluator available | `python -m eva --help` |
|   | `yaml` & `jsonschema` libs | `pip show pyyaml` |

Abort if any check fails.

---
## 2. PHASE 1 – CAPTURE INTERACTION
### 1.1 Identify High-Value Thread
Choose chat or notebook cell where output met or exceeded expectations.

### 1.2 Extract Conversation // turbo
```bash
python scripts/extract_chat.py --thread <id> --out raw_chat.md
```
Stores markdown with role tags.

---
## 3. PHASE 2 – DISTILLATION & METADATA
### 2.1 Distill Prompt Core
Use Cascade to summarise:
```
Extract system + user parts that led to desired output; condense; keep placeholders.
```
### 2.2 Create PDD YAML (see Annex for structure or refer to KOIOS_PDD_Standard.md)
Include `purpose`, `model_family`, `temperature`, `author`.

### 2.3 Link Supporting Files
If prompt relies on examples/data, add relative paths.

---
## 4. PHASE 3 – QUALITY REVIEW
### 3.1 Automated Scoring // turbo
```bash
eva score --prompt <your_pdd_file>.yaml --output scores.json
```
Must meet thresholds: Clarity ≥ 4, Robustness ≥ 4.

### 3.2 Peer Review
At least one reviewer approves via Pull Request checklist.

### 3.3 Ethical Scan
Run `/atrian_ethics_evaluation` on a sample response.

---
## 5. PHASE 4 – PDD VALIDATION & VAULTING
### 5.1 Validate PDD and Save to Vault // turbo
Once your PDD YAML file is ready (e.g., `my_distilled_prompt.yaml`), run the `validate_pdd.py` script to validate it against the KOIOS PDD schema and automatically save it as a JSON file in the PromptVault.

```powershell
# Ensure you are in a PowerShell terminal that can execute python
python C:\EGOS\subsystems\KOIOS\schemas\validate_pdd.py <path_to_your_pdd.yaml> --vault C:\EGOS\subsystems\KOIOS\vault
```
Replace `<path_to_your_pdd.yaml>` with the actual path to your PDD file.

**Expected Outcome:**
- The script will confirm successful validation.
- A JSON version of your PDD will be created in `C:\EGOS\subsystems\KOIOS\vault\` (e.g., `my_distilled_prompt.json`).

If validation fails, the script will output errors. Address these in your PDD YAML and re-run the command.

### 5.2 (Optional) Manual Index Update
Currently, the PromptVault index is not automatically updated. If an index file (e.g., `vault_manifest.json`) is implemented in `C:\EGOS\subsystems\KOIOS\vault\`, manually update it to include your new prompt.

---
## ANNEX – PDD YAML STRUCTURE EXAMPLE
This is an example of the structure for your PDD YAML file. For the complete standard and all available fields, refer to `C:\EGOS\docs\standards\KOIOS_PDD_Standard.md` and the schemas in `C:\EGOS\subsystems\KOIOS\schemas\pdd_schema.py`.
```yaml
id: <uuid>
slug: "generate-python-docstring"
title: "Generate detailed Python docstring"
purpose: "Improve code documentation quality."
model_family: "gpt-4o"
revision: 1.0
inputs:
  - name: "code"
    type: "string"
outputs:
  - name: "docstring"
    type: "string"
keywords: [documentation, python]
created: 2025-06-13T22:45:00Z
author: "enioxt"
license: CC-BY-4.0
tags: [prompt, productivity]
# --- Add other PDD fields as per KOIOS_PDD_Standard.md ---
```

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file <12 k chars; update version header on edits.

---
## Cross-References & Related Workflows

- /ai_assisted_research_and_synthesis – Provides research material that can be distilled into prompts.
- /atrian_ethics_evaluation – Evaluate distilled prompts for bias or safety issues.
- /dynamic_documentation_update_from_code_changes – Keep PromptVault docs aligned with new prompts.
- /project_handover_procedure – Transfer curated prompts to new owners.

*EOF*