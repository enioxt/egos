#!/usr/bin/env python
"""Script to save grep search results to JSON files.
Part of the EGOS Cross-Reference Standardization Initiative.

This script handles the saving of grep_search results to JSON files
in the temp_grep_results directory.

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

import json
import os
from datetime import datetime
from typing import List, Dict, Any

def save_grep_results(results: List[Dict[str, Any]], filename: str) -> str:
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
    
    # Save the results to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return output_path

def main():
    """Main function to demonstrate usage."""
    # Example usage
    results = [
        {"File": "example.py", "LineNumber": 10, "LineContent": "# Example content"}
    ]
    output_path = save_grep_results(results, "example_results.json")
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()
