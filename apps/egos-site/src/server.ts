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
    .prose table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .prose th { text-align: left; padding: 0.5rem 0.75rem; background: #1e293b; color: #e2e8f0; font-weight: 600; font-size: 0.875rem; border-bottom: 2px solid #334155; }
    .prose td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #1e293b; color: #cbd5e1; font-size: 0.875rem; }
    .prose tr:hover td { background: #0f172a; }
    .callout { border-left: 3px solid #38bdf8; background: #0c4a6e20; padding: 1rem 1.25rem; border-radius: 0 8px 8px 0; margin: 1.25rem 0; }
    .callout-warn { border-left-color: #f59e0b; background: #78350f20; }
    .callout p { margin: 0.25rem 0; }
    .code-block { position: relative; }
    .code-block .copy-btn { position: absolute; top: 0.5rem; right: 0.5rem; background: #334155; border: none; color: #94a3b8; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; opacity: 0; transition: opacity 0.2s; }
    .code-block:hover .copy-btn { opacity: 1; }
    .code-block .copy-btn:hover { background: #475569; color: #e2e8f0; }
    .toc { position: sticky; top: 2rem; }
    .toc a { display: block; padding: 0.25rem 0; color: #64748b; font-size: 0.8rem; text-decoration: none; border-left: 2px solid transparent; padding-left: 0.75rem; transition: all 0.15s; }
    .toc a:hover { color: #e2e8f0; border-left-color: #38bdf8; }
    .toc a.toc-h3 { padding-left: 1.5rem; font-size: 0.75rem; }
    .reading-progress { position: fixed; top: 0; left: 0; height: 2px; background: #38bdf8; z-index: 50; transition: width 0.1s; }
    .prose h2 a.anchor, .prose h3 a.anchor { color: #334155; text-decoration: none; margin-left: 0.35rem; font-weight: 400; }
    .prose h2:hover a.anchor, .prose h3:hover a.anchor { color: #64748b; }
    .faq-section { margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #1e293b; }
    .faq-section details { border: 1px solid #1e293b; border-radius: 8px; margin: 0.5rem 0; }
    .faq-section summary { padding: 0.75rem 1rem; cursor: pointer; color: #e2e8f0; font-weight: 500; }
    .faq-section details[open] summary { border-bottom: 1px solid #1e293b; }
    .faq-section details div { padding: 0.75rem 1rem; color: #94a3b8; }
  </style>
</head>
<body class="dark min-h-screen">
  <nav class="border-b border-slate-800 px-6 py-4 flex items-center justify-between max-w-4xl mx-auto">
    <a href="/" class="text-slate-100 font-semibold text-lg tracking-tight">EGOS</a>
    <div class="flex gap-6 text-sm text-slate-400">
      <a href="/timeline" class="hover:text-slate-100 transition-colors">Timeline</a>
      <a href="/showcase" class="hover:text-slate-100 transition-colors">Showcase</a>
      <a href="https://gemhunter.egos.ia.br" class="hover:text-slate-100 transition-colors">Gem Hunter</a>
      <a href="https://guard.egos.ia.br" class="hover:text-slate-100 transition-colors">Guard Brasil</a>
      <a href="/lab" class="hover:text-sky-400 text-sky-500 transition-colors font-medium">Lab →</a>
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

function readingTime(html: string): number {
  const text = html.replace(/<[^>]+>/g, '')
  const words = text.split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.ceil(words / 200))
}

function slugify(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').slice(0, 60)
}

function extractToc(html: string): Array<{ id: string; text: string; level: number }> {
  const toc: Array<{ id: string; text: string; level: number }> = []
  const regex = /<h([23])[^>]*>([^<]+)/g
  let match
  while ((match = regex.exec(html)) !== null) {
    const text = match[2].replace(/<[^>]+>/g, '').trim()
    if (text) toc.push({ id: slugify(text), text, level: parseInt(match[1]) })
  }
  return toc
}

function addHeadingAnchors(html: string): string {
  return html.replace(/<h([23])>([^<]+)<\/h\1>/g, (_m, level: string, text: string) => {
    const id = slugify(text)
    return `<h${level} id="${id}">${text} <a href="#${id}" class="anchor">#</a></h${level}>`
  })
}

function addCodeCopyButtons(html: string): string {
  return html.replace(/<pre><code>/g, '<div class="code-block"><button class="copy-btn" onclick="navigator.clipboard.writeText(this.parentElement.querySelector(\'code\').textContent).then(()=>{this.textContent=\'Copiado!\';setTimeout(()=>this.textContent=\'Copiar\',1500)})">Copiar</button><pre><code>'
  ).replace(/<\/code><\/pre>/g, '</code></pre></div>')
}

function articleJsonLd(article: { title: string; slug: string; published_at: string; body_html: string; views?: number }): string {
  const wordCount = (article.body_html ?? '').replace(/<[^>]+>/g, '').split(/\s+/).length
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Article',
        headline: article.title,
        datePublished: article.published_at,
        dateModified: article.published_at,
        url: `https://egos.ia.br/timeline/${article.slug}`,
        wordCount,
        inLanguage: 'pt-BR',
        author: {
          '@type': 'Person',
          name: 'Enio Rocha',
          url: 'https://github.com/enioxt'
        },
        publisher: {
          '@type': 'Organization',
          name: 'EGOS',
          url: 'https://egos.ia.br'
        },
        isPartOf: { '@type': 'Blog', name: 'EGOS Timeline', url: 'https://egos.ia.br/timeline' }
      }
    ]
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
    .select('slug, title, body_html, published_at', { count: 'exact' })
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
      ${a.body_html ? `<p class="mt-2 text-slate-400 text-sm line-clamp-3">${a.body_html.replace(/<[^>]+>/g, '').slice(0, 180)}…</p>` : ''}
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
    ?.from('timeline_articles')
    .update({ views: (article.views ?? 0) + 1 })
    .eq('slug', slug)
    .then(() => {})

  // Process content: add heading anchors and code copy buttons
  let contentHtml = article.body_html ?? renderMarkdown('')
  contentHtml = addHeadingAnchors(contentHtml)
  contentHtml = addCodeCopyButtons(contentHtml)

  const toc = extractToc(article.body_html ?? '')
  const minutes = readingTime(article.body_html ?? '')
  const jsonLd = articleJsonLd(article)

  // Fetch related articles
  const { data: related } = await (getSupabase()
    ?.from('timeline_articles')
    .select('slug, title, published_at')
    .neq('slug', slug)
    .order('published_at', { ascending: false })
    .limit(3) ?? Promise.resolve({ data: [] }))

  const tocHtml = toc.length > 2 ? `
    <nav class="toc hidden lg:block">
      <p class="text-xs text-slate-600 uppercase tracking-wider mb-2 font-semibold">Neste artigo</p>
      ${toc.map(t => `<a href="#${t.id}" class="${t.level === 3 ? 'toc-h3' : ''}">${t.text}</a>`).join('\n')}
    </nav>
  ` : ''

  const relatedHtml = (related ?? []).length > 0 ? `
    <div class="mt-12 pt-8 border-t border-slate-800">
      <h2 class="text-lg font-semibold text-slate-100 mb-4">Mais da Timeline</h2>
      <div class="grid gap-3 sm:grid-cols-3">
        ${(related ?? []).map((r: { slug: string; title: string; published_at: string }) => `
          <a href="/timeline/${r.slug}" class="border border-slate-800 rounded-lg p-4 hover:border-slate-600 transition-colors">
            <time class="text-xs text-slate-600">${formatDate(r.published_at)}</time>
            <p class="mt-1 text-sm text-slate-200 font-medium leading-snug">${r.title}</p>
          </a>
        `).join('')}
      </div>
    </div>
  ` : ''

  const body = `
    <div class="reading-progress" id="rp"></div>
    <script type="application/ld+json">${jsonLd}</script>
    <div class="${toc.length > 2 ? 'lg:grid lg:grid-cols-[1fr_200px] lg:gap-10' : ''}">
      <article>
        <header class="mb-10 pb-6 border-b border-slate-800">
          <a href="/timeline" class="text-sm text-slate-500 hover:text-slate-400 mb-4 inline-block">← Timeline</a>
          <h1 class="text-4xl font-bold text-slate-100 mt-2 leading-tight">${article.title}</h1>
          <div class="flex flex-wrap items-center gap-4 mt-4 text-sm text-slate-500">
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-sky-900 flex items-center justify-center text-xs text-sky-400 font-bold">E</div>
              <span>Enio Rocha</span>
            </div>
            <time datetime="${article.published_at}">${formatDate(article.published_at)}</time>
            <span>${minutes} min de leitura</span>
            ${article.views ? `<span>${article.views} views</span>` : ''}
            ${article.url ? `<a href="${article.url}" class="font-mono hover:text-sky-400" target="_blank">GitHub →</a>` : ''}
          </div>
        </header>
        <div class="prose max-w-none">
          ${contentHtml}
        </div>
        ${article.x_post_url ? `
          <div class="mt-8 pt-4 border-t border-slate-800">
            <p class="text-sm text-slate-500">Publicado no <a href="${article.x_post_url}" class="text-sky-400 hover:text-sky-300" target="_blank">X.com</a></p>
          </div>
        ` : ''}
        ${relatedHtml}
      </article>
      ${tocHtml}
    </div>
    <script>window.addEventListener('scroll',()=>{const d=document.documentElement;const p=d.scrollTop/(d.scrollHeight-d.clientHeight)*100;document.getElementById('rp').style.width=p+'%'})</script>
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

// ── /lab — EGOS Lab community (R$20/mês) ──────────────────────────────────────

app.get('/lab', (c) => {
  const body = `
    <div class="max-w-2xl">
      <div class="inline-block px-3 py-1 bg-sky-900/30 border border-sky-800 rounded-full text-sky-400 text-xs font-medium mb-6">
        Em construção · Lançamento em breve
      </div>
      <h1 class="text-5xl font-bold text-slate-100 leading-tight">
        EGOS Lab
      </h1>
      <p class="mt-6 text-xl text-slate-400">
        Comunidade de builders que aprendem construindo sistemas reais com IA governada.
        R$ 20/mês. Sem enrolação.
      </p>

      <div class="mt-10 grid gap-4 sm:grid-cols-2">
        <div class="border border-slate-800 rounded-xl p-5">
          <div class="text-xl mb-2">🔧</div>
          <h3 class="font-semibold text-slate-100">Projetos reais</h3>
          <p class="text-sm text-slate-400 mt-1">Acesso ao código do EGOS, sessões de desenvolvimento ao vivo, revisão de PRs.</p>
        </div>
        <div class="border border-slate-800 rounded-xl p-5">
          <div class="text-xl mb-2">🧠</div>
          <h3 class="font-semibold text-slate-100">Governance patterns</h3>
          <p class="text-sm text-slate-400 mt-1">Como estruturar agentes de IA com LGPD, SSOT, evidence-first.</p>
        </div>
        <div class="border border-slate-800 rounded-xl p-5">
          <div class="text-xl mb-2">💬</div>
          <h3 class="font-semibold text-slate-100">Grupo WhatsApp</h3>
          <p class="text-sm text-slate-400 mt-1">Grupo privado com acesso direto ao Enio Rocha e outros builders.</p>
        </div>
        <div class="border border-slate-800 rounded-xl p-5">
          <div class="text-xl mb-2">📰</div>
          <h3 class="font-semibold text-slate-100">Timeline em primeira mão</h3>
          <p class="text-sm text-slate-400 mt-1">Cada decisão de arquitetura explicada antes de ir para o público.</p>
        </div>
      </div>

      <div class="mt-12 p-6 border border-slate-700 rounded-xl bg-slate-900/50">
        <h2 class="text-lg font-semibold text-slate-100 mb-2">Interesse?</h2>
        <p class="text-slate-400 text-sm mb-4">Deixe seu email — você será notificado quando o Lab abrir.</p>
        <a href="mailto:enio@egos.ia.br?subject=EGOS Lab - Interesse" class="inline-block px-6 py-3 bg-sky-600 hover:bg-sky-500 rounded-xl text-white font-medium transition-colors text-sm">
          Quero participar →
        </a>
        <p class="mt-3 text-xs text-slate-600">Ou siga <a href="https://x.com/anoineim" class="text-sky-800 hover:text-sky-600">@anoineim no X.com</a> para updates.</p>
      </div>
    </div>
  `
  return c.html(layout('EGOS Lab — Comunidade R$20/mês', body))
})

// ── /showcase — EGOS encapsulation showcase ────────────────────────────────────

app.get('/showcase', (c) => {
  const body = `
    <div class="max-w-2xl">
      <div class="inline-block px-3 py-1 bg-green-900/30 border border-green-800 rounded-full text-green-400 text-xs font-medium mb-6">
        Primeiro artigo publicado · <a href="/timeline/altitude-errada" class="underline hover:text-green-300">ler agora →</a>
      </div>
      <h1 class="text-4xl font-bold text-slate-100 leading-tight">
        EGOS: plataforma multi-agente<br>brasileira, open-source
      </h1>
      <p class="mt-6 text-lg text-slate-400">
        Como construir um ecossistema de IA governado por 1 dev, com LGPD embutida,
        103 scripts, 24 agentes, e transparência radical. De dentro para fora.
      </p>
      <div class="mt-8 space-y-3">
        <div class="flex items-center gap-3 text-sm">
          <span class="w-6 h-6 flex items-center justify-center rounded-full bg-green-900/50 text-green-400 text-xs">✓</span>
          <span class="text-slate-300">Camada 0 — CLAUDE.md v4 auditado (4 PROVEN / 6 PARTIAL / 6 ASPIRATIONAL)</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-6 h-6 flex items-center justify-center rounded-full bg-green-900/50 text-green-400 text-xs">✓</span>
          <span class="text-slate-300">Camada 1 — 24 agents inventariados, 4 órfãos registrados</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-6 h-6 flex items-center justify-center rounded-full bg-slate-800 text-slate-500 text-xs">○</span>
          <span class="text-slate-500">Camada 2 — Governance Pipeline (próxima semana)</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="w-6 h-6 flex items-center justify-center rounded-full bg-slate-800 text-slate-500 text-xs">○</span>
          <span class="text-slate-500">Camadas 3-7 — Stack, Produtos, Data, Dashboards, Artigo</span>
        </div>
      </div>
      <div class="mt-10 flex gap-4">
        <a href="/timeline" class="px-6 py-3 bg-sky-600 hover:bg-sky-500 rounded-xl text-white font-medium transition-colors text-sm">
          Ver Timeline →
        </a>
        <a href="/lab" class="px-6 py-3 border border-slate-700 hover:border-slate-500 rounded-xl text-slate-300 font-medium transition-colors text-sm">
          Acompanhar no Lab →
        </a>
      </div>
    </div>
  `
  return c.html(layout('Showcase — EGOS Platform', body))
})

// ── health ─────────────────────────────────────────────────────────────────────

app.get('/health', (c) => c.json({ ok: true, service: 'egos-site', port: PORT }))

// llms.txt: curated map for AI agents (spec: llmstxt.org)
app.get('/llms.txt', async (c) => {
  const supabase = getSupabase()
  let articleList = ''
  if (supabase) {
    const { data } = await supabase
      .from('timeline_articles')
      .select('slug, title')
      .order('published_at', { ascending: false })
      .limit(20)
    articleList = (data ?? []).map((a: { slug: string; title: string }) =>
      `- [${a.title}](https://egos.ia.br/timeline/${a.slug})`
    ).join('\n')
  }
  c.header('Content-Type', 'text/plain; charset=utf-8')
  c.header('Cache-Control', 'public, max-age=3600')
  return c.text(`# EGOS — Governed AI Platform
> AI orchestration kernel with built-in governance, LGPD compliance, and radical transparency. Built in Brazil by Enio Rocha.

## Products
- [Guard Brasil API](https://guard.egos.ia.br): PII detection for 16 Brazilian data patterns. 4ms latency, open-source MIT
- [Gem Hunter](https://gemhunter.egos.ia.br): Discovers emerging AI repos across 14 sources
- [EGOS Timeline](https://egos.ia.br/timeline): Transparent development log

## Source Code
- [GitHub](https://github.com/enioxt/egos): Main repository
- [npm: @egosbr/guard-brasil](https://www.npmjs.com/package/@egosbr/guard-brasil): TypeScript SDK

## Articles
${articleList || '- No articles published yet'}

## Contact
- GitHub: @enioxt
- X.com: @anoineim
`)
})

app.get('/robots.txt', (c) => {
  c.header('Content-Type', 'text/plain')
  return c.text(`User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

Sitemap: https://egos.ia.br/sitemap.xml
`)
})

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
