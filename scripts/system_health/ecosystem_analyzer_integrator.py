#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Script Ecosystem Analyzer Integrator

This script ensures the Script Ecosystem Analyzer is properly integrated with other
EGOS subsystems, particularly CORUJA (human-AI connection) and the EGOS website.
It establishes cross-references, updates relevant documentation, and ensures
all components are properly interconnected.

@author: EGOS Development Team
@date: 2025-05-27
@version: 0.1.0

@references:
- C:\EGOS\MQP.md (Systemic Cartography, Evolutionary Preservation)
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\website\content\roadmap.md
- C:\EGOS\subsystems\coruja\README.md
- C:\EGOS\scripts\system_health\analyzers\script_ecosystem_analyzer.py
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
import sys
import re
import logging
import json
import datetime
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ecosystem_analyzer_integrator")

# Constants
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analyzers", "script_ecosystem_analyzer.py")
WEBSITE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "website")
CORUJA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "subsystems", "coruja")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "docs")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "reports")

def print_banner():
    """Print a banner for the script ecosystem analyzer integrator."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║       EGOS Script Ecosystem Analyzer Integrator               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def ensure_directory_exists(directory: str) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

def create_website_integration(report_path: Optional[str] = None) -> None:
    """Create website integration for the script ecosystem analyzer.
    
    Args:
        report_path: Optional path to an existing report to integrate
    """
    logger.info("Creating website integration")
    
    # Ensure website directories exist
    website_content_dir = os.path.join(WEBSITE_DIR, "content")
    website_reports_dir = os.path.join(website_content_dir, "reports")
    website_tools_dir = os.path.join(website_content_dir, "tools")
    
    ensure_directory_exists(website_content_dir)
    ensure_directory_exists(website_reports_dir)
    ensure_directory_exists(website_tools_dir)
    
    # Create tool documentation in website
    tool_doc_path = os.path.join(website_tools_dir, "script_ecosystem_analyzer.md")
    
    tool_doc_content = [
        "---",
        "title: 'Script Ecosystem Analyzer'",
        f"date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
        "author: 'EGOS System'",
        "description: 'Analyzes the distribution and health of scripts and documentation across the EGOS system.'",
        "categories: ['tools', 'system-health']",
        "tags: ['scripts', 'analysis', 'health-check', 'documentation', 'heat-map']",
        "---",
        "",
        "# Script Ecosystem Analyzer",
        "",
        "## Overview",
        "",
        "The Script Ecosystem Analyzer is a tool that analyzes the distribution and health of scripts and documentation across the EGOS system. It creates a \"heat map\" visualization that identifies:",
        "",
        "- **Isolated scripts**: Scripts in directories with few other scripts",
        "- **Potentially orphaned scripts**: Scripts with low cross-references or no recent modifications",
        "- **Underdeveloped areas**: Directories with few scripts",
        "- **Documentation health**: Documentation without clear purpose or references",
        "",
        "## Integration with EGOS",
        "",
        "The Script Ecosystem Analyzer is integrated with the following EGOS components:",
        "",
        "- **Health Check Framework**: Part of the unified health check system",
        "- **CORUJA Subsystem**: Analyzes connections with the human-AI interaction subsystem",
        "- **Website**: Generates reports that are integrated with the EGOS website",
        "",
        "## Usage",
        "",
        "```bash",
        "python C:\\EGOS\\scripts\\system_health\\analyzers\\script_ecosystem_analyzer.py [target_path] --output [output_path] --website-integration",
        "```",
        "",
        "### Parameters",
        "",
        "- `target_path`: Path to analyze (default: EGOS root directory)",
        "- `--output`: Path to save the report (default: auto-generated)",
        "- `--config`: Path to configuration file",
        "- `--verbose`: Enable verbose logging",
        "- `--max-file-size`: Maximum file size in MB to analyze (default: 10)",
        "- `--website-integration`: Generate website integration files",
        "",
        "## Latest Reports",
        "",
        "- [Latest Script Ecosystem Analysis](/reports/script_ecosystem_report/)",
        "",
        "## References",
        "",
        "- [Health Check Unification Plan](/docs/planning/health_check_unification_plan/)",
        "- [CORUJA Subsystem](/subsystems/coruja/)",
        "- [EGOS Roadmap](/roadmap/)",
        ""
    ]
    
    with open(tool_doc_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(tool_doc_content))
    
    logger.info(f"Created tool documentation: {tool_doc_path}")
    
    # If a report is provided, copy it to the website
    if report_path and os.path.exists(report_path):
        report_filename = os.path.basename(report_path)
        website_report_path = os.path.join(website_reports_dir, "script_ecosystem_report.md")
        
        # Read the report
        with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
            report_content = f.read()
        
        # Add frontmatter
        frontmatter = [
            "---",
            "title: 'EGOS Script Ecosystem Analysis'",
            f"date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
            "author: 'EGOS System'",
            "description: 'Analysis of the EGOS script ecosystem, identifying hot and cold areas of development.'",
            "categories: ['reports', 'system-health']",
            "tags: ['scripts', 'analysis', 'health-check', 'documentation']",
            "---",
            ""
        ]
        
        # Write to website directory
        with open(website_report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(frontmatter) + report_content)
        
        logger.info(f"Integrated report with website: {website_report_path}")
    
    # Update roadmap to include script ecosystem analyzer
    roadmap_path = os.path.join(website_content_dir, "roadmap.md")
    
    if os.path.exists(roadmap_path):
        with open(roadmap_path, 'r', encoding='utf-8', errors='ignore') as f:
            roadmap_content = f.readlines()
        
        # Check if script ecosystem analyzer is already in the roadmap
        analyzer_in_roadmap = any("script ecosystem analyzer" in line.lower() for line in roadmap_content)
        
        if not analyzer_in_roadmap:
            # Find the health check section or create it
            health_check_index = -1
            for i, line in enumerate(roadmap_content):
                if "health check" in line.lower() or "system health" in line.lower():
                    health_check_index = i
                    break
            
            if health_check_index >= 0:
                # Add script ecosystem analyzer to the health check section
                roadmap_content.insert(health_check_index + 1, "  - [x] Script Ecosystem Analyzer - Identifies hot and cold areas of development\n")
            else:
                # Add a new section for system health
                roadmap_content.append("\n## System Health\n\n")
                roadmap_content.append("- [x] Health Check Framework\n")
                roadmap_content.append("  - [x] Script Ecosystem Analyzer - Identifies hot and cold areas of development\n")
            
            # Write updated roadmap
            with open(roadmap_path, 'w', encoding='utf-8') as f:
                f.writelines(roadmap_content)
            
            logger.info(f"Updated roadmap: {roadmap_path}")
    
    logger.info("Website integration complete")

def create_coruja_integration() -> None:
    """Create CORUJA subsystem integration for the script ecosystem analyzer."""
    logger.info("Creating CORUJA integration")
    
    # Ensure CORUJA directories exist
    ensure_directory_exists(CORUJA_DIR)
    coruja_tools_dir = os.path.join(CORUJA_DIR, "tools")
    ensure_directory_exists(coruja_tools_dir)
    
    # Create integration documentation
    integration_path = os.path.join(coruja_tools_dir, "script_ecosystem_analyzer_integration.md")
    
    integration_content = [
        "# Script Ecosystem Analyzer Integration with CORUJA",
        "",
        f"*Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d')}*",
        "",
        "## Overview",
        "",
        "The Script Ecosystem Analyzer has been integrated with the CORUJA subsystem to provide insights into the human-AI connection components of EGOS. This integration enables better understanding of how CORUJA scripts are distributed, referenced, and maintained across the system.",
        "",
        "## Integration Points",
        "",
        "1. **CORUJA Script Analysis**: The Script Ecosystem Analyzer identifies and analyzes all CORUJA-related scripts.",
        "2. **Cross-Reference Tracking**: Tracks references to CORUJA components from other parts of the system.",
        "3. **Documentation Health**: Evaluates the quality and completeness of CORUJA documentation.",
        "",
        "## Usage for CORUJA Development",
        "",
        "To analyze CORUJA scripts specifically:",
        "",
        "```bash",
        "python C:\\EGOS\\scripts\\system_health\\analyzers\\script_ecosystem_analyzer.py C:\\EGOS\\subsystems\\coruja --output C:\\EGOS\\reports\\coruja_script_analysis.md",
        "```",
        "",
        "## References",
        "",
        "- [Script Ecosystem Analyzer Documentation](C:\\EGOS\\scripts\\system_health\\analyzers\\script_ecosystem_analyzer.py)",
        "- [Health Check Unification Plan](C:\\EGOS\\docs\\planning\\health_check_unification_plan.md)",
        "- [CORUJA README](C:\\EGOS\\subsystems\\coruja\\README.md)",
        ""
    ]
    
    with open(integration_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(integration_content))
    
    logger.info(f"Created CORUJA integration documentation: {integration_path}")
    
    # Update CORUJA README if it exists
    readme_path = os.path.join(CORUJA_DIR, "README.md")
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            readme_content = f.readlines()
        
        # Check if script ecosystem analyzer is already in the README
        analyzer_in_readme = any("script ecosystem analyzer" in line.lower() for line in readme_content)
        
        if not analyzer_in_readme:
            # Find the tools section or create it
            tools_index = -1
            for i, line in enumerate(readme_content):
                if "# tools" in line.lower() or "## tools" in line.lower():
                    tools_index = i
                    break
            
            if tools_index >= 0:
                # Add script ecosystem analyzer to the tools section
                readme_content.insert(tools_index + 1, "\n### Script Ecosystem Analyzer\n\n")
                readme_content.insert(tools_index + 2, "The Script Ecosystem Analyzer provides insights into CORUJA script distribution and health. See [integration documentation](tools/script_ecosystem_analyzer_integration.md) for details.\n\n")
            else:
                # Add a new section for tools
                readme_content.append("\n## Tools\n\n")
                readme_content.append("### Script Ecosystem Analyzer\n\n")
                readme_content.append("The Script Ecosystem Analyzer provides insights into CORUJA script distribution and health. See [integration documentation](tools/script_ecosystem_analyzer_integration.md) for details.\n\n")
            
            # Write updated README
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.writelines(readme_content)
            
            logger.info(f"Updated CORUJA README: {readme_path}")
    else:
        # Create a basic README if it doesn't exist
        readme_content = [
            "# CORUJA Subsystem",
            "",
            "## Overview",
            "",
            "CORUJA is the subsystem responsible for human-AI connections in the EGOS ecosystem.",
            "",
            "## Tools",
            "",
            "### Script Ecosystem Analyzer",
            "",
            "The Script Ecosystem Analyzer provides insights into CORUJA script distribution and health. See [integration documentation](tools/script_ecosystem_analyzer_integration.md) for details.",
            ""
        ]
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(readme_content))
        
        logger.info(f"Created CORUJA README: {readme_path}")
    
    logger.info("CORUJA integration complete")

def update_cross_references() -> None:
    """Update cross-references for the script ecosystem analyzer."""
    logger.info("Updating cross-references")
    
    # Paths to update
    paths = [
        SCRIPT_PATH,
        os.path.join(WEBSITE_DIR, "content", "tools", "script_ecosystem_analyzer.md"),
        os.path.join(CORUJA_DIR, "tools", "script_ecosystem_analyzer_integration.md"),
        os.path.join(DOCS_DIR, "planning", "health_check_unification_plan.md")
    ]
    
    # References to add
    references = [
        "C:\\EGOS\\scripts\\system_health\\analyzers\\script_ecosystem_analyzer.py",
        "C:\\EGOS\\website\\content\\tools\\script_ecosystem_analyzer.md",
        "C:\\EGOS\\subsystems\\coruja\\tools\\script_ecosystem_analyzer_integration.md",
        "C:\\EGOS\\docs\\planning\\health_check_unification_plan.md"
    ]
    
    # Update each file if it exists
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find the references section
            references_match = re.search(r'@references:(.*?)(?=\n\w|\Z)', content, re.DOTALL)
            
            if references_match:
                # Extract existing references
                existing_refs = references_match.group(1).strip().split('\n')
                existing_refs = [ref.strip() for ref in existing_refs if ref.strip()]
                
                # Add new references if they don't exist
                updated_refs = existing_refs.copy()
                for ref in references:
                    if not any(ref in existing_ref for existing_ref in existing_refs):
                        updated_refs.append(f"- {ref}")
                
                # Replace references section
                if len(updated_refs) > len(existing_refs):
                    new_refs_section = "@references:\n" + "\n".join(updated_refs)
                    updated_content = content.replace(references_match.group(0), new_refs_section)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    logger.info(f"Updated cross-references in: {path}")
            else:
                logger.warning(f"No references section found in: {path}")
    
    logger.info("Cross-references update complete")

def run_analyzer(target_path: str, output_path: Optional[str] = None) -> str:
    """Run the script ecosystem analyzer.
    
    Args:
        target_path: Path to analyze
        output_path: Optional path to save the report
        
    Returns:
        Path to the generated report
    """
    logger.info(f"Running script ecosystem analyzer on: {target_path}")
    
    # Default output path if not provided
    if not output_path:
        ensure_directory_exists(REPORTS_DIR)
        output_path = os.path.join(REPORTS_DIR, f"script_ecosystem_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    # Build command
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        target_path,
        "--output", output_path,
        "--website-integration"
    ]
    
    # Run the analyzer
    import subprocess
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Script ecosystem analyzer completed successfully. Report saved to: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running script ecosystem analyzer: {e}")
        return ""

def main():
    """Main function for running the script ecosystem analyzer integrator."""
    parser = argparse.ArgumentParser(description="EGOS Script Ecosystem Analyzer Integrator")
    parser.add_argument("--run-analyzer", action="store_true",
                        help="Run the script ecosystem analyzer")
    parser.add_argument("--target-path", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                        help="Path to analyze (default: EGOS root directory)")
    parser.add_argument("--output", help="Path to save the report")
    parser.add_argument("--website-integration", action="store_true",
                        help="Create website integration")
    parser.add_argument("--coruja-integration", action="store_true",
                        help="Create CORUJA integration")
    parser.add_argument("--update-cross-references", action="store_true",
                        help="Update cross-references")
    parser.add_argument("--all", action="store_true",
                        help="Perform all integration tasks")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Determine what to do
    run_analyzer_flag = args.run_analyzer or args.all
    website_integration_flag = args.website_integration or args.all
    coruja_integration_flag = args.coruja_integration or args.all
    update_cross_references_flag = args.update_cross_references or args.all
    
    # If no specific tasks are specified, do everything
    if not (run_analyzer_flag or website_integration_flag or coruja_integration_flag or update_cross_references_flag):
        run_analyzer_flag = True
        website_integration_flag = True
        coruja_integration_flag = True
        update_cross_references_flag = True
    
    # Run the analyzer if requested
    report_path = None
    if run_analyzer_flag:
        report_path = run_analyzer(args.target_path, args.output)
    
    # Create website integration if requested
    if website_integration_flag:
        create_website_integration(report_path)
    
    # Create CORUJA integration if requested
    if coruja_integration_flag:
        create_coruja_integration()
    
    # Update cross-references if requested
    if update_cross_references_flag:
        update_cross_references()
    
    logger.info("Script ecosystem analyzer integration complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())