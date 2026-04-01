/**
 * Cache — Redis cache-aside layer with graceful degradation.
 * Ported from br-acc/api/src/bracc/services/cache.py (BRACC-002).
 *
 * Client-agnostic: pass any Redis-compatible client to connect().
 * All operations are no-ops if Redis is unavailable.
 */

import { createHash } from "crypto";

type JsonValue = string | number | boolean | null | JsonObject | JsonArray;
type JsonObject = { [key: string]: JsonValue };
type JsonArray = JsonValue[];

/** Minimal interface any Redis client must satisfy. */
export interface RedisLike {
  get(key: string): Promise<string | null>;
  setEx(key: string, ttl: number, value: string): Promise<unknown>;
  del(keys: string[]): Promise<unknown>;
  ping(): Promise<unknown>;
  /** Optional — used for flush(). */
  scanIterator?(opts: { MATCH: string }): AsyncIterable<string>;
}

/** TTL configuration per prefix (seconds). 0 = no cache. */
export const TTL_CONFIG: Record<string, number> = {
  search: 120,      // 2 min
  entity: 300,      // 5 min
  stats: 60,        // 1 min
  chat: 0,          // no cache — conversations are unique
  connections: 180, // 3 min
};

interface CacheStats {
  hits: number;
  misses: number;
  errors: number;
  sets: number;
  total_requests: number;
  hit_rate_pct: number;
  available: boolean;
  ttl_config: Record<string, number>;
}

const _stats = { hits: 0, misses: 0, errors: 0, sets: 0 };

export class CacheService {
  private _client: RedisLike | null = null;
  private _available = false;

  /**
   * Provide a connected Redis client. Call this during app startup.
   * Example:
   *   import { createClient } from 'redis';
   *   const client = createClient({ url: process.env.REDIS_URL });
   *   await client.connect();
   *   await cache.connect(client);
   */
  async connect(client: RedisLike): Promise<void> {
    try {
      await client.ping();
      this._client = client;
      this._available = true;
    } catch (e) {
      console.warn(`[cache] Redis unavailable, cache disabled: ${(e as Error).message}`);
      this._available = false;
    }
  }

  disconnect(): void {
    this._client = null;
    this._available = false;
  }

  private static makeKey(prefix: string, params: Record<string, unknown>): string {
    const raw = JSON.stringify(
      Object.fromEntries(Object.entries(params).sort(([a], [b]) => a.localeCompare(b)))
    );
    const h = createHash("md5").update(raw).digest("hex").slice(0, 12);
    return `egos:${prefix}:${h}`;
  }

  async get(prefix: string, params: Record<string, unknown>): Promise<JsonValue | null> {
    if (!this._available || !TTL_CONFIG[prefix] || TTL_CONFIG[prefix] === 0) return null;
    try {
      const key = CacheService.makeKey(prefix, params);
      const raw = await this._client!.get(key);
      if (raw !== null) {
        _stats.hits++;
        return JSON.parse(raw) as JsonValue;
      }
      _stats.misses++;
      return null;
    } catch {
      _stats.errors++;
      return null;
    }
  }

  async set(prefix: string, params: Record<string, unknown>, value: JsonValue): Promise<void> {
    if (!this._available || !TTL_CONFIG[prefix] || TTL_CONFIG[prefix] === 0) return;
    try {
      const key = CacheService.makeKey(prefix, params);
      const ttl = TTL_CONFIG[prefix];
      const raw = JSON.stringify(value);
      if (raw.length > 500_000) return; // skip >500KB
      await this._client!.setEx(key, ttl, raw);
      _stats.sets++;
    } catch {
      _stats.errors++;
    }
  }

  getStats(): CacheStats {
    const total = _stats.hits + _stats.misses;
    return {
      ..._stats,
      total_requests: total,
      hit_rate_pct: total > 0 ? Math.round((_stats.hits / total) * 1000) / 10 : 0,
      available: this._available,
      ttl_config: TTL_CONFIG,
    };
  }

  async flush(): Promise<number> {
    if (!this._available || !this._client?.scanIterator) return 0;
    try {
      const keys: string[] = [];
      for await (const key of this._client.scanIterator({ MATCH: "egos:*" })) {
        keys.push(key);
      }
      if (keys.length > 0) await this._client.del(keys);
      return keys.length;
    } catch {
      return 0;
    }
  }
}

/** Singleton instance — call connect(redisClient) before use. */
export const cache = new CacheService();
