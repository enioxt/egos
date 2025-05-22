/**
 * ToolFiltersPanel Component
 * 
 * A component that provides filtering controls for the tools list,
 * including category, tag, status filters, and search functionality.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import React from 'react';
import { ToolFilters } from '../../types/tools';

interface ToolFiltersPanelProps {
  /** Available categories for filtering */
  categories: string[];
  /** Available tags for filtering */
  tags: string[];
  /** Available statuses for filtering */
  statuses: string[];
  /** Current filter state */
  currentFilters: ToolFilters;
  /** Callback for filter changes */
  onFilterChange: (filters: Partial<ToolFilters>) => void;
  /** Optional: Custom class name */
  className?: string;
}

/**
 * Component to display and manage tool filtering controls
 */
const ToolFiltersPanel: React.FC<ToolFiltersPanelProps> = ({
  categories,
  tags,
  statuses,
  currentFilters,
  onFilterChange,
  className = ''
}) => {
  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ search: e.target.value });
  };
  
  // Handle category selection
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ category: e.target.value || undefined });
  };
  
  // Handle tag selection
  const handleTagChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ tag: e.target.value || undefined });
  };
  
  // Handle status selection
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ status: e.target.value || undefined });
  };
  
  // Reset all filters
  const handleResetFilters = () => {
    onFilterChange({
      category: undefined,
      tag: undefined,
      status: undefined,
      search: ''
    });
  };
  
  return (
    <div className={`tool-filters-panel ${className}`}>
      <h2 className="text-xl font-semibold mb-4">Filters</h2>
      
      {/* Search Box */}
      <div className="filter-group mb-4">
        <label htmlFor="tool-search" className="block text-sm font-medium mb-2">
          Search
        </label>
        <input
          id="tool-search"
          type="text"
          className="w-full p-2 border rounded"
          placeholder="Search tools..."
          value={currentFilters.search || ''}
          onChange={handleSearchChange}
        />
      </div>
      
      {/* Category Filter */}
      <div className="filter-group mb-4">
        <label htmlFor="category-filter" className="block text-sm font-medium mb-2">
          Category
        </label>
        <select
          id="category-filter"
          className="w-full p-2 border rounded"
          value={currentFilters.category || ''}
          onChange={handleCategoryChange}
        >
          <option value="">All Categories</option>
          {categories.sort().map(category => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>
      
      {/* Tag Filter */}
      <div className="filter-group mb-4">
        <label htmlFor="tag-filter" className="block text-sm font-medium mb-2">
          Tag
        </label>
        <select
          id="tag-filter"
          className="w-full p-2 border rounded"
          value={currentFilters.tag || ''}
          onChange={handleTagChange}
        >
          <option value="">All Tags</option>
          {tags.sort().map(tag => (
            <option key={tag} value={tag}>
              {tag}
            </option>
          ))}
        </select>
      </div>
      
      {/* Status Filter */}
      <div className="filter-group mb-4">
        <label htmlFor="status-filter" className="block text-sm font-medium mb-2">
          Status
        </label>
        <select
          id="status-filter"
          className="w-full p-2 border rounded"
          value={currentFilters.status || ''}
          onChange={handleStatusChange}
        >
          <option value="">All Statuses</option>
          {statuses.map(status => (
            <option key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>
      </div>
      
      {/* Reset Button */}
      <button
        className="w-full py-2 px-4 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
        onClick={handleResetFilters}
      >
        Reset Filters
      </button>
    </div>
  );
};

export default ToolFiltersPanel;