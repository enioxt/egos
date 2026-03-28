/**
 * WhatsApp Integration Contract
 * Defines the interface for WhatsApp message adapters
 */

export interface WhatsAppMessage {
  to: string; // Phone number with country code
  body: string;
  media?: {
    type: 'image' | 'document' | 'audio' | 'video';
    url: string;
  };
  metadata?: Record<string, unknown>;
}

export interface WhatsAppAdapter {
  name: 'whatsapp';
  authenticate(credentials: Record<string, string>): Promise<void>;
  send(message: WhatsAppMessage): Promise<{ messageId: string; ok: boolean }>;
  listen(callback: (msg: WhatsAppMessage) => Promise<void>): Promise<void>;
  disconnect(): Promise<void>;
}

export class WhatsAppAdapterImpl implements WhatsAppAdapter {
  name = 'whatsapp' as const;

  async authenticate(credentials: Record<string, string>): Promise<void> {
    // TODO: Implement WhatsApp Business API authentication
    console.log('WhatsApp authentication not yet implemented');
  }

  async send(message: WhatsAppMessage): Promise<{ messageId: string; ok: boolean }> {
    // TODO: Implement WhatsApp Business API send message
    throw new Error('WhatsAppAdapterImpl.send not implemented');
  }

  async listen(callback: (msg: WhatsAppMessage) => Promise<void>): Promise<void> {
    // TODO: Implement WhatsApp webhook listener
    throw new Error('WhatsAppAdapterImpl.listen not implemented');
  }

  async disconnect(): Promise<void> {
    // TODO: Implement cleanup
  }
}
