# EGOS Environment Registry

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** canonical host/tool/MCP environment map
- **Summary:** Agnostic registry of approved hosts, runtime traits, and MCP capability surfaces across the EGOS ecosystem.
- **Read next:**
  - `docs/ACTIVATION_FLOW.md` — activation contract
  - `docs/MCP_SCOPE_POLICY.md` — least-privilege scopes
  - `TASKS.md` — open environment/governance tasks
<!-- llmrefs:end -->

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-21
> **TYPE:** AGNÓSTICO - Central de Mapeamento de Ferramentas, MCPs e Ambientes de IA do Ecossistema EGOS.

---

## Filosofia Agnóstica
O Sistema EGOS (`EGOSv3 Kernel` e extensões foliáceas) é programado para ser mantido, evoluído e auditado por *qualquer Agente Autônomo ou LLM Integrada*, não devendo possuir amarras de linguagem natural focadas em IDEs isoladas (ex: "No Windsurf você deve").

Todos os metaprompts, workflows e protocolos operacionais referem-se ao ator como **"o Agente"** ou **"a Inteligência Operacional"**. As ferramentas do Agente não são ditadas pela IDE, mas sim pela infraestrutura MCP (Model Context Protocol) mapeada neste documento.

## 1. Hosts Homologados (Ambientes de IA)

O ecossistema reconhece os seguintes domínios hospedeiros (hosts) e abstrai as capacidades de cada um:

### A. Antigravity IDE (DeepMind / Gemini Stack)
- **Papel:** Host principal de governança, resolução complexa de bugs de baixo nível computacional, infraestrutura Unix e manipulação visual contínua (Aura/Video-Context).
- **Atributos:**
  - `Context Type:` Vision/Terminal
  - `Autonomy:` Alta (execução paralela, file validation strictness)
  - `Workspace Scope:` Isolamento restrito mitigável via Multi-Root `.code-workspace`.

### B. Windsurf IDE (Cascade Stack)
- **Papel:** Editor tático-operacional para refatorações de front-end ultrarrápidas, linting, code reviews contextuais e Vibe Coding direcional.
- **Atributos:**
  - `Context Type:` Symlink/Semantic Codebase Parsing
  - `Autonomy:` Media (User in the loop frequente)
  - `Ruleset:` `.windsurfrules`

### C. Cline (VS Code Extension - Claude/OpenRouter)
- **Papel:** Motor complementar de desenvolvimento focado em delegação via MCP e customização densa de provedores agnósticos (DashScope/Haiku).
- **Atributos:**
  - `Context Type:` Task-oriented (Chat history base)
  - `Autonomy:` Elevada em execução remota de scripts.

---

## 2. Model Context Protocol (MCP) Map

Os seguintes servidores MCP suportam o ecossistema EGOS local. **Atenção (P0 de Segurança): NENHUM SERVIDOR MCP deve possuir Environment Variables injetadas hardcoded (plaintext) em arquivos de configuração JSON.** Todas as chaves devem estar centralizadas no cofre `~/.egos/.env` hospedado localmente no Kernel.

| MCP Server | Escopo / Capacidades | Comando de Inicialização (Agnostic) | Segurança |
|------------|---------------------|------------------------------------|-----------|
| `clarity` | Dados UX/UI da M. Clarity (heatmaps, replays de `852 Inteligência`) | `npx @egos-ai/mcp-clarity` | Requer `$CLARITY_API_KEY` |
| `egos-core` | Núcleo de gestão do sistema Mycelium (Tsun-Cha Protocol) | `npx @egos-ai/mcp-core` | Internal |
| `exa` | IA Web Search (Notícias, Pesquisas técnicas) / Gem Hunter Utils | `npx @exa/mcp-server` | Requer `$EXA_API_KEY` |
| `filesystem` | Navegação restrita de discos paralelos fora do Workspace | nativo (Node/Python) | - |
| `github` | Gestão de Issues, PRs e CI/CD actions inter-repos | `npx @modelcontextprotocol/server-github` | Requer `$GITHUB_TOKEN` |
| `memory` | Gravação de padrões em Grafo de conhecimento (`create_memory()`) | nativo (SQLite/Local) | Internal |
| `supabase-mcp` | Orquestração DDL global, RLS policies, migrations | `npx -y @supabase/mcp` | Requer `$SUPABASE_SERVICE_KEY` |

---

## 3. Diretrizes de Injeção de Contexto

Se for necessário criar ou portar um Workflow para o diretório `.agents/workflows` ou `.windsurf/workflows`, o dev IA **NÃO PODE**:
1. Citar extensões de navegadores ou plugins exclusivos do VS Code.
2. Armazenar secrets em pastas do usuário ocultas (`~/.cline/data` ou similares).
3. Hardcodar diretórios-folha. Referencie sempre pelo prefixo: `$ROOT/leaf-repo`.

> **Este Documento é o SSOT (Single Source of Truth) para integrações de IA no EGOS. Atualize-o sempre que um novo MCP for instalado ou deprecado.**
