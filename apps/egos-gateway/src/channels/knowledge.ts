/**
 * EGOS Gateway — Knowledge Channel
 *
 * REST API for the EGOS Knowledge System (wiki pages + learnings).
 * Backed by Supabase tables: egos_wiki_pages, egos_learnings, egos_wiki_changelog.
 *
 * Endpoints:
 *   GET  /pages              — list all wiki pages (paginated)
 *   GET  /pages/:slug        — get a single page by slug
 *   GET  /index              — wiki index grouped by category
 *   GET  /search?q=term      — full-text search across pages
 *   GET  /learnings          — list learnings (filterable)
 *   POST /learnings          — record a new learning
 *   GET  /stats              — knowledge base stats
 */

import { Hono } from "hono";

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

// ── Supabase helper ───────────────────────────────────────────────────

async function sbFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
      ...(init?.headers || {}),
    },
  });
}

// ── Routes ────────────────────────────────────────────────────────────

export const knowledge = new Hono();

// List pages (paginated)
knowledge.get("/pages", async (c) => {
  const limit = Math.min(Number(c.req.query("limit") || 50), 100);
  const offset = Number(c.req.query("offset") || 0);
  const category = c.req.query("category");

  let params = `select=slug,title,category,tags,quality_score,updated_at&order=updated_at.desc&limit=${limit}&offset=${offset}`;
  if (category) params += `&category=eq.${category}`;

  const res = await sbFetch(`egos_wiki_pages?${params}`);
  if (!res.ok) return c.json({ error: "Failed to fetch pages" }, 500);

  const pages = await res.json();
  return c.json({ pages, count: (pages as unknown[]).length, limit, offset });
});

// Get single page
knowledge.get("/pages/:slug", async (c) => {
  const slug = c.req.param("slug");
  const res = await sbFetch(`egos_wiki_pages?slug=eq.${slug}&limit=1`);
  if (!res.ok) return c.json({ error: "Failed to fetch page" }, 500);

  const pages = (await res.json()) as unknown[];
  if (pages.length === 0) return c.json({ error: "Page not found" }, 404);

  return c.json(pages[0]);
});

// Wiki index (grouped by category)
knowledge.get("/index", async (c) => {
  const res = await sbFetch(
    "egos_wiki_pages?select=slug,title,category,tags,quality_score,updated_at&order=category,title"
  );
  if (!res.ok) return c.json({ error: "Failed to fetch index" }, 500);

  const pages = (await res.json()) as Array<{
    slug: string;
    title: string;
    category: string;
    tags: string[];
    quality_score: number;
    updated_at: string;
  }>;

  const grouped: Record<string, typeof pages> = {};
  for (const p of pages) {
    if (!grouped[p.category]) grouped[p.category] = [];
    grouped[p.category].push(p);
  }

  const avgQuality = pages.length
    ? Math.round(pages.reduce((s, p) => s + p.quality_score, 0) / pages.length)
    : 0;

  return c.json({
    total_pages: pages.length,
    avg_quality: avgQuality,
    categories: grouped,
    generated_at: new Date().toISOString(),
  });
});

// Full-text search
knowledge.get("/search", async (c) => {
  const q = c.req.query("q");
  if (!q || q.length < 2) return c.json({ error: "Query too short (min 2 chars)" }, 400);

  // Use ilike for simple text search (Supabase PostgREST)
  const encoded = encodeURIComponent(`%${q}%`);
  const res = await sbFetch(
    `egos_wiki_pages?select=slug,title,category,tags,quality_score,updated_at&or=(title.ilike.${encoded},content.ilike.${encoded})&order=quality_score.desc&limit=20`
  );
  if (!res.ok) return c.json({ error: "Search failed" }, 500);

  const results = await res.json();
  return c.json({ query: q, results, count: (results as unknown[]).length });
});

// List learnings
knowledge.get("/learnings", async (c) => {
  const domain = c.req.query("domain");
  const outcome = c.req.query("outcome");
  const limit = Math.min(Number(c.req.query("limit") || 30), 100);

  let params = `select=*&order=created_at.desc&limit=${limit}`;
  if (domain) params += `&domain=eq.${domain}`;
  if (outcome) params += `&outcome=eq.${outcome}`;

  const res = await sbFetch(`egos_learnings?${params}`);
  if (!res.ok) return c.json({ error: "Failed to fetch learnings" }, 500);

  const learnings = await res.json();
  return c.json({ learnings, count: (learnings as unknown[]).length });
});

// Record a learning
knowledge.post("/learnings", async (c) => {
  const body = await c.req.json();

  const required = ["domain", "outcome", "summary"];
  for (const field of required) {
    if (!body[field]) return c.json({ error: `Missing required field: ${field}` }, 400);
  }

  const res = await sbFetch("egos_learnings", {
    method: "POST",
    body: JSON.stringify({
      session_id: body.session_id || null,
      domain: body.domain,
      outcome: body.outcome,
      summary: body.summary,
      detail: body.detail || null,
      pattern: body.pattern || null,
      evidence: body.evidence || [],
      impact: body.impact || "low",
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    return c.json({ error: "Failed to record learning", detail: err }, 500);
  }

  const result = await res.json();
  return c.json({ ok: true, learning: (result as unknown[])[0] }, 201);
});

// Knowledge base stats
knowledge.get("/stats", async (c) => {
  // Page count + category breakdown
  const pagesRes = await sbFetch(
    "egos_wiki_pages?select=category,quality_score"
  );
  const learningsRes = await sbFetch(
    "egos_learnings?select=domain,outcome"
  );

  if (!pagesRes.ok || !learningsRes.ok) {
    return c.json({ error: "Failed to fetch stats" }, 500);
  }

  const pages = (await pagesRes.json()) as Array<{ category: string; quality_score: number }>;
  const learnings = (await learningsRes.json()) as Array<{ domain: string; outcome: string }>;

  const categoryCount: Record<string, number> = {};
  let totalQuality = 0;
  for (const p of pages) {
    categoryCount[p.category] = (categoryCount[p.category] || 0) + 1;
    totalQuality += p.quality_score;
  }

  const domainCount: Record<string, number> = {};
  const outcomeCount: Record<string, number> = {};
  for (const l of learnings) {
    domainCount[l.domain] = (domainCount[l.domain] || 0) + 1;
    outcomeCount[l.outcome] = (outcomeCount[l.outcome] || 0) + 1;
  }

  return c.json({
    pages: {
      total: pages.length,
      avg_quality: pages.length ? Math.round(totalQuality / pages.length) : 0,
      by_category: categoryCount,
    },
    learnings: {
      total: learnings.length,
      by_domain: domainCount,
      by_outcome: outcomeCount,
    },
    generated_at: new Date().toISOString(),
  });
});
