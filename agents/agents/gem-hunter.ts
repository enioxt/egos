/**
 * AGENT-027: Gem Hunter v5.0
 * Preference-driven discovery engine for open-source tools, models, papers, and frameworks
 * across GitHub, GitHub Code, HuggingFace Hub, arXiv, Exa, Reddit, StackOverflow, and ProductHunt.
 *
 * v5.0 adds:
 *   - GitHub Code Search (search/code API for file-level discovery)
 *   - SSOT Lego Atomization (--deep flag, extracts reusable blocks via LLM)
 *   - Content Relevance Guard (filters spam/gaming repos)
 *   - CJK/non-Latin content filter
 *   - Source-type scoring (penalizes YouTube/Medium, rewards GitHub/NPM)
 *   - Evolution engine anti-poisoning (only high-scoring gems feed keywords)
 *   - GitHub Code result enrichment (parent repo metadata)
 *
 * v3.2 adds:
 *   - Reddit search (reddit.com/search.json, no auth, top posts)
 *   - StackOverflow search (api.stackexchange.com, no auth, vote-sorted)
 *   - ProductHunt search (via Exa scoped to producthunt.com)
 *   - SQLite historical tracking (bun:sqlite, docs/gem-hunter/history.db)
 *   - --history flag to query past runs and detect multi-run trends
 *
 * v3 adds user preference filters:
 *   --lang=typescript       Filter by programming language (GitHub)
 *   --license=mit           Filter by license (GitHub: mit, apache-2.0, gpl-3.0, etc)
 *   --min-stars=100         Minimum stars threshold
 *   --stack=react,bun       Boost keywords matching your stack
 *   --preferences           Load filters from .egos/gem-preferences.json
 *
 * APIs:
 *   - GitHub Search API (public, no token needed, 10 req/min)
 *   - HuggingFace Hub API (free, no token needed for search)
 *   - Exa API (requires EXA_API_KEY in .env)
 *
 * Usage:
 *   bun agent:run gem-hunter --dry                           # Preview search plan
 *   bun agent:run gem-hunter --exec                          # Execute all searches
 *   bun agent:run gem-hunter --exec --topic=agents           # Single category
 *   bun agent:run gem-hunter --exec --quick                  # Top 3 per keyword
 *   bun agent:run gem-hunter --exec --lang=python --min-stars=500  # Filtered
 *   bun agent:run gem-hunter --exec --preferences            # Load from file
 *   bun agent:run gem-hunter --exec --analyze                # Generate AI synthesis
 *   bun agent:run gem-hunter --exec --track=x-signals-public --x-limit=10  # Read daily X signals + draft posts
 *   bun agent:run gem-hunter --exec --track=community-signals  # Reddit + StackOverflow + ProductHunt
 *   bun agent:run gem-hunter --history                       # Show multi-run trending gems from SQLite
 */

import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { callAI } from "../../packages/shared/src/social/ai-engine";
import { appendGemSignal } from "../../packages/shared/src/gem-signals";

const ROOT = join(import.meta.dir, "../..");
const REPORTS_DIR = join(ROOT, "docs/gem-hunter");
const LATEST_RUN_PATH = join(REPORTS_DIR, "latest-run.json");
const EXA_API_KEY = process.env.EXA_API_KEY || "";
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || "";
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "";
const X_BEARER_TOKEN = process.env.X_BEARER_TOKEN || "";
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID || "";
const ARXIV_MAX_RESULTS = 10;
const GEM_HUNTER_VERSION = "6.0";

// ── Content Quality Guards ──────────────────────────────────────────────

/** Check if description has >40% CJK/Hangul/non-Latin characters */
function hasMajorityCJK(text: string): boolean {
  if (!text || text.length < 10) return false;
  const cjk = text.match(/[\u3000-\u9FFF\uAC00-\uD7AF\uF900-\uFAFF]/g);
  return cjk ? cjk.length / text.length > 0.4 : false;
}

/** Validate that a gem's description has semantic overlap with the query keywords */
function isContentRelevant(gem: GemResult, queryKeywords: string[]): boolean {
  // Non-GitHub sources (exa, arxiv, etc) have their own relevance — skip this check
  if (!["github", "github-code"].includes(gem.source)) return true;
  // CJK-dominant descriptions are almost never relevant to our English queries
  if (hasMajorityCJK(gem.description) || hasMajorityCJK(gem.name)) return false;
  // Check that at least 1 meaningful keyword from the query appears in name+description
  const text = `${gem.name} ${gem.description}`.toLowerCase();
  const meaningfulTerms = queryKeywords
    .flatMap(kw => kw.toLowerCase().split(/\s+/))
    .filter(w => w.length > 3 && !['open', 'source', 'tool', 'free', 'best', 'with', 'from', 'that', 'this'].includes(w));
  return meaningfulTerms.some(term => text.includes(term));
}

type GemSource = "github" | "github-code" | "huggingface" | "huggingface-space" | "exa" | "arxiv" | "hackernews" | "npm" | "zenodo" | "x-public" | "x-api" | "reddit" | "stackoverflow" | "producthunt" | "papers-with-code" | "papers-without-code";
type SearchTrack = "core" | "web-extraction" | "x-signals-public" | "governance-plugplay" | "community-signals" | "early-warning" | "papers-without-code";

interface GemResult {
  name: string;
  source: GemSource;
  url: string;
  description: string;
  stars?: number;
  downloads?: number;
  relevance: "high" | "medium" | "low";
  category: string;
  lastUpdated?: string;
  language?: string;
  license?: string;
  rawUrl?: string; // Optional raw URL for fetching exact content
  ssotAssetPath?: string; // Local path to the extracted Lego block markdown
  legoBlockType?: string; // Assigned block type
  structureBonus?: number; // GH-060: validated structure score bonus (0-25)
  abstractScore?: number;  // GH-056: LLM abstract triage score (0-100)
}

interface GemPreferences {
  language?: string;
  license?: string;
  minStars?: number;
  stack?: string[];
  excludeTopics?: string[];
}

function loadPreferences(): GemPreferences {
  const prefsPath = join(ROOT, '.egos', 'gem-preferences.json');
  if (!existsSync(prefsPath)) return {};
  try {
    return JSON.parse(readFileSync(prefsPath, 'utf-8'));
  } catch { return {}; }
}

interface SearchQuery {
  topic: string;
  keywords: string[];
  sources: GemSource[];
  category: string;
  track?: SearchTrack;
}

interface LatestRunManifest {
  generatedAt: string;
  reportPath: string;
  totalGems: number;
  quick: boolean;
  topicFilter: string | null;
  tracks: SearchTrack[];
  byCategory: Record<string, number>;
  bySource: Record<string, number>;
}

const DEFAULT_QUERIES: SearchQuery[] = [
  {
    topic: "AI Report & Dashboard Generators",
    keywords: [
      "AI agent static dashboard generator",
      "autonomous report generation LLM",
      "agentic BI dashboard from prompt",
    ],
    sources: ["github", "github-code", "exa"],
    category: "report-generators",
  },
  {
    topic: "Autonomous Agents (Social + Ops)",
    keywords: [
      "autonomous AI agent social media ops",
      "AI agent Twitter X automation open source",
      "agent-as-a-service autonomous ops",
    ],
    sources: ["github", "github-code", "exa"],
    category: "autonomous-agents",
  },
  {
    topic: "AI Agents / MCP / Tool Use",
    keywords: [
      "MCP server tool 2025 2026",
      "AI agent framework typescript open source",
      "autonomous agent orchestration",
    ],
    sources: ["github", "huggingface", "huggingface-space", "exa", "npm", "hackernews"],
    category: "agents",
  },
  {
    topic: "Agent Orchestration / Control Plane",
    keywords: [
      "multi agent orchestration platform open source",
      "agent workflow engine self hosted",
      "agentic workflow automation typescript",
    ],
    sources: ["github", "exa"],
    category: "control-plane",
  },
  {
    topic: "OSINT / Public Data Brazil",
    keywords: [
      "brazil public data SDK open source",
      "OSINT tool open source intelligence",
      "government transparency API",
    ],
    sources: ["github", "exa"],
    category: "osint",
  },
  // REMOVED: Device Bridge — security policy SEC-001
  {
    topic: "Local Research / Self-Hosted Search",
    keywords: [
      "perplexica self hosted search engine",
      "local first research assistant open source",
      "self hosted RAG web search",
    ],
    sources: ["github", "huggingface", "exa"],
    category: "local-research",
  },
  {
    topic: "Static Site / Report Templates",
    keywords: [
      "Vite static dashboard template tailwind",
      "single file HTML report generator",
      "chart.js dashboard template open source",
    ],
    sources: ["github", "exa", "npm"],
    category: "templates",
  },
  {
    topic: "Blockchain / x402 / On-Chain Payments",
    keywords: [
      "x402 payment protocol",
      "Base chain SDK typescript",
      "on-chain micropayment agent",
    ],
    sources: ["github", "exa"],
    category: "blockchain",
  },
  {
    topic: "HuggingFace Trending Models & Spaces",
    keywords: [
      "code generation model",
      "text to HTML generation",
      "autonomous agent model",
    ],
    sources: ["huggingface", "huggingface-space", "hackernews"],
    category: "hf-trending",
  },
  {
    topic: "Multi-Agent Coordination / Chat Rooms",
    keywords: [
      "multi-agent chat room coordination real-time",
      "agent-to-agent communication MCP mention trigger",
      "AI agents collaborative workspace open source",
      "agentchattr OR agent chat server localhost",
    ],
    sources: ["github", "exa"],
    category: "multi-agent-coordination",
  },
  {
    topic: "Declarative Sub-Agents / Chains",
    keywords: [
      "declarative sub-agent YAML frontmatter markdown",
      "agent chain parallel execution background async",
      "pi-subagents OR subagent delegation TUI",
      "agent workflow pipeline sequential fan-out",
    ],
    sources: ["github", "exa"],
    category: "declarative-agents",
  },
  {
    topic: "AutoResearch / Autonomous Experiment Loops",
    keywords: [
      "autoresearch autonomous experiment loop keep discard",
      "AI agent iterative optimization git branch",
      "autonomous research agent program.md metric",
      "karpathy autoresearch fork adaptation",
    ],
    sources: ["github", "exa"],
    category: "autoresearch",
  },
  {
    topic: "Agent Safety / Red-Teaming",
    keywords: [
      "autonomous agent safety red-teaming vulnerability",
      "multi-agent security stakeholder model",
      "OpenClaw agent sandbox isolation",
      "AI agent prompt injection defense open source",
    ],
    sources: ["github", "exa"],
    category: "agent-safety",
  },
  {
    topic: "Academic Research / arXiv",
    keywords: [
      "multi-agent systems collaboration autonomous",
      "agentic AI autonomous code agents orchestration",
      "OSINT open source intelligence NLP graph",
      "AI agent safety red-teaming vulnerability",
      "declarative agent workflow chain parallel",
    ],
    sources: ["arxiv", "exa"],
    category: "arxiv",
  },
  {
    topic: "Quantum-Inspired Software Architecture (VRCP)",
    keywords: [
      "quantum-inspired software architecture fault tolerance",
      "topological data analysis resilience software",
      "decoherence suppression pattern multiplicative layers",
      "vacuum-resonant coherence protection",
    ],
    sources: ["arxiv", "zenodo", "exa"],
    category: "quantum-software-architecture",
  },
  {
    topic: "Web Extraction / Rendered Capture",
    keywords: [
      "web extraction rendered html playwright crawler open source",
      "javascript rendering web scraper typescript open source",
      "llm markdown crawler firecrawl crawl4ai crawlee open source",
    ],
    sources: ["github", "github-code", "exa", "npm", "hackernews"],
    category: "web-extraction",
    track: "web-extraction",
  },
  {
    topic: "X Signals / Public Discovery",
    keywords: [
      "web3 agent framework release",
      "browser automation crawler open source",
      "ai agent open source github release",
      "agent harness lightweight pure python release",
      "claude code alternative open source",
      "minimal agent harness skills hooks",
    ],
    sources: ["x-api", "x-public"],
    category: "x-signals-public",
    track: "x-signals-public",
  },
  {
    topic: "Early Warning — Researcher Launches (Day 0)",
    keywords: [
      "from:huang_chao4969 OR from:HKUDS github release",
      "OpenHarness OR LightRAG OR nanobot OR AutoAgent release",
      "pure python agent harness 44x smaller release today",
      "ultra-lightweight agent open source initial commit",
      "claude code skills hooks plugins alternative github",
      "from:jxnl OR from:emollick OR from:karpathy agent release",
      "agent framework initial commit release v0.1",
    ],
    sources: ["x-api", "x-public", "github"],
    category: "early-warning",
    track: "early-warning",
  },
  {
    topic: "Strategic MCP Servers / Governance",
    keywords: [
      "model context protocol governance server typescript",
      "MCP compliance policy engine open source",
      "governance as code MCP server",
    ],
    sources: ["github", "exa", "npm", "hackernews"],
    category: "mcp-governance-servers",
    track: "governance-plugplay",
  },
  {
    topic: "A2A Agent Cards / Interoperability",
    keywords: [
      "A2A agent card typescript example",
      "agent to agent protocol agent card open source",
      "A2A governance agent card",
    ],
    sources: ["github", "exa", "arxiv", "hackernews"],
    category: "a2a-agent-cards",
    track: "governance-plugplay",
  },
  {
    topic: "Agent Adapter / Polyglot Wrappers",
    keywords: [
      "polyglot agent adapter MCP wrapper open source",
      "external agent wrapper language agnostic ai agent",
      "agent interoperability adapter layer typescript",
    ],
    sources: ["github", "exa", "npm"],
    category: "agent-adapters",
    track: "governance-plugplay",
  },
  {
    topic: "Agent Marketplaces / Registries / Tool Routers",
    keywords: [
      "OpenClaw skills registry marketplace",
      "agent registry MCP marketplace open source",
      "Composio tool router MCP A2A",
    ],
    sources: ["github", "exa", "npm", "hackernews", "x-api", "x-public"],
    category: "agent-marketplaces",
    track: "governance-plugplay",
  },
  {
    topic: "Strategic Signals / MCP + A2A + OpenClaw",
    keywords: [
      "MCP server release A2A OpenClaw",
      "agent registry MCP Composio release",
      "governance agent protocol release",
    ],
    sources: ["x-api", "x-public", "exa"],
    category: "strategic-signals",
    track: "governance-plugplay",
  },
  {
    topic: "Community Signals / Reddit Discussions",
    keywords: [
      "AI agent framework open source 2025 2026",
      "autonomous agent TypeScript Python best",
      "MCP server tool claude open source",
    ],
    sources: ["reddit", "stackoverflow"],
    category: "community-signals",
    track: "community-signals",
  },
  {
    topic: "ProductHunt AI Developer Tools",
    keywords: [
      "AI agent developer tool launch",
      "open source LLM framework product",
      "autonomous agent platform product",
    ],
    sources: ["producthunt"],
    category: "producthunt-tools",
    track: "community-signals",
  },
  {
    topic: "Agent Scaling Laws / Coordination Architectures",
    keywords: [
      "agent scaling laws coordination architectures centralized decentralized hybrid",
      "error amplification multi-agent overhead redundancy capability saturation",
      "architecture selector agent systems predictive model task characteristics",
      "Towards a Science of Scaling Agent Systems arXiv 2512.08296",
      "multi-agent scaling empirical benchmark diminishing returns tool-heavy",
    ],
    sources: ["github", "arxiv", "papers-with-code", "exa"],
    category: "agent-scaling",
  },
  {
    topic: "Low-Star Research-Backed Implementations",
    keywords: [
      "arXiv implementation clean-room stars:<20 agent coordination",
      "research paper code implementation multi-agent framework minimal",
      "empirical validation agent architecture benchmark reproducible MIT",
    ],
    sources: ["github", "papers-with-code"],
    category: "research-gems",
  },
  // Papers Without Code — Ideas that haven't been implemented yet (v6.0 / GH-051)
  {
    topic: "Papers Without Code — Multi-Agent Coordination",
    keywords: ["multi-agent coordination framework"],
    sources: ["papers-without-code"],
    category: "papers-without-code",
    track: "papers-without-code",
  },
  {
    topic: "Papers Without Code — Agent Governance",
    keywords: ["agent governance architecture"],
    sources: ["papers-without-code"],
    category: "papers-without-code",
    track: "papers-without-code",
  },
  {
    topic: "Papers Without Code — LLM Tool Use",
    keywords: ["LLM tool use orchestration"],
    sources: ["papers-without-code"],
    category: "papers-without-code",
    track: "papers-without-code",
  },
  {
    topic: "Papers Without Code — Code Intelligence",
    keywords: ["code intelligence knowledge graph"],
    sources: ["papers-without-code"],
    category: "papers-without-code",
    track: "papers-without-code",
  },
  {
    topic: "Papers Without Code — Autonomous SWE Agent",
    keywords: ["autonomous software engineering agent"],
    sources: ["papers-without-code"],
    category: "papers-without-code",
    track: "papers-without-code",
  },
];

// ── API Callers ──────────────────────────────────────────────────────────

async function searchPapersWithCode(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://paperswithcode.com/api/v1/search/?q=${encodeURIComponent(query)}&page=1&items_per_page=${maxResults}`;
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.results || [])
      .filter((r: any) => r.paper?.url_abs || r.repository?.url)
      .map((r: any) => ({
        name: r.paper?.title || r.repository?.name || "Untitled",
        source: "papers-with-code" as GemSource,
        url: r.repository?.url || r.paper?.url_abs || "",
        description: `${r.paper?.abstract?.slice(0, 180) || ""} [PWC: ${r.paper?.arxiv_id || "no-arxiv"}]`,
        relevance: (r.repository?.stars ?? 0) > 100 ? "high" as const : "medium" as const,
        category: "",
        stars: r.repository?.stars,
        lastUpdated: r.paper?.published,
      }));
  } catch {
    return [];
  }
}

// ── Papers WITHOUT Code (v6.0 / GH-051) ─────────────────────────────────
// Strategy: Query arXiv for recent CS papers, then check PWC to confirm
// they have NO implementations. These are ideas nobody has coded yet —
// the highest-value discoveries for the EGOS ecosystem.
async function searchPapersWithoutCode(query: string, maxResults = 10): Promise<GemResult[]> {
  const results: GemResult[] = [];

  try {
    // Step 1: Search arXiv for recent CS papers (AI, Multi-Agent, SE, CL, ML)
    const categories = ['cs.AI', 'cs.MA', 'cs.SE', 'cs.CL', 'cs.LG'];
    const catFilter = categories.map(c => `cat:${c}`).join('+OR+');
    const params = new URLSearchParams({
      search_query: `(${catFilter})+AND+all:${encodeURIComponent(query)}`,
      start: '0',
      max_results: String(maxResults * 2), // Over-fetch to filter
      sortBy: 'submittedDate',
      sortOrder: 'descending',
    });

    const res = await fetch(`http://export.arxiv.org/api/query?${params}`);
    if (!res.ok) return [];
    const xml = await res.text();

    const entryBlocks = xml.split('<entry>').slice(1);

    for (const block of entryBlocks) {
      const title = block.match(/<title>([^<]+)<\/title>/)?.[1]?.trim().replace(/\n/g, ' ') || '';
      const id = block.match(/<id>([^<]+)<\/id>/)?.[1] || '';
      const summary = block.match(/<summary>([\s\S]*?)<\/summary>/)?.[1]?.trim().replace(/\n/g, ' ').slice(0, 300) || '';
      const published = block.match(/<published>([^<]+)<\/published>/)?.[1]?.split('T')[0] || '';
      const arxivId = id.match(/abs\/(.+)/)?.[1] || '';

      // Filter: Skip if description mentions github.com (likely has code)
      const hasGithubLink = block.toLowerCase().includes('github.com') ||
                           block.toLowerCase().includes('github:') ||
                           summary.toLowerCase().includes('our code is available') ||
                           summary.toLowerCase().includes('code available at') ||
                           summary.toLowerCase().includes('implementation available');

      if (hasGithubLink) continue;

      // Step 2: Check PWC for this paper — if it has 0 implementations, it's a gem
      let pwcImplementations = -1; // -1 = not checked
      if (arxivId) {
        try {
          await new Promise(r => setTimeout(r, 500)); // Rate limit PWC
          const pwcRes = await fetch(`https://paperswithcode.com/api/v1/papers/${arxivId}/`);
          if (pwcRes.ok) {
            // Check if paper has implementations
            const repoRes = await fetch(`https://paperswithcode.com/api/v1/papers/${arxivId}/repositories/`);
            if (repoRes.ok) {
              const repoData = await repoRes.json() as any;
              pwcImplementations = (repoData.results || repoData || []).length;
            }
          }
        } catch {
          // PWC check failed, still include paper
        }
      }

      // Only include papers with 0 implementations (or PWC check failed)
      if (pwcImplementations > 0) continue;

      if (title && id) {
        results.push({
          name: `[NO CODE] ${title.slice(0, 90)}`,
          source: 'papers-without-code' as GemSource,
          url: id,
          description: `${summary} [arxiv:${arxivId}] [implementations:${pwcImplementations === -1 ? 'unknown' : pwcImplementations}]`,
          relevance: 'high' as const,
          category: 'papers-without-code',
          lastUpdated: published,
        });
      }

      if (results.length >= maxResults) break;
    }
  } catch {
    // Silently fail — this is a best-effort search
  }

  return results;
}

async function searchZenodo(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://zenodo.org/api/records?q=${encodeURIComponent(query)}&size=${maxResults}&sort=-mostrecent`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.hits?.hits || []).map((r: any) => ({
      name: r.metadata.title,
      source: "zenodo" as const,
      url: r.links.html || r.doi_url,
      description: r.metadata.description?.replace(/<[^>]*>?/gm, '').slice(0, 200) || "No description",
      relevance: "medium" as const,
      category: "",
      lastUpdated: r.created?.split("T")[0],
      downloads: r.stats?.downloads,
    }));
  } catch {
    return [];
  }
}

async function searchGitHub(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const headers: Record<string, string> = { Accept: "application/vnd.github+json" };
    if (GITHUB_TOKEN) headers.Authorization = `Bearer ${GITHUB_TOKEN}`;
    const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=stars&order=desc&per_page=${maxResults * 2}`;
    const res = await fetch(url, { headers });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.items || []).map((r: any) => ({
      name: r.full_name,
      source: "github" as const,
      url: r.html_url,
      description: (r.description || "").slice(0, 200),
      stars: r.stargazers_count,
      relevance: r.stargazers_count > 1000 ? "high" : r.stargazers_count > 100 ? "medium" : "low",
      category: "",
      lastUpdated: r.pushed_at?.split("T")[0],
      language: r.language?.toLowerCase(),
      license: r.license?.spdx_id?.toLowerCase(),
    }));
  } catch {
    return [];
  }
}

async function searchGitHubCode(query: string, maxResults = 3): Promise<GemResult[]> {
  if (!GITHUB_TOKEN) return []; // Code Search API requires authentication
  try {
    const headers: Record<string, string> = {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${GITHUB_TOKEN}`,
    };
    const url = `https://api.github.com/search/code?q=${encodeURIComponent(query)}&per_page=${maxResults}`;
    const res = await fetch(url, { headers });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    const results: GemResult[] = [];
    for (const r of (data.items || [])) {
      const repoFullName = r.repository?.full_name || "unknown";
      // Enrich with parent repo metadata
      let repoStars = 0;
      let repoLastPush: string | undefined;
      let repoLicense: string | undefined;
      try {
        const repoRes = await fetch(`https://api.github.com/repos/${repoFullName}`, { headers });
        if (repoRes.ok) {
          const repoData = (await repoRes.json()) as any;
          repoStars = repoData.stargazers_count || 0;
          repoLastPush = repoData.pushed_at?.split("T")[0];
          repoLicense = repoData.license?.spdx_id?.toLowerCase();
        }
      } catch {}
      results.push({
        name: `${repoFullName}/${r.name}`,
        source: "github-code" as const,
        url: r.html_url,
        rawUrl: r.html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/"),
        description: `File: ${r.path} in ${repoFullName} (${repoStars}★)`,
        stars: repoStars,
        relevance: repoStars > 500 ? "high" as const : repoStars > 50 ? "medium" as const : "low" as const,
        category: "",
        lastUpdated: repoLastPush,
        license: repoLicense,
      });
    }
    return results;
  } catch {
    return [];
  }
}

async function searchHuggingFace(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://huggingface.co/api/models?search=${encodeURIComponent(query)}&sort=likes&direction=-1&limit=${maxResults}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any[];
    return data.map((m: any) => ({
      name: m.modelId || m.id,
      source: "huggingface" as const,
      url: `https://huggingface.co/${m.modelId || m.id}`,
      description: (m.pipeline_tag || m.tags?.join(", ") || "").slice(0, 200),
      downloads: m.downloads,
      stars: m.likes,
      relevance: (m.likes || 0) > 100 ? "high" : (m.likes || 0) > 10 ? "medium" : "low",
      category: "",
      lastUpdated: m.lastModified?.split("T")[0],
    }));
  } catch {
    return [];
  }
}

async function searchArxiv(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const params = new URLSearchParams({
      search_query: `all:${query}`,
      start: "0",
      max_results: String(maxResults),
      sortBy: "submittedDate",
      sortOrder: "descending",
    });
    const res = await fetch(`http://export.arxiv.org/api/query?${params}`);
    if (!res.ok) return [];
    const xml = await res.text();
    const entries: GemResult[] = [];
    const entryBlocks = xml.split("<entry>").slice(1);
    for (const block of entryBlocks) {
      const title = block.match(/<title>([^<]+)<\/title>/)?.[1]?.trim().replace(/\n/g, " ") || "";
      const id = block.match(/<id>([^<]+)<\/id>/)?.[1] || "";
      const summary = block.match(/<summary>([^<]+)<\/summary>/)?.[1]?.trim().replace(/\n/g, " ").slice(0, 200) || "";
      const published = block.match(/<published>([^<]+)<\/published>/)?.[1]?.split("T")[0] || "";
      if (title && id) {
        entries.push({
          name: title.slice(0, 100),
          source: "arxiv" as const,
          url: id,
          description: summary,
          relevance: "medium" as const,
          category: "",
          lastUpdated: published,
        });
      }
    }
    return entries;
  } catch {
    return [];
  }
}

async function searchExa(query: string, maxResults = 5): Promise<GemResult[]> {
  if (!EXA_API_KEY) return [];
  try {
    const res = await fetch("https://api.exa.ai/search", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": EXA_API_KEY },
      body: JSON.stringify({ query, numResults: maxResults, type: "auto" }),
    });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.results || []).map((r: any) => ({
      name: r.title || r.url,
      source: "exa" as const,
      url: r.url,
      description: (r.text || r.title || "").slice(0, 200),
      relevance: "medium" as const,
      category: "",
    }));
  } catch {
    return [];
  }
}

async function searchXApiSignals(query: string, maxResults = 10): Promise<GemResult[]> {
  if (!X_BEARER_TOKEN) return [];
  try {
    const params = new URLSearchParams({
      query: `${query} (github OR \"open source\" OR repo OR release) -is:retweet -is:reply`,
      max_results: String(Math.min(Math.max(maxResults, 10), 25)),
      expansions: "author_id",
      "tweet.fields": "created_at,author_id,public_metrics",
      "user.fields": "username,name",
    });
    const res = await fetch(`https://api.twitter.com/2/tweets/search/recent?${params}`, {
      headers: { Authorization: `Bearer ${X_BEARER_TOKEN}` },
    });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    const users = new Map<string, { username?: string; name?: string }>(
      (data.includes?.users || []).map((user: any) => [user.id, { username: user.username, name: user.name }]),
    );
    return (data.data || []).map((tweet: any) => {
      const user = users.get(tweet.author_id);
      const username = user?.username || "unknown";
      const likes = tweet.public_metrics?.like_count || 0;
      return {
        name: `@${username}`,
        source: "x-api" as const,
        url: `https://x.com/${username}/status/${tweet.id}`,
        description: (tweet.text || "").replace(/\s+/g, " ").slice(0, 200),
        stars: likes,
        relevance: likes > 25 ? "high" as const : likes > 5 ? "medium" as const : "low" as const,
        category: "",
        lastUpdated: tweet.created_at?.split("T")[0],
      };
    });
  } catch {
    return [];
  }
}

async function searchXPublicSignals(query: string, maxResults = 5): Promise<GemResult[]> {
  const scopedQuery = `${query} (site:x.com OR site:twitter.com) (github OR \"open source\" OR repo OR release)`;
  const results = await searchExa(scopedQuery, maxResults);
  return results
    .filter((r) => /x\.com|twitter\.com/.test(r.url))
    .map((r) => ({
      ...r,
      source: "x-public" as const,
      relevance: r.description.length > 80 ? "medium" as const : "low" as const,
    }));
}

async function searchHuggingFaceSpaces(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://huggingface.co/api/spaces?search=${encodeURIComponent(query)}&limit=${maxResults}&sort=likes&direction=-1`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any[];
    return data.map((s: any) => ({
      name: s.id,
      source: "huggingface-space" as const,
      url: `https://huggingface.co/spaces/${s.id}`,
      description: `HuggingFace Space. Last Modified: ${s.lastModified?.split("T")[0] || "unknown"}`,
      stars: s.likes,
      relevance: (s.likes || 0) > 100 ? "high" : "medium",
      category: "",
      lastUpdated: s.lastModified?.split("T")[0],
    }));
  } catch {
    return [];
  }
}

async function searchHackerNews(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `http://hn.algolia.com/api/v1/search?query=${encodeURIComponent(query)}&tags=story&hitsPerPage=${maxResults}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.hits || []).map((h: any) => ({
      name: h.title?.slice(0, 100) || "HN Story",
      source: "hackernews" as const,
      url: h.url || `https://news.ycombinator.com/item?id=${h.objectID}`,
      description: `HN score: ${h.points} | Comments: ${h.num_comments}`,
      stars: h.points,
      relevance: "high" as const,
      category: "",
      lastUpdated: h.created_at?.split("T")[0],
    }));
  } catch {
    return [];
  }
}

async function searchNPM(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://registry.npmjs.org/-/v1/search?text=${encodeURIComponent(query)}&size=${maxResults}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.objects || []).map((pkg: any) => ({
      name: pkg.package.name,
      source: "npm" as const,
      url: pkg.package.links?.npm || `https://www.npmjs.com/package/${pkg.package.name}`,
      description: (pkg.package.description || "").slice(0, 200),
      relevance: "medium" as const,
      category: "",
      lastUpdated: pkg.package.date?.split("T")[0],
    }));
  } catch {
    return [];
  }
}

async function searchReddit(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const url = `https://www.reddit.com/search.json?q=${encodeURIComponent(query)}&sort=top&t=month&limit=${maxResults * 2}`;
    const res = await fetch(url, { headers: { "User-Agent": "egos-gem-hunter/3.2 (bot)" } });
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    const posts = data?.data?.children || [];
    return posts
      .filter((p: any) => p.data?.score > 5)
      .slice(0, maxResults)
      .map((p: any) => ({
        name: (p.data.title || "").slice(0, 100),
        source: "reddit" as const,
        url: `https://www.reddit.com${p.data.permalink}`,
        description: `r/${p.data.subreddit} | score: ${p.data.score} | ${(p.data.selftext || p.data.url || "").slice(0, 150)}`,
        stars: p.data.score,
        relevance: p.data.score > 100 ? "high" as const : p.data.score > 20 ? "medium" as const : "low" as const,
        category: "",
        lastUpdated: new Date(p.data.created_utc * 1000).toISOString().split("T")[0],
      }));
  } catch {
    return [];
  }
}

async function searchStackOverflow(query: string, maxResults = 5): Promise<GemResult[]> {
  try {
    const params = new URLSearchParams({
      order: "desc",
      sort: "votes",
      intitle: query,
      site: "stackoverflow",
      pagesize: String(maxResults),
      filter: "withbody",
    });
    const url = `https://api.stackexchange.com/2.3/search/advanced?${params}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = (await res.json()) as any;
    return (data.items || []).slice(0, maxResults).map((item: any) => ({
      name: (item.title || "").slice(0, 100),
      source: "stackoverflow" as const,
      url: item.link,
      description: `score: ${item.score} | answers: ${item.answer_count} | tags: ${(item.tags || []).slice(0, 4).join(", ")}`,
      stars: item.score,
      relevance: item.score > 50 ? "high" as const : item.score > 10 ? "medium" as const : "low" as const,
      category: "",
      lastUpdated: item.last_activity_date
        ? new Date(item.last_activity_date * 1000).toISOString().split("T")[0]
        : undefined,
    }));
  } catch {
    return [];
  }
}

async function searchProductHunt(query: string, maxResults = 5): Promise<GemResult[]> {
  if (!EXA_API_KEY) return [];
  const scopedQuery = `site:producthunt.com ${query} AI agent OR open source OR developer tool`;
  const results = await searchExa(scopedQuery, maxResults * 2);
  return results
    .filter((r) => /producthunt\.com\/posts\//.test(r.url))
    .slice(0, maxResults)
    .map((r) => ({ ...r, source: "producthunt" as const }));
}

// ── SQLite Historical Tracking ────────────────────────────────────────────

const DB_PATH = join(REPORTS_DIR, "history.db");

function getHistoryDb() {
  const { Database } = require("bun:sqlite") as typeof import("bun:sqlite");
  const db = new Database(DB_PATH, { create: true });
  db.exec(`
    CREATE TABLE IF NOT EXISTS gems (
      url TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      source TEXT NOT NULL,
      category TEXT NOT NULL,
      description TEXT,
      stars INTEGER,
      first_seen TEXT NOT NULL,
      last_seen TEXT NOT NULL,
      run_count INTEGER DEFAULT 1,
      max_score INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_date TEXT NOT NULL,
      total_gems INTEGER NOT NULL,
      by_source TEXT NOT NULL,
      by_category TEXT NOT NULL
    );
  `);
  return db;
}

function saveGemsToHistory(gems: GemResult[], runDate: string): void {
  try {
    const db = getHistoryDb();
    const today = runDate;
    const upsert = db.prepare(`
      INSERT INTO gems (url, name, source, category, description, stars, first_seen, last_seen, run_count, max_score)
      VALUES ($url, $name, $source, $category, $description, $stars, $today, $today, 1, $score)
      ON CONFLICT(url) DO UPDATE SET
        last_seen = $today,
        run_count = run_count + 1,
        stars = COALESCE($stars, stars),
        max_score = MAX(max_score, $score)
    `);
    const insertRun = db.prepare(`INSERT INTO runs (run_date, total_gems, by_source, by_category) VALUES ($date, $total, $src, $cat)`);
    const tx = db.transaction((items: GemResult[]) => {
      for (const g of items) {
        upsert.run({ $url: g.url, $name: g.name.slice(0, 200), $source: g.source, $category: g.category, $description: (g.description || "").slice(0, 500), $stars: g.stars ?? null, $today: today, $score: scoreGem(g) });
      }
    });
    tx(gems);
    const bySrc = gems.reduce<Record<string, number>>((a, g) => { a[g.source] = (a[g.source] || 0) + 1; return a; }, {});
    const byCat = gems.reduce<Record<string, number>>((a, g) => { a[g.category] = (a[g.category] || 0) + 1; return a; }, {});
    insertRun.run({ $date: today, $total: gems.length, $src: JSON.stringify(bySrc), $cat: JSON.stringify(byCat) });
    console.log(`🗄️  History DB updated: ${gems.length} gems saved (${DB_PATH})`);
    db.close();
  } catch (e) {
    console.warn(`⚠️  History DB write failed (non-fatal):`, e);
  }
}

// ── Supabase Persistence (dual-write alongside SQLite) ────────────────────

function getSupabaseClient(): any | null {
  try {
    const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) return null;
    const { createClient } = require("@supabase/supabase-js");
    return createClient(url, key);
  } catch {
    return null;
  }
}

async function syncGemsToSupabase(gems: GemResult[], runDate: string): Promise<void> {
  const client = getSupabaseClient();
  if (!client) return;
  try {
    const rows = gems.map((g) => ({
      url: g.url,
      name: g.name.slice(0, 200),
      source: g.source,
      category: g.category,
      description: (g.description || "").slice(0, 500),
      stars: g.stars ?? null,
      first_seen: runDate,
      last_seen: runDate,
      run_count: 1,
      max_score: scoreGem(g),
    }));
    const { error } = await client.from("gem_hunter_gems").upsert(rows, {
      onConflict: "url",
      ignoreDuplicates: false,
    });
    if (error) throw error;

    const bySrc = gems.reduce<Record<string, number>>((a, g) => { a[g.source] = (a[g.source] || 0) + 1; return a; }, {});
    const byCat = gems.reduce<Record<string, number>>((a, g) => { a[g.category] = (a[g.category] || 0) + 1; return a; }, {});
    await client.from("gem_hunter_runs").insert({
      run_date: runDate,
      total_gems: gems.length,
      by_source: bySrc,
      by_category: byCat,
      mode: isDry ? "dry" : "exec",
    });
    console.log(`☁️  Supabase synced: ${gems.length} gems + run log`);
  } catch (e: any) {
    console.warn(`⚠️  Supabase sync failed (non-fatal):`, e?.message || e);
  }
}

function getTrendingFromHistory(minRuns = 2, limit = 10): Array<{ url: string; name: string; run_count: number; max_score: number }> {
  try {
    const db = getHistoryDb();
    const rows = db.query(`SELECT url, name, run_count, max_score FROM gems WHERE run_count >= ? ORDER BY run_count DESC, max_score DESC LIMIT ?`).all(minRuns, limit) as any[];
    db.close();
    return rows;
  } catch {
    return [];
  }
}

// ── Main ─────────────────────────────────────────────────────────────────

const isDry = process.argv.includes("--dry");
const isExec = process.argv.includes("--exec");
const isQuick = process.argv.includes("--quick");
const queryFilter = process.argv.find((a) => a.startsWith("--topic="))?.split("=")[1];
const cliTracks = process.argv.find((a) => a.startsWith("--track="))?.split("=")[1]?.split(",").filter(Boolean) as SearchTrack[] | undefined;
const cliLicense = process.argv.find((a) => a.startsWith("--license="))?.split("=")[1];
const cliMinStars = parseInt(process.argv.find((a) => a.startsWith("--min-stars="))?.split("=")[1] || "0", 10);
const cliStack = process.argv.find((a) => a.startsWith("--stack="))?.split("=")[1]?.split(",");
const usePrefsFile = process.argv.includes("--preferences");
const doAnalyze = process.argv.includes("--analyze");
const cliLang = process.argv.find((a) => a.startsWith("--lang="))?.split("=")[1];
const cliXLimit = parseInt(process.argv.find((a) => a.startsWith("--x-limit="))?.split("=")[1] || "10", 10);
const doHistory = process.argv.includes("--history");
const doDeepAtomize = process.argv.includes("--deep");

async function main() {
  const filePrefs = usePrefsFile ? loadPreferences() : {};
  const prefs: GemPreferences = {
    language: cliLang || filePrefs.language,
    license: cliLicense || filePrefs.license,
    minStars: cliMinStars || filePrefs.minStars || 0,
    stack: cliStack || filePrefs.stack,
    excludeTopics: filePrefs.excludeTopics,
  };

  if (doHistory) {
    const trends = getTrendingFromHistory(2, 15);
    if (trends.length === 0) {
      console.log("📜 No multi-run trends yet (need 2+ runs in history.db)");
    } else {
      console.log(`\n📜 Multi-Run Trending Gems (appeared in 2+ runs):\n`);
      for (const t of trends) {
        console.log(`   [${t.run_count}x] score=${t.max_score} — ${t.name}`);
        console.log(`         ${t.url}`);
      }
    }
    process.exit(0);
  }

  console.log(`🔎 Gem Hunter v${GEM_HUNTER_VERSION}`);
  console.log(`   Mode: ${isDry ? "DRY RUN" : isExec ? "EXECUTE" : "DRY RUN (default)"}`);
  console.log(`   Exa API: ${EXA_API_KEY ? "✅" : "❌ missing (Reddit/ProductHunt degraded)"}`);
  console.log(`   GitHub token: ${GITHUB_TOKEN ? "✅ (authenticated)" : "⚠️ anonymous (10 req/min)"}`);
  console.log(`   X API: ${X_BEARER_TOKEN ? `✅ (limit ${cliXLimit})` : "⚠️ fallback to public signals"}`);
  if (prefs.language) console.log(`   Language filter: ${prefs.language}`);
  if (prefs.license) console.log(`   License filter: ${prefs.license}`);
  if (prefs.minStars) console.log(`   Min stars: ${prefs.minStars}`);
  if (prefs.stack?.length) console.log(`   Stack boost: ${prefs.stack.join(", ")}`);
  if (cliTracks?.length) console.log(`   Tracks: ${cliTracks.join(", ")}`);
  if (doAnalyze) console.log(`   AI Analysis: ✅ enabled (OpenRouter)`);
  if (doDeepAtomize) console.log(`   Atomization (Lego Blocks): ✅ enabled for top gems`);

  // GH-053: Load evolution queries from previous run and inject into query pool
  const evolutionQueriesPath = join(REPORTS_DIR, "next-queries.json");
  const dynamicQueries: SearchQuery[] = [];
  if (existsSync(evolutionQueriesPath)) {
    try {
      const evo = JSON.parse(readFileSync(evolutionQueriesPath, "utf-8"));
      for (const sq of (evo.suggestedQueries || [])) {
        dynamicQueries.push({
          topic: sq.topic,
          keywords: sq.keywords,
          sources: ["github", "arxiv", "exa"],
          category: "evolution-auto",
          track: "core",
        });
      }
      if (dynamicQueries.length > 0) {
        console.log(`\n🧬 Evolution: Injected ${dynamicQueries.length} auto-generated queries from previous run`);
      }
    } catch {}
  }
  // GH-057: Inject context-aware keywords from git log + TASKS.md
  const contextKeywords = loadContextSignals();
  if (contextKeywords.length > 0) {
    dynamicQueries.push({
      topic: "Context-Aware: Current Sprint",
      keywords: [contextKeywords.slice(0, 5).join(" "), contextKeywords.slice(5, 10).join(" ")].filter(Boolean),
      sources: ["github", "arxiv"],
      category: "context-auto",
      track: "core",
    });
    console.log(`\n🎯 Context: Injected sprint keywords — ${contextKeywords.slice(0, 5).join(", ")}`);
  }

  const ALL_QUERIES = [...DEFAULT_QUERIES, ...dynamicQueries];

  const queries = ALL_QUERIES.filter((q) => {
    const topicMatch = queryFilter ? q.category === queryFilter : true;
    const track = q.track || "core";
    const trackMatch = cliTracks?.length ? cliTracks.includes(track) : true;
    return topicMatch && trackMatch;
  });
  const activeTracks = [...new Set(queries.map((q) => q.track || "core"))] as SearchTrack[];

  if (queries.length === 0) {
    console.error(`❌ No queries found for topic: ${queryFilter}`);
    console.log(`   Available: ${DEFAULT_QUERIES.map((q) => q.category).join(", ")}`);
    process.exit(1);
  }

  console.log(`\n📋 Search Plan (${queries.length} topics, ${queries.reduce((s, q) => s + q.keywords.length, 0)} keywords):`);
  for (const q of queries) {
    console.log(`   • ${q.topic} → ${q.sources.join(", ")} (${q.keywords.length} keywords)`);
  }

  if (isDry || !isExec) {
    console.log("\n✅ Dry run complete. Use --exec to run searches.");
    return;
  }

  // Execute real searches
  const maxPerKeyword = isQuick ? 3 : 5;
  const allResults: GemResult[] = [];
  const DELAY_MS = 1200; // rate limit buffer

  for (const q of queries) {
    console.log(`\n🔍 ${q.topic}...`);
    for (let keyword of q.keywords) {
      // Inject language filter into GitHub queries
      if (prefs.language && q.sources.includes("github")) {
        keyword += ` language:${prefs.language}`;
      }
      if (prefs.license && q.sources.includes("github")) {
        keyword += ` license:${prefs.license}`;
      }
      // Boost stack keywords
      if (prefs.stack?.length && q.sources.includes("github")) {
        keyword += " " + prefs.stack.join(" ");
      }
      const results: GemResult[] = [];

      if (q.sources.includes("github")) {
        const gh = await searchGitHub(keyword, maxPerKeyword);
        results.push(...gh);
        if (gh.length) await new Promise((r) => setTimeout(r, DELAY_MS));
      }
      if (q.sources.includes("github-code")) {
        // We refine the keyword for code search to ensure files
        const codeKw = `${keyword} extension:ts OR extension:tsx OR extension:py`;
        const ghc = await searchGitHubCode(codeKw, maxPerKeyword);
        results.push(...ghc);
        if (ghc.length) await new Promise((r) => setTimeout(r, DELAY_MS + 2000)); // Code API is stricter
      }
      if (q.sources.includes("huggingface")) {
        const hf = await searchHuggingFace(keyword, maxPerKeyword);
        results.push(...hf);
      }
      if (q.sources.includes("arxiv")) {
        const arxiv = await searchArxiv(keyword, maxPerKeyword);
        results.push(...arxiv);
        if (arxiv.length) await new Promise((r) => setTimeout(r, 3500)); // arXiv rate limit: 1 req/3s
      }
      if (q.sources.includes("zenodo")) {
        const zenodo = await searchZenodo(keyword, maxPerKeyword);
        results.push(...zenodo);
      }
      if (q.sources.includes("exa")) {
        const exa = await searchExa(keyword, maxPerKeyword);
        results.push(...exa);
      }
      if (q.sources.includes("x-api")) {
        const xApiSignals = await searchXApiSignals(keyword, cliXLimit);
        results.push(...xApiSignals);
      }
      if (q.sources.includes("x-public")) {
        const xSignals = await searchXPublicSignals(keyword, maxPerKeyword);
        results.push(...xSignals);
      }
      if (q.sources.includes("huggingface-space")) {
        const hfs = await searchHuggingFaceSpaces(keyword, maxPerKeyword);
        results.push(...hfs);
      }
      if (q.sources.includes("hackernews")) {
        const hn = await searchHackerNews(keyword, maxPerKeyword);
        results.push(...hn);
      }
      if (q.sources.includes("npm")) {
        const npm = await searchNPM(keyword, maxPerKeyword);
        results.push(...npm);
      }
      if (q.sources.includes("reddit")) {
        const reddit = await searchReddit(keyword, maxPerKeyword);
        results.push(...reddit);
        if (reddit.length) await new Promise((r) => setTimeout(r, 1500)); // Reddit rate limit
      }
      if (q.sources.includes("stackoverflow")) {
        const so = await searchStackOverflow(keyword, maxPerKeyword);
        results.push(...so);
        if (so.length) await new Promise((r) => setTimeout(r, 1000));
      }
      if (q.sources.includes("producthunt")) {
        const ph = await searchProductHunt(keyword, maxPerKeyword);
        results.push(...ph);
      }
      if (q.sources.includes("papers-with-code")) {
        const pwc = await searchPapersWithCode(keyword, maxPerKeyword);
        results.push(...pwc);
      }
      if (q.sources.includes("papers-without-code")) {
        const pwoc = await searchPapersWithoutCode(keyword, isQuick ? 3 : 5);
        results.push(...pwoc);
        if (pwoc.length) await new Promise((r) => setTimeout(r, 3000)); // arXiv rate limit
      }

      for (const r of results) r.category = q.category;
      // Content relevance guard: filter irrelevant GitHub results
      const relevant = results.filter(r => isContentRelevant(r, q.keywords));
      const filtered = results.length - relevant.length;
      allResults.push(...relevant);
      console.log(`   "${keyword}" → ${relevant.length} results${filtered ? ` (${filtered} irrelevant filtered)` : ""}`);
    }
  }

  // Deduplicate by URL
  const seen = new Set<string>();
  let unique = allResults.filter((r) => {
    if (seen.has(r.url)) return false;
    seen.add(r.url);
    return true;
  });

  // Post-filter by preferences
  if (prefs.minStars) {
    const before = unique.length;
    unique = unique.filter((r) => (r.stars ?? 0) >= (prefs.minStars || 0) || r.source !== "github");
    if (unique.length < before) console.log(`\n⭐ Filtered ${before - unique.length} results below ${prefs.minStars} stars`);
  }
  const beforeXNoise = unique.length;
  unique = unique.filter((r) => !["x-public", "x-api"].includes(r.source) || isXSignalRelevant(r));
  if (unique.length < beforeXNoise) console.log(`\n🧹 Filtered ${beforeXNoise - unique.length} noisy X results`);

  console.log(`\n📊 Total: ${unique.length} unique gems found`);
  const byCategory = unique.reduce<Record<string, number>>((acc, r) => {
    acc[r.category] = (acc[r.category] || 0) + 1;
    return acc;
  }, {});
  const bySource = unique.reduce<Record<string, number>>((acc, r) => {
    acc[r.source] = (acc[r.source] || 0) + 1;
    return acc;
  }, {});

  // Generate report
  const timestamp = new Date().toISOString().split("T")[0];
  const reportPath = join(REPORTS_DIR, `gems-${timestamp}.md`);

  if (!existsSync(REPORTS_DIR)) mkdirSync(REPORTS_DIR, { recursive: true });

  let aiSynthesis = "";
  if (doAnalyze && OPENROUTER_API_KEY && unique.length > 0) {
    console.log(`\n🧠 Generating AI synthesis for top gems...`);
    const topGems = unique.slice(0, 15).map(r =>
      `${r.name} (${r.source}): ${r.description} - ${r.url}`
    ).join("\n");

    try {
      const prompt = `You are a senior tech lead evaluating tools discovered via an automated scout agent for the EGOS lab. EGOS is an advanced, rules-based, agentic TypeScript/Python ecosystem that values zero-dependency, mathematical rigor (Sacred Math), and topological software resilience (like VRCP).\n\nAnalyze the following top discovered gems and write a concise, bulleted Executive Synthesis (max 300 words) explaining *why* these specific tools, frameworks, or papers matter for our architecture, and which 1-2 we should prioritize adopting or reading:\n\n${topGems}`;

      const res = await callAI({
        userMessage: prompt,
        channelId: "gem-hunter",
        userId: "gem-hunter",
        userName: "GemHunter",
        platform: "discord",
        openrouterApiKey: OPENROUTER_API_KEY
      });
      aiSynthesis = res.reply;
      console.log(`✅ AI synthesis complete.`);
    } catch (e) {
      console.error(`❌ Failed to generate AI synthesis:`, e);
      aiSynthesis = "> AI synthesis failed or timed out.";
    }
  } else if (doAnalyze && !OPENROUTER_API_KEY) {
    console.log(`\n⚠️ Missing OPENROUTER_API_KEY, skipping AI analysis.`);
  }

  // GH-060: Structural validation for top GitHub gems
  const githubTopGems = unique
    .filter(g => ["github", "github-code"].includes(g.source))
    .sort((a, b) => scoreGem(b) - scoreGem(a))
    .slice(0, 15);
  if (githubTopGems.length > 0) {
    console.log(`\n🏗️ GH-060: Validating structure for top ${githubTopGems.length} GitHub gems...`);
    await Promise.allSettled(githubTopGems.map(g => validateGemStructure(g)));
  }

  // GH-056: Multi-stage paper pipeline (LLM triage + scaffold)
  const papersThisRun = unique.filter(g => g.source === "papers-without-code" || g.category === "papers-without-code");
  if (papersThisRun.length > 0 && OPENROUTER_API_KEY) {
    await runPaperPipeline(papersThisRun, timestamp);
  }

  // Atomization process (Lego blocks)
  if (doDeepAtomize && OPENROUTER_API_KEY && unique.length > 0) {
    console.log(`\n🧩 Extracting SSOT Lego assets (Atomization)...`);
    await atomizeTopGems(unique, timestamp);
  }

  const report = generateReport(unique, timestamp, aiSynthesis);
  writeFileSync(reportPath, report);
  console.log(`📝 Report saved: ${reportPath}`);

  saveEvolutionState(unique);

  // GH-055: Persist hot gems to signals.json + fire Telegram alert
  const hotGems = unique
    .map(g => ({ gem: g, score: scoreGem(g) }))
    .filter(({ score }) => score >= 80)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);
  for (const { gem, score } of hotGems) {
    appendGemSignal({
      name: gem.name,
      url: gem.url,
      score,
      category: gem.category,
      date: new Date().toISOString(),
      headline: gem.description.slice(0, 120),
    });
  }
  if (hotGems.length > 0) {
    console.log(`\n🔥 ${hotGems.length} hot gem(s) scored ≥80 this run`);
    await sendGemTelegramAlert(hotGems);
  }

  saveGemsToHistory(unique, timestamp);
  syncGemsToSupabase(unique, timestamp).catch(() => {});
  saveLatestRun({
    generatedAt: new Date().toISOString(),
    reportPath,
    totalGems: unique.length,
    quick: isQuick,
    topicFilter: queryFilter || null,
    tracks: activeTracks,
    byCategory,
    bySource,
  });

  console.log("\n📈 By category:");
  for (const [cat, count] of Object.entries(byCategory)) console.log(`   ${cat}: ${count}`);
}

function daysSince(lastUpdated?: string): number | null {
  if (!lastUpdated) return null;
  const diffMs = Date.now() - new Date(lastUpdated).getTime();
  if (!Number.isFinite(diffMs)) return null;
  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}

function isWebExtractionRelevant(gem: GemResult): boolean {
  const text = `${gem.name} ${gem.description}`.toLowerCase();
  const strongSignals = /playwright|crawlee|crawl4ai|firecrawl|puppeteer|browser-use|scraper|crawler|extraction|rendered|headless|markdown/;
  const weakSignals = /typescript\b|nuxt\b|directory crawler|lighthouse audit|best open-source|\bvs\b|advanced typescript/;
  return strongSignals.test(text) && !weakSignals.test(text);
}

function isXSignalRelevant(gem: GemResult): boolean {
  const text = `${gem.name} ${gem.description} ${gem.url}`.toLowerCase();
  const isEarlyWarning = /(harness|lightweight|pure python|minimal agent|initial commit|v0\.1|44x|3% of|claude code alternative|openharness|lightrag|nanobot|autoagent)/.test(text);
  const isGeneral = /(github|open source|release|crawler|scraper|browser|agent)/.test(text);
  return (isEarlyWarning || isGeneral) && !/(posts \/ x|profile|account)/.test(text);
}

function isPlugPlayRelevant(gem: GemResult): boolean {
  const text = `${gem.name} ${gem.description} ${gem.url}`.toLowerCase();
  return /(mcp|model context protocol|a2a|agent2agent|agent card|governance|policy|registry|tool router|adapter|interoperability|firewall|compliance)/.test(text);
}

function isOfficialStrategicSource(gem: GemResult): boolean {
  const url = gem.url.toLowerCase();
  return /(github\.com|npmjs\.com|modelcontextprotocol|a2aprotocol|a2aproject|composio\.dev|agentregistry|openclaw|playbooks\.com|konghq\.com)/.test(url);
}

function isStrategicNoise(gem: GemResult): boolean {
  // reddit/producthunt are intentional sources — only flag as noise when source=exa leaks them in non-community contexts
  if (["reddit", "stackoverflow", "producthunt"].includes(gem.source)) return false;
  const url = gem.url.toLowerCase();
  return /(medium\.com|reddit\.com|linkedin\.com|youtube\.com)/.test(url);
}

function scoreGem(gem: GemResult): number {
  let score = gem.relevance === "high" ? 50 : gem.relevance === "medium" ? 30 : 10;
  if (gem.stars) score += Math.min(20, Math.log10(gem.stars + 1) * 6);
  if (gem.downloads) score += Math.min(12, Math.log10(gem.downloads + 1) * 3);
  const ageDays = daysSince(gem.lastUpdated);
  if (ageDays != null) {
    score += ageDays <= 30 ? 14 : ageDays <= 90 ? 8 : ageDays <= 180 ? 4 : 0;
  }
  // CJK/non-Latin penalty
  if (hasMajorityCJK(gem.description) || hasMajorityCJK(gem.name)) {
    score -= 30;
  }

  // ── Research-backed bonus (low-star/high-value detection) ─────────────
  // Repos that cite arXiv papers or come from Papers With Code get a major bonus
  // This counteracts the star-bias that would otherwise bury 3-star gems
  const text = `${gem.name} ${gem.description}`.toLowerCase();
  const hasArxivCitation = /arxiv[:\s]*\d{4}\.\d{4,5}|arxiv\.org\/abs\//.test(text);
  const hasPaperBackedSignals = /empirical|benchmark|accuracy\s*[≥>]\s*\d{2}%|error\s+amplification|scaling\s+law|validated|f1\s*[=:]\s*\d/.test(text);
  const hasResearchStructure = /architecture\s*selector|coordination\s*metric|predictive\s*model|leave-one.*cross.?validation/.test(text);
  if (hasArxivCitation) score += 18;
  if (hasPaperBackedSignals) score += 12;
  if (hasResearchStructure) score += 10;
  // Low-star + research signals = hidden gem (inverted star bonus)
  if ((gem.stars ?? 0) < 20 && (hasArxivCitation || hasPaperBackedSignals)) {
    score += 15; // "low-star gem" bonus — these are the ones we want to find early
  }
  // Papers With Code source bonus
  if (gem.source === "papers-with-code") score += 12;

  // Source-type scoring: reward code sources, penalize non-code
  if (["github", "github-code", "npm"].includes(gem.source)) score += 5;
  if (/youtube\.com|medium\.com|linkedin\.com|superteams\.ai/.test(gem.url)) score -= 15;
  if (gem.category === "web-extraction") score += isWebExtractionRelevant(gem) ? 18 : -18;
  if (["x-public", "x-api"].includes(gem.source)) score += isXSignalRelevant(gem) ? 18 : -20;
  if (/playwright|crawlee|crawl4ai|firecrawl|puppeteer|browser-use|scraper|crawler|extraction/i.test(`${gem.name} ${gem.description}`)) {
    score += 10;
  }
  if (["mcp-governance-servers", "a2a-agent-cards", "agent-adapters", "agent-marketplaces", "strategic-signals"].includes(gem.category)) {
    score += isPlugPlayRelevant(gem) ? 16 : -12;
    if (isOfficialStrategicSource(gem)) score += 12;
    if (isStrategicNoise(gem)) score -= 10;
    if (gem.source === "github") score += 10;
    if (gem.source === "npm") score += 8;
    if (gem.source === "arxiv") score += 6;
    if (gem.source === "hackernews") score -= 6;
    if (gem.source === "exa" && !isOfficialStrategicSource(gem)) score -= 4;
  }
  // Agent-scaling and research-gems categories get base boost
  if (["agent-scaling", "research-gems"].includes(gem.category)) score += 8;

  // Papers Without Code bonus (v6.0 / GH-051)
  // High value: ideas nobody has implemented yet
  if (gem.category === 'papers-without-code' || gem.name.startsWith('[NO CODE]')) {
    score += 20;
  }

  // GH-060: Structure validation bonus (set by validateGemStructure enrichment pass)
  if (gem.structureBonus) score += gem.structureBonus;

  // GH-056: Abstract triage score bonus (set by runPaperPipeline LLM pass)
  if (gem.abstractScore && gem.abstractScore >= 70) score += Math.round((gem.abstractScore - 69) / 3);

  return Math.max(0, Math.round(score));
}

function buildXDraft(gem: GemResult): string {
  const summary = gem.description.replace(/\s+/g, " ").trim();
  const draft = `Radar do dia no X: ${gem.name} trouxe um sinal útil para o EGOS — ${summary} Vale avaliar, documentar e testar no nosso stack.`;
  return draft.length <= 280 ? draft : `${draft.slice(0, 279).trimEnd()}…`;
}

// ── SSOT Lego Atomization ───────────────────────────────────────────────

async function atomizeTopGems(gems: GemResult[], date: string) {
  // Only atomize highly relevant code gems from GitHub sources
  const candidates = gems
    .filter(g => ["github", "github-code"].includes(g.source) && (classifyGem(g) === "⚡ Implement" || classifyGem(g) === "📋 Create Task"))
    .filter(g => !hasMajorityCJK(g.description)) // Skip CJK-dominant repos
    .sort((a, b) => scoreGem(b) - scoreGem(a))
    .slice(0, 3); // Capped at top 3 to avoid high cost

  if (candidates.length === 0) {
    console.log("   No suitable candidates for atomization in this run.");
    return;
  }

  const assetsDir = join(REPORTS_DIR, "assets");
  if (!existsSync(assetsDir)) mkdirSync(assetsDir, { recursive: true });

  for (const gem of candidates) {
    console.log(`   ⚙️ Atomizing [${gem.name}]...`);
    let codeContent = "";
    
    // Fetch raw content
    if (gem.source === "github-code" && gem.rawUrl) {
      try {
        const res = await fetch(gem.rawUrl);
        if (res.ok) codeContent = await res.text();
      } catch (e) {
        console.warn(`     Failed to fetch raw code for ${gem.name}`);
      }
    } else if (gem.source === "github") {
      // Try to fetch README as the "asset" for standard repos
      const readmeUrl = gem.url.replace("github.com", "raw.githubusercontent.com") + "/master/README.md";
      const readmeUrl2 = gem.url.replace("github.com", "raw.githubusercontent.com") + "/main/README.md";
      try {
        let res = await fetch(readmeUrl);
        if (!res.ok) res = await fetch(readmeUrl2);
        if (res.ok) codeContent = await res.text();
      } catch (e) {}
    }

    if (!codeContent) {
      console.log(`     No extractable text/code found. Skipping.`);
      continue;
    }

    // Limit context length
    const contextStr = codeContent.slice(0, 16000); // approx 4000 tokens

    const prompt = `You are EGOS Atomizer, an expert system designed to extract single "SSOT Lego Blocks" from raw code or READMEs to be reused in our architecture.
Source: ${gem.name} (${gem.url})
Content snippet:
${contextStr}

Your task:
Identify the MOST VALUABLE reusable block in this content. It could be an Architectural pattern, a UI Component, a System Prompt, a Core Logic function, or an Integration Pattern.
Format the output EXACTLY as follows (no introduction, just the markdown):

---
type: [The block type, e.g., "UI Component", "Integration Pattern", "Core Logic", "AI Prompt"]
source: ${gem.url}
date: ${date}
---

# SSOT Block: [Short descriptive name]

## Value Proposition
[1-2 sentences explaining why this is useful]

## Code or Definition
\`\`\`
[The extracted code, prompt, or architectural summary]
\`\`\`

## Dependencies
[List any specific dependencies noticed, or "None"]
`;

    try {
      const res = await callAI({
        userMessage: prompt,
        channelId: "gem-hunter",
        userId: "gem-hunter",
        userName: "GemHunter",
        platform: "discord",
        openrouterApiKey: OPENROUTER_API_KEY
      });

      const extractedMd = res.reply.trim();
      const blockTypeMatch = extractedMd.match(/type:\s*\[?"?([^\]"\n]+)\]?"?/i);
      gem.legoBlockType = blockTypeMatch ? blockTypeMatch[1] : "Unknown Block";

      const safeName = gem.name.replace(/[^a-z0-9]/gi, "-").toLowerCase();
      const assetFilename = `ssot-${safeName}-${Date.now()}.md`;
      const assetPath = join(assetsDir, assetFilename);
      
      writeFileSync(assetPath, extractedMd);
      gem.ssotAssetPath = `assets/${assetFilename}`;
      console.log(`     ✅ Extracted: ${gem.legoBlockType} -> ${gem.ssotAssetPath}`);
    } catch (e) {
      console.error(`     ❌ Atomization failed:`, e);
    }
  }
}

function saveLatestRun(manifest: LatestRunManifest): void {
  writeFileSync(LATEST_RUN_PATH, JSON.stringify(manifest, null, 2));
  console.log(`🧭 Latest run manifest saved: ${LATEST_RUN_PATH}`);
}

function generateReport(results: GemResult[], date: string, aiSynthesis?: string): string {
  let md = `# Gem Hunter Report — ${date}\n\n`;
  md += `> Auto-generated by AGENT-027 Gem Hunter v${GEM_HUNTER_VERSION}\n`;
  md += `> Sources: GitHub + HuggingFace Models + HF Spaces + Exa + arXiv + HackerNews + NPM + Zenodo + X API + X Public + Reddit + StackOverflow + ProductHunt + GitHub Code\n`;
  md += `> Total gems: ${results.length}\n\n---\n\n`;

  if (aiSynthesis) {
    md += `## 🧠 AI Executive Synthesis\n\n`;
    md += `${aiSynthesis}\n\n---\n\n`;
  }

  const atomizedGems = results.filter(g => g.ssotAssetPath);
  if (atomizedGems.length > 0) {
    md += `## 🧩 SSOT Lego Assets (Atomized)\n\n`;
    md += `> The following repository components were extracted into isolated Lego blocks for direct consumption.\n\n`;
    md += `| Asset Name | Type | Source | Saved To |\n`;
    md += `|------------|------|--------|----------|\n`;
    for (const g of atomizedGems) {
      md += `| [${g.name}](${g.url}) | **${g.legoBlockType}** | ${g.source} | [${g.ssotAssetPath}](./${g.ssotAssetPath}) |\n`;
    }
    md += `\n---\n\n`;
  }

  const shortlist = [...results]
    .filter((r) => r.category === "web-extraction")
    .sort((a, b) => scoreGem(b) - scoreGem(a))
    .slice(0, 5);
  if (shortlist.length) {
    md += `## Web Extraction Shortlist\n\n`;
    md += `| # | Name | Source | Score | Decision | Description |\n`;
    md += `|---|------|--------|-------|----------|-------------|\n`;
    for (let i = 0; i < shortlist.length; i++) {
      const r = shortlist[i];
      md += `| ${i + 1} | [${r.name}](${r.url}) | ${r.source} | ${scoreGem(r)} | ${classifyGem(r)} | ${r.description.replace(/\|/g, "\\|").replace(/\n/g, " ").slice(0, 120)} |\n`;
    }
    md += `\n---\n\n`;
  }

  const xDraftSeeds = [...results]
    .filter((r) => r.source === "x-api")
    .sort((a, b) => scoreGem(b) - scoreGem(a))
    .slice(0, 3);
  if (xDraftSeeds.length) {
    md += `## X Draft Posts\n\n`;
    for (let i = 0; i < xDraftSeeds.length; i++) {
      md += `${i + 1}. ${buildXDraft(xDraftSeeds[i])}\n`;
      md += `   Source: ${xDraftSeeds[i].url}\n`;
    }
    md += `\n---\n\n`;
  }

  const categories = [...new Set(results.map((r) => r.category))];
  for (const cat of categories) {
    const catResults = results.filter((r) => r.category === cat);
    const topic = DEFAULT_QUERIES.find((q) => q.category === cat)?.topic || cat;
    md += `## ${topic}\n\n`;
    md += `| # | Name | Source | Stars | Score | Decision | Description |\n`;
    md += `|---|------|--------|-------|-------|----------|-------------|\n`;
    const sorted = catResults.sort((a, b) => scoreGem(b) - scoreGem(a));
    for (let i = 0; i < sorted.length; i++) {
      const r = sorted[i];
      const stars = r.stars != null ? String(r.stars) : r.downloads != null ? `${r.downloads} dl` : "—";
      const action = classifyGem(r);
      md += `| ${i + 1} | [${r.name}](${r.url}) | ${r.source} | ${stars} | ${scoreGem(r)} | ${action} | ${r.description.replace(/\|/g, "\\|").replace(/\n/g, " ").slice(0, 120)} |\n`;
    }
    md += `\n---\n\n`;
  }

  // Evolution Insights section
  const evolution = extractEvolutionInsights(results);
  md += `## 🧬 Evolution Insights (Self-Improving Keywords)\n\n`;
  md += `> These keywords were extracted from today's results to improve future searches.\n`;
  md += `> They are saved to \`docs/gem-hunter/next-queries.json\` for the next run.\n\n`;
  md += `### Trending Terms Detected\n\n`;
  for (const [term, count] of evolution.trendingTerms.slice(0, 20)) {
    md += `- **${term}** (appeared ${count}x)\n`;
  }
  md += `\n### Suggested New Search Topics\n\n`;
  for (const suggestion of evolution.suggestedQueries) {
    md += `- 🎯 **${suggestion.topic}**: ${suggestion.keywords.join(", ")}\n`;
  }
  md += `\n### Action Summary\n\n`;
  md += `| Action | Count |\n|--------|-------|\n`;
  const actionCounts = new Map<string, number>();
  for (const r of results) {
    const a = classifyGem(r);
    actionCounts.set(a, (actionCounts.get(a) || 0) + 1);
  }
  for (const [action, count] of actionCounts) {
    md += `| ${action} | ${count} |\n`;
  }
  md += `\n---\n\n`;
  md += `> 🔄 **Next run will automatically incorporate the evolved keywords above.**\n`;
  md += `> 🎯 **Prioritize \`⚡ Implement\` and \`📋 Create Task\` items first, then document or discard the rest.**\n`;

  return md;
}

// ── Post-Discovery Pipeline ─────────────────────────────────────────────

function classifyGem(gem: GemResult): string {
  const score = scoreGem(gem);
  if (gem.category === "web-extraction" && score >= 70 && ["github", "npm"].includes(gem.source)) {
    return "⚡ Implement";
  }
  if (score >= 60) {
    return "📋 Create Task";
  }
  if (score >= 45) {
    return "📝 Document";
  }
  if (score >= 30) {
    return "🔍 Evaluate";
  }
  return "🗑️ Discard";
}

// ── Self-Evolution Engine ─────────────────────────────────────────────

interface EvolutionInsights {
  trendingTerms: [string, number][];
  suggestedQueries: { topic: string; keywords: string[] }[];
}

function extractEvolutionInsights(results: GemResult[]): EvolutionInsights {
  // ANTI-POISONING: Only extract keywords from quality gems (score >= 40)
  // This prevents spam/gaming repos from contaminating future search queries
  const qualityGems = results.filter(r => scoreGem(r) >= 40 && !hasMajorityCJK(`${r.name} ${r.description}`));
  const wordFreq = new Map<string, number>();
  const stopWords = new Set([
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "for", "and", "or", "but", "in", "on", "at", "to", "of", "by",
    "with", "from", "as", "it", "its", "that", "this", "not", "no",
    "can", "will", "has", "have", "had", "do", "does", "did",
    "open", "source", "github", "com", "org", "io", "ai", "based",
    "using", "built", "use", "new", "your", "how", "what", "why",
    "all", "any", "each", "more", "most", "one", "two", "first",
    "via", "about", "than", "into", "over", "just", "also",
    // Anti-spam blocklist
    "anti", "propaganda", "backup", "chinese", "government", "political",
  ]);

  for (const r of qualityGems) {
    const text = `${r.name} ${r.description}`.toLowerCase();
    // Extract 2-3 word phrases (bigrams/trigrams are more valuable)
    const words = text.split(/[^a-z0-9-]+/).filter(w => w.length > 3 && !stopWords.has(w));
    for (const w of words) {
      wordFreq.set(w, (wordFreq.get(w) || 0) + 1);
    }
  }

  // Sort by frequency, filter out words already in our DEFAULT_QUERIES
  const existingKeywords = new Set(
    DEFAULT_QUERIES.flatMap(q => q.keywords.join(" ").toLowerCase().split(/\s+/))
  );
  const trendingTerms = [...wordFreq.entries()]
    .filter(([word, count]) => count >= 3 && !existingKeywords.has(word))
    .sort((a, b) => b[1] - a[1]);

  // Generate suggested queries from top trending terms
  const topTerms = trendingTerms.slice(0, 15).map(([t]) => t);
  const suggestedQueries: { topic: string; keywords: string[] }[] = [];

  // Cluster related terms into query suggestions
  if (topTerms.length >= 3) {
    suggestedQueries.push({
      topic: `Emerging: ${topTerms.slice(0, 3).join(" + ")}`,
      keywords: [
        topTerms.slice(0, 3).join(" "),
        topTerms.slice(1, 4).join(" "),
        topTerms.slice(2, 5).join(" "),
      ],
    });
  }
  if (topTerms.length >= 6) {
    suggestedQueries.push({
      topic: `Next-Gen: ${topTerms.slice(3, 6).join(" + ")}`,
      keywords: [
        topTerms.slice(3, 6).join(" "),
        topTerms.slice(5, 8).join(" "),
      ],
    });
  }

  return { trendingTerms, suggestedQueries };
}

function saveEvolutionState(results: GemResult[]): void {
  const evolution = extractEvolutionInsights(results);
  const evolutionPath = join(REPORTS_DIR, "next-queries.json");
  const state = {
    generatedAt: new Date().toISOString(),
    trendingTerms: evolution.trendingTerms.slice(0, 30),
    suggestedQueries: evolution.suggestedQueries,
    totalGemsAnalyzed: results.length,
    actionBreakdown: {} as Record<string, number>,
  };
  for (const r of results) {
    const action = classifyGem(r);
    state.actionBreakdown[action] = (state.actionBreakdown[action] || 0) + 1;
  }
  writeFileSync(evolutionPath, JSON.stringify(state, null, 2));
  console.log(`\n🧬 Evolution state saved: ${evolutionPath}`);
}

// ── GH-060: Structural validation ──────────────────────────────────────────
/** Checks GitHub repo file tree for quality signals: README, tests, benchmarks, docs */
async function validateGemStructure(gem: GemResult): Promise<void> {
  if (!["github", "github-code"].includes(gem.source)) return;
  const match = gem.url.match(/github\.com\/([^/]+\/[^/]+)/);
  if (!match) return;
  const repo = match[1];
  try {
    const headers: Record<string, string> = { "User-Agent": "egos-gem-hunter/6.0" };
    if (GITHUB_TOKEN) headers["Authorization"] = `token ${GITHUB_TOKEN}`;
    const res = await fetch(`https://api.github.com/repos/${repo}/contents/`, { headers });
    if (!res.ok) return;
    const files = (await res.json()) as Array<{ name: string; type: string }>;
    const names = files.map(f => f.name.toLowerCase());
    let bonus = 0;
    if (names.some(n => n.startsWith("readme"))) bonus += 5;
    if (names.some(n => ["test", "tests", "__tests__", "spec", "specs"].includes(n))) bonus += 8;
    if (names.some(n => ["benchmark", "benchmarks", "bench"].includes(n))) bonus += 7;
    if (names.some(n => ["docs", "doc", "documentation"].includes(n))) bonus += 5;
    gem.structureBonus = bonus;
  } catch { /* silent — best-effort */ }
}

// ── GH-057: Context awareness ───────────────────────────────────────────────
/** Reads git log + TASKS.md to extract context keywords for query injection */
function loadContextSignals(): string[] {
  const keywords: string[] = [];
  try {
    const { execSync } = require("child_process");
    const log = execSync("git log --oneline -20", { cwd: ROOT, encoding: "utf-8" }) as string;
    const logWords = log.split(/\s+/).filter((w: string) => w.length > 5 && /^[a-z]/i.test(w));
    keywords.push(...logWords.slice(0, 10));
  } catch { /* git not available */ }
  try {
    const tasks = readFileSync(join(ROOT, "TASKS.md"), "utf-8");
    const inProgress = tasks.match(/\[ \] (GH|EAGLE|EGOS)-[^\n]+/g) || [];
    const taskWords = inProgress.join(" ").split(/\s+/)
      .filter(w => w.length > 4 && /^[a-zA-Z]/.test(w) && !["with","from","that","this","have","will"].includes(w.toLowerCase()));
    keywords.push(...taskWords.slice(0, 20));
  } catch { /* TASKS.md unreadable */ }
  return [...new Set(keywords)].slice(0, 15);
}

// ── GH-056: Multi-stage paper pipeline ─────────────────────────────────────
/** Stages 2-4: LLM triage → deep read → scaffold for papers-without-code gems */
async function runPaperPipeline(papers: GemResult[], date: string): Promise<void> {
  if (papers.length === 0) return;
  console.log(`\n📄 Paper Pipeline: ${papers.length} paper(s) — LLM triage + scaffold...`);

  // Stage 2: LLM abstract triage — score 0-100 for EGOS relevance
  for (const paper of papers.slice(0, 8)) {
    try {
      const prompt = `Score this research paper abstract for relevance to an EGOS multi-agent TypeScript platform that does: orchestration, governance-as-code, crypto gem hunting, and Brazilian compliance. Reply ONLY with a JSON object: {"score": 0-100, "reason": "one sentence"}.\n\nTitle: ${paper.name}\nAbstract: ${paper.description.slice(0, 400)}`;
      const res = await callAI({ userMessage: prompt, channelId: "gem-hunter", userId: "gem-hunter", userName: "GemHunter", platform: "discord", openrouterApiKey: OPENROUTER_API_KEY });
      const jsonMatch = res.reply.match(/\{[^}]+\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        paper.abstractScore = Number(parsed.score) || 0;
        console.log(`   S2 ${paper.abstractScore}/100 — ${paper.name.slice(0, 60)}`);
      }
    } catch { /* skip if LLM unavailable */ }
  }

  // Stage 4: Scaffold top-3 papers with abstractScore >= 60
  const scaffoldCandidates = papers.filter(p => (p.abstractScore || 0) >= 60).slice(0, 3);
  if (scaffoldCandidates.length === 0) return;

  const scaffoldsDir = join(REPORTS_DIR, "scaffolds");
  if (!existsSync(scaffoldsDir)) mkdirSync(scaffoldsDir, { recursive: true });

  for (const paper of scaffoldCandidates) {
    const arxivId = paper.description.match(/arxiv:([^\]]+)/)?.[1] || "";
    const safeName = paper.name.replace(/\[NO CODE\]\s*/i, "").replace(/[^a-z0-9]/gi, "-").toLowerCase().slice(0, 50);
    const tsPath = join(scaffoldsDir, `${safeName}-${date}.ts`);
    const mdPath = join(scaffoldsDir, `${safeName}-${date}.md`);
    if (existsSync(tsPath)) continue; // Skip if already scaffolded

    try {
      const prompt = `Based on this research paper, generate a TypeScript skeleton with 1-2 exported functions + types that could implement the core idea. Keep it under 50 lines with TODO comments.\n\nTitle: ${paper.name}\nAbstract: ${paper.description.slice(0, 400)}`;
      const res = await callAI({ userMessage: prompt, channelId: "gem-hunter", userId: "gem-hunter", userName: "GemHunter", platform: "discord", openrouterApiKey: OPENROUTER_API_KEY });
      const tsCode = res.reply.match(/```(?:typescript|ts)?\n([\s\S]+?)```/)?.[1] || res.reply;
      writeFileSync(tsPath, `// GH-056 Auto-scaffold — ${paper.name}\n// Source: ${paper.url}\n// arXiv: ${arxivId}\n// Score: ${paper.abstractScore}/100\n\n${tsCode}`);
      writeFileSync(mdPath, `# ${paper.name}\n\n**Source:** ${paper.url}\n**arXiv:** ${arxivId}\n**EGOS Score:** ${paper.abstractScore}/100\n\n## Abstract\n${paper.description.slice(0, 400)}\n\n## Scaffold\nSee \`${safeName}-${date}.ts\`\n\n## Next Steps\n- [ ] Review scaffold\n- [ ] Implement core algorithm\n- [ ] Add to TASKS.md if approved\n`);
      paper.ssotAssetPath = `scaffolds/${safeName}-${date}.md`;
      console.log(`   S4 Scaffolded → ${safeName}-${date}.ts`);
    } catch { /* scaffold failed */ }
  }
}

// ── GH-055: Telegram alert for hot gems ────────────────────────────────────
async function sendGemTelegramAlert(hotGems: { gem: GemResult; score: number }[]): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("[GemAlert] Telegram skipped — TELEGRAM_BOT_TOKEN / TELEGRAM_ADMIN_CHAT_ID not set");
    return;
  }
  const lines = hotGems.map(({ gem, score }) =>
    `• *${gem.name}* (${score}/100)\n  ${gem.description.slice(0, 80)}…\n  ${gem.url}`
  );
  const message = `🔥 *Gem Hunter v${GEM_HUNTER_VERSION} — ${hotGems.length} Hot Gem(s)*\n\n${lines.join("\n\n")}`;
  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: TELEGRAM_CHAT_ID, text: message, parse_mode: "Markdown" }),
    });
    console.log(`[GemAlert] Telegram alert sent for ${hotGems.length} gem(s)`);
  } catch (err) {
    console.error("[GemAlert] Failed to send Telegram alert:", err);
  }
}

main().catch(console.error);
