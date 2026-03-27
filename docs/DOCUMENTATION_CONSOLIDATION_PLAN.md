# EGOS Documentation Consolidation Plan

> **Version:** 1.0.0 | **Date:** 2026-03-26
> **Scope:** All EGOS repositories
> **Governance:** EGOS Kernel (`/home/enio/egos`)

---

## 1. Problema

Documentação prolifera sem controle em todos os repositórios EGOS:
- **egos-lab:** 100+ arquivos em docs/, 42 handoffs acumulados
- **br-acc:** 30+ arquivos em múltiplas pastas
- **smartbuscas:** 5 arquivos Cloudflare duplicados
- **852, INPI, policia:** Sem pre-commit (sem proteção contra proliferação)

---

## 2. Solução: Standard EGOS Documentation Structure

Cada repositório deve ter **máximo 4-5 documentos** em `docs/`:

```
docs/
├── SYSTEM_MAP.md          # Capability registry (SSOT)
├── [PRODUCT|MODULE]_SPEC.md  # Especificação principal
├── ARCHITECTURE.md        # Arquitetura técnica (se necessário)
├── _generated/            # Artefatos máquina (inventory, etc.)
└── _archived_handoffs/    # Handoffs >30 dias (auto-archive)
```

**Documentos Permitidos (máximo):**
1. `SYSTEM_MAP.md` — Registry de capabilities
2. `AGENTS.md` (root) — System map para LLMs
3. `PRODUCT_SPEC.md` ou `MODULE_SPEC.md` — Especificação
4. `ARCHITECTURE.md` — Arquitetura técnica (opcional)
5. `HARVEST.md` — Consolidação de conhecimento (opcional)

**Proibido:**
- ❌ `*_2026-*.md` (timestamped)
- ❌ `*AUDIT*.md`, `*DIAGNOSTIC*.md`, `*REPORT*.md` com datas
- ❌ `CHECKLIST_*.md` (use TASKS.md)
- ❌ Handoffs >30 dias em `_current_handoffs/`
- ❌ Pastas aninhadas em `docs/` (analysis/, research/, etc.)

---

## 3. Plano por Repositório

### 🔴 P0 — Critical (Sem Pre-commit + Docs Excessivos)

#### br-acc (EGOS Inteligência)
**Problemas:**
- 30+ arquivos em docs/
- Pastas: analysis/, cases/, diagnostics/, legal/, plans/, pt-BR/, release/, reports/, research/
- Sem pre-commit
- Arquivos duplicados: `fontes-de-dados.md` vs `data-sources.md`

**Ações:**
1. [ ] Instalar pre-commit canônico
2. [ ] Consolidar `fontes-de-dados.md` + `data-sources.md` → `DATA_SOURCES.md`
3. [ ] Mover `analysis/`, `diagnostics/`, `research/` → `_archived_handoffs/2026-03/`
4. [ ] Mover `legal/` → `_archived_handoffs/2026-03/` (ou canonical em egos/docs/)
5. [ ] Consolidar `META_PROMPT_V2.md`, `MERGE_ANALYSIS.md`, `REPORT_STANDARD.md` → `SYSTEM_MAP.md`
6. [ ] Criar `ARCHITECTURE.md` se necessário

**Resultado esperado:** 4-5 arquivos em docs/

---

#### smartbuscas
**Problemas:**
- 5 arquivos Cloudflare duplicados sobre mesmo tema
- Sem pre-commit

**Ações:**
1. [ ] Instalar pre-commit canônico
2. [ ] Consolidar todos `CLOUDFLARE_*.md` → `docs/ARCHITECTURE.md` (seção Cloudflare)
3. [ ] Mover `SMARTBUSCAS_PLANO_COMPLETO.md`, `CLOUDFLARE_INDEX.md` → `_archived_handoffs/`
4. [ ] Manter: `ARCHITECTURE.md`, `PRD.md`, `ROADMAP.md`

**Resultado esperado:** 3-4 arquivos

---

#### 852 (Inteligência Policial)
**Problemas:**
- `_current_handoffs/` acumulando
- `CHATBOT_PRODUCTION_REVERSE_ENGINEERING.md` muito específico
- Sem pre-commit

**Ações:**
1. [ ] Instalar pre-commit canônico
2. [ ] Arquivar handoffs antigos (>30 dias) → `_archived_handoffs/2026-03/`
3. [ ] Consolidar `CHATBOT_PRODUCTION_REVERSE_ENGINEERING.md` + `ROADMAP_INTELIGENCIA_POLICIAL_INTEGRADA.md` → `SYSTEM_MAP.md`
4. [ ] Mover `AUTORESEARCH_TRIGGERS.md`, `gem-hunter/` → `_archived_handoffs/`

**Resultado esperado:** 2-3 arquivos

---

### 🟡 P1 — Medium (Pre-commit Existente mas Fraco)

#### egos-lab
**Problemas:**
- **100+ arquivos** em docs/ — caso mais grave
- 42 handoffs em `_current_handoffs/`
- Dezenas de pastas: agentic/, plans/, research/, stitch/, etc.

**Ações:**
1. [ ] Executar purge completo de docs/
2. [ ] Consolidar tudo em 4 documentos:
   - `docs/SYSTEM_MAP.md` — Capability registry
   - `docs/ARCHITECTURE.md` — Arquitetura do ecossistema
   - `docs/EGOS_ECOSYSTEM_MAP.md` — (já existe, manter)
   - `docs/KNOWLEDGE_ATLAS.md` — (já existe, manter)
3. [ ] Mover **todas** as pastas exceto `_generated/` e `_archived_handoffs/` → `_archived_handoffs/2026-03/`
4. [ ] Arquivar handoffs >30 dias

**Resultado esperado:** 4-5 arquivos + `_archived_handoffs/`

---

### 🟢 P2 — Low (Pre-commit OK, apenas ajustes)

#### forja (✅ Consolidado)
**Status:** Já foi consolidado nesta sessão
- 4 arquivos: SYSTEM_MAP.md, PRODUCT_SPEC.md, ARCHITECTURE.md, VISION_MODULE.md
- Pre-commit existe e funciona
- ✅ Nenhuma ação necessária

#### carteira-livre
**Status:** Pre-commit FAST mode funcional
- Docs mínimo (agora)
- ✅ Apenas garantir que pre-commit está atualizado com versão canônica

#### INPI
**Status:** Docs pequeno, sem pre-commit
**Ações:**
1. [ ] Instalar pre-commit canônico
2. [ ] Consolidar se houver mais de 5 arquivos

#### policia
**Status:** Docs mínimo, sem pre-commit
**Ações:**
1. [ ] Instalar pre-commit canônico
2. [ ] Manter estrutura atual (já está enxuta)

---

## 4. Implementação do Pre-Commit Canônico

### Script de Instalação

```bash
#!/bin/bash
# install-egos-precommit.sh
# Instala pre-commit canônico em todos os repos EGOS

REPOS="br-acc 852 smartbuscas INPI policia egos-lab"

for repo in $REPOS; do
  if [ -d "/home/enio/$repo" ]; then
    echo "Installing pre-commit in $repo..."
    
    # Create .husky if needed
    mkdir -p "/home/enio/$repo/.husky"
    
    # Copy canonical pre-commit
    cp /home/enio/egos/.guarani/templates/pre-commit-canonical.sh \
       "/home/enio/$repo/.husky/pre-commit"
    
    chmod +x "/home/enio/$repo/.husky/pre-commit"
    
    echo "✅ $repo done"
  fi
done
```

### Comando para Ativar Husky (se necessário)

```bash
cd /home/enio/[repo]
npx husky-init && npm install
# ou para Bun:
bunx husky-init && bun install
```

---

## 5. Métricas de Sucesso

| Métrica | Antes | Depois | Target |
|---------|-------|--------|--------|
| Total docs em todos repos | 200+ | <30 | 80% redução |
| Repos sem pre-commit | 5 | 0 | 100% cobertura |
| Handoffs acumulados | 50+ | <10 | Archive >30 dias |
| Pastas aninhadas em docs/ | 30+ | 0 | Flat structure |

---

## 6. Manutenção Contínua

### Mensal
- `egos-gov check` em todos repos
- Archive handoffs >30 dias
- Verificar SYSTEM_MAP.md freshness

### Por Commit
- Pre-commit canônico bloqueia automaticamente
- Não permitir bypass exceto com `--no-verify` + justificativa

---

## 7. Checklist de Execução

- [ ] Instalar pre-commit em br-acc, 852, smartbuscas, INPI, policia
- [ ] Consolidar docs em br-acc (30 → 5 arquivos)
- [ ] Consolidar docs em smartbuscas (15 → 4 arquivos)
- [ ] Consolidar docs em 852 (10 → 3 arquivos)
- [ ] Purge completo egos-lab/docs (100 → 5 arquivos)
- [ ] Atualizar pre-commit em forja e carteira-livre (versão canônica)
- [ ] Documentar no HARVEST.md do kernel
- [ ] Disseminar para todos agents via `/disseminate`

---

*"Documentação é conhecimento fossilizado. Atualize o SSOT, não crie monumentos."*
