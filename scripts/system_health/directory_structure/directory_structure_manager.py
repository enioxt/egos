# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
import os
import shutil
import logging
from pathlib import Path
from typing import List, Literal, Optional

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DirectoryStructureManager:
    """
    A generic utility class for managing directory structures.

    Provides methods for creating, deleting, listing, and ensuring
    the existence of directories. Adheres to EGOS principles for
    modularity and reusability.
    """

    def __init__(self) -> None:
        """
        Initializes the DirectoryStructureManager.
        This manager is designed to be stateless, with methods operating
        on paths provided as arguments.
        """
        pass

    def create_directory(self, dir_path: Path, parents: bool = True, exist_ok: bool = True) -> bool:
        """
        Creates a directory at the specified path.

        Args:
            dir_path (Path): The path where the directory should be created.
            parents (bool): If True, any missing parent directories will be created.
                            If False and a parent is missing, FileNotFoundError is raised.
            exist_ok (bool): If True, no error is raised if the directory already exists.
                             If False and the directory exists, FileExistsError is raised.

        Returns:
            bool: True if the directory was created or already existed (with exist_ok=True).
                  False if an error occurred during creation (e.g., permission issues).
        
        Raises:
            OSError: If an OS-level error occurs (e.g., permission denied) and is not caught.
        """
        try:
            dir_path.mkdir(parents=parents, exist_ok=exist_ok)
            logger.info(f"Successfully ensured directory exists: {dir_path}")
            return True
        except FileExistsError:
            logger.warning(f"Directory already exists and exist_ok=False: {dir_path}")
            return False
        except PermissionError:
            logger.error(f"Permission denied when trying to create directory: {dir_path}")
            return False
        except OSError as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return False

    def ensure_directory_exists(self, dir_path: Path) -> bool:
        """
        Ensures that a directory exists at the specified path.
        If it doesn't exist, it creates the directory and any necessary parent directories.

        Args:
            dir_path (Path): The path of the directory to ensure.

        Returns:
            bool: True if the directory exists or was successfully created, False otherwise.
        """
        return self.create_directory(dir_path, parents=True, exist_ok=True)

    def delete_directory(self, dir_path: Path, recursive: bool = True, ignore_errors: bool = False, missing_ok: bool = True) -> bool:
        """
        Deletes a directory at the specified path.

        Args:
            dir_path (Path): The path of the directory to delete.
            recursive (bool): If True, deletes the directory and all its contents (like shutil.rmtree).
                              If False, only deletes if the directory is empty (like os.rmdir).
            ignore_errors (bool): If True, errors during deletion will be ignored.
            missing_ok (bool): If True, no error is raised if the directory does not exist.
                               If False and the directory does not exist, FileNotFoundError might be raised
                               (or handled to return False).

        Returns:
            bool: True if the directory was successfully deleted or did not exist (with missing_ok=True).
                  False if an error occurred.
        """
        if not dir_path.exists():
            if missing_ok:
                logger.info(f"Directory not found, but missing_ok=True: {dir_path}")
                return True
            else:
                logger.warning(f"Directory not found for deletion: {dir_path}")
                return False
        
        if not dir_path.is_dir():
            logger.warning(f"Path is not a directory, cannot delete: {dir_path}")
            return False

        try:
            if recursive:
                shutil.rmtree(dir_path, ignore_errors=ignore_errors)
                if dir_path.exists() and not ignore_errors:
                    # This check is important because shutil.rmtree(ignore_errors=True) might hide some failures
                    logger.error(f"Failed to delete directory recursively (it might still exist): {dir_path}")
                    return False
            else:
                os.rmdir(dir_path) # Fails if not empty
            
            logger.info(f"Successfully deleted directory: {dir_path}")
            return True
        except OSError as e:
            logger.error(f"Error deleting directory {dir_path}: {e}")
            if ignore_errors and recursive: # os.rmdir doesn't have ignore_errors, shutil.rmtree does
                return True # Error ignored as requested for rmtree
            return False

    def list_directory_contents(
        self,
        dir_path: Path,
        item_type: Literal["all", "files", "dirs"] = "all",
        recursive: bool = False
    ) -> List[Path]:
        """
        Lists the contents of a directory.

        Args:
            dir_path (Path): The path of the directory to list.
            item_type (Literal["all", "files", "dirs"]): The type of items to list.
                Defaults to "all".
            recursive (bool): If True, lists contents recursively. Defaults to False.

        Returns:
            List[Path]: A list of Path objects for the items found. Returns an empty list
                        if the directory does not exist, is not a directory, or on error.
        """
        if not dir_path.exists():
            logger.warning(f"Directory not found for listing: {dir_path}")
            return []
        if not dir_path.is_dir():
            logger.warning(f"Path is not a directory, cannot list contents: {dir_path}")
            return []

        items: List[Path] = []
        try:
            if recursive:
                iterator = dir_path.rglob("*")
            else:
                iterator = dir_path.glob("*")

            for item in iterator:
                if item_type == "all":
                    items.append(item)
                elif item_type == "files" and item.is_file():
                    items.append(item)
                elif item_type == "dirs" and item.is_dir():
                    items.append(item)
            
            logger.info(f"Listed {len(items)} items in {dir_path} (type: {item_type}, recursive: {recursive})")
            return items
        except PermissionError:
            logger.error(f"Permission denied when trying to list directory contents: {dir_path}")
            return []
        except OSError as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            return []

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    # To run this test, execute the script directly: python directory_structure_manager.py
    # Ensure you have permissions to create/delete in the script's CWD.
    logging.getLogger().setLevel(logging.DEBUG) # More verbose for testing
    manager = DirectoryStructureManager()
    
    test_base_dir = Path("./test_dir_manager_egos") # Using a more specific name
    # Clean up from previous test run if any
    if test_base_dir.exists():
        try:
            shutil.rmtree(test_base_dir)
            logger.debug(f"Cleaned up existing test directory: {test_base_dir}")
        except OSError as e:
            logger.error(f"Error cleaning up previous test directory {test_base_dir}: {e}")
            # Depending on the error, might not be able to proceed with tests

    try:
        test_base_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create base test directory {test_base_dir}: {e}. Aborting tests.")
        exit(1)

    dir1 = test_base_dir / "dir1"
    dir2 = test_base_dir / "dir1" / "subdir1"
    file1_path = dir1 / "file1.txt"
    file2_path = dir2 / "file2.txt"

    logger.info(f"--- Testing DirectoryStructureManager in {test_base_dir.resolve()} ---")

    logger.info(f"\n[Test] ensure_directory_exists for {dir2}")
    if manager.ensure_directory_exists(dir2):
        logger.info(f"Ensure {dir2} succeeded. Exists: {dir2.exists()}")
    else:
        logger.error(f"Ensure {dir2} failed.")

    logger.info(f"\n[Test] Creating test files")
    if dir2.exists():
        try:
            with open(file1_path, "w") as f: f.write("test content for file1")
            with open(file2_path, "w") as f: f.write("test content for file2")
            logger.info(f"Created {file1_path} and {file2_path}")
        except OSError as e:
            logger.error(f"Error creating test files: {e}")
    else:
        logger.error(f"Cannot create test files as {dir2} does not exist.")

    logger.info(f"\n[Test] list_directory_contents for {dir1} (non-recursive, all)")
    contents = manager.list_directory_contents(dir1)
    for item in contents: logger.info(f"  Found: {item.relative_to(test_base_dir)}")

    logger.info(f"\n[Test] list_directory_contents for {dir1} (recursive, files)")
    contents_rec_files = manager.list_directory_contents(dir1, item_type="files", recursive=True)
    for item in contents_rec_files: logger.info(f"  Found file: {item.relative_to(test_base_dir)}")
    
    logger.info(f"\n[Test] list_directory_contents for {dir1} (recursive, dirs)")
    contents_rec_dirs = manager.list_directory_contents(dir1, item_type="dirs", recursive=True)
    for item in contents_rec_dirs: logger.info(f"  Found dir: {item.relative_to(test_base_dir)}")

    logger.info(f"\n[Test] delete_directory for {file2_path} (should fail, it's a file)")
    if not manager.delete_directory(file2_path):
        logger.info(f"Correctly failed to delete file {file2_path} using delete_directory.")
    else:
        logger.error(f"Incorrectly succeeded in deleting file {file2_path} using delete_directory.")

    logger.info(f"\n[Test] delete_directory for {dir2} (non-recursive, dir not empty)")
    if dir2.exists() and not manager.delete_directory(dir2, recursive=False, missing_ok=False):
        logger.info(f"Delete non-recursive {dir2} (not empty) correctly failed. Exists: {dir2.exists()}")
    elif not dir2.exists():
        logger.warning(f"Delete non-recursive {dir2} - directory seems to have been deleted or was already gone.")
    else:
        logger.warning(f"Delete non-recursive {dir2} (not empty) unexpectedly succeeded or other issue. Exists: {dir2.exists()}")

    # Make dir2 empty for non-recursive delete test
    if file2_path.exists():
        try:
            file2_path.unlink()
            logger.info(f"Deleted {file2_path} to make {dir2} empty for non-recursive delete test.")
        except OSError as e:
            logger.error(f"Could not delete {file2_path}: {e}")

    logger.info(f"\n[Test] delete_directory for {dir2} (non-recursive, now empty)")
    if manager.delete_directory(dir2, recursive=False, missing_ok=False):
        logger.info(f"Delete non-recursive {dir2} (empty) succeeded. Exists: {dir2.exists()}")
    else:
        logger.warning(f"Delete non-recursive {dir2} (empty) failed. Exists: {dir2.exists()}")

    # Recreate dir2 and file2 for recursive delete test of dir1
    if not dir2.exists(): manager.ensure_directory_exists(dir2)
    if not file2_path.exists():
        try: 
            with open(file2_path, "w") as f: f.write("test2_recreated")
        except OSError as e: logger.error(f"Could not recreate {file2_path}: {e}")

    logger.info(f"\n[Test] delete_directory for {dir1} (recursive)")
    if manager.delete_directory(dir1, recursive=True):
        logger.info(f"Delete recursive {dir1} succeeded. Exists: {dir1.exists()}")
    else:
        logger.error(f"Delete recursive {dir1} failed. Exists: {dir1.exists()}")

    non_existent_dir = test_base_dir / "non_existent_dir"
    logger.info(f"\n[Test] delete_directory for {non_existent_dir} (missing_ok=True)")
    if manager.delete_directory(non_existent_dir, missing_ok=True):
        logger.info(f"Delete non-existent (missing_ok=True) succeeded.")
    else:
        logger.error(f"Delete non-existent (missing_ok=True) failed.")

    logger.info(f"\n[Test] delete_directory for {non_existent_dir} (missing_ok=False)")
    if not manager.delete_directory(non_existent_dir, missing_ok=False):
        logger.info(f"Delete non-existent (missing_ok=False) correctly returned False.")
    else:
        logger.error(f"Delete non-existent (missing_ok=False) unexpectedly succeeded.")

    dir_exists_ok_false = test_base_dir / "dir_for_exist_ok_false_test"
    manager.ensure_directory_exists(dir_exists_ok_false)
    logger.info(f"\n[Test] create_directory for {dir_exists_ok_false} (exist_ok=False, should return False)")
    if not manager.create_directory(dir_exists_ok_false, exist_ok=False):
         logger.info(f"create_directory with exist_ok=False for existing dir correctly returned False.")
    else:
         logger.error(f"create_directory with exist_ok=False for existing dir unexpectedly returned True.")
    
    logger.info(f"\n--- Cleaning up test directory: {test_base_dir} ---")
    try:
        if test_base_dir.exists():
            shutil.rmtree(test_base_dir)
        logger.info("Test completed and test directory cleaned up.")
    except OSError as e:
        logger.error(f"Error cleaning up test directory {test_base_dir} post-tests: {e}")