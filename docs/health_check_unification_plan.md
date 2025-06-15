# EGOS Health Check Systems Unification Plan

**Date:** 2025-05-26
**Author:** Cascade (AI Assistant)
**Status:** Proposed
**MQP Principles:** Systemic Cartography (SC), Conscious Modularity (CM), Evolutionary Preservation (EP)

## 1. Executive Summary

This document outlines a comprehensive plan for unifying the various health check, validation, and monitoring systems within the EGOS project. The goal is to establish a single source of truth for system health validation, eliminate redundancy, and create a modular, extensible framework that can be easily maintained and enhanced.

## 2. Current State Analysis

Our comprehensive analysis has identified multiple overlapping health check and validation systems across the EGOS codebase:

### 2.1. System Monitoring Tools
- **EGOS System Monitor** (`scripts/system_monitor/egos_system_monitor.py`) - Comprehensive but marked INACTIVE
- **Website Documentation** (`website/content/tools/egos_system_monitor.md`) - Incomplete

### 2.2. Validation Framework Components
- **Directory Structure Validator** (`scripts/validation/directory_structure_validator.py`) - Active
- **Script Standards Scanner** (`scripts/validation/script_standards_scanner.py`) - Placeholder (v0.1.0)
- **Cross Reference Validator** (`scripts/validation/cross_reference_validator.py`)
- **Tool Registry Validator** (`scripts/validation/tool_registry_validator.py`)

### 2.3. Maintenance Tools
- **File Duplication Auditor** (`scripts/maintenance/file_duplication_auditor.py`) - Active (v2.0.0)
- **Scheduled Cleanup** (`scripts/maintenance/scheduled_cleanup.py`)
- **GitHub Sync Manager** (`scripts/maintenance/github_sync_manager.py`)
- **Code Health Analyzers** (in `scripts/maintenance/code_health/`)

### 2.4. Naming Convention Tools
- **Audit Tool** (`scripts/utils/audit_snake_case.py`) - Active
- **Conversion Tool** (`scripts/utils/convert_to_snake_case.py`) - Active
- **Targeted Audit** (`scripts/utils/targeted_snake_case_audit.py`) - Active
- **Targeted Conversion** (`scripts/utils/targeted_snake_case_conversion.py`) - Active

### 2.5. Key Issues Identified
1. **Fragmentation:** Health check functionality is spread across multiple directories
2. **Duplication:** Similar functionality implemented in different tools
3. **Inconsistent Status:** Some tools marked inactive despite being the most comprehensive
4. **Documentation Gaps:** Incomplete or missing documentation for several tools
5. **Integration Challenges:** Tools operate independently without a unified framework

## 3. Unification Strategy

### 3.1. Single Source of Truth
Establish a unified directory structure for all health check and validation tools:

```
C:\EGOS\scripts\system_health\
├── core\               # Core framework components
│   ├── base_validator.py
│   ├── report_generator.py
│   ├── fix_suggester.py
│   └── orchestrator.py
├── validators\         # Individual validator modules
│   ├── directory_structure_validator.py
│   ├── naming_convention_validator.py
│   ├── script_standards_validator.py
│   ├── cross_reference_validator.py
│   ├── duplication_validator.py
│   └── documentation_validator.py
├── maintenance\        # Maintenance and cleanup tools
│   ├── scheduled_cleanup.py
│   └── github_sync.py
├── utils\              # Utility functions and helpers
│   ├── file_utils.py
│   └── logging_utils.py
├── tests\              # Comprehensive test suite
├── config\             # Configuration files
└── egos_health_check.py  # Main entry point
```

### 3.2. Phased Implementation Approach

#### Phase 1: Preparation and Analysis (2 weeks)
1. **Detailed Code Review:** Analyze all existing tools in depth
2. **Functionality Mapping:** Create a comprehensive map of all features
3. **Dependency Analysis:** Identify dependencies between components
4. **Technical Debt Assessment:** Evaluate code quality and maintainability
5. **Documentation Audit:** Review existing documentation

#### Phase 2: Core Framework Development (3 weeks)
1. **Create Base Architecture:** Develop the core framework components
2. **Define Interfaces:** Establish clear interfaces for validator modules
3. **Implement Orchestrator:** Develop the central orchestration system
4. **Build Reporting System:** Create unified reporting capabilities
5. **Develop Fix Suggester:** Implement the suggestion engine

#### Phase 3: Validator Migration (4 weeks)
1. **Directory Structure Validator:** Migrate and enhance
2. **Naming Convention Validator:** Integrate `snake_case` validation
3. **Script Standards Validator:** Enhance and migrate
4. **Cross Reference Validator:** Migrate and improve
5. **Duplication Validator:** Integrate file duplication auditor
6. **Documentation Validator:** Migrate from system monitor

#### Phase 4: Integration and Testing (2 weeks)
1. **End-to-End Testing:** Validate the entire system
2. **Performance Optimization:** Ensure efficient operation
3. **Documentation:** Create comprehensive documentation
4. **CI/CD Integration:** Add to continuous integration pipeline

#### Phase 5: Deployment and Cleanup (1 week)
1. **Gradual Rollout:** Deploy to production
2. **Legacy System Deprecation:** Mark old systems as deprecated
3. **Archive Obsolete Code:** Move obsolete code to archive
4. **Final Cleanup:** Remove redundant components

### 3.3. Detailed Implementation Timeline

| Week | Phase | Tasks | Deliverables | MQP Principles |
|------|-------|-------|--------------|----------------|
| 1 | Preparation | • Detailed code review of existing tools<br>• Create functionality map<br>• Begin dependency analysis | • Comprehensive analysis report<br>• Feature matrix document | SC, EP |
| 2 | Preparation | • Complete dependency analysis<br>• Technical debt assessment<br>• Documentation audit<br>• Create directory structure | • Dependency graph<br>• Technical debt report<br>• Initial directory structure | SC, CM |
| 3 | Core Framework | • Develop `base_validator.py`<br>• Define validator interfaces<br>• Create test framework | • Base validator class<br>• Interface definitions<br>• Initial test suite | CM, EP |
| 4 | Core Framework | • Develop `orchestrator.py`<br>• Implement validator discovery<br>• Create configuration system | • Orchestrator class<br>• Configuration schema<br>• Validator registration system | CM, SC |
| 5 | Core Framework | • Develop reporting system<br>• Implement fix suggester<br>• Create CLI interface | • Report generator<br>• Fix suggestion engine<br>• Command-line interface | UA, RT |
| 6 | Validator Migration | • Migrate directory structure validator<br>• Enhance with additional checks | • Functional directory validator<br>• Test cases | CM, SC |
| 7 | Validator Migration | • Integrate `snake_case` validation<br>• Develop naming convention validator | • Naming convention validator<br>• Integration with existing tools | CM, SC |
| 8 | Validator Migration | • Migrate script standards validator<br>• Enhance with additional checks | • Script standards validator<br>• Documentation | CM, EP |
| 9 | Validator Migration | • Migrate cross-reference validator<br>• Integrate with fix suggester | • Cross-reference validator<br>• Automated fix capabilities | CM, SC |
| 10 | Integration | • End-to-end testing<br>• Performance optimization<br>• Bug fixes | • Test results<br>• Performance metrics<br>• Fixed issues | EP, RT |
| 11 | Integration | • Documentation<br>• CI/CD integration<br>• User guide creation | • Comprehensive documentation<br>• CI/CD pipeline<br>• User guide | UA, RT |
| 12 | Deployment | • Gradual rollout<br>• Legacy system deprecation<br>• Final cleanup | • Production deployment<br>• Archived obsolete code<br>• Clean codebase | EP, SC |

### 3.4. Milestone Definitions

#### Milestone 1: Framework Foundation (End of Week 5)
- Complete core framework components
- Functional orchestrator with validator registration
- Basic reporting system
- Command-line interface prototype

#### Milestone 2: First Validator Set (End of Week 9)
- Four functional validators:
  - Directory structure validator
  - Naming convention validator
  - Script standards validator
  - Cross-reference validator
- Integration with fix suggester
- Initial documentation

#### Milestone 3: Complete System (End of Week 12)
- All validators integrated and tested
- Comprehensive documentation
- CI/CD integration
- Legacy systems deprecated
- Clean, unified codebase

## 4. File Disposition Plan

### 4.1. Files to Migrate (Enhance and Move)
| Current Path | New Path | Action |
|--------------|----------|--------|
| `scripts/validation/directory_structure_validator.py` | `scripts/system_health/validators/directory_structure_validator.py` | Migrate & Enhance |
| `scripts/utils/audit_snake_case.py` | `scripts/system_health/validators/naming_convention_validator.py` | Integrate & Enhance |
| `scripts/validation/script_standards_scanner.py` | `scripts/system_health/validators/script_standards_validator.py` | Complete & Migrate |
| `scripts/validation/cross_reference_validator.py` | `scripts/system_health/validators/cross_reference_validator.py` | Migrate & Enhance |
| `scripts/maintenance/file_duplication_auditor.py` | `scripts/system_health/validators/duplication_validator.py` | Migrate & Refactor |

### 4.2. Files to Archive (Outdated or Superseded)
| Current Path | Reason | Archive Location |
|--------------|--------|------------------|
| `scripts/system_monitor/egos_system_monitor.py` | Superseded by new framework | `scripts/archive/system_monitor/` |
| `website/content/tools/egos_system_monitor.md` | Outdated documentation | `website/archive/tools/` |

### 4.3. Files to Delete (Redundant or Obsolete)
| Current Path | Reason |
|--------------|--------|
| Various temporary or backup files | Redundant |
| Deprecated test files | Obsolete |

## 5. Implementation Details

### 5.1. Core Framework Components

#### 5.1.1. Base Validator
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Health Check Base Validator

This module provides the abstract base class for all health check validators in the
EGOS system. It defines the standard interface that all validators must implement
and provides common utility functions.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/health_check_unification_plan.md
"""

import os
import logging
import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

class IssueSeverity(Enum):
    """Severity levels for health check issues."""
    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3

class Issue:
    """Represents a health check issue."""
    
    def __init__(self, path: str, message: str, severity: IssueSeverity, fix_suggestion: Optional[str] = None):
        """Initialize an issue.
        
        Args:
            path: Path to the file or directory with the issue
            message: Description of the issue
            severity: Severity level of the issue
            fix_suggestion: Optional suggestion for fixing the issue
        """
        self.path = path
        self.message = message
        self.severity = severity
        self.fix_suggestion = fix_suggestion
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary for serialization."""
        return {
            'path': self.path,
            'message': self.message,
            'severity': self.severity.name,
            'fix_suggestion': self.fix_suggestion,
            'timestamp': self.timestamp.isoformat()
        }

class ValidationResult:
    """Results of a validation run."""
    
    def __init__(self, validator_name: str):
        """Initialize validation results.
        
        Args:
            validator_name: Name of the validator that produced these results
        """
        self.validator_name = validator_name
        self.issues: List[Issue] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.items_checked = 0
        self.metadata: Dict[str, Any] = {}
    
    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the results.
        
        Args:
            issue: The issue to add
        """
        self.issues.append(issue)
    
    def complete(self) -> None:
        """Mark the validation as complete."""
        self.end_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the results to a dictionary for serialization."""
        return {
            'validator_name': self.validator_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'items_checked': self.items_checked,
            'issues': [issue.to_dict() for issue in self.issues],
            'metadata': self.metadata
        }

class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the validator.
        
        Args:
            name: Name of the validator
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"health_check.{name}")
    
    @abstractmethod
    def validate(self, target_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Run validation and return results.
        
        Args:
            target_path: Path to validate
            config: Optional configuration to override defaults
            
        Returns:
            ValidationResult containing any issues found
        """
        pass
    
    @abstractmethod
    def fix(self, issues: List[Issue], dry_run: bool = True) -> Dict[str, Any]:
        """Fix identified issues.
        
        Args:
            issues: List of issues to fix
            dry_run: If True, only simulate fixes
            
        Returns:
            Dictionary with results of fix operations
        """
        pass
    
    def generate_report(self, results: ValidationResult) -> str:
        """Generate a markdown report of validation results.
        
        Args:
            results: Validation results to report on
            
        Returns:
            Markdown formatted report
        """
        report = [f"# {self.name} Validation Report\n"]
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Items Checked:** {results.items_checked}\n")
        
        # Summary by severity
        severity_counts = {severity: 0 for severity in IssueSeverity}
        for issue in results.issues:
            severity_counts[issue.severity] += 1
        
        report.append("## Summary\n")
        report.append("| Severity | Count |\n|----------|-------|")
        for severity, count in severity_counts.items():
            report.append(f"| {severity.name} | {count} |")
        report.append("\n")
        
        # Issues by severity
        for severity in IssueSeverity:
            issues = [issue for issue in results.issues if issue.severity == severity]
            if issues:
                report.append(f"## {severity.name} Issues ({len(issues)})\n")
                for i, issue in enumerate(issues, 1):
                    report.append(f"### Issue {i}: {issue.path}\n")
                    report.append(f"**Message:** {issue.message}\n")
                    if issue.fix_suggestion:
                        report.append(f"**Suggestion:** {issue.fix_suggestion}\n")
        
        return "\n".join(report)
    
    def load_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return {}
    
    def save_report(self, results: ValidationResult, output_path: Union[str, Path]) -> str:
        """Save the validation report to a file.
        
        Args:
            results: Validation results to report on
            output_path: Path to save the report to
            
        Returns:
            Path to the saved report
        """
        report = self.generate_report(results)
        try:
            with open(output_path, 'w') as f:
                f.write(report)
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            return ""
```

#### 5.1.2. Orchestrator
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Health Check Orchestrator

This module provides the central orchestration system for running health checks
across the EGOS project. It manages validator registration, execution, reporting,
and fix suggestion.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\MQP.md (Conscious Modularity, Systemic Cartography)
"""

import os
import sys
import logging
import json
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Type
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import base validator classes
from .base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity

class HealthCheckOrchestrator:
    """Central orchestrator for running health checks."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize with optional configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.validators: Dict[str, BaseValidator] = {}
        self.logger = logging.getLogger("health_check.orchestrator")
        
        # Load configuration
        self.config = {}
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
    
    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator with the orchestrator.
        
        Args:
            validator: Validator instance to register
        """
        self.validators[validator.name] = validator
        self.logger.info(f"Registered validator: {validator.name}")
    
    def discover_validators(self, validators_dir: Union[str, Path]) -> None:
        """Discover and register validators from a directory.
        
        Args:
            validators_dir: Directory containing validator modules
        """
        validators_path = Path(validators_dir)
        if not validators_path.exists() or not validators_path.is_dir():
            self.logger.error(f"Validators directory not found: {validators_dir}")
            return
        
        # Add validators directory to path
        sys.path.append(str(validators_path.parent))
        
        # Import validator modules
        for file_path in validators_path.glob("*_validator.py"):
            module_name = file_path.stem
            try:
                # Import the module
                module = importlib.import_module(f"validators.{module_name}")
                
                # Find validator classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseValidator) and attr != BaseValidator:
                        # Instantiate and register the validator
                        validator = attr()
                        self.register_validator(validator)
            except Exception as e:
                self.logger.error(f"Error importing validator {module_name}: {e}")
    
    def run_validators(self, target_path: Union[str, Path], validators: Optional[List[str]] = None) -> Dict[str, ValidationResult]:
        """Run specified or all registered validators.
        
        Args:
            target_path: Path to validate
            validators: Optional list of validator names to run
            
        Returns:
            Dictionary mapping validator names to validation results
        """
        results: Dict[str, ValidationResult] = {}
        target_path = Path(target_path)
        
        # Determine which validators to run
        validators_to_run = {}
        if validators:
            for name in validators:
                if name in self.validators:
                    validators_to_run[name] = self.validators[name]
                else:
                    self.logger.warning(f"Validator not found: {name}")
        else:
            validators_to_run = self.validators
        
        # Run validators in parallel
        with ThreadPoolExecutor() as executor:
            future_to_validator = {}
            for name, validator in validators_to_run.items():
                future = executor.submit(validator.validate, target_path)
                future_to_validator[future] = name
            
            for future in as_completed(future_to_validator):
                name = future_to_validator[future]
                try:
                    result = future.result()
                    results[name] = result
                except Exception as e:
                    self.logger.error(f"Error running validator {name}: {e}")
        
        return results
    
    def generate_report(self, results: Dict[str, ValidationResult], output_path: Optional[Union[str, Path]] = None) -> str:
        """Generate a comprehensive report.
        
        Args:
            results: Dictionary mapping validator names to validation results
            output_path: Optional path to save the report
            
        Returns:
            Markdown formatted report
        """
        report = ["# EGOS Health Check Report\n"]
        report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        total_issues = sum(len(result.issues) for result in results.values())
        total_items = sum(result.items_checked for result in results.values())
        
        report.append("## Summary\n")
        report.append(f"**Total Items Checked:** {total_items}\n")
        report.append(f"**Total Issues Found:** {total_issues}\n\n")
        
        # Issues by severity
        severity_counts = {severity: 0 for severity in IssueSeverity}
        for result in results.values():
            for issue in result.issues:
                severity_counts[issue.severity] += 1
        
        report.append("### Issues by Severity\n")
        report.append("| Severity | Count |\n|----------|-------|")
        for severity, count in severity_counts.items():
            report.append(f"| {severity.name} | {count} |")
        report.append("\n")
        
        # Issues by validator
        report.append("### Issues by Validator\n")
        report.append("| Validator | Items Checked | Issues Found |\n|-----------|---------------|--------------|")
        for name, result in results.items():
            report.append(f"| {name} | {result.items_checked} | {len(result.issues)} |")
        report.append("\n")
        
        # Detailed results by validator
        for name, result in results.items():
            report.append(f"## {name}\n")
            if result.issues:
                for severity in IssueSeverity:
                    issues = [issue for issue in result.issues if issue.severity == severity]
                    if issues:
                        report.append(f"### {severity.name} Issues ({len(issues)})\n")
                        for i, issue in enumerate(issues, 1):
                            report.append(f"#### Issue {i}: {issue.path}\n")
                            report.append(f"**Message:** {issue.message}\n")
                            if issue.fix_suggestion:
                                report.append(f"**Suggestion:** {issue.fix_suggestion}\n")
            else:
                report.append("No issues found.\n")
        
        # Save report if output path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    f.write("\n".join(report))
            except Exception as e:
                self.logger.error(f"Error saving report: {e}")
        
        return "\n".join(report)
    
    def suggest_fixes(self, results: Dict[str, ValidationResult], dry_run: bool = True) -> Dict[str, Any]:
        """Suggest fixes for identified issues.
        
        Args:
            results: Dictionary mapping validator names to validation results
            dry_run: If True, only simulate fixes
            
        Returns:
            Dictionary with results of fix operations
        """
        fix_results = {}
        
        for name, result in results.items():
            if name in self.validators and result.issues:
                try:
                    validator = self.validators[name]
                    fix_result = validator.fix(result.issues, dry_run)
                    fix_results[name] = fix_result
                except Exception as e:
                    self.logger.error(f"Error suggesting fixes for {name}: {e}")
                    fix_results[name] = {"error": str(e)}
        
        return fix_results
```

### 5.2. Naming Convention Validator Integration

The `naming_convention_validator.py` will integrate our existing `snake_case` validation tools:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Naming Convention Validator

This module provides a validator for checking naming conventions across the EGOS project,
with a focus on snake_case compliance. It integrates the existing snake_case audit and
conversion tools into the unified health check framework.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
- C:\EGOS\scripts\utils\audit_snake_case.py
- C:\EGOS\scripts\utils\convert_to_snake_case.py
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Import base validator classes
from ..core.base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity

# Import existing snake_case utilities
# Note: In the actual implementation, we would properly import these modules
# For now, we'll simulate the imports
class SnakeCaseAuditor:
    """Placeholder for the actual snake_case auditor."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def is_snake_case(self, name):
        """Check if a name follows snake_case convention."""
        # Remove file extension if present
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Check if name is already snake_case (all lowercase with underscores)
        snake_case_pattern = r'^[a-z0-9_]+

## 6. Success Metrics

The success of this unification plan will be measured by:

1. **Reduction in Code Duplication:** Measure the reduction in duplicate functionality
2. **Improved Test Coverage:** Achieve >90% test coverage for the new framework
3. **Performance Improvements:** Faster execution time for health checks
4. **User Adoption:** Increased usage of health check tools
5. **Issue Detection:** More comprehensive detection of system health issues
6. **Documentation Quality:** Complete and accurate documentation

## 7. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing functionality | High | Medium | Comprehensive testing before migration |
| Resistance to change | Medium | Medium | Clear communication and documentation |
| Incomplete feature migration | High | Low | Detailed feature mapping and validation |
| Performance regression | Medium | Low | Performance benchmarking throughout |
| Integration challenges | Medium | Medium | Modular design with clear interfaces |

## 8. References

- [MQP.md](C:\EGOS\MQP.md) - Master Quantum Prompt defining EGOS principles
- [ADRS_Log.md](C:\EGOS\ADRS_Log.md) - Anomaly & Deviation Reporting System log
- [ROADMAP.md](C:\EGOS\ROADMAP.md) - EGOS project roadmap
- [snake_case_naming_convention.md](C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md) - Naming convention standard
        return bool(re.match(snake_case_pattern, name))
    
    def should_exclude(self, path, exclusions):
        """Check if a path should be excluded based on exclusion rules."""
        # Implementation would check against exclusion rules
        return False
    
    def audit_directory(self, directory_path, exclusions):
        """Audit a directory for non-snake_case files and directories."""
        # Implementation would scan the directory and return non-compliant items
        return []

class SnakeCaseConverter:
    """Placeholder for the actual snake_case converter."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def string_to_snake_case(self, name):
        """Convert a string to snake_case."""
        # Implementation would convert the string to snake_case
        return name.lower()
    
    def convert_item(self, item_path, dry_run=False):
        """Convert a single file or directory to snake_case."""
        # Implementation would convert the item and return the result
        return True, str(item_path), str(item_path), f"Converted: {item_path}"

class NamingConventionValidator(BaseValidator):
    """Validator for naming conventions including snake_case."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__("naming_convention", config)
        
        # Default configuration
        self.default_config = {
            "conventions": ["snake_case"],
            "exclusions": {
                "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
                "files": ["README.md", "LICENSE", "Makefile", "requirements.txt", ".gitignore", ".gitattributes"],
                "extensions_to_ignore": [".md", ".MD"],
                "patterns_to_ignore": [r".*\.git.*", r".*node_modules.*", r".*__pycache__.*", r".*\.vscode.*"]
            }
        }
        
        # Merge with provided config
        if config:
            self._merge_config(self.default_config, config)
        
        # Initialize auditor and converter
        self.auditor = SnakeCaseAuditor(self.config)
        self.converter = SnakeCaseConverter(self.config)
    
    def _merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to override base
            
        Returns:
            Merged configuration
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
        return base_config
    
    def validate(self, target_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate naming conventions in the target path.
        
        Args:
            target_path: Path to validate
            config: Optional configuration to override defaults
            
        Returns:
            ValidationResult containing any issues found
        """
        # Initialize results
        results = ValidationResult(self.name)
        target_path = Path(target_path)
        
        # Merge configuration if provided
        effective_config = self.config.copy()
        if config:
            self._merge_config(effective_config, config)
        
        # Get exclusions
        exclusions = effective_config.get("exclusions", {})
        
        # Audit the directory
        self.logger.info(f"Auditing directory: {target_path}")
        non_compliant = self.auditor.audit_directory(target_path, exclusions)
        
        # Add issues for non-compliant items
        for path in non_compliant:
            path_obj = Path(path)
            name = path_obj.name
            
            # Determine severity based on item type and location
            severity = IssueSeverity.WARNING
            if path_obj.is_dir():
                # Directories are more important to fix
                severity = IssueSeverity.ERROR
            
            # Generate fix suggestion
            snake_case_name = self.converter.string_to_snake_case(name)
            new_path = path_obj.parent / snake_case_name
            fix_suggestion = f"Rename to: {new_path}"
            
            # Add the issue
            issue = Issue(
                path=str(path),
                message=f"Name '{name}' does not follow snake_case convention",
                severity=severity,
                fix_suggestion=fix_suggestion
            )
            results.add_issue(issue)
        
        # Update metadata
        results.items_checked = len(non_compliant)
        results.metadata["non_compliant_count"] = len(non_compliant)
        
        # Mark as complete
        results.complete()
        
        return results
    
    def fix(self, issues: List[Issue], dry_run: bool = True) -> Dict[str, Any]:
        """Fix naming convention issues.
        
        Args:
            issues: List of issues to fix
            dry_run: If True, only simulate fixes
            
        Returns:
            Dictionary with results of fix operations
        """
        fix_results = {
            "total": len(issues),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for issue in issues:
            try:
                path = issue.path
                
                # Convert the item
                success, old_path, new_path, message = self.converter.convert_item(path, dry_run)
                
                # Record the result
                result = {
                    "path": path,
                    "success": success,
                    "message": message
                }
                
                if success:
                    fix_results["successful"] += 1
                else:
                    fix_results["failed"] += 1
                
                fix_results["details"].append(result)
            
            except Exception as e:
                self.logger.error(f"Error fixing issue {issue.path}: {e}")
                fix_results["failed"] += 1
                fix_results["details"].append({
                    "path": issue.path,
                    "success": False,
                    "message": f"Error: {str(e)}"
                })
        
        return fix_results
```

## 6. Success Metrics

The success of this unification plan will be measured by:

1. **Reduction in Code Duplication:** Measure the reduction in duplicate functionality
2. **Improved Test Coverage:** Achieve >90% test coverage for the new framework
3. **Performance Improvements:** Faster execution time for health checks
4. **User Adoption:** Increased usage of health check tools
5. **Issue Detection:** More comprehensive detection of system health issues
6. **Documentation Quality:** Complete and accurate documentation

## 7. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing functionality | High | Medium | Comprehensive testing before migration |
| Resistance to change | Medium | Medium | Clear communication and documentation |
| Incomplete feature migration | High | Low | Detailed feature mapping and validation |
| Performance regression | Medium | Low | Performance benchmarking throughout |
| Integration challenges | Medium | Medium | Modular design with clear interfaces |

## 8. References

- [MQP.md](C:\EGOS\MQP.md) - Master Quantum Prompt defining EGOS principles
- [ADRS_Log.md](C:\EGOS\ADRS_Log.md) - Anomaly & Deviation Reporting System log
- [ROADMAP.md](C:\EGOS\ROADMAP.md) - EGOS project roadmap
- [snake_case_naming_convention.md](C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md) - Naming convention standard