'use client';

import { useState } from 'react';
import Link from 'next/link';

type Tab = 'nodejs' | 'python' | 'langchain' | 'openai' | 'anthropic' | 'fastapi' | 'nextjs' | 'curl' | 'ai-agent';

const API_KEY_PLACEHOLDER = 'gb_live_SUA_CHAVE_AQUI';
const API_URL = 'https://guard.egos.ia.br';

const integrations: { id: Tab; label: string; icon: string; level: string; time: string }[] = [
  { id: 'curl',      label: 'cURL / REST',    icon: '🌐', level: 'Qualquer nível', time: '2 min' },
  { id: 'nodejs',    label: 'Node.js / TS',   icon: '🟨', level: 'Júnior',        time: '5 min' },
  { id: 'python',    label: 'Python',         icon: '🐍', level: 'Júnior',        time: '5 min' },
  { id: 'langchain', label: 'LangChain',      icon: '🔗', level: 'Júnior',        time: '5 min' },
  { id: 'openai',    label: 'OpenAI SDK',     icon: '🤖', level: 'Júnior',        time: '5 min' },
  { id: 'anthropic', label: 'Anthropic SDK',  icon: '🧠', level: 'Júnior',        time: '5 min' },
  { id: 'fastapi',   label: 'FastAPI',        icon: '⚡', level: 'Pleno',         time: '15 min' },
  { id: 'nextjs',    label: 'Next.js',        icon: '▲',  level: 'Pleno',         time: '15 min' },
  { id: 'ai-agent',  label: 'IA / Agentes',   icon: '🛸', level: 'IA',            time: '1 min'  },
];

const codes: Record<Tab, { title: string; description: string; steps: { label: string; code: string; lang: string }[] }> = {
  curl: {
    title: 'REST API — funciona em qualquer linguagem',
    description: 'Um POST. Qualquer linguagem que faz HTTP funciona. Tempo real de integração: 2 minutos.',
    steps: [
      {
        label: '1. Gere sua chave gratuita',
        lang: 'bash',
        code: `curl -X POST ${API_URL}/v1/keys \\
  -H "Content-Type: application/json" \\
  -d '{"name": "minha-empresa", "email": "dev@empresa.com.br"}'

# Resposta:
# {
#   "key": "gb_live_abc123...",
#   "tier": "free",
#   "quota_limit": 500,
#   "message": "Salve esta chave — ela não será mostrada novamente."
# }`,
      },
      {
        label: '2. Inspecione um texto',
        lang: 'bash',
        code: `curl -X POST ${API_URL}/v1/inspect \\
  -H "Authorization: Bearer ${API_KEY_PLACEHOLDER}" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "O cliente João, CPF 123.456.789-09, CNPJ 12.345.678/0001-95, ligou."}'

# Resposta:
# {
#   "safe": false,
#   "output": "O cliente João, CPF [CPF REMOVIDO], CNPJ [CNPJ REMOVIDO], ligou.",
#   "pii_found": ["cpf", "cnpj"],
#   "summary": "Issues found: PII: 2 finding(s) (critical)",
#   "lgpdDisclosure": "[LGPD] Dados pessoais detectados: CPF, CNPJ.",
#   "receipt": {
#     "inspectedAt": "2026-04-05T21:00:00.000Z",
#     "inputHash": "sha256...",
#     "outputHash": "sha256...",
#     "inspectionHash": "sha256..."
#   },
#   "atrian": { "score": 65 }
# }`,
      },
      {
        label: '3. Verifique sua cota',
        lang: 'bash',
        code: `curl ${API_URL}/v1/meta | jq '.pricing'
# Mostra todos os planos e o free_monthly_calls: 500`,
      },
    ],
  },

  nodejs: {
    title: 'Node.js / TypeScript — pacote npm oficial',
    description: '3 linhas. Sem servidor. Processa em memória — o texto nunca sai da sua aplicação.',
    steps: [
      {
        label: '1. Instalar',
        lang: 'bash',
        code: `npm install @egosbr/guard-brasil
# ou
bun add @egosbr/guard-brasil
# ou
yarn add @egosbr/guard-brasil`,
      },
      {
        label: '2. Uso básico (local, sem API key)',
        lang: 'typescript',
        code: `import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = GuardBrasil.create();
const result = guard.inspect('O CPF do cliente é 123.456.789-09');

console.log(result.output);
// "O CPF do cliente é [CPF REMOVIDO]"

console.log(result.safe);        // false
console.log(result.masking.findings[0].category); // "cpf"
console.log(result.atrian.score); // score ético 0-100
console.log(result.receipt.inspectionHash); // SHA-256 para auditoria`,
      },
      {
        label: '3. Middleware Express — sanitiza logs automaticamente',
        lang: 'typescript',
        code: `import express from 'express';
import { GuardBrasil } from '@egosbr/guard-brasil';

const app = express();
const guard = GuardBrasil.create();

// Intercepta TODOS os requests — mascara PII antes de qualquer log
app.use((req, res, next) => {
  const body = JSON.stringify(req.body ?? {});
  const safe = guard.inspect(body);
  req.safeBody = safe.output;   // use para logs
  // req.body segue intacto para os handlers
  next();
});

app.post('/api/chat', (req, res) => {
  console.log('body (seguro para log):', req.safeBody);
  // ... processar sem expor PII nos logs
});`,
      },
      {
        label: '4. Configuração avançada',
        lang: 'typescript',
        code: `import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = GuardBrasil.create({
  blockOnCriticalPII: true,     // bloqueia se CPF/CNPJ encontrado
  lgpdDisclosure: true,          // inclui aviso LGPD na resposta
  atrian: { enabled: true },    // habilita scoring ético
});

const result = guard.inspect(texto);

if (result.blocked) {
  return res.status(422).json({
    error: 'Dados pessoais detectados',
    categories: result.masking.findings.map(f => f.label),
  });
}`,
      },
    ],
  },

  python: {
    title: 'Python — SDK oficial via REST',
    description: 'Funciona com FastAPI, Django, scripts de ML, LangChain, qualquer código Python.',
    steps: [
      {
        label: '1. Instalar',
        lang: 'bash',
        code: `pip install egosbr-guard-brasil

# Com extras para LangChain ou OpenAI:
pip install "egosbr-guard-brasil[langchain]"
pip install "egosbr-guard-brasil[openai]"
pip install "egosbr-guard-brasil[all]"`,
      },
      {
        label: '2. Uso básico',
        lang: 'python',
        code: `from guard_brasil import GuardBrasil

guard = GuardBrasil(api_key="gb_live_...")
# ou via variável de ambiente: GUARD_BRASIL_API_KEY

result = guard.inspect("O CPF 123.456.789-09 do paciente João")

print(result.output)       # "O CPF [CPF REMOVIDO] do paciente João"
print(result.has_pii)      # True
print(result.pii_found)    # ["cpf"]
print(result.atrian_score) # 65

# Shorthand para só o texto mascarado:
safe_text = guard.mask("CPF 123.456.789-09")`,
      },
      {
        label: '3. Uso assíncrono (asyncio / FastAPI)',
        lang: 'python',
        code: `from guard_brasil import AsyncGuardBrasil
import asyncio

async def main():
    async with AsyncGuardBrasil(api_key="gb_live_...") as guard:
        result = await guard.inspect("CPF 123.456.789-09")
        print(result.output)

asyncio.run(main())`,
      },
      {
        label: '4. Context manager',
        lang: 'python',
        code: `from guard_brasil import GuardBrasil

with GuardBrasil(api_key="gb_live_...") as guard:
    for text in textos_para_processar:
        result = guard.inspect(text)
        salvar_no_banco(result.output, result.receipt.inspection_hash)`,
      },
    ],
  },

  langchain: {
    title: 'LangChain — proteção automática de PII em agentes',
    description: 'Guard Brasil como middleware no pipeline LangChain. O LLM nunca vê o CPF.',
    steps: [
      {
        label: '1. Instalar (JS/TS)',
        lang: 'bash',
        code: `npm install @egosbr/guard-brasil-langchain @egosbr/guard-brasil`,
      },
      {
        label: '2. Como Runnable — pipe antes do LLM',
        lang: 'typescript',
        code: `import { GuardBrasilRunnable } from '@egosbr/guard-brasil-langchain';
import { ChatOpenAI } from '@langchain/openai';
import { StringOutputParser } from '@langchain/core/output_parsers';

const guard = new GuardBrasilRunnable({
  onPIIDetected: (categories, text) => {
    console.warn('PII detectado antes do LLM:', categories);
  }
});

const llm = new ChatOpenAI({ modelName: 'gpt-4o' });

// Pipeline: Guard Brasil → LLM → Parser
const chain = guard.pipe(llm).pipe(new StringOutputParser());

const response = await chain.invoke(
  'O cliente com CPF 123.456.789-09 pergunta sobre seu saldo'
);
// O LLM recebeu: "O cliente com CPF [CPF REMOVIDO] pergunta sobre seu saldo"`,
      },
      {
        label: '3. Como piiMiddleware (compatível com interface LangChain)',
        lang: 'typescript',
        code: `import { createGuardRedact } from '@egosbr/guard-brasil-langchain';
import { piiMiddleware } from '@langchain/core/middleware';

const redact = createGuardRedact({
  onPIIDetected: (categories) => {
    // log, alertar, auditar
    console.log('PII bloqueado:', categories);
  }
});

// Funciona com qualquer chain LangChain
const safeChain = piiMiddleware({ redact })(meuChain);`,
      },
      {
        label: '4. Python + LangChain',
        lang: 'python',
        code: `from guard_brasil.integrations.langchain import create_guard_runnable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

guard_runnable = create_guard_runnable(api_key="gb_live_...")
llm = ChatOpenAI(model="gpt-4o")

# Pipeline: Guard Brasil → LLM
chain = guard_runnable | llm | StrOutputParser()

response = chain.invoke("CPF 123.456.789-09 precisa de atendimento")
# LLM recebeu texto sem CPF`,
      },
    ],
  },

  openai: {
    title: 'OpenAI SDK — wrapper que mascara mensagens automaticamente',
    description: 'Envolve o cliente OpenAI. Qualquer chamada passa pelo Guard Brasil primeiro. Zero mudanças no resto do código.',
    steps: [
      {
        label: '1. TypeScript — guardOpenAI()',
        lang: 'typescript',
        code: `import OpenAI from 'openai';
import { guardOpenAI } from '@egosbr/guard-brasil-langchain';

// Substitua 'new OpenAI()' por 'guardOpenAI(new OpenAI())'
const openai = guardOpenAI(new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
}));

// A partir daqui: código igual ao normal
// Mas CPF/CNPJ/RG são mascarados ANTES de sair para a OpenAI
const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    {
      role: 'user',
      content: 'O cliente João, CPF 123.456.789-09, tem dúvidas sobre sua conta'
      // → enviado como: '...CPF [CPF REMOVIDO]...'
    }
  ]
});`,
      },
      {
        label: '2. Python — GuardedOpenAI',
        lang: 'python',
        code: `from openai import OpenAI
from guard_brasil.integrations.openai import GuardedOpenAI

# Substitua OpenAI() por GuardedOpenAI(OpenAI())
client = GuardedOpenAI(
    OpenAI(api_key="sk-..."),
    guard_api_key="gb_live_..."
)

# Código normal a partir daqui — PII mascarado automaticamente
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "CPF 123.456.789-09 do cliente..."}]
)`,
      },
      {
        label: '3. Sanitizar mensagens avulsas',
        lang: 'python',
        code: `from guard_brasil.integrations.openai import guard_openai_messages

mensagens = [
    {"role": "system", "content": "Você é um assistente."},
    {"role": "user",   "content": "Meu CPF é 123.456.789-09 e tenho uma dúvida..."},
]

# Mascara PII em todas as mensagens
mensagens_seguras = guard_openai_messages(mensagens, api_key="gb_live_...")

# Agora pode enviar para qualquer LLM
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=mensagens_seguras
)`,
      },
    ],
  },

  anthropic: {
    title: 'Anthropic / Claude — proteção automática de PII',
    description: 'Mesmo padrão do OpenAI. Wrap do cliente Anthropic — zero mudanças no restante do código.',
    steps: [
      {
        label: '1. TypeScript — guardAnthropic()',
        lang: 'typescript',
        code: `import Anthropic from '@anthropic-ai/sdk';
import { guardAnthropic } from '@egosbr/guard-brasil-langchain';

// Envolve o cliente Anthropic
const claude = guardAnthropic(new Anthropic());

// Código normal — PII mascarado antes de sair
const msg = await claude.messages.create({
  model: 'claude-opus-4-6',
  max_tokens: 1024,
  messages: [
    {
      role: 'user',
      content: 'O CPF 123.456.789-09 do paciente João está correto?'
      // → Claude recebe: '...CPF [CPF REMOVIDO]...'
    }
  ]
});`,
      },
      {
        label: '2. Python — via API REST direta',
        lang: 'python',
        code: `import anthropic
from guard_brasil import GuardBrasil

guard = GuardBrasil(api_key="gb_live_...")
client = anthropic.Anthropic(api_key="sk-ant-...")

def safe_claude(user_message: str) -> str:
    """Envia mensagem para Claude com PII mascarado."""
    safe_message = guard.mask(user_message)

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": safe_message}]
    )
    return message.content[0].text

# Uso:
response = safe_claude("O paciente João, CPF 123.456.789-09, tem febre.")`,
      },
    ],
  },

  fastapi: {
    title: 'FastAPI — middleware de proteção para toda a API',
    description: 'Middleware que intercepta todos os requests. PII nunca aparece nos logs do servidor.',
    steps: [
      {
        label: '1. Middleware global (protege toda a aplicação)',
        lang: 'python',
        code: `from fastapi import FastAPI, Request
from fastapi.middleware.base import BaseHTTPMiddleware
from guard_brasil import AsyncGuardBrasil
import json

app = FastAPI()
guard = AsyncGuardBrasil(api_key="gb_live_...")

class GuardBrasilMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Sanitiza o body antes de processar (para logs seguros)
        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if body:
                try:
                    body_text = body.decode("utf-8")
                    result = await guard.inspect(body_text)
                    # Armazena versão segura para logging
                    request.state.safe_body = result.output
                    request.state.pii_found = result.pii_found
                except Exception:
                    pass

        response = await call_next(request)
        return response

app.add_middleware(GuardBrasilMiddleware)

@app.post("/chat")
async def chat(request: Request, body: dict):
    # Log seguro — sem PII
    safe = getattr(request.state, "safe_body", str(body))
    print(f"Request recebido: {safe}")

    # Processa normalmente com body original
    return {"response": "ok"}`,
      },
      {
        label: '2. Dependência por endpoint',
        lang: 'python',
        code: `from fastapi import FastAPI, Depends
from guard_brasil import GuardBrasil
from pydantic import BaseModel

app = FastAPI()
guard = GuardBrasil(api_key="gb_live_...")

class TextInput(BaseModel):
    text: str

def get_safe_text(body: TextInput) -> str:
    """Dependência FastAPI — retorna texto mascarado."""
    return guard.mask(body.text)

@app.post("/analyze")
async def analyze(safe_text: str = Depends(get_safe_text)):
    # safe_text já tem CPF/CNPJ mascarados
    # envie para qualquer LLM sem risco
    return {"safe_text": safe_text}`,
      },
      {
        label: '3. Rota de inspeção explícita',
        lang: 'python',
        code: `from fastapi import FastAPI, Header
from guard_brasil import GuardBrasil
from pydantic import BaseModel

app = FastAPI()

class InspectRequest(BaseModel):
    text: str

@app.post("/v1/guard/inspect")
async def inspect_text(
    body: InspectRequest,
    authorization: str = Header(...),
):
    api_key = authorization.replace("Bearer ", "")
    guard = GuardBrasil(api_key=api_key)
    result = guard.inspect(body.text)

    return {
        "safe": result.safe,
        "output": result.output,
        "pii_found": result.pii_found,
        "receipt_hash": result.receipt.inspection_hash if result.receipt else None,
    }`,
      },
    ],
  },

  nextjs: {
    title: 'Next.js — proteção de API routes e Server Components',
    description: 'Middleware de rota, API handler, e Server Actions com Guard Brasil.',
    steps: [
      {
        label: '1. middleware.ts — intercepta toda a aplicação',
        lang: 'typescript',
        code: `// middleware.ts (raiz do projeto Next.js)
import { NextRequest, NextResponse } from 'next/server';
import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = GuardBrasil.create();

export function middleware(request: NextRequest) {
  // Só inspeciona POST/PUT com body
  if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
    // Loga de forma segura — sem PII
    const url = request.nextUrl.pathname;
    console.log(\`[\${new Date().toISOString()}] \${request.method} \${url}\`);
  }
  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};`,
      },
      {
        label: '2. API Route — inspeção antes do LLM',
        lang: 'typescript',
        code: `// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { GuardBrasil } from '@egosbr/guard-brasil';
import OpenAI from 'openai';

const guard = GuardBrasil.create();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  // 1. Inspeciona antes de enviar ao LLM
  const inspection = guard.inspect(message);

  if (inspection.masking.findingCount > 0) {
    console.log('PII detectado:', inspection.masking.findings.map(f => f.label));
  }

  // 2. Envia texto limpo para o LLM
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: inspection.output }],
  });

  return NextResponse.json({
    response: completion.choices[0].message.content,
    receipt: inspection.receipt?.inspectionHash,
    pii_masked: inspection.masking.findingCount,
  });
}`,
      },
      {
        label: '3. Server Action — formulário com dados pessoais',
        lang: 'typescript',
        code: `// app/actions.ts
'use server';
import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = GuardBrasil.create();

export async function submitForm(formData: FormData) {
  const text = formData.get('message') as string;

  // Mascara PII antes de salvar no banco
  const result = guard.inspect(text);

  await db.messages.create({
    content: result.output,           // texto mascarado
    audit_hash: result.receipt?.inspectionHash, // prova LGPD
    had_pii: result.masking.findingCount > 0,
  });
}`,
      },
    ],
  },

  'ai-agent': {
    title: 'Para Agentes de IA — configure Guard Brasil via prompt',
    description: 'Copie este prompt para qualquer IA (Claude, GPT-4, Gemini) e ela configurará Guard Brasil no seu projeto automaticamente.',
    steps: [
      {
        label: '🛸 Prompt para IA — integração completa automática',
        lang: 'text',
        code: `Preciso integrar o Guard Brasil no meu projeto para compliance LGPD.

## Contexto do meu projeto:
- Linguagem: [Node.js / Python / outro]
- Framework: [Express / FastAPI / Next.js / outro]
- Uso de LLM: [OpenAI / Anthropic / LangChain / nenhum]
- Tenho a chave: gb_live_MINHA_CHAVE

## O que preciso:
1. Instalar o pacote correto
2. Configurar como middleware para que PII seja mascarado antes de qualquer log
3. Integrar com meu cliente de LLM para mascarar antes de enviar prompts
4. Salvar o receipt SHA-256 de cada inspeção no banco de dados

## Documentação da API:
- Endpoint: POST https://guard.egos.ia.br/v1/inspect
- Auth: Authorization: Bearer gb_live_MINHA_CHAVE
- Body: { "text": "texto a inspecionar" }
- Resposta inclui: output (mascarado), pii_found, receipt.inspectionHash, atrian.score

## npm: @egosbr/guard-brasil (local) | API REST (qualquer linguagem)

Por favor:
1. Instale e configure o Guard Brasil no meu projeto
2. Adicione o middleware de sanitização de logs
3. Integre com meu cliente LLM
4. Mostre como armazenar os receipts para auditoria LGPD`,
      },
      {
        label: '🤖 Prompt para MCP / Claude Code',
        lang: 'text',
        code: `Integre Guard Brasil na aplicação em [CAMINHO_DO_PROJETO]:

1. npm install @egosbr/guard-brasil
2. Crie src/guard.ts com singleton do GuardBrasil
3. Adicione middleware no servidor principal que inspeciona todo request POST
4. Envolva todas as chamadas para OpenAI/Anthropic com guard.inspect() antes de enviar
5. Adicione campo audit_hash na tabela de mensagens do banco de dados
6. Configure a variável GUARD_BRASIL_API_KEY no .env

API key: [MINHA_CHAVE]
Documentação: https://guard.egos.ia.br/docs`,
      },
      {
        label: '⚙️ Variáveis de ambiente necessárias',
        lang: 'bash',
        code: `# .env
GUARD_BRASIL_API_KEY=gb_live_SUA_CHAVE_AQUI

# Opcional — para uso direto da API REST em Python/Ruby/Go/etc:
GUARD_BRASIL_URL=https://guard.egos.ia.br
GUARD_BRASIL_TIMEOUT=10000`,
      },
      {
        label: '📋 Checklist de integração completa',
        lang: 'text',
        code: `[ ] 1. Chave de API gerada (guard.egos.ia.br → "Gerar chave gratuita")
[ ] 2. GUARD_BRASIL_API_KEY no .env (nunca no código)
[ ] 3. Middleware de sanitização de logs configurado
[ ] 4. Chamadas ao LLM passam por guard.inspect() primeiro
[ ] 5. Receipts SHA-256 armazenados no banco (campo audit_hash)
[ ] 6. Logs não contêm mais CPF/CNPJ/RG
[ ] 7. Testado com: "O CPF 123.456.789-09 do cliente..."
[ ] 8. Resposta esperada: "...CPF [CPF REMOVIDO]..."
[ ] 9. Documentado no README do projeto para o time`,
      },
    ],
  },
};

export default function IntegrationsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('curl');
  const [copied, setCopied] = useState<string | null>(null);

  function copy(text: string, id: string) {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  }

  const current = codes[activeTab];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/landing" className="text-emerald-400 font-bold text-lg hover:text-emerald-300 transition">
            Guard Brasil
          </Link>
          <nav className="flex gap-6 text-sm text-slate-400">
            <Link href="/docs" className="hover:text-white transition">API Docs</Link>
            <Link href="/faq" className="hover:text-white transition">FAQ</Link>
            <Link href="/landing#get-key" className="text-emerald-400 hover:text-emerald-300 transition font-medium">
              Chave grátis →
            </Link>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-3">Integrações</h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Guard Brasil funciona com qualquer stack. Escolha sua linguagem e siga os passos.
            Tempo médio de integração: <span className="text-emerald-400 font-medium">5 minutos</span>.
          </p>

          {/* Stats */}
          <div className="flex gap-8 mt-6">
            <div>
              <p className="text-2xl font-bold text-emerald-400">3 linhas</p>
              <p className="text-xs text-slate-500">integração mínima npm</p>
            </div>
            <div className="w-px bg-slate-800" />
            <div>
              <p className="text-2xl font-bold text-emerald-400">1 chamada</p>
              <p className="text-xs text-slate-500">integração REST</p>
            </div>
            <div className="w-px bg-slate-800" />
            <div>
              <p className="text-2xl font-bold text-emerald-400">500/mês</p>
              <p className="text-xs text-slate-500">grátis para começar</p>
            </div>
            <div className="w-px bg-slate-800" />
            <div>
              <p className="text-2xl font-bold text-emerald-400">SHA-256</p>
              <p className="text-xs text-slate-500">receipt por inspeção</p>
            </div>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="w-52 flex-shrink-0">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">Stack</p>
            <nav className="space-y-1">
              {integrations.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg transition text-sm ${
                    activeTab === item.id
                      ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                  <div className="flex gap-1 mt-1">
                    <span className="text-[10px] text-slate-600">{item.level}</span>
                    <span className="text-[10px] text-slate-700">·</span>
                    <span className="text-[10px] text-slate-600">{item.time}</span>
                  </div>
                </button>
              ))}
            </nav>

            <div className="mt-8 p-3 bg-slate-900 rounded-lg border border-slate-800">
              <p className="text-xs font-bold text-white mb-1">PII detectados</p>
              <ul className="text-[11px] text-slate-400 space-y-0.5">
                {['CPF', 'CNPJ', 'RG', 'CNH', 'SUS', 'CEP', 'Placa', 'MASP', 'REDS', 'Processo Judicial', 'Título Eleitor', 'NIS/PIS', 'Telefone', 'Email', 'Passaporte'].map(p => (
                  <li key={p} className="flex items-center gap-1">
                    <span className="text-emerald-500">✓</span> {p}
                  </li>
                ))}
              </ul>
            </div>
          </aside>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-2">{current.title}</h2>
              <p className="text-slate-400">{current.description}</p>
            </div>

            <div className="space-y-6">
              {current.steps.map((step, i) => (
                <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800">
                    <span className="text-sm font-medium text-slate-300">{step.label}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-600 font-mono">{step.lang}</span>
                      <button
                        onClick={() => copy(step.code, `${activeTab}-${i}`)}
                        className="text-xs text-slate-500 hover:text-emerald-400 transition px-2 py-1 rounded border border-slate-700 hover:border-emerald-600/50"
                      >
                        {copied === `${activeTab}-${i}` ? '✓ copiado' : 'copiar'}
                      </button>
                    </div>
                  </div>
                  <pre className="p-4 text-sm font-mono text-slate-300 overflow-x-auto leading-relaxed whitespace-pre-wrap">
                    <code>{step.code}</code>
                  </pre>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="mt-10 p-6 bg-emerald-900/20 border border-emerald-600/30 rounded-xl">
              <h3 className="font-bold text-white mb-1">Pronto para integrar?</h3>
              <p className="text-sm text-slate-400 mb-4">
                500 inspeções grátis por mês. Sem cartão de crédito. Chave gerada em segundos.
              </p>
              <div className="flex gap-3">
                <Link
                  href="/landing#get-key"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition"
                >
                  Gerar chave gratuita
                </Link>
                <Link
                  href="/docs"
                  className="px-4 py-2 border border-slate-700 hover:border-slate-600 text-slate-300 text-sm rounded-lg transition"
                >
                  Documentação completa da API →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800 py-8 text-center mt-16">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-4">
          <Link href="/landing" className="hover:text-white transition">Início</Link>
          <Link href="/docs" className="hover:text-white transition">API Docs</Link>
          <Link href="/faq" className="hover:text-white transition">FAQ</Link>
          <Link href="/terms" className="hover:text-white transition">Termos</Link>
          <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
        </div>
        <p className="text-xs text-slate-600">Guard Brasil | @egosbr/guard-brasil | MIT License</p>
      </footer>
    </div>
  );
}
