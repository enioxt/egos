# Incident Response Playbook — Health Data Breaches

**Scope:** All systems processing health-related personal data
**Activation:** ANY suspected unauthorized access, exposure, or loss
**Escalation:** On-call engineer → CISO → DPO → Hospital → ANPD
**Regulatory:** LGPD Art. 34; ANPD Resolução 30/2025

---

## Scenario 1: Unauthorized Access Detected

**Timeline:** T+0h to T+72h
**Trigger:** Audit logs show unusual access patterns (multiple users, off-hours, unknown IP)

### T+0h: Immediate Detection
```
[ ] Page on-call engineer (SMS + Slack)
[ ] Engage CISO (severity assessment)
[ ] Do NOT alert hospital yet (verify real breach first)
[ ] Preserve evidence (no log deletion)
```

### T+1h: Investigation
```sql
SELECT * FROM audit_logs
WHERE accessed_at > now() - interval '24 hours'
ORDER BY accessed_at DESC;
-- Check: unusual IPs, off-hours access, bulk queries, exports
```

### T+2h: Severity Assessment
- **LOW:** <10 records, normal IP/time → log incident, no notification
- **MEDIUM:** 10-100 records, suspicious but not exfiltrated → notify hospital within 6h
- **HIGH:** 100+records or exfiltration detected → notify hospital within 2h
- **CRITICAL:** 1000+ records, ongoing breach, multiple accounts compromised → immediate notification

### T+2-6h: Hospital Notification
```
Subject: URGENT: Security Incident — [Hospital] Patient Data Access

Your [X] patient records were accessed at [TIME].
Access was: [authorized/unauthorized]
Risk level: [LOW/MEDIUM/HIGH]
Our status: Investigation ongoing; preliminary findings attached.
Hospital's role: Verify account compromise; determine if patient notification needed.
```

### T+24h: Root Cause Analysis
```
Likely causes:
1. Credential compromise (phishing, password reuse, malware)
2. Account sharing (user shared credentials with colleague)
3. Insider threat (authorized user exceeding scope)
4. Application vulnerability (SQL injection, RLS bypass)

Investigations for each:
- Check: Failed login attempts, new device, unusual query patterns
- Document: Which hypothesis is most likely (%) and why
```

### T+72h: ANPD & Patient Notification
```
If risk detected (unauthorized access = risk of harm):
→ Notify ANPD within 3 business days
→ Hospital notifies patients within 72 hours

Email template for ANPD (hospital sends):
---
NOTIFICAÇÃO DE INCIDENTE — Acesso Não Autorizado

Registros afetados: [X] pacientes
Dados: Diagnósticos, medicamentos, test results
Causa: [Credential compromise / etc]
Ações tomadas: [Password reset, monitoring, training]
---
```

---

## Scenario 2: Phone Number Exposed in Log

**Timeline:** T+0h to T+24h
**Trigger:** Automated scan detects raw phone pattern in telemetry

### T+0.25h: Scope Measurement
```sql
SELECT COUNT(*) FROM telemetry_events
WHERE context::text ~ '\+55[0-9]{10,11}';
-- Result: How many logs, which phones, what time window?
```

### T+1h: Exposure Assessment
```
- Sensitivity: CRITICAL (raw phone = direct identifier)
- Exposure: Who has access to these logs? (hospital IT, monitoring tools)
- Duration: How long have phones been exposed?
- Exfiltration: Any evidence of external download?

RISK: HIGH → Immediate purge + hospital notification
```

### T+1h: Data Purge
```sql
-- Backup for forensics
COPY raw_conversations TO '/tmp/phone-exposure-backup.csv';

-- Delete
DELETE FROM telemetry_events
WHERE context::text ~ '\+55[0-9]{10,11}';

-- Verify
SELECT COUNT(*) FROM telemetry_events
WHERE context::text ~ '\+55[0-9]{10,11}';
-- Expected: 0
```

### T+2h: Hospital Notification
```
We detected and remediated a data exposure.
What happened: [X] logs captured raw phone numbers (3-day window)
What we did: Purged all logs; verified deletion
What you should do: Check your backups/monitoring; notify patients if needed
```

### T+24h: Root Cause & Prevention
```
Root cause: Bug in logging function (logged context instead of hashed values)
Prevention: Code review + regression test; CI check for raw phone patterns
```

---

## Scenario 3: Deletion Failed (Data Not Purged)

**Timeline:** T+0h to T+24h
**Trigger:** Scheduled delete job fails; raw conversations retained >1 hour

### T+4h: Detection (monitoring check every 4h)
```sql
SELECT COUNT(*) FROM raw_conversations
WHERE created_at < now() - interval '1 hour';
-- If COUNT > 0: ALERT
```

### T+4.5h: Root Cause
```
Check cron logs: Why did delete job fail?
Likely causes:
- Database connection pool exhausted
- Long-running query blocking cleanup
- Permissions issue (cannot delete)
```

### T+5h: Manual Purge
```sql
DELETE FROM raw_conversations
WHERE created_at < now() - interval '1 hour';

VERIFY: SELECT COUNT(*) should be 0
```

### T+6h: Hospital Notification
```
We identified a failure in automatic cleanup that left [X] conversations
in database for [Y] hours (violation of 1-hour SLA).
What we did: Manually purged; implemented hourly monitoring; increased DB pool.
What you should check: Your backups don't contain our raw conversations.
```

### T+24h: Fix Deployment
```
Root cause: DB connection pool limit (20) was exhausted by analytics query
Solution: Increase pool to 50; separate analytics to read replica
Monitoring: Hourly check for conversations >2 hours old
```

---

## Scenario 4: System Down >1 Hour

**Timeline:** T+0h to T+90min
**Trigger:** API unresponsive for >15 minutes; hospital cannot use system

### T+15min: Monitoring Alert
```
Alert: api.health-chat unavailable
Duration: 15+ minutes
Impact: Hospital blocked from patient queries
Action: Page on-call engineer
```

### T+30min: Hospital Notification (if still down)
```
Subject: URGENT: Health Chat Service Unavailable

Service: DOWN for 30 minutes
Cause: Being investigated [infrastructure/upstream/network]
ETA: Restoration estimate [X minutes/unknown]
Contingency: Hospital may route to manual triage
```

### T+60min: ANPD Decision (if down >60 min)
```
Question: Is this a "breach" requiring ANPD notification?
Answer: NO (unavailability ≠ breach; no data compromised)

But if unavailability causes HARM to patients:
→ Hospital may self-report to ANPD (informational)
```

### T+90min: Restore Service
```
Actions: Restart services / failover / fix upstream issue
Verify: curl health endpoint; hospital confirms chat works
Timeline: Root cause analysis within 24h
```

### T+24h: Post-Incident Communication
```
Timeline: Service down [90 minutes] due to [root cause]
Root cause: [DB connection pool / upstream provider / network]
Permanent fix: [Deployed: separate pool / increased limits / monitoring]
```

---

## Scenario 5: Third-Party Breach Impacts You

**Timeline:** T+0h to T+7d
**Trigger:** Hospital says "Our clinical system was breached; attackers accessed patient data we shared with you"

### T+0h: Hospital's Breach Report
```
Hospital: "Our clinical system compromised; patients affected: 1.2M"
Question: Does this include data we hold?
Hospital: "Yes, clinical extracts from your integration"
```

### T+2h: Your Investigation
```sql
-- Do we still have raw conversations? (should be NO)
SELECT COUNT(*) FROM raw_conversations
WHERE created_at > date '2020-01-01';
-- Expected: 0 (deleted per policy)

-- How many patient records do we have?
SELECT COUNT(DISTINCT patient_id) FROM clinical_extracts;
-- Result: [X] patients from hospital

-- Are they still encrypted?
SELECT COUNT(*) FROM clinical_extracts
WHERE clinical_notes IS NOT NULL;  -- If NULL, encryption intact
```

### T+6h: Your Response to Hospital
```
Processor's Assessment:

Data we hold: [X] patient records (clinical extracts from your system)
Our security status:
✓ Raw conversations: Deleted per 1-hour SLA (0 remaining)
✓ Clinical extracts: Encrypted (AES-256)
✓ Access: RLS enforced; audit logs intact
✓ Exfiltration: No unauthorized downloads detected

Your role: You are CONTROLLER; decide on ANPD + patient notification
Our role: Cooperate with forensics; provide audit logs

Hospital decides: Include these patients in breach notification
```

### T+24h: ANPD Notification (hospital sends)
```
Hospital notifies ANPD with:
- Breach scope (1.2M records)
- Our role (sub-processor)
- Data security status (encrypted extracts, no raw exposure)
```

### T+72h: Patient Notification (hospital sends)
```
Hospital notifies affected patients:
"Your records were accessed in breach of our clinical system.
We use [Your Company] for health chat. They report: data was encrypted;
no unauthorized access on their system."
```

---

## Common Response Timelines

| Event | Detection | Hospital | ANPD | Patients |
|-------|-----------|----------|------|----------|
| Unauthorized access | 12h | 2h | 3 days | 72h |
| Exposure | 12h | 1h | 3 days | 72h |
| Deletion failed | 24h | 6h | Optional | Optional |
| System down | Real-time | 30min | Optional | Optional |
| Third-party | 24h | 6h | Hospital decides | Hospital decides |

---

## Escalation Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-call | [Rotate] | [Emergency] | on-call@company |
| CISO | [Name] | [Phone] | ciso@company |
| DPO | [Name] | [Phone] | dpo@company |
| Hospital DPO | [Name] | [Phone] | dpo@hospital.br |

---

**Status:** ACTIVE (enforced quarterly in tabletop exercises)
**Last review:** 2026-03-28
**Next tabletop:** 2026-06-28

This playbook is binding. All scenarios must be executable within documented timelines.
