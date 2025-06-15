@references:
  - docs/planning/Dashboard_Realtime_Data_Strategy.md

# EGOS Dashboard: Real-Time Data Integration & Legacy Migration Strategy

**Version:** 1.4
**Last Updated:** 2025-06-05T14:30:00-03:00
**Status:** Implementation In Progress

## 1. Vision & Goals

**Primary Roadmap Alignment:** This strategy directly supports the epics outlined in the [EGOS Project Roadmap](file:///C:/EGOS/ROADMAP.md) under the 'EGOS Dashboard Evolution & Real-Time Integration' section (tasks DBP-P1 through DBP-P4).


- Achieve a fully operational EGOS Dashboard reflecting real-time system status, metrics, and ethical compliance insights.
- Seamlessly integrate data streams from all core EGOS components including ATRiAN, Mycelium network, ETHIK validators, and other subsystems.
- Ethically assess, transform, and integrate valuable legacy data into the new EGOS data ecosystem and dashboard views.
- Provide transparent, auditable, and actionable metrics aligned with the Master Quantum Prompt (MQP) and EGOS principles.
- Ensure the dashboard serves as a central 'Systemic Cartography' tool for monitoring, diagnostics, and decision-making.

## 2. Current State (Summary - As of June 5, 2025)

- Dashboard UI is stable and runs without critical startup errors.
- Successfully integrated with real NATS server for live data streaming.
- Real `MyceliumClient` implementation now properly connected and operational with enhanced stability.
- Live data toggle in sidebar successfully connects to NATS and subscribes to topics, with reliable reconnection capabilities.
- NATS server infrastructure established with automated deployment script.
- Import path issues and attribute compatibility between real and fallback clients resolved.
- Basic navigation link established from the main EGOS Next.js website.
- Implemented real-time activity publisher that monitors actual EGOS system activities and publishes events to NATS topics.
- Full data flow from system activities to dashboard visualization now operational.
- Connection handling significantly improved with proper drain timeout management, automatic reconnection attempts, and user-friendly error messages.
- Subscription management optimized to prevent duplicate subscriptions and provide better logging.
- Enhanced connection monitoring with color-coded status indicators and detailed connection history.
- Implemented comprehensive error reporting with actionable guidance for users.
- Added connection metrics tracking for stability analysis and performance monitoring.
- Improved event loop management to prevent "event loop is closed" errors during connection operations.

## 3. Phase 1: Establishing Real-Time Core Infrastructure (Q3 2025)

*Objective: Enable basic, end-to-end real-time data flow from a few core EGOS services to the dashboard via NATS.*

**3.1. NATS Server & Mycelium Client Activation**
    - **Task DBP1.1.1:** ✅ Verify/Deploy NATS Server: Ensure a stable NATS server is operational and accessible to the dashboard environment. Document connection parameters.
      - *Completed June 3, 2025:* Created dedicated NATS server infrastructure with automated deployment script in `C:\EGOS\tools\nats-server\`. Server successfully runs on port 4222 with HTTP monitoring on port 8222.
    - **Task DBP1.1.2:** ✅ Integrate Real `MyceliumClient`: Standardize and verify the import and usage of the main `MyceliumClient` (from `integrations/mycelium_client.py`) in the dashboard application.
      - *Completed June 3, 2025:* Fixed import paths, resolved circular imports, and added compatibility code for attribute/method differences between real and fallback clients. Dashboard now successfully connects to NATS server and subscribes to topics. `streamlit_app.py` and other necessary modules (e.g., `utils/diagnostic_mycelium.py`), ensuring it correctly uses the real client when NATS is available.
      - *Enhanced June 4, 2025:* Significantly improved connection stability with proper drain timeout handling, automatic reconnection attempts, intelligent subscription management, and user-friendly error messages in the UI. The dashboard can now toggle live data on/off reliably without requiring restarts.
      - *Enhanced June 5, 2025:* Implemented comprehensive connection monitoring system with color-coded status indicators, detailed connection history logging, and actionable error messages with retry capabilities. Added connection metrics tracking and improved event loop management to prevent common async errors.
    - **Task DBP1.1.3:** Secure NATS Connection: Implement/Verify secure connection mechanisms and credentials management for NATS (if applicable).

**3.2. EGOS Core Services: Initial Data Publication**
    - **Task DBP1.2.1:** ✅ Implement Real-Time Activity Publisher: Create publisher for SPARC tasks, LLM logs, and pattern propagation data to verify full data flow from system activities to dashboard.
      - *Completed June 3, 2025:* Developed `egos_activity_publisher.py` in `C:\EGOS\tools\nats-publisher\` that monitors actual EGOS system activities (file changes, document updates, etc.) and publishes events to NATS topics. Includes file system watchers for real-time event detection and intelligent classification of events based on file paths and content.
      - *Enhanced June 4, 2025:* Verified full end-to-end data flow with real-time detection of file changes and principle propagation. The system successfully identifies EGOS principles (Systemic Cartography, Integrated Ethics, Operational Elegance) across different subsystems and publishes them to the appropriate topics.
    - **Task DBP1.2.2:** ⏳ Identify Pilot Metrics: Select 2-3 key metrics/status updates from core EGOS services (e.g., NEXUS basic status, ETHIK validation count, CHRONICLER log rate) for initial real-time publication.
      - *In Progress (70% complete):* Currently monitoring file changes in SPARC directories, work logs, planning documents, and cross-references between subsystems. Successfully tracking principle propagation across EGOS subsystems (CORE, INTEGRATIONS, PLANNING, WORK_LOGS). Need to expand to more specific metrics for NEXUS and ETHIK.
    - **Task DBP1.2.3:** ✅ Define Initial NATS Topics & Schemas: Establish NATS topics and simple, clear data schemas (e.g., JSON) for these pilot metrics.
      - *Completed June 3, 2025:* Defined and implemented JSON schemas for three main topics: `egos.sparc.tasks`, `egos.llm.logs`, and `egos.propagation.log`. Schemas include timestamps, trace IDs, and relevant metadata for each event type.
    - **Task DBP1.2.4:** ✅ Implement NATS Publishers: Implement basic NATS publishing capabilities in the selected core EGOS services for the pilot metrics.
      - *Completed June 3, 2025:* Implemented publishing capabilities in the EGOS activity publisher, with separate event handlers for different types of system activities.
      - *Verified June 4, 2025:* Confirmed that the publisher correctly detects file system events and publishes them to the appropriate NATS topics with proper metadata and principle identification.

**3.3. Dashboard: Basic Real-Time Ingestion & Display**
    - **Task DBP1.3.1:** ✅ Implement Live Data Toggle: Add UI control to enable/disable real-time data flow in the dashboard.
      - *Completed June 3, 2025:* Added live data toggle in sidebar with proper state management. Dashboard now correctly connects to NATS when toggle is enabled and disconnects when disabled.
      - *Enhanced June 4, 2025:* Improved toggle reliability with better error handling and connection state management. Added user-friendly status indicators and error messages.
      - *Enhanced June 5, 2025:* Further improved toggle interaction with better event loop management and more robust async operations.
    - **Task DBP1.3.2:** ⏳ Basic Real-Time Visualization: Implement initial visualization of incoming real-time data (e.g., simple activity feed, status indicators).
      - *Progress (70%):* Basic visualization of incoming events implemented. Need to enhance with better formatting and more detailed information display.
    - **Task DBP1.3.3:** ✅ Connection Monitoring & Alerting: Implement basic monitoring of NATS connection status with appropriate UI feedback.
      - *Completed June 5, 2025:* Implemented comprehensive connection monitoring with color-coded status indicators, detailed connection history logging, actionable error messages with retry capabilities, and connection metrics tracking. Added expandable connection details panel with subscription status and active topics.

## 4. Phase 2: Expanding Real-Time Data Coverage & ATRiAN Integration (Q4 2025 - Q1 2026)

*Objective: Integrate comprehensive data from all key EGOS subsystems, with a special focus on ATRiAN EaaS, and enhance dashboard visualizations.*

**4.1. ATRiAN EaaS Metrics Integration**
    - **Task DBP2.1.1:** Define ATRiAN Dashboard Metrics: Specify key metrics from ATRiAN EaaS to be displayed (e.g., EaaS API call volume, ethical risk scores generated, constitution evaluation success/failure rates, active ethical contexts).
    - **Task DBP2.1.2:** ATRiAN Data Publication: Ensure ATRiAN publishes these metrics to NATS or provides a queryable API endpoint for the dashboard.
    - **Task DBP2.1.3:** Dashboard UI for ATRiAN: Develop dedicated UI components/sections in the dashboard to visualize ATRiAN metrics effectively.

**4.2. Comprehensive EGOS Subsystem Metrics**
    - **Task DBP2.2.1:** Full Subsystem Integration Plan: For each EGOS subsystem (GUARDIAN, KOIOS, ORION, etc.), define key metrics, NATS topics, data schemas, and publisher implementations.
    - **Task DBP2.2.2:** Advanced Visualizations: Implement more sophisticated charts, graphs, and interactive elements in the dashboard for the expanded dataset.
    - **Task DBP2.2.3:** Data Aggregation & Summarization: Develop logic for aggregating and summarizing real-time data for higher-level views (e.g., hourly/daily summaries).

**4.3. User Feedback Loop via NATS**
    - **Task DBP2.3.1:** Feedback Submission to NATS: Modify the dashboard's user feedback system to publish submitted feedback to a dedicated NATS topic.
    - **Task DBP2.3.2:** Backend Feedback Processor: Develop/deploy a backend service that subscribes to the feedback NATS topic and stores the feedback persistently (e.g., in a database).

## 5. Phase 3: Legacy Data Migration (Q1-Q2 2026)

*Objective: Ethically assess, transform, and integrate valuable legacy data into the EGOS ecosystem and make it accessible via the dashboard.*

**5.1. Legacy Data Inventory & Assessment**
    - **Task DBP3.1.1:** Identify & Catalog Legacy Sources: Locate, document, and analyze all relevant legacy data sources (databases, files, etc.) for format, volume, content, and current usage.
    - **Task DBP3.1.2:** Define Ethical Migration Criteria: Establish clear ethical guidelines (aligned with MQP & ATRiAN principles) for migrating legacy data, covering privacy, bias, consent, relevance, and data quality.

**5.2. Ethical Data Cleansing & Transformation (ATRiAN-Assisted)**
    - **Task DBP3.2.1:** ATRiAN Configuration for Migration: Develop/Configure an ATRiAN Ethical Constitution and rule set specifically for assessing legacy data.
    - **Task DBP3.2.2:** Automated Ethical Review: Utilize ATRiAN EaaS to perform automated ethical checks on legacy datasets. (Leverage `ATRiAN_Ethics_Evaluation_Workflow`).
    - **Task DBP3.2.3:** Data Anonymization/Pseudonymization: Implement processes for anonymizing or pseudonymizing sensitive legacy data as required by ethical criteria.
    - **Task DBP3.2.4:** Design ETL Processes: Design Extract, Transform, Load (ETL) scripts/workflows to cleanse, reformat, and map legacy data to new EGOS data models/schemas.

**5.3. Loading & Validating Migrated Data**
    - **Task DBP3.3.1:** Define Target Persistent Stores: Identify or set up appropriate persistent storage (e.g., PostgreSQL, NoSQL DB) for the cleansed and transformed legacy data.
    - **Task DBP3.3.2:** Execute & Validate ETL: Run ETL processes and rigorously validate the loaded data for accuracy, completeness, and ethical compliance.

**5.4. Dashboard Integration of Legacy Data**
    - **Task DBP3.4.1:** UI for Historical Data: Design and implement UI sections/features in the dashboard to access, visualize, and analyze migrated legacy data, clearly distinguishing it from real-time data.

## 6. Phase 4: Continuous Operation, Monitoring & Refinement (Ongoing from Q2 2026)

*Objective: Ensure stable, reliable operation of the data-driven dashboard, with continuous monitoring and iterative improvements.*

**6.1. Deployment & Infrastructure**
    - **Task DBP4.1.1:** Deploy Dashboard & Data Services: Plan and execute the deployment of the Streamlit dashboard and any associated backend data services to a production-like environment.
    - **Task DBP4.1.2:** Scalability & Performance: Ensure the infrastructure can handle the expected data load and user traffic.

**6.2. Monitoring & Alerting**
    - **Task DBP4.2.1:** Implement System Health Monitoring: Set up monitoring for NATS, EGOS data-publishing services, data storage, and the dashboard application itself (e.g., using Prometheus, Grafana).
      - *Partially Implemented June 4, 2025:* Enhanced logging throughout the NATS connection lifecycle in both `MyceliumClient` and `streamlit_app.py`. Added detailed error tracking and user-friendly error messages in the UI for connection issues.
    - **Task DBP4.2.2:** Data Flow Monitoring: Track data flow from publishers to subscribers, identify bottlenecks or failures.
      - *Partially Implemented June 4, 2025:* Added comprehensive logging for subscription management, connection callbacks, and reconnection attempts.
    - **Task DBP4.2.3:** Alerting Mechanisms: Configure alerts for critical issues (e.g., service downtime, data pipeline failures, ethical breaches detected by ATRiAN).
      - *Partially Implemented June 4, 2025:* Added user-friendly error messages in the dashboard UI for connection issues, with specific guidance based on error type.

**6.3. Iterative Refinement**
    - **Task DBP4.3.1:** User Feedback Collection: Continuously gather feedback on dashboard usability, data presentation, and features.
    - **Task DBP4.3.2:** Performance Optimization: Regularly review and optimize dashboard performance and data query efficiency.
    - **Task DBP4.3.3:** Evolve with EGOS: Update the dashboard to reflect new EGOS features, subsystems, and evolving ethical considerations.

## 7. Cross-Cutting Concerns

- **NATS Client Stability in Streamlit:** ✅ Implemented robust NATS connection management within Streamlit's re-entrant execution model. The `MyceliumClient` and its interaction with `streamlit_app.py` now handle connection, disconnection, and potential event loop conflicts gracefully. Key improvements include:
  - Proper drain timeout handling with a 3-second limit to prevent indefinite blocking
  - Comprehensive error handling and logging during connection lifecycle
  - Automatic reconnection attempts with configurable retry parameters
  - Intelligent subscription management to prevent duplicate subscriptions
  - User-friendly error messages in the UI for connection issues
  - Connection state properly reset even after errors
  - (Related to `docs/work_logs/WORK_2025-06-03_Dashboard_NATS_Debug_Wrapup.md` and `docs/work_logs/WORK_2025-06-04_Dashboard_NATS_Stability_Enhancements.md`)
- **Documentation:** Maintain comprehensive documentation for data schemas, NATS topics, API endpoints, ETL processes, and dashboard features.
- **Security:** Ensure security best practices are applied throughout the data pipeline, from NATS communication to data storage and dashboard access.
- **Testing:** Implement thorough unit, integration, and end-to-end tests for all components involved in data publishing, processing, and visualization.
- **Ethical Oversight:** Continuously involve ATRiAN and ethical review processes in all phases, especially when handling new data types or making significant changes to data processing.

## 8. Roles & Responsibilities (Placeholder - To be defined)

- EGOS Core Team
- ATRiAN Development Team
- Dashboard Development Team
- Data Engineering / Ops Team
- Ethical Review Board

## 9. Dependencies

- Stable and operational NATS server.
- Core EGOS services capable of publishing data.
- ATRiAN EaaS availability and integration points.
- Defined data schemas and governance processes.