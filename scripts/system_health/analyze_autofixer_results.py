#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EGOS Docstring Autofixer Results Analyzer
-----------------------------------------
Analyzes files modified by docstring_autofixer.py to identify potential issues.

This script helps with the manual review process by identifying common problems:
1. Misplaced shebangs (should be at the top, before docstrings)
2. Duplicate docstrings (placeholder + actual docstring)
3. Other structural issues that may need manual correction

Follows EGOS principles of Conscious Modularity, Systemic Cartography, and Sacred Privacy.
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
import argparse
import logging
import json
from typing import List, Dict, Any, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("egos_autofixer_analyzer")

class AutofixerIssue:
    """Represents an issue found in files modified by the docstring_autofixer.

    Attributes:
        file_path: Path to the file with the issue.
        issue_type: Type of issue (e.g., 'misplaced_shebang', 'duplicate_docstring').
        description: Detailed description of the issue.
        line_numbers: List of line numbers relevant to the issue.
        suggestion: Suggested fix for the issue.
    """

    def __init__(self, file_path: str, issue_type: str, description: str, 
                 line_numbers: List[int], suggestion: str):
        self.file_path = file_path
        self.issue_type = issue_type
        self.description = description
        self.line_numbers = line_numbers
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "issue_type": self.issue_type,
            "description": self.description,
            "line_numbers": self.line_numbers,
            "suggestion": self.suggestion
        }

    def __str__(self) -> str:
        return f"{self.file_path} - {self.issue_type}: {self.description}"


def find_modified_files(git_status_output: str) -> List[str]:
    """Extract modified file paths from git status output.

    Args:
        git_status_output: Output from 'git status --porcelain'

    Returns:
        List of modified file paths
    """
    modified_files = []
    for line in git_status_output.splitlines():
        if line.strip() and line[0:2] in [' M', 'M ', 'MM']:
            # Extract the file path (after the status code)
            file_path = line[3:].strip()
            if file_path.endswith('.py'):
                modified_files.append(file_path)
    return modified_files


def check_for_misplaced_shebang(file_path: str, content: List[str]) -> List[AutofixerIssue]:
    """Check if a file has a misplaced shebang (not at the top).

    Args:
        file_path: Path to the file to check
        content: List of lines in the file

    Returns:
        List of AutofixerIssue objects if issues found, empty list otherwise
    """
    issues = []

    # Find shebang lines
    shebang_pattern = re.compile(r'^#!.*python')
    shebang_lines = []

    for i, line in enumerate(content):
        if shebang_pattern.match(line):
            shebang_lines.append(i)

    # If there's a shebang but it's not at line 0
    if shebang_lines and shebang_lines[0] > 0:
        issues.append(AutofixerIssue(
            file_path=file_path,
            issue_type="misplaced_shebang",
            description=f"Shebang found at line {shebang_lines[0]}, should be at line 0",
            line_numbers=shebang_lines,
            suggestion="Move the shebang to the first line of the file, before any docstrings"
        ))

    return issues


def check_for_duplicate_docstrings(file_path: str, content: List[str]) -> List[AutofixerIssue]:
    """Check if a file has duplicate module docstrings.

    Args:
        file_path: Path to the file to check
        content: List of lines in the file

    Returns:
        List of AutofixerIssue objects if issues found, empty list otherwise
    """
    issues = []

    # Find docstring start/end positions
    docstring_starts = []
    in_docstring = False
    docstring_content = []
    current_docstring_start = -1

    for i, line in enumerate(content):
        stripped = line.strip()

        # Check for docstring start
        if not in_docstring and stripped.startswith('"""'):
            in_docstring = True
            current_docstring_start = i
            docstring_content.append(stripped)

            # Check if it's a single-line docstring
            if stripped.endswith('"""') and len(stripped) > 3:
                in_docstring = False
                docstring_starts.append((current_docstring_start, i, "".join(docstring_content)))
                docstring_content = []

        # Check for docstring end
        elif in_docstring and '"""' in stripped:
            in_docstring = False
            docstring_content.append(stripped)
            docstring_starts.append((current_docstring_start, i, "".join(docstring_content)))
            docstring_content = []

        # Add content if in a docstring
        elif in_docstring:
            docstring_content.append(stripped)

    # Check for placeholder docstrings
    placeholder_pattern = re.compile(r'"""TODO: Module docstring for.*"""')

    # If we have multiple docstrings near the top of the file
    if len(docstring_starts) >= 2 and docstring_starts[0][0] < 10 and docstring_starts[1][0] < 20:
        # Check if one is a placeholder
        for start, end, content in docstring_starts:
            if placeholder_pattern.match(content):
                issues.append(AutofixerIssue(
                    file_path=file_path,
                    issue_type="duplicate_docstring",
                    description=f"Found placeholder docstring at line {start} and another docstring nearby",
                    line_numbers=[start, end],
                    suggestion="Remove the placeholder docstring and ensure the real docstring is at the module level"
                ))
                break

    return issues


def analyze_file(file_path: str) -> List[AutofixerIssue]:
    """Analyze a file for potential issues introduced by docstring_autofixer.

    Args:
        file_path: Path to the file to analyze

    Returns:
        List of AutofixerIssue objects
    """
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        # Run checks
        issues.extend(check_for_misplaced_shebang(file_path, content))
        issues.extend(check_for_duplicate_docstrings(file_path, content))

        # Add more checks as needed

    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")

    return issues


def main():
    """Main function to analyze files modified by docstring_autofixer."""
    parser = argparse.ArgumentParser(description="Analyze files modified by docstring_autofixer.py")
    parser.add_argument("--output", default="scripts/maintenance/code_health/analysis_results/autofixer_issues.json",
                        help="Path to save the JSON report of issues")
    parser.add_argument("--git-status-file", help="File containing output of 'git status --porcelain'")
    parser.add_argument("--verbose", action="store_true", help="Show detailed logs")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Get list of modified files
        modified_files = []

        if args.git_status_file:
            # Read from file
            with open(args.git_status_file, 'r') as f:
                git_status_output = f.read()
            modified_files = find_modified_files(git_status_output)
        else:
            # Run git status command
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   capture_output=True, text=True, check=True)
            modified_files = find_modified_files(result.stdout)

        logger.info(f"Found {len(modified_files)} modified Python files to analyze")

        # Analyze each file
        all_issues = []
        for i, file_path in enumerate(modified_files):
            if i % 10 == 0:
                logger.info(f"Analyzing file {i+1}/{len(modified_files)}: {file_path}")

            file_issues = analyze_file(file_path)
            all_issues.extend(file_issues)

            if file_issues and args.verbose:
                for issue in file_issues:
                    logger.debug(f"Found issue: {issue}")

        # Save report
        if all_issues:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)

            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_issues": len(all_issues),
                    "issues": [issue.to_dict() for issue in all_issues]
                }, f, indent=2)

            logger.info(f"Found {len(all_issues)} potential issues")
            logger.info(f"Saved report to {args.output}")

            # Print summary by issue type
            issue_types = {}
            for issue in all_issues:
                if issue.issue_type not in issue_types:
                    issue_types[issue.issue_type] = 0
                issue_types[issue.issue_type] += 1

            print("\nIssue Summary:")
            for issue_type, count in issue_types.items():
                print(f"  {issue_type}: {count}")
        else:
            logger.info("No issues found in the modified files")

    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())