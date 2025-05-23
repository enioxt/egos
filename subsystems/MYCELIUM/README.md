# Mycelium Network Subsystem

**Version:** 0.3 # Updated version
**Last Updated:** 2025-04-02

## Role in Dynamic Roadmap Sync & EGOS Interconnection

MYCELIUM is responsible for:
- Acting as the event bus for roadmap updates and all inter-subsystem communication.
- Emitting and subscribing to roadmap update events so that all subsystems stay in sync.
- Facilitating event-driven architecture for EGOS, ensuring real-time updates and modularity.
- Working closely with KOIOS, CRONOS, SYNC, and CORUJA to implement and log all roadmap sync actions.

Cross-reference: See ROADMAP.md sections "Dynamic Roadmap Sync & Mycelium Interconnection" and "Technical Implementation Plan: Dynamic Roadmap Sync (Phase 1)".

## Core Vision

The Mycelium Network is the core communication and integration fabric of the EGOS system. Inspired by natural mycelial networks, it enables seamless, adaptive, and resilient information flow between all subsystems, fostering emergent collaboration and collective intelligence.

## Key Objectives

- Provide a unified communication bus for all subsystems.
- Support various communication patterns (request/response, pub/sub, events).
- Enable dynamic discovery and routing between subsystems.
- Facilitate state synchronization and resource sharing where appropriate.
- Ensure resilient and fault-tolerant communication.

## Existing Implementation (within SLOP Server)

An initial implementation of Mycelium Network concepts exists within the SLOP server (`src/services/slop/src/server/slop_server.js.backup`). This includes REST APIs and basic sync logic, serving as a reference.

## Status

- **Core Implementation (Python/Asyncio):** Completed and unit tested (`network.py`, `node.py`, `interface.py`). Provides basic registration, connection management, and message routing (Req/Res, Pub/Sub).
- **Design:** Consolidated design documented in `docs/protocol_design.md`.
- **Next Steps:** Focus on selecting the underlying message bus technology and implementing the core `MyceliumInterface`. Pilot subsystem connections (see main `ROADMAP.md`). Phase 2 features (advanced health, sync, routing) planned after initial integration.

## Basic Usage Examples (Conceptual)

These examples illustrate how a subsystem service might interact with the Mycelium network using the `MyceliumInterface`.

```python
import asyncio
from subsystems.MYCELIUM.interface import MyceliumInterface

# Assume configuration for node name, network address etc. is loaded
node_config = {
    "node_name": "ExampleServiceNode",
    "network_host": "127.0.0.1",
    "network_port": 61000, # Default Mycelium port
}

async def handle_incoming_message(topic: str, payload: dict):
    print(f"Received message on topic '{topic}': {payload}")
    # Process the message based on topic/payload
    pass

async def run_example_service():
    # 1. Initialize the interface for this service/node
    interface = MyceliumInterface(config=node_config)
    await interface.connect()
    print(f"Node {node_config['node_name']} connected to Mycelium.")

    # 2. Subscribe to relevant topics
    subscribe_topic = "event.system.startup"
    await interface.subscribe(subscribe_topic, handle_incoming_message)
    print(f"Subscribed to topic: {subscribe_topic}")

    # 3. Publish a message
    publish_topic = "request.data.process"
    message_payload = {"data_id": "123", "content": "Sample data"}
    print(f"Publishing to topic '{publish_topic}': {message_payload}")
    await interface.publish(publish_topic, message_payload)

    # Keep the service running (e.g., wait for keyboard interrupt)
    print("Service running. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Service stopping...")
    finally:
        await interface.disconnect()
        print("Node disconnected.")

# To run this example, the Mycelium network (master node)
# needs to be running separately.
# asyncio.run(run_example_service())

Refer to the detailed protocol design in `docs/protocol_design.md` and the main project `ROADMAP.md` for current priorities.

## Standard Message Schemas

Mycelium promotes standardized communication through Pydantic schemas. Key schemas include:

*   **SPARC Task Messages (`src/schemas/sparc_tasks.py`):**
    *   Defines the structure for messages related to SPARC task execution, including requests, stage updates, and final results.
    *   Models include `BaseSparcMessage`, `SparcTaskRequest`, `SparcTaskResult`, `SparcStageUpdate`, along with enums `SparcStage` and `TaskStatus`.
    *   Ensures consistent data exchange between subsystems involved in task orchestration (e.g., CORUJA, ATLAS).
    *   **Test Coverage:**
        *   Unit tests implemented in `tests/mycelium/schemas/test_sparc_tasks.py` (pytest).
        *   As of 2025-04-17, schema coverage is 80% (see coverage report). All schema tests pass.

*(More schemas will be added as the system evolves.)*

## Contributing

Contributions should focus on enhancing message schemas, client libraries, and ensuring reliable event propagation. Refer to the main <!-- TO_BE_REPLACED --> when working within this subsystem.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
