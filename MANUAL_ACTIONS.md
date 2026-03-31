# MANUAL_ACTIONS.md — Ações que Só Você Pode Fazer

> **Regra:** Este arquivo é atualizado automaticamente. Cada item aqui é um **bloqueador real** —
> sem ele, uma feature, produto ou receita está parada.
>
> **Protocolo:** No início de cada sessão (`/start`), este arquivo é lido primeiro.
> Ações concluídas são marcadas `[x]` e movidas para o histórico abaixo.
>
> **Como usar:** Basta executar as ações na ordem de prioridade, uma por vez.
> Cada item tem tempo estimado e impacto claro.

---

## 🔴 URGENTE — Bloqueia Receita

### [M-001] npm login + npm publish @egosbr/guard-brasil
- **Impacto:** npm package publicado → `npm install @egosbr/guard-brasil` funciona
- **Status:** ⚠️ AGUARDANDO LOGIN MANUAL
- **Package:** 100% pronto (tests 15/15, build OK, dist/ gerado)
- **Comandos:**
  ```bash
  cd /home/enio/egos/packages/guard-brasil
  npm login
  npm publish --access public
  ```
- **Validação:** `npm info @egosbr/guard-brasil` retorna versão 0.1.0
- **Tempo:** 3 minutos

### ~~[M-002] DNS: criar registro A para guard.egos.ia.br~~ ✅ FEITO (2026-03-31)
- **Status:** DNS resolvido + API funcional
- **Fix:** Container conectado à rede Caddy (infra_bracc), 502 → 200 ✅
- **Validação:** `curl https://guard.egos.ia.br/health` → `{"service":"egos-guard-brasil-api","status":"healthy"}` ✓
- **Próximo:** M-001 (npm publish) + M-007 (outreach emails)

---

## 🟡 IMPORTANTE — Desbloqueiam Produto

### [M-003] Executar rename br-acc → egos-inteligencia (fases 2–5)
- **Impacto:** Repositório ainda se chama br-acc internamente; Python imports ainda usam `bracc_etl`
- **Tempo:** 15 minutos (incluindo validação)
- **Pré-req:** Fase 1 (docs) já executada automaticamente — verifique com `git log br-acc`
- **Comandos:**
  ```bash
  cd /home/enio/br-acc

  # Fase 2+: Python, Docker, Shell, configs
  bash scripts/rename-to-egos-inteligencia.sh --execute

  # Rename da pasta do pacote Python
  git mv etl/src/bracc_etl etl/src/egos_inteligencia_etl

  # Commit
  git add -A
  git commit -m "feat: rename br-acc → egos-inteligencia (fases 2-5)"
  git push
  ```
- **Valida:** `python -c "from egos_inteligencia_etl.runner import main"` não dá erro

### ~~[M-004] Renomear repositório GitHub~~ ✅ FEITO
- **Status:** GitHub repo já se chama `enioxt/EGOS-Inteligencia` (confirmado via git remote)
- **Pendente local:** `git remote set-url origin git@github.com:enioxt/EGOS-Inteligencia.git` em `/home/enio/br-acc` se ainda não estiver

### [M-005] Docker network rename no Hetzner
- **Impacto:** Rede Docker ainda se chama `infra_bracc` — confuso e inconsistente
- **Tempo:** 5 minutos
- **Dep:** M-003 e M-004 executados primeiro
- **Comandos (no Hetzner):**
  ```bash
  ssh -i ~/.ssh/hetzner_ed25519 root@<redacted>
  docker network rename infra_bracc infra_egos_inteligencia
  # Recriar containers que usam essa rede:
  cd /opt/bracc && docker compose down && docker compose up -d
  ```

---

## 🟢 BAIXA PRIORIDADE — Melhoria

### [M-006] Adicionar credenciais de publicação ao pipeline de CI (elimina bloqueio manual nas próximas versões)
- **Impacto:** Próximas versões do `@egosbr/guard-brasil` precisarão de publicação manual novamente
- **Tempo:** 5 minutos
- **Dep:** M-001 primeiro (precisa ter publicação ativa)
- **Passos:**
  1. Após `npm login`, execute: `npm token create --type=publish`
  2. Copie o token gerado
  3. Armazene em cofre/secret store do CI
  4. Valide o workflow de publish com tag
- **Valida:** Push de tag `guard-brasil/v0.2.0` dispara o workflow automaticamente

### [M-007] Outreach: enviar emails para CTOs govtech BR
- **Impacto:** 0 clientes pagantes sem prospecção ativa
- **Tempo:** 2 horas
- **Material:** `docs/strategy/GUARD_BRASIL_1PAGER.md` + `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md`
- **Rascunhos:** Ver `docs/strategy/OUTREACH_EMAILS.md` (gerado automaticamente)
- **Target:** 20 CTOs de govtech, Tribunais de Contas, Ministério Público, prefeituras

---

## 🔴 CRÍTICO: APENAS M-007 BLOQUEIA RECEITA (Outreach)

**Status:** PRONTO PARA EXECUTAR HOJE (2026-03-30)

Próximas 5 emails de outreach para CTOs de govtech:
- Templates prontos em `docs/strategy/OUTREACH_EMAILS.md`
- Cada email: 1-pager + DEMO_SCRIPT + convite para demo
- Target: 20 CTOs, começar com 5

**Caminho crítico para receita:**
1. M-007 (5 emails) → HOJE
2. Respostas positivas (48h esperadas) → 3-5 respostas
3. Chamadas de demo (3-5 dias) → booking calls usando DEMO_SCRIPT
4. LOIs (1-2 semanas) → assinatura + pilots
5. Receita (M1) → R$500+/mo

**Dependências:** NENHUMA — pode executar imediatamente

## Histórico de Ações Concluídas

| ID | Ação | Concluída em |
|---|---|---|
| M-001 | npm publish @egosbr/guard-brasil@0.1.0 | 2026-03-30 10:45 UTC |
| M-002 | DNS A record guard.egos.ia.br | 2026-03-30 13:57 UTC |

---

> **Lembrete:** Se você está abrindo este arquivo, é porque há receita parada.
> Execute pelo menos M-001 e M-002 agora — são 7 minutos no total.
