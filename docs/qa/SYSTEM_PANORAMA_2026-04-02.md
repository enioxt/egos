# EGOS System Panorama — 2026-04-02

## 1) Estado atual (visão executiva)

- Kernel de governança ativo com SSOT central em `TASKS.md`, `docs/CAPABILITY_REGISTRY.md` e `docs/SSOT_REGISTRY.md`.
- Trilha de observabilidade QA operacional (`qa:observability`) com dashboard, forecast e guardrail de custo/latência.
- Guard Brasil API com endpoint de contrato runtime (`GET /v1/meta`) e endpoint principal de inspeção (`POST /v1/inspect`).
- Principal bloqueio técnico transversal no momento: qualidade de ambiente/toolchain (`typecheck` ainda com falhas amplas fora do escopo de uma única task).

## 2) Sinais de risco atuais

1. **Drift de ambiente home (`~/.egos`)**
   - `ssot:check` falha neste ambiente por ausência de sync home/kernel.
2. **Typecheck global degradado**
   - Vários erros transversais em scripts/agents impedem gate TS verde fim-a-fim.
3. **Backlog amplo em P1/P2**
   - Itens de monetização (EGOS-163/164) e observabilidade de integração (OBS-010+) seguem pendentes.

## 3) Plano recomendado

### Curto prazo (0-7 dias)

1. **Estabilizar gates de execução**
   - Isolar/fixar baseline de `typecheck` para voltar a verde contínuo.
2. **Fechar lacunas de observabilidade operacional**
   - Consolidar EGOS-TELEM-001/002 com persistência e atribuição completas.
3. **Proteger revisão de governança**
   - Manter auditoria de commits com alertas de frozen zones + artifacts em CI.

### Médio prazo (1-4 semanas)

1. **Monetização Guard Brasil**
   - EGOS-163 (Pix billing) + EGOS-164 (dashboard real de eventos).
2. **Observabilidade de hooks/runtime**
   - OBS-010/011/013 com telemetria preservando privacidade.
3. **Padronização de contratos de API**
   - Expandir padrão de endpoint-meta/contract para serviços críticos.

### Longo prazo (1-3 meses)

1. **Maturidade de governança cross-repo**
   - Redução de drift estrutural e rollout consistente de SSOT pointers.
2. **Camada de decisão orientada por custo/latência**
   - Guardrails e dashboards alimentando priorização automática de rota/modelo.
3. **Pipeline de entrega com risco previsível**
   - PR gates com sinais de congelamento, drift e regressão de observabilidade como padrão.

## 4) Próximas prioridades objetivas (ordem)

1. `EGOS-163` — Pix billing integration.
2. `EGOS-164` — dashboard com dados reais de `guard_brasil_events`.
3. `OBS-010` — hooks -> spans (OTel).
4. `EGOS-TELEM-001/002` — fechamento de persistência/atribuição fim-a-fim.

## 5) Regra operacional para não conflitar com trabalho paralelo

- Evitar mexer em frozen zones.
- Priorizar mudanças incrementais de baixo acoplamento (QA scripts, docs SSOT, endpoints aditivos).
- Registrar toda decisão em artifacts e TASKS para colaboração assíncrona sem sobreposição.
