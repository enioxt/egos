/**
 * @file CrossReferenceExplorer.tsx
 * @description Main component for the Cross-Reference Explorer that integrates visualization, filtering, and analysis features
 * @module components/cross-reference/CrossReferenceExplorer
 * @version 1.0.0
 * @date 2025-05-21
 * @license MIT
 *
 * @references
 * - mdc:website/ROADMAP.md#cross-reference-standardization (Initiative: Cross-Reference Standardization)
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/file_reference_checker_ultra.md (Tool Documentation)
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/cross_reference_validator.md (Validator Documentation)
 * - mdc:website/src/components/SystemGraph.tsx (Graph Visualization Component Base)
 */

import React, { useState, useEffect } from 'react';
import CrossReferenceGraph from './CrossReferenceGraph';
import CrossReferenceControls from './CrossReferenceControls';
import CrossReferenceStats from './CrossReferenceStats';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon, AlertTriangleIcon, FileTextIcon } from "lucide-react";

// Types for the cross-reference data
export interface CrossReferenceNode {
  id: string;
  label: string;
  type: 'file' | 'directory' | 'subsystem';
  subsystem?: string;
  size: number;
  orphaned: boolean;
  referenced: number;
  hasWarnings: boolean;
  path: string;
}

export interface CrossReferenceEdge {
  id: string;
  source: string;
  target: string;
  valid: boolean;
  type: 'direct' | 'indirect';
}

export interface CrossReferenceData {
  nodes: CrossReferenceNode[];
  edges: CrossReferenceEdge[];
  stats: {
    totalFiles: number;
    orphanedFiles: number;
    brokenReferences: number;
    totalReferences: number;
    subsystemBreakdown: Record<string, number>;
  };
}

// Mock data function - in production this would come from an API
const getMockData = (): CrossReferenceData => {
  // This function would be replaced with actual API calls in production
  return {
    nodes: [
      {
        id: 'file1',
        label: 'ROADMAP.md',
        type: 'file',
        subsystem: 'KOIOS',
        size: 15,
        orphaned: false,
        referenced: 24,
        hasWarnings: false,
        path: '/ROADMAP.md'
      },
      {
        id: 'file2',
        label: 'file_reference_checker_ultra.md',
        type: 'file',
        subsystem: 'NEXUS',
        size: 8,
        orphaned: false,
        referenced: 10,
        hasWarnings: false,
        path: '/docs_egos/08_tooling_and_scripts/reference_implementations/file_reference_checker_ultra.md'
      },
      {
        id: 'file3',
        label: 'cross_reference_validator.md',
        type: 'file',
        subsystem: 'NEXUS',
        size: 6,
        orphaned: false,
        referenced: 8,
        hasWarnings: false,
        path: '/docs_egos/08_tooling_and_scripts/reference_implementations/cross_reference_validator.md'
      },
      {
        id: 'file4',
        label: 'archive_validator.md',
        type: 'file',
        subsystem: 'NEXUS',
        size: 5,
        orphaned: false,
        referenced: 6,
        hasWarnings: false,
        path: '/docs_egos/08_tooling_and_scripts/reference_implementations/archive_validator.md'
      },
      {
        id: 'file5',
        label: 'orphaned_file.md',
        type: 'file',
        subsystem: 'OTHER',
        size: 3,
        orphaned: true,
        referenced: 0,
        hasWarnings: true,
        path: '/docs/orphaned_file.md'
      },
      {
        id: 'dir1',
        label: 'docs_egos',
        type: 'directory',
        size: 10,
        orphaned: false,
        referenced: 30,
        hasWarnings: false,
        path: '/docs_egos'
      },
    ],
    edges: [
      {
        id: 'edge1',
        source: 'file1',
        target: 'file2',
        valid: true,
        type: 'direct'
      },
      {
        id: 'edge2',
        source: 'file1',
        target: 'file3',
        valid: true,
        type: 'direct'
      },
      {
        id: 'edge3',
        source: 'file2',
        target: 'file3',
        valid: true,
        type: 'direct'
      },
      {
        id: 'edge4',
        source: 'file3',
        target: 'file4',
        valid: true,
        type: 'direct'
      },
      {
        id: 'edge5',
        source: 'file2',
        target: 'file5',
        valid: false,
        type: 'direct'
      }
    ],
    stats: {
      totalFiles: 150,
      orphanedFiles: 12,
      brokenReferences: 8,
      totalReferences: 387,
      subsystemBreakdown: {
        'KOIOS': 42,
        'ETHIK': 28,
        'NEXUS': 35,
        'CORUJA': 22,
        'ATLAS': 18,
        'OTHER': 5
      }
    }
  };
};

const CrossReferenceExplorer: React.FC = () => {
  const [data, setData] = useState<CrossReferenceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filterConfig, setFilterConfig] = useState({
    showOrphaned: true,
    showWarnings: true,
    subsystems: ['ALL'],
    searchTerm: '',
    referenceThreshold: 0
  });

  useEffect(() => {
    // Simulate API fetch with timeout
    const fetchData = async () => {
      try {
        setLoading(true);
        // In a real implementation, this would be an API call
        setTimeout(() => {
          const data = getMockData();
          setData(data);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load cross-reference data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleFilterChange = (newConfig: any) => {
    setFilterConfig({ ...filterConfig, ...newConfig });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">Carregando dados de referências cruzadas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-4">
        <AlertTriangleIcon className="h-4 w-4" />
        <AlertTitle>Erro</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <CrossReferenceControls 
          filterConfig={filterConfig} 
          onFilterChange={handleFilterChange}
          subsystems={Object.keys(data.stats.subsystemBreakdown)}
        />
      </div>
      
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 relative">
          <CrossReferenceGraph data={data} filterConfig={filterConfig} />
        </div>
        
        <div className="w-80 border-l overflow-y-auto p-4 bg-muted/30">
          <Tabs defaultValue="stats">
            <TabsList className="w-full mb-4">
              <TabsTrigger value="stats" className="flex-1">Estatísticas</TabsTrigger>
              <TabsTrigger value="warnings" className="flex-1">Avisos</TabsTrigger>
              <TabsTrigger value="info" className="flex-1">Informações</TabsTrigger>
            </TabsList>
            
            <TabsContent value="stats">
              <CrossReferenceStats data={data} />
            </TabsContent>
            
            <TabsContent value="warnings">
              <Card>
                <CardContent className="p-4">
                  <h3 className="text-lg font-medium mb-2 flex items-center">
                    <AlertTriangleIcon className="h-4 w-4 mr-2 text-warning" />
                    Problemas Detectados
                  </h3>
                  <ul className="space-y-2">
                    <li className="text-sm text-muted-foreground border-l-2 border-warning pl-2">
                      12 arquivos órfãos sem referências de entrada
                    </li>
                    <li className="text-sm text-muted-foreground border-l-2 border-warning pl-2">
                      8 referências quebradas detectadas
                    </li>
                    <li className="text-sm text-muted-foreground border-l-2 border-warning pl-2">
                      3 arquivos de implementação de referência em risco
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="info">
              <Card>
                <CardContent className="p-4">
                  <h3 className="text-lg font-medium mb-2 flex items-center">
                    <InfoIcon className="h-4 w-4 mr-2 text-info" />
                    Sobre o Explorador
                  </h3>
                  <p className="text-sm text-muted-foreground mb-2">
                    O Cross-Reference Explorer visualiza todas as relações entre arquivos de documentação e código no ecossistema EGOS.
                  </p>
                  <p className="text-sm text-muted-foreground mb-2">
                    <strong>Nós:</strong> Representam arquivos e diretórios.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    <strong>Arestas:</strong> Representam referências entre arquivos.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default CrossReferenceExplorer;
