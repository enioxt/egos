"""Main entry point for the Documentation Reference Manager.

This module allows the package to be executed directly with:
python -m documentation_reference_manager

It implements the principle of Universal Accessibility by providing
a simple entry point to the cross-reference management functionality.

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

from .cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())