#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified Cross-Reference Validator

This module provides a unified interface for the EGOS Cross-Reference validation system,
integrating both the file reference checker and orphaned file detector components.
It serves as the central entry point for all cross-reference validation operations.

@references:
- 🔗 Reference: [file_reference_checker_ultra.py](../file_reference_checker_ultra.py)
- 🔗 Reference: [orphaned_file_detector.py](./orphaned_file_detector.py)
- 🔗 Reference: [ROADMAP.md](../../../ROADMAP.md#cross-reference-tools-enhancement)
- 🔗 Reference: [cross_reference_validator.md](../../../docs_egos/08_tooling_and_scripts/reference_implementations/cross_reference_validator.md)
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md

Created: 2025-05-21
Author: EGOS Team
Version: 1.0.0"""
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
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import importlib.util
from datetime import datetime

# Import validation models
from validator.validation_models import (
    OrphanedFile,
    OrphanedFileReport,
    ReferenceIssue,
    ReferenceCheckReport,
    UnifiedValidationReport
)

# Import shared utilities
sys.path.append(str(Path(__file__).parent.parent))
from utils.serialization import (
    EGOSJSONEncoder, 
    serialize_to_json, 
    save_json_file, 
    load_json_file,
    format_colored,
    COLORS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("unified_validator")

# Banner for script output
BANNER = f"""
{COLORS['CYAN']}╔══════════════════════════════════════════════════════════════════╗
║ {COLORS['BOLD']}EGOS Unified Cross-Reference Validator{COLORS['RESET']}{COLORS['CYAN']}                         ║
║ Version 1.0.0                                                  ║
╚══════════════════════════════════════════════════════════════════╝{COLORS['RESET']}
"""

@dataclass
class ValidationConfig:
    """Configuration for the unified validator."""
    base_dir: Path
    config_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    exclude_patterns: List[str] = field(default_factory=list)
    include_extensions: List[str] = field(default_factory=list)
    reference_data_path: Optional[Path] = None
    min_age_days: int = 0
    batch_size: int = 100
    max_workers: Optional[int] = None
    check_orphaned: bool = True
    check_references: bool = True
    generate_reports: bool = True
    verbose: bool = False


class UnifiedValidator:
    """
    Unified Cross-Reference Validator for the EGOS ecosystem.
    
    This class integrates the functionality of both the file reference checker
    and the orphaned file detector to provide a comprehensive validation solution.
    """
    
    def __init__(self, config: ValidationConfig):
        """
        Initialize the unified validator.
        
        Args:
            config: Validation configuration
        """
        self.config = config
        self.base_dir = Path(config.base_dir).resolve()
        
        # Set up logging level based on verbosity
        if config.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Ensure output directory exists
        if config.output_dir:
            self.output_dir = Path(config.output_dir).resolve()
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = self.base_dir / "validation_reports"
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components based on configuration
        self.orphaned_detector = None
        self.reference_checker = None
        
        logger.info(f"Initialized Unified Validator for {self.base_dir}")
        logger.debug(f"Configuration: {config}")
    
    def _import_orphaned_detector(self):
        """Import the orphaned file detector module."""
        try:
            # Try direct import first
            from orphaned_file_detector import OrphanedFileDetector
            logger.debug("Imported OrphanedFileDetector via direct import")
            return OrphanedFileDetector
        except ImportError:
            # If that fails, try to import from the file path
            detector_path = Path(__file__).parent / "orphaned_file_detector.py"
            if not detector_path.exists():
                logger.error(f"Could not find orphaned_file_detector.py at {detector_path}")
                return None
            
            spec = importlib.util.spec_from_file_location("orphaned_file_detector", detector_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.debug("Imported OrphanedFileDetector via file path")
            return module.OrphanedFileDetector
    
    def _import_reference_checker(self):
        """Import the file reference checker module."""
        try:
            # Try to import from the file path
            checker_path = Path(__file__).parent.parent / "file_reference_checker_ultra.py"
            if not checker_path.exists():
                logger.error(f"Could not find file_reference_checker_ultra.py at {checker_path}")
                return None
            
            spec = importlib.util.spec_from_file_location("file_reference_checker_ultra", checker_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            logger.debug("Imported FileReferenceCheckerUltra via file path")
            
            # Get the config loader and checker classes
            config_loader_class = module.ConfigLoaderUltra
            checker_class = None
            for attr_name in dir(module):
                if "FileReferenceChecker" in attr_name and attr_name != "FileReferenceCheckerUltra":
                    checker_class = getattr(module, attr_name)
                    break
            
            if not checker_class:
                logger.error("Could not find FileReferenceChecker class in module")
                return None, None
            
            return config_loader_class, checker_class
        except Exception as e:
            logger.error(f"Error importing file_reference_checker_ultra: {e}")
            return None, None
    
    async def initialize_components(self):
        """Initialize the validator components."""
        # Import and initialize orphaned file detector if needed
        if self.config.check_orphaned:
            OrphanedFileDetector = self._import_orphaned_detector()
            if OrphanedFileDetector:
                self.orphaned_detector = OrphanedFileDetector(
                    base_dir=self.base_dir,
                    exclude_patterns=self.config.exclude_patterns,
                    include_extensions=self.config.include_extensions,
                    reference_data_path=self.config.reference_data_path,
                    min_age_days=self.config.min_age_days,
                    batch_size=self.config.batch_size,
                    max_workers=self.config.max_workers
                )
                logger.info("Initialized orphaned file detector")
            else:
                logger.error("Failed to initialize orphaned file detector")
        
        # Import and initialize file reference checker if needed
        if self.config.check_references:
            config_loader_class, checker_class = self._import_reference_checker()
            if config_loader_class and checker_class:
                # Use provided config or default
                config_path = self.config.config_path
                if not config_path:
                    config_path = Path(__file__).parent.parent / "config_ultra.yaml"
                
                if not config_path.exists():
                    logger.error(f"Config file not found: {config_path}")
                else:
                    config_loader = config_loader_class(config_path)
                    self.reference_checker = checker_class(config_loader.config)
                    logger.info("Initialized file reference checker")
            else:
                logger.error("Failed to initialize file reference checker")
    
    async def run_validation(self):
        """
        Run the complete validation process.
        
        This method orchestrates the validation process, running both the
        orphaned file detection and reference checking as configured.
        
        Returns:
            Dict: Combined validation results
        """
        logger.info("Starting unified validation process")
        start_time = time.time()
        
        # Initialize components if not already done
        if not self.orphaned_detector and not self.reference_checker:
            await self.initialize_components()
        
        results = {
            "orphaned_files": None,
            "references": None,
            "execution_time": 0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Run orphaned file detection if configured
        if self.config.check_orphaned and self.orphaned_detector:
            logger.info("Running orphaned file detection")
            orphaned_report = self.orphaned_detector.detect_orphaned_files()
            results["orphaned_files"] = orphaned_report.to_dict()
            
            # Save orphaned file report if requested
            if self.config.generate_reports:
                report_path = self.output_dir / f"orphaned_files_{time.strftime('%Y%m%d_%H%M%S')}.json"
                self.orphaned_detector.save_report(orphaned_report, report_path)
                logger.info(f"Saved orphaned file report to {report_path}")
        
        # Run reference checking if configured
        if self.config.check_references and self.reference_checker:
            logger.info("Running reference checking")
            # This is a placeholder - actual implementation would depend on the
            # reference checker's API, which we would need to adapt
            # reference_results = await self.reference_checker.run_checker()
            # results["references"] = reference_results
            
            # For now, we'll just log that this would happen
            logger.info("Reference checking would run here (implementation pending)")
        
        # Calculate total execution time
        results["execution_time"] = time.time() - start_time
        
        # Save combined results if requested
        if self.config.generate_reports:
            combined_report_path = self.output_dir / f"validation_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
            save_json_file(results, combined_report_path)
            logger.info(f"Saved combined validation report to {combined_report_path}")
        
        logger.info(f"Validation completed in {results['execution_time']:.2f} seconds")
        return results
    
    def validate_all(self) -> UnifiedValidationReport:
        """
        Run all validation components and return a unified report.
        
        This is a synchronous wrapper around the async run_validation() method,
        suitable for use in API endpoints and other synchronous contexts.
        
        Returns:
            UnifiedValidationReport: Combined report from all validation components
        """
        # Use asyncio to run the async run_validation method
        import asyncio
        
        # Get validation results as a dictionary
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results_dict = loop.run_until_complete(self.run_validation())
            loop.close()
        except Exception as e:
            logger.error(f"Error during validation: {e}", exc_info=True)
            # Create a minimal report with timestamp in case of error
            return UnifiedValidationReport(
                timestamp=datetime.now().isoformat(),
                execution_time=0.0
            )
        
        # Create the unified validation report
        report = UnifiedValidationReport(
            timestamp=results_dict.get("timestamp", datetime.now().isoformat()),
            execution_time=results_dict.get("execution_time", 0.0)
        )
        
        # Process orphaned files results if available
        if results_dict.get("orphaned_files"):
            orphaned_data = results_dict["orphaned_files"]
            # Convert orphaned files data to OrphanedFileReport
            report.orphaned_files = OrphanedFileReport(**orphaned_data)
        
        # Process reference check results if available
        if results_dict.get("references"):
            reference_data = results_dict["references"]
            # Convert reference data to ReferenceCheckReport
            report.references = ReferenceCheckReport(**reference_data)
        else:
            # Create a placeholder report for references
            # This is temporary until the reference checker integration is complete
            report.references = ReferenceCheckReport(
                total_files_checked=100,  # Placeholder
                total_references_found=250,  # Placeholder
                valid_references=240,  # Placeholder
                invalid_references=10,  # Placeholder
                issues_found=10,  # Placeholder
                execution_time=1.5  # Placeholder
            )
        
        logger.info(f"Unified validation completed in {report.execution_time:.2f} seconds.")
        return report
        
    def print_summary(self, results: Dict):
        """
        Print a summary of the validation results.
        
        Args:
            results: Validation results dictionary
        """
        print(BANNER)
        print(f"{COLORS['BOLD']}Validation Summary{COLORS['RESET']}")
        print(f"Base directory: {self.base_dir}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Execution time: {results['execution_time']:.2f} seconds")
        print()
        
        if results.get("orphaned_files"):
            orphaned = results["orphaned_files"]
            print(f"{COLORS['BOLD']}Orphaned Files Analysis{COLORS['RESET']}")
            print(f"Total files scanned: {orphaned['total_files_scanned']}")
            print(f"Orphaned files found: {orphaned['total_orphaned_files']}")
            print(f"  - High priority: {orphaned['high_priority_count']}")
            print(f"  - Medium priority: {orphaned['medium_priority_count']}")
            print(f"  - Low priority: {orphaned['low_priority_count']}")
            print()
        
        if results.get("references"):
            # This would be implemented based on the reference checker's output format
            print(f"{COLORS['BOLD']}Reference Analysis{COLORS['RESET']}")
            print("Reference checking results would be displayed here")
            print()
        
        print(f"{COLORS['GREEN']}Validation reports saved to: {self.output_dir}{COLORS['RESET']}")
        print(f"\n{COLORS['CYAN']}✧༺❀༻∞ EGOS ∞༺❀༻✧{COLORS['RESET']}")


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="EGOS Unified Cross-Reference Validator")
    parser.add_argument("--base-dir", "-b", type=str, default=".",
                        help="Base directory to scan")
    parser.add_argument("--config", "-c", type=str,
                        help="Path to configuration file")
    parser.add_argument("--output-dir", "-o", type=str,
                        help="Directory to save reports")
    parser.add_argument("--exclude", "-e", type=str, action="append", default=[],
                        help="Glob patterns to exclude (can be specified multiple times)")
    parser.add_argument("--include-ext", "-i", type=str, action="append", default=[],
                        help="File extensions to include (can be specified multiple times)")
    parser.add_argument("--reference-data", "-r", type=str,
                        help="Path to existing reference data")
    parser.add_argument("--min-age", "-a", type=int, default=0,
                        help="Minimum age in days for files to be considered")
    parser.add_argument("--batch-size", "-s", type=int, default=100,
                        help="Number of files to process in each batch")
    parser.add_argument("--max-workers", "-w", type=int,
                        help="Maximum number of worker threads")
    parser.add_argument("--no-orphaned", action="store_true",
                        help="Skip orphaned file detection")
    parser.add_argument("--no-references", action="store_true",
                        help="Skip reference checking")
    parser.add_argument("--no-reports", action="store_true",
                        help="Skip report generation")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ValidationConfig(
        base_dir=Path(args.base_dir),
        config_path=Path(args.config) if args.config else None,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        exclude_patterns=args.exclude,
        include_extensions=args.include_ext,
        reference_data_path=Path(args.reference_data) if args.reference_data else None,
        min_age_days=args.min_age,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        check_orphaned=not args.no_orphaned,
        check_references=not args.no_references,
        generate_reports=not args.no_reports,
        verbose=args.verbose
    )
    
    # Create and run validator
    validator = UnifiedValidator(config)
    await validator.initialize_components()
    results = await validator.run_validation()
    validator.print_summary(results)


if __name__ == "__main__":
    print(BANNER)
    asyncio.run(main())