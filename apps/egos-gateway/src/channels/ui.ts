/**
 * EGOS Gateway — Knowledge System UI
 *
 * Serves a single-page visual dashboard for the EGOS Knowledge System.
 * Fetches data from the /knowledge/* API endpoints on the same gateway.
 *
 * Route: GET /ui
 */

import { Hono } from "hono";

export const ui = new Hono();

/** Return the full base URL from a request context */
function getBase(req: Request): string {
  const url = new URL(req.url);
  return `${url.protocol}//${url.host}`;
}

const HTML = (base: string) => `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EGOS Knowledge System</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config = { darkMode: 'class' }</script>
<style>
  body { background: #0f1117; color: #e2e8f0; font-family: 'Inter', system-ui, sans-serif; }
  .card { background: #1a1f2e; border: 1px solid #2d3748; }
  .badge { font-size: 0.7rem; padding: 2px 7px; border-radius: 9999px; font-weight: 600; letter-spacing: 0.03em; }
  .badge-concept { background: #1e3a5f; color: #63b3ed; }
  .badge-pattern { background: #1a3a2e; color: #68d391; }
  .badge-decision { background: #3a1a2e; color: #f687b3; }
  .badge-entity { background: #2e2a1a; color: #f6e05e; }
  .badge-synthesis { background: #2a1a3a; color: #b794f4; }
  .badge-how-to { background: #1a2e3a; color: #76e4f7; }
  .quality-bar { height: 4px; border-radius: 2px; background: #2d3748; }
  .quality-fill { height: 4px; border-radius: 2px; transition: width 0.6s ease; }
  .q-high { background: #48bb78; }
  .q-mid { background: #ed8936; }
  .q-low { background: #fc8181; }
  input[type=text]:focus { outline: 2px solid #4299e1; outline-offset: 2px; }
  .page-card:hover { border-color: #4a5568; transform: translateY(-1px); transition: all 0.15s; }
  .spinner { border: 3px solid #2d3748; border-top: 3px solid #4299e1; border-radius: 50%; width: 28px; height: 28px; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #1a1f2e; } ::-webkit-scrollbar-thumb { background: #4a5568; border-radius: 3px; }
</style>
</head>
<body class="min-h-screen">

<!-- Header -->
<header class="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">EG</div>
    <div>
      <h1 class="text-white font-semibold text-lg leading-none">EGOS Knowledge System</h1>
      <p class="text-gray-500 text-xs mt-0.5">Wiki · Learnings · Cross-refs</p>
    </div>
  </div>
  <div class="flex items-center gap-4 text-sm text-gray-400">
    <span id="stat-pages" class="text-white font-semibold">—</span> pages
    <span>·</span>
    <span id="stat-quality" class="text-white font-semibold">—</span> avg quality
    <span>·</span>
    <span id="stat-learnings" class="text-white font-semibold">—</span> learnings
    <button onclick="refresh()" class="ml-4 text-blue-400 hover:text-blue-300 text-xs border border-gray-700 rounded px-2 py-1">↻ Refresh</button>
  </div>
</header>

<!-- Search Bar -->
<div class="px-6 py-4 border-b border-gray-800 flex gap-3 items-center">
  <svg class="w-4 h-4 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
  <input id="search-input" type="text" placeholder="Search pages by title or content… (min 2 chars)"
    class="flex-1 bg-transparent text-white placeholder-gray-600 text-sm border-none focus:ring-0"
    oninput="handleSearch(this.value)">
  <select id="cat-filter" onchange="filterByCategory(this.value)"
    class="bg-gray-800 text-gray-300 text-xs border border-gray-700 rounded px-2 py-1">
    <option value="">All categories</option>
    <option value="concept">concept</option>
    <option value="pattern">pattern</option>
    <option value="decision">decision</option>
    <option value="entity">entity</option>
    <option value="synthesis">synthesis</option>
    <option value="how-to">how-to</option>
  </select>
</div>

<!-- Main Content -->
<main class="px-6 py-6 max-w-7xl mx-auto">

  <!-- Loading -->
  <div id="loading" class="flex items-center justify-center py-20">
    <div class="spinner"></div>
  </div>

  <!-- Search results -->
  <div id="search-results" class="hidden mb-8">
    <h2 class="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-4">Search Results</h2>
    <div id="search-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"></div>
  </div>

  <!-- Category sections -->
  <div id="category-sections"></div>

  <!-- Learnings panel -->
  <div id="learnings-section" class="mt-10">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-gray-400 text-xs font-semibold uppercase tracking-widest">Recent Learnings</h2>
      <select id="learning-filter" onchange="loadLearnings(this.value)"
        class="bg-gray-800 text-gray-300 text-xs border border-gray-700 rounded px-2 py-1">
        <option value="">All domains</option>
        <option value="general">general</option>
        <option value="architecture">architecture</option>
        <option value="deployment">deployment</option>
        <option value="monetization">monetization</option>
        <option value="governance">governance</option>
        <option value="agents">agents</option>
        <option value="security">security</option>
        <option value="dx">dx</option>
      </select>
    </div>
    <div id="learnings-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3"></div>
  </div>

</main>

<!-- Page Detail Modal -->
<div id="modal" class="hidden fixed inset-0 bg-black bg-opacity-70 z-50 flex items-start justify-center pt-20 px-4" onclick="closeModal(event)">
  <div class="card rounded-xl max-w-2xl w-full max-h-[70vh] overflow-y-auto p-6 shadow-2xl">
    <div class="flex items-start justify-between mb-4">
      <div>
        <div id="modal-category" class="badge mb-2"></div>
        <h2 id="modal-title" class="text-white text-xl font-bold mt-1"></h2>
      </div>
      <button onclick="document.getElementById('modal').classList.add('hidden')" class="text-gray-500 hover:text-white text-2xl leading-none">×</button>
    </div>
    <div id="modal-content" class="text-gray-300 text-sm leading-relaxed prose prose-invert max-w-none whitespace-pre-wrap"></div>
    <div id="modal-meta" class="mt-4 pt-4 border-t border-gray-700 flex flex-wrap gap-2"></div>
  </div>
</div>

<script>
const BASE = '${base}';
let searchTimeout = null;
let allPages = {};

function qualityColor(q) {
  if (q >= 75) return 'q-high';
  if (q >= 50) return 'q-mid';
  return 'q-low';
}

function badgeClass(cat) {
  const m = { concept:'badge-concept', pattern:'badge-pattern', decision:'badge-decision', entity:'badge-entity', synthesis:'badge-synthesis', 'how-to':'badge-how-to' };
  return m[cat] || 'badge-concept';
}

function pageCard(p, onclick) {
  const qc = qualityColor(p.quality_score);
  const tags = (p.tags || []).slice(0, 3).map(t => \`<span class="text-xs text-gray-500">#\${t}</span>\`).join(' ');
  return \`
    <div class="card rounded-lg p-4 page-card cursor-pointer" onclick="\${onclick}">
      <div class="flex items-start justify-between mb-2">
        <span class="badge \${badgeClass(p.category)}">\${p.category}</span>
        <span class="text-xs text-gray-500">\${p.quality_score}/100</span>
      </div>
      <h3 class="text-white text-sm font-medium mb-2 leading-snug">\${p.title}</h3>
      <div class="quality-bar mb-2"><div class="quality-fill \${qc}" style="width:\${p.quality_score}%"></div></div>
      <div class="flex flex-wrap gap-1">\${tags}</div>
    </div>
  \`;
}

async function loadStats() {
  try {
    const r = await fetch(BASE + '/knowledge/stats');
    const d = await r.json();
    document.getElementById('stat-pages').textContent = d.pages?.total ?? '—';
    document.getElementById('stat-quality').textContent = (d.pages?.avg_quality ?? '—') + '%';
    document.getElementById('stat-learnings').textContent = d.learnings?.total ?? '—';
  } catch(e) { console.error('stats:', e); }
}

async function loadIndex() {
  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('category-sections').innerHTML = '';
  try {
    const r = await fetch(BASE + '/knowledge/index');
    const d = await r.json();
    allPages = d.categories || {};

    const catFilter = document.getElementById('cat-filter').value;
    const cats = Object.entries(allPages)
      .filter(([c]) => !catFilter || c === catFilter)
      .sort(([a], [b]) => a.localeCompare(b));

    const container = document.getElementById('category-sections');
    if (cats.length === 0) {
      container.innerHTML = '<p class="text-gray-600 text-center py-16">No pages found.</p>';
    } else {
      for (const [cat, pages] of cats) {
        const cards = pages.map(p => pageCard(p, \`openPage('\${p.slug}')\`)).join('');
        container.innerHTML += \`
          <div class="mb-8">
            <div class="flex items-center gap-3 mb-3">
              <span class="badge \${badgeClass(cat)}">\${cat}</span>
              <span class="text-gray-600 text-xs">\${pages.length} pages</span>
              <div class="flex-1 h-px bg-gray-800"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">\${cards}</div>
          </div>
        \`;
      }
    }
  } catch(e) {
    document.getElementById('category-sections').innerHTML = '<p class="text-red-500 text-center py-16">Failed to load pages. Is the gateway running?</p>';
    console.error('index:', e);
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

async function loadLearnings(domain = '') {
  const url = BASE + '/knowledge/learnings?limit=9' + (domain ? '&domain=' + domain : '');
  try {
    const r = await fetch(url);
    const d = await r.json();
    const grid = document.getElementById('learnings-grid');
    const items = d.learnings || [];
    if (items.length === 0) {
      grid.innerHTML = '<p class="text-gray-600 text-sm col-span-3">No learnings recorded yet.</p>';
      return;
    }
    const outcomeColor = { success: 'text-green-400', failure: 'text-red-400', insight: 'text-yellow-400' };
    grid.innerHTML = items.map(l => \`
      <div class="card rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <span class="badge badge-concept">\${l.domain}</span>
          <span class="text-xs \${outcomeColor[l.outcome] || 'text-gray-400'}">\${l.outcome}</span>
        </div>
        <p class="text-white text-sm font-medium mb-1 leading-snug">\${l.summary}</p>
        \${l.pattern ? '<p class="text-gray-500 text-xs">pattern: ' + l.pattern + '</p>' : ''}
      </div>
    \`).join('');
  } catch(e) { console.error('learnings:', e); }
}

async function openPage(slug) {
  try {
    const r = await fetch(BASE + '/knowledge/pages/' + slug);
    const p = await r.json();
    document.getElementById('modal-title').textContent = p.title;
    document.getElementById('modal-category').className = 'badge ' + badgeClass(p.category);
    document.getElementById('modal-category').textContent = p.category;
    document.getElementById('modal-content').textContent = p.content || '(no content)';
    const tags = (p.tags || []).map(t => \`<span class="badge badge-concept">#\${t}</span>\`).join('');
    const refs = (p.cross_refs || []).map(r => \`<span class="badge badge-pattern">\${r}</span>\`).join('');
    document.getElementById('modal-meta').innerHTML =
      (tags ? '<div class="w-full text-xs text-gray-500 mb-1">Tags: ' + tags + '</div>' : '') +
      (refs ? '<div class="w-full text-xs text-gray-500">Cross-refs: ' + refs + '</div>' : '') +
      '<div class="w-full text-xs text-gray-600 mt-2">Quality: ' + p.quality_score + '/100 · Updated: ' + (p.updated_at || '').slice(0,10) + '</div>';
    document.getElementById('modal').classList.remove('hidden');
  } catch(e) { console.error('page:', e); }
}

function closeModal(e) {
  if (e.target === document.getElementById('modal')) {
    document.getElementById('modal').classList.add('hidden');
  }
}

function handleSearch(val) {
  clearTimeout(searchTimeout);
  if (val.length < 2) {
    document.getElementById('search-results').classList.add('hidden');
    document.getElementById('category-sections').classList.remove('hidden');
    return;
  }
  searchTimeout = setTimeout(() => doSearch(val), 350);
}

async function doSearch(q) {
  try {
    const r = await fetch(BASE + '/knowledge/search?q=' + encodeURIComponent(q));
    const d = await r.json();
    const results = d.results || [];
    const grid = document.getElementById('search-grid');
    grid.innerHTML = results.length
      ? results.map(p => pageCard(p, \`openPage('\${p.slug}')\`)).join('')
      : '<p class="text-gray-600 text-sm col-span-4">No results for "' + q + '"</p>';
    document.getElementById('search-results').classList.remove('hidden');
    document.getElementById('category-sections').classList.add('hidden');
  } catch(e) { console.error('search:', e); }
}

function filterByCategory(val) {
  document.getElementById('search-input').value = '';
  document.getElementById('search-results').classList.add('hidden');
  document.getElementById('category-sections').classList.remove('hidden');
  loadIndex();
}

function refresh() {
  loadStats();
  loadIndex();
  loadLearnings(document.getElementById('learning-filter').value);
}

// Init
refresh();
</script>
</body>
</html>`;

ui.get("/", async (c) => {
  const base = getBase(c.req.raw);
  return c.html(HTML(base));
});

ui.get("/gem-hunter", async (c) => {
  const base = getBase(c.req.raw);
  return c.redirect(base + "/ui"); // redirect to main for now, full UI later
});
