---
title: rich_progress_bar_quickref
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: rich_progress_bar_quickref
tags: [documentation]
---
---
title: rich_progress_bar_quickref
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
title: rich_progress_bar_quickref
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

<!-- 
@references:
- Core References:
  - <!-- TO_BE_REPLACED --> - Master Quantum Prompt defining EGOS principles
  - <!-- TO_BE_REPLACED --> - Project roadmap and planning
- Process Documentation:
  - <!-- TO_BE_REPLACED -->




# EGOS Rich Progress Bar Quick Reference

## Standard Progress Bar Implementation

```python
from rich.progress import Progress, BarColumn, TextColumn

with Progress(
    "[progress.description]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    "•",
    "[{task.completed}/{task.total}]"
) as progress:
    task = progress.add_task("Processing items", total=len(items))
    for item in items:
        # Process item
        progress.update(task, advance=1)
```

## Progress Bar with EGOS Console

```python
from egos_aesthetics import egos_console
from rich.progress import Progress, BarColumn

with Progress(
    "[progress.description]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    "•",
    "[{task.completed}/{task.total}]",
    console=egos_console.console
) as progress:
    # Add tasks and update as above
```

## Common Patterns

### File Processing

```python
task = progress.add_task(f"Processing {len(files)} files", total=len(files))
for file_path in files:
    # Process file
    progress.update(task, advance=1)
```

### Network Operations

```python
task = progress.add_task("Downloading data", total=len(urls))
for url in urls:
    # Make request
    progress.update(task, advance=1)
```

### Indeterminate Progress

```python
task = progress.add_task("Processing", total=None)
while not done:
    # Work
    progress.update(task)
```

### Multiple Tasks

```python
task1 = progress.add_task("Step 1", total=100)
task2 = progress.add_task("Step 2", total=50, visible=False)

# Complete task1 first
for i in range(100):
    # Work on task1
    progress.update(task1, advance=1)

# Then show and complete task2
progress.update(task2, visible=True)
for i in range(50):
    # Work on task2
    progress.update(task2, advance=1)
```

## Progress Columns Options

- `TextColumn("[progress.description]{task.description}")`
- `BarColumn(bar_width=None, style="bar.complete", complete_style="bar.complete")`
- `TaskProgressColumn()`
- `TimeRemainingColumn()`
- `TimeElapsedColumn()`
- `SpinnerColumn()`
- `FileSizeColumn()`

## Best Practices

1. Always provide accurate totals when possible
2. Use clear, descriptive task names
3. Handle exceptions within the progress context
4. Show elapsed/remaining time for long operations
5. Use subsystem-appropriate colors for progress bars

## Validation

Run the aesthetic validator to ensure proper implementation:

```bash
python scripts/maintenance/utils/validate_aesthetics.py -d path/to/check
```

✧༺❀༻∞ EGOS ∞༺❀༻✧




