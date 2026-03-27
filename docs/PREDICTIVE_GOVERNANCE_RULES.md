# Predictive Governance Rules — Prevent Issues Before They Happen

> **Objective:** Use Rho Health Score + system telemetry to predict and alert on ETL failures, service downtimes, infrastructure drift before they impact production.
> **Implemented:** 2026-03-27
> **Review Cycle:** Weekly (Rho calculator runs Sundays 00:00 UTC)

---

## Problem: ETL Stuck (Case Study)

**Incident:** bracc-etl.service inactive for 19 days (2026-03-08 → 2026-03-27)

**What failed to trigger:**
- ❌ No monitoring on service status (`systemctl is-active bracc-etl.service`)
- ❌ No alerting on ETL progress stale (>24h without timestamp update)
- ❌ No pre-commit check for `run_id` parameter in Neo4j queries
- ❌ No Rho health check on br-acc repo (would show "CRITICAL" due to inactive service)

**Solution:** Create predictive rules that trigger **before** the incident.

---

## Rule Set: System Health Monitoring

### Rule 1: Service Health Tracking

**Metric:** `systemctl is-active <service>`

**Trigger condition:**
```
service_status = INACTIVE || FAILED
age_since_last_activity > 1 hour
```

**Action:**
```
1. Log event: SERVICE_INACTIVE
2. Check: Is this expected? (scheduled maintenance?)
3. If not expected: Send alert (Telegram + email)
4. Create ticket in TASKS.md: BLOCKER-XXX
```

**Implementation (cron job, br-acc):**
```bash
# Run every 30 minutes
*/30 * * * * /opt/bracc/scripts/service-health-check.sh

# service-health-check.sh
#!/bin/bash
SERVICE="bracc-etl.service"
if ! systemctl is-active --quiet $SERVICE; then
  UPTIME=$(systemctl show -p ActiveEnterTimestamp $SERVICE)
  # Send to Telegram + log
  curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=🚨 $SERVICE is INACTIVE. Last active: $UPTIME"
  # Create event for Rho
  echo "$(date +%s) SERVICE_DOWN $SERVICE" >> ~/.egos/health-events.log
fi
```

---

### Rule 2: ETL Progress Staling Detection

**Metric:** `etl-progress.last_update` (from Redis/Supabase)

**Trigger condition:**
```
(now - last_update) > 24 hours
running = false
progress < 100%
```

**Interpretation:**
- ✅ If `running=false` AND `progress=100%` → Normal (completed)
- ✅ If `running=true` AND (now - last_update) < 30min → Processing (OK)
- ❌ If `running=false` AND (now - last_update) > 24h → **STALE** (alert)

**Action:**
```
1. Create alert: ETL_STALE_STATE
2. Check last error log: /opt/bracc/etl/error.log
3. If error contains "ParameterMissing: run_id" → Suggest fix
4. Escalate: Telegram + create BLOCKER task
```

**Implementation (Node.js, br-acc):**
```typescript
// /api/v1/etl/health
async function checkETLHealth() {
  const progress = await redis.get('etl:progress');
  const lastUpdate = new Date(progress.last_update);
  const staleness = (Date.now() - lastUpdate) / 1000 / 3600; // hours

  if (progress.running === false && staleness > 24) {
    await alerting.critical(
      `ETL STALE: Last update ${staleness.toFixed(1)}h ago. Status: ${progress.status}`
    );
    return { status: 'CRITICAL', staleness };
  }
  return { status: 'OK' };
}

// Scheduled: every 1 hour
cron.schedule('0 * * * *', checkETLHealth);
```

---

### Rule 3: Rho Score Drop Detection

**Metric:** Rho health score per repo

**Trigger condition:**
```
(rho_score_today - rho_score_yesterday) < -15 points (>15% drop)
status becomes CRITICAL or EXTREME
```

**Interpretation:**
- 📊 Rho tracks: commit frequency, contributor diversity, file concentration, bus factor
- 📉 Drop > 15% typically indicates:
  - All commits now by 1 person (bus factor ↓)
  - Core contributors inactive (diversity ↓)
  - Major refactor concentrating code (authority ↓)
  - **OR** service outage preventing commits

**Action:**
```
1. Alert: RHO_SCORE_DROP_CRITICAL
2. Investigate: Check git log, service status, CI/CD status
3. Create ticket: INVESTIGATE-RHO-DROP
4. If persistent: Schedule all-hands review
```

**Implementation (cron, egos-lab):**
```typescript
// scripts/rho-watcher.ts
async function monitorRhoScores() {
  const repos = ['egos', 'br-acc', '852', 'forja', 'carteira-livre'];

  for (const repo of repos) {
    const today = await rho.calculate(repo, 1); // last 1 day
    const yesterday = await redis.get(`rho:${repo}:yesterday`);

    if (!yesterday) {
      await redis.set(`rho:${repo}:yesterday`, today);
      continue;
    }

    const drop = today.score - yesterday.score;
    if (drop < -15) {
      await alerting.warning(
        `Rho drop in ${repo}: ${yesterday.score} → ${today.score} (-${Math.abs(drop)}pts)`
      );
    }
  }

  // Store for tomorrow
  await redis.set(`rho:${repo}:yesterday`, today);
}

// Run: Weekly (Sundays after rho_calculator)
cron.schedule('0 1 * * 0', monitorRhoScores);
```

---

### Rule 4: Dependency Vulnerability Prediction

**Metric:** CVE score + package age

**Trigger condition:**
```
CVE_CVSS >= 7.0 (HIGH or CRITICAL)
package_age > 6 months
no_update_available = false
```

**Action:**
```
1. Auto-create PR: deps: update vulnerable package
2. Run test suite on PR
3. If tests pass: Auto-merge (with audit trail)
4. If tests fail: Notify + require manual review
```

**Implementation:** Existing (dependabot) — enhance with Rho checks.

---

## Dissemination & Activation

### 1. Deploy to all repos
```bash
# Copy predictive rules to leaf repos
cp /home/enio/egos/docs/PREDICTIVE_GOVERNANCE_RULES.md \
   /home/enio/{852,forja,carteira-livre,br-acc,santiago}/docs/

# Register rules in .egos/governance
bun governance:disseminate
```

### 2. Activate cron jobs
```bash
# In br-acc, on Contabo → Hetzner VPS
systemctl --user enable bracc-health-monitor.service
systemctl --user enable bracc-etl-staleness-check.service

# In egos-lab, on any machine
cron.schedule('0 1 * * 0', monitorRhoScores); // Weekly
```

### 3. Alerting Channels
- **Telegram:** @EGOSin_bot + EGOS admin chat
- **Email:** enioxt@gmail.com (for CRITICAL alerts)
- **Logs:** ~/.egos/health-events.log (persistent)
- **Dashboard:** `/admin/health` page (inteligencia.egos.ia.br)

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Mean Time to Detection (MTTD)** | <1h after issue | >19 days (ETL case) ❌ |
| **Mean Time to Resolution (MTTR)** | <2h after detection | 0 (no detection) ❌ |
| **False Positive Rate** | <5% | TBD |
| **Service Uptime** | >99.5% | >99% (19-day gap) |

---

## Future Enhancements

- [ ] ML-based anomaly detection (if pattern is unusual, alert)
- [ ] Capacity forecasting (predict when we'll hit resource limits)
- [ ] Dependency security scoring (beyond CVE alone)
- [ ] Team velocity tracking (predict sprint burndown)
- [ ] Cross-repo impact analysis (if API changes, what breaks?)
