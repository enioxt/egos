# X MOAT Keywords — Oportunidades OSINT & Inteligência Brasil

> **Versão:** 1.0.0 | **Atualizado:** 2026-04-08 | **Contexto:** Keywords alinhadas ao MOAT do EGOS para monitoramento X.com
> **SSOT:** Este documento alimenta `scripts/x-opportunity-alert.ts`

---

## 🎯 Estrutura das Keywords

| Tipo | Descrição | Exemplos |
|------|-----------|----------|
| **Moat Keywords** | Palavras-chave de alta conversão para produtos EGOS | OSINT, forense, LGPD, GovTech |
| **Anti-Keywords** | Palavras que reduzem relevância (ruído) | curso, mentoria, dropshipping, grátis |
| **Brazilian Context** | Termos específicos do mercado brasileiro | delegacia, inquérito, investigação policial, PCMG, PMMG |

---

## 🔥 Moat Keywords — Tier 1 (Alta Conversão)

### OSINT & Investigação Digital

| Keyword | Categoria | Produto | Contexto Brasil |
|---------|-----------|---------|-----------------|
| `OSINT` | Core | 852, Guard Brasil | Inteligência de fontes abertas |
| `inteligência de fontes abertas` | Core | 852, Guard Brasil | Termo oficial em português |
| `investigação digital` | Core | 852 | Forense digital policial |
| `cibercrime` | Core | 852 | Investigação de crimes digitais |
| `cruzamento de dados` | Core | 852, Guard Brasil | Análise correlacional |
| `forense digital` | Core | 852 | Perícia criminal digital |
| `análise de redes sociais` | Core | 852 | Social media intelligence (SOCMINT) |
| `monitoramento digital` | Core | 852 | Vigilância online |
| `cadeia de custódia digital` | Core | 852 | Preservação de evidências |
| `laudo digital` | Core | 852 | Documentação forense |
| `perícia em dispositivos` | Core | 852 | Mobile/PC forensics |
| `recuperação de dados` | Core | 852 | Data recovery forense |
| `análise de malware` | Core | 852 | Reverse engineering de ameaças |
| `threat intelligence` | Core | 852 | Inteligência de ameaças |
| `infringement detection` | Core | 852 | Detecção de infrações digitais |

### Username & Social Media OSINT

| Keyword | Categoria | Ferramenta | Prioridade |
|---------|-----------|------------|------------|
| `username search` | OSINT | Blackbird, Sherlock, Maigret | ⭐⭐⭐⭐⭐ |
| `social media intelligence` | OSINT | 852, Guard Brasil | ⭐⭐⭐⭐⭐ |
| `encontrar perfis` | OSINT | Blackbird, Sherlock | ⭐⭐⭐⭐⭐ |
| `mapeamento de redes` | OSINT | 852 | ⭐⭐⭐⭐ |
| `OSINT username` | OSINT | Blackbird, Maigret | ⭐⭐⭐⭐⭐ |
| `hunt down social media` | OSINT | Sherlock | ⭐⭐⭐⭐ |

### LGPD, Compliance & Privacidade

| Keyword | Categoria | Produto | Contexto Brasil |
|---------|-----------|---------|-----------------|
| `LGPD` | Core | Guard Brasil | Lei Geral de Proteção de Dados |
| `proteção de dados` | Core | Guard Brasil | Compliance LGPD |
| `compliance LGPD` | Core | Guard Brasil | Adequação legal |
| `vazamento de dados` | Core | Guard Brasil | Data breach detection |
| `dados pessoais expostos` | Core | Guard Brasil | Exposição de PII |
| `anonimização` | Core | Guard Brasil | Técnicas de pseudonimização |
| `descarte seguro de dados` | Core | Guard Brasil | Data disposal |
| `privacidade forense` | Core | Guard Brasil | Privacy-preserving forensics |
| `proteção em investigações` | Core | 852, Guard Brasil | LGPD + forense |
| `validação de evidências` | Core | 852 | Chain of custody |
| `evidence integrity` | Core | 852 | Integridade de provas |
| `evidence provenance` | Core | 852 | Proveniência de evidências |

### GovTech & Automação Governamental

| Keyword | Categoria | Produto | Contexto Brasil |
|---------|-----------|---------|-----------------|
| `GovTech` | Core | Eagle Eye | Tecnologia para governo |
| `automação de licitações` | Core | Eagle Eye | Pregão eletrônico |
| `monitoramento de contratos` | Core | Eagle Eye | Acompanhamento contratual |
| `dados abertos` | Core | Eagle Eye | Open data Brasil |
| `transparência pública` | Core | Eagle Eye | Portal da Transparência |
| `diários oficiais` | Core | Eagle Eye | Querido Diário, DOs |
| `pregão eletrônico` | Core | Eagle Eye | Compras governamentais |
| `licitação inteligente` | Core | Eagle Eye | AI em compras públicas |
| `pn.gov.br` | Core | Eagle Eye | Portal Nacional de Contratações |
| `SICAF` | Contexto | Parceiros | Habilitação governamental |
| `dispensa de licitação` | Core | Eagle Eye | Contratação direta |
| `edital de licitação` | Core | Eagle Eye | Oportunidades |
| `pregão presencial` | Core | Eagle Eye | Modalidade tradicional |
| `RDC` | Core | Eagle Eye | Regime Diferenciado de Contratações |

### AI/ML & Agent Frameworks

| Keyword | Categoria | Produto | Contexto |
|---------|-----------|---------|----------|
| `multi-agent framework` | Core | EGOS Kernel | Orquestração de agentes |
| `agent orchestration` | Core | EGOS Kernel | Coordenação de IA |
| `AI governance` | Core | EGOS Kernel | Governança de IA |
| `LLM workflow` | Core | EGOS Kernel | Pipelines de linguagem |
| `LLM pipeline` | Core | EGOS Kernel | Chain of thought |
| `AI agent runtime` | Core | EGOS Kernel | Execução de agentes |
| `agent runtime` | Core | EGOS Kernel | EGOS runner |
| `MCP server` | Core | EGOS Kernel | Model Context Protocol |
| `Model Context Protocol` | Core | EGOS Kernel | Padrão Anthropic |
| `AI observability` | Core | EGOS Kernel | Monitoramento de IA |
| `agent telemetry` | Core | EGOS Kernel | Telemetria de agentes |
| `A2A protocol` | Core | EGOS Kernel | Agent-to-Agent (Google) |

---

## 🇧🇷 Brazilian Context Keywords (Alta Relevância Local)

### Policial & Investigativo

| Keyword | Categoria | Produto | Prioridade |
|---------|-----------|---------|------------|
| `delegacia` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `inquérito policial` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `polícia civil` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `polícia militar` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `PCMG` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `PMMG` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `PCESP` | Contexto | 852 | ⭐⭐⭐⭐ |
| `PMESP` | Contexto | 852 | ⭐⭐⭐⭐ |
| `Polícia Federal` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `PF digital` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `investigação criminal` | Core | 852 | ⭐⭐⭐⭐⭐ |
| `evidência digital` | Core | 852 | ⭐⭐⭐⭐⭐ |
| `perícia criminal` | Core | 852 | ⭐⭐⭐⭐⭐ |
| `laudo pericial` | Core | 852 | ⭐⭐⭐⭐ |
| `IPL` | Contexto | 852 | Inquérito Policial | 
| `boletim de ocorrência` | Contexto | 852 | ⭐⭐⭐⭐ |
| `ocorrência policial` | Contexto | 852 | ⭐⭐⭐⭐ |
| `inteligência policial` | Core | 852 | ⭐⭐⭐⭐⭐ |
| `SISP` | Contexto | GovTech | Sistema de Informações |
| `INFOVIA` | Contexto | GovTech | Rede gov BR |
| `Intelego` | Contexto | PCMG | Sistema policial |
| `Sinesp` | Contexto | Segurança | Sistema nacional |

### Jurídico & Processual

| Keyword | Categoria | Produto | Prioridade |
|---------|-----------|---------|------------|
| `Ministério Público` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `MPMG` | Contexto | 852 | ⭐⭐⭐⭐⭐ |
| `Justiça Federal` | Contexto | Jurídico | ⭐⭐⭐⭐ |
| `TJMG` | Contexto | Jurídico | ⭐⭐⭐⭐ |
| `processo digital` | Core | Jurídico | ⭐⭐⭐⭐ |
| `PJe` | Contexto | Jurídico | Processo Judicial Eletrônico |
| `Escavador` | Ferramenta | Jurídico | ⭐⭐⭐⭐⭐ |
| `Jusbrasil` | Ferramenta | Jurídico | ⭐⭐⭐⭐⭐ |
| `diário oficial` | Contexto | Eagle Eye | ⭐⭐⭐⭐ |
| `DOE` | Contexto | Eagle Eye | Diário Oficial do Estado |
| `DOU` | Contexto | GovTech | Diário Oficial da União |

### Dados Públicos & Transparência Brasil

| Keyword | Categoria | Ferramenta | Prioridade |
|---------|-----------|------------|------------|
| `Brasil.IO` | Ferramenta | Dados | ⭐⭐⭐⭐⭐ |
| `Querido Diário` | Ferramenta | Gov | ⭐⭐⭐⭐⭐ |
| `Portal da Transparência` | Ferramenta | Gov | ⭐⭐⭐⭐⭐ |
| `CNPJ dados abertos` | Ferramenta | Receita | ⭐⭐⭐⭐⭐ |
| `sócios de empresas` | Ferramenta | Brasil.IO | ⭐⭐⭐⭐⭐ |
| `CNPJ consulta` | Ferramenta | Receita | ⭐⭐⭐⭐⭐ |
| `situação cadastral` | Ferramenta | Receita | ⭐⭐⭐⭐⭐ |
| `Receita Federal dados` | Ferramenta | Receita | ⭐⭐⭐⭐⭐ |
| `dados públicos` | Contexto | Gov | ⭐⭐⭐⭐ |
| `informação pública` | Contexto | Gov | ⭐⭐⭐⭐ |
| `LAI` | Contexto | Gov | Lei de Acesso à Informação |
| `solicitação LAI` | Contexto | Gov | ⭐⭐⭐⭐ |

---

## 🚫 Anti-Keywords (Ruído/Filtro Negativo)

### Educação/Cursos (Não são clientes B2B)

| Anti-Keyword | Motivo | Score Impact |
|--------------|--------|--------------|
| `curso de OSINT` | Educação B2C | -40 |
| `aprenda OSINT` | Educação B2C | -40 |
| `mentoria OSINT` | Serviço pessoal | -35 |
| `treinamento` | Genérico | -25 |
| `workshop` | Evento único | -25 |
| `certificação` | Educação | -30 |
| `certificado` | Educação | -30 |
| `aula gratuita` | Lead gen B2C | -45 |
| `ebook gratuito` | Marketing B2C | -40 |
| `download gratuito` | Marketing | -35 |
| `gratuito` + `curso` | Combo educação | -50 |

### Negócios Não-Alinhados

| Anti-Keyword | Motivo | Score Impact |
|--------------|--------|--------------|
| `dropshipping` | Não B2B | -40 |
| `day trade` | Não B2B | -40 |
| `forex` | Não B2B | -40 |
| `mentoria` | Serviço pessoal | -35 |
| `vaga de emprego` | Recrutamento | -40 |
| `estamos contratando` | Recrutamento | -40 |
| `oportunidade de negócio` | MLM/suspeito | -35 |
| `renda extra` | MLM | -45 |
| `ganhe dinheiro` | Scam | -45 |
| `multi-nível` | MLM | -50 |
| `marketing multinível` | MLM | -50 |
| `infoproduto` | B2C não-alinhado | -30 |
| `produto digital` | Genérico B2C | -25 |
| `hotmart` | Plataforma B2C | -30 |
| `monetizze` | Plataforma B2C | -30 |
| `eduzz` | Plataforma B2C | -30 |

### Indicadores de Baixa Prioridade

| Anti-Keyword | Motivo | Score Impact |
|--------------|--------|--------------|
| `_thread_` | Organização | -10 |
| `off-topic` | Ruído | -15 |
| `humor` | Não profissional | -15 |
| `meme` | Não profissional | -15 |
| `cotação` | Financeiro pessoal | -20 |
| `preço do dólar` | Macroeconômico | -15 |
| `notícia` | Genérico | -10 |
| `últimas notícias` | Jornalismo | -15 |
| `urgente` + `notícia` | Clickbait | -25 |

---

## 📊 Scoring Formula

Base Score: 50 pontos

### Bonificadores (Moat Keywords)

| Tipo | Bonus |
|------|-------|
| Tier 1 OSINT keyword encontrado | +20 |
| Tier 1 LGPD/Compliance keyword | +20 |
| Tier 1 GovTech keyword | +18 |
| Tier 1 AI/Agent keyword | +18 |
| Contexto Brasil (policial/jurídico) | +15 |
| Ferramenta específica mencionada | +10 |
| Produto EGOS mencionado diretamente | +25 |

### Penalidades (Anti-Keywords)

| Tipo | Penalty |
|------|---------|
| Anti-keyword de curso/educação | -30 a -50 |
| Anti-keyword de MLM/scam | -40 a -50 |
| Anti-keyword de recrutamento | -40 |
| Genérico/jornalismo | -10 a -20 |

### Thresholds

| Score | Classificação | Ação |
|-------|---------------|------|
| 80-100 | 🟢 **Alta oportunidade** | Alerta imediato Telegram + WhatsApp |
| 60-79 | 🟡 **Oportunidade** | Alerta Telegram |
| 40-59 | ⚪ **Neutro** | Log apenas |
| <40 | 🔴 **Ruído** | Ignorar |

---

## 🔗 Integração com Scripts

### Uso em `x-opportunity-alert.ts`

```typescript
// Moat keywords são usados para:
// 1. Bonus scoring (match em tweet.text)
// 2. Query generation para X API
// 3. Anti-keyword filtering

const MOAT_KEYWORDS = [
  'OSINT', 'inteligência de fontes abertas', 'investigação digital',
  'cibercrime', 'cruzamento de dados', 'forense digital',
  'LGPD', 'proteção de dados', 'compliance LGPD',
  // ... ver arquivo completo
];

const ANTI_KEYWORDS = [
  'curso', 'mentoria', 'dropshipping', 'day trade', 'forex',
  'vaga de emprego', 'estamos contratando', 'renda extra'
  // ... ver arquivo completo
];
```

### Uso em Templates DM

Templates em `X_POSTS_SSOT.md` usam estas keywords para:
- Personalização da mensagem
- Referência a ferramentas específicas (Blackbird, Sherlock, etc.)
- Contexto Brasil (delegacia, inquérito, PCMG)

---

## 📈 Revisão e Atualização

| Frequência | Ação | Responsável |
|------------|------|-------------|
| Semanal | Review de anti-keywords (novos ruídos detectados) | Agent X-COM |
| Mensal | Adição de novos moat keywords (trends) | Gem Hunter |
| Trimestral | Revisão completa de scoring weights | SSOT Auditor |
| Contínuo | Feedback loop de conversões | x-opportunity-alert |

---

*Documento SSOT para X.com Opportunity Alert System. Mantido por EGOS Intelligence.*
