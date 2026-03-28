/**
 * Tests for MCP Audit Handler — EGOS-004.4
 * Verifies audit logging for MCP calls with scope validation
 */

import { MCPAuditHandler } from './mcp-audit-handler';
import { ConsoleAuditLogger } from '@egos/audit';
import type { Identity } from '@egos/core';

describe('MCPAuditHandler', () => {
  let handler: MCPAuditHandler;
  let auditLogger: ConsoleAuditLogger;
  let testIdentity: Identity;

  beforeEach(() => {
    auditLogger = new ConsoleAuditLogger();
    handler = new MCPAuditHandler(auditLogger);

    testIdentity = {
      userId: 'user_123',
      source: 'claude-code',
      scopes: ['mcp:supabase:read'],
      token: 'test-token'
    };

    // Register test MCPs
    handler.registerMCP('test-mcp-1', ['api:read', 'api:write']);
    handler.registerMCP('test-mcp-2', ['database:query']);
  });

  test('should register MCP with scopes', () => {
    const scopes = handler.getMCPScopes('test-mcp-1');
    expect(scopes).toEqual(['api:read', 'api:write']);
  });

  test('should log successful MCP call', async () => {
    const event = {
      id: 'evt_123',
      timestamp: new Date(),
      mcpServerId: 'test-mcp-1',
      mcpServerName: 'Test MCP 1',
      identity: testIdentity,
      scopes: {
        requested: ['api:read'],
        granted: []
      },
      tool: {
        name: 'query',
        args: { table: 'users' }
      },
      result: {
        status: 'success' as const,
        executionTimeMs: 150
      }
    };

    await handler.logCall(event);

    // Verify audit entry was logged
    const entries = (auditLogger as any).getEntries?.();
    expect(entries).toBeDefined();
    expect(entries?.length).toBeGreaterThan(0);
  });

  test('should track MCP call with correct scopes', async () => {
    const result = await handler.trackMCPCall(
      'test-mcp-1',
      'Test MCP 1',
      testIdentity,
      { name: 'query', args: { table: 'users' } },
      ['api:read'],
      async () => ({ success: true, rows: [] })
    );

    expect(result).toEqual({ success: true, rows: [] });

    const entries = (auditLogger as any).getEntries?.();
    expect(entries).toBeDefined();
    expect(entries?.length).toBeGreaterThan(0);
  });

  test('should deny call when scope is missing', async () => {
    await expect(
      handler.trackMCPCall(
        'test-mcp-1',
        'Test MCP 1',
        testIdentity,
        { name: 'delete', args: { id: 'user_1' } },
        ['api:delete'], // This scope is not registered
        async () => ({ success: true })
      )
    ).rejects.toThrow('Insufficient scopes');

    const entries = (auditLogger as any).getEntries?.();
    expect(entries).toBeDefined();
    const auditEntry = entries?.[0];
    expect(auditEntry?.result).toBe('denied');
  });

  test('should log error status when MCP call fails', async () => {
    const testError = new Error('API connection failed');

    await expect(
      handler.trackMCPCall(
        'test-mcp-1',
        'Test MCP 1',
        testIdentity,
        { name: 'query' },
        ['api:read'],
        async () => {
          throw testError;
        }
      )
    ).rejects.toThrow('API connection failed');

    const entries = (auditLogger as any).getEntries?.();
    expect(entries).toBeDefined();
    const auditEntry = entries?.[0];
    expect(auditEntry?.result).toBe('denied');
    expect(auditEntry?.context?.resultStatus).toBe('error');
  });

  test('should record execution time in audit log', async () => {
    await handler.trackMCPCall(
      'test-mcp-1',
      'Test MCP 1',
      testIdentity,
      { name: 'query' },
      ['api:read'],
      async () => {
        // Simulate execution time
        await new Promise(resolve => setTimeout(resolve, 100));
        return { data: [] };
      }
    );

    const entries = (auditLogger as any).getEntries?.();
    const auditEntry = entries?.[0];
    expect(auditEntry?.context?.executionTimeMs).toBeGreaterThanOrEqual(100);
  });

  test('should include tool arguments in audit context', async () => {
    const toolArgs = { table: 'users', limit: 10 };

    await handler.trackMCPCall(
      'test-mcp-1',
      'Test MCP 1',
      testIdentity,
      { name: 'query', args: toolArgs },
      ['api:read'],
      async () => ({ rows: [] })
    );

    const entries = (auditLogger as any).getEntries?.();
    const auditEntry = entries?.[0];
    expect(auditEntry?.context?.toolArgs).toEqual(toolArgs);
  });

  test('should validate multiple scopes correctly', async () => {
    await handler.trackMCPCall(
      'test-mcp-1',
      'Test MCP 1',
      testIdentity,
      { name: 'transaction' },
      ['api:read', 'api:write'],
      async () => ({ success: true })
    );

    const entries = (auditLogger as any).getEntries?.();
    const auditEntry = entries?.[0];
    expect(auditEntry?.result).toBe('allowed');
    expect(auditEntry?.context?.scopesGranted).toEqual(['api:read', 'api:write']);
  });

  test('should return empty scopes for unregistered MCP', () => {
    const scopes = handler.getMCPScopes('unknown-mcp');
    expect(scopes).toEqual([]);
  });
});
