# EGOS-002: Universal Activation Flow — Platform-Specific Integration

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** activation contract across platforms and channels
- **Summary:** Canonical EGOS activation flow (auth, scopes, token lifecycle, troubleshooting) for ChatGPT/Codex/Claude/GitHub/mobile/custom surfaces.
- **Read next:**
  - `docs/SSOT_REGISTRY.md` — ownership and freshness contracts
  - `docs/CAPABILITY_REGISTRY.md` — capability adoption matrix
  - `TASKS.md` — open execution priorities
<!-- llmrefs:end -->

**Date:** 2026-03-28  
**Status:** Complete  
**Baseline:** All 5 platforms documented with code examples, environment setup, and troubleshooting

---

## Overview

This document defines how to activate EGOS rules and request resources from any tool or platform. The Universal Activation Layer provides:

- **Unified authentication** across ChatGPT, Codex, Claude Code, GitHub Actions, mobile apps, and custom integrations
- **Scoped permissions** ensuring each tool can only access what it needs
- **Audit trails** for compliance and debugging
- **Token management** with expiration and refresh policies

## Activation Endpoint

**Base URL (Production):** `https://egos-api.vercel.app`  
**Endpoint:** `POST /auth/activate`  
**Response Time:** <200ms (p99)  
**Rate Limit:** 100 req/min per token

### Request Schema

```json
{
  "source": "chatgpt",
  "token": "sk-...",
  "userId": "user_123",
  "action": "read",
  "resource": "egos:rules",
  "context": {
    "sessionId": "sess_xyz",
    "userAgent": "ChatGPT/2026"
  }
}
```

### Response Schema

```json
{
  "authorized": true,
  "reasoning": "ChatGPT has read-only scope",
  "scope": "read",
  "auditId": "audit_550e8400-e29b-41d4-a716-446655440000",
  "context": {
    "userId": "chatgpt-user-123",
    "source": "chatgpt",
    "scopes": ["read"],
    "expiresAt": "2026-03-29T15:30:00.000Z"
  }
}
```

### Error Response

```json
{
  "authorized": false,
  "reasoning": "No token provided for action: execute",
  "scope": "none",
  "auditId": "audit_550e8400-e29b-41d4-a716-446655440001",
  "context": {}
}
```

---

## Platform Integration Flows

### 1. ChatGPT Plugin/Action

**Scope:** Read-only access to EGOS rules and docs

#### Setup (Admin)

1. Create API key in EGOS dashboard
   ```bash
   curl -X POST https://egos-api.vercel.app/admin/api-keys \
     -H "Authorization: Bearer $EGOS_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "ChatGPT", "source": "chatgpt", "scopes": ["read"]}'
   ```

2. Store returned key securely in OpenAI platform

#### Code Example (ChatGPT Plugin)

```python
# In OpenAI plugin manifest
{
  "auth": {
    "type": "oauth",
    "client_id": "chatgpt_oauth_client_id",
    "authorization_url": "https://egos-api.vercel.app/oauth/authorize"
  }
}
```

```python
# In plugin handler
import requests

def get_egos_rules(query: str) -> dict:
    # Get ChatGPT session token from context
    token = get_openai_session_token()
    
    # Activate with EGOS
    response = requests.post(
        "https://egos-api.vercel.app/auth/activate",
        json={
            "source": "chatgpt",
            "token": token,
            "action": "read",
            "resource": "egos:rules",
            "context": {
                "query": query,
                "sessionId": get_session_id()
            }
        },
        timeout=2
    )
    
    if response.status_code == 200:
        auth = response.json()
        if auth["authorized"]:
            # Fetch rules with audit trail
            rules_response = requests.get(
                "https://egos-api.vercel.app/rules",
                headers={"X-Audit-ID": auth["auditId"]},
                timeout=5
            )
            return rules_response.json()
    
    return {"error": "Not authorized"}
```

#### Environment Variables

```bash
CHATGPT_EGOS_API_KEY=sk-egos-chatgpt-xxx
EGOS_ACTIVATION_URL=https://egos-api.vercel.app/auth/activate
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Check token is valid. Renew if expired (>24h). |
| `403 Forbidden` | ChatGPT is read-only. Cannot write/execute. |
| Timeout (>5s) | Check network. Use cached responses. |
| Invalid JSON | Ensure `source`, `action`, `resource` present. |

---

### 2. Codex (VS Code Extension)

**Scope:** Read-only access to codebase patterns and rules

#### Setup (User)

1. Generate GitHub API token with read-only access
   ```bash
   # In GitHub Settings > Developer Settings > Personal Access Tokens
   # Scopes: repo:read_only, public_repo
   ```

2. Set environment variable
   ```bash
   export EGOS_CODEX_TOKEN=github_pat_xxxxx
   export EGOS_ACTIVATION_URL=https://egos-api.vercel.app/auth/activate
   ```

3. Install Codex extension + EGOS integration

#### Code Example (VS Code Extension)

```typescript
// In VS Code extension
import axios from 'axios';

async function activateWithEGOS(): Promise<{ authorized: boolean, scope: string }> {
  const token = process.env.EGOS_CODEX_TOKEN;
  const activationUrl = process.env.EGOS_ACTIVATION_URL;
  
  const response = await axios.post(activationUrl, {
    source: 'codex',
    token,
    userId: vscode.env.machineId,
    action: 'read',
    resource: 'egos:rules',
    context: {
      workspaceFolder: vscode.workspace.workspaceFolders?.[0].uri.fsPath,
      vscodeVersion: vscode.version
    }
  });
  
  return {
    authorized: response.data.authorized,
    scope: response.data.scope
  };
}

// Use in Codex inline completion
async function getCompletionContext() {
  const auth = await activateWithEGOS();
  
  if (auth.authorized && auth.scope.includes('read')) {
    const rules = await fetchEGOSRules();
    return { rules, authToken: auth.auditId };
  }
  
  return { rules: [], authToken: null };
}
```

#### Environment Variables

```bash
# ~/.bashrc or ~/.zshrc
export EGOS_CODEX_TOKEN=github_pat_xxxxx
export EGOS_ACTIVATION_URL=https://egos-api.vercel.app/auth/activate
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| `404 Not Found` | Verify endpoint URL in environment. |
| Token not found | Check `EGOS_CODEX_TOKEN` is set. |
| Rate limited | Wait 60 seconds. Requests cached for 5 min. |

---

### 3. Claude Code / Local IDE

**Scope:** Full read/write/execute access (trusted execution)

#### Setup (Developer)

1. Install EGOS CLI
   ```bash
   npm install -g @egos/cli
   ```

2. Authenticate locally
   ```bash
   egos login
   # Prompts for local identity confirmation (no server login needed)
   ```

3. Set workspace config
   ```bash
   egos config init
   # Creates .egos/config.json in project root
   ```

#### .egos/config.json

```json
{
  "source": "local-ide",
  "userId": "local-dev",
  "scopes": ["*"],
  "activationUrl": "http://localhost:3333/auth/activate",
  "trustLevel": "full",
  "auditEnabled": true,
  "auditPath": ".egos/audit.log"
}
```

#### Code Example (Claude Code)

```typescript
// In Claude Code agent
import { EgosClient } from '@egos/client';

const egos = new EgosClient({
  source: 'claude-code',
  config: require('.egos/config.json')
});

// Activate for a task
const activation = await egos.activate({
  action: 'execute',
  resource: 'scripts:build',
  context: { target: 'production' }
});

if (activation.authorized) {
  console.log("Building for production...");
  // Run build script with full access
  await execScript('scripts/build.sh', { 
    auditId: activation.auditId 
  });
} else {
  console.error(`Not authorized: ${activation.reasoning}`);
}
```

#### Environment Variables

```bash
# .env or .env.local
EGOS_SOURCE=local-ide
EGOS_ACTIVATION_URL=http://localhost:3333/auth/activate
EGOS_AUDIT_ENABLED=true
EGOS_AUDIT_PATH=.egos/audit.log
```

#### Local Development Server

```bash
# Start local activation server for testing
npm run egos:dev

# Output:
# EGOS activation server running on http://localhost:3333
# Audit logging: console
# Policies: default
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| `ECONNREFUSED` on localhost | Ensure server running: `npm run egos:dev` |
| `Unauthorized` | Run `egos login` again. Session expired. |
| Audit not recorded | Check `.egos/audit.log` permissions. |

---

### 4. GitHub Actions

**Scope:** Full access (CI/CD trusted context)

#### Setup (Repository)

1. No setup required! GitHub Actions has built-in EGOS integration.

2. Use default token in workflow
   ```yaml
   env:
     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     EGOS_ACTIVATION_URL: https://egos-api.vercel.app/auth/activate
   ```

#### Code Example (GitHub Action)

```yaml
# .github/workflows/deploy.yml
name: Deploy with EGOS Activation

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Activate EGOS for Deployment
        run: |
          ACTIVATION=$(curl -s -X POST \
            ${{ env.EGOS_ACTIVATION_URL }} \
            -H "Content-Type: application/json" \
            -d '{
              "source": "github-actions",
              "token": "${{ secrets.GITHUB_TOKEN }}",
              "action": "deploy",
              "resource": "vercel:production"
            }')
          
          AUTHORIZED=$(echo $ACTIVATION | jq '.authorized')
          AUDIT_ID=$(echo $ACTIVATION | jq -r '.auditId')
          
          if [ "$AUTHORIZED" = "true" ]; then
            echo "Deploying with audit ID: $AUDIT_ID"
            vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
          else
            echo "Deployment not authorized"
            exit 1
          fi
      
      - name: Verify Deployment
        run: |
          curl -s https://egos-api.vercel.app/audit/$AUDIT_ID \
            | jq '.result' | grep -q "allowed" || exit 1
```

#### Environment Variables

```yaml
# No secrets needed! Uses GitHub's built-in GITHUB_TOKEN
env:
  EGOS_ACTIVATION_URL: https://egos-api.vercel.app/auth/activate
  EGOS_SOURCE: github-actions
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| `401` on activation | Verify `GITHUB_TOKEN` is available in workflow. |
| Deployment blocked | Check `egos:rules` for deployment restrictions. |
| Rate limit hit | GitHub Actions cached (5 min). Retry after. |

---

### 5. Mobile / Custom Integrations

**Scope:** Configurable based on token

#### Setup (Mobile App)

1. Initialize SDK
   ```swift
   import EgosSDK
   
   let egos = EgosClient(
     activationUrl: "https://egos-api.vercel.app/auth/activate",
     source: "mobile-app",
     apiKey: "egos_mobile_xxx"
   )
   ```

2. Request activation before sensitive operations
   ```swift
   do {
     let auth = try await egos.activate(
       action: .read,
       resource: "egos:rules",
       context: ["device": UIDevice.current.model]
     )
     
     if auth.authorized {
       // Fetch and cache rules
       let rules = try await fetchEGOSRules(auditId: auth.auditId)
       userDefaults.set(rules, forKey: "egos-rules")
     }
   } catch {
     print("Activation failed: \(error)")
   }
   ```

#### Code Example (Custom Backend)

```python
# FastAPI example
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

EGOS_API_KEY = "sk-egos-custom-xxx"
EGOS_ACTIVATION_URL = "https://egos-api.vercel.app/auth/activate"

@app.post("/api/protected-action")
async def protected_action(request: dict):
    """Custom endpoint that requires EGOS activation"""
    
    # Activate with EGOS
    async with httpx.AsyncClient() as client:
        response = await client.post(
            EGOS_ACTIVATION_URL,
            json={
                "source": "custom-api",
                "token": EGOS_API_KEY,
                "userId": request.get("user_id"),
                "action": "write",
                "resource": "project:852"
            },
            timeout=2.0
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    auth = response.json()
    
    if not auth["authorized"]:
        raise HTTPException(status_code=403, detail=auth["reasoning"])
    
    # Execute action with audit trail
    result = await perform_action(request, auditId=auth["auditId"])
    return result
```

#### Environment Variables

```bash
# .env for mobile backend
EGOS_ACTIVATION_URL=https://egos-api.vercel.app/auth/activate
EGOS_API_KEY=sk-egos-custom-xxx
EGOS_SOURCE=custom-api
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| Network timeout | Increase timeout to 5s. Check internet. |
| CORS blocked | Endpoint supports CORS. Check browser console. |
| Invalid API key | Regenerate in EGOS dashboard. |

---

## Common Patterns

### Pattern 1: Token Caching + Expiration

```typescript
class EgosTokenCache {
  private cache: Map<string, { token: string, expiresAt: Date }> = new Map();
  
  async getToken(source: string): Promise<string> {
    const cached = this.cache.get(source);
    
    if (cached && cached.expiresAt > new Date()) {
      return cached.token;
    }
    
    // Refresh token
    const newToken = await requestNewToken(source);
    this.cache.set(source, {
      token: newToken,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24h
    });
    
    return newToken;
  }
}
```

### Pattern 2: Fallback to Degraded Mode

```typescript
async function readRulesWithFallback(): Promise<Rules> {
  try {
    // Try to activate
    const auth = await egos.activate({ action: 'read', resource: 'egos:rules' });
    
    if (auth.authorized) {
      return await fetchFreshRules(auth.auditId);
    }
  } catch (error) {
    console.warn("EGOS activation failed:", error);
  }
  
  // Fallback: return cached rules
  return getCachedRules() || getDefaultRules();
}
```

### Pattern 3: Audit Trail Integration

```typescript
class AuditIntegration {
  async logAction(action: string, resource: string, auditId: string) {
    // Retrieve audit entry from EGOS
    const auditEntry = await fetch(
      `https://egos-api.vercel.app/audit/${auditId}`
    ).then(r => r.json());
    
    // Log to your system
    await database.auditLog.insert({
      timestamp: new Date(),
      userId: auditEntry.identity.userId,
      action,
      resource,
      authorized: auditEntry.result === 'allowed',
      egosAuditId: auditId,
      source: auditEntry.identity.source
    });
  }
}
```

---

## Performance & Reliability

### Activation Latency (Target)

| Platform | p50 | p95 | p99 |
|----------|-----|-----|-----|
| ChatGPT | 80ms | 150ms | 200ms |
| Codex | 50ms | 100ms | 150ms |
| Claude Code (local) | 10ms | 20ms | 50ms |
| GitHub Actions | 100ms | 200ms | 300ms |
| Mobile | 150ms | 300ms | 500ms |

### Caching Strategy

- **Token validation:** Cache for 5 minutes (reduces API calls 95%)
- **Policy rules:** Cache for 1 hour (rules rarely change)
- **Audit IDs:** No caching (write-only)

### Retry Policy

```json
{
  "maxRetries": 3,
  "backoff": "exponential",
  "delays": [100, 500, 2000],
  "retryOn": [408, 429, 500, 502, 503, 504]
}
```

---

## Security Best Practices

1. **Never hardcode tokens.** Use environment variables or secure vaults.
2. **Validate audit IDs** before trusting a response.
3. **Rotate tokens quarterly** (automated via CI/CD).
4. **Monitor failed activations** — may indicate compromise.
5. **Use HTTPS only** — never HTTP (except localhost).

---

## Monitoring & Debugging

### Enable Verbose Logging

```bash
export EGOS_DEBUG=true
export EGOS_LOG_LEVEL=debug
```

### Query Audit Trail

```bash
curl -X GET "https://egos-api.vercel.app/audit?userId=user_123&limit=20" \
  -H "Authorization: Bearer $EGOS_ADMIN_TOKEN"
```

### Health Check

```bash
curl https://egos-api.vercel.app/health
# Response: { "status": "ok", "version": "2.0.0", "uptime": "99.99%" }
```

---

## FAQ

**Q: Can I use local activation without the server?**  
A: Yes! Set `EGOS_ACTIVATION_URL=http://localhost:3333` and run `npm run egos:dev`.

**Q: What happens if the activation endpoint is down?**  
A: Most integrations use 5-minute caching. Requests within cache window proceed. After cache expiry, fallback to degraded mode or deny.

**Q: How do I request higher scopes?**  
A: Only admins can grant scopes. Submit request via EGOS dashboard or contact governance team.

**Q: Are activation logs retained forever?**  
A: No. Retention: 90 days for operational logs, 5 years for breach evidence.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-03-28 | Universal activation framework + 5 platform flows |
| 1.0.0 | 2026-03-01 | Initial activation endpoint |

---

## Support

- **Docs:** https://egos.dev/docs/activation
- **Issues:** https://github.com/enioxt/egos/issues
- **Slack:** #egos-activation (enioxt workspace)
