# EGOS — Plano de Caminho B (Case Study Público) + Caminho C (Comunidade)
> **Data:** 2026-04-09 23:30 UTC-3 (atualizado v0.3)
> **Status:** 🟢 APPROVED — Camada 1 + Camada 2 fechadas. Camada 3 (execução) liberada sem pressa.
> **SSOT:** Este arquivo é o SSOT vivo desta decisão estratégica. Atualizar aqui, não criar arquivos paralelos.
> **Versão:** v0.3.0 (Sonnet + Enio — Evidence-First + Inside-out + 12 semanas sem pressa)

---

## 1. Decisão tomada (2026-04-09, atualizado v0.2)

Depois de ler ChatGPT/Gemini/Grok/Perplexity/Kimi sobre carreira em IA no Brasil 2026-2031, e de verificar que **os LLMs externos não tinham contexto do código EGOS** — só conheciam o Enio vagamente — a convergência entre as previsões deles e o que o EGOS já é virou sinal forte de que a tese está certa por conta própria.

**Decisão confirmada em 2026-04-09:**
- **Caminho B (primário):** Publicar o EGOS como case study. **Artigo âncora no formato (c) Showcase**: "EGOS: plataforma multi-agente brasileira open source — mapa visual completo". Posicionar como referência técnica brasileira em multi-agent governed systems.
- **Caminho C (paralelo):** Comunidade paga **EGOS Lab** — R$ 20/mês simbólico, tier único com tudo incluso (WhatsApp + Notion + encontros ao vivo + dashboards). **Todos os artigos permanecem gratuitos** (Substack + egos.ia.br). O pagamento é só para acessar comunidade, contato direto, dashboards completos e encontros ao vivo.
- **Caminho A (consequência):** Parcerias com clientes diretos vão acontecer naturalmente depois que B e C criarem autoridade e rede. Sem outbound ativo.

**Princípio norteador atualizado (2026-04-09):**
> **"Nada avança sem prova."**
> Encapsular o que já existe, dar tom sério/empresarial/técnico. Testar tudo, provar cada claim com teste real e dashboard vivo. ATRiAN + Guard Brasil + Doc-Drift Shield + Evidence Gate garantem que **nenhum commit/push passa sem evidência**. Zero claims sem número, zero feature sem teste, zero alegação de capacidade sem prova reproduzível. Transparência radical é consequência, não fim.

**Decisões das perguntas de Camada 1 (fechadas 2026-04-09):**
| # | Decisão |
|---|---|
| Q1 | (c) Showcase — "EGOS: plataforma multi-agente brasileira open source — mapa visual completo" |
| Q2 | Mix PT-BR primário + EN disponível, foco inicial em devs BR usando IDEs (Claude Code, Cursor, Windsurf) |
| Q3 | **EGOS Lab** — nome da comunidade |
| Q4 | R$ 20/mês tier único — tudo incluso (WhatsApp + Notion + encontros ao vivo + dashboards). Conteúdo público permanece gratuito. |
| Q5 | **Qualitativa**: "provar cada claim com dashboard vivo". Métrica numérica a definir depois que infra de evidência estiver pronta. |

**Decisões das perguntas de Camada 2 (fechadas 2026-04-09):**
| # | Decisão |
|---|---|
| Q6 | `status.egos.ia.br` público: tiers (public/community/enio-only). Pull-based snapshot a cada 5min, Guard Brasil audita antes de servir. |
| Q6.1 | OTP: **WhatsApp via Evolution API** (já setup, já validado). Email como fallback secundário (pesquisar servidor próprio no VPS depois). Prioridade: experiência top-de-linha desde o primeiro contato. |
| Q7 | Manter `apps/egos-site/` Bun + Hono como fonte. Showcase + blog em markdown versionado no git. |
| Q7.1 | **egos.ia.br = canonical**. Substack = satélite manual via copy-paste. Task obrigatória de repost toda vez. |
| Q8.1 | Enio já tem 2-3 pessoas em mente como primeiros co-stewards/testers antes do launch público. |
| Q11 | **§33 Evidence-First vira regra AGORA** (não depois). Adicionar ao `~/.claude/CLAUDE.md` global antes de qualquer código. |
| Q12 | **Sem pressa.** 12 semanas é alvo informal, não deadline. Compromissos paralelos (Eagle Eye, Forja) podem atrasar e está OK. |
| Q13 | **Inside-out**. Kernel → Agents → Governance → Stack → Produtos → Data → Dashboards → Artigo. |
| Q14 | **Gradual.** Evidence Gate entra como warning na semana 1, blocking na semana 2. Tarefas paralelas em outros repos (Eagle Eye, Forja) podem continuar sem ser travadas. |

**O que Caminho B+C NÃO é:**
- Não é adicionar features novas
- Não é construir nova plataforma de curso
- Não é outbound comercial
- Não é content marketing genérico
- Não é construir antes de provar

---

## 1.1 Evidence-First Principle — regra canônica do EGOS (NOVA, 2026-04-09)

Esta é a decisão mais importante da sessão. Merece virar regra canônica no `~/.claude/CLAUDE.md` como §33 e ser aplicada retroativamente a todo o ecossistema.

### Regra
> **Claim sem prova = claim inválido.** Nenhum documento, README, artigo, post, agent capability ou task é considerado verdadeiro até existir:
> 1. **Teste automatizado** que exercita o claim
> 2. **Métrica coletada** que confirma o número
> 3. **Entrada no manifesto** (`.egos-manifest.yaml`) ligando o claim à prova
> 4. **Dashboard público ou dry-run reproduzível** mostrando a prova executando

Claims sem essas 4 coisas são marcados como `unverified:` no commit e não aparecem no artigo showcase nem no material de comunidade.

### Por que isso importa para B+C
O Caminho B (showcase) depende de **confiança técnica**. Se o artigo afirma "EGOS tem 19 agents ativos com governance drift zero", isso precisa estar visível num dashboard público que quem lê pode clicar e verificar. Se o artigo afirma "16 padrões PII brasileiros detectados em 4ms", isso precisa ter teste automatizado mostrado no post + endpoint público que roda.

Sem isso, o showcase vira mais um post de LinkedIn com números inventados. Com isso, vira o primeiro showcase técnico brasileiro onde **cada linha tem link para evidência**.

### O que já existe e serve de base (inventário honesto)
| Mecanismo EGOS | Função | Status atual |
|---|---|---|
| **Doc-Drift Shield (§27 CLAUDE.md)** | Manifestos `.egos-manifest.yaml` em cada repo, verificador em pre-commit, sentinel CCR | ✅ Ativo — 3 repos com manifest, verificador roda. Falta expandir cobertura. |
| **ATRiAN Ethics Layer** | Truth, Accuracy, Reversibility, Impact, Accountability, Neutrality — embedded no 852 e Guard | ✅ Implementado mas não exposto como "gate de prova" ainda. |
| **Guard Brasil** | PII scanner + LGPD compliance, 16 padrões | ✅ API live, falta usar nele mesmo (audit próprios prompts/logs/outputs antes de publicar). |
| **file-intelligence.sh** | Classifica staged files, detecta proliferação, verifica SSOT | ✅ Ativo no pre-commit. |
| **vocab-guard** | Bloqueia termos phantom (NATS/ZKP/shadow nodes etc.) | ✅ Ativo — eu consertei hoje o bug Option B. |
| **llm-test-suite.ts** | 9 testes em 5 categorias incluindo PT-BR+LGPD | ✅ Existe, rodando manual. Falta integrar ao evidence gate. |
| **CCR jobs** | 3 jobs agendados produzindo reports em `docs/jobs/` | ✅ Rodando. Falta dashboard público mostrando. |
| **governance:check** | Verifica SSOT drift | ✅ Passa limpo. |
| **Heartbeat agent** | Monitora containers VPS | ✅ Rodando. |
| **PRI (Protocolo de Recuo por Ignorância)** | Agent admite não saber ao invés de alucinar | ✅ Kernel v0.2.0, raro no mercado. |

### O que falta para o gate funcionar (gap list)
1. **Evidence gate pre-commit:** extensão do `.husky/pre-commit` que, ao detectar claim numérico em doc staged, exige entrada correspondente no manifest ANTES de permitir commit (já tem isso para .egos-manifest via Doc-Drift Shield, mas precisa expandir para **capability claims**, não só manifest claims)
2. **Dashboard público `status.egos.ia.br`:** expõe em tempo real o que os claims afirmam (ver Q6 abaixo)
3. **Evidence linking em docs:** todo número numa doc precisa ter `<!-- evidence: claim-id -->` ou link para manifest
4. **CI pipeline de evidence run:** rodar diariamente todos os testes que sustentam claims públicos, falhar alto se algum quebrar
5. **Reproducible proof commands:** cada claim tem um comando shell que qualquer um pode rodar e ver o resultado (ex: `bun scripts/guard-brasil-bench.ts` mostra os 4ms reais)
6. **Guard Brasil auditando Guard Brasil:** ironia útil — rodar Guard nos próprios prompts/logs/outputs do EGOS antes de publicar qualquer coisa pública. Fecha o loop.

### Como isso se conecta a cada Caminho
- **Caminho B (showcase):** Cada seção do artigo âncora linka para um claim reproduzível. Leitor pode clicar em "19 agents ativos" → vê dashboard → clica num agent → vê última execução real. Zero fé cega.
- **Caminho C (comunidade):** EGOS Lab é o lugar onde membros **co-constroem provas**. PRs aceitos precisam adicionar teste + manifest entry + dashboard tile se for claim novo. A comunidade é treinada no próprio método.
- **Caminho A (futuro):** Quando aparecer cliente, a venda é "aqui está o dashboard, aqui está o repo, aqui está o teste rodando agora, aqui está o ROI provado". Não precisa pitch.

---

## 2. Por que essa ordem faz sentido (B → C paralelo → A depois)

1. **EGOS já é o produto do Cenário 1/2/3 do ChatGPT simultaneamente** (ver análise na conversa anterior). O problema não é construir mais; é **nomear e mostrar**. Caminho B atende isso.
2. **Enio é researcher-builder, não vendedor** (§24 CLAUDE.md). Outbound B2B solo é antitético ao perfil. Conteúdo técnico profundo é onde ele ganha.
3. **Comunidade (C) gera:**
   - Feedback real sobre o que importa no EGOS (priorização via sinal, não adivinhação)
   - Co-construtores que melhoram o código
   - Pipeline natural para A (membros viram clientes / indicam clientes)
   - Receita simbólica que banca infra (R$ 20 × 50 membros = R$ 1k/mês = paga VPS + APIs)
4. **Parcerias (A) exigem autoridade prévia.** Metalúrgica não contrata dev solo desconhecido. Contrata quem já publicou algo que ela ou o contador dela leu.
5. **Alinha com §23 GTM-First v2 e §24.1 NO JOBS:** sem urgência, sem vagas, construção de rede através de trabalho público.

---

## 3. Redescoberta: "Live School" já existe no arquivo do EGOS

Importante: **Live School não é ideia nova**. Está no arquivo histórico do EGOSv2 desde setembro/2025. Redescobri:

### 3.1 O que já foi concebido
- **Local:** `/home/enio/egos-archive/v2/EGOSv2/docs/1_CORE/live_school_method/` + `live_school_redesign/`
- **Conceito:** "The Observatory" — cosmos de aprendizado visual (React Three Fiber 3D)
- **Filosofia original:** "Ensinar é recordar o que já se é" (método maiêutico socrático)
- **3 agentes IA concebidos:** EVA, GUARANI, MAIÊUTICA (estavam em Python, precisam port para TypeScript)
- **Método:** Learn → Apply → Monetize → Document → Scale
- **Estrutura visual:** Observatory (portal), Explorer, Mapper, Navigator
- **Tasks atuais:** LS-001 ✅ (análise feita), LS-002 ⏳ (port para TS), LS-003 ⏳ (Observatory UI)

### 3.2 O que sobrou e o que tem que morrer
| Componente original | Decisão |
|---|---|
| Método Learn→Apply→Monetize→Document→Scale | ✅ **Mantém** — é sólido e descreve o fluxo real |
| Observatory como portal visual | 🟡 **Simplificar** — React Three Fiber é grandioso demais. Começar com dashboard Notion/Paperclip simples. |
| 3 agentes EVA/GUARANI/MAIÊUTICA | 🟡 **Rebuild leve** — portar conceito para agents atuais (sem o peso filosófico antigo) |
| Sacred mathematics, Fibonacci, Tesla 3-6-9 | ❌ **Cortar** — vocab guard atual bloqueia esses termos. Enio já moveu para tom mais técnico/grounded. |
| "Learning Cosmos" como marca | 🟡 **Avaliar** — bonito mas hype-sounding. Alternativas: "EGOS Lab", "Observatório EGOS", "Estúdio EGOS", "Mesa EGOS". |
| COMMUNICATION_STRATEGY.md (de 2025) | ✅ **Reaproveitar estrutura** — audiências segmentadas, canais, cronograma ainda servem |

### 3.3 Nova forma proposta (Live School 2.0, enxuta)
**Live School 2.0** = laboratório público de construção do EGOS com comunidade paga acompanhando, aprendendo, contribuindo e eventualmente virando parceiros/clientes.

- **Não é:** curso com aulas gravadas
- **Não é:** bootcamp com cronograma fixo
- **Não é:** mentoria 1:1 paga
- **É:** transparência radical do build do EGOS + acesso direto ao Enio via comunidade + recursos compartilhados + encontros ao vivo irregulares + co-autoria no kernel

---

## 4. Referências — o que já existe no mundo e no Brasil

Não inventar roda. Vou listar o que conheço de referências próximas + pontos fortes e fracos de cada.

### 4.1 Modelos internacionais relevantes
| Comunidade | Modelo | O que funciona | O que não serve |
|---|---|---|---|
| **Buildspace (s1..s5)** | Cohort grátis, graduação com demo | Energia de cohort, sentimento de turma, demo day gera visibilidade | Descontinuada. Cohort fixo é pesado para solo. |
| **100Devs (Leon Noel)** | Bootcamp grátis via Twitch, comunidade Discord | Escala enorme por ser grátis, foco em empregabilidade | Dependente de 1 pessoa (Leon), modelo vive de live streams intensas |
| **WIP.co (Pieter Levels)** | Build in public com accountability, US$ 20/mês | Preço simbólico, acesso a indie hackers reais, foco em ship, não em teoria | Comunidade global em inglês, cultura muito SF/distant do BR |
| **Indie Hackers** | Forum grátis + newsletter | Distribuição massiva, storytelling de bootstrappers | Sem curadoria forte, conteúdo diluído |
| **MicroConf / Rob Walling** | Conferências + Slack pago + mastermind | Target bootstrapped SaaS, alto valor | Preço alto, perfil corporativo, não brasileiro |
| **Fireship (YouTube + Pro)** | Vídeos curtos grátis + Pro US$ 19/mês | Escala YouTube, humor técnico | Modelo depende de produção de vídeo semanal pesada |
| **The Odin Project** | Curriculum open source, comunidade Discord grátis | Prova que OSS curriculum funciona | Sem receita direta |
| **100rabbits (Hundred Rabbits)** | Artistas/devs nômades, Patreon | Transparência radical, lifestyle sustentável, OSS radical | Nicho muito específico |

### 4.2 Modelos brasileiros relevantes
| Comunidade | Modelo | O que funciona | O que não serve |
|---|---|---|---|
| **Rocketseat (Ignite, Explorer)** | Formações pagas R$ 600-2k, comunidade Discord | Escala BR enorme, produção top | Corporativo, aulas gravadas, não é laboratório aberto |
| **Filipe Deschamps** | YouTube grátis + tabnews (rede social dev BR) | tabnews é próximo do espírito "build in public BR" | Não tem modelo pago de acesso direto |
| **Cursos em Vídeo (Gustavo Guanabara)** | YouTube grátis | Acessibilidade absoluta | Ensino tradicional, não laboratório |
| **Erick Wendel (Training)** | Cursos Node pagos + comunidade | Qualidade técnica alta, nicho Node | Formato tradicional de curso |
| **Balta.io (André Baltieri)** | Plataforma de cursos + assinatura | Escala, catálogo grande | Corporativo, não open source |
| **Comunidade Impulso** | Grupo privado pago de devs BR | Networking sênior, alto valor | Foco em carreira, não em construção |
| **Zenklub / Kinship** | Comunidade SaaS | Gestão paga via plataforma | Não aplicável a dev |
| **Mastermind de Indie Hackers BR (vários)** | Grupos WhatsApp informais | Baixo atrito, linguagem BR | Sem estrutura, sem produto |

### 4.3 O gap que eu vejo
**Nenhum brasileiro está fazendo:**
- Build in public de infraestrutura técnica complexa (multi-agent + governança + MCP + open source) aberta para participação
- Comunidade paga simbólica (R$ 20/mês) focada em **co-construção** de um único projeto real, não tutoriais genéricos
- Fusão de "blog técnico profundo" + "comunidade WhatsApp BR" + "dashboards vivos" + "acesso ao builder"

**O mais próximo que existe:** tabnews (Filipe Deschamps) + comunidades de bootstrappers em WhatsApp + Rocketseat Ignite. Mas ninguém fez a fusão de "você acompanha um laboratório vivo de um dev solo construindo infra de ponta, com acesso direto, por R$ 20".

**Isso é o oceano azul do Caminho C.** E o Cenário 3 do ChatGPT ("quem tem governança+confiança ganha") apoia exatamente esse posicionamento: confiança não se vende com outbound, se vende com transparência.

---

## 5. Arquitetura proposta (draft, para iterar)

### 5.1 Pilares operacionais
| Pilar | O que é | Onde vive | Quem consome |
|---|---|---|---|
| **Blog / Artigo âncora** | Post público massivo: "O que eu construí em 18 meses de EGOS" — com screenshots, diagramas, métricas reais, links para commits | `egos-site/` (a construir ou reativar) ou publicar em tabnews + dev.to + LinkedIn + Medium | Público geral, devs BR, recruiters, potenciais clientes A |
| **Série de artigos técnicos** | 1 por mês, cada um sobre 1 padrão do EGOS (ATRiAN, PRI, Doc-Drift Shield, Guard Brasil, Vocab Guard, Auto-Disseminate, etc.) | Mesmo canal do artigo âncora | Devs técnicos interessados em infra agent |
| **Dashboards vivos** | Snapshot público do estado do EGOS: agents ativos, últimos commits, métricas de governança, health dos containers | `hq.egos.ia.br` (já existe privado; criar versão pública `status.egos.ia.br` ou similar) | Comunidade paga + visitantes |
| **Comunidade paga R$ 20/mês** | WhatsApp + Telegram + Notion compartilhado + acesso ao Paperclip em modo viewer | WhatsApp grupo BR + Notion workspace + Paperclip public viewer | Membros pagantes |
| **Encontros ao vivo irregulares** | Calls quinzenais ou mensais via Jitsi/Meet, gravadas, onde Enio mostra o que está construindo e ouve feedback | Agendamento via Notion | Membros pagantes |
| **Co-autoria no kernel** | PRs da comunidade aceitos no EGOS. Contribuidores recorrentes viram "co-stewards" | GitHub `enioxt/egos` + roles documentados | Membros ativos |
| **Repositório de ideias** | Lista pública de "problemas em aberto" no EGOS que comunidade pode pegar | `docs/community/OPEN_PROBLEMS.md` | Membros e devs external |
| **Certificação leve** | "EGOS Practitioner" — assinado pelo Enio, gerado automaticamente depois de N contribuições ou meses na comunidade | NFT opcional / PDF simples / badge LinkedIn | Membros ativos |

### 5.2 Canais de distribuição
- **X.com (@enioxt ou nova conta EGOS):** threads técnicas curtas, print de dashboards, quotes de conversas com a comunidade
- **LinkedIn:** versão profissional/executiva dos mesmos conteúdos, foco em middle market e setor público
- **WhatsApp BR:** canal de distribuição principal para comunidade brasileira (maior engajamento)
- **Telegram:** mirror do WhatsApp para quem prefere
- **tabnews:** submissão cruzada de artigos
- **Newsletter (Substack? Beehiiv? Self-hosted?):** 1 email/semana com "o que aconteceu no EGOS" — free tier gera funil para R$ 20/mês
- **GitHub Discussions no `enioxt/egos`:** forum público complementar

### 5.3 Stack técnica necessária para Caminho B + C
**Já existe:**
- ✅ VPS Hetzner com 19 containers
- ✅ `hq.egos.ia.br` (privado)
- ✅ Paperclip self-hosted
- ✅ Notion MCP funcional (`mcp__claude_ai_Notion__*`)
- ✅ egos-hq dashboard base
- ✅ auto-disseminate pipeline
- ✅ Knowledge MCP publicado
- ✅ Stripe billing infra (Guard Brasil)
- ✅ TASKS.md + HARVEST.md + handoffs = matéria-prima para conteúdo

**Precisa construir (P0):**
- [ ] `status.egos.ia.br` — versão pública (read-only) do HQ mostrando métricas EGOS em tempo real (sem dados sensíveis)
- [ ] `egos-site/` ou reativar domínio — landing page + blog (pode ser Astro / Next static / MDX simples)
- [ ] Sistema de assinatura R$ 20/mês (Stripe recorrente — infra já existe, só precisa de produto separado)
- [ ] Gate de acesso à comunidade WhatsApp/Notion (bot Telegram simples ou manual no início)
- [ ] Template de artigo técnico + primeiro artigo âncora

**Precisa construir (P1):**
- [ ] Notion workspace compartilhado com membros (templates, decisões, roadmap)
- [ ] Paperclip modo "viewer" para não-admins (ou subconjunto de dashboards)
- [ ] Newsletter setup
- [ ] Bot WhatsApp/Telegram para onboarding automático

**NÃO construir agora (§1 anti-proliferação):**
- ❌ Observatory 3D com React Three Fiber (over-engineering)
- ❌ Certificação NFT / tokenização / $ETHIK integration (deixar para depois da validação)
- ❌ Sistema de pagamento próprio (usar Stripe direto)
- ❌ Mobile app da comunidade
- ❌ Plataforma de curso proprietária (começar com Notion + WhatsApp + GitHub)

---

## 6. Riscos e armadilhas que vejo

| Risco | Severidade | Por que aconteceria | Mitigação |
|---|---|---|---|
| Enio vira "o cara do conteúdo" e para de construir | 🔴 Alta | Conteúdo técnico profundo consome tempo pesado | Regra: 80% do tempo continua sendo código, 20% é conteúdo. Publicar = documentar o que já foi feito, não criar coisa nova. |
| Comunidade R$ 20/mês com 5 pessoas vira obrigação sem retorno | 🟡 Média | Expectativa de engajamento > entrega real | Começar com cap de 20-30 membros manual. Só abrir mais quando estiver confortável. |
| Artigo âncora vira projeto infinito que nunca publica | 🔴 Alta | Perfeccionismo de researcher-builder | Deadline duro: 4 semanas do primeiro commit ao push. Versão v1 não precisa ter tudo. |
| Stack de comunidade vira mais 1 produto para manter | 🟡 Média | Criação de ferramentas custom para a comunidade | Usar SaaS/MVP sempre que possível. Notion, WhatsApp, Stripe — nada custom no começo. |
| Vazar dados sensíveis em dashboard público | 🔴 Alta | Reuso de infra privada | Dashboard público é read-only e passa por Guard Brasil antes. Nunca expor br-acc bruto, só métricas agregadas. |
| Comunidade vira câmara de eco, não constrói nada | 🟡 Média | Membros passivos só consomem | Critério: quem não contribui em 90 dias sai sem atrito. Focar em fazedores. |
| Enio burnout com conversas na comunidade | 🔴 Alta | Comunidade exige presença humana | Horário fixo de resposta (ex: 2x/semana). Fora do horário, bot Claude responde com contexto EGOS. |
| Artigo viraliza antes do produto estar pronto | 🟡 Média | Expectativa > entrega | OK ter lista de espera. Primeiro artigo pode ser "venho aqui compartilhar o que construí e o que vem" sem pitch de venda. |
| Competição/reação de Rocketseat/tabnews/etc. | 🟢 Baixa | Eles são grandes demais para se importar no começo | Continuar sendo específico (multi-agent + governança). Não competir em formação tradicional. |
| Problema legal/LGPD de dados públicos em comunidade | 🟡 Média | Alguém usa br-acc para coisa errada | Termos de uso claros. Guard Brasil na entrada. Nunca expor raw dump. |

---

## 6.5 Plano de Encapsulamento Top-Down (NOVO, 2026-04-09)

Tu disse: "começando de cima, começando do kernel, começando da parte principal e disseminando por todo o sistema". Vou propor a ordem exata de camadas e o que cada uma entrega.

### Camada 0 — Kernel do Kernel (semana 1)
**O que é:** `~/.claude/CLAUDE.md` (global) + `egos/CLAUDE.md` (projeto) + `.guarani/RULES_INDEX.md` + `.guarani/PREFERENCES.md`
**Ação:** Auditar cada uma das 32 seções do global CLAUDE.md. Marcar: (a) provada e ativa, (b) parcial, (c) aspirational/remover. Adicionar §33 Evidence-First Principle.
**Entregável:** `docs/audit/KERNEL_AUDIT_2026-04-09.md` — lista completa com status de cada regra.
**Prova:** Cada regra ativa tem comando reproduzível (`bash -c '...'`) que mostra ela funcionando.

### Camada 1 — Agents Registry (semana 2)
**O que é:** `agents/registry/agents.json` + todos os agents em `agents/agents/*.ts`
**Ação:** Catalogar cada agent: nome, função, última execução, dependências, SLA, testes existentes. Matar agents mortos (prove-or-kill). Documentar cada um em `docs/agents/<name>.md` com seção "Prova de vida".
**Entregável:** `docs/agents/INDEX.md` + 1 doc por agent + testes de smoke.
**Prova:** `bun agent:lint` passa + cada agent roda em modo `--dry` com output determinístico + screenshot de `agent_events` Supabase mostrando execuções reais dos últimos 7 dias.

### Camada 2 — Governance Pipeline (semana 3)
**O que é:** Pre-commit hooks, CCR jobs, Doc-Drift Shield, vocab guard, file-intelligence, auto-disseminate
**Ação:** Documentar cada hook do `.husky/pre-commit` linha a linha. Mostrar: o que bloqueia, por que, com exemplo de falha real. Unificar no `docs/governance/PIPELINE_SPEC.md`.
**Entregável:** Doc completo + diagrama do pipeline (Mermaid) + exemplos de falhas reais dos últimos 30 dias.
**Prova:** Cada gate tem teste que injeta violação e verifica bloqueio. `bun test:governance` roda tudo.

### Camada 3 — Multi-Provider Routing & MCP Stack (semana 4)
**O que é:** Qwen→Gemini→OpenRouter fallback chain + 3 MCP servers próprios (egos-governance, codebase-memory, egos-memory) + paperclip + hermes
**Ação:** Documentar a stack completa com justificativa de escolha + 2-3 alternativas por componente (requisito do Enio: sempre mostrar alternativas). Incluir benchmarks reais de custo, latência, qualidade.
**Entregável:** `docs/stack/PROVIDER_ROUTING.md` + `docs/stack/MCP_SERVERS.md` + `docs/stack/ALTERNATIVES_MATRIX.md`
**Prova:** Script `bun scripts/bench-providers.ts` que roda os 9 testes do llm-test-suite.ts contra cada provider e publica resultado em `docs/benchmarks/YYYY-MM-DD.md`.

### Camada 4 — Produtos Core (semanas 5-6)
**O que é:** Guard Brasil + 852 + Forja + Gem Hunter + KB/Knowledge MCP + Gateway
**Ação:** Para cada um: arquitetura, stack escolhida, alternativas, métricas atuais, como testar localmente, como acessar produção, roadmap honesto. Padrão único de documentação.
**Entregável:** 6 docs `docs/products/<produto>.md` seguindo template único + 1 doc mestre `docs/products/INDEX.md`.
**Prova:** Cada produto tem endpoint de health + dashboard tile + último deploy link + test suite que roda na pipeline.

### Camada 5 — Data & Observability (semana 7)
**O que é:** br-acc Neo4j (83.7M nós) + Supabase tables + CCR reports + heartbeat + obs-central (a construir como script, não agent)
**Ação:** Inventário de dados. Esquema público (sanitizado) do que tem no Neo4j. Tabelas Supabase com finalidade. Políticas de retenção. LGPD compliance check via Guard Brasil.
**Entregável:** `docs/data/INVENTORY.md` + `docs/data/LGPD_COMPLIANCE.md` + `scripts/obs-central.ts` rodando cron.
**Prova:** Dashboard público de observabilidade mostrando containers/agents/jobs em tempo real.

### Camada 6 — Dashboards Públicos & Evidence Hub (semanas 8-9)
**O que é:** `status.egos.ia.br` (a construir) + versão pública do egos-hq + tiles de prova ligados aos manifests
**Ação:** Construir versão read-only do HQ que mostra: agents ativos, últimos commits (link GitHub), lastrun de CCR jobs, health de serviços públicos (Guard, 852, Gem Hunter), contagem de capabilities, estrelas GitHub, últimos 10 artigos publicados. Gate via Guard Brasil antes de qualquer render.
**Entregável:** `status.egos.ia.br` live + `docs/public/STATUS_PAGE.md` explicando cada métrica.
**Prova:** É o próprio dashboard — auto-evidente.

### Camada 7 — Artigo Âncora Showcase (semanas 10-12)
**O que é:** O showcase público: "EGOS: plataforma multi-agente brasileira open source — mapa visual completo"
**Ação:** Compilar todo o trabalho das camadas 0-6 em um artigo único navegável. Cada seção linka para a camada correspondente. Cada número linka para claim no manifest + dashboard.
**Entregável:** Publicação em Substack + egos.ia.br + crosspost tabnews + thread X.com + post LinkedIn.
**Prova:** O próprio artigo — cada claim é clicável.

### Regras duras de execução
1. **Nenhuma camada avança sem Evidence Gate da anterior passando.** Camada 2 só começa quando Camada 1 tem `bun agent:lint` passando limpo + 100% dos agents com prova de vida.
2. **Nenhum commit durante encapsulamento adiciona feature nova.** Só consolida, testa, documenta, remove morto.
3. **Todo commit inclui `EVIDENCE:` no body apontando para prova atualizada.** Isso vira regra no commit lint.
4. **Todo push para main passa por Guard Brasil auditando logs e docs do próprio commit.** Se vazar PII em doc/log → bloqueia.
5. **Toda semana de encapsulamento termina com dry-run do showcase.** Pega um trecho do artigo âncora ainda não escrito e tenta escrever com base só nas provas existentes. Onde travar = onde falta prova.

---

## 7. Perguntas em aberto (para iteração com Enio)

Vou dividir em 3 camadas. Por favor responda no ritmo que quiser — pode ser uma por vez, pode ser todas. Sem pressa.

### 7.1 Camada Decisão (precisamos alinhar antes de mexer em código)

**Q1. Artigo âncora — qual é o nome/ângulo?**
Tenho 4 rascunhos de ângulo possíveis:
- **(a) Memoir técnico:** "18 meses construindo EGOS solo — o que eu aprendi sobre arquitetura multi-agente governada"
- **(b) Manifesto:** "Por que sistemas de IA governados são o próximo diferencial (e por que quase ninguém tá construindo)"
- **(c) Showcase:** "EGOS: uma plataforma multi-agente brasileira open source — mapa visual completo"
- **(d) Contrarian:** "Não construa mais um wrapper de LLM: o que construir no lugar (com provas do que eu construí)"

Qual ressoa contigo? Ou tu prefere outro ângulo?

**Q2. Público-alvo prioritário do artigo âncora — se tiver que escolher UM:**
- (a) Devs brasileiros sênior interessados em arquitetura (nicho técnico, baixa conversão mas alta qualidade)
- (b) Tomadores de decisão em empresas médias BR (buscando consultoria / compra)
- (c) Comunidade internacional de agent builders (inglês, maior alcance, menor conversão BR)
- (d) Mix — escrever em PT-BR mas com tradução EN disponível

**Q3. Nome da comunidade — qual te parece mais coerente com teu jeito?**
- (a) **Observatório EGOS** (reaproveita conceito Live School histórico, não hype)
- (b) **EGOS Lab** (simples, laboratório público)
- (c) **Mesa EGOS** (brasileiro, convivial, "sentar na mesa e construir junto")
- (d) **Estúdio EGOS** (artesão técnico)
- (e) **Live School EGOS** (mantém nome original, força reconhecimento do arquivo)
- (f) Outro que tu pensa agora

**Q4. Preço R$ 20/mês — a qual nível de acesso corresponde?**
- (a) Tudo: WhatsApp + Notion + encontros ao vivo + acesso ao Enio + dashboards
- (b) Tier único "apoio simbólico" (acesso básico) + Tier premium pago separado para 1:1
- (c) Acesso grátis ao básico + R$ 20/mês para "co-construtor" (vota em prioridades, entra em calls, contribui no código)
- (d) Outro modelo

**Q5. Qual é a **primeira métrica de sucesso** do Caminho B+C que se atingida faz tu dormir bem?**
Exemplos possíveis:
- 500 leitores únicos no artigo âncora na primeira semana?
- 10 membros pagantes na comunidade nos primeiros 30 dias?
- 1 PR de comunidade aceito no EGOS kernel?
- 100 estrelas no repo `enioxt/egos`?
- 1 convite para palestrar em evento técnico BR?
- Outra?

### 7.2 Camada Arquitetura (depois de alinhar decisão)

**Q6. `status.egos.ia.br` público — que métricas expor e quais esconder?**
Meu draft: expor **nº de agents ativos, últimos 10 commits (link para GitHub), lastrun de CCR jobs, uptime de serviços públicos (Guard, 852, Gem Hunter), contagem de capabilities no CAPABILITY_REGISTRY, estrelas/forks no GitHub**. Esconder: dados do br-acc, conteúdo de TASKS.md privado, handoffs, credentials. Concorda? Algo a adicionar/tirar?

**Q7. Stack do blog/site:** 
Já tem `egos-site/` em alguma forma? Quer que eu pesquise o estado atual e proponha reutilização, ou começar do zero? Se começar do zero, preferência: Astro (mais leve, MDX nativo) ou Next.js (familiar, mais pesado)?

**Q8. Moderação/governança da comunidade:**
Tu quer ser o único moderador no começo? Ou já pensar em uma "equipe de 2-3 co-stewards" convidados desde cedo (amigos da comunidade, testadores)?

### 7.3 Camada Execução (depois de arquitetura ok)

**Q9. Cronograma agressivo vs realista:**
- Agressivo: artigo âncora em 4 semanas + comunidade aberta em 6 semanas
- Realista: artigo âncora em 8 semanas + comunidade aberta em 12 semanas
- Ambos contam com o tempo atual de estudos, TASKS.md pendentes, etc.

Qual faz sentido? Lembrando §23 (sem urgência) — mas também lembrando que perfeição é inimigo.

**Q10. Primeira "aula" / primeira call pública — formato:**
- (a) Screencast gravado mostrando uma sessão de trabalho no EGOS (1-2h, sem edição pesada)
- (b) Call ao vivo aberta (qualquer um entra, grava-se)
- (c) Tutorial escrito estruturado + vídeo curto
- (d) Thread X.com longa com screenshots + deep-dive em 1 padrão específico do EGOS

---

## 8. Próximos passos (só depois que Enio responder 7.1)

**NADA de código até termos Q1-Q5 respondidas.** Já caímos em "construir antes de decidir" várias vezes. Dessa vez vamos fazer devagar.

Depois das respostas:
1. Atualizar este doc com decisões
2. Criar `docs/strategy/ARTIGO_ANCORA_OUTLINE.md` com draft do artigo
3. Criar `docs/strategy/COMUNIDADE_EGOS_SETUP.md` com stack técnica final
4. Criar novo section no TASKS.md: "### 🔭 Path B/C — Case Study Público + Comunidade"
5. Começar Dia 1 de execução

---

## 9. Meta-notas para sessões futuras (qualquer agente)

- Este doc é vivo. Atualize aqui, não crie arquivos paralelos. SSOT-First (§26).
- A decisão é Caminho B primário + C paralelo, A acontece depois. Não reverta sem discussão com Enio.
- Live School é conceito histórico do EGOS (2025), não ideia nova. Redescoberta, não invenção.
- Não caia na alucinação "instrutores autônomos" que Perplexity/Kimi propagaram. Forja = metalurgia.
- §23 GTM-First v2 (researcher-builder, sem urgência) aplica aqui. §24.1 NO JOBS aplica.
- Ordem das decisões importa: Q1-Q5 antes de qualquer código. Sem pressa.

---

**Próxima ação:** Enio responde pelo menos Q1, Q3 e Q5. O resto pode vir depois.
