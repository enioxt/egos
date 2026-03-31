# Cálculo de Custos de Infraestrutura — Modelo de Cobrança por Uso

> **Objetivo:** Definir % justa de cobrança por uso considerando custos reais
> **Data:** 2026-03-31

---

## 💰 Custos Mensais de Infraestrutura

### VPS Hetzner (Atual)
| Item | Especificação | Custo Mensal (EUR) | Custo Mensal (R$) |
|------|---------------|---------------------|-------------------|
| **VPS CPX31** | 4 vCPU, 8GB RAM, 160GB SSD | €12,90 | R$ 75 |
| **Bandwidth** | 20TB (incluído) | €0 | R$ 0 |
| **Backup** | 20% do custo VPS | €2,58 | R$ 15 |
| **Total VPS** | — | **€15,48** | **R$ 90** |

### Energia Elétrica (VPS remoto não consome local)
| Item | Consumo | Custo |
|------|---------|-------|
| **VPS remoto** | 0 kWh local | R$ 0 |
| **Desenvolvimento local** | ~50 kWh/mês (notebook) | R$ 40 |

### Internet
| Item | Plano | Custo Mensal |
|------|-------|--------------|
| **Fibra 300 Mbps** | Uso compartilhado (pessoal + EGOS) | R$ 100 (50% alocado) = R$ 50 |

### Domínios e DNS
| Item | Custo Anual | Custo Mensal |
|------|-------------|--------------|
| **egos.ia.br** | R$ 60/ano | R$ 5 |
| **commons.egos.ia.br** | Subdomínio (incluído) | R$ 0 |
| **guard.egos.ia.br** | Subdomínio (incluído) | R$ 0 |
| **Total DNS** | — | R$ 5 |

### APIs e Serviços Externos
| Serviço | Uso Atual | Custo Mensal |
|---------|-----------|--------------|
| **Supabase** | Free tier (500MB) | R$ 0 |
| **GitHub** | Free | R$ 0 |
| **Cloudflare** | Free | R$ 0 |
| **Qwen (Alibaba)** | Pay-per-use (~R$ 0,02/1k tokens) | R$ 10-50 (variável) |
| **Gemini** | Free tier | R$ 0 |
| **Total APIs** | — | **R$ 10-50** |

---

## 📊 Custo Total Mensal (Infraestrutura)

| Categoria | Custo Mensal |
|-----------|--------------|
| VPS Hetzner | R$ 90 |
| Energia (dev local) | R$ 40 |
| Internet (50% alocado) | R$ 50 |
| Domínios | R$ 5 |
| APIs (média) | R$ 30 |
| **TOTAL** | **R$ 215** |

**Por dia:** R$ 215 / 30 = **R$ 7,17/dia**
**Por hora:** R$ 7,17 / 24 = **R$ 0,30/hora**

---

## ⏱️ Tempo de Trabalho (Valor Hora)

### Desenvolvimento e Manutenção
| Atividade | Horas/Mês | Valor Hora | Custo Total |
|-----------|-----------|------------|-------------|
| **Desenvolvimento (novas features)** | 20h | R$ 150/h | R$ 3.000 |
| **Manutenção (bugs, updates)** | 10h | R$ 100/h | R$ 1.000 |
| **Suporte técnico** | 5h | R$ 80/h | R$ 400 |
| **DevOps (deploy, infra)** | 5h | R$ 100/h | R$ 500 |
| **Total Trabalho** | 40h/mês | — | **R$ 4.900** |

### Custo Total (Infra + Trabalho)
- Infraestrutura: R$ 215/mês
- Trabalho: R$ 4.900/mês
- **TOTAL:** R$ 5.115/mês

---

## 🎯 Modelo de Cobrança Por Uso (Justo)

### Cenário 1: Produto SaaS com Usuários Ativos (ex: 852, Carteira-Livre)

**Custos por usuário/mês:**
- Infraestrutura: R$ 215 / 100 usuários = R$ 2,15/usuário
- Processamento AI (Qwen): ~R$ 0,50/usuário (50 consultas/mês)
- Storage Supabase: R$ 0,10/usuário
- **Custo Total por Usuário:** R$ 2,75/mês

**Pricing Sugerido:**
- **R$ 15/usuário/mês** (markup 5,45x sobre custo)
- Lucro: R$ 12,25/usuário (82% margem)

**Split Proposto:**
| Parte | % | Valor (R$ 15/user) |
|-------|---|---------------------|
| **Lara (Comercial)** | 50% | R$ 7,50/user |
| **Implementador (EGOS)** | 40% | R$ 6,00/user |
| **Kernel (Infra/Manutenção)** | 10% | R$ 1,50/user |

**Justificativa:**
- Lara traz o cliente (50% justo)
- EGOS mantém infra + código + suporte (40%)
- Kernel cobre custos operacionais (10%)

---

### Cenário 2: API Call-Based (ex: Guard Brasil)

**Custos por 1.000 chamadas:**
- Processamento PII + ATRiAN: R$ 0,02 (Qwen)
- VPS overhead: R$ 0,01
- Bandwidth: R$ 0,005
- **Custo Total:** R$ 0,035/1k calls

**Pricing Sugerido:**
- **R$ 0,15/1k chamadas** (markup 4,3x sobre custo)
- Lucro: R$ 0,115/1k calls (77% margem)

**Split Proposto:**
| Parte | % | Valor (R$ 0,15/1k) |
|-------|---|---------------------|
| **Lara (Comercial)** | 50% | R$ 0,075/1k |
| **Implementador (EGOS)** | 35% | R$ 0,052/1k |
| **Kernel (Infra/API)** | 15% | R$ 0,023/1k |

**Justificativa:**
- Lara traz o cliente (50%)
- EGOS mantém API + SLA + monitoramento (35%)
- Kernel cobre custos de infra e latência (15%)

---

### Cenário 3: Implementação One-Time + Suporte Recorrente (ex: EGOS Kernel)

**Custos de Implementação (one-time):**
- Tempo técnico: 30-40h × R$ 150/h = R$ 4.500 - R$ 6.000
- Setup infra: R$ 500
- Onboarding: R$ 300
- **Total Implementação:** R$ 5.300 - R$ 6.800

**Pricing One-Time Sugerido:** R$ 12.000
- Margem: ~80%

**Split One-Time:**
| Parte | % | Valor (R$ 12.000) |
|-------|---|-------------------|
| **Lara (Comercial)** | 50% | R$ 6.000 |
| **Implementador (EGOS)** | 45% | R$ 5.400 |
| **Kernel** | 5% | R$ 600 |

**Suporte Mensal Recorrente:** R$ 800/mês
- Custos: R$ 200/mês (10h × R$ 20/h amortizado)
- Margem: 75%

**Split Recorrente:**
| Parte | % | Valor (R$ 800/mês) |
|-------|---|---------------------|
| **Lara** | 50% | R$ 400/mês |
| **EGOS** | 40% | R$ 320/mês |
| **Kernel** | 10% | R$ 80/mês |

---

## 🔢 Tabela Consolidada de Splits (Novo Modelo 50% Lara)

### Implementações One-Time

| Produto | Preço | Lara 50% | EGOS 45% | Kernel 5% |
|---------|-------|----------|----------|-----------|
| EGOS Kernel | R$ 12.000 | R$ 6.000 | R$ 5.400 | R$ 600 |
| Carteira-Livre | R$ 18.000 | R$ 9.000 | R$ 8.100 | R$ 900 |
| 852 Inteligência | R$ 15.000 | R$ 7.500 | R$ 6.750 | R$ 750 |
| Intel. Dados Públicos | R$ 25.000 | R$ 12.500 | R$ 11.250 | R$ 1.250 |
| Assistentes Guiados | R$ 10.000 | R$ 5.000 | R$ 4.500 | R$ 500 |
| EGOS-Lab | R$ 6.000 | R$ 3.000 | R$ 2.700 | R$ 300 |

**Ticket Médio:** R$ 14.333
**Comissão Média Lara:** R$ 7.167 por venda one-time

### Suporte Mensal Recorrente

| Tier | Preço/Mês | Lara 50% | EGOS 40% | Kernel 10% |
|------|-----------|----------|----------|------------|
| Basic | R$ 800 | R$ 400 | R$ 320 | R$ 80 |
| Pro | R$ 1.500 | R$ 750 | R$ 600 | R$ 150 |
| Enterprise | R$ 3.000 | R$ 1.500 | R$ 1.200 | R$ 300 |

### Cobrança Por Uso (SaaS)

| Modelo | Preço | Lara 50% | EGOS 40% | Kernel 10% |
|--------|-------|----------|----------|------------|
| R$ 15/user/mês | R$ 15 | R$ 7,50 | R$ 6,00 | R$ 1,50 |
| R$ 0,15/1k calls | R$ 0,15 | R$ 0,075 | R$ 0,06 | R$ 0,015 |

---

## 📈 Simulação de Receita (Ano 1 com 50% Lara)

### Cenário Conservador (10 vendas one-time + 5 suporte mensal)

| Fonte | Qtd | Receita Total | Lara 50% |
|-------|-----|---------------|----------|
| **One-time** | 10 vendas | R$ 143.330 | R$ 71.665 |
| **Suporte mensal** | 5 clientes × 12 meses × R$ 800 | R$ 48.000 | R$ 24.000 |
| **Total Ano 1** | — | **R$ 191.330** | **R$ 95.665** |

**Por mês (Lara):** R$ 95.665 / 12 = **R$ 7.972/mês**

### Cenário Otimista (20 vendas + 10 suporte + SaaS)

| Fonte | Qtd | Receita Total | Lara 50% |
|-------|-----|---------------|----------|
| **One-time** | 20 vendas | R$ 286.660 | R$ 143.330 |
| **Suporte mensal** | 10 clientes × 12 meses × R$ 1.200 (média) | R$ 144.000 | R$ 72.000 |
| **SaaS (50 users)** | 50 users × 12 meses × R$ 15 | R$ 9.000 | R$ 4.500 |
| **Total Ano 1** | — | **R$ 439.660** | **R$ 219.830** |

**Por mês (Lara):** R$ 219.830 / 12 = **R$ 18.319/mês**

---

## ✅ Recomendação Final

### Modelo de Splits Aprovado

**One-Time (Implementações):**
- Lara: **50%** (prospecção + fechamento)
- EGOS: **45%** (implementação técnica)
- Kernel: **5%** (ecossistema)

**Recorrente (Suporte/SaaS):**
- Lara: **50%** (relacionamento contínuo)
- EGOS: **40%** (manutenção + suporte)
- Kernel: **10%** (infra + custos operacionais)

**Por Uso (API/Chamadas):**
- Lara: **50%** (trouxe o cliente)
- EGOS: **35%** (manutenção da API)
- Kernel: **15%** (infra + bandwidth)

### Pricing Justo (Markup sobre Custos)

| Modelo | Custo Real | Pricing | Markup | Margem |
|--------|-----------|---------|--------|--------|
| **SaaS por usuário** | R$ 2,75 | R$ 15 | 5,45x | 82% |
| **API por 1k calls** | R$ 0,035 | R$ 0,15 | 4,3x | 77% |
| **Implementação** | R$ 5.500 | R$ 14.000 | 2,5x | 61% |

**Justificativa:**
- Margem saudável (61-82%) cobre imprevistos
- Preços competitivos com mercado BR
- Split 50/50 atrai parceiro comercial forte
- Kernel sustentável com 5-15% dependendo do modelo

---

**Calculado em:** 2026-03-31 15:00
**Válido para:** Contratos EGOS Commons 2026-2027
