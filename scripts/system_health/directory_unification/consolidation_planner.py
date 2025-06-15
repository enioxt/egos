#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Consolidation Planner Module for Directory Unification Tool

This module analyzes content discovery and cross-reference data to create a
comprehensive consolidation plan. It identifies optimal target locations for
files, evaluates context and relationships, and prepares a detailed migration
plan with user decision points.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
    - C:\EGOS\scripts\cross_reference\validation\cross_reference_validator.py
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Standard library imports
import os
import re
import sys
import json
import logging
import datetime
import math
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional, Union
from collections import defaultdict, Counter

# Third-party imports
try:
    from colorama import Fore, Style, init
    init()  # Initialize colorama
except ImportError:
    # Define dummy colorama classes if not available
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()

# Local imports
from .utils import setup_logger, print_banner, Timer, json_serialize, EGOSJSONEncoder

# Constants
CONFIG = {
    "MIN_CONTEXT_SCORE": 0.5,
    "MIN_REFERENCE_SCORE": 0.3,
    "MAX_ORPHANED_FILES_PERCENTAGE": 0.2,
    "DECISION_THRESHOLDS": {
        "automatic": 0.8,  # Score above which consolidation can be automatic
        "suggested": 0.5,  # Score above which consolidation is suggested but needs approval
        "manual": 0.3      # Score above which consolidation is possible but needs manual review
    },
    "TARGET_DIRECTORY_PATTERNS": {
        "dashboard": [
            r"dashboard[s]?",
            r"monitoring",
            r"visualization",
            r"metrics",
            r"analytics"
        ],
        "documentation": [
            r"docs?",
            r"documentation",
            r"manual[s]?",
            r"guide[s]?",
            r"tutorial[s]?"
        ],
        "configuration": [
            r"config",
            r"configuration",
            r"settings",
            r"options"
        ],
        "utilities": [
            r"utils?",
            r"utilities",
            r"helpers?",
            r"common",
            r"shared"
        ]
    }
}


class ConsolidationPlanner:
    """
    Class for planning the consolidation of related files based on content
    discovery and cross-reference analysis.
    """
    
    def __init__(self, args: Dict[str, Any], context: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the ConsolidationPlanner class.
        
        Args:
            args: Command line arguments or configuration
            context: Context data from previous modules
            logger: Logger instance
        """
        self.args = args
        self.context = context
        self.logger = logger
        self.egos_root = Path(args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))))
        
        # Ensure content discovery and cross-reference analysis data are available
        if "content" not in context or not context["content"]:
            raise ValueError("Content discovery data is required for consolidation planning")
        
        if "references" not in context or not context["references"]:
            raise ValueError("Cross-reference analysis data is required for consolidation planning")
        
        # Extract data from context
        self.files = context["content"].get("files", [])
        self.directories = context["content"].get("directories", [])
        self.inbound_references = context["references"].get("inbound_references", {})
        self.outbound_references = context["references"].get("outbound_references", {})
        
        # Initialize context analysis data if available
        self.context_scores = {}
        self.functional_groups = {}
        if "context_analysis" in context and context["context_analysis"]:
            self.context_scores = context["context_analysis"].get("context_scores", {})
            self.functional_groups = context["context_analysis"].get("functional_groups", {})
        
        # Initialize consolidation plan
        self.consolidation_plan = {
            "target_directory": None,
            "file_decisions": {},
            "directory_structure": {},
            "migration_steps": [],
            "user_decision_points": [],
            "stats": {
                "total_files": len(self.files),
                "files_to_consolidate": 0,
                "files_to_leave": 0,
                "automatic_decisions": 0,
                "suggested_decisions": 0,
                "manual_decisions": 0
            }
        }
        
        # Initialize keyword from args
        self.keyword = args.get("keyword", "")
        
        # Initialize target type based on keyword
        self.target_type = self._determine_target_type(self.keyword)
    
    def create_plan(self) -> Dict[str, Any]:
        """
        Create a consolidation plan based on content discovery and cross-reference analysis.
        
        Returns:
            Dictionary with consolidation plan
        """
        self.logger.info("Creating consolidation plan")
        
        # Start timer
        timer = Timer("Consolidation Planning")
        timer.start()
        
        try:
            # Determine optimal target location
            self._determine_target_location()
            
            # Analyze file relationships
            self._analyze_file_relationships()
            
            # Create directory structure
            self._create_directory_structure()
            
            # Generate migration steps
            self._generate_migration_steps()
            
            # Identify user decision points
            self._identify_user_decision_points()
            
            # Update statistics
            self._update_statistics()
            
            # Log completion
            elapsed_time = timer.stop()
            self.logger.info(f"Consolidation plan created in {elapsed_time:.2f} seconds")
            
            return self.consolidation_plan
            
        except Exception as e:
            elapsed_time = timer.stop()
            self.logger.error(f"Consolidation planning failed after {elapsed_time:.2f} seconds: {e}")
            raise
    
    def _determine_target_type(self, keyword: str) -> str:
        """
        Determine the target type based on the keyword.
        
        Args:
            keyword: The search keyword
            
        Returns:
            Target type (dashboard, documentation, configuration, utilities, or generic)
        """
        if not keyword:
            return "generic"
        
        keyword_lower = keyword.lower()
        
        for target_type, patterns in CONFIG["TARGET_DIRECTORY_PATTERNS"].items():
            for pattern in patterns:
                if re.search(pattern, keyword_lower):
                    return target_type
        
        return "generic"
    
    def _determine_target_location(self) -> None:
        """
        Determine the optimal target location for consolidated content.
        """
        self.logger.info("Determining optimal target location")
        
        # Get existing directories that match the target type
        matching_dirs = []
        for dir_info in self.directories:
            dir_path = dir_info["full_path"]
            dir_name = dir_info["name"].lower()
            
            # Check if directory name matches target type patterns
            if self.target_type != "generic":
                for pattern in CONFIG["TARGET_DIRECTORY_PATTERNS"].get(self.target_type, []):
                    if re.search(pattern, dir_name):
                        matching_dirs.append(dir_path)
                        break
        
        # Find the directory with the most references to/from our files
        best_dir = None
        best_score = 0
        
        for dir_path in matching_dirs:
            # Count references to/from files in this directory
            ref_score = 0
            
            for file_info in self.files:
                file_path = file_info["full_path"]
                
                # Check if file is in this directory
                if os.path.dirname(file_path) == dir_path:
                    continue  # Skip files already in this directory
                
                # Count inbound references from files in this directory
                for ref in self.inbound_references.get(file_path, []):
                    if os.path.dirname(ref["source_file"]) == dir_path:
                        ref_score += 1
                
                # Count outbound references to files in this directory
                for ref in self.outbound_references.get(file_path, []):
                    if os.path.dirname(ref["target_file"]) == dir_path:
                        ref_score += 1
            
            if ref_score > best_score:
                best_score = ref_score
                best_dir = dir_path
        
        # If no suitable directory found, create a new one
        if not best_dir:
            if self.target_type != "generic":
                # Create a new directory based on target type
                new_dir = os.path.join(str(self.egos_root), self.target_type)
                
                # Append keyword if provided
                if self.keyword:
                    new_dir = os.path.join(new_dir, self.keyword)
                
                best_dir = new_dir
            else:
                # For generic type, create a directory based on keyword
                if self.keyword:
                    best_dir = os.path.join(str(self.egos_root), self.keyword)
                else:
                    # Fallback to a consolidated directory
                    best_dir = os.path.join(str(self.egos_root), "consolidated")
        
        self.consolidation_plan["target_directory"] = best_dir
        self.logger.info(f"Selected target directory: {best_dir}")
    
    def _analyze_file_relationships(self) -> None:
        """
        Analyze relationships between files to determine which should be consolidated.
        """
        self.logger.info("Analyzing file relationships")
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Skip files already in the target directory
            if os.path.dirname(file_path) == self.consolidation_plan["target_directory"]:
                self.consolidation_plan["file_decisions"][file_path] = {
                    "decision": "leave",
                    "reason": "Already in target directory",
                    "score": 1.0,
                    "confidence": "high"
                }
                continue
            
            # Calculate consolidation score
            score = self._calculate_consolidation_score(file_path)
            
            # Determine decision based on score
            if score >= CONFIG["DECISION_THRESHOLDS"]["automatic"]:
                decision = "consolidate"
                confidence = "high"
                reason = "Strong relationship with other files"
            elif score >= CONFIG["DECISION_THRESHOLDS"]["suggested"]:
                decision = "suggest_consolidate"
                confidence = "medium"
                reason = "Moderate relationship with other files"
            elif score >= CONFIG["DECISION_THRESHOLDS"]["manual"]:
                decision = "review"
                confidence = "low"
                reason = "Weak relationship with other files"
            else:
                decision = "leave"
                confidence = "high"
                reason = "No significant relationship with other files"
            
            # Store decision
            self.consolidation_plan["file_decisions"][file_path] = {
                "decision": decision,
                "reason": reason,
                "score": score,
                "confidence": confidence,
                "target_path": os.path.join(
                    self.consolidation_plan["target_directory"],
                    os.path.basename(file_path)
                )
            }
    
    def _calculate_consolidation_score(self, file_path: str) -> float:
        """
        Calculate a score indicating how strongly a file should be consolidated.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Consolidation score (0.0 to 1.0)
        """
        # Initialize score components
        reference_score = 0.0
        context_score = 0.0
        functional_score = 0.0
        name_score = 0.0
        
        # Reference score (0.0 to 0.4)
        # Count references to/from files that are candidates for consolidation
        inbound_count = 0
        outbound_count = 0
        
        for ref in self.inbound_references.get(file_path, []):
            source_dir = os.path.dirname(ref["source_file"])
            if source_dir != os.path.dirname(file_path):
                inbound_count += 1
        
        for ref in self.outbound_references.get(file_path, []):
            target_dir = os.path.dirname(ref["target_file"])
            if target_dir != os.path.dirname(file_path):
                outbound_count += 1
        
        reference_score = min(0.4, (inbound_count + outbound_count) * 0.05)
        
        # Context score (0.0 to 0.3)
        if file_path in self.context_scores:
            context_score = min(0.3, self.context_scores[file_path].get("total", 0.0))
        
        # Functional score (0.0 to 0.2)
        # Check if file is part of a functional group with other files
        for group_id, files in self.functional_groups.items():
            if file_path in files:
                # Calculate percentage of files in the group that are candidates
                group_size = len(files)
                candidates = 0
                for other_file in files:
                    if other_file != file_path:
                        candidates += 1
                
                if group_size > 1:
                    functional_score = min(0.2, (candidates / (group_size - 1)) * 0.2)
                break
        
        # Name score (0.0 to 0.1)
        # Check if filename matches keyword or target type
        file_name = os.path.basename(file_path).lower()
        
        if self.keyword and self.keyword.lower() in file_name:
            name_score += 0.05
        
        if self.target_type != "generic":
            for pattern in CONFIG["TARGET_DIRECTORY_PATTERNS"].get(self.target_type, []):
                if re.search(pattern, file_name):
                    name_score += 0.05
                    break
        
        # Calculate total score
        total_score = reference_score + context_score + functional_score + name_score
        
        return min(total_score, 1.0)
    
    def _create_directory_structure(self) -> None:
        """
        Create a recommended directory structure for the consolidated content.
        """
        self.logger.info("Creating recommended directory structure")
        
        # Initialize directory structure with target directory
        target_dir = self.consolidation_plan["target_directory"]
        self.consolidation_plan["directory_structure"] = {
            "path": target_dir,
            "type": "directory",
            "children": []
        }
        
        # Group files by subdirectory based on relationships
        subdirectories = defaultdict(list)
        
        # First pass: identify functional groups
        for group_id, files in self.functional_groups.items():
            # Skip small groups
            if len(files) < 3:
                continue
            
            # Determine a suitable subdirectory name based on common file prefixes
            prefixes = []
            for file_path in files:
                file_name = os.path.basename(file_path)
                # Extract prefix (before first underscore or dot)
                match = re.match(r'^([a-zA-Z0-9]+)[_\.]', file_name)
                if match:
                    prefixes.append(match.group(1).lower())
            
            # Get most common prefix
            if prefixes:
                counter = Counter(prefixes)
                common_prefix = counter.most_common(1)[0][0]
                
                # Create subdirectory name
                subdir_name = f"{common_prefix}"
                
                # Add files to this subdirectory
                for file_path in files:
                    decision = self.consolidation_plan["file_decisions"].get(file_path, {})
                    if decision.get("decision") in ["consolidate", "suggest_consolidate"]:
                        subdirectories[subdir_name].append(file_path)
                        
                        # Update target path
                        new_target = os.path.join(
                            target_dir,
                            subdir_name,
                            os.path.basename(file_path)
                        )
                        self.consolidation_plan["file_decisions"][file_path]["target_path"] = new_target
        
        # Second pass: handle remaining files
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] in ["consolidate", "suggest_consolidate"]:
                # Check if file is already assigned to a subdirectory
                assigned = False
                for subdir, files in subdirectories.items():
                    if file_path in files:
                        assigned = True
                        break
                
                if not assigned:
                    # Add to root of target directory
                    subdirectories[""].append(file_path)
        
        # Build directory structure
        for subdir, files in subdirectories.items():
            if subdir:
                # Add subdirectory
                subdir_node = {
                    "path": os.path.join(target_dir, subdir),
                    "type": "directory",
                    "children": []
                }
                
                # Add files to subdirectory
                for file_path in files:
                    file_node = {
                        "path": file_path,
                        "type": "file",
                        "target_path": self.consolidation_plan["file_decisions"][file_path]["target_path"]
                    }
                    subdir_node["children"].append(file_node)
                
                self.consolidation_plan["directory_structure"]["children"].append(subdir_node)
            else:
                # Add files directly to target directory
                for file_path in files:
                    file_node = {
                        "path": file_path,
                        "type": "file",
                        "target_path": self.consolidation_plan["file_decisions"][file_path]["target_path"]
                    }
                    self.consolidation_plan["directory_structure"]["children"].append(file_node)
    
    def _generate_migration_steps(self) -> None:
        """
        Generate steps for migrating files to the consolidated structure.
        """
        self.logger.info("Generating migration steps")
        
        # Initialize migration steps
        migration_steps = []
        
        # Step 1: Create target directory structure
        directories_to_create = set()
        directories_to_create.add(self.consolidation_plan["target_directory"])
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] in ["consolidate", "suggest_consolidate"]:
                target_dir = os.path.dirname(decision["target_path"])
                directories_to_create.add(target_dir)
        
        migration_steps.append({
            "step": "create_directories",
            "description": "Create target directory structure",
            "directories": sorted(list(directories_to_create))
        })
        
        # Step 2: Copy files to target locations
        files_to_copy = []
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] in ["consolidate", "suggest_consolidate"]:
                files_to_copy.append({
                    "source": file_path,
                    "target": decision["target_path"],
                    "confidence": decision["confidence"]
                })
        
        migration_steps.append({
            "step": "copy_files",
            "description": "Copy files to target locations",
            "files": files_to_copy
        })
        
        # Step 3: Update references in files
        references_to_update = []
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] in ["consolidate", "suggest_consolidate"]:
                # Find all files that reference this file
                for ref_source in self.inbound_references.get(file_path, []):
                    references_to_update.append({
                        "file": ref_source["source_file"],
                        "old_reference": file_path,
                        "new_reference": decision["target_path"]
                    })
        
        migration_steps.append({
            "step": "update_references",
            "description": "Update references in files",
            "references": references_to_update
        })
        
        # Step 4: Validate consolidated structure
        migration_steps.append({
            "step": "validate",
            "description": "Validate consolidated structure",
            "validation_checks": [
                "Check that all files were copied correctly",
                "Verify that all references were updated correctly",
                "Ensure no functionality was broken"
            ]
        })
        
        # Step 5: Remove original files (optional)
        files_to_remove = []
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] == "consolidate":  # Only automatic decisions
                files_to_remove.append(file_path)
        
        migration_steps.append({
            "step": "remove_originals",
            "description": "Remove original files (optional)",
            "files": files_to_remove,
            "optional": True
        })
        
        self.consolidation_plan["migration_steps"] = migration_steps
    
    def _identify_user_decision_points(self) -> None:
        """
        Identify points where user decisions are required.
        """
        self.logger.info("Identifying user decision points")
        
        # Decision point 1: Confirm target directory
        self.consolidation_plan["user_decision_points"].append({
            "id": "target_directory",
            "description": "Confirm target directory for consolidation",
            "current_value": self.consolidation_plan["target_directory"],
            "options": [
                self.consolidation_plan["target_directory"],
                # Add alternative options here if available
            ],
            "required": True
        })
        
        # Decision point 2: Review files marked for manual review
        review_files = []
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] == "review":
                review_files.append({
                    "file_path": file_path,
                    "score": decision["score"],
                    "reason": decision["reason"],
                    "target_path": decision["target_path"]
                })
        
        if review_files:
            self.consolidation_plan["user_decision_points"].append({
                "id": "review_files",
                "description": "Review files with uncertain consolidation status",
                "files": review_files,
                "required": True
            })
        
        # Decision point 3: Confirm suggested consolidations
        suggested_files = []
        
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] == "suggest_consolidate":
                suggested_files.append({
                    "file_path": file_path,
                    "score": decision["score"],
                    "reason": decision["reason"],
                    "target_path": decision["target_path"]
                })
        
        if suggested_files:
            self.consolidation_plan["user_decision_points"].append({
                "id": "confirm_suggestions",
                "description": "Confirm suggested file consolidations",
                "files": suggested_files,
                "required": True
            })
        
        # Decision point 4: Confirm removal of original files
        if self.consolidation_plan["migration_steps"][-1]["files"]:
            self.consolidation_plan["user_decision_points"].append({
                "id": "confirm_removal",
                "description": "Confirm removal of original files after consolidation",
                "files": self.consolidation_plan["migration_steps"][-1]["files"],
                "required": False,
                "default": False
            })
    
    def _update_statistics(self) -> None:
        """
        Update statistics based on consolidation decisions.
        """
        # Reset counters
        stats = self.consolidation_plan["stats"]
        stats["files_to_consolidate"] = 0
        stats["files_to_leave"] = 0
        stats["automatic_decisions"] = 0
        stats["suggested_decisions"] = 0
        stats["manual_decisions"] = 0
        
        # Count decisions
        for file_path, decision in self.consolidation_plan["file_decisions"].items():
            if decision["decision"] == "consolidate":
                stats["files_to_consolidate"] += 1
                stats["automatic_decisions"] += 1
            elif decision["decision"] == "suggest_consolidate":
                stats["files_to_consolidate"] += 1
                stats["suggested_decisions"] += 1
            elif decision["decision"] == "review":
                stats["manual_decisions"] += 1
            elif decision["decision"] == "leave":
                stats["files_to_leave"] += 1
                stats["automatic_decisions"] += 1


def main():
    """Main function for testing the ConsolidationPlanner module."""
    import argparse
    import json
    
    # Print banner
    print_banner("Consolidation Planner Module")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Consolidation Planner Module for Directory Unification Tool")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    parser.add_argument("--content-file", required=True, help="Path to content discovery JSON file")
    parser.add_argument("--references-file", required=True, help="Path to cross-reference analysis JSON file")
    parser.add_argument("--context-file", help="Path to context analysis JSON file")
    parser.add_argument("--output", help="Output file for consolidation plan (JSON format)")
    parser.add_argument("--keyword", help="Keyword for content discovery")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Load content discovery data
    with open(args.content_file, "r", encoding="utf-8") as f:
        content_data = json.load(f)
    
    # Load cross-reference analysis data
    with open(args.references_file, "r", encoding="utf-8") as f:
        references_data = json.load(f)
    
    # Load context analysis data if available
    context_data = None
    if args.context_file:
        with open(args.context_file, "r", encoding="utf-8") as f:
            context_data = json.load(f)
    
    # Create context
    context = {
        "content": content_data,
        "references": references_data
    }
    
    if context_data:
        context["context_analysis"] = context_data
    
    # Set up logger
    logger = setup_logger("consolidation_planner", "%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging.DEBUG if args.verbose else logging.INFO)
    
    # Create ConsolidationPlanner instance
    planner = ConsolidationPlanner(args_dict, context, logger)
    
    # Create consolidation plan
    plan = planner.create_plan()
    
    # Display summary
    print(f"\n{Fore.CYAN}Consolidation Plan Summary:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Target directory:{Style.RESET_ALL} {plan['target_directory']}")
    print(f"  {Fore.GREEN}Files to consolidate:{Style.RESET_ALL} {plan['stats']['files_to_consolidate']}")
    print(f"  {Fore.GREEN}Files to leave in place:{Style.RESET_ALL} {plan['stats']['files_to_leave']}")
    print(f"  {Fore.GREEN}Automatic decisions:{Style.RESET_ALL} {plan['stats']['automatic_decisions']}")
    print(f"  {Fore.GREEN}Suggested decisions:{Style.RESET_ALL} {plan['stats']['suggested_decisions']}")
    print(f"  {Fore.GREEN}Manual decisions:{Style.RESET_ALL} {plan['stats']['manual_decisions']}")
    
    # Output plan to file if specified
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, default=json_serialize)
        
        print(f"\n{Fore.GREEN}Consolidation plan saved to {args.output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    main()