---
title: documentation_template
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: documentation_template
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/templates/reference_templates/metadata/documentation_template.md

---
title: documentation_template
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: Documentation Metadata Template
version: 1.0.0
status: Active
date_created: 2025-05-06
date_modified: 2025-05-06
authors: [Cascade]
description: Standard metadata template for documentation files in the EGOS project
file_type: template
scope: project-wide
primary_entity_type: template
primary_entity_name: documentation_metadata
tags: [template, metadata, documentation, standards]
depends_on:
  - docs/core/principles/cross_reference_guidelines.md
related_to:
  - docs/processes/reorganization/directory_mapping.md
---

# Documentation Metadata Template

## Required Fields

```yaml
---
title: [Clear, descriptive title]
version: [Semantic version X.Y.Z]
status: [Active/Draft/Review/Archived]
date_created: [YYYY-MM-DD]
date_modified: [YYYY-MM-DD]
authors: [List of authors]
description: [Clear, concise description]
file_type: [documentation/code/configuration/template]
scope: [project-wide/subsystem/component]
primary_entity_type: [process/component/subsystem/template]
primary_entity_name: [specific identifier]
tags: [relevant, tags, in, snake_case]
---
```

## Optional Fields

```yaml
depends_on: [List of files this depends on]
related_to: [List of related files]
supersedes: [List of files this replaces]
review_date: [YYYY-MM-DD]
review_cycle: [6 months/1 year/as needed]
security_classification: [public/internal/confidential]
compliance_standards: [List of compliance standards]
```

## Usage Guidelines

1. Place metadata block at the top of the file
2. Use relative paths for file references
3. Keep tags concise and in snake_case
4. Update date_modified when changing content
5. Maintain semantic versioning

## Examples

### Process Documentation
```yaml
---
title: Code Review Process
version: 1.0.0
status: Active
date_created: 2025-05-06
date_modified: 2025-05-06
authors: [Cascade]
description: Standard process for code review in EGOS
file_type: documentation
scope: project-wide
primary_entity_type: process
primary_entity_name: code_review
tags: [process, code_review, quality, standards]
depends_on:
  - docs/core/principles/development_standards.md
related_to:
  - docs/processes/quality/quality_gates.md
---
```

### Subsystem Documentation
```yaml
---
title: KOIOS Architecture Overview
version: 2.1.0
status: Active
date_created: 2025-01-15
date_modified: 2025-05-06
authors: [Cascade, Team]
description: Architectural overview of the KOIOS subsystem
file_type: documentation
scope: subsystem
primary_entity_type: subsystem
primary_entity_name: koios
tags: [architecture, koios, documentation]
depends_on:
  - docs/core/principles/architectural_principles.md
related_to:
  - docs/subsystems/KOIOS/api_reference.md
---
```

✧༺❀༻∞ EGOS ∞༺❀༻✧