# @references:
#   - ATRIAN/templates/tests/test_pydantic_models.py
# 
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto (C:\EGOS) ao sys.path
# para permitir importações de 'ATRIAN' como um pacote de nível superior
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import yaml
import logging

# Configurar logging para arquivo
logging.basicConfig(
    filename='pydantic_test.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Também imprimir no console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

from ATRIAN.templates.base.ethical_constitution_schema import (
    EthicalRule, 
    EthicalPrinciple, 
    EthicalConstitution,
    SeverityLevel
)

def log_separator(title):
    logging.info("\n" + "=" * 50)
    logging.info(f"  {title}")
    logging.info("=" * 50)

# Teste 1: Criar um EthicalRule diretamente
log_separator("TESTE 1: Criação direta de EthicalRule")
rule_data = {
    'id': 'R001_Test',
    'principle_ids': ['P001'],
    'description': 'Teste de regra ética',
    'trigger_keywords': ['teste', 'keyword'],
    'recommendations': ['Esta é uma recomendação de teste'],
    'severity_override': 'medium'
}

logging.info(f"Dados de entrada para EthicalRule: {rule_data}")
logging.info("Tentando criar EthicalRule...")
try:
    rule = EthicalRule(**rule_data)
    logging.info(f"[SUCESSO] EthicalRule criado: {rule}")
    logging.info(f"Campos do modelo: {rule.model_fields.keys()}")
except Exception as e:
    logging.error(f"[ERRO] ao criar EthicalRule: {e}")
    logging.error(f"Tipo de erro: {type(e).__name__}")

# Teste 2: Criar um EthicalPrinciple diretamente
log_separator("TESTE 2: Criação direta de EthicalPrinciple")
principle_data = {
    'id': 'P001',
    'name': 'TestPrinciple',
    'description': 'Teste de princípio ético',
    'severity': 'high'
}

logging.info(f"Dados de entrada para EthicalPrinciple: {principle_data}")
logging.info("Tentando criar EthicalPrinciple...")
try:
    principle = EthicalPrinciple(**principle_data)
    logging.info(f"[SUCESSO] EthicalPrinciple criado: {principle}")
    logging.info(f"Campos do modelo: {principle.model_fields.keys()}")
except Exception as e:
    logging.error(f"[ERRO] ao criar EthicalPrinciple: {e}")
    logging.error(f"Tipo de erro: {type(e).__name__}")

# Teste 3: Criar um EthicalConstitution completo
log_separator("TESTE 3: Criação direta de EthicalConstitution")
from datetime import datetime

constitution_data = {
    'id': 'C001_Test',
    'name': 'TestConstitution',
    'description': 'Teste de constituição ética',
    'metadata': {
        'version': '1.0',
        'created_date': datetime.now(),
        'author': 'Test Author',
        'purpose': 'Teste',
        'applicable_domains': ['test_domain'],
        'tags': ['test', 'validation'],
        'regulatory_alignment': ['Test_Regulation']
    },
    'principles': [principle_data],
    'rules': [rule_data]
}

logging.info(f"Dados de entrada para EthicalConstitution: {constitution_data}")
logging.info("Tentando criar EthicalConstitution...")
try:
    constitution = EthicalConstitution(**constitution_data)
    logging.info(f"[SUCESSO] EthicalConstitution criado: {constitution}")
    logging.info(f"Campos do modelo: {constitution.model_fields.keys()}")
    logging.info(f"Número de regras: {len(constitution.rules)}")
    logging.info(f"Número de princípios: {len(constitution.principles)}")
except Exception as e:
    logging.error(f"[ERRO] ao criar EthicalConstitution: {e}")
    logging.error(f"Tipo de erro: {type(e).__name__}")

# Teste 4: Verificar se SeverityLevel aceita strings
log_separator("TESTE 4: Verificação de SeverityLevel com strings")
try:
    # Testar conversão direta de string para SeverityLevel
    severity = SeverityLevel('medium')
    logging.info(f"[SUCESSO] SeverityLevel('medium') = {severity}")
except Exception as e:
    logging.error(f"[ERRO] ao converter string para SeverityLevel: {e}")
    logging.error(f"Tipo de erro: {type(e).__name__}")

# Verificar se há múltiplas definições do mesmo modelo
log_separator("VERIFICAÇÃO DE IMPORTAÇÕES MÚLTIPLAS")
import inspect
logging.info(f"EthicalRule definido em: {inspect.getfile(EthicalRule)}")
logging.info(f"EthicalPrinciple definido em: {inspect.getfile(EthicalPrinciple)}")
logging.info(f"EthicalConstitution definido em: {inspect.getfile(EthicalConstitution)}")
logging.info(f"SeverityLevel definido em: {inspect.getfile(SeverityLevel)}")