#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Naming Convention Validator

This module provides a validator for checking naming conventions across the EGOS project,
with a focus on snake_case compliance. It integrates the existing snake_case audit and
conversion tools into the unified health check framework.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.0

@references:
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
- C:\EGOS\scripts\utils\audit_snake_case.py
- C:\EGOS\scripts\utils\convert_to_snake_case.py
- C:\EGOS\docs\core_materials\standards\manual_conversion_documentation_standard.md
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
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base validator classes
try:
    from core.base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity
except ImportError:
    # Handle case when running as standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.base_validator import BaseValidator, ValidationResult, Issue, IssueSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("health_check.naming_convention")

class NamingConventionValidator(BaseValidator):
    """Validator for naming conventions including snake_case."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__("naming_convention", config)
        
        # Default configuration
        self.default_config = {
            "conventions": ["snake_case"],
            "exclusions": {
                "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
                "files": ["README.md", "LICENSE", "Makefile", "requirements.txt", ".gitignore", ".gitattributes"],
                "extensions_to_ignore": [".md", ".MD"],
                "patterns_to_ignore": [r".*\.git.*", r".*node_modules.*", r".*__pycache__.*", r".*\.vscode.*"]
            },
            "pattern_types": {
                "UPPERCASE_TO_LOWERCASE": r"^[A-Z]+$",
                "PASCALCASE_TO_SNAKE_CASE": r"^[A-Z][a-zA-Z0-9]*$",
                "CAMELCASE_TO_SNAKE_CASE": r"^[a-z]+[A-Z][a-zA-Z0-9]*$",
                "KEBABCASE_TO_SNAKE_CASE": r"^[a-z0-9]+(-[a-z0-9]+)+$",
                "SPACE_TO_SNAKE_CASE": r"^.*\s+.*$",
                "MIXED_PATTERN": r".*"
            }
        }
        
        # Merge with provided config
        self.config = self.default_config.copy()
        if config:
            self._merge_config(self.config, config)
    
    def _merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to override base
            
        Returns:
            Merged configuration
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
        return base_config
    
    def is_snake_case(self, name: str) -> bool:
        """Check if a name follows snake_case convention.
        
        Args:
            name: The name to check
            
        Returns:
            True if the name follows snake_case, False otherwise
        """
        # Remove file extension if present
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Check if name is already snake_case (all lowercase with underscores)
        snake_case_pattern = r'^[a-z0-9_]+$'
        return bool(re.match(snake_case_pattern, name))
    
    def should_exclude(self, path: Path, exclusions: Dict[str, List[str]]) -> bool:
        """Check if a path should be excluded based on exclusion rules.
        
        Args:
            path: The path to check
            exclusions: Dictionary of exclusion rules
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        # Check directory exclusions
        for part in path.parts:
            if part in exclusions.get('directories', []):
                return True
        
        # Check file exclusions
        if path.name in exclusions.get('files', []):
            return True
        
        # Check extension exclusions
        if path.suffix.lower() in exclusions.get('extensions_to_ignore', []):
            return True
        
        # Check pattern exclusions
        str_path = str(path).replace('\\', '/')
        for pattern in exclusions.get('patterns_to_ignore', []):
            try:
                if re.search(pattern, str_path):
                    return True
            except re.error:
                logger.warning(f"Invalid regex pattern: {pattern}")
        
        return False
    
    def identify_pattern_type(self, name: str) -> str:
        """Identify the pattern type of a name.
        
        Args:
            name: The name to identify
            
        Returns:
            Pattern type string
        """
        # Remove file extension if present
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Check against pattern types
        for pattern_type, regex in self.config.get('pattern_types', {}).items():
            if re.match(regex, name):
                return pattern_type
        
        return "MIXED_PATTERN"
    
    def string_to_snake_case(self, s: str) -> str:
        """Convert a string to snake_case.
        
        Args:
            s: The string to convert
            
        Returns:
            The snake_case version of the string
        """
        # Handle empty strings
        if not s:
            return s
        
        # Handle file extensions
        name_part, ext_part = os.path.splitext(s)
        
        # Replace hyphens and spaces with underscores
        s1 = re.sub(r'[-\s]+', '_', name_part)
        
        # Insert underscores between camelCase or PascalCase transitions
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        # Convert to lowercase
        s3 = s2.lower()
        
        # Remove leading/trailing underscores and collapse multiple underscores
        s4 = re.sub(r'_+', '_', s3).strip('_')
        
        # Combine with extension
        return s4 + ext_part
    
    def audit_directory(self, directory_path: Union[str, Path], exclusions: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Audit a directory for non-snake_case files and directories.
        
        Args:
            directory_path: Path to the directory to audit
            exclusions: Dictionary of exclusion rules
            
        Returns:
            List of non-compliant items with metadata
        """
        non_compliant = []
        directory_path = Path(directory_path)
        
        for root, dirs, files in os.walk(directory_path):
            root_path = Path(root)
            
            # Process directories
            for dir_name in dirs[:]:  # Copy to avoid modification during iteration
                path = root_path / dir_name
                if not self.should_exclude(path, exclusions) and not self.is_snake_case(dir_name):
                    pattern_type = self.identify_pattern_type(dir_name)
                    snake_case_name = self.string_to_snake_case(dir_name)
                    non_compliant.append({
                        'path': str(path),
                        'name': dir_name,
                        'type': 'directory',
                        'pattern_type': pattern_type,
                        'snake_case_name': snake_case_name
                    })
            
            # Process files
            for file_name in files:
                path = root_path / file_name
                if not self.should_exclude(path, exclusions) and not self.is_snake_case(file_name):
                    pattern_type = self.identify_pattern_type(file_name)
                    snake_case_name = self.string_to_snake_case(file_name)
                    non_compliant.append({
                        'path': str(path),
                        'name': file_name,
                        'type': 'file',
                        'pattern_type': pattern_type,
                        'snake_case_name': snake_case_name
                    })
        
        return non_compliant
    
    def validate(self, target_path: Union[str, Path], config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate naming conventions in the target path.
        
        Args:
            target_path: Path to validate
            config: Optional configuration to override defaults
            
        Returns:
            ValidationResult containing any issues found
        """
        # Initialize results
        results = ValidationResult(self.name)
        target_path = Path(target_path)
        
        # Merge configuration if provided
        effective_config = self.config.copy()
        if config:
            self._merge_config(effective_config, config)
        
        # Get exclusions
        exclusions = effective_config.get("exclusions", {})
        
        # Audit the directory
        logger.info(f"Auditing directory: {target_path}")
        non_compliant = self.audit_directory(target_path, exclusions)
        
        # Add issues for non-compliant items
        for item in non_compliant:
            path = item['path']
            name = item['name']
            item_type = item['type']
            pattern_type = item['pattern_type']
            snake_case_name = item['snake_case_name']
            
            # Determine severity based on item type and location
            severity = IssueSeverity.WARNING
            if item_type == 'directory':
                # Directories are more important to fix
                severity = IssueSeverity.ERROR
            
            # Generate fix suggestion
            new_path = str(Path(path).parent / snake_case_name)
            fix_suggestion = f"Rename to: {snake_case_name} (Pattern: {pattern_type})"
            
            # Add the issue
            issue = Issue(
                path=path,
                message=f"Name '{name}' does not follow snake_case convention",
                severity=severity,
                fix_suggestion=fix_suggestion
            )
            results.add_issue(issue)
        
        # Update metadata
        results.items_checked = len(non_compliant)
        results.metadata["non_compliant_count"] = len(non_compliant)
        results.metadata["pattern_types"] = {}
        
        # Count pattern types
        for item in non_compliant:
            pattern_type = item['pattern_type']
            if pattern_type in results.metadata["pattern_types"]:
                results.metadata["pattern_types"][pattern_type] += 1
            else:
                results.metadata["pattern_types"][pattern_type] = 1
        
        # Mark as complete
        results.complete()
        
        return results
    
    def fix(self, issues: List[Issue], dry_run: bool = True) -> Dict[str, Any]:
        """Fix naming convention issues.
        
        Args:
            issues: List of issues to fix
            dry_run: If True, only simulate fixes
            
        Returns:
            Dictionary with results of fix operations
        """
        fix_results = {
            "total": len(issues),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for issue in issues:
            try:
                path = issue.path
                path_obj = Path(path)
                
                if not path_obj.exists():
                    fix_results["failed"] += 1
                    fix_results["details"].append({
                        "path": path,
                        "success": False,
                        "message": "Path does not exist"
                    })
                    continue
                
                # Generate snake_case name
                name = path_obj.name
                snake_case_name = self.string_to_snake_case(name)
                new_path = path_obj.parent / snake_case_name
                
                # Check if target already exists
                if new_path.exists():
                    fix_results["failed"] += 1
                    fix_results["details"].append({
                        "path": path,
                        "success": False,
                        "message": f"Target already exists: {new_path}"
                    })
                    continue
                
                # Perform the rename
                if not dry_run:
                    try:
                        path_obj.rename(new_path)
                        success = True
                        message = f"Renamed: {path} -> {new_path}"
                    except Exception as e:
                        success = False
                        message = f"Error: {str(e)}"
                else:
                    success = True
                    message = f"Would rename: {path} -> {new_path}"
                
                # Record the result
                if success:
                    fix_results["successful"] += 1
                else:
                    fix_results["failed"] += 1
                
                fix_results["details"].append({
                    "path": path,
                    "new_path": str(new_path) if success else None,
                    "success": success,
                    "message": message
                })
            
            except Exception as e:
                logger.error(f"Error fixing issue {issue.path}: {e}")
                fix_results["failed"] += 1
                fix_results["details"].append({
                    "path": issue.path,
                    "success": False,
                    "message": f"Error: {str(e)}"
                })
        
        return fix_results

def main():
    """Main function for running the naming convention validator from the command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EGOS Naming Convention Validator")
    parser.add_argument("target_path", help="Path to validate")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Path to save the report")
    parser.add_argument("--fix", action="store_true", help="Fix naming convention issues")
    parser.add_argument("--dry-run", action="store_true", help="Only simulate fixes")
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Create validator
    validator = NamingConventionValidator(config)
    
    # Run validation
    results = validator.validate(args.target_path)
    
    # Generate report
    report = validator.generate_report(results)
    print(report)
    
    # Save report if output path provided
    if args.output:
        validator.save_report(results, args.output)
    
    # Fix issues if requested
    if args.fix:
        fix_results = validator.fix(results.issues, args.dry_run)
        print("\nFix Results:")
        print(f"Total: {fix_results['total']}")
        print(f"Successful: {fix_results['successful']}")
        print(f"Failed: {fix_results['failed']}")
    
    # Return exit code based on issues found
    return 1 if results.issues else 0

if __name__ == "__main__":
    sys.exit(main())