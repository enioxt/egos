# QA Automation Notes

Este diretório concentra artefatos de revisão QA.

Relatórios:
- `ANALISE_QA_ULTIMOS_100_COMMITS.md`
- `CODEX_PREFERENCES_VALIDATION_2026-04-01.md`
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

## Suite única (local/CI)

```bash
bun run qa:observability
```

## Guardrail de risco (latência/custo)

```bash
python scripts/qa/telemetry_guardrail.py --input tests/qa/fixtures/sample_telemetry.txt --max-monthly-usd 10 --max-over5s 10
```
