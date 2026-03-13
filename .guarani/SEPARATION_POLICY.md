# SEPARATION POLICY — EGOS Ecosystem
# VERSION 1.0.0 — Created 2026-03-06
# APPLIES TO: ALL agents, bots, workflows, dissemination scripts

> **This is a CONSTITUTIONAL document.** All agents, bots, and automated systems
> MUST enforce these rules. Violations are BLOCKING — stop and ask the user.

---

## 1. Repository Visibility Classification

| Repo | Visibility | Public Channels? | Notes |
|------|-----------|-----------------|-------|
| **egos-lab** | PUBLIC | ✅ Yes | Safe to mention anywhere |
| **EGOS-Inteligencia** (br-acc) | PUBLIC | ✅ Yes | Safe to mention anywhere |
| **carteira-livre** | PRIVATE | ❌ NEVER | Code not public, business-sensitive |
| **FORJA** | PRIVATE | ❌ NEVER | Client-specific, business-sensitive |
| **DHPP** | PRIVATE | ❌ NEVER | Police data, SIGILOSO |

## 2. Channel Classification

| Channel | Type | Audience | What CAN be posted |
|---------|------|----------|-------------------|
| **t.me/ethikin** | PUBLIC | Community | egos-lab, EGOS Inteligência, $ETHIK, consciousness tools |
| **Discord EGOS** | PUBLIC | Community | egos-lab, EGOS Inteligência, $ETHIK, consciousness tools |
| **@EGOSin_bot** | PUBLIC | Anyone | egos-lab ecosystem, EGOS Inteligência, public data |
| **egos.ia.br** | PUBLIC | Anyone | All public projects only |
| **GitHub Issues** | PUBLIC | Devs | Only the repo's own content |

## 3. ABSOLUTE PROHIBITIONS

### 3.1 Private Repos on Public Channels
```
❌ NEVER mention Carteira Livre on Telegram/Discord/Twitter
❌ NEVER mention Forja on Telegram/Discord/Twitter
❌ NEVER mention DHPP on ANY public channel
❌ NEVER post code snippets from private repos publicly
❌ NEVER share Carteira Livre URLs in public posts
❌ NEVER share Forja URLs in public posts
```

### 3.2 Personal Information
```
❌ NEVER post about politics, political opinions, or political affiliations
❌ NEVER post about personal stories, family, relationships
❌ NEVER post CVs, resumes, or career details
❌ NEVER post about health, finances, or personal legal matters
❌ NEVER post CPFs, personal emails, phone numbers, addresses
❌ NEVER post client names or client business details (e.g. Rocha Implementos)
```

### 3.3 Police / Investigation Data
```
❌ NEVER post investigation details on ANY channel
❌ NEVER mention case numbers, victim names, suspect names
❌ NEVER mention OVM content, even summarized
❌ NEVER reference DHPP workspace existence publicly
```

## 4. WHAT CAN BE POSTED PUBLICLY

### On Telegram (@ethikin) and Discord
- EGOS Inteligência features and updates (Neo4j stats, new tools, ETL progress)
- egos.ia.br updates (consciousness tools, calculators, new pages)
- $ETHIK token news
- Sacred Mathematics concepts
- Open-source contribution opportunities (egos-lab GitHub issues)
- General AI/tech/ethics discussions
- RHO decentralization scores (public repos only)

### On Twitter (@anoineim)
- Same as Telegram/Discord above
- Links to egos.ia.br and inteligencia.egos.ia.br
- Open-source milestones (stars, forks, contributors)

## 5. ENFORCEMENT IN CODE

### Bot System Prompts
Every bot (Telegram, Discord) MUST include in its system prompt:
```
SEPARATION RULES (MANDATORY):
- You represent the EGOS open-source ecosystem ONLY.
- You must NEVER mention: Carteira Livre, Forja, DHPP, or any private project.
- You must NEVER discuss: politics, personal life, CVs, client details.
- If asked about private projects, respond: "I can only discuss the EGOS
  open-source ecosystem. Visit egos.ia.br for more information."
```

### Dissemination Scripts
The `disseminator` and `ambient_disseminator` agents MUST:
1. Check content against this policy BEFORE posting
2. Filter out any mention of private repos
3. Filter out any personal/political content
4. Log all posts for audit

### Pre-commit Hook
Add to `scripts/disseminate.ts`:
```
SEPARATION_CHECK: Verify no private repo names appear in public-facing content
```

## 6. EXCEPTIONS

Only the USER (Enio) can authorize exceptions, and they must be:
- Explicit (written in chat)
- Specific (which content, which channel)
- Temporary (with expiry)

No agent, bot, or automated system can override this policy.

---

*"Separation is not secrecy — it's respect for boundaries."*
