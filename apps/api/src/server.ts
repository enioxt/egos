/**
 * EGOS Guard Brasil API — REST Server
 *
 * Endpoints:
 *   GET  /health                   — service health
 *   POST /v1/keys                  — self-service free-tier API key generation
 *   POST /v1/inspect               — PII inspection (requires Bearer API key)
 *   POST /v1/stripe/checkout       — create Stripe Checkout Session
 *   POST /v1/stripe/webhook        — Stripe webhook (checkout.session.completed → upgrade tier)
 */

import { GuardBrasil } from '../../../packages/guard-brasil/src/index.js';
import { recordApiCall } from '../../../packages/guard-brasil/src/telemetry.ts';
import { validateKey, createFreeTenant, incrementUsage, type Tenant } from '../../../packages/guard-brasil/src/keys.ts';
import { GUARD_BRASIL_USAGE_TIERS } from '../../../packages/shared/src/billing/pricing.ts';
import { evaluatePRI, requiresManualReview, shouldBlockOnPRI } from './pri.js';

const guard = GuardBrasil.create();
const PORT = Number(process.env.GUARD_API_PORT ?? 3099);
const API_VERSION = '0.2.0';
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

    // GET /v1/meta — API contract + runtime settings
    if (url.pathname === '/v1/meta' && req.method === 'GET') {
      return Response.json({
        service: 'egos-guard-brasil-api',
        version: API_VERSION,
        endpoints: [
          { method: 'GET',  path: '/health',                description: 'Service health' },
          { method: 'GET',  path: '/v1/meta',               description: 'Public API contract + pricing metadata' },
          { method: 'POST', path: '/v1/keys',               description: 'Create free API key' },
          { method: 'POST', path: '/v1/inspect',            description: 'Guard Brasil PII inspection' },
        ],
        capabilities: [
          'brazilian-pii-detection',
          'lgpd-disclosure',
          'atrian-validation',
          'inspection-receipts',
          'provenance-binding',
          'evidence-chain',
        ],
        pricing: {
          model: 'usage-based',
          currency: 'BRL',
          free_monthly_calls: 150,
          tiers: GUARD_BRASIL_USAGE_TIERS.map(tier => ({
            id: tier.id,
            monthly_calls: tier.monthlyCalls,
            price_per_call_brl: tier.pricePerCallBrl,
            estimated_monthly_brl: tier.estimatedMonthlyBrl,
          })),
        },
        timestamp: new Date().toISOString(),
      }, { headers: CORS });
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
        provenance?: {
          sourceUrl?: string;
          sourceMethod?: string;
          collectedAt?: string;
          rawRow?: Record<string, unknown>;
          query?: string;
          recordId?: string;
        };
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
        provenance: body.provenance,
      });
      const priDecision = await evaluatePRI(
        body.text,
        { piiTypes: body.pii_types, strategy: body.pri_strategy, context: body.pri_context },
        result.masking.findings,
      );
      const manualReviewRequired = requiresManualReview(priDecision);
      const durationMs = Math.round(performance.now() - startMs);

      // Fire-and-forget: telemetry + usage increment
      recordApiCall(result, {
        tenant_id: auth.tenant?.id,
        input_hash: result.receipt.inputHash,
        duration_ms: durationMs,
        session_id: body.sessionId,
        api_version: '0.2.0',
      })
        .catch(err => console.warn('[api] Telemetry error:', err));
      if (auth.tenant) {
        incrementUsage(auth.tenant.id).catch(err => console.warn('[api] Usage increment error:', err));
      }

      const responseHeaders = {
        'Content-Type': 'application/json',
        ...CORS,
        'X-Guard-Duration-Ms': String(durationMs),
        'X-Guard-Inspection-Hash': result.receipt.inspectionHash,
        'X-Guard-Provenance-Level': result.receipt.provenanceLevel,
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
        receipt: result.receipt,
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

    // POST /v1/stripe/checkout — create Stripe Checkout Session
    if (url.pathname === '/v1/stripe/checkout' && req.method === 'POST') {
      try {
        const { tier, email, tenant_id } = await req.json() as { tier: string; email: string; tenant_id?: string };
        const stripeKey = process.env.STRIPE_SECRET_KEY;
        if (!stripeKey) return Response.json({ error: 'Stripe not configured' }, { status: 503, headers: CORS });

        const priceId = tier === 'enterprise'
          ? process.env.STRIPE_ENTERPRISE_PRICE_ID
          : process.env.STRIPE_PRO_PRICE_ID;

        if (!priceId) return Response.json({ error: 'Invalid tier' }, { status: 400, headers: CORS });

        const origin = req.headers.get('origin') || 'https://guard.egos.ia.br';
        const body = new URLSearchParams({
          'mode': 'subscription',
          'line_items[0][price]': priceId,
          'line_items[0][quantity]': '1',
          'customer_email': email,
          'success_url': `${origin}/landing?upgrade=success&tier=${tier}`,
          'cancel_url': `${origin}/landing?upgrade=cancel`,
          'metadata[tier]': tier,
          'metadata[tenant_id]': tenant_id ?? '',
          'allow_promotion_codes': 'true',
          'billing_address_collection': 'auto',
        });

        const sessionRes = await fetch('https://api.stripe.com/v1/checkout/sessions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${stripeKey}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: body.toString(),
        });
        const session = await sessionRes.json() as any;
        if (session.error) return Response.json({ error: session.error.message }, { status: 400, headers: CORS });

        return Response.json({ url: session.url, session_id: session.id }, { headers: CORS });
      } catch (e: any) {
        return Response.json({ error: e.message }, { status: 500, headers: CORS });
      }
    }

    // POST /v1/stripe/webhook — upgrade tenant tier on payment
    if (url.pathname === '/v1/stripe/webhook' && req.method === 'POST') {
      const stripeKey = process.env.STRIPE_SECRET_KEY;
      const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
      if (!stripeKey) return Response.json({ error: 'Stripe not configured' }, { status: 503 });

      const rawBody = await req.text();

      // Verify Stripe signature if webhook secret is configured
      if (webhookSecret) {
        const sig = req.headers.get('stripe-signature') ?? '';
        if (!verifyStripeSignature(rawBody, sig, webhookSecret)) {
          return Response.json({ error: 'Invalid signature' }, { status: 400 });
        }
      }

      const event = JSON.parse(rawBody) as any;
      console.log(`🔔 Stripe webhook: ${event.type}`);

      if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        const tier = session.metadata?.tier;
        const tenantId = session.metadata?.tenant_id;
        const customerEmail = session.customer_details?.email || session.customer_email;
        const customerId = session.customer;
        const subscriptionId = session.subscription;

        if (tier && (tenantId || customerEmail)) {
          const quotaLimit = tier === 'enterprise' ? 999999 : 10000;
          const mrrBrl = tier === 'enterprise' ? 1497 : 497;

          const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '';
          const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

          // Update tenant tier via Supabase REST
          const filter = tenantId ? `id=eq.${tenantId}` : `email=eq.${encodeURIComponent(customerEmail)}`;
          const updateRes = await fetch(`${supabaseUrl}/rest/v1/guard_brasil_tenants?${filter}`, {
            method: 'PATCH',
            headers: {
              apikey: supabaseKey,
              Authorization: `Bearer ${supabaseKey}`,
              'Content-Type': 'application/json',
              Prefer: 'return=representation',
            },
            body: JSON.stringify({
              tier,
              quota_limit: quotaLimit,
              mrr_brl: mrrBrl,
              stripe_customer_id: customerId,
              stripe_subscription_id: subscriptionId,
              status: 'active',
              updated_at: new Date().toISOString(),
            }),
          });

          const updated = await updateRes.json() as any[];
          console.log(`✅ Upgraded tenant to ${tier}: ${tenantId || customerEmail} (${updated?.length ?? 0} rows updated)`);
        }
      }

      if (event.type === 'customer.subscription.deleted') {
        const sub = event.data.object;
        const customerId = sub.customer;
        const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

        // Downgrade to free on cancellation
        await fetch(`${supabaseUrl}/rest/v1/guard_brasil_tenants?stripe_customer_id=eq.${customerId}`, {
          method: 'PATCH',
          headers: {
            apikey: supabaseKey,
            Authorization: `Bearer ${supabaseKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ tier: 'free', quota_limit: 150, mrr_brl: 0, updated_at: new Date().toISOString() }),
        });
        console.log(`⬇️  Downgraded tenant ${customerId} to free (subscription cancelled)`);
      }

      return Response.json({ received: true });
    }

    // GET /api/admin/cost-dashboard — real-time cost tracking (admin only)
    if (url.pathname === '/api/admin/cost-dashboard' && req.method === 'GET') {
      const auth = req.headers.get('authorization');
      const isAdmin = auth?.startsWith('Bearer ') && API_KEYS.has(auth.slice(7));
      if (!isAdmin) return Response.json({ error: 'Unauthorized' }, { status: 403, headers: CORS });

      const supabaseUrl = process.env.SUPABASE_URL;
      const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
      if (!supabaseUrl || !supabaseKey) {
        return Response.json({ error: 'Supabase not configured' }, { status: 503, headers: CORS });
      }

      try {
        // Query last 24 hours of events
        const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        const eventsRes = await fetch(
          `${supabaseUrl}/rest/v1/guard_brasil_events?timestamp=gte.${encodeURIComponent(since)}&select=*`,
          {
            headers: {
              apikey: supabaseKey,
              Authorization: `Bearer ${supabaseKey}`,
            },
          }
        );

        if (!eventsRes.ok) throw new Error(`Supabase error: ${eventsRes.status}`);
        const events = (await eventsRes.json()) as Array<{
          cost_usd?: number;
          metadata?: Record<string, any>;
          timestamp?: string;
        }>;

        // Group by agent_id and tool_name
        const byAgent = new Map<string, number>();
        const byTool = new Map<string, number>();
        let totalCost = 0;
        const hourly = new Map<string, number>();

        for (const evt of events) {
          const cost = evt.cost_usd || 0;
          totalCost += cost;

          const agent = evt.metadata?.agentId || 'unknown';
          byAgent.set(agent, (byAgent.get(agent) || 0) + cost);

          const tool = evt.metadata?.toolName || 'api_call';
          byTool.set(tool, (byTool.get(tool) || 0) + cost);

          // Hourly breakdown
          if (evt.timestamp) {
            const hour = new Date(evt.timestamp).toISOString().slice(0, 13) + ':00:00Z';
            hourly.set(hour, (hourly.get(hour) || 0) + cost);
          }
        }

        return Response.json(
          {
            period: '24h',
            total_cost_usd: Number(totalCost.toFixed(8)),
            events_count: events.length,
            by_agent: Object.fromEntries(byAgent),
            by_tool: Object.fromEntries(byTool),
            hourly_breakdown: Object.fromEntries(hourly),
          },
          { headers: CORS }
        );
      } catch (err: any) {
        console.error('Cost dashboard error:', err);
        return Response.json(
          { error: 'Failed to fetch cost data', detail: err.message },
          { status: 500, headers: CORS }
        );
      }
    }

    return Response.json({
      error: 'Not found.',
      endpoints: { health: 'GET /health', keys: 'POST /v1/keys', inspect: 'POST /v1/inspect', checkout: 'POST /v1/stripe/checkout', webhook: 'POST /v1/stripe/webhook', 'cost-dashboard': 'GET /api/admin/cost-dashboard' },
    }, { status: 404, headers: CORS });
  },
});

// ─── Stripe signature verification ─────────────────────────────────────────
function verifyStripeSignature(payload: string, sig: string, secret: string): boolean {
  try {
    const parts = Object.fromEntries(sig.split(',').map(p => p.split('=')));
    const timestamp = parts['t'];
    const expectedSig = parts['v1'];
    if (!timestamp || !expectedSig) return false;

    const signedPayload = `${timestamp}.${payload}`;
    const { createHmac } = require('crypto');
    const computed = createHmac('sha256', secret).update(signedPayload).digest('hex');

    // Timing-safe comparison
    if (computed.length !== expectedSig.length) return false;
    let diff = 0;
    for (let i = 0; i < computed.length; i++) diff |= computed.charCodeAt(i) ^ expectedSig.charCodeAt(i);
    return diff === 0;
  } catch { return false; }
}

console.log(`🛡️  EGOS Guard Brasil API v0.2.0`);
console.log(`   Inspect: http://localhost:${PORT}/v1/inspect`);
console.log(`   Keys:    http://localhost:${PORT}/v1/keys`);
console.log(`   Health:  http://localhost:${PORT}/health`);
console.log(`   Auth:    ${API_KEYS.size > 0 ? `${API_KEYS.size} env key(s) + Supabase` : 'Supabase only'}`);
console.log(`   Rate:    ${RATE_LIMIT} req/min per key`);
