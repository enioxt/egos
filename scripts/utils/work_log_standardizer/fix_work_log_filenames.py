#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Work Log Filename Fixer

This script directly renames work log files to comply with the EGOS snake_case naming convention.
It specifically targets files identified as non-compliant by the work_log_standardizer.py script.

@author: EGOS Development Team (AI: Cascade)
@date: 2025-05-27
@version: 0.1.0
@references:
- C:\EGOS\docs\work_logs\WORK_2025-05-23_Work_Log_Standardization.md
- C:\EGOS\MQP.md (Systemic Cartography, Evolutionary Preservation principles)
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
import sys
import re
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("WorkLogFilenameFixer")

WORK_LOGS_DIR = Path("C:/EGOS/docs/work_logs")
ACTIVE_DIR = WORK_LOGS_DIR / "active"

def snake_case(text):
    """Convert text to snake_case format."""
    # Replace hyphens with spaces first
    text = text.replace('-', ' ')
    
    # Handle camelCase and PascalCase
    # Insert space before uppercase letters if they follow lowercase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Insert space between consecutive uppercase letters followed by lowercase 
    # (e.g., "MCPDoc" -> "MCP Doc")
    text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)
    
    # Convert to lowercase and replace spaces with underscores
    return text.lower().replace(' ', '_')

def fix_work_log_filename(file_path):
    """Fix a work log filename to comply with snake_case naming convention."""
    filename = file_path.name
    
    # Split filename into prefix, date, and description parts
    parts = filename.split('_', 2)
    if len(parts) < 3:
        logger.warning(f"Skipping {filename}: unexpected format (not enough parts)")
        return False
    
    prefix, date, desc_with_ext = parts
    
    # Fix date format if needed (e.g., 2025_05_22 -> 2025-05-22)
    if '-' not in date and len(date) == 8:
        if '_' in date:  # Format like YYYY_MM_DD
            year, month, day = date.split('_')
            date = f"{year}-{month}-{day}"
        else:  # Format like YYYYMMDD
            year, month, day = date[:4], date[4:6], date[6:8]
            date = f"{year}-{month}-{day}"
        logger.info(f"Fixed date format: {parts[1]} -> {date}")
    
    # Split description and extension
    if '.' in desc_with_ext:
        desc, ext = desc_with_ext.rsplit('.', 1)
    else:
        desc, ext = desc_with_ext, "md"
    
    # Convert description to snake_case
    snake_desc = snake_case(desc)
    
    # Create new filename
    new_filename = f"{prefix}_{date}_{snake_desc}.{ext}"
    
    # If filename already matches the standard, no changes needed
    if new_filename == filename:
        logger.info(f"No changes needed for {filename}")
        return False
    
    # Create new path
    new_path = file_path.parent / new_filename
    
    # Check if destination already exists
    if new_path.exists():
        logger.warning(f"Cannot rename {filename} to {new_filename}: destination already exists")
        return False
    
    # Rename file
    try:
        file_path.rename(new_path)
        logger.info(f"Successfully renamed: {filename} -> {new_filename}")
        return True
    except Exception as e:
        logger.error(f"Error renaming {filename}: {e}")
        return False

def main():
    """Main function to fix work log filenames."""
    logger.info("Starting work log filename fixing process...")
    
    # Problematic files identified from the diagnostic report
    problem_files = [
        "WORK_2025-05-23_Directory_Unification_Analysis.md",
        "WORK_2025-05-23_Work_Log_Standardization.md",
        "WORK_2025-05-24_DocOrganizerEnhancements.md",
        "WORK_2025-05-25_HARMONY_Live_Concept_Integration.md",
        "WORK_2025-05-25_MCP_Documentation_Standardization.md",
        "WORK_2025-05-25_MCP_Renaming_DIAGENIO_to_PRISM.md",
        "WORK_2025-05-26_MCP_Testing_Framework_Development.md",
        "WORK_2025_05_22_tool_registry_phase2.md",
        "WORK_2025_05_22_website_design_analysis.md",
    ]
    
    success_count = 0
    failure_count = 0
    
    for filename in problem_files:
        file_path = ACTIVE_DIR / filename
        if file_path.exists():
            if fix_work_log_filename(file_path):
                success_count += 1
            else:
                failure_count += 1
        else:
            logger.warning(f"File not found: {file_path}")
            failure_count += 1
    
    logger.info(f"Work log filename fixing completed: {success_count} succeeded, {failure_count} failed")
    
    # For additional fixes outside our specific list, scan the directory
    logger.info("Scanning for additional non-standard filenames...")
    additional_fixes = 0
    
    for file_path in ACTIVE_DIR.glob("WORK_*.md"):
        # Check if filename is already in snake_case
        filename = file_path.name
        parts = filename.split('_', 2)
        if len(parts) >= 3:
            desc_with_ext = parts[2]
            if not all(c.islower() or c.isdigit() or c == '_' or c == '.' for c in desc_with_ext):
                if fix_work_log_filename(file_path):
                    additional_fixes += 1
    
    logger.info(f"Additional non-standard filenames fixed: {additional_fixes}")
    logger.info("Process completed.")

if __name__ == "__main__":
    main()