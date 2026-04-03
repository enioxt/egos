/**
 * GH-065 — Percentage-Based Pricing Engine
 * EGOS Monetization SSOT: docs/business/MONETIZATION_SSOT.md
 *
 * Formula: customer_charge = llm_cost_usd × margin_multiplier + base_fee_usd
 * Default: 50% margin (×1.5) + $0.30 base per hunt call
 *
 * No external dependencies.
 */

import { estimateCost, type CostUsage } from "../cost-tracker.ts";

// ── Pricing config (matches MONETIZATION_SSOT.md Section 3) ─────────────────

export const DEFAULT_MARGIN_MULTIPLIER = 1.5; // 50% margin on LLM pass-through
export const GEM_HUNTER_BASE_FEE_USD  = 0.30; // per /v1/hunt call
export const GUARD_BRASIL_PER_CALL_USD = 0.00098;

export interface GuardBrasilUsageTier {
  id: "free" | "starter" | "pro" | "business" | "enterprise";
  monthlyCalls: number | null;
  pricePerCallBrl: number;
  estimatedMonthlyBrl: number | null;
}

export const GUARD_BRASIL_USAGE_TIERS: GuardBrasilUsageTier[] = [
  // Free: acquisition tier — cost is ~R$0.007/month per user (negligible)
  { id: "free",       monthlyCalls: 500,       pricePerCallBrl: 0,       estimatedMonthlyBrl: 0    },
  // Developer: indie dev / hobby project — R$0.010/call, teto R$50/mês
  { id: "starter",    monthlyCalls: 5_000,     pricePerCallBrl: 0.0100,  estimatedMonthlyBrl: 50   },
  // Startup: small team 5-50 devs — R$0.007/call, teto R$350/mês
  { id: "pro",        monthlyCalls: 50_000,    pricePerCallBrl: 0.0070,  estimatedMonthlyBrl: 350  },
  // Business: empresa mid-market — R$0.004/call, teto R$2.000/mês
  { id: "business",   monthlyCalls: 500_000,   pricePerCallBrl: 0.0040,  estimatedMonthlyBrl: 2000 },
  // Enterprise: volume >500k — R$0.002/call, negociado, mín R$1k/mês
  { id: "enterprise", monthlyCalls: null,      pricePerCallBrl: 0.0020,  estimatedMonthlyBrl: null },
];

export type Product = "gem-hunter" | "guard-brasil" | "eagle-eye";

export interface PriceEstimate {
  product: Product;
  llmCostUsd: number;
  baseFeeUsd: number;
  totalUsd: number;
  totalBrl: number; // approximate, at 5.0 BRL/USD
  breakdown: string;
}

/** Current BRL/USD rate (update monthly or fetch live) */
export const USD_TO_BRL = 5.0;

export function getGuardBrasilUsageTier(callCount: number): GuardBrasilUsageTier {
  if (callCount <= GUARD_BRASIL_USAGE_TIERS[0].monthlyCalls!) return GUARD_BRASIL_USAGE_TIERS[0];
  if (callCount <= GUARD_BRASIL_USAGE_TIERS[1].monthlyCalls!) return GUARD_BRASIL_USAGE_TIERS[1];
  if (callCount <= GUARD_BRASIL_USAGE_TIERS[2].monthlyCalls!) return GUARD_BRASIL_USAGE_TIERS[2];
  if (callCount <= GUARD_BRASIL_USAGE_TIERS[3].monthlyCalls!) return GUARD_BRASIL_USAGE_TIERS[3];
  return GUARD_BRASIL_USAGE_TIERS[4];
}

/**
 * Calculate charge for a Gem Hunter hunt run.
 * @param llmUsages - All LLM calls made during the run (from createCostSession())
 * @param marginMultiplier - Markup on LLM cost (default 1.5 = 50% margin)
 */
export function priceGemHuntRun(
  llmUsages: CostUsage[],
  marginMultiplier = DEFAULT_MARGIN_MULTIPLIER,
): PriceEstimate {
  const llmCostUsd = llmUsages.reduce((s, u) => s + u.costUsd, 0);
  const chargedLlm  = llmCostUsd * marginMultiplier;
  const totalUsd    = chargedLlm + GEM_HUNTER_BASE_FEE_USD;

  return {
    product: "gem-hunter",
    llmCostUsd: Math.round(chargedLlm * 1_000_000) / 1_000_000,
    baseFeeUsd: GEM_HUNTER_BASE_FEE_USD,
    totalUsd: Math.round(totalUsd * 1_000_000) / 1_000_000,
    totalBrl: Math.round(totalUsd * USD_TO_BRL * 100) / 100,
    breakdown: `LLM($${llmCostUsd.toFixed(6)}×${marginMultiplier}) + base($${GEM_HUNTER_BASE_FEE_USD}) = $${totalUsd.toFixed(4)}`,
  };
}

/**
 * Calculate charge for a Guard Brasil API call.
 * Uses fixed per-call pricing (not LLM-based).
 * @param callCount - Number of PII inspection calls
 */
export function priceGuardBrasilCalls(callCount: number): PriceEstimate {
  const tier = getGuardBrasilUsageTier(callCount);
  const totalBrl = callCount * tier.pricePerCallBrl;
  const totalUsd = totalBrl / USD_TO_BRL;
  return {
    product: "guard-brasil",
    llmCostUsd: 0,
    baseFeeUsd: Math.round(totalUsd * 1_000_000) / 1_000_000,
    totalUsd: Math.round(totalUsd * 1_000_000) / 1_000_000,
    totalBrl: Math.round(totalBrl * 100) / 100,
    breakdown: `${callCount} calls × R$${tier.pricePerCallBrl.toFixed(6)} (${tier.id}) = R$${totalBrl.toFixed(2)}`,
  };
}

/**
 * Check if a charge is within a customer's monthly budget.
 * Returns whether to proceed + remaining budget after charge.
 */
export function checkCustomerBudget(
  chargePlanUsd: number,
  monthlyBudgetUsd: number,
  spentThisMonthUsd: number,
): { allowed: boolean; remaining: number; chargePlan: number } {
  const remaining = monthlyBudgetUsd - spentThisMonthUsd;
  return {
    allowed: chargePlanUsd <= remaining,
    remaining: Math.max(0, remaining - chargePlanUsd),
    chargePlan: chargePlanUsd,
  };
}

/**
 * Format a PriceEstimate as a human-readable receipt line.
 */
export function formatPriceReceipt(estimate: PriceEstimate): string {
  return [
    `Product:   ${estimate.product}`,
    `Breakdown: ${estimate.breakdown}`,
    `Total USD: $${estimate.totalUsd.toFixed(4)}`,
    `Total BRL: R$${estimate.totalBrl.toFixed(2)} (~5.0 BRL/USD)`,
  ].join("\n");
}

/**
 * Simple Stripe Checkout URL builder for monthly subscriptions.
 * Requires STRIPE_PRICE_ID_<PRODUCT>_<TIER> env vars.
 *
 * Usage:
 *   const url = buildStripeCheckoutUrl('gem-hunter', 'starter', 'user@example.com');
 */
export function buildStripeCheckoutUrl(
  product: Product,
  tier: "starter" | "growth" | "enterprise",
  customerEmail: string,
  successUrl = `${process.env.APP_URL ?? "https://egos.ia.br"}/billing/success`,
  cancelUrl  = `${process.env.APP_URL ?? "https://egos.ia.br"}/billing/cancel`,
): string {
  const envKey = `STRIPE_PRICE_ID_${product.toUpperCase().replace("-", "_")}_${tier.toUpperCase()}`;
  const priceId = process.env[envKey];
  if (!priceId) throw new Error(`Missing env var: ${envKey}`);

  const base = "https://checkout.stripe.com/pay";
  const params = new URLSearchParams({
    client_reference_id: customerEmail,
    prefilled_email: customerEmail,
    success_url: successUrl,
    cancel_url: cancelUrl,
  });
  // Note: Real Stripe Checkout uses server-side session creation (apps/api/src/server.ts)
  // This URL is for reference only — call Stripe API to get actual checkout.session URL
  return `${base}/${priceId}?${params}`;
}
