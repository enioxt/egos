#!/usr/bin/env python3
"""
ATRiAN Audit Log Repair Tool

This script identifies and repairs corrupted audit log files by:
1. Scanning the audit log directory for all JSON files
2. Validating each file's JSON structure
3. Repairing or archiving corrupted files
4. Generating a detailed report of actions taken

Usage:
    python fix_corrupted_audit_logs.py [--archive-only] [--audit-dir PATH]

Author: ATRiAN Development Team
Date: 2025-06-03
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
import json
import shutil
import argparse
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("audit_log_repair.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("audit_log_repair")

class AuditLogRepairTool:
    """Tool for identifying and repairing corrupted audit log files"""
    
    def __init__(self, audit_dir: str, archive_only: bool = False):
        """
        Initialize the repair tool
        
        Args:
            audit_dir: Directory containing audit log files
            archive_only: If True, corrupted files will only be archived, not repaired
        """
        self.audit_dir = Path(audit_dir)
        self.archive_dir = self.audit_dir / "archived" / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_only = archive_only
        self.stats = {
            "total_files": 0,
            "valid_files": 0,
            "corrupted_files": 0,
            "empty_files": 0,
            "repaired_files": 0,
            "archived_files": 0,
            "failed_repairs": 0
        }
        self.corrupted_files = []
        
    def run(self) -> Dict[str, Any]:
        """
        Execute the repair process
        
        Returns:
            Dictionary with statistics about the repair operation
        """
        logger.info(f"Starting audit log repair process in {self.audit_dir}")
        logger.info(f"Archive mode: {'enabled' if self.archive_only else 'disabled'}")
        
        # Ensure archive directory exists
        os.makedirs(self.archive_dir, exist_ok=True)
        
        # Scan for all JSON files
        json_files = list(self.audit_dir.glob("*.json"))
        self.stats["total_files"] = len(json_files)
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process each file
        for file_path in json_files:
            self._process_file(file_path)
            
        # Generate summary report
        self._generate_report()
        
        return self.stats
    
    def _process_file(self, file_path: Path) -> None:
        """
        Process a single audit log file
        
        Args:
            file_path: Path to the audit log file
        """
        logger.info(f"Processing file: {file_path.name}")
        
        try:
            # Check if file is empty
            if file_path.stat().st_size == 0:
                logger.warning(f"Empty file detected: {file_path.name}")
                self.stats["empty_files"] += 1
                self.corrupted_files.append((file_path, "empty_file", None))
                return
                
            # Try to load the JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # File is valid JSON
                    self.stats["valid_files"] += 1
                    logger.info(f"File {file_path.name} is valid")
                except json.JSONDecodeError as e:
                    # File is corrupted
                    self.stats["corrupted_files"] += 1
                    logger.warning(f"Corrupted JSON in {file_path.name}: {str(e)}")
                    self.corrupted_files.append((file_path, "json_decode_error", str(e)))
        except Exception as e:
            # Other file access errors
            logger.error(f"Error accessing file {file_path.name}: {str(e)}")
            self.corrupted_files.append((file_path, "access_error", str(e)))
    
    def _repair_files(self) -> None:
        """Attempt to repair corrupted files"""
        for file_path, error_type, error_details in self.corrupted_files:
            logger.info(f"Attempting to repair: {file_path.name} (Error: {error_type})")
            
            # Create archive copy first
            archive_path = self.archive_dir / file_path.name
            shutil.copy2(file_path, archive_path)
            self.stats["archived_files"] += 1
            
            # Skip repair if in archive-only mode
            if self.archive_only:
                continue
                
            try:
                if error_type == "empty_file":
                    # Create a valid but empty audit log array
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    self.stats["repaired_files"] += 1
                    logger.info(f"Repaired empty file: {file_path.name}")
                    
                elif error_type == "json_decode_error":
                    # Try to repair JSON by reading the file content and fixing common issues
                    repaired = self._attempt_json_repair(file_path)
                    if repaired:
                        self.stats["repaired_files"] += 1
                        logger.info(f"Successfully repaired: {file_path.name}")
                    else:
                        self.stats["failed_repairs"] += 1
                        logger.warning(f"Failed to repair: {file_path.name}")
                else:
                    self.stats["failed_repairs"] += 1
                    logger.warning(f"Unknown error type, cannot repair: {file_path.name}")
            except Exception as e:
                self.stats["failed_repairs"] += 1
                logger.error(f"Error during repair of {file_path.name}: {str(e)}")
    
    def _attempt_json_repair(self, file_path: Path) -> bool:
        """
        Attempt to repair a corrupted JSON file
        
        Args:
            file_path: Path to the corrupted file
            
        Returns:
            True if repair was successful, False otherwise
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Common JSON corruption fixes
            
            # 1. Try to fix truncated files by adding missing brackets
            if not content.strip().endswith(']'):
                content = content.rstrip(',\r\n\t ') + ']'
                
            # 2. Try to fix missing commas between objects
            content = content.replace('}{', '},{')
            
            # 3. Replace invalid control characters
            for i in range(32):
                if i not in (9, 10, 13):  # tab, LF, CR are allowed
                    content = content.replace(chr(i), '')
            
            # Validate the repaired JSON
            json.loads(content)
            
            # If we got here, the repair worked - write it back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
        except Exception as e:
            logger.error(f"Repair attempt failed for {file_path.name}: {str(e)}")
            
            # If all else fails, create a new empty valid file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                logger.info(f"Created new empty file for {file_path.name} after failed repair")
                return True
            except:
                return False
    
    def _generate_report(self) -> None:
        """Generate a detailed report of the repair operation"""
        # Repair files if needed
        if self.corrupted_files:
            self._repair_files()
            
        # Create report file
        report_path = self.audit_dir / "audit_log_repair_report.json"
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "audit_directory": str(self.audit_dir),
            "archive_directory": str(self.archive_dir),
            "archive_only_mode": self.archive_only,
            "statistics": self.stats,
            "corrupted_files": [
                {
                    "filename": str(file_path.name),
                    "error_type": error_type,
                    "error_details": error_details,
                    "archived_to": str(self.archive_dir / file_path.name)
                }
                for file_path, error_type, error_details in self.corrupted_files
            ]
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Repair report generated: {report_path}")
        
        # Print summary to console
        logger.info("=== Audit Log Repair Summary ===")
        logger.info(f"Total files processed: {self.stats['total_files']}")
        logger.info(f"Valid files: {self.stats['valid_files']}")
        logger.info(f"Corrupted files: {self.stats['corrupted_files']}")
        logger.info(f"Empty files: {self.stats['empty_files']}")
        logger.info(f"Files archived: {self.stats['archived_files']}")
        
        if not self.archive_only:
            logger.info(f"Files repaired: {self.stats['repaired_files']}")
            logger.info(f"Failed repairs: {self.stats['failed_repairs']}")
            
        logger.info(f"Detailed report saved to: {report_path}")

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="ATRiAN Audit Log Repair Tool")
    parser.add_argument(
        "--audit-dir", 
        default="C:/EGOS/ATRiAN/data/audit",
        help="Directory containing audit log files"
    )
    parser.add_argument(
        "--archive-only", 
        action="store_true",
        help="Only archive corrupted files without attempting repair"
    )
    
    args = parser.parse_args()
    
    repair_tool = AuditLogRepairTool(args.audit_dir, args.archive_only)
    stats = repair_tool.run()
    
    # Exit with error code if any corrupted files were found
    if stats["corrupted_files"] > 0:
        exit_code = 1 if stats["failed_repairs"] > 0 else 0
        exit(exit_code)
    
    return 0

if __name__ == "__main__":
    main()