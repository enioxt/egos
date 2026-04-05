/**
 * EGOS Gateway — AI Orchestrator
 *
 * Shared LLM orchestration layer for WhatsApp + Telegram chatbots.
 * Uses Qwen (Alibaba DashScope) for text, Groq Whisper for audio,
 * and Qwen-VL for images.
 *
 * Tool set: gem_search, wiki_search, system_status, list_agents,
 *           get_costs, guard_status, knowledge_stats
 */

import { join } from "path";
import { existsSync, readFileSync } from "fs";

// ─── Config ───────────────────────────────────────────────────────────────────

const DASHSCOPE_BASE = process.env.ALIBABA_DASHSCOPE_BASE_URL
  ?? "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const DASHSCOPE_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const GROQ_KEY = process.env.GROQ_API_KEY ?? "";
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const GUARD_URL = "https://guard.egos.ia.br";
const GATEWAY_PORT = process.env.GATEWAY_PORT ?? "3000";
const GATEWAY_BASE = `http://localhost:${GATEWAY_PORT}`;

const ROOT = join(import.meta.dir, "../../..");

// ─── Types ────────────────────────────────────────────────────────────────────

export type MediaType = "audio" | "image" | "video" | "document" | "sticker";

export interface IncomingMessage {
  from: string;           // sender identifier
  channel: "whatsapp" | "telegram";
  text?: string;          // for text messages
  mediaType?: MediaType;  // for media messages
  mediaBase64?: string;   // base64 encoded media (for audio/image)
  mediaMime?: string;     // mimetype (audio/ogg, image/jpeg, etc.)
  mediaUrl?: string;      // direct URL if available
  caption?: string;       // caption for media messages
  fileName?: string;      // for documents
}

export interface OrchestratorResponse {
  text: string;
  toolsUsed?: string[];
}

// ─── Supabase helper ──────────────────────────────────────────────────────────

async function sbFetch(path: string): Promise<unknown> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return null;
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` },
    signal: AbortSignal.timeout(5000),
  });
  if (!res.ok) return null;
  return res.json();
}

// ─── Tool implementations ─────────────────────────────────────────────────────

async function toolGemSearch(query: string, sector?: string): Promise<string> {
  try {
    const url = sector
      ? `${GATEWAY_BASE}/gem-hunter/sector/${sector}`
      : `${GATEWAY_BASE}/gem-hunter/latest?limit=5`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return "Gem Hunter sem dados ainda. Execute: bun agent:run gem-hunter --exec";
    const data = await res.json() as { gems?: Array<{ name: string; description: string; url: string; score?: number }> };
    const gems = data.gems?.slice(0, 5) ?? [];
    if (gems.length === 0) return "Nenhum gem encontrado para esse critério.";
    return gems.map((g, i) =>
      `${i + 1}. *${g.name}* (score: ${g.score ?? "?"})\\n   ${g.description?.slice(0, 120) ?? ""}\\n   ${g.url}`
    ).join("\\n\\n");
  } catch {
    return "Gem Hunter temporariamente indisponível.";
  }
}

async function toolWikiSearch(query: string): Promise<string> {
  try {
    const res = await fetch(
      `${GATEWAY_BASE}/knowledge/search?q=${encodeURIComponent(query)}`,
      { signal: AbortSignal.timeout(5000) }
    );
    if (!res.ok) return "Knowledge base indisponível.";
    const data = await res.json() as { results?: Array<{ title: string; category: string; slug: string; quality_score: number }> };
    const results = data.results?.slice(0, 4) ?? [];
    if (results.length === 0) return `Nenhum resultado no Knowledge Base para "${query}".`;
    return results.map((r) =>
      `• *${r.title}* [${r.category}] — qualidade: ${r.quality_score}/100`
    ).join("\\n");
  } catch {
    return "Knowledge Base temporariamente indisponível.";
  }
}

async function toolSystemStatus(): Promise<string> {
  const lines: string[] = [];

  // Guard Brasil
  try {
    const res = await fetch(`${GUARD_URL}/health`, { signal: AbortSignal.timeout(5000) });
    const data = await res.json() as Record<string, unknown>;
    lines.push(`Guard Brasil: ${res.ok ? "✅ OK" : "⚠️ DEGRADED"}`);
    if (data.version) lines.push(`  versão: ${data.version}`);
  } catch {
    lines.push("Guard Brasil: ❌ UNREACHABLE");
  }

  // Knowledge stats
  try {
    const res = await fetch(`${GATEWAY_BASE}/knowledge/stats`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const d = await res.json() as { pages?: { total: number; avg_quality: number } };
      if (d.pages) lines.push(`Knowledge Base: ${d.pages.total} páginas, qualidade média ${d.pages.avg_quality}/100`);
    }
  } catch { /* skip */ }

  // Gem Hunter
  try {
    const res = await fetch(`${GATEWAY_BASE}/gem-hunter/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const d = await res.json() as { status: string; last_run: string | null; total_gems: number };
      lines.push(`Gem Hunter: ${d.status === "operational" ? "✅" : "⚠️"} último run: ${d.last_run?.slice(0, 10) ?? "nunca"} | ${d.total_gems} gems`);
    }
  } catch { /* skip */ }

  return lines.join("\\n") || "Status indisponível.";
}

async function toolListAgents(): Promise<string> {
  try {
    const agentsPath = join(ROOT, "agents/registry/agents.json");
    if (!existsSync(agentsPath)) return "agents.json não encontrado.";
    const raw = readFileSync(agentsPath, "utf-8");
    const data = JSON.parse(raw) as Record<string, { description?: string; status?: string; kind?: string }>;
    const entries = Object.entries(data).slice(0, 10);
    return `*Agentes EGOS (${Object.keys(data).length} total)*\\n` +
      entries.map(([id, a]) => `• ${id} [${a.kind ?? "?"}]: ${a.description?.slice(0, 80) ?? ""}`).join("\\n");
  } catch {
    return "Erro ao ler agentes.";
  }
}

async function toolGetCosts(): Promise<string> {
  const today = new Date().toISOString().slice(0, 10);
  try {
    const data = await sbFetch(`api_usage?select=model,tokens_in,tokens_out,cost_usd&date=eq.${today}`) as Array<{ model?: string; cost_usd?: number }> | null;
    if (!data || data.length === 0) return `Sem dados de custo para ${today}.`;
    let total = 0;
    const lines = [`*Custos de hoje (${today})*\\n`];
    for (const r of data) { total += r.cost_usd ?? 0; lines.push(`• ${r.model ?? "?"}: $${(r.cost_usd ?? 0).toFixed(4)}`); }
    lines.push(`\\n*Total: $${total.toFixed(4)}*`);
    return lines.join("\\n");
  } catch {
    return "Supabase indisponível para custos.";
  }
}

async function toolGuardStatus(): Promise<string> {
  try {
    const [health, meta] = await Promise.all([
      fetch(`${GUARD_URL}/health`, { signal: AbortSignal.timeout(5000) }).then((r) => r.json()),
      fetch(`${GUARD_URL}/v1/meta`, { signal: AbortSignal.timeout(5000) }).then((r) => r.json()),
    ]) as [Record<string, unknown>, Record<string, unknown>];
    return `*Guard Brasil API*\\nStatus: ✅ LIVE\\nVersão: ${health.version ?? "?"}\\nPadrões PII: ${(meta.patterns as unknown[])?.length ?? "?"}\\nURL: ${GUARD_URL}`;
  } catch {
    return `Guard Brasil: ❌ UNREACHABLE\\nURL: ${GUARD_URL}`;
  }
}

// ─── Tool registry ─────────────────────────────────────────────────────────────

const TOOL_DEFS = [
  {
    type: "function" as const,
    function: {
      name: "gem_search",
      description: "Busca as melhores ferramentas, repositórios, modelos e papers open-source por tópico ou setor. Setores disponíveis: ai, crypto, systems, agents, governance, research.",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Busca livre por texto (ex: 'melhor framework de agentes')" },
          sector: { type: "string", enum: ["ai", "crypto", "systems", "agents", "governance", "research"], description: "Filtrar por setor" },
        },
        required: [],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "wiki_search",
      description: "Busca no Knowledge Base do EGOS (51+ páginas: conceitos, padrões, decisões arquiteturais, entidades do sistema).",
      parameters: {
        type: "object",
        properties: { query: { type: "string", description: "Termo ou conceito para buscar" } },
        required: ["query"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "system_status",
      description: "Retorna o status atual do sistema EGOS: Guard Brasil, Knowledge Base, Gem Hunter.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "list_agents",
      description: "Lista todos os agentes registrados no EGOS (agents.json).",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_costs",
      description: "Retorna os custos de API de hoje (OpenRouter, DashScope, etc.) do Supabase.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "guard_status",
      description: "Verifica o status detalhado da API Guard Brasil (versão, padrões PII, health).",
      parameters: { type: "object", properties: {} },
    },
  },
];

// ─── Tool dispatcher ──────────────────────────────────────────────────────────

async function dispatchTool(name: string, args: Record<string, unknown>): Promise<string> {
  switch (name) {
    case "gem_search": return toolGemSearch(args.query as string ?? "", args.sector as string | undefined);
    case "wiki_search": return toolWikiSearch(args.query as string ?? "");
    case "system_status": return toolSystemStatus();
    case "list_agents": return toolListAgents();
    case "get_costs": return toolGetCosts();
    case "guard_status": return toolGuardStatus();
    default: return `Ferramenta "${name}" não reconhecida.`;
  }
}

// ─── Media processing ─────────────────────────────────────────────────────────

/** Transcribe audio using Groq Whisper */
export async function transcribeAudio(audioBase64: string, mime: string): Promise<string> {
  if (!GROQ_KEY) return "[Transcrição de áudio não configurada — GROQ_API_KEY ausente]";

  try {
    // Convert base64 to Blob
    const binaryStr = atob(audioBase64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);

    // Determine file extension from mime type
    const ext = mime.includes("mp4") ? "mp4"
      : mime.includes("ogg") ? "ogg"
      : mime.includes("mpeg") ? "mp3"
      : mime.includes("wav") ? "wav"
      : "ogg";

    const blob = new Blob([bytes], { type: mime });
    const form = new FormData();
    form.append("file", blob, `audio.${ext}`);
    form.append("model", "whisper-large-v3-turbo");
    form.append("response_format", "text");
    form.append("language", "pt"); // hint: Portuguese

    const res = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: { Authorization: `Bearer ${GROQ_KEY}` },
      body: form,
      signal: AbortSignal.timeout(30000),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error("[transcribe] Groq error:", err);
      return `[Erro na transcrição: ${res.status}]`;
    }

    const text = await res.text();
    return text.trim() || "[Áudio sem fala detectada]";
  } catch (e) {
    console.error("[transcribe] Exception:", e);
    return `[Erro na transcrição: ${(e as Error).message}]`;
  }
}

/** Describe an image using Qwen-VL */
export async function describeImage(imageBase64: string, mime: string, caption?: string): Promise<string> {
  if (!DASHSCOPE_KEY) return "[Análise de imagem não configurada — ALIBABA_DASHSCOPE_API_KEY ausente]";

  try {
    const dataUrl = `data:${mime};base64,${imageBase64}`;
    const userContent = [
      { type: "image_url", image_url: { url: dataUrl } },
      { type: "text", text: caption ? `Descreva esta imagem. Contexto do usuário: "${caption}"` : "Descreva o que você vê nesta imagem de forma detalhada." },
    ];

    const res = await fetch(`${DASHSCOPE_BASE}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${DASHSCOPE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen-vl-plus",
        messages: [{ role: "user", content: userContent }],
        max_tokens: 500,
      }),
      signal: AbortSignal.timeout(20000),
    });

    if (!res.ok) return "[Erro na análise da imagem]";
    const data = await res.json() as { choices?: Array<{ message: { content: string } }> };
    return data.choices?.[0]?.message?.content ?? "[Imagem sem descrição]";
  } catch (e) {
    return `[Erro na análise: ${(e as Error).message}]`;
  }
}

// ─── Main orchestrator ────────────────────────────────────────────────────────

const SYSTEM_PROMPT = `Você é o EGOS — assistente pessoal de IA do Enio Rocha.
Você tem acesso ao sistema EGOS completo: Knowledge Base, Gem Hunter, Guard Brasil API, agentes de IA, custos.

Capacidades:
- Buscar as melhores ferramentas open-source (gem_search por setor: ai, crypto, systems, agents, governance, research)
- Consultar a base de conhecimento do EGOS (wiki_search)
- Verificar status dos sistemas (system_status, guard_status)
- Listar agentes registrados (list_agents)
- Ver custos de API de hoje (get_costs)

Estilo:
- Responda sempre em Português brasileiro
- Seja direto e objetivo — o usuário é desenvolvedor experiente
- Use WhatsApp markdown: *negrito*, _itálico_
- Para listas use • ou numerais
- Mantenha respostas ≤ 400 chars quando possível, 800 chars no máximo
- Quando não souber algo, diga claramente

Contexto:
- Sistema: EGOS Framework (multi-agent AI platform)
- Foco atual: Guard Brasil (PII detection) + Gem Hunter (discovery engine)
- Meta: R$30k+ MRR até junho 2026`;

export async function orchestrate(msg: IncomingMessage): Promise<OrchestratorResponse> {
  if (!DASHSCOPE_KEY) {
    return { text: "❌ ALIBABA_DASHSCOPE_API_KEY não configurado no .env do gateway." };
  }

  const toolsUsed: string[] = [];
  let userText = msg.text ?? "";

  // Phase 1: Process media → text
  if (msg.mediaType === "audio" && msg.mediaBase64 && msg.mediaMime) {
    console.log("[orchestrator] Transcribing audio...");
    const transcription = await transcribeAudio(msg.mediaBase64, msg.mediaMime);
    userText = `[Áudio transcrito]: ${transcription}`;
    toolsUsed.push("whisper_transcription");
  } else if (msg.mediaType === "image" && msg.mediaBase64 && msg.mediaMime) {
    console.log("[orchestrator] Describing image...");
    const description = await describeImage(msg.mediaBase64, msg.mediaMime, msg.caption);
    userText = `[Imagem recebida]: ${description}${msg.caption ? ` (legenda do usuário: "${msg.caption}")` : ""}`;
    toolsUsed.push("qwen_vision");
  } else if (msg.mediaType === "document" && msg.fileName) {
    userText = `[Arquivo recebido: ${msg.fileName}]${msg.caption ? ` — "${msg.caption}"` : ""}. Não consigo processar o conteúdo do arquivo ainda, mas posso ajudar com outra coisa.`;
  } else if (msg.mediaType === "video") {
    userText = `[Vídeo recebido]${msg.caption ? ` — legenda: "${msg.caption}"` : ""}. Ainda não processo vídeos. Posso transcrever áudios e descrever imagens.`;
  } else if (msg.mediaType === "sticker") {
    userText = "[Sticker recebido] 😄";
  } else if (!userText) {
    return { text: "Mensagem recebida mas não reconhecida. Tente enviar texto, áudio ou imagem." };
  }

  // Phase 2: AI reasoning with tools (max 3 iterations)
  type ChatMessage = { role: "system" | "user" | "assistant" | "tool"; content: string; tool_call_id?: string; name?: string };
  const messages: ChatMessage[] = [
    { role: "system", content: SYSTEM_PROMPT },
    { role: "user", content: userText },
  ];

  for (let iter = 0; iter < 3; iter++) {
    const res = await fetch(`${DASHSCOPE_BASE}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${DASHSCOPE_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "qwen-plus",
        messages,
        tools: TOOL_DEFS,
        tool_choice: "auto",
        max_tokens: 600,
        temperature: 0.3,
      }),
      signal: AbortSignal.timeout(20000),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error("[orchestrator] DashScope error:", err);
      return { text: "❌ Erro no AI orchestrator. Tente novamente.", toolsUsed };
    }

    const data = await res.json() as {
      choices?: Array<{
        finish_reason: string;
        message: {
          content?: string;
          tool_calls?: Array<{ id: string; function: { name: string; arguments: string } }>;
        };
      }>;
    };

    const choice = data.choices?.[0];
    if (!choice) break;

    const { finish_reason, message } = choice;

    // No tool calls — final answer
    if (finish_reason === "stop" || !message.tool_calls?.length) {
      return { text: message.content ?? "Sem resposta.", toolsUsed };
    }

    // Execute tool calls
    messages.push({ role: "assistant", content: message.content ?? "", ...message });

    for (const tc of message.tool_calls) {
      let args: Record<string, unknown> = {};
      try { args = JSON.parse(tc.function.arguments); } catch { /* noop */ }

      console.log(`[orchestrator] Tool call: ${tc.function.name}(${JSON.stringify(args)})`);
      const result = await dispatchTool(tc.function.name, args);
      toolsUsed.push(tc.function.name);

      messages.push({
        role: "tool",
        tool_call_id: tc.id,
        name: tc.function.name,
        content: result,
      });
    }
  }

  return { text: "Processamento concluído, mas sem resposta final.", toolsUsed };
}
