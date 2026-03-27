# Credentials Policy — Never Expose Secrets

> **Effective:** 2026-03-27 (after X.com key exposure incident)
> **Scope:** All EGOS repos + leaf repos
> **Enforcement:** Pre-commit hooks + gitleaks scanning

---

## Rule 1: Never Commit Credentials

### ❌ DO NOT
```bash
# ❌ WRONG: Exposing in markdown docs
TWITTER_BEARER_TOKEN=AAAAAAAAAA...

# ❌ WRONG: In .env (if .env is committed)
API_KEY=sk-1234567890...

# ❌ WRONG: In code
const secretKey = "xai-JTZQL59hSq33MOrtITlPKhGFXayls8B3c15thEtyteqQi3GCVSnFBXiHV7Lb7iLpE7zbfXNR6Vud6zetG"
```

### ✅ DO
```bash
# ✅ RIGHT: .env.example with placeholders (COMMITTED)
TWITTER_BEARER_TOKEN=<regenerate_from_dashboard>
API_KEY=<get_from_vault>

# ✅ RIGHT: Store actual secrets in ~/.egos/secrets.env (GITIGNORED)
TWITTER_BEARER_TOKEN=AAAAAAAAAA...

# ✅ RIGHT: Reference from code
const secretKey = process.env.XAI_API_KEY;
```

---

## Rule 2: Credential Storage Hierarchy

1. **Local Vault:** `~/.egos/secrets.env` (user's home, never committed)
   - Sourced by: CI/CD pipelines, local dev, Claude Code hooks
   - Format: `KEY=value` (one per line)
   - Rotation: Auto-sync via `/disseminate` when updated

2. **Project .env.local:** `.env.local` (per-repo, gitignored)
   - Project-specific overrides
   - Loaded after vault (can override)
   - Example: `br-acc/.env.local` for Neo4j password

3. **VPS Systemd Env:** `/etc/systemd/system/service.env` (production)
   - Hetzner only, set via `systemctl set-environment`
   - Not in git, managed via infrastructure-as-code

4. **CI/CD Secrets:** GitHub Actions / Vercel secrets dashboard
   - Never echo or log
   - Use `--mask-secrets` flag

---

## Rule 3: Pre-Commit Hook Enforcement

All repos have `pre-commit` hook running `gitleaks`:

```bash
# Automatically scans:
- Private keys (RSA, DSA, EC, PGP)
- API keys (AWS, Azure, GCP, OpenRouter, XAI, X.com, etc.)
- Database passwords
- Tokens (JWT, OAuth, Bearer)
- Wallet/cryptocurrency private keys
- Slack tokens, webhooks

# If detected:
❌ COMMIT BLOCKED: "commit aborted - secrets detected"
✅ FIX: Remove from file, commit to vault, re-commit
```

---

## Rule 4: Audit Log

**Every credentials change logged:**

```
~/.egos/credentials-audit.log

2026-03-27T16:30:00Z REVOKE twitter_consumer_key exposed_in_commit_51f3821
2026-03-27T16:31:00Z REGENERATE twitter_consumer_key via_developer.x.com
2026-03-27T16:32:00Z STORE twitter_consumer_key -> ~/.egos/secrets.env
2026-03-27T16:33:00Z DISSEMINATE twitter_* to br-acc 852 forja
```

---

## Rule 5: Incident Response

**If credentials are exposed:**

1. **IMMEDIATE (< 5 min):**
   - [ ] Revoke at provider dashboard
   - [ ] Remove from git history (git-filter-repo or GitHub secret scanning)
   - [ ] Commit fix (remove plaintext, add placeholder)
   - [ ] Alert team (Telegram)

2. **SHORT-TERM (< 1h):**
   - [ ] Regenerate new credentials
   - [ ] Store in vault
   - [ ] Update .env.example
   - [ ] Disseminate to all repos

3. **LONG-TERM (< 1 day):**
   - [ ] Audit logs (did anyone use old key?)
   - [ ] Review pre-commit hook effectiveness
   - [ ] Update training docs

---

## Exceptions

**None.** There are no acceptable exceptions to this policy.

If you think an exception is needed, escalate to governance (create BLOCKER ticket).

---

## Dissemination

**Copy this policy to all repos:**

```bash
cp CREDENTIALS_POLICY.md /home/enio/{852,forja,br-acc,carteira-livre,santiago,INPI}/docs/
git -C <repo> add docs/CREDENTIALS_POLICY.md
git -C <repo> commit -m "docs: add CREDENTIALS_POLICY.md"
git -C <repo> push
```
