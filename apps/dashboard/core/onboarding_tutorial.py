# @references:
#   - apps/dashboard/core/onboarding_tutorial.py
# 
# C:/EGOS/apps/dashboard/core/onboarding_tutorial.py
"""
EGOS Dashboard - Onboarding Tutorial

This module provides a user-friendly onboarding tutorial for the EGOS Dashboard.
"""

import streamlit as st

def display_onboarding_tutorial():
    """Displays the onboarding tutorial content using Streamlit components."""
    st.title("🚀 Welcome to the EGOS Dashboard!")
    st.markdown("This tutorial will guide you through the key features and functionalities.")

    st.markdown("---")

    # Step 1: Understanding the Layout
    with st.expander("Step 1: Understanding the Dashboard Layout", expanded=True):
        st.markdown("""
        The EGOS Dashboard is organized into several key sections, accessible via the **sidebar navigation** on the left:

        *   **📊 Dashboard**: Your main view for real-time system activity, including SPARC tasks, LLM interactions, and propagation logs.
        *   **🛡️ Ethical Governance**: Monitor key ethical metrics, DEV validation, ETHIK compliance, ATRiAN EaaS usage, and $ETHIK token activity. You can also visualize the ethical evaluation workflow here.
        *   **📝 Feedback**: Submit your feedback or suggestions about the EGOS system or the dashboard itself.
        *   **🚀 Onboarding Tutorial**: (You are here!) Revisit this guide anytime.
        """)
        st.info("**Tip:** Use the 'Use Live Data' checkbox in the sidebar to toggle between simulated and (when available) live data streams.")

    # Step 2: Exploring the Main Dashboard Page
    with st.expander("Step 2: Exploring the Main 'Dashboard' Page"):
        st.markdown("""
        The main 'Dashboard' page provides a snapshot of ongoing activities:

        *   **SPARC Tasks**: Shows the status and details of Self-Propagating Autonomous Responsible Chores (SPARCs).
        *   **LLM Interactions**: Logs interactions with Large Language Models within the EGOS ecosystem.
        *   **Propagation Log**: Tracks the flow of information and decisions through the system.
        
        These sections update in real-time if 'Use Live Data' is enabled and the NATS messaging system is connected.
        """)
        # Placeholder for a potential image or diagram
        # st.image("path/to/dashboard_overview_image.png", caption="Main Dashboard Overview") 

    # Step 3: Monitoring Ethical Governance
    with st.expander("Step 3: Monitoring Ethical Governance Metrics"):
        st.markdown("""
        The 'Ethical Governance' page is crucial for oversight:

        *   **DEV Validation Activity**: See the latest validations performed by the Distributed Ethical Validators.
        *   **ETHIK Compliance Scores**: Track how different system modules adhere to the ETHIK framework principles.
        *   **ATRiAN EaaS Usage**: Monitor the usage of the Ethics as a Service API.
        *   **$ETHIK Token Activity**: Get insights into the $ETHIK token's performance and distribution.
        *   **Ethical Evaluation Workflow**: Understand the steps involved in an ethical evaluation.
        """)

    # Step 4: Providing Feedback
    with st.expander("Step 4: Providing Feedback"):
        st.markdown("""
        Your input is valuable! Use the 'Feedback' page to:

        *   Submit detailed feedback on any aspect of EGOS.
        *   Report bugs or suggest improvements.
        *   View a consolidated report of feedback submitted (if configured).
        """)

    st.markdown("--- ")
    st.success("🎉 You've completed the onboarding tutorial! Feel free to explore the dashboard.")
    st.balloons()

if __name__ == '__main__':
    # This part is for testing the tutorial page independently if needed
    st.set_page_config(layout="wide")
    display_onboarding_tutorial()