---
title: EGOS Roadmap Synchronization Tool
description: This script synchronizes statuses between the main EGOS roadmap and local roadmaps,
ensuring consist...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Maintenance]
toc: true
---

# EGOS Roadmap Synchronization Tool

**Status**: INACTIVE

**Path**: `scripts/maintenance/roadmap_sync.py`

**Category**: Maintenance

**Maintainer**: EGOS Development Team

## Description

This script synchronizes statuses between the main EGOS roadmap and local roadmaps,
ensuring consistent task tracking across the project hierarchy.
It implements the principles defined in docs/governance/roadmap_hierarchy.md,
maintaining proper parent-child relationships between epics and stories.
Usage:
python roadmap_sync.py [--base-path PATH] [--update] [--report-file PATH]
Author: EGOS Development Team
Date: 2025-05-18
@references:
- C:\EGOS\docs_egos_processes\script_management\script_management_best_practices.md

