#!/usr/bin/env python3
"""
ATRiAN EaaS API - Audit Endpoint Performance Monitor
---------------------------------------------------
This tool monitors the performance of the /ethics/audit endpoint with various query parameters
and result set sizes. It helps identify potential performance bottlenecks and provides
metrics for optimizing the endpoint's performance.

Usage:
    python audit_performance_monitor.py [--base-url BASE_URL] [--runs RUNS] [--max-limit MAX_LIMIT]

Author: Cascade AI Assistant
Date: 2025-06-02
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

import argparse
import csv
import datetime
import json
import os
import statistics
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests
from rich.console import Console
from rich.table import Table

# Constants
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_RUNS = 5
DEFAULT_MAX_LIMIT = 1000
AUDIT_ENDPOINT = "/ethics/audit"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "performance")


class AuditPerformanceMonitor:
    """Monitor and analyze the performance of the audit endpoint."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, runs: int = DEFAULT_RUNS, max_limit: int = DEFAULT_MAX_LIMIT):
        """Initialize the performance monitor.

        Args:
            base_url: Base URL of the ATRiAN EaaS API
            runs: Number of runs for each test case
            max_limit: Maximum limit parameter to test
        """
        self.base_url = base_url
        self.runs = runs
        self.max_limit = max_limit
        self.console = Console()
        
        # Ensure results directory exists
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = os.path.join(RESULTS_DIR, f"audit_performance_{self.timestamp}.csv")
        self.summary_file = os.path.join(RESULTS_DIR, f"audit_performance_summary_{self.timestamp}.json")
        
        # Initialize results storage
        self.results = []
        self.summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "base_url": base_url,
            "runs": runs,
            "max_limit": max_limit,
            "test_cases": [],
            "overall_metrics": {}
        }

    def run_test_case(self, name: str, params: Dict[str, any]) -> Dict[str, any]:
        """Run a single test case multiple times and collect metrics.

        Args:
            name: Name of the test case
            params: Query parameters for the API call

        Returns:
            Dictionary with test case metrics
        """
        self.console.print(f"[bold blue]Running test case:[/bold blue] {name}")
        
        url = f"{self.base_url}{AUDIT_ENDPOINT}"
        response_times = []
        log_counts = []
        status_codes = []
        errors = []
        
        for i in range(self.runs):
            self.console.print(f"  Run {i+1}/{self.runs}...", end="")
            
            start_time = time.time()
            try:
                response = requests.get(url, params=params, timeout=30)
                status_codes.append(response.status_code)
                
                if response.status_code == 200:
                    data = response.json()
                    log_counts.append(len(data.get("logs", [])))
                else:
                    errors.append(f"HTTP {response.status_code}: {response.text}")
                    log_counts.append(0)
            except Exception as e:
                errors.append(str(e))
                status_codes.append(0)
                log_counts.append(0)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            self.console.print(f" completed in {response_time:.2f}ms")
        
        # Calculate metrics
        metrics = {
            "test_case": name,
            "params": params,
            "runs": self.runs,
            "status_codes": status_codes,
            "success_rate": (status_codes.count(200) / self.runs) * 100,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "median_response_time_ms": statistics.median(response_times) if response_times else 0,
            "stdev_response_time_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "avg_log_count": statistics.mean(log_counts) if log_counts else 0,
            "errors": errors
        }
        
        # Store individual run results
        for i in range(self.runs):
            result = {
                "timestamp": datetime.datetime.now().isoformat(),
                "test_case": name,
                "run": i + 1,
                "params": json.dumps(params),
                "response_time_ms": response_times[i] if i < len(response_times) else None,
                "status_code": status_codes[i] if i < len(status_codes) else None,
                "log_count": log_counts[i] if i < len(log_counts) else None,
                "error": errors[i] if i < len(errors) else None
            }
            self.results.append(result)
        
        # Add to summary
        self.summary["test_cases"].append(metrics)
        
        return metrics

    def run_all_tests(self):
        """Run all predefined test cases."""
        # Test case 1: Default parameters
        self.run_test_case("Default Parameters", {})
        
        # Test case 2: Various limit values
        for limit in [10, 50, 100, 500, self.max_limit]:
            self.run_test_case(f"Limit {limit}", {"limit": limit})
        
        # Test case 3: Pagination
        for offset in [0, 10, 50, 100]:
            self.run_test_case(f"Pagination (offset={offset}, limit=10)", {"offset": offset, "limit": 10})
        
        # Test case 4: Filtering by action type
        self.run_test_case("Filter by Action Type", {"action_type": "retrieve_audit_logs", "limit": 100})
        
        # Test case 5: Filtering by user
        self.run_test_case("Filter by User", {"user_id": "anonymous", "limit": 100})
        
        # Test case 6: Date range filtering
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        now = datetime.datetime.now().isoformat()
        self.run_test_case("Date Range Filter", {
            "start_date": yesterday,
            "end_date": now,
            "limit": 100
        })
        
        # Test case 7: Combined filters
        self.run_test_case("Combined Filters", {
            "action_type": "retrieve_audit_logs",
            "user_id": "anonymous",
            "start_date": yesterday,
            "limit": 100
        })
        
        # Calculate overall metrics
        response_times = [result["response_time_ms"] for result in self.results if result["response_time_ms"] is not None]
        status_codes = [result["status_code"] for result in self.results if result["status_code"] is not None]
        
        self.summary["overall_metrics"] = {
            "total_runs": len(self.results),
            "success_rate": (status_codes.count(200) / len(status_codes)) * 100 if status_codes else 0,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "median_response_time_ms": statistics.median(response_times) if response_times else 0,
            "stdev_response_time_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0
        }

    def save_results(self):
        """Save test results to CSV and summary to JSON."""
        # Ensure performance directory exists
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        # Save detailed results to CSV
        with open(self.results_file, 'w', newline='') as csvfile:
            fieldnames = self.results[0].keys() if self.results else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        # Save summary to JSON
        with open(self.summary_file, 'w') as jsonfile:
            json.dump(self.summary, jsonfile, indent=2)
        
        self.console.print(f"[bold green]Results saved to:[/bold green]")
        self.console.print(f"  - CSV: {self.results_file}")
        self.console.print(f"  - JSON: {self.summary_file}")

    def display_summary(self):
        """Display a summary of the test results."""
        self.console.print("\n[bold]Overall Performance Summary[/bold]")
        
        overall = self.summary["overall_metrics"]
        self.console.print(f"Total Runs: {overall['total_runs']}")
        self.console.print(f"Success Rate: {overall['success_rate']:.2f}%")
        self.console.print(f"Average Response Time: {overall['avg_response_time_ms']:.2f}ms")
        self.console.print(f"Median Response Time: {overall['median_response_time_ms']:.2f}ms")
        self.console.print(f"Min/Max Response Time: {overall['min_response_time_ms']:.2f}ms / {overall['max_response_time_ms']:.2f}ms")
        
        # Create a table for test case summaries
        table = Table(title="Test Case Performance")
        table.add_column("Test Case", style="cyan")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg Time (ms)", style="yellow")
        table.add_column("Avg Log Count", style="magenta")
        
        for test_case in self.summary["test_cases"]:
            table.add_row(
                test_case["test_case"],
                f"{test_case['success_rate']:.2f}%",
                f"{test_case['avg_response_time_ms']:.2f}",
                f"{test_case['avg_log_count']:.1f}"
            )
        
        self.console.print(table)
        
        # Performance recommendations
        self.console.print("\n[bold]Performance Recommendations:[/bold]")
        slow_threshold = overall['median_response_time_ms'] * 2
        slow_cases = [tc for tc in self.summary["test_cases"] if tc['avg_response_time_ms'] > slow_threshold]
        
        if slow_cases:
            self.console.print("[yellow]Potential Performance Issues Detected:[/yellow]")
            for case in slow_cases:
                self.console.print(f"  - [yellow]{case['test_case']}[/yellow]: {case['avg_response_time_ms']:.2f}ms (above threshold of {slow_threshold:.2f}ms)")
                self.console.print(f"    Parameters: {case['params']}")
        else:
            self.console.print("[green]No significant performance issues detected.[/green]")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Monitor the performance of the ATRiAN EaaS API audit endpoint")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL of the ATRiAN EaaS API (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help=f"Number of runs for each test case (default: {DEFAULT_RUNS})")
    parser.add_argument("--max-limit", type=int, default=DEFAULT_MAX_LIMIT, help=f"Maximum limit parameter to test (default: {DEFAULT_MAX_LIMIT})")
    
    args = parser.parse_args()
    
    console = Console()
    console.print("[bold]ATRiAN EaaS API - Audit Endpoint Performance Monitor[/bold]")
    console.print(f"Base URL: {args.base_url}")
    console.print(f"Runs per test case: {args.runs}")
    console.print(f"Maximum limit: {args.max_limit}")
    console.print("=" * 50)
    
    monitor = AuditPerformanceMonitor(args.base_url, args.runs, args.max_limit)
    
    try:
        monitor.run_all_tests()
        monitor.save_results()
        monitor.display_summary()
    except KeyboardInterrupt:
        console.print("\n[bold red]Test interrupted by user.[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()