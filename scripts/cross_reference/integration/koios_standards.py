"""KOIOS Standards Checker Integration for File Reference Checker Ultra

This module provides integration with the KOIOS subsystem for ensuring
cross-references adhere to documentation standards and maintaining documentation health.

@references: <!-- TO_BE_REPLACED -->, KOIOS documentation standards
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import logging
import json
import uuid
import re
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger("cross_reference_integration.koios")

class KOIOSStandardsChecker:
    """
    Integrates with KOIOS subsystem to ensure references adhere to documentation standards.
    
    This class provides methods for verifying references against KOIOS documentation
    standards, calculating documentation health metrics, and enforcing reference patterns.
    """
    
    def __init__(
        self, 
        standards_version: str = "2.0",
        api_endpoint: str = "http://localhost:8002/koios/standards",
        timeout_sec: int = 30
    ):
        """
        Initialize the KOIOS Standards Checker.
        
        Args:
            standards_version: Version of KOIOS standards to apply
            api_endpoint: KOIOS API endpoint for standards checking
            timeout_sec: API request timeout in seconds
        """
        self.standards_version = standards_version
        self.api_endpoint = api_endpoint
        self.timeout_sec = timeout_sec
        self._load_standards_patterns()
        logger.info(f"KOIOS Standards Checker initialized with standards version {standards_version}")
    
    def _load_standards_patterns(self) -> None:
        """Load standard reference patterns from KOIOS standards."""
        # Standard reference patterns based on KOIOS documentation standards
        self.reference_patterns = {
            # Roadmap references (e.g., <!-- TO_BE_REPLACED -->)
            "roadmap": r"EGOS-(?:EPIC|FEATURE|TASK)-[A-Z]+-\d+",
            
            # Documentation references (e.g., @references: file.md)
            "documentation": r"@references:\s*[\w\s,./\-_]+",
            
            # Code references (e.g., from module import function)
            "code_import": r"(?:import|from)\s+[\w.]+(?:\s+import\s+[\w.]+)?",
            
            # Function references (e.g., function_name())
            "function_call": r"[\w_]+\(.*\)",
            
            # File references (e.g., file.py, file.md)
            "file": r"[\w\-_.]+\.\w+"
        }
        
        # Documentation health thresholds
        self.health_thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "moderate": 0.5,
            "poor": 0.3
        }
    
    def check_standards(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check a reference against KOIOS documentation standards.
        
        Args:
            reference_data: Reference data in standardized format
            
        Returns:
            Standards check result in standardized format
        """
        reference_id = str(uuid.uuid4())
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        reference_type = reference_data.get("reference_type", "")
        context = reference_data.get("context", "")
        
        logger.debug(f"Checking standards for reference from {source_file} to {target_file}")
        
        # Prepare standards check result structure
        check_result = {
            "reference_id": reference_id,
            "validation_status": "valid",
            "validation_messages": [],
            "validator": "KOIOS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "standards_version": self.standards_version,
                "documentation_health": 1.0,
                "pattern_compliance": True
            }
        }
        
        try:
            # Try to connect to KOIOS API if available
            if self._is_api_available():
                api_result = self._call_koios_api(reference_data)
                if api_result:
                    return api_result
            
            # Fallback to local standards checking if API is unavailable
            check_result = self._perform_local_standards_check(reference_data, check_result)
            
        except Exception as e:
            logger.error(f"Error during KOIOS standards check: {str(e)}")
            check_result["validation_status"] = "warning"
            check_result["validation_messages"].append({
                "level": "warning",
                "code": "KOS-ERR-001",
                "message": f"Standards check error: {str(e)}",
                "suggestion": "Review reference manually against KOIOS standards"
            })
        
        return check_result
    
    def _is_api_available(self) -> bool:
        """Check if the KOIOS API is available."""
        try:
            response = requests.get(
                f"{self.api_endpoint}/health", 
                timeout=self.timeout_sec
            )
            return response.status_code == 200
        except:
            logger.warning("KOIOS API is not available, falling back to local standards checking")
            return False
    
    def _call_koios_api(self, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call the KOIOS API for standards checking.
        
        Args:
            reference_data: Reference data to check
            
        Returns:
            Standards check result from API or None if API call fails
        """
        try:
            payload = {
                "reference": reference_data,
                "standards_version": self.standards_version
            }
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout_sec
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"KOIOS API returned status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling KOIOS API: {str(e)}")
            return None
    
    def _perform_local_standards_check(
        self, 
        reference_data: Dict[str, Any], 
        check_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform local standards checking when API is unavailable.
        
        Args:
            reference_data: Reference data to check
            check_result: Initial standards check result structure
            
        Returns:
            Updated standards check result
        """
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        reference_type = reference_data.get("reference_type", "")
        context = reference_data.get("context", "")
        
        # Check file extensions and naming conventions
        source_ext = Path(source_file).suffix.lower() if source_file else ""
        target_ext = Path(target_file).suffix.lower() if target_file else ""
        
        # Initialize health metrics
        pattern_compliance = True
        health_factors = []
        
        # Check reference pattern compliance
        if reference_type == "import" and not self._check_pattern(context, self.reference_patterns["code_import"]):
            pattern_compliance = False
            check_result["validation_status"] = "warning"
            check_result["validation_messages"].append({
                "level": "warning",
                "code": "KOS-PAT-001",
                "message": "Import reference does not follow KOIOS standards",
                "suggestion": "Use standard import format: 'from module import function'"
            })
            health_factors.append(0.7)  # Partial compliance
        
        # Check documentation reference format
        if reference_type == "mention" and source_ext in [".md", ".rst", ".txt"]:
            if not self._check_pattern(context, self.reference_patterns["documentation"]):
                pattern_compliance = False
                check_result["validation_status"] = "warning"
                check_result["validation_messages"].append({
                    "level": "warning",
                    "code": "KOS-PAT-002",
                    "message": "Documentation reference does not follow KOIOS standards",
                    "suggestion": "Use standard reference format: '@references: file.md'"
                })
                health_factors.append(0.6)  # Lower compliance for documentation
        
        # Check roadmap reference format
        if reference_type == "mention" and "roadmap" in source_file.lower():
            if not self._check_pattern(context, self.reference_patterns["roadmap"]):
                pattern_compliance = False
                check_result["validation_status"] = "warning"
                check_result["validation_messages"].append({
                    "level": "warning",
                    "code": "KOS-PAT-003",
                    "message": "Roadmap reference does not follow KOIOS standards",
                    "suggestion": "Use standard roadmap ID format: '<!-- TO_BE_REPLACED -->'"
                })
                health_factors.append(0.5)  # Lower compliance for roadmap references
        
        # Check file naming conventions
        if not self._check_file_naming_convention(source_file):
            check_result["validation_status"] = "warning"
            check_result["validation_messages"].append({
                "level": "warning",
                "code": "KOS-NAM-001",
                "message": "Source file name does not follow KOIOS naming conventions",
                "suggestion": "Use snake_case for file names"
            })
            health_factors.append(0.8)  # Minor issue
        
        if not self._check_file_naming_convention(target_file):
            check_result["validation_status"] = "warning"
            check_result["validation_messages"].append({
                "level": "warning",
                "code": "KOS-NAM-002",
                "message": "Target file name does not follow KOIOS naming conventions",
                "suggestion": "Use snake_case for file names"
            })
            health_factors.append(0.8)  # Minor issue
        
        # Calculate documentation health score
        documentation_health = self._calculate_documentation_health(health_factors)
        check_result["metadata"]["documentation_health"] = documentation_health
        check_result["metadata"]["pattern_compliance"] = pattern_compliance
        
        # Add health assessment
        health_assessment = self._assess_documentation_health(documentation_health)
        check_result["metadata"]["health_assessment"] = health_assessment
        
        # Add suggestions for improvement if health is not excellent
        if health_assessment != "excellent" and check_result["validation_status"] != "invalid":
            check_result["validation_messages"].append({
                "level": "info",
                "code": "KOS-HEALTH-001",
                "message": f"Documentation health assessment: {health_assessment} ({documentation_health:.2f})",
                "suggestion": "Review KOIOS documentation standards to improve reference quality"
            })
        
        return check_result
    
    def _check_pattern(self, text: str, pattern: str) -> bool:
        """
        Check if text matches a pattern.
        
        Args:
            text: Text to check
            pattern: Regex pattern to match
            
        Returns:
            True if pattern matches, False otherwise
        """
        if not text:
            return False
        
        return bool(re.search(pattern, text))
    
    def _check_file_naming_convention(self, file_path: str) -> bool:
        """
        Check if a file name follows KOIOS naming conventions.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if naming convention is followed, False otherwise
        """
        if not file_path:
            return True  # Skip empty paths
        
        file_name = Path(file_path).name
        
        # Check for snake_case (lowercase with underscores)
        snake_case_pattern = r"^[a-z0-9_]+(\.[a-z0-9]+)?$"
        return bool(re.match(snake_case_pattern, file_name))
    
    def _calculate_documentation_health(self, health_factors: List[float]) -> float:
        """
        Calculate documentation health score based on health factors.
        
        Args:
            health_factors: List of health factor scores (0.0 to 1.0)
            
        Returns:
            Documentation health score (0.0 to 1.0)
        """
        if not health_factors:
            return 1.0  # Perfect health if no factors
        
        return sum(health_factors) / len(health_factors)
    
    def _assess_documentation_health(self, health_score: float) -> str:
        """
        Assess documentation health based on score.
        
        Args:
            health_score: Documentation health score (0.0 to 1.0)
            
        Returns:
            Health assessment ("excellent", "good", "moderate", "poor", "critical")
        """
        if health_score >= self.health_thresholds["excellent"]:
            return "excellent"
        elif health_score >= self.health_thresholds["good"]:
            return "good"
        elif health_score >= self.health_thresholds["moderate"]:
            return "moderate"
        elif health_score >= self.health_thresholds["poor"]:
            return "poor"
        else:
            return "critical"
    
    def generate_documentation_health_report(self, check_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a documentation health report from check results.
        
        Args:
            check_results: List of standards check results
            
        Returns:
            Documentation health report
        """
        if not check_results:
            return {
                "report_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "overall_health": 0.0,
                "assessment": "unknown",
                "file_count": 0,
                "reference_count": 0,
                "issues": []
            }
        
        # Extract health scores
        health_scores = [
            result.get("metadata", {}).get("documentation_health", 0.0)
            for result in check_results
        ]
        
        # Calculate overall health
        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        
        # Collect issues
        issues = []
        for result in check_results:
            for message in result.get("validation_messages", []):
                if message.get("level") in ["warning", "error"]:
                    issues.append({
                        "code": message.get("code", ""),
                        "message": message.get("message", ""),
                        "suggestion": message.get("suggestion", ""),
                        "reference_id": result.get("reference_id", "")
                    })
        
        # Generate report
        return {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_health": overall_health,
            "assessment": self._assess_documentation_health(overall_health),
            "file_count": len(set([
                result.get("reference_data", {}).get("source_file", "")
                for result in check_results
            ])),
            "reference_count": len(check_results),
            "issues": issues,
            "standards_version": self.standards_version
        }