#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cross-Reference Checker Ultra (Version 4.0.0)

Designed for extreme performance and advanced features in large projects.
Key aspects:
- Advanced exclusion system
- Optimized file scanning and reference finding
- Detailed performance monitoring and reporting
- Modular architecture for maintainability and scalability

@references:
- Previous Version: file_reference_checker_turbo.py
- Configuration: ./config_ultra.yaml
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import asyncio
import datetime
import fnmatch
import json
import logging
import os
import re
import time
import sys
import math
import shutil
import importlib.util
import string
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union, Any, Callable

import yaml # Assuming PyYAML is or will be installed

# Configure basic logging (will be enhanced by config)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("cross_reference_checker_ultra")

# Try to import pyahocorasick for efficient string matching
try:
    import pyahocorasick
    HAVE_AHOCORASICK = True
    logger.info("Using pyahocorasick for efficient multi-pattern matching")
except ImportError:
    HAVE_AHOCORASICK = False
    logger.info("pyahocorasick library not found, using fallback implementation")

DEFAULT_CONFIG_ULTRA_PATH = Path(__file__).parent / "config_ultra.yaml"

# Placeholder for future state/cache file
DEFAULT_CACHE_PATH = Path(__file__).parent / ".crossref_ultra_cache.json"


class ConfigLoaderUltra:
    """Loads and validates the ultra configuration file.
    
    Provides robust configuration loading, validation, and access for the
    Cross-Reference Checker Ultra. Ensures that all required configuration
    elements are present and properly formatted.
    """
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load()
        self._validate()

    def _load(self) -> Dict:
        """Load the YAML configuration file with error handling.
        
        Returns:
            Dict: The loaded configuration data
            
        Raises:
            SystemExit: If the file cannot be loaded or parsed
        """
        logger.info(f"Loading configuration from: {self.config_path}")
        if not self.config_path.is_file():
            logger.error(f"Configuration file not found: {self.config_path}")
            sys.exit(1)
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            logger.info("Configuration loaded successfully.")
            return config_data
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration file {self.config_path}: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error loading configuration {self.config_path}: {e}")
            sys.exit(1)
    
    def _validate(self) -> None:
        """Validate the configuration structure and values.
        
        Checks for required sections and parameters, and validates their types and values.
        
        Raises:
            SystemExit: If validation fails
        """
        # Check for required top-level sections
        required_sections = ['project_base_path', 'scan_parameters', 'reference_finding', 'reporting']
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Required configuration section '{section}' is missing")
                sys.exit(1)
        
        # Validate project_base_path
        project_path = Path(self.config['project_base_path'])
        if not project_path.exists() or not project_path.is_dir():
            logger.error(f"Project base path does not exist or is not a directory: {project_path}")
            sys.exit(1)
        
        # Validate scan_parameters
        scan_params = self.config['scan_parameters']
        if not isinstance(scan_params, dict):
            logger.error("'scan_parameters' must be a dictionary")
            sys.exit(1)
            
        # Check for scan directories
        if 'scan_directories' not in scan_params or not scan_params['scan_directories']:
            logger.error("No scan directories specified in 'scan_parameters.scan_directories'")
            sys.exit(1)
        
        # Validate reference_finding
        ref_finding = self.config['reference_finding']
        if not isinstance(ref_finding, dict):
            logger.error("'reference_finding' must be a dictionary")
            sys.exit(1)
            
        # Check for patterns
        if 'patterns' not in ref_finding or not ref_finding['patterns']:
            logger.error("No reference patterns specified in 'reference_finding.patterns'")
            sys.exit(1)
        
        # Validate reporting
        reporting = self.config['reporting']
        if not isinstance(reporting, dict):
            logger.error("'reporting' must be a dictionary")
            sys.exit(1)
            
        # Check output formats
        if 'output_formats' not in reporting or not reporting['output_formats']:
            logger.warning("No output formats specified in 'reporting.output_formats', defaulting to ['markdown']")
            reporting['output_formats'] = ['markdown']
        
        # Validate numeric values
        self._validate_numeric('scan_parameters.time_window_hours', 1, None)
        self._validate_numeric('scan_parameters.max_file_size_mb', 0, None)
        self._validate_numeric('reference_finding.file_processing_timeout_sec', 1, None)
        self._validate_numeric('reporting.report_retention_days', 0, None)
        
        logger.info("Configuration validation completed successfully.")
    
    def _validate_numeric(self, path: str, min_val: Optional[float], max_val: Optional[float]) -> None:
        """Validate a numeric configuration value.
        
        Args:
            path: Dot-notation path to the configuration value
            min_val: Minimum allowed value, or None for no minimum
            max_val: Maximum allowed value, or None for no maximum
        """
        value = self.get_nested(path)
        if value is None:
            return
            
        try:
            num_val = float(value)
            
            if min_val is not None and num_val < min_val:
                logger.warning(f"Configuration value '{path}' ({num_val}) is below minimum ({min_val}), using minimum")
                self._set_nested(path, min_val)
                
            if max_val is not None and num_val > max_val:
                logger.warning(f"Configuration value '{path}' ({num_val}) is above maximum ({max_val}), using maximum")
                self._set_nested(path, max_val)
                
        except (ValueError, TypeError):
            logger.error(f"Configuration value '{path}' must be a number")
            sys.exit(1)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a top-level configuration value.
        
        Args:
            key: The configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
    
    def get_nested(self, path: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation.
        
        Args:
            path: Dot-notation path to the configuration value (e.g., 'scan_parameters.time_window_hours')
            default: Default value if path is not found
            
        Returns:
            The configuration value or default
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
            
        return value
    
    def _set_nested(self, path: str, new_value: Any) -> None:
        """Set a nested configuration value using dot notation.
        
        Args:
            path: Dot-notation path to the configuration value
            new_value: The new value to set
        """
        keys = path.split('.')
        target = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
            
        # Set the value
        target[keys[-1]] = new_value


class ExclusionManagerUltra:
    """Manages advanced exclusion logic with caching.
    
    Provides a sophisticated system for determining which files and directories
    should be excluded from processing during different phases of the cross-reference
    checking process. Features include:
    - Pattern-based exclusions (regex, glob, literal paths)
    - Phase-specific exclusion rules
    - Decision caching for performance
    - Hierarchical exclusion handling
    """
    def __init__(self, config: Dict, project_base_path: Path):
        self.config = config
        self.project_base_path = project_base_path
        
        # Exclusion patterns by type
        self.excluded_dirs_abs: List[Path] = []
        self.excluded_regex_patterns: List[Tuple[re.Pattern, str]] = []  # (pattern, phase)
        self.excluded_glob_patterns: List[Tuple[str, str]] = []  # (pattern, phase)
        
        # Cache for exclusion decisions
        self.decision_cache: Dict[Tuple[str, Path], bool] = {}
        self.cache_enabled = self.config.get('exclusions', {}).get('cache_exclusions', True)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Compile all patterns
        self._compile_patterns()
        logger.info("ExclusionManagerUltra initialized with advanced pattern handling.")

    def _compile_patterns(self) -> None:
        """Compile exclusion patterns from configuration.
        
        Processes global exclusions and phase-specific exclusions, converting them
        to the appropriate pattern types (regex, glob, literal paths).
        """
        logger.debug("Compiling exclusion patterns...")
        
        # Process global exclusions (apply to all phases)
        global_exclusions = self.config.get("exclusions", {}).get("global", [])
        for item_str in global_exclusions:
            self._add_pattern(item_str, phase='all')
            
        # Process phase-specific exclusions
        phase_specific = self.config.get("exclusions", {}).get("phase_specific", {})
        for phase, patterns in phase_specific.items():
            if isinstance(patterns, list):
                # Simple list of patterns
                for pattern in patterns:
                    self._add_pattern(pattern, phase=phase)
            elif isinstance(patterns, dict):
                # Dictionary with pattern types and conditions
                for pattern_item in patterns:
                    if isinstance(pattern_item, dict) and 'pattern' in pattern_item:
                        pattern_type = pattern_item.get('type', 'auto')
                        pattern = pattern_item['pattern']
                        self._add_pattern(pattern, phase=phase, pattern_type=pattern_type)
        
        # Log pattern statistics
        logger.debug(f"Compiled exclusion patterns:")
        logger.debug(f"  - {len(self.excluded_dirs_abs)} absolute directory paths")
        logger.debug(f"  - {len(self.excluded_regex_patterns)} regex patterns")
        logger.debug(f"  - {len(self.excluded_glob_patterns)} glob patterns")

    def _add_pattern(self, pattern: str, phase: str = 'all', pattern_type: str = 'auto') -> None:
        """Add an exclusion pattern of the specified type.
        
        Args:
            pattern: The exclusion pattern string
            phase: The processing phase this pattern applies to ('all' for all phases)
            pattern_type: The pattern type ('auto', 'regex', 'glob', 'literal')
        """
        # Handle node_modules special case (common in projects)
        if pattern == 'node_modules':
            pattern = '**/node_modules/**'
            pattern_type = 'glob'
            
        # Determine pattern type if auto
        if pattern_type == 'auto':
            if any(c in pattern for c in ['*', '?', '[', ']']):
                pattern_type = 'glob'
            elif any(c in pattern for c in ['.', '^', '$', '(', ')', '\\', '+', '{', '}']):
                pattern_type = 'regex'
            else:
                pattern_type = 'literal'
        
        # Process based on pattern type
        if pattern_type == 'regex':
            try:
                compiled_pattern = re.compile(pattern)
                self.excluded_regex_patterns.append((compiled_pattern, phase))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                
        elif pattern_type == 'glob':
            # Convert ** glob patterns to regex for better performance
            if '**' in pattern:
                try:
                    # Convert glob with ** to regex
                    regex_pattern = pattern.replace('.', '\\.')
                    regex_pattern = regex_pattern.replace('**', '.*')
                    regex_pattern = regex_pattern.replace('*', '[^/\\\\]*')
                    regex_pattern = regex_pattern.replace('?', '.')
                    # Ensure pattern matches from start to end of the path
                    if not regex_pattern.startswith('^'):
                        regex_pattern = f"^{regex_pattern}"
                    if not regex_pattern.endswith('$'):
                        regex_pattern = f"{regex_pattern}$"
                    compiled_pattern = re.compile(regex_pattern)
                    self.excluded_regex_patterns.append((compiled_pattern, phase))
                except re.error as e:
                    logger.warning(f"Error converting glob pattern '{pattern}' to regex: {e}")
                    # Fall back to regular glob pattern
                    self.excluded_glob_patterns.append((pattern, phase))
            else:
                # Regular glob pattern without **
                self.excluded_glob_patterns.append((pattern, phase))
                
        elif pattern_type == 'literal':
            # Handle literal path (exact match or directory)
            path = (self.project_base_path / pattern).resolve()
            self.excluded_dirs_abs.append(path)

    def is_excluded(self, path: Path, phase: str = 'scan') -> bool:
        """Check if a path should be excluded based on configured patterns.
        
        Args:
            path: The path to check
            phase: The current processing phase
            
        Returns:
            bool: True if the path should be excluded, False otherwise
        """
        # Check cache first if enabled
        cache_key = (phase, path)
        if self.cache_enabled and cache_key in self.decision_cache:
            self.cache_hits += 1
            return self.decision_cache[cache_key]
        
        self.cache_misses += 1
        result = self._check_exclusion(path, phase)
        
        # Cache result if enabled
        if self.cache_enabled:
            self.decision_cache[cache_key] = result
            
        return result
    
    def _check_exclusion(self, path: Path, phase: str) -> bool:
        """Internal method to check if a path matches any exclusion pattern.
        
        Args:
            path: The path to check
            phase: The current processing phase
            
        Returns:
            bool: True if the path should be excluded, False otherwise
        """
        # Check absolute directory exclusions
        for excluded_dir in self.excluded_dirs_abs:
            if path == excluded_dir or excluded_dir in path.parents:
                return True
        
        # Convert to relative path for pattern matching
        try:
            rel_path_str = str(path.relative_to(self.project_base_path))
            
            # Check regex patterns
            for pattern, pattern_phase in self.excluded_regex_patterns:
                if pattern_phase == 'all' or pattern_phase == phase:
                    if pattern.search(rel_path_str):
                        return True
            
            # Check glob patterns
            for glob_pattern, pattern_phase in self.excluded_glob_patterns:
                if pattern_phase == 'all' or pattern_phase == phase:
                    if fnmatch.fnmatch(rel_path_str, glob_pattern):
                        return True
                    # Also check just the filename against the pattern
                    if fnmatch.fnmatch(path.name, glob_pattern):
                        return True
                        
        except ValueError:
            # Path is not relative to project_base_path
            # This could happen with symlinks or absolute paths outside the project
            # For safety, we don't exclude these by default
            pass
            
        return False

    def clear_cache(self) -> None:
        """Clear the exclusion decision cache."""
        if self.cache_enabled:
            cache_size = len(self.decision_cache)
            self.decision_cache.clear()
            logger.debug(f"Cleared exclusion cache containing {cache_size} entries.")
            logger.debug(f"Cache statistics - Hits: {self.cache_hits}, Misses: {self.cache_misses}")
            self.cache_hits = 0
            self.cache_misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the exclusion manager.
        
        Returns:
            Dict containing statistics about patterns and cache usage
        """
        return {
            "absolute_dirs_count": len(self.excluded_dirs_abs),
            "regex_patterns_count": len(self.excluded_regex_patterns),
            "glob_patterns_count": len(self.excluded_glob_patterns),
            "cache_enabled": self.cache_enabled,
            "cache_size": len(self.decision_cache) if self.cache_enabled else 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses
        }


class FileScannerUltra:
    """Optimized file and directory scanning.
    
    Provides high-performance scanning for recently modified files within the project,
    with support for various optimizations:
    - Aggressive directory pruning using the ExclusionManager
    - Efficient file traversal using os.walk with topdown=True
    - File size and extension filtering
    - Support for different modification detection methods
    """
    def __init__(self, config: Dict, project_base_path: Path, exclusion_manager: ExclusionManagerUltra):
        self.config = config
        self.project_base_path = project_base_path
        self.exclusion_manager = exclusion_manager
        
        # Configure from loaded configuration
        scan_params = self.config.get('scan_parameters', {})
        self.time_window_hours = scan_params.get('time_window_hours', 168)
        self.time_cutoff = datetime.datetime.now() - datetime.timedelta(hours=self.time_window_hours)
        
        # Process target extensions
        self.target_extensions = set()
        for ext in scan_params.get('target_file_extensions', []):
            # Ensure extensions start with a dot
            if not ext.startswith('.'):
                ext = f'.{ext}'
            self.target_extensions.add(ext.lower())
        
        # File size limits
        self.max_file_size = scan_params.get('max_file_size_mb', 10) * 1024 * 1024
        self.min_file_size = scan_params.get('min_file_size_bytes', 0)
        
        # Get modification detection method
        self.mod_detection = scan_params.get('modification_detection_method', 'mtime')
        if self.mod_detection not in ['mtime', 'git']:
            logger.warning(f"Unknown modification detection method: {self.mod_detection}, falling back to 'mtime'.")
            self.mod_detection = 'mtime'
            
        logger.info(f"FileScannerUltra initialized with {len(self.target_extensions)} target extensions and {self.time_window_hours}h window.")

    async def find_recently_modified_target_files(self) -> List[Path]:
        """Find recently modified files matching the target criteria.
        
        Uses an optimized directory traversal with early pruning of excluded directories
        and efficient filtering of files based on extension, size, and modification time.
        
        Returns:
            List[Path]: List of recently modified files matching the criteria
        """
        logger.info("Starting scan for recently modified target files...")
        perf_start = time.monotonic()
        modified_files = []
        
        # Process each scan directory from config
        scan_directories = self.config.get('scan_parameters', {}).get('scan_directories', ['.'])
        
        # Statistics for reporting
        dirs_processed = 0
        dirs_skipped = 0
        files_processed = 0
        files_skipped_exclusion = 0
        files_skipped_extension = 0
        files_skipped_size = 0
        files_skipped_time = 0
        
        for scan_dir_rel in scan_directories:
            scan_dir_abs = (self.project_base_path / scan_dir_rel).resolve()
            
            if not scan_dir_abs.is_dir():
                logger.warning(f"Scan directory does not exist or is not a directory: {scan_dir_abs}")
                dirs_skipped += 1
                continue
                
            if self.exclusion_manager.is_excluded(scan_dir_abs, phase='scan_root'):
                logger.debug(f"Skipping excluded scan root: {scan_dir_abs}")
                dirs_skipped += 1
                continue
                
            logger.debug(f"Scanning directory: {scan_dir_abs}")
            
            # Walk the directory tree efficiently
            for root, dirs, files in os.walk(scan_dir_abs, topdown=True):
                root_path = Path(root).resolve()
                dirs_processed += 1
                
                # Prune excluded directories BEFORE descending
                i = 0
                while i < len(dirs):
                    dir_path = (root_path / dirs[i]).resolve()
                    if self.exclusion_manager.is_excluded(dir_path, phase='scan_dir'):
                        logger.debug(f"Pruning excluded directory: {dir_path}")
                        dirs.pop(i)  # Skip this directory in traversal
                        dirs_skipped += 1
                    else:
                        i += 1
                
                # Process files in the current directory
                for file_name in files:
                    file_path = (root_path / file_name).resolve()
                    files_processed += 1
                    
                    # Skip excluded files early
                    if self.exclusion_manager.is_excluded(file_path, phase='scan_file'):
                        files_skipped_exclusion += 1
                        continue
                    
                    # Skip files with non-target extensions
                    if self.target_extensions and file_path.suffix.lower() not in self.target_extensions:
                        files_skipped_extension += 1
                        continue
                    
                    try:
                        # Check if file exists and is a regular file
                        if not file_path.is_file():
                            continue
                        
                        # Check file size
                        file_size = file_path.stat().st_size
                        if file_size < self.min_file_size or file_size > self.max_file_size:
                            files_skipped_size += 1
                            logger.debug(f"Skipping file due to size: {file_path} ({file_size} bytes)")
                            continue
                        
                        # Check modification time
                        if self.mod_detection == 'mtime':
                            modified_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                            if modified_time < self.time_cutoff:
                                files_skipped_time += 1
                                continue
                            
                            modified_files.append(file_path)
                            logger.debug(f"Found modified file: {file_path.relative_to(self.project_base_path)}")
                        elif self.mod_detection == 'git':
                            # TODO: Implement git-based modification detection
                            # This would check if the file was modified in git within the time window
                            # For now, fall back to mtime
                            modified_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                            if modified_time < self.time_cutoff:
                                files_skipped_time += 1
                                continue
                                
                            modified_files.append(file_path)
                            
                    except (FileNotFoundError, PermissionError) as e:
                        logger.debug(f"Error accessing file {file_path}: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error processing file {file_path}: {e}")
        
        # Log statistics
        perf_duration = time.monotonic() - perf_start
        logger.info(f"Scan completed in {perf_duration:.2f} seconds:")
        logger.info(f"  - Directories processed: {dirs_processed} (skipped: {dirs_skipped})")
        logger.info(f"  - Files processed: {files_processed}")
        logger.info(f"  - Files skipped due to exclusion: {files_skipped_exclusion}")
        logger.info(f"  - Files skipped due to extension: {files_skipped_extension}")
        logger.info(f"  - Files skipped due to size: {files_skipped_size}")
        logger.info(f"  - Files skipped due to modification time: {files_skipped_time}")
        logger.info(f"  - Found {len(modified_files)} modified target files")
        
        # Return sorted unique files
        return sorted(list(set(modified_files)))
        
    @staticmethod
    def is_likely_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
        """Determine if a file is likely binary by examining a sample.
        
        This is more reliable than just using the extension, as some text files may have
        non-standard extensions, and some binary files might have text-like extensions.
        
        Args:
            file_path: Path to the file to check
            sample_size: Number of bytes to sample from the beginning of the file
            
        Returns:
            bool: True if the file is likely binary, False otherwise
        """
        try:
            # Fast check: first look at extension
            binary_extensions = {'.exe', '.dll', '.so', '.pyc', '.pyo', '.o', '.obj',
                               '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
                               '.ico', '.zip', '.tar', '.gz', '.bz2', '.xz', '.rar',
                               '.7z', '.pdf', '.doc', '.docx', '.ppt', '.pptx',
                               '.xls', '.xlsx', '.bin', '.dat', '.db', '.sqlite'}
                               
            if file_path.suffix.lower() in binary_extensions:
                return True
                
            # Check file contents
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
                
            # Look for null bytes and high ratio of non-printable characters
            if b'\x00' in sample:
                return True
                
            # Check ratio of printable to non-printable characters
            import string
            printable = sum(c in bytes(string.printable, 'ascii') for c in sample)
            if len(sample) > 0 and printable / len(sample) < 0.7:  # If less than 70% is printable, assume binary
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error checking if file is binary {file_path}: {e}")
            return False  # Assume text file in case of error


class ReferenceFinderUltra:
    """Efficiently finds references using configured methods.
    
    Provides high-performance searching for references to files using either
    the Python built-in regex engine or external tools like ripgrep when available.
    Features include:
    - Parallel or asynchronous searching
    - Pattern substitution for customizable reference patterns
    - Robust binary file detection and skipping
    - Timeout handling for large files
    """
    def __init__(self, config: Dict, project_base_path: Path, exclusion_manager: ExclusionManagerUltra):
        self.config = config
        self.project_base_path = project_base_path
        self.exclusion_manager = exclusion_manager
        
        ref_config = self.config.get('reference_finding', {})
        
        # Configure search method
        self.search_method = ref_config.get('search_method', 'python_regex')
        if self.search_method == 'ripgrep':
            self.ripgrep_path = ref_config.get('ripgrep_path', 'rg')
            # Check if ripgrep is available
            try:
                import subprocess
                subprocess.run([self.ripgrep_path, '--version'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                logger.info(f"Ripgrep found at {self.ripgrep_path}")
            except (subprocess.SubprocessError, FileNotFoundError, ImportError):
                logger.warning("Ripgrep not found or not working, falling back to python_regex")
                self.search_method = 'python_regex'
        
        # Configure patterns
        self.patterns = ref_config.get('patterns', ['{filename}'])
        self.resolve_python_modules = ref_config.get('resolve_python_modules', True)
        
        # Configure file processing
        self.timeout_sec = ref_config.get('file_processing_timeout_sec', 60)
        self.max_line_length = ref_config.get('max_line_length_for_reference_content', 500)
        
        # Configure where to search
        search_dirs_config = ref_config.get('search_in_directories', ['.'])
        self.search_dirs_abs = []
        for rel_path in search_dirs_config:
            abs_path = (self.project_base_path / rel_path).resolve()
            if abs_path.exists():
                self.search_dirs_abs.append(abs_path)
            else:
                logger.warning(f"Search directory does not exist: {abs_path}")
        
        # Configure which files to search in
        self.search_extensions = set()
        for ext in ref_config.get('search_in_file_extensions', []):
            if not ext.startswith('.'):
                ext = f'.{ext}'
            self.search_extensions.add(ext.lower())
            
        logger.info(f"ReferenceFinderUltra initialized using {self.search_method} method with {len(self.patterns)} patterns.")

    async def find_references_to_file(self, target_file: Path) -> List[Dict]:
        """Find references to a target file in other project files.
        
        Args:
            target_file: Path to the file to find references to
            
        Returns:
            List[Dict]: List of reference objects with details about where references were found
        """
        logger.debug(f"Finding references for: {target_file.relative_to(self.project_base_path)}")
        perf_start = time.monotonic()
        
        # Generate search terms based on patterns
        search_terms = self._generate_search_terms(target_file)
        if not search_terms:
            logger.warning(f"No search terms generated for {target_file}")  
            return []
            
        # Find files to search in
        files_to_search = await self._find_files_to_search_in()
        
        # Execute the search based on configured method
        if self.search_method == 'ripgrep':
            references = await self._find_references_ripgrep(target_file, search_terms, files_to_search)
        else:
            references = await self._find_references_python(target_file, search_terms, files_to_search)
            
        # Log performance metrics
        perf_duration = time.monotonic() - perf_start
        logger.info(f"Reference search for {target_file.name} completed in {perf_duration:.2f} seconds")
        logger.info(f"  - Search terms: {len(search_terms)}")
        logger.info(f"  - Files searched: {len(files_to_search)}")
        logger.info(f"  - References found: {len(references)}")
        
        return references
    
    def _generate_search_terms(self, target_file: Path) -> List[str]:
        """Generate search terms for a target file based on configured patterns.
        
        Args:
            target_file: The file to generate search terms for
            
        Returns:
            List[str]: List of search terms
        """
        search_terms = []
        target_filename = target_file.name
        
        try:
            target_relpath = str(target_file.relative_to(self.project_base_path))
        except ValueError:
            target_relpath = str(target_file)
        
        for pattern in self.patterns:
            # Replace {filename}
            if '{filename}' in pattern:
                search_terms.append(pattern.replace('{filename}', target_filename))
                
            # Replace {filepath_relative}
            if '{filepath_relative}' in pattern:
                search_terms.append(pattern.replace('{filepath_relative}', target_relpath))
                
            # Handle Python module imports
            if self.resolve_python_modules and target_file.suffix.lower() == '.py':
                module_name = target_filename[:-3]  # Remove .py extension
                
                if '{module_name}' in pattern:
                    # Simple module name
                    search_terms.append(pattern.replace('{module_name}', module_name))
                    
                    # Package module paths
                    try:
                        rel_path = target_file.relative_to(self.project_base_path)
                        parent_path = rel_path.parent
                        
                        if parent_path != Path('.'):
                            # Convert path to module path format
                            package_path = str(parent_path).replace('/', '.').replace('\\', '.')
                            package_module = f"{package_path}.{module_name}"
                            search_terms.append(pattern.replace('{module_name}', package_module))
                            
                            # Also check for parent imports
                            parts = package_path.split('.')
                            for i in range(1, len(parts) + 1):
                                partial_path = '.'.join(parts[:i])
                                if partial_path:
                                    search_terms.append(pattern.replace('{module_name}', 
                                                                      f"{partial_path}.{module_name}"))
                    except ValueError:
                        pass  # Skip if we can't get a relative path
        
        # Remove any duplicates and empty strings
        unique_terms = list(set(filter(None, search_terms)))
        
        if unique_terms:
            logger.debug(f"Generated {len(unique_terms)} search terms for {target_filename}")
        
        return unique_terms
    
    async def _find_files_to_search_in(self) -> List[Path]:
        """Find files to search for references in.
        
        Returns:
            List[Path]: List of files to search in
        """
        files_to_search = []
        
        for search_dir in self.search_dirs_abs:
            if search_dir.is_file():
                if not self.exclusion_manager.is_excluded(search_dir, phase='reference_search_target'):
                    if not self.search_extensions or search_dir.suffix.lower() in self.search_extensions:
                        files_to_search.append(search_dir)
            elif search_dir.is_dir():
                # Walk the directory
                for root, dirs, files in os.walk(search_dir, topdown=True):
                    root_path = Path(root).resolve()
                    
                    # Prune excluded directories
                    dirs[:] = [d for d in dirs if not self.exclusion_manager.is_excluded(
                        (root_path / d).resolve(), phase='reference_search_target')]
                    
                    # Process files
                    for file_name in files:
                        file_path = (root_path / file_name).resolve()
                        
                        if self.exclusion_manager.is_excluded(file_path, phase='reference_search_content'):
                            continue
                            
                        if not self.search_extensions or file_path.suffix.lower() in self.search_extensions:
                            files_to_search.append(file_path)
        
        logger.debug(f"Found {len(files_to_search)} files to search in")
        return files_to_search
    
    async def _find_references_python(self, target_file: Path, search_terms: List[str], 
                                    files_to_search: List[Path]) -> List[Dict]:
        """Find references using efficient string matching algorithms.
        
        Args:
            target_file: File to find references to
            search_terms: List of search terms to look for
            files_to_search: List of files to search in
            
        Returns:
            List[Dict]: List of reference objects
        """
        references = []
        
        # Create a progress display
        file_count = len(files_to_search)
        progress = ProgressDisplay(total=file_count, 
                                  desc=f"Searching refs to {target_file.name}", 
                                  unit="files")
        
        # Select pattern matcher based on available libraries and pattern count
        if HAVE_AHOCORASICK and len(search_terms) > 3:
            # Use Aho-Corasick for efficient multi-pattern matching
            pattern_matcher = self._build_ahocorasick_automaton(search_terms)
            matcher_type = 'ahocorasick'
        else:
            # Fall back to regex for simpler cases or when pyahocorasick is not available
            import re
            pattern_matcher = [re.compile(re.escape(term)) for term in search_terms]
            matcher_type = 'regex'
        
        # Process each file
        files_processed = 0
        files_with_refs = 0
        files_skipped = 0
        
        # Get performance monitor for timing
        perf_monitor = getattr(self, 'perf_monitor', None)
        
        # Process each file
        for file_path in files_to_search:
            files_processed += 1
            
            # Update progress every 10 files
            if files_processed % 10 == 0 or files_processed == file_count:
                progress.update(files_processed)
            
            # Skip self-references
            if file_path.resolve() == target_file.resolve():
                files_skipped += 1
                continue
                
            try:
                # Skip large files
                file_size = file_path.stat().st_size
                if file_size > 5 * 1024 * 1024:  # 5 MB limit
                    logger.debug(f"Skipping large file: {file_path} ({file_size / 1024 / 1024:.1f} MB)")
                    files_skipped += 1
                    continue
                
                # Skip binary files
                if FileScannerUltra.is_likely_binary_file(file_path):
                    logger.debug(f"Skipping binary file: {file_path}")
                    files_skipped += 1
                    continue
                
                # Process with timeout
                file_start_time = time.monotonic()
                file_refs = await self._process_file_with_timeout(file_path, pattern_matcher, matcher_type)
                file_duration = time.monotonic() - file_start_time
                
                # Record processing time if we have a performance monitor
                if perf_monitor:
                    perf_monitor.record_file_processing(file_path, file_duration)
                
                if file_refs:
                    references.extend(file_refs)
                    files_with_refs += 1
                    
            except Exception as e:
                logger.warning(f"Error processing file {file_path}: {e}")
                files_skipped += 1
        
        # Finish progress display
        progress.finish(f"Found {len(references)} refs in {files_with_refs} files")
        
        return references
        
    def _build_ahocorasick_automaton(self, search_terms: List[str]):
        """Build an Aho-Corasick automaton for efficient multi-pattern matching.
        
        Args:
            search_terms: List of search terms to build the automaton from
            
        Returns:
            An Aho-Corasick automaton object
        """
        # Create a new Aho-Corasick automaton
        automaton = pyahocorasick.Automaton()
        
        # Add each pattern to the automaton with its index as the value
        for idx, term in enumerate(search_terms):
            automaton.add_string(term.encode('utf-8'), (idx, term))
        
        # Finalize the automaton for searching
        automaton.make_automaton()
        
        return automaton
    
    async def _find_references_ripgrep(self, target_file: Path, search_terms: List[str], 
                                       files_to_search: List[Path]) -> List[Dict]:
        """Find references using the ripgrep command-line tool.
        
        Args:
            target_file: File to find references to
            search_terms: List of search terms to look for
            files_to_search: List of files to search in
            
        Returns:
            List[Dict]: List of reference objects
        """
        results = []
        
        # Check if ripgrep is available
        if not shutil.which(self.ripgrep_path):
            logger.warning(f"Ripgrep not found at {self.ripgrep_path}, falling back to Python regex")
            return await self._find_references_python(target_file, search_terms, files_to_search)
        
        # Create a progress display
        progress = ProgressDisplay(total=len(search_terms), 
                                  desc=f"Ripgrep search for {target_file.name}", 
                                  unit="patterns")
        
        # Optimize search by grouping files by extension
        files_by_ext = {}
        for file_path in files_to_search:
            ext = file_path.suffix.lower()
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file_path)
        
        # Create a temporary directory for file lists by extension
        temp_dir = tempfile.mkdtemp(prefix="crossref_rg_")
        temp_files = {}
        
        try:
            # Create a file list for each extension group
            for ext, files in files_by_ext.items():
                temp_file_path = os.path.join(temp_dir, f"files{ext}.txt")
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    for file_path in files:
                        f.write(f"{file_path}\n")
                temp_files[ext] = temp_file_path
            
            # Process each search term
            for term_idx, term in enumerate(search_terms):
                progress.update(term_idx + 1, desc=f"Searching for '{term[:20]}...'")
                
                # Process each extension group
                for ext, temp_file_path in temp_files.items():
                    # Build optimized ripgrep command
                    cmd = [
                        self.ripgrep_path,
                        "--files-from", temp_file_path,
                        "--line-number",
                        "--with-filename",
                        "--no-heading",
                        "--color", "never",
                        "--max-columns", str(self.max_line_length),
                        "-i",  # Case-insensitive
                    ]
                    
                    # Add extension-specific optimizations
                    if ext == ".py":
                        cmd.extend(["--type", "py"])
                    elif ext == ".md":
                        cmd.extend(["--type", "markdown"])
                    
                    # Add the search term (properly escaped)
                    cmd.append(term)
                    
                    # Run ripgrep with optimized settings
                    try:
                        process = subprocess.run(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            timeout=self.timeout_sec,
                            text=True,
                            check=False
                        )
                        
                        if process.returncode not in [0, 1]:  # 0=matches found, 1=no matches
                            logger.warning(f"Ripgrep error for {ext} files: {process.stderr}")
                            continue
                        
                        # Parse results
                        for line in process.stdout.splitlines():
                            parts = line.split(':', 2)
                            if len(parts) >= 3:
                                file_path, line_num, content = parts
                                results.append({
                                    'file_path': file_path,
                                    'line_number': int(line_num),
                                    'content': content.strip(),
                                    'search_term': term,
                                    'target_file': str(target_file)
                                })
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Ripgrep timed out after {self.timeout_sec}s for term '{term}' on {ext} files")
                    except Exception as e:
                        logger.warning(f"Error running ripgrep for term '{term}' on {ext} files: {e}")
            
            # Finish progress display
            progress.finish(f"Found {len(results)} references using ripgrep")
                
        finally:
            # Clean up temporary files
            try:
                for temp_file in temp_files.values():
                    os.unlink(temp_file)
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary files: {e}")
                
        return results
    
    async def _process_file_with_timeout(self, file_path: Path, patterns, matcher_type: str = 'regex') -> List[Dict]:
        """Process a file with timeout.
        
        Args:
            file_path: Path to the file to process
            patterns: Either a list of compiled regex patterns or an Aho-Corasick automaton
            matcher_type: Type of pattern matcher ('regex' or 'ahocorasick')
            
        Returns:
            List[Dict]: List of reference objects found in the file
        """
        # Create a task for processing the file
        try:
            # Create a task for file processing based on matcher type
            if matcher_type == 'ahocorasick':
                process_task = asyncio.create_task(self._process_file_ahocorasick(file_path, patterns))
            else:
                process_task = asyncio.create_task(self._process_file(file_path, patterns))
                
            # Wait for the task to complete with a timeout
            return await asyncio.wait_for(process_task, timeout=self.timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout processing file: {file_path} (exceeded {self.timeout_sec} seconds)")
            return []
        except Exception as e:
            logger.warning(f"Error processing file with timeout {file_path}: {e}")
            return []
    
    async def _process_file(self, file_path: Path, patterns: List[re.Pattern]) -> List[Dict]:
        """Process a file to find references using regex patterns.
        
        Args:
            file_path: Path to the file to process
            patterns: List of compiled regex patterns to search for
            
        Returns:
            List[Dict]: List of reference objects found in the file
        """
        references = []
        
        try:
            rel_path = str(file_path.relative_to(self.project_base_path))
        except ValueError:
            rel_path = str(file_path)
        
        # Use file content cache if available
        file_content_cache = getattr(self, 'file_content_cache', None)
        cache_key = str(file_path)
        lines = None
        
        try:
            # Check if we have this file in cache
            if file_content_cache is not None and cache_key in file_content_cache:
                lines = file_content_cache[cache_key]
            else:
                # Read the file and cache its content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()
                    
                    # Cache the file content if cache is available
                    if file_content_cache is not None:
                        file_content_cache[cache_key] = lines
                        
                except UnicodeDecodeError:
                    # This is likely a binary file that wasn't caught earlier
                    logger.debug(f"Unicode decode error in file {file_path}, possibly binary")
                    return references
            
            # Process the file lines
            if lines:
                for line_num, line_content in enumerate(lines, 1):
                    # Check each pattern
                    for pattern in patterns:
                        if pattern.search(line_content):
                            # Found a match
                            references.append({
                                'found_in_file': rel_path,
                                'line_number': line_num,
                                'line_content': line_content.strip()[:self.max_line_length]
                            })
                            # Only record the first match per line
                            break
                            
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")
            
        return references
        
    async def _process_file_ahocorasick(self, file_path: Path, automaton) -> List[Dict]:
        """Process a file to find references using Aho-Corasick algorithm.
        
        Args:
            file_path: Path to the file to process
            automaton: Aho-Corasick automaton initialized with patterns
            
        Returns:
            List[Dict]: List of reference objects found in the file
        """
        references = []
        
        try:
            rel_path = str(file_path.relative_to(self.project_base_path))
        except ValueError:
            rel_path = str(file_path)
        
        # Use file content cache if available
        file_content_cache = getattr(self, 'file_content_cache', None)
        cache_key = str(file_path)
        file_content = None
        
        try:
            # For Aho-Corasick, we need the whole file content as a single string
            # Check if we have this file in cache
            if file_content_cache is not None and cache_key in file_content_cache:
                # Convert cached lines back to full text
                lines = file_content_cache[cache_key]
                file_content = ''.join(lines)
            else:
                # Read the file and cache its content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()
                        file_content = ''.join(lines)
                    
                    # Cache the file content if cache is available
                    if file_content_cache is not None:
                        file_content_cache[cache_key] = lines
                        
                except UnicodeDecodeError:
                    # This is likely a binary file that wasn't caught earlier
                    logger.debug(f"Unicode decode error in file {file_path}, possibly binary")
                    return references
            
            # Process the file content using Aho-Corasick
            if file_content:
                # Convert file content to bytes for pyahocorasick
                content_bytes = file_content.encode('utf-8', errors='replace')
                
                # Find all matches
                matches = []
                for end_idx, (pattern_idx, pattern) in automaton.iter(content_bytes):
                    start_idx = end_idx - len(pattern) + 1
                    matches.append((start_idx, end_idx, pattern_idx, pattern))
                
                # If we found matches, convert them to line numbers
                if matches:
                    # Create line index for mapping byte offsets to line numbers
                    line_starts = [0]  # Start of first line
                    line_idx = 0
                    for i, char in enumerate(file_content):
                        if char == '\n':
                            line_idx += 1
                            line_starts.append(i + 1)  # Start of next line
                    
                    # Process each match
                    for start_idx, end_idx, pattern_idx, pattern in matches:
                        # Find which line this match is on
                        line_num = 1  # Default to first line
                        for i, offset in enumerate(line_starts):
                            if offset <= start_idx:
                                line_num = i + 1
                            else:
                                break
                        
                        # Extract the matching line
                        line_start = line_starts[line_num - 1]
                        next_line = line_starts[line_num] if line_num < len(line_starts) else len(file_content)
                        line_content = file_content[line_start:next_line]
                        
                        # Add reference
                        references.append({
                            'found_in_file': rel_path,
                            'line_number': line_num,
                            'line_content': line_content.strip()[:self.max_line_length]
                        })
                            
        except Exception as e:
            logger.warning(f"Error processing file with Aho-Corasick {file_path}: {e}")
            
        return references


class ReportGeneratorUltra:
    """Generates detailed reports including performance metrics."""
    def __init__(self, config: Dict, project_base_path: Path):
        self.config = config
        self.project_base_path = project_base_path
        logger.info("ReportGeneratorUltra initialized.")

    def generate_reports(self, processed_data: List[Dict], performance_metrics: Dict):
        # TODO: Implement generation of Markdown, JSON reports
        # TODO: Include detailed performance section
        logger.info("Generating reports...")
        output_formats = self.config.get("reporting", {}).get("output_formats", ["markdown"])
        output_filename_base = self.config.get("reporting", {}).get("output_filename_base", "cross_reference_ultra_report")
        script_dir = Path(__file__).resolve().parent
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        report_content_json = {
            "report_generated_at": datetime.datetime.now().isoformat(),
            "project_base_path": str(self.project_base_path),
            "files_analyzed_count": len(processed_data),
            "performance_metrics": performance_metrics,
            "reference_data": processed_data
        }

        if "json" in output_formats:
            json_path = script_dir / f"{output_filename_base}_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_content_json, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON report generated: {json_path}")

        if "markdown" in output_formats:
            # Basic Markdown structure
            md_lines = [
                f"# Cross-Reference Ultra Report - {timestamp}",
                f"## Performance Metrics",
                json.dumps(performance_metrics, indent=2),
                f"## Reference Details ({len(processed_data)} files analyzed)"
            ]
            for item in processed_data:
                md_lines.append(f"### File: `{item.get('file_path', 'N/A')}`")
                if item.get('references_found'):
                    for ref in item['references_found']:
                        md_lines.append(f"  - Found in: `{ref.get('found_in_file', 'N/A')}` L{ref.get('line_number', 'N/A')}: `{ref.get('line_content', '')[:100]}`")
                else:
                    md_lines.append("  - No references found or processed.")
            
            md_path = script_dir / f"{output_filename_base}_{timestamp}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(md_lines))
            logger.info(f"Markdown report generated: {md_path}")
        
        # TODO: Report retention logic


class ProgressDisplay:
    """Beautiful progress display for terminal output.
    
    Provides an aesthetic yet informative progress display with customizable styling,
    estimated time remaining, and current status information.
    """
    def __init__(self, total: int = 0, desc: str = "", unit: str = "items", refresh_rate: float = 0.5):
        self.total = total
        self.completed = 0
        self.desc = desc
        self.unit = unit
        self.refresh_rate = refresh_rate
        self.start_time = time.monotonic()
        self.last_update_time = 0
        self.last_printed_len = 0
        self.terminal_width = shutil.get_terminal_size().columns
        
        # Style elements (minimalist, cross-platform friendly)
        self.symbols = {
            'start': '│',
            'filled': '█',
            'empty': '░',
            'end': '│'
        }
        
        # Colors (if terminal supports it, otherwise use plain text)
        self.use_colors = True
        try:
            # Quick test for color support
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            self.use_colors = False
            
        self.colors = {
            'title': '\033[1;36m' if self.use_colors else '',  # Cyan, bold
            'progress': '\033[1;34m' if self.use_colors else '',  # Blue, bold
            'stats': '\033[0;37m' if self.use_colors else '',    # Light gray
            'time': '\033[0;33m' if self.use_colors else '',     # Yellow
            'reset': '\033[0m' if self.use_colors else ''        # Reset
        }
        
        if total > 0:
            self.start()
    
    def start(self):
        """Display the initial progress bar."""
        self.start_time = time.monotonic()
        self.update(0)
    
    def update(self, completed: Optional[int] = None, desc: Optional[str] = None, force: bool = False):
        """Update the progress display.
        
        Args:
            completed: Number of items completed (if None, increments by 1)
            desc: New description (if None, keeps current)
            force: Force update even if refresh_rate hasn't elapsed
        """
        current_time = time.monotonic()
        
        # Update internal state
        if completed is not None:
            self.completed = completed
        else:
            self.completed += 1
            
        if desc is not None:
            self.desc = desc
            
        # Check if we should refresh the display
        if not force and (current_time - self.last_update_time < self.refresh_rate) and self.completed < self.total:
            return
            
        self.last_update_time = current_time
        
        # Calculate metrics
        progress = min(1.0, self.completed / max(1, self.total))
        elapsed = current_time - self.start_time
        rate = self.completed / max(0.1, elapsed)  # items per second
        
        if rate > 0 and self.completed < self.total:
            eta = (self.total - self.completed) / rate
            eta_str = self._format_time(eta)
        else:
            eta_str = "--:--"
            
        # Format the progress bar
        bar_width = min(50, self.terminal_width - 40)  # Ensure it fits
        filled_width = math.floor(progress * bar_width)
        empty_width = bar_width - filled_width
        
        bar = f"{self.symbols['start']}{self.colors['progress']}{self.symbols['filled'] * filled_width}{self.symbols['empty'] * empty_width}{self.colors['reset']}{self.symbols['end']}"
        
        percent = f"{int(progress * 100):3d}%"
        count = f"{self.completed}/{self.total}"
        time_display = f"{self.colors['time']}ETA: {eta_str}{self.colors['reset']} [{self._format_time(elapsed)} elapsed]"
        
        # Build status line with description
        if len(self.desc) > 30:
            display_desc = self.desc[:27] + "..."
        else:
            display_desc = self.desc
            
        status = f"{self.colors['title']}{display_desc}{self.colors['reset']} {bar} {percent} {self.colors['stats']}({count} {self.unit}) {time_display}{self.colors['reset']}"
        
        # Clear previous line and print new status
        if self.last_printed_len > 0:
            sys.stdout.write('\r' + ' ' * self.last_printed_len + '\r')
            
        sys.stdout.write('\r' + status)
        sys.stdout.flush()
        self.last_printed_len = len(status) - (len(''.join(self.colors.values())) if self.use_colors else 0)
    
    def finish(self, final_desc: Optional[str] = None):
        """Complete the progress display with a final message."""
        if final_desc:
            self.desc = final_desc
        self.update(self.total, force=True)
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{int(minutes)}m {int(seconds % 60)}s"
        else:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            return f"{int(hours)}h {int(minutes)}m"


class PerformanceMonitorUltra:
    """Tracks and logs performance metrics.
    
    Provides detailed tracking of execution phases, timing, and resource usage
    to help identify bottlenecks and optimize performance.
    """
    def __init__(self):
        self.start_time = time.monotonic()
        self.phase_timings: Dict[str, float] = {}
        self.phase_end_times: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {}
        self.current_phase = None
        self.file_processing_stats = {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'times': []
        }
        logger.info("PerformanceMonitorUltra initialized.")
    
    def start_phase(self, phase_name: str):
        """Start timing a new execution phase."""
        self.current_phase = phase_name
        self.phase_timings[phase_name] = time.monotonic()
        logger.info(f"Starting phase: {phase_name}")
        
        # Create beautiful separator for readability
        if self.is_interactive():
            width = shutil.get_terminal_size().columns
            print(f"\n{'─' * width}")
            print(f"✧ {phase_name.upper()} PHASE STARTED ✧")
            print(f"{'─' * width}\n")
    
    def end_phase(self, phase_name: str):
        """End timing for a phase and record metrics."""
        if phase_name in self.phase_timings:
            end_time = time.monotonic()
            self.phase_end_times[phase_name] = end_time
            duration = end_time - self.phase_timings[phase_name]
            self.metrics[f"phase_{phase_name}_duration_sec"] = round(duration, 3)
            logger.info(f"Completed phase: {phase_name} in {duration:.3f} seconds.")
            
            # Print summary if interactive
            if self.is_interactive():
                width = shutil.get_terminal_size().columns
                print(f"\n{'─' * width}")
                print(f"✧ {phase_name.upper()} PHASE COMPLETED in {duration:.1f}s ✧")
                print(f"{'─' * width}\n")
        else:
            logger.warning(f"Attempted to end phase '{phase_name}' which was not started.")
    
    def record_metric(self, name: str, value: Any):
        """Record a performance metric."""
        self.metrics[name] = value
        logger.debug(f"Metric recorded: {name} = {value}")
    
    def record_file_processing(self, file_path: Path, duration: float):
        """Record statistics about individual file processing."""
        self.file_processing_stats['count'] += 1
        self.file_processing_stats['total_time'] += duration
        self.file_processing_stats['min_time'] = min(self.file_processing_stats['min_time'], duration)
        self.file_processing_stats['max_time'] = max(self.file_processing_stats['max_time'], duration)
        self.file_processing_stats['times'].append((str(file_path), duration))
    
    def get_estimated_time_remaining(self, items_processed: int, total_items: int) -> float:
        """Estimate remaining time based on current phase and progress."""
        if not self.current_phase or items_processed == 0 or total_items == 0:
            return float('inf')
            
        current_time = time.monotonic()
        elapsed = current_time - self.phase_timings.get(self.current_phase, self.start_time)
        rate = items_processed / max(0.001, elapsed)  # items per second
        remaining_items = total_items - items_processed
        
        return remaining_items / rate if rate > 0 else float('inf')
    
    def get_phase_duration(self, phase_name: str) -> float:
        """Get the duration of a specific phase in seconds."""
        if phase_name not in self.phase_timings:
            return 0.0
            
        if phase_name in self.phase_end_times:
            return self.phase_end_times[phase_name] - self.phase_timings[phase_name]
        else:
            # Phase still running
            return time.monotonic() - self.phase_timings[phase_name]
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            str: Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
    
    def get_summary(self) -> Dict:
        """Get a comprehensive summary of all recorded metrics."""
        end_time = time.monotonic()
        total_time = end_time - self.start_time
        
        # Prepare summary
        summary = {
            'total_execution_time_sec': total_time,
            'total_execution_time_formatted': self._format_time(total_time),
            'phases': {},
            'metrics': self.metrics,
            'file_processing': {
                'count': self.file_processing_stats['count'],
                'total_time': self.file_processing_stats['total_time'],
                'avg_time': self.file_processing_stats['total_time'] / self.file_processing_stats['count'] if self.file_processing_stats['count'] > 0 else 0,
                'min_time': self.file_processing_stats['min_time'] if self.file_processing_stats['min_time'] != float('inf') else 0,
                'max_time': self.file_processing_stats['max_time']
            }
        }
        
        # Add phase timings
        for phase, start_time in self.phase_timings.items():
            end_time = self.phase_end_times.get(phase, time.monotonic())
            duration = end_time - start_time
            summary['phases'][phase] = {
                'duration_sec': duration,
                'duration_formatted': self._format_time(duration),
                'percentage': (duration / total_time * 100) if total_time > 0 else 0
            }
            
        return summary
    
    def is_interactive(self) -> bool:
        """Check if script is running in an interactive terminal."""
        # Check if running in a terminal
        if hasattr(sys, 'ps1'):
            return True
        
        # Check if running in a notebook
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                return True
        except (ImportError, NameError):
            pass
            
        # Check if stdin is a tty
        return sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else False


async def run_checker(config: Dict):
    """Main asynchronous orchestrator for the checker."""
    project_base_path = Path(config.get("project_base_path", ".")).resolve()
    perf_monitor = PerformanceMonitorUltra()

    perf_monitor.start_phase("initialization")
    exclusion_mgr = ExclusionManagerUltra(config, project_base_path)
    file_scanner = FileScannerUltra(config, project_base_path, exclusion_mgr)
    ref_finder = ReferenceFinderUltra(config, project_base_path, exclusion_mgr)
    # Share performance monitor with the reference finder for detailed timing
    ref_finder.perf_monitor = perf_monitor
    report_gen = ReportGeneratorUltra(config, project_base_path)
    perf_monitor.end_phase("initialization")

    perf_monitor.start_phase("find_target_files")
    target_files = await file_scanner.find_recently_modified_target_files()
    perf_monitor.record_metric("target_files_found_count", len(target_files))
    perf_monitor.end_phase("find_target_files")

    if not target_files:
        logger.info("No target files found to process.")
        report_gen.generate_reports([], perf_monitor.get_summary())
        return
    
    # Check for quick test mode
    # Apply quick test mode if configured (limit to exactly 3 files for testing)
    quick_test = config.get('performance', {}).get('quick_test', False)
    if quick_test:
        logger.info("Quick test mode enabled - limiting to exactly 3 files for faster testing")
        # Limit to exactly 3 files for quick testing
        import random
        random.seed(42)  # For reproducible test results
        if len(target_files) > 3:
            target_files = random.sample(target_files, min(3, len(target_files)))
            logger.info(f"Quick test mode: Selected {len(target_files)} files randomly")
        logger.info(f"⚡ This is just a functionality test. For real analysis, run without --quick-test")
    else:
        # Apply hierarchical priority processing if configured
        hierarchical_priority = config.get('performance', {}).get('hierarchical_priority', False)
        reference_frequency_weighting = config.get('performance', {}).get('reference_frequency_weighting', False)
        
        if hierarchical_priority and reference_frequency_weighting:
            logger.info("🔄 Applying hierarchical priority processing based on reference frequency")
            
            # First pass: count references to each file
            reference_counts = {}
            reference_finder = ReferenceFinderUltra(config, project_base_path, exclusion_mgr)
            
            # Sample a subset of files to analyze for references (for efficiency)
            sample_size = min(50, len(target_files))
            sample_files = random.sample(target_files, sample_size) if len(target_files) > sample_size else target_files
            
            for file_path in sample_files:
                try:
                    # Find files that reference this file
                    refs = reference_finder.find_references_to_file(file_path)
                    # Count references for each file
                    for ref in refs:
                        ref_file = ref.get('file_path', None)
                        if ref_file:
                            reference_counts[ref_file] = reference_counts.get(ref_file, 0) + 1
                except Exception as e:
                    logger.warning(f"Error counting references for {file_path}: {e}")
            
            # Sort target files by reference count (highest first)
            target_files.sort(key=lambda f: reference_counts.get(str(f), 0), reverse=True)
            
            # Log the top 10 files by reference count
            top_files = [(f, reference_counts.get(str(f), 0)) for f in target_files[:10]]
            logger.info(f"Top files by reference count: {top_files}")
            logger.info(f"Prioritized {len(target_files)} files based on reference frequency")
        
        # Check for partial run configuration
        partial_run_percentage = config.get('performance', {}).get('partial_run_percentage', 100)
        if partial_run_percentage < 100:
            # Process only a percentage of files
            target_count = len(target_files)
            process_count = max(1, int(target_count * partial_run_percentage / 100))
            target_files = target_files[:process_count]
            logger.info(f"🔍 PARTIAL RUN: Processing {process_count} files ({partial_run_percentage}%) out of {target_count} total files")
        
        # Check for checkpoint continuation
        checkpoint_file = Path(config.get('reporting', {}).get('checkpoint_path', 'reports/cross_reference/checkpoint.json'))
        continue_from_checkpoint = config.get('performance', {}).get('continue_from_checkpoint', False)
        
        if continue_from_checkpoint and checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                    
                processed_files = set(checkpoint_data.get('processed_files', []))
                logger.info(f"📋 Continuing from checkpoint: {len(processed_files)} files already processed")
                
                # Filter out already processed files
                target_files = [f for f in target_files if str(f) not in processed_files]
                logger.info(f"📋 Remaining files to process: {len(target_files)}")
                
            except Exception as e:
                logger.warning(f"Failed to load checkpoint data: {e}")
                logger.warning("Proceeding with normal processing")
        
        # Apply partial run percentage if specified
        if partial_run_percentage < 100:
            original_count = len(target_files)
            partial_count = max(1, int(original_count * partial_run_percentage / 100))
            target_files = target_files[:partial_count]
            logger.info(f"🔍 PARTIAL ANALYSIS MODE: Processing {partial_run_percentage}% ({partial_count}/{original_count} files)")
            logger.info(f"🔍 To process more files later, use --continue-from-checkpoint")
    
    # Set up checkpoint creation if requested
    create_checkpoint = config.get('performance', {}).get('create_checkpoint', False)
    checkpoint_file = Path(config.get('reporting', {}).get('checkpoint_path', 'reports/cross_reference/checkpoint.json'))
    processed_file_paths = []

    # Create progress display for overall process
    detailed_results = []
    perf_monitor.start_phase("find_references")
    
    # Display beautiful header
    target_count = len(target_files)
    term_width = shutil.get_terminal_size().columns
    header = f" Processing {target_count} files for cross-references "
    padding = (term_width - len(header)) // 2
    print(f"\n{'✧' * padding}{header}{'✧' * padding}\n")
    
    # Get concurrency limit from config or default to CPU count
    perf_config = config.get('performance', {})
    max_workers_config = perf_config.get('max_workers', 'cpu_count')
    max_parallel = os.cpu_count() if max_workers_config == 'cpu_count' else int(max_workers_config)
    # Limit to reasonable number to avoid overwhelming the system
    max_parallel = min(max(1, max_parallel), 16)
    
    # Process files in batches to show progress better
    batch_size = min(10, max(1, len(target_files) // 10))
    total_batches = math.ceil(len(target_files) / batch_size)
    
    # Initialize file content cache with persistent storage
    file_content_cache = {}
    persistent_cache_enabled = config.get('performance', {}).get('persistent_cache', False)
    persistent_cache_file = Path(config.get('performance', {}).get('persistent_cache_file', 'reports/cross_reference/file_content_cache.json'))
    
    # Load persistent cache if enabled
    if persistent_cache_enabled:
        try:
            if persistent_cache_file.exists():
                logger.info(f"Loading persistent file content cache from {persistent_cache_file}")
                with open(persistent_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Convert cache keys back to strings and validate cache entries
                for file_path_str, content_data in cache_data.items():
                    file_path = Path(file_path_str)
                    
                    # Validate cache entry (check if file exists and modification time matches)
                    if file_path.exists():
                        current_mtime = file_path.stat().st_mtime
                        cached_mtime = content_data.get('mtime', 0)
                        
                        # Use cache entry only if modification time matches
                        if abs(current_mtime - cached_mtime) < 1.0:  # Allow 1 second difference
                            file_content_cache[str(file_path)] = content_data.get('content', '')
                
                logger.info(f"Loaded {len(file_content_cache)} valid entries from persistent cache")
        except Exception as e:
            logger.warning(f"Failed to load persistent cache: {e}")
    
    # Initialize performance monitor
    perf_monitor = PerformanceMonitorUltra()
    
    # Calculate and display initial time estimate
    # Base estimate on historical data or use conservative default
    avg_time_per_file_sec = perf_config.get('avg_time_per_file_sec', 7.0)  # Default: 7 seconds per file
    estimated_total_time_sec = avg_time_per_file_sec * target_count
    estimated_completion_time = datetime.datetime.now() + datetime.timedelta(seconds=estimated_total_time_sec)
    
    # Create a beautiful time estimate display
    print(f"\n{'='*term_width}")
    print(f"✧ EXECUTION PLAN ✧")
    print(f"{'='*term_width}")
    print(f"Files to process: {target_count}")
    print(f"Parallel workers: {max_parallel}")
    print(f"Batch size: {batch_size} files ({total_batches} batches)")
    print(f"Estimated time per file: {avg_time_per_file_sec:.1f} seconds")
    print(f"Estimated total time: {estimated_total_time_sec/60:.1f} minutes")
    print(f"Estimated completion: {estimated_completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Offer partial run options if total time is significant
    if estimated_total_time_sec > 300 and perf_config.get('partial_run_percentage', 100) == 100:  # If > 5 minutes and not already partial
        print(f"\nℹ️  For faster execution, you can run a partial analysis by setting:")
        print(f"   performance.partial_run_percentage: 25|50|75 in your config file")
    print(f"{'='*term_width}\n")
    
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_parallel)
    print(f"Starting processing with {max_parallel} parallel workers...\n")
    
    # Create main progress bar for overall process
    main_progress = ProgressDisplay(total=target_count, 
                                   desc="Total progress",
                                   unit="files",
                                   refresh_rate=0.3)
    
    async def process_file_with_semaphore(file_idx, target_file):
        """Process a single file with semaphore to limit concurrency."""
        async with semaphore:
            # Find references
            references = await ref_finder.find_references_to_file(target_file)
            return {
                "file_idx": file_idx,
                "file_path": str(target_file.relative_to(project_base_path) if project_base_path in target_file.parents else target_file),
                "references_found": references
            }
    
    # Set up detailed logging
    log_file = Path(config.get('reporting', {}).get('log_path', 'reports/cross_reference/performance_log.json'))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    performance_logs = {
        'batches': [],
        'overall': {
            'start_time': datetime.datetime.now().isoformat(),
            'target_count': target_count,
            'workers': max_parallel,
            'batch_size': batch_size
        }
    }
    
    # Create a global progress tracker that persists across batches
    global_progress = {
        'total_files': target_count,
        'processed_files': 0,
        'current_batch': 0,
        'total_batches': total_batches,
        'references_found': 0,
        'start_time': time.monotonic(),
        'batch_start_time': time.monotonic()
    }
    
    # Process files in batches
    for batch_idx in range(total_batches):
        # Update global progress
        global_progress['current_batch'] = batch_idx + 1
        global_progress['batch_start_time'] = time.monotonic()
        
        # Calculate batch range
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(target_files))
        batch_files = target_files[start_idx:end_idx]
        
        # Create a beautiful batch header
        batch_header = f" Batch {batch_idx+1}/{total_batches} "
        print(f"\n{'-'*20}{batch_header}{'-'*20}")
        print(f"Processing files {start_idx+1}-{end_idx} of {target_count} ({(end_idx-start_idx)} files)")
        
        # Update main progress with overall percentage and clear batch info
        overall_percent = int(start_idx / target_count * 100)
        main_progress.update(start_idx, desc=f"Overall progress: {overall_percent}% ({start_idx}/{target_count} files)")
        
        # Create batch of tasks
        tasks = []
        for i, file in enumerate(batch_files):
            file_idx = start_idx + i
            tasks.append(process_file_with_semaphore(file_idx, file))
        
        # Wait for all tasks in this batch to complete
        batch_results = await asyncio.gather(*tasks)
        
        # Process results and update progress
        batch_references = 0
        for result in batch_results:
            # Store in final results at the correct index to maintain order
            while len(detailed_results) <= result["file_idx"]:
                detailed_results.append(None)
            detailed_results[result["file_idx"]] = {
                "file_path": result["file_path"],
                "references_found": result["references_found"]
            }
            # Count references in this batch
            batch_references += len(result["references_found"])
            # Update progress
            main_progress.update(result["file_idx"] + 1)
            
            # Track processed files for checkpoint
            if create_checkpoint:
                processed_file_paths.append(str(target_files[result["file_idx"]]))
        
        # Update global progress
        global_progress['processed_files'] = end_idx
        global_progress['references_found'] += batch_references
        
        # Recalculate estimated completion time after each batch
        elapsed = perf_monitor.get_phase_duration("find_references")
        files_processed = end_idx
        batch_duration = time.monotonic() - global_progress['batch_start_time']
        
        if elapsed > 0 and files_processed > 0:
            # Calculate rates and estimates
            overall_rate = files_processed / elapsed
            batch_rate = len(batch_files) / batch_duration if batch_duration > 0 else 0
            remaining_files = target_count - files_processed
            remaining_time = remaining_files / overall_rate if overall_rate > 0 else float('inf')
            new_completion_time = datetime.datetime.now() + datetime.timedelta(seconds=remaining_time)
            overall_progress = files_processed / target_count * 100
            
            # Log batch performance
            batch_log = {
                'batch_number': batch_idx + 1,
                'files_processed': len(batch_files),
                'references_found': batch_references,
                'duration_seconds': batch_duration,
                'files_per_second': batch_rate,
                'start_index': start_idx,
                'end_index': end_idx
            }
            performance_logs['batches'].append(batch_log)
            
            # Create a beautiful batch summary
            print(f"\n{'-'*10} Batch {batch_idx+1} Summary {'-'*10}")
            print(f"Processed: {len(batch_files)} files in {batch_duration:.1f}s ({batch_rate:.2f} files/sec)")
            print(f"References found in this batch: {batch_references}")
            print(f"Total progress: {overall_progress:.1f}% ({files_processed}/{target_count} files)")
            
            # Create a beautiful overall progress summary
            print(f"\n{'-'*10} Overall Progress {'-'*10}")
            print(f"Total elapsed time: {elapsed:.1f}s")
            print(f"Overall processing rate: {overall_rate:.2f} files/sec")
            print(f"Total references found: {global_progress['references_found']}")
            print(f"Estimated completion: {new_completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Remaining time: {perf_monitor._format_time(remaining_time)}")
            print(f"Cache size: {len(file_content_cache)} files")
            
            # Save performance logs after each batch
            performance_logs['overall']['elapsed_seconds'] = elapsed
            performance_logs['overall']['files_processed'] = files_processed
            performance_logs['overall']['references_found'] = global_progress['references_found']
            performance_logs['overall']['estimated_completion'] = new_completion_time.isoformat()
            performance_logs['overall']['remaining_seconds'] = remaining_time
            
            try:
                with open(log_file, 'w') as f:
                    json.dump(performance_logs, f, indent=2)
                logger.debug(f"Performance log saved to {log_file}")
            except Exception as e:
                logger.warning(f"Failed to save performance log: {e}")
            
            # Save checkpoint if requested
            if create_checkpoint:
                try:
                    # Ensure directory exists
                    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create checkpoint data
                    checkpoint_data = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'processed_files': processed_file_paths,
                        'total_files': len(target_files),
                        'references_found': global_progress['references_found'],
                        'elapsed_seconds': elapsed
                    }
                    
                    # Save checkpoint
                    with open(checkpoint_file, 'w') as f:
                        json.dump(checkpoint_data, f, indent=2)
                    logger.info(f"📋 Checkpoint saved: {len(processed_file_paths)}/{len(target_files)} files processed")
                except Exception as e:
                    logger.warning(f"Failed to save checkpoint: {e}")
                
            # Add a separator for clarity
            print(f"{'-'*50}\n")
    
    # Make sure there are no gaps in the results (in case of errors)
    detailed_results = [r for r in detailed_results if r is not None]
    
    # Complete the progress display
    main_progress.finish(f"Completed processing {len(detailed_results)}/{target_count} files")
    
    perf_monitor.record_metric("files_processed_for_references_count", len(detailed_results))
    perf_monitor.record_metric("cache_size", len(file_content_cache))
    perf_monitor.end_phase("find_references")

    perf_monitor.start_phase("generate_reports")
    report_gen.generate_reports(detailed_results, perf_monitor.get_summary())
    perf_monitor.end_phase("generate_reports")

    # Save persistent cache if enabled
    if persistent_cache_enabled:
        try:
            # Create enhanced cache with metadata
            enhanced_cache = {}
            for file_path_str, content in file_content_cache.items():
                file_path = Path(file_path_str)
                if file_path.exists():
                    enhanced_cache[file_path_str] = {
                        'content': content,
                        'mtime': file_path.stat().st_mtime,
                        'size': file_path.stat().st_size,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
            
            # Create directory if it doesn't exist
            persistent_cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save cache to file
            with open(persistent_cache_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_cache, f, indent=2)
            
            logger.info(f"Saved persistent cache with {len(enhanced_cache)} entries to {persistent_cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save persistent cache: {e}")
    
    # Final beautiful summary
    term_width = shutil.get_terminal_size().columns
    total_time = perf_monitor.get_summary()['total_execution_time_sec']
    total_refs = sum(len(r.get('references_found', [])) for r in detailed_results)
    
    # Determine run mode for summary
    run_mode = ""
    if quick_test:
        run_mode = "⚡ QUICK TEST MODE"
    elif partial_run_percentage < 100:
        run_mode = f"🔍 PARTIAL ANALYSIS ({partial_run_percentage}%)"
    
    print(f"\n{'='*term_width}")
    print(f"✧ CROSS-REFERENCE ULTRA CHECK COMPLETED ✧ {run_mode}")
    print(f"{'='*term_width}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Files processed: {len(detailed_results)}/{target_count}")
    print(f"References found: {total_refs}")
    print(f"Content cache size: {len(file_content_cache)} files")
    
    # Show checkpoint information if relevant
    if create_checkpoint:
        print(f"Checkpoint saved: {checkpoint_file}")
        print(f"To continue processing, use: --continue-from-checkpoint")
    
    print(f"Report generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*term_width}\n")
    
    logger.info(f"Cross-Reference Ultra check completed. Total time: {total_time:.3f}s")
    logger.info(f"Files processed: {len(detailed_results)}/{target_count}, References found: {total_refs}")
    
    # Final checkpoint save at completion
    if create_checkpoint and processed_file_paths:
        try:
            # Update final checkpoint
            checkpoint_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'processed_files': processed_file_paths,
                'total_files': len(target_files),
                'references_found': total_refs,
                'elapsed_seconds': total_time,
                'completed': len(processed_file_paths) >= len(target_files)
            }
            
            # Save final checkpoint
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)


            logger.info(f"📋 Final checkpoint saved: {len(processed_file_paths)}/{len(target_files)} files processed")
        except Exception as e:
            logger.warning(f"Failed to save final checkpoint: {e}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cross-Reference Checker Ultra - Find references between files")
    parser.add_argument("--config", "-c", type=str, default="config_ultra.yaml", help="Path to configuration file")
    parser.add_argument("--quick-test", action="store_true", help="Run in quick test mode (3-5 files only)")
    parser.add_argument("--create-checkpoint", action="store_true", help="Create checkpoint file for resuming later")
    parser.add_argument("--continue-from-checkpoint", action="store_true", help="Continue from last checkpoint")
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration from file
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
        
    # Override config with command line arguments if provided
    if args.quick_test:
        if 'performance' not in config:
            config['performance'] = {}
        config['performance']['quick_test'] = True
        
    if args.create_checkpoint:
        if 'performance' not in config:
            config['performance'] = {}
        config['performance']['create_checkpoint'] = True
        
    if args.continue_from_checkpoint:
        if 'performance' not in config:
            config['performance'] = {}
        config['performance']['continue_from_checkpoint'] = True
    
    # Configure logging level from config, if specified
    log_level_str = config.get("logging", {}).get("level", "INFO").upper()
    numeric_log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Update root logger level and add file handler if configured
    logging.getLogger().setLevel(numeric_log_level)
    
    log_file_path_str = config.get("logging", {}).get("file_path", None)
    if log_file_path_str:
        log_file_path = Path(log_file_path_str)
        if not log_file_path.is_absolute():
            log_file_path = Path(config.get("project_base_path", ".")) / log_file_path
            
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(file_handler)
        logger.info(f"Logging to file: {log_file_path}")
    
    # Run the checker with exception handling
    try:
        # Log configuration summary
        logger.info(f"Using configuration from: {config_path}")
        logger.info(f"Log level set to: {log_level_str}")
        if args.quick_test:
            logger.info("Running in QUICK TEST mode (3-5 files only)")
        if args.continue_from_checkpoint:
            logger.info("Continuing from last checkpoint")
        if args.create_checkpoint:
            logger.info("Creating checkpoints during processing")
            
        # Run the checker
        asyncio.run(run_checker(config))
    except KeyboardInterrupt:
        logger.info("Script execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("Script execution completed.")


if __name__ == "__main__":
    # Set higher recursion limit if needed for deep directory structures, with caution
    sys.setrecursionlimit(5000)
    main()