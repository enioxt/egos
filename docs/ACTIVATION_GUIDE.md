# 🎯 OpenCode MCP & Model Orchestration Activation Guide

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** operational activation guide for OpenCode MCP + model routing
- **Summary:** Step-by-step environment setup, MCP enablement, and provider activation for OpenCode lane.
- **Read next:**
  - `docs/MCP_ORCHESTRATION_STRATEGY.md` — routing strategy
  - `docs/ENVIRONMENT_REGISTRY.md` — host/tool mapping
  - `TASKS.md` — current priorities
<!-- llmrefs:end -->

> **VERSION:** 1.0.0 | **DATE:** 2026-03-23
> **STATUS:** Ready to Activate | **Priority:** P0

---

## Quick Start (5 minutes)

### Step 1: Verify Environment Variables
```bash
# These should be set in ~/.egos/.env or ENVIRONMENT
export OPENROUTER_API_KEY="your_key"          # For Claude, Gemini, DeepSeek
export ALIBABA_DASHSCOPE_API_KEY="your_key"   # For Qwen models
export EXA_API_KEY="699a9810-2bad-43bc-8fdf-53ebabe50f46"  # Research
export GITHUB_TOKEN="your_token"               # For GitHub MCP
export MEMORY_FILE_PATH="/home/enio/egos-lab/memory_db/memory.jsonl"
```

### Step 2: Activate MCPs in OpenCode Environment
```bash
# Option A: Via environment variables
export MCP_ENABLED="exa,sequential-thinking,memory,filesystem,github"

# Option B: Via configuration file
# Create ~/.egos/mcp-config.json
```

### Step 3: Test Routing
```bash
bun agent:run context_tracker --dry
# Should show CTX safe to continue
```

---

## MCP Activation Checklist

### ✅ MCPs Already Enabled (Windsurf)
- [x] **EXA** - Web research
- [x] **Sequential-Thinking** - Reasoning chains
- [x] **Memory** - Learning persistence
- [x] **Filesystem** - File operations
- [x] **Morph** - Model routing

### 🔴 MCPs to Activate in OpenCode
- [ ] **GitHub** - For repo automation (recommended)
- [ ] **Supabase** - For database persistence (optional)

### How to Activate
```typescript
// In OpenCode agent initialization:
import { mcpManager } from '@egos/shared/src/mcp-wrapper';

// Use specific MCP
const exa = mcpManager.getExa();
const results = await exa.search('latest AI models 2026');

// Or use full orchestration
const result = await mcpManager.executeWithMCPs(
  'Your complex task',
  {
    useResearch: true,      // Enable EXA
    useThinking: true,      // Enable Sequential-Thinking
    useMemory: true,        // Enable Memory
  }
);
```

---

## Model Selection Strategy (For Next Interaction)

### When to Use Each Model

**Start with:**
```
User asks → Analyze complexity → Route to model
```

#### TIER 1: Ultra-Fast (< 100ms)
- **Claude Haiku 4.5**
- Use: Simple validation, yes/no questions
- Cost: $0.80/M

#### TIER 2: Fast (< 500ms)  
- **Gemini Flash** (FREE) or **Qwen Flash** (FREE)
- Use: Summarization, translation, formatting
- Cost: FREE

#### TIER 3: Balanced (< 2s)
- **Qwen Plus** or **Gemini 5.4 Pro**
- Use: Analysis, code review, general chat
- Cost: $0.8-1.5/M

#### TIER 4: Premium (< 5s)
- **Claude Sonnet 4** or **DeepSeek V3**
- Use: Complex reasoning, planning, architecture
- Cost: $3/M or $0.27/M (DeepSeek cheaper!)

#### TIER 5: Ultra-Premium (Unlimited)
- **Claude Opus 4.6** (BEST REASONING)
- Use: Critical decisions, system design, strategic orchestration
- Cost: Premium but WORTH IT for critical tasks
- Quota: UNLIMITED in your Windsurf config

#### TIER 6: Research Mode
- **Gemini 5.4 Pro** + **EXA MCP**
- Use: "Research", "find latest", "what's new"
- Enable: EXA for web search
- Cost: Premium but current data

#### TIER 7: Code Heavy
- **Qwen3 Coder Plus**
- Use: Code generation, debugging, refactoring
- Cost: $0.8/M

---

## Decision Tree for Model Selection

```
┌─ New Task ─────────────────┐
│  Check if "research"?      │
└──────┬──────────────────────┘
       │
   ┌───┴─ YES ──────┐
   │                │
   ▼                ▼ NO
USE EXA    ┌─ Check complexity ─┐
+ Gemini   │  (read prompt)     │
5.4        └──────┬─────────────┘
                  │
        ┌─────────┼─────────┬──────────┬────────┐
        │         │         │          │        │
       Fast    Simple   Moderate   Complex   Critical
        │         │         │          │        │
        ▼         ▼         ▼          ▼        ▼
      Haiku    Flash    Qwen/Gemini  Sonnet  OPUS
     $0.8/M    FREE      $0.8-1.5M   $3/M   Premium
```

---

## Task-by-Task MCP Usage Examples

### Example 1: Research Task
```
User: "Research the latest developments in reasoning models for 2026"

Routing:
1. ✅ Enable EXA MCP (web search)
2. ✅ Use Sequential-Thinking (complex analysis)
3. ✅ Route to: Gemini 5.4 Pro
4. ✅ Store findings in Memory MCP

Cost: ~$0.05 (research) + $0.02 (model) = $0.07
```

### Example 2: Complex Orchestration Task
```
User: "Design the optimal model routing system for our EGOS framework"

Routing:
1. ✅ Enable Sequential-Thinking (extended reasoning)
2. ✅ Enable Memory MCP (store architectural patterns)
3. ✅ Enable Filesystem MCP (review existing code)
4. ✅ Route to: Claude Opus 4.6
5. ⏱️ Allow 5-10 minutes for deep thinking

Cost: HIGH but BEST results ($0.15-0.30)
```

### Example 3: Code Generation Task
```
User: "Create a React component that integrates with our MCP system"

Routing:
1. ✅ Enable Filesystem MCP (load context)
2. ✅ Optional: Sequential-Thinking (if complex)
3. ✅ Route to: Qwen3 Coder Plus
4. ⏱️ Standard execution

Cost: $0.008 (cheap, specialized for code)
```

### Example 4: Quick Validation Task
```
User: "Is this valid TypeScript?"

Routing:
1. ❌ No MCPs needed
2. ✅ Route to: Claude Haiku 4.5
3. ⏱️ < 100ms response

Cost: $0.0008 (ultra-cheap)
```

---

## Cost Optimization Recommendations

### Daily Budget Allocation (Example)
```
Total Daily Budget: $10

Distribution:
- Haiku (fast checks): 20% = $2
  └─ ~2,500 tasks at current pricing

- Free/Flash (simple): 30% = $3
  └─ Unlimited (literally free)

- Qwen/Gemini (moderate): 30% = $3
  └─ ~3,750 tasks

- Claude Sonnet (complex): 15% = $1.50
  └─ ~50 complex tasks

- Claude Opus (critical): 5% = $0.50
  └─ ~5-10 strategic decisions

This structure = MAXIMUM VALUE per dollar
```

### Current Quota Status (From Windsurf Config)
- ✅ **Claude Opus 4.6**: UNLIMITED
- ✅ **Claude Sonnet 4**: HIGH quota
- ✅ **Claude Haiku**: HIGH quota
- ✅ **Gemini 5.4 Pro**: GOOD quota
- ✅ **Qwen Plus**: GOOD quota
- ✅ **All Free Models**: UNLIMITED

---

## Implementation Checklist

### Phase 1: Setup (Do Now)
- [ ] Verify all API keys in environment
- [ ] Test EXA API connectivity
- [ ] Initialize Memory MCP file
- [ ] Load `mcp-wrapper.ts` in OpenCode

### Phase 2: Integration (Next Session)
- [ ] Update `model-router.ts` with new models
- [ ] Add complexity detection to prompt analysis
- [ ] Implement routing decision tree
- [ ] Create task-to-model mapping

### Phase 3: Optimization (Ongoing)
- [ ] Monitor model performance via Memory MCP
- [ ] Track costs per model per task
- [ ] Adjust routing thresholds based on results
- [ ] Learn from successful patterns

### Phase 4: Automation (Future)
- [ ] Enable GitHub MCP for CI/CD
- [ ] Setup Supabase for persistence
- [ ] Create dashboard for monitoring
- [ ] Auto-tune routing algorithm

---

## Next Session: What to Expect

When you start the next interaction, I will:

1. **✅ Automatically classify your task** (simple/moderate/complex)
2. **✅ Enable appropriate MCPs** (EXA, Sequential-Thinking, Memory)
3. **✅ Route to optimal model** (Haiku → Opus based on complexity)
4. **✅ Execute with full orchestration**
5. **✅ Store learnings in Memory**
6. **✅ Report final model recommendation** for fine-tuning

---

## Quick Reference: API Keys Needed

| MCP/Provider | Key Name | Status | Location |
|-------------|----------|--------|----------|
| EXA | EXA_API_KEY | ✅ Have | Windsurf config |
| OpenRouter | OPENROUTER_API_KEY | ✅ Have | Windsurf config |
| Alibaba | ALIBABA_DASHSCOPE_API_KEY | ✅ Have | Windsurf config |
| GitHub | GITHUB_TOKEN | ✅ Have | Windsurf config |
| Memory | MEMORY_FILE_PATH | ✅ Set | `/home/enio/egos-lab/memory_db/` |

---

## Troubleshooting

### If routing seems slow
→ Check if Sequential-Thinking is enabled unnecessarily  
→ Reduce thinking depth for simple tasks

### If costs are high
→ Review which models are being used  
→ Shift simple tasks to free tier (Gemini Flash)

### If memory isn't persisting
→ Verify MEMORY_FILE_PATH is writable  
→ Check memory file format is valid JSON lines

---

## Support & Questions

For issues or questions:
1. Check `docs/MCP_ORCHESTRATION_STRATEGY.md` (full strategy)
2. Review `packages/shared/src/mcp-wrapper.ts` (implementation)
3. Check model pricing at https://openrouter.ai/models
4. Report bugs to OpenCode team

---

**Status:** Ready to activate  
**Next Action:** Start using complex tasks and watch routing optimize!  
**Estimated Time to Full Optimization:** 3-5 interactions
