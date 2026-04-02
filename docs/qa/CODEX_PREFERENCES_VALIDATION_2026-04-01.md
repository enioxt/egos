# Validação QA — Preferências Globais Codex (2026-04-01)

## Resultado rápido

**Status geral:** **parcialmente correto** (boa direção, com ajustes necessários para aderência ao kernel EGOS).

---

## 1) Itens corretos (alinhados)

- Postura investigativa e verificação de evidências antes de concluir.
- SSOT-first: consultar `TASKS.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/SSOT_REGISTRY.md`.
- Foco em risco: drift de governança, versionamento e lacunas de telemetria.
- Colaboração assíncrona por PR/comentários.

---

## 2) Ajustes necessários

### 2.1 Comando de health check

- Preferência proposta: `npm run ssot:check`
- **Status atualizado:** alias `ssot:check` foi adicionado ao `package.json` (aponta para `governance-sync.sh --check`).
- Comandos válidos:
  - `bun run ssot:check`
  - `bun run governance:check`
  - `bun run governance:sync` (dry)

### 2.2 Arquivo `CLAUDE.md` como crítico

- Preferência proposta cita `CLAUDE.md` como arquivo obrigatório.
- Estado real no repo `egos`: **arquivo não encontrado**.
- Recomendação: tratar como opcional/contextual até existir SSOT local formal.

### 2.3 Regra de congelamento muito ampla

- Preferência proposta bloqueia `.guarani/*` inteiro.
- No kernel atual, zona congelada explicitada é mais específica (ex.: `.guarani/orchestration/PIPELINE.md`).
- Recomendação: manter regra estrita por segurança, mas documentar exceções aprovadas por owner para evitar bloqueio operacional desnecessário.

---

## 3) Telemetria — confirmação do gap crítico

A leitura enviada está **correta**: há coleta de API de produto, mas falta visibilidade de runtime de agentes e ferramentas.

### Gap confirmado

- Sem trilha consolidada de execução por agente (duração, custo, volume).
- Sem atribuição de custo/latência por ferramenta.
- Sem heatmap operacional de gargalos ponta-a-ponta.

### Ação aplicada nesta rodada

- `TASKS.md` recebeu backlog `EGOS-TELEM-001..005` (P1 Operacional) após deduplicação.

---

## 4) Recomendação de uso da preferência (versão prática)

- Manter o texto-base proposto.
- Ajustar um ponto operacional no seu template pessoal:
  1. Tratar `CLAUDE.md` como "se existir no repo".

Isso preserva sua intenção (QA rigoroso + governança) sem gerar falsos bloqueios.
