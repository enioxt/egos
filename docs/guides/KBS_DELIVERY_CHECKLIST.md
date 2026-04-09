# KBS Delivery Checklist — Guia de Implementação Replicável

> **Version:** 1.0.0 | **Data:** 2026-04-09
> Para cada novo cliente do serviço EGOS Knowledge Base as a Service.

---

## Fase 0 — Discovery (1–2h)

- [ ] Entrevista inicial (30min): setor, volume de documentos, idioma principal, dores atuais
- [ ] Inventário de fontes: PDFs, planilhas, manuais, e-mails, WhatsApp, áudios?
- [ ] Identificar 3 perguntas que o time faz com frequência (ex: "qual o prazo da NR-12?")
- [ ] Confirmar: quem será o "admin KB" no lado do cliente?
- [ ] Verificar requisitos LGPD: documentos contêm CPF, RG, dados de saúde?
- [ ] Assinar contrato (ver `KBS_CONTRACT_TEMPLATE.md`)

---

## Fase 1 — Setup Técnico (2–4h)

### 1.1 Supabase / Infra
- [ ] Criar tenant isolado (`tenant_id = <slug-cliente>`) em `egos_wiki_pages`
- [ ] Confirmar RLS: `tenant_id = auth.uid()` ou service_role para ingest
- [ ] Testar conectividade: `curl ${SUPABASE_URL}/health`

### 1.2 Claude Code + MCP
- [ ] Instalar Claude Code no máquina do admin: `npm install -g @anthropic-ai/claude-code`
- [ ] Adicionar `@egosbr/knowledge-mcp` ao `.claude/settings.json`:
  ```json
  {
    "mcpServers": {
      "egos-knowledge": {
        "command": "npx",
        "args": ["@egosbr/knowledge-mcp"],
        "env": {
          "EGOS_GATEWAY_URL": "https://gateway.egos.ia.br",
          "SUPABASE_URL": "<url>",
          "SUPABASE_SERVICE_ROLE_KEY": "<key>"
        }
      }
    }
  }
  ```
- [ ] Testar: `/ask o que é guia de entrega KBS?` → deve retornar este documento
- [ ] Configurar Guard Brasil (se cliente tem PII): `GUARD_BRASIL_API_KEY=<key>`

### 1.3 Notion (opcional)
- [ ] Criar workspace Notion dedicado ou pasta isolada
- [ ] Instalar Notion MCP: adicionar ao settings.json conforme `KBS_ONBOARDING_PT_BR.md`
- [ ] Validar OAuth: abrir Claude Code, `/tools` deve listar `notion_*` tools

---

## Fase 2 — Ingestão Inicial (4–8h)

### 2.1 Preparação dos documentos
- [ ] Organizar documentos em pastas por categoria:
  ```
  docs/
  ├── normas/        # NBR, NR, legislação
  ├── processos/     # SOPs, manuais operacionais
  ├── comercial/     # orçamentos, contratos (CUIDADO: PII)
  ├── historico/     # atas, relatórios passados
  └── treinamento/   # materiais de capacitação
  ```
- [ ] Renomear arquivos: sem espaços, sem acentos (ex: `manual-operacao-forno-2024.pdf`)
- [ ] Separar documentos com PII (vão para ingest com Guard Brasil ativo)

### 2.2 Ingest dos documentos
- [ ] Instalar bun: `curl -fsSL https://bun.sh/install | bash`
- [ ] Clonar scripts: `git clone https://github.com/enioxt/egos --depth=1 --sparse`
- [ ] Executar ingest por pasta:
  ```bash
  bun scripts/kb-ingest.ts --dir docs/normas/ --category "norma"
  bun scripts/kb-ingest.ts --dir docs/processos/ --category "processo"
  bun scripts/kb-ingest.ts --dir docs/treinamento/ --category "treinamento"
  ```
- [ ] Verificar resultado: `bun scripts/kb-lint.ts` (deve ter 0 erros)
- [ ] Confirmar no Supabase: `SELECT COUNT(*) FROM egos_wiki_pages WHERE compiled_by='kb-ingest'`

### 2.3 Validação de qualidade
- [ ] Executar 5 queries de validação com perguntas reais do cliente
- [ ] Score médio das respostas ≥ 70? → OK para avançar
- [ ] Score < 70? → Re-ingerir com melhor formatação de documentos

---

## Fase 3 — Treinamento (2–4h)

### 3.1 Workshop com admin KB (2h)
- [ ] Demonstrar: `/ask`, `/search`, `/ingest` no Claude Code
- [ ] Praticar 10 perguntas reais do dia-a-dia
- [ ] Ensinar como adicionar novos documentos:
  ```bash
  bun scripts/kb-ingest.ts --file novo-documento.pdf --category "processo"
  ```
- [ ] Mostrar como detectar documentos desatualizados: `bun scripts/kb-lint.ts --check stale`
- [ ] Entregar guia `docs/guides/KBS_ONBOARDING_PT_BR.md` para referência

### 3.2 Workshop com usuários finais (1h, opcional)
- [ ] Como fazer perguntas eficazes (ser específico, mencionar contexto)
- [ ] O que o KB não faz (não substitui especialista, não cria documentos novos sozinho)
- [ ] Canal de suporte: WhatsApp ou Telegram do EGOS

---

## Fase 4 — Handoff e Go-Live (1h)

- [ ] Configurar cron de re-ingest (semanal recomendado):
  ```bash
  # crontab -e
  0 3 * * 1 bun /path/to/scripts/kb-ingest.ts --dir /docs/ --category "geral"
  ```
- [ ] Documentar: URL do gateway, credenciais Supabase (cofre do cliente)
- [ ] Definir SLA de atualização de documentos (ex: "todo novo processo ingerido em 48h")
- [ ] Criar canal Telegram/WhatsApp para suporte (opcional)
- [ ] Entrega formal: cliente assina termo de aceite
- [ ] Marcar data de check-in em 30 dias

---

## Fase 5 — Acompanhamento (ongoing)

- [ ] Check-in 30 dias: quantas queries/dia? Quais categorias mais usadas?
- [ ] Check-in 90 dias: ROI — qual tarefa ficou mais rápida? Quanto tempo economizado?
- [ ] Avaliar upgrade (Starter → Pro → Enterprise) baseado em volume
- [ ] Renovação de contrato anual com desconto para antecipação

---

## Checklist Rápido — Para Imprimir

```
[ ] Discovery: setor + dores + fontes inventariadas
[ ] Contrato assinado
[ ] Supabase: tenant criado + RLS configurado
[ ] Claude Code + knowledge-mcp instalado + testado
[ ] Documentos organizados por categoria
[ ] Ingest executado: 0 erros no kb-lint
[ ] 5 queries de validação passaram (score ≥ 70)
[ ] Treinamento admin concluído
[ ] Cron de re-ingest configurado
[ ] Termo de aceite assinado
[ ] Check-in 30 dias agendado
```

---

## Estimativas de Tempo por Perfil

| Perfil | Docs | Discovery | Setup | Ingest | Treino | Total |
|--------|------|-----------|-------|--------|--------|-------|
| PME simples (metalurgia) | 50–200 | 1h | 2h | 3h | 2h | 8h |
| Escritório jurídico | 200–500 | 2h | 3h | 6h | 3h | 14h |
| Clínica médica | 100–300 | 2h | 4h | 4h | 3h | 13h |
| Indústria complexa | 500+ | 4h | 4h | 12h | 4h | 24h |

---

*Gerado em: 2026-04-09 | EGOS Knowledge Base as a Service v1.0*
