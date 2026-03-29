# 🎯 FORJA — P0/P1 FOCUS (O Que REALMENTE Importa Agora)

**Data:** 2026-03-23 | **Objetivo:** Clareza brutal sobre prioridades | **Público:** Time Forja + Reunião Quarta

---

## 🚨 CONTEXTO CRÍTICO (O que você precisa saber)

### A DOR RESOLVIDA
**Metalúrgicas/Oficinas** estão presas em:
- Excel desorganizado (estoque, preços, orçamentos em abas diferentes)
- E-mails com informações espalhadas (sem classificação, sem histórico)
- Orçamentos manuais (cálculo fiscal incorreto, demora 2-3 horas)
- Sem rastreabilidade (quem fez o quê? quando?)
- Sem acesso remoto (precisam estar no escritório/fábrica)

**Forja resolve:**
- Chat conversacional que EXECUTA operações (não só responde)
- Orçamento em 30s (com fiscal correto)
- E-mail automático → WhatsApp (urgência clara)
- Auditoria completa (trilha)
- Mobile + Web (trabalha de qualquer lugar)

### O OBJETIVO ESTRATÉGICO
**Fase 1 (Agora - Abril):** MVP operacional com Rocha Implementos
- Chat → Tools operacionais funcionando
- E-mail integrado → WhatsApp triage
- Orçamento rápido com fiscal

**Fase 2 (Maio):** Dashboard admin + automações
**Fase 3 (Junho):** Produto comercializável

### A STACK (Simplificada)
```
Frontend: Next.js 15 (Vercel) → Chat PWA + Dashboard
Backend: Next.js API Routes + FastAPI (future)
Database: Supabase PostgreSQL + RLS
LLM: Gemini 2.0 Flash (cheap) + Qwen fallback
Real-time: SSE + WebSockets
Mobile: Capacitor (Android APK)
Integrations: WhatsApp (Evolution API), Gmail/M365, Whisper
```

---

## 🎯 P0 TASKS (BLOCKING — Sem isso, não funciona)

### **FORJA-003: Auth Multi-Tenant + RLS** ⬛ CRITICAL NOW

**Estado:** Não iniciada
**Por quê importa:** Sem auth, qualquer um vê dados de qualquer cliente. Impossível demonstrar no piloto Rocha.

**O que fazer:**
1. ✅ Schema RLS já existe (FORJA-001B)
2. ⏳ **Implementar Supabase Auth (GoTrue)**
   - Botão "Entrar com Google" ou Magic Link
   - JWT token no cookie
   - 1-2 dias

3. ⏳ **Adicionar RLS Policies** em ALL tables
   ```sql
   -- Exemplo: usuário só vê dados do seu tenant
   CREATE POLICY tenant_isolation ON messages
   USING (tenant_id = auth.jwt() ->> 'tenant_id');
   ```
   - 4 horas (copiar padrão)

4. ⏳ **Testar com Rocha como tenant #1**
   - Login → Rocha vê só dados de Rocha
   - Criar teste com 2 tenants (Rocha + fake)
   - 2 horas

**Impacto:** Sem isso, não consegue mostrar multi-tenancy real para Rocha (vão pensar que é mock).

**Esforço:** 1-2 dias (um dev)

---

### **FORJA-020: WhatsApp Integration (Evolution API)** ⬛ CRITICAL NOW

**Estado:** Não iniciada (mas temos Evolution API em carteira-livre)
**Por quê importa:** WhatsApp é como Rocha recebe informações urgentes. Sem isso, Forja é só um app — com WhatsApp, é um assistente 24/7 com relevância real.

**O que fazer:**
1. ✅ Reuse `carteira-livre/services/whatsapp/evolution-api.ts`
   - Já está pronta, só copiar

2. ⏳ **Criar endpoint `/api/notifications/whatsapp`**
   - Quando algo acontece (email chegou, orçamento falhou, estoque baixo)
   - Chama Evolution API
   - Envia mensagem + botões/links
   - 2 horas

3. ⏳ **Integrar E-mail Pipeline → WhatsApp**
   - E-mail chega → LLM classifica (urgência) → WhatsApp envia
   - Exemplo: "URGENTE: Cliente Acme pediu orçamento | [Ir para Chat]"
   - 3 horas

4. ⏳ **Testar com Rocha**
   - Enviar teste WhatsApp com número real
   - Verificar formatting, links, velocidade
   - 1 hora

**Impacto:** Com isso, Rocha usa Forja 24/7 (recebe alertas no WhatsApp). Sem isso, é só um app que abrem quando lembram.

**Esforço:** 6-8 horas (um dev)

---

### **FORJA-019B: Email Pipeline → LLM Classification** ⬛ CRITICAL NOW

**Estado:** Documentado, não implementado
**Por quê importa:** 60% da dor do Rocha é "onde foi esse e-mail?" + "qual é o status?". Email classif. + WhatsApp resolve isso.

**O que fazer:**
1. ✅ Schema `emails` já existe (FORJA-001B migration)

2. ⏳ **Criar Gmail Connector**
   - OAuth2 setup (user clicks "Connect Gmail")
   - Fetch last 30 days de emails
   - Store no Supabase com `status = RECEIVED`
   - 4 horas

3. ⏳ **LLM Classification**
   - Cada email → Gemini Flash classifica:
     - Tipo: Orçamento? Pedido? Suporte? Fiscal?
     - Urgência: alta/normal/baixa
     - Cliente: extract CN PJ
   - Update `emails.classification`
   - 3 horas

4. ⏳ **Notification trigger**
   - Se urgência=alta → WhatsApp em 1 minuto
   - Se tipo=orçamento → notifica operacional
   - 2 horas

5. ⏳ **E-mail search + reply suggestion**
   - Chat: "Qual era o status do e-mail de Acme?"
   - Tool finds email → LLM suggests resposta → user confirma
   - 3 horas

**Impacto:** Sem isso, Forja é "mais um app". Com isso, Forja é "o lugar onde as coisas acontecem" (emails chegam, acoes sao triadas, operacional atua).

**Esforço:** 12-16 horas (um dev, 2 dias)

---

### **FORJA-004D: PRD + ICP + Go-to-Market Canônico** ⬛ CRITICAL FOR ROCHA

**Estado:** Não iniciada
**Por quê importa:** Reunião quarta com Rocha. Sem PRD claro, vai parecer que você não sabe o que está vendendo.

**O que fazer:**
1. ⏳ **1-page PRD:**
   ```
   FORJA — Assistente Operacional para Metal/Agro
   
   ICP: Metalúrgicas/Oficinas com <50 pessoas
   Dor: Dados espalhados (Excel), e-mail caótico, sem rastreabilidade
   Solução: Chat que EXECUTA + Email triage + Orçamento rápido
   
   Piloto: Rocha Implementos (2-3 meses)
   Métrica de sucesso:
     - Operacional usa Forja 5+ vezes/dia
     - 50% redução em tempo de orçamento (2h → 30min)
     - 100% de e-mails triados em <5 min via WhatsApp
   
   Pacote inicial:
     - Setup: R$5k
     - Mensal: R$3k (5 usuários)
     - Suporte: Incluído
   ```
   - 2 horas

2. ⏳ **Critérios de sucesso piloto:**
   - Chat responde 10 perguntas operacionais com acurácia >90%
   - Orçamento PDF gerado em <1 minuto
   - 3 e-mails/dia classificados automaticamente
   - 0 security breaches (RLS funciona)
   - Rocha usa >10 horas/mês

3. ⏳ **Roadmap para Rocha:**
   - Fase 1 (Abril): Chat + Email triage
   - Fase 2 (Maio): Dashboard + Reports agendados
   - Fase 3 (Junho): Mobile Android

**Impacto:** Com PRD, Rocha entende o que está comprando. Sem, parece vago.

**Esforço:** 3-4 horas (1 dev + product thinking)

---

## 🔴 P1 TASKS (HIGH PRIORITY — Needed Within 2 Weeks)

### **FORJA-004B: Design System Chão de Fábrica** 🔴 IMPORTANT FOR UX

**Estado:** Não iniciada
**Por quê importa:** Operário com mão grande + pouca visão → botões devem ser 64px, fonte 18px+. Sem isso, ninguém usa no chão de fábrica.

**O que fazer:**
1. ⏳ **Tailwind overrides:**
   - Button: `min-h-16 min-w-16` (64px) + `text-lg` (18px)
   - Form input: `h-16 text-lg`
   - Spacing: `gap-4` minimum (não `gap-2`)

2. ⏳ **"Modo Oficina":**
   - Dark mode + AA/AAA contrast
   - Sans-serif bold (não thin)
   - Max 2 options por tela (não 5)

3. ⏳ **Mobile-first Bottom Navigation:**
   - Chat, Dashboard, Settings tabs at bottom
   - No menu hamburger (hard to tap)

4. ⏳ **Zero blind spots:**
   - Todos os botões clicáveis (não texto clicável)
   - Feedback visual ao clicar (cor + som)

**Impacto:** Com design certo, Rocha consegue usar. Sem, operários reclamam "interface pequena".

**Esforço:** 8-12 horas (1 frontend dev)

---

### **FORJA-031: Coolify Setup + Docker Compose** 🔴 INFRA CRITICAL

**Estado:** Não iniciada
**Por quê importa:** Vercel custa $20-850/mês escalando. Coolify = $36/mês fixo. Rocha não vai pagar $500+/mês em infraestrutura.

**O que fazer:**
1. ⏳ **SSH into Contabo VPS (217.216.95.126)**
   - Já existe, só login

2. ⏳ **Install Coolify**
   - Single command, takes 5 minutes

3. ⏳ **Docker Compose:**
   ```yaml
   services:
     next:
       image: node:20
       build: ./apps/forja
       ports: 3000
     postgres:
       image: postgres:15
       volumes: [pgdata:/var/lib/postgresql/data]
     redis:
       image: redis:7
   ```
   - 2 hours

4. ⏳ **Test deployment:**
   - Push to git → Coolify auto-deploys
   - Verify: https://forja.yourco.com

**Impacto:** Sem infraestrutura barata, não consegue sustentar Forja economicamente.

**Esforço:** 6-8 horas (1 devops/senior dev)

---

### **FORJA-041: LGPD Compliance** 🔴 LEGAL REQUIREMENT

**Estado:** Não iniciada
**Por quê importa:** Rocha vende para Brasil. LGPD é lei. Sem compliance, pode levar multa.

**O que fazer:**
1. ⏳ **Terms + Privacy Policy:**
   - Dados do cliente: retenção 1 ano após desativação
   - E-mails: retenção 90 dias após leitura
   - Direito de exportação / exclusão
   - 2 horas (legal review depois)

2. ⏳ **PII Masking:**
   - CPF/CNPJ: show only last 4 digits em default view
   - Reuse `src/lib/chat/safety.ts` PII scanner
   - 2 hours

3. ⏳ **Data Export + Deletion:**
   - User requests → export JSON de seus dados
   - Admin console → delete tenant (cascade delete)
   - 4 hours

**Impacto:** Sem compliance, Rocha não assina contrato.

**Esforço:** 8-10 horas (1 dev + legal)

---

### **FORJA-050: KPIs Dashboard** 🔴 BUSINESS METRICS

**Estado:** Não iniciada
**Por quê importa:** Sem métricas, não sabe se está funcionando. Rocha quer saber: "Quantas vezes foi usado?" "Qual custo IA?"

**O que fazer:**
1. ⏳ **Admin dashboard queries:**
   ```sql
   SELECT COUNT(*) as chat_messages FROM messages WHERE created_at > now() - interval '30 days';
   SELECT SUM(tokens_used * cost_per_token) as cost FROM llm_calls;
   SELECT AVG(response_time) FROM llm_calls WHERE model = 'gemini-flash';
   ```

2. ⏳ **Real-time metrics:**
   - Messages/day
   - Tool success rate
   - LLM cost/month by model
   - Average response time

3. ⏳ **Dashboard page:**
   - 4 KPI cards + chart
   - Filtro por date range
   - 4 hours

**Impacto:** Sem métricas, Rocha não sabe se está tendo ROI.

**Esforço:** 6-8 horas (1 dev)

---

## 📊 ROADMAP REALISTA (GANTT SIMPLIFICADO)

```
SEMANA 1 (Mar 24-30) — BLOCKER PHASE
├─ FORJA-003 (Auth + RLS)          [████████████░░] 80% Dev
├─ FORJA-020 (WhatsApp)            [████████░░░░░░] 60% Dev
└─ FORJA-019B (Email Pipeline)     [████░░░░░░░░░░] 40% Research

SEMANA 2 (Mar 31 - Apr 6) — INTEGRATION PHASE
├─ FORJA-003 finish               [████████████░░] Testing
├─ FORJA-020 finish               [████████████░░] Testing
├─ FORJA-019B finish              [████████████░░] Testing
└─ FORJA-004B (Design System)      [████████░░░░░░] Dev

SEMANA 3 (Apr 7-13) — HARDENING PHASE
├─ FORJA-004D (PRD + ICP)           [████████████░░] Done
├─ FORJA-031 (Coolify)              [████████░░░░░░] Dev
├─ FORJA-041 (LGPD)                 [████░░░░░░░░░░] Dev
└─ FORJA-050 (KPIs)                 [████░░░░░░░░░░] Dev

SEMANA 4 (Apr 14-20) — ROCHA PILOT START
├─ ALL P0s                          [██████████████] ✅ Done
├─ Rocha training                   [████░░░░░░░░░░] Live
└─ Iterate based on feedback        [████░░░░░░░░░░] In progress
```

---

## 💡 WHAT TO TELL ROCHA (WEDNESDAY)

**"Aqui está o que vai entregar em Abril:"**

### MVP Feature Set
1. **Chat Conversacional** com 4 ferramentas operacionais
   - "Qual estoque de aço 304?" → resposta em 2s
   - "Crie orçamento para Acme" → PDF em 30s
   - "Status do pedido?" → Rastreado com auditoria

2. **E-mail Inteligente**
   - Gmail conectado automaticamente
   - Cada e-mail → classificado (urgência, tipo)
   - Urgentes → notificação WhatsApp em <5 min

3. **Orçamento Rápido**
   - Chat: "Orçamento 10 kg aço inox 304?"
   - Sistema calcula: material + MOD + ICMS/IBS
   - PDF pronto em 30 segundos

4. **Auditoria 100%**
   - Quem fez o quê, quando
   - Rastreado em cada ferramenta
   - Só um usuário/tenant vê seus dados

### Números que importam
- **Chat accuracy:** >90% nas 10 operações core
- **Orçamento speed:** 30s vs 2 horas (4x mais rápido)
- **E-mail triage:** 100% de e-mails classificados
- **Cost:** R$3k/mês (5 usuários) + R$5k setup

### Timeline
- **Abril:** MVP + Piloto com Rocha
- **Maio:** Dashboard + Automações
- **Junho:** Pronto para vender

---

## 🎯 ALLOCATION (WHO DOES WHAT)

| Task | Dev | Effort | Start |
|------|-----|--------|-------|
| FORJA-003 (Auth) | Dev 1 | 2d | Today |
| FORJA-020 (WhatsApp) | Dev 2 | 1d | Today |
| FORJA-019B (Email) | Dev 1+2 | 2d | Mar 26 |
| FORJA-004B (Design) | Frontend Dev | 1.5d | Mar 26 |
| FORJA-004D (PRD) | Product | 0.5d | Today |
| FORJA-031 (Coolify) | DevOps | 1d | Mar 31 |
| FORJA-041 (LGPD) | Dev + Legal | 1.5d | Mar 31 |
| FORJA-050 (KPIs) | Dev 1 | 1d | Apr 7 |

**Total:** 4 devs, 11 days = ready for pilot by Apr 15

---

## ⚠️ RISKS & MITIGATION

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| RLS not working → data leak | HIGH | Daily tests with 2+ tenants |
| E-mail connector fails → data loss | HIGH | Webhook retry + dead-letter queue |
| WhatsApp API down → no notifications | MEDIUM | SMS fallback + in-app notification |
| LLM cost higher than expected | MEDIUM | Use Gemini Flash (cheapest), hard caps |
| Rocha doesn't adopt → churn | HIGH | Weekly check-ins, ask what's missing |

---

## ✅ SUCCESS CRITERIA (For April 15 Demo)

- [ ] Rocha logins → sees own data only (RLS works)
- [ ] Chat → 5 questions answered correctly (>90% accuracy)
- [ ] Orçamento → PDF generated in <1 minute
- [ ] Email → Gmail connected, 3+ emails classified + WhatsApp notified
- [ ] No security issues (penetration test pass)
- [ ] Mobile APK boots on Android phone
- [ ] KPIs dashboard shows usage correctly

If ALL are YES = Ready to expand to Phase 2.

---

**FOCUS:** Do these P0s + P1s first. Ignore everything else until mid-April.

**NEXT STEP:** Reunião quarta — confirm with Rocha que isso é o que querem.

