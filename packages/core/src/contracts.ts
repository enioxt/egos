export interface LoggerLike {
  info(message: string, meta?: unknown): void;
  warn(message: string, meta?: unknown): void;
  error(message: string, meta?: unknown): void;
}

export interface EgosContext {
  env: Record<string, string | undefined>;
  logger: LoggerLike;
}

export interface SearchQuery {
  text: string;
  filters?: Record<string, unknown>;
  limit?: number;
  userId?: string;
  channel?: string;
}
