# 🚀 EGOS Multi-MCP Orchestration & Model Routing Strategy

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** multi-MCP orchestration and model-routing strategy reference
- **Summary:** Canonical routing strategy for MCP/tool and model selection with cost/latency context across providers.
- **Read next:**
  - `docs/ACTIVATION_GUIDE.md` — activation steps
  - `docs/MCP_SCOPE_POLICY.md` — scope safety boundaries
  - `TASKS.md` — implementation priorities
<!-- llmrefs:end -->

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-23 | **TYPE:** Orchestration Framework
> **STATUS:** ACTIVE | **Priority:** P0 (Core Kernel)

---

## Executive Summary

You have a **POWERHOUSE** configuration:
- 🟢 **7 MCPs** (EXA, Sequential-Thinking, Memory, Filesystem, GitHub, Supabase, Morph)
- 🟢 **12+ LLM Models** across Alibaba + OpenRouter + Groq
- 🟢 **Multi-provider setup** with quota management
- 🔴 **PROBLEM:** Underutilized routing + no strategic orchestration

This document defines the **MASTER ROUTING ALGORITHM** for EGOS agents.

---

## Part 1: Current Model Inventory

### Alibaba DashScope (Primary)
| Model | Tier | Input Cost | Output Cost | Max Context | Best For |
|-------|------|-----------|------------|------------|----------|
| Qwen Flash | Economy | FREE | FREE | 131K | Classifications, fast ops |
| Qwen Plus | Balanced | $0.8/M | $2/M | 131K | Analysis, chat, general |
| Qwen Max | Premium | $1.6/M | $6.4/M | 32K | Complex reasoning |
| Qwen3 Coder Plus | Specialist | $0.8/M | $2/M | 131K | Code generation/review |

### OpenRouter (Secondary) - **TOP PERFORMERS 2026**
| Model | Provider | Tier | Input Cost | Use Case | Status |
|-------|----------|------|-----------|----------|--------|
| **Claude Opus 4.6** | Anthropic | ULTRA | ~$3/M | CRITICAL decisions + reasoning | 🔥 LATEST |
| **Claude Sonnet 4** | Anthropic | Premium | ~$3/M | Complex orchestration | ✅ Active |
| **Claude Haiku 4.5** | Anthropic | Economy | $0.80/M | Fast checks + validation | ✅ Active |
| **Gemini 3.1 Pro Preview** | Google | Premium | ~$1-2/M | Multimodal + research | 🆕 NEW |
| **Gemini 5.4 Pro** | Google | Premium | ~$1.5/M | High-capability reasoning | ✅ Active |
| **Gemini Flash** | Google | Free | FREE | Fast inference | ✅ Free Tier |
| **DeepSeek Chat V3** | DeepSeek | Balanced | $0.27/M | Cost-effective reasoning | ✅ Good ratio |
| **Groq (LLaMA)** | Groq | Economy | Cheap | Ultra-fast inference | ✅ Speed tier |

### Quota Status (Windsurf Config)
- ✅ **Claude Opus 4.6** - UNLIMITED (confirmed in config)
- ✅ **Claude Sonnet 4** - HIGH quota
- ✅ **Claude Haiku** - HIGH quota  
- ✅ **Gemini 5.4 Pro** - GOOD quota
- ✅ **Qwen Plus** - GOOD quota
- ✅ **Groq** - UNLIMITED

---

## Part 2: MCP Integration Map

### 🟢 ENABLED MCPs (Ready to Use)

#### 1. **EXA MCP** - Research & Web Search
- **Path:** Remote MCP (https://mcp.exa.ai/mcp)
- **API Key:** 699a9810-2bad-43bc-8fdf-53ebabe50f46
- **Capabilities:**
  - Real-time web search
  - Research summarization
  - Latest news/trends
  - Technical documentation
- **Best With:** Gemini 5.4 Pro (latest knowledge)
- **Activation:** Auto-enable for "research", "find", "search" triggers

#### 2. **Sequential-Thinking MCP** - Complex Reasoning Chains
- **Path:** @modelcontextprotocol/server-sequential-thinking
- **Capabilities:**
  - Extended thinking (up to 10k+ tokens)
  - Multi-step reasoning
  - Problem decomposition
  - Strategic planning
- **Best With:** Claude Opus 4.6 (reasoning champion)
- **Usage Pattern:** Pre-process complex tasks with thinking before execution

#### 3. **Memory MCP** - Persistent Learning
- **Path:** @modelcontextprotocol/server-memory
- **Storage:** `/home/enio/egos-lab/memory_db/memory.jsonl`
- **Capabilities:**
  - Cross-session learning
  - Pattern recognition
  - Decision history
  - Agent tuning
- **Integration:** Every task should write patterns to memory

#### 4. **Filesystem MCP** - Local Operations
- **Paths:** 
  - `/home/enio/carteira-livre`
  - `/home/enio/egos-lab`
  - `/home/enio/egos-archive`
  - `/tmp`
- **Capabilities:** File creation, reading, git operations, scanning

### 🔴 DISABLED MCPs (Available to Activate)

#### 5. **GitHub MCP** - Repo Automation
- **Status:** Disabled but configured
- **Token:** Valid PAT available
- **Activation:** Use for `git operations`, `PR creation`, `CI/CD`
- **Recommendation:** ENABLE for production workflows

#### 6. **Supabase MCPs** - Database Persistence
- **Instances:** 2 configured (carteira-livre, egosv3)
- **Status:** Optional for persistence layer
- **Use:** Store long-term memories, conversation history

#### 7. **Morph MCP** - LLM Multiplexing  
- **Status:** ENABLED (config shows morph-mcp)
- **API Key:** Present
- **Capability:** Alternative model routing

---

## Part 3: Strategic Routing Algorithm

### Decision Tree Flow

```
┌─ INCOMING TASK ─┐
│   Classify      │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Trigger?│
    └────┬────┘
         │
  ┌──────┼──────┬──────┬─────────┬──────────┐
  │      │      │      │         │          │
RESEARCH THINK CODE COMPLEX VALIDATION FAST-CHECK
  │      │      │      │         │          │
  ▼      ▼      ▼      ▼         ▼          ▼
 EXA  THINK QWEN3  OPUS SONNET HAIKU
```

### Complexity-Based Routing

#### **TIER 1: Fast Check** (< 100ms target)
- **Detection:** Simple yes/no, classification, validation
- **Model:** `Claude Haiku 4.5`
- **MCP:** None
- **Cost:** $0.80/1M
- **Example:** "Is this valid JSON?" → Haiku

#### **TIER 2: Simple** (< 500ms target)  
- **Detection:** Translation, summarization, formatting
- **Model:** `Gemini Flash` (free) or `Qwen Flash` (free)
- **MCP:** Memory (store for learning)
- **Cost:** FREE or $0
- **Example:** "Translate to Portuguese" → Gemini Flash

#### **TIER 3: Moderate** (< 2s target)
- **Detection:** Code review, analysis, chat responses
- **Model:** `Qwen Plus` or `Gemini 5.4 Pro`
- **MCP:** Sequential-Thinking (optional), Memory
- **Cost:** $0.8-1.5/M input
- **Example:** "Review this pull request" → Qwen Plus

#### **TIER 4: Complex** (< 5s target)
- **Detection:** Orchestration, planning, multi-step reasoning
- **Model:** `Claude Sonnet 4` or `Gemini 3.1 Pro`
- **MCP:** Sequential-Thinking (ENABLED), Memory
- **Cost:** $3/M input
- **Example:** "Design a deployment strategy" → Sonnet 4

#### **TIER 5: Critical** (unlimited time)
- **Detection:** Strategic decisions, system design, complex debugging
- **Model:** `Claude Opus 4.6` (PRIORITY USE)
- **MCP:** Sequential-Thinking (FULL), Memory, EXA
- **Cost:** Premium but BEST reasoning
- **Example:** "Design the EGOS orchestration system" → Opus 4.6

#### **TIER 6: Research** (Internet-dependent)
- **Detection:** "research", "find latest", "what's new"
- **Model:** Gemini 5.4 Pro (latest knowledge)
- **MCP:** EXA (web search), Sequential-Thinking, Memory
- **Cost:** Premium but current data
- **Example:** "Research latest OpenRouter models" → EXA + Gemini

#### **TIER 7: Code-Heavy** (Specialization)
- **Detection:** Code generation, debugging, syntax fixing
- **Model:** `Qwen3 Coder Plus` (code specialist)
- **MCP:** Filesystem (for context), Sequential-Thinking
- **Cost:** $0.8/M (balanced)
- **Example:** "Write a React component" → Qwen3 Coder

---

## Part 4: Implementation Rules

### Rule 1: Cost Optimization
```typescript
// Pseudocode for cost calculation
const selectModel = (task, complexity, tokens) => {
  // If free option available for tier → use it
  if (complexity === 'simple' && Gemini.FREE) return Gemini;
  
  // If quota allows premium → route to premium
  if (hasQuota('opus') && complexity === 'critical') return Opus;
  
  // Default: use balanced tier
  return Qwen.Plus;
}
```

### Rule 2: MCP Pre-Processing
```
Before routing to model:
1. ✅ Check if "research" needed → Enable EXA
2. ✅ Check if "thinking" needed → Enable Sequential-Thinking
3. ✅ Check if "memory" applicable → Initialize Memory
4. ✅ Check file access needed → Enable Filesystem
```

### Rule 3: Sequential Thinking Protocol
```
Complex tasks MUST go through:
1. Extended thinking (5-10 min thinking tokens)
2. Plan generation
3. Step-by-step execution
4. Memory storage of patterns
5. Return final answer

Cost: Higher but SIGNIFICANTLY better results
```

### Rule 4: Memory-Driven Learning
```
After EVERY task:
1. Extract key decision patterns
2. Store in Memory MCP
3. Cross-reference similar past tasks
4. Tune future routing based on success rate
```

---

## Part 5: Quick Reference Tables

### By Task Type
| Task | Model | MCP | Cost | Speed |
|------|-------|-----|------|-------|
| Classify | Haiku | - | $$ | ⚡⚡⚡ |
| Summarize | Flash | Memory | $$ | ⚡⚡⚡ |
| Review Code | Qwen3 | Sequential | $$$$ | ⚡⚡ |
| Plan/Orchestrate | Sonnet 4 | Sequential + Memory | $$$$$ | ⚡ |
| Research | Gemini 5.4 | EXA + Sequential | $$$$$ | ⚡ |
| Critical Decision | **Opus 4.6** | All | Premium | 🎯 |

### By Provider
| Provider | Best Model | Cost Tier | Use Case |
|----------|-----------|-----------|----------|
| Alibaba | Qwen Plus | Balanced | General purpose |
| Anthropic | **Claude Opus** | Premium | Strategic |
| Google | Gemini 5.4 | Premium | Research |
| Meta | LLaMA (via Groq) | Economy | Ultra-fast |

---

## Part 6: Deployment Checklist

- [ ] Update `model-router.ts` with ALL new models from this doc
- [ ] Add complexity detection logic to prompt analyzer
- [ ] Activate GitHub MCP for production
- [ ] Create MCP wrapper functions (exa_search, think_deeply, store_memory)
- [ ] Implement cost tracking per model per task
- [ ] Set up Memory MCP persistence
- [ ] Create decision matrix dashboard
- [ ] Test routing on sample tasks
- [ ] Monitor quota usage

---

## Part 7: Next Session Recommendation

**For maximum efficiency starting next interaction:**

Use this routing:
- **Start with:** `Claude Opus 4.6` + Sequential-Thinking
- **Research phase:** EXA + Gemini 5.4 Pro
- **Execution:** Qwen Plus for general tasks, Qwen3 Coder for code
- **Validation:** Haiku for fast checks

**Activate these MCPs in order:**
1. ✅ Sequential-Thinking (already enabled)
2. ✅ EXA (enabled but not used yet)
3. ✅ Memory (enabled but not persisting)
4. 🔴 → ENABLE GitHub (for automation)
5. 🔴 → ACTIVATE Supabase (for persistence)

---

## References

- `.guarani/PREFERENCES.md` - Coding standards
- `packages/shared/src/model-router.ts` - Current router
- `packages/shared/src/llm-orchestrator.ts` - Current orchestrator
- `docs/ENVIRONMENT_REGISTRY.md` - MCP registry
- Windsurf MCP Config (your settings)

---

**Last Updated:** 2026-03-23 by OpenCode Agent  
**Next Review:** After 10 tasks completed with new routing
