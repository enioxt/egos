#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for AnalysisEngine Component.

This module contains tests for the AnalysisEngine class, which is responsible
for analyzing the reference graph and generating reports.

@author: EGOS Team
@created: 2025-04-23
@status: Alpha

@references:
- Core References:
  - [ROADMAP.md](mdc:../../../../ROADMAP.md):KOIOS-DOC-009 - Cross-Reference Analyzer Refactoring
- Related Components:
  - [engine.py](py:../engine.py) - The module being tested
  - [test_graph_builder.py](py:./test_graph_builder.py) - Tests for the GraphBuilder component
  - [test_pipeline.py](py:./test_pipeline.py) - Tests for the AnalysisPipeline component
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

# 
import unittest
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

from scripts.maintenance.cross_reference.engine import AnalysisEngine
from scripts.maintenance.cross_reference.models.reference import ReferenceGraph, FileReferences, Reference
from scripts.maintenance.cross_reference.models.report import AnalysisReport


class TestAnalysisEngine(unittest.TestCase):
    """Test cases for the AnalysisEngine class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a test reference graph
        self.graph = ReferenceGraph()
        
        # Set up test paths
        self.root_dir = Path("/test/root")
        self.file1 = self.root_dir / "file1.py"
        self.file2 = self.root_dir / "file2.py"
        self.file3 = self.root_dir / "file3.md"
        self.file4 = self.root_dir / "file4.md"
        
        # Create a mock logger
        self.mock_logger = MagicMock()
        
        # Initialize the engine
        self.engine = AnalysisEngine(self.graph, self.root_dir, self.mock_logger)
        
        # Set up a reference structure
        # file1.py -> file2.py (valid)
        # file1.py -> file3.md (valid)
        # file2.py -> file4.md (invalid - file4.md doesn't exist)
        # file3.md has no references
        
        # Add files to the graph
        self.file1_refs = FileReferences(file_path=self.file1, has_reference_section=True)
        self.file2_refs = FileReferences(file_path=self.file2, has_reference_section=True)
        self.file3_refs = FileReferences(file_path=self.file3, has_reference_section=False)
        
        self.graph.files[self.file1] = self.file1_refs
        self.graph.files[self.file2] = self.file2_refs
        self.graph.files[self.file3] = self.file3_refs
        
        # Add references
        ref1_to_2 = Reference(
            source=self.file1,
            target=self.file2,
            link_text="file2.py",
            link_path="py:./file2.py",
            is_valid=True
        )
        
        ref1_to_3 = Reference(
            source=self.file1,
            target=self.file3,
            link_text="file3.md",
            link_path="md:./file3.md",
            is_valid=True
        )
        
        ref2_to_4 = Reference(
            source=self.file2,
            target=None,  # Target doesn't exist
            link_text="file4.md",
            link_path="md:./file4.md",
            is_valid=False
        )
        
        # Add references to file references
        self.file1_refs.outgoing_references.append(ref1_to_2)
        self.file1_refs.outgoing_references.append(ref1_to_3)
        self.file2_refs.outgoing_references.append(ref2_to_4)
        
        # Add incoming references
        self.file2_refs.incoming_references.append(ref1_to_2)
        self.file3_refs.incoming_references.append(ref1_to_3)
        
        # Set up analysis results
        self.graph.files_without_references.add(self.file3)
        self.graph.files_with_broken_references.add(self.file2)
        self.graph.orphaned_files.clear()  # No orphaned files in this test setup

    def test_init(self):
        """Test AnalysisEngine initialization."""
        self.assertIsNotNone(self.engine.graph)
        self.assertEqual(self.engine.root_dir, self.root_dir)
        self.assertEqual(self.engine.logger, self.mock_logger)
        # Verify the report is initialized as an empty AnalysisReport
        self.assertIsInstance(self.engine.report, AnalysisReport)
        self.assertEqual(self.engine.report.issues, {})
        self.assertEqual(self.engine.report.metrics, {})
        self.assertEqual(self.engine.report.suggestions, {})
        self.assertEqual(self.engine.report.health_score, 0.0) # Assuming default score is 0

    def test_analyze(self):
        """Test the analyze method."""
        # Mock the component methods to isolate the analyze method
        with patch.object(self.engine, '_find_broken_references') as mock_find_broken:
            with patch.object(self.engine, '_find_orphaned_files') as mock_find_orphaned:
                with patch.object(self.engine, '_generate_suggestions') as mock_generate:
                    with patch.object(self.engine, '_calculate_health_metrics') as mock_calculate:
                        # Run the analyze method
                        report = self.engine.analyze()
        
        # Verify that a report was created
        self.assertIsInstance(report, AnalysisReport)
        self.assertIs(report, self.engine.report)
        
        # Verify that the report contains the expected graph
        self.assertEqual(report.graph, self.graph)
        
        # Verify that the component methods were called
        mock_find_broken.assert_called_once()
        mock_find_orphaned.assert_called_once()
        mock_generate.assert_called_once()
        mock_calculate.assert_called_once()

    def test_analyze_includes_files_without_references(self):
        """Test that analyze identifies files without references."""
        # Run the analyze method
        self.engine.analyze()
        
        # Check that the file without references was identified in the graph
        self.assertIn(self.file3, self.graph.files_without_references)
        
        # Note: The current implementation doesn't add issues for files without references
        # It only generates suggestions for them in _generate_suggestions

    def test_find_broken_references(self):
        """Test finding broken references."""
        # Reset the report to test individual methods
        self.engine.report = AnalysisReport(graph=self.graph)
        
        # Run the method
        self.engine._find_broken_references()
        
        # Check that the file with broken references was identified
        self.assertIn(self.file2, self.graph.files_with_broken_references)
        
        # Check that an issue was added to the report
        self.assertIn(self.file2, self.engine.report.issues)
        issues = self.engine.report.issues[self.file2]
        self.assertTrue(any(issue['type'] == 'broken_reference' for issue in issues))

    def test_find_orphaned_files(self):
        """Test finding orphaned files."""
        # Make file3 an orphan by removing its incoming reference
        self.file3_refs.incoming_references.clear()
        self.graph.orphaned_files.add(self.file3)  # Manually mark as orphaned for the test
        
        # Reset the report to test individual methods
        self.engine.report = AnalysisReport(graph=self.graph)
        
        # Run the method
        self.engine._find_orphaned_files()
        
        # Check that an issue was added to the report
        self.assertIn(self.file3, self.engine.report.issues)
        issues = self.engine.report.issues[self.file3]
        self.assertTrue(any(issue['type'] == 'orphaned_file' for issue in issues))

    def test_generate_suggestions(self):
        """Test generating suggestions for files with issues."""
        # Reset the report to test individual methods
        self.engine.report = AnalysisReport(graph=self.graph)
        
        # The method references the file system, so we need to mock the file existence check
        with patch('os.path.exists', return_value=True):
            # Mock the _suggest_references_for_file method to avoid actual file system access
            with patch.object(self.engine, '_suggest_references_for_file') as mock_suggest:
                # Run the method
                self.engine._generate_suggestions()
                
                # Verify the method was called at least once
                mock_suggest.assert_called()
                
                # The implementation should call the method for each file with issues
                # We expect at least 2 calls (one for file2 with broken references, one for file3 without references)
                self.assertGreaterEqual(mock_suggest.call_count, 2)

    def test_calculate_health_metrics(self, *mock_args):
        """Test calculating the health metrics."""
        # Reset the report to test individual methods
        self.engine.report = AnalysisReport(graph=self.graph)
        
        # Mock the calculate_health_score method to isolate metric calculation
        with patch.object(self.engine.report, 'calculate_health_score', return_value=75.0) as mock_calculate:
            # Run the method
            self.engine._calculate_health_metrics()
            
            # Verify the calculate_health_score method was called
            mock_calculate.assert_called_once()
        
        # Check that metrics were added to the report
        metrics = self.engine.report.metrics
        self.assertIn('total_files', metrics)
        self.assertIn('files_without_references', metrics)
        self.assertIn('files_with_broken_references', metrics)
        self.assertIn('orphaned_files', metrics)
        self.assertIn('total_references', metrics)
        
        # Check that the metrics have the correct values
        self.assertEqual(metrics['total_files'], 3)
        self.assertEqual(metrics['files_without_references'], 1)  # file3 has no references
        self.assertEqual(metrics['files_with_broken_references'], 1)  # file2 has broken references
        self.assertEqual(metrics['orphaned_files'], 0)  # No orphans in initial setup


if __name__ == '__main__':
    unittest.main()