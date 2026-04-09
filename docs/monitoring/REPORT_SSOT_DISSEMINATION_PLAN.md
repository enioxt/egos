# Plano Técnico: Disseminação REPORT_SSOT v2.0.0
> **Documento:** DISSEMINATION-001 | **Data:** 2026-04-09  
> **Kernel SSOT:** `egos/docs/REPORT_SSOT.md` v2.0.0  
> **Alvo:** Convergir 3 implementações paralelas em padrão unificado

---

## 🎯 Situação Atual (Reality Check)

### Fragmentação Detectada

| Repo | Implementação | Status | Gap |
|------|--------------|--------|-----|
| **egos** | `REPORT_SSOT.md` v2.0.0 | ✅ Canonical | Source of truth |
| **br-acc** | `REPORT_STANDARD.md` v1.0.0 | ⚠️ Legado | Não referencia kernel |
| **852** | `report-format.ts` (interface própria) | ❌ Independent | Zero matches REPORT_SSOT |
| **egos-lab** | `arkham-templates.ts` | ⚠️ Parallel | Templates isolados |
| **egos-inteligencia** | `report:view`, `report:export` RBAC | ⚠️ Functional | Schema não documentado |

### Anti-Patterns Confirmados

1. **852**: Interface `FormattedReport` com campos diferentes do schema canônico
2. **br-acc**: Pydantic schema em Python sem referência ao kernel
3. **egos-lab**: 6 templates independentes (network_analysis, timeline, etc.)
4. **egos-inteligencia**: Permissões RBAC para reports mas sem schema estruturado

---

## 🔧 Plano de Disseminação Técnica

### Fase 1: Kernel Hardening (24h)

**Objetivo:** Tornar REPORT_SSOT.md importável e verificável

```typescript
// packages/shared/src/report-standard.ts (NOVO)
export interface ReportSchema {
  report_id: string;           // REPORT-YYYY-NNN
  version: "2.0";
  generated_at: string;        // ISO-8601
  generated_by: {
    model: string;
    agent?: string;
    cost?: string;
    platform: "EGOS" | "Intelink" | "852" | string;
  };
  metadata: {
    title: string;
    subtitle: string;
    type: ReportType;
    entity_type: EntityType;
    date: string;              // DD/MM/YYYY
    sources_count: number;
    observations_count: number;
    confidence_overall: "alta" | "media" | "baixa";
    tags: string[];
  };
  sections: ReportSection[];
  gaps: string[];
  methodology: Methodology;
  sources: Source[];
  legal_disclaimer: string;
}

export type ReportType = 
  | "investigation" 
  | "entity_profile" 
  | "network_analysis"
  | "timeline"
  | "risk_assessment"
  | "executive_summary"
  | "full_investigation"
  | "institutional_feedback"
  | "opportunity"
  | "system_status";
```

**Tasks:**
- [ ] **SSOT-001**: Criar `@egos/report-standard` package
- [ ] **SSOT-002**: Adicionar JSON Schema exportável
- [ ] **SSOT-003**: Criar validator function
- [ ] **SSOT-004**: Documentar breaking changes v1→v2

---

### Fase 2: Leaf Repo Migration (48h)

#### 852 (Next.js + TypeScript)

**Estratégia:** Adapter pattern — manter `FormattedReport` como facade

```typescript
// src/lib/report-adapter.ts (NOVO)
import type { ReportSchema, ReportType } from '@egos/report-standard';
import type { FormattedReport } from './report-format';

/**
 * Adapter: FormattedReport (852 legacy) → ReportSchema (kernel canonical)
 */
export function toCanonicalReport(
  legacy: FormattedReport,
  options: {
    type: ReportType;
    platform: "852";
    cost?: string;
  }
): ReportSchema {
  return {
    report_id: generateReportId(),
    version: "2.0",
    generated_at: new Date().toISOString(),
    generated_by: {
      model: "852-engine",
      platform: "852",
      cost: options.cost
    },
    metadata: {
      title: legacy.title,
      subtitle: legacy.summary.slice(0, 100),
      type: options.type,
      entity_type: "institutional_feedback", // 852 default
      date: new Date().toLocaleDateString('pt-BR'),
      sources_count: 0, // 852 não rastreia fontes
      observations_count: legacy.tags.length,
      confidence_overall: "media",
      tags: legacy.tags
    },
    sections: [{
      id: "summary",
      title: "Resumo",
      content: legacy.markdown,
      confidence: "media"
    }],
    gaps: ["Fontes não rastreadas em formato legado"],
    methodology: {
      approach: "institutional_feedback",
      tools: ["852-analyzer"],
      limitations: ["Legacy format pre-dates REPORT_SSOT v2"]
    },
    sources: [],
    legal_disclaimer: "Este relatório apresenta exclusivamente dados de acesso público..."
  };
}
```

**Tasks 852:**
- [ ] **852-REPORT-001**: Instalar `@egos/report-standard`
- [ ] **852-REPORT-002**: Criar `report-adapter.ts`
- [ ] **852-REPORT-003**: Adicionar referência REPORT_SSOT em `AGENTS.md`
- [ ] **852-REPORT-004**: Implementar export PDF/JSON canonical

---

#### br-acc (Python + FastAPI)

**Estratégia:** Pydantic model inheritance — unificar com kernel

```python
# api/src/bracc/report_schema.py (ATUALIZAR)
from pydantic import BaseModel
from typing import Literal, List, Optional
from datetime import datetime

class ReportSchema(BaseModel):
    """
    Canonical Report Schema v2.0.0
    Source: egos/docs/REPORT_SSOT.md (kernel_canonical)
    """
    report_id: str                    # REPORT-YYYY-NNN
    version: Literal["2.0"] = "2.0"
    generated_at: datetime
    generated_by: GeneratedBy
    metadata: ReportMetadata
    sections: List[ReportSection]
    gaps: List[str]
    methodology: Methodology
    sources: List[Source]
    legal_disclaimer: str = (
        "Este relatório apresenta exclusivamente dados de acesso público..."
    )
    
    class Config:
        json_schema_extra = {
            "$id": "https://egos.ia.br/schemas/report-v2.json",
            "title": "EGOS Report Schema v2.0",
            "source": "egos/docs/REPORT_SSOT.md"
        }

class GeneratedBy(BaseModel):
    model: str
    agent: Optional[str] = None
    cost: Optional[str] = None
    platform: Literal["EGOS", "Intelink", "BR-ACC"] = "BR-ACC"
```

**Tasks br-acc:**
- [ ] **BRACC-REPORT-001**: Atualizar `report_schema.py` para v2.0
- [ ] **BRACC-REPORT-002**: Adicionar `$ref` ao kernel REPORT_SSOT
- [ ] **BRACC-REPORT-003**: Criar migration v1→v2
- [ ] **BRACC-REPORT-004**: Deprecar `REPORT_STANDARD.md` v1.0

---

#### egos-inteligencia (Intelink v3)

**Estratégia:** Native implementation — produto de inteligência primário

```python
# api/src/egos_inteligencia/models/report.py (NOVO)
from pydantic import BaseModel
from enum import Enum

class ReportType(str, Enum):
    INVESTIGATION = "investigation"
    ENTITY_PROFILE = "entity_profile"
    NETWORK_ANALYSIS = "network_analysis"
    TIMELINE = "timeline"
    RISK_ASSESSMENT = "risk_assessment"
    EXECUTIVE_SUMMARY = "executive_summary"
    FULL_INVESTIGATION = "full_investigation"

class ReportSchema(BaseModel):
    """
    Intelink v3 Report Schema — implements REPORT_SSOT v2.0
    Canonical: egos/docs/REPORT_SSOT.md
    """
    report_id: str           # FORMAT: RPT-INTLK-YYYY-NNNN
    version: str = "2.0"
    generated_at: str        # ISO-8601
    generated_by: GeneratedByInfo
    metadata: ReportMetadata
    sections: List[ReportSection]
    gaps: List[str]
    methodology: MethodologyBlock
    sources: List[SourceReference]
    legal_disclaimer: str
    
    # Intelink-specific extensions
    intelink_data: Optional[IntelinkExtensions] = None
    
    class Config:
        schema_extra = {
            "canonical_source": "egos/docs/REPORT_SSOT.md",
            "version": "2.0.0",
            "last_sync": "2026-04-09"
        }

class IntelinkExtensions(BaseModel):
    """Intelink-specific data not in base REPORT_SSOT"""
    neo4j_node_count: Optional[int]
    graph_query_used: Optional[str]
    entity_cnpj: Optional[str]  # Masked: **.XXX.XXX-**
    investigation_id: Optional[str]
```

**Tasks Intelink:**
- [ ] **INTLK-REPORT-001**: Criar `models/report.py` com schema v2.0
- [ ] **INTLK-REPORT-002**: Implementar endpoint `/reports/generate`
- [ ] **INTLK-REPORT-003**: Integrar com Neo4j para entity profiling
- [ ] **INTLK-REPORT-004**: Export formats: PDF, JSON, DOCX
- [ ] **INTLK-REPORT-005**: RBAC enforcement (report:view, report:export)

---

### Fase 3: Auto-Dissemination (72h)

**Objetivo:** Automatizar sync via kernel mechanisms

```bash
# Workflow: .windsurf/workflows/report-ssot-sync.md (NOVO)

1. SCAN: Detectar mudanças em REPORT_SSOT.md
   └─ bun scripts/disseminate-scanner.ts --pattern="REPORT_SSOT"

2. PROPAGATE: Atualizar leaf repos
   ├─ Update packages/shared/src/report-standard.ts
   ├─ Sync br-acc report_schema.py (via AST transform)
   ├─ Sync 852 report-adapter.ts
   └─ Sync egos-inteligencia models/report.py

3. VERIFY: Validar schemas
   └─ bun scripts/report-schema-validator.ts --all

4. NOTIFY: Alertar maintainers
   └─ Telegram @EGOSin_bot: "REPORT_SSOT v2.X propagated to N repos"
```

**Implementação:**

```typescript
// scripts/report-ssot-propagator.ts (NOVO)
import { readFileSync } from 'fs';
import { parseMarkdownSections } from './lib/markdown-parser';

const REPORT_SSOT_PATH = 'docs/REPORT_SSOT.md';

interface PropagationTarget {
  repo: string;
  path: string;
  adapter: 'typescript' | 'python' | 'json-schema';
}

const TARGETS: PropagationTarget[] = [
  { repo: 'egos', path: 'packages/shared/src/report-standard.ts', adapter: 'typescript' },
  { repo: 'br-acc', path: 'api/src/bracc/report_schema.py', adapter: 'python' },
  { repo: '852', path: 'src/lib/report-adapter.ts', adapter: 'typescript' },
  { repo: 'egos-inteligencia', path: 'api/src/models/report.py', adapter: 'python' },
];

export function propagateReportSSOT(version: string): void {
  const ssotContent = readFileSync(REPORT_SSOT_PATH, 'utf-8');
  const schema = extractJsonSchema(ssotContent);
  
  for (const target of TARGETS) {
    const adapted = adaptSchema(schema, target.adapter);
    writeToRepo(target.repo, target.path, adapted);
  }
  
  console.log(`✅ REPORT_SSOT v${version} propagated to ${TARGETS.length} repos`);
}
```

---

## 📊 Métricas de Sucesso

| Métrica | Baseline | Target | Tool |
|---------|----------|--------|------|
| Repos com REPORT_SSOT ref | 1 (egos) | 4 | `grep -r "REPORT_SSOT" */AGENTS.md` |
| Schema consistency score | 25% | 95% | `bun scripts/report-schema-validator.ts` |
| Export format compliance | 40% | 100% | Test suite |
| Migration time (v1→v2) | N/A | <2h/repo | CI/CD logs |

---

## 🔗 Links e Referências

| Documento | Path | Purpose |
|-----------|------|---------|
| **Canonical SSOT** | `egos/docs/REPORT_SSOT.md` | Source of truth v2.0.0 |
| **Kernel Implementation** | `egos/packages/shared/src/report-standard.ts` | TypeScript types |
| **br-acc Python** | `br-acc/api/src/bracc/report_schema.py` | Pydantic models |
| **852 Adapter** | `852/src/lib/report-adapter.ts` | Legacy→Canonical bridge |
| **Intelink Native** | `egos-inteligencia/api/src/models/report.py` | Full implementation |
| **JSON Schema** | `egos/schemas/report-v2.json` | Cross-language validation |
| **Dissemination Script** | `egos/scripts/report-ssot-propagator.ts` | Auto-sync |

---

## 🚨 Decisões Pendentes

1. **Versioning Strategy:** 
   - Opção A: Semver for REPORT_SSOT (v2.0.0 → v2.1.0)
   - Opção B: Date-based (REPORT-2026-04-09)
   - **Recomendação:** Semver para compatibilidade com npm/pypi

2. **Breaking Changes:**
   - 852 `FormattedReport` → `ReportSchema`: campo `markdown` vira `sections[]`
   - Mitigação: Adapter com deprecated warnings

3. **PII Handling:**
   - REPORT_SSOT exige masking CPF: `***.XXX.XXX-**`
   - Intelink já tem `guard_scan_pii` — integrar no pipeline

---

## ✅ Next Actions

### Imediato (Esta sessão)
- [ ] Criar `@egos/report-standard` package skeleton
- [ ] Implementar `report-schema-validator.ts`
- [ ] Iniciar TASKS.md entries para cada repo

### Próxima sessão
- [ ] Code review com maintainers de cada repo
- [ ] Testes de integração cross-repo
- [ ] Documentar breaking changes

---

Gerado por: Cascade  
Data: 09/04/2026 16:25 UTC-3  
Plano: DISSEMINATION-001  
Referência: `egos/docs/REPORT_SSOT.md` v2.0.0
