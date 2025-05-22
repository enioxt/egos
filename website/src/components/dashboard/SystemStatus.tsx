/**
 * @file SystemStatus.tsx
 * @description System status component for monitoring EGOS subsystems
 * @module components/dashboard/SystemStatus
 * @version 0.1.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/DESIGN_GUIDE.md (Design Guidelines)
 * - mdc:docs_egos/products/dashboard/dashboard_feature_matrix.md (Feature Matrix)
 * - mdc:apps/dashboard/app_dashboard_diagnostic_mycelium.py (Source Implementation)
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  HelpCircle,
  Clock,
  Info
} from "lucide-react";

// Status types for subsystems
type SystemStatus = 'operational' | 'degraded' | 'outage' | 'maintenance' | 'unknown';

// Interface for subsystem data
interface SubsystemData {
  id: string;
  name: string;
  description: string;
  status: SystemStatus;
  lastUpdated: string;
  metrics?: {
    responseTime?: number;
    uptime?: number;
    errorRate?: number;
  };
  incidents?: {
    count: number;
    latest?: string;
  };
}

// Props for the SystemStatus component
interface SystemStatusProps {
  subsystems: SubsystemData[];
  lastUpdated?: string;
  className?: string;
}

/**
 * Status indicator component with appropriate icon and color
 */
const StatusIndicator: React.FC<{ status: SystemStatus }> = ({ status }) => {
  const statusConfig = {
    operational: {
      icon: <CheckCircle2 className="h-5 w-5" />,
      color: 'text-success',
      label: 'Operational'
    },
    degraded: {
      icon: <AlertCircle className="h-5 w-5" />,
      color: 'text-warning',
      label: 'Degraded'
    },
    outage: {
      icon: <XCircle className="h-5 w-5" />,
      color: 'text-destructive',
      label: 'Outage'
    },
    maintenance: {
      icon: <Clock className="h-5 w-5" />,
      color: 'text-info',
      label: 'Maintenance'
    },
    unknown: {
      icon: <HelpCircle className="h-5 w-5" />,
      color: 'text-muted-foreground',
      label: 'Unknown'
    }
  };

  const { icon, color, label } = statusConfig[status];

  return (
    <div className={`flex items-center ${color}`}>
      {icon}
      <span className="ml-2 text-sm font-medium">{label}</span>
    </div>
  );
};

/**
 * Subsystem status row component
 */
const SubsystemStatusRow: React.FC<{ subsystem: SubsystemData }> = ({ subsystem }) => {
  return (
    <div className="py-3 border-b last:border-0">
      <div className="flex justify-between items-center mb-1">
        <div className="flex items-center">
          <h4 className="text-sm font-medium">{subsystem.name}</h4>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button className="ml-1 text-muted-foreground">
                  <Info className="h-3.5 w-3.5" />
                </button>
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs">{subsystem.description}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <StatusIndicator status={subsystem.status} />
      </div>
      
      <div className="flex text-xs text-muted-foreground">
        <div className="mr-4">
          {subsystem.metrics?.responseTime !== undefined && (
            <span className="mr-2">Response: {subsystem.metrics.responseTime}ms</span>
          )}
          {subsystem.metrics?.uptime !== undefined && (
            <span className="mr-2">Uptime: {subsystem.metrics.uptime}%</span>
          )}
        </div>
        
        {subsystem.incidents?.count > 0 && (
          <Badge variant="outline" className="text-xs">
            {subsystem.incidents.count} {subsystem.incidents.count === 1 ? 'incident' : 'incidents'}
          </Badge>
        )}
      </div>
    </div>
  );
};

/**
 * Main SystemStatus component
 */
const SystemStatus: React.FC<SystemStatusProps> = ({ 
  subsystems, 
  lastUpdated = 'Unknown',
  className = ''
}) => {
  // Calculate overall system status
  const getOverallStatus = (): SystemStatus => {
    if (subsystems.some(s => s.status === 'outage')) return 'outage';
    if (subsystems.some(s => s.status === 'degraded')) return 'degraded';
    if (subsystems.every(s => s.status === 'operational')) return 'operational';
    if (subsystems.some(s => s.status === 'maintenance')) return 'maintenance';
    return 'unknown';
  };

  const overallStatus = getOverallStatus();

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle>System Status</CardTitle>
          <StatusIndicator status={overallStatus} />
        </div>
        <CardDescription>
          Status of EGOS subsystems • Last updated: {lastUpdated}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="divide-y">
          {subsystems.map(subsystem => (
            <SubsystemStatusRow key={subsystem.id} subsystem={subsystem} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Demo SystemStatus component with mock data
 */
export const DemoSystemStatus: React.FC<{ className?: string }> = ({ className = '' }) => {
  const mockSubsystems: SubsystemData[] = [
    {
      id: 'ethik',
      name: 'ETHIK',
      description: 'Ethical validation and governance subsystem',
      status: 'operational',
      lastUpdated: '2025-05-21T19:45:00Z',
      metrics: {
        responseTime: 45,
        uptime: 99.98,
        errorRate: 0.01
      }
    },
    {
      id: 'koios',
      name: 'KOIOS',
      description: 'Documentation standards and knowledge management',
      status: 'operational',
      lastUpdated: '2025-05-21T19:42:00Z',
      metrics: {
        responseTime: 62,
        uptime: 99.95,
        errorRate: 0.02
      }
    },
    {
      id: 'nexus',
      name: 'NEXUS',
      description: 'Code analysis and dependency management',
      status: 'degraded',
      lastUpdated: '2025-05-21T19:30:00Z',
      metrics: {
        responseTime: 120,
        uptime: 98.5,
        errorRate: 1.2
      },
      incidents: {
        count: 1,
        latest: 'High response time detected'
      }
    },
    {
      id: 'coruja',
      name: 'CORUJA',
      description: 'Communication and messaging subsystem',
      status: 'operational',
      lastUpdated: '2025-05-21T19:40:00Z',
      metrics: {
        responseTime: 38,
        uptime: 99.99,
        errorRate: 0.005
      }
    },
    {
      id: 'atlas',
      name: 'ATLAS',
      description: 'System cartography and visualization',
      status: 'operational',
      lastUpdated: '2025-05-21T19:38:00Z',
      metrics: {
        responseTime: 55,
        uptime: 99.9,
        errorRate: 0.08
      }
    },
    {
      id: 'cronos',
      name: 'CRONOS',
      description: 'Time management and scheduling',
      status: 'maintenance',
      lastUpdated: '2025-05-21T18:00:00Z',
      metrics: {
        responseTime: 80,
        uptime: 95.0,
        errorRate: 0.5
      },
      incidents: {
        count: 1,
        latest: 'Scheduled maintenance'
      }
    },
    {
      id: 'cross-reference',
      name: 'Cross-Reference System',
      description: 'Documentation cross-reference management',
      status: 'operational',
      lastUpdated: '2025-05-21T19:35:00Z',
      metrics: {
        responseTime: 48,
        uptime: 99.8,
        errorRate: 0.1
      }
    }
  ];

  return <SystemStatus subsystems={mockSubsystems} lastUpdated="2025-05-21 19:50:00" className={className} />;
};

export default SystemStatus;
