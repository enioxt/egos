/**
 * Guard Brasil — Landing Page
 *
 * 6 exemplos pré-definidos + teste interativo.
 * Convida a pessoa a testar com seus próprios dados.
 * Free tier: 150 chamadas/mês.
 */

'use client';

import { useState } from 'react';

const EXAMPLES = [
  {
    title: 'CPF Masking',
    icon: '🔢',
    input: 'O cliente com CPF 123.456.789-00 solicitou alteração cadastral.',
    description: 'Detecta e mascara CPFs automaticamente',
  },
  {
    title: 'RG Detection',
    icon: '🪪',
    input: 'Identidade RG 1234567 SSP/MG do paciente internado na ala B.',
    description: 'Identifica RGs em textos não estruturados',
  },
  {
    title: 'Placa Veicular',
    icon: '🚗',
    input: 'Veículo de placa ABC-1D23 flagrado em excesso de velocidade.',
    description: 'Anonimiza placas em relatórios policiais',
  },
  {
    title: 'ATRiAN Bias Check',
    icon: '🧠',
    input: 'Jovem negro desempregado solicita empréstimo bancário de alto valor.',
    description: 'Score ético 0-100 para detectar viés',
  },
  {
    title: 'Dados Médicos',
    icon: '🏥',
    input: 'Paciente João Silva (CPF 987.654.321-00) diagnosticado com HIV positivo.',
    description: 'Protege dados sensíveis de saúde (LGPD)',
  },
  {
    title: 'Multi-PII',
    icon: '🔐',
    input: 'Servidor MASP 12345678, lotado na 3a DP, registrou ocorrência REDS 2025-001234 sobre veículo placa DEF-5G67.',
    description: 'Detecta múltiplos tipos simultaneamente',
  },
];

interface InspectResult {
  safe: boolean;
  blocked: boolean;
  output: string;
  atrian: { score: number; reasoning: string };
  pii_found: string[];
  cost_usd: number;
  duration_ms: number;
  model_used: string;
}

export default function LandingPage() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<InspectResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [testsUsed, setTestsUsed] = useState(0);

  async function handleTest() {
    if (!input.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'API error');
      }

      const data = await res.json();
      setResult(data);
      setTestsUsed((prev) => prev + 1);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  function selectExample(text: string) {
    setInput(text);
    setResult(null);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Hero */}
      <header className="border-b border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-5xl mx-auto px-6 py-16 text-center">
          <p className="text-emerald-400 text-sm font-mono mb-4">Brazil-first AI safety for public and regulated workflows</p>
          <h1 className="text-5xl font-bold mb-4">Guard Brasil</h1>
          <p className="text-xl text-slate-300 mb-2">
            Proteja dados sensíveis brasileiros antes que eles saiam da sua aplicação
          </p>
          <p className="text-sm text-slate-400">
            CPF, RG, MASP, REDS, placa, processo judicial e validação ética em uma única camada
          </p>
          <div className="flex items-center justify-center gap-6 mt-8">
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-400">4ms</p>
              <p className="text-xs text-slate-500">latência de referência</p>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-400">150</p>
              <p className="text-xs text-slate-500">testes de demo</p>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-400">R$0</p>
              <p className="text-xs text-slate-500">free tier</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Examples Grid */}
        <section className="mb-12">
          <h2 className="text-lg font-bold text-slate-300 mb-4">Clique para testar:</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.title}
                onClick={() => selectExample(ex.input)}
                className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-left hover:border-emerald-600/50 hover:bg-slate-800/50 transition group"
              >
                <span className="text-2xl">{ex.icon}</span>
                <p className="font-bold text-sm mt-2 group-hover:text-emerald-400 transition">{ex.title}</p>
                <p className="text-xs text-slate-500 mt-1">{ex.description}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Test Form */}
        <section className="mb-12">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Teste com texto real</h2>
              <span className="text-xs text-slate-500">{testsUsed}/150 testes usados nesta sessão</span>
            </div>

            <textarea
              value={input}
              onChange={(e) => { setInput(e.target.value); setResult(null); }}
              placeholder="Cole um texto com CPF, RG, placa, dados médicos, processo ou linguagem sensível para validar a proteção"
              className="w-full h-28 bg-slate-800 border border-slate-700 rounded-xl p-4 text-sm font-mono text-slate-200 placeholder-slate-500 focus:border-emerald-600 focus:outline-none resize-none"
            />

            <button
              onClick={handleTest}
              disabled={!input.trim() || loading}
              className="mt-4 w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold py-3 rounded-xl transition text-sm"
            >
              {loading ? 'Inspecionando...' : 'Inspecionar'}
            </button>

            {error && (
              <p className="mt-3 text-sm text-red-400">{error}</p>
            )}
          </div>
        </section>

        {/* Result */}
        {result && (
          <section className="mb-12">
            <div className="bg-slate-900 border border-emerald-800/50 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold">Resultado</h2>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-blue-400 font-mono">{result.duration_ms}ms</span>
                  <span className="text-xs text-amber-400 font-mono">
                    {result.cost_usd > 0 ? `$${result.cost_usd.toFixed(5)}` : 'LOCAL'}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">{result.model_used}</span>
                </div>
              </div>

              {/* Verdict */}
              <div className={`rounded-xl p-4 mb-4 ${
                result.blocked ? 'bg-red-950/30 border border-red-900/50' :
                result.safe ? 'bg-emerald-950/30 border border-emerald-900/50' :
                'bg-amber-950/30 border border-amber-900/50'
              }`}>
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{result.blocked ? '🚫' : result.safe ? '✅' : '⚠️'}</span>
                  <div>
                    <p className="font-bold text-sm">
                      {result.blocked ? 'BLOQUEADO — revisão necessária' :
                       result.safe ? 'SEGURO — saída mascarada com sucesso' :
                       'ATENÇÃO — revisão recomendada'}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">ATRiAN Score: {result.atrian.score}/100</p>
                  </div>
                </div>
              </div>

              {/* Output */}
              <div className="mb-4">
                <p className="text-xs text-slate-500 mb-2">Saída protegida:</p>
                <pre className="bg-slate-800 rounded-xl p-4 text-sm font-mono text-emerald-300 whitespace-pre-wrap">
                  {result.output}
                </pre>
              </div>

              {/* PII Found */}
              {result.pii_found.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-slate-500 mb-2">PII detectado:</p>
                  <div className="flex gap-2 flex-wrap">
                    {result.pii_found.map((pii) => (
                      <span key={pii} className="text-xs bg-blue-900/50 text-blue-300 px-3 py-1 rounded-lg">{pii}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* ATRiAN Reasoning */}
              <div>
                <p className="text-xs text-slate-500 mb-2">Resumo da inspeção:</p>
                <p className="text-sm text-slate-300 bg-slate-800 rounded-xl p-4">{result.atrian.reasoning}</p>
              </div>

              {/* Transparency footer */}
              <div className="mt-4 pt-4 border-t border-slate-800">
                <p className="text-[10px] text-slate-500 text-center">
                  Audit trace: model={result.model_used} | cost=${result.cost_usd.toFixed(5)} |
                  latency={result.duration_ms}ms | pii={result.pii_found.join(',')} | score={result.atrian.score}
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Pricing */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-center mb-8">Pricing</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { tier: 'Free', price: 'R$ 0', calls: 'SDK local', features: ['Uso local ilimitado', 'PII Scanner BR', 'ATRiAN core'] },
              { tier: 'Starter', price: 'R$ 49', calls: '10k/mês', features: ['API hospedada', 'Dashboard básico', 'Suporte por email'] },
              { tier: 'Pro', price: 'R$ 199', calls: '100k/mês', features: ['Dashboard + alertas', 'IA insights', 'Priority support'], popular: true },
              { tier: 'Business', price: 'R$ 499', calls: '500k/mês', features: ['SLA ampliado', 'Operação multi-time', 'Suporte dedicado'] },
            ].map((plan) => (
              <div key={plan.tier} className={`bg-slate-900 border rounded-2xl p-6 ${plan.popular ? 'border-emerald-600 ring-1 ring-emerald-600/20' : 'border-slate-800'}`}>
                {plan.popular && <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-2">Most Popular</p>}
                <p className="text-sm text-slate-400">{plan.tier}</p>
                <p className="text-2xl font-bold mt-1">{plan.price}<span className="text-sm text-slate-500">/mês</span></p>
                <p className="text-xs text-slate-500 mt-1">{plan.calls}</p>
                <ul className="mt-4 space-y-2">
                  {plan.features.map((f) => (
                    <li key={f} className="text-xs text-slate-400 flex items-center gap-2">
                      <span className="text-emerald-400">+</span> {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Install */}
        <section className="mb-12">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
            <h2 className="text-xl font-bold mb-4">Comece em 30 segundos</h2>
            <div className="bg-slate-800 rounded-xl p-4 font-mono text-sm text-left max-w-md mx-auto">
              <p className="text-slate-500"># Install</p>
              <p className="text-emerald-400">npm install @egosbr/guard-brasil</p>
              <p className="text-slate-500 mt-3"># Use</p>
              <p className="text-blue-300">{'import { GuardBrasil } from \'@egosbr/guard-brasil\''}</p>
              <p className="text-slate-300 mt-1">{'const result = GuardBrasil.create().inspect(text)'}</p>
            </div>
            <div className="flex justify-center gap-4 mt-6">
              <a href="https://github.com/enioxt/egos" className="text-xs text-slate-400 hover:text-white transition">GitHub</a>
              <a href="https://www.npmjs.com/package/@egosbr/guard-brasil" className="text-xs text-slate-400 hover:text-white transition">npm</a>
              <a href="/dashboard-v2" className="text-xs text-emerald-400 hover:text-emerald-300 transition">Dashboard preview</a>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center">
        <p className="text-xs text-slate-500">
          Guard Brasil | pacote público @egosbr/guard-brasil | MIT License
        </p>
        <p className="text-[10px] text-slate-600 mt-2">
          Every inspection is auditable. Every cost is visible. No sensitive operational details in public surfaces.
        </p>
      </footer>
    </div>
  );
}
