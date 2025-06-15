"""
EGOS Diagnostic Metrics Dashboard

This module provides analytics and visualization components for tracking remediation progress,
team performance, and system health metrics from the diagnostic tracking system.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](app_dashboard_diagnostic_roadmap.py) <!-- EGOS-REF-6A8B8DFB --> - Project roadmap and planning
- Related Components:
  - [diagnostic_visualization.py](mdc:./diagnostic_visualization.py) - Main visualization
  - [diagnostic_tracking.py](mdc:./diagnostic_tracking.py) - Data tracking system
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
from plotly.subplots import make_subplots
import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
import json
from pathlib import Path
import logging

# Import local components
try:
    from dashboard.diagnostic_tracking import get_all_issues, get_status_summary
    from dashboard.diagnostic_roadmap import roadmap_manager
except ImportError:
    # Mock functions for when imports fail
    def get_all_issues():
        return []
        
    def get_status_summary():
        return {}
        
    roadmap_manager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.DiagnosticMetrics")

# Color schemes
STATUS_COLORS = {
    "identified": "#e41a1c",
    "acknowledged": "#377eb8",
    "assigned": "#4daf4a",
    "in_progress": "#984ea3",
    "reviewing": "#ff7f00",
    "resolved": "#ffff33",
    "verified": "#a65628",
    "closed": "#f781bf",
    "deferred": "#999999",
    "wont_fix": "#000000"
}

PRIORITY_COLORS = {
    "critical": "#e41a1c",
    "high": "#ff7f00",
    "medium": "#4daf4a",
    "low": "#377eb8",
    "enhancement": "#984ea3"
}

SUBSYSTEM_COLORS = {
    "KOIOS": "#8dd3c7",
    "MYCELIUM": "#ffffb3",
    "CORUJA": "#bebada",
    "ETHIK": "#fb8072",
    "SPARC": "#80b1d3",
    "NEXUS": "#fdb462",
    "CRONOS": "#b3de69"
}

def load_metrics_data() -> Dict[str, Any]:
    """Load metrics data from tracking system.
    
    Returns:
        Dictionary of metrics data
    """
    try:
        # Get all issues
        issues = get_all_issues()
        
        # Convert to DataFrame for easier analysis
        if issues:
            df = pd.DataFrame(issues)
        else:
            # Create empty DataFrame with expected columns
            df = pd.DataFrame(columns=[
                'id', 'title', 'description', 'status', 'priority', 
                'subsystem', 'created', 'updated', 'due_date', 'assignee'
            ])
        
        # Calculate metrics
        metrics = {
            "total_issues": len(issues),
            "issues_dataframe": df,
            "status_summary": get_status_summary(),
            "priority_distribution": _calculate_priority_distribution(df),
            "subsystem_distribution": _calculate_subsystem_distribution(df),
            "resolution_rate": _calculate_resolution_rate(df),
            "velocity": _calculate_velocity(df),
            "age_distribution": _calculate_age_distribution(df),
            "team_performance": _calculate_team_performance(df)
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Error loading metrics data: {e}")
        return {
            "total_issues": 0,
            "issues_dataframe": pd.DataFrame(),
            "status_summary": {},
            "priority_distribution": {},
            "subsystem_distribution": {},
            "resolution_rate": {},
            "velocity": [],
            "age_distribution": {},
            "team_performance": {}
        }

def _calculate_priority_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """Calculate distribution of issues by priority.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        Dictionary mapping priority to count
    """
    if df.empty or 'priority' not in df.columns:
        return {}
        
    return df['priority'].value_counts().to_dict()

def _calculate_subsystem_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """Calculate distribution of issues by subsystem.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        Dictionary mapping subsystem to count
    """
    if df.empty or 'subsystem' not in df.columns:
        return {}
        
    return df['subsystem'].value_counts().to_dict()

def _calculate_resolution_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate issue resolution rate over time.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        Dictionary of resolution metrics
    """
    if df.empty or 'created' not in df.columns or 'status' not in df.columns:
        return {"rate_per_week": 0, "time_series": []}
    
    try:
        # Convert date strings to datetime
        df['created_date'] = pd.to_datetime(df['created'])
        
        # Count resolved issues by week
        resolved_df = df[df['status'].isin(['resolved', 'verified', 'closed'])]
        if resolved_df.empty:
            return {"rate_per_week": 0, "time_series": []}
            
        resolved_df['week'] = resolved_df['created_date'].dt.isocalendar().week
        resolved_df['year'] = resolved_df['created_date'].dt.isocalendar().year
        
        # Group by year-week
        resolved_counts = resolved_df.groupby(['year', 'week']).size().reset_index(name='count')
        
        # Calculate average weekly resolution rate
        rate_per_week = resolved_counts['count'].mean() if len(resolved_counts) > 0 else 0
        
        # Create time series for visualization
        time_series = []
        for _, row in resolved_counts.iterrows():
            time_series.append({
                'year': int(row['year']),
                'week': int(row['week']),
                'count': int(row['count'])
            })
        
        return {
            "rate_per_week": rate_per_week,
            "time_series": time_series
        }
    except Exception as e:
        logger.error(f"Error calculating resolution rate: {e}")
        return {"rate_per_week": 0, "time_series": []}

def _calculate_velocity(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Calculate team velocity over time.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        List of velocity data points
    """
    if df.empty or 'status' not in df.columns or 'updated' not in df.columns:
        return []
    
    try:
        # Convert date strings to datetime
        df['updated_date'] = pd.to_datetime(df['updated'])
        
        # Get status transitions
        statuses = ['identified', 'acknowledged', 'assigned', 'in_progress', 
                   'reviewing', 'resolved', 'verified', 'closed']
        
        # Group by week
        df['week'] = df['updated_date'].dt.isocalendar().week
        df['year'] = df['updated_date'].dt.isocalendar().year
        
        # Count status changes by week
        status_changes = []
        
        # Handle case where status_history exists
        if 'status_history' in df.columns and not df['status_history'].isna().all():
            # Extract status changes from history
            for idx, row in df.iterrows():
                if isinstance(row.get('status_history'), list):
                    for change in row['status_history']:
                        if 'timestamp' in change and 'to' in change:
                            try:
                                change_date = pd.to_datetime(change['timestamp'])
                                status_changes.append({
                                    'year': change_date.year,
                                    'week': change_date.isocalendar().week,
                                    'status': change['to']
                                })
                            except Exception:
                                pass
        
        # Group by year-week and count statuses
        velocity_data = []
        
        if status_changes:
            # Convert to DataFrame
            changes_df = pd.DataFrame(status_changes)
            
            # Group by year, week, status
            grouped = changes_df.groupby(['year', 'week', 'status']).size().reset_index(name='count')
            
            # Format for visualization
            for _, row in grouped.iterrows():
                velocity_data.append({
                    'year': int(row['year']),
                    'week': int(row['week']),
                    'status': row['status'],
                    'count': int(row['count'])
                })
        
        return velocity_data
    except Exception as e:
        logger.error(f"Error calculating velocity: {e}")
        return []

def _calculate_age_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """Calculate age distribution of open issues.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        Dictionary mapping age buckets to counts
    """
    if df.empty or 'created' not in df.columns or 'status' not in df.columns:
        return {}
    
    try:
        # Filter open issues
        open_statuses = ['identified', 'acknowledged', 'assigned', 'in_progress', 'reviewing']
        open_issues = df[df['status'].isin(open_statuses)]
        
        if open_issues.empty:
            return {}
        
        # Calculate age in days
        open_issues['created_date'] = pd.to_datetime(open_issues['created'])
        now = pd.Timestamp(datetime.datetime.now())
        open_issues['age_days'] = (now - open_issues['created_date']).dt.days
        
        # Create age buckets
        age_buckets = {
            '< 7 days': 0,
            '7-30 days': 0, 
            '30-90 days': 0,
            '> 90 days': 0
        }
        
        for age in open_issues['age_days']:
            if age < 7:
                age_buckets['< 7 days'] += 1
            elif age < 30:
                age_buckets['7-30 days'] += 1
            elif age < 90:
                age_buckets['30-90 days'] += 1
            else:
                age_buckets['> 90 days'] += 1
        
        return age_buckets
    except Exception as e:
        logger.error(f"Error calculating age distribution: {e}")
        return {}

def _calculate_team_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate team performance metrics.
    
    Args:
        df: DataFrame of issues
        
    Returns:
        Dictionary of team performance metrics
    """
    if df.empty or 'assignee' not in df.columns or 'status' not in df.columns:
        return {}
    
    try:
        # Group by assignee
        assignee_stats = {}
        
        # Filter issues with assignees
        assigned_issues = df[df['assignee'].notna()]
        
        if assigned_issues.empty:
            return {}
        
        # Calculate metrics for each assignee
        for assignee, group in assigned_issues.groupby('assignee'):
            closed_issues = group[group['status'].isin(['resolved', 'verified', 'closed'])]
            
            # Calculate average time to resolution if possible
            avg_resolution_time = None
            if 'created' in group.columns and 'updated' in closed_issues.columns and not closed_issues.empty:
                closed_issues['created_date'] = pd.to_datetime(closed_issues['created'])
                closed_issues['updated_date'] = pd.to_datetime(closed_issues['updated'])
                resolution_times = (closed_issues['updated_date'] - closed_issues['created_date']).dt.days
                avg_resolution_time = resolution_times.mean() if not resolution_times.empty else None
            
            assignee_stats[assignee] = {
                'total_issues': len(group),
                'open_issues': len(group[group['status'].isin(['identified', 'acknowledged', 'assigned', 'in_progress', 'reviewing'])]),
                'closed_issues': len(closed_issues),
                'avg_resolution_time': avg_resolution_time
            }
        
        return assignee_stats
    except Exception as e:
        logger.error(f"Error calculating team performance: {e}")
        return {}

def visualize_status_summary(metrics: Dict[str, Any]) -> None:
    """Visualize issue status summary.
    
    Args:
        metrics: Metrics data dictionary
    """
    status_summary = metrics.get("status_summary", {})
    
    if not status_summary:
        st.warning("No status data available")
        return
    
    # Create pie chart
    fig = px.pie(
        names=list(status_summary.keys()),
        values=list(status_summary.values()),
        title="Issue Status Distribution",
        color=list(status_summary.keys()),
        color_discrete_map=STATUS_COLORS
    )
    
    # Update layout
    fig.update_layout(
        legend_title="Status",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display counts in table
    st.markdown("### Status Counts")
    
    # Create DataFrame for table
    status_df = pd.DataFrame({
        'Status': list(status_summary.keys()),
        'Count': list(status_summary.values())
    })
    
    # Calculate percentage
    total = status_df['Count'].sum()
    if total > 0:
        status_df['Percentage'] = (status_df['Count'] / total * 100).round(1).astype(str) + '%'
    else:
        status_df['Percentage'] = '0%'
    
    # Display table
    st.dataframe(status_df, hide_index=True)

def visualize_priority_distribution(metrics: Dict[str, Any]) -> None:
    """Visualize issue priority distribution.
    
    Args:
        metrics: Metrics data dictionary
    """
    priority_distribution = metrics.get("priority_distribution", {})
    
    if not priority_distribution:
        st.warning("No priority data available")
        return
    
    # Sort by priority severity
    priority_order = ["critical", "high", "medium", "low", "enhancement"]
    sorted_priorities = []
    sorted_counts = []
    
    for priority in priority_order:
        if priority in priority_distribution:
            sorted_priorities.append(priority)
            sorted_counts.append(priority_distribution[priority])
    
    # Create bar chart
    fig = px.bar(
        x=sorted_priorities,
        y=sorted_counts,
        title="Issue Priority Distribution",
        color=sorted_priorities,
        color_discrete_map=PRIORITY_COLORS,
        labels={"x": "Priority", "y": "Count"}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Priority",
        yaxis_title="Number of Issues",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def visualize_subsystem_distribution(metrics: Dict[str, Any]) -> None:
    """Visualize issue distribution by subsystem.
    
    Args:
        metrics: Metrics data dictionary
    """
    subsystem_distribution = metrics.get("subsystem_distribution", {})
    
    if not subsystem_distribution:
        st.warning("No subsystem data available")
        return
    
    # Create DataFrame for visualization
    subsystems = list(subsystem_distribution.keys())
    counts = list(subsystem_distribution.values())
    
    # Create bar chart
    fig = px.bar(
        x=subsystems,
        y=counts,
        title="Issues by Subsystem",
        color=subsystems,
        color_discrete_map=SUBSYSTEM_COLORS,
        labels={"x": "Subsystem", "y": "Count"}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Subsystem",
        yaxis_title="Number of Issues",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Create matrix of subsystems and statuses
    if metrics.get("issues_dataframe") is not None and not metrics["issues_dataframe"].empty:
        df = metrics["issues_dataframe"]
        
        if 'subsystem' in df.columns and 'status' in df.columns:
            # Create crosstab
            matrix = pd.crosstab(df['subsystem'], df['status'])
            
            # Display heatmap
            st.markdown("### Subsystem vs Status Matrix")
            
            # Create heatmap
            fig = px.imshow(
                matrix, 
                text_auto=True,
                aspect="auto",
                title="Subsystem vs Status",
                labels=dict(x="Status", y="Subsystem", color="Count")
            )
            
            # Display chart
            st.plotly_chart(fig, use_container_width=True)

def visualize_resolution_rate(metrics: Dict[str, Any]) -> None:
    """Visualize issue resolution rate over time.
    
    Args:
        metrics: Metrics data dictionary
    """
    resolution_rate = metrics.get("resolution_rate", {})
    time_series = resolution_rate.get("time_series", [])
    
    if not time_series:
        st.warning("No resolution rate data available")
        return
    
    # Create DataFrame for visualization
    weeks = []
    counts = []
    
    for point in time_series:
        year = point.get("year", 0)
        week = point.get("week", 0)
        count = point.get("count", 0)
        
        # Format as year-week
        week_label = f"{year}-W{week:02d}"
        weeks.append(week_label)
        counts.append(count)
    
    # Create line chart
    fig = px.line(
        x=weeks,
        y=counts,
        title="Issue Resolution Rate Over Time",
        markers=True,
        labels={"x": "Week", "y": "Resolved Issues"}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Week",
        yaxis_title="Number of Issues Resolved",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display weekly average
    rate_per_week = resolution_rate.get("rate_per_week", 0)
    st.metric("Average Weekly Resolution Rate", f"{rate_per_week:.1f} issues/week")

def visualize_age_distribution(metrics: Dict[str, Any]) -> None:
    """Visualize age distribution of open issues.
    
    Args:
        metrics: Metrics data dictionary
    """
    age_distribution = metrics.get("age_distribution", {})
    
    if not age_distribution:
        st.warning("No age distribution data available")
        return
    
    # Create DataFrame for visualization
    ages = list(age_distribution.keys())
    counts = list(age_distribution.values())
    
    # Create bar chart
    fig = px.bar(
        x=ages,
        y=counts,
        title="Age Distribution of Open Issues",
        labels={"x": "Age", "y": "Count"}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Number of Issues",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

def visualize_team_performance(metrics: Dict[str, Any]) -> None:
    """Visualize team performance metrics.
    
    Args:
        metrics: Metrics data dictionary
    """
    team_performance = metrics.get("team_performance", {})
    
    if not team_performance:
        st.warning("No team performance data available")
        return
    
    # Create DataFrame for table
    performance_data = []
    for assignee, stats in team_performance.items():
        performance_data.append({
            'Assignee': assignee,
            'Total Issues': stats.get('total_issues', 0),
            'Open Issues': stats.get('open_issues', 0),
            'Closed Issues': stats.get('closed_issues', 0),
            'Avg. Resolution Time (days)': round(stats.get('avg_resolution_time', 0), 1) if stats.get('avg_resolution_time') is not None else None
        })
    
    # Convert to DataFrame
    performance_df = pd.DataFrame(performance_data)
    
    # Sort by total issues
    performance_df = performance_df.sort_values('Total Issues', ascending=False)
    
    # Display table
    st.markdown("### Team Performance")
    st.dataframe(performance_df, hide_index=True)
    
    # Create bar chart for closed vs open issues
    if not performance_df.empty:
        assignees = performance_df['Assignee'].tolist()
        open_issues = performance_df['Open Issues'].tolist()
        closed_issues = performance_df['Closed Issues'].tolist()
        
        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(name='Open Issues', x=assignees, y=open_issues),
            go.Bar(name='Closed Issues', x=assignees, y=closed_issues)
        ])
        
        # Update layout
        fig.update_layout(
            title="Issues by Assignee",
            xaxis_title="Assignee",
            yaxis_title="Number of Issues",
            barmode='group',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)

def display_metrics_dashboard() -> None:
    """Display the metrics dashboard."""
    st.title("EGOS Diagnostic Metrics Dashboard")
    
    # Load metrics data
    metrics = load_metrics_data()
    
    # Display summary statistics
    st.markdown("## Summary Statistics")
    
    # Create metrics containers
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues", metrics.get("total_issues", 0))
    
    with col2:
        open_issues = sum(count for status, count in metrics.get("status_summary", {}).items() 
                        if status not in ['resolved', 'verified', 'closed', 'wont_fix'])
        st.metric("Open Issues", open_issues)
    
    with col3:
        closed_issues = sum(count for status, count in metrics.get("status_summary", {}).items() 
                          if status in ['resolved', 'verified', 'closed', 'wont_fix'])
        st.metric("Closed Issues", closed_issues)
    
    with col4:
        resolution_rate = metrics.get("resolution_rate", {}).get("rate_per_week", 0)
        st.metric("Avg. Weekly Resolution", f"{resolution_rate:.1f}")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Status", "Priority & Subsystem", "Resolution Rate", "Age Distribution", "Team Performance"
    ])
    
    with tab1:
        visualize_status_summary(metrics)
    
    with tab2:
        visualize_priority_distribution(metrics)
        visualize_subsystem_distribution(metrics)
    
    with tab3:
        visualize_resolution_rate(metrics)
    
    with tab4:
        visualize_age_distribution(metrics)
    
    with tab5:
        visualize_team_performance(metrics)

# Main function for standalone operation
if __name__ == "__main__":
    display_metrics_dashboard()