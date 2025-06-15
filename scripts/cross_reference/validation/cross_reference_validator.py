#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Cross-Reference Validator

This script validates cross-references across the EGOS ecosystem to ensure they
follow the standardized format and point to valid targets. It analyzes documents,
extracts references, validates their targets, and generates a comprehensive report.

Part of the EGOS Cross-Reference Standardization Initiative.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

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

# Standard library imports
import os
import re
import sys
import time
import json
import logging
import argparse
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Iterator
from functools import partial

# Local imports
try:
    from config_loader import ConfigLoader
except ImportError:
    # Handle the case when running from a different directory
    sys.path.append(str(Path(__file__).parent.absolute()))
    from config_loader import ConfigLoader

# Third-party imports
from tqdm import tqdm
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAVE_COLORAMA = True
except ImportError:
    HAVE_COLORAMA = False
    # Fallback implementation for colorama
    class DummyColorama:
        def __init__(self):
            self.BLUE = self.GREEN = self.RED = self.YELLOW = self.CYAN = self.MAGENTA = self.WHITE = ""
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    class DummyStyle:
        def __init__(self):
            self.RESET_ALL = self.BRIGHT = self.DIM = ""
    
    if not 'Fore' in globals():
        Fore = DummyColorama()
    if not 'Style' in globals():
        Style = DummyStyle()

# Constants
BANNER_WIDTH = 80
VALID_REFERENCE_FORMATS = [
    r'\[([^\]]+)\]\(([^)]+)\)',                   # Markdown link: [text](target)
    r'<crossref>\s*([^<]+)\s*->\s*([^<]+)\s*</crossref>',  # Custom tag: <crossref>text -> target</crossref>
    r'<!-- crossref:\s*([^\s]+)\s*->\s*([^\s]+)\s*-->'     # HTML comment: <!-- crossref: text -> target -->
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("cross_reference_validator")

def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle (if provided)
    if subtitle:
        subtitle_padding = (width - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (width - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (width-2)}╝{Style.RESET_ALL}")

def format_time(seconds: float) -> str:
    """Format time in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

class CrossReferenceValidator:
    """Validates cross-references in documents."""
    
    def __init__(self, base_path: Path, verbose: bool = False, max_workers: int = None):
        """Initialize the validator.
        
        Args:
            base_path: The base path for all references
            verbose: Whether to print verbose output
            max_workers: Maximum number of worker threads for parallel processing
                        If None, uses the default value from ThreadPoolExecutor
        """
        self.base_path = base_path
        self.verbose = verbose
        self.max_workers = max_workers or min(32, os.cpu_count() + 4)  # Default from ThreadPoolExecutor
        self.stats = {
            "files_scanned": 0,
            "references_found": 0,
            "valid_references": 0,
            "invalid_references": 0,
            "files_with_invalid_references": 0,
            "processing_time": 0
        }
        self.invalid_references = []
        self._reference_cache = {}
        self.results = []
        
        # Invalid references
        self.invalid_references = []
    
    def find_files(self) -> List[Path]:
        """Find all files to validate.
        
        Returns:
            List of file paths to validate
        """
        search_path = self.base_path
        
        if self.verbose:
            logger.info(f"Searching for files in {search_path}")
        
        files = []
        for ext in ['.md', '.mdx', '.txt', '.html']:
            if self.verbose:
                logger.info(f"Searching for *{ext} files")
            
            # Use rglob to find all files with the extension
            files.extend(search_path.rglob(f"*{ext}"))
        
        if self.verbose:
            logger.info(f"Found {len(files)} files to validate")
        
        return files
    
    def extract_references(self, file_path: Path) -> List[Tuple[str, str]]:
        """Extract references from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of tuples (reference_text, reference_target)
        """
        references = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Check for crossref blocks
            crossref_blocks = re.findall(r'(?s)<!-- crossref_block:start -->(.*?)<!-- crossref_block:end -->', content)
            for block in crossref_blocks:
                # Extract references from block using regex
                for line in block.strip().split('\n'):
                    # Look for links in the format: - 🔗 Reference: [target](path)
                    matches = re.findall(r'- 🔗 Reference: \[(.*?)\]\((.*?)\)', line)
                    for match in matches:
                        references.append(match)
            
            # Also check for individual markdown links and other formats
            for pattern in VALID_REFERENCE_FORMATS:
                matches = re.findall(pattern, content)
                references.extend(matches)
        
        except Exception as e:
            logger.error(f"Error extracting references from {file_path}: {str(e)}")
        
        if self.verbose:
            logger.info(f"Found {len(references)} references in {file_path}")
        
        return references
    
    def validate_reference(self, reference: Tuple[str, str], source_file: Path) -> Dict[str, Any]:
        """Validate a reference against the canonical format and check if the target exists.
        
        Args:
            reference: Tuple of (text, target)
            source_file: Path to the source file containing the reference
            
        Returns:
            Dictionary with validation results
        """
        # Check cache first to avoid redundant validation
        cache_key = f"{source_file}|{reference[0]}|{reference[1]}"
        if cache_key in self._reference_cache:
            return self._reference_cache[cache_key]
        
        result = {
            "valid": False,
            "text": reference[0],
            "target": reference[1],
            "error": None,
            "format_valid": False,
            "suggested_fix": None
        }
        
        # Check if the target is a URL
        if reference[1].startswith(('http://', 'https://', 'ftp://')):
            # For external URLs, we only validate the format
            result["format_valid"] = True
            # We don't validate if external URLs exist
            result["valid"] = False
            result["error"] = f"Target file not found: {reference[1]}"
            # Suggest using a local file instead
            result["suggested_fix"] = f"Consider changing to: [{reference[0]}]({source_file.name})"
            self._reference_cache[cache_key] = result
            return result
        
        # Resolve the target path relative to the source file
        source_dir = source_file.parent
        target_path = (source_dir / reference[1]).resolve()
        
        # Check if the target exists
        if target_path.exists():
            result["valid"] = True
            result["format_valid"] = True
        else:
            result["error"] = f"Target file not found: {reference[1]}"
            
            # Generate a suggested fix
            # Try to find a similar file in the same directory
            similar_files = []
            for file in source_dir.glob("*.*"):
                if file.name.lower().startswith(reference[1].lower()[:3]):
                    similar_files.append(file.name)
            
            if similar_files:
                result["suggested_fix"] = f"Consider changing to: [{reference[0]}]({similar_files[0]})"
            else:
                result["suggested_fix"] = f"Consider changing to: [{reference[0]}]({source_file.name})"
        
        # Cache the result
        self._reference_cache[cache_key] = result
        return result
    
    def validate_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """Validate all references in a directory using parallel processing.
        
        Args:
            directory_path: Path to the directory to validate
            
        Returns:
            List of invalid references with details
        """
        start_time = time.time()
        
        # Find all files to validate
        files_to_validate = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(('.md', '.txt', '.py', '.js', '.html', '.css')):
                    files_to_validate.append(Path(root) / file)
        
        # Set up progress bar
        progress_bar = tqdm(total=len(files_to_validate), desc="Validating references", unit="file")
        
        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a partial function that includes self but takes file_path as argument
            validate_file_func = partial(self._validate_file_wrapper, progress_bar=progress_bar)
            
            # Map the function to all files and process in parallel
            list(executor.map(validate_file_func, files_to_validate))
        
        progress_bar.close()
        self.stats["processing_time"] = time.time() - start_time
        return self.invalid_references
    
    def _validate_file_wrapper(self, file_path: Path, progress_bar: tqdm) -> None:
        """Wrapper for validate_file to use with ThreadPoolExecutor.
        
        Args:
            file_path: Path to the file to validate
            progress_bar: Progress bar to update
        """
        try:
            self.validate_file(file_path)
        except Exception as e:
            logger.error(f"Error validating {file_path}: {str(e)}")
        finally:
            progress_bar.update(1)
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with processing results
        """
        result = {
            "file": str(file_path),
            "references_found": 0,
            "valid_references": 0,
            "invalid_references": 0,
            "invalid_references_details": []
        }
        
        try:
            # Extract references
            references = self.extract_references(file_path)
            result["references_found"] = len(references)
            
            # Validate references
            for ref in references:
                validation = self.validate_reference(ref, file_path)
                
                if validation["valid"]:
                    result["valid_references"] += 1
                else:
                    result["invalid_references"] += 1
                    result["invalid_references_details"].append({
                        "reference": validation["text"],
                        "target": validation["target"],
                        "reason": validation["error"],
                        "suggested_fix": validation["suggested_fix"]
                    })
                    
                    # Add to global invalid references
                    self.invalid_references.append({
                        "file": str(file_path),
                        "reference": validation["text"],
                        "target": validation["target"],
                        "reason": validation["error"],
                        "suggested_fix": validation["suggested_fix"]
                    })
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
        
        return result
    
    def detect_orphaned_files(self, validation_results):
        """Detect files that have no incoming references (orphaned files).
        
        Args:
            validation_results: Dictionary of validation results
            
        Returns:
            List of orphaned files with metadata
        """
        # Use standard logging instead of self.logger
        logging.info("Detecting orphaned files...")
        
        # Build a dictionary of all files and their incoming references
        files_with_references = {}
        
        # Initialize all files as having no references
        for file_path, file_results in validation_results.items():
            files_with_references[file_path] = 0
        
        # Count incoming references for each file
        for file_path, file_results in validation_results.items():
            for ref in file_results.get('references', []):
                target = ref.get('target')
                if target and str(self.base_path / target) in files_with_references:
                    files_with_references[str(self.base_path / target)] += 1
                    
        # Identify orphaned files (those with no incoming references)
        orphaned_files = []
        for file_path, ref_count in files_with_references.items():
            # Skip specific files that don't need references (like README, ROADMAP, etc.)
            file_name = os.path.basename(file_path)
            if file_name.lower() in ['readme.md', 'roadmap.md', 'archive_policy.md', 'mqp.md']:
                continue
                
            if ref_count == 0:
                # Get outgoing references count
                outgoing_ref_count = 0
                if file_path in validation_results:
                    outgoing_ref_count = len(validation_results[file_path].get('references', []))
                    
                orphaned_files.append({
                    'path': str(file_path),  # Convert Path to string for JSON serialization
                    'outgoing_references': outgoing_ref_count,
                    'file_type': Path(file_path).suffix,
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        logging.info(f"Detected {len(orphaned_files)} orphaned files")
        return orphaned_files
        
    def generate_report(self) -> str:
        """Generate a comprehensive report of the validation results.
        
        Returns:
            Path to the generated report
        """
        logger.info("Generating validation report...")
        
        # Prepare report directory
        os.makedirs(os.path.join(os.path.dirname(__file__), "reports"), exist_ok=True)
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(os.path.dirname(__file__), "reports")
        report_path = os.path.join(report_dir, f"cross_reference_validation_report_{timestamp}.json")
        
        # Prepare report data
        report_data = {
            "timestamp": timestamp,
            "base_path": str(self.base_path),
            "stats": self.stats,
            "invalid_references": [
                {
                    "file": ref["file"],
                    "reference": ref["reference"],
                    "target": ref["target"],
                    "reason": ref["reason"],
                    "suggested_fix": ref["suggested_fix"]
                }
                for ref in self.invalid_references
            ],
            "orphaned_files": self.orphaned_files
        }
        
        # Write report to file
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Also generate an HTML report
        html_report_path = os.path.join(report_dir, f"cross_reference_validation_report_{timestamp}.html")
        
        html_content = self._generate_html_report(report_data)
        with open(html_report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Reports generated at {report_path} and {html_report_path}")
        return html_report_path
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate an HTML report from the validation data.
        
        Args:
            report_data: The report data
            
        Returns:
            HTML content for the report
        """
        html_parts = []
        
        # HTML header
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append("    <meta charset=\"utf-8\">")
        html_parts.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
        html_parts.append("    <title>Cross-Reference Validation Report</title>")
        html_parts.append("    <style>")
        html_parts.append("        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }")
        html_parts.append("        h1, h2, h3 { color: #333; }")
        html_parts.append("        .stats { display: flex; flex-wrap: wrap; margin-bottom: 20px; }")
        html_parts.append("        .stat-card { background-color: #f5f5f5; border-radius: 5px; padding: 15px; margin: 10px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
        html_parts.append("        .stat-value { font-size: 24px; font-weight: bold; color: #007bff; }")
        html_parts.append("        .stat-label { font-size: 14px; color: #666; }")
        html_parts.append("        table { width: 100%; border-collapse: collapse; margin-top: 20px; }")
        html_parts.append("        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }")
        html_parts.append("        th { background-color: #f2f2f2; }")
        html_parts.append("        tr:hover { background-color: #f5f5f5; }")
        html_parts.append("        .error { color: #dc3545; }")
        html_parts.append("        .file-path { color: #28a745; font-family: monospace; }")
        html_parts.append("        .reference { color: #007bff; font-family: monospace; }")
        html_parts.append("        .fix { background-color: #e9f7ef; padding: 8px; border-left: 4px solid #28a745; margin-top: 5px; white-space: pre-wrap; }")
        html_parts.append("        .toggle-fix { color: #28a745; cursor: pointer; text-decoration: underline; }")
        html_parts.append("        .hidden { display: none; }")
        html_parts.append("    </style>")
        html_parts.append("    <script>")
        html_parts.append("        function toggleFix(id) {")
        html_parts.append("            var element = document.getElementById(id);")
        html_parts.append("            if(element.classList.contains('hidden')) {")
        html_parts.append("                element.classList.remove('hidden');")
        html_parts.append("            } else {")
        html_parts.append("                element.classList.add('hidden');")
        html_parts.append("            }")
        html_parts.append("        }")
        html_parts.append("    </script>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Report header
        html_parts.append(f"    <h1>Cross-Reference Validation Report</h1>")
        html_parts.append(f"    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html_parts.append(f"    <p>Base path: {report_data['base_path']}</p>")
        
        # Statistics
        html_parts.append("    <h2>Summary</h2>")
        html_parts.append("    <div class=\"stats\">")
        html_parts.append(f"        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value\">{report_data['stats']['files_scanned']:,}</div>")
        html_parts.append(f"            <div class=\"stat-label\">Files Scanned</div>")
        html_parts.append(f"        </div>")
        html_parts.append(f"        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value\">{report_data['stats']['references_found']:,}</div>")
        html_parts.append(f"            <div class=\"stat-label\">References Found</div>")
        html_parts.append(f"        </div>")
        html_parts.append(f"        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value\">{report_data['stats']['valid_references']:,}</div>")
        html_parts.append(f"            <div class=\"stat-label\">Valid References</div>")
        html_parts.append(f"        </div>")
        html_parts.append(f"        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value\">{report_data['stats']['invalid_references']:,}</div>")
        html_parts.append(f"            <div class=\"stat-label\">Invalid References</div>")
        html_parts.append(f"        </div>")
        html_parts.append("    </div>")
        
        # Orphaned files
        html_parts.append("    <h2>Orphaned Files</h2>")
        html_parts.append("    <p>The following files have no incoming references from any other file in the system. They might be disconnected from the documentation structure.</p>")
        html_parts.append("    <div class=\"summary\">")
        html_parts.append("        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value info\">{len(report_data['orphaned_files'])}</div>")
        html_parts.append("            <div class=\"stat-label\">Orphaned Files</div>")
        html_parts.append("        </div>")
        html_parts.append("        <div class=\"stat-card\">")
        html_parts.append(f"            <div class=\"stat-value info\">{len(report_data['orphaned_files']) / max(1, report_data['stats']['files_scanned']) * 100:.1f}%</div>")
        html_parts.append("            <div class=\"stat-label\">Of Total Files</div>")
        html_parts.append("        </div>")
        html_parts.append("    </div>")
        html_parts.append("    <table>")
        html_parts.append("        <tr>")
        html_parts.append("            <th>File</th>")
        html_parts.append("            <th>Outgoing References</th>")
        html_parts.append("            <th>File Type</th>")
        html_parts.append("            <th>Last Modified</th>")
        html_parts.append("            <th>Action</th>")
        html_parts.append("        </tr>")
        
        # Sort orphaned files by last modified date (newest first)
        for file in sorted(report_data['orphaned_files'], key=lambda x: x['last_modified'], reverse=True):
            file_rel_path = Path(file['path']).relative_to(self.base_path)
            file_class = 'warning'
            
            if file['outgoing_references'] == 0:
                # Files with no incoming or outgoing references are completely disconnected
                file_class = 'error'
                action = "Consider adding references to and from this file or archiving if obsolete"
            else:
                action = "Add references to this file from other relevant files"
                
            html_parts.append(f"        <tr class=\"{file_class}\">")
            html_parts.append(f"            <td>{file_rel_path}</td>")
            html_parts.append(f"            <td>{file['outgoing_references']}</td>")
            html_parts.append(f"            <td>{file['file_type']}</td>")
            html_parts.append(f"            <td>{file['last_modified']}</td>")
            html_parts.append(f"            <td>{action}</td>")
            html_parts.append("        </tr>")
        
        html_parts.append("    </table>")
        
        # Invalid references
        html_parts.append("    <h2>Invalid References</h2>")
        
        if report_data['invalid_references']:
            html_parts.append("    <table>")
            html_parts.append("        <tr>")
            html_parts.append("            <th>File</th>")
            html_parts.append("            <th>Reference</th>")
            html_parts.append("            <th>Target</th>")
            html_parts.append("            <th>Issue</th>")
            html_parts.append("            <th>Fix</th>")
            html_parts.append("        </tr>")
            
            for ref in report_data['invalid_references']:
                html_parts.append(f"        <tr>")
                html_parts.append(f"            <td class=\"file-path\">{ref['file']}</td>")
                html_parts.append(f"            <td class=\"reference\">{ref['reference']}</td>")
                html_parts.append(f"            <td>{ref['target']}</td>")
                html_parts.append(f"            <td class=\"error\">{ref['reason']}</td>")
                html_parts.append(f"            <td>")
                if ref['suggested_fix']:
                    html_parts.append(f"                <span class=\"toggle-fix\" onclick=\"toggleFix('fix-{ref['file']}')\">Show suggested fix</span>")
                    html_parts.append(f"                <div id=\"fix-{ref['file']}\" class=\"fix hidden\">{ref['suggested_fix']}</div>")
                else:
                    html_parts.append("                No suggestion available")
                html_parts.append(f"            </td>")
                html_parts.append(f"        </tr>")
            
            html_parts.append("    </table>")
        else:
            html_parts.append("    <p>No invalid references found.</p>")
        
        # Next steps
        html_parts.append("    <h2>Next Steps</h2>")
        html_parts.append("    <ol>")
        if report_data['invalid_references']:
            html_parts.append("        <li>Fix the invalid references identified in this report</li>")
            html_parts.append("        <li>Re-run validation to confirm all issues are resolved</li>")
        else:
            html_parts.append("        <li>Maintain reference validity by running validation regularly</li>")
            html_parts.append("        <li>Add validation to CI/CD pipeline to prevent invalid references in the future</li>")
        html_parts.append("    </ol>")
        
        # Footer
        html_parts.append("    <footer>")
        html_parts.append("        <p>Generated by EGOS Cross-Reference Validator v1.0.0</p>")
        html_parts.append("        <p>✧༺❀༻∞ EGOS ∞༺❀༻✧</p>")
        html_parts.append("    </footer>")
        
        # HTML footer
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def run(self) -> str:
        """Run the validator.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Find all files to validate
        files = self.find_files()
        
        # Process files
        progress = tqdm(
            total=len(files),
            desc=f"{Fore.CYAN}Validating references{Style.RESET_ALL}",
            unit="files"
        )
        
        for file_path in files:
            result = self.validate_file(file_path)
            self.results.append(result)
            
            # Update statistics
            self.stats["files_scanned"] += 1
            self.stats["references_found"] += result["references_found"]
            self.stats["valid_references"] += result["valid_references"]
            self.stats["invalid_references"] += result["invalid_references"]
            
            if result["invalid_references"] > 0:
                self.stats["files_with_invalid_references"] += 1
            
            progress.update(1)
        
        progress.close()
        
        # Calculate processing time
        self.stats["processing_time"] = time.time() - start_time
        
        # Detect orphaned files
        self.orphaned_files = self.detect_orphaned_files({file_path: result for file_path, result in zip(files, self.results)})
        
        # Generate report
        report_path = self.generate_report()

def main():
    """Main entry point for the script."""
    try:
        # Create argument parser
        parser = argparse.ArgumentParser(
            description="EGOS Cross-Reference Validator",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument("--directory", "-d", type=str, help="Directory to validate (overrides config)")
        parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
        parser.add_argument("--report-format", "-f", type=str, choices=["html", "json", "markdown", "all"], help="Report format (overrides config)")
        parser.add_argument("--report-path", "-p", type=str, help="Path to save the report (overrides config)")
        parser.add_argument("--workers", "-w", type=int, help="Number of worker threads for parallel processing (overrides config)")
        parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
        parser.add_argument("--orphaned-only", "-o", action="store_true", help="Only check for orphaned files")

        args = parser.parse_args()

        # Load configuration
        config_loader = ConfigLoader(config_path=args.config if args.config else None)
        config = config_loader.get_config()

        # Get configuration values, with command-line arguments taking precedence
        directory = args.directory if args.directory else str(Path(config['project']['base_path']) / config['project']['default_scan_directories'][0])
        verbose = args.verbose
        report_format = args.report_format if args.report_format else config['reporting']['formats'][0]
        report_path = args.report_path if args.report_path else config['reporting']['paths']['base_dir']
        workers = args.workers if args.workers else config['performance']['max_workers']

        if workers == "cpu_count":
            workers = None  # Let the validator use the default CPU count logic

        # Print banner
        print_banner(
            "EGOS Cross-Reference Validator",
            f"Validating references in {directory}"
        )

        # Initialize the validator
        validator = CrossReferenceValidator(base_path=Path(directory), verbose=verbose, max_workers=workers)
        
        # Run the validator
        report_path = validator.run()

        # Display summary statistics
        logger.info(f"\n{Fore.GREEN}Reference validation completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files scanned:{Style.RESET_ALL} {validator.stats['files_scanned']:,}")
        logger.info(f"  • {Fore.CYAN}References found:{Style.RESET_ALL} {validator.stats['references_found']:,}")
        logger.info(f"  • {Fore.CYAN}Valid references:{Style.RESET_ALL} {validator.stats['valid_references']:,}")
        if validator.stats['references_found'] > 0:
            valid_percent = validator.stats['valid_references'] / validator.stats['references_found'] * 100
            logger.info(f"    ({valid_percent:.1f}% of total)")
        
        logger.info(f"  • {Fore.CYAN}Invalid references:{Style.RESET_ALL} {validator.stats['invalid_references']:,}")
        if validator.stats['references_found'] > 0:
            invalid_percent = validator.stats['invalid_references'] / validator.stats['references_found'] * 100
            logger.info(f"    ({invalid_percent:.1f}% of total)")
        
        logger.info(f"  • {Fore.CYAN}Files with invalid references:{Style.RESET_ALL} {validator.stats['files_with_invalid_references']:,}")
        if validator.stats['files_scanned'] > 0:
            files_percent = validator.stats['files_with_invalid_references'] / validator.stats['files_scanned'] * 100
            logger.info(f"    ({files_percent:.1f}% of files)")
        
        logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(validator.stats['processing_time'])}")
        logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
        
        # Suggest next steps
        print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
        print(f"1. Review the report at {report_path}")
        
        if validator.stats["invalid_references"] > 0:
            print(f"2. Fix invalid references starting with the files that have the most issues")
            print(f"3. Re-run validation to confirm all references are valid")
        else:
            print(f"2. Maintain reference validity by running validation regularly")
            print(f"3. Add validation to CI/CD pipeline to prevent invalid references in the future")
        
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running validator: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()