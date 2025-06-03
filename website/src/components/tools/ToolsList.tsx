/**
 * ToolsList Component
 * 
 * A component that displays a filterable, searchable list of tools from the registry.
 * Supports filtering by category, tag, and status, as well as text search.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Tool, ToolFilters } from '../../types/tools';
import ToolCard from './ToolCard';
import ToolFiltersPanel from './ToolFiltersPanel';

interface ToolsListProps {
  /** Array of tools to display */
  tools: Tool[];
  /** Optional: Initial filter state */
  initialFilters?: ToolFilters;
  /** Optional: Custom class name */
  className?: string;
}

/**
 * Component to display a filterable list of tools
 */
const ToolsList: React.FC<ToolsListProps> = ({ 
  tools, 
  initialFilters = {}, 
  className = '' 
}) => {
  // State for filters
  const [filters, setFilters] = useState<ToolFilters>(initialFilters);
  
  // Apply filters to tools
  const filteredTools = useMemo(() => {
    return tools.filter(tool => {
      // Filter by category
      if (filters.category && tool.category.toLowerCase() !== filters.category.toLowerCase()) {
        return false;
      }
      
      // Filter by tag
      if (filters.tag && !tool.tags.some(tag => tag.toLowerCase() === filters.tag?.toLowerCase())) {
        return false;
      }
      
      // Filter by status
      if (filters.status && tool.status !== filters.status) {
        return false;
      }
      
      // Filter by search query
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const matchesSearch = 
          tool.name.toLowerCase().includes(searchLower) ||
          tool.description.toLowerCase().includes(searchLower) ||
          tool.tags.some(tag => tag.toLowerCase().includes(searchLower));
        
        if (!matchesSearch) {
          return false;
        }
      }
      
      return true;
    });
  }, [tools, filters]);
  
  // Get unique categories, tags, and statuses for filter options
  const categories = useMemo(() => {
    return Array.from(new Set(tools.map(tool => tool.category)));
  }, [tools]);
  
  const tags = useMemo(() => {
    const allTags = tools.flatMap(tool => tool.tags);
    return Array.from(new Set(allTags));
  }, [tools]);
  
  const statuses = useMemo(() => {
    return Array.from(new Set(tools.map(tool => tool.status)));
  }, [tools]);
  
  // Handle filter changes
  const handleFilterChange = (newFilters: Partial<ToolFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };
  
  return (
    <div className={`tools-list-container ${className}`}>
      <h1 className="text-2xl font-bold mb-6">EGOS Tools Registry</h1>
      
      <div className="tools-list-layout">
        <aside className="filters-sidebar">
          <ToolFiltersPanel
            categories={categories}
            tags={tags}
            statuses={statuses}
            currentFilters={filters}
            onFilterChange={handleFilterChange}
          />
        </aside>
        
        <main className="tools-grid">
          <div className="tools-count mb-4">
            Showing {filteredTools.length} of {tools.length} tools
          </div>
          
          {filteredTools.length === 0 ? (
            <div className="no-tools-message">
              No tools match the current filters. Try adjusting your filters.
            </div>
          ) : (
            <div className="tools-cards-grid">
              {filteredTools.map(tool => (
                <ToolCard key={tool.id} tool={tool} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ToolsList;