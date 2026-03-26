import { useState } from 'react';
import { DollarSign, Building2, CreditCard, ShieldCheck } from 'lucide-react';

export function SandboxSplitTester() {
  const [gross, setGross] = useState(100);
  const [method, setMethod] = useState<'pix' | 'credit'>('pix');
  const [simulated, setSimulated] = useState<any>(null);

  const simulateSplit = async () => {
    // Placeholder fetching the /api/sandbox/split/simulate backend endpoint
    // We mock the response for UI visualization based on values.
    const feeAsaas = method === 'pix' ? 1.99 : (gross * 0.0299 + 0.49);
    const platformShare = gross * 0.05; // 5% EGOS
    const partnerShare = gross * 0.15; // 15% Lara
    const instructorNet = gross - feeAsaas - platformShare - partnerShare;

    setSimulated({
      fee_asaas: feeAsaas,
      platform_share: platformShare,
      partner_share: [{ name: "AutoEscola Lara", value: partnerShare }],
      instructor_net: instructorNet,
      atrian_log: [
        { check: "sanctions", passed: true, ms: 12 },
        { check: "smurfing", passed: true, ms: 8 }
      ],
      asaas_payload: {
        value: gross,
        billingType: method.toUpperCase(),
        split: [
          { walletId: "wal_lara_123", fixedValue: platformShare + partnerShare },
          { walletId: "wal_instructor_456", fixedValue: instructorNet }
        ]
      }
    });
  };

  return (
    <div className="p-8 max-w-6xl mx-auto mt-20">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-3">
            <Building2 className="text-emerald-400" /> Sandbox Split Tester
          </h1>
          <p className="text-slate-400 mt-2">Demonstração ao vivo do Motor de Split Integrado (Parceria Lara).</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls */}
        <div className="col-span-1 lg:col-span-4 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-slate-200 mb-6">Nova Transação</h2>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Valor Bruto (R$)</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                <input 
                  type="number" 
                  value={gross}
                  onChange={e => setGross(Number(e.target.value))}
                  className="w-full bg-slate-800 border-none rounded-lg py-3 pl-10 pr-4 text-slate-200 focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Método de Pagamento</label>
              <div className="grid grid-cols-2 gap-2">
                <button 
                  onClick={() => setMethod('pix')}
                  className={`py-3 rounded-lg border flex items-center justify-center gap-2 font-medium transition-colors ${method === 'pix' ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' : 'bg-slate-800 border-transparent text-slate-400 hover:bg-slate-700'}`}
                >
                  <Zap size={16} /> PIX
                </button>
                <button 
                  onClick={() => setMethod('credit')}
                  className={`py-3 rounded-lg border flex items-center justify-center gap-2 font-medium transition-colors ${method === 'credit' ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' : 'bg-slate-800 border-transparent text-slate-400 hover:bg-slate-700'}`}
                >
                  <CreditCard size={16} /> Cartão
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-2">Parceiro Responsável</label>
              <div className="bg-slate-800 px-4 py-3 rounded-lg text-slate-300 flex items-center gap-3 border border-slate-700">
                <Building2 size={18} className="text-slate-400"/> AutoEscola Lara (15%)
              </div>
            </div>

            <button 
              onClick={simulateSplit}
              className="w-full py-4 mt-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg shadow-emerald-500/20 transition-all active:scale-[0.98]"
            >
              Simular Roteamento
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="col-span-1 lg:col-span-8 flex flex-col gap-6">
          {simulated ? (
            <>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-6">Fluxo Financeiro (Net)</h3>
                
                <div className="grid grid-cols-4 gap-4">
                  <div className="p-4 bg-slate-800 rounded-xl border border-slate-700">
                    <div className="text-xs text-slate-400 mb-1">Taxa Asaas</div>
                    <div className="text-lg font-bold text-red-400">R$ {simulated.fee_asaas.toFixed(2)}</div>
                  </div>
                  <div className="p-4 bg-slate-800 rounded-xl border border-slate-700 opacity-80">
                    <div className="text-xs text-slate-400 mb-1">Share EGOS (5%)</div>
                    <div className="text-lg font-bold text-amber-400">R$ {simulated.platform_share.toFixed(2)}</div>
                  </div>
                  <div className="p-4 bg-emerald-900/20 rounded-xl border border-emerald-500/30">
                    <div className="text-xs text-emerald-400/70 mb-1">Parceiro Lara (15%)</div>
                    <div className="text-lg font-bold text-emerald-400">R$ {simulated.partner_share[0].value.toFixed(2)}</div>
                  </div>
                  <div className="p-4 bg-blue-900/20 rounded-xl border border-blue-500/30">
                    <div className="text-xs text-blue-400/70 mb-1">Instrutor Liquido</div>
                    <div className="text-lg font-bold text-blue-400">R$ {simulated.instructor_net.toFixed(2)}</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <ShieldCheck size={16} className="text-violet-400"/> ATRiAN Payment Guard
                  </h3>
                  <div className="space-y-3">
                    {simulated.atrian_log.map((log: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm">
                        <span className="text-slate-300 capitalize">{log.check} Check</span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-mono text-slate-500">{log.ms}ms</span>
                          <span className="px-2 py-1 rounded bg-green-500/10 text-green-400 font-medium text-xs border border-green-500/20">PASSED</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col">
                  <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Payload Asaas (JSON)</h3>
                  <pre className="flex-grow bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-emerald-300 overflow-auto font-mono">
                    {JSON.stringify(simulated.asaas_payload, null, 2)}
                  </pre>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full min-h-[400px] border-2 border-dashed border-slate-800 rounded-3xl flex flex-col items-center justify-center text-slate-500">
              <DollarSign size={48} className="text-slate-700 mb-4" />
              <p>Insira os valores e clique em Simular</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Icon helper since Zap isn't imported from lucide
function Zap(props: any) {
  return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>;
}
