import { BookOpen, CheckCircle2, FileText } from 'lucide-react'
import { commonsPlanSections, sourceDocs } from '../lib/commonsContent'

export function CommonsPlanPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto mt-20">
      <div className="flex items-center gap-3 mb-4">
        <BookOpen className="text-violet-400" size={30} />
        <h1 className="text-3xl font-bold text-slate-100">Plano do EGOS Commons</h1>
      </div>
      <p className="text-slate-400 mb-8">
        Consolidação do plano de negócio corrigido para o Commons: foco em produtos reais, serviços pagos e governança como diferencial.
      </p>

      <div className="grid gap-4 mb-10">
        {commonsPlanSections.map((item) => (
          <div key={item} className="rounded-2xl border border-slate-800 bg-slate-900 p-5 flex gap-3 items-start">
            <CheckCircle2 className="text-emerald-400 mt-0.5" size={18} />
            <p className="text-slate-200 text-sm leading-6">{item}</p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <FileText size={18} className="text-cyan-400" /> Documentos vinculados
        </h2>
        <ul className="space-y-3 text-sm text-slate-300">
          {sourceDocs.map((doc) => (
            <li key={doc} className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">{doc}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
