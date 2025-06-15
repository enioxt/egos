#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for AnalysisPipeline Component.

This module contains tests for the AnalysisPipeline class, which orchestrates
the entire cross-reference analysis process.

@author: EGOS Team
@created: 2025-04-23
@status: Alpha

@references:
- Core References:
  - [ROADMAP.md](mdc:../../../../ROADMAP.md):KOIOS-DOC-009 - Cross-Reference Analyzer Refactoring
- Related Components:
  - [pipeline.py](py:../pipeline.py) - The module being tested
  - [test_scanner.py](py:./test_scanner.py) - Tests for the FileScanner component
  - [test_graph_builder.py](py:./test_graph_builder.py) - Tests for the GraphBuilder component
  - [test_engine.py](py:./test_engine.py) - Tests for the AnalysisEngine component
- Testing Standards:
  - [testing_standards.md](mdc:../../../../docs/standards/testing_standards.md) - EGOS testing standards
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
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
import logging

# Configure logging for tests
logging.basicConfig(level=logging.ERROR)

# Add parent directory to path to enable relative imports
module_path = Path(__file__).parent.parent.parent.parent
if str(module_path) not in sys.path:
    sys.path.append(str(module_path))

from scripts.maintenance.cross_reference.pipeline import AnalysisPipeline
from scripts.maintenance.cross_reference.scanner import FileScanner
from scripts.maintenance.cross_reference.graph_builder import GraphBuilder
from scripts.maintenance.cross_reference.engine import AnalysisEngine
from scripts.maintenance.cross_reference.models.report import AnalysisReport
# Import reporter classes needed for isinstance checks
from scripts.maintenance.cross_reference.reporters.console_reporter import ConsoleReporter
from scripts.maintenance.cross_reference.reporters.markdown_reporter import MarkdownReporter


class TestAnalysisPipeline(unittest.TestCase):
    """Test cases for the AnalysisPipeline class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.root_dir = Path(self.test_dir)
        
        # Create a basic configuration
        self.config = {
            'verbose': True,
            'fix': False,
            'enable_rich': False,
            'report_dir': str(self.root_dir / "reports"),
            'markdown_report': True,
            'console_report': True
        }
        
        # Create a mock logger
        self.mock_logger = MagicMock()
        
        # Create a pipeline instance
        self.pipeline = AnalysisPipeline(
            root_dir=self.root_dir,
            config=self.config,
            logger=self.mock_logger
        )
        
        # Create test files
        self.python_file = self.root_dir / "test.py"
        self.markdown_file = self.root_dir / "test.md"
        
        os.makedirs(self.root_dir / "reports", exist_ok=True)
        
        with open(self.python_file, 'w') as f:
            f.write('"""Test file with a reference.\n\n@references:\n- [test.md](md:./test.md)\n"""\n')
        
        with open(self.markdown_file, 'w') as f:
            f.write('# Test File\n\n@references:\n- [test.py](py:./test.py)\n')

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test AnalysisPipeline initialization."""
        self.assertEqual(self.pipeline.root_dir, self.root_dir)
        self.assertEqual(self.pipeline.config, self.config)
        self.assertEqual(self.pipeline.logger, self.mock_logger)
        self.assertIsNone(self.pipeline.report)
        
        # Check that components were created
        self.assertIsInstance(self.pipeline.scanner, FileScanner)
        self.assertIsInstance(self.pipeline.graph_builder, GraphBuilder)
        self.assertIsNone(self.pipeline.engine)  # Engine is created after graph is built
        self.assertIsNotNone(self.pipeline.reporters)
        self.assertEqual(len(self.pipeline.reporters), 2)  # Console and Markdown reporters

    def test_create_scanner(self):
        """Test creating a FileScanner with the correct configuration."""
        scanner = self.pipeline._create_scanner()
        self.assertIsInstance(scanner, FileScanner)
        self.assertEqual(scanner.include_dirs, [self.root_dir])
        self.assertEqual(scanner.exclude_dirs, [])
        
        # Test with specific configuration
        self.pipeline.config['include_dirs'] = [str(self.root_dir / "src")]
        self.pipeline.config['exclude_dirs'] = [str(self.root_dir / "tests")]
        scanner = self.pipeline._create_scanner()
        self.assertEqual(scanner.include_dirs, [str(self.root_dir / "src")])
        self.assertEqual(scanner.exclude_dirs, [str(self.root_dir / "tests")])

    def test_create_graph_builder(self):
        """Test creating a GraphBuilder with the correct configuration."""
        graph_builder = self.pipeline._create_graph_builder()
        self.assertIsInstance(graph_builder, GraphBuilder)
        self.assertEqual(graph_builder.root_dir, self.root_dir)

    @patch('scripts.maintenance.cross_reference.pipeline.MarkdownReporter')
    @patch('scripts.maintenance.cross_reference.pipeline.ConsoleReporter')
    def test_create_reporters(self, mock_console_reporter, mock_markdown_reporter):
        """Test creating reporters based on configuration."""
        # Create mock reporter instances
        mock_console_instance = MagicMock()
        mock_markdown_instance = MagicMock()
        mock_console_reporter.return_value = mock_console_instance
        mock_markdown_reporter.return_value = mock_markdown_instance
        
        # Test with both reporters enabled
        reporters = self.pipeline._create_reporters()
        self.assertEqual(len(reporters), 2)
        mock_console_reporter.assert_called_once()
        mock_markdown_reporter.assert_called_once()
        
        # Test with only console reporter
        self.pipeline.config['markdown_report'] = False
        reporters = self.pipeline._create_reporters()
        self.assertEqual(len(reporters), 1)
        
        # Test with only markdown reporter
        self.pipeline.config['markdown_report'] = True
        self.pipeline.config['console_report'] = False
        reporters = self.pipeline._create_reporters()
        self.assertEqual(len(reporters), 1)
        
        # Test with no reporters
        self.pipeline.config['markdown_report'] = False
        reporters = self.pipeline._create_reporters()
        self.assertEqual(len(reporters), 0)

    @patch.object(AnalysisPipeline, 'generate_report')
    @patch.object(AnalysisEngine, 'analyze')
    @patch.object(GraphBuilder, 'build_graph')
    @patch.object(FileScanner, 'scan')
    def test_run(self, mock_scan, mock_build_graph, mock_analyze, mock_generate_report):
        """Test the run method of the pipeline."""
        # Set up mock return values
        file_paths = [self.python_file, self.markdown_file]
        mock_scan.return_value = file_paths
        
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph
        
        mock_report = MagicMock()
        mock_analyze.return_value = mock_report
        
        mock_report_path = self.root_dir / "reports" / "report.md"
        mock_generate_report.return_value = mock_report_path
        
        # Run the pipeline
        result = self.pipeline.run()
        
        # Verify the steps were called in the correct order
        mock_scan.assert_called_once()
        mock_build_graph.assert_called_once_with(file_paths)
        mock_analyze.assert_called_once()
        mock_generate_report.assert_called_once()
        
        # Check the returned report
        self.assertEqual(result, mock_report)
        
        # Check that the engine was created
        self.assertIsNotNone(self.pipeline.engine)

    def test_generate_report(self):
        """Test generating reports."""
        # Create a mock report object
        mock_analysis_report = MagicMock(spec=AnalysisReport)
        self.pipeline.report = mock_analysis_report
        
        # Find the actual reporter instances created in setUp
        console_reporter_instance = None
        markdown_reporter_instance = None
        for reporter in self.pipeline.reporters:
            if isinstance(reporter, ConsoleReporter):
                console_reporter_instance = reporter
            elif isinstance(reporter, MarkdownReporter):
                markdown_reporter_instance = reporter
                
        self.assertIsNotNone(console_reporter_instance, "ConsoleReporter instance not found")
        self.assertIsNotNone(markdown_reporter_instance, "MarkdownReporter instance not found")

        # Patch the methods on the specific instances
        with patch.object(markdown_reporter_instance, 'generate_report', return_value=Path("mock_report.md")) as mock_md_generate, \
             patch.object(console_reporter_instance, 'display_report') as mock_console_display:
            
            # Run the method under test
            report_path = self.pipeline.generate_report()
            
            # Assert that the correct methods were called on the instances
            mock_md_generate.assert_called_once_with(mock_analysis_report, Path(self.config["report_dir"]))
            # ConsoleReporter's display_report *is* called by generate_report for non-Markdown reporters.
            mock_console_display.assert_called_once_with(mock_analysis_report)

            # Assert the returned path (comes from the mocked markdown_reporter.generate_report)
            self.assertEqual(report_path, Path("mock_report.md"))


if __name__ == '__main__':
    unittest.main()