"""
EGOS Diagnostic Visualization Module

This module extends the EGOS Dashboard with interactive visualizations for diagnostic findings,
remediation tracking, and timeline management based on the comprehensive diagnostic report.

@references:
- Core References:
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [EGOS_Project_Diagnostic_Report.md](mdc:../../strategic-thinking/reports/EGOS_Project_Diagnostic_Report.md)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Union, Any
import json
import datetime
from pathlib import Path
import os
import re

# Constants
SEVERITY_COLORS = {
    "CRITICAL": "#FF4136",  # Red
    "WARNING": "#FF851B",   # Orange
    "ISSUE": "#FFDC00",     # Yellow
    "INFO": "#0074D9",      # Blue
    "POSITIVE": "#2ECC40",  # Green
}

PRIORITY_COLORS = {
    "Critical": "#FF4136",  # Red
    "High": "#FF851B",      # Orange
    "Medium": "#FFDC00",    # Yellow
    "Low": "#0074D9",       # Blue
}

# Path to diagnostic report
DIAGNOSTIC_REPORT_PATH = Path("../../strategic-thinking/reports/EGOS_Project_Diagnostic_Report.md")

class DiagnosticData:
    """Class to parse and hold diagnostic data from the EGOS Diagnostic Report."""
    
    def __init__(self, report_path: Path):
        """Initialize with path to diagnostic report.
        
        Args:
            report_path: Path to the diagnostic report markdown file
        """
        self.report_path = report_path
        self.issues: List[Dict[str, Any]] = []
        self.subsystems: List[str] = []
        self.severities: List[str] = []
        self.priorities: List[str] = []
        self.load_data()
    
    def load_data(self) -> None:
        """Load and parse diagnostic data from the report."""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract issues
            issue_pattern = r'\*\*\[([A-Z]+-[A-Z]+-\d+)\]\*\*\s+(.*?)\s+\*\*Status:\s+([A-Z]+)\*\*'
            issue_matches = re.finditer(issue_pattern, content)
            
            # Extract recommendations
            recommendation_pattern = r'\*\*\[([A-Z]+-ACTION-\d+)\]\*\*\s+(.*?)\s+\*\*Priority:\s+([A-Za-z]+)\*\*'
            recommendation_matches = re.finditer(recommendation_pattern, content)
            
            # Process issues
            for match in issue_matches:
                issue_id, description, severity = match.groups()
                subsystem = issue_id.split('-')[0]
                
                self.issues.append({
                    "id": issue_id,
                    "description": description,
                    "severity": severity,
                    "subsystem": subsystem,
                    "type": "issue"
                })
                
                if subsystem not in self.subsystems:
                    self.subsystems.append(subsystem)
                if severity not in self.severities:
                    self.severities.append(severity)
            
            # Process recommendations
            for match in recommendation_matches:
                rec_id, description, priority = match.groups()
                subsystem = rec_id.split('-')[0]
                
                self.issues.append({
                    "id": rec_id,
                    "description": description,
                    "priority": priority,
                    "subsystem": subsystem,
                    "type": "recommendation",
                    "status": "Not Started",  # Default status
                    "due_date": None,
                    "assignee": None
                })
                
                if subsystem not in self.subsystems:
                    self.subsystems.append(subsystem)
                if priority not in self.priorities:
                    self.priorities.append(priority)
            
            # Create empty tracking file if it doesn't exist
            tracking_file = Path("diagnostic_tracking.json")
            if not tracking_file.exists():
                self.save_tracking_data({
                    "last_updated": datetime.datetime.now().isoformat(),
                    "issues": self.issues
                })
            else:
                # Update from tracking file
                self.load_tracking_data()
                
        except Exception as e:
            st.error(f"Error loading diagnostic data: {e}")
            self.issues = []
    
    def save_tracking_data(self, data: Dict[str, Any]) -> None:
        """Save tracking data to JSON file.
        
        Args:
            data: Dictionary containing tracking data
        """
        try:
            with open("diagnostic_tracking.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving tracking data: {e}")
    
    def load_tracking_data(self) -> None:
        """Load tracking data from JSON file and update issues."""
        try:
            with open("diagnostic_tracking.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Update issues with tracking data
            tracked_issues = {issue["id"]: issue for issue in data.get("issues", [])}
            
            for i, issue in enumerate(self.issues):
                if issue["id"] in tracked_issues:
                    # Update with tracked data while preserving original data
                    tracked_issue = tracked_issues[issue["id"]]
                    for key, value in tracked_issue.items():
                        if key not in ["id", "description", "subsystem"]:
                            issue[key] = value
            
        except Exception as e:
            st.error(f"Error loading tracking data: {e}")

    def update_issue(self, issue_id: str, updates: Dict[str, Any]) -> None:
        """Update an issue with new data and save to tracking file.
        
        Args:
            issue_id: ID of the issue to update
            updates: Dictionary of fields to update
        """
        for i, issue in enumerate(self.issues):
            if issue["id"] == issue_id:
                for key, value in updates.items():
                    self.issues[i][key] = value
                break
        
        # Save updated data
        self.save_tracking_data({
            "last_updated": datetime.datetime.now().isoformat(),
            "issues": self.issues
        })

def display_dashboard(diagnostic_data: DiagnosticData) -> None:
    """Main function to display the diagnostic dashboard.
    
    Args:
        diagnostic_data: Loaded diagnostic data
    """
    st.title("EGOS Diagnostic Dashboard")
    
    tabs = st.tabs(["Overview", "Remediation Timeline", "Issue Tracking", "Subsystem Analysis"])
    
    with tabs[0]:
        display_overview(diagnostic_data)
    
    with tabs[1]:
        display_remediation_timeline(diagnostic_data)
    
    with tabs[2]:
        display_issue_tracking(diagnostic_data)
    
    with tabs[3]:
        display_subsystem_analysis(diagnostic_data)

def display_overview(data: DiagnosticData) -> None:
    """Display overview statistics and charts.
    
    Args:
        data: Diagnostic data instance
    """
    st.header("Diagnostic Overview")
    
    # Calculate statistics
    total_issues = len([i for i in data.issues if i["type"] == "issue"])
    total_recommendations = len([i for i in data.issues if i["type"] == "recommendation"])
    critical_issues = len([i for i in data.issues if i.get("severity") == "CRITICAL"])
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Issues", total_issues)
    col2.metric("Recommendations", total_recommendations)
    col3.metric("Critical Issues", critical_issues)
    
    # Calculate completion rate for recommendations
    completed = len([i for i in data.issues 
                     if i["type"] == "recommendation" and i.get("status") == "Completed"])
    
    if total_recommendations > 0:
        completion_rate = completed / total_recommendations * 100
    else:
        completion_rate = 0
    
    col4.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Severity distribution
    st.subheader("Issue Severity Distribution")
    severity_counts = {}
    for severity in data.severities:
        count = len([i for i in data.issues if i.get("severity") == severity])
        severity_counts[severity] = count
    
    # Create chart
    if severity_counts:
        df = pd.DataFrame({
            "Severity": list(severity_counts.keys()),
            "Count": list(severity_counts.values())
        })
        
        fig = px.bar(df, x="Severity", y="Count", 
                    color="Severity", 
                    color_discrete_map=SEVERITY_COLORS,
                    title="Issue Severity Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Subsystem health overview
    st.subheader("Subsystem Health Overview")
    
    subsystem_issues = {}
    for subsystem in data.subsystems:
        issues = [i for i in data.issues if i["subsystem"] == subsystem]
        severity_breakdown = {
            "CRITICAL": len([i for i in issues if i.get("severity") == "CRITICAL"]),
            "WARNING": len([i for i in issues if i.get("severity") == "WARNING"]),
            "ISSUE": len([i for i in issues if i.get("severity") == "ISSUE"]),
            "INFO": len([i for i in issues if i.get("severity") == "INFO"]),
            "POSITIVE": len([i for i in issues if i.get("severity") == "POSITIVE"])
        }
        
        # Calculate health score (higher is better)
        # Positive findings add to the score, issues subtract based on severity
        health_score = (
            severity_breakdown["POSITIVE"] * 10 - 
            severity_breakdown["CRITICAL"] * 10 -
            severity_breakdown["WARNING"] * 5 -
            severity_breakdown["ISSUE"] * 2 -
            severity_breakdown["INFO"] * 0
        )
        
        subsystem_issues[subsystem] = {
            "breakdown": severity_breakdown,
            "health_score": health_score,
            "total_issues": sum(severity_breakdown.values()) - severity_breakdown["POSITIVE"]
        }
    
    # Create health score chart
    if subsystem_issues:
        df = pd.DataFrame({
            "Subsystem": list(subsystem_issues.keys()),
            "Health Score": [data["health_score"] for data in subsystem_issues.values()],
            "Total Issues": [data["total_issues"] for data in subsystem_issues.values()]
        })
        
        # Sort by health score
        df = df.sort_values("Health Score")
        
        fig = px.bar(df, x="Subsystem", y="Health Score", 
                    color="Health Score",
                    color_continuous_scale=["red", "yellow", "green"],
                    title="Subsystem Health Scores",
                    hover_data=["Total Issues"])
                    
        st.plotly_chart(fig, use_container_width=True)

def display_remediation_timeline(data: DiagnosticData) -> None:
    """Display remediation timeline visualization.
    
    Args:
        data: Diagnostic data instance
    """
    st.header("Remediation Timeline")
    
    # Get all recommendations
    recommendations = [i for i in data.issues if i["type"] == "recommendation"]
    
    # Sidebar for setting timeline parameters
    st.sidebar.subheader("Timeline Settings")
    timeline_start = st.sidebar.date_input(
        "Timeline Start Date", 
        value=datetime.date.today()
    )
    
    # Determine timeline dates if not set
    timeline_dates = {}
    
    for i, rec in enumerate(recommendations):
        # Default timeline based on priority if not set
        if not rec.get("due_date"):
            if rec.get("priority") == "Critical":
                days_to_add = 7
            elif rec.get("priority") == "High":
                days_to_add = 14
            elif rec.get("priority") == "Medium":
                days_to_add = 30
            else:  # Low
                days_to_add = 60
                
            due_date = timeline_start + datetime.timedelta(days=days_to_add)
            timeline_dates[rec["id"]] = due_date.isoformat()
    
    # Allow editing timeline
    st.subheader("Set Remediation Dates")
    st.write("Adjust due dates for recommendations")
    
    priority_filter = st.multiselect(
        "Filter by Priority",
        options=data.priorities,
        default=data.priorities
    )
    
    subsystem_filter = st.multiselect(
        "Filter by Subsystem",
        options=data.subsystems,
        default=data.subsystems
    )
    
    # Filter recommendations
    filtered_recs = [r for r in recommendations 
                     if r.get("priority", "") in priority_filter 
                     and r["subsystem"] in subsystem_filter]
    
    # Group by priority
    for priority in ["Critical", "High", "Medium", "Low"]:
        if priority in priority_filter:
            priority_recs = [r for r in filtered_recs if r.get("priority") == priority]
            if priority_recs:
                st.subheader(f"{priority} Priority")
                
                for rec in priority_recs:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**{rec['id']}**: {rec['description']}")
                    
                    with col2:
                        # Get current due date or default
                        current_due_date = rec.get("due_date")
                        if current_due_date:
                            try:
                                due_date = datetime.datetime.fromisoformat(current_due_date).date()
                            except:
                                due_date = timeline_start + datetime.timedelta(days=30)
                        else:
                            due_date = timeline_dates.get(
                                rec["id"], 
                                (timeline_start + datetime.timedelta(days=30))
                            )
                            
                        new_due_date = st.date_input(
                            f"Due Date for {rec['id']}", 
                            value=due_date,
                            key=f"due_date_{rec['id']}"
                        )
                        
                        # Update if changed
                        if new_due_date != due_date:
                            data.update_issue(rec["id"], {"due_date": new_due_date.isoformat()})
                    
                    with col3:
                        status_options = ["Not Started", "In Progress", "Completed", "Blocked"]
                        current_status = rec.get("status", "Not Started")
                        new_status = st.selectbox(
                            "Status",
                            options=status_options,
                            index=status_options.index(current_status),
                            key=f"status_{rec['id']}"
                        )
                        
                        # Update if changed
                        if new_status != current_status:
                            data.update_issue(rec["id"], {"status": new_status})
    
    # Display Gantt chart
    st.subheader("Remediation Timeline")
    
    # Prepare data for Gantt chart
    gantt_data = []
    for rec in recommendations:
        if rec.get("due_date"):
            try:
                due_date = datetime.datetime.fromisoformat(rec["due_date"])
                start_date = timeline_start
                
                # Estimate start based on priority
                if rec.get("priority") == "Critical":
                    start_offset = 0
                elif rec.get("priority") == "High":
                    start_offset = 7
                elif rec.get("priority") == "Medium":
                    start_offset = 14
                else:  # Low
                    start_offset = 30
                
                start_date = timeline_start + datetime.timedelta(days=start_offset)
                
                gantt_data.append({
                    "Task": rec["id"],
                    "Description": rec["description"][:30] + "..." if len(rec["description"]) > 30 else rec["description"],
                    "Start": start_date,
                    "Finish": due_date,
                    "Priority": rec.get("priority", "Medium"),
                    "Status": rec.get("status", "Not Started"),
                    "Subsystem": rec["subsystem"]
                })
            except:
                pass
    
    if gantt_data:
        df = pd.DataFrame(gantt_data)
        
        # Color mapping for status
        status_colors = {
            "Not Started": "lightgrey",
            "In Progress": "royalblue",
            "Completed": "green",
            "Blocked": "red"
        }
        
        fig = px.timeline(
            df, 
            x_start="Start", 
            x_end="Finish", 
            y="Task",
            color="Status",
            color_discrete_map=status_colors,
            hover_data=["Description", "Priority", "Subsystem"],
            title="Remediation Timeline"
        )
        
        # Customize layout
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=600)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Set due dates for recommendations to generate a timeline visualization")

def display_issue_tracking(data: DiagnosticData) -> None:
    """Display issue tracking interface.
    
    Args:
        data: Diagnostic data instance
    """
    st.header("Issue Tracking System")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subsystem_filter = st.multiselect(
            "Filter by Subsystem",
            options=data.subsystems,
            default=data.subsystems
        )
    
    with col2:
        type_filter = st.multiselect(
            "Filter by Type",
            options=["issue", "recommendation"],
            default=["issue", "recommendation"]
        )
    
    with col3:
        severity_priority_filter = st.multiselect(
            "Filter by Severity/Priority",
            options=data.severities + data.priorities,
            default=["CRITICAL"] if "CRITICAL" in data.severities else []
        )
    
    # Search bar
    search_query = st.text_input("Search Issues", "")
    
    # Filter issues
    filtered_issues = []
    for issue in data.issues:
        if issue["subsystem"] not in subsystem_filter:
            continue
        
        if issue["type"] not in type_filter:
            continue
        
        severity_or_priority = issue.get("severity", issue.get("priority", ""))
        if severity_or_priority not in severity_priority_filter and severity_priority_filter:
            continue
        
        if search_query and search_query.lower() not in issue["description"].lower() and search_query.lower() not in issue["id"].lower():
            continue
        
        filtered_issues.append(issue)
    
    # Display count
    st.write(f"Displaying {len(filtered_issues)} of {len(data.issues)} issues")
    
    # Display issues in a table
    if filtered_issues:
        # Convert to DataFrame for display
        table_data = []
        for issue in filtered_issues:
            row = {
                "ID": issue["id"],
                "Description": issue["description"],
                "Subsystem": issue["subsystem"],
                "Type": issue["type"].capitalize()
            }
            
            if issue["type"] == "issue":
                row["Severity"] = issue.get("severity", "")
            else:
                row["Priority"] = issue.get("priority", "")
                row["Status"] = issue.get("status", "Not Started")
                row["Due Date"] = issue.get("due_date", "")
                
            table_data.append(row)
        
        df = pd.DataFrame(table_data)
        
        # Display as interactive table
        st.dataframe(
            df,
            column_config={
                "Description": st.column_config.TextColumn("Description", width="large"),
                "Due Date": st.column_config.DateColumn("Due Date")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Issue details and editing
        st.subheader("Issue Details")
        
        selected_issue_id = st.selectbox(
            "Select Issue for Details",
            options=[issue["id"] for issue in filtered_issues]
        )
        
        if selected_issue_id:
            # Find the selected issue
            selected_issue = next((i for i in data.issues if i["id"] == selected_issue_id), None)
            
            if selected_issue:
                # Display details
                st.subheader(f"{selected_issue['id']}")
                st.write(f"**Description:** {selected_issue['description']}")
                st.write(f"**Subsystem:** {selected_issue['subsystem']}")
                
                if selected_issue["type"] == "issue":
                    st.write(f"**Severity:** {selected_issue.get('severity', '')}")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Priority:** {selected_issue.get('priority', '')}")
                        
                        status_options = ["Not Started", "In Progress", "Completed", "Blocked"]
                        current_status = selected_issue.get("status", "Not Started")
                        new_status = st.selectbox(
                            "Status",
                            options=status_options,
                            index=status_options.index(current_status)
                        )
                        
                        # Update if changed
                        if new_status != current_status:
                            data.update_issue(selected_issue_id, {"status": new_status})
                    
                    with col2:
                        # Due date editing
                        current_due_date = selected_issue.get("due_date")
                        if current_due_date:
                            try:
                                due_date = datetime.datetime.fromisoformat(current_due_date).date()
                            except:
                                due_date = datetime.date.today() + datetime.timedelta(days=30)
                        else:
                            due_date = datetime.date.today() + datetime.timedelta(days=30)
                            
                        new_due_date = st.date_input(
                            "Due Date", 
                            value=due_date
                        )
                        
                        # Update if changed
                        if new_due_date != due_date:
                            data.update_issue(selected_issue_id, {"due_date": new_due_date.isoformat()})
                    
                    with col3:
                        # Assignee
                        current_assignee = selected_issue.get("assignee", "")
                        new_assignee = st.text_input("Assignee", value=current_assignee)
                        
                        # Update if changed
                        if new_assignee != current_assignee:
                            data.update_issue(selected_issue_id, {"assignee": new_assignee})
                
                # Notes
                st.subheader("Notes")
                current_notes = selected_issue.get("notes", "")
                new_notes = st.text_area("Add/Edit Notes", value=current_notes, height=100)
                
                # Update notes if changed
                if new_notes != current_notes:
                    data.update_issue(selected_issue_id, {"notes": new_notes})
                    st.success("Notes updated")

def display_subsystem_analysis(data: DiagnosticData) -> None:
    """Display detailed subsystem analysis.
    
    Args:
        data: Diagnostic data instance
    """
    st.header("Subsystem Analysis")
    
    # Select subsystem
    selected_subsystem = st.selectbox(
        "Select Subsystem",
        options=data.subsystems
    )
    
    if selected_subsystem:
        # Filter issues for selected subsystem
        subsystem_issues = [i for i in data.issues if i["subsystem"] == selected_subsystem]
        
        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Total issues
        issues_count = len([i for i in subsystem_issues if i["type"] == "issue"])
        col1.metric("Total Issues", issues_count)
        
        # Critical issues
        critical_count = len([i for i in subsystem_issues 
                             if i["type"] == "issue" and i.get("severity") == "CRITICAL"])
        col2.metric("Critical Issues", critical_count)
        
        # Recommendations
        rec_count = len([i for i in subsystem_issues if i["type"] == "recommendation"])
        col3.metric("Recommendations", rec_count)
        
        # Completion rate
        completed = len([i for i in subsystem_issues 
                         if i["type"] == "recommendation" and i.get("status") == "Completed"])
        if rec_count > 0:
            completion_rate = completed / rec_count * 100
        else:
            completion_rate = 0
        col4.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # Severity breakdown
        severity_counts = {}
        for severity in data.severities:
            count = len([i for i in subsystem_issues 
                         if i["type"] == "issue" and i.get("severity") == severity])
            if count > 0:
                severity_counts[severity] = count
        
        # Create chart
        if severity_counts:
            st.subheader("Issue Severity Breakdown")
            
            df = pd.DataFrame({
                "Severity": list(severity_counts.keys()),
                "Count": list(severity_counts.values())
            })
            
            fig = px.pie(df, values="Count", names="Severity", 
                        color="Severity", 
                        color_discrete_map=SEVERITY_COLORS,
                        title=f"{selected_subsystem} Severity Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations by priority
        priority_counts = {}
        for priority in data.priorities:
            count = len([i for i in subsystem_issues 
                         if i["type"] == "recommendation" and i.get("priority") == priority])
            if count > 0:
                priority_counts[priority] = count
        
        # Create chart
        if priority_counts:
            st.subheader("Recommendations by Priority")
            
            df = pd.DataFrame({
                "Priority": list(priority_counts.keys()),
                "Count": list(priority_counts.values())
            })
            
            fig = px.pie(df, values="Count", names="Priority", 
                        color="Priority", 
                        color_discrete_map=PRIORITY_COLORS,
                        title=f"{selected_subsystem} Recommendation Priorities")
            st.plotly_chart(fig, use_container_width=True)
        
        # Issue list
        st.subheader("Issues & Recommendations")
        
        tabs = st.tabs(["Issues", "Recommendations"])
        
        with tabs[0]:
            issues = [i for i in subsystem_issues if i["type"] == "issue"]
            
            if issues:
                for issue in issues:
                    severity = issue.get("severity", "")
                    severity_color = SEVERITY_COLORS.get(severity, "gray")
                    
                    st.markdown(
                        f"<div style='border-left: 5px solid {severity_color}; padding-left: 10px;'>"
                        f"<h4>{issue['id']}</h4>"
                        f"<p>{issue['description']}</p>"
                        f"<p><strong>Severity:</strong> {severity}</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("No issues found for this subsystem")
        
        with tabs[1]:
            recommendations = [i for i in subsystem_issues if i["type"] == "recommendation"]
            
            if recommendations:
                for rec in recommendations:
                    priority = rec.get("priority", "")
                    priority_color = PRIORITY_COLORS.get(priority, "gray")
                    status = rec.get("status", "Not Started")
                    
                    # Determine status color
                    if status == "Completed":
                        status_color = "green"
                    elif status == "In Progress":
                        status_color = "blue"
                    elif status == "Blocked":
                        status_color = "red"
                    else:
                        status_color = "gray"
                    
                    st.markdown(
                        f"<div style='border-left: 5px solid {priority_color}; padding-left: 10px;'>"
                        f"<h4>{rec['id']}</h4>"
                        f"<p>{rec['description']}</p>"
                        f"<p><strong>Priority:</strong> {priority} | "
                        f"<strong>Status:</strong> <span style='color: {status_color};'>{status}</span></p>"
                        f"<p><strong>Due Date:</strong> {rec.get('due_date', 'Not set')}</p>"
                        "</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("No recommendations found for this subsystem")

def main():
    """Main entry point for the diagnostic visualization module."""
    st.set_page_config(
        page_title="EGOS Diagnostic Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Load diagnostic data
    report_path = Path(__file__).parent.parent / "strategic-thinking" / "reports" / "EGOS_Project_Diagnostic_Report.md"
    if not report_path.exists():
        report_path = Path(DIAGNOSTIC_REPORT_PATH)
    
    data = DiagnosticData(report_path)
    
    # Display dashboard
    display_dashboard(data)

if __name__ == "__main__":
    main()