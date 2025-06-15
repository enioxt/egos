#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Registry Population Tool

This script scans the EGOS codebase for Python scripts that can be registered as tools,
extracts metadata using the Docstring Metadata Extractor, and adds them to the 
tool registry. It supports scanning specific directories, updating existing entries,
and validating the registry after population.

Part of the EGOS Tool Registry and Integration System - Phase 2.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

Usage:
    python scripts/registry/registry_populator.py --scan-dir scripts/
    python scripts/registry/registry_populator.py --scan-all
    python scripts/registry/registry_populator.py --update-existing

@references:
- C:\EGOS\WORK_2025_05_22_tool_registry_phase2.md (Tool Registry Phase 2 Plan)
- C:\EGOS\config\tool_registry_schema.json (Tool Registry Schema)
- C:\EGOS\scripts\registry\docstring_extractor.py (Docstring Metadata Extractor)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import subprocess

# Import the docstring extractor
try:
    from docstring_extractor import DocstringParser, RegistryEntryGenerator, scan_file
except ImportError:
    # Add the current directory to the path if running from another location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from docstring_extractor import DocstringParser, RegistryEntryGenerator, scan_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("registry_populator")

class CodebaseScanner:
    """
    Scans the codebase for potential tools to add to the registry.
    
    Recursively traverses directories to find Python scripts that could be
    registered as tools. Uses heuristics to identify scripts that are likely
    to be standalone tools rather than library modules.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the codebase scanner.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = base_path
        
        # Directories to exclude from scanning
        self.excluded_dirs = {
            'venv', '.venv', 'env', '.env', '.git', '__pycache__',
            'tests', 'test', 'node_modules', 'build', 'dist', 
            'site-packages'
        }
        
        # Patterns indicating a file is likely a tool
        self.tool_indicators = [
            'def main', 'if __name__', 'argparse', 'click', 
            'CommandLineInterface', 'CLI', 'parser.add_argument'
        ]
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """
        Recursively scan a directory for Python files that may be tools.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of paths to potential tool files
        """
        potential_tools = []
        
        try:
            for item in directory.iterdir():
                # Skip excluded directories
                if item.is_dir() and item.name in self.excluded_dirs:
                    continue
                
                # Recursively scan subdirectories
                if item.is_dir():
                    potential_tools.extend(self.scan_directory(item))
                
                # Check Python files
                elif item.suffix == '.py':
                    if self.is_potential_tool(item):
                        potential_tools.append(item)
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        return potential_tools
    
    def is_potential_tool(self, file_path: Path) -> bool:
        """
        Determine if a file is likely a tool based on content and structure.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Boolean indicating if the file is likely a tool
        """
        # Skip __init__.py files
        if file_path.name == '__init__.py':
            return False
        
        # Skip test files
        if 'test' in file_path.name.lower():
            return False
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for indicators that this is a tool
            for indicator in self.tool_indicators:
                if indicator in content:
                    return True
            
            # Check if the file has a module docstring
            if content.strip().startswith('"""') or content.strip().startswith("'''"):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get basic information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            rel_path = file_path.relative_to(self.base_path)
            return {
                'path': str(rel_path),
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return {
                'path': str(file_path),
                'name': file_path.name
            }


class RegistryPopulator:
    """
    Populates the tool registry with discovered tools.
    
    Manages the process of scanning the codebase, extracting metadata,
    and updating the registry. Handles merging new entries with existing ones
    and validating the registry after updates.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the registry populator.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = base_path
        self.registry_path = base_path / 'config' / 'tool_registry.json'
        self.schema_path = base_path / 'config' / 'tool_registry_schema.json'
        self.validator_path = base_path / 'scripts' / 'validation' / 'tool_registry_validator.py'
    
    def load_existing_registry(self) -> Dict[str, Any]:
        """
        Load the existing tool registry.
        
        Returns:
            Dictionary containing the registry data
        """
        try:
            if self.registry_path.exists():
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Registry file not found at {self.registry_path}")
                return {"tools": []}
                
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            return {"tools": []}
    
    def populate_registry(self, scan_dirs: List[Path] = None, update_existing: bool = False) -> int:
        """
        Populate the registry with tools from the specified directories.
        
        Args:
            scan_dirs: List of directories to scan for tools
            update_existing: Whether to update existing entries
            
        Returns:
            Number of tools added or updated
        """
        # Load existing registry
        registry = self.load_existing_registry()
        existing_tools = {tool['id']: tool for tool in registry.get('tools', [])}
        existing_paths = {tool['path']: tool['id'] for tool in registry.get('tools', [])}
        
        # Initialize scanner
        scanner = CodebaseScanner(self.base_path)
        
        # If no directories specified, use scripts/ as default
        if not scan_dirs:
            scan_dirs = [self.base_path / 'scripts']
        
        # Collect all potential tools
        potential_tools = []
        for directory in scan_dirs:
            logger.info(f"Scanning directory: {directory}")
            potential_tools.extend(scanner.scan_directory(directory))
        
        logger.info(f"Found {len(potential_tools)} potential tools")
        
        # Process each potential tool
        added_count = 0
        updated_count = 0
        
        for file_path in potential_tools:
            # Get relative path for matching
            rel_path = str(file_path.relative_to(self.base_path)).replace('\\', '/')
            
            # Check if this tool is already in the registry
            if rel_path in existing_paths and not update_existing:
                logger.info(f"Skipping existing tool: {rel_path}")
                continue
            
            # Extract metadata and generate entry
            entry = scan_file(file_path, self.base_path)
            
            if not entry:
                logger.warning(f"Could not generate entry for {file_path}")
                continue
            
            # If this is an update to an existing entry
            if entry['id'] in existing_tools:
                if update_existing:
                    # Merge the entries
                    merged_entry = self.merge_entries(existing_tools[entry['id']], entry)
                    # Replace the existing entry
                    for i, tool in enumerate(registry['tools']):
                        if tool['id'] == entry['id']:
                            registry['tools'][i] = merged_entry
                            updated_count += 1
                            logger.info(f"Updated tool: {entry['id']}")
                            break
            else:
                # Add as a new entry
                registry['tools'].append(entry)
                added_count += 1
                logger.info(f"Added new tool: {entry['id']}")
        
        # Save the updated registry
        if added_count > 0 or updated_count > 0:
            self.save_registry(registry)
            logger.info(f"Registry updated with {added_count} new tools and {updated_count} updated tools")
        else:
            logger.info("No changes made to registry")
        
        # Validate the registry
        self.validate_registry()
        
        return added_count + updated_count
    
    def merge_entries(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge an existing entry with new data.
        
        Args:
            existing: Existing registry entry
            new: New registry entry
            
        Returns:
            Merged registry entry
        """
        # Start with the existing entry
        merged = existing.copy()
        
        # Update fields that should be replaced
        for field in ['description', 'path', 'tags', 'category', 'dependencies']:
            if field in new and new[field]:
                merged[field] = new[field]
        
        # Update last_updated
        merged['last_updated'] = new['last_updated']
        
        # Merge examples
        if 'examples' in new and new['examples']:
            # Keep existing examples, add new ones
            existing_examples = {ex.get('description', ''): ex for ex in merged.get('examples', [])}
            for example in new['examples']:
                if example.get('description', '') not in existing_examples:
                    if 'examples' not in merged:
                        merged['examples'] = []
                    merged['examples'].append(example)
        
        return merged
    
    def save_registry(self, registry: Dict[str, Any]) -> None:
        """
        Save the updated registry.
        
        Args:
            registry: Registry data to save
        """
        try:
            # Create parent directories if they don't exist
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort tools by ID for consistency
            registry['tools'] = sorted(registry['tools'], key=lambda x: x['id'])
            
            # Write the registry
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            
            logger.info(f"Registry saved to {self.registry_path}")
            
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def validate_registry(self) -> bool:
        """
        Validate the registry using the registry validator.
        
        Returns:
            Boolean indicating if validation passed
        """
        if not self.validator_path.exists():
            logger.warning(f"Validator not found at {self.validator_path}")
            return False
        
        try:
            logger.info("Validating registry...")
            result = subprocess.run(
                [sys.executable, str(self.validator_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Registry validation passed")
                return True
            else:
                logger.error(f"Registry validation failed: {result.stderr or result.stdout}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating registry: {e}")
            return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="EGOS Registry Population Tool - Scan codebase for tools and populate registry"
    )
    
    # Scanning options
    scan_group = parser.add_argument_group('Scanning Options')
    scan_group.add_argument("--scan-dir", type=str, action='append',
                          help="Directory to scan for tools (can be specified multiple times)")
    scan_group.add_argument("--scan-all", action='store_true',
                          help="Scan all relevant directories for tools")
    
    # Update options
    update_group = parser.add_argument_group('Update Options')
    update_group.add_argument("--update-existing", action='store_true',
                            help="Update existing entries when found")
    
    # Other options
    parser.add_argument("--base-path", type=str, default=os.getcwd(),
                      help="Base path of the EGOS project")
    parser.add_argument("--verbose", action="store_true",
                      help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        base_path = Path(args.base_path)
        populator = RegistryPopulator(base_path)
        
        scan_dirs = []
        
        # Process scanning options
        if args.scan_all:
            # Scan all relevant directories
            scan_dirs = [
                base_path / 'scripts',
                base_path / 'tools',
                base_path / 'src'
            ]
            scan_dirs = [d for d in scan_dirs if d.exists()]
        elif args.scan_dir:
            # Scan specified directories
            scan_dirs = [base_path / dir_path for dir_path in args.scan_dir]
        
        if not scan_dirs:
            # Default to scripts directory
            default_dir = base_path / 'scripts'
            if default_dir.exists():
                scan_dirs = [default_dir]
            else:
                logger.error("No directories to scan. Please specify with --scan-dir or --scan-all")
                return 1
        
        # Populate the registry
        result = populator.populate_registry(
            scan_dirs=scan_dirs,
            update_existing=args.update_existing
        )
        
        return 0 if result >= 0 else 1
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())