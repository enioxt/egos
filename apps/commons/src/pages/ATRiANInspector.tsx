import { useState } from 'react';
import { validateWithAtrian } from '../lib/agents';
import { ShieldCheck, ShieldAlert, Loader2 } from 'lucide-react';

export function ATRiANInspector() {
  const [content, setContent] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleValidate = async () => {
    setLoading(true);
    const res = await validateWithAtrian(content);
    setResult(res);
    setLoading(false);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto mt-20">
      <div className="flex items-center gap-3 mb-6">
        <ShieldCheck size={32} className="text-violet-400" />
        <h1 className="text-3xl font-bold text-slate-100">ATRiAN Inspector</h1>
      </div>
      <p className="text-slate-400 mb-8">Cole qualquer texto ou payload para validar contra o filtro ético e de conformidade (LGPD/PII) do núcleo EGOS.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="flex flex-col gap-4">
          <textarea
            className="w-full h-64 p-4 bg-slate-900 border border-slate-700 rounded-xl text-slate-300 focus:outline-none focus:border-violet-500 transition-colors resize-none"
            placeholder="Insira o texto para validação..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <button
            onClick={handleValidate}
            disabled={loading || !content.trim()}
            className="flex items-center justify-center gap-2 py-3 px-6 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl font-semibold text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : 'Validar Conteúdo'}
          </button>
        </div>

        <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
          <h2 className="text-xl font-semibold text-slate-200 mb-4">Resultado da Análise</h2>
          {!result ? (
            <div className="text-slate-500 text-sm italic">Aguardando validação...</div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-700">
                <span className="text-slate-400">Status</span>
                {result.passed ? (
                  <span className="flex items-center gap-2 text-green-400 font-medium"><ShieldCheck size={18} /> Aprovado</span>
                ) : (
                  <span className="flex items-center gap-2 text-red-400 font-medium"><ShieldAlert size={18} /> Rejeitado</span>
                )}
              </div>
              
              <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-700">
                <span className="text-slate-400">Score de Risco</span>
                <span className="text-xl font-bold text-slate-200">{result.score}/100</span>
              </div>

              {result.violations?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-red-400 mb-3 uppercase tracking-wider">Violações Encontradas</h3>
                  <ul className="space-y-2">
                    {result.violations.map((v: string, i: number) => (
                      <li key={i} className="text-slate-300 text-sm p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        {v}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {result.mock && (
                <div className="text-xs text-amber-500/70 mt-4 text-center">
                  * Note: Chamada de API falhou. Resultado provido por mock de fallback.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
