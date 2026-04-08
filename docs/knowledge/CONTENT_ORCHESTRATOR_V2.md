# Content Orchestrator v2 — OpenMontage + OpenScreen Deep Integration

> **SSOT:** Este documento | **Versão:** 1.0.0 | **Atualizado:** 2026-04-08

## Visão Geral

Sistema agentic de produção de conteúdo (vídeos + demos) integrado ao EGOS, combinando:
- **OpenMontage** (AGPL-3.0, 498⭐): 11 pipelines de produção de vídeo AI
- **OpenScreen** (MIT, 8400+⭐): Screen recording profissional open-source

## Contexto

### OpenMontage
- **Criador:** calesthio
- **Pipelines:** 11 pipelines completos, 49 tools, 400+ agent skills
- **Custo por vídeo:** $0.15 - $1.33
- **Exemplos reais:**
  - "The Last Banana" (Pixar-style, 60s): $1.33
  - "Void — Neural Interface" (product ad): $0.69
  - "Afternoon in Candyland" (Ghibli-style): $0.15

### OpenScreen
- **Alternativa a:** Screen Studio ($29/mês)
- **Features:** Auto-zoom, motion blur, animated cursor, webcam overlay
- **Export:** MP4/WebM/GIF, sem watermarks
- **Ideal para:** Demos de produto, tutoriais, walkthroughs

## Arquitetura de Integração

```
┌─────────────────────────────────────────────────────────────┐
│                  EGOS Content Orchestrator                 │
│                     (Comando: egos content)               │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Input: Linguagem natural    │
              │   "Crie vídeo sobre MemPalace" │
              └──────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Meta-prompt Router         │
              │   Decide: video|demo|combined│
              └──────────────────────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  OpenMontage │ │  OpenScreen  │ │   Combined   │
    │  (Video AI)  │ │ (Screen Rec) │ │  (Hybrid)    │
    └──────────────┘ └──────────────┘ └──────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   EGOS Governance Layer      │
              │   • Guard Brasil PII scan    │
              │   • Audit trail              │
              │   • Cost approval gate       │
              └──────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   MemPalace (Wing: content)  │
              │   Room: project-name         │
              └──────────────────────────────┘
```

## OpenMontage Pipelines Detalhados

### 1. Reference Analysis
**Input:** URL de vídeo (YouTube, Shorts, Reels, TikTok) ou descrição
**Output:**
- Pacing analysis (tempo de cortes, ritmo)
- Hook style identification
- Estrutura de atos (3-act structure detectada)
- Tom de voz/estilo visual

**Prompt de exemplo:**
```
"Here's a YouTube Short I love. Make me something like this, but about quantum computing."
```

**Output esperado:**
```
What it keeps: Fast-paced cuts every 2-3s, text-on-screen hooks, dramatic music drops
What it changes: Topic to quantum computing, visual style to educational
```

### 2. Concept Generation
**Input:** Análise da referência + tema desejado
**Output:** 2-3 conceitos diferenciados com:
- Angle único para cada conceito
- Honest tool path (quais ferramentas usar)
- Cost estimate detalhado
- Sample visual description

### 3. Asset Generation
**Imagens:**
- FLUX (via fal.ai)
- DALL-E 3
- gpt-image-1 (OpenAI)

**Vídeos:**
- Veo (Google)
- Kling v3 (via fal.ai)

**Custo estimado:** $0.05 - $0.30 por asset

### 4. Voice/Narration
**Opções:**
- Google Chirp3-HD (mais natural)
- ElevenLabs (mais controle)
- OpenAI TTS (mais barato)

**Recursos:**
- Auto-detecção de idioma
- Ajuste de velocidade
- Pauses naturais

### 5. Music
**Fontes:**
- Royalty-free auto-sourced
- Energy offset detection (sincronia com corte)

**Gêneros mapeados automaticamente:**
- Epic/cinematic → Orchestra
- Tech/educational → Electronic/ambient
- Fun/light → Upbeat/indie

### 6. Editing (Remotion)
**Composição automatizada:**
- TikTok-style word-level captions (WhisperX)
- Ken Burns effects (zoom/pan)
- Transições suaves
- Particle overlays (se solicitado)

### 7. Review
**Agente revisora avalia:**
- Cost vs budget
- Quality score (LLM-as-judge)
- Brand alignment
- Ajustes solicitados (se necessário)

## OpenScreen Capabilities

### Core Features
- **Auto-zoom:** Segue cursor automaticamente com suavidade
- **Motion blur:** Transições cinematográficas
- **Animated cursor:** Cursor customizado para visibilidade
- **Webcam overlay:** Picture-in-picture opcional
- **No watermarks:** Export limpo
- **No subscription:** 100% free

### Use Cases
1. **Product Demo:** Walkthrough de funcionalidade EGOS
2. **Tutorial:** Como usar feature específica
3. **Bug Report:** Screen recording de issue
4. **Release Notes:** Quick demo de novo release

### Integration Points
- Trigger: `egos content "demo do Guard Brasil" --type=demo`
- Pré-configuração: resolução, zoom behavior, cursor style
- Pós-gravação: auto-upload para MemPalace wing "content"

## EGOS Governance Wrapper

### Guard Brasil Integration
```typescript
// Antes de gerar qualquer script ou asset:
const scan = await guard.inspect({
  content: generatedScript,
  purpose: 'video-script-public'
});

if (scan.findings.length > 0) {
  // Redact PII antes de prosseguir
  script = guard.redact(generatedScript, scan.findings);
}
```

### Audit Trail
Todo pipeline registra:
- Timestamp de cada stage
- Modelos/tools usados
- Custos incurridos
- Quem aprovou (agent ou humano)
- Final output hash

### Cost Approval Gate
```typescript
const estimate = await openmontage.estimate(prompt);

if (estimate.total > COST_THRESHOLD) {
  // Envia para aprovação Telegram/WhatsApp
  await notifyApprovalRequired(estimate);
  await waitForApproval();
}
```

## Comandos EGOS

### egos content
```bash
# Vídeo completo (OpenMontage)
egos content "Explique MemPalace para desenvolvedores" --type=video --budget=$2.00

# Demo screen recording (OpenScreen)
egos content "Demo do novo dashboard EGOS" --type=demo --duration=60s

# Combined (vídeo + demo injetado)
egos content "Tutorial completo Guard Brasil" --type=combined --budget=$3.00
```

### Parâmetros
| Flag | Descrição | Padrão |
|------|-----------|--------|
| `--type` | video, demo, combined | video |
| `--budget` | Max custo em USD | $2.00 |
| `--duration` | Duração alvo | 60s |
| `--style` | cinematic, tutorial, product | auto |
| `--voice` | chirp3, elevenlabs, openai | chirp3 |
| `--reference` | URL de referência | none |

## Workflows Avançados

### Auto-Content Calendar
```
Trigger: Novo release EGOS detectado
↓
Action: Gera vídeo explicativo automaticamente
↓
Review: Agente valida qualidade
↓
Approval: Notificação Telegram com preview
↓
Publish: Post no X com thread automática (X-COM integration)
```

### Content Variants
Para cada conceito, gerar:
1. **Short:** 30s (TikTok/Reels)
2. **Medium:** 2min (YouTube/LinkedIn)
3. **Long:** 5min (Documentação/tutorial)

### A/B Testing Framework
```
Gerar 2 variações de thumbnail/título
↓
Publicar ambas no X (alternadas)
↓
Medir CTR e engagement (24h)
↓
Reportar winner
↓
Usar winner para futuros vídeos similares
```

## Templates Pré-Built

### 1. Product Release
```yaml
structure:
  - Hook: Problem statement (3s)
  - Solution: Feature showcase (20s)
  - Demo: Quick walkthrough (30s)
  - CTA: Como começar (7s)
style: cinematic
music: upbeat-electronic
```

### 2. Feature Demo
```yaml
structure:
  - Intro: Contexto (5s)
  - Demo: Screen recording (45s)
  - Outro: Value proposition (10s)
type: openscreen
voice: none ( captions only )
```

### 3. Tutorial
```yaml
structure:
  - Overview: O que vamos aprender (10s)
  - Step 1: Setup (30s)
  - Step 2: Implementation (60s)
  - Step 3: Verification (20s)
  - Recap: Key takeaways (10s)
type: combined
music: ambient
```

### 4. Case Study
```yaml
structure:
  - Hook: Cliente + problema (10s)
  - Solution: EGOS approach (20s)
  - Results: Metrics (15s)
  - Testimonial: Quote (10s)
style: professional
music: corporate
```

## Performance Analytics

### Métricas Trackadas
- Views (X, YouTube, LinkedIn)
- Engagement rate (likes, shares, comments)
- Watch time / completion rate
- Cost per view
- CTR (click-through rate)
- Conversion (se aplicável)

### Dashboard HQ
Visualizações:
- Content calendar (próximos 30 dias)
- Performance por tipo (video vs demo)
- ROI de conteúdo (cost vs engagement)
- Top performing templates
- A/B test results

## Integrações EGOS

### MemPalace
```typescript
// Salvar todo output
await mempalace.retain({
  wing: 'content',
  room: 'project-guard-v2.5',
  data: {
    scripts: generatedScripts,
    assets: assetUrls,
    config: pipelineConfig,
    finalVideo: videoUrl,
    analytics: performanceData
  }
});
```

### Event Bus
```typescript
// Tópicos publicados
eventBus.publish('content.pipeline.started', { projectId, type, budget });
eventBus.publish('content.asset.generated', { assetType, cost, url });
eventBus.publish('content.completed', { projectId, finalVideo, totalCost });
eventBus.publish('content.demo.recorded', { projectId, duration, path });
```

### X-COM (X.com Automation)
```typescript
// Auto-post após aprovação
await xCom.post({
  content: videoUrl,
  thread: autoGeneratedThread,
  schedule: 'optimal_time', // via x-smart-scheduler
  approval: 'required' // aguarda aprovação manual
});
```

## Referências

- **OpenMontage GitHub:** https://github.com/calesthio/OpenMontage
- **OpenScreen Docs:** https://mintlify.com/siddharthvaddem/openscreen/
- **OpenScreen Review (PyShine):** https://pyshine.com/OpenScreen-Free-Screen-Recording-Studio/
- **AI Heartland (Japonês):** https://ai-heartland.com/tool/openmontage/

## Tasks Relacionadas

- CONTENT-001..014 (TASKS.md §Content Orchestrator v2)

---

**Nota:** Este sistema permite que o EGOS produza conteúdo de alta qualidade (vídeos explicativos + demos profissionais) de forma automatizada, governada e escalável, com custos controlados ($0.15-$3.00 por vídeo).
