import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'

const app = new Hono()
const PORT = parseInt(process.env.PORT ?? '3070', 10)

// Root → index.html
app.get('/', serveStatic({ path: './public/index.html' }))

// Serve all static files from /public directory
app.use('/*', serveStatic({ root: './public' }))

// Fallback for any other route → index.html (SPA-style)
app.get('*', serveStatic({ path: './public/index.html' }))

console.log(`💎 Gem Hunter landing running on http://localhost:${PORT}`)

export default {
  port: PORT,
  fetch: app.fetch,
}
