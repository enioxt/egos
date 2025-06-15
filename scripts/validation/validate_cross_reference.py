#!/usr/bin/env python3
"""validate_cross_reference.py

Thin wrapper around the legacy `cross_reference_validator.py` so that all validators follow the
`validate_*.py` naming convention.

Cross-References:
    - .windsurfrules → (future) add RULE-XREF-VALIDATION once CI job is wired
    - scripts/validation/cross_reference_validator.py (legacy implementation)
    - scripts/validation/validate_directory_structure.py (related structural check)
"""
# 
# @references:
#   - scripts/validation/validate_cross_reference.py
# 
from importlib import import_module
import sys

_impl = import_module("scripts.validation.cross_reference_validator")  # type: ignore

if __name__ == "__main__":
    # delegate to legacy main if present
    if hasattr(_impl, "main"):
        sys.exit(_impl.main())  # type: ignore[arg-type]
    raise SystemExit("cross_reference_validator.py has no main() function")