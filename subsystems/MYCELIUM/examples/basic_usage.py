#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO: Module docstring for basic_usage.py"""

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)



"""
EGOS Mycelium Network - Basic Usage Example
------------------------------------------
This example demonstrates the fundamental patterns for using the Mycelium Network
for inter-subsystem communication within EGOS.

It covers:
- Initializing the client
- Point-to-point messaging
- Topic-based publish/subscribe
- Request-response patterns
- Broadcast messaging

EGOS Principles Applied:
- Universal Accessibility: Simple usage patterns for all subsystems
- Reciprocal Trust: Reliable communication between components
- Conscious Modularity: Clean separation of responsibilities
"""

import asyncio
import logging
import uuid
from typing import Dict, Any

from subsystems.MYCELIUM import (
    create_client,
    MyceliumMessage
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mycelium.example")


# Example callback for handling messages
async def handle_message(message: MyceliumMessage) -> None:
    """Handle a received message."""
    logger.info(f"Received message from {message.source}: {message.payload}")


# Example callback for handling ethical validation requests
async def handle_validation_request(message: MyceliumMessage) -> None:
    """Handle an ethical validation request."""
    logger.info(f"Received validation request: {message.payload}")

    # Process the validation request
    validation_result = {
        "is_valid": True,
        "principles_applied": ["Universal Accessibility", "Reciprocal Trust"],
        "reasoning": "The requested action aligns with EGOS principles."
    }

    # Create a response
    response = message.create_response(payload=validation_result)

    # In a real implementation, this would send the response
    logger.info(f"Sending validation response: {response.payload}")


async def example_publisher() -> None:
    """Example of a subsystem publishing messages."""
    # Create a client for the CORUJA subsystem
    client = create_client("CORUJA")

    try:
        # Connect to the Mycelium Network
        await client.connect()

        # Publish a message to a topic
        await client.publish(
            topic="tasks.assigned",
            payload={
                "task_id": str(uuid.uuid4()),
                "title": "Optimize legacy file management",
                "priority": "high",
                "assigned_to": "HARMONY"
            }
        )
        logger.info("Published task assignment")

        # Broadcast a system-wide notification
        await client.broadcast(
            payload={
                "type": "notification",
                "severity": "info",
                "message": "System optimization in progress"
            }
        )
        logger.info("Broadcast notification sent")

        # Direct message to a specific subsystem
        await client.send(
            destination="CRONOS",
            payload={
                "type": "command",
                "action": "schedule_backup",
                "parameters": {
                    "tag": "pre_optimization"
                }
            }
        )
        logger.info("Sent backup command to CRONOS")

        # Make a request and wait for response
        try:
            response = await client.request(
                destination="ETHIK",
                payload={
                    "type": "validation",
                    "action": "file_deletion",
                    "context": {
                        "file_type": "temporary",
                        "age_days": 30
                    }
                },
                timeout=5.0
            )
            logger.info(f"Received validation response: {response}")
        except asyncio.TimeoutError:
            logger.error("Validation request timed out")

    finally:
        # Disconnect when done
        await client.disconnect()


async def example_subscriber() -> None:
    """Example of a subsystem subscribing to messages."""
    # Create a client for the HARMONY subsystem
    client = create_client("HARMONY")

    try:
        # Connect to the Mycelium Network
        await client.connect()

        # Subscribe to task assignments
        await client.subscribe(
            topic_pattern="tasks.assigned",
            callback=handle_message
        )
        logger.info("Subscribed to task assignments")

        # Subscribe to all validation requests
        await client.subscribe(
            topic_pattern="*.validation.request",
            callback=handle_validation_request
        )
        logger.info("Subscribed to validation requests")

        # Keep running to receive messages
        await asyncio.sleep(60)  # Run for 60 seconds

    finally:
        # Disconnect when done
        await client.disconnect()


async def run_examples() -> None:
    """Run the examples concurrently."""
    # Start the subscriber first
    subscriber_task = asyncio.create_task(example_subscriber())

    # Wait a moment for the subscriber to connect
    await asyncio.sleep(1)

    # Run the publisher
    await example_publisher()

    # Wait for the subscriber to finish
    await subscriber_task


def main() -> None:
    """Main entry point."""
    asyncio.run(run_examples())


if __name__ == "__main__":
    main()