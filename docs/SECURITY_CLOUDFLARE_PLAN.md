# Security & CloudFlare Plan

**Goal:** Protect egos.ia.br and leaf domains (852.egos.ia.br, inteligencia.egos.ia.br, openclaw.egos.ia.br) from DDoS, abuse, and improve latency via edge caching.

**Current state:** Domains point directly to Hetzner IP (204.168.217.125). No CloudFlare protection yet.

---

## Current Architecture

```
Client
  ↓
DNS: egos.ia.br → 204.168.217.125 (Hetzner)
  ↓
Caddy (SSL, reverse proxy) @ 204.168.217.125:80,443
  ├→ inteligencia.egos.ia.br (bracc API+Frontend)
  ├→ 852.egos.ia.br (News aggregator)
  ├→ openclaw.egos.ia.br (Agent gateway WS)
  └→ waha.egos.ia.br (Telegram connector)
```

**Problems:**
- No DDoS protection
- No rate limiting (attackers can hammer endpoints)
- No WAF (Web Application Firewall)
- No geo-blocking or bot detection
- Caddy handles all traffic directly (no edge caching)
- No API abuse protection

---

## CloudFlare Solution (Recommended)

### Step 1: Setup CloudFlare
```bash
1. Go to https://dash.cloudflare.com
2. Add site → egos.ia.br (select Free or Pro plan)
3. CloudFlare will scan DNS records
4. Update nameservers at your domain registrar to:
   - ns1.cloudflare.com
   - ns2.cloudflare.com
5. Wait 24h for propagation
```

### Step 2: Configure DNS Records

| Type | Name | Value | Proxy | TTL |
|------|------|-------|-------|-----|
| A | @ | 204.168.217.125 | :orange: (Proxied) | Auto |
| A | 852 | 204.168.217.125 | :orange: | Auto |
| A | inteligencia | 204.168.217.125 | :orange: | Auto |
| A | openclaw | 204.168.217.125 | :orange: | Auto |
| A | waha | 204.168.217.125 | :orange: | Auto |
| CNAME | www | @ | :orange: | Auto |
| TXT | @ | v=spf1 ... | — | Auto |

**Key:** `:orange:` (Proxied) = traffic goes through CloudFlare edge → cache + protection

### Step 3: Enable Security Features (Free Tier)

#### 🛡️ DDoS Protection
- **Status:** Automatically enabled
- **What it does:** Detects and mitigates L3/L4 DDoS attacks
- **Config:** Dashboard → Security → DDoS

#### 🤖 Bot Management (Free: Basic)
- **Enable:** Dashboard → Security → Bot Management
- **Rules:**
  - Block: Definitely Automated (CAPTCHAs)
  - Challenge: Likely Automated
  - Allow: Verified Bots (Google, Bing, etc.)

#### 🔐 WAF (Web Application Firewall)
- **Free tier:** OWASP ModSecurity rules (limited)
- **Pro plan:** Full WAF + custom rules
- **Enable:** Dashboard → Security → WAF
- **Recommended rules:**
  - OWASP Top 10 Protection
  - Rate Limiting Module

#### 🚫 Rate Limiting (Paid, but doable with Workers)
```
Free: Use Caddy rate-limiter (local)
Paid: CloudFlare rate limiting rules
```

#### 🌍 Geo-IP Blocking (Optional)
- **Dashboard:** Security → Geo-IP
- **Use case:** Block specific countries if needed
- **Example:** Block countries with high attack rates

#### 🔒 SSL/TLS
- **Mode:** Full (strict) — requires valid cert on origin
- **Current:** Caddy already has valid certs ✅
- **Enable:** Dashboard → SSL/TLS → Full
- **Minimum TLS version:** 1.2

#### 🎯 Page Rules (Free: 3 rules)
```
Rule 1: inteligencia.egos.ia.br/api/*
  - Cache Level: Bypass
  - Browser TTL: 0
  (no caching for API)

Rule 2: 852.egos.ia.br/static/*
  - Cache Level: Cache Everything
  - Browser TTL: 30 days
  (cache static assets)

Rule 3: openclaw.egos.ia.br/ws
  - Web Sockets: On
  (enable WebSocket passthrough)
```

---

## Caddy-Level Protection (On-Origin)

Even with CloudFlare, Caddy should defend itself.

### Rate Limiting in Caddy

```caddyfile
# File: /opt/bracc/infra/Caddyfile

(rate_limit_api) {
    rate {
        zone api
        100/m         # 100 requests per minute
        key {remote_host}
    }
}

(rate_limit_tight) {
    rate {
        zone auth
        10/m          # 10 requests per minute (login, register)
        key {remote_host}
    }
}

inteligencia.egos.ia.br {
    handle /api/* {
        import rate_limit_api
        reverse_proxy api:8000
    }
    handle /auth/* {
        import rate_limit_tight
        reverse_proxy api:8000
    }
}
```

### Security Headers (Caddy)

Already in place:
```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### Additional Headers to Add
```
header {
    Content-Security-Policy "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.openrouter.ai https://dashscope.aliyun.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    X-Permitted-Cross-Domain-Policies "none"
    Permissions-Policy "accelerometer=(), ambient-light-sensor=(), autoplay=(), camera=(), cross-origin-isolated=(), display-capture=(), encrypted-media=(), fullscreen=(self), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), speaker-selection=(), sync-xhr=(), usb=(), xr-spatial-tracking=()"
}
```

---

## Latency Optimization

### CloudFlare Edge Caching
- **Static assets:** Cache everything (30 days TTL)
- **API responses:** Cache-Control headers from origin
- **Dynamic content:** Bypass cache, use edge compression

### Hetzner Location
- **Current:** Hetzner Nuremberg, Germany (fsn1)
- **Latency to Brazil:** ~140ms (acceptable)
- **Latency via CloudFlare edge:** ~50-80ms (improvement via cache)

### Caddy Compression
```caddyfile
# Already enabled in Caddy, but verify:
encode gzip {
    level 5  # Balance: speed vs compression
}
encode brotli {
    level 5
}
```

### Image Optimization (CloudFlare Paid)
- **Free:** Polish (lossless optimization)
- **Paid:** Adaptive images, WebP conversion

---

## Monitoring & Alerts

### CloudFlare Analytics
- **Dashboard:** Insights → Analytics
- **Metrics:**
  - Requests: total, by country, by status
  - Threats: blocked by WAF, rate limit, bot
  - Cache ratio: % of traffic served from edge
  - Performance: response time, SSL handshake

### Alerts to Setup
```
1. DDoS attack detected (> 1000 req/sec)
2. WAF block rate > 5%
3. Origin error rate > 2%
4. TLS cert expiring in 30 days
```

### Caddy Logs
```bash
# Already logging via Caddy
# View real-time:
ssh root@204.168.217.125
docker logs infra-caddy-1 -f --tail=50
```

---

## Implementation Checklist

### Phase 1: CloudFlare Setup (1 day)
- [ ] Sign up for CloudFlare account
- [ ] Add egos.ia.br as new site
- [ ] Update nameservers at registrar
- [ ] Wait for DNS propagation (24h)
- [ ] Verify DNS records in CloudFlare dashboard

### Phase 2: Security Config (2h)
- [ ] Enable DDoS protection
- [ ] Configure Bot Management rules
- [ ] Set WAF rules (OWASP Top 10)
- [ ] Enable SSL/TLS (Full Strict)
- [ ] Create 3 Page Rules (API bypass, static cache, WebSocket)

### Phase 3: Caddy Hardening (1h)
- [ ] Add rate limiting rules for /api/* (100/min)
- [ ] Add strict rate limiting for /auth/* (10/min)
- [ ] Add CSP + security headers
- [ ] Test with `ab` or `wrk` load testing

### Phase 4: Monitor (ongoing)
- [ ] Check CloudFlare analytics daily (first week)
- [ ] Review WAF blocks weekly
- [ ] Monitor cache ratio (target: >50% static)
- [ ] Test latency from Brazil with `mtr egos.ia.br`

---

## Expected Improvements

| Metric | Before | After | Gain |
|--------|--------|-------|------|
| DDoS protection | None | Full | Attacks blocked at edge |
| Bot filtering | None | ~20% of traffic | Stops scrapers, attacks |
| Rate limiting | None | Per-endpoint | Prevents API abuse |
| Cache ratio | 0% | ~40-60% | Faster responses |
| Latency (Brazil) | ~140ms | ~60-80ms | 40-50% faster |
| SSL grade | A | A+ | Better handshake |

---

## Notes
- **Free vs Pro:** Free plan is sufficient to start (DDoS, basic WAF, DNS management)
- **Cost:** ~$20/month Pro plan (worth it for rate limiting + advanced WAF)
- **Migration:** Zero downtime when switching nameservers
- **Rollback:** Can revert to direct IP in 5min if needed
