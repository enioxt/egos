#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Script Standards Scanner

This script scans the EGOS codebase to identify scripts that don't follow
the established EGOS script standards. It analyzes scripts for compliance
with visual elements, performance considerations, error handling, code structure,
configuration management, logging, and user experience standards.

Part of the EGOS Cross-Reference Standardization Initiative.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

@references: 
- C:\EGOS\docs\standards\scripting\script_management_best_practices.md
- C:\EGOS\config\script_standards_definition.yaml"""
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
import json
import time
import logging
import argparse
import ast
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Pattern, Union, Callable
from collections import defaultdict, Counter

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

import yaml

# Constants
EGOS_ROOT_PATH = Path(__file__).resolve().parents[2] # EGOS/scripts/cross_reference/ -> EGOS/
"""Root path of the EGOS project."""
STANDARDS_DEFINITION_FILE = EGOS_ROOT_PATH / "config" / "script_standards_definition.yaml"
"""Path to the script standards definition YAML file."""
BANNER_WIDTH = 80
TERMINAL_WIDTH = 120
DEFAULT_SCRIPT_EXTENSIONS = {'.py'}
DEFAULT_EXCLUDE_DIRS = {'.git', 'venv', 'node_modules', '__pycache__', 'dist', 'build', 'target', 'bin', 'obj'}

# Configuration
CONFIG = {
    # Scanning settings
    "script_extensions": DEFAULT_SCRIPT_EXTENSIONS,
    "exclude_dirs": DEFAULT_EXCLUDE_DIRS,
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'script_standards_scanner.log'),
    "log_level": "INFO",
    
    # Standards settings
    "required_imports": [
        "argparse",
        "logging",
        "pathlib",
        "typing",
    ],
    "recommended_imports": [
        "tqdm",
        "colorama",
    ],
    "visual_elements": [
        "print_banner",
        "ProgressTracker",
        "Fore.CYAN",
        "Fore.YELLOW",
        "Fore.GREEN",
        "Fore.RED",
        "Fore.BLUE",
    ],
    "performance_patterns": [
        "batch_size",
        "ThreadPoolExecutor",
        "concurrent.futures",
        "timeout",
        "asyncio",
    ],
    "error_handling_patterns": [
        "try:",
        "except Exception as e:",
        "finally:",
        "backup",
        "dry_run",
    ],
    "code_structure_patterns": [
        "class ",
        "def __init__",
        "\"\"\"",
        "Args:",
        "Returns:",
        "from typing import",
    ],
    "configuration_patterns": [
        "CONFIG",
        "parser.add_argument",
        "argparse.ArgumentParser",
    ],
    "logging_patterns": [
        "logging.basicConfig",
        "logger =",
        "logger.info",
        "logger.warning",
        "logger.error",
        "logger.debug",
    ],
    "user_experience_patterns": [
        "help=",
        "description=",
        "epilog=",
        "print(f\"",
    ],
}

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("script_standards_scanner")

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (width - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (width - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (width-2)}╝{Style.RESET_ALL}")
    print()

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

class StandardsScanner:
    """Scanner for EGOS script standards compliance.
    
    Performs comprehensive validation of Python scripts against the EGOS script standards.
    Supports batch scanning, interactive reporting, and integration with the template generator.
    """

    def _get_call_func_name(self, call_node_func: ast.AST) -> str:
        """Recursively reconstructs the full function name from an AST call node's func attribute."""
        if isinstance(call_node_func, ast.Name):
            return call_node_func.id
        elif isinstance(call_node_func, ast.Attribute):
            # Recursively get the base part of the name (e.g., 'logging' from 'logging.basicConfig')
            # and append the attribute part (e.g., '.basicConfig')
            base_name = self._get_call_func_name(call_node_func.value)
            if base_name: # Ensure base_name is not empty to avoid leading '.'
                return f"{base_name}.{call_node_func.attr}"
            else:
                return call_node_func.attr # Should ideally not happen with valid calls
        # Add handling for ast.Subscript if needed for calls like obj['method']()
        # For now, focusing on Name and Attribute which cover most common function calls.
        return "" # Return empty string for unhandled node types or if name cannot be resolved
    
    def __init__(self, base_path: str, verbose: bool = False, include_pattern: Optional[str] = None, 
                 exclude_pattern: Optional[str] = None, html_report: bool = False):
        """Initialize the standards scanner.
        
        Args:
            base_path: Base path to scan
            verbose: If True, print detailed information
            include_pattern: Only scan files matching this pattern (e.g., '*.py')
            exclude_pattern: Exclude files matching this pattern (e.g., 'test_*.py')
            html_report: If True, generate an HTML report with enhanced visualization
            """
            self.defined_standards: List[Dict[str, Any]] = []
    self._load_external_standards() # Load standards from YAML

    self.base_path = Path(base_path)
        self.verbose = verbose
        self.include_pattern = include_pattern
        self.exclude_pattern = exclude_pattern
        self.html_report = html_report
        
        # Statistics
        self.stats = {
            "files_scanned": 0,
            "compliant_files": 0,
            "non_compliant_files": 0,
            "errors": 0,
            "processing_time": 0,
        }
        
        # Results
        self.results = []

    def _load_external_standards(self) -> None:
        """Loads script standards definitions from the YAML file."""
        if not STANDARDS_DEFINITION_FILE.is_file():
            logger.error(f"Standards definition file not found or is not a file: {STANDARDS_DEFINITION_FILE}")
            self.defined_standards = [] # Ensure it's an empty list
            return

        try:
            with open(STANDARDS_DEFINITION_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data and isinstance(data.get('standards'), list):
                self.defined_standards = data['standards']
                logger.info(f"Successfully loaded {len(self.defined_standards)} standards from {STANDARDS_DEFINITION_FILE}")
            elif data is None: # Handles empty YAML file
                logger.warning(f"Standards definition file is empty: {STANDARDS_DEFINITION_FILE}")
                self.defined_standards = []
            else:
                logger.error(f"Invalid format in standards definition file: {STANDARDS_DEFINITION_FILE}. 'standards' list not found or malformed.")
                self.defined_standards = []
        
        except FileNotFoundError: # Should be caught by is_file() check, but as a fallback.
            logger.error(f"Standards definition file not found during open: {STANDARDS_DEFINITION_FILE}")
            self.defined_standards = []
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML from {STANDARDS_DEFINITION_FILE}: {e}")
            self.defined_standards = []
        except Exception as e: # Catch any other unexpected errors during file processing
            logger.error(f"An unexpected error occurred while loading standards from {STANDARDS_DEFINITION_FILE}: {e}")
            self.defined_standards = []
    
    def find_scripts(self) -> List[Path]:
        """Find all scripts to scan with enhanced filtering.
        
        Uses the include_pattern and exclude_pattern parameters for more precise control over
        which files are scanned. Supports glob patterns for efficient filtering.
        
        Returns:
            List of script paths matching the specified criteria
        """
        scripts = []
        
        # Find all Python files in the base path
        for ext in CONFIG["script_extensions"]:
            # Apply include_pattern if specified
            if self.include_pattern:
                pattern = self.include_pattern
            else:
                pattern = f"**/*{ext}"
                
            for file_path in self.base_path.glob(pattern):
                # Skip excluded directories
                if any(excluded in str(file_path) for excluded in CONFIG["exclude_dirs"]):
                    continue
                
                # Apply exclude_pattern if specified
                if self.exclude_pattern and fnmatch.fnmatch(file_path.name, self.exclude_pattern):
                    if self.verbose:
                        logger.debug(f"Skipping {file_path}: Matches exclude pattern {self.exclude_pattern}")
                    continue
                
                # Ensure file has the right extension if using custom include_pattern
                if self.include_pattern and not any(file_path.name.endswith(ext) for ext in CONFIG["script_extensions"]):
                    continue
                    
                # Skip files larger than the maximum size
                try:
                    if file_path.stat().st_size > CONFIG["max_file_size"]:
                        logger.warning(f"Skipping {file_path}: File too large ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
                        continue
                except OSError as e:
                    logger.warning(f"Error accessing {file_path}: {str(e)}")
                    continue
                    
                scripts.append(file_path)
        
        if self.verbose:
            logger.info(f"Found {len(scripts)} scripts to scan")
            
            # Print directories breakdown if verbose
            dir_count = Counter([str(script.parent.relative_to(self.base_path) if self.base_path in script.parents else script.parent) for script in scripts])
            logger.info(f"Scripts by directory:")
            for directory, count in sorted(dir_count.most_common(), key=lambda x: (-x[1], x[0])):
                logger.info(f"  • {directory}: {count} scripts")
                
        logger.info(f"Found {len(scripts)} scripts to scan")
        return scripts
    
    def check_standards(self, file_path: Path) -> Dict[str, Any]:
        """Check if a script follows EGOS script standards.
        
        Performs comprehensive validation across all standard categories including
        visual elements, performance, error handling, code structure, configuration,
        logging, and user experience.
        
        Args:
            file_path: Path to the script
            
        Returns:
            Dictionary with compliance results including detailed scoring by category
        """
        result = {
            "file": str(file_path),
            "compliant": False,
            "compliance_score": 0,
            "category_scores": {},
            "issues": [],
            "error": None
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Prepare for AST parsing if any standard requires it
            ast_tree = None
            can_perform_ast_checks = True # Assume we can, unless parsing fails
            # Check if any defined standard requires AST analysis to avoid unnecessary parsing
            if any(std.get('type', '').startswith('ast_') for std in self.defined_standards):
                try:
                    ast_tree = ast.parse(content)
                except SyntaxError as e:
                    can_perform_ast_checks = False
                    result["error"] = f"Syntax error, cannot perform AST-based checks: {e}"
                    result["issues"].append({
                        "id": "CRITICAL_SYNTAX_ERROR",
                        "name": "Syntax Error in Script",
                        "message": f"Script has a syntax error preventing AST analysis: {getattr(e, 'filename', 'N/A')}, line {getattr(e, 'lineno', 'N/A')}, offset {getattr(e, 'offset', 'N/A')}: {getattr(e, 'msg', 'Unknown syntax error')}",
                        "severity": "critical",
                        "category": "structure"
                    })
                    # Continue with non-AST checks if possible.

            lines = content.splitlines(keepends=True) # Keep ends for accurate line content if needed later
            first_line = lines[0] if lines else ""
            second_line = lines[1] if len(lines) > 1 else ""

            for standard in self.defined_standards:
                check_passed = True # Assume pass unless a check fails
                standard_type = standard.get('type')
                standard_id = standard.get('id', 'UNKNOWN_ID') # For logging

                # --- Handle regex_present checks --- 
                if standard_type == 'regex_present':
                    pattern_str = standard.get('pattern')
                    if not pattern_str:
                        logger.warning(f"Standard {standard_id} is 'regex_present' but has no pattern. Skipping.")
                        continue
                    
                    try:
                        regex_flags = 0
                        if standard.get('regex_multiline'):
                            regex_flags |= re.MULTILINE
                        if standard.get('regex_ignorecase'):
                            regex_flags |= re.IGNORECASE
                        pattern = re.compile(pattern_str, flags=regex_flags)
                    except re.error as e:
                        logger.warning(f"Invalid regex pattern for standard {standard_id}: '{pattern_str}'. Error: {e}. Skipping.")
                        continue

                    target_content_for_regex = ""
                    scope = standard.get('scope')
                    # Let's assume for now that if AST parsing fails, AST checks dependent on it cannot pass.
                    check_passed = False # Or handle this state differently, e.g. add to a 'skipped_checks' list
                else:
                    module_docstring = ast.get_docstring(ast_tree)
                    if not module_docstring: # Checks for None or empty string
                        check_passed = False
            
            # --- Handle ast_module_docstring_present --- 
            elif standard_type == 'ast_module_docstring_present':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for module docstring presence due to syntax error or no AST tree.")
                    check_passed = False 
                else:
                    module_docstring = ast.get_docstring(ast_tree)
                    if not module_docstring:
                        check_passed = False
            
            # --- Handle regex_present_in_docstring for module docstrings ---
            elif standard_type == 'regex_present_in_docstring' and standard.get('docstring_target') == 'module':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for regex in module docstring due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    module_docstring = ast.get_docstring(ast_tree)
                    if not module_docstring:
                        # If the docstring itself is missing, this check also fails (implicitly covered by STD_SCRIPT_003)
                        # However, we explicitly fail it here too if this specific standard is being checked.
                        logger.debug(f"Module docstring missing, cannot perform regex check {standard_id}.")
                        check_passed = False
                    else:
                        pattern_str = standard.get('pattern')
                        if not pattern_str:
                            logger.warning(f"Standard {standard_id} is '{standard_type}' but has no pattern. Skipping this specific check.")
                            # This specific check for a pattern is skipped, but check_passed remains true unless pattern fails
                            # Or, decide if missing pattern in standard definition means the check auto-fails or is skipped.
                            # For now, let's assume it's a configuration error in the YAML and skip the check, not failing the script for it.
                            pass # check_passed remains true
                        else:
                            try:
                                regex_flags = 0
                                if standard.get('regex_multiline'): # Assuming these flags might be useful here too
                                    regex_flags |= re.MULTILINE
                                if standard.get('regex_ignorecase'):
                                    regex_flags |= re.IGNORECASE
                                pattern = re.compile(pattern_str, flags=regex_flags)
                                if not pattern.search(module_docstring):
                                    check_passed = False
                            except re.error as e:
                                logger.warning(f"Invalid regex pattern for standard {standard_id}: '{pattern_str}'. Error: {e}. Skipping check.")
                                # Consider if an invalid regex in a standard should fail the check or just be logged.
                                # For now, skipping the check (check_passed remains true), assuming it's a standard definition issue.
                                pass # check_passed remains true

            # --- Handle ast_function_defined --- 
            elif standard_type == 'ast_function_defined':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for function definition due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    function_name_to_find = standard.get('function_name')
                    if not function_name_to_find:
                        logger.warning(f"Standard {standard_id} is '{standard_type}' but missing 'function_name'. Skipping check.")
                        # check_passed remains true, as it's a standard definition issue
                    else:
                        found_function = False
                        for node in ast_tree.body:
                            if isinstance(node, ast.FunctionDef) and node.name == function_name_to_find:
                                found_function = True
                                break
                        if not found_function:
                            check_passed = False
            
            # --- Handle ast_main_entry_point_present --- 
            elif standard_type == 'ast_main_entry_point_present':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for main entry point due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    found_entry_point = False
                    for node in ast_tree.body:
                        if isinstance(node, ast.If):
                            # Check if node.test is Compare(Name(id='__name__'), Eq(), [Constant(value='__main__')])
                            # or Compare(Name(id='__name__'), Eq(), [Str(s='__main__')]) for older Python versions
                            if isinstance(node.test, ast.Compare):
                                if isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__':
                                    if isinstance(node.test.ops[0], ast.Eq):
                                        if len(node.test.comparators) == 1:
                                            comparator = node.test.comparators[0]
                                            is_main_str = False
                                            if isinstance(comparator, ast.Constant) and comparator.value == '__main__': # Python 3.8+
                                                is_main_str = True
                                            elif isinstance(comparator, ast.Str) and comparator.s == '__main__': # Python < 3.8
                                                is_main_str = True
                                            
                                            if is_main_str:
                                                found_entry_point = True
                                                break
                    if not found_entry_point:
                        check_passed = False

            # --- Handle ast_import_present --- 
            elif standard_type == 'ast_import_present':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for import presence due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    module_name_to_find = standard.get('module_name')
                    if not module_name_to_find:
                        logger.warning(f"Standard {standard_id} is '{standard_type}' but missing 'module_name'. Skipping check.")
                    else:
                        found_import = False
                        for node in ast_tree.body:
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    if alias.name == module_name_to_find:
                                        found_import = True
                                        break
                            elif isinstance(node, ast.ImportFrom):
                                # For 'from X import Y', node.module is 'X'
                                # For 'from .X import Y', node.module is '.X' (relative)
                                # This check is for top-level module imports like 'import argparse' or 'from os import path'
                                # where 'os' would be module_name_to_find.
                                if node.module == module_name_to_find:
                                    found_import = True
                                    break
                            if found_import:
                                break
                        if not found_import:
                            check_passed = False

            # --- Handle ast_variable_defined --- 
            elif standard_type == 'ast_variable_defined':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for variable definition due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    variable_name_to_find = standard.get('variable_name')
                    expected_variable_type = standard.get('variable_type') # e.g., "Dict", "List", "Call"

                    if not variable_name_to_find:
                        logger.warning(f"Standard {standard_id} is '{standard_type}' but missing 'variable_name'. Skipping check.")
                        # This is a standard definition issue, so we don't fail the script check_passed remains true.
                    else:
                        found_variable_definition = False
                        variable_type_matched = False # Assume no type or type matches until proven otherwise

                        for node in ast_tree.body:
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if isinstance(target, ast.Name) and target.id == variable_name_to_find:
                                        found_variable_definition = True
                                        # Variable name found. Now check type if specified.
                                        if expected_variable_type:
                                            value_node = node.value
                                            current_type_match = False
                                            if expected_variable_type == "Dict" and isinstance(value_node, ast.Dict):
                                                current_type_match = True
                                            elif expected_variable_type == "List" and isinstance(value_node, ast.List):
                                                current_type_match = True
                                            elif expected_variable_type == "Tuple" and isinstance(value_node, ast.Tuple):
                                                current_type_match = True
                                            elif expected_variable_type == "Set" and isinstance(value_node, ast.Set):
                                                current_type_match = True
                                            elif expected_variable_type == "Call" and isinstance(value_node, ast.Call):
                                                current_type_match = True
                                            # Add more specific type checks for ast.Constant, etc. if needed
                                            
                                            if current_type_match:
                                                variable_type_matched = True
                                            else:
                                                logger.debug(f"Variable '{variable_name_to_find}' defined but type mismatch for standard {standard_id}. Expected AST type for '{expected_variable_type}', got {type(value_node).__name__}.")
                                                variable_type_matched = False # Explicitly set to false on mismatch
                                        else:
                                            variable_type_matched = True # No specific type expected, so name match is enough
                                        break # Found variable name in targets, exit inner loop
                                if found_variable_definition:
                                    break # Exit outer loop (nodes) if variable found
                        
                        if not found_variable_definition:
                            check_passed = False
                        elif expected_variable_type and not variable_type_matched:
                            # Variable was found, but its type did not match the expected type.
                            check_passed = False

            # --- Handle ast_function_call_present --- 
            elif standard_type == 'ast_function_call_present':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for function call presence due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    function_to_find = standard.get('function_name')
                    if not function_to_find:
                        logger.warning(f"Standard {standard_id} is '{standard_type}' but missing 'function_name'. Skipping check.")
                    else:
                        # Define a local visitor class to find the function call
                        class FunctionCallVisitor(ast.NodeVisitor):
                            def __init__(self, target_func_name, scanner_instance):
                                self.target_func_name = target_func_name
                                self.scanner_instance = scanner_instance # To access _get_call_func_name
                                self.found = False

                            def visit_Call(self, node):
                                if self.found: # Stop visiting if already found
                                    return
                                
                                called_func_name = self.scanner_instance._get_call_func_name(node.func)
                                if called_func_name == self.target_func_name:
                                    self.found = True
                                    return # Stop visiting this branch
                                self.generic_visit(node) # Continue visiting other nodes
                        
                        visitor = FunctionCallVisitor(function_to_find, self) # Pass 'self' (StandardsScanner instance)
                        visitor.visit(ast_tree)
                        if not visitor.found:
                            check_passed = False

            # --- Handle ast_try_except_present --- 
            elif standard_type == 'ast_try_except_present':
                if not can_perform_ast_checks or not ast_tree:
                    logger.debug(f"Skipping AST check {standard_id} for try-except presence due to syntax error or no AST tree.")
                    check_passed = False
                else:
                    # Define a local visitor class to find if any try-except block exists
                    class TryExceptVisitor(ast.NodeVisitor):
                        def __init__(self):
                            self.found = False

                        def visit_Try(self, node):
                            # An ast.Try node represents a try block.
                            # It can have handlers (except), orelse (else), and finalbody (finally).
                            # For this check, just finding an ast.Try node is sufficient.
                            self.found = True
                            # We can stop visiting further if one is found, by not calling generic_visit or raising an exception.
                            # However, standard visitor pattern would continue. For presence, one is enough.
                            # To stop early, we could raise a custom exception caught outside.
                            # For now, let it visit all, 'found' will remain true if any Try is encountered.
                            # To be more performant for simple presence, one could adapt the visitor to stop.
                            self.generic_visit(node) # Continue visiting in case of nested try-excepts, though not strictly needed for this check
                    
                    visitor = TryExceptVisitor()
                    visitor.visit(ast_tree)
                    if not visitor.found:
                        check_passed = False

            # --- Handle regex_match_all_in_block ---
            elif standard_type == 'regex_match_all_in_block':
                check_passed = True # Assume pass unless proven otherwise or block content violates rules
                
                docstring_target = standard.get('docstring_target')
                target_text_for_block_check = ""

                if docstring_target == 'module':
                    if module_docstring_node and module_docstring_content:
                        target_text_for_block_check = module_docstring_content
                    else:
                        # Module docstring targeted but not found. Block cannot exist in target.
                        logger.debug(f"Skipping {standard_id} ({standard_type}): module docstring targeted but not found.")
                        # check_passed remains True, as no block means no violation of its internal content.
                        pass # Block will not be found in empty target_text_for_block_check
                else:
                    target_text_for_block_check = content

                # Proceed only if there's text to check or if it's not a module_docstring specific check that failed to find its target text
                if target_text_for_block_check or not (docstring_target == 'module' and not module_docstring_content):
                    block_start_pattern = standard.get('block_start_pattern')
                    block_end_pattern = standard.get('block_end_pattern')
                    item_pattern = standard.get('item_pattern')

                    if not all([block_start_pattern, block_end_pattern, item_pattern]):
                        logger.warning(f"Standard {standard_id} ('{standard_type}') is missing one or more required patterns (block_start_pattern, block_end_pattern, item_pattern). Skipping check.")
                        # This is a configuration error for the standard, arguably should not affect script compliance score.
                        # Or, if strict, consider it a failure: check_passed = False
                    else:
                        block_content_found = ""
                        start_match = re.search(block_start_pattern, target_text_for_block_check, re.MULTILINE)
                        
                        if start_match:
                            search_from_index = start_match.end()
                            # Search for the end_pattern from the point after the start_pattern match
                            end_match = re.search(block_end_pattern, target_text_for_block_check[search_from_index:], re.MULTILINE)
                            
                            if end_match:
                                block_content_found = target_text_for_block_check[search_from_index : search_from_index + end_match.start()]
                            else:
                                # Block extends to the end of the target_text
                                block_content_found = target_text_for_block_check[search_from_index:]
                            
                            block_lines = [line.strip() for line in block_content_found.splitlines() if line.strip()]
                            
                            if not block_lines: # Block exists but is empty or only whitespace lines
                                # If the standard implies the block should not be empty, this might be a fail.
                                # For "all items must conform", an empty set of items conforms.
                                pass # check_passed remains True
                            else:
                                for line in block_lines:
                                    if not re.fullmatch(item_pattern, line):
                                        logger.debug(f"Standard {standard_id}: Line '{line}' in block (starting with '{block_start_pattern}') does not fullmatch item_pattern '{item_pattern}'.")
                                        check_passed = False
                                        break
                        # else: block_start_pattern not found in target_text_for_block_check
                            # If block is not found, check_passed remains True (no violation of content within a non-existent block)

            # Add more elif blocks here for other standard types.

            if not check_passed:
                result["issues"].append({
                    "id": standard.get('id', 'UNKNOWN_ID'),
                    "name": standard.get('name', 'Unknown Standard Name'),
                    "message": standard.get('message', 'Compliance issue.'),
                    "severity": standard.get('severity', 'unknown'),
                    "category": standard.get('category', 'general')
                })
            else:
                # Increment compliance score based on standard.get('points', 0)
                # result["compliance_score"] += standard.get('points', 0)
                # Potentially add to a list of passed checks or update category_scores
                pass 

        # The old hardcoded docstring and import checks are being replaced or will be handled by YAML-driven logic.
            
            # Check imports organization
            import_sections = self._check_import_organization(content) # Assuming this method exists and works
            if not import_sections["organized"]:
                result["issues"].append({
                    "id": "LEGACY_IMPORTS_UNORGANIZED",
                    "name": "Legacy: Imports Not Properly Organized",
                    "message": "Imports not properly organized. Suggestion: Organize imports: standard library first, then third-party, then local imports.",
                    "severity": "low",
                    "category": "basic"
                })
            
            # VISUAL ELEMENTS CHECKS
            if "print_banner" not in content:
                result["issues"].append({
                    "id": "LEGACY_VISUAL_NO_BANNER",
                    "name": "Legacy: Missing Banner",
                    "message": "Missing banner for script headers. Suggestion: Add print_banner function and use it to display script headers.",
                    "severity": "low",
                    "category": "visual"
                })
                
            if "tqdm" not in content and any(term in content for term in ["for ", "while "]):
                result["issues"].append({
                    "id": "LEGACY_VISUAL_NO_PROGRESS_BAR",
                    "name": "Legacy: Missing Progress Bars",
                    "message": "Missing progress bars for long-running operations. Suggestion: Use tqdm for progress tracking in loops processing many items.",
                    "severity": "medium",
                    "category": "visual"
                })
                
            if not HAVE_COLORAMA or ("Fore." not in content and "Style." not in content):
                result["issues"].append({
                    "id": "LEGACY_VISUAL_NO_COLOR_CODING",
                    "name": "Legacy: Missing Color Coding",
                    "message": "Missing color coding for console output. Suggestion: Use colorama for color-coded console output (e.g., warnings, errors).",
                    "severity": "low",
                    "category": "visual"
                })
                
            # PERFORMANCE CONSIDERATIONS
            if "batch" not in content.lower() and ("for " in content or "while " in content):
                result["issues"].append({
                    "id": "LEGACY_PERF_NO_BATCH_PROCESSING",
                    "name": "Legacy: Consider Batch Processing",
                    "message": "Consider batch processing for large datasets. Suggestion: Implement batch processing to prevent memory issues with large datasets.",
                    "severity": "medium",
                    "category": "performance"
                })
                
            if "timeout" not in content.lower() and ("requests." in content or "urlopen" in content or "subprocess." in content):
                result["issues"].append({
                    "id": "LEGACY_PERF_NO_TIMEOUTS",
                    "name": "Legacy: Missing Timeout Mechanisms",
                    "message": "Missing timeout mechanisms for operations that might hang. Suggestion: Add timeout parameters to network requests and subprocess calls.",
                    "severity": "high",
                    "category": "performance"
                })
                
            has_async = "async " in content or "await " in content
            has_io_ops = any(term in content for term in ["open(", "requests.", "urlopen", "subprocess.", "os.path"])
            if has_io_ops and not has_async and "ThreadPoolExecutor" not in content:
                result["issues"].append({
                    "id": "LEGACY_PERF_NO_ASYNC_IO",
                    "name": "Legacy: Consider Async/ThreadPool for I/O",
                    "message": "Consider async/await or ThreadPoolExecutor for I/O-bound operations. Suggestion: Use async/await or ThreadPoolExecutor for parallel I/O operations.",
                    "severity": "medium",
                    "category": "performance"
                })
                
            # ERROR HANDLING CHECKS
            try_except_count = content.count("try:") 
            if try_except_count == 0 and len(content) > 500:  # Only flag for non-trivial scripts
                result["issues"].append({
                    "id": "LEGACY_ERROR_NO_TRY_EXCEPT",
                    "name": "Legacy: Missing Error Handling",
                    "message": "Missing error handling (try/except blocks). Suggestion: Add try/except blocks with detailed error messages.",
                    "severity": "high",
                    "category": "error_handling"
                })
                
            if "backup" not in content.lower() and any(term in content for term in ["remove", "delete", "rmdir", "rmtree", "unlink"]):
                result["issues"].append({
                    "id": "LEGACY_ERROR_NO_BACKUP",
                    "name": "Legacy: Missing Backup Mechanism",
                    "message": "Missing backup mechanism before destructive operations. Suggestion: Implement backup functionality before destructive operations.",
                    "severity": "critical",
                    "category": "error_handling"
                })
                
            if "--dry-run" not in content and any(term in content for term in ["remove", "delete", "rmdir", "rmtree", "unlink", "write", "create"]):
                result["issues"].append({
                    "id": "LEGACY_ERROR_NO_DRY_RUN",
                    "name": "Legacy: Missing Dry-Run Mode",
                    "message": "Missing dry-run mode for testing destructive/modifying operations. Suggestion: Add a --dry-run flag for testing without making actual changes.",
                    "severity": "high",
                    "category": "error_handling"
                })
                
            # CODE STRUCTURE CHECKS
            class_count = content.count("class ")
            if class_count == 0 and len(content) > 1000:  # Only flag for larger scripts
                result["issues"].append({
                    "id": "LEGACY_STRUCTURE_NO_CLASSES",
                    "name": "Legacy: Missing Class-Based Design",
                    "message": "Missing class-based design for encapsulation in a large script. Suggestion: Refactor into class-based design for better encapsulation.",
                    "severity": "medium",
                    "category": "code_structure"
                })
                
            function_docstrings = self._check_function_docstrings(content)
            if not function_docstrings["all_documented"]:
                issues["code_structure"].append(f"Missing docstrings for {function_docstrings['missing_count']} functions/methods")
                suggestions["code_structure"].append("Add comprehensive docstrings to all functions and methods")
                
            typing_annotations = self._check_type_hints(content)
            if not typing_annotations["all_typed"]:
                issues["code_structure"].append(f"Missing type hints for {typing_annotations['missing_count']} functions/parameters")
                suggestions["code_structure"].append("Add type hints to all functions and parameters")
            
            # CONFIGURATION MANAGEMENT CHECKS
            if "config" in content.lower() and "yaml" not in content.lower() and "json" not in content.lower():
                issues["config"].append("Consider using YAML or JSON for configuration")
                suggestions["config"].append("Implement YAML or JSON loading for configuration management")
                
            has_argparse = "argparse" in content
            if has_argparse and "config" in content.lower() and not any(term in content for term in ["--config", "-c"]):
                issues["config"].append("Missing command-line override for configuration")
                suggestions["config"].append("Add --config option to override configuration file path")
                
            # LOGGING CHECKS
            if "logging" in content:
                if "filehandler" not in content.lower() and "filehandler" not in content.lower():
                    issues["logging"].append("Missing file logging configuration")
                    suggestions["logging"].append("Configure both console and file logging")
                
                log_levels = ["debug", "info", "warning", "error", "critical"]
                used_levels = sum(1 for level in log_levels if f"logger.{level}" in content.lower())
                if used_levels < 2:  # Using at least 2 different log levels
                    issues["logging"].append("Not using multiple log levels")
                    suggestions["logging"].append("Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)")
            else:
                issues["logging"].append("Missing logging configuration")
                suggestions["logging"].append("Add logging with both console and file handlers")
            
            # USER EXPERIENCE CHECKS
            if has_argparse and "--help" not in content and "-h" not in content:
                issues["user_experience"].append("Missing help message configuration")
                suggestions["user_experience"].append("Configure comprehensive help messages with usage examples")
                
            has_summary = any(term in content for term in ["summary", "statistics", "stats"])
            if not has_summary and len(content) > 1000:  # Only flag for non-trivial scripts
                issues["user_experience"].append("Missing summary statistics at end of operation")
                suggestions["user_experience"].append("Add summary statistics output at the end of operations")
                
            has_egos_signature = "✧༺❀༻∞ EGOS ∞༺❀༻✧" in content
            if not has_egos_signature:
                issues["user_experience"].append("Missing EGOS signature")
                suggestions["user_experience"].append("Add the EGOS signature: ✧༺❀༻∞ EGOS ∞༺❀༻✧")
            
            # Calculate category compliance scores
            category_max_issues = {
                "basic": 8,  # Update these counts as more checks are added
                "visual": 3,
                "performance": 3,
                "error_handling": 3,
                "code_structure": 3,
                "config": 2,
                "logging": 2,
                "user_experience": 3
            }
            
            category_scores = {}
            for category, max_issues in category_max_issues.items():
                issues_found = len(issues[category])
                category_scores[category] = max(0, ((max_issues - issues_found) / max_issues) * 100)
            
            # Calculate overall compliance score (weighted average)
            weights = {
                "basic": 0.3,
                "visual": 0.1,
                "performance": 0.1,
                "error_handling": 0.15,
                "code_structure": 0.15,
                "config": 0.05,
                "logging": 0.05,
                "user_experience": 0.1
            }
            
            overall_score = sum(weights[category] * category_scores[category] for category in category_scores)
            
            # Flatten issues and suggestions lists
            all_issues = []
            all_suggestions = []
            for category in issues:
                for issue in issues[category]:
                    all_issues.append(f"[{category.upper()}] {issue}")
                for suggestion in suggestions[category]:
                    all_suggestions.append(f"[{category.upper()}] {suggestion}")
            
            # Update result
            result["compliant"] = overall_score >= 80  # Consider 80% as the threshold for compliance
            result["compliance_score"] = overall_score
            result["category_scores"] = category_scores
            result["issues"] = all_issues
            result["suggestions"] = all_suggestions
            
        except Exception as e:
            result["error"] = str(e)
            logging.debug(f"Error checking standards for {file_path}: {str(e)}", exc_info=True)
        
        return result
        
    def _check_import_organization(self, content: str) -> Dict[str, Any]:
        """Check if imports are properly organized.
        
        Proper organization is:
        1. Standard library imports
        2. Third-party imports
        3. Local imports
        
        Args:
            content: File content
            
        Returns:
            Dictionary with import organization results
        """
        result = {
            "organized": True,
            "standard_library": [],
            "third_party": [],
            "local": []
        }
        
        try:
            # Extract import statements
            import_lines = re.findall(r'^(?:import|from)\s+\S+.*$', content, re.MULTILINE)
            
            if not import_lines:
                return result
            
            # Group imports by type
            for line in import_lines:
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                    
                if line.startswith('import '):
                    module = line.split()[1].split('.')[0]
                elif line.startswith('from '):
                    module = line.split()[1].split('.')[0]
                else:
                    continue
                
                # Check if standard library
                if module in sys.builtin_module_names or module in ['os', 'sys', 're', 'time', 'json', 'logging',
                                                                  'argparse', 'datetime', 'math', 'random', 'collections',
                                                                  'functools', 'itertools', 'pathlib', 'shutil', 'tempfile',
                                                                  'typing', 'unittest', 'urllib', 'uuid', 'xml', 'csv',
                                                                  'configparser', 'hashlib', 'io', 'zipfile', 'subprocess']:
                    result["standard_library"].append(line)
                # Check if third-party
                elif module in ['tqdm', 'colorama', 'requests', 'numpy', 'pandas', 'matplotlib', 'pytest',
                              'flask', 'django', 'sqlalchemy', 'boto3', 'click', 'pyyaml', 'pillow', 'tensorflow',
                              'torch', 'cv2', 'opencv', 'bs4', 'selenium', 'scrapy', 'kivy', 'pygame']:
                    result["third_party"].append(line)
                # Assume local import
                else:
                    result["local"].append(line)
            
            # Check if order is correct
            import_sections = []
            if result["standard_library"]:
                import_sections.append("standard_library")
            if result["third_party"]:
                import_sections.append("third_party")
            if result["local"]:
                import_sections.append("local")
            
            # Find all imports in order
            imports_in_order = []
            for line in import_lines:
                if line.strip().startswith('#'):
                    continue
                    
                if line.startswith('import '):
                    module = line.split()[1].split('.')[0]
                elif line.startswith('from '):
                    module = line.split()[1].split('.')[0]
                else:
                    continue
                
                if module in sys.builtin_module_names or module in ['os', 'sys', 're', 'time', 'json', 'logging',
                                                                  'argparse', 'datetime', 'math', 'random', 'collections',
                                                                  'functools', 'itertools', 'pathlib', 'shutil', 'tempfile',
                                                                  'typing', 'unittest', 'urllib', 'uuid', 'xml', 'csv',
                                                                  'configparser', 'hashlib', 'io', 'zipfile', 'subprocess']:
                    imports_in_order.append("standard_library")
                elif module in ['tqdm', 'colorama', 'requests', 'numpy', 'pandas', 'matplotlib', 'pytest',
                              'flask', 'django', 'sqlalchemy', 'boto3', 'click', 'pyyaml', 'pillow', 'tensorflow',
                              'torch', 'cv2', 'opencv', 'bs4', 'selenium', 'scrapy', 'kivy', 'pygame']:
                    imports_in_order.append("third_party")
                else:
                    imports_in_order.append("local")
            
            # Check for correct order of sections
            expected_order = ['standard_library', 'third_party', 'local']
            current_section_idx = -1
            
            for section in imports_in_order:
                section_idx = expected_order.index(section)
                if section_idx < current_section_idx:
                    result["organized"] = False
                    break
                current_section_idx = section_idx
                
        except Exception as e:
            logging.debug(f"Error checking import organization: {str(e)}", exc_info=True)
            result["organized"] = False
            
        return result
    
    def _check_function_docstrings(self, content: str) -> Dict[str, Any]:
        """Check if all functions and methods have proper docstrings.
        
        Args:
            content: File content
            
        Returns:
            Dictionary with docstring check results
        """
        result = {
            "all_documented": True,
            "total_count": 0,
            "documented_count": 0,
            "missing_count": 0,
            "undocumented_functions": []
        }
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            # Find all function and method definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result["total_count"] += 1
                    
                    # Skip private methods/functions
                    if node.name.startswith('_') and node.name != '__init__':
                        result["documented_count"] += 1
                        continue
                    
                    # Check for docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        result["documented_count"] += 1
                    else:
                        result["missing_count"] += 1
                        result["undocumented_functions"].append(node.name)
            
            result["all_documented"] = result["missing_count"] == 0
        except Exception as e:
            logging.debug(f"Error checking function docstrings: {str(e)}", exc_info=True)
            result["all_documented"] = False
            
        return result
    
    def _check_type_hints(self, content: str) -> Dict[str, Any]:
        """Check if functions and methods have proper type hints.
        
        Args:
            content: File content
            
        Returns:
            Dictionary with type hint check results
        """
        result = {
            "all_typed": True,
            "total_functions": 0,
            "typed_functions": 0,
            "missing_count": 0,
            "untyped_functions": []
        }
        
        try:
            # Parse the AST
            tree = ast.parse(content)
            
            # Find all function and method definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private methods/functions
                    if node.name.startswith('_') and node.name != '__init__':
                        continue
                        
                    result["total_functions"] += 1
                    
                    # Check for return type annotation
                    has_return_type = node.returns is not None
                    
                    # Check for parameter type annotations
                    all_params_typed = True
                    for arg in node.args.args:
                        if arg.name == 'self' or arg.name == 'cls':
                            continue
                        if arg.annotation is None:
                            all_params_typed = False
                            break
                    
                    # Function is considered typed if it has return type and all params typed
                    if has_return_type and all_params_typed:
                        result["typed_functions"] += 1
                    else:
                        result["missing_count"] += 1
                        result["untyped_functions"].append(node.name)
            
            result["all_typed"] = result["missing_count"] == 0
        except Exception as e:
            logging.debug(f"Error checking type hints: {str(e)}", exc_info=True)
            result["all_typed"] = False
            
        return result
    
    def scan_script(self, script_path: Path) -> Dict[str, Any]:
        """Scan a script for standards compliance.
        
        Args:
            script_path: Path to the script to scan
            
        Returns:
            Dictionary containing scan results
        """
        result = {
            "file": str(script_path),
            "compliant": True,
            "missing_standards": [],
            "compliance_score": 0.0,
            "error": None,
        }
        
        try:
            # Read file content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for standards compliance
            standards_results = {}
            
            # Check imports
            imports = self.extract_imports(content)
            required_imports_found = [imp for imp in CONFIG["required_imports"] if imp in imports]
            recommended_imports_found = [imp for imp in CONFIG["recommended_imports"] if imp in imports]
            
            standards_results["imports"] = {
                "required": {
                    "total": len(CONFIG["required_imports"]),
                    "found": len(required_imports_found),
                    "missing": [imp for imp in CONFIG["required_imports"] if imp not in imports],
                },
                "recommended": {
                    "total": len(CONFIG["recommended_imports"]),
                    "found": len(recommended_imports_found),
                    "missing": [imp for imp in CONFIG["recommended_imports"] if imp not in imports],
                },
            }
            
            # Check visual elements
            visual_elements_found = [pattern for pattern in CONFIG["visual_elements"] if pattern in content]
            standards_results["visual_elements"] = {
                "total": len(CONFIG["visual_elements"]),
                "found": len(visual_elements_found),
                "missing": [pattern for pattern in CONFIG["visual_elements"] if pattern not in content],
            }
            
            # Check performance patterns
            performance_patterns_found = [pattern for pattern in CONFIG["performance_patterns"] if pattern in content]
            standards_results["performance_patterns"] = {
                "total": len(CONFIG["performance_patterns"]),
                "found": len(performance_patterns_found),
                "missing": [pattern for pattern in CONFIG["performance_patterns"] if pattern not in content],
            }
            
            # Check error handling patterns
            error_handling_patterns_found = [pattern for pattern in CONFIG["error_handling_patterns"] if pattern in content]
            standards_results["error_handling_patterns"] = {
                "total": len(CONFIG["error_handling_patterns"]),
                "found": len(error_handling_patterns_found),
                "missing": [pattern for pattern in CONFIG["error_handling_patterns"] if pattern not in content],
            }
            
            # Check code structure patterns
            code_structure_patterns_found = [pattern for pattern in CONFIG["code_structure_patterns"] if pattern in content]
            standards_results["code_structure_patterns"] = {
                "total": len(CONFIG["code_structure_patterns"]),
                "found": len(code_structure_patterns_found),
                "missing": [pattern for pattern in CONFIG["code_structure_patterns"] if pattern not in content],
            }
            
            # Check configuration patterns
            configuration_patterns_found = [pattern for pattern in CONFIG["configuration_patterns"] if pattern in content]
            standards_results["configuration_patterns"] = {
                "total": len(CONFIG["configuration_patterns"]),
                "found": len(configuration_patterns_found),
                "missing": [pattern for pattern in CONFIG["configuration_patterns"] if pattern not in content],
            }
            
            # Check logging patterns
            logging_patterns_found = [pattern for pattern in CONFIG["logging_patterns"] if pattern in content]
            standards_results["logging_patterns"] = {
                "total": len(CONFIG["logging_patterns"]),
                "found": len(logging_patterns_found),
                "missing": [pattern for pattern in CONFIG["logging_patterns"] if pattern not in content],
            }
            
            # Check user experience patterns
            user_experience_patterns_found = [pattern for pattern in CONFIG["user_experience_patterns"] if pattern in content]
            standards_results["user_experience_patterns"] = {
                "total": len(CONFIG["user_experience_patterns"]),
                "found": len(user_experience_patterns_found),
                "missing": [pattern for pattern in CONFIG["user_experience_patterns"] if pattern not in content],
            }
            
            # Calculate compliance score
            total_patterns = 0
            found_patterns = 0
            
            # Required imports are weighted more heavily
            total_patterns += len(CONFIG["required_imports"]) * 2
            found_patterns += len(required_imports_found) * 2
            
            # Other patterns
            for category in ["recommended_imports", "visual_elements", "performance_patterns", 
                            "error_handling_patterns", "code_structure_patterns", 
                            "configuration_patterns", "logging_patterns", "user_experience_patterns"]:
                if category == "recommended_imports":
                    total_patterns += len(CONFIG["recommended_imports"])
                    found_patterns += len(recommended_imports_found)
                else:
                    total_patterns += standards_results[category]["total"]
                    found_patterns += standards_results[category]["found"]
            
            compliance_score = found_patterns / total_patterns if total_patterns > 0 else 0.0
            result["compliance_score"] = compliance_score
            
            # Determine compliance
            if compliance_score < 0.5:
                result["compliant"] = False
                
                # Collect missing standards
                for category, data in standards_results.items():
                    if category == "imports":
                        if data["required"]["missing"]:
                            result["missing_standards"].append(f"Required imports: {', '.join(data['required']['missing'])}")
                        if data["recommended"]["missing"]:
                            result["missing_standards"].append(f"Recommended imports: {', '.join(data['recommended']['missing'])}")
                    else:
                        if data["missing"]:
                            result["missing_standards"].append(f"{category.replace('_', ' ').title()}: {', '.join(data['missing'])}")
            
            # Store detailed results
            result["standards_results"] = standards_results
            
        except Exception as e:
            result["error"] = str(e)
            result["compliant"] = False
            logger.error(f"Error scanning {script_path}: {str(e)}")
            self.stats["errors"] += 1
        
        return result
    
    def extract_imports(self, content: str) -> List[str]:
        """Extract imports from Python code.
        
        Args:
            content: Python code content
            
        Returns:
            List of imported modules
        """
        imports = []
        
        try:
            # Parse the code
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
        except Exception as e:
            logger.warning(f"Error parsing code for imports: {str(e)}")
            
            # Fallback to regex
            import_regex = re.compile(r'^import\s+(\w+)|^from\s+(\w+)', re.MULTILINE)
            for match in import_regex.finditer(content):
                module = match.group(1) or match.group(2)
                if module:
                    imports.append(module)
        
        return imports
    
    def scan_scripts(self) -> List[Dict[str, Any]]:
        """Scan scripts for standards compliance.
        
        Returns:
            List of scan results
        """
        scripts = self.find_scripts()
        
        logger.info(f"Scanning {len(scripts)} scripts for standards compliance")
        
        progress = tqdm(
            total=len(scripts),
            desc=f"{Fore.CYAN}Scanning scripts{Style.RESET_ALL}",
            unit="scripts",
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        
        for script_path in scripts:
            result = self.scan_script(script_path)
            self.results.append(result)
            
            # Update statistics
            self.stats["files_scanned"] += 1
            if result["compliant"]:
                self.stats["compliant_files"] += 1
            else:
                self.stats["non_compliant_files"] += 1
            
            # Update progress
            progress.update(1)
        
        progress.close()
        
        return self.results
    
    def generate_report(self) -> Path:
        """Generate a comprehensive report of the scan results.
        
        Returns:
            Path to the generated report
        """
        # Create report directory if it doesn't exist
        report_dir = self.base_path / "docs" / "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"script_standards_scan_{timestamp}.md"
        
        # Sort results by compliance score
        sorted_results = sorted(self.results, key=lambda x: x["compliance_score"])
        
        # Group by directory
        dir_groups = defaultdict(list)
        for result in self.results:
            file_path = Path(result["file"])
            try:
                # Check if base_path is part of the file path
                if str(self.base_path) in str(file_path):
                    parent = str(file_path.parent.relative_to(self.base_path))
                else:
                    parent = str(file_path.parent)
                dir_groups[parent].append(result)
            except Exception as e:
                logger.warning(f"Error grouping file {file_path}: {str(e)}")
                # Use a fallback group
                if "Other" not in dir_groups:
                    dir_groups["Other"] = []
                dir_groups["Other"].append(result)
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            # Title and metadata with EGOS styling
            f.write(f"# EGOS Script Standards Scan Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Part of:** Cross-Reference Standardization Initiative (Phase 4: Automated Compliance Checking)\n\n")
            
            # Executive summary with enhanced formatting
            f.write(f"## 📊 Executive Summary\n\n")
            f.write(f"This report presents the results of scanning EGOS scripts for standards compliance.\n\n")
            f.write(f"- **Files Scanned:** {self.stats['files_scanned']:,}\n")
            f.write(f"- **Compliant Files:** {self.stats['compliant_files']:,} ({self.stats['compliant_files'] / self.stats['files_scanned'] * 100:.1f}%)\n")
            f.write(f"- **Non-Compliant Files:** {self.stats['non_compliant_files']:,} ({self.stats['non_compliant_files'] / self.stats['files_scanned'] * 100:.1f}%)\n")
            f.write(f"- **Errors:** {self.stats['errors']:,}\n")
            f.write(f"- **Processing Time:** {format_time(self.stats['processing_time'])}\n\n")
            
            # Compliance by directory
            f.write(f"## 📁 Compliance by Directory\n\n")
            f.write(f"| Directory | Files | Compliant | Non-Compliant | Compliance Rate |\n")
            f.write(f"|-----------|-------|-----------|---------------|----------------|\n")
            
            for parent, results in sorted(dir_groups.items(), key=lambda x: len(x[1]), reverse=True):
                total = len(results)
                compliant = sum(1 for r in results if r["compliant"])
                non_compliant = total - compliant
                compliance_rate = compliant / total if total > 0 else 0.0
                
                f.write(f"| {parent} | {total} | {compliant} | {non_compliant} | {compliance_rate:.1%} |\n")
            
            # Top non-compliant files
            f.write(f"\n## ⚠️ Top Non-Compliant Files\n\n")
            f.write(f"The following files have the lowest compliance scores and should be prioritized for updates:\n\n")
            f.write(f"| File | Compliance Score | Missing Standards |\n")
            f.write(f"|------|-----------------|-------------------|\n")
            
            for result in sorted_results[:20]:
                if not result["compliant"]:
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    missing = "<br>".join(result["missing_standards"][:5])
                    if len(result["missing_standards"]) > 5:
                        missing += f"<br>...and {len(result['missing_standards']) - 5} more"
                    
                    f.write(f"| {rel_path} | {result['compliance_score']:.1%} | {missing} |\n")
            
            # Top compliant files
            f.write(f"\n## ✅ Top Compliant Files\n\n")
            f.write(f"The following files have the highest compliance scores and can serve as examples:\n\n")
            f.write(f"| File | Compliance Score |\n")
            f.write(f"|------|------------------|\n")
            
            for result in sorted(sorted_results, key=lambda x: x["compliance_score"], reverse=True)[:10]:
                if result["compliant"]:
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    f.write(f"| {rel_path} | {result['compliance_score']:.1%} |\n")
            
            # Standards compliance breakdown
            f.write(f"\n## 📈 Standards Compliance Breakdown\n\n")
            
            # Calculate compliance by standard
            standards_compliance = defaultdict(lambda: {"total": 0, "found": 0})
            
            for result in self.results:
                if "standards_results" in result:
                    for category, data in result["standards_results"].items():
                        if category == "imports":
                            standards_compliance["required_imports"]["total"] += data["required"]["total"]
                            standards_compliance["required_imports"]["found"] += data["required"]["found"]
                            standards_compliance["recommended_imports"]["total"] += data["recommended"]["total"]
                            standards_compliance["recommended_imports"]["found"] += data["recommended"]["found"]
                        else:
                            standards_compliance[category]["total"] += data["total"]
                            standards_compliance[category]["found"] += data["found"]
            
            f.write(f"| Standard | Compliance Rate |\n")
            f.write(f"|----------|----------------|\n")
            
            for category, data in sorted(standards_compliance.items(), key=lambda x: x[0]):
                compliance_rate = data["found"] / data["total"] if data["total"] > 0 else 0.0
                category_name = category.replace("_", " ").title()
                f.write(f"| {category_name} | {compliance_rate:.1%} |\n")
            
            # Next steps
            f.write(f"\n## 🚀 Next Steps\n\n")
            f.write(f"1. **Update non-compliant scripts** starting with the lowest compliance scores\n")
            f.write(f"2. **Use the script template generator** to create new scripts with pre-applied standards\n")
            f.write(f"3. **Add script standards compliance checks** to the CI/CD pipeline\n")
            f.write(f"4. **Re-run this scan periodically** to track progress\n\n")
            
            # Add EGOS signature
            f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    def run(self) -> Path:
        """Run the standards scanner.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Scan scripts
        self.scan_scripts()
        
        # Generate report
        report_path = self.generate_report()
        
        # Update statistics
        self.stats["processing_time"] = time.time() - start_time
        
        return report_path

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Scan EGOS scripts for standards compliance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--base-path",
        default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        help="Base path to scan (default: EGOS root)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information"
    )
    
    parser.add_argument(
        "--batch-scan",
        action="store_true",
        help="Enable batch scanning of all scripts in the codebase"
    )
    
    parser.add_argument(
        "--target-dir",
        help="Specific directory to scan instead of the entire codebase"
    )
    
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate an HTML report with enhanced visualization and interactive features"
    )
    
    parser.add_argument(
        "--auto-templates",
        action="store_true",
        help="Automatically generate template files for non-compliant scripts"
    )
    
    parser.add_argument(
        "--min-score",
        type=float,
        default=60.0,
        help="Minimum compliance score threshold for generating templates (default: 60.0)"
    )
    
    parser.add_argument(
        "--include-pattern",
        help="Only scan files matching this pattern (e.g., '*.py')"
    )
    
    parser.add_argument(
        "--exclude-pattern",
        help="Exclude files matching this pattern (e.g., 'test_*.py')"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner(
        "EGOS Script Standards Scanner",
        f"Scanning for compliance with EGOS script standards"
    )
    
    # Set the base path for scanning
    base_path = args.target_dir if args.target_dir else args.base_path
    
    # Create and run the standards scanner
    scanner = StandardsScanner(
        base_path=base_path,
        verbose=args.verbose,
        include_pattern=args.include_pattern,
        exclude_pattern=args.exclude_pattern,
        html_report=args.html_report
    )
    
    try:
        # Run the scanner
        if args.batch_scan:
            print(f"{Fore.CYAN}Initiating batch scan of the entire codebase...{Style.RESET_ALL}")
            # This will scan all scripts in the specified directory and subdirectories
        
        report_path = scanner.run()
        
        # Display summary statistics
        logger.info(f"\n{Fore.GREEN}Script standards scan completed successfully!{Style.RESET_ALL}")
        logger.info(f"  • {Fore.CYAN}Files scanned:{Style.RESET_ALL} {scanner.stats['files_scanned']:,}")
        logger.info(f"  • {Fore.CYAN}Compliant files:{Style.RESET_ALL} {scanner.stats['compliant_files']:,} ({scanner.stats['compliant_files'] / scanner.stats['files_scanned'] * 100:.1f}%)")
        logger.info(f"  • {Fore.CYAN}Non-compliant files:{Style.RESET_ALL} {scanner.stats['non_compliant_files']:,} ({scanner.stats['non_compliant_files'] / scanner.stats['files_scanned'] * 100:.1f}%)")
        logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {scanner.stats['errors']:,}")
        logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(scanner.stats['processing_time'])}")
        logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
        
        # Auto-generate templates if requested
        if args.auto_templates and scanner.stats['non_compliant_files'] > 0:
            print(f"{Fore.YELLOW}\nGenerating templates for non-compliant scripts...{Style.RESET_ALL}")
            template_results = generate_templates_for_non_compliant(scanner.results, args.min_score)
            logger.info(f"  • {Fore.CYAN}Templates generated:{Style.RESET_ALL} {template_results['generated']}")
            logger.info(f"  • {Fore.CYAN}Templates skipped:{Style.RESET_ALL} {template_results['skipped']} (compliance score above threshold)")
            logger.info(f"  • {Fore.CYAN}Template generation errors:{Style.RESET_ALL} {template_results['errors']}")
            logger.info(f"  • {Fore.CYAN}Templates directory:{Style.RESET_ALL} {template_results['output_dir']}")
        
        # Suggest next steps
        print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
        print(f"1. Review the {'HTML ' if args.html_report else ''}report at {report_path}")
        print(f"2. Update non-compliant scripts starting with the lowest compliance scores")
        if not args.auto_templates:
            print(f"3. Use the script template generator to create new scripts with pre-applied standards:")
            print(f"   python script_template_generator.py --name script_name.py --description \"Script purpose\"")
        else:
            print(f"3. Review the generated templates in {template_results['output_dir'] if 'output_dir' in template_results else 'templates directory'}")
        print(f"4. Run this scanner with batch mode to monitor progress: python script_standards_scanner.py --batch-scan --html-report")
        
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running standards scanner: {str(e)}")
        logger.debug("Error details:", exc_info=True)
        sys.exit(1)


def generate_templates_for_non_compliant(results: List[Dict[str, Any]], min_score: float = 60.0) -> Dict[str, Any]:
    """Generate template files for non-compliant scripts.
    
    Args:
        results: List of scan results
        min_score: Minimum compliance score threshold for generating templates
        
    Returns:
        Dictionary with template generation results
    """
    import subprocess
    from pathlib import Path
    
    output_stats = {
        "generated": 0,
        "skipped": 0,
        "errors": 0,
        "output_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    }
    
    # Ensure templates directory exists
    os.makedirs(output_stats["output_dir"], exist_ok=True)
    
    # Find the script_template_generator.py path
    template_generator_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_template_generator.py")
    
    # Generate templates for non-compliant scripts
    progress = tqdm(
        total=len([r for r in results if not r.get("compliant", True)]),
        desc=f"{Fore.CYAN}Generating templates{Style.RESET_ALL}",
        unit="templates",
        ncols=TERMINAL_WIDTH - 20,
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
    )
    
    for result in results:
        if not result.get("compliant", True):
            # Skip if compliance score is above threshold
            if result.get("compliance_score", 0) * 100 > min_score:
                output_stats["skipped"] += 1
                progress.update(1)
                continue
            
            try:
                file_path = Path(result["file"])
                script_name = file_path.name
                script_description = f"Compliant version of {script_name}"
                
                # Generate template
                cmd = [
                    sys.executable,
                    template_generator_path,
                    "--name", f"compliant_{script_name}",
                    "--description", script_description,
                    "--output-dir", output_stats["output_dir"]
                ]
                
                # Add options based on script analysis
                if "class " in open(file_path, "r", encoding="utf-8").read():
                    # Script has classes, so include class in template
                    pass  # Default is to include class
                else:
                    cmd.append("--no-class")
                
                # Check for async patterns
                if "async " in open(file_path, "r", encoding="utf-8").read() or "await " in open(file_path, "r", encoding="utf-8").read():
                    cmd.append("--async")
                
                # Run template generator
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_stats["generated"] += 1
            except Exception as e:
                logger.warning(f"Error generating template for {result['file']}: {str(e)}")
                output_stats["errors"] += 1
            finally:
                progress.update(1)
    
    progress.close()
    return output_stats

if __name__ == "__main__":
    main()