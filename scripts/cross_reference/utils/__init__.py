"""Cross-Reference System Utilities Package

This package provides utility modules for the EGOS Cross-Reference System.

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

from .serialization import (
    EGOSJSONEncoder,
    serialize_to_json,
    save_json_file,
    load_json_file,
    format_colored,
    COLORS
)

__all__ = [
    'EGOSJSONEncoder',
    'serialize_to_json',
    'save_json_file',
    'load_json_file',
    'format_colored',
    'COLORS'
]