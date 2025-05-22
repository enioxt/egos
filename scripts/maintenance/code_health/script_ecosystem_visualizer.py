#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Script Ecosystem Visualizer

This script generates interactive visualizations of the EGOS script ecosystem,
including script relationships, dependencies, and status information. It integrates
with the script validator to provide a comprehensive view of the system's architecture.

Features:
- Interactive network graph of script relationships
- Script capability matrix visualization
- Subsystem organization visualization
- Health metrics visualization

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md
- C:\EGOS\scripts\maintenance\code_health\script_validator.py
- C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
- C:\EGOS\scripts\cross_reference\cross_reference_visualizer.py

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable

# Try to import visualization libraries with graceful fallbacks
try:
    import networkx as nx
    from pyvis.network import Network
    HAVE_NETWORKX = True
except ImportError:
    HAVE_NETWORKX = False
    print("Warning: NetworkX or PyVis not installed. Network visualization will be limited.")
    print("To install: pip install networkx pyvis")

try:
    import matplotlib.pyplot as plt
    HAVE_MATPLOTLIB = True
except ImportError:
    HAVE_MATPLOTLIB = False
    print("Warning: Matplotlib not installed. Some visualizations will be disabled.")
    print("To install: pip install matplotlib")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "script_ecosystem_visualizer.log")
    ]
)
logger = logging.getLogger("script_ecosystem_visualizer")


class ScriptEcosystemVisualizer:
    """
    Generates visualizations of the EGOS script ecosystem.
    
    This class analyzes script validation results and creates various visualizations
    to help understand the ecosystem structure, relationships, and health metrics.
    """
    
    def __init__(self, validation_results_path: Path, output_dir: Path):
        """
        Initialize the visualizer.
        
        Args:
            validation_results_path: Path to the script validation results JSON file
            output_dir: Directory to save visualization outputs
        """
        self.validation_results_path = validation_results_path
        self.output_dir = output_dir
        self.validation_results = None
        self.script_data = {}
        self.subsystem_data = {}
        self.graph = None
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ensure required visualization libraries are available
        self.network_viz_available = HAVE_NETWORKX
        self.chart_viz_available = HAVE_MATPLOTLIB
        
        logger.info(f"Script Ecosystem Visualizer initialized with output to {output_dir}")
    
    def load_validation_results(self) -> bool:
        """
        Load script validation results from JSON file.
        
        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            if not self.validation_results_path.exists():
                logger.error(f"Validation results file not found: {self.validation_results_path}")
                return False
            
            with open(self.validation_results_path, 'r', encoding='utf-8') as f:
                self.validation_results = json.load(f)
            
            logger.info(f"Loaded validation results for {len(self.validation_results['script_results'])} scripts")
            return True
        except Exception as e:
            logger.error(f"Error loading validation results: {str(e)}")
            return False
    
    def process_script_data(self) -> None:
        """
        Process validation results into structured data for visualization.
        """
        if not self.validation_results:
            logger.error("No validation results loaded")
            return
        
        # Process script results
        for script in self.validation_results['script_results']:
            path = script['path']
            rel_path = os.path.relpath(path, self.validation_results['root_path'])
            
            # Extract script data
            self.script_data[path] = {
                'path': path,
                'rel_path': rel_path,
                'valid_syntax': script.get('valid_syntax', False),
                'has_docstring': script.get('has_docstring', False),
                'has_type_hints': script.get('has_type_hints', False),
                'line_count': script.get('line_count', 0),
                'references': script.get('references', []),
                'imports': script.get('imports', []),
                'issues': script.get('issues', []),
                'subsystem': self._determine_subsystem(path)
            }
        
        # Process subsystem statistics
        for subsystem, stats in self.validation_results['statistics']['subsystems'].items():
            self.subsystem_data[subsystem] = stats
        
        logger.info(f"Processed data for {len(self.script_data)} scripts across {len(self.subsystem_data)} subsystems")
    
    def _determine_subsystem(self, path: str) -> str:
        """
        Determine which subsystem a script belongs to.
        
        Args:
            path: Path to the script
            
        Returns:
            Name of the subsystem
        """
        rel_path = os.path.relpath(path, self.validation_results['root_path'])
        parts = rel_path.split(os.sep)
        
        if len(parts) < 2:
            return "root"
        
        if parts[0] == "scripts":
            if len(parts) < 3:
                return parts[1]
            else:
                return f"{parts[1]}/{parts[2]}"
        elif parts[0] == "subsystems":
            return parts[1]
        else:
            return parts[0]
    
    def build_dependency_graph(self) -> None:
        """
        Build a directed graph representing script dependencies and references.
        """
        if not HAVE_NETWORKX:
            logger.warning("NetworkX not available, skipping graph generation")
            return
        
        if not self.script_data:
            logger.error("No script data processed")
            return
        
        # Create directed graph
        self.graph = nx.DiGraph()
        
        # Add nodes (scripts)
        for path, data in self.script_data.items():
            rel_path = data['rel_path']
            subsystem = data['subsystem']
            
            # Add node with attributes
            self.graph.add_node(
                rel_path,
                valid=data['valid_syntax'],
                has_docstring=data['has_docstring'],
                has_type_hints=data['has_type_hints'],
                lines=data['line_count'],
                subsystem=subsystem,
                issues=len(data['issues'])
            )
        
        # Add edges (references between scripts)
        for path, data in self.script_data.items():
            source = data['rel_path']
            
            # Add edges for references
            for ref in data['references']:
                # Convert reference to relative path if it's a file path
                if os.path.isabs(ref) and os.path.exists(ref):
                    ref_rel = os.path.relpath(ref, self.validation_results['root_path'])
                    if ref_rel in [d['rel_path'] for d in self.script_data.values()]:
                        self.graph.add_edge(source, ref_rel, type='reference')
        
        logger.info(f"Built dependency graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def create_network_visualization(self) -> Path:
        """
        Create an interactive network visualization of the script ecosystem.
        
        Returns:
            Path to the generated HTML file
        """
        if not HAVE_NETWORKX:
            logger.warning("NetworkX not available, skipping network visualization")
            return None
        
        if not self.graph:
            logger.error("No graph built, run build_dependency_graph first")
            return None
        
        # Create PyVis network
        net = Network(height="900px", width="100%", directed=True, notebook=False)
        
        # Define node colors based on subsystem and status
        subsystem_colors = {
            "cross_reference": "#3498db",  # Blue
            "system_monitor": "#2ecc71",   # Green
            "maintenance": "#e74c3c",      # Red
            "migrations": "#f39c12",       # Orange
            "nexus": "#9b59b6"             # Purple
        }
        
        # Default color for other subsystems
        default_color = "#95a5a6"  # Gray
        
        # Add nodes with attributes
        for node, attrs in self.graph.nodes(data=True):
            subsystem = attrs['subsystem']
            
            # Determine color based on subsystem and validity
            base_color = None
            for key, color in subsystem_colors.items():
                if key in subsystem:
                    base_color = color
                    break
            
            if base_color is None:
                base_color = default_color
            
            # If the script has issues, adjust the color intensity
            if attrs['issues'] > 0:
                # Create a lighter version of the color
                color = base_color + "80"  # Add 50% transparency
            else:
                color = base_color
            
            # Set node size based on line count
            size = min(50, max(15, attrs['lines'] / 100))
            
            # Add node with title showing details
            title = f"<b>{node}</b><br>"
            title += f"Subsystem: {subsystem}<br>"
            title += f"Lines: {attrs['lines']}<br>"
            title += f"Valid: {'Yes' if attrs['valid'] else 'No'}<br>"
            title += f"Docstring: {'Yes' if attrs['has_docstring'] else 'No'}<br>"
            title += f"Type Hints: {'Yes' if attrs['has_type_hints'] else 'No'}<br>"
            title += f"Issues: {attrs['issues']}"
            
            net.add_node(node, title=title, color=color, size=size)
        
        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            net.add_edge(source, target)
        
        # Set physics options for better visualization
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -100,
              "centralGravity": 0.15,
              "springLength": 100,
              "springConstant": 0.08
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
              "iterations": 100
            }
          },
          "interaction": {
            "navigationButtons": true,
            "keyboard": {
              "enabled": true
            }
          }
        }
        """)
        
        # Save visualization
        output_file = self.output_dir / "script_ecosystem_network.html"
        net.save_graph(str(output_file))
        logger.info(f"Created network visualization: {output_file}")
        
        return output_file
    
    def create_subsystem_chart(self) -> Path:
        """
        Create a chart showing script distribution and health by subsystem.
        
        Returns:
            Path to the generated chart image
        """
        if not HAVE_MATPLOTLIB:
            logger.warning("Matplotlib not available, skipping subsystem chart")
            return None
        
        if not self.subsystem_data:
            logger.error("No subsystem data processed")
            return None
        
        # Prepare data
        subsystems = []
        valid_counts = []
        invalid_counts = []
        
        # Get top 10 subsystems by total script count
        sorted_subsystems = sorted(
            self.subsystem_data.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]
        
        for subsystem, stats in sorted_subsystems:
            subsystems.append(subsystem)
            valid_counts.append(stats['valid'])
            invalid_counts.append(stats['invalid'])
        
        # Create stacked bar chart
        plt.figure(figsize=(12, 8))
        
        # Plot bars
        bar_width = 0.8
        bars = plt.bar(subsystems, valid_counts, bar_width, label='Valid Scripts', color='#2ecc71')
        bars = plt.bar(subsystems, invalid_counts, bar_width, bottom=valid_counts, label='Invalid Scripts', color='#e74c3c')
        
        # Add labels and title
        plt.xlabel('Subsystem')
        plt.ylabel('Script Count')
        plt.title('Script Distribution and Health by Subsystem')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart
        output_file = self.output_dir / "subsystem_distribution.png"
        plt.savefig(output_file)
        logger.info(f"Created subsystem chart: {output_file}")
        
        return output_file
    
    def create_issue_chart(self) -> Path:
        """
        Create a chart showing distribution of script issues.
        
        Returns:
            Path to the generated chart image
        """
        if not HAVE_MATPLOTLIB:
            logger.warning("Matplotlib not available, skipping issue chart")
            return None
        
        if not self.validation_results:
            logger.error("No validation results loaded")
            return None
        
        # Prepare data
        issues = self.validation_results['statistics']['issues_by_type']
        if not issues:
            logger.warning("No issues found in validation results")
            return None
        
        # Sort issues by count
        sorted_issues = sorted(issues.items(), key=lambda x: x[1], reverse=True)
        issue_types = [item[0] for item in sorted_issues]
        issue_counts = [item[1] for item in sorted_issues]
        
        # Create bar chart
        plt.figure(figsize=(12, 8))
        
        # Plot bars
        bars = plt.bar(issue_types, issue_counts, color='#3498db')
        
        # Add labels and title
        plt.xlabel('Issue Type')
        plt.ylabel('Count')
        plt.title('Distribution of Script Issues')
        plt.xticks(rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.5,
                f'{int(height)}',
                ha='center',
                va='bottom'
            )
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart
        output_file = self.output_dir / "issue_distribution.png"
        plt.savefig(output_file)
        logger.info(f"Created issue chart: {output_file}")
        
        return output_file
    
    def create_ecosystem_json(self) -> Path:
        """
        Create a JSON representation of the script ecosystem for frontend integration.
        
        Returns:
            Path to the generated JSON file
        """
        if not self.script_data:
            logger.error("No script data processed")
            return None
        
        # Create structured data for frontend
        ecosystem_data = {
            "scripts": [],
            "subsystems": [],
            "relationships": [],
            "statistics": self.validation_results['statistics']
        }
        
        # Add scripts
        for path, data in self.script_data.items():
            script_info = {
                "id": data['rel_path'],
                "path": data['path'],
                "rel_path": data['rel_path'],
                "subsystem": data['subsystem'],
                "valid": data['valid_syntax'],
                "has_docstring": data['has_docstring'],
                "has_type_hints": data['has_type_hints'],
                "line_count": data['line_count'],
                "issues": data['issues'],
                "references": data['references'],
                "imports": data['imports']
            }
            ecosystem_data["scripts"].append(script_info)
        
        # Add subsystems
        for subsystem, stats in self.subsystem_data.items():
            subsystem_info = {
                "id": subsystem,
                "name": subsystem,
                "total": stats['total'],
                "valid": stats['valid'],
                "invalid": stats['invalid'],
                "valid_percentage": stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
            }
            ecosystem_data["subsystems"].append(subsystem_info)
        
        # Add relationships (if graph is available)
        if self.graph:
            for source, target, attrs in self.graph.edges(data=True):
                relationship = {
                    "source": source,
                    "target": target,
                    "type": attrs.get('type', 'reference')
                }
                ecosystem_data["relationships"].append(relationship)
        
        # Save JSON
        output_file = self.output_dir / "script_ecosystem.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ecosystem_data, f, indent=2)
        
        logger.info(f"Created ecosystem JSON: {output_file}")
        return output_file
    
    def create_html_dashboard(self, network_path: Optional[Path] = None, 
                              subsystem_chart_path: Optional[Path] = None,
                              issue_chart_path: Optional[Path] = None) -> Path:
        """
        Create a simple HTML dashboard integrating all visualizations.
        
        Args:
            network_path: Path to the network visualization HTML
            subsystem_chart_path: Path to the subsystem chart image
            issue_chart_path: Path to the issue chart image
            
        Returns:
            Path to the generated HTML dashboard
        """
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGOS Script Ecosystem Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #3498db;
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .stats-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            width: 23%;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin-top: 0;
            color: #333;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .chart-container {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .chart-container h2 {{
            margin-top: 0;
            color: #333;
        }}
        .chart-image {{
            width: 100%;
            max-width: 100%;
            height: auto;
        }}
        .network-container {{
            height: 800px;
            width: 100%;
            border: none;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EGOS Script Ecosystem Dashboard</h1>
        <p>Generated on {self.validation_results['timestamp']}</p>
    </div>
    
    <div class="container">
        <div class="stats-container">
            <div class="stat-card">
                <h3>Total Scripts</h3>
                <div class="value">{self.validation_results['statistics']['total_scripts']}</div>
            </div>
            <div class="stat-card">
                <h3>Valid Scripts</h3>
                <div class="value">{self.validation_results['statistics']['total_valid']}</div>
            </div>
            <div class="stat-card">
                <h3>Invalid Scripts</h3>
                <div class="value">{self.validation_results['statistics']['total_invalid']}</div>
            </div>
            <div class="stat-card">
                <h3>Valid Percentage</h3>
                <div class="value">{self.validation_results['statistics']['valid_percentage']}%</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Subsystem Distribution</h2>
            {f'<img src="{os.path.basename(subsystem_chart_path)}" class="chart-image" alt="Subsystem Distribution">' if subsystem_chart_path else '<p>Subsystem chart not available</p>'}
        </div>
        
        <div class="chart-container">
            <h2>Issue Distribution</h2>
            {f'<img src="{os.path.basename(issue_chart_path)}" class="chart-image" alt="Issue Distribution">' if issue_chart_path else '<p>Issue chart not available</p>'}
        </div>
        
        <div class="chart-container">
            <h2>Script Ecosystem Network</h2>
            {f'<iframe src="{os.path.basename(network_path)}" class="network-container"></iframe>' if network_path else '<p>Network visualization not available</p>'}
        </div>
    </div>
    
    <div class="footer">
        <p>EGOS Script Ecosystem Visualizer | Version 1.0.0</p>
    </div>
</body>
</html>
"""
        
        # Save HTML
        output_file = self.output_dir / "script_ecosystem_dashboard.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Created HTML dashboard: {output_file}")
        return output_file
    
    def generate_visualizations(self) -> Dict[str, Path]:
        """
        Generate all visualizations.
        
        Returns:
            Dictionary with paths to generated visualizations
        """
        results = {}
        
        # Load data
        if not self.load_validation_results():
            return results
        
        # Process data
        self.process_script_data()
        
        # Build dependency graph
        self.build_dependency_graph()
        
        # Create visualizations
        network_path = self.create_network_visualization()
        if network_path:
            results['network'] = network_path
        
        subsystem_chart_path = self.create_subsystem_chart()
        if subsystem_chart_path:
            results['subsystem_chart'] = subsystem_chart_path
        
        issue_chart_path = self.create_issue_chart()
        if issue_chart_path:
            results['issue_chart'] = issue_chart_path
        
        ecosystem_json_path = self.create_ecosystem_json()
        if ecosystem_json_path:
            results['ecosystem_json'] = ecosystem_json_path
        
        # Create dashboard
        dashboard_path = self.create_html_dashboard(
            network_path, subsystem_chart_path, issue_chart_path
        )
        if dashboard_path:
            results['dashboard'] = dashboard_path
        
        return results


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EGOS Script Ecosystem Visualizer')
    parser.add_argument('--input', type=str, default=None,
                        help='Path to the script validation results JSON file')
    parser.add_argument('--output', type=str, default='C:\\EGOS\\docs\\visualizations',
                        help='Output directory for visualizations')
    parser.add_argument('--run-validator', action='store_true',
                        help='Run the script validator before generating visualizations')
    parser.add_argument('--validator-root', type=str, default='C:\\EGOS\\scripts',
                        help='Root directory for script validator if --run-validator is specified')
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    # Run validator if requested
    if args.run_validator:
        import subprocess
        import tempfile
        
        # Create temporary file for validation results
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Run validator with JSON output
        logger.info(f"Running script validator on {args.validator_root}")
        try:
            subprocess.run([
                sys.executable,
                str(Path(__file__).parent / "script_validator.py"),
                "--root", args.validator_root,
                "--output", str(Path(tmp_path).parent),
                "--format", "json"
            ], check=True)
            
            # Use generated results
            input_path = Path(tmp_path.replace('.json', '_report.json'))
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running script validator: {e}")
            return 1
    else:
        # Use provided input path
        if not args.input:
            logger.error("No input file specified and --run-validator not used")
            return 1
        input_path = Path(args.input)
    
    # Create visualizer
    visualizer = ScriptEcosystemVisualizer(input_path, output_dir)
    
    # Generate visualizations
    results = visualizer.generate_visualizations()
    
    # Print results
    if results:
        print(f"\nGenerated {len(results)} visualizations:")
        for name, path in results.items():
            print(f"- {name}: {path}")
    else:
        print("No visualizations were generated")
    
    # Clean up temporary file if used
    if args.run_validator and 'tmp_path' in locals():
        try:
            os.unlink(tmp_path)
        except:
            pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
