import { useEffect, useState } from 'react';
import {
  Activity, ShieldAlert, Cpu, GitBranch, Code2, Shield,
  AlertTriangle, Info, AlertCircle, DollarSign, ListChecks,
  Zap, BarChart3, ChevronRight, ExternalLink
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend
} from 'recharts';

import rawData from './data/report.json';

const COLORS = ['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#ec4899'];
const STATUS_COLORS: Record<string, string> = {
  production: '#10b981',
  mvp: '#f59e0b',
  kernel: '#8b5cf6',
  lab: '#06b6d4',
  operational: '#3b82f6',
};
const SEVERITY_CONFIG: Record<string, { color: string; bg: string; Icon: typeof AlertCircle }> = {
  critical: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20', Icon: AlertCircle },
  warning: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', Icon: AlertTriangle },
  info: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', Icon: Info },
};
const STAT_ICONS: Record<string, typeof Cpu> = {
  git: GitBranch, cpu: Cpu, code: Code2, shield: Shield,
};

function ScoreRing({ score, size = 120 }: { score: number; size?: number }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 90 ? '#10b981' : score >= 75 ? '#f59e0b' : '#ef4444';
  return (
    <svg width={size} height={size} className="drop-shadow-lg">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={8}
        strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`} className="transition-all duration-1000" />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
        className="fill-foreground text-2xl font-bold" style={{ fontSize: size * 0.22 }}>
        {score}
      </text>
    </svg>
  );
}

function App() {
  const [data] = useState(rawData);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  const budgetPct = (data.cost_tracker.monthly_total_usd / data.cost_tracker.budget_limit) * 100;

  return (
    <div className={`min-h-screen transition-opacity duration-700 ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      <div className="max-w-[1440px] mx-auto p-4 md:p-8 lg:p-12 space-y-6">

        {/* ─── Header ─── */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_12px_rgba(16,185,129,0.6)]" />
              <span className="text-emerald-400 font-mono text-xs tracking-[0.2em] uppercase">{data.subtitle}</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-white/90 to-white/50">
              {data.title}
            </h1>
            <p className="text-foreground/40 text-sm mt-1 font-mono">
              {data.agent} / {data.model} / {new Date(data.generated_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
          <div className="flex items-center gap-6">
            <ScoreRing score={data.meta_score} size={80} />
            <div className="text-right">
              <p className="text-xs text-foreground/40 uppercase tracking-wider">Health Score</p>
              <p className="text-sm text-foreground/60 mt-0.5">
                {data.meta_score >= 90 ? 'Excellent' : data.meta_score >= 75 ? 'Good' : 'Needs Attention'}
              </p>
            </div>
          </div>
        </header>

        {/* ─── Stats Row ─── */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {data.stats.map((stat, i) => {
            const IconComp = STAT_ICONS[stat.icon] || Zap;
            return (
              <div key={i} className="glass-card p-4 relative overflow-hidden group">
                <div className="absolute -right-3 -top-3 w-16 h-16 bg-primary/5 rounded-full blur-xl group-hover:bg-primary/10 transition-colors" />
                <div className="flex items-center gap-2 mb-2">
                  <IconComp className="w-4 h-4 text-foreground/40" />
                  <p className="text-xs text-foreground/40 font-medium uppercase tracking-wider">{stat.label}</p>
                </div>
                <div className="flex items-end gap-2">
                  <h3 className="text-2xl font-bold">{stat.value}</h3>
                  <span className={`text-xs mb-0.5 font-mono ${
                    stat.trend.startsWith('+') ? 'text-emerald-400' : stat.trend.startsWith('-') ? 'text-red-400' : 'text-blue-400'
                  }`}>{stat.trend}</span>
                </div>
              </div>
            );
          })}
        </section>

        {/* ─── Row 2: Activity Chart + Repo Health Radar ─── */}
        <section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 glass-card p-5">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-semibold flex items-center gap-2">
                <Activity className="text-primary w-4 h-4" />Weekly Activity
              </h3>
              <div className="flex gap-3 text-xs text-foreground/40">
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary inline-block" /> Commits</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-400 inline-block" /> Issues</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" /> Deploys</span>
              </div>
            </div>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.activity_data}>
                  <defs>
                    <linearGradient id="gCommits" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gIssues" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#ffffff20" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#ffffff15" fontSize={11} tickLine={false} axisLine={false} width={30} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(10,10,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }} />
                  <Area type="monotone" dataKey="commits" stroke="#8b5cf6" strokeWidth={2} fill="url(#gCommits)" />
                  <Area type="monotone" dataKey="issues" stroke="#06b6d4" strokeWidth={2} fill="url(#gIssues)" />
                  <Area type="monotone" dataKey="deploys" stroke="#10b981" strokeWidth={2} fillOpacity={0} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="lg:col-span-2 glass-card p-5">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-2">
              <BarChart3 className="text-primary w-4 h-4" />Repo Health Radar
            </h3>
            <div className="h-[230px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={data.repo_health.map(r => ({ name: r.name, score: r.score }))}>
                  <PolarGrid stroke="#ffffff10" />
                  <PolarAngleAxis dataKey="name" tick={{ fill: '#ffffff60', fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar dataKey="score" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* ─── Row 3: Repo Table + Language Pie + Cost ─── */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Repo Health Table */}
          <div className="lg:col-span-6 glass-card p-5">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-4">
              <GitBranch className="text-primary w-4 h-4" />Repository Overview
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-foreground/40 text-xs uppercase tracking-wider border-b border-white/5">
                    <th className="text-left pb-2 font-medium">Repo</th>
                    <th className="text-center pb-2 font-medium">Score</th>
                    <th className="text-right pb-2 font-medium">LOC</th>
                    <th className="text-right pb-2 font-medium">APIs</th>
                    <th className="text-right pb-2 font-medium">Pages</th>
                    <th className="text-center pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.repo_health.map((repo, i) => (
                    <tr key={i} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                      <td className="py-2.5 font-mono text-foreground/80">{repo.name}</td>
                      <td className="py-2.5 text-center">
                        <span className={`font-bold ${repo.score >= 90 ? 'text-emerald-400' : repo.score >= 75 ? 'text-amber-400' : 'text-red-400'}`}>
                          {repo.score}
                        </span>
                      </td>
                      <td className="py-2.5 text-right text-foreground/60 font-mono text-xs">{repo.loc.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-foreground/60">{repo.apis}</td>
                      <td className="py-2.5 text-right text-foreground/60">{repo.pages}</td>
                      <td className="py-2.5 text-center">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wider font-medium border"
                          style={{ color: STATUS_COLORS[repo.status], borderColor: STATUS_COLORS[repo.status] + '40', backgroundColor: STATUS_COLORS[repo.status] + '10' }}>
                          {repo.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Language Distribution */}
          <div className="lg:col-span-3 glass-card p-5">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-4">
              <Code2 className="text-primary w-4 h-4" />Languages
            </h3>
            <div className="h-[160px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data.distribution} cx="50%" cy="50%" innerRadius={40} outerRadius={65}
                    paddingAngle={3} dataKey="value" stroke="none">
                    {data.distribution.map((_: unknown, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend iconType="circle" iconSize={6}
                    formatter={(value: string) => <span className="text-foreground/60 text-xs ml-1">{value}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Cost Tracker */}
          <div className="lg:col-span-3 glass-card p-5 flex flex-col">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-4">
              <DollarSign className="text-primary w-4 h-4" />Monthly Cost
            </h3>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl font-bold">${data.cost_tracker.monthly_total_usd}</span>
              <span className="text-foreground/40 text-xs">/ ${data.cost_tracker.budget_limit}</span>
            </div>
            <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-4">
              <div className="h-full rounded-full transition-all duration-1000"
                style={{ width: `${budgetPct}%`, backgroundColor: budgetPct < 50 ? '#10b981' : budgetPct < 80 ? '#f59e0b' : '#ef4444' }} />
            </div>
            <div className="space-y-1.5 flex-1">
              {data.cost_tracker.breakdown.filter(b => b.cost > 0).map((item, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <span className="text-foreground/50">{item.service}</span>
                  <span className="text-foreground/70 font-mono">${item.cost.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Row 4: Key Findings + Tasks ─── */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-5">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-4">
              <ShieldAlert className="text-primary w-4 h-4" />Key Findings
            </h3>
            <div className="space-y-3">
              {data.key_findings.map((finding, i) => {
                const cfg = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.info;
                const SevIcon = cfg.Icon;
                return (
                  <div key={i} className={`p-3 rounded-xl border ${cfg.bg} flex items-start gap-3 group hover:border-opacity-60 transition-all`}>
                    <SevIcon className={`w-4 h-4 mt-0.5 ${cfg.color} flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-sm">{finding.title}</h4>
                        <span className="text-[10px] font-mono text-foreground/30 bg-white/5 px-1.5 py-0.5 rounded">{finding.repo}</span>
                      </div>
                      <p className="text-xs text-foreground/50 mt-0.5 leading-relaxed">{finding.description}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-foreground/20 group-hover:text-foreground/40 flex-shrink-0 mt-0.5 transition-colors" />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Tasks + API Bar Chart */}
          <div className="glass-card p-5 flex flex-col">
            <h3 className="text-base font-semibold flex items-center gap-2 mb-4">
              <ListChecks className="text-primary w-4 h-4" />Task Pipeline
            </h3>
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-red-400">{data.tasks_summary.p0}</p>
                <p className="text-[10px] text-foreground/40 uppercase tracking-wider">P0 Blockers</p>
              </div>
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-amber-400">{data.tasks_summary.p1}</p>
                <p className="text-[10px] text-foreground/40 uppercase tracking-wider">P1 Sprint</p>
              </div>
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-blue-400">{data.tasks_summary.p2}</p>
                <p className="text-[10px] text-foreground/40 uppercase tracking-wider">P2 Backlog</p>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold text-emerald-400">{data.tasks_summary.completed_this_week}</p>
                <p className="text-[10px] text-foreground/40 uppercase tracking-wider">Done (7d)</p>
              </div>
            </div>
            <div className="flex-1 min-h-[120px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.repo_health} layout="vertical" margin={{ left: 0, right: 0 }}>
                  <XAxis type="number" domain={[0, 250]} hide />
                  <YAxis dataKey="name" type="category" width={70} tick={{ fill: '#ffffff50', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(10,10,20,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="apis" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={10} name="APIs" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        {/* ─── Footer ─── */}
        <footer className="pt-6 pb-4 flex flex-col sm:flex-row justify-between items-center gap-2 text-xs text-foreground/30 font-mono border-t border-white/5">
          <span>Generated by EGOS {data.agent} via {data.model}</span>
          <span className="flex items-center gap-1.5">
            <ExternalLink className="w-3 h-3" />
            <a href="https://egos.ia.br" className="hover:text-foreground/60 transition-colors">egos.ia.br</a>
          </span>
        </footer>

      </div>
    </div>
  );
}

export default App;
