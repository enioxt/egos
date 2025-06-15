#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Cross-Reference Update Script for Post-Rename Operations

This script updates cross-references in Markdown files after files or directories
have been renamed, particularly during the snake_case conversion process.

@author: Cascade (AI Assistant)
@date: 2025-05-26
@version: 0.1.0

@references:
  - C:\EGOS\docs\planning\snake_case_conversion_plan.md
  - C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
  - C:\EGOS\.windsurfrules (Global & Workspace for RULE-XREF-01)
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
import json
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
    ]
)
logger = logging.getLogger("xref_updater")

# Default configuration
DEFAULT_CONFIG = {
    "start_path": "C:\\EGOS",
    "exclusions": {
        "directories": [".git", "venv", ".venv", "env", "node_modules", "__pycache__", ".vscode", ".idea"],
        "files": [],
        "extensions": [".exe", ".dll", ".so", ".pyc", ".pyo", ".pyd", ".png", ".jpg", ".jpeg", ".gif", ".pdf"]
    },
    "rename_map_file": "C:\\EGOS\\logs\\snake_case_rename_map.json",
    "log_file": "C:\\EGOS\\logs\\xref_update_log.txt",
    "file_types": [".md", ".txt", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"]
}

def load_config(config_path=None):
    """Load configuration from a file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Deep merge
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                        for sub_key, sub_value in value.items():
                            config[key][sub_key] = sub_value
                    else:
                        config[key] = value
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    return config

def load_rename_map(rename_map_file):
    """Load the rename map from a JSON file."""
    try:
        with open(rename_map_file, 'r', encoding='utf-8') as f:
            rename_map = json.load(f)
        logger.info(f"Loaded rename map from {rename_map_file} with {len(rename_map)} entries")
        return rename_map
    except FileNotFoundError:
        logger.error(f"Rename map file not found: {rename_map_file}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in rename map file: {rename_map_file}")
        return {}
    except Exception as e:
        logger.error(f"Error loading rename map: {e}")
        return {}

def should_process_file(file_path, config):
    """Determine if a file should be processed based on exclusion rules."""
    # Check file extension
    if file_path.suffix.lower() not in config["file_types"]:
        return False
    
    # Check excluded extensions
    if file_path.suffix.lower() in config["exclusions"]["extensions"]:
        return False
    
    # Check excluded files
    if file_path.name in config["exclusions"]["files"]:
        return False
    
    # Check excluded directories
    for part in file_path.parts:
        if part in config["exclusions"]["directories"]:
            return False
    
    return True

def update_xrefs_in_file(file_path, rename_map, dry_run=False):
    """Update cross-references in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Update cross-references
        # Look for patterns like [text](file:///C:/EGOS/path/to/file.ext) or similar
        # This regex matches Markdown links with file:/// protocol
        file_link_pattern = r'\[([^\]]+)\]\((file:///[^)]+)\)'
        
        # Find all matches
        matches = re.findall(file_link_pattern, content)
        
        # Process each match
        for link_text, file_url in matches:
            # Convert URL to path
            file_url_clean = file_url.replace('file:///', '')
            
            # Check if this path or any parent directory was renamed
            for old_path, new_path in rename_map.items():
                # Normalize paths for comparison
                old_path_norm = old_path.replace('\\', '/')
                new_path_norm = new_path.replace('\\', '/')
                file_url_norm = file_url_clean.replace('\\', '/')
                
                # Check if the file URL contains the old path
                if old_path_norm in file_url_norm:
                    # Replace the old path with the new path
                    new_file_url = file_url.replace(old_path_norm, new_path_norm)
                    # Replace in content
                    old_link = f'[{link_text}]({file_url})'
                    new_link = f'[{link_text}]({new_file_url})'
                    content = content.replace(old_link, new_link)
                    changes_made += 1
                    logger.debug(f"Updated link in {file_path}: {old_link} -> {new_link}")
        
        # If changes were made and not in dry run mode, write the file
        if changes_made > 0 and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Updated {changes_made} cross-references in {file_path}")
        elif changes_made > 0:
            logger.info(f"[DRY RUN] Would update {changes_made} cross-references in {file_path}")
        
        return changes_made
    
    except Exception as e:
        logger.error(f"Error updating cross-references in {file_path}: {e}")
        return 0

def update_all_xrefs(config, dry_run=False):
    """Update cross-references in all relevant files."""
    start_path = Path(config["start_path"])
    rename_map = load_rename_map(config["rename_map_file"])
    
    if not rename_map:
        logger.warning("No rename map found or it's empty. No cross-references will be updated.")
        return 0
    
    total_files_processed = 0
    total_changes_made = 0
    
    # Walk through all files
    for root, dirs, files in os.walk(start_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in config["exclusions"]["directories"]]
        
        for file in files:
            file_path = Path(root) / file
            
            if should_process_file(file_path, config):
                changes = update_xrefs_in_file(file_path, rename_map, dry_run)
                if changes > 0:
                    total_files_processed += 1
                    total_changes_made += changes
    
    logger.info(f"Processed {total_files_processed} files, made {total_changes_made} cross-reference updates")
    return total_changes_made

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="EGOS Cross-Reference Update Script for Post-Rename Operations")
    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to a JSON configuration file"
    )
    parser.add_argument(
        "--rename-map",
        type=str,
        help="Path to the rename map JSON file"
    )
    parser.add_argument(
        "--start-path",
        type=str,
        help="Path to start searching for files to update"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to save the log file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate updates without making changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config_file)
    
    # Override config with command line arguments
    if args.rename_map:
        config["rename_map_file"] = args.rename_map
    if args.start_path:
        config["start_path"] = args.start_path
    if args.log_file:
        config["log_file"] = args.log_file
    
    # Configure logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Add file handler if log file is specified
    if config["log_file"]:
        file_handler = logging.FileHandler(config["log_file"])
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
    
    # Print banner
    logger.info("=" * 80)
    logger.info("EGOS Cross-Reference Update Script")
    logger.info(f"Start Path: {config['start_path']}")
    logger.info(f"Rename Map: {config['rename_map_file']}")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info("=" * 80)
    
    # Run the update
    start_time = datetime.now()
    changes_made = update_all_xrefs(config, args.dry_run)
    end_time = datetime.now()
    
    # Print summary
    logger.info("=" * 80)
    logger.info(f"Cross-Reference Update Complete")
    logger.info(f"Total Changes Made: {changes_made}")
    logger.info(f"Execution Time: {end_time - start_time}")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()