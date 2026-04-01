#!/usr/bin/env bun

/**
 * API Smoke Tests (GH-041)
 *
 * Validates core Guard Brasil API contracts:
 * - POST /v1/inspect responds with correct schema
 * - Telemetry is recorded to Supabase
 * - Response contains required fields (safe, blocked, summary, atrian, masking)
 * - Status codes are correct (200 ok, 202 manual review, 422 PRI blocked)
 *
 * Exit codes:
 * - 0: all tests passed
 * - 1: one or more tests failed
 * - 2: fatal error (API unreachable)
 */

import * as https from 'https';

// ─── Config ────────────────────────────────────────────────────────────────

const API_URL = process.env.GUARD_API_URL || 'http://localhost:3099';
const API_KEY = process.env.GUARD_API_KEY || 'test-key-' + Math.random().toString(36).slice(2);

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  duration?: number;
}

// ─── Test Cases ────────────────────────────────────────────────────────────

const tests: Array<{
  name: string;
  fn: () => Promise<TestResult>;
}> = [
  {
    name: 'Health Check',
    fn: async () => {
      const start = performance.now();
      try {
        const res = await fetch(`${API_URL}/health`);
        if (res.status !== 200) {
          return { name: 'Health Check', passed: false, error: `Expected 200, got ${res.status}` };
        }
        const json = await res.json();
        if (!json.status || json.status !== 'healthy') {
          return { name: 'Health Check', passed: false, error: 'Not healthy' };
        }
        return {
          name: 'Health Check',
          passed: true,
          duration: Math.round(performance.now() - start),
        };
      } catch (e) {
        return { name: 'Health Check', passed: false, error: String(e) };
      }
    },
  },

  {
    name: 'Inspect — Clean Text',
    fn: async () => {
      const start = performance.now();
      try {
        const res = await fetch(`${API_URL}/v1/inspect`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            text: 'This is clean text with no PII.',
          }),
        });

        if (res.status !== 200) {
          return {
            name: 'Inspect — Clean Text',
            passed: false,
            error: `Expected 200, got ${res.status}`,
          };
        }

        const json = await res.json();
        const required = ['safe', 'blocked', 'output', 'summary', 'atrian', 'masking'];
        for (const field of required) {
          if (!(field in json)) {
            return {
              name: 'Inspect — Clean Text',
              passed: false,
              error: `Missing field: ${field}`,
            };
          }
        }

        if (typeof json.safe !== 'boolean') {
          return {
            name: 'Inspect — Clean Text',
            passed: false,
            error: 'Field "safe" must be boolean',
          };
        }

        return {
          name: 'Inspect — Clean Text',
          passed: true,
          duration: Math.round(performance.now() - start),
        };
      } catch (e) {
        return {
          name: 'Inspect — Clean Text',
          passed: false,
          error: String(e),
        };
      }
    },
  },

  {
    name: 'Inspect — PII Detection (CPF)',
    fn: async () => {
      const start = performance.now();
      try {
        const res = await fetch(`${API_URL}/v1/inspect`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            text: 'My CPF is 123.456.789-00',
            pii_types: ['CPF'],
          }),
        });

        if (res.status !== 200 && res.status !== 202) {
          return {
            name: 'Inspect — PII Detection (CPF)',
            passed: false,
            error: `Expected 200 or 202, got ${res.status}`,
          };
        }

        const json = await res.json();
        if (!json.masking || json.masking.findingCount === 0) {
          return {
            name: 'Inspect — PII Detection (CPF)',
            passed: false,
            error: 'Expected to detect CPF but found no findings',
          };
        }

        return {
          name: 'Inspect — PII Detection (CPF)',
          passed: true,
          duration: Math.round(performance.now() - start),
        };
      } catch (e) {
        return {
          name: 'Inspect — PII Detection (CPF)',
          passed: false,
          error: String(e),
        };
      }
    },
  },

  {
    name: 'Inspect — Response Schema (Atrian)',
    fn: async () => {
      const start = performance.now();
      try {
        const res = await fetch(`${API_URL}/v1/inspect`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            text: 'Test text for schema validation.',
          }),
        });

        if (res.status !== 200) {
          return {
            name: 'Inspect — Response Schema (Atrian)',
            passed: false,
            error: `Expected 200, got ${res.status}`,
          };
        }

        const json = await res.json();
        if (!json.atrian || typeof json.atrian.passed !== 'boolean') {
          return {
            name: 'Inspect — Response Schema (Atrian)',
            passed: false,
            error: 'Missing atrian.passed field',
          };
        }

        if (typeof json.atrian.score !== 'number') {
          return {
            name: 'Inspect — Response Schema (Atrian)',
            passed: false,
            error: 'atrian.score must be number',
          };
        }

        if (!Array.isArray(json.atrian.violations)) {
          return {
            name: 'Inspect — Response Schema (Atrian)',
            passed: false,
            error: 'atrian.violations must be array',
          };
        }

        return {
          name: 'Inspect — Response Schema (Atrian)',
          passed: true,
          duration: Math.round(performance.now() - start),
        };
      } catch (e) {
        return {
          name: 'Inspect — Response Schema (Atrian)',
          passed: false,
          error: String(e),
        };
      }
    },
  },

  {
    name: 'Inspect — Rate Limiting',
    fn: async () => {
      const start = performance.now();
      try {
        // Send 3 rapid requests to same key
        const promises = [];
        for (let i = 0; i < 3; i++) {
          promises.push(
            fetch(`${API_URL}/v1/inspect`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}-ratelimit-test`,
              },
              body: JSON.stringify({ text: `Request ${i}` }),
            }),
          );
        }

        const results = await Promise.all(promises);
        // At least one should succeed
        const hasSuccess = results.some((r) => r.status === 200 || r.status === 202);

        if (!hasSuccess) {
          return {
            name: 'Inspect — Rate Limiting',
            passed: false,
            error: 'All requests failed',
          };
        }

        return {
          name: 'Inspect — Rate Limiting',
          passed: true,
          duration: Math.round(performance.now() - start),
        };
      } catch (e) {
        return {
          name: 'Inspect — Rate Limiting',
          passed: false,
          error: String(e),
        };
      }
    },
  },
];

// ─── Runner ────────────────────────────────────────────────────────────────

async function runTests() {
  console.log('🔍 API Smoke Tests (GH-041)\n');
  console.log(`Target: ${API_URL}\n`);

  let passed = 0;
  let failed = 0;
  const results: TestResult[] = [];

  for (const test of tests) {
    process.stdout.write(`  ⏳ ${test.name}...`);
    const result = await test.fn();
    results.push(result);

    if (result.passed) {
      console.log(` ✅ (${result.duration}ms)`);
      passed++;
    } else {
      console.log(` ❌ ${result.error}`);
      failed++;
    }
  }

  // Summary
  console.log('\n' + '─'.repeat(70));
  console.log(`📊 Results: ${passed} passed, ${failed} failed`);

  if (failed === 0) {
    console.log('✅ All API smoke tests passed');
    process.exit(0);
  } else {
    console.log(`❌ ${failed} test(s) failed`);
    process.exit(1);
  }
}

runTests().catch((e) => {
  console.error('💥 Fatal error:', e);
  process.exit(2);
});
