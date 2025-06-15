---
title: Validator Report Templates
description: Jinja2 + WeasyPrint template guidelines for HTML/PDF outputs
status: Draft
---

@references:
  - docs/validator/REPORT_TEMPLATES.md

## Directory Layout
```
validator_reports/
  base_template.html.j2
  styles.css
  partials/
    summary.html.j2
    constitution_block.html.j2
```

## Jinja Blocks
* `{{ validation.overall_score }}`  
* Loop `validation.constitution_results.items()` to render per-constitution table.

## PDF Generation (CLI)
```bash
weasyprint render.html report.pdf
```