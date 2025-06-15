#!/usr/bin/env python
"""Cross-Reference Inventory Scan Execution Script
Part of the EGOS Cross-Reference Standardization Initiative.

This script executes a comprehensive inventory scan of cross-reference patterns
across the EGOS codebase, handling encoding issues properly and saving results
for later consolidation and analysis.

Author: EGOS Development Team
Date: 2025-05-21
Version: 1.0.0

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

import json
import os
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'inventory_scan.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define the queries to execute
QUERIES = [
    # Keyword-based (Case-Insensitive: true)
    {"query": "Ref:", "output_file": "grep_Ref_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "Reference:", "output_file": "grep_Reference_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "Source:", "output_file": "grep_Source_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "See also:", "output_file": "grep_SeeAlso_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "Related:", "output_file": "grep_Related_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "Doc:", "output_file": "grep_Doc_results.json", "case_insensitive": True, "category": "keyword"},
    {"query": "Link to:", "output_file": "grep_LinkTo_results.json", "case_insensitive": True, "category": "keyword"},
    
    # Structural Patterns
    {"query": "[[", "output_file": "grep_WikiLinkStart_results.json", "case_insensitive": False, "category": "structural"},
    {"query": "<!-- TO_BE_REPLACED -->", "output_file": "grep_REF_XYZ_Start_results.json", "case_insensitive": False, "category": "structural"},
    {"query": "<!-- TO_BE_REPLACED -->", "output_file": "grep_xref_results.json", "case_insensitive": True, "category": "structural"},
    
    # EGOS ID Patterns
    {"query": "EGOS-", "output_file": "grep_EGOS_ID_Start_results.json", "case_insensitive": False, "category": "id"},
    
    # Relative Path Indicators
    {"query": "../", "output_file": "grep_RelativePathParent_results.json", "case_insensitive": False, "category": "path"},
    {"query": "./", "output_file": "grep_RelativePathSelf_results.json", "case_insensitive": False, "category": "path"},
    
    # Memory References
    {"query": "MEMORY[", "output_file": "grep_MEMORY_results.json", "case_insensitive": False, "category": "memory"},
]

# Directories to exclude from the search
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'venv', 'node_modules', 'dist', 'build', '.idea', '.vscode'
}

# File extensions to include in the search
INCLUDE_EXTENSIONS = {
    '.md', '.py', '.yaml', '.yml', '.json', '.txt', '.sh', '.ps1', '.rst', '.tex', '.ini', '.cfg'
}

def find_files(base_path: str, extensions: Set[str]) -> List[str]:
    """
    Find all files with given extensions, skipping excluded directories.
    
    Args:
        base_path: Base directory to start the search
        extensions: Set of file extensions to include
        
    Returns:
        List of file paths matching the criteria
    """
    matching_files = []
    base_path = Path(base_path)
    
    logger.info(f"Finding files with extensions {extensions} in {base_path}")
    start_time = time.time()
    
    for root, dirs, files in os.walk(base_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            file_ext = Path(file).suffix.lower()
            if file_ext in extensions:
                matching_files.append(os.path.join(root, file))
    
    elapsed = time.time() - start_time
    logger.info(f"Found {len(matching_files)} files in {elapsed:.2f} seconds")
    
    return matching_files

def execute_grep_search(query: str, case_insensitive: bool = True, 
                       file_extensions: Set[str] = INCLUDE_EXTENSIONS) -> List[Dict[str, Any]]:
    """
    Search files for the given pattern.
    
    Args:
        query: The search query
        case_insensitive: Whether to perform a case-insensitive search
        file_extensions: Set of file extensions to include
        
    Returns:
        List of dictionaries containing the search results
    """
    logger.info(f"Executing search for: '{query}' (case_insensitive={case_insensitive})")
    start_time = time.time()
    
    # Find all relevant files
    files = find_files("C:\\EGOS", file_extensions)
    
    # Compile regex pattern
    flags = re.IGNORECASE if case_insensitive else 0
    pattern = re.compile(re.escape(query), flags)
    
    results = []
    processed_files = 0
    matched_files = 0
    
    # Process each file
    for file_path in files:
        processed_files += 1
        
        if processed_files % 100 == 0:
            logger.info(f"Processed {processed_files}/{len(files)} files...")
        
        try:
            # Open with error handling for encoding issues
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            # Search for pattern in each line
            for line_num, line_content in enumerate(lines, 1):
                if pattern.search(line_content):
                    results.append({
                        "File": file_path,
                        "LineNumber": line_num,
                        "LineContent": line_content.rstrip('\n')
                    })
                    matched_files += 1
                    break  # Only count each file once
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
    
    elapsed = time.time() - start_time
    logger.info(f"Found {len(results)} matches in {matched_files} files (processed {processed_files} files) in {elapsed:.2f} seconds")
    
    return results

def save_results(results: List[Dict[str, Any]], filename: str) -> str:
    """
    Save grep search results to a JSON file.
    
    Args:
        results: List of dictionaries containing grep search results
        filename: Name of the file to save results to
        
    Returns:
        Path to the saved file
    """
    # Ensure the directory exists
    output_dir = r"C:\EGOS\docs\reports\temp_grep_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Full path to the output file
    output_path = os.path.join(output_dir, filename)
    
    try:
        # Save the results to the file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving results to {output_path}: {str(e)}")
        return ""

def main():
    """Execute all grep searches and save results."""
    logger.info(f"Starting cross-reference inventory scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total queries to execute: {len(QUERIES)}")
    
    # Create a summary file to track execution
    summary_path = r"C:\EGOS\docs\reports\temp_grep_results\execution_summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# Cross-Reference Inventory Scan Execution Summary\n\n")
        f.write(f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Queries Executed\n\n")
        f.write(f"| Query | Category | Case Insensitive | Result Count | Output File |\n")
        f.write(f"|-------|----------|-----------------|--------------|-------------|\n")
    
    # Execute each query and save results
    for query_info in QUERIES:
        query = query_info["query"]
        output_file = query_info["output_file"]
        case_insensitive = query_info.get("case_insensitive", True)
        category = query_info.get("category", "other")
        
        # Execute the search
        results = execute_grep_search(query, case_insensitive)
        
        # Save the results
        save_results(results, output_file)
        
        # Update the summary file
        with open(summary_path, 'a', encoding='utf-8') as f:
            f.write(f"| `{query}` | {category} | {case_insensitive} | {len(results)} | [{output_file}]({output_file}) |\n")
    
    logger.info(f"Inventory scan completed. Summary available at: {summary_path}")
    logger.info(f"Next step: Develop the inventory consolidation script (Action 3)")

if __name__ == "__main__":
    main()