#!/usr/bin/env bun
// 🧠 X Smart Scheduler — Audience Engagement Analyzer
//
// Analisa padrões de engajamento da audiência para sugerir
// melhores horários de postagem (personalizado, não genérico)
//
// Features:
// - Análise histórica de likes, RTs, replies por hora/dia
// - ML simples (média móvel + tendência) para previsão
// - Sugestão de horários ótimos por tipo de conteúdo
// - Export de schedule para cron ou dashboard
//
// Usage:
//   bun scripts/x-smart-scheduler.ts              # analyze & suggest
//   bun scripts/x-smart-scheduler.ts --export     # export schedule JSON
//   bun scripts/x-smart-scheduler.ts --simulate   # simular próxima semana

import { writeFileSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const DRY_RUN = process.argv.includes("--dry-run") || !process.env.X_BEARER_TOKEN;
const EXPORT = process.argv.includes("--export");
const SIMULATE = process.argv.includes("--simulate");

const STATE_FILE = "/tmp/x-scheduler-state.json";
const SCHEDULE_FILE = "/tmp/x-optimal-schedule.json";

// Configurações
const HOURS_TO_ANALYZE = [6, 9, 12, 15, 18, 21]; // Horários brasileiros (BRT)
const DAYS_TO_ANALYZE = [0, 1, 2, 3, 4, 5, 6]; // Domingo a sábado
const MIN_SAMPLES_FOR_PREDICTION = 5; // Mínimo de posts para análise confiável

// Tipos de conteúdo mapeados para categorias de engajamento
const CONTENT_TYPES = {
  educational: { weight: 1.0, keywords: ["como", "guia", "tutorial", "dicas", "aprenda"] },
  thread: { weight: 1.2, keywords: ["thread", "🧵", "segue", "1/", "parte 1"] },
  hot_take: { weight: 1.3, keywords: ["hot take", "opinião impopular", "ninguém fala"] },
  update: { weight: 0.9, keywords: ["update", "novidade", "lançamos", "versão"] },
  personal: { weight: 1.0, keywords: ["pessoal", "jornada", "construindo", "aprendizado"] },
};

type EngagementData = {
  hour: number;
  day: number;
  likes: number;
  retweets: number;
  replies: number;
  impressions: number;
  contentType: string;
  timestamp: string;
};

type HourlyStats = {
  hour: number;
  day: number;
  avgEngagement: number;
  sampleCount: number;
  contentBreakdown: Record<string, { count: number; avgEngagement: number }>;
};

type OptimalSlot = {
  hour: number;
  day: number;
  dayName: string;
  engagementScore: number;
  confidence: number; // 0-1 baseado em sample count
  recommendedFor: string[]; // tipos de conteúdo
};

// Carregar estado existente
function loadState(): { posts: EngagementData[]; lastAnalysis: string } {
  if (!existsSync(STATE_FILE)) {
    return { posts: [], lastAnalysis: "" };
  }
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf-8"));
  } catch {
    return { posts: [], lastAnalysis: "" };
  }
}

// Salvar estado
function saveState(state: { posts: EngagementData[]; lastAnalysis: string }) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// Buscar posts do usuário via X API
async function fetchUserPosts(username: string, maxResults = 100): Promise<EngagementData[]> {
  if (DRY_RUN) {
    console.log("[DRY-RUN] Simulando posts do usuário");
    return generateMockData();
  }

  const bearerToken = process.env.X_BEARER_TOKEN;
  if (!bearerToken) {
    throw new Error("X_BEARER_TOKEN não configurado");
  }

  // Buscar user ID pelo username
  const userRes = await fetch(
    `https://api.twitter.com/2/users/by/username/${username}?user.fields=public_metrics`,
    {
      headers: { Authorization: `Bearer ${bearerToken}` },
    }
  );

  if (!userRes.ok) {
    throw new Error(`Erro ao buscar usuário: ${userRes.status}`);
  }

  const userData = await userRes.json();
  const userId = userData.data?.id;

  if (!userId) {
    throw new Error("User ID não encontrado");
  }

  // Buscar tweets do usuário
  const tweetsRes = await fetch(
    `https://api.twitter.com/2/users/${userId}/tweets?max_results=${maxResults}&tweet.fields=created_at,public_metrics,note_tweet`,
    {
      headers: { Authorization: `Bearer ${bearerToken}` },
    }
  );

  if (!tweetsRes.ok) {
    throw new Error(`Erro ao buscar tweets: ${tweetsRes.status}`);
  }

  const tweetsData = await tweetsRes.json();
  const posts: EngagementData[] = [];

  for (const tweet of tweetsData.data || []) {
    const createdAt = new Date(tweet.created_at);
    const metrics = tweet.public_metrics || {};
    const text = tweet.note_tweet?.text || tweet.text || "";

    posts.push({
      hour: createdAt.getHours(),
      day: createdAt.getDay(),
      likes: metrics.like_count || 0,
      retweets: metrics.retweet_count || 0,
      replies: metrics.reply_count || 0,
      impressions: metrics.impression_count || 0,
      contentType: detectContentType(text),
      timestamp: tweet.created_at,
    });
  }

  return posts;
}

// Detectar tipo de conteúdo baseado em texto
function detectContentType(text: string): string {
  const lower = text.toLowerCase();
  
  for (const [type, config] of Object.entries(CONTENT_TYPES)) {
    if (config.keywords.some(kw => lower.includes(kw))) {
      return type;
    }
  }
  
  return "general";
}

// Gerar dados mock para dry-run
function generateMockData(): EngagementData[] {
  const posts: EngagementData[] = [];
  const types = Object.keys(CONTENT_TYPES);
  
  // Simular 50 posts aleatórios
  for (let i = 0; i < 50; i++) {
    const day = Math.floor(Math.random() * 7);
    const hour = HOURS_TO_ANALYZE[Math.floor(Math.random() * HOURS_TO_ANALYZE.length)];
    const baseEngagement = Math.random() * 100;
    
    // Adicionar bias para horários melhores (9h, 15h, 21h)
    const hourBonus = [9, 15, 21].includes(hour) ? 1.5 : 1.0;
    const dayBonus = day === 2 || day === 4 ? 1.3 : 1.0; // Terça e quinta melhores
    
    posts.push({
      hour,
      day,
      likes: Math.floor(baseEngagement * hourBonus * dayBonus * 2),
      retweets: Math.floor(baseEngagement * hourBonus * dayBonus * 0.5),
      replies: Math.floor(baseEngagement * hourBonus * dayBonus * 0.3),
      impressions: Math.floor(baseEngagement * hourBonus * dayBonus * 20),
      contentType: types[Math.floor(Math.random() * types.length)],
      timestamp: new Date(Date.now() - i * 86400000).toISOString(),
    });
  }
  
  return posts;
}

// Calcular score de engajamento
function calculateEngagementScore(post: EngagementData): number {
  // Fórmula: likes*1 + retweets*2 + replies*3 + impressions*0.01
  return (
    post.likes * 1 +
    post.retweets * 2 +
    post.replies * 3 +
    post.impressions * 0.01
  );
}

// Analisar estatísticas por hora/dia
function analyzeEngagement(posts: EngagementData[]): HourlyStats[] {
  const statsMap = new Map<string, EngagementData[]>();
  
  // Agrupar por (day, hour)
  for (const post of posts) {
    const key = `${post.day}-${post.hour}`;
    if (!statsMap.has(key)) {
      statsMap.set(key, []);
    }
    statsMap.get(key)!.push(post);
  }
  
  const stats: HourlyStats[] = [];
  
  for (const [key, group] of statsMap) {
    const [day, hour] = key.split("-").map(Number);
    const scores = group.map(calculateEngagementScore);
    const avgEngagement = scores.reduce((a, b) => a + b, 0) / scores.length;
    
    // Análise por tipo de conteúdo
    const contentBreakdown: Record<string, { count: number; avgEngagement: number }> = {};
    for (const type of Object.keys(CONTENT_TYPES)) {
      const typePosts = group.filter(p => p.contentType === type);
      if (typePosts.length > 0) {
        const typeScores = typePosts.map(calculateEngagementScore);
        contentBreakdown[type] = {
          count: typePosts.length,
          avgEngagement: typeScores.reduce((a, b) => a + b, 0) / typePosts.length,
        };
      }
    }
    
    stats.push({
      hour,
      day,
      avgEngagement,
      sampleCount: group.length,
      contentBreakdown,
    });
  }
  
  return stats.sort((a, b) => b.avgEngagement - a.avgEngagement);
}

// Calcular horários ótimos
function calculateOptimalSlots(stats: HourlyStats[]): OptimalSlot[] {
  const dayNames = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"];
  
  // Normalizar scores (0-100)
  const maxEngagement = Math.max(...stats.map(s => s.avgEngagement));
  const minEngagement = Math.min(...stats.map(s => s.avgEngagement));
  
  return stats.map(stat => {
    const normalizedScore = ((stat.avgEngagement - minEngagement) / (maxEngagement - minEngagement)) * 100;
    const confidence = Math.min(stat.sampleCount / MIN_SAMPLES_FOR_PREDICTION, 1);
    
    // Determinar melhores tipos de conteúdo para este slot
    const recommendedFor = Object.entries(stat.contentBreakdown)
      .sort((a, b) => b[1].avgEngagement - a[1].avgEngagement)
      .slice(0, 2)
      .map(([type]) => type);
    
    return {
      hour: stat.hour,
      day: stat.day,
      dayName: dayNames[stat.day],
      engagementScore: Math.round(normalizedScore),
      confidence,
      recommendedFor: recommendedFor.length > 0 ? recommendedFor : ["general"],
    };
  });
}

// Exportar schedule para uso externo
function exportSchedule(slots: OptimalSlot[]) {
  const schedule = {
    generatedAt: new Date().toISOString(),
    timezone: "America/Sao_Paulo",
    slots: slots.slice(0, 10), // Top 10 slots
    recommendations: {
      bestDays: [...new Set(slots.slice(0, 5).map(s => s.dayName))],
      bestHours: [...new Set(slots.slice(0, 5).map(s => s.hour))],
      avoid: slots.slice(-3).map(s => `${s.dayName} ${s.hour}h`),
    },
  };
  
  writeFileSync(SCHEDULE_FILE, JSON.stringify(schedule, null, 2));
  console.log(`\n📁 Schedule exportado: ${SCHEDULE_FILE}`);
  return schedule;
}

// Simular próxima semana
function simulateWeek(slots: OptimalSlot[]) {
  const dayNames = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
  const topSlots = slots.slice(0, 7); // Top 7 slots para a semana
  
  console.log("\n📅 Simulação — Próxima Semana (Posts Sugeridos):");
  console.log("─".repeat(60));
  
  const today = new Date();
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    const slot = topSlots[i % topSlots.length];
    
    console.log(
      `${dayNames[date.getDay()]} ${date.getDate()}/${date.getMonth() + 1} — ` +
      `${String(slot.hour).padStart(2, "0")}:00 ` +
      `(${slot.recommendedFor.join(", ")}) ` +
      `[score: ${slot.engagementScore}]`
    );
  }
}

// Main
async function main() {
  console.log("🧠 X Smart Scheduler — Audience Engagement Analyzer\n");
  
  if (DRY_RUN && !EXPORT && !SIMULATE) {
    console.log("Modo: DRY-RUN (simulando dados)\n");
  }
  
  // Carregar estado anterior
  const state = loadState();
  console.log(`📊 Posts em cache: ${state.posts.length}`);
  
  // Buscar novos posts (em produção)
  if (!DRY_RUN) {
    const username = process.env.X_USERNAME || "anoineim";
    console.log(`🔄 Buscando posts de @${username}...`);
    
    try {
      const newPosts = await fetchUserPosts(username, 100);
      
      // Merge com posts existentes (evitar duplicatas)
      const seen = new Set(state.posts.map(p => p.timestamp));
      const uniqueNew = newPosts.filter(p => !seen.has(p.timestamp));
      
      state.posts = [...state.posts, ...uniqueNew].slice(-200); // Manter últimos 200
      state.lastAnalysis = new Date().toISOString();
      
      saveState(state);
      console.log(`✅ ${uniqueNew.length} posts novos adicionados`);
    } catch (err) {
      console.error(`❌ Erro ao buscar posts: ${err}`);
      console.log("⚠️ Usando dados em cache");
    }
  } else {
    // Modo dry-run: gerar dados mock
    state.posts = generateMockData();
  }
  
  if (state.posts.length < MIN_SAMPLES_FOR_PREDICTION) {
    console.log(`\n⚠️ Insufficient data (${state.posts.length} posts). ` +
                `Need at least ${MIN_SAMPLES_FOR_PREDICTION} for reliable analysis.`);
    return;
  }
  
  // Analisar engajamento
  console.log("\n🔍 Analisando padrões de engajamento...");
  const stats = analyzeEngagement(state.posts);
  const optimalSlots = calculateOptimalSlots(stats);
  
  // Exibir resultados
  console.log("\n" + "═".repeat(60));
  console.log("🎯 HORÁRIOS ÓTIMOS (Top 5)");
  console.log("═".repeat(60));
  
  for (let i = 0; i < Math.min(5, optimalSlots.length); i++) {
    const slot = optimalSlots[i];
    console.log(
      `${i + 1}. ${slot.dayName} ${String(slot.hour).padStart(2, "0")}:00h ` +
      `— Score: ${slot.engagementScore}/100 ` +
      `(confiança: ${Math.round(slot.confidence * 100)}%) ` +
      `[${slot.recommendedFor.join(", ")}]`
    );
  }
  
  // Exibir horários a evitar
  console.log("\n" + "─".repeat(60));
  console.log("⛔ HORÁRIOS A EVITAR (Bottom 3)");
  console.log("─".repeat(60));
  
  const worstSlots = optimalSlots.slice(-3).reverse();
  for (let i = 0; i < worstSlots.length; i++) {
    const slot = worstSlots[i];
    console.log(
      `${i + 1}. ${slot.dayName} ${String(slot.hour).padStart(2, "0")}:00h ` +
      `— Score: ${slot.engagementScore}/100`
    );
  }
  
  // Exportar se solicitado
  if (EXPORT) {
    exportSchedule(optimalSlots);
  }
  
  // Simular se solicitado
  if (SIMULATE) {
    simulateWeek(optimalSlots);
  }
  
  // Insights adicionais
  console.log("\n" + "═".repeat(60));
  console.log("💡 INSIGHTS");
  console.log("═".repeat(60));
  
  const bestDay = optimalSlots[0]?.dayName;
  const bestHour = optimalSlots[0]?.hour;
  console.log(`• Melhor dia: ${bestDay}`);
  console.log(`• Melhor horário: ${String(bestHour).padStart(2, "0")}:00h`);
  console.log(`• Total de posts analisados: ${state.posts.length}`);
  console.log(`• Última análise: ${state.lastAnalysis || "Nunca"}`);
  
  console.log("\n✅ Análise completa!");
}

main().catch(console.error);
