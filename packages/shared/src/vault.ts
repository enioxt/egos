/**
 * 🔐 Credentials Vault — @egos/shared
 *
 * Centralized credential lookup with audit trail.
 * NEVER stores actual secret values in code — only reads from:
 *   1. Environment variables (.env files)
 *   2. Supabase credentials_vault table (metadata only)
 *
 * Usage:
 *   const vault = createVault({ supabaseUrl, supabaseKey });
 *   const token = vault.get('TELEGRAM_BOT_TOKEN_AI_AGENTS');
 *   const status = await vault.verifyAll(); // check all credentials
 */

export interface VaultConfig {
  supabaseUrl?: string;
  supabaseKey?: string;
  logPrefix?: string;
}

export interface CredentialStatus {
  name: string;
  envVar: string;
  present: boolean;
  service: string;
  location: string;
  expiresAt?: string;
}

export interface VaultRecorder {
  /** Get credential value from env (never from Supabase — values aren't stored there) */
  get: (envVarName: string) => string | undefined;
  /** Get credential or throw if missing */
  require: (envVarName: string) => string;
  /** Check if credential exists in environment */
  has: (envVarName: string) => boolean;
  /** Verify all known credentials from Supabase vault registry */
  verifyAll: () => Promise<CredentialStatus[]>;
  /** Log credential access for audit */
  logAccess: (envVarName: string, purpose: string) => void;
}

export function createVault(config: VaultConfig = {}): VaultRecorder {
  const { supabaseUrl, supabaseKey, logPrefix = 'vault' } = config;
  const accessLog: Array<{ envVar: string; purpose: string; timestamp: string }> = [];

  function get(envVarName: string): string | undefined {
    return process.env[envVarName];
  }

  function require(envVarName: string): string {
    const value = get(envVarName);
    if (!value) {
      throw new Error(`[${logPrefix}] Missing required credential: ${envVarName}. Check .env or credentials_vault in Supabase.`);
    }
    return value;
  }

  function has(envVarName: string): boolean {
    return !!process.env[envVarName];
  }

  async function verifyAll(): Promise<CredentialStatus[]> {
    if (!supabaseUrl || !supabaseKey) {
      console.warn(`[${logPrefix}] Supabase not configured — cannot verify credentials from vault registry.`);
      return [];
    }

    try {
      const res = await fetch(
        `${supabaseUrl}/rest/v1/credentials_vault?select=name,env_var_name,service,location,expires_at,status&status=eq.active`,
        {
          headers: {
            apikey: supabaseKey,
            Authorization: `Bearer ${supabaseKey}`,
          },
        }
      );

      if (!res.ok) {
        console.warn(`[${logPrefix}] Failed to fetch vault registry: ${res.status}`);
        return [];
      }

      const credentials = await res.json() as Array<{
        name: string;
        env_var_name: string;
        service: string;
        location: string;
        expires_at?: string;
        status: string;
      }>;

      return credentials.map(cred => ({
        name: cred.name,
        envVar: cred.env_var_name,
        present: cred.location === 'env_file' ? has(cred.env_var_name) : true,
        service: cred.service,
        location: cred.location,
        expiresAt: cred.expires_at ?? undefined,
      }));
    } catch (err) {
      console.warn(`[${logPrefix}] Vault verification failed:`, err);
      return [];
    }
  }

  function logAccess(envVarName: string, purpose: string): void {
    accessLog.push({
      envVar: envVarName,
      purpose,
      timestamp: new Date().toISOString(),
    });
    if (accessLog.length > 1000) accessLog.splice(0, 500);
  }

  return { get, require, has, verifyAll, logAccess };
}
