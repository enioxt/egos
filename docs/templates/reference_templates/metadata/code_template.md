---
title: code_template
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: code_template
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/templates/reference_templates/metadata/code_template.md

---
title: code_template
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
title: Code File Metadata Template
version: 1.0.0
status: Active
date_created: 2025-05-06
date_modified: 2025-05-06
authors: [Cascade]
description: Standard metadata template for Python code files in the EGOS project
file_type: template
scope: project-wide
primary_entity_type: template
primary_entity_name: code_metadata
tags: [template, metadata, code, standards, python]
depends_on:
  - docs/core/principles/cross_reference_guidelines.md
related_to:
  - docs/templates/metadata/documentation_template.md
---

# Code File Metadata Template

## Python Files

```python
"""
title: [Clear, descriptive title]
version: [Semantic version X.Y.Z]
status: [Active/Draft/Review/Archived]
date_created: [YYYY-MM-DD]
date_modified: [YYYY-MM-DD]
authors: [List of authors]
description: [Clear, concise description]
file_type: code
scope: [project-wide/subsystem/component]
primary_entity_type: [module/class/utility/script]
primary_entity_name: [specific identifier]
tags: [relevant, tags, in, snake_case]
depends_on: [List of files this depends on]
related_to: [List of related files]
"""

# Standard imports
import sys
import os
from typing import List, Dict, Any, Optional

# Third-party imports
# ...

# EGOS imports
# ...

# Constants
# ...

# Code implementation
# ...
```

## JavaScript/TypeScript Files

```javascript
/**
 * title: [Clear, descriptive title]
 * version: [Semantic version X.Y.Z]
 * status: [Active/Draft/Review/Archived]
 * date_created: [YYYY-MM-DD]
 * date_modified: [YYYY-MM-DD]
 * authors: [List of authors]
 * description: [Clear, concise description]
 * file_type: code
 * scope: [project-wide/subsystem/component]
 * primary_entity_type: [module/class/utility/script]
 * primary_entity_name: [specific identifier]
 * tags: [relevant, tags, in, snake_case]
 * depends_on: [List of files this depends on]
 * related_to: [List of related files]
 */

// Standard imports
// ...

// Third-party imports
// ...

// EGOS imports
// ...

// Constants
// ...

// Code implementation
// ...
```

## Usage Guidelines

1. Place metadata block at the top of the file as a docstring/comment
2. Organize imports in the standard order shown
3. Use relative paths for file references
4. Keep tags concise and in snake_case
5. Update date_modified when changing content
6. Maintain semantic versioning
7. Include type hints in Python code

## Examples

### Python Module

```python
"""
title: KOIOS Documentation Parser
version: 1.2.0
status: Active
date_created: 2025-01-15
date_modified: 2025-05-06
authors: [Cascade, Team]
description: Parser for KOIOS documentation files
file_type: code
scope: subsystem
primary_entity_type: module
primary_entity_name: doc_parser
tags: [koios, parser, documentation, utility]
depends_on:
  - scripts/utilities/file_utils.py
related_to:
  - scripts/subsystems/KOIOS/doc_generator.py
"""

import os
import re
from typing import Dict, List, Optional

from egos.utilities.file_utils import read_file, write_file

# Implementation...
```

### JavaScript Component

```javascript
/**
 * title: Dashboard Data Visualizer
 * version: 0.9.0
 * status: Active
 * date_created: 2025-03-10
 * date_modified: 2025-05-06
 * authors: [Cascade, Team]
 * description: Component for visualizing EGOS dashboard data
 * file_type: code
 * scope: application
 * primary_entity_type: component
 * primary_entity_name: data_visualizer
 * tags: [dashboard, visualization, component, react]
 * depends_on:
 *   - scripts/apps/dashboard/data_fetcher.js
 * related_to:
 *   - scripts/apps/dashboard/chart_components.js
 */

import React, { useState, useEffect } from 'react';
import { fetchData } from '../utils/data_fetcher';

// Implementation...
```

✧༺❀༻∞ EGOS ∞༺❀༻✧