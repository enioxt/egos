"""
EGOS Diagnostic Tracking System

This module provides persistence and synchronization for the diagnostic tracking system,
managing issue data storage, status updates, and collaborative features.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Diagnostic visualization
  - [diagnostic_mycelium.py](mdc:./diagnostic_mycelium.py) - MYCELIUM integration
  - [diagnostic_roadmap.py](mdc:./diagnostic_roadmap.py) - Roadmap integration
  - [diagnostic_notifications.py](mdc:./diagnostic_notifications.py) - Notification system
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
import uuid
import os
from typing import Dict, List, Any, Optional, Union, Set
from pathlib import Path
import datetime
from threading import Lock
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticTracking")

# Issue status options
ISSUE_STATUSES = [
    "identified",       # Initial status when issue is identified
    "acknowledged",     # Issue has been acknowledged but not yet assigned
    "assigned",         # Issue has been assigned but work not started
    "in_progress",      # Work is in progress
    "reviewing",        # Solution is being reviewed
    "resolved",         # Issue has been resolved
    "verified",         # Resolution has been verified
    "closed",           # Issue is closed and complete
    "deferred",         # Issue is deferred to later
    "wont_fix"          # Issue will not be fixed
]

# Issue priority options
ISSUE_PRIORITIES = [
    "critical",         # Must be fixed immediately
    "high",             # Important to fix soon
    "medium",           # Should be fixed in normal course of work
    "low",              # Fix when convenient
    "enhancement"       # Not a bug, but would improve system
]

# Lock for file operations
tracking_lock = Lock()

class DiagnosticTrackingManager:
    """Manages persistence and synchronization for diagnostic tracking data."""
    
    def __init__(self, data_path: str = "diagnostic_tracking.json", 
               backup_dir: str = "tracking_backups"):
        """Initialize the tracking manager.
        
        Args:
            data_path: Path to the diagnostic tracking data file
            backup_dir: Directory for tracking data backups
        """
        self.data_path = Path(data_path)
        self.backup_dir = Path(backup_dir)
        self.logger = logger
        
        # Create backup directory if it doesn't exist
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial data or create empty structure
        self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """Load tracking data from file.
        
        Returns:
            Tracking data dictionary
        """
        with tracking_lock:
            try:
                if self.data_path.exists():
                    with open(self.data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.logger.info(f"Loaded tracking data with {len(data.get('issues', []))} issues")
                    return data
                else:
                    # Create initial data structure
                    empty_data = {
                        "metadata": {
                            "created": datetime.datetime.now().isoformat(),
                            "last_updated": datetime.datetime.now().isoformat(),
                            "version": "1.0.0"
                        },
                        "issues": []
                    }
                    
                    # Save empty data
                    with open(self.data_path, 'w', encoding='utf-8') as f:
                        json.dump(empty_data, f, indent=2)
                    
                    self.logger.info("Created new tracking data file")
                    return empty_data
            except Exception as e:
                self.logger.error(f"Error loading tracking data: {e}")
                return {
                    "metadata": {
                        "created": datetime.datetime.now().isoformat(),
                        "last_updated": datetime.datetime.now().isoformat(),
                        "version": "1.0.0",
                        "error": str(e)
                    },
                    "issues": []
                }
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save tracking data to file.
        
        Args:
            data: Tracking data dictionary
            
        Returns:
            Success status
        """
        with tracking_lock:
            try:
                # Update metadata
                if "metadata" not in data:
                    data["metadata"] = {}
                
                data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
                
                # Create backup
                self._create_backup()
                
                # Save data
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                self.logger.info(f"Saved tracking data with {len(data.get('issues', []))} issues")
                return True
            except Exception as e:
                self.logger.error(f"Error saving tracking data: {e}")
                return False
    
    def _create_backup(self) -> None:
        """Create a backup of the current tracking data."""
        try:
            if not self.data_path.exists():
                return
            
            # Generate backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"tracking_backup_{timestamp}.json"
            
            # Copy file
            shutil.copy2(self.data_path, backup_path)
            
            # Clean up old backups (keep most recent 10)
            self._cleanup_backups()
            
            self.logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
    
    def _cleanup_backups(self) -> None:
        """Clean up old backups, keeping the most recent ones."""
        try:
            # List all backup files
            backup_files = list(self.backup_dir.glob("tracking_backup_*.json"))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Delete old backups (keep most recent 10)
            max_backups = 10
            if len(backup_files) > max_backups:
                for old_file in backup_files[max_backups:]:
                    old_file.unlink()
                    self.logger.info(f"Deleted old backup {old_file}")
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
    
    def get_all_issues(self) -> List[Dict[str, Any]]:
        """Get all issues in the tracking system.
        
        Returns:
            List of issue dictionaries
        """
        data = self.load_data()
        return data.get("issues", [])
    
    def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific issue by ID.
        
        Args:
            issue_id: ID of the issue to retrieve
            
        Returns:
            Issue dictionary or None if not found
        """
        data = self.load_data()
        
        for issue in data.get("issues", []):
            if issue.get("id") == issue_id:
                return issue
        
        return None
    
    def add_issue(self, issue_data: Dict[str, Any]) -> str:
        """Add a new issue to the tracking system.
        
        Args:
            issue_data: Issue data dictionary
            
        Returns:
            ID of the created issue
        """
        with tracking_lock:
            # Load current data
            data = self.load_data()
            
            # Generate unique ID if not provided
            if "id" not in issue_data:
                issue_data["id"] = str(len(data.get("issues", [])) + 1).zfill(3)
            
            # Add timestamps
            if "created" not in issue_data:
                issue_data["created"] = datetime.datetime.now().isoformat()
            if "updated" not in issue_data:
                issue_data["updated"] = datetime.datetime.now().isoformat()
            
            # Set default status if not provided
            if "status" not in issue_data:
                issue_data["status"] = "identified"
            
            # Add to issues list
            data["issues"].append(issue_data)
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Added issue {issue_data['id']}: {issue_data.get('title', 'Untitled')}")
            return issue_data["id"]
    
    def update_issue(self, issue_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing issue.
        
        Args:
            issue_id: ID of the issue to update
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        with tracking_lock:
            # Load current data
            data = self.load_data()
            
            # Find issue
            found = False
            for i, issue in enumerate(data.get("issues", [])):
                if issue.get("id") == issue_id:
                    # Update fields
                    for key, value in updates.items():
                        data["issues"][i][key] = value
                    
                    # Update timestamp
                    data["issues"][i]["updated"] = datetime.datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Updated issue {issue_id}")
            return True
    
    def delete_issue(self, issue_id: str) -> bool:
        """Delete an issue from the tracking system.
        
        Args:
            issue_id: ID of the issue to delete
            
        Returns:
            Success status
        """
        with tracking_lock:
            # Load current data
            data = self.load_data()
            
            # Find issue
            found = False
            for i, issue in enumerate(data.get("issues", [])):
                if issue.get("id") == issue_id:
                    # Remove issue
                    del data["issues"][i]
                    found = True
                    break
            
            if not found:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Deleted issue {issue_id}")
            return True
    
    def add_comment(self, issue_id: str, comment: str, 
                 user_info: Optional[Dict[str, Any]] = None) -> bool:
        """Add a comment to an issue.
        
        Args:
            issue_id: ID of the issue to comment on
            comment: Comment text
            user_info: Optional information about the commenter
            
        Returns:
            Success status
        """
        with tracking_lock:
            # Load current data
            data = self.load_data()
            
            # Find issue
            found = False
            for i, issue in enumerate(data.get("issues", [])):
                if issue.get("id") == issue_id:
                    # Create comments list if it doesn't exist
                    if "comments" not in issue:
                        data["issues"][i]["comments"] = []
                    
                    # Add comment
                    comment_data = {
                        "id": str(uuid.uuid4()),
                        "text": comment,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    
                    # Add user info if provided
                    if user_info:
                        comment_data["user"] = user_info
                    
                    data["issues"][i]["comments"].append(comment_data)
                    
                    # Update timestamp
                    data["issues"][i]["updated"] = datetime.datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Added comment to issue {issue_id}")
            return True
    
    def update_status(self, issue_id: str, status: str, 
                    user_info: Optional[Dict[str, Any]] = None) -> bool:
        """Update the status of an issue.
        
        Args:
            issue_id: ID of the issue to update
            status: New status
            user_info: Optional information about the user making the update
            
        Returns:
            Success status
        """
        # Validate status
        if status not in ISSUE_STATUSES:
            self.logger.error(f"Invalid status: {status}")
            return False
        
        with tracking_lock:
            # Load current data
            data = self.load_data()
            
            # Find issue
            found = False
            for i, issue in enumerate(data.get("issues", [])):
                if issue.get("id") == issue_id:
                    # Store previous status
                    previous_status = issue.get("status", "identified")
                    
                    # Update status
                    data["issues"][i]["status"] = status
                    
                    # Add status history if it doesn't exist
                    if "status_history" not in issue:
                        data["issues"][i]["status_history"] = []
                    
                    # Add status change to history
                    status_change = {
                        "from": previous_status,
                        "to": status,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    
                    # Add user info if provided
                    if user_info:
                        status_change["user"] = user_info
                    
                    data["issues"][i]["status_history"].append(status_change)
                    
                    # Update timestamp
                    data["issues"][i]["updated"] = datetime.datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Updated status of issue {issue_id} to {status}")
            return True
    
    def get_issues_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all issues with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of matching issues
        """
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get("status") == status]
    
    def get_issues_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """Get all issues assigned to a specific person.
        
        Args:
            assignee: Assignee to filter by
            
        Returns:
            List of matching issues
        """
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get("assignee") == assignee]
    
    def get_issues_by_subsystem(self, subsystem: str) -> List[Dict[str, Any]]:
        """Get all issues for a specific subsystem.
        
        Args:
            subsystem: Subsystem to filter by
            
        Returns:
            List of matching issues
        """
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get("subsystem") == subsystem]
    
    def get_issues_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get all issues with a specific priority.
        
        Args:
            priority: Priority to filter by
            
        Returns:
            List of matching issues
        """
        issues = self.get_all_issues()
        return [issue for issue in issues if issue.get("priority") == priority]
    
    def get_status_summary(self) -> Dict[str, int]:
        """Get a summary of issues by status.
        
        Returns:
            Dictionary mapping status to count
        """
        issues = self.get_all_issues()
        status_counts = {}
        
        for issue in issues:
            status = issue.get("status", "identified")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def get_priority_summary(self) -> Dict[str, int]:
        """Get a summary of issues by priority.
        
        Returns:
            Dictionary mapping priority to count
        """
        issues = self.get_all_issues()
        priority_counts = {}
        
        for issue in issues:
            priority = issue.get("priority", "medium")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return priority_counts
    
    def get_subsystem_summary(self) -> Dict[str, int]:
        """Get a summary of issues by subsystem.
        
        Returns:
            Dictionary mapping subsystem to count
        """
        issues = self.get_all_issues()
        subsystem_counts = {}
        
        for issue in issues:
            subsystem = issue.get("subsystem", "unknown")
            subsystem_counts[subsystem] = subsystem_counts.get(subsystem, 0) + 1
        
        return subsystem_counts
    
    def get_recently_updated_issues(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get issues updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recently updated issues
        """
        issues = self.get_all_issues()
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_date_str = cutoff_date.isoformat()
        
        return [
            issue for issue in issues
            if issue.get("updated", "").split("T")[0] >= cutoff_date_str.split("T")[0]
        ]
    
    def get_overdue_issues(self) -> List[Dict[str, Any]]:
        """Get issues that are past their due date.
        
        Returns:
            List of overdue issues
        """
        issues = self.get_all_issues()
        today = datetime.datetime.now().date()
        
        overdue_issues = []
        for issue in issues:
            # Skip issues that are already resolved/closed/won't fix
            if issue.get("status") in ["resolved", "closed", "wont_fix", "verified"]:
                continue
                
            # Check due date
            if "due_date" in issue:
                try:
                    due_date = datetime.datetime.fromisoformat(issue["due_date"]).date()
                    if due_date < today:
                        overdue_issues.append(issue)
                except (ValueError, TypeError):
                    pass
        
        return overdue_issues
    
    def merge_issues_from_report(self, report_issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Merge issues from a diagnostic report into the tracking system.
        
        Args:
            report_issues: List of issues from the diagnostic report
            
        Returns:
            Dictionary with counts of added, updated, and skipped issues
        """
        with tracking_lock:
            # Load current data
            data = self.load_data()
            current_issues = data.get("issues", [])
            
            # Track counts
            counts = {
                "added": 0,
                "updated": 0,
                "skipped": 0
            }
            
            # Create index of existing issues by description/title for matching
            existing_issues_index = {}
            for issue in current_issues:
                # Use description as key if available, otherwise title
                key = issue.get("description", "").strip()
                if not key:
                    key = issue.get("title", "").strip()
                
                if key:
                    existing_issues_index[key] = issue
            
            # Process each report issue
            for report_issue in report_issues:
                # Find matching key (description or title)
                key = report_issue.get("description", "").strip()
                if not key:
                    key = report_issue.get("title", "").strip()
                
                if not key:
                    counts["skipped"] += 1
                    continue
                
                # Check if issue already exists
                if key in existing_issues_index:
                    # Get existing issue
                    existing_issue = existing_issues_index[key]
                    
                    # Check if anything needs to be updated
                    update_needed = False
                    for field in ["title", "description", "priority", "subsystem"]:
                        if field in report_issue and report_issue[field] != existing_issue.get(field):
                            update_needed = True
                            break
                    
                    if update_needed:
                        # Update existing issue
                        for i, issue in enumerate(data["issues"]):
                            if issue.get("id") == existing_issue.get("id"):
                                # Update fields from report
                                for field in ["title", "description", "priority", "subsystem"]:
                                    if field in report_issue:
                                        data["issues"][i][field] = report_issue[field]
                                
                                # Update timestamp
                                data["issues"][i]["updated"] = datetime.datetime.now().isoformat()
                                counts["updated"] += 1
                                break
                    else:
                        counts["skipped"] += 1
                else:
                    # Create new issue from report issue
                    new_issue = report_issue.copy()
                    
                    # Generate ID
                    new_issue["id"] = str(len(data["issues"]) + 1).zfill(3)
                    
                    # Set timestamps
                    new_issue["created"] = datetime.datetime.now().isoformat()
                    new_issue["updated"] = datetime.datetime.now().isoformat()
                    
                    # Set default status
                    new_issue["status"] = "identified"
                    
                    # Add to issues list
                    data["issues"].append(new_issue)
                    counts["added"] += 1
                    
                    # Add to index
                    existing_issues_index[key] = new_issue
            
            # Save data
            self.save_data(data)
            
            self.logger.info(f"Merged issues from report: {counts['added']} added, {counts['updated']} updated, {counts['skipped']} skipped")
            return counts

# Create a tracking manager instance for import
tracking_manager = DiagnosticTrackingManager()

# Helper functions for external components
def get_all_issues() -> List[Dict[str, Any]]:
    """Get all issues in the tracking system.
    
    Returns:
        List of issue dictionaries
    """
    global tracking_manager
    return tracking_manager.get_all_issues()

def get_issue(issue_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific issue by ID.
    
    Args:
        issue_id: ID of the issue to retrieve
        
    Returns:
        Issue dictionary or None if not found
    """
    global tracking_manager
    return tracking_manager.get_issue(issue_id)

def update_issue(issue_id: str, updates: Dict[str, Any]) -> bool:
    """Update an existing issue.
    
    Args:
        issue_id: ID of the issue to update
        updates: Dictionary of fields to update
        
    Returns:
        Success status
    """
    global tracking_manager
    return tracking_manager.update_issue(issue_id, updates)

def get_status_summary() -> Dict[str, int]:
    """Get a summary of issues by status.
    
    Returns:
        Dictionary mapping status to count
    """
    global tracking_manager
    return tracking_manager.get_status_summary()