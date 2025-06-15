# ATRiAN Sector-Specific Rules

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
- ATRIAN/docs/methods/incident_analysis_methods.md
- ATRIAN/docs/case_studies/top_incidents.md
- docs/workflows/atrian_data_pipeline_roi_workflow.md
- scripts/roi_simulate.py
- .windsurf/workflows/atrian_roi_calc.md

## Overview

This directory contains sector-specific YAML rule configurations for the ATRiAN Ethics as a Service (EaaS) platform. These rule files define:

1. **Detectors**: Specialized components that monitor for specific ethical risks, anomalies, or incidents
2. **Integration Points**: How these detectors connect with systems, pipelines, and workflows
3. **ROI Factors**: Sector-specific parameters for ROI calculations, including risk mitigation multipliers

## Directory Structure

```
rules/
├── README.md                 # This file
├── mobility.yaml             # Rules for autonomous vehicles, transportation
├── manufacturing.yaml        # Rules for industrial robotics, factory automation
├── media.yaml                # Rules for content platforms, recommendation systems
├── public_safety.yaml        # Rules for predictive policing, risk assessment
└── [additional sectors]      # Future sector-specific rule files
```

## Rule File Format

Each YAML rule file follows a standardized format:

```yaml
---
# Metadata
# References and cross-references

detectors:
  detector_name:
    id: "sector-###"
    name: "Human-Readable Name"
    description: "Detailed description"
    severity: "critical|high|medium|low"
    operational_context: "when this should run"
    reference_incident_ids: [id1, id2]  # References to case studies
    
    parameters:
      # Detector-specific configuration parameters
      
    implementation:
      module: "atrian.detectors.sector.component"
      class: "DetectorClass"
      threshold_violation_action: "action_to_take"
      
    webhook_targets:
      - "target1"
      - "target2"

# Integration settings
integration:
  # System integration points
  
# ROI model factors
roi_factors:
  sector_risk_mitigation_multiplier: 1.X  # Sector-specific multiplier
  cost_severity_mapping:
    # Sector-specific cost factors
```

## Usage

### Loading Rules

Rules can be loaded using the ATRiAN Rules Engine:

```python
from atrian.rules import RuleEngine

# Load all rules for a specific sector
engine = RuleEngine()
engine.load_sector_rules("mobility")

# Or load specific detectors across sectors
engine.load_detectors(["mobility-001", "pubsafe-002"])
```

### ROI Simulation

The sector-specific ROI factors are automatically used by the `roi_simulate.py` script when running with the `--by-sector` flag:

```bash
python scripts/roi_simulate.py --model data/roi/models/atrian_roi_model.yaml --incidents_data data/roi/master_incidents.parquet --out results/roi_simulation.json --by-sector
```

## Extending Rule Files

To add a new sector or detector:

1. Create a new YAML file following the format above
2. Register any required detector implementations in `atrian.detectors.[sector]`
3. Update the corresponding test files in `tests/rules/`
4. Run verification tests: `pytest tests/rules/test_rule_loading.py`

## Cross-References

* `ATRIAN/docs/methods/incident_analysis_methods.md` - Methodology for incident analysis
* `ATRIAN/docs/case_studies/top_incidents.md` - Case studies referenced by rule detectors
* `.windsurf/workflows/atrian_roi_calc.md` - Workflow for ROI calculation using these rules
