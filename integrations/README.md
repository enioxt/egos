# EGOS Integrations

Standardized adapters and contracts for integrating EGOS agents with external platforms and services.

## Available Integrations

### Messaging Platforms
- **Slack** — Enterprise messaging, threads, channels
- **Discord** — Community messaging, webhooks, embeds
- **Telegram** — Bot API, polling/webhooks
- **WhatsApp** — Business API, media support

### Generic
- **Webhook** — Generic HTTP endpoint sender/listener
- **GitHub** — Issue creation, webhook events

## Contract Pattern

Each integration follows a standardized interface:

```typescript
export interface SomeAdapter {
  name: 'some-platform';
  authenticate(credentials: unknown): Promise<void>;
  send(payload: SomePayload): Promise<{ ok: boolean; [key: string]: unknown }>;
  listen(callback: (msg: SomePayload) => Promise<void>): Promise<() => void>;
  disconnect(): Promise<void>;
}
```

## Creating a New Integration

1. Create `egos/integrations/_contracts/my-platform.ts`
2. Define interfaces (Message, Adapter)
3. Implement stub class with `// TODO:` comments
4. Export from `_contracts/index.ts`
5. Add documentation to this README

Example:

```typescript
// _contracts/my-platform.ts
export interface MyPlatformMessage {
  destination: string;
  content: string;
}

export interface MyPlatformAdapter {
  name: 'my-platform';
  authenticate(token: string): Promise<void>;
  send(message: MyPlatformMessage): Promise<{ id: string; ok: boolean }>;
  listen(callback: (msg: MyPlatformMessage) => Promise<void>): Promise<void>;
  disconnect(): Promise<void>;
}

export class MyPlatformAdapterImpl implements MyPlatformAdapter {
  name = 'my-platform' as const;
  // implement methods...
}
```

## Implementation Status

- [x] Contracts defined (all 6 platforms)
- [ ] Slack implementation
- [ ] Discord implementation
- [ ] Telegram implementation
- [ ] WhatsApp implementation
- [ ] Webhook implementation
- [ ] GitHub implementation

## Security

All integrations must:
- Read credentials from environment variables, never hardcode
- Validate tokens on authenticate()
- Log access via EGOS audit system
- Support graceful disconnect/cleanup
- Handle rate limits with exponential backoff
