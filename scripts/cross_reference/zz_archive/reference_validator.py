#!/usr/bin/env python3
"""Reference Validator for File Reference Checker Ultra

This module provides validation functionality for cross-references against
the canonical EGOS cross-reference standards.

@references: <!-- TO_BE_REPLACED -->, <!-- TO_BE_REPLACED -->, Cross-reference validation implementation
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - subsystems/AutoCrossRef/CROSSREF_STANDARD.md

import re
import os
import logging
import yaml
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger("reference_validator")

class ReferenceValidator:
    """
    Validates cross-references against the canonical EGOS cross-reference standards.
    
    This class provides methods for validating references in various file types,
    checking reference IDs against a registry, and generating validation reports.
    """
    
    # Reference ID pattern: EGOS-[TYPE]-[SUBSYSTEM]-[NUMBER]
    REFERENCE_ID_PATTERN = re.compile(r'EGOS-([A-Z]+)-([A-Z]+)-(\d+)')
    
    # Inline reference pattern: @references: [REFERENCE-ID-1], [REFERENCE-ID-2], [DESCRIPTION]
    INLINE_REFERENCE_PATTERN = re.compile(r'@references:\s*((?:EGOS-[A-Z]+-[A-Z]+-\d+(?:,\s*)?)+)(?:,\s*(.+))?')
    
    # Valid reference types
    VALID_TYPES = {
        'EPIC', 'FEAT', 'TASK', 'DOC', 'STD', 'MOD', 'BUG', 'TEST', 'CONFIG'
    }
    
    # Valid subsystems
    VALID_SUBSYSTEMS = {
        'ETHIK', 'KOIOS', 'NEXUS', 'ATLAS', 'HARMONY', 'MYCELIUM', 
        'CORUJA', 'CRONOS', 'XREF', 'SYSTEM'
    }
    
    def __init__(
        self, 
        registry_path: Optional[str] = None,
        strict_mode: bool = False
    ):
        """
        Initialize the Reference Validator.
        
        Args:
            registry_path: Path to the reference registry file
            strict_mode: Whether to enforce strict validation (fail on any error)
        """
        self.registry_path = registry_path
        self.strict_mode = strict_mode
        self.registry = self._load_registry() if registry_path else {}
        self.validation_results = []
        logger.info(f"Reference Validator initialized with strict_mode={strict_mode}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """
        Load the reference registry from file.
        
        Returns:
            Dictionary containing the reference registry
        """
        if not self.registry_path or not os.path.exists(self.registry_path):
            logger.warning(f"Registry file not found: {self.registry_path}")
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                registry = yaml.safe_load(f)
            
            logger.info(f"Loaded reference registry with {len(registry.get('references', []))} references")
            return registry
        except Exception as e:
            logger.error(f"Error loading registry: {str(e)}")
            return {}
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate all references in a file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Validation result dictionary
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                "file": file_path,
                "valid": False,
                "errors": ["File not found"],
                "warnings": [],
                "references": []
            }
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Initialize validation result
        result = {
            "file": file_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "references": []
        }
        
        try:
            # Validate based on file type
            if file_ext == '.py':
                self._validate_python_file(file_path, result)
            elif file_ext == '.md':
                self._validate_markdown_file(file_path, result)
            elif file_ext in ['.yaml', '.yml']:
                self._validate_yaml_file(file_path, result)
            else:
                self._validate_generic_file(file_path, result)
            
            # Set overall validity
            result["valid"] = len(result["errors"]) == 0
            
            # Add to validation results
            self.validation_results.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {str(e)}")
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
            self.validation_results.append(result)
            return result
    
    def _validate_python_file(self, file_path: str, result: Dict[str, Any]) -> None:
        """
        Validate references in a Python file.
        
        Args:
            file_path: Path to the Python file
            result: Validation result dictionary to update
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if not docstring_match:
                result["warnings"].append("No module docstring found")
                return
            
            docstring = docstring_match.group(1)
            
            # Check for references in docstring
            reference_match = self.INLINE_REFERENCE_PATTERN.search(docstring)
            if not reference_match:
                result["warnings"].append("No references found in module docstring")
                return
            
            # Extract and validate references
            reference_ids = reference_match.group(1).split(',')
            reference_ids = [ref_id.strip() for ref_id in reference_ids]
            
            for ref_id in reference_ids:
                ref_result = self._validate_reference_id(ref_id)
                result["references"].append({
                    "id": ref_id,
                    "valid": ref_result["valid"],
                    "errors": ref_result["errors"],
                    "warnings": ref_result["warnings"]
                })
                
                if not ref_result["valid"]:
                    if self.strict_mode:
                        result["errors"].extend(ref_result["errors"])
                    else:
                        result["warnings"].extend(ref_result["errors"])
            
        except Exception as e:
            logger.error(f"Error validating Python file {file_path}: {str(e)}")
            result["errors"].append(f"Validation error: {str(e)}")
    
    def _validate_markdown_file(self, file_path: str, result: Dict[str, Any]) -> None:
        """
        Validate references in a Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            result: Validation result dictionary to update
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                
                # Parse frontmatter
                try:
                    frontmatter_data = yaml.safe_load(frontmatter)
                    
                    # Check for references in frontmatter
                    if 'references' in frontmatter_data:
                        references = frontmatter_data['references']
                        if isinstance(references, list):
                            for ref_id in references:
                                ref_result = self._validate_reference_id(ref_id)
                                result["references"].append({
                                    "id": ref_id,
                                    "valid": ref_result["valid"],
                                    "errors": ref_result["errors"],
                                    "warnings": ref_result["warnings"],
                                    "location": "frontmatter"
                                })
                                
                                if not ref_result["valid"]:
                                    if self.strict_mode:
                                        result["errors"].extend(ref_result["errors"])
                                    else:
                                        result["warnings"].extend(ref_result["errors"])
                        else:
                            result["warnings"].append("Frontmatter 'references' is not a list")
                    else:
                        result["warnings"].append("No 'references' field found in frontmatter")
                        
                except Exception as e:
                    result["warnings"].append(f"Error parsing frontmatter: {str(e)}")
            else:
                result["warnings"].append("No frontmatter found")
            
            # Check for inline references
            inline_references = self.INLINE_REFERENCE_PATTERN.findall(content)
            if inline_references:
                for ref_match in inline_references:
                    ref_ids = ref_match[0].split(',')
                    ref_ids = [ref_id.strip() for ref_id in ref_ids]
                    
                    for ref_id in ref_ids:
                        # Skip if already validated in frontmatter
                        if any(r.get("id") == ref_id and r.get("location") == "frontmatter" 
                               for r in result["references"]):
                            continue
                        
                        ref_result = self._validate_reference_id(ref_id)
                        result["references"].append({
                            "id": ref_id,
                            "valid": ref_result["valid"],
                            "errors": ref_result["errors"],
                            "warnings": ref_result["warnings"],
                            "location": "inline"
                        })
                        
                        if not ref_result["valid"]:
                            if self.strict_mode:
                                result["errors"].extend(ref_result["errors"])
                            else:
                                result["warnings"].extend(ref_result["errors"])
            else:
                result["warnings"].append("No inline references found")
                
        except Exception as e:
            logger.error(f"Error validating Markdown file {file_path}: {str(e)}")
            result["errors"].append(f"Validation error: {str(e)}")
    
    def _validate_yaml_file(self, file_path: str, result: Dict[str, Any]) -> None:
        """
        Validate references in a YAML file.
        
        Args:
            file_path: Path to the YAML file
            result: Validation result dictionary to update
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for reference comments
            comment_lines = re.findall(r'^\s*#\s*(.+)$', content, re.MULTILINE)
            
            found_references = False
            for line in comment_lines:
                reference_match = self.INLINE_REFERENCE_PATTERN.search(line)
                if reference_match:
                    found_references = True
                    ref_ids = reference_match.group(1).split(',')
                    ref_ids = [ref_id.strip() for ref_id in ref_ids]
                    
                    for ref_id in ref_ids:
                        ref_result = self._validate_reference_id(ref_id)
                        result["references"].append({
                            "id": ref_id,
                            "valid": ref_result["valid"],
                            "errors": ref_result["errors"],
                            "warnings": ref_result["warnings"]
                        })
                        
                        if not ref_result["valid"]:
                            if self.strict_mode:
                                result["errors"].extend(ref_result["errors"])
                            else:
                                result["warnings"].extend(ref_result["errors"])
            
            if not found_references:
                result["warnings"].append("No references found in YAML comments")
                
        except Exception as e:
            logger.error(f"Error validating YAML file {file_path}: {str(e)}")
            result["errors"].append(f"Validation error: {str(e)}")
    
    def _validate_generic_file(self, file_path: str, result: Dict[str, Any]) -> None:
        """
        Validate references in a generic file.
        
        Args:
            file_path: Path to the file
            result: Validation result dictionary to update
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for inline references
            inline_references = self.INLINE_REFERENCE_PATTERN.findall(content)
            if inline_references:
                for ref_match in inline_references:
                    ref_ids = ref_match[0].split(',')
                    ref_ids = [ref_id.strip() for ref_id in ref_ids]
                    
                    for ref_id in ref_ids:
                        ref_result = self._validate_reference_id(ref_id)
                        result["references"].append({
                            "id": ref_id,
                            "valid": ref_result["valid"],
                            "errors": ref_result["errors"],
                            "warnings": ref_result["warnings"]
                        })
                        
                        if not ref_result["valid"]:
                            if self.strict_mode:
                                result["errors"].extend(ref_result["errors"])
                            else:
                                result["warnings"].extend(ref_result["errors"])
            else:
                result["warnings"].append("No references found")
                
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {str(e)}")
            result["errors"].append(f"Validation error: {str(e)}")
    
    def _validate_reference_id(self, reference_id: str) -> Dict[str, Any]:
        """
        Validate a reference ID against the canonical format.
        
        Args:
            reference_id: Reference ID to validate
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check format
        match = self.REFERENCE_ID_PATTERN.match(reference_id)
        if not match:
            result["valid"] = False
            result["errors"].append(f"Invalid reference ID format: {reference_id}")
            return result
        
        # Extract components
        ref_type, subsystem, number = match.groups()
        
        # Validate type
        if ref_type not in self.VALID_TYPES:
            result["valid"] = False
            result["errors"].append(f"Invalid reference type: {ref_type}")
        
        # Validate subsystem
        if subsystem not in self.VALID_SUBSYSTEMS:
            result["valid"] = False
            result["errors"].append(f"Invalid subsystem: {subsystem}")
        
        # Validate number format
        try:
            num = int(number)
            if num <= 0:
                result["valid"] = False
                result["errors"].append(f"Invalid reference number: {number}")
        except ValueError:
            result["valid"] = False
            result["errors"].append(f"Invalid reference number: {number}")
        
        # Check against registry if available
        if self.registry and 'references' in self.registry:
            if reference_id not in [ref.get('id') for ref in self.registry['references']]:
                result["warnings"].append(f"Reference ID not found in registry: {reference_id}")
        
        return result
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a validation report.
        
        Args:
            output_path: Path to save the report (optional)
            
        Returns:
            Report dictionary
        """
        # Compile report data
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.validation_results),
            "valid_files": sum(1 for r in self.validation_results if r["valid"]),
            "invalid_files": sum(1 for r in self.validation_results if not r["valid"]),
            "total_references": sum(len(r["references"]) for r in self.validation_results),
            "valid_references": sum(sum(1 for ref in r["references"] if ref["valid"]) 
                                  for r in self.validation_results),
            "invalid_references": sum(sum(1 for ref in r["references"] if not ref["valid"]) 
                                    for r in self.validation_results),
            "errors": sum(len(r["errors"]) for r in self.validation_results),
            "warnings": sum(len(r["warnings"]) for r in self.validation_results),
            "results": self.validation_results
        }
        
        # Save report if output path provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    yaml.dump(report, f, default_flow_style=False)
                logger.info(f"Validation report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving validation report: {str(e)}")
        
        return report
    
    def validate_directory(
        self, 
        directory_path: str, 
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate all files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to recursively validate subdirectories
            file_extensions: List of file extensions to validate (e.g., ['.py', '.md'])
            
        Returns:
            Validation report dictionary
        """
        if not os.path.isdir(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return {
                "valid": False,
                "errors": [f"Directory not found: {directory_path}"],
                "warnings": [],
                "results": []
            }
        
        # Default to common file types if not specified
        if file_extensions is None:
            file_extensions = ['.py', '.md', '.yaml', '.yml', '.txt']
        
        # Find files to validate
        files_to_validate = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        files_to_validate.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                if os.path.isfile(os.path.join(directory_path, file)) and \
                   any(file.endswith(ext) for ext in file_extensions):
                    files_to_validate.append(os.path.join(directory_path, file))
        
        # Validate each file
        for file_path in files_to_validate:
            self.validate_file(file_path)
        
        # Generate report
        return self.generate_report()


if __name__ == "__main__":
    import argparse
    
    # Configure argument parser
    parser = argparse.ArgumentParser(description="Validate cross-references against EGOS standards")
    parser.add_argument("--path", type=str, required=True, help="File or directory to validate")
    parser.add_argument("--registry", type=str, help="Path to reference registry file")
    parser.add_argument("--output", type=str, help="Path to save validation report")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation mode")
    parser.add_argument("--recursive", action="store_true", help="Recursively validate directories")
    parser.add_argument("--extensions", type=str, help="Comma-separated list of file extensions to validate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize validator
    validator = ReferenceValidator(
        registry_path=args.registry,
        strict_mode=args.strict
    )
    
    # Validate path
    if os.path.isfile(args.path):
        result = validator.validate_file(args.path)
        report = validator.generate_report(args.output)
    elif os.path.isdir(args.path):
        extensions = args.extensions.split(',') if args.extensions else None
        report = validator.validate_directory(
            args.path,
            recursive=args.recursive,
            file_extensions=extensions
        )
    else:
        logger.error(f"Path not found: {args.path}")
        exit(1)
    
    # Print summary
    print(f"Validation Summary:")
    print(f"  Total Files: {report['total_files']}")
    print(f"  Valid Files: {report['valid_files']}")
    print(f"  Invalid Files: {report['invalid_files']}")
    print(f"  Total References: {report['total_references']}")
    print(f"  Valid References: {report['valid_references']}")
    print(f"  Invalid References: {report['invalid_references']}")
    print(f"  Errors: {report['errors']}")
    print(f"  Warnings: {report['warnings']}")
    
    if args.output:
        print(f"Full report saved to: {args.output}")
    
    # Exit with appropriate status code
    exit(0 if report['invalid_files'] == 0 else 1)
