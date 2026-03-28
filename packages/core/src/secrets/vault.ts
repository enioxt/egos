/**
 * EGOS-004: Secrets Vault Abstraction
 * Provides secure, centralized secret management without hardcoded credentials
 * Supports multiple backends: EnvSecretStore (current), VaultSecretStore (future)
 */

export interface SecretStore {
  /**
   * Retrieve a secret value by key
   * @param key - Secret identifier (e.g., OPENAI_API_KEY)
   * @returns Promise<string | undefined> - Secret value or undefined if not found
   */
  get(key: string): Promise<string | undefined>;

  /**
   * Store a secret value
   * @param key - Secret identifier
   * @param value - Secret value
   * @throws Error if operation fails (e.g., permission denied)
   */
  set(key: string, value: string): Promise<void>;

  /**
   * List all secret keys (without values for security)
   * @returns Promise<string[]> - Array of secret keys
   */
  list(): Promise<string[]>;

  /**
   * Delete a secret
   * @param key - Secret identifier
   * @throws Error if operation fails
   */
  delete(key: string): Promise<void>;

  /**
   * Check if a secret exists
   * @param key - Secret identifier
   */
  exists(key: string): Promise<boolean>;
}

/**
 * EnvSecretStore: Read-only secrets from process.env
 * - Reads from environment variables only (no persistence)
 * - Set/delete operations throw UnsupportedOperationError
 * - Suitable for: containerized deployments, 12-factor apps
 * - Security: Requires secrets to be injected at runtime (K8s secrets, Vercel env, etc.)
 */
export class EnvSecretStore implements SecretStore {
  async get(key: string): Promise<string | undefined> {
    return process.env[key];
  }

  async set(_key: string, _value: string): Promise<void> {
    throw new Error(
      'EnvSecretStore is read-only. Set secrets via environment variables.'
    );
  }

  async list(): Promise<string[]> {
    // Return common EGOS-related env vars that exist
    const commonKeys = [
      'OPENAI_API_KEY',
      'GITHUB_TOKEN',
      'SUPABASE_ANON_KEY',
      'SUPABASE_SERVICE_KEY',
      'LLM_ROUTER_SECRET',
      'CALENDAR_API_KEY',
      'EXA_API_KEY',
      'ANTHROPIC_API_KEY',
      'DASHSCOPE_API_KEY',
      'OPENROUTER_API_KEY'
    ];

    return commonKeys.filter(key => process.env[key] !== undefined);
  }

  async delete(_key: string): Promise<void> {
    throw new Error('EnvSecretStore is read-only. Cannot delete environment variables.');
  }

  async exists(key: string): Promise<boolean> {
    return process.env[key] !== undefined;
  }
}

/**
 * VaultSecretStore: HashiCorp Vault integration (PLANNED)
 * - Centralized secret management
 * - Dynamic secret generation
 * - Audit logging of all access
 * - Automatic secret rotation
 *
 * To implement:
 * 1. Add @hashicorp/vault dependency
 * 2. Implement auth method (token, AppRole, K8s)
 * 3. Add health checks and retry logic
 * 4. Integrate with ConsoleAuditLogger for access tracking
 */
export class VaultSecretStore implements SecretStore {
  private vaultAddr: string;
  private vaultToken: string;

  constructor(vaultAddr: string, vaultToken: string) {
    this.vaultAddr = vaultAddr;
    this.vaultToken = vaultToken;
  }

  async get(_key: string): Promise<string | undefined> {
    throw new Error(
      'VaultSecretStore not yet implemented. Use EnvSecretStore for now.'
    );
  }

  async set(_key: string, _value: string): Promise<void> {
    throw new Error('VaultSecretStore not yet implemented.');
  }

  async list(): Promise<string[]> {
    throw new Error('VaultSecretStore not yet implemented.');
  }

  async delete(_key: string): Promise<void> {
    throw new Error('VaultSecretStore not yet implemented.');
  }

  async exists(_key: string): Promise<boolean> {
    throw new Error('VaultSecretStore not yet implemented.');
  }
}

/**
 * Factory function to create appropriate SecretStore based on environment
 * @param backend - 'env' | 'vault' | auto-detect
 * @returns SecretStore instance
 */
export function createSecretStore(
  backend: 'env' | 'vault' = 'env'
): SecretStore {
  switch (backend) {
    case 'env':
      return new EnvSecretStore();
    case 'vault':
      const vaultAddr = process.env.VAULT_ADDR;
      const vaultToken = process.env.VAULT_TOKEN;
      if (!vaultAddr || !vaultToken) {
        throw new Error(
          'Vault backend requested but VAULT_ADDR or VAULT_TOKEN not set'
        );
      }
      return new VaultSecretStore(vaultAddr, vaultToken);
    default:
      return new EnvSecretStore();
  }
}

/**
 * Singleton instance (lazy-initialized)
 * Use: const store = getSecretStore(); await store.get('OPENAI_API_KEY')
 */
let _secretStore: SecretStore | null = null;

export function getSecretStore(): SecretStore {
  if (!_secretStore) {
    _secretStore = createSecretStore();
  }
  return _secretStore;
}

/**
 * Reset secret store (for testing)
 */
export function resetSecretStore(): void {
  _secretStore = null;
}
