#!/usr/bin/env python3
"""EGOS Migration Integrity Verification Tool

This script verifies the integrity of migrated files, checking for proper metadata,
broken links, orphaned references, and ensuring overall migration quality.

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-008
**Status:** Active
**Version:** 1.0.0

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import logging
import os
import re
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import concurrent.futures

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migration_integrity.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migration_integrity")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")

# Regex patterns
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
MDC_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(mdc:([^)]+)\)')
REFERENCE_PATTERN = re.compile(r'@references:[\s\S]*?(?=\n---|\n#|\Z)')
YAML_PATTERN = re.compile(r'---\n(.*?)\n---', re.DOTALL)


class MigrationIntegrityVerifier:
    """
    Verifies the integrity of migrated files.
    """

    def __init__(self, root_dir: str = ROOT_DIR, fix_issues: bool = False):
        """
        Initialize the verifier.
        
        Args:
            root_dir: Root directory of the EGOS project
            fix_issues: If True, attempt to fix identified issues
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.project_documentation_dir = self.docs_dir / "project_documentation"
        self.fix_issues = fix_issues
        
        # Statistics
        self.stats = {
            "files_checked": 0,
            "files_with_issues": 0,
            "broken_links": 0,
            "missing_metadata": 0,
            "orphaned_references": 0,
            "fixed_issues": 0,
        }
        
        # Issues tracking
        self.issues = {
            "broken_links": [],
            "missing_metadata": [],
            "orphaned_references": [],
        }
        
        # Map of all files for reference checking
        self.file_map = {}
        
    def verify_integrity(self):
        """
        Verify the integrity of migrated files.
        """
        logger.info("Starting migration integrity verification...")
        
        # Build file map
        self._build_file_map()
        
        # Check all files in the project documentation directory
        for file_path in self.project_documentation_dir.glob("**/*.md"):
            self._check_file(file_path)
        
        # Generate report
        self._generate_report()
        
        logger.info(f"Verification completed with stats: {self.stats}")
        
    def _build_file_map(self):
        """
        Build a map of all markdown files in the project.
        """
        logger.info("Building file map...")
        
        for file_path in self.docs_dir.glob("**/*.md"):
            rel_path = file_path.relative_to(self.docs_dir)
            self.file_map[str(rel_path)] = file_path
            
            # Also add without the .md extension
            rel_path_no_ext = str(rel_path.with_suffix(''))
            self.file_map[rel_path_no_ext] = file_path
        
        logger.info(f"Built file map with {len(self.file_map)} entries")
    
    def _check_file(self, file_path: Path):
        """
        Check a single file for integrity issues.
        
        Args:
            file_path: Path to the file to check
        """
        self.stats["files_checked"] += 1
        file_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML metadata
            yaml_match = YAML_PATTERN.search(content)
            if not yaml_match:
                self.stats["missing_metadata"] += 1
                self.issues["missing_metadata"].append(str(file_path))
                file_issues.append(f"Missing YAML metadata")
            else:
                # Check for required metadata fields
                yaml_content = yaml_match.group(1)
                try:
                    metadata = yaml.safe_load(yaml_content)
                    required_fields = ["title", "version", "status", "date_created", "date_modified", "authors", "description"]
                    missing_fields = [field for field in required_fields if field not in metadata]
                    
                    if missing_fields:
                        self.stats["missing_metadata"] += 1
                        self.issues["missing_metadata"].append(str(file_path))
                        file_issues.append(f"Missing required metadata fields: {', '.join(missing_fields)}")
                except Exception as e:
                    self.stats["missing_metadata"] += 1
                    self.issues["missing_metadata"].append(str(file_path))
                    file_issues.append(f"Invalid YAML metadata: {str(e)}")
            
            # Check for broken links
            links = LINK_PATTERN.findall(content)
            for link_text, link_path in links:
                if link_path.startswith("http://") or link_path.startswith("https://"):
                    # Skip external links for now
                    continue
                
                # Handle relative links
                if link_path.startswith("./") or link_path.startswith("../"):
                    # Convert to absolute path
                    abs_link_path = (file_path.parent / link_path).resolve()
                    if not abs_link_path.exists():
                        self.stats["broken_links"] += 1
                        self.issues["broken_links"].append((str(file_path), link_text, link_path))
                        file_issues.append(f"Broken link: [{link_text}]({link_path})")
                else:
                    # Assume it's relative to the project root
                    abs_link_path = self.root_dir / link_path
                    if not abs_link_path.exists():
                        self.stats["broken_links"] += 1
                        self.issues["broken_links"].append((str(file_path), link_text, link_path))
                        file_issues.append(f"Broken link: [{link_text}]({link_path})")
            
            # Check for broken mdc links
            mdc_links = MDC_LINK_PATTERN.findall(content)
            for link_text, link_path in mdc_links:
                if link_path not in self.file_map:
                    self.stats["broken_links"] += 1
                    self.issues["broken_links"].append((str(file_path), link_text, f"mdc:{link_path}"))
                    file_issues.append(f"Broken mdc link: [{link_text}](mdc:{link_path})")
            
            # Check for orphaned references
            ref_match = REFERENCE_PATTERN.search(content)
            if ref_match:
                ref_content = ref_match.group(0)
                ref_links = LINK_PATTERN.findall(ref_content)
                
                for link_text, link_path in ref_links:
                    if "mdc:" in link_path:
                        # Extract the path from mdc: link
                        mdc_path = link_path.replace("mdc:", "")
                        if mdc_path not in self.file_map:
                            self.stats["orphaned_references"] += 1
                            self.issues["orphaned_references"].append((str(file_path), link_text, link_path))
                            file_issues.append(f"Orphaned reference: [{link_text}]({link_path})")
                    elif link_path.startswith("http://") or link_path.startswith("https://"):
                        # Skip external links
                        continue
                    else:
                        # Handle relative links
                        if link_path.startswith("./") or link_path.startswith("../"):
                            # Convert to absolute path
                            abs_link_path = (file_path.parent / link_path).resolve()
                            if not abs_link_path.exists():
                                self.stats["orphaned_references"] += 1
                                self.issues["orphaned_references"].append((str(file_path), link_text, link_path))
                                file_issues.append(f"Orphaned reference: [{link_text}]({link_path})")
                        else:
                            # Assume it's relative to the project root
                            abs_link_path = self.root_dir / link_path
                            if not abs_link_path.exists():
                                self.stats["orphaned_references"] += 1
                                self.issues["orphaned_references"].append((str(file_path), link_text, link_path))
                                file_issues.append(f"Orphaned reference: [{link_text}]({link_path})")
            
            if file_issues:
                self.stats["files_with_issues"] += 1
                logger.warning(f"Issues in {file_path}:")
                for issue in file_issues:
                    logger.warning(f"  - {issue}")
                
                # Fix issues if requested
                if self.fix_issues:
                    fixed = self._fix_issues(file_path, content, file_issues)
                    if fixed:
                        self.stats["fixed_issues"] += 1
                        
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
    
    def _fix_issues(self, file_path: Path, content: str, issues: List[str]) -> bool:
        """
        Attempt to fix issues in a file.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            issues: List of issues in the file
            
        Returns:
            True if any issues were fixed, False otherwise
        """
        fixed = False
        new_content = content
        
        # Fix missing metadata
        if any(issue.startswith("Missing YAML metadata") for issue in issues):
            # Add basic metadata
            metadata = {
                "title": file_path.stem.replace('_', ' ').title(),
                "version": "1.0.0",
                "status": "Active",
                "date_created": datetime.now().strftime("%Y-%m-%d"),
                "date_modified": datetime.now().strftime("%Y-%m-%d"),
                "authors": ["EGOS Team", "Cascade AI"],
                "description": f"Documentation for {file_path.stem.replace('_', ' ').title()}",
                "file_type": "documentation",
                "scope": "project-specific",
                "primary_entity_type": "documentation",
                "primary_entity_name": file_path.stem.lower(),
                "subsystem": self._guess_subsystem(file_path),
                "tags": [file_path.stem.lower(), "documentation", "egos"],
            }
            
            yaml_str = yaml.dump(metadata, default_flow_style=False)
            new_content = f"---\n{yaml_str}---\n\n{content}"
            fixed = True
        
        # Fix broken links - this is more complex and would require more context
        # For now, we'll just log the broken links and let the user fix them manually
        
        if fixed:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"Fixed issues in {file_path}")
                return True
            except Exception as e:
                logger.error(f"Error fixing issues in {file_path}: {e}")
                return False
        
        return False
    
    def _guess_subsystem(self, file_path: Path) -> str:
        """
        Guess the subsystem for a file based on its path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Guessed subsystem name
        """
        path_str = str(file_path)
        
        subsystems = [
            "KOIOS", "MYCELIUM", "ETHIK", "NEXUS", "ATLAS", 
            "CRONOS", "AETHER", "KARDIA", "HARMONY", "ORACLE",
            "GUARDIAN", "TRUST_WEAVER"
        ]
        
        for subsystem in subsystems:
            if subsystem.lower() in path_str.lower() or subsystem[:3].lower() in path_str.lower():
                return subsystem
        
        # Default to KOIOS for documentation
        return "KOIOS"
    
    def _generate_report(self):
        """
        Generate a verification report.
        """
        report_path = os.path.join(SCRIPT_DIR, "migration_integrity_report.md")
        json_report_path = os.path.join(SCRIPT_DIR, "migration_integrity_report.json")
        
        # Generate JSON report
        json_report = {
            "stats": self.stats,
            "issues": self.issues,
            "timestamp": datetime.now().isoformat(),
        }
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        
        # Generate Markdown report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Migration Integrity Verification Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Files Checked:** {self.stats['files_checked']}\n")
            f.write(f"- **Files with Issues:** {self.stats['files_with_issues']}\n")
            f.write(f"- **Broken Links:** {self.stats['broken_links']}\n")
            f.write(f"- **Missing Metadata:** {self.stats['missing_metadata']}\n")
            f.write(f"- **Orphaned References:** {self.stats['orphaned_references']}\n")
            
            if self.fix_issues:
                f.write(f"- **Issues Fixed:** {self.stats['fixed_issues']}\n")
            
            f.write("\n## Issues\n\n")
            
            if self.issues["broken_links"]:
                f.write("### Broken Links\n\n")
                for file_path, link_text, link_path in self.issues["broken_links"][:20]:  # Limit to 20 for readability
                    f.write(f"- **{file_path}**: [{link_text}]({link_path})\n")
                
                if len(self.issues["broken_links"]) > 20:
                    f.write(f"\n*...and {len(self.issues['broken_links']) - 20} more broken links*\n")
            
            if self.issues["missing_metadata"]:
                f.write("\n### Missing Metadata\n\n")
                for file_path in self.issues["missing_metadata"][:20]:  # Limit to 20 for readability
                    f.write(f"- {file_path}\n")
                
                if len(self.issues["missing_metadata"]) > 20:
                    f.write(f"\n*...and {len(self.issues['missing_metadata']) - 20} more files with missing metadata*\n")
            
            if self.issues["orphaned_references"]:
                f.write("\n### Orphaned References\n\n")
                for file_path, link_text, link_path in self.issues["orphaned_references"][:20]:  # Limit to 20 for readability
                    f.write(f"- **{file_path}**: [{link_text}]({link_path})\n")
                
                if len(self.issues["orphaned_references"]) > 20:
                    f.write(f"\n*...and {len(self.issues['orphaned_references']) - 20} more orphaned references*\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("1. Fix broken links to ensure all documentation is properly connected.\n")
            f.write("2. Add missing metadata to ensure all documentation is properly categorized.\n")
            f.write("3. Update orphaned references to ensure all documentation is properly cross-referenced.\n")
            f.write("4. Run this verification tool again after making changes to ensure all issues are resolved.\n")
        
        logger.info(f"Report generated: {report_path}")
        logger.info(f"JSON report generated: {json_report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS MIGRATION INTEGRITY VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"- Files Checked: {self.stats['files_checked']}")
        print(f"- Files with Issues: {self.stats['files_with_issues']}")
        print(f"- Broken Links: {self.stats['broken_links']}")
        print(f"- Missing Metadata: {self.stats['missing_metadata']}")
        print(f"- Orphaned References: {self.stats['orphaned_references']}")
        
        if self.fix_issues:
            print(f"- Issues Fixed: {self.stats['fixed_issues']}")
        
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print(f"JSON report: {json_report_path}")
        print("=" * 80 + "\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Migration Integrity Verification Tool")
    parser.add_argument(
        "--fix-issues", 
        action="store_true", 
        help="Attempt to fix identified issues"
    )
    parser.add_argument(
        "--root-dir",
        default=ROOT_DIR,
        help=f"Root directory of the EGOS project (default: {ROOT_DIR})"
    )
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()
    
    logger.info(f"Starting migration integrity verification{' (with fixes)' if args.fix_issues else ''}")
    logger.info(f"Root directory: {args.root_dir}")
    
    verifier = MigrationIntegrityVerifier(root_dir=args.root_dir, fix_issues=args.fix_issues)
    
    try:
        # Verify migration integrity
        verifier.verify_integrity()
        
        logger.info("Verification completed successfully")
        logger.info(f"Stats: {verifier.stats}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during verification: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())