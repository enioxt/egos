# DOMAIN RULES — egos-lab

> **Version:** 1.1.0 | **Updated:** 2026-02-25
> **Project:** egos-lab (monorepo-lab + agentic-platform)

---

## How to Use

When a task touches a specific domain, load that domain's section
and apply its checklist BEFORE executing. Multiple domains can apply.

---

## 1. AGENTIC PLATFORM

### SSOT

- **Agent registry:** `agents/registry/agents.json` (SSOT for all agents)
- **Agent runner:** `agents/runtime/runner.ts` (frozen zone)
- **Agent CLI:** `agents/cli.ts`
- **Agent implementations:** `agents/agents/*.ts`
- **Shared utils:** `packages/shared/` (ai-client, rate limiter, types)

### Anti-Patterns

- Creating an agent without a registry entry
- Agent depending on external npm packages (zero-deps rule)
- Running `--exec` without first running `--dry`
- Duplicating logic that exists in `packages/shared/`
- Modifying `agents/runtime/runner.ts` without explicit approval

### Checklist

- [ ] Agent has registry entry in `agents.json` (id, name, description, path)
- [ ] Agent supports `--dry` mode (default)
- [ ] Agent produces structured JSON output
- [ ] Agent uses `packages/shared/ai-client.ts` for AI calls
- [ ] Agent is idempotent (safe to re-run)
- [ ] Cost tracked per AI call
- [ ] PII masked in all output (CPF, email)

### Frozen Files

```
agents/runtime/runner.ts
agents/registry/agents.json (structure, not content)
```

---

## 2. EGOS-WEB (Mission Control)

### SSOT

- **Framework:** React + Vite
- **Deploy:** Vercel (auto on push)
- **URL:** egos.ia.br
- **Design:** Tailwind, Lucide icons, dark mode first

### Anti-Patterns

- Creating new pages without updating navigation
- Using inline styles instead of Tailwind
- Adding heavy dependencies to the frontend bundle
- Forgetting to run `tsc -b && vite build` before push

### Checklist

- [ ] Checked existing components before creating new ones
- [ ] Mobile responsive
- [ ] Dark mode compatible
- [ ] `tsc -b` passes
- [ ] `vite build` succeeds locally before push

---

## 3. TELEGRAM BOT

### SSOT

- **Framework:** Telegraf + Bun
- **PM2 name:** `egos-telegram`
- **Channel:** @ethikin
- **Token:** `TELEGRAM_BOT_TOKEN` env var
- **Entry:** `apps/telegram-bot/src/index.ts`

### Anti-Patterns

- Hardcoding bot token in code
- Not handling Telegram API rate limits
- Sending unsanitized user input to LLM (prompt injection)
- Not logging errors to console for PM2 to capture

### Checklist

- [ ] Bot token from env var, never hardcoded
- [ ] Input sanitized before LLM processing
- [ ] Rate limiting on user commands
- [ ] Error handling with user-friendly messages
- [ ] PM2 restart tested after changes

---

## 4. EAGLE-EYE (OSINT)

### SSOT

- **Framework:** Bun scripts
- **Path:** `apps/eagle-eye/`
- **Purpose:** Gazette monitoring + AI analysis

### Checklist

- [ ] API connections tested before analysis
- [ ] AI analysis uses `packages/shared/ai-client.ts`
- [ ] Results structured as JSON
- [ ] PII handling follows masking rules

---

## 5. INFRASTRUCTURE & DEPLOY

### SSOT

- **Web deploy:** Vercel (auto on push)
- **Worker deploy:** Railway (`egos-lab-infrastructure`)
- **Database:** Supabase (`lhscgsqhiooyatkebose`)
- **Queue:** Railway Redis (internal)
- **Bot:** PM2 local

### Anti-Patterns

- More than 3 pushes per session
- Pushing without `tsc -b && vite build`
- Hardcoding env vars
- Missing env vars in Vercel/Railway

### Checklist

- [ ] `tsc -b` passes
- [ ] `vite build` succeeds
- [ ] No hardcoded secrets or API keys
- [ ] Env vars set in all deploy targets
- [ ] Pre-push hooks pass

---

## 6. SECURITY & GOVERNANCE

### SSOT

- **Pre-commit:** `scripts/security_scan.ts` + `scripts/ssot_governance.ts`
- **Pre-push:** `.husky/pre-push` (registry lint + vite build)
- **PII policy:** Mask CPF/email in ALL agent output
- **Prompt injection:** Sanitize external text before LLM
- **RLS:** Every new Supabase table MUST have RLS enabled
- **Extensions:** Install in `extensions` schema, never `public`

### Checklist

- [ ] No secrets in committed code
- [ ] PII masked in logs and agent output
- [ ] External text sanitized before LLM calls
- [ ] RLS enabled on new tables
- [ ] Extensions in `extensions` schema

---

## 7. SHARED PACKAGES

### SSOT

- **Path:** `packages/shared/`
- **AI client:** `packages/shared/ai-client.ts` (all AI calls go through here)
- **Types:** `packages/shared/types/`
- **API registry:** `packages/shared/api-registry/`

### Anti-Patterns

- Duplicating logic that exists in shared packages
- Agent-specific code leaking into shared packages
- Breaking the ai-client interface without updating all consumers

### Checklist

- [ ] New shared code is truly reusable (not agent-specific)
- [ ] TypeScript types exported properly
- [ ] No circular dependencies
- [ ] All consumers updated if interface changes

---

## Domain Detection Heuristic

| Task Keywords | Domains to Load |
|---------------|----------------|
| agent, registry, runner, orchestrator, dry-run | Agentic Platform |
| web, dashboard, mission control, egos.ia.br | egos-web |
| telegram, bot, PM2, @ethikin, telegraf | Telegram Bot |
| eagle-eye, gazette, OSINT, monitor | Eagle-Eye |
| deploy, vercel, railway, redis, infra, env | Infrastructure |
| security, PII, RLS, secret, scan, governance | Security & Governance |
| shared, ai-client, packages, types | Shared Packages |
