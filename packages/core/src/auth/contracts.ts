/**
 * EGOS-002: Universal Activation Layer — Identity, Permission, Audit Framework
 * 
 * Identity & Permission Contracts define the core structures for any tool
 * (ChatGPT, Codex, Claude Code, IDE) to authenticate and request resources
 * under controlled identity with audit trails.
 */

const SOURCES = ['chatgpt', 'codex', 'claude-code', 'local-ide', 'github-actions', 'api', 'custom'] as const;
const ACTIONS = ['read', 'execute', 'write', 'deploy'] as const;

function asRecord(input: unknown, label: string): Record<string, unknown> {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error(`${label} must be an object`);
  return input as Record<string, unknown>;
}

function asString(input: unknown, label: string): string {
  if (typeof input !== 'string' || input.trim().length === 0) throw new Error(`${label} is required`);
  return input;
}

function asEnum<T extends readonly string[]>(input: unknown, values: T, label: string): T[number] {
  if (typeof input !== 'string' || !values.includes(input as T[number])) throw new Error(`${label} is invalid`);
  return input as T[number];
}

function asStringArray(input: unknown): string[] {
  if (input === undefined) return [];
  if (!Array.isArray(input) || input.some((item) => typeof item !== 'string')) throw new Error('scopes must be a string array');
  return input;
}

function asOptionalDate(input: unknown): Date | undefined {
  if (input === undefined) return undefined;
  const date = input instanceof Date ? input : new Date(String(input));
  if (Number.isNaN(date.valueOf())) throw new Error('expiresAt is invalid');
  return date;
}

function asOptionalObject(input: unknown, label: string): Record<string, unknown> | undefined {
  if (input === undefined) return undefined;
  return asRecord(input, label);
}

export interface Identity {
  userId: string;
  source: 'chatgpt' | 'codex' | 'claude-code' | 'local-ide' | 'github-actions' | 'api' | 'custom';
  scopes: string[];
  token?: string;
  expiresAt?: Date;
  metadata?: Record<string, unknown>;
}

export const IdentitySchema = {
  parse(input: unknown): Identity {
    const data = asRecord(input, 'identity');
    return {
      userId: asString(data.userId, 'userId'),
      source: asEnum(data.source, SOURCES, 'source'),
      scopes: asStringArray(data.scopes),
      token: data.token === undefined ? undefined : asString(data.token, 'token'),
      expiresAt: asOptionalDate(data.expiresAt),
      metadata: asOptionalObject(data.metadata, 'metadata'),
    };
  },
};

export interface ActivationRequest {
  identity: Identity;
  action: 'read' | 'execute' | 'write' | 'deploy';
  resource: string;
  context?: Record<string, unknown>;
}

export const ActivationRequestSchema = {
  parse(input: unknown): ActivationRequest {
    const data = asRecord(input, 'activationRequest');
    return {
      identity: IdentitySchema.parse(data.identity),
      action: asEnum(data.action, ACTIONS, 'action'),
      resource: asString(data.resource, 'resource'),
      context: asOptionalObject(data.context, 'context'),
    };
  },
};

export interface ActivationResponse {
  authorized: boolean;
  reasoning: string;
  scope: string;
  auditId: string;
  context: Record<string, unknown>;
}

export const ActivationResponseSchema = {
  parse(input: unknown): ActivationResponse {
    const data = asRecord(input, 'activationResponse');
    if (typeof data.authorized !== 'boolean') throw new Error('authorized must be a boolean');
    return {
      authorized: data.authorized,
      reasoning: asString(data.reasoning, 'reasoning'),
      scope: asString(data.scope, 'scope'),
      auditId: asString(data.auditId, 'auditId'),
      context: asRecord(data.context, 'context'),
    };
  },
};
