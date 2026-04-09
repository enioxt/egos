/**
 * EGOS Report Standard v1.0.0
 * 
 * Canonical implementation of REPORT_SSOT v2.0.0
 * 
 * @example
 * ```typescript
 * import { validateReport, ReportSchema } from '@egos/report-standard';
 * 
 * const result = validateReport(myReport);
 * if (result.valid) {
 *   console.log('Report is valid!');
 * }
 * ```
 */

// Schema exports
export {
  ReportSchema,
  ReportType,
  ReportSectionType,
  ReportFormat,
  ValidationStatus,
  ReportSource,
  ReportInsight,
  ReportAuthor,
  ReportSection,
  DisseminationRecord,
} from './schema';

export type {
  Report,
  ReportType as ReportTypeEnum,
  ReportFormat as ReportFormatEnum,
  ValidationStatus as ValidationStatusEnum,
  ReportSource as ReportSourceType,
  ReportInsight as ReportInsightType,
  ReportAuthor as ReportAuthorType,
  ReportSection as ReportSectionInterface,
  DisseminationRecord as DisseminationRecordType,
} from './schema';

// Validator exports
export {
  validateReport,
  isValidReport,
  migrateLegacyReport,
  type ValidationResult,
} from './validator';

// Version info
export const VERSION = '1.0.0';
export const SCHEMA_VERSION = '2.0.0';
