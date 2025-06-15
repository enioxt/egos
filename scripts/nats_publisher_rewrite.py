#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""NATS Publisher Tool for EGOS

This script simulates various EGOS subsystems publishing events to NATS topics.
It can be used to test the dashboard live data functionality without requiring
the actual subsystems to be running.

Usage:
    python nats_publisher.py --topic egos.sparc.tasks --count 5 --interval 2
    python nats_publisher.py --topic egos.llm.logs --count 3
    python nats_publisher.py --topic egos.propagation.log --count 2 --interval 5

Topics:
    - egos.sparc.tasks: SPARC task events
    - egos.llm.logs: LLM interaction logs
    - egos.propagation.log: System propagation events

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
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

# Standard library imports
import asyncio
import json
import os
import random
import time
import uuid
import argparse
import datetime
from datetime import timedelta
import logging
from typing import Dict, Any, List, Optional

# Third-party imports
import nats  # Make sure nats-py is installed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("EGOS.NATSPublisher")

# Default NATS server URL (same as in mycelium_client.py)
DEFAULT_NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4222")

# Data generators for different topics
def generate_sparc_task() -> Dict[str, Any]:
    """Generate a simulated SPARC task event."""
    task_types = ["sparc_analyze", "sparc_ingest", "sparc_refactor", "sparc_generate", "sparc_summarize"]
    statuses = ["queued", "in_progress", "completed", "failed"]

    # Weight the statuses to make completed and in_progress more common
    status_weights = [0.1, 0.3, 0.4, 0.2]

    task_type = random.choice(task_types)
    status = random.choices(statuses, weights=status_weights)[0]

    result = ""
    if status == "completed":
        results = ["No issues found.", "Generated code stub.", "Analysis complete.", "Summary generated."]
        result = random.choice(results)
    elif status == "failed":
        results = ["Syntax error", "Timeout", "Resource error", "Validation failed"]
        result = random.choice(results)

    return {
        "id": f"T-{uuid.uuid4().hex[:6]}",
        "type": task_type,
        "status": status,
        "result": result,
        "timestamp": datetime.datetime.now().isoformat()
    }

def generate_llm_log() -> Dict[str, Any]:
    """Generate a simulated LLM interaction log."""
    users = ["alice", "bob", "carlos", "dana", "system"]
    prompts = [
        "Summarize the latest batch results",
        "Analyze code quality in module X",
        "Generate documentation for function Y",
        "Explain the EGOS architecture",
        "Suggest improvements for subsystem Z"
    ]
    responses = [
        "Analysis complete. Found 3 areas for improvement.",
        "Documentation generated successfully.",
        "EGOS uses a modular architecture with these key components...",
        "Suggested refactoring: split the class into two separate concerns.",
        "The latest batch shows improved performance across all metrics."
    ]

    return {
        "user": random.choice(users),
        "prompt": random.choice(prompts),
        "response": random.choice(responses),
        "timestamp": time.strftime('%H:%M:%S')
    }

def generate_propagation_log() -> Dict[str, Any]:
    """Generate a simulated system propagation event."""
    subsystems = ["SPARC", "KOIOS", "CORUJA", "ETHIK", "CRONOS", "MYCELIUM"]
    patterns = [
        "Async Error Handling", 
        "Context Logger", 
        "Modular Visualization",
        "Recursive Analysis",
        "Feedback Loop",
        "Distributed Event Processing"
    ]
    statuses = ["Proposed", "Under Review", "Adopted", "Completed"]

    # Randomly generate a timestamp within the last 2 days
    random_minutes = random.randint(0, 60*48)  # Up to 48 hours in minutes
    timestamp = datetime.datetime.now() - timedelta(minutes=random_minutes)

    return {
        "timestamp": timestamp.isoformat(),
        "subsystem": random.choice(subsystems),
        "pattern": random.choice(patterns),
        "status": random.choice(statuses)
    }

# Topic to generator mapping
TOPIC_GENERATORS = {
    "egos.sparc.tasks": generate_sparc_task,
    "egos.llm.logs": generate_llm_log,
    "egos.propagation.log": generate_propagation_log,
}

async def publish_events(
    nats_url: str, 
    topic: str, 
    count: int, 
    interval: float = 1.0,
    generator_func=None
) -> None:
    """
    Publish a series of events to a NATS topic.

    Args:
        nats_url: NATS server URL
        topic: NATS topic to publish to
        count: Number of events to publish
        interval: Interval between events in seconds
        generator_func: Function to generate event data
    """
    if generator_func is None:
        generator_func = TOPIC_GENERATORS.get(topic)
        if generator_func is None:
            raise ValueError(f"No generator found for topic: {topic}")

    try:
        logger.info(f"Connecting to NATS server at {nats_url}...")
        nc = await nats.connect(nats_url)
        logger.info(f"Connected to NATS server at {nats_url}")

        for i in range(count):
            event_data = generator_func()
            payload = json.dumps(event_data).encode()
            await nc.publish(topic, payload)
            logger.info(f"Published to {topic}: {event_data}")

            if i < count - 1:  # Don't sleep after the last event
                await asyncio.sleep(interval)

        logger.info(f"Published {count} events to {topic}")
        await nc.drain()
    except Exception as e:
        logger.error(f"Error publishing to NATS: {e}")
        raise
    finally:
        try:
            await nc.close()
        except:
            pass

def main():
    """Process command line arguments and run the publisher."""
    parser = argparse.ArgumentParser(description="Publish events to NATS topics")
    parser.add_argument("--url", default=DEFAULT_NATS_URL, help="NATS server URL")
    parser.add_argument("--topic", required=True, choices=list(TOPIC_GENERATORS.keys()), 
                        help="Topic to publish to")
    parser.add_argument("--count", type=int, default=1, help="Number of events to publish")
    parser.add_argument("--interval", type=float, default=1.0, 
                        help="Interval between events in seconds")

    args = parser.parse_args()

    asyncio.run(publish_events(
        args.url, 
        args.topic, 
        args.count, 
        args.interval
    ))

if __name__ == "__main__":
    main()