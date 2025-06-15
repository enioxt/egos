#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN ROI Calculator - Indentation Fix Script

This script fixes indentation issues in the example_usage.py file
that occurred after our previous fixes.

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

import re
import sys
from pathlib import Path

def fix_indentation_in_comparative_analysis(file_path):
    """
    Fix indentation issues in the comparative analysis function.
    
    Args:
        file_path (str): Path to the example_usage.py file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the comparative analysis function
        comparative_analysis_pattern = r'def generate_comparative_analysis\([^)]*\):(.*?)(?=\n\s*def|\Z)'
        match = re.search(comparative_analysis_pattern, content, re.DOTALL)
        
        if not match:
            print("❌ Could not find the comparative analysis function")
            return False
        
        # Get the function content
        func_content = match.group(1)
        
        # Fix indentation in the function
        # Split the function into lines
        lines = func_content.split('\n')
        fixed_lines = []
        
        # Determine the base indentation (should be 4 spaces)
        base_indent = 4
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                fixed_lines.append(line)
                continue
                
            # Count leading spaces
            leading_spaces = len(line) - len(line.lstrip())
            
            # If the line is already indented with 4 spaces or is empty, keep it as is
            if leading_spaces == base_indent or not line.strip():
                fixed_lines.append(line)
            else:
                # Otherwise, reindent it with 4 spaces
                fixed_lines.append(' ' * base_indent + line.lstrip())
        
        # Join the fixed lines back into a string
        fixed_func_content = '\n'.join(fixed_lines)
        
        # Replace the function content in the original content
        modified_content = content.replace(func_content, fixed_func_content)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Successfully fixed indentation issues in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing indentation: {str(e)}")
        return False

def main():
    """Main execution function"""
    script_dir = Path(__file__).parent.parent
    target_file = script_dir / "example_usage.py"
    
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return False
    
    success = fix_indentation_in_comparative_analysis(target_file)
    
    if success:
        print("\n[INFO] Indentation issues fixed successfully.")
        print("[INFO] The ROI Calculator should now run without indentation errors.")
        print("[INFO] To run the complete analysis: python example_usage.py --industry all")
    else:
        print("\n[ERROR] Failed to fix indentation issues. Manual intervention required.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)