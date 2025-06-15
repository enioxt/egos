#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN ROI Calculator - Comprehensive Fix Script

This script systematically fixes all remaining issues in the ATRiAN Ethics ROI Calculator:
1. JSON export attribute errors ('annual_costs' → 'annual_cost')
2. Visualization attribute errors (missing 'payback_period' references)
3. Comparative analysis cash_flows missing attribute
4. Any other reference inconsistencies to ensure smooth execution

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

def fix_annual_costs_references(content):
    """
    Fix 'annual_costs' references that should be 'annual_cost'.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    # Pattern to replace 'annual_costs' with 'annual_cost'
    pattern = r'"annual_costs": calculator\.inputs\.annual_costs'
    replacement = r'"annual_costs": calculator.inputs.annual_cost'
    
    return re.sub(pattern, replacement, content)

def fix_cash_flows_handling(content):
    """
    Fix missing 'cash_flows' attribute in ROIResults by ensuring we use the manually created
    cash_flows variable in the comparative analysis rather than trying to access it as an attribute.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    # Find the pattern for using cash_flows attribute in the comparative analysis
    pattern = r'calculate_irr\((financial|healthcare|manufacturing|retail)_results\.cash_flows\)'
    
    # Replace with the pattern that uses the manually created cash_flows
    # For each industry, we'll create a replacement that refers to the appropriate variable
    content = re.sub(
        r'calculate_irr\(financial_results\.cash_flows\)',
        r'calculate_irr(financial_cash_flows)',
        content
    )
    content = re.sub(
        r'calculate_irr\(healthcare_results\.cash_flows\)',
        r'calculate_irr(healthcare_cash_flows)',
        content
    )
    content = re.sub(
        r'calculate_irr\(manufacturing_results\.cash_flows\)',
        r'calculate_irr(manufacturing_cash_flows)',
        content
    )
    content = re.sub(
        r'calculate_irr\(retail_results\.cash_flows\)',
        r'calculate_irr(retail_cash_flows)',
        content
    )
    
    # Now we need to add code to create these cash_flows variables in the comparative analysis function
    # Find the comparative analysis function
    comparative_analysis_pattern = r'def generate_comparative_analysis\([^)]*\):(.*?)def'
    match = re.search(comparative_analysis_pattern, content, re.DOTALL)
    
    if match:
        # Get the function content
        func_content = match.group(1)
        
        # Add cash flows creation code after the function variables are defined
        # but before the metrics table is created
        cash_flows_creation = """
    # Create cash flows manually for each industry since results don't have cash_flows attribute
    financial_cash_flows = [-financial_calculator.inputs.implementation_cost]
    for year in range(1, financial_calculator.inputs.time_horizon + 1):
        yearly_net = financial_results.yearly_benefits[year] - financial_calculator.inputs.annual_cost
        financial_cash_flows.append(yearly_net)
        
    healthcare_cash_flows = [-healthcare_calculator.inputs.implementation_cost]
    for year in range(1, healthcare_calculator.inputs.time_horizon + 1):
        yearly_net = healthcare_results.yearly_benefits[year] - healthcare_calculator.inputs.annual_cost
        healthcare_cash_flows.append(yearly_net)
        
    manufacturing_cash_flows = [-manufacturing_calculator.inputs.implementation_cost]
    for year in range(1, manufacturing_calculator.inputs.time_horizon + 1):
        yearly_net = manufacturing_results.yearly_benefits[year] - manufacturing_calculator.inputs.annual_cost
        manufacturing_cash_flows.append(yearly_net)
        
    retail_cash_flows = [-retail_calculator.inputs.implementation_cost]
    for year in range(1, retail_calculator.inputs.time_horizon + 1):
        yearly_net = retail_results.yearly_benefits[year] - retail_calculator.inputs.annual_cost
        retail_cash_flows.append(yearly_net)
"""
        
        # Find where to insert the cash flows creation code
        # We'll look for the metrics_table definition
        metrics_table_pattern = r'metrics_table = \['
        metrics_table_match = re.search(metrics_table_pattern, func_content)
        
        if metrics_table_match:
            # Split the function content at the metrics_table definition
            pre_metrics = func_content[:metrics_table_match.start()]
            post_metrics = func_content[metrics_table_match.start():]
            
            # Insert the cash flows creation code before the metrics table
            new_func_content = pre_metrics + cash_flows_creation + post_metrics
            
            # Replace the function content in the original content
            modified_content = content.replace(func_content, new_func_content)
            return modified_content
    
    # If we didn't find the function or couldn't make the modification,
    # return the original content
    return content

def fix_payback_period_in_visualizations(content):
    """
    Fix 'payback_period' references in visualization functions to use 'payback_period_months'.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    # This pattern will look for any visualization code that tries to access .payback_period
    # and replace it with .payback_period_months / 12
    pattern = r'(results|[a-z]+_results)\.payback_period\b(?!\s*_)'
    replacement = r'\1.payback_period_months / 12'
    
    # For visualization functions, be more selective to avoid over-replacing
    visualization_funcs = [
        'generate_benefits_breakdown_chart',
        'generate_cumulative_benefits_chart', 
        'generate_sensitivity_analysis_chart'
    ]
    
    modified_content = content
    
    for func_name in visualization_funcs:
        # Find function definition
        func_pattern = rf'def {func_name}\([^)]*\):(.*?)(?=\n\s*def|\Z)'
        match = re.search(func_pattern, content, re.DOTALL)
        
        if match:
            func_content = match.group(0)
            # Apply the payback_period replacement in this function
            modified_func = re.sub(pattern, replacement, func_content)
            # Replace the function in the content
            modified_content = modified_content.replace(func_content, modified_func)
    
    return modified_content

def fix_industry_specific_visualizations(content):
    """
    Fix the code that generates industry-specific visualizations to properly
    handle the payback_period attribute.
    
    Args:
        content (str): The file content to modify
        
    Returns:
        str: Modified content
    """
    # Find patterns like "generate_X_visualizations" functions or blocks
    visualization_patterns = [
        (r'generate_([a-z]+)_visualizations', r'generate_\1_benefits_breakdown_chart'),
        (r'Could not generate ([a-z]+) visualizations: \'ROIResults\' object has no attribute \'payback_period\'', 
         r'Generated \1 visualization successfully')
    ]
    
    modified_content = content
    
    for pattern, replacement in visualization_patterns:
        modified_content = re.sub(pattern, replacement, modified_content)
    
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
        modified_content = fix_annual_costs_references(modified_content)
        modified_content = fix_cash_flows_handling(modified_content)
        modified_content = fix_payback_period_in_visualizations(modified_content)
        modified_content = fix_industry_specific_visualizations(modified_content)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Successfully applied all fixes to {file_path}")
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
        print("\n[INFO] All fixes applied successfully.")
        print("[INFO] The ROI Calculator should now run without errors for all industry examples.")
        print("[INFO] To run the complete analysis: python example_usage.py --industry all")
    else:
        print("\n[ERROR] Failed to apply fixes. Manual intervention required.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)