---
title: EGOS Docs Directory Fixer
description: This script addresses the issue of the old 'docs' directory reappearing after migration to 'docs_ego...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Cross-Reference]
toc: true
---

# EGOS Docs Directory Fixer

**Status**: INACTIVE

**Path**: `scripts/cross_reference/docs_directory_fixer.py`

**Category**: Cross-Reference

**Maintainer**: EGOS Development Team

## Description

This script addresses the issue of the old 'docs' directory reappearing after migration to 'docs_egos'.
It identifies references to the old directory, updates them to use the new directory structure,
Features:
- Identifies files to migrate, update, or delete
- Interactive conflict resolution with diff viewing
- Batch operations for handling multiple conflicts
- Reference path updating in migrated files
- Detailed logging and reporting
- Dry-run mode for safe testing
References:
- [EGOS Cross-Reference Standardization](../../docs_egos/05_development/standards/cross_reference_standard.md)
- [KOIOS Documentation Standards](../../docs_egos/02_koios_standards/documentation_standards.md)
Author: EGOS Development Team
Created: 2025-05-20
Version: 1.1.0
@references:
- C:\EGOS\docs_egos_processes\script_management\script_management_best_practices.md

