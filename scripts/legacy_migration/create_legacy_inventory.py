#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Legacy Inventory Generator
-------------------------------
Este script gera um inventário completo de arquivos legados no sistema EGOS.
Ele identifica arquivos com base em padrões, localização e extensão, e gera
um relatório em formato Markdown com metadados relevantes.

Parte da tarefa LEGACY-SCAN-01 do roadmap do EGOS.
"""

import os
import sys
import argparse
import logging
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("legacy_inventory")

# Constantes
DEFAULT_LEGACY_DIRS = [
    "strategic-thinking",
    "STRATEGIC_THINKING",
    "research",
    "legacy",
    "archive",
    "old",
    "backup",
    "histórico",
    "historico",
]

DEFAULT_LEGACY_EXTENSIONS = [
    ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml",
    ".bat", ".sh", ".ps1", ".sql", ".ipynb", ".csv", ".tsv", ".xml"
]

# Padrões que indicam conteúdo legado
LEGACY_PATTERNS = [
    "legacy", "deprecated", "old", "archive", "backup", "histórico", "v1", "v0",
    "draft", "rascunho", "todo", "fixme", "obsolete", "outdated"
]

# Subsistemas EGOS para categorização
EGOS_SUBSYSTEMS = [
    "ATLAS", "CORUJA", "CRONOS", "ETHIK", "HARMONY", "KOIOS", 
    "MYCELIUM", "NEXUS", "SYNAPSE"
]

class LegacyInventoryGenerator:
    """Gerador de inventário de arquivos legados no sistema EGOS."""
    
    def __init__(
        self, 
        root_dir: str,
        output_file: str,
        legacy_dirs: Optional[List[str]] = None,
        legacy_extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        min_age_days: int = 0,
        include_all_files: bool = False,
        verbose: bool = False
    ):
        """
        Inicializa o gerador de inventário.
        
        Args:
            root_dir: Diretório raiz para iniciar a busca
            output_file: Arquivo de saída para o inventário (formato Markdown)
            legacy_dirs: Lista de nomes de diretórios considerados legados
            legacy_extensions: Lista de extensões de arquivo a serem incluídas
            exclude_dirs: Lista de diretórios a serem excluídos da busca
            exclude_patterns: Lista de padrões a serem excluídos
            min_age_days: Idade mínima em dias para considerar um arquivo como legado
            include_all_files: Se True, inclui todos os arquivos, não apenas os que parecem legados
            verbose: Se True, exibe informações detalhadas durante a execução
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_file = output_file
        self.legacy_dirs = legacy_dirs or DEFAULT_LEGACY_DIRS
        self.legacy_extensions = legacy_extensions or DEFAULT_LEGACY_EXTENSIONS
        self.exclude_dirs = exclude_dirs or ["venv", ".git", ".github", "node_modules", "__pycache__", ".vscode"]
        self.exclude_patterns = exclude_patterns or []
        self.min_age_days = min_age_days
        self.include_all_files = include_all_files
        self.verbose = verbose
        
        # Configuração de logging
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        # Estatísticas
        self.stats = {
            "total_files_scanned": 0,
            "legacy_files_found": 0,
            "by_extension": {},
            "by_subsystem": {},
            "by_age": {
                "recent": 0,  # < 30 dias
                "medium": 0,  # 30-90 dias
                "old": 0      # > 90 dias
            }
        }
        
        logger.info(f"Iniciando gerador de inventário no diretório: {self.root_dir}")
        logger.debug(f"Diretórios legados: {self.legacy_dirs}")
        logger.debug(f"Extensões: {self.legacy_extensions}")
        logger.debug(f"Diretórios excluídos: {self.exclude_dirs}")
    
    def is_legacy_file(self, file_path: str, file_stat: os.stat_result) -> bool:
        """
        Determina se um arquivo é considerado legado com base em vários critérios.
        
        Args:
            file_path: Caminho completo para o arquivo
            file_stat: Resultado de os.stat() para o arquivo
            
        Returns:
            bool: True se o arquivo for considerado legado, False caso contrário
        """
        if self.include_all_files:
            return True
            
        # Verificar idade
        if self.min_age_days > 0:
            file_age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(file_stat.st_mtime)).days
            if file_age_days >= self.min_age_days:
                return True
        
        # Verificar se está em um diretório legado
        for legacy_dir in self.legacy_dirs:
            if f"/{legacy_dir}/" in file_path.replace("\\", "/") or f"\\{legacy_dir}\\" in file_path:
                return True
        
        # Verificar nome do arquivo
        file_name = os.path.basename(file_path).lower()
        for pattern in LEGACY_PATTERNS:
            if pattern in file_name:
                return True
        
        # Verificar conteúdo (apenas para arquivos de texto pequenos)
        if os.path.getsize(file_path) < 1024 * 100:  # Limitar a 100KB
            try:
                _, ext = os.path.splitext(file_path)
                if ext.lower() in ['.txt', '.md', '.py', '.js', '.html', '.bat', '.sh', '.ps1']:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # Ler apenas os primeiros 1000 caracteres
                        for pattern in LEGACY_PATTERNS:
                            if pattern in content.lower():
                                return True
            except Exception as e:
                logger.debug(f"Erro ao ler conteúdo do arquivo {file_path}: {e}")
        
        return False
    
    def get_file_metadata(self, file_path: str, file_stat: os.stat_result) -> Dict[str, Any]:
        """
        Extrai metadados de um arquivo.
        
        Args:
            file_path: Caminho completo para o arquivo
            file_stat: Resultado de os.stat() para o arquivo
            
        Returns:
            Dict: Dicionário com metadados do arquivo
        """
        rel_path = os.path.relpath(file_path, self.root_dir)
        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_path)
        
        # Calcular idade
        mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
        age_days = (datetime.datetime.now() - mod_time).days
        
        # Determinar subsistema
        subsystem = "Unknown"
        for sys in EGOS_SUBSYSTEMS:
            if f"/subsystems/{sys}/" in file_path.replace("\\", "/") or f"\\subsystems\\{sys}\\" in file_path:
                subsystem = sys
                break
        
        # Atualizar estatísticas
        self.stats["total_files_scanned"] += 1
        
        # Extensão
        ext_key = ext.lower() if ext else "no_extension"
        if ext_key not in self.stats["by_extension"]:
            self.stats["by_extension"][ext_key] = 0
        self.stats["by_extension"][ext_key] += 1
        
        # Subsistema
        if subsystem not in self.stats["by_subsystem"]:
            self.stats["by_subsystem"][subsystem] = 0
        self.stats["by_subsystem"][subsystem] += 1
        
        # Idade
        if age_days < 30:
            self.stats["by_age"]["recent"] += 1
        elif age_days < 90:
            self.stats["by_age"]["medium"] += 1
        else:
            self.stats["by_age"]["old"] += 1
        
        return {
            "path": rel_path,
            "name": file_name,
            "extension": ext.lower() if ext else "",
            "size_bytes": file_stat.st_size,
            "size_human": self._format_size(file_stat.st_size),
            "modified": mod_time.strftime("%Y-%m-%d"),
            "age_days": age_days,
            "subsystem": subsystem
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def scan_directory(self) -> List[Dict[str, Any]]:
        """
        Escaneia o diretório em busca de arquivos legados.
        
        Returns:
            List[Dict]: Lista de metadados de arquivos legados
        """
        legacy_files = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Filtrar diretórios excluídos
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                
                # Verificar extensão
                if ext.lower() not in self.legacy_extensions:
                    continue
                
                # Verificar padrões excluídos
                skip = False
                for pattern in self.exclude_patterns:
                    if pattern in file_path:
                        skip = True
                        break
                if skip:
                    continue
                
                try:
                    file_stat = os.stat(file_path)
                    
                    # Verificar se é legado
                    if self.is_legacy_file(file_path, file_stat):
                        metadata = self.get_file_metadata(file_path, file_stat)
                        legacy_files.append(metadata)
                        self.stats["legacy_files_found"] += 1
                        
                        if self.verbose and self.stats["legacy_files_found"] % 100 == 0:
                            logger.info(f"Encontrados {self.stats['legacy_files_found']} arquivos legados até agora...")
                except Exception as e:
                    logger.warning(f"Erro ao processar arquivo {file_path}: {e}")
        
        return legacy_files
    
    def generate_markdown_report(self, legacy_files: List[Dict[str, Any]]) -> None:
        """
        Gera relatório em formato Markdown com os arquivos legados encontrados.
        
        Args:
            legacy_files: Lista de metadados de arquivos legados
        """
        # Ordenar por caminho
        legacy_files.sort(key=lambda x: x["path"])
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# Inventário de Arquivos Legados - EGOS\n\n")
            f.write(f"**Data de Geração:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Estatísticas
            f.write("## Estatísticas\n\n")
            f.write(f"- **Total de Arquivos Escaneados:** {self.stats['total_files_scanned']}\n")
            f.write(f"- **Arquivos Legados Encontrados:** {self.stats['legacy_files_found']}\n\n")
            
            # Por extensão
            f.write("### Por Extensão\n\n")
            f.write("| Extensão | Quantidade |\n")
            f.write("|----------|------------|\n")
            for ext, count in sorted(self.stats["by_extension"].items(), key=lambda x: x[1], reverse=True):
                f.write(f"| {ext} | {count} |\n")
            f.write("\n")
            
            # Por subsistema
            f.write("### Por Subsistema\n\n")
            f.write("| Subsistema | Quantidade |\n")
            f.write("|------------|------------|\n")
            for sys, count in sorted(self.stats["by_subsystem"].items(), key=lambda x: x[1], reverse=True):
                f.write(f"| {sys} | {count} |\n")
            f.write("\n")
            
            # Por idade
            f.write("### Por Idade\n\n")
            f.write("| Faixa | Quantidade |\n")
            f.write("|-------|------------|\n")
            f.write(f"| Recente (<30 dias) | {self.stats['by_age']['recent']} |\n")
            f.write(f"| Médio (30-90 dias) | {self.stats['by_age']['medium']} |\n")
            f.write(f"| Antigo (>90 dias) | {self.stats['by_age']['old']} |\n")
            f.write("\n")
            
            # Lista de arquivos
            f.write("## Lista de Arquivos Legados\n\n")
            f.write("| Caminho | Tamanho | Modificado | Idade (dias) | Subsistema |\n")
            f.write("|---------|---------|------------|--------------|------------|\n")
            
            for file in legacy_files:
                path_md = file["path"].replace(" ", "%20")  # Escapar espaços para links Markdown
                f.write(f"| [{file['path']}]({path_md}) | {file['size_human']} | {file['modified']} | {file['age_days']} | {file['subsystem']} |\n")
            
            logger.info(f"Relatório gerado com sucesso em {self.output_file}")
    
    def run(self) -> None:
        """Executa o processo completo de geração de inventário."""
        logger.info("Iniciando escaneamento de diretórios...")
        legacy_files = self.scan_directory()
        logger.info(f"Escaneamento concluído. Encontrados {len(legacy_files)} arquivos legados.")
        
        logger.info("Gerando relatório Markdown...")
        self.generate_markdown_report(legacy_files)
        logger.info("Processo concluído com sucesso!")


def main():
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(description="Gerador de inventário de arquivos legados do EGOS")
    parser.add_argument("--root", default=".", help="Diretório raiz para iniciar a busca")
    parser.add_argument("--output", default="legacy_inventory_full.md", help="Arquivo de saída (formato Markdown)")
    parser.add_argument("--min-age", type=int, default=0, help="Idade mínima em dias para considerar um arquivo como legado")
    parser.add_argument("--include-all", action="store_true", help="Incluir todos os arquivos, não apenas os que parecem legados")
    parser.add_argument("--verbose", action="store_true", help="Exibir informações detalhadas durante a execução")
    parser.add_argument("--exclude-dirs", nargs="+", help="Diretórios adicionais a serem excluídos")
    parser.add_argument("--legacy-dirs", nargs="+", help="Diretórios adicionais a serem considerados legados")
    parser.add_argument("--extensions", nargs="+", help="Extensões de arquivo a serem incluídas")
    
    args = parser.parse_args()
    
    # Combinar listas de exclusão
    exclude_dirs = DEFAULT_LEGACY_DIRS.copy()
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)
    
    # Combinar listas de diretórios legados
    legacy_dirs = DEFAULT_LEGACY_DIRS.copy()
    if args.legacy_dirs:
        legacy_dirs.extend(args.legacy_dirs)
    
    # Combinar listas de extensões
    extensions = DEFAULT_LEGACY_EXTENSIONS.copy()
    if args.extensions:
        extensions.extend(args.extensions)
    
    generator = LegacyInventoryGenerator(
        root_dir=args.root,
        output_file=args.output,
        legacy_dirs=legacy_dirs,
        legacy_extensions=extensions,
        exclude_dirs=exclude_dirs,
        min_age_days=args.min_age,
        include_all_files=args.include_all,
        verbose=args.verbose
    )
    
    generator.run()


if __name__ == "__main__":
    main()
