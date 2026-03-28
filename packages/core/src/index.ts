/**
 * EGOS Core Package
 * Central exports for core functionality: contracts, auth, secrets, modules
 */

export type { LoggerLike, EgosContext, SearchQuery } from './contracts';
export type { SecretStore } from './secrets';
export {
  EnvSecretStore,
  VaultSecretStore,
  createSecretStore,
  getSecretStore,
  resetSecretStore
} from './secrets';
