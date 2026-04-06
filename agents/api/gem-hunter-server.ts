/**
 * GH-058/GH-061 — Gem Hunter Standalone API + Dashboard
 *
 * Endpoints:
 *   GET  /                    — Dashboard UI (GH-061)
 *   GET  /health              — liveness check
 *   GET  /v1/findings         — latest run summary + top gems
 *   GET  /v1/papers           — scaffolded papers (docs/gem-hunter/scaffolds/)
 *   GET  /v1/signals          — signals.json (world-model feed)
 *   GET  /v1/kols             — kol-list.json if available
 *   POST /v1/hunt             — trigger gem hunt (async, returns job status)
 *   GET  /v1/jobs/:id         — hunt job status
 *
 * Auth: Bearer token from env GEM_HUNTER_API_KEY (open if not set — dev mode)
 * Port: 3095 (env GEM_HUNTER_API_PORT)
 */

import { existsSync, readFileSync, readdirSync } from "fs";
import { join } from "path";
import { spawn } from "child_process";

const PORT = Number(process.env.GEM_HUNTER_API_PORT ?? 3095);
const API_KEY = process.env.GEM_HUNTER_API_KEY ?? "";
const ROOT = join(import.meta.dir, "../..");
const REPORTS_DIR = join(ROOT, "docs/gem-hunter");
const VERSION = "1.1.0";

const jobs = new Map<string, { status: "running" | "done" | "error"; startedAt: string; pid?: number }>();

function isAuthorized(req: Request): boolean {
  if (!API_KEY) return true;
  const auth = req.headers.get("Authorization") ?? "";
  return auth === `Bearer ${API_KEY}`;
}

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

function scoreColor(s: number): string {
  if (s >= 80) return "#22c55e";
  if (s >= 60) return "#f59e0b";
  return "#ef4444";
}

function sourceIcon(src: string): string {
  const m: Record<string, string> = { github: "GH", huggingface: "HF", arxiv: "arXiv", reddit: "↑", producthunt: "PH", npm: "npm", exa: "Exa" };
  return m[src.toLowerCase()] ?? src.slice(0, 3).toUpperCase();
}

function sourceColor(src: string): string {
  const m: Record<string, string> = { github: "#e5e5e5", huggingface: "#f59e0b", arxiv: "#3b82f6", reddit: "#ff6314", producthunt: "#da552f", npm: "#cb3837", exa: "#8b5cf6" };
  return m[src.toLowerCase()] ?? "#737373";
}

// ── Dashboard HTML (GH-061) ────────────────────────────────────────────────────

function dashboardHTML(): Response {
  const latestPath = join(REPORTS_DIR, "latest-run.json");
  const hasData = existsSync(latestPath);
  let inlineGems = "[]";
  let inlineDate = "";

  if (hasData) {
    try {
      const run = JSON.parse(readFileSync(latestPath, "utf-8"));
      const gems = (run.gems ?? []).sort((a: {score?: number}, b: {score?: number}) => (b.score ?? 0) - (a.score ?? 0));
      inlineGems = JSON.stringify(gems);
      inlineDate = run.date ?? "";
    } catch { /* ignore */ }
  }

  const signalsPath = join(REPORTS_DIR, "signals.json");
  let inlineSignals = "[]";
  if (existsSync(signalsPath)) {
    try {
      const s = JSON.parse(readFileSync(signalsPath, "utf-8"));
      inlineSignals = JSON.stringify(s.signals ?? []);
    } catch { /* ignore */ }
  }

  const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gem Hunter — EGOS Discovery Engine</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body { font-family: 'Inter', system-ui, sans-serif; }
  .mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
  .gem-card { transition: all 0.15s ease; }
  .gem-card:hover { border-color: #22c55e44; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(34,197,94,0.05); }
  @keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .pulse-dot { animation: pulse-dot 2s infinite; }
  .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
</head>
<body class="bg-[#0a0a0a] text-[#e5e5e5] min-h-screen">

<header class="border-b border-[#1a1a1a] px-6 py-4 flex items-center justify-between sticky top-0 bg-[#0a0a0a]/95 backdrop-blur z-10">
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 rounded-lg bg-[#111] border border-[#22c55e22] flex items-center justify-center text-[#22c55e]">◈</div>
    <div>
      <div class="text-sm font-semibold">Gem Hunter</div>
      <div class="text-[10px] text-[#555] mono">EGOS Discovery Engine v${VERSION}</div>
    </div>
  </div>
  <div class="flex items-center gap-3">
    <div id="hunt-status" class="hidden items-center gap-2 text-xs text-[#f59e0b]">
      <div class="w-2 h-2 rounded-full bg-[#f59e0b] pulse-dot"></div>
      <span class="mono">Hunt em execução...</span>
    </div>
    <button onclick="triggerHunt()" id="hunt-btn"
      class="px-3 py-1.5 bg-[#0f1f0f] border border-[#22c55e] rounded-lg text-[#22c55e] text-xs font-semibold hover:bg-[#22c55e] hover:text-black transition-all mono">
      ▶ Run Hunt
    </button>
  </div>
</header>

<div class="border-b border-[#1a1a1a] px-6 py-2.5 flex gap-6 text-[11px] mono text-[#444]">
  <span>gems: <b id="stat-gems" class="text-[#22c55e]">—</b></span>
  <span>signals: <b id="stat-signals" class="text-[#8b5cf6]">—</b></span>
  <span>último run: <b id="stat-date" class="text-[#737373]">—</b></span>
  <span class="ml-auto text-[#333]">gemhunter.egos.ia.br</span>
</div>

<div class="max-w-7xl mx-auto px-6 py-6">

  <div class="flex gap-0 mb-6 border-b border-[#1a1a1a]">
    <button onclick="showTab('gems')" id="tab-gems"
      class="px-4 py-2.5 text-sm border-b-2 border-[#22c55e] text-[#22c55e] mono -mb-px">Gems</button>
    <button onclick="showTab('signals')" id="tab-signals"
      class="px-4 py-2.5 text-sm border-b-2 border-transparent text-[#555] mono -mb-px hover:text-[#737373]">Signals</button>
  </div>

  <!-- Gems -->
  <div id="tab-gems-content">
    <div class="flex gap-3 mb-5 flex-wrap items-center">
      <input id="q" oninput="filter()" placeholder="Buscar gems..."
        class="bg-[#111] border border-[#1a1a1a] focus:border-[#22c55e33] rounded-lg px-3 py-1.5 text-sm text-[#e5e5e5] outline-none mono placeholder-[#444] w-56">
      <select id="sector" onchange="filter()"
        class="bg-[#111] border border-[#1a1a1a] rounded-lg px-3 py-1.5 text-sm text-[#555] outline-none mono cursor-pointer">
        <option value="">Todos setores</option>
        <option value="agent">Agents</option>
        <option value="ai">AI / LLM</option>
        <option value="crypto">Crypto</option>
        <option value="governance">Governance</option>
        <option value="research">Research</option>
        <option value="system">Systems</option>
      </select>
      <span class="text-xs mono text-[#444] ml-auto"><span id="cnt">—</span> gems</span>
    </div>
    <div id="gems-grid" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3"></div>
    <div id="gems-empty" class="hidden text-center py-24">
      <div class="text-5xl mb-5 opacity-20">◈</div>
      <p class="text-[#555] text-sm mb-1">Nenhum gem encontrado.</p>
      <p class="text-[#333] text-xs mono mb-6">Execute um hunt para descobrir os melhores projetos.</p>
      <button onclick="triggerHunt()"
        class="px-5 py-2 bg-[#0f1f0f] border border-[#22c55e] rounded-lg text-[#22c55e] text-sm mono hover:bg-[#22c55e] hover:text-black transition-all">
        ▶ Run Hunt Agora
      </button>
    </div>
  </div>

  <!-- Signals -->
  <div id="tab-signals-content" class="hidden">
    <div id="signals-list" class="flex flex-col gap-3"></div>
    <div id="signals-empty" class="hidden text-center py-24">
      <div class="text-5xl mb-5 opacity-20">◉</div>
      <p class="text-[#555] text-sm">Nenhum signal disponível.</p>
      <p class="text-[#333] text-xs mono mt-1">Execute hunt com --track=x-signals-public.</p>
    </div>
  </div>

</div>

<script>
const INLINE_GEMS = ${inlineGems};
const INLINE_DATE = ${JSON.stringify(inlineDate)};
const INLINE_SIGNALS = ${inlineSignals};

let allGems = INLINE_GEMS;
let allSignals = INLINE_SIGNALS;
let pollTimer = null;

// Stats
document.getElementById('stat-gems').textContent = allGems.length || '0';
document.getElementById('stat-signals').textContent = allSignals.length || '0';
if (INLINE_DATE) document.getElementById('stat-date').textContent = new Date(INLINE_DATE).toLocaleDateString('pt-BR');

function showTab(name) {
  ['gems','signals'].forEach(t => {
    const content = document.getElementById('tab-' + t + '-content');
    const btn = document.getElementById('tab-' + t);
    const active = t === name;
    content.classList.toggle('hidden', !active);
    btn.classList.toggle('border-[#22c55e]', active);
    btn.classList.toggle('text-[#22c55e]', active);
    btn.classList.toggle('border-transparent', !active);
    btn.classList.toggle('text-[#555]', !active);
  });
}

function scoreColor(s) {
  return s >= 80 ? '#22c55e' : s >= 60 ? '#f59e0b' : '#ef4444';
}

function srcIcon(s) {
  return {github:'GH',huggingface:'HF',arxiv:'Ax',reddit:'↑',producthunt:'PH',npm:'npm',exa:'Exa'}[(s||'').toLowerCase()] || (s||'?').slice(0,3);
}

function srcColor(s) {
  return {github:'#d4d4d4',huggingface:'#f59e0b',arxiv:'#3b82f6',reddit:'#ff6314',producthunt:'#ef4444',npm:'#cb3837',exa:'#8b5cf6'}[(s||'').toLowerCase()] || '#737373';
}

function fmtStars(n) {
  if (!n) return '';
  return n >= 1000 ? '⭐ ' + (n/1000).toFixed(1) + 'k' : '⭐ ' + n;
}

function renderGems(gems) {
  const grid = document.getElementById('gems-grid');
  const empty = document.getElementById('gems-empty');
  document.getElementById('cnt').textContent = gems.length;
  if (!gems.length) { grid.classList.add('hidden'); empty.classList.remove('hidden'); return; }
  grid.classList.remove('hidden'); empty.classList.add('hidden');

  grid.innerHTML = gems.map(g => {
    const score = g.score ?? 0;
    const color = scoreColor(score);
    const src = g.source || 'github';
    const tags = (g.tags || []).slice(0, 3);
    const url = g.url || '#';
    return \`<div class="gem-card bg-[#111] border border-[#1a1a1a] rounded-xl p-4 cursor-pointer" onclick="window.open('\${url}','_blank')">
      <div class="flex items-start gap-3 mb-3">
        <div class="w-9 h-9 rounded-lg bg-[#0d0d0d] border border-[#1a1a1a] flex items-center justify-center text-[10px] mono font-bold shrink-0" style="color:\${srcColor(src)}">\${srcIcon(src)}</div>
        <div class="flex-1 min-w-0">
          <div class="text-[13px] font-semibold truncate">\${g.name || '?'}</div>
          <div class="text-[10px] text-[#444] mono truncate">\${url.replace('https://','')}</div>
        </div>
        <div class="text-right shrink-0">
          <div class="text-lg font-bold mono leading-none" style="color:\${color}">\${score || '?'}</div>
          <div class="text-[9px] text-[#444] mt-0.5">/100</div>
        </div>
      </div>
      <p class="text-[12px] text-[#666] leading-relaxed mb-3 line-clamp-2">\${g.description || ''}</p>
      <div class="flex items-center gap-1.5 flex-wrap">
        \${g.stars ? \`<span class="text-[10px] mono text-[#555]">\${fmtStars(g.stars)}</span>\` : ''}
        \${(g.topic||g.category) ? \`<span class="text-[10px] px-1.5 py-0.5 bg-[#1a1a1a] rounded-md text-[#555] mono">\${(g.topic||g.category||'').slice(0,22)}</span>\` : ''}
        \${tags.map(t=>\`<span class="text-[10px] px-1.5 py-0.5 bg-[#111] border border-[#1a1a1a] rounded-md text-[#444] mono">#\${t}</span>\`).join('')}
      </div>
    </div>\`;
  }).join('');
}

function renderSignals(signals) {
  const list = document.getElementById('signals-list');
  const empty = document.getElementById('signals-empty');
  if (!signals.length) { list.classList.add('hidden'); empty.classList.remove('hidden'); return; }
  list.classList.remove('hidden'); empty.classList.add('hidden');
  list.innerHTML = signals.map(s => \`
    <div class="bg-[#111] border border-[#1a1a1a] rounded-xl p-4">
      <div class="flex items-center gap-3 mb-2">
        <span class="text-[10px] px-2 py-0.5 bg-[#1a1a1a] rounded-md mono text-[#8b5cf6]">\${s.type||'signal'}</span>
        \${s.ts ? \`<span class="text-[10px] text-[#444] mono ml-auto">\${new Date(s.ts).toLocaleDateString('pt-BR')}</span>\` : ''}
      </div>
      <p class="text-[13px] text-[#d4d4d4] leading-relaxed">\${s.content||s.text||JSON.stringify(s)}</p>
    </div>
  \`).join('');
}

function filter() {
  const q = (document.getElementById('q').value||'').toLowerCase();
  const sector = (document.getElementById('sector').value||'').toLowerCase();
  renderGems(allGems.filter(g => {
    const text = ((g.name||'')+' '+(g.description||'')+' '+(g.topic||'')+' '+(g.category||'')).toLowerCase();
    return (!q||text.includes(q)) && (!sector||text.includes(sector));
  }));
}

async function triggerHunt() {
  const btn = document.getElementById('hunt-btn');
  const statusEl = document.getElementById('hunt-status');
  btn.disabled = true; btn.textContent = '⏳ Iniciando...';
  try {
    const res = await fetch('/v1/hunt', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({quick:true})});
    const data = await res.json();
    if (data.jobId) {
      statusEl.classList.remove('hidden'); statusEl.classList.add('flex');
      pollTimer = setInterval(async () => {
        const r = await fetch('/v1/jobs/'+data.jobId).then(r=>r.json()).catch(()=>null);
        if (!r) return;
        if (r.status === 'done') {
          clearInterval(pollTimer);
          statusEl.classList.add('hidden'); statusEl.classList.remove('flex');
          btn.disabled = false; btn.textContent = '▶ Run Hunt';
          const d = await fetch('/v1/findings').then(r=>r.json()).catch(()=>null);
          if (d?.latest?.gems) {
            allGems = d.latest.gems.sort((a,b)=>(b.score||0)-(a.score||0));
            document.getElementById('stat-gems').textContent = allGems.length;
            if (d.latest.date) document.getElementById('stat-date').textContent = new Date(d.latest.date).toLocaleDateString('pt-BR');
            filter();
          }
        } else if (r.status === 'error') {
          clearInterval(pollTimer); statusEl.classList.add('hidden');
          btn.disabled = false; btn.textContent = '▶ Run Hunt';
        }
      }, 8000);
    }
  } catch(e) { btn.disabled = false; btn.textContent = '▶ Run Hunt'; }
}

// Init
renderGems(allGems);
renderSignals(allSignals);
</script>
</body>
</html>`;

  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...CORS },
  });
}

// ── API handlers ───────────────────────────────────────────────────────────────

function handleHealth(): Response {
  return json({ status: "ok", version: VERSION, reportsDir: existsSync(REPORTS_DIR), activeJobs: jobs.size, ts: new Date().toISOString() });
}

function handleFindings(): Response {
  const latestPath = join(REPORTS_DIR, "latest-run.json");
  if (!existsSync(latestPath)) return json({ error: "No runs yet — POST /v1/hunt first" }, 404);
  const latest = JSON.parse(readFileSync(latestPath, "utf-8"));
  const signalsPath = join(REPORTS_DIR, "signals.json");
  const signals = existsSync(signalsPath) ? JSON.parse(readFileSync(signalsPath, "utf-8")).signals?.slice(0, 10) ?? [] : [];
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
  if (!existsSync(kolPath)) return json({ error: "KOL list not generated yet" }, 404);
  return json(JSON.parse(readFileSync(kolPath, "utf-8")));
}

async function handleHunt(req: Request): Promise<Response> {
  const body = await req.json().catch(() => ({})) as Record<string, unknown>;
  const track = typeof body.track === "string" ? body.track : "";
  const quick = body.quick !== false;

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
    if (path === "/" || path === "/dashboard") return dashboardHTML();
    if (path === "/health") return handleHealth();
    if (!isAuthorized(req)) return json({ error: "Unauthorized — provide Bearer token" }, 401);
    if (path === "/v1/findings" && req.method === "GET") return handleFindings();
    if (path === "/v1/papers"   && req.method === "GET") return handlePapers();
    if (path === "/v1/signals"  && req.method === "GET") return handleSignals();
    if (path === "/v1/kols"     && req.method === "GET") return handleKOLs();
    if (path === "/v1/hunt"     && req.method === "POST") return handleHunt(req);
    if (path.startsWith("/v1/jobs/")) {
      const jobId = path.split("/").pop() ?? "";
      const job = jobs.get(jobId);
      if (!job) return json({ error: "Job not found" }, 404);
      return json({ jobId, ...job });
    }
    return json({ error: "Not found", dashboard: "/", availableRoutes: ["/", "/health", "/v1/findings", "/v1/papers", "/v1/signals", "/v1/kols", "/v1/hunt", "/v1/jobs/:id"] }, 404);
  },
});

console.log(`🔎 Gem Hunter v${VERSION} — http://localhost:${PORT}`);
console.log(`   Dashboard: http://localhost:${PORT}/`);
if (!API_KEY) console.log("⚠️  No GEM_HUNTER_API_KEY — open access (dev mode)");
