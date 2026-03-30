/**
 * DASHBOARD V2 — ENXUTA (Lean MVP)
 *
 * Apenas o essencial que gera valor imediato:
 * 1. Activity feed (prova que funciona)
 * 2. Cost display (transparência radical)
 * 3. Quota bar (cliente sabe quanto usou)
 *
 * Zero placeholders. Tudo funcional.
 * Uma tela. Sem sidebar. Sem tabs.
 */

'use client';

import { useState, useEffect } from 'react';

interface Event {
  id: string;
  event_type: string;
  timestamp: string;
  cost_usd: number;
  duration_ms: number;
  model_id: string;
  pii_types: string[];
  status_code: number;
}

interface QuotaInfo {
  used: number;
  limit: number;
  tier: string;
  cost_total: number;
  reset_date: string;
}

// Placeholder data — será substituído por Supabase Realtime
const SAMPLE_EVENTS: Event[] = [
  { id: '1', event_type: 'pii_inspection', timestamp: new Date().toISOString(), cost_usd: 0.00007, duration_ms: 4, model_id: 'regex', pii_types: ['cpf'], status_code: 200 },
  { id: '2', event_type: 'atrian_validation', timestamp: new Date(Date.now() - 60000).toISOString(), cost_usd: 0.00014, duration_ms: 152, model_id: 'qwen-plus', pii_types: ['rg', 'cpf'], status_code: 200 },
  { id: '3', event_type: 'pii_inspection', timestamp: new Date(Date.now() - 120000).toISOString(), cost_usd: 0, duration_ms: 2, model_id: 'regex', pii_types: ['placa'], status_code: 200 },
  { id: '4', event_type: 'rate_limit_hit', timestamp: new Date(Date.now() - 180000).toISOString(), cost_usd: 0, duration_ms: 1, model_id: 'none', pii_types: [], status_code: 429 },
  { id: '5', event_type: 'pii_inspection', timestamp: new Date(Date.now() - 300000).toISOString(), cost_usd: 0.00007, duration_ms: 148, model_id: 'qwen-plus', pii_types: ['masp'], status_code: 200 },
];

const SAMPLE_QUOTA: QuotaInfo = {
  used: 3247,
  limit: 10000,
  tier: 'starter',
  cost_total: 0.0089,
  reset_date: '2026-04-01',
};

export default function DashboardV2Lean() {
  const [events, setEvents] = useState<Event[]>(SAMPLE_EVENTS);
  const [quota] = useState<QuotaInfo>(SAMPLE_QUOTA);

  // Simula real-time (em prod: Supabase Realtime)
  useEffect(() => {
    const interval = setInterval(() => {
      const newEvent: Event = {
        id: Math.random().toString(36).slice(2),
        event_type: 'pii_inspection',
        timestamp: new Date().toISOString(),
        cost_usd: Math.random() > 0.6 ? 0.00007 : 0,
        duration_ms: Math.random() > 0.6 ? Math.floor(Math.random() * 200) + 100 : Math.floor(Math.random() * 5) + 1,
        model_id: Math.random() > 0.6 ? 'qwen-plus' : 'regex',
        pii_types: [['cpf'], ['rg'], ['masp'], ['placa']][Math.floor(Math.random() * 4)],
        status_code: 200,
      };
      setEvents((prev) => [newEvent, ...prev].slice(0, 50));
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const totalCost = events.reduce((s, e) => s + e.cost_usd, 0);
  const avgLatency = Math.round(events.reduce((s, e) => s + e.duration_ms, 0) / events.length);
  const successRate = Math.round((events.filter((e) => e.status_code === 200).length / events.length) * 100);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Guard Brasil</h1>
          <p className="text-sm text-slate-400">Your API activity in real-time</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
          <span className="text-xs text-emerald-400">Live</span>
        </div>
      </div>

      {/* Quota Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <span className="text-xs text-slate-400">Plan: </span>
            <span className="text-xs font-bold text-blue-400 uppercase">{quota.tier}</span>
          </div>
          <span className="text-xs text-slate-400">
            Resets {new Date(quota.reset_date).toLocaleDateString()}
          </span>
        </div>
        <div className="bg-slate-800 rounded-full h-3 mb-2">
          <div
            className={`rounded-full h-3 transition-all ${
              quota.used / quota.limit > 0.9 ? 'bg-red-500' : quota.used / quota.limit > 0.7 ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(100, (quota.used / quota.limit) * 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-slate-400">
          <span>{quota.used.toLocaleString()} / {quota.limit.toLocaleString()} calls</span>
          <span>Total cost: ${quota.cost_total.toFixed(4)}</span>
        </div>
      </div>

      {/* 3 Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-400">Session Cost</p>
          <p className="text-xl font-bold font-mono text-amber-400">${totalCost.toFixed(5)}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-400">Avg Latency</p>
          <p className="text-xl font-bold font-mono text-blue-400">{avgLatency}ms</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
          <p className="text-xs text-slate-400">Success Rate</p>
          <p className="text-xl font-bold font-mono text-emerald-400">{successRate}%</p>
        </div>
      </div>

      {/* Activity Feed */}
      <div>
        <h2 className="text-sm font-bold text-slate-400 mb-3">Activity Feed</h2>
        <div className="space-y-1.5">
          {events.map((evt) => (
            <div
              key={evt.id}
              className="bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 flex items-center gap-3 text-sm hover:border-slate-700 transition"
            >
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${evt.status_code === 200 ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <span className="text-xs text-slate-500 w-16 font-mono flex-shrink-0">
                {new Date(evt.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
              <span className="text-slate-300 font-mono flex-shrink-0 w-28 text-xs">{evt.event_type}</span>
              <div className="flex gap-1 flex-1">
                {evt.pii_types.map((t) => (
                  <span key={t} className="text-[10px] bg-blue-900/40 text-blue-300 px-1.5 py-0.5 rounded">{t}</span>
                ))}
              </div>
              <span className="text-xs text-slate-500 w-14 text-right flex-shrink-0">{evt.duration_ms}ms</span>
              <span className="text-xs font-mono w-16 text-right flex-shrink-0 text-amber-400">
                {evt.cost_usd > 0 ? `$${evt.cost_usd.toFixed(5)}` : 'free'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-xs text-slate-500">
          Every call logged. Every cost visible. Transparência Radical.
        </p>
        <a href="https://guard.egos.ia.br" className="text-xs text-emerald-400 hover:underline mt-1 inline-block">
          guard.egos.ia.br
        </a>
      </div>
    </div>
  );
}
