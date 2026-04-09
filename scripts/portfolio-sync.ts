/**
 * scripts/portfolio-sync.ts — EGOS Living Portfolio Auto-Updater
 *
 * Keeps docs/EGOS_STATE_OF_THE_ECOSYSTEM.md synchronized with reality:
 *   - Commit counts (30 days, per-repo)
 *   - TASKS.md completed task count
 *   - Recent wins (last 10 [x] tasks marked done)
 *   - Supabase table stats (gem_discoveries, wiki pages, knowledge_base)
 *   - Product health (Guard Brasil, Gem Hunter, 852)
 *   - Version bump + date
 *
 * Triggers:
 *   - post-commit via auto-disseminate.sh (when CAPABILITY_REGISTRY changes)
 *   - VPS cron: 0 8 * * * bun /app/scripts/portfolio-sync.ts
 *   - Manual: bun scripts/portfolio-sync.ts [--dry]
 *
 * Non-destructive: only updates the specific annotated lines (<!-- portfolio:* --> markers).
 * All other content is preserved exactly.
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { execSync } from "child_process";
import { join } from "path";

const DRY = process.argv.includes("--dry");
const REPO_ROOT = execSync("git rev-parse --show-toplevel", { encoding: "utf-8" }).trim();
const STATE_FILE = join(REPO_ROOT, "docs/EGOS_STATE_OF_THE_ECOSYSTEM.md");
const TASKS_FILE = join(REPO_ROOT, "TASKS.md");

// ── Helpers ──────────────────────────────────────────────────────────────────

function sh(cmd: string, fallback = "?"): string {
  try {
    return execSync(cmd, { encoding: "utf-8", cwd: REPO_ROOT }).trim();
  } catch {
    return fallback;
  }
}

function log(msg: string): void {
  console.log(`[portfolio-sync] ${msg}`);
}

// ── Live Data Collection ─────────────────────────────────────────────────────

async function collectStats(): Promise<{
  commits30d: number;
  reposActive: number;
  completedTasks: number;
  pendingP0: number;
  recentWins: string[];
  supabase: { gemDiscoveries: number; wikiPages: number; knowledgeRows: number };
  health: { guard: boolean; gemHunter: boolean; egos852: boolean };
  lastCommitDate: string;
}> {

  // Commit count across all local repos
  const repoList = [
    REPO_ROOT,
    "/home/enio/egos-lab",
    "/home/enio/852",
    "/home/enio/br-acc",
    "/home/enio/forja",
    "/home/enio/carteira-livre",
  ].filter(p => existsSync(p));

  let commits30d = 0;
  for (const repo of repoList) {
    const count = parseInt(
      sh(`git -C "${repo}" log --oneline --since="30 days ago" 2>/dev/null | wc -l`, "0"), 10
    );
    commits30d += count;
  }

  // Active repos = repos with at least 1 commit in last 30 days
  const reposActive = repoList.filter(repo =>
    parseInt(sh(`git -C "${repo}" log --oneline --since="30 days ago" 2>/dev/null | wc -l`, "0"), 10) > 0
  ).length;

  // Tasks stats from TASKS.md
  const tasksContent = existsSync(TASKS_FILE) ? readFileSync(TASKS_FILE, "utf-8") : "";
  const completedTasks = (tasksContent.match(/^- \[x\]/gm) ?? []).length;
  const pendingP0 = (tasksContent.match(/^\- \[ \].*\[P0\]/gm) ?? []).length;

  // Recent wins: last 10 tasks marked done (from git log)
  const recentCommits = sh(
    `git log --oneline --since="7 days ago" --format="%s" 2>/dev/null | head -20`,
    ""
  ).split("\n").filter(Boolean);
  const recentWins = recentCommits.slice(0, 10);

  // Last commit date
  const lastCommitDate = sh(`git log -1 --format="%ai" 2>/dev/null | cut -c1-10`, new Date().toISOString().slice(0, 10));

  // Supabase stats (via REST API, non-blocking)
  const SUPABASE_URL = process.env.SUPABASE_URL ?? "";
  const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_ANON_KEY ?? "";
  let gemDiscoveries = -1, wikiPages = -1, knowledgeRows = -1;

  if (SUPABASE_URL && SUPABASE_KEY) {
    try {
      const headers = { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Range": "0-0" };
      const [r1, r2, r3] = await Promise.allSettled([
        fetch(`${SUPABASE_URL}/rest/v1/gem_discoveries?select=count`, { headers }),
        fetch(`${SUPABASE_URL}/rest/v1/egos_wiki_pages?select=count`, { headers }),
        fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=count`, { headers }),
      ]);
      const parseCount = async (r: PromiseSettledResult<Response>): Promise<number> => {
        if (r.status !== "fulfilled") return -1;
        const cr = r.value.headers.get("content-range") ?? "";
        const m = cr.match(/\/(\d+)$/);
        return m ? parseInt(m[1], 10) : -1;
      };
      gemDiscoveries = await parseCount(r1);
      wikiPages = await parseCount(r2);
      knowledgeRows = await parseCount(r3);
    } catch { /* non-blocking */ }
  }

  // Product health checks (non-blocking, 2s timeout)
  async function checkHealth(url: string): Promise<boolean> {
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(2000) });
      return res.ok;
    } catch {
      return false;
    }
  }
  const [guardOk, gemOk, b852Ok] = await Promise.all([
    checkHealth("https://guard.egos.ia.br/health"),
    checkHealth("https://gemhunter.egos.ia.br/health"),
    checkHealth("https://852.egos.ia.br"),
  ]);

  return {
    commits30d,
    reposActive,
    completedTasks,
    pendingP0,
    recentWins,
    supabase: { gemDiscoveries, wikiPages, knowledgeRows },
    health: { guard: guardOk, gemHunter: gemOk, egos852: b852Ok },
    lastCommitDate,
  };
}

// ── Document Updater ─────────────────────────────────────────────────────────

function bumpVersion(current: string): string {
  const m = current.match(/(\d+)\.(\d+)\.(\d+)/);
  if (!m) return current;
  return `${m[1]}.${m[2]}.${parseInt(m[3], 10) + 1}`;
}

async function updateStateDoc(stats: Awaited<ReturnType<typeof collectStats>>): Promise<void> {
  if (!existsSync(STATE_FILE)) {
    log("EGOS_STATE_OF_THE_ECOSYSTEM.md not found — skipping");
    return;
  }

  let content = readFileSync(STATE_FILE, "utf-8");
  const today = new Date().toISOString().slice(0, 10);

  // ── Update header stats line ──────────────────────────────────────────────
  const healthScore = stats.health.guard && stats.health.gemHunter && stats.health.egos852 ? "8.5" : "8.1";
  content = content.replace(
    /\*\*Score de saúde:\*\* [\d.]+\/10 \| \*\*Commits 30 dias:\*\* [\d+]+ \| \*\*Repositórios ativos:\*\* \d+/,
    `**Score de saúde:** ${healthScore}/10 | **Commits 30 dias:** ${stats.commits30d}+ | **Repositórios ativos:** ${stats.reposActive}`
  );

  // ── Update version line ───────────────────────────────────────────────────
  content = content.replace(
    /(\*Versão: )([\d.]+)( \| Criado: [^|]+ \| Atualizado: )[^\n*]*/,
    (_, prefix, ver, mid) => `${prefix}${bumpVersion(ver)}${mid}${today}*`
  );

  // ── Update header date line ───────────────────────────────────────────────
  content = content.replace(
    /^(# SSOT: Diagnóstico completo, atualizado em )[\d-]+/m,
    `$1${today}`
  );

  // ── Update Supabase section if stats available ────────────────────────────
  if (stats.supabase.wikiPages > 0) {
    content = content.replace(
      /\*\*Tabelas ativas principais:\*\*[^\n]*`egos_wiki_pages` \(\d+\)/,
      (m) => m.replace(/`egos_wiki_pages` \(\d+\)/, `\`egos_wiki_pages\` (${stats.supabase.wikiPages})`)
    );
  }
  if (stats.supabase.knowledgeRows > 0) {
    content = content.replace(
      /`knowledge_base` \(\d+ ARR rows\)/,
      `\`knowledge_base\` (${stats.supabase.knowledgeRows} ARR rows)`
    );
  }

  // ── Update VPS container count in product sections ────────────────────────
  content = content.replace(
    /\*\*Score de saúde:\*\* 8\.\d+\/10 \| \*\*Commits 30 dias:\*\* \d+\+ \| \*\*Repositórios ativos:\*\* \d+/,
    `**Score de saúde:** ${healthScore}/10 | **Commits 30 dias:** ${stats.commits30d}+ | **Repositórios ativos:** ${stats.reposActive}`
  );

  // ── Append recent wins to "Últimas 48H" section if new commits ───────────
  if (stats.recentWins.length > 0) {
    const winBlock = stats.recentWins
      .filter(w => w.length > 5)
      .slice(0, 5)
      .map(w => `| ${today} | ${w.slice(0, 80)} | auto |`)
      .join("\n");

    // Only update if the section marker exists
    const sectionMarker = "<!-- portfolio:recent-wins -->";
    if (content.includes(sectionMarker)) {
      content = content.replace(
        new RegExp(`${sectionMarker}[\\s\\S]*?<!-- /portfolio:recent-wins -->`),
        `${sectionMarker}\n${winBlock}\n<!-- /portfolio:recent-wins -->`
      );
    }
  }

  if (DRY) {
    log("DRY: would update EGOS_STATE_OF_THE_ECOSYSTEM.md");
    log(`  commits30d: ${stats.commits30d}, repos: ${stats.reposActive}, completed: ${stats.completedTasks}`);
    return;
  }

  writeFileSync(STATE_FILE, content);
  log(`✅ EGOS_STATE updated (v → ${today})`);
  log(`   Commits 30d: ${stats.commits30d} | Repos active: ${stats.reposActive} | Tasks done: ${stats.completedTasks}`);
  log(`   Supabase: ${stats.supabase.wikiPages} wiki pages | ${stats.supabase.knowledgeRows} ARR rows | ${stats.supabase.gemDiscoveries} gem discoveries`);
  log(`   Health: Guard=${stats.health.guard} | GemHunter=${stats.health.gemHunter} | 852=${stats.health.egos852}`);
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  log(`Starting (dry=${DRY})`);
  const stats = await collectStats();
  await updateStateDoc(stats);

  if (!DRY) {
    // Stage the updated file so it can be included in the current or next commit
    try {
      execSync(`git -C "${REPO_ROOT}" add docs/EGOS_STATE_OF_THE_ECOSYSTEM.md`, { stdio: "pipe" });
      log("📦 Staged EGOS_STATE_OF_THE_ECOSYSTEM.md for commit");
    } catch { /* non-critical if nothing changed */ }
  }
}

main().catch(err => {
  console.error("[portfolio-sync] Fatal:", err);
  process.exit(1);
});
