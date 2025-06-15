#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix F-String Syntax Errors

This utility fixes f-string syntax errors in Python files by properly
escaping curly braces in HTML, CSS, and JavaScript sections.

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

import re
import sys
from pathlib import Path

def fix_f_strings(file_path):
    """Fix f-string syntax errors in a Python file."""
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = str(file_path) + '.bak2'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Original file backed up to: {backup_path}")
    
    # Fix f-string syntax by properly escaping curly braces in HTML/CSS/JS
    # Look for triple-quoted f-strings
    f_string_pattern = r'f"""(.*?)"""'
    matches = list(re.finditer(f_string_pattern, content, re.DOTALL))
    
    # Process matches in reverse order to avoid affecting positions
    for match in reversed(matches):
        template = match.group(1)
        start, end = match.span()
        
        # Handle specific sections that need escaping
        fixed_template = template
        
        # 1. Fix CSS rules
        css_sections = re.findall(r'<style>(.*?)</style>', fixed_template, re.DOTALL)
        for css in css_sections:
            # Properly escape curly braces in CSS rules
            fixed_css = re.sub(r'([^{]){([^{])', r'\1{{\2', css)
            fixed_css = re.sub(r'([^}])}([^}])', r'\1}}\2', fixed_css)
            fixed_template = fixed_template.replace(css, fixed_css)
        
        # 2. Fix JavaScript sections
        js_sections = re.findall(r'<script>(.*?)</script>', fixed_template, re.DOTALL)
        for js in js_sections:
            # Replace single curly braces with double curly braces in JS
            fixed_js = js.replace('{', '{{').replace('}', '}}')
            # Ensure placeholders are preserved (restore single braces for actual f-string placeholders)
            fixed_js = re.sub(r'{{([^{]*?)}}', r'{\1}', fixed_js)
            fixed_template = fixed_template.replace(js, fixed_js)
        
        # Update the content with fixed template
        fixed_f_string = f'f"""{fixed_template}"""'
        content = content[:start] + fixed_f_string + content[end:]
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed f-string syntax errors in: {file_path}")
    print("Please test the fixed file to ensure it works correctly.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_f_strings.py <file_path>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)
    
    fix_f_strings(file_path)
