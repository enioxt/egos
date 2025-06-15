# @references:
#   - subsystems/AutoCrossRef/src/orchestrator.py
# 
# AutoCrossRef Orchestrator

"""Main command-line interface and control flow for the AutoCrossRef subsystem."""

import argparse
import logging
import os
import sys

# Ensure other modules in src can be imported
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

EGOS_PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, '..', '..', '..'))

from config_loader import load_config
from scanner import scan_files
from candidate_detector import detect_candidates_in_file
from path_resolver import resolve_candidate, build_file_index
from existing_ref_checker import is_reference_present
from ref_injector import inject_reference

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_and_suggest(paths_args, apply_changes=False, interactive_approval=False, custom_config_path=None, output_path=None):
    """Main function to scan for cross-references and suggest/apply them."""
    logging.info("Starting AutoCrossRef orchestrator...")

    try:
        config = load_config(custom_config_path)
        logging.info(f"Configuration loaded successfully from: {custom_config_path or 'default location'}")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}", exc_info=True)
        return

    scan_paths_to_use = paths_args if paths_args else config.get('scan_paths', [])
    if not scan_paths_to_use:
        logging.warning("No scan paths specified either via CLI or in configuration. Exiting.")
        return
    
    logging.info(f"Scanning paths: {scan_paths_to_use}")
    logging.info(f"Include extensions: {config.get('include_file_extensions', [])}")
    logging.info(f"Exclude patterns: {config.get('exclude_patterns', [])}")

    try:
        logging.info("Building file index...")
        file_index = build_file_index(
            config.get('scan_paths', []),
            config.get('include_file_extensions', []),
            EGOS_PROJECT_ROOT
        )
        logging.info(f"File index built with {len(file_index)} entries.")
    except Exception as e:
        logging.error(f"Failed to build file index: {e}", exc_info=True)
        return

    try:
        files_to_process = scan_files(
            paths_to_scan=scan_paths_to_use,
            include_extensions=config.get('include_file_extensions', []),
            exclude_patterns=config.get('exclude_patterns', []),
            project_root_for_config_paths=EGOS_PROJECT_ROOT
        )
        logging.info(f"Found {len(files_to_process)} files to process.")
    except Exception as e:
        logging.error(f"Error during file scanning: {e}", exc_info=True)
        return

    if not files_to_process:
        logging.info("No files found to process based on current scan paths and filters.")
        return

    total_candidates_found = 0
    total_suggestions_made = 0
    total_references_injected = 0

    for file_path in files_to_process:
        logging.info(f"--- Processing file: {file_path} ---")
        try:
            candidates = detect_candidates_in_file(file_path, config)
            if not candidates:
                logging.info(f"No potential candidates found in {file_path}.")
                continue
            
            logging.info(f"Found {len(candidates)} potential candidates in {file_path}:")
            total_candidates_found += len(candidates)

            for candidate_text, candidate_type, source_context, original_link_target in candidates:
                logging.info(f"  Candidate: '{candidate_text}' (Type: {candidate_type}, Original Target: {original_link_target or 'N/A'}) ({source_context[:50]}...)")

                resolved_info = resolve_candidate(
                    (candidate_text, candidate_type, source_context, original_link_target),
                    file_index,
                    config,
                    file_path,
                    EGOS_PROJECT_ROOT
                )

                if resolved_info:
                    resolved_abs_path, resolved_by, preferred_link_text = resolved_info
                    logging.info(f"    Resolved to: '{resolved_abs_path}' (via {resolved_by}, preferred text: '{preferred_link_text}')")

                    if is_reference_present(file_path, resolved_abs_path, config):
                        logging.info(f"    Reference to '{resolved_abs_path}' already exists in {file_path}. Skipping.")
                    else:
                        logging.info(f"    New reference suggestion: Link to '{resolved_abs_path}' (as '{preferred_link_text}') in {file_path}")
                        total_suggestions_made += 1
                        
                        try:
                            source_dir = os.path.dirname(file_path)
                            path_to_inject_str = os.path.relpath(resolved_abs_path, start=source_dir).replace('\\', '/')
                        except ValueError: # Happens if paths are on different drives on Windows
                            # Fallback to a project-root relative path if possible, or absolute
                            try:
                                path_to_inject_str = os.path.relpath(resolved_abs_path, start=EGOS_PROJECT_ROOT).replace('\\', '/')
                            except ValueError:
                                path_to_inject_str = resolved_abs_path.replace('\\', '/') # Absolute path as last resort

                        logging.info(f"      Proposed injection string: '{path_to_inject_str}'")

                        should_inject = False
                        if apply_changes:
                            if interactive_approval:
                                approval = input(f"      Inject this reference into {os.path.basename(file_path)}? (y/N): ").strip().lower()
                                if approval == 'y':
                                    should_inject = True
                            else:
                                logging.info("      Auto-applying change (non-interactive mode).")
                                should_inject = True
                        
                        if should_inject:
                            # The dry_run for inject_reference is False because we are in an apply_changes block
                            if inject_reference(file_path, path_to_inject_str, resolved_abs_path, config, dry_run=False):
                                logging.info(f"      Successfully injected reference into {file_path}.")
                                total_references_injected +=1
                            else:
                                logging.error(f"      Failed to inject reference into {file_path}.")
                        elif apply_changes and not should_inject:
                             logging.info(f"      Injection skipped by user for {file_path}.")
                        elif not apply_changes: # Orchestrator dry-run mode
                            logging.info(f"      (Dry Run) Would attempt to inject reference into {file_path}.")
                else:
                    logging.warning(f"    Could not resolve candidate: '{candidate_text}' in {file_path}")
        
        except Exception as e:
            logging.error(f"Failed to process file {file_path}: {e}", exc_info=True)

    logging.info("--- Summary ---")
    logging.info(f"Total files processed: {len(files_to_process)}")
    logging.info(f"Total potential candidates found: {total_candidates_found}")
    logging.info(f"Total new reference suggestions: {total_suggestions_made}")
    if apply_changes:
        logging.info(f"Total references injected: {total_references_injected}")
    else:
        # Correctly report suggestions that would be made in dry run
        references_that_would_be_injected = total_suggestions_made
        logging.info(f"Total references that would be injected (dry run): {references_that_would_be_injected}")

    logging.info("AutoCrossRef orchestrator finished.")

def main():
    parser = argparse.ArgumentParser(description="AutoCrossRef: Automated Cross-Reference Management for EGOS.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    scan_parser = subparsers.add_parser('scan', help='Scan for potential cross-references and suggest/apply them.')
    scan_parser.add_argument('paths', nargs='*', help='Optional list of specific files or directories to scan. If omitted, uses paths from config.')
    scan_parser.add_argument('--apply', action='store_true', help='If present, approved suggestions will be written to files.')
    scan_parser.add_argument('--interactive', action='store_true', help='Prompts the user to approve/reject each suggestion interactively.')
    scan_parser.add_argument('--config', type=str, help='Path to a custom autocrossref_config.yaml file.')
    scan_parser.add_argument('--output', type=str, help='Path to save the suggestions report (e.g., report.json). Currently not implemented.')
    scan_parser.set_defaults(func=lambda args: scan_and_suggest(args.paths, args.apply, args.interactive, args.config, args.output))

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()