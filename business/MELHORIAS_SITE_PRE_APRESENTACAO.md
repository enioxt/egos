# Melhorias no Site — Antes da Apresentação para Lara

> **Status Atual:** Commons rodando local (localhost:3099), MVP 100% completo
> **Objetivo:** Deixar site pronto para demo profissional

---

## 🔴 CRÍTICO (Fazer ANTES da apresentação)

### 1. Deploy em Produção
**O que:** Colocar Commons no ar em commons.egos.ia.br
**Por quê:** Demo em localhost passa impressão amadora, URL pública é mais profissional
**Como:**
```bash
# Opção A: Deploy Hetzner (recomendado)
cd /home/enio/egos/apps/commons
bun run build
docker build -t egos-commons .
docker run -d -p 3099:80 --name egos-commons egos-commons

# Configurar Caddy
# Adicionar em /etc/caddy/Caddyfile:
# commons.egos.ia.br {
#     reverse_proxy localhost:3099
# }
# systemctl reload caddy

# Opção B: Vercel (mais rápido, 5 min)
npm i -g vercel
vercel --prod
# Conectar domínio commons.egos.ia.br
```
**Tempo:** 15-30 min (Hetzner) ou 5 min (Vercel)
**Bloqueante?** ⚠️ Não bloqueante (pode fazer demo em localhost), mas MUITO recomendado

---

## 🟡 IMPORTANTE (Fazer se tiver tempo, <2h)

### 2. CTAs Funcionais
**O que:** Botões "Adquirir" levam a formulário de contato real
**Por quê:** Atualmente apenas emitem eventos no console (não funcional para usuário)
**Como:**
```tsx
// Em App.tsx, função handleAction:
const handleAction = async (e: React.MouseEvent) => {
  e.stopPropagation();
  // Opção A: Redirect para Calendly
  window.location.href = 'https://calendly.com/egos/implementacao'

  // Opção B: Abrir modal com formulário
  // setShowContactModal(true)

  // Opção C: Enviar para Typeform
  window.open('https://form.typeform.com/to/XXXXX')
}
```
**Tempo:** 1-2h
**Bloqueante?** ❌ Não bloqueante (Lara pode anotar interesse manualmente na call)

### 3. Informações de Contato Visíveis
**O que:** Footer com email/telefone/LinkedIn EGOS
**Por quê:** Lara vai querer passar contato aos prospects
**Como:**
```tsx
// Em Footer component, adicionar:
<div style={{ marginTop: 16, color: '#64748b' }}>
  <a href="mailto:contato@egos.ia.br">contato@egos.ia.br</a>
  {' | '}
  <a href="https://linkedin.com/company/egos">LinkedIn</a>
  {' | '}
  <a href="https://github.com/eniocc">GitHub</a>
</div>
```
**Tempo:** 15 min
**Bloqueante?** ❌ Não bloqueante (pode passar contato verbalmente)

### 4. Badge "Em Desenvolvimento" ou "Preview"
**O que:** Banner discreto no topo indicando que é versão preview
**Por quê:** Gerencia expectativas (se algo não funcionar 100%)
**Como:**
```tsx
// Em App.tsx, logo após <Navbar>:
<div style={{
  background: 'rgba(251, 191, 36, 0.1)',
  borderBottom: '1px solid rgba(251, 191, 36, 0.3)',
  padding: '8px 24px',
  textAlign: 'center',
  fontSize: 13,
  color: '#fbbf24'
}}>
  ⚠️ Preview — Em validação com primeiros clientes
</div>
```
**Tempo:** 10 min
**Bloqueante?** ❌ Não bloqueante (mas passa transparência)

---

## 🟢 NICE-TO-HAVE (Fazer DEPOIS da apresentação)

### 5. Screenshots Reais dos Produtos
**O que:** Adicionar 1-2 screenshots em cada ProductDetailPage
**Por quê:** Atualmente só tem specs de texto, visual ajuda a vender
**Como:**
- Tirar screenshots de cada produto rodando
- Salvar em `apps/commons/public/screenshots/`
- Adicionar section de imagens em ProductDetailPage
**Tempo:** 2-3h
**Bloqueante?** ❌ Não bloqueante (nice-to-have, não urgente)

### 6. Vídeo Demo (2 min)
**O que:** Loom de 2 min navegando no Commons
**Por quê:** Lara pode enviar aos prospects que não querem call
**Como:**
- Gravar tela com loom.com
- Roteiro: Homepage → Produto → Ficha → Pricing → Contribuir
- Embedar no Commons ou enviar link separado
**Tempo:** 30 min
**Bloqueante?** ❌ Não bloqueante (post-apresentação)

### 7. Deck em PDF
**O que:** Versão PDF da apresentação com screenshots
**Por quê:** Alguns prospects preferem PDF a demo ao vivo
**Como:**
- Usar Canva ou Figma
- 10-15 slides: Problema → Solução → Produtos → Pricing → CTA
- Exportar PDF
**Tempo:** 2-3h
**Bloqueante?** ❌ Não bloqueante (temos .md que pode virar PDF depois)

### 8. Analytics (Google/Plausible)
**O que:** Tracking de visitantes e conversões
**Por quê:** Entender quantos prospects visitam, quais produtos interessam
**Como:**
```html
<!-- Em index.html, antes de </head>: -->
<script defer data-domain="commons.egos.ia.br" src="https://plausible.io/js/script.js"></script>
```
**Tempo:** 15 min
**Bloqueante?** ❌ Não bloqueante (útil mas não urgente)

---

## ✅ O Que JÁ Está BOM (Não Precisa Mexer)

- ✅ Design profissional (dark mode, gradientes, spacing)
- ✅ Responsivo mobile (testado)
- ✅ Performance (305KB JS, <1s load)
- ✅ SEO básico (meta tags, title, description)
- ✅ UX intuitiva (abas, filtros, navegação clara)
- ✅ Content completo (6 produtos bem descritos)
- ✅ Split explicado (transparência no pricing)

---

## 🎯 Priorização Recomendada

### Se você tem 30 min:
1. ✅ Deploy em Vercel (5 min)
2. ✅ Adicionar contatos no footer (15 min)
3. ✅ Badge "Preview" no topo (10 min)

### Se você tem 2h:
1. ✅ Deploy em Vercel (5 min)
2. ✅ CTAs funcionais (Calendly ou Typeform) (1h)
3. ✅ Contatos + Badge (25 min)
4. ✅ Testar end-to-end (30 min)

### Se você tem 1 dia:
1. ✅ Deploy Hetzner (30 min)
2. ✅ CTAs funcionais (1h)
3. ✅ Screenshots de 3 produtos principais (2h)
4. ✅ Vídeo demo (30 min)
5. ✅ Contatos, badge, analytics (1h)
6. ✅ Testar + ajustes (2h)

---

## 🚦 Recomendação Final

### Cenário A: Apresentação HOJE/AMANHÃ
**Fazer:**
- Deploy Vercel (5 min) — passa profissionalismo
- Badge "Preview" (10 min) — gerencia expectativas
- Contatos no footer (15 min) — facilita follow-up

**Total:** 30 min
**Demo:** Pode apresentar com confiança

### Cenário B: Apresentação PRÓXIMA SEMANA
**Fazer:**
- Deploy Hetzner (30 min)
- CTAs funcionais (1h)
- Screenshots de Kernel + Carteira + 852 (2h)
- Vídeo demo (30 min)
- Badge + Contatos + Analytics (1h)

**Total:** 5h
**Demo:** Produto polished, zero fricção

### Cenário C: Apresentação MÊS QUE VEM
**Fazer:** Tudo acima + deck PDF + landing page otimizada + CRM integrado
**Total:** 15-20h
**Demo:** Produto production-grade

---

## 🔧 Como Executar (Se Escolher Deploy Vercel Rápido)

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Build production
cd /home/enio/egos/apps/commons
bun run build

# 3. Deploy
vercel --prod

# 4. Configurar domínio (no dashboard Vercel)
# Domains → Add → commons.egos.ia.br
# Copiar DNS records para registro.br

# 5. Testar
curl -I https://commons.egos.ia.br
```

**Tempo total:** 5-10 min
**Custo:** R$ 0 (plano free Vercel)

---

## ✨ Status Ideal Para Apresentação

| Métrica | Mínimo Aceitável | Ideal |
|---------|------------------|-------|
| **Deploy** | localhost:3099 | commons.egos.ia.br |
| **CTAs** | Console logs | Formulário real |
| **Contato** | Verbal na call | Footer visível |
| **Screenshots** | 0 (specs texto) | 3 produtos |
| **Vídeo** | Não tem | Loom 2 min |
| **Analytics** | Não tem | Plausible |

**Você está em:** Mínimo Aceitável ✓ (pode apresentar)
**Recomendado chegar em:** Ideal - 1 item (deploy + contatos)

---

**Última atualização:** 2026-03-31 14:40
**Próxima ação:** Decidir se faz deploy rápido antes da apresentação
