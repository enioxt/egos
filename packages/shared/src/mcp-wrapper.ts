/**
 * MCP Wrapper — Unified Interface for Model Context Protocol Servers
 *
 * Type definitions for MCP integration.
 * Implementation delegated to actual MCP servers.
 */

// @public - Used for MCP interface definitions
export interface MCPCapability {
  name: string;
  status: 'enabled' | 'disabled';
  apiKey?: string;
  endpoint?: string;
}

// @public - Used for search results across MCPs
export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
  relevance: number;
}

// @public - Used for thinking session tracking
export interface ThinkingSession {
  id: string;
  thinking: string;
  depth: 'shallow' | 'moderate' | 'deep';
  tokenCount: number;
  executionTime: number;
}

// @public - Used for memory entry definitions
export interface MemoryEntry {
  id: string;
  key: string;
  value: unknown;
  timestamp: number;
  taskId?: string;
  tags: string[];
}
