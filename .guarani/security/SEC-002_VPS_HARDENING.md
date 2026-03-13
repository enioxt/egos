# SEC-002: VPS Hardening Policy

> **STATUS:** ACTIVE | **DATE:** 2026-03-08
> **APPLIES TO:** Contabo VPS (217.216.95.126)
> **PRIORITY:** P0 — CRITICAL

---

## Mandates

1. **SSH Key-Only** — Password authentication MUST be disabled. Ed25519 keys only.
2. **Non-Standard Port** — SSH on port 2244, not 22.
3. **UFW Firewall** — Default deny incoming. Explicit allowlist only.
4. **fail2ban** — Active on SSH, Neo4j, and any exposed API.
5. **WireGuard VPN** — Internal services (Neo4j, Redis) accessible only via VPN.
6. **No Root Login** — `PermitRootLogin prohibit-password` minimum.
7. **Secrets Encrypted** — All `.env` files encrypted with SOPS + age. Never plaintext in repos.
8. **Credential Rotation** — VPS password every 90 days. API keys every 180 days.
9. **Audit Logging** — All SSH logins logged. `auditd` active.
10. **Automated Updates** — `unattended-upgrades` for security patches.

## Checklist (Run Monthly)

- [ ] `sudo ufw status verbose` — verify rules
- [ ] `sudo fail2ban-client status sshd` — check bans
- [ ] `sudo wg show` — verify VPN peers
- [ ] `last -20` — review recent logins
- [ ] `sudo journalctl -u sshd --since "30 days ago" | grep "Failed"` — brute force attempts
- [ ] Verify `.env` NOT in `git ls-files --cached`
- [ ] Check credential rotation dates

## Emergency Procedures

If compromise suspected:
1. `sudo ufw deny incoming` — block all traffic immediately
2. `sudo systemctl stop sshd` — stop SSH (use Contabo VNC console)
3. Review `/var/log/auth.log` for unauthorized access
4. Rotate ALL credentials
5. Restore from backup if data integrity questionable

---

*Full plan: `docs/plans/SECURITY_AND_DECENTRALIZATION_PLAN.md`*
