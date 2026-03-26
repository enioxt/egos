# LLM Models & Pricing — March 2026

## Executive Summary

**Best Free:** OpenRouter (27 free models, no credit card)
**Best Cheap ($0.075/M):** Gemini 2.0 Flash-Lite
**Best Value ($0.28/M + 90% cache off):** DeepSeek V3.2
**Best Quality:** Claude Opus 4.6 ($5/M), but overkill for most tasks

---

## 🆓 Free Models — No Credit Card Required

### OpenRouter Free Tier (27 models)
- **Rate limits:** 20 requests/min, 200 requests/day per model
- **Best Coding:** Qwen3-Coder 480B (262K context) ⭐
- **Best Reasoning:** Nemotron 3 Super 120B (262K context)
- **Best General:** Llama 3.3 70B (66K context) — GPT-4 level
- **Best Long Context:** Qwen3-Next 80B (262K context)

**Recommended free router endpoint:** `openrouter/free` (auto-selects best available model)

### Alibaba DashScope
- **Free quota:** 1M tokens per model, valid 90 days (Singapore region only)
- **Best for:** Qwen-Plus (fast), Qwen-Max (strong), Qwen-Coder-Plus (code)
- **After quota:** $0.27–$3/M tokens (very cheap)

---

## 💰 Paid Models — Best Bang for Buck

| Model | Input/Output | Context | Use Case | Value Score |
|-------|-------------|---------|----------|-------------|
| **Gemini 2.0 Flash-Lite** | $0.075/$0.30 | 1M | Ultra-budget, high volume | ⭐⭐⭐⭐⭐ |
| **Mistral Small 3.2** | $0.06/$0.18 | 128K | Cheapest general-purpose | ⭐⭐⭐⭐⭐ |
| **GPT-5 Nano** | $0.05/$0.40 | 128K | Cheapest input | ⭐⭐⭐⭐ |
| **Gemini 2.5 Flash** | $0.30/$2.50 | 1M | Fast, multimodal | ⭐⭐⭐⭐ |
| **DeepSeek V3.2** | $0.28/$0.42 | 128K | Code + reasoning, cache hits 90% off | ⭐⭐⭐⭐⭐ |
| **Claude Sonnet 4.6** | $3/$15 | 1M | High quality, reliable | ⭐⭐⭐⭐ |
| **Claude Opus 4.6** | $5/$25 | 1M | Best reasoning quality | ⭐⭐⭐ (overkill) |

---

## 🚀 Recommended Routing Strategy (2026)

### For Task Queue (EGOS)

1. **Simple tasks** (extraction, classification, templating)
   → **Gemini 2.0 Flash-Lite** ($0.075/M input)

2. **General purpose** (chat, summarization, analysis)
   → **Mistral Small 3.2** ($0.06 input, $0.18 output)
   OR **DeepSeek V3.2** ($0.28/$0.42, better quality)

3. **Code generation & refactoring**
   → **Qwen3-Coder (FREE on OpenRouter)**
   OR **Claude Sonnet 4.6** ($3/$15)

4. **Complex reasoning, architecture**
   → **Claude Opus 4.6** ($5/$25)
   OR **DeepSeek R1** (paid, $0.55/$2.19)

5. **If free quota available:**
   → **Alibaba Qwen** (1M free tokens/90 days)

---

## 📊 Cost Examples

**1M API calls, 100 input tokens, 200 output tokens each:**

| Provider | Cost |
|----------|------|
| Gemini 2.0 Flash-Lite | **$0.035** 🏆 |
| Mistral Small 3.2 | **$0.090** |
| DeepSeek V3.2 | **$0.140** |
| Claude Sonnet 4.6 | **$3.00** |
| Claude Opus 4.6 | **$5.00** |

---

## 💡 Special Cases

### Transcription (Audio → Text)
- **Groq Whisper** (fast, free tier: 14.4K req/day)
- **OpenAI Whisper** (API: $0.06/min audio)

### Vision/Multimodal
- **Gemini 2.5 Flash** ($0.30/$2.50, 1M context, video support)
- **Claude Sonnet 4.6** ($3/$15, excellent vision)

### Very Long Context (100K+)
- **Alibaba Qwen-Long** (10M tokens)
- **Gemini 2.5 Pro** ($1.25/$10, 2M context)
- **Claude Opus** ($5/$25, 200K context)

---

## 🔑 API Keys & Setup

### OpenRouter
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
# Use: https://openrouter.ai/api/v1/chat/completions
```

### Alibaba DashScope
```bash
export ALIBABA_DASHSCOPE_API_KEY="sk-..."
# Use: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

### Claude Pro (via CLI)
```bash
claude --model claude-opus-4-6 --print "prompt"
# No API key needed if logged in
```

### Codex (Local)
Credentials at: `~/.codex/auth.json`

---

## ⚠️ Important Notes

1. **Free models are volatile** — rate limits and availability change frequently
2. **DeepSeek cache hits** (90% off input cost) are game-changing for repetitive tasks
3. **Gemini free tier** — 1,500 requests/day from Google AI Studio (no card needed)
4. **Alibaba regional restriction** — Free quota only in Singapore region
5. **Output cost is King** — Most workloads output > input, so focus on output pricing

---

## 📈 Price Trend (2025 → 2026)

- **80% price drop** across all major models
- **Cheapest mainstream:** Gemini 2.0 Flash-Lite ($0.075/M) in Feb 2026
- **Most consistent:** DeepSeek V3.2 (stayed ~$0.14 blended)
- **Premium tier unchanged:** Claude Opus still ~$5/M

---

**Last updated:** March 26, 2026
**Source:** OpenRouter, Google Gemini API, Alibaba DashScope, DeepSeek, Anthropic pricing
