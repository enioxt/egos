"""Integration Manager for File Reference Checker Ultra

This module provides the core integration framework for connecting
the File Reference Checker Ultra with EGOS subsystems.

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
import os
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger("cross_reference_integration")

@dataclass
class IntegrationConfig:
    """Configuration for subsystem integration."""
    enabled: bool = True
    ethik_enabled: bool = True
    koios_enabled: bool = True
    nexus_enabled: bool = True
    ethik_validation_level: str = "standard"
    ethik_api_endpoint: str = "http://localhost:8001/ethik/validate"
    ethik_timeout_sec: int = 30
    koios_standards_version: str = "2.0"
    koios_api_endpoint: str = "http://localhost:8002/koios/standards"
    koios_timeout_sec: int = 30
    nexus_dependency_mapping: bool = True
    nexus_impact_analysis: bool = True
    nexus_visualization: bool = True
    nexus_api_endpoint: str = "http://localhost:8003/nexus/analyze"
    nexus_timeout_sec: int = 60


class IntegrationManager:
    """
    Manages integration between File Reference Checker Ultra and EGOS subsystems.
    
    This class serves as the central coordination point for all subsystem
    integrations, handling configuration, data exchange, and API communication.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Integration Manager.
        
        Args:
            config_path: Path to the integration configuration file.
                         If None, uses default configuration.
        """
        self.config = self._load_config(config_path)
        self.ethik_validator = None
        self.koios_checker = None
        self.nexus_mapper = None
        self._initialize_integrations()
        logger.info(f"Integration Manager initialized with {self._get_enabled_integrations()} active integrations")
    
    def _load_config(self, config_path: Optional[str]) -> IntegrationConfig:
        """
        Load integration configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            IntegrationConfig object with parsed configuration
        """
        if not config_path:
            logger.info("No configuration file provided, using defaults")
            return IntegrationConfig()
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Extract integration configuration
            integration_config = config_data.get('integration', {})
            
            # Create configuration object
            config = IntegrationConfig(
                enabled=integration_config.get('enabled', True),
                ethik_enabled=integration_config.get('ethik', {}).get('enabled', True),
                koios_enabled=integration_config.get('koios', {}).get('enabled', True),
                nexus_enabled=integration_config.get('nexus', {}).get('enabled', True),
                ethik_validation_level=integration_config.get('ethik', {}).get('validation_level', "standard"),
                ethik_api_endpoint=integration_config.get('ethik', {}).get('api_endpoint', "http://localhost:8001/ethik/validate"),
                ethik_timeout_sec=integration_config.get('ethik', {}).get('timeout_sec', 30),
                koios_standards_version=integration_config.get('koios', {}).get('standards_version', "2.0"),
                koios_api_endpoint=integration_config.get('koios', {}).get('api_endpoint', "http://localhost:8002/koios/standards"),
                koios_timeout_sec=integration_config.get('koios', {}).get('timeout_sec', 30),
                nexus_dependency_mapping=integration_config.get('nexus', {}).get('dependency_mapping', True),
                nexus_impact_analysis=integration_config.get('nexus', {}).get('impact_analysis', True),
                nexus_visualization=integration_config.get('nexus', {}).get('visualization', True),
                nexus_api_endpoint=integration_config.get('nexus', {}).get('api_endpoint', "http://localhost:8003/nexus/analyze"),
                nexus_timeout_sec=integration_config.get('nexus', {}).get('timeout_sec', 60)
            )
            
            logger.info(f"Loaded integration configuration from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading integration configuration: {str(e)}")
            logger.info("Using default configuration")
            return IntegrationConfig()
    
    def _initialize_integrations(self) -> None:
        """Initialize all enabled subsystem integrations."""
        if not self.config.enabled:
            logger.info("Integration is disabled, skipping initialization")
            return
        
        # Import integrations only when needed to avoid circular imports
        if self.config.ethik_enabled:
            from .ethik_validator import ETHIKValidator
            self.ethik_validator = ETHIKValidator(
                validation_level=self.config.ethik_validation_level,
                api_endpoint=self.config.ethik_api_endpoint,
                timeout_sec=self.config.ethik_timeout_sec
            )
            logger.info("ETHIK integration initialized")
        
        if self.config.koios_enabled:
            from .koios_standards import KOIOSStandardsChecker
            self.koios_checker = KOIOSStandardsChecker(
                standards_version=self.config.koios_standards_version,
                api_endpoint=self.config.koios_api_endpoint,
                timeout_sec=self.config.koios_timeout_sec
            )
            logger.info("KOIOS integration initialized")
        
        if self.config.nexus_enabled:
            from .nexus_dependency import NEXUSDependencyMapper
            self.nexus_mapper = NEXUSDependencyMapper(
                dependency_mapping=self.config.nexus_dependency_mapping,
                impact_analysis=self.config.nexus_impact_analysis,
                visualization=self.config.nexus_visualization,
                api_endpoint=self.config.nexus_api_endpoint,
                timeout_sec=self.config.nexus_timeout_sec
            )
            logger.info("NEXUS integration initialized")
    
    def _get_enabled_integrations(self) -> List[str]:
        """Get a list of enabled integrations."""
        enabled = []
        if self.config.ethik_enabled:
            enabled.append("ETHIK")
        if self.config.koios_enabled:
            enabled.append("KOIOS")
        if self.config.nexus_enabled:
            enabled.append("NEXUS")
        return enabled
    
    def process_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a reference through all enabled integrations.
        
        Args:
            reference_data: Reference data in standardized format
            
        Returns:
            Processed reference data with validation results
        """
        if not self.config.enabled:
            return reference_data
        
        results = {
            "reference_data": reference_data,
            "validation_results": [],
            "processed_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Process through ETHIK
        if self.config.ethik_enabled and self.ethik_validator:
            ethik_result = self.ethik_validator.validate_reference(reference_data)
            results["validation_results"].append(ethik_result)
        
        # Process through KOIOS
        if self.config.koios_enabled and self.koios_checker:
            koios_result = self.koios_checker.check_standards(reference_data)
            results["validation_results"].append(koios_result)
        
        # Process through NEXUS
        if self.config.nexus_enabled and self.nexus_mapper:
            nexus_result = self.nexus_mapper.map_dependency(reference_data)
            results["validation_results"].append(nexus_result)
        
        return results
    
    def process_references_batch(self, references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of references through all enabled integrations.
        
        Args:
            references: List of reference data in standardized format
            
        Returns:
            List of processed reference data with validation results
        """
        return [self.process_reference(ref) for ref in references]
    
    def generate_integration_report(self, results: List[Dict[str, Any]], output_dir: str) -> str:
        """
        Generate a comprehensive integration report from processing results.
        
        Args:
            results: List of processed reference results
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report file
        """
        if not results:
            logger.warning("No results to generate report from")
            return ""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"integration_report_{timestamp}.json")
        
        # Compile report data
        report_data = {
            "report_id": f"XREF-INT-{timestamp}",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "integrations_used": self._get_enabled_integrations(),
            "summary": self._generate_summary(results),
            "detailed_results": results
        }
        
        # Write report to file
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Integration report generated: {report_file}")
        return report_file
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of processing results."""
        total_references = len(results)
        validation_counts = {
            "valid": 0,
            "invalid": 0,
            "warning": 0
        }
        
        subsystem_stats = {
            "ETHIK": {"valid": 0, "invalid": 0, "warning": 0},
            "KOIOS": {"valid": 0, "invalid": 0, "warning": 0},
            "NEXUS": {"valid": 0, "invalid": 0, "warning": 0}
        }
        
        for result in results:
            for validation in result.get("validation_results", []):
                status = validation.get("validation_status", "")
                validator = validation.get("validator", "")
                
                if status in validation_counts:
                    validation_counts[status] += 1
                
                if validator in subsystem_stats and status in subsystem_stats[validator]:
                    subsystem_stats[validator][status] += 1
        
        return {
            "total_references": total_references,
            "validation_counts": validation_counts,
            "subsystem_stats": subsystem_stats
        }