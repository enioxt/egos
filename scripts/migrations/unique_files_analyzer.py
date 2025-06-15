#!/usr/bin/env python3
"""EGOS Unique Files Analyzer

This script analyzes unique files in old documentation directories that were not migrated
to the new structure. It categorizes files by type, analyzes content, and generates
recommendations for each file (migrate, archive, or delete).

**Subsystem:** KOIOS
**Module ID:** KOIOS-MIG-005
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
import mimetypes
import hashlib

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unique_files_analysis.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("unique_files_analyzer")

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROJECT_DOCUMENTATION_DIR = os.path.join(DOCS_DIR, "project_documentation")

# Default old directories to analyze if not specified
DEFAULT_OLD_DIRECTORIES = [
    os.path.join(DOCS_DIR, "reference"),
    os.path.join(DOCS_DIR, "subsystems"),
    os.path.join(DOCS_DIR, "governance"),
    os.path.join(DOCS_DIR, "guides"),
    os.path.join(DOCS_DIR, "templates"),
    os.path.join(DOCS_DIR, "development"),
]

# File categories
FILE_CATEGORIES = {
    "documentation": [".md", ".mdc", ".txt", ".rst"],
    "code": [".py", ".js", ".html", ".css", ".ps1", ".sh", ".bat", ".cmd"],
    "data": [".json", ".yaml", ".yml", ".csv", ".xml", ".toml"],
    "image": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"],
    "binary": [".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".tar", ".gz"],
    "other": []
}

# Recommendation criteria
RECOMMENDATION_CRITERIA = {
    "documentation": {
        "migrate": ["koios", "egos", "standard", "guide", "reference", "architecture"],
        "archive": ["draft", "deprecated", "old", "legacy", "archive"],
        "default": "review"
    },
    "code": {
        "migrate": ["koios", "egos", "util", "tool", "script"],
        "archive": ["deprecated", "old", "legacy", "archive", "test"],
        "default": "review"
    },
    "data": {
        "migrate": ["koios", "egos", "config", "schema"],
        "archive": ["deprecated", "old", "legacy", "archive", "test"],
        "default": "review"
    },
    "image": {
        "migrate": ["koios", "egos", "diagram", "architecture"],
        "archive": ["deprecated", "old", "legacy", "archive"],
        "default": "archive"
    },
    "binary": {
        "migrate": ["koios", "egos", "important"],
        "archive": ["deprecated", "old", "legacy", "archive"],
        "default": "archive"
    },
    "other": {
        "default": "review"
    }
}


class UniqueFilesAnalyzer:
    """
    Analyzes unique files in old documentation directories.
    """

    def __init__(self, root_dir: str = ROOT_DIR, old_dirs: List[str] = None, new_dir: str = None, output_format: str = "markdown"):
        """
        Initialize the analyzer.
        
        Args:
            root_dir: Root directory of the EGOS project
            old_dirs: List of old directories to analyze
            new_dir: New directory structure to compare against
            output_format: Output format for the analysis report (markdown or json)
        """
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        
        # Set old directories to analyze
        if old_dirs:
            self.old_directories = [Path(d) if os.path.isabs(d) else self.root_dir / d for d in old_dirs]
        else:
            self.old_directories = [Path(d) for d in DEFAULT_OLD_DIRECTORIES]
        
        # Set new directory to compare against
        if new_dir:
            self.project_documentation_dir = Path(new_dir) if os.path.isabs(new_dir) else self.root_dir / new_dir
        else:
            self.project_documentation_dir = self.docs_dir / "project_documentation"
            
        self.output_format = output_format
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "by_category": {},
            "by_recommendation": {
                "migrate": 0,
                "archive": 0,
                "delete": 0,
                "review": 0
            },
            "by_directory": {}
        }
        
        # File analysis results
        self.file_analysis = []
        
        # Initialize file categories stats
        for category in FILE_CATEGORIES.keys():
            self.stats["by_category"][category] = 0
    
    def analyze_files(self):
        """
        Analyze unique files in old documentation directories.
        """
        logger.info("Starting unique files analysis...")
        logger.info(f"Old directories: {[str(d) for d in self.old_directories]}")
        logger.info(f"New directory: {self.project_documentation_dir}")
        
        # Process each old directory
        for old_dir_path in self.old_directories:
            if not old_dir_path.exists():
                logger.warning(f"Directory does not exist: {old_dir_path}")
                continue
                
            # Initialize directory stats
            dir_name = old_dir_path.name
            self.stats["by_directory"][dir_name] = 0
            
            # Process all files in the directory
            for file_path in old_dir_path.glob("**/*"):
                if file_path.is_file():
                    self._analyze_file(file_path)
                    self.stats["total_files"] += 1
                    self.stats["by_directory"][dir_name] += 1
        
        # Generate analysis report
        self._generate_report()
        
        logger.info(f"Analysis completed with {self.stats['total_files']} files processed")
    
    def _analyze_file(self, file_path: Path):
        """
        Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
        """
        try:
            # Get file extension and determine category
            extension = file_path.suffix.lower()
            category = self._get_file_category(extension)
            self.stats["by_category"][category] += 1
            
            # Get file metadata
            size_bytes = file_path.stat().st_size
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Get file content for text files
            content_preview = ""
            content_keywords = []
            frontmatter = None
            
            if category in ["documentation", "code", "data"]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(4096)  # Read first 4KB for preview
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        
                        # Extract keywords from content
                        content_keywords = self._extract_keywords(content)
                        
                        # Extract frontmatter if present
                        frontmatter = self._extract_frontmatter(content)
                except UnicodeDecodeError:
                    # Not a text file or not UTF-8 encoded
                    content_preview = "[Binary content]"
            
            # Determine recommendation
            recommendation = self._determine_recommendation(file_path, category, content_keywords, frontmatter)
            self.stats["by_recommendation"][recommendation] += 1
            
            # Add file analysis to results
            self.file_analysis.append({
                "path": str(file_path),
                "name": file_path.name,
                "directory": str(file_path.parent),
                "category": category,
                "extension": extension,
                "size_bytes": size_bytes,
                "modified_time": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content_preview": content_preview,
                "keywords": content_keywords,
                "frontmatter": frontmatter,
                "recommendation": recommendation
            })
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
    
    def _get_file_category(self, extension: str) -> str:
        """
        Determine the category of a file based on its extension.
        
        Args:
            extension: File extension
            
        Returns:
            File category
        """
        for category, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        
        # If no match, check with mimetypes
        mime_type, _ = mimetypes.guess_type(f"file{extension}")
        
        if mime_type:
            if mime_type.startswith("text/"):
                return "documentation"
            elif mime_type.startswith("image/"):
                return "image"
            elif mime_type.startswith("application/"):
                if any(app_type in mime_type for app_type in ["pdf", "msword", "vnd.ms", "zip", "x-tar"]):
                    return "binary"
                else:
                    return "data"
        
        return "other"
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract keywords from file content.
        
        Args:
            content: File content
            
        Returns:
            List of keywords
        """
        # Convert to lowercase and remove special characters
        content = content.lower()
        content = re.sub(r'[^\w\s]', ' ', content)
        
        # Split into words
        words = content.split()
        
        # Count word frequency
        word_count = {}
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10 keywords
        return [word for word, count in sorted_words[:10]]
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict]:
        """
        Extract YAML frontmatter from file content.
        
        Args:
            content: File content
            
        Returns:
            Frontmatter as a dictionary, or None if no frontmatter is present
        """
        # Check if content starts with YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if frontmatter_match:
            try:
                frontmatter_content = frontmatter_match.group(1)
                return yaml.safe_load(frontmatter_content)
            except Exception:
                return None
        
        return None
    
    def _determine_recommendation(self, file_path: Path, category: str, keywords: List[str], frontmatter: Optional[Dict]) -> str:
        """
        Determine recommendation for a file (migrate, archive, delete, or review).
        
        Args:
            file_path: Path to the file
            category: File category
            keywords: Keywords extracted from file content
            frontmatter: Frontmatter extracted from file content
            
        Returns:
            Recommendation (migrate, archive, delete, or review)
        """
        # Check if file is empty
        if file_path.stat().st_size == 0:
            return "delete"
        
        # Check if file is a temporary or backup file
        if re.search(r'(~|\.(bak|tmp|temp|old|swp))$', file_path.name, re.IGNORECASE):
            return "delete"
        
        # Check frontmatter for status
        if frontmatter and "status" in frontmatter:
            status = frontmatter["status"].lower()
            if status in ["deprecated", "archived"]:
                return "archive"
            elif status in ["draft"]:
                return "review"
        
        # Check criteria based on category
        criteria = RECOMMENDATION_CRITERIA.get(category, RECOMMENDATION_CRITERIA["other"])
        
        # Check for migration keywords
        if "migrate" in criteria:
            for keyword in criteria["migrate"]:
                if keyword in file_path.name.lower() or any(keyword in kw for kw in keywords):
                    return "migrate"
        
        # Check for archive keywords
        if "archive" in criteria:
            for keyword in criteria["archive"]:
                if keyword in file_path.name.lower() or any(keyword in kw for kw in keywords):
                    return "archive"
        
        # Return default recommendation
        return criteria.get("default", "review")
    
    def _generate_report(self):
        """
        Generate analysis report.
        """
        if self.output_format == "json":
            self._generate_json_report()
        else:
            self._generate_markdown_report()
    
    def _generate_markdown_report(self):
        """
        Generate analysis report in markdown format.
        """
        report_path = os.path.join(SCRIPT_DIR, "unique_files_analysis_report.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# EGOS Unique Files Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Files:** {self.stats['total_files']}\n\n")
            
            f.write("### Files by Category\n\n")
            for category, count in self.stats["by_category"].items():
                if count > 0:
                    f.write(f"- **{category.capitalize()}:** {count}\n")
            f.write("\n")
            
            f.write("### Files by Recommendation\n\n")
            for recommendation, count in self.stats["by_recommendation"].items():
                if count > 0:
                    f.write(f"- **{recommendation.capitalize()}:** {count}\n")
            f.write("\n")
            
            f.write("### Files by Directory\n\n")
            for directory, count in self.stats["by_directory"].items():
                if count > 0:
                    f.write(f"- **{directory}:** {count}\n")
            f.write("\n")
            
            # Group files by recommendation
            files_by_recommendation = {
                "migrate": [],
                "archive": [],
                "delete": [],
                "review": []
            }
            
            for file_info in self.file_analysis:
                files_by_recommendation[file_info["recommendation"]].append(file_info)
            
            # Output files to migrate
            if files_by_recommendation["migrate"]:
                f.write("## Files to Migrate\n\n")
                f.write("| File | Category | Size | Modified | Keywords |\n")
                f.write("|------|----------|------|----------|----------|\n")
                
                for file_info in sorted(files_by_recommendation["migrate"], key=lambda x: x["path"]):
                    keywords_str = ", ".join(file_info["keywords"][:5]) if file_info["keywords"] else ""
                    size_kb = file_info["size_bytes"] / 1024
                    size_str = f"{size_kb:.1f} KB"
                    
                    f.write(f"| {file_info['path']} | {file_info['category']} | {size_str} | {file_info['modified_time']} | {keywords_str} |\n")
                
                f.write("\n")
            
            # Output files to archive
            if files_by_recommendation["archive"]:
                f.write("## Files to Archive\n\n")
                f.write("| File | Category | Size | Modified | Keywords |\n")
                f.write("|------|----------|------|----------|----------|\n")
                
                for file_info in sorted(files_by_recommendation["archive"], key=lambda x: x["path"]):
                    keywords_str = ", ".join(file_info["keywords"][:5]) if file_info["keywords"] else ""
                    size_kb = file_info["size_bytes"] / 1024
                    size_str = f"{size_kb:.1f} KB"
                    
                    f.write(f"| {file_info['path']} | {file_info['category']} | {size_str} | {file_info['modified_time']} | {keywords_str} |\n")
                
                f.write("\n")
            
            # Output files to delete
            if files_by_recommendation["delete"]:
                f.write("## Files to Delete\n\n")
                f.write("| File | Category | Size | Modified |\n")
                f.write("|------|----------|------|----------|\n")
                
                for file_info in sorted(files_by_recommendation["delete"], key=lambda x: x["path"]):
                    size_kb = file_info["size_bytes"] / 1024
                    size_str = f"{size_kb:.1f} KB"
                    
                    f.write(f"| {file_info['path']} | {file_info['category']} | {size_str} | {file_info['modified_time']} |\n")
                
                f.write("\n")
            
            # Output files to review
            if files_by_recommendation["review"]:
                f.write("## Files to Review\n\n")
                f.write("| File | Category | Size | Modified | Content Preview |\n")
                f.write("|------|----------|------|----------|----------------|\n")
                
                for file_info in sorted(files_by_recommendation["review"], key=lambda x: x["path"]):
                    preview = file_info["content_preview"].replace("\n", " ").replace("|", "\\|")
                    preview = preview[:100] + "..." if len(preview) > 100 else preview
                    size_kb = file_info["size_bytes"] / 1024
                    size_str = f"{size_kb:.1f} KB"
                    
                    f.write(f"| {file_info['path']} | {file_info['category']} | {size_str} | {file_info['modified_time']} | {preview} |\n")
                
                f.write("\n")
            
            f.write("## Recommendations\n\n")
            f.write("1. **Files to Migrate:** These files should be moved to the new documentation structure.\n")
            f.write("2. **Files to Archive:** These files should be moved to an archive directory for historical reference.\n")
            f.write("3. **Files to Delete:** These files are temporary, empty, or no longer needed and can be safely deleted.\n")
            f.write("4. **Files to Review:** These files require manual review to determine their fate.\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review this analysis report and confirm the recommendations.\n")
            f.write("2. Create migration, archiving, and deletion scripts based on the recommendations.\n")
            f.write("3. Execute the scripts to complete the cleanup process.\n")
            f.write("4. Verify the results and update the documentation structure standard if needed.\n")
        
        logger.info(f"Markdown report generated: {report_path}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print("EGOS UNIQUE FILES ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total Files: {self.stats['total_files']}")
        print("\nFiles by Recommendation:")
        for recommendation, count in self.stats["by_recommendation"].items():
            if count > 0:
                print(f"- {recommendation.capitalize()}: {count}")
        print("=" * 80)
        print(f"Detailed report: {report_path}")
        print("=" * 80 + "\n")
    
    def _generate_json_report(self):
        """
        Generate analysis report in JSON format.
        """
        report_path = os.path.join(SCRIPT_DIR, "unique_files_analysis_report.json")
        
        # Convert datetime objects to strings for JSON serialization
        file_analysis = []
        for file_info in self.file_analysis:
            file_info_copy = file_info.copy()
            file_analysis.append(file_info_copy)
        
        report_data = {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": self.stats,
            "files": file_analysis
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"JSON report generated: {report_path}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="EGOS Unique Files Analyzer")
    parser.add_argument(
        "--old-dirs",
        nargs="+",
        help="List of old directories to analyze (relative to root or absolute paths)"
    )
    parser.add_argument(
        "--new-dir",
        help="New directory structure to compare against (relative to root or absolute path)"
    )
    parser.add_argument(
        "--output-format", 
        choices=["markdown", "json"],
        default="markdown",
        help="Output format for the analysis report (default: markdown)"
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
    
    logger.info(f"Starting unique files analysis...")
    logger.info(f"Root directory: {args.root_dir}")
    logger.info(f"Old directories: {args.old_dirs or 'Using defaults'}")
    logger.info(f"New directory: {args.new_dir or 'Using default'}")
    logger.info(f"Output format: {args.output_format}")
    
    analyzer = UniqueFilesAnalyzer(
        root_dir=args.root_dir,
        old_dirs=args.old_dirs,
        new_dir=args.new_dir,
        output_format=args.output_format
    )
    
    try:
        # Analyze files
        analyzer.analyze_files()
        
        logger.info("Analysis completed successfully")
        
        return 0
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())