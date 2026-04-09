/**
 * EGOS Report SSOT v2.0.0 — Validator
 * 
 * Validates reports against the canonical schema.
 * Provides detailed error messages for debugging.
 * 
 * @see docs/REPORT_SSOT.md
 */

import { ReportSchema, ValidationStatus } from './schema';
import type { Report } from './schema';
import { ZodError } from 'zod';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  report?: Report;
  metadata: {
    validated_at: string;
    validator_version: string;
    schema_version: string;
  };
}

/**
 * Validate a report against the canonical schema
 */
export function validateReport(data: unknown): ValidationResult {
  const result: ValidationResult = {
    valid: false,
    errors: [],
    warnings: [],
    metadata: {
      validated_at: new Date().toISOString(),
      validator_version: '1.0.0',
      schema_version: '2.0.0'
    }
  };

  try {
    const parsed = ReportSchema.parse(data);
    result.valid = true;
    result.report = parsed;

    // Additional semantic validation
    validateSemantics(parsed, result);

  } catch (error) {
    if (error instanceof ZodError) {
      result.errors = error.issues.map(e =>
        `${(e.path as (string | number)[]).join('.')}: ${e.message}`
      );
    } else {
      result.errors.push(String(error));
    }
  }

  return result;
}

/**
 * Validate report semantics beyond schema compliance
 */
function validateSemantics(report: Report, result: ValidationResult): void {
  // Check for required sections based on report type
  const requiredSections = getRequiredSections(report.type);
  const presentSections = new Set(report.sections.map(s => s.type));

  for (const section of requiredSections) {
    if (!presentSections.has(section)) {
      result.warnings.push(`Missing recommended section: ${section}`);
    }
  }

  // Check timestamp ordering
  if (report.updated_at < report.created_at) {
    result.errors.push('updated_at must be >= created_at');
    result.valid = false;
  }

  // Check for empty content
  const emptySections = report.sections.filter(s => !s.content.trim());
  if (emptySections.length > 0) {
    result.warnings.push(
      `Empty content in sections: ${emptySections.map(s => s.title).join(', ')}`
    );
  }

  // Validate insight references
  if (report.insights) {
    const insightIds = new Set(report.insights.map(i => i.id));
    for (const section of report.sections) {
      if (section.insights) {
        for (const ref of section.insights) {
          if (!insightIds.has(ref)) {
            result.warnings.push(`Section "${section.title}" references unknown insight: ${ref}`);
          }
        }
      }
    }
  }
}

/**
 * Get required sections for each report type
 */
type SectionType = 'executive_summary' | 'methodology' | 'findings' | 'recommendations' | 'appendix' | 'metadata';

function getRequiredSections(type: string): SectionType[] {
  const base: SectionType[] = ['metadata'];
  
  switch (type) {
    case 'analytics':
    case 'intelligence':
    case 'research':
      return [...base, 'executive_summary' as SectionType, 'methodology' as SectionType, 'findings' as SectionType];
    case 'audit':
    case 'compliance':
      return [...base, 'executive_summary' as SectionType, 'findings' as SectionType, 'recommendations' as SectionType];
    case 'incident':
      return [...base, 'executive_summary' as SectionType, 'findings' as SectionType];
    default:
      return [...base, 'executive_summary' as SectionType];
  }
}

/**
 * Check if a report passes validation and return detailed info
 */
export function isValidReport(data: unknown): { valid: boolean; errors: string[] } {
  const result = validateReport(data);
  return {
    valid: result.valid && result.errors.length === 0,
    errors: [...result.errors, ...result.warnings]
  };
}

/**
 * Convert a legacy report format to canonical format
 */
export function migrateLegacyReport(legacy: Record<string, any>): ValidationResult {
  // Basic migration logic for common legacy formats
  const migrated = {
    id: legacy.id || crypto.randomUUID(),
    type: legacy.type || 'technical',
    version: '2.0.0',
    title: legacy.title || legacy.name || 'Untitled Report',
    description: legacy.description || legacy.summary,
    created_at: legacy.created_at || legacy.date || new Date().toISOString(),
    updated_at: legacy.updated_at || legacy.date || new Date().toISOString(),
    authors: legacy.authors || [{
      id: 'legacy',
      name: legacy.author || 'Unknown',
      role: 'author'
    }],
    sections: legacy.sections || [{
      type: 'executive_summary',
      title: 'Summary',
      content: legacy.content || legacy.body || '',
      order: 0
    }],
    validation: {
      status: 'draft' as ValidationStatus,
      validated_at: undefined,
      validated_by: undefined
    }
  };

  return validateReport(migrated);
}
