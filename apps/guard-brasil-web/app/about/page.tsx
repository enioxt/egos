'use client';

import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/landing" className="text-emerald-400 font-bold text-lg hover:text-emerald-300 transition">
            Guard Brasil
          </Link>
          <nav className="flex gap-6 text-sm text-slate-400">
            <Link href="/faq" className="hover:text-white transition">FAQ</Link>
            <Link href="/terms" className="hover:text-white transition">Termos</Link>
            <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold mb-8">Sobre o Guard Brasil</h1>

        {/* Mission */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-emerald-400 mb-4">Nossa Missao</h2>
          <p className="text-slate-300 text-lg leading-relaxed">
            Proteger dados pessoais brasileiros em sistemas de IA. O Guard Brasil
            existe para que empresas e desenvolvedores possam processar texto com
            seguranca, garantindo conformidade com a LGPD (Lei 13.709/2018) sem
            complexidade.
          </p>
        </section>

        {/* How it works */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-emerald-400 mb-4">Como Funciona</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-start gap-4">
              <span className="text-2xl">🔍</span>
              <div>
                <p className="font-bold text-sm mb-1">Deteccao baseada em regex</p>
                <p className="text-sm text-slate-400">
                  Nenhum LLM e necessario para a deteccao de PII. Utilizamos expressoes
                  regulares altamente otimizadas para identificar 15 tipos de dados
                  pessoais brasileiros (CPF, CNPJ, RG, CNH, titulo de eleitor, MASP,
                  REDS, placa veicular, e mais).
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">⚡</span>
              <div>
                <p className="font-bold text-sm mb-1">4ms de latencia de referencia</p>
                <p className="text-sm text-slate-400">
                  Processamento ultrarapido porque nao depende de chamadas a modelos
                  de linguagem. A inspecao acontece inteiramente em memoria, no servidor.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">🔒</span>
              <div>
                <p className="font-bold text-sm mb-1">Processamento 100% local</p>
                <p className="text-sm text-slate-400">
                  O texto enviado e processado em memoria e descartado imediatamente.
                  Nenhum dado e armazenado. Apenas o hash SHA-256 e mantido como
                  receipt de auditoria.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <span className="text-2xl">🧠</span>
              <div>
                <p className="font-bold text-sm mb-1">Validacao etica ATRiAN</p>
                <p className="text-sm text-slate-400">
                  Alem do mascaramento de PII, o Guard Brasil oferece um score etico
                  de 0 a 100 que detecta vies, conteudo discriminatorio e violacoes
                  eticas no texto.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Team */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-emerald-400 mb-4">Equipe</h2>
          <p className="text-slate-300 leading-relaxed">
            Desenvolvido por <strong className="text-white">Enio Rocha</strong> e equipe EGOS.
            O Guard Brasil e parte do ecossistema EGOS, uma plataforma multi-agente
            focada em governanca, etica e seguranca de IA.
          </p>
        </section>

        {/* Contact */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-emerald-400 mb-4">Contato</h2>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <p className="text-slate-300 mb-2">
              Email:{' '}
              <a href="mailto:enio@egos.ia.br" className="text-emerald-400 hover:text-emerald-300 transition">
                enio@egos.ia.br
              </a>
            </p>
            <p className="text-slate-300 mb-2">
              GitHub:{' '}
              <a
                href="https://github.com/enioxt/egos"
                className="text-emerald-400 hover:text-emerald-300 transition"
                target="_blank"
                rel="noopener noreferrer"
              >
                github.com/enioxt/egos
              </a>
            </p>
            <p className="text-slate-300">
              npm:{' '}
              <a
                href="https://www.npmjs.com/package/@egosbr/guard-brasil"
                className="text-emerald-400 hover:text-emerald-300 transition"
                target="_blank"
                rel="noopener noreferrer"
              >
                @egosbr/guard-brasil
              </a>
            </p>
          </div>
        </section>

        {/* Disclaimer */}
        <section className="mb-12">
          <div className="bg-amber-950/20 border border-amber-900/30 rounded-2xl p-6">
            <p className="text-sm text-amber-300 font-bold mb-2">Aviso</p>
            <p className="text-sm text-slate-400">
              Projeto independente em fase de validacao. Sem CNPJ por enquanto.
              O Guard Brasil e oferecido como esta, sem garantias de disponibilidade
              ou adequacao a fins especificos.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-4">
          <Link href="/landing" className="hover:text-white transition">Inicio</Link>
          <Link href="/faq" className="hover:text-white transition">FAQ</Link>
          <Link href="/terms" className="hover:text-white transition">Termos</Link>
          <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
        </div>
        <p className="text-xs text-slate-600">
          Guard Brasil | @egosbr/guard-brasil | MIT License
        </p>
      </footer>
    </div>
  );
}
