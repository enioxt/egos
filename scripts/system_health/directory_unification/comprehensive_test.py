#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Test Script for Directory Unification Tool

This script performs comprehensive tests of the Directory Unification Tool modules
with various scenarios and edge cases to ensure robust functionality.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\scripts\maintenance\directory_unification\directory_unification_tool.py
    - C:\EGOS\scripts\maintenance\directory_unification\test_directory_unification.py
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
import tempfile
import shutil
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
from scripts.maintenance.directory_unification.migration_executor import MigrationExecutor
from scripts.maintenance.directory_unification.report_generator import ReportGenerator
from scripts.maintenance.directory_unification.directory_unification_tool import DirectoryUnificationTool
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
reports_dir = os.path.join(os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))), "reports")
test_reports_dir = os.path.join(reports_dir, "directory_unification", "tests")
os.makedirs(test_reports_dir, exist_ok=True)
log_file = os.path.join(test_reports_dir, f"comprehensive_test_{timestamp}.log")

# Set up logger
logger = setup_test_logger("comprehensive_test", "%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging.INFO, log_file)


class TestEnvironment:
    """Class for setting up and tearing down test environments."""
    
    def __init__(self, base_dir=None):
        """Initialize the test environment."""
        self.base_dir = base_dir or tempfile.mkdtemp(prefix="egos_test_")
        self.test_dirs = []
        self.test_files = []
        self.logger = logging.getLogger("test_environment")
    
    def create_test_structure(self, structure):
        """Create a test directory structure.
        
        Args:
            structure: Dictionary representing the directory structure
                {
                    "dirs": ["dir1", "dir2/subdir"],
                    "files": [
                        {"path": "file1.txt", "content": "content1"},
                        {"path": "dir1/file2.txt", "content": "content2"}
                    ],
                    "references": [
                        {"source": "file1.txt", "target": "dir1/file2.txt"}
                    ]
                }
        """
        # Create directories
        for dir_path in structure.get("dirs", []):
            full_path = os.path.join(self.base_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
            self.test_dirs.append(full_path)
        
        # Create files
        for file_info in structure.get("files", []):
            file_path = file_info["path"]
            content = file_info.get("content", "")
            full_path = os.path.join(self.base_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.test_files.append(full_path)
        
        # Add references between files
        for ref_info in structure.get("references", []):
            source_path = os.path.join(self.base_dir, ref_info["source"])
            target_path = ref_info["target"]
            
            if os.path.exists(source_path):
                with open(source_path, "a", encoding="utf-8") as f:
                    f.write(f"\nReference to: {target_path}")
    
    def cleanup(self):
        """Clean up the test environment."""
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)


class ComprehensiveTests(unittest.TestCase):
    """Comprehensive test cases for the Directory Unification Tool."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cls.test_environments = []
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environments after all tests."""
        for env in cls.test_environments:
            env.cleanup()
    
    def setUp(self):
        """Set up test environment for each test."""
        self.egos_root = os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
        
        # Create a timestamped temp directory for better traceability
        temp_base = os.path.join(test_reports_dir, f"test_run_{self.timestamp}")
        os.makedirs(temp_base, exist_ok=True)
        self.temp_dir = temp_base
        
        # Basic arguments for testing
        self.args = {
            "keyword": "test",
            "egos_root": self.egos_root,
            "exclude_dirs": ["venv", ".git", "__pycache__", "node_modules", ".next"],
            "exclude_files": ["*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.jar", "*.pack"],
            "max_depth": 5,
            "dry_run": True,
            "output_dir": self.temp_dir,
            "test_mode": True  # Enable test mode for faster execution
        }
        
        # Context for passing data between modules
        self.context = {}
        
        # Helper for JSON serialization
        self.json_helper = JSONHelper()
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def _make_json_serializable(self, obj):
        """Convert non-serializable objects like sets to serializable types."""
        return self.json_helper.make_serializable(obj)
    
    def test_empty_directory(self):
        """Test with an empty directory."""
        print(f"\n{Fore.CYAN}Testing with empty directory...{Style.RESET_ALL}")
        
        # Create empty test environment
        env = TestEnvironment()
        self.test_environments.append(env)
        
        # Update args to use the test environment
        args = self.args.copy()
        args["egos_root"] = env.base_dir
        args["keyword"] = "nonexistent"
        
        # Run content discovery
        content_discovery = ContentDiscovery(args, {})
        content = content_discovery.find_related_content()
        
        # Verify results
        self.assertIsNotNone(content)
        self.assertEqual(len(content.get("files", [])), 0)
        self.assertEqual(len(content.get("directories", [])), 0)
        
        print(f"{Fore.GREEN}Empty directory test passed!{Style.RESET_ALL}")
    
    def test_single_file(self):
        """Test with a single file containing the keyword."""
        print(f"\n{Fore.CYAN}Testing with single file...{Style.RESET_ALL}")
        
        # Create test environment with a single file
        env = TestEnvironment()
        self.test_environments.append(env)
        
        env.create_test_structure({
            "files": [
                {"path": "test_file.txt", "content": "This is a test file with the keyword test in it."}
            ]
        })
        
        # Update args to use the test environment
        args = self.args.copy()
        args["egos_root"] = env.base_dir
        args["keyword"] = "test"
        
        # Run content discovery
        content_discovery = ContentDiscovery(args, {})
        content = content_discovery.find_related_content()
        
        # Verify results
        self.assertIsNotNone(content)
        self.assertEqual(len(content.get("files", [])), 1)
        self.assertEqual(len(content.get("directories", [])), 0)
        
        print(f"{Fore.GREEN}Single file test passed!{Style.RESET_ALL}")
    
    def test_complex_structure(self):
        """Test with a complex directory structure."""
        print(f"\n{Fore.CYAN}Testing with complex directory structure...{Style.RESET_ALL}")
        
        # Create test environment with a complex structure
        env = TestEnvironment()
        self.test_environments.append(env)
        
        env.create_test_structure({
            "dirs": [
                "docs",
                "scripts",
                "scripts/test",
                "scripts/utils",
                "data"
            ],
            "files": [
                {"path": "README.md", "content": "# Test Project\nThis is a test project."},
                {"path": "docs/test_doc.md", "content": "# Test Documentation\nThis is a test document."},
                {"path": "scripts/test/test_script.py", "content": "# Test script\ndef test_function():\n    print('This is a test')"},
                {"path": "scripts/utils/helper.py", "content": "# Helper functions\ndef helper():\n    print('Helper function')"},
                {"path": "data/sample.txt", "content": "Sample data without the keyword"}
            ],
            "references": [
                {"source": "README.md", "target": "docs/test_doc.md"},
                {"source": "scripts/test/test_script.py", "target": "scripts/utils/helper.py"}
            ]
        })
        
        # Update args to use the test environment
        args = self.args.copy()
        args["egos_root"] = env.base_dir
        args["keyword"] = "test"
        
        # Run content discovery
        content_discovery = ContentDiscovery(args, {})
        content = content_discovery.find_related_content()
        
        # Verify results
        self.assertIsNotNone(content)
        self.assertEqual(len(content.get("files", [])), 3)  # README.md, test_doc.md, test_script.py
        self.assertEqual(len(content.get("directories", [])), 2)  # scripts/test, docs
        
        # Add to context
        context = {"content": content}
        
        # Run cross-reference analyzer
        cross_reference_analyzer = CrossReferenceAnalyzer(args, context)
        references = cross_reference_analyzer.analyze_references()
        
        # Verify results
        self.assertIsNotNone(references)
        self.assertIn("inbound_references", references)
        self.assertIn("outbound_references", references)
        
        # Make JSON serializable
        self._make_json_serializable(references)
        
        # Add to context
        context["references"] = references
        
        # Run consolidation planner
        consolidation_planner = ConsolidationPlanner(args, context)
        plan = consolidation_planner.create_plan()
        
        # Verify results
        self.assertIsNotNone(plan)
        self.assertIn("target_location", plan)
        self.assertIn("file_classifications", plan)
        
        # Make JSON serializable
        self._make_json_serializable(plan)
        
        # Add to context
        context["plan"] = plan
        
        print(f"{Fore.GREEN}Complex structure test passed!{Style.RESET_ALL}")
        print(f"Found {len(content.get('files', []))} files and {len(content.get('directories', []))} directories")
        print(f"Target location: {plan.get('target_location', '')}")
    
    def test_end_to_end(self):
        """Test the entire workflow end-to-end."""
        print(f"\n{Fore.CYAN}Testing end-to-end workflow...{Style.RESET_ALL}")
        
        # Create test environment with a simple structure
        env = TestEnvironment()
        self.test_environments.append(env)
        
        env.create_test_structure({
            "dirs": [
                "docs",
                "scripts"
            ],
            "files": [
                {"path": "README.md", "content": "# Test Project\nThis is a test project."},
                {"path": "docs/test1.md", "content": "# Test 1\nThis is test document 1."},
                {"path": "docs/test2.md", "content": "# Test 2\nThis is test document 2."},
                {"path": "scripts/test_script.py", "content": "# Test script\ndef test_function():\n    print('This is a test')"}
            ],
            "references": [
                {"source": "README.md", "target": "docs/test1.md"},
                {"source": "docs/test1.md", "target": "docs/test2.md"}
            ]
        })
        
        # Update args to use the test environment
        args = self.args.copy()
        args["egos_root"] = env.base_dir
        args["keyword"] = "test"
        
        # Create DirectoryUnificationTool instance
        tool = DirectoryUnificationTool(args)
        
        # Run the tool
        result = tool.run()
        
        # Verify results
        self.assertTrue(result["success"])
        self.assertIn("reports", result)
        self.assertIn("html_report", result["reports"])
        self.assertIn("markdown_report", result["reports"])
        
        print(f"{Fore.GREEN}End-to-end test passed!{Style.RESET_ALL}")
        print(f"HTML Report: {result['reports']['html_report']}")
        print(f"Markdown Report: {result['reports']['markdown_report']}")


class JSONHelper:
    """Helper class for JSON serialization."""
    
    def make_serializable(self, obj):
        """Make an object JSON serializable by converting sets to lists, etc."""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)


def main():
    """Main function to run the comprehensive tests."""
    # Print banner
    print_banner("Directory Unification Tool Comprehensive Tests")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(ComprehensiveTests('test_empty_directory'))
    suite.addTest(ComprehensiveTests('test_single_file'))
    suite.addTest(ComprehensiveTests('test_complex_structure'))
    suite.addTest(ComprehensiveTests('test_end_to_end'))
    
    # Run the tests
    print(f"{Fore.YELLOW}\n{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}RUNNING COMPREHENSIVE TESTS FOR DIRECTORY UNIFICATION TOOL{Style.RESET_ALL}")
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
    print(f"  {Fore.GREEN}Location:{Style.RESET_ALL} {os.path.abspath(test_reports_dir)}")
    print(f"  {Fore.GREEN}Log File:{Style.RESET_ALL} {log_file}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run comprehensive tests for Directory Unification Tool")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Set logger level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        print(f"{Fore.YELLOW}Verbose logging enabled{Style.RESET_ALL}")
    
    main()