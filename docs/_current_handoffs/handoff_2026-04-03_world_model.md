# Handoff 2026-04-03 — World Model Research Complete

> **Agent:** cascade  
> **Session:** World Model Deep Research — SSOT Created  
> **Duration:** ~1.5h  
> **Context:** 220/280 🔴 HIGH  

---

## Summary Executivo

Pesquisa completa sobre **World Models** concluída. SSOT criado em `docs/strategy/WORLD_MODEL_SSOT.md` com:
- Conceito formal e importância para AGI
- Estado atual EGOS (Foundation v1.0)
- Roadmap completo: curto/médio/longo prazo
- Hardware 16-24GB VRAM
- Tasks WM-001..WM-016 criadas no TASKS.md

---

## O que foi entregue

### 1. SSOT Document — WORLD_MODEL_SSOT.md (8.5KB)

**Local:** `docs/strategy/WORLD_MODEL_SSOT.md`

**Seções criadas:**
- Executive Summary
- Conceito: O que é um World Model? (formal definition, LLM vs World Model)
- Importância para o EGOS (4 pilares)
- Estado Atual EGOS (Foundation v1.0)
- Roadmap completo com 4 fases
- Modelos de referência (DeepMind Genie 2, MuZero, Dreamer v3, JEPA, Qwen3Guard, Hermes-3)
- EGOS-WorldModel: Modelo Próprio? (3 opções analisadas)
- Hardware: 16-24GB VRAM (configurações recomendadas)
- Tasks WM-001..WM-016
- Métricas de sucesso
- Riscos e mitigações

### 2. TASKS.md Atualizado

**Novas tasks adicionadas:**

**P0 — World Model Foundation (NEW 2026-04-03):**
- WM-001: Setup hardware local LLM (Ollama/LM Studio)
- WM-002: Integrate local LLM to world-model.ts
- WM-003: Capability composition suggestions
- WM-004: Dataset preparation

**P1 — World Model Enhanced:**
- WM-005: Dynamics model (simulação)
- WM-006: Causal discovery
- WM-007: Counterfactual reasoning
- WM-008: Model-predictive control

**P2 — Ethics & Safety:**
- WM-009: Qwen3Guard integration
- WM-010: Constitutional rules embedding
- WM-011: Value alignment local
- WM-012: Intervention system

**P3 — AGI Capabilities:**
- WM-013..WM-016: Auto-observação, auto-modificação, long-horizon planning, auto-agent creation

### 3. Pesquisa Exa/Mercado

**Fontes consultadas:**
- DeepMind Genie 2 (foundation world model)
- World-Model-Based AGI Architectures (Medium)
- Qwen3Guard (ethical AI guardrails)
- Papers: Ha & Schmidhuber, Hafner et al., Schrittwieser et al. (MuZero)

**Key Insights:**
1. World models são a base para AGI (Yann LeCun)
2. Model-based RL é mais sample-efficient que model-free
3. DeepMind já demonstra: Genie 2 (3D worlds), MuZero (sem regras), Dreamer v3 (Atari)
4. Ethical guardrails: Qwen3Guard (streaming, 119 línguas, 3 tiers)

### 4. Análise EGOS Current State

**world-model.ts existente:**
- Snapshot estático: tasks, agents, capabilities, signals
- Health score: 61% (116/189 tasks done)
- Mermaid graph generation
- P0 blockers identification

**GAPs para AGI identificados:**
- Sem simulação ("e se...")
- Sem causalidade (por que things happen)
- Sem reasoning LLM local
- Sem guardrails éticos
- Sem counterfactuals
- Sem planning MPC

---

## Decisões Tomadas

1. **Modelo próprio vs Fine-tuning?** → **Fine-tuning de base existente** (Opção B recomendada)
   - Custo: $100-500 (LoRA) vs $10K-100K (treinamento from scratch)
   - Hardware 24GB VRAM suficiente

2. **Qual modelo base?** → **Qwen2.5-14B** (planner) + **Hermes-3-8B** (executor) + **Qwen3Guard-4B** (safety)

3. **Prioridade P0:** Setup hardware + integração local LLM → WM-001/002

4. **Ethics first:** Qwen3Guard integrado antes de capabilities avançadas → WM-009 P2

---

## Roadmap Resumido

| Fase | Timeline | Key Deliverables | Hardware |
|------|----------|------------------|----------|
| **P0 — Foundation** | 2-4 semanas | Local LLM setup, reasoning integration, capability suggestions | 16GB VRAM OK |
| **P1 — Enhanced** | 2-3 meses | Dynamics model, causal discovery, counterfactuals, MPC | 24GB VRAM recomendado |
| **P2 — Ethics** | 3-4 meses | Qwen3Guard, constitutional rules, value alignment, intervention | 24GB VRAM |
| **P3 — AGI** | 6-12 meses | Auto-observation, auto-modification, long-horizon planning | 48GB ideal, 24GB mínimo |

---

## Hardware Recomendado (16-24GB VRAM)

**Config 24GB (RTX 3090/4090/A5000):**
```
Planner: Qwen2.5-14B-Instruct (~10GB)
Executor: Hermes-3-8B (~6GB)
Safety: Qwen3Guard-4B (~5GB)
Total: ~21GB (4-bit quantization)
```

**Config 16GB:**
```
Single model: Qwen2.5-7B (~8GB) ou Hermes-3-8B (~6GB)
Safety via API (cloud)
```

**Frameworks:** llama.cpp, Ollama, vLLM, Axolotl, Unsloth

---

## Métricas de Sucesso Definidas

| Métrica | Baseline | Target 6 meses |
|---------|----------|----------------|
| Blockers detectados proativamente | 0% | 80% |
| Sugestões de agent composition aceitas | N/A | 70% |
| Decisões com ethics check | 0% | 100% |
| Hardware utilizado | Cloud APIs | 80% local |
| Latency de planning | Manual (horas) | < 5 min |

---

## Próximos Passos Imediatos (P0)

1. **Confirmar hardware:** Qual GPU específica (RTX 3090/4090/A5000)?
2. **Priorizar:** Focar em WM-001/002 (local LLM) ou HERMES-001 (cloud primeiro)?
3. **Setup Ollama/vLLM:** Instalar e testar Qwen2.5-7B
4. **Dataset:** Exportar tasks + handoffs para fine-tuning futuro

---

## Arquivos Criados/Modificados

**NEW:**
- `docs/strategy/WORLD_MODEL_SSOT.md` — SSOT completo (8.5KB)

**UPDATED:**
- `TASKS.md` — Tasks WM-001..WM-016 adicionadas (P0/P1/P2/P3)

---

## Contexto de Sessão

**Tokens usados:** ~15K em research + ~5K em documentação  
**Context tracker:** 220/280 HIGH  
**Commits pendentes:** SSOT document, TASKS.md updates  

**Recomendação:** Executar commit após revisão do SSOT.

---

*Signed: cascade-agent — 2026-04-03T13:00:00Z*
