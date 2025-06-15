---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~8 k)
# Version 2.0 – “Refactor Loop” – 2025-06-13

description: A structured process for progressively improving code quality, functionality, and performance using AI-assisted feedback loops and automated checks
categories: [development, quality_assurance, automation]
requires: [ATRiAN, TaskMaster]
---

# ITERATIVE CODE REFINEMENT CYCLE WORKFLOW (EGOS × WINDSURF)

> “Code never stops evolving—nor should we.”

Invoke with `/iterative_code_refinement_cycle`.

---
## TABLE OF CONTENTS
1. Prerequisites  
2. Phase 1 – Identify Target  
3. Phase 2 – Hypothesize Improvement  
4. Phase 3 – Implement & Test  
5. Phase 4 – Measure & Compare  
6. Phase 5 – Document & Iterate  
7. Annex – Metrics Dashboard  

---
## 1. PREREQUISITES // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Hyper-TDD pipeline green | `pytest -q` |
|   | Coverage ≥ 90 % | `coverage html` |
|   | Linters clean | `ruff .` |

Abort if any check fails.

---
## 2. PHASE 1 – IDENTIFY TARGET
Use `grep_search` or code review to select function/module needing improvement (complexity, performance, clarity).
Log ticket in TaskMaster.

---
## 3. PHASE 2 – HYPOTHESIZE IMPROVEMENT
Write hypothesis with expected measurable gain (e.g., 20 % speed).

---
## 4. PHASE 3 – IMPLEMENT & TEST
### 3.1 AI-assisted Refactor
Use Cascade to propose patch.

### 3.2 Run Tests & Mutation Gate // turbo
```bash
pytest && mutmut run
```

---
## 5. PHASE 4 – MEASURE & COMPARE
### 4.1 Benchmark Old vs New
`pytest-benchmark compare`.

### 4.2 Accept Criteria
If metrics improved and tests pass, proceed; else revert.

---
## 6. PHASE 5 – DOCUMENT & ITERATE
* Update docstrings & changelog.
* Open PR, reviewer checks metric deltas.
* Repeat cycle until KPI plateau.

---
## ANNEX – METRICS DASHBOARD (Prometheus)
| Metric | Goal |
|--------|------|
| function_cpu_ms | ↓ |
| alloc_bytes | ↓ |
| cyclomatic_complexity | ↓ |

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file <12 k chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /atrian_ethics_evaluation – Feed failing evaluation results into the cycle for fix implementation.
- /dynamic_documentation_update_from_code_changes – Update docs automatically after each iteration.
- /tdd_based_dev_workflow – Combine to enforce quality gates and test coverage.
- /project_handover_procedure – Provide clean state before handover.

*EOF*