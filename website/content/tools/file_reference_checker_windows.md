---
title: Cross-Reference Checker for Windows (Version 2.0.0)
description: This script identifies files modified within a configurable time window and searches for
references ...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Validation]
toc: true
---

# Cross-Reference Checker for Windows (Version 2.0.0)

**Status**: INACTIVE

**Path**: `scripts/cross_reference/zz_archive/obsolete_scripts/file_reference_checker_windows.py`

**Category**: Validation

**Maintainer**: EGOS Development Team

## Description

This script identifies files modified within a configurable time window and searches for
references to these files across specified project directories and file types.
It generates timestamped Markdown and JSON reports detailing cross-references.
Key Features:
- Windows-compatible (no SIGALRM dependency)
- Efficient file scanning with robust exclusion patterns
- File size limits to prevent processing extremely large files
- Comprehensive reporting in Markdown and JSON formats
- Configurable via 'config.yaml'
Author: EGOS Development Team
Date: 2025-05-20
Version: 2.0.0
@references:
- Original Script: file_reference_checker_optimized.py
- Configuration: ./config.yaml
- C:\EGOS\docs_egos_processes\script_management\script_management_best_practices.md

