#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Directory Unification Tool

This script serves as the main entry point for the Directory Unification Tool,
orchestrating the execution of all modules in the correct sequence to identify,
analyze, and consolidate related content across the EGOS system. The tool is
designed to be agnostic to the type of files being analyzed, allowing for
consolidation of any content type based on user-specified keywords.

Author: Cascade
Date: 2025-05-23
Version: 1.1.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\maintenance\directory_unification\content_discovery.py
    - C:\EGOS\scripts\maintenance\directory_unification\cross_reference_analyzer.py
    - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
    - C:\EGOS\scripts\maintenance\directory_unification\consolidation_planner.py
    - C:\EGOS\scripts\maintenance\directory_unification\migration_executor.py
    - C:\EGOS\scripts\maintenance\directory_unification\report_generator.py
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
import sys
import json
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Third-party imports
try:
    from colorama import Fore, Style, init
    # init()  # Initialize colorama - Temporarily commented out for debugging output issues
except ImportError:
    # Define dummy colorama classes if not available
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()

# Local imports - using absolute imports to avoid module resolution issues
import sys
import os

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the modules using relative paths
from directory_unification.content_discovery import ContentDiscovery
from directory_unification.cross_reference_analyzer import CrossReferenceAnalyzer
from directory_unification.consolidation_planner import ConsolidationPlanner
from directory_unification.migration_executor import MigrationExecutor
from directory_unification.report_generator import ReportGenerator
from directory_unification.utils import setup_logger, print_banner, Timer, json_serialize, EGOSJSONEncoder

# Import context analyzer if available
try:
    from directory_unification.context_analyzer import ContextAnalyzer
    HAVE_CONTEXT_ANALYZER = True
except ImportError:
    HAVE_CONTEXT_ANALYZER = False

# Constants
CONFIG = {
    "STANDARD_REPORTS_DIR": os.path.join(os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))), "reports"),
    "TOOL_REPORTS_DIR": "directory_unification",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_LEVEL": logging.INFO,
    "LOG_FILENAME": "directory_unification.log",
    "DEFAULT_BATCH_SIZE": 100,
    "ENABLE_CONTEXT_ANALYSIS": True,
    "USER_DECISION_REQUIRED": True
}

# Logger will be set up within the DirectoryUnificationTool class instance
print("DEBUG: TOP LEVEL PRINT BEFORE MAIN", file=sys.stderr, flush=True) # TOP LEVEL DEBUG


class DirectoryUnificationTool:
    """
    Main class for the Directory Unification Tool, orchestrating the execution
    of all modules in the correct sequence.
    """
    
    def __init__(self, args: Dict[str, Any]):
        """
        Initialize the DirectoryUnificationTool class.
        
        Args:
            args: Command line arguments or configuration
        """
        self.args = args
        self.egos_root = Path(args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))))
        
        # Get the keyword from arguments
        self.keyword = args.get("keyword", "")
        
        # Set up standardized report directory structure
        self.standard_reports_dir = CONFIG["STANDARD_REPORTS_DIR"]
        self.tool_reports_dir = os.path.join(self.standard_reports_dir, CONFIG["TOOL_REPORTS_DIR"])
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir_name = f"report_{self.keyword}_{self.timestamp}" if self.keyword else f"report_{self.timestamp}"
        
        # Default report directory using Path for robustness
        _default_report_dir = Path(self.egos_root) / self.tool_reports_dir / self.report_dir_name
        
        # Use output_dir from args if specified, otherwise use the default report_dir
        # Also ensure it's an absolute path
        _user_output_dir = self.args.get("output_dir")
        if _user_output_dir:
            self.output_dir = str(Path(_user_output_dir).resolve())
        else:
            self.output_dir = str(_default_report_dir.resolve())
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a marker file to confirm the output directory
        marker_path = os.path.join(self.output_dir, "directory_marker.txt")
        try:
            with open(marker_path, "w") as f:
                f.write(f"Directory Unification Tool output directory marker created at {datetime.datetime.now()}\n")
                f.write(f"Output directory: {self.output_dir}\n")
                f.write(f"Keyword: {self.keyword}\n")
                f.write(f"Verbose mode: {bool(self.args.get('verbose', False))}\n")
        except Exception as e:
            print(f"Error creating marker file: {e}", file=sys.stderr, flush=True)
        
        # Initialize context for passing data between modules
        self.context = {}
        
        # Determine log level based on verbosity
        log_level_to_use = logging.DEBUG if self.args.get("verbose") else CONFIG.get("LOG_LEVEL", logging.INFO)

        # Set up instance logger
        self.logger = setup_logger(
            name="directory_unification_tool",
            log_format=CONFIG["LOG_FORMAT"],
            log_level=log_level_to_use,
            log_dir=self.output_dir,
            log_filename=CONFIG.get("LOG_FILENAME", "directory_unification.log")
        )
        self.logger.info(f"Logger initialized. Output directory: {self.output_dir}")
        self.logger.info(f"Log file should be at: {Path(self.output_dir) / CONFIG.get('LOG_FILENAME')}")
        
        self.results = {
            "keyword": self.keyword,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_directory": self.output_dir,
            "phases": {},
            "success": False
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Run the Directory Unification Tool.
        
        Returns:
            Dictionary with results and report paths
        """
        self.logger.info("Starting Directory Unification Tool")
        
        # Start timer
        timer = Timer("Directory Unification Tool")
        timer.start()
        
        try:
            # Step 1: Content Discovery
            content_discovery = ContentDiscovery(self.args, self.logger)
            content_results = content_discovery.discover_content()
            self.logger.info(f"Content discovery found {len(content_results.get('files', []))} files and {len(content_results.get('directories', []))} directories")
            
            # Step 2: Cross-Reference Analysis
            cross_reference_analyzer = CrossReferenceAnalyzer(self.args, {"content": content_results}, self.logger)
            reference_results = cross_reference_analyzer.analyze_references()
            self.logger.info(f"Cross-reference analysis found {len(reference_results.get('inbound_references', {}))} files with inbound references")
            
            # Step 3: Context Analysis (if available and enabled)
            context_results = None
            if HAVE_CONTEXT_ANALYZER and CONFIG.get("ENABLE_CONTEXT_ANALYSIS", True):
                self.logger.info("Starting context analysis")
                context_analyzer = ContextAnalyzer(self.args, {
                    "content": content_results,
                    "references": reference_results
                }, self.logger)
                context_results = context_analyzer.analyze_context()
                self.logger.info(f"Context analysis completed with {context_results.get('stats', {}).get('files_with_documentation', 0)} files having documentation")
            else:
                self.logger.info("Context analysis skipped (not available or disabled)")
            
            # Step 4: Consolidation Planning
            consolidation_context = {
                "content": content_results,
                "references": reference_results
            }
            
            # Add context analysis results if available
            if context_results:
                consolidation_context["context_analysis"] = context_results
            
            consolidation_planner = ConsolidationPlanner(self.args, consolidation_context, self.logger)
            consolidation_plan = consolidation_planner.create_plan()
            self.logger.info(f"Consolidation plan created with target directory: {consolidation_plan.get('target_directory')}")
            
            # Step 5: User Decision Points (if required and not in automatic mode)
            if CONFIG.get("USER_DECISION_REQUIRED", True) and not self.args.get("automatic", False):
                self.logger.info("User decisions required before proceeding")
                # In a real implementation, this would prompt the user for decisions
                # For now, we'll just log the decision points
                for decision_point in consolidation_plan.get("user_decision_points", []):
                    self.logger.info(f"Decision point: {decision_point.get('description')}")
            
            # Step 6: Migration Execution (if --execute flag is set)
            migration_results = None
            if self.args.get("execute", False):
                migration_executor = MigrationExecutor(self.args, {
                    "content": content_results,
                    "references": reference_results,
                    "context_analysis": context_results,
                    "consolidation_plan": consolidation_plan
                }, self.logger)
                migration_results = migration_executor.execute_migration()
                self.logger.info(f"Migration executed with {migration_results.get('files_migrated', 0)} files migrated")
            
            # Step 7: Report Generation
            report_generator = ReportGenerator(self.args, {
                "content": content_results,
                "references": reference_results,
                "context_analysis": context_results,
                "consolidation_plan": consolidation_plan,
                "migration_results": migration_results
            }, self.logger)
            report_results = report_generator.generate_report()
            self.logger.info(f"Report generated at {report_results.get('report_path')}")
            
            # Prepare results
            results = {
                "content": content_results,
                "references": reference_results,
                "context_analysis": context_results,
                "consolidation_plan": consolidation_plan,
                "migration_results": migration_results,
                "report": report_results,
                "output_dir": self.output_dir
            }
            
            # Log completion
            elapsed_time = timer.stop()
            self.logger.info(f"Directory Unification Tool completed in {elapsed_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            elapsed_time = timer.stop()
            self.logger.error(f"Directory Unification Tool failed after {elapsed_time:.2f} seconds: {e}")
            raise


def main():
    """Main function for the Directory Unification Tool."""
    # Print banner
    print_banner("Directory Unification Tool")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Directory Unification Tool for EGOS")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    parser.add_argument("--keyword", required=True, help="Keyword for content discovery")
    parser.add_argument("--output-dir", help="Output directory for reports and logs")
    parser.add_argument("--execute", action="store_true", help="Execute migration plan")
    parser.add_argument("--automatic", action="store_true", help="Run in automatic mode without user decisions")
    parser.add_argument("--skip-context", action="store_true", help="Skip context analysis")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--batch-size", type=int, default=CONFIG["DEFAULT_BATCH_SIZE"], help="Batch size for processing large file sets")
    
    args = parser.parse_args()
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Override CONFIG settings based on arguments
    if args.skip_context:
        CONFIG["ENABLE_CONTEXT_ANALYSIS"] = False
    
    if args.automatic:
        CONFIG["USER_DECISION_REQUIRED"] = False
    
    # Create DirectoryUnificationTool instance
    tool = DirectoryUnificationTool(args_dict)
    
    # Run tool
    try:
        results = tool.run()
        
        # Display summary
        print(f"\n{Fore.CYAN}Directory Unification Tool Summary:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Files found:{Style.RESET_ALL} {len(results['content'].get('files', []))}")
        print(f"  {Fore.GREEN}Directories found:{Style.RESET_ALL} {len(results['content'].get('directories', []))}")
        print(f"  {Fore.GREEN}Files with references:{Style.RESET_ALL} {len(results['references'].get('inbound_references', {}))}")
        
        if results.get('context_analysis'):
            print(f"  {Fore.GREEN}Files with documentation:{Style.RESET_ALL} {results['context_analysis'].get('stats', {}).get('files_with_documentation', 0)}")
            print(f"  {Fore.GREEN}Functional groups identified:{Style.RESET_ALL} {results['context_analysis'].get('stats', {}).get('functional_groups_identified', 0)}")
        
        print(f"  {Fore.GREEN}Target directory:{Style.RESET_ALL} {results['consolidation_plan'].get('target_directory')}")
        print(f"  {Fore.GREEN}Files to consolidate:{Style.RESET_ALL} {results['consolidation_plan'].get('stats', {}).get('files_to_consolidate', 0)}")
        print(f"  {Fore.GREEN}Files to leave in place:{Style.RESET_ALL} {results['consolidation_plan'].get('stats', {}).get('files_to_leave', 0)}")
        print(f"  {Fore.GREEN}User decision points:{Style.RESET_ALL} {len(results['consolidation_plan'].get('user_decision_points', []))}")
        
        if results.get('migration_results'):
            print(f"  {Fore.GREEN}Files migrated:{Style.RESET_ALL} {results['migration_results'].get('files_migrated', 0)}")
            print(f"  {Fore.GREEN}References updated:{Style.RESET_ALL} {results['migration_results'].get('references_updated', 0)}")
        
        print(f"  {Fore.GREEN}Report generated at:{Style.RESET_ALL} {results['report'].get('report_path')}")
        print(f"  {Fore.GREEN}Output directory:{Style.RESET_ALL} {results['output_dir']}")
        
        # EGOS signature
        print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")
        
        return 0
        
    except Exception as e:
        print(f"\n{Fore.RED}Error:{Style.RESET_ALL} {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        
        return 1
    
    # If reports were generated, show their paths
    if "report_generation" in results.get("phases", {}) and results["phases"]["report_generation"].get("status") == "success":
        print(f"\n{Fore.CYAN}Reports:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}HTML Report:{Style.RESET_ALL} {results['phases']['report_generation'].get('html_report', '')}")
        print(f"  {Fore.GREEN}Markdown Report:{Style.RESET_ALL} {results['phases']['report_generation'].get('markdown_report', '')}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")
    
    # Return success status as exit code
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())