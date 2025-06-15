#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for injecting new cross-references into files, adhering to standardized
placement rules for @references: blocks.
"""
# 
# @references:
#   - subsystems/AutoCrossRef/src/ref_injector.py

import os
import shutil
import datetime
import re
from typing import Dict, Any, List, Tuple, Optional

# Assuming existing_ref_checker is in the same directory or PYTHONPATH
from .existing_ref_checker import get_references_from_block

EGOS_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def _create_backup(file_path: str, config: Dict[str, Any]) -> Optional[str]:
    """Creates a backup of the file if backup is enabled in config.
    Returns the backup path on success, None otherwise or if disabled.
    """
    backup_options = config.get('backup_options', {})
    if not backup_options.get('enabled', False):
        return None

    backup_dir_config = backup_options.get('directory', 'C:/EGOS/backups/autocrossref_default/')
    # Ensure backup_dir is absolute. If not, make it relative to EGOS_PROJECT_ROOT
    if not os.path.isabs(backup_dir_config):
        backup_dir = os.path.join(EGOS_PROJECT_ROOT, backup_dir_config)
    else:
        backup_dir = backup_dir_config
        
    ts_format = backup_options.get('timestamp_format', '%Y%m%d_%H%M%S')
    
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime(ts_format)
        base_filename = os.path.basename(file_path)
        backup_filename = f"{os.path.splitext(base_filename)[0]}_{timestamp}{os.path.splitext(base_filename)[1]}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        print(f"RefInjector: Backup created at {backup_path}", flush=True)
        return backup_path
    except Exception as e:
        print(f"RefInjector: Error creating backup for {file_path}: {e}", flush=True)
        return None

def _find_insertion_point_and_block_details(lines: List[str], file_type: str) -> Tuple[int, Optional[str], Optional[str], Optional[List[str]]]:
    """Finds the insertion point for the @references block and details of any existing block.

    Returns a tuple: (insertion_index, existing_block_indent, existing_block_comment_char, existing_block_content_lines)
    insertion_index: The line number (0-indexed) where the new block should be inserted.
    existing_block_indent: The indentation string (e.g., '  ') of the existing block, if found.
    existing_block_comment_char: The comment character (e.g., '#', '<!--') of the existing block, if found.
    existing_block_content_lines: A list of strings, each being a content line from the existing block (without comment chars/indent), if found.
    """
    shebang_present = lines and lines[0].startswith('#!')
    encoding_re = re.compile(r"^#\s*-\*-\s*coding:\s*([-\w.]+)\s*-\*-\s*(#.*)?$")
    existing_block_re_str = r"^(\s*)({comment_chars}\s*@references:.*)"
    
    insertion_point = 0
    if shebang_present:
        insertion_point = 1
    
    if len(lines) > insertion_point and encoding_re.match(lines[insertion_point]):
        insertion_point += 1
    
    # Skip any blank lines immediately after shebang/encoding or at the start of the file
    while insertion_point < len(lines) and not lines[insertion_point].strip():
        insertion_point += 1

    # Python specific: check for module-level docstring
    if file_type == 'py':
        # Check for module docstring (single or multi-line)
        if insertion_point < len(lines) and (lines[insertion_point].strip().startswith('"""') or lines[insertion_point].strip().startswith("'''")):
            docstring_marker = lines[insertion_point].strip()[:3]
            if lines[insertion_point].strip().endswith(docstring_marker) and len(lines[insertion_point].strip()) > 5: # Single line docstring
                insertion_point +=1
            else: # Potentially multi-line docstring
                insertion_point +=1 # Move past the opening docstring line
                while insertion_point < len(lines) and not lines[insertion_point].strip().endswith(docstring_marker):
                    insertion_point += 1
                if insertion_point < len(lines): # Found closing marker
                    insertion_point += 1 # Move past the closing docstring line
            # Skip blank lines after docstring
            while insertion_point < len(lines) and not lines[insertion_point].strip():
                insertion_point += 1

    # Search for existing @references block
    comment_chars_map = {
        'py': '#',
        'md': '<!--',
        'default': '#'
    }
    comment_char_pattern = re.escape(comment_chars_map.get(file_type, comment_chars_map['default']))
    if file_type == 'md': # Markdown can also have HTML comments or just be plain
        # Regex to find @references: possibly inside an HTML comment or as plain text
        # It captures indent, the comment opening (if any), @references:, and the comment closing (if any)
        # Group 1: Indentation
        # Group 2: Optional HTML comment start '<!--'
        # Group 3: '@references:' with optional surrounding whitespace
        # Group 4: Optional HTML comment end '-->'
        # Group 5: The actual content line (including @references:)
        existing_block_re = re.compile(r"^(\s*)(<!--\s*)?(@references:.*?)(\s*-->)?(.*?)$\n", re.IGNORECASE)
        ref_content_re = re.compile(r"^(\s*)(?:<!--\s*)?(?:-\s*)?(.*?)(?:\s*-->)?$\n")
    else:
        existing_block_re = re.compile(f"^(\s*)({comment_char_pattern}\s*@references:.*?)$\n", re.IGNORECASE)
        ref_content_re = re.compile(f"^(\s*){comment_char_pattern}\s*(?:-\s*)?(.*?)$\n")

    for i, line in enumerate(lines):
        match = existing_block_re.match(line)
        if match:
            # For MD, if it's an HTML comment, the comment char is '<!--'
            # otherwise, if it's just '@references:' it has no specific comment char for the block itself.
            current_comment_char = ''
            if file_type == 'md':
                if match.group(2) and match.group(4): # HTML comment '<!-- ... -->'
                    current_comment_char = '<!--'
            else: # For Python or others
                current_comment_char = comment_chars_map.get(file_type, comment_chars_map['default'])

            # Start collecting content from the line after @references:
            # The insertion point for new refs would be *inside* this block.
            block_content_lines = []
            block_indent = match.group(1) # Indentation of the @references: line
            
            # Check if the @references: line itself has content like '@references: [Content Here]'
            # This is unusual but handle it.
            # For MD: match.group(3) is '@references:...' potentially with content
            # For PY: match.group(2) is '# @references:...' potentially with content
            header_line_content_match = None
            if file_type == 'md':
                # Extract content from the '@references:' line itself if it's not just the header
                # The regex for md already tries to capture this in group 3.
                # We need to strip '@references:' and comment markers.
                temp_content = match.group(3).lower().replace('@references:', '').strip()
                if match.group(2) and match.group(4): # if it's an HTML comment
                    temp_content = temp_content.replace('-->', '').strip()
                if temp_content and not temp_content.startswith('- '):
                    # This implies content on the same line as @references:, not typical
                    # For now, we'll assume content starts on next line or is properly formatted with '- '
                    pass 
            else: # Python
                header_line_content_match = re.match(f"^(\s*){comment_char_pattern}\s*@references:\s*(?:-\s*)?(.*)", line, re.IGNORECASE)
                if header_line_content_match and header_line_content_match.group(2).strip():
                    block_content_lines.append(header_line_content_match.group(2).strip())

            # Collect subsequent lines that are part of the block
            for j in range(i + 1, len(lines)):
                sub_line = lines[j]
                content_match = ref_content_re.match(sub_line)
                if content_match and content_match.group(1) == block_indent: # Line is part of the block
                    actual_content = content_match.group(2).strip()
                    if actual_content: # Only add if there's actual content
                        block_content_lines.append(actual_content)
                else: # Line is not part of the block (different indent or not a comment/ref line)
                    break
            return i + 1 + len(block_content_lines), block_indent, current_comment_char, block_content_lines

    return insertion_point, None, None, None # No existing block found

def _format_reference_for_file_type(reference: str, file_type: str, indent: str, comment_char: Optional[str]) -> str:
    """Formats a single reference line based on file type, indent, and comment character."""
    if file_type == 'md':
        if comment_char == '<!--': # Inside an HTML comment block
            return f"{indent}  - {reference}\n"
        else: # Plain markdown list or no existing block (will become plain list)
            return f"{indent}- {reference}\n"
    else: # Python or default
        actual_comment_char = comment_char if comment_char is not None else '#'
        return f"{indent}{actual_comment_char}   - {reference}\n"

def inject_reference(
    file_path: str, 
    reference_to_inject: str, 
    absolute_reference_path: str, 
    config: Dict[str, Any], 
    is_dry_run: bool = False,
    # New parameters for hierarchical reference standard
    references_to_ensure: Optional[List[str]] = None,
    all_valid_core_refs: Optional[List[str]] = None,
    mode: str = 'fix-core',
    create_backup: bool = True
) -> Dict[str, Any]:
    """Injects cross-references into a file according to the hierarchical reference standard.
    
    This function has two operational modes:
    1. Legacy mode: When called with just reference_to_inject, it behaves like the original function
       and adds a single reference if not present.
    2. Standard mode: When called with references_to_ensure and all_valid_core_refs, it:
       - Removes self-references
       - Purges legacy references not in all_valid_core_refs
       - Ensures all references in references_to_ensure are present
       - Operates according to the specified mode

    Args:
        file_path: Path to the file to modify.
        reference_to_inject: The reference string to inject (legacy mode only).
        absolute_reference_path: The absolute path of the file being referenced (legacy mode).
        config: Configuration dictionary, possibly containing backup options.
        is_dry_run: If True, no changes are written to disk.
        references_to_ensure: List of references that must be present in the file.
        all_valid_core_refs: Complete list of valid core references for purging legacy refs.
        mode: Operation mode - 'diagnose', 'fix-core', or 'full'.
        create_backup: Whether to create a backup before modifying (if enabled in config).

    Returns:
        A dictionary with details of the operation:
        {
            'file_path': str,       # The processed file path
            'status': str,          # 'modified', 'skipped_idempotent', 'error_backup',
                                    # 'error_read', 'error_write', 'error_insertion_point',
                                    # 'dry_run_would_modify', 'unknown', 'purged_legacy_refs',
                                    # 'non_compliant'
            'message': str,         # Description of the outcome
            'backup_path': Optional[str], # Path to backup if created
            'content_changed': bool, # True if the file content was (or would be) changed
            'references_added': List[str], # References that were added
            'references_purged': List[str], # Legacy references that were removed
            'is_compliant': bool,   # Whether the file is compliant with the standard
            'missing_references': List[str] # References that should be present but aren't
        }
    """
    result = {
        "file_path": file_path,
        "status": "unknown",
        "message": "Processing did not complete as expected or was not fully handled.",
        "backup_path": None,
        "content_changed": False,
        "references_added": [],
        "references_purged": [],
        "is_compliant": True,  # Assume compliant until proven otherwise
        "missing_references": []
    }
    
    # Determine if we're in legacy mode or standard mode
    using_standard_mode = references_to_ensure is not None and all_valid_core_refs is not None
    
    # If in standard mode but no references to ensure, this is a no-op
    if using_standard_mode and not references_to_ensure:
        result["status"] = "skipped_idempotent"
        result["message"] = "No references to ensure specified. No changes made."
        return result
        
    # In standard mode, diagnose mode means dry run
    if using_standard_mode and mode == 'diagnose':
        is_dry_run = True

    backup_options = config.get('backup_options', {})
    if backup_options.get('enabled', False) and create_backup and not is_dry_run:
        backup_path_val = _create_backup(file_path, config)
        if backup_path_val is None:
            result["status"] = "error_backup"
            result["message"] = f"Backup creation failed for {file_path}. Halting modification."
            print(f"RefInjector: {result['message']}", flush=True)
            return result
        result["backup_path"] = backup_path_val
    else:
        result["backup_path"] = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, IOError) as e_utf8:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
            print(f"RefInjector: Warning - File {file_path} successfully read with latin-1 encoding after UTF-8 failure: {e_utf8}", flush=True)
        except Exception as e_fallback:
            result["status"] = "error_read"
            result["message"] = f"Error reading file {file_path}. UTF-8 failed: {str(e_utf8)}. Fallback latin-1 failed: {str(e_fallback)}."
            print(f"RefInjector: {result['message']}", flush=True)
            return result
    except Exception as e_general:
        result["status"] = "error_read"
        result["message"] = f"General error reading file {file_path}: {str(e_general)}."
        print(f"RefInjector: {result['message']}", flush=True)
        return result

    file_type = os.path.splitext(file_path)[1].lstrip('.')
    insertion_point, existing_block_indent, existing_block_comment_char, existing_block_content = _find_insertion_point_and_block_details(lines, file_type)

    # Extract the relative path of the current file for self-reference detection
    rel_file_path = os.path.relpath(file_path, EGOS_PROJECT_ROOT).replace('\\', '/')
    
    # Get existing references if a block exists
    existing_references = []
    if existing_block_content is not None:
        existing_references = get_references_from_block('\n'.join(existing_block_content))
    
    # Normalize all paths for comparison
    normalized_existing_refs = [os.path.normpath(ref) for ref in existing_references]
    
    if using_standard_mode:
        # STANDARD MODE PROCESSING
        # 1. Identify self-references to remove
        normalized_rel_file_path = os.path.normpath(rel_file_path)
        # Treat both exact relative path matches and plain-basename matches as self-references
        self_references = [ref for ref in existing_references 
                           if os.path.normpath(ref) == normalized_rel_file_path
                           or os.path.basename(os.path.normpath(ref)) == os.path.basename(normalized_rel_file_path)]
        
        # 2. Identify legacy references to purge (not in all_valid_core_refs and not self)
        normalized_valid_core_refs = [os.path.normpath(ref) for ref in all_valid_core_refs]
        legacy_references = [ref for ref in existing_references 
                           if os.path.normpath(ref) not in normalized_valid_core_refs 
                           and os.path.normpath(ref) != normalized_rel_file_path]
        
        # 3. Identify references to add (in references_to_ensure but not in existing_references)
        normalized_refs_to_ensure = [os.path.normpath(ref) for ref in references_to_ensure]
        references_to_add = [ref for i, ref in enumerate(references_to_ensure) 
                           if os.path.normpath(ref) not in normalized_existing_refs]
        
        # 4. Check compliance
        missing_refs = [ref for ref in references_to_ensure 
                      if os.path.normpath(ref) not in normalized_existing_refs]
        has_legacy_or_self_refs = bool(self_references or legacy_references)
        is_compliant = not missing_refs and not has_legacy_or_self_refs
        
        # Update result with compliance info
        result["is_compliant"] = is_compliant
        result["missing_references"] = missing_refs
        result["references_purged"] = self_references + legacy_references
        
        # If diagnose mode, just report without changes
        if mode == 'diagnose':
            result["status"] = "diagnose_only"
            result["message"] = f"Diagnose mode: {len(missing_refs)} missing refs, {len(self_references)} self refs, {len(legacy_references)} legacy refs."
            result["references_added"] = references_to_add
            return result
        
        # If no changes needed, return early
        if is_compliant and not references_to_add and not self_references and not legacy_references:
            result["status"] = "skipped_idempotent"
            result["message"] = "File is already compliant with reference standard. No changes needed."
            return result
            
        # If dry run but would modify, return early
        if is_dry_run:
            result["status"] = "dry_run_would_modify"
            result["message"] = f"[DRY RUN] Would add {len(references_to_add)} refs, remove {len(self_references)} self refs, purge {len(legacy_references)} legacy refs."
            result["references_added"] = references_to_add
            return result
    else:
        # LEGACY MODE PROCESSING - Single reference injection
        # Check if the reference is already in the list
        reference_present = os.path.normpath(reference_to_inject) in normalized_existing_refs
                
        if reference_present:
            result["status"] = "skipped_idempotent"
            result["message"] = f"Reference '{reference_to_inject}' already present. No changes made."
            result["content_changed"] = False
            if not is_dry_run:
                print(f"RefInjector: {result['message']} in {file_path}", flush=True)
            return result

    # Determine indent and comment char for new block/addition
    indent = existing_block_indent if existing_block_indent is not None else ''
    # For MD, if no block exists, comment_char should be None to format as plain list
    # For PY, if no block, default to '#'
    comment_char_for_new_ref = existing_block_comment_char
    if existing_block_content is None: # No existing block
        if file_type == 'py':
            comment_char_for_new_ref = '#'
        elif file_type == 'md':
            comment_char_for_new_ref = None # Will create a plain MD list
        else:
            comment_char_for_new_ref = '#'
    
    # For legacy mode, format a single reference line
    if not using_standard_mode:
        new_ref_line = _format_reference_for_file_type(reference_to_inject, file_type, indent, comment_char_for_new_ref)

        if is_dry_run:
            result["status"] = "dry_run_would_modify"
            result["message"] = f"[DRY RUN] Would inject '{reference_to_inject}'."
            result["content_changed"] = False # content_changed is False because no actual write
            print(f"RefInjector: {result['message']} for {file_path} at line approx {insertion_point}", flush=True)
            return result
    
    # Make a mutable copy of the content lines
    new_content_lines = list(lines)
    
    # STANDARD MODE PROCESSING - Rebuild reference block if needed
    if using_standard_mode:
        # If we have an existing block, we'll rebuild it completely
        if existing_block_content is not None:
            # First, remove the existing block entirely
            block_start_line = insertion_point - len(existing_block_content)
            for _ in range(len(existing_block_content)):
                new_content_lines.pop(block_start_line)
            
            # Now create a new block with the correct references
            # Start with all existing references
            references_to_keep = []
            for ref in existing_references:
                # Skip self-references and legacy references
                if (os.path.normpath(ref) == os.path.normpath(rel_file_path) or 
                    (all_valid_core_refs and os.path.normpath(ref) not in 
                     [os.path.normpath(valid_ref) for valid_ref in all_valid_core_refs])):
                    continue
                references_to_keep.append(ref)
            
            # Add the references we need to ensure
            for ref in references_to_ensure:
                if ref not in references_to_keep:
                    references_to_keep.append(ref)
            
            # Sort references for consistency
            references_to_keep.sort()
            
            # Create the new block
            header_comment_char = '#' if file_type == 'py' else '<!--'
            header_closer = '' if file_type == 'py' else ' -->'
            if file_type == 'md' and comment_char_for_new_ref is None:
                header_comment_char = ''
                header_closer = ''
            
            # Insert the header (only once)
            ref_block_header = f"{indent}{header_comment_char} @references:{header_closer}\n"
            new_content_lines.insert(block_start_line, ref_block_header)
            insertion_point = block_start_line + 1
            
            # Insert each reference
            for ref in references_to_keep:
                ref_line = _format_reference_for_file_type(ref, file_type, indent, comment_char_for_new_ref)
                new_content_lines.insert(insertion_point, ref_line)
                insertion_point += 1
                result["references_added"].append(ref)
            
            # Add a trailing newline if needed
            if insertion_point < len(new_content_lines) and new_content_lines[insertion_point].strip() != "":
                new_content_lines.insert(insertion_point, '\n')
        else:
            # No existing block, create a new one with all references to ensure
            header_comment_char = '#'
            header_closer = ''
            if file_type == 'md':
                header_comment_char = '<!--'
                header_closer = ' -->'
                if comment_char_for_new_ref is None:
                    header_comment_char = ''
                    header_closer = ''
            
            # Add spacing before the block if needed
            if file_type == 'py' and insertion_point == 0 and new_content_lines and new_content_lines[0].strip() != "":
                new_content_lines.insert(insertion_point, '\n')
                insertion_point += 1
            elif insertion_point > 0 and new_content_lines[insertion_point-1].strip() != "":
                new_content_lines.insert(insertion_point, '\n')
                insertion_point += 1
            
            # Insert the header
            ref_block_header = f"{indent}{header_comment_char} @references:{header_closer}\n"
            new_content_lines.insert(insertion_point, ref_block_header)
            insertion_point += 1
            
            # Insert each reference
            for ref in sorted(references_to_ensure):
                ref_line = _format_reference_for_file_type(ref, file_type, indent, comment_char_for_new_ref)
                new_content_lines.insert(insertion_point, ref_line)
                insertion_point += 1
                result["references_added"].append(ref)
            
            # Add a trailing newline if needed
            if insertion_point < len(new_content_lines) and new_content_lines[insertion_point].strip() != "":
                new_content_lines.insert(insertion_point, '\n')
            elif insertion_point == len(new_content_lines):
                new_content_lines.append('\n')
    else:
        # LEGACY MODE PROCESSING - Single reference injection
        if existing_block_content is not None:
            # Add to existing block. Insertion point is inside the block.
            new_content_lines.insert(insertion_point, new_ref_line)
            result["references_added"].append(reference_to_inject)
        else:
            # Create new block
            header_comment_char = '#'
            header_closer = ''
            if file_type == 'md':
                header_comment_char = '<!--'
                header_closer = ' -->'
                if comment_char_for_new_ref is None:
                    header_comment_char = '' # No comment for plain MD list header
                    header_closer = ''

            ref_block_header = f"{indent}{header_comment_char} @references:{header_closer}\n"
            if file_type == 'py' and insertion_point == 0 and not (new_content_lines and new_content_lines[0].strip() == ""):
                # If python file is empty or first line is not blank, add a newline before the block
                if new_content_lines and new_content_lines[0].strip() != "":
                    new_content_lines.insert(insertion_point, '\n')
                    insertion_point += 1
            elif insertion_point > 0 and new_content_lines[insertion_point-1].strip() != "":
                # Add a preceding newline if the line before insertion isn't blank (and not start of file)
                new_content_lines.insert(insertion_point, '\n')
                insertion_point += 1

            new_content_lines.insert(insertion_point, ref_block_header)
            insertion_point += 1
            new_content_lines.insert(insertion_point, new_ref_line)
            result["references_added"].append(reference_to_inject)

            # Add a trailing newline if the line after insertion isn't blank (and not end of file)
            if insertion_point < len(new_content_lines) -1 and new_content_lines[insertion_point+1].strip() != "":
                new_content_lines.insert(insertion_point + 1, '\n')
            elif insertion_point == len(new_content_lines) -1: # if inserted at the very end
                new_content_lines.append('\n')

    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.writelines(new_content_lines)
        
        # Set status and message based on mode
        if using_standard_mode:
            # In standard mode, we might have added multiple references and/or purged legacy refs
            refs_added_count = len(result["references_added"])
            refs_purged_count = len(result["references_purged"])
            
            if refs_added_count > 0 and refs_purged_count > 0:
                result["status"] = "modified"
                result["message"] = f"Added {refs_added_count} references and purged {refs_purged_count} legacy references."
            elif refs_added_count > 0:
                result["status"] = "modified"
                result["message"] = f"Added {refs_added_count} references."
            elif refs_purged_count > 0:
                result["status"] = "purged_legacy_refs"
                result["message"] = f"Purged {refs_purged_count} legacy references."
            else:
                # This shouldn't happen as we check for no changes earlier
                result["status"] = "skipped_idempotent"
                result["message"] = "No changes needed, file is already compliant."
                result["content_changed"] = False
                return result
                
            # Check compliance in full mode
            if mode == 'full' and not result["is_compliant"]:
                result["status"] = "non_compliant"
                result["message"] += f" File is non-compliant: {len(result['missing_references'])} missing references."
        else:
            # Legacy mode - single reference injection
            result["status"] = "modified"
            result["message"] = f"Successfully modified to include '{reference_to_inject}'."
        
        result["content_changed"] = True
        print(f"RefInjector: {result['message']} for {file_path}", flush=True)
        return result
    except Exception as e:
        result["status"] = "error_write"
        result["message"] = f"Error writing to file: {str(e)}."
        print(f"RefInjector: {result['message']} for {file_path}", flush=True)
        # TODO: Consider attempting to restore from backup if a backup_path exists
        return result

# --- Test Suite (Potentially Broken by return type changes) --- 
if __name__ == "__main__":
    print("RefInjector: Starting test execution...", flush=True)
    # Setup a temporary test directory
    test_dir = os.path.join(EGOS_PROJECT_ROOT, "_test_ref_injector")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    print(f"RefInjector: Test directory created at {test_dir}", flush=True)

    # Mock config for testing
    test_config = {
        'backup_options': {
            'enabled': True,
            'directory': os.path.join(test_dir, "backups"), # Relative to test_dir for cleanup
            'timestamp_format': '%Y%m%d_%H%M%S%f'
        }
    }
    os.makedirs(test_config['backup_options']['directory'], exist_ok=True)

    # Global test status
    test_status = {"all_passed": True, "tests_run": 0, "tests_failed": 0}

    def _run_test(test_name, filename, initial_content, ref_to_inject, abs_ref_path, expected_parts_in_final_content, is_dry_run=False, expected_return_status=None, expect_change=True):
        test_status["tests_run"] += 1
        full_path = os.path.join(test_dir, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        print(f"\n--- Running Test: {test_name} ---", flush=True)
        print(f"Initial content for {filename}:\n{initial_content}", flush=True)
        
        # Call inject_reference
        # IMPORTANT: The test suite now needs to expect a dictionary
        result_dict = inject_reference(full_path, ref_to_inject, abs_ref_path, test_config, is_dry_run)
        
        print(f"inject_reference returned: {result_dict}", flush=True)

        # Basic check on result_dict structure
        if not isinstance(result_dict, dict) or not all(k in result_dict for k in ['status', 'message', 'content_changed']):
            print(f"FAIL: {test_name} - Return value is not a valid result dictionary.", flush=True)
            test_status["all_passed"] = False
            test_status["tests_failed"] += 1
            return

        # Check status if expected_return_status is provided
        if expected_return_status and result_dict['status'] != expected_return_status:
            print(f"FAIL: {test_name} - Expected status '{expected_return_status}', got '{result_dict['status']}'.", flush=True)
            test_status["all_passed"] = False
            test_status["tests_failed"] += 1
            # Don't return yet, check content too

        # Check content_changed based on expect_change and dry_run
        expected_content_changed = expect_change and not is_dry_run
        if result_dict['content_changed'] != expected_content_changed:
            print(f"FAIL: {test_name} - Expected content_changed to be {expected_content_changed}, got {result_dict['content_changed']}.", flush=True)
            test_status["all_passed"] = False
            test_status["tests_failed"] += 1

        # Read final content
        with open(full_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        print(f"Final content of {filename}:\n{final_content}", flush=True)

        # If dry run, final content should be initial content
        if is_dry_run:
            if final_content != initial_content:
                print(f"FAIL: {test_name} (Dry Run) - Content was modified!", flush=True)
                test_status["all_passed"] = False
                test_status["tests_failed"] += 1
                return # No need to check parts if content changed in dry run
            else:
                print(f"PASS: {test_name} (Dry Run) - Content unchanged as expected.", flush=True)
                # For dry run that would modify, check if status is 'dry_run_would_modify'
                if expect_change and result_dict['status'] != 'dry_run_would_modify':
                    print(f"FAIL: {test_name} (Dry Run) - Expected status 'dry_run_would_modify' for a change, got '{result_dict['status']}'.", flush=True)
                    test_status["all_passed"] = False
                    test_status["tests_failed"] += 1
                elif not expect_change and result_dict['status'] != 'skipped_idempotent': # Assuming no change means idempotent for dry run too
                     print(f"FAIL: {test_name} (Dry Run) - Expected status 'skipped_idempotent' for no change, got '{result_dict['status']}'.", flush=True)
                     test_status["all_passed"] = False
                     test_status["tests_failed"] += 1
                return # Test for dry run is complete

        # For non-dry runs, check if all expected parts are in the final content
        all_parts_found = True
        for part in expected_parts_in_final_content:
            if part not in final_content:
                all_parts_found = False
                print(f"FAIL: {test_name} - Expected part NOT FOUND: '{part}'", flush=True)
                break
        
        if all_parts_found:
            print(f"PASS: {test_name}", flush=True)
        else:
            test_status["all_passed"] = False
            test_status["tests_failed"] += 1

    # Define some common refs for testing
    md_ref = "docs/new_doc.md"
    md_ref_abs = os.path.join(EGOS_PROJECT_ROOT, md_ref)
    py_ref = "subsystems/another_module.py"
    py_ref_abs = os.path.join(EGOS_PROJECT_ROOT, py_ref)

    # --- Test Cases (adapted for new return type) ---
    print("\nStarting Test Cases for ref_injector...", flush=True)

    # MD Files
    _run_test("MD - New Block - Empty File", "empty.md", "", md_ref, md_ref_abs, ["@references:", f"- {md_ref}"], expected_return_status='modified')
    _run_test("MD - New Block - Simple Content", "simple.md", "Hello World\n", md_ref, md_ref_abs, ["Hello World", "@references:", f"- {md_ref}"], expected_return_status='modified')
    _run_test("MD - New Block - With Frontmatter", "frontmatter.md", "---\ntitle: Test\n---\nContent.", md_ref, md_ref_abs, ["---", "Content.", "@references:", f"- {md_ref}"], expected_return_status='modified')
    _run_test("MD - Add to Existing Block", "existing.md", "@references:\n- old/doc.md\n\nText.", md_ref, md_ref_abs, ["@references:", "old/doc.md", f"- {md_ref}", "Text."], expected_return_status='modified')
    _run_test("MD - Add to Existing HTML Comment Block", "existing_html_comment.md", "<!-- @references: -->\n<!--   - old/doc.md -->\n\nText.", md_ref, md_ref_abs, ["<!-- @references: -->", "old/doc.md", f"- {md_ref}", "Text."], expected_return_status='modified')

    # PY Files
    _run_test("PY - New Block - Empty File", "empty.py", "", py_ref, py_ref_abs, ["# @references:", f"#   - {py_ref}"], expected_return_status='modified')
    _run_test("PY - New Block - Simple Content", "simple.py", "print('hello')\n", py_ref, py_ref_abs, ["print('hello')", "# @references:", f"#   - {py_ref}"], expected_return_status='modified')
    _run_test("PY - New Block - With Shebang", "shebang.py", "#!/usr/bin/env python3\nprint('hi')", py_ref, py_ref_abs, ["#!/usr/bin/env python3", "# @references:", f"#   - {py_ref}", "print('hi')"], expected_return_status='modified')
    _run_test("PY - New Block - With Shebang & Encoding", "shebang_encoding.py", "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nprint('hi')", py_ref, py_ref_abs, ["#!/usr/bin/env python3", "# -*- coding: utf-8 -*-", "# @references:", f"#   - {py_ref}", "print('hi')"], expected_return_status='modified')
    _run_test("PY - New Block - With Module Docstring (single-line)", "docstring_single.py", '"""My module."""\n\nprint("Hi")\n', py_ref, py_ref_abs, ['"""My module."""', "# @references:", f"#   - {py_ref}", '\nprint("Hi")'], expected_return_status='modified')
    _run_test("PY - New Block - With Module Docstring (multi-line)", "docstring_multi.py", '"""\nMy module.\nDoes things.\n"""\n\nprint("Hi")\n', py_ref, py_ref_abs, ['"""\nMy module.\nDoes things.\n"""', "\n# @references:", f"#   - {py_ref}", '\nprint("Hi")'], expected_return_status='modified')
    _run_test("PY - Add to Existing Block", "existing_py.py", "# @references:\n#   - old/util.py\n\n# Code", py_ref, py_ref_abs, ["# @references:", "old/util.py", py_ref, "# Code"], expected_return_status='modified')
    _run_test("PY - Add to Existing Empty Block", "existing_empty_py.py", "# @references:\n\n# Code", py_ref, py_ref_abs, ["# @references:", py_ref, "# Code"], expected_return_status='modified')

    # Test Duplicate (resolved)
    initial_dup_content = "@references:\n  - docs/new_doc.md\n\nText."
    _run_test("MD - Skip Resolved Duplicate", "existing_md_dup.md", initial_dup_content, md_ref, md_ref_abs, [initial_dup_content.strip()], is_dry_run=False, expected_return_status='skipped_idempotent', expect_change=False)

    # Test Dry Run (would modify)
    _run_test("MD - Dry Run New Block (would modify)", "dry_run_md.md", "Hello\n", md_ref, md_ref_abs, ["Hello\n"], is_dry_run=True, expected_return_status='dry_run_would_modify', expect_change=True)
    # Test Dry Run (idempotent, no change needed)
    _run_test("MD - Dry Run Existing Block (idempotent)", "dry_run_md_idem.md", "@references:\n- docs/new_doc.md\n", md_ref, md_ref_abs, ["@references:\n- docs/new_doc.md\n"], is_dry_run=True, expected_return_status='skipped_idempotent', expect_change=False)


    print(f"\n--- Test Summary ---", flush=True)
    print(f"Total tests run: {test_status['tests_run']}", flush=True)
    print(f"Tests failed: {test_status['tests_failed']}", flush=True)
    if test_status["all_passed"]:
        print("All ref_injector tests PASSED! (Note: test suite adapted for new dict return)", flush=True)
    else:
        print("Some ref_injector tests FAILED. Please review output above.", flush=True)

    print("\nRefInjector: Test execution finished.", flush=True)
    # Clean up test directory (optional, uncomment to auto-clean)
    # shutil.rmtree(test_dir)
    # print(f"RefInjector: Cleaned up test directory: {test_dir}", flush=True)