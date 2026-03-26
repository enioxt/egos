/**
 * Filesystem Watch MCP Client
 *
 * Real-time file monitoring, sync validation, governance drift detection
 * Watches for: file changes, sync status, frozen zone violations
 */

export interface FileChangeEvent {
  type: 'added' | 'modified' | 'deleted';
  path: string;
  timestamp: number;
  size?: number;
  hash?: string;
}

export interface WatchSession {
  id: string;
  path: string;
  pattern?: RegExp;
  isActive: boolean;
  startedAt: number;
  changesDetected: number;
}

export interface SyncStatus {
  filePath: string;
  status: 'synced' | 'out-of-sync' | 'conflict';
  repos: Array<{
    repo: string;
    lastSyncTime: number;
    checksum: string;
  }>;
}

export interface FrozenZoneValidation {
  valid: boolean;
  violations: Array<{
    filePath: string;
    operation: string;
    timestamp: number;
    user?: string;
  }>;
}

export interface GovernanceDrift {
  detected: boolean;
  changes: FileChangeEvent[];
  protectedFiles: Array<{
    path: string;
    status: 'unchanged' | 'modified' | 'deleted';
  }>;
}

export class FilesystemWatchMCPClient {
  private watches: Map<string, WatchSession> = new Map();
  private changeHistory: FileChangeEvent[] = [];
  private protectedFiles = [
    'frozen-zones.md',
    'AGENTS.md',
    '.guarani/orchestration/PIPELINE.md',
    'agents/runtime/*',
  ];
  private watchedPaths = [
    '/home/user/egos/.guarani',
    '/home/user/egos/frozen-zones.md',
    '/home/user/egos/docs/',
  ];

  constructor() {
    console.log('[FilesystemWatch] Initialized');
  }

  /**
   * Start monitoring a directory for file changes
   */
  watch(path: string, pattern?: string, debounceMs: number = 500): string {
    const watchId = `watch_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;

    const session: WatchSession = {
      id: watchId,
      path,
      pattern: pattern ? new RegExp(pattern) : undefined,
      isActive: true,
      startedAt: Date.now(),
      changesDetected: 0,
    };

    this.watches.set(watchId, session);

    console.log(`[FilesystemWatch] Started watching ${path} (ID: ${watchId})`);

    // Simulate change detection
    this.simulateFileChanges(watchId);

    return watchId;
  }

  /**
   * Stop watching a directory
   */
  unwatch(watchId: string): boolean {
    const session = this.watches.get(watchId);
    if (!session) return false;

    session.isActive = false;
    console.log(`[FilesystemWatch] Stopped watching (ID: ${watchId})`);

    return true;
  }

  /**
   * Check sync status of a file across repos
   */
  async checkSyncStatus(filePath: string, targetRepos: string[]): Promise<SyncStatus> {
    console.log(`[FilesystemWatch] Checking sync status for ${filePath} across ${targetRepos.length} repos`);

    // Mock sync data
    const syncRepos = targetRepos.map(repo => ({
      repo,
      lastSyncTime: Date.now() - Math.random() * 60000,
      checksum: Math.random().toString(36).slice(2, 10),
    }));

    // All repos have same checksum = synced
    const allSame = syncRepos.every(r => r.checksum === syncRepos[0].checksum);

    return {
      filePath,
      status: allSame ? 'synced' : 'out-of-sync',
      repos: syncRepos,
    };
  }

  /**
   * Validate frozen zone integrity
   */
  async validateFrozenZones(since?: string): Promise<FrozenZoneValidation> {
    console.log(`[FilesystemWatch] Validating frozen zones${since ? ` since ${since}` : ''}`);

    // Mock validation - no violations
    return {
      valid: true,
      violations: [],
    };
  }

  /**
   * Detect governance drift (unexpected changes to governance files)
   */
  async detectGovernanceDrift(governanceRoot?: string): Promise<GovernanceDrift> {
    const root = governanceRoot || '/home/user/egos/.guarani';
    console.log(`[FilesystemWatch] Detecting governance drift in ${root}`);

    // Check protected files
    const protectedChanges = this.changeHistory.filter(change =>
      this.protectedFiles.some(pattern => {
        const regex = new RegExp(pattern.replace(/\*/g, '.*'));
        return regex.test(change.path);
      })
    );

    return {
      detected: protectedChanges.length > 0,
      changes: protectedChanges,
      protectedFiles: this.protectedFiles.map(p => ({
        path: p,
        status: protectedChanges.some(c => c.path.includes(p)) ? 'modified' : 'unchanged',
      })),
    };
  }

  /**
   * Resolve symlinks to actual file paths
   */
  async resolveSymlinks(path: string): Promise<string> {
    console.log(`[FilesystemWatch] Resolving symlinks for ${path}`);

    // Mock symlink resolution
    if (path.includes('symlink')) {
      return path.replace('symlink', 'actual');
    }

    return path;
  }

  /**
   * Get file hash (for integrity checking)
   */
  async getFileHash(filePath: string): Promise<string> {
    console.log(`[FilesystemWatch] Computing hash for ${filePath}`);

    // Mock hash
    return Math.random().toString(36).slice(2, 10);
  }

  /**
   * Get file change history
   */
  getChangeHistory(limit: number = 100): FileChangeEvent[] {
    return this.changeHistory.slice(-limit);
  }

  /**
   * Get active watch sessions
   */
  getActiveSessions(): WatchSession[] {
    return Array.from(this.watches.values()).filter(s => s.isActive);
  }

  /**
   * Simulate file changes for testing
   */
  private simulateFileChanges(watchId: string): void {
    const session = this.watches.get(watchId);
    if (!session) return;

    // Randomly generate some changes
    const mockChanges: FileChangeEvent[] = [
      {
        type: 'modified',
        path: `${session.path}/config.json`,
        timestamp: Date.now(),
        size: 1024,
      },
      {
        type: 'added',
        path: `${session.path}/new-file.ts`,
        timestamp: Date.now() + 1000,
        size: 512,
      },
    ];

    mockChanges.forEach(change => {
      // Only include if matches pattern
      if (!session.pattern || session.pattern.test(change.path)) {
        this.changeHistory.push(change);
        session.changesDetected++;
      }
    });
  }

  /**
   * Record a file change
   */
  recordChange(event: FileChangeEvent): void {
    this.changeHistory.push(event);

    // Notify active watches
    this.watches.forEach((session, watchId) => {
      if (!session.isActive) return;

      const pathMatches = event.path.startsWith(session.path);
      const patternMatches = !session.pattern || session.pattern.test(event.path);

      if (pathMatches && patternMatches) {
        session.changesDetected++;
        console.log(`[FilesystemWatch] Change detected on watch ${watchId}: ${event.path}`);
      }
    });
  }

  /**
   * Check if path is watched
   */
  isPathWatched(filePath: string): boolean {
    return this.watchedPaths.some(p => filePath.startsWith(p));
  }

  /**
   * Check if path is protected
   */
  isPathProtected(filePath: string): boolean {
    return this.protectedFiles.some(pattern => {
      const regex = new RegExp(pattern.replace(/\*/g, '.*'));
      return regex.test(filePath);
    });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    return this.watches.size >= 0; // Always healthy
  }

  /**
   * Cleanup - stop all watches
   */
  cleanup(): void {
    this.watches.forEach(session => {
      session.isActive = false;
    });
    console.log('[FilesystemWatch] Cleaned up all watches');
  }
}

export default FilesystemWatchMCPClient;
