@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - scripts/cross_reference/zz_archive/reports/cross_reference_ultra_report_20250521_000119.md

# Cross-Reference Ultra Report - 20250521_000119
## Performance Metrics
{
  "total_execution_time_sec": 25.14100000000326,
  "total_execution_time_formatted": "25.1 seconds",
  "phases": {
    "initialization": {
      "duration_sec": 0.0,
      "duration_formatted": "0.0 seconds",
      "percentage": 0.0
    },
    "find_target_files": {
      "duration_sec": 0.046999999991385266,
      "duration_formatted": "0.0 seconds",
      "percentage": 0.18694562663131606
    },
    "find_references": {
      "duration_sec": 25.094000000011874,
      "duration_formatted": "25.1 seconds",
      "percentage": 99.81305437336869
    },
    "generate_reports": {
      "duration_sec": 0.0,
      "duration_formatted": "0.0 seconds",
      "percentage": 0.0
    }
  },
  "metrics": {
    "phase_initialization_duration_sec": 0.0,
    "target_files_found_count": 41,
    "phase_find_target_files_duration_sec": 0.047,
    "files_processed_for_references_count": 3,
    "cache_size": 2578,
    "phase_find_references_duration_sec": 25.094
  },
  "file_processing": {
    "count": 7731,
    "total_time": 4.704999999841675,
    "avg_time": 0.0006085887983238488,
    "min_time": 0.0,
    "max_time": 0.0629999999946449
  }
}
## Reference Details (3 files analyzed)
### File: `scripts\cross_reference\temp_test_file_ignore.tmp`
  - No references found or processed.
### File: `scripts\cross_reference\config_ultra.yaml`
  - Found in: `scripts\cross_reference\config_ultra_test.yaml` L2: `# Modified from config_ultra.yaml to test with a small subset`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L471: `### File: `scripts\cross_reference\config_ultra.yaml``
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L472: `- Found in: `scripts\cross_reference\config_ultra_test.yaml` L2: `# Modified from config_ultra.yaml `
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L473: `- Found in: `scripts\cross_reference\file_reference_checker_ultra.py` L15: `- Configuration: ./confi`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L474: `- Found in: `scripts\cross_reference\file_reference_checker_ultra.py` L57: `DEFAULT_CONFIG_ULTRA_PAT`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L478: `- Found in: `scripts\cross_reference\config_ultra.yaml` L9: `file_path: "./cross_reference_ultra_deb`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L479: `- Found in: `scripts\cross_reference\config_ultra.yaml` L52: `- "./scripts/cross_reference/cross_ref`
  - Found in: `scripts\cross_reference\file_reference_checker_ultra.py` L15: `- Configuration: ./config_ultra.yaml`
  - Found in: `scripts\cross_reference\file_reference_checker_ultra.py` L57: `DEFAULT_CONFIG_ULTRA_PATH = Path(__file__).parent / "config_ultra.yaml"`
  - Found in: `scripts\cross_reference\file_reference_checker_ultra.py` L1884: `parser.add_argument("--config", "-c", type=str, default="config_ultra.yaml", help="Path to configura`
### File: `scripts\cross_reference\__pycache__\temp_test_file_excluded.py`
  - Found in: `scripts\cross_reference\checker_debug_output.log` L853: `2025-05-20 22:18:58,640 | INFO | file_reference_checker_windows:260 | Found candidate: scripts\cross`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L206: `### File: `scripts\cross_reference\__pycache__\temp_test_file_excluded.py``
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L208: `- Found in: `scripts\cross_reference\file_reference_report.json` L2586: `"path": "scripts\\cross_ref`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L209: `- Found in: `scripts\cross_reference\file_reference_report.md` L649: `- `scripts\cross_reference\__p`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_235545.md` L48: `### File: `scripts\cross_reference\__pycache__\temp_test_file_excluded.py``
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_235545.md` L50: `- Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_234950.md` L206: `### Fil`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_235545.md` L53: `- Found in: `scripts\cross_reference\file_reference_report.json` L2586: `"path": "scripts\\cross_ref`
  - Found in: `scripts\cross_reference\cross_reference_ultra_report_20250520_235545.md` L54: `- Found in: `scripts\cross_reference\file_reference_report.md` L649: `- `scripts\cross_reference\__p`
  - Found in: `scripts\cross_reference\file_reference_report.json` L2586: `"path": "scripts\\cross_reference\\__pycache__\\temp_test_file_excluded.py",`
  - Found in: `scripts\cross_reference\file_reference_report.md` L649: `- `scripts\cross_reference\__pycache__\temp_test_file_excluded.py``