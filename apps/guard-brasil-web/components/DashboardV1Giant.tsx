/**
 * DASHBOARD V1 — GIGANTE (Full Vision)
 *
 * Tudo que teríamos se fôssemos um player global.
 * REGRA: Todas as seções não conectadas a dados reais têm badge [PLACEHOLDER].
 * Removemos o badge à medida que conectamos dados reais.
 * Esta regra se aplica a TODOS os sistemas EGOS.
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// ── Placeholder Badge ──────────────────────────────────────

function PH({ tooltip }: { tooltip?: string }) {
  return (
    <span
      title={tooltip || 'Dados simulados — conectar à API real para remover'}
      className="ml-2 text-[9px] font-bold tracking-wider uppercase bg-amber-500/20 text-amber-400 border border-amber-500/40 px-1.5 py-0.5 rounded cursor-help"
    >
      PLACEHOLDER
    </span>
  );
}

// ── Types ──────────────────────────────────────────────────

interface Event {
  id: string;
  event_type: string;
  timestamp: string;
  cost_usd: number;
  duration_ms: number;
  model_id: string;
  policy_pack: string;
  pii_types: string[];
  atrian_score: number;
  status_code: number;
}

interface Customer {
  id: string;
  name: string;
  tier: 'free' | 'starter' | 'pro' | 'business' | 'enterprise';
  calls_this_month: number;
  quota_limit: number;
  mrr: number;
}

// Scanner types (V3 embedded)
interface DataPacket {
  id: string;
  text_preview: string;
  pii_found: string[];
  atrian_score: number;
  cost_usd: number;
  duration_ms: number;
  model_used: string;
  verdict: 'clean' | 'masked' | 'blocked';
  phase: 'entering' | 'scanning' | 'processed';
  x: number;
  y: number;
}

interface StreamStats {
  total_processed: number;
  total_blocked: number;
  total_cost: number;
  avg_latency: number;
  pii_breakdown: Record<string, number>;
}

// ── Placeholder Data ───────────────────────────────────────

const PLACEHOLDER_EVENTS: Event[] = Array.from({ length: 20 }, (_, i) => ({
  id: `evt-${i}`,
  event_type: ['pii_inspection', 'atrian_validation', 'api_call', 'rate_limit_hit'][i % 4],
  timestamp: new Date(Date.now() - i * 300000).toISOString(),
  cost_usd: Math.random() * 0.001,
  duration_ms: Math.floor(Math.random() * 200) + 2,
  model_id: ['regex', 'qwen-plus', 'gemini-flash'][i % 3],
  policy_pack: ['security', 'health', 'judicial', 'financial'][i % 4],
  pii_types: [['cpf'], ['rg', 'cpf'], ['masp'], ['placa'], ['processo']][i % 5],
  atrian_score: Math.floor(Math.random() * 40) + 60,
  status_code: i % 15 === 0 ? 429 : 200,
}));

const PLACEHOLDER_CUSTOMERS: Customer[] = [
  { id: 'c1', name: 'Prefeitura de BH', tier: 'pro', calls_this_month: 45200, quota_limit: 100000, mrr: 199 },
  { id: 'c2', name: 'TCE-MG', tier: 'business', calls_this_month: 312000, quota_limit: 500000, mrr: 499 },
  { id: 'c3', name: 'Startup XYZ', tier: 'starter', calls_this_month: 3200, quota_limit: 10000, mrr: 49 },
  { id: 'c4', name: 'Dev Teste', tier: 'free', calls_this_month: 87, quota_limit: 150, mrr: 0 },
  { id: 'c5', name: 'MP-MG', tier: 'enterprise', calls_this_month: 890000, quota_limit: -1, mrr: 5000 },
];

function generatePacket(): DataPacket {
  const samples = [
    { text: 'CPF: 123.456.789-00...', pii: ['cpf'], verdict: 'masked' as const },
    { text: 'SELECT * FROM users...', pii: [], verdict: 'clean' as const },
    { text: 'RG 1234567 paciente...', pii: ['rg'], verdict: 'masked' as const },
    { text: 'Placa ABC-1234 no...', pii: ['placa'], verdict: 'masked' as const },
    { text: 'Jovem negro empres...', pii: [], verdict: 'blocked' as const },
    { text: 'Email: joao@gov.br...', pii: ['email'], verdict: 'masked' as const },
    { text: 'MASP 12345678 del...', pii: ['masp'], verdict: 'masked' as const },
    { text: 'Relatório mensal d...', pii: [], verdict: 'clean' as const },
    { text: 'PIX b74c886c-020f...', pii: ['pix_key'], verdict: 'masked' as const },
    { text: 'Processo 1234567-...', pii: ['processo'], verdict: 'masked' as const },
  ];
  const sample = samples[Math.floor(Math.random() * samples.length)];
  const isLLM = sample.pii.length > 0 && Math.random() > 0.5;
  return {
    id: Math.random().toString(36).slice(2, 10),
    text_preview: sample.text,
    pii_found: sample.pii,
    atrian_score: sample.verdict === 'blocked' ? Math.floor(Math.random() * 40) + 10 : Math.floor(Math.random() * 20) + 80,
    cost_usd: isLLM ? 0.00007 : 0,
    duration_ms: isLLM ? Math.floor(Math.random() * 150) + 50 : Math.floor(Math.random() * 5) + 1,
    model_used: isLLM ? 'qwen-plus' : 'regex',
    verdict: sample.verdict,
    phase: 'entering',
    x: 0,
    y: Math.random() * 80 + 10,
  };
}

// ── Component ──────────────────────────────────────────────

export default function DashboardV1Giant() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  // ── Real data from Supabase ────────────────────────────────────────────────
  const [realCustomers, setRealCustomers] = useState<Customer[]>([]);
  const [realStats, setRealStats] = useState<{
    total_events: number; total_mrr_brl: number; active_customers: number;
    total_calls_this_month: number; block_rate: number; avg_latency_ms: number;
  } | null>(null);

  useEffect(() => {
    async function loadRealData() {
      try {
        const [tenantsRes, statsRes] = await Promise.all([
          fetch('/api/tenants').then(r => r.ok ? r.json() : null),
          fetch('/api/stats').then(r => r.ok ? r.json() : null),
        ]);
        if (tenantsRes?.tenants?.length > 0) setRealCustomers(tenantsRes.tenants);
        if (statsRes) setRealStats(statsRes);
      } catch { /* silently fall back to placeholder data */ }
    }
    loadRealData();
    const interval = setInterval(loadRealData, 30_000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'overview',      label: 'Overview',        icon: '📊' },
    { id: 'scanner',       label: 'Live Scanner',     icon: '🔬' },
    { id: 'activity',      label: 'Activity Feed',    icon: '⚡' },
    { id: 'customers',     label: 'Customers',        icon: '👥' },
    { id: 'costs',         label: 'Cost Analysis',    icon: '💰' },
    { id: 'atrian',        label: 'ATRiAN Ethics',    icon: '🧠' },
    { id: 'social',        label: 'Social Media',     icon: '📱' },
    { id: 'alerts',        label: 'Alerts',           icon: '🔔' },
    { id: 'reports',       label: 'IA Reports',       icon: '📄' },
    { id: 'integrations',  label: 'Integrations',     icon: '🔌' },
    { id: 'settings',      label: 'Settings',         icon: '⚙️' },
  ];

  // Tabs with real/live data (no PLACEHOLDER badge in sidebar)
  const liveTabs = new Set(['scanner', 'customers']);

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      {/* ── Sidebar ── */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold">Guard Brasil</h1>
          <p className="text-xs text-slate-400 mt-1">Dashboard — Full Vision</p>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left px-4 py-2.5 rounded-lg text-sm flex items-center gap-3 transition ${
                activeTab === tab.id
                  ? 'bg-emerald-600/20 text-emerald-400'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="flex-1">{tab.label}</span>
              {!liveTabs.has(tab.id) && (
                <span className="text-[8px] text-amber-500/60 font-bold">PH</span>
              )}
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800 rounded-lg p-3">
            <p className="text-xs text-slate-400">MRR Total</p>
            <p className="text-2xl font-bold text-emerald-400">
              {realStats ? `R$ ${realStats.total_mrr_brl.toFixed(0)}` : 'R$ —'}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {realStats ? `${realStats.active_customers} customer${realStats.active_customers !== 1 ? 's' : ''} active` : '—'}
            </p>
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 overflow-auto">
        {activeTab === 'overview'     && <OverviewTab />}
        {activeTab === 'scanner'      && <ScannerTab />}
        {activeTab === 'activity'     && <ActivityTab events={PLACEHOLDER_EVENTS} />}
        {activeTab === 'customers'    && <CustomersTab customers={realCustomers.length > 0 ? realCustomers : PLACEHOLDER_CUSTOMERS} />}
        {activeTab === 'costs'        && <CostsTab events={PLACEHOLDER_EVENTS} />}
        {activeTab === 'atrian'       && <AtrianTab />}
        {activeTab === 'social'       && <SocialTab />}
        {activeTab === 'alerts'       && <PlaceholderTab name="Alerts" description="Webhook alerts, Slack notifications, email digests, anomaly detection" />}
        {activeTab === 'reports'      && <PlaceholderTab name="IA Reports" description="Daily Qwen summaries, weekly trends, monthly executive report, custom queries" />}
        {activeTab === 'integrations' && <PlaceholderTab name="Integrations" description="Slack, Discord, Telegram, Webhook, GitHub Actions, Zapier, n8n" />}
        {activeTab === 'settings'     && <PlaceholderTab name="Settings" description="API keys, team members, billing, policy packs, custom recognizers, webhooks" />}
      </main>
    </div>
  );
}

// ── Overview Tab ───────────────────────────────────────────

function OverviewTab() {
  const stats = [
    { label: 'API Calls Today',     value: '12,847', change: '+23%', color: 'emerald' },
    { label: 'PII Detected',        value: '3,291',  change: '+15%', color: 'amber' },
    { label: 'ATRiAN Blocks',       value: '47',     change: '-8%',  color: 'red' },
    { label: 'Avg Latency',         value: '4.2ms',  change: '-12%', color: 'blue' },
    { label: 'Cost Today',          value: '$0.89',  change: '+5%',  color: 'purple' },
    { label: 'Active Customers',    value: '5',      change: '+1',   color: 'emerald' },
  ];

  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">Overview</h2>
        <PH tooltip="Conectar guard.egos.ia.br/v1/stats" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <p className="text-sm text-slate-400 flex items-center">{stat.label} <PH /></p>
            <p className="text-3xl font-bold mt-1">{stat.value}</p>
            <p className={`text-sm mt-2 ${stat.change.startsWith('+') ? 'text-emerald-400' : stat.change.startsWith('-') ? 'text-red-400' : 'text-slate-400'}`}>
              {stat.change} vs yesterday
            </p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-64">
          <h3 className="text-sm font-bold text-slate-400 mb-1 flex items-center">
            API Calls (7 days) <PH tooltip="Conectar tabela guard_brasil_events" />
          </h3>
          <div className="flex items-end gap-2 h-40 mt-4">
            {[65, 78, 52, 91, 84, 97, 88].map((h, i) => (
              <div key={i} className="flex-1 bg-emerald-600/30 rounded-t" style={{ height: `${h}%` }}>
                <div className="bg-emerald-500 rounded-t h-1/3" />
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-64">
          <h3 className="text-sm font-bold text-slate-400 mb-1 flex items-center">
            PII Types Distribution <PH tooltip="Conectar tabela guard_brasil_events" />
          </h3>
          <div className="space-y-3 mt-4">
            {[
              { type: 'CPF',      pct: 42, color: 'bg-blue-500' },
              { type: 'RG',       pct: 23, color: 'bg-purple-500' },
              { type: 'Email',    pct: 18, color: 'bg-amber-500' },
              { type: 'MASP',     pct: 9,  color: 'bg-emerald-500' },
              { type: 'Placa',    pct: 5,  color: 'bg-red-500' },
              { type: 'Processo', pct: 3,  color: 'bg-cyan-500' },
            ].map((item) => (
              <div key={item.type} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-16">{item.type}</span>
                <div className="flex-1 bg-slate-800 rounded-full h-2">
                  <div className={`${item.color} rounded-full h-2`} style={{ width: `${item.pct}%` }} />
                </div>
                <span className="text-xs text-slate-400 w-8">{item.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Revenue + Cost split */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-400 mb-2 flex items-center">Revenue (MRR) <PH tooltip="Conectar tabela billing" /></h3>
          <p className="text-3xl font-bold text-emerald-400">R$ 5.747</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs"><span className="text-slate-400">Enterprise</span><span>R$ 5.000</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Business</span><span>R$ 499</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Pro</span><span>R$ 199</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Starter</span><span>R$ 49</span></div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-400 mb-2 flex items-center">LLM Costs (Month) <PH tooltip="Conectar OpenRouter billing API" /></h3>
          <p className="text-3xl font-bold text-amber-400">$12.40</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs"><span className="text-slate-400">Qwen-plus</span><span>$8.20</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Gemini flash</span><span>$3.10</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Regex (free)</span><span>$0.00</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Reports (Qwen)</span><span>$1.10</span></div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-400 mb-2 flex items-center">Margin <PH tooltip="Calculado a partir de billing + LLM costs" /></h3>
          <p className="text-3xl font-bold text-blue-400">96.2%</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs"><span className="text-slate-400">Revenue</span><span className="text-emerald-400">R$ 5.747</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">LLM Cost</span><span className="text-red-400">-R$ 62</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Infra</span><span className="text-red-400">-R$ 650</span></div>
            <div className="flex justify-between text-xs font-bold border-t border-slate-700 pt-2"><span>Net</span><span className="text-emerald-400">R$ 5.035</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Scanner Tab (V3 embedded) ─────────────────────────────

// CSS for blocked packet animations
const SCANNER_STYLES = `
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.6), 0 0 16px rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 16px rgba(239, 68, 68, 1), 0 0 32px rgba(239, 68, 68, 0.5); }
}

@keyframes shake-violent {
  0%, 100% { transform: translateX(-50%) translateY(0px); }
  25% { transform: translateX(-50%) translateY(-3px); }
  50% { transform: translateX(-50%) translateY(3px); }
  75% { transform: translateX(-50%) translateY(-2px); }
}

@keyframes blink-alert {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes scan-flash {
  0% { background-color: rgba(239, 68, 68, 0.2); }
  50% { background-color: rgba(239, 68, 68, 0.4); }
  100% { background-color: rgba(239, 68, 68, 0.1); }
}

.blocked-packet {
  animation: pulse-glow 0.8s ease-in-out infinite, shake-violent 0.3s ease-in-out infinite, blink-alert 1.2s ease-in-out infinite !important;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.8), inset 0 0 10px rgba(239, 68, 68, 0.4) !important;
  border-width: 2px !important;
  z-index: 20 !important;
}

.scanner-alert-flash {
  animation: scan-flash 0.6s ease-in-out !important;
}

@keyframes density-pulse {
  0%, 100% { border-color: rgba(251, 146, 60, 0.3); background-color: rgba(251, 146, 60, 0.05); }
  50% { border-color: rgba(251, 146, 60, 0.8); background-color: rgba(251, 146, 60, 0.15); }
}

.density-warning {
  animation: density-pulse 1.5s ease-in-out !important;
  border-color: rgba(251, 146, 60, 0.8) !important;
}
`;

function ScannerTab() {
  const [packets, setPackets] = useState<DataPacket[]>([]);
  const [stats, setStats] = useState<StreamStats>({
    total_processed: 0,
    total_blocked: 0,
    total_cost: 0,
    avg_latency: 0,
    pii_breakdown: {},
  });
  const [isPaused, setIsPaused] = useState(false);
  const [selectedPacket, setSelectedPacket] = useState<DataPacket | null>(null);
  const [alertFlash, setAlertFlash] = useState(false);
  const startTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      const p = generatePacket();
      // Trigger alert flash on blocked packet
      if (p.verdict === 'blocked') {
        setAlertFlash(true);
        setTimeout(() => setAlertFlash(false), 600);
      }
      setPackets((prev) => [...prev, p].slice(-40)); // allow more packets
      setStats((prev) => {
        const newCount = prev.total_processed + 1;
        return {
          total_processed: newCount,
          total_blocked: prev.total_blocked + (p.verdict === 'blocked' ? 1 : 0),
          total_cost: prev.total_cost + p.cost_usd,
          avg_latency: Math.round((prev.avg_latency * prev.total_processed + p.duration_ms) / newCount),
          pii_breakdown: p.pii_found.reduce((acc, pii) => ({
            ...acc, [pii]: (prev.pii_breakdown[pii] || 0) + 1,
          }), { ...prev.pii_breakdown }),
        };
      });
    }, 1800 + Math.random() * 1800);
    return () => clearInterval(interval);
  }, [isPaused]);

  useEffect(() => {
    let raf: number;
    const animate = () => {
      setPackets((prev) =>
        prev
          .map((p) => ({
            ...p,
            x: Math.min(100, p.x + (p.verdict === 'blocked' ? 0.15 : 0.35)), // blocked slower
            phase: p.x < 30 ? 'entering' as const : p.x < 70 ? 'scanning' as const : 'processed' as const,
          }))
          .filter((p) => p.x < 105)
      );
      raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, []);

  const verdictColor = useCallback((v: string) => {
    if (v === 'clean') return 'border-emerald-500 bg-emerald-500/10 text-emerald-300';
    if (v === 'masked') return 'border-blue-500 bg-blue-500/10 text-blue-300';
    return 'border-red-600 bg-red-600/20 text-red-200';
  }, []);

  const packetCount = packets.length;
  const isHighDensity = packetCount > 25;

  return (
    <div className="relative bg-black rounded-xl overflow-hidden" style={{ height: 'calc(100vh - 0px)' }}>
      <style>{SCANNER_STYLES}</style>

      {/* Alert Flash Overlay (blocked packet) */}
      {alertFlash && (
        <div className="absolute inset-0 z-40 bg-red-600/10 scanner-alert-flash pointer-events-none" />
      )}

      {/* Header */}
      <div className={`absolute top-0 left-0 right-0 z-20 bg-black/80 backdrop-blur border-b transition-colors ${
        alertFlash ? 'border-red-600' : isHighDensity ? 'border-amber-600' : 'border-slate-800'
      } px-6 py-3 flex items-center justify-between`}>
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold tracking-wider">RADICAL TRANSPARENCY SCANNER</h2>
          <span className="text-[10px] text-slate-500 tracking-widest uppercase">dados fluindo em tempo real</span>
          {isHighDensity && (
            <span className="text-[9px] text-amber-400 bg-amber-900/40 px-2 py-1 rounded-full animate-pulse">
              ⚠ HIGH DENSITY ({packetCount} packets)
            </span>
          )}
          {alertFlash && (
            <span className="text-[9px] text-red-400 bg-red-900/40 px-2 py-1 rounded-full animate-pulse font-bold">
              🚨 BLOCKED!
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`text-xs px-3 py-1 rounded border transition ${isPaused ? 'border-emerald-500 text-emerald-400' : 'border-slate-700 text-slate-400 hover:border-slate-500'}`}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isPaused ? 'bg-amber-500' : alertFlash ? 'bg-red-500 animate-pulse' : 'bg-emerald-500 animate-pulse'}`} />
            <span className={`text-xs ${alertFlash ? 'text-red-400' : 'text-slate-400'}`}>
              {isPaused ? 'Paused' : alertFlash ? 'ALERT!' : 'Live (simulated)'}
            </span>
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div className="relative w-full h-full pt-14 pb-16">
        {/* Zone labels */}
        <div className="absolute top-16 left-0 right-0 flex z-10 pointer-events-none">
          <div className="w-[30%] text-center">
            <span className="text-[10px] text-slate-600 tracking-[0.3em] uppercase">Input</span>
          </div>
          <div className="w-[40%] text-center">
            <span className={`text-[10px] tracking-[0.3em] uppercase transition-colors ${alertFlash ? 'text-red-600' : 'text-emerald-800'}`}>
              Guard Processing
            </span>
          </div>
          <div className="w-[30%] text-center">
            <span className="text-[10px] text-slate-600 tracking-[0.3em] uppercase">Output</span>
          </div>
        </div>

        {/* Zone dividers */}
        <div className={`absolute top-14 bottom-0 left-[30%] w-px bg-gradient-to-b transition-colors ${
          alertFlash ? 'from-red-900/80 via-red-600/40 to-transparent' : 'from-emerald-900/50 via-emerald-600/20 to-transparent'
        } z-10`} />
        <div className={`absolute top-14 bottom-0 left-[70%] w-px bg-gradient-to-b transition-colors ${
          alertFlash ? 'from-red-900/80 via-red-600/40 to-transparent' : 'from-emerald-900/50 via-emerald-600/20 to-transparent'
        } z-10`} />
        <div className={`absolute top-14 bottom-0 left-[30%] w-[40%] bg-gradient-to-b transition-colors ${
          alertFlash ? 'from-red-950/50 via-red-950/20 to-transparent' : 'from-emerald-950/30 via-emerald-950/10 to-transparent'
        } z-0`} />

        {/* Blocked zone accumulator (right side) */}
        {stats.total_blocked > 0 && (
          <div className="absolute top-20 right-8 bg-red-950/40 border border-red-600/60 rounded-lg p-4 z-5 density-warning">
            <p className="text-[10px] text-red-400 font-bold uppercase tracking-wider">Blocked Queue</p>
            <p className="text-2xl font-bold text-red-500 mt-1">{stats.total_blocked}</p>
            <p className="text-[9px] text-red-600 mt-1">packets quarantined</p>
          </div>
        )}

        {/* Packets */}
        {packets.map((packet) => (
          <div
            key={packet.id}
            onClick={() => setSelectedPacket(packet)}
            className={`absolute cursor-pointer border rounded-lg px-3 py-2 hover:scale-125 transition-all ${
              packet.verdict === 'blocked'
                ? 'blocked-packet'
                : isHighDensity ? 'density-warning' : ''
            } ${verdictColor(packet.verdict)}`}
            style={{
              left: `${packet.x}%`,
              top: `${packet.y}%`,
              opacity: packet.x > 90 ? (100 - packet.x) / 10 : packet.x < 5 ? packet.x / 5 : 1,
              transform: `translateX(-50%) scale(${packet.phase === 'scanning' ? 1.05 : 1})`,
            }}
          >
            <p className="text-[10px] font-mono whitespace-nowrap max-w-[120px] truncate">
              {packet.text_preview}
            </p>
            <div className="flex items-center gap-1 mt-1">
              {packet.pii_found.map((pii) => (
                <span key={pii} className="text-[8px] bg-white/10 px-1 rounded">{pii}</span>
              ))}
              {packet.verdict === 'blocked' && (
                <span className="text-[8px] bg-red-700 text-red-100 px-1 rounded font-bold">✕ BLOCKED</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Stats Bar */}
      <div className={`absolute bottom-0 left-0 right-0 z-20 bg-black/90 backdrop-blur border-t transition-colors ${
        alertFlash ? 'border-red-600 shadow-[0_-4px_20px_rgba(239,68,68,0.3)]' : 'border-slate-800'
      } px-6 py-3`}>
        <div className="flex items-center justify-between gap-8 max-w-full">
          <div className="text-center">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Processed</p>
            <p className="text-lg font-bold font-mono">{stats.total_processed}</p>
          </div>
          <div className={`text-center px-3 py-2 rounded-lg transition-all ${
            stats.total_blocked > 0 ? 'bg-red-950/60 border border-red-600/50' : ''
          }`}>
            <p className={`text-[10px] uppercase tracking-wider ${stats.total_blocked > 0 ? 'text-red-400' : 'text-slate-500'}`}>
              Blocked {stats.total_blocked > 0 ? '🚨' : ''}
            </p>
            <p className={`text-lg font-bold font-mono transition-colors ${stats.total_blocked > 0 ? 'text-red-500 animate-pulse' : 'text-slate-400'}`}>
              {stats.total_blocked}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Total Cost</p>
            <p className="text-lg font-bold font-mono text-amber-400">${stats.total_cost.toFixed(5)}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Avg Latency</p>
            <p className="text-lg font-bold font-mono text-blue-400">{stats.avg_latency}ms</p>
          </div>
          <div className="text-center min-w-fit">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">PII Caught</p>
            <div className="flex gap-1 mt-1 justify-center flex-wrap">
              {Object.entries(stats.pii_breakdown)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([type, count]) => (
                  <span key={type} className="text-[8px] bg-blue-900/60 text-blue-200 px-1.5 py-0.5 rounded whitespace-nowrap">
                    {type}:{count}
                  </span>
                ))}
              {Object.keys(stats.pii_breakdown).length === 0 && (
                <span className="text-[8px] text-slate-600">aguardando...</span>
              )}
            </div>
          </div>
          <div className="text-[8px] text-slate-600 italic whitespace-nowrap">
            simulado
          </div>
        </div>
      </div>

      {/* Packet Detail Modal */}
      {selectedPacket && (
        <div
          className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => setSelectedPacket(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold">Packet Inspection</h3>
              <button onClick={() => setSelectedPacket(null)} className="text-slate-400 hover:text-white text-lg">×</button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Input Preview</p>
                <p className="text-sm font-mono bg-slate-800 rounded p-3">{selectedPacket.text_preview}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Verdict</p>
                  <span className={`text-sm font-bold ${selectedPacket.verdict === 'clean' ? 'text-emerald-400' : selectedPacket.verdict === 'masked' ? 'text-blue-400' : 'text-red-400'}`}>
                    {selectedPacket.verdict.toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">ATRiAN Score</p>
                  <span className={`text-sm font-bold ${selectedPacket.atrian_score > 70 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {selectedPacket.atrian_score}/100
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Model</p>
                  <p className="text-sm font-mono">{selectedPacket.model_used}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">Cost</p>
                  <p className="text-sm font-mono text-amber-400">
                    {selectedPacket.cost_usd > 0 ? `$${selectedPacket.cost_usd.toFixed(5)}` : 'Free (regex)'}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Latency</p>
                  <p className="text-sm font-mono text-blue-400">{selectedPacket.duration_ms}ms</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">PII Found</p>
                  <div className="flex gap-1 flex-wrap">
                    {selectedPacket.pii_found.length > 0
                      ? selectedPacket.pii_found.map((p) => (
                          <span key={p} className="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded">{p}</span>
                        ))
                      : <span className="text-xs text-slate-400">None</span>}
                  </div>
                </div>
              </div>
              <div className="bg-emerald-900/20 border border-emerald-800/50 rounded-lg p-3 mt-2">
                <p className="text-[10px] text-emerald-400 uppercase tracking-wider mb-1">Transparência Radical</p>
                <p className="text-xs text-slate-300">
                  Este registro ficará no seu audit trail. Exportável, consultável, deletável. Zero opacidade.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Activity Tab ──────────────────────────────────────────

function ActivityTab({ events }: { events: Event[] }) {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Live Activity</h2>
          <PH tooltip="Conectar Supabase Realtime → tabela guard_brasil_events" />
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-amber-500 rounded-full" />
          <span className="text-xs text-amber-400">Simulated</span>
        </div>
      </div>
      <div className="space-y-2">
        {events.map((evt) => (
          <div key={evt.id} className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex items-center gap-4 hover:border-slate-700 transition">
            <span className={`w-2 h-2 rounded-full ${evt.status_code === 200 ? 'bg-emerald-500' : 'bg-red-500'}`} />
            <span className="text-xs text-slate-500 w-20 font-mono">{new Date(evt.timestamp).toLocaleTimeString()}</span>
            <span className="text-sm font-mono text-slate-300 w-32">{evt.event_type}</span>
            <span className="text-xs text-slate-500 w-20">{evt.model_id}</span>
            <span className="text-xs text-slate-500 w-20">{evt.policy_pack}</span>
            <div className="flex gap-1 flex-1">
              {evt.pii_types.map((t) => (
                <span key={t} className="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded">{t}</span>
              ))}
            </div>
            <span className="text-xs text-slate-400 w-16 text-right">{evt.duration_ms}ms</span>
            <span className="text-xs text-emerald-400 w-20 text-right font-mono">${evt.cost_usd.toFixed(5)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Customers Tab ─────────────────────────────────────────

function CustomersTab({ customers }: { customers: Customer[] }) {
  const tierColors: Record<string, string> = {
    free:       'bg-slate-700 text-slate-300',
    starter:    'bg-blue-900/50 text-blue-300',
    pro:        'bg-purple-900/50 text-purple-300',
    business:   'bg-amber-900/50 text-amber-300',
    enterprise: 'bg-emerald-900/50 text-emerald-300',
  };

  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">Customers</h2>
        <PH tooltip="Conectar Supabase → tabela tenants / subscriptions" />
      </div>
      <div className="space-y-3">
        {customers.map((c) => (
          <div key={c.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-6">
            <div className="flex-1">
              <p className="font-bold">{c.name}</p>
              <span className={`text-xs px-2 py-0.5 rounded ${tierColors[c.tier]}`}>{c.tier.toUpperCase()}</span>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400">Calls this month</p>
              <p className="font-mono">{c.calls_this_month.toLocaleString()}</p>
            </div>
            <div className="w-32">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Quota</span>
                <span>{c.quota_limit === -1 ? '∞' : `${Math.round(c.calls_this_month / c.quota_limit * 100)}%`}</span>
              </div>
              <div className="bg-slate-800 rounded-full h-2">
                <div
                  className={`rounded-full h-2 ${c.calls_this_month / c.quota_limit > 0.9 ? 'bg-red-500' : 'bg-emerald-500'}`}
                  style={{ width: `${c.quota_limit === -1 ? 30 : Math.min(100, c.calls_this_month / c.quota_limit * 100)}%` }}
                />
              </div>
            </div>
            <div className="text-right w-24">
              <p className="text-sm text-slate-400">MRR</p>
              <p className="font-bold text-emerald-400">R$ {c.mrr}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Costs Tab ─────────────────────────────────────────────

function CostsTab({ events }: { events: Event[] }) {
  const totalCost = events.reduce((sum, e) => sum + e.cost_usd, 0);
  const byModel = events.reduce((acc, e) => {
    acc[e.model_id] = (acc[e.model_id] || 0) + e.cost_usd;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">Cost Analysis — Transparência Radical</h2>
        <PH tooltip="Conectar guard.egos.ia.br/v1/billing + OpenRouter API" />
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm text-slate-400 mb-2 flex items-center">Total Cost (displayed period) <PH /></h3>
          <p className="text-4xl font-bold text-amber-400">${totalCost.toFixed(4)}</p>
          <p className="text-xs text-slate-500 mt-2">Every single call is logged. No hidden fees.</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm text-slate-400 mb-4 flex items-center">Cost by Model <PH /></h3>
          <div className="space-y-3">
            {Object.entries(byModel).sort((a, b) => b[1] - a[1]).map(([model, cost]) => (
              <div key={model} className="flex items-center justify-between">
                <span className="text-sm font-mono">{model}</span>
                <span className="text-sm font-mono text-amber-400">${cost.toFixed(5)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-emerald-900/20 border border-emerald-800 rounded-xl p-6">
        <h3 className="text-sm font-bold text-emerald-400 mb-2">Por que mostramos tudo</h3>
        <p className="text-sm text-slate-300">
          Guard Brasil opera em Transparência Radical. Cada chamada de API, cada token de LLM,
          cada custo é visível em tempo real. Sem faturas agregadas. Sem surpresas.
          Sua IA gera relatórios diários explicando por que os custos mudaram.
        </p>
      </div>
    </div>
  );
}

// ── ATRiAN Tab ────────────────────────────────────────────

function AtrianTab() {
  const violations = [
    { text: 'Jovem negro aplicando para empréstimo...', score: 32, type: 'racial_bias',        time: '14:32' },
    { text: 'Paciente HIV+ identificado pelo nome...', score: 18, type: 'medical_privacy',     time: '13:45' },
    { text: 'Suspeito residente da favela X...',       score: 41, type: 'socioeconomic_bias',  time: '11:20' },
  ];

  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">ATRiAN — Ethical AI Validation</h2>
        <PH tooltip="Conectar guard.egos.ia.br/v1/atrian + tabela atrian_violations" />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400 flex items-center">Avg ATRiAN Score <PH /></p>
          <p className="text-3xl font-bold text-emerald-400">87.3</p>
          <p className="text-xs text-slate-500">out of 100 (safe)</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400 flex items-center">Violations (24h) <PH /></p>
          <p className="text-3xl font-bold text-red-400">3</p>
          <p className="text-xs text-slate-500">blocked or flagged</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400 flex items-center">Axioms Checked <PH /></p>
          <p className="text-3xl font-bold text-blue-400">7</p>
          <p className="text-xs text-slate-500">fairness, privacy, consent, etc.</p>
        </div>
      </div>

      <h3 className="text-lg font-bold mb-4 text-red-400 flex items-center">
        Recent Violations <PH tooltip="Conectar tabela atrian_violations via Supabase Realtime" />
      </h3>
      <div className="space-y-3">
        {violations.map((v, i) => (
          <div key={i} className="bg-red-950/30 border border-red-900/50 rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-red-400 bg-red-900/50 px-2 py-0.5 rounded">{v.type}</span>
              <span className="text-xs text-slate-500">{v.time}</span>
            </div>
            <p className="text-sm text-slate-300 font-mono">"{v.text}"</p>
            <div className="flex items-center gap-3 mt-3">
              <span className="text-xs text-slate-400">ATRiAN Score:</span>
              <div className="flex-1 bg-slate-800 rounded-full h-2">
                <div className="bg-red-500 rounded-full h-2" style={{ width: `${v.score}%` }} />
              </div>
              <span className="text-sm font-bold text-red-400">{v.score}/100</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Social Tab ────────────────────────────────────────────

function SocialTab() {
  const posts = [
    { day: 'Mon', text: 'CPF masking demo...', status: 'posted',  impressions: 342, engagement: 3.5 },
    { day: 'Tue', text: 'Placa detection...',  status: 'posted',  impressions: 198, engagement: 4.0 },
    { day: 'Wed', text: 'ATRiAN feature...',   status: 'pending', impressions: 0,   engagement: 0 },
    { day: 'Thu', text: 'Poll: compliance?',   status: 'draft',   impressions: 0,   engagement: 0 },
    { day: 'Fri', text: 'LGPD 8 years...',     status: 'draft',   impressions: 0,   engagement: 0 },
  ];

  const statusColors: Record<string, string> = {
    posted:  'bg-emerald-900/50 text-emerald-300',
    pending: 'bg-amber-900/50 text-amber-300',
    draft:   'bg-slate-700 text-slate-300',
  };

  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">Social Media — X.com @anoineim</h2>
        <PH tooltip="Conectar X.com API (Free tier: 500 writes/mo)" />
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Posts This Week',    value: '5',    ph: true },
          { label: 'Total Impressions',  value: '540',  ph: true },
          { label: 'Avg Engagement',     value: '3.7%', ph: true, color: 'text-emerald-400' },
          { label: 'API Tests from X',   value: '23',   ph: true, color: 'text-blue-400' },
        ].map((s) => (
          <div key={s.label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <p className="text-sm text-slate-400 flex items-center">{s.label} {s.ph && <PH />}</p>
            <p className={`text-3xl font-bold ${s.color || ''}`}>{s.value}</p>
          </div>
        ))}
      </div>

      <h3 className="text-lg font-bold mb-4 flex items-center">
        Content Calendar <PH tooltip="Conectar tabela social_posts + X API publisher" />
      </h3>
      <div className="space-y-2">
        {posts.map((p, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex items-center gap-4">
            <span className="text-sm text-slate-400 w-10">{p.day}</span>
            <span className={`text-xs px-2 py-0.5 rounded ${statusColors[p.status]}`}>{p.status}</span>
            <span className="text-sm flex-1">{p.text}</span>
            <span className="text-xs text-slate-400">{p.impressions > 0 ? `${p.impressions} imp` : '—'}</span>
            <span className="text-xs text-emerald-400">{p.engagement > 0 ? `${p.engagement}%` : '—'}</span>
          </div>
        ))}
      </div>

      <h3 className="text-lg font-bold mb-4 mt-8 flex items-center">
        Competitor Watch <PH tooltip="Conectar X API search por keywords" />
      </h3>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <p className="text-sm text-slate-400">
          Grepture: 2 posts this week (EU privacy) | Protecto: 1 post (healthcare) | Strac: 3 posts (DLP)
        </p>
      </div>
    </div>
  );
}

// ── Placeholder Tab ───────────────────────────────────────

function PlaceholderTab({ name, description }: { name: string; description: string }) {
  return (
    <div className="p-8">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-2xl font-bold">{name}</h2>
        <PH />
      </div>
      <div className="bg-slate-900 border border-slate-800 border-dashed rounded-xl p-12 text-center">
        <p className="text-4xl mb-4">🚧</p>
        <p className="text-lg font-bold text-slate-400">Coming Soon</p>
        <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto">{description}</p>
      </div>
    </div>
  );
}
