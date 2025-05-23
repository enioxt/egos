"""TODO: Module docstring for broker.py"""
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Mycelium Network - Message Broker Module
--------------------------------------------
Implements the central message broker component for the Mycelium Network,
responsible for routing messages between subsystems.

This module provides the core messaging infrastructure with:
- Connection management for subsystems
- Message routing based on destination or topic
- Pub/sub topic registry
- Trace ID propagation for message tracking
- Error handling and recovery mechanisms

EGOS Principles Applied:
- Conscious Modularity: Separation of broker components
- Systemic Cartography: Tracing message flow through the system
- Reciprocal Trust: Reliable message delivery with acknowledgments
- Sacred Privacy: Protecting message integrity and privacy
"""

import uuid
import logging
import asyncio
import datetime
import re
from typing import Dict, List, Set, Optional, Any, Callable, Awaitable, Tuple, Union
from collections import defaultdict
from enum import Enum
from pydantic import BaseModel, Field, validator

from subsystems.MYCELIUM.core.message import MyceliumMessage

# Setup logging
logger = logging.getLogger("mycelium.broker")

# Custom types
ConnectionId = str
TopicPattern = str
CallbackFunc = Callable<!-- TO_BE_REPLACED -->
SubscriptionId = str


class ConnectionStatus(Enum):
            Attributes:
            None
"""Status of a connection to a subsystem."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class BrokerConfig(BaseModel):
    """Configuration for the Mycelium message broker."""
    
    node_id: str = Field(default_factory=lambda: f"broker-{uuid.uuid4().hex[:8]}")
    max_queue_size: int = 1000
    max_subscribers_per_topic: int = 100
    default_message_ttl: int = 60  # seconds
    persistence_enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    monitoring_enabled: bool = True
    max_hop_count: int = 10
    
    @validator('max_queue_size')
    def validate_queue_size(cls, v: int) -> int:
        """Validate the maximum queue size."""
        if v <= 0:
            raise ValueError("Queue size must be positive")
        return v


class Connection(BaseModel):
    """Represents a connection from a subsystem to the broker."""
    
    connection_id: ConnectionId
    subsystem_name: str
    status: ConnectionStatus = ConnectionStatus.PENDING
    connected_at: Optional[datetime.datetime] = None
    last_activity: Optional[datetime.datetime] = None
    send_queue: List[MyceliumMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def mark_connected(self) -> None:
        """Mark the connection as connected."""
        self.status = ConnectionStatus.CONNECTED
        self.connected_at = datetime.datetime.now()
        self.last_activity = self.connected_at
    
    def mark_disconnected(self) -> None:
        """Mark the connection as disconnected."""
        self.status = ConnectionStatus.DISCONNECTED
    
    def mark_error(self) -> None:
        """Mark the connection as having an error."""
        self.status = ConnectionStatus.ERROR
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.datetime.now()
    
    def add_to_queue(self, message: MyceliumMessage) -> bool:
        """
        Add a message to the send queue.
        
        Args:
            message: The message to queue
            
        Returns:
            True if the message was added, False if the queue is full
        """
        # In a real implementation, this would use a proper bounded queue
        self.send_queue.append(message)
        return True


class Subscription(BaseModel):
    """Represents a subscription to a topic."""
    
    subscription_id: SubscriptionId = Field(default_factory=lambda: f"sub-{uuid.uuid4().hex[:8]}")
    connection_id: ConnectionId
    topic_pattern: TopicPattern
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    regex_pattern: Optional[str] = None
    
    def __init__(self, **data):
        """Initialize the subscription and compile the regex pattern."""
        super().__init__(**data)
        
        # Convert topic pattern to regex for matching
        # Replace * with wildcard regex and escape other special chars
        pattern = self.topic_pattern.replace('.', r'\.')
        pattern = pattern.replace('*', '[^.]+')
        self.regex_pattern = f"^{pattern}$"
    
    def matches(self, topic: str) -> bool:
        """
        Check if this subscription matches the given topic.
        
        Args:
            topic: The topic to check against this subscription
            
        Returns:
            True if the topic matches this subscription's pattern
        """
        if not self.regex_pattern:
            return False
        
        return bool(re.match(self.regex_pattern, topic))


class MyceliumBroker:
    """
    Central message broker for the Mycelium Network.
    
    Handles connections from subsystems, routes messages,
    and manages pub/sub topics.
    """
    
    def __init__(self, config: Optional[BrokerConfig] = None):
        """
        Initialize the message broker.
        
        Args:
            config: Optional broker configuration
        """
        self.config = config or BrokerConfig()
        self.connections: Dict[ConnectionId, Connection] = {}
        self.subsystem_connections: Dict[str, List[ConnectionId]] = defaultdict(list)
        self.subscriptions: Dict[SubscriptionId, Subscription] = {}
        self.connection_subscriptions: Dict[ConnectionId, List[SubscriptionId]] = defaultdict(list)
        self.topic_subscriptions: Dict[str, List[SubscriptionId]] = defaultdict(list)
        self.pattern_subscriptions: List[SubscriptionId] = []
        
        # Message delivery tracking
        self.pending_messages: Dict[uuid.UUID, MyceliumMessage] = {}
        self.acknowledged_messages: Set[uuid.UUID] = set()
        
        # Statistics
        self.message_count = 0
        self.error_count = 0
        self.start_time = datetime.datetime.now()
        
        logger.info(f"Initializing Mycelium Broker with ID {self.config.node_id}")
    
    async def start(self) -> None:
        """Start the broker service."""
        logger.info("Starting Mycelium Broker service")
        # In a real implementation, this would set up network listeners,
        # initialize persistent storage, etc.
        
        # Start background tasks
        if self.config.monitoring_enabled:
            # Task for monitoring would be started here in a real implementation
            pass
    
    async def stop(self) -> None:
        """Stop the broker service."""
        logger.info("Stopping Mycelium Broker service")
        # In a real implementation, this would close connections,
        # flush any pending messages, etc.
    
    async def register_client(self, subsystem_name: str, metadata: Optional[Dict[str, Any]] = None) -> ConnectionId:
        """
        Register a new client connection.
        
        Args:
            subsystem_name: Name of the connecting subsystem
            metadata: Optional connection metadata
            
        Returns:
            The connection ID for the registered client
        """
        connection_id = f"{subsystem_name}-{uuid.uuid4().hex[:8]}"
        
        connection = Connection(
            connection_id=connection_id,
            subsystem_name=subsystem_name,
            metadata=metadata or {}
        )
        
        connection.mark_connected()
        
        self.connections[connection_id] = connection
        self.subsystem_connections[subsystem_name].append(connection_id)
        
        logger.info(f"Registered new client: {subsystem_name} (connection_id: {connection_id})")
        return connection_id
    
    async def unregister_client(self, connection_id: ConnectionId) -> bool:
        """
        Unregister a client connection.
        
        Args:
            connection_id: The connection ID to unregister
            
        Returns:
            True if successfully unregistered, False otherwise
        """
        if connection_id not in self.connections:
            logger.warning(f"Attempted to unregister unknown connection: {connection_id}")
            return False
        
        connection = self.connections[connection_id]
        connection.mark_disconnected()
        
        # Remove from subsystem connections
        self.subsystem_connections[connection.subsystem_name].remove(connection_id)
        if not self.subsystem_connections[connection.subsystem_name]:
            del self.subsystem_connections[connection.subsystem_name]
        
        # Clean up subscriptions
        subscription_ids = self.connection_subscriptions.get(connection_id, [])
        for subscription_id in subscription_ids:
            await self._remove_subscription(subscription_id)
        
        # Remove connection entirely
        del self.connections[connection_id]
        if connection_id in self.connection_subscriptions:
            del self.connection_subscriptions[connection_id]
        
        logger.info(f"Unregistered client: {connection.subsystem_name} (connection_id: {connection_id})")
        return True
    
    async def route_message(self, message: MyceliumMessage) -> bool:
        """
        Route a message to its destination(s).
        
        Args:
            message: The message to route
            
        Returns:
            True if the message was successfully routed
        """
        # Track statistics
        self.message_count += 1
        
        # Add routing information
        message.add_routing_info(self.config.node_id)
        message.increment_hops()
        
        # Check hop count to prevent infinite loops
        if message.metadata.get('hops', 0) > self.config.max_hop_count:
            logger.warning(f"Message exceeded maximum hop count: {message.message_id}")
            self.error_count += 1
            return False
        
        # Handle based on message type (direct, topic, or broadcast)
        if message.destination == "BROADCAST":
            return await self._broadcast_message(message)
        elif message.destination is not None:
            return await self._route_direct_message(message)
        elif message.topic is not None:
            return await self._route_topic_message(message)
        else:
            logger.error(f"Message has neither destination nor topic: {message.message_id}")
            self.error_count += 1
            return False
    
    async def _route_direct_message(self, message: MyceliumMessage) -> bool:
        """
        Route a message to a specific destination.
        
        Args:
            message: The message to route
            
        Returns:
            True if the message was successfully routed
        """
        if not message.destination:
            logger.error(f"Direct message without destination: {message.message_id}")
            self.error_count += 1
            return False
        
        # Find connections for the destination subsystem
        connection_ids = self.subsystem_connections.get(message.destination, [])
        
        if not connection_ids:
            logger.warning(f"No connections found for destination: {message.destination}")
            self.error_count += 1
            return False
        
        # For simplicity, we'll send to the first connection
        # In a real implementation, we'd use load balancing or other strategies
        connection_id = connection_ids[0]
        connection = self.connections.get(connection_id)
        
        if not connection or connection.status != ConnectionStatus.CONNECTED:
            logger.warning(f"Selected connection unavailable: {connection_id}")
            self.error_count += 1
            return False
        
        # Add to the connection's send queue
        success = connection.add_to_queue(message)
        connection.update_activity()
        
        logger.debug(f"Routed direct message from {message.source} to {message.destination}")
        return success
    
    async def _route_topic_message(self, message: MyceliumMessage) -> bool:
        """
        Route a message to all subscribers of a topic.
        
        Args:
            message: The message to route
            
        Returns:
            True if the message was successfully routed to at least one subscriber
        """
        if not message.topic:
            logger.error(f"Topic message without topic: {message.message_id}")
            self.error_count += 1
            return False
        
        # Find all subscriptions that match this topic
        matching_subscription_ids = []
        
        # First, check exact topic matches
        matching_subscription_ids.extend(self.topic_subscriptions.get(message.topic, []))
        
        # Then check pattern matches
        for subscription_id in self.pattern_subscriptions:
            subscription = self.subscriptions.get(subscription_id)
            if subscription and subscription.matches(message.topic):
                matching_subscription_ids.append(subscription_id)
        
        if not matching_subscription_ids:
            logger.debug(f"No subscribers found for topic: {message.topic}")
            return True  # Not an error, just no subscribers
        
        # Route to each matching subscription
        success = False
        delivered_count = 0
        
        for subscription_id in matching_subscription_ids:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                continue
            
            connection_id = subscription.connection_id
            connection = self.connections.get(connection_id)
            
            if not connection or connection.status != ConnectionStatus.CONNECTED:
                continue
            
            # Add to the connection's send queue
            if connection.add_to_queue(message):
                connection.update_activity()
                delivered_count += 1
                success = True
        
        logger.debug(f"Routed topic message to {delivered_count} subscribers: {message.topic}")
        return success
    
    async def _broadcast_message(self, message: MyceliumMessage) -> bool:
        """
        Broadcast a message to all connected subsystems.
        
        Args:
            message: The message to broadcast
            
        Returns:
            True if the message was successfully broadcast
        """
        # Send to all connected clients except the source
        success = False
        delivered_count = 0
        
        for connection_id, connection in self.connections.items():
            # Skip the source
            if connection.subsystem_name == message.source:
                continue
            
            # Skip disconnected connections
            if connection.status != ConnectionStatus.CONNECTED:
                continue
            
            # Add to the connection's send queue
            if connection.add_to_queue(message):
                connection.update_activity()
                delivered_count += 1
                success = True
        
        logger.debug(f"Broadcast message to {delivered_count} subsystems")
        return success
    
    async def subscribe(self, connection_id: ConnectionId, topic_pattern: str) -> Optional[SubscriptionId]:
        """
        Subscribe a connection to a topic pattern.
        
        Args:
            connection_id: The connection to subscribe
            topic_pattern: The topic pattern to subscribe to
            
        Returns:
            The subscription ID if successful, None otherwise
        """
        if connection_id not in self.connections:
            logger.warning(f"Cannot subscribe: unknown connection {connection_id}")
            return None
        
        connection = self.connections[connection_id]
        
        # Create the subscription
        subscription = Subscription(
            connection_id=connection_id,
            topic_pattern=topic_pattern
        )
        
        # Store the subscription
        self.subscriptions[subscription.subscription_id] = subscription
        self.connection_subscriptions[connection_id].append(subscription.subscription_id)
        
        # If it's an exact topic (no wildcards), store in topic_subscriptions for faster lookup
        if '*' not in topic_pattern:
            self.topic_subscriptions[topic_pattern].append(subscription.subscription_id)
        else:
            # Otherwise store in pattern_subscriptions which requires regex matching
            self.pattern_subscriptions.append(subscription.subscription_id)
        
        logger.info(f"Subscription created: {connection.subsystem_name} to '{topic_pattern}' " 
                    f"(subscription_id: {subscription.subscription_id})")
        
        return subscription.subscription_id
    
    async def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            subscription_id: The subscription ID to remove
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        return await self._remove_subscription(subscription_id)
    
    async def _remove_subscription(self, subscription_id: SubscriptionId) -> bool:
        """
        Remove a subscription.
        
        Args:
            subscription_id: The subscription ID to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        if subscription_id not in self.subscriptions:
            return False
        
        subscription = self.subscriptions[subscription_id]
        connection_id = subscription.connection_id
        
        # Remove from connection_subscriptions
        if connection_id in self.connection_subscriptions:
            if subscription_id in self.connection_subscriptions[connection_id]:
                self.connection_subscriptions[connection_id].remove(subscription_id)
            
            if not self.connection_subscriptions[connection_id]:
                del self.connection_subscriptions[connection_id]
        
        # Remove from topic_subscriptions or pattern_subscriptions
        if '*' not in subscription.topic_pattern:
            topic = subscription.topic_pattern
            if topic in self.topic_subscriptions and subscription_id in self.topic_subscriptions[topic]:
                self.topic_subscriptions[topic].remove(subscription_id)
                
                if not self.topic_subscriptions[topic]:
                    del self.topic_subscriptions[topic]
        else:
            if subscription_id in self.pattern_subscriptions:
                self.pattern_subscriptions.remove(subscription_id)
        
        # Remove the subscription itself
        del self.subscriptions[subscription_id]
        
        logger.info(f"Subscription removed: {subscription_id}")
        return True
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get broker statistics.
        
        Returns:
            Dictionary of broker statistics
        """
        uptime = datetime.datetime.now() - self.start_time
        
        return {
            "node_id": self.config.node_id,
            "uptime_seconds": uptime.total_seconds(),
            "start_time": self.start_time.isoformat(),
            "connections": len(self.connections),
            "subscriptions": len(self.subscriptions),
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "subsystems": list(self.subsystem_connections.keys())
        }


# Factory function
def create_broker(config: Optional[Dict[str, Any]] = None) -> MyceliumBroker:
    """
    Create a new message broker instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured MyceliumBroker instance
    """
    broker_config = BrokerConfig(**(config or {}))
    return MyceliumBroker(config=broker_config)