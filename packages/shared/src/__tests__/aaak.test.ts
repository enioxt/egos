/**
 * AAAK Compression Tests
 *
 * Validates compression/decompression roundtrip and metrics.
 */

import { describe, it, expect } from 'bun:test';
import {
  compress,
  decompress,
  compressionRatio,
  tokenSavings,
  batchCompress,
  buildAAAKMemoryBlock,
} from '../aaak';

describe('AAAK Compression', () => {
  describe('Basic Compression', () => {
    it('should compress simple text', () => {
      const text = 'The user implemented a function for the agent configuration.';
      const compressed = compress(text);

      expect(compressed.length).toBeLessThan(text.length);
      expect(compressed).toContain('impl');
      expect(compressed).toContain('fn');
      expect(compressed).toContain('ag');
      expect(compressed).toContain('cfg');
    });

    it('should handle empty string', () => {
      expect(compress('')).toBe('');
      expect(decompress('')).toBe('');
    });

    it('should handle whitespace-only input', () => {
      expect(compress('   \n\t  ')).toBe('');
    });
  });

  describe('Roundtrip Compression', () => {
    it('should decompress to semantically equivalent text', () => {
      const original = 'The assistant created a new database table for storing agent memories.';
      const compressed = compress(original);
      const decompressed = decompress(compressed);

      // Decompressed should contain key terms
      expect(decompressed.toLowerCase()).toContain('assistant');
      expect(decompressed.toLowerCase()).toContain('database');
      expect(decompressed.toLowerCase()).toContain('table');
      expect(decompressed.toLowerCase()).toContain('agent');
      expect(decompressed.toLowerCase()).toContain('memories');
    });

    it('should preserve EGOS domain terms', () => {
      const text = 'The agent runtime manages multiple agents in the repository.';
      const compressed = compress(text);

      expect(compressed).toContain('ag');
      expect(compressed).toContain('repos');
    });
  });

  describe('Compression Metrics', () => {
    it('should achieve >50% compression for typical memory text', () => {
      const text = `
        ASSISTANT: I have implemented the memory store interface.
        USER: Please configure the database connection for production.
        ASSISTANT: The configuration has been updated with the correct parameters.
        USER: What is the status of the agent deployment?
        ASSISTANT: The agents are running in the development environment.
      `;

      const compressed = compress(text);
      const ratio = compressionRatio(text, compressed);

      expect(ratio).toBeLessThan(0.5); // >50% reduction
    });

    it('should report token savings', () => {
      const original = 'This is a test of the AAAK compression system for AI memories.';
      const compressed = compress(original);
      const savings = tokenSavings(original, compressed);

      expect(savings).toBeGreaterThan(0);
    });
  });

  describe('Structural Compression', () => {
    it('should compress markdown headers', () => {
      const text = '## Agent Configuration\n### Database Setup';
      const compressed = compress(text, { preserveStructure: true });

      expect(compressed).toContain('〔');
      expect(compressed).toContain('〕');
    });

    it('should compress bullet points', () => {
      const text = '- First item\n- Second item\n- Third item';
      const compressed = compress(text, { preserveStructure: true });

      expect(compressed).toContain('〖');
      expect(compressed).toContain('〗');
    });
  });

  describe('Batch Operations', () => {
    it('should compress multiple memories', () => {
      const memories = [
        'First conversation about agent configuration.',
        'Second discussion about memory storage.',
        'Third session on event bus architecture.',
      ];

      const compressed = batchCompress(memories);

      expect(compressed).toHaveLength(3);
      expect(compressed[0].length).toBeLessThan(memories[0].length);
      expect(compressed[1].length).toBeLessThan(memories[1].length);
      expect(compressed[2].length).toBeLessThan(memories[2].length);
    });
  });

  describe('Memory Block Builder', () => {
    it('should create AAAK memory block', () => {
      const memories = [
        'First memory summary',
        'Second memory summary',
        'Third memory summary',
      ];

      const block = buildAAAKMemoryBlock(memories);

      expect(block).toContain('〔AAAK-MEM〕');
      expect(block).toContain('〔/AAAK-MEM〕');
      expect(block).toContain('〖1〗');
      expect(block).toContain('〖2〗');
      expect(block).toContain('〖3〗');
    });

    it('should return empty string for no memories', () => {
      expect(buildAAAKMemoryBlock([])).toBe('');
    });
  });

  describe('Options', () => {
    it('should respect maxTokens option', () => {
      const text = 'A'.repeat(1000);
      const compressed = compress(text, { maxTokens: 10 });

      expect(estimateTokens(compressed)).toBeLessThanOrEqual(15); // Allow small margin
    });

    it('should work with aggressive=false', () => {
      const text = 'The user implemented a function.';
      const compressed = compress(text, { aggressive: false });

      // Without aggressive compression, should still work but less compressed
      expect(compressed.length).toBeGreaterThan(0);
    });
  });
});

// Helper function (not exported from module)
function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}
