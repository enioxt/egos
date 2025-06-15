# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
import os
import logging
from pathlib import Path
from typing import List, Tuple

# Configure logging
# CRONOS & KOIOS Logging: Using standard logging for now, KoiosLogger can be integrated later.
LOG_FILE_PATH = Path("c:/EGOS/logs/migrations/docs_migration_report.log")
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True) # Ensure log directory exists

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__) # Using __name__ for logger identification

# EGOS Ops: Define root directory clearly
ROOT_DIR = Path("c:/EGOS")
OLD_PATH_SEGMENT = "docs_egos"
NEW_PATH_SEGMENT = "docs"
# KOIOS Documentation: File extensions to check, ensure .ipynb is handled if necessary
FILE_EXTENSIONS: Tuple[str, ...] = ('.md', '.py', '.html', '.yml', '.yaml', '.json', '.ipynb')
# Windsurf Integration: Respect .codeiumignore implicitly by excluding common large/binary/temp dirs
# EGOS File Migration Best Practices: Standard exclusions
EXCLUDE_DIRS_RELATIVE: List[str] = [
    '.git', '.idea', '.vscode', 'venv', '.venv', '__pycache__', 'node_modules',
    'backup', 'backups', 'archive', 'logs', 'temp', '.history', 'dependencies',
    'build', 'dist', 'docs_egos' # Explicitly exclude docs_egos if it somehow reappears
]
# Ensure the script doesn't modify itself or its log file
EXCLUDE_FILES: List[str] = ["migrate_docs_references.py", LOG_FILE_PATH.name]

def is_binary_file(filepath: Path, sample_size: int = 1024) -> bool:
    """
    Heuristically checks if a file is binary by reading a sample
    and looking for null bytes.

    Args:
        filepath (Path): The path to the file.
        sample_size (int): Number of bytes to read for checking.

    Returns:
        bool: True if the file is likely binary, False otherwise.
    """
    try:
        with open(filepath, 'rb') as f:
            sample = f.read(sample_size)
        return b'\x00' in sample
    except IOError:
        logger.warning(f"IOError reading {filepath}, treating as binary.")
        return True # Treat as binary in case of read error

def update_references_in_file(file_path: Path) -> bool:
    """
    Updates references from OLD_PATH_SEGMENT to NEW_PATH_SEGMENT in a single file.

    Args:
        file_path (Path): The path to the file to be processed.

    Returns:
        bool: True if the file was modified, False otherwise.
    """
    if file_path.name in EXCLUDE_FILES:
        logger.info(f"Skipping self or log file: {file_path}")
        return False

    if not file_path.is_file():
        logger.warning(f"Path is not a file, skipping: {file_path}")
        return False

    # Security Practices: Avoid processing potentially harmful or very large binary files
    if is_binary_file(file_path):
        logger.info(f"Skipping binary file: {file_path}")
        return False

    modified = False
    try:
        # Attempt to read with UTF-8, fallback to latin-1 for broader compatibility
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 decoding failed for {file_path}, attempting latin-1.")
            content = file_path.read_text(encoding='latin-1') # Fallback encoding

        if OLD_PATH_SEGMENT in content:
            new_content = content.replace(OLD_PATH_SEGMENT, NEW_PATH_SEGMENT)
            # Attempt to write back with UTF-8, then latin-1 if original was latin-1
            try:
                file_path.write_text(new_content, encoding='utf-8')
            except UnicodeEncodeError: # If original was latin-1 and new content has chars not in latin-1
                logger.warning(f"UTF-8 encoding for writing failed for {file_path}, attempting latin-1.")
                file_path.write_text(new_content, encoding='latin-1')
            
            logger.info(f"Updated references in: {file_path}")
            modified = True
        else:
            # Log files that were checked but had no occurrences for completeness
            logger.debug(f"No references to '{OLD_PATH_SEGMENT}' found in: {file_path}")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}", exc_info=True) # exc_info for traceback
    return modified

def migrate_all_references(root_directory: Path) -> Tuple[int, int]:
    """
    Traverses all files in the root directory and updates references.
    Respects exclusion lists for directories and files.

    Args:
        root_directory (Path): The root directory to start the scan from.

    Returns:
        Tuple[int, int]: Number of files processed and number of files changed.
    """
    logger.info(f"Starting reference migration from '{OLD_PATH_SEGMENT}' to '{NEW_PATH_SEGMENT}' in '{root_directory}'")
    changed_files_count = 0
    processed_files_count = 0
    
    # Resolve absolute paths for exclusion list for robust comparison
    absolute_exclude_dirs = [ (root_directory / d).resolve() for d in EXCLUDE_DIRS_RELATIVE ]

    for dirpath_str, dirnames, filenames in os.walk(root_directory, topdown=True):
        current_dir = Path(dirpath_str)

        # Filter out excluded directories to prevent further traversal
        # RULE-FILE-ACCESS-01: This is a direct traversal, not a terminal search fallback.
        dirnames[:] = [
            d_name for d_name in dirnames
            if (current_dir / d_name).resolve() not in absolute_exclude_dirs
        ]
        
        # Check if the current directory itself is in the exclusion list
        if current_dir.resolve() in absolute_exclude_dirs:
            logger.info(f"Skipping excluded directory: {current_dir}")
            continue

        for filename in filenames:
            file_path = current_dir / filename
            if file_path.suffix.lower() in FILE_EXTENSIONS:
                processed_files_count += 1
                if update_references_in_file(file_path):
                    changed_files_count += 1
            else:
                # Log files that don't match extension for transparency, if needed (can be verbose)
                logger.debug(f"Skipping file due to extension mismatch: {file_path}")
                
    logger.info(f"Migration complete. Processed {processed_files_count} files. Updated {changed_files_count} files.")
    return processed_files_count, changed_files_count

if __name__ == '__main__':
    # Operational Procedures: Register task in ROADMAP.md (done by Cascade/User)
    # CRONOS & KOIOS Logging: Recommend backup (manual step for user before running destructive script)
    logger.info("EGOS Documentation Path Migration Script Initialized.")
    logger.info(f"IMPORTANT: Ensure you have backed up the '{ROOT_DIR}' directory before proceeding if this is a live run.")
    
    # Example of how to run, ideally this would be triggered with care
    # For safety, this script doesn't run automatically when imported.
    # To run: python migrate_docs_references.py
    
    # RULE-OPS-AUTONOMY-01: This script is intended to be run by the user.
    # The main execution block here is for direct invocation.
    
    # Uncomment the line below to run the migration directly from the script.
    # processed, changed = migrate_all_references(ROOT_DIR)
    # logger.info(f"Script finished. Processed: {processed}, Changed: {changed}")
    
    print(f"Script ready. To run the migration, uncomment the execution line in the if __name__ == '__main__': block.")
    print(f"Logging to: {LOG_FILE_PATH}")
    print(f"This script will replace all occurrences of '{OLD_PATH_SEGMENT}' with '{NEW_PATH_SEGMENT}'.")
    print("Please review excluded directories and files before running.")