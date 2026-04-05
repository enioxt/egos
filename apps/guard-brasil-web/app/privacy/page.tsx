'use client';

import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/landing" className="text-emerald-400 font-bold text-lg hover:text-emerald-300 transition">
            Guard Brasil
          </Link>
          <nav className="flex gap-6 text-sm text-slate-400">
            <Link href="/about" className="hover:text-white transition">Sobre</Link>
            <Link href="/faq" className="hover:text-white transition">FAQ</Link>
            <Link href="/terms" className="hover:text-white transition">Termos</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold mb-2">Politica de Privacidade</h1>
        <p className="text-sm text-slate-500 mb-12">Ultima atualizacao: 03 de abril de 2026</p>

        <div className="space-y-10 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">1. Dados que Coletamos</h2>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div>
                <p className="text-sm font-bold text-white mb-1">O que coletamos:</p>
                <ul className="text-sm space-y-1 ml-4">
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-400">&#x2713;</span>
                    Nome e email (para geracao de chave de API)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-400">&#x2713;</span>
                    Hashes SHA-256 dos resultados de inspecao (para trilha de auditoria)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-400">&#x2713;</span>
                    Metadados de uso (contagem de chamadas, timestamps)
                  </li>
                </ul>
              </div>
              <div>
                <p className="text-sm font-bold text-white mb-1">O que NAO coletamos:</p>
                <ul className="text-sm space-y-1 ml-4">
                  <li className="flex items-start gap-2">
                    <span className="text-red-400">&#x2717;</span>
                    O texto que voce envia para inspecao (processado em memoria, descartado)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400">&#x2717;</span>
                    Dados pessoais detectados no texto (mascarados antes de qualquer log)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400">&#x2717;</span>
                    Dados de navegacao, localizacao ou fingerprint do dispositivo
                  </li>
                </ul>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">2. Hashes SHA-256</h2>
            <p className="text-sm">
              Os hashes SHA-256 armazenados como receipts de auditoria sao
              irreversiveis. Nao e possivel reconstruir o texto original a partir
              do hash. Esses receipts servem exclusivamente para comprovar que uma
              inspecao foi realizada em determinado momento, garantindo conformidade
              com a LGPD.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">3. Infraestrutura e Armazenamento</h2>
            <p className="text-sm mb-3">
              Utilizamos o Supabase para gerenciamento de tenants e chaves de API.
            </p>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <ul className="text-sm space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">&#x2022;</span>
                  <span><strong className="text-white">Provedor:</strong> Supabase (PostgreSQL gerenciado)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">&#x2022;</span>
                  <span><strong className="text-white">Regiao:</strong> us-east-1</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">&#x2022;</span>
                  <span><strong className="text-white">Criptografia:</strong> Em repouso (AES-256) e em transito (TLS 1.3)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">&#x2022;</span>
                  <span><strong className="text-white">Backups:</strong> Diarios, retencao de 7 dias</span>
                </li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">4. Cookies</h2>
            <p className="text-sm">
              O Guard Brasil nao utiliza cookies de rastreamento. O unico cookie
              possivel e o de autenticacao Privy (se habilitado), necessario para
              manter a sessao do usuario. Nenhum cookie de terceiros e utilizado
              para publicidade ou analytics.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">5. Conformidade LGPD</h2>
            <p className="text-sm mb-3">
              O Guard Brasil foi projetado em conformidade com a Lei Geral de
              Protecao de Dados (Lei 13.709/2018):
            </p>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <ul className="text-sm space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-emerald-400 font-mono text-xs mt-0.5 flex-shrink-0">Art. 6</span>
                  <span>
                    <strong className="text-white">Minimizacao de dados:</strong> Coletamos
                    apenas o minimo necessario (nome + email). O texto inspecionado
                    nunca e armazenado.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-emerald-400 font-mono text-xs mt-0.5 flex-shrink-0">Art. 46</span>
                  <span>
                    <strong className="text-white">Medidas de seguranca:</strong> Processamento
                    em memoria, hashes irreversiveis, criptografia em transito e em
                    repouso, rate limiting por chave.
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-emerald-400 font-mono text-xs mt-0.5 flex-shrink-0">Art. 18</span>
                  <span>
                    <strong className="text-white">Direitos do titular:</strong> Voce pode
                    solicitar acesso, correcao ou exclusao dos seus dados a qualquer
                    momento.
                  </span>
                </li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">6. Encarregado (DPO)</h2>
            <p className="text-sm">
              Para questoes relacionadas a privacidade e protecao de dados, entre
              em contato com o Encarregado de Protecao de Dados:{' '}
              <a href="mailto:enio@egos.ia.br" className="text-emerald-400 hover:text-emerald-300 transition">
                enio@egos.ia.br
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">7. Direito a Exclusao</h2>
            <p className="text-sm">
              Solicite a exclusao completa dos seus dados (nome, email, chaves de API e receipts) enviando email para{' '}
              <a href="mailto:enio@egos.ia.br" className="text-emerald-400 hover:text-emerald-300 transition">enio@egos.ia.br</a>{' '}
              com o assunto &quot;Exclusao de Dados&quot;. Prazo: ate 15 dias uteis.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">8. Alteracoes nesta Politica</h2>
            <p className="text-sm">
              Podemos atualizar esta Politica periodicamente. Alteracoes significativas serao comunicadas por email ou aviso no site.
            </p>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-4">
          <Link href="/landing" className="hover:text-white transition">Inicio</Link>
          <Link href="/about" className="hover:text-white transition">Sobre</Link>
          <Link href="/faq" className="hover:text-white transition">FAQ</Link>
          <Link href="/terms" className="hover:text-white transition">Termos</Link>
        </div>
        <p className="text-xs text-slate-600">
          Guard Brasil | @egosbr/guard-brasil | MIT License
        </p>
      </footer>
    </div>
  );
}
