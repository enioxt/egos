# EGOS Agents Index
> **Generated:** 2026-04-10 | **Task:** ENC-L1-003+004 | **Total:** 24 agents

| ID | Name | Status | Area | LOC | Runtime Proof |
|----|------|--------|------|-----|---------------|
| [ssot-auditor](ssot-auditor.md) | SSOT Auditor | ✅ active | architecture | 3075 | `bun agents/agents/ssot-auditor.ts --dry-run --target .` |
| [ssot-fixer](ssot-fixer.md) | SSOT Fixer | ✅ active | architecture | 227 | `bun agents/agents/ssot-fixer.ts --dry-run` |
| [drift-sentinel](drift-sentinel.md) | Drift Sentinel | ✅ active | governance | 391 | `bun agents/agents/drift-sentinel.ts --dry-run` |
| [dep-auditor](dep-auditor.md) | Dependency Auditor | ✅ active | architecture | 247 | `bun agents/agents/dep-auditor.ts --dry-run --target .` |
| [archaeology-digger](archaeology-digger.md) | Archaeology Digger | ✅ active | knowledge | 417 | `bun agents/agents/archaeology-digger.ts --dry-run` |
| [chatbot-compliance-checker](chatbot-compliance-checker.md) | Chatbot Compliance Checker | 💀 dead | qa | 54 | `none` |
| [dead-code-detector](dead-code-detector.md) | Dead Code Detector | ✅ active | qa | 237 | `bun agents/agents/dead-code-detector.ts --dry-run --target .` |
| [capability-drift-checker](capability-drift-checker.md) | Capability Drift Checker | ✅ active | governance | 205 | `bun agents/agents/capability-drift-checker.ts --target ../85...` |
| [context-tracker](context-tracker.md) | Context Tracker | ✅ active | observability | 156 | `bun agents/agents/context-tracker.ts` |
| [gtm-harvester](gtm-harvester.md) | GTM Harvester | 💀 dead | knowledge | 143 | `none` |
| [framework-benchmarker](framework-benchmarker.md) | Framework Benchmarker | ✅ active | knowledge | 116 | `bun agents/agents/framework-benchmarker.ts --dry-run` |
| [mcp-router](mcp-router.md) | MCP Router | ✅ active | infrastructure | 531 | `bun agents/agents/mcp-router.ts --dry-run` |
| [spec-router](spec-router.md) | Spec Pipeline Router | ✅ active | governance | 447 | `bun agents/agents/spec-router.ts --mode validate --spec docs...` |
| [gem-hunter](gem-hunter.md) | Gem Hunter v6.0 | ✅ active | intelligence | 2537 | `bun agents/agents/gem-hunter.ts --dry` |
| [kol-discovery](kol-discovery.md) | KOL Discovery | ✅ active | intelligence | 291 | `bun scripts/kol-discovery.ts --dry` |
| [gem-hunter-api](gem-hunter-api.md) | Gem Hunter API | ✅ active | intelligence | 428 | `bun agents/api/gem-hunter-server.ts` |
| [agent-validator](agent-validator.md) | Agent Registry Validator | ✅ active | governance | 180 | `bun agents/agents/agent-validator.ts --exec` |
| [wiki-compiler](wiki-compiler.md) | Wiki Compiler | ✅ active | knowledge | 846 | `bun agents/agents/wiki-compiler.ts --compile --dry` |
| [doc-drift-sentinel](doc-drift-sentinel.md) | Doc-Drift Sentinel | ✅ active | governance | 595 | `bun agents/agents/doc-drift-sentinel.ts --dry` |
| [egos-pr](egos-pr.md) | EGOS PR Creator | ✅ active | git | 90 | `bash scripts/create-pr.sh --help` |
| [article-writer](article-writer.md) | Article Writer | ✅ active | publishing | 567 | `bun agents/agents/article-writer.ts --dry` |
| [doc-drift-verifier](doc-drift-verifier.md) | Doc-Drift Verifier | ✅ active | governance | 721 | `bun agents/agents/doc-drift-verifier.ts --dry` |
| [doc-drift-analyzer](doc-drift-analyzer.md) | Doc-Drift Analyzer | ✅ active | governance | 271 | `bun agents/agents/doc-drift-analyzer.ts --dry` |
| [readme-syncer](readme-syncer.md) | README Syncer | ✅ active | governance | 212 | `bun agents/agents/readme-syncer.ts --dry` |

---

*Next: ENC-L1-005 — smoke test suite for each agent (bun agent:run <id> --dry)*