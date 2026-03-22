---
description: Avaliação de Gaps, Atualização de TASKS.md e Extração de Conhecimento por Repositório (NotebookLM Ready)
---
# Protocolo de Extração de Conhecimento e Análise de Gaps (Repo-by-Repo)

Este workflow define as regras estritas que o Agente EGOS deve seguir ao analisar qualquer repositório do ecossistema para gerar módulos de conhecimento e fechar lacunas de produção.

## 1. Diretrizes Principais
- **Foco em Produção Primeiro:** Priorize o mapeamento e a documentação profunda de integrações que *já estão em produção e funcionando*.
- **Sem Funcionalidade Oculta:** Se algo está rodando bem mas não está documentado no README ou na pasta `docs/`, a prioridade absoluta é documentar.
- **Geração de Módulos Mastigáveis:** A arquitetura do código deve refletir a capacidade de ser convertida em conteúdo/aulas.

## 2. Passo a Passo do Workflow (Execução Obrigatória)

Ao receber a instrução de focar em um repositório (ex: `br-acc`, `carteira-livre`), execute sequencialmente:

1. **Reconhecimento de Terreno:**
   - Leia o `AGENTS.md` e `TASKS.md` atuais.
   - Execute o script `export-notebooklm-split.sh` para mapear o peso e a estrutura.

2. **Auditoria de Produção (Gap Analysis):**
   - Identifique features que estão completas no código fonte mas ausentes na documentação de uso.
   - Identifique integrações sistêmicas (ex: pagamentos, IA, envio de mensagens) que precisam de diagramas.

3. **Atualização do TASKS.md:**
   - Feche (marque como `[x]`) tarefas que você identificar que já estão no código.
   - Crie novas tarefas organizadas por: `[P0] Documentação de Produção`, `[P1] Integrações Essenciais`, `[P2] MVPs e Produtos Avançados`.

4. **Documentação e Empacotamento:**
   - Escreva a documentação faltante.
   - Re-rode o script de exportação fragmentada (`export-notebooklm-split.sh`) para gerar os `.md` finais e puros.
   - Entregue ao usuário o relatório: "O que estava pronto", "O que documentamos", "O que falta no TASKS.md".
