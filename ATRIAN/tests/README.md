@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - ATRIAN/tests/README.md

# ATRiAN Test Fixtures

This directory contains test data fixtures used by the ATRiAN EaaS API test suite. These files provide standardized input and expected output for various test scenarios.

## File Descriptions

### Evaluation Fixtures
- `test_evaluation.json` - Basic evaluation test data
- `test_evaluation_correct.json` - Corrected evaluation test data with expected results
- `test_evaluation_fixed.json` - Fixed version of evaluation test data after bug fixes

### Framework Fixtures
- `test_framework.json` - Test data for ethics framework validation

### Explanation Fixtures
- `test_explain.json` - Test data for the explain endpoint

### Suggestion Fixtures
- `test_suggest.json` - Test data for the suggest endpoint

## Usage

These fixtures should be loaded in test files using relative paths:

```python
import json
import os

def load_fixture(filename):
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(fixture_path, 'r') as f:
        return json.load(f)

# Example usage
test_data = load_fixture('test_evaluation.json')
```

## Maintenance

When updating these fixtures:
1. Document the purpose of any new fixtures
2. Maintain backward compatibility when possible
3. Update this README with descriptions of new fixtures

## Related Files

- `../test_eaas_api.py` - Main API test suite that uses these fixtures
- `../../tools/audit_performance_monitor.py` - Performance monitoring tool