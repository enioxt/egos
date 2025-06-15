#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EGOS Hierarchical Reference Injection Script

This script implements the standardized cross-reference format across the EGOS ecosystem,
replacing outdated reference formats with a hierarchical, standardized approach.
It analyzes document relationships, generates appropriate EGOS IDs, and injects
standardized reference blocks at appropriate locations.

Part of the EGOS Cross-Reference Standardization Initiative.

References:
- [EGOS Cross-Reference Standardization](../../../docs_egos/05_development/standards/cross_reference_standard.md)
- [KOIOS Documentation Standards](../../../docs_egos/05_development/standards/documentation_standards.md)
- [Optimized Reference Fixer](../cross_reference/optimized_reference_fixer.py)
- [Docs Directory Fixer](../cross_reference/docs_directory_fixer.py)
- [Reference Validator](../cross_reference/reference_validator.py)

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

# Standard library imports
import os
import re
import sys
import time
import json
import shutil
import logging
import argparse
import asyncio
import math
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Pattern, Union, Callable
from collections import defaultdict, Counter

# Third-party imports
import concurrent.futures
from tqdm import tqdm
try:
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

# Constants
BANNER_WIDTH = 80
TERMINAL_WIDTH = 120
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Configuration
CONFIG = {
    # Performance settings
    "batch_size": DEFAULT_BATCH_SIZE,
    "max_workers": DEFAULT_MAX_WORKERS,
    "timeout": DEFAULT_TIMEOUT,
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'logs', 'reference_injection.log'),
    "log_level": "INFO",
    
    # File processing settings
    "max_file_size": DEFAULT_MAX_FILE_SIZE,
    "chunk_size": 8192,  # Read files in chunks of this size
    
    # Safety settings
    "max_replacements_per_file": 1000,  # Maximum number of replacements in a single file
    
    # Reference settings
    "reference_block_start": "<!-- crossref_block:start -->",
    "reference_block_end": "<!-- crossref_block:end -->",
    "reference_line_prefix": "- 🔗 Reference: ",
    "egos_id_prefix": "EGOS-REF-",
}

# Configure logging
os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("reference_injector")

# Add file handler if configured
if CONFIG["log_file"]:
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# Helper functions
def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    width = BANNER_WIDTH
    
    # Top border
    print(f"{Fore.BLUE}╔{'═' * (width-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (width - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (width - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (width - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (width - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (width-2)}╝{Style.RESET_ALL}")
    print()

def format_time(seconds: float) -> str:
    """Format time in a human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

class ProgressTracker:
    """Enhanced progress tracking with ETA and visual feedback."""
    
    def __init__(self, total: int, description: str = "Processing", unit: str = "files"):
        self.total = total
        self.description = description
        self.unit = unit
        self.processed = 0
        self.start_time = time.time()
        
        # Create progress bar
        self.pbar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}{description}{Style.RESET_ALL}",
            unit=unit,
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
    
    def update(self, n: int = 1) -> None:
        """Update progress by n units."""
        self.processed += n
        self.pbar.update(n)
    
    def close(self) -> None:
        """Close the progress bar."""
        self.pbar.close()

class ReferenceInjector:
    """Hierarchical reference injector for standardized EGOS references."""
    
    def __init__(self, base_path: str, dry_run: bool = True, backup: bool = True):
        """Initialize the reference injector.
        
        Args:
            base_path: Base path to process
            dry_run: If True, don't make any changes
            backup: If True, create backups before making changes
        """
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir = Path(os.path.join(
            self.base_path, 
            "docs", 
            "reports", 
            "backups", 
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ))
        
        # Create backup directory if needed
        if backup and not dry_run:
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.info(f"Backup directory created at: {self.backup_dir}")
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "references_injected": 0,
            "references_updated": 0,
            "errors": 0,
            "skipped_files": 0,
            "processing_time": 0,
        }
        
        # Document graph for hierarchical analysis
        self.document_graph = defaultdict(set)
        self.document_metadata = {}
        self.egos_id_registry = {}

    def find_files(self) -> List[Path]:
        """Find all files to process with enhanced filtering."""
        logger.info(f"Finding files to process in {self.base_path}")
        
        # File extensions to process
        extensions = {'.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'}
        
        # Directories to exclude
        exclude_dirs = {
            '.git', 'venv', 'node_modules', '__pycache__', 
            'dist', 'build', 'target', 'bin', 'obj'
        }
        
        files = []
        for root, dirs, filenames in os.walk(self.base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in filenames:
                file_path = Path(os.path.join(root, filename))
                
                # Check if extension is in the list to process
                if file_path.suffix.lower() in extensions:
                    # Skip files that are too large
                    try:
                        if file_path.stat().st_size > CONFIG["max_file_size"]:
                            logger.warning(f"Skipping large file: {file_path} ({file_path.stat().st_size / 1024 / 1024:.2f} MB)")
                            self.stats["skipped_files"] += 1
                            continue
                    except Exception as e:
                        logger.error(f"Error checking file size for {file_path}: {str(e)}")
                        self.stats["errors"] += 1
                        continue
                    
                    files.append(file_path)
        
        logger.info(f"Found {len(files)} files to process")
        return files

    def backup_file(self, file_path: Path) -> bool:
        """Create a backup of the file with enhanced error handling."""
        try:
            # Create relative path structure in backup directory
            rel_path = file_path.relative_to(self.base_path)
            backup_path = self.backup_dir / rel_path
            
            # Create parent directories if they don't exist
            os.makedirs(backup_path.parent, exist_ok=True)
            
            # Copy the file
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            logger.error(f"Error backing up {file_path}: {str(e)}")
            return False

    def analyze_document_relationships(self) -> None:
        """Analyze document relationships to build a hierarchical graph."""
        logger.info("Analyzing document relationships...")
        
        files = self.find_files()
        progress = ProgressTracker(len(files), "Analyzing documents", "files")
        
        for file_path in files:
            try:
                # Extract document metadata and references
                metadata = self.extract_document_metadata(file_path)
                references = self.extract_document_references(file_path)
                
                # Store metadata
                self.document_metadata[str(file_path)] = metadata
                
                # Build document graph
                for ref in references:
                    self.document_graph[str(file_path)].add(ref)
                
                progress.update()
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {str(e)}")
                self.stats["errors"] += 1
                progress.update()
        
        progress.close()
        logger.info(f"Document analysis complete. Found {len(self.document_graph)} documents with relationships.")
    
    def extract_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary containing document metadata
        """
        metadata = {
            "path": str(file_path),
            "title": None,
            "egos_id": None,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "size": file_path.stat().st_size,
            "type": file_path.suffix.lower(),
        }
        
        try:
            # Read the first 50 lines to extract metadata
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [f.readline() for _ in range(50)]
            
            # Extract title from the first heading
            for line in lines:
                # Look for Markdown headings
                if line.startswith('# '):
                    metadata["title"] = line[2:].strip()
                    break
                # Look for YAML frontmatter title
                if line.strip().startswith('title:'):
                    metadata["title"] = line.split(':', 1)[1].strip().strip('"\'')
                    break
            
            # If no title found, use the filename
            if not metadata["title"]:
                metadata["title"] = file_path.stem
            
            # Extract EGOS ID if present
            egos_id_pattern = re.compile(r'EGOS-[A-Z]+-\d+')
            for line in lines:
                match = egos_id_pattern.search(line)
                if match:
                    metadata["egos_id"] = match.group(0)
                    break
        
        except Exception as e:
            logger.warning(f"Error extracting metadata from {file_path}: {str(e)}")
        
        return metadata
    
    def extract_document_references(self, file_path: Path) -> List[str]:
        """Extract references from a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of reference paths
        """
        references = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract Markdown links
            md_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
            for match in md_link_pattern.finditer(content):
                link_text, link_target = match.groups()
                
                # Skip external links
                if link_target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                    continue
                
                # Normalize path
                if not os.path.isabs(link_target):
                    # Convert relative path to absolute
                    abs_path = os.path.normpath(os.path.join(file_path.parent, link_target))
                    references.append(abs_path)
                else:
                    references.append(link_target)
            
            # Extract HTML links
            html_link_pattern = re.compile(r'<a\s+href=["\']([^"\']+)["\']')
            for match in html_link_pattern.finditer(content):
                link_target = match.group(1)
                
                # Skip external links
                if link_target.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                    continue
                
                # Normalize path
                if not os.path.isabs(link_target):
                    # Convert relative path to absolute
                    abs_path = os.path.normpath(os.path.join(file_path.parent, link_target))
                    references.append(abs_path)
                else:
                    references.append(link_target)
        
        except Exception as e:
            logger.warning(f"Error extracting references from {file_path}: {str(e)}")
        
        return references
    
    def generate_egos_id(self, file_path: Path) -> str:
        """Generate a unique EGOS ID for a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            EGOS ID string
        """
        # Check if we already have an ID for this document
        if str(file_path) in self.egos_id_registry:
            return self.egos_id_registry[str(file_path)]
        
        # Check if the document already has an ID in its metadata
        if str(file_path) in self.document_metadata and self.document_metadata[str(file_path)]["egos_id"]:
            self.egos_id_registry[str(file_path)] = self.document_metadata[str(file_path)]["egos_id"]
            return self.document_metadata[str(file_path)]["egos_id"]
        
        # Generate a new ID based on file path and content hash
        try:
            # Use relative path for more readable IDs
            rel_path = file_path.relative_to(self.base_path)
            
            # Determine category based on directory structure
            parts = rel_path.parts
            category = "DOC"
            
            if "subsystems" in parts:
                category = "SYS"
            elif "scripts" in parts:
                category = "SCR"
            elif "docs" in parts:
                category = "DOC"
            elif "tests" in parts:
                category = "TST"
            
            # Generate a unique number based on file path
            import hashlib
            path_hash = hashlib.md5(str(rel_path).encode()).hexdigest()
            unique_number = int(path_hash[:8], 16) % 100000
            
            # Format: EGOS-<CATEGORY>-<NUMBER>
            egos_id = f"{CONFIG['egos_id_prefix']}{category}-{unique_number:05d}"
            
            # Store in registry
            self.egos_id_registry[str(file_path)] = egos_id
            
            return egos_id
        
        except Exception as e:
            logger.error(f"Error generating EGOS ID for {file_path}: {str(e)}")
            # Fallback ID
            return f"{CONFIG['egos_id_prefix']}UNK-{len(self.egos_id_registry):05d}"
    
    def create_reference_block(self, file_path: Path) -> str:
        """Create a standardized reference block for a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Formatted reference block string
        """
        references = []
        
        # Get outgoing references from document graph
        if str(file_path) in self.document_graph:
            outgoing_refs = self.document_graph[str(file_path)]
            
            for ref in outgoing_refs:
                try:
                    ref_path = Path(ref)
                    
                    # Skip if reference doesn't exist
                    if not ref_path.exists():
                        continue
                    
                    # Get or create metadata for reference
                    if ref not in self.document_metadata:
                        self.document_metadata[ref] = self.extract_document_metadata(ref_path)
                    
                    # Get or generate EGOS ID
                    egos_id = self.generate_egos_id(ref_path)
                    
                    # Get title
                    title = self.document_metadata[ref]["title"] or ref_path.stem
                    
                    # Create relative path from current file to reference
                    try:
                        rel_path = os.path.relpath(ref_path, file_path.parent)
                        # Ensure forward slashes for consistency
                        rel_path = rel_path.replace('\\', '/')
                    except ValueError:
                        # Fallback to absolute path if relative path can't be determined
                        rel_path = str(ref_path)
                    
                    # Add reference to list
                    references.append(f"{CONFIG['reference_line_prefix']}[{title}]({rel_path}) - {egos_id}")
                
                except Exception as e:
                    logger.warning(f"Error creating reference for {ref}: {str(e)}")
        
        # Create block if we have references
        if references:
            block = f"{CONFIG['reference_block_start']}\n"
            for ref in references:
                block += f"{ref}\n"
            block += f"{CONFIG['reference_block_end']}"
            return block
        
        return ""
    
    def inject_references(self, file_path: Path) -> Dict[str, Any]:
        """Inject standardized references into a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary containing processing results
        """
        result = {
            "file": str(file_path),
            "modified": False,
            "references_injected": 0,
            "references_updated": 0,
            "error": None,
            "processing_time": 0
        }
        
        start_time = time.time()
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file already has reference blocks
            existing_blocks = re.findall(
                f"{re.escape(CONFIG['reference_block_start'])}.*?{re.escape(CONFIG['reference_block_end'])}", 
                content, 
                re.DOTALL
            )
            
            # Create new reference block
            new_block = self.create_reference_block(file_path)
            
            if new_block:
                if existing_blocks:
                    # Update existing blocks
                    for block in existing_blocks:
                        content = content.replace(block, new_block)
                        result["references_updated"] += 1
                else:
                    # Find appropriate insertion point
                    # Try to insert after YAML frontmatter if present
                    yaml_end = re.search(r'^---\n.*?\n---\n', content, re.DOTALL)
                    if yaml_end:
                        insertion_point = yaml_end.end()
                        content = content[:insertion_point] + "\n" + new_block + "\n\n" + content[insertion_point:]
                    else:
                        # Try to insert after the first heading if present
                        first_heading = re.search(r'^# .*\n', content)
                        if first_heading:
                            insertion_point = first_heading.end()
                            content = content[:insertion_point] + "\n" + new_block + "\n\n" + content[insertion_point:]
                        else:
                            # Insert at the beginning of the file
                            content = new_block + "\n\n" + content
                    
                    result["references_injected"] += 1
            
            # Check if content was modified
            if content != original_content:
                result["modified"] = True
                
                # Write changes if not in dry-run mode
                if not self.dry_run:
                    # Backup file if needed
                    if self.backup:
                        self.backup_file(file_path)
                    
                    # Write changes
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error injecting references into {file_path}: {str(e)}")
        
        # Calculate processing time
        result["processing_time"] = time.time() - start_time
        
        return result
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file with timeout protection.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing processing results
        """
        start_time = time.time()
        
        try:
            # Check if file exists and is readable
            if not file_path.exists() or not os.access(file_path, os.R_OK):
                return {
                    "file": str(file_path),
                    "modified": False,
                    "references_injected": 0,
                    "references_updated": 0,
                    "error": f"File does not exist or is not readable",
                    "processing_time": time.time() - start_time
                }
            
            # Process with timeout protection
            while time.time() - start_time < CONFIG["timeout"]:
                # Inject references
                result = self.inject_references(file_path)
                return result
            
            # If we get here, we've timed out
            return {
                "file": str(file_path),
                "modified": False,
                "references_injected": 0,
                "references_updated": 0,
                "error": f"Processing timed out after {CONFIG['timeout']} seconds",
                "processing_time": time.time() - start_time
            }
        
        except Exception as e:
            return {
                "file": str(file_path),
                "modified": False,
                "references_injected": 0,
                "references_updated": 0,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def process_files_async(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process files asynchronously in batches.
        
        Args:
            files: List of files to process
            
        Returns:
            List of processing results
        """
        results = []
        total_files = len(files)
        
        # Process files in batches
        batch_size = CONFIG["batch_size"]
        num_batches = math.ceil(total_files / batch_size)
        
        progress = ProgressTracker(total_files, "Injecting references", "files")
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_files = files[start_idx:end_idx]
            
            # Process batch in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self.process_file, file_path): file_path
                    for file_path in batch_files
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Update statistics
                        self.stats["files_processed"] += 1
                        if result["modified"]:
                            self.stats["files_modified"] += 1
                        self.stats["references_injected"] += result["references_injected"]
                        self.stats["references_updated"] += result["references_updated"]
                        if result["error"]:
                            self.stats["errors"] += 1
                        
                        # Update progress
                        progress.update()
                    
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        self.stats["errors"] += 1
                        progress.update()
            
            # Allow event loop to process other tasks
            await asyncio.sleep(0.1)
        
        progress.close()
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Path:
        """Generate a comprehensive report of the operation.
        
        Args:
            results: List of processing results
            
        Returns:
            Path to the generated report
        """
        # Determine mode
        mode = "DRY_RUN" if self.dry_run else "ACTUAL"
        
        # Create report directory if it doesn't exist
        report_dir = self.base_path / "docs" / "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"reference_injection_report_{mode.lower()}_{timestamp}.md"
        
        # Filter results
        modified_files = [r for r in results if r["modified"]]
        error_files = [r for r in results if r["error"]]
        
        # Generate Mermaid diagram data
        mermaid_nodes = {}
        mermaid_edges = []
        
        # Limit to top 20 documents for diagram clarity
        top_docs = sorted(
            self.document_graph.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:20]
        
        for doc, refs in top_docs:
            doc_id = f"doc{len(mermaid_nodes)}"
            doc_path = Path(doc)
            doc_name = doc_path.name
            mermaid_nodes[doc] = (doc_id, doc_name)
            
            for ref in refs:
                if ref not in mermaid_nodes and len(mermaid_nodes) < 20:
                    ref_id = f"doc{len(mermaid_nodes)}"
                    ref_path = Path(ref)
                    ref_name = ref_path.name
                    mermaid_nodes[ref] = (ref_id, ref_name)
                
                if ref in mermaid_nodes:
                    mermaid_edges.append((mermaid_nodes[doc][0], mermaid_nodes[ref][0]))
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            # Title and metadata with EGOS styling
            f.write(f"# EGOS Reference Injection Report ({mode})\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Part of:** Cross-Reference Standardization Initiative (Phase 3: Hierarchical Injection)\n\n")
            
            # Executive summary with enhanced formatting
            f.write(f"## 📊 Executive Summary\n\n")
            f.write(f"This report presents the results of the reference injection operation.\n\n")
            f.write(f"- **Mode:** {'🔍 Dry Run (no changes made)' if self.dry_run else '✏️ Actual (changes applied)'}\n")
            f.write(f"- **Files Processed:** {self.stats['files_processed']:,}\n")
            f.write(f"- **Files Modified:** {self.stats['files_modified']:,}\n")
            f.write(f"- **References Injected:** {self.stats['references_injected']:,}\n")
            f.write(f"- **References Updated:** {self.stats['references_updated']:,}\n")
            f.write(f"- **Errors:** {self.stats['errors']:,}\n")
            f.write(f"- **Skipped Files:** {self.stats['skipped_files']:,}\n")
            f.write(f"- **Processing Time:** {format_time(self.stats['processing_time'])}\n\n")
            
            # Document relationship visualization
            if mermaid_nodes:
                f.write(f"## 🔄 Document Relationship Visualization\n\n")
                f.write(f"The following diagram shows the top document relationships in the codebase:\n\n")
                
                # Generate Mermaid diagram
                f.write("```mermaid\ngraph TD\n")
                
                # Add nodes
                for doc_id, doc_name in mermaid_nodes.values():
                    f.write(f"    {doc_id}[\"{doc_name}\"]\n")
                
                # Add edges
                for source, target in mermaid_edges:
                    f.write(f"    {source} --> {target}\n")
                
                f.write("```\n\n")
            
            # Modified files section
            if modified_files:
                f.write(f"## 🔄 Modified Files\n\n")
                f.write(f"The following {len(modified_files):,} files were modified:\n\n")
                
                # Group by directory for better organization
                dir_groups = {}
                for result in modified_files:
                    file_path = Path(result["file"])
                    try:
                        # Check if base_path is part of the file path
                        if str(self.base_path) in str(file_path):
                            parent = str(file_path.parent.relative_to(self.base_path))
                        else:
                            parent = str(file_path.parent)
                        if parent not in dir_groups:
                            dir_groups[parent] = []
                        dir_groups[parent].append(result)
                    except Exception as e:
                        logger.warning(f"Error grouping file {file_path}: {str(e)}")
                        # Use a fallback group
                        if "Other" not in dir_groups:
                            dir_groups["Other"] = []
                        dir_groups["Other"].append(result)
                
                # Display top directories with most changes
                f.write(f"### Top Directories\n\n")
                for parent, results in sorted(dir_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
                    f.write(f"- **{parent}** - {len(results)} files modified\n")
                
                f.write(f"\n### Files with Most References\n\n")
                for result in sorted(modified_files, key=lambda x: x["references_injected"] + x["references_updated"], reverse=True)[:10]:
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    refs = result["references_injected"] + result["references_updated"]
                    f.write(f"- **{rel_path}** - {refs} references {'injected' if result['references_injected'] > 0 else 'updated'}\n")
                
                f.write(f"\n... and {len(modified_files) - 10 if len(modified_files) > 10 else 0} more files.\n\n")
            
            # Errors section
            if error_files:
                f.write(f"## ⚠️ Errors\n\n")
                f.write(f"The following errors were encountered during processing:\n\n")
                
                for result in error_files[:20]:  # Limit to 20 errors to keep report manageable
                    file_path = Path(result["file"])
                    try:
                        rel_path = file_path.relative_to(self.base_path)
                    except ValueError:
                        rel_path = file_path
                    
                    f.write(f"- **{rel_path}**: {result['error']}\n")
                
                if len(error_files) > 20:
                    f.write(f"\n... and {len(error_files) - 20} more errors.\n\n")
            else:
                f.write(f"## ⚠️ Errors\n\n")
                f.write(f"No errors were encountered during processing.\n\n")
            
            # Next steps
            f.write(f"## 🚀 Next Steps\n\n")
            
            if self.dry_run:
                f.write(f"1. **Review this report** to confirm the changes are as expected\n")
                f.write(f"2. **Run the reference injection script in actual mode** to apply the changes:\n\n")
                f.write(f"   ```bash\n   python scripts/cross_reference/inject_standardized_references.py\n   ```\n\n")
            else:
                f.write(f"1. **Verify the changes** made by the reference injection script\n")
                f.write(f"2. **Create a script scanner** to identify scripts not following the standards\n")
                f.write(f"3. **Develop a script template generator** that creates new scripts with all standards pre-applied\n\n")
            
            f.write(f"3. **Proceed to Phase 4** (Automated Compliance Checking)\n\n")
            
            # Add EGOS signature
            f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path
    
    async def run(self) -> Path:
        """Run the reference injector.
        
        Returns:
            Path to the generated report
        """
        start_time = time.time()
        
        # Step 1: Analyze document relationships
        self.analyze_document_relationships()
        
        # Step 2: Find files to process
        files = self.find_files()
        
        # Step 3: Process files
        results = await self.process_files_async(files)
        
        # Step 4: Generate report
        report_path = self.generate_report(results)
        
        # Update statistics
        self.stats["processing_time"] = time.time() - start_time
        
        return report_path

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Inject standardized hierarchical references into EGOS documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Run in dry-run mode (no changes made)
  python inject_standardized_references.py --dry-run
  
  # Run in actual mode with 8 worker threads
  python inject_standardized_references.py --workers 8
  
  # Run without creating backups (use with caution)
  python inject_standardized_references.py --no-backup

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes made)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backups before making changes")
    parser.add_argument("--workers", type=int, default=CONFIG["max_workers"], help="Number of worker threads")
    parser.add_argument("--batch-size", type=int, default=CONFIG["batch_size"], help="Number of files to process in each batch")
    parser.add_argument("--timeout", type=int, default=CONFIG["timeout"], help="Timeout for processing a single file (seconds)")
    parser.add_argument("--base-path", type=str, default=os.getcwd(), help="Base path to process")
    
    args = parser.parse_args()
    
    # Update configuration from command line arguments
    CONFIG["max_workers"] = args.workers
    CONFIG["batch_size"] = args.batch_size
    CONFIG["timeout"] = args.timeout
    
    # Print banner
    print_banner(
        "EGOS Hierarchical Reference Injection",
        f"Mode: {'DRY RUN' if args.dry_run else 'ACTUAL'}"
    )
    
    # Confirm if running in actual mode
    if not args.dry_run:
        print(f"\n{Fore.RED}WARNING: You are about to run in ACTUAL mode, which will modify files.{Style.RESET_ALL}")
        print(f"Backup {'will NOT' if args.no_backup else 'will'} be created.\n")
        
        try:
            confirm = input(f"Type 'yes' to continue or anything else to abort: ")
            if confirm.lower() != "yes":
                logger.info("Operation aborted by user.")
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info("Operation aborted by user.")
            sys.exit(0)
    
    # Create the reference injector
    injector = ReferenceInjector(
        base_path=args.base_path,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    # Run the reference injector using asyncio
    try:
        # Create and run the event loop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        loop = asyncio.get_event_loop()
        report_path = loop.run_until_complete(injector.run())
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running reference injector: {str(e)}")
        sys.exit(1)
    
    # Display summary statistics
    logger.info(f"\n{Fore.GREEN}Reference injection completed successfully!{Style.RESET_ALL}")
    logger.info(f"  • {Fore.CYAN}Files processed:{Style.RESET_ALL} {injector.stats['files_processed']:,}")
    logger.info(f"  • {Fore.CYAN}Files modified:{Style.RESET_ALL} {injector.stats['files_modified']:,}")
    logger.info(f"  • {Fore.CYAN}References injected:{Style.RESET_ALL} {injector.stats['references_injected']:,}")
    logger.info(f"  • {Fore.CYAN}References updated:{Style.RESET_ALL} {injector.stats['references_updated']:,}")
    logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {injector.stats['errors']:,}")
    logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(injector.stats['processing_time'])}")
    logger.info(f"  • {Fore.CYAN}Report:{Style.RESET_ALL} {report_path}")
    
    # Suggest next steps
    print(f"\n{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
    if args.dry_run:
        print(f"1. Review the report at {report_path}")
        print(f"2. Run the script in actual mode to apply changes:")
        print(f"   python scripts/cross_reference/inject_standardized_references.py")
    else:
        print(f"1. Verify the changes in the report at {report_path}")
        print(f"2. Proceed to Phase 4: Automated Compliance Checking")
    
    print(f"\n✧༺❀༻∞ EGOS ∞༺❀༻✧")

if __name__ == "__main__":
    main()