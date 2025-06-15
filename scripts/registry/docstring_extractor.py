#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Docstring Metadata Extractor

This script extracts metadata from Python docstrings to automatically generate
tool registry entries. It supports multiple docstring formats including Google,
NumPy, and reStructuredText.

Part of the EGOS Tool Registry and Integration System - Phase 2.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\WORK_2025_05_22_tool_registry_phase2.md (Tool Registry Phase 2 Plan)
- C:\EGOS\config\tool_registry_schema.json (Tool Registry Schema)
- C:\EGOS\docs\guides\tool_registry_guide.md (Tool Registry Guide)
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
import re
import ast
import inspect
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Pattern
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("docstring_extractor")

class DocstringParser:
    """
    Parser for Python docstrings in various formats to extract metadata.
    
    Supports Google, NumPy, and reStructuredText docstring formats.
    Extracts metadata including description, parameters, returns,
    examples, and references.
    """
    
    # Regular expressions for parsing different docstring sections
    SECTION_REGEX = {
        'google': {
            'args': re.compile(r'(?:Args|Arguments|Parameters):(.*?)(?:$|(?:Returns|Yields|Raises|Examples|Notes|References):\s*\n)', re.DOTALL),
            'returns': re.compile(r'Returns:(.*?)(?:$|(?:Yields|Raises|Examples|Notes|References):\s*\n)', re.DOTALL),
            'examples': re.compile(r'Examples:(.*?)(?:$|(?:Notes|References):\s*\n)', re.DOTALL),
            'references': re.compile(r'References:(.*?)(?:$|\Z)', re.DOTALL),
        },
        'numpy': {
            'parameters': re.compile(r'Parameters\s*\n\s*-+\s*\n(.*?)(?:\n\s*(?:Returns|Yields|Raises|Examples|Notes|References)\s*\n\s*-+\s*\n|\Z)', re.DOTALL),
            'returns': re.compile(r'Returns\s*\n\s*-+\s*\n(.*?)(?:\n\s*(?:Yields|Raises|Examples|Notes|References)\s*\n\s*-+\s*\n|\Z)', re.DOTALL),
            'examples': re.compile(r'Examples\s*\n\s*-+\s*\n(.*?)(?:\n\s*(?:Notes|References)\s*\n\s*-+\s*\n|\Z)', re.DOTALL),
            'references': re.compile(r'References\s*\n\s*-+\s*\n(.*?)(?:\Z)', re.DOTALL),
        },
        'rest': {
            'parameters': re.compile(r':param (.*?):(.*?)(?=$|:param|:type|:return|:rtype|:raises|:example)', re.DOTALL),
            'returns': re.compile(r':return:(.*?)(?=$|:param|:type|:raises|:example)', re.DOTALL),
            'examples': re.compile(r':example:(.*?)(?=$|\Z)', re.DOTALL),
            'references': re.compile(r':see:|:references:(.*?)(?=$|\Z)', re.DOTALL),
        }
    }
    
    # Regular expressions for extracting usage examples
    USAGE_REGEX = re.compile(r'```(?:python)?\s*(.*?)\s*```', re.DOTALL)
    COMMAND_REGEX = re.compile(r'(?:python|py)\s+([^\n]+)')
    
    def __init__(self):
        """Initialize the docstring parser."""
        pass
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract docstring and metadata from a Python file.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            tree = ast.parse(file_content)
            module_docstring = ast.get_docstring(tree)
            
            if not module_docstring:
                logger.warning(f"No module docstring found in {file_path}")
                return {}
            
            # Extract basic metadata from docstring
            docstring_format = self.detect_format(module_docstring)
            metadata = self.extract_metadata(module_docstring, docstring_format)
            
            # Add file path and other basic info
            metadata['file_path'] = str(file_path)
            metadata['file_name'] = file_path.name
            
            # Extract references to other files
            metadata['references'] = self.extract_references(module_docstring)
            
            # Extract dependencies from imports
            metadata['dependencies'] = self.extract_dependencies(file_content)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return {}
    
    def detect_format(self, docstring: str) -> str:
        """
        Detect the format of a docstring (Google, NumPy, reST).
        
        Args:
            docstring: The docstring to analyze
            
        Returns:
            String indicating the detected format ('google', 'numpy', or 'rest')
        """
        # Check for NumPy-style section headers (with underlines)
        if re.search(r'Parameters\s*\n\s*-+\s*\n', docstring):
            return 'numpy'
        
        # Check for reStructuredText directives
        if re.search(r':(param|return|raises|example):', docstring):
            return 'rest'
        
        # Default to Google style
        return 'google'
    
    def extract_metadata(self, docstring: str, format_type: str) -> Dict[str, Any]:
        """
        Extract metadata from docstring based on its format.
        
        Args:
            docstring: The docstring to parse
            format_type: The format of the docstring ('google', 'numpy', or 'rest')
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}
        
        # Extract description (first paragraph of docstring)
        description_match = re.match(r'^(.*?)(?:\n\s*\n|\n\s*(?:Args|Arguments|Parameters|Returns|Yields|Raises|Examples|Notes|References):)', docstring, re.DOTALL)
        if description_match:
            metadata['description'] = self._clean_text(description_match.group(1))
        else:
            metadata['description'] = self._clean_text(docstring.split('\n\n')[0])
        
        # Extract usage examples
        metadata['usage_examples'] = self.extract_usage_examples(docstring)
        
        # Extract command-line usage if present
        metadata['command_usage'] = self.extract_command_usage(docstring)
        
        return metadata
    
    def extract_usage_examples(self, docstring: str) -> List[Dict[str, str]]:
        """
        Extract usage examples from docstring.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            List of dictionaries with example descriptions and code
        """
        examples = []
        
        # Look for code blocks
        code_blocks = self.USAGE_REGEX.findall(docstring)
        for i, code in enumerate(code_blocks, 1):
            examples.append({
                'description': f'Example {i}',
                'code': code.strip()
            })
        
        # Look for Examples section
        examples_section = None
        for format_type in self.SECTION_REGEX:
            if 'examples' in self.SECTION_REGEX[format_type]:
                match = self.SECTION_REGEX[format_type]['examples'].search(docstring)
                if match:
                    examples_section = match.group(1).strip()
                    break
        
        if examples_section and not examples:
            # If we found an Examples section but no code blocks, use the text
            examples.append({
                'description': 'Example',
                'code': examples_section
            })
        
        return examples
    
    def extract_command_usage(self, docstring: str) -> Optional[str]:
        """
        Extract command-line usage pattern from docstring.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            Command usage string if found, None otherwise
        """
        # Look for patterns like "python script.py arg1 arg2"
        command_matches = self.COMMAND_REGEX.findall(docstring)
        if command_matches:
            return command_matches[0].strip()
        return None
    
    def extract_references(self, docstring: str) -> List[str]:
        """
        Extract file references from docstring.
        
        Args:
            docstring: The docstring to parse
            
        Returns:
            List of referenced file paths
        """
        references = []
        
        # Look for paths in the format C:\path\to\file.ext or /path/to/file.ext
        win_paths = re.findall(r'(?:C:\\[^\s,]+\.[a-zA-Z0-9]+)', docstring)
        unix_paths = re.findall(r'(?:/[^\s,]+\.[a-zA-Z0-9]+)', docstring)
        
        references.extend(win_paths)
        references.extend(unix_paths)
        
        # Look for relative paths like module/file.py
        rel_paths = re.findall(r'(?:[\w/\\-]+\.(?:py|md|json|yaml|txt))', docstring)
        references.extend([p for p in rel_paths if '/' in p or '\\' in p])
        
        return list(set(references))
    
    def extract_dependencies(self, file_content: str) -> List[str]:
        """
        Extract dependencies from import statements.
        
        Args:
            file_content: Content of the Python file
            
        Returns:
            List of imported module names
        """
        try:
            tree = ast.parse(file_content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Filter out standard library imports
            std_libs = set([
                'os', 're', 'sys', 'json', 'time', 'datetime', 'logging',
                'argparse', 'pathlib', 'typing', 'collections', 'math',
                'random', 'shutil', 'subprocess', 'tempfile', 'unittest',
                'urllib', 'xml', 'csv', 'io', 'glob', 'itertools'
            ])
            
            return [imp for imp in imports if imp.split('.')[0] not in std_libs]
            
        except Exception as e:
            logger.error(f"Error extracting dependencies: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and indentation.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines]
        return ' '.join(cleaned_lines).strip()


class RegistryEntryGenerator:
    """
    Generates tool registry entries from parsed docstrings.
    
    Converts extracted metadata into the format required by the tool registry,
    including generating IDs, detecting categories, and formatting examples.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the registry entry generator.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = base_path
        self.categories = {
            'validation': ['valid', 'check', 'lint', 'verify'],
            'analysis': ['analy', 'report', 'metric', 'stat'],
            'maintenance': ['maintain', 'update', 'clean', 'fix'],
            'documentation': ['doc', 'readme', 'guide'],
            'development': ['dev', 'build', 'compile'],
            'testing': ['test', 'assert', 'mock'],
            'deployment': ['deploy', 'release', 'publish'],
            'visualization': ['visual', 'chart', 'graph', 'plot'],
            'integration': ['integrat', 'connect', 'bridge'],
            'security': ['secur', 'auth', 'encrypt'],
            'utility': ['util', 'helper', 'common']
        }
    
    def generate_entry(self, metadata: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        Generate a registry entry from extracted metadata.
        
        Args:
            metadata: Extracted metadata from docstring
            file_path: Path to the Python file
            
        Returns:
            Dictionary containing the registry entry
        """
        rel_path = str(file_path.relative_to(self.base_path)).replace('\\', '/')
        
        # Generate tool name from filename
        name_parts = file_path.stem.split('_')
        name = ' '.join(part.capitalize() for part in name_parts)
        
        # Generate tool ID from path
        tool_id = self.generate_id(file_path, name)
        
        # Determine category
        category = self.determine_category(metadata, file_path)
        
        # Extract tags
        tags = self.extract_tags(metadata, file_path)
        
        # Format usage examples
        examples = self.format_examples(metadata.get('usage_examples', []), metadata.get('command_usage'))
        
        # Build the entry
        entry = {
            "id": tool_id,
            "name": name,
            "path": rel_path,
            "description": metadata.get('description', f"Tool located at {rel_path}"),
            "usage": metadata.get('command_usage', f"python {rel_path}"),
            "tags": tags,
            "category": category,
            "status": "active",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "maintainer": "EGOS Development Team",
            "dependencies": metadata.get('dependencies', []),
            "website_integration": {
                "page": f"/tools/{category.lower()}",
                "category": f"{category} Tools",
                "priority": "medium"
            }
        }
        
        # Add examples if available
        if examples:
            entry["examples"] = examples
        
        return entry
    
    def generate_id(self, file_path: Path, name: str) -> str:
        """
        Generate a unique ID for the tool.
        
        Args:
            file_path: Path to the Python file
            name: Name of the tool
            
        Returns:
            String ID in kebab-case
        """
        # Convert to kebab-case
        id_base = file_path.stem.replace('_', '-').lower()
        
        # If it's in a subdirectory, use that as a prefix
        parent = file_path.parent.name
        if parent and parent not in ('scripts', 'tools'):
            return f"{parent}-{id_base}"
        
        return id_base
    
    def determine_category(self, metadata: Dict[str, Any], file_path: Path) -> str:
        """
        Determine the appropriate category for a tool.
        
        Args:
            metadata: Extracted metadata from docstring
            file_path: Path to the Python file
            
        Returns:
            Category string
        """
        # First check the file path
        path_str = str(file_path)
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in path_str.lower():
                    return category.capitalize()
        
        # Then check the description
        description = metadata.get('description', '')
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    return category.capitalize()
        
        # Default to Utility
        return "Utility"
    
    def extract_tags(self, metadata: Dict[str, Any], file_path: Path) -> List[str]:
        """
        Extract tags from metadata and file path.
        
        Args:
            metadata: Extracted metadata from docstring
            file_path: Path to the Python file
            
        Returns:
            List of tag strings
        """
        tags = set()
        
        # Add tags based on file path components
        path_parts = file_path.parts
        for part in path_parts:
            if part not in ('scripts', 'tools', 'src', 'EGOS'):
                tags.add(part.replace('_', '-').lower())
        
        # Add tags based on description keywords
        description = metadata.get('description', '')
        potential_tags = re.findall(r'\b\w+\b', description.lower())
        for tag in potential_tags:
            if len(tag) > 3 and tag not in ('this', 'that', 'with', 'from', 'tool'):
                tags.add(tag)
        
        # Limit to 5 most relevant tags
        return sorted(list(tags))[:5]
    
    def format_examples(self, examples: List[Dict[str, str]], command_usage: Optional[str]) -> List[Dict[str, str]]:
        """
        Format usage examples for the registry.
        
        Args:
            examples: List of example dictionaries
            command_usage: Command-line usage string
            
        Returns:
            List of formatted example dictionaries
        """
        formatted_examples = []
        
        # Add command usage as the first example if available
        if command_usage:
            formatted_examples.append({
                "description": "Basic usage",
                "command": command_usage,
                "output": ""
            })
        
        # Add other examples
        for example in examples:
            formatted_examples.append({
                "description": example.get('description', 'Example'),
                "command": example.get('code', ''),
                "output": ""
            })
        
        return formatted_examples


def scan_file(file_path: Path, base_path: Path) -> Optional[Dict[str, Any]]:
    """
    Scan a single Python file and generate a registry entry if it's a tool.
    
    Args:
        file_path: Path to the Python file
        base_path: Base path of the EGOS project
        
    Returns:
        Registry entry dictionary if successful, None otherwise
    """
    try:
        # Skip test files and __init__.py
        if file_path.name == '__init__.py' or 'test' in file_path.name.lower():
            return None
        
        logger.info(f"Scanning {file_path}")
        
        parser = DocstringParser()
        metadata = parser.parse_file(file_path)
        
        if not metadata or not metadata.get('description'):
            logger.warning(f"No useful metadata found in {file_path}")
            return None
        
        generator = RegistryEntryGenerator(base_path)
        entry = generator.generate_entry(metadata, file_path)
        
        return entry
        
    except Exception as e:
        logger.error(f"Error scanning {file_path}: {e}")
        return None


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="EGOS Docstring Metadata Extractor - Extract metadata from Python docstrings"
    )
    
    parser.add_argument("--file", type=str,
                      help="Path to a single Python file to process")
    parser.add_argument("--output", type=str,
                      help="Path to write the extracted metadata (default: stdout)")
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
        
        if args.file:
            file_path = Path(args.file)
            entry = scan_file(file_path, base_path)
            
            if entry:
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(entry, f, indent=2)
                else:
                    print(json.dumps(entry, indent=2))
            else:
                print("No registry entry could be generated.")
                return 1
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()