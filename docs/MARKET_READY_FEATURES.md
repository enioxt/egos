# Features Prontas para Mercado — 2026-03-20

> **Objetivo:** Identificar o que está pronto para apresentar/vender HOJE nos 4 produtos principais

---

## 🚀 Forja — ERP Chat-First para Metalúrgicas

### ✅ Pronto para Piloto
- **Chat API** com LLM multi-provider (Gemini Flash free → qwen-turbo → qwen-plus)
- **Tool Runner** com 4 ferramentas operacionais:
  - `search_products` — busca no catálogo
  - `get_stock_level` — consulta estoque
  - `create_quote` — cria orçamento
  - `get_production_status` — status de produção
- **Tool Calling Integration** — LLM chama ferramentas automaticamente
- **Guardrails** — ATRiAN validation, PII scanning, rate limiting
- **Database** — Supabase PostgreSQL com RLS
- **UI** — 7 telas completas (Login, Painel, Chat, Orçamentos, Materiais, Produção, Clientes, Config)
- **Dados Mock** — Rocha Implementos (20 materiais, 8 clientes, 5 orçamentos)

### 🚧 Pendente para Produção
- [ ] Conectar tools ao banco real (substituir mocks)
- [ ] Auth multi-tenant
- [ ] Streaming SSE
- [ ] Teste end-to-end com cliente real

### 💰 Proposta de Valor
"ERP na conversa. Orçamento, estoque e produção por WhatsApp/Chat."

---

## 🚗 Carteira Livre — Marketplace de Instrutores

### ✅ Pronto para Mercado
- **191 perfis**, **30 instrutores ativos**, **234 API endpoints**
- **Multi-estado** — 27 UFs, IBGE municipalities, CEP progressivo
- **Pagamentos** — Asaas (PIX, Boleto, Cartão) com split automático
- **Partner Dashboard** — `/parceiro` operacional com badges, indicações, PIX
- **KYC** — Upload CNH, credencial DETRAN, foto de perfil
- **WhatsApp** — Evolution API + AI Router (Railway deploy)
- **Admin** — 40+ páginas, observability completa, telemetria
- **Mobile** — Android APK via Capacitor
- **Deploy** — Vercel (auto on push)

### 🚧 Pendente
- [ ] WhatsApp AI Flow teste end-to-end (WHATSAPP-002)
- [ ] UI admin para scan QR WhatsApp self-hosted

### 💰 Proposta de Valor
"Marketplace de instrutores autônomos. Zero comissão, base própria, WhatsApp integrado."

---

## ☕ Santiago — Delivery App para Café

### ✅ Pronto para Mercado
- **Cardápio real** — 38 produtos, 9 categorias, preços reais
- **Carrinho** — zonas de entrega, cupom, Pix/Cartão
- **Admin Dashboard** — toggle delivery, pedidos ativos, métricas
- **Auth** — Supabase (email/senha + Google OAuth)
- **UI/UX** — Mobile-first, PWA-ready
- **Dados reais** — Metre POS (R$5.720/mês, ticket R$44)
- **Admin AI Chatbot** — Qwen Plus tool-calling

### 🚨 Blocker
- **Vercel Deploy** — falhando por falta de env vars Supabase
- **Solução:** Adicionar `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY` no dashboard

### 🚧 Pendente
- [ ] Asaas pagamento (Pix + Cartão)
- [ ] WhatsApp notificações (WAHA)
- [ ] PWA + Capacitor → APK

### 💰 Proposta de Valor
"Delivery próprio. Zero comissão iFood. Base de clientes 100% sua."

---

## 🚔 852 Inteligência — Chatbot Policial

### ✅ Pronto para Mercado
- **46 capabilities** ativas (chat, reports, issues, analytics)
- **ATRiAN** — validação ética em tempo real
- **PII Protection** — mascaramento automático
- **Anonymous Identity** — nicknames policiais
- **Gamification** — ranks (Recruta → Comissário)
- **Reports Sharing** — cross-device via Supabase
- **Issues Board** — GitHub-style voting
- **Admin Dashboard** — telemetria, violations, activity feed
- **Deploy** — managed VPS + Docker + Caddy (`852.egos.ia.br`)

### 🚧 Pendente
- [ ] Piloto ativo com PCMG
- [ ] Apresentação institucional
- [ ] Treinamento de usuários

### 💰 Proposta de Valor
"Chatbot anônimo para inteligência policial. ATRiAN-validated, PII-safe."

---

## 📊 Resumo Executivo

| Produto | Status | Blocker | Próximo Passo |
|---------|--------|---------|---------------|
| **Forja** | MVP 80% | Teste end-to-end | Validar com Rocha Implementos |
| **Carteira Livre** | Produção | WhatsApp flow | Teste completo via WhatsApp |
| **Santiago** | Deploy bloqueado | Env vars Vercel | Adicionar vars + redeploy |
| **852** | Produção | Sem piloto ativo | Apresentar para PCMG |

---

## 🎯 Ação Imediata

1. **Santiago:** Adicionar env vars no Vercel → redeploy → validar
2. **Forja:** Testar chat + tools end-to-end → conectar Supabase real
3. **Carteira Livre:** Simular reserva completa via WhatsApp
4. **852:** Preparar apresentação para PCMG

---

**Conclusão:** Temos 4 produtos com features reais prontas para resolver problemas de hoje. Foco em validação e go-to-market.
