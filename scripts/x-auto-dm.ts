#!/usr/bin/env bun
/**
 * X-COM-013: Auto-DM Sequences
 * Workflow automatizado de DMs day 0/3/7 pós-aprovação
 * 
 * @task X-COM-013
 * @priority P1
 */

import { LeadCRM, type Lead } from "./x-lead-crm.ts";

interface DMSequence {
  id: string;
  name: string;
  trigger: "lead_qualified" | "engagement_high" | "manual";
  messages: {
    day: number; // 0 = imediato, 1 = 24h, etc
    template: string;
    condition?: string; // condição para enviar (ex: "score > 60")
  }[];
  active: boolean;
}

interface DMSent {
  id: string;
  leadHandle: string;
  sequenceId: string;
  messageDay: number;
  content: string;
  sentAt: string;
  status: "sent" | "delivered" | "replied" | "failed";
  xPostId?: string;
}

const DEFAULT_SEQUENCES: DMSequence[] = [
  {
    id: "seq_qualified",
    name: "Lead Qualificado — Boas-vindas",
    trigger: "lead_qualified",
    active: true,
    messages: [
      {
        day: 0,
        template: "Oi {{name}}! Vi seu interesse em {{topic}}. Sou do EGOS — construímos inteligência para {{use_case}}. Posso te mostrar um case similar?"
      },
      {
        day: 3,
        template: "Fala {{name}}! Conseguiu explorar o que conversamos? Tenho um material exclusivo sobre {{topic}} que pode te interessar.",
        condition: "no_reply"
      },
      {
        day: 7,
        template: "{{name}}, última mensagem: estamos rodando pilotos com {{use_case}} similar ao seu. Se quiser entrar na lista de early access, é só responder.",
        condition: "no_reply"
      }
    ]
  },
  {
    id: "seq_osint",
    name: "OSINT Interest",
    trigger: "engagement_high",
    active: true,
    messages: [
      {
        day: 0,
        template: "Oi {{name}}! Vi seu post sobre OSINT. Trabalhamos com cruzamento de dados públicos para investigação — sem violar LGPD. Quer conhecer?"
      },
      {
        day: 2,
        template: "{{name}}, montei um mini-case de como usamos OSINT em {{use_case}}. Posso te mandar o link?",
        condition: "no_reply"
      }
    ]
  },
  {
    id: "seq_govtech",
    name: "GovTech Partnership",
    trigger: "manual",
    active: true,
    messages: [
      {
        day: 0,
        template: "Olá {{name}}! Sou do EGOS Inteligência — plataforma de dados públicos para governança. Vi que {{company}} trabalha com {{topic}}. Podemos conversar sobre parceria?"
      },
      {
        day: 5,
        template: "{{name}}, seguindo nossa conversa: temos cases com {{use_case}} e API pronta para integração. Posso agendar 15min essa semana?"
      }
    ]
  }
];

class AutoDMManager {
  private crm: LeadCRM;
  private sequences: DMSequence[] = DEFAULT_SEQUENCES;
  private sentDMs: DMSent[] = [];

  constructor() {
    this.crm = new LeadCRM();
  }

  async init(): Promise<void> {
    await this.crm.init();
    console.log("📨 Auto-DM Manager inicializado");
    console.log(`   Sequências ativas: ${this.sequences.filter(s => s.active).length}`);
  }

  async processSequences(): Promise<void> {
    console.log("\n🔄 Processando sequências de DM...");
    
    for (const sequence of this.sequences.filter(s => s.active)) {
      const leads = await this.getLeadsForSequence(sequence);
      
      for (const lead of leads) {
        await this.processLeadSequence(lead, sequence);
      }
    }
  }

  async queueDM(leadHandle: string, sequenceId: string, customVars?: Record<string, string>): Promise<boolean> {
    const sequence = this.sequences.find(s => s.id === sequenceId);
    if (!sequence) {
      console.error(`❌ Sequência ${sequenceId} não encontrada`);
      return false;
    }

    const leads = await this.crm.getLeads();
    const lead = leads.find(l => l.x_handle === leadHandle.replace("@", ""));
    
    if (!lead) {
      console.error(`❌ Lead @${leadHandle} não encontrado no CRM`);
      return false;
    }

    // Verificar se já existe envio para esta sequência
    const existing = this.sentDMs.filter(s => 
      s.leadHandle === lead.x_handle && s.sequenceId === sequenceId
    );

    for (const message of sequence.messages) {
      const alreadySent = existing.some(e => e.messageDay === message.day);
      if (alreadySent) continue;

      const shouldSend = await this.shouldSendMessage(lead, message, existing);
      if (!shouldSend) continue;

      const content = this.renderTemplate(message.template, lead, customVars);
      
      console.log(`\n📨 DM para @${lead.x_handle} (day ${message.day}):`);
      console.log(`   ${content}`);
      console.log(`   [SIMULAÇÃO — em produção usaria X API v2]`);

      this.sentDMs.push({
        id: `dm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        leadHandle: lead.x_handle,
        sequenceId,
        messageDay: message.day,
        content,
        sentAt: new Date().toISOString(),
        status: "sent"
      });
    }

    return true;
  }

  getStats(): {
    totalSequences: number;
    activeSequences: number;
    totalDMsSent: number;
    byStatus: Record<string, number>;
    replyRate: number;
  } {
    const byStatus: Record<string, number> = {};
    let replied = 0;
    
    for (const dm of this.sentDMs) {
      byStatus[dm.status] = (byStatus[dm.status] || 0) + 1;
      if (dm.status === "replied") replied++;
    }

    return {
      totalSequences: this.sequences.length,
      activeSequences: this.sequences.filter(s => s.active).length,
      totalDMsSent: this.sentDMs.length,
      byStatus,
      replyRate: this.sentDMs.length ? Math.round((replied / this.sentDMs.length) * 100) : 0
    };
  }

  private async getLeadsForSequence(sequence: DMSequence): Promise<Lead[]> {
    const allLeads = await this.crm.getLeads();
    
    switch (sequence.trigger) {
      case "lead_qualified":
        return allLeads.filter(l => l.status === "qualified" && l.score >= 60);
      case "engagement_high":
        return allLeads.filter(l => l.score >= 70);
      case "manual":
        return []; // Manual não processa automaticamente
      default:
        return [];
    }
  }

  private async processLeadSequence(lead: Lead, sequence: DMSequence): Promise<void> {
    const sentForLead = this.sentDMs.filter(s => 
      s.leadHandle === lead.x_handle && s.sequenceId === sequence.id
    );

    for (const message of sequence.messages) {
      const shouldSend = await this.shouldSendMessage(lead, message, sentForLead);
      if (!shouldSend) continue;

      const content = this.renderTemplate(message.template, lead);
      
      // Simulação (em produção: POST /2/dm_conversations/with/{participant_id}/dm_events)
      console.log(`   → Day ${message.day}: ${content.substring(0, 60)}...`);
      
      this.sentDMs.push({
        id: `dm_${Date.now()}`,
        leadHandle: lead.x_handle,
        sequenceId: sequence.id,
        messageDay: message.day,
        content,
        sentAt: new Date().toISOString(),
        status: "sent"
      });
    }
  }

  private async shouldSendMessage(
    lead: Lead, 
    message: DMSequence["messages"][0],
    sentDMs: DMSent[]
  ): Promise<boolean> {
    // Verificar se já enviou para este dia
    const alreadySent = sentDMs.some(s => s.messageDay === message.day);
    if (alreadySent) return false;

    // Verificar condição
    if (message.condition === "no_reply") {
      const hasReply = sentDMs.some(s => s.status === "replied");
      if (hasReply) return false;
    }

    if (message.condition?.includes("score")) {
      const minScore = parseInt(message.condition.match(/\d+/)?.[0] || "0");
      if (lead.score < minScore) return false;
    }

    // Verificar timing
    const firstContact = new Date(lead.first_contact_at);
    const now = new Date();
    const daysSince = Math.floor((now.getTime() - firstContact.getTime()) / (1000 * 60 * 60 * 24));
    
    return daysSince >= message.day;
  }

  private renderTemplate(
    template: string, 
    lead: Lead, 
    customVars?: Record<string, string>
  ): string {
    const vars: Record<string, string> = {
      name: lead.x_display_name || lead.x_handle,
      handle: "@" + lead.x_handle,
      topic: lead.interest_signals?.[0] || "inteligência",
      use_case: this.inferUseCase(lead),
      company: customVars?.company || "sua organização",
      ...customVars
    };

    return template.replace(/\{\{(\w+)\}\}/g, (match, key) => vars[key] || match);
  }

  private inferUseCase(lead: Lead): string {
    const signals = lead.interest_signals || [];
    
    if (signals.some(s => s.includes("gov") || s.includes("transparencia"))) {
      return "fiscalização e transparência";
    }
    if (signals.some(s => s.includes("osint") || s.includes("investiga"))) {
      return "investigação e OSINT";
    }
    if (signals.some(s => s.includes("ai") || s.includes("automa"))) {
      return "automação com AI";
    }
    if (signals.some(s => s.includes("policia") || s.includes("segur"))) {
      return "inteligência policial";
    }
    
    return "análise de dados";
  }
}

// CLI interface
async function main() {
  const manager = new AutoDMManager();
  await manager.init();

  const command = process.argv[2];

  switch (command) {
    case "process": {
      await manager.processSequences();
      break;
    }

    case "queue": {
      const handle = process.argv[3];
      const sequenceId = process.argv[4] || "seq_qualified";
      
      if (!handle) {
        console.log("Uso: bun x-auto-dm.ts queue @handle [sequenceId]");
        console.log("Sequências:", DEFAULT_SEQUENCES.map(s => `${s.id} (${s.name})`).join("\n  "));
        process.exit(1);
      }

      await manager.queueDM(handle, sequenceId);
      break;
    }

    case "stats": {
      const stats = manager.getStats();
      console.log("\n📨 Stats de Auto-DM:");
      console.log(`   Sequências: ${stats.activeSequences}/${stats.totalSequences} ativas`);
      console.log(`   DMs enviados: ${stats.totalDMsSent}`);
      console.log(`   Taxa de resposta: ${stats.replyRate}%`);
      console.log(`   Por status:`, stats.byStatus);
      break;
    }

    case "sequences": {
      console.log("\n📋 Sequências disponíveis:");
      DEFAULT_SEQUENCES.forEach(seq => {
        console.log(`\n${seq.id} — ${seq.name} ${seq.active ? "✅" : "❌"}`);
        console.log(`   Trigger: ${seq.trigger}`);
        seq.messages.forEach(m => {
          console.log(`   Day ${m.day}: ${m.template.substring(0, 50)}...`);
        });
      });
      break;
    }

    default:
      console.log(`
📨 Auto-DM Sequences — X-COM-013

Comandos:
  process              Processar todas as sequências ativas
  queue @handle [seq]  Enfileirar DM para lead específico
  stats                Estatísticas de envios
  sequences            Listar sequências disponíveis

Exemplos:
  bun x-auto-dm.ts queue @usuario seq_osint
  bun x-auto-dm.ts process
      `);
  }
}

if (import.meta.main) {
  main();
}

export { AutoDMManager, DEFAULT_SEQUENCES, type DMSequence, type DMSent };
