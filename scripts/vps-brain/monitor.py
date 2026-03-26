#!/usr/bin/env python3
"""
EGOS Orchestrator Monitor & Performance Analytics
Real-time tracking of all API calls, costs, errors, latency, and quality metrics.
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
BENCHMARKS_DIR = RESULTS_DIR / "benchmarks"
MONITOR_LOG = RESULTS_DIR / "monitor.jsonl"
STATS_FILE = RESULTS_DIR / "stats.json"

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)
BENCHMARKS_DIR.mkdir(exist_ok=True)


class OrchestratorMonitor:
    def __init__(self):
        self.calls = []
        self.errors = []
        self.costs = defaultdict(float)
        self.latencies = defaultdict(list)
        self.success_rates = defaultdict(int)
        self.total_calls = defaultdict(int)
        self.load_history()

    def load_history(self):
        """Load previous metrics from monitor log"""
        if MONITOR_LOG.exists():
            try:
                with open(MONITOR_LOG) as f:
                    for line in f:
                        if line.strip():
                            record = json.loads(line)
                            self.calls.append(record)
            except:
                pass

    def log_call(self, provider: str, model: str, prompt_tokens: int, output_tokens: int,
                 latency: float, success: bool, error: str = None, cost: float = 0):
        """Log an API call"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "latency": latency,
            "success": success,
            "error": error,
            "cost": cost,
        }

        # Append to log
        with open(MONITOR_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")

        # Update metrics
        self.calls.append(record)
        self.costs[provider] += cost
        self.latencies[provider].append(latency)
        self.total_calls[provider] += 1
        if success:
            self.success_rates[provider] += 1
        else:
            self.errors.append((provider, model, error, datetime.now().isoformat()))

    def get_stats(self):
        """Calculate real-time statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_calls": sum(self.total_calls.values()),
                "total_cost": sum(self.costs.values()),
                "total_errors": len(self.errors),
                "uptime_hours": (len(self.calls) / max(sum(self.total_calls.values()), 1)) * 100,
            },
            "by_provider": {},
            "recent_errors": self.errors[-10:] if self.errors else [],
            "cost_breakdown": dict(self.costs),
            "performance": {},
        }

        # Per-provider stats
        for provider in self.total_calls:
            total = self.total_calls[provider]
            success = self.success_rates[provider]
            lats = self.latencies[provider]

            stats["by_provider"][provider] = {
                "calls": total,
                "success_rate": f"{(success/total*100):.1f}%",
                "avg_latency": f"{statistics.mean(lats):.2f}s" if lats else "N/A",
                "p95_latency": f"{sorted(lats)[int(len(lats)*0.95)]:.2f}s" if lats else "N/A",
                "cost": f"${self.costs[provider]:.4f}",
            }

            stats["performance"][provider] = {
                "throughput_tokens_per_sec": sum(
                    r["output_tokens"] / r["latency"]
                    for r in self.calls
                    if r["provider"] == provider and r["latency"] > 0
                ) / max(sum(1 for r in self.calls if r["provider"] == provider), 1),
            }

        return stats

    def print_dashboard(self):
        """Print real-time dashboard"""
        stats = self.get_stats()

        print("\n" + "="*80)
        print("🔍 EGOS ORCHESTRATOR MONITOR — REAL-TIME DASHBOARD")
        print("="*80)
        print(f"⏰ {stats['timestamp']}")

        print("\n📊 OVERALL STATS:")
        print(f"  Total Calls: {stats['summary']['total_calls']}")
        print(f"  Total Cost: ${stats['summary']['total_cost']:.4f}")
        print(f"  Total Errors: {stats['summary']['total_errors']}")
        print(f"  Global Success Rate: {stats['summary']['uptime_hours']:.1f}%")

        print("\n🏢 BY PROVIDER:")
        for provider, pstats in stats["by_provider"].items():
            print(f"\n  {provider.upper()}")
            for key, val in pstats.items():
                print(f"    {key}: {val}")

        print("\n⚠️  RECENT ERRORS (Last 5):")
        if stats['recent_errors']:
            for provider, model, error, ts in stats['recent_errors'][-5:]:
                print(f"  [{ts}] {provider}/{model}: {error[:60]}")
        else:
            print("  ✅ No errors")

        # Save to file
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)

        print("\n" + "="*80)
        return stats


def run_benchmark_suite():
    """Execute full benchmark suite with monitoring"""
    monitor = OrchestratorMonitor()

    print("\n🚀 STARTING ORCHESTRATOR BENCHMARK SUITE")
    print("=" * 80)

    # Import orchestrator
    import sys
    sys.path.insert(0, str(BASE_DIR))
    from orchestrator import (
        call_alibaba, call_openrouter, call_groq, call_claude_cli,
        test_all_providers, PROVIDERS
    )

    test_prompt = "Responda em 1 linha: qual seu nome e para que serve?"

    # Test Alibaba
    print("\n📡 Testing Alibaba DashScope...")
    start = time.time()
    result = call_alibaba(test_prompt, "fast")
    elapsed = time.time() - start
    monitor.log_call(
        "alibaba", "qwen-plus",
        prompt_tokens=50, output_tokens=30,
        latency=elapsed,
        success=result.get("success", False),
        error=result.get("error"),
        cost=0  # Free quota
    )
    if result.get("success"):
        print(f"✅ Alibaba: {result['content'][:60]}... ({elapsed:.2f}s)")
    else:
        print(f"❌ Alibaba failed: {result.get('error')}")

    # Test OpenRouter free
    print("\n📡 Testing OpenRouter Free Tier...")
    start = time.time()
    result = call_openrouter(test_prompt, "medium")
    elapsed = time.time() - start
    monitor.log_call(
        "openrouter_free", "gemma-3-12b",
        prompt_tokens=50, output_tokens=40,
        latency=elapsed,
        success=result.get("success", False),
        error=result.get("error"),
        cost=0  # Free
    )
    if result.get("success"):
        print(f"✅ OpenRouter Free: {result['content'][:60]}... ({elapsed:.2f}s)")
    else:
        print(f"❌ OpenRouter failed: {result.get('error')}")

    # Test Claude CLI
    print("\n📡 Testing Claude CLI Pro...")
    start = time.time()
    result = call_claude_cli(test_prompt, "fast")
    elapsed = time.time() - start
    monitor.log_call(
        "claude_cli", "haiku-4.5",
        prompt_tokens=50, output_tokens=35,
        latency=elapsed,
        success=result.get("success", False),
        error=result.get("error"),
        cost=0.0015  # Approximate
    )
    if result.get("success"):
        print(f"✅ Claude CLI: {result['content'][:60]}... ({elapsed:.2f}s)")
    else:
        print(f"❌ Claude CLI failed: {result.get('error')}")

    # Full provider test
    print("\n📡 Running full provider benchmark...")
    test_all_providers()

    # Print dashboard
    monitor.print_dashboard()

    return monitor


def analyze_errors(last_n_hours: int = 24):
    """Analyze error patterns from the last N hours"""
    monitor = OrchestratorMonitor()

    cutoff = datetime.now() - timedelta(hours=last_n_hours)
    recent_errors = [
        e for e in monitor.errors
        if datetime.fromisoformat(e[3]) > cutoff
    ]

    print(f"\n🔍 ERROR ANALYSIS (Last {last_n_hours}h)")
    print("=" * 80)

    error_by_provider = defaultdict(list)
    for provider, model, error, ts in recent_errors:
        error_by_provider[provider].append(error)

    for provider, errors in error_by_provider.items():
        print(f"\n{provider.upper()}:")
        error_counts = defaultdict(int)
        for err in errors:
            # Group similar errors
            if "403" in str(err):
                error_counts["403 Forbidden (IP blocked)"] += 1
            elif "429" in str(err):
                error_counts["429 Rate Limited"] += 1
            elif "401" in str(err):
                error_counts["401 Unauthorized (key invalid)"] += 1
            elif "404" in str(err):
                error_counts["404 Not Found (model deprecated)"] += 1
            else:
                error_counts[str(err)[:50]] += 1

        for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1]):
            print(f"  • {error_type}: {count}x")


def optimize_recommendations(monitor: OrchestratorMonitor):
    """Generate optimization recommendations based on real data"""
    stats = monitor.get_stats()

    print("\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    # Analyze cost vs quality
    for provider, pstats in stats["by_provider"].items():
        success_rate = float(pstats["success_rate"].rstrip("%"))
        cost = float(pstats["cost"].lstrip("$"))

        if success_rate < 50:
            print(f"\n⚠️  {provider}: LOW SUCCESS RATE ({success_rate:.1f}%)")
            print(f"  → Action: Disable or reduce traffic to this provider")

        if cost > 0.10 and success_rate < 95:
            print(f"\n⚠️  {provider}: HIGH COST ({cost:.4f}) WITH ERRORS")
            print(f"  → Action: Evaluate cheaper alternatives (Gemini Flash-Lite: $0.075/M)")

    # Check latency
    avg_latencies = {
        p: statistics.mean(monitor.latencies[p])
        for p in monitor.latencies if monitor.latencies[p]
    }

    fastest = min(avg_latencies.items(), key=lambda x: x[1]) if avg_latencies else None
    slowest = max(avg_latencies.items(), key=lambda x: x[1]) if avg_latencies else None

    if fastest and slowest:
        print(f"\n⚡ LATENCY ANALYSIS:")
        print(f"  Fastest: {fastest[0]} ({fastest[1]:.2f}s)")
        print(f"  Slowest: {slowest[0]} ({slowest[1]:.2f}s)")
        if slowest[1] > 10:
            print(f"  → Action: {slowest[0]} is too slow for real-time tasks")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "run":
            monitor = run_benchmark_suite()
        elif command == "errors":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            analyze_errors(hours)
        elif command == "optimize":
            monitor = OrchestratorMonitor()
            optimize_recommendations(monitor)
        elif command == "status":
            monitor = OrchestratorMonitor()
            monitor.print_dashboard()
    else:
        print("EGOS Orchestrator Monitor")
        print("Usage:")
        print("  python3 monitor.py run       — Run full benchmark & collect metrics")
        print("  python3 monitor.py status    — Show current stats dashboard")
        print("  python3 monitor.py errors [N] — Analyze errors from last N hours")
        print("  python3 monitor.py optimize  — Get optimization recommendations")
