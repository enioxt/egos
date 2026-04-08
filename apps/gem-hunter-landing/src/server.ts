import { Hono, type Context } from 'hono'
import { serveStatic } from 'hono/bun'
import { cors } from 'hono/cors'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const app = new Hono<any>()
const PORT = parseInt(process.env.PORT ?? '3070', 10)

const SUPABASE_URL = process.env.SUPABASE_URL ?? ''
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY ?? process.env.SUPABASE_ANON_KEY ?? ''

// ── CORS for API routes ────────────────────────────────────────────────────────
app.use('/api/*', cors({ origin: '*', allowMethods: ['GET', 'POST', 'DELETE'] }))

// ── helpers ────────────────────────────────────────────────────────────────────

async function supabaseQuery(path: string, options: RequestInit = {}): Promise<Response> {
  return fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...options,
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
      ...(options.headers as Record<string, string> ?? {}),
    },
  })
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function requireSupabase(c: Context<any>) {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    return c.json({ error: 'Supabase not configured' }, 503)
  }
  return null
}

// ── GH-078: Voting API ─────────────────────────────────────────────────────────

// POST /api/gems/:encodedUrl/upvote — upvote a gem (anon via fingerprint)
app.post('/api/gems/:encodedUrl/upvote', async (c) => {
  const err = requireSupabase(c)
  if (err) return err

  const gemUrl = decodeURIComponent(c.req.param('encodedUrl'))
  const body = await c.req.json().catch(() => ({})) as { fingerprint?: string }
  const fingerprint = (body.fingerprint ?? c.req.header('x-forwarded-for') ?? 'anon').slice(0, 64)

  const res = await supabaseQuery('gem_votes', {
    method: 'POST',
    body: JSON.stringify({ gem_url: gemUrl, fingerprint }),
  })

  if (res.status === 409) {
    return c.json({ ok: false, error: 'already_voted' }, 409)
  }
  if (!res.ok) {
    const text = await res.text()
    return c.json({ ok: false, error: text }, 400)
  }

  // Return updated vote count
  const countRes = await supabaseQuery(
    `gem_hunter_gems?url=eq.${encodeURIComponent(gemUrl)}&select=vote_count`
  )
  const gems = await countRes.json() as Array<{ vote_count: number }>
  return c.json({ ok: true, vote_count: gems[0]?.vote_count ?? 0 })
})

// GET /api/gems/trending — gems sorted by votes
app.get('/api/gems/trending', async (c) => {
  const err = requireSupabase(c)
  if (err) return err

  const limit = Math.min(parseInt(c.req.query('limit') ?? '20', 10), 50)
  const res = await supabaseQuery(
    `gem_hunter_gems?select=url,name,description,stars,language,max_score,vote_count&order=vote_count.desc,max_score.desc&limit=${limit}`
  )

  if (!res.ok) return c.json({ error: 'query failed' }, 500)
  return c.json(await res.json())
})

// GET /api/lists — public lists
app.get('/api/lists', async (c) => {
  const err = requireSupabase(c)
  if (err) return err

  const res = await supabaseQuery(
    'gem_lists?is_public=eq.true&select=id,name,slug,description,gem_count,created_at&order=gem_count.desc&limit=20'
  )
  if (!res.ok) return c.json({ error: 'query failed' }, 500)
  return c.json(await res.json())
})

// GET /api/lists/:slug — list + gems
app.get('/api/lists/:slug', async (c) => {
  const err = requireSupabase(c)
  if (err) return err

  const slug = c.req.param('slug')
  const res = await supabaseQuery(
    `gem_lists?slug=eq.${slug}&select=id,name,slug,description,gem_count,gem_list_items(gem_url,note,added_at)&limit=1`
  )
  if (!res.ok) return c.json({ error: 'query failed' }, 500)
  const data = await res.json() as unknown[]
  if (!data.length) return c.json({ error: 'not found' }, 404)
  return c.json(data[0])
})

// GET /api/health
app.get('/api/health', (c) => c.json({ ok: true, service: 'gem-hunter', port: PORT }))

// ── Static files ───────────────────────────────────────────────────────────────
app.get('/', serveStatic({ path: './public/index.html' }))
app.use('/*', serveStatic({ root: './public' }))
app.get('*', serveStatic({ path: './public/index.html' }))

console.log(`💎 Gem Hunter running on http://localhost:${PORT}`)

export default {
  port: PORT,
  fetch: app.fetch,
}
