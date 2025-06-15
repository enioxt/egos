#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Interactive snake_case Converter

This script interactively renames files and directories to conform to the
snake_case naming convention as defined in EGOS standards.

@author: Cascade (AI Assistant)
@date: 2025-05-26
@version: 0.1.0

@references:
  - C:\EGOS\docs\planning\snake_case_conversion_plan.md
  - C:\EGOS\reports\snake_case_audit_report.md
  - C:\EGOS\.windsurfrules (Global & Workspace for RULE-FS-SNAKE-CASE-01)
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
import argparse
import json # For configuration
from pathlib import Path
import shutil # For robust renaming/moving if needed across filesystems

# EGOS Standard: RULE-FS-SNAKE-CASE-01
# This script helps enforce this rule by correcting deviations.

# Default configuration (can be overridden by a config file or CLI args)
DEFAULT_CONVERSION_CONFIG = {
    "start_path": None, # Must be provided by user
    "exclusions": {
        "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
        "files": ["README.md", "LICENSE", "Makefile", "requirements.txt", ".gitignore", ".gitattributes", "DS_Store"],
        "extensions_to_ignore_stem_case": [".SQL", ".DLL", ".EXE"], # Extensions where stem case might be preserved
        "patterns_to_ignore": [] # Regex patterns for full paths to ignore
    },
    "log_file": "C:\\EGOS\\logs\\snake_case_conversion_log.txt",
    "dry_run": True, # Default to dry-run for safety
    "interactive": True # Default to interactive mode
}

# --- Helper Functions (to be developed) ---

def string_to_snake_case(name_string):
    """Converts a string to snake_case.
    Handles CamelCase, PascalCase, kebab-case, spaces, and multiple underscores.
    Example: "SomeName" -> "some_name", "some-name" -> "some_name",
             "HTTPRequest" -> "http_request", "Version2Update" -> "version_2_update"
    """
    if not name_string:
        return ""

    # Replace hyphens and spaces with underscores
    s = re.sub(r'[-\s]+', '_', name_string)
    
    # Handle cases like 'WORDWord' or 'WordWORD' by inserting underscore
    # between a lowercase/digit and an uppercase, or between two uppercases followed by lowercase
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', s)
    
    # Convert to lowercase
    s = s.lower()
    
    # Remove any leading/trailing underscores that might have formed
    s = s.strip('_')
    
    # Replace multiple consecutive underscores with a single underscore
    s = re.sub(r'_+', '_', s)
    
    # Handle potential edge case of name being only underscores after processing
    if not s and name_string: # If string becomes empty but original was not
        # This might happen for strings like "-" or "__".
        # Decide on a sensible default, e.g., 'untitled' or raise error, or return original if unconvertible
        # For now, let's try to preserve original if it only contained non-alphanumeric for snake_case
        # or return a placeholder if it was purely separators
        if all(c in ['_', '-', ' '] for c in name_string):
            return '_'
        # A more sophisticated approach might be needed for truly unconvertible names
        # For now, if it's not just separators, it might be an issue with the original name
        # or the regexes. Let's assume the regexes above handle most valid input for conversion.

    # Ensure it doesn't start or end with an underscore if it's not just a single underscore
    if len(s) > 1:
        s = s.strip('_')
        
    # Final check for multiple underscores again, as strip might re-expose them
    s = re.sub(r'_+', '_', s)

    return s

def load_conversion_config(config_path_str, default_config):
    """Loads conversion configuration from a JSON file and merges with defaults."""
    config = default_config.copy() # Start with a copy of the defaults

    if config_path_str:
        try:
            config_path = Path(config_path_str)
            if config_path.exists() and config_path.is_file():
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Deep merge user_config into config
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                        # For dictionaries (like 'exclusions'), merge their sub-keys
                        for sub_key, sub_value in value.items():
                            if sub_key in config[key] and isinstance(sub_value, list) and isinstance(config[key][sub_key], list):
                                # Merge and deduplicate lists like exclusion lists
                                config[key][sub_key] = list(set(config[key][sub_key] + sub_value))
                            else:
                                config[key][sub_key] = sub_value
                    elif isinstance(value, list) and key in config and isinstance(config[key], list):
                        # For top-level lists (if any), merge and deduplicate (though not typical for this config structure)
                        config[key] = list(set(config[key] + value))
                    else:
                        # For other top-level keys, user's value overrides default
                        config[key] = value
                print(f"[ConfigLoader] Loaded and merged conversion config from: {config_path_str}")
            else:
                print(f"[ConfigLoader] Warning: Conversion config file not found at {config_path_str}. Using defaults.")
                log_entries.append(f"WARNING_CONFIG_NOT_FOUND: {config_path_str}") # Assuming log_entries is accessible or handle logging differently
        except Exception as e:
            print(f"[ConfigLoader] Error loading or merging conversion config file {config_path_str}: {e}. Using defaults.")
            # log_entries.append(f"ERROR_CONFIG_LOAD: {config_path_str} | {e}")
    return config

def is_item_snake_case(name, item_type, config):
    """Checks if an item name (file stem or dir name) is snake_case."""
    # This is a simplified check. A more robust one would align with audit_snake_case.py's is_snake_case
    # For now, we assume string_to_snake_case(name) == name implies it's already compliant enough.
    # Or, more accurately, if the conversion doesn't change it, it's considered compliant for renaming purposes.
    if item_type == 'file':
        # For files, we primarily care about the stem for conversion.
        # The extension's case is usually preserved or handled by OS/filesystem conventions.
        stem, _ = os.path.splitext(name)
        return string_to_snake_case(stem) == stem
    else: # directory
        return string_to_snake_case(name) == name

def process_item(item_path, item_type, config, log_entries):
    """Processes a single file or directory for renaming."""
    original_name = item_path.name
    
    # Check if already compliant based on its type (file stem or dir name)
    if is_item_snake_case(original_name, item_type, config):
        # print(f"[Process] '{original_name}' ({item_type}) is already snake_case. Skipping.")
        return

    if item_type == 'file':
        original_stem = item_path.stem
        original_ext = item_path.suffix # Preserve original extension case
        name_to_convert = original_stem
        # Check if this file extension means we should ignore stem case conversion
        if original_ext.lower() in [ext.lower() for ext in config["exclusions"]["extensions_to_ignore_stem_case"]]:
            # print(f"[Process] Stem case for '{original_name}' will be preserved due to extension '{original_ext}'. Skipping conversion of stem.")
            # If we want to convert the full name IF it contains spaces/hyphens even with ignored stem, add logic here.
            # For now, this means if ext is in ignore list, we don't attempt to snake_case the stem.
            return 
    else: # directory
        name_to_convert = original_name
        original_ext = ''

    suggested_new_stem_or_name = string_to_snake_case(name_to_convert)
    
    if not suggested_new_stem_or_name: # string_to_snake_case might return empty for odd inputs
        print(f"[Error] Could not generate a valid snake_case name for '{name_to_convert}'. Skipping '{item_path}'.")
        log_entries.append(f"ERROR_CONVERSION_EMPTY: {item_path}")
        return

    if item_type == 'file':
        suggested_new_name = suggested_new_stem_or_name + original_ext
    else:
        suggested_new_name = suggested_new_stem_or_name

    if suggested_new_name == original_name:
        # print(f"[Process] Suggested name for '{original_name}' is the same after conversion attempt. Skipping.")
        return

    print(f"\n[Candidate] Original {item_type}: {item_path.relative_to(config['start_path_obj']) if config.get('start_path_obj') else item_path}")
    print(f"             Suggested new name: {suggested_new_name}")

    user_confirmed_rename = False
    final_new_name = suggested_new_name

    if config['interactive']:
        while True:
            action = input(f"  Action for '{original_name}' -> '{suggested_new_name}'? (Y/n/s/c/a): ").lower()
            # Y: Yes, N: No (default), S: Skip, C: Custom, A: Auto (non-interactive for rest of session for this type)
            if action == 'y' or not action: # Default to Yes if empty
                user_confirmed_rename = True
                break
            elif action == 'n' or action == 's':
                print("[Skipped by user]")
                log_entries.append(f"SKIPPED_USER: {item_path}")
                return
            elif action == 'c':
                custom_input = input("  Enter custom name (if file, include extension): ")
                if custom_input:
                    final_new_name = custom_input
                    user_confirmed_rename = True
                    print(f"             Using custom name: {final_new_name}")
                    break
                else:
                    print("[Skipped] No custom name provided.")
                    log_entries.append(f"SKIPPED_CUSTOM_EMPTY: {item_path}")
                    return # Skip if custom name is empty
            elif action == 'a': # Auto mode for future items of this type (not fully implemented here, simple flag)
                config['interactive'] = False # Basic way to turn off for subsequent calls
                print("[Mode] Switched to non-interactive (auto-yes) for subsequent items.")
                user_confirmed_rename = True
                break
            else:
                print("  Invalid input. (Y)es, (N)o, (S)kip, (C)ustom, (A)uto-confirm rest")
    else: # Non-interactive mode
        user_confirmed_rename = True # Auto-confirm

    if not user_confirmed_rename:
        # This case should be handled by returns above, but as a safeguard:
        log_entries.append(f"SKIPPED_NO_CONFIRM: {item_path}")
        return
    
    new_path = item_path.parent / final_new_name

    if new_path.exists():
        print(f"[Error] Target path '{new_path}' already exists. Skipping rename of '{item_path}'.")
        log_entries.append(f"ERROR_TARGET_EXISTS: {item_path} -> {new_path}")
        return

    if not config['dry_run']:
        try:
            shutil.move(str(item_path), str(new_path))
            print(f"[Renamed] '{item_path}' to '{new_path}'")
            log_entries.append(f"RENAMED: {item_path} -> {new_path}")
        except Exception as e:
            print(f"[Error] Failed to rename '{item_path}' to '{new_path}': {e}")
            log_entries.append(f"ERROR_RENAME_FAILED: {item_path} -> {new_path} | Exception: {e}")
    else:
        print(f"[DryRun] Would rename '{item_path}' to '{new_path}'")
        log_entries.append(f"DRYRUN_RENAME: {item_path} -> {new_path}")

def traverse_and_convert(config, log_entries):
    """Traverses directories and processes items for conversion."""
    start_path_obj = Path(config["start_path"])
    config['start_path_obj'] = start_path_obj # Store for relative path display

    if not start_path_obj.exists() or not start_path_obj.is_dir():
        print(f"[Error] Start path '{config['start_path']}' is not a valid directory.")
        log_entries.append(f"ERROR_INVALID_START_PATH: {config['start_path']}")
        return

    print(f"Starting traversal from: {start_path_obj}")
    
    excluded_dir_names = config["exclusions"]["directories"]
    excluded_file_names = config["exclusions"]["files"]
    # excluded_extensions_stem_ignore = [ext.lower() for ext in config["exclusions"]["extensions_to_ignore_stem_case"]]
    # This ^ is handled inside process_item now.
    try:
        excluded_patterns = [re.compile(p) for p in config["exclusions"]["patterns_to_ignore"]]
    except re.error as e:
        print(f"[Error] Invalid regex in 'patterns_to_ignore': {e}. No pattern exclusions will be applied.")
        log_entries.append(f"ERROR_INVALID_REGEX_PATTERN: {e}")
        excluded_patterns = []

    # Revised loop structure for clarity and correctness with topdown=False:
    # print("Collecting items for snake_case conversion...") # Less verbose
    all_items_to_process = []
    
    # First, collect all items (files and directories) that are candidates for processing.
    # os.walk with topdown=False ensures that we get items from deepest levels first.
    for root, dirs, files in os.walk(start_path_obj, topdown=False):
        current_root_path = Path(root)

        # Check if current_root_path itself is an excluded directory branch
        # This helps prune entire branches early if a parent dir in the path is excluded.
        # Example: if '.git' is in excluded_dir_names, C:/EGOS/.git/hooks will be skipped.
        is_excluded_branch = False
        for part in current_root_path.relative_to(start_path_obj).parts:
            if part in excluded_dir_names:
                is_excluded_branch = True
                break
        if is_excluded_branch:
            # print(f"[Skipping Branch] Path '{current_root_path}' is within an excluded directory branch.")
            dirs[:] = [] # Don't traverse further into this branch's subdirectories
            files[:] = [] # Don't process files in this branch's current directory
            continue
        
        # Also check current_root_path against patterns
        if any(pattern.search(str(current_root_path)) for pattern in excluded_patterns):
            # print(f"[Skipping Branch by Pattern] Path '{current_root_path}' matches an exclusion pattern.")
            dirs[:] = [] 
            files[:] = []
            continue

        # Add files for processing from the current root
        for name in files:
            file_path = current_root_path / name
            if name in excluded_file_names:
                continue
            if any(pattern.search(str(file_path)) for pattern in excluded_patterns):
                continue
            # Extension-based stem ignore is handled in process_item
            all_items_to_process.append({'path': file_path, 'type': 'file'})
        
        # Add directories for processing (these are the subdirectories of current_root_path)
        # These will be processed based on their original names as found by os.walk.
        # Since it's topdown=False, these subdirectories (as items) would have been added
        # to all_items_to_process in previous iterations if they contained further items.
        # Here, we are adding the directory *itself* as an item to be potentially renamed.
        for name in dirs:
            dir_path = current_root_path / name
            if name in excluded_dir_names:
                continue
            if any(pattern.search(str(dir_path)) for pattern in excluded_patterns):
                continue
            all_items_to_process.append({'path': dir_path, 'type': 'directory'})
    
    # If the start_path_obj itself should be considered (e.g., if C:/EGOS/MyFolder and MyFolder is not snake_case)
    # This is complex as renaming the root of traversal while traversing is problematic.
    # For now, this script assumes it renames *contents of* start_path.
    # To rename start_path itself, it would typically be done by a script running from its parent directory.

    # The `all_items_to_process` list is already ordered from deepest to shallowest due to topdown=False.
    print(f"Collected {len(all_items_to_process)} items for potential renaming (after initial filtering).")
    
    # This set helps avoid issues if, hypothetically, an item's processing somehow leads to it being re-evaluated.
    # Given the single pass over `all_items_to_process`, its main role is more of a safeguard.
    processed_paths_in_this_run = set()

    for item_info in all_items_to_process: 
        item_path = item_info['path']
        item_type = item_info['type']

        # A path might have been implicitly handled if its parent was renamed and it moved with it.
        # However, direct processing is based on original paths. If a parent was renamed,
        # the original item_path might no longer be valid. This is a hard problem for in-place full-tree renames.
        # The `shutil.move` should handle the item correctly at its current (original) path.
        # The `processed_paths_in_this_run` helps avoid trying to process an original path twice if it appeared multiple times
        # in `all_items_to_process` due to some collection artifact (shouldn't happen with current logic).
        if str(item_path) in processed_paths_in_this_run:
            # print(f"[Skipping Duplicate Process] Path {item_path} already in this run's process queue.")
            continue
        
        # Final check: Does the item still exist? It might have been moved if a parent was renamed.
        # This check is tricky because if `item_path` was `parent/child` and `parent` became `new_parent`,
        # then `parent/child` doesn't exist, but `new_parent/child` might. Our `item_path` is original.
        # The `topdown=False` order (children first) is key to making this work: we rename `child` to `new_child`
        # inside `parent`. Then we rename `parent` to `new_parent`. `new_parent` now contains `new_child`.
        if not item_path.exists():
            # print(f"[Skipping Stale] Path {item_path} no longer exists. Likely moved with a renamed parent.")
            log_entries.append(f"INFO_STALE_PATH_SKIPPED: {item_path}")
            continue

        processed_paths_in_this_run.add(str(item_path))
        process_item(item_path, item_type, config, log_entries)


def write_log(log_file_path, log_entries):
    """Writes log entries to the log file."""
    try:
        Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file_path, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f"\n--- Conversion Log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            for entry in log_entries:
                f.write(f"{entry}\n")
        print(f"Log updated at: {log_file_path}")
    except IOError as e:
        print(f"Error writing log to {log_file_path}: {e}")

def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(description="EGOS Interactive snake_case Naming Convention Converter.")
    parser.add_argument(
        "start_path", 
        type=str, 
        help="The root directory to start the conversion from."
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None, 
        help="Path to a JSON configuration file for conversion parameters (e.g., C:\\EGOS\\config\\snake_case_convert_config.json)."
    )
    parser.add_argument(
        "--log-file", 
        type=str, 
        help="Optional path to save the conversion log file."
    )
    parser.add_argument(
        "--dry-run", 
        action=argparse.BooleanOptionalAction, # Allows --dry-run or --no-dry-run
        default=None, # Will be overridden by config if not specified
        help="Simulate renames without making changes. Overrides config if set."
    )
    parser.add_argument(
        "--interactive",
        action=argparse.BooleanOptionalAction,
        default=None, # Will be overridden by config if not specified
        help="Prompt for confirmation before each rename. Overrides config if set."
    )

    args = parser.parse_args()

    # Load base config (e.g., from a standard path or internal defaults)
    # For now, using internal default. A standard path like C:\EGOS\config\snake_case_convert_config.json could be added.
    config = load_conversion_config(args.config_file, DEFAULT_CONVERSION_CONFIG)

    # Override config with CLI arguments if provided
    config["start_path"] = args.start_path # Mandatory CLI arg
    if args.log_file:
        config["log_file"] = args.log_file
    if args.dry_run is not None:
        config["dry_run"] = args.dry_run
    if args.interactive is not None:
        config["interactive"] = args.interactive

    print("--- EGOS snake_case Converter Initializing ---")
    print(f"Mode: {'Dry Run' if config['dry_run'] else 'Live Run'}, {'Interactive' if config['interactive'] else 'Non-Interactive'}")
    print(f"Starting conversion for: {config['start_path']}")
    print(f"Log file: {config['log_file']}")
    # print(f"Exclusions: {config['exclusions']}") # Can be verbose

    log_entries = []
    try:
        traverse_and_convert(config, log_entries)
        print("\n--- Conversion Summary ---")
        # Basic summary from log entries
        renamed_count = sum(1 for entry in log_entries if entry.startswith("RENAMED:"))
        dryrun_count = sum(1 for entry in log_entries if entry.startswith("DRYRUN_RENAME:"))
        error_count = sum(1 for entry in log_entries if entry.startswith("ERROR"))
        skipped_count = sum(1 for entry in log_entries if entry.startswith("SKIPPED"))
        
        if config['dry_run']:
            print(f"{dryrun_count} items would be renamed.")
        else:
            print(f"{renamed_count} items were renamed.")
        print(f"{error_count} errors encountered.")
        print(f"{skipped_count} items were skipped by the user or due to issues.")

    except Exception as e:
        print(f"An unexpected error occurred during conversion: {e}")
        import traceback
        log_entries.append(f"FATAL_ERROR: {traceback.format_exc()}")
        print(traceback.format_exc())
    finally:
        if config['log_file']:
            write_log(config['log_file'], log_entries)
        print("--- EGOS snake_case Converter Finished ---")

if __name__ == "__main__":
    main()