# Guard Brasil — Demo Script (30 minutos)

> **Para:** CTOs / gestores de TI em govtech, delegacias, tribunais, prefeituras
> **Objetivo:** Mostrar o problema real → solução ao vivo → path para contrato
> **Duração:** 30 min (15 demo + 10 Q&A + 5 próximos passos)

---

## Abertura (2 min)

> "Vou te mostrar algo que provavelmente está acontecendo hoje no sistema de vocês, sem que ninguém perceba."

Abra um terminal. Mostre a API **sem proteção** primeiro:

```bash
# SEM Guard Brasil — IA vaza dados
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{
      "role": "user",
      "content": "Resuma esse relatório: O suspeito João Silva, CPF 123.456.789-00, RG 12.345.678-9, foi abordado..."
    }]
  }' | jq '.choices[0].message.content'
```

**O que acontece:** O resumo da OpenAI contém o CPF e RG no output. Esse output vai para o log, para a interface, possivelmente para o histórico de treinamento da OpenAI.

> "Isso é uma violação da LGPD. O órgão é responsável."

---

## Demo 1 — API ao Vivo (5 min)

```bash
# Com Guard Brasil — dados protegidos automaticamente
API_KEY="9e573724-8f4f-45bb-a946-af7d4d2c324f"

curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "text": "O suspeito João Silva, CPF 123.456.789-00, RG 12.345.678-9, condutor da placa ABC-1234, foi abordado na Av. Paulista."
  }' | python3 -m json.tool
```

**Mostre no output:**
- `"safe": false` — detectou PII
- `"output"` — CPF, RG e placa mascarados
- `"masking.sensitivityLevel": "critical"`
- `"lgpdDisclosure"` — gerado automaticamente
- `"meta.durationMs": 4` — 4ms de overhead

> "Isso é colocado na frente da IA antes de qualquer processamento. O modelo nunca vê os dados reais."

---

## Demo 2 — Cenário govtech (5 min)

```bash
# Cenário: delegacia usando IA para resumir BOs
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "text": "BO 2024/001234-MASP: Vítima Maria Costa, RG 98.765.432-1, registrou ocorrência de furto. REDS: 2024-0123456789. Processo: 1234567-89.2024.8.26.0100",
    "sessionId": "demo-delegacia-001"
  }' | python3 -m json.tool
```

**Destaque:**
- MASP detectado e mascarado
- REDS detectado e mascarado
- Número de processo detectado
- `evidenceChain.auditHash` — trilha de auditoria imutável

> "Cada resposta gera um hash. Se houver auditoria da CGU ou MPF, vocês têm prova de que os dados foram protegidos."

---

## Demo 3 — SDK Python (3 min)

> "Para quem tem sistema legado em Python:"

```python
import httpx

GUARD_API = "https://guard.egos.ia.br/v1/inspect"
API_KEY = "9e573724-8f4f-45bb-a946-af7d4d2c324f"

def safe_ai_call(text: str) -> str:
    # 1. Guard Brasil inspeciona
    r = httpx.post(GUARD_API,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"text": text})
    result = r.json()

    if not result["safe"]:
        # 2. Usa output mascarado para a IA
        text = result["output"]

    # 3. Chama a IA com texto já limpo
    # ... sua chamada para OpenAI / Ollama / etc
    return text

# Teste
print(safe_ai_call("CPF do autuado: 111.222.333-44"))
# Output: "CPF do autuado: [CPF REMOVIDO]"
```

---

## Perguntas frequentes (prep)

**"Isso não atrasa o sistema?"**
> "4ms. Menos do que o ping da rede interna. Imperceptível."

**"Precisamos instalar alguma coisa?"**
> "Não. É uma chamada HTTP. Se vocês já chamam OpenAI ou qualquer API, a integração é idêntica."

**"E se tivermos dados on-premise que não podem sair?"**
> "Temos plano Enterprise com deploy local. O SDK open source roda offline, sem chamada de rede."

**"Quem usa isso hoje?"**
> "Lançamento em 2026. Você seria um dos primeiros clientes — preço Starter por tempo limitado."

**"E o ATRiAN score?"**
> "É uma avaliação ética da resposta — detecta viés, linguagem discriminatória, afirmações não fundamentadas. Score 0-100. Violações são categorizadas por taxonomia."

---

## Fechamento (5 min)

**Proposta concreta:**

> "Vou propor um piloto de 30 dias. Vocês colocam Guard Brasil na frente de um fluxo — pode ser o menor que tiver. Medimos: (1) quantos dados sensíveis foram interceptados, (2) qual seria o risco LGPD sem proteção. Custo: R$ 99/mês no Starter. Se não funcionar, cancela."

**Próximos passos:**
1. Compartilha um exemplo de texto que vocês processam hoje
2. Eu crio um teste específico para o caso de vocês (< 24h)
3. Assina Starter, integra em 1 dia, piloto por 30 dias

---

**Contato pós-demo:**
```
Para: enio@egos.ia.br
Assunto: Guard Brasil — [Nome do Órgão] — Piloto

Olá,
Tivemos a demo hoje. Gostaríamos de avançar com o piloto de 30 dias.
[Descreva brevemente o fluxo que querem proteger]
```

---

> API Key para demos: `9e573724-8f4f-45bb-a946-af7d4d2c324f` (100 req/min)
> Endpoint: `https://guard.egos.ia.br/v1/inspect`
