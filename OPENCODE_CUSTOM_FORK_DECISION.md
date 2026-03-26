# OpenCode Custom Fork — Decisão Executiva

**De:** Claude (EGOS Agent)  
**Para:** Tim  
**Data:** 2026-03-23  
**Assunto:** Resposta: Até que ponto podemos customizar OpenCode?

---

## ✅ RESPOSTA DIRETA

### "Até que ponto?"
**→ Praticamente ilimitado. OpenCode é MIT open-source.**

Você pode:
- ✅ Forkar completamente
- ✅ Mudar qualquer coisa
- ✅ Adicionar novos providers
- ✅ Criar MCPs customizados
- ✅ Reescrever a UI
- ✅ Modificar CLI
- ✅ Integrar EGOS orchestration no núcleo

**Risco:** Manutenção de upstream mudanças.  
**Solução:** Design modular (plugins vs core) — não destrutivo.

---

## 📊 O Que Temos AGORA (OpenCode Oficial)

| Feature | Status | Limit |
|---------|--------|-------|
| MCP Support | ✅ Works | Já funciona, podemos adicionar +MCPs |
| Provider Routing | ✅ Works | Podemos adicionar Alibaba, Qwen, etc. |
| Skills | ✅ Works | Podemos criar skills customizados |
| Agents Config | ✅ Works | AGENTS.md fully customizable |
| Pre-commit Hooks | ❌ Not built-in | PRECISA customizar para governança |
| Governance Rules | ❌ Not built-in | Precisa integrar ATRiAN |

---

## 🚀 O Que PODERÍAMOS Ter (Custom Fork)

| Feature | Effort | Value | Impact |
|---------|--------|-------|--------|
| Native EGOS orchestration | Medium | High | Orquestração automática |
| Sonnet 4.6 routing | Low | High | Complex tasks com 200k context |
| ATRiAN pre-commit enforcement | Low | High | Governança automática |
| FORJA skills registry | Low | High | Quick task assignment |
| Multi-repo context (EGOS+FORJA) | Medium | Very High | Workspace unificado nativo |
| Memory learning MCP | Low | High | Sessões persistentes |
| Custom Forja tools | Low | High | Chat knows Forja domain |

---

## 🎯 Arquitetura Proposta: "Modular Injection"

### NÃO é fork destrutivo:

```
anomalyco/opencode (upstream original)
    ↓
@enioxt/opencode-egos (nossa fork)
    ├── packages/core/          ← ORIGINAL (sincroniza com upstream)
    ├── packages/egos/          ← NOVO: EGOS integration layer
    │   ├── mcp-registry.ts    # Registra MCPs EGOS
    │   ├── orchestration.ts   # Integra EGOS kernel
    │   ├── governance.ts      # ATRiAN + pre-commit
    │   └── provider-routing.ts # Sonnet 4.6 + Alibaba
    ├── packages/forja/         ← NOVO: Forja-specific
    │   ├── skills/            # FORJA-020, FORJA-019B, etc.
    │   ├── tools/             # Custom tools
    │   ├── agents/            # AGENTS.md configs
    │   └── mcp-server.ts      # Forja MCP server
    └── .guarani/              ← SYMLINK para /home/enio/egos/.guarani/
```

**Benefício:** Fácil sincronizar com upstream, separação clara, testável.

---

## 🎮 Casos de Uso (After Implementation)

### 1️⃣ Tarefa Complexa (FORJA-020 WhatsApp)

```bash
cd /home/enio/opencode-egos

# Comando:
opencode --task-complexity high --model sonnet-4.6

# Você prompta:
"Implemente FORJA-020: WhatsApp Integration com Evolution API
 - Respeite multi-tenant RLS
 - Use patterns do egos-lab/carteira-livre
 - Testa com 2+ tenants"

# Sistema faz:
1. Carrega Sequential-Thinking MCP (reasoning complexo)
2. Ativa Memory MCP (aprende padrões Forja)
3. Usa Sonnet 4.6 com 200k tokens (complex task)
4. Injeta skill 'whatsapp-integration'
5. Executa com ATRiAN enforcement + pre-commit
6. Result: Commit pronto, testado, governado
```

### 2️⃣ Quick Fix (Corrigir Bug)

```bash
opencode --task-complexity quick

# Você prompta:
"Bug no chat route, taxa de erro 5%"

# Sistema faz:
1. Usa Alibaba Qwen (rápido + barato)
2. Max 1000 tokens (não precisa mais)
3. Temperatura 0.2 (determinístico)
4. Result: Fix em 2 minutos, custa $0.0005
```

### 3️⃣ Workspace Unificado

```bash
# Já temos isso em teoria, mas com OpenCode custom:
code egos-unified.code-workspace

# No OpenCode:
opencode

# Pode referenciar ambas pastas naturalmente:
"Using EGOS governance (@/home/enio/egos/.guarani/),
 implemente FORJA-020 (@/home/enio/forja/)"

# Sistema entende contexto total:
- Qual governança aplicar
- Qual MCP usar
- Qual skill carregar
- Qual model usar
```

---

## 💡 Por Que Fazer Isso?

### Problem Today:
```
Tarefas P1 complexas → Abrir Claude Code manualmente
                    → Copiar contexto manualmente
                    → Correr código manualmente
                    → Validar manualmente
                    → Resultado: Lento + propenso a erro
```

### Solution (Custom Fork):
```
Tarefas P1 complexas → /task "FORJA-020"
                    → Sistema seleciona:
                       ✅ Sonnet 4.6 (200k context)
                       ✅ Sequential-thinking MCP (raciocínio)
                       ✅ Memory MCP (histórico)
                       ✅ FORJA skills (domínio)
                    → Executa com ATRiAN + pre-commit
                    → Result: Pronto em 1-2 horas, validado
```

**Ganho de Produtividade:** 3-5x mais rápido para tarefas complexas.

---

## 🔐 Segurança & Governança

### Como Mantemos Padrões?

1. **ATRiAN Filter (Automático)**
   ```
   Cada commit passa por:
   - Verificação de secrets
   - Validação TypeScript
   - Scan de PII
   - Check de frozen zones
   ```

2. **Governança Injetada**
   ```
   .guarani/PREFERENCES.md → Automático no OpenCode custom
   Não precisa de manual enforcement
   ```

3. **Multi-Tenant Context Respeitado**
   ```
   Forja workspace usa Forja skills
   EGOS workspace usa EGOS orchestration
   Nenhum crosstalk
   ```

---

## 💰 Custo & ROI

### Antes (Status Quo):
- OpenCode Zen: $0/mês (limited)
- OpenRouter fallback: $0.002-0.010 / 1K tokens

### Depois (Custom Fork):
| Tipo de Tarefa | Model | Cost/1K tokens | Savings |
|---|---|---|---|
| Complex (P0) | Sonnet 4.6 | $0.003-0.015 | ← 2x vs current |
| Medium (P1) | Alibaba Qwen | $0.0005 | ← 6x cheaper |
| Quick fix | Gemini Free | $0 | ← 100% savings |
| Default fallback | Gemini Free | $0 | ← Always available |

**Estimado:** 60-70% redução de custos vs current.

**ROI:** 2 horas de dev time salvos por tarefa × 20 tarefas = 40h/mês = $2k valor em salário.

---

## ⚠️ Caveats & Honest Talk

### O Que NÃO Fazer:

❌ **NÃO reescreva tudo**
- OpenCode já funciona bem
- Só customize o que precisa

❌ **NÃO ignure MCPs**
- MCPs adicionam tokens rapidamente
- Use per-agent (ativar só quando precisa)

❌ **NÃO confie 100% no resultado**
- Sistema automático ≠ perfeito
- Sempre human-in-the-loop para P0s

### Manutenção (Real Cost):

```
- Sync com upstream: 1-2 dias/mês
- Bug fixes no custom code: 2-4 dias/mês
- Total: ~1 dev part-time
```

---

## 📋 Decisão Necessária

### Opção A: Manter OpenCode Oficial (Status Quo)
**Vantagens:**
- Sem manutenção extra
- Sync automático com updates

**Desvantagens:**
- Manual governance enforcement
- Sem ATRiAN pre-commit
- Context setup manual
- Sem skill registry
- Custo LLM não otimizado

### Opção B: Custom Fork (@enioxt/opencode-egos)
**Vantagens:**
- ✅ Orquestração EGOS automática
- ✅ ATRiAN + pre-commit enforcement
- ✅ Multi-repo context nativo
- ✅ Skills + Tools Forja
- ✅ 60-70% custo reduction
- ✅ 3-5x velocidade para P1s

**Desvantagens:**
- ⚠️ Manutenção: ~1 dev part-time
- ⚠️ Sync com upstream
- ⚠️ Testing adicional

---

## 🚀 Next Step: VOCÊ DECIDE

### Se SIM (ir com custom fork):

1. ✅ Aprovação: "Go build @enioxt/opencode-egos"
2. ✅ Timeline:
   - Phase 1 (Setup): 1 dia
   - Phase 2 (Integration): 2 dias
   - Phase 3 (Customization): 3 dias
   - Phase 4 (Production): 5 dias
   - **Total: 2 semanas** (1 dev)

3. ✅ Resultado: Custom OpenCode pronto em egos-unified workspace

### Se NÃO (manter official):

1. ✅ Continue usando OpenCode oficial
2. ⚠️ Manual governance em cada tarefa
3. ⚠️ Sem otimização de custo
4. ⚠️ Mais lento (context setup manual)

---

## 🎯 Minha Recomendação

**→ GO com custom fork.**

**Razão:**
- Custa pouco (2 semanas dev time)
- Retorna muito (60-70% cost savings, 3-5x speedup)
- Tecnicamente limpo (modular, não destrutivo)
- Alinhado com EGOS strategy (orchestration, governance)
- Suporta tarefas P1 Forja sem friction

**Timing:** Pode começar AGORA (paralelo com FORJA-020 outros devs).

---

## 📞 Próximas Ações

### Se Aprovado:

1. **[HOJE]** Criar repo `/home/enio/opencode-egos/`
2. **[HOJE]** Clone anomalyco/opencode
3. **[AMANHÃ]** Setup packages/egos + packages/forja
4. **[Esta Semana]** Integração + testing
5. **[Próxima Semana]** Production ready

### Se Negado:

1. Continue com OpenCode oficial
2. Voltamos a manual governance
3. Pode revisar em 1-2 meses

---

**Documento criado por:** Claude  
**Status:** Awaiting Decision  
**Recomendação:** ✅ GO with custom fork

Qualquer dúvida? Fale.
