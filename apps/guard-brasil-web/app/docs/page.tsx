'use client';

import { useState } from 'react';

const BASE_URL = 'https://guard.egos.ia.br';
const EAGLE_URL = 'https://eagleeye.egos.ia.br';

export default function DocsPage() {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  function copy(text: string, id: string) {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-mono">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900/50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛡️</span>
            <div>
              <div className="font-bold text-white">EGOS API — Documentação</div>
              <div className="text-xs text-gray-400">Guard Brasil + Eagle Eye</div>
            </div>
          </div>
          <a
            href="/landing"
            className="text-xs text-amber-400 border border-amber-400/30 px-3 py-1.5 rounded hover:bg-amber-400/10 transition"
          >
            ← Obter chave gratuita
          </a>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Quick start */}
        <section className="mb-12">
          <h1 className="text-3xl font-bold text-white mb-2">Início Rápido</h1>
          <p className="text-gray-400 mb-8">
            Duas APIs, uma chave. Sua chave <code className="text-amber-300">gb_live_*</code> funciona em ambas.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="border border-gray-700 rounded-xl p-5 bg-gray-900/40">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">🛡️</span>
                <span className="font-bold text-white">Guard Brasil API</span>
              </div>
              <p className="text-sm text-gray-400 mb-2">
                Detecção de PII no texto: CPF, CNPJ, RG, telefone, endereço.
              </p>
              <div className="text-xs text-green-400">✓ 150 chamadas/mês grátis</div>
              <div className="text-xs text-gray-500 mt-1">{BASE_URL}/v1/inspect</div>
            </div>
            <div className="border border-gray-700 rounded-xl p-5 bg-gray-900/40">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">🦅</span>
                <span className="font-bold text-white">Eagle Eye API</span>
              </div>
              <p className="text-sm text-gray-400 mb-2">
                Inteligência de licitações: 121+ oportunidades de 80 municípios brasileiros.
              </p>
              <div className="text-xs text-green-400">✓ Mesma chave, 150 chamadas/mês grátis</div>
              <div className="text-xs text-gray-500 mt-1">{EAGLE_URL}/api/opportunities</div>
            </div>
          </div>
        </section>

        {/* Guard Brasil */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
            <span>🛡️</span> Guard Brasil — Detecção de PII
          </h2>
          <p className="text-gray-400 text-sm mb-6">
            Identifica e redige dados pessoais sensíveis em qualquer texto.
          </p>

          <CodeBlock
            id="inspect-curl"
            title="Detectar PII — cURL"
            lang="bash"
            code={`curl -X POST ${BASE_URL}/v1/inspect \\
  -H "Authorization: Bearer SEU_GB_LIVE_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "O CPF do cliente é 123.456.789-00 e o telefone é (11) 99999-0000"}'`}
            onCopy={copy}
            copiedId={copiedId}
          />

          <CodeBlock
            id="inspect-js"
            title="Detectar PII — JavaScript/TypeScript"
            lang="typescript"
            code={`const response = await fetch('${BASE_URL}/v1/inspect', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer SEU_GB_LIVE_KEY',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'O CPF do cliente é 123.456.789-00 e o telefone é (11) 99999-0000',
  }),
});

const result = await response.json();
// result.verdict: 'blocked' | 'allowed'
// result.pii_found: ['CPF', 'TELEFONE']
// result.redacted_text: 'O CPF do cliente é [CPF REDACTED] e...'
console.log(result);`}
            onCopy={copy}
            copiedId={copiedId}
          />

          <CodeBlock
            id="inspect-python"
            title="Detectar PII — Python"
            lang="python"
            code={`import requests

response = requests.post(
    '${BASE_URL}/v1/inspect',
    headers={'Authorization': 'Bearer SEU_GB_LIVE_KEY'},
    json={'text': 'O CPF do cliente é 123.456.789-00 e o telefone é (11) 99999-0000'},
)
result = response.json()
print(result['verdict'])      # 'blocked' ou 'allowed'
print(result['pii_found'])    # ['CPF', 'TELEFONE']
print(result['redacted_text'])  # texto com PII substituído`}
            onCopy={copy}
            copiedId={copiedId}
          />

          <div className="border border-gray-700 rounded-xl p-5 bg-gray-900/40 mt-4">
            <div className="text-sm font-bold text-gray-300 mb-3">Exemplo de Resposta</div>
            <pre className="text-xs text-green-300 overflow-x-auto">{`{
  "verdict": "blocked",
  "confidence": 0.97,
  "pii_found": ["CPF", "TELEFONE"],
  "redacted_text": "O CPF do cliente é [CPF REDACTED] e o telefone é [TELEFONE REDACTED]",
  "atrian_score": 8.2,
  "processing_time_ms": 45,
  "remaining_quota": 149
}`}</pre>
          </div>

          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            {['CPF', 'CNPJ', 'RG', 'E-MAIL', 'TELEFONE', 'ENDEREÇO', 'NOME', 'MASP'].map(t => (
              <div key={t} className="text-xs text-center border border-gray-700 rounded px-2 py-1.5 text-gray-300">
                {t}
              </div>
            ))}
          </div>
        </section>

        {/* Eagle Eye */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
            <span>🦅</span> Eagle Eye — Inteligência de Licitações
          </h2>
          <p className="text-gray-400 text-sm mb-6">
            Oportunidades de licitações detectadas por IA em Diários Oficiais de 80 municípios.
          </p>

          <CodeBlock
            id="opps-curl"
            title="Listar Oportunidades — cURL"
            lang="bash"
            code={`curl "${EAGLE_URL}/api/opportunities?limit=10&category=TI" \\
  -H "Authorization: Bearer SEU_GB_LIVE_KEY"`}
            onCopy={copy}
            copiedId={copiedId}
          />

          <CodeBlock
            id="opps-js"
            title="Listar Oportunidades — JavaScript"
            lang="typescript"
            code={`// Buscar oportunidades de TI com alto potencial
const response = await fetch(
  '${EAGLE_URL}/api/opportunities?limit=20&status=open',
  { headers: { 'Authorization': 'Bearer SEU_GB_LIVE_KEY' } }
);
const { data, count } = await response.json();

// Filtrar por TI/Software
const software = data.filter(o =>
  o.category?.includes('TI') || o.ai_summary?.includes('software')
);

software.forEach(o => {
  console.log(\`[\${o.market_potential}] \${o.title}\`);
  console.log(\`  \${o.territory_name} — R$ \${o.estimated_value_brl?.toLocaleString('pt-BR')}\`);
  console.log(\`  \${o.source_url}\`);
});`}
            onCopy={copy}
            copiedId={copiedId}
          />

          <div className="border border-gray-700 rounded-xl p-5 bg-gray-900/40 mt-4">
            <div className="text-sm font-bold text-gray-300 mb-3">Parâmetros da API</div>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500 border-b border-gray-700">
                  <th className="text-left py-2 pr-4">Parâmetro</th>
                  <th className="text-left py-2 pr-4">Tipo</th>
                  <th className="text-left py-2">Descrição</th>
                </tr>
              </thead>
              <tbody className="text-gray-300">
                {[
                  ['limit', 'number', 'Máximo de resultados (padrão: 20, máx: 100)'],
                  ['offset', 'number', 'Paginação'],
                  ['status', 'string', 'open | closed'],
                  ['category', 'string', 'Filtro parcial: TI, SAUDE, OBRAS...'],
                  ['territory_id', 'uuid', 'UUID do território (de /api/territories)'],
                ].map(([p, t, d]) => (
                  <tr key={p} className="border-b border-gray-800">
                    <td className="py-2 pr-4 text-amber-300">{p}</td>
                    <td className="py-2 pr-4 text-blue-300">{t}</td>
                    <td className="py-2 text-gray-400">{d}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Auth */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-4">Autenticação</h2>
          <div className="border border-gray-700 rounded-xl p-5 bg-gray-900/40">
            <p className="text-sm text-gray-400 mb-4">
              Todas as requisições precisam do header <code className="text-amber-300">Authorization</code>:
            </p>
            <pre className="text-xs text-amber-300 bg-black/40 p-3 rounded mb-4">
              Authorization: Bearer gb_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...
            </pre>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              {[
                ['401 Unauthorized', 'red', 'Chave inválida ou ausente'],
                ['429 Quota Exceeded', 'yellow', 'Limite atingido — faça upgrade'],
                ['200 OK', 'green', 'Sucesso + X-RateLimit-Remaining'],
              ].map(([code, color, desc]) => (
                <div key={code} className={`border border-${color}-700/40 rounded p-3 bg-${color}-900/10`}>
                  <div className={`font-bold text-${color}-400 mb-1`}>{code}</div>
                  <div className="text-gray-400">{desc}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-white mb-4">Planos</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                name: 'Free',
                price: 'R$ 0',
                period: '/mês',
                features: ['150 chamadas/mês', 'Guard Brasil + Eagle Eye', 'Sem cartão de crédito', 'Suporte comunidade'],
                cta: 'Criar conta grátis',
                href: '/landing',
                highlight: false,
              },
              {
                name: 'Pro',
                price: 'R$ 497',
                period: '/mês',
                features: ['10.000 chamadas/mês', 'Guard Brasil + Eagle Eye', 'Alertas por email/Telegram', 'Suporte prioritário'],
                cta: 'Assinar Pro',
                href: 'mailto:enio@egos.ia.br?subject=Eagle Eye Pro',
                highlight: true,
              },
              {
                name: 'Enterprise',
                price: 'R$ 1.497',
                period: '/mês',
                features: ['Chamadas ilimitadas', 'SLA 99.9%', 'IP whitelist', 'Suporte dedicado + SLAs'],
                cta: 'Falar com vendas',
                href: 'mailto:enio@egos.ia.br?subject=Eagle Eye Enterprise',
                highlight: false,
              },
            ].map(plan => (
              <div
                key={plan.name}
                className={`rounded-xl p-6 border ${plan.highlight
                  ? 'border-amber-500 bg-amber-950/20'
                  : 'border-gray-700 bg-gray-900/40'
                }`}
              >
                {plan.highlight && (
                  <div className="text-xs font-bold text-amber-400 bg-amber-400/10 border border-amber-400/30 rounded-full px-3 py-1 w-fit mb-3">
                    MAIS POPULAR
                  </div>
                )}
                <div className="font-bold text-white text-lg mb-1">{plan.name}</div>
                <div className="mb-4">
                  <span className="text-2xl font-bold text-white">{plan.price}</span>
                  <span className="text-gray-400 text-sm">{plan.period}</span>
                </div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map(f => (
                    <li key={f} className="text-sm text-gray-300 flex items-center gap-2">
                      <span className="text-green-400">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <a
                  href={plan.href}
                  className={`block text-center py-2 rounded-lg text-sm font-medium transition ${plan.highlight
                    ? 'bg-amber-500 text-black hover:bg-amber-400'
                    : 'border border-gray-600 text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  {plan.cta}
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-gray-800 pt-8 text-center">
          <p className="text-gray-500 text-sm">
            Dúvidas? <a href="mailto:enio@egos.ia.br" className="text-amber-400 hover:underline">enio@egos.ia.br</a>
            {' · '}
            <a href="/landing" className="text-amber-400 hover:underline">Criar conta grátis</a>
            {' · '}
            <a href={EAGLE_URL} target="_blank" rel="noopener noreferrer" className="text-amber-400 hover:underline">Eagle Eye Dashboard</a>
          </p>
        </footer>
      </div>
    </div>
  );
}

// ── CodeBlock Component ───────────────────────────────────────────────────────

function CodeBlock({
  id,
  title,
  lang,
  code,
  onCopy,
  copiedId,
}: {
  id: string;
  title: string;
  lang: string;
  code: string;
  onCopy: (text: string, id: string) => void;
  copiedId: string | null;
}) {
  return (
    <div className="border border-gray-700 rounded-xl overflow-hidden mb-4">
      <div className="flex items-center justify-between bg-gray-800/60 px-4 py-2">
        <span className="text-xs text-gray-400">{title}</span>
        <button
          onClick={() => onCopy(code, id)}
          className="text-xs text-gray-400 hover:text-white transition px-2 py-1 rounded hover:bg-gray-700"
        >
          {copiedId === id ? '✓ Copiado' : 'Copiar'}
        </button>
      </div>
      <pre className="bg-black/40 p-4 text-xs text-gray-300 overflow-x-auto leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}
