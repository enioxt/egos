#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cross-Reference Analyzer Module for Directory Unification Tool

This module analyzes cross-references between files to identify relationships
and dependencies, supporting the directory unification process.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\cross_reference\file_reference_checker_ultra.py
    - C:\EGOS\scripts\cross_reference\optimized_reference_fixer.py
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
import time
import logging
from typing import Dict, Any, List, Set, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from concurrent.futures import TimeoutError as FuturesTimeoutError # Alias to avoid conflict if tqdm had one
from pathlib import Path

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

# Local imports
from .utils import setup_logger, print_banner, format_path, Timer, progress_bar

# Constants
CONFIG = {
    "REFERENCE_PATTERNS": [
        # EGOS canonical references (e.g., C:\EGOS\path\to\file.ext)
        r'C:\\EGOS\\[^"\'<>\n\r]*',
        # Relative paths with EGOS reference
        r'(?:\.\.\\|\./|\.\./)(?:[^"\'<>\n\r]*)',
        # Import statements in Python
        r'(?:from|import)\s+([a-zA-Z0-9_\.]+)',
        # Include statements in various languages
        r'#include\s+[<"]([^>"\']+)[>"]',
        # Markdown links with file references
        r'\[.*?\]\((?!https?://)([^)]+)\)',
        # HTML links with file references
        r'href=["\']((?!https?://)(?!#)[^"\']+)["\']',
        # Reference tags in documentation
        r'@references?:?\s+([^\n]+)',
        # EGOS canonical reference in square brackets
        r'\[egos:([^\]]+)\]',
        # Cross-reference format
        r'cci:[0-9]+://file:///[^"\'<>\n\r]*:[0-9]+:[0-9]+-[0-9]+:[0-9]+'
    ],
    "MAX_THREADS": 8,
    "BATCH_SIZE": 50,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Set up logger
logger = setup_logger("cross_reference_analyzer", CONFIG["LOG_FORMAT"])


class CrossReferenceAnalyzer:
    """
    Class for analyzing cross-references between files to identify relationships and dependencies.
    """
    
    def __init__(self, args: Dict[str, Any], context: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the CrossReferenceAnalyzer class.
        
        Args:
            args: Command line arguments or configuration
            context: Context data from previous modules
        """
        self.args = args
        self.context = context
        self.egos_root = Path(args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))))
        
        # Use the logger passed from the main tool
        self.logger = logger
        
        # Set processing parameters
        self.max_workers = args.get("thread_count", CONFIG.get("DEFAULT_THREAD_COUNT", 8))
        self.batch_size = args.get("batch_size", CONFIG.get("DEFAULT_BATCH_SIZE", 100))
        self.timeout = args.get("timeout", CONFIG.get("DEFAULT_TIMEOUT", 10))  # seconds
        
        # Ensure content discovery data is available
        if "content" not in context or not context["content"]:
            raise ValueError("Content discovery data is required for cross-reference analysis")
        
        # Extract files from content discovery
        self.files = context["content"].get("files", [])
        self.directories = context["content"].get("directories", [])
        
        # Initialize reference containers
        self.inbound_references = {}  # Files that reference a file
        self.outbound_references = {}  # Files referenced by a file
        self.reference_patterns = self._compile_reference_patterns()
        
        # Initialize statistics
        self.stats = {
            "total_files_analyzed": 0,
            "total_references_found": 0,
            "files_with_references": 0,
            "files_being_referenced": 0,
            "circular_references": 0,
            "broken_references": 0,
            "errors": 0
        }
    
    def _compile_reference_patterns(self) -> List[re.Pattern]:
        """
        Compile reference patterns for searching.
        
        Returns:
            List of compiled regex patterns
        """
        patterns = []
        for pattern in CONFIG["REFERENCE_PATTERNS"]:
            try:
                patterns.append(re.compile(pattern))
            except re.error as e:
                logger.error(f"Error compiling regex pattern '{pattern}': {e}")
        return patterns
    
    def analyze_references(self) -> Dict[str, Any]:
        """
        Analyze cross-references between files.
        
        Returns:
            Dict[str, Any]: Dictionary containing inbound and outbound references,
                           along with importance metrics.
        """
        self.logger.info("Starting cross-reference analysis")
        
        # Get files from context
        content = self.context.get("content", {})
        files = content.get("files", [])
        
        # For testing purposes, limit the number of files if needed
        if self.args.get("test_mode", False) and len(files) > 100:
            self.logger.info(f"Test mode: Limiting analysis to 100 files (from {len(files)})")
            files = files[:100]
        
        self.logger.info(f"Analyzing cross-references in {len(files)} files")
        
        # Initialize reference dictionaries
        inbound_references: Dict[str, Set[str]] = {}
        outbound_references: Dict[str, Set[str]] = {}
        
        # Track processing statistics
        processed_files = 0
        failed_files = 0
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            total_files = len(files)
            batch_size = min(self.batch_size, total_files)  # Process in batches to avoid memory issues
            
            for batch_start in range(0, total_files, batch_size):
                batch_end = min(batch_start + batch_size, total_files)
                batch = files[batch_start:batch_end]
                
                # Submit tasks to the executor
                futures.clear()
                for file_path in batch:
                    futures[executor.submit(self._analyze_file_references, file_path, files)] = file_path
                
                # Collect results with timeout
                for future in tqdm(as_completed(futures), total=len(futures), desc=f"Analyzing batch {batch_start//batch_size + 1}", unit="file", leave=False, disable=not self.args.get("verbose", False), ncols=100):
                    try:
                        file_path, file_outbound = future.result(timeout=self.timeout)  # Timeout per file
                        
                        # Update outbound references
                        outbound_references[file_path] = file_outbound
                        
                        # Update inbound references
                        for ref in file_outbound:
                            if ref not in inbound_references:
                                inbound_references[ref] = set()
                            inbound_references[ref].add(file_path)
                        
                        processed_files += 1
                    except FuturesTimeoutError:
                        self.logger.warning(f"Timeout analyzing references for {futures[future]}")
                        failed_files += 1
                    except Exception as e:
                        self.logger.error(f"Error analyzing references for {futures[future]}: {e}")
                        failed_files += 1
        
        # Calculate importance metrics
        importance_metrics = self._calculate_importance_metrics(inbound_references, outbound_references)
        
        elapsed = time.time() - start_time # Recalculate elapsed time for final log message
        
        self.logger.info(f"Cross-reference analysis completed. Processed {processed_files} files, {failed_files} failures")
        
        return {
            "inbound_references": inbound_references,
            "outbound_references": outbound_references,
            "importance_metrics": importance_metrics,
            "stats": {
                "processed_files": processed_files,
                "failed_files": failed_files,
                "total_files": total_files,
                "processing_time": elapsed
            }
        }
    
    def _analyze_file_references(self, file_path: str, all_files: List[str]) -> tuple[str, set[str]]:
        """
        Analyze references in a single file.
        
        Args:
            file_path: Path of the file to analyze
            all_files: List of all files in the content discovery
        
        Returns:
            tuple[str, set[str]]: File path and set of outbound references
        """
        try:
            # Skip files that are too large (>10MB)
            file_full_path = os.path.join(self.egos_root, file_path)
            if os.path.getsize(file_full_path) > 10 * 1024 * 1024:
                self.logger.warning(f"Skipping large file: {file_path}")
                return file_path, set()
                
            # Skip binary files
            if self._is_binary_file(file_full_path):
                self.logger.debug(f"Skipping binary file: {file_path}")
                return file_path, set()
                
            with open(file_full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
                # Find all references in the file content
                references = self._extract_references(content, file_path)
                
                # Return the file path and a set of referenced paths
                outbound_refs = set()
                for ref in references:
                    if "target_path" in ref and ref["target_path"]:
                        outbound_refs.add(ref["target_path"])
                        
                return file_path, outbound_refs
        
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return file_path, set()
    
    def _extract_references(self, content: str, source_path: str) -> List[Dict[str, Any]]:
        """
        Extract references from file content.
        
        Args:
            content: File content
            source_path: Path of the source file
            
        Returns:
            List of extracted references
        """
        references = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            for pattern in self.reference_patterns:
                matches = pattern.findall(line)
                if matches:
                    for match in matches:
                        # Skip empty matches
                        if not match:
                            continue
                        
                        # Handle tuple matches from regex groups
                        if isinstance(match, tuple):
                            match = match[0]
                        
                        # Normalize reference path
                        target_path = self._normalize_reference_path(match, source_path)
                        if not target_path:
                            continue
                        
                        # Get context (line before, current line, line after)
                        context_start = max(0, i - 1)
                        context_end = min(len(lines), i + 2)
                        context = lines[context_start:context_end]
                        
                        # Add reference to results
                        references.append({
                            "target_path": target_path,
                            "source_path": source_path,
                            "reference_text": match,
                            "line_number": i + 1,
                            "context": context
                        })
        
        return references
    
    def _normalize_reference_path(self, reference: str, source_path: str) -> Optional[str]:
        """
        Normalize a reference path to a standard format.
        
        Args:
            reference: Reference path or text
            source_path: Path of the source file
            
        Returns:
            Normalized reference path or None if invalid
        """
        # Handle EGOS canonical references
        if reference.startswith("C:\\EGOS\\"):
            # Convert to relative path from EGOS root
            return reference.replace("C:\\EGOS\\", "").replace("\\", "/")
        
        # Handle relative paths
        if reference.startswith("./") or reference.startswith("../") or reference.startswith(".\\") or reference.startswith("..\\"):
            # Get the directory of the source file
            source_dir = os.path.dirname(source_path)
            
            # Normalize path separator
            reference = reference.replace("\\", "/")
            
            # Resolve relative path
            try:
                full_path = os.path.normpath(os.path.join(source_dir, reference))
                
                # Ensure the path is within EGOS root
                if os.path.commonpath([self.egos_root, os.path.join(self.egos_root, full_path)]) == str(self.egos_root):
                    # Convert to relative path from EGOS root
                    return os.path.relpath(full_path, self.egos_root).replace("\\", "/")
            except Exception:
                return None
        
        # Handle cross-reference format
        if reference.startswith("cci:"):
            # Extract file path from cross-reference
            match = re.search(r'file:///([^:]+)', reference)
            if match:
                file_path = match.group(1).replace("\\", "/")
                
                # Extract EGOS root path if present
                egos_root_str = str(self.egos_root).replace("\\", "/")
                if file_path.startswith(egos_root_str):
                    return file_path[len(egos_root_str) + 1:]
        
        # Handle import statements
        if "." in reference and not reference.startswith(".") and not os.path.sep in reference:
            # This is likely a Python import, not a file reference
            return None
        
        # Default: return the reference as-is
        return reference
    
    def _find_circular_references(self) -> List[Dict[str, Any]]:
        """
        Find circular references in the analyzed files.
        
        Returns:
            List of circular reference chains
        """
        circular_refs = []
        visited = set()
        
        def dfs(current_path, path_so_far, visited_in_this_path):
            visited.add(current_path)
            visited_in_this_path.add(current_path)
            
            for ref in self.outbound_references.get(current_path, []):
                target_path = ref["target_path"]
                
                if target_path in visited_in_this_path:
                    # Found a circular reference
                    cycle = path_so_far + [target_path]
                    circular_refs.append({
                        "cycle": cycle,
                        "references": [
                            {
                                "source": cycle[i],
                                "target": cycle[i + 1]
                            }
                            for i in range(len(cycle) - 1)
                        ] + [
                            {
                                "source": cycle[-1],
                                "target": cycle[0]
                            }
                        ]
                    })
                elif target_path not in visited:
                    dfs(target_path, path_so_far + [target_path], visited_in_this_path.copy())
        
        for path in self.outbound_references.keys():
            if path not in visited:
                dfs(path, [path], set())
        
        return circular_refs
    
    def _find_broken_references(self) -> List[Dict[str, Any]]:
        """
        Find broken references in the analyzed files.
        
        Returns:
            List of broken references
        """
        broken_refs = []
        all_file_paths = {file_info["path"] for file_info in self.files}
        
        for source_path, references in self.outbound_references.items():
            for ref in references:
                target_path = ref["target_path"]
                
                # Check if the target file exists
                if target_path not in all_file_paths:
                    broken_refs.append({
                        "source_path": source_path,
                        "target_path": target_path,
                        "line_number": ref["line_number"],
                        "context": ref["context"]
                    })
        
        return broken_refs
    
    def _prepare_results(self) -> Dict[str, Any]:
        """
        Prepare analysis results for return.
        
        Returns:
            Dictionary with analysis results
        """
        # Build dependency graph
        dependency_graph = self._build_dependency_graph()
        
        # Build reference importance metrics
        importance_metrics = self._calculate_importance_metrics()
        
        return {
            "inbound_references": dict(self.inbound_references),
            "outbound_references": dict(self.outbound_references),
            "circular_references": self._find_circular_references(),
            "broken_references": self._find_broken_references(),
            "dependency_graph": dependency_graph,
            "importance_metrics": importance_metrics,
            "stats": self.stats
        }
    
    def _build_dependency_graph(self) -> Dict[str, Any]:
        """
        Build a dependency graph from the analyzed references.
        
        Returns:
            Dictionary representation of the dependency graph
        """
        nodes = []
        edges = []
        
        # Add nodes for all files
        file_indices = {}
        for i, file_info in enumerate(self.files):
            path = file_info["path"]
            file_indices[path] = i
            
            inbound_count = len(self.inbound_references.get(path, []))
            outbound_count = len(self.outbound_references.get(path, []))
            
            nodes.append({
                "id": i,
                "path": path,
                "name": os.path.basename(path),
                "inbound_count": inbound_count,
                "outbound_count": outbound_count,
                "total_references": inbound_count + outbound_count
            })
        
        # Add edges for references
        edge_id = 0
        for source_path, references in self.outbound_references.items():
            if source_path not in file_indices:
                continue
                
            source_id = file_indices[source_path]
            
            for ref in references:
                target_path = ref["target_path"]
                if target_path in file_indices:
                    target_id = file_indices[target_path]
                    edges.append({
                        "id": edge_id,
                        "source": source_id,
                        "target": target_id,
                        "line_number": ref["line_number"]
                    })
                    edge_id += 1
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary by reading the first 8KB and looking for null bytes.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file is binary, False otherwise
        """
        try:
            # Common binary file extensions
            binary_extensions = {
                '.pyc', '.pyd', '.dll', '.so', '.exe', '.bin', '.jar', '.war', '.ear',
                '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar', '.pdf', '.doc', '.docx',
                '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
                '.ico', '.tif', '.tiff', '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
                '.pack', '.idx', '.class', '.o'
            }
            
            # Check extension first for efficiency
            if any(file_path.lower().endswith(ext) for ext in binary_extensions):
                return True
                
            # Read first 8KB of the file
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
                
            # Additional heuristic: high ratio of non-printable characters
            non_printable = sum(1 for b in chunk if b < 8 or b > 13 and b < 32 or b > 126)
            if len(chunk) > 0 and non_printable / len(chunk) > 0.3:
                return True
                
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking if file is binary: {e}")
            # If we can't determine, assume it's not binary
            return False
    
    def _calculate_importance_metrics(self, inbound_refs: Dict[str, Set[str]], outbound_refs: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate importance metrics for files based on references.
        
        Args:
            inbound_refs: Dictionary mapping file paths to sets of files that reference them
            outbound_refs: Dictionary mapping file paths to sets of files they reference
            
        Returns:
            Dictionary mapping file paths to importance metrics
        """
        importance_metrics = {}
        
        # Get all unique file paths
        all_files = set(inbound_refs.keys()) | set(outbound_refs.keys())
        
        for file_path in all_files:
            inbound_count = len(inbound_refs.get(file_path, set()))
            outbound_count = len(outbound_refs.get(file_path, set()))
            
            # Calculate centrality (how important this file is in the reference network)
            centrality = inbound_count * 2 + outbound_count
            
            # Calculate dependency factor (how dependent other files are on this file)
            dependency_factor = inbound_count / (outbound_count + 1) if outbound_count > 0 else inbound_count
            
            # Calculate risk factor (how risky it would be to move/modify this file)
            risk_factor = centrality * dependency_factor
            
            importance_metrics[file_path] = {
                "centrality": centrality,
                "dependency_factor": dependency_factor,
                "risk_factor": risk_factor,
                "inbound_count": inbound_count,
                "outbound_count": outbound_count
            }
        
        return importance_metrics


def main():
    """Main function for testing the CrossReferenceAnalyzer module."""
    import argparse
    import json
    
    # Print banner
    print_banner("Cross-Reference Analyzer Module")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Cross-Reference Analyzer Module for Directory Unification Tool")
    parser.add_argument("--content-file", required=True, help="Path to content discovery results JSON file")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    parser.add_argument("--output", help="Output file for results (JSON format)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for testing")
    
    args = parser.parse_args()
    
    # Load content discovery results
    try:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading content file: {e}{Style.RESET_ALL}")
        return
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Create context
    context = {
        "content": content
    }
    
    # Create CrossReferenceAnalyzer instance
    test_logger = setup_logger("cross_ref_analyzer_test", CONFIG.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"), log_level=logging.DEBUG if args_dict.get("verbose") else logging.INFO)
    analyzer = CrossReferenceAnalyzer(args_dict, context, test_logger)
    
    # Analyze references
    results = analyzer.analyze_references()
    
    # Display summary
    print(f"\n{Fore.CYAN}Cross-Reference Analysis Results:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Files with outbound references:{Style.RESET_ALL} {results['stats']['files_with_references']}")
    print(f"  {Fore.GREEN}Files with inbound references:{Style.RESET_ALL} {results['stats']['files_being_referenced']}")
    print(f"  {Fore.GREEN}Total references found:{Style.RESET_ALL} {results['stats']['total_references_found']}")
    print(f"  {Fore.GREEN}Circular references:{Style.RESET_ALL} {results['stats']['circular_references']}")
    print(f"  {Fore.GREEN}Broken references:{Style.RESET_ALL} {results['stats']['broken_references']}")
    
    # Output results to file if specified
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Fore.GREEN}Results saved to {args.output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    main()