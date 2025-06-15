#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEXUS Search Engine Prototype

This script implements a basic prototype of the NEXUS Search Engine, which leverages
standardized cross-references to provide enhanced search capabilities for EGOS documentation
and code. It demonstrates the core functionality that will be expanded in the full implementation.

References:
- [NEXUS Search Engine Design](../../docs_egos/03_subsystems/NEXUS/search_engine_design.md)
- [EGOS Cross-Reference Standardization](../../docs_egos/05_development/standards/cross_reference_standard.md)
- [NEXUS Subsystem Documentation](../../docs_egos/03_subsystems/NEXUS/README.md)
- [ROADMAP.md - XREF-SEARCH-01](../../ROADMAP.md)

Author: EGOS Development Team
Created: 2025-05-21
Version: 0.1.0 (Prototype)

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
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Any, Optional, Tuple
from collections import defaultdict, Counter

# Third-party imports
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("nexus_search")

# Constants
BANNER_WIDTH = 80
TERMINAL_WIDTH = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 100

# Configuration
CONFIG = {
    "file_extensions": {".md", ".mdc", ".py", ".html", ".txt"},
    "exclude_dirs": {"venv", "__pycache__", ".git", "node_modules"},
    "exclude_patterns": [
        r'.*\.git.*',
        r'.*__pycache__.*',
        r'.*node_modules.*',
        r'.*\.venv.*',
        r'.*backup.*',
    ],
    "max_workers": min(32, (os.cpu_count() or 4) * 2),
    "batch_size": 100,
    "test_mode": False,
    "test_file_limit": 50,
}

# Helper functions
def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Print a visually appealing banner."""
    # Ensure clean output by flushing stdout first
    sys.stdout.flush()
    
    print(f"{Fore.BLUE}╔{'═' * (BANNER_WIDTH-2)}╗{Style.RESET_ALL}")
    
    # Title
    title_padding = (BANNER_WIDTH - 2 - len(title)) // 2
    print(f"{Fore.BLUE}║{' ' * title_padding}{Fore.YELLOW}{title}{' ' * (BANNER_WIDTH - 2 - len(title) - title_padding)}║{Style.RESET_ALL}")
    
    # Subtitle if provided
    if subtitle:
        subtitle_padding = (BANNER_WIDTH - 2 - len(subtitle)) // 2
        print(f"{Fore.BLUE}║{' ' * subtitle_padding}{Fore.CYAN}{subtitle}{' ' * (BANNER_WIDTH - 2 - len(subtitle) - subtitle_padding)}║{Style.RESET_ALL}")
    
    # Bottom border
    print(f"{Fore.BLUE}╚{'═' * (BANNER_WIDTH-2)}╝{Style.RESET_ALL}")
    
    # Ensure banner is fully displayed
    sys.stdout.flush()
    print()

class Document:
    """Represents a document in the EGOS ecosystem."""
    
    def __init__(self, path: Path):
        """Initialize a document.
        
        Args:
            path: Path to the document
        """
        self.path = path
        self.id = str(path.relative_to(Path.cwd()))
        self.title = self._extract_title()
        self.metadata = self._extract_metadata()
        self.references = []
        self.content = self._read_content()
    
    def _read_content(self) -> str:
        """Read document content.
        
        Returns:
            Document content as string
        """
        try:
            with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {self.path}: {str(e)}")
            return ""
    
    def _extract_title(self) -> str:
        """Extract document title.
        
        Returns:
            Document title
        """
        # Default to filename without extension
        title = self.path.stem
        
        try:
            # For Markdown files, try to extract title from frontmatter or first heading
            if self.path.suffix.lower() in ['.md', '.mdc']:
                with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(2000)  # Read first 2000 chars
                    
                    # Check for YAML frontmatter
                    frontmatter_match = re.search(r'---\s+title:\s*([^\n]+)', content)
                    if frontmatter_match:
                        return frontmatter_match.group(1).strip()
                    
                    # Check for first heading
                    heading_match = re.search(r'#\s+([^\n]+)', content)
                    if heading_match:
                        return heading_match.group(1).strip()
            
            # For Python files, try to extract from module docstring
            elif self.path.suffix.lower() == '.py':
                with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(2000)  # Read first 2000 chars
                    
                    # Check for module docstring
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        # Try to get first line of docstring
                        docstring = docstring_match.group(1).strip()
                        first_line = docstring.split('\n')[0].strip()
                        if first_line:
                            return first_line
        
        except Exception as e:
            logger.debug(f"Error extracting title from {self.path}: {str(e)}")
        
        return title
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract document metadata.
        
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'created': None,
            'updated': None,
            'author': None,
            'tags': [],
            'type': self.path.suffix.lower(),
        }
        
        try:
            # Get file stats
            stats = os.stat(self.path)
            metadata['created'] = datetime.fromtimestamp(stats.st_ctime).isoformat()
            metadata['updated'] = datetime.fromtimestamp(stats.st_mtime).isoformat()
            
            # For Markdown files, try to extract metadata from frontmatter
            if self.path.suffix.lower() in ['.md', '.mdc']:
                with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(2000)  # Read first 2000 chars
                    
                    # Check for YAML frontmatter
                    frontmatter_match = re.search(r'---\s+(.*?)\s+---', content, re.DOTALL)
                    if frontmatter_match:
                        frontmatter = frontmatter_match.group(1)
                        
                        # Extract author
                        author_match = re.search(r'author:\s*([^\n]+)', frontmatter)
                        if author_match:
                            metadata['author'] = author_match.group(1).strip()
                        
                        # Extract tags
                        tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
                        if tags_match:
                            tags = tags_match.group(1).split(',')
                            metadata['tags'] = [tag.strip() for tag in tags]
        
        except Exception as e:
            logger.debug(f"Error extracting metadata from {self.path}: {str(e)}")
        
        return metadata

class Reference:
    """Represents a reference between documents."""
    
    def __init__(self, source_id: str, target_id: str, ref_type: str, context: str, position: Tuple[int, int]):
        """Initialize a reference.
        
        Args:
            source_id: Source document ID
            target_id: Target document ID
            ref_type: Reference type
            context: Surrounding text
            position: Position in source document
        """
        self.source_id = source_id
        self.target_id = target_id
        self.ref_type = ref_type
        self.context = context
        self.position = position

class NEXUSSearchEngine:
    """NEXUS Search Engine for EGOS documentation and code."""
    
    def __init__(self, base_path: str, test_mode: bool = False):
        """Initialize the search engine.
        
        Args:
            base_path: Base path to index
            test_mode: If True, only process a limited number of files
        """
        self.base_path = Path(base_path)
        self.test_mode = test_mode
        
        # Document storage
        self.documents = {}
        self.references = []
        
        # Reference patterns
        self.reference_patterns = {
            "standard": re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            "mdc": re.compile(r'\[([^\]]+)\]\(mdc:([^)]+)\)'),
            "html": re.compile(r'<a\s+href=["\']([^"\'\']+)["\'][^>]*>([^<]+)</a>'),
            "cci": re.compile(r'\[([^\]]+)\]\(cci:7://([^)]+)\)'),
        }
        
        # Special reference prefixes to skip validation
        self.special_prefixes = [
            'cci:7://', 
            'mdc:',
            'http://', 
            'https://', 
            'ftp://', 
            'mailto:'
        ]
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "documents_indexed": 0,
            "references_found": 0,
            "processing_time": 0,
        }
    
    def index(self) -> None:
        """Index documents and extract references."""
        logger.info(f"Indexing documents in {self.base_path}...")
        
        # Find files to index
        files = self._find_files()
        
        if self.test_mode:
            logger.info(f"Test mode: limiting to {CONFIG['test_file_limit']} files")
            files = files[:CONFIG['test_file_limit']]
        
        logger.info(f"Found {len(files)} files to index")
        
        # Process files
        for file in tqdm(files, desc="Indexing documents", unit="files"):
            try:
                # Create document
                document = Document(file)
                
                # Store document
                self.documents[document.id] = document
                
                # Extract references
                self._extract_references(document)
                
                # Update statistics
                self.stats["files_processed"] += 1
                self.stats["documents_indexed"] += 1
            
            except Exception as e:
                logger.error(f"Error indexing {file}: {str(e)}")
        
        logger.info(f"Indexed {self.stats['documents_indexed']} documents with {self.stats['references_found']} references")
    
    def _find_files(self) -> List[Path]:
        """Find files to index.
        
        Returns:
            List of file paths
        """
        files = []
        
        # Compile exclude patterns for faster matching
        exclude_patterns = [re.compile(pattern) for pattern in CONFIG["exclude_patterns"]]
        
        # Walk the directory tree
        for root, dirs, filenames in os.walk(self.base_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in CONFIG["exclude_dirs"]]
            
            # Skip paths matching exclude patterns
            if any(pattern.match(root) for pattern in exclude_patterns):
                dirs[:] = []  # Skip all subdirectories
                continue
            
            # Process files
            for filename in filenames:
                file_path = Path(os.path.join(root, filename))
                file_path_str = str(file_path)
                
                # Skip files in excluded patterns
                if any(pattern.match(file_path_str) for pattern in exclude_patterns):
                    continue
                
                # Check if extension is in the list to process
                if file_path.suffix.lower() in CONFIG["file_extensions"]:
                    files.append(file_path)
        
        return files
    
    def _extract_references(self, document: Document) -> None:
        """Extract references from document.
        
        Args:
            document: Document to extract references from
        """
        content = document.content
        
        # Find standard markdown links
        for match in self.reference_patterns["standard"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            
            # Skip external links
            if not any(target.startswith(prefix) for prefix in self.special_prefixes):
                self._add_reference(document.id, target, "standard", text, (match.start(), match.end()))
        
        # Find MDC links
        for match in self.reference_patterns["mdc"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            self._add_reference(document.id, target, "mdc", text, (match.start(), match.end()))
        
        # Find CCI links
        for match in self.reference_patterns["cci"].finditer(content):
            text = match.group(1)
            target = match.group(2)
            self._add_reference(document.id, target, "cci", text, (match.start(), match.end()))
        
        # Find HTML links
        for match in self.reference_patterns["html"].finditer(content):
            target = match.group(1)
            text = match.group(2)
            
            # Skip external links
            if not any(target.startswith(prefix) for prefix in self.special_prefixes):
                self._add_reference(document.id, target, "html", text, (match.start(), match.end()))
    
    def _add_reference(self, source_id: str, target: str, ref_type: str, context: str, position: Tuple[int, int]) -> None:
        """Add a reference.
        
        Args:
            source_id: Source document ID
            target: Target reference
            ref_type: Reference type
            context: Surrounding text
            position: Position in source document
        """
        # Resolve target to document ID
        target_id = self._resolve_target(source_id, target)
        
        if target_id:
            # Create reference
            reference = Reference(source_id, target_id, ref_type, context, position)
            
            # Store reference
            self.references.append(reference)
            
            # Update statistics
            self.stats["references_found"] += 1
    
    def _resolve_target(self, source_id: str, target: str) -> Optional[str]:
        """Resolve target to document ID.
        
        Args:
            source_id: Source document ID
            target: Target reference
            
        Returns:
            Document ID or None if not found
        """
        # Handle special references
        if any(target.startswith(prefix) for prefix in self.special_prefixes):
            return target
        
        # Handle absolute paths
        if os.path.isabs(target):
            target_path = Path(target)
        else:
            # Handle relative paths
            source_path = Path(source_id)
            if source_path.is_absolute():
                source_dir = source_path.parent
            else:
                source_dir = Path.cwd() / source_path.parent
            
            target_path = source_dir / target
        
        # Normalize path
        try:
            target_path = target_path.resolve()
            target_id = str(target_path.relative_to(Path.cwd()))
            
            # Check if target exists in documents
            if target_id in self.documents:
                return target_id
        except Exception:
            pass
        
        return None
    
    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for documents matching query and filters.
        
        Args:
            query: Search query
            filters: Optional filters
            
        Returns:
            List of matching documents
        """
        if not filters:
            filters = {}
        
        logger.info(f"Searching for '{query}' with filters {filters}")
        
        results = []
        
        # Simple keyword search for prototype
        query_terms = query.lower().split()
        
        for doc_id, document in self.documents.items():
            # Check if document matches query
            content = document.content.lower()
            title = document.title.lower()
            
            # Calculate score based on term frequency
            score = 0
            for term in query_terms:
                # Title matches are weighted more heavily
                title_matches = title.count(term)
                content_matches = content.count(term)
                
                score += title_matches * 10 + content_matches
            
            # Apply filters
            if filters:
                # Filter by tags
                if 'tags' in filters and filters['tags']:
                    if not any(tag in document.metadata.get('tags', []) for tag in filters['tags']):
                        continue
                
                # Filter by type
                if 'type' in filters and filters['type']:
                    if document.metadata.get('type') != filters['type']:
                        continue
                
                # Filter by author
                if 'author' in filters and filters['author']:
                    if document.metadata.get('author') != filters['author']:
                        continue
            
            # Add to results if score > 0
            if score > 0:
                results.append({
                    'id': doc_id,
                    'title': document.title,
                    'path': str(document.path),
                    'score': score,
                    'metadata': document.metadata,
                    'snippet': self._generate_snippet(document, query_terms),
                })
        
        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _generate_snippet(self, document: Document, query_terms: List[str]) -> str:
        """Generate a snippet from document content.
        
        Args:
            document: Document to generate snippet from
            query_terms: Query terms
            
        Returns:
            Snippet
        """
        content = document.content
        
        # Find best snippet
        best_snippet = ""
        best_score = 0
        
        # Split content into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        for paragraph in paragraphs:
            # Skip very short paragraphs
            if len(paragraph) < 20:
                continue
            
            # Calculate score based on term frequency
            score = 0
            for term in query_terms:
                score += paragraph.lower().count(term.lower())
            
            # Update best snippet if score is higher
            if score > best_score:
                best_score = score
                best_snippet = paragraph
        
        # If no good snippet found, use first paragraph
        if not best_snippet and paragraphs:
            best_snippet = paragraphs[0]
        
        # Truncate snippet if too long
        if len(best_snippet) > 200:
            best_snippet = best_snippet[:197] + "..."
        
        return best_snippet
    
    def get_related_documents(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get documents related to a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of related documents
        """
        related = []
        
        # Find references to and from this document
        for reference in self.references:
            if reference.source_id == doc_id:
                # Reference from this document to another
                target_id = reference.target_id
                
                # Skip special references
                if any(target_id.startswith(prefix) for prefix in self.special_prefixes):
                    continue
                
                # Get target document
                if target_id in self.documents:
                    related.append({
                        'id': target_id,
                        'title': self.documents[target_id].title,
                        'path': str(self.documents[target_id].path),
                        'relation': 'outgoing',
                        'context': reference.context,
                    })
            
            elif reference.target_id == doc_id:
                # Reference to this document from another
                source_id = reference.source_id
                
                # Get source document
                if source_id in self.documents:
                    related.append({
                        'id': source_id,
                        'title': self.documents[source_id].title,
                        'path': str(self.documents[source_id].path),
                        'relation': 'incoming',
                        'context': reference.context,
                    })
        
        return related
    
    def print_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Print search results.
        
        Args:
            results: Search results
        """
        if not results:
            print(f"{Fore.YELLOW}No results found.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Found {len(results)} results:{Style.RESET_ALL}\n")
        
        for i, result in enumerate(results):
            print(f"{Fore.GREEN}{i+1}. {result['title']}{Style.RESET_ALL}")
            print(f"   {Fore.BLUE}Path:{Style.RESET_ALL} {result['path']}")
            print(f"   {Fore.BLUE}Score:{Style.RESET_ALL} {result['score']}")
            
            # Print tags if available
            if 'tags' in result['metadata'] and result['metadata']['tags']:
                tags = ', '.join(result['metadata']['tags'])
                print(f"   {Fore.BLUE}Tags:{Style.RESET_ALL} {tags}")
            
            # Print snippet
            if result['snippet']:
                print(f"   {Fore.BLUE}Snippet:{Style.RESET_ALL} {result['snippet']}")
            
            print()
    
    def print_document_details(self, doc_id: str) -> None:
        """Print document details.
        
        Args:
            doc_id: Document ID
        """
        if doc_id not in self.documents:
            print(f"{Fore.RED}Document not found: {doc_id}{Style.RESET_ALL}")
            return
        
        document = self.documents[doc_id]
        
        print(f"{Fore.GREEN}Document: {document.title}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Path:{Style.RESET_ALL} {document.path}")
        
        # Print metadata
        print(f"{Fore.BLUE}Metadata:{Style.RESET_ALL}")
        for key, value in document.metadata.items():
            if value:
                print(f"  {key}: {value}")
        
        # Print related documents
        related = self.get_related_documents(doc_id)
        
        if related:
            print(f"\n{Fore.BLUE}Related Documents:{Style.RESET_ALL}")
            
            # Group by relation type
            outgoing = [r for r in related if r['relation'] == 'outgoing']
            incoming = [r for r in related if r['relation'] == 'incoming']
            
            if outgoing:
                print(f"  {Fore.CYAN}Referenced by this document:{Style.RESET_ALL}")
                for r in outgoing:
                    print(f"    - {r['title']} ({r['path']})")
            
            if incoming:
                print(f"  {Fore.CYAN}References to this document:{Style.RESET_ALL}")
                for r in incoming:
                    print(f"    - {r['title']} ({r['path']})")

def interactive_mode(engine: NEXUSSearchEngine) -> None:
    """Run interactive search mode.
    
    Args:
        engine: Search engine
    """
    print_banner("NEXUS Search Engine", "Interactive Mode")
    
    print(f"{Fore.CYAN}Welcome to the NEXUS Search Engine!{Style.RESET_ALL}")
    print(f"This prototype demonstrates basic search functionality.")
    print(f"Type '{Fore.GREEN}help{Style.RESET_ALL}' for a list of commands or '{Fore.GREEN}exit{Style.RESET_ALL}' to quit.\n")
    
    while True:
        try:
            command = input(f"{Fore.GREEN}nexus>{Style.RESET_ALL} ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['exit', 'quit', 'q']:
                print(f"{Fore.YELLOW}Exiting NEXUS Search Engine.{Style.RESET_ALL}")
                break
            
            elif command.lower() in ['help', 'h', '?']:
                print(f"\n{Fore.CYAN}Available commands:{Style.RESET_ALL}")
                print(f"  {Fore.GREEN}search <query>{Style.RESET_ALL} - Search for documents")
                print(f"  {Fore.GREEN}view <result_number>{Style.RESET_ALL} - View details of a search result")
                print(f"  {Fore.GREEN}stats{Style.RESET_ALL} - Show indexing statistics")
                print(f"  {Fore.GREEN}help{Style.RESET_ALL} - Show this help message")
                print(f"  {Fore.GREEN}exit{Style.RESET_ALL} - Exit the search engine\n")
            
            elif command.lower().startswith('search '):
                query = command[7:].strip()
                
                if not query:
                    print(f"{Fore.YELLOW}Please provide a search query.{Style.RESET_ALL}")
                    continue
                
                results = engine.search(query)
                engine.print_search_results(results)
                
                # Store results for view command
                engine.last_results = results
            
            elif command.lower().startswith('view '):
                try:
                    result_number = int(command[5:].strip())
                    
                    if not hasattr(engine, 'last_results') or not engine.last_results:
                        print(f"{Fore.YELLOW}No search results to view. Please search first.{Style.RESET_ALL}")
                        continue
                    
                    if result_number < 1 or result_number > len(engine.last_results):
                        print(f"{Fore.YELLOW}Invalid result number. Please enter a number between 1 and {len(engine.last_results)}.{Style.RESET_ALL}")
                        continue
                    
                    result = engine.last_results[result_number - 1]
                    engine.print_document_details(result['id'])
                
                except ValueError:
                    print(f"{Fore.YELLOW}Invalid result number. Please enter a number.{Style.RESET_ALL}")
            
            elif command.lower() == 'stats':
                print(f"\n{Fore.CYAN}Indexing Statistics:{Style.RESET_ALL}")
                print(f"  Files processed: {engine.stats['files_processed']}")
                print(f"  Documents indexed: {engine.stats['documents_indexed']}")
                print(f"  References found: {engine.stats['references_found']}\n")
            
            else:
                print(f"{Fore.YELLOW}Unknown command. Type 'help' for a list of commands.{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting NEXUS Search Engine.{Style.RESET_ALL}")
            break
        
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

def main() -> None:
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="NEXUS Search Engine Prototype",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Index and search in the current directory
  python search_engine_prototype.py
  
  # Index and search in a specific directory
  python search_engine_prototype.py --base-path /path/to/directory
  
  # Run in test mode (limited number of files)
  python search_engine_prototype.py --test-mode

Part of the EGOS NEXUS Search Engine Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
    )
    
    parser.add_argument("--base-path", type=str, default=os.getcwd(), help="Base path to index")
    parser.add_argument("--test-mode", action="store_true", help="Only process a limited number of files")
    
    args = parser.parse_args()
    
    # Print banner
    mode_str = "Test Mode" if args.test_mode else "Full Mode"
    
    print_banner(
        "NEXUS Search Engine Prototype",
        mode_str
    )
    
    # Create search engine
    engine = NEXUSSearchEngine(args.base_path, args.test_mode)
    
    # Index documents
    engine.index()
    
    # Run interactive mode
    interactive_mode(engine)

if __name__ == "__main__":
    main()