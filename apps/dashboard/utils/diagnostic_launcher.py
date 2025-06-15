#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_launcher.py

EGOS Diagnostic Dashboard and Tracking System Launcher

This module serves as the entry point for the Diagnostic Dashboard, integrating all
diagnostic tracking components into a comprehensive visualization and management system
for the 150+ diagnostic findings identified in the EGOS Project Diagnostic Report.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
  - [EGOS_Project_Diagnostic_Report.md](mdc:../../strategic-thinking/reports/EGOS_Project_Diagnostic_Report.md) - Source diagnostic report
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Main visualization module
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Issue tracking data persistence
  - [diagnostic_mycelium.py](mdc:./diagnostic_mycelium.py) - MYCELIUM communication integration
  - [diagnostic_notifications.py](mdc:./diagnostic_notifications.py) - Email and in-app notifications
  - [diagnostic_roadmap.py](mdc:./diagnostic_roadmap.py) - Roadmap integration and cross-referencing
  - [diagnostic_metrics.py](mdc:./diagnostic_metrics.py) - Metrics and analytics dashboard
  - [diagnostic_access_control.py](mdc:./diagnostic_access_control.py) - User authentication and authorization
  - [streamlit_app_integration.py](mdc:./streamlit_app_integration.py) - Integration with main dashboard
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import streamlit as st
import sys
import os
import logging
import asyncio
from pathlib import Path
from threading import Thread
from importlib import import_module
from typing import Dict, Any, Optional

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticLauncher")
logger.info("Diagnostic Launcher initializing...")

# Import Components (with error handling)
try:
    # Access Control (must be first to enforce authentication)
    from dashboard.diagnostic_access_control import require_login, access_manager, logout, user_management_ui
    
    # Core visualization and data tracking
    from dashboard.diagnostic_visualization import DiagnosticData, display_dashboard
    from dashboard.diagnostic_tracking import tracking_manager, get_all_issues, update_issue
    
    # Advanced features
    from dashboard.diagnostic_metrics import display_metrics_dashboard
    from dashboard.diagnostic_roadmap import roadmap_manager, find_related_tasks, link_issue_to_task
    
    # Optional components (with fallbacks if not available)
    try:
        from dashboard.diagnostic_mycelium import DiagnosticCollaborationManager
        mycelium_available = True
    except ImportError:
        logger.warning("MYCELIUM integration not available")
        mycelium_available = False
        
    try:
        from dashboard.diagnostic_notifications import notification_manager, send_notification
        notifications_available = True
    except ImportError:
        logger.warning("Notification system not available")
        notifications_available = False
    
    components_loaded = True
    logger.info("All available diagnostic components loaded successfully")
except Exception as e:
    logger.error(f"Error loading diagnostic components: {e}")
    components_loaded = False

class DiagnosticLauncher:
    """Launcher for the EGOS Diagnostic Tracking System."""
    
    def __init__(self, report_path: Optional[str] = None):
        """Initialize the diagnostic launcher.
        
        Args:
            report_path: Optional path to the diagnostic report
        """
        self.logger = logger
        
        # Find diagnostic report
        if report_path:
            self.report_path = Path(report_path)
        else:
            # Try to find report in standard location
            self.report_path = Path(__file__).parent.parent / "strategic-thinking" / "reports" / "EGOS_Project_Diagnostic_Report.md"
            
            # Fallback to search
            if not self.report_path.exists():
                possible_paths = list(Path(__file__).parent.parent.glob("**/EGOS_Project_Diagnostic_Report.md"))
                if possible_paths:
                    self.report_path = possible_paths[0]
                else:
                    self.report_path = None
        
        # Initialize components
        self.collaboration_manager = None
        self.background_task = None
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize diagnostic components."""
        # Initialize MYCELIUM integration if available
        if mycelium_available:
            try:
                loop = asyncio.new_event_loop()
                
                def run_init(loop):
                    asyncio.set_event_loop(loop)
                    loop.run_forever()
                
                self.background_task = Thread(target=run_init, args=(loop,), daemon=True)
                self.background_task.start()
                
                # Initialize collaboration manager
                future = asyncio.run_coroutine_threadsafe(self._setup_mycelium(), loop)
                self.collaboration_manager = future.result(timeout=10)
                
                self.logger.info("MYCELIUM integration initialized")
            except Exception as e:
                self.logger.error(f"Error initializing MYCELIUM integration: {e}")
    
    async def _setup_mycelium(self) -> Optional[DiagnosticCollaborationManager]:
        """Set up MYCELIUM collaboration manager.
        
        Returns:
            Initialized collaboration manager
        """
        if mycelium_available:
            try:
                from dashboard.diagnostic_mycelium import create_collaboration_manager
                manager = await create_collaboration_manager()
                return manager
            except Exception as e:
                self.logger.error(f"Error setting up MYCELIUM integration: {e}")
        return None
    
    def run(self) -> None:
        """Run the diagnostic dashboard application."""
        st.set_page_config(
            page_title="EGOS Diagnostic Tracking System",
            page_icon="📊",
            layout="wide"
        )
        
        # Check authentication
        authenticated = require_login()
        if not authenticated:
            return
        
        # Get current username
        username = st.session_state.get("username", "Unknown")
        
        # Header
        st.title("EGOS Diagnostic Tracking System")
        st.markdown(f"Welcome, **{username}**")
        
        # Logout button
        if st.button("Log Out"):
            logout()
            st.experimental_rerun()
        
        # Navigation
        nav_options = ["Dashboard", "Metrics", "User Management"]
        nav_selection = st.sidebar.radio("Navigation", nav_options)
        
        if nav_selection == "Dashboard":
            self._display_dashboard()
        elif nav_selection == "Metrics":
            if access_manager.has_permission(username, "view_metrics"):
                display_metrics_dashboard()
            else:
                st.error("You do not have permission to view metrics")
        elif nav_selection == "User Management":
            if access_manager.has_permission(username, "manage_users"):
                user_management_ui()
            else:
                st.error("You do not have permission to manage users")
    
    def _display_dashboard(self) -> None:
        """Display the main diagnostic dashboard."""
        if self.report_path and self.report_path.exists():
            try:
                # Create diagnostic data
                data = DiagnosticData(self.report_path)
                
                # Display dashboard
                display_dashboard(data)
            except Exception as e:
                st.error(f"Error displaying diagnostic dashboard: {e}")
                self.logger.error(f"Error in diagnostic visualization: {e}")
        else:
            st.error(f"Diagnostic report not found: {self.report_path}")
            
            # Provide upload option
            uploaded_file = st.file_uploader("Upload diagnostic report (Markdown)", type="md")
            if uploaded_file:
                temp_path = Path("temp_diagnostic_report.md")
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Create data from uploaded file
                try:
                    data = DiagnosticData(temp_path)
                    display_dashboard(data)
                except Exception as e:
                    st.error(f"Error processing uploaded report: {e}")
    
    def shutdown(self) -> None:
        """Shut down the launcher and release resources."""
        # Shutdown MYCELIUM integration
        if self.collaboration_manager:
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.collaboration_manager.shutdown())
                self.logger.info("MYCELIUM integration shutdown initiated")
            except Exception as e:
                self.logger.error(f"Error shutting down MYCELIUM integration: {e}")

def main() -> None:
    """Main function to run the diagnostic launcher."""
    # Check if components loaded successfully
    if not components_loaded:
        st.error("Failed to load required diagnostic components. Please check the logs.")
        return
    
    # Create and run launcher
    launcher = DiagnosticLauncher()
    launcher.run()

if __name__ == "__main__":
    main()