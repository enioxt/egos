#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""EGOS Syntax Error Remediation Tool

This tool automates the process of identifying and fixing common syntax errors
in Python files across the EGOS codebase. It builds on the syntax_checker.py
functionality but adds remediation capabilities.

Usage:
    python syntax_remediation_tool.py --scan-only  # Identify issues without fixing
    python syntax_remediation_tool.py --fix  # Attempt to fix issues automatically
    python syntax_remediation_tool.py --file path/to/file.py  # Process specific file

@references:
- [MQP.md](mdc:../../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../../ROADMAP.md) - Project roadmap and planning
- [syntax_error_remediation_process.md](mdc:../../../docs/maintenance/syntax_error_remediation_process.md)
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

import argparse
import ast
import difflib
import logging
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("syntax_remediation_tool")

# Import the SyntaxChecker class from syntax_checker.py
try:
    from scripts.maintenance.code_health.syntax_checker_rewrite import (
        SyntaxChecker, 
        find_python_files,
        SyntaxIssue
    )
except ImportError:
    logger.error("Could not import from syntax_checker_rewrite.py. Make sure it exists in the same directory.")
    sys.exit(1)


class SyntaxRemediator:
    """Automated tool for remediating common syntax errors in Python files."""

    def __init__(self, verbose: bool = False, dry_run: bool = True):
        """
        Initialize the syntax remediator.

        Args:
            verbose: If True, output detailed information during processing
            dry_run: If True, don't actually make changes to files
        """
        self.verbose = verbose
        self.dry_run = dry_run
        self.checker = SyntaxChecker(verbose=verbose)

        # Counter for statistics
        self.stats = {
            "files_scanned": 0,
            "files_with_issues": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "files_fixed": 0,
        }

        # Map of issue types to fixing functions
        self.fixers = {
            "syntax_error": self._fix_syntax_error,
            "missing_import_sys": self._fix_missing_import,
            "missing_path_import": self._fix_missing_import,
            "missing_project_root": self._fix_import_resilience,
            "missing_sys_path_check": self._fix_import_resilience,
            "missing_sys_path_insert": self._fix_import_resilience,
        }

    def scan_file(self, file_path: str) -> List[SyntaxIssue]:
        """
        Scan a file for syntax issues without fixing them.

        Args:
            file_path: Path to the Python file to scan

        Returns:
            List of SyntaxIssue objects found in the file
        """
        self.stats["files_scanned"] += 1
        issues = self.checker.check_file(file_path)

        if issues:
            self.stats["files_with_issues"] += 1
            self.stats["issues_found"] += len(issues)

        return issues

    def remediate_file(self, file_path: str) -> Tuple[int, int]:
        """
        Attempt to fix syntax issues in a file.

        Args:
            file_path: Path to the Python file to fix

        Returns:
            Tuple of (issues_found, issues_fixed)
        """
        issues = self.scan_file(file_path)
        issues_fixed = 0

        if not issues:
            if self.verbose:
                logger.info(f"No issues found in {file_path}")
            return 0, 0

        logger.info(f"Found {len(issues)} issues in {file_path}")

        # Create a temporary file for the fixed content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Group issues by type for more efficient fixing
        issues_by_type = {}
        for issue in issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)

        # Apply fixers by issue type
        for issue_type, issue_list in issues_by_type.items():
            if issue_type in self.fixers:
                logger.info(f"Attempting to fix {len(issue_list)} issues of type '{issue_type}'")
                content, fixed = self.fixers[issue_type](content, issue_list)
                issues_fixed += fixed
            else:
                logger.warning(f"No fixer available for issue type '{issue_type}'")

        # Only write changes if something was fixed and not in dry run mode
        if issues_fixed > 0 and content != original_content:
            if not self.dry_run:
                # Create backup of original file
                backup_path = f"{file_path}.bak"
                logger.info(f"Creating backup at {backup_path}")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)

                # Write fixed content
                logger.info(f"Writing fixed content to {file_path}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.stats["files_fixed"] += 1
            else:
                logger.info("Dry run: showing diff but not writing changes")
                diff = difflib.unified_diff(
                    original_content.splitlines(),
                    content.splitlines(),
                    fromfile=f"{file_path} (original)",
                    tofile=f"{file_path} (fixed)",
                    lineterm="",
                )
                for line in diff:
                    print(line)

            self.stats["issues_fixed"] += issues_fixed

        return len(issues), issues_fixed

    @staticmethod
    def _fix_syntax_error(content: str, issues: List[SyntaxIssue]) -> Tuple[str, int]:
        """
        Attempt to fix general syntax errors.
        For now, this just focuses on simple cases like:
        - Indentation issues
        - Missing colons
        - Unmatched parentheses

        Args:
            content: Original file content
            issues: List of syntax issues to fix

        Returns:
            Tuple of (modified_content, number_of_issues_fixed)
        """
        # This is a basic implementation. In a real-world scenario,
        # you would need a much more sophisticated approach.
        fixed = 0
        modified = content

        lines = content.splitlines()
        for issue in issues:
            line_num = issue.line_number - 1  # 0-indexed
            if line_num < 0 or line_num >= len(lines):
                continue

            line = lines[line_num]

            # Check for missing colon in control flow statements
            if re.search(r'^\s*(if|for|while|def|class|else|elif|try|except|finally|with)\s+.*[^:]\s*$', line):
                lines[line_num] = line + ":"
                fixed += 1
                logger.info(f"Added missing colon at line {issue.line_number}")

            # Check for unmatched parentheses - simple case
            elif line.count('(') > line.count(')'):
                lines[line_num] = line + ")"
                fixed += 1
                logger.info(f"Added missing closing parenthesis at line {issue.line_number}")

            # Check for unmatched brackets - simple case
            elif line.count('[') > line.count(']'):
                lines[line_num] = line + "]"
                fixed += 1
                logger.info(f"Added missing closing bracket at line {issue.line_number}")

        if fixed > 0:
            modified = "\n".join(lines)

        return modified, fixed

    @staticmethod
    def _fix_missing_import(content: str, issues: List[SyntaxIssue]) -> Tuple[str, int]:
        """
        Fix missing import statements.

        Args:
            content: Original file content
            issues: List of syntax issues to fix

        Returns:
            Tuple of (modified_content, number_of_issues_fixed)
        """
        fixed = 0
        lines = content.splitlines()

        for issue in issues:
            if issue.issue_type == "missing_import_sys":
                # Add import sys at the top, after any docstring
                # Find the end of the docstring if present
                in_docstring = False
                docstring_end = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        in_docstring = not in_docstring
                        if not in_docstring:
                            docstring_end = i + 1
                            break

                # Insert after docstring or at the beginning
                if "import sys" not in "\n".join(lines[:20]):  # Check first 20 lines
                    lines.insert(docstring_end, "import sys")
                    fixed += 1
                    logger.info(f"Added missing 'import sys' after line {docstring_end}")

            elif issue.issue_type == "missing_path_import":
                # Add pathlib import after sys import if possible
                try:
                    sys_import_line = next(i for i, line in enumerate(lines) if "import sys" in line)
                    if "from pathlib import Path" not in "\n".join(lines[:sys_import_line + 5]):
                        lines.insert(sys_import_line + 1, "from pathlib import Path")
                        fixed += 1
                        logger.info(f"Added missing 'from pathlib import Path' after line {sys_import_line + 1}")
                except StopIteration:
                    # If sys import wasn't found, this is likely a bigger issue
                    logger.warning("Could not find 'import sys' line to add pathlib import after")

        if fixed > 0:
            return "\n".join(lines), fixed
        else:
            return content, 0

    @staticmethod
    def _fix_import_resilience(content: str, issues: List[SyntaxIssue]) -> Tuple[str, int]:
        """
        Fix import resilience pattern issues.

        Args:
            content: Original file content
            issues: List of syntax issues to fix

        Returns:
            Tuple of (modified_content, number_of_issues_fixed)
        """
        # Check if we need to implement complete import resilience pattern
        needs_complete_pattern = any(i.issue_type in [
            "missing_project_root", "missing_sys_path_check", "missing_sys_path_insert"
        ] for i in issues)

        if not needs_complete_pattern:
            return content, 0

        fixed = 0
        lines = content.splitlines()

        # Find appropriate location to insert pattern - after any imports and docstrings
        has_sys = "import sys" in content
        has_path = "from pathlib import Path" in content
        has_resilience_comment = "# EGOS Import Resilience" in content

        # Find insertion point
        insert_line = 0
        in_docstring = False
        for i, line in enumerate(lines):
            if (line.strip().startswith('"""') or line.strip().startswith("'''")):
                in_docstring = not in_docstring
                continue

            if not in_docstring and line.strip() and insert_line == 0:
                insert_line = i

        # Prepare the import resilience pattern
        resilience_pattern = []
        if not has_resilience_comment:
            resilience_pattern.append("# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md")
            fixed += 1

        if not has_sys:
            resilience_pattern.append("import sys")
            fixed += 1

        if not has_path:
            resilience_pattern.append("from pathlib import Path")
            fixed += 1

        resilience_pattern.extend([
            "project_root = str(Path(__file__).resolve().parents[3])",
            "if project_root not in sys.path:",
            "    sys.path.insert(0, project_root)",
            ""
        ])
        fixed += 3

        # Insert the pattern
        if resilience_pattern:
            lines[insert_line:insert_line] = resilience_pattern
            logger.info(f"Added import resilience pattern at line {insert_line + 1}")

        return "\n".join(lines), fixed

    def print_stats(self):
        """Print statistics from the remediation process."""
        logger.info("\n--- Remediation Statistics ---")
        logger.info(f"Files scanned: {self.stats['files_scanned']}")
        logger.info(f"Files with issues: {self.stats['files_with_issues']}")
        logger.info(f"Total issues found: {self.stats['issues_found']}")
        logger.info(f"Issues fixed: {self.stats['issues_fixed']}")
        logger.info(f"Files fixed: {self.stats['files_fixed']}")

        if self.stats['issues_found'] > 0:
            fix_rate = self.stats['issues_fixed'] / self.stats['issues_found'] * 100
            logger.info(f"Issue fix rate: {fix_rate:.1f}%")

        if self.dry_run:
            logger.info("Note: This was a dry run. No files were actually modified.")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="EGOS Syntax Error Remediation Tool")
    parser.add_argument("--scan-only", action="store_true", help="Only scan for issues, don't fix them")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed but don't modify files")
    parser.add_argument("--file", help="Process a specific file (instead of the whole codebase)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--root-dir", default=".", help="Root directory to scan")

    args = parser.parse_args()

    # Configure logging level
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Determine operation mode
    dry_run = True
    if args.fix and not args.dry_run:
        dry_run = False
        logger.warning("Fix mode enabled - files will be modified!")

    remediator = SyntaxRemediator(verbose=args.verbose, dry_run=dry_run)

    if args.file:
        # Process a single file
        file_path = os.path.abspath(args.file)
        logger.info(f"Processing file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            sys.exit(1)

        if args.scan_only:
            issues = remediator.scan_file(file_path)
            if issues:
                logger.info(f"Found {len(issues)} issues in {file_path}:")
                for issue in issues:
                    logger.info(f"  Line {issue.line_number}: {issue.issue_type} - {issue.description}")
            else:
                logger.info(f"No issues found in {file_path}")
        else:
            issues_found, issues_fixed = remediator.remediate_file(file_path)
            logger.info(f"Found {issues_found} issues, fixed {issues_fixed}")
    else:
        # Process the entire codebase
        root_dir = os.path.abspath(args.root_dir)
        logger.info(f"Scanning Python files in {root_dir}")

        python_files = find_python_files(root_dir)
        logger.info(f"Found {len(python_files)} Python files to process")

        for i, file_path in enumerate(python_files):
            if args.verbose or (i + 1) % 100 == 0 or i == 0 or i == len(python_files) - 1:
                logger.info(f"Processing file {i + 1}/{len(python_files)}: {os.path.relpath(file_path, root_dir)}")

            if args.scan_only:
                remediator.scan_file(file_path)
            else:
                remediator.remediate_file(file_path)

    # Print statistics
    remediator.print_stats()


if __name__ == "__main__":
    main()