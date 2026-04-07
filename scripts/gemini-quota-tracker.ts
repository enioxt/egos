#!/usr/bin/env bun
// GEM-TOKEN-002: Gemini CLI Daily Quota Tracker
// Cron: 0 1 * * * (1am daily to log previous day's usage)
// Logs usage to Supabase table: vps_gemini_usage_log
// Install: bun add @supabase/supabase-js

type SupabaseClient = any; // Declare type to avoid import errors if not installed

let supabase: SupabaseClient = null;

const supabaseUrl = process.env.SUPABASE_URL || "";
const supabaseKey = process.env.SUPABASE_KEY || "";
const geminiLogFile = process.env.GEMINI_LOG_FILE || "/var/log/egos/gemini.log";
const telegramToken = process.env.TELEGRAM_BOT_TOKEN || "";
const telegramChatId = process.env.TELEGRAM_CHAT_ID || "";

interface GeminiUsageEntry {
  timestamp: string;
  requests: number;
  tokens_used: number;
  errors: number;
  status: "success" | "partial" | "error";
}

// Initialize Supabase client (lazy load)
async function getSupabaseClient(): Promise<SupabaseClient> {
  if (supabase) return supabase;
  try {
    const moduleName = "@supabase/supabase-js";
    const lib = await import(moduleName);
    supabase = lib.createClient(supabaseUrl, supabaseKey);
    return supabase;
  } catch (err) {
    console.warn("⚠️  Supabase not available, will log to console only");
    return null;
  }
}

/**
 * Parse Gemini CLI logs to extract usage metrics
 */
async function parseGeminiLogs(): Promise<GeminiUsageEntry> {
  try {
    const fs = await import("fs");
    const logs = fs.readFileSync(geminiLogFile, "utf-8");

    // Parse logs (format depends on Gemini CLI logging)
    const lines = logs.split("\n").slice(-1000); // Last 1000 lines for today

    let requests = 0;
    let tokensUsed = 0;
    let errors = 0;

    // Pattern matching for common Gemini CLI log formats
    for (const line of lines) {
      // Count API calls
      if (line.includes("POST") || line.includes("generateContent")) {
        requests++;
      }

      // Extract token count (typical format: "tokens: 1234")
      const tokenMatch = line.match(/tokens[:\s]+(\d+)/i);
      if (tokenMatch) {
        tokensUsed += parseInt(tokenMatch[1], 10);
      }

      // Count errors
      if (line.includes("ERROR") || line.includes("error")) {
        errors++;
      }
    }

    return {
      timestamp: new Date().toISOString(),
      requests,
      tokens_used: tokensUsed,
      errors,
      status: errors === 0 ? "success" : errors < requests * 0.1 ? "partial" : "error",
    };
  } catch (err) {
    console.error("Failed to parse Gemini logs:", err);
    return {
      timestamp: new Date().toISOString(),
      requests: 0,
      tokens_used: 0,
      errors: 1,
      status: "error",
    };
  }
}

/**
 * Log usage to Supabase
 */
async function logUsageToSupabase(usage: GeminiUsageEntry): Promise<boolean> {
  try {
    const client = await getSupabaseClient();
    if (!client) {
      console.warn("⚠️  Skipping Supabase logging (client unavailable)");
      return false;
    }

    const { error } = await client.from("vps_gemini_usage_log").insert([
      {
        date: new Date().toISOString().split("T")[0], // YYYY-MM-DD
        timestamp: usage.timestamp,
        requests: usage.requests,
        tokens_used: usage.tokens_used,
        errors: usage.errors,
        status: usage.status,
        created_at: new Date().toISOString(),
      },
    ]);

    if (error) {
      console.error("Supabase insert error:", error);
      return false;
    }

    console.log("✓ Usage logged to Supabase");
    return true;
  } catch (err) {
    console.error("Failed to log usage:", err);
    return false;
  }
}

/**
 * Check quota limits and alert if approaching
 */
async function checkQuotaThresholds(usage: GeminiUsageEntry): Promise<void> {
  // Get daily limit from Supabase config or environment
  const dailyTokenLimit = parseInt(process.env.GEMINI_DAILY_TOKEN_LIMIT || "1000000", 10);
  const dailyRequestLimit = parseInt(process.env.GEMINI_DAILY_REQUEST_LIMIT || "10000", 10);

  const tokenUsagePercent = (usage.tokens_used / dailyTokenLimit) * 100;
  const requestUsagePercent = (usage.requests / dailyRequestLimit) * 100;

  // Warn at 80%, critical at 95%
  if (tokenUsagePercent > 95 || requestUsagePercent > 95) {
    await alertQuotaCritical(usage, tokenUsagePercent, requestUsagePercent);
  } else if (tokenUsagePercent > 80 || requestUsagePercent > 80) {
    await alertQuotaWarning(usage, tokenUsagePercent, requestUsagePercent);
  }
}

/**
 * Send warning alert via Telegram
 */
async function alertQuotaWarning(
  usage: GeminiUsageEntry,
  tokenPercent: number,
  requestPercent: number
): Promise<void> {
  if (!telegramToken || !telegramChatId) return;

  const msg = `⚠️ **Gemini Quota Warning**

Daily usage approaching limits:
• Tokens: ${usage.tokens_used} (${tokenPercent.toFixed(1)}% of limit)
• Requests: ${usage.requests} (${requestPercent.toFixed(1)}% of limit)
• Errors: ${usage.errors}

Status: ${usage.status}

Time: ${new Date().toISOString()}`;

  await sendTelegramAlert(msg);
}

/**
 * Send critical alert via Telegram
 */
async function alertQuotaCritical(
  usage: GeminiUsageEntry,
  tokenPercent: number,
  requestPercent: number
): Promise<void> {
  if (!telegramToken || !telegramChatId) return;

  const msg = `🚨 **Gemini Quota CRITICAL**

Daily quota nearly exhausted:
• Tokens: ${usage.tokens_used} (${tokenPercent.toFixed(1)}% of limit)
• Requests: ${usage.requests} (${requestPercent.toFixed(1)}% of limit)
• Errors: ${usage.errors}

Action: Check fallback chain (GEM-TOKEN-001)
→ Fallback: DashScope or MiniMax available?

Time: ${new Date().toISOString()}`;

  await sendTelegramAlert(msg);
}

/**
 * Send alert via Telegram
 */
async function sendTelegramAlert(message: string): Promise<void> {
  try {
    const response = await fetch(
      `https://api.telegram.org/bot${telegramToken}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: telegramChatId,
          text: message,
          parse_mode: "Markdown",
        }),
      }
    );

    if (!response.ok) {
      console.error("Telegram alert failed:", response.statusText);
    }
  } catch (err) {
    console.error("Error sending Telegram alert:", err);
  }
}

/**
 * Main routine
 */
async function main(): Promise<void> {
  console.log("🔍 GEM-TOKEN-002: Gemini Quota Tracker");
  console.log("=====================================\n");

  // 1. Parse logs
  console.log("Parsing Gemini CLI logs...");
  const usage = await parseGeminiLogs();
  console.log(`  Requests: ${usage.requests}`);
  console.log(`  Tokens: ${usage.tokens_used}`);
  console.log(`  Errors: ${usage.errors}`);
  console.log(`  Status: ${usage.status}\n`);

  // 2. Log to Supabase
  console.log("Logging to Supabase...");
  const logSuccess = await logUsageToSupabase(usage);
  if (!logSuccess) {
    console.warn("⚠️  Failed to log to Supabase, but continuing...");
  }

  // 3. Check thresholds
  console.log("Checking quota thresholds...");
  await checkQuotaThresholds(usage);

  console.log("\n✅ Quota tracking complete");
}

// Execute (called by cron job)
if (import.meta.main) {
  main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
  });
}
