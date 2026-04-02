/**
 * EGOS Guard Brasil — Brazilian AI Safety Layer
 *
 * Unified entry point for the Guard Brasil product boundary.
 * Composable guardrails for Brazilian AI systems:
 *
 * 1. ATRiAN: Post-response ethical validation (7 axioms)
 * 2. PII Scanner: Brazilian personal data detection (CPF/CNPJ/RG/email/phone)
 * 3. Public Guard: LGPD-compliant output masking with audit trail
 * 4. Evidence Chain: Traceable provenance for AI-generated claims
 *
 * Usage:
 *   import { guardBrasil } from '@egos/shared/guard-brasil';
 *   const result = guardBrasil.validate(text);
 *
 * @module guard-brasil
 * @version 1.0.0
 * @license MIT
 */

import { createAtrianValidator, type AtrianConfig, type AtrianResult } from './atrian.js';
import { scanForPII, sanitizeText, getPIISummary, type PIIFinding } from './pii-scanner.js';
import { maskPublicOutput, isPublicSafe, buildLGPDDisclosure, type PublicGuardConfig, type MaskingResult } from './public-guard.js';
import { createEvidenceChain, formatEvidenceBlock, validateChain, type EvidenceChainOptions, type EvidenceChain } from './evidence-chain.js';

// Re-export all components
export { createAtrianValidator, scanForPII, sanitizeText, getPIISummary, maskPublicOutput, isPublicSafe, buildLGPDDisclosure, createEvidenceChain, formatEvidenceBlock, validateChain };
export type { AtrianConfig, AtrianResult, PIIFinding, PublicGuardConfig, MaskingResult, EvidenceChainOptions, EvidenceChain };

/**
 * Guard Brasil validation result — combines all safety checks.
 */
export interface GuardBrasilResult {
  /** Is the text safe for public output? */
  safe: boolean;
  /** ATRiAN ethical validation score (0-100) */
  atrianScore: number;
  /** ATRiAN passed? */
  atrianPassed: boolean;
  /** Number of PII findings */
  piiCount: number;
  /** LGPD sensitivity level */
  sensitivityLevel: string;
  /** Masked text (PII removed) */
  maskedText: string;
  /** LGPD disclosure note (empty if clean) */
  lgpdDisclosure: string;
  /** Full ATRiAN result */
  atrian: AtrianResult;
  /** Full masking result */
  masking: MaskingResult;
}

export interface GuardBrasilConfig {
  atrian?: AtrianConfig;
  publicGuard?: PublicGuardConfig;
  /** Minimum ATRiAN score to pass (default: 60) */
  minAtrianScore?: number;
}

/**
 * Creates a Guard Brasil validator instance.
 *
 * Runs ATRiAN ethical checks + PII masking in a single call.
 */
export function createGuardBrasil(config: GuardBrasilConfig = {}) {
  const atrianValidator = createAtrianValidator(config.atrian ?? {});
  const minScore = config.minAtrianScore ?? 60;

  function validate(text: string): GuardBrasilResult {
    // 1. ATRiAN ethical validation
    const atrian = atrianValidator.validateResponse(text);

    // 2. PII masking
    const masking = maskPublicOutput(text, config.publicGuard);

    // 3. LGPD disclosure
    const lgpdDisclosure = buildLGPDDisclosure(masking);

    // 4. Combined safety check
    const safe = atrian.passed && atrian.score >= minScore && masking.safe;

    return {
      safe,
      atrianScore: atrian.score,
      atrianPassed: atrian.passed,
      piiCount: masking.findings.length,
      sensitivityLevel: masking.sensitivityLevel,
      maskedText: masking.masked,
      lgpdDisclosure,
      atrian,
      masking,
    };
  }

  return { validate };
}
