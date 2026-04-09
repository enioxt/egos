/**
 * EGOS Report SSOT v2.0.0 — Canonical Schema
 * 
 * This module defines the canonical report structure used across all EGOS
 * repositories: egos, 852, br-acc, egos-inteligencia.
 * 
 * @see docs/REPORT_SSOT.md for full specification
 * @version 2.0.0
 */

import { z } from 'zod';

// ============================================================================
// Enums
// ============================================================================

export const ReportType = z.enum([
  'analytics',
  'audit',
  'compliance',
  'dissemination',
  'incident',
  'intelligence',
  'research',
  'strategy',
  'technical'
]);

export const ReportSectionType = z.enum([
  'executive_summary',
  'methodology',
  'findings',
  'recommendations',
  'appendix',
  'metadata'
]);

export const ReportFormat = z.enum([
  'markdown',
  'json',
  'pdf',
  'docx',
  'html'
]);

export const ValidationStatus = z.enum([
  'draft',
  'pending_review',
  'validated',
  'rejected'
]);

// ============================================================================
// Sub-schemas
// ============================================================================

export const ReportSource = z.object({
  type: z.enum(['file', 'url', 'database', 'api', 'manual']),
  path: z.string(),
  hash: z.string().optional(), // SHA-256 for provenance
  collected_at: z.string().datetime().optional(),
  verified_by: z.string().optional()
});

export const ReportInsight = z.object({
  id: z.string().uuid(),
  type: z.enum(['pattern', 'anomaly', 'opportunity', 'risk', 'trend']),
  description: z.string(),
  evidence: z.array(ReportSource),
  confidence: z.number().min(0).max(1),
  related_insights: z.array(z.string().uuid()).optional()
});

export const ReportAuthor = z.object({
  id: z.string(),
  name: z.string(),
  role: z.string(),
  agent_id: z.string().optional(), // For AI-generated reports
  signature: z.string().optional() // Commit hash or signature
});

export const ReportSection = z.object({
  type: ReportSectionType,
  title: z.string(),
  content: z.string(),
  order: z.number().int().min(0),
  sources: z.array(ReportSource).optional(),
  insights: z.array(z.string().uuid()).optional() // References to insights
});

export const DisseminationRecord = z.object({
  channel: z.enum(['github', 'telegram', 'email', 'webhook', 'mcp']),
  target: z.string(), // URL, chat ID, etc.
  status: z.enum(['pending', 'sent', 'delivered', 'failed']),
  sent_at: z.string().datetime().optional(),
  delivered_at: z.string().datetime().optional(),
  error: z.string().optional()
});

// ============================================================================
// Main Report Schema
// ============================================================================

export const ReportSchema = z.object({
  // Core identification
  id: z.string().uuid(),
  type: ReportType,
  version: z.string().default('2.0.0'),
  
  // Metadata
  title: z.string().min(5).max(200),
  description: z.string().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  
  // Authorship
  authors: z.array(ReportAuthor).min(1),
  
  // Content
  sections: z.array(ReportSection),
  insights: z.array(ReportInsight).optional(),
  
  // Provenance
  sources: z.array(ReportSource).optional(),
  
  // Validation
  validation: z.object({
    status: ValidationStatus,
    validated_by: z.string().optional(),
    validated_at: z.string().datetime().optional(),
    validator_version: z.string().optional()
  }).optional(),
  
  // Dissemination
  dissemination: z.object({
    records: z.array(DisseminationRecord).optional(),
    auto_disseminate: z.boolean().default(false),
    channels: z.array(z.enum(['github', 'telegram', 'email', 'webhook', 'mcp'])).optional()
  }).optional(),
  
  // Extensions (repository-specific)
  extensions: z.record(z.string(), z.any()).optional()
});

// ============================================================================
// Type Exports
// ============================================================================

export type ReportType = z.infer<typeof ReportType>;
export type ReportSectionType = z.infer<typeof ReportSectionType>;
export type ReportFormat = z.infer<typeof ReportFormat>;
export type ValidationStatus = z.infer<typeof ValidationStatus>;
export type ReportSource = z.infer<typeof ReportSource>;
export type ReportInsight = z.infer<typeof ReportInsight>;
export type ReportAuthor = z.infer<typeof ReportAuthor>;
export type ReportSection = z.infer<typeof ReportSection>;
export type DisseminationRecord = z.infer<typeof DisseminationRecord>;
export type Report = z.infer<typeof ReportSchema>;
