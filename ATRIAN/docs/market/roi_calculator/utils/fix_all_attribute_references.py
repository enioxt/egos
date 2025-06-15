#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN ROI Calculator - Comprehensive Attribute Reference Fix

This script systematically fixes all remaining attribute reference inconsistencies in example_usage.py:
1. JSON export attribute references 
2. Comparative analysis table attribute references
3. Visualization functions attribute references

Created: 2025-06-02
Author: EGOS Team - ATRiAN Division
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
from pathlib import Path

def fix_json_export_attribute_references(content):
    """
    Fix attribute references in the JSON export sections.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    # Common pattern for all industry examples
    patterns = [
        (r'"roi": results\.roi', r'"roi": results.roi_percentage'),
        (r'"npv": results\.npv', r'"npv": results.net_benefits'),
        (r'"payback_period": results\.payback_period', r'"payback_period": results.payback_period_months / 12'),
        (r'"initial_investment": results\.initial_investment', r'"initial_investment": calculator.inputs.implementation_cost'),
        (r'"total_benefits_npv": results\.total_benefits_npv', r'"total_benefits_npv": results.npv_benefits'),
        (r'"total_costs_npv": results\.total_costs_npv', r'"total_costs_npv": results.npv_costs'),
    ]
    
    modified_content = content
    for pattern, replacement in patterns:
        modified_content = re.sub(pattern, replacement, modified_content)
    
    return modified_content

def fix_comparative_analysis_attributes(content):
    """
    Fix attribute references in the comparative analysis section.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    patterns = [
        # Financial Services row
        (r'f"{financial_results\.roi:', r'f"{financial_results.roi_percentage:'),
        (r'format_currency\(financial_results\.npv\)', r'format_currency(financial_results.net_benefits)'),
        (r'f"{financial_results\.payback_period:', r'f"{financial_results.payback_period_months / 12:'),
        (r'f"{financial_results\.total_benefits_npv / financial_results\.total_costs_npv:', 
         r'f"{financial_results.npv_benefits / financial_results.npv_costs:'),
        
        # Healthcare row
        (r'f"{healthcare_results\.roi:', r'f"{healthcare_results.roi_percentage:'),
        (r'format_currency\(healthcare_results\.npv\)', r'format_currency(healthcare_results.net_benefits)'),
        (r'f"{healthcare_results\.payback_period:', r'f"{healthcare_results.payback_period_months / 12:'),
        (r'f"{healthcare_results\.total_benefits_npv / healthcare_results\.total_costs_npv:', 
         r'f"{healthcare_results.npv_benefits / healthcare_results.npv_costs:'),
        
        # Manufacturing row
        (r'f"{manufacturing_results\.roi:', r'f"{manufacturing_results.roi_percentage:'),
        (r'format_currency\(manufacturing_results\.npv\)', r'format_currency(manufacturing_results.net_benefits)'),
        (r'f"{manufacturing_results\.payback_period:', r'f"{manufacturing_results.payback_period_months / 12:'),
        (r'f"{manufacturing_results\.total_benefits_npv / manufacturing_results\.total_costs_npv:', 
         r'f"{manufacturing_results.npv_benefits / manufacturing_results.npv_costs:'),
        
        # Retail row
        (r'f"{retail_results\.roi:', r'f"{retail_results.roi_percentage:'),
        (r'format_currency\(retail_results\.npv\)', r'format_currency(retail_results.net_benefits)'),
        (r'f"{retail_results\.payback_period:', r'f"{retail_results.payback_period_months / 12:'),
        (r'f"{retail_results\.total_benefits_npv / retail_results\.total_costs_npv:', 
         r'f"{retail_results.npv_benefits / retail_results.npv_costs:')
    ]
    
    modified_content = content
    for pattern, replacement in patterns:
        modified_content = re.sub(pattern, replacement, modified_content)
    
    return modified_content

def fix_visualization_attribute_references(content):
    """
    Fix attribute references in the visualization functions.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    patterns = [
        (r'\.payback_period\b', r'.payback_period_months / 12'),
        (r'\.roi\b', r'.roi_percentage'),
        (r'\.total_benefits_npv\b', r'.npv_benefits'),
        (r'\.total_costs_npv\b', r'.npv_costs'),
        (r'\.npv\b', r'.net_benefits')
    ]
    
    # We need to be more selective about these replacements to avoid over-replacing
    # Find visualization functions and only replace within them
    visualization_functions = [
        'generate_benefits_breakdown_chart',
        'generate_cumulative_benefits_chart',
        'generate_sensitivity_analysis_chart'
    ]
    
    modified_content = content
    
    # Process each visualization function
    for func_name in visualization_functions:
        # Find function definition start and end
        func_pattern = rf'def {func_name}\(.*?\):\n.*?(?=\n\n|def )'
        func_matches = re.finditer(func_pattern, content, re.DOTALL)
        
        for match in func_matches:
            func_content = match.group(0)
            modified_func_content = func_content
            
            # Apply each pattern replacement within the function
            for pattern, replacement in patterns:
                modified_func_content = re.sub(pattern, replacement, modified_func_content)
            
            # Replace the function in the content
            modified_content = modified_content.replace(func_content, modified_func_content)
    
    return modified_content

def apply_all_fixes(file_path):
    """
    Apply all fixes to the specified file.
    
    Args:
        file_path (str): Path to the example_usage.py file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply each fix
        modified_content = content
        modified_content = fix_json_export_attribute_references(modified_content)
        modified_content = fix_comparative_analysis_attributes(modified_content)
        modified_content = fix_visualization_attribute_references(modified_content)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Successfully applied all attribute reference fixes to {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error applying fixes: {str(e)}")
        return False

def main():
    """Main execution function"""
    script_dir = Path(__file__).parent.parent
    target_file = script_dir / "example_usage.py"
    
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return False
    
    success = apply_all_fixes(target_file)
    
    if success:
        print("\n[INFO] All attribute reference fixes applied successfully.")
        print("[INFO] The ROI Calculator should now run without errors, including JSON export and comparative analysis.")
        print("[INFO] To run: python example_usage.py --industry all")
    else:
        print("\n[ERROR] Failed to apply fixes. Manual intervention required.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)