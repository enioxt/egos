# FORJA — KBS Namespace Config
# tenant_id: forja
# Versão: 1.0.0 — 2026-04-08
# SSOT: packages/knowledge-mcp/templates/sectors/industrial-forja.md

---

## Namespace

```
tenant_id:  forja
table:      egos_wiki_pages   (filtered by tenant_id = 'forja')
sources:    /home/enio/forja/docs/kb-pilot/**
template:   packages/knowledge-mcp/templates/sectors/industrial-forja.md
rules:      /home/enio/forja/.guarani/forja-rules.md
```

## Pilot Scope (10 docs)

Indexados via `bun agents/agents/wiki-compiler.ts --compile --tenant=forja`:

| File | Category | Description |
|------|----------|-------------|
| `orcamento-bc-007-lote50.md` | entity | Orçamento aprovado bucha BC-007, 50 pcs |
| `orcamento-sup-012-lote20.md` | entity | Orçamento suporte SUP-012, 20 pcs |
| `ficha-bc-007.md` | entity | Ficha técnica bucha BC-007 (SAE 1045) |
| `ficha-sup-012.md` | entity | Ficha técnica suporte SUP-012 (aço carbono) |
| `fornecedores-aco.md` | entity | Fornecedores de aço com histórico de prazo |
| `ata-reuniao-2026-04-01.md` | synthesis | Ata reunião produção — itens de ação |
| `historico-clientes.md` | entity | Histórico clientes: aprovação/reprovação |
| `norma-abnt-nbr-6672.md` | pattern | NBR 6672 — tolerâncias usinagem |
| `custos-processo-tornearia.md` | pattern | Custos hora/máquina tornearia CNC |
| `plano-manutencao-maquinas.md` | how-to | Manutenção preventiva torno CNC 3x/ano |

## Compilar

```bash
bun agents/agents/wiki-compiler.ts --compile --tenant=forja --dry
bun agents/agents/wiki-compiler.ts --compile --tenant=forja
bun agents/agents/wiki-compiler.ts --lint   --tenant=forja
bun agents/agents/wiki-compiler.ts --index  --tenant=forja
```

## Expandir

Adicionar docs em `/home/enio/forja/docs/kb-pilot/` e re-compilar.
Para ingestão de PDFs e áudios: FORJA-TOOLS-001/002 (backlog P1).
