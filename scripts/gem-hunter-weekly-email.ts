#!/usr/bin/env bun
/**
 * GH-076: Gem Hunter Weekly Email
 * Runs Thu 08:00 UTC — generates digest and sends to Telegram for manual Substack post
 *
 * Flow: query top gems → format Substack draft → Telegram HITL notification
 * HITL: Never auto-posts. Sends formatted draft + file to Telegram.
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs'
import { join } from 'path'

const DRY_RUN = process.argv.includes('--dry-run')
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? ''
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID ?? process.env.TELEGRAM_OWNER_ID ?? ''
const SUPABASE_URL = process.env.SUPABASE_URL ?? ''
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY ?? process.env.SUPABASE_ANON_KEY ?? ''

interface Gem {
  repo_name: string
  owner: string
  description: string | null
  stars: number
  language: string | null
  max_score: number
  topics: string[] | null
  html_url: string
  discovered_at: string
}

async function getTopGems(days = 7, limit = 5): Promise<Gem[]> {
  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.error('Missing Supabase credentials — set SUPABASE_URL + SUPABASE_ANON_KEY')
    return []
  }

  const since = new Date(Date.now() - days * 86_400_000).toISOString()
  const cols = 'repo_name,owner,description,stars,language,max_score,topics,html_url,discovered_at'
  const url = `${SUPABASE_URL}/rest/v1/gem_hunter_gems?select=${cols}&discovered_at=gte.${since}&order=max_score.desc&limit=${limit}`

  const res = await fetch(url, {
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      Accept: 'application/json',
    },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Supabase query failed (${res.status}): ${text}`)
  }

  return (await res.json()) as Gem[]
}

function formatSubstackDraft(gems: Gem[], weekLabel: string): string {
  const intro = `# Gem Hunter Weekly — ${weekLabel}

*${gems.length} repositórios de IA que você deveria conhecer antes de todo mundo.*

---`

  const gemSections = gems.map((gem, i) => {
    const score = Math.round(gem.max_score * 100) / 100
    const stars = gem.stars >= 1000 ? `${(gem.stars / 1000).toFixed(1)}k` : `${gem.stars}`
    const lang = gem.language ? ` · ${gem.language}` : ''
    const topics = (gem.topics ?? []).slice(0, 3).join(', ')

    return `## ${i + 1}. [${gem.owner}/${gem.repo_name}](${gem.html_url})

**Score: ${score}** · ⭐ ${stars}${lang}${topics ? ` · ${topics}` : ''}

${gem.description ?? 'Sem descrição.'}
`
  }).join('\n')

  const footer = `---

*Gerado automaticamente pelo [EGOS Gem Hunter](https://gemhunter.egos.ia.br)*`

  return `${intro}\n\n${gemSections}\n${footer}`
}

async function sendTelegram(text: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log('[telegram] credentials missing — skipping')
    return
  }

  const res = await fetch(
    `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      }),
    }
  )

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`Telegram API ${res.status}: ${body}`)
  }
}

async function sendTelegramDocument(filePath: string, filename: string, caption: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return

  const fileContent = await Bun.file(filePath).text()
  const formData = new FormData()
  formData.append('chat_id', TELEGRAM_CHAT_ID)
  formData.append('document', new Blob([fileContent], { type: 'text/markdown' }), filename)
  formData.append('caption', caption)

  const res = await fetch(
    `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument`,
    { method: 'POST', body: formData }
  )

  if (!res.ok) {
    console.warn('[telegram] document send failed:', res.status)
  }
}

async function main() {
  const now = new Date()
  const weekLabel = now.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
  const slug = now.toISOString().slice(0, 10)
  const filename = `gem-hunter-weekly-${slug}.md`

  console.log(`💎 Gem Hunter Weekly Email — ${weekLabel}`)
  console.log(`   dry-run: ${DRY_RUN}`)

  let gems: Gem[] = []
  try {
    gems = await getTopGems(7, 5)
  } catch (err) {
    console.error('Failed to fetch gems:', err)
  }

  if (gems.length === 0) {
    console.log('No gems found for this week.')
    if (!DRY_RUN) {
      await sendTelegram(`💎 Gem Hunter Weekly — ${weekLabel}\n\nNenhum gem encontrado esta semana.`)
    }
    return
  }

  const draft = formatSubstackDraft(gems, weekLabel)

  // Save draft locally
  const docsDir = join(import.meta.dir, '../docs/gem-hunter')
  if (!existsSync(docsDir)) mkdirSync(docsDir, { recursive: true })
  const draftPath = join(docsDir, filename)
  writeFileSync(draftPath, draft, 'utf8')
  console.log(`✅ Draft saved: docs/gem-hunter/${filename}`)

  if (DRY_RUN) {
    console.log('\n--- Draft preview (first 400 chars) ---')
    console.log(draft.slice(0, 400))
    console.log(`\n${gems.length} gems found for ${weekLabel}`)
    return
  }

  // Telegram HITL notification
  const gemList = gems
    .map((g, i) => `${i + 1}. <b>${g.owner}/${g.repo_name}</b> ⭐${g.stars} (score: ${g.max_score.toFixed(2)})`)
    .join('\n')

  const telegramMsg = `💎 <b>Gem Hunter Weekly — ${weekLabel}</b>

${gems.length} gems prontos para publicação:
${gemList}

📄 Draft Substack enviado abaixo.
Copie o markdown e poste em: <a href="https://substack.com/new-post">substack.com/new-post</a>`

  await sendTelegram(telegramMsg)
  await sendTelegramDocument(draftPath, filename, '📄 Draft Substack — copie e cole no editor')
  console.log('✅ Telegram notification + draft sent')
}

main().catch((err) => {
  console.error('Fatal:', err)
  process.exit(1)
})
