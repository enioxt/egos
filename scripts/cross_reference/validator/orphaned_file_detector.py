#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orphaned File Detector for Cross-Reference Validator

This module implements the orphaned file detection algorithm for the EGOS Cross-Reference System.
It identifies files that lack incoming references from other parts of the system, helping to
maintain documentation integrity and prevent knowledge silos.

@references:
- 🔗 Reference: [ROADMAP.md](../../../ROADMAP.md#cross-reference-tools-enhancement)
- 🔗 Reference: [WORK_2025_05_21.md](../../../WORK_2025_05_21.md#parallel-work-cross-reference-system-advancement)
- 🔗 Reference: [cross_reference_validator.md](../../../docs_egos/08_tooling_and_scripts/reference_implementations/cross_reference_validator.md)
- 🔗 Reference: [file_reference_checker_ultra.py](../../cross_reference/file_reference_checker_ultra.py)
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md

Created: 2025-05-21
Author: EGOS Team
Version: 1.0.0"""
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
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time
from tqdm import tqdm

# Import shared utilities
sys.path.append(str(Path(__file__).parent.parent))
from utils.serialization import (
    EGOSJSONEncoder,
    serialize_to_json,
    save_json_file,
    load_json_file,
    format_colored,
    COLORS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("orphaned_file_detector")

# ANSI color codes are now imported from utils.serialization

# Banner for script start
BANNER = f"""
{COLORS['CYAN']}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  {COLORS['BOLD']}EGOS Cross-Reference System - Orphaned File Detector{COLORS['RESET']}{COLORS['CYAN']}         ║
║                                                                  ║
║  Identifies files without incoming references                    ║
║  Part of the EGOS Cross-Reference Validator                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{COLORS['RESET']}
"""

@dataclass
class FileReference:
    """Represents a reference from one file to another."""
    source_file: Path
    target_file: Path
    line_number: int
    context: str = ""
    valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string paths for JSON serialization."""
        return {
            "source_file": str(self.source_file),
            "target_file": str(self.target_file),
            "line_number": self.line_number,
            "context": self.context,
            "valid": self.valid
        }

@dataclass
class OrphanedFile:
    """Represents a file with no incoming references."""
    file_path: Path
    file_type: str
    last_modified: float
    size: int
    outgoing_references: int = 0
    priority: str = "low"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with string paths for JSON serialization."""
        return {
            "file_path": str(self.file_path),
            "file_type": self.file_type,
            "last_modified": self.last_modified,
            "last_modified_date": time.strftime('%Y-%m-%d %H:%M:%S', 
                                               time.localtime(self.last_modified)),
            "size": self.size,
            "outgoing_references": self.outgoing_references,
            "priority": self.priority
        }

@dataclass
class OrphanedFileReport:
    """Report containing orphaned files and analysis."""
    orphaned_files: List[OrphanedFile] = field(default_factory=list)
    total_files_scanned: int = 0
    total_orphaned_files: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "orphaned_files": [f.to_dict() for f in self.orphaned_files],
            "total_files_scanned": self.total_files_scanned,
            "total_orphaned_files": self.total_orphaned_files,
            "high_priority_count": self.high_priority_count,
            "medium_priority_count": self.medium_priority_count,
            "low_priority_count": self.low_priority_count,
            "execution_time": self.execution_time
        }
    
    def sort_by_priority(self) -> None:
        """Sort orphaned files by priority and then by last modified date."""
        priority_map = {"high": 0, "medium": 1, "low": 2}
        self.orphaned_files.sort(
            key=lambda x: (priority_map[x.priority], -x.last_modified)
        )


# Using EGOSJSONEncoder from utils.serialization instead of a local PathEncoder class


class OrphanedFileDetector:
    """
    Detects orphaned files in the codebase by analyzing reference patterns.
    
    An orphaned file is one that has no incoming references from other files,
    making it potentially disconnected from the documentation ecosystem.
    """
    
    def __init__(
        self,
        base_dir: Path,
        exclude_patterns: List[str] = None,
        include_extensions: List[str] = None,
        reference_data_path: Optional[Path] = None,
        min_age_days: int = 0,
        batch_size: int = 100,
        max_workers: int = None
    ):
        """
        Initialize the orphaned file detector.
        
        Args:
            base_dir: Base directory to scan for orphaned files
            exclude_patterns: List of glob patterns to exclude
            include_extensions: List of file extensions to include
            reference_data_path: Path to existing reference data (if available)
            min_age_days: Minimum age in days for files to be considered
            batch_size: Number of files to process in each batch
            max_workers: Maximum number of worker threads
        """
        self.base_dir = Path(base_dir).resolve()
        self.exclude_patterns = exclude_patterns or []
        self.include_extensions = include_extensions or [".md", ".py", ".txt", ".rst"]
        self.reference_data_path = reference_data_path
        self.min_age_days = min_age_days
        self.batch_size = batch_size
        self.max_workers = max_workers or os.cpu_count()
        
        # Internal state
        self.all_files: Set[Path] = set()
        self.references: List[FileReference] = []
        self.incoming_references: Dict[Path, List[FileReference]] = {}
        self.outgoing_references: Dict[Path, List[FileReference]] = {}
        
        # Expected standalone files (no incoming references expected)
        self.standalone_patterns = [
            "README.md",
            "LICENSE",
            ".gitignore",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "CHANGELOG.md"
        ]
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Check if a file should be excluded based on patterns."""
        # Check if file matches any exclude pattern
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        # Check if file extension is not in included extensions
        if self.include_extensions and file_path.suffix.lower() not in self.include_extensions:
            return True
            
        return False
    
    def _is_expected_standalone(self, file_path: Path) -> bool:
        """Check if a file is expected to be standalone (no incoming references)."""
        for pattern in self.standalone_patterns:
            if file_path.name == pattern:
                return True
        return False
    
    async def discover_files(self) -> None:
        """Discover all files in the base directory."""
        logger.info(f"Discovering files in {self.base_dir}...")
        
        discovered_files = set()
        
        for root, _, files in os.walk(self.base_dir):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(self.base_dir)
                
                # Skip excluded files
                if self._is_excluded(rel_path):
                    continue
                
                discovered_files.add(file_path)
        
        self.all_files = discovered_files
        logger.info(f"Discovered {len(self.all_files)} files")
    
    def _load_reference_data(self) -> bool:
        """Load existing reference data if available."""
        if not self.reference_data_path or not self.reference_data_path.exists():
            return False
        
        try:
            logger.info(f"Loading reference data from {self.reference_data_path}...")
            with open(self.reference_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert dictionary data back to FileReference objects
            self.references = []
            for ref_data in data.get('references', []):
                ref = FileReference(
                    source_file=Path(ref_data['source_file']),
                    target_file=Path(ref_data['target_file']),
                    line_number=ref_data['line_number'],
                    context=ref_data.get('context', ''),
                    valid=ref_data.get('valid', True)
                )
                self.references.append(ref)
            
            logger.info(f"Loaded {len(self.references)} references")
            return True
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
            return False
    
    def _process_references(self) -> None:
        """Process references to build incoming and outgoing reference maps."""
        # Initialize reference maps
        self.incoming_references = {file: [] for file in self.all_files}
        self.outgoing_references = {file: [] for file in self.all_files}
        
        # Process each reference
        for ref in self.references:
            # Handle outgoing references
            if ref.source_file in self.outgoing_references:
                self.outgoing_references[ref.source_file].append(ref)
            
            # Handle incoming references
            if ref.target_file in self.incoming_references:
                self.incoming_references[ref.target_file].append(ref)
    
    def _calculate_priority(self, file: Path, last_modified: float, outgoing_count: int) -> str:
        """
        Calculate priority of an orphaned file based on:
        1. How recently it was modified
        2. Whether it has outgoing references
        3. File type and location
        """
        # Calculate file age in days
        age_days = (time.time() - last_modified) / (60 * 60 * 24)
        
        # Recently modified files with outgoing references are high priority
        if age_days < 30 and outgoing_count > 0:
            return "high"
        
        # Files in important directories are medium priority
        important_dirs = ["docs", "docs_egos", "subsystems"]
        for important_dir in important_dirs:
            if str(file).find(f"/{important_dir}/") >= 0 or str(file).find(f"\\{important_dir}\\") >= 0:
                return "medium"
        
        # Recently modified files are medium priority
        if age_days < 60:
            return "medium"
        
        # Everything else is low priority
        return "low"
    
    async def detect_orphaned_files(self) -> OrphanedFileReport:
        """
        Detect orphaned files in the codebase.
        
        Returns:
            OrphanedFileReport: Report containing orphaned files and analysis
        """
        start_time = time.time()
        
        # Discover files if not already done
        if not self.all_files:
            await self.discover_files()
        
        # Load reference data or generate it
        if not self._load_reference_data():
            logger.warning("Reference data not available. Please run file_reference_checker_ultra.py first.")
            return OrphanedFileReport(
                total_files_scanned=len(self.all_files),
                execution_time=time.time() - start_time
            )
        
        # Process references
        self._process_references()
        
        # Find orphaned files
        orphaned_files = []
        min_timestamp = time.time() - (self.min_age_days * 24 * 60 * 60)
        
        logger.info("Detecting orphaned files...")
        for file in tqdm(self.all_files, desc="Analyzing files"):
            # Skip files that are expected to be standalone
            if self._is_expected_standalone(file):
                continue
            
            # Check if file has incoming references
            if not self.incoming_references[file]:
                # Get file metadata
                stat = file.stat()
                last_modified = stat.st_mtime
                
                # Skip files that are too new
                if last_modified > min_timestamp:
                    continue
                
                # Count outgoing references
                outgoing_count = len(self.outgoing_references.get(file, []))
                
                # Calculate priority
                priority = self._calculate_priority(file, last_modified, outgoing_count)
                
                # Create orphaned file record
                orphaned_file = OrphanedFile(
                    file_path=file,
                    file_type=file.suffix.lower(),
                    last_modified=last_modified,
                    size=stat.st_size,
                    outgoing_references=outgoing_count,
                    priority=priority
                )
                
                orphaned_files.append(orphaned_file)
        
        # Create report
        report = OrphanedFileReport(
            orphaned_files=orphaned_files,
            total_files_scanned=len(self.all_files),
            total_orphaned_files=len(orphaned_files),
            high_priority_count=sum(1 for f in orphaned_files if f.priority == "high"),
            medium_priority_count=sum(1 for f in orphaned_files if f.priority == "medium"),
            low_priority_count=sum(1 for f in orphaned_files if f.priority == "low"),
            execution_time=time.time() - start_time
        )
        
        # Sort orphaned files by priority
        report.sort_by_priority()
        
        return report
    
    def save_report(self, report: OrphanedFileReport, output_path: Path) -> None:
        """
        Save the orphaned file report to a file.
        
        Args:
            report: The orphaned file report
            output_path: Path to save the report
        """
        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON report
            if output_path.suffix.lower() == '.json':
                save_json_file(report.to_dict(), output_path)
                logger.info(f"Saved JSON report to {output_path}")
            # Save Markdown report
            elif output_path.suffix.lower() in ('.md', '.markdown'):
                self._save_markdown_report(report, output_path)
                logger.info(f"Saved Markdown report to {output_path}")
            else:
                # Default to JSON if extension not recognized
                json_path = output_path.with_suffix('.json')
                save_json_file(report.to_dict(), json_path)
                logger.info(f"Saved JSON report to {json_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def _save_markdown_report(self, report: OrphanedFileReport, output_path: Path) -> None:
        """Save the report in Markdown format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Orphaned Files Report\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Files Scanned**: {report.total_files_scanned}\n")
            f.write(f"- **Orphaned Files**: {report.total_orphaned_files}\n")
            f.write(f"- **High Priority**: {report.high_priority_count}\n")
            f.write(f"- **Medium Priority**: {report.medium_priority_count}\n")
            f.write(f"- **Low Priority**: {report.low_priority_count}\n")
            f.write(f"- **Execution Time**: {report.execution_time:.2f} seconds\n\n")
            
            # High Priority Files
            if report.high_priority_count > 0:
                f.write("## High Priority Orphaned Files\n\n")
                f.write("| File | Last Modified | Outgoing References |\n")
                f.write("|------|--------------|---------------------|\n")
                for orphan in report.orphaned_files:
                    if orphan.priority == "high":
                        last_modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                     time.localtime(orphan.last_modified))
                        f.write(f"| {orphan.file_path} | {last_modified} | {orphan.outgoing_references} |\n")
                f.write("\n")
            
            # Medium Priority Files
            if report.medium_priority_count > 0:
                f.write("## Medium Priority Orphaned Files\n\n")
                f.write("| File | Last Modified | Outgoing References |\n")
                f.write("|------|--------------|---------------------|\n")
                for orphan in report.orphaned_files:
                    if orphan.priority == "medium":
                        last_modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                     time.localtime(orphan.last_modified))
                        f.write(f"| {orphan.file_path} | {last_modified} | {orphan.outgoing_references} |\n")
                f.write("\n")
            
            # Low Priority Files
            if report.low_priority_count > 0:
                f.write("## Low Priority Orphaned Files\n\n")
                f.write("| File | Last Modified | Outgoing References |\n")
                f.write("|------|--------------|---------------------|\n")
                for orphan in report.orphaned_files:
                    if orphan.priority == "low":
                        last_modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                     time.localtime(orphan.last_modified))
                        f.write(f"| {orphan.file_path} | {last_modified} | {orphan.outgoing_references} |\n")
                f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. **High Priority Files**: Review and add references to these files immediately\n")
            f.write("2. **Medium Priority Files**: Schedule review in the next sprint\n")
            f.write("3. **Low Priority Files**: Consider archiving if no longer needed\n\n")
            
            f.write("✧༺❀༻∞ EGOS ∞༺❀༻✧\n")


async def main():
    """Main entry point for the script."""
    print(BANNER)
    
    parser = argparse.ArgumentParser(description="EGOS Orphaned File Detector")
    parser.add_argument("--base-dir", type=str, default=".", 
                        help="Base directory to scan for orphaned files")
    parser.add_argument("--exclude", type=str, nargs="+", default=["**/venv/**", "**/.git/**"],
                        help="Glob patterns to exclude")
    parser.add_argument("--include-ext", type=str, nargs="+", default=[".md", ".py", ".txt", ".rst"],
                        help="File extensions to include")
    parser.add_argument("--reference-data", type=str, 
                        help="Path to existing reference data JSON file")
    parser.add_argument("--min-age-days", type=int, default=7,
                        help="Minimum age in days for files to be considered")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="Number of files to process in each batch")
    parser.add_argument("--max-workers", type=int, default=None,
                        help="Maximum number of worker threads")
    parser.add_argument("--output", type=str, default="orphaned_files_report.json",
                        help="Output file path for the report")
    parser.add_argument("--format", type=str, choices=["json", "md"], default=None,
                        help="Output format (default: based on file extension)")
    
    args = parser.parse_args()
    
    # Determine output format and path
    output_path = Path(args.output)
    if args.format:
        output_path = output_path.with_suffix(f".{args.format}")
    
    # Create detector
    detector = OrphanedFileDetector(
        base_dir=args.base_dir,
        exclude_patterns=args.exclude,
        include_extensions=args.include_ext,
        reference_data_path=Path(args.reference_data) if args.reference_data else None,
        min_age_days=args.min_age_days,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )
    
    # Detect orphaned files
    report = await detector.detect_orphaned_files()
    
    # Print summary
    print(f"\n{COLORS['CYAN']}Orphaned Files Summary:{COLORS['RESET']}")
    print(f"  Total Files Scanned: {report.total_files_scanned}")
    print(f"  Orphaned Files: {report.total_orphaned_files}")
    print(f"  High Priority: {COLORS['RED']}{report.high_priority_count}{COLORS['RESET']}")
    print(f"  Medium Priority: {COLORS['YELLOW']}{report.medium_priority_count}{COLORS['RESET']}")
    print(f"  Low Priority: {COLORS['GREEN']}{report.low_priority_count}{COLORS['RESET']}")
    print(f"  Execution Time: {report.execution_time:.2f} seconds")
    
    # Save report
    detector.save_report(report, output_path)
    
    # Print recommendations
    if report.total_orphaned_files > 0:
        print(f"\n{COLORS['CYAN']}Recommendations:{COLORS['RESET']}")
        print(f"  1. Review high priority orphaned files immediately")
        print(f"  2. Schedule review of medium priority files in the next sprint")
        print(f"  3. Consider archiving low priority files if no longer needed")
        print(f"\nSee the full report at: {output_path}")
    else:
        print(f"\n{COLORS['GREEN']}No orphaned files detected!{COLORS['RESET']}")


if __name__ == "__main__":
    asyncio.run(main())