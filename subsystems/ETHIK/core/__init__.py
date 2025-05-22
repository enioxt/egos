

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# subsystems/ETHIK/core/__init__.py
"""Core components for ETHIK subsystem, including validation and sanitization logic."""

from .sanitizer import EthikSanitizer
from .validator import EthikValidator

# from .rules import load_rules? TBD

__all__ = ["EthikSanitizer", "EthikValidator"]
