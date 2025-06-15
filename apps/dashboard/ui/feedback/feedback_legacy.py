"""
TODO: Module docstring for feedback.py

@references:
- Core References:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

"""
feedback.py
Module for collecting and managing beta tester feedback for the EGOS MVP.
"""

from datetime import datetime
import os

import streamlit as st


def feedback_form():
    """Streamlit feedback form. Stores feedback in feedback_log.txt (dashboard/)."""
    st.header("Beta Feedback")
    name = st.text_input("Name (optional)")
    feedback = st.text_area("Your feedback or suggestions:")
    if st.button("Submit Feedback"):
        if feedback.strip():
            # Save feedback to file
            log_path = os.path.join(os.path.dirname(__file__), "feedback_log.txt")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {name} | {feedback}\n")
            st.success("Thank you for your feedback!")
        else:
            st.warning("Please enter some feedback before submitting.")


if __name__ == "__main__":
    feedback_form()