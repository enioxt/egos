/**
 * Calendar & Schedule MCP Client
 *
 * SLA tracking, sprint planning, deadline management
 * Relevant for: EGOS-111, task lifecycle, governance SLA
 */

export interface SLADeadline {
  taskId: string;
  stage: 'analyst' | 'pm' | 'architect' | 'sm';
  deadline: string; // ISO8601
  hoursRemaining: number;
  breached: boolean;
}

export interface Milestone {
  id: string;
  name: string;
  targetDate: string; // ISO8601
  sprintId?: string;
  status: 'pending' | 'in-progress' | 'completed';
  completion?: number; // 0-100
}

export interface SprintPlan {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  durationDays: number;
  tasks: Array<{
    id: string;
    title: string;
    assigned: string[];
    status: string;
  }>;
  capacity?: {
    totalHours: number;
    allocatedHours: number;
    utilization: number;
  };
}

export interface DeadlineAlert {
  id: string;
  deadlineTime: string;
  taskId?: string;
  alertMinutesBefore: number;
  notificationChannels: string[];
  isActive: boolean;
}

export interface TeamCapacity {
  teamId: string;
  totalCapacityHours: number;
  allocatedHours: number;
  availableHours: number;
  utilization: number;
  members: Array<{
    name: string;
    allocatedHours: number;
  }>;
}

export class CalendarMCPClient {
  private milestones: Map<string, Milestone> = new Map();
  private alerts: Map<string, DeadlineAlert> = new Map();
  private teamCapacities: Map<string, TeamCapacity> = new Map();

  private slaHours = {
    analyst: 24,
    pm: 24,
    architect: 24,
    sm: 24,
  };

  private sprintLengthDays = 14;

  constructor(config: {
    slaHours?: Record<string, number>;
    sprintLengthDays?: number;
  } = {}) {
    if (config.slaHours) {
      this.slaHours = { ...this.slaHours, ...config.slaHours };
    }
    if (config.sprintLengthDays) {
      this.sprintLengthDays = config.sprintLengthDays;
    }

    console.log('[Calendar] Initialized');
  }

  /**
   * Calculate SLA deadline for a task stage
   */
  getSLADeadline(
    taskId: string,
    stage: 'analyst' | 'pm' | 'architect' | 'sm',
    startTime?: Date
  ): SLADeadline {
    const start = startTime || new Date();
    const slaHour = this.slaHours[stage];
    const deadline = new Date(start.getTime() + slaHour * 60 * 60 * 1000);

    const now = new Date();
    const hoursRemaining = (deadline.getTime() - now.getTime()) / (60 * 60 * 1000);
    const breached = hoursRemaining < 0;

    console.log(
      `[Calendar] SLA deadline for ${taskId} (${stage}): ${deadline.toISOString()} (${Math.ceil(hoursRemaining)}h remaining)`
    );

    return {
      taskId,
      stage,
      deadline: deadline.toISOString(),
      hoursRemaining: Math.max(0, hoursRemaining),
      breached,
    };
  }

  /**
   * Track and record a sprint/release milestone
   */
  trackMilestone(name: string, targetDate: string, sprintId?: string): Milestone {
    const id = `milestone_${Date.now()}`;

    const milestone: Milestone = {
      id,
      name,
      targetDate,
      sprintId,
      status: 'pending',
      completion: 0,
    };

    this.milestones.set(id, milestone);
    console.log(`[Calendar] Tracked milestone: ${name} (target: ${targetDate})`);

    return milestone;
  }

  /**
   * Set a deadline alert
   */
  setDeadlineAlert(
    deadlineTime: string,
    alertMinutesBefore: number,
    notificationChannels: string[],
    taskId?: string
  ): DeadlineAlert {
    const id = `alert_${Date.now()}`;

    const alert: DeadlineAlert = {
      id,
      deadlineTime,
      taskId,
      alertMinutesBefore,
      notificationChannels,
      isActive: true,
    };

    this.alerts.set(id, alert);
    console.log(
      `[Calendar] Set deadline alert: ${alertMinutesBefore}min before ${deadlineTime} via ${notificationChannels.join(', ')}`
    );

    return alert;
  }

  /**
   * Get current sprint plan
   */
  getSprintPlan(sprintId?: string): SprintPlan {
    // Mock current sprint
    const now = new Date();
    const sprintStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // Started 7 days ago
    const sprintEnd = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000); // Ends in 7 days

    const plan: SprintPlan = {
      id: sprintId || 'sprint-2026-03',
      name: 'Sprint Mar 2026-03',
      startDate: sprintStart.toISOString(),
      endDate: sprintEnd.toISOString(),
      durationDays: this.sprintLengthDays,
      tasks: [
        {
          id: 'EGOS-111',
          title: 'Implement MCP integration',
          assigned: ['Integration Engineer'],
          status: 'in-progress',
        },
        {
          id: 'EGOS-112',
          title: 'Create MCP router agent',
          assigned: ['Integration Engineer'],
          status: 'completed',
        },
        {
          id: 'EGOS-113',
          title: 'Integration tests',
          assigned: ['QA Engineer'],
          status: 'pending',
        },
      ],
      capacity: {
        totalHours: 160,
        allocatedHours: 120,
        utilization: 75,
      },
    };

    return plan;
  }

  /**
   * Check team availability for commitment
   */
  checkCapacity(teamId?: string, requiredHours?: number): TeamCapacity {
    const team = teamId || 'team-integration';
    const existing = this.teamCapacities.get(team);

    if (existing && requiredHours) {
      const hasCapacity = existing.availableHours >= requiredHours;
      console.log(
        `[Calendar] Capacity check for ${team}: ${hasCapacity ? 'OK' : 'INSUFFICIENT'} (need ${requiredHours}h, have ${existing.availableHours}h)`
      );
    }

    // Return mock capacity data
    return (
      existing || {
        teamId: team,
        totalCapacityHours: 160,
        allocatedHours: 100,
        availableHours: 60,
        utilization: 62.5,
        members: [
          {
            name: 'Integration Engineer',
            allocatedHours: 60,
          },
          {
            name: 'Tech Lead',
            allocatedHours: 40,
          },
        ],
      }
    );
  }

  /**
   * Update milestone status
   */
  updateMilestone(milestoneId: string, updates: Partial<Milestone>): Milestone | null {
    const milestone = this.milestones.get(milestoneId);
    if (!milestone) return null;

    Object.assign(milestone, updates);
    console.log(`[Calendar] Updated milestone ${milestoneId}: status=${milestone.status}, completion=${milestone.completion}%`);

    return milestone;
  }

  /**
   * Deactivate an alert
   */
  deactivateAlert(alertId: string): boolean {
    const alert = this.alerts.get(alertId);
    if (!alert) return false;

    alert.isActive = false;
    console.log(`[Calendar] Deactivated alert: ${alertId}`);

    return true;
  }

  /**
   * Get upcoming deadlines
   */
  getUpcomingDeadlines(days: number = 7): Milestone[] {
    const now = new Date();
    const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

    return Array.from(this.milestones.values())
      .filter(m => {
        const mDate = new Date(m.targetDate);
        return mDate >= now && mDate <= future;
      })
      .sort((a, b) => new Date(a.targetDate).getTime() - new Date(b.targetDate).getTime());
  }

  /**
   * Get SLA summary for a task across all stages
   */
  getSLASummary(taskId: string): {
    taskId: string;
    stages: SLADeadline[];
    allOnTrack: boolean;
    breachedCount: number;
  } {
    const stages: SLADeadline[] = [];
    let breachedCount = 0;

    for (const stage of ['analyst', 'pm', 'architect', 'sm'] as const) {
      const sla = this.getSLADeadline(taskId, stage);
      stages.push(sla);
      if (sla.breached) breachedCount++;
    }

    return {
      taskId,
      stages,
      allOnTrack: breachedCount === 0,
      breachedCount,
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    return true; // Always healthy
  }
}

export default CalendarMCPClient;
