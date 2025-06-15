"""Cross-Reference Validator Package

This package provides validation components for the EGOS Cross-Reference System,
including orphaned file detection and unified validation interfaces.

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

# Import key classes for easier access
try:
    from .orphaned_file_detector import OrphanedFileDetector, OrphanedFileReport
    from .unified_validator import UnifiedValidator, ValidationConfig
    
    __all__ = [
        'OrphanedFileDetector',
        'OrphanedFileReport',
        'UnifiedValidator',
        'ValidationConfig'
    ]
except ImportError:
    # Handle the case where some modules might not be available yet
    pass