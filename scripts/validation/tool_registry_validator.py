#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Tool Registry Validator

This script validates the EGOS tool registry against its schema and performs additional
consistency checks such as verifying that tool paths exist. It helps maintain
the integrity of the centralized tool registry.

Part of the EGOS Tool Registry and Integration System.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\WORK_2025_05_22_tool_registry_system_plan.md (Tool Registry System Plan)
- C:\EGOS\config\tool_registry_schema.json (Tool Registry Schema)
- C:\EGOS\config\tool_registry.json (Tool Registry)
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
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import jsonschema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("tool_registry_validator")

# Constants
DEFAULT_REGISTRY_PATH = Path("config/tool_registry.json")
DEFAULT_SCHEMA_PATH = Path("config/tool_registry_schema.json")

class ToolRegistryValidator:
    """
    Validates the EGOS tool registry against its schema and performs
    additional consistency checks.
    """
    
    def __init__(
        self, 
        base_path: Path,
        registry_path: Path = DEFAULT_REGISTRY_PATH,
        schema_path: Path = DEFAULT_SCHEMA_PATH
    ):
        """Initialize the validator with paths"""
        self.base_path = base_path
        self.registry_path = base_path / registry_path
        self.schema_path = base_path / schema_path
        self.issues: List[Dict[str, Any]] = []
        self.stats = {
            "tools_validated": 0,
            "schema_issues": 0,
            "path_issues": 0,
            "dependency_issues": 0,
            "website_issues": 0,
            "tools_with_issues": 0
        }
        
    def load_registry(self) -> Dict[str, Any]:
        """Load the tool registry from the file system"""
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tool registry: {e}")
            raise
            
    def load_schema(self) -> Dict[str, Any]:
        """Load the registry schema from the file system"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise
    
    def validate_schema(self, registry: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate the registry against its JSON schema"""
        try:
            jsonschema.validate(instance=registry, schema=schema)
            logger.info("Registry successfully validated against schema")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            self.issues.append({
                "type": "schema",
                "message": str(e),
                "path": "/".join([str(p) for p in e.path]) if e.path else "root",
                "severity": "error"
            })
            self.stats["schema_issues"] += 1
            return False
    
    def validate_tool_paths(self, registry: Dict[str, Any]) -> None:
        """Validate that tool paths exist in the file system"""
        for tool in registry.get("tools", []):
            tool_path = self.base_path / tool.get("path", "")
            self.stats["tools_validated"] += 1
            
            # Check if the tool path exists
            if not tool_path.exists():
                self.issues.append({
                    "type": "path",
                    "tool_id": tool.get("id"),
                    "message": f"Tool path does not exist: {tool_path}",
                    "path": tool.get("path"),
                    "severity": "error"
                })
                self.stats["path_issues"] += 1
                self.stats["tools_with_issues"] += 1
            
            # Check dependencies
            for dependency in tool.get("dependencies", []):
                if dependency.startswith("scripts/") or dependency.startswith("config/"):
                    dep_path = self.base_path / dependency
                    if not dep_path.exists():
                        self.issues.append({
                            "type": "dependency",
                            "tool_id": tool.get("id"),
                            "message": f"Dependency does not exist: {dep_path}",
                            "path": dependency,
                            "severity": "warning"
                        })
                        self.stats["dependency_issues"] += 1
    
    def validate_website_integration(self, registry: Dict[str, Any]) -> None:
        """Validate website integration settings"""
        # This would check for issues with website integration configuration
        # For now, we'll just do basic checks
        for tool in registry.get("tools", []):
            web_integration = tool.get("website_integration", {})
            if web_integration:
                page = web_integration.get("page", "")
                if not page.startswith("/"):
                    self.issues.append({
                        "type": "website",
                        "tool_id": tool.get("id"),
                        "message": f"Website page path should start with /: {page}",
                        "path": f"tools[id={tool.get('id')}].website_integration.page",
                        "severity": "warning"
                    })
                    self.stats["website_issues"] += 1
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a report of the validation results"""
        return {
            "valid": len(self.issues) == 0,
            "stats": self.stats,
            "issues": self.issues
        }
    
    def validate(self) -> Dict[str, Any]:
        """Run all validation checks and return a report"""
        registry = self.load_registry()
        schema = self.load_schema()
        
        # Start with schema validation
        schema_valid = self.validate_schema(registry, schema)
        
        # Continue with other checks only if schema is valid
        if schema_valid:
            self.validate_tool_paths(registry)
            self.validate_website_integration(registry)
        
        return self.generate_report()

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="EGOS Tool Registry Validator - Validates the tool registry against its schema"
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(),
                      help="Base path of the EGOS project")
    parser.add_argument("--registry", type=str, default=str(DEFAULT_REGISTRY_PATH),
                      help="Path to the tool registry JSON file")
    parser.add_argument("--schema", type=str, default=str(DEFAULT_SCHEMA_PATH),
                      help="Path to the tool registry schema JSON file")
    parser.add_argument("--output", type=str,
                      help="Path to write the validation report (default: stdout)")
    parser.add_argument("--verbose", action="store_true",
                      help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Initialize and run validator
        validator = ToolRegistryValidator(
            base_path=Path(args.base_path),
            registry_path=Path(args.registry),
            schema_path=Path(args.schema)
        )
        
        report = validator.validate()
        
        # Output the report
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
        else:
            # Print a nice summary to stdout
            print("\n=== EGOS Tool Registry Validation Report ===\n")
            print(f"Tools validated: {report['stats']['tools_validated']}")
            print(f"Schema issues: {report['stats']['schema_issues']}")
            print(f"Path issues: {report['stats']['path_issues']}")
            print(f"Dependency issues: {report['stats']['dependency_issues']}")
            print(f"Website integration issues: {report['stats']['website_issues']}")
            print(f"Total tools with issues: {report['stats']['tools_with_issues']}")
            print(f"\nValidation {'PASSED' if report['valid'] else 'FAILED'}")
            
            if report['issues']:
                print("\nIssues:")
                for issue in report['issues']:
                    severity = issue['severity'].upper()
                    print(f"  {severity}: {issue['message']}")
                    if 'tool_id' in issue:
                        print(f"    Tool: {issue['tool_id']}")
                    print(f"    Path: {issue['path']}")
                    print()
        
        # Exit with appropriate code
        sys.exit(0 if report['valid'] else 1)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()