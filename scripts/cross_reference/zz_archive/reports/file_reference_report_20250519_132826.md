@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - scripts/cross_reference/zz_archive/reports/file_reference_report_20250519_132826.md

# File Reference Checker Report

- **Report Generated At:** 2025-05-19T13:28:26.563052
- **Project Base Path:** `C:\EGOS`
- **Time Window (Hours):** 2
- **Target Extensions Scanned:** `.md, .ts, .css, .yaml, .js, .py, .yml, .json, .html`
- **Scan Directories Config:** `src, docs`
- **Reference Search Dirs:** `README.md, docs/, scripts/`
- **Reference Search Exts:** `.md, .ts, .css, .txt, .yaml, .js, .py, .yml, .json, .html`
- **Files Processed:** 4

## Candidate Files & Their References:

### `docs\new_module_notes.md`
**Found 3 reference(s):**
- In: `scripts\another_script.py` (Line: 14)
  ```
  # Text reference to new_module_notes.md
  ```
- In: `scripts\another_script.py` (Line: 15)
  ```
  # This script complements new_module_notes.md for extended details.
  ```
- In: `scripts\another_script.py` (Line: 16)
  ```
  print("Checking notes in new_module_notes.md")
  ```

### `docs\reference\file_reference_checker_optimized.md`
**Found 1 reference(s):**
- In: `scripts\cross_reference\file_reference_checker_optimized.py` (Line: 30)
  ```
  - Main Documentation: ../../../docs/reference/file_reference_checker_optimized.md (to be created/updated)
  ```

### `src\new_module.py`
**Found 7 reference(s):**
- In: `README.md` (Line: 3)
  ```
  See documentation for new_module.py.
  ```
- In: `docs\new_module_notes.md` (Line: 2)
  ```
  <!-- Intentionally no direct reference to new_module.py here for testing. -->
  ```
- In: `scripts\another_script.py` (Line: 4)
  ```
  # Reference to new_module.py
  ```
- In: `scripts\another_script.py` (Line: 6)
  ```
  # For testing, let's assume a simple import if new_module.py is in src
  ```
- In: `scripts\another_script.py` (Line: 7)
  ```
  # and the checker is run from a context where src is importable or patterns match `src/new_module.py`
  ```
- In: `scripts\another_script.py` (Line: 11)
  ```
  # The presence of the string 'new_module.py' or 'src.new_module' will be searched by patterns
  ```
- In: `scripts\another_script.py` (Line: 12)
  ```
  # Example: import src.new_module
  ```

### `src\old_module.py`
  - **No references found - WARNING: File might be undocumented or orphaned.** (<!-- TO_BE_REPLACED -->MEMORY[3bae44d3...])

