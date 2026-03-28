/**
 * Webhook Integration Contract
 * Defines the interface for generic webhook adapters
 */

export interface WebhookPayload {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
  metadata?: Record<string, unknown>;
}

export interface WebhookAdapter {
  name: 'webhook';
  authenticate(credentials?: Record<string, string>): Promise<void>;
  send(payload: WebhookPayload): Promise<{ statusCode: number; ok: boolean }>;
  listen(
    path: string,
    callback: (payload: WebhookPayload) => Promise<void>
  ): Promise<() => void>;
  disconnect(): Promise<void>;
}

export class WebhookAdapterImpl implements WebhookAdapter {
  name = 'webhook' as const;

  async authenticate(credentials?: Record<string, string>): Promise<void> {
    // TODO: Implement optional auth (API keys, OAuth tokens)
    console.log('Webhook authentication not yet implemented');
  }

  async send(payload: WebhookPayload): Promise<{ statusCode: number; ok: boolean }> {
    // TODO: Implement HTTP request with retry logic
    throw new Error('WebhookAdapterImpl.send not implemented');
  }

  async listen(
    path: string,
    callback: (payload: WebhookPayload) => Promise<void>
  ): Promise<() => void> {
    // TODO: Implement HTTP server listener for incoming webhooks
    throw new Error('WebhookAdapterImpl.listen not implemented');
  }

  async disconnect(): Promise<void> {
    // TODO: Implement cleanup
  }
}
