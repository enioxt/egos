/**
 * Guard Brasil x402 Channel — HTTP 402 Payment Required middleware
 *
 * Implements x402 protocol (EIP-7702 pattern) for micropayment-gated Guard Brasil API calls.
 * Uses Coinbase public facilitator (x402.org) to settle USDC on Base — no own infra required.
 *
 * Routes:
 *   GET  /guard-brasil/health       — channel health (free)
 *   GET  /guard-brasil/meta         — pricing + capabilities (free)
 *   POST /guard-brasil/inspect      — PII inspection ($0.001 USDC / call, Base chain)
 *
 * x402 flow:
 *   1. Client POSTs /guard-brasil/inspect without payment
 *   2. Server returns 402 with X-Payment-Required header (price, network, recipient)
 *   3. Client sends payment TX via Coinbase facilitator, includes X-Payment header
 *   4. Server verifies payment via facilitator, proxies to Guard Brasil API
 *   5. Server returns result + X-Payment-Response header
 *
 * x402 spec: https://x402.org
 * Facilitator: https://x402.org/facilitator (public Coinbase endpoint, no auth needed)
 * Base network: https://base.org (L2, ~$0.00001/tx gas)
 *
 * API-004 ✅ Base wallet: 0x7f43b82a000a1977cc355c6e7ece166dfbb885ab
 * API-005 ✅ Skeleton live. Env vars required for production:
 *   - GUARD_BRASIL_PAYMENT_ADDRESS  — Base chain USDC recipient (see API-004)
 *   - GUARD_BRASIL_API_KEY          — internal key for proxied calls
 *   - X402_PRICE_USDC_ATOMIC        — price per call in USDC atomic units (default 1000 = $0.001)
 *
 * Pricing rationale (market reference, not revenue target):
 *   $0.001 USDC/call = competitive with AWS Comprehend PII (~$0.0001/char × 10 chars avg)
 *   Free tier: via Guard Brasil API free keys (150 calls/mo), no x402 needed
 *   Always prefer free/freemium first — x402 for agent-to-agent programmatic use
 */

import { Hono } from "hono";

// ── Constants (all env-overridable — no hardcoded production values) ───────────

const GUARD_API_URL = process.env.GUARD_BRASIL_API_URL ?? "https://guard.egos.ia.br";
const GUARD_API_KEY = process.env.GUARD_BRASIL_API_KEY ?? "";
// API-004: Base wallet for USDC payments. Set via env — default is the known wallet.
const PAYMENT_ADDRESS = process.env.GUARD_BRASIL_PAYMENT_ADDRESS ?? "0x7f43b82a000a1977cc355c6e7ece166dfbb885ab";
const FACILITATOR_URL = process.env.X402_FACILITATOR_URL ?? "https://x402.org/facilitator";

// Env-overridable pricing: USDC atomic units (6 decimals). 1000 = $0.001 per call.
// Reference: AWS Comprehend PII ~$0.001/request; Guard Brasil goal: cost-covering + fair margin.
const PRICE_PER_CALL_USDC_ATOMIC = Number(process.env.X402_PRICE_USDC_ATOMIC ?? "1000");
const NETWORK = process.env.X402_NETWORK ?? "base";
const CURRENCY = "USDC";

// ── Types ──────────────────────────────────────────────────────────────────────

interface PaymentPayload {
  network: string;
  txHash: string;
  amount: number; // USDC atomic units
  recipient: string;
}

interface FacilitatorVerifyResponse {
  isValid: boolean;
  invalidReason?: string;
  settlement?: {
    txHash: string;
    amount: string;
    network: string;
  };
}

// ── Payment Verification ───────────────────────────────────────────────────────

/**
 * Verify payment via Coinbase x402 facilitator (no viem needed — HTTP call only).
 * Full verification (on-chain) requires viem + API-004 wallet.
 */
async function verifyPayment(payment: PaymentPayload): Promise<{ ok: boolean; reason?: string }> {
  if (!PAYMENT_ADDRESS) {
    // API-004 not done yet — log and allow (dev mode)
    console.warn("[x402] GUARD_BRASIL_PAYMENT_ADDRESS not set — payment verification skipped (dev mode)");
    return { ok: true };
  }

  try {
    const res = await fetch(`${FACILITATOR_URL}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: payment.network,
        txHash: payment.txHash,
        expectedRecipient: PAYMENT_ADDRESS,
        expectedAmount: PRICE_PER_CALL_USDC_ATOMIC.toString(),
        expectedCurrency: CURRENCY,
      }),
    });

    if (!res.ok) {
      return { ok: false, reason: `facilitator ${res.status}` };
    }

    const data = (await res.json()) as FacilitatorVerifyResponse;
    if (!data.isValid) {
      return { ok: false, reason: data.invalidReason ?? "invalid payment" };
    }

    return { ok: true };
  } catch (err) {
    console.error("[x402] Facilitator verify error:", err);
    return { ok: false, reason: "facilitator unreachable" };
  }
}

/** Parse X-Payment header into PaymentPayload. Format: "network:txHash:amount" */
function parsePaymentHeader(header: string | null): PaymentPayload | null {
  if (!header) return null;
  const parts = header.split(":");
  if (parts.length < 3) return null;
  const [network, txHash, amountStr] = parts;
  const amount = Number(amountStr);
  if (!network || !txHash || isNaN(amount)) return null;
  return { network, txHash, amount, recipient: PAYMENT_ADDRESS };
}

// ── Hono Router ───────────────────────────────────────────────────────────────

export const guardBrasil = new Hono();

/** Health — free, no auth */
guardBrasil.get("/health", (c) => {
  return c.json({
    service: "guard-brasil-x402",
    status: "operational",
    payment: PAYMENT_ADDRESS ? "configured" : "dev-mode (no payment address)",
    price: `$${(PRICE_PER_CALL_USDC_ATOMIC / 1_000_000).toFixed(4)} USDC per call`,
    network: NETWORK,
    facilitator: FACILITATOR_URL,
    upstream: GUARD_API_URL,
  });
});

/** Meta — pricing + capabilities, free */
guardBrasil.get("/meta", async (c) => {
  try {
    const res = await fetch(`${GUARD_API_URL}/v1/meta`);
    if (!res.ok) return c.json({ error: "upstream unavailable" }, 503);
    const data = await res.json();
    return c.json({
      ...data as object,
      x402: {
        price_per_call_usdc: PRICE_PER_CALL_USDC_ATOMIC / 1_000_000,
        network: NETWORK,
        currency: CURRENCY,
        recipient: PAYMENT_ADDRESS || "pending API-004",
        facilitator: FACILITATOR_URL,
      },
    });
  } catch {
    return c.json({ error: "upstream unreachable" }, 503);
  }
});

/**
 * Inspect — PII detection gated by x402 micropayment.
 *
 * Without X-Payment header → 402 with payment instructions.
 * With valid X-Payment header → proxy to Guard Brasil API, return result.
 */
guardBrasil.post("/inspect", async (c) => {
  const xPayment = c.req.header("X-Payment");
  const payment = parsePaymentHeader(xPayment ?? null);

  // ── 402: No payment provided ──────────────────────────────────────────────
  if (!payment) {
    c.header("X-Payment-Required", JSON.stringify({
      scheme: "exact",
      network: NETWORK,
      maxAmountRequired: PRICE_PER_CALL_USDC_ATOMIC.toString(),
      resource: `${GUARD_API_URL}/v1/inspect`,
      description: "Guard Brasil PII inspection — $0.001 USDC on Base",
      mimeType: "application/json",
      payTo: PAYMENT_ADDRESS || "pending",
      maxTimeoutSeconds: 60,
      asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", // USDC on Base
      extra: { name: "USDC", version: "1" },
    }));
    c.header("Access-Control-Expose-Headers", "X-Payment-Required");
    return c.json({
      error: "Payment Required",
      message: "Include X-Payment header with Base USDC transaction. See X-Payment-Required for details.",
      x402_spec: "https://x402.org",
    }, 402);
  }

  // ── Verify payment via facilitator ─────────────────────────────────────────
  const verification = await verifyPayment(payment);
  if (!verification.ok) {
    return c.json({
      error: "Payment Invalid",
      reason: verification.reason,
    }, 402);
  }

  // ── Proxy to Guard Brasil API ──────────────────────────────────────────────
  if (!GUARD_API_KEY) {
    return c.json({ error: "Gateway misconfigured — GUARD_BRASIL_API_KEY not set" }, 503);
  }

  try {
    const body = await c.req.json();
    const upstream = await fetch(`${GUARD_API_URL}/v1/inspect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${GUARD_API_KEY}`,
      },
      body: JSON.stringify(body),
    });

    if (!upstream.ok) {
      const err = await upstream.text();
      return c.json({ error: "upstream error", detail: err }, upstream.status as 400 | 422 | 500);
    }

    const result = await upstream.json();
    c.header("X-Payment-Response", JSON.stringify({ success: true, txHash: payment.txHash }));
    return c.json(result);
  } catch (err) {
    console.error("[x402] Upstream proxy error:", err);
    return c.json({ error: "upstream unreachable" }, 503);
  }
});
