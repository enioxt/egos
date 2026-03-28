# MCP Environment Variables Reference — EGOS-004

**Date:** 2026-03-28
**Status:** Required for MCP Operations
**Purpose:** Document all environment variables required by MCP servers (no hardcoded secrets)

---

## Overview

All MCP servers access credentials exclusively through environment variables. This document is the canonical reference for deployment automation (CI/CD, Docker, Kubernetes).

### How to Use This Document

1. **Local Development:** Set variables in `.env` or use `direnv` / `.envrc`
2. **Docker:** Inject via `docker run -e VAR=value` or `.env` file
3. **Kubernetes:** Use Secrets and mount as env vars
4. **Vercel/Railway:** Configure in deployment dashboard
5. **GitHub Actions:** Set in repository secrets

### Security Rules

- Never commit secrets to git (use `.gitignore`)
- Use different values per environment (dev, staging, prod)
- Rotate quarterly or on breach
- Log access to secrets (ConsoleAuditLogger)
- Revoke immediately if exposed

---

## Environment Variables by MCP Server

### Supabase Database MCP (`supabase-db`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `SUPABASE_PROJECT` | string | Yes | Supabase project ID (e.g., `zqcdkbnwkyitfshjkhqg`) |
| `SUPABASE_ANON_KEY` | string | Yes | Supabase anonymous key (public, safe to expose) |
| `SUPABASE_SERVICE_KEY` | string | No | Service role key (admin access, store securely) |

**Example:**
```bash
SUPABASE_PROJECT=zqcdkbnwkyitfshjkhqg
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Source:**
- Project ID: Supabase dashboard → Settings → General
- Anon Key: Settings → API → Project API keys → `anon` / `public`
- Service Key: Settings → API → Project API keys → `service_role` / `secret`

---

### LLM Router MCP (`llm-router`)

| Variable | Type | Required | Provider | Description |
|----------|------|----------|----------|-------------|
| `OPENAI_API_KEY` | string | Yes | OpenAI | API key for GPT models |
| `DASHSCOPE_API_KEY` | string | Yes | Alibaba | API key for Qwen models (default) |
| `OPENROUTER_API_KEY` | string | No | OpenRouter | Meta LLaMA 2 and other models |
| `ANTHROPIC_API_KEY` | string | No | Anthropic | API key for Claude models (fallback) |

**Example:**
```bash
OPENAI_API_KEY=sk-proj-abc123...
DASHSCOPE_API_KEY=sk-abc123...
OPENROUTER_API_KEY=sk-or-abc123...
ANTHROPIC_API_KEY=sk-ant-abc123...
```

**Source:**
- OpenAI: https://platform.openai.com/api-keys
- Alibaba DashScope: https://dashscope.console.aliyun.com/api-key
- OpenRouter: https://openrouter.ai/keys
- Anthropic: https://console.anthropic.com/account/keys

**Cost Tracking:** LLM Router tracks usage via env vars set in CI/CD; see `billing:track` scope.

---

### Git Advanced MCP (`git-advanced`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `GITHUB_TOKEN` | string | No | GitHub personal access token (for private repos) |

**Example:**
```bash
GITHUB_TOKEN=ghp_abc123...
```

**Source:**
- GitHub: Settings → Developer settings → Personal access tokens

**Scopes Required (if using private repos):**
- `repo:read` — Read repository content
- `read:org` — Read organization data

**Note:** Public repos do not require a token.

---

### Calendar & Schedule MCP (`calendar`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `CALENDAR_API_KEY` | string | No | Internal calendar service API key |

**Example:**
```bash
CALENDAR_API_KEY=ck_egos_abc123...
```

**Source:**
- Internal deployment; generate via deployment automation

---

### EXA Research MCP (`exa-research`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `EXA_API_KEY` | string | No | EXA API key for web search and research |

**Example:**
```bash
EXA_API_KEY=exa_abc123...
```

**Source:**
- EXA: https://dashboard.exa.ai/api-keys

---

### Filesystem Watch & Sequential Thinking & Memory MCPs

These MCPs do not require API keys (local-only or public services).

---

## Environment Variables for Vault Integration (Future)

For future HashiCorp Vault support (EGOS-004 roadmap):

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `VAULT_ADDR` | string | No | Vault server address (e.g., `https://vault.egos.ia.br`) |
| `VAULT_TOKEN` | string | No | Vault authentication token |
| `VAULT_SKIP_VERIFY` | boolean | No | Skip TLS verification (dev only, never in prod) |

**Example:**
```bash
VAULT_ADDR=https://vault.egos.ia.br
VAULT_TOKEN=s.abc123...
```

---

## Sample `.env` File (Development)

```bash
# Supabase
SUPABASE_PROJECT=zqcdkbnwkyitfshjkhqg
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# LLM Providers
OPENAI_API_KEY=sk-proj-abc123...
DASHSCOPE_API_KEY=sk-abc123...
OPENROUTER_API_KEY=sk-or-abc123...

# GitHub (optional, for private repos)
GITHUB_TOKEN=ghp_abc123...

# Research
EXA_API_KEY=exa_abc123...

# Calendar (internal)
CALENDAR_API_KEY=ck_egos_abc123...
```

**WARNING:** Never commit `.env` to git. Use `.env.local` (git-ignored) or `.env.example` (template only).

---

## Deployment Checklist

Before deploying to production, verify:

- [ ] All required env vars are set in deployment target
- [ ] Secrets are stored securely (not in plaintext in code)
- [ ] Different credentials per environment (dev/staging/prod)
- [ ] Credentials rotate quarterly
- [ ] Access to secrets is audit-logged
- [ ] MCP config references `${VAR}` syntax, not hardcoded values
- [ ] No secrets in logs or error messages
- [ ] `.env` file is in `.gitignore`

---

## Troubleshooting

### "MCP server failed to initialize: missing env var"

1. Check MCP config: Does it list the required env var?
2. Check environment: Is the var set? (`echo $VAR_NAME`)
3. Check syntax: Should be `${VAR}` in JSON, not `env:VAR`
4. Check scopes: Does the MCP have the required scopes?

**Debug command:**
```bash
# List all EGOS-related env vars
env | grep -E "SUPABASE|OPENAI|DASHSCOPE|GITHUB|CALENDAR|EXA|VAULT"
```

### "Authorization failed: invalid token"

1. Verify the token is correct (copy-paste without whitespace)
2. Check token expiration (GitHub PATs expire after 1 year)
3. Check token scopes (GitHub tokens need `repo:read`, not just `public_repo`)
4. Regenerate the token if unsure

### "Audit log shows scope mismatch"

The MCP tried to access a resource without the required scope.

1. Check `MCP_SCOPE_POLICY.md` for required scopes
2. Update `.guarani/mcp-config.json` to add the scope
3. Check allowed resources in config (allowlist)

---

## Rotation Schedule

**Every 90 Days:**
- Rotate OpenAI, DashScope, OpenRouter, EXA API keys
- Regenerate GitHub PATs (expires after 1 year by default)
- Update Supabase keys if compromised

**On Breach:**
- Immediately revoke the exposed key
- Rotate all related keys
- Check audit logs for unauthorized access
- Update incident response log

---

## References

- **EGOS-004:** MCP Security Hardening (this task)
- **MCP_SCOPE_POLICY.md:** Scope definitions per MCP server
- **mcp-config.json:** Central MCP configuration
- **ConsoleAuditLogger:** Audit trail (packages/audit/src/activation-audit.ts)
- **SecretStore:** Vault abstraction (packages/core/src/secrets/vault.ts)

---

**Last Updated:** 2026-03-28
**Owner:** Enio (EGOS Security)
**Next Review:** 2026-06-28
