#!/usr/bin/env python3
"""validate_tool_registry.py

Thin wrapper to align naming convention for tool registry validation.

Cross-References:
    - .windsurfrules → (future) RULE-TOOLS-REGISTRY-VALIDATION
    - scripts/validation/tool_registry_validator.py (legacy implementation)
"""
# 
# @references:
#   - scripts/validation/validate_tool_registry.py
# 
from importlib import import_module
import sys

_impl = import_module("scripts.validation.tool_registry_validator")  # type: ignore

if __name__ == "__main__":
    if hasattr(_impl, "main"):
        sys.exit(_impl.main())  # type: ignore[arg-type]
    raise SystemExit("tool_registry_validator.py has no main() function")