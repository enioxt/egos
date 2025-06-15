#!/usr/bin/env python
"""
Script para atualizar arquivos de constituição ética YAML,
adicionando campos obrigatórios faltantes no metadata.

Este script procura por arquivos YAML que parecem ser constituições éticas
(contendo campos como 'principles', 'rules', etc.) e adiciona os campos
obrigatórios 'created_date' e 'author' se estiverem faltando.
"""
# 
# @references:
#   - ATRIAN/templates/tests/update_constitutions.py

import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto (C:\EGOS) ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import yaml
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_constitution_file(file_path, content=None):
    """Verifica se o arquivo parece ser uma constituição ética."""
    if content is None:
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Erro ao ler {file_path}: {e}")
            return False
    
    # Verifica se tem estrutura básica de constituição
    if not isinstance(content, dict):
        return False
    
    required_keys = ['id', 'name', 'metadata', 'principles', 'rules']
    return all(key in content for key in required_keys)

def update_constitution_file(file_path):
    """Atualiza um arquivo de constituição ética com campos obrigatórios faltantes."""
    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
        
        if not is_constitution_file(file_path, content):
            logging.info(f"Arquivo {file_path} não parece ser uma constituição ética. Pulando.")
            return False
        
        modified = False
        
        # Verifica e atualiza metadata
        if 'metadata' in content and isinstance(content['metadata'], dict):
            metadata = content['metadata']
            
            # Adiciona created_date se estiver faltando
            if 'created_date' not in metadata:
                metadata['created_date'] = datetime.now()
                modified = True
                logging.info(f"Adicionado 'created_date' a {file_path}")
            
            # Adiciona author se estiver faltando
            if 'author' not in metadata:
                metadata['author'] = "EGOS System"
                modified = True
                logging.info(f"Adicionado 'author' a {file_path}")
        
        # Se houve modificações, salva o arquivo
        if modified:
            with open(file_path, 'w') as f:
                yaml.dump(content, f)
            logging.info(f"Arquivo {file_path} atualizado com sucesso.")
            return True
        else:
            logging.info(f"Arquivo {file_path} já possui todos os campos obrigatórios.")
            return False
    
    except Exception as e:
        logging.error(f"Erro ao processar {file_path}: {e}")
        return False

def find_and_update_constitutions(root_dir):
    """Encontra e atualiza todos os arquivos de constituição ética no diretório."""
    updated_count = 0
    yaml_files = []
    
    # Encontra todos os arquivos YAML
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                yaml_files.append(os.path.join(root, file))
    
    logging.info(f"Encontrados {len(yaml_files)} arquivos YAML para verificação.")
    print(f"Encontrados {len(yaml_files)} arquivos YAML para verificação.")
    
    # Lista todos os arquivos YAML encontrados
    for i, file_path in enumerate(yaml_files):
        print(f"{i+1}. {file_path}")
    
    # Processa cada arquivo
    updated_files = []
    for file_path in yaml_files:
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                if is_constitution_file(file_path, content):
                    print(f"\nVerificando constituição: {file_path}")
                    if 'metadata' in content:
                        print(f"  Campos atuais no metadata: {list(content['metadata'].keys())}")
                        if update_constitution_file(file_path):
                            updated_count += 1
                            updated_files.append(file_path)
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
    
    print("\nArquivos atualizados:")
    for file in updated_files:
        print(f"- {file}")
    
    logging.info(f"Atualização concluída. {updated_count} arquivos foram atualizados.")
    print(f"\nAtualização concluída. {updated_count} arquivos foram atualizados.")
    return updated_count

if __name__ == "__main__":
    # Define o diretório raiz para busca (padrão: diretório atual)
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "C:\\EGOS"
    logging.info(f"Iniciando busca por constituições éticas em: {root_dir}")
    find_and_update_constitutions(root_dir)