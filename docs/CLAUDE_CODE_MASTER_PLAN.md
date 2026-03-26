# 🚀 Claude Code Master Plan — EGOS Hub Central (90 Days)

**Status:** Phase 0 → Phase 4 | **Duration:** 90 days | **Owner:** Claude Code (Haiku 4.5)
**Goal:** Claude Code becomes primary interface for EGOS orchestration across all platforms

---

## 📊 Strategic Vision

```
PHASE 0: Foundation (DONE ✅ 2026-03-25)
├─ Integrate EGOS kernel
├─ Document integrations
├─ Design 3 MCPs
└─ Create master plan

PHASE 1: Hub Activation (WEEK 1-2)
├─ Configure Claude Code as SSOT client
├─ Setup model routing system
├─ Deploy governance automation
└─ Test Phase 2 repo sync

PHASE 2: Multi-Repo Orchestration (WEEK 3-4)
├─ Sync all 11 leaf repos
├─ Setup automated drift detection
├─ Configure Telegram cockpit
└─ Create monitoring dashboard

PHASE 3: Custom MCP Implementation (WEEK 5-6)
├─ Build Forja MCP (6 tools)
├─ Build Telegram Bot MCP (25+ commands)
├─ Build WhatsApp Workflow MCP
└─ Test with real users

PHASE 4: Universal Activation (WEEK 7-8)
├─ Deploy MCPs to ChatGPT/Claude/Codex
├─ Setup model rotation system
├─ Implement cost optimization
└─ Reach 10/10 power level

PHASE 5: Continuous Evolution (WEEK 9+)
├─ Monitor performance metrics
├─ Add new integrations (Linear, Slack, Discord)
├─ Optimize context routing
└─ Maintain EGOS as distributed system
```

---

## 🎯 PHASE 1: Hub Activation (Week 1-2)

### Goal: Claude Code = Primary EGOS Interface

#### 1.1 Configuration

**File:** `~/.claude/claude-code-hub.json`

```json
{
  "name": "EGOS Hub (Claude Code)",
  "type": "orchestration-kernel",
  "role": "primary-interface",
  "version": "1.0.0",

  "routing": {
    "default_model": "haiku-4-5",
    "fallback_model": "sonnet-4-6",
    "context_threshold": 180000,

    "model_selection": {
      "trivial": {
        "model": "haiku",
        "max_tokens": 2000,
        "use_case": "Simple reads, lists, status checks"
      },
      "simple": {
        "model": "haiku",
        "max_tokens": 4000,
        "use_case": "Basic edits, small tasks, queries"
      },
      "moderate": {
        "model": "sonnet",
        "max_tokens": 8000,
        "use_case": "Multi-step tasks, integration work, tests"
      },
      "complex": {
        "model": "opus",
        "max_tokens": 16000,
        "use_case": "Architecture, refactoring, design"
      },
      "critical": {
        "model": "opus",
        "max_tokens": 32000,
        "context": "full",
        "use_case": "Security, compliance, mission-critical"
      }
    }
  },

  "egos_integration": {
    "kernel_path": "/home/enio/egos",
    "shared_path": "~/.egos",
    "leaf_repos": 11,
    "ssot_registry": "egos/docs/SSOT_REGISTRY.md",
    "meta_prompts": "egos/.guarani/prompts/PROMPT_SYSTEM.md"
  },

  "automation": {
    "governance_check": "0 9 * * *",
    "repo_sync": "weekly",
    "drift_detection": "hourly",
    "cost_optimization": "daily"
  }
}
```

#### 1.2 Model Router Implementation

**File:** `~/.claude/scripts/model-router.ts`

```typescript
interface TaskContext {
  complexity: 'trivial' | 'simple' | 'moderate' | 'complex' | 'critical';
  contextSize: number;
  domain: string;
  deadline?: string;
  costBudget?: number;
}

function suggestModel(context: TaskContext): {
  model: string;
  reason: string;
  alternatives: string[];
} {
  // Complexity-based routing
  if (context.complexity === 'critical') {
    return {
      model: 'opus-4-6',
      reason: 'Mission-critical: need full reasoning + safety',
      alternatives: ['sonnet-4-6']
    };
  }

  if (context.complexity === 'complex') {
    if (context.contextSize > 150000) {
      return {
        model: 'opus-4-6',
        reason: 'High context: need extended window',
        alternatives: ['sonnet-4-6', 'haiku-4-5']
      };
    }
    return {
      model: 'sonnet-4-6',
      reason: 'Complex task: balanced power + speed',
      alternatives: ['opus-4-6', 'haiku-4-5']
    };
  }

  if (context.complexity === 'moderate') {
    return {
      model: 'sonnet-4-6',
      reason: 'Moderate: good balance',
      alternatives: ['haiku-4-5', 'opus-4-6']
    };
  }

  // Domain-based routing
  if (context.domain === 'governance' || context.domain === 'security') {
    return {
      model: 'opus-4-6',
      reason: 'Domain requires deep reasoning',
      alternatives: ['sonnet-4-6']
    };
  }

  if (context.domain === 'chat' || context.domain === 'simple-tasks') {
    return {
      model: 'haiku-4-5',
      reason: 'Fast, cost-effective, sufficient',
      alternatives: ['sonnet-4-6']
    };
  }

  // Cost-based routing
  if (context.costBudget && context.costBudget < 0.01) {
    return {
      model: 'haiku-4-5',
      reason: 'Ultra-low budget: most cost-effective',
      alternatives: ['sonnet-4-6']
    };
  }

  // Default
  return {
    model: 'haiku-4-5',
    reason: 'Fast default for most tasks',
    alternatives: ['sonnet-4-6', 'opus-4-6']
  };
}

// Usage in Claude Code:
// Auto-suggest before complex tasks:
// "This looks complex (6+ files, 8+ decisions).
//  Suggest: sonnet-4-6 for better reasoning.
//  Current: haiku-4-5. Switch? [Yes] [No] [Ask]"
```

#### 1.3 Windsurf IDE Config

**File:** `.windsurfrules` (top section)

```markdown
# Claude Code Hub Configuration
---
project: "EGOS Hub (Claude Code)"
version: "1.0.0"
role: "primary-orchestration-interface"
environment: "Windsurf IDE + Claude Code"

## AUTO-MODEL SUGGESTION
The system will suggest model changes based on task complexity:

| Task Type | Suggested Model | Reason |
|-----------|---|---|
| Governance sync | Opus 4.6 | Full reasoning needed |
| Multi-repo changes | Sonnet 4.6 | Balanced power + speed |
| Simple edits | Haiku 4.5 | Fast, cost-effective |
| Research/exploration | Sonnet 4.6 | Better web access |
| Code review | Opus 4.6 | Security-critical |

**AUTO-TOGGLE TRIGGERS:**
- If context > 150k tokens AND complexity > moderate → suggest Sonnet/Opus
- If multiple file edits (>5 files) → suggest Sonnet
- If security/compliance topic → always Opus
- If cost budget < $0.01 → always Haiku
- If speed critical (< 10s needed) → Haiku
```

#### 1.4 Automation Setup

**File:** `/home/enio/egos/scripts/claude-code-init.sh`

```bash
#!/bin/bash
# Initialize Claude Code as EGOS Hub

echo "🚀 Claude Code Hub Initialization"
echo "================================="

# 1. Create config files
mkdir -p ~/.claude/config
cp claude-code-hub.json ~/.claude/config/

# 2. Setup model router
curl -o ~/.claude/scripts/model-router.ts https://raw.github.com/enioxt/egos/main/scripts/model-router.ts

# 3. Create status line config
cat > ~/.claude/statusline.json << 'EOF'
{
  "left": [
    { "segment": "model", "format": "Model: ${model}" },
    { "segment": "tokens", "format": "Tokens: ${used}/${max}" },
    { "segment": "complexity", "format": "Complexity: ${task_level}" }
  ],
  "right": [
    { "segment": "cost", "format": "Cost: ${estimate}" },
    { "segment": "egos_sync", "format": "EGOS: ${drift_status}" }
  ]
}
EOF

# 4. Setup hooks
cat > ~/.claude/hooks/on-task-start.sh << 'EOF'
#!/bin/bash
# Auto-suggest model before complex tasks
COMPLEXITY=$(claude-code analyze-complexity)
if [ "$COMPLEXITY" = "complex" ] || [ "$COMPLEXITY" = "critical" ]; then
  echo "⚠️  Complex task detected. Consider: /model sonnet or /model opus"
fi
EOF

# 5. Create governance watch
/schedule "0 9 * * *" "bash /home/enio/egos/scripts/claude-code-init.sh --check-governance"

echo "✅ Claude Code Hub initialized"
echo "📍 Next: Run Phase 2 (repo sync)"
```

#### 1.5 Status Dashboard

**File:** `~/.claude/dashboards/egos-hub.md`

```markdown
# EGOS Hub Status Dashboard

## Current State
- Model: Haiku 4.5
- Context Used: 180k / 200k
- Session Time: 2h 15m
- Cost This Session: $0.45

## Recommendations
🔄 **Switch to Sonnet?**
- Context usage at 90%
- Task complexity increasing (architecture work)
- Estimated cost increase: +$0.12

## Governance Status
✅ Kernel: 0 drift
✅ Forja: 0 drift
⚠️ 852: 2 warnings (old docs)
⏳ Phase 2: Ready to execute

## Upcoming
- Tomorrow 9am: Governance check
- This week: Phase 2 (repo sync)
- Next week: Phase 3 (MCP build)

## Cost Tracker
- This session: $0.45 (Haiku: $0.35, Sonnet: $0.10)
- This month: $12.30
- Budget: $50/month
```

---

## 🎯 PHASE 2: Multi-Repo Orchestration (Week 3-4)

### Goal: All 11 repos synchronized, automated monitoring

#### 2.1 Automated Drift Detection

**File:** `/home/enio/egos/scripts/claude-code-watch.sh`

```bash
#!/bin/bash
# Claude Code continuous governance watch

WATCH_INTERVAL=3600  # Every hour
ALERT_THRESHOLD=3    # Drift in 3+ files

while true; do
  echo "[$(date)] Running governance check..."

  DRIFT=$(bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --check 2>&1 | grep "Drift:")

  if [ ! -z "$DRIFT" ]; then
    # Alert to Claude Code status line
    echo "⚠️  EGOS Drift detected: $DRIFT"

    # Suggest action
    echo "🤖 Claude Code suggestion:"
    echo "   Run: bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --exec"
    echo "   Or: /loop 5m 'bash ... --check' to monitor live"
  else
    echo "✅ All repos clean"
  fi

  sleep $WATCH_INTERVAL
done
```

**Setup:**
```bash
# Run in background
nohup bash ~/.claude/scripts/claude-code-watch.sh > ~/.claude/logs/egos-watch.log 2>&1 &

# Or schedule via Claude Code
/schedule "*/60 * * * *" "bash /home/enio/egos/scripts/claude-code-watch.sh"
```

#### 2.2 Telegram Cockpit Integration

**File:** `/home/enio/forja/scripts/claude-code-telegram-bridge.ts`

```typescript
// Bridge between Claude Code and Telegram Bot

interface TelegramCommand {
  command: string;
  args: string[];
  user_id: string;
  chat_id: string;
}

async function handleCommand(cmd: TelegramCommand): Promise<string> {
  // Execute via Claude Code if needed
  if (cmd.command === 'governance' && cmd.args[0] === 'check') {
    // Trigger Claude Code to run check
    const result = await claudeCode.execute({
      tool: 'bash',
      command: 'bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --check'
    });

    return formatTelegramResponse(result);
  }

  // Other commands...
}

// Claude Code will automatically suggest:
// "Telegram command received. Run via /skill telegram:handle-command?"
```

#### 2.3 Monitoring Dashboard

**File:** `~/.claude/dashboards/phase-2-status.md`

```markdown
# Phase 2 Status: Multi-Repo Orchestration

## Repo Sync Status
| Repo | Status | Last Sync | Drift |
|------|--------|-----------|-------|
| egos (kernel) | ✅ | Now | 0 |
| forja | ✅ | 2h ago | 0 |
| 852 | ✅ | 3h ago | 0 |
| br-acc | ✅ | 5h ago | 0 |
| carteira-livre | ✅ | 6h ago | 0 |
| commons | ⚠️ | 12h ago | 2 |
| egos-lab | ✅ | 4h ago | 0 |
| egos-self | ✅ | 7h ago | 0 |
| policia | ⏳ | Never | N/A |
| santiago | ⏳ | Never | N/A |
| smartbuscas | ✅ | 1h ago | 0 |
| INPI | ⏳ | Never | N/A |

## Automation Status
✅ Hourly drift detection active
✅ Telegram cockpit ready
✅ Email alerts configured
✅ Cost tracking enabled

## Next
- Fix commons (2 drift files)
- Setup policia, santiago, INPI
- Full 11/11 repos synchronized
```

---

## 🎯 PHASE 3: Custom MCP Implementation (Week 5-6)

### Goal: Build 3 MCPs, become available everywhere

#### 3.1 Forja MCP Server

**File:** `/home/enio/forja/mcp/server.ts`

```typescript
import Anthropic from "@anthropic-ai/sdk";

const server = new Anthropic.SDK.MCPServer({
  name: "forja-tools",
  description: "Forja operational tools (quotes, inventory, production)",
  version: "1.0.0"
});

// 6 tools exposed
server.tool("forja.quote.create", {
  description: "Create quotation",
  inputSchema: {
    type: "object",
    properties: {
      customer_id: { type: "string" },
      items: { type: "array" },
      deadline: { type: "string" }
    }
  },
  execute: async (input) => {
    // Implementation
  }
});

server.tool("forja.inventory.check", {
  description: "Check stock status",
  inputSchema: { /* ... */ },
  execute: async (input) => { /* ... */ }
});

// 4 more tools...

// Claude Code suggestion when building:
// "Building MCP server. Consider: opus-4-6 for architecture review"
```

#### 3.2 Deployment

**File:** `/home/enio/forja/scripts/deploy-mcp.sh`

```bash
#!/bin/bash
# Deploy MCP servers

echo "🚀 Deploying MCP Servers..."

# 1. Forja MCP
npm run mcp:build
npm run mcp:deploy --env=production
echo "✅ Forja MCP deployed to https://forja.vercel.app/api/mcp"

# 2. Telegram Bot MCP
cd /home/enio/forja/mcp/telegram
npm run deploy
echo "✅ Telegram Bot MCP deployed"

# 3. WhatsApp Workflow MCP
cd /home/enio/forja/mcp/whatsapp
npm run deploy
echo "✅ WhatsApp Workflow MCP deployed"

# Register with Claude Code
echo "📋 Registering with Claude Code..."
cat >> ~/.claude/mcp.json << 'EOF'
{
  "forja-tools": {
    "command": "curl",
    "args": ["https://forja.vercel.app/api/mcp"],
    "env": { "FORJA_API_KEY": "${env:FORJA_API_KEY}" }
  },
  "telegram-bot": { /* ... */ },
  "whatsapp-workflow": { /* ... */ }
}
EOF

echo "✅ All MCPs registered"
echo "🔗 Now available in: Claude Code, ChatGPT, Codex, Perplexity"
```

---

## 🎯 PHASE 4: Universal Activation (Week 7-8)

### Goal: Claude Code controls access to EGOS everywhere

#### 4.1 Model Recommendation System

**When task starts, Claude Code asks:**

```
📊 Task Analysis:
  • Complexity: Moderate
  • Context needed: 120k tokens
  • Domain: Governance (requires reasoning)
  • Files to edit: 5
  • Time budget: < 5 minutes

💡 Current: Haiku 4.5
✅ Recommended: Sonnet 4.6 (better reasoning for governance)
🔥 Premium: Opus 4.6 (full context window, advanced reasoning)

Cost estimate:
  • Haiku: $0.05
  • Sonnet: $0.18
  • Opus: $0.45

[Use Sonnet] [Use Opus] [Stay Haiku] [Ask me next time]
```

#### 4.2 Alternative Models Integration

**File:** `~/.claude/model-router.json`

```json
{
  "providers": {
    "anthropic": {
      "models": [
        "opus-4-6",
        "sonnet-4-6",
        "haiku-4-5"
      ]
    },
    "google": {
      "models": ["gemini-2-0-pro", "gemini-2-0-flash"],
      "trigger": "when_context > 200k OR when_image_heavy"
    },
    "alibaba": {
      "models": ["qwen-plus", "qwen-turbo"],
      "trigger": "cost_optimization OR speed_critical",
      "cost_per_1k": 0.002
    },
    "kimi": {
      "models": ["kimi-2-5"],
      "trigger": "long_context OR research_heavy",
      "max_tokens": 200000
    },
    "openai": {
      "models": ["o1", "gpt-4-turbo"],
      "trigger": "when_reasoning_critical"
    }
  },

  "switching_rules": {
    "when_context_exceeds_150k": "suggest sonnet or gemini",
    "when_token_limit_reaches_90_percent": "suggest model with larger window",
    "when_task_is_research_heavy": "suggest kimi or gemini",
    "when_cost_critical": "suggest haiku or qwen",
    "when_speed_critical": "suggest gemini-flash or qwen-turbo",
    "when_image_input": "suggest gemini or claude",
    "when_reasoning_heavy": "suggest opus or o1"
  }
}
```

#### 4.3 Cost Optimization Dashboard

**File:** `~/.claude/dashboards/cost-optimization.md`

```markdown
# Cost Optimization Dashboard

## Current Month (March 2026)
- Total: $12.30 / $50 budget (24.6%)
- Haiku: $8.10 (66%)
- Sonnet: $3.50 (28%)
- Opus: $0.70 (6%)

## Recommended Actions
1. **Haiku overuse**: 40% of tasks could use Haiku
   - Savings: -$2.10/month

2. **Qwen integration**: Cheaper for simple tasks
   - Cost: $0.002/1k tokens (vs $0.001 for Haiku)
   - Use for: Non-critical, simple tasks

3. **Gemini for research**: Better web context
   - Cost: Similar to Sonnet
   - Use for: Web-heavy research

## Model Recommendations by Task
| Type | Best | Cost | Speed | Reasoning |
|------|------|------|-------|-----------|
| Simple edits | Haiku | $ | Fast | Low |
| Multi-file changes | Sonnet | $$ | Medium | High |
| Architecture | Opus | $$$ | Slow | Very High |
| Web research | Gemini | $$ | Medium | Medium |
| Cost-critical | Qwen | $ | Medium | Low |
```

---

## 📋 PHASE 5: Continuous Evolution (Week 9+)

### Goal: EGOS as distributed, intelligent system

#### 5.1 Automated Integration Additions

```markdown
## Future Integrations (Ready to Add)

### Linear/Jira Sync
- Auto-create tickets from TASKS.md
- Link PRs to tickets
- Update status on merge

### Slack Notifications
- Governance drift alerts
- Deployment status
- Team updates

### Discord Integration
- Public team chat
- Bot commands
- Logs streaming

### OpenCloud Connector
- Sync docs to mobile
- Export conversations
- Cloud backup

### Advanced Monitoring
- Custom Grafana dashboards
- Real-time metrics
- Cost per repo tracking
```

#### 5.2 Continuous Learning

**File:** `~/.claude/learning/task-analysis.json`

```json
{
  "task_history": [
    {
      "date": "2026-03-25",
      "task": "Sync governance across 11 repos",
      "complexity_actual": "moderate",
      "complexity_predicted": "moderate",
      "model_used": "haiku",
      "model_optimal": "haiku",
      "success": true,
      "cost": 0.05,
      "time": "15min"
    }
  ],

  "patterns": {
    "governance_tasks": {
      "avg_complexity": 6.2,
      "optimal_model": "sonnet",
      "success_rate": 95
    },
    "simple_edits": {
      "avg_complexity": 2.1,
      "optimal_model": "haiku",
      "success_rate": 98
    }
  },

  "recommendations": {
    "governance_tasks_should_default_to_sonnet": true,
    "haiku_is_95_percent_sufficient": true,
    "cost_optimization_possible": 12.5
  }
}
```

---

## 🔧 IMPLEMENTATION CHECKLIST

### Phase 1 (This Week)
- [ ] Create `claude-code-hub.json` configuration
- [ ] Build model router system
- [ ] Setup Windsurf IDE config
- [ ] Create status dashboard
- [ ] Test model switching
- [ ] Document auto-suggestions

### Phase 2 (Week 3-4)
- [ ] Deploy drift detection automation
- [ ] Integrate Telegram cockpit
- [ ] Setup monitoring dashboard
- [ ] Sync all 11 repos
- [ ] Test automation triggers
- [ ] Document Phase 2 completion

### Phase 3 (Week 5-6)
- [ ] Build Forja MCP (6 tools)
- [ ] Build Telegram MCP (25+ commands)
- [ ] Build WhatsApp MCP
- [ ] Test MCP registration
- [ ] Deploy to Vercel
- [ ] Make available in ChatGPT/Codex

### Phase 4 (Week 7-8)
- [ ] Implement model recommendation system
- [ ] Setup alternative model routing
- [ ] Create cost optimization dashboard
- [ ] Test with real tasks
- [ ] Document savings achieved
- [ ] Reach 10/10 power level

### Phase 5 (Week 9+)
- [ ] Add Linear/Jira sync
- [ ] Add Slack integration
- [ ] Add Discord bot
- [ ] Setup continuous learning
- [ ] Monitor performance metrics
- [ ] Plan next quarter improvements

---

## 💰 Cost Projections

### Current Model
- Haiku: $0.80/day = $24/month
- Sonnet: $0.15/day = $4.50/month
- **Total: ~$30/month**

### With Phase 4 Optimization
- Haiku (80%): $19.20/month
- Sonnet (15%): $2.25/month
- Qwen (5%): $0.15/month
- **Total: ~$22/month (-27% savings)**

### With Alternative Models
- Add Gemini for research: +$3/month
- Add Kimi for long-context: +$2/month
- **Optimized total: ~$27/month**

---

## 📞 Quick Command Reference

```bash
# Switch models
/model haiku|sonnet|opus|gemini|qwen|kimi

# Check recommendation
/model suggest

# Start Phase 1
bash /home/enio/egos/scripts/claude-code-init.sh

# Monitor governance
/loop 1h "bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --check"

# View cost dashboard
cat ~/.claude/dashboards/cost-optimization.md

# Deploy MCPs
bash /home/enio/forja/scripts/deploy-mcp.sh

# Check EGOS status
/skill egos:status-check
```

---

## 🏁 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Power Level | 10/10 | 8/10 |
| Repos Synced | 11/11 | 1/11 |
| MCPs Active | 3/3 | 0/3 |
| Automation | 100% | 60% |
| Cost/month | $27 | $30 |
| Model Switching | Automatic | Manual |
| Context Optimization | Full | Partial |

---

## 🎯 By End of Phase 4:

✅ Claude Code = Primary EGOS interface
✅ All 11 repos orchestrated
✅ 3 MCPs deployed (Forja, Telegram, WhatsApp)
✅ Automatic model selection
✅ Cost optimized (-27%)
✅ Available everywhere (Claude Code, ChatGPT, Codex, Perplexity)
✅ Power level: 10/10 🔥

**Claude Code becomes the brain. EGOS becomes the nervous system.**

---

**Created:** 2026-03-25 | **By:** Claude Code (Haiku 4.5) | **For:** Enio Rocha
**Status:** Ready for Phase 1 execution
