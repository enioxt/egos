/**
 * EGOS Core Package
 * Central exports for core functionality: contracts, auth, secrets, modules
 */

export type { LoggerLike, EgosContext, SearchQuery } from './contracts';
export type { Identity, ActivationRequest, ActivationResponse } from './auth/contracts';
export { IdentitySchema, ActivationRequestSchema, ActivationResponseSchema } from './auth/contracts';
export type { PolicyConfig } from './auth/policy-evaluator';
export { DefaultPolicyEvaluator } from './auth/policy-evaluator';
export type { SecretStore } from './secrets';
export {
  EnvSecretStore,
  VaultSecretStore,
  createSecretStore,
  getSecretStore,
  resetSecretStore
} from './secrets';
export type { PRIOutput, PRIStrategy, PRIDecision, PRIRequest, PRIAuditEvent } from './guards/pri';
export { PRIGate, getPRIGate } from './guards/pri';
export type {
  IntegrationChannel,
  IntegrationAuthType,
  IntegrationStatus,
  IntegrationDistributionKind,
  IntegrationProofKind,
  IntegrationDocumentationRefs,
  IntegrationRuntimeProof,
  IntegrationDistribution,
  IntegrationValidation,
  IntegrationManifest,
  EgosIntegration,
} from './integration';
export { validateIntegrationManifest } from './integration';
