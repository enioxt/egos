# @references:
#   - scripts/regen_references.py
# 
import sys
import pathlib
import datetime
import argparse
import os
import json
from fnmatch import fnmatch
from html import escape  # For HTML escaping in the report
from typing import Optional, Union, Any, Callable, Generator # For older Python type hints
import yaml  # Added for parsing CROSSREF_STANDARD.md

# Optional progress bar
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = None

# Ensure PROJECT_ROOT is in sys.path for the import below
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from subsystems.AutoCrossRef.src.ref_injector import inject_reference

# ------------------------------------------------------------------
# Define excluded directory names (top-level relative to PROJECT_ROOT)
EXCLUDE_TOP_LEVEL_DIR_NAMES = [
    'website', '.git', '.github', '.vscode', '__pycache__', 'tools',
    '_ref_bak', 'node_modules', 'venv', '.venv', 'dist', 'build',
    'target', 'eggs', '.eggs', 'wheels', 'htmlcov', '.tox', '.nox',
    '.hypothesis', '.pytest_cache', 'docs_build', 'site',
    'subsystems/AutoCrossRef/reports' # Exclude the report directory itself
]

# Precompute sets for efficient exclusion checking, AFTER EXCLUDE_TOP_LEVEL_DIR_NAMES is defined
_EXCLUDE_TOP_LEVEL_SINGLE_NAMES = {
    p for p in EXCLUDE_TOP_LEVEL_DIR_NAMES if '/' not in p and '\\' not in p
}
_EXCLUDE_TOP_LEVEL_MULTI_PATHS_STR = { # Store as strings for direct comparison
    p.replace('/', os.sep) for p in EXCLUDE_TOP_LEVEL_DIR_NAMES if '/' in p or '\\' in p
}

# Define patterns for excluded directories anywhere in the tree
EXCLUDE_DIR_PATTERNS = [
    '*.egg-info',      # Packaging metadata
    '*venv*',          # Any virtual environment folders (venv, .venv, venv_py312, etc.)
    '.venv*',
    '*_archive*',      # Archive or backup directories
    '*archive*',
    'zz_archive'
]

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoCrossRef Execution Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --background: hsl(0, 0%, 100%);
            --foreground: hsl(222.2, 84%, 4.9%);
            --card: hsl(0, 0%, 100%);
            --card-foreground: hsl(222.2, 84%, 4.9%);
            --primary: hsl(221.2, 83.2%, 53.3%);
            --primary-alt: #0A2342; /* EGOS Deep Blue */
            --primary-foreground: hsl(210, 40%, 98%);
            --secondary: hsl(210, 40%, 96.1%);
            --secondary-foreground: hsl(222.2, 47.4%, 11.2%);
            --accent-orange: #FF6600; /* EGOS Warm Orange */
            --destructive: hsl(0, 84.2%, 60.2%);
            --destructive-foreground: hsl(210, 40%, 98%);
            --muted: hsl(210, 40%, 96.1%);
            --muted-foreground: hsl(215.4, 16.3%, 46.9%);
            --success-green: hsl(140, 70%, 40%);
            --border: hsl(214.3, 31.8%, 91.4%);
            --radius: 0.5rem;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--background);
            color: var(--foreground);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: var(--card);
            padding: 25px;
            border-radius: var(--radius);
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        h1, h2, h3 {{
            font-family: 'Playfair Display', serif;
            color: var(--primary-alt);
            margin-top: 0;
        }}
        h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
        h2 {{ font-size: 1.8em; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid var(--primary-alt); padding-bottom: 5px; }}
        h3 {{ font-size: 1.4em; margin-top: 25px; margin-bottom: 10px; color: var(--accent-orange); }}
        p, li {{ color: var(--muted-foreground); }}
        .timestamp {{ font-size: 0.9em; color: var(--muted-foreground); margin-bottom: 20px; }}
        .summary-section ul {{ list-style-type: none; padding-left: 0; }}
        .summary-section li {{ margin-bottom: 8px; font-size: 1.1em; }}
        .summary-section strong {{ color: var(--foreground); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: var(--secondary);
            color: var(--secondary-foreground);
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background-color: hsl(0, 0%, 98%); }}
        td code {{
            background-color: var(--muted);
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--primary-alt);
        }}
        .status-modified {{ color: var(--success-green); font-weight: bold; }}
        .status-skipped_idempotent {{ color: var(--accent-orange); }}
        .status-error {{ color: var(--destructive); font-weight: bold; }}
        .status-error_backup, .status-error_read, .status-error_write {{ color: var(--destructive); }}
        .path-cell {{ word-break: break-all; }}
        .excluded-lists {{ margin-top: 10px; padding-left: 20px; }}
        .excluded-lists li {{ font-family: monospace; font-size: 0.9em; color: var(--muted-foreground); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AutoCrossRef Execution Report</h1>
        <p class="timestamp">Generated: {generation_time}</p>

        <h2>Execution Summary</h2>
        <div class="summary-section">
            <ul>
                <li><strong>Project Root:</strong> <code>{project_root}</code></li>
                <li><strong>Total Files Scanned:</strong> {total_scanned_files}</li>
                <li><strong>Total Files Processed (Attempted Injection):</strong> {total_processed_attempts}</li>
                <li><strong>Files Successfully Modified:</strong> <span class="status-modified">{modified_count}</span></li>
                <li><strong>References Already Present (Skipped):</strong> <span class="status-skipped_idempotent">{idempotent_count}</span></li>
                <li><strong>Files with Errors:</strong> <span class="status-error">{error_count}</span></li>
                <li><strong>Files Skipped (Exclusion Rules/Type):</strong> {skipped_due_to_exclusion_count}</li>
            </ul>
            <h3>Exclusion Rules Applied:</h3>
            <p><strong>Top-Level Excluded Directories:</strong></p>
            <ul class="excluded-lists">
                {excluded_top_level_dirs_html}
            </ul>
            <p><strong>Excluded Directory Patterns:</strong></p>
            <ul class="excluded-lists">
                {excluded_dir_patterns_html}
            </ul>
        </div>

        {modified_files_table}
        {idempotent_files_table}
        {error_files_table}

    </div>
</body>
</html>
"""

TABLE_TEMPLATE = """
<h2>{title} ({count})</h2>
{no_files_message}
<table>
    <thead>
        <tr>
            {headers}
        </tr>
    </thead>
    <tbody>
        {rows}
    </tbody>
</table>
"""

def generate_html_table(title, results_list, headers_map, status_key_for_count=None):
    if not results_list:
        no_files_html = "<p><em>No files in this category.</em></p>"
        return TABLE_TEMPLATE.format(
            title=title,
            count=0,
            no_files_message=no_files_html,
            headers="",
            rows=""
        ).replace("<table>", "<div style='margin-top:15px;'>").replace("</table>", "</div>")

    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers_map.keys())
    rows_html = ""
    for item in results_list:
        rows_html += "<tr>"
        for data_key, cell_class in headers_map.items():
            content = item.get(data_key, "N/A")
            if data_key == "backup_path" and content is None:
                content = "N/A (Disabled or Failed)"
            
            status_class_str = ""
            if data_key == "status" and content:
                 status_class_str = f"status-{str(content).lower().replace('error_', 'error')}" # Ensure no leading space for class name

            rows_html += f"<td class='{escape(cell_class)} {escape(status_class_str)}'><code>{escape(str(content))}</code></td>"
        rows_html += "</tr>"

    return TABLE_TEMPLATE.format(
        title=title,
        count=len(results_list),
        no_files_message="",
        headers=header_html,
        rows=rows_html
    )

def generate_html_report(all_results, project_root_path, excluded_top_level, excluded_patterns, skipped_exclusions, total_scanned):
    generation_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    modified_files = [r for r in all_results if r['status'] == 'modified']
    idempotent_files = [r for r in all_results if r['status'] == 'skipped_idempotent']
    error_files = [r for r in all_results if 'error' in r['status']]
    
    total_processed_attempts = len(all_results)

    modified_headers = {"File Path": "path-cell", "Backup Path": "path-cell"}
    # Adjusting keys to match the dictionary returned by inject_reference
    modified_table_html = generate_html_table("Files Modified", modified_files, {"file_path": "path-cell", "backup_path": "path-cell"})

    idempotent_headers = {"File Path": "path-cell", "Message": ""}
    idempotent_table_html = generate_html_table("References Already Present (Skipped)", idempotent_files, {"file_path": "path-cell", "message": ""})

    error_headers = {"File Path": "path-cell", "Status": "status-cell", "Message": ""}
    error_table_html = generate_html_table("Errors Encountered", error_files, {"file_path": "path-cell", "status": "status-cell", "message": ""})

    excluded_top_level_html = "".join(f"<li><code>{escape(d)}</code></li>" for d in excluded_top_level)
    excluded_dir_patterns_html = "".join(f"<li><code>{escape(p)}</code></li>" for p in excluded_patterns)

    html_content = HTML_REPORT_TEMPLATE.format(
        generation_time=generation_time_str,
        project_root=escape(str(project_root_path)),
        total_scanned_files=total_scanned,
        total_processed_attempts=total_processed_attempts,
        modified_count=len(modified_files),
        idempotent_count=len(idempotent_files),
        error_count=len(error_files),
        skipped_due_to_exclusion_count=skipped_exclusions,
        excluded_top_level_dirs_html=excluded_top_level_html,
        excluded_dir_patterns_html=excluded_dir_patterns_html,
        modified_files_table=modified_table_html,
        idempotent_files_table=idempotent_table_html,
        error_files_table=error_table_html
    )
    return html_content

def walk_and_inject(is_dry_run: bool = False, verbose: bool = False):
    config = {
        'backup_options': {'enabled': True, 'directory': str(PROJECT_ROOT / '_ref_bak')},
        'resolve_options': {'enabled': False},
        'file_index_cache_ttl': 0,
        'parser_options': {'python': {}, 'markdown': {}},
    }
    
    all_injection_results = []
    skipped_due_to_exclusion_count = 0
    total_scanned_files = 0

    print(f"Starting scan from project root: {PROJECT_ROOT}")
    if is_dry_run:
        print("Running in DRY RUN mode – no files will be modified.")
    print(f"Excluding top-level directories: {EXCLUDE_TOP_LEVEL_DIR_NAMES}")
    print(f"Excluding directory patterns: {EXCLUDE_DIR_PATTERNS}")

    for path in PROJECT_ROOT.rglob('*'):
        total_scanned_files += 1
        if not path.is_file():
            continue

        try:
            rel_path = path.relative_to(PROJECT_ROOT)
        except ValueError:
            print(f"Warning: Path {path} is not relative to {PROJECT_ROOT}. Skipping.")
            skipped_due_to_exclusion_count +=1
            continue

        if rel_path.parts and rel_path.parts[0] in EXCLUDE_TOP_LEVEL_DIR_NAMES:
            if verbose:
                print(f"SKIP top-level excl: {rel_path}")
            skipped_due_to_exclusion_count += 1
            continue

        # Evaluate exclusion patterns across all ancestor directory names, not just the immediate parent.
        from fnmatch import fnmatch
        skip_due_pattern = any(
            fnmatch(part, pattern)
            for part in rel_path.parts
            for pattern in EXCLUDE_DIR_PATTERNS
        )
        if skip_due_pattern:
            if verbose:
                print(f"SKIP pattern excl: {rel_path}")
            skipped_due_to_exclusion_count += 1
            continue

        if path.suffix not in ['.py', '.md']:
            if verbose:
                print(f"SKIP unsupported type: {rel_path}")
            skipped_due_to_exclusion_count += 1
            continue

        ref_to_add = str(rel_path).replace('\\', '/')
        
        try:
            if verbose:
                print(f"INJECT attempt: {rel_path}")
            result_dict = inject_reference(str(path), ref_to_add, str(path), config, dry_run=is_dry_run)
            all_injection_results.append(result_dict)
        except Exception as e:
            print(f"Critical Error calling inject_reference for {path}: {e}")
            all_injection_results.append({
                "file_path": str(path),
                "status": "error_critical_call",
                "message": f"Critical error during inject_reference call: {str(e)}",
                "backup_path": None,
                "content_changed": False
            })

    print(f"Scan complete. Processed {len(all_injection_results)} files for injection attempts.")
    print(f"Total files scanned: {total_scanned_files}")
    print(f"Total files skipped due to exclusion/type rules: {skipped_due_to_exclusion_count}")

    report_html_content = generate_html_report(
        all_injection_results,
        PROJECT_ROOT,
        EXCLUDE_TOP_LEVEL_DIR_NAMES,
        EXCLUDE_DIR_PATTERNS,
        skipped_due_to_exclusion_count,
        total_scanned_files
    )
    
    report_dir = PROJECT_ROOT / 'subsystems' / 'AutoCrossRef' / 'reports'
    if not report_dir.exists():
        report_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created report directory: {report_dir}")

    report_filename = f"autocrossref_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_filepath = report_dir / report_filename

    try:
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(report_html_content)
        print(f"Successfully generated HTML report: {report_filepath}")
    except Exception as e:
        print(f"Error writing HTML report to {report_filepath}: {e}")

#######################################################################
# Improved entry-point with extra UX flags                            #
#######################################################################

def run_and_report(
    *,
    is_dry_run: bool,
    verbose: bool,
    path_globs: Optional[list],
    max_candidates: Optional[int],
    auto_yes: bool,
    json_out: Optional[str],
    file_extensions: Optional[list[str]] = None, # Added for --ext
    mode: str = 'fix-core', # New mode argument
):
    """Main execution wrapper providing quick-scope, confirmation and progress bar."""
    print("DEBUG: run_and_report entered.", file=sys.stderr)

    # Error tracking for better reporting
    error_count = 0
    error_types = {}
    non_compliant_files_count = 0  # For strict mode reporting
    
    # Process extensions
    if not file_extensions:
        file_extensions = ['.py', '.md']  # Default if None or empty list
    
    # Normalize extensions to start with dot
    target_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in file_extensions]
    print(f"DEBUG: Processing files with extensions: {', '.join(target_extensions)}", file=sys.stderr)
    
    # ------------------------------------------------------------------
    # Build candidate file list first using os.walk with directory pruning
    # to avoid traversing excluded folders at all
    # ------------------------------------------------------------------
    all_candidate_paths: list[pathlib.Path] = []
    skipped_due_to_exclusion_count = 0
    total_scanned_files = 0

    def _dir_is_excluded(rel_parts: tuple[str, ...]) -> bool:
        """Return True if the directory represented by rel_parts should be excluded."""
        if not rel_parts:
            return False

        # Check 1: Top-level single name exclusion (e.g., '.git')
        if rel_parts[0] in _EXCLUDE_TOP_LEVEL_SINGLE_NAMES:
            # print(f"DEBUG: Excluding '{os.path.join(*rel_parts)}' due to top-level single name: {rel_parts[0]}", file=sys.stderr)
            return True

        # Check 2: Top-level multi-segment path exclusion (e.g., 'subsystems/AutoCrossRef/reports')
        current_rel_path_str = os.path.join(*rel_parts)
        if current_rel_path_str in _EXCLUDE_TOP_LEVEL_MULTI_PATHS_STR:
            # print(f"DEBUG: Excluding '{current_rel_path_str}' due to top-level multi-path match.", file=sys.stderr)
            return True
            
        # Check 3: Pattern exclusion for any part of the path (e.g., '*venv*')
        for part in rel_parts:
            if any(fnmatch(part, pattern) for pattern in EXCLUDE_DIR_PATTERNS):
                # print(f"DEBUG: Excluding '{os.path.join(*rel_parts)}' due to pattern match on part '{part}'", file=sys.stderr)
                return True
        return False

    for root, dirs, files in os.walk(PROJECT_ROOT):
        root_path = pathlib.Path(root)
        try:
            rel_root_parts = root_path.relative_to(PROJECT_ROOT).parts
        except ValueError:
            # Should not happen, but guard anyway
            rel_root_parts = ()
        # Prune directories that should be excluded _before_ descending
        dirs[:] = [d for d in dirs if not _dir_is_excluded(rel_root_parts + (d,))]

        # Skip this root completely if it is excluded
        if _dir_is_excluded(rel_root_parts):
            continue

        for fname in files:
            total_scanned_files += 1
            file_path = root_path / fname
            rel_path = file_path.relative_to(PROJECT_ROOT)

            # Extension filter early
            # We already normalized target_extensions at the beginning of the function
            if file_path.suffix not in target_extensions:
                skipped_due_to_exclusion_count += 1
                continue

            # Apply path_globs filter if provided
            rel_posix = str(rel_path).replace('\\', '/')
            if path_globs and not any(fnmatch(rel_posix, g) for g in path_globs):
                skipped_due_to_exclusion_count += 1
                continue

            all_candidate_paths.append(file_path)

    # ------------------------------------------------------------------

    # Apply --max N
    if max_candidates is not None:
        all_candidate_paths = all_candidate_paths[: max_candidates]

    if is_dry_run:
        mode_msg = 'DRY RUN'
    else:
        mode_msg = 'LIVE RUN'
    print(f"Total scanned: {total_scanned_files} | Eligible for processing: {len(all_candidate_paths)} | Skipped: {skipped_due_to_exclusion_count}  | Mode: {mode_msg}")

    # ------------------------------------------------------------------
    # Confirmation step if we are going to write
    # ------------------------------------------------------------------
    if not is_dry_run and not auto_yes:
        reply = input(f"About to modify {len(all_candidate_paths)} files. Continue? [y/N]: ").strip().lower()
        if reply != 'y':
            print('Aborted by user.')
            return

    # Configuration for injector
    config = {
        'backup_options': {'enabled': True, 'directory': str(PROJECT_ROOT / '_ref_bak')},
        'resolve_options': {'enabled': False},
        'file_index_cache_ttl': 0,
        'parser_options': {'python': {}, 'markdown': {}},
    }

    # Choose iterator (progress bar if wanted and available)
    iterator = all_candidate_paths
    if not verbose and tqdm is not None:
        iterator = tqdm(iterator, desc='Injecting', unit='file')

    all_injection_results: list[dict] = []

        # Determine once the name (if any) of the dry-run parameter accepted by inject_reference
    try:
        _sig_params = inspect.signature(inject_reference).parameters
        if 'is_dry_run' in _sig_params:
            _DRY_RUN_KWNAME = 'is_dry_run'
        elif 'dry_run' in _sig_params:
            _DRY_RUN_KWNAME = 'dry_run'
        else:
            _DRY_RUN_KWNAME = None
    except Exception:
        _DRY_RUN_KWNAME = None

    for path in iterator:
        rel_path_obj = path.relative_to(PROJECT_ROOT)
        rel_posix = str(rel_path_obj).replace('\\', '/')
        
        # Load core references from the standard file
        try:
            standard_file_path = PROJECT_ROOT / 'subsystems' / 'AutoCrossRef' / 'CROSSREF_STANDARD.md'
            if not standard_file_path.exists():
                print(f"ERROR: CROSSREF_STANDARD.md not found at {standard_file_path}", file=sys.stderr)
                raise FileNotFoundError(f"CROSSREF_STANDARD.md not found at {standard_file_path}")

            with open(standard_file_path, 'r', encoding='utf-8') as f_standard:
                standard_data = yaml.safe_load(f_standard)
                if not isinstance(standard_data, dict) or 'core_refs' not in standard_data:
                    print(f"ERROR: CROSSREF_STANDARD.md is malformed or missing 'core_refs' key.", file=sys.stderr)
                    raise ValueError("Malformed CROSSREF_STANDARD.md")
                loaded_core_references = standard_data.get('core_refs', [])
                if not isinstance(loaded_core_references, list):
                    print(f"ERROR: 'core_refs' in CROSSREF_STANDARD.md is not a list.", file=sys.stderr)
                    raise ValueError("'core_refs' is not a list")
                # Ensure all paths are strings, just in case
                loaded_core_references = [str(ref) for ref in loaded_core_references]
        except Exception as e_yaml:
            print(f"CRITICAL ERROR: Could not load or parse CROSSREF_STANDARD.md: {e_yaml}", file=sys.stderr)
            print("Aborting operation. Please fix the standard file or ensure it's accessible.", file=sys.stderr)
            # In a real scenario, might re-raise or exit, but for now, let's allow empty to see other errors.
            # For CI, a failure here should definitely stop the process.
            if mode == 'full': # For strict CI mode, this is a fatal error.
                raise
            loaded_core_references = [] # Fallback to empty if not in strict mode, though this is bad.

        # Determine operational parameters based on mode
        dry_run_for_injection = is_dry_run or (mode == 'diagnose')
        # create_backup_for_injection is determined but used by the new inject_reference
        # create_backup_for_injection = not is_dry_run and mode != 'diagnose'

        # Build list of references to add for this specific file (core refs excluding self)
        references_to_ensure_for_file = [core for core in loaded_core_references if core.lower() != rel_posix.lower()]
        
        if verbose:
            print(f"PROCESSING {rel_posix} | Mode: {mode} | Dry Run: {dry_run_for_injection}")
            # print(f"  Core refs to ensure: {references_to_ensure_for_file}")
            # print(f"  All valid core refs (for purge check): {loaded_core_references}")

        file_had_processing_error = False
        file_content_changed_overall = False

        try:
            # Use the enhanced inject_reference function with hierarchical reference standard
            injection_result = None
            try:
                # Call the enhanced inject_reference with all references at once
                injection_result = inject_reference(
                    str(path),                      # file_path we are modifying
                    "",                             # reference_to_inject (not used in standard mode)
                    "",                             # absolute_reference_path (not used in standard mode)
                    config,                         # configuration dictionary
                    dry_run_for_injection,          # is_dry_run based on mode
                    references_to_ensure=references_to_ensure_for_file,  # core refs for this file
                    all_valid_core_refs=loaded_core_references,          # all valid core refs
                    mode=mode                       # operation mode
                )
                
                # Process the result
                if injection_result:
                    all_injection_results.append(injection_result)
                    if injection_result.get('content_changed', False):
                        file_content_changed_overall = True
                    
                    # Check compliance for strict mode
                    if mode == 'full' and not injection_result.get('is_compliant', True):
                        non_compliant_files_count += 1
                        if verbose:
                            missing_refs = injection_result.get('missing_references', [])
                            purged_refs = injection_result.get('references_purged', [])
                            print(f"  STRICT MODE: File {rel_posix} is non-compliant:")
                            if missing_refs:
                                print(f"    - Missing references: {', '.join(missing_refs)}")
                            if purged_refs:
                                print(f"    - Had legacy/self references: {', '.join(purged_refs)}")
            
            except Exception as e_inject:
                error_count += 1
                error_type = type(e_inject).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                print(f"Error processing references for {path}: {e_inject}")
                injection_result = {
                    'file_path': str(path),
                    'status': 'error_inject_ref',
                    'message': f'Error during injection: {e_inject}',
                    'error_type': error_type,
                    'content_changed': False,
                    'is_compliant': False,
                    'references_added': [],
                    'references_purged': [],
                    'missing_references': references_to_ensure_for_file  # Assume all are missing on error
                }
                all_injection_results.append(injection_result)
                file_had_processing_error = True
                
                # Mark as non-compliant in strict mode
                if mode == 'full':
                    non_compliant_files_count += 1
                    if verbose:
                        print(f"  STRICT MODE: File {rel_posix} marked as non-compliant due to processing error.")

        except Exception as e_file_processing: # Catch-all for the whole file's processing block
            error_count += 1
            error_type_file = type(e_file_processing).__name__
            error_types[error_type_file] = error_types.get(error_type_file, 0) + 1
            print(f"CRITICAL Error processing file {path}: {e_file_processing}")
            all_injection_results.append({
                'file_path': str(path),
                'status': 'error_file_processing_critical',
                'message': f'Critical error processing file: {e_file_processing}',
                'error_type': error_type_file,
                'content_changed': False,
            })
            file_had_processing_error = True # Ensure this is set
            if mode == 'full':
                non_compliant_files_count += 1 # File with critical error is non-compliant
                if verbose:
                    print(f"  STRICT MODE: File {rel_posix} marked as non-compliant due to critical processing error.")

    # ------------------------------------------------------------------
    # Generate reports
    # ------------------------------------------------------------------
    
    # Add error summary to output
    if error_count > 0:
        error_summary = f"\nErrors encountered: {error_count} ({', '.join(f'{count} {err_type}' for err_type, count in error_types.items())})"
        print(error_summary)
    else:
        print("No errors encountered during injection process.")

    if mode == 'full':
        print(f"Strict mode validation: {non_compliant_files_count} file(s) marked as non-compliant.")
        # Exit with non-zero status code if any files are non-compliant in strict mode
        if non_compliant_files_count > 0:
            print("\nSTRICT MODE FAILURE: Some files are not compliant with reference standards.")
            print("CI checks should fail. Fix the issues or use a less strict mode.")
            sys.exit(1)  # Exit with error code for CI integration
        
    report_html_content = generate_html_report(
        all_injection_results,
        PROJECT_ROOT,
        EXCLUDE_TOP_LEVEL_DIR_NAMES,
        EXCLUDE_DIR_PATTERNS,
        skipped_due_to_exclusion_count,
        total_scanned_files,
    )

    report_dir = PROJECT_ROOT / 'subsystems' / 'AutoCrossRef' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    report_filename = f"autocrossref_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = report_dir / report_filename
    report_path.write_text(report_html_content, encoding='utf-8')
    print(f"HTML report written to: {report_path}")

    # Optional JSON dump
    if json_out:
        try:
            with open(json_out, 'w', encoding='utf-8') as jf:
                json.dump(all_injection_results, jf, indent=2)
            print(f"JSON report saved to: {json_out}")
        except Exception as e:
            print(f"Failed to write JSON report: {e}")

    if mode == 'full' and non_compliant_files_count > 0:
        print(f"\nSTRICT MODE FAILURE: {non_compliant_files_count} file(s) did not meet compliance standards.")
        return False # Indicate failure for strict mode
    
    return True # Indicate success or non-strict mode completion


# ---------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------

if __name__ == '__main__':
    print("DEBUG: Script execution started.", file=sys.stderr)
    parser = argparse.ArgumentParser(description='Run AutoCrossRef reference injection sweep.')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulate injections without modifying files.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Log each file being processed.')
    parser.add_argument('--paths', nargs='+', default=None, help='One or more glob patterns (relative to project root) to limit the scan.')
    parser.add_argument('--max', type=int, default=None, help='Stop after the first N eligible files.')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt when modifying files.')
    parser.add_argument('--json-out', dest='json_out', default=None, help='Optional path to write a JSON report alongside the HTML report.')
    parser.add_argument('--ext', nargs='+', default=['.py', '.md'],
                      help=('One or more file extensions to process (e.g., .py .md). Specifying multiple extensions requires '
                            'space separation like "--ext .py .md .txt". Default is ".py .md".'))
    parser.add_argument(
        '--mode',
        choices=['diagnose', 'fix-core', 'full'],
        default='fix-core',
        help='Operation mode: '
             'diagnose=scan and report only; '
             'fix-core=remove self/legacy, inject core (default); '
             'full=fix-core + strict validation for CI (fail on non-compliance)'
    )

    cli_args = parser.parse_args()

    overall_status_success = run_and_report(
        is_dry_run=cli_args.dry_run,
        verbose=cli_args.verbose,
        path_globs=cli_args.paths,
        max_candidates=cli_args.max,
        auto_yes=cli_args.yes,
        json_out=cli_args.json_out,
        file_extensions=cli_args.ext, # Pass the new arg
        mode=cli_args.mode, # Pass the mode
    )

    if not overall_status_success:
        print("DEBUG: Script exiting with status 1 due to strict mode failure.", file=sys.stderr)
        sys.exit(1)