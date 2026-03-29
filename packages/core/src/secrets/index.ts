/**
 * EGOS Secrets Management
 * Central export point for all secret store implementations
 */

export type { SecretStore } from './vault';
export {
  EnvSecretStore,
  VaultSecretStore,
  createSecretStore,
  getSecretStore,
  resetSecretStore
} from './vault';
