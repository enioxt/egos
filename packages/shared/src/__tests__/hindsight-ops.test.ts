/**
 * Hindsight Operations Tests
 *
 * Validates Retain/Recall/Reflect biomimetic memory lifecycle.
 */

import { describe, it, expect } from 'bun:test';
import {
  retain,
  recall,
  reflect,
  batchRetain,
  getMemoryStats,
  pruneFadingMemories,
  type HindsightMemory,
} from '../hindsight-ops';

describe('Hindsight Operations', () => {
  describe('Retain', () => {
    it('should retain a new memory', () => {
      const memory = retain('Test memory content');

      expect(memory.id).toBeDefined();
      expect(memory.content).toBe('Test memory content');
      expect(memory.state).toBe('consolidating');
      expect(memory.accessCount).toBe(0);
      expect(memory.relevanceScore).toBeGreaterThan(0);
    });

    it('should encode content', () => {
      const memory = retain('  Multiple   spaces   and\n\nnewlines  ');

      expect(memory.content).toBe('Multiple spaces and newlines');
    });

    it('should set importance-based relevance', () => {
      const low = retain('Low', { importance: 'low' });
      const medium = retain('Medium', { importance: 'medium' });
      const high = retain('High', { importance: 'high' });
      const critical = retain('Critical', { importance: 'critical' });

      expect(low.relevanceScore).toBe(0.3);
      expect(medium.relevanceScore).toBe(0.5);
      expect(high.relevanceScore).toBe(0.8);
      expect(critical.relevanceScore).toBe(1.0);
    });

    it('should store context', () => {
      const memory = retain('Content', {
        sessionId: 'ses-123',
        agentId: 'ag-456',
        taskId: 'task-789',
      });

      expect(memory.context.sessionId).toBe('ses-123');
      expect(memory.context.agentId).toBe('ag-456');
      expect(memory.context.taskId).toBe('task-789');
    });
  });

  describe('Recall', () => {
    it('should recall relevant memories', () => {
      const memories = [
        retain('The agent configuration was updated successfully'),
        retain('Database connection established for production'),
        retain('User requested changes to the interface design'),
      ];

      const results = recall('agent configuration', memories);

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].content).toContain('agent');
    });

    it('should update access metrics on recall', () => {
      const memories = [retain('Test memory')];

      expect(memories[0].accessCount).toBe(0);
      expect(memories[0].lastAccessedAt).toBeNull();

      recall('test', memories);

      expect(memories[0].accessCount).toBe(1);
      expect(memories[0].lastAccessedAt).toBeDefined();
    });

    it('should transition consolidating to retrievable after 2 accesses', () => {
      const memories = [retain('Test memory')];

      recall('test', memories);
      expect(memories[0].state).toBe('consolidating');

      recall('test', memories);
      expect(memories[0].state).toBe('retrievable');
    });

    it('should respect limit option', () => {
      const memories = Array(10).fill(null).map((_, i) =>
        retain(`Memory ${i}`)
      );

      const results = recall('memory', memories, { limit: 3 });

      expect(results.length).toBe(3);
    });

    it('should exclude fading memories by default', () => {
      const memories = [
        retain('Active memory'),
        { ...retain('Fading memory'), state: 'fading' as const },
      ];

      const results = recall('memory', memories);

      expect(results.length).toBe(1);
      expect(results[0].content).toBe('Active memory');
    });
  });

  describe('Reflect', () => {
    it('should consolidate frequently accessed memories', () => {
      const memory = retain('Important decision');
      memory.accessCount = 5;

      const [consolidated] = reflect([memory], { consolidationThreshold: 3 });

      expect(consolidated.state).toBe('retrievable');
    });

    it('should mark inactive memories as fading', () => {
      const memory = retain('Old memory');
      memory.state = 'retrievable';
      memory.lastAccessedAt = new Date(Date.now() - 40 * 24 * 60 * 60 * 1000).toISOString(); // 40 days ago

      const [reflected] = reflect([memory], { fadingThreshold: 30 });

      expect(reflected.state).toBe('fading');
    });

    it('should boost relevance for consolidated memories', () => {
      const memory = retain('Important');
      memory.state = 'consolidating';
      memory.accessCount = 5;
      const initialRelevance = memory.relevanceScore;

      const [reflected] = reflect([memory], { consolidationThreshold: 3 });

      expect(reflected.relevanceScore).toBeGreaterThan(initialRelevance);
    });
  });

  describe('Batch Operations', () => {
    it('should retain multiple memories', () => {
      const contents = ['First', 'Second', 'Third'];
      const memories = batchRetain(contents);

      expect(memories.length).toBe(3);
      expect(memories[0].content).toBe('First');
      expect(memories[1].content).toBe('Second');
      expect(memories[2].content).toBe('Third');
    });
  });

  describe('Statistics', () => {
    it('should calculate memory stats', () => {
      const memories = [
        retain('A'),
        retain('B'),
        { ...retain('C'), state: 'retrievable' as const, accessCount: 5, relevanceScore: 0.9 },
        { ...retain('D'), state: 'fading' as const },
      ];

      const stats = getMemoryStats(memories);

      expect(stats.total).toBe(4);
      expect(stats.byState.consolidating).toBe(2);
      expect(stats.byState.retrievable).toBe(1);
      expect(stats.byState.fading).toBe(1);
      expect(stats.avgAccessCount).toBeGreaterThan(0);
      expect(stats.highRelevanceCount).toBe(1);
    });
  });

  describe('Pruning', () => {
    it('should prune old fading memories', () => {
      const oldFading = retain('Very old');
      oldFading.state = 'fading';
      oldFading.lastAccessedAt = new Date(Date.now() - 100 * 24 * 60 * 60 * 1000).toISOString();

      const memories = [
        retain('Active'),
        oldFading,
      ];

      const { kept, pruned } = pruneFadingMemories(memories, 60);

      expect(kept.length).toBe(1);
      expect(pruned.length).toBe(1);
      expect(pruned[0].content).toBe('Very old');
    });
  });
});
