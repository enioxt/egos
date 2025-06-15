#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS System Monitor - Test Suite

This script provides comprehensive testing for the EGOS System Monitor,
including time-based filtering, file type categorization, and reporting features.
It follows the EGOS Script Management Best Practices and integrates with pytest.

Part of the EGOS System Monitoring Initiative.

@references: 
- C:\EGOS\scripts\system_monitor\egos_system_monitor.py
- C:\EGOS\ROADMAP.md
- C:\EGOS\WORK_2025_05_21.md
- C:\EGOS\docs\process\script_management_best_practices.md

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0
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
import json
import shutil
import tempfile
import unittest
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

# Add parent directory to path to import system_monitor module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the system monitor module
from egos_system_monitor import (
    EGOSSystemMonitor, 
    FileScanner, 
    SystemHealthReport,
    FileReference
)

class TestFileScanner(unittest.TestCase):
    """Test the FileScanner class functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        # Create a temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test files with different modification times
        self.test_files = {
            "recent_file.txt": 0,                  # Now
            "hour_old_file.py": 1,                 # 1 hour ago
            "day_old_file.md": 24,                 # 24 hours ago
            "week_old_file.json": 168,             # 7 days ago
            "large_file.bin": 0,                   # Now, but large
            "small_file.txt": 0,                   # Now, but small
        }
        
        # Create the test files with specified modification times
        for filename, hours_ago in self.test_files.items():
            file_path = self.test_dir / filename
            
            # Create the file
            with open(file_path, "w") as f:
                # Make large_file.bin 1MB and others small
                if "large" in filename:
                    f.write("X" * 1_000_000)  # 1MB file
                else:
                    f.write("Test content")
            
            # Set modification time
            if hours_ago > 0:
                mtime = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
                os.utime(file_path, (mtime.timestamp(), mtime.timestamp()))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_time_filtering(self):
        """Test that files are correctly filtered based on modification time."""
        # Test with 2 hour threshold
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None,  # No exclusions for testing
            hours_threshold=2
        )
        
        # Scan files
        scanner.scan()
        
        # Should find 3 files: recent_file.txt, hour_old_file.py, large_file.bin, small_file.txt
        self.assertEqual(len(scanner.recent_files), 4)
        
        # Test with 12 hour threshold
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None,
            hours_threshold=12
        )
        
        # Scan files
        scanner.scan()
        
        # Should find 4 files (excluding week_old_file.json)
        self.assertEqual(len(scanner.recent_files), 5)
    
    def test_file_type_filtering(self):
        """Test that files are correctly filtered based on file type."""
        # Test with .txt filter
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None,
            file_type_filter=".txt"
        )
        
        # Scan files
        scanner.scan()
        
        # Should find only .txt files
        self.assertEqual(len(scanner.recent_files), 2)
        for file in scanner.recent_files:
            self.assertTrue(str(file.path).endswith(".txt"))
    
    def test_size_filtering(self):
        """Test that files are correctly filtered based on size."""
        # Test with min_size filter (500KB)
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None,
            min_size=500_000
        )
        
        # Scan files
        scanner.scan()
        
        # Should find only large_file.bin
        self.assertEqual(len(scanner.recent_files), 1)
        self.assertTrue("large_file.bin" in str(scanner.recent_files[0].path))
        
        # Test with max_size filter (100KB)
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None,
            max_size=100_000
        )
        
        # Scan files
        scanner.scan()
        
        # Should find all files except large_file.bin
        self.assertEqual(len(scanner.recent_files), 5)
        for file in scanner.recent_files:
            self.assertFalse("large_file.bin" in str(file.path))
    
    def test_file_type_categorization(self):
        """Test that files are correctly categorized by type."""
        # Create scanner with no filters
        scanner = FileScanner(
            root_path=self.test_dir,
            exclusion_manager=None
        )
        
        # Scan files
        scanner.scan()
        
        # Check file type categorization
        self.assertEqual(scanner.recent_files_by_type.get(".txt", 0), 2)
        self.assertEqual(scanner.recent_files_by_type.get(".py", 0), 1)
        self.assertEqual(scanner.recent_files_by_type.get(".md", 0), 1)
        self.assertEqual(scanner.recent_files_by_type.get(".json", 0), 1)
        self.assertEqual(scanner.recent_files_by_type.get(".bin", 0), 1)


class TestEGOSSystemMonitor(unittest.TestCase):
    """Test the EGOSSystemMonitor class functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        # Create a temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test files with different modification times
        self.test_files = {
            "recent_file.txt": 0,                  # Now
            "hour_old_file.py": 1,                 # 1 hour ago
            "day_old_file.md": 24,                 # 24 hours ago
            "week_old_file.json": 168,             # 7 days ago
        }
        
        # Create the test files with specified modification times
        for filename, hours_ago in self.test_files.items():
            file_path = self.test_dir / filename
            
            # Create the file
            with open(file_path, "w") as f:
                f.write("Test content")
            
            # Set modification time
            if hours_ago > 0:
                mtime = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
                os.utime(file_path, (mtime.timestamp(), mtime.timestamp()))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_report_generation(self):
        """Test that the system monitor generates reports correctly."""
        # Create system monitor with test directory
        monitor = EGOSSystemMonitor(
            root_path=self.test_dir,
            hours_threshold=48,  # Include all but week_old_file.json
            file_type_filter=None,
            min_size=None,
            max_size=None
        )
        
        # Generate report
        report = monitor.generate_report()
        
        # Check report contains expected information
        self.assertIsInstance(report, SystemHealthReport)
        self.assertEqual(len(report.recent_files_list), 3)  # 3 files within 48 hours
        
        # Check file type distribution in report
        self.assertIn(".txt", report.recent_files_by_type)
        self.assertIn(".py", report.recent_files_by_type)
        self.assertIn(".md", report.recent_files_by_type)
    
    def test_report_to_markdown(self):
        """Test that the system monitor generates Markdown reports correctly."""
        # Create system monitor with test directory
        monitor = EGOSSystemMonitor(
            root_path=self.test_dir,
            hours_threshold=48,  # Include all but week_old_file.json
            file_type_filter=None,
            min_size=None,
            max_size=None
        )
        
        # Generate report
        report = monitor.generate_report()
        
        # Convert to Markdown
        markdown = monitor.report_to_markdown(report)
        
        # Check Markdown contains expected sections
        self.assertIn("# EGOS System Health Report", markdown)
        self.assertIn("## Recent File Activity", markdown)
        self.assertIn("## File Type Distribution", markdown)
        
        # Check file type distribution visualization
        self.assertIn("ASCII Bar Chart", markdown)


if __name__ == "__main__":
    unittest.main()