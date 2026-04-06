'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';

const API_URL = 'https://guard.egos.ia.br';

// ── Types ──────────────────────────────────────────────────────────────────

interface Finding {
  category: string;
  label: string;
  suggestion: string;
}

interface InspectResult {
  safe: boolean;
  blocked: boolean;
  output: string;
  summary?: string;
  lgpdDisclosure?: string;
  atrian?: { passed: boolean; score: number; violationCount: number };
  masking?: { sensitivityLevel: string; findingCount: number; findings: Finding[] };
  receipt?: {
    inspectedAt: string;
    inputHash: string;
    outputHash: string;
    inspectionHash: string;
    guardVersion: string;
  };
  pri?: { output: string; confidence: number; reasoning: string };
  meta?: { durationMs: number; version: string; timestamp?: string };
  error?: string;
}

interface Scenario {
  id: string;
  label: string;
  category: string;
  input: string;
  body: InspectResult;
  stats: { http_status: number; time_total: number; size: number };
}

interface AuditEntry {
  seq: number;
  ts: string;
  input: string;
  inputHash: string;
  inspectionHash: string;
  findingCount: number;
  categories: string[];
  durationMs: number;
  source: 'scenario' | 'sandbox';
  scenarioId?: string;
}

// ── Helpers ────────────────────────────────────────────────────────────────

async function sha256hex(text: string): Promise<string> {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function highlightPii(text: string, findings: Finding[]): string {
  if (!findings?.length) return escapeHtml(text);
  const sorted = [...findings].sort((a, b) => (b.suggestion?.length ?? 0) - (a.suggestion?.length ?? 0));
  let result = escapeHtml(text);
  for (const f of sorted) {
    const mask = escapeHtml(f.suggestion ?? '');
    const color = CATEGORY_COLORS[f.category] ?? 'text-red-400 bg-red-900/30 border border-red-700/40';
    result = result.replace(
      new RegExp(escapeRegex(mask), 'g'),
      `<mark class="inline-block rounded px-0.5 ${color} not-italic font-mono text-xs">${mask}</mark>`,
    );
  }
  return result;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const CATEGORY_COLORS: Record<string, string> = {
  cpf:            'text-red-300 bg-red-900/40 border border-red-700/40',
  cnpj:           'text-orange-300 bg-orange-900/40 border border-orange-700/40',
  rg:             'text-yellow-300 bg-yellow-900/40 border border-yellow-700/40',
  cnh:            'text-amber-300 bg-amber-900/40 border border-amber-700/40',
  email:          'text-blue-300 bg-blue-900/40 border border-blue-700/40',
  phone:          'text-cyan-300 bg-cyan-900/40 border border-cyan-700/40',
  cep:            'text-purple-300 bg-purple-900/40 border border-purple-700/40',
  sus:            'text-pink-300 bg-pink-900/40 border border-pink-700/40',
  nis:            'text-indigo-300 bg-indigo-900/40 border border-indigo-700/40',
  masp:           'text-teal-300 bg-teal-900/40 border border-teal-700/40',
  plate:          'text-lime-300 bg-lime-900/40 border border-lime-700/40',
  passport:       'text-rose-300 bg-rose-900/40 border border-rose-700/40',
  titulo_eleitor: 'text-violet-300 bg-violet-900/40 border border-violet-700/40',
  reds:           'text-emerald-300 bg-emerald-900/40 border border-emerald-700/40',
  process_number: 'text-sky-300 bg-sky-900/40 border border-sky-700/40',
};

const CATEGORY_BADGE_COLORS: Record<string, string> = {
  cpf:            'bg-red-900/30 text-red-300 border-red-700/40',
  cnpj:           'bg-orange-900/30 text-orange-300 border-orange-700/40',
  rg:             'bg-yellow-900/30 text-yellow-300 border-yellow-700/40',
  cnh:            'bg-amber-900/30 text-amber-300 border-amber-700/40',
  email:          'bg-blue-900/30 text-blue-300 border-blue-700/40',
  phone:          'bg-cyan-900/30 text-cyan-300 border-cyan-700/40',
  cep:            'bg-purple-900/30 text-purple-300 border-purple-700/40',
  sus:            'bg-pink-900/30 text-pink-300 border-pink-700/40',
  nis:            'bg-indigo-900/30 text-indigo-300 border-indigo-700/40',
  masp:           'bg-teal-900/30 text-teal-300 border-teal-700/40',
  plate:          'bg-lime-900/30 text-lime-300 border-lime-700/40',
  passport:       'bg-rose-900/30 text-rose-300 border-rose-700/40',
  titulo_eleitor: 'bg-violet-900/30 text-violet-300 border-violet-700/40',
  mixed:          'bg-slate-700/30 text-slate-300 border-slate-600/40',
  clean:          'bg-emerald-900/30 text-emerald-300 border-emerald-700/40',
};

// Curated scenario labels and inputs (supplement what's in the JSON)
const SCENARIO_META: Record<string, { label: string; input: string; category: string }> = {
  '01_cpf_formatted':          { label: 'CPF formatado',          input: 'Meu CPF é 123.456.789-09',                                                                  category: 'cpf' },
  '02_cpf_unformatted':        { label: 'CPF sem formatação',      input: 'O número é 12345678909 para cadastro',                                                      category: 'cpf' },
  '03_cpf_invalid_checksum':   { label: 'CPF checksum inválido',   input: 'CPF: 111.111.111-11',                                                                       category: 'cpf' },
  '04_cnpj_formatted':         { label: 'CNPJ formatado',          input: 'CNPJ da empresa: 12.345.678/0001-95',                                                      category: 'cnpj' },
  '05_cnpj_branch':            { label: 'CNPJ filial',             input: 'Filial: 12.345.678/0002-76',                                                               category: 'cnpj' },
  '06_rg_sp':                  { label: 'RG São Paulo',            input: 'RG 12.345.678-9 expedido SP',                                                              category: 'rg' },
  '07_rg_mg':                  { label: 'RG Minas Gerais',         input: 'Documento MG-12345678',                                                                    category: 'rg' },
  '08_email':                  { label: 'E-mail corporativo',      input: 'Contato: joao.silva@empresa.com.br',                                                       category: 'email' },
  '09_phone_mobile':           { label: 'Celular com DDD',         input: 'WhatsApp: (11) 99999-8888',                                                                category: 'phone' },
  '10_cep':                    { label: 'CEP endereço',            input: 'Entrega no CEP 01310-100, São Paulo',                                                      category: 'cep' },
  '11_multiple_pii':           { label: 'Múltiplos PII',           input: 'Cliente João, CPF 123.456.789-09, e-mail joao@x.com, cel (11) 99999-1234',                category: 'mixed' },
  '12_sus_card':               { label: 'Cartão SUS',              input: 'Cartão SUS do paciente: 898 0012 3456 7890',                                               category: 'sus' },
  '13_cnh':                    { label: 'CNH número',              input: 'CNH 12345678901 vencimento 2028',                                                          category: 'cnh' },
  '14_plate_old':              { label: 'Placa antiga',            input: 'Veículo ABC-1234 registrado SP',                                                           category: 'plate' },
  '15_plate_mercosul':         { label: 'Placa Mercosul',          input: 'Placa ABC1D23 — padrão Mercosul',                                                          category: 'plate' },
  '16_masp':                   { label: 'MASP funcional',          input: 'Servidor MASP 1234567-8 ativo',                                                            category: 'masp' },
  '17_titulo_eleitor':         { label: 'Título de eleitor',       input: 'Título: 1234 5678 9012 zona 001',                                                          category: 'titulo_eleitor' },
  '18_nis_pis':                { label: 'NIS/PIS',                 input: 'PIS/PASEP 123.45678.90-1',                                                                 category: 'nis' },
  '19_process_number':         { label: 'Processo judicial',       input: 'Processo 1234567-89.2024.1.00.0000 TJ-SP',                                                 category: 'process_number' },
  '20_clean_text':             { label: 'Texto limpo (sem PII)',   input: 'O prazo de entrega é 5 dias úteis após confirmação do pedido.',                            category: 'clean' },
};

// ── Main Component ─────────────────────────────────────────────────────────

export default function SandboxClient() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [liveResults, setLiveResults] = useState<Record<string, { result: InspectResult; durationMs: number; clientHash: string }>>({});
  const [runningScenario, setRunningScenario] = useState<string | null>(null);

  const [sandboxText, setSandboxText] = useState('');
  const [sandboxResult, setSandboxResult] = useState<InspectResult | null>(null);
  const [sandboxRunning, setSandboxRunning] = useState(false);
  const [sandboxDuration, setSandboxDuration] = useState(0);
  const [sandboxClientHash, setSandboxClientHash] = useState('');

  const [apiKey, setApiKey] = useState('');
  const [auditTrail, setAuditTrail] = useState<AuditEntry[]>([]);
  const seqRef = useRef(0);

  const [signupEmail, setSignupEmail] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupResult, setSignupResult] = useState<{ key: string; quota: number } | null>(null);
  const [signupError, setSignupError] = useState('');

  const [activeTab, setActiveTab] = useState<'scenarios' | 'sandbox' | 'audit'>('scenarios');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  // ── Load scenarios ──────────────────────────────────────────────────────

  useEffect(() => {
    fetch('/sandbox-dataset.json')
      .then(r => r.json())
      .then((data: { tests: Array<{ id: string; body: InspectResult; stats: { http_status: number; time_total: number; size: number } }> }) => {
        const enriched: Scenario[] = data.tests.map(t => {
          const meta = SCENARIO_META[t.id] ?? { label: t.id, input: '', category: 'mixed' };
          return { ...t, label: meta.label, input: meta.input, category: meta.category };
        });
        setScenarios(enriched);
      })
      .catch(() => {/* silently use empty list */});
  }, []);

  // ── Inspect helpers ──────────────────────────────────────────────────────

  const addAuditEntry = useCallback(async (
    input: string,
    result: InspectResult,
    durationMs: number,
    source: 'scenario' | 'sandbox',
    scenarioId?: string,
  ) => {
    const clientHash = await sha256hex(input);
    seqRef.current += 1;
    const entry: AuditEntry = {
      seq: seqRef.current,
      ts: new Date().toISOString(),
      input: input.length > 60 ? input.slice(0, 57) + '…' : input,
      inputHash: clientHash,
      inspectionHash: result.receipt?.inspectionHash ?? '',
      findingCount: result.masking?.findingCount ?? 0,
      categories: result.masking?.findings?.map(f => f.category) ?? [],
      durationMs,
      source,
      scenarioId,
    };
    setAuditTrail(prev => [entry, ...prev].slice(0, 100));
    return clientHash;
  }, []);

  const runScenarioLive = useCallback(async (scenario: Scenario) => {
    if (!scenario.input) return;
    setRunningScenario(scenario.id);
    const t0 = performance.now();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
      const resp = await fetch(`${API_URL}/v1/inspect`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text: scenario.input }),
      });
      const durationMs = Math.round(performance.now() - t0);
      const result: InspectResult = await resp.json();
      const clientHash = await sha256hex(scenario.input);
      setLiveResults(prev => ({ ...prev, [scenario.id]: { result, durationMs, clientHash } }));
      await addAuditEntry(scenario.input, result, durationMs, 'scenario', scenario.id);
      setActiveScenario(scenario.id);
    } catch {
      setLiveResults(prev => ({ ...prev, [scenario.id]: {
        result: { safe: false, blocked: false, output: '', error: 'Falha na conexão com a API' },
        durationMs: Math.round(performance.now() - t0),
        clientHash: '',
      }}));
    } finally {
      setRunningScenario(null);
    }
  }, [apiKey, addAuditEntry]);

  const runSandbox = useCallback(async () => {
    if (!sandboxText.trim()) return;
    setSandboxRunning(true);
    setSandboxResult(null);
    const t0 = performance.now();
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
      const resp = await fetch(`${API_URL}/v1/inspect`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text: sandboxText }),
      });
      const durationMs = Math.round(performance.now() - t0);
      const result: InspectResult = await resp.json();
      const clientHash = await sha256hex(sandboxText);
      setSandboxResult(result);
      setSandboxDuration(durationMs);
      setSandboxClientHash(clientHash);
      await addAuditEntry(sandboxText, result, durationMs, 'sandbox');
    } catch (e) {
      setSandboxResult({ safe: false, blocked: false, output: '', error: String(e) });
      setSandboxDuration(Math.round(performance.now() - t0));
    } finally {
      setSandboxRunning(false);
    }
  }, [sandboxText, apiKey, addAuditEntry]);

  const exportAudit = useCallback(() => {
    const payload = {
      exported_at: new Date().toISOString(),
      session_entries: auditTrail.length,
      entries: auditTrail,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `guard-brasil-audit-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [auditTrail]);

  const signup = useCallback(async () => {
    if (!signupEmail.trim()) return;
    setSignupLoading(true);
    setSignupError('');
    try {
      const resp = await fetch(`${API_URL}/v1/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: signupEmail, name: signupName || 'sandbox-key' }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error((body as { error?: string }).error ?? `HTTP ${resp.status}`);
      }
      const data = await resp.json() as { key: string; quota_limit: number };
      setSignupResult({ key: data.key, quota: data.quota_limit });
      setApiKey(data.key);
    } catch (e) {
      setSignupError(String(e));
    } finally {
      setSignupLoading(false);
    }
  }, [signupEmail, signupName]);

  // ── Derived ──────────────────────────────────────────────────────────────

  const categories = ['all', ...Array.from(new Set(scenarios.map(s => s.category)))];
  const filteredScenarios = filterCategory === 'all'
    ? scenarios
    : scenarios.filter(s => s.category === filterCategory);

  const activeResult = activeScenario ? (liveResults[activeScenario]?.result ?? scenarios.find(s => s.id === activeScenario)?.body ?? null) : null;
  const activeInput  = scenarios.find(s => s.id === activeScenario)?.input ?? '';
  const activeDuration = activeScenario && liveResults[activeScenario] ? liveResults[activeScenario].durationMs : null;
  const isLive = !!(activeScenario && liveResults[activeScenario]);

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* ── Header ────────────────────────────────────────────────────────── */}
      <header className="border-b border-slate-800 sticky top-0 bg-slate-950/95 backdrop-blur z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <Link href="/landing" className="text-emerald-400 font-bold text-base hover:text-emerald-300 transition flex-shrink-0">
              Guard Brasil
            </Link>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 text-sm truncate">Sandbox Auditável</span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <input
              type="text"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="gb_live_... (opcional)"
              className="hidden sm:block w-52 px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-emerald-600"
            />
            <Link
              href="/landing#get-key"
              className="px-3 py-1.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition flex-shrink-0"
            >
              Chave grátis
            </Link>
          </div>
        </div>
      </header>

      {/* ── Hero strip ────────────────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-950 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-white mb-1">
                Sandbox Auditável
                <span className="ml-2 text-xs font-normal text-emerald-400 bg-emerald-900/30 border border-emerald-700/40 px-2 py-0.5 rounded-full align-middle">
                  ao vivo
                </span>
              </h1>
              <p className="text-slate-400 text-sm">
                20 cenários pré-validados · Receipts SHA-256 verificáveis · Trilha de auditoria exportável
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>API live</span>
              </div>
              <div>p50 ~1s BR→DE</div>
              <div>v0.2.2</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Tabs ──────────────────────────────────────────────────────────── */}
      <div className="border-b border-slate-800 bg-slate-950 sticky top-[53px] z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex gap-0">
          {([
            ['scenarios', '20 Cenários', scenarios.length],
            ['sandbox',   'Sandbox livre', null],
            ['audit',     'Trilha de auditoria', auditTrail.length],
          ] as const).map(([id, label, count]) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition flex items-center gap-2 ${
                activeTab === id
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-slate-400 hover:text-white'
              }`}
            >
              {label}
              {count != null && count > 0 && (
                <span className="bg-slate-800 text-slate-400 text-xs px-1.5 py-0.5 rounded-full">{count}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">

        {/* ═══════════════════════════════════════════════════════════════════
            ZONE 1 — Pre-validated scenarios
        ═══════════════════════════════════════════════════════════════════ */}
        {activeTab === 'scenarios' && (
          <div className="flex flex-col lg:flex-row gap-6">

            {/* Left: scenario list */}
            <div className="lg:w-96 flex-shrink-0">
              {/* Category filter */}
              <div className="flex flex-wrap gap-1.5 mb-4">
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setFilterCategory(cat)}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
                      filterCategory === cat
                        ? 'bg-emerald-600 text-white border-emerald-500'
                        : `${CATEGORY_BADGE_COLORS[cat] ?? 'bg-slate-800 text-slate-400 border-slate-700'} hover:border-slate-500`
                    }`}
                  >
                    {cat === 'all' ? 'Todos' : cat.toUpperCase().replace('_', ' ')}
                  </button>
                ))}
              </div>

              {/* Scenario cards */}
              <div className="space-y-1.5 max-h-[calc(100vh-260px)] overflow-y-auto pr-1">
                {filteredScenarios.map(s => {
                  const isSelected = activeScenario === s.id;
                  const hasLive = !!liveResults[s.id];
                  const isRunning = runningScenario === s.id;
                  const result = liveResults[s.id]?.result ?? s.body;
                  const findingCount = result.masking?.findingCount ?? 0;

                  return (
                    <div
                      key={s.id}
                      onClick={() => setActiveScenario(s.id)}
                      className={`group flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition ${
                        isSelected
                          ? 'bg-slate-800 border-emerald-700/60 shadow-md shadow-emerald-900/20'
                          : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/60 hover:border-slate-700'
                      }`}
                    >
                      {/* Status dot */}
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        hasLive ? 'bg-emerald-400' : 'bg-slate-600'
                      }`} />

                      {/* Label + category */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{s.label}</p>
                        <p className="text-xs text-slate-500 font-mono truncate mt-0.5">{s.id}</p>
                      </div>

                      {/* Badges */}
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {findingCount > 0 && (
                          <span className="text-xs text-red-400 bg-red-900/30 border border-red-700/40 px-1.5 py-0.5 rounded-full">
                            {findingCount} PII
                          </span>
                        )}
                        {findingCount === 0 && (
                          <span className="text-xs text-emerald-400 bg-emerald-900/20 border border-emerald-700/40 px-1.5 py-0.5 rounded-full">
                            ✓
                          </span>
                        )}

                        {/* Run button */}
                        <button
                          onClick={e => { e.stopPropagation(); runScenarioLive(s); }}
                          disabled={!s.input || isRunning}
                          className={`p-1.5 rounded-lg border transition text-xs ${
                            isRunning
                              ? 'text-slate-500 border-slate-700 bg-slate-800 cursor-not-allowed'
                              : 'text-emerald-400 border-emerald-700/40 bg-emerald-900/20 hover:bg-emerald-900/40 opacity-0 group-hover:opacity-100'
                          }`}
                          title="Executar ao vivo"
                        >
                          {isRunning ? '…' : '▶'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Run all button */}
              <button
                onClick={() => { filteredScenarios.slice(0, 5).forEach(s => runScenarioLive(s)); }}
                disabled={!!runningScenario}
                className="mt-3 w-full py-2 text-xs font-medium text-slate-400 border border-slate-700 rounded-xl hover:border-slate-600 hover:text-white transition disabled:opacity-40"
              >
                ▶ Executar primeiros 5 ao vivo
              </button>
            </div>

            {/* Right: result panel */}
            <div className="flex-1 min-w-0">
              {activeResult ? (
                <ResultPanel
                  result={activeResult}
                  input={activeInput}
                  durationMs={activeDuration}
                  isLive={isLive}
                  scenarioId={activeScenario ?? ''}
                  clientHash={isLive && activeScenario ? liveResults[activeScenario]?.clientHash : ''}
                  prerecordedStats={scenarios.find(s => s.id === activeScenario)?.stats}
                />
              ) : (
                <EmptyResultPane />
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            ZONE 2 — Free-form sandbox
        ═══════════════════════════════════════════════════════════════════ */}
        {activeTab === 'sandbox' && (
          <div className="flex flex-col lg:flex-row gap-6">
            <div className="lg:w-1/2">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
                  <span className="text-sm font-semibold text-white">Texto para inspecionar</span>
                  <div className="flex gap-2">
                    {SANDBOX_PRESETS.map(p => (
                      <button
                        key={p.label}
                        onClick={() => setSandboxText(p.text)}
                        className={`px-2 py-0.5 text-xs border rounded-lg transition ${CATEGORY_BADGE_COLORS[p.cat] ?? 'bg-slate-800 border-slate-700 text-slate-400'} hover:opacity-80`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>
                <textarea
                  value={sandboxText}
                  onChange={e => setSandboxText(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); runSandbox(); } }}
                  placeholder={`Cole qualquer texto com dados brasileiros:\n"Nome: Maria Santos, CPF 987.654.321-00, e-mail maria@empresa.com.br, cel (21) 98765-4321"\n\n⌘+Enter para inspecionar`}
                  className="w-full h-56 px-4 py-3 bg-transparent text-sm text-slate-300 font-mono placeholder:text-slate-600 resize-none focus:outline-none"
                />
                <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 bg-slate-950/40">
                  <span className="text-xs text-slate-500">{sandboxText.length} chars</span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-600 hidden sm:block">⌘+Enter</span>
                    <button
                      onClick={runSandbox}
                      disabled={!sandboxText.trim() || sandboxRunning}
                      className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition flex items-center gap-2"
                    >
                      {sandboxRunning ? (
                        <>
                          <span className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                          Inspecionando…
                        </>
                      ) : (
                        '→ Inspecionar'
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* API key inline */}
              <div className="mt-3 flex items-center gap-2">
                <input
                  type="text"
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  placeholder="Chave API (opcional — usa modo anônimo sem chave)"
                  className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-xs font-mono text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-emerald-600"
                />
              </div>
            </div>

            <div className="lg:w-1/2">
              {sandboxResult ? (
                <ResultPanel
                  result={sandboxResult}
                  input={sandboxText}
                  durationMs={sandboxDuration}
                  isLive
                  scenarioId=""
                  clientHash={sandboxClientHash}
                />
              ) : (
                <EmptyResultPane />
              )}
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            ZONE 3 — Audit trail
        ═══════════════════════════════════════════════════════════════════ */}
        {activeTab === 'audit' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white">Trilha de Auditoria da Sessão</h2>
                <p className="text-sm text-slate-400 mt-0.5">
                  {auditTrail.length} inspeções · Hashes SHA-256 verificáveis · Exportável para ANPD
                </p>
              </div>
              <div className="flex gap-2">
                {auditTrail.length > 0 && (
                  <>
                    <button
                      onClick={() => setAuditTrail([])}
                      className="px-3 py-1.5 text-xs text-slate-400 border border-slate-700 rounded-xl hover:border-slate-600 transition"
                    >
                      Limpar
                    </button>
                    <button
                      onClick={exportAudit}
                      className="px-4 py-1.5 text-xs font-medium text-emerald-400 border border-emerald-700/40 bg-emerald-900/20 rounded-xl hover:bg-emerald-900/40 transition"
                    >
                      ↓ Exportar JSON
                    </button>
                  </>
                )}
              </div>
            </div>

            {auditTrail.length === 0 ? (
              <div className="text-center py-20 text-slate-600">
                <div className="text-4xl mb-3">🔍</div>
                <p className="text-sm">Nenhuma inspeção ainda nesta sessão.</p>
                <p className="text-xs mt-1">Execute cenários ou inspecione texto para ver a trilha.</p>
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-800 text-left">
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium">#</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium">Tempo</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium hidden md:table-cell">Texto</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium">PII</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium hidden lg:table-cell">Categorias</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium">inspectionHash</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium hidden xl:table-cell">ms</th>
                        <th className="px-4 py-3 text-xs text-slate-500 font-medium">Fonte</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditTrail.map(entry => (
                        <tr key={entry.seq} className="border-b border-slate-800/60 hover:bg-slate-800/30 transition">
                          <td className="px-4 py-3 text-xs text-slate-500 font-mono">{entry.seq}</td>
                          <td className="px-4 py-3 text-xs text-slate-400 font-mono whitespace-nowrap">
                            {new Date(entry.ts).toLocaleTimeString('pt-BR')}
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-400 max-w-xs truncate hidden md:table-cell">
                            {entry.input}
                          </td>
                          <td className="px-4 py-3">
                            {entry.findingCount > 0 ? (
                              <span className="text-xs text-red-400 bg-red-900/20 border border-red-700/30 px-1.5 py-0.5 rounded-full">
                                {entry.findingCount}
                              </span>
                            ) : (
                              <span className="text-xs text-emerald-400">✓</span>
                            )}
                          </td>
                          <td className="px-4 py-3 hidden lg:table-cell">
                            <div className="flex gap-1 flex-wrap">
                              {entry.categories.slice(0, 3).map(c => (
                                <span key={c} className={`text-xs px-1.5 py-0.5 rounded border ${CATEGORY_BADGE_COLORS[c] ?? 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                                  {c}
                                </span>
                              ))}
                              {entry.categories.length > 3 && (
                                <span className="text-xs text-slate-500">+{entry.categories.length - 3}</span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            {entry.inspectionHash ? (
                              <code className="text-xs text-slate-400 font-mono" title={entry.inspectionHash}>
                                {entry.inspectionHash.slice(0, 8)}…
                              </code>
                            ) : (
                              <span className="text-xs text-slate-600">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-400 font-mono hidden xl:table-cell">
                            {entry.durationMs}ms
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-xs px-1.5 py-0.5 rounded border ${
                              entry.source === 'scenario'
                                ? 'bg-blue-900/20 text-blue-400 border-blue-700/30'
                                : 'bg-purple-900/20 text-purple-400 border-purple-700/30'
                            }`}>
                              {entry.source === 'scenario' ? 'cen.' : 'live'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* LGPD compliance note */}
                <div className="px-4 py-3 border-t border-slate-800 bg-slate-950/40 flex items-start gap-3">
                  <span className="text-emerald-400 text-sm flex-shrink-0 mt-0.5">🔒</span>
                  <p className="text-xs text-slate-500">
                    Esta trilha existe apenas na memória desta sessão. Nenhum texto é armazenado pelo Guard Brasil — apenas hashes SHA-256 irreversíveis.
                    O arquivo exportado é gerado 100% no cliente e nunca sai do seu navegador.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            ZONE 4 — Inline free tier signup
        ═══════════════════════════════════════════════════════════════════ */}
        <div className="mt-10 p-6 bg-gradient-to-r from-emerald-900/20 to-slate-900/20 border border-emerald-700/30 rounded-2xl">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-white mb-1">
                Chave API gratuita — 500 chamadas/mês
              </h3>
              <p className="text-sm text-slate-400">
                Sem cartão. Sem cadastro de empresa. Sem telefone. Um email para começar.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {['500 chamadas/mês', 'SHA-256 receipts', 'npm @egosbr/guard-brasil', 'Sem expiração'].map(f => (
                  <span key={f} className="text-xs text-emerald-400 bg-emerald-900/20 border border-emerald-700/30 px-2 py-0.5 rounded-full">{f}</span>
                ))}
              </div>
            </div>

            <div className="w-full md:w-80">
              {signupResult ? (
                <div className="space-y-3">
                  <div className="p-3 bg-emerald-900/30 border border-emerald-600/40 rounded-xl">
                    <p className="text-xs text-emerald-400 font-medium mb-1">✓ Chave gerada — copie agora:</p>
                    <code className="text-sm font-mono text-white break-all select-all">{signupResult.key}</code>
                  </div>
                  <p className="text-xs text-slate-400">
                    Quota: {signupResult.quota} chamadas/mês. A chave foi automaticamente ativada no sandbox acima.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <input
                    type="email"
                    value={signupEmail}
                    onChange={e => setSignupEmail(e.target.value)}
                    placeholder="dev@empresa.com.br"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-600"
                  />
                  <input
                    type="text"
                    value={signupName}
                    onChange={e => setSignupName(e.target.value)}
                    placeholder="Nome do projeto (opcional)"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-emerald-600"
                  />
                  {signupError && (
                    <p className="text-xs text-red-400">{signupError}</p>
                  )}
                  <button
                    onClick={signup}
                    disabled={!signupEmail.trim() || signupLoading}
                    className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-semibold text-sm rounded-xl transition flex items-center justify-center gap-2"
                  >
                    {signupLoading ? (
                      <>
                        <span className="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                        Gerando chave…
                      </>
                    ) : 'Gerar chave gratuita →'}
                  </button>
                  <p className="text-xs text-slate-600 text-center">
                    Ao continuar você aceita os{' '}
                    <Link href="/terms" className="underline hover:text-slate-400">termos de uso</Link>.
                    Sem spam.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-800 py-8 text-center mt-12">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-3">
          <Link href="/landing"     className="hover:text-white transition">Início</Link>
          <Link href="/docs"        className="hover:text-white transition">Docs</Link>
          <Link href="/integrations" className="hover:text-white transition">Integrações</Link>
          <Link href="/faq"         className="hover:text-white transition">FAQ</Link>
          <a href={`${API_URL}/openapi.json`} target="_blank" rel="noopener noreferrer" className="hover:text-white transition">OpenAPI</a>
        </div>
        <p className="text-xs text-slate-600">Guard Brasil | @egosbr/guard-brasil | MIT License</p>
      </footer>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────

function EmptyResultPane() {
  return (
    <div className="h-80 flex flex-col items-center justify-center text-slate-600 border border-dashed border-slate-800 rounded-2xl">
      <div className="text-4xl mb-3 opacity-30">🛡</div>
      <p className="text-sm">Selecione um cenário ou execute ao vivo</p>
      <p className="text-xs mt-1 opacity-60">O resultado aparecerá aqui com highlights de PII</p>
    </div>
  );
}

interface ResultPanelProps {
  result: InspectResult;
  input: string;
  durationMs: number | null;
  isLive: boolean;
  scenarioId: string;
  clientHash: string;
  prerecordedStats?: { http_status: number; time_total: number; size: number };
}

function ResultPanel({ result, input, durationMs, isLive, scenarioId, clientHash, prerecordedStats }: ResultPanelProps) {
  const [hashVerified, setHashVerified] = useState<boolean | null>(null);
  const [showRaw, setShowRaw] = useState(false);

  useEffect(() => {
    setHashVerified(null);
    if (!input || !result.receipt?.inputHash) return;
    sha256hex(input).then(computed => {
      setHashVerified(computed === result.receipt!.inputHash);
    });
  }, [input, result.receipt?.inputHash]);

  const findings = result.masking?.findings ?? [];
  const highlightedOutput = result.output
    ? highlightPii(result.output, findings)
    : '';

  const severityColor = result.masking?.sensitivityLevel === 'critical' ? 'text-red-400'
    : result.masking?.sensitivityLevel === 'high' ? 'text-orange-400'
    : result.masking?.sensitivityLevel === 'medium' ? 'text-yellow-400'
    : 'text-emerald-400';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
      {/* Result header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${result.safe ? 'bg-emerald-400' : 'bg-red-400'}`} />
          <span className={`text-sm font-semibold ${result.safe ? 'text-emerald-400' : 'text-red-400'}`}>
            {result.safe ? 'Texto limpo' : 'PII detectada'}
          </span>
          {result.masking && result.masking.findingCount > 0 && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${
              result.masking.sensitivityLevel === 'critical'
                ? 'bg-red-900/30 text-red-300 border-red-700/40'
                : 'bg-orange-900/30 text-orange-300 border-orange-700/40'
            }`}>
              {result.masking.findingCount} finding{result.masking.findingCount > 1 ? 's' : ''} · {result.masking.sensitivityLevel}
            </span>
          )}
          {isLive && (
            <span className="text-xs text-emerald-400 bg-emerald-900/20 border border-emerald-700/30 px-2 py-0.5 rounded-full">
              ao vivo
            </span>
          )}
          {!isLive && (
            <span className="text-xs text-slate-500 bg-slate-800 border border-slate-700 px-2 py-0.5 rounded-full">
              pré-gravado
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {durationMs != null && (
            <span className="text-xs text-slate-500 font-mono">{durationMs}ms</span>
          )}
          {!isLive && prerecordedStats && (
            <span className="text-xs text-slate-600 font-mono">~{Math.round(prerecordedStats.time_total * 1000)}ms</span>
          )}
          <button
            onClick={() => setShowRaw(v => !v)}
            className="text-xs text-slate-500 hover:text-white px-2 py-1 border border-slate-700 rounded-lg transition"
          >
            {showRaw ? 'Visualização' : 'JSON raw'}
          </button>
        </div>
      </div>

      {result.error ? (
        <div className="px-4 py-6 text-red-400 text-sm font-mono">{result.error}</div>
      ) : showRaw ? (
        <pre className="px-4 py-4 text-xs font-mono text-slate-300 overflow-x-auto max-h-96">
          {JSON.stringify(result, null, 2)}
        </pre>
      ) : (
        <div className="p-4 space-y-4">

          {/* Output with PII highlighting */}
          {result.output && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1.5 font-medium">Saída mascarada</p>
              <div
                className="p-3 bg-slate-950/60 rounded-xl text-sm text-slate-200 font-mono leading-relaxed border border-slate-800"
                dangerouslySetInnerHTML={{ __html: highlightedOutput }}
              />
            </div>
          )}

          {/* Findings grid */}
          {findings.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1.5 font-medium">
                Dados encontrados
              </p>
              <div className="flex flex-wrap gap-1.5">
                {findings.map((f, i) => (
                  <div key={i} className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-medium ${CATEGORY_BADGE_COLORS[f.category] ?? 'bg-slate-800 text-slate-300 border-slate-700'}`}>
                    <span>{f.label}</span>
                    <span className="opacity-50">→</span>
                    <code className="font-mono text-xs opacity-80">{f.suggestion}</code>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ATRiAN + PRI row */}
          {(result.atrian || result.pri) && (
            <div className="grid grid-cols-2 gap-3">
              {result.atrian && (
                <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-500 mb-1">ATRiAN Score</p>
                  <div className="flex items-baseline gap-1.5">
                    <span className={`text-2xl font-bold ${result.atrian.score >= 80 ? 'text-emerald-400' : result.atrian.score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {result.atrian.score}
                    </span>
                    <span className="text-xs text-slate-500">/100</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {result.atrian.passed ? '✓ Passed' : '✗ Failed'} · {result.atrian.violationCount} violations
                  </p>
                </div>
              )}
              {result.pri && (
                <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-500 mb-1">PRI Decision</p>
                  <span className={`text-sm font-bold font-mono ${
                    result.pri.output === 'ALLOW' ? 'text-emerald-400' :
                    result.pri.output === 'BLOCK' ? 'text-red-400' : 'text-yellow-400'
                  }`}>
                    {result.pri.output}
                  </span>
                  <p className="text-xs text-slate-500 mt-0.5 truncate" title={result.pri.reasoning}>
                    {result.pri.confidence}% · {result.pri.reasoning}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Receipt / proof section */}
          {result.receipt && (
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-medium">Receipt SHA-256</p>
                {hashVerified !== null && (
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                    hashVerified
                      ? 'text-emerald-400 bg-emerald-900/20 border-emerald-700/30'
                      : 'text-red-400 bg-red-900/20 border-red-700/30'
                  }`}>
                    {hashVerified ? '✓ inputHash verificado' : '✗ inputHash divergente'}
                  </span>
                )}
              </div>
              <div className="space-y-1.5">
                {[
                  ['inputHash',      result.receipt.inputHash,      'Hash do texto original'],
                  ['outputHash',     result.receipt.outputHash,     'Hash do texto mascarado'],
                  ['inspectionHash', result.receipt.inspectionHash, 'Armazene para a ANPD ←'],
                ].map(([key, value, hint]) => (
                  <div key={key} className="flex items-center gap-2">
                    <code className="text-xs text-slate-500 font-mono w-28 flex-shrink-0">{key}</code>
                    <code
                      className={`text-xs font-mono truncate flex-1 ${key === 'inspectionHash' ? 'text-emerald-400' : 'text-slate-400'}`}
                      title={value}
                    >
                      {value}
                    </code>
                    <span className="text-xs text-slate-600 hidden sm:block flex-shrink-0">{hint}</span>
                  </div>
                ))}
              </div>
              {clientHash && (
                <div className="pt-1.5 border-t border-slate-800">
                  <div className="flex items-center gap-2">
                    <code className="text-xs text-slate-500 font-mono w-28 flex-shrink-0">clientHash</code>
                    <code className="text-xs font-mono text-blue-400 truncate flex-1" title={clientHash}>{clientHash}</code>
                    <span className="text-xs text-slate-600 hidden sm:block flex-shrink-0">Computado localmente</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* LGPD disclosure */}
          {result.lgpdDisclosure && (
            <div className="flex items-start gap-2.5 p-3 bg-blue-900/10 border border-blue-700/20 rounded-xl">
              <span className="text-blue-400 text-sm flex-shrink-0 mt-0.5">⚖</span>
              <p className="text-xs text-blue-300/80 leading-relaxed">{result.lgpdDisclosure}</p>
            </div>
          )}

          {/* Meta */}
          {result.meta && (
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 pt-1">
              <span className="font-mono">Guard {result.meta.version}</span>
              <span className="font-mono">server: {result.meta.durationMs}ms</span>
              {isLive && durationMs != null && (
                <span className="font-mono">e2e: {durationMs}ms</span>
              )}
              <span className="font-mono">{new Date(result.meta.timestamp ?? result.receipt?.inspectedAt ?? '').toLocaleTimeString('pt-BR')}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Sandbox presets ────────────────────────────────────────────────────────

const SANDBOX_PRESETS = [
  {
    label: 'Fintech',
    cat: 'cpf',
    text: 'Cliente Maria Santos, CPF 987.654.321-00, conta corrente, e-mail maria@banco.com.br, cel (21) 98765-4321.',
  },
  {
    label: 'Healthtech',
    cat: 'sus',
    text: 'Paciente: João Alves, CPF 111.222.333-96, SUS 898 0012 3456 7890, CEP 30130-110, médico responsável Dr. Pedro Lima CRM-MG 12345.',
  },
  {
    label: 'RH',
    cat: 'mixed',
    text: 'Funcionário: Ana Costa, CPF 444.555.666-45, RG 9.876.543-2 SSP/SP, CNH 00123456789, MASP 1234567-8, admissão 2024-01-15.',
  },
  {
    label: 'Limpo',
    cat: 'clean',
    text: 'O prazo de entrega é de 5 dias úteis após confirmação do pagamento. Devoluções aceitas em até 30 dias.',
  },
];
