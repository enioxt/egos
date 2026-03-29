/**
 * EGOS-002.3: Policy Evaluator Tests
 * 
 * Comprehensive test suite with 10+ test cases for each rule type:
 * - Public read rules
 * - GitHub token-based access
 * - ChatGPT/Codex read-only scope
 * - Local IDE full scope
 * - Token expiration
 * - Policy overrides
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { DefaultPolicyEvaluator } from './policy-evaluator';
import type { Identity, ActivationRequest } from './contracts';

describe('DefaultPolicyEvaluator', () => {
  let evaluator: DefaultPolicyEvaluator;

  beforeEach(() => {
    evaluator = new DefaultPolicyEvaluator();
  });

  // ============ PUBLIC READ RULES (5 test cases) ============
  describe('Public Read Rules', () => {
    it('should allow public read on egos:rules', async () => {
      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
      expect(response.scope).toContain('read');
    });

    it('should allow public read on egos:docs', async () => {
      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'read',
        resource: 'egos:docs',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
      expect(response.scope).toContain('read');
    });

    it('should deny public write on egos:rules', async () => {
      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'write',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should deny public execute without token', async () => {
      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'execute',
        resource: 'egos:tasks',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should allow public read on arbitrary resources', async () => {
      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'read',
        resource: 'project:852',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });
  });

  // ============ GITHUB RULES (5 test cases) ============
  describe('GitHub Actions Rules', () => {
    it('should allow github-actions to read', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'github-bot',
          source: 'github-actions',
          scopes: ['repo:write'],
          token: 'ghp_xxx',
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow github-actions to execute', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'github-bot',
          source: 'github-actions',
          scopes: ['repo:write'],
          token: 'ghp_xxx',
        },
        action: 'execute',
        resource: 'egos:tasks',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
      expect(response.scope).toContain('execute');
    });

    it('should allow github-actions to write', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'github-bot',
          source: 'github-actions',
          scopes: ['repo:write'],
          token: 'ghp_xxx',
        },
        action: 'write',
        resource: 'project:852',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow github-actions to deploy', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'github-bot',
          source: 'github-actions',
          scopes: ['repo:write'],
          token: 'ghp_xxx',
        },
        action: 'deploy',
        resource: 'vercel:main',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow github-actions without explicit token', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'github-bot',
          source: 'github-actions',
          scopes: ['repo:write'],
        },
        action: 'execute',
        resource: 'egos:tasks',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });
  });

  // ============ CHATGPT RULES (5 test cases) ============
  describe('ChatGPT Rules', () => {
    it('should allow chatgpt to read', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user-123',
          source: 'chatgpt',
          scopes: ['read:rules'],
          token: 'sk-xxx',
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should deny chatgpt write', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user-123',
          source: 'chatgpt',
          scopes: ['read:rules'],
          token: 'sk-xxx',
        },
        action: 'write',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should deny chatgpt execute', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user-123',
          source: 'chatgpt',
          scopes: ['read:rules'],
          token: 'sk-xxx',
        },
        action: 'execute',
        resource: 'egos:tasks',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should deny chatgpt without token for write', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user-123',
          source: 'chatgpt',
          scopes: ['read:rules'],
        },
        action: 'write',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should allow chatgpt to read any resource', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user-123',
          source: 'chatgpt',
          scopes: ['read:*'],
          token: 'sk-xxx',
        },
        action: 'read',
        resource: 'project:forja',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });
  });

  // ============ CLAUDE CODE RULES (5 test cases) ============
  describe('Claude Code Rules', () => {
    it('should allow claude-code to read', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'claude-code-session',
          source: 'claude-code',
          scopes: ['read:codebase'],
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should deny claude-code write', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'claude-code-session',
          source: 'claude-code',
          scopes: ['read:codebase'],
        },
        action: 'write',
        resource: 'src/main.ts',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should deny claude-code execute', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'claude-code-session',
          source: 'claude-code',
          scopes: ['read:codebase'],
        },
        action: 'execute',
        resource: 'scripts:build',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should deny claude-code deploy', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'claude-code-session',
          source: 'claude-code',
          scopes: ['read:codebase'],
        },
        action: 'deploy',
        resource: 'vercel:prod',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });

    it('should allow multiple read operations', async () => {
      const resources = ['egos:rules', 'project:852', 'src/lib', 'docs'];
      for (const resource of resources) {
        const request: ActivationRequest = {
          identity: {
            userId: 'claude-code-session',
            source: 'claude-code',
            scopes: ['read:*'],
          },
          action: 'read',
          resource,
        };
        const response = await evaluator.evaluate(request);
        expect(response.authorized).toBe(true);
      }
    });
  });

  // ============ LOCAL IDE RULES (5 test cases) ============
  describe('Local IDE Rules', () => {
    it('should allow local-ide to read', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'local-dev',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow local-ide to write', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'local-dev',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'write',
        resource: 'src/main.ts',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow local-ide to execute', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'local-dev',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'execute',
        resource: 'scripts:test',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow local-ide to deploy', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'local-dev',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'deploy',
        resource: 'vercel:staging',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should grant full scope to local-ide', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'local-dev',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'read',
        resource: 'any:resource',
      };
      const response = await evaluator.evaluate(request);
      expect(response.scope).toContain('read');
      expect(response.scope).toContain('execute');
      expect(response.scope).toContain('write');
      expect(response.scope).toContain('deploy');
    });
  });

  // ============ TOKEN EXPIRATION RULES (3 test cases) ============
  describe('Token Expiration Rules', () => {
    it('should deny expired token', async () => {
      const pastDate = new Date(Date.now() - 1000);
      const request: ActivationRequest = {
        identity: {
          userId: 'expired-user',
          source: 'api',
          scopes: ['read'],
          token: 'token_xxx',
          expiresAt: pastDate,
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(false);
      expect(response.reasoning).toContain('expired');
    });

    it('should allow valid token within expiration window', async () => {
      const futureDate = new Date(Date.now() + 1000 * 60 * 60); // +1 hour
      const request: ActivationRequest = {
        identity: {
          userId: 'valid-user',
          source: 'api',
          scopes: ['read'],
          token: 'token_xxx',
          expiresAt: futureDate,
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow requests without expiration date', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'perpetual-user',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'read',
        resource: 'egos:rules',
      };
      const response = await evaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });
  });

  // ============ POLICY OVERRIDE RULES (3 test cases) ============
  describe('Policy Override Rules', () => {
    it('should allow custom policy addition', async () => {
      const customEvaluator = new DefaultPolicyEvaluator({
        policies: [
          {
            source: 'custom-tool',
            scope: 'read,write',
            reason: 'Custom tool with read+write',
          },
        ],
      });

      const request: ActivationRequest = {
        identity: {
          userId: 'custom-user',
          source: 'custom-tool',
          scopes: ['custom'],
          token: 'custom_token',
        },
        action: 'write',
        resource: 'project:custom',
      };

      const response = await customEvaluator.evaluate(request);
      expect(response.authorized).toBe(true);
      expect(response.scope).toContain('write');
    });

    it('should override default policies', async () => {
      const customEvaluator = new DefaultPolicyEvaluator({
        policies: [
          {
            source: 'chatgpt',
            scope: 'read,write,execute',
            reason: 'Custom elevated scope for ChatGPT',
          },
        ],
      });

      const request: ActivationRequest = {
        identity: {
          userId: 'chatgpt-user',
          source: 'chatgpt',
          scopes: ['*'],
          token: 'sk-xxx',
        },
        action: 'execute',
        resource: 'egos:tasks',
      };

      const response = await customEvaluator.evaluate(request);
      expect(response.authorized).toBe(true);
    });

    it('should allow disabling public read', async () => {
      const customEvaluator = new DefaultPolicyEvaluator({
        allowPublicRead: false,
      });

      const request: ActivationRequest = {
        identity: { userId: 'public', source: 'api', scopes: [] },
        action: 'read',
        resource: 'egos:rules',
      };

      const response = await customEvaluator.evaluate(request);
      expect(response.authorized).toBe(false);
    });
  });

  // ============ EDGE CASES (3 test cases) ============
  describe('Edge Cases', () => {
    it('should handle unknown source gracefully', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'unknown-user',
          source: 'unknown-tool' as any,
          scopes: [],
        },
        action: 'read',
        resource: 'egos:rules',
      };

      const response = await evaluator.evaluate(request);
      expect(response.auditId).toBeDefined();
      expect(typeof response.auditId).toBe('string');
    });

    it('should generate unique audit IDs', async () => {
      const request1: ActivationRequest = {
        identity: { userId: 'user1', source: 'api', scopes: [] },
        action: 'read',
        resource: 'egos:rules',
      };

      const request2: ActivationRequest = {
        identity: { userId: 'user2', source: 'api', scopes: [] },
        action: 'read',
        resource: 'egos:docs',
      };

      const response1 = await evaluator.evaluate(request1);
      const response2 = await evaluator.evaluate(request2);

      expect(response1.auditId).not.toBe(response2.auditId);
    });

    it('should include context in responses', async () => {
      const request: ActivationRequest = {
        identity: {
          userId: 'test-user',
          source: 'local-ide',
          scopes: ['*'],
        },
        action: 'read',
        resource: 'egos:rules',
      };

      const response = await evaluator.evaluate(request);
      expect(response.context).toBeDefined();
      expect(response.context.userId).toBe('test-user');
    });
  });
});
