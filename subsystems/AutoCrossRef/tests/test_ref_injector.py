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
from pathlib import Path
from typing import Dict, Any, List

# Add the parent directory to sys.path to allow importing the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ref_injector import inject_reference

class TestRefInjector(unittest.TestCase):
    """Test suite for the refactored inject_reference function."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a config dictionary for testing
        self.config = {
            'backup_options': {
                'enabled': True,
                'directory': str(self.test_dir / "backups"),
                'timestamp_format': '%Y%m%d_%H%M%S'
            }
        }
        
        # Create backup directory
        os.makedirs(self.config['backup_options']['directory'], exist_ok=True)
        
        # Define core references for testing
        self.core_references = [
            'MQP.md',
            '.windsurfrules',
            'ADRS_Log.md',
            'subsystems/AutoCrossRef/CROSSREF_STANDARD.md'
        ]
    
    def tearDown(self):
        """Clean up after each test."""
        self.temp_dir.cleanup()
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with the given content."""
        file_path = self.test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_inject_reference_legacy_mode(self):
        """Test the legacy mode of inject_reference (single reference injection)."""
        # Create a test Python file with no references
        test_file = self.create_test_file("test_legacy.py", "# Test file\n\ndef main():\n    print('Hello')\n")
        
        # Inject a reference in legacy mode
        result = inject_reference(
            str(test_file),
            'MQP.md',
            str(self.test_dir / 'MQP.md'),
            self.config,
            is_dry_run=False
        )
        
        # Check the result
        self.assertEqual(result['status'], 'modified')
        self.assertTrue(result['content_changed'])
        self.assertEqual(len(result['references_added']), 1)
        self.assertEqual(result['references_added'][0], 'MQP.md')
        
        # Verify the file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# @references:', content)
        self.assertIn('# MQP.md', content)
    
    def test_inject_reference_standard_mode_new_file(self):
        """Test standard mode with a file that has no existing references."""
        # Create a test Python file with no references
        test_file = self.create_test_file("test_standard_new.py", "# Test file\n\ndef main():\n    print('Hello')\n")
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules', 'ADRS_Log.md']
        
        # Inject references in standard mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='fix-core'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'modified')
        self.assertTrue(result['content_changed'])
        self.assertEqual(len(result['references_added']), 3)
        self.assertTrue(all(ref in result['references_added'] for ref in refs_to_ensure))
        
        # Verify the file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# @references:', content)
        for ref in refs_to_ensure:
            self.assertIn(f'# {ref}', content)
    
    def test_inject_reference_standard_mode_existing_refs(self):
        """Test standard mode with a file that has existing references."""
        # Create a test Python file with some existing references
        test_file = self.create_test_file(
            "test_standard_existing.py", 
            "# Test file\n\n# @references:\n# MQP.md\n# legacy_ref.md\n\ndef main():\n    print('Hello')\n"
        )
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules', 'ADRS_Log.md']
        
        # Inject references in standard mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='fix-core'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'modified')
        self.assertTrue(result['content_changed'])
        self.assertEqual(len(result['references_purged']), 1)  # legacy_ref.md should be purged
        self.assertEqual(result['references_purged'][0], 'legacy_ref.md')
        
        # Verify the file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# @references:', content)
        for ref in refs_to_ensure:
            self.assertIn(f'# {ref}', content)
        self.assertNotIn('# legacy_ref.md', content)
    
    def test_inject_reference_self_reference_removal(self):
        """Test that self-references are properly removed."""
        # Create a test file with a self-reference
        file_name = "test_self_ref.py"
        test_file = self.create_test_file(
            file_name, 
            f"# Test file\n\n# @references:\n# MQP.md\n# {file_name}\n\ndef main():\n    print('Hello')\n"
        )
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules']
        
        # Inject references in standard mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='fix-core'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'modified')
        self.assertTrue(result['content_changed'])
        self.assertEqual(len(result['references_purged']), 1)  # self-reference should be purged
        self.assertEqual(result['references_purged'][0], file_name)
        
        # Verify the file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# @references:', content)
        for ref in refs_to_ensure:
            self.assertIn(f'# {ref}', content)
        self.assertNotIn(f'# {file_name}', content)
    
    def test_inject_reference_diagnose_mode(self):
        """Test diagnose mode (dry run)."""
        # Create a test file with some existing references
        test_file = self.create_test_file(
            "test_diagnose.py", 
            "# Test file\n\n# @references:\n# MQP.md\n# legacy_ref.md\n\ndef main():\n    print('Hello')\n"
        )
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules', 'ADRS_Log.md']
        
        # Inject references in diagnose mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,  # This should be overridden by mode='diagnose'
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='diagnose'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'diagnose_only')
        self.assertFalse(result['content_changed'])
        self.assertEqual(len(result['references_purged']), 1)  # legacy_ref.md should be identified for purging
        
        # Verify the file content is unchanged
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# legacy_ref.md', content)  # Legacy ref should still be there
    
    def test_inject_reference_full_mode_compliant(self):
        """Test full mode with a compliant file."""
        # Create a test file with all required references
        test_file = self.create_test_file(
            "test_full_compliant.py", 
            "# Test file\n\n# @references:\n# MQP.md\n# .windsurfrules\n# ADRS_Log.md\n\ndef main():\n    print('Hello')\n"
        )
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules', 'ADRS_Log.md']
        
        # Inject references in full mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='full'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'skipped_idempotent')
        self.assertFalse(result['content_changed'])
        self.assertTrue(result['is_compliant'])
    
    def test_inject_reference_full_mode_non_compliant(self):
        """Test full mode with a non-compliant file."""
        # Create a test file with missing references
        test_file = self.create_test_file(
            "test_full_non_compliant.py", 
            "# Test file\n\n# @references:\n# MQP.md\n\ndef main():\n    print('Hello')\n"
        )
        
        # Define references to ensure for this file
        refs_to_ensure = ['MQP.md', '.windsurfrules', 'ADRS_Log.md']
        
        # Inject references in full mode
        result = inject_reference(
            str(test_file),
            '',  # Not used in standard mode
            '',  # Not used in standard mode
            self.config,
            is_dry_run=False,
            references_to_ensure=refs_to_ensure,
            all_valid_core_refs=self.core_references,
            mode='full'
        )
        
        # Check the result
        self.assertEqual(result['status'], 'modified')
        self.assertTrue(result['content_changed'])
        self.assertTrue(result['is_compliant'])  # Should be compliant after modification
        
        # Verify the file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        for ref in refs_to_ensure:
            self.assertIn(f'# {ref}', content)

if __name__ == '__main__':
    unittest.main()