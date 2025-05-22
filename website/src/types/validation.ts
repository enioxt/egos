/**
 * @file validation.ts
 * @description TypeScript type definitions for the cross-reference validation system
 * @module types/validation
 * @version 0.1.0
 * @date 2025-05-21
 * @license MIT
 *
 * @references
 * - mdc:scripts/cross_reference/validator/validation_models.py (Python validation models)
 * - mdc:website/src/lib/api/validationRunner.ts (API bridge)
 * - mdc:website/src/lib/api/dashboardClient.ts (API client)
 */

/**
 * Configuration for a validation run
 */
export interface ValidationConfig {
  /** Whether to check for orphaned files */
  orphaned_files: boolean;
  /** Whether to check for broken references */
  reference_check: boolean;
  /** Maximum number of files to check (optional) */
  max_files?: number;
  /** Patterns to include in validation (optional) */
  include_patterns?: string[];
  /** Patterns to exclude from validation (optional) */
  exclude_patterns?: string[];
  /** Path to save the report (optional) */
  report_path?: string;
}

/**
 * Status of the validation service
 */
export interface ValidationStatus {
  /** Whether validation is currently running */
  running: boolean;
  /** Timestamp of the latest validation run (ISO format) */
  latest_timestamp: string | null;
  /** Timestamps of scheduled validation runs (ISO format) */
  scheduled_runs: string[];
}

/**
 * Information about an orphaned file
 */
export interface OrphanedFile {
  /** Path to the orphaned file */
  file_path: string;
  /** Type of the file (e.g., markdown, python) */
  file_type: string;
  /** Last modified timestamp (Unix timestamp) */
  last_modified: number;
  /** Size of the file in bytes */
  size: number;
  /** Number of outgoing references in the file */
  outgoing_references: number;
  /** Priority level of the orphaned file */
  priority: 'high' | 'medium' | 'low';
}

/**
 * Report on orphaned files
 */
export interface OrphanedFilesReport {
  /** List of orphaned files */
  orphaned_files: OrphanedFile[];
  /** Total number of files scanned */
  total_files_scanned: number;
  /** Total number of orphaned files found */
  total_orphaned_files: number;
  /** Number of high priority orphaned files */
  high_priority_count: number;
  /** Number of medium priority orphaned files */
  medium_priority_count: number;
  /** Number of low priority orphaned files */
  low_priority_count: number;
  /** Execution time in seconds */
  execution_time: number;
}

/**
 * Information about a reference issue
 */
export interface ReferenceIssue {
  /** Path to the source file containing the reference */
  source_file: string;
  /** Path to the target file being referenced */
  target_file: string;
  /** Line number where the reference is found */
  line_number: number;
  /** Context surrounding the reference */
  context: string;
  /** Type of issue (e.g., broken, invalid) */
  issue_type: string;
  /** Severity of the issue */
  severity: 'high' | 'medium' | 'low';
  /** Description of the issue */
  message: string;
}

/**
 * Report on reference checking
 */
export interface ReferenceCheckReport {
  /** Total number of files checked */
  total_files_checked: number;
  /** Total number of references found */
  total_references_found: number;
  /** Number of valid references */
  valid_references: number;
  /** Number of invalid references */
  invalid_references: number;
  /** Number of issues found */
  issues_found: number;
  /** List of reference issues */
  issues: ReferenceIssue[];
  /** Execution time in seconds */
  execution_time: number;
}

/**
 * Unified validation report combining orphaned files and reference checking
 */
export interface UnifiedValidationReport {
  /** Report on orphaned files */
  orphaned_files: OrphanedFilesReport;
  /** Report on reference checking */
  references: ReferenceCheckReport;
  /** Total execution time in seconds */
  execution_time: number;
  /** Timestamp of the validation run (ISO format) */
  timestamp: string;
}

/**
 * Schedule configuration for a validation run
 */
export interface ValidationSchedule {
  /** When to run the validation (ISO format) */
  schedule_time: string;
  /** Validation configuration */
  config: ValidationConfig;
}

/**
 * Response from the API when triggering a validation run
 */
export interface TriggerResponse {
  /** Status of the operation */
  status: string;
  /** Human-readable message */
  message: string;
  /** Timestamp of the request */
  timestamp: string;
}

/**
 * Response from the API when scheduling a validation run
 */
export interface ScheduleResponse {
  /** Status of the operation */
  status: string;
  /** Scheduled time (ISO format) */
  schedule_time: string;
  /** Human-readable message */
  message: string;
}

/**
 * Response from the API when canceling a scheduled validation run
 */
export interface CancelResponse {
  /** Status of the operation */
  status: string;
  /** Scheduled time that was canceled (ISO format) */
  schedule_time: string;
  /** Human-readable message */
  message: string;
}
