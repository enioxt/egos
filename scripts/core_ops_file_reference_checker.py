#!/usr/bin/env python3
"""EGOS File Reference Checker

This script scans the repository for recently modified files and checks
for cross-references to them in other important documentation and code files.
It helps identify undocumented or poorly referenced components.

Requires: PyYAML (for configuration file parsing)

Subsystem: KOIOS (Auditing & Quality Sub-module)
Module ID: KOS-AUD-001 (Tentative)
Status: Development

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
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import yaml # Added for YAML config loading
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging (can be replaced by KoiosLogger if available)
# Basic config, level might be overridden by --verbose flag in main()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("file_reference_checker")

# --- Configuration Defaults (can be overridden by config file or CLI) ---
DEFAULT_TIME_WINDOW_HOURS = 48
DEFAULT_MONITORED_EXTENSIONS = [
    ".py", ".js", ".ts", ".md", ".yaml", ".yml", ".json", ".rst", ".java", ".cs", ".go", ".php", ".rb", ".html", ".css"
]
DEFAULT_EXCLUDED_DIRS = [
    "node_modules", ".git", "venv", "__pycache__", "build", "dist", "target", ".serverless", ".terraform", ".pytest_cache", ".tox"
]
DEFAULT_REFERENCE_FILE_EXTENSIONS = [
    ".py", ".js", ".ts", ".md", ".yaml", ".yml", ".json", ".rst", ".java", ".cs", ".go", ".php", ".rb", ".html", ".css",
    ".txt", ".xml", ".sh", ".ps1", ".cfg", ".ini"
]
CONFIG_FILE_NAME = ".file_ref_checker.yml"

class FileReferenceChecker:
    def __init__(
        self,
        repo_path: str,
        since: str = f"{DEFAULT_TIME_WINDOW_HOURS}h",
        exclude_dirs: Optional[List[str]] = None,
        monitored_extensions: Optional[List[str]] = None,
        reference_extensions: Optional[List[str]] = None,
        config_file_path: Optional[str] = None,
        output_json_path: Optional[str] = None,
        output_md_path: Optional[str] = None,
        agent_mode: bool = False,
    ):
        self.repo_path = os.path.abspath(repo_path)
        self.agent_mode = agent_mode

        # Load config from file first, then override with CLI/API params
        self.config = self._load_config(config_file_path)
        
        self.time_window_str = since
        self.time_delta = self._parse_time_window(self.config.get("time_window", since))
        
        self.exclude_dirs = list(set(DEFAULT_EXCLUDED_DIRS + self.config.get("exclude_dirs", [])))
        if exclude_dirs:
            self.exclude_dirs = list(set(self.exclude_dirs + exclude_dirs))
            
        self.monitored_extensions = list(set(DEFAULT_MONITORED_EXTENSIONS + self.config.get("monitored_extensions", [])))
        if monitored_extensions:
            self.monitored_extensions = list(set(self.monitored_extensions + monitored_extensions))
            
        self.reference_extensions = list(set(DEFAULT_REFERENCE_FILE_EXTENSIONS + self.config.get("reference_extensions", [])))
        if reference_extensions:
            self.reference_extensions = list(set(self.reference_extensions + reference_extensions))

        self.output_json_path = self.config.get("output_json", output_json_path)
        self.output_md_path = self.config.get("output_md", output_md_path)

        if not self.agent_mode:
            logger.info(f"FileReferenceChecker initialized for repo: {self.repo_path}")
            logger.info(f"Time window: {self.time_window_str}")
            logger.info(f"Excluded Dirs: {self.exclude_dirs}")
            logger.info(f"Monitored Exts: {self.monitored_extensions}")
            logger.info(f"Reference Exts: {self.reference_extensions}")

    def _load_config(self, config_file_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        paths_to_try = []
        if config_file_path:
            paths_to_try.append(os.path.abspath(config_file_path))
        
        # Default config file in repo root
        paths_to_try.append(os.path.join(self.repo_path, CONFIG_FILE_NAME))
        # Fallback: .config directory in repo root (as per some EGOS conventions)
        paths_to_try.append(os.path.join(self.repo_path, ".config", CONFIG_FILE_NAME))

        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if isinstance(config, dict):
                            if not self.agent_mode:
                                logger.info(f"Successfully loaded configuration from {path}")
                            return config
                        else:
                            if not self.agent_mode:
                                logger.warning(f"Configuration file {path} is not a valid YAML dictionary. Ignoring.")
                            return {}
                except yaml.YAMLError as e:
                    if not self.agent_mode:
                        logger.error(f"Error parsing YAML configuration file {path}: {e}. Ignoring config file.")
                    return {}
                except IOError as e:
                    if not self.agent_mode:
                        logger.error(f"Error reading configuration file {path}: {e}. Ignoring config file.")
                    return {}
        if not self.agent_mode:
            logger.info(f"No configuration file found or loaded. Using default settings and CLI arguments.")
        return {}

    def _parse_time_window(self, time_str: str) -> datetime.timedelta:
        """Parse time window string (e.g., '48h', '7d') into timedelta."""
        match = re.match(r"(\d+)([hd])", time_str.lower())
        if not match:
            logger.warning(f"Invalid time window format: {time_str}. Using default {DEFAULT_TIME_WINDOW_HOURS}h.")
            return datetime.timedelta(hours=DEFAULT_TIME_WINDOW_HOURS)
        value, unit = int(match.group(1)), match.group(2)
        if unit == 'h':
            return datetime.timedelta(hours=value)
        elif unit == 'd':
            return datetime.timedelta(days=value)
        return datetime.timedelta(hours=DEFAULT_TIME_WINDOW_HOURS) # Fallback

    def _find_modified_files_git(self) -> List[Dict[str, Any]]:
        """Find files modified within the time window using Git, respecting monitored extensions and excluded directories."""
        since_date = datetime.datetime.now(datetime.timezone.utc) - self.time_delta
        since_iso = since_date.isoformat()

        # Using --name-status to capture file status (A)dded, (M)odified, (D)eleted, etc.
        # We are interested in A, M, and R (renamed, treat new name as modified)
        # --diff-filter=AMR filters for Added, Modified, Renamed files directly in git log.
        # %H: commit hash, %aI: author date ISO 8601, %ct: committer timestamp UNIX
        # Using committer timestamp as it's more aligned with when the change was integrated.
        cmd = [
            "git", "-C", self.repo_path, "log",
            f"--since={since_iso}",
            "--name-status",
            "--pretty=format:COMMIT:%H %ct",
            "--no-renames", # Handled by diff-filter, but kept for clarity; consider removing if redundant
            "--diff-filter=AMR" # Focus on Added, Modified, Renamed files
        ]

        modified_files_details: Dict[str, Dict[str, Any]] = {}

        try:
            if not self.agent_mode:
                logger.debug(f"Executing git command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            output = process.stdout.strip()
            
            current_commit_hash = None
            current_commit_timestamp = None

            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("COMMIT:"):
                    parts = line.split(" ", 2)
                    current_commit_hash = parts[0][7:]
                    current_commit_timestamp = int(parts[1])
                    continue
                
                if current_commit_hash and current_commit_timestamp:
                    # Line should be status <tab> filepath
                    # Example: M       path/to/file.py
                    # Example: A       path/to/new_file.py
                    # Renamed files (RXXX) might have two paths, R100 old_path new_path. We only care about the new_path.
                    status_path = line.split('\t', 1)
                    if len(status_path) < 2:
                        if not self.agent_mode:
                            logger.debug(f"Skipping malformed git log line: {line}")
                        continue
                    
                    status, file_path_relative = status_path[0], status_path[1]
                    # For renamed files (e.g., R100 old new), file_path_relative might contain both.
                    # git log with --name-status and --diff-filter=AMR should simplify this:
                    # R status usually shows the new name.
                    # If it's a rename like 'R100\told_path\tnew_path', we take the new_path.
                    if '\t' in file_path_relative: # Handles RXXX cases with old and new path
                        _, file_path_relative = file_path_relative.split('\t',1)

                    file_path_abs = os.path.join(self.repo_path, file_path_relative)
                    file_path_abs = os.path.normpath(file_path_abs)

                    # 1. Check if in excluded directory
                    if any(ex_dir in file_path_abs for ex_dir in self.exclude_dirs):
                        continue

                    # 2. Check if it has a monitored extension
                    _, ext = os.path.splitext(file_path_relative)
                    if ext.lower() not in self.monitored_extensions:
                        continue
                    
                    # If file is already tracked from a more recent commit, skip
                    if file_path_abs in modified_files_details and modified_files_details[file_path_abs]['timestamp_unix'] > current_commit_timestamp:
                        continue
                        
                    modified_files_details[file_path_abs] = {
                        "path": file_path_abs,
                        "relative_path": file_path_relative,
                        "last_modified_iso": datetime.datetime.fromtimestamp(current_commit_timestamp, datetime.timezone.utc).isoformat(),
                        "timestamp_unix": current_commit_timestamp,
                        "status": status # M, A, R (usually new name)
                    }

        except subprocess.CalledProcessError as e:
            if not self.agent_mode:
                logger.error(f"Git log command failed: {e}")
                logger.error(f"Git stderr: {e.stderr}")
            return []
        except FileNotFoundError:
            if not self.agent_mode:
                logger.error("'git' command not found. Please ensure Git is installed and in your PATH.")
            return []
        except Exception as e:
            if not self.agent_mode:
                logger.error(f"An unexpected error occurred while finding modified files: {e}")
            return []
            
        result_list = list(modified_files_details.values())
        if not self.agent_mode:
            logger.info(f"Found {len(result_list)} modified files matching criteria.")
            for f_detail in result_list[:5]: # Log a few examples
                logger.debug(f"  - {f_detail['relative_path']} (Status: {f_detail['status']}, Modified: {f_detail['last_modified_iso']})")
        return result_list

    def _find_reference_files(self) -> List[str]:
        """Gather all files of specified reference types to search within, respecting exclusions."""
        reference_files: List[str] = []
        if not self.agent_mode:
            logger.info(f"Scanning for reference files in {self.repo_path}...")
            logger.debug(f"Reference extensions: {self.reference_extensions}")
            logger.debug(f"Excluded directories: {self.exclude_dirs}")

        for root, dirs, files in os.walk(self.repo_path, topdown=True):
            # Modify dirs in-place to skip excluded directories
            # Based on https://docs.python.org/3/library/os.html#os.walk example
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in [os.path.join(self.repo_path, ex_d) for ex_d in self.exclude_dirs] and not d.startswith('.') and d not in self.exclude_dirs]
            
            for file_name in files:
                # Check if current directory is within an excluded path segment
                # This check is important as dirs[:] modification only prunes full directory names
                # listed in exclude_dirs, not subdirectories of those or pattern-based exclusions.
                current_file_path_abs = os.path.join(root, file_name)
                current_file_path_abs_norm = os.path.normpath(current_file_path_abs)
                
                is_excluded = False
                for ex_path_segment in self.exclude_dirs:
                    # Normalize ex_path_segment to handle cases like 'venv' vs './venv'
                    normalized_ex_segment = os.path.normpath(os.path.join(self.repo_path, ex_path_segment))
                    if current_file_path_abs_norm.startswith(normalized_ex_segment + os.sep) or current_file_path_abs_norm == normalized_ex_segment:
                        is_excluded = True
                        break
                if is_excluded:
                    continue

                _, ext = os.path.splitext(file_name)
                if ext.lower() in self.reference_extensions:
                    reference_files.append(current_file_path_abs_norm)
        
        if not self.agent_mode:
            logger.info(f"Found {len(reference_files)} reference files to search within.")
            if reference_files:
                 logger.debug(f"First few reference files: {reference_files[:5]}")
        return reference_files

    def _is_rg_available(self) -> bool:
        """Check if ripgrep (rg) is installed and available in PATH."""
        if hasattr(self, '_rg_available_cached'): # Cache the check
            return self._rg_available_cached
        try:
            subprocess.run(["rg", "--version"], capture_output=True, check=True, text=True, encoding='utf-8')
            self._rg_available_cached = True
            if not self.agent_mode:
                logger.info("ripgrep (rg) is available. Using rg for faster searches.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._rg_available_cached = False
            if not self.agent_mode:
                logger.info("ripgrep (rg) not found or not working. Falling back to Python's regex for searching. This may be slower.")
            return False

    def _search_for_mentions_rg(self, patterns: List[str], search_files: List[str], modified_file_path_abs: str) -> List[Dict[str, Any]]:
        """Search for patterns in files using ripgrep."""
        mentions: List[Dict[str, Any]] = []
        # ripgrep can handle multiple patterns. -e pattern1 -e pattern2 ...
        # We'll use --regexp for each pattern for clarity and to ensure they are treated as regex.
        # --json output provides structured data: file, line_number, lines.text, submatches.
        # We need to be careful with shell quoting if patterns contain special characters, but subprocess list args handle this.
        base_cmd = ["rg", "--json", "--case-insensitive", "--stats"]
        pattern_args = []
        for p in patterns:
            pattern_args.extend(["--regexp", p])
        
        # ripgrep might struggle with a huge number of individual files as arguments.
        # It's often better to let rg search directories or use its include/exclude mechanisms.
        # However, our reference_files list is already filtered. We can pass them if the list is not excessively long.
        # For very large lists, consider writing to a temp file list and using --file-list with rg, or searching common parent dirs.
        # For now, pass files directly, assuming the list is manageable.
        # We must exclude the modified file itself from the search.
        files_to_search_rg = [f for f in search_files if f != modified_file_path_abs]
        if not files_to_search_rg:
            return []

        cmd = base_cmd + pattern_args + files_to_search_rg

        try:
            # Limit rg execution time to prevent stalls on massive repositories / pathological cases
            # This timeout might need to be configurable if it causes issues.
            process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=120) # 2 min timeout
            # rg with --json outputs one JSON object per line for each match or summary.
            for line in process.stdout.strip().splitlines():
                try:
                    match_data = json.loads(line)
                    if match_data.get("type") == "match":
                        file_path = match_data.get("data", {}).get("path", {}).get("text")
                        line_number = match_data.get("data", {}).get("line_number")
                        text_bytes = match_data.get("data", {}).get("lines", {}).get("bytes") # Prefer bytes, decode carefully
                        text_str = match_data.get("data", {}).get("lines", {}).get("text") # Fallback to text if bytes not present
                        context = ""
                        if text_bytes:
                            try:
                                context = bytes.fromhex(text_bytes.strip()).decode('utf-8', errors='replace').strip()
                            except ValueError:
                                context = text_str.strip() if text_str else "[Error decoding context]"
                        elif text_str:
                            context = text_str.strip()
                        
                        # Identify which pattern matched (requires --vimgrep or more complex parsing, or run rg per pattern)
                        # For now, we don't precisely know which pattern matched from a single rg run with multiple patterns.
                        # This is a simplification for V1. To get exact pattern, one might run rg per pattern or parse submatches.
                        submatches = match_data.get("data", {}).get("submatches", [])
                        matched_text_parts = [sm.get("match", {}).get("text") for sm in submatches if sm.get("match", {}).get("text")]
                        matched_pattern_derived = matched_text_parts[0] if matched_text_parts else "(multiple patterns)"

                        mentions.append({
                            "in": os.path.normpath(os.path.join(self.repo_path, file_path)), # rg returns relative paths by default if searching within repo_path
                            "line_number": line_number,
                            "context": context[:200] + ('...' if len(context) > 200 else ''), # Truncate long contexts
                            "pattern_matched": matched_pattern_derived # This is a simplification
                        })
                    elif match_data.get("type") == "summary":
                        if not self.agent_mode:
                            logger.debug(f"ripgrep summary for {modified_file_path_abs}: matched {match_data['data']['stats']['matches']} lines in {match_data['data']['stats']['num_files_with_matches']} files.")
                except json.JSONDecodeError:
                    if not self.agent_mode:
                        logger.debug(f"Skipping non-JSON line from rg output: {line}")
        except subprocess.TimeoutExpired:
            if not self.agent_mode:
                logger.warning(f"ripgrep search timed out for patterns related to {modified_file_path_abs}.")
        except subprocess.CalledProcessError as e:
            # rg exits with 1 if no matches are found, which is not an error for us.
            # It exits with 2 for actual errors.
            if e.returncode > 1 :
                 if not self.agent_mode:
                    logger.error(f"ripgrep search failed for {modified_file_path_abs}: {e}\nStderr: {e.stderr}")
        except FileNotFoundError: # Should be caught by _is_rg_available, but as a safeguard
            if not self.agent_mode:
                logger.error("ripgrep not found during search execution.")
            return [] # Should trigger fallback in calling function
        except Exception as e:
            if not self.agent_mode:
                logger.error(f"An unexpected error occurred during ripgrep search for {modified_file_path_abs}: {e}")
        return mentions

    def _search_for_mentions_python(self, patterns: List[str], search_files: List[str], modified_file_path_abs: str) -> List[Dict[str, Any]]:
        """Search for patterns in files using Python's re module (slower fallback)."""
        mentions: List[Dict[str, Any]] = []
        # Compile regex patterns for efficiency
        compiled_patterns = []
        for p_str in patterns:
            try:
                compiled_patterns.append((p_str, re.compile(p_str, re.IGNORECASE)))
            except re.error as e:
                if not self.agent_mode:
                    logger.warning(f"Invalid regex pattern '{p_str}': {e}. Skipping this pattern.")

        if not compiled_patterns:
            return []

        for ref_file_path in search_files:
            if ref_file_path == modified_file_path_abs: # Do not search file in itself
                continue
            try:
                with open(ref_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line_content in enumerate(f, 1):
                        for p_str, compiled_re in compiled_patterns:
                            match = compiled_re.search(line_content)
                            if match:
                                context_start = max(0, match.start() - 50)
                                context_end = min(len(line_content), match.end() + 50)
                                context = line_content[context_start:context_end].strip()
                                mentions.append({
                                    "in": ref_file_path,
                                    "line_number": i,
                                    "context": context[:200] + ('...' if len(context) > 200 else ''),
                                    "pattern_matched": p_str
                                })
                                break # Found a match in this line for one pattern, move to next line
            except Exception as e:
                if not self.agent_mode:
                    logger.debug(f"Could not read or process file {ref_file_path} with Python regex: {e}")
        return mentions

    def _search_for_mentions(self, modified_file_path_abs: str, reference_files: List[str]) -> List[Dict[str, Any]]:
        """Search for mentions of the modified file in reference files."""
        mentions: List[Dict[str, Any]] = []
        if not reference_files:
            return mentions

        # Generate search patterns
        # 1. Exact filename
        # 2. Filename without extension
        # 3. Relative path from repo root
        # More sophisticated patterns can be added (e.g., significant path parts)
        
        file_name_exact = os.path.basename(modified_file_path_abs)
        file_name_no_ext, _ = os.path.splitext(file_name_exact)
        relative_path_from_repo = os.path.relpath(modified_file_path_abs, self.repo_path).replace("\\", "/") # Normalize to fwd slashes

        patterns_to_search = [
            re.escape(file_name_exact), # Escaped for regex, literal string for rg
            re.escape(file_name_no_ext),
            re.escape(relative_path_from_repo) 
        ]
        # Add unescaped for rg if rg handles literal strings by default for some flags, but --regexp needs valid regex
        # For rg with --regexp, re.escape is good practice.
        
        # Remove duplicates that might arise (e.g. filename is same as filename_no_ext if no ext)
        patterns_to_search = sorted(list(set(p for p in patterns_to_search if p))) # Ensure non-empty patterns

        if not patterns_to_search:
            if not self.agent_mode:
                logger.debug(f"No valid search patterns generated for {modified_file_path_abs}")
            return []

        if not self.agent_mode:
            logger.debug(f"Searching for patterns {patterns_to_search} related to {modified_file_path_abs}")

        if self._is_rg_available():
            mentions = self._search_for_mentions_rg(patterns_to_search, reference_files, modified_file_path_abs)
        else:
            mentions = self._search_for_mentions_python(patterns_to_search, reference_files, modified_file_path_abs)
        
        # Deduplicate mentions based on file, line_number, and context to avoid near-identical entries from overlapping patterns
        # A more robust deduplication might be needed if context snippets vary slightly for the same essential match
        deduplicated_mentions_map: Dict[Tuple[str, int, str], Dict[str, Any]] = {}
        for m in mentions:
            key = (m['in'], m['line_number'], m['context'][:50]) # Key on first 50 chars of context for dedup
            if key not in deduplicated_mentions_map:
                deduplicated_mentions_map[key] = m
            else:
                # Potentially merge matched_pattern info if different patterns hit same line
                existing_pattern = deduplicated_mentions_map[key]['pattern_matched']
                new_pattern = m['pattern_matched']
                if existing_pattern != new_pattern and new_pattern not in existing_pattern:
                    deduplicated_mentions_map[key]['pattern_matched'] += f", {new_pattern}"
                    
        return list(deduplicated_mentions_map.values())

    def _generate_report_json(self, results: List[Dict[str, Any]]) -> str:
        """Generate JSON report."""
        return json.dumps(results, indent=2)

    def _generate_report_markdown(self, results: List[Dict[str, Any]]) -> str:
        """Generate Markdown report."""
        now = datetime.datetime.now()
        lines = [
            "# File Reference Check Report",
            f"_Generated on: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}_",
            f"_Time Window: {self.time_window_str}_",
            f"_Repository Path: `{self.repo_path}`_",
            ""
        ]

        undocumented_files = [res for res in results if res['status'] == "Undocumented"]
        documented_files = [res for res in results if res['status'] == "Documented"]

        lines.append(f"## Summary")
        lines.append(f"- Total Files Checked: {len(results)}")
        lines.append(f"- Documented Files: {len(documented_files)}")
        lines.append(f"- Undocumented Files: {len(undocumented_files)}")
        lines.append("")

        if undocumented_files:
            lines.append("## 🚨 Undocumented Files")
            lines.append("The following recently modified files had no clear references found:")
            lines.append("")
            for item in undocumented_files:
                lines.append(f"### `{item['file']}`")
                lines.append(f"- **Last Modified**: {item['last_modified']}")
                lines.append(f"- **Status**: <span style='color:red;'>**{item['status']}**</span>")
                lines.append("") 
        else:
            lines.append("## ✅ All Recently Modified Files Appear Documented")
            lines.append("No undocumented files found within the specified criteria.")
            lines.append("")

        if documented_files:
            lines.append("## 📄 Documented Files Details")
            lines.append("The following recently modified files have references:")
            lines.append("")
            for item in documented_files:
                lines.append(f"### `{item['file']}`")
                lines.append(f"- **Last Modified**: {item['last_modified']}")
                lines.append(f"- **Status**: <span style='color:green;'>**{item['status']}**</span>")
                if item['mentions']:
                    lines.append(f"- **Mentions Found**: {len(item['mentions'])} (See JSON report for full details and contexts)")
                    # Optionally, show a few sample mentions if needed, e.g., first 3 unique files
                    # unique_mention_files = sorted(list(set(os.path.relpath(m['in'], self.repo_path) for m in item['mentions'])))
                    # lines.append(f"  - Sample mention locations: {', '.join('`' + f + '`' for f in unique_mention_files[:3])}{'...' if len(unique_mention_files) > 3 else ''}")
                lines.append("")
        
        lines.append("---")
        lines.append("End of Report")
        return "\n".join(lines)

    def run(self) -> List[Dict[str, Any]]:
        """Run the file reference check."""
        if not self.agent_mode:
            logger.info("Starting file reference check...")
        
        modified_files_details = self._find_modified_files_git()
        if not modified_files_details:
            if not self.agent_mode:
                logger.info("No recently modified files found matching criteria.")
            return []

        reference_files = self._find_reference_files()
        if not reference_files:
            if not self.agent_mode:
                logger.warning("No reference files found to search within.")
            # Still process modified files to mark them as undocumented

        results = []
        for mod_file_detail in modified_files_details:
            file_path = mod_file_detail["path"]
            last_modified = mod_file_detail["last_modified_iso"]
            
            mentions = self._search_for_mentions(file_path, reference_files)
            status = "Documented" if mentions else "Undocumented"
            
            results.append({
                "file": os.path.relpath(file_path, self.repo_path),
                "last_modified": last_modified,
                "mentions": mentions,
                "status": status
            })

        if not self.agent_mode:
            logger.info(f"File reference check completed. Found {len(results)} relevant files.")

        if self.output_json_path:
            json_report = self._generate_report_json(results)
            try:
                os.makedirs(os.path.dirname(self.output_json_path), exist_ok=True)
                with open(self.output_json_path, 'w', encoding='utf-8') as f:
                    f.write(json_report)
                if not self.agent_mode:
                    logger.info(f"JSON report saved to {os.path.abspath(self.output_json_path)}")
            except IOError as e:
                if not self.agent_mode:
                    logger.error(f"Failed to save JSON report to {self.output_json_path}: {e}")

        if self.output_md_path:
            md_report = self._generate_report_markdown(results)
            try:
                os.makedirs(os.path.dirname(self.output_md_path), exist_ok=True)
                with open(self.output_md_path, 'w', encoding='utf-8') as f:
                    f.write(md_report)
                if not self.agent_mode:
                    logger.info(f"Markdown report saved to {os.path.abspath(self.output_md_path)}")
            except IOError as e:
                if not self.agent_mode:
                    logger.error(f"Failed to save Markdown report to {self.output_md_path}: {e}")
        
        if self.agent_mode:
            print(json.dumps(results)) # Output JSON to stdout for agent consumption
            
        return results

def main():
    parser = argparse.ArgumentParser(description="EGOS File Reference Checker.")
    parser.add_argument("repo_path", nargs="?", default=os.getcwd(), help="Path to the repository root (default: current directory).")
    parser.add_argument("--since", default=f"{DEFAULT_TIME_WINDOW_HOURS}h", help="Time window for modified files (e.g., '48h', '7d').")
    parser.add_argument("--exclude-dir", action="append", help="Directory to exclude (can be used multiple times).")
    parser.add_argument("--monitored-ext", action="append", help="File extension to monitor for modifications (e.g., '.py').")
    parser.add_argument("--reference-ext", action="append", help="File extension to search for references within (e.g., '.md').")
    parser.add_argument("--config-file", help="Path to a custom YAML/JSON configuration file.")
    parser.add_argument("--output-json", help="Path to save JSON report.")
    parser.add_argument("--output-md", help="Path to save Markdown report.")
    parser.add_argument("--agent-mode", action="store_true", help="Run in agent mode (prints JSON to stdout, minimal logging).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (DEBUG level) logging.")
    
    args = parser.parse_args()

    checker = FileReferenceChecker(
        repo_path=args.repo_path,
        since=args.since,
        exclude_dirs=args.exclude_dir,
        monitored_extensions=args.monitored_ext,
        reference_extensions=args.reference_ext,
        config_file_path=args.config_file,
        output_json_path=args.output_json,
        output_md_path=args.output_md,
        agent_mode=args.agent_mode,
    )

    if args.verbose and not args.agent_mode:
        logger.setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled.")

    checker.run()

if __name__ == "__main__":
    main()