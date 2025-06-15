"""EGOS File Reference Checker Ultra - Subsystem Integration Package

This package provides integration between the File Reference Checker Ultra
and core EGOS subsystems (ETHIK, KOIOS, and NEXUS).

@references: <!-- TO_BE_REPLACED -->, KOIOS documentation standards
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

from .integration_manager import IntegrationManager
from .ethik_validator import ETHIKValidator
from .koios_standards import KOIOSStandardsChecker
from .nexus_dependency import NEXUSDependencyMapper

__all__ = [
    'IntegrationManager',
    'ETHIKValidator',
    'KOIOSStandardsChecker',
    'NEXUSDependencyMapper',
]