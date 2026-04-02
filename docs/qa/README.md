# QA Automation Notes

Este diretório concentra artefatos de revisão QA.

Relatórios:
- `ANALISE_QA_ULTIMOS_100_COMMITS.md`
- `CODEX_PREFERENCES_VALIDATION_2026-04-01.md`
- `CODEX_GLOBAL_PREFERENCES_V2.md`
- `CODEX_GLOBAL_PREFERENCES_V3.md`
- `PENDING_TASKS_SNAPSHOT_2026-04-02.md`
- `STOPPED_FRONTS_REPORT_2026-04-02.md`
- `SYSTEM_PANORAMA_2026-04-02.md`
- `TELEMETRY_ASYNC_COMMENT_TEMPLATE.md`

## Gerar auditoria rápida dos últimos commits

```bash
python scripts/qa/analyze_commits.py --count 100 --format markdown
```

## Gerar auditoria em arquivo

```bash
mkdir -p docs/qa/_generated
python scripts/qa/analyze_commits.py --count 100 --format markdown > docs/qa/_generated/commit_audit_last100.md
```

Ou usando saída nativa do script:

```bash
python scripts/qa/analyze_commits.py --count 100 --format markdown --output docs/qa/_generated/commit_audit_last100.md
```

## Formato texto (integração scripts)

```bash
python scripts/qa/analyze_commits.py --count 100 --format text
```

## Testes locais (script)

```bash
python -m unittest discover -s tests/qa -p 'test_*.py'
```

## Health check de governança/SSOT

```bash
bun run ssot:check
```

## Teste de telemetria (Bun)

```bash
bun test packages/shared/src/__tests__/telemetry.test.ts
```

## Dashboard de telemetria por logs

```bash
python scripts/qa/telemetry_dashboard.py --input /tmp/agents-telemetry.log --output docs/qa/_generated/telemetry_dashboard.md
```

Smoke fixture (CI/local):

```bash
python scripts/qa/telemetry_dashboard.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-dashboard.md
```

Saída inclui:
- volume por evento/agente/ferramenta
- custo por agente
- eventos lentos (>5s)
- forecast de custo (run-rate diário/mensal) quando timestamps estiverem presentes

## Forecast histórico de custo (7d/30d)

```bash
python scripts/qa/telemetry_forecast.py --input /tmp/agents-telemetry.log --output docs/qa/_generated/telemetry_forecast.md
```

Smoke fixture (CI/local):

```bash
python scripts/qa/telemetry_forecast.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-forecast.md
```

## Artefatos de CI

- Workflow publica `qa-observability-artifacts` com:
  - `/tmp/qa-commit-audit.md`
  - `/tmp/qa-telemetry-dashboard.md`
  - `/tmp/qa-telemetry-forecast.md`
  - `/tmp/qa-pending-tasks.md`
  - `/tmp/qa-stalled-tasks.md`
  - `/tmp/qa-guardrail.txt`
  - `/tmp/qa-evidence.md`
  - `/tmp/qa-ssot-check.md`
  - `/tmp/qa-envelope.json`

## Suite única (local/CI)

```bash
bun run qa:observability
```

> A suíte também gera diagnóstico SSOT em `/tmp/qa-ssot-check.md` via `ssot_check_diagnostic.py`.

## Inventário rápido de pendências

```bash
bun run qa:pending
```

Formato JSON (integrações):

```bash
bun run qa:pending:json
```

## Relatório de frentes paradas

```bash
bun run qa:stalled
```

## Guardrail de risco (latência/custo)

```bash
python scripts/qa/telemetry_guardrail.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-guardrail.txt
```

Thresholds por ambiente (opcional):

```bash
QA_MAX_MONTHLY_USD=50 QA_MAX_OVER5S=5 bun run qa:observability
```

> A suíte também gera diagnóstico SSOT em `/tmp/qa-ssot-check.md` via `ssot_check_diagnostic.py`.

## Evidence summary (telemetry gate)

```bash
bun run qa:evidence
```

Gate estrito (falha se telemetry minimum gate não passar):

```bash
bun run qa:evidence:gate
```

## CI anotação amigável de falha

Quando `qa:observability` falha no CI, o workflow publica no **Job Summary**:

- conteúdo de `/tmp/qa-evidence.md` (quando disponível)
- hint de correção com comandos locais (`qa:observability` e `qa:evidence:gate`)

Isso facilita revisão assíncrona sem abrir artifacts manualmente em todo caso.

## SSOT diagnostic (env drift vs repo drift)

```bash
bun run ssot:diagnostic
```

`/tmp/qa-ssot-check.md` agora inclui seção **Ação recomendada** automática por classificação (`env_drift`, `repo_drift`, `unknown_fail`).

As ações recomendadas no SSOT diagnostic agora vêm com **prioridade, owner sugerido e comando copiável**.

Melhoria contínua anti-regressão: usar `bun run ssot:diagnostic` no fluxo local antes de commit (hook global `~/.egos/hooks/pre-commit`) para detectar `mixed_drift` cedo, sem alterar zonas congeladas do kernel.

Formato JSON (integração):

```bash
bun run ssot:diagnostic:json
```

Envelope único (interconexão para automações):

```bash
bun run qa:compose
```

Validação do envelope (schema mínimo + campos de gate):

```bash
bun run qa:compose:validate
```

Exemplo de validação com frescor estrito:

```bash
python scripts/qa/validate_qa_envelope.py --input /tmp/qa-envelope.json --max-age-minutes 30
```

Validação de coerência entre guardrail e telemetry gate:

```bash
python scripts/qa/validate_qa_envelope.py --input /tmp/qa-envelope.json --max-age-minutes 30 --coherence-mode fail
```

Modo `warn` (não quebra pipeline, apenas sinaliza incoerência):

```bash
python scripts/qa/validate_qa_envelope.py --input /tmp/qa-envelope.json --coherence-mode warn
```

Lista restrita de artifacts versionados: `scripts/qa/artifact_manifest.json` (envelope inválido se `sources` apontar para paths fora da allowlist).

No CI, o upload de artifacts agora usa a lista do manifest (`artifact_manifest.json`) para manter conjunto restrito e evitar drift de paths no workflow.
