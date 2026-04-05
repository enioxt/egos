# @egosbr/guard-brasil-langchain

Guard Brasil middleware for LangChain — Brazilian PII masking for AI agents.

Automatically masks CPF, CNPJ, RG, CNH, MASP, REDS, phone numbers, emails, CEP, and other Brazilian PII before text reaches any LLM. LGPD-compliant.

## Installation

```bash
npm install @egosbr/guard-brasil-langchain @egosbr/guard-brasil
```

## Usage

### 1. `createGuardRedact` — LangChain piiMiddleware

Drop-in for LangChain's `piiMiddleware`. Returns a `redact(text) => string` function.

```typescript
import { piiMiddleware } from 'langchain'
import { createGuardRedact } from '@egosbr/guard-brasil-langchain'

const chain = new LLMChain({
  llm: model,
  middlewares: [
    piiMiddleware({ redact: createGuardRedact() })
  ]
})

// With callbacks
const redact = createGuardRedact({
  onPIIDetected: (categories, original) => {
    console.warn('PII detected:', categories)
    auditLog.write({ categories, ts: Date.now() })
  }
})

// Throw instead of masking
const strictRedact = createGuardRedact({ throwOnPII: true })
```

### 2. `GuardBrasilRunnable` — pipeable Runnable

Use `.pipe()` to prepend Guard Brasil to any LangChain chain.

```typescript
import { GuardBrasilRunnable } from '@egosbr/guard-brasil-langchain'
import { ChatOpenAI } from '@langchain/openai'

const chain = new GuardBrasilRunnable({
  onPIIDetected: (categories) => console.warn('Masked PII:', categories)
}).pipe(new ChatOpenAI({ modelName: 'gpt-4o' }))

const result = await chain.invoke('O CPF do cliente é 123.456.789-09')
// CPF is masked before reaching OpenAI
```

### 3. `guardOpenAI` — OpenAI SDK proxy

Wraps the OpenAI client with a transparent Proxy. All `chat.completions.create` calls automatically mask PII in message content.

```typescript
import OpenAI from 'openai'
import { guardOpenAI } from '@egosbr/guard-brasil-langchain'

const openai = guardOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }))

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'user', content: 'O CPF 123.456.789-09 do cliente João...' }
  ]
})
// The CPF is masked to [CPF REMOVIDO] before the request leaves your server
```

### 4. `guardAnthropic` — Anthropic SDK proxy

Same pattern for the Anthropic SDK.

```typescript
import Anthropic from '@anthropic-ai/sdk'
import { guardAnthropic } from '@egosbr/guard-brasil-langchain'

const claude = guardAnthropic(new Anthropic())

const msg = await claude.messages.create({
  model: 'claude-opus-4-6',
  max_tokens: 1024,
  messages: [
    { role: 'user', content: 'O CNPJ da empresa é 12.345.678/0001-90' }
  ]
})
// CNPJ is masked before the request reaches Anthropic's API
```

## Configuration

```typescript
interface GuardMiddlewareOptions {
  config?: {
    blockOnCriticalPII?: boolean  // block entirely instead of masking (default: false)
    lgpdDisclosure?: boolean       // add LGPD footer to output (default: true)
  }
  throwOnPII?: boolean             // throw Error when PII found (default: false)
  onPIIDetected?: (categories: string[], originalText: string) => void
}
```

## PII Categories Detected

| Category | Example |
|----------|---------|
| `cpf` | 123.456.789-09 |
| `cnpj` | 12.345.678/0001-90 |
| `rg` | 12.345.678-9 |
| `cnh` | 12345678901 |
| `masp` | 1234567-8 |
| `email` | joao@exemplo.com.br |
| `phone` | (11) 99999-9999 |
| `cep` | 01310-100 |
| `plate` | ABC-1234 / ABC1D23 |
| `process_number` | 0001234-56.2024.8.26.0100 |

## License

MIT — EGOS / Guard Brasil
