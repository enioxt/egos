import { CircleDollarSign, Users, ShieldCheck } from 'lucide-react'
import { marketEvidence, splitPersonas } from '../lib/commonsContent'

export function PersonasSplitPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto mt-20">
      <div className="flex items-center gap-3 mb-4">
        <Users className="text-emerald-400" size={30} />
        <h1 className="text-3xl font-bold text-slate-100">Personas e Split de Pagamentos</h1>
      </div>
      <p className="text-slate-400 mb-8">
        Quem realmente compra e opera infraestrutura de split no ecossistema EGOS, com base no Commons, Carteira Livre e pesquisa externa.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        {splitPersonas.map((persona) => (
          <div key={persona.title} className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="flex items-center gap-2 mb-3 text-emerald-400 font-semibold">
              <CircleDollarSign size={18} /> {persona.title}
            </div>
            <p className="text-slate-300 text-sm mb-3"><strong>Quem:</strong> {persona.who}</p>
            <p className="text-slate-300 text-sm"><strong>Dor:</strong> {persona.why}</p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <ShieldCheck size={18} className="text-violet-400" /> Evidência de mercado
        </h2>
        <ul className="space-y-3 text-sm text-slate-300">
          {marketEvidence.map((item) => (
            <li key={item} className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">{item}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
