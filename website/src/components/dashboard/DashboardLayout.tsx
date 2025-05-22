/**
 * @file DashboardLayout.tsx
 * @description Primary layout component for the unified EGOS dashboard
 * @module components/dashboard/DashboardLayout
 * @version 0.1.0
 * @date 2025-05-21
 *
 * @references
 * - mdc:website/DESIGN_GUIDE.md (Design Guidelines)
 * - mdc:website/src/app/dashboard/page.tsx (Current Dashboard Page)
 * - mdc:docs_egos/products/dashboard/dashboard_feature_matrix.md (Feature Matrix)
 */

import React, { ReactNode } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  LayoutDashboard, 
  BarChart3, 
  AlertTriangle, 
  Settings, 
  FileText, 
  Activity,
  MessageSquare,
  Network
} from "lucide-react";

interface DashboardLayoutProps {
  children: ReactNode;
  activeTab?: string;
  showSidebar?: boolean;
}

/**
 * Primary layout component for the EGOS Dashboard
 * Provides consistent structure with sidebar navigation and content area
 */
const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  children, 
  activeTab = "overview",
  showSidebar = true
}) => {
  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] min-h-[600px] bg-background">
      <div className="flex-1 flex overflow-hidden">
        {showSidebar && (
          <div className="w-64 border-r bg-card/50 overflow-y-auto p-4">
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-2">EGOS Dashboard</h2>
              <p className="text-sm text-muted-foreground">
                System monitoring and management
              </p>
            </div>
            
            <nav className="space-y-1">
              <SidebarItem 
                icon={<LayoutDashboard className="h-4 w-4" />} 
                label="Overview" 
                href="/dashboard"
                active={activeTab === "overview"}
              />
              <SidebarItem 
                icon={<Activity className="h-4 w-4" />} 
                label="System Health" 
                href="/dashboard/health"
                active={activeTab === "health"}
              />
              <SidebarItem 
                icon={<BarChart3 className="h-4 w-4" />} 
                label="Analytics" 
                href="/dashboard/analytics"
                active={activeTab === "analytics"}
              />
              <SidebarItem 
                icon={<AlertTriangle className="h-4 w-4" />} 
                label="Diagnostics" 
                href="/dashboard/diagnostics"
                active={activeTab === "diagnostics"}
              />
              <SidebarItem 
                icon={<Network className="h-4 w-4" />} 
                label="Cross-References" 
                href="/cross-reference-explorer"
                active={activeTab === "cross-references"}
              />
              <SidebarItem 
                icon={<MessageSquare className="h-4 w-4" />} 
                label="Feedback" 
                href="/dashboard/feedback"
                active={activeTab === "feedback"}
              />
              <SidebarItem 
                icon={<FileText className="h-4 w-4" />} 
                label="Reports" 
                href="/dashboard/reports"
                active={activeTab === "reports"}
              />
              <SidebarItem 
                icon={<Settings className="h-4 w-4" />} 
                label="Settings" 
                href="/dashboard/settings"
                active={activeTab === "settings"}
              />
            </nav>
          </div>
        )}
        
        <div className="flex-1 overflow-auto">
          <main className="p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
};

interface SidebarItemProps {
  icon: ReactNode;
  label: string;
  href: string;
  active?: boolean;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ 
  icon, 
  label, 
  href, 
  active = false 
}) => {
  return (
    <a
      href={href}
      className={`flex items-center px-3 py-2 text-sm rounded-md transition-colors ${
        active 
          ? 'bg-primary text-primary-foreground' 
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      }`}
    >
      <span className="mr-3">{icon}</span>
      {label}
    </a>
  );
};

export default DashboardLayout;
