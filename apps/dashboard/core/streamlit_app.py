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

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import logging
import json
import uuid
import time
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid

# Import local dashboard components with robust approach for direct execution or importing
import sys
import os
from pathlib import Path

# Define the dashboard base directory to ensure correct imports
DASHBOARD_DIR = Path(__file__).parent.parent  # C:\EGOS\apps\dashboard

# Add dashboard directory to system path if not already there
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))
    
# We'll import event_persister after logger is initialized

# EGOS Theming & Translation imports
from utils.theming import apply_theme
from utils.translations import get_translation, TRANSLATIONS

# Imports from the 'ui' package, relying on its __init__.py
try:
    from ui import feedback_form
except ImportError as e_ff_app:
    print(f"ERROR in streamlit_app.py: Failed to import feedback_form from ui: {e_ff_app}")
    def feedback_form(): # Fallback
        import streamlit as st
        st.error("App Critical: feedback_form could not be loaded.")
        return

try:
    from ui import generate_feedback_report
except ImportError as e_fr_app:
    print(f"ERROR in streamlit_app.py: Failed to import generate_feedback_report from ui: {e_fr_app}")
    def generate_feedback_report(*args, **kwargs): # Fallback
        import streamlit as st
        st.error("App Critical: generate_feedback_report could not be loaded.")
        return

# Importação de mycelium_client com tratamento de erro
try:
    from utils.diagnostic_mycelium import MyceliumClient
except ImportError:
    try:
        # Tentativa alternativa caso a localização seja diferente
        from utils import diagnostic_mycelium
        MyceliumClient = diagnostic_mycelium.MyceliumClient
    except (ImportError, AttributeError):
        # Classe placeholder se o módulo não for encontrado
        class MyceliumClient:
            """Placeholder para MyceliumClient se não for encontrado"""
            def __init__(self, *args, **kwargs):
                print("Aviso: Usando versão placeholder do MyceliumClient")

# Import da mesma pasta (core)
from core.onboarding_tutorial import display_onboarding_tutorial

# Importando do módulo analytics
from analytics.ethical_metrics import (
    get_dev_validation_activity,
    get_ethik_compliance_scores,
    get_atrian_eaas_usage_metrics,
    get_ethik_token_activity
)

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
    """Initialize Streamlit session state variables."""
    # Application state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
        
    # Ensure data directory exists for event persistence
    data_dir = Path("C:/EGOS/data/events")
    data_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured event persistence directory exists at {data_dir}")
    
    defaults = {
        # Connection state
        'nats_connected': False,
        'nats_subscribed': False,
        'live_data_active': True,  # Default to ON as requested
        'connection_status': 'Disconnected ',
        'connection_color': 'gray',
        'connection_error': None,
        'connection_history': [],
        
        # Live data containers
        'live_sparc_tasks': [],
        'live_llm_logs': [],
        'live_propagation_log': [],
        
        # Heartbeat tracking
        'last_heartbeat_check': 0,
        'system_heartbeat': '',
        'last_heartbeat_time': datetime.now().strftime("%H:%M:%S"),
        
        # Connection metrics
        'connection_attempts': 0,
        'successful_connections': 0,
        'connection_failures': 0,
        'last_connection_time': None,
        'last_disconnection_time': None,
        
        # Data source indicator
        'using_synthetic_data': False,  # Flag to indicate if synthetic data is being used
        'event_loop_recovery_attempts': 0  # Track event loop recovery attempts
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    logger.debug("Session state initialized/verified with enhanced connection tracking.")
    
    # Initialize connection metrics if this is the first run
    if 'connection_metrics' not in st.session_state:
        st.session_state.connection_metrics = {
            'uptime_percentage': 0.0,
            'avg_connection_time': 0.0,
            'reconnection_count': 0,
            'stability_score': 100.0  # 100 is perfect stability
        }

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
    """Get or create the MyceliumClient instance with improved event loop handling."""
    logger.debug("Accessing/Creating MyceliumClient instance.")
    try:
        # Try to get a valid event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                logger.info("Creating new event loop for MyceliumClient")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            logger.info("No event loop for MyceliumClient, creating new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Create client with the valid loop
        return MyceliumClient(loop=loop)
    except Exception as e:
        logger.error(f"Error setting up MyceliumClient: {e}")
        # Fallback to default initialization
        return MyceliumClient()

def _add_live_data(state_key, data, max_items=MAX_LIVE_ITEMS, force_rerun=False):
    """Helper to add data to a session state list and trim it.
    
    Args:
        state_key: The session state key to update
        data: The data to add to the list
        max_items: Maximum number of items to keep in the list
        force_rerun: Whether to force a UI rerun (use sparingly)
    """
    if state_key not in st.session_state:
        st.session_state[state_key] = []
    st.session_state[state_key].insert(0, data) # Add to the beginning
    st.session_state[state_key] = st.session_state[state_key][:max_items]
    logger.debug(f"Updated {state_key}. Count: {len(st.session_state[state_key])}")
    
    # Only rerun if explicitly requested and not too frequent
    if force_rerun and _should_allow_rerun():
        try:
            logger.debug("Triggering manual UI rerun after data update")
            st.session_state.last_rerun_time = time.time()
            st.rerun()
        except Exception as e:
            logger.warning(f"Error during UI rerun after data update: {e}")

def _should_allow_rerun():
    """Check if enough time has passed since the last rerun to prevent infinite loops."""
    current_time = time.time()
    if 'last_rerun_time' not in st.session_state:
        st.session_state.last_rerun_time = 0
    if 'rerun_counter' not in st.session_state:
        st.session_state.rerun_counter = 0
    
    # Only allow reruns every 2 seconds (adjust as needed)
    min_interval = 2.0
    elapsed = current_time - st.session_state.last_rerun_time
    
    if elapsed < min_interval:
        logger.debug(f"Rerun throttled. Only {elapsed:.2f}s since last rerun (minimum: {min_interval}s)")
        return False
    
    # Increment counter for tracking
    st.session_state.rerun_counter += 1
    logger.debug(f"Allowing rerun #{st.session_state.rerun_counter}. Time since last: {elapsed:.2f}s")
    return True

# Import event persistence system for storing NATS events
try:
    from utils.event_persistence import event_persister
    print("Successfully imported event_persister for data persistence")
except ImportError as e_ep:
    print(f"ERROR in streamlit_app.py: Failed to import event_persister: {e_ep}")
    # Create a dummy event persister as fallback
    class DummyEventPersister:
        def store_event(self, *args, **kwargs):
            return False
    event_persister = DummyEventPersister()

async def handle_sparc_message(subject, data):
    """Callback to process incoming SPARC task messages."""
    logger.debug(f"Received SPARC message on subject '{subject}': {data}")
    if isinstance(data, dict) and all(k in data for k in ['id', 'type', 'status']):
        data['timestamp'] = pd.Timestamp.now(timezone.utc)
        # Add to session state for UI display
        _add_live_data('sparc_tasks', data, force_rerun=False)
        
        # Persist the event for future analysis
        event_persister.store_event(subject, data)
    else:
        logger.warning(f"Received malformed SPARC message: {data}")

async def handle_llm_message(subject, data):
    """Callback to process incoming LLM log messages."""
    logger.debug(f"Received LLM message on subject '{subject}': {data}")
    if isinstance(data, dict):
        data['timestamp'] = datetime.now(timezone.utc).strftime('%H:%M:%S')
        # Add to session state for UI display
        _add_live_data('llm_logs', data, force_rerun=False)
        
        # Persist the event for future analysis and auditing
        event_persister.store_event(subject, data)
    else:
        logger.warning(f"Received malformed LLM message: {data}")

async def handle_propagation_message(subject, data):
    """Callback to process incoming propagation log messages."""
    logger.debug(f"Received Propagation message on subject '{subject}': {data}")
    if isinstance(data, dict):
        data['timestamp'] = pd.Timestamp.now(timezone.utc)
        # Add to session state for UI display
        _add_live_data('propagation_events', data, force_rerun=False)
        
        # Persist the event for future analysis and historical tracking
        event_persister.store_event(subject, data)
    else:
        logger.warning(f"Received malformed Propagation message: {data}")

async def manage_nats_connection(client, live_data_flag):
    """Manage the NATS connection based on the live data flag with improved event loop handling.
    
    Args:
        client: The MyceliumClient instance.
        live_data_flag: Whether live data is enabled.
    """
    import traceback  # Import here to ensure it's available
    
    # Initialize connection history if not present
    if 'connection_history' not in st.session_state:
        st.session_state.connection_history = []
    
    # Add timestamp to connection history entries
    def add_connection_event(event):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {event}"
        st.session_state.connection_history.insert(0, entry)
        # Keep only the last 10 events
        if len(st.session_state.connection_history) > 10:
            st.session_state.connection_history = st.session_state.connection_history[:10]
    
    # Helper function to safely manage event loop state
    def get_or_create_event_loop():
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                logger.info("Detected closed event loop, creating a new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop
        except RuntimeError:
            # No event loop in current thread, create one
            logger.info("No event loop in current thread, creating a new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
                    
    # Determine connection state
    connected_attr = "is_connected" if hasattr(client, "is_connected") else "connected"
    is_connected = getattr(client, connected_attr, False)
    
    # Update session state with client connection status
    st.session_state.nats_connected = is_connected
    
    # Handle connection request
    if live_data_flag and not is_connected:
        try:
            # Ensure we have a valid event loop
            loop = get_or_create_event_loop()
            
            # Update UI to show connecting state
            st.session_state.connection_status = "Connecting... "
            st.session_state.connection_color = "orange"
            st.session_state.connection_error = None  # Clear any previous error messages
            add_connection_event("Connecting to NATS server...")
            
            # Attempt to force a UI update before connection attempt
            # Trigger a UI update if enough time has passed
            if _should_allow_rerun():
                try:
                    logger.debug("Triggering rerun after connection retry")
                    st.session_state.last_rerun_time = time.time()
                    st.rerun()
                except Exception:
                    pass  # Ignore rerun errors
            
            # Update connection metrics
            st.session_state.connection_attempts += 1
            
            # Connect with improved error handling
            logger.info(" Attempting to connect to NATS server...")
            
            # Use the loop we've verified/created
            if hasattr(client, 'loop') and client.loop != loop:
                logger.info("Updating client event loop to match current loop")
                client.loop = loop
                
            # The client.connect method already has its own retry logic with defaults
            # max_retries=3 and retry_delay=2, so we can call it directly
            connected = await client.connect()
            
            if connected:
                logger.info(" Successfully connected to NATS server")
                st.session_state.connection_status = "Connected "
                st.session_state.connection_color = "green"
                st.session_state.connection_error = None  # Clear any previous error messages
                add_connection_event("Successfully connected to NATS")
                
                # Subscribe to topics with improved error handling
                logger.info(" Setting up subscriptions...")
                subscription_results = []
                
                try:
                    await client.subscribe(SPARC_TASK_TOPIC, handle_sparc_message)
                    subscription_results.append(f" {SPARC_TASK_TOPIC}")
                except Exception as e:
                    logger.error(f"Failed to subscribe to {SPARC_TASK_TOPIC}: {e}")
                    subscription_results.append(f" {SPARC_TASK_TOPIC}: {str(e)[:50]}...")
                
                try:
                    await client.subscribe(LLM_LOG_TOPIC, handle_llm_message)
                    subscription_results.append(f" {LLM_LOG_TOPIC}")
                except Exception as e:
                    logger.error(f"Failed to subscribe to {LLM_LOG_TOPIC}: {e}")
                    subscription_results.append(f" {LLM_LOG_TOPIC}: {str(e)[:50]}...")
                
                try:
                    await client.subscribe(PROPAGATION_TOPIC, handle_propagation_message)
                    subscription_results.append(f" {PROPAGATION_TOPIC}")
                except Exception as e:
                    logger.error(f"Failed to subscribe to {PROPAGATION_TOPIC}: {e}")
                    subscription_results.append(f" {PROPAGATION_TOPIC}: {str(e)[:50]}...")
                
                # Update subscription status
                st.session_state.nats_subscribed = True
                add_connection_event(f"Subscriptions: {', '.join(subscription_results)}")
                logger.info(" Subscriptions complete")
            else:
                logger.error(" Failed to connect to NATS server")
                st.session_state.connection_status = "Disconnected "
                st.session_state.connection_color = "red"
                st.session_state.connection_error = "Could not establish connection to NATS server. Please check if the NATS server is running."
                add_connection_event("Failed to connect to NATS server")
        except Exception as e:
            error_message = str(e)
            logger.error(f" Error connecting to NATS: {error_message}")
            logger.error(traceback.format_exc())
            st.session_state.connection_status = "Disconnected "
            st.session_state.connection_color = "red"
            
            # Provide user-friendly error messages based on common error types
            if "connection refused" in error_message.lower():
                error_msg = "Connection refused. Please ensure the NATS server is running at the specified address."
                add_connection_event("Error: Connection refused")
            elif "timeout" in error_message.lower():
                error_msg = "Connection timed out. The NATS server might be overloaded or unreachable."
                add_connection_event("Error: Connection timeout")
            elif "authentication" in error_message.lower():
                error_msg = "Authentication failed. Please check your credentials."
                add_connection_event("Error: Authentication failed")
            elif "event loop is closed" in error_message.lower():
                # Create a new event loop and retry connection if needed
                try:
                    logger.warning("Event loop closed during connection, attempting recovery")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    st.session_state.event_loop_recovery_attempts += 1
                    
                    if st.session_state.event_loop_recovery_attempts <= 3:  # Limit recovery attempts
                        error_msg = "Event loop was closed. Attempting to recover connection..."
                        add_connection_event(f"Error: Event loop closed, recovery attempt #{st.session_state.event_loop_recovery_attempts}")
                    else:
                        error_msg = "Event loop closed repeatedly. Try refreshing the dashboard completely."
                        add_connection_event(f"Error: Event loop closed, max recovery attempts reached")
                except Exception as loop_err:
                    error_msg = f"Event loop error: {loop_err}. Try refreshing the dashboard."
                    add_connection_event(f"Error: Event loop recovery failed")
            else:
                error_msg = f"Connection error: {error_message}"
                add_connection_event(f"Error: {error_message[:50]}...")
                
            st.session_state.connection_error = error_msg
            
    # Handle disconnection request
    elif not live_data_flag and is_connected:
        try:
            # Ensure we have a valid event loop before disconnecting
            loop = get_or_create_event_loop()
            
            logger.info(" Disconnecting from NATS server...")
            add_connection_event("Disconnecting from NATS server...")
            
            # Update UI state
            st.session_state.connection_status = "Disconnecting... "
            st.session_state.connection_color = "orange"
            
            # Record disconnection time
            st.session_state.last_disconnection_time = datetime.now()
            
            # First try to unsubscribe from all topics to clean up
            if hasattr(client, "subscriptions") and client.subscriptions:
                for topic in list(client.subscriptions.keys()):
                    try:
                        logger.debug(f"Unsubscribing from {topic} before disconnect")
                        await client.unsubscribe(topic)
                    except Exception as unsub_err:
                        logger.warning(f"Error unsubscribing from {topic}: {unsub_err}")
            
            # Close connection with proper method and enhanced error handling
            if hasattr(client, "close"):
                try:
                    # Set a reasonable timeout for drain operation
                    await asyncio.wait_for(client.close(), timeout=5.0)
                    logger.info(" Successfully disconnected from NATS")
                    add_connection_event("Successfully disconnected from NATS")
                except asyncio.TimeoutError:
                    logger.warning("NATS disconnect timed out, forcing connection closure")
                    add_connection_event("Disconnect timed out, forcing closure")
                    # Even with timeout, consider it closed from UI perspective
                except Exception as e:
                    if "event loop is closed" in str(e).lower():
                        # Create a new event loop if needed
                        logger.warning("Event loop closed during disconnect, creating new one")
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        st.session_state.event_loop_recovery_attempts += 1
                        add_connection_event("Reset event loop during disconnect")
                        # Don't retry here, just record recovery attempt
                    else:
                        logger.warning(f" Warning during NATS disconnect: {e}")
                        logger.warning(traceback.format_exc())
                        add_connection_event(f"Warning during disconnect: {str(e)[:50]}...")
            else:
                # Fallback to disconnect method if close is not available
                try:
                    await client.disconnect()
                    add_connection_event("Disconnected using legacy method")
                except Exception as e:
                    logger.warning(f"Error during legacy disconnect: {e}")
                    add_connection_event(f"Legacy disconnect error: {str(e)[:50]}...")
                    # Still consider it disconnected for UI purposes
                
            logger.info(" NATS disconnection process completed.")
            
            # Update UI state
            st.session_state.connection_status = "Disconnected "
            st.session_state.connection_color = "gray"
            st.session_state.nats_connected = False
            st.session_state.nats_subscribed = False
            st.session_state.connection_error = None  # Clear any error messages
        except Exception as e:
            logger.error(f" Exception during NATS disconnection: {e}", exc_info=True)
            add_connection_event(f"Error during disconnect: {str(e)[:50]}...")
            
            # Still mark as disconnected even if there was an error
            st.session_state.connection_status = "Disconnected with errors "
            st.session_state.connection_color = "orange"
            st.session_state.nats_connected = False
            st.session_state.nats_subscribed = False
            st.session_state.connection_error = f"Disconnection warning: {str(e)}"
    
    # Update connection status if already connected but not reflected in UI
    elif live_data_flag and is_connected and st.session_state.connection_status != "Connected ":
        st.session_state.connection_status = "Connected "
        st.session_state.connection_color = "green"
        st.session_state.connection_error = None
        add_connection_event("Connection status synchronized")
    
    # Update synthetic data flag based on connection status
    st.session_state.using_synthetic_data = not (live_data_flag and is_connected)
    logger.debug(f"Updated synthetic data flag: {st.session_state.using_synthetic_data} (live_data={live_data_flag}, connected={is_connected})")
    
    # UI updates are now throttled to prevent infinite loops
    # All rerun calls use _should_allow_rerun() to prevent excessive refreshing

# --- UI Display Functions ---
def display_sidebar(client):
    """Display the sidebar content with enhanced connection status and error messages."""
    st.sidebar.title(get_translation("title"))
    
    # --- NAVIGATION SECTION (moved to top) ---
    # --- SETTINGS SECTION ---
    st.sidebar.markdown("---")
    st.sidebar.header(get_translation("settings_header"))

    # Language selector
    language_options = list(TRANSLATIONS.keys())
    language_display = {"en": "English", "pt": "Português"}
    selected_language_key = st.sidebar.selectbox(
        get_translation("language_select"),
        options=language_options,
        format_func=lambda code: language_display.get(code, code.upper()),
        index=language_options.index(st.session_state.language)
    )
    if selected_language_key != st.session_state.language:
        st.session_state.language = selected_language_key
        st.experimental_rerun()

    # Theme selector
    theme_options = ["light", "dark"]
    selected_theme_key = st.sidebar.radio(
        get_translation("theme_select_label"),
        options=theme_options,
        format_func=lambda t: t.capitalize(),
        index=theme_options.index(st.session_state.theme)
    )
    if selected_theme_key != st.session_state.theme:
        st.session_state.theme = selected_theme_key
        st.experimental_rerun()

    st.sidebar.markdown("--- *Navigation* ---")
    page_keys = ["Dashboard", "Incident Analysis", "Ethical Governance", "Feedback", "🚀 Onboarding Tutorial"]
    
    def _nav_label(key):
        mapping = {
            "Dashboard": get_translation("nav_dashboard"),
            "Incident Analysis": get_translation("nav_incident_analysis"),
            "Ethical Governance": get_translation("nav_ethical_governance"),
            "Feedback": get_translation("nav_feedback"),
            "🚀 Onboarding Tutorial": get_translation("nav_onboarding_tutorial"),
        }
        return mapping.get(key, key)

    page = st.sidebar.radio(
        get_translation("navigation_go_to_label"),
        options=page_keys,
        format_func=_nav_label,
        key="navigation"
    )
    
    st.sidebar.markdown("--- *System Status* ---")
    
    # Only the main banner will show the data mode status, removing sidebar warning
    
    # Live Data Toggle with improved status display
    previous_live_data_active = st.session_state.live_data_active
    
    # Connection Status with color coding
    if not hasattr(st.session_state, 'connection_status'):
        st.session_state.connection_status = "Disconnected "
        st.session_state.connection_color = "gray"
    
    status_color = st.session_state.get('connection_color', 'gray')
    
    # NATS status will be displayed on main page instead of sidebar
    
    # Live data toggle with current connection status context (moved before error display)
    current_checkbox_value = st.sidebar.checkbox(
        "Use Live Data", 
        value=st.session_state.live_data_active, 
        key="live_data_toggle",
        help="Toggle real-time data from NATS. Green status indicates successful connection."
    )
    
    # Display any connection errors
    if hasattr(st.session_state, 'connection_error') and st.session_state.connection_error:
        st.sidebar.error(st.session_state.connection_error)
        # Add a retry button if there's an error
        if st.sidebar.button("Retry Connection"):
            try:
                logger.info("Manual connection retry requested")
                st.session_state.connection_status = "Retrying... "
                st.session_state.connection_color = "blue"
                asyncio.run(client.reconnect())
                if _should_allow_rerun():
                    try:
                        logger.debug("Triggering rerun after manual retry")
                        st.session_state.last_rerun_time = time.time()
                        st.rerun()
                    except Exception as e:
                        logger.warning(f"Error during UI rerun after manual retry: {e}")
            except Exception as e:
                logger.error(f"Manual retry failed: {e}")
                if _should_allow_rerun():
                    try:
                        logger.debug("Triggering rerun after manual retry failure")
                        st.session_state.last_rerun_time = time.time()
                        st.rerun()
                    except Exception as e:
                        logger.warning(f"Error during UI rerun after manual retry failure: {e}")

    if previous_live_data_active != current_checkbox_value:
        # Set a new random seed whenever the toggle changes to ensure different synthetic data
        # This ensures users can visually confirm the mode change
        if not hasattr(st.session_state, 'synthetic_data_seed'):
            st.session_state.synthetic_data_seed = 42  # Initial seed
            
        # Generate new seed for synthetic data to ensure visual feedback when toggling
        st.session_state.synthetic_data_seed = random.randint(1, 10000)
        logger.info(f"Live data toggle changed - new synthetic data seed: {st.session_state.synthetic_data_seed}")
        
        st.session_state.live_data_active = current_checkbox_value # Update state first
        logger.info(f"Live data toggle changed from {previous_live_data_active} to {st.session_state.live_data_active}. Managing NATS connection.")
        try:
            # Ensure we have a valid event loop using our helper function
            def get_or_create_event_loop_for_toggle():
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        logger.info("Toggle: Detected closed event loop, creating a new one")
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    return loop
                except RuntimeError:
                    logger.info("Toggle: No event loop in current thread, creating a new one")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop
                    
            # Safe execution strategy with multiple fallbacks
            try:
                # First attempt: Use client's event loop if possible and running
                if hasattr(client, 'loop') and client.loop and not client.loop.is_closed():
                    logger.debug("Using client's running event loop for connection management")
                    client.loop.create_task(manage_nats_connection(client, st.session_state.live_data_active))
                    # Force rerun to update UI immediately
                    if _should_allow_rerun():
                        try:
                            logger.debug("Triggering rerun after connection management")
                            st.session_state.last_rerun_time = time.time()
                            st.rerun()
                        except Exception as e:
                            logger.warning(f"Error during UI rerun after connection management: {e}")
                    
                # Second attempt: Try asyncio.run (works in clean environment)
                else:
                    try:
                        asyncio.run(manage_nats_connection(client, st.session_state.live_data_active))
                        # Force rerun to update UI immediately
                        if _should_allow_rerun():
                            try:
                                logger.debug("Triggering rerun after connection management")
                                st.session_state.last_rerun_time = time.time()
                                st.rerun()
                            except Exception as e:
                                logger.warning(f"Error during UI rerun after connection management: {e}")
                    except RuntimeError as e:
                        # Third attempt: Already in an event loop, create task
                        if "cannot be called from a running event loop" in str(e):
                            logger.warning("Toggle: Already in an event loop, creating task")
                            loop = asyncio.get_event_loop()
                            loop.create_task(manage_nats_connection(client, st.session_state.live_data_active))
                            # Force rerun to update UI immediately
                            if _should_allow_rerun():
                                try:
                                    logger.debug("Triggering rerun after connection management")
                                    st.session_state.last_rerun_time = time.time()
                                    st.rerun()
                                except Exception as e:
                                    logger.warning(f"Error during UI rerun after connection management: {e}")
                            
                        # Fourth attempt: No event loop, create one
                        elif "There is no current event loop in thread" in str(e):
                            logger.warning("Toggle: No event loop, creating new one")
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(manage_nats_connection(client, st.session_state.live_data_active))
                                # Force rerun to update UI immediately
                                if _should_allow_rerun():
                                    try:
                                        logger.debug("Triggering rerun after connection management")
                                        st.session_state.last_rerun_time = time.time()
                                        st.rerun()
                                    except Exception as e:
                                        logger.warning(f"Error during UI rerun after connection management: {e}")
                            finally:
                                # Don't close the loop here as it might be needed later
                                pass
                                
                        # Fifth attempt: Other error, create fresh loop
                        else:
                            logger.error(f"Toggle: Unexpected error: {e}, attempting recovery")
                            try:
                                loop = get_or_create_event_loop_for_toggle()
                                asyncio.run_coroutine_threadsafe(manage_nats_connection(client, st.session_state.live_data_active), loop)
                                # Force a rerun to update all components immediately
                                if _should_allow_rerun():
                                    try:
                                        logger.debug("Triggering rerun after connection management")
                                        st.session_state.last_rerun_time = time.time()
                                        st.rerun()
                                    except Exception as e:
                                        logger.warning(f"Error during UI rerun after connection management: {e}")
                            except Exception as inner_e:
                                logger.error(f"Toggle: Final fallback failed: {inner_e}")
                                st.session_state.connection_error = f"Connection management error. Try refreshing the page."
            except Exception as outer_e:
                logger.error(f"Toggle: Outer execution error: {outer_e}")
                st.session_state.connection_error = f"Connection management error: {str(outer_e)[:100]}"
                
        except Exception as e:
            logger.error(f"Unexpected error in connection management: {e}", exc_info=True)
            st.session_state.connection_error = f"Connection error: {str(e)[:100]}"
            if _should_allow_rerun():
                try:
                    logger.debug("Triggering rerun after connection management error")
                    st.session_state.last_rerun_time = time.time()
                    st.rerun()
                except Exception as e:
                    logger.warning(f"Error during UI rerun after connection management error: {e}")

    live_data = st.session_state.live_data_active # Use the potentially updated state
    
    # Heartbeat with timestamp (moved above connection details)
    now = time.time()
    if now - st.session_state.last_heartbeat_check > HEARTBEAT_INTERVAL:
        st.session_state.system_heartbeat = "" if st.session_state.nats_connected else ""
        st.session_state.last_heartbeat_check = now
        st.session_state.last_heartbeat_time = datetime.now().strftime("%H:%M:%S")
    
    heartbeat_time = st.session_state.get('last_heartbeat_time', 'N/A')
    st.sidebar.write(f"System Heartbeat: {st.session_state.system_heartbeat} ({heartbeat_time})")
    
    # Connection details expander moved to bottom
    with st.sidebar.expander("Connection Details"):
        # Subscription Status
        sub_status = "Active" if st.session_state.nats_subscribed else "Inactive"
        st.write(f"Subscriptions: {sub_status}")
        
        # Show connected topics
        if st.session_state.nats_subscribed:
            topics = [SPARC_TASK_TOPIC, LLM_LOG_TOPIC, PROPAGATION_TOPIC]
            st.write("Active Topics:")
            for topic in topics:
                st.code(topic, language="text")
        
        # Fallback mode indicator
        if hasattr(client, 'fallback_mode') and client.fallback_mode:
            st.warning(" Running in fallback mode (no NATS)")
        
        # Connection history - store last 5 connection events
        if 'connection_history' not in st.session_state:
            st.session_state.connection_history = []
            
        # Display connection history
        if st.session_state.connection_history:
            st.write("Recent Connection Events:")
            for event in st.session_state.connection_history[-5:]:
                st.text(event)
    
    return page, live_data

def display_sparc_tasks(live_data):
    """Display SPARC task information."""
    st.header("SPARC Task Flow")
    
    # Determine if we're showing synthetic data
    is_synthetic = not (live_data and st.session_state.nats_connected)
    logger.debug(f"Display function using synthetic data: {is_synthetic} (live_data={live_data}, connected={st.session_state.nats_connected})")
    
    if is_synthetic:
        tasks_df = simulate_sparc_tasks()
    else:
        tasks_df = pd.DataFrame(st.session_state.live_sparc_tasks)
        
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
    
    # Determine if we're showing synthetic data
    is_synthetic = not (live_data and st.session_state.nats_connected)
    logger.debug(f"Display function using synthetic data: {is_synthetic} (live_data={live_data}, connected={st.session_state.nats_connected})")
    
    if is_synthetic:
        llm_logs = simulate_llm_logs()
    else:
        llm_logs = st.session_state.live_llm_logs
        
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
    
    # Determine if we're showing synthetic data
    is_synthetic = not (live_data and st.session_state.nats_connected)
    logger.debug(f"Display function using synthetic data: {is_synthetic} (live_data={live_data}, connected={st.session_state.nats_connected})")
    
    if is_synthetic:
        prop_df = simulate_propagation_log()
    else:
        prop_df = pd.DataFrame(st.session_state.live_propagation_log)
        
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

# --- UI Display Functions (Ethical Governance) ---
def display_ethical_governance_metrics(live_data):
    """Display ethical governance metrics."""
    st.title("🛡️ Ethical Governance Metrics")
    
    # Determine if we're showing synthetic data
    is_synthetic = not (live_data and st.session_state.nats_connected)
    logger.debug(f"Display function using synthetic data: {is_synthetic} (live_data={live_data}, connected={st.session_state.nats_connected})")
    
    # Log the data mode for debugging
    logger.info(f"Ethical Governance page using {'SYNTHETIC' if is_synthetic else 'LIVE'} data mode")
    logger.debug(f"NATS connected: {st.session_state.nats_connected}, Live data toggle: {live_data}")
    
    # Force synthetic mode if the toggle is off
    if not live_data:
        logger.info("Live data toggle is OFF - forcing synthetic data mode")
        is_synthetic = True
    else:
        # If live data toggle is ON but not connected, still force synthetic
        if not st.session_state.nats_connected:
            logger.warning("Live data toggle is ON but NATS is not connected - falling back to synthetic data")
            is_synthetic = True
        else:
            # If connected and live toggle is ON, force live mode (empty data)
            logger.info("Live data toggle is ON and NATS is connected - using LIVE data mode")
            is_synthetic = False
            
    # Show a clear indicator at the top of the page about data mode
    if not is_synthetic:
        # Não precisamos de mensagem duplicada aqui, pois já temos na tela principal
        pass
    else:
        st.warning("📊 **SYNTHETIC DATA MODE** - Showing simulated data for demonstration purposes.")
        
    # Store the current mode in session state for consistent behavior
    st.session_state.ethical_governance_using_synthetic = is_synthetic
    
    # Ensure we have a synthetic data seed for consistent behavior
    if not hasattr(st.session_state, 'synthetic_data_seed'):
        st.session_state.synthetic_data_seed = random.randint(1, 10000)
        logger.info(f"Created new synthetic data seed for Ethical Governance: {st.session_state.synthetic_data_seed}")

    # DEV Validation Activity
    with st.expander("Validators: Distributed Ethical Validator (DEV) Activity", expanded=True):
        st.markdown("#### DEV Validation Activity (Last 24h)")
        
        # Use a try-except block to handle potential parameter issues
        try:
            # Use synthetic or live data based on connection state
            # Pass the session's synthetic data seed to ensure consistent behavior
            if hasattr(st.session_state, 'synthetic_data_seed'):
                logger.debug(f"Using synthetic data seed for DEV activity: {st.session_state.synthetic_data_seed}")
                
            # Always pass synthetic=is_synthetic to ensure proper mode is used
            dev_activity_df = get_dev_validation_activity(synthetic=is_synthetic)
        except TypeError:
            # Fall back to calling without parameters if the synthetic parameter isn't supported
            try:
                dev_activity_df = get_dev_validation_activity()
            except Exception as e:
                st.error(f"Error fetching validation activity data: {str(e)}")
                dev_activity_df = pd.DataFrame()  # Empty dataframe as fallback
            
        if not dev_activity_df.empty:
            st.dataframe(dev_activity_df, use_container_width=True, height=300)
            st.metric("Total Validations (24h)", len(dev_activity_df))
        else:
            if not is_synthetic:
                st.warning("No live DEV validation data available yet. Live data integration is under development.")
            else:
                st.info("No DEV validation activity data available.")

    # ETHIK Framework Compliance
    with st.expander("Compliance: ETHIK Framework Scores", expanded=True):
        st.markdown("#### ETHIK Framework Compliance Scores")
        
        # Use a try-except block to handle potential parameter issues
        try:
            # Use synthetic or live data based on connection state
            # Pass the session's synthetic data seed to ensure consistent behavior
            if hasattr(st.session_state, 'synthetic_data_seed'):
                logger.debug(f"Using synthetic data seed for ETHIK scores: {st.session_state.synthetic_data_seed}")
                
            # Always pass synthetic=is_synthetic to ensure proper mode is used
            ethik_scores_df = get_ethik_compliance_scores(synthetic=is_synthetic)
        except TypeError:
            # Fall back to calling without parameters if the synthetic parameter isn't supported
            try:
                ethik_scores_df = get_ethik_compliance_scores()
            except Exception as e:
                st.error(f"Error fetching ETHIK compliance scores: {str(e)}")
                ethik_scores_df = pd.DataFrame()  # Empty dataframe as fallback
            
        if not ethik_scores_df.empty:
            st.dataframe(ethik_scores_df, use_container_width=True)
            if 'overall_compliance' in ethik_scores_df.columns:
                avg_compliance = ethik_scores_df['overall_compliance'].mean()
                st.metric("Average Overall Compliance", f"{avg_compliance:.2%}")
        else:
            if not is_synthetic:
                st.warning("No live ETHIK compliance data available yet. Live data integration is under development.")
            else:
                st.info("No ETHIK compliance data available.")

    # ATRiAN EaaS API Usage
    with st.expander("API: ATRiAN Ethics as a Service Usage", expanded=True):
        st.markdown("#### ATRiAN EaaS API Usage (Last 7 Days)")
        
        # Use a try-except block to handle potential parameter issues
        try:
            # Use synthetic or live data based on connection state
            # Pass the session's synthetic data seed to ensure consistent behavior
            if hasattr(st.session_state, 'synthetic_data_seed'):
                logger.debug(f"Using synthetic data seed for EaaS usage: {st.session_state.synthetic_data_seed}")
                
            # Always pass synthetic=is_synthetic to ensure proper mode is used
            eaas_usage_df = get_atrian_eaas_usage_metrics(synthetic=is_synthetic)
        except TypeError:
            # Fall back to calling without parameters if the synthetic parameter isn't supported
            try:
                eaas_usage_df = get_atrian_eaas_usage_metrics()
            except Exception as e:
                st.error(f"Error fetching ATRiAN EaaS usage metrics: {str(e)}")
                eaas_usage_df = pd.DataFrame()  # Empty dataframe as fallback
            
        if not eaas_usage_df.empty:
            st.dataframe(eaas_usage_df, use_container_width=True, height=300)
            st.metric("Total API Calls (7d)", len(eaas_usage_df))
        else:
            if not is_synthetic:
                st.warning("No live ATRiAN EaaS usage data available yet. Live data integration is under development.")
            else:
                st.info("No ATRiAN EaaS usage data available.")

    # $ETHIK Token Activity
    with st.expander("Token: $ETHIK Activity Across Chains", expanded=True):
        st.markdown("#### $ETHIK Token Activity (All Chains)")
        
        # Use a try-except block to handle potential parameter issues
        try:
            # Use synthetic or live data based on connection state
            # Pass the session's synthetic data seed to ensure consistent behavior
            if hasattr(st.session_state, 'synthetic_data_seed'):
                logger.debug(f"Using synthetic data seed for token activity: {st.session_state.synthetic_data_seed}")
                
            # Always pass synthetic=is_synthetic to ensure proper mode is used
            token_activity_df = get_ethik_token_activity(synthetic=is_synthetic)
        except TypeError:
            # Fall back to calling without parameters if the synthetic parameter isn't supported
            try:
                token_activity_df = get_ethik_token_activity()
            except Exception as e:
                st.error(f"Error fetching $ETHIK token activity data: {str(e)}")
                token_activity_df = pd.DataFrame()  # Empty dataframe as fallback
            
        if not token_activity_df.empty:
            st.dataframe(token_activity_df, use_container_width=True)
            if 'market_cap_usd' in token_activity_df.columns:
                total_market_cap = token_activity_df['market_cap_usd'].sum()
                st.metric("Total $ETHIK Market Cap (USD)", f"${total_market_cap:,.2f}")
        else:
            if not is_synthetic:
                st.warning("No live $ETHIK token activity data available yet. Live data integration is under development.")
            else:
                st.info("No $ETHIK token activity data available.")

    # Ethical Evaluation Process Visualization
    with st.expander("Process: Ethical Evaluation Workflow Visualization", expanded=False):
        st.markdown("#### Overview of the Ethical Evaluation Process")
        ethical_process_dot = """
        digraph EthicalEvaluationProcess {
            rankdir=TB; 
            node [shape=box, style="rounded,filled", fontname="Arial", fillcolor="#E8E8E8"];
            edge [fontname="Arial"];

            start [label="Start: Evaluation Triggered", shape=ellipse, fillcolor="#D6EAF8"];
            request_submission [label="1. Request Submission\n(to ATRiAN EaaS)"];
            atrian_assessment [label="2. ATRiAN Assessment\n(EthicalCompass Logic)"];
            dev_involvement_check [label="3. DEV Involvement Check\n(Based on impact/rules)", shape=diamond, fillcolor="#FADBD8"];
            dev_validation [label="4. DEV Validation Process\n(Decentralized Consensus)"];
            final_report [label="5. Final Evaluation Report\n& Audit Log", shape=document, fillcolor="#D5F5E3"];
            end_process [label="End: Outcome Recorded", shape=ellipse, fillcolor="#D6EAF8"];

            start -> request_submission;
            request_submission -> atrian_assessment;
            atrian_assessment -> dev_involvement_check;
            dev_involvement_check -> dev_validation [label="Yes, High Impact /\nContested / Configured"];
            dev_involvement_check -> final_report [label="No, Low Impact / Clear"];
            dev_validation -> final_report [label="DEV Outcome Input"];
            final_report -> end_process;

            subgraph cluster_atrian {
                label="ATRiAN EaaS Domain";
                style="filled";
                color="#F2F3F4";
                request_submission; atrian_assessment;
            }

            subgraph cluster_dev {
                label="Distributed Ethical Validator (DEV) Domain";
                style="filled";
                color="#EBF5FB";
                dev_validation;
            }
        }
        """
        st.graphviz_chart(ethical_process_dot)

# --- Main Application Logic ---
def main():
    """Main Streamlit application function with improved event loop management."""
    # Initialize language and theme session defaults
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    # Apply page configuration and theme
    st.set_page_config(layout="wide", page_title=get_translation("title"))
    st.markdown(apply_theme(st.session_state.theme), unsafe_allow_html=True)
    logger.info("--- EGOS Dashboard Started ---")
    
    # Initialize rerun throttling mechanism
    if 'last_rerun_time' not in st.session_state:
        st.session_state.last_rerun_time = time.time() - 10  # Initialize to allow first rerun
    if 'rerun_counter' not in st.session_state:
        st.session_state.rerun_counter = 0  # Track number of reruns for debugging
    
    initialize_session_state()
    client = get_mycelium_client()
    
    # Ensure mycelium client has a valid event loop
    if hasattr(client, 'loop') and (client.loop is None or client.loop.is_closed()):
        try:
            logger.info("Main: Initializing fresh event loop for MyceliumClient")
            client.loop = asyncio.new_event_loop()
        except Exception as e:
            logger.error(f"Main: Error setting up client event loop: {e}")
    
    # Handle initial connection if live_data_active is True (default)
    if st.session_state.live_data_active and not st.session_state.nats_connected:
        try:
            logger.info("Main: Initiating first connection to NATS server")
            # Safe event loop handling for initial connection
            try:
                # Method 1: Use asyncio.run (cleanest approach)
                asyncio.run(manage_nats_connection(client, True))
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # Method 2: Already in an event loop
                    loop = asyncio.get_event_loop()
                    loop.create_task(manage_nats_connection(client, True))
                elif "There is no current event loop in thread" in str(e):
                    # Method 3: No event loop, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(manage_nats_connection(client, True))
                    except Exception as loop_e:
                        logger.error(f"Main: Error in initial connection: {loop_e}")
                else:
                    logger.error(f"Main: Unexpected error during initial connection: {e}")
        except Exception as e:
            logger.error(f"Main: Failed to manage initial connection: {e}")
    
    page, live_data = display_sidebar(client)
    
    # Display connection status banner at the very top of the page based on the actual live_data state
    if live_data and st.session_state.nats_connected:
        status_color = "green"
        status_message = "Connected ✅"
    else:
        status_color = "gray"
        status_message = "Disconnected (Using Synthetic Data)"
    
    # Create a centralized status banner with better styling
    st.markdown(
        f"<div style='padding: 10px; border-radius: 5px; background-color: {status_color}; "
        f"color: white; text-align: center; font-weight: bold; margin-bottom: 10px;'>"
        f"NATS Status: {status_message}</div>", 
        unsafe_allow_html=True
    )
    
    # Display data mode banner below the connection status based on live_data parameter
    is_synthetic = not (live_data and st.session_state.nats_connected)
    st.session_state.using_synthetic_data = is_synthetic
    
    if is_synthetic:
        st.warning("⚠️ **SYNTHETIC DATA MODE** - The dashboard is displaying simulated data. For live data, enable 'Use Live Data' in the sidebar.")
    else:
        st.success("✅ **LIVE DATA MODE** - The dashboard is connected to real-time data sources via NATS/Mycelium.")
    
    if page == "Dashboard":
        st.title("EGOS System Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            display_sparc_tasks(live_data)
        with col2:
            display_llm_interactions(live_data)
            
        display_propagation_log(live_data)
        
    elif page == "Incident Analysis":
        from core.incident_pattern_dashboard import display_incident_pattern_dashboard
        display_incident_pattern_dashboard(live_data)

    elif page == "Ethical Governance":

        display_ethical_governance_metrics(live_data)

    elif page == "Feedback":
        st.title("User Feedback")
        feedback_form()
        st.markdown("---")
        st.header("Feedback Report")
        report_text = generate_feedback_report()
        st.markdown(report_text)

    elif page == "🚀 Onboarding Tutorial":
        display_onboarding_tutorial()
        
    logger.info("--- EGOS Dashboard Render Complete ---")

if __name__ == "__main__":
    main()