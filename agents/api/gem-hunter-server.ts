/**
 * GH-058 — Gem Hunter Standalone API
 * Phase 1 of standalone product roadmap (API → Bot → Dashboard → NPM)
 *
 * Endpoints:
 *   GET  /health              — liveness check
 *   GET  /v1/findings         — latest run summary + top gems
 *   GET  /v1/papers           — scaffolded papers (docs/gem-hunter/scaffolds/)
 *   GET  /v1/signals          — signals.json (world-model feed)
 *   POST /v1/hunt             — trigger gem hunt (async, returns job status)
 *   GET  /v1/kols             — kol-list.json if available
 *
 * Auth: Bearer token from env GEM_HUNTER_API_KEY (open if not set — dev mode)
 * Port: 3097 (env GEM_HUNTER_API_PORT)
 */

import { existsSync, readFileSync, readdirSync } from "fs";
import { join } from "path";
import { spawn } from "child_process";

const PORT = Number(process.env.GEM_HUNTER_API_PORT ?? 3097);
const API_KEY = process.env.GEM_HUNTER_API_KEY ?? "";
const ROOT = join(import.meta.dir, "../..");
const REPORTS_DIR = join(ROOT, "docs/gem-hunter");
const VERSION = "1.0.0";

// Active hunt jobs: jobId → { status, startedAt, pid? }
const jobs = new Map<string, { status: "running" | "done" | "error"; startedAt: string; pid?: number }>();

// ── Auth ──────────────────────────────────────────────────────────────────────
function isAuthorized(req: Request): boolean {
  if (!API_KEY) return true; // open in dev mode
  const auth = req.headers.get("Authorization") ?? "";
  return auth === `Bearer ${API_KEY}`;
}

// ── CORS headers ──────────────────────────────────────────────────────────────
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

function unauthorized(): Response {
  return json({ error: "Unauthorized — provide Bearer token" }, 401);
}

// ── Route handlers ─────────────────────────────────────────────────────────────
function handleHealth(): Response {
  return json({
    status: "ok",
    version: VERSION,
    reportsDir: existsSync(REPORTS_DIR),
    activeJobs: jobs.size,
    ts: new Date().toISOString(),
  });
}

function handleFindings(): Response {
  const latestPath = join(REPORTS_DIR, "latest-run.json");
  if (!existsSync(latestPath)) return json({ error: "No runs yet — POST /v1/hunt first" }, 404);
  const latest = JSON.parse(readFileSync(latestPath, "utf-8"));

  // Also grab top signals if available
  const signalsPath = join(REPORTS_DIR, "signals.json");
  const signals = existsSync(signalsPath)
    ? JSON.parse(readFileSync(signalsPath, "utf-8")).signals?.slice(0, 10) ?? []
    : [];

  return json({ latest, topSignals: signals });
}

function handlePapers(): Response {
  const scaffoldsDir = join(REPORTS_DIR, "scaffolds");
  if (!existsSync(scaffoldsDir)) return json({ papers: [] });
  const files = readdirSync(scaffoldsDir)
    .filter(f => f.endsWith(".md"))
    .map(f => {
      const content = readFileSync(join(scaffoldsDir, f), "utf-8");
      const title = content.match(/^# (.+)/m)?.[1] ?? f;
      const score = content.match(/Score:\s*(\d+)\/100/)?.[1];
      return { file: f, title, score: score ? Number(score) : null };
    })
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
  return json({ count: files.length, papers: files });
}

function handleSignals(): Response {
  const signalsPath = join(REPORTS_DIR, "signals.json");
  if (!existsSync(signalsPath)) return json({ version: "1.0.0", signals: [] });
  return json(JSON.parse(readFileSync(signalsPath, "utf-8")));
}

function handleKOLs(): Response {
  const kolPath = join(REPORTS_DIR, "kol-list.json");
  if (!existsSync(kolPath)) return json({ error: "KOL list not generated yet — run: bun scripts/kol-discovery.ts" }, 404);
  return json(JSON.parse(readFileSync(kolPath, "utf-8")));
}

async function handleHunt(req: Request): Promise<Response> {
  const body = await req.json().catch(() => ({})) as Record<string, unknown>;
  const track = typeof body.track === "string" ? body.track : "";
  const quick = body.quick === true;

  const jobId = `hunt-${Date.now()}`;
  jobs.set(jobId, { status: "running", startedAt: new Date().toISOString() });

  const args = ["agent:run", "gem-hunter", "--exec"];
  if (quick) args.push("--quick");
  if (track) args.push(`--track=${track}`);

  const child = spawn("bun", args, { cwd: ROOT, detached: true, stdio: "ignore" });
  jobs.get(jobId)!.pid = child.pid;
  child.on("close", (code) => {
    const job = jobs.get(jobId);
    if (job) job.status = code === 0 ? "done" : "error";
  });
  child.unref();

  return json({ jobId, status: "running", args, startedAt: jobs.get(jobId)!.startedAt }, 202);
}

// ── Server ─────────────────────────────────────────────────────────────────────
Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);
    const path = url.pathname;

    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

    if (path === "/health") return handleHealth();

    if (!isAuthorized(req)) return unauthorized();

    if (path === "/v1/findings" && req.method === "GET") return handleFindings();
    if (path === "/v1/papers"   && req.method === "GET") return handlePapers();
    if (path === "/v1/signals"  && req.method === "GET") return handleSignals();
    if (path === "/v1/kols"     && req.method === "GET") return handleKOLs();
    if (path === "/v1/hunt"     && req.method === "POST") return handleHunt(req);

    // Job status
    if (path.startsWith("/v1/jobs/")) {
      const jobId = path.split("/").pop() ?? "";
      const job = jobs.get(jobId);
      if (!job) return json({ error: "Job not found" }, 404);
      return json({ jobId, ...job });
    }

    return json({ error: "Not found", availableRoutes: ["/health", "/v1/findings", "/v1/papers", "/v1/signals", "/v1/kols", "/v1/hunt", "/v1/jobs/:id"] }, 404);
  },
});

console.log(`🔎 Gem Hunter API v${VERSION} running on http://localhost:${PORT}`);
if (!API_KEY) console.log("⚠️  No GEM_HUNTER_API_KEY set — open access (dev mode)");
