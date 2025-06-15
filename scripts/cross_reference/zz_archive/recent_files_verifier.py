#!/usr/bin/env python
"""EGOS Recent Files Cross-Reference Verifier
==========================================

Identifies files modified within a specified time window and verifies
their cross-reference status using the documentation_reference_manager.

This script implements the principle of Evolutionary Preservation by ensuring
that recently modified files maintain proper cross-references to the rest
of the documentation ecosystem.

Usage:
    python recent_files_verifier.py --base-path <path> [options]

For detailed help:
    python recent_files_verifier.py --help

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - subsystems/AutoCrossRef/CROSSREF_STANDARD.md

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Import from documentation_reference_manager package
try:
    from cross_reference.documentation_reference_manager.manager import CrossReferenceManager
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from cross_reference.documentation_reference_manager.manager import CrossReferenceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RecentFilesVerifier:
    """Verifies cross-reference status of recently modified files.
    
    This class identifies files modified within a specified time window
    and verifies their cross-reference status using the CrossReferenceManager.
    
    Attributes:
        base_path: Base path of the EGOS project
        hours: Time window in hours for considering files as "recent"
        extensions: File extensions to include
        exclude_dirs: Directories to exclude from scanning
        min_references: Minimum number of references expected per file
        cross_ref_manager: Instance of CrossReferenceManager
    """
    
    def __init__(
        self,
        base_path: str,
        hours: int = 48,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        min_references: int = 2
    ):
        """Initialize the RecentFilesVerifier.
        
        Args:
            base_path: Base path of the EGOS project
            hours: Time window in hours for considering files as "recent"
            extensions: File extensions to include (default: ['.md'])
            exclude_dirs: Directories to exclude from scanning
            min_references: Minimum number of references expected per file
        """
        self.base_path = Path(base_path)
        self.hours = hours
        self.extensions = extensions or ['.md']
        self.exclude_dirs = exclude_dirs or ['venv', '.git', 'node_modules', '__pycache__']
        self.min_references = min_references
        
        # Initialize CrossReferenceManager
        self.cross_ref_manager = CrossReferenceManager(base_path, min_references)
        
        # Ensure base path exists
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")
    
    def find_recent_files(self) -> List[Path]:
        """Find files modified within the specified time window.
        
        Returns:
            List of Path objects for recently modified files
        """
        logger.info(f"Finding files modified in the last {self.hours} hours...")
        
        # Calculate cutoff time
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=self.hours)
        cutoff_timestamp = cutoff_time.timestamp()
        
        recent_files = []
        
        # Walk through directory structure
        for root, dirs, files in os.walk(self.base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                # Check if file has one of the target extensions
                if not any(file.endswith(ext) for ext in self.extensions):
                    continue
                
                file_path = Path(root) / file
                
                try:
                    # Get file modification time
                    mod_time = os.path.getmtime(file_path)
                    
                    # Check if file was modified after cutoff time
                    if mod_time >= cutoff_timestamp:
                        recent_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Error checking modification time for {file_path}: {e}")
        
        logger.info(f"Found {len(recent_files)} recently modified files")
        return recent_files
    
    def verify_cross_references(self, recent_files: List[Path]) -> Dict[str, Dict]:
        """Verify cross-reference status of recently modified files.
        
        Args:
            recent_files: List of Path objects for recently modified files
            
        Returns:
            Dictionary with verification results
        """
        logger.info("Verifying cross-reference status...")
        
        # Scan all documentation files
        self.cross_ref_manager.scan_documentation(self.extensions)
        
        # Extract references from all files
        self.cross_ref_manager.extract_references()
        
        # Initialize results
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "time_window_hours": self.hours,
            "total_files_scanned": len(self.cross_ref_manager.doc_paths),
            "recent_files_count": len(recent_files),
            "min_references_expected": self.min_references,
            "files": {}
        }
        
        # Check each recent file
        for file_path in recent_files:
            rel_path = str(file_path.relative_to(self.base_path).as_posix())
            
            # Get references for this file
            references = self.cross_ref_manager.references.get(rel_path, set())
            referenced_by = self.cross_ref_manager.referenced_by.get(rel_path, set())
            
            # Determine status
            status = "ok"
            issues = []
            
            if len(references) < self.min_references:
                status = "warning"
                issues.append(f"Has fewer than {self.min_references} outgoing references ({len(references)} found)")
            
            if len(referenced_by) == 0:
                status = "warning"
                issues.append("Not referenced by any other document")
            
            # Add to results
            results["files"][rel_path] = {
                "status": status,
                "issues": issues,
                "outgoing_references_count": len(references),
                "incoming_references_count": len(referenced_by),
                "outgoing_references": list(references),
                "incoming_references": list(referenced_by),
                "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
        
        # Add summary statistics
        results["summary"] = {
            "files_with_issues": sum(1 for f in results["files"].values() if f["status"] != "ok"),
            "files_without_issues": sum(1 for f in results["files"].values() if f["status"] == "ok"),
            "files_without_outgoing_references": sum(1 for f in results["files"].values() if f["outgoing_references_count"] == 0),
            "files_without_incoming_references": sum(1 for f in results["files"].values() if f["incoming_references_count"] == 0)
        }
        
        return results
    
    def generate_report(self, results: Dict, report_dir: str) -> Tuple[str, str]:
        """Generate JSON and Markdown reports for verification results.
        
        Args:
            results: Verification results dictionary
            report_dir: Directory to save reports
            
        Returns:
            Tuple of (json_report_path, markdown_report_path)
        """
        # Create report directory if it doesn't exist
        report_path = Path(report_dir)
        report_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Save JSON report
        json_report_path = report_path / f"recent_files_report_{timestamp}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Generate Markdown report
        markdown_report_path = report_path / f"recent_files_report_{timestamp}.md"
        
        with open(markdown_report_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Recent Files Cross-Reference Report\n\n")
            f.write(f"Generated: {results['timestamp']}\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Time window: {results['time_window_hours']} hours\n")
            f.write(f"- Total files scanned: {results['total_files_scanned']}\n")
            f.write(f"- Recently modified files: {results['recent_files_count']}\n")
            f.write(f"- Files with issues: {results['summary']['files_with_issues']}\n")
            f.write(f"- Files without issues: {results['summary']['files_without_issues']}\n\n")
            
            # Write files with issues
            f.write("## Files Needing Attention\n\n")
            
            files_with_issues = {path: info for path, info in results["files"].items() if info["status"] != "ok"}
            
            if files_with_issues:
                f.write("| File | Issues | Outgoing Refs | Incoming Refs |\n")
                f.write("|------|--------|--------------|---------------|\n")
                
                for path, info in files_with_issues.items():
                    issues_text = "<br>".join(info["issues"])
                    f.write(f"| `{path}` | {issues_text} | {info['outgoing_references_count']} | {info['incoming_references_count']} |\n")
            else:
                f.write("No files with issues found. Great job! 🎉\n\n")
            
            # Write detailed information
            f.write("\n## All Recently Modified Files\n\n")
            f.write("| File | Status | Outgoing Refs | Incoming Refs | Last Modified |\n")
            f.write("|------|--------|--------------|---------------|---------------|\n")
            
            for path, info in results["files"].items():
                status_emoji = "✅" if info["status"] == "ok" else "⚠️"
                f.write(f"| `{path}` | {status_emoji} | {info['outgoing_references_count']} | {info['incoming_references_count']} | {info['last_modified']} |\n")
            
            # Write footer with reference to JSON report
            f.write(f"\n\n---\n\nDetailed information available in the JSON report: `{json_report_path.name}`\n")
        
        logger.info(f"JSON report saved to: {json_report_path}")
        logger.info(f"Markdown report saved to: {markdown_report_path}")
        
        return str(json_report_path), str(markdown_report_path)


def main():
    """Main entry point for the recent files verifier."""
    parser = argparse.ArgumentParser(
        description="Verify cross-reference status of recently modified files"
    )
    parser.add_argument(
        "--base-path", "-b", default=".",
        help="Base path of the EGOS project (default: current directory)"
    )
    parser.add_argument(
        "--hours", "-t", type=int, default=48,
        help="Time window in hours for considering files as 'recent' (default: 48)"
    )
    parser.add_argument(
        "--extensions", "-e", nargs="+", default=[".md"],
        help="File extensions to include (default: .md)"
    )
    parser.add_argument(
        "--exclude-dirs", "-x", nargs="+", default=["venv", ".git", "node_modules", "__pycache__"],
        help="Directories to exclude from scanning"
    )
    parser.add_argument(
        "--min-references", "-m", type=int, default=2,
        help="Minimum number of references expected per file (default: 2)"
    )
    parser.add_argument(
        "--report-dir", "-r", default="reports/documentation/recent_files",
        help="Directory to save reports (default: reports/documentation/recent_files)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create verifier instance
        verifier = RecentFilesVerifier(
            args.base_path,
            args.hours,
            args.extensions,
            args.exclude_dirs,
            args.min_references
        )
        
        # Find recent files
        recent_files = verifier.find_recent_files()
        
        if not recent_files:
            logger.info(f"No files modified in the last {args.hours} hours were found.")
            return 0
        
        # Verify cross-references
        results = verifier.verify_cross_references(recent_files)
        
        # Generate reports
        report_dir = os.path.join(args.base_path, args.report_dir)
        json_report, markdown_report = verifier.generate_report(results, report_dir)
        
        # Print summary
        files_with_issues = results["summary"]["files_with_issues"]
        if files_with_issues > 0:
            logger.warning(f"{files_with_issues} recently modified files need attention. See the report for details.")
        else:
            logger.info("All recently modified files have proper cross-references. Great job!")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())