/**
 * EGOS-002: Universal Activation Layer — Identity, Permission, Audit Framework
 * 
 * Identity & Permission Contracts define the core structures for any tool
 * (ChatGPT, Codex, Claude Code, IDE) to authenticate and request resources
 * under controlled identity with audit trails.
 */

import { z } from 'zod';

/**
 * Identity — Represents the requester and their capabilities
 * 
 * @field userId - Unique identifier for the user/entity making the request
 * @field source - Where the request originates from (tool, platform)
 * @field scopes - Array of capabilities granted to this identity
 * @field token - Optional authentication token (JWT, OAuth, etc.)
 * @field expiresAt - Optional expiration time for the identity session
 * @field metadata - Optional context-specific metadata
 */
export interface Identity {
  userId: string;
  source: 'chatgpt' | 'codex' | 'claude-code' | 'local-ide' | 'github-actions' | 'api' | 'custom';
  scopes: string[];
  token?: string;
  expiresAt?: Date;
  metadata?: Record<string, unknown>;
}

/**
 * Zod schema for Identity validation
 * Ensures runtime type safety when parsing untrusted input
 */
export const IdentitySchema = z.object({
  userId: z.string().min(1, 'userId is required'),
  source: z.enum(['chatgpt', 'codex', 'claude-code', 'local-ide', 'github-actions', 'api', 'custom']),
  scopes: z.array(z.string()).default([]),
  token: z.string().optional(),
  expiresAt: z.date().optional(),
  metadata: z.record(z.unknown()).optional(),
});

/**
 * ActivationRequest — Request to perform an action on a resource
 * 
 * @field identity - The identity making the request
 * @field action - What operation is being requested (read, execute, write, deploy)
 * @field resource - What is being accessed (e.g., "egos:rules", "project:852")
 * @field context - Optional contextual information about the request
 */
export interface ActivationRequest {
  identity: Identity;
  action: 'read' | 'execute' | 'write' | 'deploy';
  resource: string;
  context?: Record<string, unknown>;
}

/**
 * Zod schema for ActivationRequest validation
 */
export const ActivationRequestSchema = z.object({
  identity: IdentitySchema,
  action: z.enum(['read', 'execute', 'write', 'deploy']),
  resource: z.string().min(1, 'resource is required'),
  context: z.record(z.unknown()).optional(),
});

/**
 * ActivationResponse — Result of activation decision
 * 
 * @field authorized - Whether the action was allowed
 * @field reasoning - Human-readable explanation of the decision
 * @field scope - The actual scope granted (may be subset of requested)
 * @field auditId - Unique ID for audit trail lookup
 * @field context - Response context (userId, expiresAt, etc.)
 */
export interface ActivationResponse {
  authorized: boolean;
  reasoning: string;
  scope: string;
  auditId: string;
  context: Record<string, unknown>;
}

/**
 * Zod schema for ActivationResponse validation
 */
export const ActivationResponseSchema = z.object({
  authorized: z.boolean(),
  reasoning: z.string(),
  scope: z.string(),
  auditId: z.string().uuid('auditId must be a valid UUID'),
  context: z.record(z.unknown()),
});

/**
 * Type exports for use in other packages
 */
export type { Identity, ActivationRequest, ActivationResponse };
