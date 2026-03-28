/**
 * GitHub Integration Contract
 * Defines the interface for GitHub API adapters
 */

export interface GitHubIssueEvent {
  action: 'opened' | 'closed' | 'edited' | 'commented';
  issue: {
    number: number;
    title: string;
    body: string;
    state: 'open' | 'closed';
    creator: string;
  };
  repository: string;
}

export interface GitHubAdapter {
  name: 'github';
  authenticate(token: string): Promise<void>;
  createIssue(repo: string, title: string, body: string): Promise<{ number: number; ok: boolean }>;
  listen(
    repo: string,
    callback: (event: GitHubIssueEvent) => Promise<void>
  ): Promise<() => void>;
  disconnect(): Promise<void>;
}

export class GitHubAdapterImpl implements GitHubAdapter {
  name = 'github' as const;

  async authenticate(token: string): Promise<void> {
    // TODO: Implement GitHub OAuth token validation
    console.log('GitHub authentication not yet implemented');
  }

  async createIssue(
    repo: string,
    title: string,
    body: string
  ): Promise<{ number: number; ok: boolean }> {
    // TODO: Implement GitHub REST API create issue
    throw new Error('GitHubAdapterImpl.createIssue not implemented');
  }

  async listen(
    repo: string,
    callback: (event: GitHubIssueEvent) => Promise<void>
  ): Promise<() => void> {
    // TODO: Implement GitHub webhook listener for issue events
    throw new Error('GitHubAdapterImpl.listen not implemented');
  }

  async disconnect(): Promise<void> {
    // TODO: Implement cleanup
  }
}
