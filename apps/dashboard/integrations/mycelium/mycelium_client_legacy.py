"""TODO: Module docstring for mycelium_client.py

@references:
- Core References:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
sys.path.insert(0, project_root)

"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
"""mycelium_client.py
Mycelium/NATS integration for real-time SPARC event updates in the dashboard.
Utilizes the nats-py library for asynchronous communication.

This module implements the EGOS Neural Journey metaphor, tracking events
through the system with trace_ids for complete observability.

Interconnected with:
- mycelium_utils.py: Shared utilities for trace_id management
- event_schemas.py: Pydantic schemas for event validation
- nats_simulator.py: Simulated NATS server for testing
- direct_event_injector.py: Direct event injection for testing
"""

import asyncio
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List, Union

# Import shared utilities and schemas
from dashboard.mycelium_utils import (
    current_trace_id, generate_trace_id, set_trace_id, 
    reset_trace_id, ensure_trace_id, extract_trace_id,
    log_with_trace_id, create_timestamped_event
)
try:
    from dashboard.event_schemas import validate_event
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False
    logging.warning("event_schemas module not found. Event validation disabled.")

# Import nats with error handling to support fallback mode
try:
    import nats
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    logging.warning("nats-py package not found. MyceliumClient will operate in fallback mode.")

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - Consider moving to env vars or a config file
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
DEFAULT_TIMEOUT = 5 # seconds

class MyceliumClient:
    """Client for connecting to NATS/Mycelium message bus.
    
    This client handles connection to NATS, subscription to topics,
    and processing of messages with appropriate callbacks.
    
    Features:
    - Automatic reconnection with exponential backoff
    - Fallback mode when NATS is unavailable
    - Direct event injection for testing without NATS
    - Comprehensive error handling and logging
    - Trace ID propagation for end-to-end event tracking
    - Event validation using Pydantic schemas
        Attributes:
        None
"""
    
    def __init__(self, nats_url: str = None, loop: asyncio.AbstractEventLoop = None):
        """Initialize the client.
        
        Args:
            nats_url: URL for the NATS server. Defaults to NATS_URL env var or localhost.
            loop: Optional event loop to use. If not provided, will get or create one.
        """
        self.logger = logging.getLogger("dashboard.mycelium_client")
        self.nats_url = nats_url or os.environ.get("NATS_URL", "nats://localhost:4222")
        self.nc = None # NATS connection object
        self.subscriptions = {} # topic: sid
        self.callbacks = {} # topic: callback function
        self.connection_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_wait_time = 2  # Initial wait time in seconds
        
        # Event injection mode (fallback when NATS is unavailable)
        self.fallback_mode = not NATS_AVAILABLE
        self.injected_events: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize event loop
        if loop is not None:
            self.loop = loop
        else:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        
        self.is_connected = False
        
        # Log initialization state
        if self.fallback_mode:
            self.logger.warning("Initializing MyceliumClient in FALLBACK MODE (no NATS)")
        else:
            self.logger.info(f"Initializing MyceliumClient with NATS URL: {self.nats_url}")

    async def connect(self):
        """Connect to the NATS server.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        # If in fallback mode, simulate a successful connection
        if self.fallback_mode:
            self.logger.warning("Operating in fallback mode - NATS connection simulated")
            self.is_connected = True
            return True
            
        # Normal NATS connection with retry logic
        try:
            self.connection_attempts += 1
            self.logger.info(f"Connecting to NATS server at {self.nats_url} (attempt {self.connection_attempts})")
            
            # Try multiple connection strategies
            # First try the full URL
            try:
                self.nc = await nats.connect(
                    self.nats_url,
                    reconnect_time_wait=self.reconnect_wait_time,
                    max_reconnect_attempts=self.max_reconnect_attempts,
                    connect_timeout=5  # 5 second connection timeout
                )
                self.is_connected = True
                self.connection_attempts = 0  # Reset counter on success
                self.logger.info(f"Successfully connected to NATS server at {self.nats_url}")
                return True
            except Exception as e1:
                self.logger.warning(f"Failed to connect using URL {self.nats_url}: {e1}")
                
                # Try connecting to localhost explicitly
                try:
                    self.logger.info("Trying direct localhost connection...")
                    self.nc = await nats.connect(
                        "nats://localhost:4222",
                        reconnect_time_wait=self.reconnect_wait_time,
                        max_reconnect_attempts=self.max_reconnect_attempts,
                        connect_timeout=5
                    )
                    self.is_connected = True
                    self.connection_attempts = 0  # Reset counter on success
                    self.logger.info("Successfully connected to NATS server using direct localhost connection")
                    return True
                except Exception as e2:
                    self.logger.warning(f"Failed to connect using direct localhost: {e2}")
                    
                    # Try connecting to 127.0.0.1 explicitly
                    try:
                        self.logger.info("Trying 127.0.0.1 connection...")
                        self.nc = await nats.connect(
                            "nats://127.0.0.1:4222",
                            reconnect_time_wait=self.reconnect_wait_time,
                            max_reconnect_attempts=self.max_reconnect_attempts,
                            connect_timeout=5
                        )
                        self.is_connected = True
                        self.connection_attempts = 0  # Reset counter on success
                        self.logger.info("Successfully connected to NATS server using 127.0.0.1 connection")
                        return True
                    except Exception as e3:
                        self.logger.error(f"All connection attempts failed: {e3}")
                        raise Exception(f"Failed all connection strategies: {e1}, {e2}, {e3}")
        except Exception as e:
            self.logger.error(f"NATS Error: {e}")
            self.is_connected = False
            
            # Implement exponential backoff for reconnection attempts
            if self.connection_attempts < self.max_reconnect_attempts:
                wait_time = self.reconnect_wait_time * (2 ** (self.connection_attempts - 1))
                self.logger.info(f"Will attempt reconnection in {wait_time} seconds")
                
            return False

    async def publish(self, topic: str, data: bytes):
        """Publish a message to a NATS topic.
        
        Args:
            topic: The topic to publish to.
            data: The message data as bytes.
            
        Returns:
            bool: True if the message was published successfully, False otherwise.
        """
        if not self.is_connected:
            self.logger.error("Cannot publish: not connected to NATS")
            return False
            
        if self.fallback_mode:
            self.logger.warning(f"Cannot publish to NATS in fallback mode: {topic}")
            return False
            
        try:
            # Extract trace_id from data if it's JSON
            trace_id = extract_trace_id(data)
            
            # If no trace_id found, add one
            if trace_id == 'N/A':
                try:
                    data_dict = json.loads(data.decode())
                    data_dict['trace_id'] = generate_trace_id()
                    trace_id = data_dict['trace_id']
                    # Re-encode with trace_id
                    data = json.dumps(data_dict).encode()
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Not JSON or can't decode, leave as is
                    pass
                
            # Set trace_id in context for logging
            token = set_trace_id(trace_id)
            try:
                await self.nc.publish(topic, data)
                log_with_trace_id(self.logger, 'info', f"Published message to topic '{topic}'", trace_id)
                return True
            finally:
                reset_trace_id(token)
        except Exception as e:
            self.logger.error(f"Error publishing to topic '{topic}': {e}")
            return False

    async def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a NATS topic.
        
        Args:
            topic: The topic to subscribe to.
            callback: The callback function to call when a message is received.
                      Should accept (subject, data) as parameters.
                      
        Returns:
            bool: True if the subscription was successful, False otherwise.
        """
        if topic in self.callbacks:
            self.logger.warning(f"Already subscribed to topic '{topic}'. Updating callback.")
            self.callbacks[topic] = callback
            return True
            
        self.callbacks[topic] = callback
        
        # If in fallback mode, just store the callback for direct event injection
        if self.fallback_mode:
            self.logger.info(f"Subscribed to topic '{topic}' in fallback mode")
            return True
            
        # Normal NATS subscription
        if not self.is_connected:
            self.logger.error("Cannot subscribe: not connected to NATS")
            return False
            
        try:
            handler = await self._message_handler(callback)
            sid = await self.nc.subscribe(topic, cb=handler)
            self.subscriptions[topic] = sid
            self.logger.info(f"Successfully subscribed to topic '{topic}' (SID: {sid})")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to topic '{topic}': {e}")
            return False

    async def unsubscribe(self, topic: str):
        """Unsubscribe from a NATS topic.
        
        Args:
            topic: The topic to unsubscribe from.
            
        Returns:
            bool: True if the unsubscription was successful, False otherwise.
        """
        # Remove the callback regardless of connection mode
        if topic in self.callbacks:
            del self.callbacks[topic]
            
        # If in fallback mode, just log and return
        if self.fallback_mode:
            self.logger.info(f"Unsubscribed from topic '{topic}' in fallback mode")
            return True
            
        # Normal NATS unsubscription
        if not self.is_connected:
            self.logger.warning("Cannot unsubscribe: not connected to NATS")
            return False
            
        if topic in self.subscriptions:
            sid = self.subscriptions[topic]
            try:
                await self.nc.unsubscribe(sid)
                del self.subscriptions[topic]
                self.logger.info(f"Successfully unsubscribed from topic '{topic}' (SID: {sid}).")
            except Exception as e:
                self.logger.error(f"Error unsubscribing from topic '{topic}' (SID: {sid}): {e}", exc_info=True)
        else:
            self.logger.warning(f"Not subscribed to topic '{topic}'.")

    async def close(self):
        """Close the connection to the NATS server."""
        if self.fallback_mode:
            self.logger.info("Closing fallback mode connection")
            self.is_connected = False
            return
            
        if self.is_connected and self.nc:
            try:
                await self.nc.drain()
                await self.nc.close()
                self.is_connected = False
                self.subscriptions = {}
                self.logger.info("Disconnected from NATS")
            except Exception as e:
                self.logger.error(f"Error closing NATS connection: {e}")
        else:
            self.logger.warning("Cannot close: not connected to NATS")

        # --- Callback Handlers --- #
    async def _error_cb(self, e):
        logger.error(f"NATS Error: {e}")

    async def _disconnected_cb(self):
        self.is_connected = False
        logger.warning("Disconnected from NATS.")

    async def _reconnected_cb(self):
        self.is_connected = True
        logger.info(f"Reconnected to NATS at {self.nc.connected_url.netloc}...")
        # Resubscribe logic could potentially go here if needed, though drain might handle it.

    async def _closed_cb(self):
        self.is_connected = False
        logger.info("NATS connection is closed.")

    async def _message_handler(self, callback: Callable):
        async def handler(msg):
            subject = msg.subject
            data = msg.data
            token = None
            
            try:
                # Assume message data is JSON encoded
                data_str = data.decode()
                decoded_data = json.loads(data_str)
                
                # Extract trace_id for logging
                trace_id = decoded_data.get('trace_id', 'N/A')
                token = set_trace_id(trace_id)
                
                # Validate event if schemas are available
                if SCHEMAS_AVAILABLE:
                    try:
                        decoded_data = validate_event(subject, decoded_data)
                    except Exception as ve:
                        log_with_trace_id(self.logger, 'warning', f"Event validation failed: {ve}", trace_id)
                
                log_with_trace_id(self.logger, 'debug', f"Received message on '{subject}'", trace_id)
                
                # Await the user-provided callback
                await callback(subject, decoded_data)
            except json.JSONDecodeError:
                self.logger.error(f"Received invalid JSON: {data_str[:100]}...")
            except Exception as e:
                trace_id = decoded_data.get('trace_id', 'N/A') if 'decoded_data' in locals() and isinstance(decoded_data, dict) else 'N/A'
                log_with_trace_id(self.logger, 'error', f"Error processing message: {e}", trace_id, exc_info=True)
            finally:
                # Reset trace_id context
                if token:
                    reset_trace_id(token)
            return handler

        # Direct event injection methods (for testing and fallback mode)
    
    async def inject_event(self, topic: str, data: Dict[str, Any]):
        """Inject an event directly, bypassing NATS.
        
        This is useful for testing or when NATS is unavailable.
        
        Args:
        topic: The topic to inject the event into.
        data: The event data.
            
        Returns:
        bool: True if the event was successfully injected.
        """
        # Ensure trace_id exists, generate if not
        data = ensure_trace_id(data)
        trace_id = data['trace_id']
        token = set_trace_id(trace_id)  # Set context var for logging
        
        try:
            # Validate event if schemas are available
            if SCHEMAS_AVAILABLE:
                try:
                    data = validate_event(topic, data)
                except Exception as ve:
                    log_with_trace_id(self.logger, 'warning', f"Event validation failed: {ve}", trace_id)
            
            log_with_trace_id(self.logger, 'info', f"Injecting event into topic {topic}", trace_id)
            
            # Store the event for later retrieval
            if topic not in self.injected_events:
                self.injected_events[topic] = []
            self.injected_events[topic].append(data)
            
            # If we have a callback for this topic, call it
            if topic in self.callbacks:
                try:
                    await self.callbacks[topic](topic, data)
                    return True
                except Exception as e:
                    log_with_trace_id(self.logger, 'error', f"Error processing injected event: {e}", trace_id, exc_info=True)
                    return False
            return True
        finally:
            # Always reset the trace_id context
            reset_trace_id(token)
    
    async def inject_sample_events(self, count: int = 1, interval: float = 1.0):
        """Inject a series of sample events for testing.
        
        Args:
            count: Number of events to inject.
            interval: Interval between events in seconds.
        """
        import random
        from datetime import timedelta
        
        task_types = ["sparc_analyze", "sparc_ingest", "sparc_refactor", "sparc_generate", "sparc_summarize"]
        statuses = ["queued", "in_progress", "completed", "failed"]
        status_weights = [0.1, 0.3, 0.4, 0.2]
        
        def generate_sparc_task():
            task_type = random.choice(task_types)
            status = random.choices(statuses, weights=status_weights)[0]
            
            result = ""
            if status == "completed":
                results = ["No issues found.", "Generated code stub.", "Analysis complete.", "Summary generated."]
                result = random.choice(results)
            elif status == "failed":
                results = ["Syntax error", "Timeout", "Resource error", "Validation failed"]
                result = random.choice(results)
            
            # Use the shared utility to create a timestamped event
            return create_timestamped_event(
                event_type="task_update",
                source_subsystem="SPARC",
                payload={
                    "id": f"T-{uuid.uuid4().hex[:6]}",
                    "type": task_type,
                    "status": status,
                    "result": result
                }
            )
        
        def generate_llm_log():
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
            
            # Use the shared utility to create a timestamped event
            return create_timestamped_event(
                event_type="llm_interaction",
                source_subsystem="LLM",
                payload={
                    "user": random.choice(users),
                    "prompt": random.choice(prompts),
                    "response": random.choice(responses)
                }
            )
        
        def generate_propagation_log():
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
            
            random_minutes = random.randint(0, 60*48)  # Up to 48 hours in minutes
            timestamp = datetime.now() - timedelta(minutes=random_minutes)
            
            # Use the shared utility to create a timestamped event
            return create_timestamped_event(
                event_type="pattern_propagation",
                source_subsystem="PROPAGATION",
                payload={
                    "subsystem": random.choice(subsystems),
                    "pattern": random.choice(patterns),
                    "status": random.choice(statuses),
                    "timestamp": timestamp.isoformat()
                }
            )
        
        # Topic to generator mapping
        generators = {
            "egos.sparc.tasks": generate_sparc_task,
            "egos.llm.logs": generate_llm_log,
            "egos.propagation.log": generate_propagation_log,
        }
        
        # Inject events
        for i in range(count):
            for topic, generator in generators.items():
                await self.inject_event(topic, generator())
            
            if i < count - 1:  # Don't sleep after the last event
                await asyncio.sleep(interval)

# Example usage (for testing purposes)
async def main_test():
    client = MyceliumClient()

    async def dummy_callback(subject, data):
        trace_id = data.get('trace_id', 'N/A')
        print(f"[TraceID: {trace_id}] [Callback] Received on '{subject}': {data}")

    if await client.connect():
        await client.subscribe("egos.test.topic", dummy_callback)
        
        # Test publishing with trace_id
        test_data = {
            "message": "Hello, NATS!",
            "timestamp": datetime.now().isoformat(),
            "trace_id": generate_trace_id()
        }
        await client.publish("egos.test.topic", json.dumps(test_data).encode())
        
        # Wait a bit to receive messages
        await asyncio.sleep(2)
        
        # Test direct event injection
        await client.inject_sample_events(count=2, interval=0.5)
        
        # Wait a bit more
        await asyncio.sleep(2)
        
        # Clean up
        await client.unsubscribe("egos.test.topic")
        await client.close()

if __name__ == "__main__":
    # This allows testing the client independently
    # Note: You need a NATS server running at NATS_URL
    # You can publish test messages using a NATS tool (e.g., nats cli)
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")