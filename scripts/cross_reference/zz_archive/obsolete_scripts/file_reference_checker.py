#!/usr/bin/env python
"""File Reference Checker

Finds files modified in the last N hours and checks if they are referenced in other files.
Generates a report of undocumented files to help maintain proper cross-references.

Author: EGOS Development Team
Date: 2025-05-18

@references: 
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

import argparse
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "monitored_extensions": [
        ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md", 
        ".html", ".css", ".scss", ".jsx", ".tsx", ".ps1", ".sh"
    ],
    "excluded_dirs": [
        "node_modules", ".git", "venv", "build", "dist", 
        "__pycache__", ".pytest_cache", ".vscode", ".idea"
    ],
    "time_window_hours": 48,
    "output_dir": "reports/file_references",
    "search_methods": ["exact", "path", "basename"],
    "context_lines": 2,
    "parallel_processes": 4
}


class FileReferenceChecker:
    """Checks if recently modified files are referenced in other files."""
    
    def __init__(
        self, 
        repo_path: str, 
        since: str = "48h", 
        exclude_dirs: Optional[List[str]] = None,
        include_exts: Optional[List[str]] = None,
        output_json: Optional[str] = None,
        output_md: Optional[str] = None,
        agent_mode: bool = False
    ):
        """Initialize the checker.
        
        Args:
            repo_path: Path to the repository
            since: Time window (e.g., "48h" for 48 hours, "7d" for 7 days)
            exclude_dirs: List of directories to exclude
            include_exts: List of file extensions to include
            output_json: Path to save JSON report
            output_md: Path to save Markdown report
            agent_mode: Whether to run in agent mode (print JSON to stdout)
        """
        self.repo_path = Path(repo_path).resolve()
        self.config = DEFAULT_CONFIG.copy()
        
        # Parse time window
        self.time_window_hours = self._parse_time_window(since)
        
        # Update configuration
        if exclude_dirs:
            self.config["excluded_dirs"].extend(exclude_dirs)
        
        if include_exts:
            self.config["monitored_extensions"] = include_exts
        
        # Ensure all extensions have a leading dot
        self.config["monitored_extensions"] = [
            ext if ext.startswith(".") else f".{ext}" 
            for ext in self.config["monitored_extensions"]
        ]
        
        # Set output paths
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config["output_dir"])
        
        self.output_json = output_json or str(output_dir / f"file_reference_check_{timestamp}.json")
        self.output_md = output_md or str(output_dir / f"file_reference_check_{timestamp}.md")
        self.agent_mode = agent_mode
        
        # Create output directory if it doesn't exist
        if not self.agent_mode:
            os.makedirs(os.path.dirname(self.output_json), exist_ok=True)
            os.makedirs(os.path.dirname(self.output_md), exist_ok=True)
    
    def _parse_time_window(self, since: str) -> int:
        """Parse time window string into hours.
        
        Args:
            since: Time window string (e.g., "48h", "7d")
            
        Returns:
            Number of hours
        """
        match = re.match(r"^(\d+)([hd])$", since)
        if not match:
            raise ValueError(f"Invalid time window format: {since}. Use format like '48h' or '7d'.")
        
        value, unit = match.groups()
        if unit == "h":
            return int(value)
        elif unit == "d":
            return int(value) * 24
        else:
            raise ValueError(f"Invalid time unit: {unit}. Use 'h' for hours or 'd' for days.")
    
    def _is_excluded_dir(self, path: Path) -> bool:
        """Check if a path should be excluded.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        path_parts = path.parts
        return any(excluded in path_parts for excluded in self.config["excluded_dirs"])
    
    def _is_monitored_file(self, path: Path) -> bool:
        """Check if a file should be monitored.
        
        Args:
            path: Path to check
            
        Returns:
            True if the file should be monitored, False otherwise
        """
        return path.suffix.lower() in self.config["monitored_extensions"]
    
    def find_modified_files(self) -> List[Path]:
        """Find files modified within the time window.
        
        Returns:
            List of paths to modified files
        """
        logger.info(f"Finding files modified in the last {self.time_window_hours} hours...")
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=self.time_window_hours)
        modified_files = []
        
        # Try to use git for faster modification detection
        try:
            git_time_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
            git_cmd = ["git", "-C", str(self.repo_path), "log", "--name-only", "--pretty=format:", f"--since={git_time_str}"]
            result = subprocess.run(git_cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                # Process git output
                git_files = set(line.strip() for line in result.stdout.splitlines() if line.strip())
                
                # Convert to absolute paths and filter
                for file_path in git_files:
                    abs_path = (self.repo_path / file_path).resolve()
                    if (abs_path.is_file() and 
                        self._is_monitored_file(abs_path) and 
                        not self._is_excluded_dir(abs_path)):
                        modified_files.append(abs_path)
                
                logger.info(f"Found {len(modified_files)} modified files using git")
                return modified_files
        
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.info("Git method failed, falling back to filesystem scan")
        
        # Fallback to filesystem scan
        for root, dirs, files in os.walk(self.repo_path):
            # Modify dirs in-place to exclude directories
            dirs[:] = [d for d in dirs if d not in self.config["excluded_dirs"]]
            
            for file in files:
                file_path = Path(root) / file
                if not self._is_monitored_file(file_path):
                    continue
                
                try:
                    mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime >= cutoff_time:
                        modified_files.append(file_path)
                except (OSError, PermissionError) as e:
                    logger.warning(f"Error accessing {file_path}: {e}")
        
        logger.info(f"Found {len(modified_files)} modified files using filesystem scan")
        return modified_files
    
    def find_reference_files(self) -> List[Path]:
        """Find all files that could contain references.
        
        Returns:
            List of paths to reference files
        """
        logger.info("Finding reference files...")
        
        reference_files = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Modify dirs in-place to exclude directories
            dirs[:] = [d for d in dirs if d not in self.config["excluded_dirs"]]
            
            for file in files:
                file_path = Path(root) / file
                if self._is_monitored_file(file_path):
                    reference_files.append(file_path)
        
        logger.info(f"Found {len(reference_files)} reference files")
        return reference_files
    
    def _generate_search_patterns(self, file_path: Path) -> List[str]:
        """Generate search patterns for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of search patterns
        """
        patterns = []
        
        # Get relative path from repo root
        rel_path = file_path.relative_to(self.repo_path)
        
        # Add patterns based on search methods
        if "exact" in self.config["search_methods"]:
            # Exact filename with extension
            patterns.append(str(rel_path))
            # With forward slashes (for markdown links)
            patterns.append(str(rel_path).replace("\\", "/"))
        
        if "path" in self.config["search_methods"]:
            # Path fragments
            path_parts = list(rel_path.parts)
            if len(path_parts) > 1:
                for i in range(1, len(path_parts)):
                    path_fragment = os.path.join(*path_parts[-i:])
                    patterns.append(path_fragment)
                    patterns.append(path_fragment.replace("\\", "/"))
        
        if "basename" in self.config["search_methods"]:
            # Basename without extension
            patterns.append(file_path.stem)
        
        return patterns
    
    def _search_file_for_references(
        self, 
        search_file: Path, 
        patterns: List[str],
        exclude_file: Path
    ) -> List[Dict]:
        """Search a file for references to patterns.
        
        Args:
            search_file: File to search in
            patterns: Patterns to search for
            exclude_file: File to exclude from search (the file itself)
            
        Returns:
            List of references found
        """
        if search_file == exclude_file:
            return []
        
        try:
            with open(search_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, OSError, PermissionError):
            # Skip files that can't be read
            return []
        
        references = []
        
        for pattern in patterns:
            # Skip very short patterns to avoid false positives
            if len(pattern) < 3:
                continue
                
            # Find all occurrences of the pattern
            for match in re.finditer(re.escape(pattern), content, re.IGNORECASE):
                # Get context around the match
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(content), match.end() + 50)
                context = content[start_pos:end_pos]
                
                # Add reference
                references.append({
                    "in": str(search_file.relative_to(self.repo_path)),
                    "pattern": pattern,
                    "context": context.replace("\n", " ").strip()
                })
                
                # One match per pattern is enough
                break
        
        return references
    
    def _process_file_batch(
        self, 
        modified_file: Path, 
        reference_files: List[Path]
    ) -> Tuple[Path, List[Dict]]:
        """Process a batch of files to find references.
        
        Args:
            modified_file: Modified file to check
            reference_files: Files to search in
            
        Returns:
            Tuple of (modified_file, references)
        """
        patterns = self._generate_search_patterns(modified_file)
        references = []
        
        for ref_file in reference_files:
            refs = self._search_file_for_references(ref_file, patterns, modified_file)
            references.extend(refs)
        
        return modified_file, references
    
    def find_references(
        self, 
        modified_files: List[Path], 
        reference_files: List[Path]
    ) -> Dict[Path, List[Dict]]:
        """Find references to modified files.
        
        Args:
            modified_files: List of modified files
            reference_files: List of reference files
            
        Returns:
            Dictionary mapping modified files to their references
        """
        logger.info("Searching for references...")
        
        results = {}
        total_files = len(modified_files)
        
        # Process files in parallel
        with ProcessPoolExecutor(max_workers=self.config["parallel_processes"]) as executor:
            futures = []
            
            for i, modified_file in enumerate(modified_files):
                future = executor.submit(
                    self._process_file_batch, 
                    modified_file, 
                    reference_files
                )
                futures.append(future)
            
            # Process results as they complete
            for i, future in enumerate(as_completed(futures)):
                modified_file, references = future.result()
                results[modified_file] = references
                
                if (i + 1) % 10 == 0 or (i + 1) == total_files:
                    logger.info(f"Processed {i + 1}/{total_files} files")
        
        return results
    
    def generate_report(self, results: Dict[Path, List[Dict]]) -> Dict:
        """Generate a report of the results.
        
        Args:
            results: Dictionary mapping modified files to their references
            
        Returns:
            Report dictionary
        """
        logger.info("Generating report...")
        
        report = []
        
        for file_path, references in results.items():
            status = "Documented" if references else "Undocumented"
            
            report_item = {
                "file": str(file_path.relative_to(self.repo_path)),
                "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "mentions": references,
                "status": status
            }
            
            report.append(report_item)
        
        # Sort by status (undocumented first) and then by file path
        report.sort(key=lambda x: (0 if x["status"] == "Undocumented" else 1, x["file"]))
        
        return report
    
    def save_json_report(self, report: List[Dict]) -> None:
        """Save the report as JSON.
        
        Args:
            report: Report data
        """
        with open(self.output_json, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"JSON report saved to {self.output_json}")
    
    def save_markdown_report(self, report: List[Dict]) -> None:
        """Save the report as Markdown.
        
        Args:
            report: Report data
        """
        documented_count = sum(1 for item in report if item["status"] == "Documented")
        undocumented_count = len(report) - documented_count
        
        with open(self.output_md, 'w', encoding='utf-8') as f:
            f.write("# File Reference Check Report\n\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Time Window: {self.time_window_hours} hours\n")
            f.write(f"- Total Files Checked: {len(report)}\n")
            f.write(f"- Documented Files: {documented_count}\n")
            f.write(f"- Undocumented Files: {undocumented_count}\n\n")
            
            if undocumented_count > 0:
                f.write("## Undocumented Files\n\n")
                f.write("These files have been modified recently but are not referenced anywhere else:\n\n")
                
                for item in report:
                    if item["status"] == "Undocumented":
                        f.write(f"- `{item['file']}`\n")
                
                f.write("\n")
            
            f.write("## Documented Files\n\n")
            
            for item in report:
                if item["status"] == "Documented":
                    f.write(f"### {item['file']}\n\n")
                    f.write(f"Last Modified: {item['last_modified']}\n\n")
                    f.write("Referenced in:\n\n")
                    
                    for mention in item["mentions"]:
                        f.write(f"- **{mention['in']}**: \"{mention['context']}\"\n")
                    
                    f.write("\n")
        
        logger.info(f"Markdown report saved to {self.output_md}")
    
    def run(self) -> List[Dict]:
        """Run the checker.
        
        Returns:
            Report data
        """
        start_time = time.time()
        
        # Find modified files
        modified_files = self.find_modified_files()
        
        if not modified_files:
            logger.info(f"No files modified in the last {self.time_window_hours} hours")
            report = []
        else:
            # Find reference files
            reference_files = self.find_reference_files()
            
            # Find references
            results = self.find_references(modified_files, reference_files)
            
            # Generate report
            report = self.generate_report(results)
            
            # Save reports
            if not self.agent_mode:
                self.save_json_report(report)
                self.save_markdown_report(report)
            
        elapsed_time = time.time() - start_time
        logger.info(f"Completed in {elapsed_time:.2f} seconds")
        
        # Print JSON to stdout in agent mode
        if self.agent_mode:
            print(json.dumps(report, indent=2))
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check if recently modified files are referenced in other files"
    )
    
    parser.add_argument(
        "--repo-path", "-r",
        default=".",
        help="Path to the repository (default: current directory)"
    )
    
    parser.add_argument(
        "--since", "-s",
        default="48h",
        help="Time window (e.g., '48h' for 48 hours, '7d' for 7 days) (default: 48h)"
    )
    
    parser.add_argument(
        "--exclude-dir", "-e",
        action="append",
        help="Directory to exclude (can be specified multiple times)"
    )
    
    parser.add_argument(
        "--include-ext", "-i",
        action="append",
        help="File extension to include (can be specified multiple times)"
    )
    
    parser.add_argument(
        "--output-json", "-j",
        help="Path to save JSON report"
    )
    
    parser.add_argument(
        "--output-md", "-m",
        help="Path to save Markdown report"
    )
    
    parser.add_argument(
        "--agent-mode", "-a",
        action="store_true",
        help="Run in agent mode (print JSON to stdout)"
    )
    
    args = parser.parse_args()
    
    try:
        checker = FileReferenceChecker(
            repo_path=args.repo_path,
            since=args.since,
            exclude_dirs=args.exclude_dir,
            include_exts=args.include_ext,
            output_json=args.output_json,
            output_md=args.output_md,
            agent_mode=args.agent_mode
        )
        
        checker.run()
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())