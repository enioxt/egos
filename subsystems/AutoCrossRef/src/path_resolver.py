#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module for resolving identified candidate strings to canonical file paths."""
# 
# @references:
#   - subsystems/AutoCrossRef/src/path_resolver.py

import os
from typing import Dict, Any, Optional, List, Set

# Assuming EGOS_PROJECT_ROOT needs to be defined similarly to scanner.py
# This should ideally come from a shared project settings module or be passed around.
EGOS_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Placeholder for a file index (filename/title -> absolute_path)
# This would be built by scanning the project (e.g., during orchestrator startup)
_file_index: Optional[Dict[str, str]] = None
_file_index_built = False

def build_file_index(config: Dict[str, Any], scanner_func) -> None:
    """
    Builds an index of project files (markdown for now) mapping titles and filenames to paths.
    This is a simplified initial version.
    Args:
        config: The application configuration.
        scanner_func: The scan_project_files function from scanner.py.
    """
    global _file_index, _file_index_built
    if _file_index_built:
        return

    print("Path Resolver: Building file index...", flush=True)
    _file_index = {}
    # Use scanner_func to get all relevant files (e.g., markdown)
    # For now, let's assume scanner_func is available and gives us markdown files.
    files_to_index = scanner_func(config) # This might need specific config for indexing

    for file_path in files_to_index:
        filename = os.path.basename(file_path)
        _file_index[filename.lower()] = file_path # Index by lowercase filename

        # Attempt to extract title from Markdown frontmatter (simplified)
        if file_path.endswith('.md'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if len(lines) > 1 and lines[0].strip() == '---':
                        for line in lines[1:]:
                            if line.strip() == '---': break
                            if line.lower().startswith('title:'):
                                title = line.split(':', 1)[1].strip().strip('"\'')
                                _file_index[title.lower()] = file_path # Index by lowercase title
                                break
            except Exception as e:
                print(f"Path Resolver: Error indexing title for {file_path}: {e}", flush=True)
    
    _file_index_built = True
    print(f"Path Resolver: File index built. {len(_file_index) if _file_index else 0} entries.", flush=True)

def resolve_candidate_to_path(candidate_text: str, 
                              source_file_path: str, 
                              config: Dict[str, Any],
                              original_link_target: Optional[str] = None) -> Optional[str]:
    """
    Attempts to resolve a candidate string to a canonical file path.

    Args:
        candidate_text: The identified candidate string (e.g., "MQP", "KOIOS PDD Standard").
        source_file_path: The path of the file where the candidate was found.
        config: The loaded AutoCrossRef configuration.
        original_link_target: If the candidate came from an existing markdown link, this is its original target.

    Returns:
        An absolute, canonical file path if resolved, otherwise None.
    """
    global _file_index
    if not _file_index_built:
        # This should ideally be called by an orchestrator once at the start.
        # For standalone testing, we might call it here, but it's inefficient.
        print("Warning: File index not pre-built. Path resolution might be incomplete.", flush=True)
        # In a real scenario, you'd pass the scanner function here or ensure index is built.
        # from scanner import scan_project_files # Avoid circular import for simple test
        # build_file_index(config, scan_project_files) 

    # 1. Handle existing Markdown links (if original_link_target is provided)
    if original_link_target:
        if os.path.isabs(original_link_target):
            resolved_path = os.path.normpath(original_link_target)
        else:
            # Resolve relative to the source file's directory
            source_dir = os.path.dirname(source_file_path)
            resolved_path = os.path.normpath(os.path.join(source_dir, original_link_target))
        
        if os.path.exists(resolved_path):
            return resolved_path
        else:
            # If original link doesn't resolve, fall through to other methods using candidate_text
            pass 

    # 2. Check known_terms_to_paths from config
    known_terms_map = config.get('known_terms_to_paths', {})
    # Case-insensitive check for keys in known_terms_map
    for term, path_str in known_terms_map.items():
        if term.lower() == candidate_text.lower():
            if os.path.isabs(path_str):
                abs_path = os.path.normpath(path_str)
            else:
                abs_path = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, path_str))
            if os.path.exists(abs_path):
                return abs_path
            else:
                print(f"Warning: Configured path for '{term}' not found: {abs_path}", flush=True)

    # 3. Check against the file index (filenames and titles)
    if _file_index:
        resolved_path = _file_index.get(candidate_text.lower())
        if resolved_path and os.path.exists(resolved_path):
            return resolved_path

    # 4. Direct filename match in common directories (simplified)
    # This is a fallback if not in index or known_terms. More robust scanning needed for a full system.
    # For example, if candidate_text is 'README.md'
    common_dirs_to_check = config.get('scan_paths', ['docs/', 'subsystems/'])
    if '.' in candidate_text: # Basic check if it looks like a filename
        for rel_dir in common_dirs_to_check:
            potential_path = os.path.normpath(os.path.join(EGOS_PROJECT_ROOT, rel_dir, candidate_text))
            if os.path.exists(potential_path):
                return potential_path

    return None

if __name__ == '__main__':
    try:
        from config_loader import load_config, ConfigError
        from scanner import scan_project_files # Needed for build_file_index
        # For testing candidate_detector output
        from candidate_detector import PotentialCandidate 

        print("Path Resolver: Attempting to load configuration...", flush=True)
        app_config = load_config()
        print("Path Resolver: Configuration loaded.", flush=True)

        # Crucial: Build the file index before trying to resolve paths
        build_file_index(app_config, scan_project_files)

        # Test cases
        test_candidates: List[PotentialCandidate] = [
            ("C:/EGOS/dummy.md", "MQP", 1, "keyword", None, None),
            ("C:/EGOS/dummy.md", "KOIOS PDD Standard", 2, "capitalized_phrase", None, None),
            ("C:/EGOS/dummy.md", "ATRiAN.md", 3, "filename_guess", None, None), # Test filename from index
            ("C:/EGOS/dummy.md", "non_existent_term", 4, "keyword", None, None),
            ("C:/EGOS/subsystems/AutoCrossRef/README.md", "config_loader.py", 5, "filename_guess", None, None), # Relative from a source
            ("C:/EGOS/subsystems/AutoCrossRef/README.md", "src/orchestrator.py", 6, "markdown_link_path_part", None, "src/orchestrator.py"),
            ("C:/EGOS/README.md", "ROADMAP.md", 7, "markdown_link_path_part", None, "ROADMAP.md"),
        ]

        print("\nPath Resolver: Testing path resolution for candidates...", flush=True)
        for cand_tuple in test_candidates:
            source_f, text, _, _, _, orig_link = cand_tuple
            resolved = resolve_candidate_to_path(text, source_f, app_config, original_link_target=orig_link)
            status = "RESOLVED" if resolved else "NOT RESOLVED"
            print(f"  - Candidate: '{text}' (OriginalLink: {orig_link}) -> {status}", flush=True)
            if resolved:
                print(f"    To: {resolved}", flush=True)
        
    except ConfigError as e:
        print(f"Path Resolver: Configuration error - {e}", flush=True)
    except ImportError as e:
        print(f"Path Resolver: Import error - {e}. Ensure all modules are accessible.", flush=True)
    except Exception as e:
        print(f"Path Resolver: An unexpected error occurred: {e}", flush=True)
        import traceback
        traceback.print_exc()