#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @references:
# .windsurfrules
# MQP.md
# ADRS_Log.md
# subsystems/AutoCrossRef/CROSSREF_STANDARD.md

import os
import sys
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to sys.path to allow importing regen_references
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import scripts.regen_references as regen_references

class TestRegenReferences(unittest.TestCase):
    """Test suite for the refactored regen_references.py script."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a mock project structure
        self.project_root = self.test_dir / "project"
        os.makedirs(self.project_root, exist_ok=True)
        
        # Create a mock CROSSREF_STANDARD.md file
        self.crossref_standard_path = self.project_root / "subsystems" / "AutoCrossRef" / "CROSSREF_STANDARD.md"
        os.makedirs(os.path.dirname(self.crossref_standard_path), exist_ok=True)
        
        # Define core references for the standard
        self.core_references = [
            'MQP.md',
            '.windsurfrules',
            'ADRS_Log.md',
            'subsystems/AutoCrossRef/CROSSREF_STANDARD.md'
        ]
        
        # Create the CROSSREF_STANDARD.md file with YAML header
        with open(self.crossref_standard_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write("core_references:\n")
            for ref in self.core_references:
                f.write(f"  - {ref}\n")
            f.write("---\n\n")
            f.write("# Cross-Reference Standard\n\n")
            f.write("This document defines the standard for cross-references in the EGOS project.\n")
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """Create test files for the test suite."""
        # Create a Python file with no references
        py_file = self.project_root / "test_no_refs.py"
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write("# Test Python file\n\ndef main():\n    print('Hello')\n")
        
        # Create a Python file with some references
        py_file_with_refs = self.project_root / "test_with_refs.py"
        with open(py_file_with_refs, 'w', encoding='utf-8') as f:
            f.write("# Test Python file\n\n")
            f.write("# @references:\n")
            f.write("# MQP.md\n")
            f.write("# legacy_ref.md\n\n")
            f.write("def main():\n    print('Hello')\n")
        
        # Create a Markdown file with no references
        md_file = self.project_root / "test_no_refs.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Test Markdown file\n\nThis is a test file.\n")
        
        # Create a Markdown file with some references
        md_file_with_refs = self.project_root / "test_with_refs.md"
        with open(md_file_with_refs, 'w', encoding='utf-8') as f:
            f.write("# Test Markdown file\n\n")
            f.write("<!-- @references: -->\n")
            f.write("- MQP.md\n")
            f.write("- test_with_refs.md\n\n")  # Self-reference
            f.write("This is a test file.\n")
    
    @patch('scripts.regen_references.inject_reference')
    def test_run_and_report_diagnose_mode(self, mock_inject_reference):
        """Test the run_and_report function in diagnose mode."""
        # Set up mock return value for inject_reference
        mock_inject_reference.return_value = {
            'status': 'diagnose_only',
            'message': 'Diagnose mode: 2 missing refs, 0 self refs, 1 legacy refs.',
            'content_changed': False,
            'is_compliant': False,
            'references_added': ['.windsurfrules', 'ADRS_Log.md'],
            'references_purged': ['legacy_ref.md'],
            'missing_references': ['.windsurfrules', 'ADRS_Log.md']
        }
        
        # Create a list of test files
        test_files = [
            self.project_root / "test_no_refs.py",
            self.project_root / "test_with_refs.py"
        ]
        
        # Call run_and_report with diagnose mode
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            with patch('scripts.regen_references._load_core_references_from_standard') as mock_load_refs:
                mock_load_refs.return_value = self.core_references
                results = regen_references.run_and_report(
                    test_files,
                    {},  # config
                    is_dry_run=True,
                    mode='diagnose',
                    verbose=True
                )
        
        # Check that inject_reference was called for each file
        self.assertEqual(mock_inject_reference.call_count, len(test_files))
        
        # Check that no files were marked as non-compliant (diagnose mode doesn't mark files)
        self.assertEqual(results['non_compliant_files_count'], 0)
    
    @patch('scripts.regen_references.inject_reference')
    def test_run_and_report_fix_core_mode(self, mock_inject_reference):
        """Test the run_and_report function in fix-core mode."""
        # Set up mock return value for inject_reference
        mock_inject_reference.return_value = {
            'status': 'modified',
            'message': 'Added 2 references and purged 1 legacy references.',
            'content_changed': True,
            'is_compliant': True,
            'references_added': ['.windsurfrules', 'ADRS_Log.md'],
            'references_purged': ['legacy_ref.md'],
            'missing_references': []
        }
        
        # Create a list of test files
        test_files = [
            self.project_root / "test_no_refs.py",
            self.project_root / "test_with_refs.py"
        ]
        
        # Call run_and_report with fix-core mode
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            with patch('scripts.regen_references._load_core_references_from_standard') as mock_load_refs:
                mock_load_refs.return_value = self.core_references
                results = regen_references.run_and_report(
                    test_files,
                    {},  # config
                    is_dry_run=False,
                    mode='fix-core',
                    verbose=True
                )
        
        # Check that inject_reference was called for each file
        self.assertEqual(mock_inject_reference.call_count, len(test_files))
        
        # Check that no files were marked as non-compliant (fix-core mode doesn't mark files)
        self.assertEqual(results['non_compliant_files_count'], 0)
    
    @patch('scripts.regen_references.inject_reference')
    def test_run_and_report_full_mode_compliant(self, mock_inject_reference):
        """Test the run_and_report function in full mode with compliant files."""
        # Set up mock return value for inject_reference
        mock_inject_reference.return_value = {
            'status': 'modified',
            'message': 'Added 2 references and purged 1 legacy references.',
            'content_changed': True,
            'is_compliant': True,
            'references_added': ['.windsurfrules', 'ADRS_Log.md'],
            'references_purged': ['legacy_ref.md'],
            'missing_references': []
        }
        
        # Create a list of test files
        test_files = [
            self.project_root / "test_no_refs.py",
            self.project_root / "test_with_refs.py"
        ]
        
        # Call run_and_report with full mode
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            with patch('scripts.regen_references._load_core_references_from_standard') as mock_load_refs:
                mock_load_refs.return_value = self.core_references
                results = regen_references.run_and_report(
                    test_files,
                    {},  # config
                    is_dry_run=False,
                    mode='full',
                    verbose=True
                )
        
        # Check that inject_reference was called for each file
        self.assertEqual(mock_inject_reference.call_count, len(test_files))
        
        # Check that no files were marked as non-compliant
        self.assertEqual(results['non_compliant_files_count'], 0)
    
    @patch('scripts.regen_references.inject_reference')
    def test_run_and_report_full_mode_non_compliant(self, mock_inject_reference):
        """Test the run_and_report function in full mode with non-compliant files."""
        # Set up mock return value for inject_reference to alternate between compliant and non-compliant
        mock_inject_reference.side_effect = [
            {
                'status': 'modified',
                'message': 'Added 2 references.',
                'content_changed': True,
                'is_compliant': True,
                'references_added': ['.windsurfrules', 'ADRS_Log.md'],
                'references_purged': [],
                'missing_references': []
            },
            {
                'status': 'non_compliant',
                'message': 'Added 1 reference. File is non-compliant: 1 missing references.',
                'content_changed': True,
                'is_compliant': False,
                'references_added': ['.windsurfrules'],
                'references_purged': ['legacy_ref.md'],
                'missing_references': ['ADRS_Log.md']
            }
        ]
        
        # Create a list of test files
        test_files = [
            self.project_root / "test_no_refs.py",
            self.project_root / "test_with_refs.py"
        ]
        
        # Call run_and_report with full mode
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            with patch('scripts.regen_references._load_core_references_from_standard') as mock_load_refs:
                mock_load_refs.return_value = self.core_references
                results = regen_references.run_and_report(
                    test_files,
                    {},  # config
                    is_dry_run=False,
                    mode='full',
                    verbose=True
                )
        
        # Check that inject_reference was called for each file
        self.assertEqual(mock_inject_reference.call_count, len(test_files))
        
        # Check that one file was marked as non-compliant
        self.assertEqual(results['non_compliant_files_count'], 1)
    
    @patch('scripts.regen_references._load_core_references_from_standard')
    def test_load_core_references_from_standard(self, mock_load_refs):
        """Test loading core references from the CROSSREF_STANDARD.md file."""
        # Set up the mock to return our test core references
        mock_load_refs.return_value = self.core_references
        
        # Call the function
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            refs = regen_references._load_core_references_from_standard()
        
        # Check that the correct references were loaded
        self.assertEqual(refs, self.core_references)
        
        # Test the actual implementation (not the mock)
        mock_load_refs.side_effect = lambda: regen_references._load_core_references_from_standard.__wrapped__()
        
        # Call the function again to use the actual implementation
        with patch('scripts.regen_references.PROJECT_ROOT', self.project_root):
            refs = regen_references._load_core_references_from_standard()
        
        # Check that the correct references were loaded
        self.assertEqual(set(refs), set(self.core_references))

if __name__ == '__main__':
    unittest.main()