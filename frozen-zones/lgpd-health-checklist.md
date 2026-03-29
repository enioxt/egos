# Pre-Deploy Checklist — Health-Data Systems

**Purpose:** Verify LGPD compliance before deploying health-related systems
**Frequency:** Required for every production deployment
**Owner:** Engineering team (automated) + DPO/Legal (manual sign-off)
**Status:** MANDATORY — deployment blocked if any item unchecked

---

## Automated Checks (CI/CD Pipeline)

Run automatically on every commit to main branch.

### 1. ✓ No raw phone numbers in logs
```bash
grep -r '\+55[0-9]\{10,11\}' src/ lib/ && exit 1 || echo "✓ PASS"
```
**Rationale:** Raw phone enables re-identification
**Fix:** Use `pseudonymize(phone)` from `lib/pseudonymizer.ts`

### 2. ✓ No test/real CPF in code
```bash
grep -r '[0-9]\{3\}\.[0-9]\{3\}\.[0-9]\{3\}-[0-9]\{2\}' src/ && exit 1 || echo "✓ PASS"
```
**Rationale:** Even test CPFs are dangerous
**Fix:** Use faker library for tests; never hardcode

### 3. ✓ Retention windows defined
```bash
grep 'TELEMETRY_RETENTION_DAYS' .env && grep 'CONSENT_RETENTION_YEARS' .env && echo "✓ PASS"
```
**Expected values:** TELEMETRY=90, CONSENT=5, CLINICAL=20

### 4. ✓ Delete cron job confirmed
```bash
grep -r 'DELETE.*raw_conversations' supabase/migrations/ && echo "✓ PASS"
```
**Fix:** Add migration with cron schedule (hourly)

### 5. ✓ Audit log captures consent
```bash
grep 'consent_log' supabase/migrations/ && echo "✓ PASS"
```
**Verify:** Table exists with columns: created_at, consent_version, response

### 6. ✓ RLS policies enforced
```bash
grep 'ENABLE ROW LEVEL SECURITY' supabase/migrations/ && echo "✓ PASS"
```
**Verify:** At least 1 policy per sensitive table

### 7. ✓ Encryption at rest enabled
```bash
grep 'pgp_sym_encrypt' supabase/migrations/ && echo "✓ PASS"
```
**Verify:** Triggers call pgp_sym_encrypt; key from env var (not hardcoded)

### 8. ✓ TLS 1.3+ enforced
```bash
grep 'Strict-Transport-Security' next.config.ts && echo "✓ PASS"
```
**Verify:** HSTS header; secure cookie flags

### 9. ✓ No hardcoded secrets
```bash
gitleaks detect --exit-code 1 && echo "✓ PASS"
```
**Fix:** Use environment variables only

### 10. ✓ TypeScript compilation succeeds
```bash
npm run build && echo "✓ PASS"
```

---

## Manual Checks (DPO / Legal Sign-Off)

Require human verification before production.

### 11. ✓ DPA signed by hospital
**File:** `contracts/DPA_[HospitalName]_[YYYY].pdf`
**Covers:**
- [ ] Lawful basis (Art. 11, II-a assistential care)
- [ ] Data types explicitly listed
- [ ] Retention periods per type
- [ ] Sub-processor list (Supabase, LLM provider, etc.)
- [ ] Breach notification (24-hour timeline)
- [ ] Audit rights (hospital can audit annually)
- [ ] Termination clause (data deletion upon contract end)
- [ ] Liability & indemnification

**How to fix:** Provide completed DPA to hospital DPO; request signature within 5 business days

### 12. ✓ Incident playbook documented + tested
**File:** `docs/INCIDENT_RESPONSE_HEALTH.md`
**Verify:**
- [ ] Covers 5+ scenarios (unauthorized access, exposure, deletion failed, system down, third-party breach)
- [ ] Each scenario has: timeline, action steps, contacts, escalation path
- [ ] Tabletop drill completed (last 90 days)
- [ ] Results documented

**How to fix:** Write playbook; conduct 2-hour tabletop exercise; document findings

### 13. ✓ Consent collection verified
**Verify:**
- [ ] Users see explicit opt-in before health data
- [ ] Consent recorded with timestamp + IP + device
- [ ] User can revoke consent anytime (`/stop` command)
- [ ] Revocation honored within 24 hours
- [ ] Consent reminder sent every 90 days

**Test:**
1. Send health message as test user
2. System should prompt: "Consent to share health data?" (Y/N)
3. Click Y → verify recorded in consent_log
4. Click N → system rejects health requests
5. Type `/stop` → consent revoked, verified in DB

### 14. ✓ Hospital IT/DPO training completed
**Verify:**
- [ ] Hospital DPO understands architecture
- [ ] Hospital IT can audit logs (provided read-only access)
- [ ] Hospital DPO knows incident timeline (24h notification)
- [ ] Hospital IT trained on RLS policies
- [ ] Contact info documented (DPO, IT lead, legal)

**How:** Conduct 1-hour knowledge transfer call; document attendees

### 15. ✓ Pseudonymization salt is secure
**Verify:**
- [ ] PSEUDONYM_SALT is 32-byte random hex
- [ ] Stored in secure vault (NOT in repo/`.env.example`)
- [ ] Hospital does NOT have salt access
- [ ] Salt rotated annually
- [ ] Old salt archived (not deleted)

**Check:** `echo $PSEUDONYM_SALT | wc -c` should be 65 (64 hex + newline)

---

## Pre-Deployment Sign-Off

| Role | Sign-Off | Method | Deadline |
|------|----------|--------|----------|
| Engineering | "Code review complete, tests pass" | GitHub PR approval | Required |
| DPO/Legal | "LGPD compliance verified" | Email or signed doc | Required |
| Hospital | "Approved for integration" | Email or verbal (logged) | Required |
| Security | "Encryption & auth verified" | Security audit | Required |

---

## GitHub Actions Workflow

Save as `.github/workflows/lgpd-compliance-check.yml`:

```yaml
name: LGPD Compliance Check
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for raw phone numbers
        run: |
          ! grep -r '\+55[0-9]\{10,11\}' src/ lib/ 2>/dev/null
          echo "✓ No raw phones"

      - name: Check for CPFs
        run: |
          ! grep -r '[0-9]\{3\}\.[0-9]\{3\}\.[0-9]\{3\}-[0-9]\{2\}' src/ lib/ 2>/dev/null
          echo "✓ No CPFs"

      - name: Verify retention windows
        run: |
          grep -q TELEMETRY_RETENTION_DAYS .env.example || exit 1
          echo "✓ Retention defined"

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2

      - name: TypeScript compilation
        run: npm run build

      - name: All checks passed
        run: echo "✅ LGPD compliance checks PASSED"
```

---

## Running Locally

```bash
# Run all automated checks
npm run lint                    # ESLint
npm run build                   # TypeScript
gitleaks detect                 # Secrets scan

# Manual verification
grep -r '\+55[0-9]\{10,11\}' src/  # Phone numbers
grep -r 'CPF_PATTERN' src/         # CPF values
grep 'RETENTION_DAYS' .env         # Retention windows
grep 'RLS' supabase/migrations/    # RLS policies
```

---

**Status:** ACTIVE — enforced on every deployment
**Last validated:** 2026-03-28
**Review cadence:** Annually + after every incident

No exceptions. This checklist is binding.
