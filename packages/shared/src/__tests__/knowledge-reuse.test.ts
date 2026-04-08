/**
 * Knowledge Reuse Tests
 *
 * Validates CORAL pattern: finding and reusing relevant discoveries.
 */

import { describe, it, expect } from 'bun:test';
import {
  findRelevantDiscoveries,
  prioritizeDiscoveries,
  shouldSkipExploration,
  markReused,
  getReuseStats,
  filterByAge,
  filterByScore,
  type Discovery,
} from '../knowledge-reuse';

describe('Knowledge Reuse', () => {
  const mockDiscoveries: Discovery[] = [
    {
      id: '1',
      repoUrl: 'https://github.com/user/repo1',
      gemName: 'gem-hunter-pattern',
      category: 'tool',
      score: 8.5,
      summary: 'Pattern for hunting gems in GitHub repositories',
      tags: ['github', 'pattern', 'discovery'],
      noveltyScore: 0.8,
      applicabilityScore: 0.9,
      reuseCount: 2,
      discoveredAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: '2',
      repoUrl: 'https://github.com/user/repo2',
      gemName: 'memory-store',
      category: 'library',
      score: 9.0,
      summary: 'Efficient memory storage for AI agents',
      tags: ['memory', 'storage', 'ai'],
      noveltyScore: 0.9,
      applicabilityScore: 0.7,
      reuseCount: 0,
      discoveredAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: '3',
      repoUrl: 'https://github.com/user/repo3',
      gemName: 'old-discovery',
      category: 'tool',
      score: 6.0,
      summary: 'Old discovery with low score',
      tags: ['old', 'deprecated'],
      noveltyScore: 0.3,
      applicabilityScore: 0.4,
      reuseCount: 5,
      discoveredAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  describe('findRelevantDiscoveries', () => {
    it('should find relevant discoveries by keywords', () => {
      const results = findRelevantDiscoveries(
        'pattern for discovery',
        mockDiscoveries
      );

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].discovery.gemName).toBe('gem-hunter-pattern');
    });

    it('should filter by score threshold', () => {
      const results = findRelevantDiscoveries(
        'discovery',
        mockDiscoveries,
        { minScore: 8.0 }
      );

      expect(results.every(r => r.discovery.score >= 8.0)).toBe(true);
    });

    it('should filter by age', () => {
      const results = findRelevantDiscoveries(
        'discovery',
        mockDiscoveries,
        { maxAgeDays: 10 }
      );

      expect(results.length).toBeLessThan(mockDiscoveries.length);
    });

    it('should score by tag matches', () => {
      const results = findRelevantDiscoveries(
        'storage system',
        mockDiscoveries,
        { tags: ['memory', 'storage'] }
      );

      // Should prioritize discovery with matching tags
      const memoryDiscovery = results.find(r =>
        r.discovery.tags.includes('memory')
      );
      expect(memoryDiscovery).toBeDefined();
    });

    it('should return empty array for no matches', () => {
      const results = findRelevantDiscoveries(
        'completely unrelated query',
        mockDiscoveries
      );

      expect(results).toEqual([]);
    });
  });

  describe('prioritizeDiscoveries', () => {
    it('should prioritize by novelty and applicability', () => {
      const result = prioritizeDiscoveries(mockDiscoveries, 10);

      expect(result.discoveries.length).toBeGreaterThan(0);
      // First should be high novelty + applicability
      expect(result.discoveries[0].noveltyScore).toBeGreaterThan(0.7);
    });

    it('should limit by budget', () => {
      const result = prioritizeDiscoveries(mockDiscoveries, 2);

      expect(result.discoveries.length).toBe(2);
    });

    it('should penalize frequently reused discoveries', () => {
      const result = prioritizeDiscoveries(mockDiscoveries, 10);

      // High reuse count should lower priority
      const highReuse = mockDiscoveries.find(d => d.reuseCount === 5)!;
      const highReuseIndex = result.discoveries.findIndex(
        d => d.id === highReuse.id
      );

      // Should not be first (lower priority due to reuse penalty)
      if (highReuseIndex >= 0) {
        expect(highReuseIndex).toBeGreaterThan(0);
      }
    });

    it('should report potential savings', () => {
      const result = prioritizeDiscoveries(mockDiscoveries, 1);

      expect(result.skippedCount).toBeGreaterThan(0);
      expect(result.potentialSavings).toBeGreaterThan(0);
    });
  });

  describe('shouldSkipExploration', () => {
    it('should recommend skip for recently discovered repo', () => {
      const result = shouldSkipExploration(
        'https://github.com/user/repo1',
        mockDiscoveries,
        14
      );

      expect(result.skip).toBe(true);
      expect(result.reason).toContain('Already discovered');
      expect(result.existingDiscovery).toBeDefined();
    });

    it('should allow exploration for new repo', () => {
      const result = shouldSkipExploration(
        'https://github.com/user/new-repo',
        mockDiscoveries,
        14
      );

      expect(result.skip).toBe(false);
    });

    it('should allow re-exploration of old discoveries', () => {
      const result = shouldSkipExploration(
        'https://github.com/user/repo3',
        mockDiscoveries,
        10 // 10 days threshold, repo3 is 20 days old
      );

      expect(result.skip).toBe(false);
    });
  });

  describe('markReused', () => {
    it('should increment reuse count', () => {
      const discovery = mockDiscoveries[0];
      const initialCount = discovery.reuseCount;

      const updated = markReused(discovery);

      expect(updated.reuseCount).toBe(initialCount + 1);
    });

    it('should set last reused timestamp', () => {
      const discovery = mockDiscoveries[0];

      const updated = markReused(discovery);

      expect(updated.lastReusedAt).toBeDefined();
    });
  });

  describe('Statistics', () => {
    it('should calculate reuse stats', () => {
      const stats = getReuseStats(mockDiscoveries);

      expect(stats.totalDiscoveries).toBe(3);
      expect(stats.totalReuses).toBe(7); // 2 + 0 + 5
      expect(stats.avgReusesPerDiscovery).toBeCloseTo(2.33, 1);
      expect(stats.topReused.length).toBe(3);
      expect(stats.neverReused).toBe(1);
    });
  });

  describe('Filters', () => {
    it('should filter by age', () => {
      const filtered = filterByAge(mockDiscoveries, 10);

      expect(filtered.length).toBeLessThan(mockDiscoveries.length);
      expect(filtered.every(d => {
        const age = (Date.now() - new Date(d.discoveredAt).getTime()) / (1000 * 60 * 60 * 24);
        return age <= 10;
      })).toBe(true);
    });

    it('should filter by score', () => {
      const filtered = filterByScore(mockDiscoveries, 8.0);

      expect(filtered.length).toBe(2);
      expect(filtered.every(d => d.score >= 8.0)).toBe(true);
    });
  });
});
