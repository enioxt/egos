#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cross-Reference Checker for Windows (Version 2.0.0)

This script identifies files modified within a configurable time window and searches for 
references to these files across specified project directories and file types. 
It generates timestamped Markdown and JSON reports detailing cross-references.

Key Features:
- Windows-compatible (no SIGALRM dependency)
- Efficient file scanning with robust exclusion patterns
- File size limits to prevent processing extremely large files
- Comprehensive reporting in Markdown and JSON formats
- Configurable via 'config.yaml'

Author: EGOS Development Team
Date: 2025-05-20
Version: 2.0.0

@references:
- Original Script: file_reference_checker_optimized.py
- Configuration: ./config.yaml
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
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import yaml

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "checker_debug_output.log", mode='w', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Default configuration path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config(config_path: Path) -> Dict:
    """Loads the YAML configuration file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        logger.info(f"Configuration loaded successfully from {config_path}")
        return config_data
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {config_path}. Please create it or check the path.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration file {config_path}: {e}")
        sys.exit(1)

class CrossReferenceChecker:
    """Finds and reports cross-references between files in a project."""
    
    def __init__(self, config: Dict):
        """Initialize the checker with configuration settings."""
        self.config = config
        self.project_base_path = Path(self.config.get("project_base_path", ".")).resolve()
        
        # Scan directories configuration
        self.scan_directories_config = self.config.get("scan_directories", ["."])
        
        # File extensions to consider
        raw_target_exts = self.config.get("target_file_extensions", [])
        self.target_file_extensions = {ext.lower() for ext in raw_target_exts if ext.startswith('.')}

        # Time window for modified files
        time_window_hours = self.config.get("time_window_hours", 48)
        self.time_cutoff = datetime.datetime.now() - datetime.timedelta(hours=time_window_hours)
        
        # File size limit
        self.max_file_size_bytes = self.config.get("max_file_size_mb", 5) * 1024 * 1024
        
        # Processing timeout
        self.file_processing_timeout_sec = self.config.get("file_processing_timeout_sec", 30)
        
        # Exclusion patterns
        self.excluded_dirs_abs = []
        self.excluded_patterns = []
        for excluded_item_str in self.config.get("excluded_directories", []):
            if "*" in excluded_item_str or "?" in excluded_item_str or "[" in excluded_item_str:
                self.excluded_patterns.append(excluded_item_str)
            else:
                self.excluded_dirs_abs.append((self.project_base_path / Path(excluded_item_str)).resolve())
        
        # Reference search configuration
        self.reference_search_dirs_config = self.config.get("reference_search_directories", [])
        self.reference_search_dirs_abs = []
        for rel_path_str in self.reference_search_dirs_config:
            self.reference_search_dirs_abs.append((self.project_base_path / Path(rel_path_str)).resolve())

        raw_ref_search_exts = self.config.get("reference_file_extensions", [])
        self.reference_file_extensions_search = {ext.lower() for ext in raw_ref_search_exts if ext.startswith('.')}
        
        self.reference_patterns = self.config.get("reference_patterns", ["{filename}"])
        self.resolve_python_modules = self.config.get("resolve_python_modules", True)
        
        # Log configuration details
        logger.debug(f"Initialized CrossReferenceChecker:")
        logger.debug(f"  Project Base: {self.project_base_path}")
        logger.debug(f"  Scan Dirs: {self.scan_directories_config}")
        logger.debug(f"  Target Extensions: {self.target_file_extensions}")
        logger.debug(f"  Time Cutoff: {self.time_cutoff}")
        logger.debug(f"  Max File Size: {self.max_file_size_bytes/1024/1024:.2f} MB")
        logger.debug(f"  Processing Timeout: {self.file_processing_timeout_sec} seconds")
        logger.debug(f"  Excluded Dirs: {self.excluded_dirs_abs}")
        logger.debug(f"  Excluded Patterns: {self.excluded_patterns}")
        logger.debug(f"  Reference Search Dirs: {self.reference_search_dirs_config}")
        logger.debug(f"  Reference File Extensions: {self.reference_file_extensions_search}")
        logger.debug(f"  Reference Patterns: {self.reference_patterns}")

    def _is_excluded(self, file_path: Path) -> bool:
        """Check if a file should be excluded based on patterns."""
        try:
            path_for_logging = file_path.relative_to(self.project_base_path)
        except ValueError:
            path_for_logging = file_path
            
        # Check if file is in an excluded directory
        for excluded_dir_abs_path in self.excluded_dirs_abs:
            if file_path == excluded_dir_abs_path or any(p == excluded_dir_abs_path for p in file_path.parents):
                logger.debug(f"Excluding file in excluded directory: {path_for_logging}")
                return True
                
        # Check if file matches an excluded pattern
        try:
            relative_to_project = file_path.relative_to(self.project_base_path)
            relative_str = str(relative_to_project)
            
            for pattern in self.excluded_patterns:
                # Use Path.match for glob pattern matching
                if Path(file_path.name).match(pattern) or relative_to_project.match(pattern):
                    logger.debug(f"Excluding file matching pattern '{pattern}': {path_for_logging}")
                    return True
                    
                # Additional check for ** patterns which Path.match doesn't handle well
                if '**' in pattern:
                    # Convert ** pattern to regex
                    regex_pattern = pattern.replace('.', '\\.').replace('**', '.*').replace('*', '[^/\\\\]*')
                    if re.match(regex_pattern, relative_str):
                        logger.debug(f"Excluding file matching ** pattern '{pattern}': {path_for_logging}")
                        return True
        except ValueError:
            pass
            
        return False

    def _is_excluded_dir_for_walk(self, dir_path: Path) -> bool:
        """Check if a directory should be excluded from walking."""
        try:
            path_for_logging = dir_path.relative_to(self.project_base_path)
        except ValueError:
            path_for_logging = dir_path

        for excluded_dir_abs_path in self.excluded_dirs_abs:
            if dir_path == excluded_dir_abs_path or excluded_dir_abs_path in dir_path.parents:
                logger.info(f"Pruning excluded directory during walk: {path_for_logging}")
                return True

        try:
            relative_to_project = dir_path.relative_to(self.project_base_path)
            relative_str = str(relative_to_project)
            
            for pattern in self.excluded_patterns:
                # Check directory name against pattern
                if Path(dir_path.name).match(pattern):
                    logger.info(f"Pruning directory matching name pattern: {path_for_logging} (pattern: '{pattern}')")
                    return True
                    
                # Check relative path against pattern
                if relative_to_project.match(pattern):
                    logger.info(f"Pruning directory matching relative path pattern: {path_for_logging} (pattern: '{pattern}')")
                    return True
                    
                # Additional check for ** patterns
                if '**' in pattern:
                    regex_pattern = pattern.replace('.', '\\.').replace('**', '.*').replace('*', '[^/\\\\]*')
                    if re.match(regex_pattern, relative_str):
                        logger.info(f"Pruning directory matching ** pattern: {path_for_logging} (pattern: '{pattern}')")
                        return True
        except ValueError:
            pass
            
        return False

    def _find_recently_modified_files(self) -> List[Path]:
        """Find files modified within the configured time window."""
        logger.info("Starting to find recently modified files...")
        modified_files_resolved = set()
        processed_scan_dirs_abs = set()

        for scan_dir_config_entry in self.scan_directories_config:
            current_scan_dir_abs = (self.project_base_path / Path(scan_dir_config_entry)).resolve()
            
            if not current_scan_dir_abs.is_dir():
                logger.warning(f"Scan directory {current_scan_dir_abs} does not exist or is not a directory. Skipping.")
                continue
            
            if current_scan_dir_abs in processed_scan_dirs_abs:
                logger.debug(f"Skipping already processed scan directory: {current_scan_dir_abs}")
                continue
                
            processed_scan_dirs_abs.add(current_scan_dir_abs)
            logger.info(f"Scanning directory for modified files: {current_scan_dir_abs}")
            
            for root, dirs, files in os.walk(current_scan_dir_abs, topdown=True, followlinks=False):
                current_root_path = Path(root).resolve()
                
                # Prune excluded directories
                dirs[:] = [d_name for d_name in dirs 
                          if not self._is_excluded_dir_for_walk((current_root_path / d_name).resolve())]

                for filename in files:
                    item_path = current_root_path / filename
                    
                    try:
                        # Resolve symlinks
                        resolved_item_path = item_path.resolve(strict=True)
                    except (FileNotFoundError, RuntimeError):
                        continue

                    if not resolved_item_path.is_file():
                        continue

                    # Check exclusions
                    if self._is_excluded(resolved_item_path):
                        continue
                        
                    # Check file extension
                    if self.target_file_extensions and resolved_item_path.suffix.lower() not in self.target_file_extensions:
                        continue
                    
                    try:
                        # Check modification time
                        modified_time_dt = datetime.datetime.fromtimestamp(resolved_item_path.stat().st_mtime)
                        if modified_time_dt >= self.time_cutoff:
                            modified_files_resolved.add(resolved_item_path)
                            try:
                                rel_path_for_log = resolved_item_path.relative_to(self.project_base_path)
                            except ValueError:
                                rel_path_for_log = resolved_item_path
                            logger.info(f"Found candidate: {rel_path_for_log} (Mod: {modified_time_dt.strftime('%Y-%m-%d %H:%M')})")
                    except Exception as e:
                        logger.error(f"Error processing file {resolved_item_path}: {e}")
                        continue
        
        final_list = sorted(list(modified_files_resolved))
        logger.info(f"Found {len(final_list)} unique recently modified files matching criteria.")
        
        # Display limited number of files in log
        if final_list:
            display_limit = 20
            if len(final_list) > display_limit:
                logger.info(f"Recently modified files (first {display_limit} of {len(final_list)}):")
                for i, rf in enumerate(final_list[:display_limit]):
                    try:
                        logger.info(f"  - {i+1}. {rf.relative_to(self.project_base_path)}")
                    except ValueError:
                        logger.info(f"  - {i+1}. {rf}")
                logger.info(f"...and {len(final_list) - display_limit} more files.")
                
        return final_list

    def _process_file_with_timeout(self, file_path, search_terms, timeout):
        """Process a file with timeout using threading."""
        result = []
        exception = []
        completed = []
        
        def target():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line_content in enumerate(f, 1):
                        if any(term in line_content for term in search_terms):
                            try:
                                rel_path = str(file_path.relative_to(self.project_base_path))
                            except ValueError:
                                rel_path = str(file_path)
                                
                            found_ref = {
                                "found_in_file": rel_path,
                                "line_number": line_num,
                                "line_content": line_content.strip()[:250]
                            }
                            result.append(found_ref)
                completed.append(True)
            except Exception as e:
                exception.append(e)
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Timeout occurred
            try:
                rel_path = str(file_path.relative_to(self.project_base_path))
            except ValueError:
                rel_path = str(file_path)
            logger.warning(f"Timeout processing file: {rel_path} (exceeded {timeout} seconds)")
            return None
            
        if exception:
            # Exception occurred
            raise exception[0]
            
        return result

    def _find_references_for_file(self, candidate_file_path: Path) -> List[Dict]:
        """Find references to a file in other project files."""
        references_found = []
        filename = candidate_file_path.name
        
        # Generate search terms based on reference patterns
        search_terms = []
        for pattern in self.reference_patterns:
            # Replace {filename} with the actual filename
            if "{filename}" in pattern:
                search_terms.append(pattern.replace("{filename}", filename))
                
            # Replace {filepath} with relative path if possible
            if "{filepath}" in pattern:
                try:
                    rel_path = str(candidate_file_path.relative_to(self.project_base_path))
                    search_terms.append(pattern.replace("{filepath}", rel_path))
                except ValueError:
                    # Skip if we can't get a relative path
                    pass
                    
            # Handle Python module imports if enabled
            if self.resolve_python_modules and candidate_file_path.suffix.lower() == '.py':
                if "{module_name}" in pattern:
                    module_name = filename[:-3]  # Remove .py extension
                    search_terms.append(pattern.replace("{module_name}", module_name))
                    
                    # Also add package-style imports
                    try:
                        rel_path = candidate_file_path.relative_to(self.project_base_path)
                        parent_dirs = list(rel_path.parents)
                        if len(parent_dirs) > 1:  # Has at least one parent directory
                            package_path = str(rel_path.parent / Path(module_name)).replace('\\', '.')
                            if package_path.startswith('.'):
                                package_path = package_path[1:]
                            search_terms.append(pattern.replace("{module_name}", package_path))
                    except ValueError:
                        pass
        
        if not search_terms:
            logger.warning(f"No search terms generated for {filename}")
            return []

        logger.debug(f"Searching for refs to '{filename}' using terms: {search_terms}")

        for search_location_config_path_str in self.reference_search_dirs_config:
            search_location_abs = (self.project_base_path / Path(search_location_config_path_str)).resolve()
            files_to_search_in = []

            if not search_location_abs.exists():
                logger.warning(f"Reference search location does not exist: {search_location_abs}")
                continue

            # Handle file vs directory search locations
            if search_location_abs.is_file():
                if search_location_abs.suffix.lower() in self.reference_file_extensions_search:
                    files_to_search_in.append(search_location_abs)
            elif search_location_abs.is_dir():
                for item in search_location_abs.rglob("*"):
                    if (item.is_file() and 
                        item.suffix.lower() in self.reference_file_extensions_search and
                        not self._is_excluded(item)):
                        files_to_search_in.append(item)
            
            # Process each file
            for file_to_search_path in files_to_search_in:
                try:
                    # Skip self-references
                    if candidate_file_path.resolve() == file_to_search_path.resolve():
                        continue
                        
                    # Check file size
                    file_size = file_to_search_path.stat().st_size
                    if file_size > self.max_file_size_bytes:
                        try:
                            rel_path = str(file_to_search_path.relative_to(self.project_base_path))
                        except ValueError:
                            rel_path = str(file_to_search_path)
                        logger.warning(f"Skipping oversized file: {rel_path} ({file_size/1024/1024:.2f} MB > {self.max_file_size_bytes/1024/1024:.2f} MB limit)")
                        continue
                    
                    # Process file with timeout
                    file_refs = self._process_file_with_timeout(
                        file_to_search_path, 
                        search_terms, 
                        self.file_processing_timeout_sec
                    )
                    
                    if file_refs is not None:
                        references_found.extend(file_refs)
                        
                except Exception as e:
                    try:
                        rel_path = str(file_to_search_path.relative_to(self.project_base_path))
                    except ValueError:
                        rel_path = str(file_to_search_path)
                    logger.warning(f"Error processing file {rel_path}: {e}")
        
        return references_found

    def _generate_reports(self, detailed_file_data: List[Dict]):
        """Generate Markdown and JSON reports of cross-references."""
        output_formats = self.config.get("output_formats", [])
        output_filename_base = self.config.get("output_filename", "file_reference_report")
        script_dir = Path(__file__).resolve().parent

        # Generate timestamp for filenames
        now = datetime.datetime.now()
        report_generated_at_iso = now.isoformat()
        timestamp_for_file = now.strftime("%Y%m%d_%H%M%S")
        
        archived_output_filename_base = f"{output_filename_base}_{timestamp_for_file}"

        if not detailed_file_data:
            logger.info("No candidate files found to report details for.")
    
        # Prepare JSON report data
        report_data_for_json = {
            "report_generated_at": report_generated_at_iso,
            "project_base_path": str(self.project_base_path),
            "time_window_hours": self.config.get("time_window_hours"),
            "target_file_extensions": list(self.target_file_extensions),
            "reference_search_directories": self.reference_search_dirs_config,
            "reference_file_extensions_search": list(self.reference_file_extensions_search),
            "reference_patterns": self.reference_patterns,
            "scan_directories": self.scan_directories_config,
            "excluded_directories_abs": [str(p) for p in self.excluded_dirs_abs],
            "excluded_patterns": self.excluded_patterns,
            "files_processed_count": len(detailed_file_data),
            "files": [] 
        }

        # Prepare Markdown report content
        markdown_lines = [
            f"# File Reference Report\n",
            f"Generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"## Configuration\n",
            f"- Project Base Path: `{self.project_base_path}`",
            f"- Time Window: {self.config.get('time_window_hours')} hours",
            f"- Scan Directories: {', '.join(f'`{d}`' for d in self.scan_directories_config)}",
            f"- Reference Search Directories: {', '.join(f'`{d}`' for d in self.reference_search_dirs_config)}",
            f"- Files Processed: {len(detailed_file_data)}\n",
            f"## Reference Results\n"
        ]

        # Process each file's data
        for item_data in detailed_file_data:
            f_path = item_data["file_path"]
            references = item_data["references_found"]
            
            try:
                relative_path_str = str(f_path.relative_to(self.project_base_path))
            except ValueError:
                relative_path_str = str(f_path.resolve())
            
            # Add to JSON data
            serializable_references = []
            for ref in references:
                serializable_ref = ref.copy()
                if isinstance(serializable_ref.get("found_in_file"), Path):
                    serializable_ref["found_in_file"] = str(serializable_ref["found_in_file"])
                serializable_references.append(serializable_ref)

            report_data_for_json["files"].append({
                "path": relative_path_str,
                "references_found": serializable_references
            })
            
            # Add to Markdown content
            markdown_lines.append(f"### File: `{relative_path_str}`\n")
            
            if references:
                markdown_lines.append(f"Found {len(references)} references:\n")
                for ref in references:
                    ref_file = ref["found_in_file"]
                    line_num = ref["line_number"]
                    line_content = ref["line_content"]
                    markdown_lines.append(f"- In `{ref_file}` at line {line_num}:")
                    markdown_lines.append(f"  ```\n  {line_content}\n  ```\n")
            else:
                markdown_lines.append("No references found.\n")

        # Write reports
        if "json" in output_formats:
            json_output_path = script_dir / f"{archived_output_filename_base}.json"
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data_for_json, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON report written to: {json_output_path}")
            
        if "markdown" in output_formats:
            md_output_path = script_dir / f"{archived_output_filename_base}.md"
            with open(md_output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(markdown_lines))
            logger.info(f"Markdown report written to: {md_output_path}")
            
        # Manage report retention
        self._manage_report_retention()

    def _manage_report_retention(self):
        """Delete old reports based on retention policy."""
        retention_days = self.config.get("report_retention_days", 30)
        if retention_days <= 0:
            logger.info("Report retention disabled.")
            return
            
        script_dir = Path(__file__).resolve().parent
        output_filename_base = self.config.get("output_filename", "file_reference_report")
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        logger.info(f"Managing report retention: Removing reports older than {retention_days} days.")
        
        # Process JSON reports
        for report_file in script_dir.glob(f"{output_filename_base}_*.json"):
            self._process_retention_for_file(report_file, cutoff_date, output_filename_base)
            
        # Process Markdown reports
        for report_file in script_dir.glob(f"{output_filename_base}_*.md"):
            self._process_retention_for_file(report_file, cutoff_date, output_filename_base)

    def _process_retention_for_file(self, report_file: Path, cutoff_date: datetime.datetime, output_filename_base: str):
        """Process a single file for retention policy."""
        try:
            # Extract timestamp from filename
            filename = report_file.name
            if not filename.startswith(output_filename_base + "_"):
                return
                
            timestamp_str = filename[len(output_filename_base) + 1:].split('.')[0]
            if len(timestamp_str) != 15:  # Format: YYYYMMDD_HHMMSS
                return
                
            try:
                file_date = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                return
                
            if file_date < cutoff_date:
                report_file.unlink()
                logger.info(f"Deleted old report: {report_file}")
        except Exception as e:
            logger.warning(f"Error processing file {report_file} for retention: {e}")

    def run(self):
        """Run the cross-reference checking process."""
        logger.info("Starting cross-reference checking process...")
        
        # Find recently modified files
        modified_files = self._find_recently_modified_files()
        
        if not modified_files:
            logger.info("No modified files found within the specified time window.")
            return
            
        # Process each file to find references
        detailed_file_data = []
        
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            future_to_file = {
                executor.submit(self._find_references_for_file, f_path): f_path 
                for f_path in modified_files
            }
            
            for future in as_completed(future_to_file):
                f_path = future_to_file[future]
                try:
                    references = future.result()
                    detailed_file_data.append({
                        "file_path": f_path,
                        "references_found": references
                    })
                    
                    try:
                        rel_path = f_path.relative_to(self.project_base_path)
                    except ValueError:
                        rel_path = f_path
                        
                    logger.info(f"Processed {rel_path}: Found {len(references)} references")
                except Exception as e:
                    logger.error(f"Error processing {f_path}: {e}")
        
        # Generate reports
        self._generate_reports(detailed_file_data)
        logger.info("Cross-reference checking process completed.")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Cross-Reference Checker for Windows")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    args = parser.parse_args()
    
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    
    # Configure logging level from config
    log_level_str = config.get("log_level", "INFO").upper()
    numeric_log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(numeric_log_level)
    
    # Run the checker
    checker = CrossReferenceChecker(config)
    checker.run()

if __name__ == "__main__":
    logger.info("Script starting execution.")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
