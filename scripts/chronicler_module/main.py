#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""KOIOS Chronicler Module - Main Entry Point

This script serves as the CLI entry point for the Chronicler Module,
orchestrating the analysis, generation, and rendering processes.

Part of the KOIOS subsystem within EGOS.

Usage:
    python main.py "<path_to_project_directory>" [options]

Options:
    -o, --output <dir>    Specify output directory (default: current directory)
    -c, --config <file>   Specify custom config file (default: chronicler_config.yaml)
    -v, --verbose         Enable verbose logging
    -h, --help            Show this help message

Example:
    python main.py "C:/my_project" -o "C:/reports" -v

Author: EGOS Team
Date Created: 2025-04-22
Last Modified: 2025-05-18

@references: 
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
import argparse
import logging
from typing import Dict, Any, Optional
import yaml

# Local imports
from analyzer import CodebaseAnalyzer
from generator import DocumentationGenerator
from renderer import HTMLRenderer

# Constants
DEFAULT_CONFIG_FILE = "chronicler_config.yaml"
DEFAULT_OUTPUT_DIR = "."
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(output_dir: str, verbose: bool = False) -> None:
    """
    Configure logging for the Chronicler module.
    
    Args:
        output_dir: Directory where log file will be created
        verbose: If True, sets logging level to DEBUG, otherwise INFO
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = os.path.join(output_dir, "chronicler.log")
    
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info(f"Logging initialized. Log file: {log_file}")


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file has invalid YAML
    """
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        logging.info(f"Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_file}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file: {e}")
        raise


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Namespace containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="KOIOS Chronicler - AI-powered documentation generator"
    )
    
    parser.add_argument(
        "project_dir",
        help="Path to the project directory to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for generated files (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "-c", "--config",
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to configuration file (default: {DEFAULT_CONFIG_FILE})"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the Chronicler Module.
    
    Orchestrates the analysis, generation, and rendering processes.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.output, args.verbose)
    logging.info("KOIOS Chronicler Module starting...")
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Validate project directory
        if not os.path.isdir(args.project_dir):
            logging.error(f"Project directory does not exist: {args.project_dir}")
            sys.exit(1)
        
        # Initialize components
        logging.info(f"Analyzing project: {args.project_dir}")
        analyzer = CodebaseAnalyzer(args.project_dir, config)
        generator = DocumentationGenerator(config)
        renderer = HTMLRenderer(config)
        
        # Analyze codebase
        analysis_results = analyzer.analyze()
        logging.info(f"Analysis complete. Found {len(analysis_results['files'])} files.")
        
        # Generate documentation
        documentation = generator.generate(analysis_results)
        logging.info("Documentation generation complete.")
        
        # Render output
        output_file = renderer.render(documentation, args.project_dir, args.output)
        logging.info(f"Report generated: {output_file}")
        
        logging.info("KOIOS Chronicler Module completed successfully.")
        print(f"\nDocumentation generated successfully: {output_file}")
        
    except Exception as e:
        logging.exception(f"Error in Chronicler execution: {e}")
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()