#!/usr/bin/env bun
/**
 * GOV-TECH-005: PNCP Monitor
 * Monitoramento diário de licitações no Portal Nacional de Contratações Públicas
 * 
 * @task GOV-TECH-005
 * @priority P1
 */

const PNCP_API_BASE = "https://pncp.gov.br/api/pncp/v1";

interface PNCPLicitacao {
  id: string;
  numeroCompra: string;
  orgao: string;
  objeto: string;
  valorEstimado: number;
  dataPublicacao: string;
  dataAbertura?: string;
  situacao: string;
  modalidade: string;
  urlPNCP: string;
  itens: Array<{
    descricao: string;
    quantidade: number;
    valorUnitarioEstimado: number;
  }>;
}

interface MatchResult {
  licitacao: PNCPLicitacao;
  relevanceScore: number;
  matchedKeywords: string[];
  recommendedAction: string;
}

// Keywords de match para stack EGOS
const MATCH_KEYWORDS = {
  ai: ["inteligência artificial", "IA", "machine learning", "ML", "LLM", "NLP", "automação inteligente"],
  data: ["big data", "analytics", "business intelligence", "BI", "data mining", "cruzamento de dados"],
  osint: ["inteligência", "investigação", "OSINT", "informações", "dados públicos", "transparência"],
  govtech: ["govtech", "governo digital", "transformação digital", "smart city", "cidade inteligente"],
  security: ["cibersegurança", "segurança da informação", "LGPD", "proteção de dados"],
  cloud: ["cloud", "nuvem", "AWS", "Azure", "hospedagem", "SaaS"],
  integration: ["integração", "API", "sistemas", "plataforma", "software"]
};

class PNCPMonitor {
  private lastCheck: string | null = null;
  private matches: MatchResult[] = [];

  async searchLicitacoes(
    dataInicial: string,
    dataFinal: string,
    uf?: string,
    modalidade?: string
  ): Promise<PNCPLicitacao[]> {
    const params = new URLSearchParams({
      dataInicial,
      dataFinal,
      ...(uf && { uf }),
      ...(modalidade && { modalidade })
    });

    const url = `${PNCP_API_BASE}/consulta/compras?${params}`;
    
    console.log(`🔍 Buscando licitações: ${url}`);
    
    try {
      const response = await fetch(url, {
        headers: {
          "Accept": "application/json",
          "User-Agent": "EGOS-GovTech-Monitor/1.0"
        }
      });

      if (!response.ok) {
        console.error(`❌ Erro PNCP: ${response.status}`);
        return [];
      }

      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error("❌ Erro buscando licitações:", error);
      return [];
    }
  }

  async getDetalhesLicitacao(codigo: string): Promise<PNCPLicitacao | null> {
    try {
      const response = await fetch(`${PNCP_API_BASE}/compras/${codigo}`, {
        headers: {
          "Accept": "application/json",
          "User-Agent": "EGOS-GovTech-Monitor/1.0"
        }
      });

      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  analyzeMatch(licitacao: PNCPLicitacao): MatchResult | null {
    const texto = `${licitacao.objeto} ${licitacao.itens.map(i => i.descricao).join(" ")}`.toLowerCase();
    const matchedKeywords: string[] = [];
    let score = 0;

    // Analisar matches por categoria
    for (const [category, keywords] of Object.entries(MATCH_KEYWORDS)) {
      for (const keyword of keywords) {
        if (texto.includes(keyword.toLowerCase())) {
          matchedKeywords.push(`${category}:${keyword}`);
          score += this.getCategoryWeight(category);
        }
      }
    }

    // Bonus por valor
    if (licitacao.valorEstimado > 1000000) score += 10;
    if (licitacao.valorEstimado > 500000) score += 5;

    // Bonus por modalidade
    if (licitacao.modalidade?.includes("Tecnologia")) score += 5;

    if (score < 15) return null; // Threshold de relevância

    return {
      licitacao,
      relevanceScore: Math.min(100, score),
      matchedKeywords,
      recommendedAction: this.getRecommendedAction(score, licitacao)
    };
  }

  async dailyCheck(uf = "MG", dias = 7): Promise<MatchResult[]> {
    const hoje = new Date();
    const passado = new Date(hoje.getTime() - dias * 24 * 60 * 60 * 1000);
    
    const dataFinal = hoje.toISOString().split("T")[0];
    const dataInicial = passado.toISOString().split("T")[0];

    console.log(`📅 Check diário: ${dataInicial} a ${dataFinal} — UF: ${uf}`);

    const licitacoes = await this.searchLicitacoes(dataInicial, dataFinal, uf);
    console.log(`   ${licitacoes.length} licitações encontradas`);

    this.matches = [];

    for (const lic of licitacoes.slice(0, 50)) { // Limitar para performance
      const detalhes = await this.getDetalhesLicitacao(lic.id || lic.numeroCompra);
      if (!detalhes) continue;

      const match = this.analyzeMatch(detalhes);
      if (match) {
        this.matches.push(match);
      }
    }

    // Ordenar por relevância
    this.matches.sort((a, b) => b.relevanceScore - a.relevanceScore);

    this.lastCheck = new Date().toISOString();

    console.log(`   ✅ ${this.matches.length} matches relevantes`);
    return this.matches;
  }

  generateReport(): string {
    if (this.matches.length === 0) {
      return "📊 Nenhuma licitação relevante encontrada no período.";
    }

    const top = this.matches.slice(0, 10);
    const totalValue = this.matches.reduce((sum, m) => sum + m.licitacao.valorEstimado, 0);

    let report = `📊 Relatório PNCP — ${this.lastCheck?.split("T")[0]}\n\n`;
    report += `Resumo:\n`;
    report += `   Total matches: ${this.matches.length}\n`;
    report += `   Valor total: R$ ${(totalValue / 1000000).toFixed(1)}M\n`;
    report += `   Score médio: ${Math.round(this.matches.reduce((s, m) => s + m.relevanceScore, 0) / this.matches.length)}\n\n`;
    
    report += `Top 10 Oportunidades:\n\n`;

    top.forEach((match, i) => {
      const l = match.licitacao;
      report += `${i + 1}. [Score: ${match.relevanceScore}] ${l.orgao}\n`;
      report += `   Objeto: ${l.objeto.substring(0, 80)}...\n`;
      report += `   Valor: R$ ${(l.valorEstimado / 1000000).toFixed(2)}M\n`;
      report += `   Match: ${match.matchedKeywords.slice(0, 5).join(", ")}\n`;
      report += `   Ação: ${match.recommendedAction}\n`;
      report += `   Link: ${l.urlPNCP}\n\n`;
    });

    return report;
  }

  private getCategoryWeight(category: string): number {
    const weights: Record<string, number> = {
      ai: 15,
      data: 12,
      osint: 12,
      govtech: 10,
      security: 10,
      cloud: 8,
      integration: 8
    };
    return weights[category] || 5;
  }

  private getRecommendedAction(score: number, licitacao: PNCPLicitacao): string {
    if (score >= 80 && licitacao.valorEstimado > 2000000) {
      return "🎯 ALTA PRIORIDADE: Contatar parceiro SICAF imediatamente";
    }
    if (score >= 60) {
      return "📈 PRIORIDADE: Avaliar viabilidade técnica";
    }
    if (score >= 40) {
      return "📋 MONITORAR: Adicionar a watchlist";
    }
    return "📎 BAIXA: Registrar para referência";
  }
}

// CLI interface
async function main() {
  const monitor = new PNCPMonitor();
  const command = process.argv[2];

  switch (command) {
    case "check": {
      const uf = process.argv[3] || "MG";
      const dias = parseInt(process.argv[4]) || 7;
      
      await monitor.dailyCheck(uf, dias);
      console.log(monitor.generateReport());
      break;
    }

    case "search": {
      const termo = process.argv[3];
      const uf = process.argv[4] || "MG";
      
      if (!termo) {
        console.log("Uso: bun govtech-pncp-monitor.ts search 'termo' [uf]");
        process.exit(1);
      }

      const hoje = new Date().toISOString().split("T")[0];
      const passado = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
      
      const licitacoes = await monitor.searchLicitacoes(passado, hoje, uf);
      const matches = licitacoes.filter(l => 
        l.objeto.toLowerCase().includes(termo.toLowerCase())
      );

      console.log(`\n🔍 ${matches.length} resultados para "${termo}":\n`);
      matches.forEach(l => {
        console.log(`   ${l.numeroCompra} — ${l.orgao}`);
        console.log(`   ${l.objeto.substring(0, 80)}...`);
        console.log(`   Valor: R$ ${(l.valorEstimado / 1000000).toFixed(2)}M`);
        console.log(`   ${l.urlPNCP}\n`);
      });
      break;
    }

    case "report": {
      // Simular relatório baseado em dados fictícios para demo
      console.log(`
📊 Relatório PNCP — ${new Date().toISOString().split("T")[0]}

Resumo:
   Total matches: 7
   Valor total: R$ 45.2M
   Score médio: 62

Top Oportunidades:

1. [Score: 85] PCMG — Inteligência Policial
   Objeto: Contratação de solução de cruzamento de dados para investigação criminal...
   Valor: R$ 8.5M
   Match: ai:inteligência artificial, data:cruzamento de dados, osint:investigação
   Ação: 🎯 ALTA PRIORIDADE: Contatar parceiro SICAF imediatamente

2. [Score: 78] Cidade de Belo Horizonte
   Objeto: Plataforma de análise preditiva para gestão municipal...
   Valor: R$ 12.0M
   Match: ai:machine learning, data:analytics, govtech:governo digital
   Ação: 🎯 ALTA PRIORIDADE: Contatar parceiro SICAF imediatamente

3. [Score: 65] TRE-MG
   Objeto: Sistema de monitoramento de desinformação em redes sociais...
   Valor: R$ 4.2M
   Match: osint:OSINT, ai:NLP, data:big data
   Ação: 📈 PRIORIDADE: Avaliar viabilidade técnica

[... mais 4 itens]
      `);
      break;
    }

    default:
      console.log(`
🏛️ PNCP Monitor — GOV-TECH-005

Comandos:
  check [uf] [dias]    Check diário de licitações (default: MG, 7 dias)
  search 'termo' [uf]  Buscar por termo específico
  report               Gerar relatório de exemplo

Exemplos:
  bun govtech-pncp-monitor.ts check MG 7
  bun govtech-pncp-monitor.ts search "inteligência artificial" MG
      `);
  }
}

if (import.meta.main) {
  main();
}

export { PNCPMonitor, type PNCPLicitacao, type MatchResult };
