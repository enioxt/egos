/**
 * Guard Brasil — API Key Management (EGOS-MONETIZE-001)
 *
 * Customer API keys backed by guard_brasil_tenants in Supabase.
 * Keys stored as SHA-256 hashes — never plaintext.
 */

import { createHash, randomBytes } from 'crypto';

const KEY_PREFIX = 'gb_live_';

export interface Tenant {
  id: string;
  name: string;
  email: string | null;
  tier: string;
  quota_limit: number;
  calls_this_month: number;
  status: string;
}

// Lazy Supabase (same pattern as telemetry.ts)
let _supabase: any = null;

function getSupabase(): any {
  if (_supabase) return _supabase;
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { createClient } = require('@supabase/supabase-js');
    const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) return null;
    _supabase = createClient(url, key);
    return _supabase;
  } catch {
    return null;
  }
}

export function generateApiKey(): string {
  return KEY_PREFIX + randomBytes(24).toString('hex');
}

export function hashKey(key: string): string {
  return createHash('sha256').update(key).digest('hex');
}

export async function validateKey(rawKey: string): Promise<Tenant | null> {
  const sb = getSupabase();
  if (!sb) return null;
  const hash = hashKey(rawKey);
  const { data, error } = await sb
    .from('guard_brasil_tenants')
    .select('id, name, email, tier, quota_limit, calls_this_month, status')
    .eq('api_key_hash', hash)
    .eq('status', 'active')
    .single();
  if (error || !data) return null;
  return data as Tenant;
}

export async function incrementUsage(tenantId: string): Promise<void> {
  const sb = getSupabase();
  if (!sb) return;
  await sb.rpc('increment_api_usage', { p_tenant_id: tenantId });
}

export async function createFreeTenant(
  name: string,
  email: string,
): Promise<{ key: string; tenant: Tenant }> {
  const sb = getSupabase();
  if (!sb) throw new Error('Database unavailable');

  const rawKey = generateApiKey();
  const hash = hashKey(rawKey);

  const { data, error } = await sb
    .from('guard_brasil_tenants')
    .insert({
      name,
      email,
      tier: 'free',
      api_key_hash: hash,
      quota_limit: 500,
      calls_this_month: 0,
    })
    .select('id, name, email, tier, quota_limit, calls_this_month, status')
    .single();

  if (error) throw new Error(error.message);
  return { key: rawKey, tenant: data as Tenant };
}
