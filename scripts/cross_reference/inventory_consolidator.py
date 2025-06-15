#!/usr/bin/env python
"""Cross-Reference Inventory Consolidation Script
Part of the EGOS Cross-Reference Standardization Initiative.

This script processes the raw JSON outputs from the inventory scan,
consolidates the findings, categorizes patterns, and generates a
comprehensive inventory report in Markdown format.

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
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set, Counter
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'inventory_consolidation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INPUT_DIR = r"C:\EGOS\docs\reports\temp_grep_results"
OUTPUT_DIR = r"C:\EGOS\docs\reports"
OUTPUT_FILENAME = f"cross_reference_inventory_{datetime.now().strftime('%Y%m%d')}.md"

# Pattern categories
PATTERN_CATEGORIES = {
    "keyword": "Keyword-based References",
    "structural": "Structural Pattern References",
    "id": "ID-based References",
    "path": "Path-based References",
    "memory": "Memory References",
    "other": "Other Reference Patterns"
}

def load_all_results() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load all JSON result files from the temporary directory.
    
    Returns:
        Dictionary mapping query types to lists of results
    """
    logger.info(f"Loading results from {INPUT_DIR}")
    
    results = {}
    
    # Get all JSON files in the input directory
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    
    for json_file in json_files:
        file_path = os.path.join(INPUT_DIR, json_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract query name from filename (e.g., grep_Ref_results.json -> Ref)
            query_name = json_file.replace('grep_', '').replace('_results.json', '')
            
            results[query_name] = data
            logger.info(f"Loaded {len(data)} results from {json_file}")
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
    
    return results

def analyze_patterns(all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Analyze and categorize patterns found in the inventory scan.
    
    Args:
        all_results: Dictionary mapping query types to lists of results
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info("Analyzing patterns")
    
    analysis = {
        "total_matches": 0,
        "unique_files": set(),
        "categories": defaultdict(list),
        "file_extensions": Counter(),
        "directories": Counter(),
        "examples": {},
        "most_referenced_files": Counter(),
        "pattern_frequency": Counter()
    }
    
    # Load the execution summary to get category information
    summary_path = os.path.join(INPUT_DIR, "execution_summary.md")
    category_map = {}
    
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse the table to extract category information
        for line in lines:
            if '|' in line and not line.startswith('| Query') and not line.startswith('|---'):
                parts = line.split('|')
                if len(parts) >= 3:
                    query = parts[1].strip().strip('`')
                    category = parts[2].strip()
                    category_map[query] = category
    
    # Add category_map to analysis for use in generate_report
    analysis["category_map"] = category_map
    
    # Process each query's results
    for query_name, results in all_results.items():
        analysis["total_matches"] += len(results)
        analysis["pattern_frequency"][query_name] = len(results)
        
        # Get category for this query
        category = category_map.get(query_name, "other")
        
        # Add to category
        analysis["categories"][category].extend(results)
        
        # Store example for this pattern (up to 3)
        analysis["examples"][query_name] = results[:3] if results else []
        
        # Process each result
        for result in results:
            file_path = result.get("File", "")
            analysis["unique_files"].add(file_path)
            
            # Count file extensions
            ext = Path(file_path).suffix.lower()
            analysis["file_extensions"][ext] += 1
            
            # Count directories (top-level only)
            try:
                rel_path = os.path.relpath(file_path, "C:\\EGOS")
                top_dir = rel_path.split(os.sep)[0]
                analysis["directories"][top_dir] += 1
            except:
                pass
            
            # Count referenced files
            # This is a simplistic approach - a more sophisticated analysis would
            # extract actual file references from the line content
            analysis["most_referenced_files"][file_path] += 1
    
    # Convert sets to lists for JSON serialization
    analysis["unique_files"] = list(analysis["unique_files"])
    
    logger.info(f"Analysis complete: {analysis['total_matches']} matches in {len(analysis['unique_files'])} unique files")
    
    return analysis

def generate_report(analysis: Dict[str, Any]) -> str:
    """
    Generate a comprehensive Markdown report from the analysis results.
    
    Args:
        analysis: Dictionary containing analysis results
        
    Returns:
        Path to the generated report file
    """
    logger.info("Generating report")
    
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Title and metadata
        f.write(f"# EGOS Cross-Reference Inventory Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Part of:** Cross-Reference Standardization Initiative (Phase 1: Preparation and Inventory)\n\n")
        
        # Executive summary
        f.write(f"## Executive Summary\n\n")
        f.write(f"This report presents the findings from a comprehensive inventory of cross-reference patterns across the EGOS codebase. ")
        f.write(f"The inventory identified **{analysis['total_matches']}** potential references across **{len(analysis['unique_files'])}** unique files.\n\n")
        
        # Pattern distribution
        f.write(f"### Pattern Distribution\n\n")
        f.write(f"| Pattern | Count | Percentage |\n")
        f.write(f"|---------|-------|------------|\n")
        
        for pattern, count in analysis["pattern_frequency"].most_common():
            percentage = (count / analysis["total_matches"]) * 100 if analysis["total_matches"] > 0 else 0
            f.write(f"| `{pattern}` | {count} | {percentage:.2f}% |\n")
        
        # File type distribution
        f.write(f"\n### File Type Distribution\n\n")
        f.write(f"| Extension | Count | Percentage |\n")
        f.write(f"|-----------|-------|------------|\n")
        
        for ext, count in analysis["file_extensions"].most_common():
            percentage = (count / len(analysis["unique_files"])) * 100 if analysis["unique_files"] else 0
            f.write(f"| `{ext}` | {count} | {percentage:.2f}% |\n")
        
        # Directory distribution
        f.write(f"\n### Directory Distribution\n\n")
        f.write(f"| Directory | Count | Percentage |\n")
        f.write(f"|-----------|-------|------------|\n")
        
        for directory, count in analysis["directories"].most_common(10):  # Top 10
            percentage = (count / len(analysis["unique_files"])) * 100 if analysis["unique_files"] else 0
            f.write(f"| `{directory}` | {count} | {percentage:.2f}% |\n")
        
        # Detailed findings by category
        f.write(f"\n## Detailed Findings\n\n")
        
        for category, category_name in PATTERN_CATEGORIES.items():
            results = analysis["categories"].get(category, [])
            if not results:
                continue
                
            f.write(f"\n### {category_name}\n\n")
            f.write(f"Found **{len(results)}** instances of {category_name.lower()}.\n\n")
            
            # Examples
            f.write(f"#### Examples\n\n")
            
            # Group examples by pattern
            pattern_examples = defaultdict(list)
            for query, examples in analysis["examples"].items():
                if analysis["category_map"].get(query, "other") == category:
                    pattern_examples[query] = examples
            
            for pattern, examples in pattern_examples.items():
                if not examples:
                    continue
                    
                f.write(f"**Pattern: `{pattern}`**\n\n")
                f.write(f"```\n")
                
                for i, example in enumerate(examples[:3], 1):  # Show up to 3 examples
                    file_path = example.get("File", "")
                    line_number = example.get("LineNumber", "")
                    line_content = example.get("LineContent", "")
                    
                    # Truncate long lines
                    if len(line_content) > 100:
                        line_content = line_content[:97] + "..."
                    
                    f.write(f"Example {i}: {file_path}:{line_number}\n")
                    f.write(f"  {line_content}\n\n")
                
                f.write(f"```\n\n")
        
        # Recommendations
        f.write(f"\n## Recommendations\n\n")
        
        f.write(f"Based on the inventory findings, the following recommendations are made for the cross-reference standardization process:\n\n")
        
        f.write(f"1. **Standardize on a Canonical Format:** Implement the `<!-- crossref_block -->` format for all references:\n\n")
        f.write(f"```markdown\n")
        f.write(f"<!-- crossref_block:start -->\n")
        f.write(f"- 🔗 <!-- TO_BE_REPLACED --><!-- TO_BE_REPLACED -->\n")
        f.write(f"- 🔗 <!-- TO_BE_REPLACED --><!-- TO_BE_REPLACED -->\n")
        f.write(f"- 🔗 <!-- TO_BE_REPLACED --><!-- TO_BE_REPLACED -->\n")
        f.write(f"<!-- crossref_block:end -->\n")
        f.write(f"```\n\n")
        
        f.write(f"2. **Purge Strategy:** Develop a purge script that targets the following patterns for replacement:\n\n")
        
        # List top patterns to purge
        for pattern, count in analysis["pattern_frequency"].most_common(5):
            f.write(f"   - `{pattern}` ({count} instances)\n")
        
        f.write(f"\n3. **Prioritize High-Impact Directories:** Focus initial standardization efforts on these key directories:\n\n")
        
        # List top directories to prioritize
        for directory, count in analysis["directories"].most_common(3):
            f.write(f"   - `{directory}` ({count} files with references)\n")
        
        f.write(f"\n4. **Develop Specialized Handlers:** Create specialized handlers for different file types, particularly:\n\n")
        
        # List top file extensions
        for ext, count in analysis["file_extensions"].most_common(3):
            f.write(f"   - `{ext}` files ({count} instances)\n")
        
        # Next steps
        f.write(f"\n## Next Steps\n\n")
        f.write(f"1. Review this inventory report to confirm completeness\n")
        f.write(f"2. Develop the purge script for outdated reference formats\n")
        f.write(f"3. Create a hierarchical injection strategy for standardized references\n")
        f.write(f"4. Implement system-wide validation of reference compliance\n")
    
    logger.info(f"Report generated: {output_path}")
    
    return output_path

def main():
    """Main function to consolidate inventory results and generate report."""
    logger.info("Starting inventory consolidation")
    
    # Load all results
    all_results = load_all_results()
    
    # Analyze patterns
    analysis = analyze_patterns(all_results)
    
    # Generate report
    report_path = generate_report(analysis)
    
    logger.info(f"Inventory consolidation complete. Report available at: {report_path}")
    logger.info("Next step: Review the inventory report and proceed to Phase 2 (Purge Outdated Formats)")

if __name__ == "__main__":
    main()