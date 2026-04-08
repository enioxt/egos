#!/usr/bin/env bun
// ♻️ X Evergreen Recycler — Smart Content Reposting
//
// Recompartilha automaticamente posts de melhor performance
// para novos seguidores, com espaçamento inteligente e variações.
//
// Usage:
//   bun scripts/x-evergreen-recycler.ts              # run analysis & queue
//   bun scripts/x-evergreen-recycler.ts --dry-run    # simulate only
//   bun scripts/x-evergreen-recycler.ts --list-top   # list top posts

import { writeFileSync, readFileSync, existsSync } from "fs";

const DRY_RUN = process.argv.includes("--dry-run") || !process.env.X_ACCESS_TOKEN;
const LIST_TOP = process.argv.includes("--list-top");

const STATE_FILE = "/tmp/x-recycler-state.json";
const MIN_ENGAGEMENT_THRESHOLD = 50;
const TOP_PERCENTILE = 0.2;
const MIN_DAYS_BETWEEN_REPOSTS = 7;
const MAX_REPOSTS_PER_DAY = 2;

type PostMetrics = {
  id: string;
  text: string;
  createdAt: string;
  likes: number;
  retweets: number;
  replies: number;
  impressions: number;
  engagementScore: number;
};

type RepostRecord = {
  originalId: string;
  repostedAt: string;
  variationUsed: number;
};

type RecyclerState = {
  posts: PostMetrics[];
  repostHistory: RepostRecord[];
  lastRun: string;
  dailyRepostCount: number;
  lastRepostDate: string;
};

function loadState(): RecyclerState {
  if (!existsSync(STATE_FILE)) {
    return { posts: [], repostHistory: [], lastRun: "", dailyRepostCount: 0, lastRepostDate: "" };
  }
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf-8"));
  } catch {
    return { posts: [], repostHistory: [], lastRun: "", dailyRepostCount: 0, lastRepostDate: "" };
  }
}

function saveState(state: RecyclerState) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function calculateEngagement(post: PostMetrics): number {
  return post.likes * 1 + post.retweets * 2 + post.replies * 3 + post.impressions * 0.01;
}

function generateMockPosts(): PostMetrics[] {
  const templates = [
    "Como automatizar X.com sem pagar $99/mo",
    "GovTech: 7 licitações abertas",
    "O segredo dos agentes de IA",
    "Por que eu parei de usar TweetHunter",
    "LGPD + IA: como processar dados",
  ];
  const posts: PostMetrics[] = [];
  for (let i = 0; i < 30; i++) {
    const baseEngagement = Math.random() * 100;
    const multiplier = i < 6 ? 3 : 1;
    posts.push({
      id: `mock-${i}`,
      text: templates[i % templates.length],
      createdAt: new Date(Date.now() - i * 86400000).toISOString(),
      likes: Math.floor(baseEngagement * multiplier * 3),
      retweets: Math.floor(baseEngagement * multiplier),
      replies: Math.floor(baseEngagement * multiplier * 0.5),
      impressions: Math.floor(baseEngagement * multiplier * 30),
      engagementScore: 0,
    });
  }
  for (const post of posts) {
    post.engagementScore = calculateEngagement(post);
  }
  return posts.sort((a, b) => b.engagementScore - a.engagementScore);
}

function identifyEvergreenPosts(posts: PostMetrics[]): PostMetrics[] {
  const qualified = posts.filter(p => p.engagementScore >= MIN_ENGAGEMENT_THRESHOLD);
  if (qualified.length === 0) return [];
  const sorted = [...qualified].sort((a, b) => b.engagementScore - a.engagementScore);
  const topCount = Math.max(1, Math.floor(sorted.length * TOP_PERCENTILE));
  return sorted.slice(0, topCount);
}

function canRepost(post: PostMetrics, history: RepostRecord[]): boolean {
  const lastRepost = history
    .filter(h => h.originalId === post.id)
    .sort((a, b) => new Date(b.repostedAt).getTime() - new Date(a.repostedAt).getTime())[0];
  if (!lastRepost) return true;
  const daysSinceLastRepost = (Date.now() - new Date(lastRepost.repostedAt).getTime()) / (1000 * 60 * 60 * 24);
  return daysSinceLastRepost >= MIN_DAYS_BETWEEN_REPOSTS;
}

function listTopPosts(posts: PostMetrics[], history: RepostRecord[]) {
  const evergreen = identifyEvergreenPosts(posts);
  console.log("\n🏆 TOP POSTS (Evergreen Candidates)");
  console.log("─".repeat(70));
  for (let i = 0; i < Math.min(10, evergreen.length); i++) {
    const post = evergreen[i];
    const canDo = canRepost(post, history);
    console.log(`${i + 1}. ${post.text.substring(0, 50)}...`);
    console.log(`   Engajamento: ${Math.round(post.engagementScore)} | Status: ${canDo ? "✅" : "⛔"}`);
  }
}

async function main() {
  console.log("♻️ X Evergreen Recycler\n");
  const state = loadState();
  const today = new Date().toISOString().split("T")[0];
  
  if (state.lastRepostDate !== today) {
    state.dailyRepostCount = 0;
    state.lastRepostDate = today;
  }
  
  // Load mock data
  state.posts = generateMockPosts();
  
  if (LIST_TOP) {
    listTopPosts(state.posts, state.repostHistory);
    saveState(state);
    return;
  }
  
  const evergreen = identifyEvergreenPosts(state.posts);
  console.log(`🌱 Evergreen: ${evergreen.length} posts`);
  
  const available = evergreen.filter(p => canRepost(p, state.repostHistory));
  console.log(`✅ Disponíveis: ${available.length}`);
  console.log(`📊 Reposts hoje: ${state.dailyRepostCount}/${MAX_REPOSTS_PER_DAY}`);
  
  if (DRY_RUN && available.length > 0) {
    console.log(`\n[DRY-RUN] Próximo candidato: ${available[0].text.substring(0, 50)}...`);
  }
  
  saveState(state);
}

main().catch(console.error);
