/**
 * ToolCard Component
 * 
 * Displays a summary card for a single tool from the registry.
 * Shows the tool's name, description, category, status, and tags.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Tool } from '../../types/tools';

interface ToolCardProps {
  /** Tool to display */
  tool: Tool;
  /** Optional: Custom class name */
  className?: string;
}

/**
 * Component to display a card for a single tool
 */
const ToolCard: React.FC<ToolCardProps> = ({ tool, className = '' }) => {
  // Status indicator colors
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'deprecated':
        return 'bg-yellow-500';
      case 'experimental':
        return 'bg-purple-500';
      case 'planning':
        return 'bg-blue-500';
      case 'archived':
        return 'bg-gray-500';
      default:
        return 'bg-gray-400';
    }
  };
  
  return (
    <div className={`tool-card rounded-lg border p-4 hover:shadow-md transition-shadow ${className}`}>
      <div className="tool-header flex justify-between items-start mb-2">
        <h3 className="text-lg font-bold">{tool.name}</h3>
        <div className={`status-indicator ${getStatusColor(tool.status)} rounded-full px-2 py-1 text-xs text-white`}>
          {tool.status.charAt(0).toUpperCase() + tool.status.slice(1)}
        </div>
      </div>
      
      <div className="tool-category text-sm text-gray-600 mb-2">
        Category: <span className="font-medium">{tool.category}</span>
      </div>
      
      <p className="tool-description text-sm mb-4 line-clamp-3">
        {tool.description}
      </p>
      
      <div className="tool-tags flex flex-wrap gap-1 mb-3">
        {tool.tags.map(tag => (
          <span
            key={tag}
            className="tag bg-gray-100 rounded-full px-2 py-1 text-xs"
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div className="tool-meta flex justify-between text-xs text-gray-500">
        <div>Updated: {tool.last_updated}</div>
        <div>Maintainer: {tool.maintainer}</div>
      </div>
      
      <div className="tool-actions mt-3 pt-3 border-t">
        <Link
          to={`/tools/${tool.id}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View Details →
        </Link>
      </div>
    </div>
  );
};

export default ToolCard;