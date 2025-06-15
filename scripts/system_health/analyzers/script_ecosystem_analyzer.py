#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Script Ecosystem Analyzer

This script analyzes the distribution and health of scripts and documentation across 
the EGOS system, creating a "heat map" visualization that identifies:
- Isolated scripts (scripts in directories with few other scripts)
- Potentially orphaned scripts (low cross-references, no recent modifications)
- Underdeveloped areas (directories with few scripts)
- Documentation health (documentation without clear purpose or references)

The tool generates comprehensive reports in markdown format with visualizations
to help identify areas that need attention or consolidation. It also provides
special analysis of the CORUJA subsystem (human-AI connection) and website integration.

@author: EGOS Development Team
@date: 2025-05-26
@version: 0.1.1

@references:
- C:\EGOS\MQP.md (Systemic Cartography, Evolutionary Preservation)
- C:\EGOS\docs\planning\health_check_unification_plan.md
- C:\EGOS\website\content\roadmap.md
- C:\EGOS\subsystems\coruja\README.md
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
import re
import logging
import json
import datetime
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any, Optional, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("script_ecosystem_analyzer")

# Constants
SCRIPT_EXTENSIONS = ['.py', '.sh', '.bat', '.ps1', '.js', '.ts', '.rb']
DOC_EXTENSIONS = ['.md', '.txt', '.rst', '.html', '.pdf', '.docx']
DEFAULT_EXCLUSIONS = [
    '.git', 'venv', '.venv', 'env', 'node_modules', '__pycache__', 
    '.vscode', '.idea', 'build', 'dist', '.pytest_cache'
]
XREF_PATTERN = r'(?:file://|C:\\|/)[A-Za-z0-9_\-\.\/\\]+'
IMPORT_PATTERN = r'^\s*(?:import|from)\s+([A-Za-z0-9_\.]+)'
FUNCTION_PATTERN = r'^\s*def\s+([A-Za-z0-9_]+)'
CLASS_PATTERN = r'^\s*class\s+([A-Za-z0-9_]+)'

class ScriptEcosystemAnalyzer:
    """Analyzer for script and documentation ecosystem."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the analyzer with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        # Default configuration
        self.default_config = {
            "exclusions": DEFAULT_EXCLUSIONS,
            "script_extensions": SCRIPT_EXTENSIONS,
            "doc_extensions": DOC_EXTENSIONS,
            "max_age_days": 180,  # Scripts older than this are considered potentially obsolete
            "min_references": 1,  # Scripts with fewer references are potentially orphaned
            "min_scripts_per_dir": 3,  # Directories with fewer scripts are potentially underdeveloped
            "visualization": {
                "enabled": True,
                "max_depth": 4,  # Maximum directory depth to show in visualization
                "heat_scale": ["❄️", "🔵", "🟢", "🟡", "🔴", "🔥"]  # Cold to hot
            }
        }
        
        # Merge with provided config
        self.config = self.default_config.copy()
        if config:
            self._merge_config(self.config, config)
        
        # Initialize data structures
        self.scripts = {}  # path -> metadata
        self.docs = {}  # path -> metadata
        self.directories = defaultdict(list)  # dir -> [files]
        self.references = defaultdict(set)  # path -> {referenced_by}
        self.imports = defaultdict(set)  # module -> {imported_by}
        self.modification_times = {}  # path -> timestamp
        self.script_density = {}  # dir -> count
        self.doc_density = {}  # dir -> count
        self.orphaned_scripts = []  # list of potentially orphaned scripts
        self.isolated_scripts = []  # list of isolated scripts
        self.underdeveloped_areas = []  # list of underdeveloped directories
        self.obsolete_candidates = []  # list of potentially obsolete scripts
        self.docs_without_purpose = []  # list of docs without clear purpose
    
    def _merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to override base
            
        Returns:
            Merged configuration
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
        return base_config
    
    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on exclusion rules.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        # Check directory exclusions
        for part in path.parts:
            if part in self.config["exclusions"]:
                return True
        
        return False
    
    def is_script(self, path: Path) -> bool:
        """Check if a path is a script file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a script file, False otherwise
        """
        return path.suffix.lower() in self.config["script_extensions"]
    
    def is_doc(self, path: Path) -> bool:
        """Check if a path is a documentation file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a documentation file, False otherwise
        """
        return path.suffix.lower() in self.config["doc_extensions"]
    
    def scan_directory(self, directory: Union[str, Path]) -> None:
        """Scan a directory for scripts and documentation.
        
        Args:
            directory: Directory to scan
        """
        directory = Path(directory)
        logger.info(f"Scanning directory: {directory}")
        
        # Walk the directory tree
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d)]
            
            root_path = Path(root)
            
            # Process files
            for file_name in files:
                file_path = root_path / file_name
                
                # Skip excluded files
                if self.should_exclude(file_path):
                    continue
                
                # Get file metadata
                try:
                    stat = file_path.stat()
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                    self.modification_times[str(file_path)] = mtime
                    
                    # Track files by directory
                    self.directories[str(root_path)].append(str(file_path))
                    
                    # Process scripts
                    if self.is_script(file_path):
                        self.scripts[str(file_path)] = {
                            "path": str(file_path),
                            "name": file_name,
                            "directory": str(root_path),
                            "size": stat.st_size,
                            "modified": mtime,
                            "references": [],
                            "imports": [],
                            "functions": [],
                            "classes": []
                        }
                    
                    # Process documentation
                    elif self.is_doc(file_path):
                        self.docs[str(file_path)] = {
                            "path": str(file_path),
                            "name": file_name,
                            "directory": str(root_path),
                            "size": stat.st_size,
                            "modified": mtime,
                            "references": [],
                            "has_purpose": False
                        }
                
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
        
        # Calculate script and doc density by directory
        for dir_path, files in self.directories.items():
            script_count = sum(1 for f in files if Path(f).suffix.lower() in self.config["script_extensions"])
            doc_count = sum(1 for f in files if Path(f).suffix.lower() in self.config["doc_extensions"])
            
            self.script_density[dir_path] = script_count
            self.doc_density[dir_path] = doc_count
    
    def analyze_scripts(self) -> None:
        """Analyze script files for imports, references, functions, and classes."""
        logger.info(f"Analyzing {len(self.scripts)} script files")
        
        for path, metadata in self.scripts.items():
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Find cross-references
                    refs = re.findall(XREF_PATTERN, content)
                    metadata["references"] = refs
                    
                    # Track references
                    for ref in refs:
                        ref_path = ref.replace('file://', '').replace('\\', '/').strip()
                        self.references[ref_path].add(path)
                    
                    # Find imports
                    lines = content.split('\n')
                    for line in lines:
                        # Find imports
                        import_match = re.search(IMPORT_PATTERN, line)
                        if import_match:
                            module = import_match.group(1)
                            metadata["imports"].append(module)
                            self.imports[module].add(path)
                        
                        # Find functions
                        func_match = re.search(FUNCTION_PATTERN, line)
                        if func_match:
                            metadata["functions"].append(func_match.group(1))
                        
                        # Find classes
                        class_match = re.search(CLASS_PATTERN, line)
                        if class_match:
                            metadata["classes"].append(class_match.group(1))
            
            except Exception as e:
                logger.warning(f"Error analyzing script {path}: {e}")
    
    def analyze_docs(self) -> None:
        """Analyze documentation files for references and purpose."""
        logger.info(f"Analyzing {len(self.docs)} documentation files")
        
        purpose_keywords = [
            "purpose", "objective", "goal", "aim", "intent", "function",
            "role", "task", "mission", "responsibility", "description"
        ]
        
        # Maximum file size to read completely (10 MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        for path, metadata in self.docs.items():
            try:
                # Get file size
                file_size = os.path.getsize(path)
                
                # Skip files that are too large
                if file_size > MAX_FILE_SIZE:
                    logger.info(f"Skipping large file {path} ({file_size / 1024 / 1024:.2f} MB)")
                    metadata["references"] = []
                    metadata["has_purpose"] = False
                    metadata["skipped_due_to_size"] = True
                    continue
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Read file in chunks to avoid memory issues
                    content = ""
                    chunk_size = 1024 * 1024  # 1 MB chunks
                    
                    # Read first chunk for analysis
                    content = f.read(chunk_size).lower()
                    
                    # Find cross-references
                    refs = re.findall(XREF_PATTERN, content)
                    metadata["references"] = refs
                    
                    # Track references
                    for ref in refs:
                        ref_path = ref.replace('file://', '').replace('\\', '/').strip()
                        self.references[ref_path].add(path)
                    
                    # Check for purpose statements
                    metadata["has_purpose"] = any(keyword in content for keyword in purpose_keywords)
            
            except KeyboardInterrupt:
                logger.warning("Analysis interrupted by user")
                raise
            except Exception as e:
                logger.warning(f"Error analyzing doc {path}: {e}")
    
    def identify_issues(self) -> None:
        """Identify potential issues with scripts and documentation."""
        logger.info("Identifying potential issues")
        
        now = datetime.datetime.now()
        max_age = datetime.timedelta(days=self.config["max_age_days"])
        min_references = self.config["min_references"]
        min_scripts_per_dir = self.config["min_scripts_per_dir"]
        
        # Identify potentially obsolete scripts
        for path, metadata in self.scripts.items():
            age = now - metadata["modified"]
            if age > max_age:
                self.obsolete_candidates.append({
                    "path": path,
                    "age_days": age.days,
                    "last_modified": metadata["modified"].strftime("%Y-%m-%d")
                })
        
        # Identify potentially orphaned scripts (few references)
        for path, metadata in self.scripts.items():
            ref_count = len(self.references.get(path.replace('\\', '/'), set()))
            if ref_count < min_references:
                self.orphaned_scripts.append({
                    "path": path,
                    "reference_count": ref_count,
                    "last_modified": metadata["modified"].strftime("%Y-%m-%d")
                })
        
        # Identify isolated scripts (in directories with few scripts)
        for dir_path, script_count in self.script_density.items():
            if 0 < script_count < min_scripts_per_dir:
                self.underdeveloped_areas.append({
                    "directory": dir_path,
                    "script_count": script_count,
                    "doc_count": self.doc_density.get(dir_path, 0)
                })
                
                # Add scripts in underdeveloped areas to isolated scripts list
                for path in self.directories[dir_path]:
                    if path in self.scripts:
                        self.isolated_scripts.append({
                            "path": path,
                            "directory": dir_path,
                            "directory_script_count": script_count
                        })
        
        # Identify documentation without clear purpose
        for path, metadata in self.docs.items():
            if not metadata["has_purpose"]:
                self.docs_without_purpose.append({
                    "path": path,
                    "reference_count": len(self.references.get(path.replace('\\', '/'), set())),
                    "last_modified": metadata["modified"].strftime("%Y-%m-%d")
                })
    
    def generate_directory_tree(self, root_dir: Union[str, Path], max_depth: int = 4) -> Dict[str, Any]:
        """Generate a directory tree structure for visualization.
        
        Args:
            root_dir: Root directory
            max_depth: Maximum depth to traverse
            
        Returns:
            Directory tree structure
        """
        root_dir = Path(root_dir)
        
        def _build_tree(directory: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {"name": directory.name, "type": "directory", "truncated": True}
            
            result = {
                "name": directory.name,
                "path": str(directory),
                "type": "directory",
                "children": [],
                "script_count": self.script_density.get(str(directory), 0),
                "doc_count": self.doc_density.get(str(directory), 0)
            }
            
            try:
                # Add subdirectories
                for item in directory.iterdir():
                    if item.is_dir() and not self.should_exclude(item):
                        child = _build_tree(item, current_depth + 1)
                        result["children"].append(child)
                
                # Sort children by name
                result["children"].sort(key=lambda x: x["name"])
                
                return result
            
            except Exception as e:
                logger.warning(f"Error building tree for {directory}: {e}")
                return {
                    "name": directory.name,
                    "path": str(directory),
                    "type": "directory",
                    "error": str(e)
                }
        
        return _build_tree(root_dir)
    
    def generate_heat_map(self, tree: Dict[str, Any]) -> str:
        """Generate a heat map visualization of the directory tree.
        
        Args:
            tree: Directory tree structure
            
        Returns:
            Markdown representation of the heat map
        """
        heat_scale = self.config["visualization"]["heat_scale"]
        max_scripts = max(self.script_density.values()) if self.script_density else 1
        
        def _get_heat_icon(script_count: int) -> str:
            if script_count == 0:
                return heat_scale[0]  # Cold
            
            # Normalize to 0-1 range and map to heat scale
            normalized = min(script_count / max_scripts, 1.0)
            index = min(int(normalized * (len(heat_scale) - 1)), len(heat_scale) - 1)
            return heat_scale[index]
        
        def _format_tree(node: Dict[str, Any], prefix: str = "", is_last: bool = True, depth: int = 0) -> List[str]:
            lines = []
            
            # Skip root node
            if depth > 0:
                script_count = node.get("script_count", 0)
                doc_count = node.get("doc_count", 0)
                heat_icon = _get_heat_icon(script_count)
                
                connector = "└── " if is_last else "├── "
                line = f"{prefix}{connector}{heat_icon} {node['name']} ({script_count} scripts, {doc_count} docs)"
                lines.append(line)
            
            # Process children
            if "children" in node:
                # Sort children by script count (descending)
                children = sorted(node["children"], key=lambda x: x.get("script_count", 0), reverse=True)
                
                # Determine new prefix for children
                new_prefix = prefix
                if depth > 0:
                    new_prefix += "    " if is_last else "│   "
                
                # Process each child
                for i, child in enumerate(children):
                    is_last_child = i == len(children) - 1
                    lines.extend(_format_tree(child, new_prefix, is_last_child, depth + 1))
            
            return lines
        
        # Generate tree lines
        tree_lines = _format_tree(tree)
        
        # Add legend
        legend = [
            "\n### Heat Map Legend",
            "Temperature indicates script density:",
            " ".join(f"{icon} " for icon in heat_scale),
            "Cold ←────────────────→ Hot"
        ]
        
        return "\n".join(tree_lines + [""] + legend)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate a comprehensive report of the analysis.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Markdown report content
        """
        logger.info("Generating report")
        
        # Build report sections
        sections = []
        
        # Header
        sections.append("# EGOS Script Ecosystem Analysis Report")
        sections.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        
        # Summary
        sections.append("## Summary")
        sections.append(f"- Total scripts analyzed: {len(self.scripts)}")
        sections.append(f"- Total documentation files analyzed: {len(self.docs)}")
        sections.append(f"- Directories analyzed: {len(self.directories)}")
        sections.append(f"- Potentially obsolete scripts: {len(self.obsolete_candidates)}")
        sections.append(f"- Potentially orphaned scripts: {len(self.orphaned_scripts)}")
        sections.append(f"- Isolated scripts: {len(self.isolated_scripts)}")
        sections.append(f"- Underdeveloped areas: {len(self.underdeveloped_areas)}")
        sections.append(f"- Documentation without clear purpose: {len(self.docs_without_purpose)}")
        sections.append("")
        
        # Heat Map Visualization
        if self.config["visualization"]["enabled"]:
            sections.append("## Script Ecosystem Heat Map")
            sections.append("This visualization shows the distribution of scripts across the directory structure.")
            sections.append("Hotter colors indicate higher script density.")
            sections.append("")
            
            # Generate directory tree and heat map
            root_dir = next(iter(self.directories.keys())).split(os.path.sep)[0] if self.directories else "."
            tree = self.generate_directory_tree(root_dir, self.config["visualization"]["max_depth"])
            heat_map = self.generate_heat_map(tree)
            sections.append(heat_map)
            sections.append("")
        
        # Script Density by Directory
        sections.append("## Script Density by Directory")
        sections.append("| Directory | Script Count | Doc Count |")
        sections.append("|-----------|--------------|-----------|")
        
        # Sort directories by script count (descending)
        sorted_dirs = sorted(self.script_density.items(), key=lambda x: x[1], reverse=True)
        for dir_path, count in sorted_dirs:
            doc_count = self.doc_density.get(dir_path, 0)
            sections.append(f"| {dir_path} | {count} | {doc_count} |")
        
        sections.append("")
        
        # Potentially Obsolete Scripts
        if self.obsolete_candidates:
            sections.append("## Potentially Obsolete Scripts")
            sections.append("These scripts have not been modified in a long time and may be obsolete.")
            sections.append("")
            sections.append("| Script | Last Modified | Age (days) |")
            sections.append("|--------|---------------|------------|")
            
            # Sort by age (descending)
            sorted_obsolete = sorted(self.obsolete_candidates, key=lambda x: x["age_days"], reverse=True)
            for item in sorted_obsolete:
                sections.append(f"| {item['path']} | {item['last_modified']} | {item['age_days']} |")
            
            sections.append("")
        
        # Potentially Orphaned Scripts
        if self.orphaned_scripts:
            sections.append("## Potentially Orphaned Scripts")
            sections.append("These scripts have few or no references from other files.")
            sections.append("")
            sections.append("| Script | Reference Count | Last Modified |")
            sections.append("|--------|----------------|---------------|")
            
            # Sort by reference count (ascending)
            sorted_orphaned = sorted(self.orphaned_scripts, key=lambda x: x["reference_count"])
            for item in sorted_orphaned:
                sections.append(f"| {item['path']} | {item['reference_count']} | {item['last_modified']} |")
            
            sections.append("")
        
        # Underdeveloped Areas
        if self.underdeveloped_areas:
            sections.append("## Underdeveloped Areas")
            sections.append("These directories have few scripts and may be underdeveloped or isolated.")
            sections.append("")
            sections.append("| Directory | Script Count | Doc Count |")
            sections.append("|-----------|--------------|-----------|")
            
            # Sort by script count (ascending)
            sorted_areas = sorted(self.underdeveloped_areas, key=lambda x: x["script_count"])
            for item in sorted_areas:
                sections.append(f"| {item['directory']} | {item['script_count']} | {item['doc_count']} |")
            
            sections.append("")
        
        # Isolated Scripts
        if self.isolated_scripts:
            sections.append("## Isolated Scripts")
            sections.append("These scripts are in directories with few other scripts.")
            sections.append("")
            sections.append("| Script | Directory | Directory Script Count |")
            sections.append("|--------|-----------|------------------------|")
            
            # Sort by directory script count (ascending)
            sorted_isolated = sorted(self.isolated_scripts, key=lambda x: x["directory_script_count"])
            for item in sorted_isolated:
                sections.append(f"| {item['path']} | {item['directory']} | {item['directory_script_count']} |")
            
            sections.append("")
        
        # Documentation Without Clear Purpose
        if self.docs_without_purpose:
            sections.append("## Documentation Without Clear Purpose")
            sections.append("These documentation files do not have a clear purpose statement.")
            sections.append("")
            sections.append("| Documentation | Reference Count | Last Modified | Notes |")
            sections.append("|--------------|----------------|---------------|-------|")
            
            # Sort by reference count (ascending)
            sorted_docs = sorted(self.docs_without_purpose, key=lambda x: x["reference_count"])
            for item in sorted_docs:
                skipped = "Skipped due to size" if item.get("skipped_due_to_size", False) else ""
                sections.append(f"| {item['path']} | {item['reference_count']} | {item['last_modified']} | {skipped} |")
            
            sections.append("")
            
        # CORUJA Subsystem Integration
        sections.append("## CORUJA Subsystem Integration")
        sections.append("The CORUJA subsystem is responsible for human-AI connections and is a critical component of the EGOS ecosystem.")
        sections.append("This section highlights connections between scripts and the CORUJA subsystem.")
        sections.append("")
        
        # Find CORUJA-related scripts
        coruja_scripts = [path for path in self.scripts.keys() if "coruja" in path.lower()]
        if coruja_scripts:
            sections.append("### CORUJA Scripts")
            sections.append("| Script | Last Modified | Reference Count |")
            sections.append("|--------|---------------|----------------|")
            
            for path in coruja_scripts:
                metadata = self.scripts[path]
                ref_count = len(self.references.get(path.replace('\\', '/'), set()))
                last_modified = metadata["modified"].strftime("%Y-%m-%d")
                sections.append(f"| {path} | {last_modified} | {ref_count} |")
            
            sections.append("")
        
        # Website Integration
        sections.append("## Website Integration")
        sections.append("The EGOS website serves as the visual representation of our progress and capabilities.")
        sections.append("This section highlights connections between scripts and the website.")
        sections.append("")
        
        # Find website-related scripts
        website_scripts = [path for path in self.scripts.keys() if "website" in path.lower()]
        if website_scripts:
            sections.append("### Website Scripts")
            sections.append("| Script | Last Modified | Reference Count |")
            sections.append("|--------|---------------|----------------|")
            
            for path in website_scripts:
                metadata = self.scripts[path]
                ref_count = len(self.references.get(path.replace('\\', '/'), set()))
                last_modified = metadata["modified"].strftime("%Y-%m-%d")
                sections.append(f"| {path} | {last_modified} | {ref_count} |")
            
            sections.append("")
        
        # Join sections
        report = "\n".join(sections)
        
        # Save report if output path provided
        if output_path:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Write report
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                logger.info(f"Report saved to {output_path}")
            
            except Exception as e:
                logger.error(f"Error saving report: {e}")
        
        return report
    
    def analyze(self, target_path: Union[str, Path]) -> Dict[str, Any]:
        """Run the complete analysis process.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Analysis results
        """
        # Scan directory
        self.scan_directory(target_path)
        
        # Analyze scripts and docs
        self.analyze_scripts()
        self.analyze_docs()
        
        # Identify issues
        self.identify_issues()
        
        # Return results
        return {
            "scripts": self.scripts,
            "docs": self.docs,
            "script_density": self.script_density,
            "doc_density": self.doc_density,
            "obsolete_candidates": self.obsolete_candidates,
            "orphaned_scripts": self.orphaned_scripts,
            "isolated_scripts": self.isolated_scripts,
            "underdeveloped_areas": self.underdeveloped_areas,
            "docs_without_purpose": self.docs_without_purpose
        }

def print_banner():
    """Print a banner for the script ecosystem analyzer."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║             EGOS Script Ecosystem Analyzer                    ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main function for running the script ecosystem analyzer from the command line."""
    parser = argparse.ArgumentParser(description="EGOS Script Ecosystem Analyzer")
    parser.add_argument("target_path", nargs="?", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        help="Path to analyze (default: EGOS root directory)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Path to save the report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--max-file-size", type=int, default=10, 
                        help="Maximum file size in MB to analyze (default: 10)")
    parser.add_argument("--website-integration", action="store_true", 
                        help="Generate website integration files")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print_banner()
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    else:
        # Create default configuration
        config = {
            "exclusions": DEFAULT_EXCLUSIONS,
            "script_extensions": SCRIPT_EXTENSIONS,
            "doc_extensions": DOC_EXTENSIONS,
            "max_age_days": 180,
            "min_references": 1,
            "min_scripts_per_dir": 3,
            "max_file_size_mb": args.max_file_size,
            "visualization": {
                "enabled": True,
                "max_depth": 4,
                "heat_scale": ["❄️", "🔵", "🟢", "🟡", "🔴", "🔥"]
            }
        }
    
    try:
        # Create analyzer
        analyzer = ScriptEcosystemAnalyzer(config)
        
        # Run analysis
        logger.info(f"Analyzing {args.target_path}")
        analyzer.analyze(args.target_path)
        
        # Generate report
        output_path = args.output
        if not output_path:
            # Generate default output path
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"script_ecosystem_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        report = analyzer.generate_report(output_path)
        
        # Generate website integration files if requested
        if args.website_integration:
            website_dir = os.path.join(args.target_path, "website", "content", "reports")
            os.makedirs(website_dir, exist_ok=True)
            website_path = os.path.join(website_dir, f"script_ecosystem_report.md")
            
            # Add frontmatter for website integration
            frontmatter = [
                "---",
                "title: 'EGOS Script Ecosystem Analysis'",
                f"date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
                "author: 'EGOS System'",
                "description: 'Analysis of the EGOS script ecosystem, identifying hot and cold areas of development.'",
                "categories: ['reports', 'system-health']",
                "tags: ['scripts', 'analysis', 'health-check', 'documentation']",
                "---",
                ""
            ]
            
            # Write to website directory
            with open(website_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(frontmatter) + report)
            
            logger.info(f"Website integration file saved to {website_path}")
        
        logger.info(f"Analysis complete. Report saved to {output_path}")
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Analysis interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())