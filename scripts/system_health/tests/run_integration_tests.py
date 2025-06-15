#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS File Duplication Integration Test Runner

This script runs integration tests for the File Duplication Auditor
and its integration with the Cross-Reference system.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\scripts\maintenance\file_duplication_auditor.py
- C:\EGOS\scripts\maintenance\integration\duplication_xref_integration.py
- C:\EGOS\scripts\maintenance\tests\test_duplication_integration.py
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
import unittest
import logging
from pathlib import Path

# Add parent directories to path to allow imports
parent_dir = str(Path(__file__).parent.parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("integration_test_runner")

# Import test class directly from the same directory
from test_duplication_integration import TestDuplicationIntegration

def print_banner(title, subtitle=None):
    """
    Print a visually appealing banner.
    
    Args:
        title: Title to display in the banner
        subtitle: Optional subtitle to display
    """
    width = 80
    print("╔" + "═" * (width - 2) + "╗")
    print("║" + " " * (width - 2) + "║")
    print("║" + title.center(width - 2) + "║")
    if subtitle:
        print("║" + subtitle.center(width - 2) + "║")
    print("║" + " " * (width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")
    print()

def main():
    """
    Main entry point for the test runner.
    """
    print_banner("EGOS File Duplication Integration Tests", "Testing Cross-Reference Integration")
    
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestDuplicationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Print EGOS signature
    print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())