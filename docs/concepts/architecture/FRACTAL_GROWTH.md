# Arquitetura de Crescimento Fractal (Fractal Growth Protocol)

> **STATUS: PLANNED — conceptual framework, no code implements this protocol**
> **Versao:** 1.0.0
> **Data:** 2026-03-22
> **Contexto:** Definindo as camadas biologicas de emancipacao do software

## 1. Visão Geral
A Arquitetura Fractal do EGOS dita como o sistema escala não apenas em tráfego (Load Balancing), mas em **Governança de Organismo**. Quando adicionamos uma feature (Semente), estamos apenas testando sua capacidade de gerar um Domínio. Se gerar um Domínio, ela sofre Hard Fork.

Esse documento detalha o ciclo de vida utilizando o `EGOS Media Sector` como caso prático.

## 2. Fases da Biologia Fractal

### Fase 1: A Semente (Seed Module)
- **O que é:** Scripts soltos, rascunhos em HTML, "APIs improvisadas".
- **Hospedagem:** Artefatos na thread (via IAs como Antigravity ou Windsurf) ou subdiretórios ocultos (`/opt/egos-media/public` como HTML estático).
- **Exemplo Real:** A página inicial do *EGOS Brand Presentation*, jogada num Nginx ou Caddy, conectada a geradores do Nano Banana via CLI.
- **Objetivo:** Sobreviver ao teste de visão. Ele convence um humano de alto nível?

### Fase 2: O Broto (Feature Arm)
- **O que é:** Integração formalizada num repositório consumidor (`egos-lab/apps/` ou roteado no framework).
- **Hospedagem:** Next.js pages, rotas de API, Supabase Edge Functions.
- **Exemplo Real:** Se a Semente Media for aceita, ela se torna o "Brand Console" logado dentro do painel `egos-web`.

### Fase 3: A Raiz Aprofundada (Micro-Sovereignty)
- **O que é:** O braço começa a requisitar atenção arquitetural desproporcional. Começa a ter seu próprio pool de usuários ou geradores independentes. O Event Bus local não suporta sua latência.
- **Exemplo Real:** O Brand Console exige renderização intensa na nuvem para GPUs e workflows próprios.

### Fase 4: A Emancipação (The Hard Fork)
- **O que é:** O módulo rompe com o Kernel em execução diária, mas preserva a Governança (`.guarani`).
- **Hospedagem:** Subdomínios dedicados com roteamento apartado, Bancos de Dados isolados, Servidores de Worker exclusivos.
- **Exemplo Real:** `brand.egos.ia.br` (Ou uma eventual *Agência EGOS*) vira um monolito isolado, governado por seu próprio mantenedor (ex. Gabriel Cambraia), separando-se totalmente das missões de Cibersegurança e Event Bus do Orquestrador.

## 3. Implementação Prática Hoje
Ao posicionar a página estática no VPS Contabo agora, não estamos "escondendo" a aplicação; estamos alocando propositalmente na **Fase 1 (A Semente)** para mitigar risco e não manchar o Kernel complexo, ao passo que a exibimos cruamente sob a luz do Caddy, totalmente governada pelas Leis da Constituição EGOS.
