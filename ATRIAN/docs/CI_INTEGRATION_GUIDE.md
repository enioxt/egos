# AutoCrossRef CI Integration Guide

@references:
- ROADMAP.md
- docs/AutoCrossRef_Refactor_Documentation.md
- CROSSREF_STANDARD.md

@references(level=1):
  - ATRIAN/.windsurf/workflows/tdd_based_dev_workflow.md
  - ATRIAN/docs/AutoCrossRef_Refactor_Documentation.md








## Overview

This guide outlines the process for integrating the AutoCrossRef hierarchical reference system into Continuous Integration (CI) pipelines. The integration ensures that all files in the EGOS project maintain proper cross-references according to the standardized reference hierarchy defined in `CROSSREF_STANDARD.md`.

## Prerequisites

Before setting up CI integration, ensure the following components are in place:

1. **AutoCrossRef System**: The refactored AutoCrossRef system with hierarchical reference support
2. **CROSSREF_STANDARD.md**: Properly formatted YAML header defining core references
3. **Unit Tests**: All unit tests for `ref_injector.py` and `regen_references.py` passing
4. **CI Pipeline**: Access to your project's CI pipeline configuration (GitHub Actions, Jenkins, etc.)

## Integration Steps

### 1. Create CI Configuration File

#### For GitHub Actions

Create a file at `.github/workflows/autocrossref-validation.yml`:

```yaml
name: AutoCrossRef Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  validate-references:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml
          
      - name: Run reference validation
        run: |
          python scripts/regen_references.py --mode diagnose --report-html
          
      - name: Check for non-compliant files
        run: |
          python scripts/regen_references.py --mode full --strict
          
      - name: Upload HTML report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: autocrossref-report
          path: autocrossref-report.html
```

#### For Jenkins

Create a `Jenkinsfile` or add to an existing one:

```groovy
pipeline {
    agent any
    
    stages {
        stage('AutoCrossRef Validation') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'pip install pyyaml'
                sh 'python scripts/regen_references.py --mode diagnose --report-html'
                sh 'python scripts/regen_references.py --mode full --strict'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'autocrossref-report.html', allowEmptyArchive: true
                }
            }
        }
    }
}
```

### 2. Configure Pre-commit Hook (Optional)

For local validation before commits, create a pre-commit hook:

1. Create a file at `.git/hooks/pre-commit` (or in your project's hook template directory):

```bash
#!/bin/bash

# Run AutoCrossRef validation
python scripts/regen_references.py --mode diagnose

# Check if there are non-compliant files
python scripts/regen_references.py --mode full --strict --quiet
if [ $? -ne 0 ]; then
    echo "❌ AutoCrossRef validation failed. Some files are non-compliant."
    echo "Run 'python scripts/regen_references.py --mode fix-core' to fix core references."
    exit 1
fi

echo "✅ AutoCrossRef validation passed."
```

2. Make the hook executable:

```bash
chmod +x .git/hooks/pre-commit
```

### 3. CI Pipeline Configuration Options

The `regen_references.py` script supports several command-line options for CI integration:

| Option | Description |
|--------|-------------|
| `--mode diagnose` | Dry-run mode that reports issues without modifying files |
| `--mode fix-core` | Adds missing core references but doesn't enforce strict compliance |
| `--mode full` | Strict mode that enforces complete compliance with the reference standard |
| `--strict` | Exit with non-zero status if any files are non-compliant |
| `--report-html` | Generate an HTML report of the validation results |
| `--quiet` | Suppress detailed output, showing only summary information |

### 4. Integration Testing

Before deploying to production, run integration tests on a fixture repository:

```bash
# Clone a test repository
git clone https://github.com/your-org/test-repo.git
cd test-repo

# Copy the AutoCrossRef system
cp -r /path/to/egos/subsystems/AutoCrossRef .
cp /path/to/egos/scripts/regen_references.py scripts/

# Run in diagnose mode first
python scripts/regen_references.py --mode diagnose --report-html

# Run in fix-core mode to add missing references
python scripts/regen_references.py --mode fix-core

# Run in full mode to check compliance
python scripts/regen_references.py --mode full --strict
```

### 5. Monitoring and Reporting

For ongoing monitoring:

1. Configure your CI system to store HTML reports as artifacts
2. Set up notifications for failed reference validation
3. Track compliance metrics over time to identify trends

## Best Practices

1. **Gradual Implementation**: Start with `diagnose` mode to assess the current state before enforcing strict compliance
2. **Documentation**: Keep `CROSSREF_STANDARD.md` updated with clear documentation on reference hierarchy
3. **Team Training**: Ensure all team members understand the reference standard and how to maintain compliance
4. **Regular Audits**: Periodically review the reference system and update as needed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| False positives | Check for special cases in file parsing logic |
| Performance issues | Consider using `--include` and `--exclude` options to limit scope |
| Encoding errors | Ensure all files use consistent encoding (UTF-8 recommended) |

## References

- [AutoCrossRef Refactor Documentation](AutoCrossRef_Refactor_Documentation.md)
- [CROSSREF_STANDARD.md](../subsystems/AutoCrossRef/CROSSREF_STANDARD.md)
- [TDD-based Development Workflow](../.windsurf/workflows/tdd_based_dev_workflow.md)

---

<p align="center">✧༺─༻∞ EGOS ∞༺─༻✧</p>