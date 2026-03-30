/**
 * Circuit Breaker — EGOS-086
 *
 * Prevents cascading failures by tracking consecutive errors and
 * opening a circuit when a failure threshold is exceeded.
 *
 * States:
 *   CLOSED    — normal operation, all calls pass through
 *   OPEN      — circuit tripped, calls rejected immediately
 *   HALF_OPEN — trial period after recoveryTimeout; one probe call is allowed
 *
 * Usage:
 *   const cb = new CircuitBreaker({ failureThreshold: 5, recoveryTimeout: 60_000, name: 'llm-api' });
 *   const result = await cb.execute(() => fetch('/api'));
 *
 * Zero external dependencies.
 */

// ── Types ──────────────────────────────────────────────────────────────────

export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface CircuitBreakerOptions {
  /** Number of consecutive failures before the circuit opens (default: 5) */
  failureThreshold?: number;
  /** Milliseconds to wait before transitioning OPEN → HALF_OPEN (default: 60_000) */
  recoveryTimeout?: number;
  /** Human-readable name for logging (default: 'circuit') */
  name?: string;
  /** If provided, called whenever the circuit state changes */
  onStateChange?: (from: CircuitState, to: CircuitState, name: string) => void;
}

export interface CircuitBreakerStatus {
  state: CircuitState;
  failureCount: number;
  lastFailure: Date | null;
  /** Earliest time a probe call will be allowed (only relevant when OPEN) */
  nextRetry: Date | null;
}

// ── Class ──────────────────────────────────────────────────────────────────

export class CircuitBreaker {
  private readonly name: string;
  private readonly failureThreshold: number;
  private readonly recoveryTimeout: number;
  private readonly onStateChange?: CircuitBreakerOptions['onStateChange'];

  private state: CircuitState = 'CLOSED';
  private failureCount = 0;
  private lastFailure: Date | null = null;
  private openedAt: Date | null = null;

  constructor(options: CircuitBreakerOptions = {}) {
    this.name = options.name ?? 'circuit';
    this.failureThreshold = options.failureThreshold ?? 5;
    this.recoveryTimeout = options.recoveryTimeout ?? 60_000;
    this.onStateChange = options.onStateChange;
  }

  // ── Public API ─────────────────────────────────────────────────────────

  /**
   * Execute a function guarded by the circuit breaker.
   * Throws `CircuitOpenError` when the circuit is OPEN and the recovery
   * window has not elapsed yet.
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    this.transitionIfNeeded();

    if (this.state === 'OPEN') {
      throw new CircuitOpenError(this.name, this.nextRetryDate());
    }

    // HALF_OPEN: allow exactly one probe call
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  /** Returns a snapshot of the current circuit state. */
  getState(): CircuitBreakerStatus {
    this.transitionIfNeeded();
    return {
      state: this.state,
      failureCount: this.failureCount,
      lastFailure: this.lastFailure,
      nextRetry: this.nextRetryDate(),
    };
  }

  /** Manually reset the circuit to CLOSED and clear all counters. */
  reset(): void {
    const prev = this.state;
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.lastFailure = null;
    this.openedAt = null;
    if (prev !== 'CLOSED') {
      this.onStateChange?.(prev, 'CLOSED', this.name);
    }
  }

  // ── Private ─────────────────────────────────────────────────────────────

  private onSuccess(): void {
    if (this.state === 'HALF_OPEN') {
      // Probe succeeded — close the circuit
      this.setState('CLOSED');
      this.failureCount = 0;
      this.lastFailure = null;
      this.openedAt = null;
    } else {
      // CLOSED: reset consecutive failure count on any success
      this.failureCount = 0;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailure = new Date();

    if (this.state === 'HALF_OPEN') {
      // Probe failed — go back to OPEN
      this.openedAt = new Date();
      this.setState('OPEN');
      return;
    }

    if (this.state === 'CLOSED' && this.failureCount >= this.failureThreshold) {
      this.openedAt = new Date();
      this.setState('OPEN');
    }
  }

  /** Check if enough time has passed to move OPEN → HALF_OPEN. */
  private transitionIfNeeded(): void {
    if (this.state === 'OPEN' && this.openedAt) {
      const elapsed = Date.now() - this.openedAt.getTime();
      if (elapsed >= this.recoveryTimeout) {
        this.setState('HALF_OPEN');
      }
    }
  }

  private setState(next: CircuitState): void {
    const prev = this.state;
    if (prev === next) return;
    this.state = next;
    this.onStateChange?.(prev, next, this.name);
  }

  private nextRetryDate(): Date | null {
    if (this.state !== 'OPEN' || !this.openedAt) return null;
    return new Date(this.openedAt.getTime() + this.recoveryTimeout);
  }
}

// ── Error ──────────────────────────────────────────────────────────────────

export class CircuitOpenError extends Error {
  constructor(
    public readonly circuitName: string,
    public readonly nextRetry: Date | null,
  ) {
    const retryMsg = nextRetry
      ? ` Retry after ${nextRetry.toISOString()}.`
      : '';
    super(`Circuit "${circuitName}" is OPEN — call rejected.${retryMsg}`);
    this.name = 'CircuitOpenError';
  }
}
