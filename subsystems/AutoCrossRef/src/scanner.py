#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module for scanning file system to find relevant files for AutoCrossRef."""
# 
# @references:
#   - subsystems/AutoCrossRef/src/scanner.py

import os
from typing import List, Dict, Any, Optional

# Assuming EGOS_ROOT is the parent directory of 'subsystems'
# This might need to be configurable or determined more robustly
EGOS_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def scan_project_files(config: Dict[str, Any], base_paths_override: Optional[List[str]] = None) -> List[str]:
    """
    Scans specified project directories for files matching configured extensions.

    Args:
        config: The loaded AutoCrossRef configuration dictionary.
        base_paths_override: Optional list of base paths to scan, overriding config.

    Returns:
        A list of absolute file paths matching the criteria.
    """
    found_files: List[str] = []
    scan_paths_config = base_paths_override if base_paths_override else config.get('scan_paths', [])
    include_extensions = tuple(config.get('include_file_extensions', ['.md']))

    if not scan_paths_config:
        print("Warning: No scan_paths defined in configuration or provided as override.")
        return found_files

    abs_scan_paths: List[str] = []
    for path_item in scan_paths_config:
        if os.path.isabs(path_item):
            abs_scan_paths.append(path_item)
        else:
            # Interpret relative paths from EGOS project root
            abs_scan_paths.append(os.path.join(EGOS_PROJECT_ROOT, path_item))

    for base_path in abs_scan_paths:
        if not os.path.isdir(base_path):
            print(f"Warning: Scan path '{base_path}' is not a valid directory. Skipping.")
            continue

        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(include_extensions):
                    found_files.append(os.path.join(root, file))
    
    return sorted(list(set(found_files))) # Sort and remove duplicates

if __name__ == '__main__':
    # Example usage and basic test
    # This requires config_loader.py to be in the same directory or Python path
    try:
        from config_loader import load_config, ConfigError
        print("Scanner: Attempting to load configuration...")
        app_config = load_config()
        print("Scanner: Configuration loaded.")

        print(f"\nScanner: Scanning files based on configuration (EGOS_PROJECT_ROOT: {EGOS_PROJECT_ROOT})...")
        # Example: Override scan paths for testing if needed
        # test_scan_paths = ["docs/guides"]
        # scanned_files = scan_project_files(app_config, base_paths_override=test_scan_paths)
        scanned_files = scan_project_files(app_config)

        if scanned_files:
            print(f"\nScanner: Found {len(scanned_files)} files:")
            for f_path in scanned_files[:20]: # Print first 20 found files
                print(f"  - {f_path}")
            if len(scanned_files) > 20:
                print(f"  ... and {len(scanned_files) - 20} more.")
        else:
            print("Scanner: No files found matching criteria.")

    except ConfigError as e:
        print(f"Scanner: Configuration error - {e}")
    except ImportError:
        print("Scanner: Error importing 'config_loader'. Make sure it's in the Python path or same directory.")
    except Exception as e:
        print(f"Scanner: An unexpected error occurred: {e}")