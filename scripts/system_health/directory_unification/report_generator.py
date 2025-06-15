#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Report Generator Module for Directory Unification Tool

This module generates comprehensive HTML and Markdown reports documenting
the directory unification process, results, and impact assessment.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\reporting\html_report_builder.py
    - C:\EGOS\scripts\reporting\markdown_formatter.py
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
import json
import logging
import datetime
import shutil
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64
import io

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

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import networkx as nx
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

# Local imports
from .utils import setup_logger, print_banner, format_path, Timer, human_readable_size

# Constants
CONFIG = {
    "REPORT_TEMPLATE_DIR": os.path.join(os.path.dirname(__file__), "templates"),
    "HTML_TEMPLATE": "report_template.html",
    "MD_TEMPLATE": "report_template.md",
    "MAX_ITEMS_IN_REPORT": 100,
    "STANDARD_REPORTS_DIR": os.path.join(os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))), "reports"),
    "REPORT_RETENTION_DAYS": 30,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "CHART_COLORS": ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"]
}

# Set up logger
logger = setup_logger("report_generator", CONFIG["LOG_FORMAT"])


class ReportGenerator:
    """Class for generating detailed reports of the directory unification process."""
    
    def __init__(self, args: Dict[str, Any], context: Dict[str, Any], logger: logging.Logger):
        """Initialize the ReportGenerator class.
        
        Args:
            args: Command line arguments or configuration
            context: Context data from previous modules
        """
        self.args = args
        self.context = context
        self.egos_root = args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))))
        
        # Set up standardized report directory structure
        self.standard_reports_dir = CONFIG["STANDARD_REPORTS_DIR"]
        self.tool_reports_dir = os.path.join(self.standard_reports_dir, "directory_unification")
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir = os.path.join(self.tool_reports_dir, f"report_{self.timestamp}")
        
        # Use output_dir from args if specified, otherwise use the standard location
        self.output_dir = args.get("output_dir", self.report_dir)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Use the logger passed from the main tool
        self.logger = logger
        
        # Clean up old reports
        if not args.get("skip_cleanup", False):
            self._cleanup_old_reports()
    
    def _prepare_report_data(self) -> Dict[str, Any]:
        """Prepare data for the report.
        
        Returns:
            Dict[str, Any]: Data for the report
        """
        # Start with a copy of the full results from self.context
        # self.context is the results dictionary from DirectoryUnificationTool
        report_data = self.context.copy()

        # Add or override specific report metadata
        report_data["title"] = f"Directory Unification Report for Keyword: {self.args.get('keyword', 'N/A')}"
        report_data["report_id"] = self.timestamp # ReportGenerator's timestamp for this specific report instance
        report_data["egos_root"] = self.egos_root
        report_data["dry_run"] = self.args.get("dry_run", True) # Ensure this is correctly sourced
        report_data["standard_reports_location"] = self.standard_reports_dir
        report_data["tool_reports_location"] = self.tool_reports_dir
        report_data["report_location"] = self.report_dir
        
        # Ensure elapsed_time_total is set for the template (maps from 'elapsed_time' in results)
        if 'elapsed_time' in report_data and 'elapsed_time_total' not in report_data:
            report_data['elapsed_time_total'] = report_data['elapsed_time']
        elif 'elapsed_time_total' not in report_data: # If 'elapsed_time' was also missing
            report_data['elapsed_time_total'] = "N/A"

        # Load JSON content for detailed sections
        phases_data_from_context = self.context.get("phases", {})

        # Content Discovery JSON
        try:
            cd_output_file = phases_data_from_context.get("content_discovery", {}).get("output_file")
            if cd_output_file and os.path.exists(cd_output_file):
                with open(cd_output_file, "r", encoding="utf-8") as f:
                    report_data["content_discovery_json"] = f.read()
            else:
                report_data["content_discovery_json"] = "Content discovery data file not found or path missing in results."
                self.logger.warning(f"Content discovery JSON file path not found or invalid: {cd_output_file}")
        except Exception as e:
            self.logger.error(f"Error loading content_discovery.json for report: {e}")
            report_data["content_discovery_json"] = f"Error loading content discovery data: {str(e)}"

        # Cross-Reference Analysis JSON
        try:
            cra_output_file = phases_data_from_context.get("cross_reference_analysis", {}).get("output_file")
            if cra_output_file and os.path.exists(cra_output_file):
                with open(cra_output_file, "r", encoding="utf-8") as f:
                    report_data["cross_reference_analysis_json"] = f.read()
            else:
                report_data["cross_reference_analysis_json"] = "Cross-reference analysis data file not found or path missing in results."
                self.logger.warning(f"Cross-reference analysis JSON file path not found or invalid: {cra_output_file}")
        except Exception as e:
            self.logger.error(f"Error loading cross_reference_analysis.json for report: {e}")
            report_data["cross_reference_analysis_json"] = f"Error loading cross-reference analysis data: {str(e)}"

        # Consolidation Plan JSON
        try:
            cp_output_file = phases_data_from_context.get("consolidation_planning", {}).get("output_file")
            if cp_output_file and os.path.exists(cp_output_file):
                with open(cp_output_file, "r", encoding="utf-8") as f:
                    report_data["consolidation_plan_json"] = f.read()
            else:
                report_data["consolidation_plan_json"] = "Consolidation plan data file not found or path missing in results."
                self.logger.warning(f"Consolidation plan JSON file path not found or invalid: {cp_output_file}")
        except Exception as e:
            self.logger.error(f"Error loading consolidation_plan.json for report: {e}")
            report_data["consolidation_plan_json"] = f"Error loading consolidation plan data: {str(e)}"
            
        return report_data
    
    def _cleanup_old_reports(self) -> None:
        """Clean up old reports."""
        # Calculate retention period
        retention_period = datetime.timedelta(days=CONFIG["REPORT_RETENTION_DAYS"])
        
        # Get current date and time
        current_date = datetime.datetime.now()
        
        # Iterate over reports in the standard reports directory
        for report_dir in os.listdir(self.standard_reports_dir):
            report_path = os.path.join(self.standard_reports_dir, report_dir)
            
            # Check if the report is older than the retention period
            if os.path.isdir(report_path):
                report_date = datetime.datetime.strptime(report_dir, "report_%Y%m%d_%H%M%S")
                if current_date - report_date > retention_period:
                    shutil.rmtree(report_path)
                    self.logger.info(f"Removed old report: {report_path}")
    
    def _copy_reports_to_standard_location(self, html_report_path: str, md_report_path: str) -> None:
        """Copy reports to the standard location."""
        # Copy HTML report
        standard_html_report_path = os.path.join(self.report_dir, os.path.basename(html_report_path))
        shutil.copy2(html_report_path, standard_html_report_path)
        self.logger.info(f"Copied HTML report to standard location: {standard_html_report_path}")
        
        # Copy Markdown report
        standard_md_report_path = os.path.join(self.report_dir, os.path.basename(md_report_path))
        shutil.copy2(md_report_path, standard_md_report_path)
        self.logger.info(f"Copied Markdown report to standard location: {standard_md_report_path}")
    
    def generate_reports(self) -> Dict[str, str]:
        """Generate HTML and Markdown reports.
        
        Returns:
            Dict[str, str]: Dictionary with report file paths
        """
        self.logger.info("Generating reports")
        
        # Prepare report data
        report_data = self._prepare_report_data()
        
        # Generate HTML report
        html_report_path = self._generate_html_report(report_data)
        
        # Generate Markdown report
        md_report_path = self._generate_markdown_report(report_data)
        
        # Copy reports to standard location if output_dir is custom
        if self.output_dir != self.report_dir:
            self._copy_reports_to_standard_location(html_report_path, md_report_path)
        
        self.logger.info(f"Reports generated successfully in {self.output_dir}")
        self.logger.info(f"Standard reports location: {self.report_dir}")
        
        return {
            "html_report": html_report_path,
            "markdown_report": md_report_path,
            "standard_html_report": os.path.join(self.report_dir, os.path.basename(html_report_path)),
            "standard_markdown_report": os.path.join(self.report_dir, os.path.basename(md_report_path))
        }
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report.
        
        Args:
            report_data: Data for the report
            
        Returns:
            str: Path to the generated HTML report
        """
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(CONFIG["REPORT_TEMPLATE_DIR"]))
        template = env.get_template(CONFIG["HTML_TEMPLATE"])
        
        # Generate HTML content
        html_content = template.render(**report_data)
        
        # Write to file with standardized naming
        keyword = self.args.get("keyword", "general")
        html_report_path = os.path.join(self.output_dir, f"directory_unification_{keyword}_{self.timestamp}.html")
        
        with open(html_report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return html_report_path
        
    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown report.
        
        Args:
            report_data: Data for the report
            
        Returns:
            str: Path to the generated Markdown report
        """
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(CONFIG["REPORT_TEMPLATE_DIR"]))
        template = env.get_template(CONFIG["MD_TEMPLATE"])
        
        # Generate Markdown content
        md_content = template.render(**report_data)
        
        # Write to file with standardized naming
        keyword = self.args.get("keyword", "general")
        md_report_path = os.path.join(self.output_dir, f"directory_unification_{keyword}_{self.timestamp}.md")
        
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        return md_report_path
    
    def _cleanup_old_reports(self) -> None:
        """Clean up old reports based on retention policy."""
        try:
            if not os.path.exists(self.tool_reports_dir):
                return
                
            # Get current time
            now = datetime.datetime.now()
            retention_days = CONFIG["REPORT_RETENTION_DAYS"]
            
            # List all report directories
            for item in os.listdir(self.tool_reports_dir):
                item_path = os.path.join(self.tool_reports_dir, item)
                
                # Skip if not a directory or doesn't match the report pattern
                if not os.path.isdir(item_path) or not item.startswith("report_"):
                    continue
                    
                try:
                    # Extract timestamp from directory name
                    timestamp_str = item.replace("report_", "")
                    report_date = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # Check if older than retention period
                    age_days = (now - report_date).days
                    if age_days > retention_days:
                        self.logger.info(f"Removing old report directory: {item_path} (age: {age_days} days)")
                        shutil.rmtree(item_path)
                        
                except (ValueError, OSError) as e:
                    self.logger.warning(f"Error processing report directory {item}: {e}")
                    
            self.logger.info(f"Cleaned up reports older than {retention_days} days")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old reports: {e}")
            
    def _copy_reports_to_standard_location(self, html_report_path: str, md_report_path: str) -> None:
        """Copy reports to the standard location.
        
        Args:
            html_report_path: Path to the HTML report
            md_report_path: Path to the Markdown report
        """
        try:
            # Create standard report directory if it doesn't exist
            os.makedirs(self.report_dir, exist_ok=True)
            
            # Copy HTML report
            html_dest = os.path.join(self.report_dir, os.path.basename(html_report_path))
            shutil.copy2(html_report_path, html_dest)
            
            # Copy Markdown report
            md_dest = os.path.join(self.report_dir, os.path.basename(md_report_path))
            shutil.copy2(md_report_path, md_dest)
            
            self.logger.info(f"Reports copied to standard location: {self.report_dir}")
            
        except Exception as e:
            self.logger.error(f"Error copying reports to standard location: {e}")
    
    def _create_default_template(self, template_path: str) -> None:
        """
        Create a default HTML template if none exists.
        
        Args:
            template_path: Path to create the template at
        """
        logger.info(f"Creating default HTML template at {template_path}")
        
        # Basic HTML template with Bootstrap for styling
        template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding: 20px; }
        .report-header { margin-bottom: 30px; }
        .card { margin-bottom: 20px; }
        .chart-container { text-align: center; margin: 20px 0; }
        .table-container { margin-top: 20px; }
        .egos-signature { 
            text-align: center; 
            margin-top: 50px; 
            font-size: 1.2em; 
            color: #4e73df;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>{{ title }}</h1>
            <p class="text-muted">Generated on: {{ timestamp }}</p>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h2 class="card-title h5 mb-0">Summary</h2>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-group">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Keyword
                                        <span class="badge badge-primary badge-pill">{{ keyword }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Target Location
                                        <span class="badge badge-primary badge-pill">{{ summary.target_location }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Total Files Found
                                        <span class="badge badge-primary badge-pill">{{ summary.total_files_found }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Total Directories Found
                                        <span class="badge badge-primary badge-pill">{{ summary.total_directories_found }}</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-group">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Files to Unify
                                        <span class="badge badge-success badge-pill">{{ summary.files_to_unify }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Files to Preserve
                                        <span class="badge badge-info badge-pill">{{ summary.files_to_preserve }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Files to Archive
                                        <span class="badge badge-warning badge-pill">{{ summary.files_to_archive }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Files to Delete
                                        <span class="badge badge-danger badge-pill">{{ summary.files_to_delete }}</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        {% if has_visualization and charts %}
        <div class="row">
            {% if charts.file_classification %}
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h2 class="card-title h5 mb-0">File Classification</h2>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <img src="data:image/png;base64,{{ charts.file_classification }}" alt="File Classification Chart">
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
            
            {% if charts.migration_results %}
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h2 class="card-title h5 mb-0">Migration Results</h2>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <img src="data:image/png;base64,{{ charts.migration_results }}" alt="Migration Results Chart">
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h2 class="card-title h5 mb-0">Migration Results</h2>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-group">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Completed Steps
                                        <span class="badge badge-primary badge-pill">{{ summary.completed_steps }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Successful Steps
                                        <span class="badge badge-success badge-pill">{{ summary.successful_steps }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Failed Steps
                                        <span class="badge badge-danger badge-pill">{{ summary.failed_steps }}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Reference Updates
                                        <span class="badge badge-info badge-pill">{{ summary.reference_updates }}</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-group">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Backup Created
                                        <span class="badge badge-{{ summary.backup_created and 'success' or 'danger' }} badge-pill">
                                            {{ summary.backup_created and 'Yes' or 'No' }}
                                        </span>
                                    </li>
                                    {% if summary.backup_created %}
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Backup Location
                                        <span class="badge badge-primary badge-pill">{{ summary.backup_location }}</span>
                                    </li>
                                    {% endif %}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Successful Operations -->
        {% if migration and migration.successful_operations %}
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h2 class="card-title h5 mb-0">Successful Operations</h2>
                    </div>
                    <div class="card-body">
                        <div class="table-container">
                            <table class="table table-striped table-sm">
                                <thead>
                                    <tr>
                                        <th>Step ID</th>
                                        <th>Action</th>
                                        <th>Source Path</th>
                                        <th>Target Path</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for op in migration.successful_operations %}
                                    <tr>
                                        <td>{{ op.step_id }}</td>
                                        <td>{{ op.action }}</td>
                                        <td>{{ op.source_path }}</td>
                                        <td>{{ op.target_path or 'N/A' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Failed Operations -->
        {% if migration and migration.failed_operations %}
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-danger text-white">
                        <h2 class="card-title h5 mb-0">Failed Operations</h2>
                    </div>
                    <div class="card-body">
                        <div class="table-container">
                            <table class="table table-striped table-sm">
                                <thead>
                                    <tr>
                                        <th>Step ID</th>
                                        <th>Action</th>
                                        <th>Source Path</th>
                                        <th>Error</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for op in migration.failed_operations %}
                                    <tr>
                                        <td>{{ op.step_id }}</td>
                                        <td>{{ op.action }}</td>
                                        <td>{{ op.source_path }}</td>
                                        <td>{{ op.error }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="egos-signature">
            ✧༺❀༻∞ EGOS ∞༺❀༻✧
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""
        
        # Create the template directory if it doesn't exist
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        # Write the template
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template)


def main():
    """Main function for testing the ReportGenerator module."""
    import argparse
    import json
    
    # Print banner
    print_banner("Report Generator Module")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Report Generator Module for Directory Unification Tool")
    parser.add_argument("--content-file", required=True, help="Path to content discovery results JSON file")
    parser.add_argument("--references-file", required=True, help="Path to cross-reference analysis results JSON file")
    parser.add_argument("--plan-file", required=True, help="Path to consolidation plan JSON file")
    parser.add_argument("--migration-file", help="Path to migration results JSON file")
    parser.add_argument("--keyword", required=True, help="Keyword for consolidation")
    parser.add_argument("--output-dir", help="Output directory for reports")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    
    args = parser.parse_args()
    
    # Load content discovery results
    try:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading content file: {e}{Style.RESET_ALL}")
        return
    
    # Load cross-reference analysis results
    try:
        with open(args.references_file, "r", encoding="utf-8") as f:
            references = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading references file: {e}{Style.RESET_ALL}")
        return
    
    # Load consolidation plan
    try:
        with open(args.plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading plan file: {e}{Style.RESET_ALL}")
        return
    
    # Load migration results if provided
    migration = {}
    if args.migration_file:
        try:
            with open(args.migration_file, "r", encoding="utf-8") as f:
                migration = json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading migration file: {e}{Style.RESET_ALL}")
            return
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Create context
    context = {
        "content": content,
        "references": references,
        "plan": plan,
        "migration": migration
    }
    
    # Create ReportGenerator instance
    generator = ReportGenerator(args_dict, context)
    
    # Generate reports
    results = generator.generate_reports()
    
    # Display results
    if results["success"]:
        print(f"\n{Fore.GREEN}Reports generated successfully:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}HTML Report:{Style.RESET_ALL} {results['html_report']}")
        print(f"  {Fore.CYAN}Markdown Report:{Style.RESET_ALL} {results['markdown_report']}")
    else:
        print(f"\n{Fore.RED}Failed to generate reports{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    main()