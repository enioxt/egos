---
title: EGOS Script Standards
description: Standardized design patterns and best practices for all EGOS scripts
created: 2025-05-21
updated: 2025-05-21
author: EGOS Development Team
version: 1.0.0
status: Active
tags: [standards, scripts, best-practices, cross-reference]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - scripts/cross_reference/file_reference_checker_ultra.py





  - scripts/cross_reference/integration/script_standards.md

# EGOS Script Standards

**@references: <!-- TO_BE_REPLACED -->, KOIOS documentation standards**

## Overview

This document defines the standardized design patterns and best practices that should be applied to all scripts within the EGOS ecosystem. These standards were derived from analyzing the exemplary implementation of `file_reference_checker_ultra.py` and have been formalized to ensure consistency, performance, and user experience across all EGOS tools.

<!-- crossref_block:start -->
- 🔗 Reference: [file_reference_checker_ultra.py](../file_reference_checker_ultra.py)
- 🔗 <!-- TO_BE_REPLACED --><!-- TO_BE_REPLACED -->
<!-- crossref_block:end -->

## Visual Elements

All EGOS scripts should implement consistent visual elements to enhance user experience and provide clear feedback during execution.

### 1. Banners and Headers

Use colorful banners for script headers and section divisions:

```python
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
```

### 2. Progress Tracking

Implement detailed progress bars with ETA for long-running operations:

```python
class ProgressTracker:
    """Enhanced progress tracking with ETA and visual feedback."""
    
    def __init__(self, total: int, description: str = "Processing", unit: str = "files"):
        self.total = total
        self.description = description
        self.unit = unit
        self.processed = 0
        self.start_time = time.time()
        # Additional initialization...
        
        # Create progress bar
        self.pbar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}{description}{Style.RESET_ALL}",
            unit=unit,
            ncols=TERMINAL_WIDTH - 20,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
```

### 3. Color Coding

Apply consistent color coding for different types of information:

- **Cyan**: Descriptions, labels, and status information
- **Yellow**: Important notices, warnings, and highlights
- **Green**: Success messages and completion notices
- **Red**: Error messages and critical warnings
- **Blue**: Structural elements like borders and dividers

### 4. Unicode Symbols

Use Unicode symbols for enhanced visual communication:

- **✓** or **✅**: Success or completion
- **⚠️**: Warning
- **❌**: Error or failure
- **📊**: Statistics or reports
- **🔄**: Processing or updating
- **🚀**: Next steps or actions
- **⏱️**: Time-related information
- **📁**: File operations

## Performance Considerations

### 1. Batch Processing

Process files in batches to prevent memory issues:

```python
# Process files in batches
batch_size = CONFIG["batch_size"]
num_batches = math.ceil(total_files / batch_size)

for batch_idx in range(num_batches):
    start_idx = batch_idx * batch_size
    end_idx = min(start_idx + batch_size, total_files)
    batch_files = files[start_idx:end_idx]
    
    # Process batch...
```

### 2. Timeout Mechanisms

Implement timeout protection for operations that might hang:

```python
start_time = time.time()
# Check timeout periodically
if time.time() - start_time > CONFIG["timeout"]:
    raise TimeoutError(f"Processing timed out after {CONFIG['timeout']} seconds")
```

### 3. Asynchronous Processing

Use async/await for I/O-bound operations:

```python
async def process_files_async(self, files: List[Path]) -> List[Dict[str, Any]]:
    """Process files asynchronously in batches."""
    # Implementation...
    
    # Allow event loop to process other tasks
    await asyncio.sleep(0.1)
```

### 4. Parallel Execution

Utilize ThreadPoolExecutor for CPU-bound tasks:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
    # Submit all tasks
    future_to_file = {
        executor.submit(self.process_file, file_path): file_path
        for file_path in batch_files
    }
    
    # Process results as they complete
    for future in concurrent.futures.as_completed(future_to_file):
        # Handle results...
```

## Error Handling

### 1. Comprehensive Exception Handling

Implement detailed exception handling with contextual information:

```python
try:
    # Operation that might fail
except SpecificException as e:
    logger.error(f"Specific error occurred: {str(e)}")
    # Handle specific error
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    # General error handling
finally:
    # Cleanup operations
```

### 2. Backup Mechanisms

Create backups before destructive operations:

```python
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
```

### 3. Dry-Run Mode

Support dry-run modes for testing operations without making changes:

```python
if not self.dry_run:
    if self.backup_file(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
```

### 4. User Confirmation

Implement confirmation prompts for destructive operations:

```python
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
```

## Code Structure

### 1. Class-Based Design

Use classes for encapsulation of related functionality:

```python
class ReferencePurger:
    """Enhanced class for purging old reference formats from files."""
    
    def __init__(self, base_path: str, dry_run: bool = True, backup: bool = True):
        # Initialization
    
    def find_files(self) -> List[Path]:
        """Find all files to process with enhanced filtering."""
        # Implementation
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file with timeout protection."""
        # Implementation
```

### 2. Comprehensive Docstrings

Implement detailed docstrings with parameter documentation:

```python
def process_file(self, file_path: Path) -> Dict[str, Any]:
    """Process a single file to purge old references with timeout protection.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        Dictionary containing processing results, including:
        - file: Path to the processed file
        - modified: Whether the file was modified
        - references_purged: Number of references purged
        - patterns: Dictionary mapping pattern names to counts
        - error: Error message if an error occurred, None otherwise
        - processing_time: Time taken to process the file in seconds
    """
```

### 3. Organized Imports

Organize imports logically:

```python
# Standard library imports
import os
import re
import shutil
import logging
import argparse
import json
import sys
import time
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
    # Fallback implementation
```

### 4. Type Hints

Use type hints consistently:

```python
def find_files(self) -> List[Path]:
    """Find all files to process."""
    
def process_file(self, file_path: Path) -> Dict[str, Any]:
    """Process a single file."""
    
def generate_report(self, results: List[Dict[str, Any]]) -> Path:
    """Generate a report of the operation."""
```

## Configuration Management

### 1. Centralized Configuration

Use a centralized configuration system:

```python
# Configuration section - can be moved to a separate YAML file in the future
CONFIG = {
    # Performance settings
    "batch_size": 100,  # Number of files to process in each batch
    "max_workers": 4,   # Maximum number of parallel workers
    "timeout": 30,      # Timeout for processing a single file (seconds)
    
    # Logging settings
    "log_file": os.path.join(os.path.dirname(__file__), 'log_file.log'),
    "log_level": "INFO",
    
    # File processing settings
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "chunk_size": 8192,  # Read files in chunks of this size
    
    # Safety settings
    "max_replacements_per_file": 1000,  # Maximum number of replacements in a single file
}
```

### 2. Command-Line Overrides

Allow command-line overrides of configuration options:

```python
parser.add_argument("--workers", type=int, default=CONFIG["max_workers"], help="Number of worker threads")
parser.add_argument("--batch-size", type=int, default=CONFIG["batch_size"], help="Number of files to process in each batch")
parser.add_argument("--timeout", type=int, default=CONFIG["timeout"], help="Timeout for processing a single file (seconds)")

# Update configuration from command line arguments
CONFIG["max_workers"] = args.workers
CONFIG["batch_size"] = args.batch_size
CONFIG["timeout"] = args.timeout
```

### 3. YAML Configuration Files

Support YAML configuration files for more complex settings:

```python
def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        logger.warning(f"Configuration file {config_path} not found, using defaults")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}
```

## Logging

### 1. Configurable Logging

Configure both console and file logging:

```python
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("script_name")

# Add file handler if configured
if CONFIG["log_file"]:
    file_handler = logging.FileHandler(CONFIG["log_file"])
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
```

### 2. Appropriate Log Levels

Use appropriate log levels for different types of information:

- **DEBUG**: Detailed debugging information
- **INFO**: General information about progress
- **WARNING**: Warning messages that don't prevent execution
- **ERROR**: Error messages that may prevent some functionality
- **CRITICAL**: Critical errors that prevent execution

### 3. Structured Logging

Include contextual information in log messages:

```python
logger.info(f"Processing file: {file_path}")
logger.warning(f"Large file detected: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
logger.error(f"Error processing {file_path}: {str(e)}")
```

## User Experience

### 1. Help Messages

Provide clear help messages and usage examples:

```python
parser = argparse.ArgumentParser(
    description="Purge outdated reference formats from the EGOS codebase.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Examples:
  # Run in dry-run mode (no changes made)
  python purge_old_references.py --dry-run
  
  # Run in actual mode with 8 worker threads
  python purge_old_references.py --workers 8
  
  # Run without creating backups (use with caution)
  python purge_old_references.py --no-backup

Part of the EGOS Cross-Reference Standardization Initiative
✧༺❀༻∞ EGOS ∞༺❀༻✧"""
)
```

### 2. Summary Statistics

Display summary statistics at the end of operations:

```python
# Display summary
logger.info(f"\n{Fore.GREEN}Reference purge completed successfully!{Style.RESET_ALL}")
logger.info(f"  • {Fore.CYAN}Files processed:{Style.RESET_ALL} {purger.stats['files_processed']:,}")
logger.info(f"  • {Fore.CYAN}Files modified:{Style.RESET_ALL} {purger.stats['files_modified']:,}")
logger.info(f"  • {Fore.CYAN}References purged:{Style.RESET_ALL} {purger.stats['references_purged']:,}")
logger.info(f"  • {Fore.CYAN}Errors:{Style.RESET_ALL} {purger.stats['errors']:,}")
logger.info(f"  • {Fore.CYAN}Processing time:{Style.RESET_ALL} {format_time(purger.stats['processing_time'])}")
```

### 3. Rich Reports

Generate comprehensive reports with visual enhancements:

```python
# Title and metadata with EGOS styling
f.write(f"# EGOS Cross-Reference Purge Report ({mode.upper()})\n\n")
f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# Executive summary with enhanced formatting
f.write(f"## 📊 Executive Summary\n\n")
f.write(f"This report presents the results of the purge operation for outdated reference formats.\n\n")
```

### 4. EGOS Signature

Include the EGOS signature in all outputs:

```python
# Add EGOS signature
f.write(f"\n\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n")
```

## Implementation Checklist

When creating or updating scripts in the EGOS ecosystem, ensure they adhere to these standards:

- [ ] Implement visual elements (banners, progress tracking, color coding)
- [ ] Apply performance optimizations (batch processing, timeouts, async/parallel)
- [ ] Include comprehensive error handling (try/except, backups, dry-run)
- [ ] Follow code structure guidelines (classes, docstrings, imports, type hints)
- [ ] Use centralized configuration management
- [ ] Configure appropriate logging
- [ ] Enhance user experience (help, statistics, reports, signature)

## Conclusion

Following these standardized design patterns and best practices ensures that all EGOS scripts provide a consistent, high-quality experience for users while maintaining performance, reliability, and maintainability.

✧༺❀༻∞ EGOS ∞༺❀༻✧