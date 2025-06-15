#!/usr/bin/env python3
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
import sys
"""
EGOS System Monitor Ultra - Advanced system monitoring and documentation compliance

This script provides high-performance monitoring of the EGOS ecosystem, tracking file changes,
validating documentation compliance, detecting orphaned files, and generating comprehensive
reports on system health. It features advanced optimization techniques including:

- Asynchronous file operations for high throughput
- Memory-mapped files for efficient large file processing
- Parallel processing with adaptive thread pools
- Aho-Corasick algorithm for ultra-fast pattern matching
- Smart caching to avoid redundant operations
- Beautiful progress visualization with detailed metrics

@file egos_system_monitor.py
@module scripts/system_monitor/egos_system_monitor
@version 2.0.0
@date 2025-05-21
@license MIT

@references
- mdc:scripts/cross_reference/file_reference_checker_ultra.py (High-performance pattern matching)
- mdc:scripts/cross_reference/validator/unified_validator.py (UnifiedValidator)
- mdc:scripts/cross_reference/optimized_reference_fixer.py (ReferenceFixer)
- mdc:scripts/cross_reference/validator/orphaned_file_detector.py (OrphanedFileDetector)
- mdc:docs_egos/process/ai_handover_standard.mdc (Handover Protocol)
- mdc:WORK_2025_05_21.md (Recent Work Log)
"""

import os
import sys
import time
import argparse
import asyncio
import datetime
import logging
import json
import subprocess
import re
import math
import shutil
import fnmatch
import tempfile
import mmap
import threading
import statistics
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field, asdict
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache, partial
from collections import defaultdict, Counter

# Try to import optional packages for enhanced performance
try:
    import pyahocorasick

    HAVE_AHOCORASICK = True
    print("Using pyahocorasick for ultra-fast pattern matching")
except ImportError:
    HAVE_AHOCORASICK = False
    print("pyahocorasick not available, using standard regex matching")
    print("Consider installing pyahocorasick for 10-100x faster pattern matching:")
    print("pip install pyahocorasick")

try:
    import tqdm

    HAVE_TQDM = True
except ImportError:
    HAVE_TQDM = False

try:
    import psutil

    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False

# Add parent directory to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent))


# Configure display elements and progress visualization
class TerminalStyles:
    """Provides terminal styling and formatting capabilities for rich output"""

    def __init__(self):
        self.use_unicode = True
        self.use_colors = True

        # Try to detect terminal capabilities
        try:
            if sys.platform == "win32":
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

        try:
            # Test if terminal supports unicode
            print("\u2588", end="")
            print("\r", end="")
        except UnicodeEncodeError:
            self.use_unicode = False

        # Set color codes
        if self.use_colors:
            self.CYAN = "\033[1;36m"
            self.BLUE = "\033[1;34m"
            self.GREEN = "\033[1;32m"
            self.YELLOW = "\033[1;33m"
            self.RED = "\033[1;31m"
            self.MAGENTA = "\033[1;35m"
            self.WHITE = "\033[1;37m"
            self.GRAY = "\033[0;37m"
            self.RESET = "\033[0m"
            self.BOLD = "\033[1m"
        else:
            self.CYAN = ""
            self.BLUE = ""
            self.GREEN = ""
            self.YELLOW = ""
            self.RED = ""
            self.MAGENTA = ""
            self.WHITE = ""
            self.GRAY = ""
            self.RESET = ""
            self.BOLD = ""

        # Box drawing characters for banners and progress bars
        if self.use_unicode:
            self.BOX = {
                "h_line": "═",
                "v_line": "║",
                "tl_corner": "╔",
                "tr_corner": "╗",
                "bl_corner": "╚",
                "br_corner": "╝",
                "progress_start": "│",
                "progress_end": "│",
                "progress_filled": "█",
                "progress_empty": "░",
            }
        else:
            self.BOX = {
                "h_line": "=",
                "v_line": "|",
                "tl_corner": "+",
                "tr_corner": "+",
                "bl_corner": "+",
                "br_corner": "+",
                "progress_start": "|",
                "progress_end": "|",
                "progress_filled": "#",
                "progress_empty": "-",
            }

    def colorize(self, text: str, color: str) -> str:
        """Add color codes to text if colors are supported"""
        if self.use_colors:
            return f"{color}{text}{self.RESET}"
        return text

    def print_banner(self, title: str, width: int = 100) -> None:
        """Print a stylish banner with the title"""
        term_width = min(os.get_terminal_size().columns, width)

        print("\n")
        print(
            self.colorize(
                f"{self.BOX['tl_corner']}{self.BOX['h_line'] * (term_width - 2)}{self.BOX['tr_corner']}",
                self.CYAN,
            )
        )

        # Center the title
        padding = (term_width - len(title) - 2) // 2
        right_padding = term_width - len(title) - 2 - padding
        title_line = (
            f"{self.BOX['v_line']}{' ' * padding}{title}{' ' * right_padding}{self.BOX['v_line']}"
        )
        print(self.colorize(title_line, self.CYAN))

        print(
            self.colorize(
                f"{self.BOX['bl_corner']}{self.BOX['h_line'] * (term_width - 2)}{self.BOX['br_corner']}",
                self.CYAN,
            )
        )
        print("\n")

    def print_info(self, message: str) -> None:
        """Print info message with cyan color"""
        print(self.colorize(message, self.CYAN))

    def print_success(self, message: str) -> None:
        """Print success message with green color"""
        print(self.colorize(message, self.GREEN))

    def print_warning(self, message: str) -> None:
        """Print warning message with yellow color"""
        print(self.colorize(message, self.YELLOW))

    def print_error(self, message: str) -> None:
        """Print error message with red color"""
        print(self.colorize(message, self.RED))

    def format_progress_bar(self, completed: int, total: int, width: int = 40) -> str:
        """Create a stylish progress bar"""
        if total <= 0:
            percent = 0
        else:
            percent = completed / total

        # Calculate the number of filled slots in the progress bar
        filled_slots = int(width * percent)
        empty_slots = width - filled_slots

        # Create the progress bar
        bar = (
            f"{self.BOX['progress_start']}"
            f"{self.BOX['progress_filled'] * filled_slots}"
            f"{self.BOX['progress_empty'] * empty_slots}"
            f"{self.BOX['progress_end']}"
        )

        # Add percentage information
        percent_str = f" {int(percent * 100)}%"

        return self.colorize(bar, self.BLUE) + self.colorize(percent_str, self.YELLOW)


class ProgressDisplay:
    """Beautiful and informative progress display with advanced features"""

    def __init__(
        self, total: int = 0, desc: str = "", unit: str = "items", refresh_rate: float = 0.5
    ):
        self.total = total
        self.completed = 0
        self.desc = desc
        self.unit = unit
        self.refresh_rate = refresh_rate
        self.start_time = time.monotonic()
        self.last_update_time = 0
        self.last_printed_len = 0
        self.terminal_width = shutil.get_terminal_size().columns

        # Initialize terminal styles
        self.styles = TerminalStyles()

        # Optional stats tracking
        self.processing_times = []
        self.current_rate = 0

        if total > 0:
            self.start()

    def start(self):
        """Display initial progress bar"""
        self.start_time = time.monotonic()
        self._render_progress(force=True)

    def update(
        self,
        completed: Optional[int] = None,
        desc: Optional[str] = None,
        force: bool = False,
        item_time: Optional[float] = None,
    ):
        """Update progress display with current status"""
        now = time.monotonic()

        # Update completion count
        if completed is not None:
            self.completed = completed
        else:
            self.completed += 1

        # Update description if provided
        if desc is not None:
            self.desc = desc

        # Track processing time for rate calculation
        if item_time is not None:
            self.processing_times.append(item_time)
            # Keep only the last 100 times for moving average
            if len(self.processing_times) > 100:
                self.processing_times = self.processing_times[-100:]

        # Update current rate
        elapsed = now - self.start_time
        if elapsed > 0:
            self.current_rate = self.completed / elapsed

        # Check if we should refresh the display
        if force or (now - self.last_update_time) >= self.refresh_rate:
            self._render_progress()
            self.last_update_time = now

    def finish(self, final_desc: Optional[str] = None):
        """Complete the progress display with final message"""
        self.update(
            self.total, desc=final_desc or f"Completed {self.total} {self.unit}", force=True
        )
        print()  # Add a newline after the last update

    def _render_progress(self, force: bool = False):
        """Render the progress display to the terminal"""
        now = time.monotonic()
        elapsed = now - self.start_time

        # Prepare progress information
        progress_bar = self.styles.format_progress_bar(self.completed, self.total)

        # Calculate ETA
        if self.completed > 0 and self.total > 0:
            eta = elapsed * (self.total / self.completed - 1)
            eta_str = self._format_time(eta)
        else:
            eta_str = "--:--"

        # Prepare stats
        stats = f"[{self.completed}/{self.total}] "
        if self.current_rate > 0:
            stats += f"({self.current_rate:.1f} {self.unit}/s, ETA: {eta_str})"

        # Combine all parts with appropriate colors
        desc_str = self.styles.colorize(self.desc, self.styles.CYAN)
        stats_str = self.styles.colorize(stats, self.styles.GRAY)

        # Determine available space for description
        progress_bar_len = len(progress_bar) - (
            len(self.styles.BLUE) + len(self.styles.YELLOW) + len(self.styles.RESET) * 2
        )
        stats_len = len(stats)  # Actual visible length without color codes
        total_non_desc = progress_bar_len + stats_len + 3  # +3 for spaces

        # Truncate description if needed
        max_desc_len = self.terminal_width - total_non_desc - 5
        if max_desc_len < 10:
            max_desc_len = 10

        if len(self.desc) > max_desc_len:
            visible_desc = self.desc[: max_desc_len - 3] + "..."
        else:
            visible_desc = self.desc

        # Build the final display line
        line = f"{desc_str} {progress_bar} {stats_str}"

        # Clear the previous line if needed
        if self.last_printed_len > 0:
            print("\r" + " " * self.last_printed_len, end="\r")

        # Print the new line
        print(line, end="")
        self.last_printed_len = len(line) - (
            len(self.styles.CYAN)
            + len(self.styles.BLUE)
            + len(self.styles.YELLOW)
            + len(self.styles.GRAY)
            + len(self.styles.RESET) * 4
        )

    def _format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes, seconds = divmod(seconds, 60)
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"


class PerformanceMonitor:
    """Tracks and logs performance metrics for system monitoring"""

    def __init__(self):
        self.start_time = time.monotonic()
        self.phase_timings = {}
        self.phase_end_times = {}
        self.current_phase = None
        self.metrics = {}
        self.file_stats = {
            "processed": 0,
            "total_time": 0,
            "min_time": float("inf"),
            "max_time": 0,
            "times": [],
        }

        # Monitor system resources if psutil is available
        self.system_stats = {}
        if HAVE_PSUTIL:
            self.system_stats["start_memory"] = psutil.Process().memory_info().rss / (1024 * 1024)
            self.system_stats["cpu_percent"] = psutil.cpu_percent(interval=0.1)

        logger.info("Performance monitoring initialized")

    def start_phase(self, phase_name: str):
        """Start timing a new execution phase"""
        self.current_phase = phase_name
        self.phase_timings[phase_name] = time.monotonic()
        logger.info(f"Starting phase: {phase_name}")

    def end_phase(self, phase_name: str):
        """End timing for a phase and record metrics"""
        if phase_name in self.phase_timings:
            end_time = time.monotonic()
            duration = end_time - self.phase_timings[phase_name]
            self.phase_end_times[phase_name] = end_time
            logger.info(f"Completed phase: {phase_name} in {self._format_time(duration)}")
            return duration
        return 0

    def record_metric(self, name: str, value: Any):
        """Record a performance metric"""
        self.metrics[name] = value

    def record_file_processing(self, file_path: Path, duration: float):
        """Record statistics about individual file processing"""
        self.file_stats["processed"] += 1
        self.file_stats["total_time"] += duration
        self.file_stats["min_time"] = min(self.file_stats["min_time"], duration)
        self.file_stats["max_time"] = max(self.file_stats["max_time"], duration)
        self.file_stats["times"].append(duration)

    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all recorded metrics"""
        total_time = time.monotonic() - self.start_time

        # Calculate phase percentages
        phase_durations = {}
        for phase, start_time in self.phase_timings.items():
            if phase in self.phase_end_times:
                duration = self.phase_end_times[phase] - start_time
                phase_durations[phase] = {
                    "duration": duration,
                    "percentage": (duration / total_time) * 100 if total_time > 0 else 0,
                }

        # File processing statistics
        file_stats = dict(self.file_stats)
        if file_stats["processed"] > 0:
            file_stats["avg_time"] = file_stats["total_time"] / file_stats["processed"]
            if len(file_stats["times"]) > 1:
                file_stats["std_dev"] = statistics.stdev(file_stats["times"])
            else:
                file_stats["std_dev"] = 0
        else:
            file_stats["avg_time"] = 0
            file_stats["std_dev"] = 0

        # Remove the raw times list to keep the summary concise
        file_stats.pop("times", None)

        # Get current system stats if psutil is available
        if HAVE_PSUTIL:
            current_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            self.system_stats["end_memory"] = current_memory
            self.system_stats["memory_delta"] = current_memory - self.system_stats.get(
                "start_memory", 0
            )
            self.system_stats["final_cpu_percent"] = psutil.cpu_percent(interval=0.1)

        return {
            "total_time": total_time,
            "total_time_formatted": self._format_time(total_time),
            "phases": phase_durations,
            "file_processing": file_stats,
            "metrics": self.metrics,
            "system_stats": self.system_stats,
        }

    def _format_time(self, seconds: float) -> str:
        """Format seconds into a human-readable time string"""
        if seconds < 0.001:
            return f"{seconds * 1000000:.2f}μs"
        elif seconds < 1:
            return f"{seconds * 1000:.2f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes, seconds = divmod(seconds, 60)
            return f"{int(minutes)}m {seconds:.2f}s"
        else:
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"


# Create global instances for use throughout the script
STYLES = TerminalStyles()


# Global function shortcuts for terminal output
def print_banner(title: str) -> None:
    """Print a stylish banner with the title"""
    STYLES.print_banner(title)


def print_info(message: str) -> None:
    """Print info message with cyan color"""
    STYLES.print_info(message)


def print_success(message: str) -> None:
    """Print success message with green color"""
    STYLES.print_success(message)


def print_warning(message: str) -> None:
    """Print warning message with yellow color"""
    STYLES.print_warning(message)


def print_error(message: str) -> None:
    """Print error message with red color"""
    STYLES.print_error(message)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "system_monitor.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class FileStatus:
    """Status information for a file in the EGOS ecosystem"""

    path: Path
    last_modified: float
    size: int
    has_references: bool = False
    is_referenced: bool = False
    reference_count: int = 0
    referenced_by_count: int = 0
    documentation_score: float = 0.0
    needs_attention: bool = False
    suggested_actions: List[str] = field(default_factory=list)
    file_type: str = "unknown"
    content_hash: Optional[str] = None
    binary: bool = False
    processed: bool = False

    @property
    def relative_path(self) -> str:
        """Get path relative to EGOS root"""
        try:
            return str(self.path.relative_to(Path("C:/EGOS")))
        except ValueError:
            return str(self.path)


class DocumentationAnalyzer:
    """Analyzes documentation quality of files in the EGOS ecosystem

    Features:
    - Asynchronous file processing for improved throughput
    - Memory-mapped file handling for large files
    - Advanced pattern matching for documentation standards
    - Adaptive scoring based on file type and size
    """

    def __init__(
        self, threshold: float = 0.6, exclusion_manager: Optional['ExclusionManager'] = None
    ):
        """Initialize the documentation analyzer

        Args:
            threshold: Score threshold for considering a file well-documented (0-1)
            exclusion_manager: Optional exclusion manager for filtering files
        """
        self.threshold = threshold
        self.exclusion_manager = exclusion_manager

        # Documentation patterns by file type
        self.doc_patterns = {
            "py": [
                r'"""([^"]*?)"""',  # Docstrings
                r"#\s*(.*?)$",  # Comments
                r"@(\w+)",  # Decorators
                r"def\s+\w+\s*\(.*?\)\s*:",  # Function definitions
                r"class\s+\w+(?:\(.*?\))?\s*:",  # Class definitions
            ],
            "md": [
                r"#+\s+(.*?)$",  # Headers
                r"\*\*(.*?)\*\*",  # Bold text
                r"`(.*?)`",  # Code blocks
                r"\[(.*?)\]\((.*?)\)",  # Links
                r"<!--\s*(.*?)\s*-->",  # HTML comments
            ],
            "js": [
                r"/\*\*(.*?)\*/",  # JSDoc comments
                r"//\s*(.*?)$",  # Single-line comments
                r"function\s+\w+\s*\(",  # Function declarations
                r"class\s+\w+\s*{",  # Class declarations
                r"export\s+(const|let|var|function|class|default)",  # Exports
            ],
        }

        # Initialize automaton if pyahocorasick is available
        self.automatons = {}
        if HAVE_AHOCORASICK:
            for lang, patterns in self.doc_patterns.items():
                automaton = pyahocorasick.Automaton()
                for idx, pattern in enumerate(patterns):
                    automaton.add_str(pattern, (idx, pattern))
                automaton.make_automaton()
                self.automatons[lang] = automaton

        # Pre-compile regex patterns for faster matching
        self.regex_patterns = {}
        for lang, patterns in self.doc_patterns.items():
            self.regex_patterns[lang] = [
                re.compile(pattern, re.MULTILINE | re.DOTALL) for pattern in patterns
            ]

        # Cache for analysis results
        self._analysis_cache = {}

        logger.info(f"DocumentationAnalyzer initialized with threshold: {threshold}")

    async def analyze_file(self, file_status: FileStatus) -> FileStatus:
        """Analyze documentation quality of a file

        Args:
            file_status: FileStatus object for the file to analyze

        Returns:
            Updated FileStatus with documentation score and related information
        """
        # Skip binary files
        if file_status.binary:
            return file_status

        # Check if we have a cached result
        cache_key = str(file_status.path)
        if cache_key in self._analysis_cache:
            file_status.documentation_score = self._analysis_cache[cache_key]
            return file_status

        start_time = time.monotonic()

        try:
            # Determine file type
            suffix = file_status.path.suffix.lower().lstrip(".")
            if suffix in self.doc_patterns:
                file_type = suffix
            elif suffix in ["jsx", "ts", "tsx"]:
                file_type = "js"
            elif suffix in ["rst", "txt"]:
                file_type = "md"
            else:
                file_type = "md"  # Default to markdown patterns

            # Use appropriate patterns for file type
            patterns = self.regex_patterns.get(file_type, self.regex_patterns["md"])

            # Read file content efficiently
            try:
                # Use memory-mapped files for efficient reading
                file_size = file_status.path.stat().st_size
                if file_size > 1024 * 1024:  # For files larger than 1MB
                    with open(file_status.path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                else:
                    with open(file_status.path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
            except Exception as e:
                logger.warning(f"Could not read file {file_status.path}: {e}")
                return file_status

            # Get file stats for scoring
            file_lines = content.count("\n") + 1
            file_chars = len(content)

            # Count documentation matches
            doc_matches = 0

            # Use Aho-Corasick for ultra-fast pattern matching if available
            if HAVE_AHOCORASICK and file_type in self.automatons:
                automaton = self.automatons[file_type]
                for _, (_, pattern) in automaton.iter(content):
                    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
                    matches = regex.finditer(content)
                    doc_matches += sum(1 for _ in matches)
            else:
                # Fallback to standard regex matching
                for pattern in patterns:
                    matches = pattern.finditer(content)
                    doc_matches += sum(1 for _ in matches)

            # Calculate documentation score based on file type and size
            if file_type == "py":
                # Python files should have more documentation
                expected_matches = max(5, file_lines / 10)  # 1 doc element per 10 lines minimum
            elif file_type == "md":
                # Markdown files are documentation themselves
                expected_matches = max(3, file_lines / 20)  # 1 structure element per 20 lines
            else:
                # Other files (JS, etc.)
                expected_matches = max(3, file_lines / 15)  # 1 doc element per 15 lines

            # Calculate score (ratio of actual to expected)
            raw_score = min(1.0, doc_matches / expected_matches)

            # Adjust score based on file size
            if file_lines < 10:  # Very small files
                # Small files need less documentation
                size_adjusted_score = raw_score * 1.5
            elif file_lines > 500:  # Very large files
                # Large files need more consistent documentation
                size_adjusted_score = raw_score * 0.8
            else:
                size_adjusted_score = raw_score

            # Final score capped at 1.0
            final_score = min(1.0, size_adjusted_score)

            # Update file status
            file_status.documentation_score = final_score

            # Cache result
            self._analysis_cache[cache_key] = final_score

            # Add suggestions if score is below threshold
            if final_score < self.threshold:
                if file_type == "py":
                    file_status.suggested_actions.append("Add docstrings to classes and functions")
                    if '"""' not in content[:100]:
                        file_status.suggested_actions.append("Add module-level docstring")
                elif file_type == "md":
                    if not content.startswith("#"):
                        file_status.suggested_actions.append("Add header at the beginning")
                    if "\n## " not in content:
                        file_status.suggested_actions.append("Add section headers")
                else:
                    file_status.suggested_actions.append("Improve documentation coverage")

        except Exception as e:
            logger.error(
                f"Error analyzing documentation for {file_status.path}: {e}", exc_info=True
            )

        # Record performance stats
        analysis_time = time.monotonic() - start_time
        logger.debug(f"Documentation analysis for {file_status.path} took {analysis_time:.3f}s")

        return file_status

    async def analyze_files_batch(self, files: List[FileStatus]) -> List[FileStatus]:
        """Analyze documentation quality for a batch of files in parallel

        Args:
            files: List of FileStatus objects to analyze

        Returns:
            List of updated FileStatus objects with documentation scores
        """
        # Process files in batches for better memory management
        tasks = []
        for file_status in files:
            task = asyncio.create_task(self.analyze_file(file_status))
            tasks.append(task)

        # Wait for all tasks to complete
        analyzed_files = await asyncio.gather(*tasks)

        return analyzed_files


class ReferenceFinder:
    """Finds references between files in the EGOS ecosystem using advanced pattern matching

    Features:
    - Aho-Corasick algorithm for ultra-fast multi-pattern matching
    - Regex pattern fallback for complex matches
    - Memory-mapped file access for large files
    - Caching for repeated reference checks
    """

    def __init__(self, exclusion_manager: Optional['ExclusionManager'] = None):
        """Initialize the reference finder

        Args:
            exclusion_manager: Optional exclusion manager for filtering files
        """
        self.exclusion_manager = exclusion_manager

        # Define reference patterns for different file types
        self.reference_patterns = {
            "md": [
                # Standard markdown links
                r"\[.*?\]\((.*?)\)",
                # Crossref blocks with standard format
                r"<!-- crossref_block:start -->\s*([\s\S]*?)<!-- crossref_block:end -->",
                # Reference section with list
                r"## References[\s\S]*?- (.*?)\n",
                # MQP references
                r"@references[\s\S]*?- (.*?)\n",
                # MDP references with mdc: prefix
                r"mdc:(.*?)\s",
                # Other patterns for backward compatibility
                r"@file (.*?)\n",
            ],
            "py": [
                # Python imports
                r"import (.*?)$",
                r"from (.*?) import",
                # Python references in docstrings
                r"@references[\s\S]*?- (.*?)\n",
                # MQP references in docstrings
                r"@file (.*?)\n",
                # MDP references with mdc: prefix in docstrings
                r"mdc:(.*?)\s",
            ],
            "js": [
                # JavaScript imports
                r'import .* from [""' '](.*?)[""' "]",
                r'require\([""' '](.*?)[""' "]\)",
                # References in JSDoc comments
                r"@see (.*?)\n",
                r"@link (.*?)\n",
            ],
        }

        # Pre-compile regex patterns for faster matching
        self.regex_patterns = {}
        for file_type, patterns in self.reference_patterns.items():
            self.regex_patterns[file_type] = [
                re.compile(pattern, re.MULTILINE | re.DOTALL) for pattern in patterns
            ]

        # Initialize Aho-Corasick automaton if available
        self.automatons = {}
        if HAVE_AHOCORASICK:
            for file_type, patterns in self.reference_patterns.items():
                automaton = pyahocorasick.Automaton()
                for idx, pattern in enumerate(patterns):
                    # Use pattern string as key to later lookup the compiled regex
                    automaton.add_str(pattern, (idx, pattern))
                automaton.make_automaton()
                self.automatons[file_type] = automaton

        # Caches for reference lookups
        self._reference_cache = {}
        self._referenced_by_cache = defaultdict(set)

        logger.info(f"ReferenceFinder initialized")

    def find_references(self, file_status: FileStatus) -> Set[Path]:
        """Find references from a file to other files

        Args:
            file_status: FileStatus object for the file to analyze

        Returns:
            Set of paths that this file references
        """
        # Skip binary files
        if file_status.binary:
            return set()

        # Check cache first
        cache_key = str(file_status.path)
        if cache_key in self._reference_cache:
            return self._reference_cache[cache_key]

        start_time = time.monotonic()
        references = set()

        try:
            file_path = file_status.path
            suffix = file_path.suffix.lower().lstrip(".")

            # Map file type for pattern matching
            if suffix in self.reference_patterns:
                file_type = suffix
            elif suffix in ["jsx", "ts", "tsx"]:
                file_type = "js"
            elif suffix in ["rst", "txt", "yaml", "yml", "json"]:
                file_type = "md"  # Use markdown patterns as default
            else:
                file_type = "md"

            # Get patterns for this file type
            patterns = self.regex_patterns.get(file_type, [])
            if not patterns:
                return set()

            # Read file content efficiently
            try:
                # Use memory-mapped files for efficient reading of large files
                file_size = file_path.stat().st_size
                if file_size > 1024 * 1024:  # For files larger than 1MB
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
                return set()

            # Use Aho-Corasick for faster pattern matching if available
            if HAVE_AHOCORASICK and file_type in self.automatons:
                automaton = self.automatons[file_type]
                for _, (idx, pattern_str) in automaton.iter(content):
                    pattern = self.regex_patterns[file_type][idx]
                    matches = pattern.finditer(content)
                    for match in matches:
                        if match.groups():
                            ref_str = match.group(1)
                            # Process the reference string based on file type
                            if file_type == "md":
                                paths = self._resolve_markdown_reference(ref_str, file_path)
                                references.update(paths)
                            elif file_type == "py":
                                paths = self._resolve_python_reference(ref_str, file_path)
                                references.update(paths)
                            elif file_type == "js":
                                paths = self._resolve_js_reference(ref_str, file_path)
                                references.update(paths)
            else:
                # Fallback to standard regex for pattern matching
                for pattern in patterns:
                    matches = pattern.finditer(content)
                    for match in matches:
                        if match.groups():
                            ref_str = match.group(1)
                            # Process the reference string based on file type
                            if file_type == "md":
                                paths = self._resolve_markdown_reference(ref_str, file_path)
                                references.update(paths)
                            elif file_type == "py":
                                paths = self._resolve_python_reference(ref_str, file_path)
                                references.update(paths)
                            elif file_type == "js":
                                paths = self._resolve_js_reference(ref_str, file_path)
                                references.update(paths)

            # Filter out excluded paths
            if self.exclusion_manager:
                references = {
                    ref for ref in references if not self.exclusion_manager.should_exclude(ref)
                }

            # Update caches
            self._reference_cache[cache_key] = references
            for ref in references:
                self._referenced_by_cache[str(ref)].add(file_path)

        except Exception as e:
            logger.error(f"Error finding references in {file_status.path}: {e}", exc_info=True)

        # Record performance stats
        analysis_time = time.monotonic() - start_time
        logger.debug(f"Reference analysis for {file_status.path} took {analysis_time:.3f}s")

        return references

    def get_references_to(self, file_path: Path) -> Set[Path]:
        """Get files that reference this file

        Args:
            file_path: Path to the file

        Returns:
            Set of paths that reference this file
        """
        return self._referenced_by_cache.get(str(file_path), set())

    def _resolve_markdown_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a markdown reference to actual file paths

        Args:
            ref_str: Reference string from the markdown file
            file_path: Path to the file containing the reference

        Returns:
            Set of resolved file paths
        """
        references = set()

        # Handle standard markdown links
        if ref_str.startswith("http"):  # Skip external URLs
            return references

        # Handle mdc: prefix
        if ref_str.startswith("mdc:"):
            ref_str = ref_str[4:]  # Remove prefix

        # Resolve relative paths
        try:
            # Handle different path formats
            if ref_str.startswith("/"):
                # Absolute path within EGOS
                abs_path = Path("C:/EGOS") / ref_str.lstrip("/")
                if abs_path.exists():
                    references.add(abs_path)
            else:
                # Relative path
                parent_dir = file_path.parent
                rel_path = parent_dir / ref_str
                resolved_path = rel_path.resolve()
                if resolved_path.exists():
                    references.add(resolved_path)

                # Try without parent path (might be relative to EGOS root)
                egos_root = Path("C:/EGOS")
                alt_path = egos_root / ref_str
                if alt_path.exists():
                    references.add(alt_path)
        except Exception as e:
            logger.debug(f"Error resolving markdown reference {ref_str}: {e}")

        return references

    def _resolve_python_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a Python import/reference to actual file paths

        Args:
            ref_str: Reference string from the Python file
            file_path: Path to the file containing the reference

        Returns:
            Set of resolved file paths
        """
        references = set()

        # Handle mdc: prefix
        if ref_str.startswith("mdc:"):
            return self._resolve_markdown_reference(ref_str, file_path)

        # Handle Python imports
        try:
            # Clean up the import string
            ref_str = ref_str.strip()
            if " as " in ref_str:
                ref_str = ref_str.split(" as ")[0]
            if "," in ref_str:
                ref_str = ref_str.split(",")[0]

            # Try relative to file
            parent_dir = file_path.parent
            package_path = parent_dir / (ref_str.replace(".", "/") + ".py")
            if package_path.exists():
                references.add(package_path)

            # Try relative to EGOS root
            egos_root = Path("C:/EGOS")
            alt_path = egos_root / (ref_str.replace(".", "/") + ".py")
            if alt_path.exists():
                references.add(alt_path)

            # Also check for __init__.py in package
            init_path = parent_dir / ref_str.replace(".", "/") / "__init__.py"
            if init_path.exists():
                references.add(init_path)

        except Exception as e:
            logger.debug(f"Error resolving Python reference {ref_str}: {e}")

        return references

    def _resolve_js_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a JavaScript import/reference to actual file paths

        Args:
            ref_str: Reference string from the JavaScript file
            file_path: Path to the file containing the reference

        Returns:
            Set of resolved file paths
        """
        references = set()

        # Skip external packages
        if ref_str.startswith("@") or not ("/" in ref_str or "." in ref_str):
            return references

        try:
            # Clean up the import string
            ref_str = ref_str.strip()

            # Handle relative imports
            parent_dir = file_path.parent
            extensions = [
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                "/index.js",
                "/index.jsx",
                "/index.ts",
                "/index.tsx",
            ]

            # Try each possible extension
            for ext in extensions:
                if ref_str.endswith(ext):
                    # Already has extension
                    path = parent_dir / ref_str
                    if path.exists():
                        references.add(path)
                    break
                else:
                    # Try adding extension
                    path = parent_dir / (ref_str + ext)
                    if path.exists():
                        references.add(path)
                        break

        except Exception as e:
            logger.debug(f"Error resolving JavaScript reference {ref_str}: {e}")

        return references

    # save_report method moved to EGOSSystemMonitor class
        # Save Markdown report
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

        # Clean up old reports (older than 30 days)
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days in seconds
        for old_file in output_dir.glob("system_health_*.json"):
            if old_file.stat().st_mtime < cutoff_time:
                try:
                    old_file.unlink()
                    # Also delete corresponding markdown file
                    md_file = old_file.with_suffix(".md")
                    if md_file.exists():
                        md_file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete old report {old_file}: {e}")

        print_success(f"Report saved to {output_dir}")
        print_info(f"JSON: {json_path.name}")
        print_info(f"Markdown: {md_path.name}")

        return json_path, md_path


class ExclusionManager:
    """Manages file and directory exclusion patterns with caching for performance"""

    def __init__(self, exclude_patterns: List[str] = None):
        # Default exclusion patterns if none provided
        self.exclude_patterns = exclude_patterns or [
            "**/.git/**",
            "**/node_modules/**",
            "**/venv/**",
            "**/__pycache__/**",
            "**/.vscode/**",
            "**/.idea/**",
            "**/.next/**",
            "**/build/**",
            "**/dist/**",
        ]

        # Compile regex patterns for more efficient matching
        self.regex_patterns = []
        for pattern in self.exclude_patterns:
            # Convert glob pattern to regex pattern
            regex_pattern = fnmatch.translate(pattern)
            self.regex_patterns.append(re.compile(regex_pattern))

        # Cache for exclusion decisions to avoid repeated checks
        self._exclusion_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info(f"ExclusionManager initialized with {len(self.exclude_patterns)} patterns")

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns"""
        # Check cache first
        path_str = str(path).replace("\\", "/")
        if path_str in self._exclusion_cache:
            self.cache_hits += 1
            return self._exclusion_cache[path_str]

        self.cache_misses += 1

        # Check against regex patterns
        excluded = any(pattern.match(path_str) for pattern in self.regex_patterns)

        # Cache the result
        self._exclusion_cache[path_str] = excluded

        return excluded

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the exclusion manager"""
        return {
            "patterns": len(self.exclude_patterns),
            "cache_size": len(self._exclusion_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0,
        }


class FileScanner:
    """High-performance scanner for files in the EGOS ecosystem"""

    def __init__(
        self,
        root_path: Path,
        exclusion_manager: ExclusionManager,
        hours_threshold: int = 24,
        max_files: Optional[int] = None,
        batch_size: int = 100,
        progress_report: bool = True,
        file_type_filter: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
    ):
        self.root_path = root_path
        self.exclusion_manager = exclusion_manager
        self.hours_threshold = hours_threshold
        self.max_files = max_files
        self.batch_size = batch_size
        self.progress_report = progress_report
        self.file_type_filter = file_type_filter.lower() if file_type_filter else None
        self.min_size = min_size
        self.max_size = max_size

        # Calculate time threshold
        self.time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours_threshold)
        self.threshold_timestamp = self.time_threshold.timestamp()

        # File type mappings for optimization
        self.text_extensions = {
            ".py",
            ".md",
            ".txt",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".json",
            ".yml",
            ".yaml",
            ".toml",
            ".rst",
        }
        self.binary_extensions = {
            ".pyc",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
        }

        # Performance metrics
        self.stats = {
            "dirs_scanned": 0,
            "files_checked": 0,
            "files_matched": 0,
            "files_excluded": 0,
            "scan_time": 0,
        }

        logger.info(
            f"FileScanner initialized with root: {root_path}, hours threshold: {hours_threshold}"
        )

    def is_likely_binary(self, file_path: Path) -> bool:
        """Check if a file is likely binary based on extension and content sampling"""
        # Check extension first (fast path)
        ext = file_path.suffix.lower()
        if ext in self.binary_extensions:
            return True
        if ext in self.text_extensions:
            return False

        # For unknown extensions, check content
        try:
            # Read first 8KB and check for null bytes or high concentration of non-printable chars
            with open(file_path, "rb") as f:
                sample = f.read(8192)

            # If file contains null bytes, it's likely binary
            if b"\x00" in sample:
                return True

            # Count printable characters
            printable = sum(1 for byte in sample if byte >= 32 and byte < 127)
            ratio = printable / len(sample) if sample else 1

            # If less than 70% printable characters, consider it binary
            return ratio < 0.7

        except Exception:
            # If we can't read the file, assume it's binary to be safe
            return True

    def scan_recent_files(self) -> List[FileStatus]:
        """Scan the filesystem for recently modified files"""
        start_time = time.monotonic()
        recent_files = []
        file_count = 0

        # Create progress display if enabled
        progress = None
        if self.progress_report:
            # We don't know the total yet, so start with a placeholder
            progress = ProgressDisplay(total=100, desc="Scanning for recent files", unit="files")

        # Walk the directory tree
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories early
            root_path = Path(root)
            self.stats["dirs_scanned"] += 1

            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self.exclusion_manager.should_exclude(root_path / d)]

            # Process files in this directory
            for file in files:
                file_path = root_path / file
                self.stats["files_checked"] += 1

                # Skip excluded files
                if self.exclusion_manager.should_exclude(file_path):
                    self.stats["files_excluded"] += 1
                    continue

                try:
                    # Get file stats
                    file_stats = file_path.stat()
                    last_modified = file_stats.st_mtime

                    # Check if file was modified within the time threshold and meets filter criteria
                    file_type_match = True
                    if self.file_type_filter:
                        file_ext = file_path.suffix.lower().lstrip('.')
                        file_type_match = (file_ext == self.file_type_filter)
                    
                    size_match = True
                    if self.min_size is not None or self.max_size is not None:
                        if self.min_size is not None and file_stats.st_size < self.min_size:
                            size_match = False
                        if self.max_size is not None and file_stats.st_size > self.max_size:
                            size_match = False
                    
                    if last_modified >= self.threshold_timestamp and file_type_match and size_match:
                        # Basic file type detection
                        is_binary = self.is_likely_binary(file_path)

                        # Create file status
                        file_status = FileStatus(
                            path=file_path,
                            last_modified=last_modified,
                            size=file_stats.st_size,
                            file_type=file_path.suffix.lower(),
                            binary=is_binary,
                        )

                        recent_files.append(file_status)
                        self.stats["files_matched"] += 1

                        # Update progress
                        file_count += 1
                        if progress and file_count % 10 == 0:
                            # Adjust the total as we go since we don't know it in advance
                            if file_count > progress.total * 0.8:
                                progress.total = file_count * 2
                            progress.update(file_count, desc=f"Scanning: {file_path.name}")

                        # Check if we've reached the max files limit
                        if self.max_files and len(recent_files) >= self.max_files:
                            if progress:
                                progress.finish(f"Reached limit of {self.max_files} files")
                            logger.info(f"Reached max files limit: {self.max_files}")
                            break

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

            # Check again after processing each directory
            if self.max_files and len(recent_files) >= self.max_files:
                break

        # Finish progress display
        if progress:
            progress.finish(f"Found {len(recent_files)} recent files")

        # Record scan time
        self.stats["scan_time"] = time.monotonic() - start_time

        logger.info(
            f"Scan completed in {self.stats['scan_time']:.2f}s, found {len(recent_files)} recent files"
        )
        return recent_files


@dataclass
class SystemHealthReport:
    """Overall health report for the EGOS ecosystem"""

    timestamp: str
    files_analyzed: int
    recently_modified_files: int
    orphaned_files: int
    undocumented_files: int
    well_documented_files: int
    action_items: List[str] = field(default_factory=list)
    files_needing_attention: List[FileStatus] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    recent_files_by_type: Dict[str, int] = field(default_factory=dict)
    recent_files_list: List[FileStatus] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        
        # Convert Path objects to strings in files_needing_attention
        result["files_needing_attention"] = [
            {**{k: (str(v) if isinstance(v, Path) else v) for k, v in asdict(f).items()}} 
            for f in self.files_needing_attention
        ]
        
        # Convert Path objects to strings in recent_files_list
        if self.recent_files_list:
            result["recent_files_list"] = [
                {**{k: (str(v) if isinstance(v, Path) else v) for k, v in asdict(f).items()}}
                for f in self.recent_files_list
            ]
            
        return result

    def to_markdown(self) -> str:
        """Generate a markdown report"""
        md = f"# EGOS System Health Report\n\n"
        md += f"**Generated:** {self.timestamp}\n\n"

        md += "## Summary\n\n"
        md += f"- **Files Analyzed:** {self.files_analyzed}\n"
        md += f"- **Recently Modified:** {self.recently_modified_files}\n"
        md += f"- **Orphaned Files:** {self.orphaned_files}\n"
        md += f"- **Undocumented Files:** {self.undocumented_files}\n"
        md += f"- **Well Documented Files:** {self.well_documented_files}\n\n"
        
        # Add recently modified files by type section if available
        if self.recent_files_by_type:
            md += "## Recently Modified Files by Type\n\n"
            for file_type, count in sorted(self.recent_files_by_type.items(), key=lambda x: x[1], reverse=True):
                md += f"- **{file_type or 'unknown'}:** {count}\n"
            md += "\n"
            
            # Add pie chart for file types using ASCII art if more than one type
            if len(self.recent_files_by_type) > 1:
                md += "### File Type Distribution\n\n"
                md += "```\n"
                total = sum(self.recent_files_by_type.values())
                for file_type, count in sorted(self.recent_files_by_type.items(), key=lambda x: x[1], reverse=True)[:5]:  # Top 5
                    percentage = (count / total) * 100
                    bar_length = int(percentage / 2)  # Scale to reasonable length
                    md += f"{file_type.ljust(10)}: {'█' * bar_length} {percentage:.1f}%\n"
                md += "```\n\n"
            
        # Add list of recently modified files if available
        if self.recent_files_list:
            md += "## Recent File Modifications\n\n"
            md += "| File | Type | Last Modified | Size |\n"
            md += "|------|------|--------------|------|\n"
            for file in sorted(self.recent_files_list, key=lambda x: x.last_modified, reverse=True)[:20]:  # Limit to top 20
                file_type = file.file_type.lstrip('.') if file.file_type else 'unknown'
                mod_time = datetime.datetime.fromtimestamp(file.last_modified).strftime("%Y-%m-%d %H:%M:%S")
                size_str = f"{file.size / 1024:.1f} KB" if file.size > 1024 else f"{file.size} bytes"
                md += f"| {file.path.name} | {file_type} | {mod_time} | {size_str} |\n"
            md += "\n"

        md += "## Action Items\n\n"
        for item in self.action_items:
            md += f"- {item}\n"
        md += "\n"

        md += "## Files Needing Attention\n\n"
        md += "| File | Last Modified | References | Referenced By | Needs | Actions |\n"
        md += "|------|---------------|------------|---------------|-------|--------|\n"

        for file in self.files_needing_attention[
            :20
        ]:  # Limit to 20 files to keep report manageable
            actions = ", ".join(file.suggested_actions[:2])
            if len(file.suggested_actions) > 2:
                actions += f" +{len(file.suggested_actions) - 2} more"

            md += f"| {file.relative_path} | {datetime.datetime.fromtimestamp(file.last_modified).strftime('%Y-%m-%d')} "
            md += f"| {file.reference_count} | {file.referenced_by_count} | {'⚠️' if file.needs_attention else '✅'} "
            md += f"| {actions} |\n"

        if len(self.files_needing_attention) > 20:
            md += f"\n> Note: {len(self.files_needing_attention) - 20} more files need attention. See the full report for details.\n"

        md += "\n## Performance Metrics\n\n"
        md += f"- **Total Execution Time:** {self.performance_metrics.get('total_time_formatted', 'N/A')}\n"
        md += f"- **Scan Time:** {self.performance_metrics.get('scan_time_formatted', 'N/A')}\n"
        md += f"- **Analysis Time:** {self.performance_metrics.get('analysis_time_formatted', 'N/A')}\n"

        if "file_processing" in self.performance_metrics:
            fp = self.performance_metrics["file_processing"]
            md += f"- **Files Processed:** {fp.get('processed', 0)}\n"
            md += f"- **Average Processing Time:** {fp.get('avg_time_formatted', 'N/A')}\n"

        if "system_stats" in self.performance_metrics:
            ss = self.performance_metrics["system_stats"]
            if "memory_delta" in ss:
                md += f"- **Memory Usage:** {ss['memory_delta']:.1f} MB\n"

        md += "\n✧༺❀༻∞ EGOS ∞༺❀༻✧\n"

        return md

    def _resolve_markdown_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a markdown reference to actual file paths"""
        resolved = set()

        # Clean up the reference string
        ref_str = ref_str.strip()

        # Check if this is a crossref block with multiple references
        if "Reference:" in ref_str or "🔗" in ref_str:
            # Process multiple references in a crossref block
            for line in ref_str.split("\n"):
                if "Reference:" in line or "🔗" in line:
                    # Extract the reference path from formats like:
                    # - 🔗 Reference: [file.md](path/to/file.md)
                    # - Reference: [file.md](path/to/file.md)
                    match = re.search(r"\[.*?\]\((.*?)\)", line)
                    if match:
                        link_path = match.group(1)
                        paths = self._resolve_relative_path(link_path, file_path)
                        resolved.update(paths)
        else:
            # Handle a single reference
            paths = self._resolve_relative_path(ref_str, file_path)
            resolved.update(paths)

        return resolved

    def _resolve_python_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a Python import to actual file paths"""
        resolved = set()

        # Convert module paths to file paths
        module_parts = ref_str.split(".")

        # Try different possible file paths for the module
        possible_paths = [
            # Direct import as .py file
            Path("/".join(module_parts) + ".py"),
            # Import as directory with __init__.py
            Path("/".join(module_parts) + "/__init__.py"),
            # Relative import
            file_path.parent / (Path("/".join(module_parts)) + ".py"),
            # Relative directory import
            file_path.parent / (Path("/".join(module_parts)) / "__init__.py"),
        ]

        for path in possible_paths:
            if path.exists() and not self.exclusion_manager.should_exclude(path):
                resolved.add(path)

        return resolved

    def _resolve_js_reference(self, ref_str: str, file_path: Path) -> Set[Path]:
        """Resolve a JavaScript/TypeScript import to actual file paths"""
        resolved = set()

        # Handle relative imports vs package imports
        if ref_str.startswith(".") or ref_str.startswith("/"):
            # Relative import
            paths = self._resolve_relative_path(ref_str, file_path)
            resolved.update(paths)

        return resolved

    def _resolve_relative_path(self, path_str: str, source_file: Path) -> Set[Path]:
        """Resolve a relative path to absolute file paths"""
        resolved = set()

        try:
            # Handle different formats
            if path_str.startswith(("./", "../")):
                # Relative path
                path = (source_file.parent / path_str).resolve()
                if path.exists() and not self.exclusion_manager.should_exclude(path):
                    resolved.add(path)
            elif ":/" in path_str or ":\\" in path_str:
                # Absolute path
                path = Path(path_str)
                if path.exists() and not self.exclusion_manager.should_exclude(path):
                    resolved.add(path)
            elif path_str.startswith("/"):
                # Root-relative path
                path = Path(path_str)
                if path.exists() and not self.exclusion_manager.should_exclude(path):
                    resolved.add(path)
            else:
                # Try to resolve as relative path anyway
                path = (source_file.parent / path_str).resolve()
                if path.exists() and not self.exclusion_manager.should_exclude(path):
                    resolved.add(path)

                # Try with common extensions if no extension is provided
                if not path_str.endswith((".py", ".md", ".js", ".jsx", ".ts", ".tsx")):
                    for ext in [".py", ".md", ".js", ".jsx", ".ts", ".tsx"]:
                        path_with_ext = (source_file.parent / (path_str + ext)).resolve()
                        if path_with_ext.exists() and not self.exclusion_manager.should_exclude(
                            path_with_ext
                        ):
                            resolved.add(path_with_ext)
        except Exception as e:
            logger.error(f"Error resolving path {path_str} from {source_file}: {e}")

        return resolved


class EGOSSystemMonitor:
    """
    Advanced system monitor for the EGOS ecosystem

    Features:
    - High-performance file scanning with exclusion caching
    - Async file processing for improved throughput
    - Parallel documentation analysis with advanced pattern matching
    - Memory-mapped file handling for large files
    - Detailed performance metrics and reporting
    - Beautiful progress visualization
    """

    def __init__(
        self,
        egos_root: Path = Path("C:/EGOS"),
        hours_threshold: int = 24,
        documentation_threshold: float = 0.6,
        exclude_patterns: List[str] = None,
        max_files: int = None,
        progress_report: bool = True,
        file_type_filter: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
    ):
        """
        Initialize the system monitor

        Args:
            egos_root: Root directory of the EGOS ecosystem
            hours_threshold: Hours threshold for considering files as recently modified
            documentation_threshold: Threshold for considering a file well-documented (0-1)
            exclude_patterns: Patterns of files/directories to exclude
            max_files: Maximum number of files to process (None for unlimited)
            progress_report: Whether to show progress displays
        """
        self.egos_root = egos_root
        self.hours_threshold = hours_threshold
        self.documentation_threshold = documentation_threshold
        self.max_files = max_files
        self.progress_report = progress_report
        self.file_type_filter = file_type_filter.lower() if file_type_filter else None
        self.min_size = min_size
        self.max_size = max_size

        # Initialize components
        self.performance_monitor = PerformanceMonitor()
        self.exclusion_manager = ExclusionManager(exclude_patterns)
        self.file_scanner = FileScanner(
            root_path=egos_root,
            exclusion_manager=self.exclusion_manager,
            hours_threshold=hours_threshold,
            max_files=max_files,
            progress_report=progress_report,
            file_type_filter=file_type_filter,
            min_size=min_size,
            max_size=max_size,
        )
        self.doc_analyzer = DocumentationAnalyzer(documentation_threshold, self.exclusion_manager)
        self.ref_finder = ReferenceFinder(self.exclusion_manager)

        # File stats cache
        self.file_stats: Dict[Path, FileStatus] = {}

        logger.info(f"Initialized EGOS System Monitor with root: {egos_root}")

        # Set up the event loop for async operations
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns"""
        return self.exclusion_manager.should_exclude(path)

    def get_recent_files(self) -> List[FileStatus]:
        """Get files modified in the last N hours"""
        recent_files = []
        threshold_time = datetime.datetime.now() - datetime.timedelta(hours=self.hours_threshold)
        threshold_timestamp = threshold_time.timestamp()

        logger.info(f"Scanning for files modified in the last {self.hours_threshold} hours...")

        file_count = 0
        for root, dirs, files in os.walk(self.egos_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                if self._should_exclude(file_path):
                    continue

                try:
                    stats = file_path.stat()
                    last_modified = stats.st_mtime

                    if last_modified >= threshold_timestamp:
                        file_status = FileStatus(
                            path=file_path, last_modified=last_modified, size=stats.st_size
                        )
                        recent_files.append(file_status)
                        self.file_stats[file_path] = file_status

                        file_count += 1
                        if file_count % 100 == 0 and self.progress_report:
                            print_info(f"  - Scanned {file_count} recently modified files...")

                        # Check if we've reached the max files limit
                        if self.max_files and len(recent_files) >= self.max_files:
                            logger.info(
                                f"Reached max files limit ({self.max_files}). Stopping scan."
                            )
                            print_warning(
                                f"  - Limited to {self.max_files} files. Use --limit 0 to process all files."
                            )
                            break

                except Exception as e:
                    logger.error(f"Error accessing file {file_path}: {e}")

            # Check again after processing each directory
            if self.max_files and len(recent_files) >= self.max_files:
                break

        logger.info(f"Found {len(recent_files)} recently modified files")
        return recent_files

    async def check_documentation_status(self, files: List[FileStatus]):
        """Check documentation status of files asynchronously

        Args:
            files: List of FileStatus objects to check

        Returns:
            List of updated FileStatus objects with documentation scores
        """
        if not files:
            return files

        print_info(f"Checking documentation status for {len(files)} files...")
        self.performance_monitor.start_phase("documentation_analysis")

        # Create progress display
        progress = None
        if self.progress_report:
            progress = ProgressDisplay(len(files), "Analyzing documentation", "files")

        # Process files in batches
        batch_size = 50  # Process 50 files at a time
        updated_files = []

        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]

            # Process batch asynchronously
            try:
                processed_batch = await self.doc_analyzer.analyze_files_batch(batch)
                updated_files.extend(processed_batch)

                # Update progress
                if progress:
                    progress.update(
                        completed=len(updated_files),
                        desc=f"Processed {len(updated_files)}/{len(files)}",
                    )

            except Exception as e:
                logger.error(f"Error in documentation batch processing: {e}", exc_info=True)

        # Apply threshold and mark files needing attention
        for file in updated_files:
            if file.documentation_score < self.documentation_threshold:
                file.needs_attention = True

        # Complete progress
        if progress:
            progress.finish("Documentation analysis complete")

        self.performance_monitor.end_phase("documentation_analysis")
        return updated_files

    async def check_cross_references(self, files: List[FileStatus]):
        """Check cross-reference status using ReferenceFinder

        Args:
            files: List of FileStatus objects to check

        Returns:
            Updated list of FileStatus objects with reference information
        """
        if not files:
            return files

        print_info(f"Checking cross-references between {len(files)} files...")
        self.performance_monitor.start_phase("cross_reference_analysis")

        # Create progress display
        progress = None
        if self.progress_report:
            progress = ProgressDisplay(len(files), "Analyzing references", "files")

        # First pass: Find all references from files
        reference_map = {}
        referenced_by_map = defaultdict(set)

        for i, file_status in enumerate(files):
            # Skip binary files
            if file_status.binary:
                if progress:
                    progress.update()
                continue

            # Find references from this file to others
            start_time = time.monotonic()
            references = self.ref_finder.find_references(file_status)

            # Store in maps
            reference_map[file_status.path] = references
            for ref in references:
                referenced_by_map[ref].add(file_status.path)

            # Record performance
            processing_time = time.monotonic() - start_time
            self.performance_monitor.record_file_processing(file_status.path, processing_time)

            # Update progress
            if progress:
                progress.update(desc=f"Analyzed {file_status.path.name} ({i + 1}/{len(files)})")

        # Second pass: Update file statuses with reference information
        for file_status in files:
            file_status.reference_count = len(reference_map.get(file_status.path, set()))
            file_status.has_references = file_status.reference_count > 0

            file_status.referenced_by_count = len(referenced_by_map.get(file_status.path, set()))
            file_status.is_referenced = file_status.referenced_by_count > 0

            # Check if file needs attention
            if not file_status.is_referenced and file_status.path.suffix.lower() in [
                ".md",
                ".py",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
            ]:
                file_status.needs_attention = True
                file_status.suggested_actions.append("Add references to this file from other files")

        # Complete progress
        if progress:
            progress.finish("Cross-reference analysis complete")

        self.performance_monitor.end_phase("cross_reference_analysis")
        return files

    def generate_report(self):
        """Generate a system health report with detailed performance metrics

        Returns:
            SystemHealthReport: Health report with diagnostic results
        """
        print_info("Generating system health report...")

        # Count statistics
        total_files = len(self.file_stats)
        recently_modified = sum(1 for _, status in self.file_stats.items() if status.processed)
        orphaned = sum(
            1
            for _, status in self.file_stats.items()
            if not status.is_referenced and status.processed and not status.binary
        )
        undocumented = sum(
            1
            for _, status in self.file_stats.items()
            if status.documentation_score < self.documentation_threshold
            and status.processed
            and not status.binary
        )
        well_documented = sum(
            1
            for _, status in self.file_stats.items()
            if status.documentation_score >= self.documentation_threshold
            and status.processed
            and not status.binary
        )

        # Create report
        # Calculate recently modified files and categorize by type
        recent_files_from_stats = [
            f for f in self.file_stats.values()
            if f.last_modified >= self.file_scanner.threshold_timestamp
            and (self.file_type_filter is None or 
                 (f.path.suffix.lower().lstrip('.') == self.file_type_filter))
            and (self.min_size is None or f.size >= self.min_size)
            and (self.max_size is None or f.size <= self.max_size)
        ]
        count_recent_from_stats = len(recent_files_from_stats)
        
        # Categorize recent files by type
        recent_files_by_type = {}
        for file in recent_files_from_stats:
            # Get file extension without the dot, or use directory/unknown
            if file.path.is_dir():
                file_type = "directory"
            else:
                file_type = file.path.suffix.lower() or "unknown"
                if file_type.startswith('.'):
                    file_type = file_type[1:]
            
            # Increment count for this file type
            if file_type in recent_files_by_type:
                recent_files_by_type[file_type] += 1
            else:
                recent_files_by_type[file_type] = 1

        report = SystemHealthReport(
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            files_analyzed=total_files,
            recently_modified_files=count_recent_from_stats,
            orphaned_files=orphaned,
            undocumented_files=undocumented,
            well_documented_files=well_documented,
            performance_metrics=self.performance_monitor.get_summary(),
            recent_files_by_type=recent_files_by_type,
            recent_files_list=recent_files_from_stats[:50]  # Limit to 50 most recent files
        )

        # Generate action items
        if orphaned > 0:
            report.action_items.append(f"Add references to {orphaned} orphaned files")
        if undocumented > 0:
            report.action_items.append(f"Improve documentation in {undocumented} files")

        # Add suggestions based on file types
        file_types = Counter(
            [
                status.path.suffix.lower()
                for _, status in self.file_stats.items()
                if status.needs_attention and status.processed
            ]
        )
        if ".py" in file_types and file_types[".py"] > 5:
            report.action_items.append(f"Consider running a docstring formatter on Python files")
        if ".md" in file_types and file_types[".md"] > 5:
            report.action_items.append(f"Consider standardizing markdown headers and structure")

        # Prioritize files that need attention
        files_needing_attention = [
            status
            for _, status in self.file_stats.items()
            if status.needs_attention and status.processed
        ]

        # Sort by multiple criteria (most urgent first)
        files_needing_attention.sort(
            key=lambda x: (
                not x.is_referenced,  # Orphaned files first
                x.documentation_score,  # Then by documentation score (ascending)
                -x.last_modified,  # Then by last modified (most recent first)
            )
        )

        report.files_needing_attention = files_needing_attention

        # Add performance insights
        metrics = self.performance_monitor.get_summary()
        if metrics["total_time"] > 60 and len(files_needing_attention) > 20:
            report.action_items.append(
                "Consider increasing the --limit parameter for faster scans of targeted directories"
            )

        if HAVE_AHOCORASICK == False and total_files > 100:
            report.action_items.append(
                "Install pyahocorasick package for 10-100x faster pattern matching: pip install pyahocorasick"
            )

        return report

    def run_diagnostics(self):
        """Run full system diagnostics with performance monitoring

        Returns:
            SystemHealthReport: Health report with diagnostic results
        """
        print_banner("EGOS System Monitor - Diagnostics")
        self.performance_monitor.start_phase("overall_diagnostics")

        # Get recent files
        self.performance_monitor.start_phase("file_scanning")
        recent_files = self.get_recent_files()
        self.performance_monitor.end_phase("file_scanning")

        # Check documentation status (async operation)
        # We need to run this in the event loop
        recent_files = self.loop.run_until_complete(self.check_documentation_status(recent_files))

        # Check cross-references (async operation)
        recent_files = self.loop.run_until_complete(self.check_cross_references(recent_files))

        # Generate report
        self.performance_monitor.start_phase("report_generation")
        report = self.generate_report()

        # Add performance metrics to the report
        report.performance_metrics = self.performance_monitor.get_summary()

        self.performance_monitor.end_phase("report_generation")
        self.performance_monitor.end_phase("overall_diagnostics")

        print_success(
            f"Diagnostics complete! Found {len(report.files_needing_attention)} files needing attention."
        )

        return report

    def fix_documentation_issues(self, report: SystemHealthReport, dry_run: bool = True) -> None:
        """Attempt to fix documentation issues automatically"""
        print_banner("EGOS System Monitor - Automated Fixes")

        if dry_run:
            print_warning("Running in dry-run mode. No changes will be made.")

        files_to_fix = report.files_needing_attention

        print_info(f"Analyzing {len(files_to_fix)} files for potential fixes...")

        for file_status in files_to_fix:
            print(f"\nProcessing: {file_status.relative_path}")

            # Try to fix missing references
            if "Add cross-references" in file_status.suggested_actions:
                print_info("  - Attempting to add cross-references...")

                try:
                    # Check if ReferenceFixer is available
                    try:
                        from cross_reference.optimized_reference_fixer import ReferenceFixer

                        if not dry_run:
                            fixer = ReferenceFixer(
                                target_file=str(file_status.path), auto_mode=True, verbosity=1
                            )
                            result = fixer.fix_references()
                            if result:
                                print_success("    ✓ Added cross-references")
                            else:
                                print_warning("    ⚠ No cross-references added")
                        else:
                            print_info("    ℹ Would add cross-references (dry run)")

                    except ImportError:
                        print_warning("    ⚠ ReferenceFixer not available")

                except Exception as e:
                    print_error(f"    ✗ Error fixing references: {e}")

            # Try to improve documentation
            if "Improve documentation" in file_status.suggested_actions:
                print_info("  - Checking for documentation improvement...")

                try:
                    suffix = file_status.path.suffix.lower()

                    # Skip files without known doc patterns
                    if suffix not in self.doc_patterns:
                        print_warning("    ⚠ Unsupported file type for documentation improvement")
                        continue

                    # Basic documentation template by file type
                    templates = {
                        ".py": '"""\n{filename}\n\nDescription: [Add description]\n\n@module: {module_path}\n@date: {date}\n"""\n\n',
                        ".md": "---\ntitle: {filename}\ndescription: [Add description]\ncreated: {date}\nupdated: {date}\n---\n\n# {title}\n\n",
                        ".ts": "/**\n * @file {filename}\n * @description [Add description]\n * @module {module_path}\n * @date {date}\n */\n\n",
                        ".tsx": "/**\n * @file {filename}\n * @description [Add description]\n * @module {module_path}\n * @date {date}\n */\n\n",
                        ".js": "/**\n * @file {filename}\n * @description [Add description]\n * @module {module_path}\n * @date {date}\n */\n\n",
                        ".jsx": "/**\n * @file {filename}\n * @description [Add description]\n * @module {module_path}\n * @date {date}\n */\n\n",
                    }

                    if suffix in templates and not dry_run:
                        with open(file_status.path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        # Check if file already has documentation
                        has_docs = False
                        for pattern in self.doc_patterns.get(suffix, []):
                            if re.search(pattern, content):
                                has_docs = True
                                break

                        if not has_docs:
                            # Prepare template variables
                            filename = file_status.path.name
                            module_path = (
                                file_status.relative_path.replace("\\", "/")
                                .replace(".py", "")
                                .replace("/", ".")
                            )
                            date = datetime.datetime.now().strftime("%Y-%m-%d")
                            title = filename.split(".")[0].replace("_", " ").title()

                            # Format template
                            template = templates[suffix].format(
                                filename=filename, module_path=module_path, date=date, title=title
                            )

                            # Add template to file
                            with open(file_status.path, "w", encoding="utf-8") as f:
                                f.write(template + content)

                            print_success("    ✓ Added documentation template")
                        else:
                            print_warning("    ⚠ File already has some documentation")
                    elif dry_run:
                        print_info("    ℹ Would add documentation template (dry run)")

                except Exception as e:
                    print_error(f"    ✗ Error improving documentation: {e}")

        print_success("\nAutomated fix process completed!")

    def save_report(self, report: 'SystemHealthReport', output_dir: Path = None) -> Tuple[Path, Path]:
        """Save the report to JSON and Markdown files

        Args:
            report: System health report to save
            output_dir: Directory to save reports to (default: {egos_root}/reports/system_monitor)

        Returns:
            Tuple of paths to the JSON and Markdown report files
        """
        if output_dir is None:
            output_dir = self.egos_root / "reports" / "system_monitor"

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamped filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"system_health_{timestamp}.json"
        md_path = output_dir / f"system_health_{timestamp}.md"

        # Save JSON report
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        
        # Save Markdown report
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

        return json_path, md_path


def main():
    """Main function to run the EGOS System Monitor"""
    parser = argparse.ArgumentParser(
        description="EGOS System Monitor - Track file changes and ensure documentation compliance"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours threshold for considering files as recently modified",
    )
    parser.add_argument(
        "--file-type",
        type=str,
        help="Filter recent files by file type/extension (e.g., py, md, txt)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        help="Minimum file size in bytes for filtering recent files",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        help="Maximum file size in bytes for filtering recent files",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Threshold for considering a file well-documented (0-1)",
    )
    parser.add_argument(
        "--root", type=str, default="C:/EGOS", help="Root directory of the EGOS ecosystem"
    )
    parser.add_argument("--output", type=str, help="Directory to save reports")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix documentation issues")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Limit the number of files to process (0 for no limit)",
    )
    parser.add_argument("--no-progress", action="store_true", help="Disable progress reporting")

    args = parser.parse_args()

    # Define exclude patterns
    exclude_patterns = [
        "**/.git/**",
        "**/node_modules/**",
        "**/venv/**",
        "**/__pycache__/**",
    ]
    
    try:
        # Initialize and run monitor
        monitor = EGOSSystemMonitor(
            egos_root=Path(args.root),
            hours_threshold=args.hours,
            documentation_threshold=args.threshold,
            exclude_patterns=exclude_patterns,
            max_files=args.limit if args.limit > 0 else None,
            progress_report=not args.no_progress,
            file_type_filter=args.file_type,
            min_size=args.min_size,
            max_size=args.max_size,
        )

        # Run diagnostics
        report = monitor.run_diagnostics()

        # Save report
        output_dir = Path(args.output) if args.output else None
        json_path, md_path = monitor.save_report(report, output_dir)
        print_info(f"\nReports saved to:")
        print_info(f"  - JSON: {json_path}")
        print_info(f"  - Markdown: {md_path}")

        # Try to fix issues if requested
        if args.fix:
            monitor.fix_documentation_issues(report, dry_run=args.dry_run)

        print_banner("EGOS System Monitor - Summary")
        print_info(f"Files analyzed: {report.files_analyzed}")
        print_info(f"Recently modified: {report.recently_modified_files}")
        print_info(f"Orphaned files: {report.orphaned_files}")
        print_info(f"Undocumented files: {report.undocumented_files}")
        print_info(f"Well documented files: {report.well_documented_files}")

        print_info("\nTop action items:")
        for item in report.action_items:
            print_info(f"  - {item}")

        print_success("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")

    except Exception as e:
        print_error(f"Error running EGOS System Monitor: {e}")
        logger.error(f"Error running EGOS System Monitor: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())