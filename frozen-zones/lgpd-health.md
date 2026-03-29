# LGPD Health Data Frozen Zone

**Status:** IMMUTABLE POLICY — cannot be overridden per instance or deployment
**Last Updated:** 2026-03-28
**Regulatory Basis:** Law 13.709/2018 (LGPD), Resolução CD/ANPD nº 30/2025, Law 13.787
**Authority:** ANPD (Autoridade Nacional de Proteção de Dados)

## 1. Classification

Health data is **sensitive personal data** per LGPD Art. 5º, II.

### Data Types & Storage Rules

| Category | Storage | Retention | Example |
|----------|---------|-----------|---------|
| Raw conversation | ❌ NO | 0 days | "I feel dizzy" |
| Diagnoses (coded) | ✅ YES | 20 years | ICD-10: E11 (Diabetes) |
| Medications (coded) | ✅ YES | 20 years | "Metformin 500mg" |
| Test results | ✅ YES | 20 years | "Blood glucose: 145" |
| Phone (raw) | ❌ NO | 0 days | "+5585999999999" |
| Phone (hashed) | ✅ YES | 5 years | SHA256(phone+salt) |
| Consent events | ✅ YES | Contract+5y | {timestamp, response} |
| Telemetry | ✅ (pseudo) | 90 days | {id_hash, action, time} |

## 2. Storage Mandates

### Raw Conversations
- **Delete:** Immediately after structured extraction (≤1 hour)
- **Exception:** None
- **Reason:** Highest risk; unstructured; enables re-identification

### Structured Clinical Data
- **Retain:** Minimum 20 years (Law 13.787)
- **Location:** Hospital's clinical system (MV, Tasy), NOT in middleware
- **Encrypt:** AES-256 at rest
- **Access:** RLS + role-based + audit logged

### Consent Log
- **Retain:** Contract duration + 5 years
- **Format:** Append-only; no UPDATE/DELETE
- **Content:** timestamp, hashed_phone, consent_version, response, IP

### Telemetry
- **Retain:** 90 days maximum
- **Pseudonymize:** SHA256(phone + SALT) where SALT ≠ hardcoded
- **Never include:** raw phone, name, diagnoses, medications
- **Purpose:** Debugging, performance analysis only

## 3. Processing Mandates

### Consent (Dual-Layer)
**Layer 1: Channel** (WhatsApp/SMS)
- Explicit opt-in before any health conversation
- Recorded immutably in consent_log
- Revokable anytime via `/stop` command

**Layer 2: Clinical** (Assistential care)
- Base legal: LGPD Art. 11, II-a (healthcare treatment)
- Applies when patient is registered in hospital
- No additional consent needed (dual-layer satisfied)

### Pseudonymization
- **Function:** SHA256(phone + SALT)
- **Salt:** 32-byte random, stored in separate vault (NOT hardcoded)
- **Re-id Map:** Encrypted (AES-256); access audit-logged
- **Scope:** All operational logs; never pseudonymize clinical extracts

### Encryption
- **At Rest:** AES-256 (pgp_sym_encrypt in PostgreSQL)
- **In Transit:** TLS 1.3+ (HSTS headers)
- **Key Rotation:** Quarterly; old keys archived
- **Access:** Encryption key from environment variable only

### Access Control
- **RLS:** Row-Level Security mandatory on all health tables
- **Roles:** patient (own data), provider (assigned), admin, auditor
- **No Admin Bypass:** Even admins require audit-logged approval
- **Enforcement:** System prevents UPDATE/DELETE on clinical data

## 4. Incident Response

### Detection Timeline
| Event | SLA | Action |
|-------|-----|--------|
| Unauthorized access | 12h | Investigate; assess risk |
| Data exposure | 12h | Measure scope; quarantine |
| Deletion failed | 24h | Manual purge; check cron |
| System down | Real-time | Restore; notify hospital |
| Third-party breach | 24h | Investigate hospital impact |

### Notification Timeline
- **ANPD:** 3 business days if risk detected
- **Hospital:** 2 hours if HIGH risk; 6h if MEDIUM
- **Patients:** 72 hours if harm confirmed (hospital decides)

### Playbook
See `docs/INCIDENT_RESPONSE_HEALTH.md` for detailed 5+ scenarios:
1. Unauthorized access
2. Phone number exposed in log
3. Deletion failed
4. System down >1 hour
5. Third-party breach impacts you

## 5. Contracting (DPA Clauses)

**Mandatory in hospital contract:**
1. **Purpose:** Explicitly defined (clinical decision support via WhatsApp only)
2. **Data Types:** Explicit list (diagnoses, medications, test results)
3. **Retention:** Per type (raw: 0d; structured: 20y; consent: 5y; telemetry: 90d)
4. **Sub-processors:** Each vendor listed + hospital approval required
5. **Breach Notification:** 24-hour timeline
6. **Audit Rights:** Hospital can audit annually
7. **Liability:** Indemnification for your negligence
8. **Termination:** Data deletion attestation required

## 6. Enforcement

### Pre-Deploy Checks (Automated)
```
[ ] No raw phone numbers in code
[ ] No test/real CPF in code
[ ] Retention windows defined (.env)
[ ] Delete cron job for raw conversations exists
[ ] Consent log table created (append-only)
[ ] RLS policies on clinical tables
[ ] Encryption triggers enabled
[ ] TLS 1.3+ configured
[ ] No hardcoded secrets (gitleaks)
[ ] TypeScript compiles (0 errors)
```

See `frozen-zones/lgpd-health-checklist.md` for full 15-item checklist.

### Ongoing Audits (Weekly)
- Automated scan: Raw phones in telemetry? → ALERT
- Consent log: Any DELETE operations? → INVESTIGATION
- RLS: Policies still active? → RE-APPLY if missing
- Telemetry: Older than 90d? → DELETE automatically
- Encryption: Triggers still firing? → RE-APPLY if missing

### Quarterly Review
- Hospital + legal counsel audit
- Encryption key rotation verification
- Access pattern anomalies
- RLS enforcement verification
- Signed compliance attestation

### Breach Simulation (Quarterly)
- Tabletop exercise: "Clinical system breached"
- Verify incident playbook executable
- Update playbook if gaps found
- Document decisions + timeline

---

## Quick Reference: What Can/Cannot Be Stored

| Data | Store? | Format | Example |
|------|--------|--------|---------|
| Raw symptom text | ❌ | N/A | "I feel dizzy" |
| Symptom code (SNOMED) | ✅ | Coded | "R06.02" |
| Raw diagnosis | ❌ | N/A | "Diabetes" |
| Diagnosis code (ICD-10) | ✅ | Coded | "E11" |
| Phone number (raw) | ❌ | N/A | "+5585999" |
| Phone hash (SHA256) | ✅ | Hex | "a7f3..." |
| Timestamp (in logs) | ❌ | N/A | "2026-03-28 14:30" |
| Timestamp (structured) | ✅ | ISO | "2026-03-28" (no time) |
| Consent yes/no | ✅ | Immutable | {yes, 2026-03-28} |
| Test result value | ✅ | Structured | {glucose: 145, unit: "mg/dL"} |
| Patient name | ❌ | N/A | "João Silva" |
| Patient ID (hospital) | ✅ | Coded | hospital_patient_id_123 |

---

## Consequences of Violation

This policy is **immutable** and **binding**:
1. **Code review rejection** — PRs violating this policy blocked by CI
2. **Deployment block** — Pre-deploy checklist failure = no production push
3. **Incident escalation** — Any violation → hospital + ANPD notification
4. **Contract suspension** — Hospital may pause integration
5. **Legal liability** — LGPD fines: up to 2% annual revenue or R$50M

**No exceptions. No overrides.**

---

**Status:** ACTIVE (enforced by default)
**Review:** Annually + after ANPD guidance changes
**Last validated:** 2026-03-28
**Next review:** 2027-03-28

