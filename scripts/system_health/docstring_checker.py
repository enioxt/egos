#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Docstring and Type Annotation Checker
-----------------------------------------
Analyzes Python files for docstring consistency and type annotation completeness.
Generates reports and suggestions for improving documentation quality.

Follows EGOS principles of Conscious Modularity, Universal Accessibility, and Integrated Ethics.
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import re
import ast
import argparse
import logging
import datetime
import json
from typing import List, Dict, Tuple, Optional, Set, Any, Union, get_type_hints

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("egos_docstring_checker")

class DocstringIssue:
    """Represents a docstring or type annotation issue found in a Python file.

    Attributes:
        None
    """

    def __init__(self, file_path: str, line_number: int, issue_type: str, 
                 element_name: str, description: str, suggestion: str):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.element_name = element_name
        self.description = description
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "issue_type": self.issue_type,
            "element_name": self.element_name,
            "description": self.description,
            "suggestion": self.suggestion
        }

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number} - {self.issue_type} in {self.element_name}: {self.description}"


class DocstringChecker:
    """Checks Python files for docstring consistency and type annotation completeness."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Define docstring templates
        self.class_docstring_template = """\"\"\"
{class_description}

{attributes_section}
{methods_section}
\"\"\""""

        self.function_docstring_template = """\"\"\"
{function_description}

{args_section}
{returns_section}
{raises_section}
\"\"\""""

        # Define regex patterns for docstring analysis
        self.args_pattern = r"Args?:"
        self.returns_pattern = r"Returns?:"
        self.raises_pattern = r"Raises?:"
        self.attributes_pattern = r"Attributes?:"
        self.methods_pattern = r"Methods?:"

    def check_file(self, file_path: str) -> List[DocstringIssue]:
        """Check a Python file for docstring and type annotation issues."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file with AST
            tree = ast.parse(content)

            # Check module docstring
            module_issues = self._check_module_docstring(file_path, tree, content)
            issues.extend(module_issues)

            # Check classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_issues = self._check_class_docstring(file_path, node, content)
                    issues.extend(class_issues)

                elif isinstance(node, ast.FunctionDef):
                    # Skip if it's a method (already checked in class)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree) if hasattr(parent, 'body') and node in parent.body):
                        function_issues = self._check_function_docstring(file_path, node, content)
                        issues.extend(function_issues)

        except Exception as e:
            logger.error(f"Error checking file {file_path}: {str(e)}")
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=0,
                issue_type="file_error",
                element_name="file",
                description=f"Error processing file: {str(e)}",
                suggestion="Check file encoding and syntax."
            ))

        return issues

    @staticmethod
    def _check_module_docstring(file_path: str, tree: ast.Module, content: str) -> List[DocstringIssue]:
        """Check if the module has a proper docstring."""
        issues = []

        # Check if module has a docstring
        if not ast.get_docstring(tree):
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=1,
                issue_type="missing_docstring",
                element_name="module",
                description="Module is missing a docstring.",
                suggestion="Add a module-level docstring describing the purpose and contents of the module."
            ))

        return issues

    def _check_class_docstring(self, file_path: str, node: ast.ClassDef, content: str) -> List[DocstringIssue]:
        """Check if a class has a proper docstring and type annotations."""
        issues = []

        # Get line number
        line_number = node.lineno

        # Check if class has a docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="missing_docstring",
                element_name=f"class {node.name}",
                description=f"Class '{node.name}' is missing a docstring.",
                suggestion="Add a class docstring describing the purpose and usage of the class."
            ))
            return issues

        # Check docstring structure
        if not re.search(self.attributes_pattern, docstring) and self._has_attributes(node):
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="incomplete_docstring",
                element_name=f"class {node.name}",
                description=f"Class '{node.name}' docstring is missing an Attributes section.",
                suggestion="Add an Attributes section to document class attributes."
            ))

        if not re.search(self.methods_pattern, docstring) and self._has_public_methods(node):
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="incomplete_docstring",
                element_name=f"class {node.name}",
                description=f"Class '{node.name}' docstring is missing a Methods section.",
                suggestion="Add a Methods section to summarize public methods."
            ))

        # Check methods
        for method in [n for n in node.body if isinstance(n, ast.FunctionDef)]:
            method_issues = self._check_function_docstring(file_path, method, content, is_method=True)
            issues.extend(method_issues)

        return issues

    def _check_function_docstring(self, file_path: str, node: ast.FunctionDef, content: str, is_method: bool = False) -> List[DocstringIssue]:
        """Check if a function has a proper docstring and type annotations."""
        issues = []

        # Skip private methods/functions (starting with _)
        if node.name.startswith('_') and node.name != '__init__':
            return issues

        # Get line number
        line_number = node.lineno

        # Element name for reporting
        element_type = "method" if is_method else "function"
        element_name = f"{element_type} {node.name}"

        # Check if function has a docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="missing_docstring",
                element_name=element_name,
                description=f"{element_type.capitalize()} '{node.name}' is missing a docstring.",
                suggestion=f"Add a {element_type} docstring describing purpose, parameters, and return value."
            ))
            return issues

        # Check docstring structure
        args = self._get_function_args(node)
        if args and not re.search(self.args_pattern, docstring):
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="incomplete_docstring",
                element_name=element_name,
                description=f"{element_type.capitalize()} '{node.name}' docstring is missing an Args section.",
                suggestion="Add an Args section to document parameters."
            ))

        # Check return annotation and docstring
        returns_value = self._has_return_value(node)
        has_returns_section = bool(re.search(self.returns_pattern, docstring))

        if returns_value and not has_returns_section:
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="incomplete_docstring",
                element_name=element_name,
                description=f"{element_type.capitalize()} '{node.name}' docstring is missing a Returns section.",
                suggestion="Add a Returns section to document the return value."
            ))

        # Check type annotations
        if not node.returns and returns_value:
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="missing_type_annotation",
                element_name=element_name,
                description=f"{element_type.capitalize()} '{node.name}' is missing a return type annotation.",
                suggestion="Add a return type annotation (-> Type)."
            ))

        # Check parameter type annotations
        for arg in args:
            if arg.annotation is None and arg.arg != 'self' and arg.arg != 'cls':
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type="missing_type_annotation",
                    element_name=element_name,
                    description=f"Parameter '{arg.arg}' is missing a type annotation.",
                    suggestion=f"Add a type annotation for parameter '{arg.arg}'."
                ))

        return issues

    @staticmethod
    def _has_attributes(node: ast.ClassDef) -> bool:
        """Check if a class has attributes."""
        for item in node.body:
            # Check for assignments in the class body
            if isinstance(item, ast.Assign):
                return True

            # Check for assignments in __init__ method
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                return True

        return False

    @staticmethod
    def _has_public_methods(node: ast.ClassDef) -> bool:
        """Check if a class has public methods."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                return True

        return False

    @staticmethod
    def _get_function_args(node: ast.FunctionDef) -> List[ast.arg]:
        """Get function arguments excluding self/cls for methods."""
        args = []

        if node.args.args:
            # Skip self/cls for methods
            start_idx = 0
            if node.args.args and node.args.args[0].arg in ('self', 'cls'):
                start_idx = 1

            args.extend(node.args.args[start_idx:])

        if node.args.kwonlyargs:
            args.extend(node.args.kwonlyargs)

        if node.args.vararg:
            args.append(node.args.vararg)

        if node.args.kwarg:
            args.append(node.args.kwarg)

        return args

    @staticmethod
    def _has_return_value(node: ast.FunctionDef) -> bool:
        """Check if a function returns a value (not None)."""
        # Check for explicit return statements
        for item in ast.walk(node):
            if isinstance(item, ast.Return) and item.value is not None:
                if not (isinstance(item.value, ast.Constant) and item.value.value is None):
                    return True

        return False


def find_python_files(root_dir: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = ["venv", ".venv", "env", ".env", "__pycache__", ".git", ".pytest_cache", ".mypy_cache"]

    python_files = []

    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def generate_html_report(issues: List[DocstringIssue], output_dir: str = "reports/code_health") -> str:
    """Generate an HTML report of the docstring and type annotation issues found."""
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate a timestamp for the report filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"docstring_check_report_{timestamp}.html")

    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        if issue.file_path not in issues_by_file:
            issues_by_file[issue.file_path] = []
        issues_by_file[issue.file_path].append(issue)

    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EGOS Docstring Check Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #4a86e8;
            color: white;
            padding: 15px 20px;
            border-radius: 5px 5px 0 0;
            margin-bottom: 0;
        }}
        .content {{
            background-color: white;
            padding: 20px;
            border-radius: 0 0 5px 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-top: 0;
        }}
        .summary {{
            font-size: 1.1em;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .file-section {{
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .file-path {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #4a86e8;
        }}
        .issue {{
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f9f9f9;
            border-left: 4px solid #e74c3c;
            border-radius: 0 4px 4px 0;
        }}
        .issue-type {{
            font-weight: bold;
            color: #e74c3c;
        }}
        .issue-element {{
            color: #2c3e50;
            font-family: monospace;
        }}
        .issue-line {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .issue-description {{
            margin: 5px 0;
        }}
        .issue-suggestion {{
            color: #27ae60;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f8f8f8;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 0.9em;
            color: #777;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EGOS Docstring Check Report</h1>
    </div>
    <div class="content">
        <div class="summary">
            <p>Found {len(issues)} potential issues in {len(issues_by_file)} files.</p>
            <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <h2>Issues by Type</h2>
        <table>
            <tr>
                <th>Issue Type</th>
                <th>Count</th>
            </tr>
"""

    # Count issues by type
    issues_by_type = {}
    for issue in issues:
        if issue.issue_type not in issues_by_type:
            issues_by_type[issue.issue_type] = 0
        issues_by_type[issue.issue_type] += 1

    # Add issue type counts to the report
    for issue_type, count in sorted(issues_by_type.items(), key=lambda x: x[1], reverse=True):
        html_content += f"""
            <tr>
                <td>{issue_type}</td>
                <td>{count}</td>
            </tr>"""

    html_content += """
        </table>

        <h2>Issues by File</h2>
"""

    # Add issues grouped by file
    for file_path, file_issues in sorted(issues_by_file.items(), key=lambda x: len(x[1]), reverse=True):
        rel_path = os.path.relpath(file_path, project_root)
        html_content += f"""
        <div class="file-section">
            <div class="file-path">{rel_path} ({len(file_issues)} issues)</div>
"""

        for issue in file_issues:
            html_content += f"""
            <div class="issue">
                <div class="issue-line">Line {issue.line_number}</div>
                <div class="issue-type">{issue.issue_type} in <span class="issue-element">{issue.element_name}</span></div>
                <div class="issue-description">{issue.description}</div>
                <div class="issue-suggestion">Suggestion: {issue.suggestion}</div>
            </div>
"""

        html_content += """
        </div>
"""

    html_content += """
        <div class="footer">
            <p>Generated by EGOS Docstring Checker</p>
        </div>
    </div>
</body>
</html>"""

    # Write HTML content to file
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Generated HTML report at {report_path}")
    return report_path


def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description="EGOS Docstring and Type Annotation Checker")
    parser.add_argument("--root-dir", default=project_root, help="Root directory to scan for Python files")
    parser.add_argument("--exclude-dirs", nargs="+", help="Directories to exclude from scanning")
    parser.add_argument("--output-dir", default="reports/docstrings", help="Directory to save the report")
    parser.add_argument("--json", help="Path to save JSON report")
    parser.add_argument("--verbose", action="store_true", help="Show detailed logs")
    parser.add_argument("--open-report", action="store_true", help="Open the HTML report in the default browser")
    parser.add_argument("--file", help="Check a specific file instead of scanning the directory")
    parser.add_argument("--no-report", action="store_true", help="Do not generate HTML/JSON reports")

    args = parser.parse_args()

    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Create checker
        checker = DocstringChecker(verbose=args.verbose)

        # Check specific file or scan directory
        if args.file:
            logger.info(f"Checking file {args.file}")
            issues = checker.check_file(args.file)
        else:
            logger.info(f"Scanning Python files in {args.root_dir}")

            # Find Python files
            python_files = find_python_files(args.root_dir, args.exclude_dirs)
            logger.info(f"Found {len(python_files)} Python files to check")

            # Check each file
            issues = []
            for i, file_path in enumerate(python_files):
                if i % 10 == 0 or args.verbose:
                    logger.info(f"Checking file {i+1}/{len(python_files)}: {file_path}")

                file_issues = checker.check_file(file_path)
                issues.extend(file_issues)

                if file_issues and args.verbose:
                    for issue in file_issues:
                        logger.debug(f"Found issue: {issue}")

        logger.info(f"Found {len(issues)} potential issues")

        # Generate reports if not suppressed
        if not args.no_report:
            output_dir = args.output_dir
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Generating reports in {output_dir}")
            if not issues:
                logger.info("No issues found, creating an empty report.")

            # Generate HTML report
            report_path = generate_html_report(issues, output_dir)

            # Save JSON report if requested
            if args.json:
                json_dir = os.path.dirname(args.json)
                if json_dir:
                    os.makedirs(json_dir, exist_ok=True)

                with open(args.json, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "total_issues": len(issues),
                        "issues": [issue.to_dict() for issue in issues]
                    }, f, indent=2)

                logger.info(f"Saved JSON report to {args.json}")

            # Open report in browser if requested
            if args.open_report:
                import webbrowser
                import subprocess
                import platform

                # Convert to absolute path with forward slashes for browser compatibility
                abs_path = os.path.abspath(report_path).replace('\\', '/')
                url = f"file:///{abs_path}"

                try:
                    # Try to open specifically with Chrome on Windows
                    if platform.system() == 'Windows':
                        # Look for Chrome in standard locations
                        chrome_paths = [
                            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
                        ]

                        chrome_path = None
                        for path in chrome_paths:
                            if os.path.exists(path):
                                chrome_path = path
                                break

                        if chrome_path:
                            subprocess.Popen([chrome_path, url])
                            logger.info(f"Opened report in Google Chrome: {url}")
                        else:
                            # Fall back to default browser if Chrome not found
                            webbrowser.open(url)
                            logger.info(f"Opened report in default browser: {url}")
                    else:
                        # For non-Windows systems
                        webbrowser.open(url)
                        logger.info(f"Opened report in default browser: {url}")
                except Exception as e:
                    logger.error(f"Error opening browser: {e}")
                    # Fall back to just showing the path
                    logger.info(f"Report saved at: {abs_path}")

            print(f"\nDocstring check completed. Found {len(issues)} potential issues.")
            print(f"Report saved to: {report_path}")

        else:
            logger.info("Report generation skipped due to --no-report flag.")
            print(f"\nDocstring check completed. Found {len(issues)} potential issues.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()