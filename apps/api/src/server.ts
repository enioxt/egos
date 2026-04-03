/**
 * EGOS Guard Brasil API — REST Server
 *
 * Wraps @egos/guard-brasil into a deployable HTTP API.
 * Deploy: `bun run apps/api/src/server.ts`
 * Endpoint: POST /v1/inspect
 *
 * Monetization tier: Starter R$99/mo, Pro R$499/mo
 */

import { GuardBrasil } from '../../../packages/guard-brasil/src/index.js';
import { evaluatePRI, requiresManualReview, shouldBlockOnPRI } from './pri.js';

const guard = GuardBrasil.create();
const PORT = Number(process.env.GUARD_API_PORT ?? 3099);
const API_KEYS = new Set((process.env.GUARD_API_KEYS ?? '').split(',').filter(Boolean));
const API_VERSION = '0.2.0';
const ENDPOINTS = [
  { method: 'GET', path: '/', description: 'Service health alias' },
  { method: 'GET', path: '/health', description: 'Service health' },
  { method: 'GET', path: '/v1/meta', description: 'Runtime metadata and limits' },
  { method: 'POST', path: '/v1/inspect', description: 'Guard Brasil text inspection' },
] as const;

// ─── Auth middleware ──────────────────────────────────────────────────────────

function authenticate(req: Request): boolean {
  if (API_KEYS.size === 0) return true; // dev mode: no keys = open
  const auth = req.headers.get('authorization');
  if (!auth?.startsWith('Bearer ')) return false;
  return API_KEYS.has(auth.slice(7));
}

// ─── Rate limiting (in-memory, per API key) ───────────────────────────────────

const rateLimits = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = Number(process.env.GUARD_RATE_LIMIT ?? 100); // per minute
const RATE_WINDOW = 60_000;

function checkRateLimit(key: string): boolean {
  const now = Date.now();
  const entry = rateLimits.get(key);
  if (!entry || now > entry.resetAt) {
    rateLimits.set(key, { count: 1, resetAt: now + RATE_WINDOW });
    return true;
  }
  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

// ─── Server ───────────────────────────────────────────────────────────────────

const server = Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    // CORS
    if (req.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // Health check
    if (url.pathname === '/health' || url.pathname === '/') {
      return Response.json({
        service: 'egos-guard-brasil-api',
        version: API_VERSION,
        status: 'healthy',
        timestamp: new Date().toISOString(),
      });
    }

    // GET /v1/meta — API contract + runtime settings
    if (url.pathname === '/v1/meta' && req.method === 'GET') {
      return Response.json({
        service: 'egos-guard-brasil-api',
        version: API_VERSION,
        auth: API_KEYS.size > 0 ? 'bearer' : 'open_dev_mode',
        rateLimit: {
          requestsPerWindow: RATE_LIMIT,
          windowMs: RATE_WINDOW,
        },
        endpoints: ENDPOINTS,
        timestamp: new Date().toISOString(),
      });
    }

    // POST /v1/inspect — main endpoint
    if (url.pathname === '/v1/inspect' && req.method === 'POST') {
      // Auth
      if (!authenticate(req)) {
        return Response.json({ error: 'Unauthorized. Provide Bearer API key.' }, { status: 401 });
      }

      // Rate limit
      const apiKey = req.headers.get('authorization')?.slice(7) ?? 'anonymous';
      if (!checkRateLimit(apiKey)) {
        return Response.json({
          error: `Rate limit exceeded. Max ${RATE_LIMIT} requests/${Math.round(RATE_WINDOW / 1000)}s.`,
        }, { status: 429 });
      }

      // Parse body
      let body: {
        text: string;
        sessionId?: string;
        claims?: Array<{ claim: string; source: string; excerpt?: string; confidence?: string }>;
        pii_types?: string[];
        pri_strategy?: 'paranoid' | 'balanced' | 'permissive';
        pri_context?: {
          impacts_fundamental_rights?: boolean;
          is_admin_action?: boolean;
          user_id?: string;
        };
      };
      try {
        body = await req.json();
      } catch {
        return Response.json({ error: 'Invalid JSON body. Required: { "text": "..." }' }, { status: 400 });
      }

      if (!body.text || typeof body.text !== 'string') {
        return Response.json({ error: 'Missing required field: "text" (string)' }, { status: 400 });
      }

      // Inspect
      const startMs = performance.now();
      const result = guard.inspect(body.text, {
        sessionId: body.sessionId,
        claims: body.claims as any,
      });
      const priDecision = await evaluatePRI(
        body.text,
        {
          piiTypes: body.pii_types,
          strategy: body.pri_strategy,
          context: body.pri_context,
        },
        result.masking.findings,
      );
      const manualReviewRequired = requiresManualReview(priDecision);
      const durationMs = Math.round(performance.now() - startMs);

      if (shouldBlockOnPRI(priDecision, body.pii_types)) {
        return Response.json({
          error: 'PRI blocked request.',
          pri: priDecision,
          meta: {
            durationMs,
            timestamp: new Date().toISOString(),
            version: API_VERSION,
          },
        }, {
          status: 422,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-Guard-Duration-Ms': String(durationMs),
          },
        });
      }

      return Response.json({
        safe: result.safe,
        blocked: result.blocked,
        output: result.output,
        summary: result.summary,
        lgpdDisclosure: result.lgpdDisclosure,
        atrian: {
          passed: result.atrian.passed,
          score: result.atrian.score,
          violationCount: result.atrian.violations.length,
          violations: result.atrian.violations,
        },
        masking: {
          sensitivityLevel: result.masking.sensitivityLevel,
          findingCount: result.masking.findings.length,
          findings: result.masking.findings.map(f => ({
            category: f.category,
            label: f.label,
            suggestion: f.suggestion,
          })),
        },
        evidenceChain: result.evidenceChain ? {
          responseId: result.evidenceChain.responseId,
          overallConfidence: result.evidenceChain.overallConfidence,
          auditHash: result.evidenceChain.auditHash,
          claimCount: result.evidenceChain.claims.length,
        } : null,
        pri: priDecision ? {
          output: priDecision.output,
          confidence: priDecision.confidence,
          reasoning: priDecision.reasoning,
          missingSignals: priDecision.missing_signals,
          classifiersConsulted: priDecision.classifiers_consulted,
          auditHash: priDecision.audit_hash,
        } : null,
        meta: {
          durationMs,
          manualReviewRequired,
          timestamp: new Date().toISOString(),
          version: API_VERSION,
        },
      }, {
        status: manualReviewRequired ? 202 : 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'X-Guard-Duration-Ms': String(durationMs),
        },
      });
    }

    // 404
    return Response.json({
      error: 'Not found.',
      availableEndpoints: ENDPOINTS,
    }, { status: 404 });
  },
});

console.log(`🛡️  EGOS Guard Brasil API v${API_VERSION}`);
console.log(`   Endpoint: http://localhost:${PORT}/v1/inspect`);
console.log(`   Health:   http://localhost:${PORT}/health`);
console.log(`   Meta:     http://localhost:${PORT}/v1/meta`);
console.log(`   Auth:     ${API_KEYS.size > 0 ? `${API_KEYS.size} API key(s) configured` : 'OPEN (dev mode)'}`);
console.log(`   Rate:     ${RATE_LIMIT} req/min per key`);
