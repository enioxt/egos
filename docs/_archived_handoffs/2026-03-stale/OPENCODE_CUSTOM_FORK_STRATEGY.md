# OpenCode Custom Fork Strategy — EGOS + FORJA Integration

**Date:** 2026-03-23  
**Status:** Strategic Planning  
**Objective:** Create custom EGOS-powered OpenCode fork for production use

---

## 🎯 Executive Summary

**Tese:** OpenCode é open-source. Podemos:
1. ✅ Forkar e customizar completamente
2. ✅ Integrar EGOS orchestration no núcleo
3. ✅ Usar MCPs do EGOS diretamente
4. ✅ Adicionar Skills customizados para Forja
5. ✅ Rodar Sonnet 4.6 + Alibaba em paralelo
6. ✅ Ter governança própria (ATRiAN, pre-commit)

**Até que ponto?** → Praticamente ilimitado. É open-source MIT.

**Risco:** Manutenção de upstream. **Solução:** Modular design (plugins vs core changes).

---

## 📊 OpenCode Architecture (O Que Temos)

### Camadas:

```
┌─────────────────────────────────┐
│   TUI / Web / IDE / CLI         │  ← Interface
├─────────────────────────────────┤
│   SDK (@opencode-ai/sdk)        │  ← Programmatic API
├─────────────────────────────────┤
│   Server (@opencode-ai/server)  │  ← Core orchestration
├─────────────────────────────────┤
│   Providers (Claude, Alibaba)   │  ← LLM routing
├─────────────────────────────────┤
│   Tools + MCPs + Plugins        │  ← Extensibility
├─────────────────────────────────┤
│   Config (@opencode-ai/config)  │  ← Governance
└─────────────────────────────────┘
```

### O Que Podemos Customizar:

| Layer | Customizable | Effort | Impact |
|-------|-------------|--------|--------|
| TUI/Web | ✅ Yes | High | UI/UX |
| SDK | ✅ Yes | Medium | Integrations |
| Server | ✅ Yes (plugin-based) | High | Core behavior |
| Providers | ✅ Yes (add new ones) | Medium | LLM routing |
| Tools | ✅ Yes (completely) | Low | Functionality |
| MCPs | ✅ Yes (register custom) | Low | Capabilities |
| Config | ✅ Yes (extend schema) | Low | Governance |

---

## 🚀 Proposed Architecture: EGOS + OpenCode Fusion

### Strategy: "Modular Injection" (Não Fork Destrutivo)

```
anomalyco/opencode (upstream)
    ↓
    └─→ @enioxt/opencode-egos (fork)
            ├── packages/core/       ← ORIGINAL (sync com upstream)
            ├── packages/egos/       ← CUSTOMIZAÇÃO (governança EGOS)
            ├── packages/forja/      ← CUSTOMIZAÇÃO (skills Forja)
            ├── packages/orchestration/ ← EGOS kernel integration
            └── .guarani/            ← EGOS governance DNA

```

**Vantagens:**
- ✅ Fácil sincronizar com upstream
- ✅ Modular (cada customização é um package)
- ✅ Governança clara (o que é EGOS vs OpenCode)
- ✅ Testável isoladamente

---

## 📦 O Que Criar

### 1. Package: `@enioxt/opencode-egos` (Fork/Wrapper)

**Location:** `/home/enio/opencode-egos/`

**Estrutura:**
```bash
opencode-egos/
├── packages/
│   ├── core/                      # Symlink/copy de anomalyco/opencode
│   │   └── server/
│   │       └── src/
│   │           └── egos-provider/  ← NOVO: EGOS-specific logic
│   ├── egos/                      # NOVO: EGOS integration
│   │   ├── src/
│   │   │   ├── mcp-registry.ts    # Registrar MCPs do EGOS
│   │   │   ├── skill-loader.ts    # Carregar skills
│   │   │   ├── orchestration.ts   # EGOS orchestration kernel
│   │   │   └── governance-enforcer.ts # ATRiAN + pre-commit
│   │   └── package.json
│   ├── forja/                     # NOVO: Forja-specific extensions
│   │   ├── src/
│   │   │   ├── tools/            # Custom tools para Forja
│   │   │   ├── skills/           # Skills para FORJA tarefas
│   │   │   ├── agents/           # Agent configs
│   │   │   └── models.ts         # Forja model routing
│   │   └── package.json
│   └── orchestration/             # NOVO: Link direto ao EGOS kernel
│       └── src/
│           └── index.ts          # Export do EGOS orchestration
├── .guarani/                      # Symlink para /home/enio/egos/.guarani/
├── opencode.json                  # Config customizado
├── .windsurfrules                 # Governance
└── package.json
```

---

## 🔌 Integration Points (Onde Injetar EGOS)

### 1. **MCP Registry** ← Registrar MCPs do EGOS

**Arquivo:** `packages/egos/src/mcp-registry.ts`

```typescript
// Registro centralizado de MCPs EGOS
export const EGOS_MCPs = {
  'sequential-thinking': {
    type: 'local',
    command: ['bun', 'x', '@modelcontextprotocol/server-sequential-thinking'],
    enabled: true,
  },
  'exa-search': {
    type: 'remote',
    url: 'https://mcp.exa.ai',
    enabled: true,
  },
  'memory-learning': {
    type: 'local',
    command: ['bun', 'x', '@modelcontextprotocol/server-memory'],
    enabled: true,
  },
  'forja-tools': {
    type: 'local',
    command: ['bun', 'run', './packages/forja/mcp-server.ts'],
    enabled: true,
  },
};

// No opencode.json, registra automaticamente:
export function injectEGOSMCPs(config: OpenCodeConfig) {
  return {
    ...config,
    mcp: {
      ...EGOS_MCPs,
      ...config.mcp, // User can override
    },
  };
}
```

### 2. **Provider Routing** ← Sonnet 4.6 + Alibaba

**Arquivo:** `packages/egos/src/orchestration.ts`

```typescript
import { LLMOrchestrator } from '/home/enio/egos/packages/shared/src/llm-orchestrator.ts';

export const EGOS_PROVIDER_ROUTING = {
  // Tarefas complexas → Sonnet 4.6
  'complex-feature': {
    model: 'anthropic/claude-sonnet-4.6',
    maxTokens: 4000,
    temperature: 0.3,
  },
  // Tarefas rápidas → Alibaba (barato)
  'quick-fix': {
    model: 'alibaba/qwen-plus',
    maxTokens: 1000,
    temperature: 0.2,
  },
  // Default → Gemini (free)
  'default': {
    model: 'google/gemini-2.0-flash-001',
    maxTokens: 2000,
    temperature: 0.3,
  },
};

// Integra na seleção de modelo do OpenCode
export function selectEGOSModel(taskComplexity: string, context: any) {
  const route = EGOS_PROVIDER_ROUTING[taskComplexity] || EGOS_PROVIDER_ROUTING.default;
  return route;
}
```

### 3. **Skill Loader** ← Carregar Skills Customizados

**Arquivo:** `packages/forja/src/skills/index.ts`

```typescript
import type { AgentSkill } from '@opencode-ai/sdk';

export const FORJA_SKILLS: Record<string, AgentSkill> = {
  'whatsapp-integration': {
    name: 'WhatsApp Integration',
    description: 'Integrar Evolution API',
    instructions: `
      Use este skill quando implementar WhatsApp.
      - Considere Multi-tenant context
      - Verifique ATRiAN rules
      - Teste com 2+ tenants
    `,
  },
  'email-pipeline': {
    name: 'Email Pipeline',
    description: 'Implementar Gmail + LLM classification',
    instructions: `...`,
  },
  'lgpd-compliance': {
    name: 'LGPD Compliance',
    description: 'Garantir compliance LGPD',
    instructions: `...`,
  },
};

// No agent config (AGENTS.md), referencia:
export function injectForjaSkills(config: any) {
  return {
    ...config,
    skills: FORJA_SKILLS,
  };
}
```

### 4. **Governance Enforcer** ← ATRiAN + Pre-commit

**Arquivo:** `packages/egos/src/governance-enforcer.ts`

```typescript
// Hook no pre-commit do OpenCode
export async function enforceEGOSGovernance(changes: FileChange[]) {
  return {
    // 1. Rodar ATRiAN filter
    atrian: await runATRiAN(changes),
    
    // 2. Verificar regras .windsurfrules
    rules: await verifyWindsurfRules(changes),
    
    // 3. Validar tipos TypeScript
    typecheck: await runTypeCheck(changes),
    
    // 4. Checar frozen zones
    frozen: await checkFrozenZones(changes),
    
    // 5. Verificar PII
    pii: await scanForPII(changes),
  };
}
```

---

## 🛠️ Implementation Roadmap

### Phase 1: Setup (1 dia)
- ✅ Clonar anomalyco/opencode
- ✅ Criar packages/egos, packages/forja
- ✅ Configurar package.json dependencies
- ✅ Setup build pipeline (Bun)

### Phase 2: Integration (2 dias)
- ✅ Injetar MCP registry EGOS
- ✅ Injetar provider routing (Sonnet + Alibaba)
- ✅ Injetar governance enforcer
- ✅ Injetar skills Forja

### Phase 3: Customization (3 dias)
- ✅ Criar custom tools para Forja
- ✅ Criar MCP server customizado (Forja-specific)
- ✅ Configurar AGENTS.md do projeto
- ✅ Testar com Sonnet 4.6 + MCPs

### Phase 4: Production (5 dias)
- ✅ Validar com human-in-the-loop
- ✅ Integrar com CI/CD
- ✅ Deploy em ~/.egos/opencode
- ✅ Documentar para time

---

## 🎮 Como Usar (After Implementation)

### Cenário 1: Tarefa Complexa com MCPs

```bash
# Em /home/enio/forja/
opencode-egos

# Prompt:
/task --complexity high --model sonnet-4.6 "Implemente FORJA-020 WhatsApp"

# O sistema vai:
# 1. Ativar sequential-thinking MCP
# 2. Ativar memory MCP
# 3. Carregar skill 'whatsapp-integration'
# 4. Executar com Sonnet 4.6 (context 200k)
# 5. Enforçar ATRiAN + pre-commit
```

### Cenário 2: Rápido com Alibaba

```bash
# Prompt:
/quick "Corrigir bug em chat route"

# O sistema vai:
# 1. Usar Alibaba Qwen (rápido + barato)
# 2. Max 1000 tokens
# 3. Temperatura 0.2 (determinístico)
```

### Cenário 3: Com Context Multi-Repo

```bash
# Workspace unificado já aberto:
code egos-unified.code-workspace

# OpenCode vê EGOS + Forja:
opencode-egos

# @context pode referenciar ambos:
"Using @/home/enio/egos/.guarani/ governance,
 implemente @/home/enio/forja/FORJA-020"
```

---

## ⚠️ Risks & Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Upstream breaking changes | Medium | Modular design + version pinning |
| Context bloat (MCPs) | High | Per-agent MCP configuration |
| Token cost (Sonnet 4.6) | Medium | Usage tracking + fallback to Alibaba |
| Governance conflicts | Low | Clear .guarani/ rules + enforcement |

---

## 💰 Cost Breakdown

### Before (Current State):
- OpenCode Zen (free tier) → limited
- Fallback to OpenRouter → pay-per-token

### After (EGOS Custom Fork):
- **Sonnet 4.6:** $0.003/1K in, $0.015/1K out (complex tasks)
- **Alibaba Qwen:** $0.0005/1K (quick tasks) ← 6x cheaper
- **Gemini Flash:** FREE (default fallback)
- **MCPs:** Free (local) or included (Exa, Memory)

**Expected:** 60-70% cost reduction vs current.

---

## 🔐 Security Considerations

1. **Secrets Management:**
   - Store API keys in `~/.opencode/secrets`
   - Never commit `.env` files
   - Use `{env:VAR_NAME}` syntax in config

2. **Governance:**
   - All commits go through ATRiAN filter
   - Pre-commit validates PII scanning
   - Frozen zones protected

3. **Multi-Tenant Context:**
   - Each workspace can have its own AGENTS.md
   - Forja workspace uses FORJA-specific skills
   - EGOS workspace uses EGOS orchestration

---

## 📝 Decision Points

### ❓ Q1: Do we fork or create wrapper?
**Answer:** Wrapper approach (modular).
- **Why:** Easy to sync with upstream, clean separation.

### ❓ Q2: Which MCPs to include?
**Answer:** Start with 3:
1. sequential-thinking (complex reasoning)
2. exa-search (research)
3. memory (learning from sessions)

### ❓ Q3: Sonnet 4.6 or wait for 5.0?
**Answer:** Use 4.6 now.
- **Why:** 200k context available today, production-ready, cost-effective.

### ❓ Q4: How to manage governance?
**Answer:** Symlink .guarani/ directory.
- **Why:** Single source of truth, automatic sync.

---

## ✅ Next Steps

1. **Create repo:** `/home/enio/opencode-egos/`
2. **Clone upstream:** `git clone https://github.com/anomalyco/opencode.git`
3. **Create packages/egos:** With MCP registry + provider routing
4. **Create packages/forja:** With skills + custom tools
5. **Test integration:** With workspace unificado
6. **Deploy:** Via bun build + ~/.egos/opencode install

---

## 📚 References

- OpenCode Docs: https://opencode.ai/docs
- SDK: https://opencode.ai/docs/sdk
- MCP Support: https://opencode.ai/docs/mcp-servers
- Skills: https://opencode.ai/docs/skills
- Plugins: https://opencode.ai/docs/plugins
- GitHub: https://github.com/anomalyco/opencode

---

**Created by:** Claude (EGOS Agent)  
**Status:** Ready for review & decision  
**Next:** Awaiting approval to start Phase 1
