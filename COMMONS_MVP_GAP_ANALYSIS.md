# EGOS Commons — MVP Gap Analysis

> **Data:** 2026-03-31
> **Objetivo:** Mapear o que falta para completar MVP segundo `EGOS_COMMONS_PLANO_COMPLETO.md`
> **Status Atual:** Semana 2 parcialmente implementada

---

## Status Geral

| Semana | Fase | Status | Conclusão |
|--------|------|--------|-----------|
| Semana 1 | Inventário + Taxonomia | ✅ COMPLETO | 100% |
| Semana 2 | Fichas de Produto + Site | 🟡 PARCIAL | 60% |
| Semana 3 | Validação + Automação | ❌ NÃO INICIADO | 0% |

---

## ✅ SEMANA 1: Inventário + Taxonomia (COMPLETO)

### O que existe:
- ✅ `business/inventory.md` com 6 produtos reais
- ✅ Taxonomia de categorias definida
- ✅ Matriz de maturidade (Alpha, Beta, Production)
- ✅ Preços sugeridos para cada produto
- ✅ Split 95/5 calculado para todos

**Validação:** `business/inventory.md` tem 62 linhas, 6 produtos, pricing completo ✓

---

## 🟡 SEMANA 2: Fichas de Produto + Site (60% COMPLETO)

### O que JÁ existe:

#### App Structure ✅
- `/home/enio/egos/apps/commons/` — React 19 + Vite + TypeScript
- Build funcional (485ms, 280KB bundle)
- Routing configurado (react-router-dom v7)
- Supabase client configurado

#### UI Components ✅
- Navbar com navegação funcional
- Hero section com gradiente e badges
- ProductCard component com hover effects
- StatsBar mostrando métricas
- Footer completo

#### Pages Implementadas ✅
- `/` — Home com catálogo de produtos
- `/commons/plano` — CommonsPlanPage (lê commonsContent.ts)
- `/commons/personas-split` — PersonasSplitPage
- `/sandbox/split` — SandboxSplitTester
- `/sandbox/agents` — AgentPlayground
- `/sandbox/atrian` — ATRiANInspector

#### Product Display ✅
- 6 produtos hardcoded em `App.tsx`
- ProductCard com pricing, tags, ratings
- Split details exibidos
- Badges de tier (free/pro/enterprise)
- Featured products filtrados

### O que FALTA:

#### 1. Páginas Individuais de Produto (Fichas) ❌
**Status:** Apenas cards no catálogo, sem página de detalhes

**Necessário:**
- Criar `/produto/:id` route
- Componente `ProductDetailPage.tsx`
- Exibir informações completas:
  - Screenshots/demos
  - Casos de uso
  - Documentação técnica
  - Links para GitHub repo
  - Botão "Implementar" com Mycelium/Ethik flow
  - FAQ por produto

**Esforço:** 4-6 horas

#### 2. Automação inventory.md → products.json ❌
**Status:** Produtos hardcoded em TypeScript

**Necessário:**
- Script `scripts/sync-inventory-to-json.ts`
- Parser de `business/inventory.md` → `apps/commons/public/products.json`
- App.tsx buscar de `/products.json` em vez de array hardcoded
- Pre-commit hook para rodar sync automaticamente

**Esforço:** 2-3 horas

#### 3. Filtros de Categoria Funcionais ⚠️
**Status:** UI existe, mas apenas "all" funciona

**Necessário:**
- Implementar categorias reais em `categories` array
- Mapear produtos por categoria (tool, template, agent, etc)
- Filtro funcional quando clica em categoria

**Esforço:** 1 hora

#### 4. Abas "Grátis / Pago / Contribuir" ❌
**Status:** Todos produtos misturados

**Necessário:**
- Criar 3 views/tabs no catálogo
- **Grátis:** Links diretos para GitHub repos
- **Pago:** Produtos com implementação paga
- **Contribuir:** Como se tornar implementador certificado

**Esforço:** 2-3 horas

---

## ❌ SEMANA 3: Validação + Automação (NÃO INICIADO)

### O que falta:

#### 1. VALIDATION-CHECKLIST.md ❌
**Objetivo:** Checklist de validação para cada produto antes de publicar

**Conteúdo esperado:**
- [ ] Código roda local e em produção
- [ ] Documentação mínima existe (README)
- [ ] Preço testado com 3 potenciais clientes
- [ ] GitHub repo público e organizado
- [ ] Deploy guide validado por implementador externo

**Esforço:** 1 hora

#### 2. 10 Entrevistas com Devs/Empresas ❌
**Status:** Pesquisa de validação não iniciada

**Necessário:**
- Roteiro de entrevista estruturado
- Target: 10 devs/CTOs de software houses
- Perguntas:
  - "Você usaria código open-source governado?"
  - "Pagaria R$2.500+ para implementação profissional?"
  - "O modelo 95/5 faz sentido para você?"
- Consolidar insights em `business/VALIDATION_REPORT.md`

**Esforço:** 8-10 horas (2 horas por entrevista, prep + consolidação)

#### 3. ClawFlows Workflows ❌
**Status:** Automação de governança não implementada

**Workflows necessários:**
- `inventory-sync`: Valida inventory.md sincronizado com products.json
- `nightly-audit`: Checa se todos repos leaf estão acessíveis
- `pricing-drift`: Alerta se preço em inventory.md diverge de App.tsx

**Esforço:** 3-4 horas

#### 4. Pre-commit para business/ ❌
**Status:** Pre-commit atual valida apenas código `.ts`, não markdown business

**Necessário:**
- Adicionar hook que valida `business/*.md`
- Checar:
  - inventory.md tem todos produtos com preços
  - Links de repos GitHub estão válidos
  - Markdown bem formatado

**Esforço:** 1-2 horas

---

## Resumo de Esforço Total para MVP Completo

| Fase | Tarefas | Esforço Total | Prioridade |
|------|---------|---------------|------------|
| Semana 2 (completar) | 4 tarefas pendentes | 9-13 horas | 🔴 ALTA |
| Semana 3 (iniciar) | 4 tarefas pendentes | 13-17 horas | 🟡 MÉDIA |
| **TOTAL MVP** | **8 tarefas** | **22-30 horas** | - |

---

## Estratégia de Parceria com Lara Felix

**Contexto:** User quer delegar comercial/vendas para parceira Lara Felix

**Material necessário para pitch de parceria:**

1. **Commons 1-Pager** ✅ (já existe em `business/inventory.md`)
2. **Demo funcional** 🟡 (site no ar, mas sem fichas de produto)
3. **Proposta de parceria** ❌ FALTA CRIAR

### Proposta de Parceria — Estrutura Sugerida

```markdown
# Proposta de Parceria EGOS Commons

## Você (Lara)
- Prospecção ativa (CTOs, software houses, govtech)
- Fechamento de deals (implementações pagas)
- Relacionamento com cliente (suporte comercial)
- Split: 20% do valor de cada implementação vendida

## Enio (Criador)
- Desenvolvimento contínuo dos produtos
- Suporte técnico para implementadores
- Governança e manutenção do Kernel
- Split: 75% do valor (como implementador principal)

## EGOS Kernel (Ecossistema)
- Split fixo: 5% de todas transações
- Usado para manutenção de infraestrutura
```

**Esforço para criar proposta completa:** 2-3 horas

---

## Próximos Passos Recomendados

### Opção A: Finalizar MVP antes da parceria (3-4 semanas)
1. Completar Semana 2 (9-13h)
2. Executar Semana 3 (13-17h)
3. Fazer 10 entrevistas de validação
4. **Aí sim** apresentar Commons validado para Lara

**Vantagem:** Produto maduro, validado, com tração inicial
**Desvantagem:** Delay no comercial

### Opção B: Parceria paralela ao desenvolvimento (2 semanas)
1. Criar proposta de parceria hoje (2h)
2. Apresentar para Lara com Commons "funcional mas incompleto"
3. Lara começa prospecção enquanto você completa fichas de produto
4. Primeiros clientes ajudam a validar pricing/modelo

**Vantagem:** Receita mais rápida, validação real de mercado
**Desvantagem:** Risco de apresentar produto "cru"

---

## Recomendação Final

**Seguir Opção B — Parceria Paralela**

**Motivo:** User já tem estratégia inbound (publicar e atrair), mas reconhece que precisa de agressividade comercial. Lara pode começar outreach com material atual (inventory.md + site funcional), enquanto fichas de produto são finalizadas em 1-2 semanas.

**Ações imediatas (próximas 4 horas):**
1. ✅ Gap analysis criado (este arquivo)
2. ⏳ Criar proposta de parceria (2h)
3. ⏳ Finalizar fichas de 3 produtos prioritários (Kernel, Carteira-Livre, Guard Brasil) (6h)
4. ⏳ Enviar para Lara com acesso ao site de staging

---

*Documento gerado por Claude Code durante sessão de análise estratégica — 2026-03-31*
