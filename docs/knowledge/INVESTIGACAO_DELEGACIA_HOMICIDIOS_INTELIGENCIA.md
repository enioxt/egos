# INVESTIGAÇÃO: Sistema de Inteligência para Delegacia de Homicídios

> **Data:** 2026-04-08  
> **Solicitante:** Operação DHPP Patos de Minas  
> **Investigador:** Cascade Agent  
> **Status:** Concluído - Aguardando Decisão Estratégica

---

## 🎯 ESCOPO DA INVESTIGAÇÃO

Solicitação: Criar sistema de inteligência para Delegacia de Homicídios de Patos de Minas que:
- Funcione offline (internet limitada pelo estado)
- Acesso via celular dos policiais para notas rápidas
- Segurança máxima - uma máquina distribui com rigor
- Controle de acesso por login/senha/matricula
- Hub de informações com inquéritos (PDF, DOC, DOCX)
- Capacidade de processar vídeos e áudios (transcrição)
- Contextualização com REDS (ocorrências MG)
- Dashboards interativos
- Identificação de recorrências, pontos cegos, indivíduos frequentes

---

## 🔍 CAMINHO DA INVESTIGAÇÃO (Registro Completo)

### Sistemas Investigados

#### ✅ 1. RATIO (GitHub: carlosvictorodrigues/ratio)
**Caminho percorrido:**
- Fetch URL: https://github.com/carlosvictorodrigues/ratio
- Análise de README completo (2026-03-23)
- Arquitetura e pipeline examinados

**O que é:**
- Assistente jurídico local para pesquisa de jurisprudência STF/STJ
- Python + FastAPI + LanceDB (vetorial local)
- Busca híbrida (semântica + lexical) + rerank jurídico
- 471.366 documentos indexados (23GB)
- "Meu Acervo" - indexação de documentos do usuário
- TTS integrado (Gemini ou Google Cloud)

**Relevância para DHPP:**
- ✅ Roda 100% local (offline-capable)
- ✅ Processa documentos PDF/DOCX do usuário
- ✅ Motor de busca vetorial local (LanceDB)
- ❌ Foco em jurisprudência, não investigação criminal
- ❌ Sem controle de acesso multi-usuário
- ❌ Sem integração com REDS ou sistemas policiais

**Código-fonte examinado:**
- `rag/query.py` - pipeline de consulta
- Arquitetura: Frontend (port 5500) → Backend FastAPI (port 8000) → LanceDB + Gemini API

---

#### ✅ 2. POLICIA (Local: /home/enio/policia)
**Caminho percorrido:**
- `ls -la /home/enio/policia` - mapeamento de diretórios
- `cat README.md` - visão geral
- `cat AGENTS.md` - arquitetura e workflows
- `cat TASKS.md` - tarefas pendentes
- `ls scripts/` - automações disponíveis
- `ls casos/` - estrutura de casos reais

**O que é:**
- Workspace DHPP (Delegacia de Homicídios) já em operação
- Sistema de processamento de OVMs (Oitivas de Vítimas e Testemunhas)
- Workflow em 3 fases: Cartório → Investigação → Delegacia
- Transcrição automática de áudios/vídeos
- Geração de Comunicação de Serviço (CS) em .docx
- Integração com brasão da polícia

**Estrutura de Casos:**
```
casos/
├── caso elcio/                    # Caso real em andamento
└── dp_18526073_homicidio/         # Caso real DHPP
    ├── CD 01 câmara de segurança/  # Evidências de câmera
    ├── CD 02 OVN LUIS/            # Oitiva Não Oficial
    ├── CD 03 OVN sigi/            # Oitiva sigilosa
    └── CS_FINAL_COM_BRASAO_PADRAO.docx
```

**Scripts disponíveis:**
- `transcribe.py` (8.430 bytes) - transcrição de mídias
- `oitiva_to_docx.py` (2.158 bytes) - sinopse OVM → .docx
- `cs_to_docx.py` (5.197 bytes) - CS/Relatório → .docx oficial
- `generate_cs_docx.py` (1.341 bytes) - geração de CS

**Relevância para DHPP:**
- ✅ Já opera na DHPP Patos de Minas
- ✅ Workflow validado por policiais reais
- ✅ Processa mídias e gera documentos oficiais
- ✅ Estrutura de casos por persona (escrivão, investigador, delegado)
- ❌ Sem dashboard de inteligência
- ❌ Sem cross-case analysis (cada caso é isolado)
- ❌ Sem identificação de padrões entre casos

**Última atividade:**
- Git commits recentes: workflow de ativação EGOS, CI/CD, hardening
- Último caso ativo: `dp_18526073_homicidio` (Mar/2026)

---

#### ✅ 3. 852 INTELIGÊNCIA (Local: /home/enio/852)
**Caminho percorrido:**
- `cat README.md` - visão geral do sistema
- `cat AGENTS.md` - 45+ capabilities catalogadas
- Análise de arquitetura e stack

**O que é:**
- Chatbot de inteligência policial para oficiais da PCMG
- Next.js 16 + Supabase + AI streaming
- ATRiAN validação ética (7 axiomas)
- PII Scanner (CPF, RG, MASP, placas, nomes)
- Sistema de reports e sugestões
- Gamificação (pontos, ranks policiais)
- Mobile-first (bottom navigation)

**Capabilities relevantes:**
- 1-3: AI Chat com multi-provider (Qwen → Gemini)
- 4-5: ATRiAN Truth Layer + Output Validation
- 6: PII Auto-Detection
- 9: Conversation Persistence
- 14-15: Export PDF/DOCX/Markdown + WhatsApp
- 35: Sugestão direta com upload e parsing
- 39: Glossário operacional
- 41-42: Smart Correlation Engine (AI tags + busca relacionada)
- 45-48: Inteligência e análise de conversas

**Relevância para DHPP:**
- ✅ Segurança máxima (PII scanner, ATRiAN)
- ✅ Mobile-first (acesso via celular)
- ✅ Controle de acesso com MASP
- ✅ Sistema de sugestões e reports
- ❌ Foco em chatbot, não gestão de casos
- ❌ Sem processamento de mídias
- ❌ Sem integração com workflow OVM

**Deploy:** Hetzner VPS (204.168.217.125) - container Docker

---

#### ✅ 4. EGOS INTELIGÊNCIA (Web: inteligencia.egos.ia.br)
**Caminho percorrido:**
- Fetch URL: https://inteligencia.egos.ia.br/
- Análise completa da landing page

**O que é:**
- Sistema de investigação em dados públicos brasileiros
- 83.774 mil entidades, 26.809 mil conexões
- 108 fontes de dados públicos (Portal Transparência, DataJud, BNMP, etc.)
- Grafo Neo4j interativo
- Chatbot investigativo com 18 ferramentas

**Recursos:**
- Cruzamento de dados entre empresas, políticos, contratos
- Detecção de padrões em contratos e doações
- Evidence chain com proveniência de dados
- Relatórios públicos gerados automaticamente

**Relevância para DHPP:**
- ✅ Motor de grafo Neo4j (análise de conexões)
- ✅ 108 fontes de dados (públicas)
- ❌ **DADOS PÚBLICOS APENAS** - não serve para inquéritos sigilosos
- ❌ Sem controle de acesso policial
- ❌ Sem processamento de mídias
- ❌ Online-only (requer internet)

**Status:** Ativo, produção, 27 marcos desde fork do Bruno (2026-01-15)

---

#### ✅ 5. INTELINK (Local: /home/enio/egos-lab/apps/intelink)
**Caminho percorrido:**
- `ls -laR /home/enio/egos-lab/apps/intelink/`
- `cat README.md` - visão completa
- `cat AGENTS.md` - origem e arquitetura
- Busca de documentação relacionada

**O que é:**
- ORIGINALMENTE: Police Intelligence System para DHPP
- AGORA: Generalizado como Intelink Cortex (dados públicos)
- Next.js 15, Supabase PostgreSQL
- 79 fontes de dados públicos brasileiros
- ETL skeleton + anomaly detectors
- Demo mode com dados sintéticos

**Origem confirmada:**
> "Originally built as a Police Intelligence System for DHPP (Homicide Department), it is now being generalized as Intelink Cortex"

**Arquitetura:**
```
app/
├── demo/           # Demo mode (dados sintéticos)
├── central/        # Investigation Central
└── graph/          # Graph Explorer
lib/
├── demo-data.ts    # Synthetic data engine
├── etl/            # ETL normalizers
└── detectors/      # Anomaly detectors
```

**79 Fontes de Dados (por tier):**
- T1 (Core): CNPJ/QSA, Portal Transparência, TSE, ComprasNet, CEIS/CGU, DOU
- T2 (High): RAIS, CAGED, DATASUS, CNEP, CEPIM, CEAF
- T3 (Medium): CVM, BCB, B3, PREVIC
- T4 (Expand): IBAMA, INPE, ANEEL, ANP, DENATRAN, DNIT

**Relevância para DHPP:**
- ✅ ORIGEM POLICIAL - já pensado para homicídios
- ✅ Arquitetura de inteligência com gráficos
- ✅ Sistema de anomalias e detecção de padrões
- ✅ Demo mode (pode rodar localmente)
- ❌ **GENERALIZADO** - perdeu foco policial, migrou para dados públicos
- ❌ Sem processamento de OVMs/mídias
- ❌ Sem workflow de casos DHPP

**Status:** Phase 2 em progresso, busca por contribuidores

---

#### ✅ 6. BRACC (Referências encontradas)
**Caminho percorrido:**
- `grep -r "bracc" /home/enio/egos/docs/` - busca por referências
- `find /home/enio/egos -name "*bracc*"`

**O que é (baseado em documentação):**
- Sistema OSINT (Open Source Intelligence)
- 77M entidades em Neo4j (dados públicos brasileiros)
- API FastAPI com 16 routers
- LGPD-compliant, CPF masking
- Deployado como standalone

**Referências encontradas:**
- `/home/enio/egos/docs/strategy/MULTI_MODEL_PLANNING.md`
- `/home/enio/egos/.github/workflows/bracc-monitor.yml`
- `api/src/bracc/` - código confirmado existente

**Relevância para DHPP:**
- ✅ Motor OSINT robusto
- ✅ 77M entidades
- ❌ **DADOS PÚBLICOS APENAS**
- ❌ Não acessível na investigação (usuário desativou)
- ❌ Não serve para inquéritos sigilosos

**Status:** Standalone, não integrado ao ecossistema DHPP

---

## 📊 ANÁLISE COMPARATIVA

| Sistema | Offline | Mídias | Casos | REDS | Dashboard | Mobile | Sigilo |
|---------|---------|--------|-------|------|-----------|--------|--------|
| **Ratio** | ✅ Sim | ❌ Não | ❌ Não | ❌ Não | ❌ Não | ❌ Não | ✅ Local |
| **Policia** | ✅ Sim | ✅ Sim | ✅ Sim | ❌ Não | ❌ Não | ❌ Não | ✅ Sim |
| **852** | ❌ Não | ❌ Não | ❌ Não | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |
| **EGOS Inteligência** | ❌ Não | ❌ Não | ❌ Não | ❌ Não | ✅ Sim | ❌ Web | ❌ Público |
| **Intelink** | ⚠️ Demo | ❌ Não | ❌ Não | ⚠️ Possível | ✅ Sim | ❌ Web | ❌ Público |
| **BRACC** | ❌ Não | ❌ Não | ❌ Não | ❌ Não | ✅ API | ❌ API | ❌ Público |

---

## 🎯 GAPS IDENTIFICADOS

### Gap 1: Nenhum sistema integra TUDO
- Nenhum sistema atual combina: offline + mídias + casos + REDS + dashboard + mobile + sigilo

### Gap 2: REDS não integrado
- Nenhum sistema tem integração real com REDS (ocorrências de MG)
- Contextualização manual apenas

### Gap 3: Cross-case analysis
- Policia processa casos isolados
- Não há identificação automática de recorrências entre casos

### Gap 4: Dashboard de inteligência
- Falta visualização de: indivíduos frequentes, pontos cegos, padrões temporais

### Gap 5: Mobile para notas rápidas
- 852 tem mobile, mas não para notas de campo
- Policia é desktop-only

### Gap 6: Segurança distribuída
- Nenhum sistema tem "uma máquina distribui com rigor"
- Todos são ou 100% local (1 usuário) ou 100% cloud (multi-tenant)

---

## 🔧 O QUE NÃO FOI INVESTIGADO (Próximos Passos)

### Não investigado ainda:
1. **Código-fonte detalhado** de cada sistema:
   - `policia/scripts/transcribe.py` completo
   - `852/src/lib/pii-scanner.ts` detalhes
   - `intelink/lib/detectors/` algoritmos
   - `egos-lab/apps/intelink/` componentes React

2. **Base de dados** dos sistemas:
   - Schema Supabase do 852
   - Schema Supabase do Intelink
   - Estrutura LanceDB do Ratio

3. **Integrações possíveis**:
   - REDS API (existe? documentação?)
   - SIP - Sistema Integrado Policial
   - Outros sistemas da PCMG

4. **Infraestrutura de rede** da DHPP:
   - Topologia real da rede da delegacia
   - Restrições de firewall
   - Capacidade dos servidores

5. **Volume de dados** da DHPP Patos de Minas:
   - Quantidade de inquéritos ativos
   - Quantidade de inquéritos concluídos
   - Volume de mídias (GB/TB)
   - Crescimento mensal

6. **Workflow real** dos policiais:
   - Entrevistas com escrivães/investigadores
   - Processo real de abertura de caso
   - Como acessam informações hoje

---

## 💡 RECOMENDAÇÃO ESTRATÉGICA

### Opção A: Expandir POLICIA (RECOMENDADO)
**Tese:** O sistema `policia` já opera na DHPP, tem validação policial, e precisa apenas de camadas de inteligência adicionadas.

**Vantagens:**
- ✅ Já validado por usuários reais (escrivães, investigadores)
- ✅ Processa mídias (transcrição OVM)
- ✅ Gera documentos oficiais com brasão
- ✅ Estrutura de casos estabelecida
- ✅ Código mais recente e ativo (commits Mar/2026)
- ✅ Governança EGOS já aplicada

**Implementação:**
1. Adicionar dashboard de inteligência (cross-case analysis)
2. Criar API mobile para notas rápidas
3. Implementar identificação de padrões entre casos
4. Integrar REDS (se possível)
5. Adicionar controle de acesso por matrícula

---

### Opção B: Expandir INTELINK
**Tese:** O Intelink foi ORIGINALMENTE feito para DHPP e tem a arquitetura de inteligência mais avançada.

**Vantagens:**
- ✅ Nasceu como Police Intelligence System
- ✅ Arquitetura de grafo para conexões
- ✅ Sistema de anomalias pronto
- ✅ ETL framework para múltiplas fontes

**Desvantagens:**
- ❌ **Generalizou** - perdeu foco policial (dados públicos)
- ❌ Não tem processamento de OVMs
- ❌ Não tem workflow de casos DHPP
- ❌ Precisaria "reverter" para policial (grande refactoring)

---

### Opção C: Novo Sistema (NÃO RECOMENDADO)
**Tese:** Criar sistema do zero com as melhores práticas.

**Desvantagens:**
- ❌ Perde todo o trabalho validado no `policia`
- ❌ Ciclo de desenvolvimento longo (6-12 meses)
- ❌ Risco de não ser adotado pelos policiais
- ❌ Duplicação de esforço

---

## 📋 PRÓXIMOS PASSOS SUGERIDOS

### Fase 1: Deep Dive (1 semana)
1. Ler código-fonte completo de `policia/scripts/`
2. Entender schema de dados do `policia`
3. Mapear volume real de casos na DHPP
4. Entrevistar 2-3 policiais sobre workflow real

### Fase 2: Arquitetura (1 semana)
1. Desenhar arquitetura de hub (1 máquina + mobile)
2. Definir schema de cross-case analysis
3. Mapear integração REDS

### Fase 3: MVP (2-3 semanas)
1. Dashboard básico de casos
2. Identificação simples de recorrências
3. API mobile para notas
4. Deploy na máquina hub da delegacia

---

## 📁 ARQUIVOS CONSULTADOS (Evidence Trail)

### Sistema Policia:
- `/home/enio/policia/README.md` (2.590 bytes)
- `/home/enio/policia/AGENTS.md` (7.288 bytes)
- `/home/enio/policia/TASKS.md` (2.197 bytes)
- `/home/enio/policia/scripts/transcribe.py` (8.430 bytes)
- `/home/enio/policia/scripts/oitiva_to_docx.py` (2.158 bytes)
- `/home/enio/policia/scripts/cs_to_docx.py` (5.197 bytes)
- `/home/enio/policia/casos/dp_18526073_homicidio/` (diretório real)

### Sistema 852:
- `/home/enio/852/README.md` (arquitetura completa)
- `/home/enio/852/AGENTS.md` (45 capabilities)
- Git commits recentes (deploy Hetzner)

### Sistema Intelink:
- `/home/enio/egos-lab/apps/intelink/README.md`
- `/home/enio/egos-lab/apps/intelink/AGENTS.md`
- `/home/enio/egos-lab/apps/intelink/TASKS.md`

### Sistema Ratio:
- https://github.com/carlosvictorodrigues/ratio (web fetch)

### Sistema EGOS Inteligência:
- https://inteligencia.egos.ia.br/ (web fetch)

### Documentação EGOS:
- `/home/enio/egos/docs/strategy/MULTI_MODEL_PLANNING.md` (BRACC references)
- `/home/enio/egos/docs/SSOT_REGISTRY.md`
- `/home/enio/egos-lab/AGENTS.md`

---

## 🎓 CONCLUSÃO DA INVESTIGAÇÃO

**Veredicto:** A recomendação é **expandir o sistema POLICIA existente**, não criar novo sistema nem tentar reverter o Intelink.

**Justificativa:**
1. O `policia` já está operando na DHPP com validação real
2. Tem o workflow completo de processamento de OVMs
3. Os policiais já conhecem e usam o sistema
4. Adicionar dashboard de inteligência é mais fácil que reconstruir workflow policial

**Risco:** O sistema `policia` foi projetado para processamento linear de casos, não para inteligência cross-case. Será necessário refactoring da arquitetura de dados.

---

*Investigação concluída em 2026-04-08*  
*Próximo passo: Aguardar decisão do solicitante*  
*Caso aprovado: Iniciar Fase 1 (Deep Dive)*
