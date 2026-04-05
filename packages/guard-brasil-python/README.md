# Guard Brasil Python SDK

Brazilian PII detection and LGPD compliance for Python.

Wraps the [Guard Brasil REST API](https://guard.egos.ia.br) — detects and masks CPF, CNPJ, RG, phone numbers, emails, addresses and other Brazilian PII before it leaves your server.

## Install

```bash
pip install egosbr-guard-brasil

# With integrations:
pip install "egosbr-guard-brasil[langchain]"
pip install "egosbr-guard-brasil[openai]"
pip install "egosbr-guard-brasil[anthropic]"
pip install "egosbr-guard-brasil[all]"
```

## Quick Start

```python
from guard_brasil import GuardBrasil

guard = GuardBrasil(api_key="gb_live_...")  # or set GUARD_BRASIL_API_KEY

result = guard.inspect("O cliente João, CPF 123.456.789-09, ligou ontem.")
print(result.output)      # "O cliente João, [CPF REMOVIDO], ligou ontem."
print(result.pii_found)   # ["cpf"]
print(result.has_pii)     # True
print(result.safe)        # False (PII was found)
print(result.summary)     # Human-readable description of findings
```

Get a free API key at [guard.egos.ia.br](https://guard.egos.ia.br).

## Environment Variable

```bash
export GUARD_BRASIL_API_KEY="gb_live_..."
```

```python
guard = GuardBrasil()  # picks up GUARD_BRASIL_API_KEY automatically
```

## Core API

### `guard.inspect(text)` → `GuardResult`

Full inspection — returns structured result with masked text, findings, and audit receipt.

```python
result = guard.inspect("CNPJ 12.345.678/0001-99 do fornecedor")

result.output          # masked text (safe to store/log)
result.safe            # bool — False if PII was found
result.blocked         # bool — True if output was blocked entirely
result.pii_found       # ["cnpj"]
result.findings        # list[PIIFinding] with .category, .label, .suggestion
result.receipt         # InspectionReceipt with audit hashes (LGPD evidence)
result.receipt.input_hash
result.receipt.output_hash
result.receipt.inspection_hash
result.receipt.guard_version
result.lgpd_disclosure # LGPD notice text (if applicable)
result.atrian_score    # ATRiAN ethical score (0-100)
result.duration_ms     # API latency
result.remaining_quota # API quota remaining
```

### `guard.mask(text)` → `str`

Shorthand — returns only the masked string.

```python
safe = guard.mask("RG 12.345.678-9 do solicitante")
# "RG [RG REMOVIDO] do solicitante"
```

### `guard.is_safe(text)` → `bool`

Returns `True` only if no PII was detected.

```python
if not guard.is_safe(user_input):
    raise ValueError("Input contains PII — please remove personal data.")
```

### Context Manager

```python
with GuardBrasil() as guard:
    result = guard.inspect("...")
# HTTP connection closed automatically
```

## Async Usage

```python
import asyncio
from guard_brasil import AsyncGuardBrasil

async def main():
    async with AsyncGuardBrasil() as guard:
        result = await guard.inspect("CPF 987.654.321-00")
        print(result.output)

    # Or manually:
    guard = AsyncGuardBrasil(api_key="gb_live_...")
    safe = await guard.mask("E-mail: joao@empresa.com.br")
    await guard._async_client.aclose()

asyncio.run(main())
```

## LangChain Integration

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from guard_brasil.integrations.langchain import create_guard_runnable

guard = create_guard_runnable()  # uses GUARD_BRASIL_API_KEY

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
])
llm = ChatOpenAI(model="gpt-4o-mini")

# Chain: prompt → LLM → guard (masks PII in LLM output before returning)
chain = prompt | llm | guard

response = chain.invoke({"input": "Summarize this: CPF 111.222.333-44..."})
# PII in the LLM's response is automatically masked
```

### Guard as pre-processing step (mask input before LLM sees it)

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

guard = create_guard_runnable()

# Mask user input BEFORE sending to LLM
chain = (
    RunnablePassthrough.assign(input=RunnableLambda(lambda x: guard.invoke(x["input"])))
    | prompt
    | llm
)
```

## OpenAI Integration

```python
from openai import OpenAI
from guard_brasil.integrations.openai import GuardedOpenAI

# Drop-in replacement — identical API, PII masked automatically
client = GuardedOpenAI(OpenAI())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "O CPF 123.456.789-09 é válido?"},
    ],
)
# CPF is masked before the request leaves your server
```

### Manual message masking

```python
from guard_brasil.integrations.openai import guard_openai_messages

messages = [{"role": "user", "content": "CNPJ 12.345.678/0001-99"}]
safe_messages = guard_openai_messages(messages)
response = openai_client.chat.completions.create(model="gpt-4o", messages=safe_messages)
```

## Anthropic Integration

```python
from anthropic import Anthropic
from guard_brasil.integrations.anthropic import GuardedAnthropic

client = GuardedAnthropic(Anthropic())

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Analise: RG 98.765.432-1, CPF 000.000.000-00"},
    ],
)
# Both PII items masked before reaching Anthropic
```

### Streaming

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Telefone: (11) 99999-9999"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## FastAPI Middleware

```python
from fastapi import FastAPI, Request, Response
from guard_brasil import GuardBrasil
import json

app = FastAPI()
guard = GuardBrasil()

@app.middleware("http")
async def guard_brasil_middleware(request: Request, call_next):
    """Mask PII in all incoming request bodies."""
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
        if body:
            try:
                data = json.loads(body)
                # Mask all string values at top level
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = guard.mask(value)
                body = json.dumps(data).encode()
            except (json.JSONDecodeError, Exception):
                pass  # Non-JSON body — skip masking

            # Rebuild request with masked body
            async def receive():
                return {"type": "http.request", "body": body}
            request = Request(request.scope, receive)

    return await call_next(request)

@app.post("/users")
async def create_user(data: dict):
    # PII already masked by middleware
    return {"status": "ok", "data": data}
```

## Django Middleware

```python
# myapp/middleware.py
import json
from guard_brasil import GuardBrasil

class GuardBrasilMiddleware:
    """Django middleware that masks Brazilian PII in POST request bodies."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.guard = GuardBrasil()

    def __call__(self, request):
        if request.method in ("POST", "PUT", "PATCH") and request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                masked = {
                    k: self.guard.mask(v) if isinstance(v, str) else v
                    for k, v in data.items()
                }
                request._body = json.dumps(masked).encode()
            except Exception:
                pass  # Don't break on parse errors

        return self.get_response(request)
```

```python
# settings.py
MIDDLEWARE = [
    "myapp.middleware.GuardBrasilMiddleware",
    # ... other middleware
]
```

## What Gets Detected

| PII Type | Example | Masked Output |
|----------|---------|---------------|
| CPF | `123.456.789-09` | `[CPF REMOVIDO]` |
| CNPJ | `12.345.678/0001-99` | `[CNPJ REMOVIDO]` |
| RG | `12.345.678-9` | `[RG REMOVIDO]` |
| Phone | `(11) 99999-9999` | `[TELEFONE REMOVIDO]` |
| Email | `joao@empresa.com` | `[EMAIL REMOVIDO]` |
| Full Name | `João da Silva` | `[NOME REMOVIDO]` |
| Address | `Rua das Flores, 123` | `[ENDEREÇO REMOVIDO]` |
| Bank | `Ag. 1234, CC 56789-0` | `[DADOS BANCÁRIOS REMOVIDOS]` |

## Error Handling

```python
import httpx
from guard_brasil import GuardBrasil

guard = GuardBrasil()

try:
    result = guard.inspect(user_input)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded — check your quota")
    elif e.response.status_code >= 500:
        print("Guard Brasil API error — using original text as fallback")
        result = None
except httpx.TimeoutException:
    print("Request timed out")
```

## LGPD Compliance

Every `inspect()` call returns a cryptographic `InspectionReceipt` you can store as evidence:

```python
result = guard.inspect(sensitive_text)

# Store receipt as LGPD evidence of due diligence
evidence = {
    "inspected_at": result.receipt.inspected_at,
    "input_hash": result.receipt.input_hash,
    "output_hash": result.receipt.output_hash,
    "inspection_hash": result.receipt.inspection_hash,
    "guard_version": result.receipt.guard_version,
    "pii_found": result.pii_found,
}
# Save to your audit log / database
```

## License

MIT — see [LICENSE](LICENSE)

## Links

- API: [guard.egos.ia.br](https://guard.egos.ia.br)
- Docs: [guard.egos.ia.br/docs](https://guard.egos.ia.br/docs)
- TypeScript SDK: [`@egosbr/guard-brasil`](https://www.npmjs.com/package/@egosbr/guard-brasil)
- Issues: [github.com/enioxt/egos](https://github.com/enioxt/egos)
