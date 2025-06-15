---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~7 k)
# Version 2.0 – “Constitution Test Matrix” – 2025-06-13

description: Comprehensive testing workflow for ATRiAN Ethical Constitution Validator
categories: [testing, ethics, governance]
requires: [ATRiAN]
---

# ATRIAN VALIDATOR TESTING WORKFLOW (EGOS × WINDSURF)

> “Every constitution, bullet-proof.”

Invoke with `/atrian_validator_testing`.

---
## TABLE OF CONTENTS
1. Prerequisites & Fixtures  
2. Phase 1 – Fixture Loader  
3. Phase 2 – Parallel Test Matrix  
4. Phase 3 – Benchmark & Regression  
5. Phase 4 – Reporting & Gates  
6. Annex – Benchmark Thresholds  

---
## 1. PREREQUISITES & FIXTURES // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Constitutions dir exists | `dir constitutions/` |
|   | Validator CLI installed | `pip install atrian-validator` |
|   | `pytest-xdist` for parallel | `pip show pytest-xdist` |

Abort if any check fails.

---
## 2. PHASE 1 – FIXTURE LOADER
Generate param fixtures from YAML constitutions:
```python
import yaml, pytest, glob
@pytest.fixture(params=glob.glob('constitutions/*.yaml'))
```

---
## 3. PHASE 2 – PARALLEL TEST MATRIX // turbo
```bash
pytest -n auto tests/test_validator.py
```
Covers valid, invalid, edge-case constitutions.

---
## 4. PHASE 3 – BENCHMARK & REGRESSION
### 3.1 Performance Bench
Use `pytest-benchmark`; ensure median validation time <50 ms.

### 3.2 Mutation Gate
`mutmut` over validator core; surviving mutants <10%.

---
## 5. PHASE 4 – REPORTING & GATES
* HTML coverage report 95%+.
* If any benchmark metric > threshold, block merge.
* Log failures to `ADRS_Log.md` if security critical.

---
## ANNEX – BENCHMARK THRESHOLDS
| Metric | Target |
|--------|--------|
| median_ms | <50 |
| p99_ms | <70 |

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs.  
* Keep file <12 k chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /atrian_ethics_evaluation – Shares evaluation rubrics used by the validator.
- /atrian_sdk_dev – Ensure new SDK features pass validator tests.
- /iterative_code_refinement_cycle – Address issues uncovered during validator runs.
- /dynamic_documentation_update_from_code_changes – Sync test-guides and reports.
- /project_handover_procedure – Pass validated test harness to QA teams.

*EOF*