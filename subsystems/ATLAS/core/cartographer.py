"""
EGOS - ATLAS Subsystem Cartographer
====================================

Handles the dynamic mapping of system components and interactions,
listening to Mycelium messages and updating the internal map state.
Provides functionality to query and interact with the map.

Version: 1.0.0 (Migrated)
"""

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from datetime import datetime
import logging
from typing import Any, Dict, Optional, Set, Callable

# Replace the koios logger with standard logging for testing
# from koios.logger import KoiosLogger

# Create dummy classes if mycelium can't be imported
try:
    from mycelium import Message, MyceliumClient, Topic
except ImportError:
    # Mock the mycelium imports for tests
    class Message:
        """Mock Mycelium Message class for testing.

        Attributes:
            id: The mock message ID.
            data: The mock message data.
        """
        def __init__(self, id: Any, data: Any):
            """Initializes a mock Message.

            Args:
                id: The mock message ID.
                data: The mock message data.
            """
            self.id = id
            self.data = data

    class Topic:
        """Mock Mycelium Topic class for testing.

        Attributes:
            name (str): The name of the mock topic.
        """
        def __init__(self, name: str):
            """Initializes a mock Topic.

            Args:
                name: The name of the mock topic.
            """
            self.name = name

    class MyceliumClient:
        """Mock MyceliumClient class for testing.

        Attributes:
            published_messages (list): List of messages published via this mock.
            subscriptions (dict): Dictionary mapping subscribed topics to handlers.

        Methods:
            subscribe: Decorator to register a mock subscription handler.
            publish: Simulates publishing a message.
        """
        def __init__(self):
            """Initializes the mock client with empty state."""
            self.published_messages = []
            self.subscriptions = {}

        def subscribe(self, topic: str) -> Callable:
            """Decorator to mock subscribing a function to a topic.

            Args:
                topic: The topic name to subscribe to.

            Returns:
                A decorator function.
            """
            def decorator(func: Callable) -> Callable:
                """Inner decorator function that registers the subscription.

                Args:
                    func (Callable): The function to be called for the topic.

                Returns:
                    Callable: The original function, unchanged.
                """
                self.subscriptions[topic] = func
                return func

            return decorator

        async def publish(self, topic: str, data: dict):
            """Publishes a message to the specified topic.

            Args:
                topic: The topic to publish to.
                data: The message data to publish.
            """
            self.published_messages.append(
                {"topic": topic, "data": data, "timestamp": datetime.now().isoformat()}
            )


class AtlasCartographer:
    """System cartography: Manages the in-memory map state and Mycelium updates.

    This class holds the current representation of the system map (nodes,
    relationships, metadata) as potentially updated by messages received
    via Mycelium. It handles requests to generate maps based on this internal
    state and implements caching for map generation results.

    It does NOT typically perform the initial discovery or analysis itself,
    relying on external updates or potentially delegating complex generation/
    analysis tasks to ATLASCore.

    Attributes:
        logger (logging.Logger): Logger instance for this cartographer.
        mycelium (Optional[MyceliumClient]): The client for Mycelium communication.
        config (Dict[str, Any]): Configuration settings for the cartographer.
        system_map (Dict): Stores the nodes and their properties.
        relationships (Dict): Stores the relationships between nodes.
        metadata (Dict): Stores metadata about the map or system.
        analysis_cache (Dict): Caches results of map analysis.
        topics (Dict): Dictionary mapping semantic topic names to actual
                      Mycelium topic strings (loaded from config).
    """

    def __init__(
        self,
        # config_path: Optional[Path] = None, # Config should be passed by service
        config: Dict[str, Any],  # Expect config dict directly
        logger: logging.Logger,  # Expect logger instance
        mycelium_client: Optional[MyceliumClient] = None,
    ):
        """Initialize the cartographer.

        Args:
            config (Dict[str, Any]): Configuration dictionary, expects keys like
                                     'max_depth', 'cache_duration', and 'mycelium.topics'.
            logger (logging.Logger): Pre-configured logger instance.
            mycelium_client (Optional[MyceliumClient]): Mycelium client for messaging.
                                                     If provided, message handlers are set up.
        """
        # Use standard logging for testing
        # self.logger = logging.getLogger("ATLAS.Cartographer") # Replaced by passed logger
        self.logger = logger
        self.mycelium = mycelium_client

        # Load configuration
        # self.config = self._load_config(config_path) # Replaced by passed config
        self.config = config

        # Initialize system map
        self.system_map = {}
        self.relationships = {}
        self.metadata = {}
        self.analysis_cache = {}

        # Setup Mycelium handlers if client provided
        if self.mycelium:
            self.topics = self.config["mycelium"]["topics"]
            self._setup_mycelium_handlers()

        self.logger.info("AtlasCartographer initialized")

    def _setup_mycelium_handlers(self):
        """Setup handlers for Mycelium messages to update internal state."""

        @self.mycelium.subscribe(self.topics["map_request"])
        async def handle_map_request(message: Message):
            """Handle incoming mapping requests based on current internal state."""
            try:
                self.logger.info(
                    f"Received Cartographer map request: {message.id}"
                )  # Clarify this is Cartographer level

                # Extract mapping parameters
                target = message.data["target"]
                depth = message.data.get("depth", 1)
                include_metadata = message.data.get("include_metadata", True)

                # Generate map
                map_result = await self.generate_map(target, depth, include_metadata)

                # Publish result
                await self.mycelium.publish(
                    self.topics["map_result"],
                    {
                        "request_id": message.id,
                        "target": target,
                        "map": map_result,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            except Exception as e:
                self.logger.error(f"Error handling map request: {e}", exc_info=True)
                await self.mycelium.publish(
                    self.topics["map_result"],
                    {"request_id": message.id, "status": "error", "error": str(e)},
                )

        @self.mycelium.subscribe(self.topics["metadata_update"])
        async def handle_metadata_update(message: Message):
            """Handle requests to update component metadata in the internal state."""
            try:
                self.logger.info(f"Received metadata update request: {message.id}")

                # Check for required fields
                if "component" not in message.data:
                    raise ValueError("Missing 'component' field in metadata update request")
                if "metadata" not in message.data:
                    raise ValueError("Missing 'metadata' field in metadata update request")

                # Update metadata
                component = message.data["component"]
                metadata = message.data["metadata"]
                await self.update_metadata(component, metadata)

                # Publish confirmation
                await self.mycelium.publish(
                    self.topics["metadata_status"],
                    {"request_id": message.id, "status": "success", "component": component},
                )

            except Exception as e:
                self.logger.error(f"Error handling metadata update: {e}", exc_info=True)
                await self.mycelium.publish(
                    self.topics["metadata_status"],
                    {"request_id": message.id, "status": "error", "error": str(e)},
                )

        @self.mycelium.subscribe(self.topics["relationship_update"])
        async def handle_relationship_update(message: Message):
            """Handle requests to update relationships in the internal state."""
            try:
                self.logger.info(f"Received relationship update request: {message.id}")

                # Check for required fields
                if "source" not in message.data:
                    raise ValueError("Missing 'source' field in relationship update request")
                if "target" not in message.data:
                    raise ValueError("Missing 'target' field in relationship update request")
                if "type" not in message.data:
                    raise ValueError("Missing 'type' field in relationship update request")

                # Update relationship
                source = message.data["source"]
                target = message.data["target"]
                relationship_type = message.data["type"]
                metadata = message.data.get("metadata", {})

                await self.update_relationship(source, target, relationship_type, metadata)

                # Publish confirmation
                await self.mycelium.publish(
                    self.topics["relationship_status"],
                    {
                        "request_id": message.id,
                        "status": "success",
                        "source": source,
                        "target": target,
                    },
                )

            except Exception as e:
                self.logger.error(
                    f"Error handling relationship update: {e}", exc_info=True
                )
                await self.mycelium.publish(
                    self.topics["relationship_status"],
                    {"request_id": message.id, "status": "error", "error": str(e)},
                )

    async def _publish_alert(self, alert_type: str, message: str, details: Dict[str, Any]):
        """Publish an alert through Mycelium."""
        if not self.mycelium:
            return

        try:
            await self.mycelium.publish(
                self.topics["alert"],
                {
                    "type": alert_type,
                    "message": message,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            self.logger.error(f"Failed to publish alert: {e}")

    async def generate_map(
        self, target: str, depth: int = 1, include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Generate a map subsection from the internal state.

        Traverses the internally stored relationships (`self.relationships`)
        starting from the target component up to the specified depth.
        Uses cached results if available and valid.

        Args:
            target: The starting component ID for the map.
            depth: Maximum relationship depth to traverse.
            include_metadata: Whether to include component metadata (`self.metadata`).

        Returns:
            A dictionary representing the map subsection with 'nodes',
            'relationships', and potentially 'metadata' keys.
        """
        try:
            # Check cache first
            cache_key = f"{target}:{depth}:{include_metadata}"
            if cache_key in self.analysis_cache:
                cache_entry = self.analysis_cache[cache_key]
                cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()

                if cache_age < self.config["cache_duration"]:
                    self.logger.info(f"Returning cached map for {target} (age: {cache_age:.1f}s)")
                    return cache_entry["result"]
                else:
                    self.logger.info(f"Cache expired for {target} (age: {cache_age:.1f}s)")

            if depth > self.config["max_depth"]:
                depth = self.config["max_depth"]
                await self._publish_alert(
                    "map_depth_limited",
                    f"Map depth limited to {self.config['max_depth']} for target {target}",
                    {"target": target, "requested_depth": depth},
                )

            visited = set()
            result = await self._build_map_recursive(target, depth, visited, include_metadata)

            # Update cache
            self.analysis_cache[cache_key] = {"result": result, "timestamp": datetime.now()}

            return result

        except Exception as e:
            self.logger.error(f"Error generating map for {target}: {e}", exc_info=True)
            raise

    async def _build_map_recursive(
        self, target: str, depth: int, visited: Set[str], include_metadata: bool
    ) -> Dict[str, Any]:
        """Build a map recursively (internal implementation, wraps _map_component)."""
        # This is a stub method that just wraps _map_component for testing mocking purposes
        result = {"nodes": {}, "relationships": [], "metadata": {} if include_metadata else None}
        await self._map_component(target, depth, visited, result, include_metadata)
        return result

    async def _map_component(
        self,
        component: str,
        depth: int,
        visited: Set[str],
        result: Dict[str, Any],
        include_metadata: bool,
    ):
        """Recursively traverse and map components based on internal state."""
        if depth < 0 or component in visited:
            return

        visited.add(component)

        # Only add to nodes if it exists in the system_map
        if component in self.system_map:
            result["nodes"][component] = self.system_map[component]

            # Only add metadata for components that exist
            if include_metadata and component in self.metadata:
                result["metadata"][component] = self.metadata[component]

        if component in self.relationships:
            for rel in self.relationships[component]:
                result["relationships"].append(rel)
                target = rel["target"]
                if target not in visited:
                    await self._map_component(target, depth - 1, visited, result, include_metadata)

    async def update_metadata(self, component: str, metadata: Dict[str, Any]):
        """Update metadata for a component in the internal state (`self.metadata`).

        Also invalidates relevant cache entries.
        """
        try:
            # Invalidate cache entries for this component
            self._invalidate_cache_for_component(component)

            self.metadata[component] = metadata
            self.logger.info(f"Updated metadata for {component}")

        except Exception as e:
            self.logger.error(f"Error updating metadata for {component}: {e}", exc_info=True)
            raise

    async def update_relationship(
        self, source: str, target: str, relationship_type: str, metadata: Dict[str, Any] = None
    ):
        """Update or create a relationship in the internal state (`self.relationships`).

        Removes any existing relationship of the same type between source and target
        before adding the new one. Invalidates relevant cache entries.
        """
        try:
            # Invalidate cache entries for source and target
            self._invalidate_cache_for_component(source)
            self._invalidate_cache_for_component(target)

            if source not in self.relationships:
                self.relationships[source] = []

            # Update existing relationship or add new one
            relationship = {
                "source": source,
                "target": target,
                "type": relationship_type,
                "metadata": metadata or {},
            }

            # Remove existing relationship if present
            self.relationships[source] = [
                r
                for r in self.relationships[source]
                if r["target"] != target or r["type"] != relationship_type
            ]
            self.relationships[source].append(relationship)

            self.logger.info(f"Updated relationship: {source} -> {target} ({relationship_type})")

        except Exception as e:
            self.logger.error(
                f"Error updating relationship {source} -> {target}: {e}", exc_info=True
            )
            raise

    def _invalidate_cache_for_component(self, component: str):
        """Invalidate cache entries related to a specific component."""
        keys_to_remove = []
        for key in self.analysis_cache:
            if key.startswith(f"{component}:"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.analysis_cache[key]
            self.logger.debug(f"Invalidated cache entry: {key}")
