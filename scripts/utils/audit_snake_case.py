#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS snake_case Naming Convention Auditor

This script audits the EGOS workspace for files and directories not adhering
to the snake_case naming convention as defined in EGOS standards.

@author: Cascade (AI Assistant)
@date: 2025-05-26
@version: 0.1.0

@references:
  - C:\EGOS\docs\planning\snake_case_conversion_plan.md
  - C:\EGOS\ADRS_Log.md (Entry for snake_case inconsistency)
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
import json # Or yaml, if preferred for config
from pathlib import Path

# EGOS Standard: RULE-FS-SNAKE-CASE-01
# This script helps enforce this rule.

# Configuration (defaults, can be overridden by a config file or CLI args)
DEFAULT_CONFIG = {
    "start_path": "C:\\EGOS",
    "exclusions": {
        "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
        "files": ["README.md", "LICENSE", "Makefile", "requirements.txt"],
        "extensions": []
    },
    "report_file": "C:\\EGOS\\reports\\default_snake_case_audit_report.md" # Default report path
}

# Regex for basic snake_case validation (can be refined)
# This regex checks for: no uppercase, no spaces, only lowercase, numbers, and underscores.
# It doesn't strictly enforce starting/ending with letters/numbers or double underscores.
SNAKE_CASE_PATTERN = re.compile(r"^[a-z0-9_]+(?<!_)$|^[a-z0-9_]*[a-z][a-z0-9_]*$")

# More specific checks can be added:
# - Check for CamelCase: re.compile(r".*[a-z][A-Z].*")
# - Check for PascalCase: re.compile(r"^[A-Z][a-zA-Z0-9]*$")
# - Check for hyphens: re.compile(r".*-.+")
# - Check for spaces: re.compile(r".* .+")

def is_snake_case(name):
    """Checks if a given name string is likely snake_case."""
    # Check for disallowed characters first (more efficient)
    if ' ' in name or '-' in name:
        return False
    for char_code in range(ord('A'), ord('Z') + 1):
        if chr(char_code) in name:
            return False
    # Optional: A more precise regex could be used here if needed, but the char check is fast.
    # The current SNAKE_CASE_PATTERN is a bit strict and might need refinement for edge cases.
    # For now, the absence of uppercase, spaces, and hyphens is the primary check.
    return True

def audit_directory(start_path, config):
    """Audits the directory for snake_case compliance."""
    print(f"[AuditDir] Attempting to audit: {start_path}")
    non_compliant_dirs = []
    non_compliant_files = []
    items_scanned = 0

    start_path_obj = Path(start_path)
    if not start_path_obj.exists():
        print(f"[AuditDir] Error: Start path '{start_path}' does not exist.")
        return [], [], 0
    if not start_path_obj.is_dir():
        print(f"[AuditDir] Error: Start path '{start_path}' is not a directory.")
        return [], [], 0
    
    print(f"[AuditDir] Starting os.walk for {start_path_obj}")
    for root, dirs, files in os.walk(start_path_obj, topdown=True):
        current_path_obj = Path(root)
        print(f"[AuditDir] Walking: {current_path_obj}")
        items_scanned += 1 # Count the directory itself

        excluded_dir_names = config["exclusions"]["directories"]
        # Filter out excluded directories by name at the current level
        original_dirs = list(dirs) # Keep a copy for comparison/logging if needed
        dirs[:] = [d for d in original_dirs if d not in excluded_dir_names]
        # print(f"[AuditDir] Dirs in {current_path_obj} before filtering: {original_dirs}, after: {dirs}")

        for dir_name in dirs:
            items_scanned += 1
            if not is_snake_case(dir_name):
                print(f"[AuditDir] Non-compliant directory found: {Path(root) / dir_name}")
                non_compliant_dirs.append(str(Path(root) / dir_name))

        for file_name in files:
            items_scanned += 1
            file_stem, file_ext = os.path.splitext(file_name)
            
            if file_name in config["exclusions"]["files"]:
                # print(f"[AuditDir] File '{file_name}' in general exclusion list. Skipping.")
                continue
            
            # Case-insensitive check for excluded extensions
            if file_ext.lower() in [ext.lower() for ext in config["exclusions"]["extensions"]]: 
                # print(f"[AuditDir] File extension '{file_ext}' for '{file_name}' in exclusion list. Skipping file.")
                continue 
            
            if not is_snake_case(file_stem):
                print(f"[AuditDir] Non-compliant file stem: '{file_stem}' (from file: {Path(root) / file_name})")
                non_compliant_files.append(str(Path(root) / file_name))
    
    print(f"[AuditDir] Finished os.walk. Total items scanned: {items_scanned}")
    print(f"[AuditDir] Found {len(non_compliant_dirs)} non-compliant dirs, {len(non_compliant_files)} non-compliant files.")
    return non_compliant_dirs, non_compliant_files, items_scanned

def generate_report(non_compliant_dirs, non_compliant_files, items_scanned, report_path):
    """Generates a Markdown report of the audit findings."""
    from datetime import datetime
    report_content = f"# snake_case Compliance Audit Report\n\n"
    report_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"**Total Items Scanned (approx.):** {items_scanned}\n"
    report_content += f"**Non-Compliant Items Found:** {len(non_compliant_dirs) + len(non_compliant_files)}\n\n"

    if non_compliant_dirs:
        report_content += "## Non-Compliant Directories:\n"
        for d in non_compliant_dirs:
            report_content += f"- {d}\n"
        report_content += "\n"
    else:
        report_content += "No non-compliant directories found.\n\n"

    if non_compliant_files:
        report_content += "## Non-Compliant Files:\n"
        for f in non_compliant_files:
            report_content += f"- {f}\n"
        report_content += "\n"
    else:
        report_content += "No non-compliant files found.\n\n"
    
    if report_path:
        try:
            Path(report_path).parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report generated at: {report_path}")
        except IOError as e:
            print(f"Error writing report to {report_path}: {e}")
    else:
        print(report_content)

def load_config(cli_config_path_str, default_config_dict):
    """Loads configuration, prioritizing CLI, then standard path, then internal defaults."""
    config = default_config_dict.copy()
    print(f"[ConfigLoader] Initialized with internal default config.")

    config_file_to_load = cli_config_path_str
    source_type = "CLI specified"

    if not config_file_to_load:
        print(f"[ConfigLoader] CLI config path not provided.")
        standard_config_path = Path("C:\\EGOS\\config\\snake_case_audit_config.json")
        if standard_config_path.exists() and standard_config_path.is_file():
            config_file_to_load = str(standard_config_path)
            source_type = "standard path"
            print(f"[ConfigLoader] Attempting to load from {source_type}: {config_file_to_load}")
        else:
            print(f"[ConfigLoader] Standard config file {standard_config_path} not found or not a file. Using internal defaults.")
            return config # Return internal defaults

    if config_file_to_load:
        try:
            config_path_obj = Path(config_file_to_load)
            if config_path_obj.exists() and config_path_obj.is_file():
                with open(config_path_obj, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge user_config into config
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                            config[key].update(value)
                        elif isinstance(value, list) and key in config and isinstance(config[key], list):
                            config[key] = value # Replace lists like exclusions
                        else:
                            config[key] = value
                print(f"[ConfigLoader] Successfully loaded and merged configuration from {source_type}: {config_file_to_load}")
            else:
                print(f"[ConfigLoader] Warning: Config file from {source_type} ({config_file_to_load}) not found or not a file. Reverting to internal defaults.")
                config = default_config_dict.copy() # Revert to internal defaults
        except Exception as e:
            print(f"[ConfigLoader] Error loading config file {config_file_to_load} (from {source_type}): {e}. Reverting to internal defaults.")
            config = default_config_dict.copy() # Revert to internal defaults
    else:
        # This case should ideally be covered by the logic above, but as a fallback:
        print(f"[ConfigLoader] No config file path determined. Using internal defaults.")

    return config

def main():
    """Main function to parse arguments and run the audit."""
    parser = argparse.ArgumentParser(description="EGOS snake_case Naming Convention Auditor.")
    parser.add_argument(
        "--start-path", 
        type=str, 
        help="The root directory to start the audit from."
    )
    parser.add_argument(
        "--report-file", 
        type=str, 
        help="Optional path to save the audit report (Markdown format)."
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default=None, 
        help="Path to a JSON configuration file for audit parameters. If not provided, attempts to load 'C:\\EGOS\\config\\snake_case_audit_config.json'."
    )

    args = parser.parse_args()

    config = load_config(args.config_file, DEFAULT_CONFIG)

    if args.start_path:
        config["start_path"] = args.start_path
    if args.report_file is not None: # Allow explicitly setting report_file to '' or None via CLI to suppress file output
        config["report_file"] = args.report_file

    print(f"Starting snake_case audit for: {config['start_path']}")
    print(f"Excluding directories: {config['exclusions']['directories']}")
    print(f"Excluding files: {config['exclusions']['files']}")
    print(f"Excluding extensions: {config['exclusions']['extensions']}")

    try:
        non_compliant_dirs, non_compliant_files, items_scanned = audit_directory(config['start_path'], config)
        
        print("\n--- Audit Summary ---")
        if not non_compliant_dirs and not non_compliant_files:
            print("Congratulations! All scanned items adhere to snake_case naming conventions (based on current rules)." )
        else:
            print(f"Found {len(non_compliant_dirs)} non-compliant directory names.")
            print(f"Found {len(non_compliant_files)} non-compliant file names (stem check)." )
        print(f"Scanned approximately {items_scanned} items.")

        generate_report(non_compliant_dirs, non_compliant_files, items_scanned, config["report_file"])

    except Exception as e:
        print(f"An error occurred during the audit: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # EGOS System Signature
    # MQP Principle: Systemic Cartography (SC) - This script maps naming convention adherence.
    # MQP Principle: Progressive Standardization (PS) - This script is a tool for PS.
    print("--- EGOS snake_case Auditor Initializing --- ")
    main()
    print("--- EGOS snake_case Auditor Finished --- ")