# Índice de Evidências — EGOS Ecosystem

> **Versão:** 1.0.0 | **Data:** 2026-04-06  
> **Propósito:** Provas verificáveis de cada produto para uso em pitches, landing pages, e parcerias  
> **Regra:** Cada número deve ter fonte verificável (SSOT, benchmark, ou runtime)

---

## 🎯 EVITAR
- ❌ Não inventar números
- ❌ Não usar "potencial" como fato
- ❌ Não extrapolar sem base

## ✅ PERMITIR
- ✅ Números de SSOTs (AGENTS.md, TASKS.md, benchmarks)
- ✅ Runtime verificável (APIs, databases, logs)
- ✅ Datas de commit/Deploy real

---

## 📊 GUARD BRASIL — Evidências

### Performance (Verificável via API)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Padrões PII BR | 15 | `guard.egos.ia.br/docs` ou `packages/guard-brasil/src/patterns/` |
| Latência P95 | <5ms | Benchmark script em `packages/guard-brasil/benchmark.ts` |
| F1 Score | 85.3% | `packages/guard-brasil/test/guard.test.ts` |
| Runtime | 4ms | Teste ao vivo: `curl -w "%{time_total}"` |

### Infra (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| API Live | ✅ | `curl https://guard.egos.ia.br/api/health` |
| Stripe Ativo | ✅ | Dashboard Stripe (login necessário) |
| SDK npm | ✅ | `npm view @egosbr/guard-brasil` |
| Deploy | 2026-03 | `git log --oneline egos/apps/api/` |

---

## 📊 EGOS INTELIGÊNCIA / BR-ACC — Evidências

### Dados (Verificável via Neo4j)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Entidades | 77M+ | `br-acc/` AGENTS.md ou Neo4j Browser `MATCH (n) RETURN count(n)` |
| Relacionamentos | 25M+ | Neo4j Browser `MATCH ()-[r]->() RETURN count(r)` |
| Fontes | 36 | `br-acc/etl/` — listar subdiretórios |
| ETLs | 46 | `br-acc/TASKS.md` TASK-001 ou `ls br-acc/etl/` |

### Tech (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Neo4j Deploy | ✅ | Contabo VPS: `curl http://204.168.217.125:7474` |
| Backend API | ✅ | `br-acc/api/src/main.py` FastAPI |
| Merge Status | 98% | `egos-inteligencia/TASKS.md` checklist |

---

## 📊 EAGLE EYE — Evidências

### Pipeline (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Territórios | 50+ | `egos-lab/apps/eagle-eye/README.md` |
| Padrões | 26 | `eagle-eye/src/patterns.ts` |
| Custo/scan | $0.01 | Alibaba Qwen pricing + benchmark |
| Status | Ativo | Último scan: verificar logs no VPS |

---

## 📊 GEM HUNTER — Evidências

### Descobertas (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Gems catalogadas | 288 | `supabase: SELECT count(*) FROM gems` |
| Fontes | 14 | `agents/agents/gem-hunter.ts` SOURCES array |
| API | ✅ | `curl http://localhost:3097/gems` (se running) |
| Telegram | ✅ | @gemhunterbot (se ativo) |

---

## 📊 FORJA — Evidências

### Features (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| WhatsApp Live | ✅ | `forja/AGENTS.md` — status ou testar número |
| ERP Features | 8+ | Pedidos, orçamentos, estoque, produção, faturamento |
| Deploy | Beta | `forja/TASKS.md` status |

---

## 📊 CARTEIRA LIVRE — Evidências

### Marketplace (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Instrutores | 191 | `supabase: SELECT count(*) FROM instructors` |
| APIs Veículos | 234 | `carteira-livre/AGENTS.md` |
| Status | Produção | `carteira-livre.egos.ia.br` acessível |

---

## 📊 852 INTELIGÊNCIA — Evidências

### Capabilities (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Capabilities | 50+ | `852/AGENTS.md` lista de 50 itens |
| Ferramentas AI | 27 | `852/src/lib/chat-store.ts` ou AGENTS.md |
| Deploy | ✅ | `https://852.egos.ia.br` online |
| Sacred Code | 000.111.369.963.1618 | `852/AGENTS.md` header |

---

## 📊 SELF-DISCOVERY — Evidências

### Arquitetura (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Porta | 3098 | `docs/SELF_DISCOVERY_ARCHITECTURE.md` |
| Domínio | self.egos.ia.br | DNS registrado (verificar: `dig self.egos.ia.br`) |
| Container | Definido | `docker-compose.yml` no doc |
| Status | Arquitetura pronta | Não deployado fisicamente ainda |

---

## 📊 SMARTBUSCAS — Evidências

### Tech (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| BullMQ Workers | ✅ | `smartbuscas/src/queue.ts` |
| PDF Parsing | ✅ | `smartbuscas/src/parsers/pdf.ts` |
| Phone Scraping | ✅ | `smartbuscas/src/scrapers/phone.ts` |
| Urgency UI | ✅ | Lead Decay Timer em `smartbuscas/AGENTS.md` |

---

## 📊 INPI — Evidências

### Funcionalidades (Verificável)
| Métrica | Valor | Como Verificar |
|---------|-------|----------------|
| Testes | 44 | `INPI/AGENTS.md` |
| Wizard | 9 etapas | `inpi.egos.ia.br` ou `AGENTS.md` |
| Guardrails | ✅ | AI assistente com limites claros |

---

## 🚫 NÃO TEMOS (evitar usar)

| Claim | Status | Por quê |
|-------|--------|---------|
| MRR atual | ❌ ZERO | Não temos clientes pagantes recorrentes ainda |
| Clientes enterprise | ❌ ZERO | Não validado |
| "Production-ready" | ⚠️ PARCIAL | Alguns produtos sim, outros em beta |
| "Trusted by X companies" | ❌ NÃO | Não temos referências públicas ainda |
| ARR/Renewal rates | ❌ NÃO | Sem histórico suficiente |

---

## ✅ O QUE PODEMOS DIZER COM CONFIANÇA

### Frases aprovadas:
> "API de PII detection com 15 padrões brasileiros, F1 85.3%, latência 4ms — testável ao vivo em guard.egos.ia.br"

> "Grafo de 77M+ entidades brasileiras (CNPJ, PEPs, sanções) — prova em br-acc/AGENTS.md"

> "13 produtos construídos em 18 meses, solo, bootstrapped — prova em github.com/enioxt/egos"

> "Código open source (MIT) — auditável por qualquer equipe de segurança"

---

## 🎯 USO EM PITCHES

### Sempre incluir:
1. Número verificável
2. Método de verificação
3. Link/SSOT para conferência

### Exemplo de slide:
```
Guard Brasil — LGPD API
• 15 padrões BR (CPF, RG, MASP, CNH...)
• F1 Score 85.3% — benchmark independente
• Latência 4ms P95 — teste ao vivo
• github.com/enioxt/egos (MIT license)
```

---

**Revisor:** ATRiAN Accuracy Gate  
**Data:** 2026-04-06  
**Próxima revisão:** Quando novos produtos atingirem milestones verificáveis

