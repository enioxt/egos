/**
 * EGOS-002.2: Audit Logger Interface + Console Implementation
 * 
 * Provides audit trail functionality for activation requests.
 * Currently implements console logging; can be extended for PostgreSQL, file, cloud storage.
 */

import { z } from 'zod';
import type { Identity } from '@egos/core';

/**
 * AuditEntry — Immutable record of an activation event
 * 
 * @field id - Unique UUID for this audit entry
 * @field timestamp - When the event occurred (ISO 8601)
 * @field identity - The identity that made the request
 * @field action - The action attempted (read, execute, write, deploy)
 * @field resource - The resource being accessed
 * @field result - Whether the action was allowed or denied
 * @field reasoning - Why the decision was made
 * @field context - Optional additional context (IP, user agent, etc.)
 */
export interface AuditEntry {
  id: string;
  timestamp: Date;
  identity: Identity;
  action: string;
  resource: string;
  result: 'allowed' | 'denied';
  reasoning: string;
  context?: Record<string, unknown>;
}

/**
 * Zod schema for AuditEntry validation
 */
export const AuditEntrySchema = z.object({
  id: z.string().uuid('id must be a valid UUID'),
  timestamp: z.date(),
  identity: z.object({
    userId: z.string(),
    source: z.string(),
    scopes: z.array(z.string()),
    token: z.string().optional(),
    expiresAt: z.date().optional(),
    metadata: z.record(z.unknown()).optional(),
  }),
  action: z.string(),
  resource: z.string(),
  result: z.enum(['allowed', 'denied']),
  reasoning: z.string(),
  context: z.record(z.unknown()).optional(),
});

/**
 * AuditLogger interface — Abstract contract for audit implementations
 */
export interface AuditLogger {
  /**
   * Log an audit entry
   * @param entry The audit entry to log
   * @returns Promise that resolves when logging is complete
   */
  log(entry: AuditEntry): Promise<void>;

  /**
   * Retrieve audit entries (optional, implementation-specific)
   * @param filter Optional filter criteria
   * @returns Promise resolving to matching entries
   */
  query?(filter?: Record<string, unknown>): Promise<AuditEntry[]>;
}

/**
 * ConsoleAuditLogger — Reference implementation logging to console
 * 
 * Outputs structured JSON for easy parsing by log aggregation tools.
 * Production use: switch to PostgreSQL, CloudWatch, or similar.
 */
export class ConsoleAuditLogger implements AuditLogger {
  private entries: AuditEntry[] = [];

  async log(entry: AuditEntry): Promise<void> {
    // Validate entry structure
    AuditEntrySchema.parse(entry);

    // Store in memory for potential querying
    this.entries.push(entry);

    // Format for console output
    const logEntry = {
      timestamp: entry.timestamp.toISOString(),
      auditId: entry.id,
      userId: entry.identity.userId,
      source: entry.identity.source,
      action: entry.action,
      resource: entry.resource,
      result: entry.result,
      reasoning: entry.reasoning,
      scopes: entry.identity.scopes,
      context: entry.context,
    };

    // Output based on result
    if (entry.result === 'allowed') {
      console.log('[AUDIT-ALLOWED]', JSON.stringify(logEntry, null, 2));
    } else {
      console.warn('[AUDIT-DENIED]', JSON.stringify(logEntry, null, 2));
    }
  }

  /**
   * Query audit entries by filter
   * Useful for testing and local debugging
   */
  async query(filter?: Record<string, unknown>): Promise<AuditEntry[]> {
    if (!filter) {
      return this.entries;
    }

    return this.entries.filter((entry) => {
      for (const [key, value] of Object.entries(filter)) {
        if (key === 'userId' && entry.identity.userId !== value) return false;
        if (key === 'source' && entry.identity.source !== value) return false;
        if (key === 'action' && entry.action !== value) return false;
        if (key === 'resource' && entry.resource !== value) return false;
        if (key === 'result' && entry.result !== value) return false;
      }
      return true;
    });
  }

  /**
   * Get all audit entries (for testing)
   */
  getEntries(): AuditEntry[] {
    return [...this.entries];
  }

  /**
   * Clear audit entries (for testing)
   */
  clear(): void {
    this.entries = [];
  }
}

/**
 * Type exports
 */
export type { AuditEntry, AuditLogger };
