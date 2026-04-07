#!/usr/bin/env bun
// 🔔 X Opportunity Alert System
// 
// Monitora X.com por oportunidades relevantes usando cota gratuita da API
// Envia alertas via WhatsApp/Telegram quando encontra posts/DMs candidatos
// 
// Cota X API (Free tier):
// - 500 posts/month read (≈ 16/dia)
// - 500 posts/month write (≈ 16/dia)
// - 10 searches/15min (≈ 960/dia)
// 
// Estratégia: Busca a cada 2h (12x/dia), máx 10 queries/run = 120 buscas/dia
// Alertas: imediatos via WhatsApp/Telegram para aprovação manual
// 
// Deploy: VPS cron "0 */2 * * *" (a cada 2h)
// 
// Usage:
//   bun scripts/x-opportunity-alert.ts              # run (dry-run if no keys)
//   bun scripts/x-opportunity-alert.ts --dry-run    # never sends, only logs
//   bun scripts/x-opportunity-alert.ts --test-alert   # test WhatsApp/Telegram

import { writeFileSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const DRY_RUN = process.argv.includes("--dry-run") || !process.env.X_BEARER_TOKEN;
const TEST_ALERT = process.argv.includes("--test-alert");
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? "";
const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL ?? ""; // WhatsApp via Evolution API
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY ?? "";
const WHATSAPP_INSTANCE = process.env.WHATSAPP_INSTANCE ?? "egos-alerts";
const STATE_FILE = "/tmp/x-opportunity-state.json";

// ── Rate Limiting ─────────────────────────────────────────────────────────

interface OpportunityState {
  date: string;
  searches_today: number;
  alerts_sent: number;
  last_search_time: string;
  candidates_found: Candidate[];
}

interface Candidate {
  id: string;
  author: string;
  text: string;
  url: string;
  category: string;
  priority: "P0" | "P1" | "P2";
  product_match: string;
  template_suggestion: string;
  found_at: string;
  status: "new" | "alerted" | "approved" | "rejected" | "sent";
}

const MAX_SEARCHES_PER_DAY = 120; // 10 queries × 12 runs
const MAX_ALERTS_PER_DAY = 20;
const MAX_CANDIDATES_STORED = 50;

function loadState(): OpportunityState {
  const today = new Date().toISOString().slice(0, 10);
  if (existsSync(STATE_FILE)) {
    try {
      const s = JSON.parse(readFileSync(STATE_FILE, "utf8")) as OpportunityState;
      if (s.date === today) return s;
    } catch { }
  }
  return {
    date: today,
    searches_today: 0,
    alerts_sent: 0,
    last_search_time: "",
    candidates_found: [],
  };
}

function saveState(s: OpportunityState) {
  writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
}

// ── Search Queries — Oportunidades de Negócio ──────────────────────────────

interface SearchQuery {
  query: string;
  category: string;
  priority: "P0" | "P1" | "P2";
  product_match: string;
  template_suggestion: string;
  min_likes?: number;
  lang?: string;
}

const OPPORTUNITY_QUERIES: SearchQuery[] = [
  // P0 — Alta prioridade (parceiros potenciais)
  {
    query: '"procuro parceiro técnico" OR "preciso de CTO" OR "procuro co-fundador" Brasil',
    category: "parceria_tecnica",
    priority: "P0",
    product_match: "EGOS produtos",
    template_suggestion: "4K — Procuro parceiro técnico",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '"procuro vendedor" OR "procuro parceiro comercial" SaaS OR software',
    category: "parceria_comercial",
    priority: "P0",
    product_match: "Todos",
    template_suggestion: "4O — Cansado de trabalhar sozinho",
    min_likes: 3,
    lang: "pt",
  },

  // P0 — LGPD/Compliance (Guard Brasil)
  {
    query: 'consultor LGPD "proteção de dados" OR "DPO" Brasil contratar',
    category: "lgpd_consultor",
    priority: "P0",
    product_match: "Guard Brasil",
    template_suggestion: "4B — LGPD/compliance",
    min_likes: 5,
    lang: "pt",
  },
  {
    query: 'vazamento dados Brasil OR "vazou CPF" OR breach "dados pessoais"',
    category: "vazamento_dados",
    priority: "P0",
    product_match: "Guard Brasil",
    template_suggestion: "4G — Vazamento de dados",
    min_likes: 10,
    lang: "pt",
  },

  // P1 — GovTech/Licitações (Eagle Eye)
  {
    query: 'licitação software OR "pregão eletrônico" TI OR govtech Brasil',
    category: "licitacao_ti",
    priority: "P1",
    product_match: "Eagle Eye",
    template_suggestion: "4C — GovTech/licitações",
    min_likes: 5,
    lang: "pt",
  },
  {
    query: '"software house" prospectar governo OR "B2G" Brasil',
    category: "software_house_b2g",
    priority: "P1",
    product_match: "Eagle Eye",
    template_suggestion: "4H — Software house",
    min_likes: 3,
    lang: "pt",
  },

  // P1 — Split Payment/Fiscal (Carteira Livre)
  {
    query: '"split payment" Brasil 2026 OR marketplace fiscal OR "nota fiscal destinatário"',
    category: "split_payment",
    priority: "P1",
    product_match: "Carteira Livre",
    template_suggestion: "4F — Split payment",
    min_likes: 5,
    lang: "pt",
  },
  {
    query: '"marketplace" desenvolvimento OR "plataforma digital" pagamento Brasil',
    category: "marketplace_dev",
    priority: "P1",
    product_match: "Carteira Livre",
    template_suggestion: "4F — Marketplace",
    min_likes: 5,
    lang: "pt",
  },

  // P1 — HealthTech/Recruiting (Guard Brasil)
  {
    query: 'healthtech Brasil startup OR telemedicina compliance LGPD',
    category: "healthtech",
    priority: "P1",
    product_match: "Guard Brasil",
    template_suggestion: "4R — HealthTech",
    min_likes: 5,
    lang: "pt",
  },
  {
    query: '"RH tech" OR recruiting tech OR ATS Brasil startup',
    category: "rh_tech",
    priority: "P1",
    product_match: "Guard Brasil",
    template_suggestion: "4Q — RH tech",
    min_likes: 5,
    lang: "pt",
  },

  // P2 — Builders/Dev (EGOS Kernel)
  {
    query: '"multi-agent framework" OR "agent governance" open source lang:en',
    category: "agent_framework",
    priority: "P2",
    product_match: "EGOS Kernel",
    template_suggestion: "4P — Head de produto/dívida técnica",
    min_likes: 10,
    lang: "en",
  },
];

// ── X API Search ───────────────────────────────────────────────────────────

async function searchX(query: string, maxResults: number = 10): Promise<any[]> {
  const bearerToken = process.env.X_BEARER_TOKEN;
  if (!bearerToken) {
    console.error("❌ X_BEARER_TOKEN não configurado");
    return [];
  }

  try {
    const response = await fetch(
      `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${maxResults}&tweet.fields=author_id,public_metrics,created_at,lang&expansions=author_id&user.fields=username,name`,
      {
        headers: {
          Authorization: `Bearer ${bearerToken}`,
        },
      }
    );

    if (!response.ok) {
      console.error(`❌ X API error: ${response.status} ${await response.text()}`);
      return [];
    }

    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.error("❌ Erro na busca X:", error);
    return [];
  }
}

// ── Alert Senders ─────────────────────────────────────────────────────────

async function sendTelegramAlert(candidate: Candidate): Promise<boolean> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("⚠️ Telegram não configurado");
    return false;
  }

  const message = `
🚨 <b>Oportunidade ${candidate.priority} — X.com</b>

<b>Categoria:</b> ${candidate.category}
<b>Produto:</b> ${candidate.product_match}
<b>Template:</b> ${candidate.template_suggestion}

<b>Autor:</b> @${candidate.author}
<b>Post:</b> ${candidate.text.slice(0, 200)}${candidate.text.length > 200 ? "..." : ""}

🔗 <a href="${candidate.url}">Ver no X</a>

✅ Aprovar: Responda /approve ${candidate.id}
❌ Rejeitar: Responda /reject ${candidate.id}
  `.trim();

  try {
    const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: "HTML",
        disable_web_page_preview: false,
      }),
    });

    return response.ok;
  } catch (error) {
    console.error("❌ Erro Telegram:", error);
    return false;
  }
}

async function sendWhatsAppAlert(candidate: Candidate): Promise<boolean> {
  if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
    console.log("⚠️ WhatsApp (Evolution API) não configurado");
    return false;
  }

  // Primeiro, obter contatos da instância
  try {
    const contactsResponse = await fetch(
      `${EVOLUTION_API_URL}/chat/findContacts/${WHATSAPP_INSTANCE}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: EVOLUTION_API_KEY,
        },
        body: JSON.stringify({
          where: {
            key: {
              remoteJid: process.env.WHATSAPP_ALERT_NUMBER + "@s.whatsapp.net",
            },
          },
        }),
      }
    );

    // Enviar mensagem
    const message = `*Oportunidade ${candidate.priority} — X.com*

Categoria: ${candidate.category}
Produto: ${candidate.product_match}
Template: ${candidate.template_suggestion}

Autor: @${candidate.author}
Post: ${candidate.text.slice(0, 150)}${candidate.text.length > 150 ? "..." : ""}

Ver: ${candidate.url}`;

    const sendResponse = await fetch(
      `${EVOLUTION_API_URL}/message/sendText/${WHATSAPP_INSTANCE}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: EVOLUTION_API_KEY,
        },
        body: JSON.stringify({
          number: process.env.WHATSAPP_ALERT_NUMBER,
          text: message,
        }),
      }
    );

    return sendResponse.ok;
  } catch (error) {
    console.error("❌ Erro WhatsApp:", error);
    return false;
  }
}

// ── Main Execution ─────────────────────────────────────────────────────────

async function main() {
  console.log("🔔 X Opportunity Alert System");
  console.log(`Modo: ${DRY_RUN ? "DRY-RUN (não envia)" : "LIVE"}`);

  const state = loadState();
  console.log(`\n📊 Estado hoje: ${state.searches_today}/${MAX_SEARCHES_PER_DAY} buscas, ${state.alerts_sent}/${MAX_ALERTS_PER_DAY} alertas`);

  // Test mode
  if (TEST_ALERT) {
    console.log("\n🧪 Modo de teste — enviando alerta de teste...");
    const testCandidate: Candidate = {
      id: "test-001",
      author: "testuser",
      text: "Este é um teste do sistema de alertas X.com. Procuro parceiro técnico para projeto SaaS.",
      url: "https://x.com/testuser/status/1234567890",
      category: "test",
      priority: "P0",
      product_match: "Test",
      template_suggestion: "4K",
      found_at: new Date().toISOString(),
      status: "new",
    };

    const telegramOk = await sendTelegramAlert(testCandidate);
    const whatsappOk = await sendWhatsAppAlert(testCandidate);

    console.log(`\n📱 Telegram: ${telegramOk ? "✅ OK" : "❌ Falha"}`);
    console.log(`📱 WhatsApp: ${whatsappOk ? "✅ OK" : "❌ Falha"}`);
    return;
  }

  if (DRY_RUN) {
    console.log("\n⚠️ Modo DRY-RUN — simulando buscas...");
  }

  // Check rate limits
  if (state.searches_today >= MAX_SEARCHES_PER_DAY) {
    console.log("\n⛔ Limite diário de buscas atingido. Aguardando amanhã.");
    return;
  }

  // Search for opportunities
  console.log("\n🔍 Buscando oportunidades...");
  const newCandidates: Candidate[] = [];

  for (const q of OPPORTUNITY_QUERIES) {
    if (state.searches_today >= MAX_SEARCHES_PER_DAY) break;
    if (state.alerts_sent >= MAX_ALERTS_PER_DAY) break;

    console.log(`\n  → ${q.category} (${q.priority})`);

    if (!DRY_RUN) {
      const tweets = await searchX(q.query, 10);
      state.searches_today++;

      for (const tweet of tweets) {
        // Check if already processed
        const existing = state.candidates_found.find(c => c.id === tweet.id);
        if (existing) continue;

        // Check min likes
        const likes = tweet.public_metrics?.like_count || 0;
        if (likes < (q.min_likes || 0)) continue;

        // Check if author looks relevant (not a bot, has followers)
        // Simplified check — could be enhanced

        const candidate: Candidate = {
          id: tweet.id,
          author: tweet.username || "unknown",
          text: tweet.text,
          url: `https://x.com/${tweet.username}/status/${tweet.id}`,
          category: q.category,
          priority: q.priority,
          product_match: q.product_match,
          template_suggestion: q.template_suggestion,
          found_at: new Date().toISOString(),
          status: "new",
        };

        newCandidates.push(candidate);
        state.candidates_found.push(candidate);

        // Send alert
        if (state.alerts_sent < MAX_ALERTS_PER_DAY) {
          const telegramOk = await sendTelegramAlert(candidate);
          const whatsappOk = await sendWhatsAppAlert(candidate);

          if (telegramOk || whatsappOk) {
            candidate.status = "alerted";
            state.alerts_sent++;
            console.log(`    ✅ Alerta enviado: @${candidate.author} (${q.priority})`);
          } else {
            console.log(`    ⚠️ Falha no alerta: @${candidate.author}`);
          }
        }

        // Keep only recent candidates
        if (state.candidates_found.length > MAX_CANDIDATES_STORED) {
          state.candidates_found = state.candidates_found.slice(-MAX_CANDIDATES_STORED);
        }
      }
    } else {
      console.log(`    [DRY-RUN] Simulando busca: ${q.query.slice(0, 50)}...`);
    }
  }

  // Save state
  state.last_search_time = new Date().toISOString();
  saveState(state);

  // Summary
  console.log("\n" + "=".repeat(50));
  console.log("📊 RESUMO DA EXECUÇÃO");
  console.log("=".repeat(50));
  console.log(`Buscas hoje: ${state.searches_today}/${MAX_SEARCHES_PER_DAY}`);
  console.log(`Alertas enviados hoje: ${state.alerts_sent}/${MAX_ALERTS_PER_DAY}`);
  console.log(`Novos candidatos: ${newCandidates.length}`);
  console.log(`Total em fila: ${state.candidates_found.length}`);

  if (newCandidates.length > 0) {
    console.log("\n🎯 NOVAS OPORTUNIDADES:");
    for (const c of newCandidates) {
      console.log(`  ${c.priority} | ${c.category} | @${c.author} | ${c.template_suggestion}`);
    }
  }

  console.log("\n✅ Execução concluída");
}

// Run
main().catch(console.error);
