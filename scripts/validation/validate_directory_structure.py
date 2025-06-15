#!/usr/bin/env python3
"""validate_directory_structure.py

Thin wrapper so that directory structure validation aligns with the `validate_*` naming convention.

Cross-References:
    - .windsurfrules → (future) RULE-FS-STRUCTURE-VALIDATION
    - scripts/validation/directory_structure_validator.py (legacy implementation)
    - scripts/validation/validate_cross_reference.py (related consistency check)
"""
# 
# @references:
#   - scripts/validation/validate_directory_structure.py
# 
from importlib import import_module
import sys

_impl = import_module("scripts.validation.directory_structure_validator")  # type: ignore

if __name__ == "__main__":
    if hasattr(_impl, "main"):
        sys.exit(_impl.main())  # type: ignore[arg-type]
    raise SystemExit("directory_structure_validator.py has no main() function")