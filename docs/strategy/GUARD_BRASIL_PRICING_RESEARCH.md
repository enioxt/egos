# Guard Brasil — Pesquisa de Pricing e Mercado (com dados reais)

> **Data:** 2026-03-30 | **Fontes:** Exa search, Grepture, Cloak, Protecto, Skyflow, AWS, Google Cloud DLP
> **Objetivo:** Definir pricing ideal para Guard Brasil com base em competidores reais

---

## 1. MAPA DO MERCADO — Quem faz o quê hoje

### Competidores diretos (PII redaction/masking para APIs de IA)

| Produto | Modelo | Free Tier | Starter | Pro | Enterprise | Diferencial |
|---------|--------|-----------|---------|-----|-----------|-------------|
| **Grepture** | Proxy API | 1.000 req/mo FREE | EUR 49/mo (100k req) | EUR 299/mo (1M req) | Custom | Reversible redaction, EU-hosted, secret scanning |
| **Cloak.business** | Token-based | 10.000 tokens FREE | EUR 3/mo (50k tokens) | EUR 15/mo (300k tokens) | EUR 29/mo (750k) | 48 languages, 317 recognizers, Chrome extension |
| **Protecto** | API-first | 1.000 calls FREE | $250/mo | Custom | Custom | Context-aware masking, LLM-powered, <50ms |
| **Private AI** | Enterprise | Nenhum | Nenhum | Nenhum | $50k+/ano | Healthcare PHI, 50+ linguas |
| **Strac** | DLP SaaS | Nenhum | Custom | Custom | Custom | DLP amplo (Slack, email, AI) |
| **LLM Guard** | Open source | Ilimitado (self-host) | N/A | N/A | N/A | 35+ scanners, toxicity, bias |
| **MS Presidio** | Open source | Ilimitado (self-host) | N/A | N/A | N/A | Python, NLP customization |

### Competidores indiretos (Cloud DLP)

| Produto | Modelo | Preço |
|---------|--------|-------|
| **AWS Comprehend** | Pay per character | $0.0001/char (~$0.01/100 chars) |
| **Google Cloud DLP** | Pay per request | $1-$3 per 10k findings |
| **Azure Content Safety** | Pay per request | Similar ao Google |

---

## 2. PADROES DE PRICING QUE FUNCIONAM

### O que o mercado mostra:

1. **FREE TIER é OBRIGATÓRIO** — Todos os produtos modernos oferecem (exceto enterprise-only como Private AI)
2. **Pay-per-use escala melhor** — Cloak cobra EUR 0.06/1k tokens no Starter, EUR 0.039/1k no Business (desconto por volume)
3. **A faixa de $250-$299/mo é o sweet spot para Pro** — Grepture (EUR 299/1M req), Protecto ($250/mo)
4. **Enterprise é custom** — Ninguém publica preço acima de $500/mo
5. **Reversible redaction é diferencial** — Só Grepture tem; Guard Brasil pode ter

### Insight-chave de pricing (Cloak.business):

> "Enterprise DLP solutions custam $50k-$500k/ano. Token-based pricing pode entregar o mesmo por **277x menos**."

Isto confirma que **pay-per-use é a estratégia correta** para Guard Brasil.

---

## 3. PROPOSTA DE PRICING — Guard Brasil (baseada em dados reais)

### Princípio: **Degressive pricing** — quanto mais usa, mais barato fica

| Tier | Preço | Chamadas/mês | Custo/chamada | Público |
|------|-------|-------------|---------------|---------|
| **Free** | R$ 0 | 150 | R$ 0 | Devs, estudantes, teste |
| **Starter** | R$ 49/mo | 10.000 | R$ 0,0049 | Startups, pequenas prefeituras |
| **Pro** | R$ 199/mo | 100.000 | R$ 0,00199 | Médias empresas, tribunais |
| **Business** | R$ 499/mo | 500.000 | R$ 0,000998 | Grandes órgãos, ministérios |
| **Enterprise** | Custom | Ilimitado | Negociável | Governo federal, bancos |

### Por que estes valores:

**Free tier = 150 chamadas (não 100, não 5)**
- Suficiente para testar durante 1 semana (20 chamadas/dia)
- Não exige cartão de crédito
- Baixo custo real: ~$0.01 total em LLM (150 * $0.00007)
- **Referência:** Cloak dá 10k tokens/mo, Grepture dá 1k req/mo, Protecto dá 1k calls
- **Guard Brasil: 150 chamadas = generoso para teste, curto para produção**

**Starter R$ 49/mo (comparação):**
- Grepture: EUR 49/mo = ~R$ 280 (para 100k req) — nós somos **6x mais barato**
- Cloak: EUR 3/mo = ~R$ 17 (para 50k tokens, mas token ≠ request) — comparável
- Protecto: $250/mo = ~R$ 1.400 — nós somos **28x mais barato**
- **Guard Brasil posicionado como o mais acessível do mercado para govtech BR**

**Pro R$ 199/mo:**
- Grepture Business: EUR 299/mo = ~R$ 1.700 (1M req) — nós somos **8x mais barato**
- Mas entregamos menos features (sem reversible redaction por enquanto)
- **Custo por chamada cai 60%** vs Starter = recompensa growth

**Business R$ 499/mo:**
- Posicionado entre Protecto ($250) e Grepture Pro (EUR 299)
- Adequado para um secretário de estado que precisa assinar PO
- Volume alto = desconto natural (R$ 0,001/chamada)
- **Margem:** 500k chamadas × $0.00007 LLM = $35/mo = R$175 custo → **margem 65%**

**Enterprise = Custom:**
- Para Prodemge, Serpro, Datasus, TCU, TCE-MG
- SLA, suporte dedicado, on-premise
- Ticket médio: R$ 2k-10k/mo

### Modelo de desconto por volume (degressive):

```
Chamadas/mês    Custo/chamada     Desconto vs Free
150             GRÁTIS            —
10.000          R$ 0,0049         Referência
100.000         R$ 0,00199        -59%
500.000         R$ 0,000998       -80%
1.000.000+      R$ 0,0005 (neg)   -90%
```

### Por que NÃO R$ 0,02/chamada (nosso valor anterior):

O mercado mostra que R$ 0,02/chamada é **caro demais** para volume. Competidores cobram:
- Cloak: EUR 0,039/1k = R$ 0,22/1k = **R$ 0,00022/chamada**
- Grepture: EUR 49/100k = EUR 0,00049/chamada = **R$ 0,0028/chamada**
- Guard Brasil a R$ 0,02 seria **7x mais caro que Grepture** e **90x mais caro que Cloak**

**Novo valor recomendado: R$ 0,0049/chamada (Starter) a R$ 0,001 (Business)**

Isto posiciona Guard Brasil como:
- **Mais barato que Grepture** (nosso principal competidor funcional)
- **Mais acessível que Protecto** (que cobra $250/mo)
- **Competitivo com Cloak** (nosso competidor de preço)
- **Infinitamente mais barato que enterprise DLP** ($50k+/ano)

### Mas ATENÇÃO — nosso diferencial NÃO é preço:

O que Guard Brasil tem que NINGUÉM tem:
1. **PII brasileiro** — CPF, RG, MASP, REDS, placa, processo judicial
2. **ATRiAN ethical validation** — score 0-100 de ética (bias, fairness)
3. **LGPD-first** — compliance brasileiro de nascença
4. **Transparência Radical** — customer vê cada chamada, cada custo, cada decisão da IA
5. **Govtech-native** — fala a língua de prefeitura, tribunal, ministério público

**Competidores são todos EUA/EU. Nenhum foca em Brasil.**

---

## 4. SIMULAÇÃO DE RECEITA COM NOVO PRICING

### Cenário A: Conservador (5 clientes em 3 meses)

```
Mês 1: 2 Starter (R$ 49) + 1 Free = R$ 98/mo
Mês 2: 3 Starter (R$ 49) + 1 Pro (R$ 199) = R$ 346/mo
Mês 3: 4 Starter + 2 Pro = R$ 594/mo
Mês 6: 8 Starter + 3 Pro + 1 Business = R$ 1.489/mo
```

### Cenário B: Otimista (X.com viral + outreach)

```
Mês 1: 5 Starter + 3 Free = R$ 245/mo
Mês 2: 10 Starter + 2 Pro = R$ 888/mo
Mês 3: 15 Starter + 5 Pro + 1 Business = R$ 2.230/mo
Mês 6: 30 Starter + 10 Pro + 3 Business = R$ 4.957/mo
```

### Cenário C: Institucional (1 contrato govtech grande)

```
Mês 3: 1 Enterprise = R$ 5.000/mo (contrato anual R$ 60k)
+ pequenos Starters de teste = R$ 5.200/mo
```

### Break-even com novo pricing:

```
Infraestrutura: R$ 650/mo (Hetzner)
Break-even: ~14 Starters OU 4 Pros OU 2 Business
Timeline: Mês 2-3 (conservador), Mês 1 (se institucional)
```

---

## 5. CUSTO REAL POR CHAMADA (nosso lado)

### Chamada simples (60% dos casos — REGEX ONLY):

```
Input: "CPF: 123.456.789-00"
Processing: regex match → mask → return
LLM: NENHUM
Custo: R$ 0,00 (zero, regex local)
Latência: <5ms
```

### Chamada média (30% — Qwen-plus):

```
Input: "Texto com múltiplos dados sensíveis e contexto"
Processing: regex + LLM validation
LLM: Qwen-plus (~100 tokens in, ~50 out)
Custo: $0.00007 = R$ 0,00035
Latência: ~150ms
```

### Chamada complexa (10% — validação ética ATRiAN):

```
Input: "Texto que precisa de análise de bias/fairness"
Processing: regex + LLM scoring + ATRiAN
LLM: Qwen-plus (~200 tokens in, ~100 out)
Custo: $0.00014 = R$ 0,0007
Latência: ~300ms
```

### Custo médio ponderado:

```
(0.6 × R$0) + (0.3 × R$0.00035) + (0.1 × R$0.0007) = R$ 0,000175/chamada

Margem no Starter (R$ 0,0049/chamada):
R$ 0,0049 - R$ 0,000175 = R$ 0,004725 margem (96,4% margem bruta!)

Margem no Business (R$ 0,001/chamada):
R$ 0,001 - R$ 0,000175 = R$ 0,000825 margem (82,5% margem bruta!)
```

**Conclusão: Margem de 82-96% em todas as tiers. O produto é extremamente lucrativo.**

---

## 6. RECOMENDAÇÃO FINAL

### Modelo aprovado:

```
GUARD BRASIL PRICING v2.0

FREE:     R$ 0       | 150 chamadas/mês | Sem cartão
STARTER:  R$ 49/mês  | 10k chamadas     | Dashboard básico
PRO:      R$ 199/mês | 100k chamadas    | Dashboard + IA insights
BUSINESS: R$ 499/mês | 500k chamadas    | Tudo + SLA + suporte
ENTERPRISE: Custom    | Ilimitado        | On-premise + dedicado
```

### Overage (excedente):

```
Se ultrapassar a cota do tier:
- Starter: R$ 0,008/chamada extra (60% mais caro que o tier)
- Pro: R$ 0,004/chamada extra
- Business: R$ 0,002/chamada extra
- Motivo: incentivo para upgrade, não para punição
```

### Comparação final com mercado:

| Guard Brasil | Grepture | Cloak | Protecto |
|---|---|---|---|
| R$ 0 (150 req) | EUR 0 (1k req) | EUR 0 (10k tok) | $0 (1k calls) |
| R$ 49 (10k req) | EUR 49 (100k req) | EUR 3 (50k tok) | $250 (custom) |
| R$ 199 (100k req) | EUR 299 (1M req) | EUR 15 (300k tok) | Custom |
| R$ 499 (500k req) | Custom | EUR 29 (750k tok) | Custom |

**Posicionamento: Premium para Brasil (ninguém mais faz PII BR), acessível vs. mercado global.**
