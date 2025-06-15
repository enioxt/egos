"""
EGOS Syntax and Import Checker
------------------------------
Scans Python files in the EGOS codebase for common syntax issues and import problems.
Identifies patterns that could lead to runtime errors and suggests fixes.

Follows EGOS principles of Conscious Modularity and Integrated Ethics.
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
from typing import List, Dict, Tuple, Optional, Set, Any
import fnmatch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("egos_syntax_checker")

class SyntaxIssue:
    """Represents a syntax issue found in a Python file.

    Attributes:
        None
            Methods:
            None
"""

    def __init__(self, file_path: str, line_number: int, issue_type: str, description: str, suggestion: str):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "issue_type": self.issue_type,
            "description": self.description,
            "suggestion": self.suggestion
        }

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number} - {self.issue_type}: {self.description}"


class SyntaxChecker:
    """Checks Python files for common syntax issues and import problems."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Common patterns to check (Temporarily disabled - high false positives - See MEMORY[403f6d5e...])
        self.patterns = {
            # "unmatched_parenthesis": r'[^\\]\)\s*\)',
            # "incomplete_assignment": r'=\s*(?:\n|$)',
            # "empty_if_block": r'if.*:\s*(?:\n\s*\n|\n\s*[^\s])',
            # "invalid_import_resilience": r'if\s+project_root\s+not\s+in\s+sys\.path:\s*\n\s*(?:\n|[^\s])',
            # "makedirs_without_path": r'os\.makedirs\(\s*\)',
            # "relative_import_in_script": r'from\s+\.\w+\s+import',
        }

    def check_file(self, file_path: str) -> List[SyntaxIssue]:
        """Check a Python file for syntax issues."""
        issues = []

        # --- EGOS Check: Ensure we only process Python files ---
        if not file_path.endswith('.py'):
            logger.debug(f"Skipping non-Python file: {file_path}")
            return issues
        # --- End EGOS Check ---

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Check for common regex patterns (Temporarily disabled - high false positives - See MEMORY[403f6d5e...])
            # for pattern_name, pattern in self.patterns.items():
            #     for match in re.finditer(pattern, content):
            #         line_number = content[:match.start()].count('\n') + 1
            #         line = lines[line_number - 1] if line_number <= len(lines) else ""
            #         
            #         issue = self._create_issue_from_pattern(file_path, line_number, pattern_name, line)
            #         if issue:
            #             issues.append(issue)

            # Try to parse with AST to catch syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(SyntaxIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    description=f"Syntax error: {str(e)}",
                    suggestion="Fix the syntax error according to the Python error message."
                ))

            # Check for import resilience pattern correctness
            if "# EGOS Import Resilience" in content:
                resilience_issues = self._check_import_resilience(file_path, content, lines)
                issues.extend(resilience_issues)

        except Exception as e:
            logger.error(f"Error checking file {file_path}: {str(e)}")
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=0,
                issue_type="file_error",
                description=f"Error processing file: {str(e)}",
                suggestion="Check file encoding and permissions."
            ))

        return issues

    @staticmethod
    def _create_issue_from_pattern(file_path: str, line_number: int, pattern_name: str, line: str) -> Optional[SyntaxIssue]:
        """Create a SyntaxIssue based on the pattern matched."""
        # (Temporarily disabled - See MEMORY[403f6d5e...])
        # if pattern_name == "unmatched_parenthesis":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="unmatched_parenthesis",
        #         description="Possible unmatched parenthesis detected.",
        #         suggestion="Check for balanced parentheses in expressions and function calls."
        #     )
        # if pattern_name == "incomplete_assignment":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="incomplete_assignment",
        #         description="Assignment without a value detected.",
        #         suggestion="Complete the assignment with a proper value."
        #     )
        # elif pattern_name == "empty_if_block":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="empty_if_block",
        #         description="If statement with empty block detected.",
        #         suggestion="Add proper indented code under the if statement or use 'pass'."
        #     )
        # elif pattern_name == "invalid_import_resilience":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="invalid_import_resilience",
        #         description="Import resilience pattern without sys.path.insert detected.",
        #         suggestion="Add 'sys.path.insert(0, project_root)' under the if statement."
        #     )
        # elif pattern_name == "makedirs_without_path":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="makedirs_without_path",
        #         description="os.makedirs() call without a path parameter detected.",
        #         suggestion="Provide a directory path to os.makedirs()."
        #     )
        # elif pattern_name == "relative_import_in_script":
        #     return SyntaxIssue(
        #         file_path=file_path,
        #         line_number=line_number,
        #         issue_type="relative_import_in_script",
        #         description="Relative import in a script that might be run directly.",
        #         suggestion="Use absolute imports with the EGOS import resilience pattern instead."
        #     )

        return None

    @staticmethod
    def _check_import_resilience(file_path: str, content: str, lines: List[str]) -> List[SyntaxIssue]:
        """Check if the import resilience pattern is correctly implemented."""
        issues = []

        # Basic pattern components to check for
        has_import_sys = "import sys" in content
        has_path_import = "from pathlib import Path" in content
        has_project_root = "project_root = " in content and "Path(__file__).resolve().parents" in content
        has_sys_path_check = "if project_root not in sys.path:" in content
        has_sys_path_insert = "sys.path.insert(0, project_root)" in content

        # Find the line numbers for context
        import_sys_line = next((i+1 for i, line in enumerate(lines) if "import sys" in line), 0)
        project_root_line = next((i+1 for i, line in enumerate(lines) if "project_root = " in line and "Path(__file__).resolve().parents" in line), 0)

        if not has_import_sys:
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=1,
                issue_type="missing_import_sys",
                description="Import resilience pattern is missing 'import sys'.",
                suggestion="Add 'import sys' at the top of the file."
            ))

        if not has_path_import:
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=import_sys_line,
                issue_type="missing_path_import",
                description="Import resilience pattern is missing 'from pathlib import Path'.",
                suggestion="Add 'from pathlib import Path' after importing sys."
            ))

        if not has_project_root:
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=import_sys_line + 1,
                issue_type="missing_project_root",
                description="Import resilience pattern is missing project_root assignment.",
                suggestion="Add 'project_root = str(Path(__file__).resolve().parents[N])' where N is the number of parent directories to the project root."
            ))

        if not has_sys_path_check:
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=project_root_line + 1 if project_root_line else import_sys_line + 2,
                issue_type="missing_sys_path_check",
                description="Import resilience pattern is missing sys.path check.",
                suggestion="Add 'if project_root not in sys.path:' after the project_root assignment."
            ))

        if not has_sys_path_insert:
            issues.append(SyntaxIssue(
                file_path=file_path,
                line_number=project_root_line + 2 if project_root_line else import_sys_line + 3,
                issue_type="missing_sys_path_insert",
                description="Import resilience pattern is missing sys.path.insert.",
                suggestion="Add '    sys.path.insert(0, project_root)' under the if statement."
            ))

        return issues


def find_python_files(root_dir: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = [
            # Standard virtual environments
            "venv", ".venv", "env", ".env", 
            # Cache and build directories
            "__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist", "*.egg-info",
            # Version control
            ".git",
            # EGOS specific exclusions
            "backups", 
            "examples",
            "reports", # Exclude the reports generated by this and other tools
            # Add other project-specific directories to exclude here
            "node_modules" # Common in projects with JS components
        ]

    python_files = []
    exclude_patterns = [re.compile(fnmatch.translate(pattern)) for pattern in exclude_dirs]

    for root, dirs, files in os.walk(root_dir):
        # Filter directories in place to prevent walking into them
        # Exclude hidden directories (starting with '.') and explicitly excluded ones
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in exclude_dirs]
        # Exclude directories matching glob patterns (like *.egg-info)
        dirs[:] = [d for d in dirs if not any(pattern.match(d) for pattern in exclude_patterns)]

        for file in files:
            # Also check if the root directory itself is excluded or hidden
            rel_root = os.path.relpath(root, root_dir)
            if rel_root != '.' and (rel_root.startswith('.') or any(part in exclude_dirs for part in Path(rel_root).parts)):
                continue # Skip files in excluded or hidden root directories

            if file.endswith('.py'):
                # Ensure the file itself isn't hidden
                if not file.startswith('.'):
                    python_files.append(os.path.join(root, file))

    return python_files


def generate_html_report(issues: List[SyntaxIssue], output_dir: str = "reports/code_health") -> str:
    """Generate an HTML report of the syntax issues found."""
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate a timestamp for the report filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"syntax_check_report_{timestamp}.html")

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
    <title>EGOS Syntax Check Report</title>
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
        <h1>EGOS Syntax Check Report</h1>
    </div>
    <div class="content">
        <div class="summary">
            <p>Found {len(issues)} potential issues in {len(issues_by_file)} files.</p>
            <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <h2>Issues by File</h2>
"""

    # Add issues grouped by file
    for file_path, file_issues in issues_by_file.items():
        relative_path = os.path.relpath(file_path, project_root)
        html_content += f"""
        <div class="file-section">
            <div class="file-path">{relative_path} ({len(file_issues)} issues)</div>
"""

        for issue in file_issues:
            html_content += f"""
            <div class="issue">
                <div class="issue-line">Line {issue.line_number}</div>
                <div class="issue-type">{issue.issue_type}</div>
                <div class="issue-description">{issue.description}</div>
                <div class="issue-suggestion">Suggestion: {issue.suggestion}</div>
            </div>
"""

        html_content += """
        </div>
"""

    # Add issue type summary
    issue_types = {}
    for issue in issues:
        if issue.issue_type not in issue_types:
            issue_types[issue.issue_type] = 0
        issue_types[issue.issue_type] += 1

    html_content += """
        <h2>Issue Types Summary</h2>
        <table>
            <tr>
                <th>Issue Type</th>
                <th>Count</th>
            </tr>
"""

    for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
        html_content += f"""
            <tr>
                <td>{issue_type}</td>
                <td>{count}</td>
            </tr>
"""

    html_content += """
        </table>

        <div class="footer">
            <p>Generated by EGOS Syntax Checker</p>
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
    parser = argparse.ArgumentParser(description="EGOS Syntax and Import Checker")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--root-dir", default=".", help="Root directory to scan.")
    parser.add_argument("--output-dir", default="reports/code_health", help="Directory to save reports.")
    args = parser.parse_args()

    # Configure logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logging.basicConfig(level=log_level, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')

    logging.info(f"Scanning Python files in {os.path.abspath(args.root_dir)}")

    # Find all Python files
    python_files = find_python_files(args.root_dir)
    logging.info(f"Found {len(python_files)} Python files to check")

    checker = SyntaxChecker(verbose=args.verbose)
    all_issues = []
    files_with_issues = 0

    for i, file_path in enumerate(python_files):
        if args.verbose or (i + 1) % 50 == 0 or i == 0 or i == len(python_files) - 1:
            logging.info(f"Checking file {i+1}/{len(python_files)}: {os.path.relpath(file_path, args.root_dir)}")

        issues = checker.check_file(file_path)
        if issues:
            files_with_issues += 1
            all_issues.extend(issues)
            if args.verbose:
                for issue in issues:
                    logging.debug(f"Found issue: {issue}")

    # Generate reports
    report_path = generate_html_report(all_issues, args.output_dir)

    if all_issues:
        logging.warning(f"Syntax check completed. Found {len(all_issues)} potential issues in {files_with_issues} files.")
        logging.warning(f"See HTML report at {os.path.relpath(report_path, args.root_dir)} for details.")
        print(f"\nSyntax check completed. Found {len(all_issues)} potential issues in {files_with_issues} files.")
        print(f"See HTML report at {os.path.relpath(report_path, args.root_dir)} for details.")
        print("Please review and fix these issues.")
        # Exit with non-zero code to signal failure for pre-commit hooks
        sys.exit(1)
    else:
        logging.info("Syntax check completed. No issues found.")
        print("Syntax check completed. No issues found.")


if __name__ == "__main__":
    main()