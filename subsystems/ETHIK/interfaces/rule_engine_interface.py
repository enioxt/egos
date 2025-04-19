
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from abc import ABC, abstractmethod
from typing import Dict, Any

# Assuming ValidationRule is defined elsewhere (e.g., ETHIK core)
from ..core.validator import ValidationRule # Adjust import path as needed

class RuleEngineInterface(ABC):
            Methods:
            None
"""Interface for different ethical rule evaluation engines."""

    @abstractmethod
    def evaluate(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates a single rule against a given context.

        Args:
            rule: The ValidationRule to evaluate.
            context: The context dictionary against which conditions are checked.

        Returns:
            A dictionary representing the evaluation result for this rule,
            typically including keys like 'is_valid', 'score', 'details'.
        """
        pass
