#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Cross-Reference Visualizer

This script visualizes cross-references across the EGOS ecosystem by creating
interactive network graphs and Mermaid diagrams. It works with the output from
the cross-reference validator to provide visual insights into document relationships.

Part of the EGOS Cross-Reference Standardization Initiative.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

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

# Standard library imports
import os
import re
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from collections import defaultdict

# Third-party imports
try:
    import networkx as nx
    from pyvis.network import Network
    import matplotlib.pyplot as plt
    HAVE_VISUALIZATION_LIBS = True
except ImportError:
    HAVE_VISUALIZATION_LIBS = False

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    if not 'Fore' in globals():
        Fore = DummyColorama()
    if not 'Style' in globals():
        Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
TERMINAL_WIDTH = 120

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("cross_reference_visualizer")

# Helper functions
def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (width - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (width - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (width-2)}╝{Style.RESET_ALL}")
    print()

def check_dependencies():
    """Check if required dependencies are installed."""
    if not HAVE_VISUALIZATION_LIBS:
        logger.error("Required visualization libraries are not installed.")
        logger.error("Please install them with: pip install networkx pyvis matplotlib")
        return False
    return True

class ReferenceVisualizer:
    """Cross-reference visualizer for EGOS documents."""
    
    def __init__(self, base_path: str, report_path: Optional[str] = None):
        """Initialize the reference visualizer.
        
        Args:
            base_path: Base path to process
            report_path: Path to the cross-reference validation report
        """
        self.base_path = Path(base_path)
        self.report_path = Path(report_path) if report_path else None
        
        # Create output directory
        self.output_dir = self.base_path / "docs" / "visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize graph
        self.graph = nx.DiGraph()
        
        # Reference data
        self.references = []
        self.files = set()
        
        # Node types and colors
        self.node_types = {
            ".md": {"color": "#3498db", "size": 25, "group": "Documentation"},
            ".py": {"color": "#2ecc71", "size": 20, "group": "Python"},
            ".js": {"color": "#f1c40f", "size": 20, "group": "JavaScript"},
            ".html": {"color": "#e74c3c", "size": 20, "group": "HTML"},
            ".css": {"color": "#9b59b6", "size": 20, "group": "CSS"},
            ".json": {"color": "#1abc9c", "size": 20, "group": "JSON"},
            ".txt": {"color": "#95a5a6", "size": 15, "group": "Text"},
            "default": {"color": "#7f8c8d", "size": 15, "group": "Other"}
        }
    
    def load_data_from_validator_report(self) -> bool:
        """Load reference data from a cross-reference validator report.
        
        Returns:
            True if data was loaded successfully, False otherwise
        """
        if not self.report_path or not self.report_path.exists():
            logger.error(f"Report file not found: {self.report_path}")
            return False
        
        try:
            # Parse the Markdown report
            with open(self.report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract invalid references from the report
            invalid_refs_section = re.search(r'## ⚠️ Files with Most Invalid References(.*?)##', content, re.DOTALL)
            if invalid_refs_section:
                invalid_refs_text = invalid_refs_section.group(1)
                
                # Parse the table
                table_rows = re.findall(r'\| (.*?) \| (\d+) \| (.*?) \|', invalid_refs_text)
                
                for file_path, count, details in table_rows:
                    # Extract references from details
                    refs = details.split("<br>")
                    for ref in refs:
                        if "->" in ref:
                            parts = ref.split("->")
                            if len(parts) == 2:
                                text = parts[0].strip()
                                target = parts[1].split("(")[0].strip()
                                
                                self.references.append({
                                    "source_file": file_path.strip(),
                                    "reference_text": text,
                                    "reference_target": target,
                                    "valid": False
                                })
            
            logger.info(f"Loaded {len(self.references)} references from the report")
            return True
        
        except Exception as e:
            logger.error(f"Error loading data from report: {str(e)}")
            return False
    
    def scan_files_for_references(self) -> bool:
        """Scan files for references directly.
        
        Returns:
            True if scanning was successful, False otherwise
        """
        try:
            # Find all files
            for root, _, filenames in os.walk(self.base_path):
                for filename in filenames:
                    file_path = Path(os.path.join(root, filename))
                    
                    # Check if it's a file we want to process
                    if file_path.suffix.lower() in ['.md', '.txt', '.py', '.js', '.html']:
                        self.files.add(file_path)
            
            logger.info(f"Found {len(self.files)} files to scan")
            
            # Extract references from files
            for file_path in self.files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Extract markdown links
                    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    for text, target in md_links:
                        # Skip external links
                        if not target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                            self.references.append({
                                "source_file": str(file_path),
                                "reference_text": text,
                                "reference_target": target,
                                "valid": True  # Assume valid for now
                            })
                
                except Exception as e:
                    logger.warning(f"Error processing {file_path}: {str(e)}")
            
            logger.info(f"Extracted {len(self.references)} references")
            return True
        
        except Exception as e:
            logger.error(f"Error scanning files: {str(e)}")
            return False
    
    def build_graph(self) -> None:
        """Build the reference graph."""
        # Add nodes for all files
        for file_path in self.files:
            try:
                rel_path = file_path.relative_to(self.base_path)
                
                # Determine node attributes based on file extension
                ext = file_path.suffix.lower()
                attrs = self.node_types.get(ext, self.node_types["default"])
                
                # Add node
                self.graph.add_node(
                    str(rel_path),
                    label=str(rel_path),
                    color=attrs["color"],
                    size=attrs["size"],
                    group=attrs["group"],
                    title=f"File: {rel_path}<br>Type: {attrs['group']}"
                )
            
            except Exception as e:
                logger.warning(f"Error adding node for {file_path}: {str(e)}")
        
        # Add edges for references
        for ref in self.references:
            try:
                source_file = Path(ref["source_file"])
                target_file = Path(ref["reference_target"])
                
                # Handle relative paths
                if not target_file.is_absolute():
                    target_file = source_file.parent / target_file
                
                # Try to make paths relative to base_path
                try:
                    source_rel = source_file.relative_to(self.base_path)
                except ValueError:
                    source_rel = source_file
                
                try:
                    target_rel = target_file.relative_to(self.base_path)
                except ValueError:
                    target_rel = target_file
                
                # Add edge
                self.graph.add_edge(
                    str(source_rel),
                    str(target_rel),
                    title=ref["reference_text"],
                    label=ref["reference_text"][:20] + "..." if len(ref["reference_text"]) > 20 else ref["reference_text"],
                    color="green" if ref.get("valid", True) else "red"
                )
            
            except Exception as e:
                logger.warning(f"Error adding edge for reference: {str(e)}")
    
    def create_interactive_visualization(self) -> Path:
        """Create an interactive HTML visualization of the reference graph.
        
        Returns:
            Path to the generated HTML file
        """
        # Create network
        net = Network(
            height="800px",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Add nodes and edges from NetworkX graph
        net.from_nx(self.graph)
        
        # Set options
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {
                    "enabled": true,
                    "iterations": 1000
                }
            },
            "edges": {
                "smooth": {
                    "type": "continuous",
                    "forceDirection": "none"
                },
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.5
                    }
                }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": true
            }
        }
        """)
        
        # Generate HTML file
        output_path = self.output_dir / "reference_graph.html"
        net.save_graph(str(output_path))
        
        logger.info(f"Interactive visualization saved to {output_path}")
        return output_path
    
    def create_mermaid_diagram(self) -> Path:
        """Create a Mermaid diagram of the reference graph.
        
        Returns:
            Path to the generated Markdown file with Mermaid diagram
        """
        # Create Mermaid diagram
        mermaid_lines = ["```mermaid", "graph TD;"]
        
        # Add nodes
        for node in self.graph.nodes():
            attrs = self.graph.nodes[node]
            node_id = node.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
            mermaid_lines.append(f'    {node_id}["{node}"];')
        
        # Add edges
        for source, target in self.graph.edges():
            source_id = source.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
            target_id = target.replace(" ", "_").replace(".", "_").replace("-", "_").replace("/", "_")
            mermaid_lines.append(f'    {source_id} --> {target_id};')
        
        mermaid_lines.append("```")
        
        # Write to file
        output_path = self.output_dir / "reference_mermaid.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# EGOS Cross-Reference Visualization\n\n")
            f.write("This diagram shows the relationships between documents in the EGOS ecosystem.\n\n")
            f.write("\n".join(mermaid_lines))
            f.write("\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Mermaid diagram saved to {output_path}")
        return output_path
    
    def create_summary_visualization(self) -> Path:
        """Create a summary visualization with statistics.
        
        Returns:
            Path to the generated HTML file
        """
        # Calculate statistics
        total_files = len(self.files)
        total_references = len(self.references)
        
        # Count references by file type
        refs_by_type = defaultdict(int)
        for ref in self.references:
            source_file = Path(ref["source_file"])
            ext = source_file.suffix.lower()
            refs_by_type[ext] += 1
        
        # Create HTML file
        output_path = self.output_dir / "reference_summary.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>EGOS Cross-Reference Summary</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1, h2 {
                        color: #333;
                    }
                    .card {
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                        padding: 15px;
                        margin-bottom: 20px;
                    }
                    .stat {
                        font-size: 24px;
                        font-weight: bold;
                        color: #3498db;
                    }
                    .footer {
                        margin-top: 30px;
                        text-align: center;
                        color: #777;
                    }
                    .chart-container {
                        width: 100%;
                        height: 400px;
                    }
                </style>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <div class="container">
                    <h1>EGOS Cross-Reference Summary</h1>
                    
                    <div class="card">
                        <h2>Overview</h2>
                        <p>Total Files: <span class="stat">""" + str(total_files) + """</span></p>
                        <p>Total References: <span class="stat">""" + str(total_references) + """</span></p>
                        <p>Average References per File: <span class="stat">""" + str(round(total_references / total_files if total_files > 0 else 0, 2)) + """</span></p>
                    </div>
                    
                    <div class="card">
                        <h2>References by File Type</h2>
                        <div class="chart-container">
                            <canvas id="referencesByTypeChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Generated by EGOS Cross-Reference Visualizer</p>
                        <p>✧༺❀༻∞ EGOS ∞༺❀༻✧</p>
                    </div>
                </div>
                
                <script>
                    // References by file type chart
                    const typeCtx = document.getElementById('referencesByTypeChart').getContext('2d');
                    const typeChart = new Chart(typeCtx, {
                        type: 'bar',
                        data: {
                            labels: [""" + ", ".join([f"'{k}'" for k in refs_by_type.keys()]) + """],
                            datasets: [{
                                label: 'Number of References',
                                data: [""" + ", ".join([str(v) for v in refs_by_type.values()]) + """],
                                backgroundColor: [
                                    '#3498db',
                                    '#2ecc71',
                                    '#f1c40f',
                                    '#e74c3c',
                                    '#9b59b6',
                                    '#1abc9c',
                                    '#95a5a6',
                                    '#7f8c8d'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                </script>
            </body>
            </html>
            """)
        
        logger.info(f"Summary visualization saved to {output_path}")
        return output_path
    
    def run(self) -> Dict[str, Path]:
        """Run the reference visualizer.
        
        Returns:
            Dictionary with paths to generated visualizations
        """
        outputs = {}
        
        # Load data
        if self.report_path:
            self.load_data_from_validator_report()
        else:
            self.scan_files_for_references()
        
        # Build graph
        self.build_graph()
        
        # Create visualizations
        outputs["interactive"] = self.create_interactive_visualization()
        outputs["mermaid"] = self.create_mermaid_diagram()
        outputs["summary"] = self.create_summary_visualization()
        
        return outputs

def main():
    """Main entry point for the script."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Visualize cross-references across the EGOS ecosystem.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Visualize references in the current directory
  python cross_reference_visualizer.py
  
  # Visualize references from a validation report
  python cross_reference_visualizer.py --report-path /path/to/report.md
  
  # Visualize references in a specific directory
  python cross_reference_visualizer.py --base-path /path/to/directory

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(), help="Base path to process")
    parser.add_argument("--report-path", type=str, help="Path to the cross-reference validation report")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner(
        "EGOS Cross-Reference Visualizer",
        f"Visualizing references in {args.base_path}"
    )
    
    # Create and run the reference visualizer
    visualizer = ReferenceVisualizer(
        base_path=args.base_path,
        report_path=args.report_path
    )
    
    try:
        outputs = visualizer.run()
        
        # Display results
        logger.info(f"\n{Fore.GREEN}Reference visualization completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Interactive visualization:{Style.RESET_ALL} {outputs['interactive']}")
        logger.info(f"  • {Fore.CYAN}Mermaid diagram:{Style.RESET_ALL} {outputs['mermaid']}")
        logger.info(f"  • {Fore.CYAN}Summary visualization:{Style.RESET_ALL} {outputs['summary']}")
        
        # Suggest next steps
        print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
        print(f"1. Open the interactive visualization in a web browser")
        print(f"2. Review the Mermaid diagram for document relationships")
        print(f"3. Analyze the summary visualization for reference statistics")
        
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running reference visualizer: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()