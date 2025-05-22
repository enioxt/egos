/**
 * @file CrossReferenceStats.tsx
 * @description Statistics component for the Cross-Reference Explorer
 * @module components/cross-reference/CrossReferenceStats
 * @version 1.0.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/cross_reference_validator.md (Validator Documentation)
 * - mdc:website/DESIGN_GUIDE.md (Design Guidelines)
 */

import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { 
  BookOpenIcon, 
  FileWarningIcon, 
  LinkIcon, 
  FileIcon,
  PieChartIcon
} from "lucide-react";
import { CrossReferenceData } from './CrossReferenceExplorer';

interface CrossReferenceStatsProps {
  data: CrossReferenceData;
}

const CrossReferenceStats: React.FC<CrossReferenceStatsProps> = ({ data }) => {
  const { stats } = data;
  
  // Calculate health percentage (higher is better)
  const healthPercentage = Math.max(
    0, 
    Math.min(
      100, 
      100 - (stats.brokenReferences + stats.orphanedFiles) * 100 / stats.totalFiles
    )
  );
  
  // Get color based on health percentage
  const getHealthColor = (health: number): string => {
    if (health >= 90) return 'text-success';
    if (health >= 70) return 'text-info';
    if (health >= 50) return 'text-warning';
    return 'text-destructive';
  };
  
  // Get color based on health percentage for backgrounds
  const getHealthBgColor = (health: number): string => {
    if (health >= 90) return 'bg-success';
    if (health >= 70) return 'bg-info';
    if (health >= 50) return 'bg-warning';
    return 'bg-destructive';
  };
  
  // Get status text based on health percentage
  const getHealthStatus = (health: number): string => {
    if (health >= 90) return 'Excelente';
    if (health >= 70) return 'Bom';
    if (health >= 50) return 'Requer Atenção';
    return 'Crítico';
  };

  return (
    <div className="space-y-4">
      {/* Health Card */}
      <Card>
        <CardContent className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Saúde do Sistema de Referências</h3>
          
          <div className="mb-3">
            <Progress value={healthPercentage} className="h-2" indicatorClassName={getHealthBgColor(healthPercentage)} />
          </div>
          
          <div className="flex justify-between items-center">
            <span className={`text-lg font-bold ${getHealthColor(healthPercentage)}`}>
              {healthPercentage.toFixed(1)}%
            </span>
            <span className="text-sm font-medium text-muted-foreground">
              {getHealthStatus(healthPercentage)}
            </span>
          </div>
        </CardContent>
      </Card>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-2">
        <Card>
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <FileIcon className="h-4 w-4 text-primary" />
              <span className="text-xs text-muted-foreground">Total de Arquivos</span>
            </div>
            <p className="text-lg font-bold mt-1">{stats.totalFiles}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <LinkIcon className="h-4 w-4 text-primary" />
              <span className="text-xs text-muted-foreground">Total de Referências</span>
            </div>
            <p className="text-lg font-bold mt-1">{stats.totalReferences}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <FileWarningIcon className="h-4 w-4 text-warning" />
              <span className="text-xs text-muted-foreground">Arquivos Órfãos</span>
            </div>
            <p className="text-lg font-bold mt-1">{stats.orphanedFiles}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <BookOpenIcon className="h-4 w-4 text-destructive" />
              <span className="text-xs text-muted-foreground">Referências Quebradas</span>
            </div>
            <p className="text-lg font-bold mt-1">{stats.brokenReferences}</p>
          </CardContent>
        </Card>
      </div>
      
      {/* Subsystem Breakdown */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <PieChartIcon className="h-4 w-4" />
            <h3 className="text-sm font-medium">Distribuição por Subsistema</h3>
          </div>
          
          <div className="space-y-2">
            {Object.entries(stats.subsystemBreakdown).map(([subsystem, count]) => {
              const percentage = (count / stats.totalFiles) * 100;
              return (
                <div key={subsystem} className="space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span>{subsystem}</span>
                    <span className="text-muted-foreground">{count} ({percentage.toFixed(1)}%)</span>
                  </div>
                  <Progress value={percentage} className="h-1.5" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CrossReferenceStats;
