#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGOS File Duplication Cross-Reference Integration

This module provides integration between the File Duplication Auditor and
the EGOS Cross-Reference system. It enables updating cross-references when
files are moved to canonical locations and ensures references remain valid
after cleanup operations.

Part of the EGOS File Organization and Management Initiative.

Author: EGOS Development Team
Created: 2025-05-22
Version: 1.0.0

@references:
- C:\EGOS\WORK_2025_05_22_file_duplication_management.md
- C:\EGOS\scripts\cross_reference\cross_reference_validator.py
- C:\EGOS\scripts\maintenance\file_duplication_auditor.py
"""
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
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Add parent directory to path to allow imports from sibling modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# EGOS imports
from scripts.cross_reference.cross_reference_validator import CrossReferenceValidator
from scripts.cross_reference.optimized_reference_fixer import ReferenceUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("duplication_xref_integration")

class DuplicationXRefIntegration:
    """
    Integration class for connecting File Duplication Auditor with Cross-Reference system.
    
    This class provides methods to update cross-references when files are moved to
    canonical locations and ensures references remain valid after cleanup operations.
    """
    
    def __init__(self, base_path: Path = None):
        """
        Initialize the integration module.
        
        Args:
            base_path: Base path of the EGOS project
        """
        self.base_path = base_path or Path.cwd()
        self.validator = CrossReferenceValidator(self.base_path)
        self.updater = ReferenceUpdater(self.base_path)
    
    def update_references_for_canonical_files(self, duplicate_report_path: Path) -> Dict[str, Any]:
        """
        Update cross-references to point to canonical files.
        
        Args:
            duplicate_report_path: Path to the duplicate files report (JSON format)
            
        Returns:
            Dictionary with update statistics
        """
        logger.info(f"Updating cross-references based on duplicate report: {duplicate_report_path}")
        
        # Load duplicate report
        with open(duplicate_report_path, 'r', encoding='utf-8') as f:
            duplicate_data = json.load(f)
        
        # Extract duplicate groups
        duplicate_groups = duplicate_data.get('duplicate_groups', [])
        if not duplicate_groups:
            logger.warning("No duplicate groups found in the report")
            return {"status": "error", "message": "No duplicate groups found"}
        
        # Extract canonical proposals if available
        canonical_proposals = duplicate_data.get('canonical_proposals', {})
        
        # Track statistics
        stats = {
            "total_groups": len(duplicate_groups),
            "updated_references": 0,
            "failed_updates": 0,
            "skipped_groups": 0,
            "canonical_files_identified": 0
        }
        
        # Process each group
        for group_idx, group in enumerate(duplicate_groups):
            group_id = str(group_idx)
            
            # Get canonical file from group or proposals
            canonical_path = None
            
            # First check if there's a canonical file in the group
            if 'canonical_file' in group and group['canonical_file']:
                canonical_path = group['canonical_file'].get('path')
                stats["canonical_files_identified"] += 1
            
            # If not, check canonical proposals
            elif group_id in canonical_proposals:
                proposal = canonical_proposals[group_id]
                canonical_path = proposal.get('canonical_path')
                stats["canonical_files_identified"] += 1
            if not canonical_path:
                logger.warning(f"No canonical path found for group {group_id}")
                stats["skipped_groups"] += 1
                continue
            
            # Get all duplicates for this group
            group_data = None
            for group in duplicate_data.get('groups', []):
                if str(group.get('id', '')) == group_id:
                    group_data = group
                    break
            
            if not group_data:
                logger.warning(f"Group data not found for group {group_id}")
                stats["skipped_groups"] += 1
                continue
            
            # Update references for each duplicate
            for file_info in group_data.get('files', []):
                file_path = file_info.get('path')
                if file_path == canonical_path:
                    # Skip the canonical file
                    continue
                
                # Update references from duplicate to canonical
                try:
                    update_result = self.updater.update_references(
                        old_path=file_path,
                        new_path=canonical_path,
                        dry_run=False
                    )
                    stats["updated_references"] += update_result.get('updated_count', 0)
                except Exception as e:
                    logger.error(f"Error updating references for {file_path}: {str(e)}")
                    stats["failed_updates"] += 1
        
        logger.info(f"Reference update complete. Updated {stats['updated_references']} references across {stats['total_groups']} groups.")
        return stats
    
    def validate_references_after_cleanup(self, cleanup_log_path: Path) -> Dict[str, Any]:
        """
        Validate cross-references after cleanup operations.
        
        Args:
            cleanup_log_path: Path to the cleanup log file
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating cross-references after cleanup: {cleanup_log_path}")
        
        # Load cleanup log
        with open(cleanup_log_path, 'r', encoding='utf-8') as f:
            cleanup_data = json.load(f)
        
        # Extract removed files
        removed_files = cleanup_data.get('removed_files', [])
        if not removed_files:
            logger.warning("No removed files found in the cleanup log")
            return {"status": "warning", "message": "No removed files found"}
        
        # Validate references
        validation_results = self.validator.validate_references()
        
        # Extract broken references
        broken_references = validation_results.get('broken_references', [])
        
        # Check if any broken references point to removed files
        cleanup_related_issues = []
        for ref in broken_references:
            target = ref.get('target')
            if any(removed == target for removed in removed_files):
                cleanup_related_issues.append(ref)
        
        return {
            "status": "success",
            "total_removed_files": len(removed_files),
            "total_broken_references": len(broken_references),
            "cleanup_related_issues": len(cleanup_related_issues),
            "issues": cleanup_related_issues
        }
        
    def generate_canonical_proposals(self, duplicate_report_path: Path) -> Dict[str, Any]:
        """
        Generate proposals for canonical file locations based on duplication report.
        
        Args:
            duplicate_report_path: Path to the duplicate files report (JSON format)
            
        Returns:
            Dictionary with canonical proposals
        """
        logger.info(f"Generating canonical file proposals from: {duplicate_report_path}")
        
        # Load duplicate report
        with open(duplicate_report_path, 'r', encoding='utf-8') as f:
            duplicate_data = json.load(f)
        
        # Extract duplicate groups
        duplicate_groups = duplicate_data.get('duplicate_groups', [])
        if not duplicate_groups:
            logger.warning("No duplicate groups found in the report")
            return {"status": "error", "message": "No duplicate groups found"}
        
        # Generate proposals
        proposals = {}
        
        for group_idx, group in enumerate(duplicate_groups):
            group_id = str(group_idx)
            files = group.get('files', [])
            
            if len(files) <= 1:
                continue
                
            # Score each file to determine the best canonical location
            scored_files = []
            for file in files:
                path = file.get('path', '')
                score = self._score_file_for_canonical(path)
                scored_files.append((path, score))
            
            # Sort by score (higher is better)
            scored_files.sort(key=lambda x: x[1], reverse=True)
            
            # Create proposal
            if scored_files:
                best_path, best_score = scored_files[0]
                proposals[group_id] = {
                    'canonical_path': best_path,
                    'score': best_score,
                    'alternatives': [path for path, _ in scored_files[1:]]
                }
        
        return {
            "status": "success",
            "total_groups": len(duplicate_groups),
            "proposals_generated": len(proposals),
            "proposals": proposals
        }
    
    def _score_file_for_canonical(self, file_path: str) -> float:
        """
        Score a file path to determine if it's a good canonical location.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Score value (higher is better)
        """
        # Start with base score
        score = 10.0
        
        # Convert to lowercase for case-insensitive matching
        path_lower = file_path.lower()
        
        # Prefer files in standard documentation directories
        if '/docs/' in path_lower or '\\docs\\' in path_lower:
            score += 5.0
        
        # Penalize files in archive directories
        archive_patterns = ['archive', 'backup', 'old', 'temp', 'zz_']
        for pattern in archive_patterns:
            if pattern in path_lower:
                score -= 3.0
        
        # Prefer files with shorter paths (more accessible)
        score -= len(file_path) * 0.01
        
        # Prefer files in standard locations
        standard_locations = [
            'docs/guides', 'docs/reference', 'docs/standards',
            'docs\\guides', 'docs\\reference', 'docs\\standards'
        ]
        for location in standard_locations:
            if location in path_lower:
                score += 2.0
                
        return max(0.0, score)  # Ensure score is not negative

def main():
    """
    Main entry point for the script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="EGOS File Duplication Cross-Reference Integration")
    
    # Add arguments
    parser.add_argument('--update-references', type=str, help='Update cross-references based on duplicate report')
    parser.add_argument('--validate-cleanup', type=str, help='Validate references after cleanup')
    parser.add_argument('--generate-proposals', type=str, help='Generate canonical file proposals from duplicate report')
    parser.add_argument('--base-path', type=str, default=os.getcwd(), help='Base path of the EGOS project')
    parser.add_argument('--output', type=str, help='Output file for results (JSON format)')
    
    args = parser.parse_args()
    
    # Create integration object
    integration = DuplicationXRefIntegration(Path(args.base_path))
    
    results = None
    
    # Update references
    if args.update_references:
        results = integration.update_references_for_canonical_files(Path(args.update_references))
    
    # Validate cleanup
    elif args.validate_cleanup:
        results = integration.validate_references_after_cleanup(Path(args.validate_cleanup))
    
    # Generate proposals
    elif args.generate_proposals:
        results = integration.generate_canonical_proposals(Path(args.generate_proposals))
    
    else:
        parser.print_help()
        return
    
    # Print or save results
    if results:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()