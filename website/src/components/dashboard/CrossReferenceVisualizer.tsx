"use client";

/**
 * @file CrossReferenceVisualizer.tsx
 * @description Component to visualize cross-reference validation data
 * @module components/dashboard/CrossReferenceVisualizer
 * @version 0.1.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/src/lib/api/dashboardClient.ts (API Client)
 * - mdc:docs_egos/products/dashboard/dashboard_feature_matrix.md (Feature Matrix)
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  Link,
  Loader2,
  Network,
  GitFork,
  PackageSearch, // For orphaned files
} from 'lucide-react';
import {
  getUnifiedValidationReport,
  UnifiedValidationReport,
  OrphanedFile,
} from '@/lib/api'; // Use the barrel file for cleaner imports
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface CrossReferenceVisualizerProps {
  className?: string;
}

const CrossReferenceVisualizer: React.FC<CrossReferenceVisualizerProps> = ({
  className = '',
}) => {
  const [report, setReport] = useState<UnifiedValidationReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getUnifiedValidationReport();
        setReport(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch validation report');
        console.error('Error fetching validation report:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  if (loading) {
    return (
      <Card className={`p-6 flex flex-col items-center justify-center h-full ${className}`}>
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Loading cross-reference report...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`p-6 flex flex-col items-center justify-center h-full bg-destructive/10 ${className}`}>
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <p className="text-destructive font-semibold">Error loading report</p>
        <p className="text-sm text-destructive/80">{error}</p>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card className={`p-6 flex flex-col items-center justify-center h-full ${className}`}>
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">No cross-reference report data available.</p>
      </Card>
    );
  }

  const { orphaned_files, references, execution_time, timestamp } = report;

  const getPriorityBadgeVariant = (priority: OrphanedFile['priority']) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary'; // Using 'secondary' as yellow/orange might not be standard
      case 'low': return 'outline';
      default: return 'default';
    }
  };

  return (
    <div className={`grid gap-6 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Network className="mr-2 h-6 w-6 text-primary" />
            Cross-Reference Validation Overview
          </CardTitle>
          <CardDescription>
            Summary of the latest validation run, executed on {new Date(timestamp).toLocaleString()}.
            Total execution time: {execution_time.toFixed(2)}s.
          </CardDescription>
        </CardHeader>
      </Card>

      {orphaned_files && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PackageSearch className="mr-2 h-5 w-5" />
              Orphaned Files Report
            </CardTitle>
            <CardDescription>
              Detected {orphaned_files.total_orphaned_files} orphaned files out of {orphaned_files.total_files_scanned} scanned.
              ({orphaned_files.high_priority_count} high, {orphaned_files.medium_priority_count} medium, {orphaned_files.low_priority_count} low priority).
            </CardDescription>
          </CardHeader>
          <CardContent>
            {orphaned_files.orphaned_files.length > 0 ? (
              <ScrollArea className="h-[300px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>File Path</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Size</TableHead>
                      <TableHead>Priority</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {orphaned_files.orphaned_files.map((file) => (
                      <TableRow key={file.file_path}>
                        <TableCell className="font-medium">{file.file_path}</TableCell>
                        <TableCell>{file.file_type}</TableCell>
                        <TableCell>{(file.size / 1024).toFixed(2)} KB</TableCell>
                        <TableCell>
                          <Badge variant={getPriorityBadgeVariant(file.priority)}>
                            {file.priority}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            ) : (
              <p className="text-sm text-muted-foreground">No orphaned files found. Well done!</p>
            )}
          </CardContent>
        </Card>
      )}

      {references && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Link className="mr-2 h-5 w-5" />
              Reference Check Report
            </CardTitle>
            <CardDescription>
              Checked {references.total_files_checked} files and found {references.total_references_found} references.
              Detected {references.issues_found} issues.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Detailed reference issues could be listed here if available in the report */}
            {references.issues_found > 0 ? (
              <p className="text-sm text-orange-500 flex items-center">
                <AlertTriangle className="mr-2 h-4 w-4" />
                {references.issues_found} reference issues require attention.
              </p>
            ) : (
              <p className="text-sm text-green-600 flex items-center">
                <CheckCircle2 className="mr-2 h-4 w-4" />
                No reference issues found.
              </p>
            )}
            {/* Placeholder for more detailed reference data visualization */}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CrossReferenceVisualizer;
