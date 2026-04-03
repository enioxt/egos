# Incident Response Playbook — MCP Security Breaches — EGOS-004

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** MCP-specific security incident response runbook
- **Summary:** Operational procedures for leaked credentials, unauthorized MCP actions, and containment/recovery workflows.
- **Read next:**
  - `docs/MCP_SCOPE_POLICY.md` — preventive scope controls
  - `docs/INCIDENT_RESPONSE_HEALTH.md` — regulated incident handling
  - `TASKS.md` — active remediation tasks
<!-- llmrefs:end -->

**Date:** 2026-03-28
**Status:** ACTIVE
**Purpose:** Step-by-step procedures for responding to MCP security incidents (leaked tokens, unauthorized access, etc.)

---

## Incident Types & Response Procedures

### Incident Type 1: Leaked API Key

**Severity:** CRITICAL

**When this happens:**
- Secret scanning tool detects exposed key in code/logs/chat
- Developer accidentally commits credentials
- Key found in git history
- Key exposed in error message or logs

**Response Timeline:**

#### IMMEDIATELY (< 5 minutes)

- [ ] **STOP all activity** on that MCP server
  - Disable the affected MCP in `mcp-config.json` (set `"enabled": false`)
  - This prevents further exploitation

- [ ] **Notify on-call security**
  - Slack: `@security-oncall Incident: MCP key exposed`
  - Include: Which key, where found, potential impact

- [ ] **Revoke the key immediately**
  - **OpenAI:** https://platform.openai.com/account/api-keys → delete key
  - **DashScope:** https://dashscope.console.aliyun.com/api-key → revoke
  - **GitHub:** https://github.com/settings/tokens → delete token
  - **Supabase:** Supabase dashboard → Settings → API Keys → delete key
  - **Exa:** https://dashboard.exa.ai/api-keys → revoke

**Command examples:**
```bash
# Disable affected MCP in config
jq '.servers[] |= if .id == "llm-router" then .enabled = false else . end' \
  /home/enio/egos/.guarani/mcp-config.json > /tmp/mcp-config.json.tmp
mv /tmp/mcp-config.json.tmp /home/enio/egos/.guarani/mcp-config.json

# Commit immediately
git add .guarani/mcp-config.json
git commit -m "SECURITY: Disable llm-router due to exposed API key"
git push origin main
```

#### WITHIN 30 MINUTES (< 30 min)

- [ ] **Generate new API key**
  - Follow same procedure as initial setup (see MCP_ENV_VARS_REFERENCE.md)
  - Use different key than before (if possible)

- [ ] **Update environment variables**
  - Dev: Update `.env.local`
  - Staging: Update in deployment dashboard
  - Prod: Update via CI/CD secrets (GitHub, Vercel, etc.)

- [ ] **Test new key**
  ```bash
  # Quick test that new key works
  npm run test-mcp -- --mcp-id llm-router --quick
  ```

- [ ] **Re-enable the MCP**
  ```bash
  # Re-enable in config
  jq '.servers[] |= if .id == "llm-router" then .enabled = true else . end' \
    /home/enio/egos/.guarani/mcp-config.json > /tmp/mcp-config.json.tmp
  mv /tmp/mcp-config.json.tmp /home/enio/egos/.guarani/mcp-config.json

  # Deploy
  git add .guarani/mcp-config.json
  git commit -m "SECURITY: Re-enable llm-router with rotated API key"
  git push origin main
  ```

#### WITHIN 2 HOURS (< 2h)

- [ ] **Audit access logs**
  ```bash
  # Check if compromised key was used
  grep "OPENAI_API_KEY\|llm-router" /tmp/egos-mcp-metrics.jsonl | \
    jq 'select(.timestamp > "2026-03-28T12:00:00Z")'
  ```

- [ ] **Determine breach scope**
  - Who could access the exposed key?
  - How long was it exposed?
  - Was it actually used by unauthorized parties?
  - What data could be accessed with this scope?

- [ ] **Notify stakeholders**
  - Internal: Security team, DevOps, Product team
  - External (if applicable): Affected customers, compliance officer

#### WITHIN 24 HOURS (< 24h)

- [ ] **Write incident report**
  - What happened
  - When it was discovered
  - Impact assessment
  - Actions taken
  - Root cause analysis
  - Prevention measures

- [ ] **Update incident log**
  ```
  File: /home/enio/egos/docs/SECURITY_INCIDENTS.log
  Date: 2026-03-28
  Type: Leaked API Key
  MCP: llm-router (OPENAI_API_KEY)
  Status: RESOLVED
  Cause: Developer commit
  Impact: 0 unauthorized calls
  ```

---

### Incident Type 2: Unauthorized MCP Access

**Severity:** HIGH

**When this happens:**
- Audit logs show calls from unknown identity
- Scope mismatch: broader scopes than expected
- Access to forbidden resources
- Repeated denied calls from same identity

**Response Timeline:**

#### IMMEDIATELY (< 5 minutes)

- [ ] **Identify the threat**
  ```bash
  # Find suspicious audit entries
  grep "result.*denied\|scopes.*mismatch" /tmp/egos-mcp-metrics.jsonl | \
    tail -20 | jq '.identity, .action, .resource'
  ```

- [ ] **Check if access was successful**
  ```bash
  # If status = denied, no data was accessed
  grep '"result": "allowed"' /tmp/egos-mcp-metrics.jsonl | \
    grep "unknown_user\|suspicious_id"
  ```

- [ ] **If no success**: Continue monitoring
- [ ] **If access succeeded**: Escalate to CRITICAL

#### WITHIN 1 HOUR (< 1h)

- [ ] **Analyze what was accessed**
  ```bash
  # Get list of allowed operations
  jq '.servers[] | select(.id == "AFFECTED_MCP") | .governance.allowedTables' \
    /home/enio/egos/.guarani/mcp-config.json
  ```

- [ ] **Determine data exposure**
  - What tables were queried?
  - How many rows returned?
  - What personally identifiable info (PII) accessed?

- [ ] **Revoke compromised credentials**
  - If GITHUB_TOKEN used: Regenerate and revoke
  - If identity token involved: Invalidate it
  - If session token: Kill all sessions from that identity

- [ ] **Update scope restrictions**
  ```bash
  # Tighten scopes if too broad
  jq '.servers[] |= if .id == "affected-mcp" then .scopes = ["restricted:scope"] else . end' \
    /home/enio/egos/.guarani/mcp-config.json
  ```

#### WITHIN 4 HOURS (< 4h)

- [ ] **Notify affected users** (if PII accessed)
  - Required if personal data exposed
  - Include: What data, when, actions taken, what they should do

- [ ] **File regulatory report** (if LGPD/healthcare data)
  - ANPD notification (if risk detected) — within 3 business days
  - Internal compliance team
  - Legal review

#### WITHIN 24 HOURS (< 24h)

- [ ] **Post-incident analysis**
  - How did unauthorized access occur?
  - Was scope validation working?
  - Were audit logs captured?
  - What preventive measures needed?

- [ ] **Update detection rules**
  - Add identity to watchlist
  - Tighten scope validation
  - Add alerting for repeated denials

---

### Incident Type 3: MCP Misconfiguration (Over-Scoped)

**Severity:** MEDIUM

**When this happens:**
- Audit review finds MCP with broader scopes than needed
- Scope policy violation detected
- Over-privilege grant to MCP

**Response Timeline:**

#### WITHIN 24 HOURS (< 24h)

- [ ] **Verify the scope is actually used**
  ```bash
  # Check if scope was actually invoked
  grep '"scope.*:write"' /tmp/egos-mcp-metrics.jsonl | wc -l
  ```

- [ ] **If not used**: Remove scope immediately
  ```bash
  jq '.servers[] |= if .id == "mcp" then .scopes -= ["unused:scope"] else . end' \
    /home/enio/egos/.guarani/mcp-config.json
  ```

- [ ] **If used**: Document why
  - Add comment in mcp-config.json
  - Link to business requirement
  - Set quarterly re-review date

- [ ] **Update scope policy**
  - Document scope in `MCP_SCOPE_POLICY.md`
  - Explain why it's necessary
  - List any risks

---

### Incident Type 4: Audit Log Tampering / Loss

**Severity:** CRITICAL

**When this happens:**
- Audit logs deleted or corrupted
- Audit entries missing for time period
- Cannot reconstruct activity
- Data integrity compromised

**Response Timeline:**

#### IMMEDIATELY (< 5 minutes)

- [ ] **STOP using affected MCP**
  - Disable in config until resolved
  - May indicate compromise

- [ ] **Check backups**
  ```bash
  # Verify backups exist
  ls -la /backups/egos-mcp-metrics*.jsonl.bak
  ```

- [ ] **Restore from backup**
  ```bash
  # Restore if available
  cp /backups/egos-mcp-metrics.jsonl.bak.2026-03-28 /tmp/egos-mcp-metrics.jsonl
  ```

#### WITHIN 2 HOURS (< 2h)

- [ ] **Investigate how tampering occurred**
  - Who had access to log files?
  - Was filesystem compromised?
  - Was audit logger disabled?
  - Check git history for deletions

- [ ] **Verify no other data affected**
  - Check database integrity
  - Verify code/config unchanged
  - Check for other suspicious activity

#### WITHIN 24 HOURS (< 24h)

- [ ] **Enhanced monitoring**
  - Enable log rotation with write-once storage
  - Send audit logs to external service (syslog, CloudWatch)
  - Alert on any log deletions

- [ ] **Post-incident review**
  - What allowed tampering?
  - How to prevent in future?
  - Do we need immutable logging?

---

## Detection & Alerting

### Automated Detection

Configure alerts for:

```bash
# 1. Repeated scope denials
# Alert if same identity denied >3 times in 5 min
grep '"result": "denied"' /tmp/egos-mcp-metrics.jsonl | \
  jq '.identity.userId' | sort | uniq -c | awk '$1 > 3 {print}'

# 2. Unusual MCP access patterns
# Alert if MCP called outside normal hours
jq 'select(.timestamp | strptime("%Y-%m-%dT%H:%M:%SZ") | hour > 22 or hour < 6)' \
  /tmp/egos-mcp-metrics.jsonl

# 3. New identity accessing MCP
# Alert if new user appears in logs
jq '.identity.userId' /tmp/egos-mcp-metrics.jsonl | sort | uniq > /tmp/current_ids
comm -23 /tmp/current_ids /tmp/previous_ids
```

### Manual Audits

**Weekly:** Review denied calls
```bash
jq 'select(.result == "denied")' /tmp/egos-mcp-metrics.jsonl | \
  jq -s 'group_by(.identity.userId) | map({userId: .[0].identity.userId, denials: length})' | \
  jq 'sort_by(.denials) | reverse | .[0:10]'
```

**Monthly:** Review all MCP scopes
```bash
npm run validate-mcp-scopes
```

**Quarterly:** Full security audit
```bash
npm run security-audit
```

---

## Communication Templates

### Slack Alert (Immediate)

```
:rotating_light: MCP SECURITY INCIDENT

Type: [LEAKED_KEY | UNAUTHORIZED_ACCESS | MISCONFIGURATION | LOG_TAMPERING]
MCP: [supabase-db | llm-router | etc]
Severity: [CRITICAL | HIGH | MEDIUM]
Time: [2026-03-28T15:30:00Z]
Status: [DETECTED | INVESTIGATING | MITIGATED | RESOLVED]

Details: [Brief description]
Next Steps: [Immediate action taken]

On-call: @security-oncall
Incident Lead: [Name]

Thread: [Link to incident tracking]
```

### Email Notification (Customers)

```
Subject: Security Incident Notification — [Date] — RESOLVED

Dear [Customer],

We discovered and resolved a security incident on [Date] affecting
the [MCP Service] component. Here's what you need to know:

WHAT HAPPENED:
[Explain in non-technical terms]

IMPACT TO YOU:
- No personal data accessed
- [OR] Personal data [Name] may have been accessed
- [OR] No impact to your account

WHAT WE DID:
- Immediately revoked compromised credentials
- Rotated all related API keys
- Enhanced monitoring and logging
- Full security audit completed

WHAT YOU SHOULD DO:
- Change any passwords
- Monitor for suspicious activity
- Contact us with questions

TIMELINE:
- [Date/Time]: Incident detected
- [Date/Time]: Credentials revoked
- [Date/Time]: System restored
- [Date/Time]: Full audit completed

Questions? Contact security@egos.ia.br

Best regards,
EGOS Security Team
```

---

## Escalation Contacts

**Security Team:** security@egos.ia.br
**On-Call (24/7):** [Pager duty / On-call schedule]
**Compliance Officer:** compliance@egos.ia.br
**Legal Team:** legal@egos.ia.br
**CEO:** [Name] (for regulatory incidents)

---

## Post-Incident Tasks

After any incident:

1. **Write incident report** (within 24h)
   - File: `/home/enio/egos/docs/SECURITY_INCIDENTS/[DATE]_[TYPE].md`

2. **Update incident log** (within 24h)
   - File: `/home/enio/egos/docs/SECURITY_INCIDENTS.log`

3. **Track follow-up items** (within 48h)
   - Update TASKS.md with prevention measures
   - Set owner and due date

4. **Share learnings** (within 1 week)
   - Team meeting / blog post
   - Update playbook based on what we learned
   - Update detection rules

5. **Verify fixes** (within 1 month)
   - Confirm prevention measures implemented
   - Run security tests
   - Document what changed

---

## Example: Full Incident Response

### Scenario: OPENAI_API_KEY leaked in git commit

**T+0min: Detection**
```
GitHub secret scanning alerts: OPENAI_API_KEY found in commit abc123
```

**T+2min: Immediate Actions**
```bash
# 1. Disable affected MCP
jq '.servers[] |= if .id == "llm-router" then .enabled = false else . end' \
  /home/enio/egos/.guarani/mcp-config.json | \
  tee /tmp/mcp-config-disabled.json

# 2. Commit disable
git add .guarani/mcp-config.json
git commit -m "SECURITY: Disable llm-router due to exposed API key"
git push origin main

# 3. Notify team
# Slack message sent
```

**T+10min: Investigation**
```bash
# 1. Check if key was used
grep "OPENAI_API_KEY\|llm-router" /tmp/egos-mcp-metrics.jsonl | \
  jq 'select(.timestamp > "2026-03-28T15:00:00Z")'

# Result: 3 calls from authorized identity, no unauthorized access

# 2. Revoke key
# OpenAI dashboard: Delete key sk-proj-abc123
```

**T+20min: Restoration**
```bash
# 1. Generate new key
# OpenAI: Create new key

# 2. Update env var
# GitHub: Update OPENAI_API_KEY secret

# 3. Test new key
npm run test-mcp -- --mcp-id llm-router --quick

# 4. Re-enable MCP
jq '.servers[] |= if .id == "llm-router" then .enabled = true else . end' \
  /home/enio/egos/.guarani/mcp-config.json | \
  tee /tmp/mcp-config-enabled.json

# 5. Deploy
git add .guarani/mcp-config.json
git commit -m "SECURITY: Re-enable llm-router with rotated API key"
git push origin main
```

**T+1h: Documentation**
```bash
# 1. Create incident report
cat > /home/enio/egos/docs/SECURITY_INCIDENTS/2026-03-28_LEAKED_OPENAI_KEY.md << 'EOF'
# Incident: Leaked OpenAI API Key

**Date:** 2026-03-28
**Severity:** CRITICAL
**Status:** RESOLVED

## Timeline
- T+0: GitHub secret scanning detected key in commit abc123
- T+2: Disabled llm-router MCP
- T+10: Verified no unauthorized access in logs
- T+20: Revoked old key, generated new key, re-enabled MCP

## Impact
- 0 unauthorized API calls
- 0 data accessed
- MCP service restored in 20 minutes

## Cause
Developer accidentally committed .env file

## Prevention
- Add comprehensive .env to .gitignore
- Train team on secret management
- Enable pre-commit hooks to scan for secrets
EOF

# 2. Update log
echo "2026-03-28 CRITICAL RESOLVED Leaked OPENAI_API_KEY" >> \
  /home/enio/egos/docs/SECURITY_INCIDENTS.log
```

**T+24h: Follow-up**
```bash
# 1. Update tasks
# Add: Implement pre-commit secret scanning
# Add: Review all exposed keys in git history

# 2. Update playbook
# Update INCIDENT_RESPONSE_MCP.md with learnings

# 3. Team meeting
# Discuss what happened and how to prevent next time
```

---

## References

- **MCP Security Hardening:** `/egos/docs/EGOS-004_MCP_SECURITY_HARDENING.md`
- **Scope Policy:** `/egos/docs/MCP_SCOPE_POLICY.md`
- **Environment Variables:** `/egos/docs/MCP_ENV_VARS_REFERENCE.md`
- **Deployment Checklist:** `/egos/docs/MCP_DEPLOYMENT_CHECKLIST.md`
- **Audit Handler:** `/egos/packages/shared/src/mcp-audit-handler.ts`
- **Secret Store:** `/egos/packages/core/src/secrets/vault.ts`

---

**Last Updated:** 2026-03-28
**Owner:** Enio (EGOS Security)
**Review Cycle:** Quarterly
**Next Review Due:** 2026-06-28
