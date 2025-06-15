#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Restore Missing Files from GitHub Repository

This script identifies files that exist in the GitHub repository but are missing from the local repository,
and downloads them to restore the local repository to a complete state.

Author: Cascade (AI Assistant)
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\DiagEnio.md (Section M: GitHub Synchronization Strategy)
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
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Set

# Third-party imports
try:
    import requests
    from colorama import Fore, Style, init
    init()  # Initialize colorama
except ImportError:
    print("Required dependencies not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "colorama"])
    import requests
    from colorama import Fore, Style, init
    init()  # Initialize colorama

# Constants
CONFIG = {
    "EGOS_ROOT": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
    "GITHUB_REPO": "enioxt/egos",
    "GITHUB_BRANCH": "main",
    "LOG_LEVEL": logging.INFO,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOG_FILE": os.path.join(os.path.dirname(__file__), "..", "..", "logs", "restore_missing_files.log"),
}

# Configure logging
logging.basicConfig(
    level=CONFIG["LOG_LEVEL"],
    format=CONFIG["LOG_FORMAT"],
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("restore_missing_files")

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
    ║ {Fore.YELLOW}EGOS Missing Files Restoration Tool{Fore.CYAN}                   ║
    ║ {Fore.WHITE}Restoring files from GitHub to local repository{Fore.CYAN}        ║
    ╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


class MissingFilesRestorer:
    """
    Identifies and restores files that exist in the GitHub repository but are missing from the local repository.
    """
    
    def __init__(self, egos_root: str = CONFIG["EGOS_ROOT"], github_repo: str = CONFIG["GITHUB_REPO"], github_branch: str = CONFIG["GITHUB_BRANCH"]):
        """
        Initialize the Missing Files Restorer.
        
        Args:
            egos_root: Path to the EGOS root directory
            github_repo: GitHub repository in the format "username/repo"
            github_branch: GitHub branch to compare against
        """
        self.egos_root = Path(egos_root)
        self.github_repo = github_repo
        self.github_branch = github_branch
        
    def get_github_files(self) -> Set[str]:
        """
        Get a set of all files in the GitHub repository.
        
        Returns:
            Set of file paths in the GitHub repository
        """
        logger.info(f"Fetching files from GitHub repository: {self.github_repo}, branch: {self.github_branch}")
        
        # Use GitHub API to get the repository tree
        url = f"https://api.github.com/repos/{self.github_repo}/git/trees/{self.github_branch}?recursive=1"
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch repository tree from GitHub: {response.status_code} {response.reason}")
            return set()
        
        # Parse the response to get all file paths
        data = response.json()
        github_files = set()
        
        for item in data.get("tree", []):
            if item.get("type") == "blob":  # Only include files, not directories
                github_files.add(item.get("path"))
        
        logger.info(f"Found {len(github_files)} files in GitHub repository")
        return github_files
    
    def get_local_files(self) -> Set[str]:
        """
        Get a set of all files in the local repository.
        
        Returns:
            Set of file paths in the local repository
        """
        logger.info(f"Scanning local repository: {self.egos_root}")
        
        local_files = set()
        
        for root, _, files in os.walk(self.egos_root):
            # Skip .git directory
            if ".git" in Path(root).parts:
                continue
                
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.egos_root)
                local_files.add(str(rel_path).replace("\\", "/"))  # Normalize path separators
        
        logger.info(f"Found {len(local_files)} files in local repository")
        return local_files
    
    def identify_missing_files(self) -> List[str]:
        """
        Identify files that exist in the GitHub repository but are missing from the local repository.
        
        Returns:
            List of missing file paths
        """
        github_files = self.get_github_files()
        local_files = self.get_local_files()
        
        missing_files = list(github_files - local_files)
        missing_files.sort()  # Sort for consistent output
        
        logger.info(f"Identified {len(missing_files)} files missing from local repository")
        return missing_files
    
    def download_file(self, file_path: str) -> bool:
        """
        Download a file from GitHub to the local repository.
        
        Args:
            file_path: Path to the file in the repository
            
        Returns:
            True if the file was downloaded successfully, False otherwise
        """
        # Create the URL for the raw file content
        url = f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{file_path}"
        
        # Create the local file path
        local_path = self.egos_root / file_path
        
        # Create the directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download the file
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Failed to download file {file_path}: {response.status_code} {response.reason}")
                return False
            
            # Write the file to disk
            with open(local_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Downloaded file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            return False
    
    def restore_missing_files(self, filter_prefix: str = None) -> Dict[str, Any]:
        """
        Restore files that exist in the GitHub repository but are missing from the local repository.
        
        Args:
            filter_prefix: Optional prefix to filter files by (e.g., "scripts/cross_reference")
            
        Returns:
            Dictionary with restoration results
        """
        missing_files = self.identify_missing_files()
        
        # Filter files by prefix if specified
        if filter_prefix:
            missing_files = [f for f in missing_files if f.startswith(filter_prefix)]
            logger.info(f"Filtered to {len(missing_files)} files with prefix: {filter_prefix}")
        
        results = {
            "total_missing": len(missing_files),
            "successfully_restored": 0,
            "failed_to_restore": 0,
            "restored_files": [],
            "failed_files": []
        }
        
        for file_path in missing_files:
            if self.download_file(file_path):
                results["successfully_restored"] += 1
                results["restored_files"].append(file_path)
            else:
                results["failed_to_restore"] += 1
                results["failed_files"].append(file_path)
        
        logger.info(f"Restoration complete: {results['successfully_restored']} files restored, {results['failed_to_restore']} files failed")
        return results


def main():
    """Main function to run the Missing Files Restorer."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="EGOS Missing Files Restoration Tool")
    parser.add_argument("--egos-root", type=str, default=CONFIG["EGOS_ROOT"], help="Path to EGOS root directory")
    parser.add_argument("--github-repo", type=str, default=CONFIG["GITHUB_REPO"], help="GitHub repository in the format 'username/repo'")
    parser.add_argument("--github-branch", type=str, default=CONFIG["GITHUB_BRANCH"], help="GitHub branch to compare against")
    parser.add_argument("--filter-prefix", type=str, help="Optional prefix to filter files by (e.g., 'scripts/cross_reference')")
    
    args = parser.parse_args()
    
    restorer = MissingFilesRestorer(
        egos_root=args.egos_root,
        github_repo=args.github_repo,
        github_branch=args.github_branch
    )
    
    print(f"{Fore.GREEN}Identifying missing files...{Style.RESET_ALL}")
    results = restorer.restore_missing_files(filter_prefix=args.filter_prefix)
    
    print(f"\n{Fore.CYAN}Restoration Results:{Style.RESET_ALL}")
    print(f"  Total missing files: {results['total_missing']}")
    print(f"  Successfully restored: {results['successfully_restored']}")
    print(f"  Failed to restore: {results['failed_to_restore']}")
    
    if results['restored_files']:
        print(f"\n{Fore.GREEN}Restored Files:{Style.RESET_ALL}")
        for file in results['restored_files'][:10]:  # Show first 10 files
            print(f"  - {file}")
        if len(results['restored_files']) > 10:
            print(f"  ... and {len(results['restored_files']) - 10} more files")
    
    if results['failed_files']:
        print(f"\n{Fore.RED}Failed Files:{Style.RESET_ALL}")
        for file in results['failed_files']:
            print(f"  - {file}")
    
    print(f"\n{Fore.CYAN}EGOS Missing Files Restoration Tool completed!{Style.RESET_ALL}")
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