#!/usr/bin/env python
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# scripts/another_script.py

# Reference to new_module.py
# Assuming src directory is handled by PYTHONPATH or reference_patterns
# For testing, let's assume a simple import if new_module.py is in src
# and the checker is run from a context where src is importable or patterns match `src/new_module.py`

def main():
    print("Another script running.")
    # The presence of the string 'new_module.py' or 'src.new_module' will be searched by patterns
    # Example: import src.new_module
    # Example: from src import new_module
    # Text reference to new_module_notes.md
    # This script complements new_module_notes.md for extended details.
    print("Checking notes in new_module_notes.md")

if __name__ == "__main__":
    main()