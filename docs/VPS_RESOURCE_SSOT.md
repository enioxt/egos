# VPS Resource Management SSOT

**Version:** 1.0.0 | **Date:** 2026-04-07 | **Status:** Active  
**Source:** P34 Investigation (vps_hetzner_complete_infrastructure_map_2026-04-07.md)

---

## Current State (as of 2026-04-07)

### Hardware
- **Server:** Hetzner VPS (204.168.217.125)
- **CPU:** Adequate (0.50 load avg)
- **RAM:** 15GB total / 7.2GB used / **604-620MB free** ⚠️ CRITICAL
- **Disk:** 301GB total / 69GB used / 220GB free ✅

### Containers (19 active)
- **Neo4j BR-ACC:** 4.8GB RAM, 83.7M nodes (production SSOT)
- **Guard Brasil API:** Running
- **Eagle Eye:** Running
- **EGOS HQ:** Running
- **Evolution API:** Running (WhatsApp)
- **+ 14 more:** Database/infrastructure services

### Uptime
- Container uptime: 9 days (stable)
- No OOM crashes reported
- Neo4j healthy (page errors 2026-04-03/04, resolved)

---

## Decisions (P34)

### ✅ Keep BR-ACC Online
- Real production SSOT: 83.7M nodes, live since 2026-03-28
- Data posterior to backups (last backup: 2026-04-05)
- Will NOT restore from backup dumps
- Rationale: Live data is authoritative; backups are safety net only

### ✅ Archive Backup Dumps
- **Action:** Moved `/opt/backups/` → `/opt/backups.archived_20260407` (2026-04-07)
- **Content:** 3x Neo4j dumps (5GB each, dated 2026-04-03/04/05)
- **Safety:** 24-hour observe period before permanent delete
- **Rationale:** Frees ~15GB disk space, reduces memory pressure
- **No cron depends on backups** (verified)

### ✅ RAM Monitoring Required
- **Threshold:** Alert if free_ram < 1GB
- **Current:** 604-620MB free = very tight
- **Action:** Add watchdog alert to `/opt/egos/bin/vps-ram-monitor.sh` (VPS-MEMORY-001)
- **Blocker for Hermes MVP:** Must have >2GB free before deployment

---

## Monitoring Rules

### RAM Alerts (VPS-MEMORY-001)
```
if free_ram < 1GB:
  → Send Telegram alert (immediate)
  
if free_ram < 500MB:
  → Escalate (page on-call)
  
if free_ram < 100MB:
  → Kill non-critical containers (except Neo4j)
```

### Neo4j Monitoring (VPS-NEO4J-TUNE-001)
- Heap allocation: 4.8GB (current)
- Max heap: Audit `dbms.memory.heap.max_size` in neo4j.conf
- Optimization: Possible to reduce page cache if tolerable
- Measure: Compare query latency before/after

### Disk Monitoring
- **Alert if < 50GB free:** May impact temp operations
- **Alert if < 20GB free:** Critical (backups, logs, crash dumps)

---

## Future Capacity Planning (VPS-CAPACITY-001)

### Given: Current 19 containers + Neo4j 4.8GB
- **Available after cleanup:** ~2-4GB additional
- **Hermes MVP requirement:** 600MB
- **Codex proxy:** ~200MB
- **Gemini CLI:** ~100MB
- **Total new:** ~900MB

### Scenarios
- ✅ Cleanup + MVP: Safe (2GB available, using 900MB)
- ⚠️ Without cleanup: Risky (only 620MB available)
- ❌ Without cleanup + full scale (6 profiles): OOM crash likely

### Recommendations
1. Keep cleanup as P0 blocker for Hermes
2. Monitor Neo4j heap tuning (could free 500MB-1GB if optimized)
3. Consider swap partition if heap tuning insufficient (P1)
4. Document swap performance impact (may hurt latency)

---

## Backup Strategy (VPS-BACKUP-002)

### We Use: Live Neo4j (Production SSOT)
- Container data is canonical
- 24/7 persistence (no ephemeral volumes)
- Survives container restart

### Why Not Backups
- 15GB = expensive storage
- Slower recovery (restore dump takes 30min+)
- Not automated restore (manual process)
- Live data > backup for operational use

### Safety Net
- Archived copy: `/opt/backups.archived_20260407` (24h retention)
- If major incident: Can restore within 24h
- After 24h: Safe to delete permanently

### New Strategy
- **Automated backup:** Daily cron (DreamCycle module) → Supabase backup table
- **Retention:** Keep last 7 days in Supabase
- **Emergency restore:** Terraform-based redeploy from Supabase + git

---

## Rollout Checklist

### Phase 1: Cleanup (2026-04-07 ✅)
- [x] Move `/opt/backups/` → `/opt/backups.archived_20260407`
- [ ] Monitor for 24 hours (no issues expected)
- [ ] Permanent delete if clean

### Phase 2: Monitoring (2026-04-08)
- [ ] Add RAM alerting to vps-ram-monitor.sh (VPS-MEMORY-001)
- [ ] Verify alerts work (manual test)
- [ ] Document thresholds in this SSOT

### Phase 3: Hermes MVP (2026-04-08+)
- [ ] Verify >2GB free RAM before deployment
- [ ] Document actual RAM usage post-cleanup
- [ ] Monitor during 1-week trial

### Phase 4: Optimization (P35+)
- [ ] Audit Neo4j heap (VPS-NEO4J-TUNE-001)
- [ ] Build capacity model (VPS-CAPACITY-001)
- [ ] Consider swap if needed (VPS-SWAP-001)

---

## References

- **Investigation:** `/home/enio/.egos/memory/mcp-store/vps_hetzner_complete_infrastructure_map_2026-04-07.md`
- **TASKS:** `TASKS.md` sections VPS Infrastructure, Hermes MVP, VPS Orchestration
- **Handoff:** `docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md` §2

---

*Canonical SSOT for VPS resource management. Update as operational state changes.*
