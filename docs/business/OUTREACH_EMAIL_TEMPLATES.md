# Guard Brasil — Templates de Email para Outreach (M-007)

> **Criado:** 2026-04-04 | **Status:** PRONTO PARA ENVIAR | **Meta:** 5 emails esta semana

---

## Email 1: Cold Intro — Compliance Officer / DPO

**Para:** Responsável LGPD de empresas SaaS BR
**Subject:** Proteção de dados brasileiros em 4 linhas de código

Olá [Nome],

Vi que a [Empresa] processa dados de clientes brasileiros. Uma pergunta rápida: como vocês mascaram CPFs e CNPJs antes de enviar para seus modelos de IA?

Criamos o **Guard Brasil** — uma API que detecta e mascara 15 tipos de PII brasileiro (CPF, CNPJ, RG, CNH, etc.) em tempo real. Uma chamada REST, 4ms de latência, compliance LGPD automático.

**Funciona assim:**
```
curl -X POST guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer SUA_CHAVE" \
  -d '{"text": "O CPF 123.456.789-00 do João..."}'
```

Resposta: texto mascarado + relatório de compliance + receipt hash.

500 chamadas/mês grátis. Posso gerar uma chave de teste para vocês agora?

— Enio Rocha | EGOS | guard.egos.ia.br

---

## Email 2: Pain Point — Startup que usa IA

**Para:** CTO/tech lead de startups que integram LLMs
**Subject:** Seus prompts vazam CPFs para a OpenAI?

[Nome],

Se vocês mandam texto de usuários brasileiros para qualquer LLM (ChatGPT, Claude, Gemini), provavelmente estão enviando CPFs, RGs e telefones sem saber.

O **Guard Brasil** resolve isso em uma chamada de API:
- Detecta 15 tipos de PII brasileiro automaticamente
- Mascara antes de enviar ao LLM
- Devolve o texto limpo + receipt de compliance
- R$0.007/chamada (500 grátis/mês)

Já estamos live em produção: guard.egos.ia.br/v1/meta

Quer testar com dados reais do seu produto? Gero uma key em 10 segundos.

— Enio Rocha | guard.egos.ia.br

---

## Email 3: Regulatório — Empresa grande

**Para:** Head of Legal / Compliance de empresas enterprise
**Subject:** LGPD + IA: como garantir compliance automático nas APIs

Prezado(a) [Nome],

Com a ANPD intensificando fiscalizações em 2026, empresas que processam dados pessoais via IA precisam comprovar que mascaramento ocorre ANTES do processamento.

O **Guard Brasil** é uma camada de segurança que se integra entre seu sistema e qualquer API de IA:

- **15 padrões PII brasileiros** detectados (CPF, CNPJ, RG, CNH, SUS, NIS, CEP, placas...)
- **Receipt com hash SHA-256** — prova auditável de compliance por chamada
- **Validação ética ATRiAN** — scoring de conteúdo sensível (0-100)
- **SLA enterprise**: <5ms latência, 99.9% uptime

Preços sob demanda: R$0.002/chamada no volume enterprise.
Documentação completa: guard.egos.ia.br/openapi.json

Podemos agendar 15 min para demonstração?

— Enio Rocha | EGOS | guard.egos.ia.br

---

## Email 4: Developer Evangelist — Comunidade dev

**Para:** Devs influentes, tech bloggers, community leads
**Subject:** Open source: detecção de PII brasileiro em tempo real

Ei [Nome],

Lancei o `@egosbr/guard-brasil` no npm — detecção de PII brasileiro com 85.3% F1 score (melhor que Presidio para dados BR).

```
npm install @egosbr/guard-brasil
```

15 padrões: CPF, CNPJ, RG, CNH, SUS, NIS, CEP, placas, processos judiciais...

API REST grátis (500/mês): guard.egos.ia.br
OpenAPI spec: guard.egos.ia.br/openapi.json
npm: npmjs.com/package/@egosbr/guard-brasil

Se você escrever/publicar sobre proteção de dados em IA, posso dar acesso Pro ilimitado em troca de um review honesto.

— Enio | @anoineim

---

## Email 5: Integração — Parceiro SaaS

**Para:** Founders de SaaS BR que já vendem compliance/security
**Subject:** Parceria: Guard Brasil como módulo white-label

Olá [Nome],

Percebi que a [Empresa] já atende clientes brasileiros com [solução de compliance/security]. Temos uma API de detecção de PII brasileiro que pode complementar o produto de vocês:

**Proposta:** Integrar o Guard Brasil como módulo dentro do [Produto]:
- Vocês ganham feature de mascaramento LGPD sem build interno
- Nós ganhamos distribuição via sua base de clientes
- Revenue share: 30% da receita gerada por clientes indicados

Stack técnica: REST API, <5ms, 15 padrões BR, receipt com hash.
API doc: guard.egos.ia.br/openapi.json

Vale uma call de 15 min esta semana?

— Enio Rocha | EGOS | guard.egos.ia.br

---

## Prospects sugeridos (pesquisar no LinkedIn)

| Segmento | Empresas exemplo | Email template |
|----------|-----------------|----------------|
| SaaS com IA | Nuvemshop, RD Station, Pipefy | #2 Pain Point |
| Fintechs | Nubank, PicPay, Stone | #1 Cold Intro |
| Healthtech | Dr. Consulta, Memed, iClinic | #3 Regulatório |
| Devtools | Rocketseat, Alura, Cubos | #4 Developer |
| Compliance SaaS | OneTrust BR, DPOnet, LGPD Brasil | #5 Parceria |

---

*Pronto para enviar. Adapte [Nome] e [Empresa]. Use guard.egos.ia.br como link principal.*
