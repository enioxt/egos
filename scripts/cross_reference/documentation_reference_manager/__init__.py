"""EGOS Documentation Reference Manager
===================================

A system for managing cross-references within the EGOS documentation ecosystem.
Implements the principle that "no file exists in isolation" by creating and
maintaining a mycelium-like interconnection structure across all documentation files.

This package provides tools to:
- Scan documentation files
- Extract existing references
- Analyze potential new connections
- Add suggested cross-references
- Generate reports on the reference structure

Version: 1.0.0

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

from pathlib import Path
import os

# Package metadata
__version__ = "1.0.0"
__author__ = "EGOS Development Team"

# Package directory structure
PACKAGE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))