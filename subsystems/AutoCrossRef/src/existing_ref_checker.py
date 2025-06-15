#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to check if a resolved target path is already referenced in a source file."""
# 
# @references:
#   - subsystems/AutoCrossRef/src/existing_ref_checker.py

import os
import re
from typing import Dict, Any, List

# Assuming EGOS_PROJECT_ROOT might be needed for resolving paths if not absolute
EGOS_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def get_references_from_block(content: str, comment_prefix: str = "") -> List[str]:
    """
    Extracts all reference items from an @references: block.
    A reference item can be a direct path or a markdown link path.
    Handles optional comment prefixes for languages like Python.
    """
    references = []
    in_references_block = False
    # Regex for Markdown link: captures text in group 1, path in group 2
    markdown_link_regex = re.compile(r"^\s*[-\*]?\s*\[([^\]]*)\]\(([^)]+)\)")

    # Determine the actual header string based on comment_prefix
    block_header_md = "@references:"
    # For Python, the actual header in file is like "# @references:"
    # The comment_prefix passed from ref_injector is "#"
    # The line in file will be checked against (comment_prefix + "@references:").lower()
    # or just "@references:".lower() for MD
    
    # Construct the expected header string for commented blocks
    # If comment_prefix is "#", header becomes "#@references:"
    # If comment_prefix is "# ", header becomes "# @references:"
    # The ref_injector uses "#" as prefix, and then adds " @references:", so it becomes "# @references:"
    # Let's ensure this logic is robust for various comment_prefix styles.
    # The key is that the line starts with comment_prefix and then contains "@references:"
    
    for line_number, line_content in enumerate(content.splitlines()):
        stripped_line = line_content.strip()

        if not in_references_block:
            # Check for Markdown block start
            if stripped_line.lower().startswith(block_header_md.lower()):
                 # Ensure it's not a commented out MD block header if comment_prefix is active
                if not (comment_prefix and line_content.lstrip().startswith(comment_prefix)):
                    in_references_block = True
                    # If we just entered a MD block, ensure comment_prefix is cleared for item parsing
                    # This is a local shadow, not changing the arg. Better: pass effective_prefix to item parser.
                    # For now, this function's comment_prefix arg is for the *block type*.
                    # Let's assume if it's MD, comment_prefix for items is empty.
                    # This is getting complex. Let's simplify: the passed comment_prefix defines the block.
                    # effective_item_comment_prefix = "" # For MD items
                    continue
            # Check for Python-style commented block start
            elif comment_prefix and stripped_line.lower().startswith(f"{comment_prefix.rstrip()}@references:".lower()): # e.g., "#@references:" or "# @references:"
                in_references_block = True
                # effective_item_comment_prefix = comment_prefix # For PY items
                continue
            elif comment_prefix and stripped_line.lower().startswith(f"{comment_prefix.rstrip()} @references:".lower()): # Handles if ref_injector adds a space
                in_references_block = True
                # effective_item_comment_prefix = comment_prefix
                continue

        else: # We are inside a references block
            current_line_is_commented = comment_prefix and line_content.lstrip().startswith(comment_prefix)
            
            # Prepare line for item parsing: remove comment_prefix if it exists and matches
            item_line_for_parsing = stripped_line
            if current_line_is_commented:
                item_line_for_parsing = line_content.lstrip()[len(comment_prefix):].lstrip()
            
            # Check for end of block conditions
            # 1. Empty line (after potential comment stripping)
            if not item_line_for_parsing: # An empty line or a line that was purely a comment
                # If the original line was just the comment_prefix (e.g., "#" or "# "), it's a blank commented line.
                # These can exist within blocks for spacing.
                # However, if item_line_for_parsing is empty, it means it's effectively an empty data line.
                # A truly blank line (no comment) or a line that becomes empty after stripping comment prefix
                # and list markers should terminate the block.
                # Let's refine: if original stripped_line is empty OR item_line_for_parsing is empty, consider termination.
                if not stripped_line: # Original line was blank
                    in_references_block = False
                    continue
                # If it was a comment line that became empty (e.g. "#   "), it might be an item.
                # This needs to be handled by list marker check. If no list marker, it's an empty item or end.
                # For now, if item_line_for_parsing is empty, and it's not a list marker, it's the end.
                if not (item_line_for_parsing.startswith(('-', '*'))):
                    in_references_block = False
                    continue
            
            # 2. Line doesn't conform to item structure (e.g., not a list item, or not commented in PY block)
            # For Python blocks, items must also start with the comment_prefix
            if comment_prefix and not current_line_is_commented:
                in_references_block = False
                continue # This line is not part of the commented block

            # For Markdown blocks (no comment_prefix active for items)
            if not comment_prefix and not (line_content.startswith('  ') or line_content.startswith('\t') or stripped_line.startswith(('-', '*'))):
                in_references_block = False
                continue

            # At this point, item_line_for_parsing is the content of the item, with outer comment stripped.
            # Now, strip common list markers like '-' or '*'
            path_candidate_line = item_line_for_parsing
            if item_line_for_parsing.startswith(('-', '*')):
                path_candidate_line = item_line_for_parsing[1:].lstrip()
            
            # If after stripping list marker, the line is empty, skip it (e.g. "# - ")
            if not path_candidate_line:
                continue

            md_match = markdown_link_regex.match(path_candidate_line) # Check on the item_line_for_parsing
            if md_match:
                references.append(md_match.group(2).strip()) # Path is in group 2
            elif path_candidate_line: # If not a markdown link, take the whole line as path
                references.append(path_candidate_line.strip())
                
    return references

def is_reference_present(source_file_path: str, 
                           target_file_path: str, 
                           config: Dict[str, Any]) -> bool:
    """
    Checks if the target_file_path is already listed in an @references: block
    within the source_file_path.

    Args:
        source_file_path: Absolute path to the source file.
        target_file_path: Absolute path to the target file to check for.
        config: The AutoCrossRef configuration (currently unused in this basic version).

    Returns:
        True if the reference is found and matches, False otherwise.
    """
    try:
        with open(source_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except IOError:
        print(f"ExistingRefChecker: Could not read source file {source_file_path}", flush=True)
        return False # Cannot determine if reference is present

    # Determine file type and set appropriate comment prefix
    file_extension = os.path.splitext(source_file_path)[1].lower()
    is_python_file = file_extension == '.py'
    
    # Consistent with ref_injector.py's _find_insertion_point_and_block_details
    current_comment_prefix = "#" if is_python_file else ""
    
    paths_in_block = get_references_from_block(content, current_comment_prefix)
    normalized_target_path = os.path.normpath(target_file_path)
    source_dir = os.path.dirname(source_file_path)

    for path_str in paths_in_block:
        if not path_str: continue

        normalized_ref_path = ''
        if os.path.isabs(path_str):
            normalized_ref_path = os.path.normpath(path_str)
        else:
            # Resolve relative to source file's directory
            normalized_ref_path = os.path.normpath(os.path.join(source_dir, path_str))
        
        # Debug print
        # print(f"DEBUG: Comparing Ref: '{normalized_ref_path}' (from '{path_str}') WITH Target: '{normalized_target_path}'", flush=True)

        if normalized_ref_path == normalized_target_path:
            # print(f"DEBUG: Match found!", flush=True)
            return True
        
        # If path_str was relative and didn't match when resolved from source_dir,
        # try resolving from EGOS_PROJECT_ROOT if it doesn't start with '.' or '..'
        # This handles project-root relative paths like 'docs/file.md'
        if not os.path.isabs(path_str) and not path_str.startswith(('.', '..')):
            project_root_resolved_path = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, path_str))
            # print(f"DEBUG: Trying project root. Ref: '{project_root_resolved_path}' WITH Target: '{normalized_target_path}'", flush=True)
            if project_root_resolved_path == normalized_target_path:
                # print(f"DEBUG: Match found via project root!", flush=True)
                return True
        
        # TODO: Add more sophisticated checks, e.g.:
        # - Checking if target_file_path is equivalent (e.g. different casing on case-insensitive FS)

    return False

if __name__ == '__main__':
    from config_loader import load_config
    app_config = load_config()

    # Create dummy files for testing
    dummy_source_content_template = """
Some text before.

@references:
  - {ref1}
  - [Some Link]({ref2})
  - {ref3}

Some text after.
    """
    dummy_target_path = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, "docs/standards/KOIOS_PDD_Standard.md"))
    dummy_target_path_rel_from_src = "../docs/standards/KOIOS_PDD_Standard.md" # if source is in subsystems/AutoCrossRef/src
    dummy_target_path_abs = "C:/EGOS/docs/standards/KOIOS_PDD_Standard.md"

    # Test case 1: Absolute path match
    source_content1 = dummy_source_content_template.format(
        ref1=dummy_target_path_abs,
        ref2="another/link.md",
        ref3="yet/another.md"
    )
    # Test case 2: Relative path match
    source_content2 = dummy_source_content_template.format(
        ref1="some/other.md",
        ref2=dummy_target_path_rel_from_src, # This path needs to resolve correctly from dummy_source_file
        ref3="yet/another.md"
    )
    # Test case 3: No match
    source_content3 = dummy_source_content_template.format(
        ref1="some/other.md",
        ref2="another/link.md",
        ref3="yet/another.md"
    )
    # Test case 4: Reference block with mixed content and tricky formatting
    source_content4 = """
@references:
    - C:/EGOS/MQP.md
    - [KOIOS PDD Standard](docs/standards/KOIOS_PDD_Standard.md) 
    - subsystems/AutoCrossRef/README.md
Not a reference.
@references:  # Should ignore this second block for now, or handle multiple
    - docs/some_other_doc.md
    """

    dummy_source_file = os.path.join(os.path.dirname(__file__), "_test_source_ref_checker.md")

    def run_test(content, target_path, test_name):
        with open(dummy_source_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        present = is_reference_present(dummy_source_file, target_path, app_config)
        print(f"Test '{test_name}': Target '{os.path.basename(target_path)}' present? {present}", flush=True)
        return present

    print("ExistingRefChecker: Running tests...", flush=True)
    run_test(source_content1, dummy_target_path, "Absolute Path Match")
    # For relative path test, source_file_path is dummy_source_file in AutoCrossRef/src/
    # So dummy_target_path_rel_from_src ("../docs/standards/KOIOS_PDD_Standard.md") should resolve to
    # AutoCrossRef/src/../docs/standards/KOIOS_PDD_Standard.md -> AutoCrossRef/docs/standards/KOIOS_PDD_Standard.md
    # This is NOT the same as dummy_target_path. Let's adjust the relative path for the test.
    # If dummy_source_file is C:\EGOS\subsystems\AutoCrossRef\src\_test_source_ref_checker.md
    # And target is C:\EGOS\docs\standards\KOIOS_PDD_Standard.md
    # Relative path from src to EGOS root is ../../..
    # So, ../../../docs/standards/KOIOS_PDD_Standard.md
    correct_rel_path_for_test2 = "../../../docs/standards/KOIOS_PDD_Standard.md"
    source_content2_corrected = dummy_source_content_template.format(
        ref1="some/other.md",
        ref2=correct_rel_path_for_test2,
        ref3="yet/another.md"
    )
    run_test(source_content2_corrected, dummy_target_path, "Relative Path Match")
    run_test(source_content3, dummy_target_path, "No Match")
    
    # Test with source_content4
    print("\nTesting content4:", flush=True)
    target_mqp = "C:/EGOS/MQP.md"
    target_koios_from_root = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, "docs/standards/KOIOS_PDD_Standard.md"))
    target_autocrossref_readme_from_root = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, "subsystems/AutoCrossRef/README.md"))

    run_test(source_content4, target_mqp, "Content4 - MQP (abs)")
    run_test(source_content4, target_koios_from_root, "Content4 - KOIOS (rel from EGOS root)")
    run_test(source_content4, target_autocrossref_readme_from_root, "Content4 - AutoCrossRef README (rel from EGOS root)")

    # Clean up dummy file
    if os.path.exists(dummy_source_file):
        os.remove(dummy_source_file)
    print("\nExistingRefChecker: Tests finished.", flush=True)