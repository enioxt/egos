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
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import sys
import logging
import json
import importlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Type
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import base validator classes
try:
    from .base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity, print_banner
except ImportError:
    # Handle case when running as standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity, print_banner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_check.orchestrator")

class HealthCheckOrchestrator:
    """Central orchestrator for running health checks."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize with optional configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.validators: Dict[str, BaseValidator] = {}
        
        # Load configuration
        self.config = {}
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
    
    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator with the orchestrator.
        
        Args:
            validator: Validator instance to register
        """
        self.validators[validator.name] = validator
        logger.info(f"Registered validator: {validator.name}")
    
    def discover_validators(self, validators_dir: Union[str, Path]) -> None:
        """Discover and register validators from a directory.
        
        Args:
            validators_dir: Directory containing validator modules
        """
        validators_path = Path(validators_dir)
        if not validators_path.exists() or not validators_path.is_dir():
            logger.error(f"Validators directory not found: {validators_dir}")
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
                        logger.info(f"Discovered and registered validator: {validator.name}")
            except Exception as e:
                logger.error(f"Error importing validator {module_name}: {e}")
    
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
                    logger.warning(f"Validator not found: {name}")
        else:
            validators_to_run = self.validators
        
        if not validators_to_run:
            logger.warning("No validators to run")
            return results
        
        logger.info(f"Running {len(validators_to_run)} validators on {target_path}")
        
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
                    logger.info(f"Validator {name} completed with {len(result.issues)} issues")
                except Exception as e:
                    logger.error(f"Error running validator {name}: {e}")
        
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
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("\n".join(report))
                logger.info(f"Report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving report: {e}")
        
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
                    logger.info(f"Generated fix suggestions for {name}: {len(result.issues)} issues")
                except Exception as e:
                    logger.error(f"Error suggesting fixes for {name}: {e}")
                    fix_results[name] = {"error": str(e)}
        
        return fix_results

def main():
    """Main function for running the health check orchestrator from the command line."""
    parser = argparse.ArgumentParser(description="EGOS Health Check Orchestrator")
    parser.add_argument("target_path", help="Path to validate")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--validators", nargs="+", help="Validators to run (default: all)")
    parser.add_argument("--output", help="Path to save the report")
    parser.add_argument("--fix", action="store_true", help="Suggest fixes for issues")
    parser.add_argument("--dry-run", action="store_true", help="Only simulate fixes")
    parser.add_argument("--discover", help="Path to discover validators from")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Create orchestrator
    orchestrator = HealthCheckOrchestrator(args.config)
    
    # Discover validators if specified
    if args.discover:
        orchestrator.discover_validators(args.discover)
    
    # Run validators
    results = orchestrator.run_validators(args.target_path, args.validators)
    
    # Generate report
    report = orchestrator.generate_report(results, args.output)
    
    # Suggest fixes if requested
    if args.fix:
        fix_results = orchestrator.suggest_fixes(results, args.dry_run)
        print("\nFix Suggestions:")
        for name, result in fix_results.items():
            print(f"\n{name}:")
            if "error" in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Total: {result.get('total', 0)}")
                print(f"  Successful: {result.get('successful', 0)}")
                print(f"  Failed: {result.get('failed', 0)}")
    
    # Print summary
    total_issues = sum(len(result.issues) for result in results.values())
    print(f"\nTotal issues found: {total_issues}")
    
    # Return exit code based on issues found
    return 1 if total_issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main())