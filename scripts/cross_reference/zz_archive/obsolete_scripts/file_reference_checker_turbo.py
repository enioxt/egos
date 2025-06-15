#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cross-Reference Checker Turbo (Version 3.0.0)

Otimizado para desempenho máximo em projetos grandes, com foco em:
- Exclusão prévia de diretórios para evitar processamento desnecessário
- Compatibilidade total com Windows
- Tratamento eficiente de arquivos grandes e caminhos complexos
- Geração de relatórios detalhados de referências cruzadas

Key Features:
- Exclusão prévia de diretórios para evitar processamento desnecessário
- Compatibilidade total com Windows (sem dependências de SIGALRM)
- Limite de tamanho de arquivo para evitar processamento de arquivos grandes
- Processamento paralelo para melhor desempenho
- Relatórios detalhados em Markdown e JSON

@references:
- Original Script: file_reference_checker_optimized.py
- Windows Version: file_reference_checker_windows.py
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

class CrossReferenceTurbo:
    """Finds and reports cross-references between files in a project with maximum efficiency."""
    
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
        
        # Compile exclusion patterns for maximum efficiency
        self._setup_exclusion_patterns()
        
        # Reference search configuration
        self.reference_search_dirs_config = self.config.get("reference_search_directories", [])
        self.reference_search_dirs_abs = []
        
        # Pre-compute absolute paths for reference search directories
        for rel_path_str in self.reference_search_dirs_config:
            path = (self.project_base_path / Path(rel_path_str)).resolve()
            if path.exists():
                self.reference_search_dirs_abs.append(path)
            else:
                logger.warning(f"Reference search directory does not exist and will be skipped: {path}")

        # File extensions for reference search
        raw_ref_search_exts = self.config.get("reference_file_extensions", [])
        self.reference_file_extensions_search = {ext.lower() for ext in raw_ref_search_exts if ext.startswith('.')}
        
        # Reference patterns
        self.reference_patterns = self.config.get("reference_patterns", ["{filename}"])
        self.resolve_python_modules = self.config.get("resolve_python_modules", True)
        
        # Log configuration details
        logger.debug(f"Initialized CrossReferenceTurbo:")
        logger.debug(f"  Project Base: {self.project_base_path}")
        logger.debug(f"  Scan Dirs: {self.scan_directories_config}")
        logger.debug(f"  Target Extensions: {self.target_file_extensions}")
        logger.debug(f"  Time Cutoff: {self.time_cutoff}")
        logger.debug(f"  Max File Size: {self.max_file_size_bytes/1024/1024:.2f} MB")
        logger.debug(f"  Processing Timeout: {self.file_processing_timeout_sec} seconds")
        logger.debug(f"  Reference Search Dirs: {self.reference_search_dirs_config}")
        logger.debug(f"  Reference File Extensions: {self.reference_file_extensions_search}")
        logger.debug(f"  Reference Patterns: {self.reference_patterns}")

    def _setup_exclusion_patterns(self):
        """Set up exclusion patterns for maximum efficiency."""
        # Literal directory paths to exclude
        self.excluded_dirs_abs = []
        
        # Regex patterns for path exclusion
        self.excluded_regex_patterns = []
        
        # Glob patterns for exclusion
        self.excluded_glob_patterns = []
        
        # Process exclusion patterns from config
        for excluded_item_str in self.config.get("excluded_directories", []):
            if "*" in excluded_item_str or "?" in excluded_item_str or "[" in excluded_item_str:
                # Convert glob patterns to regex for faster matching
                if "**" in excluded_item_str:
                    # Handle ** patterns (match any level of directories)
                    regex_pattern = excluded_item_str.replace(".", "\\.").replace("**", ".*").replace("*", "[^/\\\\]*")
                    self.excluded_regex_patterns.append(re.compile(regex_pattern))
                else:
                    # Regular glob pattern
                    self.excluded_glob_patterns.append(excluded_item_str)
            else:
                # Literal directory path
                abs_path = (self.project_base_path / Path(excluded_item_str)).resolve()
                self.excluded_dirs_abs.append(abs_path)
        
        # Log exclusion patterns
        logger.debug(f"Excluded absolute directories: {[str(p) for p in self.excluded_dirs_abs]}")
        logger.debug(f"Excluded regex patterns: {[p.pattern for p in self.excluded_regex_patterns]}")
        logger.debug(f"Excluded glob patterns: {self.excluded_glob_patterns}")

    def _should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded based on configured patterns."""
        # Fast path: check if path is in excluded_dirs_abs or is a child of one
        for excluded_dir in self.excluded_dirs_abs:
            if path == excluded_dir or excluded_dir in path.parents:
                return True
        
        # Convert to relative path for pattern matching
        try:
            rel_path = path.relative_to(self.project_base_path)
            rel_path_str = str(rel_path)
            
            # Check regex patterns (fastest)
            for pattern in self.excluded_regex_patterns:
                if pattern.match(rel_path_str):
                    return True
            
            # Check glob patterns
            for pattern in self.excluded_glob_patterns:
                if rel_path.match(pattern) or Path(path.name).match(pattern):
                    return True
                    
        except ValueError:
            # Path is not relative to project_base_path
            pass
            
        return False

    def _find_recently_modified_files(self) -> List[Path]:
        """Find files modified within the configured time window, with efficient directory exclusion."""
        logger.info("Starting to find recently modified files...")
        modified_files = []
        processed_scan_dirs = set()
        
        # Process each scan directory
        for scan_dir_config in self.scan_directories_config:
            current_scan_dir = (self.project_base_path / Path(scan_dir_config)).resolve()
            
            if not current_scan_dir.is_dir():
                logger.warning(f"Scan directory {current_scan_dir} does not exist or is not a directory. Skipping.")
                continue
            
            if current_scan_dir in processed_scan_dirs:
                logger.debug(f"Skipping already processed scan directory: {current_scan_dir}")
                continue
                
            processed_scan_dirs.add(current_scan_dir)
            logger.info(f"Scanning directory for modified files: {current_scan_dir}")
            
            # Walk directory tree with efficient pruning
            for root, dirs, files in os.walk(current_scan_dir, topdown=True, followlinks=False):
                root_path = Path(root).resolve()
                
                # Prune excluded directories BEFORE descending
                # This is critical for performance
                i = 0
                while i < len(dirs):
                    dir_path = (root_path / dirs[i]).resolve()
                    if self._should_exclude_path(dir_path):
                        logger.info(f"Pruning excluded directory: {dir_path.relative_to(self.project_base_path)}")
                        dirs.pop(i)  # Remove directory from list to skip it
                    else:
                        i += 1
                
                # Process files in current directory
                for filename in files:
                    file_path = (root_path / filename).resolve()
                    
                    # Skip excluded files
                    if self._should_exclude_path(file_path):
                        continue
                    
                    # Skip files with non-target extensions
                    if self.target_file_extensions and file_path.suffix.lower() not in self.target_file_extensions:
                        continue
                    
                    try:
                        # Check if file exists and is a regular file
                        if not file_path.is_file():
                            continue
                            
                        # Check file size
                        file_size = file_path.stat().st_size
                        if file_size > self.max_file_size_bytes:
                            rel_path = file_path.relative_to(self.project_base_path)
                            logger.warning(f"Skipping oversized file: {rel_path} ({file_size/1024/1024:.2f} MB > {self.max_file_size_bytes/1024/1024:.2f} MB limit)")
                            continue
                        
                        # Check modification time
                        modified_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                        if modified_time >= self.time_cutoff:
                            modified_files.append(file_path)
                            rel_path = file_path.relative_to(self.project_base_path)
                            logger.info(f"Found candidate: {rel_path} (Mod: {modified_time.strftime('%Y-%m-%d %H:%M')})")
                    except (FileNotFoundError, PermissionError) as e:
                        # File might have been deleted or is inaccessible
                        logger.debug(f"Skipping inaccessible file {filename}: {e}")
                    except Exception as e:
                        logger.error(f"Error processing file {filename}: {e}")
        
        # Sort files for consistent output
        modified_files.sort()
        
        logger.info(f"Found {len(modified_files)} unique recently modified files matching criteria.")
        
        # Display limited number of files in log
        if modified_files:
            display_limit = 20
            if len(modified_files) > display_limit:
                logger.info(f"Recently modified files (first {display_limit} of {len(modified_files)}):")
                for i, file_path in enumerate(modified_files[:display_limit]):
                    try:
                        rel_path = file_path.relative_to(self.project_base_path)
                        logger.info(f"  - {i+1}. {rel_path}")
                    except ValueError:
                        logger.info(f"  - {i+1}. {file_path}")
                logger.info(f"...and {len(modified_files) - display_limit} more files.")
                
        return modified_files

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

        # Collect files to search in
        files_to_search = []
        
        for search_location in self.reference_search_dirs_abs:
            if search_location.is_file():
                if search_location.suffix.lower() in self.reference_file_extensions_search:
                    files_to_search.append(search_location)
            elif search_location.is_dir():
                try:
                    # Use os.walk for better performance than rglob
                    for root, _, files in os.walk(search_location):
                        root_path = Path(root)
                        for file in files:
                            file_path = (root_path / file).resolve()
                            
                            # Skip excluded files
                            if self._should_exclude_path(file_path):
                                continue
                                
                            # Check extension
                            if file_path.suffix.lower() in self.reference_file_extensions_search:
                                files_to_search.append(file_path)
                except Exception as e:
                    logger.error(f"Error walking directory {search_location}: {e}")
        
        # Process each file
        for file_to_search in files_to_search:
            try:
                # Skip self-references
                if candidate_file_path.resolve() == file_to_search.resolve():
                    continue
                    
                # Check file size
                try:
                    file_size = file_to_search.stat().st_size
                    if file_size > self.max_file_size_bytes:
                        rel_path = file_to_search.relative_to(self.project_base_path)
                        logger.warning(f"Skipping oversized file: {rel_path} ({file_size/1024/1024:.2f} MB > {self.max_file_size_bytes/1024/1024:.2f} MB limit)")
                        continue
                except (FileNotFoundError, PermissionError):
                    # Skip files that don't exist or can't be accessed
                    continue
                
                # Process file with timeout
                file_refs = self._process_file_with_timeout(
                    file_to_search, 
                    search_terms, 
                    self.file_processing_timeout_sec
                )
                
                if file_refs is not None:
                    references_found.extend(file_refs)
                    
            except Exception as e:
                try:
                    rel_path = str(file_to_search.relative_to(self.project_base_path))
                except ValueError:
                    rel_path = str(file_to_search)
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
            return
    
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
        start_time = time.time()
        
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
        
        # Log execution time
        elapsed_time = time.time() - start_time
        logger.info(f"Cross-reference checking process completed in {elapsed_time:.2f} seconds.")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Cross-Reference Checker Turbo")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    args = parser.parse_args()
    
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    
    # Configure logging level from config
    log_level_str = config.get("log_level", "INFO").upper()
    numeric_log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(numeric_log_level)
    
    # Run the checker
    checker = CrossReferenceTurbo(config)
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
