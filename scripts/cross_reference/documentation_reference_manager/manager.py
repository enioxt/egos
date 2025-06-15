# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
﻿"""
Reference Manager Module

Core implementation of the Documentation Reference Manager system.
This module provides the CrossReferenceManager class which handles:
- Scanning documentation files
- Extracting existing references
- Analyzing potential connections
- Adding suggested cross-references
- Generating reports

This implements the EGOS principle that 'no file exists in isolation' by creating
a mycelium-like interconnection structure across all documentation files.


@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .checkpoint_utils import load_checkpoint, save_checkpoint
from .progress_utils import get_progress_bar

# Configure module logger
logger = logging.getLogger(__name__)


class CrossReferenceManager:
    """Manager for document cross-references within the EGOS ecosystem.
    
    Analyzes documentation files to identify existing references and
    suggests or adds new references to create a mycelium-like interconnection
    structure.
    
    Attributes:
        base_path: Base path of the EGOS project
        doc_paths: List of documentation file paths
        references: Dictionary mapping files to their references
        referenced_by: Dictionary mapping files to files that reference them
        related_docs: Dictionary mapping files to related documents
        min_references: Minimum number of references per file
        batch_size: Number of files to process in each batch
    """
    
    def __init__(self, base_path: str, min_references: int = 2, batch_size: int = 500):
        """Initialize the CrossReferenceManager.
        
        Args:
            base_path: Base path of the EGOS project
            min_references: Minimum number of references per document
            batch_size: Number of files to process in each batch
        """
        self.base_path = Path(base_path)
        self.doc_paths: List[Path] = []
        self.references: Dict[str, Set[str]] = defaultdict(set)  # file_path -> set of referenced file_paths
        self.referenced_by: Dict[str, Set[str]] = defaultdict(set)  # file_path -> set of file_paths referencing it
        self.related_docs: Dict[str, List[str]] = defaultdict(list)  # file_path -> list of related file_paths
        self.min_references = min_references
        self.batch_size = batch_size
        
        # Ensure base path exists
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")
    
    def scan_documentation(self, extensions: Optional[List[str]] = None, resume: bool = False) -> int:
        """Scan EGOS documentation files.
        
        Args:
            extensions: File extensions to include (default: ['.md'])
            resume: Whether to resume from a checkpoint
            
        Returns:
            Number of documentation files found
        """
        if extensions is None:
            extensions = ['.md']
        
        if resume:
            loaded_paths = load_checkpoint("scan", str(self.base_path))
            if loaded_paths and isinstance(loaded_paths, list):
                self.doc_paths = [Path(p) for p in loaded_paths]
                logger.info(f"Resumed scan: {len(self.doc_paths)} files loaded from checkpoint.")
                return len(self.doc_paths)
        
        self.doc_paths = []
        logger.info(f"Scanning documentation in {self.base_path} with extensions {extensions}...")
        
        for ext in extensions:
            for filepath in self.base_path.rglob(f"*{ext}"):
                if filepath.is_file():
                    self.doc_paths.append(filepath)
        
        logger.info(f"Scan complete: Found {len(self.doc_paths)} documentation files.")
        save_checkpoint("scan", [str(p) for p in self.doc_paths], str(self.base_path))
        return len(self.doc_paths)
    
    def extract_references(self, resume: bool = False) -> Dict[str, Set[str]]:
        """Extract existing references from all documentation files.
        
        Args:
            resume: Whether to resume from a checkpoint
            
        Returns:
            Dictionary mapping files to their references
        """
        if resume:
            refs_checkpoint = load_checkpoint("references", str(self.base_path))
            refs_by_checkpoint = load_checkpoint("referenced_by", str(self.base_path))
            
            if refs_checkpoint and refs_by_checkpoint:
                # Convert lists back to sets
                self.references = defaultdict(set, {k: set(v) for k, v in refs_checkpoint.items()})
                self.referenced_by = defaultdict(set, {k: set(v) for k, v in refs_by_checkpoint.items()})
                logger.info(f"Loaded references for {len(self.references)} files from checkpoint")
                return dict(self.references)
        
        # Clear existing references
        self.references = defaultdict(set)
        self.referenced_by = defaultdict(set)
        
        # Reference patterns to look for
        patterns = [
            r'@references:',  # Reference block marker
            r'\[([^\]]+)\]\((mdc:[^)]+|[^)]+\.md)\)',  # Markdown links [text](mdc:path or path.md)
            r'<!-- TO_BE_REPLACED -->([^,\n]+\.md)',  # Plain text "See also" references
            r'<!-- TO_BE_REPLACED -->([^,\n]+\.md)',  # Plain text "Related" references
        ]
        
        if not self.doc_paths:
            logger.warning("No documents scanned. Please run scan_documentation() first.")
            return {}
        
        progress = get_progress_bar(len(self.doc_paths), "Extracting References")
        
        for doc_path in self.doc_paths:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                str_doc_path = str(doc_path.relative_to(self.base_path).as_posix())
                
                # Process @references block if present
                ref_block_match = re.search(r'@references:(.*?)(@end_references|\Z)', content, re.DOTALL | re.IGNORECASE)
                if ref_block_match:
                    block_content = ref_block_match.group(1)
                    # Extract markdown links from the block
                    for link_match in re.finditer(r'\[([^\]]+)\]\((mdc:[^)]+|[^)]+\.md)\)', block_content):
                        ref_path = link_match.group(2)
                        self._process_reference(str_doc_path, ref_path, doc_path)
                
                # Process regular markdown links
                for link_match in re.finditer(r'\[([^\]]+)\]\((mdc:[^)]+|[^)]+\.md)\)', content):
                    ref_path = link_match.group(2)
                    self._process_reference(str_doc_path, ref_path, doc_path)
                
                # Process "See also" and "Related" references
                for pattern in [r'<!-- TO_BE_REPLACED -->([^,\n]+\.md)', r'<!-- TO_BE_REPLACED -->([^,\n]+\.md)']:
                    for match in re.finditer(pattern, content):
                        ref_path = match.group(1)
                        self._process_reference(str_doc_path, ref_path, doc_path)
                
            except Exception as e:
                logger.error(f"Error processing {doc_path}: {e}")
            
            progress.update(1)
        
        progress.close()
        
        # Save checkpoints
        save_checkpoint("references", {k: list(v) for k, v in self.references.items()}, str(self.base_path))
        save_checkpoint("referenced_by", {k: list(v) for k, v in self.referenced_by.items()}, str(self.base_path))
        
        logger.info(f"Reference extraction complete. Found references in {len(self.references)} files.")
        return dict(self.references)
    
    def _process_reference(self, source_path: str, ref_path: str, source_file_path: Path) -> None:
        """Process a single reference, resolving paths and updating reference maps.
        
        Args:
            source_path: Relative path of the source document
            ref_path: Raw reference path from the document
            source_file_path: Absolute Path object of the source document
        """
        # Handle mdc: protocol
        if ref_path.startswith("mdc:"):
            ref_path = ref_path[4:]  # Remove mdc: prefix
        
        try:
            # Try to resolve path relative to current document's directory
            resolved_ref = (source_file_path.parent / Path(ref_path)).resolve()
            
            if resolved_ref.is_file() and resolved_ref.exists():
                # Convert to relative path for storage
                str_resolved_ref = str(resolved_ref.relative_to(self.base_path).as_posix())
                
                # Update reference maps
                self.references[source_path].add(str_resolved_ref)
                self.referenced_by[str_resolved_ref].add(source_path)
        except Exception as e:
            logger.debug(f"Could not resolve reference '{ref_path}' from '{source_path}': {e}")
    
    def analyze_connections(self, resume: bool = False) -> Dict[str, List[str]]:
        """Analyze connections and identify potential new references.
        
        Args:
            resume: Whether to resume from a checkpoint
            
        Returns:
            Dictionary mapping files to potential related documents
        """
        if resume:
            related_docs = load_checkpoint("related_docs", str(self.base_path))
            if related_docs:
                self.related_docs = defaultdict(list, related_docs)
                logger.info(f"Loaded related documents for {len(self.related_docs)} files from checkpoint")
                return dict(self.related_docs)
        
        # Clear existing related docs
        self.related_docs = defaultdict(list)
        
        # This would implement logic to find related documents based on:
        # - Content similarity
        # - Common references
        # - Directory proximity
        # - Other heuristics
        
        # For now, this is a placeholder implementation that suggests connections
        # based on common references (documents that reference the same files)
        
        logger.info("Analyzing document connections...")
        progress = get_progress_bar(len(self.doc_paths), "Analyzing Connections")
        
        for doc_path in self.doc_paths:
            str_doc_path = str(doc_path.relative_to(self.base_path).as_posix())
            
            # Skip if this document already has sufficient references
            if len(self.references.get(str_doc_path, set())) >= self.min_references:
                progress.update(1)
                continue
            
            # Find documents that reference the same files as this document
            related = set()
            for ref in self.references.get(str_doc_path, set()):
                for other_doc in self.referenced_by.get(ref, set()):
                    if other_doc != str_doc_path:
                        related.add(other_doc)
            
            # Find documents referenced by the same documents that reference this one
            for ref_by in self.referenced_by.get(str_doc_path, set()):
                for other_ref in self.references.get(ref_by, set()):
                    if other_ref != str_doc_path:
                        related.add(other_ref)
            
            # Convert to list and store
            self.related_docs[str_doc_path] = list(related)
            progress.update(1)
        
        progress.close()
        
        # Save checkpoint
        save_checkpoint("related_docs", dict(self.related_docs), str(self.base_path))
        
        logger.info(f"Connection analysis complete. Found potential connections for {len(self.related_docs)} files.")
        return dict(self.related_docs)
    
    def add_references(self, dry_run: bool = True, resume: bool = False) -> List[Tuple[str, List[str]]]:
        """Add suggested references to documentation files.
        
        Args:
            dry_run: If True, only simulate adding references
            resume: Whether to resume from a checkpoint
            
        Returns:
            List of (file_path, added_references) tuples
        """
        if not self.related_docs:
            logger.warning("No related documents analyzed. Please run analyze_connections() first.")
            return []
        
        if resume:
            added_refs = load_checkpoint("added_references", str(self.base_path))
            if added_refs:
                logger.info(f"Loaded added references checkpoint for {len(added_refs)} files")
                # We can't actually resume the addition process since files may have changed
                # But we can use this to skip files that were already processed
        
        results = []
        progress = get_progress_bar(len(self.related_docs), "Adding References")
        
        for doc_path, related in self.related_docs.items():
            # Skip if no related documents or already has sufficient references
            if not related or len(self.references.get(doc_path, set())) >= self.min_references:
                progress.update(1)
                continue
            
            try:
                # Convert relative path to absolute
                abs_doc_path = self.base_path / doc_path
                
                if not abs_doc_path.exists():
                    logger.warning(f"Document {doc_path} not found, skipping")
                    progress.update(1)
                    continue
                
                # Read the document content
                with open(abs_doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if document already has a references section
                has_ref_section = re.search(r'@references:', content, re.IGNORECASE) is not None
                
                # Prepare new references to add
                new_refs = []
                for related_doc in related[:self.min_references]:  # Limit to min_references
                    if related_doc not in self.references.get(doc_path, set()):
                        # Convert to relative path for display
                        rel_path = Path(related_doc)
                        display_name = rel_path.name
                        
                        # Create reference in markdown format
                        new_ref = f"- [{display_name}](mdc:{related_doc}) - Related document"
                        new_refs.append(new_ref)
                
                if not new_refs:
                    progress.update(1)
                    continue
                
                # Prepare the new content
                if has_ref_section:
                    # Add to existing references section
                    new_content = re.sub(
                        r'(@references:.*?)(@end_references|\Z)',
                        r'\1\n' + '\n'.join(new_refs) + r'\n\2',
                        content,
                        flags=re.DOTALL | re.IGNORECASE
                    )
                else:
                    # Create new references section at the end
                    ref_section = "\n\n@references:\n" + "\n".join(new_refs) + "\n@end_references\n"
                    new_content = content + ref_section
                
                # Write changes if not dry run
                if not dry_run:
                    with open(abs_doc_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # Update reference maps
                    for related_doc in related[:self.min_references]:
                        if related_doc not in self.references.get(doc_path, set()):
                            self.references[doc_path].add(related_doc)
                            self.referenced_by[related_doc].add(doc_path)
                
                results.append((doc_path, new_refs))
                logger.info(f"{'Would add' if dry_run else 'Added'} {len(new_refs)} references to {doc_path}")
            
            except Exception as e:
                logger.error(f"Error adding references to {doc_path}: {e}")
            
            progress.update(1)
        
        progress.close()
        
        # Save checkpoint of added references
        if not dry_run:
            save_checkpoint("added_references", results, str(self.base_path))
        
        action = "Would add" if dry_run else "Added"
        logger.info(f"{action} references to {len(results)} files.")
        return results
    
    def generate_report(self, report_path: str) -> None:
        """Generate a report of the cross-reference structure.
        
        Args:
            report_path: Path to save the report.
        """
        # Ensure directory exists
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate orphaned documents (no references in or out)
        orphaned_docs = []
        for doc_path in self.doc_paths:
            str_doc_path = str(doc_path.relative_to(self.base_path).as_posix())
            if (str_doc_path not in self.references or not self.references[str_doc_path]) and \
               (str_doc_path not in self.referenced_by or not self.referenced_by[str_doc_path]):
                orphaned_docs.append(str_doc_path)
        
        # Prepare report data
        report_data = {
            "total_documents": len(self.doc_paths),
            "documents_with_references": len(self.references),
            "documents_referenced_by_others": len(self.referenced_by),
            "orphaned_documents": orphaned_docs,
            "reference_map": {k: list(v) for k, v in self.references.items()},
            "referenced_by_map": {k: list(v) for k, v in self.referenced_by.items()},
            "statistics": {
                "avg_references_per_doc": sum(len(refs) for refs in self.references.values()) / max(1, len(self.references)),
                "max_references": max([len(refs) for refs in self.references.values()]) if self.references else 0,
                "min_references": min([len(refs) for refs in self.references.values()]) if self.references else 0,
                "orphaned_percentage": len(orphaned_docs) / max(1, len(self.doc_paths)) * 100
            }
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            logger.info(f"Cross-reference report generated at {report_path}")
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")