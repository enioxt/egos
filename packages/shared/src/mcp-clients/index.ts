/**
 * MCP Clients Index
 *
 * Centralized export for all MCP client implementations
 * Provides easy access to database, LLM, git, filesystem, and calendar integrations
 */

export { DatabaseMCPClient, type QueryOptions, type SchemaInfo, type QueryResult } from './database-mcp-client';

export {
  LLMRouterMCPClient,
  type ModelConfig,
  type CostEstimate,
  type UsageRecord,
  type CostSummary,
  type ModelSelection,
} from './llm-router-mcp-client';

export {
  GitAdvancedMCPClient,
  type BlameEntry,
  type BranchStats,
  type MergeCommit,
  type GovernanceDrift,
  type CommitValidation,
} from './git-advanced-mcp-client';

export {
  FilesystemWatchMCPClient,
  type FileChangeEvent,
  type WatchSession,
  type SyncStatus,
  type FrozenZoneValidation,
} from './fs-watch-mcp-client';

export {
  CalendarMCPClient,
  type SLADeadline,
  type Milestone,
  type SprintPlan,
  type DeadlineAlert,
  type TeamCapacity,
} from './calendar-mcp-client';

// Import all clients for batch initialization
import DatabaseMCPClient from './database-mcp-client';
import LLMRouterMCPClient from './llm-router-mcp-client';
import GitAdvancedMCPClient from './git-advanced-mcp-client';
import FilesystemWatchMCPClient from './fs-watch-mcp-client';
import CalendarMCPClient from './calendar-mcp-client';

/**
 * MCP Client Factory
 *
 * Unified interface for creating and managing all MCP clients
 */
export class MCPClientFactory {
  private static instance: MCPClientFactory;
  private databaseClient: DatabaseMCPClient;
  private llmRouterClient: LLMRouterMCPClient;
  private gitClient: GitAdvancedMCPClient;
  private fsWatchClient: FilesystemWatchMCPClient;
  private calendarClient: CalendarMCPClient;

  private constructor() {
    this.databaseClient = new DatabaseMCPClient();
    this.llmRouterClient = new LLMRouterMCPClient();
    this.gitClient = new GitAdvancedMCPClient();
    this.fsWatchClient = new FilesystemWatchMCPClient();
    this.calendarClient = new CalendarMCPClient();
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): MCPClientFactory {
    if (!MCPClientFactory.instance) {
      MCPClientFactory.instance = new MCPClientFactory();
    }
    return MCPClientFactory.instance;
  }

  /**
   * Get database client
   */
  getDatabase(): DatabaseMCPClient {
    return this.databaseClient;
  }

  /**
   * Get LLM router client
   */
  getLLMRouter(): LLMRouterMCPClient {
    return this.llmRouterClient;
  }

  /**
   * Get git advanced client
   */
  getGit(): GitAdvancedMCPClient {
    return this.gitClient;
  }

  /**
   * Get filesystem watch client
   */
  getFilesystemWatch(): FilesystemWatchMCPClient {
    return this.fsWatchClient;
  }

  /**
   * Get calendar client
   */
  getCalendar(): CalendarMCPClient {
    return this.calendarClient;
  }

  /**
   * Health check all clients
   */
  async checkAllHealth(): Promise<Record<string, boolean>> {
    return {
      database: await this.databaseClient.healthCheck(),
      llmRouter: await this.llmRouterClient.healthCheck(),
      git: await this.gitClient.healthCheck(),
      filesystemWatch: await this.fsWatchClient.healthCheck(),
      calendar: await this.calendarClient.healthCheck(),
    };
  }
}

// Export factory singleton
export const mcpClientFactory = MCPClientFactory.getInstance();

export default mcpClientFactory;
