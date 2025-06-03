/**
 * ToolDetailPage Component
 * 
 * Displays detailed information about a specific tool from the registry.
 * Shows all metadata, usage examples, dependencies, and related information.
 * 
 * Created: 2025-05-22
 * Author: EGOS Development Team
 */

import React, { useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Tool } from '../../types/tools';
import useToolRegistry from '../../hooks/useToolRegistry';

interface CodeBlockProps {
  code: string;
  language?: string;
}

/**
 * Component to display a formatted code block
 */
const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = 'bash' }) => {
  return (
    <div className="code-block bg-gray-900 rounded-md overflow-hidden">
      <div className="code-header bg-gray-800 px-4 py-2 text-gray-400 text-xs">
        {language}
      </div>
      <pre className="p-4 text-gray-300 overflow-x-auto">
        <code>{code}</code>
      </pre>
    </div>
  );
};

/**
 * Component to display detailed information about a specific tool
 */
const ToolDetailPage: React.FC = () => {
  // Get the tool ID from the URL
  const { toolId } = useParams<{ toolId: string }>();
  
  // Load the tool registry data
  const { tools, loading, error } = useToolRegistry();
  
  // Find the specific tool
  const tool = useMemo(() => {
    return tools.find(t => t.id === toolId);
  }, [tools, toolId]);
  
  // If loading, show loading indicator
  if (loading) {
    return (
      <div className="tool-detail-loading flex justify-center items-center min-h-[500px]">
        <div className="loading-spinner animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }
  
  // If error, show error message
  if (error) {
    return (
      <div className="tool-detail-error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> Failed to load tool registry data. Please try again later.</span>
        <p className="mt-2 text-sm">{error}</p>
      </div>
    );
  }
  
  // If tool not found, show error message
  if (!tool) {
    return (
      <div className="tool-not-found bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Tool Not Found!</strong>
        <span className="block sm:inline"> The tool "{toolId}" does not exist in the registry.</span>
        <div className="mt-4">
          <Link to="/tools" className="text-blue-600 hover:text-blue-800">
            ← Back to Tools List
          </Link>
        </div>
      </div>
    );
  }
  
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
    <div className="tool-detail-page">
      {/* Back link */}
      <Link to="/tools" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
        ← Back to Tools List
      </Link>
      
      {/* Tool header */}
      <div className="tool-header flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-1">{tool.name}</h1>
          <div className="tool-id text-sm text-gray-500 mb-2">ID: {tool.id}</div>
        </div>
        <div className={`status-indicator ${getStatusColor(tool.status)} rounded-full px-3 py-1 text-sm text-white`}>
          {tool.status.charAt(0).toUpperCase() + tool.status.slice(1)}
        </div>
      </div>
      
      {/* Tool metadata grid */}
      <div className="tool-meta-grid grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Left column */}
        <div className="col-span-2">
          {/* Description */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Description</h2>
            <p className="text-gray-700">{tool.description}</p>
          </div>
          
          {/* Usage */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Usage</h2>
            <CodeBlock code={tool.usage} />
          </div>
          
          {/* Examples */}
          {tool.examples && tool.examples.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Examples</h2>
              <div className="examples-list space-y-4">
                {tool.examples.map((example, index) => (
                  <div key={index} className="example-item bg-gray-50 p-4 rounded-lg border">
                    <h3 className="text-md font-medium mb-2">{example.description}</h3>
                    <CodeBlock code={example.command} />
                    {example.output && (
                      <div className="mt-2">
                        <div className="text-sm text-gray-500 mb-1">Output:</div>
                        <div className="bg-gray-100 p-3 rounded text-sm font-mono">
                          {example.output}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Right column */}
        <div>
          {/* Details card */}
          <div className="tool-details-card bg-gray-50 p-4 rounded-lg border mb-6">
            <h2 className="text-xl font-semibold mb-3">Details</h2>
            
            <div className="detail-item mb-3">
              <div className="text-sm text-gray-500">Category</div>
              <div>{tool.category}</div>
            </div>
            
            <div className="detail-item mb-3">
              <div className="text-sm text-gray-500">Path</div>
              <div className="font-mono text-sm">{tool.path}</div>
            </div>
            
            <div className="detail-item mb-3">
              <div className="text-sm text-gray-500">Created</div>
              <div>{tool.created}</div>
            </div>
            
            <div className="detail-item mb-3">
              <div className="text-sm text-gray-500">Last Updated</div>
              <div>{tool.last_updated}</div>
            </div>
            
            <div className="detail-item">
              <div className="text-sm text-gray-500">Maintainer</div>
              <div>{tool.maintainer}</div>
            </div>
          </div>
          
          {/* Tags */}
          <div className="tool-tags mb-6">
            <h2 className="text-xl font-semibold mb-2">Tags</h2>
            <div className="flex flex-wrap gap-2">
              {tool.tags.map(tag => (
                <Link
                  key={tag}
                  to={`/tools?tag=${tag}`}
                  className="tag bg-blue-100 text-blue-800 rounded-full px-3 py-1 text-sm hover:bg-blue-200"
                >
                  {tag}
                </Link>
              ))}
            </div>
          </div>
          
          {/* Dependencies */}
          {tool.dependencies && tool.dependencies.length > 0 && (
            <div className="tool-dependencies mb-6">
              <h2 className="text-xl font-semibold mb-2">Dependencies</h2>
              <ul className="list-disc list-inside">
                {tool.dependencies.map((dep, index) => (
                  <li key={index} className="mb-1">
                    {dep}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Documentation */}
          {tool.documentation && (
            <div className="tool-documentation">
              <h2 className="text-xl font-semibold mb-2">Documentation</h2>
              <ul className="space-y-2">
                {tool.documentation.guide && (
                  <li>
                    <a href={tool.documentation.guide} className="text-blue-600 hover:text-blue-800">
                      Detailed Guide
                    </a>
                  </li>
                )}
                {tool.documentation.api && (
                  <li>
                    <a href={tool.documentation.api} className="text-blue-600 hover:text-blue-800">
                      API Documentation
                    </a>
                  </li>
                )}
                {tool.documentation.references && tool.documentation.references.length > 0 && (
                  <li>
                    <div className="text-gray-700 mb-1">References:</div>
                    <ul className="list-disc list-inside pl-2">
                      {tool.documentation.references.map((ref, index) => (
                        <li key={index} className="text-sm">
                          {ref}
                        </li>
                      ))}
                    </ul>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ToolDetailPage;