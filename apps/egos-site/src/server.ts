import { Hono } from 'hono'
import { createClient } from '@supabase/supabase-js'

const PORT = parseInt(process.env.PORT ?? '3071', 10)

function getSupabase() {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_ANON_KEY
  if (!url || !key) return null
  return createClient(url, key)
}

const app = new Hono()

// ── helpers ────────────────────────────────────────────────────────────────────

function layout(title: string, body: string): string {
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | EGOS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config = { darkMode: 'class' }</script>
  <style>
    body { background: #0a0a0f; color: #e2e8f0; font-family: 'Inter', system-ui, sans-serif; }
    .prose h1 { font-size: 1.75rem; font-weight: 700; margin: 1.5rem 0 1rem; }
    .prose h2 { font-size: 1.35rem; font-weight: 600; margin: 1.25rem 0 0.75rem; border-bottom: 1px solid #1e293b; padding-bottom: 0.4rem; }
    .prose h3 { font-size: 1.1rem; font-weight: 600; margin: 1rem 0 0.5rem; }
    .prose p { margin: 0.75rem 0; line-height: 1.7; color: #cbd5e1; }
    .prose ul { list-style: disc; margin: 0.75rem 0 0.75rem 1.5rem; }
    .prose li { margin: 0.3rem 0; color: #cbd5e1; }
    .prose code { background: #1e293b; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.875rem; color: #7dd3fc; }
    .prose pre { background: #1e293b; padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 1rem 0; }
    .prose pre code { background: none; padding: 0; }
    .prose a { color: #38bdf8; text-decoration: underline; }
    .prose blockquote { border-left: 3px solid #334155; padding-left: 1rem; color: #94a3b8; margin: 1rem 0; }
  </style>
</head>
<body class="dark min-h-screen">
  <nav class="border-b border-slate-800 px-6 py-4 flex items-center justify-between max-w-4xl mx-auto">
    <a href="/" class="text-slate-100 font-semibold text-lg tracking-tight">EGOS</a>
    <div class="flex gap-6 text-sm text-slate-400">
      <a href="/timeline" class="hover:text-slate-100 transition-colors">Timeline</a>
      <a href="https://gemhunter.egos.ia.br" class="hover:text-slate-100 transition-colors">Gem Hunter</a>
      <a href="https://guard.egos.ia.br" class="hover:text-slate-100 transition-colors">Guard Brasil</a>
    </div>
  </nav>
  <main class="max-w-4xl mx-auto px-6 py-10">
    ${body}
  </main>
  <footer class="border-t border-slate-800 px-6 py-8 mt-16 text-center text-sm text-slate-600">
    <p>EGOS — Governed AI Platform · <a href="https://github.com/enioxt/egos" class="hover:text-slate-400 transition-colors">GitHub</a></p>
  </footer>
</body>
</html>`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit', month: 'long', year: 'numeric'
  })
}

// ── routes ─────────────────────────────────────────────────────────────────────

// TL-006: GET /timeline — list articles paginated
app.get('/timeline', async (c) => {
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const limit = 12
  const offset = (page - 1) * limit

  const supabase = getSupabase()
  if (!supabase) return c.html(layout('Timeline', '<p class="text-slate-400">Supabase não configurado.</p>'))

  const { data: articles, error, count } = await supabase
    .from('timeline_articles')
    .select('slug, title, summary, published_at, commit_hash', { count: 'exact' })
    .order('published_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) {
    return c.html(layout('Timeline', `<p class="text-red-400">Erro ao carregar artigos: ${error.message}</p>`))
  }

  const totalPages = Math.ceil((count ?? 0) / limit)

  const articleCards = (articles ?? []).map(a => `
    <article class="border border-slate-800 rounded-xl p-6 hover:border-slate-600 transition-colors">
      <time class="text-xs text-slate-500 uppercase tracking-wide">${formatDate(a.published_at)}</time>
      <h2 class="mt-2 text-xl font-semibold text-slate-100 leading-snug">
        <a href="/timeline/${a.slug}" class="hover:text-sky-400 transition-colors">${a.title}</a>
      </h2>
      ${a.summary ? `<p class="mt-2 text-slate-400 text-sm line-clamp-3">${a.summary}</p>` : ''}
      ${a.commit_hash ? `<p class="mt-3 text-xs text-slate-600 font-mono">commit ${a.commit_hash.slice(0, 7)}</p>` : ''}
      <a href="/timeline/${a.slug}" class="mt-4 inline-block text-sm text-sky-400 hover:text-sky-300">Ler artigo →</a>
    </article>
  `).join('\n')

  const pagination = totalPages > 1 ? `
    <div class="flex justify-center gap-3 mt-10">
      ${page > 1 ? `<a href="/timeline?page=${page - 1}" class="px-4 py-2 bg-slate-800 rounded-lg text-sm hover:bg-slate-700">← Anterior</a>` : ''}
      <span class="px-4 py-2 text-sm text-slate-500">${page} / ${totalPages}</span>
      ${page < totalPages ? `<a href="/timeline?page=${page + 1}" class="px-4 py-2 bg-slate-800 rounded-lg text-sm hover:bg-slate-700">Próxima →</a>` : ''}
    </div>
  ` : ''

  const body = `
    <header class="mb-10">
      <h1 class="text-4xl font-bold text-slate-100">Timeline</h1>
      <p class="mt-2 text-slate-400">O que foi construído, como e por quê. Transparência radical do desenvolvimento do EGOS.</p>
    </header>
    ${(articles ?? []).length === 0 ? '<p class="text-slate-500">Nenhum artigo publicado ainda.</p>' : `
      <div class="grid gap-4 sm:grid-cols-2">
        ${articleCards}
      </div>
      ${pagination}
    `}
  `

  return c.html(layout('Timeline', body))
})

// TL-007: GET /timeline/:slug — render article + metrics
app.get('/timeline/:slug', async (c) => {
  const slug = c.req.param('slug')

  const supabase = getSupabase()
  if (!supabase) return c.html(layout('Artigo não encontrado', '<p class="text-slate-400">Supabase não configurado.</p>'), 503)

  const { data: article, error } = await supabase
    .from('timeline_articles')
    .select('*')
    .eq('slug', slug)
    .single()

  if (error || !article) {
    return c.html(layout('Artigo não encontrado', `
      <div class="text-center py-20">
        <p class="text-6xl mb-6">404</p>
        <p class="text-slate-400">Artigo não encontrado.</p>
        <a href="/timeline" class="mt-6 inline-block text-sky-400 hover:text-sky-300">← Voltar para Timeline</a>
      </div>
    `), 404)
  }

  // Track view (fire-and-forget)
  getSupabase()
    .from('timeline_articles')
    .update({ view_count: (article.view_count ?? 0) + 1 })
    .eq('slug', slug)
    .then(() => {})

  // Convert markdown-like content to simple HTML
  const contentHtml = renderMarkdown(article.content ?? article.summary ?? '')

  const body = `
    <article>
      <header class="mb-10 pb-6 border-b border-slate-800">
        <a href="/timeline" class="text-sm text-slate-500 hover:text-slate-400 mb-4 inline-block">← Timeline</a>
        <h1 class="text-4xl font-bold text-slate-100 mt-2 leading-tight">${article.title}</h1>
        <div class="flex items-center gap-6 mt-4 text-sm text-slate-500">
          <time>${formatDate(article.published_at)}</time>
          ${article.commit_hash ? `<span class="font-mono">commit ${article.commit_hash.slice(0, 7)}</span>` : ''}
          ${article.view_count ? `<span>${article.view_count} visualizações</span>` : ''}
        </div>
      </header>
      <div class="prose max-w-none">
        ${contentHtml}
      </div>
      ${article.x_post_url ? `
        <div class="mt-12 pt-6 border-t border-slate-800">
          <p class="text-sm text-slate-500">Publicado no <a href="${article.x_post_url}" class="text-sky-400 hover:text-sky-300" target="_blank">X.com</a></p>
        </div>
      ` : ''}
    </article>
  `

  return c.html(layout(article.title, body))
})

// ── homepage ───────────────────────────────────────────────────────────────────

app.get('/', (c) => {
  const body = `
    <div class="py-10">
      <h1 class="text-5xl font-bold text-slate-100 leading-tight">
        Governed AI,<br><span class="text-sky-400">built in public.</span>
      </h1>
      <p class="mt-6 text-xl text-slate-400 max-w-2xl">
        EGOS é um kernel de orquestração para agentes de IA com governança embutida.
        Construído no Brasil, focado em LGPD, transparência e automação real.
      </p>
      <div class="mt-10 flex gap-4">
        <a href="/timeline" class="px-6 py-3 bg-sky-600 hover:bg-sky-500 rounded-xl text-white font-medium transition-colors">
          Ver Timeline →
        </a>
        <a href="https://guard.egos.ia.br" class="px-6 py-3 border border-slate-700 hover:border-slate-500 rounded-xl text-slate-300 font-medium transition-colors">
          Guard Brasil API
        </a>
      </div>
    </div>

    <div class="mt-20 grid gap-6 sm:grid-cols-3">
      <div class="border border-slate-800 rounded-xl p-6">
        <div class="text-2xl mb-3">🛡️</div>
        <h3 class="font-semibold text-slate-100">Guard Brasil</h3>
        <p class="text-sm text-slate-400 mt-2">PII detection e LGPD compliance em 4ms. 16 padrões brasileiros.</p>
        <a href="https://guard.egos.ia.br" class="mt-4 text-sm text-sky-400 hover:text-sky-300 block">guard.egos.ia.br →</a>
      </div>
      <div class="border border-slate-800 rounded-xl p-6">
        <div class="text-2xl mb-3">💎</div>
        <h3 class="font-semibold text-slate-100">Gem Hunter</h3>
        <p class="text-sm text-slate-400 mt-2">Descobre repositórios de IA emergentes antes de virarem mainstream.</p>
        <a href="https://gemhunter.egos.ia.br" class="mt-4 text-sm text-sky-400 hover:text-sky-300 block">gemhunter.egos.ia.br →</a>
      </div>
      <div class="border border-slate-800 rounded-xl p-6">
        <div class="text-2xl mb-3">📰</div>
        <h3 class="font-semibold text-slate-100">Timeline</h3>
        <p class="text-sm text-slate-400 mt-2">Cada commit vira um artigo. Desenvolvimento transparente, em público.</p>
        <a href="/timeline" class="mt-4 text-sm text-sky-400 hover:text-sky-300 block">egos.ia.br/timeline →</a>
      </div>
    </div>
  `
  return c.html(layout('EGOS — Governed AI Platform', body))
})

// ── health ─────────────────────────────────────────────────────────────────────

app.get('/health', (c) => c.json({ ok: true, service: 'egos-site', port: PORT }))

// ── markdown renderer (simple, no deps) ────────────────────────────────────────

function renderMarkdown(text: string): string {
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
    .replace(/^(?!<[hul]).+/gm, '<p>$&</p>')
    .replace(/<p><\/p>/g, '')
    .replace(/\n{2,}/g, '\n')
}

// ── start ──────────────────────────────────────────────────────────────────────

console.log(`🌐 EGOS site running on http://localhost:${PORT}`)

export default {
  port: PORT,
  fetch: app.fetch,
}
