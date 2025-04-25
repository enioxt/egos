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
import pickle
import time
from typing import Dict, List, Optional, Set, Tuple, Any

# Configuração de logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger("legacy_inventory")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

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

# Extensões a serem excluídas (arquivos binários, mídia, etc.)
DEFAULT_EXCLUDE_EXTENSIONS = [
    ".exe", ".dll", ".so", ".dylib", ".obj", ".o", ".a", ".lib",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".tif", ".tiff",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".flv", ".mkv",
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    ".pyc", ".pyo", ".pyd", ".class", ".jar",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf"
]

# Diretórios a serem excluídos
DEFAULT_EXCLUDE_DIRS = [
    "venv", ".venv", "env", ".env", "virtualenv",
    ".git", ".github", ".gitlab", ".svn", ".hg",
    "node_modules", "bower_components", "jspm_packages",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".vscode", ".idea", ".vs", ".eclipse",
    "build", "dist", "target", "out",
    "logs", "log", "temp", "tmp"
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
        exclude_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        min_age_days: int = 0,
        max_size_mb: float = 10.0,
        max_files: int = 0,
        batch_size: int = 1000,
        checkpoint_file: Optional[str] = None,
        log_file: Optional[str] = None,
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
            exclude_extensions: Lista de extensões de arquivo a serem excluídas
            exclude_patterns: Lista de padrões a serem excluídos
            min_age_days: Idade mínima em dias para considerar um arquivo como legado
            max_size_mb: Tamanho máximo em MB para processar um arquivo
            max_files: Número máximo de arquivos a processar (0 = sem limite)
            batch_size: Número de arquivos a processar antes de salvar checkpoint
            checkpoint_file: Arquivo para salvar/carregar checkpoint
            log_file: Arquivo para salvar logs detalhados
            include_all_files: Se True, inclui todos os arquivos, não apenas os que parecem legados
            verbose: Se True, exibe informações detalhadas durante a execução
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_file = output_file
        self.legacy_dirs = legacy_dirs or DEFAULT_LEGACY_DIRS
        self.legacy_extensions = legacy_extensions or DEFAULT_LEGACY_EXTENSIONS
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.exclude_extensions = exclude_extensions or DEFAULT_EXCLUDE_EXTENSIONS
        self.exclude_patterns = exclude_patterns or []
        self.min_age_days = min_age_days
        self.max_size_mb = max_size_mb
        self.max_files = max_files
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file or "legacy_inventory_checkpoint.pkl"
        self.include_all_files = include_all_files
        self.verbose = verbose

        # Configuração de logging de arquivo
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_formatter)
            logger.addHandler(file_handler)

        # Configuração de nível de logging
        if verbose:
            logger.setLevel(logging.DEBUG)

        # Estatísticas
        self.stats = {
            "total_files_scanned": 0,
            "legacy_files_found": 0,
            "skipped_files": 0,
            "removal_candidates": 0,
            "by_extension": {},
            "by_subsystem": {},
            "by_age": {
                "recent": 0,  # < 30 dias
                "medium": 0,  # 30-90 dias
                "old": 0      # > 90 dias
            }
        }

        # Inicialização de dados de checkpoint
        self.processed_files = set()  # Arquivos já processados
        self.legacy_files = []  # Arquivos legados encontrados
        self.removal_candidates = []  # Candidatos à remoção
        self.last_checkpoint_time = time.time()
        self.start_time = time.time()

        # Carregar checkpoint se existir
        self._load_checkpoint()

        logger.info(f"Iniciando gerador de inventário no diretório: {self.root_dir}")
        logger.debug(f"Diretórios legados: {self.legacy_dirs}")
        logger.debug(f"Extensões incluídas: {self.legacy_extensions}")
        logger.debug(f"Extensões excluídas: {self.exclude_extensions}")
        logger.debug(f"Diretórios excluídos: {self.exclude_dirs}")

    def _load_checkpoint(self):
        """Carrega dados de checkpoint se o arquivo existir."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
                    self.processed_files = checkpoint_data.get('processed_files', set())
                    self.legacy_files = checkpoint_data.get('legacy_files', [])
                    self.removal_candidates = checkpoint_data.get('removal_candidates', [])
                    self.stats = checkpoint_data.get('stats', self.stats)
                logger.info(f"Checkpoint carregado: {len(self.processed_files)} arquivos já processados")
            except Exception as e:
                logger.warning(f"Erro ao carregar checkpoint: {e}")

    def _save_checkpoint(self, force=False):
        """Salva dados de checkpoint."""
        current_time = time.time()
        # Salvar a cada 5 minutos ou quando forçado
        if force or (current_time - self.last_checkpoint_time) > 300:
            try:
                checkpoint_data = {
                    'processed_files': self.processed_files,
                    'legacy_files': self.legacy_files,
                    'removal_candidates': self.removal_candidates,
                    'stats': self.stats
                }
                with open(self.checkpoint_file, 'wb') as f:
                    pickle.dump(checkpoint_data, f)
                self.last_checkpoint_time = current_time
                logger.info(f"Checkpoint salvo: {len(self.processed_files)} arquivos processados")
            except Exception as e:
                logger.warning(f"Erro ao salvar checkpoint: {e}")

    def _should_exclude_file(self, file_path: str) -> bool:
        """
        Determina se um arquivo deve ser excluído do processamento.

        Args:
            file_path: Caminho completo para o arquivo

        Returns:
            bool: True se o arquivo deve ser excluído, False caso contrário
        """
        # Verificar extensão
        _, ext = os.path.splitext(file_path)
        if ext.lower() in self.exclude_extensions:
            return True

        # Verificar padrões excluídos
        for pattern in self.exclude_patterns:
            if pattern in file_path:
                return True

        # Verificar tamanho máximo
        try:
            if os.path.getsize(file_path) > (self.max_size_mb * 1024 * 1024):
                logger.debug(f"Arquivo muito grande, ignorando: {file_path}")
                return True
        except Exception as e:
            logger.debug(f"Erro ao verificar tamanho do arquivo {file_path}: {e}")
            return True

        return False

    def is_removal_candidate(self, file_path: str, file_stat: os.stat_result) -> bool:
        """
        Determina se um arquivo é candidato à remoção segura.

        Args:
            file_path: Caminho completo para o arquivo
            file_stat: Resultado de os.stat() para o arquivo

        Returns:
            bool: True se o arquivo for candidato à remoção, False caso contrário
        """
        # Arquivos muito antigos (mais de 1 ano)
        file_age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(file_stat.st_mtime)).days
        if file_age_days > 365:
            # Verificar se está em diretório legado
            for legacy_dir in self.legacy_dirs:
                if f"/{legacy_dir}/" in file_path.replace("\\", "/") or f"\\{legacy_dir}\\" in file_path:
                    return True

        # Arquivos com padrões específicos no nome
        file_name = os.path.basename(file_path)
        name_base, ext = os.path.splitext(file_name)
        patterns = ["old", "backup", "bak", "temp", "tmp", "copy", "copia", "v1", "v2"]
        for pattern in patterns:
            if pattern in name_base.lower():
                return True

        # Arquivos duplicados em diretórios legados
        if file_path.endswith(".txt") or file_path.endswith(".md"):
            for legacy_dir in self.legacy_dirs:
                if f"/{legacy_dir}/" in file_path.replace("\\", "/") or f"\\{legacy_dir}\\" in file_path:
                    # Verificar se existe uma versão processada deste arquivo
                    base_name = os.path.basename(file_path)
                    if os.path.exists(os.path.join(self.root_dir, "docs", "legacy", base_name)):
                        return True

        return False

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

    @staticmethod
    def _format_size(size_bytes: int) -> str:
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
        if self.legacy_files and len(self.processed_files) > 0:
            logger.info(f"Usando {len(self.legacy_files)} arquivos legados já encontrados do checkpoint")
            return self.legacy_files

        legacy_files = self.legacy_files.copy() if self.legacy_files else []
        files_processed = 0
        batch_count = 0

        try:
            for root, dirs, files in os.walk(self.root_dir):
                # Filtrar diretórios excluídos
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

                # Verificar se há muitos arquivos no diretório atual
                if len(files) > 1000:
                    logger.warning(f"Diretório com muitos arquivos: {root} ({len(files)} arquivos). Processando apenas os primeiros 1000.")
                    files = files[:1000]

                for file in files:
                    file_path = os.path.join(root, file)

                    # Verificar se já foi processado
                    if file_path in self.processed_files:
                        continue

                    # Verificar limite de arquivos
                    if self.max_files > 0 and files_processed >= self.max_files:
                        logger.info(f"Limite de {self.max_files} arquivos atingido. Parando processamento.")
                        break

                    # Verificar extensão
                    _, ext = os.path.splitext(file_path)
                    if ext.lower() not in self.legacy_extensions:
                        self.processed_files.add(file_path)
                        continue

                    # Verificar se deve ser excluído
                    if self._should_exclude_file(file_path):
                        self.stats["skipped_files"] += 1
                        self.processed_files.add(file_path)
                        continue

                    try:
                        file_stat = os.stat(file_path)
                        self.stats["total_files_scanned"] += 1

                        # Verificar se é candidato à remoção
                        if self.is_removal_candidate(file_path, file_stat):
                            removal_metadata = self.get_file_metadata(file_path, file_stat)
                            removal_metadata["reason"] = "candidate_for_removal"
                            self.removal_candidates.append(removal_metadata)
                            self.stats["removal_candidates"] += 1

                        # Verificar se é legado
                        if self.is_legacy_file(file_path, file_stat):
                            metadata = self.get_file_metadata(file_path, file_stat)
                            legacy_files.append(metadata)
                            self.stats["legacy_files_found"] += 1

                        # Atualizar contadores
                        files_processed += 1
                        batch_count += 1
                        self.processed_files.add(file_path)

                        # Salvar checkpoint a cada N arquivos
                        if batch_count >= self.batch_size:
                            self._save_checkpoint()
                            batch_count = 0

                        # Log de progresso
                        if files_processed % 1000 == 0:
                            elapsed = time.time() - self.start_time
                            rate = files_processed / elapsed if elapsed > 0 else 0
                            logger.info(f"Processados {files_processed} arquivos ({rate:.1f} arquivos/s)")
                            logger.info(f"Encontrados {self.stats['legacy_files_found']} arquivos legados e {self.stats['removal_candidates']} candidatos à remoção")

                    except Exception as e:
                        logger.warning(f"Erro ao processar arquivo {file_path}: {e}")
                        self.processed_files.add(file_path)  # Marcar como processado mesmo com erro

                # Verificar limite de arquivos (novamente, após processar um diretório)
                if self.max_files > 0 and files_processed >= self.max_files:
                    logger.info(f"Limite de {self.max_files} arquivos atingido. Parando processamento.")
                    break

        except KeyboardInterrupt:
            logger.warning("Processamento interrompido pelo usuário")
            self._save_checkpoint(force=True)

        # Salvar checkpoint final
        self._save_checkpoint(force=True)
        self.legacy_files = legacy_files

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
            f.write(f"**Diretório Base:** {self.root_dir}\n\n")

            # Resumo Executivo
            f.write("## Resumo Executivo\n\n")
            f.write("Este relatório foi gerado para auxiliar na otimização do espaço em disco e na organização dos arquivos legados do projeto EGOS. ")
            f.write("O objetivo é identificar arquivos que podem ser removidos com segurança, bem como mapear o conteúdo legado que precisa ser preservado.\n\n")

            # Estatísticas
            f.write("## Estatísticas\n\n")
            f.write(f"- **Total de Arquivos Escaneados:** {self.stats['total_files_scanned']}\n")
            f.write(f"- **Arquivos Legados Encontrados:** {self.stats['legacy_files_found']}\n")
            f.write(f"- **Arquivos Ignorados:** {self.stats['skipped_files']}\n")
            f.write(f"- **Candidatos à Remoção:** {self.stats['removal_candidates']}\n\n")

            # Configuração do escaneamento
            f.write("### Configuração do Escaneamento\n\n")
            f.write(f"- **Diretórios Legados:** {', '.join(self.legacy_dirs)}\n")
            f.write(f"- **Extensões Incluídas:** {', '.join(self.legacy_extensions)}\n")
            f.write(f"- **Diretórios Excluídos:** {', '.join(self.exclude_dirs[:10])}... (total: {len(self.exclude_dirs)})\n")
            f.write(f"- **Tamanho Máximo de Arquivo:** {self.max_size_mb} MB\n\n")

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

            # Candidatos à remoção
            if self.removal_candidates:
                f.write("## Candidatos à Remoção\n\n")
                f.write("Estes arquivos foram identificados como possíveis candidatos para remoção segura. ")
                f.write("**IMPORTANTE:** Revise esta lista cuidadosamente antes de remover qualquer arquivo.\n\n")

                f.write("### Resumo de Espaço Potencial\n\n")
                total_size_bytes = sum(file["size_bytes"] for file in self.removal_candidates)
                f.write(f"- **Total de Arquivos:** {len(self.removal_candidates)}\n")
                f.write(f"- **Espaço Total:** {self._format_size(total_size_bytes)}\n\n")

                f.write("### Lista de Candidatos\n\n")
                f.write("| Caminho | Tamanho | Modificado | Idade (dias) | Subsistema |\n")
                f.write("|---------|---------|------------|--------------|------------|\n")

                # Ordenar por tamanho (maior primeiro)
                sorted_candidates = sorted(self.removal_candidates, key=lambda x: x["size_bytes"], reverse=True)

                for file in sorted_candidates:
                    path_md = file["path"].replace(" ", "%20")  # Escapar espaços para links Markdown
                    f.write(f"| [{file['path']}]({path_md}) | {file['size_human']} | {file['modified']} | {file['age_days']} | {file['subsystem']} |\n")
                f.write("\n")

                # Gerar script de remoção
                script_path = os.path.join(os.path.dirname(self.output_file), "removal_script.ps1")
                with open(script_path, 'w', encoding='utf-8') as script_file:
                    script_file.write("# Script para remoção de arquivos candidatos\n")
                    script_file.write("# ATENÇÃO: Este script foi gerado automaticamente. Revise cuidadosamente antes de executar.\n")
                    script_file.write("# Gere um backup antes de executar este script.\n\n")

                    for file in sorted_candidates:
                        script_file.write(f"# Remover: {file['path']} ({file['size_human']})\n")
                        script_file.write(f"# Remove-Item -Path \"{os.path.join(self.root_dir, file['path'])}\" -Force # Descomente para executar\n\n")

                f.write(f"Um script PowerShell para remoção foi gerado em: `{script_path}`\n\n")

            # Lista de arquivos legados
            f.write("## Lista de Arquivos Legados\n\n")
            f.write("| Caminho | Tamanho | Modificado | Idade (dias) | Subsistema |\n")
            f.write("|---------|---------|------------|--------------|------------|\n")

            for file in legacy_files:
                path_md = file["path"].replace(" ", "%20")  # Escapar espaços para links Markdown
                f.write(f"| [{file['path']}]({path_md}) | {file['size_human']} | {file['modified']} | {file['age_days']} | {file['subsystem']} |\n")

            # Recomendações
            f.write("\n## Recomendações\n\n")
            f.write("1. **Backup**: Antes de remover qualquer arquivo, faça um backup completo.\n")
            f.write("2. **Remoção em Fases**: Remova os arquivos em pequenos lotes, começando pelos maiores.\n")
            f.write("3. **Verificação**: Após cada fase de remoção, verifique se o sistema continua funcionando corretamente.\n")
            f.write("4. **Documentação**: Mantenha um registro dos arquivos removidos.\n")

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
    parser.add_argument("--checkpoint", help="Arquivo de checkpoint para retomar processamento")
    parser.add_argument("--log-file", help="Arquivo para salvar logs detalhados")
    parser.add_argument("--min-age", type=int, default=0, help="Idade mínima em dias para considerar um arquivo como legado")
    parser.add_argument("--max-size", type=float, default=10.0, help="Tamanho máximo em MB para processar um arquivo")
    parser.add_argument("--max-files", type=int, default=0, help="Número máximo de arquivos a processar (0 = sem limite)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Número de arquivos a processar antes de salvar checkpoint")
    parser.add_argument("--include-all", action="store_true", help="Incluir todos os arquivos, não apenas os que parecem legados")
    parser.add_argument("--verbose", action="store_true", help="Exibir informações detalhadas durante a execução")
    parser.add_argument("--exclude-dirs", nargs="+", help="Diretórios adicionais a serem excluídos")
    parser.add_argument("--legacy-dirs", nargs="+", help="Diretórios adicionais a serem considerados legados")
    parser.add_argument("--include-extensions", nargs="+", help="Extensões de arquivo a serem incluídas")
    parser.add_argument("--exclude-extensions", nargs="+", help="Extensões de arquivo a serem excluídas")

    args = parser.parse_args()

    # Combinar listas de diretórios excluídos
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)

    # Combinar listas de diretórios legados
    legacy_dirs = DEFAULT_LEGACY_DIRS.copy()
    if args.legacy_dirs:
        legacy_dirs.extend(args.legacy_dirs)

    # Combinar listas de extensões incluídas
    include_extensions = DEFAULT_LEGACY_EXTENSIONS.copy()
    if args.include_extensions:
        include_extensions.extend(args.include_extensions)

    # Combinar listas de extensões excluídas
    exclude_extensions = DEFAULT_EXCLUDE_EXTENSIONS.copy()
    if args.exclude_extensions:
        exclude_extensions.extend(args.exclude_extensions)

    generator = LegacyInventoryGenerator(
        root_dir=args.root,
        output_file=args.output,
        legacy_dirs=legacy_dirs,
        legacy_extensions=include_extensions,
        exclude_dirs=exclude_dirs,
        exclude_extensions=exclude_extensions,
        min_age_days=args.min_age,
        max_size_mb=args.max_size,
        max_files=args.max_files,
        batch_size=args.batch_size,
        checkpoint_file=args.checkpoint,
        log_file=args.log_file,
        include_all_files=args.include_all,
        verbose=args.verbose
    )

    generator.run()


if __name__ == "__main__":
    main()
