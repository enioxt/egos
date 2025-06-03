/**
 * ToolsPage Component
 * 
 * Main page component for the tools section of the EGOS website.
 * Loads and displays the tool registry data with filtering capabilities.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import React, { useState, useEffect } from 'react';
import { ToolRegistry } from '../../types/tools';
import ToolsList from './ToolsList';
import useToolRegistry from '../../hooks/useToolRegistry';

/**
 * Main page component for the tools section
 */
const ToolsPage: React.FC = () => {
  // Load tool registry data
  const { tools, loading, error } = useToolRegistry();
  
  // If loading, show loading indicator
  if (loading) {
    return (
      <div className="tools-page-loading flex justify-center items-center min-h-[500px]">
        <div className="loading-spinner animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }
  
  // If error, show error message
  if (error) {
    return (
      <div className="tools-page-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> Failed to load tool registry data. Please try again later.</span>
        <p className="mt-2 text-sm">{error}</p>
      </div>
    );
  }
  
  return (
    <div className="tools-page">
      <div className="tools-header mb-8">
        <h1 className="text-3xl font-bold mb-2">EGOS Tools</h1>
        <p className="text-lg text-gray-600">
          Discover and use the various tools available in the EGOS ecosystem
        </p>
      </div>
      
      <div className="tools-stats-summary flex gap-4 mb-8">
        <div className="stat-card bg-blue-50 border border-blue-200 rounded-lg p-4 flex-1">
          <div className="stat-value text-2xl font-bold text-blue-700">{tools.length}</div>
          <div className="stat-label text-sm text-blue-600">Total Tools</div>
        </div>
        
        <div className="stat-card bg-green-50 border border-green-200 rounded-lg p-4 flex-1">
          <div className="stat-value text-2xl font-bold text-green-700">
            {tools.filter(tool => tool.status === 'active').length}
          </div>
          <div className="stat-label text-sm text-green-600">Active Tools</div>
        </div>
        
        <div className="stat-card bg-purple-50 border border-purple-200 rounded-lg p-4 flex-1">
          <div className="stat-value text-2xl font-bold text-purple-700">
            {Array.from(new Set(tools.map(tool => tool.category))).length}
          </div>
          <div className="stat-label text-sm text-purple-600">Categories</div>
        </div>
      </div>
      
      <ToolsList tools={tools} />
    </div>
  );
};

export default ToolsPage;