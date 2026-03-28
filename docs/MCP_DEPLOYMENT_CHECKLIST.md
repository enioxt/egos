# MCP Deployment Checklist — EGOS-004

**Date:** 2026-03-28
**Status:** MANDATORY for all MCP deployments
**Purpose:** Pre-deployment verification that all MCP servers are securely configured

---

## Pre-Deployment Checklist

Use this checklist **before deploying** MCP servers to any environment (dev, staging, production).

### Phase 1: Secrets Management

- [ ] **No hardcoded API keys in code** — Search entire codebase for hardcoded secrets
  ```bash
  # Run this to detect exposed keys
  git grep -i "api.key\|api.secret\|password" -- ':!*.md' ':!*.lock'
  ```

- [ ] **All credentials from environment variables only** — `.guarani/mcp-config.json` uses `${VAR}` syntax
  ```bash
  # Verify config syntax
  grep -o '\${\w\+}' /home/enio/egos/.guarani/mcp-config.json | sort | uniq
  ```

- [ ] **Environment variables documented** — See `MCP_ENV_VARS_REFERENCE.md` for all required vars

- [ ] **.env file in .gitignore** — Prevents accidental commits
  ```bash
  # Verify .env is ignored
  grep "^\.env" /home/enio/egos/.gitignore
  ```

- [ ] **Environment-specific values** — Different credentials for dev/staging/prod
  - Dev: Use test API keys with rate limits
  - Staging: Use staging credentials (if available)
  - Prod: Use production credentials with monitoring

- [ ] **API keys have appropriate scopes** — Check GitHub PATs, Supabase keys, etc.
  - GitHub: `repo:read`, `read:org` (not full admin)
  - Supabase: Use `anon` key (not `service_role`)
  - OpenAI: Standard API key (no billing admin)

### Phase 2: MCP Configuration

- [ ] **All MCPs declare scopes** — Each MCP in mcp-config.json has `"scopes": [...]`
  ```json
  {
    "id": "example-mcp",
    "scopes": ["category:operation"]
  }
  ```

- [ ] **Scopes are minimized** — Only necessary scopes, no wildcards
  - NOT: `["database:*"]` (too broad)
  - YES: `["database:query:tasks", "database:read:schema"]` (specific)

- [ ] **Scopes match MCP capability** — Check against `MCP_SCOPE_POLICY.md`
  - Supabase: read + query only, no write/delete
  - Git: read + governance only, no force-push
  - LLM: chat + embed only, no fine-tune
  - Filesystem: watch + read only, no write/delete

- [ ] **Forbidden operations documented** — Each MCP has `"forbiddenOperations": [...]`

- [ ] **Risk level assigned** — Each MCP has `"riskLevel": "T0"|"T1"|"T2"|"T3"`
  - T0: No sensitive data access
  - T1: Read-only sensitive data
  - T2: Write to sensitive data
  - T3: Critical infrastructure access

### Phase 3: Authentication & Secrets Vault

- [ ] **SecretStore implemented** — Can verify at `/egos/packages/core/src/secrets/vault.ts`
  ```bash
  # Check vault.ts exists
  test -f /home/enio/egos/packages/core/src/secrets/vault.ts && echo "OK" || echo "MISSING"
  ```

- [ ] **EnvSecretStore used** — MCP configs use environment variables (no Vault yet)

- [ ] **Secret rotation policy documented** — Quarterly rotation schedule
  - Quarterly: Rotate all API keys
  - On incident: Immediate revocation + rotation
  - Tool: GitHub Actions scheduled job (planned)

- [ ] **Incident response for leaked token** — Document below:
  - [ ] Detect exposure (log alerts, security scan)
  - [ ] Revoke immediately (disable API key)
  - [ ] Rotate (generate new key, update env var)
  - [ ] Audit (check logs for unauthorized access)
  - [ ] Notify (internal security team, compliance)
  - [ ] Example playbook: `INCIDENT_RESPONSE_MCP.md`

### Phase 4: Audit Logging

- [ ] **ConsoleAuditLogger integrated** — MCP calls logged with audit trail
  ```bash
  # Check audit handler exists
  test -f /home/enio/egos/packages/shared/src/mcp-audit-handler.ts && echo "OK" || echo "MISSING"
  ```

- [ ] **MCP calls audit-logged** — Every tool invocation generates audit entry
  ```json
  {
    "timestamp": "2026-03-28T15:30:00Z",
    "mcp_server": "supabase-db",
    "identity": { "userId": "user_123", "source": "claude-code" },
    "action": "mcp:query",
    "scope_requested": ["database:query:tasks"],
    "scope_granted": ["database:query:tasks"],
    "result": "allowed"
  }
  ```

- [ ] **Audit logs retained** — Minimum 90 days (1 year for compliance)
  - Dev: Can delete after 7 days
  - Staging: Retain 30 days
  - Prod: Retain 1 year

- [ ] **Audit logs searchable** — Can query by:
  - Timestamp range
  - MCP server ID
  - User ID / source
  - Action / resource
  - Result (allowed/denied)

- [ ] **Access to logs restricted** — Only security team + compliance
  - No viewing audit logs in regular development
  - Special permission required in prod

### Phase 5: Scope Validation

- [ ] **Scope policy document complete** — `MCP_SCOPE_POLICY.md` exists
  ```bash
  # Check scope policy
  test -f /home/enio/egos/docs/MCP_SCOPE_POLICY.md && echo "OK" || echo "MISSING"
  ```

- [ ] **Each MCP scope justified** — Policy explains why each scope is needed
  - NOT: "It might be useful someday"
  - YES: "Required for production order tracking via tasks table"

- [ ] **Forbidden scopes documented** — Each MCP lists what it cannot do
  - Supabase: Cannot delete, truncate, or migrate
  - Git: Cannot push, force-push, or delete branches
  - LLM: Cannot fine-tune, change billing, manage accounts

- [ ] **Access control enforced** — Runtime validation before MCP call
  - Check scope in MCP call handler
  - Deny + log if scope missing
  - Return error to caller

- [ ] **Scope drift prevention** — Monthly audit of actual scopes vs. documented
  ```bash
  # Planned: Script to validate all scopes match policy
  node scripts/validate-mcp-scopes.js
  ```

### Phase 6: Deployment Integration

- [ ] **CI/CD checks pass** — Linter + tests for MCP configs
  ```bash
  # Run pre-deploy checks
  npm run lint -- --ignore-path .gitignore
  npm run test -- packages/shared/src/mcp-audit-handler.test.ts
  npm run test -- packages/core/src/secrets/vault.test.ts
  ```

- [ ] **No hardcoded secrets detected** — Security scan passes
  ```bash
  # Tool: npm audit (for dependencies)
  npm audit

  # Tool: git-secrets (for committed secrets)
  git secrets --scan
  ```

- [ ] **MCP config schema valid** — JSON schema validation
  ```bash
  # Validate MCP config schema
  npm run validate-mcp-config
  ```

- [ ] **Deployment playbook documented** — For operations team
  - How to deploy MCP servers
  - How to set environment variables
  - How to verify deployment
  - How to monitor health
  - How to respond to incidents

### Phase 7: Runtime Verification

After deployment, verify MCP servers are secure:

- [ ] **Health checks pass** — All MCPs responding
  ```bash
  # Verify MCP health
  npm run mcp-health-check
  ```

- [ ] **Secrets loading correctly** — No env var resolution errors
  ```bash
  # Check logs for "missing env var" errors
  grep -i "missing\|undefined" /var/log/mcp/*.log
  ```

- [ ] **Audit logs generating** — Sample calls are logged
  ```bash
  # Check recent audit entries
  tail -20 /tmp/egos-mcp-metrics.jsonl | jq '.audit'
  ```

- [ ] **Scopes enforced** — Unauthorized calls denied
  ```bash
  # Simulate unauthorized scope request and verify denial
  # (documented in testing guide)
  ```

- [ ] **No secrets in error messages** — Logs don't leak credentials
  ```bash
  # Scan logs for API keys (should not appear)
  grep -E "sk-|ghp_|Bearer" /var/log/mcp/*.log
  ```

---

## Sign-Off

This checklist must be **completed and signed off** by:

- [ ] **Security Team** — Verified scopes, secrets handling, audit logging
- [ ] **DevOps/SRE** — Verified deployment, monitoring, incident response
- [ ] **Product Manager** — Verified required functionality available
- [ ] **Compliance/Legal** (if health data involved) — Verified LGPD/healthcare compliance

**Sign-off format:**

```
Security: [Name] [Date] [Signature]
DevOps:   [Name] [Date] [Signature]
Product:  [Name] [Date] [Signature]
Compliance: [Name] [Date] [Signature] (if applicable)
```

---

## Example: Complete Deployment

### Pre-Flight (1 hour before deploy)

```bash
# 1. Final checks
npm run lint
npm run test
npm audit

# 2. Verify secrets are set
echo "SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:=MISSING}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:=MISSING}"
echo "DASHSCOPE_API_KEY: ${DASHSCOPE_API_KEY:=MISSING}"

# 3. Validate config
npm run validate-mcp-config

# 4. Audit current logs
wc -l /tmp/egos-mcp-metrics.jsonl
```

### Deployment (production)

```bash
# 1. Deploy new version
npm run build
vercel --prod

# 2. Verify health
npm run mcp-health-check

# 3. Monitor logs
tail -f /var/log/mcp/audit.log | grep -i "error\|denied"

# 4. Quick smoke test
curl https://forja-orpin.vercel.app/api/health
```

### Post-Deployment (validation)

```bash
# 1. Check audit logs are generating
tail -10 /tmp/egos-mcp-metrics.jsonl | jq '.'

# 2. Verify scopes enforced
# (Run test against prod API)

# 3. Alert on failures
# (Send notification if errors detected)
```

---

## Troubleshooting

### "MCP config schema invalid"
- Run: `npm run validate-mcp-config -- --verbose`
- Check JSON syntax: `cat .guarani/mcp-config.json | jq .`
- Verify all required fields present (id, name, scopes, auth, etc.)

### "Env var not found"
- List set vars: `env | grep -E "SUPABASE|OPENAI|DASHSCOPE"`
- Check .env file: `cat .env | grep VAR_NAME`
- Verify not in .gitignore: `cat .gitignore | grep env`

### "Scope denied at runtime"
- Check MCP config scopes: `jq '.servers[] | {id, scopes}' mcp-config.json`
- Check scope policy: `grep -A5 "MCP ID" docs/MCP_SCOPE_POLICY.md`
- Verify identity has scopes: `jq '.identity.scopes' /tmp/mcp-call.json`

### "Audit logs not generating"
- Check ConsoleAuditLogger: `grep -i "audit" packages/audit/src/activation-audit.ts`
- Verify audit handler registered: `npm run test -- mcp-audit-handler.test.ts`
- Check metrics path: `ls -la /tmp/egos-mcp-metrics.jsonl`

---

## Related Documents

- **MCP_SCOPE_POLICY.md** — Detailed scope definitions
- **MCP_ENV_VARS_REFERENCE.md** — All environment variables
- **packages/core/src/secrets/vault.ts** — Secret store implementation
- **packages/shared/src/mcp-audit-handler.ts** — Audit logging handler
- **packages/audit/src/activation-audit.ts** — ConsoleAuditLogger implementation
- **INCIDENT_RESPONSE_MCP.md** — Breach response procedures

---

**Last Updated:** 2026-03-28
**Owner:** Enio (EGOS Security)
**Review Cycle:** Quarterly (every 3 months)
**Next Review Due:** 2026-06-28
