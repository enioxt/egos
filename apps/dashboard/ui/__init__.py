"""EGOS Dashboard UI Package

This package exports core UI components for the EGOS dashboard.

It makes `feedback_form` from `feedback.py` and `generate_feedback_report`
from `feedback_report.py` available at the `ui` package level.

@references:
- Core References:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Attempt to import and expose key UI components
# This ensures that `from ui import feedback_form` works.

try:
    from .feedback_module import feedback_form  # Refers to ui/feedback_module.py
except ImportError as e_ff:
    print(f"INFO: Could not import feedback_form from ui.feedback_module: {e_ff}")
    # Define a fallback if needed, or let the error propagate if critical
    def feedback_form():
        import streamlit as st
        st.error("CRITICAL: Feedback form component failed to load.")
        print("ERROR: Fallback feedback_form called because import failed.")

try:
    from .feedback_report import generate_feedback_report # Refers to ui/feedback_report.py
except ImportError as e_fr:
    print(f"INFO: Could not import generate_feedback_report from ui.feedback_report: {e_fr}")
    # Define a fallback if needed
    def generate_feedback_report(*args, **kwargs):
        import streamlit as st
        st.error("CRITICAL: Feedback report component failed to load.")
        print("ERROR: Fallback generate_feedback_report called because import failed.")

__all__ = ['feedback_form', 'generate_feedback_report']