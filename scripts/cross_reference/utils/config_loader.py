#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Cross-Reference Tools - Configuration Loader

This module provides functionality for loading and validating configuration files
for the EGOS cross-reference tools. It ensures that configuration files adhere to
the defined schema and provides sensible defaults when needed.

Author: EGOS Development Team
Created: 2025-05-21
Version: 1.0.0

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

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║                  EGOS Cross-Reference Configuration Loader                   ║
# ║                                                                              ║
# ║  Loads and validates configuration files for EGOS cross-reference tools      ║
# ║                                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Standard library imports
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Third-party imports
try:
    import yaml
    from jsonschema import validate, ValidationError
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("config_loader")

# Constants
SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config_consolidated.yaml"
DEFAULT_SCHEMA_PATH = SCRIPT_DIR / "config_schema.json"
BANNER_WIDTH = 80

def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a banner with the given title and optional subtitle.
    
    Args:
        title: The title to display in the banner
        subtitle: Optional subtitle to display below the title
    """
    print("\n" + "╔" + "═" * (BANNER_WIDTH - 2) + "╗")
    print("║" + " " * (BANNER_WIDTH - 2) + "║")
    
    # Center the title
    title_padding = (BANNER_WIDTH - 2 - len(title)) // 2
    print("║" + " " * title_padding + title + " " * (BANNER_WIDTH - 2 - len(title) - title_padding) + "║")
    
    if subtitle:
        # Center the subtitle
        subtitle_padding = (BANNER_WIDTH - 2 - len(subtitle)) // 2
        print("║" + " " * subtitle_padding + subtitle + " " * (BANNER_WIDTH - 2 - len(subtitle) - subtitle_padding) + "║")
    
    print("║" + " " * (BANNER_WIDTH - 2) + "║")
    print("╚" + "═" * (BANNER_WIDTH - 2) + "╝")

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)} minutes, {remaining_seconds:.2f} seconds"
    else:
        hours = seconds // 3600
        remaining = seconds % 3600
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{int(hours)} hours, {int(minutes)} minutes, {seconds:.2f} seconds"

class ConfigLoader:
    """Configuration loader for EGOS cross-reference tools."""
    
    def __init__(self, config_path: Optional[str] = None, schema_path: Optional[str] = None):
        """Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file
            schema_path: Path to the schema file
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.schema_path = schema_path or DEFAULT_SCHEMA_PATH
        self.config = {}
        self.schema = {}
        self.is_valid = False
    
    def load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for configuration validation.
        
        Returns:
            The loaded schema
        """
        try:
            schema_path = Path(self.schema_path)
            if not schema_path.exists():
                logger.error(f"Schema file not found: {schema_path}")
                sys.exit(1)
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            logger.debug(f"Loaded schema from {schema_path}")
            return self.schema
        
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            sys.exit(1)
    
    def load_config(self) -> Dict[str, Any]:
        """Load the configuration file.
        
        Returns:
            The loaded configuration
        """
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.error(f"Configuration file not found: {config_path}")
                sys.exit(1)
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    self.config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    self.config = json.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {config_path.suffix}")
                    sys.exit(1)
            
            logger.debug(f"Loaded configuration from {config_path}")
            return self.config
        
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            sys.exit(1)
    
    def validate_config(self) -> bool:
        """Validate the configuration against the schema.
        
        Returns:
            True if the configuration is valid, False otherwise
        """
        try:
            # Load schema if not already loaded
            if not self.schema:
                self.load_schema()
            
            # Load config if not already loaded
            if not self.config:
                self.load_config()
            
            # Validate the configuration against the schema
            validate(instance=self.config, schema=self.schema)
            
            logger.info(f"{Fore.GREEN}Configuration is valid{Style.RESET_ALL}")
            self.is_valid = True
            return True
        
        except ValidationError as e:
            logger.error(f"{Fore.RED}Configuration validation error: {e.message}{Style.RESET_ALL}")
            logger.error(f"Path: {'.'.join(str(p) for p in e.path)}")
            self.is_valid = False
            return False
        
        except Exception as e:
            logger.error(f"{Fore.RED}Error validating configuration: {str(e)}{Style.RESET_ALL}")
            self.is_valid = False
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the loaded and validated configuration.
        
        Returns:
            The configuration dictionary
        """
        if not self.config:
            self.load_config()
        
        if not self.is_valid:
            self.validate_config()
        
        return self.config
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """Get a value from the configuration using a dot-separated path.
        
        Args:
            path: Dot-separated path to the configuration value
            default: Default value to return if the path is not found
            
        Returns:
            The configuration value or the default value
        """
        if not self.config:
            self.load_config()
        
        parts = path.split('.')
        current = self.config
        
        try:
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            
            return current
        
        except Exception:
            return default
    
    def print_config_summary(self) -> None:
        """Print a summary of the loaded configuration."""
        if not self.config:
            self.load_config()
        
        print_banner("Configuration Summary", f"Loaded from {self.config_path}")
        
        # Project settings
        print(f"\n{Fore.CYAN}┌─ Project Settings{Style.RESET_ALL}")
        print(f"  • Base Path: {self.get_value('project.base_path', 'Not specified')}")
        print(f"  • Default Scan Directories: {', '.join(self.get_value('project.default_scan_directories', []))}")
        
        # File settings
        print(f"\n{Fore.CYAN}┌─ File Settings{Style.RESET_ALL}")
        print(f"  • Extensions: {', '.join(self.get_value('files.extensions', []))}")
        print(f"  • Size Limits: Min {self.get_value('files.size_limits.min_bytes', 'N/A')} bytes, Max {self.get_value('files.size_limits.max_mb', 'N/A')} MB")
        
        # Performance settings
        print(f"\n{Fore.CYAN}┌─ Performance Settings{Style.RESET_ALL}")
        print(f"  • Max Workers: {self.get_value('performance.max_workers', 'N/A')}")
        print(f"  • Batch Size: {self.get_value('performance.batch_size', 'N/A')}")
        print(f"  • Cache Enabled: {self.get_value('performance.cache_enabled', 'N/A')}")
        print(f"  • Search Method: {self.get_value('performance.search_method', 'N/A')}")
        
        # Reporting settings
        print(f"\n{Fore.CYAN}┌─ Reporting Settings{Style.RESET_ALL}")
        print(f"  • Formats: {', '.join(self.get_value('reporting.formats', []))}")
        print(f"  • Retention Days: {self.get_value('reporting.retention_days', 'N/A')}")
        
        # Schema version
        print(f"\n{Fore.CYAN}┌─ Schema Information{Style.RESET_ALL}")
        print(f"  • Version: {self.get_value('schema.version', 'N/A')}")
        print(f"  • Validation Enabled: {self.get_value('schema.validation_enabled', 'N/A')}")
        
        print(f"\n{Fore.GREEN}Configuration loaded successfully{Style.RESET_ALL}")
        print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")

def main():
    """Main entry point for the script."""
    try:
        print_banner("EGOS Cross-Reference Configuration Loader", "Validating configuration files")
        
        # Parse command-line arguments
        import argparse
        parser = argparse.ArgumentParser(description="EGOS Cross-Reference Configuration Loader")
        parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to the configuration file")
        parser.add_argument("--schema", "-s", type=str, default=DEFAULT_SCHEMA_PATH, help="Path to the schema file")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        
        args = parser.parse_args()
        
        # Set logging level based on verbosity
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Load and validate configuration
        loader = ConfigLoader(config_path=args.config, schema_path=args.schema)
        loader.load_schema()
        loader.load_config()
        
        if loader.validate_config():
            loader.print_config_summary()
            sys.exit(0)
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()