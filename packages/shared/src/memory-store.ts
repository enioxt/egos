/**
 * memory-store.ts — Adapter interface + implementations for conversational memory
 *
 * Decouples chatbot memory persistence from any specific backend.
 * Each chatbot repo (852, egos-web, ratio, etc.) instantiates the
 * appropriate adapter without changing the calling code.
 *
 * Implementations:
 *   - SupabaseMemoryStore — persists to Supabase (production)
 *   - InMemoryStore       — process-scoped Map (dev/test)
 *   - NullMemoryStore     — no-op, always returns null (CI/offline)
 *
 * Usage (852 example):
 *   import { SupabaseMemoryStore } from '@egos/shared';
 *   const memory = new SupabaseMemoryStore(supabaseClient, 'conversations_852');
 *   const block = await memory.buildMemoryBlock(identityKey);
 */

import { buildConversationMemoryBlock, type ConversationMemoryOptions } from './conversation-memory';

// ─── Core Interface ───────────────────────────────────────────────────────────

export interface MemoryEntry {
  id: string;
  /** Identity key (session hash or user id) */
  key: string;
  /** Summary or content text */
  content: string;
  /** Title / label for this entry */
  title?: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

export interface MemoryStore {
  /** Get the N most recent entries for an identity key */
  getRecent(key: string, limit?: number): Promise<MemoryEntry[]>;
  /** Persist a new memory entry */
  save(
    key: string,
    content: string,
    options?: { title?: string; metadata?: Record<string, unknown> },
  ): Promise<void>;
  /**
   * Build a text block ready for injection into a system prompt.
   * Returns null if no memory found or store is unavailable.
   */
  buildMemoryBlock(
    key: string,
    limit?: number,
    options?: ConversationMemoryOptions,
  ): Promise<string | null>;
}

// ─── Supabase Implementation ──────────────────────────────────────────────────

/**
 * Minimal Supabase client interface — accepts the real @supabase/supabase-js
 * client or any compatible mock.
 */
export interface SupabaseClientLike {
  from(table: string): {
    select(columns: string): {
      eq(column: string, value: string): {
        order(column: string, opts: { ascending: boolean }): {
          limit(n: number): Promise<{ data: unknown[] | null; error: unknown }>;
        };
      };
    };
    insert(row: Record<string, unknown>): Promise<{ error: unknown }>;
    update(row: Record<string, unknown>): {
      eq(column: string, value: string): Promise<{ error: unknown }>;
    };
  };
}

export interface SupabaseMemoryStoreOptions {
  /** Table column used as the identity key. Default: 'session_hash' */
  keyColumn?: string;
  /** Table column storing the summary text. Default: 'summary' */
  contentColumn?: string;
  /** Table column storing the title. Default: 'title' */
  titleColumn?: string;
  /** Table column storing metadata (jsonb). Default: 'metadata' */
  metadataColumn?: string;
  /** Table column for timestamps. Default: 'updated_at' */
  timestampColumn?: string;
}

export class SupabaseMemoryStore implements MemoryStore {
  private readonly opts: Required<SupabaseMemoryStoreOptions>;

  constructor(
    private readonly client: SupabaseClientLike,
    private readonly tableName: string,
    options: SupabaseMemoryStoreOptions = {},
  ) {
    this.opts = {
      keyColumn: options.keyColumn ?? 'session_hash',
      contentColumn: options.contentColumn ?? 'summary',
      titleColumn: options.titleColumn ?? 'title',
      metadataColumn: options.metadataColumn ?? 'metadata',
      timestampColumn: options.timestampColumn ?? 'updated_at',
    };
  }

  async getRecent(key: string, limit = 3): Promise<MemoryEntry[]> {
    const { keyColumn, contentColumn, titleColumn, metadataColumn, timestampColumn } = this.opts;

    const { data, error } = await this.client
      .from(this.tableName)
      .select(`id, ${keyColumn}, ${contentColumn}, ${titleColumn}, ${metadataColumn}, ${timestampColumn}`)
      .eq(keyColumn, key)
      .order(timestampColumn, { ascending: false })
      .limit(limit);

    if (error || !data) return [];

    return (data as Record<string, unknown>[]).map(row => ({
      id: String(row.id ?? ''),
      key: String(row[keyColumn] ?? ''),
      content: String(row[contentColumn] ?? ''),
      title: row[titleColumn] ? String(row[titleColumn]) : undefined,
      createdAt: String(row[timestampColumn] ?? ''),
      metadata: row[metadataColumn] && typeof row[metadataColumn] === 'object'
        ? row[metadataColumn] as Record<string, unknown>
        : undefined,
    })).filter(e => e.content.trim().length > 0);
  }

  async save(
    key: string,
    content: string,
    options: { title?: string; metadata?: Record<string, unknown> } = {},
  ): Promise<void> {
    const { keyColumn, contentColumn, titleColumn, metadataColumn, timestampColumn } = this.opts;

    await this.client.from(this.tableName).insert({
      [keyColumn]: key,
      [contentColumn]: content,
      [titleColumn]: options.title ?? null,
      [metadataColumn]: options.metadata ?? null,
      [timestampColumn]: new Date().toISOString(),
    });
  }

  async buildMemoryBlock(
    key: string,
    limit = 3,
    options?: ConversationMemoryOptions,
  ): Promise<string | null> {
    const entries = await this.getRecent(key, limit);
    if (entries.length === 0) return null;
    return buildConversationMemoryBlock(
      entries.map(e => ({ title: e.title, summary: e.content })),
      options,
    );
  }
}

// ─── In-Memory Implementation ─────────────────────────────────────────────────

/** Process-scoped store — resets on restart. For dev/test only. */
export class InMemoryStore implements MemoryStore {
  private readonly store = new Map<string, MemoryEntry[]>();

  async getRecent(key: string, limit = 3): Promise<MemoryEntry[]> {
    return (this.store.get(key) ?? []).slice(-limit).reverse();
  }

  async save(
    key: string,
    content: string,
    options: { title?: string; metadata?: Record<string, unknown> } = {},
  ): Promise<void> {
    const existing = this.store.get(key) ?? [];
    existing.push({
      id: `${key}-${Date.now()}`,
      key,
      content,
      title: options.title,
      createdAt: new Date().toISOString(),
      metadata: options.metadata,
    });
    this.store.set(key, existing);
  }

  async buildMemoryBlock(
    key: string,
    limit = 3,
    options?: ConversationMemoryOptions,
  ): Promise<string | null> {
    const entries = await this.getRecent(key, limit);
    if (entries.length === 0) return null;
    return buildConversationMemoryBlock(
      entries.map(e => ({ title: e.title, summary: e.content })),
      options,
    );
  }

  /** Test helper — clear all stored entries */
  clear(): void {
    this.store.clear();
  }
}

// ─── Null Implementation ──────────────────────────────────────────────────────

/** No-op store — always returns null. Safe for CI, offline, or opt-out. */
export class NullMemoryStore implements MemoryStore {
  async getRecent(): Promise<MemoryEntry[]> { return []; }
  async save(): Promise<void> { /* no-op */ }
  async buildMemoryBlock(): Promise<null> { return null; }
}
