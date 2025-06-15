#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Context Analyzer Module for Directory Unification Tool

This module enhances the cross-reference analysis with deeper context understanding,
analyzing documentation, imports, function calls, and semantic relationships
between files to ensure accurate consolidation decisions.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\maintenance\directory_unification\cross_reference_analyzer.py
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
import ast
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict

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
from .utils import setup_logger, print_banner, format_path, Timer

# Constants
CONFIG = {
    "DOCUMENTATION_PATTERNS": [
        r'@references:',
        r'References:',
        r'Related files:',
        r'See also:',
        r'mdc:',
        r'cci:'
    ],
    "IMPORT_PATTERNS": [
        r'import\s+([a-zA-Z0-9_\.]+)',
        r'from\s+([a-zA-Z0-9_\.]+)\s+import'
    ],
    "FUNCTION_CALL_PATTERNS": [
        r'([a-zA-Z0-9_]+)\(',
        r'([a-zA-Z0-9_]+)\.'
    ],
    "SEMANTIC_SIMILARITY_THRESHOLD": 0.7,
    "MIN_DOCUMENTATION_SCORE": 0.3,
    "MIN_FUNCTIONAL_SCORE": 0.5
}


class ContextAnalyzer:
    """
    Class for analyzing the context and relationships between files to ensure
    accurate consolidation decisions.
    """
    
    def __init__(self, args: Dict[str, Any], context: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the ContextAnalyzer class.
        
        Args:
            args: Command line arguments or configuration
            context: Context data from previous modules
            logger: Logger instance
        """
        self.args = args
        self.context = context
        self.logger = logger
        self.egos_root = Path(args.get("egos_root", os.environ.get("EGOS_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))))
        
        # Ensure content discovery and cross-reference analysis data are available
        if "content" not in context or not context["content"]:
            raise ValueError("Content discovery data is required for context analysis")
        
        if "references" not in context or not context["references"]:
            raise ValueError("Cross-reference analysis data is required for context analysis")
        
        # Extract data from context
        self.files = context["content"].get("files", [])
        self.inbound_references = context["references"].get("inbound_references", {})
        self.outbound_references = context["references"].get("outbound_references", {})
        
        # Initialize analysis results
        self.documentation_scores = {}
        self.functional_groups = {}
        self.semantic_relationships = {}
        self.orphaned_files = set()
        self.context_scores = {}
        
        # Initialize statistics
        self.stats = {
            "total_files_analyzed": len(self.files),
            "files_with_documentation": 0,
            "orphaned_files": 0,
            "functional_groups_identified": 0,
            "semantic_relationships_found": 0
        }
    
    def analyze_context(self) -> Dict[str, Any]:
        """
        Analyze the context and relationships between files.
        
        Returns:
            Dictionary with context analysis results
        """
        self.logger.info("Starting context analysis")
        
        # Start timer
        timer = Timer("Context Analysis")
        timer.start()
        
        try:
            # Analyze documentation
            self._analyze_documentation()
            
            # Analyze functional groups
            self._analyze_functional_groups()
            
            # Analyze semantic relationships
            self._analyze_semantic_relationships()
            
            # Identify orphaned files
            self._identify_orphaned_files()
            
            # Calculate context scores
            self._calculate_context_scores()
            
            # Prepare results
            results = self._prepare_results()
            
            # Update statistics
            self._update_statistics()
            
            # Log completion
            elapsed_time = timer.stop()
            self.logger.info(f"Context analysis completed in {elapsed_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            elapsed_time = timer.stop()
            self.logger.error(f"Context analysis failed after {elapsed_time:.2f} seconds: {e}")
            raise
    
    def _analyze_documentation(self) -> None:
        """
        Analyze documentation to determine the purpose and context of files.
        """
        self.logger.info("Analyzing documentation")
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Skip binary files
            if file_info.get("binary", False):
                continue
            
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Extract documentation
                docstring = self._extract_docstring(content)
                references = self._extract_references(content)
                
                # Calculate documentation score
                doc_score = self._calculate_documentation_score(docstring, references)
                self.documentation_scores[file_path] = doc_score
                
                if doc_score > CONFIG["MIN_DOCUMENTATION_SCORE"]:
                    self.stats["files_with_documentation"] += 1
                    
            except Exception as e:
                self.logger.warning(f"Error analyzing documentation for {file_path}: {e}")
    
    def _extract_docstring(self, content: str) -> str:
        """
        Extract docstring from file content.
        
        Args:
            content: File content
            
        Returns:
            Extracted docstring or empty string if not found
        """
        # Try to parse as Python
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and ast.get_docstring(node):
                    return ast.get_docstring(node) or ""
        except SyntaxError:
            pass
        
        # Fallback to regex for non-Python files or if parsing failed
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1)
        
        return ""
    
    def _extract_references(self, content: str) -> List[str]:
        """
        Extract references from file content.
        
        Args:
            content: File content
            
        Returns:
            List of extracted references
        """
        references = []
        
        # Check for each reference pattern
        for pattern in CONFIG["DOCUMENTATION_PATTERNS"]:
            matches = re.findall(f'{pattern}\\s*([^\\n]+)', content)
            references.extend(matches)
        
        return references
    
    def _calculate_documentation_score(self, docstring: str, references: List[str]) -> float:
        """
        Calculate documentation score based on docstring and references.
        
        Args:
            docstring: Extracted docstring
            references: Extracted references
            
        Returns:
            Documentation score (0.0 to 1.0)
        """
        # Base score
        score = 0.0
        
        # Score for docstring
        if docstring:
            # Length factor (longer docstrings get higher scores, up to a point)
            length_factor = min(len(docstring) / 500, 1.0)
            
            # Quality factor (presence of key sections)
            quality_factor = 0.0
            if "Args:" in docstring or "Parameters:" in docstring:
                quality_factor += 0.2
            if "Returns:" in docstring:
                quality_factor += 0.2
            if "Examples:" in docstring:
                quality_factor += 0.2
            if "References:" in docstring:
                quality_factor += 0.2
            
            # Combine factors
            score += 0.5 * (length_factor + quality_factor)
        
        # Score for references
        if references:
            score += min(0.5, len(references) * 0.1)
        
        return min(score, 1.0)
    
    def _analyze_functional_groups(self) -> None:
        """
        Analyze functional groups based on imports and function calls.
        """
        self.logger.info("Analyzing functional groups")
        
        # Build import graph
        import_graph = self._build_import_graph()
        
        # Build function call graph
        function_call_graph = self._build_function_call_graph()
        
        # Combine graphs to identify functional groups
        self._identify_functional_groups(import_graph, function_call_graph)
    
    def _build_import_graph(self) -> Dict[str, Set[str]]:
        """
        Build import graph from file imports.
        
        Returns:
            Dictionary mapping file paths to sets of imported modules
        """
        import_graph = defaultdict(set)
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Skip binary files
            if file_info.get("binary", False):
                continue
            
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Extract imports
                for pattern in CONFIG["IMPORT_PATTERNS"]:
                    matches = re.findall(pattern, content)
                    import_graph[file_path].update(matches)
                    
            except Exception as e:
                self.logger.warning(f"Error building import graph for {file_path}: {e}")
        
        return import_graph
    
    def _build_function_call_graph(self) -> Dict[str, Set[str]]:
        """
        Build function call graph from file content.
        
        Returns:
            Dictionary mapping file paths to sets of function calls
        """
        function_call_graph = defaultdict(set)
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Skip binary files
            if file_info.get("binary", False):
                continue
            
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Extract function calls
                for pattern in CONFIG["FUNCTION_CALL_PATTERNS"]:
                    matches = re.findall(pattern, content)
                    function_call_graph[file_path].update(matches)
                    
            except Exception as e:
                self.logger.warning(f"Error building function call graph for {file_path}: {e}")
        
        return function_call_graph
    
    def _identify_functional_groups(self, import_graph: Dict[str, Set[str]], function_call_graph: Dict[str, Set[str]]) -> None:
        """
        Identify functional groups based on import and function call graphs.
        
        Args:
            import_graph: Import graph
            function_call_graph: Function call graph
        """
        # Initialize functional groups
        functional_groups = defaultdict(set)
        
        # Group files by common imports
        import_groups = defaultdict(set)
        for file_path, imports in import_graph.items():
            for import_name in imports:
                import_groups[import_name].add(file_path)
        
        # Group files by common function calls
        function_groups = defaultdict(set)
        for file_path, function_calls in function_call_graph.items():
            for function_name in function_calls:
                function_groups[function_name].add(file_path)
        
        # Combine groups
        group_id = 0
        for group_name, files in import_groups.items():
            if len(files) > 1:
                functional_groups[f"group_{group_id}"] = files
                group_id += 1
        
        for group_name, files in function_groups.items():
            if len(files) > 1:
                functional_groups[f"group_{group_id}"] = files
                group_id += 1
        
        # Merge overlapping groups
        merged_groups = self._merge_overlapping_groups(functional_groups)
        
        # Store functional groups
        self.functional_groups = merged_groups
        self.stats["functional_groups_identified"] = len(merged_groups)
    
    def _merge_overlapping_groups(self, groups: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """
        Merge overlapping groups.
        
        Args:
            groups: Dictionary mapping group IDs to sets of file paths
            
        Returns:
            Dictionary with merged groups
        """
        merged_groups = {}
        merged = True
        
        # Copy groups
        current_groups = groups.copy()
        
        # Merge until no more merges are possible
        while merged:
            merged = False
            new_groups = {}
            processed_groups = set()
            
            for group_id1, files1 in current_groups.items():
                if group_id1 in processed_groups:
                    continue
                
                merged_files = files1.copy()
                merged_with = [group_id1]
                
                for group_id2, files2 in current_groups.items():
                    if group_id1 != group_id2 and group_id2 not in processed_groups:
                        # Check for overlap
                        if files1.intersection(files2):
                            merged_files.update(files2)
                            merged_with.append(group_id2)
                            processed_groups.add(group_id2)
                            merged = True
                
                processed_groups.add(group_id1)
                new_group_id = "_".join(merged_with)
                new_groups[new_group_id] = merged_files
            
            current_groups = new_groups
        
        # Rename groups
        for i, (group_id, files) in enumerate(current_groups.items()):
            merged_groups[f"functional_group_{i}"] = files
        
        return merged_groups
    
    def _analyze_semantic_relationships(self) -> None:
        """
        Analyze semantic relationships between files.
        """
        self.logger.info("Analyzing semantic relationships")
        
        # For simplicity, we'll use a basic approach based on filename similarity
        # In a real implementation, this would use more sophisticated NLP techniques
        
        for i, file_info1 in enumerate(self.files):
            file_path1 = file_info1["full_path"]
            file_name1 = file_info1["name"]
            
            for file_info2 in self.files[i+1:]:
                file_path2 = file_info2["full_path"]
                file_name2 = file_info2["name"]
                
                # Calculate similarity
                similarity = self._calculate_filename_similarity(file_name1, file_name2)
                
                # Store if above threshold
                if similarity > CONFIG["SEMANTIC_SIMILARITY_THRESHOLD"]:
                    if file_path1 not in self.semantic_relationships:
                        self.semantic_relationships[file_path1] = []
                    
                    self.semantic_relationships[file_path1].append({
                        "file_path": file_path2,
                        "similarity": similarity
                    })
                    
                    self.stats["semantic_relationships_found"] += 1
    
    def _calculate_filename_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two filenames.
        
        Args:
            name1: First filename
            name2: Second filename
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Remove extension
        base1 = os.path.splitext(name1)[0]
        base2 = os.path.splitext(name2)[0]
        
        # Split into words
        words1 = set(re.findall(r'[a-z]+', base1.lower()))
        words2 = set(re.findall(r'[a-z]+', base2.lower()))
        
        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union
    
    def _identify_orphaned_files(self) -> None:
        """
        Identify orphaned files (not referenced and not referencing).
        """
        self.logger.info("Identifying orphaned files")
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Check if file is referenced by other files
            is_referenced = file_path in self.inbound_references and self.inbound_references[file_path]
            
            # Check if file references other files
            has_references = file_path in self.outbound_references and self.outbound_references[file_path]
            
            # Check if file has documentation
            has_documentation = file_path in self.documentation_scores and self.documentation_scores[file_path] > CONFIG["MIN_DOCUMENTATION_SCORE"]
            
            # Check if file is part of a functional group
            in_functional_group = any(file_path in group for group in self.functional_groups.values())
            
            # Check if file has semantic relationships
            has_semantic_relationships = file_path in self.semantic_relationships and self.semantic_relationships[file_path]
            
            # Mark as orphaned if not connected in any way
            if not (is_referenced or has_references or has_documentation or in_functional_group or has_semantic_relationships):
                self.orphaned_files.add(file_path)
                self.stats["orphaned_files"] += 1
    
    def _calculate_context_scores(self) -> None:
        """
        Calculate context scores for files based on various factors.
        """
        self.logger.info("Calculating context scores")
        
        for file_info in self.files:
            file_path = file_info["full_path"]
            
            # Initialize score components
            reference_score = 0.0
            documentation_score = 0.0
            functional_score = 0.0
            semantic_score = 0.0
            
            # Reference score (0.0 to 0.3)
            inbound_count = len(self.inbound_references.get(file_path, []))
            outbound_count = len(self.outbound_references.get(file_path, []))
            reference_score = min(0.3, (inbound_count + outbound_count) * 0.05)
            
            # Documentation score (0.0 to 0.3)
            documentation_score = min(0.3, self.documentation_scores.get(file_path, 0.0))
            
            # Functional score (0.0 to 0.2)
            functional_score = 0.2 if any(file_path in group for group in self.functional_groups.values()) else 0.0
            
            # Semantic score (0.0 to 0.2)
            if file_path in self.semantic_relationships:
                semantic_score = min(0.2, len(self.semantic_relationships[file_path]) * 0.05)
            
            # Calculate total score
            total_score = reference_score + documentation_score + functional_score + semantic_score
            
            # Store score
            self.context_scores[file_path] = {
                "total": total_score,
                "reference": reference_score,
                "documentation": documentation_score,
                "functional": functional_score,
                "semantic": semantic_score,
                "is_orphaned": file_path in self.orphaned_files
            }
    
    def _update_statistics(self) -> None:
        """
        Update statistics based on analysis results.
        """
        # Statistics are already updated during analysis
        pass
    
    def _prepare_results(self) -> Dict[str, Any]:
        """
        Prepare context analysis results for return.
        
        Returns:
            Dictionary with context analysis results
        """
        return {
            "documentation_scores": self.documentation_scores,
            "functional_groups": self.functional_groups,
            "semantic_relationships": self.semantic_relationships,
            "orphaned_files": list(self.orphaned_files),
            "context_scores": self.context_scores,
            "stats": self.stats
        }


def main():
    """Main function for testing the ContextAnalyzer module."""
    import argparse
    import json
    
    # Print banner
    print_banner("Context Analyzer Module")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Context Analyzer Module for Directory Unification Tool")
    parser.add_argument("--egos-root", help="Path to EGOS root directory")
    parser.add_argument("--content-file", required=True, help="Path to content discovery JSON file")
    parser.add_argument("--references-file", required=True, help="Path to cross-reference analysis JSON file")
    parser.add_argument("--output", help="Output file for results (JSON format)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Convert arguments to dictionary
    args_dict = vars(args)
    
    # Load content discovery data
    with open(args.content_file, "r", encoding="utf-8") as f:
        content_data = json.load(f)
    
    # Load cross-reference analysis data
    with open(args.references_file, "r", encoding="utf-8") as f:
        references_data = json.load(f)
    
    # Create context
    context = {
        "content": content_data,
        "references": references_data
    }
    
    # Set up logger
    logger = setup_logger("context_analyzer", "%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging.DEBUG if args.verbose else logging.INFO)
    
    # Create ContextAnalyzer instance
    analyzer = ContextAnalyzer(args_dict, context, logger)
    
    # Analyze context
    results = analyzer.analyze_context()
    
    # Display summary
    print(f"\n{Fore.CYAN}Context Analysis Results:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Files analyzed:{Style.RESET_ALL} {results['stats']['total_files_analyzed']}")
    print(f"  {Fore.GREEN}Files with documentation:{Style.RESET_ALL} {results['stats']['files_with_documentation']}")
    print(f"  {Fore.GREEN}Functional groups identified:{Style.RESET_ALL} {results['stats']['functional_groups_identified']}")
    print(f"  {Fore.GREEN}Semantic relationships found:{Style.RESET_ALL} {results['stats']['semantic_relationships_found']}")
    print(f"  {Fore.GREEN}Orphaned files:{Style.RESET_ALL} {results['stats']['orphaned_files']}")
    
    # Output results to file if specified
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{Fore.GREEN}Results saved to {args.output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    main()