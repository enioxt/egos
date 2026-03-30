/**
 * Mycelium → Redis Pub/Sub Bridge
 *
 * EGOS-089: Bridges the in-memory Mycelium reference graph to Redis Pub/Sub
 * for cross-process agent communication.
 *
 * Design principles:
 * - Export functions, not classes
 * - Graceful degradation when Redis is unavailable (logs to console)
 * - Importable without Redis running
 * - No hard runtime dependency on a Redis client package — uses
 *   Node.js native `net` for the RESP2 wire protocol OR falls back
 *   to the mock transport when REDIS_URL is not set.
 *
 * @see docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md
 * @see TASKS.md EGOS-089
 */

import * as net from 'net';

// ═══════════════════════════════════════════════════════════
// Public Types
// ═══════════════════════════════════════════════════════════

export interface RedisBridgeConfig {
  /** Redis connection URL, e.g. redis://localhost:6379 */
  redisUrl: string;
  /** Pub/Sub channel name, e.g. 'egos:mycelium:events' */
  channel: string;
  /** When true, automatically publish events on graph mutations */
  publishOnMutation: boolean;
}

export interface MyceliumEvent {
  type: 'node_added' | 'node_updated' | 'edge_added' | 'edge_removed' | 'graph_snapshot';
  timestamp: string;
  payload: unknown;
  /** Origin repo or agent identifier */
  source: string;
}

/** Opaque bridge handle returned by createRedisBridge */
export interface RedisBridge {
  /** Publish a single MyceliumEvent to the configured channel */
  publish: (event: MyceliumEvent) => Promise<void>;
  /**
   * Subscribe to the configured channel.
   * Returns an unsubscribe function — call it to stop receiving events.
   */
  subscribe: (handler: (event: MyceliumEvent) => void) => () => void;
  /** Tear down all connections gracefully */
  close: () => Promise<void>;
  /** Internal transport — 'redis' | 'mock' */
  readonly transport: 'redis' | 'mock';
}

// ═══════════════════════════════════════════════════════════
// RESP2 helpers (minimal subset for PUBLISH / SUBSCRIBE)
// ═══════════════════════════════════════════════════════════

function encodeRespArray(...args: string[]): Buffer {
  const parts: string[] = [`*${args.length}\r\n`];
  for (const arg of args) {
    parts.push(`$${Buffer.byteLength(arg)}\r\n${arg}\r\n`);
  }
  return Buffer.from(parts.join(''));
}

interface RespSocket {
  socket: net.Socket;
  write: (cmd: Buffer) => void;
  destroy: () => void;
}

function connectRespSocket(host: string, port: number): Promise<RespSocket> {
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host, port });
    const timeout = setTimeout(() => {
      socket.destroy();
      reject(new Error(`Redis connection timeout ${host}:${port}`));
    }, 3000);

    socket.once('connect', () => {
      clearTimeout(timeout);
      resolve({
        socket,
        write: (cmd: Buffer) => socket.write(cmd),
        destroy: () => socket.destroy(),
      });
    });

    socket.once('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
  });
}

function parseRedisUrl(redisUrl: string): { host: string; port: number } {
  try {
    const url = new URL(redisUrl);
    return {
      host: url.hostname || 'localhost',
      port: url.port ? parseInt(url.port, 10) : 6379,
    };
  } catch {
    return { host: 'localhost', port: 6379 };
  }
}

// ═══════════════════════════════════════════════════════════
// Mock Transport (used when Redis is unavailable)
// ═══════════════════════════════════════════════════════════

const _mockHandlers: Set<(event: MyceliumEvent) => void> = new Set();

function createMockBridge(config: RedisBridgeConfig): RedisBridge {
  const prefix = `[mycelium:mock][${config.channel}]`;

  return {
    transport: 'mock',

    async publish(event: MyceliumEvent): Promise<void> {
      console.log(`${prefix} PUBLISH`, JSON.stringify(event));
      // Also fan-out to in-process subscribers so tests work without Redis
      for (const handler of _mockHandlers) {
        try {
          handler(event);
        } catch (err) {
          console.error(`${prefix} subscriber error`, err);
        }
      }
    },

    subscribe(handler: (event: MyceliumEvent) => void): () => void {
      _mockHandlers.add(handler);
      console.log(`${prefix} SUBSCRIBE (mock — ${_mockHandlers.size} subscriber(s))`);
      return () => {
        _mockHandlers.delete(handler);
      };
    },

    async close(): Promise<void> {
      _mockHandlers.clear();
      console.log(`${prefix} CLOSE (mock)`);
    },
  };
}

// ═══════════════════════════════════════════════════════════
// Redis Transport
// ═══════════════════════════════════════════════════════════

interface RedisTransportState {
  publisher: RespSocket;
  subscribers: Map<(event: MyceliumEvent) => void, RespSocket>;
}

async function createRedisBridgeTransport(
  config: RedisBridgeConfig,
  { host, port }: { host: string; port: number },
): Promise<RedisBridge> {
  const publisher = await connectRespSocket(host, port);

  const state: RedisTransportState = {
    publisher,
    subscribers: new Map(),
  };

  return {
    transport: 'redis',

    async publish(event: MyceliumEvent): Promise<void> {
      const message = JSON.stringify(event);
      const cmd = encodeRespArray('PUBLISH', config.channel, message);
      await new Promise<void>((resolve, reject) => {
        state.publisher.socket.once('error', reject);
        state.publisher.write(cmd);
        // PUBLISH response is an integer — we fire and don't block for it
        setImmediate(resolve);
      });
    },

    subscribe(handler: (event: MyceliumEvent) => void): () => void {
      // Each subscriber gets its own socket so the SUBSCRIBE command
      // doesn't block the shared publisher socket
      let subSocket: RespSocket | null = null;

      connectRespSocket(host, port)
        .then((sock) => {
          subSocket = sock;
          state.subscribers.set(handler, sock);

          const cmd = encodeRespArray('SUBSCRIBE', config.channel);
          sock.write(cmd);

          let buf = '';
          sock.socket.on('data', (chunk: Buffer) => {
            buf += chunk.toString();
            // Naive scan for the message payload line (3rd element of RESP array)
            // Full RESP2 parser is out of scope for this scaffold
            const lines = buf.split('\r\n');
            // A pub/sub message looks like: *3\r\n$7\r\nmessage\r\n$<channel-len>\r\n<channel>\r\n$<msg-len>\r\n<msg>\r\n
            for (let i = 0; i < lines.length - 1; i++) {
              if (lines[i] === '$' + lines[i + 1]?.length || lines[i].startsWith('$')) {
                const candidate = lines[i + 1];
                if (candidate && candidate.startsWith('{')) {
                  try {
                    const event = JSON.parse(candidate) as MyceliumEvent;
                    handler(event);
                    buf = '';
                  } catch {
                    // not valid JSON — keep buffering
                  }
                }
              }
            }
          });

          sock.socket.on('error', (err) => {
            console.error('[mycelium:redis-bridge] subscriber socket error', err);
          });
        })
        .catch((err) => {
          console.error('[mycelium:redis-bridge] failed to open subscriber socket', err);
        });

      return () => {
        if (subSocket) {
          state.subscribers.delete(handler);
          subSocket.destroy();
        }
      };
    },

    async close(): Promise<void> {
      for (const sock of state.subscribers.values()) {
        sock.destroy();
      }
      state.subscribers.clear();
      state.publisher.destroy();
    },
  };
}

// ═══════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════

/**
 * Create a RedisBridge from config.
 *
 * If REDIS_URL is not set AND no redisUrl is provided, or if the Redis
 * server is unreachable, falls back to a mock transport that logs events
 * to stdout and fans out to in-process subscribers.
 *
 * @example
 * ```ts
 * const bridge = await createRedisBridge({
 *   redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
 *   channel: 'egos:mycelium:events',
 *   publishOnMutation: true,
 * });
 * ```
 */
export async function createRedisBridge(config: RedisBridgeConfig): Promise<RedisBridge> {
  const effectiveUrl = config.redisUrl || process.env.REDIS_URL || '';

  if (!effectiveUrl) {
    console.warn('[mycelium:redis-bridge] REDIS_URL not set — using mock transport');
    return createMockBridge(config);
  }

  const { host, port } = parseRedisUrl(effectiveUrl);

  try {
    return await createRedisBridgeTransport(config, { host, port });
  } catch (err) {
    console.warn(
      `[mycelium:redis-bridge] Redis unreachable (${host}:${port}) — falling back to mock transport. Error: ${(err as Error).message}`,
    );
    return createMockBridge(config);
  }
}

/**
 * Publish a MyceliumEvent through the bridge.
 *
 * @example
 * ```ts
 * await publishEvent(bridge, {
 *   type: 'node_added',
 *   timestamp: new Date().toISOString(),
 *   payload: node,
 *   source: 'egos-kernel',
 * });
 * ```
 */
export async function publishEvent(bridge: RedisBridge, event: MyceliumEvent): Promise<void> {
  return bridge.publish(event);
}

/**
 * Subscribe to MyceliumEvents through the bridge.
 * Returns an unsubscribe function — call it to stop receiving events.
 *
 * @example
 * ```ts
 * const unsubscribe = subscribeToEvents(bridge, (event) => {
 *   console.log('received', event.type, event.source);
 * });
 * // later:
 * unsubscribe();
 * ```
 */
export function subscribeToEvents(
  bridge: RedisBridge,
  handler: (event: MyceliumEvent) => void,
): () => void {
  return bridge.subscribe(handler);
}

/**
 * Build a MyceliumEvent with current timestamp. Convenience helper.
 */
export function buildEvent(
  type: MyceliumEvent['type'],
  payload: unknown,
  source: string,
): MyceliumEvent {
  return {
    type,
    timestamp: new Date().toISOString(),
    payload,
    source,
  };
}
