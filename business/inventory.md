# EGOS Commons — Inventário Real (MVP Honesto)

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-23
> **Foco:** Produtos reais que JÁ EXISTEM nos repositórios. Sem hype, sem promessas futuras de orquestração mágica. Foco total em entregar código + split ético 95/5.

---

## O Modelo 95/5 (A Estrela do Commons)
Nossa proposta de valor primária não é "agentes mágicos que fazem tudo". É o modelo comercial transparente e ético:
- **Grátis**: O código-fonte governado (via repos EGOS).
- **Implementação Paga**: O cliente paga para implantarmos.
- **Split Ético**: 95% do valor volta imediatamente para a conta do criador/implementador ou fundo comunitário. 5% vai para a ETC (Ecossistema de Trabalho Compartilhado) / manutenção do EGOS Kernel.

---

## Os 6 Produtos Reais Disponíveis Hoje

### 1. EGOS Kernel (Orchestration Engine)
- **Descrição Real:** O núcleo de governança, pipeline de prompts e runtime base (*runner + event-bus*) para construir agentes baseados em TypeScript/Node.
- **Estado:** Produção (v1.2.0). Em uso nos repositórios leaf.
- **O que entregamos:** Setup do kernel, sincronização via `.egos` symlink, ruleops básicos (`.windsurfrules`).
- **Preço Sugerido:** R$ 2.500 (Setup Básico)
- **Split (95/5):** R$ 2.375 (Implementador) / R$ 125 (Kernel/ETC)

### 2. Carteira Livre (SaaS Marketplace Base)
- **Descrição Real:** Plataforma Next.js 15 pronta com autenticação Supabase, pagamentos integrado (Asaas PIX/Cartão), onboarding e dashboard de agendamento (MVP focado em instrutores, mas adaptável a outros serviços autônomos).
- **Estado:** Produção (Next.js + Vercel + Supabase).
- **O que entregamos:** Fork limpo, setup das chaves Asaas/Supabase, customização visual inicial, deploy guiado.
- **Preço Sugerido:** R$ 4.900 (Setup Base Saas)
- **Split (95/5):** R$ 4.655 (Implementador) / R$ 245 (Kernel/ETC)

### 3. 852 Inteligência (Chatbot Institucional Seguro)
- **Descrição Real:** Chatbot streaming Next.js + Qwen/Gemini com detecção agressiva de PII, validação ética (ATRiAN level 1) e persistência local/remota. Feito originalmente para Polícia Civil, ideal para dados sensíveis corporativos corporativos.
- **Estado:** Produção (VPS + Caddy + Docker Compose).
- **O que entregamos:** Deploy do container via VPS, setup de chaves LLM (BYOK), personalização de prompt system e branding.
- **Preço Sugerido:** R$ 3.500
- **Split (95/5):** R$ 3.325 (Implementador) / R$ 175 (Kernel/ETC)

### 4. Inteligência de Dados Públicos (Base de Grafo BR/ACC)
- **Descrição Real:** Plataforma ETL (Python) + Banco de Grafos (Neo4j) construída para rastrear CPFs/CNPJs e relações de empresas/sócios a partir de bases públicas (Receita/Transparência). Interface simplificada React.
- **Estado:** Produção parcial (ETL rodando, milhões de nós ingeridos).
- **O que entregamos:** Instância isolada do banco de grafos Neo4j no VPS local, setups de ETL customizados para a base do cliente.
- **Preço Sugerido:** R$ 7.900 (Infra Pesada + Ingestão)
- **Split (95/5):** R$ 7.505 (Implementador) / R$ 395 (Kernel/ETC)

### 5. Assistentes Guiados (Modelos INPI / Ratio Jurídico)
- **Descrição Real:** Aplicações web focadas (Next.js App Router) que guiam usuários por um processo complexo burocrático (ex: registro de marca, laudo técnico). Combina Wizard de passos + Chat com guardrails de escopo.
- **Estado:** Produção (Modelo INPI testado).
- **O que entregamos:** Setup do Wizard, injeção de base de conhecimento legal (RAG simplificado ou Hardcoded Policies).
- **Preço Sugerido:** R$ 3.000
- **Split (95/5):** R$ 2.850 (Implementador) / R$ 150 (Kernel/ETC)

### 6. Ferramentas EGOS-Lab (Micro-SaaS Utilitários)
- **Descrição Real:** Implementações rápidas e focadas de IA que agregam valor instantâneo: Calculadora de Valor Real, Scanner de Precarização de Contratos, CV Builder otimizado para ATS.
- **Estado:** Lab / POC madura.
- **O que entregamos:** Hospedagem como white-label sob o monorepo do cliente ou página dedicada Vercel.
- **Preço Sugerido:** R$ 1.500
- **Split (95/5):** R$ 1.425 (Implementador) / R$ 75 (Kernel/ETC)

---
*Este é o inventário real. Sem hypes inalcançáveis, apenas software que roda, resolve um problema, e recompensa quem implementa de forma ética.*
