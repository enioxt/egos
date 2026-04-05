/**
 * EGOS Gateway — AI Orchestrator v2
 *
 * Shared LLM orchestration for WhatsApp + Telegram chatbots.
 * Model: qwen-plus (Alibaba DashScope)
 * Transcription: Groq Whisper-large-v3-turbo
 * Vision: qwen-vl-plus
 *
 * Tools (13):
 *   system_status, guard_status, guard_test, gem_search, gem_trending,
 *   wiki_search, wiki_page, list_agents, get_tasks, recent_commits,
 *   get_costs, knowledge_stats, world_model
 */

import { join } from "path";
import { existsSync, readFileSync } from "fs";
import { execSync } from "child_process";

// ─── Config ───────────────────────────────────────────────────────────────────

const DASHSCOPE_BASE =
  process.env.ALIBABA_DASHSCOPE_BASE_URL ??
  "https://dashscope-intl.aliyuncs.com/compatible-mode/v1";
const DASHSCOPE_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? "";
const GROQ_KEY = process.env.GROQ_API_KEY ?? "";
const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const GUARD_URL = "https://guard.egos.ia.br";
const GW_PORT = process.env.GATEWAY_PORT ?? "3000";
const GW = `http://localhost:${GW_PORT}`;
const ROOT = join(import.meta.dir, "../../..");

// ─── Types ────────────────────────────────────────────────────────────────────

export type MediaType = "audio" | "image" | "video" | "document" | "sticker";
export type Channel = "whatsapp" | "telegram";

export interface IncomingMessage {
  from: string;
  channel: Channel;
  text?: string;
  mediaType?: MediaType;
  mediaBase64?: string;
  mediaMime?: string;
  mediaUrl?: string;
  caption?: string;
  fileName?: string;
}

export interface OrchestratorResponse {
  text: string;
  toolsUsed?: string[];
}

// ─── Supabase helpers ─────────────────────────────────────────────────────────

const SB_HEADERS = () => ({
  apikey: SUPABASE_KEY,
  Authorization: `Bearer ${SUPABASE_KEY}`,
  "Content-Type": "application/json",
  Prefer: "return=minimal",
});

async function sbFetch(path: string): Promise<unknown> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return null;
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
      headers: SB_HEADERS(),
      signal: AbortSignal.timeout(6000),
    });
    return res.ok ? res.json() : null;
  } catch {
    return null;
  }
}

async function sbInsert(table: string, row: Record<string, unknown>): Promise<boolean> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return false;
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
      method: "POST",
      headers: SB_HEADERS(),
      body: JSON.stringify(row),
      signal: AbortSignal.timeout(6000),
    });
    return res.status === 201 || res.status === 200;
  } catch {
    return false;
  }
}

// ─── Conversation memory ──────────────────────────────────────────────────────

interface HistoryRow {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

async function loadHistory(channel: string, userId: string, limit = 12): Promise<HistoryRow[]> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return [];
  try {
    const rows = await sbFetch(
      `egos_chat_history?channel=eq.${encodeURIComponent(channel)}&user_id=eq.${encodeURIComponent(userId)}&order=created_at.desc&limit=${limit}&select=role,content,created_at`
    ) as HistoryRow[] | null;
    if (!rows?.length) return [];
    return rows.reverse(); // oldest first for LLM context
  } catch {
    return [];
  }
}

async function saveHistory(
  channel: string,
  userId: string,
  userContent: string,
  assistantContent: string,
  toolsUsed: string[],
  mediaType?: string,
): Promise<void> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return;
  // Save user turn
  await sbInsert("egos_chat_history", {
    channel,
    user_id: userId,
    role: "user",
    content: userContent,
    media_type: mediaType ?? null,
    tools_used: [],
  });
  // Save assistant turn
  await sbInsert("egos_chat_history", {
    channel,
    user_id: userId,
    role: "assistant",
    content: assistantContent,
    tools_used: toolsUsed,
  });
}

// ─── Tool: system_status ──────────────────────────────────────────────────────

async function toolSystemStatus(): Promise<string> {
  const parts: string[] = [];

  // Guard Brasil
  try {
    const res = await fetch(`${GUARD_URL}/health`, { signal: AbortSignal.timeout(5000) });
    const d = await res.json() as { version?: string; status?: string };
    parts.push(`🛡 Guard Brasil: ${res.ok ? "✅ LIVE" : "⚠️"} v${d.version ?? "?"} ${d.status ?? ""}`);
  } catch {
    parts.push("🛡 Guard Brasil: ❌ UNREACHABLE");
  }

  // Knowledge Base
  try {
    const res = await fetch(`${GW}/knowledge/stats`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const d = await res.json() as { pages?: { total: number; avg_quality: number }; learnings?: { total: number } };
      parts.push(`📚 Knowledge Base: ${d.pages?.total ?? 0} páginas | qualidade ${d.pages?.avg_quality ?? 0}/100 | ${d.learnings?.total ?? 0} learnings`);
    }
  } catch { /* skip */ }

  // Gem Hunter
  try {
    const res = await fetch(`${GW}/gem-hunter/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const d = await res.json() as { status: string; last_run: string | null; total_gems: number };
      const lastRun = d.last_run ? d.last_run.slice(0, 10) : "nunca";
      parts.push(`💎 Gem Hunter: ${d.status === "operational" ? "✅" : "⚠️ sem dados"} | último run: ${lastRun}`);
    }
  } catch { /* skip */ }

  // VPS + Docker (lightweight check)
  try {
    const sshRes = execSync(
      `ssh -i ~/.ssh/hetzner_ed25519 -o ConnectTimeout=3 -o StrictHostKeyChecking=no root@204.168.217.125 "docker ps --format '{{.Names}}' | wc -l" 2>/dev/null`,
      { timeout: 6000 }
    ).toString().trim();
    parts.push(`🖥 VPS: ✅ ${sshRes} containers ativos`);
  } catch {
    parts.push("🖥 VPS: não alcançável neste contexto");
  }

  return parts.join("\n") || "Status indisponível.";
}

// ─── Tool: guard_status ───────────────────────────────────────────────────────

async function toolGuardStatus(): Promise<string> {
  try {
    const [hRes, mRes] = await Promise.all([
      fetch(`${GUARD_URL}/health`, { signal: AbortSignal.timeout(5000) }),
      fetch(`${GUARD_URL}/v1/meta`, { signal: AbortSignal.timeout(5000) }),
    ]);
    const h = await hRes.json() as { version?: string; status?: string; uptime?: number };
    const m = await mRes.json() as { patterns?: unknown[]; version?: string };
    const uptime = h.uptime ? `${Math.floor(h.uptime / 3600)}h` : "?";
    return `🛡 *Guard Brasil API*\nStatus: ✅ LIVE\nVersão: ${h.version ?? "?"}\nUptime: ${uptime}\nPadrões PII: ${m.patterns?.length ?? "?"}\nEndpoints: /v1/inspect, /v1/meta\nURL: ${GUARD_URL}`;
  } catch {
    return `🛡 Guard Brasil: ❌ UNREACHABLE\n${GUARD_URL}`;
  }
}

// ─── Tool: guard_test ─────────────────────────────────────────────────────────

async function toolGuardTest(text: string): Promise<string> {
  if (!text) return "Forneça um texto para testar (ex: 'João Silva CPF 123.456.789-00')";
  try {
    const res = await fetch(`${GUARD_URL}/v1/inspect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return `Guard Brasil respondeu ${res.status}`;
    const d = await res.json() as {
      pii_detected?: boolean;
      entities?: Array<{ type: string; value: string; confidence?: number }>;
      risk_level?: string;
    };
    const entities = d.entities ?? [];
    if (!d.pii_detected || entities.length === 0) {
      return `✅ Sem PII detectado no texto fornecido.\nTexto analisado: "${text.slice(0, 60)}${text.length > 60 ? "..." : ""}"`;
    }
    const list = entities.map((e) => `• ${e.type}: "${e.value}" (conf: ${((e.confidence ?? 1) * 100).toFixed(0)}%)`).join("\n");
    return `⚠️ PII detectado! Risco: ${d.risk_level ?? "?"}\n${list}`;
  } catch (e) {
    return `Erro no teste: ${(e as Error).message}`;
  }
}

// ─── Tool: gem_search ─────────────────────────────────────────────────────────

async function toolGemSearch(query: string, sector?: string): Promise<string> {
  try {
    const url = sector
      ? `${GW}/gem-hunter/sector/${sector}`
      : `${GW}/gem-hunter/latest?limit=5`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return "💎 Gem Hunter sem dados. Rode: bun agent:run gem-hunter --exec";
    const d = await res.json() as { gems?: Array<{ name: string; description: string; url: string; score?: number; source?: string }> };
    const gems = (d.gems ?? []).slice(0, 5);
    if (!gems.length) return "Nenhum gem encontrado.";
    return gems.map((g, i) =>
      `${i + 1}. *${g.name}* [${g.source ?? "?"}] score:${g.score ?? "?"}\n   ${(g.description ?? "").slice(0, 100)}\n   ${g.url}`
    ).join("\n\n");
  } catch {
    return "💎 Gem Hunter temporariamente indisponível.";
  }
}

// ─── Tool: gem_trending ──────────────────────────────────────────────────────

async function toolGemTrending(): Promise<string> {
  try {
    const res = await fetch(`${GW}/gem-hunter/trending`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return "Sem histórico de trending ainda.";
    const d = await res.json() as { trending?: Array<{ name: string; url: string; run_count: number; max_score: number }> };
    const gems = d.trending ?? [];
    if (!gems.length) return "Sem trending (precisa de 2+ runs do gem-hunter).";
    return `💎 *Trending Gems (multi-run):*\n` +
      gems.slice(0, 7).map((g, i) => `${i + 1}. *${g.name}* [${g.run_count}x, max:${g.max_score}]\n   ${g.url}`).join("\n");
  } catch {
    return "Trending indisponível.";
  }
}

// ─── Tool: wiki_search ───────────────────────────────────────────────────────

async function toolWikiSearch(query: string): Promise<string> {
  try {
    const res = await fetch(`${GW}/knowledge/search?q=${encodeURIComponent(query)}`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return "Knowledge base indisponível.";
    const d = await res.json() as { results?: Array<{ slug: string; title: string; category: string; quality_score: number }> };
    const results = (d.results ?? []).slice(0, 5);
    if (!results.length) return `Sem resultados para "${query}".`;
    return `📚 *Resultados no Knowledge Base:*\n` +
      results.map((r) => `• *${r.title}* [${r.category}] q:${r.quality_score}/100\n  slug: ${r.slug}`).join("\n");
  } catch {
    return "Knowledge Base indisponível.";
  }
}

// ─── Tool: wiki_page ─────────────────────────────────────────────────────────

async function toolWikiPage(slug: string): Promise<string> {
  try {
    const res = await fetch(`${GW}/knowledge/pages/${slug}`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return `Página "${slug}" não encontrada.`;
    const p = await res.json() as { title: string; category: string; content: string; tags: string[]; quality_score: number; cross_refs: string[] };
    const content = (p.content ?? "").slice(0, 800);
    const tags = (p.tags ?? []).join(", ");
    const refs = (p.cross_refs ?? []).join(", ");
    return `📄 *${p.title}* [${p.category}] q:${p.quality_score}/100\n${refs ? `refs: ${refs}\n` : ""}${tags ? `tags: ${tags}\n` : ""}\n${content}${(p.content?.length ?? 0) > 800 ? "\n...(truncado)" : ""}`;
  } catch {
    return `Erro ao carregar página "${slug}".`;
  }
}

// ─── Tool: list_agents ───────────────────────────────────────────────────────

async function toolListAgents(): Promise<string> {
  try {
    const agentsPath = join(ROOT, "agents/registry/agents.json");
    if (!existsSync(agentsPath)) return "agents.json não encontrado.";
    const data = JSON.parse(readFileSync(agentsPath, "utf-8")) as Record<
      string,
      { description?: string; status?: string; kind?: string; area?: string }
    >;
    const entries = Object.entries(data);
    const byKind: Record<string, typeof entries> = {};
    for (const e of entries) {
      const k = e[1].kind ?? "other";
      if (!byKind[k]) byKind[k] = [];
      byKind[k].push(e);
    }
    const lines = [`🤖 *Agentes EGOS (${entries.length} total)*`];
    for (const [kind, list] of Object.entries(byKind)) {
      lines.push(`\n*${kind.toUpperCase()}* (${list.length})`);
      for (const [id, a] of list.slice(0, 4)) {
        lines.push(`  • ${id}: ${(a.description ?? "").slice(0, 60)}`);
      }
      if (list.length > 4) lines.push(`  ... +${list.length - 4} mais`);
    }
    return lines.join("\n");
  } catch {
    return "Erro ao ler agentes.";
  }
}

// ─── Tool: get_tasks ─────────────────────────────────────────────────────────

async function toolGetTasks(filter: "p0" | "p1" | "all" = "p0"): Promise<string> {
  try {
    const tasksPath = join(ROOT, "TASKS.md");
    if (!existsSync(tasksPath)) return "TASKS.md não encontrado.";
    const content = readFileSync(tasksPath, "utf-8");

    // Extract P0/P1 sections
    const lines = content.split("\n");
    const result: string[] = [`📋 *TASKS.md — ${filter.toUpperCase()} pendentes:*`];
    let inSection = false;
    let count = 0;

    for (const line of lines) {
      const isP0 = line.includes("P0") || line.includes("CRITICAL");
      const isP1 = line.includes("P1") || line.includes("Sprint");
      if (isP0 || isP1) inSection = true;
      if (inSection && line.match(/^- \[ \]/)) {
        const priority = isP0 || (filter === "p0" && count < 5) ? "🔴" : "🟡";
        result.push(`${priority} ${line.replace("- [ ] ", "").slice(0, 80)}`);
        count++;
        if (filter !== "all" && count >= 8) break;
      }
      // Stop at horizontal rule or end of section
      if (inSection && line.startsWith("---") && count > 0) break;
    }

    // Also grab inline P0/P1 checklist items
    if (count === 0) {
      const pending = lines
        .filter((l) => l.match(/^- \[ \]/))
        .slice(0, 8)
        .map((l) => `• ${l.replace("- [ ] ", "").slice(0, 80)}`);
      result.push(...pending);
      if (!pending.length) result.push("Sem tarefas pendentes encontradas.");
    }

    return result.join("\n");
  } catch {
    return "Erro ao ler TASKS.md.";
  }
}

// ─── Tool: recent_commits ────────────────────────────────────────────────────

async function toolRecentCommits(limit = 7): Promise<string> {
  try {
    const out = execSync(
      `git -C ${ROOT} log --oneline -${limit} --format="%h %s (%cr)" 2>/dev/null`,
      { timeout: 5000 }
    ).toString().trim();
    if (!out) return "Sem commits recentes.";
    return `📝 *Últimos ${limit} commits:*\n` + out.split("\n").map((l) => `• ${l}`).join("\n");
  } catch {
    return "Git indisponível neste contexto.";
  }
}

// ─── Tool: get_costs ─────────────────────────────────────────────────────────

async function toolGetCosts(): Promise<string> {
  const today = new Date().toISOString().slice(0, 10);
  const data = await sbFetch(`api_usage?select=model,tokens_in,tokens_out,cost_usd&date=eq.${today}`) as
    | Array<{ model?: string; tokens_in?: number; tokens_out?: number; cost_usd?: number }>
    | null;

  if (!data || !data.length) {
    return `💰 Sem dados de custo para ${today}.\n(Supabase não configurado localmente)`;
  }
  let total = 0;
  const lines = [`💰 *Custos de hoje (${today}):*`];
  for (const r of data) {
    const c = r.cost_usd ?? 0;
    total += c;
    lines.push(`• ${r.model ?? "?"}: $${c.toFixed(4)} (${r.tokens_in ?? 0}in/${r.tokens_out ?? 0}out)`);
  }
  lines.push(`\n*Total: $${total.toFixed(4)}*`);
  return lines.join("\n");
}

// ─── Tool: knowledge_stats ───────────────────────────────────────────────────

async function toolKnowledgeStats(): Promise<string> {
  try {
    const res = await fetch(`${GW}/knowledge/stats`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return "Knowledge Base indisponível.";
    const d = await res.json() as {
      pages: { total: number; avg_quality: number; by_category: Record<string, number> };
      learnings: { total: number; by_domain: Record<string, number>; by_outcome: Record<string, number> };
    };
    const cats = Object.entries(d.pages.by_category)
      .sort(([, a], [, b]) => b - a)
      .map(([k, v]) => `${k}:${v}`)
      .join(", ");
    const domains = Object.entries(d.learnings.by_domain)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 4)
      .map(([k, v]) => `${k}:${v}`)
      .join(", ");
    return `📚 *Knowledge Base Stats:*\nPáginas: ${d.pages.total} | Qualidade média: ${d.pages.avg_quality}/100\nCategorias: ${cats}\nLearnings: ${d.learnings.total} (${domains})`;
  } catch {
    return "Knowledge Base indisponível.";
  }
}

// ─── Tool: memory_search ─────────────────────────────────────────────────────

async function toolMemorySearch(query: string, channel: string, userId: string): Promise<string> {
  if (!SUPABASE_URL || !SUPABASE_KEY) return "Memória não disponível (Supabase não configurado).";
  try {
    // Full-text search across stored messages for this user
    const encoded = encodeURIComponent(`%${query}%`);
    const rows = await sbFetch(
      `egos_chat_history?channel=eq.${encodeURIComponent(channel)}&user_id=eq.${encodeURIComponent(userId)}&content=ilike.${encoded}&order=created_at.desc&limit=8&select=role,content,created_at`
    ) as Array<{ role: string; content: string; created_at: string }> | null;

    if (!rows?.length) return `Nenhuma conversa encontrada sobre "${query}".`;

    const lines = rows.map((r) => {
      const d = new Date(r.created_at).toLocaleDateString("pt-BR");
      const who = r.role === "user" ? "Você" : "EGOS";
      return `[${d}] ${who}: ${r.content.slice(0, 150)}`;
    });
    return `Memória — "${query}":\n${lines.join("\n")}`;
  } catch (e) {
    return `Erro ao buscar memória: ${(e as Error).message}`;
  }
}

// ─── Tool: world_model ───────────────────────────────────────────────────────

async function toolWorldModel(): Promise<string> {
  try {
    const out = execSync(
      `cd ${ROOT} && timeout 15 bun packages/shared/src/world-model.ts --json 2>/dev/null`,
      { timeout: 20000 }
    ).toString().trim();
    const d = JSON.parse(out) as {
      health?: number;
      blockers?: Array<{ id: string; title: string }>;
      sprint?: Array<{ id: string; title: string }>;
    };
    const blockers = (d.blockers ?? []).slice(0, 3).map((b) => `🔴 ${b.id}: ${b.title.slice(0, 60)}`).join("\n");
    const sprint = (d.sprint ?? []).slice(0, 3).map((s) => `🟡 ${s.id}: ${s.title.slice(0, 60)}`).join("\n");
    return `🌍 *World Model Snapshot*\nSaúde: ${d.health ?? "?"}%\n\n*P0 Blockers:*\n${blockers || "✅ Nenhum"}\n\n*Sprint atual:*\n${sprint || "(vazio)"}`;
  } catch {
    return "World model indisponível neste contexto.";
  }
}

// ─── Tool registry ────────────────────────────────────────────────────────────

const TOOL_DEFS = [
  {
    type: "function" as const,
    function: {
      name: "system_status",
      description: "Status completo do sistema EGOS: Guard Brasil API, Knowledge Base, Gem Hunter, VPS.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "guard_status",
      description: "Status detalhado da Guard Brasil API (versão, uptime, padrões PII, endpoints).",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "guard_test",
      description: "Testa detecção de PII/dados sensíveis em um texto usando a Guard Brasil API. Útil para demos e validações.",
      parameters: {
        type: "object",
        properties: { text: { type: "string", description: "Texto para análise de PII (ex: 'João CPF 123.456.789-00')" } },
        required: ["text"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "gem_search",
      description: "Busca os melhores repositórios, modelos, papers e ferramentas open-source. Setores: ai, crypto, systems, agents, governance, research.",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Texto livre (ex: 'frameworks de agentes com tool calling')" },
          sector: { type: "string", enum: ["ai", "crypto", "systems", "agents", "governance", "research"] },
        },
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "gem_trending",
      description: "Gems que apareceram em múltiplos runs do Gem Hunter (alta confiabilidade).",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "wiki_search",
      description: "Busca no Knowledge Base EGOS (conceitos, padrões, decisões arquiteturais, entidades do sistema).",
      parameters: {
        type: "object",
        properties: { query: { type: "string", description: "Termo para buscar" } },
        required: ["query"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "wiki_page",
      description: "Lê o conteúdo completo de uma página específica do Knowledge Base pelo slug.",
      parameters: {
        type: "object",
        properties: { slug: { type: "string", description: "Slug da página (ex: event-bus-architecture)" } },
        required: ["slug"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "list_agents",
      description: "Lista todos os agentes registrados no EGOS com kind e descrição.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_tasks",
      description: "Lê tarefas pendentes do TASKS.md. Use filter='p0' para críticas, 'p1' para sprint, 'all' para todas.",
      parameters: {
        type: "object",
        properties: {
          filter: { type: "string", enum: ["p0", "p1", "all"], description: "Nível de prioridade" },
        },
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "recent_commits",
      description: "Mostra os commits mais recentes do repositório EGOS.",
      parameters: {
        type: "object",
        properties: { limit: { type: "number", description: "Quantos commits mostrar (padrão: 7)" } },
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_costs",
      description: "Custos de API de hoje (modelos, tokens, USD) do Supabase.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "knowledge_stats",
      description: "Estatísticas do Knowledge Base: total de páginas, qualidade média, distribuição por categoria e domínio.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "world_model",
      description: "Snapshot do World Model EGOS: saúde % do sistema, P0 blockers, sprint atual.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "memory_search",
      description: "Busca no histórico de conversas passadas. Use quando o usuário perguntar sobre algo que foi discutido antes ('lembra quando...', 'o que falamos sobre...').",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Termo ou assunto a buscar nas conversas passadas" },
        },
        required: ["query"],
      },
    },
  },
];

// ─── Tool dispatcher ──────────────────────────────────────────────────────────

async function dispatchTool(
  name: string,
  args: Record<string, unknown>,
  ctx: { channel: Channel; userId: string },
): Promise<string> {
  switch (name) {
    case "system_status":    return toolSystemStatus();
    case "guard_status":     return toolGuardStatus();
    case "guard_test":       return toolGuardTest(args.text as string ?? "");
    case "gem_search":       return toolGemSearch(args.query as string ?? "", args.sector as string | undefined);
    case "gem_trending":     return toolGemTrending();
    case "wiki_search":      return toolWikiSearch(args.query as string ?? "");
    case "wiki_page":        return toolWikiPage(args.slug as string ?? "");
    case "list_agents":      return toolListAgents();
    case "get_tasks":        return toolGetTasks((args.filter as "p0" | "p1" | "all") ?? "p0");
    case "recent_commits":   return toolRecentCommits(Number(args.limit ?? 7));
    case "get_costs":        return toolGetCosts();
    case "knowledge_stats":  return toolKnowledgeStats();
    case "world_model":      return toolWorldModel();
    case "memory_search":    return toolMemorySearch(args.query as string ?? "", ctx.channel, ctx.userId);
    default:                 return `Ferramenta "${name}" não reconhecida.`;
  }
}

// ─── Media processing ─────────────────────────────────────────────────────────

export async function transcribeAudio(audioBase64: string, mime: string): Promise<string> {
  if (!GROQ_KEY) return "[Transcrição não configurada — GROQ_API_KEY ausente]";
  try {
    const binaryStr = atob(audioBase64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);

    const ext = mime.includes("mp4") ? "mp4" : mime.includes("ogg") ? "ogg"
      : mime.includes("mpeg") ? "mp3" : mime.includes("wav") ? "wav" : "ogg";

    const form = new FormData();
    form.append("file", new Blob([bytes], { type: mime }), `audio.${ext}`);
    form.append("model", "whisper-large-v3-turbo");
    form.append("response_format", "text");
    form.append("language", "pt");

    const res = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: { Authorization: `Bearer ${GROQ_KEY}` },
      body: form,
      signal: AbortSignal.timeout(30000),
    });
    if (!res.ok) return `[Erro na transcrição: ${res.status}]`;
    return (await res.text()).trim() || "[Áudio sem fala]";
  } catch (e) {
    return `[Erro na transcrição: ${(e as Error).message}]`;
  }
}

export async function describeImage(imageBase64: string, mime: string, caption?: string): Promise<string> {
  if (!DASHSCOPE_KEY) return "[Análise de imagem não configurada]";
  try {
    const dataUrl = `data:${mime};base64,${imageBase64}`;
    const res = await fetch(`${DASHSCOPE_BASE}/chat/completions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${DASHSCOPE_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "qwen-vl-plus",
        messages: [{
          role: "user",
          content: [
            { type: "image_url", image_url: { url: dataUrl } },
            { type: "text", text: caption ? `Descreva esta imagem. Contexto: "${caption}"` : "Descreva o que você vê nesta imagem." },
          ],
        }],
        max_tokens: 500,
      }),
      signal: AbortSignal.timeout(20000),
    });
    if (!res.ok) return "[Erro na análise da imagem]";
    const d = await res.json() as { choices?: Array<{ message: { content: string } }> };
    return d.choices?.[0]?.message?.content ?? "[Sem descrição]";
  } catch (e) {
    return `[Erro na análise: ${(e as Error).message}]`;
  }
}

// ─── Format response per channel ─────────────────────────────────────────────

function formatForChannel(text: string, channel: Channel): string {
  if (channel === "whatsapp") {
    // WhatsApp uses *bold*, _italic_, ~strikethrough~, `mono`
    // Remove markdown headers (##) and convert to bold
    return text
      .replace(/^#{1,3}\s+(.+)$/gm, "*$1*")
      .replace(/\*\*(.+?)\*\*/g, "*$1*")
      .replace(/__(.+?)__/g, "_$1_")
      // Limit to 1500 chars for WhatsApp
      .slice(0, 1500);
  }
  // Telegram: already using * for bold — keep as is, just limit length
  return text.slice(0, 2000);
}

// ─── System prompt ────────────────────────────────────────────────────────────

function buildSystemPrompt(channel: Channel): string {
  const today = new Date().toLocaleDateString("pt-BR", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  const fmt = channel === "whatsapp" ? "WhatsApp (*negrito*, _itálico_, `código`)" : "Telegram (*negrito*, _itálico_, `código`)";

  return `Você é o EGOS — assistente pessoal de IA do Enio Rocha, engenheiro e empreendedor.
Data de hoje: ${today}

CONTEXTO DO SISTEMA:
O EGOS é uma plataforma multi-agente de IA em produção. Principais produtos:
• Guard Brasil — API de detecção de PII/LGPD (live em guard.egos.ia.br)
• Gem Hunter — motor de descoberta de ferramentas open-source (gemhunter.egos.ia.br)
• Knowledge Base — 51+ páginas de conhecimento compilado (wiki pages + learnings)
• Gateway — este servidor (WhatsApp + Telegram + API REST)
Meta: R$30k+ MRR até junho 2026 (Guard Brasil + Gem Hunter)

FERRAMENTAS DISPONÍVEIS (use proativamente):
1. system_status — status completo: Guard Brasil, KB, Gem Hunter, VPS
2. guard_status — detalhes da API Guard Brasil
3. guard_test(text) — testa detecção de PII num texto
4. gem_search(query, sector) — busca tools/repos por setor [ai|crypto|systems|agents|governance|research]
5. gem_trending — gems que apareceram em múltiplos runs (alta confiabilidade)
6. wiki_search(query) — busca no Knowledge Base
7. wiki_page(slug) — lê conteúdo completo de uma página
8. list_agents — lista os ~17 agentes EGOS registrados
9. get_tasks(filter) — tarefas pendentes do TASKS.md [p0|p1|all]
10. recent_commits(limit) — últimos commits do repositório
11. get_costs — custos de API de hoje
12. knowledge_stats — estatísticas do Knowledge Base
13. world_model — snapshot de saúde do sistema
14. memory_search(query) — busca no histórico de conversas passadas (use quando Enio perguntar sobre algo já discutido)

MEMÓRIA PERSISTENTE:
• As últimas mensagens desta conversa já estão no contexto acima (histórico automático)
• Use memory_search para buscar conversas mais antigas por assunto
• Nunca diga "não tenho acesso ao histórico" — você tem via memory_search

ESTILO DE RESPOSTA:
• Formato: ${fmt}
• Idioma: Português brasileiro sempre
• Tom: direto, técnico, sem rodeios — Enio é dev experiente
• Comprimento: 200-400 chars para respostas simples, até 800 para análises
• Use bullet points • e emojis funcionais (não decorativos)
• Se a resposta requer múltiplas ferramentas, use todas antes de responder
• Nunca invente dados — se não souber, diga claramente
• Para tarefas críticas: mencione P0 blockers se relevante
• Se Enio perguntar "lembra quando..." ou "o que falamos sobre..." → use memory_search antes de responder`;
}

// ─── Main orchestrator ────────────────────────────────────────────────────────

export async function orchestrate(msg: IncomingMessage): Promise<OrchestratorResponse> {
  if (!DASHSCOPE_KEY) {
    return { text: "❌ ALIBABA_DASHSCOPE_API_KEY não configurado." };
  }

  const toolsUsed: string[] = [];
  let userText = msg.text ?? "";

  // Phase 1: Process media → text
  if (msg.mediaType === "audio" && msg.mediaBase64 && msg.mediaMime) {
    const transcription = await transcribeAudio(msg.mediaBase64, msg.mediaMime);
    userText = `[Transcrição do áudio]: ${transcription}`;
    toolsUsed.push("whisper");
    console.log(`[orchestrator] Audio transcribed: "${transcription.slice(0, 80)}"`);
  } else if (msg.mediaType === "image" && msg.mediaBase64 && msg.mediaMime) {
    const description = await describeImage(msg.mediaBase64, msg.mediaMime, msg.caption);
    userText = `[Imagem]: ${description}${msg.caption ? ` | Legenda do usuário: "${msg.caption}"` : ""}`;
    toolsUsed.push("qwen-vl");
    console.log(`[orchestrator] Image described: "${description.slice(0, 60)}"`);
  } else if (msg.mediaType === "document") {
    userText = `[Arquivo recebido: ${msg.fileName ?? "sem nome"}]${msg.caption ? ` — "${msg.caption}"` : ""}. Não processo conteúdo de arquivos ainda.`;
  } else if (msg.mediaType === "video") {
    userText = `[Vídeo recebido]${msg.caption ? ` — "${msg.caption}"` : ""}. Não processo vídeos ainda. Posso transcrever áudio e descrever imagens.`;
  } else if (msg.mediaType === "sticker") {
    return { text: "😄" };
  } else if (!userText) {
    return { text: "Mensagem recebida mas não reconhecida. Envie texto, áudio ou imagem." };
  }

  // Phase 2: Load conversation history + build messages
  type ChatMsg = {
    role: "system" | "user" | "assistant" | "tool";
    content: string | unknown;
    tool_call_id?: string;
    name?: string;
    tool_calls?: unknown;
  };

  const history = await loadHistory(msg.channel, msg.from, 12);

  const messages: ChatMsg[] = [
    { role: "system", content: buildSystemPrompt(msg.channel) },
    ...history.map((h) => ({ role: h.role as "user" | "assistant", content: h.content })),
    { role: "user", content: userText },
  ];

  for (let iter = 0; iter < 4; iter++) {
    let data: {
      choices?: Array<{
        finish_reason: string;
        message: {
          content?: string;
          tool_calls?: Array<{ id: string; function: { name: string; arguments: string } }>;
        };
      }>;
    };

    try {
      const res = await fetch(`${DASHSCOPE_BASE}/chat/completions`, {
        method: "POST",
        headers: { Authorization: `Bearer ${DASHSCOPE_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "qwen-plus",
          messages,
          tools: TOOL_DEFS,
          tool_choice: "auto",
          max_tokens: 800,
          temperature: 0.2,
        }),
        signal: AbortSignal.timeout(25000),
      });

      if (!res.ok) {
        console.error(`[orchestrator] DashScope ${res.status}: ${await res.text()}`);
        return { text: "❌ Erro no AI. Tente novamente.", toolsUsed };
      }
      data = await res.json();
    } catch (e) {
      console.error("[orchestrator] fetch error:", e);
      return { text: "❌ Timeout no AI. Tente novamente.", toolsUsed };
    }

    const choice = data.choices?.[0];
    if (!choice) break;

    const { finish_reason, message } = choice;

    if (finish_reason === "stop" || !message.tool_calls?.length) {
      const raw = message.content ?? "Sem resposta.";
      const formatted = formatForChannel(raw, msg.channel);
      // Persist conversation turn (non-blocking)
      saveHistory(msg.channel, msg.from, userText, raw, toolsUsed, msg.mediaType).catch(() => {});
      return { text: formatted, toolsUsed };
    }

    // Push assistant message with tool_calls
    messages.push({ role: "assistant", content: message.content ?? "", tool_calls: message.tool_calls });

    // Execute each tool call
    for (const tc of message.tool_calls) {
      let args: Record<string, unknown> = {};
      try { args = JSON.parse(tc.function.arguments); } catch { /* noop */ }

      console.log(`[orchestrator] Tool: ${tc.function.name}(${JSON.stringify(args)})`);
      const result = await dispatchTool(tc.function.name, args, { channel: msg.channel, userId: msg.from });
      toolsUsed.push(tc.function.name);

      messages.push({ role: "tool", tool_call_id: tc.id, name: tc.function.name, content: result });
    }
  }

  const fallback = "Processamento completo.";
  saveHistory(msg.channel, msg.from, userText, fallback, toolsUsed, msg.mediaType).catch(() => {});
  return { text: fallback, toolsUsed };
}
