"""
ATRiAN Ethical Constitution Validator

This module provides functions for validating prompts against ethical constitutions.
It serves as the core integration point between ATRiAN's ethical governance capabilities
and PromptVault's prompt storage and management.

Version: 0.2.0
Last Modified: 2025-06-13
"""
# 
# @references:
#   - ATRIAN/templates/constitution_validator.py
# 
import os
import yaml
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timezone
import json
import time
import uuid
from enum import Enum

# Import Pydantic models for validation
from .base.ethical_constitution_schema import EthicalConstitution, EthicalRule, SeverityLevel

# Configure logging with enhanced format for better diagnostics
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ATRiAN.ConstitutionValidator')

class ValidationLogLevel(Enum):
    """Log levels for validation process"""
    MINIMAL = 0   # Only critical information
    STANDARD = 1  # Standard operational logs
    VERBOSE = 2   # Detailed logs for debugging
    DEBUG = 3     # Full debug information
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
        
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
        
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
        
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

class ConstitutionValidationResult:
    """Container for validation results against an ethical constitution
    
    Enhanced with detailed metrics, timestamps, and visualization capabilities.
    Provides comprehensive data collection for analysis and reporting.
    """
    
    def __init__(self, constitution_id: str, constitution_name: str):
        # Basic identification
        self.constitution_id = constitution_id
        self.constitution_name = constitution_name
        self.validation_id = str(uuid.uuid4())  # Unique identifier for this validation
        
        # Timestamps for performance metrics
        self.start_timestamp = datetime.now()
        self.end_timestamp = None
        self.processing_time_ms = None
        
        # Core validation results
        self.passed = True
        self.overall_score = 1.0
        self.rule_results = []
        self.critical_failures = []
        self.warnings = []
        self.recommendations = []
        self.critical_rule_triggered = False
        
        # Enhanced metrics
        self.total_rules_checked = 0
        self.rules_triggered_count = 0
        self.rules_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        
        # Input context (will be populated during validation)
        self.prompt_length = 0
        self.prompt_hash = None  # For reference without storing actual content
        
        logger.info(f"Initialized validation result for constitution '{constitution_name}' (ID: {constitution_id})")
        
        # Backward compatibility
        self.timestamp = self.start_timestamp
        
    def add_rule_result(self, rule_id: str, passed: bool, principle_ids: List[str], 
                        severity: str, details: str, recommendations: List[str] = None):
        """Add result for a specific rule validation with enhanced metrics and logging"""
        # Ensure recommendations is always a list, even if empty
        rec_list = recommendations if recommendations is not None else []
        
        # Track rule check in metrics
        # self.total_rules_checked += 1
        
        # Normalize severity for consistent tracking
        normalized_severity = severity.lower() if severity.lower() in ["critical", "high", "medium", "low"] else "unknown"
        
        # Create detailed rule result record with timestamp
        rule_result = {
            "rule_id": rule_id,
            "passed": passed,
            "principle_ids": principle_ids,
            "severity": normalized_severity,
            "details": details,
            "recommendations": rec_list,
            "timestamp": datetime.now().isoformat()
        }
        
        self.rule_results.append(rule_result)
        
        # Log the rule check result
        if passed:
            logger.debug(f"Rule {rule_id} check: PASSED")
        else:
            logger.info(f"Rule {rule_id} check: FAILED (Severity: {normalized_severity})")
            # self.rules_triggered_count += 1 # Moved to validate_prompt
            self.rules_by_severity[normalized_severity] += 1
        
        # Always add the rule's recommendations to the main list
        if rec_list:
            self.recommendations.extend(rec_list)
            logger.debug(f"Added {len(rec_list)} recommendations from rule {rule_id}")
        
        # Handle rule failure scenarios
        if not passed:
            if normalized_severity == "critical":
                self.passed = False
                self.critical_rule_triggered = True
                self.critical_failures.append(rule_id)
                
                # Add critical message as additional recommendation
                critical_message = f"CRITICAL FAILURE on rule '{rule_id}': {details}"
                self.recommendations.append(critical_message)
                logger.warning(f"Critical rule triggered: {critical_message}")
                
                # Critical rules set overall score to 0
                self.overall_score = 0.0
            else:
                # Apply score reduction based on severity
                score_impacts = {
                    "low": 0.05,
                    "medium": 0.1,
                    "high": 0.2,
                    "unknown": 0.1
                }
                impact = score_impacts.get(normalized_severity, 0.1)
                self.overall_score -= impact
                self.overall_score = max(0, self.overall_score) # Ensure score doesn't go below 0
                logger.info(f"Applied score impact of -{impact} for {normalized_severity} rule {rule_id}. New score: {self.overall_score:.2f}")
        
        return rule_result

    def finalize(self, prompt_text: str = None):
        """Finalize the validation result with performance metrics
        
        Args:
            prompt_text: Optional prompt text to calculate length and hash metrics
            
        Returns:
            self: Returns self for method chaining
        """
        self.end_timestamp = datetime.now()
        self.processing_time_ms = (self.end_timestamp - self.start_timestamp).total_seconds() * 1000
        
        if prompt_text:
            self.prompt_length = len(prompt_text)
            # Create a hash of the prompt for reference without storing content
            import hashlib
            self.prompt_hash = hashlib.md5(prompt_text.encode()).hexdigest()
        
        # Enhanced logging with more detailed metrics
        log_prefix = f"[{self.validation_id}] {self.constitution_name} ({self.constitution_id})"
        logger.info(f"{log_prefix} - Validation complete in {self.processing_time_ms:.2f}ms")
        
        if self.passed:
            logger.info(f"{log_prefix} - PASSED with score {self.overall_score:.2f}")
        else:
            logger.warning(f"{log_prefix} - FAILED with score {self.overall_score:.2f}")
            if self.critical_failures:
                logger.warning(f"{log_prefix} - Critical failures: {', '.join(self.critical_failures)}")
        
        # Log detailed metrics
        logger.info(f"{log_prefix} - Rules: {self.rules_triggered_count} triggered of {self.total_rules_checked} total")
        
        # Log severity breakdown if any rules were triggered
        if self.rules_triggered_count > 0:
            severity_details = [f"{sev}: {count}" for sev, count in self.rules_by_severity.items() if count > 0]
            if severity_details:
                logger.info(f"{log_prefix} - Severity breakdown: {', '.join(severity_details)}")
        
        # Log recommendations count if any exist
        if self.recommendations:
            logger.info(f"{log_prefix} - {len(self.recommendations)} recommendations generated")
        
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary for serialization with enhanced metrics and diagnostics"""
        logger.debug(f"[to_dict] self.recommendations: {self.recommendations}, type: {type(self.recommendations)}")
        result = {
            "validation_id": self.validation_id,
            "constitution_id": self.constitution_id,
            "constitution_name": self.constitution_name,
            "timestamp": self.timestamp.isoformat(),
            "passed": self.passed,
            "overall_score": self.overall_score,
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "rule_results": self.rule_results,
            "critical_rule_triggered": self.critical_rule_triggered,
            
            # Enhanced metrics with more detailed information
            "metrics": {
                "total_rules_checked": self.total_rules_checked,
                "rules_triggered_count": self.rules_triggered_count,
                "rules_by_severity": self.rules_by_severity,
                "prompt_length": self.prompt_length,
                "prompt_hash": self.prompt_hash,
                "processing_time_ms": self.processing_time_ms
            },
            
            # Add detailed diagnostics section
            "diagnostics": {
                "validation_version": "0.2.0",  # Match module version
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "rules_summary": {
                    "passed": len([r for r in self.rule_results if r.get("passed", True)]),
                    "failed": len([r for r in self.rule_results if not r.get("passed", True)]),
                    "by_severity": self.rules_by_severity
                }
            }
        }
        
        # Add timestamps if available
        if self.start_timestamp:
            result["start_timestamp"] = self.start_timestamp.isoformat()
        if self.end_timestamp:
            result["end_timestamp"] = self.end_timestamp.isoformat()
        
        # Add error information if available
        if hasattr(self, 'error_type'):
            result["diagnostics"]["error"] = {
                "type": getattr(self, 'error_type', 'Unknown'),
                "details": getattr(self, 'error_details', '')
            }
            
            # Include truncated traceback if available (first 20 lines)
            if hasattr(self, 'error_traceback'):
                tb_lines = getattr(self, 'error_traceback', '').splitlines()
                result["diagnostics"]["error"]["traceback_summary"] = '\n'.join(tb_lines[:20])
                if len(tb_lines) > 20:
                    result["diagnostics"]["error"]["traceback_summary"] += "\n... (truncated)"
            
        return result
        
    def generate_report(self, format: str = "text") -> str:
        """Generate a formatted report of the validation results
        
        Args:
            format: Output format ("text", "markdown", "json")
            
        Returns:
            Formatted report string
        """
        if format == "json":
            return json.dumps(self.to_dict(), indent=2)
        
        elif format == "markdown":
            md = []
            md.append(f"# Ethical Constitution Validation Report")
            md.append(f"**Constitution**: {self.constitution_name} ({self.constitution_id})")
            md.append(f"**Timestamp**: {self.timestamp.isoformat()}")
            if hasattr(self, 'processing_time_ms') and self.processing_time_ms:
                md.append(f"**Duration**: {self.processing_time_ms:.2f}ms")
            md.append(f"**Result**: {':white_check_mark: PASSED' if self.passed else ':x: FAILED'}")
            md.append(f"**Score**: {self.overall_score:.2f}/1.00")
            
            md.append(f"\n## Summary")
            md.append(f"- Rules checked: {self.total_rules_checked}")
            md.append(f"- Rules triggered: {self.rules_triggered_count}")
            md.append(f"- Critical issues: {len(self.critical_failures)}")
            md.append(f"- Recommendations: {len(self.recommendations)}")
            
            if hasattr(self, 'rules_by_severity') and self.rules_by_severity and sum(self.rules_by_severity.values()) > 0:
                md.append(f"\n## Rules by Severity")
                for severity, count in self.rules_by_severity.items():
                    if count > 0:
                        symbol = ":red_circle:" if severity == "critical" else ":large_orange_circle:" if severity == "high" else ":yellow_circle:" if severity == "medium" else ":green_circle:"
                        md.append(f"- {symbol} **{severity.title()}**: {count}")
            
            if self.recommendations:
                md.append(f"\n## Recommendations")
                for i, rec in enumerate(self.recommendations, 1):
                    md.append(f"{i}. {rec}")
            
            if self.critical_failures:
                md.append(f"\n## Critical Issues")
                for i, issue in enumerate(self.critical_failures, 1):
                    md.append(f"{i}. Rule ID: `{issue}`")
            
            return "\n".join(md)
        
        else:  # Default to text format
            lines = []
            lines.append("=" * 80)
            lines.append(f"ETHICAL CONSTITUTION VALIDATION REPORT")
            lines.append(f"Constitution: {self.constitution_name} ({self.constitution_id})")
            lines.append(f"Timestamp: {self.timestamp.isoformat()}")
            if hasattr(self, 'processing_time_ms') and self.processing_time_ms:
                lines.append(f"Duration: {self.processing_time_ms:.2f}ms")
            lines.append("-" * 80)
            lines.append(f"Result: {'PASSED' if self.passed else 'FAILED'}")
            lines.append(f"Score: {self.overall_score:.2f}/1.00")
            lines.append(f"Rules checked: {self.total_rules_checked}")
            lines.append(f"Rules triggered: {self.rules_triggered_count}")
            
            if self.recommendations:
                lines.append("\nRECOMMENDATIONS:")
                for i, rec in enumerate(self.recommendations, 1):
                    lines.append(f"{i}. {rec}")
            
            if self.critical_failures:
                lines.append("\nCRITICAL ISSUES:")
                for i, issue in enumerate(self.critical_failures, 1):
                    lines.append(f"{i}. Rule ID: {issue}")
            
            lines.append("=" * 80)
            return "\n".join(lines)

class EthicalConstitutionValidator:
    """Validates prompts against one or more ethical constitutions."""
    
    def __init__(self, constitutions_dir: Optional[Union[str, Path]] = None):
        """Initialize the validator with a directory containing constitution files."""
        self.constitutions_dir = Path(constitutions_dir) if constitutions_dir else Path.cwd() / "constitutions"
        self.loaded_constitutions = {}  # Cache for loaded constitutions
        
    def _load_constitution(self, constitution_path: Path) -> EthicalConstitution:
        """Load a constitution from a YAML file, handling inheritance."""
        abs_path_str = str(constitution_path.resolve())
        if abs_path_str in self.loaded_constitutions:
            return self.loaded_constitutions[abs_path_str]
        
        # Load the raw YAML data
        with open(constitution_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
        
        # Handle inheritance if 'extends' is present
        combined_rules = []
        combined_principles = {}
        
        # Process parent constitutions if specified
        if 'extends' in raw_data:
            parent_paths = raw_data.pop('extends')
            if not isinstance(parent_paths, list):
                parent_paths = [parent_paths]
                
            for parent_path in parent_paths:
                try:
                    base_const = self._load_constitution(Path(parent_path))
                    
                    # Merge rules, avoiding duplicates by ID
                    for r_object in base_const.rules:
                        # Check if this rule ID already exists in our combined rules
                        if not any(r.id == r_object.id for r in combined_rules):
                            combined_rules.append(r_object)
                    
                    # Merge principles, avoiding duplicates by name
                    for p_object in base_const.principles:
                        if p_object.name not in combined_principles: # combined_principles is keyed by principle name
                            combined_principles[p_object.name] = p_object.model_dump() # Pydantic v2 uses model_dump()
                except Exception as e:
                    print(f"Warning: Failed to load parent constitution {parent_path}: {str(e)}")
        
        # Add rules from the current constitution
        if 'rules' in raw_data:
            for rule_data in raw_data['rules']:
                # Check if this rule ID already exists in our combined rules
                if not any(r.id == rule_data['id'] for r in combined_rules):
                    combined_rules.append(EthicalRule(**rule_data))
        
        # Add principles from the current constitution
        if 'principles' in raw_data:
            for principle_data in raw_data['principles']:
                combined_principles[principle_data['name']] = principle_data
                
        # Update raw_data with combined rules and principles
        if combined_rules:
            raw_data['rules'] = [r.model_dump() for r in combined_rules]
        if combined_principles:
            raw_data['principles'] = list(combined_principles.values())
        
        # Validate and create EthicalConstitution object
        constitution = EthicalConstitution(**raw_data)
        self.loaded_constitutions[abs_path_str] = constitution
        return constitution

    def validate_prompt(self, prompt_text: str, constitution_id_or_path: str, log_level: ValidationLogLevel = ValidationLogLevel.STANDARD) -> ConstitutionValidationResult:
        """Validates a prompt against a single ethical constitution with enhanced logging and metrics.
        
        Args:
            prompt_text: The prompt text to validate
            constitution_id_or_path: ID or path of the constitution to validate against
            log_level: Level of logging detail (MINIMAL, STANDARD, VERBOSE, DEBUG)
            
        Returns:
            ConstitutionValidationResult: Detailed validation result with metrics
        """
        # Start performance tracking
        start_time = time.time()
        logger.info(f"Starting validation against constitution: {constitution_id_or_path}")
        
        try:
            constitution_path = self.constitutions_dir / f"{constitution_id_or_path}.yaml"
            if not constitution_path.exists(): # Try direct path if not found by ID
                constitution_path = Path(constitution_id_or_path)
                if not constitution_path.exists():
                    raise FileNotFoundError(f"Constitution file not found: {constitution_id_or_path}")
            
            logger.info(f"Loading constitution from: {constitution_path}")
            constitution = self._load_constitution(constitution_path)
            logger.info(f"Successfully loaded constitution: {constitution.name} (ID: {constitution.id})")
            
            if log_level >= ValidationLogLevel.VERBOSE:
                logger.info(f"Constitution contains {len(constitution.rules)} rules and {len(constitution.principles)} principles")
        except Exception as e:
            # Enhanced error handling with more detailed diagnostics
            error_type = type(e).__name__
            error_details = str(e)
            
            # Log detailed error information with traceback reference
            import traceback
            tb_info = traceback.format_exc()
            logger.error(f"Failed to load constitution '{constitution_id_or_path}': {error_type}: {error_details}")
            logger.debug(f"Traceback for constitution loading error:\n{tb_info}")
            
            # Create a more informative error result
            result = ConstitutionValidationResult(
                constitution_id=constitution_id_or_path,
                constitution_name=f"Error-{error_type}"
            )
            result.passed = False
            result.overall_score = 0.0
            
            # Add detailed error information to the rule result
            error_message = f"Failed to load or parse constitution '{constitution_id_or_path}': {error_type}: {error_details}"
            result.add_rule_result(
                rule_id="loading_error",
                passed=False,
                principle_ids=[],
                severity="critical",
                details=error_message,
                recommendations=[f"SYSTEM: Fix {error_type} error in constitution file or path"]
            )
            
            # Store error details in metrics for easier debugging
            result.error_type = error_type
            result.error_details = error_details
            
            return result.finalize(prompt_text)

        # Initialize validation result with enhanced metrics
        result = ConstitutionValidationResult(constitution.id, constitution.name)
        
        # Set prompt metrics
        result.prompt_length = len(prompt_text)
        if log_level.value >= ValidationLogLevel.VERBOSE.value:
            import hashlib
            result.prompt_hash = hashlib.md5(prompt_text.encode()).hexdigest()
            logger.info(f"Validating prompt (length: {result.prompt_length}, hash: {result.prompt_hash})")
        
        # Track total rules for metrics
        result.total_rules_checked = len(constitution.rules)
        
        # Process each rule
        for rule in constitution.rules:
            triggered = False
            details = f"Rule '{rule.id}' triggered."

            # Check for keyword triggers
            if rule.trigger_keywords:
                if log_level.value >= ValidationLogLevel.DEBUG.value:
                    logger.debug(f"Checking rule {rule.id} with {len(rule.trigger_keywords)} keywords")
                
                for keyword in rule.trigger_keywords:
                    if keyword.lower() in prompt_text.lower():
                        triggered = True
                        if log_level.value >= ValidationLogLevel.STANDARD.value:
                            logger.info(f"Rule {rule.id} triggered by keyword: '{keyword}'")
                        break
            
            if triggered:
                result.rules_triggered_count += 1
                is_critical = rule.severity_override == SeverityLevel.CRITICAL
                severity_value = rule.severity_override.value if rule.severity_override else "unknown"
                
                # Add detailed result with enhanced metrics
                result.add_rule_result(
                    rule_id=rule.id,
                    passed=not is_critical,
                    principle_ids=rule.principle_ids,
                    severity=severity_value,
                    details=details,
                    recommendations=rule.recommendations
                )
                
                # Update overall score based on severity
                if is_critical:
                    result.critical_rule_triggered = True
                    result.overall_score = 0.0  # Critical rules set score to 0
                    logger.warning(f"Critical rule {rule.id} triggered - validation failed")
                elif severity_value in ["high", "medium", "low"]:
                    # Apply score reduction based on severity
                    score_impacts = {
                        "low": 0.05,
                        "medium": 0.1,
                        "high": 0.2
                    }
                    impact = score_impacts.get(severity_value, 0.1)
                    result.overall_score -= impact
                    result.overall_score = max(0, result.overall_score)  # Ensure score doesn't go below 0
                    if log_level.value >= ValidationLogLevel.STANDARD.value:
                        logger.info(f"Score impact: -{impact} (severity: {severity_value}) for rule {rule.id}. New score: {result.overall_score:.2f}")
            elif log_level.value >= ValidationLogLevel.DEBUG.value:
                logger.debug(f"Rule {rule.id} not triggered")
        
        # Finalize result with performance metrics
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Validation completed in {elapsed_ms:.2f}ms. Result: {'PASSED' if result.passed else 'FAILED'} with score {result.overall_score:.2f}")
        
        # Generate summary report based on log level
        if log_level.value >= ValidationLogLevel.STANDARD.value:
            if result.recommendations:
                logger.info(f"Recommendations: {len(result.recommendations)}")
                if log_level.value >= ValidationLogLevel.VERBOSE.value:
                    for i, rec in enumerate(result.recommendations[:5], 1):
                        logger.info(f"  {i}. {rec}")
                    if len(result.recommendations) > 5:
                        logger.info(f"  ... and {len(result.recommendations) - 5} more")
        
        return result.finalize(prompt_text)

    def validate_prompts(self, prompt_text: str, constitution_ids: List[str], log_level: ValidationLogLevel = ValidationLogLevel.STANDARD) -> Dict[str, Any]:
        """Validates a prompt against multiple ethical constitutions with enhanced logging and metrics.
        
        Args:
            prompt_text: The prompt text to validate
            constitution_ids: List of constitution IDs or paths to validate against
            log_level: Level of logging detail (MINIMAL, STANDARD, VERBOSE, DEBUG)
            
        Returns:
            Dict containing aggregated validation results and individual constitution results
        """
        start_time = time.time()
        logger.info(f"Starting multi-constitution validation against {len(constitution_ids)} constitutions")
        
        # Generate a unique validation batch ID
        batch_id = str(uuid.uuid4())
        
        results = []
        for const_id in constitution_ids:
            try:
                # Use our enhanced validate_prompt method with logging
                result = self.validate_prompt(prompt_text, const_id, log_level)
                results.append(result)
            except Exception as e:
                # Enhanced error handling with more context and diagnostics
                error_type = type(e).__name__
                error_details = str(e)
                
                # Log detailed error information with traceback
                import traceback
                tb_info = traceback.format_exc()
                logger.error(f"Error validating against constitution {const_id}: {error_type}: {error_details}")
                logger.debug(f"Traceback for validation error on {const_id}:\n{tb_info}")
                
                # Create a more informative error result
                error_result = ConstitutionValidationResult(
                    constitution_id=const_id,
                    constitution_name=f"Error-{error_type}-{const_id}"
                )
                error_result.passed = False
                error_result.overall_score = 0.0
                
                # Add detailed error information to the rule result
                error_message = f"Exception during validation: {error_type}: {error_details}"
                error_result.add_rule_result(
                    rule_id="validation_error",
                    passed=False,
                    principle_ids=[],
                    severity="critical",
                    details=error_message,
                    recommendations=[f"SYSTEM: Fix {error_type} error in validation process"]
                )
                
                # Store error details in metrics for easier debugging
                error_result.error_type = error_type
                error_result.error_details = error_details
                error_result.error_traceback = tb_info
                
                results.append(error_result.finalize(prompt_text))
        
        # Calculate aggregate metrics
        passed = all(r.passed for r in results)
        overall_score = min([r.overall_score for r in results]) if results else 0.0
        total_rules_checked = sum(r.total_rules_checked for r in results)
        rules_triggered_count = sum(r.rules_triggered_count for r in results)
        
        # Combine all recommendations (deduplicated)
        combined_recommendations = list(set(r for result in results for r in result.recommendations))
        
        # Combine all critical failures
        combined_critical_failures = []
        for r in results:
            for failure in r.critical_failures:
                combined_critical_failures.append(f"{r.constitution_id}:{failure}")
        
        # Calculate processing time
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Generate aggregate report
        logger.info(f"Multi-constitution validation completed in {elapsed_ms:.2f}ms")
        logger.info(f"Result: {'PASSED' if passed else 'FAILED'} with overall score {overall_score:.2f}")
        logger.info(f"Total rules checked: {total_rules_checked}, triggered: {rules_triggered_count}")
        
        if log_level.value >= ValidationLogLevel.STANDARD.value and combined_recommendations:
            logger.info(f"Combined recommendations: {len(combined_recommendations)}")
            if log_level.value >= ValidationLogLevel.VERBOSE.value:
                for i, rec in enumerate(combined_recommendations[:5], 1):
                    logger.info(f"  {i}. {rec}")
                if len(combined_recommendations) > 5:
                    logger.info(f"  ... and {len(combined_recommendations) - 5} more")
        
        # Build comprehensive result dictionary
        return {
            "validation_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "overall_score": overall_score,
            "constitution_results": [r.to_dict() for r in results],
            "combined_recommendations": combined_recommendations,
            "combined_critical_failures": combined_critical_failures,
            "metrics": {
                "total_constitutions": len(constitution_ids),
                "total_rules_checked": total_rules_checked,
                "rules_triggered_count": rules_triggered_count,
                "prompt_length": len(prompt_text),
                "processing_time_ms": elapsed_ms
            }
        }

def load_constitution_from_file(file_path: str, base_dir: Optional[str] = None) -> EthicalConstitution:
    """Loads a single constitution from a YAML file, handling inheritance. (Standalone version)"""
    validator = EthicalConstitutionValidator(constitutions_dir=base_dir or os.path.dirname(file_path))
    return validator._load_constitution(Path(file_path))

def aggregate_results(results: List[ConstitutionValidationResult]) -> Dict[str, Any]:
    """Aggregates multiple validation results into a single summary with enhanced metrics."""
    if not results:
        return {
            "passed": True,
            "overall_score": 1.0,
            "recommendations": [],
            "critical_failures": [],
            "details_by_constitution": {},
            "metrics": {
                "total_constitutions": 0,
                "total_rules_checked": 0,
                "rules_triggered_count": 0,
                "processing_time_ms": 0
            }
        }
    
    # If any result fails, the overall result fails
    passed = all(r.passed for r in results)
    
    # Overall score is the minimum of all scores
    overall_score = min([r.overall_score for r in results])
    
    # Combine all recommendations and critical failures
    recommendations = []
    critical_failures = []
    details_by_constitution = {}
    
    # Aggregate metrics
    total_rules_checked = 0
    rules_triggered_count = 0
    total_processing_time = 0
    rules_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    
    for r in results:
        # Extend recommendations and critical failures
        recommendations.extend(r.recommendations)
        critical_failures.extend(r.critical_failures)
        
        # Aggregate metrics
        total_rules_checked += r.total_rules_checked
        rules_triggered_count += r.rules_triggered_count
        
        # Add processing time if available
        if hasattr(r, 'processing_time_ms') and r.processing_time_ms:
            total_processing_time += r.processing_time_ms
            
        # Aggregate severity counts
        if hasattr(r, 'rules_by_severity') and r.rules_by_severity:
            for severity, count in r.rules_by_severity.items():
                rules_by_severity[severity] = rules_by_severity.get(severity, 0) + count
        
        # Add detailed constitution results
        details_by_constitution[r.constitution_name] = {
            "constitution_id": r.constitution_id,
            "passed": r.passed,
            "overall_score": r.overall_score,
            "critical_failures": r.critical_failures,
            "recommendations": r.recommendations,
            "metrics": {
                "total_rules_checked": r.total_rules_checked,
                "rules_triggered_count": r.rules_triggered_count,
                "rules_by_severity": r.rules_by_severity if hasattr(r, 'rules_by_severity') else {}
            }
        }
    
    # Deduplicate recommendations
    unique_recommendations = list(set(recommendations))
    
    # Create validation timestamp
    validation_timestamp = datetime.now().isoformat()
    
    return {
        "validation_id": str(uuid.uuid4()),
        "timestamp": validation_timestamp,
        "passed": passed,
        "overall_score": overall_score,
        "recommendations": unique_recommendations,
        "critical_failures": critical_failures,
        "details_by_constitution": details_by_constitution,
        "metrics": {
            "total_constitutions": len(results),
            "total_rules_checked": total_rules_checked,
            "rules_triggered_count": rules_triggered_count,
            "rules_by_severity": rules_by_severity,
            "processing_time_ms": total_processing_time
        }
    }

def generate_validation_report(validation_result: Dict[str, Any], format: str = "markdown") -> str:
    """Generate a comprehensive report from validation results.
    
    Args:
        validation_result: The result dictionary from validate_prompts or aggregate_results
        format: Output format ("text", "markdown", "json")
        
    Returns:
        Formatted report string
    """
    if format == "json":
        return json.dumps(validation_result, indent=2)
    
    # Extract key metrics
    passed = validation_result.get("passed", False)
    overall_score = validation_result.get("overall_score", 0.0)
    timestamp = validation_result.get("timestamp", datetime.now().isoformat())
    validation_id = validation_result.get("validation_id", "unknown")
    recommendations = validation_result.get("recommendations", [])
    critical_failures = validation_result.get("critical_failures", [])
    
    # Extract metrics
    metrics = validation_result.get("metrics", {})
    total_constitutions = metrics.get("total_constitutions", 0)
    total_rules_checked = metrics.get("total_rules_checked", 0)
    rules_triggered_count = metrics.get("rules_triggered_count", 0)
    processing_time_ms = metrics.get("processing_time_ms", 0)
    rules_by_severity = metrics.get("rules_by_severity", {})
    
    # Get constitution details
    details_by_constitution = validation_result.get("details_by_constitution", {})
    constitution_results = validation_result.get("constitution_results", [])
    
    if format == "markdown":
        md = []
        md.append(f"# ATRiAN Ethical Constitution Validation Report")
        md.append(f"**Validation ID**: `{validation_id}`")
        md.append(f"**Timestamp**: {timestamp}")
        md.append(f"**Duration**: {processing_time_ms:.2f}ms")
        md.append(f"**Result**: {':white_check_mark: PASSED' if passed else ':x: FAILED'}")
        md.append(f"**Score**: {overall_score:.2f}/1.00")
        
        md.append(f"\n## Summary")
        md.append(f"- Constitutions validated: {total_constitutions}")
        md.append(f"- Rules checked: {total_rules_checked}")
        md.append(f"- Rules triggered: {rules_triggered_count}")
        md.append(f"- Critical issues: {len(critical_failures)}")
        md.append(f"- Recommendations: {len(recommendations)}")
        
        # Add severity breakdown if available
        if rules_by_severity and sum(rules_by_severity.values()) > 0:
            md.append(f"\n## Rules by Severity")
            for severity, count in rules_by_severity.items():
                if count > 0:
                    symbol = ":red_circle:" if severity == "critical" else ":large_orange_circle:" if severity == "high" else ":yellow_circle:" if severity == "medium" else ":green_circle:"
                    md.append(f"- {symbol} **{severity.title()}**: {count}")
        
        # Add recommendations
        if recommendations:
            md.append(f"\n## Recommendations")
            for i, rec in enumerate(recommendations, 1):
                md.append(f"{i}. {rec}")
        
        # Add critical issues
        if critical_failures:
            md.append(f"\n## Critical Issues")
            for i, issue in enumerate(critical_failures, 1):
                md.append(f"{i}. `{issue}`")
        
        # Add per-constitution breakdown
        if constitution_results or details_by_constitution:
            md.append(f"\n## Constitution Details")
            
            # Process results from either source
            constitutions = []
            if constitution_results:
                constitutions = constitution_results
            elif details_by_constitution:
                for name, details in details_by_constitution.items():
                    details["constitution_name"] = name
                    constitutions.append(details)
            
            for i, const in enumerate(constitutions, 1):
                name = const.get("constitution_name", f"Constitution {i}")
                const_id = const.get("constitution_id", "unknown")
                const_score = const.get("overall_score", 0.0)
                const_passed = const.get("passed", False)
                
                md.append(f"### {i}. {name} ({const_id})")
                md.append(f"- **Result**: {':white_check_mark: PASSED' if const_passed else ':x: FAILED'}")
                md.append(f"- **Score**: {const_score:.2f}/1.00")
                
                # Add constitution-specific metrics if available
                const_metrics = const.get("metrics", {})
                if const_metrics:
                    md.append(f"- Rules checked: {const_metrics.get('total_rules_checked', 0)}")
                    md.append(f"- Rules triggered: {const_metrics.get('rules_triggered_count', 0)}")
        
        return "\n".join(md)
    
    else:  # Default to text format
        lines = []
        lines.append("=" * 80)
        lines.append(f"ATRiAN ETHICAL CONSTITUTION VALIDATION REPORT")
        lines.append(f"Validation ID: {validation_id}")
        lines.append(f"Timestamp: {timestamp}")
        lines.append(f"Duration: {processing_time_ms:.2f}ms")
        lines.append("-" * 80)
        lines.append(f"Result: {'PASSED' if passed else 'FAILED'}")
        lines.append(f"Score: {overall_score:.2f}/1.00")
        lines.append(f"Constitutions validated: {total_constitutions}")
        lines.append(f"Rules checked: {total_rules_checked}")
        lines.append(f"Rules triggered: {rules_triggered_count}")
        
        if recommendations:
            lines.append("\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        
        if critical_failures:
            lines.append("\nCRITICAL ISSUES:")
            for i, issue in enumerate(critical_failures, 1):
                lines.append(f"{i}. {issue}")
        
        if constitution_results or details_by_constitution:
            lines.append("\nCONSTITUTION DETAILS:")
            
            # Process results from either source
            constitutions = []
            if constitution_results:
                constitutions = constitution_results
            elif details_by_constitution:
                for name, details in details_by_constitution.items():
                    details["constitution_name"] = name
                    constitutions.append(details)
            
            for i, const in enumerate(constitutions, 1):
                name = const.get("constitution_name", f"Constitution {i}")
                const_id = const.get("constitution_id", "unknown")
                const_score = const.get("overall_score", 0.0)
                const_passed = const.get("passed", False)
                
                lines.append(f"\n{i}. {name} ({const_id})")
                lines.append(f"   Result: {'PASSED' if const_passed else 'FAILED'}")
                lines.append(f"   Score: {const_score:.2f}/1.00")
        
        lines.append("=" * 80)
        return "\n".join(lines)


def combine_constitutions(constitutions: List[EthicalConstitution]) -> EthicalConstitution:
    """
    Combines multiple constitutions into a single one.
    This is useful for creating a unified view of multiple constitutions.
    """
    if not constitutions:
        raise ValueError("No constitutions provided to combine")
    
    if len(constitutions) == 1:
        return constitutions[0]
    
    # Combine rules, avoiding duplicates by ID
    combined_rules = []
    for constitution in constitutions:
        for rule in constitution.rules:
            if not any(r.id == rule.id for r in combined_rules):
                combined_rules.append(rule)
    
    # Combine principles, avoiding duplicates by name
    combined_principles = {}
    critical_principles = []
    
    for constitution in constitutions:
        for principle in constitution.principles:
            if principle.name not in combined_principles:
                combined_principles[principle.name] = principle.model_dump()
                if principle.severity == "critical":
                    critical_principles.append(principle.id)
    
    # Create combined metadata
    combined_metadata = {
        "version": "1.0",
        "created_date": datetime.now(),
        "author": "ATRiAN Validator",
        "purpose": "Combined constitution for multi-constitution validation",
        "applicable_domains": list(set([domain for c in constitutions for domain in c.metadata.applicable_domains])),
        "tags": list(set([tag for c in constitutions for tag in c.metadata.tags])),
        "parent_constitutions": [c.id for c in constitutions],
        "regulatory_alignment": list(set([reg for c in constitutions for reg in c.metadata.regulatory_alignment]))
    }
    
    # Create combined validation config
    combined_validation_config = {
        "severity_impact": {"critical": 1.0, "high": 0.3, "medium": 0.15, "low": 0.05},
        "critical_principles": list(set(critical_principles)),
        "allow_override": False,
        "inheritance_behavior": "extend"
    }
    
    # Create the combined constitution
    combined = EthicalConstitution(
        id=f"combined-{'-'.join([c.id.split('-')[1] for c in constitutions])}",
        name=f"Combined Constitution ({', '.join([c.name for c in constitutions])})",
        description="Automatically generated combined ethical constitution",
        metadata=combined_metadata,
        principles=list(combined_principles.values()),
        rules=combined_rules,
        validation_config=combined_validation_config
    )
    
    return combined


def validate_prompt_with_pv(prompt_vault_id: str, constitution_ids: List[str], validator_dir: Optional[str] = None, log_level: ValidationLogLevel = ValidationLogLevel.STANDARD) -> Dict[str, Any]:
    """Validates a prompt from PromptVault against multiple constitutions with enhanced logging and metrics.
    
    Args:
        prompt_vault_id: ID of the prompt in PromptVault
        constitution_ids: List of constitution IDs or paths to validate against
        validator_dir: Optional directory containing constitutions
        log_level: Level of logging detail
        
    Returns:
        Dict containing validation results with metrics
    """
    try:
        from promptvault import PromptVault
        logger.info(f"Loading prompt {prompt_vault_id} from PromptVault")
        pv = PromptVault()
        prompt = pv.get_prompt(prompt_vault_id)
        logger.info(f"Successfully loaded prompt (length: {len(prompt)})")
    except ImportError:
        logger.error("PromptVault module not available")
        return {"error": "PromptVault module not available"}
    except Exception as e:
        logger.error(f"Failed to load prompt {prompt_vault_id}: {str(e)}")
        return {"error": f"Failed to load prompt {prompt_vault_id}: {str(e)}"}
    
    validator = EthicalConstitutionValidator(constitutions_dir=validator_dir)
    
    # Use the enhanced validate_prompts method
    return validator.validate_prompts(prompt, constitution_ids, log_level)


# Integration functions for PromptVault

def validate_prompt_with_constitutions(prompt: str, constitution_ids: List[str]) -> Dict[str, Any]:
    """
    Validate a prompt against multiple constitutions, returning combined results.
    This function serves as the main integration point with PromptVault.
    
    Args:
        prompt: The prompt text to validate
        constitution_ids: List of constitution IDs to validate against
        
    Returns:
        Dictionary with validation results
    """
    validator = EthicalConstitutionValidator() # Corrected class name here
    
    results = []
    for const_id in constitution_ids:
        try:
            result = validator.validate_prompt(prompt, const_id)
            results.append(result)
        except Exception as e:
            print(f"Error validating prompt against constitution {const_id}: {str(e)}")
    
    passed = all(r.passed for r in results)
    overall_score = min([r.overall_score for r in results]) if results else 0.0
    
    return {
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "overall_score": overall_score,
        "constitution_results": [r.to_dict() for r in results],
        "combined_recommendations": list({r for result in results for r in result.recommendations})
    }