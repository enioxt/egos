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

### [M-001] npm login + npm publish @egos/guard-brasil
- **Impacto:** npm package não publicado → desenvolvedores não conseguem `npm install @egos/guard-brasil`
- **Tempo:** 5 minutos
- **Comando:**
  ```bash
  cd /home/enio/egos/packages/guard-brasil
  npm login          # abre browser para autenticação
  npm publish --access public
  ```
- **Valida:** `npm info @egos/guard-brasil` retorna versão 0.1.0
- **Desbloqueado por:** EGOS-064, EGOS-123

### [M-002] DNS: criar registro A para guard.egos.ia.br → 204.168.217.125
- **Impacto:** API Guard Brasil não acessível publicamente → demos falham, clientes não conseguem testar
- **Tempo:** 2 minutos
- **Onde:** Painel DNS do domínio egos.ia.br (provavelmente Cloudflare ou Registro.br)
- **Registro:**
  ```
  Tipo: A
  Nome: guard
  Valor: 204.168.217.125
  TTL: 300
  ```
- **Valida:** `curl https://guard.egos.ia.br/health` retorna `{"status":"healthy"}`
- **Obs:** Caddy já está configurado e vai emitir certificado TLS automaticamente

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
  ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125
  docker network rename infra_bracc infra_egos_inteligencia
  # Recriar containers que usam essa rede:
  cd /opt/bracc && docker compose down && docker compose up -d
  ```

---

## 🟢 BAIXA PRIORIDADE — Melhoria

### [M-006] Adicionar NPM_TOKEN ao GitHub Actions (elimina bloqueio de npm login nas próximas versões)
- **Impacto:** Próximas versões do @egos/guard-brasil precisarão de npm login manual novamente
- **Tempo:** 5 minutos
- **Dep:** M-001 primeiro (precisa ter conta npm ativa e token)
- **Passos:**
  1. Após `npm login`, execute: `npm token create --type=publish`
  2. Copie o token gerado
  3. Acesse: https://github.com/enioxt/egos/settings/secrets/actions → New secret
  4. Nome: `NPM_TOKEN`, Valor: token copiado
- **Valida:** Push de tag `guard-brasil/v0.2.0` dispara o workflow `.github/workflows/publish-npm.yml` automaticamente

### [M-007] Outreach: enviar emails para CTOs govtech BR
- **Impacto:** 0 clientes pagantes sem prospecção ativa
- **Tempo:** 2 horas
- **Material:** `docs/strategy/GUARD_BRASIL_1PAGER.md` + `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md`
- **Rascunhos:** Ver `docs/strategy/OUTREACH_EMAILS.md` (gerado automaticamente)
- **Target:** 20 CTOs de govtech, Tribunais de Contas, Ministério Público, prefeituras

---

## Histórico de Ações Concluídas

| ID | Ação | Concluída em |
|---|---|---|
| — | — | — |

---

> **Lembrete:** Se você está abrindo este arquivo, é porque há receita parada.
> Execute pelo menos M-001 e M-002 agora — são 7 minutos no total.
