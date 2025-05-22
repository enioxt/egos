/**
 * useToolRegistry Hook
 * 
 * Custom React hook that fetches and provides access to the EGOS Tool Registry data.
 * Handles loading states, caching, and error handling.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import { useState, useEffect } from 'react';
import { Tool, ToolRegistry } from '../types/tools';

interface UseToolRegistryResult {
  /** List of tools from the registry */
  tools: Tool[];
  /** Whether the data is currently being loaded */
  loading: boolean;
  /** Error message if the fetch failed */
  error: string | null;
  /** Manually refresh the data */
  refresh: () => void;
}

/**
 * Hook to fetch and manage tool registry data
 * 
 * @returns Object containing tools data, loading state, and error state
 */
const useToolRegistry = (): UseToolRegistryResult => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number>(0);

  /**
   * Fetch the tool registry data from the JSON file
   */
  const fetchToolRegistry = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch the registry data
      const response = await fetch('/api/data/tool_registry.json');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch tool registry: ${response.status} ${response.statusText}`);
      }
      
      const data: ToolRegistry = await response.json();
      
      // Validate the data structure
      if (!data || !Array.isArray(data.tools)) {
        throw new Error('Invalid tool registry data format');
      }
      
      // Sort tools by name
      const sortedTools = [...data.tools].sort((a, b) => 
        a.name.localeCompare(b.name)
      );
      
      setTools(sortedTools);
      setLastFetch(Date.now());
    } catch (err) {
      console.error('Error fetching tool registry:', err);
      setError(err instanceof Error ? err.message : 'Unknown error fetching tool registry');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Effect to fetch data on mount and when refresh is called
   */
  useEffect(() => {
    fetchToolRegistry();
  }, []);

  /**
   * Manual refresh function
   */
  const refresh = () => {
    // Only allow refreshing once every 5 seconds to prevent spam
    if (Date.now() - lastFetch > 5000) {
      fetchToolRegistry();
    }
  };

  return { tools, loading, error, refresh };
};

export default useToolRegistry;