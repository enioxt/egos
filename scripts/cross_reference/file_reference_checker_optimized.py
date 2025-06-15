#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimized File Reference Checker (Version 1.1.0)

This script identifies files modified within a configurable time window (e.g., last N hours)
and then searches for references to these files across specified project directories 
and file types. It generates timestamped Markdown and JSON reports detailing each 
modified file and any cross-references found (or a warning if none are found).

Key Features:
- Scans for recently modified files based on a configurable time window.
- Searches for references to these files using configurable patterns, paths, and file types.
- Generates comprehensive Markdown and JSON reports.
- Archives reports with timestamps to prevent overwriting.
- Implements an automatic report retention policy to manage storage by deleting old reports.
- Highly configurable via 'config.yaml'.

This version enhances the original checker by adding robust reference searching,
detailed reporting including reference locations, and automated report archival/retention.

Author: EGOS Development Team (with Cascade AI)
Date: 2025-05-19 (Last Update)
Version: 1.1.0

Cross-References:
- Original Script: ../file_reference_checker.py (if applicable)
- Configuration: ./config.yaml (relative to script)
- Example Reports: ./file_reference_report_YYYYMMDD_HHMMSS.md / .json
- Main Documentation: ../../../docs/reference/file_reference_checker_optimized.md (to be created/updated)

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
import os
import datetime
import json
import logging

# Initialize logger early for use in load_config
logger = logging.getLogger(__name__)
import os
import re
import subprocess
import sys
import signal
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import yaml

# Configure basic logging first, it will be updated after config is loaded
logging.basicConfig(
    level=logging.INFO, # Default level
    format="%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "checker_debug_output.log", mode='w', encoding='utf-8')
    ]
)

# Default configuration path (can be overridden by command-line argument later)
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

# Load configuration
CONFIG = load_config(DEFAULT_CONFIG_PATH)

# Reconfigure logging level based on the loaded configuration
log_level_str = CONFIG.get("log_level", "INFO").upper()
numeric_log_level = getattr(logging, log_level_str, logging.INFO)
# Get the root logger and set its level and handlers
root_logger = logging.getLogger()
root_logger.setLevel(numeric_log_level)
# Ensure all handlers attached to the root logger also respect this level
# (or configure them individually if more granular control is needed later)
for handler in root_logger.handlers:
    handler.setLevel(numeric_log_level)
    # Optionally, re-set formatter if it was different per handler before
    # handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s"))
# If we want to change format or handlers, we'd do it here too
# For now, just updating the level is fine.
logger.info(f"Logging level set to {log_level_str} based on configuration.")


# === MAIN CLASS AND FUNCTION DEFINITIONS WILL BE APPENDED BELOW VIA TERMINAL ===
# === This initial structure is created by an AI agent.                 ===

class FileReferenceCheckerOptimized:
    def __init__(self, config: Dict):
        """Initializes the checker with configurations for scanning, exclusion, reference searching, and report retention."""
        self.config = config
        self.project_base_path = Path(self.config.get("project_base_path", ".")).resolve()
        
        self.scan_directories_config = self.config.get("scan_directories", ["."])
        
        raw_target_exts = self.config.get("target_file_extensions", [])
        self.target_file_extensions = {ext.lower() for ext in raw_target_exts if ext.startswith('.')}

        time_window_hours = self.config.get("time_window_hours", 48)
        self.time_cutoff = datetime.datetime.now() - datetime.timedelta(hours=time_window_hours)
        
        # Set a maximum file size for processing to prevent hanging on extremely large files
        # Default to 5MB which should be more than enough for most code/doc files
        self.max_file_size_bytes = self.config.get("max_file_size_mb", 5) * 1024 * 1024
        
        # Set a timeout for file processing operations (in seconds)
        self.file_processing_timeout = self.config.get("file_processing_timeout_sec", 30)
        
        self.excluded_dirs_abs: List[Path] = []
        self.excluded_patterns: List[str] = []
        for excluded_item_str in self.config.get("excluded_directories", []):
            if "*" in excluded_item_str or "?" in excluded_item_str or "[" in excluded_item_str:
                self.excluded_patterns.append(excluded_item_str)
            else:
                self.excluded_dirs_abs.append((self.project_base_path / Path(excluded_item_str)).resolve())

        logger.debug(f"Initialized FileReferenceCheckerOptimized:")
        logger.debug(f"  Project Base: {self.project_base_path}")
        logger.debug(f"  Scan Dirs Config: {self.scan_directories_config}")
        logger.debug(f"  Target Exts: {self.target_file_extensions}")
        logger.debug(f"  Time Cutoff: {self.time_cutoff}")
        logger.debug(f"  Excluded Dirs Abs: {self.excluded_dirs_abs}")
        logger.debug(f"  Excluded Patterns: {self.excluded_patterns}")

        # Load reference searching configurations
        self.reference_search_dirs_config = self.config.get("reference_search_directories", [])
        self.reference_search_dirs_abs: List[Path] = []
        for rel_path_str in self.reference_search_dirs_config:
            # Check if the path is a file or directory before resolving
            # This assumes paths in config can be files (like README.md) or dirs (like docs/)
            # For simplicity, we resolve all. If a file path doesn't exist, resolve() might error or behave unexpectedly
            # depending on the Pathlib version and OS. Better to ensure files exist or handle potential errors later.
            # For now, direct resolve is fine as we expect configured paths to be valid.
            self.reference_search_dirs_abs.append((self.project_base_path / Path(rel_path_str)).resolve())

        raw_ref_search_exts = self.config.get("reference_file_extensions", [])
        self.reference_file_extensions_search = {ext.lower() for ext in raw_ref_search_exts if ext.startswith('.')}
        
        self.reference_patterns = self.config.get("reference_patterns", ["{filename}"]) # Default to filename if not specified
        self.resolve_python_modules = self.config.get("resolve_python_modules", True)

        logger.debug(f"  Reference Search Dirs Config: {self.reference_search_dirs_config}")
        logger.debug(f"  Reference Search Dirs Abs: {self.reference_search_dirs_abs}")
        logger.debug(f"  Reference File Exts for Search: {self.reference_file_extensions_search}")
        logger.debug(f"  Reference Patterns: {self.reference_patterns}")
        logger.debug(f"  Resolve Python Modules: {self.resolve_python_modules}")

    def _timeout_handler(self, signum, frame):
        """Handler for signal timeouts to prevent script from hanging on problematic files."""
        raise TimeoutError(f"File processing timed out after {self.file_processing_timeout} seconds")
        
    def _find_references_for_file(self, candidate_file_path: Path) -> List[Dict]:
        """Searches for references to the given candidate_file_path within the configured
        reference_search_directories and using the configured reference_patterns.

        Args:
            candidate_file_path: The Path object of the recently modified file to search for.

        Returns:
            A list of dictionaries, where each dictionary represents a found reference
            and includes 'found_in_file', 'line_number', and 'line_content'.
        """
        references_found: List[Dict] = []
        
        # Prepare search patterns based on the candidate file
        filename = candidate_file_path.name
        try:
            filepath_rel_to_project = str(candidate_file_path.relative_to(self.project_base_path))
        except ValueError:
            # If candidate_file_path is not under project_base_path (should not happen for candidates)
            # or if project_base_path is not a parent, use the full path as a fallback for pattern generation.
            # This might make some {filepath} patterns less effective if they rely on relative paths.
            filepath_rel_to_project = str(candidate_file_path.resolve()) 
        
        # For {module_name} pattern, typically used for Python files
        module_name = ""
        if candidate_file_path.suffix.lower() == '.py':
            if self.resolve_python_modules:
                try:
                    module_name = str(candidate_file_path.relative_to(self.project_base_path).with_suffix('')).replace(os.sep, '.')
                except ValueError: 
                    module_name = candidate_file_path.stem 
            else:
                module_name = candidate_file_path.stem

        search_terms: List[str] = []
        for pattern_template in self.reference_patterns:
            term = pattern_template.replace("{filename}", filename)\
                                   .replace("{filepath}", filepath_rel_to_project)
            if "{module_name}" in pattern_template: 
                 term = term.replace("{module_name}", module_name if module_name else filename.replace(".py",""))
            search_terms.append(term)
        
        search_terms = sorted(list(set(st for st in search_terms if st)))

        if not search_terms:
            logger.warning(f"No valid search terms generated for candidate: {candidate_file_path}")
            return []

        logger.debug(f"Searching for refs to '{filename}' (terms: {search_terms}) in {self.reference_search_dirs_config}")

        for search_location_config_path_str in self.reference_search_dirs_config:
            search_location_abs = (self.project_base_path / Path(search_location_config_path_str)).resolve()
            files_to_search_in: List[Path] = []

            if not search_location_abs.exists():
                logger.warning(f"Configured reference search location does not exist: {search_location_abs}")
                continue

            if search_location_abs.is_file():
                if search_location_abs.suffix.lower() in self.reference_file_extensions_search:
                    files_to_search_in.append(search_location_abs)
                else:
                    logger.debug(f"Skipping direct file {search_location_abs} for ref search; ext not in 'reference_file_extensions_search'.")
            elif search_location_abs.is_dir():
                for item in search_location_abs.rglob("*"):
                    if item.is_file() and item.suffix.lower() in self.reference_file_extensions_search:
                        files_to_search_in.append(item)
            
            for file_to_search_path in files_to_search_in:
                try:
                    if candidate_file_path.resolve() == file_to_search_path.resolve():
                        # Optionally skip searching a file for references to itself if it's too noisy.
                        # Depends on patterns; specific patterns might still be relevant.
                        # logger.debug(f"Skipping search for {filename} within itself ({file_to_search_path})")
                        continue # For now, skip simple self-reference to avoid direct name matches in its own content
                    
                    # Check file size before processing to avoid hanging on extremely large files
                    file_size = file_to_search_path.stat().st_size
                    if file_size > self.max_file_size_bytes:
                        logger.warning(f"Skipping oversized file: {file_to_search_path.relative_to(self.project_base_path)} ({file_size/1024/1024:.2f} MB > {self.max_file_size_bytes/1024/1024:.2f} MB limit)")
                        continue

                    # Set up timeout to prevent hanging on problematic files
                    original_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                    signal.alarm(self.file_processing_timeout)
                    
                    try:
                        with open(file_to_search_path, 'r', encoding='utf-8', errors='ignore') as f_search:
                            for line_num, line_content in enumerate(f_search, 1):
                                if any(term in line_content for term in search_terms):
                                    found_ref = {
                                        "found_in_file": str(file_to_search_path.relative_to(self.project_base_path)),
                                        "line_number": line_num,
                                        "line_content": line_content.strip()[:250] 
                                    }
                                    references_found.append(found_ref)
                                    logger.debug(f"  Found ref to '{filename}' in '{found_ref['found_in_file']}' at line {line_num}")
                                    # Optimization: if one reference is found, could break if only existence matters.
                                    # But for reporting, we want all references.
                    except TimeoutError:
                        rel_path = str(file_to_search_path.relative_to(self.project_base_path))
                        logger.warning(f"Timeout while processing {rel_path}. File may be too complex or contain circular references.")
                    finally:
                        # Reset the alarm and restore original handler
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, original_handler)
                except Exception as e:
                    logger.warning(f"Could not read/process file {file_to_search_path} for ref search: {e}")
        
        return references_found

    def _generate_reports(self, detailed_file_data: List[Dict]):
        """Generates reports based on detailed file data, including found references, with timestamped filenames.

        Reports include paths of modified files and any cross-references found for them,
        or a warning if none are found. Output formats (Markdown, JSON) are configurable.
        """
        output_formats = self.config.get("output_formats", [])
        output_filename_base = self.config.get("output_filename", "file_reference_report")
        script_dir = Path(__file__).resolve().parent

        # Generate timestamp for filenames and report metadata
        now = datetime.datetime.now()
        report_generated_at_iso = now.isoformat()
        timestamp_for_file = now.strftime("%Y%m%d_%H%M%S")
        
        archived_output_filename_base = f"{output_filename_base}_{timestamp_for_file}"

        if not detailed_file_data:
            logger.info("No candidate files found to report details for.")
            # Still generate an empty-ish report to show the script ran.
    
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

        for item_data in detailed_file_data:
            f_path = item_data["file_path"]
            references = item_data["references_found"]
            try:
                relative_path_str = str(f_path.relative_to(self.project_base_path))
            except ValueError:
                relative_path_str = str(f_path.resolve())
        
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

        if "markdown" in output_formats:
            md_path = script_dir / f"{archived_output_filename_base}.md"
            logger.info(f"Generating Markdown report: {md_path}")
            try:
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# File Reference Checker Report\n\n")
                    f.write(f"- **Report Generated At:** {report_data_for_json['report_generated_at']}\n")
                    f.write(f"- **Project Base Path:** `{self.project_base_path}`\n")
                    f.write(f"- **Time Window (Hours):** {report_data_for_json['time_window_hours']}\n")
                    f.write(f"- **Target Extensions Scanned:** `{', '.join(self.target_file_extensions) if self.target_file_extensions else 'Any'}`\n")
                    f.write(f"- **Scan Directories Config:** `{', '.join(self.scan_directories_config)}`\n") # Added Config for clarity
                    f.write(f"- **Reference Search Dirs:** `{', '.join(self.reference_search_dirs_config)}`\n")
                    f.write(f"- **Reference Search Exts:** `{', '.join(self.reference_file_extensions_search)}`\n")
                    f.write(f"- **Files Processed:** {report_data_for_json['files_processed_count']}\n\n")
                
                    if report_data_for_json["files"]:
                        f.write("## Candidate Files & Their References:\n\n")
                        for file_detail in report_data_for_json["files"]:
                            f.write(f"### `{file_detail['path']}`\n")
                            if file_detail["references_found"]:
                                f.write(f"**Found {len(file_detail['references_found'])} reference(s):**\n")
                                for ref in file_detail["references_found"]:
                                    f.write(f"- In: `{ref['found_in_file']}` (Line: {ref['line_number']})\n")
                                    f.write(f"  ```\n  {ref['line_content']}\n  ```\n")
                            else:
                                f.write(f"  - **No references found - WARNING: File might be undocumented or orphaned.** (<!-- TO_BE_REPLACED -->MEMORY[3bae44d3...])\n")
                            f.write("\n")
                    else:
                        f.write("No recently modified files found matching the criteria to process for references.\n")
                logger.info(f"Markdown report saved to {md_path}")
            except IOError as e:
                logger.error(f"Failed to write Markdown report {md_path}: {e}")

        if "json" in output_formats:
            json_path = script_dir / f"{archived_output_filename_base}.json"
            logger.info(f"Generating JSON report: {json_path}")
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data_for_json, f, indent=4)
                logger.info(f"JSON report saved to {json_path}")
            except IOError as e:
                logger.error(f"Failed to write JSON report {json_path}: {e}")
            except TypeError as e:
                logger.error(f"Data serialization error for JSON report {json_path}: {e}")

    def _manage_report_retention(self):
        """Manages report file retention, deleting reports older than a configured period."""
        script_dir = Path(__file__).resolve().parent
        output_filename_base = self.config.get("output_filename", "file_reference_report")
        retention_days = self.config.get("report_retention_days", 30) 
        
        if retention_days <= 0:
            logger.info("Report retention is disabled (retention_days <= 0).")
            return

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        logger.info(f"Managing report retention: Deleting reports older than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} ({retention_days} days old).")

        deleted_count = 0
        for report_file in script_dir.glob(f"{output_filename_base}_*.md"):
            if self._process_retention_for_file(report_file, cutoff_date, output_filename_base):
                deleted_count += 1
        for report_file in script_dir.glob(f"{output_filename_base}_*.json"):
            if self._process_retention_for_file(report_file, cutoff_date, output_filename_base):
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old report(s).")
        else:
            logger.info("No old reports found to delete.")

    def _process_retention_for_file(self, report_file: Path, cutoff_date: datetime.datetime, output_filename_base: str) -> bool:
        """Helper to process a single file for retention policy."""
        try:
            filename_stem = report_file.stem
            if not filename_stem.startswith(output_filename_base + "_"):
                return False 

            timestamp_str = filename_stem[len(output_filename_base)+1:]
            
            if not (len(timestamp_str) == 15 and timestamp_str[8] == '_'):
                 logger.debug(f"Could not parse timestamp from report filename (unexpected format): {report_file.name}")
                 return False

            report_date = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            if report_date < cutoff_date:
                report_file.unlink()
                logger.info(f"Deleted old report: {report_file.name} (Date: {report_date.strftime('%Y-%m-%d')})")
                return True
        except ValueError:
            logger.warning(f"Could not parse timestamp from report filename: {report_file.name}")
        except OSError as e:
            logger.error(f"Error deleting report file {report_file.name}: {e}")
        return False

    def _is_excluded(self, file_path: Path) -> bool:
        # file_path is expected to be an absolute, resolved path
        try:
            path_for_logging = file_path.relative_to(self.project_base_path)
        except ValueError:
            path_for_logging = file_path 

        # Check against absolute excluded directories (already resolved)
        # This check is more relevant for files directly in an excluded dir, 
        # as os.walk pruning should handle most subdirectory cases.
        for excluded_dir in self.excluded_dirs_abs:
            if excluded_dir in file_path.parents or excluded_dir == file_path.parent:
                # This file is inside an excluded directory.
                # No specific log here as the directory pruning should be the primary mechanism.
                return True
        
        # Check against excluded glob patterns
        try:
            relative_to_project = file_path.relative_to(self.project_base_path)
        except ValueError:
            relative_to_project = None 

        for pattern in self.excluded_patterns:
            if Path(file_path.name).match(pattern): # e.g., "*.log", "*.egg-info"
                logger.info(f"Excluding file by name pattern: {path_for_logging} (pattern: '{pattern}')")
                return True
            if relative_to_project and relative_to_project.match(pattern): # e.g., "output/*"
                logger.info(f"Excluding file by relative path pattern: {path_for_logging} (pattern: '{pattern}')")
                return True
        return False

    def _is_excluded_dir_for_walk(self, dir_path: Path) -> bool:
        # dir_path is expected to be an absolute, resolved path
        try:
            path_for_logging = dir_path.relative_to(self.project_base_path)
        except ValueError:
            path_for_logging = dir_path

        for excluded_dir_abs_path in self.excluded_dirs_abs:
            if dir_path == excluded_dir_abs_path or excluded_dir_abs_path in dir_path.parents:
                logger.info(f"Pruning excluded directory during walk: {path_for_logging} (rule: {excluded_dir_abs_path.name})")
                return True

        try:
            relative_to_project = dir_path.relative_to(self.project_base_path)
        except ValueError:
            relative_to_project = None

        for pattern in self.excluded_patterns:
            # Match pattern against the directory name itself (e.g., "__pycache__", "build")
            if Path(dir_path.name).match(pattern):
                logger.info(f"Pruning directory matching name pattern during walk: {path_for_logging} (pattern: '{pattern}')")
                return True
            # Match pattern against path relative to project_base_path (e.g., "docs/build", "*/output")
            if relative_to_project and relative_to_project.match(pattern):
                logger.info(f"Pruning directory matching relative path pattern during walk: {path_for_logging} (pattern: '{pattern}')")
                return True
        return False

    def _find_recently_modified_files(self) -> List[Path]:
        logger.info("Starting to find recently modified files...")
        modified_files_resolved: Set[Path] = set()
        processed_scan_dirs_abs: Set[Path] = set()

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
                
                # Prune directories before descending
                # Must modify dirs[:] in place for os.walk to respect it
                dirs[:] = [d_name for d_name in dirs if not self._is_excluded_dir_for_walk((current_root_path / d_name).resolve())]

                for filename in files:
                    item_path = current_root_path / filename
                    
                    try:
                        # Resolve symlinks for files, strict=True to catch broken ones
                        resolved_item_path = item_path.resolve(strict=True) 
                    except FileNotFoundError: # Broken symlink
                        # logger.debug(f"Skipping broken symlink: {item_path}") # Can be verbose
                        continue
                    except RuntimeError: # Max symlink recursion depth
                        logger.warning(f"Maximum symlink recursion hit for: {item_path}. Skipping.")
                        continue

                    if not resolved_item_path.is_file():
                        # This case should be rare if item_path came from 'files' list of os.walk
                        # and resolved successfully to something that isn't a file (e.g. symlink loop to dir)
                        # logger.debug(f"Skipping non-file after resolve: {resolved_item_path}")
                        continue

                    # Individual file exclusion check (e.g., specific file patterns not caught by dir exclusion)
                    if self._is_excluded(resolved_item_path):
                        # logger.info for pattern matches is handled within _is_excluded
                        continue
                        
                    if self.target_file_extensions and resolved_item_path.suffix.lower() not in self.target_file_extensions:
                        # logger.debug(f"Skipping file due to non-target extension '{resolved_item_path.suffix.lower()}': {resolved_item_path.name}")
                        continue
                    
                    try:
                        modified_time_dt = datetime.datetime.fromtimestamp(resolved_item_path.stat().st_mtime)
                        if modified_time_dt >= self.time_cutoff:
                            modified_files_resolved.add(resolved_item_path)
                            try:
                                rel_path_for_log = resolved_item_path.relative_to(self.project_base_path)
                            except ValueError:
                                rel_path_for_log = resolved_item_path
                            logger.info(f"Found candidate: {rel_path_for_log} (Mod: {modified_time_dt.strftime('%Y-%m-%d %H:%M')})")
                        # else:
                            # logger.debug(f"Skipping file due to old mod time: {resolved_item_path.name}") # Too verbose
                    except FileNotFoundError: # Should be rare due to strict=True in resolve
                        logger.warning(f"File not found during stat (deleted mid-scan?): {resolved_item_path}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing file {resolved_item_path}: {e}")
                        continue
        
        final_list = sorted(list(modified_files_resolved))
        logger.info(f"Found {len(final_list)} unique recently modified files matching criteria.")
        
        if final_list:
            # Adhering to <!-- TO_BE_REPLACED --> for concise logging
            display_limit = 20 
            if len(final_list) > display_limit:
                logger.info(f"Recently modified files (first {display_limit} of {len(final_list)}, resolved, relative to project):")
                for i, rf in enumerate(final_list[:display_limit]):
                    try:
                        logger.info(f"  - {i+1}. {rf.relative_to(self.project_base_path)}")
                    except ValueError:
                        logger.info(f"  - {i+1}. {rf} (not relative to project base)")
                logger.info(f"...and {len(final_list) - display_limit} more files. Full list available at DEBUG level.")
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Full list of recently modified files (DEBUG):")
                    for idx, rf_debug in enumerate(final_list):
                        try:
                            logger.debug(f"  - {idx+1}. {rf_debug.relative_to(self.project_base_path)}")
                        except ValueError:
                            logger.debug(f"  - {idx+1}. {rf_debug} (not relative to project base)")
            else:
                logger.info("Recently modified files (resolved, relative to project):")
                for idx, rf in enumerate(final_list):
                    try:
                        logger.info(f"  - {idx+1}. {rf.relative_to(self.project_base_path)}")
                    except ValueError:
                        logger.info(f"  - {idx+1}. {rf} (not relative to project base)")
        return final_list

def main_optimized():
    pass
    # Main CLI logic will be appended here

# === END OF INITIAL STRUCTURE ===

if __name__ == "__main__":
    # Check if platform supports SIGALRM (mainly for Windows compatibility)
    if not hasattr(signal, 'SIGALRM'):
        logger.warning("SIGALRM not available on this platform. File processing timeout will be disabled.")
        # Define a no-op replacement for signal-based timeout on Windows
        original_find_references = FileReferenceCheckerOptimized._find_references_for_file
        def patched_find_references(self, candidate_file_path):
            # Remove the timeout mechanism for Windows
            self._timeout_handler = lambda *args: None
            return original_find_references(self, candidate_file_path)
        FileReferenceCheckerOptimized._find_references_for_file = patched_find_references
    
    logger.info("Script starting execution.")
    checker = FileReferenceCheckerOptimized(CONFIG)
    
    logger.info("Attempting to find recently modified files...")
    recently_modified_paths = checker._find_recently_modified_files()
    
    detailed_found_files_data = []
    if recently_modified_paths:
        logger.info("--- Finding references for recently modified files ---")
        for f_path in recently_modified_paths:
            try:
                path_for_log = f_path.relative_to(checker.project_base_path)
            except ValueError:
                path_for_log = f_path
            logger.info(f"  Processing: {path_for_log}")
            
            references = checker._find_references_for_file(f_path)
            # To add last_modified, you'd do:
            # mod_time = datetime.datetime.fromtimestamp(f_path.stat().st_mtime).isoformat()
            detailed_found_files_data.append({
                "file_path": f_path,
                "references_found": references
                # "last_modified": mod_time # If we add this
            })
            if references:
                logger.info(f"    Found {len(references)} reference(s) for {path_for_log}")
            else:
                logger.info(f"    No references found for {path_for_log}")
        logger.info("----------------------------------------------------")
    else:
        logger.info("No recently modified files found to process for references.")
    
    # Call _generate_reports with the new data structure
    if 'checker' in locals() and hasattr(checker, '_generate_reports'):
        checker._generate_reports(detailed_found_files_data)
    else:
        logger.warning("Could not call _generate_reports. 'checker' not found or method missing.")
    # Manage report retention
    if 'checker' in locals() and hasattr(checker, '_manage_report_retention'):
        checker._manage_report_retention()
    else:
        logger.warning("Could not call _manage_report_retention. 'checker' not found or method missing.")

    logger.info("Script finished.")