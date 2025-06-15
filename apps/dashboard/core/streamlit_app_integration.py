"""streamlit_app_integration.py

Integration module for incorporating the diagnostic visualization components
into the main EGOS Dashboard without modifying the core streamlit_app.py.

This approach follows the Conscious Modularity principle of EGOS by extending
functionality through a modular design rather than modifying existing code.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Dashboard Components:
  - [streamlit_app.py](mdc:./streamlit_app.py) - Main dashboard application
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Diagnostic visualization module
  - [EGOS_Project_Diagnostic_Report.md](mdc:../../strategic-thinking/reports/EGOS_Project_Diagnostic_Report.md) - Source diagnostic report
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
from pathlib import Path
from importlib import import_module
import logging
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.Integration")
logger.info("Dashboard Integration module initialized.")

# Import the main dashboard application and diagnostic visualization
try:
    # Ensure the dashboard module is in path
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Try to dynamically import diagnostic_visualization
    diagnostic_viz = import_module("dashboard.diagnostic_visualization")
    logger.info("Successfully imported diagnostic visualization module")
except ImportError as e:
    logger.error(f"Error importing diagnostic visualization module: {e}")
    diagnostic_viz = None


def extend_sidebar(original_sidebar_func: Callable) -> Callable:
    """Extend the sidebar function to include diagnostic options.
    
    Args:
        original_sidebar_func: The original sidebar display function from streamlit_app
        
    Returns:
        Extended sidebar function that includes diagnostic options
    """
    def extended_sidebar(*args, **kwargs):
        # Call the original sidebar function
        original_sidebar(*args, **kwargs)
        
        # Add separator
        st.sidebar.markdown("---")
        
        # Add diagnostic options
        st.sidebar.header("Diagnostic Tools")
        
        show_diagnostics = st.sidebar.checkbox(
            "Show Diagnostic Dashboard",
            value=False,
            key="show_diagnostics"
        )
        
        if show_diagnostics:
            st.session_state.show_diagnostics = True
        else:
            st.session_state.show_diagnostics = False
    
    return extended_sidebar


def extend_main_app(original_main_func: Callable) -> Callable:
    """Extend the main application function to incorporate diagnostic visualization.
    
    Args:
        original_main_func: The original main function from streamlit_app
        
    Returns:
        Extended main function with diagnostic visualization capabilities
    """
    def extended_main(*args, **kwargs):
        # Initialize session state for diagnostics if not present
        if "show_diagnostics" not in st.session_state:
            st.session_state.show_diagnostics = False
        
        # If diagnostics are active, display diagnostic dashboard
        if st.session_state.show_diagnostics and diagnostic_viz is not None:
            st.title("EGOS Diagnostic Dashboard")
            
            # Get diagnostic data from the module
            try:
                # Find the diagnostic report path
                report_path = Path(__file__).parent.parent / "strategic-thinking" / "reports" / "EGOS_Project_Diagnostic_Report.md"
                
                # Create diagnostic data instance
                data = diagnostic_viz.DiagnosticData(report_path)
                
                # Display the dashboard
                diagnostic_viz.display_dashboard(data)
            except Exception as e:
                st.error(f"Error loading diagnostic dashboard: {e}")
                logger.error(f"Error in diagnostic visualization: {e}")
                
                # Fallback to original dashboard
                original_main(*args, **kwargs)
        else:
            # Run the original main function
            original_main(*args, **kwargs)
    
    return extended_main


def apply_extensions(st_app_module_name: str = "dashboard.streamlit_app") -> None:
    """Apply extensions to the main streamlit app module.
    
    This function dynamically imports the main streamlit app module and
    replaces its sidebar and main functions with extended versions that
    incorporate diagnostic visualization.
    
    Args:
        st_app_module_name: The module name for the main streamlit app
    """
    try:
        # Import the main streamlit app module
        st_app = import_module(st_app_module_name)
        
        # Store original functions
        original_sidebar = st_app.display_sidebar
        original_main = st_app.main
        
        # Replace with extended versions
        st_app.display_sidebar = extend_sidebar(original_sidebar)
        st_app.main = extend_main_app(original_main)
        
        logger.info("Successfully applied extensions to main streamlit app")
    except ImportError as e:
        logger.error(f"Error importing main streamlit app module: {e}")
    except AttributeError as e:
        logger.error(f"Error accessing required functions in main streamlit app: {e}")


def create_standalone_diagnostic_app():
    """Create a standalone diagnostic dashboard application.
    
    This function can be used to run the diagnostic dashboard independently
    of the main EGOS dashboard.
    """
    if diagnostic_viz is not None:
        st.set_page_config(
            page_title="EGOS Diagnostic Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        # Find the diagnostic report path
        report_path = Path(__file__).parent.parent / "strategic-thinking" / "reports" / "EGOS_Project_Diagnostic_Report.md"
        if not report_path.exists():
            report_path = Path(diagnostic_viz.DIAGNOSTIC_REPORT_PATH)
        
        # Create diagnostic data instance
        data = diagnostic_viz.DiagnosticData(report_path)
        
        # Display the dashboard
        diagnostic_viz.display_dashboard(data)
    else:
        st.error("Diagnostic visualization module not available")


if __name__ == "__main__":
    # When run directly, create a standalone diagnostic dashboard
    create_standalone_diagnostic_app()