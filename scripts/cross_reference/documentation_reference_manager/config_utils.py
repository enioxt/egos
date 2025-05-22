"""Configuration Utilities for Documentation Reference Manager

This module provides utilities for loading and processing configuration
for the documentation reference manager system.

It implements the principle of Conscious Modularity by separating
configuration handling from core functionality.

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

# Configure module logger
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join("config", "cross_reference", "config.yaml")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file (default: config/cross_reference/config.yaml)
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If configuration file does not exist
        yaml.YAMLError: If configuration file is invalid YAML
    """
    if config_path is None:
        # Try to find config in default location
        base_path = _find_project_root()
        config_path = os.path.join(base_path, DEFAULT_CONFIG_PATH)
    
    logger.info(f"Loading configuration from {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate configuration
        _validate_config(config)
        
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def _find_project_root() -> str:
    """Find the project root directory.
    
    Walks up the directory tree from the current directory
    until it finds a directory containing config/cross_reference/config.yaml
    or a directory containing .git.
    
    Returns:
        Absolute path to project root directory
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Walk up the directory tree
    while True:
        # Check if this is the project root
        if os.path.exists(os.path.join(current_dir, "config", "cross_reference", "config.yaml")):
            return current_dir
        
        # Check for .git directory as fallback
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        
        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        
        # If we've reached the root of the filesystem, stop
        if parent_dir == current_dir:
            # Fallback to current working directory
            return os.getcwd()
        
        current_dir = parent_dir


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Check for required sections
    required_sections = ["general", "file_monitoring", "verification", "reporting"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate general section
    if "base_path" not in config["general"]:
        raise ValueError("Missing required configuration: general.base_path")
    
    # Validate file_monitoring section
    if "extensions" not in config["file_monitoring"]:
        raise ValueError("Missing required configuration: file_monitoring.extensions")


def get_file_patterns(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract file pattern configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary containing file pattern configuration
    """
    return {
        "extensions": config["file_monitoring"].get("extensions", [".md"]),
        "exclude_dirs": config["file_monitoring"].get("exclude_dirs", []),
        "include_dirs": config["file_monitoring"].get("include_dirs", [])
    }


def get_cross_reference_rules(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract cross-reference rules from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of cross-reference rule dictionaries
    """
    return config.get("cross_reference_rules", [])


def get_verification_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract verification configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary containing verification configuration
    """
    return config.get("verification", {})


def get_reporting_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract reporting configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary containing reporting configuration
    """
    return config.get("reporting", {})


def resolve_paths(config: Dict[str, Any], base_path: Optional[str] = None) -> Dict[str, Any]:
    """Resolve relative paths in configuration to absolute paths.
    
    Args:
        config: Configuration dictionary
        base_path: Base path to resolve relative paths against (default: config["general"]["base_path"])
        
    Returns:
        Configuration dictionary with resolved paths
    """
    if base_path is None:
        base_path = config["general"].get("base_path", os.getcwd())
    
    # Create a deep copy of the configuration
    resolved_config = config.copy()
    
    # Resolve paths in general section
    if "report_dir" in resolved_config["general"]:
        resolved_config["general"]["report_dir"] = os.path.join(
            base_path, resolved_config["general"]["report_dir"]
        )
    
    if "checkpoint_dir" in resolved_config["general"]:
        resolved_config["general"]["checkpoint_dir"] = os.path.join(
            base_path, resolved_config["general"]["checkpoint_dir"]
        )
    
    # Resolve paths in reporting section
    if "dashboard" in resolved_config.get("reporting", {}):
        if "path" in resolved_config["reporting"]["dashboard"]:
            resolved_config["reporting"]["dashboard"]["path"] = os.path.join(
                base_path, resolved_config["reporting"]["dashboard"]["path"]
            )
    
    return resolved_config