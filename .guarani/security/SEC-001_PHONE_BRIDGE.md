# SEC-001: Phone Bridge Security Policy

> **Status:** ENFORCED | **Created:** 2026-03-07
> **Scope:** egos-self, egos-lab, any project touching phone↔desktop communication

---

## Policy

**The phone is an air-gapped 2FA security layer. No bridge to desktop until a secure channel spec is approved.**

## Threat Model

| Vector | Risk | Impact |
|--------|------|--------|
| Notification mirroring | 2FA push codes visible on desktop | **2FA defeated** |
| Clipboard sync | Copied 2FA codes leak to desktop | **2FA defeated** |
| SMS integration | Desktop reads SMS with auth codes | **2FA defeated** |
| Remote input | Desktop sends taps to phone | Can approve 2FA push remotely |
| File transfer | Bidirectional storage access | Authenticator DB, photos, keys exposed |
| Network discovery | mDNS on local network | MITM if network untrusted |

## What Is Blocked

- KDE Connect pairing with personal phone
- Any egos-self CLI command that bridges to phone
- gem-hunter agent "device-bridge" search track (removed)
- Any code that reads phone notifications, clipboard, or SMS

## Requirements for Future Secure Bridge (SEC-001-FUTURE)

A phone↔desktop bridge may only be re-enabled if ALL of these are met:

1. **Explicit opt-in per data type** — user must approve each: notifications, clipboard, files, SMS, input
2. **No 2FA passthrough** — notifications from authenticator apps are NEVER mirrored
3. **Allowlist-only** — only explicitly named apps can send data across the bridge
4. **End-to-end encryption** — not just transport (TLS), but E2E with keys on device only
5. **Audit log** — every cross-device action is logged locally with timestamp and data type
6. **Kill switch** — one-tap disconnect from phone, no desktop override possible
7. **No persistent connection** — bridge activates only for approved actions, then disconnects
8. **Code review** — security-focused review before any bridge code is merged
9. **Separate device for 2FA** — if bridge is enabled, 2FA should move to a dedicated hardware key (YubiKey)

## Affected Code

- `agents/agents/gem-hunter.ts` — device-bridge track removed
- `apps/egos-web/src/pages/Roadmap.tsx` — egos-self marked as paused
- `apps/egos-self/` — KDE Connect integration exists but phone MUST NOT be paired
- `README.md` — references KDE Connect (acceptable as documentation, not execution)
