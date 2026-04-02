/**
 * GH-052 — KOL Discovery & Classification
 * Fetches accounts @anoineim follows on X, classifies them by bio keywords,
 * scores signal quality, and outputs docs/gem-hunter/kol-list.json.
 *
 * Usage:
 *   bun scripts/kol-discovery.ts
 *   bun scripts/kol-discovery.ts --dry
 *   bun scripts/kol-discovery.ts --category=crypto
 */

import { writeFileSync } from 'fs';
import { join } from 'path';

// ── Types ────────────────────────────────────────────────────────────────────

type Category =
  | 'crypto'
  | 'ai-ml'
  | 'dev-tooling'
  | 'governance'
  | 'osint-intel'
  | 'markets'
  | 'uncategorized';

type SignalQuality = 'HIGH' | 'MEDIUM' | 'LOW';

interface XUser {
  id: string;
  name: string;
  username: string;
  description?: string;
  public_metrics?: {
    followers_count: number;
    following_count: number;
    tweet_count: number;
    listed_count: number;
  };
  created_at?: string;
  verified?: boolean;
}

interface KOLAccount {
  id: string;
  name: string;
  username: string;
  description: string;
  categories: Category[];
  signalQuality: SignalQuality;
  followers: number;
  tweets: number;
}

interface KOLOutput {
  version: string;
  generatedAt: string;
  total: number;
  stats: Record<Category, number>;
  accounts: KOLAccount[];
}

// ── Category keyword map ─────────────────────────────────────────────────────

const CATEGORY_KEYWORDS: Record<Category, string[]> = {
  crypto: ['bitcoin', 'ethereum', 'defi', 'nft', 'web3', 'token', 'blockchain', 'solana', 'altcoin'],
  'ai-ml': ['llm', 'machine learning', 'ai agent', 'transformer', 'neural', 'gpt', 'diffusion'],
  'dev-tooling': ['typescript', 'rust', 'golang', 'open source', 'developer', 'engineer', 'software'],
  governance: ['dao', 'protocol', 'governance', 'treasury', 'on-chain voting'],
  'osint-intel': ['osint', 'intelligence', 'surveillance', 'reconnaissance'],
  markets: ['trading', 'quant', 'alpha', 'fund', 'investor', 'portfolio'],
  uncategorized: [],
};

// ── Classification helpers ───────────────────────────────────────────────────

function classifyBio(bio: string): Category[] {
  const lower = bio.toLowerCase();
  const matched: Category[] = [];
  for (const [cat, keywords] of Object.entries(CATEGORY_KEYWORDS) as [Category, string[]][]) {
    if (cat === 'uncategorized') continue;
    if (keywords.some((kw) => lower.includes(kw))) matched.push(cat);
  }
  return matched.length > 0 ? matched : ['uncategorized'];
}

function scoreSignal(user: XUser, categories: Category[]): SignalQuality {
  const followers = user.public_metrics?.followers_count ?? 0;
  const tweets = user.public_metrics?.tweet_count ?? 0;
  const hasRelevantBio = !categories.includes('uncategorized');

  if (followers > 10_000 && tweets > 500 && hasRelevantBio) return 'HIGH';
  if (followers > 1_000 || tweets > 200) return 'MEDIUM';
  return 'LOW';
}

function isActive(user: XUser): boolean {
  const tweets = user.public_metrics?.tweet_count ?? 0;
  if (tweets <= 100) return false;
  if (!user.created_at) return true; // no date = don't filter out
  const created = new Date(user.created_at);
  return created < new Date('2025-01-01');
}

// ── X API helpers ────────────────────────────────────────────────────────────

const BASE = 'https://api.twitter.com/2';
const USER_FIELDS = 'id,name,username,description,public_metrics,created_at,verified';

async function xGet(url: string, token: string): Promise<Response> {
  return fetch(url, { headers: { Authorization: `Bearer ${token}` } });
}

async function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

async function resolveUserId(username: string, token: string): Promise<string> {
  const res = await xGet(`${BASE}/users/by/username/${username}?user.fields=id`, token);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to resolve @${username}: ${res.status} ${body}`);
  }
  const json = (await res.json()) as { data: { id: string } };
  return json.data.id;
}

async function fetchFollowing(userId: string, token: string): Promise<XUser[]> {
  const accounts: XUser[] = [];
  let paginationToken: string | undefined;
  let pages = 0;
  const MAX_ACCOUNTS = 1000;

  while (accounts.length < MAX_ACCOUNTS) {
    const params = new URLSearchParams({
      max_results: '100',
      'user.fields': USER_FIELDS,
    });
    if (paginationToken) params.set('pagination_token', paginationToken);

    const url = `${BASE}/users/${userId}/following?${params}`;
    let res = await xGet(url, token);

    // Rate-limit retry
    if (res.status === 429) {
      console.warn('Rate limited (429) — waiting 60s and retrying once...');
      await sleep(60_000);
      res = await xGet(url, token);
      if (!res.status.toString().startsWith('2')) {
        throw new Error(`Rate limit retry failed: ${res.status}`);
      }
    }

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`following endpoint error: ${res.status} ${body}`);
    }

    const json = (await res.json()) as {
      data?: XUser[];
      meta?: { next_token?: string; result_count?: number };
    };

    if (!json.data || json.data.length === 0) break;
    accounts.push(...json.data);
    pages++;

    paginationToken = json.meta?.next_token;
    if (!paginationToken) break;

    // 500ms delay between pages to respect rate limits
    await sleep(500);
    process.stdout.write(`\r  Fetched ${accounts.length} accounts (${pages} pages)...`);
  }

  process.stdout.write('\n');
  return accounts;
}

// ── CLI arg parsing ──────────────────────────────────────────────────────────

function parseArgs(): { dry: boolean; filterCategory: Category | null } {
  const args = process.argv.slice(2);
  const dry = args.includes('--dry');
  const catArg = args.find((a) => a.startsWith('--category='));
  const filterCategory = catArg ? (catArg.split('=')[1] as Category) : null;
  return { dry, filterCategory };
}

// ── Summary table ────────────────────────────────────────────────────────────

function printSummary(accounts: KOLAccount[], stats: Record<Category, number>): void {
  console.log('\n── Category Counts ──────────────────────────────');
  for (const [cat, count] of Object.entries(stats)) {
    if (count > 0) console.log(`  ${cat.padEnd(14)} ${count}`);
  }

  const top5 = accounts
    .filter((a) => a.signalQuality === 'HIGH')
    .sort((a, b) => b.followers - a.followers)
    .slice(0, 5);

  console.log('\n── Top 5 HIGH Signal Accounts ───────────────────');
  if (top5.length === 0) {
    console.log('  (none found)');
  } else {
    for (const a of top5) {
      console.log(`  @${a.username.padEnd(20)} ${String(a.followers).padStart(8)} followers  [${a.categories.join(', ')}]`);
    }
  }
  console.log('');
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const token = process.env.X_BEARER_TOKEN;
  if (!token) {
    console.error('ERROR: X_BEARER_TOKEN is not set. Export it or add it to .env before running.');
    process.exit(1);
  }

  const { dry, filterCategory } = parseArgs();
  const HANDLE = 'anoineim';

  console.log(`[kol-discovery] Resolving @${HANDLE}...`);
  const userId = await resolveUserId(HANDLE, token);
  console.log(`[kol-discovery] User ID: ${userId}`);

  console.log('[kol-discovery] Fetching following list (up to 1000)...');
  const raw = await fetchFollowing(userId, token);
  console.log(`[kol-discovery] Fetched ${raw.length} accounts total`);

  // Filter to active accounts
  const active = raw.filter(isActive);
  console.log(`[kol-discovery] Active accounts (pre-2025, >100 tweets): ${active.length}`);

  if (dry) {
    console.log(`\n[--dry] Would write ${active.length} active accounts. No file written.`);
    return;
  }

  // Build KOL account list
  const accounts: KOLAccount[] = active.map((u) => {
    const bio = u.description ?? '';
    const categories = classifyBio(bio);
    const signalQuality = scoreSignal(u, categories);
    return {
      id: u.id,
      name: u.name,
      username: u.username,
      description: bio,
      categories,
      signalQuality,
      followers: u.public_metrics?.followers_count ?? 0,
      tweets: u.public_metrics?.tweet_count ?? 0,
    };
  });

  // Apply --category filter if provided
  const filtered = filterCategory
    ? accounts.filter((a) => a.categories.includes(filterCategory))
    : accounts;

  // Build stats
  const stats: Record<Category, number> = {
    crypto: 0, 'ai-ml': 0, 'dev-tooling': 0, governance: 0,
    'osint-intel': 0, markets: 0, uncategorized: 0,
  };
  for (const a of filtered) {
    for (const cat of a.categories) stats[cat]++;
  }

  const output: KOLOutput = {
    version: '1.0.0',
    generatedAt: new Date().toISOString(),
    total: filtered.length,
    stats,
    accounts: filtered,
  };

  const outPath = join(process.cwd(), 'docs', 'gem-hunter', 'kol-list.json');
  writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`[kol-discovery] Written → ${outPath}`);

  printSummary(filtered, stats);
}

main().catch((err) => {
  console.error('[kol-discovery] Fatal:', err.message ?? err);
  process.exit(1);
});
