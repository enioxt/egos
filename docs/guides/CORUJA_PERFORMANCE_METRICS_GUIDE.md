---
title: CORUJA_PERFORMANCE_METRICS_GUIDE
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: coruja_performance_metrics_guide
tags: [documentation]
---
---
title: CORUJA_PERFORMANCE_METRICS_GUIDE
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: CORUJA_PERFORMANCE_METRICS_GUIDE
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: CORUJA Performance Metrics Guide
date: 2025-05-01
status: Active
tags: [CORUJA, performance, metrics, monitoring, guide]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - [MQP](../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Implementation:
  - [performance_metrics.py](../../..\subsystems\CORUJA\adapters\performance_metrics.py)
  - [mycelium_adapter.py](../../..\subsystems\CORUJA\adapters\mycelium_adapter.py)
  - [performance_analysis_example.py](../../..\subsystems\CORUJA\examples\performance_analysis_example.py)
---
  - docs/guides/CORUJA_PERFORMANCE_METRICS_GUIDE.md

# CORUJA Performance Metrics Guide

This guide explains how to use the CORUJA Performance Metrics system to monitor, analyze, and optimize the performance of CORUJA subsystem operations, particularly focusing on the CORUJA-MYCELIUM integration.

## Overview

The CORUJA Performance Metrics system provides:

- **Comprehensive metrics collection**: Latency, error rates, throughput, and custom metrics
- **Statistical analysis**: Min, max, avg, median, percentiles
- **Time-based filtering**: Analyze metrics over specific time windows
- **Circuit breaker monitoring**: Track state changes and performance
- **Decorators for easy instrumentation**: For both synchronous and asynchronous functions
- **Thread-safe implementation**: For concurrent environments
- **Low overhead design**: Minimal impact on application performance

## Getting Started

### Basic Usage

The simplest way to use the metrics system is through the global metrics instance:

```python
from subsystems.CORUJA.adapters import get_performance_metrics

# Get the global metrics instance
metrics = get_performance_metrics()

# Record a latency sample
metrics.record_latency("operation_name", 150.0)  # 150ms

# Record an error
metrics.record_error("operation_name", "ConnectionError")

# Record a request
metrics.record_request("operation_name")

# Get statistics
latency_stats = metrics.get_latency_statistics("operation_name")
print(f"Average latency: {latency_stats['avg']}ms")
```

### Using with CORUJA-MYCELIUM Adapter

The CORUJA-MYCELIUM adapter is already integrated with the metrics system. When you create an adapter using the factory function, it automatically uses the global metrics instance:

```python
from subsystems.CORUJA.adapters import create_mycelium_adapter

async def example():
    # Create an adapter with metrics enabled
    adapter = await create_mycelium_adapter()
    
    # The adapter will automatically record metrics for all operations
    request_id = await adapter.send_reasoning_request(
        problem_statement="How to implement feature X?",
        context={"existing_code": "..."}
    )
    
    response = await adapter.wait_for_response(request_id)
    
    # Get all metrics collected
    all_metrics = adapter.get_metrics()
    print(f"Average latency: {all_metrics['latency']['send_reasoning_request']['avg']}ms")
```

### Using Decorators

You can use decorators to easily instrument your functions:

```python
from subsystems.CORUJA.adapters import get_performance_metrics
from subsystems.CORUJA.adapters.performance_metrics import measure_latency, measure_async_latency

metrics = get_performance_metrics()

# For synchronous functions
@measure_latency("my_operation", metrics)
def my_function(arg1, arg2):
    # Function code...
    return result

# For asynchronous functions
@measure_async_latency("my_async_operation", metrics)
async def my_async_function(arg1, arg2):
    # Async function code...
    return result
```

## Available Metrics

### 1. Latency Metrics

Latency metrics measure the time it takes to complete an operation:

```python
# Record a latency sample
metrics.record_latency("operation_name", 150.0)  # 150ms

# Get latency statistics
stats = metrics.get_latency_statistics("operation_name")
print(f"Min: {stats['min']}ms")
print(f"Max: {stats['max']}ms")
print(f"Average: {stats['avg']}ms")
print(f"Median: {stats['median']}ms")
print(f"90th percentile: {stats['p90']}ms")
print(f"95th percentile: {stats['p95']}ms")
print(f"99th percentile: {stats['p99']}ms")
```

### 2. Error Metrics

Error metrics track the occurrence of errors by type:

```python
# Record an error
metrics.record_error("operation_name", "ConnectionError")

# Get error statistics
error_stats = metrics.get_error_statistics()
for operation, errors in error_stats.items():
    print(f"Operation: {operation}")
    for error_type, count in errors.items():
        print(f"  {error_type}: {count}")
```

### 3. Throughput Metrics

Throughput metrics measure the number of operations per second:

```python
# Record a request
metrics.record_request("operation_name")

# Get throughput
throughput = metrics.get_throughput("operation_name")
print(f"Throughput: {throughput} requests/second")
```

### 4. Circuit Breaker Metrics

Circuit breaker metrics track the state changes of circuit breakers:

```python
# Record a circuit breaker state change
metrics.record_circuit_state_change(
    "circuit_name",
    "open",
    "Failure threshold exceeded"
)

# Get circuit breaker statistics
circuit_stats = metrics.get_circuit_breaker_statistics("circuit_name")
print(f"Current state: {circuit_stats['circuit_name']['current_state']}")
print(f"State changes: {circuit_stats['circuit_name']['total_changes']}")
print(f"Mean time between changes: {circuit_stats['circuit_name']['mean_time_between_state_changes']}s")
```

### 5. Custom Metrics

Custom metrics allow you to track any value:

```python
# Record a custom metric
metrics.record_custom_metric("payload_size", 1024)
```

## Time-based Filtering

You can filter metrics by time window:

```python
# Get statistics for the last 10 minutes
time_window = 600  # seconds
stats = metrics.get_latency_statistics("operation_name", time_window=time_window)
```

## Comprehensive Analysis

To get all statistics in a single call:

```python
# Get all statistics
all_stats = metrics.get_all_statistics()
```

## Example: Performance Analysis Script

The CORUJA subsystem includes a performance analysis example script that demonstrates how to:

1. Simulate different workloads
2. Collect and analyze metrics
3. Compare performance across different scenarios
4. Generate comprehensive reports

To run the script:

```bash
python -m subsystems.CORUJA.examples.performance_analysis_example --requests 50 --concurrency 10 --context-size medium --scenarios baseline high_concurrency large_payload
```

The script provides output like:

```
CORUJA-MYCELIUM PERFORMANCE METRICS REPORT
===============================================================================

LATENCY STATISTICS (milliseconds):
--------------------------------------------------------------------------------
Operation                 Min      Avg      Median   p90      p95      p99      Max      Count   
--------------------------------------------------------------------------------
send_reasoning_request    10.25    15.67    14.89    20.15    22.48    24.92    25.18    50      
wait_for_response         200.45   215.32   210.67   235.14   240.88   245.67   250.21   50      
handle_reasoning_response 5.12     7.89     7.45     10.24    12.56    15.33    18.45    50      

THROUGHPUT STATISTICS (requests/second):
--------------------------------------------------
send_reasoning_request    25.12
wait_for_response         25.08
publish_message           25.15

...
```

## Integration with Monitoring Systems

The metrics system is designed to be easily integrated with external monitoring systems like Prometheus, Grafana, or DataDog. Future enhancements will include exporters for these systems.

## Best Practices

1. **Use descriptive operation names**: Choose clear, consistent names for operations to make analysis easier.
2. **Record at appropriate granularity**: Don't record too many metrics (which adds overhead) or too few (which reduces visibility).
3. **Use time windows for analysis**: Focus on recent metrics to identify current issues.
4. **Monitor percentiles, not just averages**: High percentiles (p95, p99) often reveal issues that averages hide.
5. **Track custom metrics for domain-specific insights**: Add custom metrics for payload sizes, queue lengths, etc.
6. **Regularly analyze trends**: Look for changes in performance over time.

## Troubleshooting

### High Latency

If you observe high latency:

1. Look at the 90th, 95th, and 99th percentiles to understand if it's affecting all requests or just a subset.
2. Check if the issue is specific to certain operations.
3. Analyze whether the latency correlates with payload size (using custom metrics).
4. Check if the circuit breaker is opening frequently, indicating underlying issues.

### High Error Rates

If you observe many errors:

1. Look at the error types to identify patterns.
2. Check if errors correlate with specific operations or request types.
3. Analyze if error rates increase under higher load.

## Advanced Usage

### Custom Performance Metrics Instance

You can create a custom metrics instance for specific uses:

```python
from subsystems.CORUJA.adapters.performance_metrics import PerformanceMetrics

# Create a custom metrics instance
custom_metrics = PerformanceMetrics(
    max_samples=500,  # Store up to 500 samples per metric
    history_window=1800  # Keep data for the last 30 minutes
)

# Use the custom instance
custom_metrics.record_latency("my_operation", 100.0)
```

### Integrating with Other Components

To integrate the metrics system with other components:

```python
class MyComponent:
    def __init__(self, metrics=None):
        from subsystems.CORUJA.adapters import get_performance_metrics
        self.metrics = metrics or get_performance_metrics()
        
    def some_operation(self):
        start_time = time.time()
        try:
            # Operation code...
            result = self._process()
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency("my_component.some_operation", latency_ms)
            self.metrics.record_request("my_component.some_operation")
            
            return result
        except Exception as e:
            # Record error
            self.metrics.record_error("my_component.some_operation", type(e).__name__)
            raise
```

## Future Enhancements

Planned enhancements to the metrics system include:

1. Integration with Prometheus, Grafana, and DataDog
2. Automatic alerting based on threshold breaches
3. Enhanced historical data storage
4. Machine learning-based anomaly detection
5. Correlation analysis between different metrics

## References

- [CORUJA Performance Metrics Implementation](../../..\subsystems\CORUJA\adapters\performance_metrics.py)
- [CORUJA-MYCELIUM Adapter](../../..\subsystems\CORUJA\adapters\mycelium_adapter.py)
- [Performance Analysis Example](../../..\subsystems\CORUJA\examples\performance_analysis_example.py)
- [Performance Metrics Tests](../../..\subsystems\CORUJA\tests\adapters\test_performance_metrics.py)
- [CORUJA-MYCELIUM Enhancement Plan](../../..\docs\CORUJA_MYCELIUM_ENHANCEMENT_PLAN.md)

✧༺❀༻∞ EGOS ∞༺❀༻✧ 