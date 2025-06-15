#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module for identifying potential cross-reference candidates in files."""
# 
# @references:
#   - subsystems/AutoCrossRef/src/candidate_detector.py

import re
import os
from typing import List, Dict, Any, Tuple, Optional

# Assuming PotentialCandidate structure from DESIGN.md:
# (source_file_path: str, candidate_text: str, line_number: int, 
#  identification_method: str, resolved_target_path: Optional[str],
#  original_link_target: Optional[str])
PotentialCandidate = Tuple[str, str, int, str, Optional[str], Optional[str]]

def identify_candidates_in_file(file_path: str, config: Dict[str, Any]) -> List[PotentialCandidate]:
    """
    Identifies potential cross-reference candidates within a single file.

    Args:
        file_path: Absolute path to the file to scan.
        config: The loaded AutoCrossRef configuration dictionary.

    Returns:
        A list of PotentialCandidate tuples found in the file.
    """
    candidates: List[PotentialCandidate] = []
    detection_patterns = config.get('candidate_detection_patterns', [])
    standalone_keywords = config.get('standalone_keywords', [])

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line_content in enumerate(f, 1):
                # 1. Apply regex patterns from candidate_detection_patterns
                for pattern_info in detection_patterns:
                    pattern_name = pattern_info.get('name', 'unknown_regex')
                    regex_str = pattern_info.get('regex')
                    pattern_type = pattern_info.get('type', pattern_name)
                    
                    if not regex_str:
                        continue

                    try:
                        for match in re.finditer(regex_str, line_content):
                            candidate_text = match.group(0) # Full match
                            original_link_target = None
                            # If regex has named groups 'text' and 'path' (for markdown links)
                            if 'text' in match.groupdict() and 'path' in match.groupdict():
                                candidate_text = match.group('text')
                                original_link_target = match.group('path')
                            
                            # Simplified: resolved_target_path is None for now
                            candidates.append((file_path, candidate_text, line_num, pattern_type, None, original_link_target))
                    except re.error as e:
                        print(f"Warning: Invalid regex pattern '{regex_str}' for '{pattern_name}': {e}", flush=True)

                # 2. Check for standalone keywords (case-sensitive for now, could be made insensitive)
                for keyword in standalone_keywords:
                    # Use regex to find whole word matches for keywords
                    # This avoids matching substrings within larger words
                    keyword_regex = r'\b' + re.escape(keyword) + r'\b'
                    try:
                        for match in re.finditer(keyword_regex, line_content):
                            candidates.append((file_path, match.group(0), line_num, "keyword_match", None, None))
                    except re.error as e:
                        # Should not happen with re.escape, but good practice
                        print(f"Warning: Invalid regex for keyword '{keyword}': {e}", flush=True)

    except IOError as e:
        print(f"Warning: Could not read file {file_path}: {e}", flush=True)
    except Exception as e:
        print(f"Warning: Unexpected error processing file {file_path}: {e}", flush=True)
    
    return candidates

if __name__ == '__main__':
    # Example usage and basic test
    try:
        from config_loader import load_config, ConfigError
        from scanner import scan_project_files

        print("Candidate Detector: Attempting to load configuration...", flush=True)
        app_config = load_config()
        print("Candidate Detector: Configuration loaded.", flush=True)

        # For testing, let's scan a small subset of files or a specific file
        # For example, the AutoCrossRef README itself
        test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'README.md'))
        
        if not os.path.exists(test_file_path):
            print(f"Test file {test_file_path} not found. Skipping candidate detection test.", flush=True)
        else:
            print(f"\nCandidate Detector: Scanning file '{test_file_path}' for candidates...", flush=True)
            detected_candidates = identify_candidates_in_file(test_file_path, app_config)

            if detected_candidates:
                print(f"\nCandidate Detector: Found {len(detected_candidates)} candidates in '{test_file_path}':", flush=True)
                for cand in detected_candidates[:20]: # Print first 20
                    print(f"  - Line {cand[2]}: '{cand[1]}' (Type: {cand[3]}, OriginalLink: {cand[5]})", flush=True)
                if len(detected_candidates) > 20:
                    print(f"  ... and {len(detected_candidates) - 20} more.", flush=True)
            else:
                print(f"Candidate Detector: No candidates found in '{test_file_path}'.", flush=True)

    except ConfigError as e:
        print(f"Candidate Detector: Configuration error - {e}", flush=True)
    except ImportError as e:
        print(f"Candidate Detector: Import error - {e}. Make sure all modules are accessible.", flush=True)
    except Exception as e:
        print(f"Candidate Detector: An unexpected error occurred: {e}", flush=True)