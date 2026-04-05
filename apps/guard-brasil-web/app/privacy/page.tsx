'use client';

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-300 px-4 py-16 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">Política de Privacidade</h1>
      <p className="text-xs text-slate-500 mb-8">Última atualização: 5 de abril de 2026</p>

      <section className="space-y-6 text-sm leading-relaxed">
        <div>
          <h2 className="text-lg font-semibold text-white mb-2">1. O que coletamos</h2>
          <p><strong>Para gerar sua chave de API:</strong> nome e email. Armazenados no Supabase (região us-east-1) para autenticação e controle de quota.</p>
          <p className="mt-2"><strong>Para cada chamada à API:</strong> apenas metadados — hash SHA-256 do texto de entrada, hash do resultado, timestamp, duração, e ID do tenant. <em>O texto original NÃO é armazenado.</em></p>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">2. O que NÃO coletamos</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>O texto enviado para inspeção (processado em memória, descartado imediatamente)</li>
            <li>Dados pessoais detectados (CPF, RG, etc.) — apenas a categoria é registrada</li>
            <li>Endereço IP completo (apenas hash irreversível para rate limiting)</li>
            <li>Cookies de rastreamento (sem analytics de terceiros)</li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">3. Como processamos dados</h2>
          <p>O Guard Brasil utiliza expressões regulares (regex) para detecção de PII. Todo processamento é feito em memória no servidor, sem envio para LLMs ou serviços externos. O texto é descartado após a resposta ser enviada.</p>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">4. Conformidade LGPD</h2>
          <p>Em conformidade com a Lei 13.709/2018 (LGPD):</p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li><strong>Art. 6, III (Necessidade):</strong> coletamos apenas o mínimo necessário (nome + email)</li>
            <li><strong>Art. 46 (Segurança):</strong> dados em trânsito via HTTPS/TLS, hashing SHA-256, sem armazenamento de PII</li>
            <li><strong>Art. 12 (Anonimização):</strong> textos processados são anonimizados em memória</li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">5. Receipts e auditoria</h2>
          <p>Cada inspeção gera um receipt com 3 hashes SHA-256: entrada, saída e inspeção. Esses hashes são irreversíveis — não é possível reconstruir o texto original a partir deles. Servem como prova auditável de que a inspeção ocorreu.</p>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">6. Seus direitos</h2>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Acesso:</strong> solicite seus dados via email</li>
            <li><strong>Correção:</strong> solicite correção de dados cadastrais</li>
            <li><strong>Exclusão:</strong> solicite exclusão completa da sua conta e dados</li>
            <li><strong>Portabilidade:</strong> exporte seus dados em formato JSON</li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-2">7. Contato</h2>
          <p>Para questões de privacidade: <a href="mailto:enio@egos.ia.br" className="text-emerald-400 hover:underline">enio@egos.ia.br</a></p>
        </div>
      </section>

      <div className="mt-12 flex gap-4 text-xs text-slate-500">
        <a href="/landing" className="hover:text-emerald-400">← Voltar</a>
        <a href="/terms" className="hover:text-emerald-400">Termos de Uso</a>
        <a href="/faq" className="hover:text-emerald-400">FAQ</a>
        <a href="/about" className="hover:text-emerald-400">Sobre</a>
      </div>
    </main>
  );
}
