# Integration Master Plan — Intelink + BR-ACC + EGOS Inteligência

> **Version:** 1.0.0 | **Created:** 2026-04-09  
> **Status:** EXECUTIVE DRAFT — Awaiting decision on P0 items  
> **Sacred Code:** 000.111.369.963.1618

---

## 🎯 Escopo Confirmado (Investigação Completa)

A integração **NÃO é merge de codebases**. É arquitetura em **5 camadas** com contratos de dados:

| Camada | Sistema | Função | Status Real |
|--------|---------|--------|-------------|
| **1 — Intake** | `852` | Relatos, PII, sanitização | ✅ **100% operacional** |
| **2 — Triagem** | `852` + painel | Consolidação, priorização | 🟡 **Parcial** |
| **3 — Operação** | `/home/enio/policia` | Mídia, OVM, REDS, formal | ✅ **Isolado, funcional** |
| **4 — Fusão** | `Intelink` (egos-inteligencia) | Grafo, vínculos, cross-case | 🟡 **Backend 100%, Frontend 10%** |
| **5 — OSINT** | `BR-ACC` | Dados públicos, enriquecimento | 🔴 **ETL parado 70%** |

**Fonte canônica:** `/home/enio/852/docs/ROADMAP_INTELIGENCIA_POLICIAL_INTEGRADA.md`

---

## 🔴 P0 — Blockers Imediatos (Escolha Obrigatória)

### P0-1: ETL BR-ACC — Decisão Crítica

| Opção | Descrição | Esforço | Impacto |
|-------|-----------|---------|---------|
| **A) Retomar** | Corrigir run_id, completar Fase 3 (17.4M/24.6M) | 2-4h | 🟢 Completa 77M entidades |
| **B) Importar Snapshot** | Exportar BR-ACC, importar em EGOS-Inteligência | 4-8h | 🟡 Preserva dados, novo schema |
| **C) Desativar** | Usar BR-ACC como-read-only, novo ETL no Intelink | 1-2 dias | 🔴 Perde 77M, recomeça do zero |

**Recomendação:** Opção A — Fix já existe localmente, falta apenas deploy.

**Evidência:**
```
TASKS.md TASK-001: "Local fix já aplicado (06/03/2026): linking_hooks.py, runner.py"
VPS Check: "egos-inteligencia-etl.service: Unit could not be found"
VPS Check: "Nenhum processo ETL rodando"
```

---

### P0-2: Frontend EGOS-Inteligência — Decisão Arquitetural

| Opção | Descrição | Esforço | Trade-offs |
|-------|-----------|---------|------------|
| **A) Reimplementar** | Criar 134 componentes do zero | 3-4 meses | 🟢 Controle total, 🟡 Alto custo |
| **B) Portar do 852** | Adaptar chat UI do 852 para Intelink | 1-2 meses | 🟢 Proven, 🟡 Redesign necessário |
| **C) Reduzir Escopo** | 20 componentes core (login, search, graph, report) | 2-3 semanas | 🟢 Rápido, 🟡 Menos features |

**Recomendação:** Opção B — 852 tem chat UI completa, ATRiAN, PII scanner, export PDF/DOCX.

**Componentes-chave do 852 para portar:**
- `ChatInputArea.tsx` — streaming + abort
- `MessageList.tsx` + `MarkdownMessage.tsx` — renderização
- `ReportReview.tsx` — 3-step PII + AI review
- `ExportMenu.tsx` — PDF/DOCX/MD + WhatsApp
- `Sidebar.tsx` — histórico + navegação

---

### P0-3: Neo4j Canonical — Evitar Duplicação

**Problema:** 2 Neo4j (BR-ACC com 77M, EGOS-Inteligência vazio)

| Opção | Solução |
|-------|---------|
| **A) BR-ACC = Canonical** | EGOS-Inteligência conecta ao BR-ACC Neo4j via read-only |
| **B) EGOS-Inteligência = Canonical** | Migrar 77M para novo cluster (downtime + risco) |
| **C) Federado** | BR-ACC = histórico, EGOS-Inteligência = ativo (complexo) |

**Recomendação:** Opção A — BR-ACC tem 77M + performance tuning, Intelink consome via API.

---

## 📋 Contrato de Dados — 5 Camadas

```yaml
# Schema de integração proposto
interfaces:
  camada_1_to_2:
    from: 852-intake
    to: 852-triagem
    schema:
      relato_id: uuid
      categoria: enum[fiscalizacao,operacional,infra]
      urgencia: 1-5
      pii_mascarado: boolean
      origem: enum[chat,sugestao,upload]
      timestamp: iso8601

  camada_2_to_3:
    from: triagem
    to: policia
    schema:
      caso_id: uuid
      autorizacao: hash_masp
      material_sensivel: boolean
      status: enum[aprovado,rejeitado,pendente]

  camada_2_to_4:
    from: triagem
    to: intelink
    schema:
      entidade_tipo: enum[pessoa,empresa,veiculo,telefone,local]
      entidade_id: uuid
      propriedades: map
      fonte: enum[intake_publico,triagem_institucional]

  camada_4_to_5:
    from: intelink
    to: bracc-osint
    schema:
      cnpj: masked_cnpj
      nome: string
      request_id: uuid
      proposito: enum[enriquecimento,anomalia,cross_ref]
```

---

## 🔍 Tasks Fantasmas Auditadas

| Task | Onde Listada | Status Real | Ação |
|------|--------------|-------------|------|
| **ETL fix run_id** | TASK-001 [ ] | ✅ **Código corrigido 06/03**, não fez deploy | Marcar como [x] com nota |
| **Neo4j scripts** | TASK-002 [x] | ⚠️ Criados mas **não aplicados** (esperam ETL) | Adicionar sub-task "apply post-etl" |
| **Frontend 134 components** | Commits/documentação | 🔴 **14 existentes** (10%) | Reality check completo |
| **PII scanner** | 852 ✅ / Intelink ❌ | 🟡 Duplicação não documentada | Criar task de sync |
| **GDS Algorithms** | TASK-005 [ ] | 🔴 Bloqueado por TASK-001, TASK-002 | Corrigir dependências |

---

## ⚡ Plano de Execução Imediata (24-48h)

### Fase 1 — Desbloquear ETL (4-6h)

```bash
# 1. Conectar ao VPS
ssh root@204.168.217.125

# 2. Verificar fix local
ls -la /opt/egos_inteligencia/etl/src/egos_inteligencia_etl/linking_hooks.py

# 3. Se fix existe, reiniciar ETL manualmente
cd /opt/egos_inteligencia
docker compose -f infra/docker-compose.yml restart etl

# 4. Ou reexecutar com tmux
tmux new -s etl-fase3
cd /opt/egos_inteligencia/etl && python -m egos_inteligencia_etl.runner --phase 3
```

### Fase 2 — Deploy EGOS-Inteligência (2-4h)

```bash
# Configurar secrets GitHub (manual)
# Hetzner: HETZNER_TOKEN, HETZNER_SSH_KEY
# Cloudflare: CLOUDFLARE_TOKEN, CLOUDFLARE_ZONE_ID

# Deploy Terraform + Ansible
cd /home/enio/egos-inteligencia/infra/terraform
git pull origin main
cp terraform.tfvars.example terraform.tfvars  # editar
terraform init
terraform apply

# Ansible
ansible-playbook -i ansible/inventory/production ansible/playbook.yml
```

### Fase 3 — Sincronizar PII Scanner (1-2h)

```bash
# 1. Diff entre 852 e kernel
diff /home/enio/852/src/lib/pii-scanner.ts /home/enio/egos/packages/shared/src/pii-scanner.ts

# 2. Se 852 tem features novas, portar para kernel
cp /home/enio/852/src/lib/pii-scanner.ts /home/enio/egos/packages/shared/src/pii-scanner.ts

# 3. Atualizar 852 para usar kernel
cd /home/enio/852
# Atualizar imports: from '@/lib/pii-scanner' → from '@egos/shared/pii-scanner'
```

---

## 📊 Dashboard de Status Real (VPS)

```
Container              Status        Dados/Progresso
─────────────────────────────────────────────────────────
bracc-neo4j            ✅ Healthy    77M+ entidades
infra-api-1            ✅ Healthy    25 routers ativos
infra-frontend-1       ✅ Healthy    14/134 componentes
infra-redis-1          ✅ Healthy    50% cache hit
852-app                ✅ Healthy    100% operacional
egos-inteligencia-etl  🔴 Missing    70% completo, PARADO
─────────────────────────────────────────────────────────
Serviço systemd        🔴 Inactive   Não registrado
Processo tmux          🔴 Inativo    Último erro: run_id
```

---

## 🎯 Decisões Pendentes (Próximos 24h)

| Decisão | Dono | Opção Recomendada |
|---------|------|-------------------|
| ETL BR-ACC | @enioxt | **A) Retomar** — Fix existe, deploy pendente |
| Frontend | @enioxt | **B) Portar do 852** — 1-2 meses vs 3-4 |
| Neo4j Canonical | @enioxt | **A) BR-ACC = Master** — 77M preservados |
| PII Sync | Cascade | Kernel ← 852, 852 → kernel import |

---

## 📁 Documentos de Referência

| Documento | Caminho | Status |
|-----------|---------|--------|
| Arquitetura 5 Camadas | `/home/enio/852/docs/ROADMAP_INTELIGENCIA_POLICIAL_INTEGRADA.md` | ✅ Canônico |
| TASKS BR-ACC | `/home/enio/br-acc/TASKS.md` | 🟡 Reality check aplicado |
| TASKS 852 | `/home/enio/852/TASKS.md` | ✅ Atualizado 2026-04-08 |
| SSOT Registry | `/home/enio/egos/docs/SSOT_REGISTRY.md` | ✅ Kernel canonical |
| HARVEST Patterns | `/home/enio/egos/docs/knowledge/HARVEST.md` | ✅ Knowledge base |

---

## ✅ Checklist de Validação (Próximos Passos)

- [ ] Decisão P0-1: ETL (A/B/C)
- [ ] Decisão P0-2: Frontend (A/B/C)
- [ ] Decisão P0-3: Neo4j Canonical (A/B/C)
- [ ] Executar ETL fix no VPS (se Opção A)
- [ ] Configurar GitHub secrets (se deploy)
- [ ] Criar branch `integration/port-852-ui` (se Opção B)
- [ ] Atualizar TASKS.md com decisões

---

*Part of the EGOS Framework · Kernel Canonical*
