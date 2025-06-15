"""
TODO: Module docstring for feedback_report.py

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
feedback_report.py
Automated reporting for beta feedback, with summary and visualization.
"""

from collections import Counter
import os
import random  # For simulation

import pandas as pd
import streamlit as st

# Attempt to import WordCloud, handle if not installed
try:
    from wordcloud import WordCloud

    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False


def generate_feedback_report(log_path=None):
    """
    Generate a report from feedback data.

    This function parses feedback_log.txt, summarizes feedback data,
    simulates tags and votes, and visualizes trends in the feedback.
    It includes a 'Top Feedback' section and handles potential file
    errors and missing libraries gracefully.

    Args:
        log_path: Optional path to the feedback log file. If None,
                 uses the default path in the dashboard directory.

    """
    if log_path is None:
        log_path = os.path.join(os.path.dirname(__file__), "feedback_log.txt")

    if not os.path.exists(log_path):
        st.info("No feedback submitted yet (feedback_log.txt not found).")
        return

    try:
        with open(log_path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        st.error(f"Error reading feedback log: {e}")
        return

    if not lines:
        st.info("Feedback log is empty.")
        return

    # Attempt to parse, handle potential errors
    data = []
    possible_tags = [
        "UI/UX",
        "Bug",
        "Feature Request",
        "Docs",
        "Performance",
        "Suggestion",
        "Praise",
    ]
    for i, line in enumerate(lines):
        parts = line.split("|", 2)
        if len(parts) == 3:
            # Simulate tags and upvotes
            num_tags = random.randint(0, 2)
            sim_tags = random.sample(possible_tags, k=num_tags) if num_tags > 0 else []
            sim_upvotes = random.randint(0, 25)
            data.append(
                {
                    "timestamp": parts[0],
                    "name": parts[1],
                    "feedback": parts[2],
                    "tags (sim)": ", ".join(sim_tags),
                    "upvotes (sim)": sim_upvotes,
                },
            )
        else:
            st.warning(f"Skipping malformed feedback entry (line {i + 1}): {line}")

    if not data:
        st.info("No valid feedback entries found after parsing.")
        return

    df = pd.DataFrame(data)
    # Convert timestamp string to datetime if possible for sorting, handle errors
    try:
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    except Exception:
        df["timestamp_dt"] = None  # Assign None if conversion fails broadly

    st.subheader("Feedback Summary")
    st.write(f"Total valid feedback entries: {len(df)}")

    # Display Top Feedback (Simulated)
    st.subheader(" Top Feedback (Simulated Ranking)")
    top_feedback = df.sort_values(by="upvotes (sim)", ascending=False).head(5)
    # Display specific columns, maybe add timestamp if available
    display_cols = ["feedback", "tags (sim)", "upvotes (sim)"]
    if "timestamp_dt" in top_feedback.columns and not top_feedback["timestamp_dt"].isnull().all():
        display_cols.insert(0, "timestamp_dt")  # Add timestamp if valid
        top_feedback["timestamp_dt"] = top_feedback["timestamp_dt"].dt.strftime(
            "%Y-%m-%d %H:%M",
        )  # Format for display

    st.dataframe(top_feedback[display_cols], use_container_width=True)
    st.caption("Ranking based on simulated upvotes. [TODO] Implement real tagging/voting.")

    st.subheader("")
    # Sort by actual timestamp if possible, otherwise use original order (tail)
    if "timestamp_dt" in df.columns and not df["timestamp_dt"].isnull().all():
        recent_feedback = df.sort_values(by="timestamp_dt", ascending=False).head(10)
    else:
        recent_feedback = df.tail(10)
    st.dataframe(
        recent_feedback,
        use_container_width=True,
    )

    # Word frequency analysis
    st.subheader("")
    all_feedback_text = " ".join(df["feedback"].astype(str).tolist())
    if all_feedback_text.strip():
        words = all_feedback_text.lower().split()
        # Simple stop word removal (extend as needed)
        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "it",
            "and",
            "to",
            "in",
            "of",
            "this",
            "that",
            "i",
            "you",
            "for",
            "with",
            "be",
            "was",
            "are",
            "as",
            "at",
            "so",
            "if",
            "or",
            "but",
            "not",
        }
        words = [
            word for word in words if word.isalnum() and word not in stop_words and len(word) > 1
        ]
        word_counts = Counter(words)

        if word_counts:
            st.write("**Most Common Words:**")
            st.write(word_counts.most_common(15))

            # Word cloud
            if WORDCLOUD_AVAILABLE:
                try:
                    wc = WordCloud(
                        width=700,
                        height=350,
                        background_color="#FFFFFF",
                        colormap="viridis",
                    ).generate(" ".join(words))
                    st.image(wc.to_array(), caption="Feedback Word Cloud")
                except ValueError:
                    st.warning("Could not generate word cloud (perhaps too few unique words?).")
            else:
                st.warning(
                    "WordCloud library not installed. Cannot generate word cloud. `pip install wordcloud`",
                )
        else:
            st.info("No significant words found after filtering.")
    else:
        st.info("Not enough text content in feedback to generate word analysis.")


# Example usage (optional, for direct script testing)
# if __name__ == "__main__":
#     # Create a dummy feedback log for testing
#     dummy_log = "feedback_log_test.txt"
#     with open(dummy_log, "w", encoding="utf-8") as f:
#         f.write("2025-04-18 10:00:00|Tester1|Great UI! Love the colors.\n")
#         f.write("2025-04-18 10:05:00|Tester2|Found a bug in the filter.\n")
#         f.write("2025-04-18 10:15:00|Tester1|Suggestion: Add dark mode.\n")
#         f.write("Malformed line\n")
#         f.write("2025-04-18 10:20:00|Tester3|The timeline chart is confusing.\n")

#     st.set_page_config(layout="wide")
#     st.title("Feedback Report Test")
#     generate_feedback_report(log_path=dummy_log)
#     os.remove(dummy_log) # Clean up dummy file