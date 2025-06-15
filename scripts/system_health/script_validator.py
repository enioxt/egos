#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Script Validator

This script performs static analysis on Python scripts in the EGOS ecosystem without
executing them. It validates structure, dependencies, documentation, and compliance
with EGOS Script Management Best Practices.

Part of the EGOS Code Quality Initiative.

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md
- C:\EGOS\scripts\system_monitor\egos_system_monitor.py
- C:\EGOS\scripts\cross_reference\cross_reference_validator.py

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0
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
import ast
import re
import json
import logging
import argparse
import importlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "script_validator.log")
    ]
)
logger = logging.getLogger("script_validator")

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ScriptValidator:
    """
    Validates Python scripts without executing them.
    
    This class analyzes Python scripts to ensure they meet EGOS standards,
    have proper documentation, and follow best practices.
    """
    
    def __init__(self, root_path: Path, exclude_dirs: List[str] = None, recursive: bool = True):
        """
        Initialize the script validator.
        
        Args:
            root_path: Base directory to search for scripts
            exclude_dirs: Directories to exclude from validation
            recursive: Whether to search recursively
        """
        self.root_path = root_path
        self.exclude_dirs = exclude_dirs or ["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"]
        self.recursive = recursive
        self.results = {
            "valid_scripts": [],
            "invalid_scripts": [],
            "scripts_missing_docstring": [],
            "scripts_missing_references": [],
            "scripts_with_import_errors": [],
            "scripts_missing_type_hints": [],
            "scripts_with_standards_issues": []
        }
        self.statistics = {
            "total_scripts": 0,
            "total_valid": 0,
            "total_invalid": 0,
            "total_lines": 0,
            "issues_by_type": {},
            "subsystems": {}
        }
        
        # Required docstring elements
        self.required_docstring_elements = [
            "Author",
            "Created",
            "Version"
        ]
        
        # Common standard libraries to ignore in import validation
        self.standard_libraries = set([
            "os", "sys", "re", "json", "csv", "time", "datetime", "logging", 
            "argparse", "pathlib", "typing", "collections", "itertools", 
            "functools", "math", "random", "shutil", "tempfile", "subprocess",
            "unittest", "pytest", "importlib", "inspect", "ast"
        ])
        
    def find_python_scripts(self) -> List[Path]:
        """
        Find all Python scripts in the specified directory.
        
        Returns:
            List of paths to Python script files
        """
        python_files = []
        
        if self.recursive:
            for root, dirs, files in os.walk(self.root_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(Path(root) / file)
        else:
            python_files = [f for f in self.root_path.glob('*.py')]
        
        logger.info(f"Found {len(python_files)} Python scripts to validate")
        return python_files
    
    def validate_script_syntax(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate the syntax of a Python script without executing it.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "path": str(file_path),
            "valid_syntax": False,
            "error": None,
            # Remove AST from result as it's not JSON serializable
            "line_count": 0,
            "has_docstring": False,
            "has_type_hints": False,
            "references": [],
            "imports": [],
            "classes": [],
            "functions": [],
            "issues": []
        }
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count lines
            result["line_count"] = len(content.splitlines())
            self.statistics["total_lines"] += result["line_count"]
            
            # Parse AST
            tree = ast.parse(content)
            # Don't store the AST in results (not JSON serializable)
            result["valid_syntax"] = True
            
            # Extract module docstring
            if ast.get_docstring(tree):
                result["has_docstring"] = True
                result["docstring"] = ast.get_docstring(tree)
                
                # Check for references
                references = self.extract_references(result["docstring"])
                if references:
                    result["references"] = references
                else:
                    result["issues"].append("Missing cross-references in docstring")
                    self.results["scripts_missing_references"].append(str(file_path))
                
                # Check for required docstring elements
                for element in self.required_docstring_elements:
                    if not re.search(rf"{element}:\s*\w+", result["docstring"], re.IGNORECASE):
                        result["issues"].append(f"Missing {element} in docstring")
            else:
                result["issues"].append("Missing module docstring")
                self.results["scripts_missing_docstring"].append(str(file_path))
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["imports"].append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result["imports"].append(node.module)
            
            # Check for type hints
            result["has_type_hints"] = self.check_type_hints(tree)
            if not result["has_type_hints"]:
                result["issues"].append("Missing type hints")
                self.results["scripts_missing_type_hints"].append(str(file_path))
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "has_docstring": bool(ast.get_docstring(node)),
                        "methods": []
                    }
                    
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            method_info = {
                                "name": child.name,
                                "has_docstring": bool(ast.get_docstring(child)),
                                "has_type_hints": self.check_function_type_hints(child)
                            }
                            class_info["methods"].append(method_info)
                    
                    result["classes"].append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and node.parent_field != 'body':
                    func_info = {
                        "name": node.name,
                        "has_docstring": bool(ast.get_docstring(node)),
                        "has_type_hints": self.check_function_type_hints(node)
                    }
                    result["functions"].append(func_info)
            
        except SyntaxError as e:
            result["error"] = f"Syntax error: {str(e)}"
            result["issues"].append(f"Syntax error: {str(e)}")
            logger.error(f"Syntax error in {file_path}: {str(e)}")
        except Exception as e:
            result["error"] = f"Error analyzing script: {str(e)}"
            result["issues"].append(f"Error: {str(e)}")
            logger.error(f"Error analyzing {file_path}: {str(e)}")
        
        # Update statistics
        self.statistics["total_scripts"] += 1
        if result["valid_syntax"] and not result["issues"]:
            self.statistics["total_valid"] += 1
            self.results["valid_scripts"].append(str(file_path))
        else:
            self.statistics["total_invalid"] += 1
            self.results["invalid_scripts"].append(str(file_path))
            
            # Track issues by type
            for issue in result["issues"]:
                issue_type = issue.split(":")[0]
                self.statistics["issues_by_type"][issue_type] = self.statistics["issues_by_type"].get(issue_type, 0) + 1
        
        # Track by subsystem
        subsystem = self.determine_subsystem(file_path)
        if subsystem not in self.statistics["subsystems"]:
            self.statistics["subsystems"][subsystem] = {
                "valid": 0,
                "invalid": 0,
                "total": 0
            }
        
        self.statistics["subsystems"][subsystem]["total"] += 1
        if result["valid_syntax"] and not result["issues"]:
            self.statistics["subsystems"][subsystem]["valid"] += 1
        else:
            self.statistics["subsystems"][subsystem]["invalid"] += 1
        
        return result
    
    def extract_references(self, docstring: str) -> List[str]:
        """
        Extract cross-references from a docstring.
        
        Args:
            docstring: The docstring to extract references from
            
        Returns:
            List of reference strings
        """
        references = []
        
        # Match @references: followed by a list
        ref_match = re.search(r'@references:(.+?)(?=\n\n|\Z)', docstring, re.DOTALL)
        if ref_match:
            ref_text = ref_match.group(1).strip()
            
            # Handle bullet point format
            if '-' in ref_text:
                refs = re.findall(r'-\s*(.+?)(?=\n-|\Z)', ref_text + '\n', re.DOTALL)
                references.extend([r.strip() for r in refs if r.strip()])
            else:
                # Handle comma-separated format
                refs = ref_text.split(',')
                references.extend([r.strip() for r in refs if r.strip()])
        
        return references
    
    def check_type_hints(self, tree: ast.AST) -> bool:
        """
        Check if a script uses type hints.
        
        Args:
            tree: AST of the script
            
        Returns:
            True if type hints are used, False otherwise
        """
        has_type_hints = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self.check_function_type_hints(node):
                    has_type_hints = True
                    break
        
        return has_type_hints
    
    def check_function_type_hints(self, func_node: ast.FunctionDef) -> bool:
        """
        Check if a function uses type hints.
        
        Args:
            func_node: AST node for the function
            
        Returns:
            True if the function uses type hints, False otherwise
        """
        # Check return type annotation
        if func_node.returns:
            return True
        
        # Check argument type annotations
        for arg in func_node.args.args:
            if arg.annotation:
                return True
        
        return False
    
    def determine_subsystem(self, file_path: Path) -> str:
        """
        Determine which subsystem a file belongs to.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Name of the subsystem
        """
        rel_path = file_path.relative_to(self.root_path.parent)
        parts = rel_path.parts
        
        if len(parts) < 2:
            return "root"
        
        if parts[0] == "scripts":
            if len(parts) < 3:
                return parts[1]
            else:
                return f"{parts[1]}/{parts[2]}"
        elif parts[0] == "subsystems":
            return parts[1]
        else:
            return parts[0]
    
    def validate_scripts(self) -> Dict[str, Any]:
        """
        Validate all Python scripts in the specified directory.
        
        Returns:
            Dictionary with validation results and statistics
        """
        scripts = self.find_python_scripts()
        script_results = []
        
        for script in scripts:
            logger.info(f"Validating {script}")
            result = self.validate_script_syntax(script)
            script_results.append(result)
        
        # Calculate statistics
        if self.statistics["total_scripts"] > 0:
            valid_percentage = (self.statistics["total_valid"] / self.statistics["total_scripts"]) * 100
            self.statistics["valid_percentage"] = round(valid_percentage, 2)
        else:
            self.statistics["valid_percentage"] = 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "script_results": script_results,
            "statistics": self.statistics,
            "results": self.results
        }
    
    def generate_report(self, validation_results: Dict[str, Any], output_format: str = "markdown") -> str:
        """
        Generate a report from validation results.
        
        Args:
            validation_results: Results from validate_scripts()
            output_format: Format of the report (markdown, json)
            
        Returns:
            Report as a string
        """
        if output_format == "json":
            # Create a JSON-serializable copy of the validation results
            serializable_results = self._make_json_serializable(validation_results)
            return json.dumps(serializable_results, indent=2)
            
    def _make_json_serializable(self, obj):
        """Convert any non-serializable objects to serializable formats."""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, Path):
            return str(obj)
        else:
            # Convert any other types to string representation
            return str(obj)
        
        # Generate Markdown report
        report = []
        report.append("# EGOS Script Validation Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nRoot Directory: `{validation_results['root_path']}`")
        
        # Add statistics
        stats = validation_results["statistics"]
        report.append("\n## Summary Statistics")
        report.append(f"\n- **Total Scripts**: {stats['total_scripts']}")
        report.append(f"- **Valid Scripts**: {stats['total_valid']} ({stats['valid_percentage']}%)")
        report.append(f"- **Invalid Scripts**: {stats['total_invalid']}")
        report.append(f"- **Total Lines**: {stats['total_lines']}")
        
        # Add issues by type
        if stats["issues_by_type"]:
            report.append("\n## Issues by Type")
            for issue_type, count in sorted(stats["issues_by_type"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"\n- **{issue_type}**: {count}")
        
        # Add subsystem statistics
        report.append("\n## Subsystem Statistics")
        for subsystem, sub_stats in sorted(stats["subsystems"].items()):
            report.append(f"\n### {subsystem}")
            report.append(f"- **Total Scripts**: {sub_stats['total']}")
            report.append(f"- **Valid Scripts**: {sub_stats['valid']}")
            report.append(f"- **Invalid Scripts**: {sub_stats['invalid']}")
            valid_percent = 0 if sub_stats['total'] == 0 else round((sub_stats['valid'] / sub_stats['total']) * 100, 2)
            report.append(f"- **Valid Percentage**: {valid_percent}%")
        
        # Add invalid scripts
        if validation_results["results"]["invalid_scripts"]:
            report.append("\n## Invalid Scripts")
            for script in validation_results["results"]["invalid_scripts"]:
                report.append(f"\n- `{script}`")
        
        # Add scripts missing docstrings
        if validation_results["results"]["scripts_missing_docstring"]:
            report.append("\n## Scripts Missing Docstrings")
            for script in validation_results["results"]["scripts_missing_docstring"]:
                report.append(f"\n- `{script}`")
        
        # Add scripts missing references
        if validation_results["results"]["scripts_missing_references"]:
            report.append("\n## Scripts Missing References")
            for script in validation_results["results"]["scripts_missing_references"]:
                report.append(f"\n- `{script}`")
        
        # Add scripts missing type hints
        if validation_results["results"]["scripts_missing_type_hints"]:
            report.append("\n## Scripts Missing Type Hints")
            for script in validation_results["results"]["scripts_missing_type_hints"]:
                report.append(f"\n- `{script}`")
        
        return "\n".join(report)
    
    def save_report(self, report: str, output_path: Path, output_format: str = "markdown"):
        """
        Save a report to a file.
        
        Args:
            report: Report content
            output_path: Path to save the report
            output_format: Format of the report (markdown, json)
        """
        extension = "md" if output_format == "markdown" else "json"
        output_file = output_path / f"script_validation_report.{extension}"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to {output_file}")
        return output_file


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EGOS Script Validator')
    parser.add_argument('--root', type=str, default='C:\\EGOS\\scripts',
                        help='Root directory to validate scripts in')
    parser.add_argument('--output', type=str, default='C:\\EGOS\\docs\\reports',
                        help='Output directory for reports')
    parser.add_argument('--format', type=str, choices=['markdown', 'json'], default='markdown',
                        help='Output format for the report')
    parser.add_argument('--exclude', type=str, nargs='+',
                        default=["venv", ".venv", "__pycache__", "node_modules", ".git", ".vs"],
                        help='Directories to exclude from validation')
    parser.add_argument('--non-recursive', action='store_true',
                        help='Do not search directories recursively')
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    root_path = Path(args.root)
    output_path = Path(args.output)
    
    if not root_path.exists():
        logger.error(f"Root directory {root_path} does not exist")
        sys.exit(1)
    
    if not output_path.exists():
        logger.info(f"Creating output directory {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Validating scripts in {root_path}")
    
    # Create validator
    validator = ScriptValidator(
        root_path=root_path,
        exclude_dirs=args.exclude,
        recursive=not args.non_recursive
    )
    
    # Run validation
    validation_results = validator.validate_scripts()
    
    # Generate and save report
    report = validator.generate_report(validation_results, args.format)
    output_file = validator.save_report(report, output_path, args.format)
    
    # Print summary
    stats = validation_results["statistics"]
    print(f"\n{Colors.HEADER}EGOS Script Validation Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}Total Scripts:{Colors.ENDC} {stats['total_scripts']}")
    print(f"{Colors.BOLD}Valid Scripts:{Colors.ENDC} {Colors.GREEN}{stats['total_valid']} ({stats['valid_percentage']}%){Colors.ENDC}")
    print(f"{Colors.BOLD}Invalid Scripts:{Colors.ENDC} {Colors.WARNING if stats['total_invalid'] > 0 else ''}{stats['total_invalid']}{Colors.ENDC}")
    print(f"{Colors.BOLD}Report saved to:{Colors.ENDC} {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())