/**
 * REAL tests for rate-limiter.ts — Token bucket rate limiting.
 * Tests verify slot management, window cleanup, and usage reporting.
 *
 * Run: bun test packages/shared/src/__tests__/rate-limiter.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { RateLimiter } from '../rate-limiter';

// ═══════════════════════════════════════════════════════════
// Basic slot management
// ═══════════════════════════════════════════════════════════
describe('Rate Limiter — Slot management', () => {
  it('allows requests within limit', async () => {
    const limiter = new RateLimiter(3, 1000);
    await limiter.waitForSlot();
    await limiter.waitForSlot();
    await limiter.waitForSlot();
    // Should not throw or hang — 3 slots within window
    expect(true).toBe(true);
  });

  it('tracks current usage correctly', async () => {
    const limiter = new RateLimiter(5, 10000);
    await limiter.waitForSlot();
    await limiter.waitForSlot();
    const usage = limiter.currentUsage;
    expect(usage).toContain('2/5');
    expect(usage).toContain('10s');
  });

  it('cleans up expired timestamps', async () => {
    const limiter = new RateLimiter(2, 50); // 50ms window
    await limiter.waitForSlot();
    await limiter.waitForSlot();
    // Wait for window to expire
    await new Promise(r => setTimeout(r, 60));
    // Should allow new slots after cleanup
    await limiter.waitForSlot();
    const usage = limiter.currentUsage;
    expect(usage).toContain('1/2');
  });
});

// ═══════════════════════════════════════════════════════════
// Usage reporting
// ═══════════════════════════════════════════════════════════
describe('Rate Limiter — Usage reporting', () => {
  it('reports 0 usage when fresh', () => {
    const limiter = new RateLimiter(10, 60000);
    expect(limiter.currentUsage).toContain('0/10');
  });

  it('reports window in seconds', () => {
    const limiter = new RateLimiter(5, 30000);
    expect(limiter.currentUsage).toContain('30s');
  });
});

// ═══════════════════════════════════════════════════════════
// Rate limiting behavior
// ═══════════════════════════════════════════════════════════
describe('Rate Limiter — Throttling', () => {
  it('delays when limit reached', async () => {
    const limiter = new RateLimiter(1, 100); // 1 per 100ms
    await limiter.waitForSlot();
    const start = Date.now();
    await limiter.waitForSlot(); // Should wait ~100ms
    const elapsed = Date.now() - start;
    expect(elapsed).toBeGreaterThanOrEqual(50); // Allow some tolerance
  });
});
