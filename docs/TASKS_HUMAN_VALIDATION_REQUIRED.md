# Tasks Pendentes — Validação Humana vs Autônomas

> **Data:** 2026-03-20
> **Objetivo:** Separar tasks que dependem de ação humana vs tasks autônomas

---

## 🔴 DEPENDEM DE VALIDAÇÃO/CONFIGURAÇÃO HUMANA

### Santiago (P0 — BLOCKER)
**Task:** Adicionar env vars no Vercel
**Ação Humana:** Autorizar Cascade a executar:
```bash
cd /home/enio/santiago
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Valor: https://cwqwtgwuwqaihjrcsdtf.supabase.co

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Valor: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cXd0Z3d1d3FhaWhqcmNzZHRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4ODM1OTAsImV4cCI6MjA4OTQ1OTU5MH0.RbkgfCyYpt4ItFMHa4qUzQLW1ybdHURRGL2kQugo3-I

vercel --prod  # trigger redeploy
```
**Impacto:** App offline, não pode ir pro mercado
**Status:** Aguardando autorização

---

### Forja (P0 — MVP)
**Task:** Testar chat + tool calling end-to-end
**Ação Humana:** 
1. Abrir https://forja-orpin.vercel.app
2. Testar chat com perguntas que acionem tools:
   - "Busque produtos de aço"
   - "Qual o estoque de chapa 3mm?"
   - "Crie um orçamento para cliente X"
3. Validar se tools são chamados e retornam dados
**Impacto:** MVP não validado, não pode apresentar ao piloto
**Status:** Aguardando teste manual

---

### Forja (P1)
**Task:** Conectar tools ao Supabase real (substituir mocks)
**Ação Humana:** Decidir estrutura de dados real:
- Tabela `products` — quais campos?
- Tabela `stock` — como rastrear?
- Tabela `quotes` — workflow de aprovação?
**Impacto:** Tools retornam dados mockados
**Status:** Aguardando definição de schema

---

### Carteira Livre (P1)
**Task:** Testar WhatsApp AI Flow end-to-end (WHATSAPP-002)
**Ação Humana:**
1. Enviar mensagem WhatsApp para número configurado
2. Simular: "Quero agendar aula em Patos de Minas"
3. Validar se IA extrai CEP, busca instrutores, oferece agendamento
4. Validar se PIX é gerado via Asaas
**Impacto:** Canal principal não validado
**Status:** Aguardando teste manual

---

### 852 (P1)
**Task:** Preparar apresentação para PCMG
**Ação Humana:**
1. Revisar proposta HTML (`/home/enio/852/docs/proposta/v4_plano_completo_corrigido.html`)
2. Agendar reunião com comando da PCMG
3. Apresentar sistema funcionando (852.egos.ia.br)
**Impacto:** Produto pronto mas sem tração
**Status:** Aguardando agendamento

---

### Carteira Livre (P2)
**Task:** Remover alias `../egos` do tsconfig (START-HARDENING-001)
**Ação Humana:** Decidir se mantém ou remove dependência do kernel
**Impacto:** Build portátil comprometido
**Status:** Aguardando decisão arquitetural

---

## 🟢 POSSO EXECUTAR AUTONOMAMENTE

### Forja (P0)
**Task:** Atualizar AGENTS.md com capabilities reais
**Ação:** Consolidar Tool Runner + Tool Calling no AGENTS.md
**Impacto:** Documentação desatualizada
**Status:** Pronto para executar

---

### Forja (P1)
**Task:** Implementar Streaming SSE para frontend
**Ação:** Adicionar streaming no `/api/chat/route.ts`
**Impacto:** UX melhorada (resposta em tempo real)
**Status:** Pronto para executar

---

### Egos (P1)
**Task:** Adicionar regra sobre Vercel CLI access no .windsurfrules
**Ação:** Documentar que Cascade tem acesso ao Vercel CLI
**Impacto:** Regras incompletas
**Status:** Pronto para executar

---

### Carteira Livre (P2)
**Task:** Criar AI Usage Dashboard (`/admin/ai-usage`)
**Ação:** Página admin com tokens, cost, latency, errors
**Impacto:** Observabilidade AI incompleta
**Status:** Pronto para executar

---

### Egos-Lab (P2)
**Task:** Consolidar gem-hunter dailies (LAB-ARCHIVE-001)
**Ação:** Criar summaries mensais, arquivar >30 dias
**Impacto:** 8 arquivos duplicados
**Status:** Pronto para executar (baixa prioridade)

---

## 📋 RESUMO

| Categoria | Count | Exemplos |
|-----------|-------|----------|
| **Validação Humana** | 6 | Santiago env vars, Forja teste, WhatsApp teste, 852 apresentação |
| **Autônomas** | 5 | AGENTS.md update, Streaming SSE, Vercel CLI rules, AI dashboard |

---

## 🎯 RECOMENDAÇÃO

**Prioridade 1 (Hoje):**
1. Autorizar Cascade a configurar Santiago no Vercel → desbloqueia deploy
2. Testar Forja chat manualmente → valida MVP

**Prioridade 2 (Esta Semana):**
3. Testar WhatsApp flow Carteira Livre → valida canal principal
4. Agendar apresentação 852 PCMG → gera tração

**Enquanto isso, Cascade executa autonomamente:**
- Atualizar AGENTS.md do Forja
- Adicionar regra Vercel CLI
- Implementar Streaming SSE (se aprovado)

---

**Status:** Aguardando autorização para tasks P0
