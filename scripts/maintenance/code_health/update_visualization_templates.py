#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Visualization Template Updater

This script updates all visualization HTML templates in the EGOS ecosystem to ensure
they follow the standardized EGOS website format. It identifies HTML files used for
visualization and updates them to use the EGOS HTML template structure.

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md
- C:\EGOS\scripts\templates\egos_html_template.html
- C:\EGOS\scripts\maintenance\code_health\script_ecosystem_visualizer.py
- C:\EGOS\scripts\cross_reference\cross_reference_visualizer.py

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0
"""

import os
import sys
import re
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "update_visualization_templates.log")
    ]
)
logger = logging.getLogger("update_visualization_templates")

# Define constants
DEFAULT_TEMPLATE_PATH = Path("C:\\EGOS\\scripts\\templates\\egos_html_template.html")


class VisualizationTemplateUpdater:
    """
    Updates visualization HTML templates to follow EGOS website standards.
    """
    
    def __init__(self, root_path: Path, template_path: Path, exclude_dirs: List[str] = None, dry_run: bool = False):
        """
        Initialize the template updater.
        
        Args:
            root_path: Base directory to search for HTML files
            template_path: Path to the EGOS HTML template
            exclude_dirs: Directories to exclude from scanning
            dry_run: If True, only show what would be changed without making changes
        """
        self.root_path = root_path
        self.template_path = template_path
        self.exclude_dirs = exclude_dirs or ["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"]
        self.dry_run = dry_run
        self.stats = {
            "total_html_files": 0,
            "visualization_files": 0,
            "updated_files": 0,
            "skipped_files": 0,
            "error_files": 0
        }
        
        # Load template
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.template_content = f.read()
            logger.info(f"Loaded template from {self.template_path}")
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            self.template_content = None
        
        logger.info(f"Visualization Template Updater initialized with root: {root_path}, dry_run: {dry_run}")
    
    def find_html_files(self) -> List[Path]:
        """
        Find all HTML files in the specified directory.
        
        Returns:
            List of paths to HTML files
        """
        html_files = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.html'):
                    html_files.append(Path(root) / file)
        
        logger.info(f"Found {len(html_files)} HTML files to check")
        self.stats["total_html_files"] = len(html_files)
        return html_files
    
    def is_visualization_file(self, file_path: Path) -> bool:
        """
        Determine if an HTML file is a visualization file.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            True if the file is a visualization file, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for visualization-related keywords
            viz_keywords = [
                "chart", "graph", "visualization", "dashboard", "network",
                "d3.js", "chart.js", "plotly", "vis.js", "pyvis", "ecosystem"
            ]
            
            for keyword in viz_keywords:
                if keyword.lower() in content.lower():
                    self.stats["visualization_files"] += 1
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking visualization file {file_path}: {str(e)}")
            return False
    
    def extract_content_sections(self, content: str) -> Dict[str, str]:
        """
        Extract content sections from an HTML file.
        
        Args:
            content: HTML content
            
        Returns:
            Dictionary of extracted sections
        """
        sections = {
            "title": "EGOS Visualization",
            "subtitle": "Generated by EGOS Ecosystem",
            "main_content": "",
            "header_scripts": "",
            "footer_scripts": "",
            "custom_styles": "",
            "version": "1.0.0"
        }
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            sections["title"] = title_match.group(1)
        
        # Extract header scripts
        header_scripts = []
        script_tags = re.findall(r'<script.*?>.*?</script>', content, re.DOTALL | re.IGNORECASE)
        for script in script_tags:
            if "body" not in content[:content.find(script)].lower():
                header_scripts.append(script)
        
        if header_scripts:
            sections["header_scripts"] = "\n    ".join(header_scripts)
        
        # Extract footer scripts
        footer_scripts = []
        for script in script_tags:
            if "body" in content[:content.find(script)].lower():
                footer_scripts.append(script)
        
        if footer_scripts:
            sections["footer_scripts"] = "\n    ".join(footer_scripts)
        
        # Extract style tags
        style_tags = re.findall(r'<style.*?>.*?</style>', content, re.DOTALL | re.IGNORECASE)
        if style_tags:
            styles = "\n".join([style.replace('<style>', '').replace('</style>', '') for style in style_tags])
            sections["custom_styles"] = styles
        
        # Extract main content
        body_match = re.search(r'<body.*?>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
            
            # Extract h1 for title and subtitle if not already found
            h1_match = re.search(r'<h1.*?>(.*?)</h1>', body_content, re.IGNORECASE)
            if h1_match and "title" not in title_match.group(1).lower() if title_match else True:
                sections["title"] = h1_match.group(1)
                
                # Look for subtitle (p after h1)
                subtitle_match = re.search(r'<h1.*?>.*?</h1>.*?<p.*?>(.*?)</p>', body_content, re.DOTALL | re.IGNORECASE)
                if subtitle_match:
                    sections["subtitle"] = subtitle_match.group(1)
            
            # Clean up main content (remove header/footer)
            main_content = body_content
            
            # Remove potential headers
            header_match = re.search(r'<header.*?>.*?</header>', main_content, re.DOTALL | re.IGNORECASE)
            if header_match:
                main_content = main_content.replace(header_match.group(0), '')
            
            # Remove potential footers
            footer_match = re.search(r'<footer.*?>.*?</footer>', main_content, re.DOTALL | re.IGNORECASE)
            if footer_match:
                main_content = main_content.replace(footer_match.group(0), '')
            
            sections["main_content"] = main_content.strip()
        
        return sections
    
    def apply_template(self, sections: Dict[str, str]) -> str:
        """
        Apply the EGOS template to the extracted sections.
        
        Args:
            sections: Dictionary of content sections
            
        Returns:
            Updated HTML content
        """
        if not self.template_content:
            logger.error("Template content not available")
            return ""
        
        # Replace placeholders in template
        content = self.template_content
        
        # Replace basic placeholders
        content = content.replace("{{TITLE}}", sections["title"])
        content = content.replace("{{SUBTITLE}}", sections["subtitle"])
        content = content.replace("{{MAIN_CONTENT}}", sections["main_content"])
        content = content.replace("{{HEADER_SCRIPTS}}", sections["header_scripts"])
        content = content.replace("{{FOOTER_SCRIPTS}}", sections["footer_scripts"])
        content = content.replace("{{CUSTOM_STYLES}}", sections["custom_styles"])
        content = content.replace("{{VERSION}}", sections["version"])
        content = content.replace("{{GENERATION_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return content
    
    def update_html_file(self, file_path: Path) -> bool:
        """
        Update an HTML file to use the EGOS template.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            True if the file was updated, False otherwise
        """
        if not self.is_visualization_file(file_path):
            logger.info(f"Skipping non-visualization file: {file_path}")
            self.stats["skipped_files"] += 1
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract content sections
            sections = self.extract_content_sections(content)
            
            # Apply template
            updated_content = self.apply_template(sections)
            
            if not updated_content:
                logger.error(f"Failed to apply template to {file_path}")
                self.stats["error_files"] += 1
                return False
            
            if self.dry_run:
                logger.info(f"Would update {file_path}")
                return True
            
            # Backup original file
            backup_path = file_path.with_suffix('.html.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"Updated {file_path}")
            self.stats["updated_files"] += 1
            return True
        
        except Exception as e:
            logger.error(f"Error updating {file_path}: {str(e)}")
            self.stats["error_files"] += 1
            return False
    
    def update_all_html_files(self) -> Dict[str, Any]:
        """
        Update all HTML files in the specified directory.
        
        Returns:
            Dictionary with update statistics
        """
        html_files = self.find_html_files()
        
        for html_file in html_files:
            logger.info(f"Checking {html_file}")
            self.update_html_file(html_file)
        
        return self.stats
    
    def generate_report(self) -> str:
        """
        Generate a report of the update process.
        
        Returns:
            Report as a string
        """
        report = []
        report.append("# Visualization Template Update Report")
        report.append(f"\nDry Run: {self.dry_run}")
        report.append(f"\nRoot Directory: {self.root_path}")
        report.append(f"\nTemplate: {self.template_path}")
        
        # Add statistics
        report.append("\n## Statistics")
        report.append(f"\n- Total HTML Files: {self.stats['total_html_files']}")
        report.append(f"- Visualization Files: {self.stats['visualization_files']}")
        report.append(f"- Updated Files: {self.stats['updated_files']}")
        report.append(f"- Skipped Files: {self.stats['skipped_files']}")
        report.append(f"- Error Files: {self.stats['error_files']}")
        
        # Calculate coverage percentage
        if self.stats['visualization_files'] > 0:
            coverage = (self.stats['updated_files'] / self.stats['visualization_files']) * 100
        else:
            coverage = 0
        report.append(f"\n\nVisualization Template Coverage: {coverage:.2f}%")
        
        return "\n".join(report)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EGOS Visualization Template Updater')
    parser.add_argument('--root', type=str, default='C:\\EGOS\\docs\\visualizations',
                        help='Root directory to search for HTML files')
    parser.add_argument('--template', type=str, default=str(DEFAULT_TEMPLATE_PATH),
                        help='Path to the EGOS HTML template')
    parser.add_argument('--output', type=str, default='C:\\EGOS\\docs\\reports',
                        help='Output directory for reports')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--exclude', type=str, nargs='+',
                        default=["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"],
                        help='Directories to exclude from scanning')
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    root_path = Path(args.root)
    template_path = Path(args.template)
    output_path = Path(args.output)
    
    if not root_path.exists():
        logger.error(f"Root directory {root_path} does not exist")
        return 1
    
    if not template_path.exists():
        logger.error(f"Template file {template_path} does not exist")
        return 1
    
    if not output_path.exists():
        logger.info(f"Creating output directory {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Updating visualization templates in {root_path}")
    
    # Create updater
    updater = VisualizationTemplateUpdater(
        root_path=root_path,
        template_path=template_path,
        exclude_dirs=args.exclude,
        dry_run=args.dry_run
    )
    
    # Update HTML files
    stats = updater.update_all_html_files()
    
    # Generate and save report
    report = updater.generate_report()
    report_file = output_path / "visualization_template_update_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Report saved to {report_file}")
    
    # Print summary
    print("\nVisualization Template Update Summary")
    print(f"Total HTML Files: {stats['total_html_files']}")
    print(f"Visualization Files: {stats['visualization_files']}")
    print(f"Updated Files: {stats['updated_files']}")
    print(f"Skipped Files: {stats['skipped_files']}")
    print(f"Error Files: {stats['error_files']}")
    
    if stats['visualization_files'] > 0:
        coverage = (stats['updated_files'] / stats['visualization_files']) * 100
    else:
        coverage = 0
    print(f"\nVisualization Template Coverage: {coverage:.2f}%")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
