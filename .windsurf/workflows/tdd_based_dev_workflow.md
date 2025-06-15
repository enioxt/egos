---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12000 chars (current ~10 k)
# Version 2.0 – "Hyper-TDD" rev after comprehensive web + internal research – 2025-06-13

description: Holistic Test-Driven Development workflow for EGOS, fusing modern practices—property-based, mutation, contract & ethical testing—with AI/Windsurf automations and CI/CD governance.
categories: [development, testing, quality_assurance, ethics]
requires: [ATRiAN, KOIOS]
---

# HYPER-TDD WORKFLOW (WINDSURF × EGOS)

*Maxim: “Tests craft design, automation crafts velocity, ethics crafts trust.”*

Invoke anytime with `/tdd_based_dev_workflow` (slash command). All `// turbo` steps may auto-run.

---
## 0. PREREQUISITES CHECKLIST  // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Python ≥3.11 + Poetry | `poetry --version` |
|   | Core test libs | `poetry add --group dev pytest pytest-cov hypothesis mutmut` |
|   | Static analysis | `poetry add --group dev ruff mypy bandit` |
|   | Mutation score goal set in `pyproject.toml` | – |
|   | ATRiAN / ETHIK endpoints responsive | `curl http://localhost:8600/health` |

Abort if any check fails.

---
## 1. IDEATION & DOMAIN MODELLING (OPTIONAL)
Use `/ai_assisted_research_and_synthesis` to explore problem context, competitor patterns, user stories. Pin artefacts under `docs/specs/`.

---
## 2. DESIGN FOR TESTABILITY
### 2.1 Define Boundaries (Hexagonal / Clean Arch)
• Identify domain entities, ports, adapters.  
• Prefer pure functions; inject IO via interfaces.

### 2.2 Scenario Matrix
Capture *happy*, *edge*, *failure*, *security*, *ethics* cases. Ex:
```
|ID|Scenario                 |Expected     |Priority|
|01|valid payment           |OK receipt   |H|
|07|fraudulent card         |blocked + log|H|
```
Store as `tests/specs/payment_scenarios.md`.

### 2.3 Skeleton Code
Generate minimal class/function stubs with type hints. Eg.:
```python
class PaymentGateway(Protocol):
    def charge(self, amount: Decimal, token: str) -> bool: ...
```

---
## 3. RED – AUTHOR FAILING TESTS
### 3.1 Unit Layer (PyTest + Hypothesis)
```python
@given(amount=st.decimals(min_value=0, max_value=1000))
def test_charge_success(payment_gateway_stub, amount):
    assert gateway.charge(amount, "tok") is True
```
Hypothesis explores value space beyond hand-picked inputs.

### 3.2 Contract/Consumer-Driven Tests (CDC) – Pact
• Define expectations for external microservices under `contracts/`  
• Run `pact-verifier` in CI.

### 3.3 Security/Abuse Tests
Use `pytest-bandit` or OWASP ZAP docker for API surfaces.

### 3.4 Ethical Assertions
```python
@ethik_guard("no_bias")
```
ATRiAN validates decisions against constitution.

Run selective suite: `pytest -k "payment and not slow" -q`  // turbo

---
## 4. GREEN – MINIMAL IMPLEMENTATION
### 4.1 Pass the Red
Implement smallest logic; steal design ideas from tests. Keep cyclomatic complexity <7.

### 4.2 Commit Signed Off  // turbo
```
git commit -S -m "GREEN: payment charge passes basic + property tests"
```

---
## 5. REFACTOR – CLEAN DESIGN
### 5.1 Rule of Three
Refactor on third similar code path.

### 5.2 Patterns
Apply SOLID, DDD, FP purity, extract modules. Ensure public API unchanged.

### 5.3 Observability
Add OpenTelemetry spans and structured logs; tests assert span names.

### 5.4 Static & Mutation Gates  // turbo-all
```
ruff . && mypy . && mutmut run --paths-to-mutate project/ --runner pytest --use-coverage
```
Target mutation score ≥70%.

---
## 6. INTEGRATION, SYSTEM & REGRESSION
### 6.1 Docker Compose Test Environment
Spin up DB, Redis, mock services.
```bash
docker compose -f docker-compose.test.yml up -d
pytest tests/integration -q
```
### 6.2 End-to-End (E2E) via Playwright/Cypress
Ensure UI flows remain intact; tag tests `@e2e` to run nightly.

### 6.3 Performance Budgets
Use `pytest-benchmark` to guard latency; fail if >20 ms regression.

---
## 7. GOVERNANCE & ETHIK VALIDATION
### 7.1 ETHIK Batch Suite
`python scripts/ethik_validator.py --all` ensures no policy breach.

### 7.2 License & Compliance Scans
`cyclonedx-python` SBOM + `license-compliance`.

---
## 8. CI/CD PIPELINE TEMPLATE (GITHUB ACTIONS)
```yaml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: {python-version: '3.12'}
    - run: pip install poetry && poetry install --with dev
    - run: poetry run pytest --cov=project --cov-report=xml
    - run: poetry run mutmut run --paths-to-mutate project/ --runner "pytest -q"
    - run: poetry run bandit -r project -ll
    - name: ETHIK
      run: python scripts/ethik_validator.py --ci
```
Set branch protection: tests + mutation + bandit + ethik all green.

---
## 9. TEST PYRAMID & EXECUTION STRATEGY
```
        E2E (UI)
     Integration / CDC
 Unit / Property / Mutation
```
*Keep pyramid healthy*: unit ≫ integration ≫ e2e in count & runtime.

---
## 10. METRICS & FEEDBACK LOOPS
• Coverage %, Mutation %, MTTR to test fail, Ethical violation count  
• Expose metrics to Mycelium dashboard; add Grafana alerts if mutation < threshold.

---
## 11. AI-AUGMENTED TEST GENERATION
* EVA & GPT-4o suggest missing edge tests after diff  
* `scripts/eva_suggest_tests.py <commit_sha>`  
* Developer reviews suggestions before commit.

---
## 12. SAFETY & ROLLBACK PLAYBOOK
1. Always `git tag pre-refactor-<date>` before large change.  
2. If test coverage drops >5 %, block merge.  
3. Failed deploy → auto rollback to last green tag.

---
## 13. CONTINUOUS LEARNING
• Retro every sprint: inspect flaky tests, debt, false positives.  
• Upgrade toolchain quarterly (pytest, mutmut) and re-run mutation baseline.

---
## ANNEX – COMMAND CHEAT-SHEET
| Goal | Command |
|------|---------|
| Quick unit pass | `pytest -m unit -q` |
| Run mutation only new files | `mutmut run --changed-files` |
| Visual coverage | `coverage html && open htmlcov/index.html` |
| Dockerised tests | `docker compose run --rm sut pytest -q` |
| Pact publish | `pact-broker publish pacts/ --consumer App --version $GIT_SHA` |

---
### WORKFLOW META
* `// turbo` indicates optional safe auto-run; `// turbo-all` applies below its marker.  
* Keep file synced via `/dynamic_documentation_update_from_code_changes`.

---
## 14. QUANTUM PROMPT & PROMPTVAULT ALIGNMENT
When implementing complex algorithms or business rules, accompany the code with a **QuantumPrompt** (see `MQP.md`) capturing:
* Objective, constraints, key context snippets
* Ethical considerations & bias mitigations
* Tests-to-Prompt mapping (which test asserts which objective)
Save prompts under `PromptVault/` with metadata linking to the corresponding test file. Validate using `/distill_and_vault_prompt` workflow.

## 15. CROSS-WORKFLOW TOUCHPOINTS
| Phase | Supporting Workflow |
|-------|--------------------|
| Design for Testability | /ai_assisted_research_and_synthesis |
| Red→Green Loop | /iterative_code_refinement_cycle |
| Documentation Sync | /dynamic_documentation_update_from_code_changes |
| Ethics Validation   | /atrian_ethics_evaluation |
| Project Handover    | /project_handover_procedure |

Follow these to maintain systemic coherence.

---
## Cross-References & Related Workflows

- /iterative_code_refinement_cycle – Continuous improvements build on TDD foundations.
- /atrian_ethics_evaluation – Integrate ethics tests into TDD suites.
- /dynamic_documentation_update_from_code_changes – Document code & test changes automatically.
- /project_handover_procedure – Provide clean test coverage reports on handover.

*EOF*