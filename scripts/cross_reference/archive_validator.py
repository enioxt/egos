#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Archive Validator (Version 1.0.0)

Validates files before they are archived to ensure critical reference 
implementations aren't accidentally archived.

This script should be run before any archive operation to prevent 
accidental archiving of important files.

@references:
- Reference Implementation: file_reference_checker_ultra.py
- Configuration: config_consolidated.yaml
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import datetime
import json
import logging
import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from colorama import Fore, Back, Style, init
import shutil
import time
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Banner width for consistent visual elements
BANNER_WIDTH = 80

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("archive_validator")

class ArchiveValidator:
    """
    Validates files before archiving to prevent accidental archiving of 
    important reference implementations and critical files.
    """
    
    def __init__(self, config_path: Path = None):
        """
        Initialize the Archive Validator.
        
        Args:
            config_path: Path to the configuration file. If None, will use default.
        """
        self.config_path = config_path or Path(__file__).parent / "config_consolidated.yaml"
        self.config = self._load_config()
        self.protected_files = self._get_protected_files()
        self.protected_patterns = self._get_protected_patterns()
        
        # Create a timestamp for report file naming
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def _get_protected_files(self) -> List[str]:
        """Get list of protected files from config."""
        protected_files = self.config.get('archive_validation', {}).get('protected_files', [])
        if not protected_files:
            # Default protected files if not specified in config
            protected_files = [
                "file_reference_checker_ultra.py",
                "purge_old_references.py",
                "script_standards_scanner.py",
                "cross_reference_validator.py",
                "config_loader.py",
                "optimized_reference_fixer.py"
            ]
        return protected_files
    
    def _get_protected_patterns(self) -> List[str]:
        """Get list of protected file patterns from config."""
        protected_patterns = self.config.get('archive_validation', {}).get('protected_patterns', [])
        if not protected_patterns:
            # Default protected patterns if not specified in config
            protected_patterns = [
                r"^README\.md$",
                r"^ROADMAP\.md$",
                r"^ARCHIVE_POLICY\.md$",
                r".*reference_implementation.*\.py$",
                r".*standards.*\.md$"
            ]
        return protected_patterns
        
    def display_banner(self, title: str, subtitle: str = None):
        """Display a standardized banner with title and optional subtitle."""
        print()
        sys.stdout.flush()
        
        print(f"{Fore.CYAN}╔{'═' * (BANNER_WIDTH - 2)}╗")
        print(f"║{title.center(BANNER_WIDTH - 2)}║")
        
        if subtitle:
            print(f"║{subtitle.center(BANNER_WIDTH - 2)}║")
        
        print(f"╚{'═' * (BANNER_WIDTH - 2)}╝{Style.RESET_ALL}")
        
        sys.stdout.flush()
        print()
    
    def validate_files_for_archive(self, files_to_archive: List[Path]) -> Dict[str, List[Path]]:
        """
        Validate a list of files before archiving.
        
        Args:
            files_to_archive: List of file paths to validate
            
        Returns:
            Dictionary with 'safe' and 'protected' file lists
        """
        self.display_banner(
            "Archive Validator", 
            f"Validating {len(files_to_archive)} files before archiving"
        )
        
        result = {
            'safe': [],
            'protected': []
        }
        
        print(f"{Fore.CYAN}Checking files against protection rules...{Style.RESET_ALL}")
        
        # Use tqdm for a progress bar
        for file_path in tqdm(files_to_archive, desc="Validating files"):
            file_name = file_path.name
            
            # Check if file is explicitly protected
            if file_name in self.protected_files:
                logger.warning(f"Protected file detected: {file_path}")
                result['protected'].append(file_path)
                continue
                
            # Check if file matches any protected pattern
            if any(re.match(pattern, file_name) for pattern in self.protected_patterns):
                logger.warning(f"File matches protected pattern: {file_path}")
                result['protected'].append(file_path)
                continue
                
            # Check file content for reference implementation markers
            try:
                if file_path.suffix.lower() in ['.py', '.md', '.txt']:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(5000)  # Read first 5000 chars for efficiency
                        if "reference implementation" in content.lower() or "reference script" in content.lower():
                            logger.warning(f"File contains reference implementation markers: {file_path}")
                            result['protected'].append(file_path)
                            continue
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                
            # If we got here, the file is safe to archive
            result['safe'].append(file_path)
        
        # Display summary
        print(f"\n{Fore.GREEN}✓ {len(result['safe'])} files are safe to archive")
        
        if result['protected']:
            print(f"{Fore.RED}⚠ {len(result['protected'])} protected files cannot be archived:{Style.RESET_ALL}")
            for file in result['protected'][:10]:  # Show first 10
                print(f"  - {file}")
            
            if len(result['protected']) > 10:
                print(f"  ... and {len(result['protected']) - 10} more")
                
        return result
    
    def generate_report(self, validation_result: Dict[str, List[Path]], output_dir: Path = None) -> Path:
        """
        Generate a detailed report of the validation.
        
        Args:
            validation_result: Result from validate_files_for_archive
            output_dir: Directory to save the report (default: ./reports)
            
        Returns:
            Path to the generated report
        """
        # Ensure output directory exists
        output_dir = output_dir or Path(__file__).parent / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create report file
        report_file = output_dir / f"archive_validation_{self.timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: Archive Validation Report
description: Results of validating files before archiving
created: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
author: EGOS Archive Validator
status: Generated
---

# Archive Validation Report

Report generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

- **Total files checked**: {len(validation_result['safe']) + len(validation_result['protected'])}
- **Safe to archive**: {len(validation_result['safe'])}
- **Protected (cannot archive)**: {len(validation_result['protected'])}

## Protected Files

The following files are protected and should not be archived:

""")
            
            for file in validation_result['protected']:
                f.write(f"- `{file}`\n")
                
            f.write("""
## Next Steps

If you need to archive any of the protected files:

1. Review the [Archive Policy](../../../ARCHIVE_POLICY.md)
2. Obtain documented approval for archiving reference implementations
3. Update the `protected_files` list in the configuration if necessary
4. Re-run the validation with the `--override` flag

## Protection Rules

The following files and patterns are protected:

""")
            
            f.write("### Protected Files\n\n")
            for file in self.protected_files:
                f.write(f"- `{file}`\n")
                
            f.write("\n### Protected Patterns\n\n")
            for pattern in self.protected_patterns:
                f.write(f"- `{pattern}`\n")
                
            f.write("\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
            
        logger.info(f"Generated report at {report_file}")
        return report_file
    
    def run(self, directory: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Run the archive validation on a directory.
        
        Args:
            directory: Directory containing files to validate
            recursive: Whether to scan subdirectories
            
        Returns:
            Validation results with report path
        """
        # Find files to validate
        files_to_archive = []
        
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    files_to_archive.append(Path(root) / file)
        else:
            for file in os.listdir(directory):
                file_path = directory / file
                if file_path.is_file():
                    files_to_archive.append(file_path)
        
        # Validate files
        validation_result = self.validate_files_for_archive(files_to_archive)
        
        # Generate report
        report_path = self.generate_report(validation_result)
        
        # Display conclusion
        if validation_result['protected']:
            self.display_banner(
                "⚠ Archive Validation Failed ⚠",
                f"{len(validation_result['protected'])} protected files cannot be archived"
            )
            print(f"{Fore.YELLOW}Review the report at: {report_path}{Style.RESET_ALL}")
            print()
            print(f"{Fore.CYAN}To proceed with archiving safe files only:{Style.RESET_ALL}")
            print(f"  python archive_validator.py --directory {directory} --safe-only")
            print()
        else:
            self.display_banner(
                "✓ Archive Validation Passed",
                f"All {len(validation_result['safe'])} files are safe to archive"
            )
            
        print(f"✧༺❀༻∞ EGOS ∞༺❀༻✧")
        
        return {
            'result': validation_result,
            'report': str(report_path)
        }

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Validate files before archiving")
    parser.add_argument("--directory", "-d", type=str, required=True, 
                      help="Directory containing files to validate")
    parser.add_argument("--config", "-c", type=str, default=None,
                      help="Path to configuration file")
    parser.add_argument("--recursive", "-r", action="store_true", default=True,
                      help="Scan subdirectories recursively")
    parser.add_argument("--safe-only", "-s", action="store_true", default=False,
                      help="Only display files that are safe to archive")
    
    args = parser.parse_args()
    
    config_path = Path(args.config) if args.config else None
    validator = ArchiveValidator(config_path)
    
    try:
        directory = Path(args.directory)
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            sys.exit(1)
            
        validator.run(directory, args.recursive)
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()