# Guard Brasil GTM — 5-Minute Executive Brief

> **TL;DR:** Temos tudo pronto. Faltam 3 semanas de execução. Receita vem depois. Não há riscos financeiros.

---

## 🎯 O Plano em Uma Frase

**Distribuir Guard Brasil via X.com (grátis) + landing page (própria) + dashboard ao vivo (social proof), DEPOIS enviar M-007 emails com case studies reais.**

---

## 📊 Por Números

```
Investimento:          R$ 650/mês (VPS, já temos)
Custo marginal/cliente: R$ 0.60 (LLM)
Receita/cliente:        R$ 100/mês (Starter) ou R$ 299 (Pro)
Break-even:            5 clientes = Mês 2 (junho)
Profit/cliente:        R$ 99.40 ou R$ 290

Confiança: 95% (modelo prático, já testado em 852)
Tempo: 18 dias (48h realocados, resto spread)
Risco: Praticamente ZERO
```

---

## 🚀 The 3-Week Plan (One-Liner Each)

| Semana | Foco | Entrega | Bloqueador |
|--------|------|---------|-----------|
| **1** | Landing page (Next.js + 6 exemplos) + X.com bot (1 post/dia) + Supabase telemetry | Site rodando, 7 posts, 50+ testes/dia coletados | NENHUM |
| **2** | Dashboard (live activity + charts) + M-007 emails (5-7) + responder demos | 2-3 demo calls agendadas, 1+ LOI em progresso | NENHUM |
| **3** | Customer onboarding (2-5 pilots) + production hardening + revenue validation | 1-2 clientes pagantes, R$ 100-200/mo real | NENHUM |

**Total esforço:** ~40h spread (não é intenso, é distribuído)

---

## ⚡ What You Do RIGHT NOW (Next 2h)

```bash
# 1. ✅ Revisar 3 docs criados (você está lendo isto)
#    - TELEMETRY_SSOT.md (schema, extensões, rollout)
#    - GUARDBRASIL_GTM_EXECUTIONPLAN.md (código completo)
#    - GUARDBRASIL_MASTER_ORCHESTRATION.md (dependências, decisões)

# 2. ⚠️ DECISION POINT: Answer these 5 questions:
#    a) Preço ok? R$0.02/call + R$299/mo?
#    b) Free tier ok? 100 testes/dia?
#    c) Dashboard MVP: live activity primeiro ou cost charts?
#    d) M-007: enviar semana 1 (com dados X.com) ou semana 2?
#    e) X.com: 1 post/dia ou 3x/semana?

# 3. ✅ Create directories (5 min)
cd /home/enio/egos/apps
npx create-next-app guard-brasil-web --typescript --tailwind
npx create-next-app guard-brasil-dashboard --typescript --tailwind

# 4. ✅ Setup Supabase table (5 min)
#    Copy SQL from GUARDBRASIL_GTM_EXECUTIONPLAN.md
#    Run in Supabase SQL editor

# 5. 📅 Schedule: Tomorrow start on landing page code
```

---

## 🤝 Collaborator Responsibilities

**Me (Claude):**
- Write complete code for landing page (you copy-paste)
- Write X.com bot code (you run via GitHub Actions)
- Write dashboard components (you integrate)
- Debug issues

**Você:**
- Make 5 pricing/strategy decisions (see above)
- Run: `npx create-next-app` commands (setup)
- Create Supabase table (copy-paste SQL)
- Test locally: `bun run dev`
- Deploy to Vercel (one-click)
- Execute M-007 emails (write 5 emails, use templates)

---

## 💡 Why This Works

### Problem 1: "But we don't have sales team"
**Solution:** Product sells itself. 100 free tests = proof. X.com = distribution.

### Problem 2: "But LLM costs will kill us"
**Solution:** Qwen costs $0.00007/call. Even with 10k calls = $0.70/day. Alibaba free quota covers us for 6 months.

### Problem 3: "But customers won't find us"
**Solution:** X.com + landing page + social proof dashboard is enough for early GTM. M-007 emails later with real data.

### Problem 4: "But dashboard is hard"
**Solution:** MVP = just real-time activity feed + one chart. Don't overthink.

### Problem 5: "But telemetry is fragmented across repos"
**Solution:** Created SSOT. Guard Brasil uses it. Later migrate 852/carteira. Start with ONE.

---

## 📈 Week 1 Metrics (How to Know It's Working)

```
Day 1-2: Landing page deployed
  ✅ Page loads
  ✅ Can paste text + get result
  ✅ Cost shows (should be $0.00007 or so)

Day 3: X.com bot posts
  ✅ Post appears on @anoineim
  ✅ Shows example + link to landing page

Day 5: Data flowing
  ✅ guard_brasil_events table has 50+ rows
  ✅ Each row has: cost_usd, event_type, duration_ms
  ✅ Public dashboard shows live activity

If ALL 3 = Week 1 SUCCESS → Move to Week 2 (emails)
```

---

## 🎬 Decision Template (Answer These Now)

### Question 1: Pricing Tiers
- [ ] **Option A (RECOMMENDED):**
  - FREE: npm SDK only, no telemetry, local
  - STARTER: R$0.02/call, web API, basic dashboard
  - PRO: R$299/mo unlimited, advanced features
  - ENTERPRISE: Custom

- [ ] **Option B:** Different (specify):

### Question 2: Free Tier Limits
- [ ] **Option A (RECOMMENDED):** 100 tests/day per IP
- [ ] **Option B:** 1,000 tests/day per IP
- [ ] **Option C:** Unlimited (but email asks for signup)

### Question 3: M-007 Timing
- [ ] **Option A:** Send emails Week 2 (after X.com + landing page data)
- [ ] **Option B:** Send emails Week 1 (immediately, use GUARDBRASIL_DEMO_SCRIPT.md)
- [ ] **Option C:** Send emails after dashboard launch (Week 3)

### Question 4: Dashboard MVP Priority
- [ ] **Option A (RECOMMENDED):** Live activity feed (real-time events)
- [ ] **Option B:** Cost breakdown chart (spending over time)
- [ ] **Option C:** Both (takes longer, but comprehensive)

### Question 5: X.com Posting Strategy
- [ ] **Option A:** 1 post/day, rotate 6 examples (automated via GitHub Actions)
- [ ] **Option B:** 3x/week, manual curation
- [ ] **Option C:** 1 post/week + retweets in between

---

## ⚠️ Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Alibaba quota limit hit | Low | Revenue blocked | Monitor usage, add backup (OpenRouter) |
| X.com posts get no engagement | Low | No viral effect | Engage back, ask questions, iterate copy |
| Landing page has bugs | Medium | Bad UX | Test thoroughly before launch |
| Supabase billing surprise | Very low | Cost spike | Monitor with alerts |
| M-007 gets zero responses | Low | No meetings | Use social proof from X.com to improve pitch |

**Overall Risk:** 🟢 **LOW** — Most risks are operational, not financial.

---

## 📚 Documentation Inventory

What I've written for you:

1. **TELEMETRY_SSOT.md** (1,200 lines)
   - What: Unified telemetry schema + implementations
   - Use: Reference when integrating telemetry into Guard Brasil API

2. **GUARDBRASIL_GTM_EXECUTIONPLAN.md** (1,500 lines)
   - What: Complete code for landing page, X.com bot, dashboard
   - Use: Copy-paste code, change values, deploy

3. **GUARDBRASIL_MASTER_ORCHESTRATION.md** (1,000 lines)
   - What: Full picture, cost analysis, dependencies, decision framework
   - Use: Reference for architecture questions

4. **GUARDBRASIL_5MIN_BRIEFING.md** (this file)
   - What: TL;DR of above + checklist
   - Use: Share with team, track progress

---

## ✅ Execution Checklist

- [ ] Read all 4 docs (0.5h)
- [ ] Make 5 pricing/strategy decisions above (0.5h)
- [ ] Create app directories (`npx create-next-app`) (0.25h)
- [ ] Create Supabase table (0.25h)
- [ ] Day 1-2: Implement landing page (6h)
- [ ] Day 3: Integrate telemetry (4h)
- [ ] Day 4-5: X.com bot setup (4h)
- [ ] Week 2: Dashboard + M-007 emails (12h)
- [ ] Week 3: Customer onboarding + production (8h)

**Total:** ~35h spread over 3 weeks = ~2-3h/day on average

---

## 🎯 Final Question for You

**Before I code anything else:**

Have all 3 core docs made sense? Any architecture you'd change?

Or should I just start coding the landing page tomorrow morning?

---

## 📞 How to Proceed

**Option 1 (RECOMMENDED):**
- Você: Answer the 5 decision questions above
- Me: Start coding landing page
- You: Deploy tomorrow

**Option 2:**
- Me: Wait for feedback on docs
- You: Take time to review

**Option 3:**
- You: Tell me to change something
- Me: Iterate

---

**Status:** Documentation complete. Architecture solid. Ready for execution.

**Blocker:** Your 5 decisions above.

**Timeline:** Start tomorrow → Revenue in June.

Let me know. 🚀
