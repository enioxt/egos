@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/processes/legacy_cleanup_process.md

# Processo de Limpeza e Otimização de Arquivos Legados

**ID do Processo:** LEGACY-CLEANUP-01  
**Versão:** 1.0  
**Data:** 2025-04-18  
**Autor:** Cascade AI  
**Status:** Ativo  
**Subsistema Relacionado:** CRONOS, KOIOS  
**Princípios EGOS Aplicados:** Compassionate Temporality, Evolutionary Preservation, Conscious Modularity

## Visão Geral

Este documento descreve o processo sistemático para identificar, avaliar e remover com segurança arquivos legados desnecessários no sistema EGOS, mantendo a integridade do sistema e preservando informações valiosas.

## Motivação

O sistema EGOS acumulou aproximadamente 320.000 arquivos ocupando quase 6GB de espaço em disco. Este volume excessivo:
- Reduz o desempenho do sistema
- Aumenta o tempo de processamento em operações de busca e backup
- Dificulta a navegação e manutenção do código
- Consome recursos computacionais desnecessariamente

## Pré-requisitos

1. Acesso ao sistema de arquivos EGOS
2. Permissões para executar scripts Python
3. Ferramentas de backup CRONOS configuradas
4. Scripts de inventário de arquivos legados (`create_legacy_inventory.py`)

## Processo

### Fase 1: Backup e Preparação

1. **Backup Completo**
   ```powershell
   # Executar backup completo via CRONOS antes de qualquer remoção
   python subsystems/CRONOS/scripts/create_full_backup.py --tag "pre_cleanup"
   ```

2. **Configuração do Ambiente**
   ```powershell
   # Garantir que todas as dependências estejam instaladas
   pip install -r requirements.txt
   ```

### Fase 2: Análise e Inventário

1. **Geração de Inventário por Diretório**
   ```powershell
   # Gerar inventário para diretórios específicos
   python scripts/legacy_migration/create_legacy_inventory.py --root "strategic-thinking" --output docs/legacy/strategic_thinking_inventory.md --max-files 5000 --log-file legacy_scan.log --verbose --batch-size 500
   
   python scripts/legacy_migration/create_legacy_inventory.py --root "research" --output docs/legacy/research_inventory.md --max-files 5000 --log-file legacy_scan_research.log --verbose --batch-size 500
   
   python scripts/legacy_migration/create_legacy_inventory.py --root "backups" --output docs/legacy/backups_inventory.md --max-files 5000 --log-file legacy_scan_backups.log --verbose --batch-size 500
   ```

2. **Análise de Resultados**
   - Revisar os relatórios gerados em `docs/legacy/`
   - Identificar padrões de arquivos redundantes
   - Verificar candidatos à remoção sugeridos pelo sistema

### Fase 3: Remoção Incremental

1. **Remoção de Arquivos Redundantes em Backups**
   - Revisar o script de remoção gerado para backups
   - Remover arquivos redundantes em backups antigos
   ```powershell
   # Exemplo: Remover arquivos de backup redundantes
   # Descomente as linhas relevantes no script de remoção
   # .\docs\legacy\removal_script.ps1
   ```

2. **Remoção de Arquivos Temporários e de Teste**
   - Identificar e remover arquivos de teste, temporários e de cache
   ```powershell
   # Remover arquivos de cache e temporários
   Get-ChildItem -Path . -Include "__pycache__", "*.pyc", "*.pyo", ".pytest_cache" -Recurse -Force | Remove-Item -Recurse -Force
   ```

3. **Remoção de Arquivos Legados Processados**
   - Remover arquivos originais que já foram processados e padronizados
   ```powershell
   # Usar o script de remoção gerado, após revisão cuidadosa
   # Editar o script para descomentá-lo e executar em lotes
   ```

### Fase 4: Verificação e Documentação

1. **Verificação de Integridade**
   ```powershell
   # Executar testes do sistema para garantir que nada foi quebrado
   python -m pytest
   
   # Verificar funcionalidades críticas
   python subsystems/KOIOS/scripts/system_integrity_check.py
   ```

2. **Documentação das Alterações**
   - Registrar todos os arquivos removidos
   - Atualizar o inventário após a limpeza
   ```powershell
   # Gerar inventário atualizado
   python scripts/legacy_migration/create_legacy_inventory.py --root "." --output docs/legacy/post_cleanup_inventory.md --max-files 10000 --log-file post_cleanup.log --verbose
   ```

3. **Relatório de Otimização**
   - Documentar o espaço recuperado
   - Registrar quaisquer problemas encontrados
   - Atualizar o ROADMAP.md com o status da tarefa

## Boas Práticas

1. **Abordagem Incremental**
   - Remover arquivos em pequenos lotes
   - Verificar a integridade do sistema após cada lote

2. **Priorização**
   - Priorizar a remoção de arquivos grandes
   - Focar em diretórios com maior redundância
   - Começar com arquivos claramente obsoletos

3. **Preservação**
   - Manter pelo menos uma cópia de cada tipo de conteúdo legado
   - Preservar documentação histórica importante
   - Documentar decisões de remoção

4. **Automação**
   - Usar scripts para tarefas repetitivas
   - Automatizar a verificação pós-remoção
   - Manter logs detalhados de todas as operações

## Prevenção de Acúmulo Futuro

1. **Políticas de Retenção**
   - Estabelecer políticas claras para backups e arquivos temporários
   - Definir ciclos de vida para diferentes tipos de arquivos

2. **Limpeza Automática**
   - Implementar scripts de limpeza periódica
   - Configurar tarefas agendadas para remoção de arquivos temporários

3. **Monitoramento**
   - Monitorar o crescimento do sistema de arquivos
   - Estabelecer alertas para crescimento anormal

## Referências

- [Script de Inventário de Arquivos Legados](file:///c:/EGOS/scripts/legacy_migration/create_legacy_inventory.py)
- [Documentação do CRONOS - Backup e Restauração](file:///c:/EGOS/docs/subsystems/CRONOS/backup_restore.md)
- [Princípios EGOS - Compassionate Temporality](file:///c:/EGOS/docs/principles/compassionate_temporality.md)

---

*Este processo segue os princípios EGOS de Compassionate Temporality (respeitando o ciclo de vida natural dos artefatos), Evolutionary Preservation (mantendo a essência enquanto permite transformação) e Conscious Modularity (entendendo as relações entre componentes do sistema).*

✧༺❀༻∞ EGOS ∞༺❀༻✧