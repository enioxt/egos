#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# Last Modified: 2025-05-27

import os
import sys
import traceback

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting import tests...")

# Try individual imports to isolate the problematic one
try:
    print("Testing windsurf_memory_adapter imports...")
    from memory.windsurf_memory_adapter import WindsurfMemoryAdapter, LocalStorageBackend, PrivacySensitivity
    print("✅ Successful")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()

try:
    print("\nTesting windsurf_api_backend imports...")
    from memory.windsurf_api_backend import WindsurfAPIBackend
    print("✅ Successful")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()

try:
    print("\nTesting atrian_windsurf_adapter imports...")
    from atrian_windsurf_adapter import ATRiANWindsurfAdapter, WindsurfOperationType
    print("✅ Successful")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    traceback.print_exc()

print("\nImport tests completed.")