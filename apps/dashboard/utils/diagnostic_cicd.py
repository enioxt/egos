#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_cicd.py

CI/CD integration for the EGOS Diagnostic Tracking System, enabling automated
roadmap updates and integration with development workflows.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_roadmap.py](mdc:./diagnostic_roadmap.py) - Roadmap integration
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Issue tracking
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import sys
import json
import logging
import argparse
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticCICD")

# EGOS Import Resilience
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import local components
try:
    from dashboard.diagnostic_roadmap import roadmap_manager
    from dashboard.diagnostic_tracking import tracking_manager
    local_imports_available = True
except ImportError:
    logger.warning("Local imports not available, using standalone mode")
    local_imports_available = False
    roadmap_manager = None
    tracking_manager = None

# GitHub integration settings
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN_ENV = "EGOS_GITHUB_TOKEN"

class CICDIntegration:
    """Manages CI/CD integration for the diagnostic tracking system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize CI/CD integration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        
        # Initialize components if available
        self.roadmap_manager = roadmap_manager
        self.tracking_manager = tracking_manager
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "github": {
                "owner": "enioxt",
                "repo": "egos",
                "default_branch": "main",
                "pull_request_title_prefix": "[DIAG]",
                "commit_message_prefix": "fix(diagnostic): "
            },
            "roadmap": {
                "main_roadmap_path": "ROADMAP.md",
                "subsystem_roadmap_paths": [
                    "subsystems/*/ROADMAP.md"
                ]
            },
            "ci": {
                "update_status_on_commit": True,
                "auto_create_tasks": True,
                "auto_assign_prs": True,
                "auto_close_issues": True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Merge configs
                def merge_configs(target, source):
                    for key, value in source.items():
                        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                            merge_configs(target[key], value)
                        else:
                            target[key] = value
                
                merge_configs(default_config, user_config)
                
                self.logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
        
        return default_config
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub API token.
        
        Returns:
            GitHub API token or None
        """
        return os.environ.get(GITHUB_TOKEN_ENV)
    
    def github_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GitHub API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        token = self.get_github_token()
        if not token:
            raise ValueError(f"GitHub token not found in environment variable {GITHUB_TOKEN_ENV}")
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{GITHUB_API_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
        except Exception as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise
    
    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> bool:
        """Create a new Git branch.
        
        Args:
            branch_name: Name of the branch to create
            base_branch: Base branch to create from
            
        Returns:
            Success status
        """
        try:
            # Get base branch if not specified
            if not base_branch:
                base_branch = self.config["github"]["default_branch"]
            
            # Get reference to base branch
            endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/git/refs/heads/{base_branch}"
            ref_data = self.github_request("GET", endpoint)
            
            # Create new branch
            new_ref_endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/git/refs"
            data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": ref_data["object"]["sha"]
            }
            
            self.github_request("POST", new_ref_endpoint, data)
            
            self.logger.info(f"Created branch {branch_name} from {base_branch}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            return False
    
    def update_roadmap_file(self, issue_id: str, status_update: Dict[str, Any], 
                         branch_name: str) -> bool:
        """Update a roadmap file in GitHub with diagnostic issue status.
        
        Args:
            issue_id: ID of the diagnostic issue
            status_update: Status update data
            branch_name: Branch to update
            
        Returns:
            Success status
        """
        try:
            # Get issue details
            if self.tracking_manager:
                issue = self.tracking_manager.get_issue(issue_id)
            else:
                # Standalone mode - get issue from API
                issue = self._get_issue_from_api(issue_id)
            
            if not issue:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Get roadmap task ID
            task_id = issue.get("roadmap_task_id")
            if not task_id:
                self.logger.warning(f"Issue {issue_id} has no linked roadmap task")
                
                # Auto-create task if enabled
                if self.config["ci"]["auto_create_tasks"]:
                    if self.roadmap_manager:
                        task_id = self.roadmap_manager.create_new_task_for_issue(issue)
                    else:
                        # Standalone mode
                        task_id = self._create_task_from_api(issue)
                    
                    if not task_id:
                        return False
                else:
                    return False
            
            # Find roadmap file containing the task
            if self.roadmap_manager:
                task_data = self.roadmap_manager.find_task(task_id)
            else:
                # Standalone mode
                task_data = self._find_task_from_api(task_id)
            
            if not task_data:
                self.logger.error(f"Task {task_id} not found in roadmap")
                return False
            
            # Get roadmap file path
            roadmap_path = task_data.get("file_path")
            if not roadmap_path:
                self.logger.error(f"Roadmap file path not found for task {task_id}")
                return False
            
            # Make roadmap path relative to repo root
            if str(project_root) in roadmap_path:
                relative_path = roadmap_path.replace(str(project_root), "").lstrip(os.sep).replace("\\", "/")
            else:
                relative_path = roadmap_path
            
            # Get current file content
            file_endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/contents/{relative_path}"
            params = {"ref": branch_name}
            file_data = self.github_request("GET", file_endpoint + "?" + "&".join([f"{k}={v}" for k, v in params.items()]))
            
            # Decode content
            import base64
            content = base64.b64decode(file_data["content"]).decode("utf-8")
            
            # Update task status in content
            task_line = task_data.get("line")
            if not task_line:
                self.logger.error(f"Task line not found for task {task_id}")
                return False
            
            # Update status indicator
            status = status_update.get("status", "in_progress")
            status_indicators = {
                "in_progress": "⏳",
                "completed": "✅",
                "resolved": "✅",
                "verified": "✅",
                "closed": "✅",
                "active": "⚡",
                "identified": "🔍",
                "acknowledged": "👀",
                "assigned": "👤",
                "reviewing": "🔎",
                "deferred": "⏰",
                "wont_fix": "❌"
            }
            
            indicator = status_indicators.get(status, "📋")
            
            # Replace status indicator in task line
            for old_indicator in status_indicators.values():
                if old_indicator in task_line:
                    updated_line = task_line.replace(old_indicator, indicator)
                    break
            else:
                # No indicator found, add one
                parts = task_line.split(task_id, 1)
                if len(parts) > 1:
                    updated_line = f"{parts[0]}{task_id} {indicator}{parts[1]}"
                else:
                    updated_line = f"{indicator} {task_line}"
            
            # Update content
            updated_content = content.replace(task_line, updated_line)
            
            # Commit updated file
            update_data = {
                "message": f"{self.config['github']['commit_message_prefix']}Update task {task_id} status to {status}",
                "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
                "sha": file_data["sha"],
                "branch": branch_name
            }
            
            self.github_request("PUT", file_endpoint, update_data)
            
            self.logger.info(f"Updated task {task_id} in {relative_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating roadmap file: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, issue_id: str) -> Optional[int]:
        """Create a pull request for roadmap updates.
        
        Args:
            branch_name: Branch name
            issue_id: Diagnostic issue ID
            
        Returns:
            Pull request number or None
        """
        try:
            # Get issue details
            if self.tracking_manager:
                issue = self.tracking_manager.get_issue(issue_id)
            else:
                # Standalone mode
                issue = self._get_issue_from_api(issue_id)
            
            if not issue:
                self.logger.error(f"Issue {issue_id} not found")
                return None
            
            # Create PR
            endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/pulls"
            data = {
                "title": f"{self.config['github']['pull_request_title_prefix']} Update roadmap for diagnostic issue DI-{issue_id}",
                "body": f"This PR updates the roadmap status for diagnostic issue DI-{issue_id}: {issue.get('title', 'Unknown Issue')}",
                "head": branch_name,
                "base": self.config["github"]["default_branch"]
            }
            
            response = self.github_request("POST", endpoint, data)
            
            pr_number = response.get("number")
            if not pr_number:
                self.logger.error("Pull request creation failed")
                return None
            
            self.logger.info(f"Created pull request #{pr_number} for issue DI-{issue_id}")
            
            # Auto-assign PR if enabled
            if self.config["ci"]["auto_assign_prs"] and issue.get("assignee"):
                self._assign_pull_request(pr_number, issue["assignee"])
            
            return pr_number
        except Exception as e:
            self.logger.error(f"Error creating pull request: {e}")
            return None
    
    def _assign_pull_request(self, pr_number: int, assignee: str) -> bool:
        """Assign a pull request to a user.
        
        Args:
            pr_number: Pull request number
            assignee: GitHub username to assign
            
        Returns:
            Success status
        """
        try:
            endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/issues/{pr_number}"
            data = {
                "assignees": [assignee]
            }
            
            self.github_request("PATCH", endpoint, data)
            
            self.logger.info(f"Assigned pull request #{pr_number} to {assignee}")
            return True
        except Exception as e:
            self.logger.error(f"Error assigning pull request: {e}")
            return False
    
    def update_issue_status_from_commit(self, commit_hash: str) -> List[str]:
        """Update issue status based on a commit message.
        
        Args:
            commit_hash: Commit hash
            
        Returns:
            List of updated issue IDs
        """
        try:
            # Get commit details
            endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/commits/{commit_hash}"
            commit_data = self.github_request("GET", endpoint)
            
            # Check commit message for issue references
            commit_message = commit_data.get("commit", {}).get("message", "")
            
            # Look for references to diagnostic issues (DI-XXX)
            issue_refs = re.findall(r'DI-(\d+)', commit_message)
            
            # Also check for "fixes #X" or "closes #X" syntax
            fixes_refs = re.findall(r'(?:fix|fixes|close|closes)\s+#(\d+)', commit_message.lower())
            
            # Combine and deduplicate
            all_refs = set(issue_refs + fixes_refs)
            
            updated_issues = []
            
            # Process each reference
            for issue_id in all_refs:
                # Determine status from commit message
                status = "in_progress"
                if "fix" in commit_message.lower() or "resolve" in commit_message.lower():
                    status = "resolved"
                elif "close" in commit_message.lower():
                    status = "closed"
                
                # Update issue status
                if self.tracking_manager:
                    self.tracking_manager.update_status(issue_id, status)
                else:
                    # Standalone mode
                    self._update_issue_status_api(issue_id, status)
                
                updated_issues.append(issue_id)
                self.logger.info(f"Updated issue DI-{issue_id} status to {status} from commit {commit_hash}")
            
            return updated_issues
        except Exception as e:
            self.logger.error(f"Error updating issue status from commit: {e}")
            return []
    
    def process_merged_pull_request(self, pr_number: int) -> List[str]:
        """Process a merged pull request to update issue status.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            List of updated issue IDs
        """
        try:
            # Get PR details
            endpoint = f"/repos/{self.config['github']['owner']}/{self.config['github']['repo']}/pulls/{pr_number}"
            pr_data = self.github_request("GET", endpoint)
            
            # Check if PR is merged
            if not pr_data.get("merged"):
                self.logger.warning(f"Pull request #{pr_number} is not merged")
                return []
            
            # Get PR description and title
            description = pr_data.get("body", "")
            title = pr_data.get("title", "")
            
            # Look for references to diagnostic issues (DI-XXX)
            issue_refs = re.findall(r'DI-(\d+)', description + " " + title)
            
            updated_issues = []
            
            # Process each reference
            for issue_id in issue_refs:
                # Auto-close issue if enabled
                if self.config["ci"]["auto_close_issues"]:
                    if self.tracking_manager:
                        self.tracking_manager.update_status(issue_id, "verified")
                    else:
                        # Standalone mode
                        self._update_issue_status_api(issue_id, "verified")
                    
                    updated_issues.append(issue_id)
                    self.logger.info(f"Updated issue DI-{issue_id} status to verified from merged PR #{pr_number}")
            
            return updated_issues
        except Exception as e:
            self.logger.error(f"Error processing merged pull request: {e}")
            return []
    
    # Standalone mode API methods
    def _get_issue_from_api(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get issue details via API in standalone mode.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Issue data or None
        """
        try:
            # Implementation depends on your API
            # This is a placeholder
            api_url = os.environ.get("DIAGNOSTIC_API_URL", "http://localhost:8000")
            response = requests.get(f"{api_url}/api/issues/{issue_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting issue from API: {e}")
            return None
    
    def _update_issue_status_api(self, issue_id: str, status: str) -> bool:
        """Update issue status via API in standalone mode.
        
        Args:
            issue_id: Issue ID
            status: New status
            
        Returns:
            Success status
        """
        try:
            # Implementation depends on your API
            # This is a placeholder
            api_url = os.environ.get("DIAGNOSTIC_API_URL", "http://localhost:8000")
            response = requests.patch(
                f"{api_url}/api/issues/{issue_id}",
                json={"status": status}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Error updating issue status via API: {e}")
            return False
    
    def _find_task_from_api(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Find roadmap task via API in standalone mode.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None
        """
        try:
            # Implementation depends on your API
            # This is a placeholder
            api_url = os.environ.get("DIAGNOSTIC_API_URL", "http://localhost:8000")
            response = requests.get(f"{api_url}/api/roadmap/tasks/{task_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error finding task from API: {e}")
            return None
    
    def _create_task_from_api(self, issue: Dict[str, Any]) -> Optional[str]:
        """Create roadmap task via API in standalone mode.
        
        Args:
            issue: Issue data
            
        Returns:
            Task ID or None
        """
        try:
            # Implementation depends on your API
            # This is a placeholder
            api_url = os.environ.get("DIAGNOSTIC_API_URL", "http://localhost:8000")
            response = requests.post(
                f"{api_url}/api/roadmap/tasks",
                json={"issue": issue}
            )
            response.raise_for_status()
            return response.json().get("task_id")
        except Exception as e:
            self.logger.error(f"Error creating task from API: {e}")
            return None

# CLI for standalone use
def main():
    """Command-line interface for CI/CD integration."""
    parser = argparse.ArgumentParser(description="EGOS Diagnostic CI/CD Integration")
    parser.add_argument("--config", help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Update issue status
    update_parser = subparsers.add_parser("update-issue", help="Update issue status from commit")
    update_parser.add_argument("--commit", required=True, help="Commit hash")
    
    # Update roadmap
    roadmap_parser = subparsers.add_parser("update-roadmap", help="Update roadmap for issue")
    roadmap_parser.add_argument("--issue-id", required=True, help="Diagnostic issue ID")
    roadmap_parser.add_argument("--status", required=True, help="New status")
    roadmap_parser.add_argument("--create-pr", action="store_true", help="Create pull request")
    
    # Process PR
    pr_parser = subparsers.add_parser("process-pr", help="Process merged pull request")
    pr_parser.add_argument("--pr-number", required=True, type=int, help="Pull request number")
    
    args = parser.parse_args()
    
    # Initialize CI/CD integration
    cicd = CICDIntegration(args.config)
    
    if args.command == "update-issue":
        updated_issues = cicd.update_issue_status_from_commit(args.commit)
        if updated_issues:
            print(f"Updated issues: {', '.join(['DI-' + i for i in updated_issues])}")
        else:
            print("No issues updated")
    
    elif args.command == "update-roadmap":
        # Create branch
        branch_name = f"diagnostic-{args.issue_id}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if not cicd.create_branch(branch_name):
            print(f"Failed to create branch {branch_name}")
            return 1
        
        # Update roadmap
        status_update = {"status": args.status}
        success = cicd.update_roadmap_file(args.issue_id, status_update, branch_name)
        
        if not success:
            print(f"Failed to update roadmap for issue DI-{args.issue_id}")
            return 1
        
        # Create PR if requested
        if args.create_pr:
            pr_number = cicd.create_pull_request(branch_name, args.issue_id)
            if pr_number:
                print(f"Created pull request #{pr_number}")
            else:
                print("Failed to create pull request")
                return 1
        
        print(f"Successfully updated roadmap for issue DI-{args.issue_id}")
    
    elif args.command == "process-pr":
        updated_issues = cicd.process_merged_pull_request(args.pr_number)
        if updated_issues:
            print(f"Updated issues: {', '.join(['DI-' + i for i in updated_issues])}")
        else:
            print("No issues updated")
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())