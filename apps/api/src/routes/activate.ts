/**
 * EGOS-002.4: Activation Endpoint
 * 
 * POST /auth/activate
 * 
 * Evaluates activation requests from any tool and returns authorization decision
 * with audit trail. This is the main entry point for the Universal Activation Layer.
 */

import { v4 as uuidv4 } from 'uuid';
import { ActivationRequestSchema, ActivationResponseSchema } from '@egos/core';
import { DefaultPolicyEvaluator } from '@egos/core';
import { ConsoleAuditLogger } from '@egos/audit';
import type { AuditEntry } from '@egos/audit';

/**
 * Request body type for POST /auth/activate
 */
interface ActivateRequestBody {
  source: 'chatgpt' | 'codex' | 'claude-code' | 'local-ide' | 'github-actions' | 'api' | 'custom';
  token?: string;
  userId?: string;
  action: 'read' | 'execute' | 'write' | 'deploy';
  resource: string;
  context?: Record<string, unknown>;
}

/**
 * ActivateHandler - Main request handler for activation endpoint
 */
export class ActivateHandler {
  private evaluator: DefaultPolicyEvaluator;
  private auditLogger: ConsoleAuditLogger;

  constructor(evaluator?: DefaultPolicyEvaluator, auditLogger?: ConsoleAuditLogger) {
    this.evaluator = evaluator || new DefaultPolicyEvaluator();
    this.auditLogger = auditLogger || new ConsoleAuditLogger();
  }

  /**
   * Handle POST /auth/activate request
   */
  async handle(req: any, res: any): Promise<void> {
    try {
      // Parse and validate request body
      const body = req.body as ActivateRequestBody;

      // Validate required fields
      if (!body.source || !body.action || !body.resource) {
        res.status(400).json({
          authorized: false,
          reasoning: 'Missing required fields: source, action, resource',
          scope: 'none',
          auditId: uuidv4(),
          context: {},
        });
        return;
      }

      // Extract user ID from token or request
      const userId = body.userId || this.extractUserIdFromToken(body.token, body.source);

      // Create activation request
      const activationRequest = {
        identity: {
          userId,
          source: body.source,
          scopes: this.getScopesFromToken(body.token, body.source),
          token: body.token,
          metadata: body.context,
        },
        action: body.action,
        resource: body.resource,
        context: body.context,
      };

      // Validate request schema
      const validatedRequest = ActivationRequestSchema.parse(activationRequest);

      // Evaluate activation request
      const response = await this.evaluator.evaluate(validatedRequest);

      // Validate response schema
      const validatedResponse = ActivationResponseSchema.parse(response);

      // Log audit entry
      const auditEntry: AuditEntry = {
        id: response.auditId,
        timestamp: new Date(),
        identity: validatedRequest.identity,
        action: validatedRequest.action,
        resource: validatedRequest.resource,
        result: response.authorized ? 'allowed' : 'denied',
        reasoning: response.reasoning,
        context: {
          source: body.source,
          requestContext: body.context,
          ipAddress: req.ip,
          userAgent: req.get('user-agent'),
        },
      };

      await this.auditLogger.log(auditEntry);

      // Return response
      res.status(response.authorized ? 200 : 403).json(validatedResponse);
    } catch (err) {
      // Log handler
      console.error('ACTIVATE_ERROR', err);

      // Return error response
      const auditId = uuidv4();
      res.status(500).json({
        authorized: false,
        reasoning: 'Server error',
        scope: 'none',
        auditId,
        context: { error: true },
      });
    }
  }

  /**
   * Extract user ID from token based on source
   */
  private extractUserIdFromToken(token?: string, source?: string): string {
    if (!token) {
      return source === 'local-ide' ? 'local-user' : `${source}-anonymous`;
    }

    switch (source) {
      case 'github-actions':
        return `github-${token.substring(0, 10)}`;
      case 'chatgpt':
        return `chatgpt-${token.substring(0, 10)}`;
      case 'codex':
        return `codex-${token.substring(0, 10)}`;
      case 'claude-code':
        return `claude-code-${token.substring(0, 10)}`;
      default:
        return `user-${token.substring(0, 10)}`;
    }
  }

  /**
   * Extract scopes from token based on source
   */
  private getScopesFromToken(token?: string, source?: string): string[] {
    if (!token) {
      switch (source) {
        case 'chatgpt':
        case 'codex':
        case 'claude-code':
          return ['read'];
        case 'github-actions':
          return ['read', 'execute', 'write', 'deploy'];
        case 'local-ide':
          return ['*'];
        default:
          return ['read'];
      }
    }

    return source === 'github-actions' ? ['read', 'execute', 'write', 'deploy'] : ['read'];
  }
}

/**
 * Express middleware factory for activation endpoint
 * Usage: app.post('/auth/activate', activateRoute)
 */
export function createActivateRoute(
  evaluator?: DefaultPolicyEvaluator,
  auditLogger?: ConsoleAuditLogger
) {
  const handler = new ActivateHandler(evaluator, auditLogger);
  return (req: any, res: any) => handler.handle(req, res);
}

/**
 * Type exports
 */
export type { ActivateRequestBody };
