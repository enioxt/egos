#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""KOIOS Chronicler Module - HTML Renderer

This module is responsible for rendering documentation as HTML, including:
- HTML report generation with styling
- Charts and visualizations for codebase statistics
- File and directory structure representation

Part of the KOIOS subsystem within EGOS.

Author: EGOS Team
Date Created: 2025-04-22
Last Modified: 2025-05-18

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

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class HTMLRenderer:
    """
    Renders documentation as HTML reports.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the HTMLRenderer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized HTML renderer")
    
    def render(self, documentation: Dict[str, Any], project_dir: str, output_dir: str) -> str:
        """
        Render documentation as an HTML report.
        
        Args:
            documentation: Dictionary containing generated documentation
            project_dir: Path to the analyzed project directory
            output_dir: Directory where the report should be saved
            
        Returns:
            Path to the generated HTML file
        """
        self.logger.info("Rendering HTML report...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on project name and timestamp
        project_name = os.path.basename(project_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chronicler_{project_name}_{timestamp}.html"
        output_path = os.path.join(output_dir, filename)
        
        # Generate HTML content
        html_content = self._generate_html(documentation, project_dir)
        
        # Write HTML to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"HTML report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error writing HTML report: {e}")
            raise
        
        return output_path
    
    def _generate_html(self, documentation: Dict[str, Any], project_dir: str) -> str:
        """
        Generate HTML content from documentation.
        
        Args:
            documentation: Dictionary containing generated documentation
            project_dir: Path to the analyzed project directory
            
        Returns:
            HTML content as string
        """
        # Extract data from documentation
        project_name = documentation.get("project_name", os.path.basename(project_dir))
        generation_date = documentation.get("generation_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        summary = documentation.get("summary", "No summary available.")
        structure_overview = documentation.get("structure_overview", "No structure overview available.")
        language_analysis = documentation.get("language_analysis", "No language analysis available.")
        recommendations = documentation.get("recommendations", "No recommendations available.")
        
        # Get raw analysis data for charts
        raw_analysis = documentation.get("raw_analysis", {})
        languages = raw_analysis.get("languages", {})
        
        # Generate language distribution data for chart
        language_data = self._prepare_language_chart_data(languages)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chronicler Report - {project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --accent-color: #e74c3c;
            --light-bg: #ecf0f1;
            --dark-bg: #34495e;
            --text-color: #333;
            --light-text: #f8f9fa;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            margin: 0;
            padding: 0;
            background-color: var(--light-bg);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background-color: var(--dark-bg);
            color: var(--light-text);
            padding: 20px;
            text-align: center;
        }}
        
        h1, h2, h3, h4 {{
            margin-top: 0;
        }}
        
        .card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        
        .card-header {{
            border-bottom: 1px solid var(--light-bg);
            margin-bottom: 15px;
            padding-bottom: 10px;
        }}
        
        .card-header h2 {{
            color: var(--primary-color);
            margin: 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        
        .stat-card h3 {{
            margin: 0;
            font-size: 2rem;
        }}
        
        .stat-card p {{
            margin: 5px 0 0;
            opacity: 0.8;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 20px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: var(--secondary-color);
            font-size: 0.9rem;
        }}
        
        pre {{
            background-color: var(--dark-bg);
            color: var(--light-text);
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        
        code {{
            font-family: 'Courier New', Courier, monospace;
        }}
        
        .recommendations {{
            background-color: #fff8dc;
            border-left: 4px solid var(--accent-color);
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .recommendations h3 {{
            color: var(--accent-color);
            margin-top: 0;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Chronicler Report</h1>
        <p>{project_name}</p>
    </header>
    
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2>Project Overview</h2>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{raw_analysis.get("file_count", 0)}</h3>
                    <p>Files</p>
                </div>
                <div class="stat-card">
                    <h3>{len(raw_analysis.get("directories", []))}</h3>
                    <p>Directories</p>
                </div>
                <div class="stat-card">
                    <h3>{len(languages)}</h3>
                    <p>Languages</p>
                </div>
                <div class="stat-card">
                    <h3>{raw_analysis.get("total_size", 0) / 1024:.1f} KB</h3>
                    <p>Total Size</p>
                </div>
            </div>
            
            <div class="section">
                <h3>Project Summary</h3>
                <p>{summary}</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>Language Distribution</h2>
            </div>
            <div class="chart-container">
                <canvas id="languageChart"></canvas>
            </div>
            <div class="section">
                <h3>Language Analysis</h3>
                <p>{language_analysis}</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>Project Structure</h2>
            </div>
            <div class="section">
                <p>{structure_overview}</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>Recommendations</h2>
            </div>
            <div class="recommendations">
                <p>{recommendations}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by KOIOS Chronicler on {generation_date}</p>
            <p>Part of the EGOS (Eva Guarani Operating System) Project</p>
        </div>
    </div>
    
    <script>
        // Language distribution chart
        const languageCtx = document.getElementById('languageChart').getContext('2d');
        const languageChart = new Chart(languageCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps([lang for lang in language_data["labels"]])},
                datasets: [{{
                    label: 'Files',
                    data: {json.dumps(language_data["counts"])},
                    backgroundColor: {json.dumps(language_data["colors"])},
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${{label}}: ${{value}} files (${{percentage}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        return html
    
    def _prepare_language_chart_data(self, languages: Dict[str, Dict[str, Any]]) -> Dict[str, List]:
        """
        Prepare language data for chart visualization.
        
        Args:
            languages: Dictionary containing language statistics
            
        Returns:
            Dictionary with labels, counts, and colors for chart
        """
        # Default colors for common languages
        language_colors = {
            "Python": "#3776AB",
            "JavaScript": "#F7DF1E",
            "TypeScript": "#3178C6",
            "HTML": "#E34F26",
            "CSS": "#1572B6",
            "Java": "#007396",
            "C#": "#239120",
            "C++": "#00599C",
            "Ruby": "#CC342D",
            "Go": "#00ADD8",
            "Rust": "#DEA584",
            "PHP": "#777BB4",
            "Swift": "#FA7343",
            "Kotlin": "#7F52FF",
            "Markdown": "#083fa1",
            "JSON": "#292929",
            "YAML": "#CB171E"
        }
        
        # Default color palette for other languages
        default_colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
            "#1abc9c", "#d35400", "#34495e", "#7f8c8d", "#27ae60",
            "#2980b9", "#8e44ad", "#c0392b", "#16a085", "#f1c40f"
        ]
        
        # Prepare data for chart
        labels = []
        counts = []
        colors = []
        color_index = 0
        
        # Sort languages by file count
        sorted_languages = sorted(
            languages.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        # Limit to top 10 languages, group others
        if len(sorted_languages) > 10:
            top_languages = sorted_languages[:9]
            other_count = sum(lang[1]["count"] for lang in sorted_languages[9:])
            
            for lang, stats in top_languages:
                labels.append(lang)
                counts.append(stats["count"])
                colors.append(language_colors.get(lang, default_colors[color_index % len(default_colors)]))
                color_index += 1
            
            # Add "Other" category
            if other_count > 0:
                labels.append("Other")
                counts.append(other_count)
                colors.append("#7f8c8d")  # Gray for "Other"
        else:
            # Use all languages
            for lang, stats in sorted_languages:
                labels.append(lang)
                counts.append(stats["count"])
                colors.append(language_colors.get(lang, default_colors[color_index % len(default_colors)]))
                color_index += 1
        
        return {
            "labels": labels,
            "counts": counts,
            "colors": colors
        }


# For testing
if __name__ == "__main__":
    import sys
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample documentation for testing
    sample_documentation = {
        "project_name": "sample_project",
        "project_path": "/path/to/sample_project",
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": "This is a sample project summary.",
        "structure_overview": "This is a sample structure overview.",
        "language_analysis": "This is a sample language analysis.",
        "recommendations": "These are sample recommendations.",
        "raw_analysis": {
            "file_count": 100,
            "directories": [{"path": "dir1"}, {"path": "dir2"}],
            "total_size": 1024 * 1024,  # 1 MB
            "languages": {
                "Python": {"count": 50, "size": 512 * 1024},
                "JavaScript": {"count": 30, "size": 256 * 1024},
                "HTML": {"count": 15, "size": 128 * 1024},
                "CSS": {"count": 5, "size": 128 * 1024}
            }
        }
    }
    
    print("This is a test module. Run main.py to generate a complete report.")