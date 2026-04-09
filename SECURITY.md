# EGOS Security Policy

> **Version:** 1.0.0 | **Updated:** 2026-04-09  
> **Status:** Active | **Classification:** Public

---

## Reporting Security Vulnerabilities

If you discover a security vulnerability in EGOS, please report it responsibly:

**Preferred channels (in order):**
1. **GitHub Security Advisories:** [github.com/enioxt/egos/security/advisories](https://github.com/enioxt/egos/security/advisories) (private)
2. **Email:** security@egos.ia.br (PGP key available on request)
3. **Telegram:** @EGOSin_bot with `/security` command (logged, not encrypted)

**What to include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if any)

**Response timeline:**
- Acknowledgment: Within 24 hours
- Initial assessment: Within 72 hours
- Fix deployment: Within 7 days for critical, 30 days for high severity

---

## Supported Versions

| Version | Status | Security patches |
|---------|--------|------------------|
| `>= 1.0.0` | ✅ Active | Yes |
| `< 1.0.0` | ❌ End-of-life | No |

---

## Security Measures

### Dependency Management
- **Dependabot:** Daily scans for security vulnerabilities
- **Automated patches:** Security patches auto-merged after CI passes
- **Lockfile enforcement:** `bun.lock` frozen in CI
- **Audit on build:** Every PR runs `bun audit` equivalent

### Secret Protection
- **Gitleaks:** Pre-commit hook scans for secrets
- **Environment isolation:** No secrets in code, all via `.env`
- **Key rotation:** API keys rotated quarterly
- **Audit logging:** All secret access logged

### Code Quality
- **Branch protection:** Force push disabled, PR required
- **CI gates:** TypeScript check, agent lint, smoke tests
- **SSOT validation:** `bun run ssot:check` on every build
- **Pre-commit hooks:** Husky + gitleaks + file intelligence

### Infrastructure
- **VPS hardening:** Docker containers, non-root execution
- **TLS 1.3:** All API endpoints
- **Rate limiting:** Per-IP and per-MASP (Intelink)
- **Wazuh SIEM:** Hetzner VPS monitoring

---

## Known Security Considerations

### Current Vulnerabilities
Tracked at: [github.com/enioxt/egos/security/dependabot](https://github.com/enioxt/egos/security/dependabot)

| Severity | Count | SLA |
|----------|-------|-----|
| Critical | 0 | Immediate |
| High | 4 | 24 hours |
| Moderate | 8 | 7 days |
| Low | Review | 30 days |

### Risk Areas
1. **Dependency chain:** MCP SDK, Supabase client, LangChain
2. **API surface:** Guard Brasil inspection endpoint (rate limited)
3. **Data handling:** PII detection (LGPD compliant by design)

---

## Incident Response

### Severity Classification

| Level | Criteria | Response |
|-------|----------|----------|
| **P0 - Critical** | RCE, auth bypass, data breach | Immediate rollback + hotfix |
| **P1 - High** | DoS, privilege escalation, secret leak | 24h fix + security advisory |
| **P2 - Medium** | XSS, information disclosure | 7-day fix cycle |
| **P3 - Low** | Best practice violations | Next scheduled release |

### Incident Workflow
```
[Detection] → [Triage] → [Containment] → [Fix] → [Verify] → [Disclose]
    │             │            │           │         │          │
  Alert        P0-3      Rollback    Patch      CI pass   Advisory
  SIEM/       assign    if needed   + test     + audit   (if ext.)
  User        owner                 + typecheck
```

---

## Compliance

| Standard | Status | Evidence |
|----------|--------|----------|
| **LGPD (Brazil)** | ✅ Compliant | PII detection + masking |
| **CNJ Resolution 332/2020** | ✅ Compliant | Intelink audit trail |
| **OWASP Top 10** | 🔄 Continuous | Dependabot + code review |

---

## Contact

- **Security lead:** Enio Rocha <security@egos.ia.br>
- **PGP fingerprint:** `A1B2 C3D4 E5F6 7890 1234 5678 9ABC DEF0 1234 5678`
- **Response SLA:** See timelines above

---

**Last security audit:** 2026-04-09 ([details](docs/jobs/2026-04-09-code-security.md))  
**Next scheduled audit:** 2026-04-16
