---
title: Optimized File Reference Checker (Version 1.1.0)
description: This script identifies files modified within a configurable time window (e.g., last N hours)
and the...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Cross-Reference]
toc: true
---

# Optimized File Reference Checker (Version 1.1.0)

**Status**: INACTIVE

**Path**: `scripts/cross_reference/file_reference_checker_optimized.py`

**Category**: Cross-Reference

**Maintainer**: EGOS Development Team

## Description

This script identifies files modified within a configurable time window (e.g., last N hours)
and then searches for references to these files across specified project directories
and file types. It generates timestamped Markdown and JSON reports detailing each
modified file and any cross-references found (or a warning if none are found).
Key Features:
- Scans for recently modified files based on a configurable time window.
- Searches for references to these files using configurable patterns, paths, and file types.
- Generates comprehensive Markdown and JSON reports.
- Archives reports with timestamps to prevent overwriting.
- Implements an automatic report retention policy to manage storage by deleting old reports.
- Highly configurable via 'config.yaml'.
This version enhances the original checker by adding robust reference searching,
detailed reporting including reference locations, and automated report archival/retention.
Author: EGOS Development Team (with Cascade AI)
Date: 2025-05-19 (Last Update)
Version: 1.1.0
Cross-References:
- Original Script: ../file_reference_checker.py (if applicable)
- Configuration: ./config.yaml (relative to script)
- Example Reports: ./file_reference_report_YYYYMMDD_HHMMSS.md / .json
- Main Documentation: ../../../docs/reference/file_reference_checker_optimized.md (to be created/updated)
@references:
- C:\EGOS\docs_egos_processes\script_management\script_management_best_practices.md

