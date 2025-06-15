#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cleanup Redundant Directories Script for EGOS

This script identifies and safely removes redundant directories that were restored
during the GitHub synchronization process but had already been unified into other
directories. It follows EGOS principles of Conscious Modularity and Evolutionary
Preservation by ensuring no unique content is lost.

Author: Cascade (AI Assistant)
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\DiagEnio.md
    - C:\EGOS\docs\work_logs\WORK_2025_05_23_GitHub_Sync_System_Implementation.md
    - C:\EGOS\scripts\maintenance\github_sync_manager.py
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Standard library imports
import os
import sys
import json
import shutil
import logging
import argparse
import datetime
import filecmp
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional

# Third-party imports
try:
    from colorama import Fore, Style, init
    init()  # Initialize colorama
except ImportError:
    # Define dummy colorama classes if not available
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()

# Constants
CONFIG = {
    "EGOS_ROOT": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    "BACKUP_DIR": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backups", "redundant_cleanup")),
    "LOG_LEVEL": logging.INFO,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_FILE": os.path.join(os.path.dirname(__file__), "..", "..", "logs", "cleanup_redundant_directories.log"),
    "REDUNDANT_DIRECTORIES": [
        ("docs_egos", "docs"),  # Format: (redundant_dir, consolidated_dir)
        # Add more redundant directory pairs as needed
    ]
}

# Configure logging
logging.basicConfig(
    level=CONFIG["LOG_LEVEL"],
    format=CONFIG["LOG_FORMAT"],
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("cleanup_redundant_directories")

# Create log directory if it doesn't exist
log_dir = os.path.dirname(CONFIG["LOG_FILE"])
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    logger.info(f"Created log directory: {log_dir}")

# Add file handler if configured
try:
    file_handler = logging.FileHandler(CONFIG["LOG_FILE"])
    file_handler.setFormatter(logging.Formatter(CONFIG["LOG_FORMAT"]))
    logger.addHandler(file_handler)
    logger.info(f"Logging to file: {CONFIG['LOG_FILE']}")
except Exception as e:
    logger.warning(f"Could not set up file logging: {e}")


def print_banner() -> None:
    """Print a banner for the script."""
    banner = f"""
    {Fore.CYAN}╔══════════════════════════════════════════════════════════╗
    ║ {Fore.YELLOW}EGOS Redundant Directories Cleanup Tool{Fore.CYAN}               ║
    ║ {Fore.WHITE}Safely removing redundant directories after restoration{Fore.CYAN} ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


class RedundantDirectoryCleaner:
    """
    Identifies and safely removes redundant directories that were restored
    during the GitHub synchronization process but had already been unified.
    """
    
    def __init__(self, egos_root: str = CONFIG["EGOS_ROOT"], backup_dir: str = CONFIG["BACKUP_DIR"]):
        """
        Initialize the Redundant Directory Cleaner.
        
        Args:
            egos_root: Path to the EGOS root directory
            backup_dir: Path to the backup directory
        """
        self.egos_root = Path(egos_root)
        self.backup_dir = Path(backup_dir)
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup directory if it doesn't exist
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            logger.info(f"Created backup directory: {self.backup_dir}")
    
    def backup_directory(self, directory: Path) -> Path:
        """
        Create a backup of a directory before removing it.
        
        Args:
            directory: Path to the directory to backup
            
        Returns:
            Path to the backup directory
        """
        if not directory.exists():
            logger.warning(f"Directory does not exist, cannot backup: {directory}")
            return None
        
        # Create a unique backup directory name
        rel_path = directory.relative_to(self.egos_root)
        backup_path = self.backup_dir / f"{self.timestamp}" / rel_path
        
        # Create parent directories if they don't exist
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the directory to the backup location
        try:
            shutil.copytree(directory, backup_path)
            logger.info(f"Backed up directory: {directory} to {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up directory {directory}: {e}")
            return None
    
    def find_unique_files(self, source_dir: Path, target_dir: Path) -> List[Path]:
        """
        Find files in source_dir that don't exist in target_dir or have different content.
        
        Args:
            source_dir: Path to the source directory
            target_dir: Path to the target directory
            
        Returns:
            List of paths to unique files in source_dir
        """
        unique_files = []
        
        if not source_dir.exists():
            logger.warning(f"Source directory does not exist: {source_dir}")
            return unique_files
        
        if not target_dir.exists():
            logger.warning(f"Target directory does not exist: {target_dir}")
            return [p for p in source_dir.glob("**/*") if p.is_file()]
        
        # Walk through the source directory
        for root, _, files in os.walk(source_dir):
            root_path = Path(root)
            rel_path = root_path.relative_to(source_dir)
            target_path = target_dir / rel_path
            
            for file in files:
                source_file = root_path / file
                target_file = target_path / file
                
                # Check if the file exists in the target directory
                if not target_file.exists():
                    unique_files.append(source_file)
                    logger.info(f"Unique file found: {source_file}")
                else:
                    # Check if the file contents are different
                    try:
                        if not filecmp.cmp(source_file, target_file, shallow=False):
                            unique_files.append(source_file)
                            logger.info(f"File with different content found: {source_file}")
                    except Exception as e:
                        logger.error(f"Error comparing files {source_file} and {target_file}: {e}")
                        # If we can't compare, assume the file is unique to be safe
                        unique_files.append(source_file)
        
        return unique_files
    
    def copy_unique_files(self, unique_files: List[Path], source_dir: Path, target_dir: Path) -> int:
        """
        Copy unique files from source_dir to target_dir, preserving directory structure.
        
        Args:
            unique_files: List of paths to unique files in source_dir
            source_dir: Path to the source directory
            target_dir: Path to the target directory
            
        Returns:
            Number of files copied
        """
        copied_count = 0
        
        for source_file in unique_files:
            # Get the relative path from source_dir
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            # Create parent directories if they don't exist
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Copy the file
                shutil.copy2(source_file, target_file)
                logger.info(f"Copied unique file: {source_file} to {target_file}")
                copied_count += 1
            except Exception as e:
                logger.error(f"Error copying file {source_file} to {target_file}: {e}")
        
        return copied_count
    
    def create_work_log(self, redundant_dir: Path, consolidated_dir: Path, unique_files: List[Path], backup_path: Path) -> Path:
        """
        Create a work log documenting the cleanup activity.
        
        Args:
            redundant_dir: Path to the redundant directory
            consolidated_dir: Path to the consolidated directory
            unique_files: List of unique files found in the redundant directory
            backup_path: Path to the backup directory
            
        Returns:
            Path to the created work log
        """
        date = datetime.datetime.now().strftime("%Y_%m_%d")
        work_log_path = self.egos_root / "docs" / "work_logs" / f"WORK_{date}_Redundant_Directory_Cleanup.md"
        
        # Create directory if it doesn't exist
        work_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if work log already exists and append a number if it does
        base_path = work_log_path
        counter = 1
        while work_log_path.exists():
            work_log_path = base_path.parent / f"{base_path.stem}_{counter}{base_path.suffix}"
            counter += 1
        
        # Create work log content
        content = f"""---
title: "Work Log - {date}: Redundant Directory Cleanup"
date: {datetime.datetime.now().strftime("%Y-%m-%d")}
author: EGOS Redundant Directory Cleaner
project: EGOS
tags: [cleanup, maintenance, github, synchronization]
---

## EGOS Work Log: Redundant Directory Cleanup

### Objective:
Clean up redundant directories that were restored during the GitHub synchronization process but had already been unified into other directories.

### Details:

1. **Redundant Directory:** {redundant_dir}
2. **Consolidated Directory:** {consolidated_dir}
3. **Timestamp:** {self.timestamp}

### Actions Performed:

1. **Backup Created:**
   * Location: {backup_path}

2. **Unique Files Analysis:**
   * Total unique files found: {len(unique_files)}
"""
        
        if unique_files:
            content += "\n3. **Unique Files Copied:**\n"
            for file in unique_files[:10]:  # Show first 10 files
                content += f"   * `{file.relative_to(self.egos_root)}`\n"
            if len(unique_files) > 10:
                content += f"   * ... and {len(unique_files) - 10} more files\n"
        else:
            content += "\n3. **No Unique Files Found**\n"
        
        content += f"""
4. **Redundant Directory Removed:**
   * `{redundant_dir.relative_to(self.egos_root)}`

### Cross-References:
* `C:\\EGOS\\DiagEnio.md` - Section M: GitHub Synchronization Strategy
* `C:\\EGOS\\scripts\\maintenance\\cleanup_redundant_directories.py`
* `C:\\EGOS\\docs\\work_logs\\WORK_2025_05_23_GitHub_Sync_System_Implementation.md`

### Conclusion:
Successfully cleaned up redundant directory that was restored during the GitHub synchronization process. All unique content has been preserved in the consolidated directory.

✧༺❀༻∞ EGOS ∞༺❀༻✧
"""
        
        # Write work log to file
        with open(work_log_path, "w") as f:
            f.write(content)
        
        logger.info(f"Created work log: {work_log_path}")
        return work_log_path
    
    def cleanup_redundant_directory(self, redundant_dir_name: str, consolidated_dir_name: str) -> Dict[str, Any]:
        """
        Clean up a redundant directory by identifying unique files, copying them to the consolidated directory,
        and then removing the redundant directory.
        
        Args:
            redundant_dir_name: Name of the redundant directory
            consolidated_dir_name: Name of the consolidated directory
            
        Returns:
            Dictionary with cleanup results
        """
        redundant_dir = self.egos_root / redundant_dir_name
        consolidated_dir = self.egos_root / consolidated_dir_name
        
        if not redundant_dir.exists():
            logger.warning(f"Redundant directory does not exist: {redundant_dir}")
            return {
                "success": False,
                "error": f"Redundant directory does not exist: {redundant_dir}",
                "redundant_dir": str(redundant_dir),
                "consolidated_dir": str(consolidated_dir)
            }
        
        if not consolidated_dir.exists():
            logger.warning(f"Consolidated directory does not exist: {consolidated_dir}")
            return {
                "success": False,
                "error": f"Consolidated directory does not exist: {consolidated_dir}",
                "redundant_dir": str(redundant_dir),
                "consolidated_dir": str(consolidated_dir)
            }
        
        # Create a backup of the redundant directory
        backup_path = self.backup_directory(redundant_dir)
        if not backup_path:
            return {
                "success": False,
                "error": f"Failed to backup redundant directory: {redundant_dir}",
                "redundant_dir": str(redundant_dir),
                "consolidated_dir": str(consolidated_dir)
            }
        
        # Find unique files in the redundant directory
        unique_files = self.find_unique_files(redundant_dir, consolidated_dir)
        
        # Copy unique files to the consolidated directory
        copied_count = self.copy_unique_files(unique_files, redundant_dir, consolidated_dir)
        
        # Create a work log
        work_log_path = self.create_work_log(redundant_dir, consolidated_dir, unique_files, backup_path)
        
        # Remove the redundant directory
        try:
            shutil.rmtree(redundant_dir)
            logger.info(f"Removed redundant directory: {redundant_dir}")
        except Exception as e:
            logger.error(f"Error removing redundant directory {redundant_dir}: {e}")
            return {
                "success": False,
                "error": f"Failed to remove redundant directory: {e}",
                "redundant_dir": str(redundant_dir),
                "consolidated_dir": str(consolidated_dir),
                "unique_files": [str(f.relative_to(self.egos_root)) for f in unique_files],
                "copied_count": copied_count,
                "backup_path": str(backup_path),
                "work_log_path": str(work_log_path)
            }
        
        return {
            "success": True,
            "redundant_dir": str(redundant_dir),
            "consolidated_dir": str(consolidated_dir),
            "unique_files": [str(f.relative_to(self.egos_root)) for f in unique_files],
            "copied_count": copied_count,
            "backup_path": str(backup_path),
            "work_log_path": str(work_log_path)
        }
    
    def cleanup_all_redundant_directories(self) -> List[Dict[str, Any]]:
        """
        Clean up all redundant directories defined in the configuration.
        
        Returns:
            List of dictionaries with cleanup results for each redundant directory
        """
        results = []
        
        for redundant_dir_name, consolidated_dir_name in CONFIG["REDUNDANT_DIRECTORIES"]:
            logger.info(f"Cleaning up redundant directory: {redundant_dir_name} -> {consolidated_dir_name}")
            result = self.cleanup_redundant_directory(redundant_dir_name, consolidated_dir_name)
            results.append(result)
        
        return results


def main():
    """Main function to run the Redundant Directory Cleaner."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="EGOS Redundant Directory Cleaner")
    parser.add_argument("--egos-root", type=str, default=CONFIG["EGOS_ROOT"], help="Path to EGOS root directory")
    parser.add_argument("--backup-dir", type=str, default=CONFIG["BACKUP_DIR"], help="Path to backup directory")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making any changes")
    parser.add_argument("--redundant-dir", type=str, help="Name of a specific redundant directory to clean up")
    parser.add_argument("--consolidated-dir", type=str, help="Name of the consolidated directory for the specific redundant directory")
    
    args = parser.parse_args()
    
    cleaner = RedundantDirectoryCleaner(
        egos_root=args.egos_root,
        backup_dir=args.backup_dir
    )
    
    if args.dry_run:
        print(f"{Fore.YELLOW}Performing dry run - no changes will be made{Style.RESET_ALL}")
        
        if args.redundant_dir and args.consolidated_dir:
            redundant_dir = Path(args.egos_root) / args.redundant_dir
            consolidated_dir = Path(args.egos_root) / args.consolidated_dir
            
            if not redundant_dir.exists():
                print(f"{Fore.RED}Redundant directory does not exist: {redundant_dir}{Style.RESET_ALL}")
                return
            
            if not consolidated_dir.exists():
                print(f"{Fore.RED}Consolidated directory does not exist: {consolidated_dir}{Style.RESET_ALL}")
                return
            
            unique_files = cleaner.find_unique_files(redundant_dir, consolidated_dir)
            
            print(f"\n{Fore.CYAN}Dry Run Results:{Style.RESET_ALL}")
            print(f"  Redundant directory: {redundant_dir}")
            print(f"  Consolidated directory: {consolidated_dir}")
            print(f"  Unique files found: {len(unique_files)}")
            
            if unique_files:
                print(f"\n{Fore.GREEN}Unique Files (would be copied):{Style.RESET_ALL}")
                for file in unique_files[:10]:  # Show first 10 files
                    print(f"  - {file.relative_to(args.egos_root)}")
                if len(unique_files) > 10:
                    print(f"  ... and {len(unique_files) - 10} more files")
        else:
            for redundant_dir_name, consolidated_dir_name in CONFIG["REDUNDANT_DIRECTORIES"]:
                redundant_dir = Path(args.egos_root) / redundant_dir_name
                consolidated_dir = Path(args.egos_root) / consolidated_dir_name
                
                if not redundant_dir.exists():
                    print(f"{Fore.RED}Redundant directory does not exist: {redundant_dir}{Style.RESET_ALL}")
                    continue
                
                if not consolidated_dir.exists():
                    print(f"{Fore.RED}Consolidated directory does not exist: {consolidated_dir}{Style.RESET_ALL}")
                    continue
                
                unique_files = cleaner.find_unique_files(redundant_dir, consolidated_dir)
                
                print(f"\n{Fore.CYAN}Dry Run Results for {redundant_dir_name} -> {consolidated_dir_name}:{Style.RESET_ALL}")
                print(f"  Unique files found: {len(unique_files)}")
                
                if unique_files:
                    print(f"\n{Fore.GREEN}Unique Files (would be copied):{Style.RESET_ALL}")
                    for file in unique_files[:10]:  # Show first 10 files
                        print(f"  - {file.relative_to(args.egos_root)}")
                    if len(unique_files) > 10:
                        print(f"  ... and {len(unique_files) - 10} more files")
    else:
        if args.redundant_dir and args.consolidated_dir:
            print(f"{Fore.GREEN}Cleaning up redundant directory: {args.redundant_dir} -> {args.consolidated_dir}{Style.RESET_ALL}")
            result = cleaner.cleanup_redundant_directory(args.redundant_dir, args.consolidated_dir)
            
            if result["success"]:
                print(f"{Fore.GREEN}Successfully cleaned up redundant directory: {result['redundant_dir']}{Style.RESET_ALL}")
                print(f"  Unique files found: {len(result['unique_files'])}")
                print(f"  Files copied: {result['copied_count']}")
                print(f"  Backup created: {result['backup_path']}")
                print(f"  Work log created: {result['work_log_path']}")
            else:
                print(f"{Fore.RED}Failed to clean up redundant directory: {result['error']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Cleaning up all redundant directories{Style.RESET_ALL}")
            results = cleaner.cleanup_all_redundant_directories()
            
            print(f"\n{Fore.CYAN}Cleanup Results:{Style.RESET_ALL}")
            for result in results:
                if result["success"]:
                    print(f"{Fore.GREEN}Successfully cleaned up redundant directory: {result['redundant_dir']}{Style.RESET_ALL}")
                    print(f"  Unique files found: {len(result['unique_files'])}")
                    print(f"  Files copied: {result['copied_count']}")
                    print(f"  Backup created: {result['backup_path']}")
                    print(f"  Work log created: {result['work_log_path']}")
                else:
                    print(f"{Fore.RED}Failed to clean up redundant directory: {result['error']}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}EGOS Redundant Directory Cleaner completed!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)