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
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\MQP.md (Conscious Modularity, Systemic Cartography)
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
import logging
import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# EGOS Banner
BANNER = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                       EGOS Health Check Framework                         ║
║                                                                           ║
║                 "Ensuring system integrity through validation"            ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

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

def print_banner():
    """Print the EGOS Health Check Framework banner."""
    print(BANNER)

if __name__ == "__main__":
    print_banner()
    print("This module provides the base validator class for the EGOS Health Check Framework.")
    print("It is not intended to be run directly.")