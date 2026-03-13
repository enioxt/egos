import { readFileSync, writeFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

const REPOS = ['egos', 'egos-lab', 'carteira-livre', 'br-acc', 'forja', 'policia', 'egos-self'];
const ROOT = '/home/enio';

interface RepoProfile {
  name: string;
  hasGovernance: boolean;
  agentCount: number;
  scriptCount: number;
  lastCommit?: string;
  ssotScore: number;
}

const profiles: RepoProfile[] = [];

for (const repo of REPOS) {
  const repoPath = join(ROOT, repo);
  if (!existsSync(repoPath)) continue;

  const profile: RepoProfile = {
    name: repo,
    hasGovernance: existsSync(join(repoPath, '.guarani')),
    agentCount: 0,
    scriptCount: 0,
    ssotScore: 0,
  };

  // Check agents registry
  const registryPath = join(repoPath, 'agents', 'registry', 'agents.json');
  if (existsSync(registryPath)) {
    try {
      const data = JSON.parse(readFileSync(registryPath, 'utf-8'));
      profile.agentCount = data.agents?.length || 0;
    } catch {}
  }

  // Check scripts
  const scriptsPath = join(repoPath, 'scripts');
  if (existsSync(scriptsPath)) {
    profile.scriptCount = readdirSync(scriptsPath).filter(f => f.endsWith('.ts') || f.endsWith('.js')).length;
  }

  // Check SSOT
  if (existsSync(join(repoPath, '.windsurfrules'))) profile.ssotScore += 25;
  if (existsSync(join(repoPath, 'AGENTS.md'))) profile.ssotScore += 25;
  if (existsSync(join(repoPath, 'TASKS.md'))) profile.ssotScore += 25;
  if (profile.hasGovernance) profile.ssotScore += 25;

  profiles.push(profile);
}

console.log(JSON.stringify(profiles, null, 2));
