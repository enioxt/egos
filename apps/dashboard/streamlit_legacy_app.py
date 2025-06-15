#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""streamlit_app.py

EGOS Dashboard for visualizing SPARC task flows, LLM interactions,
Mycelium messages, and system status.

Provides a real-time view into the EGOS system's operations and allows
for user feedback submission.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Dashboard Components:
  - [feedback.py](mdc:./feedback.py)
  - [feedback_report.py](mdc:./feedback_report.py)
  - [mycelium_client.py](mdc:./mycelium_client.py)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# EGOS Import Resilience block removed/commented out for package-based imports
# import sys
# from pathlib import Path
# project_root = str(Path(__file__).resolve().parents[1])
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import time
import random
import asyncio
import logging
from datetime import datetime, timezone
import uuid

# Import local dashboard components
from .ui.feedback.feedback_legacy import feedback_form
from .ui.feedback.feedback_report_legacy import generate_feedback_report
from .integrations.mycelium.mycelium_client_legacy import MyceliumClient # Import the client

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Use INFO for production, DEBUG for dev
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard")
logger.info("Dashboard Logger initialized.")

# --- Constants & Configuration ---
SPARC_TASK_TOPIC = "egos.sparc.tasks" # Example NATS topic
LLM_LOG_TOPIC = "egos.llm.logs" # Example NATS topic for LLM logs
PROPAGATION_TOPIC = "egos.propagation.log" # Example NATS topic for propagation
MAX_LIVE_ITEMS = 50 # Max number of live items to keep in state
HEARTBEAT_INTERVAL = 60 # Seconds for sidebar heartbeat update

# --- Session State Initialization ---
def initialize_session_state():
    """Initialize required session state variables."""
    defaults = {
        'nats_connected': False,
        'nats_subscribed': False,
        'live_data_active': False,
        'live_sparc_tasks': [],
        'live_llm_logs': [],
        'live_propagation_log': [],
        'last_heartbeat_check': 0,
        'system_heartbeat': '⚪'
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    logger.debug("Session state initialized/verified.")

# --- Data Simulation (Keep for fallback/comparison) ---
def simulate_sparc_tasks():
    """Simulate fetching tasks with timestamps."""
    return pd.DataFrame([
        {"id": 1, "type": "sparc_analyze", "status": "completed", "result": "No issues found.", "timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(minutes=10)},
        {"id": 2, "type": "sparc_refactor", "status": "in_progress", "result": None, "timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(minutes=5)},
        {"id": 3, "type": "sparc_analyze", "status": "failed", "result": "Syntax error.", "timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(minutes=2)},
        {"id": 4, "type": "sparc_generate", "status": "completed", "result": "Generated code stub.", "timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(minutes=15)},
    ])

def simulate_llm_logs():
    """Simulate LLM logs."""
    return [
        {"timestamp": datetime.now(timezone.utc).strftime('%H:%M:%S'), "model": "gpt-4o", "prompt": "Analyze code", "response": "Looks good.", "trace_id": str(uuid.uuid4())},
        {"timestamp": datetime.now(timezone.utc).strftime('%H:%M:%S'), "model": "claude-3-opus", "prompt": "Refactor function", "response": "Refactored successfully.", "trace_id": str(uuid.uuid4())},
    ]

def simulate_propagation_log():
    """Simulate log of pattern adoption."""
    return pd.DataFrame([
        {"timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(days=1), "subsystem": "ETHIK", "pattern": "Context Logging", "status": "Adopted"},
        {"timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(hours=2), "subsystem": "CORUJA", "pattern": "Modular Visualization", "status": "Proposed"},
        {"timestamp": pd.Timestamp.now(timezone.utc) - pd.Timedelta(minutes=30), "subsystem": "KOIOS", "pattern": "Automated Reporting", "status": "Adopted"},
    ]).sort_values(by="timestamp", ascending=False)

# --- NATS Client Management & Callbacks ---

@st.cache_resource
def get_mycelium_client():
    """Get or create the MyceliumClient instance."""
    logger.debug("Accessing/Creating MyceliumClient instance.")
    return MyceliumClient()

def _add_live_data(state_key, data, max_items=MAX_LIVE_ITEMS):
    """Helper to add data to a session state list and trim it."""
    if state_key not in st.session_state:
        st.session_state[state_key] = []
    st.session_state[state_key].insert(0, data) # Add to the beginning
    st.session_state[state_key] = st.session_state[state_key][:max_items]
    logger.debug(f"Updated {state_key}. Count: {len(st.session_state[state_key])}")
    st.rerun() # Trigger rerun to update UI

async def handle_sparc_message(subject, data):
    """Callback to process incoming SPARC task messages."""
    logger.debug(f"Received SPARC message on subject '{subject}': {data}")
    if isinstance(data, dict) and all(k in data for k in ['id', 'type', 'status']):
        data['timestamp'] = pd.Timestamp.now(timezone.utc)
        _add_live_data('live_sparc_tasks', data)
    else:
        logger.warning(f"Received malformed SPARC message: {data}")

async def handle_llm_message(subject, data):
    """Callback to process incoming LLM log messages."""
    logger.debug(f"Received LLM message on subject '{subject}': {data}")
    if isinstance(data, dict):
        data['timestamp'] = datetime.now(timezone.utc).strftime('%H:%M:%S')
        _add_live_data('live_llm_logs', data)
    else:
        logger.warning(f"Received malformed LLM message: {data}")

async def handle_propagation_message(subject, data):
    """Callback to process incoming propagation log messages."""
    logger.debug(f"Received Propagation message on subject '{subject}': {data}")
    if isinstance(data, dict):
        data['timestamp'] = pd.Timestamp.now(timezone.utc)
        _add_live_data('live_propagation_log', data)
    else:
        logger.warning(f"Received malformed Propagation message: {data}")

async def manage_nats_connection(client, live_data_flag):
    """Connect or disconnect NATS based on the live_data flag."""
    logger.debug(f"manage_nats_connection: live={live_data_flag}, connected={client.is_connected}")
    needs_rerun = False
    if live_data_flag and not client.is_connected:
        logger.info("Attempting to connect to NATS...")
        connected = await client.connect()
        if connected:
            logger.info("NATS connected. Subscribing...")
            st.session_state.nats_connected = True
            await client.subscribe(SPARC_TASK_TOPIC, handle_sparc_message)
            await client.subscribe(LLM_LOG_TOPIC, handle_llm_message)
            await client.subscribe(PROPAGATION_TOPIC, handle_propagation_message)
            st.session_state.nats_subscribed = True
            logger.info("NATS subscriptions complete.")
            needs_rerun = True
        else:
            logger.error("NATS connection failed.")
            st.session_state.nats_connected = False
            st.session_state.nats_subscribed = False
            needs_rerun = True # Rerun to show disconnected state

    elif not live_data_flag and client.is_connected:
        logger.info("Disconnecting from NATS...")
        await client.close()
        logger.info("NATS disconnected.")
        st.session_state.nats_connected = False
        st.session_state.nats_subscribed = False
        needs_rerun = True

    if needs_rerun:
        st.rerun()

# --- UI Display Functions ---
def display_sidebar(client):
    """Display the sidebar content."""
    st.sidebar.title("EGOS Dashboard")
    st.sidebar.markdown("--- *System Status* ---")

    # Live Data Toggle
    live_data = st.sidebar.checkbox("Use Live Data", value=st.session_state.live_data_active, key="live_data_toggle")
    st.session_state.live_data_active = live_data

    # Connection Status
    conn_status_indicator = "🟢 Connected" if st.session_state.nats_connected else "🔴 Disconnected"
    if client.fallback_mode:
        conn_status_indicator += " (Fallback)"
    st.sidebar.write(f"NATS Status: {conn_status_indicator}")

    # Subscription Status
    sub_status = "Active" if st.session_state.nats_subscribed else "Inactive"
    st.sidebar.write(f"Subscriptions: {sub_status}")

    # Heartbeat
    now = time.time()
    if now - st.session_state.last_heartbeat_check > HEARTBEAT_INTERVAL:
        st.session_state.system_heartbeat = "🟢" if st.session_state.nats_connected else "⚪"
        st.session_state.last_heartbeat_check = now
    st.sidebar.write(f"System Heartbeat: {st.session_state.system_heartbeat}")

    st.sidebar.markdown("--- *Navigation* ---")
    page = st.sidebar.radio("Go to:", ["Dashboard", "Feedback"], key="navigation")
    return page, live_data

def display_sparc_tasks(live_data):
    """Display SPARC task information."""
    st.header("SPARC Task Flow")
    if live_data:
        st.write("Displaying Live SPARC tasks from Mycelium/NATS.")
        if not st.session_state.nats_connected:
            st.warning("Not connected to NATS. Showing last known or empty data.")
        tasks_df = pd.DataFrame(st.session_state.live_sparc_tasks)
    else:
        st.write("Displaying Simulated SPARC tasks.")
        tasks_df = simulate_sparc_tasks()

    if not tasks_df.empty:
        # Ensure columns exist, fill NaN for display
        required_cols = ['id', 'type', 'status', 'result', 'timestamp']
        for col in required_cols:
            if col not in tasks_df.columns:
                tasks_df[col] = None
        tasks_df = tasks_df[required_cols] # Order columns
        tasks_df['timestamp'] = pd.to_datetime(tasks_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        tasks_df.fillna('N/A', inplace=True)
        st.dataframe(tasks_df, use_container_width=True)
    else:
        st.info("No SPARC task data available.")

def display_llm_interactions(live_data):
    """Display LLM interaction logs."""
    st.header("LLM Interactions")
    if live_data:
        st.write("Displaying Live LLM interaction logs from Mycelium/NATS.")
        if not st.session_state.nats_connected:
            st.warning("Not connected to NATS. Showing last known or empty data.")
        llm_logs = st.session_state.live_llm_logs
    else:
        st.write("Displaying Simulated LLM interaction logs.")
        llm_logs = simulate_llm_logs()

    if llm_logs:
        for log in llm_logs:
            with st.expander(f"{log.get('timestamp', 'N/A')} - {log.get('model', 'Unknown Model')} - Prompt: {log.get('prompt', '')[:50]}..."):
                st.text(f"Prompt: {log.get('prompt', 'N/A')}")
                st.text(f"Response: {log.get('response', 'N/A')}")
                st.caption(f"Trace ID: {log.get('trace_id', 'N/A')}")
    else:
        st.info("No LLM interaction data available.")

def display_propagation_log(live_data):
    """Display the propagation log."""
    st.header("Knowledge Propagation Log")
    if live_data:
        st.write("Displaying Live propagation log from Mycelium/NATS.")
        if not st.session_state.nats_connected:
            st.warning("Not connected to NATS. Showing last known or empty data.")
        prop_df = pd.DataFrame(st.session_state.live_propagation_log)
    else:
        st.write("Displaying Simulated propagation log.")
        prop_df = simulate_propagation_log()

    if not prop_df.empty:
        required_cols = ['timestamp', 'subsystem', 'pattern', 'status']
        for col in required_cols:
            if col not in prop_df.columns:
                prop_df[col] = None
        prop_df = prop_df[required_cols]
        prop_df['timestamp'] = pd.to_datetime(prop_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        prop_df.fillna('N/A', inplace=True)
        st.dataframe(prop_df, use_container_width=True)
    else:
        st.info("No propagation log data available.")

# --- Main Application Logic ---
def main():
    """Main Streamlit application function."""
    st.set_page_config(layout="wide", page_title="EGOS Dashboard")
    logger.info("--- EGOS Dashboard Started ---")

    initialize_session_state()
    client = get_mycelium_client()

    page, live_data = display_sidebar(client)

    # Run NATS connection/disconnection logic asynchronously
    # This needs to be handled carefully in Streamlit's execution model
    # We trigger the async function but don't block the main thread
    # Note: Direct asyncio.run() inside Streamlit is tricky. 
    # MyceliumClient might need adaptation or use threading.
    # For now, let's assume MyceliumClient handles its async loop.
    # We just tell it what state we want.
    asyncio.run(manage_nats_connection(client, live_data)) 

    if page == "Dashboard":
        st.title("EGOS System Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            display_sparc_tasks(live_data)
        with col2:
            display_llm_interactions(live_data)

        display_propagation_log(live_data)

    elif page == "Feedback":
        st.title("User Feedback")
        feedback_form()
        st.markdown("---")
        st.header("Feedback Report")
        report_text = generate_feedback_report()
        st.markdown(report_text)

    logger.info("--- EGOS Dashboard Render Complete ---")

if __name__ == "__main__":
    main()