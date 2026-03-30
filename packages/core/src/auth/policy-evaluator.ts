/**
 * EGOS-002.3: Default Policy Evaluator
 * 
 * Implements basic permission rules for different sources:
 * - Public read: anyone can read rules, docs (no auth required)
 * - GitHub: via GitHub token, can write/execute
 * - ChatGPT/Codex: identity from token, scoped to read
 * - Local execution: full scope, audit logged
 * 
 * Policies can be overridden via configuration.
 */

import { randomUUID } from 'node:crypto';
import type { Identity, ActivationRequest, ActivationResponse } from './contracts.ts';

/**
 * PolicyRule — Definition of what a source is allowed to do
 */
export interface PolicyRule {
  source: string;
  action?: 'read' | 'execute' | 'write' | 'deploy';
  resource?: string;
  scope: string;
  reason?: string;
}

/**
 * PolicyConfig — Configuration for the evaluator
 */
export interface PolicyConfig {
  policies?: PolicyRule[];
  allowPublicRead?: boolean;
  requireAuth?: boolean;
  defaultScope?: string;
}

/**
 * DefaultPolicyEvaluator — Evaluates activation requests against rules
 */
export class DefaultPolicyEvaluator {
  private policies: PolicyRule[];
  private allowPublicRead: boolean;
  private requireAuth: boolean;
  private defaultScope: string;

  constructor(config: PolicyConfig = {}) {
    this.allowPublicRead = config.allowPublicRead !== false;
    this.requireAuth = config.requireAuth !== true;
    this.defaultScope = config.defaultScope || 'none';

    // Initialize with sensible defaults if not overridden
    this.policies = config.policies || this.getDefaultPolicies();
  }

  /**
   * Get default policies for all sources
   */
  private getDefaultPolicies(): PolicyRule[] {
    return [
      // Public read — anyone can read docs and rules
      {
        source: 'public',
        action: 'read',
        resource: 'egos:rules',
        scope: 'read',
        reason: 'Public read access to rules',
      },
      {
        source: 'public',
        action: 'read',
        resource: 'egos:docs',
        scope: 'read',
        reason: 'Public read access to documentation',
      },

      // GitHub — full access with token
      {
        source: 'github-actions',
        scope: 'read,execute,write,deploy',
        reason: 'GitHub Actions has full scope',
      },

      // ChatGPT — read-only via token
      {
        source: 'chatgpt',
        scope: 'read',
        reason: 'ChatGPT has read-only scope',
      },

      // Codex — read-only via token
      {
        source: 'codex',
        scope: 'read',
        reason: 'Codex has read-only scope',
      },

      // Claude Code — read-only (same as Codex)
      {
        source: 'claude-code',
        scope: 'read',
        reason: 'Claude Code has read-only scope',
      },

      // Local IDE — full scope (trusted execution)
      {
        source: 'local-ide',
        scope: 'read,execute,write,deploy',
        reason: 'Local IDE execution is fully trusted',
      },

      // API — depends on token scope
      {
        source: 'api',
        scope: 'read',
        reason: 'API access defaults to read-only',
      },
    ];
  }

  /**
   * Main evaluation method
   * Returns whether the request is authorized and what scope is granted
   */
  async evaluate(request: ActivationRequest): Promise<ActivationResponse> {
    const auditId = randomUUID();

    try {
      // Check if request is expired
      if (request.identity.expiresAt && request.identity.expiresAt < new Date()) {
        return {
          authorized: false,
          reasoning: "Identity expired",
          scope: 'none',
          auditId,
          context: { userId: request.identity.userId },
        };
      }

      // Check for public read
      if (this.allowPublicRead && request.action === 'read') {
        const publicRule = this.policies.find(
          (p) => p.source === 'public' && (!p.resource || p.resource === request.resource)
        );
        if (publicRule) {
          return {
            authorized: true,
            reasoning: publicRule.reason || 'Public read access granted',
            scope: publicRule.scope,
            auditId,
            context: {
              userId: 'public',
              source: 'public',
              expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
            },
          };
        }
      }

      // Check if token is present for non-public actions
      if (!request.identity.token && request.action !== 'read') {
        return {
          authorized: false,
          reasoning: "No token provided for action",
          scope: 'none',
          auditId,
          context: { userId: request.identity.userId },
        };
      }

      // Find matching policy
      const matchedPolicy = this.findMatchingPolicy(request);

      if (!matchedPolicy) {
        return {
          authorized: false,
          reasoning: "No policy found for source",
          scope: 'none',
          auditId,
          context: { userId: request.identity.userId },
        };
      }

      // Check if identity has required scopes
      const grantedScopes = matchedPolicy.scope.split(',');
      const actionScope = request.action;
      const hasScope = grantedScopes.some((s) => s.includes(actionScope));

      if (!hasScope && request.action !== 'read') {
        return {
          authorized: false,
          reasoning: "Identity does not have scope for action",
          scope: 'none',
          auditId,
          context: { userId: request.identity.userId, grantedScopes },
        };
      }

      // Authorization successful
      return {
        authorized: true,
        reasoning: matchedPolicy.reason || "Authorization granted",
        scope: matchedPolicy.scope,
        auditId,
        context: {
          userId: request.identity.userId,
          source: request.identity.source,
          scopes: request.identity.scopes,
          expiresAt: request.identity.expiresAt?.toISOString(),
        },
      };
    } catch (error) {
      return {
        authorized: false,
        reasoning: "Evaluation error",
        scope: 'none',
        auditId,
        context: { userId: request.identity.userId },
      };
    }
  }

  /**
   * Find matching policy for a request
   */
  private findMatchingPolicy(request: ActivationRequest): PolicyRule | undefined {
    // Exact match: source + action + resource
    let match = this.policies.find(
      (p) =>
        p.source === request.identity.source &&
        (!p.action || p.action === request.action) &&
        (!p.resource || p.resource === request.resource)
    );

    // Fallback: source + action
    if (!match) {
      match = this.policies.find(
        (p) => p.source === request.identity.source && (!p.action || p.action === request.action)
      );
    }

    // Fallback: source only
    if (!match) {
      match = this.policies.find((p) => p.source === request.identity.source);
    }

    return match;
  }

  /**
   * Add or override a policy
   */
  addPolicy(rule: PolicyRule): void {
    // Remove existing matching policy
    this.policies = this.policies.filter(
      (p) => !(p.source === rule.source && p.action === rule.action && p.resource === rule.resource)
    );
    // Add new policy
    this.policies.push(rule);
  }

  /**
   * Get all policies (for debugging/testing)
   */
  getPolicies(): PolicyRule[] {
    return [...this.policies];
  }
}
