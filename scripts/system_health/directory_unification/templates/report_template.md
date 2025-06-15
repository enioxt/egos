@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - scripts/system_health/directory_unification/templates/report_template.md

# Directory Unification Report

**Keyword:** {{ keyword }}
**Timestamp:** {{ timestamp }}
**Output Directory:** {{ output_directory }}

## Summary
- Overall Success: {{ success }}
{% if error %}
- Error: 
  ```
  {{ error }}
  ```
{% endif %}
- Elapsed Time: {{ elapsed_time_total }} seconds

## Phases

{% for phase_name, phase_data in phases.items() %}
### {{ phase_name | capitalize }}
- Status: {{ phase_data.status }}
{% if phase_data.elapsed_time %}
- Elapsed Time: {{ phase_data.elapsed_time | round(2) }} seconds
{% endif %}
{% if phase_data.error %}
- Error:
  ```
  {{ phase_data.error }}
  ```
{% endif %}
{% if phase_data.output_file %}
- Output File: `{{ phase_data.output_file }}`
{% endif %}
{% endfor %}

## Content Discovery Details
```json
{{ content_discovery_json }}
```

## Cross-Reference Analysis Details
```json
{{ cross_reference_analysis_json }}
```

## Consolidation Plan Details
```json
{{ consolidation_plan_json }}
```