#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Health Check Framework

This script serves as the main entry point for the EGOS Health Check Framework.
It provides a unified interface for running various health checks across the EGOS project,
generating reports, and suggesting fixes for identified issues.

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
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core components
from core.orchestrator import HealthCheckOrchestrator
from core.base_validator import print_banner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_check")

# Constants
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "health_check_config.json")
DEFAULT_VALIDATORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validators")
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "health_check")

def create_default_config() -> Dict[str, Any]:
    """Create default configuration for the health check framework.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "validators": {
            "naming_convention": {
                "enabled": True,
                "severity_threshold": "warning",
                "exclusions": {
                    "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
                    "files": ["README.md", "LICENSE", "Makefile", "requirements.txt", ".gitignore", ".gitattributes"],
                    "extensions_to_ignore": [".md", ".MD"],
                    "patterns_to_ignore": [r".*\.git.*", r".*node_modules.*", r".*__pycache__.*", r".*\.vscode.*"]
                }
            },
            "directory_structure": {
                "enabled": False,
                "severity_threshold": "error",
                "structure_definition": os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "directory_structure_definition.json")
            },
            "script_standards": {
                "enabled": False,
                "severity_threshold": "warning"
            },
            "cross_reference": {
                "enabled": False,
                "severity_threshold": "warning"
            }
        },
        "reporting": {
            "format": "markdown",
            "output_path": os.path.join(DEFAULT_OUTPUT_DIR, f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"),
            "include_visualizations": True
        },
        "remediation": {
            "suggest_fixes": True,
            "auto_apply": False,
            "backup_before_fix": True
        }
    }

def ensure_config_exists(config_path: str) -> None:
    """Ensure that the configuration file exists, creating it if necessary.
    
    Args:
        config_path: Path to the configuration file
    """
    if not os.path.exists(config_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Create default configuration
        config = create_default_config()
        
        # Write configuration to file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created default configuration at {config_path}")

def main() -> int:
    """Main function for running the health check framework from the command line.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="EGOS Health Check Framework")
    parser.add_argument("target_path", nargs="?", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help="Path to validate (default: EGOS root directory)")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                        help=f"Path to configuration file (default: {DEFAULT_CONFIG_PATH})")
    parser.add_argument("--validators", nargs="+",
                        help="Validators to run (default: all enabled in config)")
    parser.add_argument("--output",
                        help="Path to save the report (default: from config)")
    parser.add_argument("--fix", action="store_true",
                        help="Suggest fixes for issues")
    parser.add_argument("--auto-fix", action="store_true",
                        help="Automatically apply fixes (use with caution)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only simulate fixes")
    parser.add_argument("--create-config", action="store_true",
                        help="Create default configuration file")
    parser.add_argument("--list-validators", action="store_true",
                        help="List available validators")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print_banner()
    
    # Create default configuration if requested
    if args.create_config:
        ensure_config_exists(args.config)
        print(f"Created default configuration at {args.config}")
        return 0
    
    # Ensure configuration exists
    ensure_config_exists(args.config)
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return 1
    
    # Create orchestrator
    orchestrator = HealthCheckOrchestrator(args.config)
    
    # Discover validators
    orchestrator.discover_validators(DEFAULT_VALIDATORS_DIR)
    
    # List validators if requested
    if args.list_validators:
        print("Available validators:")
        for name in orchestrator.validators:
            enabled = config.get("validators", {}).get(name, {}).get("enabled", False)
            status = "Enabled" if enabled else "Disabled"
            print(f"  - {name}: {status}")
        return 0
    
    # Determine which validators to run
    validators_to_run = []
    if args.validators:
        validators_to_run = args.validators
    else:
        # Use enabled validators from configuration
        for name, validator_config in config.get("validators", {}).items():
            if validator_config.get("enabled", False):
                validators_to_run.append(name)
    
    if not validators_to_run:
        logger.warning("No validators enabled. Enable validators in the configuration or specify with --validators")
        return 0
    
    # Ensure target path exists
    target_path = Path(args.target_path)
    if not target_path.exists():
        logger.error(f"Target path does not exist: {target_path}")
        return 1
    
    # Run validators
    logger.info(f"Running validators: {', '.join(validators_to_run)}")
    results = orchestrator.run_validators(target_path, validators_to_run)
    
    # Determine output path
    output_path = args.output
    if not output_path:
        output_path = config.get("reporting", {}).get("output_path")
        if not output_path:
            # Generate default output path
            os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(DEFAULT_OUTPUT_DIR, f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    # Generate report
    report = orchestrator.generate_report(results, output_path)
    logger.info(f"Report saved to {output_path}")
    
    # Print summary
    total_issues = sum(len(result.issues) for result in results.values())
    print(f"\nTotal issues found: {total_issues}")
    
    # Suggest fixes if requested
    if args.fix or args.auto_fix:
        fix_results = orchestrator.suggest_fixes(results, not args.auto_fix)
        print("\nFix Results:")
        for name, result in fix_results.items():
            print(f"\n{name}:")
            if "error" in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Total: {result.get('total', 0)}")
                print(f"  Successful: {result.get('successful', 0)}")
                print(f"  Failed: {result.get('failed', 0)}")
    
    # Return exit code based on issues found
    return 1 if total_issues > 0 else 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)