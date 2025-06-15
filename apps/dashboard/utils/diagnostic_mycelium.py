"""
EGOS Diagnostic MYCELIUM Integration

This module provides integration between the diagnostic tracking system and
the MYCELIUM communication backbone, enabling real-time updates, multi-user
collaboration, and cross-system notifications.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](app_dashboard_diagnostic_roadmap.py) <!-- EGOS-REF-195669B7 --> - Project roadmap and planning
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Diagnostic visualization module
  - [diagnostic_notifications.py](mdc:./diagnostic_notifications.py) - Notification system
  - [diagnostic_roadmap.py](mdc:./diagnostic_roadmap.py) - Roadmap integration
  - [mycelium_client.py](mdc:./mycelium_client.py) - Existing MYCELIUM client
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
import datetime
import uuid
from threading import Thread, Lock

# Import MYCELIUM client from existing dashboard
try:
    from integrations.mycelium_client import MyceliumClient
except ImportError:
    # Fallback implementation if the import fails
    class MyceliumClient:
        """Fallback implementation of MyceliumClient."""
        def __init__(self, *args, **kwargs):
            self.connected = False
            self.server_url = "nats://localhost:4222"
            self.logger = logging.getLogger("EGOS.Dashboard.DiagnosticMycelium.FallbackClient")
            self.logger.warning("Using fallback MyceliumClient implementation")
            self.fallback_mode = True  # Indicate this is the fallback client
        
        async def connect(self):
            self.logger.warning("Fallback connect() called")
            self.connected = True
        
        async def disconnect(self):
            self.logger.warning("Fallback disconnect() called")
            self.connected = False
        
        async def subscribe(self, subject, callback):
            self.logger.warning(f"Fallback subscribe() called for {subject}")
        
        async def publish(self, subject, data):
            self.logger.warning(f"Fallback publish() called for {subject} with data: {data}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticMycelium")

# MYCELIUM Topics/Subjects
DIAGNOSTIC_TOPIC_BASE = "diagnostic"
DIAGNOSTIC_UPDATE_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.update"
DIAGNOSTIC_ASSIGNMENT_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.assignment"
DIAGNOSTIC_TIMELINE_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.timeline"
DIAGNOSTIC_COMMENT_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.comment"
DIAGNOSTIC_NOTIFICATION_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.notification"
DIAGNOSTIC_ROADMAP_TOPIC = f"{DIAGNOSTIC_TOPIC_BASE}.roadmap"

# In-memory storage for active clients and data locks
active_clients = {}
data_lock = Lock()

class DiagnosticCollaborationManager:
    """Manages multi-user collaboration and real-time updates for diagnostic tracking."""
    
    def __init__(self, diagnostic_data_path: str = "diagnostic_tracking.json"):
        """Initialize the collaboration manager.
        
        Args:
            diagnostic_data_path: Path to the diagnostic tracking data JSON file
        """
        self.data_path = Path(diagnostic_data_path)
        self.mycelium_client = None
        self.client_id = str(uuid.uuid4())
        self.active_users = {}
        self.event_callbacks = {
            "update": [],
            "assignment": [],
            "timeline": [],
            "comment": [],
            "notification": [],
            "roadmap": []
        }
        self.logger = logger
        self.connected = False
        self.background_task = None
    
    async def initialize(self, server_url: str = "nats://localhost:4222") -> bool:
        """Initialize the collaboration manager and connect to MYCELIUM.
        
        Args:
            server_url: URL of the NATS/MYCELIUM server
            
        Returns:
            Success status of initialization
        """
        try:
            # Create MYCELIUM client
            self.mycelium_client = MyceliumClient(
                server_url=server_url,
                client_id=self.client_id,
                client_type="diagnostic"
            )
            
            # Connect to MYCELIUM
            await self.mycelium_client.connect()
            
            # Subscribe to relevant topics
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_UPDATE_TOPIC, 
                self._handle_update_message
            )
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_ASSIGNMENT_TOPIC,
                self._handle_assignment_message
            )
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_TIMELINE_TOPIC,
                self._handle_timeline_message
            )
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_COMMENT_TOPIC,
                self._handle_comment_message
            )
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_NOTIFICATION_TOPIC,
                self._handle_notification_message
            )
            await self.mycelium_client.subscribe(
                DIAGNOSTIC_ROADMAP_TOPIC,
                self._handle_roadmap_message
            )
            
            # Register with active clients
            global active_clients
            active_clients[self.client_id] = {
                "last_active": datetime.datetime.now().isoformat(),
                "user": "Unknown"  # Will be updated when user info is available
            }
            
            # Announce presence
            await self.publish_presence()
            
            self.connected = True
            self.logger.info(f"Diagnostic collaboration manager initialized with client ID {self.client_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing diagnostic collaboration manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the collaboration manager and disconnect from MYCELIUM."""
        try:
            # Announce departure
            if self.mycelium_client and self.connected:
                await self.mycelium_client.publish(
                    f"{DIAGNOSTIC_TOPIC_BASE}.presence",
                    {
                        "client_id": self.client_id,
                        "status": "offline",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                )
                
                # Disconnect from MYCELIUM
                await self.mycelium_client.disconnect()
                
                # Remove from active clients
                global active_clients
                if self.client_id in active_clients:
                    del active_clients[self.client_id]
                
                self.connected = False
                self.logger.info(f"Diagnostic collaboration manager shutdown")
        except Exception as e:
            self.logger.error(f"Error shutting down diagnostic collaboration manager: {e}")
    
    async def publish_presence(self, user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish presence information to MYCELIUM.
        
        Args:
            user_info: Optional user information
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare presence message
            message = {
                "client_id": self.client_id,
                "status": "online",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
                
                # Update active clients
                global active_clients
                if self.client_id in active_clients:
                    active_clients[self.client_id]["user"] = user_info
            
            # Publish presence
            await self.mycelium_client.publish(
                f"{DIAGNOSTIC_TOPIC_BASE}.presence",
                message
            )
            
            self.logger.info(f"Published presence information")
        except Exception as e:
            self.logger.error(f"Error publishing presence information: {e}")
    
    async def publish_issue_update(self, issue_id: str, updates: Dict[str, Any], 
                            user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish an issue update to MYCELIUM.
        
        Args:
            issue_id: ID of the issue being updated
            updates: Dictionary of fields to update
            user_info: Optional information about the user making the update
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare update message
            message = {
                "client_id": self.client_id,
                "issue_id": issue_id,
                "updates": updates,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
            
            # Publish update
            await self.mycelium_client.publish(
                DIAGNOSTIC_UPDATE_TOPIC,
                message
            )
            
            self.logger.info(f"Published update for issue {issue_id}")
        except Exception as e:
            self.logger.error(f"Error publishing issue update: {e}")
    
    async def publish_assignment(self, issue_id: str, assignee: str, 
                          user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish an assignment update to MYCELIUM.
        
        Args:
            issue_id: ID of the issue being assigned
            assignee: Username or email of the assignee
            user_info: Optional information about the user making the assignment
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare assignment message
            message = {
                "client_id": self.client_id,
                "issue_id": issue_id,
                "assignee": assignee,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
            
            # Publish assignment
            await self.mycelium_client.publish(
                DIAGNOSTIC_ASSIGNMENT_TOPIC,
                message
            )
            
            self.logger.info(f"Published assignment for issue {issue_id} to {assignee}")
        except Exception as e:
            self.logger.error(f"Error publishing assignment: {e}")
    
    async def publish_timeline_update(self, issue_id: str, due_date: str,
                               user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish a timeline update to MYCELIUM.
        
        Args:
            issue_id: ID of the issue whose timeline is being updated
            due_date: New due date (ISO format)
            user_info: Optional information about the user making the update
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare timeline message
            message = {
                "client_id": self.client_id,
                "issue_id": issue_id,
                "due_date": due_date,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
            
            # Publish timeline update
            await self.mycelium_client.publish(
                DIAGNOSTIC_TIMELINE_TOPIC,
                message
            )
            
            self.logger.info(f"Published timeline update for issue {issue_id}")
        except Exception as e:
            self.logger.error(f"Error publishing timeline update: {e}")
    
    async def publish_comment(self, issue_id: str, comment: str,
                       user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish a comment on an issue to MYCELIUM.
        
        Args:
            issue_id: ID of the issue being commented on
            comment: The comment text
            user_info: Optional information about the user making the comment
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare comment message
            message = {
                "client_id": self.client_id,
                "issue_id": issue_id,
                "comment": comment,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
            
            # Publish comment
            await self.mycelium_client.publish(
                DIAGNOSTIC_COMMENT_TOPIC,
                message
            )
            
            self.logger.info(f"Published comment for issue {issue_id}")
        except Exception as e:
            self.logger.error(f"Error publishing comment: {e}")
    
    async def publish_roadmap_link(self, issue_id: str, roadmap_task_id: str,
                            user_info: Optional[Dict[str, Any]] = None) -> None:
        """Publish a roadmap link to MYCELIUM.
        
        Args:
            issue_id: ID of the diagnostic issue
            roadmap_task_id: ID of the roadmap task to link
            user_info: Optional information about the user creating the link
        """
        if not self.mycelium_client or not self.connected:
            return
            
        try:
            # Prepare roadmap link message
            message = {
                "client_id": self.client_id,
                "issue_id": issue_id,
                "roadmap_task_id": roadmap_task_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add user info if provided
            if user_info:
                message["user"] = user_info
            
            # Publish roadmap link
            await self.mycelium_client.publish(
                DIAGNOSTIC_ROADMAP_TOPIC,
                message
            )
            
            self.logger.info(f"Published roadmap link for issue {issue_id} to task {roadmap_task_id}")
        except Exception as e:
            self.logger.error(f"Error publishing roadmap link: {e}")
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to register for (update, assignment, etc.)
            callback: Callback function to call when event occurs
        """
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
            self.logger.info(f"Registered callback for event type {event_type}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def start_background_tasks(self) -> None:
        """Start background tasks for the collaboration manager."""
        if self.background_task is not None:
            return
            
        # Create and start background task
        loop = asyncio.new_event_loop()
        
        def run_background(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        self.background_task = Thread(target=run_background, args=(loop,), daemon=True)
        self.background_task.start()
        
        # Schedule heartbeat task
        asyncio.run_coroutine_threadsafe(self._heartbeat_task(), loop)
        
        self.logger.info("Started background tasks")
    
    async def _heartbeat_task(self) -> None:
        """Background task to send periodic heartbeats."""
        while True:
            if self.connected:
                try:
                    # Send heartbeat
                    await self.mycelium_client.publish(
                        f"{DIAGNOSTIC_TOPIC_BASE}.heartbeat",
                        {
                            "client_id": self.client_id,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    )
                    
                    # Update active clients
                    global active_clients
                    if self.client_id in active_clients:
                        active_clients[self.client_id]["last_active"] = datetime.datetime.now().isoformat()
                except Exception as e:
                    self.logger.error(f"Error sending heartbeat: {e}")
            
            # Sleep for 30 seconds
            await asyncio.sleep(30)
    
    # Message handlers
    async def _handle_update_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle an update message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        # Ignore own messages
        if data.get("client_id") == self.client_id:
            return
            
        self.logger.info(f"Received update message for issue {data.get('issue_id')}")
        
        # Get global lock for data updates
        with data_lock:
            # Read current data
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                else:
                    tracking_data = {
                        "last_updated": datetime.datetime.now().isoformat(),
                        "issues": []
                    }
                
                # Find and update the issue
                issue_id = data.get("issue_id")
                updates = data.get("updates", {})
                
                for i, issue in enumerate(tracking_data.get("issues", [])):
                    if issue.get("id") == issue_id:
                        # Apply updates
                        for key, value in updates.items():
                            tracking_data["issues"][i][key] = value
                        
                        tracking_data["last_updated"] = datetime.datetime.now().isoformat()
                        break
                
                # Save updated data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(tracking_data, f, indent=2)
                
                # Call registered callbacks
                for callback in self.event_callbacks["update"]:
                    try:
                        callback(issue_id, updates, data.get("user"))
                    except Exception as e:
                        self.logger.error(f"Error in update callback: {e}")
            
            except Exception as e:
                self.logger.error(f"Error handling update message: {e}")
    
    async def _handle_assignment_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle an assignment message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        # Ignore own messages
        if data.get("client_id") == self.client_id:
            return
            
        self.logger.info(f"Received assignment message for issue {data.get('issue_id')}")
        
        # Get global lock for data updates
        with data_lock:
            # Read current data
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                else:
                    tracking_data = {
                        "last_updated": datetime.datetime.now().isoformat(),
                        "issues": []
                    }
                
                # Find and update the issue
                issue_id = data.get("issue_id")
                assignee = data.get("assignee")
                
                for i, issue in enumerate(tracking_data.get("issues", [])):
                    if issue.get("id") == issue_id:
                        # Update assignee
                        tracking_data["issues"][i]["assignee"] = assignee
                        
                        tracking_data["last_updated"] = datetime.datetime.now().isoformat()
                        break
                
                # Save updated data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(tracking_data, f, indent=2)
                
                # Call registered callbacks
                for callback in self.event_callbacks["assignment"]:
                    try:
                        callback(issue_id, assignee, data.get("user"))
                    except Exception as e:
                        self.logger.error(f"Error in assignment callback: {e}")
            
            except Exception as e:
                self.logger.error(f"Error handling assignment message: {e}")
    
    async def _handle_timeline_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle a timeline message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        # Ignore own messages
        if data.get("client_id") == self.client_id:
            return
            
        self.logger.info(f"Received timeline message for issue {data.get('issue_id')}")
        
        # Get global lock for data updates
        with data_lock:
            # Read current data
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                else:
                    tracking_data = {
                        "last_updated": datetime.datetime.now().isoformat(),
                        "issues": []
                    }
                
                # Find and update the issue
                issue_id = data.get("issue_id")
                due_date = data.get("due_date")
                
                for i, issue in enumerate(tracking_data.get("issues", [])):
                    if issue.get("id") == issue_id:
                        # Update due date
                        tracking_data["issues"][i]["due_date"] = due_date
                        
                        tracking_data["last_updated"] = datetime.datetime.now().isoformat()
                        break
                
                # Save updated data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(tracking_data, f, indent=2)
                
                # Call registered callbacks
                for callback in self.event_callbacks["timeline"]:
                    try:
                        callback(issue_id, due_date, data.get("user"))
                    except Exception as e:
                        self.logger.error(f"Error in timeline callback: {e}")
            
            except Exception as e:
                self.logger.error(f"Error handling timeline message: {e}")
    
    async def _handle_comment_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle a comment message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        # Ignore own messages
        if data.get("client_id") == self.client_id:
            return
            
        self.logger.info(f"Received comment message for issue {data.get('issue_id')}")
        
        # Get global lock for data updates
        with data_lock:
            # Read current data
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                else:
                    tracking_data = {
                        "last_updated": datetime.datetime.now().isoformat(),
                        "issues": []
                    }
                
                # Find and update the issue
                issue_id = data.get("issue_id")
                comment = data.get("comment")
                
                for i, issue in enumerate(tracking_data.get("issues", [])):
                    if issue.get("id") == issue_id:
                        # Add comment to issue
                        if "comments" not in tracking_data["issues"][i]:
                            tracking_data["issues"][i]["comments"] = []
                        
                        # Add comment with timestamp and user info
                        tracking_data["issues"][i]["comments"].append({
                            "text": comment,
                            "timestamp": data.get("timestamp", datetime.datetime.now().isoformat()),
                            "user": data.get("user", "Unknown")
                        })
                        
                        tracking_data["last_updated"] = datetime.datetime.now().isoformat()
                        break
                
                # Save updated data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(tracking_data, f, indent=2)
                
                # Call registered callbacks
                for callback in self.event_callbacks["comment"]:
                    try:
                        callback(issue_id, comment, data.get("user"))
                    except Exception as e:
                        self.logger.error(f"Error in comment callback: {e}")
            
            except Exception as e:
                self.logger.error(f"Error handling comment message: {e}")
    
    async def _handle_notification_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle a notification message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        self.logger.info(f"Received notification message")
        
        # Call registered callbacks
        for callback in self.event_callbacks["notification"]:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in notification callback: {e}")
    
    async def _handle_roadmap_message(self, subject: str, data: Dict[str, Any]) -> None:
        """Handle a roadmap message from MYCELIUM.
        
        Args:
            subject: MYCELIUM subject
            data: Message data
        """
        # Ignore own messages
        if data.get("client_id") == self.client_id:
            return
            
        self.logger.info(f"Received roadmap message for issue {data.get('issue_id')}")
        
        # Get global lock for data updates
        with data_lock:
            # Read current data
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                else:
                    tracking_data = {
                        "last_updated": datetime.datetime.now().isoformat(),
                        "issues": []
                    }
                
                # Find and update the issue
                issue_id = data.get("issue_id")
                roadmap_task_id = data.get("roadmap_task_id")
                
                for i, issue in enumerate(tracking_data.get("issues", [])):
                    if issue.get("id") == issue_id:
                        # Update roadmap link
                        tracking_data["issues"][i]["roadmap_task_id"] = roadmap_task_id
                        
                        tracking_data["last_updated"] = datetime.datetime.now().isoformat()
                        break
                
                # Save updated data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(tracking_data, f, indent=2)
                
                # Call registered callbacks
                for callback in self.event_callbacks["roadmap"]:
                    try:
                        callback(issue_id, roadmap_task_id, data.get("user"))
                    except Exception as e:
                        self.logger.error(f"Error in roadmap callback: {e}")
            
            except Exception as e:
                self.logger.error(f"Error handling roadmap message: {e}")

# Helper function to create and initialize collaboration manager
async def create_collaboration_manager(data_path: str = "diagnostic_tracking.json",
                                     server_url: str = "nats://localhost:4222") -> DiagnosticCollaborationManager:
    """Create and initialize a DiagnosticCollaborationManager.
    
    Args:
        data_path: Path to the diagnostic tracking data file
        server_url: URL of the NATS/MYCELIUM server
        
    Returns:
        Initialized DiagnosticCollaborationManager instance
    """
    manager = DiagnosticCollaborationManager(data_path)
    await manager.initialize(server_url)
    manager.start_background_tasks()
    return manager