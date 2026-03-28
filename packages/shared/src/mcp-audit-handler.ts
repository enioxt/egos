/**
 * EGOS-004.4: MCP Audit Handler
 *
 * Middleware that logs all MCP server calls with:
 * - Timestamp, MCP server ID, identity
 * - Scopes requested vs. granted
 * - Tool/action called and result
 * - Audit trail for compliance
 */

import { v4 as uuidv4 } from 'uuid';
import type { AuditEntry, AuditLogger } from '@egos/audit';
import type { Identity } from '@egos/core';
import { ConsoleAuditLogger } from '@egos/audit';

/**
 * MCP Call Event — Details of an MCP server invocation
 */
export interface MCPCallEvent {
  id: string;
  timestamp: Date;
  mcpServerId: string;
  mcpServerName: string;
  identity: Identity;
  scopes: {
    requested: string[];
    granted: string[];
  };
  tool: {
    name: string;
    args?: Record<string, unknown>;
  };
  result: {
    status: 'success' | 'denied' | 'error';
    message?: string;
    errorCode?: string;
    executionTimeMs?: number;
  };
  context?: Record<string, unknown>;
}

/**
 * MCP Audit Handler — Logs all MCP calls with audit trail
 *
 * Integrates with ConsoleAuditLogger (EGOS-002) to maintain
 * compliance audit trail for all MCP operations.
 */
export class MCPAuditHandler {
  private auditLogger: AuditLogger;
  private mcpScopes: Map<string, string[]>; // MCP ID -> allowed scopes

  constructor(
    auditLogger: AuditLogger = new ConsoleAuditLogger(),
    mcpScopes: Map<string, string[]> = new Map()
  ) {
    this.auditLogger = auditLogger;
    this.mcpScopes = mcpScopes;
  }

  /**
   * Register MCP server with allowed scopes
   * @param mcpId - MCP server ID (e.g., "supabase-db")
   * @param scopes - Array of allowed scopes for this MCP
   */
  registerMCP(mcpId: string, scopes: string[]): void {
    this.mcpScopes.set(mcpId, scopes);
  }

  /**
   * Check if an MCP has permission for requested scopes
   * @param mcpId - MCP server ID
   * @param requestedScopes - Scopes being requested
   * @returns Array of scopes actually granted
   */
  private validateScopes(mcpId: string, requestedScopes: string[]): string[] {
    const allowedScopes = this.mcpScopes.get(mcpId) || [];
    return requestedScopes.filter(scope => allowedScopes.includes(scope));
  }

  /**
   * Log an MCP call (success path)
   * @param event - MCP call event details
   */
  async logCall(event: MCPCallEvent): Promise<void> {
    // Validate scopes
    const grantedScopes = this.validateScopes(event.mcpServerId, event.scopes.requested);
    const allScopesGranted =
      grantedScopes.length === event.scopes.requested.length &&
      grantedScopes.length > 0;

    // Create audit entry
    const auditEntry: AuditEntry = {
      id: uuidv4(),
      timestamp: event.timestamp,
      identity: event.identity,
      action: `mcp:${event.mcpServerName}:${event.tool.name}`,
      resource: `mcp:${event.mcpServerId}`,
      result: allScopesGranted && event.result.status === 'success' ? 'allowed' : 'denied',
      reasoning: this.buildReasoning(event, allScopesGranted, grantedScopes),
      context: {
        mcpServerId: event.mcpServerId,
        mcpServerName: event.mcpServerName,
        toolName: event.tool.name,
        toolArgs: event.tool.args,
        scopesRequested: event.scopes.requested,
        scopesGranted: grantedScopes,
        resultStatus: event.result.status,
        resultMessage: event.result.message,
        executionTimeMs: event.result.executionTimeMs,
        ...event.context
      }
    };

    // Log to audit system
    await this.auditLogger.log(auditEntry);
  }

  /**
   * Build human-readable reasoning for audit log
   */
  private buildReasoning(
    event: MCPCallEvent,
    allScopesGranted: boolean,
    grantedScopes: string[]
  ): string {
    if (!allScopesGranted) {
      const denied = event.scopes.requested.filter(s => !grantedScopes.includes(s));
      return `Scope check failed. Requested: [${event.scopes.requested.join(', ')}]. Denied: [${denied.join(', ')}]`;
    }

    if (event.result.status === 'denied') {
      return event.result.message || 'MCP call denied by policy';
    }

    if (event.result.status === 'error') {
      return `MCP error: ${event.result.message || event.result.errorCode || 'unknown'}`;
    }

    return `MCP call allowed. Scopes: [${grantedScopes.join(', ')}]. Tool: ${event.tool.name}`;
  }

  /**
   * Log MCP call with automatic event capture
   * Convenience method that wraps an async MCP call
   */
  async trackMCPCall<T>(
    mcpServerId: string,
    mcpServerName: string,
    identity: Identity,
    tool: { name: string; args?: Record<string, unknown> },
    requestedScopes: string[],
    callFn: () => Promise<T>
  ): Promise<T> {
    const startTime = Date.now();
    const event: MCPCallEvent = {
      id: uuidv4(),
      timestamp: new Date(),
      mcpServerId,
      mcpServerName,
      identity,
      scopes: {
        requested: requestedScopes,
        granted: this.validateScopes(mcpServerId, requestedScopes)
      },
      tool,
      result: {
        status: 'success'
      }
    };

    try {
      // Check scopes before executing
      if (event.scopes.granted.length < event.scopes.requested.length) {
        const denied = event.scopes.requested.filter(s => !event.scopes.granted.includes(s));
        event.result.status = 'denied';
        event.result.message = `Insufficient scopes: ${denied.join(', ')}`;
        await this.logCall(event);
        throw new Error(event.result.message);
      }

      // Execute MCP call
      const result = await callFn();
      event.result.executionTimeMs = Date.now() - startTime;
      await this.logCall(event);
      return result;
    } catch (error) {
      event.result.status = 'error';
      event.result.message = error instanceof Error ? error.message : 'Unknown error';
      event.result.errorCode = error instanceof Error ? error.name : 'Error';
      event.result.executionTimeMs = Date.now() - startTime;
      await this.logCall(event);
      throw error;
    }
  }

  /**
   * Get audit logger (for direct access if needed)
   */
  getAuditLogger(): AuditLogger {
    return this.auditLogger;
  }

  /**
   * Get registered MCP scopes
   */
  getMCPScopes(mcpId: string): string[] {
    return this.mcpScopes.get(mcpId) || [];
  }
}

/**
 * Global MCP audit handler instance
 * Initialize with MCP scope configuration from mcp-config.json
 */
let _mcpAuditHandler: MCPAuditHandler | null = null;

export function getMCPAuditHandler(): MCPAuditHandler {
  if (!_mcpAuditHandler) {
    // Initialize with default scopes from mcp-config.json
    const handler = new MCPAuditHandler();

    // Register all known MCPs with their scopes
    handler.registerMCP('supabase-db', [
      'database:read:schema',
      'database:query:vision_events',
      'database:query:vision_anomalies',
      'database:query:cameras',
      'database:query:tasks',
      'database:subscribe:realtime',
      'database:read:rls'
    ]);

    handler.registerMCP('llm-router', [
      'api:chat',
      'api:embed',
      'billing:track'
    ]);

    handler.registerMCP('git-advanced', [
      'git:read:blame',
      'git:read:history',
      'git:read:governance',
      'git:validate:messages'
    ]);

    handler.registerMCP('fs-watch', [
      'fs:watch:directory',
      'fs:read:governance',
      'fs:validate:frozen'
    ]);

    handler.registerMCP('calendar', [
      'schedule:read:sla',
      'schedule:read:sprint',
      'schedule:write:milestone',
      'schedule:read:capacity'
    ]);

    handler.registerMCP('sequential-thinking', [
      'reasoning:execute'
    ]);

    handler.registerMCP('exa-research', [
      'search:web',
      'search:research',
      'search:news',
      'search:similar'
    ]);

    handler.registerMCP('memory', [
      'knowledge:create:entity',
      'knowledge:add:observation',
      'knowledge:read:entities',
      'knowledge:read:sessions'
    ]);

    _mcpAuditHandler = handler;
  }
  return _mcpAuditHandler;
}

/**
 * Reset audit handler (for testing)
 */
export function resetMCPAuditHandler(): void {
  _mcpAuditHandler = null;
}

/**
 * Export types for use in MCP clients
 */
export type { MCPCallEvent, MCPAuditHandler };
