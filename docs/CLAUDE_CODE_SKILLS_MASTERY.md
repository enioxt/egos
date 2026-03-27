# Claude Code Skills Mastery Guide

> **Updated:** 2026-03-27 (Research: Exa + Reddit + GitHub)
> **Goal:** Use all available skills automatically + discover new ones
> **Framework:** Agent Orcha, VoltAgent, GitHub Agentic Workflows

---

## Available Skills in Claude Code

### Built-in Skills (Always Available)

| Skill | Syntax | Use Case |
|-------|--------|----------|
| `/commit` | `/commit "message"` | Git commits with auto-formatting |
| `/pr` | `/pr create --title "PR Title"` | Create pull requests + test validation |
| `/help` | `/help` | Documentation + troubleshooting |
| `/model` | `/model sonnet` | Switch LLM model |
| `/fast` | `/fast` | Toggle fast mode (faster output) |
| `/disseminate` | `/disseminate` | Sync governance to leaf repos |
| `/end` | `/end` | Session handoff + handoff docs |
| `/review-pr` | `/review-pr <PR#>` | Audit + improve pull requests |

### Marketplace Skills (Browse with `/plugin`)

**Top Recommended 2026:**

1. **Code Quality:** SonarQube, ESLint, Prettier integrations
2. **Testing:** vitest, jest, testing-library auto-runners
3. **Security:** gitleaks, OWASP ZAP, dependency scanning
4. **Deployment:** Docker, Kubernetes, Vercel, Railway builders
5. **Monitoring:** Sentry, DataDog, New Relic connectors
6. **Documentation:** Sphinx, MkDocs, Typedoc generators
7. **Search:** Exa, Perplexity, Google Search
8. **AI Models:** OpenRouter, Anthropic, OpenAI, XAI, Groq switchers
9. **Git:** GitHub Actions, GitLab CI, advanced merge strategies
10. **Database:** Supabase, PostgreSQL, MySQL CLI tools

---

## How to Use Skills: 3 Methods

### Method 1: Explicit Invocation (What you do now)
```
/commit "feat: add feature"
/pr create --title "New Feature"
/model haiku  # Switch to Haiku
```

### Method 2: Auto-Suggestion (I should propose)
**Current:** You ask, I execute
**Improved:** I suggest when tool would help
```
Example scenario:
User: "Fix that error in main.ts"
Me: "Found 3 issues. Should I run `/pr review` to audit them first?"
```

### Method 3: Automatic Execution (Hooks)
**Configuration in `.claude/settings.json`:**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "trigger": "if_modified_multiple_files",
        "auto_execute": ["/pr review", "/help"]
      },
      {
        "matcher": "Bash",
        "trigger": "on_test_failure",
        "auto_execute": ["/model sonnet", "re-analyze"]
      }
    ],
    "SessionStart": [
      {
        "auto_execute": ["check /tasks", "suggest next skill"]
      }
    ]
  }
}
```

---

## Skill Discovery & Learning

### 1. List Available Skills (No Built-in Command Yet)
```bash
# Manual discovery
ls ~/.claude/skills/                    # Local custom skills
gh marketplace list-actions             # GitHub Actions
vercel dev --list-functions             # Vercel functions
npm search @claude --quality             # Published skills
```

### 2. Recommended Learning Resources (2026)

**Official:**
- Bozhidar Batsov: "Essential Claude Code Skills" (Mar 2026)
- Medium: "Complete Claude Code Power User Guide" (Mar 2026)
- PolySkill.ai: "How to Add Skills" (Feb 2026)

**Community (Reddit /r/ClaudeCode):**
- "What skills are you using?" (Mar 2026) — 200+ comments on best practices
- "Build a Claude Skill in 10 Minutes" (Mar 2026) — 500+ upvotes

**Hands-on:**
- YouTube: "Claude Skills Tutorial for Beginners" (Mar 2026)
- GitHub: sdras/awesome-actions (27,597 ⭐) — GitHub Actions best practices
- GitHub: caramaschiHG/awesome-ai-agents-2026 (175⭐) — 300+ agent frameworks

---

## Framework Integration: Agent Orcha + VoltAgent

### Recommended Stack 2026

```typescript
// Use BOTH for different needs:

// 1. Agent Orcha — Declarative YAML-based orchestration
// Best for: Simple multi-agent workflows, team collaboration
const workflow = yaml.load(`
agents:
  - dep_auditor
  - archaeology_digger
  - dead_code_detector
connections:
  - dep_auditor → archaeology_digger (findings)
  - archaeology_digger → dead_code_detector (files)
`);

// 2. VoltAgent — TypeScript-first, production-ready
// Best for: Complex coordination, memory, observability
import { VoltAgent, Memory, ObserverGroup } from 'voltagent';

const agent = new VoltAgent({
  name: 'egos-orchestrator',
  memory: new Memory.Persistent('~/.egos/agent-memory'),
  tools: [dep_auditor, archaeology_digger, dead_code_detector],
  observers: new ObserverGroup(['telemetry', 'governance-drift'])
});

// 3. GitHub Agentic Workflows (NEW 2026) — CI/CD native
// Best for: Automated triage, issue investigation, PR analysis
// Deploy in .github/workflows/agentic-*.yml
name: 'Agentic Workflow'
on: [push, pull_request]
jobs:
  auto-triage:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: github/agentic-workflows@v1
        with:
          agent: 'issue-triage'
          model: 'claude-opus-4-6'
```

---

## Skill Auto-Activation Rules

**Create `.claude/skill-automation.json`:**

```json
{
  "auto_suggest": [
    {
      "trigger": "file_count > 5 modified",
      "suggest": "/review-pr",
      "reason": "Large change should be audited"
    },
    {
      "trigger": "contains('TODO', 'FIXME', 'XXX')",
      "suggest": "/help",
      "reason": "Code comments suggest documentation needed"
    },
    {
      "trigger": "test_failure detected",
      "suggest": "/model sonnet",
      "reason": "Sonnet better for debugging complex test failures"
    },
    {
      "trigger": "security vulnerability found",
      "suggest": "/commit --force-review",
      "reason": "Security issues need governance audit"
    },
    {
      "trigger": "cross_repo_impact detected",
      "suggest": "/disseminate",
      "reason": "Changes affect leaf repos, sync governance"
    }
  ],
  "auto_execute": [
    {
      "trigger": "pre_commit_hook",
      "execute": ["gitleaks", "tsc --strict", "prettier --check"],
      "block_on": "error"
    },
    {
      "trigger": "session_end",
      "execute": ["/end"],
      "reason": "Auto-handoff for session continuity"
    }
  ]
}
```

---

## Best Practices (From 2026 Research)

### ✅ DO

1. **Discover skills early** — Check marketplace in first 5 minutes of session
2. **Suggest before executing** — Let user approve before auto-running
3. **Chain skills logically** — `/review-pr` → `/commit` → `/pr create`
4. **Log skill usage** — Track which skills were helpful (telemetry)
5. **Version skills** — Keep in git for reproducibility

### ❌ DON'T

1. **Auto-execute without permission** — Ask first, execute after approval
2. **Use wrong tool for job** — ESLint is not a security scanner
3. **Ignore failures silently** — Log errors, suggest alternatives
4. **Mix conflicting skills** — Prettier then ESLint auto-format conflicts
5. **Forget to suggest** — User should know options exist

---

## Skill Roadmap: What to Build

| Skill | Type | Priority | Effort |
|-------|------|----------|--------|
| **Rho Watcher** | Governance | P0 | 2h |
| **X.com Streamer** | Integration | P0 | 4h |
| **ETL Health Monitor** | Operations | P0 | 3h |
| **CLAUDE.md Generator** | Automation | P1 | 1h |
| **Governance Sync** | Distribution | P1 | 2h |
| **Multi-repo Auditor** | Analysis | P1 | 4h |
| **Skills Auto-Suggester** | Convenience | P2 | 2h |
| **Knowledge Graph Builder** | Learning | P2 | 6h |

---

## Implementation Checklist

- [ ] Read skill marketplace (find 5 new ones)
- [ ] Configure `.claude/skill-automation.json`
- [ ] Set up `/plugin` browser shortcuts
- [ ] Enable auto-suggestions in hooks
- [ ] Document custom skills in SKILLS_REGISTRY.md
- [ ] Test skill chaining (3 sequential)
- [ ] Train team on skill discovery
- [ ] Monthly skill audit (what's working? what's obsolete?)

---

## Sources

- Exa search: GitHub Agentic Workflows, Agent Orcha, VoltAgent
- Reddit: /r/ClaudeCode skill discussions (Mar 2026)
- Medium: "Complete Claude Code Power User Guide" (Aeon Flex, Mar 2026)
- GitHub: caramaschiHG/awesome-ai-agents-2026 (175⭐)
- Official: Bozhidar Batsov article (Mar 11, 2026)
