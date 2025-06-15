---
description: "Five high-severity AI incidents – diagnostics & ATRiAN preventive patterns"
---

# Top-5 High-Severity AI Incidents (EGOS Case-Study Library)

These case studies illustrate how ATRiAN-powered governance could have predicted, detected, or mitigated critical failures across sectors. They serve as reusable patterns for simulation scenarios, KPI monitors, and ROI assumptions.

| ID | Title | Year | Sector | Severity | Core Failure | ATRiAN Early-Warning Signals | Preventive Controls |
|----|-------|------|--------|----------|--------------|-----------------------------|---------------------|
| 4 | Uber AV killed pedestrian in Arizona | 2018 | Mobility | Fatality (3) | Mis-classified object; safety driver distraction | Perception confusion-matrix deficit on "jaywalking at night"; sim logs → high brake latency; missing redundancy flag | Night-pedestrian CI tests; dual-sensor fusion; driver-alert monitoring |
| 12 | Robot kills worker at Volkswagen plant | 2015 | Manufacturing | Fatality (3) | Safety cage disabled; motion planner assumed empty cell | Config diff disabling lockouts; risk-matrix anomaly (human in restricted zone) | Dual-check override workflow; proximity sensors |
| 23 | Las Vegas autonomous shuttle bus accident | 2017 | Mobility | Injury risk (2) | Shuttle stopped but no reverse; edge-case truck manoeuvre | Simulation scenario "others violate right-of-way" uncovered no evasive path; KPI "evasion available" alarm | Add reverse capability; V2X messaging tests |
| 1 | YouTube Kids shows inappropriate content | 2017 | Media | Child harm (2) | Recommender surfaced violent/sexual videos to kids | Real-time toxicity classifier exceeded threshold; CTR spike on flagged content | Stricter policy tests; adversarial prompt generation; human escalation |
| 54 | PredPol predictive-policing bias | 2016 | Public Safety | Systemic discrimination (2) | Feedback loop targeting minorities | Fairness KPI regression; counterfactual disparity eval | Data re-weighting; socio-economic covariates; governance board review |

## Usage in Workflows

1. **Simulation Library** – Each incident is encoded as a scenario template in the safety-simulation engine.
2. **Severity-Aware ROI** – `severity_score` informs `risk_mitigation_perc` scaling in ROI Monte-Carlo runs.
3. **Prompt Distillation** – Use `/distill_and_vault_prompt` on these diagnostics to create reusable prompts for automated reviews.

## Cross-References

* `docs/workflows/atrian_data_pipeline_roi_workflow.md`
* `docs/methods/atrian_incident_analysis_methods.md`
* `.windsurf/workflows/atrian_roi_calc.md`
* `.windsurf/workflows/distill_and_vault_prompt.md`
