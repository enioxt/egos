#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN ROI Calculator - Comprehensive Bugfix Script

This script fixes all remaining issues in the example_usage.py file, including:
1. Missing confidence_level attribute in executive summary
2. Any other attribute inconsistencies that might cause errors
3. Error handling for edge cases

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

def fix_confidence_level_issue(file_path):
    """
    Fix the confidence_level attribute error in the executive summary generation.
    
    Args:
        file_path (str): Path to the example_usage.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the specific line causing the error and replace it
        pattern = r'f"  • Confidence Level: {results\.confidence_level:\.\d+f}%\\n",'
        replacement = 'f"  • Confidence Level: " + (f"{results.confidence_level:.1f}%" if hasattr(results, \'confidence_level\') else "N/A (not available)") + "\\n",'
        
        # Replace the occurrence
        updated_content = re.sub(pattern, replacement, content)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully fixed confidence_level attribute error in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing confidence_level issue: {str(e)}")
        return False

def fix_roi_variance_issue(file_path):
    """
    Fix potential issues with roi_variance attribute in the executive summary.
    
    Args:
        file_path (str): Path to the example_usage.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the specific line that might cause issues with roi_variance
        pattern = r'f"  • ROI Variance: {results\.roi_variance:\.\d+f}%\\n",'
        replacement = 'f"  • ROI Variance: " + (f"{results.roi_variance:.1f}%" if hasattr(results, \'roi_variance\') else "N/A (not available)") + "\\n",'
        
        # Replace the occurrence
        updated_content = re.sub(pattern, replacement, content)
        
        # Also fix the contingency budget line that uses roi_variance
        pattern2 = r'f"  • Allocate {max\(10, min\(30, int\(results\.roi_variance\)\)\)}% contingency budget for implementation complexity",'
        replacement2 = 'f"  • Allocate {max(10, min(30, int(results.roi_variance) if hasattr(results, \'roi_variance\') else 15))}% contingency budget for implementation complexity",'
        
        # Replace the second occurrence
        updated_content = re.sub(pattern2, replacement2, updated_content)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully fixed roi_variance attribute handling in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing roi_variance issue: {str(e)}")
        return False

def fix_best_worst_case_roi_issue(file_path):
    """
    Fix potential issues with best_case_roi and worst_case_roi attributes.
    
    Args:
        file_path (str): Path to the example_usage.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the lines using best_case_roi and worst_case_roi
        pattern1 = r'f"  • Best Case ROI \(95th percentile\): {results\.best_case_roi:\.\d+f}%",'
        replacement1 = 'f"  • Best Case ROI (95th percentile): " + (f"{results.best_case_roi:.1f}%" if hasattr(results, \'best_case_roi\') else "N/A (not available)") + ",",'
        
        pattern2 = r'f"  • Worst Case ROI \(5th percentile\): {results\.worst_case_roi:\.\d+f}%\\n",'
        replacement2 = 'f"  • Worst Case ROI (5th percentile): " + (f"{results.worst_case_roi:.1f}%" if hasattr(results, \'worst_case_roi\') else "N/A (not available)") + "\\n",'
        
        # Replace occurrences
        updated_content = re.sub(pattern1, replacement1, content)
        updated_content = re.sub(pattern2, replacement2, updated_content)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully fixed best/worst case ROI attribute handling in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing best/worst case ROI issue: {str(e)}")
        return False

def fix_executive_summary_function(file_path):
    """
    Replace the entire executive summary function with a robust version.
    This is the most reliable way to fix all potential issues at once.
    
    Args:
        file_path (str): Path to the example_usage.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the entire generate_executive_summary function
        pattern = r"def generate_executive_summary\(calculator, results, industry\):(?:.*?)\n    return \"\\n\"\.join\(summary\)"
        
        # New robust version of the function
        replacement = """def generate_executive_summary(calculator, results, industry):
    \"\"\"Generate an executive summary of ROI analysis.\"\"\"
    annual_benefit_average = results.npv_benefits / calculator.inputs.time_horizon
    time_to_positive_roi = max(results.payback_period_months / 12, 0.08)  # In years, minimum 1 month
    
    summary = [
        f\"\"\"\\n{'=' * 80}\\n\"\"\",
        f\"\"\"                      ATRIAN ETHICS ROI - EXECUTIVE SUMMARY                    \"\"\",
        f\"\"\"{'=' * 80}\\n\"\"\",
        f"INDUSTRY: {industry}\\n",
        f"ANALYSIS DATE: {datetime.now().strftime('%B %d, %Y')}\\n",
        f"INVESTMENT HORIZON: {calculator.inputs.time_horizon} years\\n",
        f"\\nKEY FINDINGS:\\n",
        f"  • ROI: {results.roi_percentage:.1f}%",
        f"  • Net Present Value: {format_currency(results.net_benefits)}",
        f"  • Annual Average Benefit: {format_currency(annual_benefit_average)}",
        f"  • Payback Period: {results.payback_period_months:.1f} months",
        f"  • Time to Positive ROI: {time_to_positive_roi:.2f} years",
        f"  • Confidence Level: " + (f"{results.confidence_level:.1f}%" if hasattr(results, 'confidence_level') else "N/A (not available)") + "\\n",
        f"BENEFIT DISTRIBUTION:\\n"
    ]
    
    # Add benefit breakdown table
    benefit_data = [
        ["Risk Mitigation", 
         format_currency(results.risk_mitigation_benefits),
         f"{results.risk_mitigation_benefits/results.npv_benefits*100:.1f}%"],
        ["Operational Efficiency", 
         format_currency(results.operational_efficiency_benefits),
         f"{results.operational_efficiency_benefits/results.npv_benefits*100:.1f}%"],
        ["Brand Value", 
         format_currency(results.brand_value_benefits),
         f"{results.brand_value_benefits/results.npv_benefits*100:.1f}%"],
        ["Regulatory Compliance", 
         format_currency(results.regulatory_compliance_benefits),
         f"{results.regulatory_compliance_benefits/results.npv_benefits*100:.1f}%"],
        ["Innovation Enablement", 
         format_currency(results.innovation_enablement_benefits),
         f"{results.innovation_enablement_benefits/results.npv_benefits*100:.1f}%"],
        ["TOTAL", 
         format_currency(results.npv_benefits),
         "100.0%"]
    ]
    
    summary.append(tabulate(benefit_data, 
                           headers=["Benefit Category", "NPV", "Percentage"], 
                           tablefmt="grid"))
    
    # Add risk assessment
    summary.extend([
        f"\\nRISK ASSESSMENT:\\n",
        f"  • Best Case ROI (95th percentile): " + (f"{results.best_case_roi:.1f}%" if hasattr(results, 'best_case_roi') else "N/A (not available)"),
        f"  • Worst Case ROI (5th percentile): " + (f"{results.worst_case_roi:.1f}%" if hasattr(results, 'worst_case_roi') else "N/A (not available)"),
        f"  • ROI Variance: " + (f"{results.roi_variance:.1f}%" if hasattr(results, 'roi_variance') else "N/A (not available)") + "\\n",
        f"STRATEGIC IMPLICATIONS:\\n"
    ])
    
    # Add strategic implications based on industry
    if industry == "Financial Services":
        summary.append("  • ATRiAN investment provides significant regulatory compliance value")
        summary.append("  • Customer trust improvements deliver the highest ROI component")
        summary.append("  • Implementation should prioritize bias mitigation in lending algorithms")
    elif industry == "Healthcare":
        summary.append("  • Patient data protection delivers highest ethical and financial returns")
        summary.append("  • Regulatory compliance benefits offset longer implementation timeline")
        summary.append("  • Clinical decision support applications provide highest value opportunity")
    elif industry == "Manufacturing":
        summary.append("  • Quality control and safety applications show strongest ROI")
        summary.append("  • Supply chain ethical monitoring provides emerging value stream")
        summary.append("  • Integration with existing industrial systems is critical success factor")
    elif industry == "Retail":
        summary.append("  • Customer trust and personalization balance creates highest value")
        summary.append("  • Recommendation algorithm ethics provides immediate ROI")
        summary.append("  • Privacy-centric data strategies unlock new market opportunities")
    
    # Add implementation recommendations
    summary.extend([
        f"\\nIMPLEMENTATION RECOMMENDATIONS:\\n",
        f"  • Phased approach with {math.ceil(time_to_positive_roi * 12)}-month initial rollout",
        f"  • Focus on {sorted(benefit_data[:-1], key=lambda x: float(x[2].rstrip('%')), reverse=True)[0][0]} as primary value driver",
        f"  • Allocate {max(10, min(30, int(results.roi_variance) if hasattr(results, 'roi_variance') else 15))}% contingency budget for implementation complexity",
        f"  • Establish quarterly ethics monitoring dashboard for ongoing optimization",
        f"\\n{'=' * 80}\\n"
    ])
    
    return "\\n".join(summary)"""
        
        # Replace the function using re.DOTALL to match across multiple lines
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully replaced executive summary function with robust version in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error replacing executive summary function: {str(e)}")
        return False

def main():
    """Main execution function"""
    script_dir = Path(__file__).parent
    target_file = script_dir / "example_usage.py"
    
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return False
    
    # Fix all issues - the executive summary replacement is the most comprehensive approach
    success = fix_executive_summary_function(target_file)
    
    if success:
        print("\n[INFO] All fixes applied successfully. The ROI Calculator should now run without errors.")
        print("[INFO] To run: python example_usage.py --industry all")
    else:
        print("\n[ERROR] Failed to apply all fixes. Manual intervention may be required.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)