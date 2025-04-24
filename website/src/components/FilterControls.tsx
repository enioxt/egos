/**
 * @file FilterControls.tsx
 * @description Filter controls component for the EGOS cross-reference network visualization.
 * @module components/FilterControls
 * @version 1.0.0
 * @date 2025-04-23
 * @license MIT
 *
 * @references
 * - mdc:website/ROADMAP.md#vis-005 (Task: Add filtering capabilities)
 * - mdc:website/src/components/SystemGraph.tsx (Visualization Component)
 * - mdc:website/src/app/system-explorer/visualization/page.tsx (Usage Context)
 * - mdc:docs/process/cross_reference_best_practices.md (Cross-Reference Standards)
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

/**
 * Filter options interface defining all possible filter criteria
 */
export interface FilterOptions {
  /** Array of file types to include (empty means all) */
  fileTypes: string[];
  /** Array of subsystems to include (empty means all) */
  subsystems: string[];
  /** Minimum number of connections a node must have */
  minConnections: number;
  /** Filter by core status (true = only core, false = non-core, null = all) */
  showCore: boolean | null;
}

interface FilterControlsProps {
  /** Callback function triggered when filters change */
  onFilterChange: (filters: FilterOptions) => void;
  /** Available file types for filtering */
  fileTypes: string[];
  /** Available subsystems for filtering */
  subsystems: string[];
}

/**
 * FilterControls component that provides UI for filtering the cross-reference visualization
 */
const FilterControls: React.FC<FilterControlsProps> = ({ 
  onFilterChange, 
  fileTypes = [], 
  subsystems = [] 
}) => {
  // Filter state
  const [selectedFileTypes, setSelectedFileTypes] = useState<string[]>([]);
  const [selectedSubsystems, setSelectedSubsystems] = useState<string[]>([]);
  const [minConnections, setMinConnections] = useState<number>(0);
  const [showCore, setShowCore] = useState<boolean | null>(null);
  
  // Apply filters when they change
  useEffect(() => {
    onFilterChange({
      fileTypes: selectedFileTypes,
      subsystems: selectedSubsystems,
      minConnections,
      showCore
    });
  }, [selectedFileTypes, selectedSubsystems, minConnections, showCore, onFilterChange]);

  // Toggle file type selection
  const toggleFileType = (fileType: string) => {
    setSelectedFileTypes(prev => 
      prev.includes(fileType)
        ? prev.filter(t => t !== fileType)
        : [...prev, fileType]
    );
  };

  // Toggle subsystem selection
  const toggleSubsystem = (subsystem: string) => {
    setSelectedSubsystems(prev => 
      prev.includes(subsystem)
        ? prev.filter(s => s !== subsystem)
        : [...prev, subsystem]
    );
  };

  // Reset all filters
  const resetFilters = () => {
    setSelectedFileTypes([]);
    setSelectedSubsystems([]);
    setMinConnections(0);
    setShowCore(null);
  };

  return (
    <div className="filter-controls bg-gray-800 p-4 rounded-lg mb-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Filter Visualization</h3>
        <button 
          onClick={resetFilters}
          className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded-md transition-colors"
        >
          Reset Filters
        </button>
      </div>

      <Accordion type="multiple" defaultValue={["file-types", "connections"]}>
        {/* File Type Filter */}
        <AccordionItem value="file-types">
          <AccordionTrigger className="text-white">
            File Types
            {selectedFileTypes.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {selectedFileTypes.length}
              </Badge>
            )}
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
              {fileTypes.map(fileType => (
                <div key={fileType} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`file-type-${fileType}`}
                    checked={selectedFileTypes.includes(fileType)}
                    onCheckedChange={() => toggleFileType(fileType)}
                  />
                  <label 
                    htmlFor={`file-type-${fileType}`}
                    className="text-sm text-gray-300 cursor-pointer"
                  >
                    {fileType}
                  </label>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Subsystem Filter */}
        <AccordionItem value="subsystems">
          <AccordionTrigger className="text-white">
            Subsystems
            {selectedSubsystems.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {selectedSubsystems.length}
              </Badge>
            )}
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
              {subsystems.map(subsystem => (
                <div key={subsystem} className="flex items-center space-x-2">
                  <Checkbox 
                    id={`subsystem-${subsystem}`}
                    checked={selectedSubsystems.includes(subsystem)}
                    onCheckedChange={() => toggleSubsystem(subsystem)}
                  />
                  <label 
                    htmlFor={`subsystem-${subsystem}`}
                    className="text-sm text-gray-300 cursor-pointer"
                  >
                    {subsystem}
                  </label>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Connection Threshold */}
        <AccordionItem value="connections">
          <AccordionTrigger className="text-white">
            Minimum Connections
            {minConnections > 0 && (
              <Badge variant="secondary" className="ml-2">
                {minConnections}
              </Badge>
            )}
          </AccordionTrigger>
          <AccordionContent>
            <div className="px-2 py-4">
              <Slider
                defaultValue={[0]}
                max={20}
                step={1}
                value={[minConnections]}
                onValueChange={(values: number[]) => setMinConnections(values[0])}
              />
              <div className="flex justify-between mt-2 text-xs text-gray-400">
                <span>0</span>
                <span>5</span>
                <span>10</span>
                <span>15</span>
                <span>20+</span>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Core Files Filter */}
        <AccordionItem value="core-files">
          <AccordionTrigger className="text-white">
            Core Files
            {showCore !== null && (
              <Badge variant="secondary" className="ml-2">
                {showCore ? "Only Core" : "Non-Core"}
              </Badge>
            )}
          </AccordionTrigger>
          <AccordionContent>
            <Select 
              value={showCore === null ? "all" : showCore ? "core" : "non-core"}
              onValueChange={(value: string) => {
                if (value === "all") setShowCore(null);
                else if (value === "core") setShowCore(true);
                else setShowCore(false);
              }}
            >
              <SelectTrigger className="w-full bg-gray-700 text-white border-gray-600">
                <SelectValue placeholder="Show all files" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Files</SelectItem>
                <SelectItem value="core">Core Files Only</SelectItem>
                <SelectItem value="non-core">Non-Core Files Only</SelectItem>
              </SelectContent>
            </Select>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <div className="mt-4 pt-3 border-t border-gray-700 text-xs text-gray-400">
        <p>
          Active filters will dynamically update the visualization to help you focus on specific aspects of the EGOS ecosystem.
        </p>
      </div>
    </div>
  );
};

export default FilterControls;
