/**
 * EGOS Guard Brasil API — REST Server
 *
 * Endpoints:
 *   GET  /health       — service health
 *   POST /v1/keys      — self-service free-tier API key generation
 *   POST /v1/inspect   — PII inspection (requires Bearer API key)
 */

import { GuardBrasil } from '../../../packages/guard-brasil/src/index.js';
import { recordApiCall } from '../../../packages/guard-brasil/src/telemetry.ts';
import { validateKey, createFreeTenant, incrementUsage, type Tenant } from '../../../packages/guard-brasil/src/keys.ts';
import { evaluatePRI, requiresManualReview, shouldBlockOnPRI } from './pri.js';

const guard = GuardBrasil.create();
const PORT = Number(process.env.GUARD_API_PORT ?? 3099);
// Internal/CI keys loaded from env (bypass Supabase quota)
const API_KEYS = new Set((process.env.GUARD_API_KEYS ?? '').split(',').filter(Boolean));

// ─── CORS ─────────────────────────────────────────────────────────────────────

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// ─── Auth ─────────────────────────────────────────────────────────────────────

type AuthResult =
  | { ok: false }
  | { ok: true; tenant: Tenant | null; remaining: number };

async function authenticateRequest(req: Request): Promise<AuthResult> {
  const auth = req.headers.get('authorization');
  if (!auth?.startsWith('Bearer ')) {
    // Dev mode: no keys configured → open
    if (API_KEYS.size === 0) return { ok: true, tenant: null, remaining: Infinity };
    return { ok: false };
  }
  const rawKey = auth.slice(7);
  // Fast path: internal env-var keys bypass quota
  if (API_KEYS.has(rawKey)) return { ok: true, tenant: null, remaining: Infinity };
  // Customer keys via Supabase
  const tenant = await validateKey(rawKey);
  if (!tenant) return { ok: false };
  const remaining = tenant.quota_limit - tenant.calls_this_month;
  return { ok: true, tenant, remaining };
}

// ─── Rate limiting (in-memory, per-key per-minute) ───────────────────────────

const rateLimits = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = Number(process.env.GUARD_RATE_LIMIT ?? 100);

function checkRateLimit(key: string): boolean {
  const now = Date.now();
  const entry = rateLimits.get(key);
  if (!entry || now > entry.resetAt) {
    rateLimits.set(key, { count: 1, resetAt: now + 60_000 });
    return true;
  }
  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

// ─── Server ───────────────────────────────────────────────────────────────────

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

    // GET /health
    if (url.pathname === '/health' || url.pathname === '/') {
      return Response.json({
        service: 'egos-guard-brasil-api',
        version: '0.2.0',
        status: 'healthy',
        timestamp: new Date().toISOString(),
      });
    }

    // POST /v1/keys — self-service free-tier key generation
    if (url.pathname === '/v1/keys' && req.method === 'POST') {
      let body: { name?: string; email?: string };
      try { body = await req.json(); } catch {
        return Response.json({ error: 'Invalid JSON body' }, { status: 400, headers: CORS });
      }
      if (!body.name?.trim() || !body.email?.trim()) {
        return Response.json({ error: 'Required: name, email' }, { status: 400, headers: CORS });
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
        return Response.json({ error: 'Invalid email format' }, { status: 400, headers: CORS });
      }
      try {
        const { key, tenant } = await createFreeTenant(body.name.trim(), body.email.trim());
        return Response.json({
          key,
          tier: tenant.tier,
          quota_limit: tenant.quota_limit,
          message: 'Save this key — it will not be shown again.',
          docs: 'POST https://guard.egos.ia.br/v1/inspect with Authorization: Bearer <key>',
        }, { headers: CORS });
      } catch (e: any) {
        const isDuplicate = e.message?.includes('duplicate') || e.message?.includes('unique');
        return Response.json(
          { error: isDuplicate ? 'An API key already exists for this email.' : 'Failed to create key. Try again.' },
          { status: isDuplicate ? 409 : 500, headers: CORS },
        );
      }
    }

    // POST /v1/inspect
    if (url.pathname === '/v1/inspect' && req.method === 'POST') {
      const auth = await authenticateRequest(req);
      if (!auth.ok) {
        return Response.json(
          { error: 'Unauthorized. Get a free API key at https://guard.egos.ia.br' },
          { status: 401, headers: CORS },
        );
      }
      if (auth.remaining <= 0 && auth.tenant !== null) {
        return Response.json({
          error: 'Monthly quota exceeded.',
          tier: auth.tenant.tier,
          quota_limit: auth.tenant.quota_limit,
          upgrade_url: 'https://guard.egos.ia.br/#pricing',
        }, { status: 429, headers: CORS });
      }

      const rawKey = req.headers.get('authorization')?.slice(7) ?? 'anonymous';
      if (!checkRateLimit(rawKey)) {
        return Response.json({ error: 'Rate limit exceeded. Max 100 requests/minute.' }, { status: 429, headers: CORS });
      }

      let body: {
        text: string;
        sessionId?: string;
        claims?: Array<{ claim: string; source: string; excerpt?: string; confidence?: string }>;
        pii_types?: string[];
        pri_strategy?: 'paranoid' | 'balanced' | 'permissive';
        pri_context?: { impacts_fundamental_rights?: boolean; is_admin_action?: boolean; user_id?: string };
      };
      try { body = await req.json(); } catch {
        return Response.json({ error: 'Invalid JSON body. Required: { "text": "..." }' }, { status: 400, headers: CORS });
      }
      if (!body.text || typeof body.text !== 'string') {
        return Response.json({ error: 'Missing required field: "text" (string)' }, { status: 400, headers: CORS });
      }

      const startMs = performance.now();
      const result = guard.inspect(body.text, {
        sessionId: body.sessionId,
        claims: body.claims as any,
      });
      const priDecision = await evaluatePRI(
        body.text,
        { piiTypes: body.pii_types, strategy: body.pri_strategy, context: body.pri_context },
        result.masking.findings,
      );
      const manualReviewRequired = requiresManualReview(priDecision);
      const durationMs = Math.round(performance.now() - startMs);

      // Fire-and-forget: telemetry + usage increment
      recordApiCall(result, { duration_ms: durationMs, session_id: body.sessionId, api_version: '0.2.0' })
        .catch(err => console.warn('[api] Telemetry error:', err));
      if (auth.tenant) {
        incrementUsage(auth.tenant.id).catch(err => console.warn('[api] Usage increment error:', err));
      }

      const responseHeaders = {
        'Content-Type': 'application/json',
        ...CORS,
        'X-Guard-Duration-Ms': String(durationMs),
        ...(auth.tenant && { 'X-RateLimit-Remaining': String(Math.max(0, auth.remaining - 1)) }),
      };

      if (shouldBlockOnPRI(priDecision, body.pii_types)) {
        return Response.json({
          error: 'PRI blocked request.',
          pri: priDecision,
          meta: { durationMs, timestamp: new Date().toISOString(), version: '0.2.0' },
        }, { status: 422, headers: responseHeaders });
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
          version: '0.2.0',
        },
      }, { status: manualReviewRequired ? 202 : 200, headers: responseHeaders });
    }

    return Response.json({
      error: 'Not found.',
      endpoints: { health: 'GET /health', keys: 'POST /v1/keys', inspect: 'POST /v1/inspect' },
    }, { status: 404, headers: CORS });
  },
});

console.log(`🛡️  EGOS Guard Brasil API v0.2.0`);
console.log(`   Inspect: http://localhost:${PORT}/v1/inspect`);
console.log(`   Keys:    http://localhost:${PORT}/v1/keys`);
console.log(`   Health:  http://localhost:${PORT}/health`);
console.log(`   Auth:    ${API_KEYS.size > 0 ? `${API_KEYS.size} env key(s) + Supabase` : 'Supabase only'}`);
console.log(`   Rate:    ${RATE_LIMIT} req/min per key`);
