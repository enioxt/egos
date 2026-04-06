#!/usr/bin/env node
/**
 * @egosbr/guard-brasil-mcp — MCP Server
 * 
 * Model Context Protocol server exposing Guard Brasil PII detection
 * for Claude Code, Windsurf, Cursor, and other MCP-compatible IDEs.
 * 
 * Install:
 *   npm install -g @egosbr/guard-brasil-mcp
 *   
 * Usage:
 *   guard-brasil-mcp
 * 
 * Or add to Claude Code:
 *   claude mcp add guard-brasil -- npx @egosbr/guard-brasil-mcp
 */

import { GuardBrasil, type PIIFinding } from '../../guard-brasil/src/index.js';

const guard = GuardBrasil.create();

// ─── Types ───────────────────────────────────────────────────────────────────

interface Finding {
  type: string;
  value: string;
  maskedValue: string;
  position: number;
}

// ─── MCP Protocol (stdio JSON-RPC 2.0) ───────────────────────────────────────

interface JsonRpcRequest {
  jsonrpc: '2.0';
  id: number | string;
  method: string;
  params?: Record<string, unknown>;
}

interface JsonRpcResponse {
  jsonrpc: '2.0';
  id: number | string;
  result?: unknown;
  error?: { code: number; message: string };
}

function respond(id: number | string, result: unknown): void {
  const msg: JsonRpcResponse = { jsonrpc: '2.0', id, result };
  console.log(JSON.stringify(msg));
}

function respondError(id: number | string, code: number, message: string): void {
  const msg: JsonRpcResponse = { jsonrpc: '2.0', id, error: { code, message } };
  console.log(JSON.stringify(msg));
}

// ─── Tool definitions ─────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: 'guard_inspect',
    description: 'Full LGPD PII inspection with ATRiAN ethics validation',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to analyze for Brazilian PII' },
        mask: { type: 'boolean', description: 'Whether to mask detected PII', default: true }
      },
      required: ['text']
    }
  },
  {
    name: 'guard_scan_pii',
    description: 'Quick PII-only scan (CPF, CNPJ, RG, MASP, etc.)',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to scan' }
      },
      required: ['text']
    }
  },
  {
    name: 'guard_check_safe',
    description: 'Boolean safety check for public sharing',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to check' }
      },
      required: ['text']
    }
  }
];

// ─── Handlers ──────────────────────────────────────────────────────────────────

async function handleInspect(params: { text: string; mask?: boolean }) {
  const result = guard.inspect(params.text);
  const findings = result.masking.findings || [];
  return {
    safe: result.safe,
    piiDetected: findings.length > 0,
    findings: findings.map((f: any) => ({
      type: f.type,
      value: params.mask !== false ? f.maskedValue : f.value,
      position: f.position
    })),
    atrian: result.atrian,
    recommendation: findings.length > 0 
      ? 'Contains Brazilian PII. Review before sharing.' 
      : 'No PII detected. Safe for public sharing.'
  };
}

async function handleScanPII(params: { text: string }) {
  const result = guard.inspect(params.text);
  const findings = result.masking.findings || [];
  return {
    piiCount: findings.length,
    types: [...new Set(findings.map((f: any) => f.type))],
    hasCPF: findings.some((f: any) => f.type === 'CPF'),
    hasCNPJ: findings.some((f: any) => f.type === 'CNPJ'),
    hasRG: findings.some((f: any) => f.type === 'RG'),
    hasEmail: findings.some((f: any) => f.type === 'EMAIL')
  };
}

async function handleCheckSafe(params: { text: string }) {
  const result = guard.inspect(params.text);
  const findings = result.masking.findings || [];
  return {
    safe: result.safe,
    canShare: findings.length === 0,
    reason: findings.length > 0 
      ? `Contains ${findings.length} PII occurrence(s)` 
      : 'No PII found'
  };
}

// ─── Main loop ─────────────────────────────────────────────────────────────────

async function main() {
  // Send initialization
  respond(0, {
    protocolVersion: '2024-11-05',
    capabilities: { tools: {} },
    serverInfo: { name: '@egosbr/guard-brasil-mcp', version: '0.1.0' }
  });

  // Tool list
  respond(1, { tools: TOOLS });

  // Process stdin
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', async (chunk) => {
    const lines = chunk.toString().split('\n').filter(Boolean);
    
    for (const line of lines) {
      try {
        const req: JsonRpcRequest = JSON.parse(line);
        
        if (req.method === 'tools/call') {
          const { name, arguments: args } = req.params as { name: string; arguments: Record<string, unknown> };
          
          let result;
          switch (name) {
            case 'guard_inspect':
              result = await handleInspect(args as { text: string; mask?: boolean });
              break;
            case 'guard_scan_pii':
              result = await handleScanPII(args as { text: string });
              break;
            case 'guard_check_safe':
              result = await handleCheckSafe(args as { text: string });
              break;
            default:
              respondError(req.id, -32601, `Unknown tool: ${name}`);
              continue;
          }
          
          respond(req.id, { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] });
        }
      } catch (err) {
        // Ignore parse errors (keepalive messages)
      }
    }
  });
}

main().catch(console.error);
