# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
﻿"""
Command Line Interface

Entry point for the Documentation Reference Manager system.
Provides a command-line interface for scanning documentation files,
extracting references, analyzing connections, and adding cross-references.

This module implements the principle of Universal Accessibility by providing
a simple, consistent interface to the cross-reference management functionality.


@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import argparse
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Optional

from .manager import CrossReferenceManager

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_progress_summary(manager: CrossReferenceManager) -> None:
    """Print a summary of the current progress.
    
    Args:
        manager: The CrossReferenceManager instance
    """
    total_files = len(manager.doc_paths) if hasattr(manager, 'doc_paths') and manager.doc_paths else 0
    processed_files = len(manager.references) if hasattr(manager, 'references') else 0
    pending_files = total_files - processed_files if total_files >= processed_files else 0
    
    summary = [
        "\n============ PROGRESS SUMMARY ============",
        f"Total files scanned: {total_files}",
        f"Files processed (references extracted): {processed_files}",
        f"Files pending processing: {pending_files}",
    ]
    
    # Add more details as stages are completed
    if hasattr(manager, 'related_docs') and manager.related_docs:
        summary.append(f"Files with potential new connections analyzed: {len(manager.related_docs)}")
    
    summary.append("======================================\n")
    logger.info('\n'.join(summary))


def handle_interrupt(signum: int, frame: Optional[object], manager: Optional[CrossReferenceManager] = None, base_path: Optional[str] = None) -> None:
    """Handle keyboard interrupt (Ctrl+C) by printing progress and saving checkpoints.
    
    Args:
        signum: Signal number
        frame: Current stack frame
        manager: The CrossReferenceManager instance
        base_path: Base path of the EGOS project
    """
    logger.warning("\nProcess interrupted by user (Ctrl+C).")
    
    if manager and base_path:
        logger.warning("Attempting to save current progress before exiting...")
        
        try:
            from .checkpoint_utils import save_checkpoint
            
            if hasattr(manager, 'doc_paths') and manager.doc_paths:
                save_checkpoint("scan", [str(p) for p in manager.doc_paths], base_path)
                
            if hasattr(manager, 'references') and manager.references:
                save_checkpoint("references", {k: list(v) for k, v in manager.references.items()}, base_path)
                
            if hasattr(manager, 'referenced_by') and manager.referenced_by:
                save_checkpoint("referenced_by", {k: list(v) for k, v in manager.referenced_by.items()}, base_path)
                
            if hasattr(manager, 'related_docs') and manager.related_docs:
                save_checkpoint("related_docs", dict(manager.related_docs), base_path)
                
            logger.info("Progress saved successfully.")
            
        except Exception as e:
            logger.error(f"Could not save checkpoints during interrupt: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Exit gracefully
    sys.exit(130)  # 130 is the conventional exit code for Ctrl+C


def main() -> int:
    """Main entry point for the cross-reference manager.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="Analyze and enhance cross-references in EGOS documentation"
    )
    parser.add_argument(
        "--base-path", "-b", default=".",
        help="Base path of the EGOS project (default: current directory)"
    )
    parser.add_argument(
        "--min-references", "-m", type=int, default=2,
        help="Minimum number of references per document"
    )
    parser.add_argument(
        "--add-references", "-a", action="store_true",
        help="Add suggested references to documents (without this flag, runs in dry-run mode)"
    )
    parser.add_argument(
        "--report", "-r",
        help="Generate a JSON report and save to the specified path"
    )
    parser.add_argument(
        "--extensions", "-e", nargs="+", default=[".md"],
        help="File extensions to include (default: .md)"
    )
    parser.add_argument(
        "--batch-size", "-bs", type=int, default=500,
        help="Number of files to process in each batch"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from last successful checkpoint for each stage"
    )
    parser.add_argument(
        "--stage", choices=["scan", "extract", "analyze", "add", "all"], default="all",
        help="Specific stage to run (default: all stages)"
    )
    parser.add_argument(
        "--filter-dir", "-f", nargs="+",
        help="Only process files in these directories (relative to base-path)"
    )
    parser.add_argument(
        "--notify", action="store_true",
        help="Send notification when complete (future feature)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create reports directory if it doesn't exist
        reports_dir = Path(args.base_path) / "reports" / "documentation"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Create manager instance
        manager = CrossReferenceManager(args.base_path, args.min_references, args.batch_size)
        
        # Setup signal handler for graceful interruption
        signal.signal(signal.SIGINT, lambda s, f: handle_interrupt(s, f, manager, args.base_path))
        
        # Determine which stages to run
        run_scan = args.stage in ["scan", "all"]
        run_extract = args.stage in ["extract", "all"]
        run_analyze = args.stage in ["analyze", "all"]
        run_add = args.stage in ["add", "all"] or args.add_references
        
        # Scan documentation
        if run_scan:
            logger.info("--- Starting Scan Stage ---")
            manager.scan_documentation(args.extensions, args.resume)
            print_progress_summary(manager)
        elif args.resume and (run_extract or run_analyze or run_add):
            # If resuming and not running scan, still try to load doc_paths for subsequent stages
            from .checkpoint_utils import load_checkpoint
            
            loaded_paths = load_checkpoint("scan", args.base_path)
            if loaded_paths and isinstance(loaded_paths, list):
                manager.doc_paths = [Path(p) for p in loaded_paths]
                logger.info(f"Resumed: {len(manager.doc_paths)} document paths loaded from scan checkpoint.")
            else:
                logger.error("Resume requested but no scan checkpoint found. Please run the scan stage first.")
                return 1
        
        # Filter by directory if specified
        if args.filter_dir and manager.doc_paths:
            original_count = len(manager.doc_paths)
            filtered_paths = []
            
            for doc_path in manager.doc_paths:
                str_doc_path = str(doc_path.relative_to(manager.base_path).as_posix())
                if any(str_doc_path.startswith(dir_path) for dir_path in args.filter_dir):
                    filtered_paths.append(doc_path)
            
            manager.doc_paths = filtered_paths
            logger.info(f"Filtered to {len(manager.doc_paths)} files in specified directories (from {original_count})")
        
        # Extract references
        if run_extract:
            logger.info("--- Starting Extract Stage ---")
            manager.extract_references(args.resume)
            print_progress_summary(manager)
        elif args.resume and (run_analyze or run_add):
            # If resuming and not running extract, still try to load references for subsequent stages
            from .checkpoint_utils import load_checkpoint
            
            refs_checkpoint = load_checkpoint("references", args.base_path)
            refs_by_checkpoint = load_checkpoint("referenced_by", args.base_path)
            
            if refs_checkpoint and refs_by_checkpoint:
                # Convert lists back to sets
                manager.references = {k: set(v) for k, v in refs_checkpoint.items()}
                manager.referenced_by = {k: set(v) for k, v in refs_by_checkpoint.items()}
                logger.info(f"Resumed: references loaded from checkpoint for {len(manager.references)} files.")
            else:
                logger.error("Resume requested but no references checkpoint found. Please run the extract stage first.")
                return 1
        
        # Analyze connections
        if run_analyze:
            logger.info("--- Starting Analysis Stage ---")
            manager.analyze_connections(args.resume)
            print_progress_summary(manager)
        elif args.resume and run_add:
            # If resuming and not running analyze, still try to load related_docs for add stage
            from .checkpoint_utils import load_checkpoint
            
            related_docs = load_checkpoint("related_docs", args.base_path)
            if related_docs:
                manager.related_docs = related_docs
                logger.info(f"Resumed: related documents loaded from checkpoint for {len(manager.related_docs)} files.")
            else:
                logger.warning("Resume requested but no related_docs checkpoint found. Running analyze stage...")
                manager.analyze_connections(False)
        
        # Add references
        if run_add:
            logger.info("--- Starting Add References Stage ---")
            results = manager.add_references(dry_run=not args.add_references, resume=args.resume)
            
            # Print details about added references
            action = "Added" if args.add_references else "Would add"
            for file_path, added_refs in results:
                if added_refs:
                    logger.info(f"{action} {len(added_refs)} references to {file_path}")
            
            print_progress_summary(manager)
        
        # Generate report if requested
        if args.report:
            logger.info("--- Generating Report ---")
            manager.generate_report(args.report)
            logger.info(f"Report generated at {args.report}")
        
        # Print final summary
        logger.info("Processing complete. Final summary:")
        print_progress_summary(manager)
        
        # Placeholder for future notification feature
        if args.notify:
            logger.info("Notification feature will be implemented in a future version.")
        
        return 0
        
    except KeyboardInterrupt:
        # This shouldn't be reached as the signal handler should catch it,
        # but just in case for environments where signals don't work correctly
        handle_interrupt(None, None, manager, args.base_path)
        return 130
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Try to save checkpoints before exiting
        if 'manager' in locals() and 'args' in locals():
            logger.error("Attempting to save checkpoints before exiting...")
            try:
                handle_interrupt(None, None, manager, args.base_path)
            except Exception as checkpoint_error:
                logger.error(f"Failed to save checkpoints: {str(checkpoint_error)}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())