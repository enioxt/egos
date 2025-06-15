"""
EGOS Diagnostic Notification System

This module provides email and in-app notifications for the EGOS diagnostic tracking system,
enabling automated alerts for issue assignments, due dates, and status updates.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Diagnostic visualization
  - [diagnostic_mycelium.py](mdc:./diagnostic_mycelium.py) - MYCELIUM integration
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import smtplib
import ssl
import logging
import json
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
import datetime
import os
from threading import Thread, Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticNotifications")

# Default email templates
DEFAULT_ASSIGNMENT_TEMPLATE = """
<html>
<body>
<h2>EGOS Diagnostic Issue Assignment</h2>
<p>Hello {assignee_name},</p>
<p>You have been assigned to work on the following diagnostic issue:</p>
<div style="border-left: 4px solid #ccc; padding-left: 10px; margin: 10px 0;">
    <p><strong>Issue ID:</strong> {issue_id}</p>
    <p><strong>Title:</strong> {issue_title}</p>
    <p><strong>Priority:</strong> {issue_priority}</p>
    <p><strong>Due Date:</strong> {due_date}</p>
    <p><strong>Description:</strong> {issue_description}</p>
</div>
<p>Please access the <a href="{dashboard_url}">EGOS Diagnostic Dashboard</a> to view more details and update your progress.</p>
<p>Thank you,<br/>EGOS Diagnostic System</p>
</body>
</html>
"""

DEFAULT_DUE_DATE_TEMPLATE = """
<html>
<body>
<h2>EGOS Diagnostic Issue Due Date Reminder</h2>
<p>Hello {assignee_name},</p>
<p>This is a reminder that the following diagnostic issue is due soon:</p>
<div style="border-left: 4px solid #ccc; padding-left: 10px; margin: 10px 0;">
    <p><strong>Issue ID:</strong> {issue_id}</p>
    <p><strong>Title:</strong> {issue_title}</p>
    <p><strong>Priority:</strong> {issue_priority}</p>
    <p><strong>Due Date:</strong> {due_date}</p>
    <p><strong>Time Remaining:</strong> {time_remaining}</p>
</div>
<p>Please access the <a href="{dashboard_url}">EGOS Diagnostic Dashboard</a> to update your progress.</p>
<p>Thank you,<br/>EGOS Diagnostic System</p>
</body>
</html>
"""

DEFAULT_STATUS_UPDATE_TEMPLATE = """
<html>
<body>
<h2>EGOS Diagnostic Issue Status Update</h2>
<p>Hello {recipient_name},</p>
<p>The status of the following diagnostic issue has been updated:</p>
<div style="border-left: 4px solid #ccc; padding-left: 10px; margin: 10px 0;">
    <p><strong>Issue ID:</strong> {issue_id}</p>
    <p><strong>Title:</strong> {issue_title}</p>
    <p><strong>Previous Status:</strong> {previous_status}</p>
    <p><strong>New Status:</strong> {new_status}</p>
    <p><strong>Updated By:</strong> {updated_by}</p>
    <p><strong>Update Time:</strong> {update_time}</p>
</div>
<p>Please access the <a href="{dashboard_url}">EGOS Diagnostic Dashboard</a> to view more details.</p>
<p>Thank you,<br/>EGOS Diagnostic System</p>
</body>
</html>
"""

class NotificationManager:
    """Manages email and in-app notifications for the diagnostic tracking system."""
    
    def __init__(self, config_path: str = "notification_config.json"):
        """Initialize the notification manager.
        
        Args:
            config_path: Path to the notification configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logger
        self.config = self._load_config()
        self.notification_lock = Lock()
        self.background_task = None
        self.notification_queue = []
        self.running = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration.
        
        Returns:
            Configuration dictionary
        """
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "from_email": "egos.diagnostic@example.com",
            "dashboard_url": "http://localhost:8501",
            "notification_interval": 60,  # seconds
            "due_date_reminder_days": [7, 3, 1],  # days before due date
            "templates": {
                "assignment": DEFAULT_ASSIGNMENT_TEMPLATE,
                "due_date": DEFAULT_DUE_DATE_TEMPLATE,
                "status_update": DEFAULT_STATUS_UPDATE_TEMPLATE
            },
            "enabled": False  # Default to disabled until properly configured
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Merge with default config for any missing values
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                        
                return config
            else:
                # Save default config
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                    
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading notification configuration: {e}")
            return default_config
    
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                
            self.logger.info("Notification configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving notification configuration: {e}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update the notification configuration.
        
        Args:
            updates: Dictionary of configuration updates
        """
        with self.notification_lock:
            for key, value in updates.items():
                if key == "templates" and isinstance(value, dict):
                    # Update templates individually
                    if "templates" not in self.config:
                        self.config["templates"] = {}
                        
                    for template_key, template_value in value.items():
                        self.config["templates"][template_key] = template_value
                else:
                    self.config[key] = value
            
            self.save_config()
    
    def send_email(self, recipient: str, subject: str, body: str, 
                  html: bool = True) -> bool:
        """Send an email notification.
        
        Args:
            recipient: Email address of the recipient
            subject: Email subject
            body: Email body content
            html: Whether the body is HTML
            
        Returns:
            Success status
        """
        if not self.config.get("enabled", False):
            self.logger.warning("Email notifications are disabled. Update config to enable.")
            return False
            
        # Check for required configuration
        if not self.config.get("smtp_username") or not self.config.get("smtp_password"):
            self.logger.error("SMTP credentials not configured. Cannot send email.")
            return False
            
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.config.get("from_email", "egos.diagnostic@example.com")
            message["To"] = recipient
            
            # Attach body
            content_type = "html" if html else "plain"
            message.attach(MIMEText(body, content_type))
            
            # Create secure connection and send message
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config.get("smtp_server", "smtp.gmail.com"), 
                             self.config.get("smtp_port", 587)) as server:
                server.starttls(context=context)
                server.login(self.config.get("smtp_username"), self.config.get("smtp_password"))
                server.sendmail(message["From"], recipient, message.as_string())
                
            self.logger.info(f"Email notification sent to {recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
            return False
    
    def send_assignment_notification(self, issue: Dict[str, Any], 
                                   assignee_email: str) -> bool:
        """Send an assignment notification.
        
        Args:
            issue: Issue data dictionary
            assignee_email: Email of the assignee
            
        Returns:
            Success status
        """
        try:
            # Get template
            template = self.config.get("templates", {}).get(
                "assignment", DEFAULT_ASSIGNMENT_TEMPLATE
            )
            
            # Format template
            body = template.format(
                assignee_name=issue.get("assignee_name", "Team Member"),
                issue_id=issue.get("id", "Unknown"),
                issue_title=issue.get("title", "Unknown Issue"),
                issue_priority=issue.get("priority", "Medium"),
                issue_description=issue.get("description", "No description available"),
                due_date=issue.get("due_date", "Not specified"),
                dashboard_url=self.config.get("dashboard_url", "http://localhost:8501")
            )
            
            # Send email
            return self.send_email(
                recipient=assignee_email,
                subject=f"EGOS Diagnostic Issue Assignment: {issue.get('title', 'Issue')}",
                body=body,
                html=True
            )
        except Exception as e:
            self.logger.error(f"Error sending assignment notification: {e}")
            return False
    
    def send_due_date_notification(self, issue: Dict[str, Any], 
                                assignee_email: str,
                                days_remaining: int) -> bool:
        """Send a due date reminder notification.
        
        Args:
            issue: Issue data dictionary
            assignee_email: Email of the assignee
            days_remaining: Number of days remaining until due date
            
        Returns:
            Success status
        """
        try:
            # Get template
            template = self.config.get("templates", {}).get(
                "due_date", DEFAULT_DUE_DATE_TEMPLATE
            )
            
            # Format time remaining
            if days_remaining <= 0:
                time_remaining = "Due today!"
            elif days_remaining == 1:
                time_remaining = "Due tomorrow"
            else:
                time_remaining = f"{days_remaining} days remaining"
            
            # Format template
            body = template.format(
                assignee_name=issue.get("assignee_name", "Team Member"),
                issue_id=issue.get("id", "Unknown"),
                issue_title=issue.get("title", "Unknown Issue"),
                issue_priority=issue.get("priority", "Medium"),
                due_date=issue.get("due_date", "Not specified"),
                time_remaining=time_remaining,
                dashboard_url=self.config.get("dashboard_url", "http://localhost:8501")
            )
            
            # Send email
            return self.send_email(
                recipient=assignee_email,
                subject=f"EGOS Diagnostic Issue Due Date Reminder: {issue.get('title', 'Issue')}",
                body=body,
                html=True
            )
        except Exception as e:
            self.logger.error(f"Error sending due date notification: {e}")
            return False
    
    def send_status_update_notification(self, issue: Dict[str, Any], 
                                     recipient_email: str,
                                     previous_status: str,
                                     new_status: str,
                                     updated_by: str) -> bool:
        """Send a status update notification.
        
        Args:
            issue: Issue data dictionary
            recipient_email: Email of the recipient
            previous_status: Previous status of the issue
            new_status: New status of the issue
            updated_by: User who updated the status
            
        Returns:
            Success status
        """
        try:
            # Get template
            template = self.config.get("templates", {}).get(
                "status_update", DEFAULT_STATUS_UPDATE_TEMPLATE
            )
            
            # Format template
            body = template.format(
                recipient_name=issue.get("assignee_name", "Team Member"),
                issue_id=issue.get("id", "Unknown"),
                issue_title=issue.get("title", "Unknown Issue"),
                previous_status=previous_status,
                new_status=new_status,
                updated_by=updated_by,
                update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                dashboard_url=self.config.get("dashboard_url", "http://localhost:8501")
            )
            
            # Send email
            return self.send_email(
                recipient=recipient_email,
                subject=f"EGOS Diagnostic Issue Status Update: {issue.get('title', 'Issue')}",
                body=body,
                html=True
            )
        except Exception as e:
            self.logger.error(f"Error sending status update notification: {e}")
            return False
    
    def queue_notification(self, notification_type: str, data: Dict[str, Any]) -> None:
        """Queue a notification for processing.
        
        Args:
            notification_type: Type of notification (assignment, due_date, status_update)
            data: Notification data
        """
        with self.notification_lock:
            self.notification_queue.append({
                "type": notification_type,
                "data": data,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            self.logger.info(f"Queued {notification_type} notification")
    
    def start_notification_service(self) -> None:
        """Start the notification processing service in the background."""
        if self.background_task is not None:
            return
            
        self.running = True
        
        # Create and start background task
        loop = asyncio.new_event_loop()
        
        def run_notification_service(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        self.background_task = Thread(target=run_notification_service, args=(loop,), daemon=True)
        self.background_task.start()
        
        # Schedule notification processing task
        asyncio.run_coroutine_threadsafe(self._process_notifications(), loop)
        
        # Schedule due date reminder task
        asyncio.run_coroutine_threadsafe(self._check_due_dates(), loop)
        
        self.logger.info("Started notification service")
    
    def stop_notification_service(self) -> None:
        """Stop the notification processing service."""
        self.running = False
        self.logger.info("Notification service stopped")
    
    async def _process_notifications(self) -> None:
        """Process queued notifications."""
        while self.running:
            # Process queued notifications
            with self.notification_lock:
                queue_copy = self.notification_queue.copy()
                self.notification_queue = []
            
            for notification in queue_copy:
                try:
                    notification_type = notification.get("type")
                    data = notification.get("data", {})
                    
                    if notification_type == "assignment":
                        self.send_assignment_notification(
                            data.get("issue", {}),
                            data.get("assignee_email", "")
                        )
                    elif notification_type == "due_date":
                        self.send_due_date_notification(
                            data.get("issue", {}),
                            data.get("assignee_email", ""),
                            data.get("days_remaining", 0)
                        )
                    elif notification_type == "status_update":
                        self.send_status_update_notification(
                            data.get("issue", {}),
                            data.get("recipient_email", ""),
                            data.get("previous_status", ""),
                            data.get("new_status", ""),
                            data.get("updated_by", "")
                        )
                    else:
                        self.logger.warning(f"Unknown notification type: {notification_type}")
                except Exception as e:
                    self.logger.error(f"Error processing notification: {e}")
            
            # Sleep before next processing cycle
            await asyncio.sleep(self.config.get("notification_interval", 60))
    
    async def _check_due_dates(self) -> None:
        """Check for upcoming due dates and send reminders."""
        while self.running:
            try:
                # Get due date reminder days from config
                reminder_days = self.config.get("due_date_reminder_days", [7, 3, 1])
                
                # Load tracking data
                data_path = Path("diagnostic_tracking.json")
                if data_path.exists():
                    with open(data_path, 'r', encoding='utf-8') as f:
                        tracking_data = json.load(f)
                        
                    # Check each issue for upcoming due dates
                    today = datetime.datetime.now().date()
                    
                    for issue in tracking_data.get("issues", []):
                        if "due_date" in issue and issue.get("assignee_email"):
                            try:
                                # Parse due date
                                due_date = datetime.datetime.fromisoformat(issue["due_date"]).date()
                                
                                # Calculate days remaining
                                days_remaining = (due_date - today).days
                                
                                # Check if reminder should be sent
                                if days_remaining in reminder_days:
                                    # Queue reminder notification
                                    self.queue_notification("due_date", {
                                        "issue": issue,
                                        "assignee_email": issue["assignee_email"],
                                        "days_remaining": days_remaining
                                    })
                            except (ValueError, TypeError) as e:
                                self.logger.error(f"Error processing due date for issue {issue.get('id')}: {e}")
            except Exception as e:
                self.logger.error(f"Error checking due dates: {e}")
            
            # Check once per day
            await asyncio.sleep(86400)  # 24 hours

# Create a notification manager instance for import
notification_manager = NotificationManager()

# Helper function for external components to send notifications
def send_notification(notification_type: str, **kwargs) -> None:
    """Send a notification via the notification manager.
    
    Args:
        notification_type: Type of notification (assignment, due_date, status_update)
        **kwargs: Notification data
    """
    global notification_manager
    notification_manager.queue_notification(notification_type, kwargs)

# Start notification service on import
if __name__ != "__main__":
    notification_manager.start_notification_service()