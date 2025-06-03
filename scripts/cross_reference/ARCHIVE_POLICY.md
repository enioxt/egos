---
title: EGOS Cross-Reference Tools Archive Policy
description: Política e procedimentos para arquivamento de scripts e documentação
created: 2025-05-21
updated: 2025-05-21
author: EGOS Development Team
version: 1.0.0
status: Active
tags: [archive, policy, cross-reference, documentation, standards]
---

# EGOS Cross-Reference Tools Archive Policy

Este documento define a política oficial para arquivamento de scripts, configurações e documentação no ecossistema EGOS, com foco específico nas ferramentas de referência cruzada.

<!-- crossref_block:start -->
- 🔗 Reference: [README.md](./README.md)
- 🔗 Reference: [WORK_2025_05_21_update.md](./WORK_2025_05_21_update.md)
- 🔗 Reference: [implementation_plan.md](./implementation_plan.md)
- 🔗 Reference: [ROADMAP.md](../ROADMAP.md)
<!-- crossref_block:end -->

## Princípios Fundamentais

1. **Preservação Evolutiva**: Nenhum código ou documento deve ser excluído permanentemente, apenas arquivado.
2. **Documentação Completa**: Todo arquivamento deve ser documentado com justificativa clara e referência a substitutos.
3. **Avaliação Rigorosa**: Arquivos só devem ser arquivados após avaliação formal usando o EGOS Script Analysis Framework.
4. **Aprovação Necessária**: Arquivamento de scripts de produção requer aprovação documentada.
5. **Reversibilidade**: Todo arquivamento deve ser facilmente reversível.

## Critérios para Arquivamento

Um arquivo só pode ser considerado para arquivamento se atender a pelo menos um dos seguintes critérios:

### Critérios para Scripts

1. **Obsolescência Funcional**: O script foi completamente substituído por outro com funcionalidade igual ou superior.
2. **Redundância Comprovada**: O script duplica funcionalidade já disponível em outro script mais robusto.
3. **Problemas Críticos**: O script contém erros críticos que não podem ser corrigidos sem reescrita completa.
4. **Dependências Obsoletas**: O script depende de bibliotecas ou APIs obsoletas ou inseguras.

### Critérios para Documentação

1. **Informação Desatualizada**: A documentação contém informações obsoletas que podem confundir os usuários.
2. **Substituição Completa**: A documentação foi completamente substituída por uma versão mais abrangente.
3. **Reorganização Estrutural**: A documentação foi reorganizada em uma nova estrutura.

### Critérios para Configurações

1. **Configuração Consolidada**: A configuração foi consolidada em um arquivo mais abrangente.
2. **Ambiente Obsoleto**: A configuração se refere a um ambiente que não existe mais.

## Processo de Arquivamento

O processo de arquivamento deve seguir estes passos obrigatórios:

### 1. Avaliação Formal

- Utilize o [EGOS Script Analysis Framework](../docs_egos/05_development/frameworks/script_analysis_framework.md) para avaliar o script.
- Documente a avaliação no formato padrão, incluindo pontuações em todas as dimensões.
- Identifique claramente qual script substituirá a funcionalidade (se aplicável).

### 2. Verificação de Dependências

- Verifique se outros scripts ou sistemas dependem do arquivo a ser arquivado.
- Documente todas as dependências e planos de migração.
- Certifique-se de que todas as dependências foram atualizadas antes do arquivamento.

### 3. Aprovação

- Para scripts de produção: Obtenha aprovação documentada.
- Para scripts experimentais: Notifique a equipe sobre o arquivamento planejado.

### 4. Documentação no Manifesto de Arquivamento

- Adicione uma entrada no [ARCHIVE_MANIFEST.md](./zz_archive/ARCHIVE_MANIFEST.md) com:
  - Nome do arquivo
  - Data de arquivamento
  - Justificativa detalhada
  - Script substituto (se aplicável)
  - Funcionalidades preservadas/perdidas
  - Autor do arquivamento

### 5. Arquivamento Físico

- Mova o arquivo para a pasta `zz_archive` apropriada:
  - Scripts: `zz_archive/obsolete_scripts/`
  - Configurações: `zz_archive/configs/`
  - Logs: `zz_archive/logs/`
  - Relatórios: `zz_archive/reports/`
  - Documentação: `zz_archive/docs/`
- Mantenha a estrutura de diretórios original dentro da pasta de arquivo.

### 6. Atualização da Documentação

- Atualize o README.md para refletir as mudanças.
- Atualize o WORK_yyyy_mm_dd_update.md com informações sobre o arquivamento.
- Atualize quaisquer documentos que façam referência ao arquivo arquivado.

## Scripts de Referência Protegidos

Os seguintes scripts são considerados implementações de referência e NÃO DEVEM ser arquivados sem um processo de revisão especial:

1. **file_reference_checker_ultra.py**: Implementação de referência para padrões visuais EGOS e otimizações de desempenho.
2. **purge_old_references.py**: Implementação de referência para operações destrutivas seguras.
3. **script_standards_scanner.py**: Implementação de referência para análise de conformidade com padrões.

## Restauração de Arquivos Arquivados

Se for necessário restaurar um arquivo arquivado:

1. Documente a justificativa para restauração.
2. Mova o arquivo de volta para sua localização original.
3. Atualize o ARCHIVE_MANIFEST.md para refletir a restauração.
4. Atualize a documentação relevante.

## Revisão da Política

Esta política deve ser revisada a cada 3 meses para garantir que continue atendendo às necessidades do projeto.

✧༺❀༻∞ EGOS ∞༺❀༻✧
