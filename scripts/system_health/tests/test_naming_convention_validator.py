#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Health Check Framework - Naming Convention Validator Tests

This module contains unit tests for the naming convention validator component
of the EGOS Health Check Framework.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
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
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import validator
from validators.naming_convention_validator import NamingConventionValidator
from core.base_validator import IssueSeverity

class TestNamingConventionValidator(unittest.TestCase):
    """Test cases for the naming convention validator."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create validator with test configuration
        self.validator = NamingConventionValidator({
            "exclusions": {
                "directories": [".git", "venv", "__pycache__"],
                "files": ["README.md", "LICENSE"],
                "extensions_to_ignore": [],
                "patterns_to_ignore": []
            }
        })
        
        # Create test files with various naming patterns
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files with various naming patterns."""
        # Create directories
        os.makedirs(os.path.join(self.test_dir, "snake_case_dir"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "PascalCaseDir"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "camelCaseDir"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "UPPERCASE_DIR"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "kebab-case-dir"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "Mixed-caseDir"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, ".git"), exist_ok=True)  # Should be excluded
        
        # Create files
        self.create_file(os.path.join(self.test_dir, "snake_case_file.py"))
        self.create_file(os.path.join(self.test_dir, "PascalCaseFile.py"))
        self.create_file(os.path.join(self.test_dir, "camelCaseFile.py"))
        self.create_file(os.path.join(self.test_dir, "UPPERCASE_FILE.py"))
        self.create_file(os.path.join(self.test_dir, "kebab-case-file.py"))
        self.create_file(os.path.join(self.test_dir, "Mixed-caseFile.py"))
        self.create_file(os.path.join(self.test_dir, "README.md"))  # Should be excluded
    
    def create_file(self, path):
        """Create a file with some content."""
        with open(path, 'w') as f:
            f.write("# Test file\n")
    
    def test_is_snake_case(self):
        """Test the is_snake_case method."""
        self.assertTrue(self.validator.is_snake_case("snake_case"))
        self.assertTrue(self.validator.is_snake_case("snake_case.py"))
        self.assertTrue(self.validator.is_snake_case("snake123_case.py"))
        
        self.assertFalse(self.validator.is_snake_case("PascalCase"))
        self.assertFalse(self.validator.is_snake_case("camelCase"))
        self.assertFalse(self.validator.is_snake_case("UPPERCASE"))
        self.assertFalse(self.validator.is_snake_case("kebab-case"))
        self.assertFalse(self.validator.is_snake_case("Mixed-case"))
    
    def test_identify_pattern_type(self):
        """Test the identify_pattern_type method."""
        self.assertEqual(self.validator.identify_pattern_type("UPPERCASE"), "UPPERCASE_TO_LOWERCASE")
        self.assertEqual(self.validator.identify_pattern_type("PascalCase"), "PASCALCASE_TO_SNAKE_CASE")
        self.assertEqual(self.validator.identify_pattern_type("camelCase"), "CAMELCASE_TO_SNAKE_CASE")
        self.assertEqual(self.validator.identify_pattern_type("kebab-case"), "KEBABCASE_TO_SNAKE_CASE")
        self.assertEqual(self.validator.identify_pattern_type("Mixed-case"), "MIXED_PATTERN")
    
    def test_string_to_snake_case(self):
        """Test the string_to_snake_case method."""
        self.assertEqual(self.validator.string_to_snake_case("snake_case"), "snake_case")
        self.assertEqual(self.validator.string_to_snake_case("PascalCase"), "pascal_case")
        self.assertEqual(self.validator.string_to_snake_case("camelCase"), "camel_case")
        self.assertEqual(self.validator.string_to_snake_case("UPPERCASE"), "uppercase")
        self.assertEqual(self.validator.string_to_snake_case("kebab-case"), "kebab_case")
        self.assertEqual(self.validator.string_to_snake_case("Mixed-case"), "mixed_case")
        
        # Test with file extensions
        self.assertEqual(self.validator.string_to_snake_case("PascalCase.py"), "pascal_case.py")
        self.assertEqual(self.validator.string_to_snake_case("camelCase.py"), "camel_case.py")
    
    def test_should_exclude(self):
        """Test the should_exclude method."""
        exclusions = {
            "directories": [".git", "venv", "__pycache__"],
            "files": ["README.md", "LICENSE"],
            "extensions_to_ignore": [".md"],
            "patterns_to_ignore": [r".*\.git.*"]
        }
        
        # Test directories
        self.assertTrue(self.validator.should_exclude(Path(".git/file.txt"), exclusions))
        self.assertTrue(self.validator.should_exclude(Path("venv/lib/file.txt"), exclusions))
        self.assertFalse(self.validator.should_exclude(Path("src/file.txt"), exclusions))
        
        # Test files
        self.assertTrue(self.validator.should_exclude(Path("README.md"), exclusions))
        self.assertTrue(self.validator.should_exclude(Path("LICENSE"), exclusions))
        self.assertFalse(self.validator.should_exclude(Path("file.py"), exclusions))
        
        # Test extensions
        self.assertTrue(self.validator.should_exclude(Path("file.md"), exclusions))
        self.assertFalse(self.validator.should_exclude(Path("file.py"), exclusions))
        
        # Test patterns
        self.assertTrue(self.validator.should_exclude(Path("something.git/file.txt"), exclusions))
        self.assertFalse(self.validator.should_exclude(Path("something/file.txt"), exclusions))
    
    def test_validate(self):
        """Test the validate method."""
        # Run validation
        results = self.validator.validate(self.test_dir)
        
        # Check results
        self.assertEqual(results.validator_name, "naming_convention")
        
        # We should have 10 non-compliant items (5 directories and 5 files)
        # excluding .git directory and README.md file
        self.assertEqual(len(results.issues), 10)
        
        # Check pattern types in metadata
        pattern_types = results.metadata.get("pattern_types", {})
        self.assertEqual(pattern_types.get("PASCALCASE_TO_SNAKE_CASE", 0), 2)  # PascalCaseDir, PascalCaseFile.py
        self.assertEqual(pattern_types.get("CAMELCASE_TO_SNAKE_CASE", 0), 2)   # camelCaseDir, camelCaseFile.py
        self.assertEqual(pattern_types.get("UPPERCASE_TO_LOWERCASE", 0), 2)     # UPPERCASE_DIR, UPPERCASE_FILE.py
        self.assertEqual(pattern_types.get("KEBABCASE_TO_SNAKE_CASE", 0), 2)    # kebab-case-dir, kebab-case-file.py
        self.assertEqual(pattern_types.get("MIXED_PATTERN", 0), 2)              # Mixed-caseDir, Mixed-caseFile.py
        
        # Check severity levels
        directory_issues = [issue for issue in results.issues if "Dir" in issue.path or "dir" in issue.path]
        file_issues = [issue for issue in results.issues if ".py" in issue.path]
        
        for issue in directory_issues:
            self.assertEqual(issue.severity, IssueSeverity.ERROR)
        
        for issue in file_issues:
            self.assertEqual(issue.severity, IssueSeverity.WARNING)
    
    def test_fix(self):
        """Test the fix method with dry run."""
        # Run validation
        results = self.validator.validate(self.test_dir)
        
        # Fix issues with dry run
        fix_results = self.validator.fix(results.issues, dry_run=True)
        
        # Check fix results
        self.assertEqual(fix_results["total"], 10)
        self.assertEqual(fix_results["successful"], 10)
        self.assertEqual(fix_results["failed"], 0)
        
        # Check that files were not actually renamed (dry run)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "PascalCaseDir")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "camelCaseDir")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "PascalCaseFile.py")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "camelCaseFile.py")))

if __name__ == "__main__":
    unittest.main()