#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Cross-Reference Validator (Basic Prototype)

This script validates cross-references across the EGOS ecosystem to ensure they
follow the standardized format and point to valid targets. This is a basic prototype
to validate the approach before implementing the full version with all EGOS script standards.

Author: EGOS Development Team
Created: 2025-05-21
Version: 0.1.0 (Prototype)

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

import os
import re
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("cross_reference_validator")

# Regular expressions for identifying cross-references
REFERENCE_PATTERNS = [
    # Standard markdown links
    r'\[([^\]]+)\]\(([^)]+)\)',
    
    # Standardized reference format
    r'<!-- crossref_block:start -->.*?<!-- crossref_block:end -->',
    
    # EGOS ID references
    r'EGOS-[A-Z]+-\d+',
]

def find_files(base_path: str, extensions: List[str] = ['.md', '.txt']) -> List[Path]:
    """Find all files with specified extensions in the base path.
    
    Args:
        base_path: Base path to search
        extensions: List of file extensions to include
        
    Returns:
        List of file paths
    """
    files = []
    base_path = Path(base_path)
    
    # Skip directories to exclude
    exclude_dirs = {'.git', 'venv', 'node_modules', '__pycache__', 'dist', 'build'}
    
    for root, dirs, filenames in os.walk(base_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(Path(os.path.join(root, filename)))
    
    return files

def extract_references(file_path: Path) -> List[Tuple[str, str]]:
    """Extract references from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of tuples (reference_text, reference_target)
    """
    references = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract standard markdown links
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, target in md_links:
            # Skip external links
            if not target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                references.append((text, target))
        
        # Extract standardized reference blocks
        ref_blocks = re.findall(r'<!-- crossref_block:start -->(.*?)<!-- crossref_block:end -->', content, re.DOTALL)
        for block in ref_blocks:
            # Extract references from the block
            block_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', block)
            for text, target in block_links:
                references.append((text, target))
    
    except Exception as e:
        logger.error(f"Error extracting references from {file_path}: {str(e)}")
    
    return references

def validate_reference(reference: Tuple[str, str], source_file: Path, all_files: Set[Path]) -> Dict[str, Any]:
    """Validate a reference.
    
    Args:
        reference: Tuple (reference_text, reference_target)
        source_file: Path to the source file
        all_files: Set of all files in the codebase
        
    Returns:
        Dictionary with validation results
    """
    text, target = reference
    result = {
        "source_file": str(source_file),
        "reference_text": text,
        "reference_target": target,
        "valid": False,
        "error": None
    }
    
    try:
        # Handle relative paths
        if not os.path.isabs(target):
            target_path = source_file.parent / target
        else:
            target_path = Path(target)
        
        # Normalize path
        target_path = target_path.resolve()
        
        # Check if target exists
        if target_path in all_files:
            result["valid"] = True
        else:
            result["error"] = "Target file does not exist"
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.getcwd()
    
    logger.info(f"Starting cross-reference validation in {base_path}")
    
    # Find all files
    files = find_files(base_path)
    all_files_set = set(file.resolve() for file in files)
    logger.info(f"Found {len(files)} files to scan")
    
    # Extract and validate references
    valid_refs = 0
    invalid_refs = 0
    invalid_files = set()
    
    for file in files:
        references = extract_references(file)
        
        if references:
            logger.info(f"Found {len(references)} references in {file}")
            
            for ref in references:
                result = validate_reference(ref, file, all_files_set)
                
                if result["valid"]:
                    valid_refs += 1
                else:
                    invalid_refs += 1
                    invalid_files.add(file)
                    logger.warning(f"Invalid reference in {file}: {ref[0]} -> {ref[1]} ({result['error']})")
    
    # Print summary
    logger.info(f"Validation complete:")
    logger.info(f"  - Total references: {valid_refs + invalid_refs}")
    logger.info(f"  - Valid references: {valid_refs}")
    logger.info(f"  - Invalid references: {invalid_refs}")
    logger.info(f"  - Files with invalid references: {len(invalid_files)}")

if __name__ == "__main__":
    main()