#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Cross-Reference Tools - Test Runner

This script runs all tests for the EGOS cross-reference tools and generates
a comprehensive test report.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║                  EGOS Cross-Reference Tools Test Runner                      ║
# ║                                                                              ║
# ║  Runs all tests for the EGOS cross-reference tools                           ║
# ║                                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Standard library imports
import os
import sys
import time
import unittest
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    if not 'Fore' in globals():
        Fore = DummyColorama()
    if not 'Style' in globals():
        Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
TEST_DIR = Path(__file__).parent / "tests"
REPORT_DIR = Path(__file__).parent / "test_reports"

def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a banner with the given title and optional subtitle.
    
    Args:
        title: The title to display in the banner
        subtitle: Optional subtitle to display below the title
    """
    print("\n" + "╔" + "═" * (BANNER_WIDTH - 2) + "╗")
    print("║" + " " * (BANNER_WIDTH - 2) + "║")
    
    # Center the title
    title_padding = (BANNER_WIDTH - 2 - len(title)) // 2
    print("║" + " " * title_padding + title + " " * (BANNER_WIDTH - 2 - len(title) - title_padding) + "║")
    
    if subtitle:
        # Center the subtitle
        subtitle_padding = (BANNER_WIDTH - 2 - len(subtitle)) // 2
        print("║" + " " * subtitle_padding + subtitle + " " * (BANNER_WIDTH - 2 - len(subtitle) - subtitle_padding) + "║")
    
    print("║" + " " * (BANNER_WIDTH - 2) + "║")
    print("╚" + "═" * (BANNER_WIDTH - 2) + "╝")

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)} minutes, {remaining_seconds:.2f} seconds"
    else:
        hours = seconds // 3600
        remaining = seconds % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{int(hours)} hours, {int(minutes)} minutes, {seconds:.2f} seconds"

def discover_tests() -> unittest.TestSuite:
    """Discover all tests in the tests directory.
    
    Returns:
        TestSuite containing all discovered tests
    """
    loader = unittest.TestLoader()
    return loader.discover(str(TEST_DIR), pattern="test_*.py")

def run_tests(verbosity: int = 2) -> unittest.TestResult:
    """Run all discovered tests.
    
    Args:
        verbosity: Verbosity level for test output
        
    Returns:
        TestResult containing test results
    """
    # Create test suite
    test_suite = discover_tests()
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    # Run tests
    print(f"\n{Fore.CYAN}Running {test_suite.countTestCases()} tests...{Style.RESET_ALL}")
    start_time = time.time()
    result = runner.run(test_suite)
    end_time = time.time()
    
    # Print summary
    print(f"\n{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
    print(f"  • {Fore.GREEN}Tests run:{Style.RESET_ALL} {result.testsRun}")
    print(f"  • {Fore.GREEN}Tests passed:{Style.RESET_ALL} {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  • {Fore.RED}Tests failed:{Style.RESET_ALL} {len(result.failures)}")
    print(f"  • {Fore.RED}Tests errored:{Style.RESET_ALL} {len(result.errors)}")
    print(f"  • {Fore.CYAN}Time taken:{Style.RESET_ALL} {format_time(end_time - start_time)}")
    
    return result

def generate_html_report(result: unittest.TestResult) -> Path:
    """Generate an HTML report of test results.
    
    Args:
        result: TestResult containing test results
        
    Returns:
        Path to the generated HTML report
    """
    # Create report directory if it doesn't exist
    REPORT_DIR.mkdir(exist_ok=True)
    
    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"test_report_{timestamp}.html"
    
    # Generate HTML report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>EGOS Cross-Reference Tools Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #333; }
        .summary { display: flex; flex-wrap: wrap; margin-bottom: 20px; }
        .stat-card { background-color: #f5f5f5; border-radius: 5px; padding: 15px; margin: 10px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 24px; font-weight: bold; }
        .stat-label { font-size: 14px; color: #666; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
        .errored { color: #fd7e14; }
        .info { color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        .failure, .error { background-color: #fff3f3; }
        .details { background-color: #f9f9f9; padding: 10px; border-left: 4px solid #ddd; white-space: pre-wrap; }
        .toggle-details { color: #007bff; cursor: pointer; text-decoration: underline; }
        .hidden { display: none; }
    </style>
    <script>
        function toggleDetails(id) {
            var element = document.getElementById(id);
            if(element.classList.contains('hidden')) {
                element.classList.remove('hidden');
            } else {
                element.classList.add('hidden');
            }
        }
    </script>
</head>
<body>
    <h1>EGOS Cross-Reference Tools Test Report</h1>
    <p>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    
    <h2>Summary</h2>
    <div class="summary">
        <div class="stat-card">
            <div class="stat-value info">""" + str(result.testsRun) + """</div>
            <div class="stat-label">Tests Run</div>
        </div>
        <div class="stat-card">
            <div class="stat-value passed">""" + str(result.testsRun - len(result.failures) - len(result.errors)) + """</div>
            <div class="stat-label">Tests Passed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value failed">""" + str(len(result.failures)) + """</div>
            <div class="stat-label">Tests Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value errored">""" + str(len(result.errors)) + """</div>
            <div class="stat-label">Tests Errored</div>
        </div>
    </div>
    """)
        
        # Add failures section if there are any failures
        if result.failures:
            f.write("""
    <h2>Failures</h2>
    <table>
        <tr>
            <th>Test</th>
            <th>Details</th>
        </tr>
    """)
            
            for i, (test, traceback) in enumerate(result.failures):
                f.write(f"""
        <tr class="failure">
            <td>{test}</td>
            <td>
                <span class="toggle-details" onclick="toggleDetails('failure-{i}')">Show details</span>
                <div id="failure-{i}" class="details hidden">{traceback}</div>
            </td>
        </tr>
    """)
            
            f.write("</table>")
        
        # Add errors section if there are any errors
        if result.errors:
            f.write("""
    <h2>Errors</h2>
    <table>
        <tr>
            <th>Test</th>
            <th>Details</th>
        </tr>
    """)
            
            for i, (test, traceback) in enumerate(result.errors):
                f.write(f"""
        <tr class="error">
            <td>{test}</td>
            <td>
                <span class="toggle-details" onclick="toggleDetails('error-{i}')">Show details</span>
                <div id="error-{i}" class="details hidden">{traceback}</div>
            </td>
        </tr>
    """)
            
            f.write("</table>")
        
        # Add footer
        f.write("""
    <footer>
        <p>Generated by EGOS Cross-Reference Tools Test Runner</p>
        <p>✧༺❀༻∞ EGOS ∞༺❀༻✧</p>
    </footer>
</body>
</html>
""")
    
    return report_path

def main():
    """Main entry point for the script."""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="EGOS Cross-Reference Tools Test Runner")
        parser.add_argument("--verbosity", "-v", type=int, choices=[0, 1, 2], default=2, help="Verbosity level for test output")
        parser.add_argument("--html-report", "-r", action="store_true", help="Generate HTML report")
        
        args = parser.parse_args()
        
        # Print banner
        print_banner("EGOS Cross-Reference Tools Test Runner", "Running tests for all cross-reference tools")
        
        # Run tests
        result = run_tests(verbosity=args.verbosity)
        
        # Generate HTML report if requested
        if args.html_report:
            report_path = generate_html_report(result)
            print(f"\n{Fore.CYAN}HTML report generated:{Style.RESET_ALL} {report_path}")
        
        # Print conclusion
        if result.wasSuccessful():
            print(f"\n{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
            print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
            sys.exit(0)
        else:
            print(f"\n{Fore.RED}Some tests failed or errored.{Style.RESET_ALL}")
            print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()