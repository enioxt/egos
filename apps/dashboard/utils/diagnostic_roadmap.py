"""
EGOS Diagnostic Roadmap Integration

This module provides integration between the diagnostic tracking system and
EGOS roadmaps, enabling automatic cross-referencing of diagnostic issues
with roadmap tasks for better project management and oversight.

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

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import datetime
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticRoadmap")

# Roadmap file patterns
MAIN_ROADMAP_PATH = "../../ROADMAP.md"
ROADMAP_PATTERNS = [
    "**/ROADMAP.md",
    "**/*roadmap*.md",
    "**/roadmap/*.md"
]

# Task ID pattern - matches format like KOI-DOC-001
TASK_ID_PATTERN = re.compile(r'([A-Z]{2,5})-([A-Z]{2,5})-(\d{3,4})')

# Markdown section pattern - matches ## Heading format
SECTION_PATTERN = re.compile(r'^#+\s+(.+)$')

# Task status indicators
TASK_STATUS_INDICATORS = {
    "active": "⚡",
    "in_progress": "⏳",
    "completed": "✅",
    "planned": "📋",
    "blocked": "🚫",
    "deprecated": "❌"
}

class RoadmapManager:
    """Manages integration between diagnostic issues and roadmap tasks."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the roadmap manager.
        
        Args:
            project_root: Path to the project root directory
        """
        # Set project root
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Try to determine project root from file location
            self.project_root = Path(__file__).resolve().parents[2]
        
        self.logger = logger
        self.roadmap_lock = Lock()
        self.roadmap_files = {}  # Cache of roadmap files {path: last_modified_time}
        self.task_index = {}  # Index of tasks {task_id: {path, title, etc.}}
        
        # Initialize
        self._discover_roadmap_files()
        self._build_task_index()
    
    def _discover_roadmap_files(self) -> None:
        """Discover all roadmap files in the project."""
        try:
            # Clear existing cache
            self.roadmap_files = {}
            
            # Always add main roadmap if it exists
            main_roadmap = self.project_root / MAIN_ROADMAP_PATH
            if main_roadmap.exists():
                self.roadmap_files[str(main_roadmap)] = main_roadmap.stat().st_mtime
                self.logger.info(f"Found main roadmap at {main_roadmap}")
            
            # Find roadmap files using patterns
            for pattern in ROADMAP_PATTERNS:
                for path in self.project_root.glob(pattern):
                    if path.is_file():
                        self.roadmap_files[str(path)] = path.stat().st_mtime
                        self.logger.info(f"Found roadmap file: {path}")
            
            self.logger.info(f"Discovered {len(self.roadmap_files)} roadmap files")
        except Exception as e:
            self.logger.error(f"Error discovering roadmap files: {e}")
    
    def _build_task_index(self) -> None:
        """Build an index of all tasks in all roadmap files."""
        with self.roadmap_lock:
            # Clear existing index
            self.task_index = {}
            
            # Process each roadmap file
            for file_path in self.roadmap_files:
                try:
                    self._index_roadmap_file(file_path)
                except Exception as e:
                    self.logger.error(f"Error indexing roadmap file {file_path}: {e}")
    
    def _index_roadmap_file(self, file_path: str) -> None:
        """Index tasks in a roadmap file.
        
        Args:
            file_path: Path to the roadmap file
        """
        current_section = "Unknown"
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Process lines
            for i, line in enumerate(lines):
                # Check for section
                section_match = SECTION_PATTERN.match(line.strip())
                if section_match:
                    current_section = section_match.group(1)
                    continue
                
                # Check for task ID
                task_ids = TASK_ID_PATTERN.findall(line)
                for task_id_parts in task_ids:
                    task_id = f"{task_id_parts[0]}-{task_id_parts[1]}-{task_id_parts[2]}"
                    
                    # Check status
                    status = "planned"
                    for status_key, indicator in TASK_STATUS_INDICATORS.items():
                        if indicator in line:
                            status = status_key
                            break
                    
                    # Extract title (text after task ID)
                    title_match = re.search(fr'{task_id}\s*-?\s*(.+)', line)
                    title = title_match.group(1).strip() if title_match else "Unknown Task"
                    
                    # Add to index
                    self.task_index[task_id] = {
                        "id": task_id,
                        "title": title,
                        "file_path": file_path,
                        "line_number": i + 1,
                        "section": current_section,
                        "status": status,
                        "line": line.strip()
                    }
                    
                    self.logger.debug(f"Indexed task {task_id} in {file_path}")
        except Exception as e:
            self.logger.error(f"Error processing roadmap file {file_path}: {e}")
    
    def refresh_index(self) -> None:
        """Refresh the roadmap file index."""
        self._discover_roadmap_files()
        self._build_task_index()
    
    def find_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Find a task by ID.
        
        Args:
            task_id: Task ID to find
            
        Returns:
            Task data or None if not found
        """
        return self.task_index.get(task_id)
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search for tasks matching the query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tasks
        """
        results = []
        query = query.lower()
        
        for task_id, task_data in self.task_index.items():
            # Check if query matches task ID or title
            if query in task_id.lower() or query in task_data["title"].lower():
                results.append(task_data)
        
        return results
    
    def find_related_tasks(self, issue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find tasks that might be related to a diagnostic issue.
        
        Args:
            issue_data: Diagnostic issue data
            
        Returns:
            List of potentially related tasks
        """
        related_tasks = []
        
        # Extract keywords from issue
        keywords = set()
        if "title" in issue_data:
            keywords.update(issue_data["title"].lower().split())
        if "description" in issue_data:
            keywords.update(issue_data["description"].lower().split())
        if "subsystem" in issue_data:
            keywords.add(issue_data["subsystem"].lower())
        
        # Remove common words
        common_words = {"the", "and", "or", "in", "of", "to", "a", "an", "is", "for", "with", "by"}
        keywords = keywords - common_words
        
        # Find tasks that match keywords
        for task_id, task_data in self.task_index.items():
            task_text = f"{task_data['title']} {task_data['line']}".lower()
            
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in task_text)
            
            if matches > 0:
                task_data["relevance"] = matches
                related_tasks.append(task_data)
        
        # Sort by relevance
        related_tasks.sort(key=lambda x: x["relevance"], reverse=True)
        
        return related_tasks[:10]  # Return top 10 related tasks
    
    def link_issue_to_task(self, issue_id: str, task_id: str) -> bool:
        """Link a diagnostic issue to a roadmap task.
        
        Args:
            issue_id: Diagnostic issue ID
            task_id: Roadmap task ID
            
        Returns:
            Success status
        """
        # Verify task exists
        task_data = self.find_task(task_id)
        if not task_data:
            self.logger.error(f"Task {task_id} not found")
            return False
        
        # Load diagnostic tracking data
        try:
            data_path = Path("diagnostic_tracking.json")
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    tracking_data = json.load(f)
            else:
                tracking_data = {
                    "last_updated": datetime.datetime.now().isoformat(),
                    "issues": []
                }
            
            # Find issue and update roadmap link
            found = False
            for issue in tracking_data.get("issues", []):
                if issue.get("id") == issue_id:
                    issue["roadmap_task_id"] = task_id
                    issue["roadmap_task_title"] = task_data["title"]
                    issue["roadmap_task_file"] = task_data["file_path"]
                    found = True
                    break
            
            if not found:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Save updated tracking data
            tracking_data["last_updated"] = datetime.datetime.now().isoformat()
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(tracking_data, f, indent=2)
            
            self.logger.info(f"Linked issue {issue_id} to task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error linking issue to task: {e}")
            return False
    
    def update_roadmap_with_issue(self, issue_id: str, task_id: str) -> bool:
        """Update a roadmap file with a reference to a diagnostic issue.
        
        Args:
            issue_id: Diagnostic issue ID
            task_id: Roadmap task ID
            
        Returns:
            Success status
        """
        # Verify task exists
        task_data = self.find_task(task_id)
        if not task_data:
            self.logger.error(f"Task {task_id} not found")
            return False
        
        try:
            # Load diagnostic tracking data to get issue details
            data_path = Path("diagnostic_tracking.json")
            if not data_path.exists():
                self.logger.error("Diagnostic tracking data not found")
                return False
                
            with open(data_path, 'r', encoding='utf-8') as f:
                tracking_data = json.load(f)
            
            # Find issue
            issue_data = None
            for issue in tracking_data.get("issues", []):
                if issue.get("id") == issue_id:
                    issue_data = issue
                    break
            
            if not issue_data:
                self.logger.error(f"Issue {issue_id} not found")
                return False
            
            # Read roadmap file
            file_path = task_data["file_path"]
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the line with the task
            line_index = task_data["line_number"] - 1
            if line_index >= len(lines):
                self.logger.error(f"Line index out of range for task {task_id}")
                return False
            
            # Check if issue reference already exists
            if issue_id in lines[line_index]:
                self.logger.info(f"Issue reference already exists in task {task_id}")
                return True
            
            # Prepare issue reference
            issue_title = issue_data.get("title", "Unknown Issue")
            issue_reference = f" [DI-{issue_id}: {issue_title}]"
            
            # Add issue reference to the end of the line
            line = lines[line_index].rstrip()
            lines[line_index] = line + issue_reference + "\n"
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.logger.info(f"Updated roadmap file {file_path} with reference to issue {issue_id}")
            
            # Refresh index to capture the change
            self._build_task_index()
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating roadmap with issue reference: {e}")
            return False
    
    def generate_cross_references(self, issue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cross-references for an issue to potentially relevant tasks.
        
        Args:
            issue_data: Diagnostic issue data
            
        Returns:
            List of cross-reference data
        """
        # Find related tasks
        related_tasks = self.find_related_tasks(issue_data)
        
        # Format cross-references
        cross_references = []
        for task in related_tasks:
            # Get relative path for markdown link
            try:
                file_path = Path(task["file_path"])
                relative_path = file_path.relative_to(self.project_root)
                markdown_path = f"mdc:{relative_path}"
                
                cross_references.append({
                    "task_id": task["id"],
                    "title": task["title"],
                    "file_path": str(relative_path),
                    "markdown_link": f"[{task['id']}]({markdown_path}#{task['id'].lower()})",
                    "relevance": task.get("relevance", 0)
                })
            except Exception as e:
                self.logger.error(f"Error formatting cross-reference for task {task['id']}: {e}")
        
        return cross_references
    
    def create_new_task_for_issue(self, issue_data: Dict[str, Any], 
                               roadmap_path: Optional[str] = None) -> Optional[str]:
        """Create a new roadmap task for a diagnostic issue.
        
        Args:
            issue_data: Diagnostic issue data
            roadmap_path: Optional path to the roadmap file to update
            
        Returns:
            New task ID or None if creation failed
        """
        try:
            # Determine roadmap file to update
            if roadmap_path:
                file_path = Path(roadmap_path)
            else:
                # Default to main roadmap
                file_path = self.project_root / MAIN_ROADMAP_PATH
            
            if not file_path.exists():
                self.logger.error(f"Roadmap file {file_path} not found")
                return None
            
            # Generate task ID based on subsystem
            subsystem = issue_data.get("subsystem", "SYS")
            subsystem_code = subsystem[:3].upper()
            
            # Get existing task IDs for this subsystem to determine next number
            existing_ids = [
                task["id"] for task in self.task_index.values()
                if task["id"].startswith(f"{subsystem_code}-")
            ]
            
            # Find next available number
            if existing_ids:
                existing_numbers = []
                for task_id in existing_ids:
                    parts = task_id.split("-")
                    if len(parts) == 3:
                        try:
                            existing_numbers.append(int(parts[2]))
                        except ValueError:
                            pass
                
                next_number = max(existing_numbers) + 1 if existing_numbers else 1
            else:
                next_number = 1
            
            # Create task ID
            task_id = f"{subsystem_code}-FIX-{next_number:03d}"
            
            # Determine task section based on priority
            priority = issue_data.get("priority", "medium").lower()
            if priority == "high":
                section = "## In Progress"
            else:
                section = "## Planned"
            
            # Create task entry
            issue_id = issue_data.get("id", "unknown")
            issue_title = issue_data.get("title", "Unknown Issue")
            task_title = f"Fix {issue_title}"
            task_entry = f"- {TASK_STATUS_INDICATORS.get('planned', '📋')} {task_id} - {task_title} [DI-{issue_id}]"
            
            # Read roadmap file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find appropriate section
            section_line = -1
            for i, line in enumerate(lines):
                if line.strip() == section:
                    section_line = i
                    break
            
            if section_line == -1:
                # Section not found, add it at the end
                lines.append("\n" + section + "\n\n")
                section_line = len(lines) - 2
            
            # Find end of section or start of next section
            end_of_section = len(lines)
            for i in range(section_line + 1, len(lines)):
                if lines[i].startswith("#"):
                    end_of_section = i
                    break
            
            # Insert task entry
            lines.insert(end_of_section, task_entry + "\n")
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.logger.info(f"Created new task {task_id} for issue {issue_id} in roadmap {file_path}")
            
            # Refresh index to capture the new task
            self._build_task_index()
            
            return task_id
        except Exception as e:
            self.logger.error(f"Error creating new task for issue: {e}")
            return None
    
    def get_task_status_distribution(self) -> Dict[str, int]:
        """Get distribution of task statuses across all roadmaps.
        
        Returns:
            Dictionary of status counts
        """
        status_counts = {status: 0 for status in TASK_STATUS_INDICATORS.keys()}
        
        for task in self.task_index.values():
            status = task.get("status", "planned")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def get_roadmap_task_count(self) -> Dict[str, int]:
        """Get count of tasks in each roadmap file.
        
        Returns:
            Dictionary of file paths and task counts
        """
        roadmap_counts = {}
        
        for task in self.task_index.values():
            file_path = task.get("file_path", "unknown")
            roadmap_counts[file_path] = roadmap_counts.get(file_path, 0) + 1
        
        return roadmap_counts

# Create a roadmap manager instance for import
roadmap_manager = RoadmapManager()

# Helper functions for external components
def find_related_tasks(issue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find roadmap tasks related to an issue.
    
    Args:
        issue_data: Diagnostic issue data
        
    Returns:
        List of related tasks
    """
    global roadmap_manager
    return roadmap_manager.find_related_tasks(issue_data)

def link_issue_to_task(issue_id: str, task_id: str) -> bool:
    """Link a diagnostic issue to a roadmap task.
    
    Args:
        issue_id: Diagnostic issue ID
        task_id: Roadmap task ID
        
    Returns:
        Success status
    """
    global roadmap_manager
    return roadmap_manager.link_issue_to_task(issue_id, task_id)

def create_task_for_issue(issue_data: Dict[str, Any]) -> Optional[str]:
    """Create a new roadmap task for a diagnostic issue.
    
    Args:
        issue_data: Diagnostic issue data
        
    Returns:
        New task ID or None if creation failed
    """
    global roadmap_manager
    return roadmap_manager.create_new_task_for_issue(issue_data)

# Refresh index on module import
if __name__ != "__main__":
    roadmap_manager.refresh_index()