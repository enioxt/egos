#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Directory Unification Tool Package

This package provides modules for identifying, analyzing, and consolidating
related content across the EGOS system, following EGOS Core Principles.

Author: Cascade
Date: 2025-05-23
Version: 1.0.0
References:
    - C:\EGOS\docs\tools\directory_unification_tool_prd.md
    - C:\EGOS\scripts\maintenance\directory_unification\directory_unification_tool.py
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

from .directory_unification_tool import DirectoryUnificationTool
from .content_discovery import ContentDiscovery
from .cross_reference_analyzer import CrossReferenceAnalyzer
from .consolidation_planner import ConsolidationPlanner
from .migration_executor import MigrationExecutor
from .report_generator import ReportGenerator
from .utils import setup_logger, print_banner, Timer, format_path, human_readable_size

__all__ = [
    'DirectoryUnificationTool',
    'ContentDiscovery',
    'CrossReferenceAnalyzer',
    'ConsolidationPlanner',
    'MigrationExecutor',
    'ReportGenerator',
    'setup_logger',
    'print_banner',
    'Timer',
    'format_path',
    'human_readable_size'
]