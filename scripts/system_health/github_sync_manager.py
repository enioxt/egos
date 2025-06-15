#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Synchronization Manager for EGOS

This script implements a robust GitHub synchronization strategy as outlined in Section M of DiagEnio.md.
It provides utilities for:
1. Creating backups of critical files before Git operations
2. Systematically verifying repository integrity after synchronization
3. Properly handling large files using Git LFS or exclusion patterns
4. Comprehensive documentation of synchronization activities

Author: Cascade (AI Assistant)
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\DiagEnio.md (Section M: GitHub Synchronization Strategy)
    - C:\EGOS\MQP.md (CRONOS principles for versioning and preservation)
    - C:\EGOS\scripts\cross_reference\script_template_generator.py
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
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

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
    "BACKUP_DIR": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backups", "github_sync")),
    "CRITICAL_FILES": [
        "DiagEnio.md",
        "MQP.md",
        "ROADMAP.md",
        "README.md",
        "config/tool_registry.json",
        "scripts/cross_reference/script_template_generator.py"
    ],
    "CRITICAL_DIRS": [
        "docs/work_logs",
        "scripts/cross_reference",
        "config",
        "subsystems"
    ],
    "LARGE_FILE_THRESHOLD": 50 * 1024 * 1024,  # 50MB
    "LOG_LEVEL": logging.INFO,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_FILE": os.path.join(os.path.dirname(__file__), "..", "..", "logs", "github_sync.log"),
    "WORK_LOG_TEMPLATE": os.path.join(os.path.dirname(__file__), "..", "..", "docs", "work_logs", "WORK_{date}_GitHub_Sync.md")
}

# Configure logging
logging.basicConfig(
    level=CONFIG["LOG_LEVEL"],
    format=CONFIG["LOG_FORMAT"],
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("github_sync_manager")

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
    ║ {Fore.YELLOW}EGOS GitHub Synchronization Manager{Fore.CYAN}                    ║
    ║ {Fore.WHITE}Implementing robust synchronization strategies{Fore.CYAN}          ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


class GitHubSyncManager:
    """
    GitHub Synchronization Manager for EGOS.
    
    This class implements the synchronization strategy outlined in DiagEnio.md,
    providing utilities for backup, verification, and documentation of GitHub
    synchronization activities.
    """
    
    def __init__(self, egos_root: str = CONFIG["EGOS_ROOT"]):
        """
        Initialize the GitHub Synchronization Manager.
        
        Args:
            egos_root: Path to the EGOS root directory
        """
        self.egos_root = Path(egos_root)
        self.backup_dir = Path(CONFIG["BACKUP_DIR"])
        self.critical_files = CONFIG["CRITICAL_FILES"]
        self.critical_dirs = CONFIG["CRITICAL_DIRS"]
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup directory if it doesn't exist
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            logger.info(f"Created backup directory: {self.backup_dir}")
    
    def run_git_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run a Git command and return the result.
        
        Args:
            command: Git command as a list of strings
            cwd: Working directory for the command
            
        Returns:
            Tuple of (return code, stdout, stderr)
        """
        if cwd is None:
            cwd = self.egos_root
            
        try:
            process = subprocess.Popen(
                ["git"] + command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=cwd
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            logger.error(f"Error running Git command: {e}")
            return 1, "", str(e)
    
    def backup_critical_files(self) -> Path:
        """
        Create a backup of critical files before Git operations.
        
        Returns:
            Path to the backup directory
        """
        backup_path = self.backup_dir / f"backup_{self.timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating backup in {backup_path}")
        
        # Backup critical files
        for file_path in self.critical_files:
            src_path = self.egos_root / file_path
            if src_path.exists():
                # Create directory structure in backup
                dest_path = backup_path / file_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_path, dest_path)
                logger.info(f"Backed up {file_path}")
            else:
                logger.warning(f"Critical file not found for backup: {file_path}")
        
        # Backup critical directories
        for dir_path in self.critical_dirs:
            src_path = self.egos_root / dir_path
            if src_path.exists() and src_path.is_dir():
                # Create directory structure in backup
                dest_path = backup_path / dir_path
                
                # Copy directory recursively
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                logger.info(f"Backed up directory {dir_path}")
            else:
                logger.warning(f"Critical directory not found for backup: {dir_path}")
        
        # Create a manifest file with backup details
        manifest = {
            "timestamp": self.timestamp,
            "egos_root": str(self.egos_root),
            "files_backed_up": [str(f) for f in self.critical_files if (self.egos_root / f).exists()],
            "directories_backed_up": [str(d) for d in self.critical_dirs if (self.egos_root / d).exists()],
            "git_status": self.get_git_status()
        }
        
        with open(backup_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup completed: {backup_path}")
        return backup_path
    
    def get_git_status(self) -> Dict[str, Any]:
        """
        Get the current Git status information.
        
        Returns:
            Dictionary with Git status information
        """
        status = {}
        
        # Get current branch
        returncode, stdout, stderr = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if returncode == 0:
            status["current_branch"] = stdout.strip()
        else:
            status["current_branch"] = "unknown"
            logger.warning(f"Could not determine current branch: {stderr}")
        
        # Get remote information
        returncode, stdout, stderr = self.run_git_command(["remote", "-v"])
        if returncode == 0:
            remotes = {}
            for line in stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name, url = parts[0], parts[1]
                        remotes[name] = url
            status["remotes"] = remotes
        else:
            status["remotes"] = {}
            logger.warning(f"Could not get remote information: {stderr}")
        
        # Get last commit
        returncode, stdout, stderr = self.run_git_command(["log", "-1", "--pretty=format:%H|%an|%ad|%s"])
        if returncode == 0 and stdout.strip():
            parts = stdout.strip().split("|", 3)
            if len(parts) >= 4:
                status["last_commit"] = {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                }
        else:
            status["last_commit"] = {}
            logger.warning(f"Could not get last commit information: {stderr}")
        
        return status
    
    def verify_repository_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the repository after synchronization.
        
        Returns:
            Dictionary with verification results
        """
        verification = {
            "timestamp": self.timestamp,
            "critical_files_present": {},
            "critical_dirs_present": {},
            "large_files": [],
            "git_status": self.get_git_status(),
            "overall_status": "pass"
        }
        
        # Check critical files
        for file_path in self.critical_files:
            file_exists = (self.egos_root / file_path).exists()
            verification["critical_files_present"][file_path] = file_exists
            if not file_exists:
                verification["overall_status"] = "fail"
                logger.warning(f"Critical file missing: {file_path}")
        
        # Check critical directories
        for dir_path in self.critical_dirs:
            dir_exists = (self.egos_root / dir_path).exists() and (self.egos_root / dir_path).is_dir()
            verification["critical_dirs_present"][dir_path] = dir_exists
            if not dir_exists:
                verification["overall_status"] = "fail"
                logger.warning(f"Critical directory missing: {dir_path}")
        
        # Check for large files that might cause GitHub issues
        for root, _, files in os.walk(self.egos_root):
            for file in files:
                file_path = Path(root) / file
                if file_path.exists() and file_path.stat().st_size > CONFIG["LARGE_FILE_THRESHOLD"]:
                    rel_path = file_path.relative_to(self.egos_root)
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    verification["large_files"].append({
                        "path": str(rel_path),
                        "size_mb": round(size_mb, 2)
                    })
                    logger.warning(f"Large file detected: {rel_path} ({round(size_mb, 2)} MB)")
        
        # Save verification results
        verification_path = self.backup_dir / f"verification_{self.timestamp}.json"
        with open(verification_path, "w") as f:
            json.dump(verification, f, indent=2)
        
        logger.info(f"Repository verification completed: {verification_path}")
        return verification
    
    def create_work_log(self, operation: str, details: Dict[str, Any]) -> Path:
        """
        Create a work log documenting the synchronization activity.
        
        Args:
            operation: The synchronization operation performed
            details: Details of the operation
            
        Returns:
            Path to the created work log
        """
        date = datetime.datetime.now().strftime("%Y_%m_%d")
        work_log_path = Path(CONFIG["WORK_LOG_TEMPLATE"].format(date=date))
        
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
title: "Work Log - {date}: GitHub Synchronization - {operation}"
date: {datetime.datetime.now().strftime("%Y-%m-%d")}
author: EGOS GitHub Sync Manager
project: EGOS
tags: [github, synchronization, maintenance]
---

## EGOS Work Log: GitHub Synchronization

### Objective:
Document the GitHub synchronization activity: {operation}

### Details:

1. **Operation:** {operation}
2. **Timestamp:** {self.timestamp}
3. **Branch:** {details.get("git_status", {}).get("current_branch", "unknown")}

### Actions Performed:

"""
        
        # Add operation-specific details
        if operation == "backup":
            content += f"""1. **Backup Created:**
   * Location: {details.get("backup_path", "unknown")}
   * Files backed up: {len(details.get("files_backed_up", []))}
   * Directories backed up: {len(details.get("directories_backed_up", []))}

2. **Critical Files Backed Up:**
"""
            for file in details.get("files_backed_up", []):
                content += f"   * `{file}`\n"
            
            content += "\n3. **Critical Directories Backed Up:**\n"
            for directory in details.get("directories_backed_up", []):
                content += f"   * `{directory}`\n"
        
        elif operation == "verification":
            content += f"""1. **Repository Integrity Check:**
   * Overall status: {details.get("overall_status", "unknown").upper()}
   * Critical files checked: {len(details.get("critical_files_present", {}))}
   * Critical directories checked: {len(details.get("critical_dirs_present", {}))}

2. **Missing Critical Files:**
"""
            missing_files = [f for f, exists in details.get("critical_files_present", {}).items() if not exists]
            if missing_files:
                for file in missing_files:
                    content += f"   * `{file}`\n"
            else:
                content += "   * None\n"
            
            content += "\n3. **Missing Critical Directories:**\n"
            missing_dirs = [d for d, exists in details.get("critical_dirs_present", {}).items() if not exists]
            if missing_dirs:
                for directory in missing_dirs:
                    content += f"   * `{directory}`\n"
            else:
                content += "   * None\n"
            
            content += "\n4. **Large Files Detected:**\n"
            if details.get("large_files", []):
                for file in details.get("large_files", []):
                    content += f"   * `{file['path']}` ({file['size_mb']} MB)\n"
            else:
                content += "   * None\n"
        
        # Add cross-references and conclusion
        content += f"""
### Cross-References:
* `C:\\EGOS\\DiagEnio.md` - Section M: GitHub Synchronization Strategy
* `C:\\EGOS\\MQP.md` - CRONOS principles for versioning and preservation
* `C:\\EGOS\\scripts\\maintenance\\github_sync_manager.py`

### Conclusion:
GitHub synchronization activity "{operation}" completed successfully. This work log documents the actions taken and results for future reference, in accordance with EGOS principles of Evolutionary Preservation and Conscious Modularity.

✧༺❀༻∞ EGOS ∞༺❀༻✧
"""
        
        # Write work log to file
        with open(work_log_path, "w") as f:
            f.write(content)
        
        logger.info(f"Created work log: {work_log_path}")
        return work_log_path
    
    def check_for_large_files(self) -> List[Dict[str, Any]]:
        """
        Check for large files that might cause GitHub issues.
        
        Returns:
            List of dictionaries with information about large files
        """
        large_files = []
        
        for root, _, files in os.walk(self.egos_root):
            # Skip .git directory
            if ".git" in Path(root).parts:
                continue
                
            for file in files:
                file_path = Path(root) / file
                if file_path.exists() and file_path.stat().st_size > CONFIG["LARGE_FILE_THRESHOLD"]:
                    rel_path = file_path.relative_to(self.egos_root)
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    large_files.append({
                        "path": str(rel_path),
                        "size_mb": round(size_mb, 2),
                        "absolute_path": str(file_path)
                    })
        
        return large_files
    
    def update_gitignore_for_large_files(self, large_files: List[Dict[str, Any]]) -> bool:
        """
        Update .gitignore to exclude large files.
        
        Args:
            large_files: List of large files to exclude
            
        Returns:
            True if .gitignore was updated, False otherwise
        """
        gitignore_path = self.egos_root / ".gitignore"
        
        # Read existing .gitignore
        existing_patterns = []
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                existing_patterns = [line.strip() for line in f.readlines()]
        
        # Create patterns for large files
        new_patterns = []
        for file_info in large_files:
            file_path = file_info["path"]
            pattern = str(file_path).replace("\\", "/")
            
            # Also add a pattern for similar files
            file_name = Path(file_path).name
            file_prefix = file_name.split("_")[0] if "_" in file_name else file_name.split(".")[0]
            file_suffix = "".join(Path(file_path).suffixes)
            pattern_generic = f"**/{file_prefix}*{file_suffix}"
            
            if pattern not in existing_patterns:
                new_patterns.append(pattern)
            if pattern_generic not in existing_patterns:
                new_patterns.append(pattern_generic)
        
        if not new_patterns:
            logger.info("No new patterns to add to .gitignore")
            return False
        
        # Add a section header if we're adding new patterns
        with open(gitignore_path, "a") as f:
            f.write("\n\n# Large files identified by github_sync_manager.py\n")
            for pattern in new_patterns:
                f.write(f"{pattern}\n")
        
        logger.info(f"Updated .gitignore with {len(new_patterns)} patterns for large files")
        return True
    
    def perform_backup(self) -> Dict[str, Any]:
        """
        Perform a backup of critical files and directories.
        
        Returns:
            Dictionary with backup details
        """
        backup_path = self.backup_critical_files()
        
        # Get details for work log
        details = {
            "backup_path": str(backup_path),
            "files_backed_up": [str(f) for f in self.critical_files if (self.egos_root / f).exists()],
            "directories_backed_up": [str(d) for d in self.critical_dirs if (self.egos_root / d).exists()],
            "git_status": self.get_git_status()
        }
        
        # Create work log
        work_log_path = self.create_work_log("backup", details)
        details["work_log_path"] = str(work_log_path)
        
        return details
    
    def perform_verification(self) -> Dict[str, Any]:
        """
        Perform verification of repository integrity.
        
        Returns:
            Dictionary with verification details
        """
        verification = self.verify_repository_integrity()
        
        # Create work log
        work_log_path = self.create_work_log("verification", verification)
        verification["work_log_path"] = str(work_log_path)
        
        return verification
    
    def handle_large_files(self) -> Dict[str, Any]:
        """
        Handle large files that might cause GitHub issues.
        
        Returns:
            Dictionary with large file handling details
        """
        large_files = self.check_for_large_files()
        
        if not large_files:
            logger.info("No large files detected")
            return {"large_files": []}
        
        logger.warning(f"Detected {len(large_files)} large files that may cause GitHub issues")
        
        # Update .gitignore
        gitignore_updated = self.update_gitignore_for_large_files(large_files)
        
        details = {
            "large_files": large_files,
            "gitignore_updated": gitignore_updated,
            "git_status": self.get_git_status()
        }
        
        # Create work log
        work_log_path = self.create_work_log("large_file_handling", details)
        details["work_log_path"] = str(work_log_path)
        
        return details


def main():
    """Main function to run the GitHub Synchronization Manager."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="EGOS GitHub Synchronization Manager")
    parser.add_argument("--backup", action="store_true", help="Create a backup of critical files")
    parser.add_argument("--verify", action="store_true", help="Verify repository integrity")
    parser.add_argument("--handle-large-files", action="store_true", help="Handle large files that might cause GitHub issues")
    parser.add_argument("--all", action="store_true", help="Perform all operations")
    parser.add_argument("--egos-root", type=str, default=CONFIG["EGOS_ROOT"], help="Path to EGOS root directory")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not (args.backup or args.verify or args.handle_large_files or args.all):
        parser.print_help()
        return
    
    sync_manager = GitHubSyncManager(egos_root=args.egos_root)
    
    if args.backup or args.all:
        print(f"{Fore.GREEN}Performing backup of critical files...{Style.RESET_ALL}")
        details = sync_manager.perform_backup()
        print(f"{Fore.GREEN}Backup completed: {details['backup_path']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Work log created: {details['work_log_path']}{Style.RESET_ALL}")
    
    if args.verify or args.all:
        print(f"{Fore.GREEN}Verifying repository integrity...{Style.RESET_ALL}")
        details = sync_manager.perform_verification()
        status = details.get("overall_status", "unknown").upper()
        color = Fore.GREEN if status == "PASS" else Fore.RED
        print(f"{color}Verification status: {status}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Work log created: {details['work_log_path']}{Style.RESET_ALL}")
    
    if args.handle_large_files or args.all:
        print(f"{Fore.GREEN}Checking for large files...{Style.RESET_ALL}")
        details = sync_manager.handle_large_files()
        if details["large_files"]:
            print(f"{Fore.YELLOW}Detected {len(details['large_files'])} large files that may cause GitHub issues{Style.RESET_ALL}")
            for file in details["large_files"]:
                print(f"{Fore.YELLOW}  - {file['path']} ({file['size_mb']} MB){Style.RESET_ALL}")
            if details["gitignore_updated"]:
                print(f"{Fore.GREEN}.gitignore updated to exclude large files{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Work log created: {details['work_log_path']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}No large files detected{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}EGOS GitHub Synchronization Manager completed successfully!{Style.RESET_ALL}")
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