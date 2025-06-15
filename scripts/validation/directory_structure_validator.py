#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Directory Structure Validator

This script validates the EGOS directory structure against the canonical configuration.
It checks for required files and directories, naming conventions, and special rules.

Part of the EGOS Directory Structure Standardization Initiative.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\config\directory_structure_config.json (Canonical Structure Definition)
- C:\EGOS\ROADMAP.md#DIR-STRUCT-01 (Directory Structure Standardization Initiative)
- C:\EGOS\scripts\maintenance\directory_structure\directory_structure_manager.py (Directory Manager)
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
import re
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass
import concurrent.futures
from enum import Enum
import ast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("directory_validation.log", mode="w")
    ]
)
logger = logging.getLogger("directory_validator")

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    if not 'Fore' in globals():
        Fore = DummyColorama()
    if not 'Style' in globals():
        Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
DEFAULT_CONFIG_PATH = Path("config/directory_structure_config.json")

class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    """Class representing a directory structure validation issue"""
    path: Path
    message: str
    severity: ValidationSeverity
    rule: str
    suggestion: Optional[str] = None

class DirectoryStructureValidator:
    """
    Validates the directory structure against a canonical configuration.
    Provides detailed reporting on compliance and issues.
    """
    
    def __init__(
        self, 
        base_path: Path, 
        config_path: Path = DEFAULT_CONFIG_PATH,
        generate_report: bool = True,
        fix_issues: bool = False
    ):
        """Initialize the validator with paths and options"""
        self.base_path = base_path
        self.config_path = config_path
        self.generate_report = generate_report
        self.fix_issues = fix_issues
        self.issues: List[ValidationIssue] = []
        self.stats: Dict[str, Any] = {
            "files_scanned": 0,
            "directories_scanned": 0,
            "issues_found": 0,
            "issues_by_severity": {
                "info": 0,
                "warning": 0,
                "error": 0,
                "critical": 0
            },
            "fixed_issues": 0
        }
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the directory structure configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def validate(self) -> bool:
        """
        Validate the directory structure against the configuration.
        Returns True if validation passes with no critical issues.
        """
        logger.info(f"Starting directory structure validation for {self.base_path}")
        
        # Validate root level requirements
        self._validate_root_level()
        
        # Validate each main directory
        for dir_name, dir_config in self.config["canonical_structure"].items():
            if dir_name != "root_level" and dir_name != "special_rules":
                dir_path = self.base_path / dir_name
                self._validate_directory(dir_path, dir_config, is_root_child=True)
        
        # Apply special rules
        self._apply_special_rules()
        
        # Generate report if requested
        if self.generate_report:
            self._generate_report()
        
        # Check if validation passed (no critical issues)
        return self.stats["issues_by_severity"]["critical"] == 0
    
    def _validate_root_level(self) -> None:
        """Validate root level requirements"""
        root_config = self.config["canonical_structure"]["root_level"]
        
        # Check required files
        for required_file in root_config.get("required_files", []):
            file_path = self.base_path / required_file
            if not file_path.exists() or not file_path.is_file():
                self.issues.append(ValidationIssue(
                    path=file_path,
                    message=f"Required root file {required_file} is missing",
                    severity=ValidationSeverity.ERROR,
                    rule="required_root_file",
                    suggestion=f"Create {required_file} in the root directory"
                ))
                self.stats["issues_by_severity"]["error"] += 1
                self.stats["issues_found"] += 1
            else:
                logger.debug(f"Required root file {required_file} exists")
        
        # Check required directories
        for required_dir in root_config.get("required_directories", []):
            dir_path = self.base_path / required_dir
            if not dir_path.exists() or not dir_path.is_dir():
                self.issues.append(ValidationIssue(
                    path=dir_path,
                    message=f"Required root directory {required_dir} is missing",
                    severity=ValidationSeverity.ERROR,
                    rule="required_root_directory",
                    suggestion=f"Create {required_dir} directory in the root"
                ))
                self.stats["issues_by_severity"]["error"] += 1
                self.stats["issues_found"] += 1
            else:
                logger.debug(f"Required root directory {required_dir} exists")
    
    def _validate_directory(
        self, 
        dir_path: Path, 
        dir_config: Dict[str, Any],
        is_root_child: bool = False
    ) -> None:
        """Validate a directory against its configuration"""
        if not dir_path.exists():
            if is_root_child:  # Only report missing root child directories
                self.issues.append(ValidationIssue(
                    path=dir_path,
                    message=f"Required directory {dir_path.name} is missing",
                    severity=ValidationSeverity.ERROR,
                    rule="required_directory",
                    suggestion=f"Create {dir_path.name} directory"
                ))
                self.stats["issues_by_severity"]["error"] += 1
                self.stats["issues_found"] += 1
            return
        
        self.stats["directories_scanned"] += 1
        
        # Check required subdirectories
        for subdir in dir_config.get("required_subdirectories", []):
            subdir_path = dir_path / subdir
            if not subdir_path.exists() or not subdir_path.is_dir():
                self.issues.append(ValidationIssue(
                    path=subdir_path,
                    message=f"Required subdirectory {subdir} in {dir_path.name} is missing",
                    severity=ValidationSeverity.WARNING,
                    rule="required_subdirectory",
                    suggestion=f"Create {subdir} subdirectory in {dir_path.name}"
                ))
                self.stats["issues_by_severity"]["warning"] += 1
                self.stats["issues_found"] += 1
        
        # Check naming convention
        if "pattern" in dir_config and "naming_convention" in dir_config:
            pattern = re.compile(dir_config["pattern"])
            for item in dir_path.iterdir():
                if not pattern.match(item.name):
                    self.issues.append(ValidationIssue(
                        path=item,
                        message=f"{item.name} does not follow the {dir_config['naming_convention']} naming convention",
                        severity=ValidationSeverity.WARNING,
                        rule="naming_convention",
                        suggestion=f"Rename to follow {dir_config['naming_convention']} convention"
                    ))
                    self.stats["issues_by_severity"]["warning"] += 1
                    self.stats["issues_found"] += 1
    
    def _apply_special_rules(self) -> None:
        """Apply special rules defined in the configuration"""
        special_rules = self.config["canonical_structure"].get("special_rules", [])
        
        for rule in special_rules:
            pattern = re.compile(rule["pattern"])
            
            # Find matching files
            for root, _, files in os.walk(self.base_path):
                root_path = Path(root)
                
                # Skip .git and other hidden directories
                if any(part.startswith('.') for part in root_path.parts):
                    continue
                
                for file in files:
                    file_path = root_path / file
                    rel_path = file_path.relative_to(self.base_path)
                    
                    # Check if file matches pattern
                    if pattern.match(str(rel_path)):
                        self.stats["files_scanned"] += 1
                        
                        # Apply rule
                        if rule.get("forbidden", False):
                            self.issues.append(ValidationIssue(
                                path=file_path,
                                message=f"{file} matches forbidden pattern: {rule['description']}",
                                severity=ValidationSeverity.ERROR,
                                rule="forbidden_pattern",
                                suggestion=f"Remove or relocate {file}"
                            ))
                            self.stats["issues_by_severity"]["error"] += 1
                            self.stats["issues_found"] += 1
                        
                        # Check for docstring if required
                        if rule.get("validation") == "has_docstring":
                            if not self._check_has_docstring(file_path):
                                self.issues.append(ValidationIssue(
                                    path=file_path,
                                    message=f"{file} lacks a proper module docstring",
                                    severity=ValidationSeverity.WARNING,
                                    rule="missing_docstring",
                                    suggestion=f"Add a module docstring to {file}"
                                ))
                                self.stats["issues_by_severity"]["warning"] += 1
                                self.stats["issues_found"] += 1
    
    def _check_has_docstring(self, file_path: Path) -> bool:
        """Check if a Python file has a module-level docstring"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Parse the file
            tree = ast.parse(file_content)
            
            # Check for module docstring
            return ast.get_docstring(tree) is not None
        except Exception as e:
            logger.debug(f"Error checking docstring for {file_path}: {e}")
            return True  # Assume it's fine if we can't check
    
    def _generate_report(self) -> Path:
        """Generate a validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self.base_path / "reports" / "structure_validation"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"directory_structure_validation_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write("# EGOS Directory Structure Validation Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Base Path:** {self.base_path}\n")
            f.write(f"**Configuration:** {self.config_path}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files Scanned: {self.stats['files_scanned']}\n")
            f.write(f"- Directories Scanned: {self.stats['directories_scanned']}\n")
            f.write(f"- Issues Found: {self.stats['issues_found']}\n")
            f.write(f"  - Critical: {self.stats['issues_by_severity']['critical']}\n")
            f.write(f"  - Error: {self.stats['issues_by_severity']['error']}\n")
            f.write(f"  - Warning: {self.stats['issues_by_severity']['warning']}\n")
            f.write(f"  - Info: {self.stats['issues_by_severity']['info']}\n")
            
            if self.stats['issues_found'] > 0:
                f.write("\n## Issues\n\n")
                
                # Group issues by severity
                for severity in ValidationSeverity:
                    severity_issues = [i for i in self.issues if i.severity == severity]
                    if severity_issues:
                        f.write(f"\n### {severity.name.title()} Issues\n\n")
                        
                        for issue in severity_issues:
                            f.write(f"- **{issue.path.relative_to(self.base_path)}**\n")
                            f.write(f"  - {issue.message}\n")
                            f.write(f"  - Rule: {issue.rule}\n")
                            if issue.suggestion:
                                f.write(f"  - Suggestion: {issue.suggestion}\n")
                            f.write("\n")
            else:
                f.write("\n## No Issues Found\n\n")
                f.write("The directory structure complies with all rules defined in the configuration.\n")
            
            f.write("\n## Next Steps\n\n")
            if self.stats['issues_found'] > 0:
                f.write("1. Address the identified issues, starting with Critical and Error severity\n")
                f.write("2. Run the validator again to confirm issues are resolved\n")
            else:
                f.write("1. Continue maintaining the directory structure according to the canonical configuration\n")
                f.write("2. Run this validation regularly as part of your development workflow\n")
            
            f.write("\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated at {report_path}")
        return report_path

def print_banner(title: str, subtitle: str = None) -> None:
    """Print a formatted banner with title and optional subtitle"""
    print("\n" + "=" * BANNER_WIDTH)
    print(f"{Fore.CYAN}{title.center(BANNER_WIDTH)}{Style.RESET_ALL}")
    if subtitle:
        print(f"{subtitle.center(BANNER_WIDTH)}")
    print("=" * BANNER_WIDTH + "\n")

def main() -> None:
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="EGOS Directory Structure Validator - Verify directory structure compliance"
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(),
                      help="Base path of the EGOS project to validate")
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG_PATH),
                      help="Path to directory structure configuration file")
    parser.add_argument("--no-report", action="store_true",
                      help="Skip generating a detailed report")
    parser.add_argument("--fix", action="store_true",
                      help="Attempt to fix simple issues automatically")
    parser.add_argument("--ci", action="store_true",
                      help="Run in CI mode (exits with non-zero code on critical/error issues)")
    
    args = parser.parse_args()
    
    try:
        # Print banner
        print_banner(
            "EGOS Directory Structure Validator",
            f"Validating structure in {args.base_path}"
        )
        
        # Initialize and run validator
        validator = DirectoryStructureValidator(
            base_path=Path(args.base_path),
            config_path=Path(args.config),
            generate_report=not args.no_report,
            fix_issues=args.fix
        )
        
        valid = validator.validate()
        
        # Print summary
        print(f"\n{Fore.CYAN}Validation Summary:{Style.RESET_ALL}")
        print(f"  • Files scanned: {validator.stats['files_scanned']}")
        print(f"  • Directories scanned: {validator.stats['directories_scanned']}")
        print(f"  • Issues found: {validator.stats['issues_found']}")
        
        if validator.stats['issues_found'] > 0:
            print(f"    - {Fore.RED}Critical: {validator.stats['issues_by_severity']['critical']}{Style.RESET_ALL}")
            print(f"    - {Fore.YELLOW}Error: {validator.stats['issues_by_severity']['error']}{Style.RESET_ALL}")
            print(f"    - {Fore.CYAN}Warning: {validator.stats['issues_by_severity']['warning']}{Style.RESET_ALL}")
            print(f"    - Info: {validator.stats['issues_by_severity']['info']}")
        
        # Print result
        if valid:
            print(f"\n{Fore.GREEN}Directory structure validation passed!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}Directory structure validation failed!{Style.RESET_ALL}")
            print("Review the report for details on issues that need to be addressed.")
        
        # Exit with appropriate code in CI mode
        if args.ci and not valid:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import datetime
    main()