/**
 * @file CrossReferenceControls.tsx
 * @description Filter controls for the Cross-Reference Explorer
 * @module components/cross-reference/CrossReferenceControls
 * @version 1.0.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/src/components/FilterControls.tsx (Base Filter Component)
 * - mdc:docs_egos/08_tooling_and_scripts/reference_implementations/file_reference_checker_ultra.md (Tool Documentation)
 */

import React from 'react';
import { Input } from "@/components/ui/input";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { 
  SearchIcon, 
  FilterIcon, 
  RotateCcwIcon,
  AlertTriangleIcon,
  FileIcon
} from "lucide-react";

interface CrossReferenceControlsProps {
  filterConfig: {
    showOrphaned: boolean;
    showWarnings: boolean;
    subsystems: string[];
    searchTerm: string;
    referenceThreshold: number;
  };
  onFilterChange: (config: Partial<CrossReferenceControlsProps['filterConfig']>) => void;
  subsystems: string[];
}

const CrossReferenceControls: React.FC<CrossReferenceControlsProps> = ({
  filterConfig,
  onFilterChange,
  subsystems
}) => {
  const handleSubsystemChange = (value: string) => {
    if (value === 'ALL') {
      onFilterChange({ subsystems: ['ALL'] });
    } else {
      onFilterChange({ 
        subsystems: value === 'MULTIPLE' 
          ? filterConfig.subsystems.filter(s => s !== 'ALL')
          : [value] 
      });
    }
  };

  const handleReset = () => {
    onFilterChange({
      showOrphaned: true,
      showWarnings: true,
      subsystems: ['ALL'],
      searchTerm: '',
      referenceThreshold: 0
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex-grow max-w-md relative">
          <SearchIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome de arquivo ou caminho..."
            value={filterConfig.searchTerm}
            onChange={(e) => onFilterChange({ searchTerm: e.target.value })}
            className="pl-9"
          />
        </div>
        
        <div className="w-48">
          <Select 
            value={filterConfig.subsystems.length === 1 ? filterConfig.subsystems[0] : 'MULTIPLE'}
            onValueChange={handleSubsystemChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="Subsistema" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Todos os Subsistemas</SelectItem>
              {subsystems.map(subsystem => (
                <SelectItem key={subsystem} value={subsystem}>{subsystem}</SelectItem>
              ))}
              {filterConfig.subsystems.length > 1 && (
                <SelectItem value="MULTIPLE">Múltiplos Selecionados</SelectItem>
              )}
            </SelectContent>
          </Select>
        </div>
        
        <Button
          variant="outline"
          size="icon"
          title="Redefinir Filtros"
          onClick={handleReset}
        >
          <RotateCcwIcon className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex flex-wrap gap-6 items-center">
        <div className="flex items-center gap-2">
          <Checkbox 
            id="show-orphaned"
            checked={filterConfig.showOrphaned}
            onCheckedChange={(checked) => 
              onFilterChange({ showOrphaned: checked as boolean })
            }
          />
          <Label htmlFor="show-orphaned" className="flex items-center text-sm cursor-pointer">
            <FileIcon className="h-3.5 w-3.5 mr-1 text-amber-500" />
            Mostrar Arquivos Órfãos
          </Label>
        </div>
        
        <div className="flex items-center gap-2">
          <Checkbox 
            id="show-warnings"
            checked={filterConfig.showWarnings}
            onCheckedChange={(checked) => 
              onFilterChange({ showWarnings: checked as boolean })
            }
          />
          <Label htmlFor="show-warnings" className="flex items-center text-sm cursor-pointer">
            <AlertTriangleIcon className="h-3.5 w-3.5 mr-1 text-warning" />
            Mostrar Warnings
          </Label>
        </div>
        
        <div className="flex items-center gap-3">
          <Label htmlFor="reference-threshold" className="text-sm whitespace-nowrap">
            Mín. Referências:
          </Label>
          <Slider
            id="reference-threshold"
            defaultValue={[0]}
            max={25}
            step={1}
            value={[filterConfig.referenceThreshold]}
            onValueChange={([value]) => 
              onFilterChange({ referenceThreshold: value })
            }
            className="w-32"
          />
          <span className="text-sm text-muted-foreground w-5 text-center">{filterConfig.referenceThreshold}</span>
        </div>
      </div>
    </div>
  );
};

export default CrossReferenceControls;
