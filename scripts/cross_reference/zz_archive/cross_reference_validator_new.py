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
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - subsystems/AutoCrossRef/CROSSREF_STANDARD.md

# Standard library imports
import os
import re
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

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
    
    def __init__(self, base_path: str, directory: Optional[str] = None, verbose: bool = False):
        """Initialize the validator.
        
        Args:
            base_path: Base directory to search for files
            directory: Specific directory to validate (within base_path)
            verbose: Print detailed information during validation
        """
        self.base_path = Path(base_path)
        self.directory = Path(directory) if directory else None
        self.verbose = verbose
        
        # Statistics
        self.stats = {
            "files_scanned": 0,
            "references_found": 0,
            "valid_references": 0,
            "invalid_references": 0,
            "files_with_invalid_references": 0,
            "processing_time": 0
        }
        
        # Results
        self.results = []
        
        # Invalid references
        self.invalid_references = []
    
    def find_files(self) -> List[Path]:
        """Find all files to validate.
        
        Returns:
            List of file paths to validate
        """
        search_path = self.directory if self.directory else self.base_path
        
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
        """Validate a reference.
        
        Args:
            reference: Tuple (reference_text, reference_target)
            source_file: Path to the source file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": False,
            "reference": reference[0],
            "target": reference[1],
            "source": str(source_file),
            "reason": "",
            "suggested_fix": ""
        }
        
        # Extract the target path
        target_path = reference[1]
        
        # Handle relative paths
        if not target_path.startswith(('http://', 'https://', '/')):
            # Make path relative to source file's directory
            source_dir = source_file.parent
            target_path = str(source_dir / target_path)
        
        # Check if target exists
        target_file = Path(target_path)
        if target_file.exists():
            result["valid"] = True
        else:
            result["valid"] = False
            result["reason"] = f"Target file not found: {target_path}"
            
            # Generate suggested fix
            # Find closest matching file
            potential_files = list(source_file.parent.glob('*.md'))
            potential_files.extend(list(source_file.parent.glob('*.html')))
            
            if potential_files:
                # Sort by similarity to target path (using simple string distance)
                potential_files.sort(key=lambda x: len(set(str(x)) ^ set(target_path)))
                suggested_path = str(potential_files[0].relative_to(source_file.parent))
                result["suggested_fix"] = f"Consider changing to: [{reference[0]}]({suggested_path})"
        
        return result
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
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
                        "reference": validation["reference"],
                        "target": validation["target"],
                        "reason": validation["reason"],
                        "suggested_fix": validation["suggested_fix"]
                    })
                    
                    # Add to global invalid references
                    self.invalid_references.append(validation)
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
        
        return result
    
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
            "directory": str(self.directory) if self.directory else None,
            "stats": self.stats,
            "invalid_references": [
                {
                    "file": ref["source"],
                    "reference": ref["reference"],
                    "target": ref["target"],
                    "reason": ref["reason"],
                    "suggested_fix": ref["suggested_fix"]
                }
                for ref in self.invalid_references
            ]
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
        if report_data['directory']:
            html_parts.append(f"    <p>Directory: {report_data['directory']}</p>")
        
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
            
            for i, ref in enumerate(report_data['invalid_references']):
                html_parts.append(f"        <tr>")
                html_parts.append(f"            <td class=\"file-path\">{ref['file']}</td>")
                html_parts.append(f"            <td class=\"reference\">{ref['reference']}</td>")
                html_parts.append(f"            <td>{ref['target']}</td>")
                html_parts.append(f"            <td class=\"error\">{ref['reason']}</td>")
                html_parts.append(f"            <td>")
                if ref['suggested_fix']:
                    html_parts.append(f"                <span class=\"toggle-fix\" onclick=\"toggleFix('fix-{i}')\">Show suggested fix</span>")
                    html_parts.append(f"                <div id=\"fix-{i}\" class=\"fix hidden\">{ref['suggested_fix']}</div>")
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
            html_parts.append("        <li>Re-run the validation to confirm all issues are resolved</li>")
        else:
            html_parts.append("        <li>Maintain reference validity by running validation regularly</li>")
        html_parts.append("        <li>Consider adding validation to CI/CD pipeline</li>")
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
            result = self.process_file(file_path)
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
        
        # Generate report
        report_path = self.generate_report()
        
        return report_path

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Validate cross-references across the EGOS ecosystem",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--base-path", default=os.getcwd(), help="Base path to search for files")
    parser.add_argument("--directory", help="Specific directory to validate (within base-path)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed information during validation")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner(
        "EGOS Cross-Reference Validator",
        f"Validating references in {args.directory if args.directory else args.base_path}"
    )
    
    # Create and run the validator
    validator = CrossReferenceValidator(
        base_path=args.base_path,
        directory=args.directory,
        verbose=args.verbose
    )
    
    try:
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
