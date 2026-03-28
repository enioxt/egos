export interface IntegrationManifest {
  id: string;
  channel: 'slack' | 'discord' | 'telegram' | 'whatsapp' | 'webhook' | 'github' | 'custom';
  name: string;
  version: string;
  authType: 'oauth' | 'api-key' | 'bot-token' | 'custom';
  events: string[];
  actions: string[];
  configSchemaRef?: string;
}

export interface EgosIntegration {
  manifest: IntegrationManifest;
  connect(): Promise<void>;
  disconnect?(): Promise<void>;
}
