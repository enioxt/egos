#!/usr/bin/env python
"""EGOS Documentation Cross-Reference Manager
=========================================

Command-line tool for managing cross-references in EGOS documentation.
This script serves as a convenient entry point to the documentation_reference_manager package.

Usage:
    python manage_documentation_references.py --base-path <path> [options]

For detailed help:
    python manage_documentation_references.py --help

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - subsystems/AutoCrossRef/CROSSREF_STANDARD.md

import sys
from cross_reference.documentation_reference_manager.cli import main

if __name__ == "__main__":
    sys.exit(main())