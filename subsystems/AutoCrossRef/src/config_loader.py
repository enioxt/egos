#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module for loading and validating AutoCrossRef configurations."""
# 
# @references:
#   - subsystems/AutoCrossRef/src/config_loader.py

import yaml
import os
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # Moves up to AutoCrossRef root
    'config',
    'autocrossref_config.yaml'
)

class ConfigError(Exception):
    """Custom exception for configuration loading errors."""
    pass

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads the AutoCrossRef configuration from a YAML file.

    Args:
        config_path: Optional path to the configuration file.
                     If None, uses DEFAULT_CONFIG_PATH.

    Returns:
        A dictionary containing the configuration.

    Raises:
        ConfigError: If the configuration file cannot be found or parsed.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    if not os.path.exists(config_path):
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        if not isinstance(config_data, dict):
            raise ConfigError(f"Configuration file {config_path} is not a valid YAML dictionary.")
        return config_data
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing YAML configuration file {config_path}: {e}")
    except IOError as e:
        raise ConfigError(f"Error reading configuration file {config_path}: {e}")

if __name__ == '__main__':
    # Example usage and basic test
    print(f"Attempting to load default config from: {DEFAULT_CONFIG_PATH}")
    try:
        config = load_config()
        print("Configuration loaded successfully:")
        # print(yaml.dump(config, indent=2))

        # Basic validation checks based on DESIGN.md
        required_keys = [
            'scan_paths',
            'candidate_detection_patterns',
            'known_terms_to_paths',
            'standalone_keywords',
            'backup_options',
            'logging'
        ]
        for key in required_keys:
            if key not in config:
                print(f"WARNING: Required configuration key '{key}' not found.")

        if 'backup_options' in config and 'enabled' not in config['backup_options']:
            print("WARNING: 'backup_options.enabled' not found.")

        print("\nBasic structure check complete.")

    except ConfigError as err:
        print(f"ERROR: {err}")