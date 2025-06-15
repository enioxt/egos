#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Content Discovery Module for Directory Unification Tool

This module provides functionality for discovering content related to a specified
keyword across the EGOS system. It supports various search methods and filters.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Standard library imports
import os
import re
import logging
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports
try:
    from colorama import Fore, Style, init
    init()  # Initialize colorama
except ImportError:
    # Define dummy colorama classes if not available
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()
from tqdm import tqdm

# Local imports
from .utils import setup_logger, print_banner, format_path, is_binary_file

# Constants
CONFIG = {
    "DEFAULT_SEARCH_DEPTH": 10,
    "DEFAULT_BATCH_SIZE": 100,
    "DEFAULT_THREAD_COUNT": 8,
    "DEFAULT_MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10 MB
    "BINARY_FILE_EXTENSIONS": {".pyc", ".exe", ".dll", ".pyd", ".so", ".zip", ".tar", ".gz", ".7z", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".pdf"},
    "DEFAULT_EXCLUDE_PATTERNS": ["__pycache__", "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.exe", ".git", ".svn", ".hg", ".venv", "venv", "node_modules", ".vs", ".vscode"],
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Logger will be passed in during instantiation.


class ContentDiscovery:
    """
    Class for discovering content related to a specified keyword across the EGOS system.
    """
    
    def __init__(self, args: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the ContentDiscovery class.
        
        Args:
            args: Command line arguments or configuration
            egos_root: Path to the EGOS root directory (optional)
        """
        self.args = args
        self.logger = logger
        self.egos_root = Path(args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))))
        
        # Set up search parameters
        self.keyword = args.get("keyword", "")
        self.search_method = args.get("search_method", "all")
        self.search_depth = args.get("search_depth", CONFIG["DEFAULT_SEARCH_DEPTH"])
        self.include_types = args.get("include_types", [])
        self.exclude_patterns = args.get("exclude_patterns", CONFIG["DEFAULT_EXCLUDE_PATTERNS"])
        self.max_file_size = args.get("max_file_size", CONFIG["DEFAULT_MAX_FILE_SIZE"])
        self.thread_count = args.get("thread_count", CONFIG["DEFAULT_THREAD_COUNT"])
        self.batch_size = args.get("batch_size", CONFIG["DEFAULT_BATCH_SIZE"])
        self.case_sensitive = args.get("case_sensitive", False)
        self.verbose = args.get("verbose", False)
        
        # Initialize result containers
        self.found_files = []
        self.found_directories = []
        self.stats = {
            "total_files_searched": 0,
            "total_directories_searched": 0,
            "total_files_matched": 0,
            "total_directories_matched": 0,
            "total_content_matches": 0,
            "skipped_files": 0,
            "errors": 0
        }
        
        # Compile regex pattern if needed
        self.regex_pattern = None
        if self.keyword:
            pattern = self.keyword if self.case_sensitive else self.keyword.lower()
            self.regex_pattern = re.compile(pattern)
    
    def find_related_content(self) -> Dict[str, Any]:

        """
        Find content related to the specified keyword across the EGOS system.
        
        Returns:
            Dictionary with search results and statistics
        """
        self.logger.info(f"Starting content discovery for keyword: {self.keyword}")
        
        if not self.keyword:
            self.logger.error("No keyword specified for content discovery")
            return {
                "files": [],
                "directories": [],
                "stats": self.stats
            }
        
        # Check if the EGOS root exists
        if not self.egos_root.exists():
            self.logger.error(f"EGOS root directory does not exist: {self.egos_root}")
            return {
                "files": [],
                "directories": [],
                "stats": self.stats
            }
        
        # Search for files and directories
        self.logger.info(f"Searching in {self.egos_root} with depth {self.search_depth}")
        self._search_directory(self.egos_root, depth=0)
        
        self.logger.info(f"Content discovery completed. Found {len(self.found_files)} files and {len(self.found_directories)} directories.")
        
        # Return the results
        return {
            "files": self.found_files,
            "directories": self.found_directories,
            "stats": self.stats
        }
    
    def _search_directory(self, directory: Path, depth: int) -> None:
        """
        Search a directory for content related to the specified keyword.
        
        Args:
            directory: Path to the directory to search
            depth: Current search depth
        """
        if depth > self.search_depth:
            return
        
        try:
            # Check if the directory name matches the keyword
            dir_name = directory.name
            if self._match_name(dir_name):
                self._add_matched_directory(directory)
            
            # Skip excluded directories
            if any(fnmatch.fnmatch(dir_name, pattern) for pattern in self.exclude_patterns):
                return
            
            # Get all files and directories in the current directory
            items = list(directory.iterdir())
            
            # Update statistics
            self.stats["total_directories_searched"] += 1
            
            # Process files in batches using ThreadPoolExecutor for performance
            files = [item for item in items if item.is_file()]
            self.stats["total_files_searched"] += len(files)
            
            for i in range(0, len(files), self.batch_size):
                batch = files[i:i + self.batch_size]
                with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                    futures = {executor.submit(self._process_file, file_path): file_path for file_path in batch}
                    for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing files in {directory.name.ljust(20)}", unit="file", leave=False, disable=not self.verbose, ncols=100):
                        try:
                            future.result()
                        except Exception as e:
                            file_path = futures[future]
                            self.logger.error(f"Error processing file {file_path}: {e}")
                            self.stats["errors"] += 1
            
            # Process subdirectories recursively
            directories = [item for item in items if item.is_dir()]
            for subdir in tqdm(directories, desc=f"Scanning subdirs in {directory.name.ljust(20)}", unit="dir", leave=False, disable=not self.verbose, ncols=100):
                self._search_directory(subdir, depth + 1)
        
        except Exception as e:
            self.logger.error(f"Error searching directory {directory}: {e}")
            self.stats["errors"] += 1
    
    def _process_file(self, file_path: Path) -> None:
        """
        Process a file to check if it matches the keyword.
        
        Args:
            file_path: Path to the file to process
        """
        try:
            # Skip excluded file patterns
            if any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.exclude_patterns):
                self.stats["skipped_files"] += 1
                return
            
            # Filter by file type if specified
            if self.include_types and not any(file_path.suffix.lower().lstrip('.') == ext.lower().lstrip('.') for ext in self.include_types):
                self.stats["skipped_files"] += 1
                return
            
            # Check file size
            try:
                if file_path.stat().st_size > self.max_file_size:
                    self.logger.warning(f"Skipping file due to size: {file_path}")
                    self.stats["skipped_files"] += 1
                    return
            except Exception as e:
                self.logger.error(f"Error getting file size for {file_path}: {e}")
                self.stats["errors"] += 1
                return
            
            # Check if the file name matches the keyword
            if self.search_method in ("all", "filename") and self._match_name(file_path.name):
                self._add_matched_file(file_path, match_type="filename")
            
            # Check if the file content matches the keyword
            if self.search_method in ("all", "content"):
                if is_binary_file(file_path):
                    self.logger.debug(f"Skipping binary file: {file_path}")
                    self.stats["skipped_files"] += 1
                    return
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                        if not self.case_sensitive:
                            content = content.lower()
                        
                        if self.keyword in content:
                            # Count occurrences
                            occurrences = content.count(self.keyword)
                            self.stats["total_content_matches"] += occurrences
                            
                            # Extract context for each match
                            context_lines = []
                            if occurrences <= 10:  # Limit to first 10 occurrences for performance
                                lines = content.splitlines()
                                for i, line in enumerate(lines):
                                    if self.keyword in (line.lower() if not self.case_sensitive else line):
                                        start = max(0, i - 1)
                                        end = min(len(lines), i + 2)
                                        context = lines[start:end]
                                        context_lines.append({
                                            "line_number": i + 1,
                                            "context": context
                                        })
                            
                            self._add_matched_file(file_path, match_type="content", occurrences=occurrences, context=context_lines)
                except Exception as e:
                    self.logger.error(f"Error reading file {file_path}: {e}")
                    self.stats["errors"] += 1
        
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            self.stats["errors"] += 1
    
    def _match_name(self, name: str) -> bool:
        """
        Check if a name matches the keyword.
        
        Args:
            name: Name to check
            
        Returns:
            True if the name matches the keyword, False otherwise
        """
        if not self.case_sensitive:
            name = name.lower()
            
        return self.keyword in name
    
    def _add_matched_file(self, file_path: Path, match_type: str, occurrences: int = 0, context: List[Dict[str, Any]] = None) -> None:
        """
        Add a matched file to the results.
        
        Args:
            file_path: Path to the matched file
            match_type: Type of match (filename or content)
            occurrences: Number of occurrences in content (if applicable)
            context: Context lines for content matches (if applicable)
        """
        rel_path = file_path.relative_to(self.egos_root)
        
        # Check if the file is already in the results
        for existing_file in self.found_files:
            if existing_file["path"] == str(rel_path):
                # Update match types and occurrences
                existing_file["match_types"].add(match_type)
                existing_file["occurrences"] += occurrences
                
                # Update context if provided
                if context:
                    if "context" not in existing_file:
                        existing_file["context"] = []
                    existing_file["context"].extend(context)
                
                return
        
        # Add new file to results
        file_info = {
            "path": str(rel_path),
            "full_path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
            "extension": file_path.suffix,
            "match_types": {match_type},
            "occurrences": occurrences
        }
        
        if context:
            file_info["context"] = context
        
        self.found_files.append(file_info)
        self.stats["total_files_matched"] += 1
        
        self.logger.debug(f"Found matching file: {rel_path} ({match_type})")
    
    def _add_matched_directory(self, dir_path: Path) -> None:
        """
        Add a matched directory to the results.
        
        Args:
            dir_path: Path to the matched directory
        """
        rel_path = dir_path.relative_to(self.egos_root)
        
        # Check if the directory is already in the results
        for existing_dir in self.found_directories:
            if existing_dir["path"] == str(rel_path):
                return
        
        # Add new directory to results
        dir_info = {
            "path": str(rel_path),
            "full_path": str(dir_path),
            "name": dir_path.name,
            "modified": dir_path.stat().st_mtime
        }
        
        self.found_directories.append(dir_info)
        self.stats["total_directories_matched"] += 1
        
        self.logger.debug(f"Found matching directory: {rel_path}")


def main():
    """Main function for testing the ContentDiscovery module."""
    import argparse
    import json
    
    # Print banner
    print_banner("Content Discovery Module")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Content Discovery Module for Directory Unification Tool")
    parser.add_argument("--keyword", required=True, help="Keyword to search for")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    parser.add_argument("--search-method", choices=["all", "filename", "content"], default="all", help="Search method")
    parser.add_argument("--search-depth", type=int, default=CONFIG["DEFAULT_SEARCH_DEPTH"], help="Maximum search depth")
    parser.add_argument("--include-types", help="Comma-separated list of file types to include")
    parser.add_argument("--exclude-patterns", help="Comma-separated list of patterns to exclude")
    parser.add_argument("--max-file-size", type=int, default=CONFIG["DEFAULT_MAX_FILE_SIZE"], help="Maximum file size in bytes")
    parser.add_argument("--thread-count", type=int, default=CONFIG["DEFAULT_THREAD_COUNT"], help="Number of threads for file processing")
    parser.add_argument("--case-sensitive", action="store_true", help="Enable case-sensitive search")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", help="Output file for results (JSON format)")
    
    args = parser.parse_args()
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Process include_types and exclude_patterns
    if args.include_types:
        args_dict["include_types"] = [t.strip() for t in args.include_types.split(",")]
    
    if args.exclude_patterns:
        args_dict["exclude_patterns"] = [p.strip() for p in args.exclude_patterns.split(",")]
    
    # Create ContentDiscovery instance
    test_logger = setup_logger("content_discovery_test", CONFIG["LOG_FORMAT"], log_level=logging.DEBUG if args.verbose else logging.INFO)
    discovery = ContentDiscovery(args_dict, test_logger)
    
    # Find related content
    results = discovery.find_related_content()
    
    # Display summary
    print(f"\n{Fore.CYAN}Content Discovery Results:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Files found:{Style.RESET_ALL} {len(results['files'])}")
    print(f"  {Fore.GREEN}Directories found:{Style.RESET_ALL} {len(results['directories'])}")
    print(f"\n{Fore.CYAN}Statistics:{Style.RESET_ALL}")
    for key, value in results["stats"].items():
        print(f"  {Fore.GREEN}{key}:{Style.RESET_ALL} {value}")
    
    # Output results to file if specified
    if args.output:
        # Convert sets to lists for JSON serialization
        for file_info in results["files"]:
            file_info["match_types"] = list(file_info["match_types"])
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Fore.GREEN}Results saved to {args.output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    main()