#!/usr/bin/env bun
// 🔔 X Opportunity Alert System v2 — OSINT/Moat Focused
//
// Monitora X.com por oportunidades alinhadas ao moat EGOS
// Envia alertas via WhatsApp/Telegram quando encontra posts candidatos
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
const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL ?? "";
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY ?? "";
const WHATSAPP_INSTANCE = process.env.WHATSAPP_INSTANCE ?? "egos-alerts";
const STATE_FILE = "/tmp/x-opportunity-state.json";
const DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const DASHSCOPE_BASE_URL = process.env.ALIBABA_DASHSCOPE_BASE_URL ?? "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? "";

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
  status: "new" | "alerted" | "replied" | "archived" | "rejected";
}

const MAX_SEARCHES_PER_DAY = 100;
const MAX_ALERTS_PER_DAY = 10;
const MAX_CANDIDATES_STORED = 200;

function loadState(): OpportunityState {
  if (!existsSync(STATE_FILE)) {
    return {
      date: new Date().toISOString().slice(0, 10),
      searches_today: 0,
      alerts_sent: 0,
      last_search_time: new Date().toISOString(),
      candidates_found: [],
    };
  }

  try {
    const raw = JSON.parse(readFileSync(STATE_FILE, "utf8"));
    const today = new Date().toISOString().slice(0, 10);

    if (raw.date !== today) {
      raw.date = today;
      raw.searches_today = 0;
      raw.alerts_sent = 0;
    }

    return raw;
  } catch {
    return {
      date: new Date().toISOString().slice(0, 10),
      searches_today: 0,
      alerts_sent: 0,
      last_search_time: new Date().toISOString(),
      candidates_found: [],
    };
  }
}

function saveState(state: OpportunityState) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// ── Search Queries — MOAT Focused ───────────────────────────────────────────

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
  // ═══════════════════════════════════════════════════════════════════════════
  // P0 — MOAT PRINCIPAL: OSINT & Intelligence (852, Guard Brasil Forense)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    query: "(OSINT OR osint OR \"inteligência de fontes abertas\") Brasil lang:pt",
    category: "osint_core",
    priority: "P0",
    product_match: "852 / Guard Brasil",
    template_suggestion: "OSINT-1 — Ferramenta de investigação",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '("cruzamento de dados" OR "cross reference" OR "análise forense") Brasil lang:pt',
    category: "investigacao_dados",
    priority: "P0",
    product_match: "852",
    template_suggestion: "OSINT-2 — Cruzamento automático",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '(investigação OR investigações OR inteligência) (digital OR cibercrime OR forense) Brasil lang:pt',
    category: "investigacao_digital",
    priority: "P0",
    product_match: "852",
    template_suggestion: "OSINT-3 — Plataforma policial",
    min_likes: 5,
    lang: "pt",
  },
  {
    query: '"análise de redes sociais" OR "monitoramento digital" OR "rastreamento online" Brasil lang:pt',
    category: "monitoramento_digital",
    priority: "P0",
    product_match: "852",
    template_suggestion: "OSINT-4 — Monitoramento",
    min_likes: 3,
    lang: "pt",
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // P0 — MOAT: AI + Automação + Frameworks (EGOS Kernel)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    query: '("multi-agent" OR "agent framework" OR "AI orchestration") (github OR open source) lang:en',
    category: "agent_framework",
    priority: "P0",
    product_match: "EGOS Kernel",
    template_suggestion: "AI-1 — Framework multi-agent",
    min_likes: 5,
    lang: "en",
  },
  {
    query: '"agent governance" OR "orquestração de agentes" OR "AI automation" lang:en',
    category: "ai_governance",
    priority: "P0",
    product_match: "EGOS Kernel",
    template_suggestion: "AI-2 — Governança de agentes",
    min_likes: 5,
    lang: "en",
  },
  {
    query: '(LLM workflow OR "LLM pipeline") (automation OR framework) lang:en',
    category: "llm_automation",
    priority: "P0",
    product_match: "EGOS Kernel",
    template_suggestion: "AI-3 — Pipeline LLM",
    min_likes: 5,
    lang: "en",
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // P1 — GovTech + Dados Abertos + Automação (Eagle Eye)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    query: '(govtech OR "dados abertos" OR transparência) (automação OR IA OR software) Brasil lang:pt',
    category: "govtech_automacao",
    priority: "P1",
    product_match: "Eagle Eye",
    template_suggestion: "GOV-1 — GovTech automação",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '"licitação" (inteligência artificial OR IA OR software) Brasil lang:pt',
    category: "licitacao_ia",
    priority: "P1",
    product_match: "Eagle Eye",
    template_suggestion: "GOV-2 — Licitações + IA",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '("monitorar contratos" OR "transparência pública") automação Brasil lang:pt',
    category: "transparencia_automacao",
    priority: "P1",
    product_match: "Eagle Eye",
    template_suggestion: "GOV-3 — Transparência",
    min_likes: 3,
    lang: "pt",
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // P1 — LGPD Forense + Compliance Investigativo (Guard Brasil)
  // ═══════════════════════════════════════════════════════════════════════════
  {
    query: '(LGPD OR compliance) (forense OR investigação OR PII) Brasil lang:pt',
    category: "lgpd_forense",
    priority: "P1",
    product_match: "Guard Brasil",
    template_suggestion: "LGPD-1 — Forense",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '"proteção de dados" (investigação OR relatório OR forense) Brasil lang:pt',
    category: "protecao_dados_forense",
    priority: "P1",
    product_match: "Guard Brasil",
    template_suggestion: "LGPD-2 — Proteção em investigações",
    min_likes: 3,
    lang: "pt",
  },
  {
    query: '"vazamento de dados" (análise OR investigação OR cruzamento) Brasil lang:pt',
    category: "vazamento_analise",
    priority: "P1",
    product_match: "Guard Brasil",
    template_suggestion: "LGPD-3 — Análise de vazamentos",
    min_likes: 5,
    lang: "pt",
  },
];

// ── Anti-Keyword Filter & Relevance Scoring ────────────────────────────────

const ANTI_KEYWORDS = [
  // Cursos/educação (está vendendo, não precisa de produto)
  "curso de", "mentoria", "sou coach", "aprenda a", "aula de", "workshop de",
  // Marketing genérico
  "marketing digital", "dropshipping", "day trade", "trader", "forex",
  // Contratação (não é parceria)
  "estou contratando", "vaga de emprego", "procuro estagiário", "clt",
  // Conteúdo viral/genérico
  "siga que eu sigo", "sdv", "follow back",
];

const MOAT_KEYWORDS = {
  osint: ["osint", "inteligência de fontes abertas", "cruzamento de dados", "investigação digital", "forense", "análise forense"],
  ai_framework: ["multi-agent", "agent framework", "ai orchestration", "llm workflow", "agent governance", "orquestração"],
  govtech: ["govtech", "dados abertos", "transparência", "licitação", "controle social", "monitorar contratos"],
  security: ["lgpd", "compliance", "proteção de dados", "vazamento", "breach", "pii"],
};

function isRelevantPost(text: string, category: string): { relevant: boolean; score: number; reasons: string[] } {
  const lowerText = text.toLowerCase();
  const reasons: string[] = [];
  let score = 50; // Base score

  // Check anti-keywords (penalty)
  for (const anti of ANTI_KEYWORDS) {
    if (lowerText.includes(anti.toLowerCase())) {
      score -= 30;
      reasons.push(`❌ anti: ${anti}`);
    }
  }

  // Check moat keywords (bonus)
  for (const [moatCategory, keywords] of Object.entries(MOAT_KEYWORDS)) {
    for (const kw of keywords) {
      if (lowerText.includes(kw.toLowerCase())) {
        score += 20;
        reasons.push(`✅ moat: ${kw}`);
      }
    }
  }

  // Category-specific bonuses
  if (category.includes("osint") && /\b(osint|investigação|cruzamento|forense)\b/i.test(text)) {
    score += 15;
    reasons.push("✅ OSINT match");
  }

  if (category.includes("agent") && /\b(agent|ai|automation|llm|framework)\b/i.test(text)) {
    score += 15;
    reasons.push("✅ AI match");
  }

  // Cap score
  score = Math.max(0, Math.min(100, score));

  return { relevant: score >= 60, score, reasons };
}

// ── Feedback Learning System ────────────────────────────────────────────────

const FEEDBACK_FILE = "/tmp/x-feedback-state.json";

interface FeedbackRecord {
  candidateId: string;
  tweetId: string;
  category: string;
  queryUsed: string;
  relevanceScore: number;
  action: "alerted" | "approved" | "rejected" | "ignored";
  timestamp: string;
}

function loadFeedback(): FeedbackRecord[] {
  if (!existsSync(FEEDBACK_FILE)) return [];
  try {
    return JSON.parse(readFileSync(FEEDBACK_FILE, "utf8"));
  } catch {
    return [];
  }
}

function saveFeedback(feedback: FeedbackRecord[]) {
  writeFileSync(FEEDBACK_FILE, JSON.stringify(feedback, null, 2));
}

function recordFeedback(candidate: Candidate, query: SearchQuery, relevanceScore: number, action: FeedbackRecord["action"]) {
  const feedback = loadFeedback();
  feedback.push({
    candidateId: candidate.id,
    tweetId: candidate.id,
    category: candidate.category,
    queryUsed: query.query,
    relevanceScore,
    action,
    timestamp: new Date().toISOString(),
  });
  saveFeedback(feedback.slice(-100));
}

function getQueryPerformance(query: string): { avgScore: number; count: number } {
  const feedback = loadFeedback();
  const relevant = feedback.filter(f => f.queryUsed === query);
  if (relevant.length === 0) return { avgScore: 50, count: 0 };
  const avg = relevant.reduce((sum, f) => sum + f.relevanceScore, 0) / relevant.length;
  return { avgScore: avg, count: relevant.length };
}

// ── X API Search ───────────────────────────────────────────────────────────

async function searchX(query: string, maxResults: number = 10): Promise<any[]> {
  const bearerToken = process.env.X_BEARER_TOKEN;
  if (!bearerToken) {
    console.error("❌ X_BEARER_TOKEN não configurado");
    return [];
  }

  try {
    const url = new URL("https://api.twitter.com/2/tweets/search/recent");
    url.searchParams.set("query", query);
    url.searchParams.set("max_results", String(maxResults));
    url.searchParams.set("tweet.fields", "public_metrics,author_id,created_at");
    url.searchParams.set("expansions", "author_id");
    url.searchParams.set("user.fields", "username,public_metrics");

    const response = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${bearerToken}` },
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌ X API error: ${response.status} ${error}`);
      return [];
    }

    const data = await response.json();
    const users = data.includes?.users || [];
    const tweets = data.data || [];

    return tweets.map((tweet: any) => {
      const user = users.find((u: any) => u.id === tweet.author_id);
      return {
        id: tweet.id,
        text: tweet.text,
        username: user?.username || "unknown",
        created_at: tweet.created_at,
        public_metrics: tweet.public_metrics || {},
        user_metrics: user?.public_metrics || {},
      };
    });
  } catch (error) {
    console.error("❌ Erro na busca X:", error);
    return [];
  }
}

// ── LLM Analysis (DashScope qwen-plus → OpenRouter fallback) ──────────────

interface AIAnalysis {
  summary: string;      // 1-line pt-BR
  diagnosis: string;    // 2-3 sentences with context
  recommendation: "vale" | "nao_vale" | "incerto";
  fit_score: number;    // 0-100
  provider: string;
}

async function analyzeWithLLM(candidate: Candidate): Promise<AIAnalysis | null> {
  const prompt = `Analise esta oportunidade encontrada no X.com para a empresa EGOS (plataforma de agentes IA + Guard Brasil - proteção de dados LGPD).

Post de @${candidate.author}:
"${candidate.text.slice(0, 400)}"

Categoria detectada: ${candidate.category}
Produto EGOS relevante: ${candidate.product_match}

Responda em JSON com exatamente estes campos:
{
  "summary": "<1 linha em pt-BR resumindo o post e oportunidade>",
  "diagnosis": "<2-3 frases: contexto do autor, dor identificada, como EGOS pode ajudar>",
  "recommendation": "<vale|nao_vale|incerto>",
  "fit_score": <0-100 fit com EGOS>
}`;

  const body = JSON.stringify({
    model: "qwen-plus",
    messages: [{ role: "user", content: prompt }],
    max_tokens: 300,
    temperature: 0.3,
  });

  // Primary: Alibaba DashScope
  if (DASHSCOPE_API_KEY) {
    try {
      const res = await fetch(`${DASHSCOPE_BASE_URL}/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${DASHSCOPE_API_KEY}` },
        body,
        signal: AbortSignal.timeout(10000),
      });
      if (res.ok) {
        const data = await res.json() as { choices?: { message?: { content?: string } }[] };
        const content = data.choices?.[0]?.message?.content ?? "";
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]) as Omit<AIAnalysis, "provider">;
          return { ...parsed, fit_score: Math.min(100, Math.max(0, Number(parsed.fit_score) || 0)), provider: "alibaba/qwen-plus" };
        }
      }
    } catch {
      // fall through to OpenRouter
    }
  }

  // Fallback: OpenRouter free
  if (OPENROUTER_API_KEY) {
    try {
      const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${OPENROUTER_API_KEY}` },
        body: JSON.stringify({ ...JSON.parse(body), model: "google/gemma-4-26b-a4b-it:free" }),
        signal: AbortSignal.timeout(15000),
      });
      if (res.ok) {
        const data = await res.json() as { choices?: { message?: { content?: string } }[] };
        const content = data.choices?.[0]?.message?.content ?? "";
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]) as Omit<AIAnalysis, "provider">;
          return { ...parsed, fit_score: Math.min(100, Math.max(0, Number(parsed.fit_score) || 0)), provider: "openrouter/gemma-4-26b" };
        }
      }
    } catch {
      // no LLM available
    }
  }

  return null;
}

// ── Telegram Alerts ────────────────────────────────────────────────────────

async function sendTelegramAlert(candidate: Candidate, analysis?: AIAnalysis | null): Promise<boolean> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.log("⚠️ Telegram não configurado");
    return false;
  }

  try {
    const recEmoji = analysis?.recommendation === "vale" ? "✅" : analysis?.recommendation === "nao_vale" ? "❌" : "⚠️";
    const aiBlock = analysis
      ? `\n\n🤖 <b>Análise IA</b> (${analysis.provider})
<b>Resumo:</b> ${analysis.summary}
<b>Contexto:</b> ${analysis.diagnosis}
${recEmoji} <b>Recomendação:</b> ${analysis.recommendation.replace("_", " ")} | fit ${analysis.fit_score}/100`
      : "";

    const message = `🔔 <b>Oportunidade ${candidate.priority} — X.com</b>

<b>Categoria:</b> ${candidate.category}
<b>Produto:</b> ${candidate.product_match}
<b>Template:</b> ${candidate.template_suggestion}

<b>Autor:</b> @${candidate.author}
<b>Post:</b> ${candidate.text.slice(0, 200)}${candidate.text.length > 200 ? "..." : ""}${aiBlock}

🔗 <a href="${candidate.url}">Ver no X</a>`;

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

  try {
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
  console.log("🔔 X Opportunity Alert System v2 — OSINT/Moat Focused");
  console.log(`Modo: ${DRY_RUN ? "DRY-RUN (não envia)" : "LIVE"}`);

  const state = loadState();
  console.log(`\n📊 Estado atual: ${state.searches_today}/${MAX_SEARCHES_PER_DAY} buscas, ${state.alerts_sent}/${MAX_ALERTS_PER_DAY} alertas`);

  if (TEST_ALERT) {
    console.log("\n🧪 Teste de alertas...");
    const testCandidate: Candidate = {
      id: "test-123",
      author: "test_user",
      text: "Teste de alerta do sistema X Opportunity",
      url: "https://x.com/test",
      category: "test",
      priority: "P0",
      product_match: "Test",
      template_suggestion: "Test template",
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

        // 🧠 RELEVANCE SCORING — Moat-aligned filtering
        const relevance = isRelevantPost(tweet.text, q.category);
        console.log(`    📝 @${tweet.username}: ${relevance.score}/100 ${relevance.relevant ? "✅" : "❌"}`);
        if (relevance.reasons.length > 0) console.log(`       ${relevance.reasons.slice(0, 2).join(" | ")}`);

        // Skip if not relevant
        if (!relevance.relevant) {
          recordFeedback({ id: tweet.id, author: tweet.username || "unknown", text: tweet.text, url: "", category: q.category, priority: q.priority, product_match: q.product_match, template_suggestion: q.template_suggestion, found_at: new Date().toISOString(), status: "rejected" }, q, relevance.score, "rejected");
          continue;
        }

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
          const aiAnalysis = await analyzeWithLLM(candidate);
          if (aiAnalysis) {
            console.log(`    🤖 IA: ${aiAnalysis.recommendation} (fit ${aiAnalysis.fit_score}/100) via ${aiAnalysis.provider}`);
          }
          const telegramOk = await sendTelegramAlert(candidate, aiAnalysis);
          const whatsappOk = await sendWhatsAppAlert(candidate);

          if (telegramOk || whatsappOk) {
            candidate.status = "alerted";
            state.alerts_sent++;
            recordFeedback(candidate, q, relevance.score, "alerted");
            console.log(`    ✅ Alerta: @${candidate.author} (${q.priority}, ${relevance.score}pts)`);
          } else {
            console.log(`    ⚠️ Falha: @${candidate.author}`);
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
  saveState(state);

  // Summary
  console.log("\n" + "=".repeat(50));
  console.log(`✅ Buscas hoje: ${state.searches_today}/${MAX_SEARCHES_PER_DAY}`);
  console.log(`📢 Alertas hoje: ${state.alerts_sent}/${MAX_ALERTS_PER_DAY}`);
  console.log(`📊 Candidatos encontrados: ${newCandidates.length}`);
  console.log(`📁 Total armazenado: ${state.candidates_found.length}`);
  console.log("=".repeat(50));

  // Performance report
  console.log("\n📈 Performance das queries:");
  for (const q of OPPORTUNITY_QUERIES) {
    const perf = getQueryPerformance(q.query);
    if (perf.count > 0) {
      console.log(`   ${q.category}: ${perf.avgScore.toFixed(1)} avg (${perf.count} samples)`);
    }
  }
}

main().catch(console.error);
