# EGOS Commons — Inventário Real (MVP Honesto)

> **VERSION:** 2.0.0 | **UPDATED:** 2026-03-31 — Novo modelo de splits (50/45/5) + pricing ajustado
> **Foco:** Produtos reais que JÁ EXISTEM nos repositórios. Sem hype, sem promessas futuras de orquestração mágica. Foco total em entregar código + split ético 95/5.

---

## O Modelo de Split Ético (A Estrela do Commons)
Nossa proposta de valor primária não é "agentes mágicos que fazem tudo". É o modelo comercial transparente e ético:
- **Grátis**: O código-fonte governado (via repos EGOS).
- **Implementação Paga**: O cliente paga para implantarmos.
- **Split Transparente**:
  - **50%** para o parceiro comercial (prospecção + fechamento)
  - **45%** para o implementador técnico (EGOS)
  - **5%** para o Kernel/ETC (ecossistema + infraestrutura)
- **Suporte Recorrente**: 50/40/10 (parceiro/EGOS/kernel)

---

## Os 6 Produtos Reais Disponíveis Hoje

### 1. EGOS Kernel (Orchestration Engine)
- **Descrição Real:** O núcleo de governança, pipeline de prompts e runtime base (*runner + event-bus*) para construir agentes baseados em TypeScript/Node.
- **Estado:** Produção (v1.2.0). Em uso nos repositórios leaf.
- **O que entregamos:** Setup do kernel, sincronização via `.egos` symlink, ruleops básicos (`.windsurfrules`).
- **Preço Implementação:** R$ 12.000 (Setup Completo)
- **Split (50/45/5):** R$ 6.000 (Parceiro) / R$ 5.400 (EGOS) / R$ 600 (Kernel)
- **Suporte Mensal:** R$ 800-1.500/mês (50/40/10)

### 2. Carteira Livre (SaaS Marketplace Base)
- **Descrição Real:** Plataforma Next.js 15 pronta com autenticação Supabase, pagamentos integrado (Asaas PIX/Cartão), onboarding e dashboard de agendamento (MVP focado em instrutores, mas adaptável a outros serviços autônomos).
- **Estado:** Produção (Next.js + Vercel + Supabase).
- **O que entregamos:** Fork limpo, setup das chaves Asaas/Supabase, customização visual inicial, deploy guiado.
- **Preço Implementação:** R$ 18.000 (Setup Base SaaS)
- **Split (50/45/5):** R$ 9.000 (Parceiro) / R$ 8.100 (EGOS) / R$ 900 (Kernel)
- **Suporte Mensal:** R$ 1.500-3.000/mês (50/40/10)

### 3. 852 Inteligência (Chatbot Institucional Seguro)
- **Descrição Real:** Chatbot streaming Next.js + Qwen/Gemini com detecção agressiva de PII, validação ética (ATRiAN level 1) e persistência local/remota. Feito originalmente para Polícia Civil, ideal para dados sensíveis corporativos corporativos.
- **Estado:** Produção (VPS + Caddy + Docker Compose).
- **O que entregamos:** Deploy do container via VPS, setup de chaves LLM (BYOK), personalização de prompt system e branding.
- **Preço Implementação:** R$ 15.000
- **Split (50/45/5):** R$ 7.500 (Parceiro) / R$ 6.750 (EGOS) / R$ 750 (Kernel)
- **Suporte Mensal:** R$ 800-1.500/mês (50/40/10)
- **Cobrança Por Uso:** R$ 15/usuário/mês ou R$ 0,15/1k chamadas (split 50/40/10)

### 4. Inteligência de Dados Públicos (Base de Grafo BR/ACC)
- **Descrição Real:** Plataforma ETL (Python) + Banco de Grafos (Neo4j) construída para rastrear CPFs/CNPJs e relações de empresas/sócios a partir de bases públicas (Receita/Transparência). Interface simplificada React.
- **Estado:** Produção parcial (ETL rodando, milhões de nós ingeridos).
- **O que entregamos:** Instância isolada do banco de grafos Neo4j no VPS local, setups de ETL customizados para a base do cliente.
- **Preço Implementação:** R$ 25.000 (Infra Pesada + Ingestão)
- **Split (50/45/5):** R$ 12.500 (Parceiro) / R$ 11.250 (EGOS) / R$ 1.250 (Kernel)
- **Suporte Mensal:** R$ 3.000/mês (Enterprise) (50/40/10)

### 5. Assistentes Guiados (Modelos INPI / Ratio Jurídico)
- **Descrição Real:** Aplicações web focadas (Next.js App Router) que guiam usuários por um processo complexo burocrático (ex: registro de marca, laudo técnico). Combina Wizard de passos + Chat com guardrails de escopo.
- **Estado:** Produção (Modelo INPI testado).
- **O que entregamos:** Setup do Wizard, injeção de base de conhecimento legal (RAG simplificado ou Hardcoded Policies).
- **Preço Implementação:** R$ 10.000
- **Split (50/45/5):** R$ 5.000 (Parceiro) / R$ 4.500 (EGOS) / R$ 500 (Kernel)
- **Suporte Mensal:** R$ 800/mês (50/40/10)
- **Split (95/5):** R$ 2.850 (Implementador) / R$ 150 (Kernel/ETC)

### 6. Ferramentas EGOS-Lab (Micro-SaaS Utilitários)
- **Descrição Real:** Implementações rápidas e focadas de IA que agregam valor instantâneo: Calculadora de Valor Real, Scanner de Precarização de Contratos, CV Builder otimizado para ATS.
- **Estado:** Lab / POC madura.
- **O que entregamos:** Hospedagem como white-label sob o monorepo do cliente ou página dedicada Vercel.
- **Preço Implementação:** R$ 6.000
- **Split (50/45/5):** R$ 3.000 (Parceiro) / R$ 2.700 (EGOS) / R$ 300 (Kernel)
- **Suporte Mensal:** R$ 400/mês (50/40/10)

---
*Este é o inventário real. Sem hypes inalcançáveis, apenas software que roda, resolve um problema, e recompensa quem implementa de forma ética.*
