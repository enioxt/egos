# Codebase Mining Report — 2026-04-09
> Generated: 08/04/2026, 23:21:45 BRT | Repos: 6 | Phase 1: TODO/FIXME/HACK scan

## Summary

| Metric | Value |
|--------|-------|
| Total markers found | 127 |
| Repos scanned | 6 |
| TODO | 110 |
| XXX | 3 |
| FIXME | 3 |
| WIP | 10 |
| HACK | 1 |

## Findings by Repository

### 852 (3 markers)

**`EVOLUTION_API_CARTEIRA_LIVRE_INVESTIGATION.md`** (1)
```
  L451 [TODO] // TODO: Processar mensagem com AI router
```

**`FORJA_IMPLEMENTATION_STRUCTURE.md`** (1)
```
  L287 [TODO] // TODO: Processar a mensagem
```

**`docs/_current_handoffs/ATOMIC_TASK_DECOMPOSITION_2026-03-28.md`** (1)
```
  L127 [TODO] // TODO: later → PostgreSQL, file, cloud
```

### br-acc (2 markers)

**`README.md`** (1)
```
  L219 [TODO] - **CPF é bloqueado em TODO o sistema** — busca, exibição, exportação
```

**`docs/META_PROMPT_V2.md`** (1)
```
  L368 [TODO] 1. Leia TODO o repositório: README.md, ROADMAP.md, ETHICS.md, LGPD.md, docs/, código-fonte
```

### carteira-livre (12 markers)

**`app/api/admin/analytics/route.ts`** (1)
```
  L208 [TODO] // TODO: Consider adding city to volante_instructors table if city-based analytics needed
```

**`app/api/feedback/route.ts`** (1)
```
  L197 [TODO] // TODO: Notificar admin
```

**`app/api/lgpd/delete/route.ts`** (1)
```
  L167 [TODO] // TODO: Enviar email de confirmação com link
```

**`app/api/wallet/withdraw/route.ts`** (1)
```
  L93 [TODO] // TODO: Integrar com Asaas para fazer o PIX real
```

**`components/ethik/index.ts`** (1)
```
  L7 [TODO] * TODO: Implement EthikBadge and EthikHistory components
```

**`docs/ADMIN_QUALITY_REPORT.md`** (1)
```
  L87 [TODO] return <div>TODO: KPIs Page</div>
```

**`docs/guides/WHATSAPP_SETUP_GUIDE.md`** (1)
```
  L260 [TODO] // TODO: Fase 5 — Conectar ao agente IA com MCP tools
```

**`scripts/audit/scan_system.ts`** (2)
```
  L276 [TODO] // TODO count
  L277 [TODO] const todoCount = countOccurrences(codeFiles, /TODO|FIXME|HACK|XXX/gi);
```

**`supabase/functions/check-mg-credentials/index.ts`** (2)
```
  L55 [TODO] // TODO: Notify instructors about expiration (Blocker)
  L85 [TODO] // TODO: Notify instructors D-30
```

**`supabase/functions/expire-payments/index.ts`** (1)
```
  L80 [TODO] // TODO: Send notifications to students about expired payments
```

### egos (82 markers)

**`.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md`** (1)
```
  L470 [XXX] 4. Link spec PR to implementation PR via "Closes #XXX" reference
```

**`.guarani/tools/code-health-monitor.ts`** (3)
```
  L11 [TODO] * - TODO/FIXME tracking
  L71 [TODO] const todos = (content.match(/TODO/gi) || []).length;
  L72 [FIXME] const fixmes = (content.match(/FIXME/gi) || []).length;
```

**`BLUEPRINT_ANALYSIS_INDEX.md`** (1)
```
  L144 [WIP] | Future | TBD | WIP | Weekly updates to TASKS.md |
```

**`TASKS.md`** (1)
```
  L827 [TODO] - [ ] **ARCH-001 [P1]**: `scripts/codebase-miner.ts` — agente de arqueologia. Fase 1: scana todos os repos locais (`~/85
```

**`agents/agents/agent-validator.ts`** (1)
```
  L149 [TODO] orphanFiles: 0, // TODO: Check for files in agents/agents/ not in registry
```

**`agents/agents/dead-code-detector.ts`** (1)
```
  L171 [TODO] suggestion: 'Delete if unused or add TODO comment',
```

**`agents/agents/gem-hunter.ts`** (1)
```
  L2375 [TODO] const prompt = `Based on this research paper, generate a TypeScript skeleton with 1-2 exported functions + types that co
```

**`docs/BRAND_CANONICAL.md`** (9)
```
  L117 [TODO] | Logo artwork | TODO | Fibonacci spiral concept defined, no SVG yet |
  L118 [TODO] | Logo variations | TODO | Full / mark / wordmark / horizontal / vertical |
  L119 [TODO] | Favicon | TODO | 32px mark variant needed |
  L120 [TODO] | Component library | TODO | Figma file — entire token set needs production-ready implementation |
  L121 [TODO] | Illustration style | TODO | Geometric, Fibonacci-based, SVG only — concept defined, no assets |
  L122 [TODO] | Social templates | TODO | Figma templates for X, LinkedIn, Telegram announcement |
  L123 [TODO] | Email signature | TODO | HTML template per brand spec |
  L124 [TODO] | Motion guidelines | TODO | Subtle animations (opacity + y translate) — principles noted, not specified |
  L125 [TODO] | Brand book PDF | TODO | Formal document for partnership/investor contexts |
```

**`docs/EGOS-116_COMPLETION_STATUS.md`** (1)
```
  L110 [TODO] | Brand Assets Checklist | ⭐⭐⭐⭐ | TODO items for design team (logos, icons, templates) |
```

**`docs/EGOS_KNOWLEDGE_BASE_ARCHITECTURE.md`** (1)
```
  L163 [TODO] # Validate wiki health (TODO)
```

**`docs/PRESENTATION_VISUAL_IDENTITY.md`** (9)
```
  L476 [TODO] | Logo (full) | SVG | `/brand/egos-logo.svg` | TODO |
  L477 [TODO] | Logo (mark) | SVG | `/brand/egos-mark.svg` | TODO |
  L478 [TODO] | Logo (wordmark) | SVG | `/brand/egos-wordmark.svg` | TODO |
  L479 [TODO] | Favicon | ICO/PNG | `/public/favicon.ico` | TODO |
  L480 [TODO] | Color swatches | PDF/figma | `/brand/color-palette.pdf` | TODO |
  L481 [TODO] | Typography guide | PDF | `/brand/typography-guide.pdf` | TODO |
  L482 [TODO] | Component library | Figma | Shared link | TODO |
  L483 [TODO] | Social templates | Figma | Shared link | TODO |
  L484 [TODO] | Email signatures | HTML | `/brand/email-sig.html` | TODO |
```

**`docs/concepts/NEURAL_MESH_ARCHITECTURE.md`** (1)
```
  L208 [TODO] 5. Writes the block (with `<!-- TODO: verify -->` markers)
```

**`docs/conversaGROK.md`** (3)
```
  L1882 [TODO] NUNCA deixe README ou comentário ganhar de fluxo executável. Import de SDK não prova integração. Variável de ambiente nã
  L1899 [TODO] 3. SEM INFERÊNCIA POR PROXIMIDADE (pasta sugestiva, dependência no package.json, interface sem implementação, mock, TODO
  L1911 [TODO] D. Detectar ilusões técnicas (dead code, mock tratado como feature, wrapper fino, TODO como roadmap)
```

**`docs/examples/spec-pipeline-example.md`** (1)
```
  L418 [XXX] 5. Link implementation PR to this spec via "Closes #XXX"
```

**`docs/gem-hunter/SSOT.md`** (1)
```
  L68 [TODO] | Gem Hunter deps-watch | TODO: add weekly Fri 3h00 BRT | Claude Code CCR (create via /schedule) |
```

**`docs/knowledge/HARVEST.md`** (2)
```
  L1673 [TODO] TODO_COUNT=$(git diff --cached -- "*.ts" "*.tsx" | grep '^+' | grep -c 'TODO\|FIXME' || true)
  L1677 [TODO] **>3 TODO/FIXME additions, >2 console.log/debug, >5 commented-out lines, hardcoded localhost URLs, possible unused TS im
```

**`docs/products/GUARD_BRASIL_FLAGSHIP_ROADMAP.md`** (2)
```
  L240 [TODO] | Tenant Guard | Intelink only | Guard Brasil core | 🔴 TODO |
  L241 [TODO] | Rate Limiter | Circuit Breaker ✅ | Guard Brasil quotas | 🔴 TODO |
```

**`docs/social/X_POSTS_SSOT.md`** (1)
```
  L3 [TODO] # Rule: TODO sobre X.com vive aqui. Nenhum outro arquivo de posts/social deve existir.
```

**`integrations/_contracts/discord.ts`** (4)
```
  L25 [TODO] // TODO: Implement Discord bot token validation
  L30 [TODO] // TODO: Implement Discord REST API message send
  L38 [TODO] // TODO: Implement Discord gateway event listening
  L43 [TODO] // TODO: Implement cleanup
```

**`integrations/_contracts/github.ts`** (4)
```
  L33 [TODO] // TODO: Implement GitHub OAuth token validation
  L42 [TODO] // TODO: Implement GitHub REST API create issue
  L50 [TODO] // TODO: Implement GitHub webhook listener for issue events
  L55 [TODO] // TODO: Implement cleanup
```

**`integrations/_contracts/slack.ts`** (4)
```
  L25 [TODO] // TODO: Implement Slack OAuth or token validation
  L30 [TODO] // TODO: Implement Slack Web API send message
  L35 [TODO] // TODO: Implement Slack event subscription (Socket Mode or webhooks)
  L40 [TODO] // TODO: Implement cleanup
```

**`integrations/_contracts/telegram.ts`** (4)
```
  L25 [TODO] // TODO: Implement Telegram bot token validation
  L30 [TODO] // TODO: Implement Telegram Bot API sendMessage
  L38 [TODO] // TODO: Implement Telegram polling or webhook
  L43 [TODO] // TODO: Implement cleanup
```

**`integrations/_contracts/webhook.ts`** (4)
```
  L29 [TODO] // TODO: Implement optional auth (API keys, OAuth tokens)
  L34 [TODO] // TODO: Implement HTTP request with retry logic
  L42 [TODO] // TODO: Implement HTTP server listener for incoming webhooks
  L47 [TODO] // TODO: Implement cleanup
```

**`integrations/_contracts/whatsapp.ts`** (4)
```
  L28 [TODO] // TODO: Implement WhatsApp Business API authentication
  L33 [TODO] // TODO: Implement WhatsApp Business API send message
  L38 [TODO] // TODO: Implement WhatsApp webhook listener
  L43 [TODO] // TODO: Implement cleanup
```

**`notebooklm_export_egos.md`** (7)
```
  L3682 [TODO] * - TODO/FIXME tracking
  L3742 [TODO] const todos = (content.match(/TODO/gi) || []).length;
  L3743 [FIXME] const fixmes = (content.match(/FIXME/gi) || []).length;
  L6221 [TODO] suggestion: 'Delete if unused or add TODO comment',
  L16979 [TODO] NUNCA deixe README ou comentário ganhar de fluxo executável. Import de SDK não prova integração. Variável de ambiente nã
  L16996 [TODO] 3. SEM INFERÊNCIA POR PROXIMIDADE (pasta sugestiva, dependência no package.json, interface sem implementação, mock, TODO
  L17008 [TODO] D. Detectar ilusões técnicas (dead code, mock tratado como feature, wrapper fino, TODO como roadmap)
```

**`scripts/codebase-miner.ts`** (10)
```
  L5 [TODO] * Phase 1: Scan all EGOS repos for TODO/FIXME/HACK/XXX/WIP markers in .ts/.py/.md files.
  L56 [TODO] /handoff_.*\.md$/, // session handoffs often have TODO in examples
  L60 [TODO] { pattern: /\bTODO\b/, label: "TODO" },
  L61 [FIXME] { pattern: /\bFIXME\b/, label: "FIXME" },
  L62 [HACK] { pattern: /\bHACK\b/, label: "HACK" },
  L63 [XXX] // XXX: require it to appear as a comment marker, not in placeholder IDs like "EGOS-XXX"
  L65 [WIP] { pattern: /\bWIP\b/, label: "WIP" },
  L220 [TODO] `> Generated: ${now} BRT | Repos: ${REPOS.length} | Phase 1: TODO/FIXME/HACK scan`,
  L239 [TODO] lines.push("✅ No TODO/FIXME/HACK markers found across all repos.");
  L331 [TODO] console.log("[codebase-miner] ARCH-001 — Phase 1: Scanning for TODO/FIXME/HACK/XXX/WIP...");
```

**`scripts/manifest-generator.ts`** (1)
```
  L295 [TODO] command: `echo '${claim.value}'  # TODO: replace with real verification command`,
```

### egos-lab (15 markers)

**`agents/agents/security-scanner.ts`** (1)
```
  L105 [TODO] /TODO.*(?:password|senha|key|token|secret)\s*[:=]\s*\S{8,}/i,
```

**`agents/agents/showcase-writer.ts`** (2)
```
  L113 [TODO] `grep -rn "TODO\\|FIXME\\|HACK\\|XXX" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" "${repoRoot}"
  L328 [TODO] message: `💡 Found ${todos.length} TODO/FIXME comments — perfect for "good first issue" labels!`,
```

**`apps/carteira-x/src/app/api/webhooks/whatsapp/route.ts`** (1)
```
  L18 [TODO] // TODO: Parse message text or image content
```

**`apps/eagle-eye/MIGRATION_INSTRUCTIONS.md`** (1)
```
  L27 [TODO] - Copie TODO o conteúdo (366 linhas)
```

**`apps/eagle-eye/src/analyze_viability.ts`** (1)
```
  L172 [TODO] // TODO: Implement proper ID lookup across all files if needed
```

**`apps/egos-web/api/stats.ts`** (1)
```
  L139 [TODO] const freeToolsCount = 6; // TODO: derive from API registry when available
```

**`apps/marketplace-core/src/domain/payment/ledger.ts`** (1)
```
  L80 [TODO] // TODO: Strict validation or default remainder handling.
```

**`apps/telegram-bot/src/index.ts`** (1)
```
  L99 [TODO] Você opera no grupo oficial t.me/ethikin e representa TODO o ecossistema EGOS.
```

**`contrib/IPED/iped-app/resources/scripts/tasks/PythonScriptTask.py`** (1)
```
  L32 [TODO] # TODO: document methods of those objects.
```

**`contrib/IPED/target/release/iped-4.4.0-SNAPSHOT/scripts/tasks/PythonScriptTask.py`** (1)
```
  L32 [TODO] # TODO: document methods of those objects.
```

**`docs/agentic/GOVERNANCE_RULES.md`** (1)
```
  L43 [TODO] | `tasks-in-ssot` | Warning | TODO/FIXME comments without TASKS.md reference |
```

**`docs/plans/ChatGPT-Estudo de caso Duolingo.md`** (1)
```
  L813 [TODO] **Propriedades mínimas em TODO evento**
```

**`docs/plans/SPRINT_EXECUTAVEL_2026-02-24.md`** (1)
```
  L66 [WIP] **Mitigação:** limitar WIP por trilha (máx. 2 itens ativos).
```

**`projects/00-CORE-intelink/PLAN_TELEMETRY.md`** (1)
```
  L941 [TODO] * **Checklist:** Update the `TODO.md` or Kanban. Add a specific column/tag: `WAITING_HUMAN_TEST`.
```

### forja (13 markers)

**`TASKS.md`** (2)
```
  L607 [TODO] ### EGOS-CONS-004: Remover TODO EGOS-158 ✅
  L608 [TODO] - [x] Remover comentário TODO da linha 1-2 de `safety.ts`
```

**`docs/ARQUITETURA_EGOS_CONSOLIDADA.md`** (1)
```
  L107 [TODO] **TODO existente:** EGOS-158 (linha 1-2 do safety.ts)
```

**`docs/VISION_MODULE.md`** (6)
```
  L16 [WIP] - **Silent WIP accumulation** — parts wait hours unnoticed
  L57 [WIP] | **CAM-01** | Shop overview — overhead high | 4-5 MP, varifocal, RTSP | Macro-flow: WIP, bay occupancy, movement |
  L107 [WIP] - 📦 **WIP accumulating** (queue > X pieces waiting)
  L281 [WIP] "get_wip_queue_status",        // Current WIP queue by station
  L322 [WIP] name: "WIP accumulating",
  L764 [WIP] - **Third camera:** add only after confirming that the first two views are producing reliable anomaly and WIP signals
```

**`docs/_archived_handoffs/2026-03/FORJA_INTELLIGENCE_REPORT_v1.2.0.md`** (1)
```
  L74 [WIP] - [ ] **Sprint 3 (Jun):** Pose analysis, WIP Queue management, ROS 2 integration.
```

**`src/app/api/notifications/whatsapp/route.ts`** (2)
```
  L115 [TODO] // TODO: Implement auto-reply logic
  L124 [TODO] // TODO: Implement connection monitoring
```

**`src/services/telegram/core.ts`** (1)
```
  L2 [TODO] // TODO: implement with real bot token when available
```


---

*ARCH-001 | codebase-miner.ts | Next run: weekly CCR (ARCH-004)*