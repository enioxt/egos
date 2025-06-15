---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~7 k)
# Version 2.0 – “EaaS Plugin Forge” – 2025-06-13

description: A structured process for integrating with and developing extensions for the ATRiAN Ethics as a Service (EaaS) SDKs
categories: [sdk_development, ethics, testing, devops]
requires: [ATRiAN]
---

# ATRIAN SDK DEVELOPMENT WORKFLOW (EGOS × WINDSURF)

> “Forge ethical extensions with confidence.”

Invoke with `/atrian_sdk_dev`.

---
## TABLE OF CONTENTS
1. Prerequisites & Toolchain  
2. Phase 1 – Scaffold Plugin  
3. Phase 2 – Implement Core Logic  
4. Phase 3 – Tests (Hyper-TDD)  
5. Phase 4 – Documentation & Samples  
6. Phase 5 – Publish & Version  
7. Annex A – Mutation Testing Gate  

---
## 1. PREREQUISITES & TOOLCHAIN // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | ATRiAN SDK repo cloned | `git submodule update --init` |
|   | Poetry installed | `poetry --version` |
|   | Mutmut + Hypothesis | `pip install mutmut hypothesis` |

Abort if any check fails.

---
## 2. PHASE 1 – SCAFFOLD PLUGIN
### 1.1 Generate Boilerplate // turbo
```bash
poetry new atrian_myplugin && cd atrian_myplugin
```
### 1.2 Add SDK Dependency
`poetry add atrian-eaas-sdk`.

### 1.3 Define Entry Point
In `pyproject.toml`:
```toml
[tool.poetry.plugins."atrian.plugins"]
myplugin = "atrian_myplugin.main:MyPlugin"
```

---
## 3. PHASE 2 – IMPLEMENT CORE LOGIC
Create `main.py` with `from atrian import PluginBase`.
Implement `evaluate()` returning ethical score adjustments.

---
## 4. PHASE 3 – TESTS (HYPER-TDD)
### 3.1 Red ➜ Green ➜ Refactor
Create failing unit test `tests/test_myplugin.py` using `pytest`.

### 3.2 Property-Based Tests
Use `Hypothesis` to check idempotent scoring.

### 3.3 Mutation Test Gate // turbo
```bash
mutmut run --paths-to-mutate atrian_myplugin
mutmut html
```
Fail build if score < 85%.

### 3.4 Ethical Assertions
Use `/atrian_ethics_evaluation` against generated logs.

---
## 5. PHASE 4 – DOCUMENTATION & SAMPLES
* Auto-gen API docs with `mkdocstrings`.
* Provide Jupyter notebook example.
* Update `README.md` with installation snippet.

---
## 6. PHASE 5 – PUBLISH & VERSION
### 5.1 Semantic Versioning
Follow `MAJOR.MINOR.PATCH` aligned with ATRiAN SDK minor.

### 5.2 Publish to Internal PyPI // turbo
```bash
poetry publish -r egos
```
### 5.3 Changelog & ADRS
Update `CHANGELOG.md`; record breaking changes in `ADRS_Log.md`.

---
## ANNEX A – MUTATION TESTING GATE
| Metric | Minimum |
|--------|---------|
| Surviving Mutants | <15% |
| Equivalent Mutants | auto-exclude |

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs.  
* Keep file <12 k chars; bump version on edits.

---
## Cross-References & Related Workflows

- /atrian_external_integration – Leverage this workflow when integrating SDK outputs with external platforms.
- /atrian_validator_testing – Ensure SDK extensions pass ethics validation.
- /iterative_code_refinement_cycle – Refine SDK codebase through continuous improvement.
- /dynamic_documentation_update_from_code_changes – Auto-update SDK docs after code mods.
- /project_handover_procedure – Transfer SDK package maintenance to another maintainer.

*EOF*