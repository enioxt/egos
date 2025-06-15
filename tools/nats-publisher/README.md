@references:
  - tools/nats-publisher/README.md

# EGOS Activity Publisher

## Overview

The EGOS Activity Publisher is a real-time monitoring and publishing system that captures actual EGOS system activities and publishes them to NATS topics for visualization in the EGOS Dashboard. This implementation follows the EGOS principles of **Conscious Modularity**, **Systemic Cartography**, and **Authentic Integration** by using real system data rather than simulated content.

## Features

- **Real-Time Activity Monitoring**: Watches file changes and system activities across the EGOS ecosystem
- **Multi-Topic Publishing**: Publishes events to three key NATS topics:
  - `egos.sparc.tasks`: SPARC task execution and file modifications
  - `egos.llm.logs`: LLM interactions and document processing
  - `egos.propagation.log`: Pattern adoption and cross-references between subsystems
- **File System Watching**: Uses the watchdog library to detect file changes in real-time
- **Intelligent Event Classification**: Determines event types, subsystems, and patterns based on file paths and content
- **Heartbeat Mechanism**: Publishes regular heartbeat messages to verify system health

## Requirements

- Python 3.9+
- NATS server running on localhost:4222
- Python packages:
  - `nats-py`: For NATS messaging
  - `watchdog`: For file system monitoring

## Usage

### Running the Publisher

1. Start the NATS server and publisher using the provided PowerShell script:

```powershell
.\run_publisher.ps1
```

This script will:
- Check if required Python packages are installed
- Start the NATS server if it's not already running
- Launch the EGOS activity publisher

### Manual Startup

Alternatively, you can start the components manually:

1. Start the NATS server:
```powershell
cd C:\EGOS\tools\nats-server
.\download-and-run-nats.ps1
```

2. In a separate terminal, start the activity publisher:
```powershell
cd C:\EGOS\tools\nats-publisher
python egos_activity_publisher.py
```

### Viewing Events in the Dashboard

1. Start the EGOS Dashboard:
```powershell
cd C:\EGOS\apps\dashboard
python -m streamlit run core\streamlit_app.py
```

2. In the dashboard, enable the "Use Live Data" toggle to connect to NATS and subscribe to the topics.

3. As you work within the EGOS system (editing files, creating documents, etc.), the activity publisher will detect these changes and publish events to the appropriate topics, which will then appear in the dashboard.

## Monitored Activities

### SPARC Tasks
- Python file modifications in SPARC directories
- JavaScript/TypeScript file changes
- Documentation updates related to SPARC

### LLM Logs
- Work log document updates
- Planning document modifications
- ATRiAN ethical evaluation documents

### Knowledge Propagation
- Cross-references between subsystems
- Pattern adoption across the EGOS ecosystem
- System-wide file changes that indicate knowledge transfer

## Extending the Publisher

To monitor additional activities or publish to new topics:

1. Add new paths to the `MONITOR_PATHS` dictionary in `egos_activity_publisher.py`
2. Create a new event handler class that extends `FileSystemEventHandler`
3. Implement the appropriate event detection and publishing logic
4. Add the new handler to the `setup_file_watchers` function

## References

- [Master Quantum Prompt (MQP.md)](../../MQP.md)
- [EGOS Roadmap](../../ROADMAP.md)
- [Dashboard Realtime Data Strategy](../../docs/planning/Dashboard_Realtime_Data_Strategy.md)
- [NATS Messaging System](https://nats.io/)

## Alignment with EGOS Principles

This implementation embodies several key EGOS principles:

- **Conscious Modularity**: Separate monitoring components for different activity types
- **Systemic Cartography**: Mapping system activities to meaningful events
- **Authentic Integration**: Using real system data rather than simulated content
- **Operational Elegance**: Automated startup and monitoring with clear logging
- **Adaptive Resilience**: Graceful handling of connection issues and file system events

@references(level=1):
  - docs/planning/Dashboard_Realtime_Data_Strategy.md