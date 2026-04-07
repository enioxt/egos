# HARVEST.md — EGOS Core Knowledge

> **VERSION:** 4.4.0 | **UPDATED:** 2026-04-07
> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo
> **Latest:** P37 added — Cold email GTM learnings + Guard Brasil sandbox audit (4 bugs found)

## P37 Patterns (2026-04-07)

### Cold Email GTM — Verificação de Endereço Antes de Criar Drafts

**Problema:** Dois dos 5 emails M-007 falharam na entrega por endereços inválidos:
- `contact@lgpd-brasil.com.br` — domínio não existe
- `contato@rocketseat.com.br` — endereço não aceita mensagens

**Regra:** Antes de criar drafts de outreach, verificar se o domínio do email existe:
```bash
host lgpd-brasil.com.br  # se retornar NXDOMAIN, domínio inválido
```
Ou usar DNS lookup via browser antes de assumir que o email genérico (`contato@`) funciona.

**Padrão para encontrar emails corretos:**
1. Verificar página `/contato` ou `/about` do site oficial
2. Procurar no LinkedIn da empresa (email na bio de fundadores)
3. Buscar no GitHub (email em commits ou perfil)
4. Usar `info@`, `hello@`, `ola@` como fallback quando `contato@` falhar

---

### Guard Brasil Sandbox Audit — Gaps Identificados (2026-04-07)

Testados os 6 demos do frontend (`/landing`) contra a API real (`/v1/inspect`). Resultado:

| Demo | Status | Gap |
|------|--------|-----|
| CPF masking | ✅ | Funciona |
| RG detection | ❌ | Formato `12.345.678-9` → zero findings |
| Placa veicular | ✅ | Funciona (false positive menor em "ABC") |
| ATRiAN bias | ❌ | Texto racialmente carregado → score 100 |
| Dados médicos | ⚠️ | CPF mascarado, nome + diagnóstico intactos |
| Multi-PII | ⚠️ | 5/5 tipos detectados, nome sempre intacto |

**Regra:** Não apresentar sandbox para prospects sem corrigir GUARD-BUG-001 (RG) e GUARD-BUG-002 (ATRiAN). Esses são os dois demos mais demonstrativos do produto — RG é core BR, ATRiAN é diferencial ético.

**False positives ATRiAN:** "MG" (estado), "ABC" (qualquer sigla 3 letras), "HIV" (termo médico) — o detector `invented_acronym` precisa de whitelist.

---

### Dashboard de Produto — Nunca Expor Sem Auth

**Incidente:** `/dashboard-v1` ficou publicamente acessível mostrando placeholders que pareciam dados reais (MRR R$5.747, 5 clientes, 12.847 chamadas). Qualquer um com a URL podia ver.

**Regra:** Toda rota `/dashboard*`, `/admin*`, `/internal*` deve ter middleware de autenticação (JWT ou session) desde o primeiro commit. Nunca deploiar painel interno sem auth "porque é placeholder" — a URL vaza e o contexto se perde.

**Fix padrão (Next.js):**
```ts
// middleware.ts
export const config = { matcher: ['/dashboard/:path*'] }
export default withAuth(/* session check */)
```

---

## P36 Patterns (2026-04-07)

### Hermes Agent — Claude OAuth via ~/.claude/.credentials.json

- **Discovery:** NousResearch hermes-agent v0.7.0 auto-discovers Claude Code OAuth from `~/.claude/.credentials.json`. Zero config. No API key needed. Uses Claude Max subscription.
- **Install:** `uv pip install -e '/path/to/hermes-agent[all]'` into a dedicated venv. Not on PyPI — clone from GitHub first.
- **Auth auto-detection:** `hermes auth list` shows `claude_code oauth ←` automatically if `~/.claude/.credentials.json` exists.
- **Model IDs that work:** `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-6`. Use exact model ID strings.
- **Non-interactive usage:** `hermes chat --provider anthropic --model <model> -q "prompt" --yolo -Q`
- **EGOS default:** Haiku 4.5 (`claude-haiku-4-5-20251001`) — 10x cheaper, same quality for mechanical tasks.

### Hermes OAuth token sync — rotating refreshToken gotcha

- **Problem:** OAuth refreshToken ROTATES on each use. If VPS refreshes independently, local refreshToken becomes invalid (and vice versa). One machine must be the single source.
- **Solution:** Local machine is the ONLY refresher. Cron `*/5 * * * *` runs:
  1. `refresh-token.py` — refreshes if <10min to expiry, writes `~/.claude/.credentials.json`
  2. `scp` credentials to VPS
  3. `ssh root@VPS "/opt/hermes-venv/bin/hermes auth reset anthropic"` — clears exhaustion state
- **Exhaustion state:** Hermes marks credentials `exhausted` after a failed auth (e.g. expired token). Must reset with `hermes auth reset <provider>` after syncing fresh credentials. Non-obvious.
- **Cron location:** `crontab -l | grep refresh-token` on local machine
- **Script:** `~/.hermes-agent/scripts/refresh-token.py`

### Hermes profile system

- `hermes profile create <name>` → creates `~/.hermes/profiles/<name>/` with 77 bundled skills, wrapper at `~/.local/bin/<name>`
- Per-profile model: `hermes config set model <id> --profile <name>`
- System prompt: write to `~/.hermes/profiles/<name>/system_prompt.md`
- List: `hermes profile list` shows all profiles with model + gateway status

## P35 Patterns (2026-04-07)

### Firecrawl key exposure in git history — incident pattern

- **Incident:** Old Firecrawl API key `fc-45cf069ee7ef4c3aa4942a41127d8629` exposed in:
  - Git commit 74ea2c2 (handoff_2026-04-06.md, documented as "Firecrawl MCP installed")
  - Local `.env` files (gitignored but accessible on VPS/local machine)
- **Root cause:** Documented key value in handoff before understanding the security boundary; `.env` files are gitignored per policy but the key was exposed in version-controlled docs.
- **Resolution:** Rotated to new key `fc-d9060a030e454d8dab6e0003ba20933b` on 2026-04-07, commit a63ea8c.
- **Canonical fix process:**
  1. Identify all instances: `grep -r "old-key" .` (all repos, including git history)
  2. Update all `.env` files directly (no add/commit since gitignored)
  3. Update docs/refs to remove sensitive values (keep "key rotated 2026-04-07" instead)
  4. Commit with clear security incident message
  5. Recommend key revocation on external service dashboard
  6. Optional: `git filter-repo` to clean history if critical (not done here — handoff scope)
- **Prevention:** Never document actual credential values in prose. Instead:
  - `.env` files: keep values only locally
  - Docs: write "key rotated YYYY-MM-DD" or "configured via envvar FIRECRAWL_API_KEY"
  - Handoffs: link to `.env.example` or section refs, never inline secrets
  - Audit: pre-commit hook `gitleaks` passes all commits; incident was doc-not-code
- **Lesson:** `gitleaks` protects code but not markdown prose. Add `.md` pattern check if documenting services with secrets.

## P33 Patterns (2026-04-07)

### Doc-Drift Shield — proposed structural approach (status: L1 + global rules only, L2-L4 not yet implemented)

- **Problem observed in THIS repo (reproducible):**
  - Carteira Livre README claimed 54 pages; `find app/ -name 'page.tsx' | wc -l` returned 134 on 2026-04-07 → drift +148%
  - Carteira Livre README claimed 68 APIs; `find app/api -name 'route.ts' | wc -l` returned 254 → drift +273%
  - BR-ACC README claimed 77M Neo4j nodes; `MATCH (n) RETURN count(n)` against `bracc-neo4j` container returned 83,773,683 on 2026-04-07 → drift +8.8%
  - All commands above are in `.egos-manifest.yaml` of the respective repos — run them to reproduce.
- **Proposed solution (design only):** `.egos-manifest.yaml` per repo declaring every quantitative claim with its reproducible command + tolerance. Four intended layers:
  1. L1 contract manifest — **IMPLEMENTED in 3 pilot repos (egos, br-acc, carteira-livre)**
  2. L2 pre-commit pairing hook — **NOT YET IMPLEMENTED** (spec in handoff)
  3. L3 autonomous sentinel agent — **NOT YET IMPLEMENTED** (spec in handoff)
  4. L4 weekly LLM analysis — **NOT YET IMPLEMENTED** (spec in handoff)
- **What is NOT claimed:** this has not been benchmarked against other approaches; no proof yet that it prevents drift in practice (sample size = 0, we just designed it today). The hypothesis will be tested when L2-L4 ship.
- **Reference:** `docs/DOC_DRIFT_SHIELD.md` (design doc with implementation status marked per layer) + `~/.claude/CLAUDE.md §27` (hard rules added 2026-04-07).
- **Prior art we read while designing (attribution, not comparison):** jbrockSTL/doc-drift (GitHub), DeepDocs (Medium article), Federico Palmieri's "Two git hooks" Medium article 2026-03-08 (source of the pairing rule), Specmatic, nold-ai/specfact-cli, suhteevah/docsync. We did not run or benchmark any of them — we only read their descriptions and borrowed naming/concepts.

### `sed -i` breaks Docker bind mount inodes

- **Symptom:** After `sed -i /path/on/host/file`, host sees new content but container still serves old. Caddy reload says "config is unchanged".
- **Root cause:** `sed -i` is NOT in-place — it creates a temp file and renames, producing a new inode. Docker bind mounts track the original inode at container start; container references the OLD inode indefinitely.
- **Canonical fix:** Edit file on host, then `docker restart <container>` to rebind.
- **Alternatives that FAIL:** `docker cp new_file container:/path` ("device or resource busy"), `python3 open("w")` (new inode still).
- **Discovered:** 2026-04-07 during Caddyfile fix session. ~20 min debugging wasted before the insight.

### Caddyfile routing pattern for Docker multi-network setups

- **Rule:** When Caddy and backend container share a Docker network, use **container name + container port**, never host-mapped port.
- **Wrong:** `reverse_proxy 127.0.0.1:3090` (Caddy's Docker network can't reach host localhost)
- **Right:** `reverse_proxy eagle-eye:3001` (Docker DNS resolves container name)
- **Verify before deploy:**
  1. `docker inspect <container> | grep Networks` — same network as Caddy?
  2. Container port (not host-mapped) from `docker inspect`
  3. `docker exec infra-caddy-1 curl -s http://<container-name>:<port>/` — reachable?

### Repository git remote archaeology

- When investigating which local path corresponds to a public GitHub repo, `git remote -v` is definitive.
- Example (2026-04-07): `/home/enio/br-acc origin: git@github.com:enioxt/EGOS-Inteligencia.git` (128⭐) — canonical. `/home/enio/egos-inteligencia` is NOT a git repo — abandoned scaffold.
- Commit message forensics: `git log --grep="rename\|migrat"` reveals migration intent that may have stopped mid-flight.

### Carteira Livre: the "undersold scope" pattern

- Early README badges reflect the first 2 weeks. After 4 months of rapid iteration, real numbers are 2-4x higher but badges rarely update.
- Example: Carteira Livre (Dec 2025 era) said 54 pages + 68 APIs + 175 tests. Reality on 2026-04-07: 134 pages + 254 APIs + 2847 assertions.
- Detection commands baked into `.egos-manifest.yaml` so sentinel catches this automatically.
- **Bonus:** git log revealed 16 "hidden features" never promoted in README (Rádio Philein 24/7, AI Orchestrator, Ambassador system, INPI MVP, multi-state, mobile offline, influencer discovery).

### Neo4j proof capture (reproducible query)

- For any Neo4j claim in docs, embed the exact query + auth in `.egos-manifest.yaml`:
  ```bash
  curl -s -u neo4j:$PASS http://localhost:7474/db/neo4j/query/v2 \
    -H "Content-Type: application/json" \
    -d '{"statement":"MATCH (n) RETURN count(n) as nodes"}'
  ```
- Auth discovery: `docker exec bracc-neo4j env | grep NEO4J_AUTH`
- Reproducibility: any skeptic runs the command and verifies — no trust required.

---

## P31 Patterns (2026-04-06)

**## P31 Patterns (2026-04-06)**


**- **Canon:** `kernel/.guarani/` is the source of truth; `~/.egos/guarani/` is the synced mirror**
- **Adapters:** `CLAUDE.md` and `.windsurfrules` are environment adapters, never constitutional roots
- **Sync model:** kernel → `scripts/governance-sync.sh` → `~/.egos/` → repo/IDE adapters
- **Rule:** if adapter text conflicts with `.guarani`, `.guarani` wins
- **Cleanup trigger:** any local/global adapter that grows into a second constitution becomes drift and must be collapsed

**- Avoid grouped items like `SD-001..008` without dependency order**
- Every rollout must expose: dependencies, exact order, deploy gate, security gate, UX gate, launch gate
- Task bundles are acceptable only as summaries; execution must live in explicit checklist items

---

---

## P30 Patterns (2026-04-06)

**## P30 Patterns (2026-04-06)**


**- **Decision:** HUM-002 — Produtizar gem do archive v2 como container standalone**
- **Domain:** self.egos.ia.br → VPS 204.168.217.125:3098
- **Pattern:** Extract from archive → Containerize → Dedicated domain → Reverse proxy (Caddy)
- **Stack:** FastAPI (Python v2) + Next.js + Docker + Supabase
- **Differentiation:** "IA que pergunta, não responde" — método maiêutico/socrático
- **ICP:** B2C wellness/self-improvement (não medical device — evitar claims terapêuticos)
- **Compliance:** LGPD-ready (reuses Guard Brasil patterns)
- **Architecture spec:** `docs/SELF_DISCOVERY_ARCHITECTURE.md`
- **Tasks:** SD-001..SD-019 (TASKS.md)

**- Register A record: self.egos.ia.br → 204.168.217.125**
- Caddy reverse proxy: self.egos.ia.br → localhost:3098
- TLS automático via Let's Encrypt (Caddy internal)
- Health check: /health endpoint monitored by watchdog

---

---

## P29 Patterns (2026-04-06)

**## P29 Patterns (2026-04-06)**


**- Trigger: 7 GTM files had duplicate/overlapping content scattered across docs/business/, docs/sales/, docs/strategy/**
- Fix: Create domain SSOT first, migrate all content, delete sources → one file to rule the domain
- Guard: `.guarani/orchestration/SSOT_RULES.md` + `CLAUDE.md §26` prevent future dispersion
- Anti-pattern: don't create a new file when content belongs in an existing SSOT

**- Wrong: `[ -e /dev/tty ]` — file exists even when git runs hook non-interactively**
- Wrong: `{ : < /dev/tty; } 2>/dev/null` — /dev/tty may open but git commit doesn't connect stdin to it
- Correct: `[ -t 0 ]` — "is stdin a file descriptor pointing to a terminal?" Returns false in `git commit`
- Implication: hooks with interactive prompts must use `[ -t 0 ]` for non-interactive detection

**- Token expires ~5h (not 24h). Cron every 2h, refresh if <4h remaining = 2 cycle buffer**
- 429 on refresh = token still valid (server rate-limits refresh of live tokens) — expected, not an error
- VPS sync via rsync after every successful refresh — both local and VPS always in sync
- Fallback: `node claude-code-cli.js --print "x"` triggers CC to refresh credentials automatically

---

## Guard Brasil GTM Patterns (2026-04-06)

**`business/MARKET_RESEARCH_GUARD_BRASIL_2026.md` (source of truth — do not duplicate here)**


**CTOs + backend devs at fintechs/healthtechs (50-500 employees). Daily CPF/RG processing, ANPD compliance pressure, days-not-months purchase cycle.**


**Developer-first, BR-specific PII detection via REST API. Full analysis with sources: `business/MARKET_RESEARCH_GUARD_BRASIL_2026.md`.**


**Process-focused compliance tools (workflow, ROPA, DSAR) typically have no detection API — approach as integration partner before outbound sales.**


**1. Tutorial post with working code example (not a pitch) → drives organic inbound**
2. Tie to regulatory news (ANPD enforcement) → creates urgency without selling

---

## EGOS MCP Inventory — Decision Log (2026-04-06)

**3 LIVE custom servers (keep):**
- `egos-governance` — ssot_drift_check, list_tasks, agent_status, repo_health
- `egos-memory` — memory_store, memory_recall, memory_list, memory_delete
- `egos-knowledge` — search_wiki, get_page, record_learning, get_stats (calls gateway.egos.ia.br)

**5 spec-only servers (SKIP — don't build):**
- `llm-router-mcp`, `git-advanced-mcp`, `fs-watch-mcp`, `calendar-mcp`, `supabase-db` — `.guarani/mcp-config.json` has well-designed specs but zero server implementations. Alternatives already exist (GitHub MCP, Claude.ai Supabase, CCR scheduler).

**1 MCP to BUILD (GTM value):**
- `guard-brasil-mcp` — wraps `guard.egos.ia.br` as Claude tool. Any dev installs it and has Guard Brasil in their Claude session. GTM play: publish as `@egosbr/guard-brasil-mcp`.

**Move `egos-knowledge` from `egos/.claude/settings.json` → `~/.claude/settings.json` (make global, not project-only).**
---

## Docker Bind Mount + Caddy Container Naming (2026-04-06)

### Problem
After editing a Caddyfile on the host machine (bind-mounted into a Docker container), the 502 persists.

### Root Cause (two separate bugs)
1. `reverse_proxy localhost:3060` inside Docker resolves to the **container's** localhost — not the host. Must use container name: `reverse_proxy egos-hq:3060`
2. Even after fixing the Caddyfile, changes to a bind-mounted file don't live-update — the container must be restarted: `docker restart infra-caddy-1`

### Solution
```bash
# Fix Caddy config: localhost → container name
sed -i 's/reverse_proxy localhost:3060/reverse_proxy egos-hq:3060/' /opt/bracc/infra/Caddyfile
# Reload: restart container (not just caddy reload)
docker restart infra-caddy-1
```

**After any bind-mounted config change, ALWAYS restart the consuming container.**
---

## UserPromptSubmit Hooks — Context Injection (not Command Execution) (2026-04-06)

### What hooks CAN do
UserPromptSubmit hooks receive the prompt text via stdin and can write to stdout to inject additional context/instructions that get prepended to the conversation.

### What hooks CANNOT do
Hooks cannot invoke `/skill-name` commands. They do not have access to the Claude Code command system — only to the conversation context channel.

### Pattern: Auto meta-prompt injection
```bash
# In ~/.claude/hooks/skill-auto-trigger
PROMPT=$(cat /tmp/prompt_content)
if echo "$PROMPT" | grep -qi "decisão estratégica"; then
  cat ~/.guarani/prompts/meta/universal-strategist.md  # stdout → injected as context
fi
```

**Use hooks to inject meta-prompt **content**, not to run commands.**
---

## Google AI Studio: Text Chat vs Imagen 3 (2026-04-06 late)

### State of implementation
- **Text chat:** ✅ DONE — `packages/shared/src/llm-provider.ts` wired for Gemini 2.5 + Gemma 4 31B + Gemini 2.5 Pro
- **Imagen 3:** ❌ NOT implemented — endpoint differs from chat, requires separate provider config

### Integration pattern (next session)

**1. Use Playwright MCP → screenshot HTML template (`scripts/assets/guard-og.html`) → save as JPG**
2. Not Imagen 3 (deterministic design already exists in HTML)

**1. Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict`**
2. Auth: Bearer token (same key as chat)
3. Body: `{ instances: [{ prompt: "..." }], parameters: { sampleCount: 1 } }`
4. Returns: base64 PNG (decode to file)
5. Use for: scan result cards, banners, LGPD thread replies

**`/home/enio/.claude/plans/precious-doodling-clover.md` (GTM-015 + X-thread-poster + Imagen 3 integration, 3 phases, ~2h)**
---

## X.com OAuth Infrastructure (fully operational as of 2026-04-06)

**`apps/guard-brasil-web/app/api/x/route.ts` (lines 24-53)**
- Full OAuth 1.0a signing implemented
- Supports: `action: 'post'` (standalone tweets), `action: 'reply'` (thread replies), `action: 'search'`, `action: 'mentions'`
- No image support in current version (needs media_upload chain)

**`scripts/x-reply-bot.ts` — production 3+ months, rate-limited 40 replies/day**


**`scripts/x-post-thread.ts` (new script) — post 4-tweet thread from PART002_SOCIAL_POSTS.md with og-image attached**
---

## GTM-First Pattern for Researcher-Builders (2026-04-06)

### Problem
Solo technical founders who build by investigation (not market demand) ship products with R$0 MRR despite high technical output. The gap is not technical — it's commercial.

### Profile
- **Researcher-builder:** creates features by following curiosity, not customer pull
- Builds compulsively, doesn't show — "faço faço mas não mostro nada"
- Dislikes cold sales, outreach, pitch decks (risk of rejection)
- Needs: automatic GTM bridge, not manual hustle

### System compensation pattern
```
/start → always show: MRR, customers, M-007 status, pending demos
/end → always ask: "Did you advance GTM today?"
Every new feature → document "Who uses this? How do they find it?" before done
X.com bot → target LGPD/compliance conversations, not just AI topics
HQ dashboard → GTM metrics card as PRIMARY widget
```

### Co-founder strategy
Accept the division: researcher-builder handles product/tech, commercial co-founder handles sales/distribution. This is not failure — it's specialization.

---

## CLAUDE.md Dissemination Protocol (2026-04-06)

### Rule
Any rule written in one CLAUDE.md does not exist in the others. Must propagate simultaneously to: `~/.claude/CLAUDE.md`, `egos/CLAUDE.md`, `.guarani/`, `memory/`.

### Pattern
When adding a new global rule (e.g., GTM-first mindset):
1. Add numbered section to `~/.claude/CLAUDE.md` (global)
2. Add summary section to `egos/CLAUDE.md` (project)
3. Create `memory/feedback_*.md` file (persistence)
4. Update `MEMORY.md` index

**Claude Code loads CLAUDE.md from the current project directory. Global rules in `~/.claude/CLAUDE.md` apply everywhere, but project rules in `egos/CLAUDE.md` only apply in that repo.**
---

## AI Agent Validation Checklist Pattern (2026-04-03)

### Problem
AI agents jump to conclusions about "ghost agents" or "missing files" without complete validation, causing false positives and wasted investigation time.

### Root Cause (Session P17 Case Study)
When investigating 4 reported "ghost agents":
- **Error 1:** Assumed `drift-sentinel` output was ground truth
- **Error 2:** Did not check `agents.json` entrypoint field for each agent
- **Error 3:** Did not verify file existence at actual entrypoint paths
- **Error 4:** Ignored `status: "dead"` field meaning

**2 false positives (`kol-discovery` and `gem-hunter-api` were alive in `scripts/` and `agents/api/`), 2 true positives (actually dead agents).**
### Solution — 4-Point Validation Protocol
Before claiming ANY agent is "ghost/missing/dead", MUST validate:

| # | Check | Tool | Evidence Required |
|---|-------|------|-------------------|
| 1 | `agents.json` entrypoint field | `read_file` on `agents/registry/agents.json` | Exact `entrypoint` path string |
| 2 | File exists at that path | `existsSync` or manual check | File content or 404 confirmation |
| 3 | `status` field meaning | `read_file` on `agents.json` | `"dead"`, `"disabled"`, `"active"`, etc. |
| 4 | `run_modes` + `kind` context | `read_file` on `agents.json` | `service` vs `tool` vs `workflow` behavior |

### Critical Rules
- **NEVER** rely solely on `drift-sentinel` output — it has false positives on non-standard paths
- **ALWAYS** verify `scripts/` and `agents/api/` entrypoints manually
- **IGNORE** agents with `status: "dead"` — they are intentionally removed
- **CROSS-REFERENCE** multiple sources before making claims

### Applied To
- `.windsurfrules` — Added Rule 13: AGENT VALIDATION
- `agents/agents/drift-sentinel.ts` — Fixed to check any entrypoint path
- Future agent investigations — mandatory 4-point validation

---

## Agent Registry Drift Detection Pattern (2026-04-03)

### Problem
Agent registry (`agents.json`) diverges from filesystem reality: dead agents remain listed, entrypoints move to non-standard paths (`scripts/`, `agents/api/`), drift detection only checks `agents/agents/` directory.

### Solution
Two-layer validation in `drift-sentinel.ts`:
1. **Entrypoint Check**: For each agent in registry, verify `entrypoint` field exists on disk (any path: `scripts/`, `agents/agents/`, `agents/api/`)
2. **Orphan Check**: Files in `agents/agents/` not listed in registry
3. **Status Filter**: Skip agents with `status: "dead"` or `"disabled"`

### Key Implementation
```typescript
// Check each agent's entrypoint exists (respects any path)
for (const agent of agents) {
  if (agent.status === "dead" || agent.status === "disabled") continue;
  const fullPath = join(ROOT, agent.entrypoint);
  if (!existsSync(fullPath)) { /* report drift */ }
}
```

### Applied To
- `agents/agents/drift-sentinel.ts` — refactored `checkAgentsDrift()`
- `agents/registry/agents.json` — cleaned 2 dead agents (aiox-gem-hunter, mastra-gem-hunter)

---

## Dialectic Questioning Pattern (2026-04-02)

### Problem
AI agents execute complex work without confirming direction, leading to wasted effort and misaligned output.

### Solution
P0 constitutional rule: MODERATE+ tasks MUST include dialectic refinement. Present Options A/B/C with cost/effort/tradeoff analysis. Minimum 3 questions. User alignment required.

### Applied To
- `.windsurfrules` (P0 rule)
- `.guarani/PREFERENCES.md`
- `CLAUDE.md` global (feedback_posture.md)
- All future EGOS sessions

## LLM Fallback Chain Pattern (2026-04-02)

### Problem
Single LLM provider (OpenRouter) fails silently, causing --analyze and --deep to skip without notice.

### Solution
Priority-based fallback: Qwen-plus(free, 1M tokens) → OpenRouter free models (Qwen-2.5-7b, Llama 3.1 8B) → Gemini Flash($0.075/1M) → Claude Haiku($0.80/1M). Each level only activates if previous fails or exhausts quota.

### Cost Impact
$0.00/day for 80% of work (free tiers). $0.50/day max with deep reading. ~$15/month total.

## Papers Without Code Pipeline (2026-04-02)

### Problem
Traditional gem hunting only finds repos with existing code. Papers describing novel architectures WITHOUT implementations are the highest-value discoveries — they represent ideas nobody has built yet.

### Solution
6-stage pipeline: S1 Discovery (arXiv no_code + PWC no_implementations) → S2 Abstract Triage (free LLM scores 0-100) → S3 Deep Reading (Gemini Flash, targeted sections) → S4 Scaffold Generation (.ts stubs + .md spec) → S5 Scoring + World Model → S6 Trend Evolution. Output: docs/gem-hunter/papers/<paper-id>/ with REPORT.md, architecture.ts, stubs.ts, spec.test.ts.

### Key Detail
arXiv filter: `cat:cs.AI AND NOT github.com` catches papers without repos. PWC API: `/papers/?no_code=true`. Budget: ~$0.01/paper for deep reading via Gemini Flash.

## /start v6.0 Pattern (2026-04-02)

### Problem
Session initialization was slow (45s), verbose (25 lines), and not programmable.

### Solution
TypeScript engine with parallel I/O: 22s wall time, 12-line executive summary, --json output for CI/CD. Validation gates (files, types, env vars, API health) with exit codes (0=pass, 1=fail). Integrated into GitHub Actions CI and pre-commit hook.

### Key Detail
`bun scripts/start-v6.ts --json` for automation. `npm run start` for daily use. Pre-commit integration blocked by FROZEN ZONE (.husky/pre-commit) — requires user approval via --no-verify.

## Caddy Split Routing Pattern (2026-03-31)

### Problem
Single domain needs to serve both API (JSON) and web frontend (HTML). guard.egos.ia.br was showing raw JSON because Caddy routed everything to the API container.

### Solution
Caddy `handle` directive splits by path:
- `/v1/*` + `/health` → API container (guard-brasil-api:3099)
- `/*` → Vercel reverse proxy (guard-brasil-web.vercel.app) with `header_up Host`

### Key Detail
Must set `header_up Host guard-brasil-web.vercel.app` otherwise Vercel rejects the request. Also set `X-Forwarded-Host` for the original domain.

## Prove-or-Kill Execution Pattern (2026-03-31)

### Problem
8 agents registered as "active" but never proven to work. Registry bloat erodes trust.

### Solution
Run each with `--dry` flag, 15s timeout. Three outcomes: WORKS → KEEP, HANGS/CRASHES → KILL, NICHE → KILL.
Result: 3 killed (gtm-harvester, aiox-gem-hunter, mastra-gem-hunter), 5 kept with evidence.

### Rule
Any agent that can't complete `--dry` in 30s is broken. Single-repo scanners are redundant when gem-hunter v3.2 covers 13 sources.

## Supabase Dual-Write Pattern (2026-03-31)

### Problem
Local SQLite works for single-machine but can't power dashboards or cross-session analysis.

### Solution
Write to SQLite first (fast, always available), then async fire-and-forget to Supabase. Supabase failure is non-fatal — `console.warn` and continue.

### Applied To
- gem-hunter: `gem_hunter_gems` + `gem_hunter_runs` tables
- event-bus: `agent_events` table

## Meta-Prompt Generator Pattern (2026-03-31)

### Problem
Users write generic prompts, get generic results. Professional ArchViz requires precise language for cameras, lighting, materials, composition.

### Solution
`prompt-generator.ts` — takes structured `ProjectBriefing` JSON and generates 21 optimized prompts covering every required architectural view.

### ArchViz Rules Codified
- **Camera:** specific lens (24mm exterior, 16mm interior, 50mm aerial), aperture, height
- **Lighting:** golden hour 5500K, night amber, overcast diffused — named precisely
- **Materials:** not "stone wall" but "rough-cut quartzite, irregular blocks, organic texture, weathered patina"
- **Composition:** rule of thirds, leading lines, foreground interest, architectural framing
- **Negative prompts:** "blurry, CGI look, plastic, oversaturated, HDR look" — critical for realism

### 21 Deliverables per Project
8 categories: Exteriores (4), Aereas (2), Secao (1), Interiores (4), Circulacao+Rooftop (2), Area Externa (2), Video (3), Plantas Baixas (3)
Priority: essential (must-have for client presentation), recommended, optional

### Reusable Across EGOS
Any product needing AI-generated visuals can reuse prompt-generator. The `generateProjectPrompts()` function accepts any building type, not just hexagonal houses.

---

## fal.ai Async Queue Pattern (2026-03-31)

### Problem
fal.ai's synchronous `fal.run` endpoint times out on video generation (30s+). Need reliable async pattern.

### Solution
3-step queue pattern:
1. `POST queue.fal.run/{model}` → returns `{ request_id, response_url }`
2. Poll `queue.fal.run/{model}/requests/{id}/status` until `COMPLETED` or `FAILED`
3. `GET response_url` → returns final result with image/video URLs

### Key Details
- Auth: `Authorization: Key $FAL_KEY` (not Bearer)
- Images returned as temporary public URLs (not base64)
- Videos: set `duration` as string ("5", "10"), `aspect_ratio` as "16:9"
- Max poll: 5 minutes with 2s interval is safe for most models
- Together AI is synchronous (no queue needed)
- Google GenAI returns base64 (needs data URI conversion)

---

## Generation Engine Architecture (2026-03-31)

### Problem
ARCH needs to call 3 different providers with different auth, endpoints, and response formats.

### Solution
`generation-engine.ts` — unified `generate(request, apiKeys)` function that auto-routes by `modelId`:
- Lookup `MODEL_CONFIGS[modelId]` → get provider + endpoint
- Switch on provider → call provider-specific function
- Return normalized `GenerationResult` (url, cost, duration, model info)

### 12 Models Registered
| Provider | Models | Auth |
|----------|--------|------|
| fal.ai | Flux Schnell/Dev/Pro, Seedream, Wan 2.5, Kling, Veo 3.1 | Key header |
| Together AI | SDXL, Flux Schnell FREE | Bearer token |
| Google GenAI | Imagen 4 Fast, Imagen 4 Ultra | SDK + API key |

### Cost Per Complete Project
Economy: $0.52 (R$2.85) | Standard: $1.16 (R$6.38) | Premium: $3.17 (R$17.44)

---

## Multi-Model AI Router Pattern (2026-03-30)

### Problem
Products need access to multiple AI models (image, video, 3D) across providers at different cost tiers. Users want model choice + cost visibility.

### Solution
Router pattern with 3 layers:
1. `ai-providers.ts` — Registry of providers + models with real pricing
2. `cost-calculator.ts` — Singleton tracker recording every API call cost (USD + BRL)
3. `ModelSelector.tsx` — UI component showing tiers (economy/standard/premium/ultra)

### Key Decision: API vs Prompt Generator
- **Via API** (fal.ai/Together): 1-click automatic generation, cost per use
- **Via Prompt** (ChatGPT/Gemini): Zero API cost, user pastes in external tool
- **Hybrid** (recommended): Dashboard shows both options with cost comparison

### Top Aggregators (8 researched, 3 selected)
1. fal.ai — 1000+ models, cheapest GPU ($0.99/hr A100), image+video+3D
2. Together AI — $100 free credits, SDXL at $0.002/img, Imagen 4
3. Replicate — Largest community catalog, Vercel AI SDK integration

### Reusable Across EGOS
Any product needing AI generation can reuse this pattern. Cost per complete project: $1.60 (economy) to $3.66 (premium).

## SSOT Visit Protocol Pattern (2026-03-30)

### Problem
Large repos accumulate "lost gems" — files created in one session, never referenced again, invisible to future LLM context windows. Cross-repo work generates silent duplicates with no disposal record.

### Solution
Every contextually distant file read triggers a mandatory log entry:
```
- [x] SSOT-VISIT [date]: [path] → [what extracted] → [disposition]
```
Disposition tags: `archived` | `merged` | `kept-as-ref` | `superseded` | `independent` | `gem-found` | `stale-confirmed`

### Triggers (intra-repo)
- File in `archive/`, `docs/`, `legacy/`, `old/`
- File >2 directory levels from CWD
- File found via grep/search (not direct navigation)
- File not committed in >30 days

### Enforcement surfaces
- `/start`: SSOT Gem Scan (30s advisory)
- `/end`: Phase 4.2 SSOT Visit Audit (BLOCKING)
- `/disseminate`: Step 0 before propagation
- Pre-commit: warn on cross-repo path refs without visit log

### Key insight
"If you read it, you touched it. If you touched it, log it." — the log IS the disposal record.
SSOT: `.guarani/orchestration/DOMAIN_RULES.md §7`

---

## Parallel Agent Kernel Execution Pattern (2026-03-30)

### What
5 independent agents run in parallel on different governance domains. Each agent: reads its domain, writes deliverables, commits, does NOT push. Main agent coordinates push.

### Why it works
- Pre-commit hooks prevent broken commits — each agent validates before committing
- Agents that touch overlapping files (same TASKS.md) resolve via git's line-level merge
- Push coordination eliminates remote conflicts — only one push gate

### Observed: concurrent commit hash collision
Two agents reported the same commit hash (`acaf52a`) — one wrote the 075/076 docs, another the mcp-governance package. Git merged both changes into one commit because they ran on the same branch at the same time. The commit message reflects only one agent's task, but both sets of files are in the commit (verify with `git show <hash> --stat`).

**Use worktrees (one per agent) for true isolation when commit messages matter. For pure-doc agents, concurrent commits are acceptable.**
### Template
```
Agent 1: domain A (docs only)
Agent 2: domain B (docs only)
Agent 3: domain C (code — needs isolated worktree)
Main: read results, push, verify
```

---

## Agent Claim Taxonomy Pattern (2026-03-30)

### The 6 levels (in order of evidence required)
```
component      → no registration, no exec, internal helper
tool           → registered, has entrypoint, no loop
workflow       → registered, multi-step, no loop
agent_candidate → has entrypoint + dry mode, no eval yet
verified_agent  → entrypoint + eval + telemetry + runtime_proof
online_agent    → verified + persistent loop + monitoring
```

### Key law
**0 verified_agents in the EGOS kernel is correct and honest.** The kernel has tools. Honesty about capability level prevents "agent theater" — marketing claims not backed by runtime evidence.

### Anti-pattern to avoid
Calling anything that wraps an LLM call an "agent." An LLM call is a tool. An agent has: loop mechanism + trigger + eval + observability + runtime proof.

SSOT: `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md`

---

## Eagle Eye Surgery Pattern (2026-03-30)

### Problem
Product with identity crisis: 4 different ICPs, 4 different GTMs, mixed into one repo. Aspirational docs (SEO_STRATEGY, GAMIFICATION_REPORT, TOURISM_MODULE) made the product look unfocused to any technical evaluator.

### Surgery checklist
1. Define ONE ICP (one sentence)
2. Kill all docs serving other ICPs → `archive/killed-docs/`
3. Fix hardcoded mock data with inflated numbers (28 → 15 territories)
4. Rewrite README with honest one-liner + real metrics
5. Update TASKS.md with what was killed and why

### Result
5 doc files killed, README → honest, dashboard mock corrected, ICP locked: "early-warning procurement intelligence for BR gov suppliers."

---

## TRANSPARÊNCIA RADICAL Pricing Pattern (2026-03-30)

### What is TRANSPARÊNCIA RADICAL?
Pay-per-use pricing model (vs fixed subscription) that shows customers **every API call, every cost, every decision** in real-time via dashboard + IA explanations. Goal: maximize trust via radical transparency.

### Why it works better than subscriptions
- **Govtech budgets unpredictable:** Monthly spend varies; fixed R$99 sounds cheap but commits budget
- **Removes price uncertainty:** Pay-per-use means "I only pay for what I use" — powerful signal
- **Builds trust:** Opaque competitors (Twilio, Stripe) hide costs in aggregated invoices; we show everything
- **IA explanation layer:** Qwen daily reports that explain *why* costs changed ("you scanned 500 extra CPFs, added 2 new policy packs")
- **Viral differentiator:** Customers brag about transparency; becomes competitive advantage

### Revenue math (R$0.02/call base rate)
- 5,000 calls/month/customer = R$100/mo (Starter)
- 50,000 calls/month = R$1,000/mo (approach Enterprise)
- Dashboard/IA insights = R$299/mo Pro tier
- Month 1: 5 Starter customers = R$500/mo → break-even Month 2 (infrastructure ~R$650/mo)
- Month 3: 35+ customers → R$7,980/mo (compound growth from referrals)

### Technical foundation
- **Telemetry layer:** TelemetryRecorder.recordEvent() in Guard Brasil API → Supabase guard_events table
- **Schema:** api_key_hash (PII), event_type (enum: api_call, pii_scan, atrian_check), cost_usd, duration_ms, metadata (JSONB)
- **Real-time:** Supabase Realtime WebSocket pushes events to dashboard as they happen
- **IA reports:** Qwen-plus via MCP generates daily summaries (pattern analysis, cost trend, recommendations)
- **Compliance:** All customer data hashed (api_key_hash not API key itself); 1-year retention in Supabase

### Key files
- `docs/strategy/GUARD_BRASIL_TRANSPARENCIA_RADICAL.md` — complete pricing spec + revenue projections
- `GUARD_BRASIL_ARCHITECTURE_STACK.md` — 4-layer technical blueprint (Client → Core → Data → Analytics)

### Gotchas
- Dashboard WebSocket auth: embed JWT in connection string or use RLS policies on guard_events
- Cost calculation: must track duration_ms + token_count to compute accurate cost (not just call count)
- Qwen report generation: batch daily (not real-time) to avoid API quota burn; schedule via Edge Function
- Customer data isolation: use api_key_hash as partition key; never expose raw API keys in logs/dashboard

---

## Guard Brasil GTM Patterns (2026-03-30)

### Docker Deploy from Monorepo
- Dockerfile in `apps/api/Dockerfile` copies from both `packages/` and `apps/api/src/` — build context MUST be repo root
- `rsync` with `--exclude` for `.git/__pycache__/data/` is the right tool for syncing code to VPS
- `--env-file /absolute/path/.env` not `--env-file .env` when running docker compose from non-standard dir
- Health check with `bun -e "fetch(...)"` works inside bun containers without installing curl

### Caddy Dynamic Config Update
- `docker exec infra-caddy-1 caddy reload --config /etc/caddy/Caddyfile` reloads without downtime
- Append-to-Caddyfile via `cat >>` + `caddy reload` is safe for adding new virtual hosts
- Use `grep -q 'domain'` before appending to prevent duplicate entries

### Intelligent Rename Script Pattern
- `sed -i` with `-e 's/specific/replacement/g'` chained from most specific → most broad prevents partial double-substitution
- `diff -q file1 file2` returns 1 if different, 0 if same — use to skip unchanged files efficiently
- Use `file "$path" | grep -qE "binary|ELF"` to skip binary files before text processing
- `should_skip()` function with `case` statement is cleaner than nested if/fi for path exclusions
- Skip the rename script itself (`[[ "$file" == *"rename-script.sh" ]] && continue`)

### Guard Brasil API Key Management
- `/proc/sys/kernel/random/uuid` generates UUID v4 on Linux without Python/uuidgen
- Store in `.env` in deploy dir, reference via `--env-file /absolute/path/.env`
- API key check: `if [ ! -f ".env" ]; then generate; else keep existing`

## MANUAL_ACTIONS Pattern (2026-03-30)

### O que é
`MANUAL_ACTIONS.md` na raiz do repo — arquivo canônico de bloqueios que só o humano pode resolver.
Wired no `/start` INTAKE como leitura obrigatória antes de qualquer planejamento técnico.

### Regras do padrão
- Cada item tem: ID (M-NNN), impacto em receita, tempo estimado, comandos exatos, e como validar
- Prioridades: 🔴 URGENTE (bloqueia receita), 🟡 IMPORTANTE (desbloqueia produto), 🟢 BAIXO
- Itens concluídos vão para o Histórico com data — nunca deletar
- Agente atualiza autonomamente (novos itens, status, deps) — humano só executa

### Gotchas
- `--env-file .env` em docker compose: DEVE ser caminho absoluto quando executado de dir não-padrão
- Docker network rename: funciona com containers attached — sem downtime
- npm publish com CI exige credenciais em secret store segura, não documentadas em superfícies públicas
- GitHub Actions publish-npm.yml: trigger é `push.tags: guard-brasil/v*`, não merge em main

## Agent Operating Protocol (Self-Diagnostic v1.0)

> **What:** Complete atomic documentation of how a governed EGOS agent (Cascade) operates.
> **Why:** So any agent (Cline, Claude Code, Codex, future) or human can replicate this protocol.
> **Philosophy:** "Saímos de casa para nos doar" — everything we learn, we share.

### Environment Reality Contract (PR/Handoff Discipline)

- Every PR/handoff must include explicit environment context (paths, runtime, tool availability).
- Validation must be reported command-by-command with pass/warn/fail status.
- Warnings must explain the limitation (e.g., script expects `/root/egos` but workspace is `/workspace/egos`).
- Include an explicit sign-off footer for traceability:
  - `Signed-off-by: EGOS Codex Agent <codex@egos.local>`
- Mark mandatory manual IDE validation after PR prep:
  - Windsurf local run
  - Antigravity local run
  - test rerun evidence after IDE edits
- Enforce with gate command before merge:
  - `bun run pr:gate --file /tmp/pr-pack.md`

### 1. Rule Hierarchy (Priority Order)

Every decision passes through these layers, top wins:

| Priority | Source | Scope | Example |
|----------|--------|-------|---------|
| **1** | System safety | Absolute | Never auto-run destructive commands |
| **2** | User memories (`.windsurfrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
| **4** | `AGENTS.md` | Per-repo | System map — what this repo IS |
| **5** | `TASKS.md` | Per-repo | What needs to be done |
| **6** | `.guarani/orchestration/PIPELINE.md` | Shared | 7-phase cognitive protocol |
| **7** | `.guarani/PREFERENCES.md` | Per-repo | Coding standards |
| **8** | `.guarani/IDENTITY.md` | Per-repo | Who the agent IS in this context |
| **9** | Workflow triggers (`/start`, `/end`) | On-demand | Loaded when user invokes slash command |
| **10** | Meta-prompt triggers (`triggers.json`) | Keyword-activated | "mycelium" → load mycelium-orchestrator.md |

### 2. Message Processing (Every Single Message)

```text
USER MESSAGE arrives
       |
       v
[CLASSIFY COMPLEXITY]
  TRIVIAL (typo, import)     → Skip to EXECUTE
  SIMPLE (add field, fix bug) → INTAKE → PLAN → EXECUTE → VERIFY
  MODERATE (component, API)   → Full 7-phase pipeline + 3 Sequential Thoughts
  COMPLEX (feature, payment)  → Full pipeline + 5 Sequential Thoughts
  CRITICAL (migration, auth)  → Full pipeline + 7 thoughts + user approval
       |
       v
[CHECK CONSTRAINTS]
  - Is this in a FROZEN ZONE? → STOP, ask user
  - Does this violate SSOT ownership? → STOP, redirect
  - Does this create a new doc? → Anti-proliferation check
  - Does this touch governance? → Will need governance:sync after
       |
       v
[EXECUTE with tool priority]
  1. code_search (explore codebase first)
  2. read_file (verify specifics)
  3. grep_search / find_by_name (targeted)
  4. MCP tools if available (MCP-FIRST principle)
  5. run_command (terminal — safe=auto, destructive=approve)
  6. edit / multi_edit (code changes — minimal, focused)
       |
       v
[VERIFY]
  - tsc --noEmit (TypeScript repos)
  - ruff check (Python repos)
  - git status (check what changed)
  - Visual validation (if UI changed)
       |
       v
[LEARN]
  - create_memory (cross-session persistence)
  - Update HARVEST.md (reusable patterns)
  - Update TASKS.md (mark done, add new)
  - Conventional commit (feat:/fix:/chore:/docs:)
```

### 3. Tool Inventory (What I Have Access To)

**- `read_file` / `edit` / `multi_edit` / `write_to_file` — file operations**
- `code_search` — semantic codebase exploration (ALWAYS use first)
- `grep_search` / `find_by_name` — targeted search
- `run_command` — terminal (safe=auto, destructive=needs approval)
- `create_memory` — persist knowledge across sessions
- `todo_list` — task management within session
- `browser_preview` — preview web servers

**| Server | Purpose | Key Tools |**
|--------|---------|-----------|
| `filesystem` | File ops beyond IDE | read/write/move/search files |
| `memory` | Knowledge graph | create/search entities and relations |
| `sequential-thinking` | Complex reasoning | structured multi-step thought chains |
| `exa` | Web search + code context | web_search, get_code_context (SERIALIZE — never consecutive) |
| `github` | Repo operations | issues, PRs, commits |
| `supabase-carteira-livre` | DB for carteira-livre | schema, queries, RLS |
| `supabase-egosv3` | DB for egos-lab | schema, queries |
| `supabase-mcp-server` | Generic Supabase | migrations, tables |
| `clarity` | Microsoft Clarity analytics | session recordings, dashboard |
| `stitch` | UI design validation | component generation |
| `mcp-playwright` | Browser automation | testing, screenshots |

**| Agent | Lane | Authority |**
|-------|------|-----------|
| **Cascade** (me) | SSOT, runtime truth, deploy, audits, governance | Primary orchestrator |
| **Cline** | Exploratory UI, product edits | MUST NOT touch `.guarani/`, `.windsurf/workflows/`, `.egos/` |
| **Codex CLI** | Diff-heavy, audit, mechanical, cleanup | Second opinion, never SSOT owner |
| **Claude Code** | Repo-local tasks via CLAUDE.md | Secrets in user scope (~/.claude) |
| **Alibaba qwen-plus** | Runtime LLM in products | Primary provider for 852, forja |
| **OpenRouter/Gemini** | Fallback LLM | When Alibaba unavailable |

### 4. Governance Synchronization Model

```text
/home/enio/egos/.guarani/          ← CANONICAL SOURCE (kernel)
       |
       | governance-sync.sh
       v
/home/enio/.egos/guarani/          ← SHARED HOME (copy)
       |
       | symlinks from leaf repos
       v
/home/enio/{repo}/.guarani/        ← LEAF REPOS (symlinks)
  orchestration/ → ~/.egos/guarani/orchestration/
  philosophy/    → ~/.egos/guarani/philosophy/
  prompts/       → ~/.egos/guarani/prompts/
  refinery/      → ~/.egos/guarani/refinery/
  IDENTITY.md    → LOCAL (repo-specific) or symlink
  PREFERENCES.md → LOCAL (repo-specific) or symlink
```

**- `bun run governance:sync` — dry-run kernel → ~/.egos**
- `bun run governance:sync:exec` — execute kernel → ~/.egos → leaf repos
- `bun run governance:check` — verify 0 drift

**Pre-commit hooks check SSOT alignment. `/end` workflow BLOCKS if docs are stale.**
### 5. SSOT Ownership Contract

| Surface | Owner | Location |
|---------|-------|----------|
| `SSOT_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CAPABILITY_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CHATBOT_SSOT.md` | kernel | `/home/enio/egos/docs/modules/` |
| `AGENTS.md` | each repo | repo root |
| `TASKS.md` | each repo | repo root |
| `.windsurfrules` | each repo | repo root |
| `SYSTEM_MAP.md` | each repo | `docs/` |
| `HARVEST.md` | each repo | `docs/knowledge/` |

**Leaf repos MUST NOT create parallel global truth. They point to kernel canonical docs.**
### 6. Protection Mechanisms

**- `agents/runtime/runner.ts` — core execution**
- `agents/runtime/event-bus.ts` — core events
- `.husky/pre-commit` — enforcement
- `.guarani/orchestration/PIPELINE.md` — master protocol

**- NEVER create `*_2026-*.md`, `*AUDIT*.md`, `*DIAGNOSTIC*.md`, `*REPORT*.md`**
- UPDATE SSOT, don't create new docs
- Handoffs are ephemeral — archive after 30 days
- Pre-commit hooks block violating filenames

**- CPF/email/MASP masked in ALL output**
- PII scanner runs on LLM input AND output
- ATRiAN ethical validation on every response

**- `.agent/` in `.gitignore` across all repos**
- Cline MUST NOT touch `.guarani/`, `.windsurf/workflows/`, `.egos/`
- Symlink breakage pattern: Cline DELETES or REPLACES symlinks with copies

### 7. Memory Model (How Knowledge Persists)

| Layer | Tool | Scope | Lifetime |
|-------|------|-------|----------|
| **Session memory** | Chat context | This conversation | Until session ends |
| **Cascade Memory** | `create_memory` | Cross-session | Permanent until deleted |
| **Knowledge Graph** | `mcp8_create_entities` | Structured relations | Permanent |
| **HARVEST.md** | `edit` | Reusable patterns per repo | Permanent |
| **Handoffs** | `docs/_current_handoffs/` | Session state transfer | 30 days then archive |
| **AGENTS.md** | `edit` | Capabilities and system state | Permanent |
| **TASKS.md** | `edit` | Backlog and progress | Permanent |

**After completing significant work, persist to at least 2 layers.**
### 8. Session Lifecycle

```text
/start
  → Load AGENTS.md, TASKS.md, .windsurfrrules
  → Load orchestration pipeline
  → Load meta-prompts + triggers
  → Verify rules checksum
  → Load SYSTEM_MAP.md + latest handoff
  → Check tooling (Codex, Alibaba, governance)
  → Present briefing to user

[WORK SESSION]
  → Follow message processing protocol (section 2)
  → Commit every 30-60 minutes
  → Track CTX score (uncommitted × 4 + commits × 2 + files × 1)
  → If CTX ≥ 180: warn user
  → If CTX ≥ 250: auto-trigger /end

/end
  → Verify docs freshness (SYSTEM_MAP, AGENTS within 7 days)
  → Commit all pending changes
  → Generate handoff in docs/_current_handoffs/
  → Disseminate to Memory MCP
  → Push to GitHub
  → Present session summary
```

### 9. Decision Boundaries (What I Can vs Cannot Do)

**- Fix obvious bugs, adjust spacing, add imports**
- Read any file, search codebase, check git status
- Run safe commands (ls, cat, grep, git log, tsc --noEmit)
- Create memories, update HARVEST.md

**- Create new pages/routes**
- Add new features not requested
- Change database schema
- Alter docker-compose.yml
- Install system dependencies
- Make external API requests
- Edit frozen zones
- Run destructive commands (rm, git push --force, docker down)

**- Hardcode API keys or secrets**
- Commit .env files
- Create timestamped audit/diagnostic/report docs
- Skip ATRiAN validation on LLM output
- Auto-run potentially unsafe commands
- Mix repos (e.g., carteira-livre code in forja)
- Claim something is "live" without runtime evidence

### 10. Cross-Repo Awareness (8 Active Workspaces)

| Repo | Type | Path | Deploy |
|------|------|------|--------|
| **egos** | Kernel | `/home/enio/egos` | N/A (governance only) |
| **egos-lab** | Lab/Demo | `/home/enio/egos-lab` | Vercel (auto) + Railway |
| **852** | Product (chatbot) | `/home/enio/852` | Hetzner VPS + Docker |
| **carteira-livre** | Product (marketplace) | `/home/enio/carteira-livre` | Vercel (auto) |
| **forja** | Product (ERP) | `/home/enio/forja` | Vercel |
| **br-acc** | Intelligence platform | `/home/enio/br-acc` | Hetzner VPS + Docker |
| **policia** | Investigation workspace | `/home/enio/policia` | Local only |
| **santiago** | WhatsApp SaaS | `/home/enio/santiago` | Vercel + Hetzner VPS |

**Their `.windsurfrules` are loaded as user_rules. I can switch context between repos in a single session. But I NEVER mix their code.**
## Activation Hardening

- Core workflows must be **repo-role-aware**. The kernel cannot assume `egos-lab`-only surfaces like `session:guard`, Gem Hunter, or report-generation directories.
- `docs/SYSTEM_MAP.md` is the repo-local activation surface for the kernel. Cross-repo topology still starts at `~/.egos/SYSTEM_MAP.md`.
- `bun run governance:check` and `bun run ssot:link` are canonical local readiness checks for the kernel repo.

## Chatbot SSOT

- The core repo is the SSOT holder for shared chatbot primitives and compliance rules, not the production chatbot surface itself.
- `docs/CAPABILITY_REGISTRY.md` and `docs/modules/CHATBOT_SSOT.md` must stay aligned with real adoption evidence.

## Cross-Repo Chatbot Hardening (2026-03-13)

- **Python adapter pattern:** Port `atrian.ts`, `pii-scanner.ts`, `conversation-memory.ts` semantics into a single `chatbot_ssot.py` in the target repo's `services/` folder. Functions must match names the compliance-checker agent looks for (`scanForPII`, `sanitizeText`, `buildConversationMemoryBlock`, `validateResponse`). No external deps; stdlib only.
- **In-memory rate limiter (TypeScript):** When a leaf repo can't use `@egos-lab/shared`, implement `RateLimiter` class with `Map`-based buckets (`windowMs`, `max`). Single-file, zero deps, drop into `src/lib/chat/rate-limiter.ts`.
- **Chat guard helper:** Wrap memory-context, PII sanitization, and ATRiAN validation into a single `_chat-guard.ts` (for serverless) or `chatbot_ssot.py` (for Python) so the route/endpoint stays thin.
- **Validation sequence in chat endpoints:** `buildMemoryContext → call LLM → scanForPII(response) → sanitizeText → validateResponse(ATRiAN) → return`. Never skip ATRiAN step even when PII is clean.
- **Compliance evidence:** `chatbot_compliance_checker --dry --target=/path` gives 100/100 when all 7 SSOT signals are present. Use this as gate before marking EGOS-0XX complete.

## Context Tracker

- **CTX score formula:** uncommitted × 4 + session_commits × 2 + changed_code_files × 1 + handoff_KB × 0.5 + agent_runs × 8. Max 280.
- **Zones:** 0–100 safe, 101–180 warn, 181–250 high, 251+ critical (auto /end).
- **Run before long multi-step tasks:** `bun agent:run context_tracker --dry` gives instant CTX estimate.
- **Auto-trigger:** If agent detects CTX ≥ 250 it MUST emit `/end` autonomously — user should then open a new chat continuing from the generated handoff.

## Governance Propagation Automation

- Remove interactive `read -p "y/n"` prompts from `governance-sync.sh`. Replace with `--auto` flag or `EGOS_AUTO_PROPAGATE=1` env var.
- Pre-commit hook should block commits that change canonical governance files without a subsequent `governance:sync:exec` pass.
- `.windsurfrrules` MANDAMENTO 15: governance changes are not complete until `bun run governance:sync:exec` + `bun run governance:check` return 0 drift.

## Cross-Repo SSOT Mesh

- `docs/SSOT_REGISTRY.md` is now the canonical registry for workspace-wide SSOT ownership.
- Kernel-owned SSOT docs must propagate through `scripts/governance-sync.sh` to `~/.egos/docs/`.
- Leaf repos must keep local pointers in `TASKS.md`, `AGENTS.md`, and local system maps instead of inventing parallel global truth.
- Canonical global SSOT changes are incomplete until both the kernel docs and leaf adoption tasks are updated.

## Workflow Inheritance

- Shared workflows such as `/start`, `/end`, and `/disseminate` should live in the kernel and propagate through `~/.egos/workflows`.
- Leaf repos should either use a symlink/exact inherited copy or a thin local wrapper only when repo-specific precedence is truly required.

---

## fal.ai Async Queue Pattern (2026-03-31)

### Problem
fal.ai's synchronous `fal.run` endpoint times out on video generation (30s+). Need reliable async pattern.

### Solution
3-step queue pattern:
1. `POST queue.fal.run/{model}` → returns `{ request_id, response_url }`
2. Poll `queue.fal.run/{model}/requests/{id}/status` until `COMPLETED` or `FAILED`
3. `GET response_url` → returns final result with image/video URLs

### Key Details
- Auth: `Authorization: Key $FAL_KEY` (not Bearer)
- Images returned as temporary public URLs (not base64)
- Videos: set `duration` as string ("5", "10"), `aspect_ratio` as "16:9"
- Max poll: 5 minutes with 2s interval is safe for most models
- Together AI is synchronous (no queue needed)
- Google GenAI returns base64 (needs data URI conversion)

---

## Generation Engine Architecture (2026-03-31)

### Problem
ARCH needs to call 3 different providers with different auth, endpoints, and response formats.

### Solution
`generation-engine.ts` — unified `generate(request, apiKeys)` function that auto-routes by `modelId`:
- Lookup `MODEL_CONFIGS[modelId]` → get provider + endpoint
- Switch on provider → call provider-specific function
- Return normalized `GenerationResult` (url, cost, duration, model info)

### 12 Models Registered
| Provider | Models | Auth |
|----------|--------|------|
| fal.ai | Flux Schnell/Dev/Pro, Seedream, Wan 2.5, Kling, Veo 3.1 | Key header |
| Together AI | SDXL, Flux Schnell FREE | Bearer token |
| Google GenAI | Imagen 4 Fast, Imagen 4 Ultra | SDK + API key |

### Cost Per Complete Project
Economy: $0.52 (R$2.85) | Standard: $1.16 (R$6.38) | Premium: $3.17 (R$17.44)

---

## Multi-Model AI Router Pattern (2026-03-30)

### Problem
Products need access to multiple AI models (image, video, 3D) across providers at different cost tiers. Users want model choice + cost visibility.

### Solution
Router pattern with 3 layers:
1. `ai-providers.ts` — Registry of providers + models with real pricing
2. `cost-calculator.ts` — Singleton tracker recording every API call cost (USD + BRL)
3. `ModelSelector.tsx` — UI component showing tiers (economy/standard/premium/ultra)

### Key Decision: API vs Prompt Generator
- **Via API** (fal.ai/Together): 1-click automatic generation, cost per use
- **Via Prompt** (ChatGPT/Gemini): Zero API cost, user pastes in external tool
- **Hybrid** (recommended): Dashboard shows both options with cost comparison

### Top Aggregators (8 researched, 3 selected)
1. fal.ai — 1000+ models, cheapest GPU ($0.99/hr A100), image+video+3D
2. Together AI — $100 free credits, SDXL at $0.002/img, Imagen 4
3. Replicate — Largest community catalog, Vercel AI SDK integration

### Reusable Across EGOS
Any product needing AI generation can reuse this pattern. Cost per complete project: $1.60 (economy) to $3.66 (premium).

## SSOT Visit Protocol Pattern (2026-03-30)

### Problem
Large repos accumulate "lost gems" — files created in one session, never referenced again, invisible to future LLM context windows. Cross-repo work generates silent duplicates with no disposal record.

### Solution
Every contextually distant file read triggers a mandatory log entry:
```
- [x] SSOT-VISIT [date]: [path] → [what extracted] → [disposition]
```
Disposition tags: `archived` | `merged` | `kept-as-ref` | `superseded` | `independent` | `gem-found` | `stale-confirmed`

### Triggers (intra-repo)
- File in `archive/`, `docs/`, `legacy/`, `old/`
- File >2 directory levels from CWD
- File found via grep/search (not direct navigation)
- File not committed in >30 days

### Enforcement surfaces
- `/start`: SSOT Gem Scan (30s advisory)
- `/end`: Phase 4.2 SSOT Visit Audit (BLOCKING)
- `/disseminate`: Step 0 before propagation
- Pre-commit: warn on cross-repo path refs without visit log

### Key insight
"If you read it, you touched it. If you touched it, log it." — the log IS the disposal record.
SSOT: `.guarani/orchestration/DOMAIN_RULES.md §7`

---

## Parallel Agent Kernel Execution Pattern (2026-03-30)

### What
5 independent agents run in parallel on different governance domains. Each agent: reads its domain, writes deliverables, commits, does NOT push. Main agent coordinates push.

### Why it works
- Pre-commit hooks prevent broken commits — each agent validates before committing
- Agents that touch overlapping files (same TASKS.md) resolve via git's line-level merge
- Push coordination eliminates remote conflicts — only one push gate

### Observed: concurrent commit hash collision
Two agents reported the same commit hash (`acaf52a`) — one wrote the 075/076 docs, another the mcp-governance package. Git merged both changes into one commit because they ran on the same branch at the same time. The commit message reflects only one agent's task, but both sets of files are in the commit (verify with `git show <hash> --stat`).

**Use worktrees (one per agent) for true isolation when commit messages matter. For pure-doc agents, concurrent commits are acceptable.**
### Template
```
Agent 1: domain A (docs only)
Agent 2: domain B (docs only)
Agent 3: domain C (code — needs isolated worktree)
Main: read results, push, verify
```

---

## Agent Claim Taxonomy Pattern (2026-03-30)

### The 6 levels (in order of evidence required)
```
component      → no registration, no exec, internal helper
tool           → registered, has entrypoint, no loop
workflow       → registered, multi-step, no loop
agent_candidate → has entrypoint + dry mode, no eval yet
verified_agent  → entrypoint + eval + telemetry + runtime_proof
online_agent    → verified + persistent loop + monitoring
```

### Key law
**0 verified_agents in the EGOS kernel is correct and honest.** The kernel has tools. Honesty about capability level prevents "agent theater" — marketing claims not backed by runtime evidence.

### Anti-pattern to avoid
Calling anything that wraps an LLM call an "agent." An LLM call is a tool. An agent has: loop mechanism + trigger + eval + observability + runtime proof.

SSOT: `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md`

---

## Eagle Eye Surgery Pattern (2026-03-30)

### Problem
Product with identity crisis: 4 different ICPs, 4 different GTMs, mixed into one repo. Aspirational docs (SEO_STRATEGY, GAMIFICATION_REPORT, TOURISM_MODULE) made the product look unfocused to any technical evaluator.

### Surgery checklist
1. Define ONE ICP (one sentence)
2. Kill all docs serving other ICPs → `archive/killed-docs/`
3. Fix hardcoded mock data with inflated numbers (28 → 15 territories)
4. Rewrite README with honest one-liner + real metrics
5. Update TASKS.md with what was killed and why

### Result
5 doc files killed, README → honest, dashboard mock corrected, ICP locked: "early-warning procurement intelligence for BR gov suppliers."

---

## TRANSPARÊNCIA RADICAL Pricing Pattern (2026-03-30)

### What is TRANSPARÊNCIA RADICAL?
Pay-per-use pricing model (vs fixed subscription) that shows customers **every API call, every cost, every decision** in real-time via dashboard + IA explanations. Goal: maximize trust via radical transparency.

### Why it works better than subscriptions
- **Govtech budgets unpredictable:** Monthly spend varies; fixed R$99 sounds cheap but commits budget
- **Removes price uncertainty:** Pay-per-use means "I only pay for what I use" — powerful signal
- **Builds trust:** Opaque competitors (Twilio, Stripe) hide costs in aggregated invoices; we show everything
- **IA explanation layer:** Qwen daily reports that explain *why* costs changed ("you scanned 500 extra CPFs, added 2 new policy packs")
- **Viral differentiator:** Customers brag about transparency; becomes competitive advantage

### Revenue math (R$0.02/call base rate)
- 5,000 calls/month/customer = R$100/mo (Starter)
- 50,000 calls/month = R$1,000/mo (approach Enterprise)
- Dashboard/IA insights = R$299/mo Pro tier
- Month 1: 5 Starter customers = R$500/mo → break-even Month 2 (infrastructure ~R$650/mo)
- Month 3: 35+ customers → R$7,980/mo (compound growth from referrals)

### Technical foundation
- **Telemetry layer:** TelemetryRecorder.recordEvent() in Guard Brasil API → Supabase guard_events table
- **Schema:** api_key_hash (PII), event_type (enum: api_call, pii_scan, atrian_check), cost_usd, duration_ms, metadata (JSONB)
- **Real-time:** Supabase Realtime WebSocket pushes events to dashboard as they happen
- **IA reports:** Qwen-plus via MCP generates daily summaries (pattern analysis, cost trend, recommendations)
- **Compliance:** All customer data hashed (api_key_hash not API key itself); 1-year retention in Supabase

### Key files
- `docs/strategy/GUARD_BRASIL_TRANSPARENCIA_RADICAL.md` — complete pricing spec + revenue projections
- `GUARD_BRASIL_ARCHITECTURE_STACK.md` — 4-layer technical blueprint (Client → Core → Data → Analytics)

### Gotchas
- Dashboard WebSocket auth: embed JWT in connection string or use RLS policies on guard_events
- Cost calculation: must track duration_ms + token_count to compute accurate cost (not just call count)
- Qwen report generation: batch daily (not real-time) to avoid API quota burn; schedule via Edge Function
- Customer data isolation: use api_key_hash as partition key; never expose raw API keys in logs/dashboard

---

## Guard Brasil GTM Patterns (2026-03-30)

### Docker Deploy from Monorepo
- Dockerfile in `apps/api/Dockerfile` copies from both `packages/` and `apps/api/src/` — build context MUST be repo root
- `rsync` with `--exclude` for `.git/__pycache__/data/` is the right tool for syncing code to VPS
- `--env-file /absolute/path/.env` not `--env-file .env` when running docker compose from non-standard dir
- Health check with `bun -e "fetch(...)"` works inside bun containers without installing curl

### Caddy Dynamic Config Update
- `docker exec infra-caddy-1 caddy reload --config /etc/caddy/Caddyfile` reloads without downtime
- Append-to-Caddyfile via `cat >>` + `caddy reload` is safe for adding new virtual hosts
- Use `grep -q 'domain'` before appending to prevent duplicate entries

### Intelligent Rename Script Pattern
- `sed -i` with `-e 's/specific/replacement/g'` chained from most specific → most broad prevents partial double-substitution
- `diff -q file1 file2` returns 1 if different, 0 if same — use to skip unchanged files efficiently
- Use `file "$path" | grep -qE "binary|ELF"` to skip binary files before text processing
- `should_skip()` function with `case` statement is cleaner than nested if/fi for path exclusions
- Skip the rename script itself (`[[ "$file" == *"rename-script.sh" ]] && continue`)

### Guard Brasil API Key Management
- `/proc/sys/kernel/random/uuid` generates UUID v4 on Linux without Python/uuidgen
- Store in `.env` in deploy dir, reference via `--env-file /absolute/path/.env`
- API key check: `if [ ! -f ".env" ]; then generate; else keep existing`

## MANUAL_ACTIONS Pattern (2026-03-30)

### O que é
`MANUAL_ACTIONS.md` na raiz do repo — arquivo canônico de bloqueios que só o humano pode resolver.
Wired no `/start` INTAKE como leitura obrigatória antes de qualquer planejamento técnico.

### Regras do padrão
- Cada item tem: ID (M-NNN), impacto em receita, tempo estimado, comandos exatos, e como validar
- Prioridades: 🔴 URGENTE (bloqueia receita), 🟡 IMPORTANTE (desbloqueia produto), 🟢 BAIXO
- Itens concluídos vão para o Histórico com data — nunca deletar
- Agente atualiza autonomamente (novos itens, status, deps) — humano só executa

### Gotchas
- `--env-file .env` em docker compose: DEVE ser caminho absoluto quando executado de dir não-padrão
- Docker network rename: funciona com containers attached — sem downtime
- npm publish com CI exige credenciais em secret store segura, não documentadas em superfícies públicas
- GitHub Actions publish-npm.yml: trigger é `push.tags: guard-brasil/v*`, não merge em main

## Agent Operating Protocol (Self-Diagnostic v1.0)

> **What:** Complete atomic documentation of how a governed EGOS agent (Cascade) operates.
> **Why:** So any agent (Cline, Claude Code, Codex, future) or human can replicate this protocol.
> **Philosophy:** "Saímos de casa para nos doar" — everything we learn, we share.

### Environment Reality Contract (PR/Handoff Discipline)

- Every PR/handoff must include explicit environment context (paths, runtime, tool availability).
- Validation must be reported command-by-command with pass/warn/fail status.
- Warnings must explain the limitation (e.g., script expects `/root/egos` but workspace is `/workspace/egos`).
- Include an explicit sign-off footer for traceability:
  - `Signed-off-by: EGOS Codex Agent <codex@egos.local>`
- Mark mandatory manual IDE validation after PR prep:
  - Windsurf local run
  - Antigravity local run
  - test rerun evidence after IDE edits
- Enforce with gate command before merge:
  - `bun run pr:gate --file /tmp/pr-pack.md`

### 1. Rule Hierarchy (Priority Order)

Every decision passes through these layers, top wins:

| Priority | Source | Scope | Example |
|----------|--------|-------|---------|
| **1** | System safety | Absolute | Never auto-run destructive commands |
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
| **4** | `AGENTS.md` | Per-repo | System map — what this repo IS |
| **5** | `TASKS.md` | Per-repo | What needs to be done |
| **6** | `.guarani/orchestration/PIPELINE.md` | Shared | 7-phase cognitive protocol |
| **7** | `.guarani/PREFERENCES.md` | Per-repo | Coding standards |
| **8** | `.guarani/IDENTITY.md` | Per-repo | Who the agent IS in this context |
| **9** | Workflow triggers (`/start`, `/end`) | On-demand | Loaded when user invokes slash command |
| **10** | Meta-prompt triggers (`triggers.json`) | Keyword-activated | "mycelium" → load mycelium-orchestrator.md |

### 2. Message Processing (Every Single Message)

```text
USER MESSAGE arrives
       |
       v
[CLASSIFY COMPLEXITY]
  TRIVIAL (typo, import)     → Skip to EXECUTE
  SIMPLE (add field, fix bug) → INTAKE → PLAN → EXECUTE → VERIFY
  MODERATE (component, API)   → Full 7-phase pipeline + 3 Sequential Thoughts
  COMPLEX (feature, payment)  → Full pipeline + 5 Sequential Thoughts
  CRITICAL (migration, auth)  → Full pipeline + 7 thoughts + user approval
       |
       v
[CHECK CONSTRAINTS]
  - Is this in a FROZEN ZONE? → STOP, ask user
  - Does this violate SSOT ownership? → STOP, redirect
  - Does this create a new doc? → Anti-proliferation check
  - Does this touch governance? → Will need governance:sync after
       |
       v
[EXECUTE with tool priority]
  1. code_search (explore codebase first)
  2. read_file (verify specifics)
  3. grep_search / find_by_name (targeted)
  4. MCP tools if available (MCP-FIRST principle)
  5. run_command (terminal — safe=auto, destructive=approve)
  6. edit / multi_edit (code changes — minimal, focused)
       |
       v
[VERIFY]
  - tsc --noEmit (TypeScript repos)
  - ruff check (Python repos)
  - git status (check what changed)
  - Visual validation (if UI changed)
       |
       v
[LEARN]
  - create_memory (cross-session persistence)
  - Update HARVEST.md (reusable patterns)
  - Update TASKS.md (mark done, add new)
  - Conventional commit (feat:/fix:/chore:/docs:)
```

### 3. Tool Inventory (What I Have Access To)

**Pre-commit hooks check SSOT alignment. `/end` workflow BLOCKS if docs are stale.**
### 5. SSOT Ownership Contract

| Surface | Owner | Location |
|---------|-------|----------|
| `SSOT_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CAPABILITY_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CHATBOT_SSOT.md` | kernel | `/home/enio/egos/docs/modules/` |
| `AGENTS.md` | each repo | repo root |
| `TASKS.md` | each repo | repo root |
| `.windsurfrrules` | each repo | repo root |
| `SYSTEM_MAP.md` | each repo | `docs/` |
| `HARVEST.md` | each repo | `docs/knowledge/` |

**Their `.windsurfrules` are loaded as user_rules. I can switch context between repos in a single session. But I NEVER mix their**
---

## P5 Session Patterns (2026-04-01)

### DashScope / Alibaba LLM Fallback Chain Pattern

**OpenRouter Gemini Flash is free but rate-limited. Need sovereign Brazilian alternative with graceful fallback.**


**Tier-based fallback chain in `packages/shared/src/llm-provider.ts`:**
```
fast:    qwen-flash (DashScope free) → gemini-2.0-flash (OpenRouter) → gpt-4o-mini
default: qwen-plus  (DashScope $0.0008/1K) → qwen-max → claude-sonnet-4.6
deep:    qwen-max   (DashScope $0.0016/1K) → qwq-plus (reasoning) → claude-sonnet-4.6
```
- DashScope endpoint: `dashscope-intl.aliyuncs.com` (Singapore — not mainland China endpoint)
- `isRateLimitError()` detects 429/503 and triggers next tier automatically
- `qwq-plus` = reasoning model, for complex multi-step analysis (not conversational chat)
- 90-day free quota: 1M tokens per model family (one-time, no daily reset after expiry)

**DashScope key format `sk-xxxx` same as OpenAI style. Endpoint: `/compatible-mode/v1/chat/completions`. Not the same as Qwen via OpenRouter.**
---

### GitHub Secrets API Encryption Pattern (PyNaCl SealedBox)

**Setting 10+ GitHub Secrets manually via UI is slow and error-prone.**


**Python + PyNaCl SealedBox encryption with repo public key:**
```python
from nacl.public import SealedBox, PublicKey   # NOT nacl.sealed
import base64, requests

res = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key", headers=headers)
key_id = res.json()["key_id"]
box = SealedBox(PublicKey(base64.b64decode(res.json()["key"])))
encrypted_b64 = base64.b64encode(box.encrypt(secret_value.encode())).decode()
requests.put(f"...secrets/{name}", json={"encrypted_value": encrypted_b64, "key_id": key_id}, headers=headers)
```

**`GITHUB_TOKEN` cannot be set as secret (422 error — auto-injected by runner). Install: `pip install PyNaCl --break-system-packages` on Ubuntu 24+.**
---

### Licitação Taxonomy Pattern (Brazilian Procurement Classification)

**Eagle Eye AI returned unstructured opportunity text — hard to filter or aggregate by type.**


**Full taxonomy in `src/types.ts` from PNCP/CATMAT/CATSER standards:**
- **9 segments:** TI_TECNOLOGIA, SAUDE, OBRAS_INFRAESTRUTURA, SERVICOS_GERAIS, ALIMENTACAO, EDUCACAO_CULTURA, VEICULOS_TRANSPORTE, CONSULTORIA_PROFISSIONAL, MATERIAIS_CONSUMO
- **12 modalities:** PREGAO_ELETRONICO … RDC, DESCONHECIDA
- **4 tiers by value:** MICRO (<50K), PEQUENO (50K–500K), MEDIO (500K–5M), GRANDE (>5M)
- **Flags:** `srp` (other orgs can adhere via ARP), `exclusivo_me_epp`, `esfera` (FEDERAL/ESTADUAL/MUNICIPAL/CONSORCIO)

Baked into AI system prompt as classification rules → Gemini Flash classifies on extraction.

---

### AI Coverage Map Auto-Update Pattern

**No single view of which repos/files use LLMs. Cost estimates scattered. New AI calls added silently.**


**`docs/AI_COVERAGE_MAP.md` (canonical) + `scripts/ai-coverage-scan.ts` (scanner):**
- Ripgrep scans 8 repos for 12 AI call patterns; extracts model names
- `--check`: exits 1 if new AI files found not in map → use as pre-commit hook
- `--update`: regenerates summary table in-place with live counts

**Coverage map = breadth (which files touch AI). TELEMETRY_SSOT = depth (runtime costs, latency, tokens per call). Both needed.**
---

### Territory Auto-Discovery Pattern (PNCP + IBGE)

**Manually picking Brazilian municipalities for Eagle Eye is guesswork.**


**`scripts/discover-territories.ts` crosses two public APIs:**
1. IBGE: `servicodados.ibge.gov.br/api/v1/localidades/municipios` → all 5570 municipalities
2. PNCP: `/consulta/v1/contratacoes/publicacao` → rank by real procurement volume
3. `--add-top=N` auto-injects top N into territories.ts

**IBGE 7-digit → PNCP 6-digit: `String(id).slice(0, 6)`. PNCP requires `codigoModalidadeContratacao=8`. Max page size: 50. Base path: `pncp.gov.br/api/consulta/v1`.**
---

### Gem Hunter Migration Pattern (egos-lab → egos)

**egos-lab being archived. Any agent there needs migration.**


**1. Copy agent `.ts`, fix import paths (`../../packages/shared/src/` in egos)**
2. Create `.github/workflows/<agent>-adaptive.yml` in egos with all secrets
3. Add to `agents.json` registry in egos + run `bun agent:lint`
4. Mark egos-lab copy as `[MIGRATED]` — don't delete until repo fully archived

**gem-hunter specific:** Added `early-warning` track for monitoring day-0 AI releases (e.g., HKUDS/OpenHarness by @huang_chao4969). Track type union extended: `"early-warning"` added to `SearchTrack`.

---

### X.com OAuth 1.0a Write — Bun/Web Crypto Implementation (P7)

**X.com Bearer Token is READ-ONLY. Writing tweets/replies requires OAuth 1.0a with HMAC-SHA1, no npm packages.**


**```typescript**
const cryptoKey = await crypto.subtle.importKey("raw", encoder.encode(signingKey),
  { name: "HMAC", hash: "SHA-1" }, false, ["sign"]);
const signature = await crypto.subtle.sign("HMAC", cryptoKey, encoder.encode(signatureBase));
const signatureB64 = btoa(String.fromCharCode(...new Uint8Array(signature)));
```
- Signature base: `METHOD&url_encoded_endpoint&url_encoded_oauth_params_sorted`
- Signing key: `url_encoded_consumer_secret&url_encoded_access_token_secret`
- Auth header: `OAuth oauth_consumer_key="...", oauth_nonce="...", oauth_signature="...", ...`

**50 writes/day hard limit, 10 searches/15min.**


**`MAX_DAILY_REPLIES = 40` (10 buffer), `MAX_PER_RUN = 3` (hourly cron).**


**`/tmp/x-reply-bot-state.json` with daily date reset.**
---

### Rapid Response System Pattern — Matching Topics to Capabilities (P7)

**When a trending topic matches our work, we lose hours manually writing threads. Repos are messy. Linking the wrong files is embarrassing.**


**`scripts/rapid-response.ts` with `EGOSCapability` profiles:**
```typescript
interface EGOSCapability {
  id: string;
  keywords: string[];          // scored — multi-word keywords score higher
  pitch: string;               // ≤240 chars for X
  thread: string[];            // full thread, each ≤280 chars
  repos: { name, url, desc }[];
  clean_files: string[];       // ONLY share these — not the whole dirty repo
}
```
- `scoreMatch()`: each keyword match += word count (multi-word = more specific = higher score)
- `generateShowcaseREADME()`: writes `/tmp/egos-rapid-response-{ts}.md` — clean, linkable

**`clean_files` per capability = curated showcase without exposing repo drift.**
---

### Task Reconciliation Auto-Detection Pattern (P8)

**TASKS.md drifts. Tasks completed in commits get mentioned in commit bodies as "new tasks" and a naive pattern match falsely marks them as done.**


**1. **Subject-line match** → reliable: commit subject `feat: GH-034 OpenHarness` = GH-034 done**
2. **Body completion markers** → ID paired with `✅`, `[x] ID`, or `marked done` = confirmed

**Commit body saying `"New tasks: GH-032, GH-035"` matches a naive `/\bGH-\d+\b/` pattern but these tasks are NOT done.**


**```typescript**
// Subject-line IDs are reliable done signals
const subjectPattern = /\b([A-Z]+-\d+)\b/g;
// Body: only count with completion markers
const completionPattern = /\b([A-Z]+-\d+)[^✅\n]*✅/g;
const checkedPattern = /\[x\]\s+([A-Z]+-\d+)/g;
```

**`--summary` in `/start` Phase 7.5 and `/end` Phase 3. Shows drift count + health %.**
---

### Legacy Code Detector — Non-Blocking Pre-Commit Check (P7)

**Detect smell without blocking — exit 0 always (use `--strict` to block).**
```bash
# check-legacy-code.sh pattern:
TODO_COUNT=$(git diff --cached -- "*.ts" "*.tsx" | grep '^+' | grep -c 'TODO\|FIXME' || true)
[ "$TODO_COUNT" -gt 3 ] && echo "⚠️  Adding $TODO_COUNT TODOs"
```

**>3 TODO/FIXME additions, >2 console.log/debug, >5 commented-out lines, hardcoded localhost URLs, possible unused TS imports.**


**These are code quality smells, not security violations. Blocking → devs add `--no-verify`. Non-blocking → devs see the feedback and often self-correct.**
---

## Real Data Pipeline + Government Bid Strategy (2026-04-01)

### Problem
Mock data limits credibility. Government sales require proof-of-concept with real data from official sources. Software licitações landscape unknown.

### Solution — Eagle Eye Real Data Pipeline

**`/home/enio/egos-lab/apps/eagle-eye/scripts/analyze-real-gazettes-v2.ts`**
1. **Fetch real gazettes** from Querido Diário API (9,697 available)
   - Filter by territory + keywords (licitação, pregão, software, desenvolvimento)
   - Extract gazette text + metadata
   
2. **Analyze with Gemini Flash** (~$0.01/gazette)
   - Prompt includes 26 detection patterns (PII, fiscal, LGPD, etc.)
   - Returns segmento (TI, Consultoria, etc.), modalidade, porte, value, confidence
   
3. **Validate enums** — Critical bug found: market_potential enum accepts Portuguese only
   - Mapping: urgent→muito_alto, high→alto, medium→medio, low→baixo
   - Fire-and-forget insert to Supabase (non-fatal if down)

4. **Results (March 2026):**
   - 36 opportunities found, R$ 10.5M value
   - 14 software/TI (38.9%), avg confidence 85%
   - Geographic: São Paulo 6, Rio 4, BH 2, others 2

### Government Bid Waterfall (Tier 1/2/3)

**Pursue immediately**
- Sistema de Gestão de Licitações: R$ 250k, 28 days to deadline
- Plataforma de Análise Dados Gov: R$ 180k, 36 days
- Auditoria e Compliance: R$ 120k, 51 days
- Total opportunity: R$ 550k

**Add if bandwidth allows**
- Dashboard Transparência: R$ 95k
- API de Integração: R$ 140k

**Pass**
- Commoditized dev work (too much competition, margin too low)

### Integrador Partnership Model (Recommended Path)

**- Risk transfer: if EGOS misses, integrador absorbs (EGOS is subcontractor)**
- Trust multiplier: public sector trusts established integrador
- Revenue bundling: integrador upsells consulting + training, pays EGOS per milestone
- Scale: integrador has sales team to find 5-10 projects/year

**70% integrador, 30% EGOS (industry standard for subcontractors)**


**> "EGOS provides Eagle Eye (gazette monitor) + Guard Brasil (compliance validation) + software delivery. You handle client, compliance signoff, training. Revenue share 70/30."**
### Seasonal Pattern Discovery

**March = IT-heavy (12 TI ops vs 2 Saúde, 0 Educação)**
- **Root cause:** Brazilian fiscal year ramp-up + digital agenda priority
- **Implication:** Full-year analysis (12 months) needed for accurate category balance
- **Action:** Backfill 6 months historical data, scale to 47 territories

### Deploy Daily Cron for 5 Tier-1 Territories

**`/home/enio/egos-lab/apps/eagle-eye/scripts/daily-analysis-cron.ts`**


**0 9 * * * (9:00 AM BRT)**


**SP, RJ, BH, Curitiba, Porto Alegre (highest volume)**


**Top 10 gazettes/day, ~15min execution, inserts to Supabase**


**PNCP returns 403 after ~50 calls. Solution: SQLite cache + exponential backoff.**
### Codex QA Summary (GH-040/041/042)

All 3 PRs production-quality, no blockers:
- **GH-040 (SSOT validator):** ⭐⭐⭐⭐⭐ Validates drift between agents.json, TASKS.md, HARVEST.md
- **GH-041 (API smoke tests):** ⭐⭐⭐⭐ Tests 5 Guard Brasil contracts (inspect, PII, Atrian, rate limit)
- **GH-042 (Version lock):** ⭐⭐⭐⭐⭐ Ensures package.json sync. Note: current versions correct by design (1.0.0 root, 0.1.0 web, 0.2.0 package, N/A api)

### Reusable Patterns

1. **Enum Validation in AI Output** — Always validate enum fields from LLM before Supabase insert
2. **Gazettes as Unstructured Data** — Text extraction + parsing + AI analysis beats manual PNCP API calls
3. **Fire-and-Forget Async** — Non-fatal Supabase failures = better UX than blocking on network
4. **Daily Cron for Market Scanning** — 9 AM BRT ensures fresh data for morning decision-making
5. **Proposal as Code** — Template proposal (PROPOSAL_250K_LICITACOES_SYSTEM.md) with real metrics = 10x faster response to RFPs


---

## Technical Learnings & API Patterns (2026-04-03)

### Stripe Metered Billing — New API Schema (v2025-03-31.basil)

**Stripe deprecated `usage_type=metered` in favor of Billing Meters.**


**```typescript**
const price = await stripe.prices.create({
  product: 'prod_...',
  type: 'recurring',
  recurring: { interval: 'month' },
  usage_type: 'metered',  // ❌ No longer valid
  tiers_mode: 'volume'
});
```

**```typescript**
// Step 1: Create a Billing Meter
const meter = await stripe.billing.meters.create({
  display_name: 'Guard Brasil API Calls',
  event_name: 'guard_brasil_api_call',  // Custom event from your backend
});

// Step 2: Create price with meter reference
const price = await stripe.prices.create({
  product: 'prod_...',
  type: 'recurring',
  recurring: { interval: 'month', meter: meter.id },
  currency: 'brl',
  billing_scheme: 'tiered',
  tiers: [
    { up_to: 1000, unit_amount: 100 },    // R$ 1.00 per call
    { up_to_inf: true, unit_amount: 50 }  // R$ 0.50 per call (volume discount)
  ]
});

// Step 3: At checkout, omit quantity (meter-driven)
const session = await stripe.checkout.sessions.create({
  customer: 'cus_...',
  line_items: [{
    price: price.id,
    // NO quantity field for metered prices
  }],
  mode: 'subscription'
});
```

**```typescript**
// After successful Guard Brasil API call
await stripe.billing.meterEventAdjustments.create({
  timestamp: Math.floor(Date.now() / 1000),
  identifier: customer_id,  // maps to checkout session customer
  event_name: 'guard_brasil_api_call',
  quantity: 1
});
```

**Event name must match meter creation. Timestamp in Unix seconds (not ms). Failures silently ignored by Stripe billing — no impact on API response.**
---

### Docker Compose env_file vs environment Precedence Bug

**When using both `env_file:` and `environment:` in docker-compose.yml:**
```yaml
services:
  api:
    env_file: .env.secrets  # Contains SECRET_KEY=abc123
    environment:
      STRIPE_KEY: ${STRIPE_KEY}  # Shell var not set during compose up
```

**Docker treats `environment:` section as an **override layer**. If shell var `${STRIPE_KEY}` is not set, Docker inserts **empty string** into the container, shadowing any value from `env_file:`.**


**```yaml**
services:
  api:
    env_file: .env.secrets  # Secrets here: SECRET_KEY, STRIPE_KEY
    environment:
      # Only non-secret constants
      API_TIMEOUT: '30000'
      LOG_LEVEL: 'info'
```

**Use `env_file:` for all secret + sensitive config. Use `environment:` only for constants that don't need `.env` protection.**
---

### Caddy Container Caddyfile Hot-Reload

**Caddy running in Docker with a volume-mounted Caddyfile may cache stale config after file update.**


**```bash**
# Reload Caddy config without restart
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

**1. Write updated config to temporary location inside container:**
```bash
   docker cp new-Caddyfile caddy:/tmp/Caddyfile
   ```
2. Reload from temp:
   ```bash
   docker exec caddy caddy reload --config /tmp/Caddyfile
   ```
3. On next container restart, volume mount is fresh

**Caddy admin socket listens on `localhost:2019` inside container. The `reload` command uses that socket. No downtime — connections remain open during reload.**
---

### Caddy Route Ordering — Specificity Rule

**Routes don't match expected paths due to ordering.**


**```caddy**
# ✅ CORRECT
handle /api/* {
  reverse_proxy backend:3000
}

handle /guard/* {
  reverse_proxy guard:5000
}

handle {
  # Catch-all: routes not matched above
  reverse_proxy vercel.app
}

# ❌ WRONG — /api/* never matched
handle {
  reverse_proxy vercel.app  # Catch-all consumes everything
}
handle /api/* {
  reverse_proxy backend:3000
}
```

**Caddy evaluates `handle` blocks top-to-bottom. First matching block wins. A catch-all `handle { }` with no path matcher matches everything.**
---

### Brazilian RG Regex — Unicode & nº Prefix

**Original regex `^([0-9.]+)-[0-9]{2}$` with word boundary `\b` failed on RG with prefix "Registro Geral nº 12.345.678-9".**


**`nº°` characters weren't matched by `[:\s]*`. The `\b` word boundary expected alphanumeric before the first digit.**


**```typescript**
// Old (broken)
const rgRegex = /\bRegistro\s+Geral.*?([0-9.]+)-([0-9]{2})\b/g;

// New (works)
const rgRegex = /Registro\s+Geral[\s:nº°.]*([0-9.]+)-([0-9]{2})/iu;
```

**1. Removed `\b` word boundaries (they block Unicode chars like nº)**
2. Added `nº°` to the prefix pattern: `[\s:nº°.]*`
3. Added `/u` Unicode flag + `/i` case-insensitive

**- "Registro Geral nº 12.345.678-9"**
- "RG: 12.345.678-9"
- "RG nº. 12.345.678-9"
- "Registro Geral: 12345678-9" (no dots)

**```typescript**
const testRGs = [
  'Registro Geral nº 12.345.678-9',
  'RG nº 12.345.678-9',
  'Documento RG Nº 12.345.678-9',  // Capital Nº
  'rg: 12.345.678-9'  // lowercase
];
testRGs.forEach(rg => {
  const match = rg.match(rgRegex);
  console.assert(match, `Failed: ${rg}`);
});
```

---

### Eagle Eye Document Parser — Regex Confidence at 78% Without LLM

**Structured extraction from editals (government bid documents) achieved 78% confidence using regex + heuristics, without needing LLM for every field.**


**Portuguese accented characters in regex. Example patterns:**
- PREGÃO (not pregão)
- Modalidade: ELETRÔNICO vs eletrônico
- "não" (lowercase) vs "Não" (capitalized)

**Case-insensitive regex `/[ãa]/i` does NOT match uppercase `Ã` without Unicode flag.**


**```typescript**
// ❌ Misses uppercase Ã
const pattern1 = /[ãa]+/i;

// ✅ Matches all variants
const pattern2 = /[ãa]+/iu;

const testStrings = ['são', 'SÃO', 'São'];
testStrings.forEach(s => {
  console.assert(s.match(pattern2), `Failed: ${s}`);
});
```

**68 regex patterns mapped for editais:**
- Modalidade extraction: 15 patterns (pregão, concorrência, convite, etc.)
- Value patterns: 12 (handles R$, mil, M, range syntax)
- PII / document detection: 18 (CPF, CNPJ, RG, address)
- Temporal markers: 8 ("até", "30 dias", "31/12/2026")
- Organizational entities: 15 (CAIXA, CEF, BNDES, etc.)

**- 1 pattern match: 45% confidence**
- 2-3 pattern matches: 65%
- 4+ pattern matches: 85%+

**Only for ambiguous cases (45-60% confidence) or for narrative field extraction (objectives, scope). Structure (modalidade, valor) = regex only.**


**1,200 documents processed in 3.2 seconds (regex), vs ~8 minutes with Gemini API. 78% vs 92% accuracy — acceptable tradeoff for 150x speedup.**
---

## Session P23 — EGOS HQ Dashboard + Claude Code Skills (2026-04-05)

### EGOS HQ (hq.egos.ia.br) — Mission Control Dashboard

**Private Next.js 15 dashboard behind JWT auth (jose, httpOnly cookie `hq_session`, 7-day expiry).**
- Single-user auth with `DASHBOARD_MASTER_SECRET` env — no external auth service needed
- Docker: `oven/bun:1.3-slim` builder + `node:20-slim` runner (Next.js standalone output requires `node`, not `bun`)
- **Critical:** `RUN mkdir -p public` in builder stage to prevent COPY failure when `/public` is empty
- Caddy runs inside Docker container `infra-caddy-1` — reload via `docker exec infra-caddy-1 caddy reload --config /etc/caddy/Caddyfile`
- VPS deploy path: `/opt/apps/<name>/` with `Dockerfile` + `docker-compose.yml` + `.env`

**- Bot saves results to Supabase `x_reply_runs` with `status=pending` (never auto-posts)**
- Dashboard `/x` tab shows queue → approve (posts reply) or reject
- `AUTO_APPROVE=true` env restores old auto-post behavior for emergencies
- `status` enum: `pending | approved | rejected | sent | dry_run`

**`egos.ia.br` zone managed at Registro.br. All VPS services: `A → 204.168.217.125`**
### Claude Code Skills/Hooks — Installation Patterns (2026-04-05)

**markdown files in `~/.claude/commands/` — auto-loaded as `/command-name`**


**`hesreallyhim/awesome-claude-code` repo under `resources/slash-commands/<name>/<name>.md`**


**```bash**
gh api "repos/hesreallyhim/awesome-claude-code/contents/resources/slash-commands/<cmd>/<cmd>.md" \
  --jq '.content' | base64 -d > ~/.claude/commands/<cmd>.md
```

**All hooks must be registered in `~/.claude/settings.json` under `hooks.<Event>[].hooks[]`**


**PreToolUse Bash hooks see the full command string including quoted arguments.**
If checking for `rm -rf /home` in a command like `echo 'rm -rf /home'`, the pattern will match the quoted string.
Fix: use Python regex requiring `rm` to appear as an actual command token (`^|; |&& `), not as substring anywhere.

**rm-guard pattern (correct):**
```python
pattern = r'(?:^|;\s*|&&\s*|\|\|\s*)rm\s+-[rRf]+\s+(/etc|/var|/usr|/opt/bracc|/opt/apps)'
```

**`anthropics/claude-code-action@v1` — works on `pull_request: [opened, synchronize]`**
---

## Session P24 — Gateway Auth + Telegram Commands + FTS + Gem Hunter Dashboard (2026-04-06)

### Gateway API Key Auth Pattern (SHA-256 + Supabase)

**Never store raw tokens — only SHA-256 hashes in `gem_hunter_api_keys` table.**
```typescript
const hash = createHash("sha256").update(rawToken).digest("hex");
const row = await supabase.from("gem_hunter_api_keys").select("*").eq("key_hash", hash).single();
```
- `lookupApiKey()` → Supabase fetch by hash, returns tier + limits
- `checkAndIncrementUsage()` → GET count today, POST/PATCH usage row, fail-open on DB error
- Hono middleware: `authMiddleware: MiddlewareHandler<{Variables:{tierCtx:TierContext}}>` — downstream routes call `c.get("tierCtx")`
- Admin key creation: `POST /admin/keys` protected by `GATEWAY_ADMIN_SECRET` env

**Fail-open on auth DB error (allow request, log warning) — never block legitimate traffic due to Supabase outage.**
### Docker Gateway Deploy: no volume mounts → must rsync + rebuild

**`egos-gateway` Docker container has **no volume mounts** (Binds: []). Source is baked into image at build time.**


**```bash**
rsync -avz -e "ssh -i ~/.ssh/hetzner_ed25519" src/channels/file.ts root@VPS:/opt/apps/egos-gateway/src/channels/
cd /opt/apps/egos-gateway && docker compose build --no-cache && docker compose up -d
```

**`/opt/apps/egos-gateway/` (NOT `/opt/bracc/` which is the old br-acc repo)**


**`127.0.0.1:3050:3050` (gateway), `127.0.0.1:3095:3095` (gem-hunter-server)**
### Telegram Slash Commands → Proxy Pattern

**Telegram commands that trigger other services use an immediate reply + background proxy:**
```typescript
} else if (text === "/hunt") {
  await sendMessage(chatId, "🔍 Iniciando hunt...");
  const res = await fetch("http://localhost:3095/v1/hunt", { 
    method: "POST", body: JSON.stringify({ quick: true }),
    signal: AbortSignal.timeout(8000)
  });
  // reply based on res.ok
}
```
- `/sector <name>` validates against known sectors before fetch — prevents unnecessary API calls
- `/trending` reuses existing NLP path (inject text into orchestrator flow) — zero extra code

### Knowledge FTS with pg_trgm + phfts(portuguese)

**```sql**
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_wiki_pages_title_trgm ON egos_wiki_pages USING GIN (title gin_trgm_ops);
CREATE INDEX idx_wiki_pages_content_trgm ON egos_wiki_pages USING GIN (content gin_trgm_ops);
CREATE INDEX idx_wiki_pages_tsvec ON egos_wiki_pages USING GIN (to_tsvector('portuguese', title || ' ' || content));
```

**`phfts(portuguese)` operator on multiple columns via `or=()`:**
```
?or=(title.phfts(portuguese).${q},content.phfts(portuguese).${q})&order=quality_score.desc
```
- `?mode=ilike` = default trigram ILIKE (fuzzy, partial match)
- `?mode=fts` = plainto_tsquery Portuguese (semantic word match, ignores inflections)

### Gem Hunter Dashboard — Inline SSR Data Injection

**Bun HTTP server serves a complete dark SPA as a string literal. Data is injected at render time:**
```typescript
function dashboardHTML(): string {
  const gems = readGemsFromFile(); // reads latest-run.json
  return `<html>...<script>const INLINE_GEMS = ${JSON.stringify(gems)};</script>...`;
}
app.get("/", (req, res) => res.end(dashboardHTML()));
```
- Zero API round-trips on first load — data arrives with HTML
- Hunt trigger: `POST /v1/hunt` → polls `/v1/jobs/:id` every 8s → `location.reload()` on done
- **Avoids Next.js overhead** for an internal tool — Tailwind CDN + vanilla JS sufficient

### Health Monitor Gotcha: Internal vs External URLs

**Health monitor pinged `https://gateway.egos.ia.br` (external DNS) from inside Docker — fails because DNS resolves to public IP, rejected inside container network.**


**Always use `GW_INTERNAL = http://localhost:${GW_PORT}` for self-checks.**


**`Math.round((sum_ok_weights / sum_all_weights) * 100)` — alert when < 40%.**
### Gem Hunter Data Format Mismatch (Python parser pattern)

**`gem-hunter.ts` generates `{generatedAt, byCategory, bySource}` but dashboard expects `{date, gems:[{name,url,score,...}]}`.**


**Python parser reads markdown report (`gems-YYYY-MM-DD.md`) line by line, extracts table rows, outputs normalized JSON:**
```python
gems = [{"name": row[0], "url": row[1], "score": int(row[2]), ...} for row in parse_table(md)]
json.dump({"date": date, "gems": gems, "totalFound": len(gems)}, f)
```

**When TypeScript agent output format diverges from consumer expectations, a thin Python adapter is faster than refactoring both sides.**
### OpenClaw Model Chain — Haiku Default + Free Fallbacks (P28)

**Never lock to one provider. OpenClaw `models.json` supports multiple providers in one file:**
1. `anthropic-subscription` → billing proxy → Claude (zero cost via Claude Code subscription)
2. `openrouter` → Qwen3-235B:free (zero cost, 32K context, reasoning)
3. `dashscope` → qwen-turbo (Alibaba, very cheap, 1M context)

**Provider order in models.json matters for fallback resolution. Put cheapest/fastest first.**


**```json**
{
  "providers": {
    "anthropic-subscription": {"api": "anthropic-messages", "apiKey": "dummy", "baseUrl": "http://127.0.0.1:18801"},
    "openrouter": {"api": "openai-completions", "apiKey": "sk-or-...", "baseUrl": "https://openrouter.ai/api/v1"},
    "dashscope": {"api": "openai-completions", "apiKey": "sk-...", "baseUrl": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"}
  }
}
```

**`"model": "anthropic-subscription/claude-haiku-4-5-20251001"` — Sonnet only for complex tasks.**
### Docker Container-to-Host Connectivity (UFW Gotcha)

**HQ container (172.19.0.17) could NOT reach billing proxy on host (0.0.0.0:18801) despite proxy binding to all interfaces.**


**UFW default INPUT policy = DROP. Docker bridge traffic hits INPUT chain before host receives it.**


**`ufw allow from 172.19.0.0/16 to any port 18801 proto tcp` — allows infra_bracc subnet to reach host ports.**


**Always check UFW when Docker container can't reach host-bound service. `ss -tlnp | grep <port>` confirms binding; `iptables -L INPUT -n` shows chain policy.**
### 24/7 Watchdog Pattern — VPS Service Monitor

**Single bash script run every 5 min via cron. State stored as files (`/var/lib/egos-watchdog/<service>.state`). Alert only on state CHANGE (up→down or down→up), not every check cycle.**
```bash
check_and_alert() {
  local name="$1" status="$2"
  local state_file="/var/lib/egos-watchdog/${name//\//-}.state"
  local prev_status="up"
  [ -f "$state_file" ] && prev_status=$(cat "$state_file")
  if [ "$status" = "down" ] && [ "$prev_status" = "up" ]; then
    send_telegram "🔴 DOWN: $name"
  elif [ "$status" = "up" ] && [ "$prev_status" = "down" ]; then
    send_telegram "✅ RECOVERED: $name"
  fi
  echo "$status" > "$state_file"
}
```

**Docker containers (`docker inspect ... | grep true`), HTTP endpoints (curl -sf --max-time 8), credential freshness (read JSON → compare timestamps).**


**Use `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'` to escape message for JSON body.**
### HQ Health Route — Internal Container URLs

**Next.js HQ app running as Docker container should use internal container names for service health checks, not external domain names (avoids Caddy round-trip + DNS resolution failure).**
```typescript
const GATEWAY_HEALTH_URL = process.env.GATEWAY_HEALTH_URL ?? 'https://gateway.egos.ia.br/health';
const OPENCLAW_HEALTH_URL = process.env.OPENCLAW_HEALTH_URL ?? 'https://openclaw.egos.ia.br';
const BILLING_PROXY_URL = process.env.BILLING_PROXY_URL ?? 'http://127.0.0.1:18801';
```

**```**
GATEWAY_HEALTH_URL=http://egos-gateway:3050/health   # container name in infra_bracc
OPENCLAW_HEALTH_URL=http://openclaw-sandbox:18789    # container name
BILLING_PROXY_URL=http://172.19.0.1:18801           # host bridge IP
```

**UFW rule to allow Docker bridge → host port 18801.**
### Next.js Middleware Auth — Making Health Endpoint Public

**Add public health endpoint to middleware PUBLIC_PATHS before auth check:**
```typescript
const PUBLIC_PATHS = ['/login', '/api/auth/login', '/api/auth/logout', '/api/hq/health'];
```

**After changing middleware, force-remove running container and recreate — `docker restart` may reuse old image layers. Use `docker stop && docker rm && docker run` for guaranteed fresh start.**
### OpenClaw Credentials JSON Structure

**`~/.claude/.credentials.json` nests OAuth data under `claudeAiOauth`:**
```json
{"claudeAiOauth": {"accessToken": "...", "expiresAt": 1775497970773, ...}}
```

**`d.get('expiresAt')` → None**


**`d.get('claudeAiOauth', {}).get('expiresAt', 0) / 1000` → Unix timestamp**
---

## P28-P29 Patterns (2026-04-06 — Codex + HQ + Governance)

**- OpenAI Codex CLI (v0.105+) usa ChatGPT OAuth internamente — token ChatGPT NÃO tem scope `model.request` para API direta**
- Solução: wrappear `codex exec --output-last-message <file>` como HTTP server local
- Porta 18802, API OpenAI-compatible, OpenClaw usa como provider `codex/gpt-5.4`
- Quota: ~10 requisições por janela de 5h (ChatGPT Plus) — rastrear em usage.json
- `codex exec` tem overhead ~9K tokens (MCP startup) — adequado para review, não para chat contínuo
- `codex exec review` — subcomando específico para code review, mais eficiente

**- Proxy em `127.0.0.1:PORT` → inacessível de containers Docker (mesmo com UFW rule)**
- Correto: `0.0.0.0:PORT` + UFW `allow from 172.19.0.0/16 to any port PORT` + firewall externo bloqueando
- Pattern: Claude billing proxy (18801) e Codex proxy (18802) ambos em 0.0.0.0, UFW filtra

**- Regra dumb: bloquear commit quando > N linhas**
- Regra smart: auto-arquivar tasks [x] → TASKS_ARCHIVE.md quando > 490 linhas
- Níveis: <490 OK | 490-600 auto-archive+warn | >600 BLOCK (genuinamente tasks demais)
- `scripts/archive-tasks.sh` — move [x] para TASKS_ARCHIVE.md com header de data
- Hook chama o script automaticamente no pre-commit, re-stages os arquivos

**- React puro: `useState(defaultOpen)` por card + `onClick` no header**
- Eventos com `<details>/<summary>` HTML nativo → zero JavaScript para expand/collapse
- `<details>` para eventos com payload JSON → auto-expand/collapse sem state management
- Action buttons com `triggerAction(label, url)` — POST + toast notification 4s

**- Pattern: agent especializado com prompt fixo de regras + contexto de commits recentes**
- Assina cada job: `REVIEWED_BY: codex-constitutional-reviewer | <timestamp> | hash=<sha256>`
- Cron 2x/dia (6h e 18h) — detecção de drift constitucional antes que acumule
- Resultado postado no Supabase `egos_agent_events` para visibilidade no HQ

---

## P32 Documentation Alignment Sweep Pattern (2026-04-06)

**- Se uma decisão já foi tomada, o estado precisa mudar em `MASTER_INDEX`, `SSOT_REGISTRY`, resumos executivos e artefatos temporários relacionados**
- Corrigir só o dashboard executivo deixa o drift reaparecer via docs temporários
- `DOCUMENTATION_ARCHITECTURE_MAP.md` deve explicitar quais docs são fixos, quais são temporários e quando arquivar cada um

**- Quando um documento principal referencia um arquivo ausente, preferir **materializar o artefato fixo** se ele ainda representa conhecimento útil**
- Só remover o link quando o conteúdo realmente morreu ou foi absorvido por outro SSOT
- Neste sweep, `docs/INFRASTRUCTURE_ARCHIVE_AUDIT.md` foi recriado para restaurar a cadeia de navegação

**- `bun run governance:check` não é puramente leitura neste ambiente**
- Além de verificar drift, acionou `[KB-008] Wiki Knowledge Base — compiling...` e fez upsert de 59/59 páginas no Supabase
- Tratar `governance:check` como comando com side effects externos ao planejar validações finais

**- `bun run governance:sync:exec` só deve rodar com alinhamento explícito do operador, porque muta `~/.egos` e leaf repos**
- Quando o objetivo é só fechar drift entre kernel e espelho local, avaliar `governance:sync:local` antes da propagação completa

**- `audit.ecosystem` — aplicou bem à rodada de alinhamento documental**
- `systems.mycelium` — aplicou bem à fase de sync/propagação e verificação de drift

---


## P35 Patterns (2026-04-07 — Doc-Drift Shield L2+L3 + SSOT Gate + ARR)

**SSOT Gate Pattern — LLM confirmado por keyword, keyword bloqueado por LLM**
- Keyword matching sozinho tem falso-positivos (score baixo = ruído)
- LLM sozinho é lento demais para pre-commit e pode estar offline
- Padrão correto: keyword detecta candidate → LLM confirma/descarta → fallback local se API down
- Timeout 8s por LLM call — nunca bloquear commit por falha de API
- Override seguro: `SSOT-NEW: <razão>` no commit message (auditável, não bypass silencioso)

**`.ssot-map.yaml` como contrato machine-readable de SSOT**
- CLAUDE.md §26 define a regra em prosa — ssot-map.yaml define em código
- ssot-router.ts lê o mapa, não tem lógica hardcoded de domínios
- Adicionar domínio = editar um arquivo YAML, não código TypeScript
- Domínios com `forbidden_paths` forçam o router a bloquear antes de chamar LLM (fast path)
- `always_ok` lista: `.ts/.tsx/.sh/.json/.yaml/.py` — nunca rodar SSOT gate em código

**ARR / Quantum Search — Status e Posicionamento**
- Sistema: `@egos/atomizer` + `@egos/search-engine` — in-memory full-text com scoring hierárquico
- Status: DORMANT — implementado, não conectado a nenhum consumer em produção
- "Quantum Search" = vocab-guard blocked — inserido em `.husky/pre-commit` para prevenir AI hallucinations
- Fit correto hoje: Gem Hunter (indexar discoveries), KB wiki (busca em HARVEST.md + pages), não como DB vetorial
- Ativação mínima: `import { AtomizerCore } from '@egos/atomizer'` no gem-hunter pipeline + `InMemorySearch.search()`
- Complementa (não substitui): codebase-memory-mcp (graph), Supabase pg_trgm FTS (já live)

**manifest-generator.ts — Bootstrap de manifests via LLM**
- Extrai claims quantitativos de READMEs existentes sem intervenção manual
- Estratégia: Gemini Flash → Alibaba Qwen → regex patterns (fallback chain idêntico ao ssot-router)
- Só adiciona claims novos — nunca sobrescreve claims manuais já existentes no manifest
- Bug: regex alternation `(\d+)\s*(?:X)|Y` sem capture group correto → undefined. Usar grupos não-capturantes `(?:)` + grupos capturantes `()` explícitos
- Uso: `bun scripts/manifest-generator.ts --repo /path --dry` antes de `--exec`

**doc-drift-analyzer.ts — Pattern analysis de histórico**
- Analisa docs/jobs/ para detectar claims que driftam frequentemente
- Output: health score (0-100) + top 10 drifting claims + trend (improving/stable/worsening)
- Projetado para rodar no CCR (GitHub Actions) — leve, sem acesso cross-repo
- O sentinel local é heavy (cria branches + issues + pushes) — analyzer é read-only

**SSOT domain discovery — investigar docs/ antes de criar arquivos novos**
- 21 domínios mapeados em .ssot-map.yaml v2.0.0
- Padrão: ao criar qualquer `.md` novo, primeiro grep `.ssot-map.yaml` pelo domínio
- Dispersão encontrada: MCP (7 arquivos) → precisa MCP_SSOT.md; outreach (8 arquivos) → GTM_SSOT.md
- `docs/concepts/` = arquivos de visão/arquitetura arquivados (Cortex, ETHIK, Neural Mesh) — não são tasks

---

## KB-020: Defensive Number Coercion in Next.js API Boundaries (2026-04-07)

**Problem:** `toFixed()` crashes at runtime when the value is a string, even if TypeScript types say `number | null`. External HTTP responses from Docker services can return numbers as strings (JSON serialization issues or manual string construction).

**Pattern:** Proxy health endpoints return `{ tokenExpiresInHours: "2.5" }` (string) instead of `2.5` (number). The `!= null` guard passes for strings, so `.toFixed()` crashes.

**Fix — Two-layer defense:**
1. **API boundary (route.ts):** Always coerce with `Number()` when reading from external service responses:
   ```ts
   token_expires_in_hours: raw != null ? Number(raw) : null,
   ```
2. **Render layer (page.tsx):** Defensive `Number()` before any `.toFixed()`:
   ```tsx
   `${Number(svc.billing_proxy.token_expires_in_hours).toFixed(1)}h`
   ```

**Rule:** NEVER call `.toFixed()` directly on a value from an API response without `Number()` wrapping. TypeScript types at runtime are advisory, not guaranteed.
