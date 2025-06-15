@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - apps/dashboard/README.md

# EGOS Dashboard System

## Overview

This dashboard provides a centralized view of the EGOS ecosystem's operational status, ethical metrics, and system health. The dashboard now supports **real-time data integration** via NATS messaging system, allowing live monitoring of EGOS subsystems.

For the detailed strategy on real-time data integration and legacy systems migration, please refer to the [EGOS Dashboard: Real-Time Data Integration & Legacy Migration Strategy](file:///C:/EGOS/docs/planning/Dashboard_Realtime_Data_Strategy.md).

## Real-Time Data Features

### Current Status (June 3, 2025)

✅ **NATS Integration**: Successfully integrated with NATS server for real-time messaging
✅ **Live Data Toggle**: Use the "Use Live Data" toggle in the sidebar to connect to the NATS server
✅ **Connection Status**: Dashboard shows NATS connection status and subscription status
⏳ **Test Publishers**: Development of test publishers for sample data in progress

### Using Real-Time Features

1. **Start the NATS Server**:
   ```powershell
   cd C:\EGOS\tools\nats-server
   powershell -ExecutionPolicy Bypass -File download-and-run-nats.ps1
   ```

2. **Launch the Dashboard**:
   ```powershell
   cd C:\EGOS\apps\dashboard\core
   streamlit run streamlit_app.py
   ```

3. **Enable Live Data**:
   - Toggle "Use Live Data" in the sidebar
   - Verify that NATS Status shows "Connected" (green indicator)
   - Verify that Subscriptions shows "Active"


The EGOS Dashboard System provides a unified interface for monitoring, visualizing, and interacting with the EGOS ecosystem. This consolidated dashboard implementation follows the EGOS principles of Conscious Modularity and Systemic Cartography, providing a clear structure and organization.

## Directory Structure

```
dashboard/
├── core/               # Core dashboard application files
│   ├── streamlit_app.py             # Main Streamlit application
│   ├── streamlit_app_integration.py # Integration with other EGOS components
│   └── production_deployment.py     # Production deployment configuration
├── ui/                 # User interface components
│   ├── feedback.py                  # User feedback collection
│   └── feedback_report.py           # Feedback reporting and visualization
├── integrations/       # Integration with other EGOS subsystems
│   ├── mycelium_client.py           # NATS-based Mycelium client
│   ├── mycelium_utils.py            # Utilities for Mycelium integration
│   └── event_schemas.py             # Event schema definitions
├── analytics/          # Data analysis and processing
│   ├── core.py                      # Core analytics functionality
│   ├── models.py                    # Data models and structures
│   ├── preprocessor.py              # Data preprocessing
│   ├── resource.py                  # Resource management
│   └── timeseries.py                # Time series analysis
├── utils/              # Utility functions and diagnostic tools
│   ├── diagnostic_access_control.py # Access control diagnostics
│   ├── diagnostic_cicd.py           # CI/CD diagnostics
│   ├── diagnostic_launcher.py       # Dashboard launcher
│   ├── diagnostic_metrics.py        # Metrics collection
│   ├── diagnostic_mycelium.py       # Mycelium diagnostics
│   ├── diagnostic_notifications.py  # Notification system
│   ├── diagnostic_roadmap.py        # Roadmap integration
│   ├── diagnostic_tracking.py       # Event tracking
│   └── diagnostic_visualization.py  # Visualization utilities
└── docs/               # Documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- Streamlit
- NATS server running (for Mycelium integration)

### Installation

1. Clone the EGOS repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Dashboard

```bash
cd apps/dashboard
python -m core.streamlit_app
```

## Integration with EGOS Subsystems

The dashboard integrates with other EGOS subsystems through the Mycelium messaging system. The `integrations/mycelium_client.py` provides a standardized interface for communication with:

- NEXUS (System Coordination)
- ETHIK (Validation Framework)
- KOIOS (Documentation System)
- CHRONICLER (Logging and Auditing)

## Current Features (As of June 2025)

- **Modular UI Structure:** Sidebar navigation to various sections including Dashboard Home, Ethical Governance Metrics, User Feedback, System Architecture, and Onboarding.
- **Ethical Governance Metrics Display:** Visualizes (currently simulated) data for:
  - Distributed Ethical Validator (DEV) Activity
  - ETHIK Framework Compliance Scores
  - ATRiAN EaaS Usage Metrics
  - $ETHIK Token Activity
- **User Feedback System:** Allows users to submit feedback through a form. Generates a feedback report (currently based on session data or simulated inputs).
- **NATS Connection Status:** Displays the status of the connection to the NATS messaging server (currently operates in fallback mode if the real connection fails).
- **Data Export:** Users can download displayed tabular data (e.g., ethical metrics) as CSV files.
- **Basic Onboarding Tutorial:** Provides an introductory guide to the dashboard.
- **System Architecture View:** Embeds a view of the EGOS system architecture diagram.

## Recent Fixes & Achievements (May-June 2025)

- **Resolved Critical Python Import Errors:** Addressed `ModuleNotFoundError`, circular imports, and module/package name collisions (e.g., by renaming `ui/feedback.py` to `ui/feedback_module.py`).
- **Fixed `AttributeError` Issues:** Corrected several `AttributeError` problems related to the `MyceliumClient` (fallback client) interactions, specifically for `fallback_mode`, `is_connected`, and `close`/`disconnect` attributes/methods.
- **Enhanced Application Stability:** The dashboard now starts and runs more reliably without immediate crashes, facilitating further development and testing.
- **Improved Module Management:** Refined `__init__.py` files across the UI package for clearer and more robust export management.
- **Website Integration:** Added a direct link to this Streamlit dashboard from the main EGOS Next.js website's header navigation for improved accessibility.

## Next Steps for Real Data Integration

The following tasks are key to transitioning the dashboard from simulated data to displaying real-time information from the EGOS ecosystem:

1.  **Activate Real NATS/Mycelium Client:**
    *   Ensure the NATS server is operational and accessible to the dashboard environment.
    *   Verify and correct the import path and configuration of the *actual* `MyceliumClient` (e.g., `dashboard.mycelium_client.MyceliumClient`) within `streamlit_app.py` and `utils/diagnostic_mycelium.py` (to use the real client when not in fallback mode).
    *   Update NATS connection parameters (server URL, credentials if required) in a secure and configurable manner.
2.  **Implement Real-Time Data Subscriptions:**
    *   Refactor data-loading logic in `analytics/ethical_metrics.py` and other relevant data display modules.
    *   Replace simulated data generation with subscriptions to appropriate NATS topics to receive live data streams.
    *   Implement asynchronous callback functions to process incoming NATS messages and update Streamlit's session state and UI components dynamically.
3.  **Ensure EGOS Components Publish Data:**
    *   Verify that core EGOS components (DEV, ETHIK, ATRiAN, logging services, etc.) are actively publishing their metrics, logs, and status updates to the designated NATS topics.
    *   Establish and adhere to clear, versioned data schemas (e.g., using Avro, Protobuf, or JSON Schema) for all messages exchanged over NATS.
4.  **Persistent Storage for Feedback & Other User-Generated Data:**
    *   Design and implement a mechanism for user-submitted data (like feedback) to be sent (e.g., via NATS) to a backend service that stores it persistently (e.g., in a database like PostgreSQL or a document store).
    *   Modify the feedback report generation and other relevant sections to query this persistent store.
5.  **Refine Data Visualizations and Interactions:**
    *   Once real data is flowing, critically review and enhance all charts, tables, and visualizations to ensure they accurately and effectively represent the information.
    *   Consider adding more interactive features, such as filtering, sorting, drill-downs, and date range selections for time-series data.
6.  **Implement Robust Error Handling and Resilience for Live Data:**
    *   Strengthen error handling for NATS connection issues, message deserialization errors, and unexpected data formats.
    *   Provide clear, user-friendly feedback in the UI if data streams are interrupted or if errors occur during data processing.

## Development Guidelines

When extending the dashboard:

1. Follow the modular structure - place new components in the appropriate directory
2. Maintain clear separation of concerns
3. Update this README when adding significant new functionality
4. Follow EGOS cross-reference standards for documentation
5. Implement proper error handling and logging

## References

- [EGOS Dashboard Consolidation Plan](C:\EGOS\WORK_2025-05-23_Dashboard_Consolidation_Plan.md)
- [EGOS Diagnostic Analysis](C:\EGOS\DiagEnio.md)
- [EGOS Mycelium Interface](C:\EGOS\apps\dashboard\integrations\mycelium_client.py)
- [EGOS System Reorganization](C:\EGOS\docs\processes\reorganization\2025_05_REORGANIZATION.md)

✧༺❀༻∞ EGOS ∞༺❀༻✧