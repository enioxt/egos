#!/usr/bin/env python
"""EGOS Roadmap Synchronization Tool

This script synchronizes statuses between the main EGOS roadmap and local roadmaps,
ensuring consistent task tracking across the project hierarchy.

It implements the principles defined in docs/governance/roadmap_hierarchy.md,
maintaining proper parent-child relationships between epics and stories.

Usage:
    python roadmap_sync.py [--base-path PATH] [--update] [--report-file PATH]

Author: EGOS Development Team
Date: 2025-05-18

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Status definitions and mappings
STATUS_HIERARCHY = {
    "backlog": 0,
    "blocked": 1,
    "in progress": 2,
    "review": 3,
    "done": 4,
    "deferred": 5
}

STATUS_EMOJI = {
    "backlog": "🔄",
    "blocked": "⛔",
    "in progress": "⏳",
    "review": "🔍",
    "done": "✅",
    "deferred": "🔜"
}

# Regular expressions for parsing roadmaps
EPIC_PATTERN = r'###\s+\[(?P<id>EGOS-EPIC-\d+)\]\s+(?P<title>.+)'
STORY_PATTERN = r'###\s+\[(?P<id>EGOS-EPIC-\d+-\d+)\]\s+(?P<title>.+)'
STATUS_PATTERN = r'\*\*Status:\*\*\s+(?P<status>[^\\n]+)'
PARENT_PATTERN = r'\*\*Parent Epic:\*\*\s+\[(?P<parent_id>EGOS-EPIC-\d+)\]'
CHILD_PATTERN = r'\*\*Child Tasks:\*\*\s+(?P<children>[\s\S]+?)(?=\n\n|\Z)'
CHILD_ITEM_PATTERN = r'-\s+\[(?P<child_id>EGOS-EPIC-\d+-\d+)\]'


class RoadmapItem:
    """Represents a roadmap item (epic or story)."""
    
    def __init__(self, item_id: str, title: str, status: str, file_path: str, line_number: int):
        """Initialize a roadmap item.
        
        Args:
            item_id: Unique identifier for the item
            title: Title of the item
            status: Current status of the item
            file_path: Path to the file containing the item
            line_number: Line number where the item starts
        """
        self.item_id = item_id
        self.title = title
        self.status = self._normalize_status(status)
        self.file_path = file_path
        self.line_number = line_number
        self.parent_id = None
        self.children = []
        
    def _normalize_status(self, status: str) -> str:
        """Normalize status string to a standard format.
        
        Args:
            status: Status string to normalize
            
        Returns:
            Normalized status string
        """
        # Remove emoji and convert to lowercase
        status = re.sub(r'[^\w\s]', '', status).strip().lower()
        
        # Map common variations to standard statuses
        status_map = {
            "not started": "backlog",
            "pending": "backlog",
            "planned": "backlog",
            "in development": "in progress",
            "implementing": "in progress",
            "active": "in progress",
            "reviewing": "review",
            "testing": "review",
            "completed": "done",
            "finished": "done",
            "postponed": "deferred",
            "on hold": "deferred",
            "waiting": "blocked",
            "dependency": "blocked"
        }
        
        return status_map.get(status, status)
    
    def is_epic(self) -> bool:
        """Check if this item is an epic.
        
        Returns:
            True if this is an epic, False if it's a story
        """
        return "-" not in self.item_id.split("-")[-1]
    
    def get_status_level(self) -> int:
        """Get the numeric level of this item's status.
        
        Returns:
            Numeric status level (higher is more complete)
        """
        return STATUS_HIERARCHY.get(self.status, 0)
    
    def get_status_emoji(self) -> str:
        """Get the emoji for this item's status.
        
        Returns:
            Emoji representing the status
        """
        return STATUS_EMOJI.get(self.status, "")
    
    def __str__(self) -> str:
        """Get string representation of this item.
        
        Returns:
            String representation
        """
        return f"{self.item_id} - {self.title} ({self.status})"


class RoadmapSynchronizer:
    """Synchronizes statuses between main and local roadmaps."""
    
    def __init__(self, base_path: str):
        """Initialize the roadmap synchronizer.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = Path(base_path)
        self.main_roadmap_path = self.base_path / "ROADMAP.md"
        self.epics = {}  # id -> RoadmapItem
        self.stories = {}  # id -> RoadmapItem
        self.parent_child_map = defaultdict(list)  # parent_id -> [child_id, ...]
        self.child_parent_map = {}  # child_id -> parent_id
        self.roadmap_files = []
        self.issues = []
        
    def scan_roadmaps(self) -> None:
        """Scan all roadmap files in the project."""
        logger.info("Scanning for roadmap files...")
        
        # Find all roadmap files
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.lower() == "roadmap.md":
                    roadmap_path = Path(root) / file
                    self.roadmap_files.append(roadmap_path)
        
        logger.info(f"Found {len(self.roadmap_files)} roadmap files")
        
        # Process main roadmap first
        if self.main_roadmap_path in self.roadmap_files:
            self._process_roadmap(self.main_roadmap_path)
            self.roadmap_files.remove(self.main_roadmap_path)
        
        # Process remaining roadmaps
        for roadmap_path in self.roadmap_files:
            self._process_roadmap(roadmap_path)
        
        # Build parent-child relationships
        self._build_relationships()
        
        logger.info(f"Processed {len(self.epics)} epics and {len(self.stories)} stories")
    
    def _process_roadmap(self, roadmap_path: Path) -> None:
        """Process a single roadmap file.
        
        Args:
            roadmap_path: Path to the roadmap file
        """
        try:
            with open(roadmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            is_main_roadmap = roadmap_path == self.main_roadmap_path
            
            # Find epics and stories
            for i, line in enumerate(lines):
                if is_main_roadmap:
                    # Look for epics in main roadmap
                    epic_match = re.search(EPIC_PATTERN, line)
                    if epic_match:
                        epic_id = epic_match.group('id')
                        epic_title = epic_match.group('title')
                        
                        # Find status
                        status = "backlog"  # Default status
                        for j in range(i + 1, min(i + 10, len(lines))):
                            status_match = re.search(STATUS_PATTERN, lines[j])
                            if status_match:
                                status = status_match.group('status')
                                break
                        
                        # Create epic
                        epic = RoadmapItem(epic_id, epic_title, status, str(roadmap_path), i + 1)
                        self.epics[epic_id] = epic
                        
                        # Find child tasks
                        for j in range(i + 1, min(i + 30, len(lines))):
                            child_section_match = re.search(CHILD_PATTERN, '\n'.join(lines[j:j+20]))
                            if child_section_match:
                                children_text = child_section_match.group('children')
                                for child_match in re.finditer(CHILD_ITEM_PATTERN, children_text):
                                    child_id = child_match.group('child_id')
                                    self.parent_child_map[epic_id].append(child_id)
                                break
                else:
                    # Look for stories in local roadmaps
                    story_match = re.search(STORY_PATTERN, line)
                    if story_match:
                        story_id = story_match.group('id')
                        story_title = story_match.group('title')
                        
                        # Find status and parent
                        status = "backlog"  # Default status
                        parent_id = None
                        for j in range(i + 1, min(i + 10, len(lines))):
                            status_match = re.search(STATUS_PATTERN, lines[j])
                            if status_match:
                                status = status_match.group('status')
                            
                            parent_match = re.search(PARENT_PATTERN, lines[j])
                            if parent_match:
                                parent_id = parent_match.group('parent_id')
                        
                        # Create story
                        story = RoadmapItem(story_id, story_title, status, str(roadmap_path), i + 1)
                        if parent_id:
                            story.parent_id = parent_id
                            self.child_parent_map[story_id] = parent_id
                        
                        self.stories[story_id] = story
        
        except Exception as e:
            logger.error(f"Error processing roadmap {roadmap_path}: {e}")
            self.issues.append({
                "type": "error",
                "file": str(roadmap_path),
                "message": f"Failed to process roadmap: {e}"
            })
    
    def _build_relationships(self) -> None:
        """Build parent-child relationships between epics and stories."""
        # Connect stories to epics
        for story_id, story in self.stories.items():
            if story.parent_id:
                if story.parent_id in self.epics:
                    self.epics[story.parent_id].children.append(story_id)
                else:
                    self.issues.append({
                        "type": "warning",
                        "file": story.file_path,
                        "line": story.line_number,
                        "message": f"Story {story_id} references non-existent epic {story.parent_id}"
                    })
        
        # Check for missing relationships
        for epic_id, children in self.parent_child_map.items():
            for child_id in children:
                if child_id not in self.stories:
                    self.issues.append({
                        "type": "warning",
                        "file": self.epics[epic_id].file_path if epic_id in self.epics else "unknown",
                        "line": self.epics[epic_id].line_number if epic_id in self.epics else 0,
                        "message": f"Epic {epic_id} references non-existent story {child_id}"
                    })
    
    def analyze_status_consistency(self) -> List[Dict]:
        """Analyze status consistency between epics and their stories.
        
        Returns:
            List of inconsistencies found
        """
        logger.info("Analyzing status consistency...")
        inconsistencies = []
        
        for epic_id, epic in self.epics.items():
            # Get all child stories
            child_stories = []
            for child_id in self.parent_child_map[epic_id]:
                if child_id in self.stories:
                    child_stories.append(self.stories[child_id])
            
            if not child_stories:
                continue
            
            # Determine expected epic status based on child stories
            child_statuses = [story.status for story in child_stories]
            
            # All done -> epic should be done
            if all(status == "done" for status in child_statuses):
                expected_status = "done"
            # Any blocked -> epic should be blocked
            elif any(status == "blocked" for status in child_statuses):
                expected_status = "blocked"
            # All deferred -> epic should be deferred
            elif all(status == "deferred" for status in child_statuses):
                expected_status = "deferred"
            # Any in progress -> epic should be in progress
            elif any(status == "in progress" for status in child_statuses):
                expected_status = "in progress"
            # Any in review -> epic should be in progress
            elif any(status == "review" for status in child_statuses):
                expected_status = "in progress"
            # Otherwise -> epic should be backlog
            else:
                expected_status = "backlog"
            
            # Check if epic status matches expected status
            if epic.status != expected_status:
                inconsistencies.append({
                    "type": "status_mismatch",
                    "epic_id": epic_id,
                    "epic_title": epic.title,
                    "epic_file": epic.file_path,
                    "epic_line": epic.line_number,
                    "current_status": epic.status,
                    "expected_status": expected_status,
                    "child_stories": [
                        {"id": story.item_id, "status": story.status}
                        for story in child_stories
                    ]
                })
        
        logger.info(f"Found {len(inconsistencies)} status inconsistencies")
        return inconsistencies
    
    def generate_report(self, inconsistencies: List[Dict], report_file: str) -> None:
        """Generate a report of roadmap status consistency.
        
        Args:
            inconsistencies: List of inconsistencies found
            report_file: Path to save the report
        """
        logger.info(f"Generating report: {report_file}")
        
        # Create report directory if it doesn't exist
        report_path = Path(report_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate JSON report
        json_report = {
            "timestamp": datetime.now().isoformat(),
            "roadmaps_scanned": len(self.roadmap_files) + 1,  # +1 for main roadmap
            "epics_found": len(self.epics),
            "stories_found": len(self.stories),
            "inconsistencies": inconsistencies,
            "issues": self.issues
        }
        
        with open(f"{report_file}.json", 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        
        # Generate Markdown report
        with open(f"{report_file}.md", 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Roadmap Synchronization Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Roadmaps Scanned: {len(self.roadmap_files) + 1}\n")
            f.write(f"- Epics Found: {len(self.epics)}\n")
            f.write(f"- Stories Found: {len(self.stories)}\n")
            f.write(f"- Status Inconsistencies: {len(inconsistencies)}\n")
            f.write(f"- Issues Found: {len(self.issues)}\n\n")
            
            if inconsistencies:
                f.write("## Status Inconsistencies\n\n")
                f.write("| Epic ID | Current Status | Expected Status | Child Stories |\n")
                f.write("|---------|----------------|-----------------|---------------|\n")
                
                for inconsistency in inconsistencies:
                    epic_id = inconsistency["epic_id"]
                    current_status = inconsistency["current_status"]
                    expected_status = inconsistency["expected_status"]
                    child_stories = ", ".join([story["id"] for story in inconsistency["child_stories"]])
                    
                    f.write(f"| {epic_id} | {current_status} | {expected_status} | {child_stories} |\n")
                
                f.write("\n")
            
            if self.issues:
                f.write("## Issues\n\n")
                f.write("| Type | File | Line | Message |\n")
                f.write("|------|------|------|--------|\n")
                
                for issue in self.issues:
                    issue_type = issue["type"]
                    file_path = issue.get("file", "")
                    line = issue.get("line", "")
                    message = issue["message"]
                    
                    f.write(f"| {issue_type} | {file_path} | {line} | {message} |\n")
                
                f.write("\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review and resolve status inconsistencies\n")
            f.write("2. Fix missing or incorrect parent-child relationships\n")
            f.write("3. Update roadmap files as needed\n")
            
            f.write("\n## Related Documents\n\n")
            f.write("- <!-- TO_BE_REPLACED -->\n")
            f.write("- <!-- TO_BE_REPLACED -->\n")
            f.write("- <!-- TO_BE_REPLACED -->\n")
        
        logger.info(f"Reports generated: {report_file}.json and {report_file}.md")
    
    def update_roadmaps(self, inconsistencies: List[Dict]) -> None:
        """Update roadmap files to fix status inconsistencies.
        
        Args:
            inconsistencies: List of inconsistencies to fix
        """
        logger.info("Updating roadmap files...")
        
        # Group inconsistencies by file
        file_updates = defaultdict(list)
        for inconsistency in inconsistencies:
            file_path = inconsistency["epic_file"]
            file_updates[file_path].append({
                "line": inconsistency["epic_line"],
                "epic_id": inconsistency["epic_id"],
                "current_status": inconsistency["current_status"],
                "expected_status": inconsistency["expected_status"]
            })
        
        # Update each file
        for file_path, updates in file_updates.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Sort updates by line number (descending) to avoid line number changes
                updates.sort(key=lambda u: u["line"], reverse=True)
                
                for update in updates:
                    line_num = update["line"]
                    current_status = update["current_status"]
                    expected_status = update["expected_status"]
                    epic_id = update["epic_id"]
                    
                    # Find the status line
                    for i in range(line_num, min(line_num + 10, len(lines))):
                        if "**Status:**" in lines[i]:
                            # Update the status
                            current_line = lines[i]
                            updated_line = re.sub(
                                r'\*\*Status:\*\*\s+.*',
                                f'**Status:** {STATUS_EMOJI.get(expected_status, "")} {expected_status.title()}',
                                current_line
                            )
                            lines[i] = updated_line
                            logger.info(f"Updated status for {epic_id} in {file_path}: {current_status} -> {expected_status}")
                            break
                
                # Write the updated file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                logger.info(f"Updated file: {file_path}")
            
            except Exception as e:
                logger.error(f"Error updating file {file_path}: {e}")
                self.issues.append({
                    "type": "error",
                    "file": file_path,
                    "message": f"Failed to update file: {e}"
                })


def main():
    """Main entry point for the roadmap synchronization tool."""
    parser = argparse.ArgumentParser(
        description="Synchronize statuses between main and local roadmaps"
    )
    parser.add_argument(
        "--base-path", "-b", default=".",
        help="Base path of the EGOS project (default: current directory)"
    )
    parser.add_argument(
        "--update", "-u", action="store_true",
        help="Update roadmap files to fix inconsistencies"
    )
    parser.add_argument(
        "--report-file", "-r", default="reports/roadmap/sync_report",
        help="Path to save the report (without extension)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create synchronizer
        synchronizer = RoadmapSynchronizer(args.base_path)
        
        # Scan roadmaps
        synchronizer.scan_roadmaps()
        
        # Analyze status consistency
        inconsistencies = synchronizer.analyze_status_consistency()
        
        # Generate report
        report_path = os.path.join(args.base_path, args.report_file)
        synchronizer.generate_report(inconsistencies, report_path)
        
        # Update roadmaps if requested
        if args.update and inconsistencies:
            synchronizer.update_roadmaps(inconsistencies)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())