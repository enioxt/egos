'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { ArrowDownNarrowWide, Clock, CheckCircle, AlertCircle, PauseCircle, X, ExternalLink, Github, PlusCircle, ArrowRight, PanelRight, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Task, roadmapTasks } from '../data/roadmapData';

// Helper function to get status icon
const getStatusIcon = (status: Task['status']) => {
  switch(status) {
    case 'Completed':
    case 'DONE':
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'In Progress':
      return <Clock className="h-5 w-5 text-blue-500" />;
    case 'Blocked':
      return <PauseCircle className="h-5 w-5 text-red-500" />;
    case 'Planned':
      return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    default:
      return null;
  }
};

// Helper function to get priority badge
const getPriorityBadge = (priority: Task['priority']) => {
  switch(priority) {
    case 'CRITICAL':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Critical</span>;
    case 'HIGH':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">High</span>;
    case 'MEDIUM':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Medium</span>;
    case 'LOW':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Low</span>;
    default:
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">Unknown</span>;
  }
};

// Helper function to group and sort tasks
const groupAndSortTasks = (tasks: Task[]) => {
  const inProgress = tasks.filter(t => t.status === 'In Progress').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  const planned = tasks.filter(t => t.status === 'Planned').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  const completed = tasks.filter(t => t.status === 'Completed' || t.status === 'DONE').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  return { inProgress, planned, completed };
};

const priorityOrder = (priority: Task['priority']) => {
  switch(priority) {
    case 'CRITICAL': return 1;
    case 'HIGH': return 2;
    case 'MEDIUM': return 3;
    case 'LOW': return 4;
    default: return 5;
  }
};

export const Roadmap = () => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showContribution, setShowContribution] = useState(false);
  const [visibleCount, setVisibleCount] = useState(5);
  const modalRef = useRef<HTMLDivElement>(null);

  const { inProgress, planned, completed } = groupAndSortTasks(roadmapTasks);
  const allTasks = [...inProgress, ...planned, ...completed];

  // Define priority order
  const priorityOrder: { [key: string]: number } = {
    'CRITICAL': 1,
    'HIGH': 2,
    'MEDIUM': 3,
    'LOW': 4,
    'Unknown': 5, // Treat Unknown like Low or last
  };

  // Define status order
  const statusOrder: { [key: string]: number } = {
    'In Progress': 1,
    'Blocked': 2,
    'Planned': 3,
    'Completed': 4,
    'DONE': 4,
  };

  // Sort tasks
  const sortedTasks = [...roadmapTasks].sort((a, b) => {
    const statusDiff = (statusOrder[a.status] ?? 99) - (statusOrder[b.status] ?? 99);
    if (statusDiff !== 0) {
      return statusDiff;
    }
    // If statuses are the same, sort by priority
    const priorityDiff = (priorityOrder[a.priority] ?? 99) - (priorityOrder[b.priority] ?? 99);
    return priorityDiff;
  });

  const totalTasks = sortedTasks.length;

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setShowContribution(true);
  };

  const handleCloseModal = () => {
    setShowContribution(false);
  };

  const handleShowMore = () => {
    setVisibleCount(prevCount => Math.min(prevCount + 5, totalTasks));
  };

  // Handle Escape key 
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      handleCloseModal();
    }
  }, [handleCloseModal]); // Added handleCloseModal dependency

  // Simplified click handler for backdrop
  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
      // Close only if the click is directly on the backdrop, not the modal content
      if (event.target === event.currentTarget) {
          handleCloseModal();
      }
  };

  // Remove useEffect for global listeners, handle Escape globally
  useEffect(() => {
    if (showContribution) {
      document.addEventListener('keydown', handleKeyDown);
    } else {
      document.removeEventListener('keydown', handleKeyDown);
    }

    // Cleanup function
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showContribution, handleKeyDown]); // Removed handleClickOutside dependency


  return (
    <section id="roadmap" className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">Project Roadmap</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Follow our progress and see what's planned for the EGOS project.
          </p>
        </div>

        <div className="overflow-x-auto rounded-lg shadow">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted/50">
              <tr className="border-b transition-colors hover:bg-muted/50">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Subsystem(s)</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Priority</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-card">
              {sortedTasks.slice(0, visibleCount).map((item, index) => (
                <tr 
                  key={index} 
                  className={`hover:bg-muted/50 transition-colors cursor-pointer ${item.status === 'Completed' || item.status === 'DONE' ? 'opacity-60' : ''}`} 
                  onClick={() => handleTaskClick(item)}
                >
                  <td className="p-4 align-middle flex items-center gap-2">
                    {getStatusIcon(item.status)}
                    {item.status}
                  </td>
                  <td className="p-4 align-middle">{item.subsystem}</td>
                  <td className="p-4 align-middle font-mono text-sm">{item.id}</td>
                  <td className="p-4 align-middle">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityClass(item.priority)}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="p-4 align-middle text-sm">{item.titleKey}</td> 
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {visibleCount < totalTasks && (
          <div className="text-center mt-8">
            <Button onClick={handleShowMore} variant="secondary">
              Show More ({totalTasks - visibleCount} remaining)
            </Button>
          </div>
        )}
      </div>

      {showContribution && selectedTask && (
         <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={handleBackdropClick}> {/* Use handleBackdropClick */}
          <div ref={modalRef} className="bg-card p-6 rounded-lg shadow-xl max-w-2xl w-full mx-4 relative transform transition-all duration-300 scale-100 opacity-100 border border-border">
            <Button variant="ghost" size="icon" className="absolute top-3 right-3 text-muted-foreground hover:text-foreground" onClick={handleCloseModal} aria-label="Close modal">
              <X className="h-5 w-5" />
            </Button>
            <h3 className="text-2xl font-semibold mb-4">Task Details: {selectedTask.id}</h3>
            <div className="space-y-4 text-sm">
              <p><strong>Title:</strong> {selectedTask.titleKey}</p>
              <p className="flex items-center gap-2"><strong>Status:</strong> {getStatusIcon(selectedTask.status)} {selectedTask.status}</p>
              <p><strong>Priority:</strong> <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityClass(selectedTask.priority)}`}>{selectedTask.priority}</span></p>
              {selectedTask.subsystem && <p><strong>Subsystem:</strong> {selectedTask.subsystem}</p>}
              {selectedTask.phase && <p><strong>Phase:</strong> {selectedTask.phase}</p>}
              {selectedTask.detailsKey && <p className="mt-4 text-muted-foreground"><strong>Details:</strong> {selectedTask.detailsKey}</p>}
              
              {selectedTask.link && (
                <p>
                  <Link href={selectedTask.link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-primary hover:underline">
                    <ExternalLink className="h-4 w-4" />
                    View on GitHub
                  </Link>
                </p>
              )}

              <div className="border-t pt-4 mt-6">
                <h4 className="text-lg font-medium mb-3">Want to contribute?</h4>
                <p className="text-muted-foreground mb-4">
                  We welcome contributions! Find this issue on GitHub to discuss or start working on it.
                </p>
                <div className="flex flex-wrap gap-3">
                  <Button asChild>
                    <Link href={`https://github.com/enioxt/egos/issues/new?title=[Roadmap Task]: ${selectedTask.id} - ${selectedTask.titleKey}&body=Contributing to roadmap task: ${selectedTask.id}`} target="_blank" rel="noopener noreferrer">
                      <Github className="mr-2 h-4 w-4" /> Create Issue
                    </Link>
                  </Button>
                  <Button variant="secondary" asChild>
                    <Link href="/docs/CONTRIBUTING.md" target="_blank">
                      <BookOpen className="mr-2 h-4 w-4" /> Contribution Guide
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

// Helper to get priority class (avoids repeating logic)
const getPriorityClass = (priority: Task['priority']) => {
  switch(priority) {
    case 'CRITICAL': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'HIGH': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
    case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    case 'LOW': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  }
};
