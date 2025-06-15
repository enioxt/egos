#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Targeted snake_case Conversion Script

This script performs targeted conversion of specific files or directories to snake_case.
It's designed for precise, controlled conversions rather than bulk processing.

@author: Cascade (AI Assistant)
@date: 2025-05-26
@version: 0.1.0

@references:
  - C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md
  - C:\EGOS\docs\planning\snake_case_conversion_plan.md
  - C:\EGOS\WORK_2025-05-26_snake_case_Conversion_Implementation.md
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
import sys
import argparse
import json
from pathlib import Path
import shutil
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
logger = logging.getLogger("targeted_converter")

def string_to_snake_case(s):
    """
    Convert a string to snake_case.
    
    Args:
        s (str): The string to convert
        
    Returns:
        str: The snake_case version of the string
    """
    # Handle empty strings
    if not s:
        return s
    
    # Handle file extensions
    name_part, ext_part = os.path.splitext(s)
    
    # Replace hyphens and spaces with underscores
    s1 = re.sub(r'[-\s]+', '_', name_part)
    
    # Insert underscores between camelCase or PascalCase transitions
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    # Convert to lowercase
    s3 = s2.lower()
    
    # Remove leading/trailing underscores and collapse multiple underscores
    s4 = re.sub(r'_+', '_', s3).strip('_')
    
    # Combine with extension
    return s4 + ext_part

def convert_item(item_path, dry_run=False, rename_map=None):
    """
    Convert a single file or directory to snake_case.
    
    Args:
        item_path (str or Path): Path to the item to convert
        dry_run (bool): If True, don't actually rename, just simulate
        rename_map (dict): Dictionary to store rename mappings
        
    Returns:
        tuple: (success, old_path, new_path, message)
    """
    item_path = Path(item_path)
    
    # Skip if item doesn't exist
    if not item_path.exists():
        return False, str(item_path), "", f"Item does not exist: {item_path}"
    
    # Get the parent directory and name
    parent_dir = item_path.parent
    name = item_path.name
    
    # Convert to snake_case
    snake_case_name = string_to_snake_case(name)
    
    # Skip if already snake_case
    if snake_case_name == name:
        return False, str(item_path), "", f"Already in snake_case: {item_path}"
    
    # Construct the new path
    new_path = parent_dir / snake_case_name
    
    # Check if the new path already exists
    if new_path.exists():
        return False, str(item_path), str(new_path), f"Target already exists: {new_path}"
    
    # Perform the rename
    try:
        if not dry_run:
            shutil.move(str(item_path), str(new_path))
            if rename_map is not None:
                rename_map[str(item_path)] = str(new_path)
        
        return True, str(item_path), str(new_path), f"{'Would rename' if dry_run else 'Renamed'}: {item_path} -> {new_path}"
    
    except Exception as e:
        return False, str(item_path), str(new_path), f"Error: {e}"

def update_log_file(old_path, new_path, status, notes, log_file):
    """
    Update the manual conversion log file.
    
    Args:
        old_path (str): Original path
        new_path (str): New path
        status (str): Status of the conversion
        notes (str): Any notes about the conversion
        log_file (str): Path to the log file
    """
    try:
        # Read the existing log
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the appropriate section based on the path
        if "scripts" in old_path.lower():
            section = "### Scripts Directory"
        elif "config" in old_path.lower():
            section = "### Config Directory"
        elif "egos_framework" in old_path.lower():
            section = "## Tier 2: Core EGOS Framework & Key Documentation"
        elif "docs" in old_path.lower():
            section = "## Tier 2: Core EGOS Framework & Key Documentation"
        elif "website" in old_path.lower():
            section = "## Tier 3: Ancillary Components & High-Volume Areas"
        elif "archive" in old_path.lower():
            section = "## Tier 4: Archived/Less Critical Areas"
        else:
            section = "### Scripts Directory"  # Default
        
        # Find the section in the content
        section_pos = content.find(section)
        if section_pos == -1:
            logger.error(f"Section not found in log file: {section}")
            return
        
        # Find the table in the section
        table_pos = content.find("|", section_pos)
        if table_pos == -1:
            logger.error(f"Table not found in section: {section}")
            return
        
        # Find the end of the table header
        header_end = content.find("\n", table_pos)
        if header_end == -1:
            logger.error("Table header end not found")
            return
        
        # Find the separator line
        separator_end = content.find("\n", header_end + 1)
        if separator_end == -1:
            logger.error("Table separator end not found")
            return
        
        # Insert the new row after the separator line
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_row = f"| {old_path} | {new_path} | {date_str} | {status} | {notes} |\n"
        
        new_content = content[:separator_end + 1] + new_row + content[separator_end + 1:]
        
        # Update the summary statistics
        if status == "Completed":
            if os.path.isdir(old_path):
                new_content = re.sub(r"Total Directories Converted:\s*(\d+)", 
                                    lambda m: f"Total Directories Converted: {int(m.group(1)) + 1}", 
                                    new_content)
            else:
                new_content = re.sub(r"Total Files Converted:\s*(\d+)", 
                                    lambda m: f"Total Files Converted: {int(m.group(1)) + 1}", 
                                    new_content)
        elif status == "Skipped":
            new_content = re.sub(r"Total Skipped:\s*(\d+)", 
                                lambda m: f"Total Skipped: {int(m.group(1)) + 1}", 
                                new_content)
        elif status == "Failed":
            new_content = re.sub(r"Total Failed:\s*(\d+)", 
                                lambda m: f"Total Failed: {int(m.group(1)) + 1}", 
                                new_content)
        
        # Write the updated content
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Updated log file: {log_file}")
    
    except Exception as e:
        logger.error(f"Error updating log file: {e}")

def save_rename_map(rename_map, output_file):
    """
    Save the rename map to a JSON file.
    
    Args:
        rename_map (dict): Dictionary mapping old paths to new paths
        output_file (str): Path to the output file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rename_map, f, indent=2)
        logger.info(f"Saved rename map to {output_file}")
    except Exception as e:
        logger.error(f"Error saving rename map: {e}")

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="EGOS Targeted snake_case Conversion Script")
    parser.add_argument(
        "items",
        type=str,
        nargs='+',
        help="Paths to items (files or directories) to convert"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate conversion without making changes"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="C:\\EGOS\\logs\\snake_case_conversion\\manual_conversion_log.md",
        help="Path to the manual conversion log file"
    )
    parser.add_argument(
        "--rename-map",
        type=str,
        default="C:\\EGOS\\logs\\snake_case_conversion\\rename_map.json",
        help="Path to save the rename map JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Print banner
    logger.info("=" * 80)
    logger.info("EGOS Targeted snake_case Conversion Script")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info(f"Log File: {args.log_file}")
    logger.info(f"Rename Map: {args.rename_map}")
    logger.info("=" * 80)
    
    # Initialize rename map
    rename_map = {}
    
    # Process each item
    for item in args.items:
        item_path = Path(item)
        success, old_path, new_path, message = convert_item(item_path, args.dry_run, rename_map)
        
        # Log the result
        if success:
            logger.info(message)
            status = "Completed" if not args.dry_run else "Simulated"
            update_log_file(old_path, new_path, status, "", args.log_file)
        else:
            if "Already in snake_case" in message:
                logger.info(message)
                status = "Skipped"
            elif "Item does not exist" in message:
                logger.warning(message)
                status = "Failed"
            elif "Target already exists" in message:
                logger.warning(message)
                status = "Failed"
            else:
                logger.error(message)
                status = "Failed"
            
            update_log_file(old_path, new_path, status, message, args.log_file)
    
    # Save the rename map
    if rename_map and not args.dry_run:
        save_rename_map(rename_map, args.rename_map)
    
    # Print summary
    logger.info("=" * 80)
    logger.info("Conversion Complete")
    logger.info(f"Items processed: {len(args.items)}")
    logger.info(f"Rename map saved to: {args.rename_map if not args.dry_run and rename_map else 'N/A'}")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()