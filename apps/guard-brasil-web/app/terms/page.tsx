'use client';

import Link from 'next/link';

export default function TermsPage() {
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
            <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold mb-2">Termos de Uso</h1>
        <p className="text-sm text-slate-500 mb-12">Ultima atualizacao: 03 de abril de 2026</p>

        <div className="space-y-10 text-slate-300 leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">1. Aceitacao dos Termos</h2>
            <p className="text-sm">
              Ao acessar ou utilizar a API Guard Brasil (&quot;Servico&quot;), voce concorda
              com estes Termos de Uso. Se voce nao concorda com algum termo, nao
              utilize o Servico. O uso continuado constitui aceitacao integral.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">2. Descricao do Servico</h2>
            <p className="text-sm">
              O Guard Brasil e uma API de deteccao e mascaramento de dados pessoais
              (PII) em texto, com validacao etica ATRiAN. O Servico e oferecido
              &quot;como esta&quot; (as-is), sem garantias de disponibilidade, precisao
              ou adequacao a fins especificos.
            </p>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">3. Processamento de Dados</h2>
            <p className="text-sm">
              O texto enviado para inspecao e processado inteiramente em memoria e
              descartado imediatamente apos o processamento. Nenhum conteudo de texto
              e armazenado. Apenas o hash SHA-256 do resultado e mantido como receipt
              de auditoria, conforme detalhado na nossa Politica de Privacidade.
            </p>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">4. Uso Aceitavel</h2>
            <p className="text-sm mb-3">Voce concorda em nao utilizar o Servico para:</p>
            <ul className="text-sm space-y-2 ml-4">
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">&#x2717;</span>
                Processar, transmitir ou armazenar conteudo ilegal
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">&#x2717;</span>
                Tentar reverter hashes SHA-256 ou extrair dados de receipts
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">&#x2717;</span>
                Realizar ataques de negacao de servico ou abuso de rate limits
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">&#x2717;</span>
                Compartilhar sua chave de API com terceiros nao autorizados
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">&#x2717;</span>
                Utilizar o Servico para fins que violem legislacao brasileira vigente
              </li>
            </ul>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">5. Isencao de Garantias</h2>
            <p className="text-sm">
              O Servico e fornecido &quot;como esta&quot; e &quot;conforme
              disponivel&quot;, sem garantias de qualquer tipo, expressas ou
              implicitas. Nao garantimos que o Servico sera ininterrupto, livre de
              erros, ou que atendera a todos os requisitos regulatorios do seu caso
              de uso especifico. A conformidade LGPD e um esforco continuo, nao uma
              garantia absoluta.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">6. Limitacao de Responsabilidade</h2>
            <p className="text-sm">
              Em nenhuma hipotese o Guard Brasil, seus desenvolvedores ou a equipe
              EGOS serao responsaveis por danos diretos, indiretos, incidentais,
              especiais ou consequenciais decorrentes do uso ou impossibilidade de uso
              do Servico. A responsabilidade total esta limitada ao valor pago pelo
              usuario nos ultimos 12 meses.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">7. Chaves de API</h2>
            <p className="text-sm">
              Voce e responsavel por manter a seguranca da sua chave de API. Chaves
              comprometidas devem ser revogadas imediatamente entrando em contato
              conosco. Reservamo-nos o direito de revogar chaves que violem estes
              Termos ou que apresentem uso abusivo.
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">8. Alteracoes nos Termos</h2>
            <p className="text-sm">
              Podemos atualizar estes Termos a qualquer momento. Alteracoes
              significativas serao comunicadas por email (se disponivel) ou por aviso
              no site. O uso continuado apos as alteracoes constitui aceitacao dos
              novos termos.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">9. Legislacao Aplicavel</h2>
            <p className="text-sm">
              Estes Termos sao regidos pelas leis da Republica Federativa do Brasil.
              Qualquer disputa sera submetida ao foro da comarca de domicilio do
              desenvolvedor, com exclusao de qualquer outro, por mais privilegiado
              que seja.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-lg font-bold text-emerald-400 mb-3">10. Contato</h2>
            <p className="text-sm">
              Duvidas sobre estes Termos podem ser enviadas para{' '}
              <a href="mailto:enio@egos.ia.br" className="text-emerald-400 hover:text-emerald-300 transition">
                enio@egos.ia.br
              </a>.
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
          <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
        </div>
        <p className="text-xs text-slate-600">
          Guard Brasil | @egosbr/guard-brasil | MIT License
        </p>
      </footer>
    </div>
  );
}
