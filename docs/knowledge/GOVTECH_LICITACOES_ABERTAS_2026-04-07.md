# GovTech — Licitações Abertas + Plano de Ação
**Data:** 2026-04-07 | **Fonte:** PNCP ao vivo (verificado via Playwright)
**Escopo:** Desenvolvimento de sistemas / software para governo — janela de parceria com software house

---

## ⚠️ ALERTA URGENTE

**LICITAÇÃO #2 — SAAE Linhares/ES encerra AMANHÃ 09/04 às 08:00h.**
Match perfeito com nossa stack (WhatsApp + chatbot + IA generativa). Ação necessária HOJE.

---

## Nossa Stack (para match técnico)

| Camada | Tecnologias |
|--------|-------------|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Node.js / Bun, Python (FastAPI), TypeScript |
| Banco de dados | PostgreSQL (Supabase), Neo4j, Redis, ChromaDB |
| IA / LLM | Claude API (Haiku/Sonnet), Gemini, OpenAI, multi-LLM router |
| DevOps | Docker, VPS Ubuntu (Hetzner), Caddy, GitHub Actions, CI/CD |
| Mensageria | WhatsApp (Evolution API), Telegram, WebSocket (Supabase Realtime) |
| Especialidades | LGPD/PII compliance (Guard Brasil), OSINT (Eagle Eye), chatbots, SaaS multi-tenant |
| Integrações | PNCP API, Stripe/Pix, Supabase, webhooks REST, PDF generation |

---

## 7 Licitações Abertas — Análise Completa

---

### 🔴 #1 — URGENTE HOJE

**SAAE Linhares — Plataforma Omnicanal CPaaS + IA Generativa**

| Campo | Valor |
|-------|-------|
| Órgão | Serviço Autônomo de Água e Esgoto de Linhares (SAAE) |
| UF | Espírito Santo — Linhares |
| Edital | 000005/2026 — PNCP: `27834977000160-1-000024/2026` |
| Objeto | Plataforma multicanal/omnicanal CPaaS + SaaS: chat, voz, vídeo WebRTC, chatbot WhatsApp/Instagram/Telegram, IA generativa, Cloud PBX 60 ramais, integração Firebird |
| Valor estimado | **R$ 72.571,00** |
| **Encerra** | **09/04/2026 às 08:00 — AMANHÃ** |
| ME/EPP | Não declarado (valor < R$80k — verificar edital) |
| Link | https://pncp.gov.br/app/editais/27834977000160/2026/24 |

**Por que é match perfeito:**
- Evolution API + WhatsApp = exatamente nossa stack (rodando em produção no VPS)
- Claude API para IA generativa no chatbot = já implementado no EGOS Gateway
- Telegram = @egosin_bot rodando, código pronto
- WebRTC + gravação = integrável com Supabase Storage + VPS
- Integração com Firebird via REST API = Node/Bun adapter (2-3 dias dev)
- LGPD obrigatório = Guard Brasil já existe

**Stack de execução:**
```
Evolution API (WhatsApp) → EGOS Gateway v0.3 → Claude Haiku (chatbot)
Telegram bot → @egosin_bot (código reutilizável)
Cloud PBX → integrar com Twilio ou VoIP provider
WebRTC → Jitsi Meet self-hosted ou Daily.co API
Firebird integration → Python FastAPI adapter
Hospedagem → VPS Hetzner + Docker + Caddy (já temos)
```

**Argumentos técnicos para proposta:**
1. Sistema em produção similar (EGOS 852 — chatbot policial com WhatsApp)
2. Evolution API: integração live, não prova de conceito
3. Multi-LLM fallback chain para resiliência (Claude → Gemini → OpenAI)
4. LGPD nativo (Guard Brasil — 15 padrões PII certificados)
5. VPS própria com SLA 99.9% (10 dias uptime contínuo verificável)

**Ação imediata (HOJE):**
- [ ] Baixar edital completo e TR (Termo de Referência)
- [ ] Verificar requisitos de habilitação técnica exigidos
- [ ] Contatar software house parceira com SICAF ativo
- [ ] Preparar proposta técnica em conjunto

---

### 🟡 #2 — Alta Prioridade (encerra 13/04)

**Brumado/BA — Sistema Integrado de Gestão Pública Web (34 módulos)**

| Campo | Valor |
|-------|-------|
| Órgão | Prefeitura Municipal de Brumado |
| UF | Bahia |
| Edital | PE 012/2026 — via Bolsa Nacional de Compras |
| Objeto | Sistemas web integrados de gestão pública: contabilidade, planejamento orçamentário, financeiro, licitações, almoxarifado, patrimônio, frotas, obras, transparência, folha, tributação, educação, saúde + implantação + migração + 300h suporte |
| Valor estimado | Sigiloso (verificar edital) |
| **Encerra** | **13/04/2026 às 07:30** |
| Link | https://www.sigapregao.com.br/app/licitacao/5534133 |

**Por que é match:**
- 34 módulos web integrados = plataforma SaaS multi-módulo (nossa especialidade)
- Transparência pública = integração PNCP API (já implementamos no Eagle Eye)
- Folha de pagamento, tributação = módulos complexos que precisam de parceiro com atestado

**Ação:** Depende de parceiro com atestado em sistema de gestão municipal completo.

---

### 🟡 #3 — Alta Prioridade (encerra 15/04)

**Brumadinho/MG — GED + Workflow BPM + Aplicativo Cidadão**

| Campo | Valor |
|-------|-------|
| Órgão | Prefeitura Municipal de Brumadinho |
| UF | Minas Gerais |
| Edital | PE 04/2026 (nº 56/2026) |
| Objeto | Digitalização com validade jurídica, GED/ECM, automação de processos (workflow BPM) em plataforma low-code, aplicativo de serviços ao cidadão, implantação + suporte + 12 meses |
| Valor estimado | Não publicado — verificar TR |
| **Encerra** | **15/04/2026 às 09:00** |
| Link | https://novo.brumadinho.mg.gov.br/portal/licitacao/36767 |

**Por que é match:**
- GED/ECM = Node/Bun backend + PostgreSQL + S3/MinIO para armazenamento
- Workflow BPM = nosso padrão de agents com estados (event-bus + Supabase)
- Aplicativo cidadão = Next.js PWA (já temos padrão no 852)
- Validade jurídica = assinatura digital via ICP-Brasil (integrável)
- Guard Brasil para LGPD na digitalização de documentos pessoais

**Stack de execução:**
```
GED: PostgreSQL + S3 (Supabase Storage) + full-text search (pg_trgm)
Workflow BPM: event-bus.ts + Supabase Realtime + estado persistido
App cidadão: Next.js 15 PWA + autenticação segura
Assinatura digital: ITI ICP-Brasil API ou ClickSign parceiro
```

---

### 🟠 #4 — Prioridade Média (encerra 17/04)

**Capivari de Baixo/SC — SaaS Gestão Educacional Municipal**

| Campo | Valor |
|-------|-------|
| Órgão | Prefeitura Municipal de Capivari de Baixo |
| UF | Santa Catarina |
| Edital | PE 14/2026 — PNCP: `95780441000160-1-000026/2026` |
| Objeto | SaaS gestão educacional: Gestão Escolar, Calendário, Ensino, Secretaria, Matrículas Online, Censo Escolar, ACT, Alimentação Escolar, Módulo Professor, Almoxarifado, Pais/Responsáveis (11 módulos) + hospedagem em data center |
| Valor estimado | **R$ 215.790,29** |
| **Encerra** | **17/04/2026 às 09:00** |
| Link | https://pncp.gov.br/app/editais/95780441000160/2026/26 |

**Por que é match:**
- SaaS multi-módulo web = nossa arquitetura padrão (Next.js + Supabase)
- Hospedagem em data center inclusa = VPS Hetzner + Docker + Caddy
- Matrículas Online = formulários + banco de dados (já construímos no 852)
- Censo Escolar = relatórios governamentais padronizados (INEP API)
- Guard Brasil para LGPD com dados de alunos e responsáveis

**Desafio:** Migração de dados de sistema legado — precisa de atestado técnico educacional.

---

### 🟠 #5 — Prioridade Média (encerra 23/04)

**Câmara Municipal de Dois Vizinhos/PR — Sistema Legislativo Web**

| Campo | Valor |
|-------|-------|
| Órgão | Câmara Municipal de Dois Vizinhos |
| UF | Paraná |
| Edital | 90002/2026 — PNCP: `78103579000105-1-000003/2026` |
| Objeto | Locação de software web: desmaterialização de documentos, processos legislativos e administrativos, Website da Câmara, Painel de Votação, Diário Oficial eletrônico, certificados digitais, integração com Executivo, e-mails, manutenção 60 meses |
| Valor estimado | **R$ 356.554,50** (60 meses = R$5.515/mês + implantação) |
| **Encerra** | **23/04/2026 às 08:30** |
| Publicado | 07/04/2026 (HOJE) |
| Link | https://pncp.gov.br/app/editais/78103579000105/2026/3 |

**Por que é match:**
- Website institucional = Next.js + Tailwind (2 dias dev)
- Painel de Votação em tempo real = Supabase Realtime + WebSocket (padrão pronto no EGOS)
- Diário Oficial eletrônico = geração PDF (Puppeteer) + publicação automática
- Gestão de processos = event-bus + workflow states
- Integração Executivo-Legislativo = REST API pública

**Diferencial competitivo:** Painel de Votação em tempo real com Supabase Realtime é um recurso raramente oferecido por sistemas legados — pode ser nosso ponto de diferenciação técnica.

---

### 🟢 #6 — Janela Ampla (encerra 24/04)

**Guaraniaçu/PR — Plataforma de Gestão Pública SaaS Multi-Entidades**

| Campo | Valor |
|-------|-------|
| Órgão | Prefeitura de Guaraniaçu + Câmara + Fundação (3 entidades) |
| UF | Paraná |
| Edital | PCE 23/2026 — PNCP: `76208818000166-1-000043/2026` |
| Objeto | Solução SaaS gestão pública integrada multi-entidades: implantação + migração (R$52k), licenças mensais 12 meses (R$501k), datacenter/hospedagem (R$48k), 400h suporte técnico (R$100k), 200h customização (R$58k) |
| Valor estimado | **R$ 761.282,11** |
| **Encerra** | **24/04/2026 às 08:30** |
| Link | https://pncp.gov.br/app/editais/76208818000166/2026/43 |

**Por que é match:**
- Multi-tenant nativo (3 entidades = 3 schemas Supabase isolados)
- Datacenter/hospedagem no objeto = VPS Hetzner + Docker + Caddy (nossa infra atual)
- 200h de customização = desenvolvimento faturado por hora
- 400h de suporte = SLA mensal com equipe técnica

**Maior ticket e maior complexidade** — necessita parceiro com atestado de sistema similar.

---

### 🟢 #7 — Janela Longa (encerra 01/06)

**Astorga/PR — Modernização de Gestão Pública (1.800h desenvolvimento)**

| Campo | Valor |
|-------|-------|
| Órgão | Prefeitura Municipal de Astorga |
| UF | Paraná |
| Edital | 90009/2026 — PNCP: `75743377000130-1-000056/2026` |
| Objeto | Modernização gestão pública: 1.800h desenvolvimento (R$115k), sistema municipal integrado (R$85k), plataforma web mensal 12 meses (R$103k), serviços complementares |
| Valor estimado | **R$ 376.148,50** |
| **Encerra** | **01/06/2026** |
| Publicado | 07/04/2026 (HOJE) |
| Modalidade | Concorrência Eletrônica (aberta a todos os portes) |
| Link | https://pncp.gov.br/app/editais/75743377000130/2026/56 |

**Por que é match:**
- 1.800h de desenvolvimento faturável = receita certa, escopo definido
- Modernização = escopo aberto para propor arquitetura moderna sobre legado
- 55 dias para preparar proposta técnica = tempo suficiente para estruturar tudo
- Concorrência (não exclusivo ME/EPP) = aberto, mas sem vantagem competitiva especial

---

## Estratégia de Parceria com Software House

### O que a parceria resolve

| EGOS traz | Software house traz |
|-----------|---------------------|
| Stack técnica moderna (IA, LGPD, cloud) | CNPJ ativo e cadastrado |
| Claude/Gemini integrado nativamente | SICAF + Compras.gov.br cadastro |
| VPS/Docker/Caddy em produção | Atestados de capacidade técnica |
| Guard Brasil (LGPD) | Capital social adequado |
| Velocidade de desenvolvimento | Certidões (CND, FGTS, CNDT) |
| GitHub + CI/CD + governança | Experiência em licitações |

### Modelos de receita possíveis

**Modelo A — Subcontratação técnica (mais simples)**
```
Software house assina o contrato com o órgão público
EGOS executa tecnicamente como subcontratada
Split: 60% EGOS / 40% software house
Risco: baixo para ambos
```

**Modelo B — Consórcio (mais formal)**
```
EGOS + software house formam consórcio temporário
Ambos assinam proposta conjunta
Split negociado por papel
Exige formalização jurídica (MOU)
```

**Modelo C — White-label EGOS**
```
Software house licencia nossa plataforma
Apresenta como produto próprio
EGOS recebe por licença + suporte
Escalável para múltiplas licitações
```

### Perfil de software house ideal para parceria

**Critérios de busca:**
- CNPJ ativo com CNAE 6201-5/00 ou 6202-3/00
- SICAF cadastrado (Compras.gov.br)
- Atestado de pelo menos 1 sistema web municipal/estadual
- Capital social adequado (≥ 10% do valor do contrato)
- Equipe técnica registrada (mínimo 1 responsável técnico TI)
- Preferencialmente em SC/PR/SP (mesma região dos editais)

**Onde encontrar:**
- Vencedores anteriores no PNCP (pesquisar por CNPJ + CNAE)
- CIASC (SC): empresas cadastradas para sistemas municipais
- ASSESPRO (associação de empresas de TI por estado)
- LinkedIn: "empresa software gestão municipal" + SC/PR/SP
- Parceiros Betha/Softplan que já trabalham com prefeituras

---

## Plano de Ação Completo

### FASE 0 — Hoje (urgência máxima para Linhares)

```
[ ] 1. Baixar edital SAAE Linhares (https://pncp.gov.br/app/editais/27834977000160/2026/24)
[ ] 2. Ler Termo de Referência completo — identificar requisitos técnicos exatos
[ ] 3. Verificar: precisa de SICAF? Atestado? Capital mínimo?
[ ] 4. Contatar pelo menos 3 software houses com SICAF ativo
[ ] 5. Fazer pitch rápido: "Temos a stack completa para este edital, precisamos de parceiro habilitado"
[ ] 6. Se parceria confirmada: montar proposta técnica hoje
```

### FASE 1 — Esta semana (07-11/04)

```
[ ] GOV-TECH-003: Verificar CNPJ EGOS — CNAE, SICAF, certidões
[ ] Baixar todos os 7 editais e TRs
[ ] Classificar por match técnico (1-5) e viabilidade de habilitação
[ ] Identificar 3 software houses candidatas a parceria (pesquisa PNCP histórico)
[ ] Preparar deck de parceria (1 página): nossa stack + proposta de split
[ ] GOV-TECH-005: Draft do produto Ouvidoria+LGPD para usar como portfólio
```

### FASE 2 — Próximas 2 semanas (12-24/04)

```
[ ] Submeter propostas para #3 (Brumadinho) + #4 (Câmara PR) + #5 (Guaraniaçu)
[ ] GOV-TECH-001: Eagle Eye monitorando PNCP automaticamente (alerta diário)
[ ] Iniciar conversas com Softplan/Betha sobre parceria estratégica
[ ] Preparar documentação técnica padrão (pode ser reusada em múltiplos editais):
    - Comprovante de sistema web em produção
    - Documentação do VPS + Docker + Caddy
    - Guard Brasil como módulo LGPD
    - Portfólio: HQ, Eagle Eye, 852, Gateway
```

### FASE 3 — Médio prazo (Maio-Junho)

```
[ ] Astorga/PR (01/06) — com mais tempo, proposta técnica completa
[ ] Registrar empresa no SICAF se não habilitada
[ ] Obter primeiro atestado via pilot gratuito (GOV-TECH-009)
[ ] GOV-TECH-002: Dashboard vencedores para identificar próximas oportunidades
```

---

## Documentação Técnica para Propostas

### 1. Portfólio de Sistemas em Produção (já temos)

| Sistema | URL | Descrição |
|---------|-----|-----------|
| EGOS HQ | hq.egos.ia.br | Dashboard Next.js, JWT auth, 9 microserviços |
| Guard Brasil API | guard.egos.ia.br | API LGPD/PII, 4ms latência, 15 padrões |
| Eagle Eye | eagleeye.egos.ia.br | OSINT licitações, 84 territórios, cron diário |
| 852 Police Bot | 852.egos.ia.br | Chatbot seguro, WhatsApp + web, PostgreSQL |
| EGOS Gateway | gateway.egos.ia.br | Multi-canal (WhatsApp + Telegram + Web) |
| Hermes Agent | VPS | LLM executor 24/7, Claude OAuth |

### 2. Template de Proposta Técnica (reusável)

```markdown
## Solução Técnica Proposta

### Arquitetura
- Frontend: Next.js 15 / React / TypeScript — SSR + PWA
- Backend: Node.js + Bun / FastAPI (Python para módulos intensivos)
- Banco de Dados: PostgreSQL (Supabase) + Redis (cache) + S3 (armazenamento)
- IA Integrada: Claude Haiku (atendimento automático) com fallback Gemini
- Infraestrutura: VPS Ubuntu 20.04 + Docker + Caddy (HTTPS automático)
- LGPD: Guard Brasil — mascaramento automático PII em todas as camadas

### SLA Proposto
- Disponibilidade: 99.5% (uptime atual VPS: 10+ dias contínuos verificável)
- Tempo de resposta API: < 200ms (P95)
- Backup diário automático
- Suporte técnico: 8h/dia, resposta < 4h

### Diferenciais
1. IA generativa integrada nativamente (não como add-on)
2. LGPD compliance automático (Guard Brasil — certificado)
3. Multi-canal nativo (WhatsApp + Telegram + Web + API)
4. Código-fonte entregue ao órgão contratante
5. Documentação técnica completa (padrão EGOS governance)
```

### 3. Checklist de Habilitação (verificar por edital)

```
JURÍDICA:
[ ] CNPJ ativo + situação regular
[ ] Contrato Social / Estatuto consolidado
[ ] CNAE 6201-5/00 (desenvolvimento sob encomenda) ou 6202-3/00

FISCAL E TRABALHISTA:
[ ] CND Federal (Receita Federal + PGFN): certidao.receita.fazenda.gov.br
[ ] CND Estadual: portal da Fazenda estadual da sede
[ ] CND Municipal: prefeitura da sede da empresa
[ ] CRF FGTS: caixa.gov.br/certificado-regularidade-fgts
[ ] CNDT (trabalhistas): tst.jus.br

TÉCNICA:
[ ] Atestado capacidade técnica (pessoa jurídica de direito público ou privado)
[ ] Responsável técnico com nível superior em TI (diploma + CTPS)

ECONÔMICO-FINANCEIRA:
[ ] Capital social ≥ 10% do valor estimado anual do contrato
[ ] Balanço Patrimonial do último exercício

EXTRA ME/EPP:
[ ] Declaração de enquadramento ME/EPP (se aplicável)
[ ] Vantagem de desempate: pode cobrir até 5% acima da melhor proposta de grande porte
```

---

## Pitch para Software House Parceira (1 página)

```
PARCERIA TÉCNICA — LICITAÇÕES DE DESENVOLVIMENTO DE SOFTWARE

Quem somos:
Time técnico especializado em desenvolvimento de sistemas web modernos com IA nativa,
compliance LGPD e infraestrutura cloud. Sistemas em produção: 6 aplicações web,
1 API certificada (Guard Brasil LGPD), infrastructure VPS Docker com 19 containers.

O que propomos:
Parceria em licitações de desenvolvimento de software onde você entra com a
habilitação jurídica/fiscal e nós executamos tecnicamente.

Nossa entrega:
• Desenvolvimento full-stack (Next.js, Node, Python, PostgreSQL)
• IA integrada nativamente (Claude, Gemini, multi-LLM)
• Compliance LGPD automático (Guard Brasil)
• Infraestrutura cloud + Docker + HTTPS (VPS própria)
• CI/CD completo + documentação técnica

Primeiras oportunidades identificadas:
1. SAAE Linhares/ES — R$ 72k — chatbot IA + WhatsApp — HOJE
2. Câmara Dois Vizinhos/PR — R$ 357k — sistema legislativo web — 23/04
3. Guaraniaçu/PR — R$ 761k — gestão pública SaaS — 24/04

Modelo proposto:
Subcontratação técnica — você assina o contrato, nós executamos.
Split: 60% EGOS / 40% parceiro sobre o valor técnico do contrato.

Contato: [enio@egos.ia.br]
```

---

## Monitoramento Contínuo

### Eagle Eye PNCP (GOV-TECH-001 a implementar)

Palavras-chave para alert diário:
```sql
-- Query para Eagle Eye monitorar
WHERE objeto LIKE ANY(ARRAY[
  '%desenvolvimento de sistema%',
  '%software de gest%',
  '%plataforma digital%',
  '%chatbot%',
  '%ouvidoria digital%',
  '%portal do cidad%',
  '%sistema web%',
  '%solução integrada%'
])
AND valor_global BETWEEN 15000 AND 2000000
AND status = 'Recebendo Propostas'
```

### Fontes para monitorar manualmente

- PNCP: https://pncp.gov.br/app/editais?q=software+gestao&status=recebendo_proposta
- BEC-SP: https://www.bec.sp.gov.br
- ComprasRS: https://licitacoes.rs.gov.br
- ComprasSC: https://www.compras.sc.gov.br
- Licitar Digital (PR): https://www.licitardigital.com.br
- Siga Pregão: https://www.sigapregao.com.br

---

*Documento gerado em 2026-04-07 | Dados verificados ao vivo no PNCP via Playwright*
*SSOT: docs/knowledge/GOVTECH_LICITACOES_ABERTAS_2026-04-07.md*
