#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-Reference System Serialization Utilities

This module provides standardized serialization utilities for the EGOS Cross-Reference System,
ensuring consistent handling of Path objects, custom data types, and other serialization needs
across all cross-reference modules.

@references:
- 🔗 Reference: [file_reference_checker_ultra.py](../../cross_reference/file_reference_checker_ultra.py)
- 🔗 Reference: [orphaned_file_detector.py](../../cross_reference/validator/orphaned_file_detector.py)
- 🔗 Reference: [ROADMAP.md](../../../ROADMAP.md#cross-reference-tools-enhancement)
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md

Created: 2025-05-21
Author: EGOS Team
Version: 1.0.0"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import json
import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Optional, Union

# ANSI color codes for terminal output
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
    "WHITE": "\033[97m",
    "GRAY": "\033[90m"
}

class EGOSJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for EGOS that handles Path objects, sets, and other custom types.
    
    This encoder ensures consistent serialization across all EGOS modules, particularly
    for the Cross-Reference System where Path objects are commonly used.
    """
    def default(self, obj: Any) -> Any:
        """
        Convert special types to JSON-serializable objects.
        
        Args:
            obj: The object to serialize
            
        Returns:
            A JSON-serializable representation of the object
        """
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            return obj.to_dict()
        return super().default(obj)


def serialize_to_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """
    Serialize data to a JSON string using the EGOS JSON encoder.
    
    Args:
        data: The data to serialize
        indent: Number of spaces for indentation (default: 2)
        ensure_ascii: Whether to escape non-ASCII characters (default: False)
        
    Returns:
        JSON string representation of the data
    """
    return json.dumps(data, cls=EGOSJSONEncoder, indent=indent, ensure_ascii=ensure_ascii)


def save_json_file(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file using the EGOS JSON encoder.
    
    Args:
        data: The data to save
        file_path: Path to the output file
        indent: Number of spaces for indentation (default: 2)
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
        
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=EGOSJSONEncoder, indent=indent, ensure_ascii=False)


def load_json_file(file_path: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The deserialized data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_colored(text: str, color: str = "RESET", bold: bool = False) -> str:
    """
    Format text with ANSI color codes.
    
    Args:
        text: The text to format
        color: Color name from the COLORS dictionary
        bold: Whether to make the text bold
        
    Returns:
        Formatted text with ANSI color codes
    """
    color_code = COLORS.get(color, COLORS["RESET"])
    bold_code = COLORS["BOLD"] if bold else ""
    return f"{bold_code}{color_code}{text}{COLORS['RESET']}"