# QA de Código — Análise dos últimos 100 commits

**Data da análise:** 2026-04-01  
**Escopo:** repositório `egos` (`git log -n 100`)  
**Objetivo:** revisão de qualidade por blocos/repositórios, com sugestões de melhoria (sem execução de mudanças funcionais)

---

## 0) Escopo QA (claro e sem mudanças drásticas)

### Dentro do escopo

- Revisar histórico recente e identificar risco técnico/operacional.
- Conectar evidências (hotspots/churn) com melhorias pequenas e incrementais.
- Propor checklist objetivo para PRs futuros (gates e contratos).

### Fora do escopo

- Reescrever arquitetura do framework.
- Alterar zonas congeladas (`agents/runtime/runner.ts`, `agents/runtime/event-bus.ts`, hooks críticos).
- Introduzir breaking changes sem validação de compatibilidade.

### Princípio de execução

- **Mudança mínima com ganho máximo:** priorizar automação de validação antes de refactors amplos.

---

## 1) Metodologia

- Leitura do histórico recente (`git log --oneline -n 100`).
- Classificação por tipo de commit (`feat`, `docs`, `chore`, `fix`, `other`).
- Mapeamento de churn por área (top-level paths) e por arquivo.
- Leitura qualitativa dos temas recorrentes no histórico (governança, Guard Brasil, runtime, integrações).

> Nota QA: não existe metadado de “push” diretamente no histórico Git local padrão.
> Nesta análise, usei os commits locais/disponíveis como proxy confiável da atividade recente.

---

## 2) Resumo executivo

### 2.1 Distribuição por tipo (100 commits)

- `feat`: **51%** (alta velocidade de entrega)
- `docs`: **29%** (forte documentação e governança)
- `chore`: **14%** (manutenção operacional)
- `fix`: **4%** (baixo volume explícito de correção)
- `other`: **2%**

### 2.2 Concentração temporal

- 2026-03-29: 13 commits
- 2026-03-30: 43 commits
- 2026-03-31: 30 commits
- 2026-04-01: 14 commits

**Leitura QA:** pico de produtividade em janelas curtas (sprints intensos), com risco de regressão silenciosa se a cobertura de testes não acompanhar o ritmo.

### 2.3 Hotspots de mudança

- Áreas com maior churn: `docs/`, `packages/`, `apps/`, `TASKS.md`, `.guarani/`, `agents/`, `scripts/`.
- Arquivos mais tocados:
  - `TASKS.md` (43)
  - `docs/knowledge/HARVEST.md` (14)
  - `docs/CAPABILITY_REGISTRY.md` (8)
  - `MANUAL_ACTIONS.md` (7)
  - `agents/registry/agents.json` (6)

**Leitura QA:** excelente maturidade documental; porém há risco de desalinhamento entre “estado declarado” e “estado executável” se gates automáticos não bloquearem divergências.

---

## 3) Análise por blocos (repo/componentes)

## 3.1 Governança e SSOT (`.guarani/`, `docs/`, `TASKS.md`)

### Pontos fortes

- Governança ativa e versionada (regras, pipeline, disseminação, handoffs).
- Cultura de rastreabilidade forte (HARVEST, CAPABILITY_REGISTRY, TASKS).

### Riscos detectados

- **Risco de drift documental:** muitas atualizações manuais, especialmente em arquivos centrais.
- **Risco de acoplamento de processo:** fluxo pode depender demais de disciplina humana para sincronizar estados.

### Melhorias sugeridas

1. Criar **gate automático de consistência SSOT** no CI:
   - validar links/refs obrigatórias entre `TASKS.md`, `docs/SSOT_REGISTRY.md` e `docs/CAPABILITY_REGISTRY.md`;
   - falhar pipeline em divergência.
2. Adicionar **checksum de seção crítica** para detectar alteração sem revisão QA.
3. Introduzir **score de frescor documental** (ex.: arquivo crítico sem atualização > X dias gera alerta).

---

## 3.2 Núcleo de agentes (`agents/`, `agents/registry/agents.json`)

### Pontos fortes

- Registry tratado como SSOT e com manutenção frequente.
- Evidência de melhorias em ID normalization e coordenação de agentes.

### Riscos detectados

- **Risco de regressão semântica em registry:** mudanças frequentes em IDs e metadados podem quebrar integrações downstream.
- **Risco de compatibilidade reversa:** alterações de naming convention podem impactar scripts legados.

### Melhorias sugeridas

1. Criar **validador de compatibilidade** do registry (snapshot + diff semântico).
2. Exigir **contract tests** para comandos que dependem de `agents.json`.
3. Gerar changelog automático “breaking/non-breaking” por alteração de agente.

---

## 3.3 Pacotes compartilhados (`packages/shared`, `packages/core`, `packages/*`)

### Pontos fortes

- Evolução consistente em capacidades transversais (LLM routing, event bus, segurança, compatibilidade).
- Separação por pacotes favorece manutenção modular.

### Riscos detectados

- **Risco de integração cruzada:** mudanças em shared podem ter blast radius elevado.
- **Risco de cobertura:** ritmo alto de `feat` com baixo volume relativo de `fix` pode mascarar dívida técnica latente.

### Melhorias sugeridas

1. Adotar **matriz mínima de testes por pacote** (unit + contract + smoke).
2. Ativar **changesets/semver guard** com bloqueio de release sem nota de impacto.
3. Definir **SLO de estabilidade** para pacotes críticos (erro em smoke < X%).

---

## 3.4 Apps/API e superfícies de produto (`apps/api`, `apps/guard-brasil-web`, `packages/guard-brasil`)

### Pontos fortes

- Entregas rápidas para monetização e superfície API/MCP.
- Evolução visível de produto (padrões PII, roadmap e deploys).

### Riscos detectados

- **Risco de inconsistência versão/código** (já houve commit específico de bump de strings de versão).
- **Risco de segurança de dados sensíveis:** domínio exige validações contínuas sobre PII masking.

### Melhorias sugeridas

1. Criar **check automático de versionamento** (package/app/server em lockstep).
2. Adicionar **testes de segurança focados em PII** (casos positivos/negativos, edge cases BR).
3. Incluir **smoke de MCP/API** por PR (rotas críticas + contratos).

---

## 3.5 Integrações e distribuição (`integrations/`, manifests, bundles)

### Pontos fortes

- Framework de contratos definido e gate de validação mencionado no processo.

### Riscos detectados

- **Risco de “pronto no papel”** sem prova runtime repetível por integração.

### Melhorias sugeridas

1. Exigir evidência de execução (logs curtos + comando) em PR de integração.
2. Publicar **matriz de prontidão por adaptador** (contract OK, auth OK, smoke OK, distribuição OK).

---

## 4) Matriz de conexão (evidência -> ação recomendada)

| Evidência observada | Risco associado | Ação incremental sugerida |
|---|---|---|
| Alto churn em `TASKS.md` e docs centrais | Drift documental | Gate SSOT + validação de referências |
| Alterações frequentes em `agents/registry/agents.json` | Quebra de compatibilidade | Diff semântico + contract tests |
| Muitas `feat` vs poucas `fix` | Dívida técnica silenciosa | Smoke obrigatório + metas mínimas de cobertura |
| Commit de correção de versão em API | Drift de versionamento | Check automático de versão em CI |
| Crescimento de integrações | “Ready” sem prova runtime | Matriz de prontidão com evidências |

---

## 5) Protocolo de comunicação para outros agentes (PR/Handoff)

Para cada PR com impacto em governança/registry/integrações, incluir bloco padrão:

```md
### QA-Handoff
- Escopo: [arquivos/áreas tocadas]
- Risco: [baixo/médio/alto] + motivo
- Compatibilidade: [breaking/non-breaking] + evidência
- Checks executados: [comandos]
- Pendências explícitas: [itens]
- Próximo agente responsável: [nome/id]
```

**Objetivo:** reduzir ambiguidade entre agentes e manter rastreabilidade operacional sem mudanças drásticas de processo.

---

## 6) Priorização QA (ordem recomendada)

### P0 (imediato)

1. Gate de consistência SSOT + validação semântica de `agents.json`.
2. Smoke obrigatório para API/MCP/integrações por PR.
3. Check de versionamento automático para evitar drift de versão.

### P1 (curto prazo)

1. Contract tests nos pacotes de maior blast radius (`shared`, `core`, `registry`).
2. Score de frescor documental e alertas automáticos.

### P2 (médio prazo)

1. Dashboard QA com métricas: churn, taxa de falha de checks, tempo de correção.
2. Geração automática de changelog por impacto (breaking/non-breaking).

---

## 7) Conclusão QA

O repositório mostra **alta cadência de evolução** e boa disciplina de governança, com forte documentação e estratégia de SSOT. O principal risco atual não parece ser “falta de entrega”, e sim **sincronização confiável entre documentação, registry e comportamento executável** em um contexto de mudanças muito frequentes.

**Recomendação central:** transformar a qualidade já existente em **gates automatizados obrigatórios**, reduzindo dependência de validação manual e protegendo o ritmo de entrega.
