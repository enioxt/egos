"""TODO: Module docstring for client.py"""
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Mycelium Network - Client Module
-------------------------------------
Provides the client interface for subsystems to connect to the Mycelium Network.

This module offers a high-level API that abstracts the underlying communication
mechanisms, allowing subsystems to easily send messages, subscribe to topics,
and make request-response calls across the EGOS ecosystem.

EGOS Principles Applied:
- Universal Accessibility: Simple, intuitive API for all subsystems
- Reciprocal Trust: Reliable message delivery with acknowledgment
- Sacred Privacy: Secure communication with proper authentication
- Conscious Modularity: Clean separation between client and network internals
"""

import uuid
import asyncio
import logging
import datetime
import json
from typing import Dict, List, Set, Optional, Any, Callable, Awaitable, Tuple, Union, TypeVar, Generic
from enum import Enum
from pydantic import BaseModel, Field, validator

from subsystems.MYCELIUM.core.message import (
    MyceliumMessage, 
    MyceliumRequestMessage,
    create_direct_message,
    create_topic_message,
    create_request_message,
    create_broadcast_message
)

# Setup logging
logger = logging.getLogger("mycelium.client")

# Type definitions
T = TypeVar('T')
SubscriptionId = str
RequestId = str
CallbackFunc = Callable[[MyceliumMessage], Awaitable[None]]


class ClientStatus(Enum):
            Attributes:
            None
"""Status of a client connection to the Mycelium Network."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class ClientConfig(BaseModel):
    """Configuration for the Mycelium client."""
    
    broker_address: str = "localhost"
    broker_port: int = 8765
    auto_reconnect: bool = True
    reconnect_delay: float = 1.0  # seconds
    max_reconnect_attempts: int = 5
    request_timeout: float = 30.0  # seconds
    connection_timeout: float = 5.0  # seconds
    heartbeat_interval: float = 15.0  # seconds
    trace_id_header: str = "mycelium-trace-id"
    verbose_logging: bool = False


class RequestFuture(Generic[T]):
    """
    Future for tracking pending requests and their responses.
    
    This allows for both async/await usage and callback-based
    handling of responses.
    """
    
    def __init__(self, request_id: RequestId, timeout: float = 30.0):
        """
        Initialize a request future.
        
        Args:
            request_id: The ID of the request
            timeout: Timeout in seconds
        """
        self.request_id = request_id
        self.timeout = timeout
        self.completed = asyncio.Event()
        self.result: Optional[T] = None
        self.error: Optional[Exception] = None
        self.callbacks: List[Callable[[Optional[T], Optional[Exception]], None]] = []
    
    async def wait(self) -> T:
        """
        Wait for the request to complete.
        
        Returns:
            The result of the request
            
        Raises:
            Exception: If the request failed
            asyncio.TimeoutError: If the request timed out
        """
        try:
            await asyncio.wait_for(self.completed.wait(), timeout=self.timeout)
        except asyncio.TimeoutError:
            self.set_error(asyncio.TimeoutError(f"Request {self.request_id} timed out after {self.timeout} seconds"))
            raise asyncio.TimeoutError(f"Request {self.request_id} timed out after {self.timeout} seconds")
        
        if self.error:
            raise self.error
        
        return self.result
    
    def set_result(self, result: T) -> None:
        """
        Set the result of the request.
        
        Args:
            result: The result value
        """
        self.result = result
        self.completed.set()
        self._notify_callbacks()
    
    def set_error(self, error: Exception) -> None:
        """
        Set an error for the request.
        
        Args:
            error: The error that occurred
        """
        self.error = error
        self.completed.set()
        self._notify_callbacks()
    
    def add_callback(self, callback: Callable[[Optional[T], Optional[Exception]], None]) -> None:
        """
        Add a callback to be called when the request completes.
        
        Args:
            callback: Function to call with the result or error
        """
        self.callbacks.append(callback)
        
        # If already completed, call the callback immediately
        if self.completed.is_set():
            callback(self.result, self.error)
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of the result or error."""
        for callback in self.callbacks:
            try:
                callback(self.result, self.error)
            except Exception as e:
                logger.error(f"Error in request callback: {e}")


class TopicSubscription:
    """
    Manages a subscription to a topic pattern.
    
    Handles message callbacks and manages the subscription lifecycle.
    """
    
    def __init__(
        self, 
        subscription_id: SubscriptionId, 
        topic_pattern: str,
        callback: CallbackFunc
    ):
        """
        Initialize a topic subscription.
        
        Args:
            subscription_id: ID of the subscription from the broker
            topic_pattern: The topic pattern subscribed to
            callback: Async function to call for matching messages
        """
        self.subscription_id = subscription_id
        self.topic_pattern = topic_pattern
        self.callback = callback
        self.created_at = datetime.datetime.now()
        self.last_message_at: Optional[datetime.datetime] = None
        self.message_count = 0
    
    async def handle_message(self, message: MyceliumMessage) -> None:
        """
        Handle a message received for this subscription.
        
        Args:
            message: The received message
        """
        self.message_count += 1
        self.last_message_at = datetime.datetime.now()
        
        try:
            await self.callback(message)
        except Exception as e:
            logger.error(f"Error in subscription callback: {e}")


class MyceliumClient:
    """
    Client for connecting to the Mycelium Network.
    
    Provides a high-level API for sending messages, subscribing to topics,
    and making request-response calls across the EGOS ecosystem.
    """
    
    def __init__(self, subsystem_name: str, config: Optional[Union[ClientConfig, Dict[str, Any]]] = None):
        """
        Initialize a Mycelium client.
        
        Args:
            subsystem_name: Name of the subsystem using this client
            config: Optional client configuration
        """
        self.subsystem_name = subsystem_name
        self.config = config if isinstance(config, ClientConfig) else ClientConfig(**(config or {}))
        
        # Connection state
        self.status = ClientStatus.DISCONNECTED
        self.connection_id: Optional[str] = None
        self.connected_at: Optional[datetime.datetime] = None
        self.last_activity: Optional[datetime.datetime] = None
        self.disconnect_reason: Optional[str] = None
        self.reconnect_attempts = 0
        
        # Message tracking
        self.sent_messages: Set[uuid.UUID] = set()
        self.pending_requests: Dict[RequestId, RequestFuture] = {}
        
        # Subscriptions
        self.subscriptions: Dict[SubscriptionId, TopicSubscription] = {}
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.failed_messages = 0
        self.reconnections = 0
        
        # Event loop and tasks
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._message_handler_task: Optional[asyncio.Task] = None
        
        logger.info(f"Initializing Mycelium client for {subsystem_name}")
        
        # If verbose logging is enabled, set the logger level
        if self.config.verbose_logging:
            logger.setLevel(logging.DEBUG)
    
    async def connect(self) -> bool:
        """
        Connect to the Mycelium Network.
        
        Returns:
            True if connected successfully, False otherwise
        """
        if self.status == ClientStatus.CONNECTED:
            logger.warning("Already connected to Mycelium Network")
            return True
        
        if self.status == ClientStatus.CONNECTING:
            logger.warning("Connection already in progress")
            return False
        
        self.status = ClientStatus.CONNECTING
        logger.info(f"Connecting to Mycelium Network at {self.config.broker_address}:{self.config.broker_port}")
        
        # Store the event loop for future async operations
        self._event_loop = asyncio.get_running_loop()
        
        try:
            # In a real implementation, this would establish a network connection
            # For this prototype, we'll simulate a successful connection
            
            # Register with the broker and get a connection ID
            self.connection_id = f"{self.subsystem_name}-{uuid.uuid4().hex[:8]}"
            self.connected_at = datetime.datetime.now()
            self.last_activity = self.connected_at
            self.status = ClientStatus.CONNECTED
            self.reconnect_attempts = 0
            
            # Start heartbeat and message handler tasks
            self._start_background_tasks()
            
            logger.info(f"Connected to Mycelium Network (connection_id: {self.connection_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Mycelium Network: {e}")
            self.status = ClientStatus.ERROR
            self.disconnect_reason = str(e)
            
            # If auto-reconnect is enabled, schedule a reconnection attempt
            if self.config.auto_reconnect and self.reconnect_attempts < self.config.max_reconnect_attempts:
                self.reconnect_attempts += 1
                
                # Schedule reconnection
                if self._event_loop:
                    self._event_loop.call_later(
                        self.config.reconnect_delay,
                        lambda: asyncio.create_task(self._try_reconnect())
                    )
            
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the Mycelium Network.
        
        Returns:
            True if disconnected successfully, False otherwise
        """
        if self.status == ClientStatus.DISCONNECTED:
            logger.warning("Already disconnected from Mycelium Network")
            return True
        
        logger.info("Disconnecting from Mycelium Network")
        
        # Cancel background tasks
        self._cancel_background_tasks()
        
        try:
            # In a real implementation, this would close the network connection
            # For this prototype, we'll simulate a successful disconnection
            
            # Update state
            self.status = ClientStatus.DISCONNECTED
            self.disconnect_reason = "Client requested disconnect"
            
            logger.info("Disconnected from Mycelium Network")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Mycelium Network: {e}")
            self.status = ClientStatus.ERROR
            self.disconnect_reason = str(e)
            return False
    
    async def _try_reconnect(self) -> None:
        """Attempt to reconnect to the Mycelium Network."""
        if self.status == ClientStatus.CONNECTED:
            return
        
        logger.info(f"Attempting to reconnect (attempt {self.reconnect_attempts} of {self.config.max_reconnect_attempts})")
        
        try:
            await self.connect()
            if self.status == ClientStatus.CONNECTED:
                self.reconnections += 1
                logger.info("Reconnection successful")
                
                # Re-establish subscriptions
                for subscription_id, subscription in list(self.subscriptions.items()):
                    await self.subscribe(subscription.topic_pattern, subscription.callback)
        except Exception as e:
            logger.error(f"Reconnection attempt failed: {e}")
            
            # Schedule another attempt if allowed
            if self.config.auto_reconnect and self.reconnect_attempts < self.config.max_reconnect_attempts:
                self.reconnect_attempts += 1
                
                # Schedule reconnection
                if self._event_loop:
                    self._event_loop.call_later(
                        self.config.reconnect_delay,
                        lambda: asyncio.create_task(self._try_reconnect())
                    )
    
    def _start_background_tasks(self) -> None:
        """Start background tasks for heartbeat and message handling."""
        if self._event_loop:
            if not self._heartbeat_task:
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            if not self._message_handler_task:
                self._message_handler_task = asyncio.create_task(self._message_handler_loop())
    
    def _cancel_background_tasks(self) -> None:
        """Cancel background tasks."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
        
        if self._message_handler_task:
            self._message_handler_task.cancel()
            self._message_handler_task = None
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to the broker."""
        try:
            while self.status == ClientStatus.CONNECTED:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if self.status != ClientStatus.CONNECTED:
                    break
                
                try:
                    # Send a heartbeat message
                    logger.debug("Sending heartbeat")
                    
                    # In a real implementation, this would send a heartbeat message
                    # For this prototype, we'll just update the last activity timestamp
                    self.last_activity = datetime.datetime.now()
                    
                except Exception as e:
                    logger.error(f"Error sending heartbeat: {e}")
        except asyncio.CancelledError:
            logger.debug("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
    
    async def _message_handler_loop(self) -> None:
        """Handle incoming messages from the broker."""
        try:
            while self.status == ClientStatus.CONNECTED:
                await asyncio.sleep(0.1)  # Simulate periodic message checking
                
                if self.status != ClientStatus.CONNECTED:
                    break
                
                try:
                    # In a real implementation, this would receive messages from the broker
                    # For this prototype, we'll just simulate periodic handling
                    pass
                    
                except Exception as e:
                    logger.error(f"Error handling messages: {e}")
        except asyncio.CancelledError:
            logger.debug("Message handler task cancelled")
        except Exception as e:
            logger.error(f"Error in message handler loop: {e}")
    
    async def send(
        self, 
        destination: str, 
        payload: Dict[str, Any], 
        trace_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Send a direct message to a specific destination.
        
        Args:
            destination: Target subsystem name
            payload: Message content
            trace_id: Optional trace ID (generated if not provided)
            metadata: Optional additional metadata
            
        Returns:
            The message ID of the sent message
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
        """
        self._ensure_connected()
        
        # Create the message
        message = create_direct_message(
            source=self.subsystem_name,
            destination=destination,
            payload=payload,
            trace_id=trace_id,
            metadata=metadata
        )
        
        # Send the message
        await self._send_message(message)
        
        return message.message_id
    
    async def publish(
        self, 
        topic: str, 
        payload: Dict[str, Any], 
        trace_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            payload: Message content
            trace_id: Optional trace ID (generated if not provided)
            metadata: Optional additional metadata
            
        Returns:
            The message ID of the published message
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
        """
        self._ensure_connected()
        
        # Create the message
        message = create_topic_message(
            source=self.subsystem_name,
            topic=topic,
            payload=payload,
            trace_id=trace_id,
            metadata=metadata
        )
        
        # Send the message
        await self._send_message(message)
        
        return message.message_id
    
    async def request(
        self, 
        destination: str, 
        payload: Dict[str, Any], 
        timeout: Optional[float] = None,
        trace_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a request and wait for a response.
        
        Args:
            destination: Target subsystem name
            payload: Request content
            timeout: Optional timeout in seconds (defaults to config.request_timeout)
            trace_id: Optional trace ID (generated if not provided)
            metadata: Optional additional metadata
            
        Returns:
            The response payload
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
            asyncio.TimeoutError: If the request times out
            Exception: If the request fails
        """
        self._ensure_connected()
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.config.request_timeout
        
        # Prepare metadata
        request_metadata = metadata or {}
        request_id = str(uuid.uuid4())
        request_metadata['request_id'] = request_id
        
        # Create the message
        message = create_request_message(
            source=self.subsystem_name,
            destination=destination,
            payload=payload,
            timeout_seconds=timeout,
            trace_id=trace_id,
            metadata=request_metadata
        )
        
        # Create a future for the response
        future: RequestFuture[Dict[str, Any]] = RequestFuture(request_id, timeout)
        self.pending_requests[request_id] = future
        
        try:
            # Send the message
            await self._send_message(message)
            
            # Wait for the response
            return await future.wait()
        finally:
            # Clean up the pending request
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
    
    async def broadcast(
        self, 
        payload: Dict[str, Any], 
        trace_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Broadcast a message to all subsystems.
        
        Args:
            payload: Message content
            trace_id: Optional trace ID (generated if not provided)
            metadata: Optional additional metadata
            
        Returns:
            The message ID of the broadcast message
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
        """
        self._ensure_connected()
        
        # Create the message
        message = create_broadcast_message(
            source=self.subsystem_name,
            payload=payload,
            trace_id=trace_id,
            metadata=metadata
        )
        
        # Send the message
        await self._send_message(message)
        
        return message.message_id
    
    async def subscribe(
        self, 
        topic_pattern: str, 
        callback: CallbackFunc
    ) -> SubscriptionId:
        """
        Subscribe to messages matching a topic pattern.
        
        Args:
            topic_pattern: Topic pattern to subscribe to (can include wildcards)
            callback: Async function to call for matching messages
            
        Returns:
            The subscription ID
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
        """
        self._ensure_connected()
        
        # In a real implementation, this would register the subscription with the broker
        # For this prototype, we'll simulate a successful subscription
        
        # Generate a subscription ID
        subscription_id = f"sub-{uuid.uuid4().hex[:8]}"
        
        # Store the subscription
        subscription = TopicSubscription(
            subscription_id=subscription_id,
            topic_pattern=topic_pattern,
            callback=callback
        )
        
        self.subscriptions[subscription_id] = subscription
        
        logger.info(f"Subscribed to topic pattern: {topic_pattern} (subscription_id: {subscription_id})")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: SubscriptionId) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            subscription_id: The subscription ID to remove
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        if subscription_id not in self.subscriptions:
            logger.warning(f"Unknown subscription ID: {subscription_id}")
            return False
        
        # In a real implementation, this would unregister the subscription with the broker
        # For this prototype, we'll simulate a successful unsubscription
        
        # Remove the subscription
        del self.subscriptions[subscription_id]
        
        logger.info(f"Unsubscribed from topic (subscription_id: {subscription_id})")
        return True
    
    async def _send_message(self, message: MyceliumMessage) -> None:
        """
        Send a message through the Mycelium Network.
        
        Args:
            message: The message to send
            
        Raises:
            RuntimeError: If not connected to the Mycelium Network
        """
        self._ensure_connected()
        
        # Track the message
        self.sent_messages.add(message.message_id)
        self.messages_sent += 1
        
        # In a real implementation, this would send the message to the broker
        # For this prototype, we'll simulate successful sending
        logger.debug(f"Sent message: {message.message_id} ({message.destination or message.topic})")
    
    async def _handle_incoming_message(self, message: MyceliumMessage) -> None:
        """
        Handle an incoming message.
        
        Args:
            message: The received message
        """
        self.messages_received += 1
        
        # Check if it's a response to a request
        if 'in_response_to' in message.metadata:
            request_id = message.metadata['in_response_to']
            if request_id in self.pending_requests:
                future = self.pending_requests[request_id]
                future.set_result(message.payload)
                return
        
        # Handle topic message
        if message.topic:
            for subscription in self.subscriptions.values():
                if self._topic_matches_pattern(message.topic, subscription.topic_pattern):
                    await subscription.handle_message(message)
    
    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """
        Check if a topic matches a pattern.
        
        Args:
            topic: The topic to check
            pattern: The pattern to match against
            
        Returns:
            True if the topic matches the pattern
        """
        # Convert pattern to regex
        regex_pattern = pattern.replace('.', r'\.').replace('*', '[^.]+')
        regex_pattern = f"^{regex_pattern}$"
        
        import re
        return bool(re.match(regex_pattern, topic))
    
    def _ensure_connected(self) -> None:
        """
        Ensure the client is connected to the Mycelium Network.
        
        Raises:
            RuntimeError: If not connected
        """
        if self.status != ClientStatus.CONNECTED:
            raise RuntimeError(f"Not connected to Mycelium Network (status: {self.status.value})")
        
        self.last_activity = datetime.datetime.now()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Dictionary of client statistics
        """
        uptime = None
        if self.connected_at:
            uptime = (datetime.datetime.now() - self.connected_at).total_seconds()
        
        return {
            "subsystem_name": self.subsystem_name,
            "status": self.status.value,
            "connection_id": self.connection_id,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "uptime_seconds": uptime,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "failed_messages": self.failed_messages,
            "reconnections": self.reconnections,
            "active_subscriptions": len(self.subscriptions),
            "pending_requests": len(self.pending_requests)
        }


# Factory function
def create_client(
    subsystem_name: str, 
    config: Optional[Dict[str, Any]] = None
) -> MyceliumClient:
    """
    Create a new Mycelium client.
    
    Args:
        subsystem_name: Name of the subsystem using the client
        config: Optional client configuration
        
    Returns:
        Configured MyceliumClient instance
    """
    return MyceliumClient(subsystem_name=subsystem_name, config=config)