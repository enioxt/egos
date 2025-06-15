#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Health Check Framework - Test Runner

This script runs all the tests for the EGOS Health Check Framework.
It discovers and executes all test cases in the tests directory.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\MQP.md (Evolutionary Preservation, Conscious Modularity)
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
import logging
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_check.tests")

def print_banner():
    """Print a banner for the test runner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║             EGOS Health Check Framework - Test Runner         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    # Get the tests directory
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def main():
    """Main function for running tests."""
    print_banner()
    
    logger.info("Discovering and running tests...")
    result = discover_and_run_tests()
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())