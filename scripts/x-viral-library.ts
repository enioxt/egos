#!/usr/bin/env bun
/**
 * X-COM-011: Viral Content Library
 * Biblioteca de conteúdo viral por nicho com análise de padrões
 * 
 * @task X-COM-011
 * @priority P1
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

const LIBRARY_PATH = process.env.VIRAL_LIBRARY_PATH || "./data/viral-library.json";

interface ViralContent {
  id: string;
  x_post_id?: string;
  x_handle: string;
  content: string;
  niche: string;
  engagement: {
    likes: number;
    replies: number;
    retweets: number;
    impressions: number;
  };
  score: number; // viral score 0-100
  patterns: string[];
  postedAt: string;
  capturedAt: string;
  tags: string[];
}

interface PatternAnalysis {
  pattern: string;
  frequency: number;
  avgEngagement: number;
  examples: string[];
}

const VIRAL_NICHES = [
  "osint",
  "ai_frameworks",
  "govtech",
  "investigation",
  "data_science",
  "security",
  "brazil_tech",
  "policia",
  "transparencia"
];

const CONTENT_PATTERNS = [
  "thread_educational",
  "screenshot_results",
  "before_after",
  "how_to_guide",
  "myth_busting",
  "case_study",
  "tool_showcase",
  "data_visualization",
  "breaking_news",
  "hot_take",
  "behind_scenes",
  "user_testimonial",
  "comparison",
  "question_hook"
];

class ViralLibrary {
  private library: ViralContent[] = [];

  constructor() {
    this.load();
  }

  private load(): void {
    if (existsSync(LIBRARY_PATH)) {
      try {
        const data = JSON.parse(readFileSync(LIBRARY_PATH, "utf-8"));
        this.library = data.contents || [];
        console.log(`📚 Biblioteca carregada: ${this.library.length} itens`);
      } catch (e) {
        this.library = [];
      }
    }
  }

  private save(): void {
    const data = {
      meta: {
        version: "1.0",
        updatedAt: new Date().toISOString(),
        totalItems: this.library.length,
        niches: [...new Set(this.library.map(c => c.niche))]
      },
      contents: this.library
    };
    
    const dir = LIBRARY_PATH.substring(0, LIBRARY_PATH.lastIndexOf("/"));
    if (!existsSync(dir)) {
      Bun.write(dir + "/.gitkeep", "");
    }
    
    writeFileSync(LIBRARY_PATH, JSON.stringify(data, null, 2));
  }

  add(content: Omit<ViralContent, "id" | "capturedAt" | "score">): ViralContent {
    const score = this.calculateViralScore(content.engagement);
    
    const item: ViralContent = {
      ...content,
      id: `viral_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      capturedAt: new Date().toISOString(),
      score,
      patterns: this.detectPatterns(content.content)
    };
    
    this.library.push(item);
    this.save();
    
    console.log(`✅ Adicionado à biblioteca viral (score: ${score}): ${content.content.substring(0, 50)}...`);
    return item;
  }

  getByNiche(niche: string, minScore = 50, limit = 10): ViralContent[] {
    return this.library
      .filter(c => c.niche === niche && c.score >= minScore)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  getByPattern(pattern: string, limit = 10): ViralContent[] {
    return this.library
      .filter(c => c.patterns.includes(pattern))
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  analyzePatterns(): PatternAnalysis[] {
    const patternMap = new Map<string, { count: number; engagement: number; examples: string[] }>();
    
    for (const content of this.library) {
      for (const pattern of content.patterns) {
        const existing = patternMap.get(pattern) || { count: 0, engagement: 0, examples: [] };
        existing.count++;
        existing.engagement += this.calculateTotalEngagement(content.engagement);
        if (existing.examples.length < 3) {
          existing.examples.push(content.content.substring(0, 100));
        }
        patternMap.set(pattern, existing);
      }
    }
    
    return Array.from(patternMap.entries())
      .map(([pattern, data]) => ({
        pattern,
        frequency: data.count,
        avgEngagement: Math.round(data.engagement / data.count),
        examples: data.examples
      }))
      .sort((a, b) => b.avgEngagement - a.avgEngagement);
  }

  getInspiration(niche: string, targetPattern?: string): string {
    const candidates = targetPattern 
      ? this.getByPattern(targetPattern, 5)
      : this.getByNiche(niche, 60, 5);
    
    if (candidates.length === 0) {
      return "Nenhum conteúdo de referência encontrado para este nicho.";
    }
    
    const selected = candidates[Math.floor(Math.random() * candidates.length)];
    
    return `[Inspiração — score ${selected.score}]
Nicho: ${selected.niche}
Padrões: ${selected.patterns.join(", ")}
Engajamento: ${selected.engagement.likes} likes, ${selected.engagement.replies} replies

Conteúdo de referência:
"${selected.content}"

💡 Dica: Use este como referência de estrutura, não copie diretamente.`;
  }

  generateIdeas(niche: string, count = 5): string[] {
    const topContent = this.getByNiche(niche, 50, 20);
    const patterns = this.analyzePatterns().slice(0, 5);
    
    const ideas: string[] = [];
    const templates: Record<string, string[]> = {
      thread_educational: [
        "🧵 Thread: Como [técnica] mudou minha forma de [atividade]",
        "Mini-curso grátis: [tema] em 5 passos",
        "O que ninguém te conta sobre [tema]..."
      ],
      screenshot_results: [
        "Resultados de [tempo] usando [ferramenta/método]",
        "Antes/Depois: implementando [solução]",
        "Dashboard real de [métrica]"
      ],
      how_to_guide: [
        "Como [fazer algo] em [tempo] (guia passo a passo)",
        "Tutorial: [tema] para iniciantes",
        "Setup completo de [ferramenta]"
      ],
      data_visualization: [
        "📊 Dados revelam: [insight surpreendente]",
        "Mapeando [tema] no Brasil",
        "Análise de [quantidade] casos: o que aprendi"
      ],
      hot_take: [
        "Opinião impopular: [tema controversia]",
        "O que a maioria entende errado sobre [tema]",
        "Desmistificando [conceito popular]"
      ]
    };
    
    for (let i = 0; i < count; i++) {
      const randomPattern = patterns[Math.floor(Math.random() * patterns.length)]?.pattern || "thread_educational";
      const patternTemplates = templates[randomPattern] || templates.thread_educational;
      const template = patternTemplates[Math.floor(Math.random() * patternTemplates.length)];
      
      // Personalizar com palavras-chave do nicho
      const niches: Record<string, string[]> = {
        osint: ["OSINT", "investigação", "dados abertos", "inteligência"],
        ai_frameworks: ["AI agents", "automação", "LLMs", "orquestração"],
        govtech: ["transparência", "dados públicos", "licitações", "fiscalização"],
        investigation: ["análise", "evidências", "casos", "perícia"],
        policia: ["PCMG", "inteligência policial", "SIGMAD", "sistemas"]
      };
      
      const keywords = niches[niche] || ["tecnologia", "inovação", "dados"];
      const keyword = keywords[Math.floor(Math.random() * keywords.length)];
      
      ideas.push(template.replace(/\[.*?\]/g, () => keyword));
    }
    
    return [...new Set(ideas)]; // deduplicar
  }

  stats(): {
    total: number;
    byNiche: Record<string, number>;
    byPattern: Record<string, number>;
    avgScore: number;
    topContent: ViralContent[];
  } {
    const byNiche: Record<string, number> = {};
    const byPattern: Record<string, number> = {};
    let totalScore = 0;
    
    for (const content of this.library) {
      byNiche[content.niche] = (byNiche[content.niche] || 0) + 1;
      totalScore += content.score;
      
      for (const pattern of content.patterns) {
        byPattern[pattern] = (byPattern[pattern] || 0) + 1;
      }
    }
    
    return {
      total: this.library.length,
      byNiche,
      byPattern,
      avgScore: this.library.length ? Math.round(totalScore / this.library.length) : 0,
      topContent: this.library.sort((a, b) => b.score - a.score).slice(0, 5)
    };
  }

  private calculateViralScore(engagement: ViralContent["engagement"]): number {
    // Fórmula de viralidade ponderada
    const weighted = 
      engagement.likes * 1 +
      engagement.replies * 3 + // replies são mais valiosas
      engagement.retweets * 4 + // RTs são ouro
      (engagement.impressions / 1000) * 0.5;
    
    // Normalizar para 0-100
    const normalized = Math.min(100, Math.round(weighted / 100));
    
    return normalized;
  }

  private detectPatterns(content: string): string[] {
    const patterns: string[] = [];
    const lower = content.toLowerCase();
    
    if (content.includes("🧵") || content.includes("Thread") || content.includes("1/")) {
      patterns.push("thread_educational");
    }
    if (lower.includes("como ") && (lower.includes("passo") || lower.includes("guia"))) {
      patterns.push("how_to_guide");
    }
    if (lower.includes("antes") && lower.includes("depois")) {
      patterns.push("before_after");
    }
    if (lower.includes("resultado") || lower.includes("case")) {
      patterns.push("case_study");
    }
    if (lower.includes("📊") || lower.includes("dados") || lower.includes("%")) {
      patterns.push("data_visualization");
    }
    if (lower.includes("mito") || lower.includes("verdade") || lower.includes("engano")) {
      patterns.push("myth_busting");
    }
    if (lower.includes("opinião") || lower.includes("impopular") || lower.includes("discordo")) {
      patterns.push("hot_take");
    }
    if (lower.includes("?") && content.indexOf("?") < 50) {
      patterns.push("question_hook");
    }
    if (lower.includes("ferramenta") || lower.includes("tool") || lower.includes("app")) {
      patterns.push("tool_showcase");
    }
    
    return patterns.length ? patterns : ["general"];
  }

  private calculateTotalEngagement(e: ViralContent["engagement"]): number {
    return e.likes + e.replies * 3 + e.retweets * 4;
  }
}

// CLI interface
async function main() {
  const library = new ViralLibrary();
  const command = process.argv[2];

  switch (command) {
    case "add": {
      const content = process.argv[3];
      const niche = process.argv[4] as string;
      
      if (!content || !niche) {
        console.log("Uso: bun x-viral-library.ts add 'conteúdo' nicho");
        console.log("Nichos:", VIRAL_NICHES.join(", "));
        process.exit(1);
      }
      
      library.add({
        x_handle: "manual_add",
        content,
        niche,
        engagement: { likes: 0, replies: 0, retweets: 0, impressions: 0 },
        postedAt: new Date().toISOString(),
        tags: ["manual"],
        patterns: []
      });
      break;
    }
    
    case "list": {
      const niche = process.argv[3];
      const items = niche ? library.getByNiche(niche) : library.stats().topContent;
      
      console.log(`\n📚 ${items.length} itens:`);
      items.forEach(item => {
        console.log(`\n[${item.niche}] Score: ${item.score}`);
        console.log(`${item.content.substring(0, 80)}...`);
        console.log(`Patterns: ${item.patterns.join(", ")}`);
      });
      break;
    }
    
    case "patterns": {
      const analysis = library.analyzePatterns();
      console.log("\n📊 Análise de Padrões:");
      console.table(analysis.slice(0, 10).map(p => ({
        pattern: p.pattern,
        frequency: p.frequency,
        avgEngagement: p.avgEngagement
      })));
      break;
    }
    
    case "inspire": {
      const niche = process.argv[3] || "osint";
      console.log(library.getInspiration(niche));
      break;
    }
    
    case "ideas": {
      const niche = process.argv[3] || "osint";
      const count = parseInt(process.argv[4]) || 5;
      const ideas = library.generateIdeas(niche, count);
      
      console.log(`\n💡 ${ideas.length} ideias para nicho "${niche}":\n`);
      ideas.forEach((idea, i) => console.log(`${i + 1}. ${idea}`));
      break;
    }
    
    case "stats": {
      const stats = library.stats();
      console.log("\n📈 Estatísticas da Biblioteca Viral:");
      console.log(`   Total: ${stats.total} itens`);
      console.log(`   Score médio: ${stats.avgScore}`);
      console.log(`   Por nicho:`, stats.byNiche);
      console.log(`   Por padrão:`, stats.byPattern);
      break;
    }
    
    default:
      console.log(`
📚 Viral Content Library — X-COM-011

Comandos:
  add 'conteúdo' nicho     Adicionar conteúdo à biblioteca
  list [nicho]             Listar conteúdos (opcional: filtrar nicho)
  patterns                 Analisar padrões de viralidade
  inspire [nicho]          Obter inspiração de conteúdo
  ideas [nicho] [count]    Gerar ideias baseadas em padrões
  stats                    Estatísticas da biblioteca

Nichos disponíveis: ${VIRAL_NICHES.join(", ")}
      `);
  }
}

if (import.meta.main) {
  main();
}

export { ViralLibrary, type ViralContent };
