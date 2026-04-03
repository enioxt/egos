# EGOS World Model — SSOT Document

> **Version:** 1.0.0 | **Created:** 2026-04-03 | **Status:** P1 — Foundation Active, AGI Roadmap Defined
> **SSOT:** `docs/strategy/WORLD_MODEL_SSOT.md`
> **Code:** `packages/shared/src/world-model.ts`
> **Owner:** enioxt

---

## Executive Summary

O **World Model EGOS** é a camada de inteligência central do framework — um snapshot persistente e queryable do estado do sistema (tasks, agents, capabilities, signals). Inspirado no modelo "company as intelligence" de Jack Dorsey/Block, representa a transição de hierarquia para inteligência: em vez de protocolos de roteamento, usamos um modelo interno do mundo para tomar decisões.

**Estado Atual:** Foundation v1.0 operacional — mantém estado do ecossistema, mas ainda não possui capacidades preditivas/causais de AGI.

**Visão Futura:** EGOS-WorldModel-AGI — modelo treinado localmente (16-24GB VRAM) capaz de simular cenários, raciocinar causalmente, e tomar decisões éticas com guardrails explicitos.

---

## Conceito: O que é um World Model?

> *"A world model is an internal representation of the environment that an AI system maintains to predict future states, plan actions, and understand causality."* — Yann LeCun, 2022

### Definição Formal

Um world model é composto por:

```
M = (E, D, P, R)

Onde:
- E: Encoder (observations → latent state s_t)
- D: Dynamics model (s_t, a_t → s_{t+1}) 
- P: Predictor (rewards, termination, other agents)
- R: Reasoner (causal inference, counterfactuals)
```

### Diferença: Modelo de Linguagem vs World Model

| Aspecto | LLM (Claude, GPT) | World Model |
|---------|-------------------|-------------|
| **Input** | Tokens (texto) | Observações multi-modais |
| **Output** | Texto gerado | Predições de estado futuro |
| **Raciocínio** | Padrão estatístico | Simulação interna |
| **Causalidade** | Limitada | Explicitamente modelada |
| **Ação** | Resposta passiva | Planejamento ativo |
| **Tempo** | Contexto limitado | Horizonte longo |

**Exemplo:**
- LLM: "Se eu empurrar a bola, ela rola." (conhecimento estático)
- World Model: Simula a física da bola rolando, prediz trajetória, considera obstáculos (conhecimento dinâmico)

---

## Importância para o EGOS

### 1. Sistema Navegável (vs Arquivos Espalhados)

> *"Código aberto sem malha vira arquivo espalhado. Código aberto com Mycelium vira sistema navegável."* — ChatGPT

O World Model transforma 7 repositórios fragmentados em um sistema inteligente interconectado:
- Tasks em todos os repos → visão unificada
- Agents distribuídos → capability composition map
- Signals de múltiplas fontes → priorização automática

### 2. Inteligência Proativa (vs Reativa)

**Sem World Model:**
```
Usuário pergunta → Agent reage → Executa tarefa
```

**Com World Model:**
```
World Model escaneia P0 tasks → Detecta stale > 7 dias → Alerta Telegram
                              → Sugere composição de agents → Executa
```

### 3. Tomada de Decisão Ética

Com guardrails explícitos (Qwen3Guard-style):
- Cada ação simulada antes de executada
- Verificação de compliance (LGPD, ética)
- Intervention antes de side effects irreversíveis

### 4. Eficiência de Recursos

Model-based RL é mais sample-efficient:
- Model-free: O(1/ε²) amostras para política ε-ótima
- Model-based: O(1/ε · log(1/ε)) com modelo preciso

---

## Estado Atual EGOS (Foundation v1.0)

### Implementação: `packages/shared/src/world-model.ts`

```typescript
interface WorldModel {
  generated_at: string;           // Timestamp do snapshot
  git_sha: string;               // Versão do código
  
  tasks: {
    total: number;
    done: number;
    p0_blockers: TaskSnapshot[];   // P0 urgentes
    p1_sprint: TaskSnapshot[];     // P1 ativos
    p2_backlog: TaskSnapshot[];   // P2 futuros
  };
  
  agents: {
    total: number;
    active: AgentSnapshot[];       // Agents vivos
    killed: string[];              // Agents mortos
  };
  
  capabilities: {
    total: number;                 // 160 capabilities
    domains: DomainSnapshot[];     // 13 domínios
  };
  
  signals: SignalSnapshot[];       // Gem Hunter, Governance Drift
  
  blockers: string[];              // Human-readable P0
  health_pct: number;              // done/total * 100
}
```

### Capacidades Atuais

| Feature | Status | Descrição |
|---------|--------|-----------|
| Snapshot estático | ✅ | Geração de estado atual do ecossistema |
| Mermaid graph | ✅ | Visualização do estado como grafo |
| P0 blockers | ✅ | Identificação automática de bloqueios |
| Agent roles | ✅ | IC/DRI/Coach taxonomy |
| Signal ingestion | ✅ | Recebe sinais de Gem Hunter, Governance |
| Task parsing | ✅ | Extrai tasks de TASKS.md |
| Health score | ✅ | Porcentagem de tasks completadas |

### Limitações Atuais (GAP para AGI)

| Gap | Impacto | Prioridade |
|-----|---------|------------|
| **Sem simulação** | Não pode prever "e se..." | P0 |
| **Sem causalidade** | Não entende por que things happen | P0 |
| **Sem reasoning LLM** | Apenas estrutura de dados, não raciocínio | P0 |
| **Sem guardrails éticos** | Ações não são validadas antes | P1 |
| **Sem counterfactuals** | Não pode aprender do "não feito" | P1 |
| **Sem planning** | Não gera planos, só reporta estado | P1 |

---

## Roadmap: Do Foundation ao AGI

### Fase 1: Enhanced World Model (Curto prazo — 2-4 semanas)

**Objetivo:** Adicionar reasoning e planning ao modelo existente.

**Tasks:**
```
WM-001: Integrar LLM local (Ollama/LM Studio) ao world-model.ts
  → Usar modelo 7-8B para reasoning sobre o estado
  → Hardware: 16-24GB VRAM suporta Qwen2.5-7B, Hermes-3-8B

WM-002: Implementar capability composition suggestions
  → Dada uma task, sugerir quais agents/capabilities invocar
  → Baseado em histórico de similar tasks

WM-003: Proactive blocker detection (INTEL-006)
  → World model escaneia P0 tasks stale > 7 dias
  → Auto-cria TASKS entries ou alerta Telegram

WM-004: Signal ingestion completo (INTEL-005)
  → Gem Hunter scores > 80 → auto-append signals
  → Detectar correlações entre signals
```

**Hardware:** 16GB VRAM suficiente para:
- Qwen2.5-7B-Instruct (4-bit quantized: ~8GB)
- Hermes-3-Llama-3.1-8B (~10GB)
- Qwen3Guard-8B para safety (~10GB)

### Fase 2: Simulation & Causality (Médio prazo — 2-3 meses)

**Objetivo:** Modelo pode simular cenários e entender causalidade.

**Tasks:**
```
WM-005: Implementar dynamics model básico
  → Dado estado atual + ação hipotética, prediz estado futuro
  → Ex: "Se focarmos 100% em Guard Brasil por 1 semana, qual health_pct?"

WM-006: Causal discovery
  → Aprender relações de causa-efeito do histórico
  → Ex: "Mais agents ativos → mais tasks done?" ou "Gem Hunter signals → novas tasks?"

WM-007: Counterfactual reasoning
  → "O que teria acontecido se tivéssemos feito X em vez de Y?"
  → Valuable para aprender com decisões passadas

WM-008: Model-predictive control para planning
  → Planeja sequências de ações ótimas para atingir goals
  → Ex: caminho ótimo para lançar Guard Brasil
```

**Hardware:** 24GB VRAM recomendado para:
- Dreamer-style world models (13B params)
- Fine-tuning de adapters LoRA (16GB+)

### Fase 3: Ethical Guardrails & Alignment (Médio prazo — 3-4 meses)

**Objetivo:** Garantir que o world model tome decisões alinhadas com valores EGOS.

**Tasks:**
```
WM-009: Integrar Qwen3Guard-style safety classification
  → Três níveis: Safe / Controversial / Unsafe
  → Categorias: Violent, PII, Unethical, etc.

WM-010: EGOS Constitutional Rules embedding
  → Hard-fork law, PRIME DIRECTIVE, frozen zones
  → Bloqueio explícito de ações que violem regras

WM-011: Value alignment via RLHF local
  → Fine-tuning com preferências do usuário (enioxt)
  → ATRiAN principles: Accuracy, Truth, Reversibility, Impact, Accountability, Neutrality

WM-012: Intervention system
  → Pause + human review para ações high-impact
  → Similar ao "circuit breaker" de sistemas financeiros
```

**Hardware:** 16-24GB VRAM suficiente para:
- Qwen3Guard-8B (~10GB)
- LoRA fine-tuning de ethics adapter (~6GB)

### Fase 4: EGOS-WorldModel-AGI (Longo prazo — 6-12 meses)

**Objetivo:** Modelo unificado capaz de operar como AGI minimamente autônomo.

**Visão:**
```
EGOS-AGI = World Model + Intelligence Layer + Atomic Capabilities

Capacidades:
- Auto-observação do próprio estado
- Auto-modificação (melhorar código)
- Planejamento de longo horizonte (meses)
- Aprendizado contínuo de experiências
- Criação de novos agents quando necessário
- Decisões éticas transparentes e auditáveis
```

**Architecture Proposta:**
```
┌─────────────────────────────────────────────────────────┐
│                    EGOS-WorldModel-AGI                   │
├─────────────────────────────────────────────────────────┤
│  Perception Layer (O1)                                  │
│    ├── GitHub API (commits, PRs, issues)               │
│    ├── Filesystem (code, docs, configs)                 │
│    ├── APIs (Guard Brasil, Eagle Eye, etc.)            │
│    └── External (X.com, news, gem-hunter signals)      │
├─────────────────────────────────────────────────────────┤
│  World Model Core (O2)                                  │
│    ├── Latent State Encoder (tasks, agents, context)     │
│    ├── Dynamics Predictor ("e se...")                  │
│    ├── Causal Reasoner (por que...)                    │
│    └── Value Alignment (devemos...)                     │
├─────────────────────────────────────────────────────────┤
│  Intelligence Layer (O3)                                │
│    ├── Planning Module (BRAID-style GRD)                │
│    ├── Agent Composition (quem chamar)                  │
│    └── Execution Monitor (loop de feedback)             │
├─────────────────────────────────────────────────────────┤
│  Action Layer (O4)                                       │
│    ├── Agent Invocation (runner.ts)                     │
│    ├── Code Modification (edit safety)                  │
│    └── Human Interface (Telegram, dashboard)             │
├─────────────────────────────────────────────────────────┤
│  Ethics & Safety (Cross-Cutting)                        │
│    ├── Qwen3Guard (real-time classification)             │
│    ├── Constitutional Check (frozen zones, PRIME)        │
│    └── Intervention System (human-in-the-loop)          │
└─────────────────────────────────────────────────────────┘
```

**Hardware Necessário:**
- 24GB VRAM mínimo para operação fluida
- 48GB+ VRAM ideal para treinamento contínuo
- Alternativa: cloud (RunPod, Vast.ai) para treinamento, local para inference

---

## Modelos de Referência no Mercado

### 1. DeepMind Genie 2 (Google)

**O que faz:** Gera mundos 3D jogáveis a partir de uma imagem. Fundação para agents embodied.

**Relevância para EGOS:** Conceito de "foundation world model" — pré-treinamento em diversos dados, fine-tuning para tarefas específicas.

**Status:** Research, não open-source.

### 2. MuZero (DeepMind)

**O que faz:** Mastered Go, Chess, Atari sem conhecer regras — aprendeu model interno do jogo.

**Key Innovation:** Value-equivalent model (aprende só o necessário para planejamento, não pixel-accurate).

**Relevância para EGOS:** Modelos não precisam ser perfeitos, só úteis para decisão.

### 3. Dreamer v3 (DeepMind)

**O que faz:** Model-based RL que superou métodos model-free no Atari.

**Architecture:** RSSM (Recurrent State-Space Model) + Imagination-based policy.

**Relevância para EGOS:** RSSM pode ser adaptado para estado do EGOS (tasks, agents) em vez de pixels.

### 4. JEPA (Joint Embedding Predictive Architecture) — LeCun

**O que faz:** Aprende representações predizíveis não pixel-level.

**Key Idea:** Prediz em espaço latente abstrato, não pixels (evita compounding error).

**Relevância para EGOS:** Ideal para prever estado do ecossistema (não precisamos simular código pixel a pixel).

### 5. Qwen3Guard (Alibaba)

**O que faz:** Modelo de guardrail de segurança em tempo real.

**Features:**
- Streaming detection (token-by-token)
- Três tiers: Safe / Controversial / Unsafe
- 119 línguas
- Tamanhos: 0.6B, 4B, 8B

**Relevância para EGOS:** Base para WM-009 (ethical guardrails). Já open-source, fácil integrar.

### 6. Hermes-3 (Nous Research)

**O que faz:** Modelo fine-tuned para structured output, tool use, reasoning.

**Relevância para EGOS:** HERMES-001 já planeja usar como BRAID mechanical executor. Pode ser componente do world model.

---

## EGOS-WorldModel: Modelo Próprio?

**Questão Central:** Devemos criar um modelo LLM próprio ou usar modelos existentes?

### Opção A: Foundation Model Próprio (EGOS-LLM)

**Pros:**
- Controle total sobre arquitetura
- Treinado especificamente para código/governance
- Alinhamento perfeito com valores EGOS
- Differentiation no mercado

**Cons:**
- Custo de treinamento alto ($10K-100K)
- Necessita dados proprietários massivos
- Manutenção contínua complexa
- Hardware: mínimo 8xA100 (80GB) para treinamento

### Opção B: Fine-tuning de Modelo Existente (Recomendado)

**Base:** Qwen2.5-14B ou Llama-3.1-70B (quantized)

**Approach:**
1. **Adapter LoRA:** Fine-tune apenas camadas específicas (~$100-500)
2. **Dados:** EGOS codebase, TASKS.md, handoffs, decisions
3. **Hardware:** 24GB VRAM suficiente para fine-tuning LoRA
4. **Ethics:** Qwen3Guard como safety layer adicional

**Pros:**
- Custo acessível
- Base sólida (Qwen/Llama já bons em código)
- Rápido de implementar (2-4 semanas)
- Iterativo (melhorar incrementalmente)

**Cons:**
- Dependência de modelo base
- Limitações arquiteturais herdadas

### Opção C: Hybrid (Recomendado para EGOS)

**Arquitetura:**
```
World Model EGOS = Ensemble de Especialistas

1. Planner/Reasoner: Qwen2.5-14B-Instruct (24GB VRAM)
   → Decisões estratégicas, planning
   
2. Executor: Hermes-3-8B (10GB VRAM)  
   → Tarefas mecânicas, structured output
   
3. Safety: Qwen3Guard-4B (5GB VRAM)
   → Verificação ética em tempo real
   
4. Coder: CodeQwen2.5-7B (8GB VRAM)
   → Geração/modificação de código

Total VRAM: ~24GB (com quantization 4-bit)
```

**Vantagem:** Melhor especialista para cada tarefa, não tenta fazer tudo com um modelo só.

---

## Hardware: 16-24GB VRAM

### Configuração Recomendada para 24GB VRAM

**GPU:** RTX 3090 / RTX 4090 / A5000

**Modelos que cabem:**
| Modelo | Quantização | VRAM | Uso |
|--------|-------------|------|-----|
| Qwen2.5-14B-Instruct | 4-bit | ~10GB | Planner principal |
| Qwen2.5-14B + Qwen3Guard-4B | 4-bit | ~12GB | Planner + Safety |
| Hermes-3-8B | 4-bit | ~6GB | Executor BRAID |
| CodeQwen2.5-7B | 4-bit | ~5GB | Code generation |
| Ensemble (14B+8B+4B) | 4-bit | ~20GB | Full system |

**Configuração 16GB VRAM:**
- Foco em um modelo principal: Qwen2.5-7B ou Hermes-3-8B
- Safety via API (Qwen3Guard cloud) ou modelo menor (0.6B)

### Frameworks Recomendados

| Framework | Propósito | VRAM Optimized |
|-----------|-----------|----------------|
| **llama.cpp** | Inference CPU/GPU | ✅ Very efficient |
| **Ollama** | Easy local LLMs | ✅ Good defaults |
| **vLLM** | High-throughput serving | ✅ PagedAttention |
| **Axolotl** | Fine-tuning LoRA | ✅ QLoRA |
| **Unsloth** | Fast fine-tuning | ✅ 2x faster, 70% less VRAM |

---

## Tasks Atuais Relacionadas

**INTEL-005:** Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals (= GH-050)
**Status:** P1, não iniciado

**INTEL-006:** Proactive blocker detection — world model scans P0 list → creates TASKS entries if blocker stale > 7 days  
**Status:** P1, não iniciado

**INTEL-007:** `--mermaid` output from world-model.ts → embed in /start briefing as ASCII architecture snapshot
**Status:** P1, não iniciado

**HERMES-001:** Wire Hermes-3 as BRAID mechanical executor (OpenRouter free tier, 2h, 30-40% cost savings)
**Status:** P1, não iniciado

**INTEL-008:** DRI auto-assignment — when P0 task has no commit activity for 3 days, auto-flag + Telegram alert
**Status:** P2, não iniciado

**INTEL-009:** Capability composition map — intelligence layer dynamically suggests which agents to invoke for a given task
**Status:** P2, não iniciado

**INTEL-010:** World model diff — compare snapshots to detect regression (tasks going from [x] back to [ ])
**Status:** P2, não iniciado

---

## Novas Tasks Propostas (World Model AGI)

### P0 — Foundation (Próximas 2 semanas)

**WM-001:** Setup hardware local LLM (Ollama/LM Studio)
- Instalar Qwen2.5-7B ou Hermes-3-8B na máquina 24GB VRAM
- Configurar API endpoint local
- Testar latency vs cloud

**WM-002:** Integrate local LLM to world-model.ts
- Extender interface para suportar reasoning queries
- Primeiro uso: explain health_pct, suggest priorities

**WM-003:** Capability composition suggestions
- Input: task description
- Output: lista de agents/capabilities recomendados
- Base: embedding similarity com tasks históricas

### P1 — Enhanced (2-3 meses)

**WM-004:** Implementar dynamics model básico (simulação)
**WM-005:** Causal discovery de relações no histórico EGOS
**WM-006:** Counterfactual reasoning ("o que teria acontecido se...")
**WM-007:** Model-predictive control para planning ótimo

### P2 — Ethics (3-4 meses)

**WM-008:** Integrar Qwen3Guard para safety classification
**WM-009:** Constitutional rules embedding (frozen zones, PRIME DIRECTIVE)
**WM-010:** Value alignment training local (ATRiAN principles)
**WM-011:** Intervention system com human-in-the-loop

### P3 — AGI (6-12 meses)

**WM-012:** Auto-observação (world model que monitora a si mesmo)
**WM-013:** Auto-modificação (melhorar próprio código)
**WM-014:** Planejamento longo horizonte (quarter/year goals)
**WM-015:** Criação automática de agents quando necessário

---

## Métricas de Sucesso

| Métrica | Baseline (Hoje) | Target (6 meses) |
|---------|-----------------|------------------|
| Tasks identificados corretamente | 100% | 100% |
| Blockers detectados proativamente | 0% | 80% |
| Sugestões de agent composition aceitas | N/A | 70% |
| Simulações de cenários úteis | N/A | 60% |
| Decisões com ethics check | 0% | 100% |
| Intervenções humanas necessárias | 100% | 20% |
| Latency de planning | Manual (horas) | < 5 min |
| Hardware utilizado | Cloud APIs | 80% local |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Hallucinations em planning | Alta | Alto | Qwen3Guard + human-in-the-loop |
| Custo de hardware 24GB VRAM | Média | Médio | Cloud fallback para treinamento |
| Over-reliance em automação | Média | Alto | Circuit breakers, intervention system |
| Alignment drift | Média | Alto | ATRiAN checks, regular audits |
| Competição com OpenAI/Google | Alta | Baixo | Foco em governance-as-code (moat EGOS) |

---

## Referências

### Papers Fundamentais
1. Ha & Schmidhuber, "World Models" (2018)
2. Hafner et al., "Dream to Control" (2019)
3. Schrittwieser et al., "MuZero" (Nature 2020)
4. Hafner et al., "Mastering Diverse Domains through World Models" (2023)
5. LeCun, "A Path Towards Autonomous Machine Intelligence" (2022)

### Implementações de Referência
- **Dreamer v3:** https://github.com/danijar/dreamer
- **Genie 2:** https://deepmind.google/discover/blog/genie-2 (research only)
- **Qwen3Guard:** https://github.com/QwenLM/Qwen3Guard
- **Hermes-3:** https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B

### Documentação EGOS Relacionada
- `packages/shared/src/world-model.ts`
- `docs/world-model/current.json`
- `AGENTS.md` (Block Intelligence Model section)
- `docs/CAPABILITY_REGISTRY.md`

---

## Próximos Passos Imediatos

1. **Confirmar hardware:** Qual GPU específica (RTX 3090/4090/A5000)?
2. **Priorizar:** Focar em WM-001/002 (local LLM) ou HERMES-001 (cloud primeiro)?
3. **Dados:** Coletar dataset de tasks + decisions para fine-tuning futuro
4. **Infra:** Setup Ollama ou vLLM local?

---

**Document Owner:** enioxt  
**Last Updated:** 2026-04-03  
**Next Review:** 2026-04-17 (após hardware setup)
