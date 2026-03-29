/**
 * @egos/guard-brasil — Brazilian AI Safety Layer
 *
 * A compliance and trust layer for AI assistants operating in Brazilian
 * public-sector and enterprise contexts. Provides:
 *
 *   - ATRiAN ethical validation (absolute claims, false promises, fabricated data)
 *   - PII Scanner BR (CPF, RG, MASP, REDS, processo, placa, nome)
 *   - Public Guard — LGPD-compliant output masking
 *   - Evidence Chain — traceable response discipline
 *   - GuardBrasil facade — unified one-call API
 *
 * Compliance: Lei 13.709/2018 (LGPD)
 *
 * @example
 * ```ts
 * import { GuardBrasil } from '@egos/guard-brasil';
 *
 * const guard = GuardBrasil.create();
 * const result = await guard.inspect(llmResponse);
 * if (!result.safe) console.log(result.masked);
 * ```
 */

export { GuardBrasil, createGuardBrasil } from './guard.js';
export type { GuardBrasilConfig, GuardBrasilResult, InspectOptions } from './guard.js';

// Re-export individual modules for fine-grained usage
export { createAtrianValidator } from './lib/index.js';
export type { AtrianConfig, AtrianResult, AtrianViolation, ViolationLevel } from './lib/index.js';

export { scanForPII, sanitizeText, getPIISummary } from './lib/index.js';
export type { PIICategory, PIIFinding, PIIPatternDefinition } from './lib/index.js';

export { maskPublicOutput, isPublicSafe, buildLGPDDisclosure } from './lib/index.js';
export type { PublicGuardConfig, MaskingResult, MaskingAction, GuardAction, SensitivityLevel } from './lib/index.js';

export { createEvidenceChain, EvidenceChainBuilder, formatEvidenceBlock, validateChain } from './lib/index.js';
export type { EvidenceChain, EvidenceItem, ClaimWithEvidence, EvidenceType, ConfidenceLevel, EvidenceChainOptions } from './lib/index.js';
