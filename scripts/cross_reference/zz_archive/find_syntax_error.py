#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Syntax Error Finder

This script attempts to parse a Python file line by line to identify syntax errors.

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

import sys
from pathlib import Path

def find_syntax_error(file_path):
    """Find syntax errors in a Python file by parsing it line by line."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    # Try to parse the file in chunks to locate the error
    for i in range(len(lines)):
        try:
            chunk = ''.join(lines[:i+1])
            compile(chunk, file_path.name, 'exec')
        except SyntaxError as e:
            line_num = e.lineno
            print(f"SyntaxError at line {line_num}: {e}")
            
            # Print the offending line and surrounding context
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 2)
            
            print("\nContext:")
            for j in range(start, end):
                prefix = ">>> " if j == line_num - 1 else "    "
                print(f"{prefix}{j+1}: {lines[j].rstrip()}")
            
            return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_syntax_error.py <file_path>")
        sys.exit(1)
    
    find_syntax_error(sys.argv[1])
