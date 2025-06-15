#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Validator Script

This script identifies and fixes syntax errors in the cross-reference validator.

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
from pathlib import Path

def fix_validator_syntax():
    """Identify and fix syntax errors in the cross-reference validator."""
    file_path = Path(__file__).parent / "cross_reference_validator.py"
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Extract lines for inspection
    lines = content.splitlines()
    
    # Print the problematic line and surrounding context
    print("Examining line 635 and surrounding lines:")
    for i in range(max(0, 630), min(len(lines), 640)):
        print(f"{i+1}: {lines[i]}")
    
    # Fix common f-string issues in HTML templates
    fixed_content = content
    
    # Look for unclosed f-strings or HTML formatting issues
    pattern = r'f"""(.*?)"""'
    for match in re.finditer(pattern, content, re.DOTALL):
        template = match.group(1)
        
        # Check for unescaped curly braces in HTML/CSS/JS contexts
        if "function toggleFix" in template or "var element" in template:
            print("\nFound potentially problematic HTML template with JavaScript.")
            
            # Get a snippet of the problematic section
            start = match.start()
            end = match.end()
            context_start = max(0, start - 100)
            context_end = min(len(content), end + 100)
            snippet = content[context_start:context_end]
            
            print(f"Snippet: {snippet[:200]}...")
            
            # Create fixed version by properly escaping curly braces
            fixed_template = template
            
            # Fix JavaScript sections by escaping curly braces
            if "function toggleFix" in template:
                print("Attempting to fix JavaScript function toggleFix...")
                fixed_template = re.sub(
                    r'function toggleFix\(id\) \{(.*?)\}',
                    lambda m: m.group(0).replace('{', '{{').replace('}', '}}'),
                    fixed_template,
                    flags=re.DOTALL
                )
            
            # Fix any unescaped curly braces in CSS
            if ".hidden {" in template:
                print("Attempting to fix CSS rules...")
                fixed_template = re.sub(
                    r'\.hidden \{(.*?)\}',
                    lambda m: m.group(0).replace('{', '{{').replace('}', '}}'),
                    fixed_template,
                    flags=re.DOTALL
                )
            
            # Update the fixed content
            fixed_content = fixed_content.replace(match.group(0), f'f"""{fixed_template}"""')
    
    # Write the fixed file
    backup_path = file_path.with_suffix('.py.old')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"\nFixed file saved to {file_path}")
    print(f"Original backup saved to {backup_path}")

if __name__ == "__main__":
    fix_validator_syntax()
