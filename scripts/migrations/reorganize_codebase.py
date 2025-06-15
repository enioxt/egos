#!/usr/bin/env python3
"""
EGOS Codebase Reorganization Script

Automates the reorganization of EGOS codebase according to the plan outlined in
the Kernel Factory & PromptVault Integration project.

Cross-References:
    - .windsurfrules → RULE-FS-STRUCTURE
    - archive/handovers/handover_EGOS_Kernel_PromptVault_Integration_20250611.md
    - ADRS_Log.md (will be updated with migration results)
    - scripts/validation/validate_directory_structure.py (for post-migration validation)
"""
# 
# @references:
#   - scripts/migrations/reorganize_codebase.py

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Define reorganization plan
REORGANIZATION_PLAN = [
    # (source_path, destination_path, description)
    ("masterpromptdemo.md", "archive/ideation/masterpromptdemo.md", 
     "Early draft that evolved into MSAK kernel"),
    ("masterpromptdemo2.md", "archive/ideation/masterpromptdemo2.md", 
     "Second iteration draft that evolved into MSAK kernel"),
    ("masterpromptdemo3.md", "archive/ideation/masterpromptdemo3.md", 
     "Third iteration draft that evolved into MSAK kernel"),
    ("scripts/migrations", "archive/scripts_migrations_2025-05", 
     "Legacy migration scripts from early June 2025"),
    ("scripts/nexus", "archive/nexus_legacy", 
     "Early PoC for Mycelium+TaskMaster integration, superseded by MCP servers"),
]

# Files that need reference updates
FILES_TO_UPDATE = [
    "README.md",
    ".windsurfrules",
    "config/tool_registry.json",
    "ROADMAP.md"
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EGOS Codebase Reorganization Tool")
    parser.add_argument("--base-path", default="C:/EGOS", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--generate-adrs", action="store_true", help="Generate ADRS entry for the reorganization")
    return parser.parse_args()

def move_files(base_path: str, dry_run: bool = False) -> List[Tuple[str, str, bool]]:
    """
    Move files according to the reorganization plan.
    Returns a list of (source, destination, success) tuples.
    """
    results = []
    
    for source_rel, dest_rel, _ in REORGANIZATION_PLAN:
        source = os.path.join(base_path, source_rel)
        dest = os.path.join(base_path, dest_rel)
        
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir) and not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            print(f"Created directory: {dest_dir}")
        
        success = True
        try:
            if dry_run:
                print(f"Would move {source} -> {dest}")
            else:
                if os.path.isdir(source):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                    shutil.rmtree(source)
                    print(f"Moved directory: {source} -> {dest}")
                else:
                    shutil.copy2(source, dest)
                    os.remove(source)
                    print(f"Moved file: {source} -> {dest}")
        except Exception as e:
            print(f"Error moving {source} -> {dest}: {e}", file=sys.stderr)
            success = False
        
        results.append((source_rel, dest_rel, success))
    
    return results

def update_references(base_path: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Update references in key files.
    Returns a dictionary with file paths and the number of updates made.
    """
    updates = {}
    
    # For each file that might contain references
    for file_rel in FILES_TO_UPDATE:
        file_path = os.path.join(base_path, file_rel)
        if not os.path.exists(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            updates_count = 0
            
            # Replace references according to the reorganization plan
            for source_rel, dest_rel, _ in REORGANIZATION_PLAN:
                # Handle both absolute and relative paths
                source_patterns = [
                    source_rel,
                    f"/{source_rel}",
                    f"\\{source_rel}",
                    f"{base_path}/{source_rel}",
                    f"{base_path}\\{source_rel}"
                ]
                
                for pattern in source_patterns:
                    if pattern in content:
                        # Replace with the new path, preserving the same path style
                        replacement = pattern.replace(source_rel, dest_rel)
                        content = content.replace(pattern, replacement)
                        updates_count += 1
            
            if content != original_content:
                if dry_run:
                    print(f"Would update {updates_count} references in {file_rel}")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {updates_count} references in {file_rel}")
                
                updates[file_rel] = updates_count
        
        except Exception as e:
            print(f"Error updating references in {file_rel}: {e}", file=sys.stderr)
    
    return updates

def generate_adrs_entry(move_results: List[Tuple[str, str, bool]], 
                       reference_updates: Dict[str, int]) -> str:
    """Generate an ADRS log entry for the reorganization."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00")
    
    # Count successes and failures
    successes = sum(1 for _, _, success in move_results if success)
    failures = len(move_results) - successes
    
    total_ref_updates = sum(reference_updates.values())
    
    entry = f"""
## {timestamp} - Codebase Reorganization for Kernel Factory & PromptVault Integration

**Type:** System Maintenance
**Status:** Completed
**Reporter:** Automated Script (reorganize_codebase.py)

### Description
Executed planned reorganization of EGOS codebase to improve structure and maintainability.
Moved legacy files to appropriate archive locations and updated references.

### Details
- Files/directories moved: {successes} successful, {failures} failed
- Reference updates: {total_ref_updates} across {len(reference_updates)} files

#### Moved Items:
"""
    
    for source, dest, success in move_results:
        status = "✓" if success else "✗"
        entry += f"- {status} {source} → {dest}\n"
    
    if reference_updates:
        entry += "\n#### Updated References:\n"
        for file, count in reference_updates.items():
            entry += f"- {file}: {count} updates\n"
    
    entry += """
### Root Cause
Planned reorganization to improve codebase structure and reduce technical debt.

### Resolution
Files have been moved to more appropriate locations and references updated.
Validators should be run to confirm system integrity.

### Prevention
Regular codebase audits and adherence to the directory structure standards.
"""
    
    return entry

def main() -> None:
    args = parse_args()
    base_path = args.base_path
    dry_run = args.dry_run
    
    print(f"{'[DRY RUN] ' if dry_run else ''}EGOS Codebase Reorganization")
    print(f"Base path: {base_path}")
    print("=" * 50)
    
    # Execute the reorganization
    move_results = move_files(base_path, dry_run)
    reference_updates = update_references(base_path, dry_run)
    
    # Generate ADRS entry if requested
    if args.generate_adrs and not dry_run:
        adrs_entry = generate_adrs_entry(move_results, reference_updates)
        adrs_path = os.path.join(base_path, "ADRS_Log.md")
        
        try:
            with open(adrs_path, 'r', encoding='utf-8') as f:
                adrs_content = f.read()
            
            # Insert the new entry after the first heading
            first_heading_end = adrs_content.find('\n', adrs_content.find('# '))
            if first_heading_end > 0:
                new_content = adrs_content[:first_heading_end] + adrs_entry + adrs_content[first_heading_end:]
                
                with open(adrs_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Added ADRS entry to {adrs_path}")
        except Exception as e:
            print(f"Error updating ADRS log: {e}", file=sys.stderr)
            print("Generated ADRS entry:")
            print(adrs_entry)
    
    # Summary
    print("\nSummary:")
    print(f"- Files/directories processed: {len(move_results)}")
    print(f"- Successful moves: {sum(1 for _, _, s in move_results if s)}")
    print(f"- Failed moves: {sum(1 for _, _, s in move_results if not s)}")
    print(f"- Files with updated references: {len(reference_updates)}")
    print(f"- Total reference updates: {sum(reference_updates.values())}")
    
    if dry_run:
        print("\nThis was a dry run. No files were actually moved or modified.")
        print("Run without --dry-run to execute the reorganization.")

if __name__ == "__main__":
    main()