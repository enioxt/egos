#!/usr/bin/env python3
"""File Reference Checker Ultra - Integration Example

This script demonstrates how to use the integration framework to connect
the File Reference Checker Ultra with EGOS subsystems (ETHIK, KOIOS, and NEXUS).

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

import os
import sys
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path to import file_reference_checker_ultra
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import integration components
from integration.integration_manager import IntegrationManager
from integration.ethik_validator import ETHIKValidator
from integration.koios_standards import KOIOSStandardsChecker
from integration.nexus_dependency import NEXUSDependencyMapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("integration_example.log")
    ]
)
logger = logging.getLogger("integration_example")

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="File Reference Checker Ultra - Integration Example"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="integration/config_integration.yaml",
        help="Path to integration configuration file"
    )
    parser.add_argument(
        "--references", 
        type=str, 
        default="",
        help="Path to JSON file containing reference data to process"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="reports/integration",
        help="Directory to save integration reports"
    )
    parser.add_argument(
        "--ethik-only", 
        action="store_true",
        help="Only use ETHIK integration"
    )
    parser.add_argument(
        "--koios-only", 
        action="store_true",
        help="Only use KOIOS integration"
    )
    parser.add_argument(
        "--nexus-only", 
        action="store_true",
        help="Only use NEXUS integration"
    )
    return parser.parse_args()

def load_reference_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load reference data from a JSON file.
    
    Args:
        file_path: Path to JSON file containing reference data
        
    Returns:
        List of reference data dictionaries
    """
    if not file_path or not os.path.exists(file_path):
        # Generate sample reference data if no file provided
        return generate_sample_reference_data()
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        else:
            logger.warning(f"Invalid reference data format in {file_path}. Using sample data.")
            return generate_sample_reference_data()
            
    except Exception as e:
        logger.error(f"Error loading reference data: {str(e)}")
        return generate_sample_reference_data()

def generate_sample_reference_data() -> List[Dict[str, Any]]:
    """
    Generate sample reference data for demonstration.
    
    Returns:
        List of sample reference data dictionaries
    """
    logger.info("Generating sample reference data")
    
    return [
        {
            "source_file": "scripts/ethik/validator.py",
            "target_file": "scripts/ethik/policies/privacy_policy.md",
            "reference_type": "import",
            "line_number": 42,
            "context": "from ethik.policies import privacy_policy",
            "confidence": 0.95
        },
        {
            "source_file": "docs/ROADMAP.md",
            "target_file": "scripts/cross_reference/file_reference_checker_ultra.py",
            "reference_type": "mention",
            "line_number": 87,
            "context": "@references: <!-- TO_BE_REPLACED -->, file_reference_checker_ultra.py",
            "confidence": 0.92
        },
        {
            "source_file": "scripts/koios/documentation_validator.py",
            "target_file": "docs/standards/documentation_standards.md",
            "reference_type": "mention",
            "line_number": 105,
            "context": "# This module implements the KOIOS documentation standards",
            "confidence": 0.85
        },
        {
            "source_file": "scripts/nexus/dependency_analyzer.py",
            "target_file": "scripts/nexus/graph_builder.py",
            "reference_type": "import",
            "line_number": 23,
            "context": "from nexus.graph_builder import build_dependency_graph",
            "confidence": 0.98
        },
        {
            "source_file": "config/secrets.yaml",
            "target_file": "scripts/auth/token_manager.py",
            "reference_type": "mention",
            "line_number": 12,
            "context": "api_token: ${TOKEN_SECRET}",
            "confidence": 0.88
        }
    ]

def initialize_integration_manager(args: argparse.Namespace) -> IntegrationManager:
    """
    Initialize the Integration Manager with configuration.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Initialized IntegrationManager
    """
    # Create custom configuration based on command-line arguments
    if args.ethik_only or args.koios_only or args.nexus_only:
        from integration.integration_manager import IntegrationConfig
        
        config = IntegrationConfig(
            enabled=True,
            ethik_enabled=args.ethik_only or not (args.koios_only or args.nexus_only),
            koios_enabled=args.koios_only or not (args.ethik_only or args.nexus_only),
            nexus_enabled=args.nexus_only or not (args.ethik_only or args.koios_only)
        )
        
        logger.info(f"Using custom integration configuration: " +
                   f"ETHIK={config.ethik_enabled}, " +
                   f"KOIOS={config.koios_enabled}, " +
                   f"NEXUS={config.nexus_enabled}")
        
        return IntegrationManager(None)
    else:
        # Use configuration file
        logger.info(f"Using integration configuration from {args.config}")
        return IntegrationManager(args.config)

def process_references(
    integration_manager: IntegrationManager,
    references: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Process references through the integration manager.
    
    Args:
        integration_manager: Integration manager to use
        references: List of reference data to process
        
    Returns:
        List of processed reference results
    """
    logger.info(f"Processing {len(references)} references through integration")
    
    results = []
    for i, reference in enumerate(references):
        logger.info(f"Processing reference {i+1}/{len(references)}: " +
                   f"{reference.get('source_file', '')} -> {reference.get('target_file', '')}")
        
        result = integration_manager.process_reference(reference)
        results.append(result)
        
        # Log validation status
        status = result.get("validation_status", "unknown")
        logger.info(f"Reference {i+1} validation status: {status}")
        
        # Log validation messages
        for message in result.get("validation_messages", []):
            level = message.get("level", "info")
            if level == "error":
                logger.error(f"  {message.get('message', '')}")
            elif level == "warning":
                logger.warning(f"  {message.get('message', '')}")
            else:
                logger.info(f"  {message.get('message', '')}")
    
    return results

def main():
    """Main function."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize integration manager
    integration_manager = initialize_integration_manager(args)
    
    # Load reference data
    references = load_reference_data(args.references)
    
    # Process references
    results = process_references(integration_manager, references)
    
    # Generate integration report
    report_file = integration_manager.generate_integration_report(results, args.output_dir)
    
    if report_file:
        logger.info(f"Integration report generated: {report_file}")
        
        # Display summary
        with open(report_file, 'r') as f:
            report_data = json.load(f)
            
        summary = report_data.get("summary", {})
        print("\n=== Integration Report Summary ===")
        print(f"Total references: {summary.get('total_references', 0)}")
        print(f"Validation counts: {json.dumps(summary.get('validation_counts', {}), indent=2)}")
        print(f"Subsystem stats: {json.dumps(summary.get('subsystem_stats', {}), indent=2)}")
    else:
        logger.error("Failed to generate integration report")

if __name__ == "__main__":
    main()