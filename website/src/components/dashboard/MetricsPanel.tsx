/**
 * @file MetricsPanel.tsx
 * @description Reusable metrics panel component for the EGOS dashboard
 * @module components/dashboard/MetricsPanel
 * @version 0.1.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/DESIGN_GUIDE.md (Design Guidelines)
 * - mdc:docs_egos/products/dashboard/dashboard_feature_matrix.md (Feature Matrix)
 * - mdc:apps/dashboard/app_dashboard_diagnostic_metrics.py (Source Implementation)
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Activity, 
  ArrowUpRight, 
  ArrowDownRight, 
  Cpu, 
  HardDrive, 
  Memory,
  Network,
  Clock,
  AlertTriangle
} from "lucide-react";

interface MetricProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  status?: 'healthy' | 'warning' | 'critical' | 'unknown';
  footer?: React.ReactNode;
}

/**
 * Individual metric card component
 */
export const Metric: React.FC<MetricProps> = ({
  title,
  value,
  description,
  icon,
  trend,
  trendValue,
  status = 'healthy',
  footer
}) => {
  const statusColors = {
    healthy: 'text-success',
    warning: 'text-warning',
    critical: 'text-destructive',
    unknown: 'text-muted-foreground'
  };
  
  const trendColors = {
    up: 'text-success',
    down: 'text-destructive',
    neutral: 'text-muted-foreground'
  };
  
  const trendIcons = {
    up: <ArrowUpRight className="h-4 w-4" />,
    down: <ArrowDownRight className="h-4 w-4" />,
    neutral: null
  };
  
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          {icon && <span className="text-muted-foreground">{icon}</span>}
        </div>
        {description && (
          <CardDescription>{description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline">
          <span className={`text-2xl font-bold ${statusColors[status]}`}>{value}</span>
          {trend && trendValue && (
            <span className={`ml-2 flex items-center text-xs ${trendColors[trend]}`}>
              {trendIcons[trend]}
              {trendValue}
            </span>
          )}
        </div>
      </CardContent>
      {footer && (
        <CardFooter className="pt-0 text-xs text-muted-foreground">
          {footer}
        </CardFooter>
      )}
    </Card>
  );
};

interface MetricsPanelProps {
  title?: string;
  description?: string;
  metrics: MetricProps[];
  columns?: 1 | 2 | 3 | 4;
  className?: string;
}

/**
 * Grid layout for multiple metrics
 */
export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  title,
  description,
  metrics,
  columns = 3,
  className = ''
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  };
  
  return (
    <div className={className}>
      {(title || description) && (
        <div className="mb-4">
          {title && <h3 className="text-lg font-medium">{title}</h3>}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}
      
      <div className={`grid ${gridCols[columns]} gap-4`}>
        {metrics.map((metric, index) => (
          <Metric key={index} {...metric} />
        ))}
      </div>
    </div>
  );
};

/**
 * Predefined system metrics panel
 */
export const SystemMetricsPanel: React.FC<{
  className?: string;
  loading?: boolean;
}> = ({ className = '', loading = false }) => {
  // In a real implementation, this would fetch data from an API
  const systemMetrics = [
    {
      title: 'CPU Usage',
      value: loading ? '...' : '42%',
      icon: <Cpu className="h-4 w-4" />,
      trend: 'up' as const,
      trendValue: '8%',
      status: 'healthy' as const,
      footer: <Progress value={42} className="h-1 mt-2" />
    },
    {
      title: 'Memory Usage',
      value: loading ? '...' : '2.4 GB',
      icon: <Memory className="h-4 w-4" />,
      trend: 'neutral' as const,
      trendValue: '0%',
      status: 'healthy' as const,
      footer: <Progress value={60} className="h-1 mt-2" />
    },
    {
      title: 'Disk Space',
      value: loading ? '...' : '78%',
      icon: <HardDrive className="h-4 w-4" />,
      trend: 'up' as const,
      trendValue: '2%',
      status: 'warning' as const,
      footer: <Progress value={78} className="h-1 mt-2" indicatorClassName="bg-warning" />
    },
    {
      title: 'Network',
      value: loading ? '...' : '1.2 MB/s',
      icon: <Network className="h-4 w-4" />,
      trend: 'down' as const,
      trendValue: '5%',
      status: 'healthy' as const
    },
    {
      title: 'Response Time',
      value: loading ? '...' : '120ms',
      icon: <Clock className="h-4 w-4" />,
      trend: 'up' as const,
      trendValue: '15ms',
      status: 'healthy' as const
    },
    {
      title: 'Active Alerts',
      value: loading ? '...' : '3',
      icon: <AlertTriangle className="h-4 w-4" />,
      status: 'warning' as const,
      footer: 'Click to view details'
    }
  ];
  
  return (
    <MetricsPanel
      title="System Metrics"
      description="Real-time system performance metrics"
      metrics={systemMetrics}
      columns={3}
      className={className}
    />
  );
};

export default MetricsPanel;
