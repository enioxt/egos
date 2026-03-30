#!/usr/bin/env bun
/**
 * EGOS Guard Brasil — MCP Server
 *
 * Model Context Protocol server exposing Guard Brasil as tools
 * for Claude Code, Windsurf, Cursor, and other MCP-compatible IDEs.
 *
 * Install in Claude Code:
 *   claude mcp add guard-brasil -- bun run /path/to/apps/api/src/mcp-server.ts
 *
 * Tools exposed:
 *   - guard_inspect: Full inspection (ATRiAN + PII + masking + evidence)
 *   - guard_scan_pii: PII-only scan
 *   - guard_check_safe: Quick boolean safety check
 */

import { GuardBrasil, scanForPII, isPublicSafe, getPIISummary } from '../../../packages/guard-brasil/src/index.js';

const guard = GuardBrasil.create();

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
  const json = JSON.stringify(msg);
  process.stdout.write(`Content-Length: ${Buffer.byteLength(json)}\r\n\r\n${json}`);
}

function respondError(id: number | string, code: number, message: string): void {
  const msg: JsonRpcResponse = { jsonrpc: '2.0', id, error: { code, message } };
  const json = JSON.stringify(msg);
  process.stdout.write(`Content-Length: ${Buffer.byteLength(json)}\r\n\r\n${json}`);
}

// ─── Tool definitions ─────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: 'guard_inspect',
    description: 'Inspect text through all Guard Brasil safety layers: ATRiAN ethical validation, PII scanning (CPF/RG/MASP/REDS), LGPD-compliant masking, and evidence chain. Returns safe/unsafe status, masked output, violations, and LGPD disclosure.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to inspect (LLM output, user message, document content)' },
        session_id: { type: 'string', description: 'Optional session ID for evidence chain tracing' },
      },
      required: ['text'],
    },
  },
  {
    name: 'guard_scan_pii',
    description: 'Scan text for Brazilian PII only (CPF, RG, MASP, REDS, processo, placa, phone, email, nome, data nascimento). Returns findings with categories and replacement suggestions.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to scan for PII' },
      },
      required: ['text'],
    },
  },
  {
    name: 'guard_check_safe',
    description: 'Quick boolean check: is this text safe to publish publicly? Returns true/false. Use guard_inspect for detailed analysis.',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Text to check' },
      },
      required: ['text'],
    },
  },
];

// ─── Handle requests ──────────────────────────────────────────────────────────

function handleRequest(req: JsonRpcRequest): void {
  switch (req.method) {
    case 'initialize':
      respond(req.id, {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: {
          name: 'guard-brasil',
          version: '0.1.0',
        },
      });
      break;

    case 'initialized':
      // No response needed
      break;

    case 'tools/list':
      respond(req.id, { tools: TOOLS });
      break;

    case 'tools/call': {
      const params = req.params as { name: string; arguments: Record<string, string> };

      if (params.name === 'guard_inspect') {
        const result = guard.inspect(params.arguments.text, {
          sessionId: params.arguments.session_id,
        });
        respond(req.id, {
          content: [{
            type: 'text',
            text: JSON.stringify({
              safe: result.safe,
              blocked: result.blocked,
              output: result.output,
              summary: result.summary,
              lgpdDisclosure: result.lgpdDisclosure,
              atrianScore: result.atrian.score,
              atrianPassed: result.atrian.passed,
              violations: result.atrian.violations,
              piiFindings: result.masking.findings.map(f => ({
                category: f.category,
                label: f.label,
              })),
              sensitivityLevel: result.masking.sensitivityLevel,
              evidenceHash: result.evidenceChain?.auditHash,
            }, null, 2),
          }],
        });
      } else if (params.name === 'guard_scan_pii') {
        const findings = scanForPII(params.arguments.text);
        const summary = getPIISummary(findings);
        respond(req.id, {
          content: [{
            type: 'text',
            text: JSON.stringify({
              count: findings.length,
              summary,
              findings: findings.map(f => ({
                category: f.category,
                label: f.label,
                matched: f.matched,
                suggestion: f.suggestion,
              })),
            }, null, 2),
          }],
        });
      } else if (params.name === 'guard_check_safe') {
        const safe = isPublicSafe(params.arguments.text);
        respond(req.id, {
          content: [{
            type: 'text',
            text: safe ? 'SAFE — No PII detected.' : 'UNSAFE — PII detected. Use guard_inspect for details.',
          }],
        });
      } else {
        respondError(req.id, -32601, `Unknown tool: ${params.name}`);
      }
      break;
    }

    default:
      respondError(req.id, -32601, `Unknown method: ${req.method}`);
  }
}

// ─── stdio transport ──────────────────────────────────────────────────────────

let buffer = '';

process.stdin.setEncoding('utf-8');
process.stdin.on('data', (chunk: string) => {
  buffer += chunk;

  while (true) {
    const headerEnd = buffer.indexOf('\r\n\r\n');
    if (headerEnd === -1) break;

    const header = buffer.slice(0, headerEnd);
    const match = header.match(/Content-Length:\s*(\d+)/i);
    if (!match) {
      buffer = buffer.slice(headerEnd + 4);
      continue;
    }

    const contentLength = parseInt(match[1], 10);
    const bodyStart = headerEnd + 4;
    if (buffer.length < bodyStart + contentLength) break;

    const body = buffer.slice(bodyStart, bodyStart + contentLength);
    buffer = buffer.slice(bodyStart + contentLength);

    try {
      const req = JSON.parse(body) as JsonRpcRequest;
      handleRequest(req);
    } catch (e) {
      // Skip malformed messages
    }
  }
});

process.stderr.write('🛡️  Guard Brasil MCP Server v0.1.0 ready\n');
