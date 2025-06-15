#!/usr/bin/env python3
"""
ATRiAN Audit Endpoint Monitoring Dashboard

This script creates a web-based dashboard to visualize performance metrics
for the ATRiAN EaaS API's audit endpoint over time. It reads performance data
collected by the audit_performance_monitor.py tool and displays trends,
statistics, and recommendations.

Usage:
    python audit_dashboard.py [--port PORT] [--data-dir PATH]

Author: ATRiAN Development Team
Date: 2025-06-03
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
import json
import glob
import argparse
import datetime
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Default paths
DEFAULT_DATA_DIR = "C:/EGOS/ATRiAN/data/performance"
DEFAULT_PORT = 8050

class AuditDashboard:
    """Dashboard for visualizing audit endpoint performance metrics"""
    
    def __init__(self, data_dir: str):
        """
        Initialize the dashboard
        
        Args:
            data_dir: Directory containing performance data files
        """
        self.data_dir = Path(data_dir)
        self.app = dash.Dash(__name__, title="ATRiAN Audit Endpoint Dashboard")
        self.performance_data = self._load_performance_data()
        self._setup_layout()
        self._setup_callbacks()
        
    def _load_performance_data(self) -> pd.DataFrame:
        """
        Load performance data from JSON files
        
        Returns:
            DataFrame containing performance metrics
        """
        # Find all performance summary files
        summary_files = glob.glob(str(self.data_dir / "*_summary.json"))
        
        if not summary_files:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame({
                "timestamp": [],
                "test_case": [],
                "avg_response_time_ms": [],
                "median_response_time_ms": [],
                "min_response_time_ms": [],
                "max_response_time_ms": [],
                "p95_response_time_ms": [],
                "success_rate": [],
                "log_count": []
            })
        
        # Load and combine data from all files
        all_data = []
        
        for file_path in summary_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract timestamp
                timestamp = data.get("timestamp", "")
                
                # Process each test case
                for test_case in data.get("test_cases", []):
                    test_case["timestamp"] = timestamp
                    all_data.append(test_case)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Convert timestamp to datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date
        
        return df
    
    def _setup_layout(self):
        """Set up the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("ATRiAN Audit Endpoint Performance Dashboard"),
                html.P("Monitoring and analysis of the /ethics/audit endpoint performance metrics"),
                html.Hr()
            ], style={"textAlign": "center", "marginBottom": "20px"}),
            
            # Filters
            html.Div([
                html.H3("Filters"),
                html.Div([
                    html.Label("Date Range:"),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=self._get_min_date(),
                        max_date_allowed=self._get_max_date(),
                        start_date=self._get_min_date(),
                        end_date=self._get_max_date()
                    )
                ], style={"marginBottom": "10px"}),
                
                html.Div([
                    html.Label("Test Cases:"),
                    dcc.Dropdown(
                        id="test-case-filter",
                        options=self._get_test_case_options(),
                        value=[],
                        multi=True,
                        placeholder="Select test cases to filter..."
                    )
                ])
            ], style={"padding": "10px", "backgroundColor": "#f8f9fa", "borderRadius": "5px", "marginBottom": "20px"}),
            
            # Performance Overview
            html.Div([
                html.H3("Performance Overview"),
                html.Div([
                    html.Div([
                        html.H4("Response Time Trends"),
                        dcc.Graph(id="response-time-trend")
                    ], style={"width": "50%", "display": "inline-block"}),
                    
                    html.Div([
                        html.H4("Success Rate Trends"),
                        dcc.Graph(id="success-rate-trend")
                    ], style={"width": "50%", "display": "inline-block"})
                ]),
                
                html.Div([
                    html.H4("Performance Metrics by Test Case"),
                    dcc.Graph(id="test-case-comparison")
                ], style={"marginTop": "20px"})
            ], style={"marginBottom": "20px"}),
            
            # Detailed Metrics
            html.Div([
                html.H3("Detailed Metrics"),
                dash_table.DataTable(
                    id="metrics-table",
                    columns=[
                        {"name": "Date", "id": "date"},
                        {"name": "Test Case", "id": "test_case"},
                        {"name": "Avg Response Time (ms)", "id": "avg_response_time_ms"},
                        {"name": "Median Response Time (ms)", "id": "median_response_time_ms"},
                        {"name": "Min Response Time (ms)", "id": "min_response_time_ms"},
                        {"name": "Max Response Time (ms)", "id": "max_response_time_ms"},
                        {"name": "P95 Response Time (ms)", "id": "p95_response_time_ms"},
                        {"name": "Success Rate (%)", "id": "success_rate"},
                        {"name": "Log Count", "id": "log_count"}
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "10px"},
                    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                    page_size=10
                )
            ], style={"marginBottom": "20px"}),
            
            # Performance Recommendations
            html.Div([
                html.H3("Performance Recommendations"),
                html.Div(id="recommendations")
            ], style={"padding": "10px", "backgroundColor": "#f8f9fa", "borderRadius": "5px", "marginBottom": "20px"}),
            
            # Footer
            html.Div([
                html.Hr(),
                html.P([
                    "ATRiAN EaaS API Performance Dashboard | Last updated: ",
                    html.Span(id="last-updated")
                ]),
                html.P([
                    "Data source: ",
                    html.Code(str(self.data_dir))
                ])
            ], style={"textAlign": "center", "marginTop": "30px", "color": "#666"})
        ], style={"margin": "0 auto", "maxWidth": "1200px", "padding": "20px"})
    
    def _setup_callbacks(self):
        """Set up interactive callbacks for the dashboard"""
        
        # Update response time trend chart
        @self.app.callback(
            Output("response-time-trend", "figure"),
            [
                Input("date-range", "start_date"),
                Input("date-range", "end_date"),
                Input("test-case-filter", "value")
            ]
        )
        def update_response_time_trend(start_date, end_date, test_cases):
            filtered_df = self._filter_data(start_date, end_date, test_cases)
            
            if filtered_df.empty:
                return self._empty_figure("No data available")
            
            # Group by date and test case, calculate average response time
            df_grouped = filtered_df.groupby(["date", "test_case"]).agg({
                "avg_response_time_ms": "mean"
            }).reset_index()
            
            fig = px.line(
                df_grouped, 
                x="date", 
                y="avg_response_time_ms", 
                color="test_case",
                labels={
                    "date": "Date",
                    "avg_response_time_ms": "Average Response Time (ms)",
                    "test_case": "Test Case"
                },
                title="Average Response Time Trend"
            )
            
            # Add threshold lines
            fig.add_shape(
                type="line",
                x0=df_grouped["date"].min(),
                x1=df_grouped["date"].max(),
                y0=1000,
                y1=1000,
                line=dict(color="orange", width=2, dash="dash"),
                name="Warning Threshold"
            )
            
            fig.add_shape(
                type="line",
                x0=df_grouped["date"].min(),
                x1=df_grouped["date"].max(),
                y0=2000,
                y1=2000,
                line=dict(color="red", width=2, dash="dash"),
                name="Critical Threshold"
            )
            
            return fig
        
        # Update success rate trend chart
        @self.app.callback(
            Output("success-rate-trend", "figure"),
            [
                Input("date-range", "start_date"),
                Input("date-range", "end_date"),
                Input("test-case-filter", "value")
            ]
        )
        def update_success_rate_trend(start_date, end_date, test_cases):
            filtered_df = self._filter_data(start_date, end_date, test_cases)
            
            if filtered_df.empty:
                return self._empty_figure("No data available")
            
            # Group by date and test case, calculate average success rate
            df_grouped = filtered_df.groupby(["date", "test_case"]).agg({
                "success_rate": "mean"
            }).reset_index()
            
            fig = px.line(
                df_grouped, 
                x="date", 
                y="success_rate", 
                color="test_case",
                labels={
                    "date": "Date",
                    "success_rate": "Success Rate (%)",
                    "test_case": "Test Case"
                },
                title="Success Rate Trend"
            )
            
            # Add threshold line
            fig.add_shape(
                type="line",
                x0=df_grouped["date"].min(),
                x1=df_grouped["date"].max(),
                y0=99.5,
                y1=99.5,
                line=dict(color="red", width=2, dash="dash"),
                name="Minimum Acceptable Success Rate"
            )
            
            return fig
        
        # Update test case comparison chart
        @self.app.callback(
            Output("test-case-comparison", "figure"),
            [
                Input("date-range", "start_date"),
                Input("date-range", "end_date"),
                Input("test-case-filter", "value")
            ]
        )
        def update_test_case_comparison(start_date, end_date, test_cases):
            filtered_df = self._filter_data(start_date, end_date, test_cases)
            
            if filtered_df.empty:
                return self._empty_figure("No data available")
            
            # Group by test case, calculate average metrics
            df_grouped = filtered_df.groupby("test_case").agg({
                "avg_response_time_ms": "mean",
                "success_rate": "mean",
                "log_count": "mean"
            }).reset_index()
            
            fig = px.bar(
                df_grouped, 
                x="test_case", 
                y="avg_response_time_ms",
                color="success_rate",
                color_continuous_scale="RdYlGn",
                labels={
                    "test_case": "Test Case",
                    "avg_response_time_ms": "Average Response Time (ms)",
                    "success_rate": "Success Rate (%)"
                },
                title="Performance Comparison by Test Case"
            )
            
            return fig
        
        # Update metrics table
        @self.app.callback(
            Output("metrics-table", "data"),
            [
                Input("date-range", "start_date"),
                Input("date-range", "end_date"),
                Input("test-case-filter", "value")
            ]
        )
        def update_metrics_table(start_date, end_date, test_cases):
            filtered_df = self._filter_data(start_date, end_date, test_cases)
            
            if filtered_df.empty:
                return []
            
            # Convert date column to string for display
            if "date" in filtered_df.columns:
                filtered_df["date"] = filtered_df["date"].astype(str)
            
            # Round numeric columns for display
            numeric_cols = [
                "avg_response_time_ms", "median_response_time_ms", 
                "min_response_time_ms", "max_response_time_ms", 
                "p95_response_time_ms", "success_rate"
            ]
            
            for col in numeric_cols:
                if col in filtered_df.columns:
                    filtered_df[col] = filtered_df[col].round(2)
            
            return filtered_df.to_dict("records")
        
        # Update recommendations
        @self.app.callback(
            Output("recommendations", "children"),
            [
                Input("date-range", "start_date"),
                Input("date-range", "end_date"),
                Input("test-case-filter", "value")
            ]
        )
        def update_recommendations(start_date, end_date, test_cases):
            filtered_df = self._filter_data(start_date, end_date, test_cases)
            
            if filtered_df.empty:
                return html.P("No data available for recommendations.")
            
            recommendations = []
            
            # Check for slow response times
            slow_threshold = 2000  # ms
            slow_cases = filtered_df[filtered_df["avg_response_time_ms"] > slow_threshold]
            
            if not slow_cases.empty:
                slow_list = html.Ul([
                    html.Li(f"{row['test_case']}: {row['avg_response_time_ms']:.2f} ms")
                    for _, row in slow_cases.iterrows()
                ])
                
                recommendations.append(html.Div([
                    html.H4("Response Time Optimization", style={"color": "red"}),
                    html.P("The following test cases exceed the critical response time threshold:"),
                    slow_list,
                    html.P([
                        "Recommendation: Consider implementing caching, optimizing database queries, ",
                        "or adding indexes to improve performance."
                    ])
                ]))
            
            # Check for success rate issues
            success_threshold = 99.5  # %
            low_success_cases = filtered_df[filtered_df["success_rate"] < success_threshold]
            
            if not low_success_cases.empty:
                low_success_list = html.Ul([
                    html.Li(f"{row['test_case']}: {row['success_rate']:.2f}%")
                    for _, row in low_success_cases.iterrows()
                ])
                
                recommendations.append(html.Div([
                    html.H4("Reliability Concerns", style={"color": "red"}),
                    html.P("The following test cases have success rates below the acceptable threshold:"),
                    low_success_list,
                    html.P([
                        "Recommendation: Investigate error logs for these test cases and implement ",
                        "better error handling or fix underlying issues."
                    ])
                ]))
            
            # Check for high variability
            high_variability_cases = filtered_df[
                (filtered_df["max_response_time_ms"] - filtered_df["min_response_time_ms"]) > 
                (3 * filtered_df["avg_response_time_ms"])
            ]
            
            if not high_variability_cases.empty:
                variability_list = html.Ul([
                    html.Li(f"{row['test_case']}: Range {row['min_response_time_ms']:.2f} - {row['max_response_time_ms']:.2f} ms")
                    for _, row in high_variability_cases.iterrows()
                ])
                
                recommendations.append(html.Div([
                    html.H4("Performance Variability", style={"color": "orange"}),
                    html.P("The following test cases show high variability in response times:"),
                    variability_list,
                    html.P([
                        "Recommendation: Consider implementing more consistent resource allocation ",
                        "or investigate background processes that might be affecting performance."
                    ])
                ]))
            
            # If no specific issues found
            if not recommendations:
                recommendations.append(html.Div([
                    html.H4("Good Performance", style={"color": "green"}),
                    html.P([
                        "All test cases are performing within acceptable parameters. ",
                        "Continue monitoring for any changes in performance patterns."
                    ])
                ]))
            
            # Add general recommendations
            recommendations.append(html.Div([
                html.H4("General Recommendations", style={"marginTop": "20px"}),
                html.Ul([
                    html.Li("Consider implementing a caching layer for frequently accessed audit logs"),
                    html.Li("Evaluate database indexing strategy for audit log queries"),
                    html.Li("Monitor system resource usage during peak load periods"),
                    html.Li("Implement automated alerts for performance degradation")
                ])
            ]))
            
            return recommendations
        
        # Update last updated timestamp
        @self.app.callback(
            Output("last-updated", "children"),
            [Input("date-range", "start_date")]  # Any input will trigger this
        )
        def update_timestamp(_):
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _filter_data(self, start_date, end_date, test_cases):
        """
        Filter performance data based on date range and test cases
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            test_cases: List of test case names to include
            
        Returns:
            Filtered DataFrame
        """
        df = self.performance_data.copy()
        
        if df.empty:
            return df
        
        # Filter by date range
        if start_date and end_date and "date" in df.columns:
            start_date = pd.to_datetime(start_date).date()
            end_date = pd.to_datetime(end_date).date()
            df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        
        # Filter by test cases
        if test_cases and "test_case" in df.columns:
            if len(test_cases) > 0:
                df = df[df["test_case"].isin(test_cases)]
        
        return df
    
    def _get_min_date(self):
        """Get the earliest date in the performance data"""
        if "date" in self.performance_data.columns and not self.performance_data.empty:
            return self.performance_data["date"].min()
        return datetime.date.today() - datetime.timedelta(days=30)
    
    def _get_max_date(self):
        """Get the latest date in the performance data"""
        if "date" in self.performance_data.columns and not self.performance_data.empty:
            return self.performance_data["date"].max()
        return datetime.date.today()
    
    def _get_test_case_options(self):
        """Get options for test case dropdown"""
        if "test_case" in self.performance_data.columns and not self.performance_data.empty:
            test_cases = sorted(self.performance_data["test_case"].unique())
            return [{"label": tc, "value": tc} for tc in test_cases]
        return []
    
    def _empty_figure(self, message):
        """Create an empty figure with a message"""
        return {
            "data": [],
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": message,
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 20
                        }
                    }
                ]
            }
        }
    
    def run_server(self, port=DEFAULT_PORT, debug=False):
        """Run the dashboard server"""
        self.app.run_server(port=port, debug=debug)

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="ATRiAN Audit Endpoint Monitoring Dashboard")
    parser.add_argument(
        "--port", 
        type=int,
        default=DEFAULT_PORT,
        help="Port to run the dashboard server on"
    )
    parser.add_argument(
        "--data-dir", 
        default=DEFAULT_DATA_DIR,
        help="Directory containing performance data files"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    os.makedirs(args.data_dir, exist_ok=True)
    
    # Create and run dashboard
    dashboard = AuditDashboard(args.data_dir)
    dashboard.run_server(port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()