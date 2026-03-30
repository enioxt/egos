/**
 * DASHBOARD V1 — GIGANTE (Full Vision)
 *
 * Tudo que teríamos se fôssemos um player global.
 * Placeholders para features futuras. Semrush/Canva-style.
 * Objetivo: visualizar o máximo, depois eliminar o que não interessa.
 */

'use client';

import { useState } from 'react';

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

interface SocialPost {
  id: string;
  text: string;
  status: 'draft' | 'pending' | 'posted';
  impressions: number;
  engagement_rate: number;
  scheduled_at: string;
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

// ── Component ──────────────────────────────────────────────

export default function DashboardV1Giant() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'activity', label: 'Activity Feed', icon: '⚡' },
    { id: 'customers', label: 'Customers', icon: '👥' },
    { id: 'costs', label: 'Cost Analysis', icon: '💰' },
    { id: 'atrian', label: 'ATRiAN Ethics', icon: '🧠' },
    { id: 'social', label: 'Social Media', icon: '📱' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'reports', label: 'IA Reports', icon: '📄' },
    { id: 'integrations', label: 'Integrations', icon: '🔌' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      {/* ── Sidebar ── */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold">Guard Brasil</h1>
          <p className="text-xs text-slate-400 mt-1">Dashboard v1.0 — Full Vision</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
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
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800 rounded-lg p-3">
            <p className="text-xs text-slate-400">MRR Total</p>
            <p className="text-2xl font-bold text-emerald-400">R$ 5.747</p>
            <p className="text-xs text-slate-500 mt-1">5 customers active</p>
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 overflow-auto">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'activity' && <ActivityTab events={PLACEHOLDER_EVENTS} />}
        {activeTab === 'customers' && <CustomersTab customers={PLACEHOLDER_CUSTOMERS} />}
        {activeTab === 'costs' && <CostsTab events={PLACEHOLDER_EVENTS} />}
        {activeTab === 'atrian' && <AtrianTab />}
        {activeTab === 'social' && <SocialTab />}
        {activeTab === 'alerts' && <PlaceholderTab name="Alerts" description="Webhook alerts, Slack notifications, email digests, anomaly detection" />}
        {activeTab === 'reports' && <PlaceholderTab name="IA Reports" description="Daily Qwen summaries, weekly trends, monthly executive report, custom queries" />}
        {activeTab === 'integrations' && <PlaceholderTab name="Integrations" description="Slack, Discord, Telegram, Webhook, GitHub Actions, Zapier, n8n" />}
        {activeTab === 'settings' && <PlaceholderTab name="Settings" description="API keys, team members, billing, policy packs, custom recognizers, webhooks" />}
      </main>
    </div>
  );
}

// ── Overview Tab ───────────────────────────────────────────

function OverviewTab() {
  const stats = [
    { label: 'API Calls Today', value: '12,847', change: '+23%', color: 'emerald' },
    { label: 'PII Detected', value: '3,291', change: '+15%', color: 'amber' },
    { label: 'ATRiAN Blocks', value: '47', change: '-8%', color: 'red' },
    { label: 'Avg Latency', value: '4.2ms', change: '-12%', color: 'blue' },
    { label: 'Cost Today', value: '$0.89', change: '+5%', color: 'purple' },
    { label: 'Active Customers', value: '5', change: '+1', color: 'emerald' },
  ];

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Overview</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <p className="text-sm text-slate-400">{stat.label}</p>
            <p className="text-3xl font-bold mt-1">{stat.value}</p>
            <p className={`text-sm mt-2 ${stat.change.startsWith('+') ? 'text-emerald-400' : stat.change.startsWith('-') ? 'text-red-400' : 'text-slate-400'}`}>
              {stat.change} vs yesterday
            </p>
          </div>
        ))}
      </div>

      {/* Charts placeholder */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-64">
          <h3 className="text-sm font-bold text-slate-400 mb-4">API Calls (7 days)</h3>
          <div className="flex items-end gap-2 h-40">
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
          <h3 className="text-sm font-bold text-slate-400 mb-4">PII Types Distribution</h3>
          <div className="space-y-3 mt-6">
            {[
              { type: 'CPF', pct: 42, color: 'bg-blue-500' },
              { type: 'RG', pct: 23, color: 'bg-purple-500' },
              { type: 'Email', pct: 18, color: 'bg-amber-500' },
              { type: 'MASP', pct: 9, color: 'bg-emerald-500' },
              { type: 'Placa', pct: 5, color: 'bg-red-500' },
              { type: 'Processo', pct: 3, color: 'bg-cyan-500' },
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
          <h3 className="text-sm font-bold text-slate-400 mb-2">Revenue (MRR)</h3>
          <p className="text-3xl font-bold text-emerald-400">R$ 5.747</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs"><span className="text-slate-400">Enterprise</span><span>R$ 5.000</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Business</span><span>R$ 499</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Pro</span><span>R$ 199</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Starter</span><span>R$ 49</span></div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-400 mb-2">LLM Costs (Month)</h3>
          <p className="text-3xl font-bold text-amber-400">$12.40</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-xs"><span className="text-slate-400">Qwen-plus</span><span>$8.20</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Gemini flash</span><span>$3.10</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Regex (free)</span><span>$0.00</span></div>
            <div className="flex justify-between text-xs"><span className="text-slate-400">Reports (Qwen)</span><span>$1.10</span></div>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-bold text-slate-400 mb-2">Margin</h3>
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

// ── Activity Tab ──────────────────────────────────────────

function ActivityTab({ events }: { events: Event[] }) {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Live Activity</h2>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
          <span className="text-xs text-emerald-400">Real-time</span>
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
    free: 'bg-slate-700 text-slate-300',
    starter: 'bg-blue-900/50 text-blue-300',
    pro: 'bg-purple-900/50 text-purple-300',
    business: 'bg-amber-900/50 text-amber-300',
    enterprise: 'bg-emerald-900/50 text-emerald-300',
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Customers</h2>
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
      <h2 className="text-2xl font-bold mb-6">Cost Analysis — Transparência Radical</h2>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm text-slate-400 mb-2">Total Cost (displayed period)</h3>
          <p className="text-4xl font-bold text-amber-400">${totalCost.toFixed(4)}</p>
          <p className="text-xs text-slate-500 mt-2">Every single call is logged. No hidden fees.</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm text-slate-400 mb-4">Cost by Model</h3>
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
        <h3 className="text-sm font-bold text-emerald-400 mb-2">Why we show you everything</h3>
        <p className="text-sm text-slate-300">
          Guard Brasil operates on Transparência Radical. Every API call, every LLM token,
          every cost is visible to you in real-time. No aggregated invoices. No surprises.
          Your IA generates daily reports explaining why costs changed.
        </p>
      </div>
    </div>
  );
}

// ── ATRiAN Tab ────────────────────────────────────────────

function AtrianTab() {
  const violations = [
    { text: 'Jovem negro aplicando para empréstimo...', score: 32, type: 'racial_bias', time: '14:32' },
    { text: 'Paciente HIV+ identificado pelo nome...', score: 18, type: 'medical_privacy', time: '13:45' },
    { text: 'Suspeito residente da favela X...', score: 41, type: 'socioeconomic_bias', time: '11:20' },
  ];

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">ATRiAN — Ethical AI Validation</h2>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Avg ATRiAN Score</p>
          <p className="text-3xl font-bold text-emerald-400">87.3</p>
          <p className="text-xs text-slate-500">out of 100 (safe)</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Violations (24h)</p>
          <p className="text-3xl font-bold text-red-400">3</p>
          <p className="text-xs text-slate-500">blocked or flagged</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Axioms Checked</p>
          <p className="text-3xl font-bold text-blue-400">7</p>
          <p className="text-xs text-slate-500">fairness, privacy, consent, etc.</p>
        </div>
      </div>

      <h3 className="text-lg font-bold mb-4 text-red-400">Recent Violations</h3>
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
    { day: 'Mon', text: 'CPF masking demo...', status: 'posted', impressions: 342, engagement: 3.5 },
    { day: 'Tue', text: 'Placa detection...', status: 'posted', impressions: 198, engagement: 4.0 },
    { day: 'Wed', text: 'ATRiAN feature...', status: 'pending', impressions: 0, engagement: 0 },
    { day: 'Thu', text: 'Poll: compliance risk?', status: 'draft', impressions: 0, engagement: 0 },
    { day: 'Fri', text: 'LGPD 8 years...', status: 'draft', impressions: 0, engagement: 0 },
  ];

  const statusColors: Record<string, string> = {
    posted: 'bg-emerald-900/50 text-emerald-300',
    pending: 'bg-amber-900/50 text-amber-300',
    draft: 'bg-slate-700 text-slate-300',
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Social Media — X.com @anoineim</h2>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Posts This Week</p>
          <p className="text-3xl font-bold">5</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Total Impressions</p>
          <p className="text-3xl font-bold">540</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">Avg Engagement</p>
          <p className="text-3xl font-bold text-emerald-400">3.7%</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-sm text-slate-400">API Tests from X</p>
          <p className="text-3xl font-bold text-blue-400">23</p>
        </div>
      </div>

      <h3 className="text-lg font-bold mb-4">Content Calendar</h3>
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

      {/* Competitor watch placeholder */}
      <h3 className="text-lg font-bold mb-4 mt-8">Competitor Watch</h3>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <p className="text-sm text-slate-400">
          Grepture: 2 posts this week (EU privacy) | Protecto: 1 post (healthcare) | Strac: 3 posts (DLP)
        </p>
        <p className="text-xs text-slate-500 mt-2">Placeholder — will use X API search for real data</p>
      </div>
    </div>
  );
}

// ── Placeholder Tab ───────────────────────────────────────

function PlaceholderTab({ name, description }: { name: string; description: string }) {
  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">{name}</h2>
      <div className="bg-slate-900 border border-slate-800 border-dashed rounded-xl p-12 text-center">
        <p className="text-4xl mb-4">🚧</p>
        <p className="text-lg font-bold text-slate-400">Coming Soon</p>
        <p className="text-sm text-slate-500 mt-2 max-w-md mx-auto">{description}</p>
      </div>
    </div>
  );
}
