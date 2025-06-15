#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""KOIOS Chronicler Module - Codebase Analyzer

This module is responsible for analyzing a codebase directory, including:
- Directory scanning and file enumeration
- File filtering based on .gitignore and configuration
- Language detection and statistics gathering
- Basic code structure analysis

Part of the KOIOS subsystem within EGOS.

Author: EGOS Team
Date Created: 2025-04-22
Last Modified: 2025-05-18

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import re
import logging
import fnmatch
from typing import Dict, List, Any, Set, Optional
from pathlib import Path
import json

# Constants
DEFAULT_EXCLUSIONS = [
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    "venv", ".venv", "env", ".env",
    "node_modules", "dist", "build",
    ".git", ".svn", ".hg",
    "*.min.js", "*.min.css",
    "*.log", "*.tmp", "*.temp",
    ".DS_Store", "Thumbs.db"
]

# Language extensions mapping
LANGUAGE_EXTENSIONS = {
    # Programming languages
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "jsx": "React JSX",
    "tsx": "React TSX",
    "html": "HTML",
    "css": "CSS",
    "scss": "SCSS",
    "sass": "Sass",
    "less": "Less",
    "java": "Java",
    "c": "C",
    "cpp": "C++",
    "cs": "C#",
    "go": "Go",
    "rb": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kt": "Kotlin",
    "rs": "Rust",
    "scala": "Scala",
    "sh": "Shell",
    "ps1": "PowerShell",
    "bat": "Batch",
    "r": "R",
    "dart": "Dart",
    "lua": "Lua",
    "sql": "SQL",
    
    # Data formats
    "json": "JSON",
    "yaml": "YAML",
    "yml": "YAML",
    "xml": "XML",
    "csv": "CSV",
    "md": "Markdown",
    "txt": "Text",
    "ini": "INI",
    "toml": "TOML",
    
    # Documentation
    "rst": "reStructuredText",
    "tex": "LaTeX",
    "pdf": "PDF",
    "docx": "Word",
    "xlsx": "Excel",
    "pptx": "PowerPoint"
}


class CodebaseAnalyzer:
    """
    Analyzes a codebase directory to extract information about its structure,
    languages, and files.
    """
    
    def __init__(self, project_dir: str, config: Dict[str, Any]):
        """
        Initialize the CodebaseAnalyzer.
        
        Args:
            project_dir: Path to the project directory to analyze
            config: Configuration dictionary
        """
        self.project_dir = os.path.abspath(project_dir)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get exclusions from config or use defaults
        self.exclusions = config.get('exclusions', DEFAULT_EXCLUSIONS)
        self.logger.info(f"Initialized analyzer for {self.project_dir}")
        self.logger.debug(f"Using exclusions: {self.exclusions}")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the codebase and return structured results.
        
        Returns:
            Dictionary containing analysis results
        """
        self.logger.info("Starting codebase analysis...")
        
        # Results structure
        results = {
            "project_name": os.path.basename(self.project_dir),
            "project_path": self.project_dir,
            "files": [],
            "directories": [],
            "languages": {},
            "file_count": 0,
            "total_size": 0,
            "gitignore_rules": self._parse_gitignore()
        }
        
        # Walk the directory
        for root, dirs, files in os.walk(self.project_dir):
            # Apply exclusions to directories (modify dirs in place to affect walk)
            dirs[:] = [d for d in dirs if not self._should_exclude(d, root)]
            
            # Process this directory
            rel_dir = os.path.relpath(root, self.project_dir)
            if rel_dir != ".":  # Don't add the root directory
                results["directories"].append({
                    "path": rel_dir,
                    "name": os.path.basename(root)
                })
            
            # Process files in this directory
            for file in files:
                if self._should_exclude(file, root):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_dir)
                
                # Get file stats
                try:
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(file)[1].lstrip('.').lower()
                    language = LANGUAGE_EXTENSIONS.get(file_ext, "Unknown")
                    
                    # Update language statistics
                    if language in results["languages"]:
                        results["languages"][language]["count"] += 1
                        results["languages"][language]["size"] += file_size
                    else:
                        results["languages"][language] = {
                            "count": 1,
                            "size": file_size,
                            "extensions": [file_ext] if file_ext else []
                        }
                    
                    # Add file to results
                    results["files"].append({
                        "name": file,
                        "path": rel_path,
                        "size": file_size,
                        "extension": file_ext,
                        "language": language
                    })
                    
                    # Update totals
                    results["file_count"] += 1
                    results["total_size"] += file_size
                    
                except Exception as e:
                    self.logger.warning(f"Error processing file {file_path}: {e}")
        
        # Sort languages by file count
        results["languages"] = dict(sorted(
            results["languages"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        ))
        
        self.logger.info(f"Analysis complete. Found {results['file_count']} files "
                         f"in {len(results['directories'])} directories.")
        return results
    
    def _parse_gitignore(self) -> List[str]:
        """
        Parse .gitignore file if it exists.
        
        Returns:
            List of gitignore patterns
        """
        gitignore_path = os.path.join(self.project_dir, ".gitignore")
        patterns = []
        
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
                self.logger.info(f"Parsed .gitignore with {len(patterns)} patterns")
            except Exception as e:
                self.logger.warning(f"Error parsing .gitignore: {e}")
        
        return patterns
    
    def _should_exclude(self, name: str, parent_dir: str) -> bool:
        """
        Check if a file or directory should be excluded based on exclusion patterns.
        
        Args:
            name: Name of the file or directory
            parent_dir: Parent directory path
            
        Returns:
            True if the item should be excluded, False otherwise
        """
        # Check against explicit exclusions
        for pattern in self.exclusions:
            if fnmatch.fnmatch(name, pattern):
                return True
        
        # Check against gitignore patterns (simplified implementation)
        rel_path = os.path.relpath(os.path.join(parent_dir, name), self.project_dir)
        for pattern in self._parse_gitignore():
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
                return True
        
        return False


# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <project_directory>")
        sys.exit(1)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Analyze the specified directory
    analyzer = CodebaseAnalyzer(sys.argv[1], {"exclusions": DEFAULT_EXCLUSIONS})
    results = analyzer.analyze()
    
    # Print summary
    print(f"\nProject: {results['project_name']}")
    print(f"Files: {results['file_count']}")
    print(f"Total Size: {results['total_size'] / 1024:.2f} KB")
    print("\nLanguages:")
    for lang, stats in results["languages"].items():
        print(f"  {lang}: {stats['count']} files ({stats['size'] / 1024:.2f} KB)")