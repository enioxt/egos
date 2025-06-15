#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN ROI Calculator - IRR Handling Bugfix Script

This script fixes the IRR calculation error handling in the example_usage.py file.
It modifies all industry example functions to properly handle cases where the IRR 
calculation returns None.

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

def fix_irr_handling(file_path):
    """
    Fix IRR error handling in all industry examples.
    
    Args:
        file_path (str): Path to the example_usage.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all instances of IRR formatting and fix them
        pattern = r'print\(f"IRR: {irr:.2f}%"\)'
        replacement = 'print(f"IRR: {irr:.2f}%" if irr is not None else "IRR: N/A (insufficient cash flow data)")'
        
        # Replace all occurrences
        updated_content = re.sub(pattern, replacement, content)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully fixed IRR error handling in {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error fixing IRR handling: {str(e)}")
        return False

def main():
    """Main execution function"""
    script_dir = Path(__file__).parent
    target_file = script_dir / "example_usage.py"
    
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return False
    
    success = fix_irr_handling(target_file)
    
    if success:
        print("\n[INFO] IRR handling fix complete. Try running the examples again.")
        print("[INFO] To run: python example_usage.py --industry all")
    else:
        print("\n[ERROR] Failed to fix IRR handling. Manual intervention required.")
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)