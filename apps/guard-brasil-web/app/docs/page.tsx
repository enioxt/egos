'use client';

import { useState } from 'react';
import Link from 'next/link';

const API_URL = 'https://guard.egos.ia.br';

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
      className="text-xs text-slate-500 hover:text-emerald-400 transition px-2 py-1 rounded border border-slate-700 hover:border-emerald-600/50 flex-shrink-0"
    >
      {copied ? '✓' : 'copiar'}
    </button>
  );
}

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
        <span className="text-xs text-slate-600 font-mono">{lang}</span>
        <CopyButton text={code} />
      </div>
      <pre className="p-4 text-sm font-mono text-slate-300 overflow-x-auto leading-relaxed whitespace-pre-wrap"><code>{code}</code></pre>
    </div>
  );
}

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 sticky top-0 bg-slate-950/95 backdrop-blur z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/landing" className="text-emerald-400 font-bold text-lg hover:text-emerald-300 transition">Guard Brasil</Link>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 text-sm">API Reference</span>
          </div>
          <nav className="flex gap-4 text-sm">
            <Link href="/integrations" className="text-slate-400 hover:text-white transition">Integrações</Link>
            <Link href="/landing#get-key" className="text-emerald-400 hover:text-emerald-300 transition font-medium">Chave grátis →</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-12 space-y-16">

        {/* Hero */}
        <div>
          <h1 className="text-4xl font-bold mb-3">Guard Brasil API — Referência</h1>
          <p className="text-slate-400 text-lg mb-6">Detecção e mascaramento de PII brasileiro. 15 padrões. SHA-256 receipts. Compliance LGPD.</p>
          <div className="flex flex-wrap gap-3">
            {['v0.2.2','REST + npm','15 tipos PII BR','SHA-256 receipts','ATRiAN scoring','500 chamadas/mês grátis'].map(tag => (
              <span key={tag} className="px-2 py-1 bg-slate-800 text-slate-400 rounded border border-slate-700 text-sm">{tag}</span>
            ))}
          </div>
        </div>

        {/* Quick start */}
        <section>
          <h2 className="text-2xl font-bold mb-6">Início em 60 segundos</h2>
          <div className="space-y-4">
            <CodeBlock lang="bash" code={`# Passo 1 — Gere sua chave gratuita (sem cartão)
curl -X POST ${API_URL}/v1/keys \\
  -H "Content-Type: application/json" \\
  -d '{"name": "meu-projeto", "email": "dev@empresa.com.br"}'
# → {"key": "gb_live_abc123...", "quota_limit": 500}`} />
            <CodeBlock lang="bash" code={`# Passo 2 — Use imediatamente
curl -X POST ${API_URL}/v1/inspect \\
  -H "Authorization: Bearer gb_live_SUA_CHAVE" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Cliente João, CPF 123.456.789-09, CNPJ 12.345.678/0001-95"}'`} />
            <CodeBlock lang="json" code={`// Resposta
{
  "safe": false,
  "output": "Cliente João, CPF [CPF REMOVIDO], CNPJ [CNPJ REMOVIDO]",
  "masking": { "findingCount": 2, "findings": [{"category":"cpf"}, {"category":"cnpj"}] },
  "receipt": { "inspectionHash": "sha256_para_auditoria_ANPD...", "inspectedAt": "2026-04-05T21:00:00Z" },
  "atrian": { "score": 80, "passed": true }
}`} />
          </div>
        </section>

        {/* Autenticação */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Autenticação</h2>
          <p className="text-slate-400 mb-4">Header <code className="text-amber-300 bg-slate-800 px-1 rounded">Authorization: Bearer gb_live_...</code> em todas as requisições autenticadas.</p>
          <CodeBlock lang="bash" code={`# Variável de ambiente recomendada (nunca hard-code)
export GUARD_BRASIL_API_KEY="gb_live_abc123..."

curl -X POST ${API_URL}/v1/inspect \\
  -H "Authorization: Bearer $GUARD_BRASIL_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "texto"}'`} />
        </section>

        {/* Endpoints */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Endpoints</h2>
          <div className="space-y-2">
            {[
              {m:'GET', p:'/health',             d:'Status do serviço',                           auth:false},
              {m:'GET', p:'/v1/meta',             d:'Contrato da API e planos de preço',           auth:false},
              {m:'GET', p:'/openapi.json',        d:'Especificação OpenAPI 3.0',                   auth:false},
              {m:'GET', p:'/llms.txt',            d:'Arquivo de descoberta para agentes de IA',    auth:false},
              {m:'POST',p:'/v1/keys',             d:'Gera chave de API gratuita (500/mês)',        auth:false},
              {m:'POST',p:'/v1/inspect',          d:'Inspecciona texto — endpoint principal',      auth:true},
              {m:'POST',p:'/v1/stripe/checkout',  d:'Cria sessão de pagamento Stripe',             auth:true},
              {m:'POST',p:'/v1/crypto/checkout',  d:'Checkout NOWPayments (241 criptomoedas)',     auth:true},
            ].map(e => (
              <div key={e.p} className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg border border-slate-800">
                <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded border flex-shrink-0 ${e.m==='GET'?'text-blue-400 bg-blue-900/20 border-blue-700/40':'text-emerald-400 bg-emerald-900/20 border-emerald-700/40'}`}>{e.m}</span>
                <code className="text-sm text-white font-mono flex-1">{e.p}</code>
                <span className="text-sm text-slate-400 hidden md:block">{e.d}</span>
                {e.auth && <span className="text-xs text-amber-500 bg-amber-900/20 border border-amber-700/40 px-2 py-0.5 rounded">Auth</span>}
              </div>
            ))}
          </div>
        </section>

        {/* POST /v1/inspect detalhado */}
        <section>
          <h2 className="text-2xl font-bold mb-1">POST /v1/inspect — Detalhes</h2>
          <p className="text-slate-400 mb-6">Request body e resposta completa com todos os campos.</p>
          <div className="space-y-4">
            <CodeBlock lang="json" code={`// Request body
{
  "text": "string (obrigatório) — texto a inspecionar",
  "sessionId": "string (opcional) — agrupa inspeções na trilha de auditoria"
}`} />
            <CodeBlock lang="json" code={`// Response 200 — exemplo completo
{
  "safe": false,
  "blocked": false,
  "output": "Paciente: [CPF REMOVIDO], cartão [SUS REMOVIDO], CEP [CEP REMOVIDO]",
  "summary": "Issues found: PII: 3 finding(s) (critical)",
  "lgpdDisclosure": "[LGPD] Dados detectados e mascarados: CPF, SUS, CEP. Lei 13.709/2018.",

  "masking": {
    "sensitivityLevel": "critical",
    "findingCount": 3,
    "findings": [
      { "category": "cpf", "label": "CPF", "suggestion": "[CPF REMOVIDO]" },
      { "category": "sus", "label": "SUS", "suggestion": "[SUS REMOVIDO]" },
      { "category": "cep", "label": "CEP", "suggestion": "[CEP REMOVIDO]" }
    ]
  },

  "atrian": { "passed": true, "score": 80, "violationCount": 0, "violations": [] },

  "receipt": {
    "inspectedAt": "2026-04-05T21:00:00.000Z",
    "inputHash": "sha256 do texto original",
    "outputHash": "sha256 do texto mascarado",
    "inspectionHash": "sha256 combinado — armazene este para a ANPD",
    "guardVersion": "0.2.2"
  },

  "meta": { "durationMs": 2, "timestamp": "2026-04-05T21:00:00.000Z", "version": "0.2.2" }
}`} />
          </div>
        </section>

        {/* 15 tipos de PII */}
        <section>
          <h2 className="text-2xl font-bold mb-4">15 Tipos de PII Detectados</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-slate-800">
                <th className="pb-3 text-slate-400 pr-4">Categoria</th>
                <th className="pb-3 text-slate-400 pr-4">ID</th>
                <th className="pb-3 text-slate-400 pr-4">Exemplo</th>
                <th className="pb-3 text-slate-400">Máscara</th>
              </tr></thead>
              <tbody className="text-slate-300">
                {[
                  ['CPF','cpf','123.456.789-09 / 12345678909','[CPF REMOVIDO]'],
                  ['CNPJ','cnpj','12.345.678/0001-95','[CNPJ REMOVIDO]'],
                  ['RG','rg','RG 12.345.678-9 / SP-12.345.678 / MG-12345678','[RG REMOVIDO]'],
                  ['CNH','cnh','CNH 00000000000','[CNH REMOVIDO]'],
                  ['Cartão SUS','sus','898 0012 3456 7890','[SUS REMOVIDO]'],
                  ['NIS / PIS','nis','12345678901','[NIS REMOVIDO]'],
                  ['CEP','cep','01310-100 / 01310100','[CEP REMOVIDO]'],
                  ['Placa Veicular','plate','ABC-1234 (antiga) / ABC1D23 (Mercosul)','[PLACA REMOVIDA]'],
                  ['MASP','masp','MASP 1234567 / 1.234.567-8','[MASP REMOVIDO]'],
                  ['REDS','reds','REDS 2024/0098765','[REDS REMOVIDO]'],
                  ['Processo Judicial','process_number','1234567-89.2024.1.00.0000','[PROCESSO REMOVIDO]'],
                  ['Título de Eleitor','titulo_eleitor','1234 5678 9012','[TÍTULO REMOVIDO]'],
                  ['Telefone','phone','(11) 99999-9999 / +55 11 9 9999-9999','[TELEFONE REMOVIDO]'],
                  ['E-mail','email','joao@empresa.com.br','[EMAIL REMOVIDO]'],
                  ['Passaporte','passport','AA123456 (formato ICAO)','[PASSAPORTE REMOVIDO]'],
                ].map(([label,id,example,mask]) => (
                  <tr key={id as string} className="border-b border-slate-900">
                    <td className="py-2.5 pr-4 font-medium text-white">{label}</td>
                    <td className="py-2.5 pr-4 font-mono text-xs text-emerald-400">{id}</td>
                    <td className="py-2.5 pr-4 font-mono text-xs text-slate-400">{example}</td>
                    <td className="py-2.5 font-mono text-xs text-red-400">{mask}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Erros */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Códigos de Erro</h2>
          <div className="space-y-3">
            {[
              ['400','Bad Request','JSON inválido ou campo text ausente','{"error":"Missing required field: text"}'],
              ['401','Unauthorized','Chave ausente, inválida ou revogada','{"error":"Unauthorized. Get a free API key at guard.egos.ia.br"}'],
              ['429','Quota Exceeded','Cota mensal atingida (upgrade necessário)','{"error":"Monthly quota exceeded.","upgrade_url":"https://guard.egos.ia.br/landing#pricing"}'],
              ['429','Rate Limited','Mais de 100 req/min por chave','{"error":"Rate limit exceeded. Max 100 requests/minute."}'],
              ['500','Server Error','Erro interno — abra issue no GitHub','{"error":"Internal server error"}'],
            ].map(([code,name,desc,example],i) => (
              <div key={i} className="p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                <div className="flex items-center gap-3 mb-1">
                  <span className={`font-mono text-sm font-bold ${code.startsWith('4')?'text-amber-400':'text-red-400'}`}>{code}</span>
                  <span className="font-medium text-white">{name}</span>
                </div>
                <p className="text-sm text-slate-400 mb-2">{desc}</p>
                <code className="text-xs text-slate-500 font-mono">{example}</code>
              </div>
            ))}
          </div>
        </section>

        {/* Rate limits */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Planos e Rate Limits</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-left border-b border-slate-800">
                <th className="pb-3 text-slate-400 pr-6">Plano</th>
                <th className="pb-3 text-slate-400 pr-6">Chamadas/mês</th>
                <th className="pb-3 text-slate-400 pr-6">Rate limit</th>
                <th className="pb-3 text-slate-400 pr-6">Preço/chamada</th>
                <th className="pb-3 text-slate-400">Est. mensal</th>
              </tr></thead>
              <tbody className="text-slate-300">
                {[
                  ['Free','500','100/min','R$ 0,000','R$ 0'],
                  ['Startup','5.000','100/min','R$ 0,007','≈ R$ 35'],
                  ['Business','500.000','500/min','R$ 0,004','≈ R$ 2.000'],
                  ['Enterprise','Ilimitado','Negociável','R$ 0,002','Sob contrato'],
                ].map(([plan,calls,rate,price,est]) => (
                  <tr key={plan as string} className="border-b border-slate-900">
                    <td className="py-3 pr-6 font-medium">{plan}</td>
                    <td className="py-3 pr-6 font-mono text-xs text-emerald-400">{calls}</td>
                    <td className="py-3 pr-6 font-mono text-xs text-blue-400">{rate}</td>
                    <td className="py-3 pr-6 font-mono text-xs text-amber-400">{price}</td>
                    <td className="py-3 text-slate-400">{est}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Receipts */}
        <section>
          <h2 className="text-2xl font-bold mb-2">Receipts SHA-256 — Auditoria LGPD</h2>
          <p className="text-slate-400 mb-6">Cada inspeção gera três hashes imutáveis. Armazene <code className="text-emerald-400">inspectionHash</code> como prova para a ANPD.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {[
              ['inputHash','Hash do texto original','Prova que o texto foi recebido'],
              ['outputHash','Hash do texto mascarado','Prova do resultado'],
              ['inspectionHash','Hash combinado','← Armazene este no banco'],
            ].map(([field,title,desc]) => (
              <div key={field as string} className="p-4 bg-slate-900 rounded-xl border border-slate-800">
                <code className="text-emerald-400 text-xs font-mono">{field}</code>
                <p className="text-sm font-bold text-white mt-2">{title}</p>
                <p className="text-xs text-slate-400 mt-1">{desc}</p>
              </div>
            ))}
          </div>
          <CodeBlock lang="typescript" code={`// Como armazenar para conformidade LGPD
const result = guard.inspect(userMessage);

await db.auditLog.create({
  inspection_hash: result.receipt.inspectionHash,
  inspected_at:    result.receipt.inspectedAt,
  had_pii:         result.masking.findingCount > 0,
  pii_categories:  result.masking.findings.map(f => f.category),
});
// Prova para a ANPD: PII foi detectado e mascarado
// sem armazenar o texto original`} />
        </section>

        {/* LGPD */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Compliance LGPD (Lei 13.709/2018)</h2>
          <div className="space-y-3 mb-6">
            {[
              ['Art. 6','Minimização','Nome e email apenas para chave. Texto processado em memória e descartado.'],
              ['Art. 12','Anonimização','Hashes SHA-256 são irreversíveis — impossível reconstruir o texto original.'],
              ['Art. 46','Segurança','AES-256 em repouso, TLS 1.3 em trânsito, rate limiting por chave.'],
              ['Art. 18','Direitos','Solicite exclusão via enio@egos.ia.br — prazo de 15 dias úteis.'],
            ].map(([art,title,desc]) => (
              <div key={art as string} className="flex gap-4 p-4 bg-slate-900 border border-slate-800 rounded-xl">
                <span className="text-emerald-400 font-mono text-sm flex-shrink-0 w-14">{art}</span>
                <div><p className="font-bold text-white">{title}</p><p className="text-sm text-slate-400 mt-1">{desc}</p></div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA para integrações */}
        <div className="p-6 bg-emerald-900/20 border border-emerald-600/30 rounded-xl text-center">
          <h3 className="font-bold text-xl text-white mb-2">Pronto para integrar?</h3>
          <p className="text-slate-400 mb-4">Veja guias passo-a-passo para Node.js, Python, LangChain, OpenAI, FastAPI e mais.</p>
          <div className="flex justify-center gap-3">
            <Link href="/integrations" className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-xl transition text-sm">
              Ver todos os guias de integração →
            </Link>
            <Link href="/landing#get-key" className="px-5 py-2.5 border border-slate-700 hover:border-slate-600 text-slate-300 rounded-xl transition text-sm">
              Gerar chave gratuita
            </Link>
          </div>
        </div>

      </div>

      <footer className="border-t border-slate-800 py-8 text-center">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-3">
          <Link href="/landing" className="hover:text-white transition">Início</Link>
          <Link href="/integrations" className="hover:text-white transition">Integrações</Link>
          <Link href="/faq" className="hover:text-white transition">FAQ</Link>
          <Link href="/terms" className="hover:text-white transition">Termos</Link>
          <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
          <a href={`${API_URL}/openapi.json`} target="_blank" rel="noopener noreferrer" className="hover:text-white transition">OpenAPI JSON</a>
        </div>
        <p className="text-xs text-slate-600">Guard Brasil | @egosbr/guard-brasil | MIT License</p>
      </footer>
    </div>
  );
}
