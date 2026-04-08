# Intelink v3 — Arquitetura de Segurança + Multi-Device

> **Versão:** 1.1.0 | **Data:** 2026-04-09 | **Status:** ARQUITETURA APROVADA — pronta para implementação
> **SSOT:** Este arquivo
> **Decisões Aprovadas:** Híbrido local+cloud | TIER 3 max | MASP+2FA | CRDT (Automerge) | RxDB | PBKDF2 | Hetzner MVP→HA→Edge

---

## 1. Visão Geral

O Intelink v3 é um sistema de inteligência policial **local-first + cloud-sync** com as seguintes garantias:

| Garantia | Mecanismo |
|----------|-----------|
| **Funciona offline** | Banco local criptografado no dispositivo |
| **Sync sem conflito** | CRDT (Automerge) — merge determinístico |
| **Dados protegidos em repouso** | AES-256 no dispositivo + servidor |
| **Dados protegidos em trânsito** | TLS 1.3 + mTLS servidor↔servidor |
| **Identidade policial** | MASP + senha + 2FA (email ou Telegram) |
| **Auditoria completa** | Log append-only tamper-proof (Merkle tree) |
| **Multi-device** | Desktop (Windows/Linux), tablet Android/iPad, celular |
| **Dados TIER 3** | Nome completo, CPF, endereço, transações — acesso com justificativa |

---

## 2. Arquitetura em Camadas

```
╔══════════════════════════════════════════════════════════════════════╗
║  LAYER 5: CLIENTES (Web PWA + React Native + Electron)              ║
║  • Desktop: Next.js PWA (Windows, Linux, macOS)                     ║
║  • Tablet: React Native (Android/iPad) — app nativo                 ║
║  • Mobile: React Native (mesma codebase do tablet)                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  LAYER 4: LOCAL DATA ENGINE (por dispositivo)                       ║
║  • Banco local: RxDB v15 + plugin de encryption AES-256-GCM         ║
║  • CRDT Engine: Automerge v2 (merge sem conflito)                   ║
║  • Key derivation: PBKDF2(MASP+senha, salt_device, 600K iter.)     ║
║  • Cache de investigações TIER 1-2 offline completo                 ║
║  • TIER 3: acesso apenas com unlock ativo (JWT válido ou PIN)       ║
╠══════════════════════════════════════════════════════════════════════╣
║  LAYER 3: SYNC GATEWAY (FastAPI)                                    ║
║  • HTTPS + TLS 1.3 obrigatório                                      ║
║  • Delta sync: envia APENAS registros alterados (ops CRDT)          ║
║  • WebSocket para sync em tempo real quando online                  ║
║  • Rate limiting por MASP (100 req/min)                             ║
║  • Replay protection (nonce + timestamp)                            ║
╠══════════════════════════════════════════════════════════════════════╣
║  LAYER 2: SERVIDOR CENTRAL (Hetzner MVP → HA → Edge)               ║
║  • PostgreSQL (canonical SSOT dos dados)                            ║
║  • Redis (sessões, rate limits, 2FA tokens)                         ║
║  • Wazuh SIEM (monitoramento de segurança)                          ║
║  • Backup diário cifrado (offsite)                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  LAYER 1: SEGURANÇA + AUDITORIA (transversal)                       ║
║  • Merkle tree append-only (todo acesso/escrita registrado)         ║
║  • TIER 1-4 classification engine                                   ║
║  • Alertas: acesso fora horário, sem investigação ativa             ║
║  • Dashboard Corregedoria (read-only, TIER 1-2 apenas)              ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 3. Fluxo de Autenticação

```
[Policial abre app]
        │
        ▼
[Tela de login: MASP + Senha]
        │
        ▼
[Servidor valida MASP no DB]
        │
        ├─── FALHA → log tentativa + rate limit + alerta após 5x
        │
        ▼ SUCESSO
[Servidor envia 2FA: email institucional OU Telegram bot]
        │
        ▼
[Policial insere código 2FA (TTL: 10 minutos)]
        │
        ├─── EXPIRADO/INVÁLIDO → volta ao login, log evento
        │
        ▼ VÁLIDO
[Servidor emite:]
  • JWT de acesso (TTL: 15 minutos)
  • Refresh token (TTL: 8 horas em campo / 30 dias em base)
  • Sync key cifrada (derivada da sessão, nunca armazenada em plain)
        │
        ▼
[Device armazena:]
  • JWT: memória apenas (nunca localStorage, nunca disk)
  • Refresh token: OS keychain (Secure Enclave iOS, Keystore Android, Credential Manager Windows)
  • Sync key: memória + usa para decifrar banco local
        │
        ▼
[Acesso liberado — banco local descriptografado em memória]
```

### Regras de sessão

| Situação | Comportamento |
|----------|---------------|
| App vai para background > 5min | Bloqueia, pede PIN biométrico |
| App fecha | JWT limpo da memória |
| Dispositivo perdido/roubado | Admin revoga refresh token → sync falha → dados locais inacessíveis sem nova autenticação |
| 5 tentativas falhas de login | MASP bloqueado por 30 minutos, alerta no SIEM |
| 2FA não inserido em 10min | Token 2FA expirado, reiniciar fluxo |

---

## 4. Fluxo de Sincronização (CRDT)

```
[Policial cria/edita investigação OFFLINE]
        │
        ▼
[Automerge gera "op" CRDT local]
[Dado cifrado no banco local]
[Op adicionada à fila de sync]
        │
        ▼ [quando conexão disponível]
[Sync client envia: JWT + ops pendentes (delta)]
        │
        ▼
[Servidor valida JWT, verifica permissões TIER]
[Aplica ops no PostgreSQL usando Automerge server-side]
[Retorna ops pendentes do servidor para o device]
        │
        ▼
[Device aplica ops recebidas (merge CRDT — sem conflito por design)]
[Banco local atualizado]
[Audit log: {masp, timestamp, op_hash, tier, device_id}]
```

### Por que CRDT (Automerge)?

- **Operações são comutativas**: A edita campo X offline, B edita campo Y offline — merge resulta em A.X + B.Y, sem conflito
- **Audit trail perfeito**: cada op tem timestamp, autor, hash
- **Não precisa de lock de banco**: policiais na rua editam livremente, sync é eventual e correto
- **Leve**: Automerge v2 usa columnar binary format (compact)

---

## 5. Classificação de Dados TIER

| TIER | O que contém | Acesso | Armazenado offline? |
|------|-------------|--------|---------------------|
| **TIER 1** | Padrões agregados, estatísticas | Qualquer usuário autenticado | ✅ Sim, sempre |
| **TIER 2** | CPF mascarado, localização genérica | Usuário autenticado + justificativa registrada | ✅ Sim |
| **TIER 3** | Nome completo, CPF, endereço, transações | Autorização delegado + clearance + investigação ativa | ⚠️ Sim, mas cifrado separadamente, requer unlock explícito |
| **TIER 4** | Informantes, infiltrados, técnicas operacionais | Ordem judicial ou autoridade superior — NUNCA automático | ❌ Nunca no device |

### Regras TIER 3 no dispositivo

- Dados TIER 3 ficam em partição separada do banco local, com chave diferente
- Chave TIER 3 só é derivada após autenticação completa + confirmação de "modo campo" no servidor
- Se JWT expirar, dados TIER 3 são re-cifrados com chave de sessão revogada (ilegíveis sem novo login)
- Qualquer leitura TIER 3 gera audit event com justificativa obrigatória

---

## 6. Camada de Auditoria

### Estrutura do log (append-only)

```json
{
  "event_id": "uuid-v4",
  "prev_hash": "sha256(event_anterior)",
  "timestamp": "2026-04-09T14:32:11.432Z",
  "masp": "1234567",
  "device_id": "hash(device_fingerprint)",
  "action": "VIEW_ENTITY | EDIT | CREATE | DELETE | EXPORT | LOGIN | SYNC",
  "tier": 3,
  "investigation_id": "uuid",
  "entity_type": "PERSON | VEHICLE | ORG | DOCUMENT",
  "justification": "Suspeito vinculado à investigação INQ-2024-001",
  "ip_hash": "sha256(ip_address)",
  "session_id": "uuid"
}
```

### Propriedade tamper-proof

- Cada evento contém hash do evento anterior → **cadeia de Merkle**
- Servidor valida integridade ao receber sync
- Impossível apagar ou editar um evento sem quebrar a cadeia
- Raiz da Merkle tree publicada semanalmente em repositório Git público (ou blockchain anchor via OriginStamp — opção futura)

### Alertas automáticos (Wazuh SIEM)

| Gatilho | Ação |
|---------|------|
| Acesso TIER 3 sem investigação ativa | Alerta imediato para Corregedoria |
| Login fora do horário de serviço | Notificação supervisão |
| > 50 consultas por hora | Suspeita de exfiltração, bloquear + alerta |
| Sync de device não registrado | Rejeitar + alerta |
| Tentativa de deletar log de auditoria | Bloqueado (append-only) + alerta crítico |

---

## 7. Decisões Críticas — ✅ APROVADAS

> **Todas as decisões abaixo foram aprovadas explicitamente pelo usuário em 2026-04-09.**

### 7.1 — Banco de dados local no dispositivo

**Opção A: SQLite + SQLCipher**
- Prós: Comprovado em campo (usado por Signal, 1Password), AES-256 nativo, cross-platform, mínimo overhead
- Contras: CRDT precisa ser implementado na camada de aplicação (mais código)
- Stack: `expo-sqlite` (React Native) + `better-sqlite3` (desktop/Electron)

**Opção B: RxDB (recomendado)**
- Prós: CRDT built-in, funciona em browser PWA + React Native + Node, plugin de encryption, protocolo de sync testado
- Contras: JavaScript-only (mais pesado que SQLite), ecossistema mais jovem
- Stack: RxDB v15 + `rxdb-encryption-crypto-js` plugin

**Opção C: PouchDB + CouchDB**
- Prós: Protocolo de sync maduro (CouchDB replication), battle-tested
- Contras: Protocolo proprietário CouchDB (lock-in), não usa CRDT puro, mais antigo
- Stack: PouchDB client + CouchDB server

**✅ DECISÃO APROVADA: Opção B (RxDB)** — melhor suporte a CRDT, funciona identicamente em web PWA e React Native sem bifurcar o código.

---

### 7.2 — Gestão de chaves de criptografia

**Opção A: PBKDF2 da senha do usuário (recomendado)**
- Chave derivada localmente de `PBKDF2(MASP + senha, salt_por_device, 600000 iterações)`
- Prós: Chave NUNCA sai do device, zero dependência de servidor para decifrar dados locais
- Contras: Se policial esquecer a senha, dados locais são perdidos (recuperação via backup do servidor)
- Segurança: Mesmo se servidor for comprometido, dados locais permanecem cifrados

**Opção B: Device OS keychain**
- Chave gerada aleatoriamente, armazenada no Secure Enclave (iOS) / Keystore (Android) / DPAPI (Windows)
- Prós: Máxima segurança de hardware, não depende de senha do usuário
- Contras: Chave presa ao device — troca de device = recriar banco local (redownload do servidor)
- Segurança: Impossível extrair chave sem acesso físico ao device + biometria

**Opção C: Chave no servidor (escrow)**
- Servidor armazena chave cifrada, envia ao device após autenticação
- Prós: Recuperação fácil em qualquer device
- Contras: Se servidor for comprometido, todos os dados são comprometidos — NÃO RECOMENDADO para TIER 3

**✅ DECISÃO APROVADA: Opção A (PBKDF2)** — chave derivada localmente, nunca sai do device. Nunca Opção C para TIER 3.

---

### 7.3 — Topologia do servidor

**Opção A: Single Hetzner VPS (MVP)**
- 1 servidor Hetzner (CX31: 8GB RAM, 80GB SSD, ~€12/mês)
- Backups diários cifrados para Hetzner Object Storage
- Prós: Simples, barato, já temos experiência com Hetzner (852), rápido de implantar
- Contras: Single point of failure (downtime em manutenção)
- Adequado para: Piloto com 1 delegacia, < 50 usuários

**Opção B: Hetzner Primary + Replica (Produção)**
- 2 servidores Hetzner em datacenters diferentes (Nuremberg + Helsinki)
- PostgreSQL streaming replication
- Caddy com failover automático
- Prós: HA (high availability), < 5min de failover
- Contras: 2× custo, mais complexidade

**Opção C: Edge node por delegacia + cloud**
- Mini-servidor físico em cada delegacia + VPS cloud como coordenador
- Funciona 100% offline mesmo sem internet
- Prós: Máxima resiliência, dados nunca saem da delegacia física
- Contras: Custo de hardware, manutenção distribuída, mais complexo

**✅ DECISÃO APROVADA: Plano faseado** — Opção A (Hetzner single) para MVP → Opção B (HA dual) para produção → Opção C (edge delegacia) para expansão nacional.

---

## 8. Stack Tecnológico Definido

```yaml
# Camada de Cliente
frontend:
  web_pwa: "Next.js 16 + TailwindCSS + shadcn/ui (dark mode)"
  mobile_tablet: "React Native + Expo (Android/iOS — mesma codebase)"
  desktop: "Electron wrapping Next.js PWA (Windows/Linux)"

# Camada de Dados Local
local_data:
  db: "RxDB v15 + rxdb-encryption-crypto-js plugin"
  crdt: "Automerge v2"
  encryption: "AES-256-GCM"
  key_derivation: "PBKDF2(MASP + senha, salt_device, 600000 iterações) — chave nunca sai do device"

# Camada de Sync
sync:
  protocol: "HTTPS/WebSocket + TLS 1.3"
  format: "Automerge binary ops (delta only)"
  auth: "JWT (15min) + refresh token (8h campo / 30d base)"

# Servidor
server:
  topology: "Hetzner CX31 (MVP) → Dual Hetzner HA (produção) → Edge por delegacia (expansão)"
  api: "FastAPI (Python 3.12)"
  db: "PostgreSQL 16 + pgcrypto"
  cache: "Redis 7"
  siem: "Wazuh"
  reverse_proxy: "Caddy (TLS automático)"

# Autenticação
auth:
  identity: "MASP"
  factors: ["senha (bcrypt 14 rounds)", "2FA email ou Telegram"]
  token: "JWT (RS256) + refresh token"
  token_storage: "memória apenas (JWT) + OS keychain (refresh)"

# Auditoria
audit:
  log: "append-only Merkle tree"
  storage: "PostgreSQL tabela imutável (sem DELETE, sem UPDATE)"
  alerts: "Wazuh SIEM + Telegram para Corregedoria"
  retention: "7 anos (Marco Civil Internet Art. 15)"
```

---

## 9. O que já existe no Intelink (reaproveitável)

| Componente | Onde está | Status |
|-----------|-----------|--------|
| 2FA via Telegram | `INTELINK/` (bot existente) | ✅ Reaproveitar |
| Auth scaffold (JWT) | `apps/agent-service/` | ✅ Reaproveitar |
| Rate limiting | `src/lib/rate-limit.ts` (852) | ✅ Portar |
| Telemetry/action tracker | `action_tracker.py` | ✅ Reaproveitar |
| TIER system design | `INTELINK/docs/INTELINK_COMPARTILHAMENTO_SEGURO.md` | ✅ Implementar |
| FastAPI base | `apps/agent-service/app/main.py` | ✅ Reaproveitar |
| MASP auth | `src/lib/user-auth.ts` (852) | ✅ Portar para Intelink |
| RBAC base | `apps/agent-service/` | ⚠️ Expandir |

---

## 10. Plano de Implementação (após aprovação das decisões)

### Fase 0 — Fundação de Segurança (2 semanas)
- [ ] **INTELINK-SEC-001**: Auth server: MASP + bcrypt + JWT (RS256) + refresh token
- [ ] **INTELINK-SEC-002**: 2FA: portar bot Telegram existente + adicionar opção email
- [ ] **INTELINK-SEC-003**: Banco local cifrado + inicialização segura (decisão §7.1)
- [ ] **INTELINK-SEC-004**: Key derivation (decisão §7.2)
- [ ] **INTELINK-SEC-005**: Audit log append-only (PostgreSQL + Merkle)

### Fase 1 — Sync Engine (2 semanas)
- [ ] **INTELINK-SYNC-001**: Automerge v2 integrado no cliente
- [ ] **INTELINK-SYNC-002**: Delta sync endpoint no servidor (FastAPI)
- [ ] **INTELINK-SYNC-003**: Conflict-free merge validado com testes
- [ ] **INTELINK-SYNC-004**: Offline queue (ops pendentes persistem entre reinicializações)

### Fase 2 — Multi-device (2 semanas)
- [ ] **INTELINK-DEVICE-001**: PWA desktop (Next.js, testado em Windows + Linux)
- [ ] **INTELINK-DEVICE-002**: React Native app (tablet Android MVP)
- [ ] **INTELINK-DEVICE-003**: Device registration + revogação remota
- [ ] **INTELINK-DEVICE-004**: Session lock (background > 5min → PIN/biometria)

### Fase 3 — TIER + Auditoria (2 semanas)
- [ ] **INTELINK-TIER-001**: Classificador automático TIER 1-4 por campo
- [ ] **INTELINK-TIER-002**: Partição TIER 3 separada no banco local
- [ ] **INTELINK-TIER-003**: Wazuh SIEM + alertas Telegram para Corregedoria
- [ ] **INTELINK-TIER-004**: Dashboard de auditoria (read-only, apenas TIER 1-2)

### Fase 4 — Hardening + Piloto (2 semanas)
- [ ] **INTELINK-HARD-001**: Pen test básico (OWASP Top 10)
- [ ] **INTELINK-HARD-002**: Stress test sync (100 devices simultâneos)
- [ ] **INTELINK-HARD-003**: Documentação de recuperação (device perdido, senha esquecida)
- [ ] **INTELINK-HARD-004**: Treinamento piloto 1 delegacia

---

## Referências

- Automerge v2: https://automerge.org/
- RxDB offline-first: https://rxdb.info/
- SQLCipher: https://www.zetetic.net/sqlcipher/
- Wazuh SIEM: https://wazuh.com/
- Sealed.Info offline integrity: https://sealed.info/
- In-Synch RMS (law enforcement offline): https://in-synchrms.com/
- Intelink TIER model: `INTELINK/docs/INTELINK_COMPARTILHAMENTO_SEGURO.md`
- Intelink analysis: `INTELINK/docs/ANALISEINTELINK.md`
