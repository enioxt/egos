# Cross-Repo Context Router

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **Propósito:** Quando um tópico surgir na sessão, o agente de IA sabe ONDE buscar contexto sem carregar tudo de uma vez. Pull-based, não push-based.
> **Como usar:** Leia este arquivo quando precisar de contexto cross-repo. NÃO carregue os arquivos apontados automaticamente — só quando o tópico for relevante para a sessão.

---

## Como funciona

1. Conversa menciona um tópico (ex: "entity extraction", "licitações", "WhatsApp")
2. Agente consulta este router → encontra repo + arquivo + descrição
3. Agente lê APENAS os arquivos relevantes (Read tool nos caminhos indicados)
4. Contexto chega just-in-time, sem poluir a janela

---

## Router por Tópico

### Entity Extraction / Cross-Reference / Análise de Dados
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Investigation templates (5 tipos) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/services/investigation_templates.py` |
| Cross-reference engine (clusters, anomalias) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/services/cross_reference_engine.py` |
| Entity types + report schema | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/report_schema.py` |
| NER PT-BR (BERTimbau) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/services/nlp/bertimbau_ner.py` |
| NER PT-BR (spaCy) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/services/nlp/spacy_ner.py` |
| Benford's Law (fraude financeira) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/services/benford_analyzer.py` |
| Neo4j graph (83.7M nós) | br-acc | `/home/enio/br-acc/api/src/` |
| RAG context retrieval | egos-inteligencia | `/home/enio/egos-inteligencia/frontend/src/lib/intelligence/rag-context-retriever.ts` |

### ETL / Pipelines de Dados
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| BNMP (mandados de prisão) | egos-inteligencia | `/home/enio/egos-inteligencia/api/src/egos_inteligencia/etl/pipelines/` |
| DataJud (processos CNJ) | egos-inteligencia | mesmo diretório |
| PCMG video (transcrição Whisper) | egos-inteligencia | mesmo diretório |
| PCMG document (OCR PDF) | egos-inteligencia | mesmo diretório |

### Knowledge Base / KB-as-a-Service
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| KBS plan + entity graph v2 | egos | `docs/strategy/KB_AS_A_SERVICE_PLAN.md` |
| Offering catalog (8 camadas) | egos | `docs/strategy/EGOS_OFFERING_CATALOG.md` |
| Discovery protocol | egos | `docs/guides/KBS_DISCOVERY_PROTOCOL.md` |
| Delivery checklist (5 fases) | egos | `docs/guides/KBS_DELIVERY_CHECKLIST.md` |
| Personas Patos de Minas | egos | `docs/strategy/KBS_PATOS_DE_MINAS_PERSONAS.md` |
| Knowledge MCP (9 tools) | egos | `packages/knowledge-mcp/src/index.ts` |
| KB ingestor (PDF/DOCX/MD) | egos | `scripts/kb-ingest.ts` |
| KB lint | egos | `scripts/kb-lint.ts` |

### Guard Brasil / LGPD
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| PII patterns (16 BR) | egos | `packages/guard-brasil/src/pii-patterns.ts` |
| Evidence chain (SHA-256) | egos | `packages/guard-brasil/src/lib/evidence-chain.ts` |
| Guard API routes | egos | `apps/api/src/routes/` |
| Guard Brasil architecture | egos | `docs/strategy/GUARD_BRASIL_ARCHITECTURE_STACK.md` |

### Chatbot / Atendimento
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| 852 chatbot (72 routes) | 852 | `/home/enio/852/src/app/api/` |
| Tool-calling (27 tools) | 852 | `/home/enio/852/src/lib/tools/` |
| Chatbot SSOT | egos | `docs/modules/CHATBOT_SSOT.md` |

### WhatsApp / Telegram / Messaging
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| WhatsApp runtime (Evolution API) | egos | `integrations/distribution/whatsapp-runtime/docker-compose.yml` |
| WhatsApp SSOT | egos | `docs/knowledge/WHATSAPP_SSOT.md` |
| Telegram gateway (10+ commands) | egos | `apps/egos-gateway/src/channels/telegram.ts` |
| Telegram alerts inventory | egos | `docs/knowledge/TELEGRAM_ALERTS_INVENTORY.md` |

### ERP / Industrial
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Forja chat-first ERP | forja | `/home/enio/forja/src/app/api/` |
| Forja WhatsApp + tools | forja | `/home/enio/forja/src/lib/` |

### Marketplace / Pagamentos
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Carteira Livre (254+ routes) | carteira-livre | `/home/enio/carteira-livre/src/app/api/` |
| Asaas payment integration | carteira-livre | `/home/enio/carteira-livre/src/lib/asaas/` |

### Licitações / GovTech
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Eagle Eye (PNCP monitor) | egos-lab | `/home/enio/egos-lab/apps/eagle-eye/src/` |
| GovTech one-pager | egos | `docs/strategy/GOVTECH_LICITACOES_ABERTAS.md` |

### Governance / Regras / SSOT
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Rules index | egos | `.guarani/RULES_INDEX.md` |
| All SSOTs | egos | `docs/SSOT_REGISTRY.md` |
| Capability registry (29 seções) | egos | `docs/CAPABILITY_REGISTRY.md` |
| Agent registry (24 agents) | egos | `agents/registry/agents.json` |
| Pre-commit hooks (9 fases) | egos | `.husky/pre-commit` |

### Agents / Runtime
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Agent runner (frozen) | egos | `agents/runtime/runner.ts` |
| Event bus (frozen) | egos | `agents/runtime/event-bus.ts` |
| 24 kernel agents | egos | `agents/agents/` |
| 21 lab agents | egos-lab | `agents/registry/agents.json` |

### VPS / Deploy / Infra
| O que procurar | Repo | Caminho |
|---------------|------|---------|
| Caddyfile (all domains) | VPS | `/opt/bracc/infra/Caddyfile` (SSH) |
| VPS resource SSOT | egos | `docs/VPS_RESOURCE_SSOT.md` |
| Docker compose files | egos | `find /home/enio -name "docker-compose*" -not -path "*/node_modules/*"` |

---

## Regras de uso

1. **NÃO carregue este router inteiro no contexto** — ele é um índice de lookup
2. **Busque por tópico** — quando a conversa mencionar entity extraction, vá direto no egos-inteligencia
3. **Leia o arquivo apontado, não o router** — o router só diz onde olhar
4. **Atualize quando descobrir novos caminhos** — cada sessão pode descobrir novos arquivos relevantes
5. **Cross-repo grep:** `grep -rn "KEYWORD" /home/enio/{egos,egos-inteligencia,br-acc,852,forja,carteira-livre}/` quando o router não tiver a resposta
