#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Centralized Tool Runner

This script provides a centralized interface for discovering and running tools
in the EGOS ecosystem. It dynamically scans for available tools, presents them
to the user, and executes the selected tool with the provided arguments.

It acts as a single entry point for validation, maintenance, and utility scripts,
making it easier for developers to discover and use the available tools.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

Usage:
    python run_tools.py                  # Show interactive menu of available tools
    python run_tools.py --list           # List all available tools
    python run_tools.py --run TOOL_ID    # Run a specific tool by ID
    python run_tools.py --category CAT   # List tools in a specific category
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS Run Tools - Centralized tool management and execution system

This script provides a unified interface to discover, browse, and execute 
tools across the EGOS ecosystem. It automatically discovers scripts, reads from 
the tool registry, and provides a standardized way to find and run scripts with 
proper documentation. It's the central access point for all EGOS tools and scripts.

Author: EGOS Development Team
Created: 2025-05-22
Version: 2.0.0

@references:
- C:\EGOS\config\tool_registry.json
- C:\EGOS\scripts\cross_reference\script_standards_scanner.py
- C:\EGOS\scripts\cross_reference\script_template_generator.py
- C:\EGOS\scripts\cross_reference\integration\koios_standards.py
- C:\EGOS\docs\process\ai_handover_standard.mdc
- C:\EGOS\WORK_2025_05_22_run_tools_enhancement.md
"""

# Standard library imports
import os
import sys
import json
import re
import time
import logging
import argparse
import inspect
import importlib.util
import subprocess
import glob
import fnmatch
import textwrap
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from collections import defaultdict, Counter

# Third-party imports
try:
    from tqdm import tqdm
    HAVE_TQDM = True
except ImportError:
    HAVE_TQDM = False

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
TERMINAL_WIDTH = 120
DEFAULT_REGISTRY_PATH = os.path.join('config', 'tool_registry.json')
DEFAULT_REPORTS_DIR = os.path.join('reports', 'tools')
VERSION = '2.0.0'
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_WORKERS = 4
DEFAULT_TIMEOUT = 30  # seconds

# Configuration
CONFIG = {
    # Core settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'run_tools.log'),
    "log_level": "INFO",
    "registry_path": DEFAULT_REGISTRY_PATH,
    "auto_discover": True,
    
    # Auto-discovery settings
    "script_root_dirs": ["scripts", "tools"],
    "script_patterns": ["*.py"],
    "exclude_patterns": ["__pycache__/*", "*/__pycache__/*", "*/venv/*", "*/tests/*", "*_test.py"],
    
    # Display settings
    "use_color": HAVE_COLORAMA,
    "use_progress_bars": HAVE_TQDM,
    "terminal_width": 80,
    
    # Performance settings
    "batch_size": DEFAULT_BATCH_SIZE,
    "max_workers": DEFAULT_MAX_WORKERS,
    "timeout": DEFAULT_TIMEOUT,
    
    # Report generation settings
    "generate_report": True,
    "reports_dir": DEFAULT_REPORTS_DIR,
    "website_integration": True,
    "website_tools_dir": os.path.join('website', 'content', 'tools'),
}

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("run_tools")

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)


def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    if not CONFIG["use_color"]:
        # Simple ASCII banner
        print("=" * width)
        print(f"{title.center(width)}")
        if subtitle:
            print(f"{subtitle.center(width)}")
        print("=" * width)
        print()
        return
    
    # Colorful banner with box drawing characters
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{Style.BRIGHT}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
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


class ToolRunner:
    """
    Centralized runner for EGOS tools and scripts.
    
    Discovers tools from the registry, allows selection, and runs the selected tool.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the tool runner.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = base_path
        self.registry_path = base_path / 'config' / 'tool_registry.json'
        self.tools_cache = None
        self.discovered_scripts = []
        self.report_path = None
        self.stats = {
            "total_tools": 0,
            "active_tools": 0,
            "inactive_tools": 0,
            "deprecated_tools": 0,
            "experimental_tools": 0,
            "discovered_scripts": 0,
            "categories": {},
            "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": 0
        }
        
        # Create reports directory if it doesn't exist
        self.reports_dir = self.base_path / CONFIG["reports_dir"]
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def load_registry(self) -> List[Dict[str, Any]]:
        """
        Load the tool registry data.
        
        Returns:
            List of tool entries from the registry
        """
        if self.tools_cache is not None:
            return self.tools_cache
            
        if not self.registry_path.exists():
            print(f"{Colors.YELLOW}Warning: Registry file not found at {self.registry_path}{Colors.ENDC}")
            print(f"Would you like to scan the codebase for tools? (y/n)")
            response = input().strip().lower()
            
            if response == 'y':
                self.discover_tools()
            
            return []
            
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tools_cache = data.get('tools', [])
                return self.tools_cache
        except Exception as e:
            print(f"{Colors.RED}Error loading registry: {e}{Colors.ENDC}")
            return []
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover tools by scanning the codebase.
        
        Returns:
            List of discovered tools
        """
        print(f"{Colors.CYAN}Scanning codebase for tools...{Colors.ENDC}")
        
        try:
            # Check if registry populator exists
            populator_path = self.base_path / 'scripts' / 'registry' / 'registry_populator.py'
            
            if populator_path.exists():
                print(f"{Colors.CYAN}Running registry populator to discover tools...{Colors.ENDC}")
                result = subprocess.run(
                    [sys.executable, str(populator_path), '--scan-all'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Tool discovery completed successfully.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Error during tool discovery: {result.stderr}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}Registry populator not found. Performing basic discovery...{Colors.ENDC}")
                self._perform_basic_discovery()
                
            # Reload the registry
            self.tools_cache = None
            return self.load_registry()
            
        except Exception as e:
            print(f"{Colors.RED}Error during tool discovery: {e}{Colors.ENDC}")
            return []
    
    def _perform_basic_discovery(self):
        """Perform basic tool discovery by scanning scripts directory."""
        scripts_dir = self.base_path / 'scripts'
        discovered = []
        
        if not scripts_dir.exists():
            return
            
        # Look for Python files with a main function
        for py_file in scripts_dir.glob('**/*.py'):
            # Skip __init__.py and test files
            if py_file.name == '__init__.py' or 'test' in py_file.name.lower():
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple heuristic: has a main function or command-line interface
                    if 'def main' in content or 'if __name__ == "__main__"' in content:
                        rel_path = py_file.relative_to(self.base_path)
                        name = ' '.join(word.capitalize() for word in py_file.stem.split('_'))
                        
                        discovered.append({
                            'id': py_file.stem.replace('_', '-'),
                            'name': name,
                            'path': str(rel_path).replace('\\', '/'),
                            'description': f"Tool at {rel_path}",
                            'category': self._guess_category(py_file)
                        })
            except Exception:
                pass
                
        print(f"{Fore.GREEN}Discovered {len(discovered)} potential tools.{Style.RESET_ALL}")
        
        # Return the discovered tools
        return discovered
        
    def save_registry(self, tools: List[Dict[str, Any]]) -> bool:
        """Save the tool registry to the JSON file.
        
        Args:
            tools: List of tool entries to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            
            # Update the registry data
            self._registry_data["tools"] = tools
            self._registry_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            self._registry_data["updated_by"] = "EGOS Run Tools"
            
            # Write to file
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self._registry_data, f, indent=2)
                
            # Update mtime
            self._registry_mtime = os.path.getmtime(self.registry_path)
            return True
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
            return False
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available tools, optionally filtered by category.
        
        If auto-discovery is enabled, this will also include any newly discovered
        scripts not yet in the registry.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of tool entries
        """
        # Load existing tools
        tools = self.load_registry()
        
        # Auto-discover if enabled
        if CONFIG["auto_discover"]:
            self.discover_scripts()
            
            # Add discovered scripts not yet in registry
            registered_paths = {t.get('path', '').lower() for t in tools}
            for script in self.discovered_scripts:
                rel_path = os.path.relpath(script, os.getcwd())
                rel_path = rel_path.replace('\\', '/')
                
                if rel_path.lower() not in registered_paths:
                    # Extract basic info and add to tools list
                    info = self.extract_script_info(script)
                    if info:
                        # Create basic tool entry
                        tool_entry = {
                            "id": info.get("id", ""),
                            "name": info.get("name", ""),
                            "path": rel_path,
                            "description": info.get("description", "Auto-discovered script"),
                            "category": info.get("category", self.guess_category(rel_path)),
                            "status": "inactive",  # Mark as inactive until verified
                            "created": datetime.now().strftime("%Y-%m-%d"),
                            "last_updated": datetime.now().strftime("%Y-%m-%d"),
                            "auto_discovered": True
                        }
                        tools.append(tool_entry)
                        registered_paths.add(rel_path.lower())
        
        # Apply category filter if specified
        if category:
            tools = [t for t in tools if t.get('category', '').lower() == category.lower()]
            
        return tools
        
    def discover_scripts(self) -> None:
        """Discover Python scripts in the codebase."""
        self.discovered_scripts = []
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    script_path = os.path.join(root, file)
                    self.discovered_scripts.append(script_path)
                    
        self.stats["discovered_scripts"] = len(self.discovered_scripts)
        
    def extract_script_info(self, script_path: str) -> Dict[str, Any]:
        """Extract basic information from a Python script."""
        info = {}
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract docstring
                docstring = ast.get_docstring(ast.parse(content))
                if docstring:
                    info["description"] = docstring
                
                # Extract tool ID and name
                tree = ast.parse(content)
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == 'main':
                        info["id"] = node.name
                        info["name"] = node.name.capitalize()
                        break
        except Exception as e:
            logger.error(f"Error extracting info from {script_path}: {e}")
            
        return info
        
    def guess_category(self, script_path: str) -> str:
        """Guess the category of a script based on its path."""
        path_str = script_path.lower()
        
        if 'valid' in path_str or 'check' in path_str or 'lint' in path_str:
            return 'Validation'
        elif 'test' in path_str:
            return 'Testing'
        elif 'document' in path_str or 'doc' in path_str:
            return 'Documentation'
        elif 'visual' in path_str or 'graph' in path_str or 'chart' in path_str:
            return 'Visualization'
        elif 'maint' in path_str or 'clean' in path_str:
            return 'Maintenance'
        else:
            return 'Utility'
    
    def discover_scripts(self) -> List[str]:
        """Discover Python scripts in the EGOS codebase.
        
        Automatically scans the codebase for Python scripts based on the configured patterns
        and exclusion rules. This ensures all scripts are discoverable through the tools system.
        
        Returns:
            List of discovered script paths
        """
        start_time = time.time()
        self.discovered_scripts = []
        
        # Define patterns to include and exclude
        include_patterns = CONFIG["script_patterns"]
        exclude_patterns = CONFIG["exclude_patterns"]
        root_dirs = CONFIG["script_root_dirs"]
        
        # Create a set of normalized exclusion patterns
        exclusion_set = set()
        for pattern in exclude_patterns:
            exclusion_set.add(pattern.lower().replace('\\', '/').strip())
        
        # Discover scripts in each root directory
        for root_dir in root_dirs:
            if not os.path.exists(root_dir):
                continue
                
            logger.debug(f"Scanning directory: {root_dir}")
            for root, dirs, files in os.walk(root_dir):
                # Check if this directory should be excluded
                rel_path = os.path.relpath(root, os.getcwd()).replace('\\', '/')
                if any(rel_path.lower().startswith(p.rstrip('/*').lower()) for p in exclusion_set if '*' not in p):
                    continue
                
                # Process files in this directory
                for file in files:
                    # Check if file matches include patterns
                    if not any(fnmatch.fnmatch(file.lower(), p.lower()) for p in include_patterns):
                        continue
                        
                    # Get full path and normalize for comparison
                    file_path = os.path.join(root, file)
                    norm_path = file_path.replace('\\', '/')
                    
                    # Check exclusion patterns
                    if any(fnmatch.fnmatch(norm_path.lower(), p.lower()) for p in exclusion_set):
                        continue
                        
                    # Add script to discovered list
                    self.discovered_scripts.append(file_path)
        
        # Update stats
        self.stats["discovered_scripts"] = len(self.discovered_scripts)
        self.stats["discovery_time"] = time.time() - start_time
        
        logger.info(f"Discovered {len(self.discovered_scripts)} scripts in {format_time(self.stats['discovery_time'])}")
        return self.discovered_scripts
    
    def extract_script_info(self, script_path: str) -> Dict[str, Any]:
        """Extract detailed information from a Python script.
        
        Parses the script to extract metadata including docstrings, function definitions,
        imports, and other key information to create a rich tool entry.
        
        Args:
            script_path: Path to the script to analyze
            
        Returns:
            Dictionary containing extracted metadata
        """
        info = {
            "id": "",
            "name": "",
            "description": "",
            "category": "",
            "usage": "",
            "tags": []
        }
        
        try:
            # Read file content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic info from filename
            basename = os.path.basename(script_path)
            name_parts = basename.replace('.py', '').split('_')
            info["id"] = basename.replace('.py', '').lower().replace(' ', '-')
            info["name"] = ' '.join(word.capitalize() for word in name_parts)
            
            # Try to parse as Python code
            try:
                tree = ast.parse(content)
                
                # Extract docstring
                module_docstring = ast.get_docstring(tree)
                if module_docstring:
                    # First line as name if not empty
                    docstring_lines = module_docstring.split('\n')
                    if docstring_lines and docstring_lines[0].strip():
                        info["name"] = docstring_lines[0].strip()
                    
                    # Rest as description
                    if len(docstring_lines) > 1:
                        info["description"] = '\n'.join(line.strip() for line in docstring_lines[1:] if line.strip())
                
                # Look for @references in docstring
                if module_docstring and "@references" in module_docstring:
                    refs_section = module_docstring.split('@references')[1].strip()
                    if refs_section:
                        # Add cross-references to tags
                        info["tags"].append("cross-referenced")
                
                # Look for specific patterns in imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(n.name for n in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                # Tag based on imports
                if any(imp in ['tqdm', 'progressbar'] for imp in imports):
                    info["tags"].append("progress-tracking")
                if 'concurrent.futures' in imports:
                    info["tags"].append("parallel-processing")
                if 'logging' in imports:
                    info["tags"].append("logging")
                if any(imp in ['colorama', 'termcolor'] for imp in imports):
                    info["tags"].append("color-output")
                
                # Extract main function for usage info
                main_func = None
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == 'main':
                        main_func = node
                        break
                
                if main_func:
                    # Look for argument parsing to infer usage
                    for node in ast.walk(main_func):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                            if node.func.attr == 'add_argument':
                                # This is an argparse argument
                                arg_str = ""
                                for arg in node.args:
                                    if isinstance(arg, ast.Str):
                                        arg_str += f"{arg.s} "
                                if arg_str and not info["usage"]:
                                    info["usage"] = f"python {script_path} {arg_str}"
            except SyntaxError:
                # Not valid Python or can't be parsed
                pass
            
            # Guess category based on path and content
            if not info["category"]:
                info["category"] = self.guess_category(script_path)
            
        except Exception as e:
            logger.error(f"Error extracting info from {script_path}: {e}")
        
        return info
    
    def guess_category(self, script_path: str) -> str:
        """Guess the category of a script based on its path and content.
        
        Uses heuristics to determine the most likely category for a script
        based on its location in the file system and key terms in the path.
        
        Args:
            script_path: Path to the script
            
        Returns:
            Category name
        """
        path_parts = script_path.lower().replace('\\', '/').split('/')
        
        # Check if in a category directory
        if len(path_parts) >= 2:
            dir_name = path_parts[-2]
            
            # Direct mappings
            category_mappings = {
                'maintenance': 'Maintenance',
                'cross_reference': 'Cross-Reference',
                'docs': 'Documentation',
                'diag': 'Diagnostics',
                'diagnostic': 'Diagnostics',
                'test': 'Testing',
                'validation': 'Validation',
                'util': 'Utility',
                'tools': 'Utility',
                'viz': 'Visualization',
                'visual': 'Visualization',
                'data': 'Data Processing'
            }
            
            # Check for exact matches
            for key, category in category_mappings.items():
                if key == dir_name:
                    return category
            
            # Check for partial matches
            for key, category in category_mappings.items():
                if key in dir_name:
                    return category
        
        # Check filename
        filename = os.path.basename(script_path).lower()
        
        if any(term in filename for term in ['valid', 'check', 'lint', 'analyze', 'test']):
            return 'Validation'
        elif any(term in filename for term in ['gen', 'create', 'make', 'build']):
            return 'Generation'
        elif any(term in filename for term in ['clean', 'fix', 'repair', 'maintain']):
            return 'Maintenance'
        elif any(term in filename for term in ['view', 'visual', 'display', 'show', 'plot', 'graph', 'viz']):
            return 'Visualization'
        elif any(term in filename for term in ['xref', 'reference', 'link', 'map']):
            return 'Cross-Reference'
        elif any(term in filename for term in ['doc', 'wiki', 'manual', 'help', 'guide']):
            return 'Documentation'
        
        # Default
        return 'Utility'
    
    def run_tool(self, tool_id: str, args: List[str] = None) -> int:
        """Run a specific tool by ID.
        
        Args:
            tool_id: ID of the tool to run
            args: Optional arguments to pass to the tool
            
        Returns:
            Exit code from the tool
        """
        if args is None:
            args = []
        
        # Find the tool
        tools = self.list_tools()
        tool = next((t for t in tools if t.get('id', '').lower() == tool_id.lower()), None)
        
        if not tool:
            logger.error(f"Tool '{tool_id}' not found")
            return 1
        
        # Get the path
        path = tool.get('path', None)
        if not path:
            logger.error(f"No path defined for tool '{tool_id}'")
            return 1
        
        # Check if the file exists
        if not os.path.exists(path):
            logger.error(f"Tool script not found at '{path}'")
            return 1
        
        # Execute the tool
        start_time = time.time()
        try:
            # Build command
            if path.endswith('.py'):
                cmd = [sys.executable, path] + args
            else:
                cmd = [path] + args
            
            # Log execution
            logger.info(f"Running tool: {' '.join(cmd)}")
            
            # Execute
            result = subprocess.run(cmd, capture_output=False)
            
            # Update stats
            self.stats["executed_tools"] += 1
            self.stats["last_execution_time"] = time.time() - start_time
            
            # Check result
            if result.returncode != 0:
                logger.error(f"Tool '{tool_id}' failed with exit code {result.returncode}")
                self.stats["execution_errors"] += 1
                return result.returncode
            
            logger.info(f"Tool '{tool_id}' completed successfully in {format_time(self.stats['last_execution_time'])}")
            return 0
        except Exception as e:
            logger.error(f"Error running tool '{tool_id}': {e}")
            self.stats["execution_errors"] += 1
            return 1
    
    def get_categories(self) -> List[str]:
        """Get all available categories.
        
        Returns:
            List of category names
        """
        tools = self.list_tools()
        categories = set()
        
        for tool in tools:
            cat = tool.get('category', 'Uncategorized')
            categories.add(cat)
            
        return sorted(list(categories))
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive HTML report of all tools and their status.
        
        Creates a detailed HTML report with tool information, categories, status,
        and statistics. The report is saved to the reports directory and can be
        opened in a web browser.
        
        Returns:
            Path to the generated report file
        """
        # Create timestamp for the report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"tools_report_{timestamp}.html"
        report_path = self.reports_dir / report_filename
        
        # Load tools
        tools = self.list_tools()
        
        # Update stats
        self.stats["total_tools"] = len(tools)
        self.stats["active_tools"] = sum(1 for t in tools if t.get('status', '').lower() == 'active')
        self.stats["inactive_tools"] = sum(1 for t in tools if t.get('status', '').lower() == 'inactive')
        self.stats["deprecated_tools"] = sum(1 for t in tools if t.get('status', '').lower() == 'deprecated')
        self.stats["experimental_tools"] = sum(1 for t in tools if t.get('status', '').lower() == 'experimental')
        
        # Group tools by category
        category_map = defaultdict(list)
        for tool in tools:
            cat = tool.get('category', 'Uncategorized')
            category_map[cat].append(tool)
            
        # Update category stats
        self.stats["categories"] = {cat: len(tools) for cat, tools in category_map.items()}
        
        # Generate HTML report
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='en'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append(f"    <title>EGOS Tools Report - {timestamp}</title>")
        html.append("    <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'>")
        html.append("    <style>")
        html.append("        /* EGOS Design System - Core Variables */")
        html.append("        :root {")
        html.append("            --primary-color: #0A2342; /* Deep Blue */")
        html.append("            --accent-color: #FF6600; /* Warm Orange */")
        html.append("            --background-color: #f8f9fa; /* Very light grey */")
        html.append("            --surface-color: #ffffff; /* White for cards/surfaces */")
        html.append("            --text-color: #333; /* Dark grey for text */")
        html.append("            --text-light: #666; /* Lighter grey text */")
        html.append("            --border-color: #e0e0e0; /* Light border color */")
        html.append("            --shadow-color: rgba(0, 0, 0, 0.08); /* Softer shadow */")
        html.append("            --hover-shadow-color: rgba(0, 0, 0, 0.12); /* Slightly more pronounced hover shadow */")
        html.append("            --text-on-primary: #ffffff; /* White text on dark blue */")
        html.append("            --text-on-accent: #ffffff; /* White text on orange */")
        html.append("            --spacing-unit: 8px;")
        html.append("            --border-radius-sm: 4px;")
        html.append("            --border-radius-md: 8px;")
        html.append("            --border-radius-lg: 12px;")
        html.append("        }")
        html.append("        body { font-family: 'Inter', sans-serif; line-height: 1.65; color: var(--text-color); max-width: 1200px; margin: 0 auto; padding: 20px; background-color: var(--background-color); }")
        html.append("        h1, h2, h3 { font-family: 'Playfair Display', serif; font-weight: 700; color: var(--primary-color); }")
        html.append("        h1 { text-align: center; margin-bottom: 30px; font-size: 2.5rem; }")
        html.append("        .header { text-align: center; margin-bottom: 40px; }")
        html.append("        .stats-container { display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 30px; }")
        html.append("        .stat-box { background-color: var(--surface-color); border-radius: var(--border-radius-md); padding: 15px; margin: 10px; min-width: 150px; box-shadow: 0 3px 10px var(--shadow-color); text-align: center; transition: transform 0.3s ease, box-shadow 0.3s ease; }")
        html.append("        .stat-box:hover { transform: translateY(-5px); box-shadow: 0 8px 18px var(--hover-shadow-color); }")
        html.append("        .stat-value { font-size: 24px; font-weight: bold; margin: 10px 0; color: var(--accent-color); }")
        html.append("        .stat-label { font-size: 14px; color: var(--text-light); }")
        html.append("        .category-section { margin-bottom: 40px; }")
        html.append("        .category-header { background-color: var(--primary-color); color: var(--text-on-primary); padding: 10px 15px; border-radius: var(--border-radius-md); }")
        html.append("        .tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-top: 20px; }")
        html.append("        .tool-card { background-color: var(--surface-color); border-radius: var(--border-radius-md); padding: 20px; box-shadow: 0 3px 10px var(--shadow-color); transition: transform 0.3s ease, box-shadow 0.3s ease; }")
        html.append("        .tool-card:hover { transform: translateY(-5px); box-shadow: 0 8px 18px var(--hover-shadow-color); }")
        html.append("        .tool-card.active-tool { border-left: 4px solid var(--accent-color); }")
        html.append("        .tool-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }")
        html.append("        .tool-title { margin: 0; font-size: 18px; color: var(--primary-color); }")
        html.append("        .tool-status { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }")
        html.append("        .status-active { background-color: #2ecc71; color: white; }")
        html.append("        .status-inactive { background-color: #95a5a6; color: white; }")
        html.append("        .status-deprecated { background-color: #e74c3c; color: white; }")
        html.append("        .status-experimental { background-color: #9b59b6; color: white; }")
        html.append("        .tool-description { margin-bottom: 15px; }")
        html.append("        .tool-meta { font-size: 14px; color: #7f8c8d; }")
        html.append("        .tool-path { font-family: monospace; background-color: #f5f5f5; padding: 5px; border-radius: 3px; margin-top: 10px; }")
        html.append("        .tool-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }")
        html.append("        .tool-tag { background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }")
        html.append("        .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 14px; }")
        html.append("        .egos-signature { text-align: center; font-size: 24px; color: #8e44ad; margin: 20px 0; }")
        html.append("        .search-container { margin-bottom: 30px; text-align: center; }")
        html.append("        #toolSearch { padding: 10px; width: 300px; border-radius: 20px; border: 1px solid #ddd; }")
        html.append("        .category-count { font-size: 14px; margin-left: 10px; color: #7f8c8d; }")
        html.append("        .contribute-button { display: inline-flex; align-items: center; justify-content: center; background-color: var(--accent-color); color: var(--text-on-accent); padding: 8px 15px; border-radius: 50px; text-decoration: none; margin-top: 10px; font-size: 14px; font-weight: 600; transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease; }")
        html.append("        .contribute-button:hover { background-color: #ff7d26; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(255, 102, 0, 0.3); }")
        html.append("        .contribute-button i { margin-right: 8px; }")
        html.append("        .utility-tag { background-color: #27ae60; }")
        html.append("        .context-tag { background-color: #f39c12; }")
        html.append("        .policy-tag { background-color: #e74c3c; }")
        html.append("        .roadmap-section { background-color: #f9f9f9; border-radius: 8px; padding: 20px; margin: 30px 0; }")
        html.append("        .roadmap-section h2 { color: #8e44ad; }")
        html.append("        .roadmap-item { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }")
        html.append("        .roadmap-item:last-child { border-bottom: none; }")
        html.append("        .roadmap-item h3 { margin-bottom: 5px; }")
        html.append("        .roadmap-item p { margin-bottom: 10px; }")
        html.append("        .policy-section { background-color: #f9f9f9; border-radius: 8px; padding: 20px; margin: 30px 0; }")
        html.append("        .policy-section h2 { color: #8e44ad; }")
        html.append("        .policy-link { display: inline-block; margin: 10px; text-decoration: none; color: #3498db; }")
        html.append("        .policy-link:hover { text-decoration: underline; }")
        html.append("        .filter-buttons { display: flex; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }")
        html.append("        .filter-button { background-color: var(--background-color); border: 1px solid var(--border-color); padding: 8px 15px; border-radius: 50px; cursor: pointer; font-weight: bold; transition: all 0.3s ease; }")
        html.append("        .filter-button.active { background-color: var(--primary-color); color: var(--text-on-primary); border-color: var(--primary-color); }")
        html.append("        .filter-button:hover { background-color: #e0e0e0; transform: translateY(-2px); }")
        html.append("        .filter-button.active:hover { background-color: #0d2d5a; }")
        html.append("    </style>")
        html.append("    <script>")
        html.append("        function searchTools() {")
        html.append("            const searchTerm = document.getElementById('toolSearch').value.toLowerCase();")
        html.append("            const toolCards = document.querySelectorAll('.tool-card');")
        html.append("            const categoryContainers = document.querySelectorAll('.category-section');")
        html.append("            const activeFilter = document.querySelector('.filter-button.active').dataset.status;")
        html.append("            ")
        html.append("            toolCards.forEach(card => {")
        html.append("                const toolName = card.querySelector('.tool-title').textContent.toLowerCase();")
        html.append("                const toolDescription = card.querySelector('.tool-description').textContent.toLowerCase();")
        html.append("                const toolPath = card.querySelector('.tool-path').textContent.toLowerCase();")
        html.append("                const toolTags = Array.from(card.querySelectorAll('.tool-tag')).map(tag => tag.textContent.toLowerCase());")
        html.append("                const toolStatus = card.dataset.status;")
        html.append("                ")
        html.append("                // Check if matches search term")
        html.append("                const matchesSearch = toolName.includes(searchTerm) || ")
        html.append("                                    toolDescription.includes(searchTerm) || ")
        html.append("                                    toolPath.includes(searchTerm) || ")
        html.append("                                    toolTags.some(tag => tag.includes(searchTerm));")
        html.append("                ")
        html.append("                // Check if matches status filter")
        html.append("                const matchesFilter = activeFilter === 'all' || toolStatus === activeFilter;")
        html.append("                ")
        html.append("                // Show if matches both search and filter")
        html.append("                if (matchesSearch && matchesFilter) {")
        html.append("                    card.style.display = '';")
        html.append("                } else {")
        html.append("                    card.style.display = 'none';")
        html.append("                }")
        html.append("            });")
        html.append("            ")
        html.append("            // Hide empty categories")
        html.append("            categoryContainers.forEach(container => {")
        html.append("                const visibleTools = container.querySelectorAll('.tool-card[style=""]').length;")
        html.append("                container.style.display = visibleTools > 0 ? '' : 'none';")
        html.append("            });")
        html.append("        }")
        html.append("        ")
        html.append("        // Filter button functionality")
        html.append("        document.addEventListener('DOMContentLoaded', function() {")
        html.append("            const filterButtons = document.querySelectorAll('.filter-button');")
        html.append("            filterButtons.forEach(button => {")
        html.append("                button.addEventListener('click', function() {")
        html.append("                    // Remove active class from all buttons")
        html.append("                    filterButtons.forEach(btn => btn.classList.remove('active'));")
        html.append("                    // Add active class to clicked button")
        html.append("                    this.classList.add('active');")
        html.append("                    // Apply filter")
        html.append("                    searchTools();")
        html.append("                });")
        html.append("            });")
        html.append("        });")
        html.append("    </script>")
        html.append("</head>")
        html.append("<body>")
        html.append("    <div class='header'>")
        html.append(f"        <h1>EGOS Tools Report</h1>")
        html.append(f"        <p>Generated on {self.stats['last_run']}</p>")
        html.append("    </div>")
        
        # Search box
        html.append("    <div class='search-container'>")
        html.append("        <input type='text' id='toolSearch' placeholder='Search tools...' oninput='searchTools()'>")
        html.append("    </div>")
        
        # Filter buttons
        html.append("    <div class='filter-buttons'>")
        html.append("        <button class='filter-button active' data-status='all'>All</button>")
        html.append("        <button class='filter-button' data-status='active'>Active</button>")
        html.append("        <button class='filter-button' data-status='inactive'>Inactive</button>")
        html.append("        <button class='filter-button' data-status='experimental'>Experimental</button>")
        html.append("        <button class='filter-button' data-status='deprecated'>Deprecated</button>")
        html.append("    </div>")
        
        # Stats section
        html.append("    <div class='stats-container'>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{self.stats['total_tools']}</div>")
        html.append("            <div class='stat-label'>Total Tools</div>")
        html.append("        </div>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{self.stats['active_tools']}</div>")
        html.append("            <div class='stat-label'>Active Tools</div>")
        html.append("        </div>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{self.stats['inactive_tools']}</div>")
        html.append("            <div class='stat-label'>Inactive Tools</div>")
        html.append("        </div>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{self.stats['deprecated_tools']}</div>")
        html.append("            <div class='stat-label'>Deprecated Tools</div>")
        html.append("        </div>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{self.stats['experimental_tools']}</div>")
        html.append("            <div class='stat-label'>Experimental Tools</div>")
        html.append("        </div>")
        html.append("        <div class='stat-box'>")
        html.append(f"            <div class='stat-value'>{len(self.stats['categories'])}</div>")
        html.append("            <div class='stat-label'>Categories</div>")
        html.append("        </div>")
        html.append("    </div>")
        
        # Tools by category
        for category, cat_tools in sorted(category_map.items()):
            # Sort tools by status (active first), then by name
            cat_tools = sorted(
                cat_tools, 
                key=lambda x: (0 if x.get('status', '').lower() == 'active' else 
                              1 if x.get('status', '').lower() == 'experimental' else 
                              2 if x.get('status', '').lower() == 'inactive' else 3, 
                              x.get('name', '').lower())
            )
            html.append(f"    <div class='category-section'>")
            html.append(f"        <h2 class='category-header'>{category} <span class='category-count'>({len(cat_tools)} tools)</span></h2>")
            html.append("        <div class='tool-grid'>")
            
            for tool in sorted(cat_tools, key=lambda x: x.get('name', '').lower()):
                name = tool.get('name', 'Unnamed Tool')
                tool_id = tool.get('id', '')
                status = tool.get('status', 'unknown').lower()
                path = tool.get('path', '')
                description = tool.get('description', 'No description available')
                created = tool.get('created', 'Unknown')
                updated = tool.get('last_updated', 'Unknown')
                maintainer = tool.get('maintainer', 'EGOS Development Team')
                tags = tool.get('tags', [])
                
                # Status class
                status_class = "status-inactive"
                if status == 'active':
                    status_class = "status-active"
                elif status == 'deprecated':
                    status_class = "status-deprecated"
                elif status == 'experimental':
                    status_class = "status-experimental"
                
                # Determine utility and context tags
                utility_tags = []
                context_tags = []
                policy_tags = []
                
                # Extract tags by type
                for tag in tags:
                    if tag.lower() in ['utility', 'tool', 'script', 'automation', 'helper']:
                        utility_tags.append(tag)
                    elif tag.lower() in ['documentation', 'standard', 'policy', 'guideline', 'rule']:
                        policy_tags.append(tag)
                    else:
                        context_tags.append(tag)
                
                # Tool card with data-status attribute for filtering and special class for active tools
                active_class = " active-tool" if status.lower() == "active" else ""
                html.append(f"            <div class='tool-card{active_class}' data-status='{status}'>")
                html.append("                <div class='tool-header'>")
                html.append(f"                    <h3 class='tool-title'>{name}</h3>")
                html.append(f"                    <span class='tool-status {status_class}'>{status.upper()}</span>")
                html.append("                </div>")
                html.append(f"                <div class='tool-description'>{description}</div>")
                html.append("                <div class='tool-meta'>")
                html.append(f"                    <div>Created: {created}</div>")
                html.append(f"                    <div>Last Updated: {updated}</div>")
                html.append(f"                    <div>Maintainer: {maintainer}</div>")
                html.append("                </div>")
                html.append(f"                <div class='tool-path'>{path}</div>")
                
                if tags:
                    html.append("                <div class='tool-tags'>")
                    
                    # Utility tags
                    for tag in utility_tags:
                        html.append(f"                    <span class='tool-tag utility-tag'>#{tag}</span>")
                    
                    # Context tags
                    for tag in context_tags:
                        html.append(f"                    <span class='tool-tag context-tag'>#{tag}</span>")
                    
                    # Policy tags
                    for tag in policy_tags:
                        html.append(f"                    <span class='tool-tag policy-tag'>#{tag}</span>")
                        
                    html.append("                </div>")
                
                # Add contribute button for inactive and experimental tools
                if status.lower() in ['inactive', 'experimental']:
                    roadmap_link = "../../docs/roadmap/ROADMAP.md#" + name.lower().replace(' ', '-')
                    html.append(f"                <a href='{roadmap_link}' class='contribute-button'><i class='fas fa-code-branch'></i> Contribute to this tool</a>")
                
                html.append("            </div>")
            
            html.append("        </div>")
            html.append("    </div>")
        
        # Roadmap section
        html.append("    <div class='roadmap-section'>")
        html.append("        <h2>Contribute to EGOS</h2>")
        html.append("        <p>EGOS follows the <strong>Script Management Best Practices</strong> to maintain a clean, well-documented codebase with a single source of truth for each functionality.</p>")
        html.append("        <p>EGOS is an open ecosystem that welcomes contributions. Here are some ways you can help:</p>")
        
        # Roadmap items
        html.append("        <div class='roadmap-item'>")
        html.append("            <h3>Help with Inactive Scripts</h3>")
        html.append(f"            <p>There are currently {self.stats['inactive_tools']} inactive scripts that need attention.</p>")
        html.append("            <a href='../../docs/roadmap/ROADMAP.md' class='contribute-button'><i class='fas fa-code-branch'></i> View Development Roadmap</a>")
        html.append("        </div>")
        
        html.append("        <div class='roadmap-item'>")
        html.append("            <h3>Improve Documentation</h3>")
        html.append("            <p>Help improve the documentation for existing tools and scripts.</p>")
        html.append("            <a href='../../docs/standards/documentation_standards.md' class='contribute-button'><i class='fas fa-book'></i> Documentation Guidelines</a>")
        html.append("        </div>")
        
        html.append("        <div class='roadmap-item'>")
        html.append("            <h3>Test Experimental Features</h3>")
        html.append(f"            <p>There are {self.stats['experimental_tools']} experimental scripts that need testing and feedback.</p>")
        html.append("            <a href='../../docs/process/testing_guidelines.md' class='contribute-button'><i class='fas fa-vial'></i> Testing Guidelines</a>")
        html.append("        </div>")
        html.append("    </div>")
        
        # Policy section
        html.append("    <div class='policy-section'>")
        html.append("        <h2>EGOS Policies and Guidelines</h2>")
        html.append("        <div>")
        html.append("            <a href='../../docs/process/CONTRIBUTING.md' class='policy-link'><i class='fas fa-hands-helping'></i> Contribution Guidelines</a>")
        html.append("            <a href='../../docs/standards/code_standards.md' class='policy-link'><i class='fas fa-code'></i> Code Standards</a>")
        html.append("            <a href='../../docs/standards/cross_references.md' class='policy-link'><i class='fas fa-project-diagram'></i> Cross-Reference Standards</a>")
        html.append("            <a href='../../docs/process/script_management_guidelines.md' class='policy-link'><i class='fas fa-file-code'></i> Script Management</a>")
        html.append("            <a href='../../docs/MQP.md' class='policy-link'><i class='fas fa-brain'></i> Master Quantum Prompt</a>")
        html.append("        </div>")
        html.append("    </div>")
        
        # Footer
        html.append("    <div class='egos-signature'>✧༺❀༻∞ EGOS ∞༺❀༻✧</div>")
        html.append("    <div class='footer'>")
        html.append(f"        <p>EGOS Tools Manager v{VERSION}</p>")
        html.append(f"        <p>Generated on {self.stats['last_run']}</p>")
        html.append("    </div>")
        html.append("</body>")
        html.append("</html>")
        
        # Write the report to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
        
        # Update website integration if enabled
        if CONFIG["website_integration"]:
            self._update_website_tools()
        
        # Store report path for reference
        self.report_path = report_path
        return str(report_path)
    
    def _update_website_tools(self) -> None:
        """
        Update the website tools section with the latest tool information.
        
        Creates or updates markdown files for each tool in the website content directory.
        """
        website_dir = self.base_path / CONFIG["website_tools_dir"]
        os.makedirs(website_dir, exist_ok=True)
        
        # Load tools
        tools = self.list_tools()
        
        # Create index file
        index_path = website_dir / "_index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write("title: EGOS Tools\n")
            f.write("description: Comprehensive listing of tools in the EGOS ecosystem\n")
            f.write("date: " + datetime.now().strftime("%Y-%m-%d") + "\n")
            f.write("lastmod: " + datetime.now().strftime("%Y-%m-%d") + "\n")
            f.write("draft: false\n")
            f.write("images: []\n")
            f.write("weight: 40\n")
            f.write("toc: true\n")
            f.write("---\n\n")
            f.write("# EGOS Tools\n\n")
            f.write("This section provides a comprehensive listing of tools available in the EGOS ecosystem. ")
            f.write("Tools are organized by category and include detailed information about their purpose, usage, and status.\n\n")
            
            # Add statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Total Tools**: {self.stats['total_tools']}\n")
            f.write(f"- **Active Tools**: {self.stats['active_tools']}\n")
            f.write(f"- **Categories**: {len(self.stats['categories'])}\n")
            f.write(f"- **Last Updated**: {self.stats['last_run']}\n\n")
            
            # Add category links
            f.write("## Categories\n\n")
            for category in sorted(self.stats['categories'].keys()):
                category_slug = category.lower().replace(' ', '-')
                f.write(f"- [{category}](#{category_slug}) ({self.stats['categories'][category]} tools)\n")
            
            f.write("\n")
        
        # Create tool files
        for tool in tools:
            tool_id = tool.get('id', '').lower()
            if not tool_id:
                continue
                
            tool_path = website_dir / f"{tool_id}.md"
            with open(tool_path, 'w', encoding='utf-8') as f:
                name = tool.get('name', 'Unnamed Tool')
                status = tool.get('status', 'unknown').lower()
                path = tool.get('path', '')
                description = tool.get('description', 'No description available')
                created = tool.get('created', 'Unknown')
                updated = tool.get('last_updated', 'Unknown')
                maintainer = tool.get('maintainer', 'EGOS Development Team')
                category = tool.get('category', 'Uncategorized')
                tags = tool.get('tags', [])
                examples = tool.get('examples', [])
                documentation = tool.get('documentation', {})
                
                # Front matter
                f.write("---\n")
                f.write(f"title: {name}\n")
                f.write(f"description: {description[:100]}...\n")
                f.write(f"date: {created}\n")
                f.write(f"lastmod: {updated}\n")
                f.write("draft: false\n")
                f.write("images: []\n")
                f.write(f"categories: [{category}]\n")
                if tags:
                    f.write(f"tags: [{', '.join(tags)}]\n")
                f.write("toc: true\n")
                f.write("---\n\n")
                
                # Content
                f.write(f"# {name}\n\n")
                f.write(f"**Status**: {status.upper()}\n\n")
                f.write(f"**Path**: `{path}`\n\n")
                f.write(f"**Category**: {category}\n\n")
                f.write(f"**Maintainer**: {maintainer}\n\n")
                
                # Description
                f.write("## Description\n\n")
                f.write(f"{description}\n\n")
                
                # Examples
                if examples:
                    f.write("## Examples\n\n")
                    for i, example in enumerate(examples, 1):
                        f.write(f"### Example {i}: {example.get('description', '')}\n\n")
                        f.write(f"```bash\n{example.get('command', '')}\n```\n\n")
                        
                        if 'output' in example:
                            f.write("**Output**:\n\n")
                            f.write(f"```\n{example.get('output', '')}\n```\n\n")
                
                # Documentation
                if documentation:
                    f.write("## Documentation\n\n")
                    for doc_type, doc_path in documentation.items():
                        f.write(f"- **{doc_type}**: [{doc_path}]({doc_path})\n")
                    f.write("\n")
                
                # Tags
                if tags:
                    f.write("## Tags\n\n")
                    for tag in tags:
                        f.write(f"- #{tag}\n")
                    f.write("\n")
    
    def display_tools(self, category: Optional[str] = None, show_all: bool = False, concise: bool = True) -> None:
        """Display available tools with rich formatting and detailed information.
        
        This function presents tools in a well-structured format with visual separation
        between categories and tools. By default, it uses a concise format for terminal output.
        
        By default, only active tools are displayed. Use show_all=True to display all tools
        including inactive, deprecated, and experimental ones.
        
        Args:
            category: Optional category to filter by
            show_all: Whether to show all tools or only active ones (default: False)
            concise: Whether to use concise output format (default: True)
        """
        # Get tools to display
        tools = self.list_tools(category)
        
        # Filter to only show active tools unless show_all is True
        if not show_all:
            tools = [t for t in tools if t.get('status', '').lower() == 'active']
        
        # Check if we have any tools
        if not tools:
            if CONFIG["use_color"]:
                print(f"{Fore.YELLOW}No tools found.{Style.RESET_ALL}")
            else:
                print("No tools found.")
            return
        
        # Print banner
        print_banner(
            f"EGOS TOOLS MANAGER v{VERSION}",
            f"Total: {len(tools)} tools ({self.stats['active_tools']} active, {self.stats['inactive_tools']} inactive)"
        )
        
        # Group tools by category
        category_map = defaultdict(list)
        for tool in tools:
            cat = tool.get('category', 'Uncategorized')
            category_map[cat].append(tool)
        
        # Color helpers
        def colored(text, color, bold=False):
            if not CONFIG["use_color"]:
                return text
            result = f"{color}{text}{Style.RESET_ALL}"
            if bold:
                result = f"{Style.BRIGHT}{result}"
            return result
        
        # Display tools by category
        for cat_idx, (cat_name, cat_tools) in enumerate(sorted(category_map.items())):
            # Category header
            cat_header = f"[{cat_name.upper()}]"
            if CONFIG["use_color"]:
                print(f"{Fore.BLUE}{Style.BRIGHT}{cat_header}{Style.RESET_ALL}")
            else:
                print(cat_header)
            print()
            
            # Sort tools by status (active first), then by name
            sorted_tools = sorted(
                cat_tools, 
                key=lambda x: (0 if x.get('status', '').lower() == 'active' else 1, x.get('name', '').lower())
            )
            
            # Display each tool
            for tool in sorted_tools:
                name = tool.get('name', 'Unnamed Tool')
                status = tool.get('status', 'unknown').lower()
                path = tool.get('path', '')
                description = tool.get('description', 'No description available')
                
                # Status color
                if status == 'active':
                    status_color = Fore.GREEN
                    status_text = "ACTIVE"
                elif status == 'deprecated':
                    status_color = Fore.RED
                    status_text = "DEPRECATED"
                elif status == 'experimental':
                    status_color = Fore.MAGENTA
                    status_text = "EXPERIMENTAL"
                else:
                    status_color = Fore.YELLOW
                    status_text = "INACTIVE"
                
                if concise:
                    # Concise format - just name, status, and brief description
                    if CONFIG["use_color"]:
                        print(f"  {Fore.CYAN}{name}{Style.RESET_ALL} [{status_color}{status_text}{Style.RESET_ALL}]")
                        
                        # Truncate description if too long
                        if len(description) > 80:
                            description = description[:77] + "..."
                        print(f"    {description}")
                    else:
                        print(f"  {name} [{status_text}]")
                        if len(description) > 80:
                            description = description[:77] + "..."
                        print(f"    {description}")
                else:
                    # Detailed format
                    if CONFIG["use_color"]:
                        print(f"  {Fore.CYAN}{name}{Style.RESET_ALL} | Status: {status_color}{status_text}{Style.RESET_ALL}")
                    else:
                        print(f"  {name} | Status: {status_text}")
                    
                    # Print path
                    if path:
                        if CONFIG["use_color"]:
                            print(f"  Path: {Fore.CYAN}{path}{Style.RESET_ALL}")
                        else:
                            print(f"  Path: {path}")
                    
                    # Print description
                    if description:
                        # Wrap description text
                        wrapper = textwrap.TextWrapper(
                            width=CONFIG["terminal_width"] - 4,
                            initial_indent="  ",
                            subsequent_indent="  "
                        )
                        wrapped_description = wrapper.fill(description)
                        print(wrapped_description)
                    
                    # Print tags
                    if 'tags' in tool and tool['tags']:
                        tags = [f"#{tag}" for tag in tool['tags']]
                        tags_str = ', '.join(tags)
                        if CONFIG["use_color"]:
                            print(f"  Tags: {Fore.CYAN}{tags_str}{Style.RESET_ALL}")
                        else:
                            print(f"  Tags: {tags_str}")
                
                    else:
                        print(f"  {auto_msg}")
                
                # Add spacing between tools
                print()
            
            # Add separator between categories unless it's the last one
            if cat_idx < len(category_map) - 1:
                separator = "=" * CONFIG["terminal_width"]
                if CONFIG["use_color"]:
                    print(f"{Fore.BLUE}{separator}{Style.RESET_ALL}\n")
                else:
                    print(f"{separator}\n")
        
        # Print help information
        if CONFIG["use_color"]:
            print(f"{Fore.YELLOW}{Style.BRIGHT}HOW TO USE EGOS TOOLS:{Style.RESET_ALL}")
            print(f"  • Run a tool: {Fore.CYAN}python run_tools.py --run TOOL_ID{Style.RESET_ALL}")
            print(f"  • View active tools: {Fore.CYAN}python run_tools.py --list{Style.RESET_ALL}")
            print(f"  • View all tools: {Fore.CYAN}python run_tools.py --list --all{Style.RESET_ALL}")
            print(f"  • Filter by category: {Fore.CYAN}python run_tools.py --category CATEGORY{Style.RESET_ALL}")
            print(f"  • Get tool info: {Fore.CYAN}python run_tools.py --info TOOL_ID{Style.RESET_ALL}")
        else:
            print("HOW TO USE EGOS TOOLS:")
            print("  * Run a tool: python run_tools.py --run TOOL_ID")
            print("  * View active tools: python run_tools.py --list")
            print("  * View all tools: python run_tools.py --list --all")
            print("  * Filter by category: python run_tools.py --category CATEGORY")
            print("  * Get tool info: python run_tools.py --info TOOL_ID")
        print()
        
        # Display statistics summary
        if CONFIG["use_color"]:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}SCRIPT STATISTICS:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}Active:{Style.RESET_ALL} {self.stats['active_tools']} | "
                  f"{Fore.YELLOW}Inactive:{Style.RESET_ALL} {self.stats['inactive_tools']} | "
                  f"{Fore.RED}Deprecated:{Style.RESET_ALL} {self.stats['deprecated_tools']} | "
                  f"{Fore.MAGENTA}Experimental:{Style.RESET_ALL} {self.stats['experimental_tools']}")
            print(f"  {Fore.CYAN}Total Scripts:{Style.RESET_ALL} {self.stats['total_tools']} in {len(self.stats['categories'])} categories")
        else:
            print("\nSCRIPT STATISTICS:")
            print(f"  Active: {self.stats['active_tools']} | "
                  f"Inactive: {self.stats['inactive_tools']} | "
                  f"Deprecated: {self.stats['deprecated_tools']} | "
                  f"Experimental: {self.stats['experimental_tools']}")
            print(f"  Total Scripts: {self.stats['total_tools']} in {len(self.stats['categories'])} categories")
            
        # Print EGOS signature
        if CONFIG["use_color"]:
            try:
                print(f"\n{Style.BRIGHT}{Fore.MAGENTA}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")
            except UnicodeEncodeError:
                print(f"\n{Style.BRIGHT}{Fore.MAGENTA}EGOS{Style.RESET_ALL}")
                
    def show_tool_info(self, tool_id: str) -> bool:
        """Display detailed information about a specific tool.
        
        Args:
            tool_id: ID of the tool to show info for
            
        Returns:
            True if the tool was found, False otherwise
        """
        # Find the tool
        tools = self.list_tools()
        tool = next((t for t in tools if t.get('id', '').lower() == tool_id.lower()), None)
        
        if not tool:
            if CONFIG["use_color"]:
                print(f"{Fore.RED}Tool '{tool_id}' not found.{Style.RESET_ALL}")
            else:
                print(f"Tool '{tool_id}' not found.")
            return False
        
        # Print detailed info
        name = tool.get('name', 'Unnamed Tool')
        status = tool.get('status', 'unknown').lower()
        path = tool.get('path', '')
        description = tool.get('description', 'No description available')
        created = tool.get('created', 'Unknown')
        updated = tool.get('last_updated', 'Unknown')
        maintainer = tool.get('maintainer', 'EGOS Development Team')
        examples = tool.get('examples', [])
        documentation = tool.get('documentation', {})
        dependencies = tool.get('dependencies', [])
        
        # Tool header
        print_banner(name, f"Tool ID: {tool_id}")
        
        # Status with color
        if status == 'active':
            status_color = Fore.GREEN
            status_text = "ACTIVE"
        elif status == 'deprecated':
            status_color = Fore.RED
            status_text = "DEPRECATED"
        elif status == 'experimental':
            status_color = Fore.MAGENTA
            status_text = "EXPERIMENTAL"
        else:
            status_color = Fore.YELLOW
            status_text = "INACTIVE"
            
        if CONFIG["use_color"]:
            print(f"Status: {status_color}{status_text}{Style.RESET_ALL}")
        else:
            print(f"Status: {status_text}")
        
        # Path
        if path:
            if CONFIG["use_color"]:
                print(f"Path: {Fore.CYAN}{path}{Style.RESET_ALL}")
            else:
                print(f"Path: {path}")
        
        # Basic info
        print(f"Created: {created}")
        print(f"Last Updated: {updated}")
        print(f"Maintainer: {maintainer}")
        
        if dependencies:
            if CONFIG["use_color"]:
                print(f"\n{Fore.BLUE}Dependencies:{Style.RESET_ALL}")
            else:
                print("\nDependencies:")
            for dep in dependencies:
                print(f"  - {dep}")
        
        # Description
        if CONFIG["use_color"]:
            print(f"\n{Fore.BLUE}Description:{Style.RESET_ALL}")
        else:
            print("\nDescription:")
            
        # Format and print description with wrapping
        term_width = CONFIG["terminal_width"]
        wrapper = textwrap.TextWrapper(
            width=term_width - 2,
            initial_indent="  ",
            subsequent_indent="  "
        )
        for line in description.split('\n'):
            if line.strip():
                print(wrapper.fill(line))
        
        # Usage
        if 'usage' in tool and tool['usage']:
            if CONFIG["use_color"]:
                print(f"\n{Fore.BLUE}Usage:{Style.RESET_ALL}")
            else:
                print("\nUsage:")
            print(f"  {tool['usage']}")
        
        # Examples
        if examples:
            if CONFIG["use_color"]:
                print(f"\n{Fore.BLUE}Examples:{Style.RESET_ALL}")
            else:
                print("\nExamples:")
            
            for i, example in enumerate(examples, 1):
                if CONFIG["use_color"]:
                    print(f"\n  {Fore.YELLOW}Example {i}: {example.get('description', '')}{Style.RESET_ALL}")
                    print(f"  {Fore.CYAN}$ {example.get('command', '')}{Style.RESET_ALL}")
                else:
                    print(f"\n  Example {i}: {example.get('description', '')}")
                    print(f"  $ {example.get('command', '')}")
                
                if 'output' in example:
                    print("  Output:")
                    output_wrapper = textwrap.TextWrapper(
                        width=term_width - 4,
                        initial_indent="    ",
                        subsequent_indent="    "
                    )
                    for line in example['output'].split('\n'):
                        print(output_wrapper.fill(line))
        
        # Documentation
        if documentation:
            if CONFIG["use_color"]:
                print(f"\n{Fore.BLUE}Documentation:{Style.RESET_ALL}")
            else:
                print("\nDocumentation:")
                
            for doc_type, doc_path in documentation.items():
                if CONFIG["use_color"]:
                    print(f"  {Fore.YELLOW}{doc_type}:{Style.RESET_ALL} {doc_path}")
                else:
                    print(f"  {doc_type}: {doc_path}")
        
        # Tags
        if 'tags' in tool and tool['tags']:
            if CONFIG["use_color"]:
                print(f"\n{Fore.BLUE}Tags:{Style.RESET_ALL}")
            else:
                print("\nTags:")
                
            tags = [f"#{tag}" for tag in tool['tags']]
            tags_str = ', '.join(tags)
            if CONFIG["use_color"]:
                print(f"  {Fore.CYAN}{tags_str}{Style.RESET_ALL}")
            else:
                print(f"  {tags_str}")
        
        print()
        return True
    
    def get_categories(self) -> List[str]:
        """Get all available categories.
        
        Returns:
            List of category names
        """
        tools = self.list_tools()
        categories = set()
        
        for tool in tools:
            cat = tool.get('category', 'Uncategorized')
            categories.add(cat)
            
        return sorted(list(categories))

def main():
    """Main entry point for the script.
    
    Processes command-line arguments and dispatches to the appropriate handler.
    Supports listing tools, running tools, filtering by category, and viewing tool details.
    """
    # Print banner
    print_banner(f"EGOS TOOLS MANAGER v{VERSION}", "Central access point for EGOS tools and scripts")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='EGOS Tool Runner - Central access point for EGOS tools and scripts')
    parser.add_argument('--list', '-l', action='store_true', help='List available tools (active only by default)')
    parser.add_argument('--all', '-a', action='store_true', help='Show all tools including inactive, deprecated, and experimental')
    parser.add_argument('--run', '-r', metavar='TOOL_ID', help='Run a specific tool')
    parser.add_argument('--category', '-c', metavar='CATEGORY', help='Filter tools by category')
    parser.add_argument('--info', '-i', metavar='TOOL_ID', help='Show detailed information about a specific tool')
    parser.add_argument('--discover', '-d', action='store_true', help='Discover scripts and update registry')
    parser.add_argument('--save', '-s', action='store_true', help='Save discovered scripts to registry')
    parser.add_argument('--categories', action='store_true', help='List all available categories')
    parser.add_argument('--version', '-v', action='store_true', help='Show version information')
    parser.add_argument('args', nargs='*', help='Arguments to pass to the tool')
    
    args = parser.parse_args()
    
    # Create tool runner with current directory as base path
    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    runner = ToolRunner(current_path)
    
    # Process arguments
    if args.version:
        print(f"EGOS Tools Manager v{VERSION}")
        print(f"Python: {sys.version}")
        return 0
        
    # Track execution start time
    start_time = datetime.now()
    
    if args.categories:
        categories = runner.get_categories()
        if CONFIG["use_color"]:
            print(f"{Fore.BLUE}Available Categories:{Style.RESET_ALL}")
        else:
            print("Available Categories:")
        for cat in categories:
            if CONFIG["use_color"]:
                print(f"  {Fore.CYAN}{cat}{Style.RESET_ALL}")
            else:
                print(f"  {cat}")
        return 0
    
    if args.discover:
        # Auto-discover scripts
        scripts = runner.discover_scripts()
        print(f"Discovered {len(scripts)} scripts in the EGOS ecosystem.")
        
        if args.save:
            # Get existing tools
            tools = runner.load_registry()
            
            # Add discovered scripts not yet in registry
            registered_paths = {t.get('path', '').lower() for t in tools}
            added_count = 0
            
            for script in scripts:
                rel_path = os.path.relpath(script, os.getcwd())
                rel_path = rel_path.replace('\\', '/')
                
                if rel_path.lower() not in registered_paths:
                    # Extract basic info and add to tools list
                    info = runner.extract_script_info(script)
                    if info:
                        # Create basic tool entry
                        tool_entry = {
                            "id": info.get("id", ""),
                            "name": info.get("name", ""),
                            "path": rel_path,
                            "description": info.get("description", "Auto-discovered script"),
                            "category": info.get("category", runner.guess_category(rel_path)),
                            "status": "inactive",  # Mark as inactive until verified
                            "created": datetime.now().strftime("%Y-%m-%d"),
                            "last_updated": datetime.now().strftime("%Y-%m-%d"),
                            "auto_discovered": True,
                            "tags": info.get("tags", [])
                        }
                        tools.append(tool_entry)
                        registered_paths.add(rel_path.lower())
                        added_count += 1
            
            # Save registry
            if runner.save_registry(tools):
                print(f"Added {added_count} new scripts to the registry.")
            else:
                print(f"Error saving registry.")
                return 1
        
        return 0
    
    if args.info:
        # Show detailed tool info
        if not runner.show_tool_info(args.info):
            return 1
        return 0
    
    if args.list:
        # Track execution start time if not already tracking
        if 'start_time' not in locals():
            start_time = datetime.now()
            
        # List tools, optionally filtered by category
        runner.display_tools(args.category, show_all=args.all)
        
        # Generate report if enabled
        if CONFIG["generate_report"]:
            try:
                # Update execution time
                runner.stats["execution_time"] = (datetime.now() - start_time).total_seconds()
                
                # Generate report
                report_path = runner.generate_report()
                
                # Display report path with more visibility and proper formatting
                separator = '=' * min(80, CONFIG["terminal_width"])
                if CONFIG["use_color"]:
                    print("\n")
                    print(f"{Fore.GREEN}{separator}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}REPORT GENERATED:{Style.RESET_ALL}")
                    print("")
                    print(f"{Fore.CYAN}{report_path}{Style.RESET_ALL}")
                    print("")
                    print(f"{Fore.YELLOW}You can open this HTML file in your browser to view the complete tools report.{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{separator}{Style.RESET_ALL}")
                    print(f"{Style.BRIGHT}{Fore.MAGENTA}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")
                else:
                    print("\n")
                    print(f"{separator}")
                    print("REPORT GENERATED:")
                    print("")
                    print(f"{report_path}")
                    print("")
                    print("You can open this HTML file in your browser to view the complete tools report.")
                    print(f"{separator}")
                    print("✧༺❀༻∞ EGOS ∞༺❀༻✧")
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                if CONFIG["use_color"]:
                    print(f"\n{Fore.RED}Error generating report: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"\nError generating report: {str(e)}")
        
        return 0
    
    if args.run:
        # Run a specific tool
        return runner.run_tool(args.run, args.args)
    
    if args.category:
        # Track execution start time if not already tracking
        if 'start_time' not in locals():
            start_time = datetime.now()
            
        # List tools in a specific category
        runner.display_tools(args.category, show_all=args.all)
        
        # Generate report if enabled
        if CONFIG["generate_report"]:
            try:
                # Update execution time
                runner.stats["execution_time"] = (datetime.now() - start_time).total_seconds()
                
                # Generate report
                report_path = runner.generate_report()
                
                # Display report path with more visibility and proper formatting
                separator = '=' * min(80, CONFIG["terminal_width"])
                if CONFIG["use_color"]:
                    print("\n")
                    print(f"{Fore.GREEN}{separator}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}REPORT GENERATED:{Style.RESET_ALL}")
                    print("")
                    print(f"{Fore.CYAN}{report_path}{Style.RESET_ALL}")
                    print("")
                    print(f"{Fore.YELLOW}You can open this HTML file in your browser to view the complete tools report.{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}{separator}{Style.RESET_ALL}")
                    print(f"{Style.BRIGHT}{Fore.MAGENTA}✧༺❀༻∞ EGOS ∞༺❀༻✧{Style.RESET_ALL}")
                else:
                    print("\n")
                    print(f"{separator}")
                    print("REPORT GENERATED:")
                    print("")
                    print(f"{report_path}")
                    print("")
                    print("You can open this HTML file in your browser to view the complete tools report.")
                    print(f"{separator}")
                    print("✧༺❀༻∞ EGOS ∞༺❀༻✧")
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                if CONFIG["use_color"]:
                    print(f"\n{Fore.RED}Error generating report: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"\nError generating report: {str(e)}")
        
        return 0
    
    # No arguments provided, show help
    parser.print_help()
    
    # Generate report if enabled
    if CONFIG["generate_report"]:
        try:
            # Update execution time
            runner.stats["execution_time"] = (datetime.now() - start_time).total_seconds()
            
            # Generate report
            report_path = runner.generate_report()
            
            # Display report path
            if CONFIG["use_color"]:
                print(f"\n{Fore.GREEN}Report generated: {Fore.CYAN}{report_path}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}You can open this HTML file in your browser to view the complete tools report.{Style.RESET_ALL}")
            else:
                print(f"\nReport generated: {report_path}")
                print("You can open this HTML file in your browser to view the complete tools report.")
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            if CONFIG["use_color"]:
                print(f"\n{Fore.RED}Error generating report: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"\nError generating report: {str(e)}")
    
    return 0
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unhandled exception in run_tools.py")
        print(f"Error: {str(e)}")
        sys.exit(1)
        
# ✧༺❀༻∞ EGOS ∞༺❀༻✧