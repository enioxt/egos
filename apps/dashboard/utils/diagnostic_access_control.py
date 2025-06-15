"""
EGOS Diagnostic Access Control

This module provides user authentication, authorization, and access control
for the diagnostic tracking system, ensuring appropriate permissions for
viewing and modifying sensitive diagnostic information.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Main visualization
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Data tracking system
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

import json
import logging
import hashlib
import uuid
import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from threading import Lock
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAccessControl")

# Access control constants
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "egos_admin"  # Should be changed in production

# Role levels
ROLE_LEVELS = {
    "viewer": 1,
    "reporter": 2,
    "contributor": 3,
    "administrator": 4
}

# Permission mapping
PERMISSIONS = {
    "viewer": [
        "view_issues",
        "view_metrics",
        "export_data"
    ],
    "reporter": [
        "view_issues",
        "view_metrics",
        "export_data",
        "add_comments",
        "report_issues"
    ],
    "contributor": [
        "view_issues",
        "view_metrics",
        "export_data",
        "add_comments",
        "report_issues",
        "update_issues",
        "assign_issues",
        "roadmap_integration"
    ],
    "administrator": [
        "view_issues",
        "view_metrics",
        "export_data",
        "add_comments",
        "report_issues",
        "update_issues",
        "assign_issues",
        "roadmap_integration",
        "delete_issues",
        "manage_users",
        "system_configuration"
    ]
}

# Data locks
user_data_lock = Lock()

class AccessControlManager:
    """Manages user authentication, authorization, and access control."""
    
    def __init__(self, config_path: str = "diagnostic_auth.json"):
        """Initialize the access control manager.
        
        Args:
            config_path: Path to the authentication configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logger
        self.users = self._load_users()
        self.sessions = {}
        
        # Ensure admin user exists
        self._ensure_admin_user()
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load user data from file.
        
        Returns:
            Dictionary of users
        """
        with user_data_lock:
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        users = json.load(f)
                    
                    self.logger.info(f"Loaded user data with {len(users)} users")
                    return users
                else:
                    # Create initial user data
                    default_users = {}
                    
                    # Save empty user data
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        json.dump(default_users, f, indent=2)
                    
                    self.logger.info("Created new user data file")
                    return default_users
            except Exception as e:
                self.logger.error(f"Error loading user data: {e}")
                return {}
    
    def _save_users(self) -> bool:
        """Save user data to file.
        
        Returns:
            Success status
        """
        with user_data_lock:
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.users, f, indent=2)
                
                self.logger.info(f"Saved user data with {len(self.users)} users")
                return True
            except Exception as e:
                self.logger.error(f"Error saving user data: {e}")
                return False
    
    def _ensure_admin_user(self) -> None:
        """Ensure that an admin user exists."""
        if not self.users or DEFAULT_ADMIN_USERNAME not in self.users:
            # Create default admin user
            self.add_user(
                username=DEFAULT_ADMIN_USERNAME,
                password=DEFAULT_ADMIN_PASSWORD,
                full_name="EGOS Administrator",
                email="admin@egos.local",
                role="administrator"
            )
            
            self.logger.warning(
                f"Created default admin user '{DEFAULT_ADMIN_USERNAME}' with password '{DEFAULT_ADMIN_PASSWORD}'. "
                "Please change this password immediately!"
            )
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and create a session.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session token if authentication successful, None otherwise
        """
        # Check if user exists
        if username not in self.users:
            self.logger.warning(f"Authentication failed: User '{username}' not found")
            return None
        
        # Check password
        user = self.users[username]
        if user.get("password_hash") != self._hash_password(password):
            self.logger.warning(f"Authentication failed: Invalid password for user '{username}'")
            return None
        
        # Generate session token
        session_token = str(uuid.uuid4())
        
        # Store session
        self.sessions[session_token] = {
            "username": username,
            "created": datetime.datetime.now().isoformat(),
            "last_active": datetime.datetime.now().isoformat()
        }
        
        self.logger.info(f"User '{username}' authenticated successfully")
        
        # Update last login
        self.users[username]["last_login"] = datetime.datetime.now().isoformat()
        self._save_users()
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User data if session is valid, None otherwise
        """
        # Check if session exists
        if session_token not in self.sessions:
            return None
        
        # Get session data
        session = self.sessions[session_token]
        username = session.get("username")
        
        # Check if user still exists
        if username not in self.users:
            del self.sessions[session_token]
            return None
        
        # Update last active time
        self.sessions[session_token]["last_active"] = datetime.datetime.now().isoformat()
        
        # Return user data
        return self.users[username]
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            Success status
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.logger.info(f"Session {session_token} invalidated")
            return True
        
        return False
    
    def clean_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions.
        
        Args:
            max_age_hours: Maximum age of sessions in hours
            
        Returns:
            Number of sessions cleaned
        """
        current_time = datetime.datetime.now()
        max_age = datetime.timedelta(hours=max_age_hours)
        expired_sessions = []
        
        # Find expired sessions
        for token, session in self.sessions.items():
            last_active = datetime.datetime.fromisoformat(session.get("last_active"))
            if current_time - last_active > max_age:
                expired_sessions.append(token)
        
        # Remove expired sessions
        for token in expired_sessions:
            del self.sessions[token]
        
        self.logger.info(f"Cleaned {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
    
    def add_user(self, username: str, password: str, full_name: str, 
              email: str, role: str = "viewer") -> bool:
        """Add a new user.
        
        Args:
            username: Username
            password: Password
            full_name: Full name
            email: Email address
            role: User role
            
        Returns:
            Success status
        """
        # Validate role
        if role not in ROLE_LEVELS:
            self.logger.error(f"Invalid role: {role}")
            return False
        
        # Check if username already exists
        if username in self.users:
            self.logger.error(f"User '{username}' already exists")
            return False
        
        # Create user
        with user_data_lock:
            self.users[username] = {
                "username": username,
                "password_hash": self._hash_password(password),
                "full_name": full_name,
                "email": email,
                "role": role,
                "permissions": PERMISSIONS.get(role, []),
                "created": datetime.datetime.now().isoformat(),
                "last_login": None
            }
            
            # Save users
            success = self._save_users()
            
            if success:
                self.logger.info(f"Added user '{username}' with role '{role}'")
            
            return success
    
    def update_user(self, username: str, updates: Dict[str, Any], 
                 current_user: str) -> bool:
        """Update an existing user.
        
        Args:
            username: Username of user to update
            updates: Dictionary of fields to update
            current_user: Username of user making the update
            
        Returns:
            Success status
        """
        # Check if user exists
        if username not in self.users:
            self.logger.error(f"User '{username}' not found")
            return False
        
        # Check if current user has permission
        current_user_role = self.users.get(current_user, {}).get("role")
        if current_user != username and current_user_role != "administrator":
            self.logger.error(f"User '{current_user}' does not have permission to update user '{username}'")
            return False
        
        # Update user
        with user_data_lock:
            for key, value in updates.items():
                if key == "password":
                    # Hash password
                    self.users[username]["password_hash"] = self._hash_password(value)
                elif key == "role":
                    # Update role and permissions
                    if value in ROLE_LEVELS:
                        self.users[username]["role"] = value
                        self.users[username]["permissions"] = PERMISSIONS.get(value, [])
                    else:
                        self.logger.error(f"Invalid role: {value}")
                elif key not in ["username", "password_hash", "created"]:
                    # Update other fields
                    self.users[username][key] = value
            
            # Save users
            success = self._save_users()
            
            if success:
                self.logger.info(f"Updated user '{username}'")
            
            return success
    
    def delete_user(self, username: str, current_user: str) -> bool:
        """Delete a user.
        
        Args:
            username: Username of user to delete
            current_user: Username of user making the deletion
            
        Returns:
            Success status
        """
        # Check if user exists
        if username not in self.users:
            self.logger.error(f"User '{username}' not found")
            return False
        
        # Check if current user has permission
        current_user_role = self.users.get(current_user, {}).get("role")
        if current_user_role != "administrator":
            self.logger.error(f"User '{current_user}' does not have permission to delete users")
            return False
        
        # Prevent deletion of admin user if it's the only admin
        if username == DEFAULT_ADMIN_USERNAME:
            # Check if there are other admins
            admin_count = sum(1 for user in self.users.values() if user.get("role") == "administrator")
            if admin_count <= 1:
                self.logger.error("Cannot delete the only administrator")
                return False
        
        # Delete user
        with user_data_lock:
            del self.users[username]
            
            # Invalidate any active sessions
            for token, session in list(self.sessions.items()):
                if session.get("username") == username:
                    del self.sessions[token]
            
            # Save users
            success = self._save_users()
            
            if success:
                self.logger.info(f"Deleted user '{username}'")
            
            return success
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if a user has a specific permission.
        
        Args:
            username: Username
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        # Check if user exists
        if username not in self.users:
            return False
        
        # Get user permissions
        user_permissions = self.users[username].get("permissions", [])
        
        return permission in user_permissions
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data.
        
        Args:
            username: Username
            
        Returns:
            User data or None if not found
        """
        return self.users.get(username)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users.
        
        Returns:
            List of user data dictionaries
        """
        # Create copies without password hashes
        user_list = []
        for username, user_data in self.users.items():
            user_copy = user_data.copy()
            user_copy.pop("password_hash", None)
            user_list.append(user_copy)
        
        return user_list
    
    def change_password(self, username: str, current_password: str, 
                     new_password: str) -> bool:
        """Change a user's password.
        
        Args:
            username: Username
            current_password: Current password
            new_password: New password
            
        Returns:
            Success status
        """
        # Check if user exists
        if username not in self.users:
            self.logger.error(f"User '{username}' not found")
            return False
        
        # Verify current password
        current_hash = self.users[username].get("password_hash")
        if current_hash != self._hash_password(current_password):
            self.logger.error(f"Invalid current password for user '{username}'")
            return False
        
        # Update password
        with user_data_lock:
            self.users[username]["password_hash"] = self._hash_password(new_password)
            
            # Save users
            success = self._save_users()
            
            if success:
                self.logger.info(f"Changed password for user '{username}'")
            
            return success

# Create a singleton instance
access_manager = AccessControlManager()

# Streamlit authentication helpers
def login_form() -> Tuple[bool, Optional[str]]:
    """Display a login form and authenticate the user.
    
    Returns:
        Tuple of (authenticated, username)
    """
    # Check if already authenticated
    if "auth_token" in st.session_state and "username" in st.session_state:
        # Validate session
        user_data = access_manager.validate_session(st.session_state["auth_token"])
        if user_data:
            return True, st.session_state["username"]
    
    # Display login form
    with st.form("login_form"):
        st.title("EGOS Diagnostic Dashboard Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log In")
        
        if submit:
            # Authenticate
            auth_token = access_manager.authenticate(username, password)
            if auth_token:
                # Store session
                st.session_state["auth_token"] = auth_token
                st.session_state["username"] = username
                st.success("Authentication successful")
                return True, username
            else:
                st.error("Invalid username or password")
    
    return False, None

def logout() -> None:
    """Log out the current user."""
    if "auth_token" in st.session_state:
        access_manager.invalidate_session(st.session_state["auth_token"])
        del st.session_state["auth_token"]
    
    if "username" in st.session_state:
        del st.session_state["username"]

def require_login(permission: Optional[str] = None) -> bool:
    """Require the user to be logged in.
    
    Args:
        permission: Optional permission to check
        
    Returns:
        True if authentication successful, False otherwise
    """
    authenticated, username = login_form()
    
    if not authenticated:
        return False
    
    # Check permission if required
    if permission and not access_manager.has_permission(username, permission):
        st.error(f"You do not have the required permission: {permission}")
        return False
    
    return True

def user_management_ui() -> None:
    """Display user management UI."""
    # Check if user is an admin
    if "username" not in st.session_state:
        st.error("You must be logged in to manage users")
        return
    
    username = st.session_state["username"]
    if not access_manager.has_permission(username, "manage_users"):
        st.error("You do not have permission to manage users")
        return
    
    st.title("User Management")
    
    # Get all users
    users = access_manager.get_all_users()
    
    # Display user table
    st.markdown("### Current Users")
    user_df = {
        "Username": [],
        "Full Name": [],
        "Email": [],
        "Role": [],
        "Last Login": []
    }
    
    for user in users:
        user_df["Username"].append(user.get("username", ""))
        user_df["Full Name"].append(user.get("full_name", ""))
        user_df["Email"].append(user.get("email", ""))
        user_df["Role"].append(user.get("role", ""))
        user_df["Last Login"].append(user.get("last_login", "Never"))
    
    st.dataframe(user_df)
    
    # Add user form
    st.markdown("### Add New User")
    with st.form("add_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_full_name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_role = st.selectbox("Role", list(ROLE_LEVELS.keys()))
        submit = st.form_submit_button("Add User")
        
        if submit:
            if not new_username or not new_password:
                st.error("Username and password are required")
            else:
                success = access_manager.add_user(
                    username=new_username,
                    password=new_password,
                    full_name=new_full_name,
                    email=new_email,
                    role=new_role
                )
                
                if success:
                    st.success(f"User '{new_username}' added successfully")
                    st.experimental_rerun()
                else:
                    st.error("Failed to add user")
    
    # Delete user form
    st.markdown("### Delete User")
    with st.form("delete_user_form"):
        del_username = st.selectbox("Select User", [u.get("username") for u in users if u.get("username") != username])
        del_confirm = st.checkbox("I confirm that I want to delete this user")
        submit = st.form_submit_button("Delete User")
        
        if submit:
            if not del_confirm:
                st.error("Please confirm deletion")
            else:
                success = access_manager.delete_user(del_username, username)
                
                if success:
                    st.success(f"User '{del_username}' deleted successfully")
                    st.experimental_rerun()
                else:
                    st.error("Failed to delete user")

# For standalone testing
if __name__ == "__main__":
    if require_login("manage_users"):
        user_management_ui()