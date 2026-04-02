#!/usr/bin/env python3
"""
EGOS-TELEM-005: Monthly cost forecasting and budget alerts.
Queries guard_brasil_events from last 30 days, fits trend, projects monthly burn.
Output: CSV with daily totals + forecast, alerts if > budget.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Optional
import math

# Stub implementation (would use Supabase SDK in production)
def query_supabase_events(days: int = 30) -> list:
    """Query Supabase guard_brasil_events for last N days."""
    # Returns list of {timestamp, cost_usd} events
    # In production: use supabase.table('guard_brasil_events').select('*').gte('timestamp', since).execute()
    return []

def aggregate_by_day(events: list) -> dict:
    """Group events by day, sum cost_usd."""
    daily_costs = {}
    for evt in events:
        if 'timestamp' not in evt:
            continue
        day = evt['timestamp'][:10]  # YYYY-MM-DD
        cost = evt.get('cost_usd', 0)
        daily_costs[day] = daily_costs.get(day, 0) + cost
    return dict(sorted(daily_costs.items()))

def fit_trend(daily_costs: dict) -> tuple:
    """Fit linear trend: y = mx + b. Returns (slope, intercept, r_squared)."""
    if len(daily_costs) < 2:
        return (0, 0, 0)
    
    x_vals = list(range(len(daily_costs)))
    y_vals = list(daily_costs.values())
    n = len(x_vals)
    
    mean_x = sum(x_vals) / n
    mean_y = sum(y_vals) / n
    
    numerator = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n))
    denominator = sum((x_vals[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return (0, mean_y, 0)
    
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    
    # R-squared
    ss_tot = sum((y - mean_y) ** 2 for y in y_vals)
    ss_res = sum((y_vals[i] - (slope * x_vals[i] + intercept)) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    return (slope, intercept, r_squared)

def forecast_monthly_cost(daily_costs: dict) -> dict:
    """Project 30-day cost based on trend."""
    if not daily_costs:
        return {'forecast_daily_avg': 0, 'forecast_30day_total': 0, 'trend_slope': 0}
    
    slope, intercept, r_squared = fit_trend(daily_costs)
    
    # Average daily cost from historical data
    avg_daily = sum(daily_costs.values()) / len(daily_costs) if daily_costs else 0
    
    # Project next 30 days using trend (if strong signal) else use average
    if r_squared > 0.5 and len(daily_costs) >= 7:
        # Use trend for forecast
        future_indices = list(range(len(daily_costs), len(daily_costs) + 30))
        projected_daily_costs = [slope * x + intercept for x in future_indices]
        forecast_30day = sum(max(0, c) for c in projected_daily_costs)  # No negative costs
    else:
        # Use average (conservative)
        forecast_30day = avg_daily * 30
    
    return {
        'forecast_daily_avg': round(avg_daily, 8),
        'forecast_30day_total': round(forecast_30day, 8),
        'trend_slope': round(slope, 10),
        'r_squared': round(r_squared, 3),
        'data_points': len(daily_costs)
    }

def alert_if_over_budget(forecast: dict, budget_usd: float = 100.0) -> Optional[str]:
    """Alert if 30-day forecast exceeds budget."""
    if forecast['forecast_30day_total'] > budget_usd:
        return f"⚠️  BUDGET ALERT: Projected monthly cost (${forecast['forecast_30day_total']:.2f}) exceeds budget (${budget_usd:.2f})"
    return None

def main():
    budget_usd = float(os.environ.get('TELEMETRY_BUDGET_USD', '100.0'))
    
    print("📊 EGOS Telemetry Cost Forecast (30-day projection)")
    print(f"   Budget: ${budget_usd:.2f}")
    print()
    
    # Query last 30 days
    events = query_supabase_events(days=30)
    if not events:
        print("⚠️  No telemetry events found in last 30 days. Using placeholder data for demo.")
        # Demo: simulate 10 days of cost data
        today = datetime.now()
        events = [
            {'timestamp': (today - timedelta(days=i)).isoformat(), 'cost_usd': 0.05 + (i * 0.01)}
            for i in range(10)
        ]
    
    daily_costs = aggregate_by_day(events)
    forecast = forecast_monthly_cost(daily_costs)
    alert = alert_if_over_budget(forecast, budget_usd)
    
    # Output
    print(json.dumps(forecast, indent=2))
    if alert:
        print(f"\n{alert}")
    
    # CSV output
    csv_path = os.environ.get('TELEMETRY_FORECAST_OUTPUT', '/tmp/forecast.csv')
    with open(csv_path, 'w') as f:
        f.write("date,daily_cost_usd\n")
        for day, cost in daily_costs.items():
            f.write(f"{day},{cost}\n")
    print(f"\n✅ CSV saved to: {csv_path}")
    
    return 0 if not alert else 1

if __name__ == '__main__':
    sys.exit(main())
