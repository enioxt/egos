/**
 * EGOS Integration Contracts
 * Standardized interfaces for external integrations
 */

export type {
  SlackMessage,
  SlackAdapter,
} from './slack';
export { SlackAdapterImpl } from './slack';

export type {
  DiscordMessage,
  DiscordAdapter,
} from './discord';
export { DiscordAdapterImpl } from './discord';

export type {
  TelegramMessage,
  TelegramAdapter,
} from './telegram';
export { TelegramAdapterImpl } from './telegram';

export type {
  WhatsAppMessage,
  WhatsAppAdapter,
} from './whatsapp';
export { WhatsAppAdapterImpl } from './whatsapp';

export type {
  WebhookPayload,
  WebhookAdapter,
} from './webhook';
export { WebhookAdapterImpl } from './webhook';

export type {
  GitHubIssueEvent,
  GitHubAdapter,
} from './github';
export { GitHubAdapterImpl } from './github';
