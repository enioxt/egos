"""Progress Bar Utilities

Provides progress tracking functionality for long-running documentation processing tasks.
Implements a fallback progress bar when tqdm is not available.

This module supports the Conscious Modularity principle by isolating progress
tracking functionality from core reference management logic.

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

import sys
import time
from typing import Any, Optional, Union

# Try to import tqdm for enhanced progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class SimpleTqdm:
    """A simple progress bar implementation for when tqdm is not available.
    
    This class provides basic progress tracking functionality with a text-based
    progress bar, ETA calculation, and context manager support.
    """
    
    def __init__(self, total: int = 0, desc: str = "", **kwargs: Any) -> None:
        """Initialize the progress bar.
        
        Args:
            total: Total number of items to process.
            desc: Description to display before the progress bar.
            **kwargs: Additional arguments (ignored, for compatibility with tqdm).
        """
        self.total = total
        self.desc = desc
        self.n = 0
        self.start_time = time.time()
        
        # Only display initial progress if we have a meaningful total
        if self.total and self.total > 0:
            self._print_progress()
        else:
            sys.stdout.write(f"\r{self.desc or ''} {self.n} items processed")
            sys.stdout.flush()

    def update(self, n: int = 1) -> None:
        """Update the progress bar by incrementing the counter.
        
        Args:
            n: Number of items to increment by.
        """
        self.n += n
        self._print_progress()

    def _print_progress(self) -> None:
        """Print the current progress to stdout."""
        if self.total and self.total > 0:
            percentage = 100 * (self.n / self.total)
            elapsed = time.time() - self.start_time
            eta = 0
            
            # Calculate ETA if we have meaningful progress
            if self.n > 0 and elapsed > 0 and self.n < self.total:
                eta = elapsed * (self.total - self.n) / self.n
            
            # Create the progress bar visualization
            bar_length = 30
            filled_length = int(bar_length * self.n // self.total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Adjust ETA display based on completion status
            eta_str = f"ETA: {eta:.1f}s" if self.n < self.total else "Done"
            
            # Construct and display the progress line
            output_str = f"\r{self.desc or ''} |{bar}| {self.n}/{self.total} ({percentage:.1f}%) [{eta_str}]"
            sys.stdout.write(output_str)
            sys.stdout.flush()
        else:
            # Simple counter for indeterminate progress
            sys.stdout.write(f"\r{self.desc or ''} {self.n} items processed")
            sys.stdout.flush()

    def __enter__(self) -> "SimpleTqdm":
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit point. Ensures a newline is printed."""
        sys.stdout.write("\n")
        sys.stdout.flush()

    def close(self) -> None:
        """Close the progress bar, ensuring a newline is printed."""
        sys.stdout.write("\n")
        sys.stdout.flush()


def get_progress_bar(total: int, desc: str, **kwargs: Any) -> Union["tqdm", SimpleTqdm]:
    """Get an appropriate progress bar based on availability.
    
    This function returns a tqdm progress bar if available, otherwise falls back
    to the SimpleTqdm implementation.
    
    Args:
        total: Total number of items to process.
        desc: Description to display before the progress bar.
        **kwargs: Additional arguments to pass to the progress bar constructor.
        
    Returns:
        A progress bar instance (either tqdm or SimpleTqdm).
    """
    if TQDM_AVAILABLE:
        return tqdm(total=total, desc=desc, **kwargs)
    else:
        return SimpleTqdm(total=total, desc=desc, **kwargs)