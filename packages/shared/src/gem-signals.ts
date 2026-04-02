/**
 * Gem Hunter Signal Writer (GH-050)
 *
 * Writes high-value gem discoveries to docs/gem-hunter/signals.json
 * for ingestion by world-model.ts during /start.
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

export interface GemSignal {
  name: string;
  url: string;
  score: number;
  category: string;
  date: string;
  headline: string;
}

interface SignalsFile {
  version: string;
  signals: GemSignal[];
}

const SIGNALS_PATH = join(process.cwd(), "docs/gem-hunter/signals.json");
const MAX_SIGNALS = 50; // Keep last 50 signals

export function appendGemSignal(signal: GemSignal): void {
  let data: SignalsFile = { version: "1.0.0", signals: [] };

  try {
    if (existsSync(SIGNALS_PATH)) {
      data = JSON.parse(readFileSync(SIGNALS_PATH, "utf-8"));
    }
  } catch {}

  // Prepend new signal
  data.signals = [signal, ...data.signals].slice(0, MAX_SIGNALS);

  writeFileSync(SIGNALS_PATH, JSON.stringify(data, null, 2));
}

export function getGemSignals(): GemSignal[] {
  try {
    if (existsSync(SIGNALS_PATH)) {
      const data: SignalsFile = JSON.parse(
        readFileSync(SIGNALS_PATH, "utf-8"),
      );
      return data.signals || [];
    }
  } catch {}
  return [];
}
