#!/usr/bin/env python3
"""
EGOS Orchestrator Improvement Cycle
Runs comprehensive testing, monitors results, and implements fixes
"""

import os
import sys
import time
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from monitor import OrchestratorMonitor
from orchestrator import (
    call_alibaba, call_openrouter, call_groq, call_claude_cli,
    PROVIDERS
)

test_prompt = "Responda em 1 linha: qual seu nome e para que serve?"

def test_provider(monitor, provider_name, test_fn, model_name, max_retries=2):
    """Test a single provider with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"  [{attempt+1}/{max_retries}] {provider_name}/{model_name}...", end='', flush=True)

            start = time.time()
            result = test_fn(test_prompt, "fast")
            elapsed = time.time() - start

            success = result.get("success", False)
            error = result.get("error")
            cost = 0

            monitor.log_call(
                provider_name, model_name,
                prompt_tokens=50, output_tokens=30,
                latency=elapsed,
                success=success,
                error=error,
                cost=cost
            )

            if success:
                print(f" ✅ {elapsed:.2f}s")
                return True
            else:
                print(f" ❌ {error[:40]}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                continue

        except Exception as e:
            print(f" 💥 {str(e)[:40]}")
            if attempt < max_retries - 1:
                time.sleep(2)
            continue

    return False

def run_improvement_cycle():
    """Full testing and improvement cycle"""
    monitor = OrchestratorMonitor()

    print("\n" + "="*80)
    print("🔄 EGOS ORCHESTRATOR IMPROVEMENT CYCLE")
    print("="*80)
    print(f"Test prompt: '{test_prompt}'")
    print()

    results = defaultdict(lambda: {"success": 0, "failed": 0})

    # Test each provider
    print("📊 TESTING PROVIDERS:")
    print()

    # 1. Alibaba
    print("🟢 ALIBABA DASHSCOPE")
    if not os.getenv("ALIBABA_DASHSCOPE_API_KEY"):
        print("  ⚠️  ALIBABA_DASHSCOPE_API_KEY not set — skipping")
    else:
        for model in ["fast", "medium"]:
            ok = test_provider(monitor, "alibaba", call_alibaba, model)
            key = "success" if ok else "failed"
            results["alibaba"][key] += 1
    print()

    # 2. OpenRouter Free
    print("🟢 OPENROUTER FREE")
    if not os.getenv("OPENROUTER_API_KEY"):
        print("  ⚠️  OPENROUTER_API_KEY not set — skipping")
    else:
        for model in ["nano", "fast", "medium"]:
            ok = test_provider(monitor, "openrouter_free", call_openrouter, model)
            key = "success" if ok else "failed"
            results["openrouter_free"][key] += 1
            time.sleep(1)  # Rate limiting
    print()

    # 3. Groq (expect failures from VPS)
    print("🔴 GROQ (expected: VPS IP blocking)")
    if not os.getenv("GROQ_API_KEY"):
        print("  ⚠️  GROQ_API_KEY not set — skipping")
    else:
        ok = test_provider(monitor, "groq", call_groq, "whisper")
        key = "success" if ok else "failed"
        results["groq"][key] += 1
    print()

    # 4. Claude CLI
    print("🟡 CLAUDE CLI (local)")
    for model in ["fast", "medium"]:
        ok = test_provider(monitor, "claude_cli", call_claude_cli, model)
        key = "success" if ok else "failed"
        results["claude_cli"][key] += 1
    print()

    # Print results
    print("\n" + "="*80)
    print("📈 IMPROVEMENT CYCLE RESULTS")
    print("="*80)
    print()

    stats = monitor.get_stats()

    for provider, pstats in stats.get("by_provider", {}).items():
        print(f"\n{provider.upper()}:")
        for key, val in pstats.items():
            print(f"  {key}: {val}")

    # Generate recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    print()

    issues = []

    # Check for Groq blocking
    groq_calls = [c for c in monitor.calls if c["provider"] == "groq"]
    groq_errors = [c for c in groq_calls if not c["success"]]
    if groq_errors:
        error_msg = groq_errors[0]["error"]
        if "403" in str(error_msg):
            issues.append("🔴 Groq blocked (403) — VPS datacenter IP. Mark as transcription-only.")

    # Check for rate limiting
    openrouter_errors = [c for c in monitor.calls if c["provider"] == "openrouter_free" and not c["success"]]
    if any("429" in str(c["error"]) for c in openrouter_errors):
        issues.append("⚠️  OpenRouter 429 Rate Limited — Add 2-3s delay between requests")

    # Check for missing keys
    for c in monitor.calls:
        if "not set" in str(c["error"]).lower():
            issues.append(f"🔑 Missing key: {c['error']}")

    if not issues:
        print("✅ All tests passing! System is healthy.")
    else:
        for issue in issues:
            print(f"  • {issue}")

    print()
    print("📊 DASHBOARD:")
    monitor.print_dashboard()

    return monitor, results

if __name__ == "__main__":
    run_improvement_cycle()
