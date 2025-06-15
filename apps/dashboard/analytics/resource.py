#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""diagnostic_analytics_resource.py

Resource allocation component for the EGOS Diagnostic Analytics module.
Provides tools for optimizing resource allocation and scheduling for diagnostic issues.

@module: DIAG-AN-RES
@author: EGOS Team
@version: 1.0.0
@date: 2025-05-04
@status: development

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Related Components:
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Data source
  - [diagnostic_analytics_preprocessor.py](mdc:./diagnostic_analytics_preprocessor.py) - Data preprocessing
  - [diagnostic_analytics_models.py](mdc:./diagnostic_analytics_models.py) - Predictive models
  - [diagnostic_analytics_timeseries.py](mdc:./diagnostic_analytics_timeseries.py) - Time series analysis
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticAnalytics.Resource")


class ResourceAllocator:
    """Allocates resources and optimizes remediation schedules.
    
    This class provides methods for prioritizing issues, calculating optimal 
    resource allocation, and generating schedules based on weights and constraints.
    
    Attributes:
        priority_weights: Dictionary mapping priority levels to weight values
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the resource allocator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.logger = logger.getChild("ResourceAllocator")
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Create default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "priority_weights": {
                "critical": 10.0,
                "high": 5.0,
                "medium": 2.0,
                "low": 1.0,
                "enhancement": 0.5
            },
            "age_factor": {
                "enabled": True,
                "base_days": 30,  # Days to consider as baseline
                "max_factor": 3.0  # Maximum multiplier for age
            },
            "status_weights": {
                "in_progress": 1.5,  # Higher to avoid context switching
                "reviewing": 1.2,
                "identified": 1.0,
                "deferred": 0.5
            }
        }
    
    def calculate_issue_weights(self, issues: List[Dict[str, Any]],
                              risk_scores: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Calculate weights for issues based on priority, age, and risk.
        
        Args:
            issues: List of issue dictionaries
            risk_scores: Optional dictionary mapping issue IDs to risk scores
            
        Returns:
            Dictionary mapping issue IDs to weights
        """
        weights = {}
        
        # Extract configuration
        priority_weights = self.config["priority_weights"]
        age_factor = self.config["age_factor"]
        status_weights = self.config["status_weights"]
        
        self.logger.info(f"Calculating weights for {len(issues)} issues")
        
        # Calculate weights for each issue
        for issue in issues:
            issue_id = issue.get("id")
            if not issue_id:
                continue
                
            # Base weight from priority
            priority = issue.get("priority", "medium").lower()
            weight = priority_weights.get(priority, 2.0)
            
            # Factor in age if enabled and available
            if age_factor["enabled"] and "created" in issue:
                try:
                    created = pd.to_datetime(issue["created"])
                    now = pd.Timestamp(datetime.datetime.now())
                    age_days = (now - created).days
                    
                    # Age factor increases weight for older issues
                    age_factor_value = min(
                        1.0 + (age_days / age_factor["base_days"]), 
                        age_factor["max_factor"]
                    )
                    weight *= age_factor_value
                except Exception as e:
                    self.logger.warning(f"Error calculating age factor: {e}")
            
            # Factor in status if available
            status = issue.get("status", "identified").lower()
            status_factor = status_weights.get(status, 1.0)
            weight *= status_factor
            
            # Factor in risk score if available
            if risk_scores and issue_id in risk_scores:
                risk_score = risk_scores[issue_id]
                weight *= (1.0 + risk_score)
            
            weights[issue_id] = weight
        
        return weights
    
    def optimize_schedule(self, issues: List[Dict[str, Any]], 
                        available_resources: int = 1,
                        time_estimate_fn: Optional[Callable] = None,
                        risk_scores: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Optimize remediation schedule based on weights and available resources.
        
        Args:
            issues: List of issue dictionaries
            available_resources: Number of available resources
            time_estimate_fn: Optional function to estimate time per issue
            risk_scores: Optional dictionary mapping issue IDs to risk scores
            
        Returns:
            Dictionary with optimized schedule
        """
        self.logger.info(f"Optimizing schedule for {len(issues)} issues with {available_resources} resources")
        
        # Calculate weights
        weights = self.calculate_issue_weights(issues, risk_scores)
        
        # Sort issues by weight (descending)
        sorted_issues = sorted(
            issues, 
            key=lambda x: weights.get(x.get("id", ""), 0.0),
            reverse=True
        )
        
        # Initialize assignments
        assignments = {}
        for i in range(available_resources):
            assignments[f"resource_{i+1}"] = []
        
        # Check if we have time estimates
        if time_estimate_fn:
            # Use load balancing algorithm
            resource_loads = {r: 0 for r in assignments.keys()}
            
            for issue in sorted_issues:
                # Find resource with lowest current load
                resource = min(resource_loads, key=resource_loads.get)
                
                # Assign issue
                assignments[resource].append(issue)
                
                # Update load
                try:
                    time_estimate = time_estimate_fn(issue)
                    resource_loads[resource] += time_estimate
                except Exception:
                    # Default time estimate
                    resource_loads[resource] += 1
        else:
            # Use simple round-robin
            for i, issue in enumerate(sorted_issues):
                resource_idx = i % available_resources
                resource_key = f"resource_{resource_idx+1}"
                assignments[resource_key].append(issue)
        
        # Create schedule with timing information
        schedule = {}
        if time_estimate_fn:
            current_times = {res: 0 for res in assignments.keys()}
            
            for resource, resource_issues in assignments.items():
                schedule[resource] = []
                
                for issue in resource_issues:
                    try:
                        est_time = time_estimate_fn(issue)
                    except Exception:
                        est_time = 1  # Default
                    
                    start_time = current_times[resource]
                    end_time = start_time + est_time
                    
                    schedule[resource].append({
                        "issue": issue,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": est_time,
                        "weight": weights.get(issue.get("id", ""), 0)
                    })
                    
                    current_times[resource] = end_time
        
        return {
            "weights": weights,
            "assignments": assignments,
            "schedule": schedule
        }
    
    def visualize_schedule(self, schedule: Dict[str, List[Dict[str, Any]]],
                         title: str = "Remediation Schedule") -> go.Figure:
        """Create a Gantt chart visualization of the schedule.
        
        Args:
            schedule: Schedule dictionary from optimize_schedule
            title: Plot title
            
        Returns:
            Plotly Figure with Gantt chart
        """
        if not schedule:
            self.logger.warning("Empty schedule, cannot visualize")
            return go.Figure()
        
        # Prepare data for Gantt chart
        tasks = []
        
        for resource, resource_schedule in schedule.items():
            for item in resource_schedule:
                issue = item.get("issue", {})
                
                # Get issue details
                issue_id = issue.get("id", "Unknown")
                title = issue.get("title", f"Issue {issue_id}")
                priority = issue.get("priority", "medium")
                
                # Add to tasks
                tasks.append({
                    "Task": issue_id,
                    "Resource": resource,
                    "Start": item.get("start_time", 0),
                    "Finish": item.get("end_time", 0),
                    "Priority": priority,
                    "Description": title,
                    "Weight": item.get("weight", 0.0)
                })
        
        # Create DataFrame
        df = pd.DataFrame(tasks)
        
        if df.empty:
            self.logger.warning("No tasks in schedule")
            return go.Figure()
        
        try:
            # Create Gantt chart
            fig = px.timeline(
                df, 
                x_start="Start", 
                x_end="Finish", 
                y="Task",
                color="Priority",
                hover_data=["Description", "Weight"],
                title=title
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Time Units",
                yaxis_title="Issue ID",
                height=max(400, 100 + 20 * len(df))
            )
            
            return fig
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
            return go.Figure()


class PriorityManager:
    """Manages priority of diagnostic issues.
    
    This class provides methods for dynamic priority adjustment based on
    risk assessments, resolution time predictions, and business importance.
    """
    
    def __init__(self):
        """Initialize the priority manager."""
        self.logger = logger.getChild("PriorityManager")
    
    def calculate_priority_scores(self, issues: List[Dict[str, Any]],
                                risk_scores: Optional[np.ndarray] = None,
                                time_predictions: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate priority scores for issues based on multiple factors.
        
        Args:
            issues: List of issue dictionaries
            risk_scores: Optional array of risk scores (0-1 scale)
            time_predictions: Optional array of resolution time predictions
            
        Returns:
            Dictionary mapping issue IDs to priority scores
        """
        priority_scores = {}
        
        # Default weights for different factors
        risk_weight = 0.4
        time_weight = 0.3
        age_weight = 0.3
        
        # Calculate normalized time values (inverse - shorter times get higher priority)
        if time_predictions is not None and len(time_predictions) > 0:
            max_time = max(time_predictions) if max(time_predictions) > 0 else 1
            norm_times = 1.0 - (time_predictions / max_time)
        else:
            norm_times = None
        
        # Calculate priority for each issue
        for i, issue in enumerate(issues):
            issue_id = issue.get("id")
            if not issue_id:
                continue
            
            # Start with base score
            score = 0.5
            factor_count = 0
            
            # Add risk component
            if risk_scores is not None and i < len(risk_scores):
                score += risk_weight * risk_scores[i]
                factor_count += 1
            
            # Add time component (shorter times get higher priority)
            if norm_times is not None and i < len(norm_times):
                score += time_weight * norm_times[i]
                factor_count += 1
            
            # Add age component
            if "created" in issue:
                try:
                    created = pd.to_datetime(issue["created"])
                    now = pd.Timestamp(datetime.datetime.now())
                    age_days = (now - created).days
                    
                    # Normalize age (cap at 180 days)
                    norm_age = min(age_days / 180.0, 1.0)
                    score += age_weight * norm_age
                    factor_count += 1
                except Exception:
                    pass
            
            # Adjust for factor count
            if factor_count > 0:
                priority_scores[issue_id] = score / factor_count
            else:
                priority_scores[issue_id] = score
        
        return priority_scores
    
    def suggest_priority_changes(self, issues: List[Dict[str, Any]], 
                               priority_scores: Dict[str, float],
                               threshold: float = 0.2) -> List[Dict[str, Any]]:
        """Suggest priority changes based on calculated scores.
        
        Args:
            issues: List of issue dictionaries
            priority_scores: Dictionary mapping issue IDs to priority scores
            threshold: Threshold for suggesting changes
            
        Returns:
            List of suggested changes
        """
        # Map priority levels to numeric values
        priority_map = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
            "enhancement": 0.1
        }
        
        # Inverse mapping
        inv_priority_map = {v: k for k, v in priority_map.items()}
        
        suggested_changes = []
        
        for issue in issues:
            issue_id = issue.get("id")
            if not issue_id or issue_id not in priority_scores:
                continue
            
            # Get current priority
            current_priority = issue.get("priority", "medium").lower()
            current_value = priority_map.get(current_priority, 0.5)
            
            # Get calculated priority score
            score = priority_scores[issue_id]
            
            # Find closest priority level
            closest_level = min(priority_map.values(), key=lambda x: abs(x - score))
            suggested_priority = inv_priority_map[closest_level]
            
            # Check if difference is significant
            if abs(closest_level - current_value) >= threshold:
                suggested_changes.append({
                    "issue_id": issue_id,
                    "title": issue.get("title", f"Issue {issue_id}"),
                    "current_priority": current_priority,
                    "suggested_priority": suggested_priority,
                    "priority_score": score
                })
        
        return suggested_changes


# Standalone testing function
def test_resource_allocation():
    """Test the ResourceAllocator with sample data."""
    # Create sample issues
    sample_issues = [
        {
            "id": "ISSUE-1",
            "title": "Critical Bug in Core Module",
            "priority": "critical",
            "status": "in_progress",
            "created": "2025-04-01",
            "subsystem": "core"
        },
        {
            "id": "ISSUE-2",
            "title": "UI Enhancement",
            "priority": "low",
            "status": "identified",
            "created": "2025-04-15",
            "subsystem": "ui"
        },
        {
            "id": "ISSUE-3",
            "title": "Performance Optimization",
            "priority": "medium",
            "status": "identified",
            "created": "2025-04-10",
            "subsystem": "database"
        },
        {
            "id": "ISSUE-4",
            "title": "Security Vulnerability",
            "priority": "high",
            "status": "reviewing",
            "created": "2025-04-05",
            "subsystem": "security"
        }
    ]
    
    # Create time estimation function
    def estimate_time(issue):
        # Simple estimation based on priority
        priority_map = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "enhancement": 1
        }
        return priority_map.get(issue.get("priority", "medium").lower(), 3)
    
    # Test ResourceAllocator
    allocator = ResourceAllocator()
    
    # Calculate weights
    weights = allocator.calculate_issue_weights(sample_issues)
    print("Issue Weights:")
    for issue_id, weight in weights.items():
        print(f"  {issue_id}: {weight:.2f}")
    
    # Optimize schedule
    result = allocator.optimize_schedule(
        sample_issues, 
        available_resources=2,
        time_estimate_fn=estimate_time
    )
    
    print("\nAssignments:")
    for resource, issues in result["assignments"].items():
        print(f"  {resource}: {[issue['id'] for issue in issues]}")
    
    print("\nSchedule:")
    for resource, schedule in result["schedule"].items():
        print(f"  {resource}:")
        for item in schedule:
            issue = item["issue"]
            print(f"    {issue['id']}: Start={item['start_time']}, End={item['end_time']}")
    
    # Test PriorityManager
    print("\nTesting PriorityManager:")
    manager = PriorityManager()
    
    # Mock risk scores and time predictions
    risk_scores = np.array([0.8, 0.2, 0.5, 0.9])
    time_predictions = np.array([5, 2, 3, 4])
    
    # Calculate priority scores
    priority_scores = manager.calculate_priority_scores(
        sample_issues,
        risk_scores=risk_scores,
        time_predictions=time_predictions
    )
    
    print("Priority Scores:")
    for issue_id, score in priority_scores.items():
        print(f"  {issue_id}: {score:.2f}")
    
    # Suggest priority changes
    changes = manager.suggest_priority_changes(sample_issues, priority_scores)
    
    print("Suggested Priority Changes:")
    for change in changes:
        print(f"  {change['issue_id']}: {change['current_priority']} -> {change['suggested_priority']}")
    
    return True


if __name__ == "__main__":
    print("Testing ResourceAllocator and PriorityManager")
    success = test_resource_allocation()
    print(f"Test {'successful' if success else 'failed'}")