/**
 * EGOS Secrets Management
 * Central export point for all secret store implementations
 */

export {
  SecretStore,
  EnvSecretStore,
  VaultSecretStore,
  createSecretStore,
  getSecretStore,
  resetSecretStore
} from './vault';
