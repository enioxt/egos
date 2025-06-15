#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Directory Unification Tool

This script performs basic tests of the Directory Unification Tool modules
to verify their functionality before using the tool in production.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\scripts\maintenance\directory_unification\directory_unification_tool.py
    - C:\EGOS\docs\work_logs\WORK_2025_05_23_Directory_Unification_Implementation.md
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
import datetime
import unittest
from pathlib import Path
from typing import Dict, Any, List, Union, Set

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

# Local imports - adjust the path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from scripts.maintenance.directory_unification.content_discovery import ContentDiscovery
from scripts.maintenance.directory_unification.cross_reference_analyzer import CrossReferenceAnalyzer
from scripts.maintenance.directory_unification.consolidation_planner import ConsolidationPlanner
from scripts.maintenance.directory_unification.utils import setup_logger, print_banner

# Set up logger with file output
def setup_test_logger(name, log_format, log_level=logging.INFO, log_file=None):
    """Set up a logger with console and file output."""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]: 
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create timestamp for log file
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
temp_base = os.environ.get("TEMP", os.path.abspath(os.path.join(os.path.dirname(__file__), "temp")))
os.makedirs(temp_base, exist_ok=True)
log_file = os.path.join(temp_base, f"directory_unification_test_{timestamp}.log")

# Set up logger
logger = setup_test_logger("test_directory_unification", "%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging.INFO, log_file)


class TestDirectoryUnificationTool(unittest.TestCase):
    """Test cases for the Directory Unification Tool."""
    
    def _make_json_serializable(self, obj):
        """Convert non-serializable objects like sets to serializable types.
        
        Args:
            obj: Object to make serializable
            
        Returns:
            JSON serializable object
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._make_json_serializable(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._make_json_serializable(item)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return self._make_json_serializable(obj.__dict__)
        return obj
    
    def setUp(self):
        """Set up test environment."""
        self.egos_root = os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
        self.keyword = "test"
        
        # Create a timestamped temp directory for better traceability
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_base = os.environ.get("TEMP", os.path.abspath(os.path.join(os.path.dirname(__file__), "temp")))
        self.temp_dir = os.path.join(temp_base, f"egos_test_directory_unification_{timestamp}")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Basic arguments for testing
        self.args = {
            "keyword": self.keyword,
            "egos_root": self.egos_root,
            "exclude_dirs": ["venv", ".git", "__pycache__", "node_modules", ".next"],
            "exclude_files": ["*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.jar", "*.pack"],
            "max_depth": 5,
            "dry_run": True,
            "output_dir": self.temp_dir
        }
        
        # Context for passing data between modules
        self.context = {}
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_content_discovery(self):
        """Test the ContentDiscovery module."""
        print(f"\n{Fore.CYAN}Testing ContentDiscovery module...{Style.RESET_ALL}")
        
        try:
            # Create ContentDiscovery instance
            content_discovery = ContentDiscovery(self.args, {})
            
            # Find related content
            content = content_discovery.find_related_content()
            
            # Add to context
            self.context["content"] = content
            
            # Verify results
            self.assertIsNotNone(content)
            self.assertIn("files", content)
            self.assertIn("directories", content)
            self.assertIsInstance(content["files"], list)
            self.assertIsInstance(content["directories"], list)
            
            # Convert any sets to lists for JSON serialization
            self._make_json_serializable(content)
            
            print(f"{Fore.GREEN}ContentDiscovery test passed!{Style.RESET_ALL}")
            print(f"Found {len(content['files'])} files and {len(content['directories'])} directories")
            
            # Save results for debugging
            with open(os.path.join(self.temp_dir, "content_discovery_test.json"), "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}ContentDiscovery test failed: {e}{Style.RESET_ALL}")
            self.fail(f"ContentDiscovery test failed: {e}")
            return False
    
    def test_cross_reference_analyzer(self):
        """Test the CrossReferenceAnalyzer module."""
        print(f"\n{Fore.CYAN}Testing CrossReferenceAnalyzer module...{Style.RESET_ALL}")
        
        # First run content discovery to get required context
        if not hasattr(self, "context") or not self.context.get("content"):
            if not self.test_content_discovery():
                self.skipTest("Content discovery failed, skipping cross-reference analysis test")
        
        try:
            # Create CrossReferenceAnalyzer instance
            cross_reference_analyzer = CrossReferenceAnalyzer(self.args, self.context)
            
            # Analyze references
            references = cross_reference_analyzer.analyze_references()
            
            # Add to context
            self.context["references"] = references
            
            # Verify results
            self.assertIsNotNone(references)
            self.assertIn("inbound_references", references)
            self.assertIn("outbound_references", references)
            self.assertIn("importance_metrics", references)
            
            # Convert any sets to lists for JSON serialization
            self._make_json_serializable(references)
            
            print(f"{Fore.GREEN}CrossReferenceAnalyzer test passed!{Style.RESET_ALL}")
            print(f"Analyzed {len(references.get('inbound_references', {}))} inbound references and {len(references.get('outbound_references', {}))} outbound references")
            
            # Save results for debugging
            with open(os.path.join(self.temp_dir, "cross_reference_analyzer_test.json"), "w", encoding="utf-8") as f:
                json.dump(references, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}CrossReferenceAnalyzer test failed: {e}{Style.RESET_ALL}")
            self.fail(f"CrossReferenceAnalyzer test failed: {e}")
            return False
    
    def test_consolidation_planner(self):
        """Test the ConsolidationPlanner module."""
        print(f"\n{Fore.CYAN}Testing ConsolidationPlanner module...{Style.RESET_ALL}")
        
        # First run content discovery and cross-reference analysis to get required context
        if not hasattr(self, "context") or not self.context.get("content") or not self.context.get("references"):
            if not self.test_content_discovery() or not self.test_cross_reference_analyzer():
                self.skipTest("Previous tests failed, skipping consolidation planner test")
        
        try:
            # Create ConsolidationPlanner instance
            consolidation_planner = ConsolidationPlanner(self.args, self.context)
            
            # Create consolidation plan
            plan = consolidation_planner.create_plan()
            
            # Add to context
            self.context["plan"] = plan
            
            # Verify results
            self.assertIsNotNone(plan)
            self.assertIn("target_location", plan)
            self.assertIn("file_classifications", plan)
            self.assertIn("migration_steps", plan)
            self.assertIn("impact_assessment", plan)
            self.assertIn("stats", plan)
            
            # Convert any sets to lists for JSON serialization
            self._make_json_serializable(plan)
            
            print(f"{Fore.GREEN}ConsolidationPlanner test passed!{Style.RESET_ALL}")
            print(f"Target location: {plan.get('target_location', '')}")
            print(f"Generated {len(plan.get('migration_steps', []))} migration steps")
            print(f"Files to unify: {plan.get('stats', {}).get('files_to_unify', 0)}")
            print(f"Files to preserve: {plan.get('stats', {}).get('files_to_preserve', 0)}")
            print(f"Files to archive: {plan.get('stats', {}).get('files_to_archive', 0)}")
            print(f"Files to delete: {plan.get('stats', {}).get('files_to_delete', 0)}")
            print(f"Estimated impact: {plan.get('stats', {}).get('estimated_impact', 0)}")
            
            # Save results for debugging
            with open(os.path.join(self.temp_dir, "consolidation_planner_test.json"), "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}ConsolidationPlanner test failed: {e}{Style.RESET_ALL}")
            self.fail(f"ConsolidationPlanner test failed: {e}")
            return False
    
    def test_module_imports(self):
        """Test that all modules can be imported correctly."""
        print(f"\n{Fore.CYAN}Testing module imports...{Style.RESET_ALL}")
        
        try:
            # Test importing all modules
            from scripts.maintenance.directory_unification.content_discovery import ContentDiscovery
            from scripts.maintenance.directory_unification.cross_reference_analyzer import CrossReferenceAnalyzer
            from scripts.maintenance.directory_unification.consolidation_planner import ConsolidationPlanner
            from scripts.maintenance.directory_unification.migration_executor import MigrationExecutor
            from scripts.maintenance.directory_unification.report_generator import ReportGenerator
            from scripts.maintenance.directory_unification.directory_unification_tool import DirectoryUnificationTool
            
            # Print module versions for debugging
            modules = {
                "ContentDiscovery": ContentDiscovery,
                "CrossReferenceAnalyzer": CrossReferenceAnalyzer,
                "ConsolidationPlanner": ConsolidationPlanner,
                "MigrationExecutor": MigrationExecutor,
                "ReportGenerator": ReportGenerator,
                "DirectoryUnificationTool": DirectoryUnificationTool
            }
            
            print(f"{Fore.GREEN}All modules imported successfully!{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Module Details:{Style.RESET_ALL}")
            for name, module in modules.items():
                module_path = module.__module__
                print(f"  {Fore.GREEN}{name}:{Style.RESET_ALL} {module_path}")
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Module import test failed: {e}{Style.RESET_ALL}")
            self.fail(f"Module import test failed: {e}")
            return False


def main():
    """Main function to run the tests."""
    # Print banner
    print_banner("Directory Unification Tool Tests")
    
    # Create a temporary directory for test artifacts
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = os.path.join(os.environ.get("TEMP", os.path.abspath(os.path.join(os.path.dirname(__file__), "temp"))), 
                          f"egos_test_directory_unification_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"{Fore.CYAN}Test artifacts will be stored in: {temp_dir}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Test log file: {log_file}{Style.RESET_ALL}")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(TestDirectoryUnificationTool('test_module_imports'))
    suite.addTest(TestDirectoryUnificationTool('test_content_discovery'))
    suite.addTest(TestDirectoryUnificationTool('test_cross_reference_analyzer'))
    suite.addTest(TestDirectoryUnificationTool('test_consolidation_planner'))
    
    # Run the tests
    print(f"{Fore.YELLOW}\n{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}RUNNING TESTS FOR DIRECTORY UNIFICATION TOOL{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary report
    print(f"{Fore.YELLOW}\n{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}TEST SUMMARY REPORT{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Results:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Tests run:{Style.RESET_ALL} {result.testsRun}")
    print(f"  {Fore.GREEN}Errors:{Style.RESET_ALL} {len(result.errors)}")
    print(f"  {Fore.GREEN}Failures:{Style.RESET_ALL} {len(result.failures)}")
    print(f"  {Fore.GREEN}Skipped:{Style.RESET_ALL} {len(result.skipped)}")
    
    if result.wasSuccessful():
        print(f"\n{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Some tests failed. See details above.{Style.RESET_ALL}")
    
    # Print test artifacts location
    print(f"\n{Fore.CYAN}Test Artifacts:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Location:{Style.RESET_ALL} {temp_dir}")
    print(f"  {Fore.GREEN}Log File:{Style.RESET_ALL} {log_file}")
    
    # Print instructions for viewing results
    print(f"\n{Fore.CYAN}To view detailed test results:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}1. Check the log file for complete output{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}2. Examine the JSON files in the test artifacts directory{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}3. Run with --verbose flag for more detailed console output{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run Directory Unification Tool tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set logger level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        print(f"{Fore.YELLOW}Verbose logging enabled{Style.RESET_ALL}")
    
    main()