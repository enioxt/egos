# Guard Brasil — Proteção de Dados Sensíveis para IA Governamental

> **"Sua IA pode vazar CPF, RG e dados de investigação. A nossa não."**

---

## O Problema

Sistemas de IA em órgãos públicos, delegacias, tribunais e prefeituras processam texto com dados sensíveis diariamente:

- Relatórios de investigação com CPF, RG, MASP, REDS
- Consultas jurídicas com número de processo e partes
- Prontuários com dados de saúde e dados pessoais

**Qualquer sistema de IA sem proteção específica pode vazar esses dados** — no log, na resposta ao usuário, ou no treinamento do modelo.

A LGPD (Lei 13.709/2018) responsabiliza o órgão pelo tratamento indevido. **Multa de até R$ 50 milhões por incidente.**

---

## A Solução: Guard Brasil

Guard Brasil é uma **camada de proteção** que inspeciona toda entrada e saída de sistemas de IA, em tempo real:

| Camada | O que faz |
|---|---|
| **PII Scanner** | Detecta CPF, RG, MASP, REDS, placa, processo, telefone, e-mail |
| **Mascaramento LGPD** | Substitui dados sensíveis antes de qualquer output |
| **ATRiAN Score** | Avaliação ética 0–100 com taxonomia de violações |
| **Evidence Chain** | Hash de auditoria imutável por resposta (trilha de conformidade) |

### Exemplo real (4ms de latência):

**Entrada:** `"O suspeito tem CPF 123.456.789-00 e RG 12.345.678-9"`

**Guard Brasil output:**
```json
{
  "safe": false,
  "output": "O suspeito tem CPF [CPF REMOVIDO] e [RG REMOVIDO]",
  "masking": { "sensitivityLevel": "critical", "findingCount": 2 },
  "lgpdDisclosure": "[LGPD] Dados pessoais detectados e mascarados. Lei 13.709/2018.",
  "atrian": { "score": 100, "passed": true }
}
```

---

## Como Integrar

**Opção 1 — REST API (qualquer linguagem):**
```bash
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "texto a inspecionar"}'
```

**Opção 2 — SDK npm (Node.js / TypeScript):**
```bash
npm install @egosbr/guard-brasil
```

**Opção 3 — MCP Server (Claude Code / Cursor / Windsurf):**
```bash
claude mcp add guard-brasil -- bun run mcp-server.ts
```

---

## Planos

| Plano | Preço | Limite | Suporte |
|---|---|---|---|
| **Open Source** | Gratuito | SDK local, sem limites | Comunidade |
| **Starter API** | R$ 49/mês | 10k inspeções/mês | Email |
| **Pro** | R$ 199/mês | 100k inspeções/mês + dashboard | Prioritário |
| **Business** | R$ 499/mês | 500k inspeções/mês + SLA | Ampliado |
| **Enterprise / Órgão Público** | Sob consulta | on-premise, policy packs, relatórios LGPD | Dedicado |

**Policy Packs setoriais** (R$ 2.990/ano):
- Segurança Pública (MASP, REDS, BO, RDO)
- Judiciário (CNJ, número processo, partes)
- Saúde (CID, prontuário, CPF/CNS)
- Financeiro (CPF/CNPJ, conta, chave Pix)

---

## Por que Guard Brasil?

| | Guard Brasil | Solução genérica |
|---|---|---|
| Entidades brasileiras | ✅ CPF, RG, MASP, REDS, placa | ❌ Apenas e-mail/telefone |
| LGPD compliance nativo | ✅ Disclosure automático | ❌ Manual |
| ATRiAN ético | ✅ Score + taxonomia | ❌ Não existe |
| Evidence chain auditável | ✅ Hash imutável por resposta | ❌ Não existe |
| Latência | ✅ < 5ms | ⚠️ Depende da API externa |
| Open source verificável | ✅ MIT | ❌ Black-box |

---

## Próximos Passos

1. **Teste gratuito:** `curl https://guard.egos.ia.br/health`
2. **Demo ao vivo:** Entre em contato para demonstração em 30 minutos com dados do seu sistema
3. **Piloto:** Implantação em ambiente de homologação em 1 dia

---

**Contato:** [enio@egos.ia.br](mailto:enio@egos.ia.br) · [guard.egos.ia.br](https://guard.egos.ia.br)

**EGOS** · Infraestrutura de IA ética para o setor público brasileiro
