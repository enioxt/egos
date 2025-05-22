/**
 * EGOS Tool Registry Type Definitions
 * 
 * Type definitions for the EGOS Tool Registry data structure used by the website
 * components to display tool information, filtering, and search functionality.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

/**
 * Represents a usage example for a tool
 */
export interface ToolExample {
  /** Description of what this example demonstrates */
  description: string;
  /** The command to run the example */
  command: string;
  /** Expected output from running the command */
  output: string;
}

/**
 * Represents website integration settings for a tool
 */
export interface WebsiteIntegration {
  /** Path to the tool's page on the website */
  page: string;
  /** Category name for grouping on the website */
  category: string;
  /** Display priority (high, medium, low) */
  priority: 'high' | 'medium' | 'low';
}

/**
 * Represents documentation references for a tool
 */
export interface Documentation {
  /** Path to a detailed guide for this tool */
  guide?: string;
  /** API documentation URL if available */
  api?: string;
  /** Additional references */
  references?: string[];
}

/**
 * Represents a tool in the registry
 */
export interface Tool {
  /** Unique identifier for the tool (kebab-case) */
  id: string;
  /** Display name of the tool */
  name: string;
  /** Relative path to the tool script */
  path: string;
  /** Detailed description of the tool's purpose and functionality */
  description: string;
  /** Basic usage pattern */
  usage: string;
  /** List of descriptive tags */
  tags: string[];
  /** Primary category */
  category: string;
  /** Current status (active, deprecated, experimental, planning, archived) */
  status: 'active' | 'deprecated' | 'experimental' | 'planning' | 'archived';
  /** Creation date (YYYY-MM-DD) */
  created: string;
  /** Last update date (YYYY-MM-DD) */
  last_updated: string;
  /** Maintainer name or team */
  maintainer: string;
  /** External dependencies required by this tool */
  dependencies?: string[];
  /** Website integration settings */
  website_integration?: WebsiteIntegration;
  /** Usage examples */
  examples?: ToolExample[];
  /** Documentation references */
  documentation?: Documentation;
}

/**
 * Represents the complete tool registry
 */
export interface ToolRegistry {
  /** Array of all registered tools */
  tools: Tool[];
}

/**
 * Filter options for tool listing
 */
export interface ToolFilters {
  /** Filter by category */
  category?: string;
  /** Filter by tag */
  tag?: string;
  /** Filter by status */
  status?: string;
  /** Search query */
  search?: string;
}