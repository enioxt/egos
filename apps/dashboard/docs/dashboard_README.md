---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: readme
tags: [documentation]
---
---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - <!-- TO_BE_REPLACED --> - Project roadmap and planning
  - [MQP](..\..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
  - <!-- TO_BE_REPLACED --> - Complete dashboard architecture
  - <!-- TO_BE_REPLACED --> - Component optimization analysis
- System Standards:
  - <!-- TO_BE_REPLACED --> - SDRE protocol
  - <!-- TO_BE_REPLACED --> - SEGURO protocol
- Related Modules:
  - <!-- TO_BE_REPLACED --> - Core diagnostic data tracking
  - <!-- TO_BE_REPLACED --> - Data preprocessing
  - <!-- TO_BE_REPLACED --> - Time series analysis
  - <!-- TO_BE_REPLACED --> - Predictive modeling
  - <!-- TO_BE_REPLACED --> - Resource allocation
  - <!-- TO_BE_REPLACED --> - Analytics integration
  - <!-- TO_BE_REPLACED --> - SDRE Implementation
  - <!-- TO_BE_REPLACED --> - SEGURO Implementation
  - apps/dashboard/docs/dashboard_README.md

# EGOS Dashboard Subsystem

## Purpose

Provides a real-time, interactive interface for monitoring EGOS operations, facilitating contributor collaboration, gathering feedback, and ensuring system-wide diagnostic tracking and analytics capabilities for proactive issue remediation.

## ✨ Features

### Core Dashboard
*   **Modular UI:** Built with Streamlit, organized into logical, reusable display functions (`streamlit_app.py`).
*   **SPARC Task Monitoring:**
    *   Displays a feed of SPARC task events (simulated, ready for live data).
    *   Visualizations: Status distribution (bar chart), task timeline (basic hourly count).
    *   **Filtering (Batch 7):** Allows users to filter tasks by type and status.
*   **LLM Interaction Logs:** Shows recent interactions with language models used within EGOS (simulated).
*   **Feedback System Integration:**
    *   Direct link to the feedback submission form (`feedback.py`).
    *   **Enhanced Feedback Report (Batch 7):** Displays summaries, recent entries, top feedback (**simulated** ranking based on upvotes/tags), common word analysis, and a word cloud from `feedback_log.txt` (`feedback_report.py`).
*   **Meta-Transparency Panel:**
    *   Displays key context metrics (estimated token usage, open files, last batch ID).
    *   Shows a system "heartbeat".
    *   **Systemic Propagation Log (Batch 7):** Tracking adoption of best practices across EGOS subsystems.
*   **Live Data Readiness:**
    *   Includes a scaffold (`mycelium_client.py`) for future Mycelium/NATS integration.
    *   **UI Toggle (Batch 7):** Allows switching between simulated and (future) live data streams.
    *   **Live Data Integration (Mycelium/NATS):**
        *   Connects to a NATS server to receive real-time updates for SPARC tasks, LLM logs, and propagation events.
        *   Use the "Use Live Data" toggle in the sidebar to enable/disable the connection.
        *   Requires the NATS server URL to be set via the `NATS_URL` environment variable (defaults to `nats://localhost:4222` if not set).
        *   Displays connection status in the sidebar.

### Diagnostic Tracking System
*   **Issue Tracking** (`diagnostic_tracking.py`): Comprehensive system for tracking diagnostic issues across EGOS components.
*   **Visual Dashboard** (`diagnostic_visualization.py`): Interactive visualizations of diagnostic data.
*   **MYCELIUM Integration** (`diagnostic_mycelium.py`): Real-time collaboration and data sharing.
*   **Notification System** (`diagnostic_notifications.py`): Automated notifications for task assignments and due dates.
*   **Access Control** (`diagnostic_access_control.py`): Role-based access control for diagnostic data.
*   **CI/CD Integration** (`diagnostic_cicd.py`): Automated updates and GitHub interactions.
*   **Metrics Dashboard** (`diagnostic_metrics.py`): Analytics on remediation progress and team performance.

### Advanced Analytics Module
*   **Data Preprocessing** (`diagnostic_analytics_preprocessor.py`):
    *   Feature engineering from diagnostic data
    *   Data cleaning and normalization
    *   Categorical encoding and feature transformation
*   **Time Series Analysis** (`diagnostic_analytics_timeseries.py`):
    *   Trend analysis and seasonal decomposition
    *   ARIMA and Prophet forecasting models
    *   Interactive visualizations of temporal patterns
*   **Predictive Modeling** (`diagnostic_analytics_models.py`):
    *   Resolution time prediction
    *   Risk assessment models
    *   Feature importance analysis
*   **Resource Allocation** (`diagnostic_analytics_resource.py`):
    *   Issue weighting based on priority, age, and risk
    *   Resource optimization for remediation scheduling
    *   Priority management for dynamic issue prioritization
*   **Analytics Core** (`diagnostic_analytics_core.py`):
    *   Unified integration of all analytics components
    *   High-level API for diagnostic tracking system
    *   State management and automatic model training

## 📁 Structure

### Core Dashboard & UI
*   `streamlit_app.py`: Main application entry point, orchestrates UI components.
*   `streamlit_app_rewrite.py`: Rewritten version with improved performance (to be consolidated).
*   `streamlit_app_integration.py`: Extends dashboard with diagnostic visualization integration.
*   `feedback.py`: Contains the feedback submission form logic.
*   `feedback_report.py`: Generates the automated feedback analysis and visualizations.
*   `feedback_log.txt`: (Generated) Stores raw feedback submissions.

### Diagnostic Tracking System
*   `diagnostic_tracking.py`: Core issue tracking functionality.
*   `diagnostic_visualization.py`: Visualization components for diagnostic data.
*   `diagnostic_mycelium.py`: MYCELIUM integration for real-time collaboration.
*   `diagnostic_notifications.py`: Email and system notification components.
*   `diagnostic_roadmap.py`: Roadmap integration and discovery.
*   `diagnostic_metrics.py`: Metrics collection and dashboard.
*   `diagnostic_access_control.py`: Authentication and authorization.
*   `diagnostic_cicd.py`: CI/CD integration components.
*   `production_deployment.py`: Production configuration and security hardening.
*   `diagnostic_launcher.py`: Unified entry point for diagnostic components.

### MYCELIUM Integration
*   `mycelium_client.py`: Client for the MYCELIUM messaging system.
*   `mycelium_utils.py`: Utility functions for message handling.
*   `event_schemas.py`: Pydantic schemas for event types.

### Advanced Analytics Module
*   `diagnostic_analytics_preprocessor.py`: Data preprocessing and feature engineering.
*   `diagnostic_analytics_timeseries.py`: Time series analysis and forecasting.
*   `diagnostic_analytics_models.py`: Predictive models for resolution time and risk.
*   `diagnostic_analytics_resource.py`: Resource allocation and optimization.
*   `diagnostic_analytics_core.py`: Integration core for all analytics components.

### Documentation
*   `docs_egos/ARCHITECTURE.md`: Complete architecture documentation of all dashboard components.
*   `docs_egos/FILE_ANALYSIS.md`: Analysis of component redundancies and optimization opportunities.
*   `docs_egos/diagnostic_system_user_guide.md`: Comprehensive user documentation.
*   `README.md`: This file (high-level overview).

## Dependencies

### Core Dashboard
*   `streamlit` - Interactive web application framework
*   `pandas` - Data manipulation and analysis
*   `wordcloud` - Word cloud visualization
*   `matplotlib` - Data visualization

### MYCELIUM Messaging
*   `nats-py` - NATS messaging client
*   `asyncio` - Asynchronous I/O
*   `pydantic` - Data validation and settings management

### Diagnostic & Analytics
*   `scikit-learn` - Machine learning algorithms
*   `statsmodels` - Statistical models and tests
*   `plotly` - Interactive visualizations
*   `numpy` - Numerical operations
*   `scipy` - Scientific computing
*   `prophet` - Advanced time series forecasting
*   `fastapi` - Modern API framework
*   `uvicorn` - ASGI server
*   `sqlalchemy` - SQL toolkit and ORM
*   `jwt` - JSON Web Token
*   `bcrypt` - Password hashing

### Development Tools
*   `ruff` - Fast Python linter
*   `mypy` - Static type checking
*   `pytest` - Testing framework
*   `black` - Code formatting

### Deployment
*   `docker` - Containerization
*   `nginx` - Reverse proxy

Installation options:
1. Core dashboard: `pip install streamlit pandas wordcloud matplotlib`
2. Full installation: `pip install -r requirements.txt` (includes all dependencies)

See `requirements.txt` for specific version constraints.

## 🚀 Running the Dashboard

From the EGOS project root directory (`c:\Eva Guarani EGOS`):

```bash
streamlit run dashboard/streamlit_app.py
```

Or navigate to the dashboard directory first:

```bash
cd dashboard
streamlit run streamlit_app.py
```

## Recent Updates (2025-05-04) 🆕

*   **Diagnostic Analytics Core Module Implemented**
    *   Unified integration of all analytics components
    *   State persistence and automatic model training
    *   Comprehensive error handling and graceful degradation
    *   Enhanced time series forecasting capabilities

*   **Advanced Documentation Created**
    *   Complete architecture documentation with subsystem relationships
    *   Component redundancy analysis with optimization recommendations
    *   Cross-reference improvements for better navigation

*   **System-Wide Standards Contribution**
    *   Implementation of the SDRE (Sistema de Diagnóstico de Redundância EGOS)
    *   Development of the SEGURO protocol for safe directory navigation
    *   CLI tools for enforcing these standards across EGOS

## Future Enhancements (See `ROADMAP.md`)

*   Full Mycelium/NATS integration for live data.
*   Implementation of real tagging/upvoting for feedback.
*   More sophisticated analytics and visualizations.
*   Integration with other EGOS subsystem monitoring.
*   **Advanced Analytics (Completed): ✅**
    *   Core integration module for all analytics components.
    *   Resource allocation optimization component.
    *   Model persistence and retraining capabilities.
    *   Comprehensive documentation and architecture design.
*   **Component Optimization (In Progress): ⚡**
    *   Formal implementation of SDRE (Sistema de Diagnóstico de Redundância EGOS)
    *   Analysis completed and recommendations documented in <!-- TO_BE_REPLACED -->
    *   Consolidated architecture overview in <!-- TO_BE_REPLACED -->
    *   Scheduled consolidation of redundant UI components
*   **Protocol Implementation (Completed): ✅**
    *   SEGURO protocol for safe directory navigation
    *   CLI tools for protocol enforcement
    *   Integration with global EGOS standards
*   **API Integration (Planned): 📝**
    *   RESTful API for external system integration.
    *   Webhook support for CI/CD pipelines.
    *   OpenAPI/Swagger documentation.