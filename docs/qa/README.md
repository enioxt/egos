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

## Teste de telemetria (Bun)

```bash
bun test packages/shared/src/__tests__/telemetry.test.ts
```
