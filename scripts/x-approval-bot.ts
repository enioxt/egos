#!/usr/bin/env bun
/**
 * 🤖 X Approval Bot — Telegram
 * 
 * Bot para aprovação manual de DMs do X.com
 * Recebe alertas do x-opportunity-alert.ts e permite aprovar/rejeitar
 * 
 * Comandos:
 *   /start — Início
 *   /status — Mostra candidatos pendentes
 *   /approve <id> — Aprova candidato (DM será enviada)
 *   /reject <id> — Rejeita candidato
 *   /preview <id> — Mostra preview do DM sugerido
 * 
 * Deploy: VPS systemd service ou bun run direto
 * 
 * Usage:
 *   bun scripts/x-approval-bot.ts              # run
 *   bun scripts/x-approval-bot.ts --dry-run    # simula sem enviar
 */

import { readFileSync, writeFileSync, existsSync } from "fs";

const DRY_RUN = process.argv.includes("--dry-run");
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID || "";
const X_API_KEY = process.env.X_API_KEY || "";
const X_API_SECRET = process.env.X_API_SECRET || "";
const X_ACCESS_TOKEN = process.env.X_ACCESS_TOKEN || "";
const X_ACCESS_TOKEN_SECRET = process.env.X_ACCESS_TOKEN_SECRET || "";

const OPPORTUNITY_STATE_FILE = "/tmp/x-opportunity-state.json";
const APPROVED_STATE_FILE = "/tmp/x-approved-dms.json";

// ── Types ─────────────────────────────────────────────────────────────────

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
  dm_text?: string;
}

interface TelegramUpdate {
  update_id: number;
  message?: {
    message_id: number;
    chat: { id: number; type: string };
    from?: { id: number; username?: string; first_name?: string };
    text?: string;
    date: number;
  };
  callback_query?: {
    id: string;
    from: { id: number; username?: string };
    message?: { message_id: number; chat: { id: number } };
    data: string;
  };
}

// ── State Management ─────────────────────────────────────────────────────────

function loadOpportunities(): Candidate[] {
  if (!existsSync(OPPORTUNITY_STATE_FILE)) return [];
  try {
    const state = JSON.parse(readFileSync(OPPORTUNITY_STATE_FILE, "utf8"));
    return state.candidates_found || [];
  } catch {
    return [];
  }
}

function loadApproved(): Candidate[] {
  if (!existsSync(APPROVED_STATE_FILE)) return [];
  try {
    return JSON.parse(readFileSync(APPROVED_STATE_FILE, "utf8"));
  } catch {
    return [];
  }
}

function saveApproved(approved: Candidate[]) {
  writeFileSync(APPROVED_STATE_FILE, JSON.stringify(approved, null, 2));
}

function updateCandidateStatus(id: string, status: Candidate["status"], dmText?: string) {
  if (!existsSync(OPPORTUNITY_STATE_FILE)) return;
  try {
    const state = JSON.parse(readFileSync(OPPORTUNITY_STATE_FILE, "utf8"));
    const candidate = state.candidates_found.find((c: Candidate) => c.id === id);
    if (candidate) {
      candidate.status = status;
      if (dmText) candidate.dm_text = dmText;
    }
    writeFileSync(OPPORTUNITY_STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) {
    console.error("Erro ao atualizar candidato:", e);
  }
}

// ── Telegram API ────────────────────────────────────────────────────────────

async function sendTelegramMessage(chatId: number | string, text: string, options?: any) {
  if (!TELEGRAM_BOT_TOKEN) {
    console.error("❌ TELEGRAM_BOT_TOKEN não configurado");
    return false;
  }

  try {
    const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "HTML",
        ...options,
      }),
    });
    return response.ok;
  } catch (error) {
    console.error("❌ Erro ao enviar mensagem Telegram:", error);
    return false;
  }
}

async function getTelegramUpdates(offset: number = 0): Promise<TelegramUpdate[]> {
  if (!TELEGRAM_BOT_TOKEN) return [];

  try {
    const response = await fetch(
      `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?offset=${offset}&limit=100`
    );
    const data = await response.json();
    return data.result || [];
  } catch (error) {
    console.error("❌ Erro ao obter updates:", error);
    return [];
  }
}

async function sendTelegramReplyMarkup(chatId: number | string, text: string, candidateId: string) {
  return sendTelegramMessage(chatId, text, {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "✅ Aprovar", callback_data: `approve:${candidateId}` },
          { text: "❌ Rejeitar", callback_data: `reject:${candidateId}` },
        ],
        [
          { text: "👁️ Preview DM", callback_data: `preview:${candidateId}` },
        ],
      ],
    },
  });
}

// ── DM Generation ──────────────────────────────────────────────────────────

function generateDMText(candidate: Candidate): string {
  const templates: Record<string, string> = {
    "4A": `Oi, vi seu post. Trabalho em algo relacionado — posso te mostrar o que venho construindo?\n\n${candidate.product_match}: ${getProductLink(candidate.product_match)}\n\nSou rápido pra desenvolver mas não tenho paciência pra vender. Procurando parcerias que complementem.`,

    "4B": `Oi, vi seu post sobre LGPD/compliance.\n\nDesenvolvi uma API pra isso: guard.egos.ia.br/landing\n15 padrões brasileiros, 4ms latência.\n\nNão sou de vendas, estou procurando parceiro que entenda esse mercado. Se tiver interesse: chama.`,

    "4C": `Oi, seu trabalho com govtech me chamou atenção.\n\nTenho Eagle Eye (licitações): eagleeye.egos.ia.br\nE EGOS Inteligência (grafos): inteligencia.egos.ia.br\n\nSou pesquisador-builder, desenvolvo rápido. Se fizer sentido conversar: DM aberta.`,

    "4G": `Oi, vi seu post sobre o vazamento.\n\nInfelizmente tá ficando comum. ANPD já multou R$ 65M em 2025.\n\nDesenvolvi API que detecta PII antes que vaze: guard.egos.ia.br/landing\nFree tier pra quem quer testar. Se tiver interesse: chama.`,

    "4K": `Oi, vi seu post procurando parceiro técnico.\n\nSou builder solo, ex-investigador policial → código.\nTenho vários MVPs rodando, código MIT, infraestrutura estável.\n\nA real: sou rápido pra construir, não sei vender.\nSe você tem o lado comercial: vamos conversar.`,

    "4O": `Oi, me identifiquei com seu post.\n\nBuilder solo aqui também. Desenvolvo rápido mas distribuição é meu gargalo.\n\nTenho produtos técnicos rodando (LGPD API, licitações, marketplace).\nSe você vende bem e procura produto técnico sólido: conversamos?`,
  };

  const templateKey = candidate.template_suggestion.split(" — ")[0];
  return templates[templateKey] || templates["4A"];
}

function getProductLink(product: string): string {
  const links: Record<string, string> = {
    "Guard Brasil": "guard.egos.ia.br",
    "Eagle Eye": "eagleeye.egos.ia.br",
    "Carteira Livre": "carteiralivre.com",
    "EGOS Inteligência": "inteligencia.egos.ia.br",
    "EGOS produtos": "github.com/enioxt/egos",
    "Todos": "guard.egos.ia.br",
  };
  return links[product] || "egos.ia.br";
}

// ── X DM Sender ─────────────────────────────────────────────────────────────

async function sendXDM(username: string, text: string): Promise<boolean> {
  if (!X_API_KEY || !X_ACCESS_TOKEN) {
    console.error("❌ X API credentials não configuradas");
    return false;
  }

  // X API v2 DM endpoint
  // POST /2/dm_conversations/with/:participant_id/messages
  // Requer OAuth 1.0a ou OAuth 2.0 com scope dm.write

  console.log(`📤 Enviando DM para @${username}...`);
  console.log(`📝 Texto: ${text.slice(0, 100)}...`);

  if (DRY_RUN) {
    console.log("[DRY-RUN] DM não enviada");
    return true;
  }

  try {
    // Primeiro, obter user ID pelo username
    const userResponse = await fetch(
      `https://api.twitter.com/2/users/by/username/${username}`,
      {
        headers: {
          Authorization: `Bearer ${process.env.X_BEARER_TOKEN || ""}`,
        },
      }
    );

    if (!userResponse.ok) {
      console.error(`❌ Erro ao obter user ID: ${userResponse.status}`);
      return false;
    }

    const userData = await userResponse.json();
    const userId = userData.data?.id;

    if (!userId) {
      console.error("❌ User ID não encontrado");
      return false;
    }

    // Enviar DM
    const dmResponse = await fetch(
      `https://api.twitter.com/2/dm_conversations/with/${userId}/messages`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${process.env.X_BEARER_TOKEN || ""}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      }
    );

    if (!dmResponse.ok) {
      const error = await dmResponse.text();
      console.error(`❌ Erro ao enviar DM: ${dmResponse.status} ${error}`);
      return false;
    }

    console.log("✅ DM enviada com sucesso");
    return true;
  } catch (error) {
    console.error("❌ Erro ao enviar DM:", error);
    return false;
  }
}

// ── Command Handlers ────────────────────────────────────────────────────────

async function handleCommand(chatId: number, text: string, username?: string) {
  const parts = text.split(" ");
  const command = parts[0].toLowerCase();
  const arg = parts[1];

  switch (command) {
    case "/start":
      await sendTelegramMessage(chatId,
        `🤖 <b>X Approval Bot</b>\n\n` +
        `Aprovação manual de DMs do X.com\n\n` +
        `Comandos:\n` +
        `/status — Candidatos pendentes\n` +
        `/approve <id> — Aprovar e enviar DM\n` +
        `/reject <id> — Rejeitar candidato\n` +
        `/preview <id> — Ver preview do DM\n\n` +
        `Você receberá alertas quando encontrarmos oportunidades.`
      );
      break;

    case "/status":
      const opportunities = loadOpportunities();
      const pending = opportunities.filter(c => c.status === "new" || c.status === "alerted");
      const approvedList = opportunities.filter(c => c.status === "approved");
      const sent = opportunities.filter(c => c.status === "sent");

      let statusMsg = `📊 <b>Status dos Candidatos</b>\n\n`;
      statusMsg += `⏳ Pendentes: ${pending.length}\n`;
      statusMsg += `✅ Aprovados (aguardando envio): ${approvedList.length}\n`;
      statusMsg += `📤 Enviados: ${sent.length}\n\n`;

      if (pending.length > 0) {
        statusMsg += `<b>Pendentes P0/P1:</b>\n`;
        for (const c of pending.filter(c => c.priority !== "P2").slice(0, 5)) {
          statusMsg += `• ${c.priority} | @${c.author} | ${c.category}\n`;
        }
      }

      await sendTelegramMessage(chatId, statusMsg);
      break;

    case "/approve":
      if (!arg) {
        await sendTelegramMessage(chatId, "❌ Uso: /approve <id_do_candidato>");
        break;
      }

      const approveCandidate = loadOpportunities().find(c => c.id === arg);
      if (!approveCandidate) {
        await sendTelegramMessage(chatId, `❌ Candidato ${arg} não encontrado`);
        break;
      }

      const dmText = generateDMText(approveCandidate);
      updateCandidateStatus(arg, "approved", dmText);

      // Adicionar à fila de aprovados
      const approvedQueue = loadApproved();
      approveCandidate.dm_text = dmText;
      approvedQueue.push(approveCandidate);
      saveApproved(approvedQueue);

      await sendTelegramMessage(chatId,
        `✅ <b>Candidato aprovado!</b>\n\n` +
        `@${approveCandidate.author} | ${approveCandidate.category}\n\n` +
        `<b>DM que será enviada:</b>\n${dmText}\n\n` +
        `Use /send_now para enviar imediatamente ou aguarde envio automático.`
      );
      break;

    case "/reject":
      if (!arg) {
        await sendTelegramMessage(chatId, "❌ Uso: /reject <id_do_candidato>");
        break;
      }

      updateCandidateStatus(arg, "rejected");
      await sendTelegramMessage(chatId, `❌ Candidato ${arg} rejeitado`);
      break;

    case "/preview":
      if (!arg) {
        await sendTelegramMessage(chatId, "❌ Uso: /preview <id_do_candidato>");
        break;
      }

      const previewCandidate = loadOpportunities().find(c => c.id === arg);
      if (!previewCandidate) {
        await sendTelegramMessage(chatId, `❌ Candidato ${arg} não encontrado`);
        break;
      }

      const previewText = generateDMText(previewCandidate);
      await sendTelegramMessage(chatId,
        `👁️ <b>Preview do DM</b>\n\n` +
        `Para: @${previewCandidate.author}\n` +
        `Template: ${previewCandidate.template_suggestion}\n\n` +
        `<code>${previewText}</code>\n\n` +
        `Use /approve ${arg} para aprovar.`
      );
      break;

    case "/send_now":
      // Enviar todas as DMs aprovadas pendentes
      const approvedPending = loadApproved().filter(c => c.status !== "sent");

      if (approvedPending.length === 0) {
        await sendTelegramMessage(chatId, "📭 Nenhuma DM pendente para envio");
        break;
      }

      let sendResults = `📤 <b>Resultados do Envio</b>\n\n`;

      for (const c of approvedPending) {
        const sent = await sendXDM(c.author, c.dm_text || generateDMText(c));
        if (sent) {
          updateCandidateStatus(c.id, "sent");
          c.status = "sent";
          sendResults += `✅ @${c.author}\n`;
        } else {
          sendResults += `❌ @${c.author} (falha)\n`;
        }
      }

      saveApproved(approvedPending);
      await sendTelegramMessage(chatId, sendResults);
      break;

    default:
      await sendTelegramMessage(chatId, `Comando não reconhecido: ${command}\nUse /start para ver opções.`);
  }
}

async function handleCallback(query: TelegramUpdate["callback_query"]) {
  if (!query) return;

  const [action, candidateId] = query.data.split(":");
  const chatId = query.message?.chat.id;

  if (!chatId) return;

  switch (action) {
    case "approve":
      await handleCommand(chatId, `/approve ${candidateId}`);
      break;
    case "reject":
      await handleCommand(chatId, `/reject ${candidateId}`);
      break;
    case "preview":
      await handleCommand(chatId, `/preview ${candidateId}`);
      break;
  }
}

// ── Main Loop ───────────────────────────────────────────────────────────────

async function main() {
  console.log("🤖 X Approval Bot iniciado");
  console.log(`Modo: ${DRY_RUN ? "DRY-RUN" : "LIVE"}`);

  if (!TELEGRAM_BOT_TOKEN) {
    console.error("❌ TELEGRAM_BOT_TOKEN não configurado");
    console.log("Configure em ~/.egos/secrets.env:");
    console.log("  TELEGRAM_BOT_TOKEN=seu_token");
    console.log("  TELEGRAM_ADMIN_CHAT_ID=seu_chat_id");
    process.exit(1);
  }

  let offset = 0;

  // Loop de polling
  while (true) {
    try {
      const updates = await getTelegramUpdates(offset);

      for (const update of updates) {
        offset = Math.max(offset, update.update_id + 1);

        // Mensagem de texto
        if (update.message?.text) {
          const chatId = update.message.chat.id;
          const text = update.message.text;
          const username = update.message.from?.username;

          console.log(`📩 ${username}: ${text.slice(0, 50)}`);

          if (text.startsWith("/")) {
            await handleCommand(chatId, text, username);
          }
        }

        // Callback de botões inline
        if (update.callback_query) {
          await handleCallback(update.callback_query);
        }
      }
    } catch (error) {
      console.error("❌ Erro no loop:", error);
    }

    // Aguardar antes de próximo poll
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

// Run
main().catch(console.error);
