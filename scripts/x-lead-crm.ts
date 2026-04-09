#!/usr/bin/env bun
/**
 * X-COM-012: Lead CRM Tracking
 * Sistema de tracking de leads do X.com no Supabase
 * 
 * @task X-COM-012
 * @priority P1
 */

import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.SUPABASE_URL || "";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || "";

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error("❌ SUPABASE_URL e SUPABASE_SERVICE_KEY necessários");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

interface Lead {
  id?: string;
  x_handle: string;
  x_display_name?: string;
  source: "dm" | "mention" | "search" | "viral" | "manual";
  status: "new" | "contacted" | "engaged" | "qualified" | "converted" | "lost";
  interest_signals: string[];
  first_contact_at: string;
  last_interaction_at: string;
  notes?: string;
  tags?: string[];
  thread_id?: string;
  tweet_id?: string;
  score: number; // 0-100 lead score
}

// SQL para criar tabela (se não existir)
const CREATE_TABLE_SQL = `
CREATE TABLE IF NOT EXISTS x_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  x_handle TEXT NOT NULL UNIQUE,
  x_display_name TEXT,
  source TEXT NOT NULL CHECK (source IN ('dm', 'mention', 'search', 'viral', 'manual')),
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'engaged', 'qualified', 'converted', 'lost')),
  interest_signals TEXT[] DEFAULT '{}',
  first_contact_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_interaction_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  notes TEXT,
  tags TEXT[] DEFAULT '{}',
  thread_id TEXT,
  tweet_id TEXT,
  score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_x_leads_status ON x_leads(status);
CREATE INDEX IF NOT EXISTS idx_x_leads_source ON x_leads(source);
CREATE INDEX IF NOT EXISTS idx_x_leads_score ON x_leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_x_leads_tags ON x_leads USING gin(tags);

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_x_leads_updated_at ON x_leads;
CREATE TRIGGER update_x_leads_updated_at
  BEFORE UPDATE ON x_leads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
`;

class LeadCRM {
  async init(): Promise<void> {
    console.log("🔧 Verificando/criando tabela x_leads...");
    const { error } = await supabase.rpc("exec_sql", { sql: CREATE_TABLE_SQL });
    if (error) {
      console.log("⚠️ RPC exec_sql não disponível, tentando query direta...");
      // Tabela deve ser criada via migration
    }
    console.log("✅ LeadCRM inicializado");
  }

  async addLead(lead: Omit<Lead, "id">): Promise<{ success: boolean; lead?: Lead; error?: string }> {
    // Calcular score baseado em signals
    const score = this.calculateScore(lead.interest_signals, lead.source);
    
    const leadWithScore = { ...lead, score };
    
    const { data, error } = await supabase
      .from("x_leads")
      .insert([leadWithScore])
      .select()
      .single();
    
    if (error) {
      if (error.message.includes("unique constraint")) {
        return { success: false, error: "Lead já existe" };
      }
      return { success: false, error: error.message };
    }
    
    console.log(`✅ Lead adicionado: @${lead.x_handle} (score: ${score})`);
    return { success: true, lead: data as Lead };
  }

  async updateLead(xHandle: string, updates: Partial<Lead>): Promise<boolean> {
    const { error } = await supabase
      .from("x_leads")
      .update({ ...updates, last_interaction_at: new Date().toISOString() })
      .eq("x_handle", xHandle);
    
    if (error) {
      console.error("❌ Erro atualizando lead:", error);
      return false;
    }
    
    console.log(`✅ Lead atualizado: @${xHandle}`);
    return true;
  }

  async getLeads(filters?: {
    status?: Lead["status"];
    source?: Lead["source"];
    minScore?: number;
    tag?: string;
    limit?: number;
  }): Promise<Lead[]> {
    let query = supabase
      .from("x_leads")
      .select("*")
      .order("score", { ascending: false })
      .order("last_interaction_at", { ascending: false });
    
    if (filters?.status) {
      query = query.eq("status", filters.status);
    }
    if (filters?.source) {
      query = query.eq("source", filters.source);
    }
    if (filters?.minScore) {
      query = query.gte("score", filters.minScore);
    }
    if (filters?.tag) {
      query = query.contains("tags", [filters.tag]);
    }
    if (filters?.limit) {
      query = query.limit(filters.limit);
    }
    
    const { data, error } = await query;
    
    if (error) {
      console.error("❌ Erro buscando leads:", error);
      return [];
    }
    
    return data as Lead[];
  }

  async getStats(): Promise<{
    total: number;
    byStatus: Record<string, number>;
    bySource: Record<string, number>;
    avgScore: number;
    hotLeads: number; // score >= 70
  }> {
    const { data, error } = await supabase
      .from("x_leads")
      .select("status, source, score");
    
    if (error || !data) {
      return { total: 0, byStatus: {}, bySource: {}, avgScore: 0, hotLeads: 0 };
    }
    
    const stats = {
      total: data.length,
      byStatus: {} as Record<string, number>,
      bySource: {} as Record<string, number>,
      avgScore: 0,
      hotLeads: 0
    };
    
    let totalScore = 0;
    
    for (const lead of data) {
      stats.byStatus[lead.status] = (stats.byStatus[lead.status] || 0) + 1;
      stats.bySource[lead.source] = (stats.bySource[lead.source] || 0) + 1;
      totalScore += lead.score || 0;
      if (lead.score >= 70) stats.hotLeads++;
    }
    
    stats.avgScore = Math.round(totalScore / data.length);
    
    return stats;
  }

  private calculateScore(signals: string[], source: string): number {
    let score = 0;
    
    // Base score por source
    const sourceScores: Record<string, number> = {
      dm: 40,
      mention: 30,
      viral: 35,
      search: 20,
      manual: 25
    };
    score += sourceScores[source] || 20;
    
    // Signals adicionais
    const signalScores: Record<string, number> = {
      "price_ask": 25,
      "demo_request": 30,
      "integration_ask": 20,
      "osint_interest": 15,
      "ai_interest": 15,
      "govtech_interest": 20,
      "follow_up": 10,
      "shared_content": 10,
      "compliment": 5
    };
    
    for (const signal of signals) {
      score += signalScores[signal] || 5;
    }
    
    return Math.min(100, score);
  }
}

// CLI interface
async function main() {
  const crm = new LeadCRM();
  await crm.init();
  
  const command = process.argv[2];
  
  switch (command) {
    case "add": {
      const handle = process.argv[3];
      const source = (process.argv[4] as Lead["source"]) || "manual";
      
      if (!handle) {
        console.log("Uso: bun x-lead-crm.ts add @handle [source]");
        process.exit(1);
      }
      
      const result = await crm.addLead({
        x_handle: handle.replace("@", ""),
        source,
        status: "new",
        interest_signals: ["manual_add"],
        first_contact_at: new Date().toISOString(),
        last_interaction_at: new Date().toISOString(),
        tags: ["manual"],
        score: 0
      });
      
      console.log(result.success ? "✅ Adicionado" : `❌ ${result.error}`);
      break;
    }
    
    case "list": {
      const status = process.argv[3] as Lead["status"];
      const leads = await crm.getLeads(status ? { status } : {});
      
      console.log(`\n📊 ${leads.length} leads encontrados:\n`);
      console.table(leads.map(l => ({
        handle: `@${l.x_handle}`,
        status: l.status,
        source: l.source,
        score: l.score,
        signals: l.interest_signals?.join(", ") || "-"
      })));
      break;
    }
    
    case "stats": {
      const stats = await crm.getStats();
      console.log("\n📈 Stats do Lead CRM:");
      console.log(`   Total: ${stats.total}`);
      console.log(`   Hot leads (>=70): ${stats.hotLeads}`);
      console.log(`   Score médio: ${stats.avgScore}`);
      console.log(`   Por status:`, stats.byStatus);
      console.log(`   Por source:`, stats.bySource);
      break;
    }
    
    default:
      console.log(`
🎯 X Lead CRM — X-COM-012

Comandos:
  add @handle [source]     Adicionar lead manualmente
  list [status]           Listar leads (opção: new|contacted|engaged|qualified|converted|lost)
  stats                   Estatísticas do CRM

Sources: dm, mention, search, viral, manual
      `);
  }
}

if (import.meta.main) {
  main();
}

export { LeadCRM, type Lead };
