# KBS Discovery Protocol — Levantamento de Dados do Cliente

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **SSOT:** Este arquivo. Usado ANTES de qualquer implementação KBS.
> **Parent:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md`

---

## 0. Objetivo

Protocolo padronizado para descobrir, inventariar e classificar TODAS as fontes de dados de um cliente antes de implementar o Knowledge Base. Cada implementação alimenta e melhora este protocolo.

---

## 1. Entrevista Inicial (30-60min)

### Perguntas obrigatórias

**Fontes de dados:**
- [ ] Onde ficam os documentos principais? (pastas locais, Drive, Dropbox, SharePoint, servidor?)
- [ ] Quais sistemas vocês usam no dia-a-dia? (ERP, CRM, email, WhatsApp, PJe, prontuário?)
- [ ] Quem produz documentos? (quantas pessoas? com que frequência?)
- [ ] Quais formatos predominam? (PDF, Word, planilha, áudio, foto, email?)

**Fluxo de trabalho:**
- [ ] Qual informação você busca com mais frequência? (3 perguntas que faz toda semana)
- [ ] Quanto tempo gasta buscando? (estimativa honesta)
- [ ] Quem mais precisa acessar essa informação? (1 pessoa? equipe? clientes?)

**Dados sensíveis:**
- [ ] Tem CPF, RG, dados de saúde nos documentos? (sim/não por tipo)
- [ ] Tem informações de clientes terceiros? (LGPD art. 7 — base legal?)
- [ ] Algum documento é sigiloso/classificado? (ex: investigações policiais)

**Infraestrutura:**
- [ ] Já usa alguma IA? (ChatGPT, Gemini, Claude, Copilot?)
- [ ] Tem cartão internacional para assinar Claude Pro $20/mês?
- [ ] Tem computador com pelo menos 8GB RAM para rodar Claude Code?
- [ ] Internet estável? (Claude Code precisa de conexão constante)

---

## 2. Inventário de Fontes

Preencher para CADA fonte encontrada:

| # | Fonte | Formato(s) | Volume estimado | Localização | PII? | Prioridade |
|---|-------|-----------|-----------------|-------------|------|------------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |

### Formatos suportados (pipeline atual)

| Formato | Suporte | Ferramenta | Qualidade |
|---------|---------|-----------|-----------|
| `.pdf` | ✅ PRONTO | unpdf | Boa (texto nativo). Ruim em PDFs escaneados |
| `.docx` | ✅ PRONTO | mammoth | Boa |
| `.doc` | ⚠️ PARCIAL | mammoth (fallback) | Média — formato legado |
| `.md` | ✅ PRONTO | fs.readFileSync | Excelente |
| `.txt` | ✅ PRONTO | fs.readFileSync | Excelente |
| `.csv` | ❌ NÃO TEM | Precisa: papaparse ou csv-parse | — |
| `.xlsx` / `.xls` | ❌ NÃO TEM | Precisa: xlsx ou exceljs | — |
| `.xml` | ❌ NÃO TEM | Precisa: fast-xml-parser | — |
| `.json` / `.jsonl` | ❌ NÃO TEM | Precisa: JSON.parse nativo | — |
| `.html` | ❌ NÃO TEM | Precisa: cheerio ou turndown | — |
| `.eml` / `.mbox` | ❌ NÃO TEM | Precisa: mailparser | — |
| `.ogg` / `.mp3` / `.wav` / `.m4a` | ❌ NÃO TEM | Precisa: Whisper API ou whisper.cpp | — |
| `.mp4` / `.webm` | ❌ NÃO TEM | Precisa: ffmpeg (extrair áudio) + Whisper | — |
| `.jpg` / `.png` (scan/foto) | ❌ NÃO TEM | Precisa: Tesseract OCR ou GPT-4 Vision | — |
| `.pptx` | ❌ NÃO TEM | Precisa: pptx2json ou python-pptx | — |
| WhatsApp export (.txt) | ❌ NÃO TEM | Precisa: parser customizado (regex) | — |
| Telegram export (.json) | ❌ NÃO TEM | Precisa: JSON.parse + normalizer | — |

---

## 3. Classificação de Documentos

Após inventariar, classificar cada fonte em:

### Por tipo de conteúdo
- **Normas/Regulamentos** — leis, portarias, NBRs, resoluções, INs
- **Processos/Procedimentos** — SOPs, manuais, protocolos, rotinas
- **Casos/Registros** — processos judiciais, BOs, fichas de atendimento, prontuários
- **Comercial** — contratos, propostas, orçamentos, faturas
- **Comunicação** — emails, WhatsApp, atas de reunião, memorandos
- **Referência** — jurisprudência, artigos, livros, materiais didáticos
- **Dados estruturados** — planilhas, CSV, bases de dados exportadas

### Por sensibilidade LGPD
- **PÚBLICO** — pode indexar sem restrição
- **INTERNO** — pode indexar com acesso controlado
- **SENSÍVEL** — contém PII → Guard Brasil obrigatório no ingest
- **SIGILOSO** — NÃO indexar. Documentar existência sem conteúdo

### Por prioridade de ingestão
- **P0** — documentos que o cliente consulta todo dia
- **P1** — documentos que consulta toda semana
- **P2** — referência que consulta eventualmente
- **P3** — histórico/arquivo (ingerir depois)

---

## 4. Mapa de Sistemas

Documentar todos os sistemas que o cliente usa:

| Sistema | Tipo | Dados que contém | Formato de export | Integração possível |
|---------|------|------------------|-------------------|---------------------|
| Gmail | Email | Correspondência, anexos | EML, API | MCP nativo (Gmail MCP) |
| Google Drive | Storage | Documentos variados | API | MCP nativo (Drive MCP) |
| WhatsApp | Chat | Conversas, áudios, docs | Export .txt, Evolution API | WhatsApp MCP (validado) |
| Notion | Wiki | Notas, databases | API | MCP nativo (Notion MCP) |
| Supabase | DB | Dados estruturados | SQL/API | MCP nativo (Supabase MCP) |
| PJe / e-SAJ | Tribunal | Processos, prazos | — | NÃO (web scraping proibido) |
| Excel/Sheets | Planilha | Dados tabulares | .xlsx/.csv | Precisa ingestor |
| Telegram | Chat | Mensagens, arquivos | Export .json | Precisa ingestor |

---

## 5. Decisão de Arquitetura

Após discovery, decidir:

1. **Quais fontes entram no KB v1?** (priorizar P0 + formatos já suportados)
2. **Quais precisam de conversão?** (ex: áudio → transcrição → texto → KB)
3. **Quais ficam para v2?** (ex: integração com ERP, CRM)
4. **Qual é o tenant_id?** (nome do cliente no Supabase)
5. **Quantos usuários acessam?** (define tier: Starter/Pro/Enterprise)
6. **Guard Brasil é obrigatório?** (se tem PII → sim)

---

## 6. Entregável do Discovery

Ao final do discovery, entregar ao cliente:

1. **Inventário de fontes** (tabela preenchida)
2. **Classificação por tipo + sensibilidade + prioridade**
3. **Mapa de sistemas**
4. **Recomendação de arquitetura** (quais fontes no v1, quais no v2)
5. **Estimativa de tempo e preço** (baseado no perfil da tabela KBS_DELIVERY_CHECKLIST)
6. **Quick wins** — 3 perguntas que o sistema responderá no dia 1

---

## 7. Aprendizados por implementação

Cada implementação adiciona uma entrada aqui:

### Implementação #0 — EGOS (dogfooding, 2026-04)
- Fontes: TASKS.md, HARVEST.md, CAPABILITY_REGISTRY.md, handoffs, agents.json
- Formatos: .md, .json, .ts
- Volume: ~50 docs, ~2900 linhas HARVEST
- PII: baixo (dados internos)
- Resultado: 8→151 wikilinks, 0 quebrados, MOC 56 links
- **Aprendizado:** Obsidian vault como ponte visual funciona muito bem para o cliente "ver" as conexões

### Implementação #1 — Delegacia/DHPP (planejada, 2026-04)
- Fontes: (a preencher no discovery)
- Formatos esperados: PDF (BOs, relatórios), .doc (ofícios), planilhas, fotos, áudios
- PII: ALTO — dados de investigação, CPFs, RGs, nomes
- Guard Brasil: OBRIGATÓRIO
- **Desafio esperado:** áudio de depoimentos (OGG/MP3) precisa de transcrição

---

*Este protocolo é vivo. Cada implementação o melhora.*
