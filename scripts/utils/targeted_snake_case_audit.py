#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Targeted snake_case Audit Script

This script performs a targeted audit of a specific directory for files and directories
not adhering to the snake_case naming convention. It outputs a simple list of
non-compliant items for further processing.

@author: Cascade (AI Assistant)
@date: 2025-05-26
@version: 0.1.0

@references:
  - C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
  - C:\EGOS\docs\planning\snake_case_conversion_plan.md
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
import re
import sys
import argparse
from pathlib import Path

def is_snake_case(name):
    """
    Check if a name follows snake_case convention.
    
    Args:
        name (str): The name to check
        
    Returns:
        bool: True if the name follows snake_case, False otherwise
    """
    # Remove file extension if present
    if '.' in name:
        name = name.rsplit('.', 1)[0]
    
    # Check if name is already snake_case (all lowercase with underscores)
    snake_case_pattern = r'^[a-z0-9_]+$'
    return bool(re.match(snake_case_pattern, name))

def should_exclude(path, exclusions):
    """
    Check if a path should be excluded based on exclusion rules.
    
    Args:
        path (Path): The path to check
        exclusions (dict): Dictionary of exclusion rules
        
    Returns:
        bool: True if the path should be excluded, False otherwise
    """
    # Check directory exclusions
    for part in path.parts:
        if part in exclusions.get('directories', []):
            return True
    
    # Check file exclusions
    if path.name in exclusions.get('files', []):
        return True
    
    # Check extension exclusions
    if path.suffix.lower() in exclusions.get('extensions_to_ignore', []):
        return True
    
    # Check pattern exclusions
    str_path = str(path).replace('\\', '/')
    for pattern in exclusions.get('patterns_to_ignore', []):
        try:
            if re.search(pattern, str_path):
                return True
        except re.error:
            print(f"Warning: Invalid regex pattern: {pattern}")
    
    return False

def audit_directory(directory_path, exclusions):
    """
    Audit a directory for non-snake_case files and directories.
    
    Args:
        directory_path (str): Path to the directory to audit
        exclusions (dict): Dictionary of exclusion rules
        
    Returns:
        list: List of non-compliant paths
    """
    non_compliant = []
    
    for root, dirs, files in os.walk(directory_path):
        # Process directories
        for dir_name in dirs:
            path = Path(os.path.join(root, dir_name))
            if not should_exclude(path, exclusions) and not is_snake_case(dir_name):
                non_compliant.append(str(path))
        
        # Process files
        for file_name in files:
            path = Path(os.path.join(root, file_name))
            if not should_exclude(path, exclusions) and not is_snake_case(file_name):
                non_compliant.append(str(path))
    
    return non_compliant

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="EGOS Targeted snake_case Audit Script")
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to audit"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Basic exclusions
    exclusions = {
        'directories': ['.git', 'venv', '.venv', 'env', 'node_modules', '__pycache__', '.vscode', '.idea'],
        'files': ['README.md', 'LICENSE', 'Makefile', 'requirements.txt', '.gitignore', '.gitattributes'],
        'extensions_to_ignore': ['.md', '.MD'],
        'patterns_to_ignore': [r'.*\.git.*', r'.*node_modules.*', r'.*__pycache__.*', r'.*\.vscode.*']
    }
    
    # Run the audit
    non_compliant = audit_directory(args.directory, exclusions)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            for path in non_compliant:
                f.write(f"{path}\n")
    else:
        for path in non_compliant:
            print(path)
    
    print(f"\nTotal non-compliant items: {len(non_compliant)}", file=sys.stderr)

if __name__ == "__main__":
    main()