#!/usr/bin/env python3
"""
EGOS - Code Health Docstring Workflow Manager
=============================================

A unified CLI interface for the complete EGOS docstring management workflow.
Coordinates batch processing and integration with interactive tools.

Version: 1.0.0 (Initial)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Define paths relative to EGOS root
SCRIPTS_DIR = Path(__file__).parent
EGOS_ROOT = SCRIPTS_DIR.parent.parent.parent
REPORTS_DIR = EGOS_ROOT / "reports" / "docstrings"
BACKUP_DIR = EGOS_ROOT / "backups" / "docstrings"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Script paths
CHECKER_SCRIPT = SCRIPTS_DIR / "docstring_checker.py"
AUTOFIXER_SCRIPT = SCRIPTS_DIR / "docstring_autofixer.py"
ANALYZER_SCRIPT = SCRIPTS_DIR / "analyze_autofixer_results.py"
FIXER_SCRIPT = SCRIPTS_DIR / "fix_autofixer_issues.py"


class DocstringWorkflow:
    """Manages the complete docstring improvement workflow.

    Coordinates all the separate scripts in the docstring automation toolchain,
    providing a unified interface for checking, fixing, analyzing, and reporting
    docstring issues across the codebase.

    Attributes:
        target_dir: Path to the directory to process.
        reports_dir: Directory where reports will be saved.
        backups_dir: Directory where backups will be saved.
        report_path: Path to the JSON report file.
        timestamp: Timestamp for this workflow run.

    Methods:
        run_full_workflow: Execute the complete docstring workflow.
        check: Run the docstring checker.
        autofix: Run the docstring autofixer.
        analyze: Analyze the results of autofixing.
        fix_issues: Fix common issues with the autofixer output.
        verify: Verify the fixed docstrings.
    """

    def __init__(
        self, 
        target_dir: str, 
        reports_dir: Optional[str] = None,
        backups_dir: Optional[str] = None,
        dry_run: bool = False,
        verbose: bool = False
    ):
        """Initialize the workflow manager.

        Args:
            target_dir: Directory to process docstrings in.
            reports_dir: Directory to store reports (default: REPORTS_DIR).
            backups_dir: Directory to store backups (default: BACKUP_DIR).
            dry_run: If True, don't make actual changes.
            verbose: If True, display detailed logs.
        """
        self.target_dir = Path(target_dir)
        self.reports_dir = Path(reports_dir) if reports_dir else REPORTS_DIR
        self.backups_dir = Path(backups_dir) if backups_dir else BACKUP_DIR
        self.dry_run = dry_run
        self.verbose = verbose

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_path = self.reports_dir / f"{self.target_dir.name}_report_{self.timestamp}.json"

        # Check all dependencies are present
        self._check_dependencies()

    @staticmethod
    def _check_dependencies() -> None:
        """Verify all required script dependencies are available."""
        missing = []
        for script in [CHECKER_SCRIPT, AUTOFIXER_SCRIPT, ANALYZER_SCRIPT, FIXER_SCRIPT]:
            if not script.exists():
                missing.append(script)

        if missing:
            logger.error(f"Missing dependencies: {[str(m) for m in missing]}")
            logger.error("Please ensure all docstring automation scripts are installed.")
            sys.exit(1)

    def _run_script(self, script_path: Path, args: List[str]) -> int:
        """Run a Python script with the given arguments.

        Args:
            script_path: Path to the script to run.
            args: Arguments to pass to the script.

        Returns:
            Return code from the script execution.
        """
        cmd = [sys.executable, str(script_path)] + args
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout and self.verbose:
            logger.info(result.stdout)

        if result.stderr and result.returncode != 0:
            logger.error(result.stderr)

        return result.returncode

    def run_full_workflow(self) -> bool:
        """Execute the complete docstring workflow.

        Runs all stages of the workflow in sequence:
        1. Checking for docstring issues
        2. Applying automated fixes
        3. Analyzing the results for secondary issues
        4. Fixing secondary issues
        5. Verifying the final result

        Returns:
            True if workflow completed successfully, False otherwise.
        """
        logger.info(f"Starting complete docstring workflow for {self.target_dir.name}")

        # Create a backup before starting
        backup_path = self._create_backup()
        logger.info(f"Created backup at {backup_path}")

        # Step 1: Check docstrings
        if not self.check():
            return False

        # Step 2: Run the autofixer
        if not self.autofix():
            return False

        # Step 3: Analyze the results
        if not self.analyze():
            return False

        # Step 4: Fix any issues found
        if not self.fix_issues():
            return False

        # Step 5: Final verification
        if not self.verify():
            return False

        logger.info(f"Complete docstring workflow for {self.target_dir.name} finished successfully!")
        logger.info(f"Final report available at: {self.report_path}")
        return True

    def _create_backup(self) -> Path:
        """Create a backup of the target directory.

        Returns:
            Path to the created backup.
        """
        backup_name = f"{self.target_dir.name}_backup_{self.timestamp}"
        backup_path = self.backups_dir / backup_name

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create backup at: {backup_path}")
            return backup_path

        shutil.copytree(self.target_dir, backup_path)
        return backup_path

    def check(self) -> bool:
        """Run the docstring checker on the target directory.

        Returns:
            True if check completed successfully, False otherwise.
        """
        logger.info(f"Checking docstrings in {self.target_dir}")

        args = [
            "--root-dir", str(self.target_dir),
            "--json", str(self.report_path)
        ]

        if self.verbose:
            args.append("--verbose")

        return self._run_script(CHECKER_SCRIPT, args) == 0

    def autofix(self) -> bool:
        """Run the docstring autofixer on the target directory.

        Returns:
            True if autofix completed successfully, False otherwise.
        """
        logger.info(f"Auto-fixing docstrings based on report")

        args = ["--report-path", str(self.report_path)]

        if self.dry_run:
            args.append("--dry-run")

        if self.verbose:
            args.append("--verbose")

        return self._run_script(AUTOFIXER_SCRIPT, args) == 0

    def analyze(self) -> bool:
        """Analyze the results of the autofixer.

        Returns:
            True if analysis completed successfully, False otherwise.
        """
        logger.info("Analyzing autofixer results for secondary issues")

        args = []
        if self.verbose:
            args.append("--verbose")

        return self._run_script(ANALYZER_SCRIPT, args) == 0

    def fix_issues(self) -> bool:
        """Fix common issues found in the autofix results.

        Returns:
            True if fixes were applied successfully, False otherwise.
        """
        logger.info("Fixing secondary issues from autofixer results")

        args = []
        if self.dry_run:
            args.append("--dry-run")

        if self.verbose:
            args.append("--verbose")

        return self._run_script(FIXER_SCRIPT, args) == 0

    def verify(self) -> bool:
        """Verify the final state of docstrings after all fixes.

        This runs the checker again to see if issues remain.

        Returns:
            True if verification completed, False otherwise.
        """
        logger.info("Verifying final docstring state")

        verification_report = self.reports_dir / f"{self.target_dir.name}_verification_{self.timestamp}.json"

        args = [
            "--root-dir", str(self.target_dir),
            "--json", str(verification_report)
        ]

        if self.verbose:
            args.append("--verbose")

        success = self._run_script(CHECKER_SCRIPT, args) == 0

        # Compare initial and final reports
        try:
            with open(self.report_path, 'r') as f:
                initial_issues = len(json.load(f).get("issues", []))

            with open(verification_report, 'r') as f:
                final_issues = len(json.load(f).get("issues", []))

            reduction = initial_issues - final_issues
            if initial_issues > 0:
                percent = (reduction / initial_issues) * 100
                logger.info(f"Issues reduced: {reduction} ({percent:.1f}%)")
                logger.info(f"Remaining issues: {final_issues}")
        except Exception as e:
            logger.error(f"Error comparing reports: {e}")

        return success


def setup_ide_integration() -> None:
    """Setup recommended VS Code extensions for docstring management.

    Provides instructions for installing and configuring extensions
    that complement the EGOS docstring automation workflow.
    """
    print("\n=== VS Code Integration ===")
    print("\nTo enhance your docstring workflow with interactive tools:")
    print("\n1. Install these VS Code extensions:")
    print("   • QuantumDoc - AI-powered Google-style docstring generator")
    print("     Install: Cmd+Shift+X (Mac) or Ctrl+Shift+X (Windows/Linux), search 'QuantumDoc'")
    print("     Usage: Cmd+Shift+P > 'Generate Docstrings'")
    print("     Note: Requires Gemini API Key setup")
    print("   • autoDocstring - Template-based docstring generator")
    print("     Install: Cmd+Shift+X (Mac) or Ctrl+Shift+X (Windows/Linux), search 'autoDocstring'")
    print("     Configure: Set to Google style in VS Code settings")

    print("\n2. Recommended workflow:")
    print("   • Use autoDocstring for simple functions and standard patterns")
    print("   • Use QuantumDoc for complex functions requiring intelligent content")
    print("   • Use EGOS batch automation for existing code and bulk fixes")

    print("\n3. VS Code settings.json configuration:")
    print("""   ```
   "autoDocstring.docstringFormat": "google",
   "autoDocstring.startOnNewLine": true,
   "autoDocstring.includeExtendedSummary": true
   ```""")

def main():
    """Execute the docstring workflow from the command line."""
    parser = argparse.ArgumentParser(
        description="EGOS Docstring Workflow Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow on ATLAS subsystem
  python docstring_workflow.py --target-dir ../../subsystems/ATLAS --verbose

  # Run dry-run on ETHIK subsystem
  python docstring_workflow.py --target-dir ../../subsystems/ETHIK --dry-run

  # Show IDE integration instructions
  python docstring_workflow.py --ide-integration

  # Run just the checker and view the report
  python docstring_workflow.py --target-dir ../../subsystems/NEXUS --check-only
""")

    parser.add_argument(
        "--target-dir", 
        help="Directory to process (e.g., subsystems/ATLAS)"
    )
    parser.add_argument(
        "--reports-dir", 
        help=f"Directory to store reports (default: {REPORTS_DIR})"
    )
    parser.add_argument(
        "--backups-dir", 
        help=f"Directory to store backups (default: {BACKUP_DIR})"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Don't make actual changes"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Display detailed logs"
    )
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only run the checker, don't apply fixes"
    )
    parser.add_argument(
        "--ide-integration", 
        action="store_true", 
        help="Show information about IDE integration"
    )

    args = parser.parse_args()

    # Handle IDE integration info
    if args.ide_integration:
        setup_ide_integration()
        return 0

    # Require target directory for other operations
    if not args.target_dir:
        parser.error("--target-dir is required unless using --ide-integration")

    try:
        workflow = DocstringWorkflow(
            target_dir=args.target_dir,
            reports_dir=args.reports_dir,
            backups_dir=args.backups_dir,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        if args.check_only:
            success = workflow.check()
        else:
            success = workflow.run_full_workflow()

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Error running docstring workflow: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())